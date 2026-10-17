"""The loop: hold a key, speak, hear an answer.

**The turn itself is `Sitting.turn`, and it takes audio rather than a
microphone.** That is the whole reason `scripts/check_voice.py` can drive a
complete turn -- transcript through spoken output, against a real socket
speaking the real protocol -- on a machine with no microphone, no speakers and
no model. Everything hardware-shaped is in the loop that calls it.

**It is a thin client and it stays one.** Nothing here knows what a tool is,
what the fold does, or which say the runtime wrote. It sends `{"op": "turn"}`
and renders what comes back, exactly as `harness/client.py` does -- and if a
voice client ever needed more than that, `harness/protocol.py`'s own standard
says the protocol got too complicated rather than that this file needs to grow.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_v4/ckpt.pt
    python -m harness.voice
    python -m harness.voice --hotkey enter --stt-model tiny.en
    python -m harness.voice --devices
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime

import numpy as np

from ..client import Client
from . import audio as audio_mod
from . import stt as stt_mod
from . import surface, tts as tts_mod
from .config import SAMPLE_RATE, ConfigError, VoiceConfig, add_arguments
from .latency import Stopwatch
from .speech import Utterance
from .voicelog import VoiceLog, link_to, voice_record


class Sitting:
    """One connection, one transcriber, one voice, one log.

    Holds no audio device: `turn` takes samples. See the module docstring.
    """

    def __init__(self, client: Client, transcriber, voice, log: VoiceLog,
                 cfg: VoiceConfig, server_log: str = ""):
        self.client = client
        self.stt = transcriber
        self.voice = voice
        self.log = log
        self.cfg = cfg
        self.server_log = server_log
        self.turns = 0

    # -- one turn -----------------------------------------------------------

    def turn(self, samples: np.ndarray, watch: Stopwatch,
             clock=time.perf_counter) -> dict | None:
        """Audio in, a spoken answer out, a row back. `None` if nothing was said.

        The clock is an argument so the guard can step a turn through with a
        fake one -- `harness/voice/latency.py`'s argument, applied to the
        caller as well as to the stopwatch.
        """
        audio_ms = len(samples) / SAMPLE_RATE * 1000

        heard = self.stt.transcribe(samples, SAMPLE_RATE)
        watch.mark("stt_done", clock())
        text = heard.text
        if not text.strip():
            out(f"  (nothing heard in {audio_ms / 1000:.1f}s)")
            return None

        # **What the transcriber emitted, printed before anything else touches
        # it, and nothing else does touch it.** See `stt.py`: the mark on the
        # end of this string is worth 18/24 against 1/24 on the date tool, and
        # a client that tidied it would delete a signal 2.27M corpus rows paid
        # for.
        out(f"> {text}")

        said = Utterance()
        server: dict = {"ms": None, "outcome": None, "author": None,
                        "fell_back": None, "calls": [], "error": None,
                        "folded": None}
        when = datetime.now().astimezone()
        watch.mark("sent", clock())
        for ev in self.client.request(op="turn", user=text):
            kind = ev.get("t")
            if kind in ("text", "say"):
                watch.mark("first", clock())
            if kind == "waiting":
                out("  (queued behind another turn)")
            elif kind == "say":
                self._say(ev, said, watch, server, clock)
            elif kind == "call":
                mark = "" if ev.get("ok") else f"  !! {ev.get('why')}"
                out(f"  -> {ev.get('raw')}{mark}")
                server["calls"].append({"name": ev.get("name"),
                                        "ok": bool(ev.get("ok")),
                                        "author": ev.get("author") or "model"})
            elif kind == "obs":
                out(f"  <- {json.dumps(ev.get('payload'))}")
            elif kind == "fold":
                # Printed for the same reason `harness/client.py` prints it:
                # the model answered a turn the user did not quite say, and a
                # client that hid that would make the one runtime intervention
                # nobody watching can see.
                out(f"  ~~ folded {ev.get('raw')!r} -> {ev.get('folded')!r}")
                server["folded"] = ev.get("folded")
            elif kind == "rejected":
                out(f"  !! not executed -- {ev.get('why')}")
            elif kind == "error":
                out(f"  !! {ev.get('why')}")
                server["error"] = ev.get("why")
            elif kind == "done":
                watch.mark("done", clock())
                server["ms"] = ev.get("ms")
                server["outcome"] = ev.get("outcome")

        if said.silent():
            # **Said on screen and not through the speakers.** A turn that fell
            # out of the vocabulary and a turn that had nothing to say look
            # identical from a chair; the difference matters and the row keeps
            # it.
            why = ("every say was markers" if said.emptied
                   else "no say in the turn")
            out(f"  (silence -- {why})")
        else:
            self.voice.wait()
            watch.mark("tts_done", clock())

        self.turns += 1
        return self._record(text, heard, audio_ms, watch, said, server, when)

    def _say(self, ev: dict, said: Utterance, watch: Stopwatch,
             server: dict, clock) -> None:
        """One `say` event: sanitise, dedupe, speak, print.

        **Spoken as it arrives rather than at `done`.** A compound turn says a
        thing per tool, and holding the first sentence until the second tool
        returns would spend the whole of §3's budget waiting for a sentence
        already in hand.
        """
        server["author"] = ev.get("author") or server["author"]
        if ev.get("fell_back"):
            server["fell_back"] = ev.get("fell_back")
        speak = said.add(ev.get("text", ""))
        if not speak:
            return
        watch.mark("first_say", clock())
        tag = "  (deferred to the tool)" if ev.get("deferred") else ""
        out(f"  {speak}{tag}")
        try:
            self.voice.speak(speak)
        except Exception as exc:
            # A synthesiser that fails must not take the turn with it: the
            # answer is already on screen, and `harness/sessionlog.py` makes
            # the same argument about a log append after the reply has gone.
            out(f"  !! the voice failed ({type(exc).__name__}: {exc})")
            return
        watch.mark("tts_start", clock())

    def _record(self, text: str, heard, audio_ms: float, watch: Stopwatch,
                said: Utterance, server: dict, when: datetime) -> dict:
        link, why = (None, "join disabled")
        if self.cfg.join_server_log:
            link, why = link_to(self.server_log, text, when)
        stt_card = dict(self.cfg.stt_card())
        stt_card.update({"backend": self.stt.name, "segments": heard.segments,
                         "logprob": heard.logprob})
        row = voice_record(
            user=text,
            stages=watch.all_ms(),
            surface=surface.read(text).as_dict(),
            stt=stt_card,
            tts={"backend": self.voice.name, "measure": self.voice.measure},
            said={"text": said.whole(), "n": len(said.spoken),
                  "skipped": said.skipped, "emptied": said.emptied,
                  "marker_strikes": said.strikes,
                  "markers": said.markers[:8]},
            server=server,
            link=link, link_why=why, audio_ms=audio_ms, when=when,
        )
        self.log.append(row)
        return row


def out(text: str = "") -> None:
    print(text, flush=True)


def _console() -> None:
    """A reply the console cannot render must not end the conversation.

    `harness/client.py`'s finding, and it applies here for a second reason: a
    synthesiser handles a character a cp1252 terminal cannot, so a voice client
    would die printing a reply it had already said out loud.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main() -> int:
    _console()
    ap = argparse.ArgumentParser(description=__doc__)
    add_arguments(ap)
    ap.add_argument("--devices", action="store_true",
                    help="list input devices and exit; needs no server")
    args = ap.parse_args()

    if args.devices:
        audio_mod.print_devices()
        return 0

    try:
        cfg = VoiceConfig.load(args.config).override(args)
    except ConfigError as exc:
        print(f"configuration: {exc}", file=sys.stderr)
        return 2

    try:
        client = Client(cfg.host, cfg.port)
    except (ConnectionRefusedError, OSError):
        print(f"nothing listening on {cfg.host}:{cfg.port} -- "
              f"start it with `python -m harness.server`", file=sys.stderr)
        return 1

    server_log = ""
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            server_log = ev.get("log") or ""
            out(f"{ev.get('ckpt', '?')} -- {ev.get('params', 0):,} params, "
                f"{len(ev.get('tools') or [])} tools")
            out(f"  (recording turns to {server_log})" if server_log
                else "  (server is not recording; --no-log)")

    out(f"  loading {cfg.stt_model} on {cfg.stt_device}/{cfg.stt_compute}...")
    transcriber = stt_mod.build(cfg)
    out(f"  ready in {getattr(transcriber, 'load_ms', 0):.0f}ms")
    voice = tts_mod.build(cfg)
    hotkey = audio_mod.build_hotkey(cfg)
    mic = audio_mod.Microphone(cfg)
    log = VoiceLog(cfg.log if cfg.logging else None)

    out(f"  mic: {mic.name}")
    out(f"  voice: {voice.name} ({voice.measure} timing)")
    out(f"  rows: {log.path if log.path else 'not recorded (--no-log)'}")
    out(f"  hold {hotkey.label} to talk. Ctrl-C to leave.")
    out()

    sitting = Sitting(client, transcriber, voice, log, cfg, server_log)
    try:
        while True:
            if not hotkey.wait_down():
                break
            watch = Stopwatch()
            watch.mark("key_down", time.perf_counter())
            mic.open()
            hotkey.wait_up()
            watch.mark("key_up", time.perf_counter())
            samples, overran = mic.close()
            held_ms = watch.ms("spoke") or 0.0
            if overran:
                out(f"  (held past the {cfg.max_speech_s}s ceiling; "
                    f"the tail was dropped)")
            if held_ms < cfg.min_speech_ms:
                out(f"  (tap, not a turn -- {held_ms:.0f}ms)")
                continue
            row = sitting.turn(samples, watch)
            if row is not None:
                out(watch.line(voice.measure))
            out()
    except KeyboardInterrupt:
        out()
    finally:
        mic.shutdown()
        voice.close()
        client.close()
        if log.path:
            out(f"  {log.rows} voice turn(s) in {log.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
