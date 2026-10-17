"""Events in, a state name out. The half of the overlay with no display in it.

**Every state here is something the protocol already says.** `harness/
protocol.py` documents seven event kinds and the fields on them; this file is
the mapping from those to a small vocabulary a theme can draw, and it adds no
knowledge of its own. If the overlay ever wants to show something this cannot
name, the honest fix is a field on an event -- not a guess made here from
timing, from how long a reply took, or from what the words looked like.

**Two kinds of state, because a turn has two timescales.** A *resting* state
lasts until something changes it: he is idle, or thinking, or running a tool,
or speaking. A *flash* is a reaction to a thing that happened at one instant
and is over -- a call the schema refused, a reply the runtime had to write for
him -- and it lands one event before `done`, so a resting state built out of it
would be visible for about a millisecond and then gone. The flash is handed to
the player as a one-shot; the resting state underneath is untouched and comes
back when it finishes. `refused`, `covered`, `error`, `confirmed` and
`cancelled` are flashes for that reason and no other.

**`covered` is the one state worth defending.** `protocol.py` says `author` and
`fell_back` exist so a corpus can tell a reply the model generated from one a
runtime pool or a tool payload wrote, and that by the time a transcript is a
file the distinction is gone. It is gone on a screen too, unless something
draws it. So the overlay draws it: a reply he did not write gets a different
face than one he did. That is the whole argument for the state -- not that the
user needs to act on it, but that it is the one fact about a turn a finished
reply cannot carry and a face can.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# **Deliberately the reference client's function, imported rather than
# reimplemented.** `harness/client.py` decides when a `say` is "the same words
# the `text` events already streamed" and when it is a correction worth
# showing, and two clients disagreeing about that would put different words on
# a screen for the same turn. One rule, one implementation, one import.
from ..client import _content as spoken_content

# What a theme may name. Anything else in a theme's `states` map is a typo, and
# `anim.py` says so at load rather than at the moment it would have been drawn.
RESTING = ("offline", "idle", "listening", "thinking", "queued", "tool",
           "speaking")
FLASHES = ("refused", "covered", "error", "confirmed", "cancelled")
STATES = RESTING + FLASHES

# `done.outcome` is set by the confirmation gate and by nothing else, so these
# two are the gate resolving -- the moment the user's yes or no actually took
# effect. `expired` and `orphan` are gate outcomes too and deliberately get no
# flash: neither is a thing he did.
_OUTCOME_FLASH = {"confirmed": "confirmed", "cancelled": "cancelled"}


@dataclass
class Cue:
    """What changed, whole rather than as a delta.

    `text` is the entire bubble, not the piece that just arrived, because a
    renderer that had to accumulate would be keeping a second copy of the
    thing this class already owns -- and the two would drift on exactly the
    turns where a `say` replaces what was streamed.
    """

    state: str
    flash: str = ""
    text: str = ""
    note: str = ""
    ended: bool = False


@dataclass
class Machine:
    """One conversation's worth of state. Feed it events; read `.state`."""

    state: str = "offline"
    text: str = ""
    note: str = ""
    # What the `text` events have put up this turn, kept apart from `text`
    # because a `say` is compared against the streamed words and not against
    # whatever else may have been placed in the bubble.
    streamed: str = ""
    # The tool of the call in flight, so `obs` can keep naming it -- the field
    # is per-turn and a payload arriving is not a new tool.
    tool: str = ""
    history: list[str] = field(default_factory=list)

    def _cue(self, flash: str = "", ended: bool = False) -> Cue:
        return Cue(state=self.state, flash=flash, text=self.text,
                   note=self.note, ended=ended)

    # -- things the client end knows and the server does not ----------------

    def online(self) -> Cue:
        self.state = "idle"
        self.note = ""
        return self._cue()

    def offline(self, why: str = "") -> Cue:
        self.state = "offline"
        self.note = why
        return self._cue()

    def listening(self) -> Cue:
        """The user is typing. Only ever from `idle` -- a turn in flight is not
        interrupted by someone starting to type the next one, and drawing him
        as though it were would be a lie about what the server is doing."""
        if self.state == "idle":
            self.state = "listening"
        return self._cue()

    def submit(self, user: str = "") -> Cue:
        """A turn was sent. Nothing has come back, so `thinking` rather than
        `speaking` -- the two are different budgets in VISION section 3 and the
        face is the one thing that can show which of them is being spent."""
        self.state = "thinking"
        self.text = ""
        self.streamed = ""
        self.note = ""
        self.tool = ""
        if user:
            self.history.append(user)
        return self._cue()

    # -- the protocol -------------------------------------------------------

    def feed(self, ev: dict) -> Cue:
        """One event. Returns the cue it earned, unchanged state included.

        Unknown `t` values return the current state rather than raising: the
        server is allowed to grow events this file has not heard of (`opening`
        is already one), and an overlay that fell over on the first of them
        would make adding one a breaking change.
        """
        kind = ev.get("t", "")

        if kind == "text":
            self.state = "speaking"
            self.streamed += ev.get("text", "")
            self.text = self.streamed
            return self._cue()

        if kind == "say":
            said = ev.get("text", "")
            # The client's rule: show the whole reply only when it differs
            # from what was streamed, which is exactly the two cases the
            # runtime corrects.
            if said and spoken_content(said) != spoken_content(self.streamed):
                self.text = said
            self.state = "speaking"
            author = ev.get("author", "model")
            fell = ev.get("fell_back", "")
            if fell:
                self.note = f"covered: {fell}"
            elif author != "model":
                self.note = f"{author} wrote this"
            # A reply he did not write, for either of the two reasons
            # `protocol.py` gives. `--restrict` reaches here as a runtime
            # author with no `fell_back`, which is still not his sentence.
            if fell or author in ("runtime", "tool"):
                return self._cue(flash="covered")
            return self._cue()

        if kind == "call":
            self.tool = ev.get("name", "") or self.tool
            if ev.get("ok"):
                self.state = "tool"
                masked = ev.get("masked") or 0
                self.note = self.tool + (f"  (masked {masked})" if masked else "")
                return self._cue()
            # Written, and not run. The schema refusing a call is not an
            # error -- it is the grammar doing its job -- so it flashes over
            # whatever he was doing rather than replacing it.
            self.note = ev.get("why", "") or "refused"
            return self._cue(flash="refused")

        if kind == "rejected":
            self.note = ev.get("why", "") or "not executed"
            return self._cue(flash="refused")

        if kind == "obs":
            self.state = "tool"
            name = ev.get("name", "") or self.tool
            self.tool = name
            # `read` is the passage reading `--extract` made of the payload.
            # Naming it here is the only place the overlay can show that the
            # lookup went through him rather than around him.
            self.note = f"{name} read" if ev.get("read") else name
            return self._cue()

        if kind == "waiting":
            self.state = "queued"
            self.note = "behind another turn"
            return self._cue()

        if kind == "error":
            self.note = ev.get("why", "") or "error"
            return self._cue(flash="error")

        if kind == "done":
            self.state = "idle"
            self.tool = ""
            outcome = ev.get("outcome", "")
            return self._cue(flash=_OUTCOME_FLASH.get(outcome, ""), ended=True)

        return self._cue()
