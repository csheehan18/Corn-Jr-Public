"""One row per spoken turn, and the join into the server's own log.

**The marker the schema cannot carry.** A voice turn has to be identifiable in
the record, and it cannot be marked where the record is written. The check, in
order:

  * `harness/protocol.py`'s turn request is `{"op", "user", "id"}`, and
    `harness/server.py` reads exactly those three off the frame. An extra
    `"source": "voice"` key is accepted by `json.loads` and then dropped -- it
    reaches no event and no row.
  * `harness/sessionlog.py`'s `turn_record` builds a row from `session`,
    `turn`, `user`, the events, `wiring` and `ms`. `id` is not among them.
    Nothing a client sends survives into `turns.jsonl` except the utterance.
  * `wiring` is the *server's* configuration, read off `Session.info()` and
    per-process. A client cannot write it, and a client that could would be
    writing a column that describes the server.

So the marker is written here instead, and `docs/PLAN-VOICE.md` §6 says so
rather than the protocol growing a field for one client. That is the
instruction and it is also the right call: `protocol.py`'s whole argument is
that a client needing more than eighty lines to speak it means the protocol got
too complicated, and a per-client provenance field is the first step down that
road.

**But the join is exact, and it is obtained by reading rather than by
writing.** The server already reports its log path in `info`. After a turn
lands, this reads the last line of that file; if the row's `user` is
byte-identical to what was just sent and its timestamp is inside the turn's
window, the voice row records `(log, session, turn)`. That is a primary key
into `turns.jsonl` acquired without either end changing. When the server is on
another machine, or running `--no-log`, or another client appended in between,
`link` is `null` and `link_why` says which -- a join that sometimes cannot be
made is worth more than one that is sometimes wrong.

**What else the row carries, and why it is not just the marker.** A voice turn
and a typed turn are the same turn to the model and different events to
everyone else, and the differences are the reason to keep any of this: how long
the person spoke, what every stage cost, the exact transcriber settings the
transcript was produced under, `surface.py`'s reading of it, how many says the
turn had and how many markers the sanitiser caught. The transcript itself is
kept verbatim and is the scarce half -- `harness/sessionlog.py`'s argument,
unchanged.

It lands in `Saved Sessions/`, which `.gitignore` already covers, under the
rule stated there: what a running instance accumulates belongs to the person
running it. These are recordings of somebody talking, so the rule is if
anything more obviously right here than it was for notes.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

# Every row says so, in the column a later count will group by. The value is a
# string rather than a boolean because the day a phone client exists it is a
# third value and not a second boolean.
SOURCE = "voice"

# How far apart the server's row timestamp and this turn may be and still be
# believed to be the same turn. The server writes `timespec="seconds"`, so a
# turn that spans a second boundary is normal and anything beyond a few is
# somebody else's row.
JOIN_SLACK = timedelta(seconds=30)


def link_to(log_path: str, user: str, when: datetime) -> tuple[dict | None, str]:
    """Find this turn in the server's own log. Returns (link, why-not).

    Reads the **last** line only. The server appends one row per turn and
    flushes as it goes, so the row for a turn that has just returned `done` is
    the tail -- unless another client interleaved, which is the case this
    refuses rather than guesses at.

    Never raises. A join is a convenience and a voice row that failed to
    acquire one is still a complete record of the turn.
    """
    if not log_path:
        return None, "server is not logging"
    path = Path(log_path)
    if not path.exists():
        return None, f"{log_path} not readable from here"
    try:
        with path.open("rb") as fh:
            tail = fh.readlines()[-1:]
    except OSError as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if not tail:
        return None, "server log is empty"
    try:
        row = json.loads(tail[0].decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        return None, f"tail row unreadable: {exc}"
    if row.get("user") != user:
        # Byte-identical or nothing. Two turns with the same words are a real
        # thing and the timestamp below separates them; two *different* turns
        # mean another client got in first and this join would be a lie.
        return None, "another turn was logged after this one"
    try:
        stamp = datetime.fromisoformat(row["ts"])
    except (KeyError, ValueError):
        return None, "tail row has no readable timestamp"
    if abs(stamp - when) > JOIN_SLACK:
        return None, "the matching row is too old to be this turn"
    return {"log": str(path), "session": row.get("session"),
            "turn": row.get("turn")}, ""


def voice_record(user: str, stages: dict, surface: dict, stt: dict,
                 tts: dict, said: dict, server: dict,
                 link: dict | None, link_why: str,
                 audio_ms: float, when: datetime | None = None) -> dict:
    """One turn as a row. Pure, so the guard asserts the shape with no socket.

    Same discipline as `sessionlog.turn_record`: every field is handed in by
    whoever knew it at the time, and nothing is re-derived by re-reading a
    transcript that has already lost the distinction.
    """
    return {
        "ts": (when or datetime.now().astimezone()).isoformat(timespec="seconds"),
        # The marker. Present on every row this file writes and the reason the
        # file exists.
        "source": SOURCE,
        # **The scarce half, and here it is scarcer than usual.** A typed turn
        # can be retyped; this one is what a transcriber made of a sound that
        # is gone. Verbatim, exactly as it went on the wire -- if this string
        # ever differs from the frame's `user`, the transcript rule was broken
        # somewhere upstream and this row is the evidence.
        "user": user,
        # docs/PLAN-VOICE.md §9's whole deliverable, per turn.
        "surface": surface,
        # What produced it. Two reads under different settings are not one
        # measurement -- `harness/surfacegrid.py`'s ground rule 13.
        "stt": stt,
        "audio_ms": round(audio_ms, 1),
        "stages": {k: (None if v is None else round(v, 1))
                   for k, v in stages.items()},
        # What was said back, and what had to be cleaned off it first.
        "said": said,
        "tts": tts,
        # The server's own account of the turn: its `ms`, its outcome, the
        # say's author. Copied rather than joined, because a row that cannot
        # find its join is still worth reading.
        "server": server,
        "link": link,
        **({"link_why": link_why} if link is None and link_why else {}),
    }


class VoiceLog:
    """An append-only JSONL sink, or nothing at all.

    `path=None` is a working no-op rather than a branch every caller repeats --
    `harness/sessionlog.py`'s shape, for the same reason, and a logging failure
    must never take a turn with it. The person has already heard the answer by
    the time this runs.
    """

    def __init__(self, path: Path | str | None):
        self.path = Path(path) if path else None
        self.rows = 0
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, row: dict) -> dict | None:
        if self.path is None:
            return None
        try:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        except OSError as exc:
            print(f"-- voice log unwritable ({exc}); continuing without it")
            self.path = None
            return None
        self.rows += 1
        return row


def read_rows(path: Path | str) -> list[dict]:
    """Every voice row in a log, skipping any line that is not one.

    A half-written final line is what a killed process leaves and is not a
    reason to refuse the other fifty rows -- the same tolerance
    `SessionLog.append` buys by flushing per turn.
    """
    out: list[dict] = []
    p = Path(path)
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("source") == SOURCE:
            out.append(row)
    return out
