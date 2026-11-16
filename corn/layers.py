"""The 1.0 turn's layers at serving -- ROADMAP H3, first part: what every turn carries.

D7 (owner, 2026-11-12) took which layers ride; ROADMAP C6 wrote them onto
every 1.0 turn-shaped slice (`corn/rendergen.py`). A checkpoint trained on
those slices expects the same lines at serving, in the same places, and this
module is the runtime's half: it writes the lines the runtime owns, binds the
lines he writes, and says what each one was so the turn can be logged.

    the corpus (C6)                          at serving
    name: Vintiel                            `head`: the persona's name, always
    <|day|>2025-07-18 Friday                 `head`: the anchor, always
                                             no `tools:` line (below)
    <|user|>find out the discoverer of ...   the person's line
    parts: ask                               his, under the nested bind over the
                                             1.0 labels (`bound_line`)
    move: farewell                           his, after `parts: chat` only, bound
                                             to `MOVES_1_0`, or absent
    <|call|>... / <|say|>...                 the loop as it was, the call held
                                             to its part (`door_names`)

**The day is always written under v5, and that reverses a v4 rule.**
`corn/agent.py`'s `--day` is off by default because in v4 the header occurred
only in the temporal slice, where every transcript calls, so it voted for
`resolve_date`. C6 put a day on every turn-shaped 1.0 document (SPEC §0's
coverage rule), so on a v5 checkpoint the header carries no routing
information -- and its *absence* would be the cue no document trained.

**No `tools:` line under v5** (owner, 2026-11-12). The 1.0 slices that use
the real tools -- C1, C3, C7's owner slices, turn-2 and compound -- carry
none: only the coined-tool slices (`toolspace`, `social_v5`, `self_v5`)
declare, and there the tools are invented per document. A v5 head that
declared the real tools would show him a line no real-tool document has.
The narrowing is unchanged: the agent still holds the call grammar to its
declared set, so what he may call is the same, only no longer shown.

**`parts:` is decoded under the bind, never free.** The nested bind
(`grammar.ParseConstraint(line="nested")`, SPEC-LANGUAGE §9) is what
`parseline.line_ok` accepts, and the C6 slices pass it on every line (160,008
read, 2026-11-12). The bind can strand him -- a legal prefix with no legal
next byte -- so `bound_line` takes the last token back, bans it there and
picks again: `scripts/probe_nestgen.py`'s decoder, moved here so the runtime
and the probes stop being two implementations. Greedy over the allowed set,
whatever the turn's temperature: the parse is a decision about structure,
and sampling it would sample which tool the turn may call.

**`move:` only under `parts: chat`.** SPEC §4: a tool turn has no move part,
and in the corpus a move line sits only under a chat parse (`social_v5`,
`self_v5`); SODA's chat turns carry none (D-A1.11). So after `parts: chat`
the runtime reads which of three he prefers -- a move line, `<|say|>`, or
`<|call|>` -- and decodes a move line under its bind only if he chose one.
The move is read in place of the runtime's own detector where it names a
social family (`move_family`); `self`, `share` and `open` have no family and
leave the detector's reading in place.

**The door** (`corn/door.py`): a call under a part may name only its part's
role's tools and the helpers -- every declared tool for a `follow`
(`door.allowed_names`). `door_names` is what the agent hands
`CallConstraint.set_declared` each round; an empty answer (no actionable
part left) leaves the declaration as it was, because the door narrows and
never widens.

**What this part does not do** -- the rest of H3, named in PLAN-TAG-LANGUAGE's
H3 section: the windowed interpreter (`corn/window.py`) for a request deeper
than one flat line, traces and templates (`corn/worker.py`), and the door's
copy half. Each needs a v5 checkpoint to be read against, and none is on disk
until P1.
"""

from __future__ import annotations

from datetime import date

from . import door
from .grammar import MOVE_PREFIX, MOVES_1_0, PARSE_LABELS_1_0, PARTS_PREFIX, ParseConstraint
from .markers import D_CALL, D_SAY
from .persona import name_header
from .socialfam import FAMILIES

DAY = "<|day|>"
TOPK = 64       # the probes' value: the allowed argmax is nearly always in the top 64
LIMIT = 120     # tokens; the longest C6 parse line is well under this


def day_line(anchor: date) -> str:
    """`<|day|>YYYY-MM-DD Weekday` and its newline -- `rendergen.day_line`'s shape."""
    return f"{DAY}{anchor.isoformat()} {anchor.strftime('%A')}\n"


