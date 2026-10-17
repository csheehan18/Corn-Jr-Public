"""Push to talk: a key that is held, and a microphone that is open while it is.

**Why push-to-talk is V1 and not a stepping stone to something better.** VISION
§3 budgets 50-150ms for endpointing and calls it "sneakily the hardest part" of
the whole round trip. A finger does it in zero, perfectly, every time, and it
also settles the privacy question the design's other half raises: a microphone
that opens when a key goes down is a microphone a person can see the state of.
Wake words and always-listening are `docs/PLAN-VOICE.md` §10's, and they are
parked as decisions rather than as work not yet done.

**The hotkey is `ctypes` and thirty lines rather than a library, and that is
`protocol.py`'s rule applied here.** `keyboard` and `pynput` both work and both
are one more thing a person hosting their own Corn-Jr has to install correctly
before he says a word. `GetAsyncKeyState` is in `user32`, needs no elevation,
works when the terminal is not focused, and is a syscall in a poll loop that
does nothing else.

**The cost is real and is not hidden: the hook does not swallow the key.**
`GetAsyncKeyState` reads the keyboard without consuming it, so whatever has
focus receives the keypress too. That is why the default is `F9` -- a function
key nothing binds -- and why `--hotkey enter` exists: the console fallback has
no global hook at all, takes Enter to open the microphone and Enter to close
it, and is the right choice for anyone who would rather not have a program
watching their keyboard. It is also what `scripts/check_voice.py` drives,
because a guard cannot press a key.

**The capture callback appends and does nothing else.** Work in an audio
callback drops frames, and a dropped frame is a transcription defect that
presents as the model mishearing -- a whole afternoon of looking in the wrong
file.
"""

from __future__ import annotations

import ctypes
import sys
import threading
import time
from collections import deque
from typing import Protocol

import numpy as np

from .config import POLL_MS, SAMPLE_RATE, VoiceConfig

# The keys a hotkey name can be. Windows virtual-key codes; the names are what
# a person would write in `voice.json`. Deliberately short -- a table of 200
# would be a table nobody checked, and these are the keys that make sense for
# a hold-to-talk that does not swallow.
VK = {
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75,
    "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A,
    "f12": 0x7B, "f13": 0x7C, "f14": 0x7D, "f15": 0x7E,
    "scrolllock": 0x91, "pause": 0x13, "capslock": 0x14,
    "lctrl": 0xA2, "rctrl": 0xA3, "lshift": 0xA0, "rshift": 0xA1,
    "lalt": 0xA4, "ralt": 0xA5, "insert": 0x2D, "home": 0x24, "end": 0x23,
    "pageup": 0x21, "pagedown": 0x22, "numlock": 0x90, "apps": 0x5D,
    "space": 0x20, "tab": 0x09, "backtick": 0xC0,
}


class PushToTalk(Protocol):
    """The seam: block until the key goes down, then until it comes up."""

    label: str

    def wait_down(self) -> bool: ...
    def wait_up(self) -> None: ...


class KeyHold:
    """A global key, polled. Windows only -- see the module docstring."""

    def __init__(self, key: str):
        name = key.lower().replace(" ", "").replace("_", "")
        if name not in VK:
            raise SystemExit(f"unknown hotkey {key!r}. Known: "
                             f"{', '.join(sorted(VK))}, or 'enter' for the "
                             f"console fallback")
        if not sys.platform.startswith("win"):
            raise SystemExit("the global hotkey is Windows only; "
                             "use --hotkey enter elsewhere")
        self.vk = VK[name]
        self.label = key.upper()
        self.user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        self.stop = threading.Event()

    def _down(self) -> bool:
        # The high bit is "currently down". The low bit -- "was pressed since
        # the last call" -- is deliberately not used: it is a latch, and a
        # latch would make a key tapped during the previous turn open the
        # microphone for this one.
        return bool(self.user32.GetAsyncKeyState(self.vk) & 0x8000)

    def wait_down(self) -> bool:
        """True when the key went down. False if the client is shutting down.

        **Waits for the key to be released first.** Otherwise a key still held
        from the previous turn -- which is what a long reply plus an impatient
        finger produces -- would open the microphone again the instant the last
        one closed.
        """
        while self._down():
            if self.stop.wait(POLL_MS / 1000):
                return False
        while not self._down():
            if self.stop.wait(POLL_MS / 1000):
                return False
        return True

    def wait_up(self) -> None:
        while self._down():
            if self.stop.wait(POLL_MS / 1000):
                return


