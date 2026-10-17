"""A thin client, which is what §4 says every client should be.

Two things at once, on purpose. It is the REPL you talk to Corn-Jr through when
the server is up, and it is the reference implementation of `protocol.py` --
about eighty lines of `socket` and `readline`, no framework, no async. If a
voice client or a phone client ever needs more than this to speak the protocol,
the protocol got too complicated.

It prints time-to-first-token as well as total, because those are different
budgets in VISION §3 and a client that reported only the total would hide the
one the user actually feels. Nothing about the wait matters to someone who has
already started hearing an answer.

It keeps a copy of everything it prints, so `/saved` can drop the whole
conversation into `Saved Sessions/` in the shape those files are already in --
terminal copy-paste, which is how every one of them got there until now.

Usage:
    python -m harness.client
    python -m harness.client --ask "note down buy milk"
    python -m harness.client --port 8765

Commands: /reset  /doc <path>  /doc off  /saved  /quit
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
from pathlib import Path

from .protocol import DEFAULT_HOST, DEFAULT_PORT, encode

# **The event that ends each request**, one per op plus `error`. A module
# constant because a new op whose reply is missing here is a client that waits
# forever on an answer it already has -- `window` did exactly that on its first
# run -- and `scripts/check_server.py` asserts every op the server answers ends
# on something in this set.
ENDS = ("done", "error", "pong", "info", "reset", "doc", "window")

# **The model can say anything, and a Windows console cannot print it.**
# `en.wikipedia.org` answered "who the ceo of nvidia" with Jensen Huang's name
# in Chinese, Wade-Giles and Tai-lo; the default cp1252 stdout raised
# `UnicodeEncodeError` and took the whole client down mid-turn. Nothing about a
# reply the user cannot render should end the conversation, so the console gets
# told to substitute rather than raise. The saved transcript is written
# separately, as UTF-8, and keeps the real characters.
#
# **At import, not inside `main()`, which is where the seventy-eighth finding
# found it.** `Client` and `run_turn` are the reusable half of this module and
# every other entry point reaches them without going through the argument
# parser -- `harness/checkup.py`, a notebook, anything embedding a turn loop.
# Scoped to `main()` the guard protected the CLI and left every one of those
# importers holding the exact exception it exists to prevent; the audit hit it
# on `złoty`. A module-level side effect is the cost, and it is the right one
# here: the alternative is each embedder remembering to repeat this, which is
# the failure mode again with more places to forget it.
def _printable_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):  # not a real console; nothing to fix
            pass


_printable_console()

# Printed in front of a `say` this client renders itself, so a saved transcript
# is the same shape whether the words were streamed or handed over whole.
D_SAY = "<|say|>"

# Markers are part of the streamed transcript and never part of the spoken
# string, so they come off before the two are compared.
_MARKER = re.compile(r"<\|[a-z]+\|>")


# **The trailing marker a model-written reply streams and a pool line does
# not** (PLAN-CONVERSATION 4e). `<|end|>` and `<|endoftext|>` arrive on the
# `text` events, possibly split across two of them, and are part of the
# transcript rather than of the sentence. Stripped here at the client, never at
# the server: the transcript is the record and the `say` event is already the
# spoken string. `_Tail` holds back the longest suffix that could still turn
# out to be a marker, prints everything before it, and drops a completed one.
_STOPS = ("<|end|>", "<|endoftext|>")


class _Tail:
    def __init__(self) -> None:
        self.held = ""

    def feed(self, text: str) -> str:
        """The part of `held + text` that is safe to print now."""
        buf = self.held + text
        for stop in _STOPS:
            if stop in buf:
                buf = buf.split(stop, 1)[0]
                self.held = ""
                return buf
        keep = 0
        for n in range(min(len(buf), max(map(len, _STOPS)) - 1), 0, -1):
            if any(stop.startswith(buf[-n:]) for stop in _STOPS):
                keep = n
                break
        self.held = buf[len(buf) - keep:] if keep else ""
        return buf[:len(buf) - keep] if keep else buf

    def flush(self) -> str:
        out, self.held = self.held, ""
        return out


def _content(text: str) -> str:
    """The words, with nothing that only affects how they are punctuated.

    `tidy_say` closes a reply that `say_cut` stopped mid-clause, so the
    authoritative string is routinely the streamed one plus a full stop. That is
    not a different reply and must not be printed as though it were.
    """
    return re.sub(r"[^a-z0-9]", "", _MARKER.sub("", text).lower())

# Next to the repo, not next to this module -- these are conversations, not code.
SAVE_DIR = Path(__file__).resolve().parents[1] / "Saved Sessions"

# Every line this client prints, in order. A transcript is the only artefact of
# a turn that survives it: the server keeps history, but not what the wait or
# the masked-token counts looked like from here.
_transcript: list[str] = []
_saved_path: Path | None = None
# What the server said it is logging to, learned from `info` at connect. Empty
# when the server is running `--no-log`, which is a thing the person talking to
# it should be told rather than left to assume either way.
_log_path: str = ""


def out(text: str = "", end: str = "\n", err: bool = False) -> None:
    """Print it, and keep a copy for `/saved`."""
    print(text, end=end, flush=True, file=sys.stderr if err else sys.stdout)
    _transcript.append(text + end)


def save_transcript() -> Path:
    """Write everything printed so far to `Saved Sessions/sessionN.txt`.

    The same file for the rest of the session, so a second `/saved` is an
    update rather than a near-duplicate of the same conversation one turn on.
    """
    global _saved_path
    SAVE_DIR.mkdir(exist_ok=True)
    if _saved_path is None:
        n = 1
        while (SAVE_DIR / f"session{n}.txt").exists():
            n += 1
        _saved_path = SAVE_DIR / f"session{n}.txt"
    _saved_path.write_text("".join(_transcript), encoding="utf-8")
    return _saved_path


class Client:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.sock = socket.create_connection((host, port))
        # `makefile` so `readline` does the framing. The protocol is newline
        # delimited precisely so a client does not have to buffer by hand.
        self.rx = self.sock.makefile("rb")

    def send(self, **req) -> None:
        self.sock.sendall(encode(req))

    def events(self):
        for line in self.rx:
            if line.strip():
                yield json.loads(line)

    def request(self, **req):
        """Send, then yield events until the one that ends them.

        `done`, `error` and the bare acknowledgements all terminate. A client
        that only stopped on `done` would hang forever on a rejected frame,
        which is the failure mode worth not having in the reference client.
        """
        self.send(**req)
        for ev in self.events():
            yield ev
            if ev.get("t") in ENDS:
                return

    def close(self) -> None:
        self.rx.close()
        self.sock.close()


def run_turn(client: Client, text: str) -> None:
    sent = time.perf_counter()
    first: float | None = None
    spoke = False
    # What the `text` events have put on screen this turn, so the `say` event
    # can tell "the same words, whole" from "different words".
    streamed = ""
    tail = _Tail()
    for ev in client.request(op="turn", user=text):
        kind = ev.get("t")
        if kind == "waiting":
            out("  (queued behind another turn)", err=True)
        elif kind == "text":
            if first is None:
                first = (time.perf_counter() - sent) * 1000
            shown = tail.feed(ev["text"])
            if shown:
                out(shown, end="")
            streamed += ev["text"]
            spoke = True
        elif kind == "say":
            # **The authoritative string, and the only one a voice client should
            # ever speak.** Usually it is what the `text` events already
            # streamed, and reprinting it would double every reply -- so this
            # renders only when it differs, which is exactly the two cases the
            # runtime corrects. A deferred reply is never streamed at all (the
            # server mutes it rather than send words it is about to replace), and
            # a turn that would have ended in silence has nothing to double.
            said = ev.get("text", "")
            if said and _content(said) != _content(streamed):
                if first is None:
                    first = (time.perf_counter() - sent) * 1000
                tag = "  (deferred to the tool)" if ev.get("deferred") else ""
                out(f"{D_SAY}{said}{tag}", end="")
                spoke = True
        elif kind == "call":
            mark = "" if ev.get("ok") else f"  !! {ev.get('why')}"
            masked = f"  ~~ grammar masked {ev['masked']}" if ev.get("masked") else ""
            out(f"\n  -> {ev['raw']}{mark}{masked}")
        elif kind == "obs":
            out(f"  <- {json.dumps(ev['payload'])}")
        elif kind == "fold":
            # Present only when the utterance was changed on the way in -- see
            # `corn.agent.fold_turn`. Shown rather than swallowed because the
            # model answered a question the user did not quite type, and a
            # client that hid that would make the fold the one runtime
            # intervention nobody watching a sitting could see.
            out(f"  ~~ folded {ev.get('raw')!r} -> {ev.get('folded')!r}")
        elif kind == "rejected":
            out(f"  !! not executed -- {ev['why']}")
        elif kind == "error":
            out(f"  !! {ev['why']}", err=True)
        elif kind == "done":
            rest = tail.flush()
            if rest and not any(s.startswith(rest) for s in _STOPS):
                out(rest, end="")
            if spoke:
                out()
            ttft = f"{first:.0f}ms to first token, " if first is not None else ""
            out(f"  [{ttft}{ev['ms']:.0f}ms total]")


def main() -> None:
    global _log_path
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--ask", help="one turn, then exit")
    ap.add_argument("--info", action="store_true", help="what is loaded, then exit")
    args = ap.parse_args()

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- "
              f"start it with `python -m harness.server`", file=sys.stderr)
        raise SystemExit(1)

    try:
        if args.info:
            for ev in client.request(op="info"):
                print(json.dumps(ev, indent=2))
            return
        if args.ask:
            # The server keeps history across connections under `--multi`, so a
            # one-shot can land mid-conversation and inherit context it cannot
            # see -- measured 2026-08-29: an `--ask` after a search session
            # re-issued that session's query. The interactive client shows the
            # conversation; this is the only path that answers blind, so it is
            # the one that has to say so. A notice rather than a reset, because
            # the conversation belongs to whoever is having it, not to a
            # one-shot that dropped in.
            for ev in client.request(op="info"):
                if ev.get("t") == "info" and ev.get("turns"):
                    n = ev["turns"]
                    print(f"  (a conversation with {n} prior "
                          f"turn{'s' if n != 1 else ''} is in progress and he "
                          f"will answer within it; connect without --ask and "
                          f"/reset to start fresh)",
                          file=sys.stderr)
            run_turn(client, args.ask)
            return
        # The transcripts already in `Saved Sessions/` are pasted terminal, so
        # they open with the command that started them. Cheap to reproduce, and
        # it keeps a saved file indistinguishable from a pasted one.
        rest = " ".join(sys.argv[1:])
        _transcript.append(
            f"{os.getcwd()}>python -m harness.client{' ' + rest if rest else ''}\n"
        )
        for ev in client.request(op="info"):
            if ev.get("t") == "info":
                _log_path = ev.get("log") or ""
                out(f"{ev['ckpt']} -- {ev['params']:,} params, "
                    f"{len(ev['tools'])} tools. /quit to leave, /reset to forget, "
                    f"/doc <path> to hand him a file, /saved to keep.")
                if ev.get("doc"):
                    out(f"  (answering lookups from {ev['doc']['name']}, "
                        f"{ev['doc']['windows']} windows; /doc off to stop)")
                # Printed once, at the top, where a person deciding what to
                # say next can see it. A server that is recording should be
                # obvious from the client too and not only from the terminal
                # the server happens to be running in -- which on a LAN is a
                # different machine.
                out(f"  (recording turns to {_log_path})" if _log_path
                    else "  (not recording; --no-log)")
        while True:
            try:
                text = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if not text:
                continue
            # `input` printed the prompt, so echoing it into the transcript is
            # ours to do -- nothing else here ever sees what was typed.
            _transcript.append(f"> {text}\n")
            if text in ("/quit", "/exit"):
                return
            if text in ("/saved", "/save"):
                # **Two files, and they are not alternatives.** This one is
                # the sitting as a person reads it back. The server has been
                # appending the same turns as JSON since the first one, with
                # the provenance a transcript cannot carry, and a user who
                # thinks `/saved` is what keeps their conversation would treat
                # forgetting it as data loss -- which is exactly the habit
                # `harness/sessionlog.py` was written to make unnecessary.
                out(f"  (saved to {save_transcript()})")
                if _log_path:
                    out(f"  (structured turns already in {_log_path})")
                continue
            if text == "/reset":
                for _ in client.request(op="reset"):
                    pass
                # Only the server forgets. The transcript is the record of the
                # whole sitting, and a /reset partway through is part of it.
                out("  (history dropped)")
                continue
            if text == "/doc" or text.startswith("/doc "):
                # One document at a time; the newest load wins, `/doc off`
                # unloads. The path is opened by the *server*, which on a LAN
                # is a different machine -- the reply says what actually
                # loaded rather than this end assuming.
                arg = text[4:].strip()
                if not arg:
                    out("  usage: /doc <path on the server>  or  /doc off")
                    continue
                path = "" if arg == "off" else arg
                for ev in client.request(op="doc", path=path):
                    if ev.get("t") == "doc" and ev.get("ok"):
                        out(f"  (answering lookups from {ev['name']}, "
                            f"{ev['windows']} windows)" if ev.get("name")
                            else "  (document unloaded)")
                    elif ev.get("t") == "doc":
                        out(f"  !! {ev.get('why')}", err=True)
                    elif ev.get("t") == "error":
                        out(f"  !! {ev['why']}", err=True)
                continue
            run_turn(client, text)
    finally:
        client.close()


if __name__ == "__main__":
    main()
