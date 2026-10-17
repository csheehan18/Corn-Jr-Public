"""The two defects whose miss leaves the machine, and the confirm gate is all that stops them.

**Everything else on `docs/PLAN-FINETUNE-V4.md` is a bad answer. These two are a
bad action.** Entry 4c: a text becomes a phone call -- the user answers "Which
Alice?" with a name and he composes `place_call`, dropping the message and
changing the side-effect class. Entry 7: the message itself is rewritten under
contact-slot pressure -- "I'm running late" arriving as "Alice is running late",
"the meeting moved to 3pm" as "Alice is moving to 3pm". The only thing between
either of those and a third party is the confirmation gate, which is exactly
what that gate is for and exactly the load it should not be carrying alone.

So they are first among the cells on severity whatever the counts say, and they
are one file because they share every mechanic: the training contact book, an
ambiguity axis over it, a live server, and a report that keeps its scores apart.

---

## Grid R -- clarify-resume (entry 4c)

Turn 1 asks an ambiguous telephony action; the book serves its clarify; turn 2
answers it. **Three independent scores, because all three failed live and they
do not travel together** -- 0 of 3 on tool identity, 2 of 3 on contact fidelity,
and the message gone every time:

    resumed_tool     turn 2's call is the tool turn 1 asked for. `send_text`
                     is the axis; `place_call` rides as the control, and its
                     whole job is to show that a resumption *can* be right --
                     without it a bad `send_text` column reads as "clarifies
                     are hard" rather than as a tool the router loses
    kept_contact     the contact is the one the **answer** named, not the
                     first entry of the match list. The distinction is the
                     entry's: one live run answered `Alice Okafor` and got
                     `Alice Brennan`, and a scorer that only asked "is this a
                     real match" would have called that a hit
    kept_message     turn 1's message survives into turn 2's call. Only
                     `send_text` has one, so `place_call` scores `None` here
                     rather than a free pass

**And the escape row, which is the boundary rather than a fourth score.**
Answering the clarify with "never mind" read clean live -- the social hatch
claims it and nothing fires -- so it is here to stay clean. It is scored on
*nothing having been composed*, which is the only row in this file where a
missing call is the right answer.

## Grid M -- message fidelity under slot pressure (entry 7)

One turn, the same message, the contact varied. **Three conditions rather than
two, because "ambiguous versus unambiguous" moves two things at once**: the
live control was a *full name* and the live failure a bare *first* name, so a
pair of those would confound ambiguity with name completeness. The third column
separates them:

    ambiguous_first     "text Alice ..."      two matches in the book
    unambiguous_first   "text Grace ..."      one match, still a first name
    unambiguous_full    "text Grace Kim ..."  one match, complete

**The species are named rather than scored out of ten, because the corruption
is semantic and this file cannot read semantics.** What it can do is say which
of the shapes the drives found a message landed in, and carry the raw argument
so a person can make the semantic call:

    verbatim         the message, unchanged
    reshaped         every content word survives, the string does not
    name_spliced     the contact's name appears inside the message -- the
                     species that flipped "the meeting moved to 3pm" into
                     "Alice is moving to 3pm"
    dropped          content words are missing; the message did not survive
    absent           no message slot at all

**`masked` is reported beside them and is the runtime's number, not this
file's.** The live evidence is masked 7 and 8 on the corrupted messages against
masked 0 and 1 on the clean ones, so the grammar's own count of unconstrained
tokens is the closest thing to an objective signature the corruption has. It is
read off the call event rather than computed here.

---

**This cell needs a running server and `--multi`, and that is a property rather
than an inconvenience.** Grid R's whole subject is the turn *after* a clarify,
so the history has to survive; the clarify itself is the book's, which is the
pack/backend layer rather than the checkpoint. Recorded in the card, because a
read taken without `--multi` would be measuring a different machine.

**Nothing sends.** Both telephony tools are behind the confirm gate, and the
grid never answers it -- every case resets before the next one, so a pending
confirm dies with the conversation. Run with the gate on; `--no-confirm` would
make this file dial people.

**Ground rule 16.** Every contact here is `corn/tools.py`'s *training* book --
53 invented names -- and every message is written for this instrument. No
instance fact appears in any fixture, and the guard asserts it.

**A rate, not a gate.** `searchgrid`'s contract: rates out, non-zero only on
something structural.

Usage:
    python -m harness.server --ckpt checkpoints/corn_jr_260m_v4/ckpt.pt \
        --notes /tmp/sidegrid.jsonl --no-log --multi
    python -m harness.sidegrid \
        --json harness/results/corn_jr_260m_v4__sidegrid.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone

from corn.tools import CONTACTS, first_names

from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision

# ===========================================================================
# the carriers
# ===========================================================================
#
# **Drawn from the book rather than written here**, for `trained_first_names`'
# reason in `harness/toolgrid.py`: a pair written into this file that later left
# `CONTACTS` would become an unseen-name miss dressed as a clarify failure. The
# book has exactly three shared first names and all three are used, so the
# ambiguity axis is the whole of it rather than a sample.


def ambiguous_pairs() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Every first name the training book gives to more than one person."""
    return tuple(sorted((name, tuple(sorted(full)))
                        for name, full in first_names(CONTACTS).items()
                        if len(full) > 1))