class EnterHold:
    """Enter to open the microphone, Enter to close it.

    The fallback, and the only one a guard or a headless host can drive. Not a
    lesser mode: it is push-to-talk with a longer key, and it is the honest
    choice on a machine where a global keyboard hook is not welcome.
    """

    label = "ENTER"

    def __init__(self, prompt_in: str = "  [enter] talk  ",
                 prompt_out: str = "  listening -- [enter] to send  "):
        self.prompt_in = prompt_in
        self.prompt_out = prompt_out

    def wait_down(self) -> bool:
        try:
            line = input(self.prompt_in)
        except (EOFError, KeyboardInterrupt):
            return False
        # A typed word is a way out of the loop without a keyboard interrupt,
        # which matters when the terminal is the only interface there is.
        return line.strip().lower() not in ("q", "quit", "/quit", "exit")

    def wait_up(self) -> None:
        try:
            input(self.prompt_out)
        except (EOFError, KeyboardInterrupt):
            pass


class Scripted:
    """A fixed number of presses, for `scripts/check_voice.py`."""

    label = "SCRIPTED"

    def __init__(self, presses: int, hold_s: float = 0.0):
        self.left = presses
        self.hold_s = hold_s

    def wait_down(self) -> bool:
        if self.left <= 0:
            return False
        self.left -= 1
        return True

    def wait_up(self) -> None:
        if self.hold_s:
            time.sleep(self.hold_s)


def build_hotkey(cfg: VoiceConfig) -> PushToTalk:
    if cfg.hotkey.lower() in ("enter", "return", "console"):
        return EnterHold()
    return KeyHold(cfg.hotkey)


# How much audio from *before* the key went down is kept. A person starts
# speaking as they press, not after, and 300ms is the difference between "note
# down buy milk" and "ote down buy milk" -- a transcription defect that
# presents as the model mishearing, which is the failure this whole file is
# arranged to avoid. It is also what the always-running stream below is *for*.
PREROLL_MS = 300


