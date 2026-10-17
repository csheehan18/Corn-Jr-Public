"""The server as a subprocess: started, watched, restarted, and read.

**Why the studio owns the process at all.** Every other client assumes a
server somebody already started; the studio exists so that a person hosting
their own Corn-Jr starts *one* thing. Owning the process is also what makes a
config form honest -- `server.json` is read at server start, so "Apply" has
to mean a restart, and a button that wrote the file and left the old process
answering would be a form whose changes silently do not take effect.

**No web framework and no asyncio here**, so `scripts/check_studio.py` can drive
the whole state machine with a stubbed `Popen`. Threads only: one daemon
reader per process drains stdout into a bounded tail, which is the crash
report -- stderr is merged into stdout at spawn precisely so the tail is one
stream in one order.

**`ping` is safe to call every second.** It sends one `{"op": "ping"}` frame
and reads one line; `harness/protocol.py` promises that touches no model, so
a status poll can never queue behind a slow turn.

**A saved change is pending until the server restarts, and the studio knows
which.** `start` fingerprints everything the server reads once at start --
`server.json`'s text and the size and mtime of every file in the packs
folder, the tools folder and the book -- and `pending` compares that with
now. The files the server *writes* while it runs (notes, the turn log, the
persona marker) are deliberately not in it, or every turn would look like a
change. Only a process the studio owns has a fingerprint; an external server
was started by somebody else, on a configuration the studio never saw.

**The console does not record the supervisor talking to itself.** The
server prints `-- client gone (address)` whenever a connection closes, and
`ping` is a connection a second -- so within 200 seconds the bounded tail
held nothing but its own pings, and the startup lines and any traceback had
been pushed out of it. `ping` remembers the local port of each connection it
makes, and the reader drops exactly those lines. A real client leaving (the
terminal, the voice client) still prints, because its port was never one of
ours.

**An external server is attached to, never adopted.** If something already
answers on the configured port, `start` refuses to spawn a second process --
the port would collide, and worse, "Apply" would restart a process some other
terminal owns. The studio then behaves like every other client: it talks, and
the status line says who it is talking to.
"""

from __future__ import annotations

import json
import re
import socket
import subprocess
import sys
import threading
import time
from collections import deque
from pathlib import Path

from ..protocol import encode
from ..serverconfig import ConfigError, ServerConfig

REPO_ROOT = Path(__file__).resolve().parents[2]

# How much console survives the process. Startup is ~30 lines of wiring plus
# one per warning; a crash needs the traceback, which Python keeps short.
TAIL_LINES = 200
CRASH_LINES = 15

# The server's line for a closed connection (`harness/server.py`): the peer
# is printed as a tuple, and the port is what identifies one of our pings.
_GONE = re.compile(r"^-- client gone \('[^']*', (\d+)")
# How many recent ping ports are remembered; a ping a second makes this a
# couple of minutes of slack between a ping closing and its line arriving.
OWN_PORTS = 256


