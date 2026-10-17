"""Three entries, one skeleton: a turn that sets history, then a probe scored on its own routing.

**Entries 1, 4 and 6b of `docs/PLAN-FINETUNE-V4.md` are one build.** Entry 4 is
a fresh question captured by the turn before it; entry 6b is a question written
down instead of answered, after the turn before it; entry 1 is a class of
question that never reaches the router at all. The first two need the same
instrument -- a known history, then a probe -- and the third needs an axis that
would otherwise be built twice, so they share a file and a report keeps them
apart.

---

## The arms -- five histories, and the first one is the control

    control              nothing before the probe. **Not optional.** Every
                         claim these entries make is "the empty-room control
                         routes the same question cleanly", and without that
                         column a miss reads as "the probe is hard" rather
                         than as history capturing it
    lookup_ok            a search that answered, drawn from `corn/tools.py`'s
                         FACTS so the table backend really returns something
    lookup_fail          a search that came back `no_results` -- the trigger
                         session 12 measured
    chat_nocall          a turn that made no call at all. The third trigger
                         species: the late drive found a query that was the
                         previous turn's **user utterance** after a no-call
                         chat answer, so the copy source is wider than "a
                         prior query" and an instrument without this arm
                         reads it too narrowly
    declined_imperative  entry 6b's arm: a reminder-shaped request that
                         declines, then an ordinary question
    social_nocall        PLAN-CONVERSATION 5c (2026-09-05): a social move
                         answered by a `<|say|>` and no call -- the hatch's
                         own history, which is the one the 2026-09-04 session
                         ran under when "what's the capital of france" re-ran
                         the previous recipe query

**Whether an arm actually set the history it names is reported, not assumed.**
`chat_nocall` in particular asks the model to do something it may not do, so
every arm prints how many of its turn 1s landed as intended; an arm that did
not is measuring a different history from the one on its label.

## The probe's columns -- a miss is not one thing

Gold is a fresh call of the probe's own, and the ways of failing it are
different facts about the weights, so they are separate columns rather than one
`routed` bit:

    routed_fresh          `web_search`, and the query carries the probe's own
                          subject. The hit
    reissued_query        the query is the previous turn's query, byte for
                          byte after normalisation
    reissued_utterance    the query is the previous turn's **user text** --
                          the species that needs `chat_nocall` to be visible
    spliced               the previous query's opening stem carrying this
                          turn's noun, with what this turn asked for missing
    wrote_when_not_asked  a `save_note` on a turn that asked a question. Entry
                          6b's score, and the inverse of `notefid`, which
                          reads note fidelity when a note *was* asked for

## The social probe family, and `copied_from` -- PLAN-CONVERSATION 5c, 6d

A third probe family, `social`: a second social move after the history, scored
on its own column rather than on the routing ones --

    social_answered       no call, and the reply reads as an answer to the
                          move's family under `corn.socialfam.reply_families`

-- because a goodbye is not a `web_search` and `routed_fresh` would score every
one a miss. The routing columns read `None` on it.

And one more column on every Grid H probe:

    copied_from           `bound` when the probe's query is the turn before
                          it (its query or its user text), `distractor` when it
                          is an earlier turn's, `none` otherwise

which at depth 1 can only say `bound` or `none`, and that is the point:
`--depth N` puts N-1 unrelated finished exchanges *in front of* the arm's turn
1, so "the turn before this one" and "turn 1" stop being the same string and
the column can name which of them he copied. PLAN-CONVERSATION 6d reads it on
the shipped checkpoints before arm 8 trains; `--depth 1` is every card that
exists.

## The third turn, and it is entry 6b's second finding

6b measured that the turn *after* the destabilised one also suffered -- `how
many feet are in a mile?` went bare `<|end|>` where its empty-room control
routes. So every non-control arm runs a third turn, a fixed question, scored
only on whether the frame survived. That makes "the destabilised history costs
adjacent turns too" a column instead of an anecdote, and it costs one turn per
case.

## Grid E -- entry 1, and the cross it insists on

Entry 1's live rescue is confounded and its own text says which way: "look up
who won the 2026 super bowl" drops the question mark **as well as** adding the
imperative, and entry 0's count makes only one of those a shape the routing
slices have never carried. So the imperative and the punctuation are crossed
**independently** -- bare +/- "?", "look up ..." +/- "?" -- or the payload gets
aimed at the wrong half of the rescue.

    routed to web_search   the gold
    chose resolve_date     a **distinct** failure column, not a miss. The
                           "when is [event]" species lands on the date tool and
                           a routed-at-all score would not see it

Grid E is an empty-room grid; it is here because it shares this file's report
and because building entry 0's axis twice is how two cells come to disagree.

---

**No `--search` anywhere.** Routing and argument extraction both happen before
any tool runs, so the whole file measures with `web_search` answering out of
`FACTS`. The `lookup_ok` arm needs the table to *answer*, which is why its
subject is drawn from `FACTS` rather than written here.

**`--multi` is required.** Every arm but `control` is a two- or three-turn
conversation and the history between the turns is the measurement.

**Ground rule 16.** Every carrier is written for this instrument or drawn from
`FACTS`; no contact, no name and no instance fact appears in any of them.

**A rate, not a gate.**

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_v4/ckpt.pt \
        --notes /tmp/historygrid.jsonl --no-log --multi
    python -m harness.historygrid \
        --json harness/results/corn_jr_260m_v4__historygrid.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from corn.agent import DID_IT, NOTHING_SAID, social_family
from corn.socialfam import reply_families
from corn.tools import FACTS

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision

# ===========================================================================
# Grid E -- entry 1's carriers and its two axes
# ===========================================================================
#
# **Event-result questions about things that have not happened or that the
# weights cannot hold.** The shapes are the entry's three -- "who won X", "what
# was the score of X", "when did X happen" -- and the subjects are recent or
# future, so a correct answer is only reachable through the tool. Five of the
# eight are carriers the drives actually failed on, kept verbatim, because
# rewriting a pre-registered item after seeing the data is editing a hypothesis.
EVENT_CARRIERS = (
    "who won the 2026 super bowl",
    "who won the 2026 world cup",
    "who won the world series in 2025",
    "what was the score of the last lakers game",
    "when is the next winter olympics",
    "who won the nobel prize in physics in 2025",
    "who won the tour de france in 2025",
    "what was the score of the england game",
)

# The imperative half of the confounded rescue. One carrier, not a pool: the
# axis is imperative-or-not, and a second phrasing axis would put variance
# where this grid cannot report it. "look up {q}" is the exact form the second
# round found rescuing.
IMPERATIVE = "look up {q}"

# The distinct failure column entry 1 asks for by name.
EVENT_GOLD = "web_search"
EVENT_MISROUTE = "resolve_date"


def event_forms() -> tuple[tuple[str, bool, bool], ...]:
    """(label, imperative, punctuated) -- the independent 2x2."""
    return tuple((f"{'imperative' if imp else 'bare'}{'?' if q else ''}", imp, q)
                 for imp in (False, True) for q in (False, True))


def render_event(carrier: str, imperative: bool, punctuated: bool) -> str:
    text = IMPERATIVE.format(q=carrier) if imperative else carrier
    return text + ("?" if punctuated else "")


# ===========================================================================
# Grid H -- the histories and the probes
# ===========================================================================

# **The probes are attribute lookups, which is the point.** Every one of them
# routes cleanly first-turn -- that is the late drive's own "what read clean"
# list and the grids' 200/200 -- so a miss on the probe is attributable to the
# history rather than to the question. A probe that was hard on its own would
# make every arm unreadable at once.
PROBES = (
    "how tall is mount everest",
    "who wrote pride and prejudice",
    "the population of japan",
    "the currency of brazil",
    "what is the boiling point of water",
    "the official language of egypt",
    "who painted the mona lisa",
    "how deep is the mariana trench",
)

# **Entry 6b's own probe family, and the first read is why it exists.** The
# attribute probes above are entry 4's -- they are what a re-issue can be
# measured against -- and on them `wrote_when_not_asked` read 0 of 32, which is
# a null about a carrier the entry never used. 6b's live sighting was `what is
# 12 times 8?` becoming `save_note{"text": "12 times 8"}`: an *arithmetic*
# question, which is question-shaped, has no entity to look up, and whose
# empty-room control the entry says routes to `web_search`. A cell that read
# only attribute lookups was asking 6b about a shape it had never failed on.
#
# The first is the entry's own, verbatim.
ARITHMETIC_PROBES = (
    "what is 12 times 8",
    "what is 7 times 9",
    "what is 100 divided by 4",
    "what is 15 percent of 60",
)

# **The social probes, PLAN-CONVERSATION 5c.** One move per family the hatch
# knows, each a whole-utterance pool member so the hatch takes it and the
# say is model-written under `rephrase`; scored on `social_answered` alone.
# Deliberately not the arm's own opener, so a case's turn 2 is never its turn
# 1 repeated.
SOCIAL_PROBES = (
    "good night", "thanks a lot", "sounds good", "rough day", "how are you",
    "hello there",
)

FAMILIES = {"attribute": PROBES, "arithmetic": ARITHMETIC_PROBES,
            "social": SOCIAL_PROBES}

# The fixed third turn. Deliberately *not* one of the probes, so a case's turn 3
# is never a repeat of its own turn 2, and deliberately 6b's own carrier -- the
# adjacent turn it measured falling out of the vocabulary.
THIRD_TURN = "how many feet are in a mile"

# `lookup_fail`'s subject: real, so the corpus's invented `FACTS` table has no
# entry and the observation comes back `no_results`. `lookup_ok`'s is drawn
# from `FACTS` at run time -- see `history_openers`.
FAIL_SUBJECT = "the capital of iceland"

# **`chat_nocall`'s carrier, and finding one was harder than expected.** The
# arm needs a turn that makes no call and answers in chat register -- the
# history the late drive's third copy species was found under. The obvious
# candidate was the drive's own (`who won the world series in 2025`, which
# answered "I don't know, I didn't see it." live) and on this checkpoint it
# routes to `web_search` instead, so the first build of this arm landed 0 of 8
# and measured a lookup history wearing a chat label.
#
# **Ten candidates were probed and exactly one made no call**: ordinary chat
# register -- "do you think it will rain", "that was a strange film", "what do
# you reckon", "tell me something interesting" -- all route to `web_search`,
# and "i had a long day" declines. That is a fact about the checkpoint worth
# recording next to the arm it constrains: a no-call turn is a *rare state* on
# this base, which is also why entry 4's third species is the rarest of its
# three.
#
# The one that lands is an entry 8 carrier, and the coupling is named rather
# than hidden: if entry 8's payload ever teaches this shape to route, this arm
# stops setting the history its label claims and the `arm_landed` row is what
# will say so.
CHAT_CARRIER = "have you got my name"

# 6b's own turn 1, verbatim from the entry.
DECLINE_CARRIER = "remind me to take out the trash tomorrow"

# **The social arm's turn 1, PLAN-CONVERSATION 5c.** A thanks, because it is
# the family the hatch answers most reliably and a no-call history is what
# the arm's name claims; `arm_landed` reports whether it did. Not a probe and
# not `CHAT_CARRIER`, on the same rule as every other opener -- and one that
# shares no content word with any probe, including the social ones.
SOCIAL_OPENER = "much appreciated"

# **The pack arm, and it is here because entry 4 was measured under two
# histories.** The pack drive's ~1-in-3 was taken with six packs mounted and
# the late drive's 2-of-3 without any, so a cell that only ever read a
# table-backed lookup would be answering one of those two questions and
# claiming both. A pack-shaped observation is a different payload with a
# different shape in the transcript, and whether the copy defect cares is a
# question only this arm asks.
#
# The arm needs a turn 1 the *pack* answers, so its subject is invented for
# this instrument and is deliberately absent from `FACTS`: without a pack
# mounted it falls through to the table, comes back empty, and `arm_landed`
# reports 0 -- which is the arm saying "I was not run under the history my name
# claims" rather than quietly measuring `lookup_fail` twice.
PACK_OPENER = "what type is Grimbol"

ARMS = ("control", "lookup_ok", "lookup_fail", "lookup_pack", "chat_nocall",
        "declined_imperative", "social_nocall")

# What each arm's turn 1 is *supposed* to do, so the grid can report whether it
# did rather than assume it.
ARM_INTENT = {
    "lookup_ok": "a web_search that answered",
    "lookup_fail": "a web_search that came back empty",
    "lookup_pack": "a web_search the PACK answered (needs --packs)",
    "chat_nocall": "no call at all",
    "declined_imperative": "a decline",
    "social_nocall": "a social move answered without a call (the hatch)",
}

# **The fixture pack, written out by the instrument rather than assumed on
# disk.** Ground rule 16 forbids an instance fact in a fixture, and this
# machine's own `packs/` folder is the owner's data by definition -- so the
# pack arm brings its own table of invented creatures, in the shape
# `harness/backends/packs.py` reads (a CSV whose first column is the row key
# and whose headers are the columns). `--write-pack DIR` emits it, so the read
# is reproducible on a clone that has never seen this machine.
FIXTURE_PACK = {
    "grimoire.csv":
        "Name,Type,Height (m),Habitat,Diet\n"
        "Grimbol,Stone,2.4,upland scree,lichen\n"
        "Thessil,Water,1.1,tidal pools,shellfish\n"
        "Varnek,Ember,3.0,lava fields,ash moss\n"
        "Ondrisk,Wind,0.8,cliff ledges,insects\n",
}


def write_fixture_pack(where: Path) -> Path:
    """Write the pack this grid's `lookup_pack` arm needs, and say where."""
    where.mkdir(parents=True, exist_ok=True)
    for name, body in FIXTURE_PACK.items():
        (where / name).write_text(body, encoding="utf-8")
    return where


