"""What `recall_day` returns, and what Corn-Jr says once he has it.

**The corpus asks this question 90,293 times and never answers it once.**
Counted 2026-08-18 over `data/raw/temporal.txt`: 90,293 transcripts emit
`{"name": "recall_day", ...}` and then `<|end|>`. No observation, no reply. 55%
of the temporal slice -- the largest generated slice in the corpus -- stops mid
chain, and there is no `recall_day` observation anywhere else in `data/raw/`
either. So the only thing the corpus has ever taught about the day log is
**how to ask for it**, and `temporal.route` at 399/400 is scoring exactly that.

`corn/temporal.py`'s docstring gives the rule the truncation comes from --
"generated here is the *call*, never the answer. The tool does the maths." That
is right for `resolve_date`, whose answer is arithmetic a 250M model must never
learn to perform, and it is the core bet (VISION §2) stated at the level of one
tool. It is **wrong for `recall_day`**, whose answer is not arithmetic. It is
prose, it is the user's own history, and reading it back is the capability
VISION §5.2 calls the signature idea and §9.6 makes a success criterion:

    "What was I doing last Thursday?" answered correctly, from the day log.

The rule was decided for the first tool and inherited by the second, which is
the same shape as the pilot's shares being inherited by eight corpora. Every
other tool in the project already teaches the full loop -- `corn/tools.py`
writes `<|obs|>` then `<|say|>` for all 10,000 transcripts in `tools.txt`, 2,400
of them failures. The day log is the sole exception, and it is the one that
matters most.

## What this module is, and what it deliberately is not

It is the **content** of a day, kept out of `corn/temporal.py` on purpose. That
file is 1,386 lines of date arithmetic with a `check_temporal.py` asserting its
two implementations agree; a day's events have nothing to do with any of it, and
folding them in would put prose pools inside the module whose whole discipline
is that ground truth is exact by construction.

It is **not** a memory system. VISION §5.1 and §5.5 put the real store outside
the model, application-side, and Phase 5 builds it. This is the pretraining
prior for reading one back: what the payload looks like, and that a reply
follows it.

## Where the material comes from, and why it is not written here

The entries are rendered from `corn.toolspace.DOMAINS`, which is the same value
space the tool slices draw on. **A day log is a record of what the tools did**,
so generating it from anywhere else would put a second vocabulary in the corpus
describing the same world. Reuse also inherits that module's guarantee for
free: `HELD_OUT_DOMAINS` is disjoint from `DOMAINS` at 0 overlapping value
strings, measured, so an eval log built from the held-out side is structurally
unreachable from training in the way `HELD_OUT_FACTS` and `HELD_OUT_NOTES` are
for the copy rows.

**§11's copyable-span rule is why the scored span is the topic and not the
frame.** The report frames below are few and are meant to be -- the model should
learn the shape of a reply cheaply. The *topics* are the wide space, **67
distinct** over 14 usable domains on the training side, and they are what an eval
scores for exactness. Generate
what he must copy exactly over a wide value space; keep the phrasing narrow.
That is the rule the tools slice was rebuilt under and it applies here unchanged.

## The honest limit, recorded before the row is read rather than after

`HELD_OUT_DOMAINS` carries **16 distinct values**. An eval of 200 items over 16
topics is quantised at ~12 items, so the confabulation-versus-recitation half of
any row built on this cannot report anything finer than that. This is
`tool_copy.jsonl`'s six-fact quantum, which sat in the manifest as
`tool_copy_answers: 6` from the day it was built while fourteen findings quoted
the row out of 120. Writing it down at the source this time is the whole of the
lesson; widening it means more `HELD_OUT_DOMAINS` entries and nothing else.

**The other half of the row is not quantised at all.** Whether he says anything
rather than emitting a second call needs no topic cardinality -- any log will
do -- and that is the half this corpus defect predicts.
"""

from __future__ import annotations

import random
from datetime import date

from .temporal import WEEKDAYS
from .toolspace import DOMAINS, HELD_OUT_DOMAINS, VERBS

