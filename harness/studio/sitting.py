"""The one conversation the studio holds, shared by every tab that opens it.

**One socket to the server, many pages on it.** `harness/server.py` makes one
connection one session -- one log id, one turn counter -- and the model has
one history whichever client typed. The NiceGUI studio opened a socket per
browser tab, so a reload showed an empty page in front of a model that still
remembered everything, and two tabs were two sessions in the turn log. Here
the studio process owns the connection; a tab subscribes, is handed the
conversation so far (`snapshot`), and from then on receives every event as
it happens -- including the turns another tab sent. A reload costs nothing.

**And the conversation outlives the studio.** With a `state_path` the replay
log and the transcript are written there after every turn (atomically, off
the event loop) and read back at start, so restarting the studio -- or the
machine -- reopens on the same conversation, and Save still writes the whole
sitting to the same `sessionN.txt`. The file lives in `Saved Sessions/`,
which is gitignored for exactly this kind of content.

**A restored conversation says when he no longer remembers it.** The view
can outlive the model's memory: the studio restarts the server on a settings
save, and a studio restart spawns a fresh one. So every time the socket comes
up, the studio asks the server for its `window` -- the history the last turn
was shown -- and if the last thing typed here is not in it, a divider goes
into the conversation: everything above it is on the page and not in his
head. Asking rather than assuming is what keeps the divider off a reconnect to
a server that never went away.

**The renderings the reference client decides are decided here, in Python,
once.** `harness/client.py`'s `run_turn` is the reference: it holds back a
trailing `<|end|>` that may arrive split across two `text` events (`_Tail`),
and it renders a `say` only when its words differ from what streamed
(`_content`). Both rules are imported, not restated, and applied before an
event reaches a page -- so the page draws `text` as text and `say` when
`shown` says so, and cannot get either rule subtly wrong in JavaScript.
`scripts/check_studio.py` drives this module against a fake server and holds
what it forwards to what `run_turn` prints.

**One rule is the page's own: no marker reaches a person.** On a tool turn
the model streams `<|say|>` before its words, and the terminal prints it --
a terminal transcript is the record. A page is read by someone who should
see "Saved.", not "<|say|>Saved.", so complete markers (`client._MARKER`,
the same pattern `_content` strips) come off the forwarded text, and a run
that may still become one (`<|sa`) is held back until the next token
settles it -- `_Tail`'s move, widened from the end markers to every marker.
The transcript keeps the raw events either way.

**Events in, the same events out, three fields added and none removed except
the transcript.** `say` gains `shown`, `done` gains `first_ms` (latency is the
top-level constraint, VISION §3, and time to the first word is the half of it
a person feels), and the synthetic events are this module's: `user` (a turn
some tab sent), `note` (the restart divider), `link` (the socket came up or
went down), `status` (the supervisor's answer, with whether a saved change is
waiting on a restart), `hello` (the snapshot). `done.transcript` is dropped
on the way to the page -- it is the raw turn text, the record's and not the
reader's, and it is the largest field the protocol carries.

**The log a new tab replays is coalesced.** A reply streams as one `text`
event per token; the log keeps one `text` per run of them, so a tab opened an
hour into a sitting is handed hundreds of events rather than tens of
thousands. A live tab still sees each token as it lands.

**No framework, and asyncio only.** Like `supervisor` and `transcript`, this
imports nothing optional, so the guard runs it on a machine without the web
dependencies installed. The socket is asyncio's, not `overlay/link.py`'s
thread-and-queue, because here the reader is already inside an event loop
and a thread would only add a hop to every token.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import os
import re
import time
from pathlib import Path
from typing import Callable

from ..client import _MARKER, _STOPS, _Tail, _content
from ..protocol import MAX_LINE, encode
from . import transcript as _transcript
from .transcript import Transcript

# Events a new tab is handed on connect. `info`, `window`, `pong`, `link` and
# `status` are state rather than history -- the snapshot carries their latest
# value instead of their sequence.
LOGGED = frozenset({"user", "text", "say", "call", "obs", "fold", "rejected",
                    "error", "done", "waiting", "doc", "note"})

# A whole sitting coalesced is a few events per turn; this bound is a few
# hundred turns, past which the oldest fall off the replay (never off the
# transcript, which keeps everything).
LOG_LIMIT = 4000

# The tail of a run that could still become a marker: `<`, `<|`, `<|sa`,
# `<|say|`. Held back one token; released if the next does not complete it.
_PARTIAL = re.compile(r"<(\|[a-z]*\|?)?$")

# How often a dead socket is retried. The supervisor's `up` kicks a retry at
# once, so this is only the floor for a server somebody else started.
RETRY_S = 1.0

RESTART_NOTE = "He restarted here -- the conversation above is not in his memory."

STATE_VERSION = 1


class Sitting:
    def __init__(self, addr: Callable[[], tuple[str, int]], *,
                 status: Callable[[], tuple] | None = None,
                 state_path: Path | None = None,
                 retry: float = RETRY_S, status_every: float = 1.0):
        self.addr = addr
        self._status_fn = status
        self.state_path = Path(state_path) if state_path else None
        self.retry = retry
        self.status_every = status_every
        self.transcript = Transcript()
        self.log: list[dict] = []
        self.subs: set[asyncio.Queue] = set()
        self.up = False
        self.busy = False
        self.info: dict | None = None
        self.doc: dict | None = None
        self.status: dict = {"state": "stopped", "why": "", "pending": False}
        self._writer: asyncio.StreamWriter | None = None
        self._wake: asyncio.Event | None = None
        self._tasks: list[asyncio.Task] = []
        self._probe = False
        # One writer thread, so saves land in the order they were made: a
        # reset written before the turn it cleared would resurrect the turn.
        self._writer_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="sitting-save")
        self._turn_reset()
        self._load()

    # -- lifecycle -----------------------------------------------------------

    def start(self) -> None:
        """Begin connecting (and polling the supervisor, when there is one).
        Called once, from inside the running loop."""
        self._wake = asyncio.Event()
        self._tasks.append(asyncio.create_task(self._connect_loop()))
        if self._status_fn is not None:
            self._tasks.append(asyncio.create_task(self._status_loop()))

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()
        for t in self._tasks:
            try:
                await t
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
        self._tasks.clear()
        self._drop()
        self._writer_pool.shutdown(wait=True)
        self._write(self._state())

    def kick(self) -> None:
        """Retry the socket now rather than at the next tick -- the
        supervisor just saw the server answer."""
        if self._wake is not None:
            self._wake.set()

    # -- the conversation on disk -------------------------------------------

    def _state(self) -> dict:
        saved = self.transcript._saved
        return {"version": STATE_VERSION, "saved_at": time.time(),
                "log": list(self.log),
                "transcript": {"lines": list(self.transcript.lines),
                               "saved": saved.name if saved else None}}

    def _write(self, state: dict) -> None:
        """Atomically: a crash mid-write leaves the previous file, never half
        of a new one."""
        if self.state_path is None:
            return
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.state_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(state, ensure_ascii=False),
                           encoding="utf-8")
        except OSError:
            return  # a full disk costs the restore, not the conversation
        # Windows refuses to replace a file another process has open -- a
        # reader, an indexer, an antivirus scan -- for the moment it has it.
        # That moment passes; a write dropped on it would leave the file a
        # turn (or a reset) behind with nothing said. So: retry, briefly.
        for attempt in range(20):
            try:
                os.replace(tmp, self.state_path)
                return
            except PermissionError:
                time.sleep(0.025 * (attempt + 1))
            except OSError:
                return

    def _persist(self) -> None:
        """Write after a turn, off the event loop; the snapshot is taken now
        so the thread never reads a list the loop is appending to."""
        if self.state_path is None:
            return
        state = self._state()
        try:
            self._writer_pool.submit(self._write, state)
        except RuntimeError:  # the pool is shut: the studio is stopping
            self._write(state)

    def _load(self) -> None:
        if self.state_path is None or not self.state_path.exists():
            return
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if not isinstance(state, dict) or state.get("version") != STATE_VERSION:
            return
        log = state.get("log")
        if isinstance(log, list):
            self.log = [e for e in log
                        if isinstance(e, dict) and e.get("t") in LOGGED]
            self.log = self.log[-LOG_LIMIT:]
        t = state.get("transcript") or {}
        if isinstance(t.get("lines"), list):
            self.transcript.lines = [str(x) for x in t["lines"]]
        if t.get("saved"):
            self.transcript._saved = _transcript.SAVE_DIR / Path(
                str(t["saved"])).name

    # -- subscribers ---------------------------------------------------------

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.subs.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self.subs.discard(q)

    def snapshot(self) -> dict:
        return {"t": "hello", "log": list(self.log), "up": self.up,
                "busy": self.busy, "info": self.info, "doc": self.doc,
                "status": dict(self.status)}

    def _broadcast(self, ev: dict) -> None:
        for q in self.subs:
            q.put_nowait(ev)

    def _record(self, ev: dict) -> None:
        """Into the replay log, coalescing a run of `text`, then out."""
        if ev["t"] in LOGGED:
            last = self.log[-1] if self.log else None
            if ev["t"] == "text" and last is not None and last["t"] == "text":
                self.log[-1] = {"t": "text", "text": last["text"] + ev["text"]}
            else:
                self.log.append(dict(ev))
                if len(self.log) > LOG_LIMIT:
                    del self.log[:len(self.log) - LOG_LIMIT]
        self._broadcast(ev)

    # -- requests ------------------------------------------------------------

    async def send(self, **req) -> bool:
        """One request to the server. A `turn` is announced to every tab first,
        so the words appear on the page that did not type them too."""
        if self._writer is None:
            return False
        op = req.get("op")
        if op == "turn":
            text = str(req.get("user", ""))
            if not text.strip():
                return False
            self._turn_reset()
            self._sent = time.perf_counter()
            self.busy = True
            self.transcript.user(text)
            self._record({"t": "user", "text": text, "at": time.time()})
        try:
            self._writer.write(encode(req))
            await self._writer.drain()
        except (OSError, RuntimeError):
            self._drop("the connection broke while sending")
            return False
        return True

    def save_transcript(self):
        path = self.transcript.save()
        self._persist()  # so a restart keeps writing to the same file
        return path

    # -- the socket ----------------------------------------------------------

    async def _connect_loop(self) -> None:
        while True:
            host, port = self.addr()
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port, limit=2 * MAX_LINE),
                    timeout=2.0)
            except (OSError, asyncio.TimeoutError):
                await self._sleep()
                continue
            self._writer = writer
            self.up = True
            self._broadcast({"t": "link", "up": True})
            await self.send(op="info")
            # Does he still remember what is on the page? (`_remembers`)
            self._probe = True
            await self.send(op="window")
            why = "the server closed the connection"
            try:
                while True:
                    line = await reader.readline()
                    if not line:
                        break
                    if line.strip():
                        self._handle(json.loads(line))
            except (OSError, ValueError, asyncio.LimitOverrunError) as exc:
                why = str(exc) or type(exc).__name__
            self._drop(why)
            await self._sleep()

    async def _sleep(self) -> None:
        assert self._wake is not None
        self._wake.clear()
        try:
            await asyncio.wait_for(self._wake.wait(), timeout=self.retry)
        except asyncio.TimeoutError:
            pass

    def _drop(self, why: str = "") -> None:
        writer, self._writer = self._writer, None
        if writer is not None:
            try:
                writer.close()
            except (OSError, RuntimeError):
                pass
        was_up, self.up = self.up, False
        self._probe = False
        if self.busy:
            # A turn cut off by a restart never gets its `done`; the page
            # closes it here so the composer is not left waiting forever.
            self.busy = False
            self._record({"t": "error", "why": "the server went away "
                                               "mid-turn"})
        if was_up:
            self._broadcast({"t": "link", "up": False, "why": why})

    async def _status_loop(self) -> None:
        assert self._status_fn is not None
        while True:
            try:
                got = tuple(await asyncio.to_thread(self._status_fn))
            except Exception as exc:  # noqa: BLE001 -- a poll must not die
                got = ("stopped", f"status failed: {exc}")
            state, why, pending = (got + (False,))[:3]
            now = {"state": state, "why": why, "pending": bool(pending)}
            if now != self.status:
                self.status = now
                self._broadcast({"t": "status", **now})
            if state == "up" and not self.up:
                self.kick()
            await asyncio.sleep(self.status_every)

    # -- events --------------------------------------------------------------

    def _turn_reset(self) -> None:
        self._tail = _Tail()
        self._held = ""
        self._streamed = ""
        self._sent: float | None = None
        self._first: float | None = None

    def _unmark(self, text: str) -> str:
        """Complete markers out, a possible one held back."""
        buf = _MARKER.sub("", self._held + text)
        m = _PARTIAL.search(buf)
        self._held = buf[m.start():] if m else ""
        return buf[:m.start()] if m else buf

    def _since(self) -> float | None:
        if self._sent is None:
            return None
        return (time.perf_counter() - self._sent) * 1000

    def _remembers(self, entries: list) -> None:
        """The divider, when the last thing typed here is not in the history
        he was last shown. Compared by `_content` -- words only -- because
        the history holds the folded utterance, not the typed one."""
        last_user = None
        for ev in reversed(self.log):
            if ev["t"] == "note" and ev.get("kind") == "restart":
                return  # already said, and nothing typed since
            if ev["t"] == "user":
                last_user = ev.get("text", "")
                break
        if last_user is None:
            return
        words = _content(last_user)
        if words and any(words in _content(str(e)) for e in entries):
            return
        self.transcript.note("(he restarted -- the conversation above is "
                             "not in his memory)")
        self._record({"t": "note", "kind": "restart", "text": RESTART_NOTE})
        self._persist()

    def _handle(self, ev: dict) -> None:
        kind = ev.get("t")
        ev.pop("id", None)
        if self._probe and kind == "error" and "window" in str(ev.get("why")):
            self._probe = False  # a server older than the window op
            return
        if kind not in ("pong", "window", "info", "reset", "doc"):
            self.transcript.event(ev)

        if kind == "pong":
            return
        if kind == "info":
            self.info = {k: v for k, v in ev.items() if k != "t"}
            self.doc = self.info.get("doc")
            if not self.transcript.lines:
                self.transcript.header()
                self.transcript.banner(ev)
            self._broadcast({"t": "info", "info": self.info, "doc": self.doc})
            return
        if kind == "window":
            if self._probe:
                self._probe = False
                self._remembers(ev.get("entries") or [])
            self._broadcast(ev)
            return
        if kind == "reset":
            self.log.clear()
            self.transcript.note("(history dropped)")
            self._broadcast({"t": "reset"})
            self._persist()
            return
        if kind == "doc":
            if ev.get("ok"):
                self.doc = ({"name": ev["name"], "windows": ev.get("windows")}
                            if ev.get("name") else None)
                said = (f"(answering lookups from {ev['name']}, "
                        f"{ev.get('windows')} windows)" if ev.get("name")
                        else "(document unloaded)")
            else:
                said = str(ev.get("why", "the document did not load"))
            self.transcript.note(said)
            self._record({**ev, "doc": self.doc})
            self._persist()
            return
        if kind == "text":
            if self._first is None:
                self._first = self._since()
            self._streamed += ev.get("text", "")
            shown = self._unmark(self._tail.feed(ev.get("text", "")))
            if shown:
                self._record({"t": "text", "text": shown})
            return
        if kind == "say":
            said = ev.get("text", "")
            shown = bool(said) and _content(said) != _content(self._streamed)
            if shown and self._first is None:
                self._first = self._since()
            self._record({**ev, "shown": shown})
            return
        if kind == "done":
            rest = self._tail.flush()
            if rest and any(s.startswith(rest) for s in _STOPS):
                rest = ""
            rest = _PARTIAL.sub("", _MARKER.sub("", self._held + rest))
            self._held = ""
            if rest:
                self._record({"t": "text", "text": rest})
            out = {k: v for k, v in ev.items() if k != "transcript"}
            out["first_ms"] = self._first
            self.busy = False
            self._turn_reset()
            self._record(out)
            self._persist()
            return
        if kind == "error":
            self.busy = False
            self._record(ev)
            self._persist()
            return
        self._record(ev)
