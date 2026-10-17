"""The memory probe as an instrument: does he use a turn from further back than the last one?

ROADMAP R3, PLAN-1-0 §5c. The 2026-09-07 scratch probe -- a lookup, k filler
tool turns, then "what about {e}?" -- composed 2/5 with no filler and 0/5 with
one or more, under both trimmer settings (PLAN-CONVERSATION's decision 11
reads). It is the ruler slice 6.1 is written against and the block pilot
reads at depths 1-6, so it has to be an instrument before either exists.

**Built so that a miss can be explained by reading the card, not re-running
it.** A zero on this probe has at least five causes and they sit in
different places -- the trimmer dropped the turn, the fold kept the question
but not the answer, the turn was in view and he composed off the nearer
filler instead, he composed nothing and repeated a query, or the fillers
themselves knocked the lookup over -- and a single "composed n/k" column
cannot tell any of them apart. So every case carries:

  * **the window** -- what the probe turn was actually shown, read back from
    the server's `window` op (`harness/server.py`, `Session.window`), with the
    antecedent marked `whole`, `folded` or `gone`. That splits runtime from
    weights: a miss with the antecedent gone is the block and the trimmer, a
    miss with it whole is him. The block pilot's question is the first
    column; the corpus's is the second.
  * **structure and vocabulary in separate columns** (CLAUDE.md, "score
    structure and vocabulary apart"): which turn's *frame* the query carries
    (turn 1, a filler, none) and which *entity* (the new one, turn 1's, a
    filler's, none), beside the named outcome derived from them. "Composed off
    a filler" -- the filler's frame with the new entity -- is him composing,
    just off the wrong antecedent, and it would read as a plain miss without
    the split.
  * **three filler kinds** -- `chat` (a short social turn, no tool; it keeps
    turn 1 whole at every depth), `date` (a different tool, nothing shared
    with the frame) and `lookup` (the same tool on another frame: the
    competing antecedent). A depth effect under `chat` cannot be the trimmer.
  * **an explicit control at every depth** -- the full question ("the
    capital of spain") after the same fillers. If that fails too, the fillers
    broke the lookup and the follow-up's miss is not about memory.
  * **gates read before the probe** -- turn 1 must have done its own job (its
    query the frame on the old entity; for a note, `save_note` carrying the
    text), or the case is `unreadable: turn 1` and counted apart; every filler
    is checked against the route it should take, and misfires are a column.
  * **every raw event kept** -- the call as written, the arguments, the say,
    who authored it, what the fold did -- so `--rescore` re-scores a saved card
    with the current scorer (no GPU, no server) and `--explain` prints the
    failing cases whole, window included. When the scorer and the text
    disagree, suspect the scorer, fix it, and re-score the same card.

## Grid L -- the lookup follow-up

Turn 1 is one of chaingrid's four frames (borrowed for chaingrid's reason:
they read at ceiling first-turn, so a miss below them is attributable to
depth), on entity `a`. Then k fillers, k = 0..6 -- and 10, 15, 20 with
`--deep`, the 2048 arm's read (ROADMAP C9). Then the probe:

    follow      what about {b}?          the memory question
    explicit    the capital of {b}       the control: same fillers, no memory

    composed                 turn 1's frame on the new entity -- the gold
    composed, extra words    the same, padded past chaingrid's +2 words
    reissued turn 1          turn 1's query again, word for word
    reissued last            the turn before's query again (a lookup filler)
    copied last utterance    the turn before's *words* searched, when that
                             turn was a hatch and had no query of its own
    copied an older utterance  a filler further back, word for word
    copied the seed          the runtime's seed turn ("what day is it"),
                             which nobody typed
    literal                  the utterance searched as written
    composed off a filler    a filler's frame on the new entity
    entity only              the new entity, no frame
    something else / no call / no query
    other tool               with the tool (`route`) and whether the new
                             entity rode into it

Three pairs per frame (a->b, b->c, c->a), twelve cases a cell.

## Grid R -- recall

Turn 1 is "note down {text}", k fillers, then "what did I write down
first?" (PLAN-1-0's wording) or "what did I write down?" -- a minimal pair,
because "first" is a date word and pulled the plan's wording to
`resolve_date` on every case of the first read. No tool reads the note store back (`recall_day` is the day log), so
the only place the answer exists is the window. Scored on route and content
apart: `recalled` (no call, his say carries every content word),
`recalled in part`, `said, no content`, `re-saved` (`save_note` again),
`routed, carried the note` (another tool, the content in its arguments),
`routed`.

## Running it

**`--multi` is required** and the probe refuses without it. **Grid R writes
notes**: point `--notes` at a scratch path or it refuses (`checkup.py`'s
rule). **The lookups answer from the grid's own pack** (`PACK_ROWS`, and why
it exists), never `--search`; `t1_answered` says whether they did.

    python -m harness.memorygrid --write-pack <scratch>/pack
    python -m harness.server --ckpt <ckpt.pt> --multi --no-log \\
        --notes <scratch>/notes.jsonl --packs <scratch>/pack
    python -m harness.memorygrid --json harness/results/<tag>__memorygrid.json
    python -m harness.memorygrid --explain harness/results/<tag>__memorygrid.json \\
        --outcome "reissued last" --kind lookup --limit 5
    python -m harness.memorygrid --rescore harness/results/<tag>__memorygrid.json

Every entity is a country and every note a chore: ground rule 16, no
contact, no name, no instance fact. **A rate, not a gate.**
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from corn.markers import D_CALL, D_OBS, D_SAY, D_USER

from .chaingrid import FRAMES
from .client import Client
from .protocol import DEFAULT_HOST, DEFAULT_PORT
from .provenance import revision
from .serverconfig import DEFAULT_NOTES_STR

DEPTHS = tuple(range(7))
# **The 2048 arm's depths (ROADMAP C9, owner 2026-10-08: 10-20 turns in 1.0).**
# Off by default -- a 512 or 1024 checkpoint holds none of them whole, and the
# 0-6 grid is what every card on disk carries -- and read with `--deep`, which
# adds these to `DEPTHS`. The kill PLAN-1-0 §4 names is depth 10+ reading the
# same as depth 6 on the 2048 arm.
DEEP_DEPTHS = (10, 15, 20)
KINDS = ("chat", "date", "lookup")
PROBES = ("follow", "explicit")

# **Filler turns, by kind, each with the route it has to take.** Twenty of each
# so depth 20 never repeats one; the first six are the 0-6 grid's, unchanged, so
# a deep build's shallow cells are the cards' own. None carries a frame's key
# word, an entity, or a word that leans toward `place_call` / `send_text` --
# `check_memorygrid.py` asserts all three, because a filler that touched the
# frame would make "composed" partly the filler's doing. The added fourteen keep
# the first six's mix: most taken by a runtime hatch (the social pool, the
# temporal hatch), a few left to him.
CHAT_FILLERS = ("thanks", "ok cool", "got it", "nice, good to know",
                "great", "perfect, thanks",
                "cheers", "right", "fair enough", "lovely", "brilliant, thanks",
                "makes sense", "sounds good", "nice one", "that helps", "alright",
                "interesting", "ah ok", "cool, thanks", "neat")
DATE_FILLERS = ("what's the date next friday", "what day is tomorrow",
                "when is the first of march", "what date is two weeks from today",
                "what day was yesterday", "when is next monday",
                "when is a week on tuesday", "what date was last thursday",
                "what day will it be in ten days", "what's the date three days from now",
                "when is next sunday", "what day was it a week ago",
                "what's the date on wednesday", "when was last monday",
                "what's the date a month from today", "what day is the third of june",
                "when is the end of the month", "what day of the week is christmas",
                "what's the date this saturday", "what day is the fifth of november")
FILLER_ROUTE = {"chat": None, "date": "resolve_date", "lookup": "web_search"}

FOLLOW = "what about {e}?"
# **Two recall carriers, a minimal pair.** PLAN-1-0 §5c's wording carries
# "first", and the first CPU read sent it to `resolve_date {"expression":
# "first"}` on every case -- a date word pulling the route, which is the
# carrier-word trap CLAUDE.md names. The plan's wording stays, for continuity,
# and the same question without the word sits beside it, so the pull is a
# column rather than the whole grid.
R_PROBES = {"recall first": "what did I write down first?",
            "recall": "what did I write down?"}
NOTE_ASK = "note down {text}"
# Chores, no names. Each carries at least two content words so "in part" is a
# reading and not a coin flip.
NOTES = ("buy oat milk", "renew the car insurance", "water the tomatoes",
         "pick up the dry cleaning", "book a dentist appointment",
         "fix the kitchen tap")

# Words a query or a say may carry without carrying anything -- articles and
# the frames' glue. Content and key words are what is left.
STOP = frozenset({"the", "a", "an", "of", "to", "at", "about", "up", "on",
                  "for", "in", "and", "is", "what", "it"})

# **The lookups have to be answered, or the history is a list of failures.**
# Without `--search`, `web_search` answers out of the trained table, which
# holds invented countries only -- so every turn 1 came back "I couldn't find
# anything useful for the capital of france" and the probe was asked to compose
# off a miss, a context no conversation worth remembering has. Live search
# would fire ~1,500 queries and get the machine rate-limited (NOW.md §5). So
# the grid ships its own pack: `--write-pack DIR` writes this table as a CSV,
# the server takes `--packs DIR`, and `harness/backends/packs.py` answers every
# frame on every entity exactly and locally. Approximate figures; the scorer
# never reads the answer, only that there was one (`t1_answered`).
PACK_HEADER = ("country", "capital", "population", "currency",
               "official language")
PACK_ROWS = (
    ("france", "Paris", "68 million", "the euro", "French"),
    ("spain", "Madrid", "48 million", "the euro", "Spanish"),
    ("italy", "Rome", "59 million", "the euro", "Italian"),
    ("japan", "Tokyo", "124 million", "the yen", "Japanese"),
    ("brazil", "Brasilia", "212 million", "the real", "Portuguese"),
    ("kenya", "Nairobi", "56 million", "the shilling", "Swahili and English"),
    ("norway", "Oslo", "5.5 million", "the krone", "Norwegian"),
    ("peru", "Lima", "34 million", "the sol", "Spanish"),
    ("vietnam", "Hanoi", "101 million", "the dong", "Vietnamese"),
    ("egypt", "Cairo", "114 million", "the pound", "Arabic"),
    ("chile", "Santiago", "20 million", "the peso", "Spanish"),
    ("finland", "Helsinki", "5.6 million", "the euro", "Finnish and Swedish"),
)
PACK_FILE = "memorygrid_countries.csv"


def write_pack(folder: str) -> Path:
    path = Path(folder) / PACK_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(PACK_HEADER)] + [",".join(r) for r in PACK_ROWS]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


PROVENANCE = {
    "frames": "chaingrid.FRAMES, the four attribute shapes that read at "
              "ceiling first-turn, so a miss below them is attributable",
    "follow": "the carrier the 2026-09-07 scratch probe used and the stronger "
              "of chaingrid's two",
    "fillers": "written for this instrument; chat keeps turn 1 whole, date "
               "shares nothing, lookup is the competing antecedent",
    "notes": "written for this instrument; chores, ground rule 16",
}


def words(text: str) -> list[str]:
    return "".join(c.lower() if c.isalnum() else " " for c in text).split()


def key(frame: str) -> set[str]:
    """A frame's own words: what is left when the entity and the glue go."""
    return set(words(frame.replace("{e}", ""))) - STOP


