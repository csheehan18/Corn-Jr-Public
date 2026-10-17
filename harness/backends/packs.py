"""Data packs -- the owner's own facts, answered before the web is asked.

**The table-backed `web_search` has answered out of a lookup table since the
first corpus, and a pack is that table with the owner's data in it.** `FACTS`
is an invented index the training slice was generated from; a folder of CSV
files about the things one person cares about -- game stats, a recipe index,
a reading list -- is a *real* index of the same shape. VISION §4's line
holds exactly here: the shipped artefact is user-neutral, and a running
instance specialises through its stores. The weights never know Pokemon
exists; this instance's `packs/` folder does.

**Two tiers, because structured and prose data want opposite machinery:**

  * A **CSV or TSV** becomes an exact-lookup table: first row is the header,
    first column is the key. "what's the base speed of charizard" is a row
    match plus a column match, and the answer is composed in code from the
    one cell that holds it. Deliberately *not* the neural extractor: a stats
    row is several same-type numbers in one clause, which is finding 66's
    paired-property danger zone at maximum density, and the first-taker rule
    would answer the HP column to every question. Exact lookup sidesteps the
    model's worst measured failure; the model routes and reads back, which
    are the two things it is measured to do at ceiling.
  * A **.txt or .md** becomes prose: the best-overlapping paragraph answers,
    with the full paragraph forwarded under `PASSAGE` so `--extract`'s
    reader can do to a local guide exactly what it does to a Wikipedia page.
    The reader is source-agnostic (VISION §5.1's addendum); this is the
    first local source to use that fact.

**The payloads are the search contract's four shapes and nothing else** --
the model reads shapes, and a pack that invented a fifth would be handing
the weights a structure they have never seen. A miss falls through to
whatever backend the pack wraps (the live web under `--search`, the trained
table without it), so packs can only add answers, never take any away. A
row hit with no readable column asks which column, in the clarify shape the
contact book trained; a query naming two rows asks which one, for the same
reason `place_call` does -- ambiguity handling belongs in code.

**Column matching has two tiers, and the second exists because the first
was measured failing people.** The lexical tier scores word overlap between
the question and the header, which is why "what's charizard's speed" works
and "how tall is charizard" fell to the clarify for a question no person
would call ambiguous (PLAN-CORPUS-GAPS §6, read on `corn_jr_260m_v4`
2026-08-30: the weights don't cover this either -- the class is absent from
the corpus, so the gap was nobody's). The synonym tier runs only when the
lexical tier found *nothing*: a tiny built-in table of generic English
attribute paraphrases (`tall` -> height, `quick` -> speed), and under it
the owner's own vocabulary from a `synonyms:` front-matter block in any
pack doc -- the persona pattern, because what the owner calls their columns
is the owner's data on VISION §4's terms, not something to ship in code or
weights. A lexical *tie* is never rescued: two columns fitting equally well
is what the clarify is for, and a synonym that overrode it would be
guessing, which is what this layer removes. A wrong synonym pick still
returns a real cell of the matched row -- the layer's asymmetry survives
the widening.

**Rows answer to aliases as well as keys** (`_take_aliases`, 2026-10-13,
PLAN-PEOPLE §4): a header cell `Aliases` holds `;`-separated other names for
the row, so a people table keyed `Ruth Avery` answers "when is Mum's
birthday". It is the row matcher's, never a column read back; an alias that
is another row's key is ignored and named, and one two rows claim asks which.

**A broken pack never stops the server** -- the `Book` argument, verbatim.
A file that will not parse is dropped and counted; the rest of the folder
keeps working; `summary()` carries counts and never contents, because
`info` is published to every client and pack contents are the owner's. The
warnings do name files and keys, because they are printed on the owner's own
console at startup and go nowhere else.

The `packs/` folder is personal data on the contact book's terms and the
default path is gitignored beside it.
"""

from __future__ import annotations

import csv
import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from corn.tools import PASSAGE

from .frontmatter import parse

DEFAULT_DIR = Path("packs")

MAX_ANSWER = 400          # the search backend's own bound, mirrored
MIN_PROSE_OVERLAP = 2     # query terms a paragraph must share to answer

