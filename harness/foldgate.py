"""The fold's shipping gate -- the one family `surfacegrid` left out by design.

**Why this instrument exists and why it is not a column on an existing grid.**
Owner decision 1b/0 (`docs/PLAN-FINETUNE-V4.md`, step 5) takes the fold: the
runtime casefolds an all-caps utterance and drops a terminal question mark
before the model sees the turn. `harness/surfacegrid.py` priced that decision
over five carrier families and **none of them is temporal**, which was correct
for entry 0's axis and is exactly the hole here. The corpus count is the
reason:

    user turns ending in "?"      2,442,972   36.99% of 6,603,586
        -> resolve_date           2,268,194
        -> no call at all           173,785
        -> web_search                   993
        -> every other tool                0

A terminal question mark in this corpus means the date tool or it means chat.
So `resolve_date` is the one tool whose 2.27M-row trained signal rides the
character the fold strips, and the fold cannot ship on `surfacegrid`'s read
alone: that grid measured what the strip *buys* on families that pay for the
mark, and this one measures what it *costs* on the family that was paid by it.

**The gate fired, and the strip is retired.** It was built as a
stop-and-report: if the punctuated temporal carriers lost routing under the
fold, the fold would not ship with the strip half enabled. They lost 17 of 24.
The owner retired the strip on 2026-08-30 and the shipped fold is the casefold
alone, so **this file is now two things**: the provenance of that retirement,
and the standing check that whatever the fold becomes next still leaves this
family alone. `--compare` prints the verdict; it does not decide anything.

Under the shipped fold every carrier here is *invariant* -- none of them is
shouting -- and `scripts/check_foldgate.py` asserts that rather than assuming
it, which is what makes "the casefold half costs the temporal family nothing"
a checked claim instead of an argument. The `upper` arm is deliberately absent:
a shouted temporal carrier folds to its own lowercase twin, and that twin is
the bare control column this battery already reads.

## What it read, 2026-08-30 -- the gate failed and the strip was retired

    punctuated resolve_date carriers that reach the weights
        fold off   18/24     fold on   1/24
    the bare control column, which the fold cannot touch
        fold off    7/8      fold on   7/8
    grid T's event_date and neutral, punctuated
        fold off    8/8      fold on   8/8
    turns the hatch answered, both arms                  204/244

Every one of the seventeen turns that moved went `resolve_date` ->
`web_search`: the corpus's 300:1 prior on the mark, deleted. The control column
is byte-identical across the arms, so the two runs are one machine and the
strip is the only thing that moved.

The cards on disk (`..__foldgate-fold-off.json` and `..__foldgate-fold-on.json`)
were read while the strip still existed and are kept as that measurement's
receipt. **They do not reproduce against the shipped runtime**, which no longer
has a strip to turn on, and that is the correct behaviour rather than staleness:
`corn.agent.fold_turn`'s block comment carries the retirement, both prices, and
what replaced the punctuated repair per family.

## The arms are the server's flag, not this file's argument

One run, one instance, one `fold` setting, one card. `harness/server.py
--no-fold` is the before arm and the default is the after arm, and the card
records which it was off `info["fold"]` rather than off a flag passed here --
ground rule 13, and the same rule that made the fold appear in every grid's
`decode` block. Two cards then go to `--compare`.

Pre-folding the utterance against a `--no-fold` server would produce the same
tokens (`fold_turn` is pure and idempotent) and would still be a different
measurement of a different machine: it would not exercise the runtime seam the
decision is about, and the hatch matchers would see a string the folded runtime
never hands them. The gate is cheap enough -- 244 turns an arm, about twenty
seconds -- that the argument does not need making.

## The five families, and three of them are controls

    date_past      DATE_TEMPLATES_PAST     x resolved past expressions
    date_nonpast   DATE_TEMPLATES_NONPAST  x resolved today/future ones
    date_today     DATE_TEMPLATES_TODAY    -- the no-slot family, carried whole
                   ------ gold `resolve_date`; the templates that end in "?"
                   are the population at risk and the ones that do not are the
                   control that says the two arms are otherwise one machine
    event_date     routegrid grid T, punctuated -- read 4/4 `web_search`
    neutral        routegrid grid T's own control, punctuated -- read 4/4

Every carrier is **generator-emitted**: the templates are `corn/temporal.py`'s
own trained pools and the expressions come from its `FAMILIES` draw at a fixed
seed and a fixed anchor, so ground rule 10 is satisfied by construction and
nothing here is a phrasing somebody wrote to make a point. Grid T's two columns
are borrowed rather than copied, so this file cannot come to disagree with
`routegrid` about what they say.

## The hatch is a column, not a filter

Most well-formed date questions never reach the weights: `corn.agent.
temporal_request` recognises them and the runtime writes the call. Those turns
are reported and excluded from the routing rate, because a hatched turn
measures the hatch. The subset that matters is the one that **fell through** --
that is where the corpus's 2.27M-row vote on the question mark is doing the
work, and it is the only place the strip can cost anything.

The hatch rate itself is the second thing this gate watches. `_normalised` is
downstream of the fold and strictly stronger than it, so a hatch decision must
be identical in both arms; if it is not, the fold is reaching somewhere it was
not supposed to and the read is invalid before the routing column is even
looked at.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_v4/ckpt.pt --no-fold
    python -m harness.foldgate --json harness/results/corn_jr_260m_v4__foldgate-fold-off.json
    # restart the server without --no-fold
    python -m harness.foldgate --json harness/results/corn_jr_260m_v4__foldgate-fold-on.json
    python -m harness.foldgate --compare <before.json> <after.json>
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision
from .routegrid import TEMPORAL_CELLS

from corn.temporal import (
    DATE_TEMPLATES_NONPAST, DATE_TEMPLATES_PAST, DATE_TEMPLATES_TODAY,
    FAMILIES as TEMPORAL_FAMILIES,
)

# **A fixed anchor and a fixed seed, and both are load-bearing.** The
# expressions are drawn rather than written, so the draw has to reproduce or
# two runs of this gate are two different batteries and the comparison is
# meaningless. The anchor is the day the decision was taken; nothing in the
# score depends on the date resolving to anything in particular, only on the
# expression being one the corpus's own generator produces.
GATE_ANCHOR = date(2026, 8, 30)
GATE_SEED = 20260830

# How many expressions each slotted template is filled with.
#
# **Eight, and the number was set by the first run rather than picked.** The
# population this gate is actually about is the subset that *falls through*
# `temporal_request` to the weights, and at two expressions a template that
# subset was six turns -- three of which moved. A direction read off six turns
# is an anecdote with a table around it, and the arm costs seconds, so the
# denominator was widened until the router column could carry a reading. Four
# of the twenty-eight date templates miss the hatch, so eight expressions puts
# the at-risk column at 32 rather than 6 and the whole battery at 244 turns,
# about twenty seconds an arm.
PER_TEMPLATE = 8


def expressions(n: int, kinds: tuple[str, ...] = ("resolve",),
                tenses: tuple[str, ...] = ()) -> tuple[str, ...]:
    """`n` distinct expressions from `corn/temporal.py`'s own family draw.

    `kinds` filters to the ones `resolve_date_tool` actually resolves -- a
    `range` or `vague` expression makes the tool ask a clarifying question,
    which is a different behaviour and not the one on trial here. Deduped and
    order-stable, so the battery is a function of `GATE_SEED` alone.
    """
    rng = random.Random(GATE_SEED)
    out: list[str] = []
    seen: set[str] = set()
    # Bounded rather than `while True`: an impossible filter should return a
    # short list and let the caller's own count fail loudly, not spin.
    for _ in range(2000):
        if len(out) >= n:
            break
        fn, _weight = TEMPORAL_FAMILIES[rng.randrange(len(TEMPORAL_FAMILIES))]
        ex = fn(rng, GATE_ANCHOR)
        if ex.kind not in kinds or (tenses and ex.tense not in tenses):
            continue
        if ex.expression in seen:
            continue
        seen.add(ex.expression)
        out.append(ex.expression)
    return tuple(out)


@dataclass(frozen=True)
class Family:
    label: str
    gold: str
    provenance: str
    carriers: tuple[str, ...]


def _fill(templates: list[str], exprs: tuple[str, ...]) -> tuple[str, ...]:
    """Every template x every expression, in template order.

    `{p}` is the recall families' preposition and no date template carries one,
    so the format is `{e}` alone -- asserted by the guard rather than assumed
    here, because a template that grew a second slot would fail silently into a
    carrier with a literal brace in it.
    """
    return tuple(t.format(e=e) for t in templates for e in exprs)


def families() -> tuple[Family, ...]:
    """The five, built. Split out of `build` so the guard can read them."""
    past = expressions(PER_TEMPLATE, tenses=("past",))
    ahead = expressions(PER_TEMPLATE, tenses=("today", "future"))
    return (
        Family("date_past", "resolve_date",
               "corn.temporal.DATE_TEMPLATES_PAST x FAMILIES draw at "
               f"seed {GATE_SEED}, anchor {GATE_ANCHOR.isoformat()}",
               _fill(DATE_TEMPLATES_PAST, past)),
        Family("date_nonpast", "resolve_date",
               "corn.temporal.DATE_TEMPLATES_NONPAST x the same draw, "
               "today and future expressions",
               _fill(DATE_TEMPLATES_NONPAST, ahead)),
        Family("date_today", "resolve_date",
               "corn.temporal.DATE_TEMPLATES_TODAY -- the no-slot family, "
               "carried whole",
               tuple(DATE_TEMPLATES_TODAY)),
        # Borrowed from `routegrid`, punctuated, rather than restated: these
        # two columns are already built and already read 4/4, and a second copy
        # of them here is a second population that could drift.
        Family("event_date", "web_search",
               "harness.routegrid.TEMPORAL_CELLS['event_date'], punctuated",
               tuple(c + "?" for c in TEMPORAL_CELLS["event_date"][1])),
        Family("neutral", "web_search",
               "harness.routegrid.TEMPORAL_CELLS['neutral'], punctuated -- "
               "grid T's own control",
               tuple(c + "?" for c in TEMPORAL_CELLS["neutral"][1])),
    )


def build() -> list["Turn"]:
    """Every turn this gate will run, before any of them runs.

    Pure, so `scripts/check_foldgate.py` can assert the population and put each
    utterance through `fold_turn` and the runtime's hatches without a
    checkpoint.
    """
    return [Turn(family=f.label, gold=f.gold, provenance=f.provenance, ask=c)
            for f in families() for c in f.carriers]


@dataclass
class Turn:
    family: str
    gold: str
    provenance: str
    ask: str
    calls: list[dict] = field(default_factory=list)
    reply: str = ""
    folded: str | None = None
    error: str | None = None

    @property
    def punctuated(self) -> bool:
        """Does this carrier end in the character the fold strips?

        The whole population split. A template that never carried the mark
        cannot lose anything to a rule that removes it, so those rows are the
        control and these are the ones the gate is about.
        """
        return self.ask.rstrip().endswith("?")

    @property
    def hatched(self) -> bool:
        return any(c.get("author") == "runtime" for c in self.calls)

    @property
    def model_calls(self) -> list[dict]:
        return [c for c in self.calls if c.get("author", "model") != "runtime"]

    @property
    def called(self) -> str | None:
        """`surfacegrid.Turn.called`'s rule -- a malformed grab is not no-call."""
        if not self.model_calls:
            return None
        return self.model_calls[0].get("name") or "<malformed>"

    @property
    def routed(self) -> bool:
        return not self.hatched and self.called == self.gold


