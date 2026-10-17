"""The ruler for docs/PLAN-VOICE.md §9 -- what surface form the STT emits.

**The question this whole build exists to answer.** `docs/PLAN-FINETUNE-V4.md`
entry 0 counted the corpus's user turns and found one orthography: of 6,603,586
turns, 2,442,972 end in `?` and 2,268,194 of those are `resolve_date`; all-caps
is 15 rows in 6.6M. So every routing behaviour the model has was taught under
one surface form, and `harness/surfacegrid.py` measured what happens to the
others -- pooled, `verbatim` 43/57 against `title` 9/57 and `mixed` 4/57. Case
is the larger axis of the two.

What nobody has ever measured is **which surface form a person's voice arrives
in**, because until this package there was no voice. Entry 0's punctuated
payload is sized off the answer, and its execution order carries a standing
note saying the question is open.

**Two axes, not one, and the second is the reason this file is not four
lines.** `PLAN-FINETUNE-V4` reasons that "case comes from a keyboard rather
than a transcriber", which is true of every input the project has had and may
stop being true the moment the input is a microphone: whisper capitalises the
first word of an utterance. So this classifies case as well as punctuation,
and it carries a fifth case value the grid does not have --

    "The capital of Laos."

is not `verbatim`, not `lower`, not `title` and not `upper`. It is a leading
capital on an otherwise-lowercase turn, and if that is what a transcriber
emits on every turn then entry 0 has a case axis on the voice channel that it
currently attributes to keyboards. `sentence` is the name for it here.

**Raw columns beside the classification, and that is the discipline rather
than thoroughness.** A row keeps `leading_capital` and `caps_words` as well as
`case`, so a later session that wants a different cut of the same axis
recomputes it off rows already on disk instead of asking for fifty more spoken
turns. `sessionlog.py`'s argument -- keep what was known at the time, not what
survived the summary.

Pure. `scripts/check_voice.py` drives every branch.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass

# What counts as a terminal mark. `…` is here because a transcriber emits it
# for a trailed-off clause and it is not a question mark, which is the only
# distinction the corpus count cares about.
TERMINALS = (".", "?", "!", ",", ";", ":", "…")

# The cases, in the resolution order `classify_case` applies them. `sentence`
# sits between `title` and `mixed` because a two-word title-cased turn is also
# a leading capital and the more specific reading wins.
CASES = ("upper", "lower", "title", "sentence", "mixed", "caseless")

_WORD = re.compile(r"[^\W\d_]+", re.UNICODE)


def terminal(text: str) -> str:
    """The last non-space character if it is punctuation, else "none".

    Not "the last character": a transcript with a trailing space ends in a
    mark as far as the model is concerned, because the server does not strip
    it either and `<|user|>...\\n` puts the newline after whatever is there.
    """
    stripped = text.rstrip()
    if not stripped:
        return "none"
    last = stripped[-1]
    return last if last in TERMINALS else "none"


def classify_case(text: str) -> str:
    """One of `CASES`. See the module docstring for why `sentence` exists.

    Order is upper, lower, title, sentence, mixed -- most specific first, so a
    cell is never claimed by a looser reading of the same string. `caseless`
    is a turn with no cased letter in it at all ("2026", "..."), which is a
    real transcriber output and is not `lower`.

    **`title` needs two words, and that is not a technicality.** "Noted!" is
    one capitalised word, which satisfies "every word starts with a capital"
    and is not title case -- it is a sentence-cased turn one word long, which
    is exactly the form this build expects a transcriber to emit most often.
    Letting it read as `title` would move the commonest short voice turn into
    the cell `harness/surfacegrid.py` measured at 9/57.
    """
    words = _WORD.findall(text)
    if not any(c.isalpha() for c in text):
        return "caseless"
    if text == text.upper():
        return "upper"
    if text == text.lower():
        return "lower"
    if len(words) > 1 and all(w[0].isupper() for w in words):
        return "title"
    if words and words[0][0].isupper():
        return "sentence"
    return "mixed"


@dataclass
class Surface:
    """One transcript's surface form, classified and counted.

    The counts are the point as much as the labels: `caps_words` separates
    "whisper capitalised the first word" from "whisper capitalised three
    proper nouns", and those are different facts about the same `sentence`
    cell.
    """

    terminal: str
    case: str
    leading_capital: bool
    # Words after the first that start with a capital. Proper nouns, mostly --
    # the column that says whether a `sentence` turn is plain or full of names.
    caps_words: int
    words: int
    chars: int
    commas: int
    apostrophes: int
    hyphens: int
    digits: int
    # Punctuation anywhere but the last character. A turn with a mid-sentence
    # full stop is a two-sentence turn, which the corpus has almost none of.
    internal_terminals: int

    def as_dict(self) -> dict:
        return asdict(self)


def read(text: str) -> Surface:
    """One transcript, measured. Never raises; an empty string is a row."""
    words = _WORD.findall(text)
    stripped = text.rstrip()
    body = stripped[:-1] if terminal(text) != "none" else stripped
    return Surface(
        terminal=terminal(text),
        case=classify_case(text),
        leading_capital=bool(words) and words[0][0].isupper(),
        caps_words=sum(1 for w in words[1:] if w[0].isupper()),
        words=len(words),
        chars=len(text),
        commas=text.count(","),
        apostrophes=sum(text.count(c) for c in ("'", "’")),
        hyphens=text.count("-"),
        digits=sum(c.isdigit() for c in text),
        internal_terminals=sum(body.count(c) for c in (".", "?", "!")),
    )


def distribution(surfaces: list[Surface]) -> dict:
    """The §9 report's numbers, from a list of rows.

    Kept here rather than in the report script so the guard can assert the
    arithmetic without a log file, and so a second consumer -- a grid, a later
    session -- reads the same procedure rather than a second implementation of
    it. `harness/protocol.py`'s rule about one description of one idea.
    """
    n = len(surfaces)
    term = Counter(s.terminal for s in surfaces)
    case = Counter(s.case for s in surfaces)
    return {
        "n": n,
        "terminal": dict(term.most_common()),
        "case": dict(case.most_common()),
        # The two headline rates entry 0 actually asked for, named so nobody
        # has to recompute them off the tables above.
        "punctuated": sum(v for k, v in term.items() if k != "none"),
        "question_mark": term.get("?", 0),
        "leading_capital": sum(1 for s in surfaces if s.leading_capital),
        # The one form the corpus was written in. A voice turn that lands here
        # needs nothing from entry 0.
        "corpus_form": sum(1 for s in surfaces
                           if s.case == "lower" and s.terminal == "none"),
        "multi_sentence": sum(1 for s in surfaces if s.internal_terminals),
        "words_median": _median([s.words for s in surfaces]),
    }


def _median(xs: list[int]) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    mid = len(ys) // 2
    return float(ys[mid]) if len(ys) % 2 else (ys[mid - 1] + ys[mid]) / 2