# --------------------------------------------------------------------------
# Building the cases -- pure, unseeded, every case before any of them runs
# --------------------------------------------------------------------------


def lookup_fillers(frame: str, a: str, b: str, n: int = 6) -> list[str]:
    """`n` lookups on the other frames, never this frame or its entities.

    The first six are the 0-6 grid's, in its order. Past six (the deep cells)
    the other frames run over every pack country but `a` and `b`, so each is
    answered by `PACK_ROWS` and none names the case's own entities."""
    out = []
    others = [(f, es) for f, es in FRAMES if f != frame]
    for i in range(3):
        for f, es in others:
            e = es[i]
            if e not in (a, b):
                out.append(f.format(e=e))
    out = out[:6]
    countries = [r[0] for r in PACK_ROWS]
    for e in countries:
        for f, _es in others:
            q = f.format(e=e)
            if len(out) >= n:
                return out
            if e not in (a, b) and q not in out:
                out.append(q)
    return out[:n]


def build(grids=("L", "R"), kinds=KINDS, depths=DEPTHS,
          probes=PROBES, pairs: int = 3,
          r_probes=tuple(R_PROBES)) -> list[dict]:
    cases: list[dict] = []
    if "L" in grids:
        for frame, ents in FRAMES:
            for p in range(pairs):
                a, b = ents[p], ents[(p + 1) % len(ents)]
                for kind in kinds:
                    pool = {"chat": list(CHAT_FILLERS),
                            "date": list(DATE_FILLERS),
                            "lookup": lookup_fillers(frame, a, b,
                                                     max(depths))}[kind]
                    for depth in depths:
                        for probe in probes:
                            ask = (FOLLOW.format(e=b) if probe == "follow"
                                   else frame.format(e=b))
                            fill = pool[:depth]
                            cases.append({
                                "grid": "L", "probe": probe, "kind": kind,
                                "depth": depth, "frame": frame, "old": a,
                                "new": b, "fillers": fill,
                                "asks": [frame.format(e=a), *fill, ask],
                            })
    if "R" in grids:
        for n, text in enumerate(NOTES):
            for kind in kinds:
                pool = {"chat": list(CHAT_FILLERS), "date": list(DATE_FILLERS),
                        "lookup": lookup_fillers(FRAMES[n % len(FRAMES)][0],
                                                 "", "", max(depths))}[kind]
                for depth in depths:
                    for probe in r_probes:
                        fill = pool[:depth]
                        cases.append({
                            "grid": "R", "probe": probe, "kind": kind,
                            "depth": depth, "note": text, "fillers": fill,
                            "asks": [NOTE_ASK.format(text=text), *fill,
                                     R_PROBES[probe]],
                        })
    return cases