PROVENANCE = {
    "pack fixture": "invented creatures written for this instrument -- no "
                    "instance data, ground rule 16",
    "event_carriers": "written for this instrument; five are drive carriers "
                      "kept verbatim",
    "probes": "written for this instrument; attribute lookups of the shape the "
              "drives read clean first-turn",
    "lookup_ok subject": "drawn from corn.tools.FACTS at run time, seeded",
    "decline carrier": "PLAN-FINETUNE-V4 entry 6b's own, verbatim",
}


def history_openers(rng: random.Random) -> dict[str, str]:
    """Turn 1 per arm. The successful lookup's subject is drawn, not written.

    `searchgrid.invented_subjects`' argument: a subject written into this file
    that later left `FACTS` would stop answering, and the `lookup_ok` arm would
    quietly become a second `lookup_fail` with nothing in the report to say so.
    """
    invented = [q for q, _a, _s in FACTS if q.startswith("the capital of ")]
    subject = rng.choice(invented) if invented else FAIL_SUBJECT
    return {
        "lookup_ok": subject,
        "lookup_fail": FAIL_SUBJECT,
        "lookup_pack": PACK_OPENER,
        "chat_nocall": CHAT_CARRIER,
        "declined_imperative": DECLINE_CARRIER,
        "social_nocall": SOCIAL_OPENER,
    }