def run_turn(client: Client, turn: Turn) -> Turn:
    """One utterance from a cleared history -- `surfacegrid.run_turn`'s reset.

    The `fold` event is recorded rather than ignored: on the after arm it is
    the runtime saying which turns it actually changed, which is the check that
    the flag under test was on for the turns it was supposed to be on for.
    """
    for _ in client.request(op="reset"):
        pass
    for ev in client.request(op="turn", user=turn.ask):
        kind = ev.get("t")
        if kind == "call":
            turn.calls.append(ev)
        elif kind == "fold":
            turn.folded = ev.get("folded")
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
    hit: int = 0
    n: int = 0
    hatched: int = 0

    def add(self, turn: Turn) -> None:
        if turn.hatched:
            self.hatched += 1
            return
        self.n += 1
        self.hit += turn.routed


def tally(turns: list[Turn]) -> dict[tuple[str, bool], Cell]:
    out: dict[tuple[str, bool], Cell] = {}
    for t in turns:
        out.setdefault((t.family, t.punctuated), Cell()).add(t)
    return out


def _fmt(c: "Cell | None") -> str:
    if c is None:
        return "--"
    if not c.n:
        return f"[{c.hatched} hatched]"
    return f"{c.hit}/{c.n}" + (f" +{c.hatched}h" if c.hatched else "")


