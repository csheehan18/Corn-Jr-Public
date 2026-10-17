"""Words out. Four adapters behind one seam, and none of them is a service.

**Local, on the same rule the transcriber is held to.** No cloud voice, no
audio leaving the machine, and the reply -- which is the half of a conversation
that quotes a person's notes back at them -- never becomes an HTTP body.

**The default needs nothing installed, and that is why it is the default.**
`protocol.py`'s standing rule is that every dependency this package carries is
one a person hosting their own Corn-Jr has to install correctly before he says
a word. `System.Speech.Synthesis` is on every Windows 10 box; Piper is the
better voice and needs an `.onnx` downloaded first, which is a default that
does not work on the machine it ships to. So Piper is opt-in and SAPI is what
happens when nothing was configured.

**SAPI is driven out of a resident PowerShell, and the residency is the whole
trick.** `Add-Type -AssemblyName System.Speech` measured 272ms; a process per
utterance would spend §3's entire round-trip budget booting a runtime. One
process for the sitting spends it once. Text crosses on stdin **base64
encoded**, so no apostrophe, quote, dollar sign or non-ASCII character in a
reply can be parsed as part of the command -- the same class of bug
`protocol.py` refuses embedded newlines for, and a reply is exactly the kind of
string that eventually contains all four.

**It synthesises to a wave file and plays it here, rather than speaking to the
default device, and that buys an honest number.** `SpeechSynthesizer.Speak`
returns when it decides it is done and gives a caller nothing to timestamp;
worse, on a host where the process has no audio endpoint it returns
*immediately and silently*, which is a pipeline that measures as fast because
it is not working. Rendering to a file and playing it through `sounddevice`
means the first-audio mark is the moment this process starts a stream, the
failure is loud, and playback shares the audio stack the microphone is already
using. Measured on this machine: 102ms for the first utterance, 21ms after,
22.05kHz mono -- inside §3's 50-150ms budget for the stage it calls one of the
two real bottlenecks.

    sapi         resident PowerShell -> wav -> sounddevice   first-chunk
    sapi-direct  resident PowerShell -> the default device   handoff
    piper        piper-tts -> pcm -> sounddevice             first-chunk
    pyttsx3      whatever pyttsx3 is wired to                 handoff
    silent       printed, not spoken                          none

`tts_measure` on every row says which of those two a number is, so a streaming
adapter's figures are never quietly compared against a handoff. Calling a
handoff "time to first audio" is how a pipeline gets measured as faster than it
is.
"""

from __future__ import annotations

import base64
import io
import subprocess
import tempfile
import time
import wave
from pathlib import Path
from typing import Protocol

import numpy as np

from .config import VoiceConfig

# `auto` walks this, taking the first that builds. Piper is first because it is
# the better voice when somebody has gone to the trouble of a model file, and
# `silent` is last because a client that says nothing is still a client that
# works -- a person can read the reply.
ORDER = ("piper", "sapi", "pyttsx3", "silent")


class Voice(Protocol):
    """The seam. `speak` starts audio and returns; `wait` blocks for the end."""

    name: str
    measure: str

    def speak(self, text: str) -> None: ...
    def wait(self) -> None: ...
    def close(self) -> None: ...


class Silent:
    """Says nothing, records everything. The guard's synthesiser, and `--tts
    silent` for anyone who wants the transcript without the noise."""

    name = "silent"
    measure = "none"

    def __init__(self) -> None:
        self.said: list[str] = []

    def speak(self, text: str) -> None:
        self.said.append(text)

    def wait(self) -> None:
        pass

    def close(self) -> None:
        pass


class Player:
    """Plays PCM through `sounddevice`, and knows when it stopped.

    Shared by the two adapters that render audio rather than speaking it, so
    "first audio" means the same instant for both.
    """

    def __init__(self) -> None:
        import sounddevice as sd  # optional; see the module docstring
        self.sd = sd
        self.until = 0.0

    def play(self, samples: np.ndarray, rate: int) -> None:
        """Start audio. **Waits for whatever is already playing first.**

        `sounddevice.play` stops the current stream and starts the new one, so
        without this line a compound turn's second say would cut its first one
        off mid-word -- "Saved." replaced by "Ground types, apparently." before
        the first was audible. Blocking here is the right cost: the second
        sentence genuinely cannot start until the first has been said, and the
        stopwatch measuring it should report that rather than hide it.
        """
        self.sd.wait()
        self.sd.play(samples, rate)
        # When it will be finished, computed rather than waited for, so `wait`
        # can be called or not without changing what `speak` cost.
        self.until = time.perf_counter() + len(samples) / rate

    def wait(self) -> None:
        self.sd.wait()

    def stop(self) -> None:
        try:
            self.sd.stop()
        except Exception:
            pass