def distractors_for(rng: random.Random, n: int, avoid: str) -> list[str]:
    """`n` unrelated finished exchanges to put in front of turn 1 (`--depth`).

    Drawn from `FACTS`' invented capitals so the table answers them and none
    is an instance fact (ground rule 16); never the `lookup_ok` subject, so
    the bound turn and a distractor are never the same string.
    """
    invented = [q for q, _a, _s in FACTS
                if q.startswith("the capital of ") and q != avoid]
    return rng.sample(invented, min(n, len(invented)))


# ===========================================================================
# the turns
# ===========================================================================

@dataclass
class Turn:
    ask: str
    calls: list[dict] = field(default_factory=list)
    obs: list[dict] = field(default_factory=list)
    say: dict = field(default_factory=dict)
    error: str | None = None

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
    def query(self) -> str | None:
        q = self.args.get("query")
        return q if isinstance(q, str) else None

    @property
    def answered(self) -> bool:
        return any(o.get("answer") for o in self.obs)

    @property
    def empty(self) -> bool:
        return any(o.get("reason") == "no_results" for o in self.obs)

    @property
    def frame_kept(self) -> bool:
        """The turn produced *something* -- a call, or words that were his.

        The frame is lost when the model composed neither a call nor a sayable
        emission and the runtime supplied one of `fallback_say`'s two own
        rungs. That is entry 11's silent species, read the way
        `scripts/count_ft_rates.py` reads it off the log, so the two
        instruments agree about what the loss is.
        """
        if self.model_calls:
            return True
        text = (self.say.get("text") or "").strip()
        return not (self.say.get("author") == "runtime"
                    and text in (NOTHING_SAID, DID_IT))