_STOP = frozenset(
    "the a an of in on at is are was were what whats which who whos how "
    "does do did for to and or with about tell me look up whats s base "
    "many much".split()
)


_CLITIC = re.compile(r"'s?$")


# **One spelling, so the same question gets the same answer, 2026-09-06.**
# `docs/VOICE.md` rule 7 makes *his* spelling American and
# `scripts/check_agent.py` asserts it over the pools. Nothing ever made the
# *user's* input American, and a pack's headers come from whoever wrote the
# CSV -- so British in, American header (or the reverse) simply missed.
#
# The measurement that put this here, on the guard's own fixture, whose
# columns are Type, HP, Special Attack, Attack, Defense, Speed:
#
#     "charizard special defense"   ->  Charizard's Defense is 78.
#     "charizard special defence"   ->  Charizard's Special Attack is 109.
#
# Two spellings of one question, two different cells, and the second is a
# confident wrong number rather than a clarify -- `defence` reached no column
# at all, leaving `special` to hit Special Attack on its own.
#
# **Folded here rather than in `_SYNONYMS`, and the layer is the whole
# point.** A synonym is a different word for the same column and runs only
# after the lexical tier has found nothing; a spelling variant is the *same*
# word and has to be normalised before anything is matched, or it changes
# what the lexical tier sees. And because `_words` normalises the query, the
# column headers, the row keys and the prose alike, the fold is symmetric:
# a British header and an American question meet in the middle too.
#
# A closed list rather than a rule. `-our -> -or` would take "four" to "for"
# and `-ise -> -ize` would take "wise" to "wize"; every entry below is a word
# somebody would put in a column header or ask about one.
_BRITISH: dict[str, str] = {
    "defence": "defense", "defences": "defenses",
    "offence": "offense", "offences": "offenses",
    "licence": "license", "licences": "licenses",
    "practise": "practice", "pretence": "pretense",
    "colour": "color", "colours": "colors", "coloured": "colored",
    "flavour": "flavor", "flavours": "flavors",
    "armour": "armor", "harbour": "harbor", "humour": "humor",
    "labour": "labor", "neighbour": "neighbor", "neighbours": "neighbors",
    "favourite": "favorite", "favourites": "favorites",
    "behaviour": "behavior", "behaviours": "behaviors",
    "odour": "odor", "vapour": "vapor", "rumour": "rumor",
    "centre": "center", "centres": "centers",
    "fibre": "fiber", "fibres": "fibers", "calibre": "caliber",
    "litre": "liter", "litres": "liters",
    "metre": "meter", "metres": "meters",
    "kilometre": "kilometer", "kilometres": "kilometers",
    "millimetre": "millimeter", "centimetre": "centimeter",
    "theatre": "theater", "sombre": "somber", "spectre": "specter",
    "kilogramme": "kilogram", "gramme": "gram", "programme": "program",
    "grey": "gray", "storey": "story", "storeys": "stories",
    "catalogue": "catalog", "dialogue": "dialog", "analogue": "analog",
    "tyre": "tire", "tyres": "tires", "aluminium": "aluminum",
    "jewellery": "jewelry", "moustache": "mustache", "plough": "plow",
    "cheque": "check", "cheques": "checks", "draught": "draft",
    "aeroplane": "airplane", "speciality": "specialty",
    "organisation": "organization", "organisations": "organizations",
}


def _words(text: str) -> list[str]:
    """Lowercase word tokens, the possessive clitic off, spelling folded.

    `charizard's` and `charizard` have to come out as the same token, or the
    most natural way there is to ask a table question -- "what's charizard's
    speed" -- misses the owner's own table and goes to the web instead. The
    stripping is apostrophe-only and deliberately not stemming: a bare
    trailing `s` is left alone here, because `Chris` and `Ross` are people's
    names, and a matcher whose whole job is exactness does not get to guess
    at plurals. `_match_rows` handles the unpunctuated possessive its own
    way, from the side where guessing is safe.

    `_BRITISH` is applied last and per token, for the reason written above
    it: one spelling in, so the same question gets the same answer whichever
    side of the Atlantic wrote the query and the header.
    """
    return [_BRITISH.get(w, w)
            for w in (_CLITIC.sub("", t)
                      for t in re.findall(r"[a-z0-9']+", text.lower())) if w]