def report(turns: list[Turn], info: dict) -> dict:
    cells = tally(turns)
    labels = list(dict.fromkeys(t.family for t in turns))
    arm = "fold" if info.get("fold") else "no-fold"

    print()
    print("  routed to gold, by family x whether the carrier ends in the mark")
    print(f"  arm: {arm}   (a hatched turn measures the hatch and is counted "
          f"apart, '+Nh')")
    print()
    print(f"    {'':<14} {'bare':>16} {'punctuated':>16}")
    for fam in labels:
        print(f"    {fam:<14} {_fmt(cells.get((fam, False))):>16} "
              f"{_fmt(cells.get((fam, True))):>16}")

    hatched = [t for t in turns if t.hatched]
    folded = [t for t in turns if t.folded is not None]
    print()
    print(f"  {len(hatched)}/{len(turns)} turns answered by the runtime hatch")
    print(f"  {len(folded)}/{len(turns)} turns the fold changed"
          + ("" if arm == "fold" else "  (0 expected on this arm)"))

    return {
        "harness": "foldgate/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": revision(),
        "arm": arm,
        "anchor": GATE_ANCHOR.isoformat(),
        "seed": GATE_SEED,
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
            "grammar": info.get("grammar"),
            "fold": info.get("fold"),
        },
        "instance": info,
        "families": {
            f.label: {"provenance": f.provenance, "gold": f.gold,
                      "n": len(f.carriers)}
            for f in families()
        },
        "by_family_punctuation": {
            f"{fam}|{'mark' if p else 'bare'}": [c.hit, c.n, c.hatched]
            for (fam, p), c in cells.items()
        },
        "hatched": len(hatched),
        "folded": len(folded),
        "turns": [
            {"family": t.family, "gold": t.gold, "ask": t.ask,
             "punctuated": t.punctuated, "folded": t.folded,
             "called": t.called, "hatched": t.hatched,
             "arguments": (t.model_calls[0].get("arguments")
                           if t.model_calls else None),
             "routed": None if t.hatched else t.routed,
             "reply": t.reply.strip(), "error": t.error}
            for t in turns
        ],
    }