@dataclass
class Case:
    grid: str            # "E" | "H"
    arm: str
    probe: str
    form: str            # Grid E's axis label, or "" for Grid H
    family: str = ""     # Grid H's probe family: attribute | arithmetic
    imperative: bool = False
    punctuated: bool = False
    opener: str | None = None
    turns: list[Turn] = field(default_factory=list)
    # Unrelated finished exchanges sent *before* the opener (`--depth`); empty
    # on every card that exists. The opener stays the bound turn.
    distractors: list[str] = field(default_factory=list)

    # -- which turn is which -----------------------------------------------

    @property
    def _base(self) -> int:
        return len(self.distractors) if self.opener is not None else 0

    @property
    def prior(self) -> list[Turn]:
        """Every turn before the probe: the distractors, then the opener."""
        if self.opener is None:
            return []
        return self.turns[:self._base + 1]

    @property
    def history(self) -> Turn | None:
        i = self._base
        return self.turns[i] if self.opener is not None and len(self.turns) > i else None

    @property
    def probed(self) -> Turn | None:
        i = self._base + 1 if self.opener is not None else 0
        return self.turns[i] if len(self.turns) > i else None

    @property
    def adjacent(self) -> Turn | None:
        i = self._base + 2 if self.opener is not None else 1
        return self.turns[i] if len(self.turns) > i else None

    @property
    def arm_landed(self) -> bool | None:
        """Turn 1 set the history the arm's name claims."""
        h = self.history
        if h is None:
            return None
        if self.arm in ("lookup_ok", "lookup_pack"):
            return h.called == "web_search" and h.answered
        if self.arm == "lookup_fail":
            return h.called == "web_search" and h.empty
        if self.arm == "chat_nocall":
            return h.called is None
        if self.arm == "declined_imperative":
            return h.called == "decline"
        if self.arm == "social_nocall":
            return h.called is None and bool((h.say.get("text") or "").strip())
        return None

    # -- Grid E ------------------------------------------------------------

    @property
    def event_routed(self) -> bool | None:
        if self.grid != "E" or self.probed is None:
            return None
        return self.probed.called == EVENT_GOLD

    @property
    def chose_date(self) -> bool | None:
        """The distinct failure column entry 1 names. Not folded into a miss."""
        if self.grid != "E" or self.probed is None:
            return None
        return self.probed.called == EVENT_MISROUTE

    # -- Grid H ------------------------------------------------------------

    @property
    def routed_fresh(self) -> bool | None:
        """A `web_search` of this turn's own, and not one of the copy species.

        **Two corrections the first read forced, and both were the scorer being
        stricter than the defect.**

        The subject test is `searchgrid.Turn.kept_subject`'s -- the *head* of
        the probe rather than every content word -- because he routinely
        reshapes a span and `how tall is mount everest` answered with the query
        `mount everest` is a fresh question about the right thing. Demanding
        "tall" as well scored that a miss, which would have credited the
        history with a turn the history did not touch.

        And a splice is excluded explicitly rather than left to fail the
        subject test: `the currency of brazil` answered with `the capital of
        brazil` carries the probe's head and is still the previous turn's stem
        wearing this turn's noun. It has its own column and must not also count
        as a hit.
        """
        p = self.probed
        if self.grid != "H" or p is None or self.family == "social":
            return None
        if p.called != "web_search" or not p.query:
            return False
        if self.reissued_query or self.reissued_utterance or self.spliced:
            return False
        return _carries(p.query, self.probe)

    @property
    def reissued_query(self) -> bool | None:
        h, p = self.history, self.probed
        if self.grid != "H" or p is None or h is None or not h.query \
                or self.family == "social":
            return None
        return bool(p.query) and _same(p.query, h.query)

    @property
    def reissued_utterance(self) -> bool | None:
        h, p = self.history, self.probed
        if self.grid != "H" or p is None or h is None or self.family == "social":
            return None
        return bool(p.query) and _same(p.query, h.ask)

    @property
    def spliced(self) -> bool | None:
        h, p = self.history, self.probed
        if self.grid != "H" or p is None or h is None or not h.query \
                or not p.query or self.family == "social":
            return None
        return _spliced(h.query, p.query, self.probe)

    @property
    def wrote_when_not_asked(self) -> bool | None:
        """Entry 6b: a note on a turn that asked a question."""
        p = self.probed
        if self.grid != "H" or p is None or self.family == "social":
            return None
        return p.called == "save_note"

    @property
    def social_answered(self) -> bool | None:
        """PLAN-CONVERSATION 5c: a second social move, answered as one.

        No call, and the reply reads as an answer to the probe's family under
        the same markers `social.family` scores with. Model- or runtime-
        authored alike: the column is whether the *conversation* held, and
        `say_author` on the case says who wrote it.
        """
        p = self.probed
        if self.grid != "H" or p is None or self.family != "social":
            return None
        if p.called is not None:
            return False
        fam = social_family(self.probe)
        return fam is not None and fam in reply_families(p.say.get("text") or "")

    @property
    def copied_from(self) -> str | None:
        """Which prior turn the probe's query was lifted from, if any.

        `bound` is the turn before the probe -- its query, or its user text
        (the `reissued_*` pair, named as one source); `distractor` is any
        earlier turn's; `none` is a query that is nobody's. At depth 1 the
        distractor answer cannot occur, which is why PLAN-CONVERSATION 6d
        reads this at depth 3 before arm 8 trains.
        """
        p = self.probed
        if self.grid != "H" or p is None or not self.prior:
            return None
        if not p.query:
            return "none"
        bound = self.prior[-1]
        if (bound.query and _same(p.query, bound.query)) or _same(p.query, bound.ask):
            return "bound"
        for t in self.prior[:-1]:
            if (t.query and _same(p.query, t.query)) or _same(p.query, t.ask):
                return "distractor"
        return "none"

    @property
    def adjacent_frame_kept(self) -> bool | None:
        a = self.adjacent
        return None if a is None else a.frame_kept