# --------------------------------------------------------------------------
# Scoring -- pure functions of the stored case, so `--rescore` is the live path
# --------------------------------------------------------------------------


def model_calls(turn: dict) -> list[dict]:
    return [c for c in turn.get("calls", []) if c.get("author", "model") != "runtime"]


def called(turn: dict) -> str | None:
    calls = model_calls(turn)
    return (calls[0].get("name") or "<malformed>") if calls else None


def query(turn: dict) -> str | None:
    calls = model_calls(turn)
    args = calls[0].get("arguments") if calls else None
    q = args.get("query") if isinstance(args, dict) else None
    return q.strip() if isinstance(q, str) else None


def arg_words(turn: dict) -> set[str]:
    out: set[str] = set()
    for c in model_calls(turn):
        args = c.get("arguments")
        if isinstance(args, dict):
            for v in args.values():
                if isinstance(v, str):
                    out |= set(words(v))
    return out


def asks_for(q: str | None, frame: str, e: str) -> bool:
    """chaingrid's composed rule: the frame's words, the entity, at most +2."""
    if not q:
        return False
    want, got = words(frame.format(e=e)), set(words(q))
    return set(want) <= got and len(got) <= len(want) + 2


def filler_misfires(case: dict) -> int:
    """Fillers that did not take their route, whoever wrote the call.

    **Any author, deliberately.** A date filler is usually the temporal
    hatch's (the runtime writes `resolve_date`) and a chat filler the social
    pool's; that is the real conversation a person would have, and what the
    probe has to read past. The probe and turn 1 are the opposite --
    `check_memorygrid.py` asserts no hatch takes either, so the gold is his.
    """
    route = FILLER_ROUTE[case["kind"]]
    turns = case.get("turns", [])[1:1 + len(case["fillers"])]
    return sum(1 for t in turns
               if (t.get("calls") or [{}])[0].get("name") != route)


