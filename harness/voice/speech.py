"""What actually reaches the speakers, decided here and nowhere else.

Pure, so `scripts/check_voice.py` drives all of it with no synthesiser, and so
there is exactly one place that answers "was this spoken, and in what form".

**Two problems, and they are not the same problem.**

*Markers.* A `say` is supposed to be words. Sometimes it is words with a
`<|end|>` on the end, or a `<|say|>` in the middle, because the emission fell
out of the turn vocabulary and a floor caught it late. On a screen that is a
visible defect somebody notices. Through a synthesiser it is a voice reading
"less than vertical bar end vertical bar greater than" out loud, which is worse
than the defect it reveals. Everything between `<|` and `|>` comes off, and the
count of what came off goes in the row -- so marker leakage stops being a known
defect and becomes a rate.

*Multiple says.* A turn can emit more than one. A compound turn says a thing
per tool; a corrected turn emits a say that supersedes one already sent; and
routinely the last `say` is exactly what the `text` events already streamed,
plus the full stop `tidy_say` added when `say_cut` stopped him mid-clause. The
first two must be spoken and the third must not be spoken twice.
`harness/client.py` solved the same problem for a screen with `_content`, and
this file uses the same comparison for the same reason: a reply that differs
only in punctuation is not a different reply.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# **Wider than `harness/client.py`'s `<\|[a-z]+\|>`, deliberately.** That
# pattern is exactly right for a client deciding whether two strings are the
# same reply, because it only has to match the markers the runtime emits. This
# one decides what a speaker says out loud, and a leaked marker is by
# definition a shape the runtime did not mean to emit -- betting the speakers
# on its exact spelling is the wrong side to be wrong on. Non-greedy and
# newline-free so a `<|` with no closer cannot swallow the rest of the reply.
MARKER = re.compile(r"<\|[^|\n]*\|>")

# An unterminated opener -- `"...that's it <|"` -- is the shape a truncated
# emission leaves behind, and `MARKER` cannot match it because there is no
# closer to match. Trimmed from the tail only: a bare `<|` in the middle of a
# sentence is far likelier to be a person's punctuation than a broken marker.
DANGLING = re.compile(r"<\|[^|\n]*$")

# Letters and digits only, case folded. `harness/client.py`'s rule, copied
# rather than imported: that module is a CLI with a module-level console side
# effect, and a package that only wants one regex should not pull it in.
_CONTENT = re.compile(r"[^a-z0-9]")


def content(text: str) -> str:
    """The words, with nothing that only affects how they are punctuated."""
    return _CONTENT.sub("", MARKER.sub("", text).lower())


@dataclass
class Sanitised:
    """One say, cleaned, with what the cleaning found."""

    text: str
    # How many markers came off. Non-zero is a defect in the emission, not in
    # this file, and it is recorded per turn for exactly that reason.
    strikes: int = 0
    # What they were, so a rate can become a diagnosis without the audio back.
    found: tuple[str, ...] = ()

    def __bool__(self) -> bool:
        return bool(self.text)


def sanitise(say: str) -> Sanitised:
    """A say as a synthesiser may have it. Never raises, never reorders.

    Whitespace is collapsed because removing a marker from the middle of a
    sentence leaves a double space, and a double space is a pause in some
    synthesisers. Nothing else about the string is touched -- in particular
    the punctuation and the case are the model's and stay his, on the same
    rule the incoming transcript is held to.
    """
    found = tuple(MARKER.findall(say))
    text = MARKER.sub(" ", say)
    text = DANGLING.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return Sanitised(text=text, strikes=len(found), found=found)


@dataclass
class Utterance:
    """Everything a turn asked to have said, in the order it asked.

    `spoken` is what the synthesiser gets. `skipped` is the says that were
    duplicates of something already in it -- kept as a count because "he said
    one thing" and "he said the same thing twice and we caught it" are
    different facts about a turn.
    """

    spoken: list[str] = field(default_factory=list)
    skipped: int = 0
    strikes: int = 0
    markers: list[str] = field(default_factory=list)
    # A say arrived and sanitised to nothing at all -- the shape a pure-marker
    # emission leaves. Distinct from "no say arrived", which is silence.
    emptied: int = 0

    def add(self, say: str) -> str:
        """Take one `say` event's text. Returns what to speak, or "".

        The duplicate rule is `content`: a say that carries the same letters
        and digits as something already spoken this turn is the same reply
        differently punctuated, and speaking it again is the doubling
        `harness/client.py` avoids on screen.
        """
        clean = sanitise(say)
        self.strikes += clean.strikes
        self.markers.extend(clean.found)
        if not clean.text:
            if say.strip():
                self.emptied += 1
            return ""
        key = content(clean.text)
        if key and any(content(s) == key for s in self.spoken):
            self.skipped += 1
            return ""
        self.spoken.append(clean.text)
        return clean.text

    def whole(self) -> str:
        """Everything spoken this turn, as one string, for the transcript."""
        return " ".join(self.spoken)

    def silent(self) -> bool:
        return not self.spoken