def _terms(query: str) -> list[str]:
    return [w for w in _words(query) if w not in _STOP]


# The built-in synonym tier: generic English attribute paraphrases, and only
# them. The bar for a row here is that any English speaker would accept the
# mapping without knowing what the table is about -- "how tall" asks for a
# height whatever is being measured. Domain vocabulary ("take a hit" meaning
# Defense, "fruit" meaning Yield) is the owner's and lives in a `synonyms:`
# front-matter block instead; a domain guess shipped here would be wrong in
# somebody's pack, silently. Keys and targets are matched and added as
# `_words` sequences; a multi-word key is a phrase, found on word boundaries
# the way `_match_rows` finds a name. `kind` and `sort` map to two targets
# because English does -- in a table carrying both Type and Variety the two
# hits tie, and a tie is the clarify, which is the right answer to a question
# that genuinely does not say which.
_SYNONYMS: tuple[tuple[str, str], ...] = (
    ("tall", "height"), ("high", "height"),
    ("quick", "speed"), ("fast", "speed"), ("swift", "speed"),
    ("old", "age"),
    ("heavy", "weight"), ("weigh", "weight"), ("weighs", "weight"),
    ("long", "length"), ("wide", "width"), ("deep", "depth"),
    ("big", "size"), ("large", "size"),
    ("kind", "type variety"), ("sort", "type variety"),
    ("health", "hp"),
    ("cost", "price"), ("price", "cost"),
    # Abbreviations people actually type at stats tables. Phrases stand
    # before their pieces so "sp atk" is read whole.
    ("sp atk", "special attack"), ("sp def", "special defense"),
    ("atk", "attack"), ("def", "defense"), ("spd", "speed"),
    # British spellings are **not** here -- see `_BRITISH`, which folds them
    # in `_words` instead. A synonym is a different word that means the same
    # column; "defence" is the same word. Putting it here would also have put
    # it behind the lexical tier, which is where it fails: "special defence"
    # ties or misfires because `special` reaches a column and `defence`
    # reaches nothing, and no synonym entry can run at that point.
)


@dataclass
class Table:
    name: str                    # file stem; the spoken source
    key_label: str               # header of the first column
    columns: list[str]           # remaining headers
    rows: dict[str, list[str]]   # key -> cell values, keyed lowercase
    display: dict[str, str]      # lowercase key -> the key as written
    duplicates: list[str] = field(default_factory=list)  # keys seen twice
    # `_words`-normalised alias phrase -> the lowercase keys that claim it,
    # from a reserved `Aliases` column (`_ALIASES_HEADER`). A list, because
    # two rows claiming one alias is an ambiguity to ask about, not a tie to
    # break silently.
    aliases: dict[str, list[str]] = field(default_factory=dict)
    alias_warnings: list[str] = field(default_factory=list)
    # lowercase key -> the row's first alias as written: what the owner calls
    # that person ("Mum" for `Ruth Avery`), and so what he says when he
    # brings them up unasked (`harness/backends/persona.py`).
    called: dict[str, str] = field(default_factory=dict)


@dataclass
class Pack:
    tables: list[Table] = field(default_factory=list)
    docs: list[tuple[str, str]] = field(default_factory=list)  # (name, text)
    warnings: list[str] = field(default_factory=list)
    rejected: int = 0
    # The owner's column vocabulary: (ask phrase, column words) pairs from
    # `synonyms:` blocks, `_words`-normalised at load. Folder-wide rather
    # than per-table -- the target words simply count toward whichever
    # header carries them, so one block serves every file and a target
    # naming no column in some table costs nothing there.
    synonyms: list[tuple[str, str]] = field(default_factory=list)

    def summary(self) -> dict:
        """What `info` may publish. Counts only -- never a cell."""
        return {"tables": len(self.tables), "docs": len(self.docs),
                "rejected": self.rejected}


