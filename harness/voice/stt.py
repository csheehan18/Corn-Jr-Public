"""Speech in, text out, and the text is not touched afterwards.

**One rule, and the whole file is arranged around keeping it.** What the
transcriber returns is what goes on the wire. No stripping, no casefolding, no
"tidying up the punctuation". This is not hygiene:

    punctuated resolve_date carriers that reach the weights
        mark kept   18/24        mark stripped   1/24

`harness/foldgate.py`, 2026-08-30, `corn_jr_260m_v4`, two arms differing by the
strip alone; all seventeen turns that moved went `resolve_date` ->
`web_search`. The corpus behind that is entry 0's count -- 2,268,194 of the
2,442,972 punctuated user turns in 6.6M are the date tool. The owner retired
the strip on the strength of it. **A cleanup step here would reintroduce the
retired transform outside the fold, where no guard is watching**, on the input
channel VISION §3 calls the primary one. `scripts/check_voice.py` asserts byte
identity from this file's output to the frame.

**The model runs on the CPU by default and that is a scheduling decision.** The
3080 may be running fine-tune seeds, and a voice client that made a training
run slower is a voice client nobody leaves open. `base.en` at `int8` is the
default -- see `config.py` for the three-model measurement that picked it over
`small.en`, which costs 1759ms against 564ms and buys nothing. `--stt-device
cuda --stt-compute float16` is one flag when the card is free.

**Three settings are measurement decisions rather than tuning.** An
`initial_prompt` is the standard lever for whisper's punctuation style, so
setting one would make `docs/PLAN-VOICE.md` §9's distribution a property of the
prompt rather than of the transcriber; a VAD filter would put a second opinion
between the key and the model when the key already endpoints; and the language
is left unset unless asked. All three default off and all three are recorded in
every row, so a read taken under them cannot be mistaken for one taken without.

**The import is lazy and that is not an optimisation.** `faster_whisper` pulls
ctranslate2 and onnxruntime, which is seconds of startup and a hard dependency
on a machine that may only want the pure half of this package.
`scripts/check_voice.py` imports this module and never loads a model.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

import numpy as np

from .config import SAMPLE_RATE, VoiceConfig


@dataclass
class Transcript:
    """What the transcriber said, and what it said about saying it.

    `text` is untouched output. `segments` is how many the decoder produced --
    more than one on a single held key is worth knowing, because a
    multi-segment clip is where an internal full stop comes from and
    `surface.py` counts those.
    """

    text: str
    segments: int = 0
    # The decoder's own confidence, where the backend reports one. Recorded
    # rather than acted on: a threshold here would be a filter on what the
    # model is allowed to hear, which is a bigger decision than a client makes.
    logprob: float | None = None
    language: str | None = None
    duration_ms: float = 0.0


class Transcriber(Protocol):
    """The seam. One method, so a stub is three lines and the guard is real."""

    name: str

    def transcribe(self, audio: np.ndarray, rate: int) -> Transcript: ...


class Stub:
    """Canned answers, in order, for `scripts/check_voice.py`.

    Exists so the guard can drive a whole turn -- key-down through spoken
    output -- with no model, no download and no microphone, and so the byte
    identity assertion has something to assert about.
    """

    name = "stub"

    def __init__(self, texts: list[str]):
        self.texts = list(texts)
        self.calls: list[tuple[int, int]] = []

    def transcribe(self, audio: np.ndarray, rate: int) -> Transcript:
        self.calls.append((len(audio), rate))
        text = self.texts.pop(0) if self.texts else ""
        return Transcript(text=text, segments=1 if text else 0,
                          duration_ms=len(audio) / rate * 1000)


class Whisper:
    """faster-whisper, loaded once and kept.

    Loading is seconds and a turn budget is 500ms, so the model outlives every
    turn -- the same argument `harness/server.py` makes for being resident at
    all.
    """

    def __init__(self, cfg: VoiceConfig):
        from faster_whisper import WhisperModel  # heavy; see the docstring

        self.cfg = cfg
        self.name = f"faster-whisper/{cfg.stt_model}"
        device = cfg.stt_device
        if device == "auto":
            device = "cuda" if _cuda() else "cpu"
        t0 = time.perf_counter()
        self.model = WhisperModel(cfg.stt_model, device=device,
                                  compute_type=cfg.stt_compute)
        self.load_ms = (time.perf_counter() - t0) * 1000
        self.device = device

    def transcribe(self, audio: np.ndarray, rate: int) -> Transcript:
        """Float32 mono at `SAMPLE_RATE` in, a `Transcript` out.

        **The join is `"".join`, with no strip.** `faster_whisper` yields
        segments whose text carries a leading space; joining them and then
        stripping the ends is the one whitespace change made here, and it is
        made because a leading space is a framing artefact of the segmenter
        rather than something the speaker said. Nothing inside the string is
        touched -- no case, no punctuation, no interior whitespace.
        """
        if rate != SAMPLE_RATE:
            raise ValueError(f"expected {SAMPLE_RATE}Hz, got {rate} -- this "
                             f"client captures at whisper's native rate so "
                             f"nothing here has to resample")
        segments, info = self.model.transcribe(
            audio,
            beam_size=self.cfg.stt_beam,
            language=self.cfg.stt_language,
            initial_prompt=self.cfg.stt_prompt,
            vad_filter=self.cfg.stt_vad,
        )
        parts, logprobs = [], []
        for seg in segments:
            parts.append(seg.text)
            lp = getattr(seg, "avg_logprob", None)
            if lp is not None:
                logprobs.append(lp)
        return Transcript(
            text="".join(parts).strip(),
            segments=len(parts),
            logprob=(sum(logprobs) / len(logprobs)) if logprobs else None,
            language=getattr(info, "language", None),
            duration_ms=len(audio) / rate * 1000,
        )


def _cuda() -> bool:
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception:
        return False


def build(cfg: VoiceConfig) -> Transcriber:
    """The configured transcriber, or a message a person can act on."""
    try:
        return Whisper(cfg)
    except ImportError:
        raise SystemExit(
            "faster-whisper is not installed. It is the local transcriber "
            "this client is built on -- nothing here talks to a cloud API.\n"
            "    .venv/Scripts/pip install faster-whisper sounddevice"
        ) from None
