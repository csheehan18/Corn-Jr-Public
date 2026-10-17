"""Scripted conversations against a running instance. Does the second turn work?

**The question `harness/checkup.py` cannot ask.** That file sends twenty
unrelated sentences and scores each one on its own, which is the right shape for
"does the assembled thing work" and the wrong shape for the only question left:
a conversation is turns that know about each other, and every instrument in this
project so far has measured turns that do not. `evals/` scores single prompts
against gold strings; `checkup` scores single turns against live tools; nothing
scores turn 3.

**What the corpus actually contains, counted rather than assumed.** Over
`data/mix_v3_5b` -- the mix `corn_jr_260m` was trained on -- exactly one slice
carries a second `<|user|>`: `temporal_sayvar.txt`'s daycross follow-up, 1,720
transcripts of 25,118, which is 6.85% of that slice and ~0.34% of the mix. Of
those 1,720 second turns the marker that follows is `<|call|>` in **1,720** and
`<|say|>` in **0**, and no other slice has a second `<|user|>` at all.

So the multi-turn *shape* is trained, thinly, and the multi-turn *conversation*
is not trained at all. Those are different claims and this file is built to keep
them apart:

    trained=True    the daycross shape, near enough. If this class fails, the
                    finding is about the runtime -- the context it assembled, or
                    the trimming -- because the model has seen this.
    trained=False   everything else. If these fail and the control passes, the
                    finding is about the corpus, and the fix is a slice rather
                    than a patch.

A run without the control is unreadable, which is why it is not optional.

**Rows, and why these four.**

    in_kind         the turn got the *class* of answer it asked for -- a call
                    where a call was wanted, silence from the tools where it was
                    not. This is the row the whole file exists for: the corpus
                    says a second `<|user|>` means "call", so the predicted
                    failure is a chatty follow-up answered with a tool call
    said_something  he replied at all. A turn that produces an empty string is a
                    dead conversation whatever else it got right, and off
                    distribution that is a real outcome rather than a crash
    fresh           this reply is not the last one again. Repetition is the
                    named failure mode of a context the model has not seen, and
                    a rate that only counted correctness would score a model
                    stuck in a loop as passing every row it happened to repeat
    carried_over    the turn used something only an *earlier* turn supplied --
                    the day in "Saturday", the correction in "make that under
                    the mat". This is the row that separates a conversation from
                    a list of sentences, and it is scored on the call arguments
                    and the reply together because either is a legitimate place
                    for the referent to land

**Reported by turn position, because that is the shape of the answer.** A rate
pooled over all turns would hide the only thing worth knowing -- whether turn 1
holds and turn 3 collapses, or whether it degrades evenly. The per-position
table is the headline and the pooled row is the footnote.

**A rate, not a gate.** Same contract as `checkup`: this exits 0 on a poor
result and non-zero only on something structural -- no server, a turn that
raised, or an instance with `--multi` off, which would make every number here a
measurement of something else.

**It executes real tools, so it disturbs real state.** `save_note` writes. No
script here calls `place_call` or `send_text`, deliberately: those are gated, and
`harness/backends/confirm.py` answers the *next* utterance from the runtime
without consulting the model -- which is correct behaviour and would silently
turn a scripted second turn into a measurement of the gate. Point the server at
a scratch `--notes` path.

One honest gap in the control. The daycross transcripts all carry a `<|day|>`
header and `harness/server.py` does not send one, so the trained class is
reproduced here minus the header. `corn/agent.py` explains why the header is not
on by default -- it is a vote for `resolve_date` before the user has spoken --
and turning it on to make the control easier would be scoring the header.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m/ckpt.pt --multi --notes /tmp/converse.jsonl
    python -m harness.converse
    python -m harness.converse --json results/converse.json
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import line as provenance_line
from .provenance import revision

TALK, CALL = "talk", "call"


@dataclass(frozen=True)
class Beat:
    """One user utterance inside a conversation, and what it asks for."""
    say: str
    # TALK: no tool covers this, and reaching for one is the failure.
    # CALL: a tool does, named by `expect` when the choice is not in doubt.
    mode: str
    expect: str | None = None
    # Substrings that must turn up in the call arguments or in the reply,
    # case-insensitively. Only ever set on a beat whose meaning *depends* on an
    # earlier turn -- a referent the utterance alone does not contain. A beat
    # that could be answered on its own leaves this empty, because scoring it
    # there would be scoring comprehension rather than memory.
    carries: tuple[str, ...] = ()


@dataclass(frozen=True)
class Script:
    name: str
    beats: tuple[Beat, ...]
    # Whether the corpus contains this class at turn 2. See the module
    # docstring: exactly one class is True, and it is the control.
    trained: bool
    why: str = ""


SCRIPTS: tuple[Script, ...] = (
    # ---- the control. The one multi-turn shape in the corpus ---------------
    # A range that cannot resolve, the tool's own clarifying question, and an
    # answer to it. `corn/temporal.py:1254` writes this transcript 1,720 times
    # and every one of them answers the second turn with a call.
    Script(
        "daycross", trained=True,
        why="temporal_sayvar.txt, 1,720 transcripts",
        beats=(
            Beat("what did I get up to at the weekend", CALL, "resolve_date"),
            Beat("Saturday", CALL, "resolve_date", carries=("saturday",)),
        ),
    ),
    # ---- and the classes with no instances anywhere -------------------------
    # Pure conversation. The most ordinary thing a person does and the one the
    # marked-up corpus has never once shown him past turn 1.
    Script(
        "talk", trained=False,
        why="no slice has a second <|user|> answered by <|say|>",
        beats=(
            Beat("morning", TALK),
            Beat("not much, just got up. you?", TALK),
            Beat("same here, bit of a slow start", TALK),
            Beat("anyway, good to catch up", TALK),
        ),
    ),
    # A tool, then talk about it. The class the count above puts at zero: every
    # trained second turn calls, so an acknowledgement is the hardest easy
    # sentence in the suite.
    Script(
        "tool_then_talk", trained=False,
        why="0 of 1,720 trained second turns answer without calling",
        beats=(
            Beat("note down buy milk and coffee", CALL, "save_note"),
            Beat("thanks", TALK),
            Beat("that's all I needed", TALK),
        ),
    ),
    # The other order. Turn 1 sets no tool precedent, so this separates "a
    # second turn always calls" from "a turn after a call always calls".
    Script(
        "talk_then_tool", trained=False,
        why="a call at turn 2 after a turn that did not call",
        beats=(
            Beat("morning, how are you", TALK),
            Beat("note down the bins go out tonight", CALL, "save_note"),
            Beat("great, thanks", TALK),
        ),
    ),
    # A correction that only makes sense against the previous turn. `carried_
    # over` is the row: "under the mat" is nowhere in the utterance he is
    # answering except as a change to one he has already answered.
    Script(
        "correction", trained=False,
        why="the referent is in turn 1 and nowhere else",
        beats=(
            Beat("note down the spare key is under the pot", CALL, "save_note"),
            Beat("actually make that under the mat", CALL, "save_note",
                 carries=("mat",)),
        ),
    ),
    # An elliptical follow-up: three words that mean nothing on their own. The
    # cheapest possible test that the earlier turn is in the context at all.
    Script(
        "ellipsis", trained=False,
        why="'and tomorrow' is not a request without turn 1",
        beats=(
            Beat("what day is it today", CALL, "resolve_date"),
            Beat("and what about tomorrow", CALL, "resolve_date",
                 carries=("tomorrow",)),
        ),
    ),
)

ROWS = ("in_kind", "said_something", "fresh", "carried_over")


def norm(text: str) -> str:
    return " ".join(text.split()).strip().lower()


@dataclass
class Turn:
    """One beat, run."""
    script: Script
    beat: Beat
    position: int          # 1-based, within the script
    calls: list[dict] = field(default_factory=list)
    obs: list[dict] = field(default_factory=list)
    reply: str = ""
    ms: float = 0.0
    ttft: float | None = None
    error: str | None = None
    # The reply to the beat before this one, for `fresh`. Carried on the turn
    # rather than looked up during scoring so that `rows()` stays a pure
    # function of one record -- which is what makes it guardable without a
    # server, the same argument `check_checkup.py` makes.
    previous: str | None = None
    # Set when the confirmation gate answered instead of the model. No script
    # here should ever trip it; if one does, the row it produced is about the
    # runtime and the report says so rather than quietly counting it.
    gated: bool = False

    @property
    def called(self) -> str | None:
        """The tool he reached for. A malformed call is a reach, not a silence."""
        if not self.calls:
            return None
        return self.calls[0]["name"] or "<malformed>"

    @property
    def said(self) -> str:
        """Everything he put in front of the user this turn: the reply, and the
        arguments of any call, which is where a referent legitimately lands."""
        args = " ".join(json.dumps(c.get("arguments") or {}) for c in self.calls)
        return f"{args} {self.reply}"

    def rows(self) -> dict[str, bool | None]:
        """Per-turn verdicts. `None` means the row does not apply here."""
        if self.beat.mode == TALK:
            in_kind = not self.calls
        elif self.beat.expect is None:
            in_kind = bool(self.calls)
        else:
            in_kind = self.called == self.beat.expect
        return {
            "in_kind": in_kind,
            "said_something": bool(self.reply.strip()),
            # Inapplicable at position 1: there is nothing to have repeated.
            "fresh": (None if self.previous is None
                      else norm(self.reply) != norm(self.previous)),
            "carried_over": (None if not self.beat.carries else
                             all(w in self.said.lower()
                                 for w in self.beat.carries)),
        }


def run_script(client: Client, script: Script) -> list[Turn]:
    """One conversation, from a cleared history.

    The reset is not politeness. History lives on the *session* rather than the
    connection (see `harness/server.py`), so a second script run without it
    would open on the tail of the first -- and every number below would be
    measuring a conversation nobody scripted.
    """
    for _ in client.request(op="reset"):
        pass
    turns: list[Turn] = []
    previous: str | None = None
    for i, beat in enumerate(script.beats, start=1):
        turn = Turn(script=script, beat=beat, position=i, previous=previous)
        sent = time.perf_counter()
        for ev in client.request(op="turn", user=beat.say):
            kind = ev.get("t")
            if kind == "text":
                if turn.ttft is None:
                    turn.ttft = (time.perf_counter() - sent) * 1000
            elif kind == "say":
                turn.reply = ev["text"]
            elif kind == "call":
                turn.calls.append(ev)
            elif kind == "obs":
                turn.obs.append(ev["payload"])
            elif kind == "error":
                turn.error = ev.get("why", "?")
            elif kind == "done":
                turn.ms = ev.get("ms", 0.0)
                turn.gated = "outcome" in ev
        turns.append(turn)
        previous = turn.reply
    return turns


def tally(turns: list[Turn]) -> dict[str, list[int]]:
    out = {r: [0, 0] for r in ROWS}
    for t in turns:
        for r, v in t.rows().items():
            if v is None:
                continue
            out[r][1] += 1
            out[r][0] += bool(v)
    return out


def rate(pair: list[int]) -> str:
    hit, n = pair
    return "   --  " if not n else f"{hit:>2}/{n:<2} {100 * hit / n:3.0f}%"


def report(turns: list[Turn], info: dict) -> dict:
    print()
    print("conversations")
    for script in SCRIPTS:
        mine = [t for t in turns if t.script is script]
        if not mine:
            continue
        mark = "control" if script.trained else "untrained"
        print(f"\n  {script.name}  [{mark}] -- {script.why}")
        for t in mine:
            v = t.rows()
            bad = [r for r, x in v.items() if x is False]
            state = "ok  " if not bad else "MISS"
            got = t.called or "-"
            want = t.beat.expect or ("-" if t.beat.mode == TALK else "any")
            arrow = f"{want} -> {got}" if got != want else got
            print(f"    {state} {t.position}. {t.ms:6.0f}ms  {arrow:<26} "
                  f"{t.beat.say[:40]}")
            said = t.reply.strip()
            print(f"           said {said[:72]!r}" if said else
                  "           said nothing")
            if bad:
                print(f"           {', '.join(bad)}"
                      + (" | answered by the gate, not the model" if t.gated else "")
                      + (f" | {t.error}" if t.error else ""))

    # ---- the headline. Position, not pooled ------------------------------
    depth = max((t.position for t in turns), default=0)
    print()
    print("by turn position -- the row this file exists for")
    header = "".join(f"  turn {i:<8}" for i in range(1, depth + 1))
    print(f"  {'':<16}{header}")
    for r in ROWS:
        cells = ""
        for i in range(1, depth + 1):
            cells += f"  {rate(tally([t for t in turns if t.position == i])[r]):<11}"
        print(f"  {r:<16}{cells}")

    print()
    print("by class -- the control says whether a miss is the corpus or the runtime")
    for script in SCRIPTS:
        mine = [t for t in turns if t.script is script]
        if not mine:
            continue
        counts = tally(mine)
        mark = "control  " if script.trained else "untrained"
        cells = "".join(f"  {r}={rate(counts[r])}" for r in ("in_kind", "fresh"))
        print(f"  {script.name:<16} {mark}{cells}")

    print()
    print("pooled")
    pooled = tally(turns)
    for r in ROWS:
        print(f"  {r:<16} {rate(pooled[r])}")

    # ---- latency, which is a different question at turn 4 than at turn 1 ---
    print()
    print("latency by position -- context grows every turn and decode is "
          "bandwidth-bound")
    for i in range(1, depth + 1):
        at = [t.ms for t in turns if t.position == i]
        if at:
            print(f"  turn {i}   median {statistics.median(at):6.0f}ms   "
                  f"max {max(at):6.0f}ms   ({len(at)} turns)")

    gated = [t for t in turns if t.gated]
    if gated:
        print(f"\n  !! {len(gated)} turn(s) were answered by the confirmation "
              f"gate rather than the model -- those rows measure the runtime")

    return {
        "harness": "converse/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        # See `checkup.report` -- the scripts are in this file, so the revision
        # is the only thing that says which scripts a card was written from.
        "source": revision(),
        "instance": info,
        "pooled": {r: {"hit": pooled[r][0], "n": pooled[r][1]} for r in ROWS},
        "by_position": {
            str(i): {r: {"hit": tally([t for t in turns if t.position == i])[r][0],
                         "n": tally([t for t in turns if t.position == i])[r][1]}
                     for r in ROWS}
            for i in range(1, depth + 1)
        },
        "by_script": {
            s.name: {"trained": s.trained,
                     **{r: {"hit": tally([t for t in turns if t.script is s])[r][0],
                            "n": tally([t for t in turns if t.script is s])[r][1]}
                        for r in ROWS}}
            for s in SCRIPTS if any(t.script is s for t in turns)
        },
        "turns": [
            {"script": t.script.name, "position": t.position, "say": t.beat.say,
             "mode": t.beat.mode, "expect": t.beat.expect, "called": t.called,
             "reply": t.reply.strip(), "ms": t.ms, "gated": t.gated,
             "rows": t.rows(), "error": t.error}
            for t in turns
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--json", help="write the scorecard here")
    ap.add_argument("--only", help="run one script by name")
    args = ap.parse_args()

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- start it with "
              f"`python -m harness.server --multi`", file=sys.stderr)
        return 1

    info = {}
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            info = {k: v for k, v in ev.items() if k not in ("t", "id")}

    print(f"instance   {info.get('ckpt')} -- {info.get('params', 0):,} params, "
          f"{info.get('tokenizer')}")
    print(f"wiring     notes -> {info.get('notes')} | search {info.get('search')} "
          f"| temperature {info.get('temperature')} | multi {info.get('multi')}")
    print(provenance_line())
    if not info.get("multi"):
        # Structural, not a poor result. Without history every script here is
        # six unrelated sentences and every row would be a measurement of
        # something nobody asked about.
        print("\nthis server is not carrying history -- restart it with --multi.\n"
              "Without it there is no second turn to score.", file=sys.stderr)
        client.close()
        return 1
    if info.get("temperature"):
        print("           !! temperature is not 0 -- this run is not reproducible")
    print("           !! real tools run: notes are written")

    turns: list[Turn] = []
    for script in SCRIPTS:
        if args.only and script.name != args.only:
            continue
        turns.extend(run_script(client, script))

    if not turns:
        print(f"no script named {args.only!r}", file=sys.stderr)
        client.close()
        return 1

    card = report(turns, info)
    client.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"\nwrote {args.json}")

    broke = [t for t in turns if t.error]
    if broke:
        print(f"\n{len(broke)} turn(s) errored -- the run is incomplete")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