class _PowerShell:
    """One long-lived PowerShell with a `SpeechSynthesizer` in it.

    Everything sent is one line and every line acks, so the two ends stay in
    step without a length prefix -- `protocol.py`'s framing argument, applied
    to a pipe. A synthesiser that fell out of step would say the previous
    reply to the current turn, which is the worst failure this file has
    available.
    """

    BOOT = (
        "Add-Type -AssemblyName System.Speech",
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer",
    )

    def __init__(self, voice: str = "", rate: int = 0):
        self.proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        for line in self.BOOT:
            self._write(line)
        if rate:
            self._write(f"$s.Rate = {int(max(-10, min(10, rate)))}")
        if voice:
            # By substring, because the installed names are long and
            # machine-specific ("Microsoft Zira Desktop"). A miss leaves the
            # default voice rather than raising: the wrong voice is a
            # preference, and refusing to speak over it is not.
            enc = base64.b64encode(voice.encode("utf-8")).decode("ascii")
            self._write(
                f'$want = [Text.Encoding]::UTF8.GetString('
                f'[Convert]::FromBase64String("{enc}"));'
                f'$v = $s.GetInstalledVoices() | Where-Object '
                f'{{ $_.VoiceInfo.Name -like "*$want*" }} | Select-Object -First 1;'
                f'if ($v) {{ $s.SelectVoice($v.VoiceInfo.Name) }}'
            )
        self.ack("READY")

    def _write(self, line: str) -> None:
        assert self.proc.stdin is not None
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def send(self, line: str, token: str) -> None:
        self._write(f'{line}; "{token}"')

    def ack(self, token: str) -> None:
        """Emit the token and block until it comes back."""
        self._write(f'"{token}"')
        self.await_(token)

    def await_(self, token: str) -> None:
        assert self.proc.stdout is not None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                err = ""
                if self.proc.stderr is not None:
                    err = self.proc.stderr.read()[:400]
                raise RuntimeError(f"the speech host exited{': ' + err if err else ''}")
            if line.strip() == token:
                return

    @staticmethod
    def literal(text: str) -> str:
        """A PowerShell expression for `text`, immune to its contents."""
        enc = base64.b64encode(text.encode("utf-8")).decode("ascii")
        return (f'[Text.Encoding]::UTF8.GetString('
                f'[Convert]::FromBase64String("{enc}"))')

    def close(self) -> None:
        try:
            if self.proc.stdin is not None:
                self.proc.stdin.close()
            self.proc.wait(timeout=3)
        except Exception:
            self.proc.kill()


class Sapi:
    """The default. Renders to a wave file, plays it here. See the docstring."""

    name = "sapi"
    measure = "first-chunk"

    def __init__(self, cfg: VoiceConfig):
        self.ps = _PowerShell(cfg.tts_voice, cfg.tts_rate)
        self.player = Player()
        self.dir = Path(tempfile.mkdtemp(prefix="cornjr-voice-"))
        self.n = 0

    def speak(self, text: str) -> None:
        self.n += 1
        out = self.dir / f"say{self.n}.wav"
        # `SetOutputToNull` is what closes and flushes the file; without it the
        # wave header is never finalised and the read below gets a truncated
        # file that plays as a click.
        self.ps.send(
            f'$s.SetOutputToWaveFile("{out}"); '
            f'$s.Speak({self.ps.literal(text)}); '
            f'$s.SetOutputToNull()', "SPOKE")
        self.ps.await_("SPOKE")
        samples, rate = read_wav(out)
        self.player.play(samples, rate)
        try:
            out.unlink()
        except OSError:
            pass

    def wait(self) -> None:
        self.player.wait()

    def close(self) -> None:
        self.player.stop()
        self.ps.close()