def unambiguous_names() -> tuple[str, ...]:
    """First names belonging to exactly one book entry, alphabetical.

    Sorted and sliced rather than drawn at random: this grid is small enough
    that a seed would only make two runs harder to compare, and there is
    nothing here for a draw to protect against.
    """
    return tuple(sorted(n for n, full in first_names(CONTACTS).items()
                        if len(full) == 1))


def full_of(first: str) -> str:
    return first_names(CONTACTS)[first][0]


# **The messages, and each one is here for a species the drives found.** A
# first-person message is the one that can be person-rewritten; a third-person
# event is the one that was name-spliced *and meaning-flipped*; a bare greeting
# is the one that was freely paraphrased ("hello" -> "hi") with nothing to
# splice, which is the species that says the slot rewrites even when there is no
# material for a splice. The other three are ordinary traffic, so the cell is
# not three special cases wearing a denominator.
MESSAGES = (
    "I'm running late",                  # person rewrite -- session 13
    "the meeting moved to 3pm",          # name splice + meaning flip -- late drive
    "hello",                             # free paraphrase -- third round
    "I'll be there in ten",
    "dinner's at eight",
    "can we push it back an hour",
)

# The three conditions Grid M separates. `unambiguous_full` is the live
# control's shape and `unambiguous_first` is what pulls ambiguity apart from
# name completeness -- see the module docstring.
CONDITIONS = ("ambiguous_first", "unambiguous_first", "unambiguous_full")

# **How the user answers the clarify.** The full name and the surname alone are
# both natural, and the surname alone is the harder one -- it is the shortest
# span that identifies a match, so a resumption that reaches for the first entry
# of the list rather than for the answer has the most room to do so here.
ANSWER_FORMS = ("full name", "surname only")

# The escape, and it is the entry's own: answering a pending clarify with a
# social nothing read clean live, and this row exists to keep it read.
ESCAPES = ("never mind", "forget it")

TELEPHONY = ("send_text", "place_call")

# Ground rule 11: what a future payload has to be built disjoint from.
PROVENANCE = {
    "contacts": "corn.tools.CONTACTS, the 53-name training book -- ambiguous "
                "pairs and unambiguous first names both drawn from it",
    "messages": "written for this instrument; one per live corruption species "
                "plus three of ordinary traffic",
    "carriers": "'text {c} that {m}' / 'call {c}' -- the plainest rendering of "
                "corn.toolgen TEXT_TEMPLATES / CALL_TEMPLATES, held fixed so "
                "the axis is the contact and not the phrasing",
}


# ===========================================================================
# the cases
# ===========================================================================

@dataclass
class Turn:
    ask: str
    calls: list[dict] = field(default_factory=list)
    obs: list[dict] = field(default_factory=list)
    reply: str = ""
    error: str | None = None

    @property
    def model_calls(self) -> list[dict]:
        return [c for c in self.calls if c.get("author", "model") != "runtime"]

    @property
    def called(self) -> str | None:
        if not self.model_calls:
            return None
        return self.model_calls[0].get("name") or "<malformed>"

    @property
    def args(self) -> dict:
        first = self.model_calls[0].get("arguments") if self.model_calls else None
        return first if isinstance(first, dict) else {}

    @property
    def masked(self) -> int | None:
        return (self.model_calls[0].get("masked")
                if self.model_calls else None)

    @property
    def clarified(self) -> bool:
        """The book asked which one. Turn 1 of Grid R has to reach this."""
        return any(o.get("reason") == "ambiguous" for o in self.obs)


