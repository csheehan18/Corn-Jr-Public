"""Can he tell that a question is a lookup? A grid, because a list cannot say.

**The question `checkup` asks three times and cannot answer.** It carries three
`web_search` cases, all of them real-world subjects, two of them opening "look
up". They pass or they do not and either way the number is three, so what the
project knows about the one tool that reaches outside the machine is a rate
with a denominator of three.

Fifteen natural questions put against `corn_jr_260m` scored **4 of 15**, and
every one of the four opened with the words "look up". The obvious reading is
that he needs an imperative. That reading is wrong, and a longer list of
questions would have kept it: `corn/toolgen.py`'s `SEARCH_TEMPLATES` already
contains "what's {q}", "what is {q}" and "do you know {q}", so the corpus does
teach the question form. Something else was moving.

**Two variables, and only a grid separates them.** The search index the corpus
was generated from is `corn/tools.py`'s `FACTS`, and every entry in it is
*invented* -- "the capital of Eskirskvik" resolves to "Raviskholm". A real
subject is a different regime, which is the fiftieth finding's whole subject:
handed a real entity the weights reopen and compete with the observation. That
finding measured it on what he *says*. This measures whether it also decides
what he *reaches for*.

So: the same grammatical shape, filled once from `FACTS` and once from the
world, across templates of both kinds. Four cells, and the reading is in the
difference between them rather than in any one.

    routed          the first call of the turn is `web_search` -- not
                    `decline`, not `save_note`, and not nothing at all, which
                    is a real outcome here and the worst one
    kept_subject    the `query` argument contains the subject that was asked
                    about. A call to the right tool carrying the wrong string
                    is a lookup of something nobody asked for, and `routed`
                    alone would score it as a success

**The invented column is the control and is not optional.** Without it a poor
score reads as "the checkpoint is bad at search" when it may be "this cell is
hard", and the two call for different work -- one is a training run and the
other is a corpus that never showed him the case. It is the same argument
`harness/converse.py` makes for its `trained=True` class, applied to a
different axis.

**No `--search` needed, and that is a property rather than a convenience.**
Routing and argument extraction both happen before any tool runs, so the whole
grid measures with `web_search` still answering out of the table and nothing
leaving the machine. What live search would add is the *answer* half -- whether
he reads a real result back faithfully -- and that is the fiftieth finding's
territory, already documented, and a different instrument's job.

**A rate, not a gate.** Same contract as `checkup` and `converse`: this reports
rates and exits 0 on a poor result, and non-zero only on something structural --
no server, or a turn that raised. What a 260M does with a phrasing is behaviour,
and a pass/fail line here would sit red and then be ignored.

Usage:
    python -m harness.searchgrid
    python -m harness.searchgrid --json harness/results/corn_jr_260m__grid.json
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from corn.tools import FACTS

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision

# **All twenty-five the corpus teaches, not a sample of them.** The first cut
# of this file grouped four imperatives against four questions and reported the
# two means. That grouping was wrong and the means hid it: `search for {q}`
# names the tool in the imperative and scores 2 of 8, while `what's {q}` only
# implies it and scores 5 of 8. Averaging those two into "imperative 15/32,
# question 11/32" produced a tidy table that was measuring nothing, because the
# variance is *between templates* and not between their grammatical classes.
#
# So every phrasing the corpus contains is run, and the report is per template.
# 25 x 8 shapes x 2 worlds is 400 turns and about two and a half minutes, which
# is the right trade for the only instrument that can see this axis at all.
#
# **Held here rather than imported from `corn/toolgen.py`, for two reasons and
# the first is structural.** `scripts/check_layering.py` asserts `harness/`
# imports nothing from `corn/` outside the inference closure, and the
# generators stay behind when this package becomes its own repository. `FACTS`
# is inside that closure -- `corn/agent.py` reaches it through `corn/tools.py`
# -- and `SEARCH_TEMPLATES` is not.
#
# The second is that an instrument should pin what it measures.
# `scripts/check_searchgrid.py` asserts this tuple equals the corpus's exactly,
# so a phrasing added there is a decision here rather than a denominator that
# moved between two runs somebody wanted to compare.
TEMPLATES = (
    "what's {q}",
    "look up {q}",
    "search for {q}",
    "can you look up {q}",
    "find out {q}",
    "google {q}",
    "what is {q}",
    "tell me {q}",
    "look {q} up for me",
    "do you know {q}",
    "have a look for {q}",
    "find me {q}",
    "what was {q}",
    "remind me what {q} is",
    "could you look up {q}",
    "check {q}",
    "see if you can find {q}",
    "I need to know {q}",
    "any idea what {q} is",
    "search {q}",
    "look for {q}",
    "what would {q} be",
    "can you find out {q}",
    "quick, {q}",
    "do me a search for {q}",
)

# Recorded, and deliberately not the reporting axis -- see above. Kept because
# "did he learn the imperative and not the question" is a reasonable hypothesis
# that this grid happens to refute, and refuting it again later should not
# require re-deriving which template was which.
IMPERATIVE_FORMS = frozenset({
    "look up {q}", "search for {q}", "find out {q}", "check {q}",
    "look {q} up for me", "have a look for {q}", "find me {q}",
    "could you look up {q}", "can you look up {q}", "see if you can find {q}",
    "search {q}", "look for {q}", "can you find out {q}", "tell me {q}",
    "do me a search for {q}", "google {q}", "remind me what {q} is",
})


# **Matched by shape, filled from two worlds.** Each entry is a `FACTS` shape
# and a real-world subject of the identical grammatical form, so the only thing
# that differs across a row is whether the thing being asked about exists. A
# real subject of a *different* shape would confound the two variables again,
# which is the mistake the fifteen-question list made.
SHAPES = (
    ("the capital of", "the capital of Laos"),
    ("the population of", "the population of Iceland"),
    ("the discoverer of", "the discoverer of penicillin"),
    ("the currency of", "the currency of Japan"),
    ("the official language of", "the official language of Brazil"),
    ("the melting point of", "the melting point of iron"),
    ("the length of the", "the length of the Nile"),
    ("the river that runs through", "the river that runs through Cairo"),
)


def invented_subjects(rng: random.Random) -> dict[str, str]:
    """One invented subject per shape, drawn from the table itself.

    Drawn rather than listed because a listed one would be a span of this file
    and `FACTS` is regenerated: a name that stopped existing would quietly
    become a real-world miss dressed as an invented one, which is precisely the
    confound the grid is built to remove. Seeded, so a rerun is the same grid.
    """
    picked: dict[str, str] = {}
    for shape, _ in SHAPES:
        candidates = [q for q, _a, _s in FACTS if q.startswith(shape + " ")]
        if candidates:
            picked[shape] = rng.choice(candidates)
    return picked


@dataclass
class Cell:
    """One template or one shape, split by which world the subject came from."""
    label: str
    inv_routed: int = 0
    inv_n: int = 0
    real_routed: int = 0
    real_n: int = 0
    kept: int = 0

    def add(self, turn: "Turn") -> None:
        if turn.world == "invented":
            self.inv_n += 1
            self.inv_routed += turn.routed
        else:
            self.real_n += 1
            self.real_routed += turn.routed
        self.kept += turn.kept_subject

    @property
    def total(self) -> int:
        return self.inv_routed + self.real_routed


@dataclass
class Turn:
    ask: str
    template: str
    world: str
    subject: str
    called: str | None
    query: str | None
    error: str | None = None

    @property
    def routed(self) -> bool:
        return self.called == "web_search"

    @property
    def kept_subject(self) -> bool:
        """The query carries what was asked about.

        Compared on content words rather than as a substring, because he
        routinely reshapes the span -- "look up Ada Lovelace" produced
        `ada-lovelace`, which is a URL slug and is still the right subject.
        Requiring the last two words covers the head of every shape here
        without demanding he echo the determiner.
        """
        if not self.routed or not self.query:
            return False
        want = _words(self.subject)[-2:]
        got = _words(self.query)
        return bool(want) and all(w in got for w in want)


def _words(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()


def run_turn(client: Client, ask: str, template: str, world: str,
             subject: str) -> Turn:
    """One utterance from a cleared history.

    The reset is `checkup.run_case`'s, for its reason exactly: history lives on
    the session, so against a `--multi` instance every cell after the first
    would open on the tail of the one before and the grid would be measuring a
    sixty-turn context nobody wrote.
    """
    for _ in client.request(op="reset"):
        pass
    called = query = error = None
    for ev in client.request(op="turn", user=ask):
        if ev.get("t") == "call" and called is None:
            called = ev.get("name")
            args = ev.get("arguments")
            if isinstance(args, dict):
                q = args.get("query")
                query = q if isinstance(q, str) else None
        elif ev.get("t") == "error":
            error = ev.get("why", "?")
    return Turn(ask, template, world, subject, called, query, error)


def report(turns: list[Turn], info: dict) -> dict:
    """Two tables and a pooled delta, in that order of importance.

    Per template first, because that is where the variance is and the pooled
    number is an average over cells that do not belong together. Per shape
    second, because the subject turns out to matter nearly as much and nothing
    else in the project would show it. The invented-versus-real delta last:
    it is the smallest of the three effects and the only one that was
    predicted, which is a reason to report it and not to lead with it.
    """
    by_template: dict[str, Cell] = {}
    by_shape: dict[str, Cell] = {}
    for turn in turns:
        by_template.setdefault(turn.template, Cell(turn.template)).add(turn)
        shape = " ".join(turn.subject.split()[:-1])
        by_shape.setdefault(shape, Cell(shape)).add(turn)

    def table(title: str, cells: dict[str, Cell], width: int) -> None:
        print()
        print(f"  {title}")
        print(f"    {'':<{width}} {'invented':>10} {'real':>10}")
        for c in sorted(cells.values(), key=lambda c: (-c.total, c.label)):
            print(f"    {c.label:<{width}} {c.inv_routed:>4}/{c.inv_n:<5}"
                  f"{c.real_routed:>5}/{c.real_n:<5}")

    table("routed to web_search, by phrasing", by_template, 24)
    table("routed to web_search, by subject", by_shape, 30)

    inv_r = sum(c.inv_routed for c in by_template.values())
    inv_n = sum(c.inv_n for c in by_template.values())
    real_r = sum(c.real_routed for c in by_template.values())
    real_n = sum(c.real_n for c in by_template.values())
    kept = sum(t.kept_subject for t in turns)
    print()
    print(f"  pooled       invented {inv_r}/{inv_n} ({inv_r / max(inv_n,1):.0%})"
          f"   real {real_r}/{real_n} ({real_r / max(real_n,1):.0%})"
          f"   delta {inv_r / max(inv_n,1) - real_r / max(real_n,1):+.0%}")
    print(f"  query kept the subject {kept}/{len(turns)} "
          f"({kept}/{inv_r + real_r} of the calls he made)")

    # Where the misses went. `decline` and `place_call` are different failures
    # -- one is the over-declining the fifty-first finding measured, the other
    # is a routing error carrying a side effect -- and pooling them would hide
    # which one moved between checkpoints.
    missed: dict[str, int] = {}
    for turn in turns:
        if not turn.routed:
            missed[turn.called or "(nothing)"] = (
                missed.get(turn.called or "(nothing)", 0) + 1)
    spread = ", ".join(f"{k} {v}" for k, v in
                       sorted(missed.items(), key=lambda kv: -kv[1]))
    print(f"  the misses reached     {spread}")

    return {
        "harness": "searchgrid/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        # See `checkup.report`. `TEMPLATES` and `SHAPES` are spans of this
        # file, so a card that cannot name its revision cannot name its grid.
        "source": revision(),
        # `fold` joined the tuple with owner decision 1b/0: this cell is in
        # the regression set, and a before-card read without the fold and an
        # after-card read with it are two measurements of two machines. See
        # `corn.agent.fold_turn`.
        "instance": {k: info.get(k) for k in
                     ("ckpt", "search", "temperature", "decline", "grammar",
                      "fold")},
        "pooled": {"invented": {"routed": inv_r, "n": inv_n},
                   "real": {"routed": real_r, "n": real_n},
                   "kept_subject": kept},
        "by_template": {c.label: {"invented": [c.inv_routed, c.inv_n],
                                  "real": [c.real_routed, c.real_n],
                                  "imperative": c.label in IMPERATIVE_FORMS}
                        for c in by_template.values()},
        "by_shape": {c.label: {"invented": [c.inv_routed, c.inv_n],
                               "real": [c.real_routed, c.real_n]}
                     for c in by_shape.values()},
        "misses": missed,
        "turns": [t.__dict__ for t in turns],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--seed", type=int, default=0,
                    help="which invented subject is drawn per shape")
    ap.add_argument("--json", help="write the scorecard here")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    invented = invented_subjects(rng)
    if len(invented) != len(SHAPES):
        missing = [s for s, _ in SHAPES if s not in invented]
        print(f"FACTS has no entries for {missing} -- the grid would be "
              f"uneven and its columns are only comparable while it is not.",
              file=sys.stderr)
        return 2

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

    print(f"searchgrid against {info.get('ckpt')}")
    print(f"  web_search backend: {info.get('search')}   "
          f"temperature {info.get('temperature')}   "
          f"decline offered: {info.get('decline')}")

    turns: list[Turn] = []
    started = time.perf_counter()
    for template in TEMPLATES:
        for shape, real in SHAPES:
            for world, subject in (("invented", invented[shape]),
                                   ("real", real)):
                turn = run_turn(client, template.format(q=subject),
                                template, world, subject)
                if turn.error:
                    print(f"turn raised: {turn.ask!r} -- {turn.error}",
                          file=sys.stderr)
                    return 2
                turns.append(turn)

    card = report(turns, info)
    card["seconds"] = round(time.perf_counter() - started, 1)
    print(f"\n  {len(turns)} turns in {card['seconds']}s")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
