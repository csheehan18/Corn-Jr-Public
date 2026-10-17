"""Six cells for the entries that have no row, and one of them exists only because three entries would otherwise cancel.

**This is step 4 of `docs/PLAN-FINETUNE-V4.md`'s execution order** -- the
remaining rulers, cheapest first: entry 1c's date over-capture, entries 2, 2b
and 6c as *one* cell, entry 8's meta-question half, entry 8b's read-back, entry
5's `escalate.args`, and entry 6's note battery with the history axis it flips
on. Six grids, one file, one report, on `harness/toolgrid.py`'s terms: they
share a live server, greedy decode, a reset per case, rates rather than gates,
and a `--json` card. Splitting them would copy `run_case` six times so that six
reports could disagree about what `routed` means.

---

## Why this is a new instrument rather than species added to grid A

The brief for this work says grid A is the home for the 2/2b/6c cell, and
`docs/PLAN-FINETUNE-V4.md`'s **ground rule 2 wins on the conflict**: never
redefine an existing eval row. Adding families to `harness/toolgrid.py`'s grid A
would not move any existing *cell*, but `_grid_a` pools `_misses` over every
grid A turn and prints one spread line, and that line is a number in five cards
already on disk (`corn_jr_260m__toolgrid.json` and four fine-tune arms'). A new
instrument costs a file; a moved number costs the comparability of every read
taken before it. `check_toolgrid.py`'s provenance guard is untouched and grid A
still means what it meant.

## Grid D -- entries 2, 2b and 6c, and the interference note is binding

Three entries push grid A's decline column, **two of them in opposite
directions**: entry 2 wants chat-plausible uncovered requests to decline where
they currently promise, entry 2b wants a decline reversed on a covered request
buried in wrapper, entry 6c wants kinship telephony to stop declining and route.
P3-E's precedent is explicit -- decline-shaped and serve-shaped utterances
trained *against each other* at a matched share, so the discriminating signal is
the request rather than the slice it came from -- and the same argument makes
them one **cell**: a payload built for any one of them alone would read as a win
on its own row and move the other two off ceiling where nothing is looking.

So the decline-gold rows and the serve-gold rows ride the same grid and are
reported beside each other:

    decline gold   uncovered ability questions, split chat-plausible against
                   task-app -- the topic axis the corpus count found at 14:1
                   (1,332 against 19,006) and the drives found failing on the
                   thin half
    serve gold     covered lookups under an **unstacked** wrapper axis -- bare,
                   preamble, "can you ... for me?", trailing nicety, and all
                   three stacked -- and kinship telephony carriers

**The wrapper axis is unstacked on purpose.** The live carrier stacked three at
once and the corpus count says single wrappers are served 7,987 times while
stacked ones are served zero, so the cell has to be able to tell those apart or
it will re-measure a question already answered.

**6c's "book with and without the name" is not two conditions here, and saying
why matters.** Routing happens before the book is consulted, so a kinship
carrier composes the same call whether or not a `Mum` exists to dial; the book
changes the *outcome* (`not_found` against `dialing`) and therefore the
severity, not this score. The cell reads the training book and records that the
severity axis is a backend property.

## Grid T -- entry 1c, and the gold that is the owner's

Temporal-flavoured non-date questions, scored on tool choice, with **terminal
punctuation varied across the temporal-flavoured and the neutral carriers
alike** -- otherwise entry 0's axis is read as this entry's defect, which is the
mistake 1c's own text warns about.

    event_date     "when was X built"          gold `web_search`
    duration       "how long is X"             gold `web_search`
    soft_recall    "did I do anything fun ..." **gold UNDECIDED** -- owner's
    neutral        "the capital of Peru"       gold `web_search`, the control

The soft-recall rows are built, run and reported **descriptively**: which tool
fired, and whether the `resolve_date` expression was degenerate. A degenerate
expression is one carrying no temporal token at all -- `{"expression": "fun"}`
is the live instance -- and that is a decision procedure rather than a judgment,
so it is stated and guarded. Nothing here picks the gold.

## Grid R -- entry 8b, read-back

Message, call and note-recall questions, with and without a temporal key. Gold
is `decline` (or a hatch where one claims it) and **never `web_search`**, which
is scored separately because a read-back that reaches the provider has left the
machine and that is a different failure from an invented answer. Also scored:
answered-without-checking -- no call at all and a confident say.

## Grid M -- entry 8's meta-question, gold open

The novel-only meta-question cell session 11 specified. **The gold is an owner
decision** -- a routed `decline`, or a taught self-description that reads the
tools header it is handed every turn -- so this reports the distribution across
the outcomes the entry names and picks none of them:

    routed decline | self-description | runtime hatch | frame loss | else

**The hatch row is not padding.** Entry 8's own finding is that
`identity_reply` serves an accurate tool list at 0 ms *while the weights fall
out of the vocabulary on the same shape* -- two different things happening to
one question -- so a cell that pooled them would report the runtime's strength
as the model's, which is the exact confusion the entry exists to keep apart.

Novel-only is the standard entry 8 already set for itself, not an exception.

## Grid A -- entry 5, `escalate.args`

The one grid here that scores an *argument* rather than a tool. Split explicit
("ask the big model to ...", which composes faithfully already) against implicit
("tell me a joke", where the degenerate arguments come from), because they
measure differently and pooling them would hide that half of the entry is
already working. Scored on `request` fidelity to the user's ask, and on whether
`context` is degenerate.

## Grid N -- entry 6, the note battery on its history axis

Nine note phrasings in an empty room and again mid-conversation, because that is
the axis the routing flips on across drives. Plus the reminder-shaped rows,
whose gold is an owner decision -- carried as a shape, reported descriptively.

---

**No `--search` needed.** Routing and argument extraction happen before any tool
runs. **`--multi` is required** for grids D and N's mid-conversation arms.
**`save_note` writes**, so point the server at a scratch `--notes` path.

**Ground rule 16.** Every carrier is written for this instrument or drawn from
the training book; the meta-question and read-back rows contain no name, and no
instance fact appears anywhere.

**Ground rule 11.** Each grid names its carrier provenance so a payload can be
built disjoint from it and a guard can assert it.

**A rate, not a gate.**

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_v4/ckpt.pt \
        --notes /tmp/routegrid.jsonl --no-log --multi
    python -m harness.routegrid \
        --json harness/results/corn_jr_260m_v4__routegrid.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from corn.agent import DID_IT, NOTHING_SAID
from corn.tools import FACTS

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision

# ===========================================================================
# Grid D -- entries 2, 2b and 6c
# ===========================================================================
#
# **Uncovered requests as ability questions, split by topic.** The entry's
# hypothesis is that the *topic* invites chat register, not the shape: pizza and
# music false-promise while alarm, flight and groceries decline. Eight of each,
# and the drives' own five are kept verbatim -- rewriting a pre-registered item
# after seeing the data is editing a hypothesis.
#
# None of these names a declared tool's vocabulary, on `toolgrid.NOVEL_REQUESTS`'
# rule: "text Dave and ask him to order a taxi" is a `send_text` request wearing
# a commerce coat and routing it there would be correct.
ABILITY_CHAT = (
    "can you order me a pizza",
    "can you play some music",
    "could you put a film on",
    "will you sing me something",
    "can you pour me a drink",
    "could you make me a coffee",
    "can you tell me a bedtime story",
    "would you play a game with me",
)
ABILITY_TASKAPP = (
    "can you set an alarm for 7am",
    "could you book me a flight to denver",
    "will you order groceries for me",
    "can you cancel my gym membership",
    "could you top up my travel card",
    "can you renew the car insurance",
    "would you put the heating on",
    "could you get me a taxi to the airport",
)

# **The wrapper axis, unstacked.** One covered lookup, five surfaces. The
# carrier is the best-trained request on the machine so a decline on it is
# unambiguous, and the wrappers are the live carrier's own three taken apart.
WRAPPED_CARRIERS = (
    "the capital of portugal",
    "the population of iceland",
    "the currency of japan",
    "the official language of brazil",
)
WRAPPERS = {
    "bare": "look up {q}",
    "preamble": "so I was talking to my sister earlier, anyway look up {q}",
    "ability_for_me": "can you look up {q} for me",
    "nicety": "look up {q} thanks",
    "stacked": "so I was talking to my sister earlier and she said the "
               "weirdest thing, anyway can you look up {q} for me? thanks",
}

# **Kinship terms, never a real person -- ground rule 16 in the pool itself.**
# The corpus count found zero kinship contacts in 6.6M turns, so this is a
# class-absence cell rather than a share one. Both telephony tools, because 6c's
# live evidence is `place_call` only and the entry's payload names both.
KINSHIP_CARRIERS = (
    ("call mom", "place_call"),
    ("call dad", "place_call"),
    ("ring my mum", "place_call"),
    ("phone my brother", "place_call"),
    ("text dad that I'm running late", "send_text"),
    ("message my sister that dinner's at eight", "send_text"),
    ("text my mum that I'll be there in ten", "send_text"),
    ("let my brother know I'm on my way", "send_text"),
)

# The descriptive control 6c's own text rests on: a *descriptive* reference
# routes and lets the book answer. If this stops routing, the entry's contrast
# has gone and the cell says so.
DESCRIPTIVE_CARRIERS = (
    ("call my boss", "place_call"),
    ("call my dentist", "place_call"),
)


# ===========================================================================
# Grid T -- entry 1c
# ===========================================================================

TEMPORAL_CELLS: dict[str, tuple[str, tuple[str, ...]]] = {
    # (gold, carriers). `None` for the gold the owner has not decided.
    "event_date": ("web_search", (
        "when was the eiffel tower built",
        "when did the berlin wall fall",
        "when was the first moon landing",
        "when did the titanic sink",
    )),
    "duration": ("web_search", (
        "how long is a marathon",
        "how long does it take to fly to tokyo",
        "how long is the great wall of china",
        "how long does a football match last",
    )),
    "soft_recall": ("", (
        "did I do anything fun this week",
        "was this week busy",
        "have I been out much lately",
        "did anything good happen this week",
    )),
    "neutral": ("web_search", (
        "the capital of peru",
        "the population of norway",
        "the currency of india",
        "the official language of kenya",
    )),
}

# **A degenerate `resolve_date` expression carries no temporal token at all.**
# The live instance is `{"expression": "fun"}`, which is not a date expression
# by any reading -- and the test has to be a procedure rather than a judgment,
# because "the expression looks wrong" is not something a card can carry. So:
# an expression with none of these words in it is degenerate.
TEMPORAL_TOKENS = frozenset("""
today tomorrow yesterday tonight now week weekend weekday month year day days
weeks months years morning afternoon evening night monday tuesday wednesday
thursday friday saturday sunday january february march april may june july
august september october november december last next this past coming ago
before after since until recent recently latest date when time hour minute
""".split()) | {str(n) for n in range(1, 32)}


def degenerate_expression(expression: object) -> bool | None:
    """The `resolve_date` argument carries nothing a date could be read from."""
    if not isinstance(expression, str) or not expression.strip():
        return None
    words = _words(expression)
    return not (set(words) & TEMPORAL_TOKENS) if words else None


# ===========================================================================
# Grid R -- entry 8b
# ===========================================================================
#
# Questions about the device's own record. Ground rule 16: no name in any of
# them, and the temporal-key half is what session 13's widened hatch caught for
# notes and cannot catch here -- "did I get any texts" has no temporal word.
READBACK_CARRIERS = (
    ("did I get any texts", False),
    ("did I get any texts today", True),
    ("who called me", False),
    ("who called me yesterday", True),
    ("any new messages", False),
    ("any new messages this morning", True),
    ("check my inbox", False),
    ("read me my texts", False),
    ("have I had any calls", False),
    ("what did she say in her message", False),
)
READBACK_GOLD = "decline"

# The clean boundary the second round read: this one declines honestly, so if
# it stops the cell has lost its reference point rather than found a defect.
READBACK_CONTROL = "read me my notes"


# ===========================================================================
# Grid M -- entry 8's meta-question
# ===========================================================================
#
# **Novel-only, which is entry 8's own standard.** Questions about *him* -- what
# he can do, how he works, what he is -- none of which the corpus carries and
# none of which names the instance.
META_CARRIERS = (
    "what tools do you know",
    "what can you do",
    "what are you able to do",
    "how do you work",
    "who made you",
    "what are you",
    "what do you know",
    "what have you got",
    "can you list what you can do",
    "what sort of things can you help with",
)

# The three outcomes the entry names, plus a fourth for anything else. Reported
# as a distribution; the gold is the owner's and this file does not pick one.
META_OUTCOMES = ("routed decline", "self-description",
                 "runtime hatch (the model was not consulted)", "frame loss",
                 "something else")

# `fallback_say`'s two own rungs -- the runtime's admission and its
# acknowledgement. Every other rung takes its words out of the observation and
# is stamped `author: "tool"`. Read here so this file, `harness/historygrid.py`
# and `scripts/count_ft_rates.py` cannot disagree about what a lost frame is.
RUNTIME_FLOORS = (NOTHING_SAID, DID_IT)


# ===========================================================================
# Grid A -- entry 5
# ===========================================================================
#
# **Split, because only half is broken.** The explicit relay composes a
# near-verbatim `request` already (second round, `ask the big model to write me
# a haiku about autumn`); the degenerate arguments come from the implicit route,
# where an uncovered-but-plausible request lands on `ask_agent` without the user
# naming it. VISION section 6's rules are the gold: declared relay, verbatim
# request.
ESCALATE_EXPLICIT = (
    ("ask the big model to write me a haiku about autumn",
     "write me a haiku about autumn"),
    ("ask the big model to explain quantum tunnelling",
     "explain quantum tunnelling"),
    ("ask claude to draft a thank you note",
     "draft a thank you note"),
    ("ask the big model how photosynthesis works",
     "how photosynthesis works"),
    ("get the big model to summarise the news",
     "summarise the news"),
    ("ask the big model to come up with a name for a cat",
     "come up with a name for a cat"),
    ("ask the big model to write a limerick about rain",
     "write a limerick about rain"),
    ("ask claude what to cook with what's in the fridge",
     "what to cook with what's in the fridge"),
)
ESCALATE_IMPLICIT = (
    ("tell me a joke", "tell me a joke"),
    ("write me a poem about the sea", "write me a poem about the sea"),
    ("explain how a fridge works", "explain how a fridge works"),
    ("give me an idea for dinner", "give me an idea for dinner"),
    ("help me word an apology", "help me word an apology"),
    ("come up with a name for a boat", "come up with a name for a boat"),
    ("suggest a book for a long flight", "suggest a book for a long flight"),
    ("write a short story about a lighthouse",
     "write a short story about a lighthouse"),
)


# ===========================================================================
# Grid N -- entry 6
# ===========================================================================
#
# Session 14's battery, regenerated from `corn/toolgen.py`'s `NOTE_TEMPLATES`
# for `harness/surfacegrid.py`'s reason (the nine were never committed), with
# the three imperative stems entry 6 names pinned first. The same nine ride
# `surfacegrid`'s surface axis, so the two cells' base columns should agree and
# a disagreement is a finding.
NOTE_PHRASINGS = (
    "note down {t}", "jot down {t}", "write down {t}",
    "make a note {t}", "save a note {t}", "take a note {t}",
    "put in my notes {t}", "note that {t}", "add a note {t}",
)
NOTE_BODY = "buy milk"

# **The reminder-shaped rows, gold open.** Whether a reminder request should
# land on `save_note` or stay declined until a reminder tool exists is the
# owner's decision, so these are carried as a shape and reported descriptively.
#
# **The frames are grid A's own and the fills deliberately are not.** `remind me
# to {v}` and `set a reminder to {v}` are `corn/toolspace.py`'s trained decline
# frames, which is exactly why a reminder request is a hard case -- but grid A
# fills them from `toolgrid.DECLINE_FILLS`, and the first draft of this pool
# used `sign the school form`, which is one of those fills verbatim. A carrier
# shared with another grid makes two instruments one population, and
# `check_routegrid.py` section 1 caught it. Every fill here is written for this
# cell.
REMINDER_CARRIERS = (
    "remind me to take out the trash tomorrow",
    "remind me to call the dentist",
    "don't let me forget to move the car",
    "set a reminder to water the plants on friday",
)

NOTE_HISTORIES = ("empty room", "mid-conversation")


PROVENANCE = {
    "D ability questions": "written for this instrument; five are drive "
                           "carriers kept verbatim",
    "D wrapper axis": "the live stacked carrier taken apart into its three "
                      "wrappers, over four trained lookup subjects",
    "D kinship": "kinship TERMS only -- ground rule 16; the corpus count "
                 "found zero of these in 6.6M turns",
    "T carriers": "written for this instrument, four cells x four",
    "R read-back": "written for this instrument; no name in any of them",
    "M meta": "novel-only, entry 8's own standard",
    "A escalate": "written for this instrument; explicit half from the second "
                  "round's carrier shape",
    "N note battery": "corn.toolgen.NOTE_TEMPLATES, nine pinned here, the same "
                      "nine harness/surfacegrid.py uses",
}


# ===========================================================================
# the cases
# ===========================================================================

@dataclass
class Turn:
    ask: str
    calls: list[dict] = field(default_factory=list)
    obs: list[dict] = field(default_factory=list)
    say: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def hatched(self) -> bool:
        return any(c.get("author") == "runtime" for c in self.calls)

    @property
    def model_calls(self) -> list[dict]:
        return [c for c in self.calls if c.get("author", "model") != "runtime"]

    @property
    def called(self) -> str | None:
        if not self.model_calls:
            return None
        return self.model_calls[0].get("name") or "<malformed>"

    @property
    def args(self) -> dict:
        first = self.model_calls[0].get("arguments") if self.model_calls else None
        return first if isinstance(first, dict) else {}

    @property
    def reply(self) -> str:
        return (self.say.get("text") or "").strip()

    @property
    def runtime_answered(self) -> bool:
        """A hatch or a pool served the words -- the model was not consulted."""
        return self.hatched or self.say.get("author") == "runtime"


@dataclass
class Case:
    grid: str
    cell: str            # the reported row
    ask: str
    gold: str            # "" means the gold is an open owner decision
    opener: str | None = None
    want: str = ""       # the span an argument row must carry
    turns: list[Turn] = field(default_factory=list)

    @property
    def probed(self) -> Turn | None:
        i = 1 if self.opener is not None else 0
        return self.turns[i] if len(self.turns) > i else None

    @property
    def called(self) -> str | None:
        return self.probed.called if self.probed else None

    @property
    def routed(self) -> bool | None:
        """`None` where the gold is an owner decision -- not False."""
        if not self.gold or self.probed is None:
            return None
        return self.called == self.gold

    @property
    def sunk_to_web(self) -> bool | None:
        """Reached `web_search` where it should not have. 8b's second score."""
        if self.probed is None or self.gold == "web_search":
            return None
        return self.called == "web_search"

    @property
    def left_machine(self) -> bool | None:
        """`sunk_to_web`, and the runtime let the query go to a provider.

        **A new column, not a redefinition** (PLAN-FINETUNE-V4 ground rule
        2): `sunk_to_web` is the *model's* routing and stays what every card
        on disk read. This is the half that is the runtime's -- since
        2026-09-07 `harness/backends/search.py`'s gate reads the person's own
        line as well as the query, so a private question routed to
        `web_search` is refused before any provider is built, and the
        observation says `self_referential`. `None` where nothing routed to
        the web; `False` where it did and was refused; `True` is the leak.
        """
        if not self.sunk_to_web:
            return None
        return not any(o.get("reason") == "self_referential"
                       for o in self.probed.obs)

    @property
    def answered_without_checking(self) -> bool | None:
        """No call at all, and he said something anyway -- and it was his."""
        p = self.probed
        if p is None:
            return None
        return not p.model_calls and bool(p.reply) and not p.runtime_answered

    @property
    def kept_request(self) -> bool | None:
        """Entry 5: `request` carries the user's ask, near-verbatim."""
        p = self.probed
        if not self.want or p is None or p.called != "ask_agent":
            return None
        return _carries(p.args.get("request"), self.want)

    @property
    def degenerate_context(self) -> bool | None:
        """...and `context` is not the request read back with junk on it.

        The live instance: `{"request": "jokes", "context": "jokes, tell me a
        joke"}` -- a context that is the request repeated plus the utterance.
        Degenerate here means it carries a comma-joined echo of the request
        rather than anything the request does not already say.
        """
        p = self.probed
        if not self.want or p is None or p.called != "ask_agent":
            return None
        ctx = p.args.get("context")
        if not isinstance(ctx, str) or not ctx.strip():
            return False
        req = p.args.get("request")
        if not isinstance(req, str) or not req.strip():
            return True
        return req.strip().lower() in ctx.strip().lower()

    @property
    def degenerate_date(self) -> bool | None:
        """Grid T: `resolve_date` fired with an expression carrying no date."""
        p = self.probed
        if p is None or p.called != "resolve_date":
            return None
        return degenerate_expression(p.args.get("expression"))

    @property
    def unrecognised_date(self) -> bool | None:
        """...or with one the date backend could not resolve at all.

        **A second column, because the two live carriers fail differently and
        only one of them is a word-list matter.** `{"expression": "fun"}` is
        degenerate by any reading and the token test names it. `{"expression":
        "the next winter olympics"}` carries a temporal word and is not
        degenerate -- it is *unresolvable*, and the runtime says so itself with
        `reason: unrecognised`. Reading the observation is better than widening
        a word list until it happens to catch the second one, because the
        runtime's verdict is a fact and the word list is a judgment.
        """
        p = self.probed
        if p is None or p.called != "resolve_date":
            return None
        return any(o.get("reason") == "unrecognised" for o in p.obs)

    @property
    def meta_outcome(self) -> str | None:
        """Grid M's descriptive column. The gold is the owner's; this is not it.

        **Four outcomes, and the fourth was a scoring bug on the first read.**
        `identity_reply` is a runtime *hatch*: it answers the meta-question with
        an accurate tool list at 0 ms, with no call and a runtime-authored say.
        A classifier that read "runtime authored the words" as frame loss filed
        six of those as the model losing the frame, when the model was never
        consulted -- which is entry 8's own distinction (the hatch is a runtime
        strength; the *weights* are what fall out of the vocabulary) inverted.

        So a frame loss is the runtime *floor* specifically -- `fallback_say`'s
        two own rungs, the same two `harness/historygrid.py` and
        `scripts/count_ft_rates.py` read -- and a hatch is its own row.
        """
        p = self.probed
        if self.grid != "M" or p is None:
            return None
        if p.called == "decline":
            return "routed decline"
        if not p.model_calls:
            if p.say.get("author") == "runtime":
                return ("frame loss" if p.reply in RUNTIME_FLOORS
                        else "runtime hatch (the model was not consulted)")
            return "self-description"
        return "something else"


