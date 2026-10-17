"""A store for actions that happen later, on the rules class N wrote first.

**The first thing that ever makes this system initiate.** Every other backend
answers a turn; this one holds an action -- a reminder to the owner, a text to
a contact -- and fires it at a time `resolve_time_tool` computed. The rules
were pre-registered in `docs/PLAN-TURN-2.md` §N before this file existed, and
each one is enforced here rather than hoped for:

  * **A reminder to the owner fires without confirmation; a scheduled message
    to a contact is confirmed at scheduling time**, with the question naming
    the resolved time and recipient, and is never re-asked at fire time -- a
    confirmation nobody is awake to answer is not a gate. `question_for`
    composes that question and `add` refuses a contact text that has not been
    through it.
  * **Scheduled state is inspectable and cancellable.** `pending` lists it in
    speakable form; `cancel` drops by the words the user would use, not by an
    id nobody said out loud.
  * **A fire that cannot deliver degrades to a note, never to silence.** The
    server today has no delivery surface between turns -- the voice loop is
    Phase 4 -- so `sweep` collects everything due, writes each to the day log,
    and returns the sentences to say about it at the next conversation.
    Nothing in this file ever claims `sent` for a text that did not go: a
    swept text degrades to a note that says what *would* have been sent and
    that it was not, which is `_ask_agent`'s honesty rule pointed at the
    future.

**Not yet reachable from the model.** `schedule` is not in `REGISTRY`; the
declaration flips with the corpus that teaches it (PLAN-TURN-2 §N's
sequencing). This file exists so that decision is a one-line change instead
of an engineering project.

**The file is personal data**, like the contact book and the day log: what a
running instance schedules belongs to the person running it, and the default
path is gitignored under the same rule.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_STORE = Path("schedule.jsonl")

# The two actions the store knows. `remind` speaks to the owner; `text` goes
# out into the world, which is why only `text` needs the gate.
ACTIONS = ("remind", "text")


@dataclass(frozen=True)
class Entry:
    id: str
    at: str            # ISO datetime, minute precision
    action: str        # one of ACTIONS
    message: str
    contact: str | None
    created: str

    def spoken(self) -> str:
        when = datetime.fromisoformat(self.at)
        clock = when.strftime("%I:%M %p").lstrip("0")
        if self.action == "text":
            return f'a text to {self.contact} at {clock}: "{self.message}"'
        return f"a reminder at {clock}: {self.message}"


def question_for(contact: str, message: str, at: datetime,
                 because: str | None = None) -> str:
    """The confirmation a scheduled contact text must be held behind.

    Composed in code for `confirm.py`'s reason -- the question names the
    resolved recipient and the resolved time, which are the two things the
    user needs to hear before something goes out in their name while they
    are not watching. `because` carries the anchor it was computed from
    ("half an hour before sunset"), because a bare clock time is the answer
    with its reasoning stripped.
    """
    clock = at.strftime("%I:%M %p").lstrip("0")
    tail = f", {because}" if because else ""
    return f'I\'ll text {contact} at {clock}{tail}: "{message}". Sound good?'


class Scheduler:
    """Append-only JSONL with a live index, like the day log with a clock.

    Not thread-safe; the server serialises turns, and `sweep` runs on the
    same loop. Every mutation is a full rewrite of the small file rather
    than a tombstone log, because `pending` has to be readable by a person
    opening the file, and a store of futures stays small by nature.
    """

    def __init__(self, path: Path = DEFAULT_STORE):
        self.path = Path(path)
        self.entries: list[Entry] = []
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.entries.append(Entry(**json.loads(line)))

    # -- mutations ----------------------------------------------------------

    def add(self, at: datetime, action: str, message: str,
            contact: str | None = None, confirmed: bool = False) -> dict:
        """Hold an action. Returns a payload in the trained shapes.

        A `text` that has not been confirmed is refused here, structurally --
        the rule is worth nothing if a caller can forget it. `remind` needs
        no gate: it speaks to the owner, and the owner asked.
        """
        if action not in ACTIONS:
            return {"ok": False, "reason": "unknown_action",
                    "say": "That's not something I can schedule."}
        if action == "text" and not contact:
            return {"ok": False, "reason": "no_contact",
                    "say": "Scheduled for who, sorry?"}
        if action == "text" and not confirmed:
            return {"ok": False, "reason": "confirm",
                    "clarify": question_for(contact or "them", message, at)}
        if not message.strip():
            return {"ok": False, "reason": "nothing_to_say",
                    "say": "What should it say?"}
        entry = Entry(
            id=uuid.uuid4().hex[:8],
            at=at.replace(second=0, microsecond=0).isoformat(timespec="minutes"),
            action=action,
            message=message.strip(),
            contact=contact,
            created=datetime.now().astimezone().isoformat(timespec="seconds"),
        )
        self.entries.append(entry)
        self._flush()
        clock = at.strftime("%I:%M %p").lstrip("0")
        return {"status": "scheduled", "at": entry.at,
                "say": f"Done. I'll {'text ' + (contact or '') if action == 'text' else 'buzz you'} at {clock}."}

    def cancel(self, words: str) -> dict:
        """Drop entries matching what the user said. The voice-reach rule.

        Matching is by overlap with the entry's own message or contact,
        because "drop the sunset one" names content, not an id. Ambiguity
        drops nothing and asks -- a cancel that guessed would be the
        confident wrong label, applied to the future.
        """
        want = {w for w in words.lower().split() if len(w) > 2}
        hits = [e for e in self.entries
                if want & set((e.message + " " + (e.contact or "")).lower().split())]
        if not hits:
            return {"ok": False, "reason": "not_found",
                    "say": "I don't have anything scheduled like that."}
        if len(hits) > 1:
            listed = "; ".join(e.spoken() for e in hits)
            return {"ok": False, "reason": "ambiguous",
                    "clarify": f"Which one -- {listed}?"}
        self.entries.remove(hits[0])
        self._flush()
        return {"status": "cancelled", "say": f"Dropped {hits[0].spoken()}."}

    # -- reads --------------------------------------------------------------

    def pending(self) -> dict:
        if not self.entries:
            return {"ok": False, "reason": "empty",
                    "say": "Nothing on the schedule right now."}
        listed = "; ".join(e.spoken() for e in sorted(self.entries,
                                                      key=lambda e: e.at))
        return {"entries": [asdict(e) for e in self.entries],
                "say": f"I've got {listed}."}

    def sweep(self, now: datetime, log=None) -> list[str]:
        """Everything due, degraded honestly, said at the next chance.

        Returns the sentences to speak. A due `remind` becomes its own
        sentence; a due `text` was NOT sent -- there is no delivery path yet
        -- and the sentence says exactly that, with the note carrying what
        would have gone. `log` is a `DayLog`-shaped object with `.add`; when
        present, every swept entry is written down so a missed fire is never
        only a memory.
        """
        due = [e for e in self.entries
               if datetime.fromisoformat(e.at) <= now]
        if not due:
            return []
        said: list[str] = []
        for e in sorted(due, key=lambda e: e.at):
            self.entries.remove(e)
            if e.action == "text":
                line = (f"While you were away I was set to send {e.spoken()}, "
                        f"but I can't send texts on a timer yet, so it did "
                        f"not go out.")
            else:
                line = f"While you were away: {e.message}."
            if log is not None:
                log.add(now.date(), f"scheduled: {e.message}"
                        + (f" (for {e.contact}, not sent)"
                           if e.action == "text" else ""), None)
            said.append(line)
        self._flush()
        return said

    def _flush(self) -> None:
        self.path.write_text(
            "".join(json.dumps(asdict(e), ensure_ascii=False) + "\n"
                    for e in self.entries),
            encoding="utf-8")


def next_fire(anchor: datetime, hh_mm: str) -> datetime:
    """The next wall-clock occurrence of HH:MM after `anchor`.

    `resolve_time_tool` answers in clock time; a store needs a date. The
    rule is the obvious one -- today if still ahead, tomorrow if passed --
    stated here once so two call sites cannot disagree about midnight.
    """
    h, m = (int(p) for p in hh_mm.split(":"))
    candidate = anchor.replace(hour=h, minute=m, second=0, microsecond=0)
    if candidate <= anchor:
        candidate += timedelta(days=1)
    return candidate