# ===========================================================================
# the comparison, which is the whole point of running it twice
# ===========================================================================

def verdict(before: dict, after: dict) -> list[str]:
    """Every way this pair fails the gate, as lines. Empty means clean.

    **The condition is a loss rather than a threshold.** The strip half ships
    if the punctuated `resolve_date` carriers that reach the weights do not
    route *worse* under the fold. Equal is a pass -- the fold's job on this
    family is to cost nothing, and any gain belongs to `surfacegrid`'s families
    rather than to this one. A drop of any size is a stop-and-report, because
    the population is small and a small absolute loss here is a large fraction
    of a behaviour the corpus spent 2.27M rows on.

    A moved hatch count or a moved denominator fails too, and fails first: the
    hatches normalise for themselves and are strictly stronger than the fold,
    so a hatch that decided different turns in the two arms means they are not
    the same machine and the routing column cannot be read at all.

    Pure, so `scripts/check_foldgate.py` drives it over fixtures rather than
    over the day's cards.
    """
    out: list[str] = []
    for k in sorted(set(before["by_family_punctuation"])
                    | set(after["by_family_punctuation"])):
        b = before["by_family_punctuation"].get(k)
        a = after["by_family_punctuation"].get(k)
        if b is None or a is None:
            out.append(f"{k}: present in one arm only")
            continue
        (bh, bn, bx), (ah, an, ax) = b, a
        if bx != ax:
            out.append(f"{k}: hatch {bx} -> {ax}")
        elif bn != an:
            out.append(f"{k}: n {bn} -> {an}")
        elif ah < bh:
            out.append(f"{k}: routed {bh}/{bn} -> {ah}/{an}")
    return out