def parts(case: dict, q: str) -> tuple[str, str]:
    """Structure and vocabulary apart: whose frame, whose entity."""
    got = set(words(q))
    filler_frames = [f for f, _ in FRAMES if f != case["frame"]]
    # What the query says besides the entities and the glue. When all of it
    # is words the fillers said, his frame came from a filler whatever the
    # kind: "what day is two weeks from spain" is a date filler's frame on
    # the new entity, and the first GPU read filed it as "entity only".
    rest = got - STOP - {case["new"], case["old"]}
    filler_words = {w for a in case["fillers"] for w in words(a)}
    if key(case["frame"]) <= got:
        frame_src = "turn 1"
    elif case["kind"] == "lookup" and any(key(f) <= got for f in filler_frames):
        frame_src = "filler"
    elif rest and rest <= filler_words:
        frame_src = "filler"
    else:
        frame_src = "none"
    every_key = set().union(*(key(f) for f, _ in FRAMES))
    filler_ents = {w for a in case["fillers"] for w in words(a)} - STOP - every_key
    if case["new"] in got:
        ent = "new"
    elif case["old"] in got:
        ent = "old"
    elif case["kind"] == "lookup" and got & filler_ents:
        ent = "filler"
    else:
        ent = "none"
    return frame_src, ent


L_OUTCOMES = ("composed", "composed, extra words", "reissued turn 1",
              "reissued last", "copied last utterance",
              "copied an older utterance", "copied the seed", "literal",
              "composed off a filler",
              "entity only", "something else", "other tool", "no call",
              "no query", "unreadable: turn 1", "turn raised")
R_OUTCOMES = ("recalled", "recalled in part", "said, no content", "re-saved",
              "routed, carried the note", "routed", "unreadable: turn 1",
              "turn raised")


def score_lookup(case: dict) -> dict:
    turns = case.get("turns", [])
    if len(turns) < len(case["asks"]):
        return {"outcome": "no call", "error": "the case did not finish"}
    if not asks_for(query(turns[0]), case["frame"], case["old"]):
        return {"outcome": "unreadable: turn 1"}
    probe = turns[-1]
    name = called(probe)
    if name is None:
        return {"outcome": "no call", "frame": None, "entity": None}
    if name != "web_search":
        # Which tool, and whether he still carried the new entity into it --
        # the first CPU read sent `resolve_date {"expression": "brazil"}`
        # after date fillers: the route followed the fillers, the entity
        # followed the request.
        got = arg_words(probe)
        return {"outcome": "other tool", "route": name,
                "entity": "new" if case["new"] in got else (
                    "old" if case["old"] in got else "none")}
    q = query(probe)
    if not q:
        return {"outcome": "no query", "frame": None, "entity": None}
    frame_src, ent = parts(case, q)
    qw = words(q)
    prev = query(turns[-2]) if len(turns) >= 2 else None
    if asks_for(q, case["frame"], case["new"]):
        out = "composed"
    elif frame_src == "turn 1" and ent == "new":
        out = "composed, extra words"
    elif qw == words(query(turns[0]) or ""):
        out = "reissued turn 1"
    elif prev and qw == words(prev):
        out = "reissued last"
    elif len(turns) >= 2 and qw == words(turns[-2]["ask"]):
        # The turn before was hatched (a date filler's `resolve_date` is the
        # runtime's), so there is no query to reissue -- and he searched its
        # *words*. Found by hand in the first CPU read, filed as "something
        # else" until then.
        out = "copied last utterance"
    elif any(qw == words(t["ask"]) for t in turns[1:-2]):
        # A filler further back, word for word -- "what day was yesterday"
        # five turns after it was said (first GPU read, date fillers).
        out = "copied an older utterance"
    elif case.get("seed") and qw == words(case["seed"]):
        # The runtime's seed turn, which he never typed -- PLAN-CONVERSATION
        # 4j's contamination channel, reached here by the probe at depth 6
        # under chat fillers ("what day is it").
        out = "copied the seed"
    elif qw == words(probe["ask"]):
        out = "literal"
    elif frame_src == "filler" and ent == "new":
        out = "composed off a filler"
    elif ent == "new" and frame_src == "none":
        out = "entity only"
    else:
        out = "something else"
    return {"outcome": out, "frame": frame_src, "entity": ent}


