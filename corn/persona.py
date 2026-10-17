"""Who *he* is, held in a store instead of in the source.

**Every fact about the owner already lives in a file.** `packs/about-me.md`
holds their name, a pack table holds their people, `notes.jsonl` holds
their days, and VISION §4's rule is what put each of them there: the shipped
artefact is user-neutral, and a running instance specialises through its
stores. Every fact about *him* was hard-coded -- "Corn-Jr" appears verbatim in
four reply pools in `corn/agent.py` and in `SPEAKABLE_CAPS` -- and there was
nowhere to put a birthday, a fun fact, or anything else that makes one
instance somebody's rather than everybody's. His own identity was the one part
of the personal layer that never got a store. This is that store's shape.

**The governing property: with no persona file, nothing changes.** `DEFAULT`
is the name and the behaviour this project already had, every entry point
defaults to it, and `Persona.named` is a no-op when the name is unchanged. It
is the posture `search`, `book` and `steps` already take on `World` -- a
configuration that loaded nothing behaves exactly as it did before the seam
existed -- and `scripts/check_persona.py` asserts it first, because it is the
thing that lets this land without re-measuring a single scorecard.

**Pure, and no file parsing.** The knobs arrive as a `Persona`;
`harness/backends/persona.py` is what reads `packs/persona.md`. The split is
`corn/steps.py`'s exactly, and it is forced: `corn/` may not import `harness/`
(`scripts/check_layering.py`), and the pools that need the name are in
`corn/agent.py`. The one thing that would otherwise be written twice -- how a
date field is spelled -- lives here as `parse_when`, so the loader and the
guard read the same implementation.

**What a `line` is, and whose voice it is in.** An `on:` occasion carries the
owner's own sentence and it is spoken as written. That is the contact book's
terms, not a loosening of them: the file is on the owner's machine, written by
the owner, for their own instance. The birthday is the other kind -- no line
in the file, composed at speak time from a pool in `corn/agent.py` that had to
pass `docs/VOICE.md` like every other sentence he says. A store may hold his
facts; it does not get to hand the runtime an unchecked sentence unless a
person typed it there deliberately.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

DEFAULT_NAME = "Corn-Jr"
DEFAULT_STATE = Path("persona_state.json")

# **The two holes a trained sentence may leave, and what fills them.**
# `docs/PLAN-PERSONALITY.md` §4: the weights never carry a name. A self line
# in the payload says "I'm {name}." and a greeting may say "Morning, {user}.",
# and `Persona.speak` fills both at speak time from the two pack headers --
# `persona.md`'s `name:` and `about-me.md`'s `name:`. Plain text, three bpe8k
# tokens each, never seen in the dialogue source, so the model copies a fixed
# literal, which is the one thing every copy row reads at its ceiling. A brace
# left after filling is a sentence nobody should hear -- `unfilled` is the
# check, and the runtime refuses the say and lets the pool cover.
PLACEHOLDER_NAME = "{name}"
PLACEHOLDER_USER = "{user}"

# A birthday from the people store (`harness/backends/persona.py`
# `people_birthdays`), mentioned `Occasion.lead` days ahead rather than on the
# day -- the one kind `Persona.on` skips and `Persona.heads_up` reads.
PERSON_BIRTHDAY = "person_birthday"
# The owner's lead time, 2026-10-13 (PLAN-PEOPLE §9.1): three days, once.
# `ServerConfig.birthday_lead` overrides it per instance.
DEFAULT_BIRTHDAY_LEAD = 3

# **The header, which is what replaced the tag.** PLAN-PERSONALITY (sixth):
# arm 9's first cut asked the weights to *recall* a never-seen three-token
# literal from 152 exposures, and they answered "I'm _____." -- the right
# slot, the wrong literal, the blank the pretraining corpus uses. The
# project's own record (finding 34) says a literal is learned by copying
# from the context at one use and by recall at tens of thousands. So the
# name goes into the context: one plain-text line, first in the transcript,
# above `<|day|>` and `tools:`, in the corpus and at the runtime alike,
# rendered by `name_header` so the two cannot drift. Trained with the name
# varied per transcript, the model learns to copy whatever the line says;
# at the runtime the line says the persona's name, and `{name}` is not
# needed. `speak` stays for the tag's sake and is the identity on a
# sentence without one.
HEADER_PREFIX = "name: "


def name_header(name: str) -> str:
    """The context line that tells him his name, newline included."""
    return f"{HEADER_PREFIX}{name}\n"


# **The names a training transcript's header may say.** Plausible assistant
# names, about two hundred, so that what the weights learn is to copy the
# line rather than to recall a name; the shipped name rides at
# `SHIPPED_HEADER_SHARE` of draws so it is one of them and not the one. Here
# rather than in `corn/socialgen.py` because `corn/data.py` draws from it at
# mix-build time for every turn-shaped slice (PLAN-PERSONALITY (seventh): the
# header has to be on every transcript or it becomes a cue for the one slice
# that carries it), and `data.py` must not import the generators.
HEADER_NAMES = (
    "Sprout", "Beans", "Rusty", "Pip", "Otto", "Juniper", "Mabel", "Basil",
    "Pepper", "Clover", "Hazel", "Bramble", "Wren", "Fig", "Olive", "Moss",
    "Pickle", "Biscuit", "Waffle", "Noodle", "Dumpling", "Pretzel", "Scone",
    "Muffin", "Toast", "Crumpet", "Bagel", "Tater", "Turnip", "Radish",
    "Parsnip", "Sage", "Thyme", "Rosemary", "Marigold", "Poppy", "Daisy",
    "Iris", "Fern", "Ivy", "Willow", "Rowan", "Alder", "Birch", "Cedar",
    "Maple", "Aspen", "Elm", "Ash", "Oakley", "Ziggy", "Bolt", "Sparky",
    "Widget", "Gadget", "Gizmo", "Pixel", "Byte", "Chip", "Bit", "Dot",
    "Blip", "Beep", "Boop", "Zap", "Buzz", "Echo", "Ping", "Nudge", "Dash",
    "Scout", "Ranger", "Pilot", "Skipper", "Captain", "Major", "Chief",
    "Buddy", "Pal", "Chum", "Mate", "Bud", "Amigo", "Dude", "Jack", "Sam",
    "Max", "Alfie", "Archie", "Teddy", "Freddie", "Ollie", "Charlie", "Bertie",
    "Monty", "Reggie", "Ronnie", "Lenny", "Benny", "Danny", "Frankie",
    "Jamie", "Robin", "Morgan", "Casey", "Riley", "Quinn", "Avery", "Rory",
    "Kit", "Sky", "Rain", "Storm", "Cloud", "Frost", "Snow", "Sunny",
    "Bo", "Mo", "Jo", "Lou", "Vi", "Bea", "Dee", "Kay", "Ray", "Fay",
    "Ada", "Ida", "Una", "Ora", "Isa", "Eve", "Zed", "Rex", "Ace",
    "Hugo", "Milo", "Leo", "Theo", "Enzo", "Arlo", "Otis", "Felix", "Jasper",
    "Casper", "Digby", "Rufus", "Barney", "Bruno", "Nico", "Remy", "Louie",
    "Marlow", "Harley", "Ripley", "Finley", "Bailey", "Murphy", "Sully",
    "Tilly", "Millie", "Molly", "Polly", "Dolly", "Lottie", "Betty", "Nelly",
    "Ellie", "Ruby", "Pearl", "Opal", "Amber", "Coral", "Jade", "Onyx",
    "Nova", "Luna", "Stella", "Vega", "Lyra", "Orion", "Atlas", "Apollo",
    "Juno", "Ares", "Thor", "Loki", "Odin", "Freya", "Bjorn", "Sven",
    "Hans", "Fritz", "Gus", "Ned", "Cy", "Abe", "Ike", "Eli", "Ezra",
    "Corny", "Kernel", "Cobb", "Maize", "Husk", "Popcorn", "Nibs",
)
SHIPPED_HEADER_SHARE = 0.12


def draw_header_name(rng) -> str:
    """A header name for one transcript: a pool name, the shipped one at its share."""
    if rng.random() < SHIPPED_HEADER_SHARE:
        return DEFAULT_NAME
    return rng.choice(HEADER_NAMES)


class Headerer:
    """Put `name: <Name>` above every turn-shaped transcript of a text stream.

    `corn/data.py` feeds it the chunks `_stream_tokens` reads, in order; a
    transcript starts at the top of the file and after every
    `<|endoftext|>\\n`, and a chunk boundary falls on a line end, so the only
    state needed is whether the last chunk ended on a transcript boundary.
    A transcript is turn-shaped when a `<|user|>` sits in its first few
    thousand characters -- the declaration and the day line are short, and a
    transcript with no user turn (the structured slice, prose) gets no
    header, because the runtime never puts one above prose.
    """

    STOP_NL = "<|endoftext|>\n"
    END_NL = "<|end|>\n\n"
    # A transcript starts after `<|endoftext|>\n` (the toolspace and social
    # files) or after `<|end|>\n\n` -- the fine-tune slices (ft4m, turn2,
    # chat, temporal, daylog, compound, extract, paired) close each
    # transcript with `<|end|>` and a blank line and open the next with a
    # day line, a declaration or a user turn. A `<|end|>` followed by one
    # newline and another turn is a two-turn transcript, not a boundary.

    def __init__(self, seed: int = 0):
        import random
        self.rng = random.Random(seed)
        self.at_start = True
        self.headed = 0
        self.skipped = 0

    def _head(self, part: str) -> str:
        if "<|user|>" in part[:6000]:
            self.headed += 1
            return name_header(draw_header_name(self.rng)) + part
        self.skipped += 1
        return part

    def apply(self, chunk: str) -> str:
        import re
        # Split at every boundary, keeping the separators, so the pieces can
        # be re-joined byte-identically apart from the inserted lines.
        boundary = re.compile(r"(<\|endoftext\|>\n|<\|end\|>\n\n)")
        pieces = boundary.split(chunk)
        out = []
        starts = self.at_start
        for piece in pieces:
            if boundary.fullmatch(piece):
                out.append(piece)
                starts = True
                continue
            if starts and piece:
                piece = self._head(piece)
            starts = False
            out.append(piece)
        self.at_start = chunk.endswith(self.STOP_NL) or chunk.endswith(self.END_NL)
        return "".join(out)


def unfilled(text: str) -> str | None:
    """Why a filled sentence still cannot be spoken, or `None`.

    A brace either way is the whole test: a tag the model garbled ("{nam"),
    a tag nothing fills (`{user}` on an instance with no about-me header,
    which `speak` leaves alone on purpose), or a tag this runtime does not
    know. The caller reports the reason and speaks something else.
    """
    if "{" in text or "}" in text:
        return "placeholder"
    return None

# `YYYY-MM-DD` or `MM-DD`. The year is optional and means exactly one thing --
# whether he can say an age out loud -- so a person who wants a birthday
# without a number attached to it simply leaves it off.
_WHEN = re.compile(r"^(?:(\d{4})-)?(\d{1,2})-(\d{1,2})$")


def parse_when(text: str) -> tuple[int, int, int | None]:
    """`(month, day, year or None)` from a date field. Raises on anything else.

    Raising is right here and wrong one layer up: this is the parser, and the
    loader around it is the thing that owes the Book contract. A bad date has
    to be *distinguishable* from a good one before it can be dropped and
    counted.
    """
    m = _WHEN.match(text.strip())
    if not m:
        raise ValueError(f"not a date: {text!r} (want YYYY-MM-DD or MM-DD)")
    year = int(m.group(1)) if m.group(1) else None
    month, day = int(m.group(2)), int(m.group(3))
    try:
        # Validated by construction rather than by range checks, which is
        # `corn/temporal.py`'s discipline: the calendar decides what a date
        # is. A leap day is checked against a leap year on purpose -- 02-29
        # is a real birthday and `Occasion.falls_on` is where it learns which
        # day to land on in the years that do not have one.
        date(year or 2024, month, day)
    except ValueError as exc:
        # Re-raised carrying what the person actually typed. `month must be
        # in 1..12` on its own reaches a console that has three files open
        # and does not say which line to go and fix.
        raise ValueError(f"not a date: {text!r} ({exc})") from None
    return month, day, year


def _leap(year: int) -> bool:
    """Whether a year has a 29th of February. Asked by `Occasion.falls_on`."""
    try:
        date(year, 2, 29)
        return True
    except ValueError:
        return False


@dataclass(frozen=True)
class Occasion:
    """One day of the year that is not an ordinary day.

    `kind` decides who the day is about and therefore who composes the
    sentence: `"birthday"` is his and the runtime writes the line,
    `"owner_birthday"` is the person's and the runtime writes that one too,
    and `"on"` is anything else the owner wrote down, spoken as they typed it.

    `peppy` is the day's *register* rather than its sentence -- it is what
    warms the greeting pool for the whole day, and it is separate from `line`
    because the two are genuinely separate wishes. A quiet anniversary gets a
    line and no brightness; a day that is simply a good one can have the
    brightness and say nothing about why.
    """

    month: int
    day: int
    kind: str = "on"
    line: str = ""
    peppy: bool = True
    year: int | None = None
    who: str = ""          # whose day it is, when the runtime composes the line
    # Days ahead a `person_birthday` is mentioned (`Persona.heads_up`); 0 for
    # every other kind, which falls on its own day only.
    lead: int = 0

    def next_on(self, when: date) -> date:
        """The first day on or after `when` this occasion falls on.

        Walks forward a day at a time rather than doing month arithmetic, so
        `falls_on` -- February 29th included -- stays the one definition of
        when an occasion is.
        """
        day = when
        while not self.falls_on(day):
            day += timedelta(days=1)
        return day

    def falls_on(self, when: date) -> bool:
        if (self.month, self.day) == (when.month, when.day):
            return True
        # **February 29th, which is a day a birthday roughly three years in
        # four would otherwise silently not have.** The 28th is the choice
        # because it keeps the day in its own month, which is how people who
        # have this birthday describe it -- and it applies *only* in a year
        # with no 29th. February 28th of a leap year is an ordinary day and
        # the real one is tomorrow.
        if (self.month, self.day) != (2, 29) or (when.month, when.day) != (2, 28):
            return False
        return not _leap(when.year)

    def age_on(self, when: date) -> int | None:
        """Years old on `when`, or `None` when no year was given.

        `None` is not a failure and the caller must not treat it as one: a
        birthday with no year is a complete birthday, and the pool in
        `corn/agent.py` has a line for both cases.
        """
        if self.year is None:
            return None
        years = when.year - self.year
        return years if (when.month, when.day) >= (self.month, self.day) else years - 1


@dataclass(frozen=True)
class Persona:
    """The knobs a `packs/persona.md` can turn, and their shipped values."""

    name: str = DEFAULT_NAME
    occasions: tuple[Occasion, ...] = ()
    # What he calls the person -- `about-me.md`'s `name:` header, the field
    # the owner's birthday line already reads. Empty means he never says it:
    # `speak` leaves `{user}` standing and `unfilled` refuses the sentence.
    user_name: str = ""

    def speak(self, say: str) -> str:
        """A trained sentence with its holes filled, for the person to hear.

        Unlike `named`, this is **not** the identity function on the default
        persona: `{name}` has to become "Corn-Jr" on an instance with no
        persona file, because the weights say the tag and nobody wrote the
        name in. It *is* the identity function on a sentence with no tag,
        which is every sentence a checkpoint before arm 9 produces, so the
        runtime under this change runs those byte-identically.

        `{user}` is filled only when there is a name to fill it with. Filling
        it with nothing would speak "Morning, ." and filling it with a
        stand-in would speak a word the model did not choose; leaving the tag
        lets `unfilled` refuse the sentence and the pool cover, which is the
        honest outcome and the one `scripts/check_persona.py` asserts.
        """
        if PLACEHOLDER_NAME in say:
            say = say.replace(PLACEHOLDER_NAME, self.name)
        if self.user_name and PLACEHOLDER_USER in say:
            say = say.replace(PLACEHOLDER_USER, self.user_name)
        return say

    def named(self, line: str) -> str:
        """A pool line with this instance's name in it.

        Substitution at speak time rather than templating in the pools,
        deliberately. The pools stay readable as the sentences they are, the
        corpus generators that import them (`corn/turn2gen.py`) see exactly
        what they always saw, and `scripts/check_agent.py`'s assertion that
        every identity line says "Corn-Jr" keeps passing on the default --
        because on the default this function returns its argument.
        """
        if self.name == DEFAULT_NAME:
            return line
        return line.replace(DEFAULT_NAME, self.name)

    def pool(self, lines: tuple[str, ...]) -> tuple[str, ...]:
        """A whole pool, named -- and the naming happens *before* `_pick`.

        Naming the line `_pick` returned would have been one character
        shorter and would have quietly broken the don't-repeat-yourself
        window: the caller records the sentence it emitted, `_pick` suppresses
        by prefix against the raw pool, and under a rename the two halves stop
        being the same strings. Naming the pool keeps one vocabulary on both
        sides of that comparison.

        Returns the argument itself on the default name, so the untouched path
        allocates nothing and compares identical.
        """
        if self.name == DEFAULT_NAME:
            return lines
        return tuple(self.named(line) for line in lines)

    @property
    def caps(self) -> tuple[str, ...]:
        """Capitalised words `social_rejection` must not call invented names.

        A renamed instance whose model rephrases a greeting and says the new
        name would otherwise be rejected by `_stray_capital` -- which is
        exactly what that check is for, and exactly wrong here. Only words
        that are actually capitalised are handed over, so a lowercase name
        adds nothing and cannot widen the check by accident.

        Empty on the default name, which already sits in `SPEAKABLE_CAPS`.
        Returning it anyway would work and would make the no-file path pass a
        non-empty argument to a check it has never passed one to, which is a
        difference a later reader would have to rule out. Nothing is the
        clearer answer.

        The user's name joins the list for the same reason his does: a
        sentence that says "Morning, Corn." because `speak` put the name
        there a moment earlier is the opposite of the failure `_stray_capital`
        catches, and refusing it would refuse the whole of arm 9b. Still
        empty with no persona file *and* no about-me header, so the shipped
        default passes what it always passed.
        """
        words: list[str] = []
        if self.name != DEFAULT_NAME:
            words += [w for w in self.name.split() if w[:1].isupper()]
        words += [w for w in self.user_name.split() if w[:1].isupper()]
        return tuple(words)

    def on(self, when: date) -> Occasion | None:
        """The occasion for a date, or `None`. First match wins, in order.

        Order is the loader's: his birthday, then the owner's, then whatever
        the file listed. Two occasions on one date is a thing a person can
        write and is not an error -- he says one of them, the one nearer the
        top of the file, and says it once.
        """
        for occasion in self.occasions:
            if occasion.kind != PERSON_BIRTHDAY and occasion.falls_on(when):
                return occasion
        return None

    def heads_up(self, when: date, said=lambda key: False) -> Occasion | None:
        """A person's birthday due a mention on `when`, or `None`.

        **Owner, 2026-10-13 (PLAN-PEOPLE §9.1): three days ahead, once.** A
        birthday from the people store is due from `lead` days before it
        through the day itself, and said the first time he speaks in that
        window -- not on the third day only, because a day the owner does not
        talk to him would then lose it for the year. `said(key)` is whether
        that birthday (`heads_up_key`) was already mentioned; the caller's
        `Marker` answers it across restarts. Kept out of `on`, which decides
        the day's register: someone else's birthday in three days is not a
        reason for him to be brighter today.
        """
        for occasion in self.occasions:
            if occasion.kind != PERSON_BIRTHDAY:
                continue
            day = occasion.next_on(when)
            if (day - when).days <= occasion.lead and not said(heads_up_key(occasion, when)):
                return occasion
        return None


def heads_up_key(occasion: Occasion, when: date) -> str:
    """One birthday, one year: what `Marker` records once it has been said."""
    return f"{occasion.who}@{occasion.next_on(when).isoformat()}"


DEFAULT = Persona()


class Marker:
    """The last day an occasion was actually spoken. One field, one file.

    **Why it is on disk at all.** "The first time you talk to him that day" has
    to survive the server being restarted, or a birthday is announced afresh
    every time the process comes up. That makes it per-machine state written by
    running the agent, which is what `notes.jsonl`, `escalations.jsonl` and
    `agent_ledger.jsonl` already are, and it is gitignored beside them.

    **Never fatal, on `DayLog`'s terms and the Book's.** A state file that
    cannot be read or written must not take out a turn: the worst a failure
    here can cost is a birthday mentioned twice, and the worst an exception
    would cost is the conversation. So both halves swallow, and the read
    swallows into "not said yet", which is the direction that keeps the
    feature working rather than the one that silently disables it.
    """

    def __init__(self, path: Path | str = DEFAULT_STATE):
        self.path = Path(path)

    def said(self, when: date) -> bool:
        try:
            row = json.loads(self.path.read_text(encoding="utf-8"))
            return row.get("last_occasion") == when.isoformat()
        except Exception:
            return False

    def _row(self) -> dict:
        try:
            row = json.loads(self.path.read_text(encoding="utf-8"))
            return row if isinstance(row, dict) else {}
        except Exception:
            return {}

    def _write(self, row: dict) -> None:
        try:
            self.path.write_text(json.dumps(row) + "\n", encoding="utf-8")
        except Exception:
            pass

    def record(self, when: date) -> None:
        # Read-modify-write, so the heads-up record below survives the day's
        # own mention and the reverse.
        self._write({**self._row(), "last_occasion": when.isoformat()})

    # **Which people's birthdays have been mentioned** (`Persona.heads_up`):
    # `who@YYYY-MM-DD` keys, the newest `HEADS_UP_KEPT`. A birthday is said
    # once a year, so a bounded list is the whole memory it needs.
    HEADS_UP_KEPT = 64

    def heads_up_said(self, key: str) -> bool:
        return key in self._row().get("heads_up", [])

    def record_heads_up(self, key: str) -> None:
        row = self._row()
        keys = [k for k in row.get("heads_up", []) if k != key] + [key]
        self._write({**row, "heads_up": keys[-self.HEADS_UP_KEPT:]})
