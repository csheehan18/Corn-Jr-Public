"""Where the time went, per stage, per turn -- VISION §3's table as a line.

**§3 makes round-trip latency the top-level constraint of the project, ahead of
parameter count and benchmark scores, and budgets it stage by stage.** Until
this package nothing measured the two stages it says are the actual bottleneck:
"Endpointing and TTS are. Any work on model speed past comfortably fast enough
is wasted effort compared to work on the audio pipeline." `harness/client.py`
reports time-to-first-token and total because those are the two a keyboard
client can see. A microphone client can see all of them, so it does.

**The clock is passed in, never read here.** Every stage is a pair of marks and
`Stopwatch.mark` takes the time as an argument, so `scripts/check_voice.py`
steps a whole turn through with a fake clock and asserts the arithmetic instead
of sleeping. A guard that slept would be slow and would fail on a loaded
machine for reasons that have nothing to do with the code -- which is
`check_overlay.py`'s argument for `Player.frame(now)`.

**Two stages are honest about being worse than the budget, and that is the
point of printing them.** §3's 50-100ms for STT assumes streaming
finalisation, with most of the work already done at end-of-speech; push-to-talk
with a batch transcriber does all of it after the key comes up and cannot hit
that row. And endpointing -- §3's "sneakily the hardest part", 50-150ms -- is
zero here because a human finger does it. Those are the two numbers that make
push-to-talk the right V1 and they only argue for themselves if they are
visible.

**`tts` is a handoff unless an adapter can prove first audio.** `SpeakAsync`
returns when an utterance is queued, not when a speaker moves. Every row
carries which of the two it measured, so a streaming adapter's numbers are
never silently compared against these. Calling a handoff "time to first audio"
is how a pipeline gets measured as faster than it is.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# The marks, in the order a turn passes them. Named rather than positional so
# a stage added later cannot silently shift the meaning of a stored row.
MARKS = (
    "key_down",    # the microphone opened
    "key_up",      # it closed. Everything after this is latency the user feels
    "stt_done",    # the transcript is in hand
    "sent",        # the frame is on the socket
    "first",       # the first `text` or `say` came back
    "first_say",   # the first thing there was to actually say
    "done",        # the turn ended
    "tts_start",   # the synthesiser was handed the words, or began them
    "tts_done",    # it finished speaking, which nobody is waiting on
)

# stage -> (from, to). The one that matters is last and is printed last.
#
# **`tts` runs from `first_say` and not from `done`, because speech starts
# before the turn does.** A compound turn emits a say per tool and this client
# speaks each one as it arrives -- waiting for `done` would hold the first
# sentence hostage to the second tool. That makes `mouth_to_ear` legitimately
# smaller than `server` on those turns, which is a fact about the pipeline
# worth being able to read rather than an inconsistency to hide.
STAGES = {
    "spoke": ("key_down", "key_up"),
    "stt": ("key_up", "stt_done"),
    "server": ("sent", "done"),
    "ttft": ("sent", "first"),
    "reply": ("sent", "first_say"),
    "tts": ("first_say", "tts_start"),
    "mouth_to_ear": ("key_up", "tts_start"),
    "spoken_for": ("tts_start", "tts_done"),
}

# §3's number. Printed as the last field of the line and the only one this
# client would ever be judged on.
BUDGET_MS = 500.0


@dataclass
class Stopwatch:
    """Marks in, milliseconds out. No clock of its own -- see the docstring."""

    at: dict[str, float] = field(default_factory=dict)

    def mark(self, name: str, now: float) -> None:
        """Record one mark. `now` is `time.perf_counter()` from the caller.

        A repeated mark keeps the **first**: `first` is time to first token and
        a turn emits many, so the natural loop would otherwise overwrite it on
        every event and report time to *last* token under the name of the one
        §3 budgets.
        """
        if name not in MARKS:
            raise KeyError(f"{name!r} is not a mark: {MARKS}")
        self.at.setdefault(name, now)

    def ms(self, stage: str) -> float | None:
        """One stage in milliseconds, or `None` if it did not happen.

        `None` rather than 0.0 because a turn genuinely can skip a stage -- a
        silent turn has no `tts_start` -- and a zero would enter an average as
        a fast turn rather than as an absent one.
        """
        a, b = STAGES[stage]
        if a not in self.at or b not in self.at:
            return None
        return (self.at[b] - self.at[a]) * 1000.0

    def all_ms(self) -> dict[str, float | None]:
        return {s: self.ms(s) for s in STAGES}

    def line(self, tts_measure: str = "handoff") -> str:
        """The per-turn line. Absent stages are omitted, not zeroed.

        `mouth_to_ear` is last, carries the `!` when it is over §3's budget,
        and is the only stage this line editorialises about.
        """
        parts = []
        spoke = self.ms("spoke")
        if spoke is not None:
            parts.append(f"spoke {spoke / 1000:.1f}s")
        for stage, label in (("stt", "stt"), ("server", "server")):
            v = self.ms(stage)
            if v is not None:
                if stage == "server" and self.ms("ttft") is not None:
                    parts.append(f"{label} {v:.0f}ms "
                                 f"(ttft {self.ms('ttft'):.0f}ms)")
                else:
                    parts.append(f"{label} {v:.0f}ms")
        tts = self.ms("tts")
        if tts is not None:
            parts.append(f"tts {tts:.0f}ms {tts_measure}")
        end = self.ms("mouth_to_ear")
        if end is not None:
            over = " !" if end > BUDGET_MS else ""
            parts.append(f"{end:,.0f}ms mouth-to-ear{over}")
        return "  [" + " | ".join(parts) + "]" if parts else "  [nothing timed]"
