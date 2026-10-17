"""Entry 3's two confounded axes, pulled apart: how deep a chain goes, and which carrier carries it.

**`chain_pronoun` reads 40/50 on the v4 base and is frozen there.** Ground rule
2 forbids redefining it, and nothing here does: this is a **new** cell for the
two things that row cannot separate, flagged as optional in the build brief and
built because both axes are one conversation apart.

`docs/PLAN-FINETUNE-V4.md` entry 3 has the confound in its own words: the third
round found composition working exactly once -- `the capital of france` ->
`what about spain?` composes cleanly -> `and italy?` **re-issues the Spain query
and answers "Madrid" to a question about Italy** -- and the weak carrier is the
bare elliptical `and X?`, which is also the shape session 14's four-row control
missed. "Depth and carrier are confounded at this n; the cell should carry both
axes." So:

## Grid C -- composition, by depth and by carrier

One trained lookup frame, then two follow-ups naming new entities, each in one
of the two carriers the drives disagree about:

    what about {e}?     4 for 5 across drives
    and {e}?            0 for 2 across drives

Depth 2 is the first follow-up and depth 3 the second, and because both depths
ride one conversation the axes are crossed rather than sampled. Three columns,
because the live failures are three different things:

    composed    the query is turn 1's frame carrying THIS turn's entity --
                the gold, and the only outcome that answers the question asked
    reissued    the query is the previous turn's, byte for byte. The depth-3
                live failure, and the one that answers confidently and wrongly
    literal     the query is the follow-up utterance itself -- "and italy?"
                searched as written, which is the surrender rather than the
                confabulation

## Grid P -- the pronoun, and its three endings

Entry 3's *other* half, and the late drive found it failing three ways, two of
them confident: `who is the president of france?` then `how old is he?` searched
the literal question and the provider **answered it** ("2 days old.");
`the capital of japan` then `how big is it?` **re-issued** the previous query and
answered "Tokyo." to a size question; and after session 14's slot removal the
same shape can come back as a bare `<|end|>` and a runtime floor. One gold,
three misses -- so the misses are columned separately here rather than pooled
into one.

    resolved    the query carries the antecedent and not the pronoun
    literal     the query still carries the pronoun -- searched as written
    reissued    the previous query again
    surrendered no call at all

**This is not `chain_pronoun` re-scored.** That row is a frozen eval file with
its own construction; this is a live two-turn cell on carriers written for it,
and the two are not comparable numbers. What this adds is the *split*: which of
the three endings a miss took, which the frozen row cannot say.

---

**No `--search` needed** -- the composition happens before any tool runs.
**`--multi` is required**: every case here is a two- or three-turn conversation
and the history is the measurement.

**Ground rule 16.** Every entity is a country or a city; no contact, no name,
no instance fact.

**A rate, not a gate.**

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_v4/ckpt.pt \
        --no-log --multi
    python -m harness.chaingrid \
        --json harness/results/corn_jr_260m_v4__chaingrid.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision

# **The frames are the four attribute shapes that read at ceiling first-turn.**
# A frame that failed on its own turn would make every depth below it
# unreadable, which is why the cell borrows the strongest carriers on the
# machine rather than writing new ones.
FRAMES = (
    ("the capital of {e}", ("france", "spain", "italy")),
    ("the population of {e}", ("japan", "brazil", "kenya")),
    ("the currency of {e}", ("norway", "peru", "vietnam")),
    ("the official language of {e}", ("egypt", "chile", "finland")),
)

# The two carriers the drives disagree about, and nothing else: the axis is
# which of these two it is, and a third would put variance somewhere this cell
# cannot report it.
CARRIERS = {
    "what about {e}?": "what about {e}?",
    "and {e}?": "and {e}?",
}

# **The pronoun follow-ups, one per pro-form the entry names.** Each is paired
# with a frame whose answer it can plausibly refer to, so the antecedent is
# unambiguous to a person and the only question is whether he substitutes it.
PRONOUN_CASES = (
    ("the capital of japan", "japan", "how big is it?"),
    ("the capital of norway", "norway", "how many people live there?"),
    ("the president of france", "france", "how old is he?"),
    ("the capital of peru", "peru", "what is it called?"),
    ("the population of kenya", "kenya", "is it growing?"),
    ("the currency of vietnam", "vietnam", "what is it worth?"),
)
PRONOUNS = ("it", "there", "he", "she", "they", "them", "that one", "those")

PROVENANCE = {
    "frames": "the four attribute shapes that read at ceiling first-turn, "
              "borrowed so a depth-2 miss is attributable to the depth",
    "carriers": "the two entry 3 names, and only those two",
    "pronoun cases": "written for this instrument; countries and cities only, "
                     "ground rule 16",
}


def _words(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()


@dataclass
class Turn:
    ask: str
    calls: list[dict] = field(default_factory=list)
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
    def query(self) -> str | None:
        args = self.model_calls[0].get("arguments") if self.model_calls else None
        q = args.get("query") if isinstance(args, dict) else None
        return q.strip() if isinstance(q, str) else None


@dataclass
class Case:
    grid: str
    carrier: str          # Grid C's axis label
    frame: str
    entities: tuple[str, ...]
    asks: tuple[str, ...]
    antecedent: str = ""  # Grid P's
    turns: list[Turn] = field(default_factory=list)

    def want_at(self, depth: int) -> str:
        """The query turn `depth` should have composed. Depth 1 is turn 1."""
        return self.frame.format(e=self.entities[depth - 1])

    def outcome_at(self, depth: int) -> str | None:
        """What the turn at this depth actually did with the frame.

        One string rather than four booleans, because the four are mutually
        exclusive by construction and a person reading the table wants to know
        which one happened, not to reconstruct it from a row of flags.
        """
        if depth > len(self.turns):
            return None
        turn = self.turns[depth - 1]
        if turn.called is None:
            return "surrendered (no call)"
        if turn.called != "web_search":
            return f"other tool ({turn.called})"
        q = turn.query
        if not q:
            return "web_search, no query"
        got = set(_words(q))
        if self.grid == "C":
            want = self.want_at(depth)
            if set(_words(want)) <= got and len(got) <= len(_words(want)) + 2:
                return "composed"
            if depth > 1 and _words(q) == _words(self.turns[depth - 2].query or ""):
                return "reissued"
            if _words(q) == _words(turn.ask):
                return "literal"
            return "something else"
        # Grid P
        if depth == 1:
            return "composed" if set(_words(self.frame.format(
                e=self.entities[0]))) <= got else "something else"
        if got & set(PRONOUNS):
            return "literal (kept the pronoun)"
        if _words(q) == _words(self.turns[depth - 2].query or ""):
            return "reissued"
        if self.antecedent in got:
            return "resolved"
        return "something else"


def build() -> list[Case]:
    """Every case before any of them runs. Pure and unseeded."""
    cases: list[Case] = []
    for frame, entities in FRAMES:
        for label, carrier in CARRIERS.items():
            asks = (frame.format(e=entities[0]),
                    carrier.format(e=entities[1]),
                    carrier.format(e=entities[2]))
            cases.append(Case("C", label, frame, entities, asks))
    for opener, antecedent, follow in PRONOUN_CASES:
        frame = opener.replace(antecedent, "{e}")
        cases.append(Case("P", "pronoun", frame, (antecedent,),
                          (opener, follow), antecedent=antecedent))
    return cases


def run_case(client: Client, case: Case) -> Case:
    for _ in client.request(op="reset"):
        pass
    for ask in case.asks:
        turn = Turn(ask)
        for ev in client.request(op="turn", user=ask):
            kind = ev.get("t")
            if kind == "call":
                turn.calls.append(ev)
            elif kind == "say":
                turn.say = {k: v for k, v in ev.items() if k not in ("t", "id")}
            elif kind == "error":
                turn.error = ev.get("why", "?")
        case.turns.append(turn)
        if turn.error:
            break
    return case


C_OUTCOMES = ("composed", "reissued", "literal", "surrendered (no call)",
              "something else")
P_OUTCOMES = ("resolved", "literal (kept the pronoun)", "reissued",
              "surrendered (no call)", "something else")


def report(cases: list[Case], info: dict) -> dict:
    grids: dict[str, dict] = {}

    c = [x for x in cases if x.grid == "C"]
    if c:
        print()
        print("=" * 74)
        print("Grid C -- composition by depth and by carrier, crossed")
        print()
        print(f"  {'':<18} " + " ".join(f"{o[:13]:>15}" for o in C_OUTCOMES))
        out: dict[str, dict] = {}
        for label in CARRIERS:
            for depth in (1, 2, 3):
                rows = [x.outcome_at(depth) for x in c if x.carrier == label]
                rows = [r for r in rows if r is not None]
                counts = {o: rows.count(o) for o in C_OUTCOMES}
                name = f"{label} d{depth}" if depth > 1 else f"(turn 1) d1"
                print(f"  {name:<18} "
                      + " ".join(f"{counts[o]:>15}" for o in C_OUTCOMES))
                out[f"{label}|d{depth}"] = counts
        print()
        # The one comparison the entry asks for, stated as one line each.
        for label in CARRIERS:
            rows = [x for x in c if x.carrier == label]
            d2 = sum(1 for x in rows if x.outcome_at(2) == "composed")
            d3 = sum(1 for x in rows if x.outcome_at(3) == "composed")
            print(f"  {label:<18} composed at depth 2 {d2}/{len(rows)}, "
                  f"at depth 3 {d3}/{len(rows)}")
        grids["C"] = out

    p = [x for x in cases if x.grid == "P"]
    if p:
        print()
        print("=" * 74)
        print("Grid P -- the pronoun follow-up, and which of its endings")
        rows = [x.outcome_at(2) for x in p]
        counts = {o: rows.count(o) for o in P_OUTCOMES}
        print()
        for outcome, n in counts.items():
            print(f"    {outcome:<28} {n:>3}/{len(p)}")
        print()
        for x in p:
            t = x.turns[1] if len(x.turns) > 1 else None
            print(f"    {x.asks[0]:<28} {x.asks[1]:<26} -> "
                  f"{(t.query if t else None)!r}")
        grids["P"] = {"outcomes": counts, "n": len(p)}

    return {
        "harness": "chaingrid/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": revision(),
        "decode": {
            "temperature": info.get("temperature"),
            "speech_temperature": info.get("speech_temperature"),
            "multi": info.get("multi"),
            "dtype": info.get("dtype"),
            "search": info.get("search"),
            "packs": info.get("packs"),
            "doc": info.get("doc"),
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
        # Stated in the card as well as the docstring: a reader comparing this
        # against 40/50 is comparing two different constructions.
        "not_chain_pronoun": "chain_pronoun is a frozen eval row with its own "
                             "construction and reads 40/50; this is a live "
                             "two-turn cell on carriers written for it. The "
                             "numbers are not comparable and this cell does "
                             "not redefine that row.",
        "grids": grids,
        "cases": [
            {"grid": x.grid, "carrier": x.carrier, "frame": x.frame,
             "entities": list(x.entities), "antecedent": x.antecedent or None,
             "outcomes": {f"d{d}": x.outcome_at(d) for d in
                          range(1, len(x.asks) + 1)},
             "turns": [{"ask": t.ask, "called": t.called, "query": t.query,
                        "say": (t.say.get("text") or "")[:120],
                        "error": t.error} for t in x.turns]}
            for x in cases
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="entry 3's depth and carrier axes")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--grid", choices=("C", "P"), action="append")
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

    print(f"chaingrid against {info.get('ckpt')}")
    print(f"  temperature {info.get('temperature')}   multi {info.get('multi')}"
          f"   search {info.get('search')}")
    if not info.get("multi"):
        print("\nthis instance is not --multi, so every follow-up opens on an "
              "empty history and has nothing to compose from. Restart with "
              "--multi.", file=sys.stderr)
        client.close()
        return 2

    planned = [x for x in build() if not args.grid or x.grid in args.grid]
    print(f"  {len(planned)} cases, "
          f"{sum(len(x.asks) for x in planned)} turns planned")

    started = time.perf_counter()
    done: list[Case] = []
    for case in planned:
        run_case(client, case)
        bad = next((t for t in case.turns if t.error), None)
        if bad:
            print(f"turn raised: {bad.ask!r} -- {bad.error}", file=sys.stderr)
            return 2
        done.append(case)

    card = report(done, info)
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