class Microphone:
    """Collecting while the key is down, discarding the rest of the time.

    16kHz mono float32 -- whisper's native format, so this client never
    resamples and never owns a resampler bug. A resampler is a dependency, a
    latency cost, and a class of defect that presents as the model mishearing.

    **The stream stays open for the sitting and that is a disclosure, not an
    implementation detail.** Starting and stopping a `PortAudio` stream around
    each key press costs tens of milliseconds at the front of the clip, which
    is exactly where the first syllable is. So the device is acquired once and
    the callback throws samples away unless the key is down -- which means the
    operating system's microphone indicator is on for the whole session even
    though nothing is being kept. Anyone who would rather that were not true
    should run the client only when they intend to talk; there is no third
    option that also keeps the first word.

    What the always-running stream buys back is `PREROLL_MS`: the last 300ms
    before the key went down is prepended, so pressing slightly late costs
    nothing.
    """

    def __init__(self, cfg: VoiceConfig):
        import sounddevice as sd  # optional; the pure half does not need it

        self.sd = sd
        self.cfg = cfg
        self.device = resolve_device(sd, cfg.input_device)
        self.max_frames = cfg.max_speech_s * SAMPLE_RATE
        self.preroll_frames = PREROLL_MS * SAMPLE_RATE // 1000
        self._chunks: list[np.ndarray] = []
        self._frames = 0
        self._overran = False
        self._collect = False
        # The rolling pre-roll, kept whether or not the key is down and never
        # longer than `preroll_frames`. `deque` rather than a list so trimming
        # it in the callback is O(1) at the front.
        self._pre: deque[np.ndarray] = deque()
        self._pre_frames = 0
        self._lock = threading.Lock()
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="float32",
            device=self.device, callback=self._on_audio,
        )
        self.stream.start()
        self.name = _device_name(sd, self.device)

    def _on_audio(self, indata, frames, time_info, status) -> None:
        # Appends, or drops. Nothing else. See the module docstring.
        block = indata[:, 0].copy()
        with self._lock:
            if not self._collect:
                self._pre.append(block)
                self._pre_frames += frames
                # **Trimmed by slicing the front block, not by dropping it.**
                # A host that hands over blocks bigger than the window -- some
                # WASAPI configurations do -- would otherwise pop the only
                # block it has and leave the pre-roll permanently empty, which
                # is the buffer silently not existing rather than being short.
                while self._pre_frames > self.preroll_frames:
                    head = self._pre[0]
                    excess = self._pre_frames - self.preroll_frames
                    if len(head) <= excess:
                        self._pre.popleft()
                        self._pre_frames -= len(head)
                    else:
                        self._pre[0] = head[excess:]
                        self._pre_frames -= excess
                return
            # **The ceiling is sliced, not merely stopped at.** Refusing only
            # the block *after* the limit lets the block that crosses it in
            # whole, so `max_speech_s` would be a ceiling the buffer is allowed
            # to sail past by one block -- harmless at 1,024 frames and not
            # harmless on a host that hands over seconds at a time.
            room = self.max_frames - self._frames
            if room <= 0:
                self._overran = True
                return
            if len(block) > room:
                self._chunks.append(block[:room])
                self._frames += room
                self._overran = True
                return
            self._chunks.append(block)
            self._frames += frames

    def open(self) -> None:
        """Start collecting, beginning `PREROLL_MS` before now."""
        with self._lock:
            self._chunks = list(self._pre)
            self._frames = self._pre_frames
            self._pre.clear()
            self._pre_frames = 0
            self._overran = False
            self._collect = True

    def close(self) -> tuple[np.ndarray, bool]:
        """Stop collecting; return (samples, whether the ceiling was hit)."""
        with self._lock:
            self._collect = False
            chunks, overran = self._chunks, self._overran
            self._chunks, self._frames = [], 0
        if not chunks:
            return np.zeros(0, dtype=np.float32), overran
        return np.concatenate(chunks), overran

    def shutdown(self) -> None:
        try:
            self.stream.stop()
            self.stream.close()
        except Exception:
            pass


def resolve_device(sd, want) -> int | None:
    """An index, a name substring, or `None` for the system default."""
    if want is None or want == "":
        return None
    if isinstance(want, int) or str(want).isdigit():
        return int(want)
    needle = str(want).lower()
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] > 0 and needle in d["name"].lower():
            return i
    raise SystemExit(f"no input device matching {want!r} -- "
                     f"`python -m harness.voice --devices` lists them")


def _device_name(sd, index) -> str:
    try:
        return sd.query_devices(index if index is not None
                                else sd.default.device[0])["name"]
    except Exception:
        return "default"


def print_devices() -> None:
    """What the machine has, for `--devices`. The one command that needs no
    server, no model and no key."""
    import sounddevice as sd

    default_in = sd.default.device[0]
    print("input devices (--input-device takes an index or a name substring)")
    for i, d in enumerate(sd.query_devices()):
        if d["max_input_channels"] <= 0:
            continue
        mark = " *" if i == default_in else "  "
        print(f"{mark}{i:>3}  {d['name']}  "
              f"({d['max_input_channels']}ch, {d['default_samplerate']:.0f}Hz)")