def load(directory: str | Path = DEFAULT_DIR) -> Pack:
    """Read a pack folder. Never raises; the Book contract."""
    out = Pack()
    root = Path(directory)
    if not root.is_dir():
        out.warnings.append(f"no pack folder at {root}")
        return out
    for path in sorted(root.iterdir()):
        suffix = path.suffix.lower()
        try:
            if suffix in (".csv", ".tsv"):
                table = _load_table(path, "\t" if suffix == ".tsv" else ",")
                if table is None:
                    raise ValueError("needs a header row and one data row")
                out.tables.append(table)
                out.warnings.extend(f"{path.name}: {w}" for w in table.alias_warnings)
                if table.duplicates:
                    shown = ", ".join(sorted(set(table.duplicates))[:5])
                    out.warnings.append(
                        f"{path.name}: {len(table.duplicates)} row(s) with a "
                        f"key already seen, ignored ({shown})")
            elif suffix in (".txt", ".md"):
                # **The header comes off before the prose is indexed.** A
                # `---` block at the top of a file is configuration --
                # `harness/backends/persona.py` reads it -- and a paragraph
                # matcher handed `name: Corn-Jr` will happily answer a
                # question with it, out loud, as a sentence. A file that is
                # nothing but a header contributes no doc rather than an
                # empty one, because an empty doc is a name in `summary()`
                # that answers nothing.
                front = parse(path.read_text(encoding="utf-8",
                                             errors="replace"))
                if front.body.strip():
                    out.docs.append((path.stem, front.body))
                # A `synonyms:` list in any header teaches the column
                # matcher the owner's own vocabulary:
                #
                #     synonyms:
                #       - ask: take a hit
                #         column: Defense
                #
                # Malformed entries are named and skipped on the Book
                # pattern -- the rest of the block keeps working. An `ask`
                # that normalises to nothing ("???") could never match a
                # query and is a mistake worth hearing about.
                for entry in front.items.get("synonyms", []):
                    ask = " ".join(_words(entry.get("ask", "")))
                    target = " ".join(_words(entry.get("column", "")))
                    if ask and target:
                        out.synonyms.append((ask, target))
                    else:
                        out.warnings.append(
                            f"{path.name}: synonyms entry needs ask and "
                            f"column, got {entry}")
        except Exception as exc:
            out.rejected += 1
            out.warnings.append(f"dropped {path.name}: {exc}")
    return out


def _load_table(path: Path, delim: str) -> Table | None:
    with path.open("r", encoding="utf-8-sig", errors="replace",
                   newline="") as fh:
        rows = [r for r in csv.reader(fh, delimiter=delim) if any(r)]
    if len(rows) < 2 or len(rows[0]) < 2:
        return None
    header = [h.strip() for h in rows[0]]
    data: dict[str, list[str]] = {}
    display: dict[str, str] = {}
    duplicates: list[str] = []
    for r in rows[1:]:
        key = (r[0] or "").strip()
        if not key:
            continue
        if key.lower() in data:
            # First wins, for the cells and the spelling both. The two used
            # to disagree -- cells last-wins, spelling first-wins -- so a
            # file with a repeated key answered the last row's numbers under
            # the first row's name, silently. Either rule would have done;
            # what matters is that one rule covers both and that the owner
            # is told the other rows are sitting there.
            duplicates.append(key)
            continue
        cells = [c.strip() for c in r[1:]]
        cells += [""] * (len(header) - 1 - len(cells))
        data[key.lower()] = cells[:len(header) - 1]
        display[key.lower()] = key
    table = Table(path.stem, header[0], header[1:], data, display, duplicates)
    _drop_numbers(table)
    _take_aliases(table)
    return table


# **The people store keeps no numbers** (owner, 2026-10-13, PLAN-PEOPLE §9.3):
# nothing dials anyone but the owner, so a phone number is personal data with
# no consumer. A *people* table -- one with an `Aliases`, `Birthday` or
# `Relationship` column -- that carries a phone column has it dropped at load
# and named, so it is never answerable and never read back. Other tables are
# left alone: a stats table's `Number` is a Pokedex entry, not a phone.
_PEOPLE_MARKS = frozenset({"aliases", "birthday", "relationship"})
_PHONE_WORDS = frozenset({"phone", "mobile", "number", "tel", "telephone", "cell"})