class Supervisor:
    def __init__(self, cfg_path: Path, popen=subprocess.Popen):
        self.cfg_path = Path(cfg_path)
        # The seam the guard drives: anything with .poll(), .terminate(),
        # .wait(), .kill() and a .stdout that iterates lines.
        self._popen = popen
        self.proc = None
        self.tail: deque[str] = deque(maxlen=TAIL_LINES)
        # True when `start` found a server it did not spawn. Restart and stop
        # keep their hands off it -- see the module docstring.
        self.external = False
        self.config_error: str | None = None
        # What the running process read at start; see `fingerprint`.
        self._started: tuple | None = None
        # Local ports of our own pings, newest last; see the module header.
        self._own: deque[int] = deque(maxlen=OWN_PORTS)

    # -- what the config says ------------------------------------------------

    def config(self) -> ServerConfig | None:
        """The file as it is *now* -- reloaded per call, because Apply edits
        it between calls. A broken file is remembered rather than raised, so
        the status line can say what is wrong with it."""
        try:
            cfg = ServerConfig.load(self.cfg_path)
            self.config_error = None
            return cfg
        except ConfigError as exc:
            self.config_error = str(exc)
            return None

    def _addr(self) -> tuple[str, int]:
        cfg = self.config()
        if cfg is None:
            # The defaults are where a broken file's server would not be
            # listening anyway; ping just comes back False.
            cfg = ServerConfig()
        return cfg.host, cfg.port

    # -- the socket ----------------------------------------------------------

    def ping(self, timeout: float = 0.5) -> bool:
        host, port = self._addr()
        try:
            with socket.create_connection((host, port), timeout=timeout) as s:
                self._own.append(s.getsockname()[1])
                s.sendall(encode({"op": "ping"}))
                s.settimeout(timeout)
                line = s.makefile("rb").readline()
            return bool(line.strip()) and \
                json.loads(line).get("t") == "pong"
        except (OSError, ValueError):
            return False

    # -- the process ---------------------------------------------------------

    def start(self) -> str:
        """Spawn the server, or explain why not. Empty string on success."""
        if self.proc is not None and self.proc.poll() is None:
            return ""
        if self.config() is None:
            return f"server.json is broken: {self.config_error}"
        if self.ping():
            host, port = self._addr()
            self.external = True
            return (f"a server is already answering on {host}:{port}; "
                    f"attached to it instead of starting a second one")
        self.external = False
        self.tail.clear()
        try:
            self.proc = self._popen(
                [sys.executable, "-m", "harness.server",
                 "--config", str(self.cfg_path)],
                cwd=str(REPO_ROOT), stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                errors="replace")
        except OSError as exc:
            self.proc = None
            return f"could not start the server: {exc}"
        self._started = self.fingerprint()
        threading.Thread(target=self._read, args=(self.proc,),
                         daemon=True).start()
        return ""

    def _read(self, proc) -> None:
        try:
            for line in proc.stdout:
                line = line.rstrip("\n")
                m = _GONE.match(line)
                if m and int(m.group(1)) in self._own:
                    continue
                self.tail.append(line)
        except (OSError, ValueError):
            pass

    def fingerprint(self) -> tuple | None:
        """What the server reads once, at start: the config file's text, and
        (name, mtime, size) for every file in the folders and the file it
        names. None when the config file cannot be read at all."""
        try:
            text = self.cfg_path.read_text(encoding="utf-8")
        except OSError:
            return None
        out: list = [text]
        cfg = self.config()
        if cfg is None:
            return tuple(out)
        for rel in (cfg.packs, cfg.tools_dir):
            if not rel:
                continue
            p = Path(rel) if Path(rel).is_absolute() else REPO_ROOT / rel
            try:
                if p.is_dir():
                    out.append(tuple(sorted(
                        (f.name, f.stat().st_mtime_ns, f.stat().st_size)
                        for f in p.iterdir() if f.is_file())))
                elif p.is_file():
                    st = p.stat()
                    out.append((p.name, st.st_mtime_ns, st.st_size))
            except OSError:
                out.append((rel, "unreadable"))
        return tuple(out)

    def pending(self) -> bool:
        """A change was saved that the running process has not read."""
        if self.external or self.proc is None or self._started is None:
            return False
        if self.proc.poll() is not None:
            return False
        return self.fingerprint() != self._started

    def restart(self) -> str:
        """Stop what we own and start again. The Apply button, in effect.

        `terminate` on Windows is `TerminateProcess` -- abrupt, and safe
        here because the server writes its session log after each turn and
        buffers nothing across them (`harness/sessionlog.py`).
        """
        if self.external:
            host, port = self._addr()
            return (f"the server on {host}:{port} was not started by the "
                    f"studio; restart it where it is running")
        self.stop()
        return self.start()

    def stop(self) -> None:
        proc, self.proc = self.proc, None
        if proc is None or self.external:
            return
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(10)
            except subprocess.TimeoutExpired:
                proc.kill()

    # -- the one-line answer -------------------------------------------------

    def status(self) -> tuple[str, str]:
        """`(state, detail)`; state is stopped/starting/up/crashed.

        "starting" carries the last console line, which during the slow part
        is the server's own `loading <ckpt> ...` -- the checkpoint load and
        graph capture narrate themselves, so no second progress channel is
        needed. "crashed" carries the tail, which is where a ConfigError or
        a traceback landed.
        """
        if self.external:
            if self.ping():
                host, port = self._addr()
                return "up", f"an external server on {host}:{port}"
            self.external = False  # it went away; the studio may spawn now
        if self.config_error:
            return "stopped", f"server.json is broken: {self.config_error}"
        if self.proc is None:
            return "stopped", ""
        code = self.proc.poll()
        if code is not None:
            recent = list(self.tail)[-CRASH_LINES:]
            return "crashed", (f"exited {code}\n" + "\n".join(recent)).strip()
        if self.ping():
            loaded = next((l for l in reversed(self.tail)
                           if "loaded in" in l), "")
            return "up", loaded
        last = self.tail[-1] if self.tail else "starting"
        return "starting", last

    def wait_up(self, timeout: float = 300.0, poll: float = 1.0) -> bool:
        """Block until up, crashed, or out of time. For scripts, not pages --
        a UI polls `status` from a timer instead."""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            state, _ = self.status()
            if state == "up":
                return True
            if state in ("crashed", "stopped"):
                return False
            time.sleep(poll)
        return False
