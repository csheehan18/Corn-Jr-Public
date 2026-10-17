"""Writing the pack files the forms edit. No framework: the guard drives it.

The packs folder is hand-edited by design, and the studio does not change
that: what these writers produce is exactly what a person would have typed --
the front-matter shape `harness/backends/frontmatter.py` parses and
`examples/persona.md` demonstrates. The round trip is the contract:
`scripts/check_studio.py` writes with these functions and reads back with the
real parser, because a writer checked against its own reading is checked
against nothing.

Three files get forms:

- `persona.md` -- who *he* is: `name:`, `birthday:`, dated `on:` occasions,
  and prose.
- `about-me.md` -- the *owner's* facts. Prose only from the form's point of
  view; an existing header is preserved verbatim-in-meaning (fields and
  items are re-rendered, never dropped).
- `vocab.md` -- the one home for UI-added `synonyms:` entries, so the studio
  never edits the header of a file it did not create. Modelled on
  `examples/stats-vocab.md`; the folder-wide semantics mean one file serves
  every table.
"""

from __future__ import annotations

import csv
from pathlib import Path

from ..backends.frontmatter import Front, parse

PERSONA = "persona.md"
ABOUT = "about-me.md"
VOCAB = "vocab.md"

_VOCAB_COMMENT = (
    "# Column vocabulary added from the studio's Packs page. `ask` is a\n"
    "# phrase the way you say it; `column` is the header it should count\n"
    "# toward, in any table in this folder. See examples/stats-vocab.md.\n"
)


def read(path: Path) -> Front:
    """The parsed file, or an empty Front for one that does not exist yet."""
    p = Path(path)
    if not p.exists():
        return Front()
    return parse(p.read_text(encoding="utf-8", errors="replace"))


def render(front: Front) -> str:
    """A Front back to text, in the exact shape `parse` reads.

    Fields first, then each list, then the body -- comments are the one
    thing parsing drops, which is why `write_vocab` re-adds its own and the
    persona writer never had any.
    """
    if not front.fields and not front.items:
        return front.body
    lines = ["---"]
    for k, v in front.fields.items():
        lines.append(f"{k}: {v}")
    for key, items in front.items.items():
        lines.append(f"{key}:")
        for item in items:
            first = True
            for k, v in item.items():
                lines.append(f"  {'- ' if first else '  '}{k}: {v}")
                first = False
    lines.append("---")
    body = front.body.strip("\n")
    return "\n".join(lines) + ("\n\n" + body + "\n" if body else "\n")


def write_persona(path: Path, name: str, birthday: str,
                  occasions: list[dict], body: str) -> None:
    """`persona.md` from the form. Empty name/birthday keys are omitted, an
    empty occasions list omits `on:` entirely -- absent and empty read the
    same and absent is what a hand would write."""
    front = Front()
    if name.strip():
        front.fields["name"] = name.strip()
    if birthday.strip():
        front.fields["birthday"] = birthday.strip()
    kept = []
    for o in occasions:
        when = str(o.get("when", "")).strip()
        line = str(o.get("line", "")).strip()
        if not when or not line:
            continue
        entry = {"when": when, "line": line}
        if o.get("peppy") is not None:
            entry["peppy"] = "true" if o["peppy"] in (True, "true") else "false"
        kept.append(entry)
    if kept:
        front.items["on"] = kept
    front.body = body
    Path(path).write_text(render(front), encoding="utf-8")


def write_about(path: Path, body: str) -> None:
    """`about-me.md` with a new body and everything else it had kept."""
    front = read(path)
    front.body = body
    Path(path).write_text(render(front), encoding="utf-8")


def synonyms(path: Path) -> list[tuple[str, str]]:
    """The vocab file's own `(ask, column)` pairs, as written -- not the
    folder-wide normalised view, which is `packs.load`'s to give."""
    front = read(path)
    out = []
    for entry in front.items.get("synonyms", []):
        ask, column = entry.get("ask", ""), entry.get("column", "")
        if ask and column:
            out.append((ask, column))
    return out


def write_vocab(path: Path, entries: list[tuple[str, str]]) -> None:
    """The whole vocab file from a list of pairs. Rewritten rather than
    appended, so removing an entry in the form removes it on disk."""
    lines = ["---", _VOCAB_COMMENT.rstrip("\n"), "synonyms:"]
    for ask, column in entries:
        lines.append(f"  - ask: {ask}")
        lines.append(f"    column: {column}")
    lines.append("---")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Editing the files themselves -- tables as grids, prose as text
#
# The rules below are `harness/backends/packs.py:_load_table`'s, restated as
# lint rather than as silent drops: first row is the header, first column is
# the key, at least two columns and one data row, a repeated key keeps its
# first row, a blank key drops its row. The editor shows those before Save so
# the loader never has to.