def coverage(content: set[str], seen: set[str]) -> str:
    hit = content & seen
    return "all" if hit == content else ("some" if hit else "none")


def score_recall(case: dict) -> dict:
    turns = case.get("turns", [])
    if len(turns) < len(case["asks"]):
        return {"outcome": "said, no content", "error": "the case did not finish"}
    content = set(words(case["note"])) - STOP
    if called(turns[0]) != "save_note" or coverage(content, arg_words(turns[0])) == "none":
        return {"outcome": "unreadable: turn 1"}
    probe = turns[-1]
    name = called(probe)
    in_say = coverage(content, set(words(probe.get("say", ""))))
    in_call = coverage(content, arg_words(probe))
    cols = {"route": name or "none", "in_say": in_say, "in_call": in_call,
            "say_author": probe.get("say_author")}
    if name is None:
        if in_say == "all" and probe.get("say_author", "model") == "model":
            out = "recalled"
        elif in_say != "none":
            out = "recalled in part"
        else:
            out = "said, no content"
    elif name == "save_note":
        out = "re-saved"
    else:
        out = "routed, carried the note" if in_call != "none" else "routed"
    return {"outcome": out, **cols}


def user_line(entry: str) -> list[str]:
    if D_USER not in entry:
        return []
    return words(entry.split(D_USER, 1)[1].split("\n", 1)[0])


def antecedent(case: dict) -> dict:
    """Where turn 1 sat in what the probe was shown, if the server said."""
    win = case.get("window")
    if not win or "entries" not in win:
        return {"state": "unknown"}
    entries, tokens = win["entries"], win["tokens"]
    probe_ok = bool(entries) and user_line(entries[-1]) == words(case["asks"][-1])
    prior = entries[:-1] if probe_ok else entries
    want = words(case["asks"][0])
    at = next((i for i, e in enumerate(prior) if user_line(e) == want), None)
    out = {"window_ok": probe_ok, "entries": len(prior),
           "prior_tokens": sum(tokens[:len(prior)]), "room": win.get("room")}
    if at is None:
        return {"state": "gone", **out}
    e = prior[at]
    state = "whole" if (D_CALL in e or D_OBS in e) else "folded"
    return {"state": state, "back": len(prior) - at, **out}


def answered(turn: dict) -> bool:
    """The turn's observation carried an answer, not a miss or a clarify."""
    return any('"answer"' in (o.get("payload") or "") for o in turn.get("obs", []))


def score(case: dict) -> dict:
    # **A turn the runtime raised on is an outcome, not the end of the run.**
    # The first GPU read lost 600 finished cases to one `UnboundLocalError` in
    # `Agent.turn`; a crash is a finding about the runtime and gets counted
    # beside the others, with the turn it happened on.
    raised = next(((i, t) for i, t in enumerate(case.get("turns", []), 1)
                   if t.get("error")), None)
    if raised:
        return {"outcome": "turn raised", "at": raised[0],
                "error": raised[1]["error"][:200], "misfires": 0,
                "antecedent": {"state": "unknown"}}
    s = score_lookup(case) if case["grid"] == "L" else score_recall(case)
    turns = case.get("turns", [])
    extra = {"t1_answered": answered(turns[0])} if case["grid"] == "L" and turns else {}
    return {**s, **extra, "misfires": filler_misfires(case),
            "antecedent": antecedent(case)}


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------