def _drop_numbers(table: Table) -> None:
    heads = [" ".join(_words(c)) for c in table.columns]
    if not _PEOPLE_MARKS & set(heads):
        return
    drop = [i for i, h in enumerate(heads) if _PHONE_WORDS & set(h.split())]
    for i in reversed(drop):
        table.alias_warnings.append(
            f"column {table.columns[i]!r} dropped -- the people store keeps no "
            f"numbers (nothing dials anyone but you)")
        del table.columns[i]
        for cells in table.rows.values():
            del cells[i]


# **Aliases: the names a row answers to besides its key** (docs/PLAN-PEOPLE.md
# §4, ROADMAP H1). The column synonym tier resolves *columns*; a row had no
# equivalent -- the key was the first column and nothing else matched it, so
# "when is Mum's birthday" missed a row keyed `Ruth Avery`. A header cell
# reading `Aliases` (any case) is reserved: its cells are `;`-separated names,
# it leaves the answerable columns -- it is how a row is *found*, not a fact
# to read back -- and the row matcher consults it beside the keys.
#
# Two collisions, each decided toward the rule that never guesses:
#   * an alias equal to another row's key is dropped and named -- the name
#     the owner wrote as a key is the exact one, and a nickname that
#     silently redirected it would be the wrong row read back confidently;
#   * an alias two rows claim stays on both, so a question using it matches
#     two rows and asks which, the branch two matched keys already take.
_ALIASES_HEADER = "aliases"


def _take_aliases(table: Table) -> None:
    idx = next((i for i, c in enumerate(table.columns)
                if " ".join(_words(c)) == _ALIASES_HEADER), None)
    if idx is None:
        return
    del table.columns[idx]
    keys = {" ".join(_words(k)): k for k in table.rows}
    for key, cells in table.rows.items():
        raw = cells.pop(idx)
        for alias in (a.strip() for a in raw.split(";")):
            phrase = " ".join(_words(alias))
            if not phrase or phrase == " ".join(_words(key)):
                continue
            if phrase in keys:
                table.alias_warnings.append(
                    f"alias {alias!r} of {table.display[key]} is another "
                    f"row's key ({table.display[keys[phrase]]}), ignored")
                continue
            claimed = table.aliases.setdefault(phrase, [])
            if key not in claimed:
                claimed.append(key)
            table.called.setdefault(key, alias)
    # A name two rows answer to says nobody in particular, so it is never
    # what he calls either of them.
    table.called = {k: a for k, a in table.called.items()
                    if len(table.aliases[" ".join(_words(a))]) == 1}
    for phrase, owners in table.aliases.items():
        if len(owners) > 1:
            names = ", ".join(sorted(table.display[k] for k in owners))
            table.alias_warnings.append(
                f"alias {phrase!r} is claimed by {names}; a question using "
                f"it asks which")


def _match_rows(table: Table, query: str) -> list[str]:
    """Keys whose full name appears in the query, on word boundaries.

    Word boundaries are what keep "Mew" out of a question about Mewtwo.
    Multi-word keys match as phrases, so "Mr. Mime" is found by the words a
    person would actually say.

    A trailing `s` on the *key* is optional, which is how "charizards speed"
    -- the possessive nobody punctuates -- reaches the Charizard row. Adding
    an `s` to the key is safe in the way that stripping one off the query is
    not: it can only ever match more of what the owner actually wrote down,
    and a table holding both `Mew` and `Mews` gets two hits and asks, which
    is the behaviour ambiguity already has.
    """
    q = " ".join(_words(query))
    # Every name a row answers to: its key, and its aliases (`_take_aliases`)
    # -- matched by the same rule, so "mums birthday" reaches the row
    # aliased `Mum` the way "charizards speed" reaches Charizard.
    names = [(" ".join(_words(key)), [key]) for key in table.rows]
    names += list(table.aliases.items())
    hits = [(phrase, keys) for phrase, keys in names
            if phrase and re.search(rf"(?:^| ){re.escape(phrase)}s?(?: |$)", q)]
    # A name contained in a longer matched name was matched by accident of
    # phrasing; the longer, more specific name wins -- an alias `Sam` inside
    # "sam jones" included.
    kept = [keys for phrase, keys in hits
            if not any(phrase != o and f" {phrase} " in f" {o} " for o, _ in hits)]
    out: list[str] = []
    for keys in kept:
        out += [k for k in keys if k not in out]
    return out


