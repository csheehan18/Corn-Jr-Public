"""One character, crossed over every behaviour that already reads at ceiling.

**The corpus carries exactly one surface form of a user turn, and that is a
count rather than a hypothesis.** `docs/PLAN-FINETUNE-V4.md` entry 0 counted all
6,603,586 user turns in the `mix_v4_5b` slices: a terminal question mark means
`resolve_date` (2,268,194 calls) or it means chat (173,785 turns), and it has
never once meant `decline`, `place_call`, `send_text`, `save_note` or
`ask_agent`. `web_search` runs 298,368 unpunctuated against 993 punctuated -- a
300:1 prior against the surface form a user is most likely to type. All-caps is
15 rows in 6.6M.

So the corpus taught every routing behaviour this project has under one
orthography, and nothing has ever measured what survives the others. That is
what this grid is: **the same trained carriers, transformed, scored on the same
gold their home cells score them on.** Four cases crossed with two terminal
punctuations, over five carrier families that read at or near ceiling in their
base form.

    routed          the first **model-authored** call of the turn is the gold
                    the carrier's home cell expects. A runtime-authored call is
                    excluded and counted on its own line, `toolgrid`'s ground
                    rule 2
    base column     `lower` + bare is the form the home cells read. It is in
                    the table so drift is visible beside the axis rather than
                    argued about afterwards -- a fresh decode of a known
                    ceiling is the control this grid cannot do without

**The base form is the control and it is not optional.** Without it a low
`upper` cell reads as "shouting falls out of the vocabulary" when it may be
"this instrument's carriers are harder than the cells they came from", and
those call for different work. Same argument `searchgrid`'s invented column
makes, applied to orthography.

**What this grid must not be asked.** It says nothing about `resolve_date`'s
temporal carriers, and they are deliberately absent: the corpus's 37% "?" is
legitimately that tool's, and reading the date tool's own signal as a second
defect is the mistake entry 0 warns about in its own text. It also says nothing
about the *imperative* half of entry 1's live rescue -- "look up X" drops the
question mark **and** adds an imperative, and separating those two is entry 1's
cell in `harness/historygrid.py`, not this one.

**Carrier provenance is recorded per family, and that is ground rule 11.** Every
family below names where its carriers came from, so a payload built later can be
made disjoint from them and `scripts/check_surfacegrid.py` can assert it. A cell
whose carriers a payload trains on is inflated by exactly the amount that
matters and nothing in the scorecard would say so.

**Ground rule 13: the card records the decode settings.** Greedy calls, the
speech temperature, `--multi`, and whether a pack or a store was mounted, read
off `info` rather than asserted here -- several defects on this list are
mount-conditional and two reads taken under unstated settings cannot be
compared.

**A rate, not a gate.** `searchgrid`'s contract: this reports rates and exits
non-zero only on something structural -- no server, or a turn that raised.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_v4/ckpt.pt \
        --notes /tmp/surfacegrid.jsonl --no-log
    python -m harness.surfacegrid
    python -m harness.surfacegrid \
        --json harness/results/corn_jr_260m_v4__surfacegrid.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision
from .searchgrid import SHAPES
from .toolgrid import NOVEL_REQUESTS

# ===========================================================================
# the axis
# ===========================================================================
#
# **Case and terminal punctuation, crossed, and the cross is the point.** Entry
# 0's live evidence arrives with both moved at once -- `WHAT IS THE CAPITAL OF
# ICELAND` is upper *and* bare, `What is my name?` is title *and* punctuated --
# so a grid that varied one would attribute the whole effect to it. Eight forms
# is 8x the base denominator and about four minutes, which is the right trade
# for the only instrument that can separate them.
#
# `mixed` is entry 0's "optional and cheap" column and it is here because it is
# the one form a runtime casefold cannot rescue: the owner decision under 1b/0
# is fold-versus-transform, and a fold takes `upper` and `title` to `lower`
# while `MiXeD` and partial caps survive it. A column nobody can close in the
# runtime is the column that prices the corpus route.
#
# **`verbatim` is the control and it is first, and the first read of this grid
# is why it exists.** The obvious base column is `lower`, and for three of the
# five families it *is* the carrier as its home cell asks it. For the other two
# it is not: `searchgrid` asks "the capital of Laos" and `toolgrid` asks "call
# Grace", so lowercasing the carrier lowercases a **proper noun**, which is
# itself a surface change and one this grid is measuring. Scoring those
# families' drift against `lower` would price the transform against a cell that
# had already been transformed. `verbatim` is the carrier exactly as its home
# cell sends it, so the control reproduces a known ceiling and `lower` stays an
# honest cell of the axis rather than doubling as its own baseline.
CASES = ("verbatim", "lower", "upper", "title", "mixed")
PUNCTUATIONS = (False, True)


def recase(text: str, case: str) -> str:
    """One utterance in one case. Pure, so the guard can assert the transform.

    `title` is per-word capitalisation rather than `str.title()`, which mangles
    the apostrophe -- "What'S My Name" is not a surface form anybody produces
    and would make the column a measurement of an artefact.
    """
    if case == "verbatim":
        return text
    if case == "lower":
        return text.lower()
    if case == "upper":
        return text.upper()
    if case == "title":
        return " ".join(w[:1].upper() + w[1:] for w in text.split(" "))
    if case == "mixed":
        # Alternating over *letters*, so the shape survives punctuation and
        # spacing. Deterministic, because a random MiXeD would make two runs of
        # this grid incomparable and comparing runs is the whole use.
        out, i = [], 0
        for ch in text:
            if ch.isalpha():
                out.append(ch.upper() if i % 2 else ch.lower())
                i += 1
            else:
                out.append(ch)
        return "".join(out)
    raise ValueError(f"unknown case {case!r}")


def surface(text: str, case: str, punctuated: bool) -> str:
    """The utterance as the user would have typed it in this cell."""
    body = recase(text.rstrip("?").rstrip(), case)
    return body + ("?" if punctuated else "")


# ===========================================================================
# the families
# ===========================================================================

@dataclass(frozen=True)
class Family:
    """One carrier population, its gold, and where the carriers came from.

    `provenance` is ground rule 11's field. It names the pool a future payload
    must be built *disjoint* from, in the words a person building that payload
    would search for -- not "the search cells", which is a description of an
    intention, but the module attribute the carriers are drawn from.
    """
    label: str
    provenance: str
    carriers: tuple[tuple[str, str], ...]      # (utterance, gold tool)


# **The attribute lookups, in the bare noun-phrase form the corpus's
# `web_search` overwhelmingly carries.** Drawn from `searchgrid.SHAPES`' real
# column rather than written here, for `invented_subjects`' reason: a subject
# written into this file that later left that tuple would become a drift this
# grid could not see. These are the carriers the late drive read routing
# perfectly first-turn, and the eight shapes behind `search.route_*` 200/200.
#
# No template is wrapped around them, on purpose. A template is a *second*
# variable -- `searchgrid` reports 25 of them and the variance between them is
# larger than anything this grid is looking for -- and the bare noun phrase is
# the shape entry 0's count is about.
SEARCH_CARRIERS = tuple((real, "web_search") for _shape, real in SHAPES)

# **Grid A's decline column, two per pre-registered category.** The novel arm
# rather than the trained frames, because the trained frames' fills are the
# decline slice's own and this grid's axis has to sit on carriers whose base
# form is a routing decision rather than a possible recall. 86/100 is the
# number this column reads on the base (session 11).
DECLINE_CARRIERS = tuple(
    (req, "decline")
    for _cat, reqs in sorted(NOVEL_REQUESTS.items())
    for req in reqs[:2]
)

# **The note battery, nine phrasings, and the honest note about where they came
# from.** Session 14 ran nine note phrasings against `corn_jr_260m_v4` (six
# routed, three declined) from a scratch runner, and the nine were never
# committed -- so they are regenerated here from `corn/toolgen.py`'s
# `NOTE_TEMPLATES`, which `harness/toolgrid.py` already copies and
# `check_toolgrid.py` already holds to equality. The three entry 6 names in its
# own payload paragraph -- "note down X", "jot down X", "write down X" -- are
# pinned first, so the imperative species is in the cell by construction rather
# than by luck of which nine were taken.
#
# One body across all nine, because the axis is the surface form and a second
# content axis would put the variance somewhere this grid cannot report it.
NOTE_BODY = "buy milk"
NOTE_PHRASINGS = (
    "note down {t}", "jot down {t}", "write down {t}",
    "make a note {t}", "save a note {t}", "take a note {t}",
    "put in my notes {t}", "note that {t}", "add a note {t}",
)
NOTE_BATTERY = tuple((c.format(t=NOTE_BODY), "save_note")
                     for c in NOTE_PHRASINGS)

# **The telephony carriers, first-name, four of each tool.** The shapes are
# `corn/toolgen.py`'s `CALL_TEMPLATES`/`TEXT_TEMPLATES` entries, and the late
# drive read first-name resolution clean on both tools, so the base form is a
# ceiling here too. The names are unambiguous entries of the *training* book --
# ground rule 16: a real contact is an instance fact and never appears in a
# fixture, and an ambiguous one is a correct clarify that would land in the
# same column as a routing miss.
#
# The two golds ride one family because they are one behaviour under this
# axis -- telephony routing -- and splitting them would halve two denominators
# to report a difference this grid is not asking about.
TELEPHONY_NAMES = ("Grace", "Ivan", "Priya", "Nadia")
TELEPHONY_MESSAGE = "I'll be there in ten"
TELEPHONY_CARRIERS = (
    ("call Grace", "place_call"),
    ("ring Ivan", "place_call"),
    ("phone Priya", "place_call"),
    ("give Nadia a call", "place_call"),
    ("text Grace " + TELEPHONY_MESSAGE, "send_text"),
    ("message Ivan " + TELEPHONY_MESSAGE, "send_text"),
    ("tell Priya " + TELEPHONY_MESSAGE, "send_text"),
    ("send Nadia a text saying " + TELEPHONY_MESSAGE, "send_text"),
)

# **Entry 8's arm, and the one family here whose base form is not a ceiling.**
# Twenty-four phrasings of the owner question. Measured 2026-08-30 against
# `corn_jr_260m_v4` with `packs/about-me.md` mounted: 22 answered unpunctuated,
# and the same 24 punctuated inverted to 10 answering, 0 declining and 14
# fabricating a name. That read was driven by a scratch runner and the set was
# not committed, so it is regenerated here and pinned; the phrasings the record
# names individually (`say my name` and `what should you call me`, which
# declined; `what's my first name` and `what is my name`, which fabricated when
# punctuated) are in it by construction.
#
# **Ground rule 16, stated in the pool rather than beside it: not one of these
# contains a name.** The cell scores tool choice only and needs no store
# mounted to grade -- a miss is a miss whatever sits behind the tool -- which is
# also why it can ride this grid at all.
OWNER_QUESTIONS = (
    "what is my name",
    "what's my name",
    "whats my name",
    "say my name",
    "what should you call me",
    "what's my first name",
    "what is my first name",
    "do you know my name",
    "do you remember my name",
    "tell me my name",
    "who am i",
    "what do you call me",
    "what am i called",
    "remind me what my name is",
    "can you tell me my name",
    "you know my name right",
    "what name do you have for me",
    "what's my nickname",
    "do you know who i am",
    "tell me who i am",
    "what do people call me",
    "what is my full name",
    "have you got my name",
    "what name am i under",
)
OWNER_CARRIERS = tuple((q, "web_search") for q in OWNER_QUESTIONS)

FAMILIES = (
    Family("search_attribute",
           "harness.searchgrid.SHAPES, real column", SEARCH_CARRIERS),
    Family("decline_novel",
           "harness.toolgrid.NOVEL_REQUESTS, first two per category",
           DECLINE_CARRIERS),
    Family("note_battery",
           "corn.toolgen.NOTE_TEMPLATES via harness.toolgrid.NOTE_CARRIERS, "
           "nine phrasings pinned here", NOTE_BATTERY),
    Family("telephony",
           "corn.toolgen CALL_TEMPLATES/TEXT_TEMPLATES shapes over "
           "unambiguous training first names", TELEPHONY_CARRIERS),
    Family("owner_question",
           "regenerated for this instrument; entry 8's 24 phrasings, and no "
           "name in any of them", OWNER_CARRIERS),
)


# ===========================================================================
# the turns
# ===========================================================================

@dataclass
class Turn:
    family: str
    base: str
    gold: str
    case: str
    punctuated: bool
    ask: str
    calls: list[dict] = field(default_factory=list)
    reply: str = ""
    error: str | None = None

    @property
    def hatched(self) -> bool:
        return any(c.get("author") == "runtime" for c in self.calls)

    @property
    def model_calls(self) -> list[dict]:
        return [c for c in self.calls if c.get("author", "model") != "runtime"]

    @property
    def called(self) -> str | None:
        """The first tool the *model* reached for. `<malformed>` is not None.

        `toolgrid.Turn.called`'s rule: collapsing a malformed grab at a tool
        into "no call" would score it as restraint, and on this axis a turn
        that fell out of the vocabulary and a turn that grabbed wrongly are the
        two species entry 11 is built to keep apart.
        """
        if not self.model_calls:
            return None
        return self.model_calls[0].get("name") or "<malformed>"

    @property
    def routed(self) -> bool:
        return not self.hatched and self.called == self.gold

    @property
    def surface(self) -> str:
        return f"{self.case}{'?' if self.punctuated else ''}"


def build() -> list[Turn]:
    """Every turn this grid will run, before any of them runs.

    Pure and unseeded -- there is nothing to draw here, and
    `scripts/check_surfacegrid.py` puts each utterance through the runtime's
    hatches against this list rather than against a description of it.
    """
    turns: list[Turn] = []
    for fam in FAMILIES:
        for base, gold in fam.carriers:
            for case in CASES:
                for punctuated in PUNCTUATIONS:
                    turns.append(Turn(
                        family=fam.label, base=base, gold=gold, case=case,
                        punctuated=punctuated,
                        ask=surface(base, case, punctuated)))
    return turns


def run_turn(client: Client, turn: Turn) -> Turn:
    """One utterance from a cleared history.

    `checkup.run_case`'s reset, for its reason: history lives on the session,
    so against a `--multi` instance every cell after the first would open on
    the tail of the one before. It matters more here than anywhere -- entries 4
    and 6b say what a loaded history does to the next turn's routing, and this
    grid is not measuring that.
    """
    for _ in client.request(op="reset"):
        pass
    for ev in client.request(op="turn", user=turn.ask):
        kind = ev.get("t")
        if kind == "call":
            turn.calls.append(ev)
        elif kind == "say":
            turn.reply = ev.get("text", "")
        elif kind == "error":
            turn.error = ev.get("why", "?")
    return turn


# ===========================================================================
# the report
# ===========================================================================

SURFACES = tuple(f"{c}{'?' if p else ''}" for c in CASES for p in PUNCTUATIONS)
BASE_SURFACE = "verbatim"


@dataclass
class Cell:
    hit: int = 0
    n: int = 0
    hatched: int = 0

    def add(self, turn: Turn) -> None:
        if turn.hatched:
            self.hatched += 1
            return
        self.n += 1
        self.hit += turn.routed


def tally(turns: list[Turn]) -> dict[tuple[str, str], Cell]:
    out: dict[tuple[str, str], Cell] = {}
    for t in turns:
        out.setdefault((t.family, t.surface), Cell()).add(t)
    return out


def _fmt(c: "Cell | None") -> str:
    if c is None or not c.n:
        return "--"
    return f"{c.hit}/{c.n}"


def report(turns: list[Turn], info: dict) -> dict:
    """One table, families down and surfaces across, base column first.

    The pooled row is last and is the least of it: the reading entry 0 needs is
    which *family* survives which surface, and a mean over five golds is an
    average of five different behaviours.
    """
    cells = tally(turns)
    width = max(len(f.label) for f in FAMILIES)

    print()
    print("  routed to the carrier's own gold, by family x surface form")
    print(f"    {'':<{width}} " + " ".join(f"{s:>8}" for s in SURFACES))
    for fam in FAMILIES:
        row = " ".join(f"{_fmt(cells.get((fam.label, s))):>8}" for s in SURFACES)
        print(f"    {fam.label:<{width}} {row}")

    pooled = {s: Cell() for s in SURFACES}
    for t in turns:
        pooled[t.surface].add(t)
    print(f"    {'(pooled)':<{width}} "
          + " ".join(f"{_fmt(pooled[s]):>8}" for s in SURFACES))

    # **The two deltas, kept apart, because the corpus count predicts a
    # direction for only one of them.** Entry 0's 300:1 is about the terminal
    # character, so the punctuation delta is read *within* a case -- a bare
    # cell against the same case punctuated. The case delta is read against
    # `verbatim`, the carrier as its home cell asks it, for the reason `CASES`
    # gives: for two families `lower` has already moved a proper noun.
    print()
    print("  the punctuation delta, bare -> '?' within each case")
    print(f"    {'':<{width}} " + " ".join(f"{c:>9}" for c in CASES))
    for fam in FAMILIES:
        parts = []
        for case in CASES:
            bare = cells.get((fam.label, case))
            mark = cells.get((fam.label, f"{case}?"))
            if not (bare and mark and bare.n and mark.n):
                parts.append("       --")
            else:
                parts.append(f"{bare.hit / bare.n - mark.hit / mark.n:>+9.0%}")
        print(f"    {fam.label:<{width}} " + " ".join(parts))

    print()
    print(f"  the case delta, {BASE_SURFACE} + bare -> each case + bare")
    print(f"    {'':<{width}} " + " ".join(f"{c:>9}" for c in CASES))
    for fam in FAMILIES:
        ctrl = cells.get((fam.label, BASE_SURFACE))
        parts = []
        for case in CASES:
            cell = cells.get((fam.label, case))
            if not (ctrl and cell and ctrl.n and cell.n):
                parts.append("       --")
            else:
                parts.append(f"{cell.hit / cell.n - ctrl.hit / ctrl.n:>+9.0%}")
        print(f"    {fam.label:<{width}} " + " ".join(parts))

    # Where the misses went, per surface. `decline` and `web_search` are
    # different failures on this axis -- one is the router refusing a shape it
    # knows, the other is chat or lookup register claiming it -- and pooling
    # them would hide which one the character moved.
    print()
    print("  where the misses went, by surface")
    misses: dict[str, dict[str, int]] = {}
    for s in SURFACES:
        spread: dict[str, int] = {}
        for t in turns:
            if t.surface != s or t.hatched or t.routed:
                continue
            k = t.called or "(nothing)"
            spread[k] = spread.get(k, 0) + 1
        misses[s] = spread
        line = ", ".join(f"{k} {v}" for k, v in
                         sorted(spread.items(), key=lambda kv: -kv[1]))
        print(f"    {s:<8} {line or '(nothing missed)'}")

    hatched = [t for t in turns if t.hatched]
    print()
    if hatched:
        print(f"  !! {len(hatched)} turn(s) were answered by a runtime hatch "
              f"and are excluded from every rate above -- run "
              f"`python scripts/check_surfacegrid.py`")
        for t in hatched[:6]:
            print(f"       {t.ask[:64]}")
    else:
        print("  no turn was answered by a runtime hatch -- every rate above "
              "is the model")

    return {
        "harness": "surfacegrid/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": revision(),
        # Ground rule 13. Read off `info` rather than restated, so a card
        # cannot claim a mount the instance did not have.
        "decode": {
            "temperature": info.get("temperature"),
            "speech_temperature": info.get("speech_temperature"),
            "multi": info.get("multi"),
            "dtype": info.get("dtype"),
            "search": info.get("search"),
            "extract": info.get("extract"),
            "packs": info.get("packs"),
            "doc": info.get("doc"),
            "reach": info.get("reach"),
            "decline": info.get("decline"),
            "grammar": info.get("grammar"),
            # The fold -- owner decision 1b/0, and the setting that re-dated
            # every card on this instance the day it landed. `corn.agent.
            # fold_turn` rewrites the tokens the model is handed, so a row read
            # with it on cannot be compared with one read without it. Absent on
            # a card written before the fold existed, which is exactly what
            # "this read predates it" should look like.
            "fold": info.get("fold"),
        },
        "instance": info,
        "families": {f.label: {"provenance": f.provenance,
                               "gold": sorted({g for _c, g in f.carriers}),
                               "carriers": [c for c, _g in f.carriers]}
                     for f in FAMILIES},
        "surfaces": list(SURFACES),
        "by_family_surface": {
            f"{fam}|{s}": [c.hit, c.n, c.hatched]
            for (fam, s), c in cells.items()},
        "pooled": {s: [c.hit, c.n, c.hatched] for s, c in pooled.items()},
        "misses": misses,
        "hatched": len(hatched),
        "turns": [
            {"family": t.family, "base": t.base, "gold": t.gold,
             "case": t.case, "punctuated": t.punctuated, "ask": t.ask,
             "called": t.called, "hatched": t.hatched,
             "arguments": (t.model_calls[0].get("arguments")
                           if t.model_calls else None),
             "routed": None if t.hatched else t.routed,
             "reply": t.reply.strip(), "error": t.error}
            for t in turns
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="entry 0's surface-form axis")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--family", action="append",
                    choices=[f.label for f in FAMILIES],
                    help="run one family only; repeatable. All five by default")
    ap.add_argument("--json", help="write the scorecard here")
    args = ap.parse_args()

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- start it with "
              f"`python -m harness.server`", file=sys.stderr)
        return 2

    info = {}
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            info = {k: v for k, v in ev.items() if k not in ("t", "id")}

    print(f"surfacegrid against {info.get('ckpt')}")
    print(f"  temperature {info.get('temperature')}   speech "
          f"{info.get('speech_temperature')}   multi {info.get('multi')}   "
          f"search {info.get('search')}   packs {bool(info.get('packs'))}")
    print(f"  notes -> {info.get('notes')}   reach {info.get('reach')}")

    # The telephony family scores routing -- the first call the model writes
    # -- which happens before the runtime reads the name. Since 2026-10-13 no
    # book exists to resolve against (calls reach only the owner, PLAN-PEOPLE
    # §7), so the old training-book refusal here has nothing left to protect.
    wants = args.family or [f.label for f in FAMILIES]
    if "decline" not in (info.get("tools") or []) and "decline_novel" in wants:
        print("\nthis instance was started with --no-decline, so the decline "
              "family is measuring a tool he was not offered.", file=sys.stderr)
        client.close()
        return 2

    planned = [t for t in build() if t.family in wants]
    notes = sum(1 for t in planned if t.gold == "save_note")
    print(f"  {len(planned)} turns planned   "
          f"!! save_note may write up to {notes} notes to the path above")

    started = time.perf_counter()
    done: list[Turn] = []
    for i, turn in enumerate(planned, 1):
        run_turn(client, turn)
        if turn.error:
            print(f"turn raised: {turn.ask!r} -- {turn.error}", file=sys.stderr)
            return 2
        done.append(turn)
        if i % 100 == 0:
            print(f"    {i}/{len(planned)} ...")

    card = report(done, info)
    card["seconds"] = round(time.perf_counter() - started, 1)
    print(f"\n  {len(done)} turns in {card['seconds']}s")
    client.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