def head(name: str, anchor: date) -> str:
    """The v5 head: `name:` and the day, in the corpus's order. No `tools:`
    line -- see the module docstring."""
    return name_header(name) + day_line(anchor)


def _order(logits, k: int) -> list[int]:
    """Token ids by descending logit, the top `k` -- a torch tensor or a list."""
    if hasattr(logits, "topk"):
        return logits.topk(min(k, logits.shape[-1])).indices.tolist()
    return sorted(range(len(logits)), key=lambda i: logits[i], reverse=True)[:k]


def _argmax(logits, ids: list[int]) -> int:
    return max(ids, key=lambda i: float(logits[i]))


def bound_line(score, ids: list[int], con: ParseConstraint,
               limit: int = LIMIT) -> tuple[list[int], bool, int]:
    """Greedy under `con`, backtracking where the grammar strands him.

    `score(ids)` returns the next-token logits for a context of token ids.
    Returns the line's token ids (its closing newline included when the
    grammar closed it), whether it closed, and how many tokens were taken
    back. `con` must be reset and pointed at its parent by the caller."""
    vocab = con.vocab
    ids = list(ids)
    out: list[int] = []
    states = [con.state]
    banned: list[set[int]] = [set()]
    pops = 0
    for _ in range(limit * 4):
        if len(out) >= limit:
            break
        st = states[-1]
        logits = score(ids)
        nxt = next((t for t in _order(logits, TOPK) if t not in banned[-1]
                    and t not in con.special_ids and con._walk(st, vocab[t]) is not None), None)
        if nxt is None:
            allowed = [t for t in con.allowed_ids(st) if t not in banned[-1]]
            if allowed:
                nxt = _argmax(logits, allowed)
        if nxt is None:
            if not out:
                break
            gone = out.pop()
            ids.pop()
            states.pop()
            banned.pop()
            banned[-1].add(gone)
            pops += 1
            continue
        con.state, con.closed = st, False
        con.accept(nxt)
        out.append(nxt)
        ids.append(nxt)
        if con.closed:
            break
        states.append(con.state)
        banned.append(set())
    return out, con.closed, pops


class Layers:
    """The binds for one tokenizer, built once and reused every turn."""

    def __init__(self, tok, device: str = "cpu"):
        self.tok = tok
        self.parts = ParseConstraint(tok, device, PARSE_LABELS_1_0, "nested")
        self.move = ParseConstraint(tok, device, line="move")
        move_first = tok.encode(MOVE_PREFIX)[0]
        self.choice = {move_first: "move", tok.encode(D_SAY)[0]: "say",
                       tok.encode(D_CALL)[0]: "call"}

    def write(self, score, ctx: str, utterance: str) -> dict:
        """His layer lines for the turn whose `<|user|>` line ends `ctx`.

        Returns `{"text": the lines to append to the context, "parts": the
        line's body or None, "move": the value or None, "closed": the parse
        closed, "pops": tokens taken back}`. A parse the grammar could not
        close is not written -- the turn goes on with no `parts:` line, the
        shape the v4 corpus had, and the event says so."""
        ids = self.tok.encode(ctx)
        self.parts.reset()
        self.parts.set_parent(utterance)
        got, closed, pops = bound_line(score, ids, self.parts)
        rec = {"text": "", "parts": None, "move": None, "closed": closed, "pops": pops}
        if not closed:
            return rec
        line = self.tok.decode(got).split("\n")[0]
        rec["parts"] = line[len(PARTS_PREFIX):]
        rec["text"] = line + "\n"
        if rec["parts"] != "chat":
            return rec
        ids = ids + got
        logits = score(ids)
        if self.choice[_argmax(logits, list(self.choice))] != "move":
            return rec
        self.move.reset()
        mgot, mclosed, mpops = bound_line(score, ids, self.move)
        rec["pops"] += mpops
        if mclosed:
            mline = self.tok.decode(mgot).split("\n")[0]
            rec["move"] = mline[len(MOVE_PREFIX):]
            rec["text"] += mline + "\n"
        return rec


def move_family(move: str | None) -> str | None:
    """The social family a move names, or None when it names none."""
    return move if move in FAMILIES else None


def door_names(prompt: str, registry: tuple[str, ...]) -> tuple[str, ...] | None:
    """The names the next call may use under its part, or None to leave the
    declaration as it stands (no parse line, or no actionable part left)."""
    names = door.allowed_names(prompt, registry)
    return names or None


__all__ = ["DAY", "Layers", "bound_line", "day_line", "door_names", "head", "move_family",
           "MOVES_1_0", "PARTS_PREFIX"]