def _best_column(table: Table, terms: set[str]) -> tuple[int | None, bool]:
    """`(best, tied)` over one term set -- the scoring both tiers share.

    Scored on how much of the *column* the question accounted for, not on
    how many words happened to overlap. `Attack` and `Special Attack` each
    share exactly one word with "what is the attack of charizard", and the
    first build handed it to whichever stood earlier in the header -- which
    is finding 66's first-taker rule, rebuilt in code, inside the one layer
    whose whole reason for existing is to sidestep it. So: most-matched wins
    first, which keeps "special attack" on the longer name; tightest fit
    breaks the tie, which gives a bare "attack" the column that is nothing
    but attack.
    """
    best: int | None = None
    best_score = (0, 0.0)
    tied = False
    for i, col in enumerate(table.columns):
        words = set(_words(col))
        hit = len(words & terms)
        if not hit:
            continue
        score = (hit, hit / len(words))
        if score > best_score:
            best, best_score, tied = i, score, False
        elif score == best_score:
            tied = True
    return best, tied


def _match_column(table: Table, query: str) -> int | None:
    """The lexical tier alone: the column the question asked for by its own
    words, or `None` when it named no one.

    A real tie -- `Home Phone` and `Work Phone` against "dave's phone" --
    returns `None` and comes out as the clarify the contact book trained.
    Asking is what ambiguity is for; guessing is what this removes.

    **This function is frozen as the instrument's definition.**
    `evals/packs_column.jsonl`'s worded/paraphrase halves are *defined* as
    what this tier resolves and what it cannot (`check_packs_column.py`
    asserts it item by item), so the synonym tier lives in
    `_match_column_wide` rather than here -- widening this function would
    silently relabel the halves of every card already read against them.
    """
    best, tied = _best_column(table, set(_terms(query)))
    return None if tied else best


def _synonym_terms(query: str, synonyms: list[tuple[str, str]]) -> set[str]:
    """The column words the query's paraphrases stand for.

    Built-ins first, the owner's after -- order is cosmetic, since all hits
    are pooled into one term set and scored together. Asks match as phrases
    on word boundaries, the way `_match_rows` finds a name, so `sp atk` is
    read whole and `old` does not fire inside `golden`.
    """
    q = " ".join(_words(query))
    extra: set[str] = set()
    for ask, target in tuple(_SYNONYMS) + tuple(synonyms):
        if re.search(rf"(?:^| ){re.escape(ask)}(?: |$)", q):
            extra.update(target.split())
    return extra


def _match_column_wide(table: Table, query: str,
                       synonyms: list[tuple[str, str]] | None = None) -> int | None:
    """Both tiers: the lexical verdict where it found anything, synonyms
    only where it found nothing at all.

    The order is the safety property. A lexical *hit* stands -- a synonym
    can never take a question away from the column it literally named. A
    lexical *tie* stands too, as `None`: two columns fitting equally well is
    what the clarify is for, and a synonym that broke the tie would be
    guessing between `Home Phone` and `Work Phone` on a hunch the owner
    never wrote down. Only a question whose own words reached no column at
    all -- "how tall is the fenwhistle" against `Height (m)` -- gets the
    second reading, and a tie *inside* that reading is a clarify for the
    same reason.
    """
    terms = set(_terms(query))
    best, tied = _best_column(table, terms)
    if best is not None or tied:
        return None if tied else best
    extra = _synonym_terms(query, synonyms or [])
    if not extra:
        return None
    best, tied = _best_column(table, terms | extra)
    return None if tied else best


