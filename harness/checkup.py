"""Real turns against a running instance. Does the assembled thing work?

**The question no other instrument in this project asks.** `evals/` scores the
model against gold strings with the tools stubbed out. `scripts/check_agent.py`
tests executors with no model. `scripts/check_server.py` tests the socket with
no agent. Each is right about its own half, and none of them can tell you
whether Corn-Jr, wired to a live search and a real note store, answers a
question you would actually ask him. That gap did not matter much while every
tool read from a table. It matters now.

**This is a scorecard, not a guard, and the distinction is deliberate.** The
`check_*.py` files assert invariants and go red when something is broken. What
happens when a 260M model meets twenty real sentences is *behaviour*: it will
be imperfect, the number will move between checkpoints, and a pass/fail gate
would sit red forever and then be ignored. So this reports rates and exits 0.
It fails only on something structural -- no server, a malformed event, a turn
that raised -- because those mean the measurement did not happen at all, which
is different from measuring a poor result.

**The rows are named to be incomparable with `evals/` on purpose.** `routed`
is not `tool.selection`; `spoke_from_tool` is not `tool.copy`. Different items,
no gold answers, live tools, a different tool arity. Giving them the eval names
would invite one number to be quoted against the other, and the project has
already learned that lesson once, from a six-way choice becoming an eight-way
one. Four rows:

    routed          he reached for the tool the case expected -- or, where the
                    case expects none, reached for nothing. One chain is
                    sanctioned: a recall case answered resolve_date then
                    recall_day is routed, because that is the temporal
                    hatch's own path to the day log; see `Outcome.rows`
    executed        the call he wrote was schema-valid and actually ran
    spoke_from_tool the reply carries the tool's own words, where the tool
                    supplied words to carry. Deference, measured live: the
                    payload is right there next to the sentence, which is the
                    one thing a runtime can check that a scorer with a gold
                    answer cannot
    held_back       on a request no tool covers, he did not invent one

**Calls and texts reach only the owner** (2026-10-13, PLAN-PEOPLE §7), so the
contact cases are "call me", "text me ..." and one third party, whose right
answer is the runtime's refusal with the offer, spoken -- `spoke_from_tool`
reads it. The `named_right` row went with the contact book: there is no book
for a name to be swapped into, and the refusal names whoever the slot named.

**The suite scores against the *declared* registry, not the trained one, and
a checkpoint can be older than a tool.** `info` reports the eight tools the
runtime offers; what a given checkpoint's corpus actually contained is not
knowable from here. So a model trained before `ask_agent` existed will miss
those rows for a reason that is not a fault -- it is being asked for something
it was never shown. The thirty-fourth finding says that is not hopeless, since
he routes to *declared* tools he was never trained on at close to parity with
trained ones; but a `routed` rate is only comparable across checkpoints that
saw the same tool set, and this is the paragraph to point at when it is not.

**It executes real tools, so it disturbs real state.** `save_note` writes;
`ask_agent` queues; `web_search` may leave the machine. The server reports its
own wiring through `info` and this prints it before the first turn, because a
harness that silently appended twenty test notes to somebody's actual note
store would be a bad neighbour. Point the server at a scratch `--notes` path.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m/ckpt.pt --notes /tmp/checkup.jsonl
    python -m harness.checkup
    python -m harness.checkup --json results/checkup.json
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import line as provenance_line
from .provenance import revision


@dataclass(frozen=True)
class Case:
    ask: str
    # The tool this request wants, or None for "no tool covers this".
    expect: str | None
    # A payload key that must be present when the call runs. Not a value check:
    # the value depends on live state -- what the internet said, what is in the
    # note store -- and asserting on it would make this a test of the world.
    wants: str | None = None
    # Cases that reach the network. Skipped when the server reports its search
    # backend as `table`, because a table-backed instance cannot pass them and
    # a row it cannot pass is noise rather than a finding.
    needs_search: bool = False


# Twenty turns, weighted the way a day is rather than the way a tool list is.
# Notes and lookups are what a personal assistant is actually asked for; the
# out-of-scope rows are here because §9's most important behaviour is knowing
# when he does not know, and a suite where every request succeeds cannot see it.
CASES: tuple[Case, ...] = (
    # --- the easy one. If this fails, nothing below is worth reading. -------
    Case("note down buy milk and coffee", "save_note", "status"),
    Case("make a note that the boiler pressure should be 1.5", "save_note", "status"),
    Case("jot down the spare key is under the pot", "save_note", "status"),
    # --- dates: the canary. §6 says if he ever *reasons* about a date -------
    # instead of calling this, something is wrong upstream.
    Case("what day is it today", "resolve_date", None),
    Case("what was last Wednesday", "resolve_date", None),
    Case("what date is a week on Friday", "resolve_date", None),
    # --- the day log, which reads back what save_note wrote -----------------
    Case("what did I note down today", "recall_day", None),
    Case("what was I doing on the 14th", "recall_day", None),
    # --- lookups, live ------------------------------------------------------
    Case("look up Ada Lovelace", "web_search", None, needs_search=True),
    Case("what's the boiling point of water", "web_search", None, needs_search=True),
    Case("can you look up the Eiffel Tower", "web_search", None, needs_search=True),
    # --- escalation, the tool with no backend yet: it queues -----------------
    Case("ask Claude how to stop a laptop fan running constantly", "ask_agent", "status"),
    Case("get Qwen to draft a polite email turning down a meeting",
         "ask_agent", "status"),
    # A generic carrier as well as two vendors: an instance pointed at a model
    # on its owner's own hardware is the case `AGENT_NAMES` exists for, and it
    # is the one a checkup would otherwise never exercise.
    Case("ask the AI what the going rate is for a plasterer per day",
         "ask_agent", "status"),
    # --- calls and texts: only ever the owner ------------------------------
    Case("call me", "place_call", "status"),
    Case("text me pick up the parcel", "send_text", "status"),
    # Anyone else is the runtime's refusal with the offer, and the row that
    # matters is `spoke_from_tool`: he says the refusal as written.
    Case("call Ophelia Vance", "place_call", "say"),
    # --- and the half that must NOT call ------------------------------------
    Case("turn the heating up", None),
    Case("play some music", None),
    Case("order me a taxi", None),
    # Ordinary conversation, which is the case the runtime meets constantly
    # and the frozen eval set has none of -- every one of its 19 abstention
    # items asks for a capability instead.
    Case("morning", None),
    Case("thanks, that's great", None),
)

STOP = set("the a an is are was were to of in on at for and or my your it its "
           "be been i that this what how why when do does did can could would "
           "you me we so if not no but".split())


def content(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", text.lower()) if w not in STOP}


def spoken_source(payload: dict) -> str | None:
    """The words the tool supplied for the model to say, if it supplied any.

    `say` and `clarify` are phrasings the tool composed -- §6 puts ambiguity
    and refusal wording in code rather than in 250M parameters -- and `answer`
    is the field the tenth finding shaped `web_search` around. A payload with
    none of the three (`save_note`'s `{"status": "saved", "chars": 9}`) imposes
    no copy obligation, and this row correctly does not apply to it.
    """
    for key in ("say", "clarify", "answer"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            return v
    return None


def carried(source: str, reply: str, threshold: float = 0.7) -> bool:
    """Did the reply carry the tool's words?

    Normalised containment first, because an exact read-back is the trained
    behaviour and the common case. The overlap fallback exists because a model
    that says "It's Wednesday the 14th" off a payload saying "Wednesday 14
    August" has deferred, and a substring test would call that a failure.

    Cruder than `corn/evals.py`'s `score_tool_copy`, and deliberately not the
    same function: that one compares against a *gold* answer known in advance,
    this one against whatever the tool actually returned a moment ago. Two
    different questions, so two implementations is right here rather than the
    duplication it would be anywhere else.
    """
    a, b = " ".join(source.split()).lower(), " ".join(reply.split()).lower()
    if a and a in b:
        return True
    want = content(source)
    if not want:
        return False
    return len(want & content(reply)) / len(want) >= threshold


@dataclass
class Outcome:
    case: Case
    ask: str
    calls: list[dict] = field(default_factory=list)
    obs: list[dict] = field(default_factory=list)
    reply: str = ""
    ms: float = 0.0
    ttft: float | None = None
    error: str | None = None

    @property
    def called(self) -> str | None:
        """The tool he reached for, or None if he reached for nothing.

        A call the validator could not name is **not** None: he did reach for a
        tool, he just wrote it unreadably, and collapsing that into "no call"
        would score a malformed grab at `send_text` as successful restraint.
        """
        if not self.calls:
            return None
        return self.calls[0]["name"] or "<malformed>"

    def rows(self) -> dict[str, bool | None]:
        """Per-case verdicts. `None` means the row does not apply to this case."""
        want = self.case.expect
        if want is None:
            return {"routed": not self.calls, "executed": None,
                    "spoke_from_tool": None, "held_back": not self.calls}
        routed = self.called == want
        if not routed and want == "recall_day":
            # **The temporal hatch resolves the date before it reads the
            # day, and the chain is the routing, not a detour from it.**
            # "what did I note down today" runs `resolve_date("today")` and
            # then `recall_day` on what came back; scoring that by first
            # call alone read a correct turn as a MISS on 2026-08-26. Only
            # this exact chain is sanctioned -- a turn that wandered through
            # `web_search` before landing on `recall_day` still fails,
            # because reaching the right tool by accident is what this row
            # exists to catch.
            names = [c["name"] for c in self.calls]
            routed = ("recall_day" in names
                      and all(n == "resolve_date"
                              for n in names[:names.index("recall_day")]))
        executed = bool(self.obs) and any(c.get("ok") for c in self.calls)
        if self.case.wants and self.obs:
            executed = executed and self.case.wants in self.obs[-1]
        source = spoken_source(self.obs[-1]) if self.obs else None
        return {
            "routed": routed,
            "executed": executed,
            "spoke_from_tool": carried(source, self.reply) if source else None,
            "held_back": None,
        }


def run_case(client: Client, case: Case) -> Outcome:
    """One case, from a cleared history.

    **The reset is what makes these cases independent, and without it they are
    not.** History lives on the *session* rather than the connection (see
    `harness/server.py`), so against a `--multi` instance every case after the
    first opened on the tail of the one before -- twenty unrelated sentences
    stacked into one conversation, scored as though each stood alone. The rows
    would still print. They would be measuring a twenty-turn context nobody
    wrote, and `routed` would fall for a reason that has nothing to do with
    routing.

    Harmless against a single-turn instance, where the history is empty
    anyway, which is why this is unconditional rather than gated on `info`.
    Conversations are `harness/converse.py`'s subject, and it resets per
    script for the same reason.
    """
    for _ in client.request(op="reset"):
        pass
    ask = case.ask
    out = Outcome(case=case, ask=ask)
    sent = time.perf_counter()
    for ev in client.request(op="turn", user=ask):
        kind = ev.get("t")
        if kind == "text":
            if out.ttft is None:
                out.ttft = (time.perf_counter() - sent) * 1000
        elif kind == "say":
            out.reply = ev["text"]
        elif kind == "call":
            out.calls.append(ev)
        elif kind == "obs":
            out.obs.append(ev["payload"])
        elif kind == "error":
            out.error = ev.get("why", "?")
        elif kind == "done":
            out.ms = ev.get("ms", 0.0)
    return out


def report(outcomes: list[Outcome], info: dict, skipped: list[tuple[Case, str]]):
    rows = ("routed", "executed", "spoke_from_tool", "held_back")
    tally = {r: [0, 0] for r in rows}
    for o in outcomes:
        for r, v in o.rows().items():
            if v is None:
                continue
            tally[r][1] += 1
            tally[r][0] += bool(v)

    print()
    print("turns")
    for o in outcomes:
        v = o.rows()
        bad = [r for r, x in v.items() if x is False]
        mark = "ok  " if not bad else "MISS"
        got = o.called or "-"
        want = o.case.expect or "-"
        arrow = f"{want} -> {got}" if got != want else got
        print(f"  {mark}  {o.ms:6.0f}ms  {arrow:<28} {o.ask[:44]}")
        if bad:
            print(f"          {', '.join(bad)}"
                  + (f" | said {o.reply.strip()[:60]!r}" if o.reply.strip() else "")
                  + (f" | {o.error}" if o.error else ""))

    print()
    print("rows")
    for r in rows:
        hit, n = tally[r]
        if not n:
            print(f"  {r:<16} -- no case applies")
            continue
        print(f"  {r:<16} {hit:>3}/{n:<3} {100 * hit / n:5.1f}%")

    ms = sorted(o.ms for o in outcomes)
    ttfts = sorted(o.ttft for o in outcomes if o.ttft is not None)
    print()
    print("latency -- VISION §3 budgets the whole round trip at 500ms")
    if ms:
        p90 = ms[min(len(ms) - 1, int(0.9 * len(ms)))]
        print(f"  turn        median {statistics.median(ms):6.0f}ms   "
              f"p90 {p90:6.0f}ms   max {ms[-1]:6.0f}ms")
    if ttfts:
        p90 = ttfts[min(len(ttfts) - 1, int(0.9 * len(ttfts)))]
        print(f"  first token median {statistics.median(ttfts):6.0f}ms   "
              f"p90 {p90:6.0f}ms   max {ttfts[-1]:6.0f}ms")
    # Split because they are different budgets. A turn that calls a tool pays
    # for two rounds of decode plus whatever the tool cost; a turn that only
    # speaks is the floor, and the floor is the number §3's LLM slice is about.
    spoke = [o.ms for o in outcomes if not o.calls]
    tooled = [o.ms for o in outcomes if o.calls]
    if spoke and tooled:
        print(f"  speech only median {statistics.median(spoke):6.0f}ms "
              f"({len(spoke)} turns)   "
              f"with a tool {statistics.median(tooled):6.0f}ms ({len(tooled)})")

    for case, why in skipped:
        print(f"  skipped: {case.ask[:48]} -- {why}")

    return {
        "harness": "checkup/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        # Which tree the *harness* ran from, next to which instance it ran
        # against. `instance` already names every flag that changes what a row
        # means; this names the case list and the runtime behind them, which is
        # the half `harness/results/README.md` calls "a claim about the working
        # tree rather than about the files".
        "source": revision(),
        "instance": info,
        "rows": {r: {"hit": tally[r][0], "n": tally[r][1]} for r in rows},
        "latency_ms": {
            "turn_median": statistics.median(ms) if ms else None,
            "ttft_median": statistics.median(ttfts) if ttfts else None,
        },
        "turns": [
            {"ask": o.ask, "expect": o.case.expect, "called": o.called,
             "reply": o.reply.strip(), "ms": o.ms, "rows": o.rows(),
             "error": o.error}
            for o in outcomes
        ],
        "skipped": [{"ask": c.ask, "why": w} for c, w in skipped],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--json", help="write the scorecard here")
    args = ap.parse_args()

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- start it with "
              f"`python -m harness.server`", file=sys.stderr)
        return 1

    info = {}
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            info = {k: v for k, v in ev.items() if k not in ("t", "id")}

    print(f"instance   {info.get('ckpt')} -- {info.get('params', 0):,} params, "
          f"{info.get('tokenizer')}")
    print(f"wiring     notes -> {info.get('notes')} | search {info.get('search')} "
          f"| temperature {info.get('temperature')}")
    print(provenance_line())
    # Not a refusal, a warning: someone may deliberately want to see the spread
    # at temperature. But a scorecard nobody can reproduce should say so on its
    # own face rather than in a footnote nobody reads.
    if info.get("temperature"):
        print("           !! temperature is not 0 -- this run is not reproducible")
    print("           !! real tools run: notes are written, queries may leave "
          "the machine")

    skipped: list[tuple[Case, str]] = []
    outcomes: list[Outcome] = []
    for case in CASES:
        if case.needs_search and info.get("search") != "live":
            skipped.append((case, "server is table-backed; start it with --search"))
            continue
        outcomes.append(run_case(client, case))

    card = report(outcomes, info, skipped)
    client.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"\nwrote {args.json}")

    # Structural failure only. A poor rate is a result; a turn that never ran
    # is a measurement that did not happen, and those are not the same thing.
    broke = [o for o in outcomes if o.error]
    if broke:
        print(f"\n{len(broke)} turn(s) errored -- the run is incomplete")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
