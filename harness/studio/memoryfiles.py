"""What a running instance has written down, read back for the Memory tab.

Four stores, all per-machine and all gitignored on `contacts.json`'s terms:

- the day log (`notes.jsonl`, `corn/agent.py:DayLog`) -- one `{date, text,
  title?}` line per `save_note`; `recall_day` reads it back by date.
- the schedule (`schedule.jsonl`, `harness/backends/schedule.py`) -- actions
  that fire later. Read-only here: the `Scheduler` holds its entries in
  memory and rewrites the file on every mutation, so an edit from outside the
  process would be overwritten by the next one. It is also not yet reachable
  from the model, which the page says.
- the occasion marker (`persona_state.json`, `corn/persona.py:Marker`) -- the
  last day he mentioned an occasion, so a restart does not repeat it.
- the turn log (`Saved Sessions/turns.jsonl`, `harness/sessionlog.py`) -- every
  turn, structured, for a corpus builder. Real conversations; the most
  personal file the repo produces.

Deleting a note or clearing the turn log while the server is up is safe:
`DayLog` and `SessionLog` open the file per call and cache nothing, and the
`Marker` reads on every check. No web framework, so the guard can drive the
reads and the rewrites against a temp directory.
"""

from __future__ import annotations

import json
from pathlib import Path


def read_jsonl(path: Path) -> tuple[list[dict], int]:
    """`(rows, bad)` -- every parseable object line, and how many lines were
    not one. Never raises; a missing file is an empty store."""
    p = Path(path)
    if not p.exists():
        return [], 0
    rows, bad = [], 0
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        if isinstance(row, dict):
            rows.append(row)
        else:
            bad += 1
    return rows, bad


def notes(path: Path) -> list[dict]:
    """The day log, newest date first, each row carrying its `_line` index so
    `delete_note` can name it."""
    rows, _ = read_jsonl(path)
    for i, r in enumerate(rows):
        r["_line"] = i
    return sorted(rows, key=lambda r: (r.get("date", ""), r["_line"]),
                  reverse=True)


def delete_note(path: Path, line: int) -> bool:
    """Drop one row by its `_line` index and rewrite the file. False when
    the index is out of range (the file changed under the page)."""
    rows, _ = read_jsonl(path)
    if not 0 <= line < len(rows):
        return False
    del rows[line]
    text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    Path(path).write_text(text, encoding="utf-8")
    return True


def schedule(path: Path) -> list[dict]:
    rows, _ = read_jsonl(path)
    return sorted(rows, key=lambda r: r.get("at", ""))


def marker(path: Path) -> str | None:
    """The ISO date the marker holds, or None for no marker."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        row = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return row.get("last_occasion") if isinstance(row, dict) else None


def turns(path: Path, last: int = 20) -> tuple[int, list[dict]]:
    """`(count, tail)` of the turn log -- the number of recorded turns and the
    last `last` of them, oldest first."""
    rows, _ = read_jsonl(path)
    return len(rows), rows[-last:] if last else []


def turn_summary(row: dict) -> str:
    """One line per turn for a listing: when, what was said, what he said.
    Reads the `sessionlog.turn_record` shape and degrades to the keys it
    finds."""
    when = str(row.get("ts", ""))[:16].replace("T", " ")
    user = str(row.get("user", ""))
    said = ""
    say = row.get("say")
    if isinstance(say, dict):
        said = str(say.get("text", ""))
    elif isinstance(say, str):
        said = say
    return f"{when}  > {user}" + (f"  --  {said}" if said else "")


def remove(path: Path) -> bool:
    """Delete a store file. True if there was one."""
    p = Path(path)
    if p.exists():
        p.unlink()
        return True
    return False


def saved_sessions(folder: Path) -> list[tuple[str, int]]:
    """`(name, bytes)` for every prose transcript in the folder."""
    d = Path(folder)
    if not d.is_dir():
        return []
    return sorted((p.name, p.stat().st_size) for p in d.glob("*.txt"))