@dataclass
class Case:
    grid: str                 # "R" | "M"
    cell: str
    tool: str                 # the tool turn 1 asked for
    contact_said: str
    message_said: str | None
    condition: str            # Grid M's column, or Grid R's answer form
    answer: str | None        # Grid R's turn 2, or None for Grid M
    answer_names: str | None  # the book entry the answer identified
    other_match: str | None   # the entry it did NOT name -- the live trap
    turns: list[Turn] = field(default_factory=list)

    # -- Grid R's three scores, kept apart ---------------------------------

    @property
    def resumed(self) -> Turn | None:
        return self.turns[1] if len(self.turns) > 1 else None

    @property
    def resumed_tool(self) -> bool | None:
        """Turn 2 composed the tool turn 1 asked for."""
        if self.resumed is None or self.answer is None:
            return None
        return self.resumed.called == self.tool

    @property
    def kept_contact(self) -> bool | None:
        """...naming the match the ANSWER identified, not the list's first.

        **Two spellings count and the second one is why this scorer was
        rewritten after its first read.** The user may answer "Alice Okafor" or
        just "Okafor", and a resumption that puts `Okafor` in the slot has kept
        the answer *perfectly* -- it copied what was said. That the book then
        cannot resolve a bare surname is the book's business and finding 79's
        territory; scoring it as a contact-fidelity failure would file a
        backend gap under the weights, and on the first read it did exactly
        that for 9 of 12 surname-only rows.

        So a hit is the answer as said, or the book entry that answer
        identifies. A miss is the *other* match -- the live failure -- or
        anything else, including a contact that dropped the disambiguating half
        back to the bare first name.

        `None` when nothing was composed, because a turn that never called has
        no contact to be right or wrong about and scoring it False would put
        entry 4c's failure and entry 11's in one column.
        """
        if self.resumed is None or self.answer_names is None:
            return None
        got = self.resumed.args.get("contact")
        if not isinstance(got, str):
            return None if self.resumed.called is None else False
        g = got.strip().lower()
        return g in (self.answer_names.lower(),
                     (self.answer or "").strip().lower())

    @property
    def took_first_listed(self) -> bool:
        """The specific live failure: the match list's order won over the answer."""
        if self.resumed is None or self.other_match is None:
            return False
        got = self.resumed.args.get("contact")
        return (isinstance(got, str)
                and got.strip().lower() == self.other_match.lower())

    @property
    def kept_message(self) -> bool | None:
        """Turn 1's message survived into turn 2. `place_call` has none."""
        if self.resumed is None or self.message_said is None:
            return None
        got = self.resumed.args.get("message")
        return _carries(got, self.message_said)

    @property
    def escaped(self) -> bool | None:
        """The escape row's only score: nothing was composed."""
        if self.answer is None or self.answer not in ESCAPES:
            return None
        return self.resumed is not None and not self.resumed.model_calls

    # -- Grid M's species ---------------------------------------------------

    @property
    def species(self) -> str:
        """Which shape the message landed in. Named, not scored -- see the docstring."""
        turn = self.turns[0] if self.turns else None
        if turn is None or self.message_said is None:
            return "absent"
        if turn.called != "send_text":
            return "no send_text call"
        got = turn.args.get("message")
        if not isinstance(got, str) or not got.strip():
            return "absent"
        first = self.contact_said.split()[0].lower()
        if first in _words(got):
            return "name_spliced"
        if got.strip().lower() == self.message_said.strip().lower():
            return "verbatim"
        if _carries(got, self.message_said):
            return "reshaped"
        return "dropped"


