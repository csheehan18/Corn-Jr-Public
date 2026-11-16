"""The door on the real tools -- what a call under a part may name and copy (SPEC-LANGUAGE §3, ROADMAP A2).

PLAN-TAG-SPINE §2's thesis is three bindings: the request is cut into parts,
a part's label is a role, a role is bound to a declared tool at runtime. On
the generated worlds the role came from the tool's description
(`corn/decompgen.py`'s `ROLES`); the real tools carry none, so this file is
the table, held **in the runtime and not on the `tools:` line** (D-A2.3,
owner 2026-10-03: declaring it in the text would be a second variable in
the arm that first reads the parse on real carriers).

    role     the tools that play it
    find     web_search, recall_day; a coined tool whose verb fetches or reports
    send     send_text, ask_agent
    note     save_note
    act      place_call; a coined tool whose verb starts or stops something (D-A2.1)
    helper   resolve_date, decline -- legal under any part, and never a part's own call

`ask` binds as `find` -- a question answered by a lookup; `do`, `chat` and
`social` admit no call of their own. **A `follow` is held to the declared set
and nothing narrower**: its label says the turn refers back, not which role
it needs -- "and what about the Bryunlvnia?" repeats the search, "text them
I'm on my way" after a call sends a text, "note that down" after a search
saves a note (`corn/turn2gen.py`'s chain classes). A first draft bound it to
the role of the turn before's call; the smoke read of `probe_a2.py`
(2026-10-03) showed that door refusing the gold call on every pronoun and
result row. **A helper does not use up
its part**: "what did I do last Tuesday" is one `ask` that resolves a date and
then recalls the day, and "note that the lessons started a couple of days
ago" is one `note` that resolves a date and then saves.

**The copy half.** A call's string arguments are spans of its own part's
words, or of the last observation's values (a pipe's note writes down what
the search found; a recall copies the resolved date). Three exemptions, each
where the gold is not a span of either source: a `follow` composes its
argument from the turn before (the rule `corn.evals.role_filter` already
makes, finding 131: under the copy slot `e2e.rebind` read 5 of 50 where it
reads 48); a note after a resolved date writes its stem and the spoken date
together, which is no one span; and **a helper's arguments are not copy
slots** -- the temporal slice answers "what day is it today?" with
`resolve_date{"expression": "this morning"}` or `"tonight"`, the generator's
canonical form and no span of the request (19 of the first 4,812 temporal
calls; `check_parseline.py`, 2026-10-03). `scripts/check_parseline.py`
proves the table and both halves refuse no call the tagged corpus contains.

Not imported by `corn/agent.py`: arming it at serving is H3's.
"""

from __future__ import annotations

import json

from .grammar import PARSE_LABELS_1_0, PARTS_PREFIX, _nested_nodes
from .markers import D_CALL, D_OBS, D_USER
from .toolspace import DECL_PREFIX, DECL_SEP, DOMAINS, HELD_OUT_DOMAINS
from .toolspace import VERBS as _TS_VERBS

TOOL_ROLE: dict[str, str] = {
    "web_search": "find", "recall_day": "find",
    "send_text": "send", "ask_agent": "send",
    "save_note": "note",
    "place_call": "act",
}
HELPERS: frozenset[str] = frozenset({"resolve_date", "decline"})
LABEL_ROLE: dict[str, str] = {"ask": "find", "find": "find", "send": "send",
                              "note": "note", "act": "act"}
ACTIONABLE: frozenset[str] = frozenset(LABEL_ROLE) | {"follow"}

# `corn/toolspace.py`'s verb senses, by the word a coined name opens with --
# imported from the generator that coins them, which is legal here because
# this file is outside the runtime closure (HACKING §2; not imported by
# `corn/agent.py`). Arming the door at serving (H3) moves the table across.
SENSE_VERBS: dict[str, tuple[str, ...]] = dict(_TS_VERBS)
SENSE_ROLE: dict[str, str] = {"fetch": "find", "report": "find", "start": "act", "stop": "act"}


def sense_of_name(name: str) -> str | None:
    """A coined tool's sense from the verb its name opens with, or None."""
    best = None
    for sense, verbs in SENSE_VERBS.items():
        for v in verbs:
            if name.startswith(v + "_") and (best is None or len(v) > len(best[1])):
                best = (sense, v)
    return best[0] if best else None


def role_of(name: str) -> str | None:
    """`find` / `send` / `note` / `act` / `helper`, or None for a name nobody plays."""
    if name in HELPERS:
        return "helper"
    if name in TOOL_ROLE:
        return TOOL_ROLE[name]
    sense = sense_of_name(name)
    return SENSE_ROLE[sense] if sense else None


def leaves(line: str, utterance: str) -> list[tuple[str, str]] | None:
    """(label, span) of a `parts:` line's leaves in surface order, or None if
    the line does not parse. A bare label is one leaf spanning the utterance
    (D-A1.4); a part with children is replaced by them."""
    if not line.startswith(PARTS_PREFIX):
        return None
    body = line[len(PARTS_PREFIX):].strip()
    if body in PARSE_LABELS_1_0:
        return [(body, utterance)]
    got = _nested_nodes(body, PARSE_LABELS_1_0)
    if got is None:
        return None
    out: list[tuple[str, str]] = []

    def walk(nodes) -> None:
        for label, span, kids in nodes:
            if kids:
                walk(kids)
            else:
                out.append((label, span))
    walk(got[0])
    return out