TABLE_SUFFIXES = (".csv", ".tsv")
TEXT_SUFFIXES = (".txt", ".md")


def delimiter(path: Path) -> str:
    return "\t" if Path(path).suffix.lower() == ".tsv" else ","


def read_table(path: Path) -> tuple[list[str], list[list[str]]]:
    """`(header, rows)` exactly as the file has them, rectangular.

    Blank lines are dropped (the loader drops them too). Rows shorter than the
    header are padded; a row *longer* than the header widens the header with
    blank names rather than losing cells -- `lint_table` then names the blank
    columns, which is the honest version of the loader's truncation."""
    p = Path(path)
    if not p.exists():
        return [], []
    with p.open("r", encoding="utf-8-sig", errors="replace", newline="") as fh:
        rows = [r for r in csv.reader(fh, delimiter=delimiter(p)) if any(r)]
    if not rows:
        return [], []
    header = [h.strip() for h in rows[0]]
    width = max(len(header), *(len(r) for r in rows[1:])) if rows[1:] \
        else len(header)
    header += [""] * (width - len(header))
    data = []
    for r in rows[1:]:
        cells = [c.strip() for c in r]
        cells += [""] * (width - len(cells))
        data.append(cells)
    return header, data


def lint_table(header: list[str], rows: list[list[str]]
               ) -> tuple[list[str], list[str]]:
    """`(blocking, warnings)`. Blocking means the loader would drop the whole
    file; a warning means it would drop or ignore some rows."""
    blocking: list[str] = []
    warnings: list[str] = []
    if len(header) < 2:
        blocking.append("a table needs a key column and at least one more "
                        "column")
    keyed = [r for r in rows if r and r[0].strip()]
    if not keyed:
        blocking.append("a table needs at least one data row with a key in "
                        "the first column")
    blank_names = [i + 1 for i, h in enumerate(header) if not h.strip()]
    if blank_names:
        warnings.append(f"column(s) {blank_names} have no header name, so "
                        f"no question can name them")
    blank_keys = [i + 1 for i, r in enumerate(rows) if not (r and r[0].strip())]
    if blank_keys:
        warnings.append(f"row(s) {blank_keys} have an empty key and will be "
                        f"dropped")
    seen: dict[str, tuple[int, str]] = {}
    dups: list[str] = []
    for i, r in enumerate(rows):
        key = r[0].strip().lower() if r else ""
        if not key:
            continue
        if key in seen:
            # Named by the spelling that is kept -- the first row's, which
            # is the loader's rule for the cells and the display both.
            first_row, first_spelling = seen[key]
            dups.append(f"{first_spelling!r} (rows {first_row} and {i + 1})")
        else:
            seen[key] = (i + 1, r[0].strip())
    if dups:
        warnings.append("repeated key(s), only the first row of each is "
                        "answered from: " + ", ".join(dups[:5])
                        + (" ..." if len(dups) > 5 else ""))
    empty_cols = [h for j, h in enumerate(header[1:], start=1)
                  if h.strip() and rows and all(
                      len(r) <= j or not r[j].strip() for r in rows)]
    if empty_cols:
        warnings.append(f"column(s) {empty_cols} are empty in every row")
    return blocking, warnings


def write_table(path: Path, header: list[str], rows: list[list[str]]) -> None:
    """The grid back to disk, in the loader's dialect for the suffix. Cells
    are written as given -- the loader strips on read, so trailing spaces cost
    nothing, but a person's own quoting is `csv`'s to decide."""
    p = Path(path)
    with p.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter=delimiter(p), lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(list(r) + [""] * (len(header) - len(r))
                       if len(r) < len(header) else list(r)[:len(header)])


def read_text(path: Path) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() \
        else ""


def write_text(path: Path, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8")


def valid_name(name: str) -> str | None:
    """Why a new pack file name will not do, or None. Basename only, one of
    the four suffixes, nothing the loader ignores."""
    name = name.strip()
    if not name:
        return "the file needs a name"
    if name != Path(name).name or name in (".", ".."):
        return "a bare file name, not a path"
    if Path(name).suffix.lower() not in TABLE_SUFFIXES + TEXT_SUFFIXES:
        return ("the name needs one of " + ", ".join(
            TABLE_SUFFIXES + TEXT_SUFFIXES) + " -- nothing else loads")
    if not Path(name).stem.strip():
        return "the name needs something before the dot"
    return None


def create(path: Path) -> None:
    """A new, empty pack file of the kind its suffix says. A table starts as a
    header row only, which `lint_table` will call blocking until a row is
    added -- an example row would be a fact he might read out loud."""
    p = Path(path)
    if p.exists():
        raise FileExistsError(p.name)
    if p.suffix.lower() in TABLE_SUFFIXES:
        write_table(p, ["Name", "Value"], [])
    else:
        write_text(p, "")