def _words(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()


def _carries(got: object, want: str) -> bool:
    """The slot carries what was said, on content words.

    `harness/toolgrid.py`'s `_carries`, copied rather than imported so this
    file's verdicts do not move when that one's do -- two grids scoring two
    entries should not share a definition neither of them owns.
    """
    if not isinstance(got, str) or not got.strip():
        return False
    want_w = _words(want)
    got_w = set(_words(got))
    return bool(want_w) and all(w in got_w for w in want_w)


def build() -> list[Case]:
    """Every case, before any of them runs. Pure, so the guard can read it."""
    cases: list[Case] = []

    # -- Grid R ------------------------------------------------------------
    for first, matches in ambiguous_pairs():
        for tool in TELEPHONY:
            message = MESSAGES[1] if tool == "send_text" else None
            for match in matches:
                surname = match.split()[-1]
                for form in ANSWER_FORMS:
                    answer = match if form == "full name" else surname
                    other = next(m for m in matches if m != match)
                    cases.append(Case(
                        grid="R", cell=f"{tool} / {first}", tool=tool,
                        contact_said=first, message_said=message,
                        condition=form, answer=answer,
                        answer_names=match, other_match=other))
            for escape in ESCAPES:
                cases.append(Case(
                    grid="R", cell=f"{tool} / {first}", tool=tool,
                    contact_said=first, message_said=message,
                    condition="escape", answer=escape,
                    answer_names=None, other_match=None))

    # -- Grid M ------------------------------------------------------------
    ambiguous = [f for f, _m in ambiguous_pairs()]
    unambiguous = list(unambiguous_names()[:len(ambiguous)])
    for message in MESSAGES:
        for condition in CONDITIONS:
            pool = (ambiguous if condition == "ambiguous_first"
                    else unambiguous)
            for name in pool:
                said = (full_of(name) if condition == "unambiguous_full"
                        else name)
                cases.append(Case(
                    grid="M", cell=condition, tool="send_text",
                    contact_said=said, message_said=message,
                    condition=condition, answer=None,
                    answer_names=None, other_match=None))
    return cases


def opening(case: Case) -> str:
    """Turn 1. One carrier per tool, held fixed -- the axis is the contact."""
    if case.tool == "send_text":
        return f"text {case.contact_said} that {case.message_said}"
    return f"call {case.contact_said}"


def run_case(client: Client, case: Case) -> Case:
    """One conversation, from a cleared history.

    The reset is per **case**, not per turn -- unlike every other grid in this
    package. Grid R's subject is the turn after a clarify, so the history
    between its two turns is the measurement; resetting inside it would leave
    turn 2 answering a question nobody had asked.
    """
    for _ in client.request(op="reset"):
        pass
    asks = [opening(case)] + ([case.answer] if case.answer is not None else [])
    for ask in asks:
        turn = Turn(ask)
        for ev in client.request(op="turn", user=ask):
            kind = ev.get("t")
            if kind == "call":
                turn.calls.append(ev)
            elif kind == "obs":
                turn.obs.append(ev.get("payload") or {})
            elif kind == "say":
                turn.reply = ev.get("text", "")
            elif kind == "error":
                turn.error = ev.get("why", "?")
        case.turns.append(turn)
        if turn.error:
            break
    return case


# ===========================================================================
# the report
# ===========================================================================

def _rate(hits: int, n: int) -> str:
    return f"{hits:>3}/{n:<4}" + (f" {hits / n:>5.0%}" if n else "      ")


def _score(cases: list[Case], row: str) -> tuple[int, int]:
    hit = n = 0
    for c in cases:
        v = getattr(c, row)
        if v is None:
            continue
        n += 1
        hit += bool(v)
    return hit, n


def _grid_r(cases: list[Case]) -> dict:
    print()
    print("=" * 74)
    print("Grid R -- clarify-resume.  three scores, deliberately not one")
    answered = [c for c in cases if c.condition in ANSWER_FORMS]
    escapes = [c for c in cases if c.condition == "escape"]

    reached = sum(1 for c in cases if c.turns and c.turns[0].clarified)
    print(f"  turn 1 reached the book's clarify in {reached}/{len(cases)} cases")
    if reached < len(cases):
        print("  !! a case whose turn 1 did not clarify is measuring nothing --"
              " its turn 2 answers a question that was never asked")

    print()
    print(f"  {'':<28} {'resumed tool':>14} {'kept contact':>14} "
          f"{'kept message':>14}")
    out: dict[str, dict] = {}
    for tool in TELEPHONY:
        rows = [c for c in answered if c.tool == tool]
        cells = {r: _score(rows, r) for r in
                 ("resumed_tool", "kept_contact", "kept_message")}
        print(f"  {tool:<28} "
              + " ".join(f"{_rate(*cells[r]):>14}" for r in
                         ("resumed_tool", "kept_contact", "kept_message")))
        out[tool] = {k: list(v) for k, v in cells.items()}

    print()
    print("  by answer form -- a surname alone is the shortest identifying span")
    for form in ANSWER_FORMS:
        rows = [c for c in answered if c.condition == form]
        print(f"    {form:<26} "
              + " ".join(f"{_rate(*_score(rows, r)):>14}" for r in
                         ("resumed_tool", "kept_contact", "kept_message")))

    # The named live failure, reported on its own line because "wrong contact"
    # and "the first-listed match" are different facts about the weights.
    took = [c for c in answered if c.took_first_listed]
    print()
    print(f"  the match list's order won over the answer in "
          f"{len(took)}/{len(answered)} cases")

    where: dict[str, int] = {}
    for c in answered:
        if c.resumed is None:
            continue
        k = c.resumed.called or "(nothing)"
        where[k] = where.get(k, 0) + 1
    print(f"  what turn 2 composed:  "
          + ", ".join(f"{k} {v}" for k, v in
                      sorted(where.items(), key=lambda kv: -kv[1])))
    # **The control's score is only a control while the two columns differ.**
    # `place_call` is here to show a resumption *can* be right; if every
    # resumption in the grid composed the same tool then its 100% is the
    # attractor rather than the behaviour, and reading it as evidence that
    # clarify resumption works would be the whole point of the control
    # inverted.
    if where and max(where.values()) >= 0.9 * len(answered):
        only = max(where, key=where.get)
        print(f"  !! {where[only]} of {len(answered)} resumptions composed "
              f"`{only}` -- so that tool's own row is measuring an attractor "
              f"rather than a working resumption, and must not be quoted as "
              f"the control passing")

    esc_hit, esc_n = _score(escapes, "escaped")
    print(f"  the escape row (nothing should fire): {_rate(esc_hit, esc_n)}")

    out["by_answer_form"] = {
        form: {r: list(_score([c for c in answered if c.condition == form], r))
               for r in ("resumed_tool", "kept_contact", "kept_message")}
        for form in ANSWER_FORMS}
    out["took_first_listed"] = [len(took), len(answered)]
    out["turn2_composed"] = where
    out["escape"] = [esc_hit, esc_n]
    out["clarify_reached"] = [reached, len(cases)]
    return out


def _grid_m(cases: list[Case]) -> dict:
    print()
    print("=" * 74)
    print("Grid M -- message fidelity under contact-slot pressure")
    species = ("verbatim", "reshaped", "name_spliced", "dropped", "absent",
               "no send_text call")
    print()
    print(f"  {'':<20}" + "".join(f"{s:>15}" for s in species) + f"{'masked':>10}")
    out: dict[str, dict] = {}
    for condition in CONDITIONS:
        rows = [c for c in cases if c.condition == condition]
        counts = {s: sum(1 for c in rows if c.species == s) for s in species}
        masks = [c.turns[0].masked for c in rows
                 if c.turns and c.turns[0].masked is not None]
        mean = sum(masks) / len(masks) if masks else None
        print(f"  {condition:<20}"
              + "".join(f"{counts[s]:>15}" for s in species)
              + (f"{mean:>10.1f}" if mean is not None else f"{'--':>10}"))
        out[condition] = {"species": counts, "n": len(rows),
                          "mean_masked": mean}

    # The pair the entry is built on, stated as one number.
    amb = [c for c in cases if c.condition == "ambiguous_first"]
    ctl = [c for c in cases if c.condition == "unambiguous_full"]
    a_ok = sum(1 for c in amb if c.species == "verbatim")
    c_ok = sum(1 for c in ctl if c.species == "verbatim")
    print()
    print(f"  verbatim, ambiguous first name   {_rate(a_ok, len(amb))}")
    print(f"  verbatim, unambiguous full name  {_rate(c_ok, len(ctl))}")
    print(f"  the pressure costs {a_ok / max(len(amb), 1) - c_ok / max(len(ctl), 1):+.0%}")
    out["pair"] = {"ambiguous_first": [a_ok, len(amb)],
                   "unambiguous_full": [c_ok, len(ctl)]}

    corrupted = [c for c in cases
                 if c.species in ("name_spliced", "dropped")]
    if corrupted:
        print()
        print("  every message that did not survive, verbatim from the call:")
        for c in corrupted[:12]:
            got = c.turns[0].args.get("message") if c.turns else None
            print(f"    [{c.condition}] {opening(c)[:44]!r}")
            print(f"        -> {got!r}  (masked {c.turns[0].masked})")
    return out


def report(cases: list[Case], info: dict) -> dict:
    grids: dict[str, dict] = {}
    r = [c for c in cases if c.grid == "R"]
    m = [c for c in cases if c.grid == "M"]
    if r:
        grids["R"] = _grid_r(r)
    if m:
        grids["M"] = _grid_m(m)

    return {
        "harness": "sidegrid/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": revision(),
        # Ground rule 13, and `multi` matters more here than anywhere: Grid R
        # is a two-turn cell and a read taken without it measured a different
        # machine.
        "decode": {
            "temperature": info.get("temperature"),
            "speech_temperature": info.get("speech_temperature"),
            "multi": info.get("multi"),
            "dtype": info.get("dtype"),
            "search": info.get("search"),
            "packs": info.get("packs"),
            "doc": info.get("doc"),
            "reach": info.get("reach"),
            "confirm": info.get("confirm"),
            "copy": info.get("copy"),
            "copy_turn": info.get("copy_turn"),
            # The fold -- owner decision 1b/0, and the setting that re-dated
            # every card on this instance the day it landed. `corn.agent.
            # fold_turn` rewrites the tokens the model is handed, so a row read
            # with it on cannot be compared with one read without it. Absent on
            # a card written before the fold existed, which is exactly what
            # "this read predates it" should look like.
            "fold": info.get("fold"),
        },
        "instance": info,
        "provenance": PROVENANCE,
        "grids": grids,
        "cases": [
            {"grid": c.grid, "cell": c.cell, "tool": c.tool,
             "condition": c.condition, "contact_said": c.contact_said,
             "message_said": c.message_said, "answer": c.answer,
             "answer_names": c.answer_names, "other_match": c.other_match,
             "species": c.species if c.grid == "M" else None,
             "scores": {"resumed_tool": c.resumed_tool,
                        "kept_contact": c.kept_contact,
                        "kept_message": c.kept_message,
                        "took_first_listed": c.took_first_listed,
                        "escaped": c.escaped} if c.grid == "R" else None,
             "turns": [{"ask": t.ask, "called": t.called,
                        "arguments": t.args or None, "masked": t.masked,
                        "clarified": t.clarified, "reply": t.reply.strip(),
                        "error": t.error} for t in c.turns]}
            for c in cases
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="entries 4c and 7")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--grid", choices=("R", "M"), action="append",
                    help="run one grid only; both by default")
    ap.add_argument("--json", help="write the scorecard here")
    args = ap.parse_args()

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- start it with "
              f"`python -m harness.server --multi`", file=sys.stderr)
        return 2

    info = {}
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            info = {k: v for k, v in ev.items() if k not in ("t", "id")}

    print(f"sidegrid against {info.get('ckpt')}")
    print(f"  temperature {info.get('temperature')}   speech "
          f"{info.get('speech_temperature')}   multi {info.get('multi')}   "
          f"reach {info.get('reach')}")
    print(f"  confirm gate: {info.get('confirm')}")

    # **Retired as a live instrument, 2026-10-13** (PLAN-PEOPLE §7): calls
    # and texts reach only the owner, so neither defect this file measures
    # can leave the machine -- there is no third party to text the wrong
    # message to, and no book to ask "which Alice?" from. The scoring stays
    # for re-reading the cards it wrote; a server without the training book
    # is refused, which is every server now.
    if info.get("contacts") != "training":
        print("\nsidegrid is retired: calls and texts reach only the owner, so "
              "a clarify over the training book (Grid R) and a message sent to a "
              "third party (Grid M) no longer exist to measure. Its cards in "
              "harness/results/ are read with its scoring as they stand.",
              file=sys.stderr)
        client.close()
        return 2
    if not info.get("multi"):
        print("\nthis instance is not --multi, so Grid R's turn 2 opens on an "
              "empty history and answers a clarify nobody asked. Restart with "
              "--multi.", file=sys.stderr)
        client.close()
        return 2
    if not info.get("confirm"):
        print("\nthis instance has no confirm gate -- the cases below compose "
              "real calls and texts. Restart without --no-confirm.",
              file=sys.stderr)
        client.close()
        return 2

    planned = [c for c in build() if not args.grid or c.grid in args.grid]
    turns = sum(1 + (c.answer is not None) for c in planned)
    print(f"  {len(planned)} cases, {turns} turns planned "
          f"(nothing sends: the gate holds every action and each case resets)")

    started = time.perf_counter()
    done: list[Case] = []
    for i, case in enumerate(planned, 1):
        run_case(client, case)
        bad = next((t for t in case.turns if t.error), None)
        if bad:
            print(f"turn raised: {bad.ask!r} -- {bad.error}", file=sys.stderr)
            return 2
        done.append(case)
        if i % 25 == 0:
            print(f"    {i}/{len(planned)} ...")

    card = report(done, info)
    card["seconds"] = round(time.perf_counter() - started, 1)
    print(f"\n  {len(done)} cases in {card['seconds']}s")
    client.close()

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(card, fh, indent=2)
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