def _calls(lines: list[str]) -> list[str]:
    """The names of the turn's complete calls. A call line that does not parse
    -- the open `<|call|>` a prompt ends on, or one being written -- is not a
    call made, so it does not use up a part."""
    out = []
    for ln in lines:
        if ln.startswith(D_CALL):
            try:
                out.append(json.loads(ln[len(D_CALL):])["name"])
            except (ValueError, KeyError, TypeError):
                continue
    return out


def _turns(prompt: str) -> list[list[str]]:
    """The prompt's lines grouped by user turn, each group opening on its `<|user|>` line."""
    turns: list[list[str]] = []
    for ln in prompt.split("\n"):
        if ln.startswith(D_USER):
            turns.append([ln])
        elif turns:
            turns[-1].append(ln)
    return turns


def declared_names(prompt: str) -> tuple[str, ...] | None:
    """The `tools:` line's names, or None when the prompt declares none (the
    registry is then the whole set, as `corn/agent.py` serves it)."""
    for ln in prompt.split("\n"):
        if ln.startswith(DECL_PREFIX):
            return tuple(e.split("(", 1)[0].strip() for e in ln[len(DECL_PREFIX):].split(DECL_SEP))
    return None


def next_leaf(prompt: str) -> tuple[str, str, str | None, bool] | None:
    """(label, span, antecedent role, a date was resolved) of the leaf the next
    call executes in the prompt's last turn, or None when the turn has no
    parse line or every actionable leaf has had its call. The antecedent role
    is recorded for the item files; the door does not narrow on it."""
    turns = _turns(prompt)
    if not turns:
        return None
    turn = turns[-1]
    utt = turn[0][len(D_USER):]
    parse = next((ln for ln in turn[1:] if ln.startswith(PARTS_PREFIX)), None)
    lv = leaves(parse, utt) if parse is not None else None
    if not lv:
        return None
    acts = [(lab, span) for lab, span in lv if lab in ACTIONABLE]
    made = _calls(turn)
    own = [n for n in made if n not in HELPERS]
    if len(own) >= len(acts):
        return None
    label, span = acts[len(own)]
    ante = None
    if label == "follow" and len(turns) > 1:
        prev = [n for n in _calls(turns[-2]) if n not in HELPERS]
        ante = role_of(prev[-1]) if prev else None
    return label, span, ante, "resolve_date" in made


def allowed_names(prompt: str, registry: tuple[str, ...]) -> tuple[str, ...]:
    """The names the next call may use: its part's role's tools among those
    declared, and the helpers -- every declared tool for a `follow`. Empty
    when there is no leaf to bind."""
    got = next_leaf(prompt)
    if got is None:
        return ()
    label, _span, _ante, _dated = got
    pool = declared_names(prompt) or registry
    if label == "follow":
        return tuple(pool)
    want = LABEL_ROLE.get(label)
    return tuple(n for n in pool if role_of(n) == "helper" or (want and role_of(n) == want))


def last_values(prompt: str) -> str:
    """Every string value of the last observation, one a line -- a pipe's note
    copies the search's `answer`, a recall copies the resolved `date`."""
    at = prompt.rfind(D_OBS)
    if at < 0:
        return ""
    try:
        obs = json.loads(prompt[at + len(D_OBS):].split("\n", 1)[0])
    except ValueError:
        return ""
    if not isinstance(obs, dict):
        return ""
    return "\n".join(str(v) for v in obs.values() if isinstance(v, (str, int, float)))


def copy_source(prompt: str) -> str | None:
    """The bytes the next call's string arguments are spans of, or None when
    the call is exempt from the copy half (a `follow`; a note after a
    resolved date)."""
    got = next_leaf(prompt)
    if got is None:
        return None
    label, span, _ante, dated = got
    if label == "follow" or (label == "note" and dated):
        return None
    vals = last_values(prompt)
    return span + ("\n" + vals if vals else "")


def copy_spec(prompt: str, registry: tuple[str, ...]):
    """`(names, CopySpec or None)` -- the door for the next call, as data: the
    names it may use, and the copy constraint on their string arguments. The
    scorer arms `CallConstraint` from it; `check_parseline.py` runs every gold
    call of the tagged corpus through `grammar.accepts` with it."""
    from .grammar import CopySpec
    names = allowed_names(prompt, registry)
    if not names:
        return names, None
    src = copy_source(prompt)
    if src is None:
        return names, None
    slots = string_slots(names)
    raw = src.encode("utf-8")
    return names, CopySpec(slots=slots, source=raw, narrow=slots, narrow_source=raw)


def string_slots(names: tuple[str, ...]) -> frozenset[tuple[str, str]]:
    """Every (tool, string parameter) the copy half holds. Registry tools by
    their schema; a coined tool's one parameter is unknown here, so the
    constraint is given the toolspace parameter names it can carry."""
    from .tools import REGISTRY
    out = set()
    for n in names:
        if n in HELPERS:
            continue
        t = REGISTRY.get(n)
        if t is not None:
            out |= {(n, p.name) for p in t.params if p.kind == "string"}
        else:
            out |= {(n, p) for p in COINED_PARAMS}
    return frozenset(out)


# The parameter names `corn/toolspace.py`'s domains declare.
COINED_PARAMS: tuple[str, ...] = tuple(sorted({d[2] for d in DOMAINS + HELD_OUT_DOMAINS}))
