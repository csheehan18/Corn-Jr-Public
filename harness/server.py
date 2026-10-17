"""The resident model. One process, weights in VRAM, turns over a socket.

**This is the piece every other client needs and none of them can supply.**
`corn/agent.py` and `corn/chat.py` both load a checkpoint, do one thing and
exit -- fine for a probe, impossible for a conversation: loading a 260M
checkpoint and compiling the decode path costs seconds to minutes against a
500ms round-trip budget (VISION §3), so the load has to happen once and outlive
every turn. Voice, desktop and phone are all thin clients in §4's design, and
all three of them are blocked on this one process existing.

**It owns the model; it does not reimplement the turn.** Everything about how a
turn actually runs -- arming the grammar, discarding what the model writes past
`<|call|>`, executing against the registry, splicing the real observation back
-- stays in `corn.agent.Agent`, which is the file with the findings behind it.
This module is a socket, a lock and an event pump. If a behaviour question ever
has two answers, one here and one there, the one here is the bug.

**One turn at a time, and the queue is honest about it.** The 3080 holds one
model and single-stream decode is memory-bandwidth-bound, so a second
concurrent turn is not served faster by being accepted -- it makes both slower
and hides it behind a queue. Requests serialise on one lock, and a client that
is waiting is told so rather than left guessing.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m/ckpt.pt
    python -m harness.server --ckpt checkpoints/nano20m_v1/ckpt.pt --port 8765
"""

from __future__ import annotations

import argparse
import asyncio
import time
from functools import partial
from datetime import date
from pathlib import Path

from corn.agent import Agent, World
from corn.persona import Marker
from corn.grammar import DEFAULT_COPY_SLOTS

from .protocol import MAX_LINE, decode, encode
from .sessionlog import SessionLog

# **The runtime set is `DEFAULT_COPY_SLOTS`, and the one slot it used to add is
# gone.** Until the seventy-eighth finding this read
#
#     RUNTIME_COPY_SLOTS = DEFAULT_COPY_SLOTS | {("web_search", "query")}
#
# on the argument that a query is a span of the utterance in every corpus call
# -- `corn/grammar.py`'s `SPAN_SLOTS` still records that, and it is still true
# of the corpus. What the finding measured is that neither half of the argument
# survives contact with a *conversation*.
#
# **The rescue it was added for does not reproduce on this base.** The failure
# it was written against was `corn_jr_260m` handed `look up Ada Lovelace`,
# routing correctly and then writing
#
#     {"query": "ada-lovelace-definition-definition-definition-definition-...
#
# until the budget ran out -- no closing brace, nothing executed, nothing said.
# Re-run on `corn_jr_260m_v4`, eleven degenerate phrasings including five bare
# proper names (Vercingetorix, Zbigniew Brzezinski), a colon syntax and two
# vocatives are **byte-identical armed and unarmed**. The slot never bit once.
# The run-on was a v3 behaviour and the v4 base does not have it.
#
# **And the cost it was measured to have none of is three chain follow-ups in
# four.** The old note above was right that a query he cuts himself is a span
# already -- on a *single* utterance. `corn/agent.py` binds the source to the
# whole conversation below the declaration, so on the second turn of a chain
# the stem is in the previous turn and the entity is in this one, and
# `span_ok` wants one contiguous run holding both. There isn't one. The mask
# bites at the join and greedy lands on the string that *is* a span: the
# previous query, sitting in the history.
#
#     what about Sweden?  ->  {"query": "the capital of Norway"}     armed
#                         ->  {"query": "the capital of Sweden"}   unarmed
#
# **0 of 4 armed, 3 of 4 unarmed** against a control differing by this slot
# alone (the fourth fails identically both ways and is the weights).
# Re-scoping the source to the current utterance was priced instead of this
# and does not recover the chain either -- the stem is not in the current
# utterance, so the composition stays illegal and the best legal query becomes
# the bare entity. Only removing the slot makes the composed query legal.
# `scripts/check_grammar.py` §9 carries both properties.
#
# **What still constrains a query.** The schema half of the grammar, which the
# same controls say is pure rescue: with `--no-grammar` the same turns produced
# `{"query": "the capital of Finland"` with no closing brace and a `<|say|>`
# spliced inside the call, both `not_json`, both executing nothing. Removing
# one copy slot is not turning the grammar off. Beyond it, `web_search_tool`'s
# own refusals and `harness/backends/search.py`'s `_self_referential` gate
# decide what may leave the machine, which is where that question belongs.
RUNTIME_COPY_SLOTS = DEFAULT_COPY_SLOTS