# Words that ask for the row rather than a cell. Matched as terms, never as
# substrings, and deliberately explicit: "tell me about charizard" stays a
# clarify (the guard asserts it), because "about" promises nothing about
# wanting nine numbers read out, while "charizard's base stats" is a person
# asking for the table's own shape. "base" is already a stop word, so the
# plural here is the whole signal.
_ROW_ASKS = frozenset({"stats", "info", "information", "details"})


def _row_answer(table: Table, key: str, query: str) -> dict:
    """The whole row, composed the way a single cell is.

    Empty cells are skipped rather than read as blanks, and the composed
    string is bounded by the same MAX_ANSWER every other answer respects --
    a fifty-column table reads its first columns and stops, which is the
    search contract's own truncation rule rather than a new one.
    """
    name = table.display[key]
    parts = [f"{label} {value}"
             for label, value in zip(table.columns, table.rows[key]) if value]
    answer = f"{name}: " + ", ".join(parts) + "."
    return {"answer": answer[:MAX_ANSWER],
            "source": table.name, "query": query}


def _table_answer(pack: Pack, query: str) -> tuple[dict | None, dict | None]:
    """`(hard hit, soft clarify)` -- and the split is the fix for a real bug.

    The first build returned the clarify eagerly, and "why does charizard
    struggle against rock moves" matched the Charizard *row*, found no
    column called "why", and asked "Which one -- Type, HP, ...?" while the
    prose guide holding the actual answer was never consulted. So a row
    match without a column match is a *soft* result: the caller lets prose
    answer first and speaks the clarify only when nothing local can do
    better. Two matched rows stay soft for the same reason.
    """
    soft: dict | None = None
    for table in pack.tables:
        keys = _match_rows(table, query)
        if not keys:
            continue
        if len(keys) > 1:
            names = sorted(table.display[k] for k in keys)
            listed = " or ".join(names) if len(names) == 2 else (
                ", ".join(names[:-1]) + ", or " + names[-1])
            soft = soft or {"ok": False, "reason": "ambiguous",
                            "clarify": f"One at a time -- {listed}?"}
            continue
        key = keys[0]
        col = _match_column_wide(table, query, pack.synonyms)
        if col is None or not table.rows[key][col]:
            # A named column always beats the collective read -- the check
            # sits here, after both matcher tiers had their chance, so
            # "speed stats" is still the Speed cell and only a question that
            # named no column can ask for the row.
            if _ROW_ASKS & set(_terms(query)):
                return _row_answer(table, key, query), None
            cols = ", ".join(table.columns[:8])
            soft = soft or {"ok": False, "reason": "ambiguous",
                            "clarify": f"Which one -- {cols}?"}
            continue
        name, label = table.display[key], table.columns[col]
        value = table.rows[key][col]
        return ({"answer": f"{name}'s {label} is {value}."[:MAX_ANSWER],
                 "source": table.name, "query": query}, None)
    return None, soft


def _paragraphs(pack: Pack) -> list[tuple[str, str, set]]:
    """`(doc name, paragraph, its word set)` for every paragraph in the pack."""
    out = []
    for name, text in pack.docs:
        for para in re.split(r"\n\s*\n", text):
            para = " ".join(para.split())
            if para:
                out.append((name, para, set(_words(para))))
    return out