# How a completed action reads in a log. The **domain's own ask frame** carries
# the verb and the preposition, so `note` reads "make a note that the spare key
# is with Ann" and `alarm` reads "set an alarm for seven am"; a per-sense frame
# table cannot do that, because `DOMAINS` values are noun phrases in some
# domains and whole clauses in others. Written the short way first and it
# produced "got the spare key is with Ann going", which is what sent this back
# to the domain tables.
#
# Past tense comes from the wrapper rather than from rewriting the frame, since
# the frames are imperative and VISION §5.2 says the log records what happened
# when you interacted with him -- so "asked me to {ask}" is both grammatical and
# literally what the entry is.
REPORT_WRAPPERS = ("asked me to {a}", "had me {a}", "got me to {a}")

# Ask frames that will take a wrapper: the ones that open with a bare verb.
# **An allowlist, after a blocklist was tried and was wrong** -- rejecting
# questions and negatives still let through "weather {v}", "directions to {v}"
# and "where's {v}", which are a noun, a noun and a question, so the wrapper
# produced "asked me to weather here". A frame is usable here only if its first
# word is an imperative verb, and that is a property no blocklist can test.
#
# Seeded from `toolspace.VERBS`, which is where that module's action senses come
# from, plus the frame-initial verbs its ask templates actually use. A domain
# whose frames all open with something else is **dropped**, not fallen back to:
# `forecast` and `route` are the two live cases -- `forecast`'s frames are all
# questions ("what's the forecast for {v}", "weather {v}") and `route`'s all take
# a dative "me" -- and a fallback would put "asked me to weather here" into
# 100,000 transcripts. 14 of 16 training domains and 4 of 4 held-out ones survive.
# `scripts/check_daylog.py` pins those two counts, so a `toolspace` edit that
# silently drops another one fails there instead of shrinking the space quietly.
IMPERATIVE_VERBS = frozenset(
    v for verbs in VERBS.values() for v in verbs
) | frozenset({
    "book", "dig", "fire", "get", "give", "make", "note", "play", "put",
    "queue", "remember", "remind", "schedule", "track", "wake",
})

# Clock times a day's events land on. Spoken shape, because §3 says the reply is
# read out loud and "09:20" is not a thing anybody says.
TIMES = (
    "just after eight", "half eight", "around nine", "mid-morning",
    "just before eleven", "around noon", "just after one", "mid-afternoon",
    "around three", "just before five", "early evening", "after dinner",
)

# How the reply reports one entry. Narrow on purpose -- see the module
# docstring's note on §11. `{v}` is the topic and is the scored span; `{t}` is
# the time word, which nothing scores.
SAY_FRAMES = (
    "You {r} -- {t}.",
    "{t}, you {r}.",
    "That was the day you {r}.",
    "You {r}, {t}.",
)

# When the day has nothing in it. A log that is always full teaches that the
# tool always answers, which is the failure mode `corn/tools.py` spends 24% of
# its transcripts avoiding on the other tools.
EMPTY_SAY = (
    "Nothing in the log for that day.",
    "That day's empty -- nothing recorded.",
    "I've got nothing down for then.",
)

EMPTY_SHARE = 0.12

MIN_ENTRIES, MAX_ENTRIES = 2, 4


def _imperative(frames: tuple[str, ...]) -> tuple[str, ...]:
    """The ask frames that open with a bare verb and take no dative `me`.

    May be empty -- see the note on `IMPERATIVE_VERBS`.

    The second test is the wrapper's fault rather than the frame's: every
    wrapper already contains "me", so "get me a {v} recipe" comes out as "had me
    get me a carbonara recipe". Rejected here rather than by rewriting the
    wrappers, because "asked me to" is the one that makes the entry read as what
    it is and the alternatives ("you had X done") lose the person.
    """
    words = [f.lower().split() for f in frames]
    return tuple(
        f for f, w in zip(frames, words)
        if w[0] in IMPERATIVE_VERBS and (len(w) < 2 or w[1] != "me")
    )


