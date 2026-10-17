"""Push-to-talk. The interface VISION §3 says is the primary one.

**Every number this project has measured came in through a keyboard**, and §3
says the keyboard is the development interface. This package is the other one:
hold a key, speak, and the same `{"op": "turn"}` frame `harness/client.py`
sends goes to the same server, with the reply spoken back by a local
synthesiser. Nothing about the turn is different. That is the design, not a
simplification of it -- a client that had to be understood specially would be a
protocol that had got too complicated, which is the rule `client.py` was
written to keep.

**Local, and that word is doing work.** No cloud STT, no cloud TTS, no audio
and no transcript off this machine. A microphone is the most intrusive input a
person can give a program and the shipped artefact carries a privacy stance
(`contacts.json`, `notes.jsonl`, `packs/` are all ignored for it); a voice
client that shipped audio to a transcription API would make every one of those
decisions cosmetic.

**Two rules the rest of the package exists to keep.**

1. **The transcript reaches the server byte-identical to what the transcriber
   emitted.** No stripping, no casefolding, no cleanup. `harness/foldgate.py`
   measured what removing a terminal question mark costs: `resolve_date`
   carriers go 18/24 -> 1/24, every loss to `web_search`, because 2,268,194 of
   the corpus's 2,442,972 punctuated user turns are that tool. The owner
   retired that transform on 2026-08-30. A cleanup step here would reintroduce
   it outside the fold, where no guard is watching, on the input channel §3
   calls primary.

2. **Only a `say` is spoken, and only after the markers come off.** The `text`
   stream is not spoken even though streaming it would be faster, because the
   runtime is allowed to withdraw what the model streamed -- a deferred say, a
   refused social reply, an emission with no `<|say|>` in it -- and a screen
   can retract a sentence where a speaker cannot.

The split across the files is one line: what a guard can check without a
microphone, and what it cannot.

    config    every knob, defaults, JSON, CLI overrides            pure
    speech    marker sanitisation, multi-say, what gets said       pure
    surface   the punctuation/case ruler -- docs/PLAN-VOICE.md §9  pure
    latency   the per-stage stopwatch and the line it prints       pure
    voicelog  one JSONL row per voice turn, and the join           append-only
    stt       the Transcriber seam + faster-whisper + a stub       hardware
    tts       the Voice seam + SAPI, Piper, pyttsx3, silent        hardware
    audio     the hotkey and the capture buffer                    hardware
    __main__  the loop that wires them

`scripts/check_voice.py` drives every pure half plus a whole turn against a
fake server, on a machine with no microphone and no model.

**This package imports nothing from `corn/`.** That is stricter than
`scripts/check_layering.py` requires -- it would permit any module in the
inference closure -- and it is deliberate: the one thing a client must not be
able to do is transform the utterance, and a client holding `fold_turn` is one
import away from folding it twice. The guard asserts it here, because
`check_layering.py` globs `harness/*.py` and does not descend into
subpackages.

Usage:
    python -m harness.voice
    python -m harness.voice --hotkey enter --stt-model tiny.en
    python -m harness.voice --devices
"""