# **One slot that is copy-constrained against *this turn* rather than against
# the conversation, and it is the other half of the same question.**
# `RUNTIME_COPY_SLOTS` above lost the query slot because the source reached too
# far back to let a chain query compose. This one is added because the source
# reaching that far back lets a turn *write*:
#
#     note down buy milk               ->  decline
#     save a note that I need to       ->  save_note{"text": "buy milk"}
#     call the dentist tomorrow            "Noted."
#
# Measured on `corn_jr_260m_v4`, `--multi`, **7 of 20 identical pairs** -- and
# the carrier is the sampled decline line, so a nominally deterministic tool
# argument is decided by a draw two turns earlier. It is the only defect the
# session 13 drive found that is neither loud nor safe: the note store gets a
# row the user never authorised, and the reply says "Noted." either way.
#
# **A note is a span of the sentence that asked for it.** `corn/grammar.py`'s
# `SPAN_SLOTS` already records `("save_note", "text")` -- every note in every
# corpus call is a span of the utterance, asserted off `data/raw/tools.txt` --
# so this holds him to what he was trained to do rather than to something new.
# What is new is only *which* source: `CopySpec.narrow` points it at the current
# turn, while the contact slots keep the whole conversation, because the clarify
# path depends on copying a name out of an earlier observation and breaking that
# would trade one defect for another.
#
# Not in `DEFAULT_COPY_SLOTS`, on that constant's own standing rule: it is what
# `evals/` scores under and moving it makes every number ever measured
# incomparable. The runtime is where the second turn actually arrives.
RUNTIME_NARROW_SLOTS = frozenset({("save_note", "text")})


