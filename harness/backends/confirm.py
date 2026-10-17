"""Nothing irreversible happens without an explicit yes.

**What is gated today: declaration-file tools, and nothing built in**
(2026-10-13, PLAN-PEOPLE §7 and §9.4). The gate was built for `place_call`
and `send_text` when they could reach anyone in a contact book -- a call to
the wrong person cannot be taken back, and the copy grammar and the composed
book were defences against a *probable* failure, not against the model simply
being wrong. Since then he calls and texts only the owner (`corn.tools.
owner_call_tool`), and a ring or a text to your own phone is reversible in
every sense that matters, so the owner took the confirmation turn away from
both. What remains gated is a `tools.d/` declaration that asks for it: it
runs somebody's command, and holding it means running nothing until the yes.
The decision to ask still never routes through the weights -- §6's argument,
ambiguity in code "where it is exact", at higher stakes.

**The model is never asked to re-emit the call, and that is the design.**
Turn one it writes the call; the gate holds it and hands back a `clarify`
payload, which the model reads out because reading a tool's `clarify` back is
trained behaviour -- `place_call`'s ambiguity branch has always worked that
way. Turn two the **runtime** matches the answer and executes what it already
holds. Nothing in the corpus has a second `<|user|>` after an `<|end|>`, so
asking the model to reconstruct the call from an off-distribution context would
have added a failure mode in order to protect against one. It also means
confirmation works with turn-independent decoding, which is the default.

**Ambiguity cancels.** The affirmation list is short, explicit, and matched
against the whole utterance rather than searched for inside it, because "no,
call Mum" contains "call Mum". Anything that is not a clear yes and not a clear
no cancels the pending action and is then answered as an ordinary turn, so the
user is never trapped in a confirmation they cannot get out of by talking.

**`ask_agent` is deliberately not in the default set, and must join it the day
it can actually send.** §6 calls it the most consequential tool in the library
-- it acts *as the user* on an agent that can write code -- but today it only
writes to a queue nothing drains. Gating a no-op would spend the user's
patience on a confirmation that protects nothing, which is how confirmation
prompts get trained out of people.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

# Outward-facing and irreversible, built in: nothing, since calls and texts
# reach only the owner. A `tools.d/` declaration adds itself (`gated_customs`).
DEFAULT_GATED: tuple[str, ...] = ()

# A held action goes stale. The gate is cancelled by any non-confirming turn
# anyway, so this only catches the case where nothing at all is said -- the user
# walks away mid-question and comes back to a different conversation. Two
# minutes is long enough to think and short enough that "yes" never lands on
# something forgotten.
TTL_SECONDS = 120.0

_YES = frozenset([
    "yes", "yeah", "yep", "yup", "aye", "ok", "okay", "sure", "confirm",
    "confirmed", "correct", "please", "yes please", "yeah please",
    "please do", "go ahead", "go on", "do it", "send it", "make the call",
    "call them", "call him", "call her", "ring them", "text them",
    "go for it", "sure thing", "okay then", "yes do it",
    "yes go ahead", "yes please do", "affirmative",
    # Both spellings of every contraction, in both lists. `_normalise` keeps
    # the apostrophe, and whether a transcriber emits one is not something the
    # gate should have an opinion about -- especially since the interface this
    # is being built for is voice.
    "that's right", "thats right",
])

_NO = frozenset([
    "no", "nope", "nah", "do not", "cancel", "stop", "forget it",
    "never mind", "nevermind", "leave it", "no thanks", "no thank you",
    "not now", "hold on", "wait", "scrap that", "abort", "negative",
    "don't", "dont", "don't bother", "dont bother",
])

# **A yes or a no that arrives with nothing held is still this file's turn to
# answer.** Live on 2026-08-26 a bare "no" with no pending call fell through
# to the router and came back as a web search for the word "no" -- a paragraph
# about Norway's top-level domain, read out with confidence. The word was
# always the gate's vocabulary; only the *pending* case was handled, and the
# social pools cannot take the orphan case because `scripts/check_confirm.py`
# holds them disjoint from these very words, so that a real confirmation is
# never absorbed by a pool.
#
# Only the subset that is *nothing but* an acknowledgement or a refusal is
# answered here. "do it", "send it", "call them", "go ahead" are confirmations
# when something is held and **elliptical requests** when nothing is -- a user
# who says "call them" after naming somebody wants a phone call, and a gate
# that answered "Alright, what do you need?" would be absorbing a request,
# which is the exact failure whole-utterance matching exists to prevent on
# the social path. Those stay with the model. So do "wait" and "hold on",
# which orphaned are a different speech act again.
_ORPHAN_YES = frozenset([
    "yes", "yeah", "yep", "yup", "aye", "ok", "okay", "sure",
    "sure thing", "okay then", "affirmative",
])
_ORPHAN_NO = frozenset([
    "no", "nope", "nah", "cancel", "stop", "forget it", "never mind",
    "nevermind", "leave it", "no thanks", "no thank you", "scrap that",
    "abort", "negative", "not now",
])
# The orphan sets narrow the gate's own vocabulary and never widen it: a word
# in neither _YES nor _NO must reach the model however it is classified here.
assert _ORPHAN_YES <= _YES and _ORPHAN_NO <= _NO

# Honest about the one thing the user cannot see: whether anything was held.
# Spoken, so no em dashes; small and hand-written on DECLINE_SAYS' reasoning.
ORPHAN_YES_SAYS = (
    "Alright. What do you need?",
    "OK, I'm listening.",
    "Sure. What can I do for you?",
)
ORPHAN_NO_SAYS = (
    "OK, leaving it. Nothing was in motion anyway.",
    "Alright. Nothing was underway, so we're good.",
    "Fair enough. There's nothing running to call off.",
)


def _clip(value: str, limit: int = 0) -> str:
    """Truncate a value for a spoken question; see `QUESTION_VALUE_CHARS`."""
    limit = limit or QUESTION_VALUE_CHARS
    return value if len(value) <= limit else value[:limit - 3] + "..."


def _normalise(text: str) -> str:
    """Lowercase, strip punctuation, collapse spaces. Nothing cleverer.

    A fuzzy match here would be a way of turning "no" into a phone call, so the
    normalisation is only allowed to remove things that cannot change meaning.
    """
    kept = [c.lower() for c in text if c.isalnum() or c in " '"]
    return " ".join("".join(kept).split())


@dataclass
class Pending:
    tool: str
    arguments: dict
    # The payload a held action already has; `{}` for a declaration-file
    # tool, whose payload does not exist until the yes runs it.
    payload: dict
    question: str
    at: float
    # **A held action has not run yet.** A declaration-file tool
    # (`harness/backends/toolsd.py`) runs somebody's command, so holding it
    # means holding a closure and running nothing until the yes.
    run: object = None

    def stale(self, now: float) -> bool:
        return now - self.at > TTL_SECONDS


# How much of an argument's value the question repeats back. `relay.py`'s
# `Row.spoken` picked 300 for a ledger read on demand; a question asked out
# loud mid-turn earns less.
QUESTION_VALUE_CHARS = 80


class Gate:
    """Holds at most one pending action. Not thread-safe; the server serialises."""

    def __init__(self, gated=DEFAULT_GATED, runners: dict | None = None):
        self.gated = tuple(gated)
        # `{name: (arguments) -> payload}` for gated declaration-file tools --
        # the same callables `EXECUTORS` holds, handed in so a yes can run one
        # without going back through the turn. Empty for every server without
        # a tools folder, and every built-in behaviour is byte-identical then.
        self.runners = dict(runners or {})
        self.pending: Pending | None = None

    # -- turn one -----------------------------------------------------------

    def intercept(self, name: str, arguments: dict) -> dict | None:
        """Called instead of the executor. `None` means "run it normally".

        Returns a `clarify` payload when it holds the action -- the shape a
        tool's question back has always had, so the model reads it out by the
        behaviour it already has rather than by a new one.
        """
        if name not in self.gated:
            return None
        if name in self.runners:
            # A declaration-file tool. Held *without running* -- see
            # `Pending.run` -- and the question is composed in code because
            # code is the place that cannot get the values wrong. Raw
            # argument values, truncated.
            shown = ", ".join(
                f"{k} {_clip(str(v))!r}" for k, v in sorted(arguments.items()))
            question = (f"Running {name}" + (f" with {shown}" if shown else "")
                        + ". Shall I go ahead?")
            runner = self.runners[name]
            self.pending = Pending(name, dict(arguments), {}, question,
                                   time.monotonic(),
                                   run=lambda: runner(dict(arguments)))
            return {"ok": False, "reason": "confirm", "clarify": question}
        # A gated name with no runner: nothing built in is gated, and a
        # declaration always arrives with its runner, so there is nothing to
        # hold -- run it normally.
        return None

    # -- turn two -----------------------------------------------------------

    def answer(self, utterance: str) -> dict | None:
        """Resolve a pending action against what the user just said.

        `None` when there is nothing pending, or when the utterance is neither
        a yes nor a no -- in which case the pending action is dropped and the
        caller should treat the utterance as an ordinary turn. Dropping rather
        than keeping is the safe direction: a user who has moved on must not
        find that their next "yes", to something else entirely, dials a phone.
        """
        held = self.pending
        if held is None:
            return None
        self.pending = None
        if held.stale(time.monotonic()):
            return {"outcome": "expired", "tool": held.tool,
                    "say": "That went stale, so I left it."}

        said = _normalise(utterance)
        if said in _YES:
            # A deferred action runs now, on the yes and never before it. The
            # executor wraps its own failures into a speakable payload
            # (`toolsd.make_executor`), so this call cannot raise.
            payload = held.payload if held.run is None else held.run()
            return {"outcome": "confirmed", "tool": held.tool,
                    "arguments": held.arguments, "payload": payload,
                    "say": self._done(held, payload)}
        if said in _NO:
            return {"outcome": "cancelled", "tool": held.tool,
                    "say": "Right, I'll leave it."}
        # Neither. Already dropped above; the caller carries on with the turn.
        return None

    def orphan(self, utterance: str) -> str | None:
        """A reply for a bare yes or no that arrived with nothing held.

        `None` for everything else, and for *anything at all* while a call is
        pending -- `answer` runs first and owns that case, and this method
        double-checks rather than trusting the caller's ordering, on section
        7 of `scripts/check_confirm.py`'s argument that an ordering in
        another file is not an invariant.

        The reply admits the state: a "no" is agreed with by saying nothing
        was in motion, not by pretending to cancel something. `random.choice`
        rather than the recent-reply rotation the social pools get, because
        an orphaned yes or no is rare enough that repetition was never the
        risk here.
        """
        if self.pending is not None:
            return None
        said = _normalise(utterance)
        if said in _ORPHAN_YES:
            return random.choice(ORPHAN_YES_SAYS)
        if said in _ORPHAN_NO:
            return random.choice(ORPHAN_NO_SAYS)
        return None

    @staticmethod
    def _done(held: Pending, payload: dict) -> str:
        """What the runtime says once a held action has run.

        On this path the model is not consulted, so the sentence comes from
        code. A declaration-file tool that put a `say` in its payload chose its
        own sentence; one that did not gets a plain "Done."
        """
        say = payload.get("say")
        return say if isinstance(say, str) and say.strip() else "Done."
