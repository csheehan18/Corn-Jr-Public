"""Which tree produced a scorecard. One line of JSON, written by every harness.

**The gap this closes is the one `harness/results/README.md` already names.**
That file says a file here "is a receipt for a finding", and then admits the
receipt is missing its most important field: two runs are comparable "when they
were written by the same `checkup/N` against an unedited case list, which is a
claim about the working tree rather than about the files". A claim about the
working tree is exactly what a revision is, and nothing was recording it.

`docs/PLAN-P3-RULERS.md`'s fourth ground rule turns that into a requirement:
numbers taken before the 2026-08-26 runtime changes are **not comparable** with
numbers after, and a card that cannot say which side of that line it sits on
cannot be used for a before-and-after at all.

**`dirty` is the field that matters, and it is not a warning about hygiene.**
Every one of those runtime changes lived in an uncommitted working tree on the
day this was written, so `rev` alone would have named a parent commit that does
not contain the behaviour being measured -- a provenance field that is
confidently wrong, which is worse than none. A dirty card says "this revision,
plus edits nobody can reconstruct", and a reader who needs more than that knows
to go and get the diff.

Never raises and never blocks a run: a checkout with no git, or no `git` on the
path, reports `rev: null` and the measurement goes ahead. A harness that
refused to score because it could not find a commit hash would be spending a
GPU-hour on a bookkeeping failure.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(("git", *args), cwd=ROOT, capture_output=True,
                             text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def revision() -> dict:
    """`{"rev": ..., "dirty": ...}` for the tree this process was started from.

    `dirty` is `None` rather than `False` when the status could not be read, so
    "clean" and "unknown" stay distinguishable -- the same distinction
    `harness/server.py` makes between a log that is off and a log that is
    somewhere unexpected.
    """
    rev = _git("rev-parse", "--short", "HEAD")
    status = _git("status", "--porcelain")
    return {"rev": rev, "dirty": None if status is None else bool(status)}


def line(prov: dict | None = None) -> str:
    """The one-line form a harness prints above its first turn."""
    prov = revision() if prov is None else prov
    if prov.get("rev") is None:
        return "revision   unknown (no git here)"
    dirty = prov.get("dirty")
    tail = ("" if dirty is False else
            " + uncommitted edits" if dirty else " (working tree unread)")
    return f"revision   {prov['rev']}{tail}"