class Session:
    """One resident `Agent`, shared by every connection.

    Shared rather than per-connection because the model is the expensive thing
    and there is one of it. That makes `--multi` history a property of the
    *server* rather than of a client, which is right for a single-user design
    -- VISION §4 is explicit that one instance serves one person -- and would be
    wrong the moment it were not. `reset` is how a client drops it.
    """

    def __init__(self, agent: Agent, wiring: dict, gate=None,
                 log_path: Path | None = None, doc_control=None,
                 doc_state: dict | None = None):
        self.agent = agent
        # The pending confirmation lives on the session, not the connection: a
        # voice client that reconnects between "call Mum" and "yes" is one
        # dropped socket, not a reason to dial or to forget.
        self.gate = gate
        # The document seam: `doc_control` loads, replaces or (empty path)
        # unloads the one document mid-session, and `doc_state` is what it
        # mutates -- on the session for the gate's reason, because a resident
        # process you can only load a document into by restarting defeats the
        # resident process. See docs/PLAN-DOC-ANSWERS.md.
        self.doc_control = doc_control
        self.doc_state = doc_state if doc_state is not None else {"doc": None}
        # What this process is wired to, reported verbatim by `info`. Three of
        # these exist for `harness/checkup.py`'s benefit and are worth the
        # width: a run of real turns **executes real tools**, so a client about
        # to do that needs to know which note store it is going to write to,
        # whether queries will leave the machine, and whether the temperature
        # makes the run reproducible at all. A harness that had to guess at any
        # of the three would be measuring something it could not name.
        self.wiring = wiring
        # Not an asyncio lock held across a thread hop: the turn runs in an
        # executor, so what has to be excluded is two turns entering the model
        # at once from two coroutines.
        self.lock = asyncio.Lock()
        self.turns = 0
        # Where rows go, or `None` for `--no-log`. Per server; the identity of
        # a sitting is per connection and lives on the `SessionLog` itself.
        self.log_path = log_path

    def log_wiring(self) -> dict:
        """What `info` reports, minus what changes while a sitting runs.

        Read off `info()` rather than listed again here: a row whose wiring
        disagreed with the frame every client already gets would be the
        two-descriptions-of-one-idea failure `harness/protocol.py` exists to
        avoid. `turns` and `pending` come out because they are the state of the
        session at an instant rather than the configuration a row was produced
        under, and `params` because it is a number nobody will group by.
        """
        return {k: v for k, v in self.info().items()
                if k not in ("turns", "pending", "params", "log")}

    def window(self) -> dict:
        """The history as the last turn left it: what the model was shown.

        **Read-only, and there for the one question a transcript cannot
        answer** -- was the turn a follow-up refers to still in front of him?
        `Agent._prior` trims (and under `--fold-history` folds) the history at
        the start of every turn, in place, and then appends the turn it ran; so
        after a turn every entry but the last is exactly the prior that turn
        read. Without this a miss three tool turns back is ambiguous between
        the trimmer dropping the antecedent and the weights ignoring it, and
        those are a runtime fact and a corpus fact. `harness/memorygrid.py` is
        the reader. Token counts are the agent's own tokenizer, so `room` and
        the entries are in the unit the fit used.
        """
        a = self.agent
        return {
            "entries": list(a.history),
            "tokens": [len(a.tok.encode(e)) for e in a.history],
            "room": a.cfg.block_size - a.budget - a.round_reserve - 1,
            "block_size": a.cfg.block_size,
            "multi": a.multi,
        }

    def info(self) -> dict:
        cfg = self.agent.cfg
        doc = self.doc_state.get("doc")
        return {
            **self.wiring,
            # Name and window count, or absent -- so a client can always ask
            # what is loaded. Never the contents; a document is personal data
            # on the packs' terms.
            **({"doc": {"name": doc.name, "windows": doc.windows}}
               if doc is not None else {}),
            "params": sum(p.numel() for p in self.agent.model.parameters()),
            "n_layer": cfg.n_layer,
            "n_embd": cfg.n_embd,
            "block_size": cfg.block_size,
            "tokenizer": cfg.tokenizer,
            # Exactly what this turn offers, which is not always the
            # registry: `--no-decline` takes one name out and `--no-declare`
            # takes them all out. Reporting the registry regardless would tell
            # a scorecard the model was shown a set it never saw.
            "tools": list(self.agent.declared) if self.agent.declared else [],
            "grammar": self.agent.constraint is not None,
            "pending": self.gate.pending.tool if (
                self.gate and self.gate.pending) else None,
            "multi": self.agent.multi,
            # The name he answers to on this instance -- `packs/persona.md`'s
            # or the shipped one. A probe scoring the header design reads
            # the say against it (PLAN-PERSONALITY (sixth)).
            "persona_name": self.agent.world.persona.name,
            "name_header": getattr(self.agent, "name_header", False),
            # Ground rule 13: a card must record what the history opened on,
            # because the first-turn number and the seeded number differ by
            # 3-5x and two reads taken under unstated settings cannot be
            # compared. "" is the unseeded control.
            "seed_turn": getattr(self.agent, "seed_turn", None) or "",
            # A prefill optimisation cannot change a row -- the reuse is exact
            # -- but the whole point of recording it is that a card which
            # *did* move would otherwise look like the runtime drifting.
            "prefix_reuse": getattr(self.agent, "prefix_reuse", False),
            "buckets": getattr(self.agent, "buckets", False),
            "compile_step": getattr(self.agent, "compile_step", False),
            # So a client can tell the person whether this sitting is being
            # recorded. A path, not a boolean: "off" and "somewhere you did
            # not expect" are different things to be told.
            "log": str(self.log_path) if self.log_path else "",
            "turns": self.turns,
        }


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 session: Session) -> None:
    peer = writer.get_extra_info("peername")
    loop = asyncio.get_running_loop()
    # **One connection is one session, so the log is made here and not on
    # `Session`.** `Session` is the model and outlives every client; a sitting
    # is what a person had, and two people -- or the same person tomorrow --
    # should not have their turns run together under one id. The path and the
    # wiring are per-server and come off `session`; only the identity and the
    # turn counter are per-connection.
    log = SessionLog(session.log_path, session.log_wiring())

    async def send(obj: dict) -> None:
        writer.write(encode(obj))
        await writer.drain()

    try:
        while True:
            line = await reader.readline()
            if not line:
                break
            if len(line) > MAX_LINE:
                await send({"t": "error", "why": "frame too large"})
                break
            try:
                req = decode(line)
            except (ValueError, UnicodeDecodeError) as exc:
                await send({"t": "error", "why": f"bad frame: {exc}"})
                continue

            op, rid = req.get("op"), req.get("id")

            if op == "ping":
                await send({"t": "pong", "id": rid})
                continue
            if op == "info":
                await send({"t": "info", "id": rid, **session.info()})
                continue
            if op == "window":
                await send({"t": "window", "id": rid, **session.window()})
                continue
            if op == "reset":
                session.agent.reset_history()
                await send({"t": "reset", "id": rid})
                continue
            if op == "doc":
                # The path is opened by the server on the server's filesystem,
                # same trust model as --notes and --packs. Empty path unloads.
                path = req.get("path") or ""
                if not isinstance(path, str):
                    await send({"t": "error", "id": rid,
                                "why": "doc needs a path string"})
                    continue
                if session.doc_control is None:
                    # A Session built without the wiring -- a guard's, usually.
                    await send({"t": "doc", "id": rid, "ok": False,
                                "why": "this server has no document seam wired"})
                    continue
                await send({"t": "doc", "id": rid,
                            **session.doc_control(path)})
                continue
            if op != "turn":
                await send({"t": "error", "id": rid, "why": f"unknown op {op!r}"})
                continue

            user = req.get("user")
            if not isinstance(user, str) or not user.strip():
                await send({"t": "error", "id": rid, "why": "turn needs a user string"})
                continue

            # **Before the model, deliberately.** A pending call is resolved
            # by the runtime against what was just said; the model is not
            # consulted, because nothing in the corpus has a second `<|user|>`
            # after an `<|end|>` and asking it to reconstruct the call from an
            # off-distribution context would add a failure mode in order to
            # protect against one. See harness/backends/confirm.py.
            if session.gate is not None:
                answered = session.gate.answer(user)
                if answered is not None:
                    outcome = answered["outcome"]
                    # **Built once, then both sent and logged.** The events a
                    # client is handed and the events a row is built from are
                    # the same objects here, so the record cannot come to
                    # describe a turn the client did not see -- which is the
                    # `harness/protocol.py` rule about one description of one
                    # idea, applied to a path that assembles its own events.
                    gate_events: list[dict] = []
                    if outcome == "confirmed":
                        gate_events.append({"t": "obs",
                                            "name": answered["tool"],
                                            "payload": answered["payload"]})
                    # **Runtime, and the label matters most on this path.**
                    # These words are `harness/backends/confirm.py`'s, written
                    # by hand for a gate the model is deliberately never
                    # consulted about -- a corpus that learned to generate
                    # them would be learning to answer its own confirmations.
                    gate_events.append({"t": "say", "text": answered["say"],
                                        "deferred": False, "author": "runtime"})
                    gate_events.append({"t": "done", "ms": 0.0,
                                        "outcome": outcome,
                                        "tool": answered["tool"],
                                        "transcript": answered["say"]})
                    for ev in gate_events:
                        await send({**ev, "id": rid})
                    log.append(user, gate_events, 0.0)
                    continue
                # `None` with something previously pending means the answer was
                # neither yes nor no. `answer` has already dropped it, and the
                # utterance falls through to be answered as an ordinary turn --
                # so a user who changes the subject is never stuck in a
                # question they cannot talk their way out of.

                # A bare yes or no with nothing held is the gate's vocabulary
                # arriving without the gate's question, and the router's
                # answer to it was a web search for the word "no". The gate
                # replies instead -- see `Gate.orphan` for what is included
                # and, more importantly, what is not.
                orphaned = session.gate.orphan(user)
                if orphaned is not None:
                    gate_events = [
                        {"t": "say", "text": orphaned, "deferred": False,
                         "author": "runtime"},
                        {"t": "done", "ms": 0.0, "outcome": "orphan",
                         "transcript": orphaned},
                    ]
                    for ev in gate_events:
                        await send({**ev, "id": rid})
                    log.append(user, gate_events, 0.0)
                    continue

            if session.lock.locked():
                # Said rather than silently queued. A client that knows it is
                # behind something can tell the user; one that is merely slow
                # cannot tell that apart from a hung model.
                await send({"t": "waiting", "id": rid})

            async with session.lock:
                # The turn is synchronous and GPU-bound, so it runs in a thread
                # and posts its events back through the loop. `call_soon_
                # threadsafe` rather than awaiting from the worker: the sink is
                # called from inside the decode loop and must never block it,
                # which is what would turn a streaming server into a batching
                # one.
                queue: asyncio.Queue = asyncio.Queue()

                def sink(ev: dict) -> None:
                    loop.call_soon_threadsafe(queue.put_nowait, ev)

                started = time.perf_counter()

                def run() -> None:
                    try:
                        session.agent.turn(user, echo=False, emit=sink)
                    except Exception as exc:  # a bad turn must not kill the server
                        sink({"t": "error", "why": f"{type(exc).__name__}: {exc}"})
                    finally:
                        sink({"t": "__eot__"})

                task = loop.run_in_executor(None, run)
                # What the client was sent, kept so the row is built from the
                # events themselves rather than re-parsed out of the finished
                # transcript. `sessionlog.turn_record` explains why that
                # distinction is the whole point of the file.
                seen: list[dict] = []
                while True:
                    ev = await queue.get()
                    if ev.get("t") == "__eot__":
                        break
                    if ev.get("t") == "done":
                        ev["ms"] = round((time.perf_counter() - started) * 1000, 1)
                    seen.append(ev)
                    await send({**ev, "id": rid})
                await task
                session.turns += 1
                # After the answer has gone out, never before it. This is a
                # file append on the request path and the user is waiting on
                # nothing here; `SessionLog.append` also refuses to raise, so
                # a bad path costs a line of warning rather than a turn.
                log.append(user, seen,
                           (time.perf_counter() - started) * 1000)
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        print(f"-- client gone {peer}")
        writer.close()


