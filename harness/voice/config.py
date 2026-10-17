"""Every knob, in one dataclass, with the defaults argued for where they sit.

**Three sources, and the precedence is fixed: defaults, then a JSON file, then
the command line.** A person tunes a voice client once and then uses it, so the
file is where the tuning lives; a flag is how you try something without editing
it. The order is the only one that lets both be true.

**Unknown keys in the file are refused rather than ignored.** A misspelt
`hotkey` that silently did nothing would present as "the hotkey does not work",
which is the failure mode that costs an evening. The same argument
`scripts/check_all.py` makes for `REQUIRES`: a thing nobody classified is a
thing nobody thought about.

The file is `voice.json` at the repo root by default, on `overlay.json`'s
precedent -- per-machine state, not part of the artefact. It is absent on a
fresh clone and that is a working configuration, which is the property that
matters: a voice client whose defaults do not work is a voice client that
cannot be tried.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from ..protocol import DEFAULT_HOST, DEFAULT_PORT

# Next to the repo, not next to this module -- it describes a machine, not the
# package. `.gitignore` should carry it beside `overlay.json`.
DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "voice.json"

# Whisper's native rate. The client captures at it so nothing here ever
# resamples: a resampler is a dependency, a latency cost and a class of bug
# that presents as the model mishearing.
SAMPLE_RATE = 16_000

# How often the push-to-talk poll asks whether the key is down. 15ms is under
# the ~30ms a fast key tap lasts and is invisible against §3's 500ms budget;
# the loop does nothing else, so the cost is a syscall.
POLL_MS = 15


class ConfigError(ValueError):
    """A configuration that cannot be run, said once and plainly."""


@dataclass
class VoiceConfig:
    """What the client is wired to. Every field is a flag and a JSON key."""

    # -- the server ---------------------------------------------------------
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT

    # -- push to talk -------------------------------------------------------
    # **F9 because the hook does not swallow it.** `GetAsyncKeyState` reads the
    # key without consuming it, so whatever has focus receives it too. A
    # function key nothing binds is the cheapest way to make that harmless;
    # `enter` selects the console fallback instead, which has no global hook at
    # all. See `audio.py`.
    hotkey: str = "f9"
    input_device: str | int | None = None
    # A clip shorter than this is a bounced key rather than an utterance. Not
    # sent, and counted -- a client that transcribed 40ms of silence would put
    # a turn into the log the person did not take.
    min_speech_ms: int = 250
    # A ceiling, so a key held down by a stuck finger or a heavy window drag
    # cannot fill memory. 16kHz float32 is 64KB/s, so two minutes is 7.7MB.
    max_speech_s: int = 120

    # -- transcription ------------------------------------------------------
    # **CPU at int8, because the 3080 may be running fine-tune seeds** and a
    # voice client that slowed a training run is one nobody leaves open.
    # `--stt-device cuda --stt-compute float16` when the card is free, and
    # that flag is worth 9x: `base.en` is ~64ms on the 3080 against 564ms here
    # (measured 2026-08-30), which is the difference between missing VISION
    # §3's whole 500ms budget and meeting it with room. The default stays CPU
    # anyway, because the card is usually training and a voice client that
    # took 9x off a fine-tune run is one nobody leaves open.
    #
    # **`base.en` rather than `small.en`, and the measurement is the reason.**
    # The three English models were run over the same 55 synthesised
    # utterances at int8 on this CPU (`scripts/voice_proxy.py`, 2026-08-30):
    #
    #     tiny.en    279ms median   punctuated 94.5%   leading capital 92.7%
    #     base.en    564ms median   punctuated 98.2%   leading capital 98.2%
    #     small.en  1759ms median   punctuated 81.8%   leading capital 90.9%
    #
    # VISION §3 budgets 500ms for the **whole** round trip, so `small.en`
    # spends three and a half of them before the model is even asked, and it
    # is not buying transcription quality for the price: the word errors that
    # matter here -- "buy milk" -> "by milk", "Write down" -> "Right down",
    # "Priya Nair" -> "pre-annear" -- are identical across all three. `base.en`
    # is a third of the cost and the cleanest surface of the three.
    # `--stt-model small.en` is one flag for anyone who wants it back.
    stt_model: str = "base.en"
    stt_device: str = "cpu"
    stt_compute: str = "int8"
    stt_beam: int = 5
    # **Three measurement decisions, and they are why these are fields.**
    # An `initial_prompt` is the standard lever for whisper's punctuation
    # style, so setting one would make docs/PLAN-VOICE.md §9's distribution a
    # property of the prompt rather than of the transcriber. A VAD would put a
    # second opinion between the key and the model when the key already
    # endpoints. Both default off, both recorded per row, so a card taken with
    # them on cannot be mistaken for one taken without.
    stt_prompt: str | None = None
    stt_vad: bool = False
    stt_language: str | None = None

    # -- speech out ---------------------------------------------------------
    # `auto` walks `tts.ORDER`: piper if a model is configured, else the
    # resident PowerShell (present on every Windows 10 box, nothing to
    # install), else pyttsx3, else print-only.
    tts: str = "auto"
    tts_voice: str = ""
    tts_rate: int = 0
    piper_model: str = ""

    # -- the sitting --------------------------------------------------------
    # Where the voice rows go. `Saved Sessions/` is already ignored, and these
    # are transcripts of a person speaking -- the most personal thing this repo
    # produces, on `sessionlog.py`'s terms.
    log: str = "Saved Sessions/voice.jsonl"
    # Off means no row is written at all, on `--no-log`'s terms.
    logging: bool = True
    # Whether to read the server's own log tail to obtain an exact join key.
    # Off when the server is on another machine, where the path it reports is
    # not a path here. See `voicelog.link_to`.
    join_server_log: bool = True

    @classmethod
    def load(cls, path: Path | None) -> "VoiceConfig":
        """Defaults, overlaid with a JSON file if there is one.

        A missing file is not an error -- a fresh clone has no `voice.json` and
        must still run. A file that exists and is wrong is an error, loudly:
        the whole reason to have a file is that its contents take effect.
        """
        cfg = cls()
        if path is None or not Path(path).exists():
            return cfg
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConfigError(f"{path}: {exc}") from None
        if not isinstance(raw, dict):
            raise ConfigError(f"{path}: expected an object, got "
                              f"{type(raw).__name__}")
        known = {f.name for f in fields(cls)}
        stray = sorted(set(raw) - known)
        if stray:
            raise ConfigError(f"{path}: unknown key(s) {stray} -- known keys "
                              f"are {sorted(known)}")
        for k, v in raw.items():
            setattr(cfg, k, v)
        cfg.validate()
        return cfg

    def override(self, args: argparse.Namespace) -> "VoiceConfig":
        """The command line on top, and only where it was actually given.

        `None` from argparse means "not passed" and must not overwrite a file's
        value with a default -- which is the bug that makes a config file look
        like it is being ignored. Every flag in `add_arguments` therefore
        defaults to `None`, and the dataclass holds the real defaults.
        """
        for f in fields(self):
            v = getattr(args, f.name, None)
            if v is not None:
                setattr(self, f.name, v)
        self.validate()
        return self

    def validate(self) -> None:
        if self.port <= 0 or self.port > 65535:
            raise ConfigError(f"port {self.port} is not a port")
        if self.min_speech_ms < 0:
            raise ConfigError("min_speech_ms cannot be negative")
        if self.max_speech_s <= 0:
            raise ConfigError("max_speech_s must be positive")
        if self.stt_beam < 1:
            raise ConfigError("stt_beam must be at least 1")
        if self.tts == "piper" and not self.piper_model:
            raise ConfigError("--tts piper needs --piper-model <path to .onnx>")

    def stt_card(self) -> dict:
        """The transcription settings, as a row records them.

        Every field that can move the punctuation a turn arrives with, and
        nothing else. Two reads taken under different settings are not one
        measurement, which is `harness/surfacegrid.py`'s ground rule 13 applied
        to the transcriber.
        """
        return {
            "model": self.stt_model,
            "device": self.stt_device,
            "compute": self.stt_compute,
            "beam": self.stt_beam,
            "prompt": self.stt_prompt,
            "vad": self.stt_vad,
            "language": self.stt_language,
        }

    def as_dict(self) -> dict:
        return asdict(self)


def add_arguments(ap: argparse.ArgumentParser) -> None:
    """Every field as a flag, defaulting to `None`. See `override`."""
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                    help=f"JSON of the same keys; absent is fine "
                         f"(default {DEFAULT_CONFIG.name})")
    ap.add_argument("--host", default=None)
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--hotkey", default=None,
                    help="a key name for the global hook (f9, f8, scrolllock, "
                         "rctrl...), or 'enter' for the console fallback")
    ap.add_argument("--input-device", default=None,
                    help="index or name substring; --devices lists them")
    ap.add_argument("--min-speech-ms", type=int, default=None)
    ap.add_argument("--max-speech-s", type=int, default=None)
    ap.add_argument("--stt-model", default=None,
                    help="a faster-whisper model name or a local directory")
    ap.add_argument("--stt-device", default=None, choices=("cpu", "cuda", "auto"))
    ap.add_argument("--stt-compute", default=None,
                    help="int8, int8_float16, float16, float32")
    ap.add_argument("--stt-beam", type=int, default=None)
    ap.add_argument("--stt-prompt", default=None,
                    help="an initial prompt. Off by default and that is a "
                         "measurement decision -- see config.py")
    ap.add_argument("--stt-vad", action="store_true", default=None)
    ap.add_argument("--stt-language", default=None)
    ap.add_argument("--tts", default=None,
                    choices=("auto", "sapi", "piper", "pyttsx3", "silent"))
    ap.add_argument("--tts-voice", default=None,
                    help="substring of an installed voice's name")
    ap.add_argument("--tts-rate", type=int, default=None,
                    help="-10..10 for SAPI; 0 is the voice's own")
    ap.add_argument("--piper-model", default=None, help="path to a .onnx voice")
    ap.add_argument("--log", default=None, help="where voice rows are written")
    ap.add_argument("--no-log", dest="logging", action="store_false",
                    default=None, help="write no voice rows this sitting")
    ap.add_argument("--no-join", dest="join_server_log", action="store_false",
                    default=None,
                    help="do not read the server's log to obtain a join key")