def run_turn(client: Client, ask: str) -> dict:
    turn: dict = {"ask": ask, "calls": [], "obs": []}
    for ev in client.request(op="turn", user=ask):
        kind = ev.get("t")
        if kind == "call":
            turn["calls"].append({k: ev.get(k) for k in
                                  ("name", "arguments", "raw", "ok", "masked",
                                   "author") if k in ev})
        elif kind == "obs":
            turn["obs"].append({"name": ev.get("name"),
                                "payload": json.dumps(ev.get("payload"))[:240]})
        elif kind == "say":
            turn["say"] = ev.get("text") or ""
            turn["say_author"] = ev.get("author")
            if ev.get("fell_back"):
                turn["fell_back"] = ev["fell_back"]
        elif kind == "fold":
            turn["folded"] = ev.get("folded")
        elif kind == "rejected":
            turn["rejected"] = ev.get("why")
        elif kind == "done":
            turn["ms"] = ev.get("ms")
        elif kind == "error":
            turn["error"] = ev.get("why", "?")
    return turn


def run_case(client: Client, case: dict) -> dict:
    for _ in client.request(op="reset"):
        pass
    case["turns"] = []
    for ask in case["asks"]:
        t = run_turn(client, ask)
        case["turns"].append(t)
        if t.get("error"):
            return case
    for ev in client.request(op="window"):
        if ev.get("t") == "window":
            case["window"] = {k: ev[k] for k in ("entries", "tokens", "room",
                                                 "block_size") if k in ev}
    return case


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

STATES = ("whole", "folded", "gone", "unknown")


def cell_rows(cases: list[dict], grid: str, probe: str, kind: str) -> dict:
    out = {}
    for d in sorted({c["depth"] for c in cases}):
        rows = [c for c in cases if c["grid"] == grid and c["probe"] == probe
                and c["kind"] == kind and c["depth"] == d]
        if not rows:
            continue
        out[d] = {
            "n": len(rows),
            "outcomes": dict(Counter(c["score"]["outcome"] for c in rows)),
            "antecedent": dict(Counter(c["score"]["antecedent"]["state"]
                                       for c in rows)),
            "misfires": sum(c["score"]["misfires"] for c in rows),
        }
    return out


def gold(grid: str) -> str:
    return "composed" if grid == "L" else "recalled"


def print_cell(title: str, rows: dict, outcomes: tuple[str, ...]) -> None:
    shown = [o for o in outcomes
             if any(r["outcomes"].get(o) for r in rows.values())]
    print(f"\n  {title}")
    head = "  ".join(f"{o[:12]:>12}" for o in shown)
    print(f"    {'depth':<6}{head}   | {'whole':>5} {'fold':>5} {'gone':>5} | misfire")
    for d, r in rows.items():
        line = "  ".join(f"{r['outcomes'].get(o, 0):>12}" for o in shown)
        a = r["antecedent"]
        print(f"    {d:<6}{line}   | {a.get('whole', 0):>5} {a.get('folded', 0):>5} "
              f"{a.get('gone', 0):>5} | {r['misfires']:>3}   of {r['n']}")


def report(cases: list[dict]) -> dict:
    grids: dict = {}
    for grid, probes, outcomes in (("L", PROBES, L_OUTCOMES),
                                   ("R", tuple(R_PROBES), R_OUTCOMES)):
        mine = [c for c in cases if c["grid"] == grid]
        if not mine:
            continue
        print("\n" + "=" * 78)
        print("Grid L -- the lookup follow-up" if grid == "L" else
              "Grid R -- recall of a note")
        g: dict = {}
        for probe in probes:
            for kind in KINDS:
                rows = cell_rows(mine, grid, probe, kind)
                if rows:
                    print_cell(f"{probe} / {kind} fillers", rows, outcomes)
                    g[f"{probe}|{kind}"] = rows
        # **The attribution line**: the gold by where the antecedent sat.
        # Gone is the block and the trimmer; whole is the weights.
        for probe in (("follow",) if grid == "L" else tuple(R_PROBES)):
            readable = [c for c in mine if c["probe"] == probe
                        and c["depth"] > 0
                        and c["score"]["outcome"] != "unreadable: turn 1"]
            if not readable:
                continue
            by = {}
            print(f"\n  {probe}: {gold(grid)}, by where turn 1 sat "
                  f"(depth 1+, readable):")
            for st in STATES:
                rows = [c for c in readable
                        if c["score"]["antecedent"]["state"] == st]
                if rows:
                    k = sum(1 for c in rows if c["score"]["outcome"] == gold(grid))
                    by[st] = {"gold": k, "n": len(rows)}
                    print(f"    {st:<8} {k:>4}/{len(rows)}")
            g[f"by_antecedent|{probe}"] = by
        unread = sum(1 for c in mine if c["score"]["outcome"] == "unreadable: turn 1")
        g["unreadable"] = unread
        print(f"    unreadable (turn 1 failed its own job): {unread}/{len(mine)}")
        if grid == "L":
            ans = sum(1 for c in mine if c["score"].get("t1_answered"))
            g["t1_answered"] = ans
            print(f"    turn 1 answered (not a miss): {ans}/{len(mine)}"
                  + ("" if ans == len(mine) else
                     "   !! start the server with --packs (see --write-pack)"))
        # **Depth 0 is the same input under every filler kind**, so the kinds
        # must agree there. A disagreement is the decode, not the memory.
        zero: dict = {}
        for c in mine:
            if c["depth"] == 0:
                ident = (c["probe"], c.get("frame"), c.get("old"), c.get("new"),
                         c.get("note"))
                zero.setdefault(ident, set()).add(c["score"]["outcome"])
        agree = sum(1 for v in zero.values() if len(v) == 1)
        g["depth0_agree"] = {"agree": agree, "n": len(zero)}
        print(f"    depth 0 agrees across filler kinds: {agree}/{len(zero)}")
        grids[grid] = g
    return grids