async def serve(session: Session, host: str, port: int) -> None:
    server = await asyncio.start_server(
        lambda r, w: handle(r, w, session), host, port)
    where = ", ".join(str(s.getsockname()) for s in server.sockets)
    print(f"listening on {where}")
    async with server:
        await server.serve_forever()


def main() -> None:
    # Every knob lives in `harness/serverconfig.py` -- defaults, then
    # `server.json`, then these flags, in that order (`voice/config.py`'s
    # argument, adopted whole). The fields, the help texts and the `--all`
    # expansion are all the config module's, so the studio's form and this
    # command line can never describe the same knob twice.
    from . import serverconfig
    from .serverconfig import ServerConfig

    ap = argparse.ArgumentParser(description=__doc__)
    serverconfig.add_arguments(ap)
    args = ap.parse_args()
    try:
        cfg = ServerConfig.load(args.config).override(args)
    except serverconfig.ConfigError as exc:
        raise SystemExit(f"config: {exc}")

    # **Declaration-file tools register before anything reads the registry.**
    # `Agent` renders the declaration from `REGISTRY` at construction and the
    # `cfg.tools` subset below is validated against the same dict, so a tool
    # arriving after either would be a tool the model was never told about.
    runners: dict = {}
    gated_customs: tuple[str, ...] = ()
    custom_names: list[str] = []
    if cfg.tools_dir:
        from .backends.toolsd import load as load_toolsd
        from .backends.toolsd import register_all
        loaded_tools = load_toolsd(cfg.tools_dir)
        runners = register_all(loaded_tools)
        gated_customs = tuple(sorted(
            d.tool.name for d in loaded_tools.tools if d.gated))
        ungated = sorted(set(runners) - set(gated_customs))
        custom_names = sorted(runners)
        print(f"tools.d  -> {len(runners)} tool(s) from {cfg.tools_dir}"
              + (f" ({loaded_tools.rejected} dropped)"
                 if loaded_tools.rejected else ""))
        if ungated:
            # Named out loud for `log`'s reason: a command that runs on the
            # model's say-so alone is a thing the owner chose, and choosing
            # it should be visible every start.
            print(f"           {', '.join(ungated)} run without asking "
                  f"(gated: false)")
        for w in loaded_tools.warnings:
            print(f"           !! {w}")

    if cfg.tools:
        from corn.tools import REGISTRY
        unknown = sorted(set(cfg.tools) - set(REGISTRY))
        if unknown:
            raise SystemExit(
                f"config: tools names unknown tool(s) {unknown} -- known "
                f"after tools.d: {sorted(REGISTRY)}")

    backend = None
    if cfg.search:
        from .backends.search import record_refusal, web_search
        # **The deep path is wired here and only here**, because whether a
        # page may be fetched for its passage depends on whether anything
        # will read the passage -- see `_subject_page`. `--extract` is what
        # wires the reader, so it is what turns this on; without it the
        # backend behaves exactly as it always has.
        live = (partial(web_search, deep=True) if cfg.extract
                else web_search)

        # **The backstop on the person's own line, in front of the network
        # and behind the packs.** `record_refusal`'s docstring has the
        # reading: on the seeded runtime the query that leaves is sometimes
        # the seed's own `what day is it`, and the private question is in
        # the utterance the query-side gate never sees. `world.last_user` is
        # bound below and set by `Agent.turn` before any call runs; a caller
        # with no world (a guard, a bare backend) falls through to the
        # query-side gate exactly as before. Wrapped *inside* `pack_search`,
        # so a pack still answers "what's my name" first.
        def guarded(query, **kw):
            asked = getattr(world, "last_user", "") if world is not None else ""
            refused = record_refusal(asked)
            if refused is not None:
                return {**refused, "query": query}
            return live(query, **kw)

        backend = guarded
        print("web_search -> live (queries leave this machine)")

    packs = None
    persona = None
    marker = None
    if cfg.packs:
        from corn.tools import web_search_tool

        from .backends.packs import load as load_packs
        from .backends.packs import pack_search
        from .backends.persona import load as load_persona
        loaded_packs = load_packs(cfg.packs)
        packs = loaded_packs.summary()
        # **Read out of the same folder, because it is the same kind of
        # thing.** `persona.md` is his facts and `about-me.md` is the owner's,
        # and both are the store VISION §4 says an instance specialises
        # through. No second flag: a person who mounted their packs has said
        # everything they need to say about where their own files live.
        loaded_persona = load_persona(cfg.packs)
        persona = loaded_persona.persona
        marker = Marker(Path(cfg.persona_state))
        # In front of whichever search exists: the live web under --search,
        # the trained table without it. A pack can only add answers -- a
        # miss falls through untouched.
        backend = pack_search(loaded_packs, backend or web_search_tool)
        print(f"packs    -> {packs['tables']} tables, {packs['docs']} docs "
              f"from {cfg.packs}"
              + (f" ({packs['rejected']} dropped)" if packs["rejected"] else ""))
        for w in loaded_packs.warnings:
            print(f"           !! {w}")
        told = loaded_persona.summary()
        print(f"persona  -> {told['name']}, {told['occasions']} dated "
              f"occasion(s) from {cfg.packs}")
        # This console only, like every other store's warnings: an occasion is
        # the owner's own sentence about their own day.
        for w in loaded_persona.warnings:
            print(f"           !! {w}")
        # **The people store's birthdays** (PLAN-PEOPLE §5): every pack table
        # with a `Birthday` column, a heads-up `birthday_lead` days out.
        # Counted, never listed -- names and dates are the owner's.
        from dataclasses import replace

        from .backends.persona import people_birthdays
        people, warned = people_birthdays(loaded_packs, cfg.birthday_lead)
        if people:
            persona = replace(persona, occasions=persona.occasions + tuple(people))
            print(f"people   -> {len(people)} birthday(s), mentioned "
                  f"{cfg.birthday_lead} day(s) ahead")
        for w in warned:
            print(f"           !! {w}")

    gate = None
    if cfg.confirm:
        from .backends.confirm import DEFAULT_GATED, Gate
        gated = DEFAULT_GATED + gated_customs
        gate = Gate(gated, runners=runners)
        print(f"confirm  -> {', '.join(gated) or 'nothing gated'}; calls and "
              f"texts reach only you, so they run without asking")

    # **The document composition -- a closure over mutable state, because the
    # one document loads, replaces and unloads mid-session** (`op: doc`), and
    # `World.search` is read per turn. While a document is loaded it answers
    # first; a miss falls through to the live/pack chain only under --search,
    # and otherwise the document's own `no_results` stands -- a question the
    # paper does not answer must not be answered from the corpus's invented
    # FACTS table, which is the honest configuration for a private machine
    # (docs/PLAN-DOC-ANSWERS.md). `World` and `EXECUTORS` do not change.
    from .backends.document import answer as doc_answer
    from .backends.packs import _takes_keywords

    doc_state: dict = {"doc": None}
    inner = backend
    inner_kw = _takes_keywords(inner) if inner is not None else False

    def doc_search(query: str, **kw) -> dict:
        d = doc_state["doc"]
        if d is not None:
            # A second-source request avoids the document too: the paper
            # agreeing with itself is not corroboration. Same rule packs
            # apply to their own tables.
            avoid = kw.get("avoid") or ()
            if not any(d.name in str(a).lower() or str(a).lower() in d.name
                       for a in avoid):
                # **A request that names a set of steps starts a recitation**
                # (`corn/steps.py`). It rides here rather than in a hatch
                # because the *opening* of a recipe is an ordinary lookup --
                # the model routes it, and speaks step one in its own voice.
                # Only the mechanical "next"/"repeat"/"stop" turns are hatched.
                # `start` returns None unless the request clearly names one, so
                # an ordinary question about the document is never intercepted.
                cursor = getattr(world, "steps", None)
                if cursor is not None and cursor.recipes:
                    # **On the user's own line, not the model's query.**
                    # Beginning a recitation is a decision about what the
                    # person asked for; the query arriving here is whatever
                    # the model wrote, and under `--multi` that is sometimes
                    # the previous turn's query copied forward. Measured live
                    # 2026-08-27: "how do I make the tiramisu" -- a recipe the
                    # book does not have -- carried the prior call's
                    # "Chickpea And Spinach Curry" and restarted it. The
                    # fall-back to `query` keeps a caller that sets no
                    # utterance (a guard, a bare backend) working as before.
                    asked = getattr(world, "last_user", "") or query
                    begun = cursor.start(asked)
                    if begun is not None:
                        return begun
                hit = doc_answer(d, query)
                if "answer" in hit or hit.get("reason") == "empty_query":
                    return hit
                if not cfg.search:
                    return hit
        if inner is None:
            from corn.tools import web_search_tool
            return web_search_tool(query)
        return inner(query, **kw) if inner_kw else inner(query)

    # Installed only when it can change anything, so a table-backed server
    # with no document stays byte-identical -- `identity_reply` reads
    # `world.search is not None` as "live", and a delegating closure would
    # flip that answer for a configuration nothing is different in. A
    # mid-session load installs it then; unload takes it back out.
    world = World(date.today(), Path(cfg.notes),
                  search=doc_search if inner is not None else None,
                  confirm=gate.intercept if gate else None,
                  persona=persona, marker=marker)
    if cfg.dtype != "fp32":
        print(f"dtype    -> {cfg.dtype} (every published row is fp32; "
              f"scorecards from this instance are not comparable with them)")
    print(f"loading {cfg.ckpt} ...")
    t0 = time.perf_counter()
    agent = Agent(
        cfg.ckpt, cfg.device, cfg.temperature, world,
        grammar=cfg.grammar, copy_slots=RUNTIME_COPY_SLOTS,
        narrow_slots=RUNTIME_NARROW_SLOTS,
        multi=cfg.multi, offer_decline=cfg.decline,
        tools=tuple(cfg.tools),
        rephrase=not cfg.restrict,
        speech_temperature=cfg.speech_temperature,
        dtype=cfg.dtype,
        fold=cfg.fold,
        history_fold=cfg.history_fold,
        family_check=cfg.family_check,
        identity_check=cfg.identity_check,
        name_header=cfg.name_header,
        round_reserve=cfg.round_reserve,
        budget=cfg.budget,
        buckets=cfg.buckets,
        compile_step=cfg.compile_step,
        prefix_reuse=cfg.prefix_reuse,
    )
    # The number this whole module exists to pay once. Printed so the argument
    # for a resident process is a measurement rather than an assertion.
    print(f"loaded in {time.perf_counter() - t0:.1f}s -- "
          f"the cost a per-turn process would pay every turn")
    # The seed turn (see `Agent.seed_turn`) is planted here for the first
    # conversation and by `reset_history` for every one after. Before the
    # reader is wired, deliberately: the seed is a hatched turn and must never
    # depend on anything a tool backend does.
    if cfg.seed_turn:
        agent.seed_turn = cfg.seed_turn
        agent.seed_trim = cfg.seed_trim
        agent.seed_repass = cfg.seed_repass
        agent.reset_history()
        print(f"seeded   -> history opens on {cfg.seed_turn!r} "
              f"({len(agent.history)} entr{'y' if len(agent.history) == 1 else 'ies'})")

    # **After the load, because this is the one seam that is the model.**
    # `World` is built before `Agent` and `Agent` is what owns the weights, so
    # the reader is assigned rather than passed -- see `World.reader`. It reads
    # the same model the turn does: a second copy would double the residency
    # this whole module exists to pay once, and the worker and the speaker
    # never decode at the same moment.
    if cfg.extract:
        from .backends.read import Reader
        world.reader = Reader(agent.model, agent.tok, cfg.device,
                              gate=cfg.extract_gate,
                              gate_threshold=cfg.gate_threshold,
                              reader=cfg.reader,
                              reader_threshold=cfg.reader_threshold,
                              extent_d=cfg.reader_extent_d,
                              reader_adapter=cfg.reader_adapter,
                              reader_whole_threshold=cfg.reader_whole_threshold,
                              # The trunk this process actually loaded, not a
                              # constant that agrees with it today: the whole
                              # arm's adapter names a trunk by sha256 and the
                              # point of that is to refuse a `--ckpt` it was
                              # not fitted to.
                              trunk_ckpt=cfg.ckpt)
        print("extract  -> on (the passage is read in windows; "
              "the lead sentence is the floor)"
              + ("" if cfg.search else " -- no effect without --search"))
        # The reader is printed before the gate because it decides whether the
        # gate runs at all: the head's verifier *is* the gate, so a card that
        # said "gate on" beside `--reader head` would name a forward that
        # never happens.
        if cfg.reader == "head":
            print(f"reader   -> head at {cfg.reader_threshold} "
                  f"(extent d = {cfg.reader_extent_d}; corn/reader.py points "
                  "at the span and its verifier decides -- no decode, and "
                  "the gate is bypassed)")
        elif cfg.reader == "head_whole":
            print(f"reader   -> head_whole at {cfg.reader_whole_threshold} "
                  f"(extent d = {cfg.reader_extent_d}; the passage is read "
                  "whole in one forward through the adapter in "
                  f"{cfg.reader_adapter} -- no cut, no vote, no decode, and "
                  "the gate is bypassed)")
        else:
            print("reader   -> generate (the worker decodes an answer per "
                  "admitted window -- `--reader head` is the arm)")
            print(f"gate     -> {'on at ' + str(cfg.gate_threshold) if cfg.extract_gate else 'off (--no-extract-gate)'}"
                  + (" (each window is scored before it is read; the runtime "
                     "declines for the ones it refuses -- corn/gate.py)"
                     if cfg.extract_gate else
                     " -- every window is read and the generator decides"))

    # After the load for the reader's reason: encoding a document needs the
    # tokenizer, and the tokenizer arrives with the agent. `set_doc` is the
    # whole of what `op: doc` does -- load, replace, or (empty path) unload,
    # newest load wins, one document at a time (the single-slot posture
    # `range_span` and the confirm gate take: stale state answers questions
    # nobody remembers asking).
    def set_doc(path: str) -> dict:
        from .backends.document import load as load_doc
        from corn.steps import Cursor
        if not path.strip():
            doc_state["doc"] = None
            world.steps = None
            if inner is None:
                world.search = None
            return {"ok": True, "name": "", "windows": 0}
        d = load_doc(path, agent.tok.encode, agent.tok.decode)
        if d is None:
            # The printed reason went to the server's console; the client
            # gets the fact. Loading a broken file changes nothing loaded.
            return {"ok": False, "why": f"could not load {path} -- "
                                        f"see the server console"}
        doc_state["doc"] = d
        # Dead until a request names a set of steps, and empty for every
        # document that numbers nothing -- so a paper loads exactly as it did.
        world.steps = Cursor(d.name, d.recipes)
        if inner is None:
            world.search = doc_search
        return {"ok": True, "name": d.name, "windows": d.windows,
                "recipes": len(d.recipes)}

    if cfg.doc:
        loaded_doc = set_doc(cfg.doc)
        if loaded_doc["ok"]:
            print(f"document -> {loaded_doc['name']}, "
                  f"{loaded_doc['windows']} windows"
                  + (f", {loaded_doc['recipes']} step lists"
                     if loaded_doc.get("recipes") else "")
                  + ("" if cfg.search else
                     " (web_search answers from it or abstains; no fall-through"
                     " to the trained table)"))
        else:
            print(f"document -> !! {loaded_doc['why']}")

    # On by default since 2026-09-06 (decision 6), and said out loud for the
    # log line's reason below: what he can see of the last turn is the first
    # thing a person forms a theory about, and it should not take reading the
    # flags to learn which runtime is answering.
    if cfg.multi:
        print("turns    -> multi; the transcript carries across turns "
              "(--no-multi answers each on an empty history)")
    else:
        print("turns    -> independent; each turn opens on an empty history "
              "(--no-multi), which is the pre-2026-09-06 runtime")

    log_path = Path(cfg.log) if cfg.logging else None
    if log_path is not None:
        # Said out loud at startup, every time. A process that records the
        # conversation should never be one you have to read the flags to
        # discover you started -- `--packs` and `--search` both announce
        # themselves above for smaller reasons than this one.
        print(f"log      -> {log_path} (one JSON line per turn; --no-log is off)")
    else:
        print("log      -> off; nothing about this sitting is kept")

    session = Session(agent, log_path=log_path, gate=gate,
                      doc_control=set_doc, doc_state=doc_state, wiring={
        "confirm": list(gate.gated) if gate else [],
        "ckpt": cfg.ckpt,
        "notes": cfg.notes,
        "search": "live" if cfg.search else "table",
        # The subset the owner chose, or "all" -- `info.tools` already carries
        # the declared names verbatim, so this is the *decision* rather than
        # its result, which is what a scorecard needs: an instance narrowed to
        # three tools is answering an easier routing question than the
        # seven-way one every published row was scored on.
        "tools_enabled": sorted(cfg.tools) or "all",
        # Names only, never a command -- the declarations are the owner's.
        **({"custom_tools": custom_names} if custom_names else {}),
        # Counts only, never contents -- pack cells are the owner's. Absent
        # entirely when no pack is loaded, so old clients see the old dict.
        **({"packs": packs} if packs else {}),
        # **Every published row in this project was read in fp32.** A bf16
        # instance is the same weights answering a slightly different
        # question -- see `corn.sample.load_checkpoint` -- so a client
        # comparing a live number against a scorecard has to be able to see
        # which precision produced it. Same argument as `decline` and `copy`,
        # and a stronger one, because this changes the tokens themselves.
        "dtype": cfg.dtype,
        # For the same reason `decline` and `copy` are here: it changes what
        # the `answer` field in a `web_search` observation *is*. A row whose
        # answer was extracted and one whose answer was the provider's lead
        # sentence are two different measurements and a client comparing them
        # needs to be able to see which it has.
        "extract": bool(cfg.extract),
        # Who a call or a text can reach: the owner, and nobody else
        # (PLAN-PEOPLE §7, 2026-10-13). Replaces the contact book's count.
        "reach": "owner",
        "temperature": cfg.temperature,
        # **Reported for `--temperature`'s reason, and it was missing.** The
        # calls are greedy and the *speech* is not, so a card that recorded one
        # temperature recorded half the decode -- and
        # `docs/PLAN-FINETUNE-V4.md`'s ground rule 13 asks every cell to record
        # the settings it was read under, naming this one explicitly. It
        # changes nothing a turn does; it changes what a row means, which is
        # exactly the test the fields around it are here under.
        "speech_temperature": cfg.speech_temperature,
        # **Reported for `speech_temperature`'s reason, and it is the stronger
        # case of the two.** The fold rewrites the tokens the model is handed,
        # so a row read with it on and a row read with it off are two different
        # measurements of two different machines -- ground rule 13's whole
        # point, and the rule the fold's own before/after was run under. Every
        # grid lifts this into its card's `decode` block. See
        # `corn.agent.fold_turn`.
        "fold": cfg.fold,
        # PLAN-CONVERSATION 4a, 4h and 4f, reported for `fold`'s reason: each
        # changes what a social row or a history row means. `family_check`
        # decides who wrote a served social sentence; `round_reserve` and
        # `budget` decide how much history the model was shown.
        "family_check": cfg.family_check,
        "identity_check": cfg.identity_check,
        "name_header": cfg.name_header,
        "round_reserve": cfg.round_reserve,
        "budget": cfg.budget,
        # Reported because it changes what every row on every scorecard means.
        # A `held_back` rate from an instance that was never offered an escape
        # is not the same number as one from an instance that was, and a client
        # writing a JSON card needs to be able to say which it measured.
        "decline": cfg.decline,
        # For the same reason as `decline`, and it is a newer one: this
        # instance runs a copy constraint one slot wider than the set `evals/`
        # scores under, so a client comparing a live number against a published
        # row needs to be able to see that. See `RUNTIME_COPY_SLOTS`.
        "copy": sorted(f"{t}.{p}" for t, p in RUNTIME_COPY_SLOTS),
        # Reported separately rather than folded into `copy`, because the
        # two are not the same claim: one says a value must be a span of
        # the conversation, the other that it must be a span of this turn.
        # A row that could not tell them apart would make the session-13
        # repair invisible to anything reading the log back. See
        # `RUNTIME_NARROW_SLOTS`.
        "copy_turn": sorted(f"{t}.{p}" for t, p in RUNTIME_NARROW_SLOTS),
    })
    try:
        asyncio.run(serve(session, cfg.host, cfg.port))
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