def _words(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()


def _carries(got: object, want: str) -> bool:
    """The slot carries what was asked, on content words.

    `toolgrid._carries`' rule: he reshapes a span routinely and a reshaping
    that kept every content word has kept the thing. Every word is required
    rather than a threshold, because a relayed request that dropped half its
    words is a request nobody made -- which is exactly entry 5's defect.
    """
    if not isinstance(got, str) or not got.strip():
        return False
    want_w = _words(want)
    got_w = set(_words(got))
    return bool(want_w) and all(w in got_w for w in want_w)


def build(seed: int = 0) -> list[Case]:
    """Every case before any of them runs. Pure and seeded."""
    rng = random.Random(seed)
    invented = [q for q, _a, _s in FACTS if q.startswith("the capital of ")]
    opener = rng.choice(invented) if invented else "the capital of Laos"
    cases: list[Case] = []

    # -- Grid D ------------------------------------------------------------
    for ask in ABILITY_CHAT:
        cases.append(Case("D", "decline gold / chat-plausible", ask, "decline"))
    for ask in ABILITY_TASKAPP:
        cases.append(Case("D", "decline gold / task-app", ask, "decline"))
    for label, frame in WRAPPERS.items():
        for subject in WRAPPED_CARRIERS:
            cases.append(Case("D", f"serve gold / wrapper: {label}",
                              frame.format(q=subject), "web_search"))
    for ask, gold in KINSHIP_CARRIERS:
        cases.append(Case("D", "serve gold / kinship contact", ask, gold))
    for ask, gold in DESCRIPTIVE_CARRIERS:
        cases.append(Case("D", "serve gold / descriptive contact", ask, gold))

    # -- Grid T ------------------------------------------------------------
    for cell, (gold, carriers) in TEMPORAL_CELLS.items():
        for ask in carriers:
            for punctuated in (False, True):
                cases.append(Case("T", f"{cell}{'?' if punctuated else ''}",
                                  ask + ("?" if punctuated else ""), gold))

    # -- Grid R ------------------------------------------------------------
    for ask, keyed in READBACK_CARRIERS:
        cases.append(Case("R", "with a temporal key" if keyed
                          else "no temporal key", ask, READBACK_GOLD))
    cases.append(Case("R", "the clean boundary", READBACK_CONTROL,
                      READBACK_GOLD))

    # -- Grid M ------------------------------------------------------------
    for ask in META_CARRIERS:
        cases.append(Case("M", "meta-question (gold undecided)", ask, ""))

    # -- Grid A ------------------------------------------------------------
    for ask, want in ESCALATE_EXPLICIT:
        cases.append(Case("A", "explicit relay", ask, "ask_agent", want=want))
    for ask, want in ESCALATE_IMPLICIT:
        cases.append(Case("A", "implicit route", ask, "ask_agent", want=want))

    # -- Grid N ------------------------------------------------------------
    for history in NOTE_HISTORIES:
        head = None if history == "empty room" else opener
        for phrasing in NOTE_PHRASINGS:
            cases.append(Case("N", f"note carrier / {history}",
                              phrasing.format(t=NOTE_BODY), "save_note",
                              opener=head))
        for ask in REMINDER_CARRIERS:
            cases.append(Case("N", f"reminder shape / {history} (gold open)",
                              ask, "", opener=head))
    return cases


def run_case(client: Client, case: Case) -> Case:
    """One conversation from a cleared history."""
    for _ in client.request(op="reset"):
        pass
    asks = ([case.opener] if case.opener is not None else []) + [case.ask]
    for ask in asks:
        turn = Turn(ask)
        for ev in client.request(op="turn", user=ask):
            kind = ev.get("t")
            if kind == "call":
                turn.calls.append(ev)
            elif kind == "obs":
                turn.obs.append(ev.get("payload") or {})
            elif kind == "say":
                turn.say = {k: v for k, v in ev.items() if k not in ("t", "id")}
            elif kind == "error":
                turn.error = ev.get("why", "?")
        case.turns.append(turn)
        if turn.error:
            break
    return case


# ===========================================================================
# the report
# ===========================================================================

def _score(cases: list[Case], row: str) -> tuple[int, int]:
    hit = n = 0
    for c in cases:
        v = getattr(c, row)
        if v is None:
            continue
        n += 1
        hit += bool(v)
    return hit, n


def _cell(hit: int, n: int) -> str:
    return f"{hit:>3}/{n:<3}" if n else "  -- "


def _spread(cases: list[Case]) -> str:
    out: dict[str, int] = {}
    for c in cases:
        k = c.called or "(no call)"
        out[k] = out.get(k, 0) + 1
    return ", ".join(f"{k} {v}" for k, v in
                     sorted(out.items(), key=lambda kv: -kv[1])) or "(none)"


def _by_cell(cases: list[Case], title: str, rows=("routed",)) -> dict:
    print()
    print(f"  {title}")
    width = max((len(c.cell) for c in cases), default=10)
    out: dict[str, dict] = {}
    cells: list[str] = []
    for c in cases:
        if c.cell not in cells:
            cells.append(c.cell)
    print(f"    {'':<{width}} " + " ".join(f"{r[:13]:>14}" for r in rows)
          + "   what he reached for")
    for label in cells:
        rows_here = [c for c in cases if c.cell == label]
        scored = {r: _score(rows_here, r) for r in rows}
        print(f"    {label:<{width}} "
              + " ".join(f"{_cell(*scored[r]):>14}" for r in rows)
              + f"   {_spread(rows_here)[:52]}")
        out[label] = {k: list(v) for k, v in scored.items()}
        out[label]["reached"] = {}
        for c in rows_here:
            k = c.called or "(no call)"
            out[label]["reached"][k] = out[label]["reached"].get(k, 0) + 1
    return out


def report(cases: list[Case], info: dict, seed: int) -> dict:
    grids: dict[str, dict] = {}

    d = [c for c in cases if c.grid == "D"]
    if d:
        print()
        print("=" * 78)
        print("Grid D -- entries 2, 2b and 6c.  one cell, because they cancel")
        grids["D"] = _by_cell(d, "routed to the row's own gold")
        dec = [c for c in d if c.gold == "decline"]
        srv = [c for c in d if c.gold != "decline"]
        print()
        print(f"  decline-gold rows {_cell(*_score(dec, 'routed'))}"
              f"    serve-gold rows {_cell(*_score(srv, 'routed'))}")
        print("  a payload that moves one of those without the other is the "
              "interference note happening")
        grids["D"]["pooled"] = {"decline_gold": list(_score(dec, "routed")),
                                "serve_gold": list(_score(srv, "routed"))}

    t = [c for c in cases if c.grid == "T"]
    if t:
        print()
        print("=" * 78)
        print("Grid T -- entry 1c.  temporal flavour against the date tool")
        grids["T"] = _by_cell(t, "routed to gold; soft_recall has none")
        dg = _score(t, "degenerate_date")
        un = _score(t, "unrecognised_date")
        print()
        print(f"  of the turns that called resolve_date, {_cell(*dg)} carried "
              f"an expression with no date in it, and {_cell(*un)} carried one "
              f"the date backend could not resolve")
        for c in t:
            if c.degenerate_date or c.unrecognised_date:
                print(f"      {c.ask[:40]!r} -> "
                      f"{c.probed.args.get('expression')!r}"
                      + ("  [degenerate]" if c.degenerate_date else "")
                      + ("  [unrecognised]" if c.unrecognised_date else ""))
        soft = [c for c in t if c.cell.startswith("soft_recall")]
        print(f"  soft recall, gold UNDECIDED -- what fired: {_spread(soft)}")
        grids["T"]["degenerate_date"] = list(dg)
        grids["T"]["unrecognised_date"] = list(un)

    r = [c for c in cases if c.grid == "R"]
    if r:
        print()
        print("=" * 78)
        print("Grid R -- entry 8b.  read-back, and never the web")
        grids["R"] = _by_cell(r, "routed to decline",
                              ("routed", "sunk_to_web",
                               "answered_without_checking", "left_machine"))
        print()
        print(f"  routed to the web on {_cell(*_score(r, 'sunk_to_web'))} -- "
              f"the model's choice, and every card on disk reads this column")
        print(f"  left the machine on  {_cell(*_score(r, 'left_machine'))} -- "
              f"of those, the ones the runtime's gate did not refuse")
        for c in r:
            if c.sunk_to_web:
                gate = "" if c.left_machine else "   (refused at the gate)"
                print(f"      {c.ask[:40]!r} -> {c.probed.args.get('query')!r}"
                      f"{gate}")

    m = [c for c in cases if c.grid == "M"]
    if m:
        print()
        print("=" * 78)
        print("Grid M -- entry 8's meta-question.  the gold is the owner's")
        counts = {o: sum(1 for c in m if c.meta_outcome == o)
                  for o in META_OUTCOMES}
        print()
        for outcome, n in counts.items():
            print(f"    {outcome:<24} {n:>3}/{len(m)}")
        print()
        for c in m:
            print(f"    {c.ask:<40} {str(c.called or '(no call)'):<12} "
                  f"{c.probed.reply[:34]!r}")
        grids["M"] = {"outcomes": counts, "n": len(m)}

    a = [c for c in cases if c.grid == "A"]
    if a:
        print()
        print("=" * 78)
        print("Grid A -- entry 5.  the relay's arguments, split by route")
        grids["A"] = _by_cell(a, "routed to ask_agent",
                              ("routed", "kept_request", "degenerate_context"))
        bad = [c for c in a if c.kept_request is False]
        if bad:
            print()
            print("  every request that did not survive:")
            for c in bad[:10]:
                print(f"      {c.ask[:36]!r} -> "
                      f"{c.probed.args.get('request')!r}")

    n = [c for c in cases if c.grid == "N"]
    if n:
        print()
        print("=" * 78)
        print("Grid N -- entry 6.  the note battery on its history axis")
        grids["N"] = _by_cell(n, "routed to save_note; reminders have no gold")
        for history in NOTE_HISTORIES:
            rows = [c for c in n if history in c.cell and c.gold]
            print(f"  note carriers, {history:<18} {_cell(*_score(rows, 'routed'))}")
        rem = [c for c in n if not c.gold]
        print(f"  reminder shapes, gold UNDECIDED -- what fired: {_spread(rem)}")

    hatched = [c for c in cases if c.probed and c.probed.hatched]
    print()
    print("=" * 78)
    if hatched:
        print(f"!! {len(hatched)} turn(s) were answered by a runtime hatch:")
        for c in hatched[:8]:
            print(f"     [{c.grid}] {c.ask[:60]}")
        print("   Grid M expects some of these -- `identity_reply` claims the "
              "meta-question and that is a runtime strength, not a model one. "
              "Anywhere else, run `python scripts/check_routegrid.py`.")
    else:
        print("no turn was answered by a runtime hatch")

    return {
        "harness": "routegrid/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": revision(),
        "seed": seed,
        "decode": {
            "temperature": info.get("temperature"),
            "speech_temperature": info.get("speech_temperature"),
            "multi": info.get("multi"),
            "dtype": info.get("dtype"),
            "search": info.get("search"),
            "extract": info.get("extract"),
            "packs": info.get("packs"),
            "doc": info.get("doc"),
            "reach": info.get("reach"),
            "decline": info.get("decline"),
            "notes": info.get("notes"),
            # The fold -- owner decision 1b/0, and the setting that re-dated
            # every card on this instance the day it landed. `corn.agent.
            # fold_turn` rewrites the tokens the model is handed, so a row read
            # with it on cannot be compared with one read without it. Absent on
            # a card written before the fold existed, which is exactly what
            # "this read predates it" should look like.
            "fold": info.get("fold"),
        },
        "instance": info,
        "provenance": PROVENANCE,
        "open_golds": {
            "T soft_recall": "PLAN-FINETUNE-V4 owner decision 1c",
            "M meta-question": "owner decision 8 -- BLOCKS A PAYLOAD",
            "N reminder shape": "owner decision 6",
        },
        "grids": grids,
        "hatched": len(hatched),
        "cases": [
            {"grid": c.grid, "cell": c.cell, "ask": c.ask, "gold": c.gold or None,
             "opener": c.opener, "called": c.called,
             "arguments": (c.probed.args or None) if c.probed else None,
             "reply": c.probed.reply[:200] if c.probed else "",
             "hatched": bool(c.probed and c.probed.hatched),
             "scores": {"routed": c.routed, "sunk_to_web": c.sunk_to_web,
                        "left_machine": c.left_machine,
                        "answered_without_checking": c.answered_without_checking,
                        "kept_request": c.kept_request,
                        "degenerate_context": c.degenerate_context,
                        "degenerate_date": c.degenerate_date,
                        "unrecognised_date": c.unrecognised_date,
                        "meta_outcome": c.meta_outcome}}
            for c in cases
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="entries 1c, 2, 2b, 5, 6, 6c, 8, 8b")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--seed", type=int, default=0,
                    help="which FACTS subject the mid-conversation arm opens on")
    ap.add_argument("--grid", choices=("D", "T", "R", "M", "A", "N"),
                    action="append", help="run one grid only; all six by default")
    ap.add_argument("--json", help="write the scorecard here")
    args = ap.parse_args()

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- start it with "
              f"`python -m harness.server --multi`", file=sys.stderr)
        return 2

    info = {}
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            info = {k: v for k, v in ev.items() if k not in ("t", "id")}

    print(f"routegrid against {info.get('ckpt')}")
    print(f"  temperature {info.get('temperature')}   speech "
          f"{info.get('speech_temperature')}   multi {info.get('multi')}   "
          f"search {info.get('search')}   packs {bool(info.get('packs'))}")
    print(f"  notes -> {info.get('notes')}   reach {info.get('reach')}")

    if "decline" not in (info.get("tools") or []):
        print("\nthis instance was started with --no-decline, so Grids D and R "
              "are measuring a tool he was not offered.", file=sys.stderr)
        client.close()
        return 2

    planned = [c for c in build(args.seed)
               if not args.grid or c.grid in args.grid]
    if not info.get("multi") and any(c.opener for c in planned):
        print("\nthis instance is not --multi, so Grid N's mid-conversation arm "
              "opens on an empty history and is a second empty room. Restart "
              "with --multi.", file=sys.stderr)
        client.close()
        return 2

    turns = sum(1 + (c.opener is not None) for c in planned)
    notes = sum(1 for c in planned if c.gold == "save_note" or c.grid == "N")
    print(f"  {len(planned)} cases, {turns} turns planned   "
          f"!! save_note may write up to {notes} notes to the path above")

    started = time.perf_counter()
    done: list[Case] = []
    for i, case in enumerate(planned, 1):
        run_case(client, case)
        bad = next((t for t in case.turns if t.error), None)
        if bad:
            print(f"turn raised: {bad.ask!r} -- {bad.error}", file=sys.stderr)
            return 2
        done.append(case)
        if i % 40 == 0:
            print(f"    {i}/{len(planned)} ...")

    card = report(done, info, args.seed)
    card["seconds"] = round(time.perf_counter() - started, 1)
    print(f"\n  {len(done)} cases in {card['seconds']}s")
    client.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
