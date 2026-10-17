"""Three tools `checkup` measures with denominators of three and five. A grid.

**The instrument this project does not have, for the three failures Phase 3 is
about.** `harness/checkup.py` carries five out-of-scope cases, two contact cases
and three note cases, and on 2026-08-26 it read `held_back` **2/5** with all
three misses landing on `web_search`. That is a real failure and it is also a
rate with a denominator of five. `harness/searchgrid.py` already made the
argument for what to do about that -- fifteen questions said "he needs an
imperative" and a grid said the fifteen questions were measuring the wrong
axis -- and this file is that argument applied to `decline`, to the contact
carriers, and to `save_note` under content it was never shown.

Three grids, one file, one report, because they share every mechanic: a live
server, greedy decode, a reset per turn, rates rather than gates, and
`--json` into `harness/results/`. Splitting them into three modules would have
copied `run_turn` three times so that three reports could disagree about what
`routed` means.

**No `--search` needed, and it is the same property `searchgrid` names.**
Routing and slot extraction both happen before any tool runs, so every row here
is decided with `web_search` still answering out of `FACTS` and nothing leaving
the machine. Run it table-backed. The one thing that does touch the world is
`save_note`, which writes -- so point the server at a scratch `--notes` path,
exactly as `checkup` requires.

---

## What `routed` counts, and the field it has to read first

**Since 2026-08-26 the runtime answers some turns itself, and a grid that could
not see that would be scoring the runtime as the model.** `corn/agent.py` routes
temporal questions and social turns off hatches that write the call by hand, and
those call events carry `author: "runtime"`. So:

    routed          the first **model-authored** call of the turn is the tool
                    the cell expects. A runtime-authored call is not a miss and
                    is not a hit -- it is excluded, and counted on its own line
    hatched         how many turns the runtime answered without a decode. This
                    should be **zero** on every cell here, and it is asserted
                    rather than hoped for: `scripts/check_toolgrid.py` runs
                    every utterance below through `corn.agent.temporal_request`,
                    `conversational_reply` and the confirmation gate's orphan
                    vocabulary and fails the build if any of them fires

The fills are designed so no case *can* hatch, which is the stronger version of
reading the field. Both are here because a design intention that nothing
enforces is the thing `scripts/check_layering.py` exists to stop being true by
accident.

## The pools are copied, and the copy is pinned

`scripts/check_layering.py` forbids `harness/` from importing `corn/toolgen.py`
or `corn/toolspace.py` -- the generators stay behind when this package becomes
its own repository -- so every trained pool this grid measures is written out a
second time below. `scripts/check_toolgrid.py` asserts each copy equals the
corpus's exactly, on `check_searchgrid.py`'s argument: a phrasing added to the
corpus and not here would leave the grid reporting a denominator that no longer
covers what he was taught, and the two runs either side of that change would be
quoted against each other anyway.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_ftextract/ckpt.pt \
        --notes /tmp/toolgrid.jsonl --no-log
    python -m harness.toolgrid
    python -m harness.toolgrid --json harness/results/ckpt__toolgrid.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from corn.tools import CONTACTS, first_names, shed_overrun

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import line as provenance_line
from .provenance import revision

# ===========================================================================
# Grid A -- decline
# ===========================================================================
#
# **The live failure, and why a list of three cannot say what caused it.**
# "play some music", "order me a taxi" and "turn the heating up" all went to
# `web_search`. Two variables are crossed in those three sentences and neither
# is separable from the other: they are trained out-of-scope strings *and* they
# are smart-home, media and commerce requests. This grid pulls them apart.
#
# **Axis 1, phrasing family.** `trained` are the ask frames of the decline
# slice -- `corn/toolspace.py`'s `DOMAINS`, the pool that produced
# `data/raw/toolspace_decline_composed.txt`, which `configs/mix_v3.py` puts in
# every 260M corpus. `novel` are action requests written here.
#
# **Axis 2, request category**, pre-registered in `docs/PLAN-P3-RULERS.md`:
# smart-home, media, commerce, timers-alarms.

# **Three of the four categories, and the fourth is the first result.** The
# decline slice has **sixteen** training domains and not one of them controls
# anything in a house -- no heating, no lights, no doors, no appliances. So
# `smart_home` has no trained cell to fill, and three of the four live failures
# were smart-home requests. That is a fact about the corpus discovered at build
# time rather than a gap in this file, it is the plan's third pre-registered
# reading arriving before a single turn was run, and inventing a frame to fill
# the hole would have destroyed it. The cell is reported empty.
#
# **Two exclusions inside the categories that do exist, and both are confounds
# rather than taste.** `toolspace`'s `track` domain asks "look for {v}" and
# "find {v}", and "look for {q}" is a `SEARCH_TEMPLATE` *verbatim* -- a turn
# that sinks to `web_search` on that carrier is the model doing exactly what
# the corpus taught, not failing to decline, and pooling it with the rest would
# have put trained-correct behaviour in the miss column. Only `play me {v}`
# survives from that domain. Everything else here was checked the same way and
# `check_toolgrid.py` asserts the property rather than trusting this comment.
#
# The domains left out entirely are the ones a **declared tool covers**:
# `note` is `save_note`, and `recipe`, `route`, `forecast`, `booking`, `invoice`
# and `battery` are lookups `web_search` is right to take. Declining those
# would be the wrong answer, so a grid that scored them would be measuring the
# opposite of what it reports.
DECLINE_FRAMES: dict[str, tuple[str, tuple[str, ...]]] = {
    # domain: (category, ask frames -- byte-identical to DOMAINS[n][4])
    "timer": ("timers_alarms", (
        "set a timer for {v}",
        "start a {v} timer",
        "give me a {v} timer",
        "can you put a timer on for {v}",
    )),
    "alarm": ("timers_alarms", (
        "set an alarm for {v}",
        "wake me at {v}",
        "alarm for {v} please",
        "can you set an alarm for {v}",
    )),
    "reminder": ("timers_alarms", (
        "remind me to {v}",
        "set a reminder to {v}",
        "don't let me forget to {v}",
        "put a reminder on to {v}",
    )),
    "playlist": ("media", (
        "start {v}",
        "put {v} on",
        "queue up {v}",
    )),
    "track": ("media", (
        "play me {v}",
    )),
    "shopping_list": ("commerce", (
        "add {v} to the list",
        "put {v} on the shopping list",
        "we need {v}",
    )),
    "subscription": ("commerce", (
        "cancel {v}",
        "stop {v}",
        "get rid of {v}",
    )),
}

# Every category the plan pre-registered, including the one with no trained
# frames. Listed rather than derived from `DECLINE_FRAMES`, so the empty cell
# appears in the report instead of vanishing from it.
CATEGORIES = ("smart_home", "media", "commerce", "timers_alarms")

# **Novel fills, and the reason they are not the table's own values.** The
# obvious move is to fill a trained frame from its trained value pool, and it
# would have been wrong: `configs/mix_v3.py` built the decline slice with
# `--values composed`, so the corpus emitted `corn/toolvalues.py`'s ~9,540
# strings, and those overlap the `DOMAINS` table heavily -- "set a timer for ten
# minutes" and "queue up the running mix" are both in the file, checked rather
# than assumed. A trained frame carrying a trained fill is an utterance the
# model may have seen entire, and a hit on it would be recall rather than
# routing, which confounds the exact axis this grid is for.
#
# So the fill is novel in **both** arms of axis 1 and only the carrier moves,
# which is `searchgrid`'s discipline of holding everything but one variable
# still. `check_toolgrid.py` asserts none of these renders appears in
# `data/raw/toolspace_decline_composed.txt` when that file is on disk.
DECLINE_FILLS: dict[str, tuple[str, ...]] = {
    # **Written against `corn/toolvalues.py`'s shapes rather than away from its
    # strings**, because the first draft of this pool was written away from its
    # strings and eleven of the fifty-six were in the corpus anyway. That
    # generator composes durations as `{n} seconds|minutes|hours`, `{n} and a
    # half ...`, `an hour and {n} minutes`, `{a} hours {b} minutes` and
    # `{a} minutes {b} seconds` over a fixed number pool, and times as
    # `{hour} {minute} {am|pm}` or `{quarter|half|ten|twenty} past|to {hour}`.
    # Every fill below is a shape none of those can produce -- a fraction, a
    # hundreds count, a bare hour-and-a-bit, a named hour the pool lacks
    # (midnight, noon), or a trailing "in the morning" the frames never append.
    "timer": (
        "two thirds of an hour", "a hundred and twenty seconds",
        "a quarter of an hour", "three quarters of an hour",
        "an hour and a bit", "three hundred seconds",
        "an hour and twenty", "just under ten minutes",
    ),
    "alarm": (
        "half past midnight", "five past midnight",
        "half four in the morning", "ten past noon",
        "quarter to six in the evening", "one fifteen in the afternoon",
        "twenty past seven tomorrow morning", "eight forty in the morning",
    ),
    "reminder": (
        "descale the kettle", "move the car before eight",
        "sign the school form", "take the suit to the cleaners",
        "top up the parking", "put the recycling bin out",
        "phone the vet about the booster", "defrost the freezer drawer",
    ),
    "playlist": (
        "the rainy afternoon one", "my washing up mix",
        "the long drive north set", "the quiet study one",
        "the kitchen dancing mix", "the pre-dinner one",
        "the sunday papers set", "the walking home one",
    ),
    "track": (
        "the one they play at the end of the film",
        "that song about a lighthouse",
        "the sped up version", "the one from the advert",
        "that duet with the piano", "the acoustic radio take",
        "the one about a broken clock", "that instrumental with the strings",
    ),
    "shopping_list": (
        "tinned butter beans", "a fresh bag of oats", "some cheap tea lights",
        "a jar of piccalilli", "a pack of AAA batteries",
        "a bottle of white vinegar", "some flat leaf parsley", "a bag of ice",
    ),
    "subscription": (
        "that thing that takes four pounds a month",
        "the crossword app", "the seed box delivery",
        "the wine club", "the parking permit renewal",
        "the online chess membership", "the recipe box", "the photo backup plan",
    ),
}

# **The novel arm: eight per category, and none of them may name a declared
# tool.** That constraint is the plan's and it is load-bearing -- "text Dave and
# ask him to order a taxi" is a `send_text` request wearing a commerce coat, and
# routing it to `send_text` would be correct. `check_toolgrid.py` asserts the
# absence of every declared tool's vocabulary.
#
# Two near-misses were rewritten rather than kept, and they are worth naming so
# the next person does not put them back. "get me a cab" opens with `get me
# {q}`, a `SEARCH_TEMPLATES_WIDE` carrier; "let me know when an hour's up" opens
# with `let {c} know {m}`, a `TEXT_TEMPLATE`. Both would have been scored as
# routing failures when the model was reading a carrier the corpus taught it.
NOVEL_REQUESTS: dict[str, tuple[str, ...]] = {
    "smart_home": (
        "turn the thermostat down two degrees",
        "close the blinds in the front room",
        "switch the porch light on",
        "put the immersion heater on for an hour",
        "open the kitchen window a crack",
        "set the hallway lamp to dim",
        "run the washing machine on a quick cycle",
        "turn the extractor fan off",
    ),
    "media": (
        "put something jazzy on in the kitchen",
        "skip to the next song",
        "turn the volume down a bit",
        "pause whatever's playing",
        "shuffle my saved songs",
        "put the football commentary on",
        "play that album from the start",
        "stick a podcast on for the drive",
    ),
    "commerce": (
        "order a bag of coffee beans",
        "order a cab to the station for half seven",
        "renew the car insurance",
        "buy two tickets for saturday",
        "return the boots that didn't fit",
        "top up my travel card",
        "cancel the veg box this week",
        "book the dog into the kennels",
    ),
    "timers_alarms": (
        "ping me in twenty minutes",
        "buzz me when the pasta's done",
        "wake me up before the match starts",
        "give me a nudge at half nine",
        "count me down from three minutes",
        "snooze that for ten",
        "set something to go off at midday",
        "go off when an hour's up",
    ),
}


# ===========================================================================
# Grid B -- send_text / place_call carriers
# ===========================================================================
#
# **Finding 52's question, asked of the tools it was never asked of.** Twenty-
# five trained `web_search` phrasings and about four carried the tool; nobody has
# run that measurement on the contact tools, and the live miss that motivates it
# is "send a text to Sam Iversen" arriving as `ask_agent`.
#
# Every carrier the corpus teaches, not a sample -- `searchgrid`'s rule, for its
# reason: the first cut of that file grouped carriers into grammatical classes
# and the means hid a spread that lived *between* templates rather than between
# their classes.

# Byte-identical to `corn/toolgen.py`'s `CALL_TEMPLATES`.
CALL_CARRIERS = (
    "call {c}", "give {c} a call", "ring {c}", "phone {c}", "get {c} on the phone",
    "can you call {c}", "call {c} for me", "dial {c}", "put me through to {c}",
    "I need to speak to {c}", "get hold of {c}", "call up {c}",
    "ring {c} for me", "give {c} a ring", "can you get {c} on the phone",
    "I want to talk to {c}", "start a call with {c}", "call {c} now",
    "could you ring {c}", "get me {c}", "try {c}", "try calling {c}",
    "let's call {c}", "phone up {c}", "I need {c} on the line",
    "connect me to {c}", "would you call {c}", "call {c} please",
)

# Byte-identical to `corn/toolgen.py`'s `TEXT_TEMPLATES`.
TEXT_CARRIERS = (
    "text {c} {m}", "send {c} a text saying {m}", "message {c} {m}",
    "let {c} know {m}", "tell {c} {m}", "send a text to {c} saying {m}",
    "shoot {c} a message saying {m}", "drop {c} a text {m}",
    "can you text {c} and say {m}", "text {c} and tell them {m}",
    "message {c} saying {m}", "send {c} a message {m}",
    "text {c} to say {m}", "let {c} know that {m}",
    "could you text {c} {m}", "send a message to {c} saying {m}",
    "text {c} saying {m}", "write to {c} and say {m}",
    "tell {c} that {m}", "drop a line to {c} saying {m}",
    "please text {c} {m}", "message {c} and tell them {m}",
)

# **The plan named four carriers "measured failing live" and three of them are
# already in the pool above.** "let {c} know that {m}", "tell {c} that {m}" and
# "shoot {c} a message saying {m}" are `TEXT_TEMPLATES` entries verbatim, which
# is worth more than a fourth column: whatever went wrong live, it was not that
# the corpus had never shown him the phrasing. `check_toolgrid.py` asserts that
# membership so the claim cannot quietly stop being true.
#
# The one that is genuinely absent is the one the live miss actually used:
# **a text request with no message in it.** Every one of the twenty-two carriers
# above carries `{m}`, so "send a text to Sam Iversen" is a shape the slice does
# not contain at all. It gets its own row class -- `kept_message` cannot apply
# to a turn that named no message -- and it is the single most interesting cell
# in this grid.
MESSAGELESS_CARRIERS = (
    "send a text to {c}",
    "text {c}",
    "drop {c} a message",
)

# Byte-identical to `corn/toolgen.py`'s `MESSAGES`. A *trained* fill, on
# purpose: Grid B's axis is the carrier, so the message is held in the
# distribution the corpus taught, exactly as the plan holds the name axis to the
# default book to keep routing from being confounded with lookup.
MESSAGES = (
    "I'm running late", "on my way", "call me when you can", "see you at six",
    "the meeting moved to Thursday", "can't make it tonight", "landed safely",
    "bring the charger", "I'll be there in ten", "sorry, just seen this",
    "dinner's at eight", "we're outside", "no rush", "it's sorted",
    "train's delayed", "I'll bring the wine", "can we push it back an hour",
    "all done here", "give me five minutes", "parked round the back",
    "forgot my keys", "happy birthday", "good luck tomorrow",
    "thanks for today", "I'll call you later", "leaving now",
)


def trained_first_names(book: tuple[str, ...] = CONTACTS) -> tuple[str, ...]:
    """Unambiguous first names from the default book.

    **Trained names only, and the plan says why**: an unseen name is finding
    14's territory, already measured, and mixing it in would confound routing
    with lookup. Drawn from the book rather than listed here for
    `invented_subjects`' reason -- a name written into this file that later left
    the book would become an unseen-name miss dressed as a routing one.

    Unambiguous only, because a shared first name is a *correct* clarify and
    would land in the same column as a wrong one.
    """
    return tuple(sorted(n for n, full in first_names(book).items()
                        if len(full) == 1))


# ===========================================================================
# Grid C -- save_note under hostile content
# ===========================================================================
#
# The live miss is one turn: "note down dentist appointment moved to friday"
# arrived as `web_search`. One turn is not a finding, and the honest null here
# is that it was noise -- which one grid cell settles either way.
#
# Carrier crossed across every trained note carrier, content crossed across four
# classes. Byte-identical to `corn/toolgen.py`'s `NOTE_TEMPLATES`.
NOTE_CARRIERS = (
    "make a note {t}", "note down {t}", "write down {t}",
    "jot down {t}", "make a note to self {t}", "save a note {t}",
    "take a note {t}", "put in my notes {t}", "note to self {t}",
    "add a note {t}", "write a note {t}", "keep a note {t}",
    "note that {t}", "write down that {t}", "make a note that {t}",
    "save that {t}", "put down {t}", "get this down {t}",
    "can you note down {t}", "could you write down {t}",
    "stick a note in about {t}", "log that {t}",
)

# The four classes are the plan's, and its examples are kept verbatim where it
# gave them -- they are pre-registered items and rewriting them would be editing
# a hypothesis after seeing the data.
#
# `plain` is the control and is deliberately trained content: it is the cell
# that must work for any of the other three to mean anything, which is the
# argument `searchgrid`'s invented column makes.
NOTE_CONTENT: dict[str, tuple[str, ...]] = {
    "plain": (
        "buy milk",
        "the spare key is under the pot",
    ),
    "date_bearing": (
        "dentist appointment moved to friday",
        "rent is due on the 3rd",
    ),
    "question_shaped": (
        "whether the store opens at nine",
        "if the parcel needs signing for",
    ),
    "real_entity": (
        "the plumber's name is Marcus Webb",
        "the boiler is a Worcester Bosch",
    ),
}


# ===========================================================================
# the turns
# ===========================================================================

# Everything the runtime offers. Used only to assert that a Grid A item names
# none of them -- see `NOVEL_REQUESTS`.
DECLARED = ("place_call", "send_text", "save_note", "web_search",
            "resolve_date", "recall_day", "ask_agent", "decline")


@dataclass
class Turn:
    """One utterance and what came back. Verdicts are properties, not fields.

    Computed rather than stored for `checkup.Outcome`'s reason: the JSON card
    and the printed table are then built from one implementation of each row,
    so a card cannot come to describe a run the terminal did not show.
    """
    grid: str            # "A" | "B" | "C"
    cell: str            # category, or content class
    carrier: str         # the phrasing, or "(whole utterance)" for novel items
    family: str          # "trained" | "novel" | "messageless"
    ask: str
    expect: str          # the tool the cell wants
    said_contact: str | None = None
    said_message: str | None = None
    said_text: str | None = None
    calls: list[dict] = field(default_factory=list)
    obs: list[dict] = field(default_factory=list)
    reply: str = ""
    error: str | None = None

    # -- what the runtime did, kept apart from what the model did ------------

    @property
    def hatched(self) -> bool:
        """The runtime answered without a decode.

        Ground rule 2 of `docs/PLAN-P3-RULERS.md`: a runtime-authored call is
        neither a hit nor a miss, because the model was never consulted. Every
        cell here is designed so this is `False`; it is read anyway, because a
        design intention nothing reads is how a grid comes to score a hatch as a
        routing success.
        """
        return any(c.get("author") == "runtime" for c in self.calls)

    @property
    def model_calls(self) -> list[dict]:
        """The calls the model wrote. Absence of `author` means the model.

        `corn/agent.py` stamps `author` on the hatch path only, so the normal
        decode path emits a call event without the field at all -- read as
        "model" here rather than as "unknown", which is what it means.
        """
        return [c for c in self.calls if c.get("author", "model") != "runtime"]

    @property
    def called(self) -> str | None:
        """The first tool the *model* reached for, or None if it reached for none.

        A call the validator could not name is not None -- `checkup.Outcome`'s
        rule, for its reason: collapsing a malformed grab at a tool into "no
        call" would score it as restraint.
        """
        if not self.model_calls:
            return None
        return self.model_calls[0].get("name") or "<malformed>"

    @property
    def args(self) -> dict:
        first = self.model_calls[0].get("arguments") if self.model_calls else None
        return first if isinstance(first, dict) else {}

    # -- rows ----------------------------------------------------------------

    @property
    def routed(self) -> bool:
        return not self.hatched and self.called == self.expect

    @property
    def sunk(self) -> bool:
        """The miss landed on `web_search` specifically.

        Reported apart from the other misses because all three live failures
        were this one sink, and a miss that reaches `save_note` is a different
        fact about the corpus -- one is "he thinks every request is a lookup",
        the other is "he thinks every request is worth writing down".
        """
        return not self.hatched and self.called == "web_search" \
            and self.expect != "web_search"

    @property
    def kept_contact(self) -> bool | None:
        """The contact slot carries the name that was said. Raw, pre-repair."""
        if self.said_contact is None or not self.routed:
            return None
        return _same_name(self.args.get("contact"), self.said_contact)

    @property
    def kept_contact_shed(self) -> bool | None:
        """...and again after `shed_overrun` has trimmed the message it ate.

        **Recorded separately so the repair's live contribution is a counted
        number rather than a claim.** `corn/tools.py`'s `shed_overrun` is
        applied inside `send_text_tool`, so it fires on this path whether or not
        the confirmation gate is holding the action -- but nothing until now has
        said how often it fires, or how often it *matters*. The difference
        between this row and the one above is that number.

        `place_call` gets no repair by design -- with no message there is no
        evidence -- so the row does not apply to it, and reporting it as a hit
        there would inflate the repair's credit with turns it never touched.
        """
        if self.said_contact is None or not self.routed:
            return None
        if self.expect != "send_text":
            return None
        raw = self.args.get("contact")
        if not isinstance(raw, str):
            return False
        message = self.args.get("message")
        shed = shed_overrun(raw, message if isinstance(message, str) else "",
                            CONTACTS)
        return _same_name(shed, self.said_contact)

    @property
    def kept_message(self) -> bool | None:
        if self.said_message is None or not self.routed:
            return None
        return _carries(self.args.get("message"), self.said_message)

    @property
    def kept_text(self) -> bool | None:
        if self.said_text is None or not self.routed:
            return None
        return _carries(self.args.get("text"), self.said_text)

    def rows(self) -> dict[str, bool | None]:
        return {
            "routed": None if self.hatched else self.routed,
            "kept_contact": self.kept_contact,
            "kept_contact_shed": self.kept_contact_shed,
            "kept_message": self.kept_message,
            "kept_text": self.kept_text,
        }


ROWS = ("routed", "kept_contact", "kept_contact_shed", "kept_message",
        "kept_text")


def _words(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()


def _same_name(got: object, want: str) -> bool:
    """Case-insensitive on the bare string, first name counts, either way round.

    `checkup._named_right`'s rule and `score_name_fidelity`'s before it: the
    corpus refers to contacts by first name three times in four, so demanding a
    full name would fail a correct call.

    **The expansion direction is allowed and is gated on the book, and the gate
    is the whole subtlety.** `checkup` always asks with a *full* name, so it
    only ever needs "he shortened it". Grid B's fills are first names -- the
    plan's constraint, to keep routing from being confounded with lookup -- so
    the direction that matters here is the other one: asked for Priya, called
    Priya Raman, which is correct and would otherwise score as a slot failure.

    But "starts with the name I said" is exactly what the **overrun** looks
    like: `text Priya that I am running late` puts `Priya that I am running
    late` in the slot, and a bare prefix test would score that a hit and leave
    `kept_contact_shed` reporting that the repair contributes nothing. So an
    expansion counts only when the whole string is a **book entry** whose first
    name is what was said -- which no overrun can be, because the overrun
    carries the message and the book does not.
    """
    if not isinstance(got, str):
        return False
    g, w = got.strip().lower(), want.strip().lower()
    if not g or not w:
        return False
    if g == w or g == w.split()[0]:
        return True
    return any(g == full.lower() and full.split()[0].lower() == w
               for full in CONTACTS)


def _carries(got: object, want: str) -> bool:
    """The slot carries what was said, compared on content words.

    Not a substring test, for `Turn.kept_subject`'s reason in
    `harness/searchgrid.py`: he routinely reshapes a span, and a reshaping that
    kept every content word has kept the thing. Every content word is required
    rather than a threshold, because a note that dropped half its text is a note
    of something nobody said.
    """
    if not isinstance(got, str) or not got.strip():
        return False
    want_w = _words(want)
    got_w = set(_words(got))
    return bool(want_w) and all(w in got_w for w in want_w)


def build(seed: int = 0) -> list[Turn]:
    """Every turn the grid will run, before any of them runs.

    **Pure, seeded, and separated from the running for one reason**:
    `scripts/check_toolgrid.py` calls this and puts every utterance through the
    runtime's hatches, so ground rule 2's "no case can hatch" is checked against
    the same list the grid will actually send rather than against a description
    of it.
    """
    rng = random.Random(seed)
    turns: list[Turn] = []

    # -- Grid A ------------------------------------------------------------
    for domain, (category, frames) in DECLINE_FRAMES.items():
        for frame in frames:
            for fill in DECLINE_FILLS[domain]:
                turns.append(Turn(grid="A", cell=category, carrier=frame,
                                  family="trained", ask=frame.format(v=fill),
                                  expect="decline"))
    for category, asks in NOVEL_REQUESTS.items():
        for ask in asks:
            turns.append(Turn(grid="A", cell=category, carrier="(whole utterance)",
                              family="novel", ask=ask, expect="decline"))

    # -- Grid B ------------------------------------------------------------
    names = trained_first_names()
    for carrier in CALL_CARRIERS:
        for name in _draw(rng, names, 8):
            turns.append(Turn(grid="B", cell="place_call", carrier=carrier,
                              family="trained", ask=carrier.format(c=name),
                              expect="place_call", said_contact=name))
    for carrier in TEXT_CARRIERS:
        for name in _draw(rng, names, 8):
            msg = rng.choice(MESSAGES)
            turns.append(Turn(grid="B", cell="send_text", carrier=carrier,
                              family="trained",
                              ask=carrier.format(c=name, m=msg),
                              expect="send_text", said_contact=name,
                              said_message=msg))
    for carrier in MESSAGELESS_CARRIERS:
        for name in _draw(rng, names, 8):
            turns.append(Turn(grid="B", cell="send_text", carrier=carrier,
                              family="messageless", ask=carrier.format(c=name),
                              expect="send_text", said_contact=name))

    # -- Grid C ------------------------------------------------------------
    for carrier in NOTE_CARRIERS:
        for cls, bodies in NOTE_CONTENT.items():
            for body in bodies:
                turns.append(Turn(grid="C", cell=cls, carrier=carrier,
                                  family="trained", ask=carrier.format(t=body),
                                  expect="save_note", said_text=body))
    return turns


def _draw(rng: random.Random, pool: tuple[str, ...], n: int) -> list[str]:
    """`n` distinct items when the pool allows it, else `n` with repeats.

    Distinct where possible so a carrier's eight fills are eight names rather
    than the same name eight times, which would make a per-carrier rate a
    measurement of one name.
    """
    if len(pool) >= n:
        return rng.sample(list(pool), n)
    return [rng.choice(pool) for _ in range(n)]


def run_turn(client: Client, turn: Turn) -> Turn:
    """One utterance from a cleared history. `checkup.run_case`'s reset, for its
    reason: history lives on the session, so against a `--multi` instance every
    turn after the first would open on the tail of the one before."""
    for _ in client.request(op="reset"):
        pass
    for ev in client.request(op="turn", user=turn.ask):
        kind = ev.get("t")
        if kind == "call":
            turn.calls.append(ev)
        elif kind == "obs":
            turn.obs.append(ev.get("payload") or {})
        elif kind == "say":
            turn.reply = ev.get("text", "")
        elif kind == "error":
            turn.error = ev.get("why", "?")
    return turn


# ===========================================================================
# the report
# ===========================================================================

@dataclass
class Cell:
    label: str
    hit: int = 0
    n: int = 0
    sunk: int = 0
    hatched: int = 0

    def add(self, turn: Turn) -> None:
        if turn.hatched:
            self.hatched += 1
            return
        self.n += 1
        self.hit += turn.routed
        self.sunk += turn.sunk

    @property
    def pct(self) -> str:
        return f"{100 * self.hit / self.n:5.1f}%" if self.n else "    --"


def _tally(turns: list[Turn], key) -> dict[str, Cell]:
    out: dict[str, Cell] = {}
    for t in turns:
        label = key(t)
        out.setdefault(label, Cell(label)).add(t)
    return out


def _table(title: str, cells: dict[str, Cell], width: int,
           order: tuple[str, ...] | None = None) -> None:
    print()
    print(f"  {title}")
    print(f"    {'':<{width}} {'routed':>12} {'sunk->web':>11}")
    labels = order if order is not None else sorted(
        cells, key=lambda k: (-cells[k].hit, k))
    for label in labels:
        c = cells.get(label) or Cell(label)
        n = f"{c.hit:>3}/{c.n:<4}" if c.n else "  no cell"
        print(f"    {label:<{width}} {n:>12} {c.sunk:>8}    {c.pct}"
              + ("   !! runtime-authored: "
                 f"{c.hatched}" if c.hatched else ""))


def _misses(turns: list[Turn]) -> dict[str, int]:
    out: dict[str, int] = {}
    for t in turns:
        if t.hatched or t.routed:
            continue
        k = t.called or "(nothing)"
        out[k] = out.get(k, 0) + 1
    return out


def _cells(cells: dict[str, Cell]) -> dict:
    return {k: [v.hit, v.n, v.sunk] for k, v in cells.items()}


def _grid_a(a: list[Turn]) -> dict:
    print()
    print("=" * 72)
    print("Grid A -- decline.  routed = the first model call is `decline`")
    trained = [t for t in a if t.family == "trained"]
    novel = [t for t in a if t.family == "novel"]
    by_cat_trained = _tally(trained, lambda t: t.cell)
    by_cat_novel = _tally(novel, lambda t: t.cell)
    _table("trained decline-slice frames, by category", by_cat_trained, 16,
           CATEGORIES)
    _table("novel action requests, by category", by_cat_novel, 16, CATEGORIES)
    by_carrier = _tally(trained, lambda t: t.carrier)
    _table("trained frames, by carrier", by_carrier, 30)

    # **The pooled delta is over the categories both arms have, and saying so is
    # not pedantry.** `smart_home` is novel-only, and it is the category three of
    # the four live failures came from -- pooling a novel-only cell into a
    # trained-versus-novel difference would put the hardest cell on one side of
    # the comparison and nothing on the other.
    shared = tuple(k for k in CATEGORIES if by_cat_trained.get(k, Cell(k)).n)
    tr = [t for t in trained if t.cell in shared]
    nv = [t for t in novel if t.cell in shared]
    tr_r, nv_r = sum(t.routed for t in tr), sum(t.routed for t in nv)
    print()
    print(f"  shared categories: {', '.join(shared) or '(none)'}")
    if tr and nv:
        print(f"  pooled over those   trained {tr_r}/{len(tr)} "
              f"({tr_r / len(tr):.0%})   novel {nv_r}/{len(nv)} "
              f"({nv_r / len(nv):.0%})   "
              f"delta {tr_r / len(tr) - nv_r / len(nv):+.0%}")
    only_novel = tuple(k for k in CATEGORIES
                       if k not in shared and by_cat_novel.get(k, Cell(k)).n)
    if only_novel:
        print(f"  !! no trained frame exists for {', '.join(only_novel)} -- the "
              f"decline slice has no such domain, so the cell is novel-only")
    print(f"  the misses reached  {_spread(_misses(a))}")
    return {
        "by_category": {"trained": _cells(by_cat_trained),
                        "novel": _cells(by_cat_novel)},
        "by_carrier": _cells(by_carrier),
        "shared_categories": list(shared),
        "pooled_shared": {"trained": [tr_r, len(tr)], "novel": [nv_r, len(nv)]},
        "misses": _misses(a),
    }


def _grid_b(b: list[Turn]) -> dict:
    print()
    print("=" * 72)
    print("Grid B -- contact carriers.  routed = the tool the carrier names")
    calls = [t for t in b if t.expect == "place_call"]
    texts = [t for t in b if t.expect == "send_text"]
    trained_texts = [t for t in texts if t.family == "trained"]
    bare = [t for t in b if t.family == "messageless"]
    _table("place_call carriers", _tally(calls, lambda t: t.carrier), 30)
    _table("send_text carriers, trained",
           _tally(trained_texts, lambda t: t.carrier), 30)
    _table("send_text carriers, messageless (untrained shape)",
           _tally(bare, lambda t: t.carrier), 30)
    print()
    _slots("place_call", calls)
    _slots("send_text", texts)
    print(f"  the misses reached  {_spread(_misses(b))}")
    return {
        "by_carrier": _cells(_tally(b, lambda t: t.carrier)),
        "families": {"trained": _rowcard([t for t in b if t.family == "trained"]),
                     "messageless": _rowcard(bare)},
        "slots": {"place_call": _rowcard(calls), "send_text": _rowcard(texts)},
        "misses": _misses(b),
    }


def _grid_c(c: list[Turn]) -> dict:
    print()
    print("=" * 72)
    print("Grid C -- save_note under hostile content")
    by_class = _tally(c, lambda t: t.cell)
    by_carrier = _tally(c, lambda t: t.carrier)
    _table("by content class", by_class, 18, tuple(NOTE_CONTENT))
    _table("by carrier", by_carrier, 30)
    print()
    _slots("save_note", c)
    print(f"  the misses reached  {_spread(_misses(c))}")
    return {"by_class": _cells(by_class), "by_carrier": _cells(by_carrier),
            "slots": _rowcard(c), "misses": _misses(c)}


def report(turns: list[Turn], info: dict) -> dict:
    """One section per grid that was actually run.

    **A grid nobody ran prints nothing rather than a table of empty cells.**
    `--grid A` is the ordinary way to re-read one axis after a corpus change,
    and three empty tables under it are three invitations to quote a rate with
    no denominator behind it.
    """
    grids: dict[str, dict] = {}
    for name, fn in (("A", _grid_a), ("B", _grid_b), ("C", _grid_c)):
        rows = [t for t in turns if t.grid == name]
        if rows:
            grids[name] = fn(rows)

    # -- the field ground rule 2 exists for --------------------------------
    hatched = [t for t in turns if t.hatched]
    print()
    print("=" * 72)
    if hatched:
        print(f"!! {len(hatched)} turn(s) were answered by the runtime without a "
              f"decode and are excluded from every rate above:")
        for t in hatched[:8]:
            print(f"     {t.ask[:64]}")
        print("   the fills are supposed to make this impossible -- run "
              "`python scripts/check_toolgrid.py`")
    else:
        print("no turn was answered by a runtime hatch -- every rate above is "
              "the model")

    return {
        "harness": "toolgrid/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": revision(),
        "instance": info,
        "hatched": len(hatched),
        "grids": grids,
        "turns": [
            {"grid": t.grid, "cell": t.cell, "carrier": t.carrier,
             "family": t.family, "ask": t.ask, "expect": t.expect,
             "called": t.called, "hatched": t.hatched,
             "arguments": t.args or None, "reply": t.reply.strip(),
             "rows": t.rows(), "error": t.error}
            for t in turns
        ],
    }


def _rowcard(turns: list[Turn]) -> dict:
    out: dict[str, list[int]] = {}
    for row in ROWS:
        hit = n = 0
        for t in turns:
            v = t.rows()[row]
            if v is None:
                continue
            n += 1
            hit += bool(v)
        if n:
            out[row] = [hit, n]
    return out


def _slots(label: str, turns: list[Turn]) -> None:
    card = _rowcard(turns)
    parts = [f"{r} {h}/{n} ({100 * h / n:.0f}%)" for r, (h, n) in card.items()
             if r != "routed"]
    if parts:
        print(f"  {label:<12} {'   '.join(parts)}")
    # The number the plan asked to be counted rather than claimed.
    raw, shed = card.get("kept_contact"), card.get("kept_contact_shed")
    if raw and shed and raw[1] == shed[1]:
        print(f"  {'':<12} shed_overrun's live contribution: "
              f"{shed[0] - raw[0]:+d} of {raw[1]}")


def _spread(misses: dict[str, int]) -> str:
    if not misses:
        return "(nothing missed)"
    return ", ".join(f"{k} {v}" for k, v in
                     sorted(misses.items(), key=lambda kv: -kv[1]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--seed", type=int, default=0,
                    help="which names and messages fill Grid B")
    ap.add_argument("--grid", choices=("A", "B", "C"), action="append",
                    help="run one grid only; repeatable. All three by default")
    ap.add_argument("--json", help="write the scorecard here")
    args = ap.parse_args()

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- start it with "
              f"`python -m harness.server`", file=sys.stderr)
        return 2

    info = {}
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            info = {k: v for k, v in ev.items() if k not in ("t", "id")}

    print(f"toolgrid against {info.get('ckpt')}")
    print(f"  tools declared: {len(info.get('tools') or [])}   "
          f"decline offered: {info.get('decline')}   "
          f"temperature {info.get('temperature')}   "
          f"search {info.get('search')}")
    print(f"  notes -> {info.get('notes')}   reach {info.get('reach')}")
    print(provenance_line())
    # Grid B's contact rows score the slot the model copied against the
    # trained first names -- the call's arguments, not what the runtime did
    # with them -- so they read the same on an owner-only server (no book
    # since 2026-10-13, PLAN-PEOPLE §7).
    if "decline" not in (info.get("tools") or []):
        print("\nthis instance was started with --no-decline, so Grid A is "
              "measuring a tool he was not offered.", file=sys.stderr)
        client.close()
        return 2
    print("  !! save_note writes: Grid C appends "
          f"{len(NOTE_CARRIERS) * sum(len(v) for v in NOTE_CONTENT.values())} "
          f"notes to the path above")

    planned = build(args.seed)
    if args.grid:
        planned = [t for t in planned if t.grid in args.grid]
    print(f"  {len(planned)} turns planned")

    started = time.perf_counter()
    done: list[Turn] = []
    for i, turn in enumerate(planned, 1):
        run_turn(client, turn)
        if turn.error:
            print(f"turn raised: {turn.ask!r} -- {turn.error}", file=sys.stderr)
            return 2
        done.append(turn)
        if i % 50 == 0:
            print(f"    {i}/{len(planned)} ...")

    card = report(done, info)
    card["seconds"] = round(time.perf_counter() - started, 1)
    print(f"\n  {len(done)} turns in {card['seconds']}s")
    client.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"  wrote {args.json}")

    # A rate, not a gate -- `checkup`'s contract. Non-zero above only for
    # something structural: no server, a wrong instance, a turn that raised.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