def compare(before: dict, after: dict) -> int:
    """Print the before/after table and return the shell's verdict."""
    failures = verdict(before, after)
    print(f"  before: {before['arm']}   after: {after['arm']}")
    print()
    print(f"    {'cell':<26} {'before':>12} {'after':>12}   verdict")
    for k in sorted(set(before["by_family_punctuation"])
                    | set(after["by_family_punctuation"])):
        b = before["by_family_punctuation"].get(k)
        a = after["by_family_punctuation"].get(k)
        if b is None or a is None:
            print(f"    {k:<26} {'--' if b is None else 'present':>12} "
                  f"{'--' if a is None else 'present':>12}   !! ONE ARM ONLY")
            continue
        (bh, bn, bx), (ah, an, ax) = b, a
        if bx != ax:
            note = "!! HATCH MOVED"
        elif bn != an:
            note = "!! DENOMINATOR MOVED"
        elif ah < bh:
            note = "!! LOST ROUTING"
        elif ah > bh:
            note = "gained"
        else:
            note = "unchanged"
        print(f"    {k:<26} {f'{bh}/{bn}':>12} {f'{ah}/{an}':>12}   {note}")

    print()
    if failures:
        print("  GATE FAILS -- the strip half does not ship on this read:")
        for line in failures:
            print(f"    {line}")
        print("  This is how the 2026-08-30 cards read, and it is why the "
              "terminal-mark strip was retired.")
        print("  If a NEW fold produced this, it is a stop-and-report: the "
              "owner decides the shape, not this file.")
        return 1
    print("  GATE CLEAN -- no punctuated temporal carrier lost routing, and "
          "the hatch decided the same turns in both arms.")
    print("  (The shipped fold is casefold-only and is the identity on every "
          "carrier here, so a same-runtime pair reads clean by construction.)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="the fold's temporal before/after -- owner decision 1b/0")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--json", help="write the scorecard here")
    ap.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"),
                    help="read two cards and print the gate's verdict; "
                         "runs nothing and needs no server")
    args = ap.parse_args()

    if args.compare:
        with open(args.compare[0], encoding="utf-8") as fh:
            before = json.load(fh)
        with open(args.compare[1], encoding="utf-8") as fh:
            after = json.load(fh)
        return compare(before, after)

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

    print(f"foldgate against {info.get('ckpt')}")
    print(f"  fold {info.get('fold')}   temperature {info.get('temperature')}"
          f"   speech {info.get('speech_temperature')}   "
          f"multi {info.get('multi')}   search {info.get('search')}")
    print(f"  notes -> {info.get('notes')}   reach {info.get('reach')}")
    if info.get("fold") is None:
        print("\nthis server predates the fold and reports no `fold` in "
              "`info` -- the arm cannot be named, so the card would be "
              "unreadable.", file=sys.stderr)
        client.close()
        return 2

    planned = build()
    print(f"  {len(planned)} turns planned")

    started = time.perf_counter()
    done: list[Turn] = []
    for i, turn in enumerate(planned, 1):
        run_turn(client, turn)
        if turn.error:
            print(f"turn raised: {turn.ask!r} -- {turn.error}", file=sys.stderr)
            return 2
        done.append(turn)
        if i % 25 == 0:
            print(f"    {i}/{len(planned)} ...")

    card = report(done, info)
    card["seconds"] = round(time.perf_counter() - started, 1)
    print(f"\n  {len(done)} turns in {card['seconds']}s")
    client.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