class SapiDirect:
    """SAPI straight to the default output device.

    For a host where `sounddevice` cannot open an output stream. It is honest
    about what it measures and that is the reason it is not the default: on a
    process with no audio endpoint, `Speak` returns immediately and silently,
    so this adapter can report a 17ms "time to speech" for a turn nobody heard.
    """

    name = "sapi-direct"
    measure = "handoff"

    def __init__(self, cfg: VoiceConfig):
        self.ps = _PowerShell(cfg.tts_voice, cfg.tts_rate)
        self.ps.send("$s.SetOutputToDefaultAudioDevice()", "OUT")
        self.ps.await_("OUT")
        self.pending = False

    def speak(self, text: str) -> None:
        self.ps.send(f'$s.SpeakAsync({self.ps.literal(text)}) | Out-Null',
                     "QUEUED")
        self.ps.await_("QUEUED")
        self.pending = True

    def wait(self) -> None:
        if self.pending:
            self.ps.send("while ($s.State -ne 'Ready') "
                         "{ Start-Sleep -Milliseconds 20 }", "IDLE")
            self.ps.await_("IDLE")
            self.pending = False

    def close(self) -> None:
        self.ps.close()


class Piper:
    """The better voice, when somebody has put a model on disk.

    Synthesises to 16-bit PCM at the model's own rate and plays it through the
    same `Player` the SAPI path uses, so `first-chunk` means one instant in
    both. Streaming it chunk by chunk is `docs/PLAN-VOICE.md` §10's -- V1
    renders the whole utterance, because a stream that can be interrupted is
    barge-in and barge-in needs a cancel the protocol does not have.
    """

    name = "piper"
    measure = "first-chunk"

    def __init__(self, cfg: VoiceConfig):
        from piper import PiperVoice  # optional

        if not cfg.piper_model:
            raise ImportError("no piper model configured")
        self.voice = PiperVoice.load(cfg.piper_model)
        self.player = Player()
        self.rate = getattr(getattr(self.voice, "config", None),
                            "sample_rate", 22050)

    def speak(self, text: str) -> None:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            self.voice.synthesize(text, w)
        buf.seek(0)
        samples, rate = read_wav(buf)
        self.player.play(samples, rate)

    def wait(self) -> None:
        self.player.wait()

    def close(self) -> None:
        self.player.stop()


class Pyttsx3:
    """The third path, used if it happens to be installed. Not a dependency."""

    name = "pyttsx3"
    measure = "handoff"

    def __init__(self, cfg: VoiceConfig):
        import pyttsx3  # optional

        self.engine = pyttsx3.init()
        if cfg.tts_voice:
            for v in self.engine.getProperty("voices"):
                if cfg.tts_voice.lower() in v.name.lower():
                    self.engine.setProperty("voice", v.id)
                    break
        if cfg.tts_rate:
            base = self.engine.getProperty("rate")
            self.engine.setProperty("rate", base + cfg.tts_rate * 10)

    def speak(self, text: str) -> None:
        self.engine.say(text)

    def wait(self) -> None:
        self.engine.runAndWait()

    def close(self) -> None:
        try:
            self.engine.stop()
        except Exception:
            pass


def read_wav(source) -> tuple[np.ndarray, int]:
    """A 16-bit PCM wave file as float32 in [-1, 1], plus its rate.

    Stdlib `wave` rather than `soundfile`: SAPI and Piper both write plain
    16-bit PCM and a fourth dependency to read a format Python already reads
    would be one more thing to install before he says a word.
    """
    with wave.open(str(source) if isinstance(source, Path) else source,
                   "rb") as w:
        rate = w.getframerate()
        width = w.getsampwidth()
        channels = w.getnchannels()
        raw = w.readframes(w.getnframes())
    if width != 2:
        raise ValueError(f"expected 16-bit PCM, got {width * 8}-bit")
    samples = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    if channels > 1:
        samples = samples.reshape(-1, channels)
    return samples, rate


def build(cfg: VoiceConfig) -> Voice:
    """The configured voice, or the first in `ORDER` that builds.

    A named adapter that cannot be built is an error, because the person asked
    for it. `auto` falling through to the next is not an error, because the
    person asked for whatever works.
    """
    named = {"piper": Piper, "sapi": Sapi, "sapi-direct": SapiDirect,
             "pyttsx3": Pyttsx3, "silent": lambda _cfg: Silent()}
    if cfg.tts != "auto":
        if cfg.tts not in named:
            raise SystemExit(f"unknown --tts {cfg.tts!r}: {sorted(named)}")
        return named[cfg.tts](cfg)
    for name in ORDER:
        try:
            return named[name](cfg)
        except Exception as exc:
            print(f"  ({name} unavailable: {type(exc).__name__}: {exc})")
    return Silent()