def _prose_answer(pack: Pack, query: str) -> dict | None:
    """The paragraph that best answers `query`, or None.

    **Admission is raw overlap; the ranking is by how *informative* the
    overlap is, and the two are separate on purpose.** A count of shared
    words decides whether a paragraph is a candidate at all
    (`MIN_PROSE_OVERLAP`, unchanged) -- and it must stay a raw count, because
    the queries `corn.agent.user_identity_request` composes are made almost
    entirely of function words: "who i am" is `{i, am}` and "my name" is
    `{my, name}` after `_terms`, and a stop list wide enough to fix the bug
    below would delete those queries entirely.

    What the count cannot do is *choose*. Measured 2026-09-06 on the shipped
    pack, "what should i check first against charizard" put two paragraphs on
    exactly two shared words each:

        about-me       {i, should}          "I should be called Corn."
        pokemon-guide  {charizard, against} "Charizard struggles against rock
                                             moves because..."

    and the first won, because `>` keeps the earliest and `pack.docs` is
    alphabetical. So a question about a Pokemon was answered out of the
    owner's identity file, decided by a filename. Both halves of that are
    wrong: the answer, and that `about-me.md` -- the one document in a pack
    that is *about a person* -- was the one a tie handed the microphone to.

    The fix is to weight each shared word by how many paragraphs contain it,
    so a word the whole pack says (`i`, `should`) counts for a fraction of a
    word only this paragraph says (`charizard`). That is ordinary inverse
    document frequency and nothing cleverer; the pack is a few dozen
    paragraphs, so it is recomputed per query rather than cached, and the
    admission gate above it does not move -- exactly the same candidates are
    considered as before, and only the winner among them changes.
    """
    terms = set(_terms(query))
    if not terms:
        return None
    paras = _paragraphs(pack)
    if not paras:
        return None
    freq: dict[str, int] = {}
    for _, _, words in paras:
        for w in words & terms:
            freq[w] = freq.get(w, 0) + 1
    best: tuple[float, int, str, str] | None = None
    for name, para, words in paras:
        shared = terms & words
        if len(shared) < MIN_PROSE_OVERLAP:
            continue
        # 1/df, so a word in every paragraph is worth little and a word in
        # one is worth all of itself. Raw overlap stays as the tiebreak under
        # it, and the document order under that, so the ranking is total and
        # the same query always answers the same way.
        score = sum(1.0 / freq[w] for w in shared)
        if best is None or (score, len(shared)) > (best[0], best[1]):
            best = (score, len(shared), name, para)
    if best is None:
        return None
    _, _, name, para = best
    lead = re.split(r"(?<=[.!?])\s", para)[0][:MAX_ANSWER]
    out = {"answer": lead, "source": name, "query": query}
    if len(para) > len(lead):
        out[PASSAGE] = para
    return out


def _takes_keywords(fallback: Callable) -> bool:
    """Whether this fallback can be handed `avoid` -- read once, from the
    signature, rather than discovered by calling it.

    The wrapper used to find out by calling and catching `TypeError`, and
    that catch was wider than its reason. A `TypeError` raised *inside* a
    live provider looks exactly like an old signature from out here, and the
    retry that followed dropped `avoid` on the way -- answering a
    second-source request out of the very source it had just been told not
    to ask again. Now a bug in a provider is a bug, loudly, and only a
    provider that genuinely cannot be told to skip a source is called the
    old way. Anything unintrospectable is treated as the old shape, which
    every provider in this project accepts.
    """
    try:
        params = inspect.signature(fallback).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(p.kind is p.VAR_KEYWORD or p.name == "avoid" for p in params)


def pack_search(pack: Pack, fallback: Callable[[str], dict]) -> Callable[[str], dict]:
    """The search backend with the owner's facts in front of it.

    An exact table hit answers first; prose answers next because it is the
    owner's own text; a table *clarify* comes only after prose has had its
    chance (see `_table_answer` for the bug that ordering fixes); and
    everything else falls through untouched -- a pack can only add answers,
    never take any away, which is the reduction-is-the-floor asymmetry
    applied to a whole source.
    """
    takes_kw = _takes_keywords(fallback)

    def search(query: str, **kw) -> dict:
        # A second-source request avoids the pack too when the pack answered
        # first -- the owner's own table agreeing with itself is not
        # corroboration. `avoid` naming a pack file skips the local tiers.
        avoid = kw.get("avoid") or ()
        local = None
        if not any(a in {t.name for t in pack.tables} | {n for n, _ in pack.docs}
                   for a in avoid):
            hard, soft = _table_answer(pack, query)
            local = hard or _prose_answer(pack, query) or soft
        if local is not None:
            return local
        # A fallback that predates `avoid` -- the trained table, an older
        # provider -- is called plainly. It cannot skip a source, so the
        # caller's own source check is the net there.
        return fallback(query, **kw) if takes_kw else fallback(query)
    return search
