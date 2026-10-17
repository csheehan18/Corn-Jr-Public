"""Reading `packs/persona.md` -- his own facts, written by the person he's for.

`corn/persona.py` says what a `Persona` *is* and why it exists; this is the
half that touches the disk. The split is forced by `scripts/check_layering.py`
(`corn/` may not import `harness/`) and is the one `corn/steps.py` and
`harness/backends/document.py` already use: the type and the logic on the corn
side, the file on the harness side.

**Two files, because two people are described and only one of them is him.**

  * `persona.md` is his: the name this instance answers to, his birthday, any
    other day he should mark, and prose about himself that `packs.py` mounts
    as an ordinary doc so "where does your name come from" is answered locally
    rather than looked up on the internet.
  * `about-me.md` is the owner's, and already existed as prose. It gains the
    same optional header for the same reason the persona file has one: **the
    owner's birthday is the owner's fact**, and putting it in his file would
    have been filing it under the wrong person.

**The Book contract, verbatim.** A file that will not parse is dropped and
counted; a field that will not parse is dropped and counted while the rest of
the file stands; and a persona that fails entirely lands on
`corn.persona.DEFAULT`, which is the shipped behaviour, rather than on a dead
server. Seven working tools do not go down to protect one birthday.

The warnings name files and fields, because they print on the owner's own
console at startup and go nowhere else -- `packs.py`'s rule, and for the same
reason: `info` is published to every client and a persona line is the owner's
own sentence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from corn.persona import (DEFAULT, DEFAULT_BIRTHDAY_LEAD, DEFAULT_NAME, PERSON_BIRTHDAY,
                          Occasion, Persona, parse_when)

from .frontmatter import parse

PERSONA_FILE = "persona.md"
OWNER_FILE = "about-me.md"

_TRUE = frozenset({"true", "yes", "on", "1"})
_FALSE = frozenset({"false", "no", "off", "0"})


@dataclass
class Loaded:
    persona: Persona = DEFAULT
    warnings: list[str] = field(default_factory=list)
    rejected: int = 0

    def summary(self) -> dict:
        """What may be printed. The name and a count, never a line.

        The name is here because he says it out loud on every identity turn
        and there is nothing to protect; the occasion *lines* are the owner's
        own sentences and stay on this machine, so they are counted and not
        shown.
        """
        return {"name": self.persona.name,
                "occasions": len(self.persona.occasions),
                "rejected": self.rejected}


def _flag(text: str, default: bool = True) -> bool:
    low = text.strip().lower()
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    return default


def _read(path: Path, out: Loaded):
    """One file's header, or `None` when there is nothing usable in it."""
    if not path.is_file():
        return None
    try:
        front = parse(path.read_text(encoding="utf-8", errors="replace"))
    except Exception as exc:
        out.rejected += 1
        out.warnings.append(f"dropped {path.name}: {exc}")
        return None
    for problem in front.problems:
        out.warnings.append(f"{path.name}: {problem}")
    return front


def _occasions(front, path: Path, out: Loaded) -> list[Occasion]:
    """The `on:` list of one file. A bad entry is dropped, never the list."""
    made = []
    for n, item in enumerate(front.items.get("on", []), start=1):
        when = item.get("when", "")
        line = item.get("line", "")
        if not when or not line:
            out.warnings.append(
                f"{path.name}: occasion {n} needs both a when and a line")
            continue
        try:
            month, day, year = parse_when(when)
        except ValueError as exc:
            out.warnings.append(f"{path.name}: occasion {n} -- {exc}")
            continue
        made.append(Occasion(month, day, kind="on", line=line,
                             peppy=_flag(item.get("peppy", "true")),
                             year=year))
    return made


def _birthday(front, path: Path, out: Loaded, kind: str,
              who: str) -> Occasion | None:
    raw = front.fields.get("birthday", "")
    if not raw:
        return None
    try:
        month, day, year = parse_when(raw)
    except ValueError as exc:
        out.warnings.append(f"{path.name}: birthday -- {exc}")
        return None
    # No `line`: a birthday is composed at speak time by `corn/agent.py`, out
    # of a pool that had to pass `docs/VOICE.md`. See `corn/persona.py`'s
    # docstring for why a store gets to hold facts and not sentences.
    return Occasion(month, day, kind=kind, peppy=True, year=year, who=who)


def load(directory: str | Path) -> Loaded:
    """Read a pack folder's persona. Never raises; the Book contract.

    Order is what `Persona.on` reads as precedence when two occasions share a
    date: his birthday, the owner's, then whatever each file listed. A person
    born on Christmas Day hears about their birthday rather than about
    Christmas, which is the right way round.
    """
    out = Loaded()
    root = Path(directory)
    if not root.is_dir():
        return out

    mine = _read(root / PERSONA_FILE, out)
    theirs = _read(root / OWNER_FILE, out)
    if mine is None and theirs is None:
        return out

    name = DEFAULT_NAME
    occasions: list[Occasion] = []
    owner = theirs.fields.get("name", "") if theirs else ""

    if mine is not None:
        name = mine.fields.get("name", "").strip() or DEFAULT_NAME
        his = _birthday(mine, root / PERSONA_FILE, out, "birthday", name)
        if his is not None:
            occasions.append(his)
    if theirs is not None:
        yours = _birthday(theirs, root / OWNER_FILE, out, "owner_birthday", owner)
        if yours is not None:
            occasions.append(yours)
    if mine is not None:
        occasions += _occasions(mine, root / PERSONA_FILE, out)
    if theirs is not None:
        occasions += _occasions(theirs, root / OWNER_FILE, out)

    # The owner's `name:` is the field the birthday line already reads, and
    # it is now also what fills `{user}` in a trained sentence -- see
    # `Persona.speak`. One header, two readers, on purpose: the value is what
    # he calls the person, and a file that spells it once cannot say two
    # different things about it.
    out.persona = Persona(name=name, occasions=tuple(occasions),
                          user_name=owner.strip())
    return out


def people_birthdays(pack, lead: int = DEFAULT_BIRTHDAY_LEAD) -> tuple[list[Occasion], list[str]]:
    """`(occasions, warnings)`: a heads-up for every birthday in the people store.

    **The store is a pack table** (PLAN-PEOPLE §4), so there is no second
    file to read: any table in the loaded pack with a `Birthday` column is a
    table of people, one row a person. Each row with a date becomes a
    `person_birthday` occasion `lead` days ahead (`Persona.heads_up`; the
    owner's three, 2026-10-13), named the way the owner calls them -- the
    row's first alias where it has one, else its key. A date that will not
    parse is named and skipped, the Book contract; an empty cell is a person
    with no birthday written down, and says nothing.
    """
    made: list[Occasion] = []
    warnings: list[str] = []
    for table in pack.tables:
        col = next((i for i, c in enumerate(table.columns) if c.strip().lower() == "birthday"), None)
        if col is None:
            continue
        for key, cells in table.rows.items():
            raw = cells[col].strip()
            if not raw:
                continue
            try:
                month, day, year = parse_when(raw)
            except ValueError as exc:
                warnings.append(f"{table.name}: {table.display[key]}'s birthday -- {exc}")
                continue
            made.append(Occasion(month, day, kind=PERSON_BIRTHDAY, peppy=False, year=year,
                                 who=table.called.get(key, table.display[key]), lead=lead))
    return made, warnings