# Computed once. A domain with no usable frame is not in the space at all.
TRAIN_DOMAINS = tuple(d for d in DOMAINS if _imperative(d[4]))
EVAL_DOMAINS = tuple(d for d in HELD_OUT_DOMAINS if _imperative(d[4]))


def _domains(held_out: bool) -> tuple[tuple, ...]:
    return EVAL_DOMAINS if held_out else TRAIN_DOMAINS


def topics(held_out: bool = False) -> tuple[str, ...]:
    """Every topic string on one side of the split, deduplicated.

    Public because a scorer needs the *training* pool to accuse a reply of
    recitation, exactly as `score_note_fidelity` reaches for `NOTES`.
    """
    seen: dict[str, None] = {}
    for d in _domains(held_out):
        for v in d[3]:
            seen[v] = None
    return tuple(seen)


def entry(rng: random.Random, held_out: bool = False) -> dict:
    """One logged event: a time, the topic, and how it reads.

    `topic` is carried beside `text` rather than left to be parsed back out of
    it, because it is the span an eval scores and a scorer that had to
    re-extract it would be re-implementing this function's formatting rules in
    a second place.
    """
    domain = rng.choice(_domains(held_out))
    noun, values, asks = domain[0], domain[3], domain[4]
    topic = rng.choice(values)
    ask = rng.choice(_imperative(asks)).format(v=topic)
    return {
        "time": rng.choice(TIMES),
        "topic": topic,
        "domain": noun,
        "text": rng.choice(REPORT_WRAPPERS).format(a=ask),
    }


def day_log(d: date, rng: random.Random, held_out: bool = False,
            allow_empty: bool = True) -> dict:
    """The `recall_day` observation for one date.

    Shape follows `corn/toolspace.py`'s rule and the thirty-third finding behind
    it: **a bare object of the tool's own fields, one level deep.** That finding
    measured one level of nesting taking every copy row to zero, so the entries
    list is a list of flat objects and nothing below it nests further.

    `entries` is empty ~12% of the time. The empty case is not a failure -- the
    tool worked and the day was quiet -- so it carries no `ok: false`, and that
    distinction is the one `corn/tools.py` draws between a refusal and an
    answer.
    """
    if allow_empty and rng.random() < EMPTY_SHARE:
        return {"date": d.isoformat(), "weekday": WEEKDAYS[d.weekday()], "entries": []}

    n = rng.randint(MIN_ENTRIES, MAX_ENTRIES)
    entries: list[dict] = []
    used: set[str] = set()
    # Distinct topics within a day. A log naming the same thing twice would make
    # "which entry did he read" unanswerable on any item built from it, and the
    # targeted half of the eval row rests on exactly that being answerable.
    for _ in range(n * 4):
        if len(entries) >= n:
            break
        e = entry(rng, held_out)
        if e["topic"] in used:
            continue
        used.add(e["topic"])
        entries.append(e)
    return {"date": d.isoformat(), "weekday": WEEKDAYS[d.weekday()], "entries": entries}


def speak(log: dict, rng: random.Random, which: int | None = None) -> tuple[str, str | None]:
    """The reply, and the topic it is scored against.

    Returns `(sentence, topic)`. `topic` is `None` for an empty day, where there
    is no span to copy and the correct behaviour is to say so.

    **The reply names one entry, not all of them.** §3 asks for short spoken
    utterances -- the conversational anchor breaks at 13.5 words -- and a model
    that learns to recite a four-item list back at a voice interface has learned
    the wrong thing from the right payload. Which entry is the caller's choice
    so that a targeted question can select one.
    """
    entries = log["entries"]
    if not entries:
        return rng.choice(EMPTY_SAY), None
    e = entries[rng.randrange(len(entries))] if which is None else entries[which]
    said = rng.choice(SAY_FRAMES).format(r=e["text"], t=e["time"])
    # One frame opens on the time word, which is lower-case in `TIMES` because it
    # is mid-sentence in the other three. Capitalised here rather than by keeping
    # two copies of the pool.
    return said[0].upper() + said[1:], e["topic"]