def _words(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()


# **One stop list and one splice definition, and `scripts/count_ft_rates.py`
# imports both from here rather than keeping its own.** The log counter and this
# cell score the same species on the same argument, so two copies is two
# verdicts that can drift -- and they did, on the first build: this file's list
# was missing "about", so `what about Sweden?` composing `the capital of Sweden`
# read as a splice here and as the trained chain there. `scripts/` may import
# `harness/` and not the reverse, so the definition lives on this side of that
# line.
STOP = {"the", "a", "an", "of", "in", "on", "for", "to", "is", "are", "was",
        "were", "do", "does", "did", "what", "whats", "who", "how", "when",
        "s", "it", "that", "this", "and", "about", "much", "many", "me", "my",
        "you", "your", "can", "could", "would", "please", "look", "up"}


def _same(a: str, b: str) -> bool:
    return _words(a) == _words(b) and bool(_words(a))


def _carries(got: str, want: str) -> bool:
    """The query carries the probe's head -- its last two content words.

    `harness/searchgrid.py`'s `kept_subject` rule, for its reason exactly: he
    reshapes a span routinely ("look up Ada Lovelace" produced `ada-lovelace`,
    a URL slug and still the right subject), so requiring the determiner or
    every modifier fails a correct call. The head covers what was asked about
    without demanding he echo the sentence.
    """
    want_w = [w for w in _words(want) if w not in STOP][-2:]
    got_w = set(_words(got))
    return bool(want_w) and all(w in got_w for w in want_w)


def _spliced(prev_query: str, cur_query: str, probe: str) -> bool:
    """The previous stem, carrying this turn's noun, missing this turn's ask.

    `scripts/count_ft_rates.py`'s definition, for its reason: "keep the opening
    words, change the end" is *also* the trained chain, so the stem test alone
    would score composition as corruption.
    """
    p, c = _words(prev_query), _words(cur_query)
    if len(p) < 3 or len(c) < 2 or p == c or p[:2] != c[:2]:
        return False
    novel = [w for w in _words(probe) if w not in STOP and w not in set(p)]
    return bool(novel) and not all(w in set(c) for w in novel)


def build(seed: int = 0, depth: int = 1) -> list[Case]:
    """Every case before any of them runs. Pure and seeded.

    `depth` is how many prior exchanges sit in front of the probe on the
    non-control arms: 1 is the opener alone (every card that exists), N puts
    N-1 distractors before it -- PLAN-CONVERSATION 6d's `copied_from` read.
    """
    if depth < 1:
        raise ValueError("depth is at least 1: the opener itself")
    rng = random.Random(seed)
    openers = history_openers(rng)
    cases: list[Case] = []

    for carrier in EVENT_CARRIERS:
        for label, imp, punct in event_forms():
            cases.append(Case(grid="E", arm="control", probe=carrier,
                              form=label, imperative=imp, punctuated=punct,
                              opener=None))

    for arm in ARMS:
        for family, probes in FAMILIES.items():
            for probe in probes:
                opener = openers.get(arm)
                extra = (distractors_for(rng, depth - 1, openers["lookup_ok"])
                         if opener is not None and depth > 1 else [])
                cases.append(Case(grid="H", arm=arm, probe=probe, form="",
                                  family=family, opener=opener,
                                  distractors=extra))
    return cases


def asks_for(case: Case) -> list[str]:
    """The utterances this case will send, in order."""
    if case.grid == "E":
        return [render_event(case.probe, case.imperative, case.punctuated)]
    if case.opener is None:
        return [case.probe]
    return [*case.distractors, case.opener, case.probe, THIRD_TURN]


def run_case(client: Client, case: Case) -> Case:
    """One conversation from a cleared history.

    The reset is per **case**: Grid H's whole subject is what one turn does to
    the next, so resetting between them would delete the measurement.
    """
    for _ in client.request(op="reset"):
        pass
    for ask in asks_for(case):
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

H_ROWS = ("routed_fresh", "reissued_query", "reissued_utterance", "spliced",
          "wrote_when_not_asked", "adjacent_frame_kept")
# The social family's own rows -- the routing columns read `None` on it.
S_ROWS = ("social_answered", "adjacent_frame_kept")


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


def _grid_e(cases: list[Case]) -> dict:
    print()
    print("=" * 76)
    print("Grid E -- entry 1.  the imperative and the question mark, crossed")
    print("           independently, because the live rescue moved both")
    forms = [label for label, _i, _q in event_forms()]
    print()
    print(f"  {'':<14} " + " ".join(f"{f:>13}" for f in forms))
    routed = {f: _score([c for c in cases if c.form == f], "event_routed")
              for f in forms}
    dated = {f: _score([c for c in cases if c.form == f], "chose_date")
             for f in forms}
    print(f"  {'routed':<14} " + " ".join(f"{_cell(*routed[f]):>13}" for f in forms))
    print(f"  {'-> date tool':<14} " + " ".join(f"{_cell(*dated[f]):>13}" for f in forms))

    # The two one-variable comparisons, which is what "independently" buys.
    def pooled(pred):
        rows = [c for c in cases if pred(c)]
        return _score(rows, "event_routed")
    print()
    print(f"  imperative off  {_cell(*pooled(lambda c: not c.imperative))}"
          f"    imperative on   {_cell(*pooled(lambda c: c.imperative))}")
    print(f"  bare            {_cell(*pooled(lambda c: not c.punctuated))}"
          f"    punctuated      {_cell(*pooled(lambda c: c.punctuated))}")

    where: dict[str, int] = {}
    for c in cases:
        if c.probed is None or c.event_routed:
            continue
        k = c.probed.called or "(nothing)"
        where[k] = where.get(k, 0) + 1
    print(f"  the misses reached  "
          + (", ".join(f"{k} {v}" for k, v in
                       sorted(where.items(), key=lambda kv: -kv[1]))
             or "(nothing missed)"))

    print()
    print("  by carrier, routed / -> date tool")
    for carrier in EVENT_CARRIERS:
        rows = [c for c in cases if c.probe == carrier]
        print(f"    {carrier:<46} {_cell(*_score(rows, 'event_routed'))} "
              f"{_cell(*_score(rows, 'chose_date'))}")

    return {"by_form": {f: {"routed": list(routed[f]),
                            "chose_date": list(dated[f])} for f in forms},
            "imperative_off": list(pooled(lambda c: not c.imperative)),
            "imperative_on": list(pooled(lambda c: c.imperative)),
            "bare": list(pooled(lambda c: not c.punctuated)),
            "punctuated": list(pooled(lambda c: c.punctuated)),
            "by_carrier": {carrier: {
                "routed": list(_score([c for c in cases if c.probe == carrier],
                                      "event_routed")),
                "chose_date": list(_score([c for c in cases if c.probe == carrier],
                                          "chose_date"))}
                for carrier in EVENT_CARRIERS},
            "misses": where}


def _grid_h(cases: list[Case]) -> dict:
    print()
    print("=" * 76)
    print("Grid H -- entries 4 and 6b.  one history, then a probe of its own")

    print()
    print("  did each arm set the history its name claims?")
    landed: dict[str, list[int]] = {}
    for arm in ARMS:
        rows = [c for c in cases if c.arm == arm]
        hit, n = _score(rows, "arm_landed")
        landed[arm] = [hit, n]
        if n:
            flag = "" if hit == n else "   !! the rest measured another history"
            print(f"    {arm:<22} {_cell(hit, n)}  {ARM_INTENT[arm]}{flag}")
        else:
            print(f"    {arm:<22}   --   (no turn 1 -- this is the control)")

    # **Reported per probe family, not pooled, and the first read is why.**
    # `wrote_when_not_asked` read 0 of 32 over attribute lookups, which says
    # nothing about entry 6b -- its live sighting was an arithmetic question.
    # Pooling the two families would bury a real difference in a denominator
    # that belongs to the other entry.
    out: dict[str, dict] = {}
    for family in FAMILIES:
        print()
        print(f"  probe family: {family}")
        rows_for = S_ROWS if family == "social" else H_ROWS
        print(f"    {'':<20} " + " ".join(f"{r[:11]:>12}" for r in rows_for))
        fam = [c for c in cases if c.family == family]
        for arm in ARMS:
            rows = [c for c in fam if c.arm == arm]
            cells = {r: _score(rows, r) for r in rows_for}
            print(f"    {arm:<20} "
                  + " ".join(f"{_cell(*cells[r]):>12}" for r in rows_for))
            out.setdefault(family, {})[arm] = {k: list(v)
                                               for k, v in cells.items()}
        if family == "social":
            ctl_s = _score([c for c in fam if c.arm == "control"], "social_answered")
            print(f"    the control answers {_cell(*ctl_s)}; every drop below "
                  f"it is what the history cost the conversation")
            out[family]["control_social_answered"] = list(ctl_s)
            continue

        ctl = _score([c for c in fam if c.arm == "control"], "routed_fresh")
        print(f"    the control routes {_cell(*ctl)}; every drop below it is "
              f"what the history cost")
        for arm in ARMS[1:]:
            hit, n = _score([c for c in fam if c.arm == arm], "routed_fresh")
            if n and ctl[1]:
                print(f"      {arm:<20} {_cell(hit, n)}  "
                      f"{hit / n - ctl[0] / ctl[1]:+.0%}")
        out.setdefault(family, {})["control_routed_fresh"] = list(ctl)

    where: dict[str, int] = {}
    for c in cases:
        if c.probed is None or c.routed_fresh or c.family == "social":
            continue
        k = c.probed.called or "(nothing)"
        where[k] = where.get(k, 0) + 1
    print(f"  the misses reached  "
          + (", ".join(f"{k} {v}" for k, v in
                       sorted(where.items(), key=lambda kv: -kv[1]))
             or "(nothing missed)"))

    # **`copied_from`, PLAN-CONVERSATION 6d.** Where a re-issued query came
    # from, over every history arm, so the §1 defect can be named rather than
    # counted. At depth 1 `distractor` is impossible and the column says so.
    depth = 1 + max((len(c.distractors) for c in cases), default=0)
    copied: dict[str, int] = {}
    for c in cases:
        v = c.copied_from
        if v is not None and c.family != "social":
            copied[v] = copied.get(v, 0) + 1
    print(f"  copied_from at depth {depth}: "
          + (", ".join(f"{k} {copied[k]}" for k in ("bound", "distractor", "none")
                       if k in copied) or "--")
          + ("   (distractor cannot occur at depth 1)" if depth == 1 else ""))

    bad = [c for c in cases if c.grid == "H" and not c.routed_fresh
           and c.probed is not None and c.probed.query and c.family != "social"]
    if bad:
        print()
        print("  every probe whose query was not its own:")
        for c in bad[:14]:
            prev = c.history.query if c.history else None
            print(f"    [{c.arm}] after {str(prev)[:34]!r}")
            print(f"        {c.probe[:38]!r} -> {c.probed.query!r}")

    return {"by_family_arm": out, "arm_landed": landed, "misses": where,
            "copied_from": copied, "depth": depth}


def report(cases: list[Case], info: dict, seed: int) -> dict:
    grids: dict[str, dict] = {}
    e = [c for c in cases if c.grid == "E"]
    h = [c for c in cases if c.grid == "H"]
    if e:
        grids["E"] = _grid_e(e)
    if h:
        grids["H"] = _grid_h(h)

    return {
        "harness": "historygrid/1",
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
            # **Recorded because entry 4 was measured under two histories.**
            # The pack drive's ~1-in-3 was taken with six packs mounted and the
            # late drive's 2-of-3 without any, so a card that could not say
            # which it was cannot be compared with either.
            "packs": info.get("packs"),
            "doc": info.get("doc"),
            "reach": info.get("reach"),
            "decline": info.get("decline"),
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
        "grids": grids,
        "cases": [
            {"grid": c.grid, "arm": c.arm, "form": c.form, "probe": c.probe,
             "family": c.family,
             "opener": c.opener, "arm_landed": c.arm_landed,
             "distractors": c.distractors,
             "scores": ({"event_routed": c.event_routed,
                         "chose_date": c.chose_date} if c.grid == "E" else
                        {r: getattr(c, r) for r in H_ROWS}
                        | {"social_answered": c.social_answered,
                           "copied_from": c.copied_from}),
             "turns": [{"ask": t.ask, "called": t.called,
                        "arguments": t.args or None,
                        "answered": t.answered, "empty": t.empty,
                        "frame_kept": t.frame_kept,
                        "say": (t.say.get("text") or "")[:160],
                        "say_author": t.say.get("author"),
                        "error": t.error} for t in c.turns]}
            for c in cases
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="entries 1, 4 and 6b")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--seed", type=int, default=0,
                    help="which FACTS subject the lookup_ok arm draws")
    ap.add_argument("--grid", choices=("E", "H"), action="append",
                    help="run one grid only; both by default")
    ap.add_argument("--json", help="write the scorecard here")
    ap.add_argument("--depth", type=int, default=1,
                    help="prior exchanges in front of the probe on the history "
                         "arms: 1 is the opener alone (every card so far), N "
                         "puts N-1 unrelated exchanges before it so copied_from "
                         "can name which turn he copied (PLAN-CONVERSATION 6d)")
    ap.add_argument("--write-pack", metavar="DIR",
                    help="write the fixture pack the lookup_pack arm needs "
                         "into DIR and exit; mount it with the server's "
                         "--packs and run this grid again")
    args = ap.parse_args()

    if args.write_pack:
        where = write_fixture_pack(Path(args.write_pack))
        print(f"wrote {len(FIXTURE_PACK)} file(s) to {where}")
        print(f"  python -m harness.server --ckpt <ckpt> --multi --no-log "
              f"--packs {where}")
        return 0

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

    print(f"historygrid against {info.get('ckpt')}")
    print(f"  temperature {info.get('temperature')}   speech "
          f"{info.get('speech_temperature')}   multi {info.get('multi')}   "
          f"search {info.get('search')}   packs {bool(info.get('packs'))}")

    planned = [c for c in build(args.seed, args.depth)
               if not args.grid or c.grid in args.grid]
    if not info.get("multi") and any(c.opener is not None for c in planned):
        print("\nthis instance is not --multi, so every Grid H probe opens on "
              "an empty history and the arms are all the control. Restart with "
              "--multi.", file=sys.stderr)
        client.close()
        return 2

    turns = sum(len(asks_for(c)) for c in planned)
    print(f"  {len(planned)} cases, {turns} turns planned")
    if not info.get("packs") and any(c.arm == "lookup_pack" for c in planned):
        print("  !! no pack is mounted, so the lookup_pack arm will fall "
              "through to the table and land 0 -- `--write-pack DIR` emits "
              "the fixture and the server's --packs mounts it")

    started = time.perf_counter()
    done: list[Case] = []
    for i, case in enumerate(planned, 1):
        run_case(client, case)
        bad = next((t for t in case.turns if t.error), None)
        if bad:
            print(f"turn raised: {bad.ask!r} -- {bad.error}", file=sys.stderr)
            return 2
        done.append(case)
        if i % 20 == 0:
            print(f"    {i}/{len(planned)} ...")

    card = report(done, info, args.seed)
    card["depth"] = args.depth
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