def card(cases: list[dict], info: dict, seconds: float | None) -> dict:
    return {
        "harness": "memorygrid/1",
        "when": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": revision(),
        "decode": {k: info.get(k) for k in
                   ("temperature", "speech_temperature", "multi", "dtype",
                    "search", "packs", "fold", "seed_turn", "block_size")},
        "instance": info,
        "provenance": PROVENANCE,
        "grids": report(cases),
        "seconds": seconds,
        "cases": cases,
    }


# --------------------------------------------------------------------------
# Reading a card back
# --------------------------------------------------------------------------


def short(text: str | None, n: int = 70) -> str:
    text = (text or "").replace("\n", " | ")
    return text if len(text) <= n else text[:n - 3] + "..."


def explain(case: dict) -> None:
    s = case["score"]
    a = s["antecedent"]
    what = (f"{case['frame'].format(e=case['old'])} -> {case['new']}"
            if case["grid"] == "L" else f"note: {case['note']}")
    cols = ", ".join(f"{k} {v}" for k, v in s.items()
                     if k not in ("outcome", "antecedent", "misfires") and v)
    print(f"\n[{case['grid']} {case['probe']} {case['kind']} d{case['depth']}] "
          f"{what}\n  -> {s['outcome']}  ({cols})  misfires {s['misfires']}")
    print(f"  antecedent {a['state']}"
          + (f", {a['back']} back" if "back" in a else "")
          + (f", prior {a.get('prior_tokens')}/{a.get('room')} tok"
             if "room" in a else "")
          + ("" if a.get("window_ok", True) else "  !! window does not end on the probe"))
    for i, t in enumerate(case.get("turns", []), 1):
        calls = model_calls(t)
        call = (f"{calls[0].get('name')} {json.dumps(calls[0].get('arguments'))}"
                if calls else "-")
        print(f"   {i:>2} {short(t['ask'], 34):<34} {short(call, 60):<60} "
              f"say[{t.get('say_author')}] {short(t.get('say'), 50)!r}")
        if t.get("error") or t.get("rejected"):
            print(f"      !! {t.get('error') or t.get('rejected')}")
    win = case.get("window")
    if win and "entries" in win:
        want = words(case["asks"][0])
        print("   window the probe read:")
        for e, n in zip(win["entries"], win["tokens"]):
            mark = "  <- turn 1" if user_line(e) == want else ""
            form = "whole " if (D_CALL in e or D_OBS in e) else (
                "folded" if D_SAY in e else "open  ")
            print(f"     {n:>4} tok {form} {short(e, 90)}{mark}")


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    ap = argparse.ArgumentParser(description="the memory probe, depths 0-6 "
                                             "(and 10, 15, 20 with --deep)")
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--grid", choices=("L", "R"), action="append")
    ap.add_argument("--kind", choices=KINDS, action="append")
    ap.add_argument("--depth", type=int, action="append")
    ap.add_argument("--deep", action="store_true",
                    help=f"add depths {DEEP_DEPTHS} -- the 2048 arm's read "
                         f"(ROADMAP C9); a 512 or 1024 block holds none whole")
    ap.add_argument("--probe", choices=(*PROBES, *R_PROBES), action="append")
    ap.add_argument("--pairs", type=int, default=3,
                    help="entity pairs per frame, 1-3 (12 cases a cell at 3)")
    ap.add_argument("--json", help="write the scorecard here")
    ap.add_argument("--explain", metavar="CARD",
                    help="print the cases of a saved card whole; filter with "
                         "--grid/--kind/--depth/--probe/--outcome")
    ap.add_argument("--outcome", action="append",
                    help="with --explain: only cases with this outcome")
    ap.add_argument("--state", choices=STATES, action="append",
                    help="with --explain: only cases whose antecedent sat so")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--rescore", metavar="CARD",
                    help="re-score a saved card with this scorer, print what "
                         "moved, and write it to --json if given")
    ap.add_argument("--write-pack", metavar="DIR",
                    help="write the countries table the lookups answer from "
                         "into DIR, for the server's --packs, and exit")
    args = ap.parse_args()

    if args.write_pack:
        print(f"wrote {write_pack(args.write_pack)} -- start the server with "
              f"--packs {args.write_pack}")
        return 0

    if args.explain or args.rescore:
        c = load(args.explain or args.rescore)
        cases = c["cases"]
        if args.rescore:
            moved = 0
            for case in cases:
                case.setdefault("seed", c.get("instance", {}).get("seed_turn") or "")
                new = score(case)
                if new["outcome"] != case.get("score", {}).get("outcome"):
                    moved += 1
                    print(f"  moved: [{case['grid']} {case['probe']} {case['kind']} "
                          f"d{case['depth']}] {case.get('score', {}).get('outcome')}"
                          f" -> {new['outcome']}")
                case["score"] = new
            print(f"  {moved} of {len(cases)} cases moved")
            fresh = card(cases, c.get("instance", {}), c.get("seconds"))
            fresh["rescored_from"] = c.get("when")
            if args.json:
                with open(args.json, "w", encoding="utf-8") as fh:
                    json.dump(fresh, fh, separators=(",", ":"))
                print(f"  wrote {args.json}")
            return 0
        picked = [x for x in cases
                  if (not args.grid or x["grid"] in args.grid)
                  and (not args.kind or x["kind"] in args.kind)
                  and (not args.depth or x["depth"] in args.depth)
                  and (not args.probe or x["probe"] in args.probe)
                  and (not args.outcome or x["score"]["outcome"] in args.outcome)
                  and (not args.state
                       or x["score"]["antecedent"]["state"] in args.state)]
        print(f"{len(picked)} cases match; showing {min(len(picked), args.limit)}")
        for x in picked[:args.limit]:
            explain(x)
        return 0

    try:
        client = Client(args.host, args.port)
    except ConnectionRefusedError:
        print(f"nothing listening on {args.host}:{args.port} -- start it with "
              f"`python -m harness.server --multi`", file=sys.stderr)
        return 2
    info: dict = {}
    for ev in client.request(op="info"):
        if ev.get("t") == "info":
            info = {k: v for k, v in ev.items() if k not in ("t", "id")}
    print(f"memorygrid against {info.get('ckpt')}")
    print(f"  temperature {info.get('temperature')}   multi {info.get('multi')}"
          f"   seed {info.get('seed_turn')!r}   fold {info.get('fold')}"
          f"   notes {info.get('notes')}")
    if not info.get("multi"):
        print("\nthis instance is not --multi: every probe opens on an empty "
              "history and has nothing to remember. Restart with --multi.",
              file=sys.stderr)
        return 2
    grids = tuple(args.grid or ("L", "R"))
    if "R" in grids and Path(str(info.get("notes"))).resolve() == \
            Path(DEFAULT_NOTES_STR).resolve():
        print("\ngrid R writes notes and this instance writes them to the "
              "default store. Restart with --notes <scratch path>, or run "
              "--grid L.", file=sys.stderr)
        return 2

    probes = tuple(args.probe or (*PROBES, *R_PROBES))
    depths = tuple(args.depth if args.depth is not None else DEPTHS)
    if args.deep:
        depths = tuple(sorted(set(depths) | set(DEEP_DEPTHS)))
    if max(depths) > len(CHAT_FILLERS):
        print(f"depth {max(depths)} needs more than the {len(CHAT_FILLERS)} fillers "
              f"a kind has", file=sys.stderr)
        return 2
    planned = build(grids, tuple(args.kind or KINDS), depths,
                    tuple(p for p in probes if p in PROBES), args.pairs,
                    tuple(p for p in probes if p in R_PROBES))
    print(f"  {len(planned)} cases, {sum(len(x['asks']) for x in planned)} "
          f"turns planned")

    started = time.perf_counter()
    def save_partial(done: list[dict]) -> None:
        # Raw cases only, no report: `--rescore` turns this into a card.
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump({"harness": "memorygrid/1", "partial": True,
                           "instance": info, "cases": done}, fh)

    for i, case in enumerate(planned, 1):
        try:
            run_case(client, case)
        except (OSError, ValueError) as exc:  # the server went away
            print(f"\nthe server stopped answering at case {i}: {exc}; "
                  f"{i - 1} cases saved to {args.json} -- `--rescore` reads "
                  f"them", file=sys.stderr)
            save_partial(planned[:i - 1])
            return 2
        case["seed"] = info.get("seed_turn") or ""
        case["score"] = score(case)
        if case["score"]["outcome"] == "turn raised":
            print(f"  turn raised at case {i}: {case['asks'][case['score']['at'] - 1]!r}"
                  f" -- {case['score']['error'][:120]}", flush=True)
        if i % 50 == 0:
            print(f"  {i}/{len(planned)} cases, "
                  f"{time.perf_counter() - started:.0f}s", flush=True)
            save_partial(planned[:i])
    seconds = round(time.perf_counter() - started, 1)
    out = card(planned, info, seconds)
    print(f"\n  {len(planned)} cases in {seconds}s")
    client.close()
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, separators=(",", ":"))
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
