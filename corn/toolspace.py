"""Tools declared in the prompt, over a space too large to learn as a set.

README's thirty-third finding says the model does not read the tool's name: an
unseen name in `<|call|>` costs 3 of 300 where a nested payload costs everything.
That is the answer half of a tool call working on a tool nobody trained on. The
*choice* half has never been testable, because the runtime prompt is
`<|user|>{text}` and nothing else -- no declaration reaches the model, so it
cannot fail to route to a tool it was never told about.

**This is the `sayvar` argument applied to tool identity.** `refusal.clarify`
read 0/47 on six checkpoints across two model sizes and looked like a model
limit; it was a corpus fact, and one file moved it (`45a98e9`). Tool identity is
in exactly the regime `clarify` was in: five names, every tool-bearing transcript
in the corpus drawing from them, so the name is worth 40,000 uses and the
declaration is worth nothing. The corpus has never given Corn-Jr a reason to
read a tool name. This slice gives him one.

**The space is composed, not written**, for the reason `sayvar`'s pools were:
the point is not more names but a space too large to memorise. `verb x modifier
x noun` reaches ~35,000 names against a slice of ~200,000 examples, which puts
uses-per-name in `answer`'s regime (1.2) rather than `clarify`'s untreated one
(2,096). A hand-written list of two hundred tools would sit at a thousand uses
each and a null result would only have said the dose was small.

**No new marker, and that is forced.** `tokenizers/bpe8k.json` ships seven
specials and a fixed 8,192 vocab; an eighth would mean a new tokenizer file, a
different mapping, and every checkpoint in the project becoming incomparable.
The declaration is therefore plain text on its own line above `<|user|>`, which
keeps `tokenizer="bpe8k"` fixed so the corpus is the only thing that moves --
the discipline `mix_v1_sayvar` held and the reason its result is readable.

**Held-out tools are the whole point of the split.** `HELD_OUT_NOUNS` and
`HELD_OUT_MODIFIERS` are disjoint from the trained pools, so a declared tool
built from them is structurally unreachable from training -- the same guarantee
`HELD_OUT_FACTS` gives the copy rows and anchor dates give `temporal.route`.
An eval item declaring `queue_lakeside_playlist` cannot be answered by recall.

What this slice does *not* vary is the payload's shape, and that is deliberate.
The thirty-third finding measured shape as the load-bearing axis -- one level of
nesting takes every copy row to zero -- so a success here is a bare object of
the tool's own fields and a failure is `{"ok": false, "reason": ...}` carrying
`say` or `clarify`, exactly as `corn/tools.py` and `corn/temporal.py` write them.
Moving identity and shape at once would confound the one axis this is for.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass

from . import toolvalues
from .markers import D_CALL, D_END, D_OBS, D_SAY, D_USER
from .tools import DECLINE

# The declaration line. Plain text above `<|user|>`, one line, tools separated
# by ` | ` and a required param list in parentheses -- optional params carry a
# trailing `?`, which is the only piece of schema syntax here that has to be
# learned rather than read.
DECL_PREFIX = "tools: "
DECL_SEP = " | "

# --------------------------------------------------------------- the space

# Verbs carry the action sense; a domain declares which sense it accepts, so
# `cancel_kitchen_timer` is reachable and `queue_kitchen_timer` is not. Nonsense
# names would still compose, and would make the utterance impossible to write.
VERBS = {
    "fetch":  ("find", "fetch", "look_up", "search", "pull", "locate"),
    "start":  ("set", "start", "begin", "create", "add", "schedule"),
    "stop":   ("cancel", "clear", "stop", "remove", "delete", "end"),
    "report": ("check", "report", "show", "read", "list", "count"),
}

# (noun, sense, param, value pool, ask frames, say frames). The param name is
# part of the declaration and part of the call, so it is read rather than
# recalled -- which is the second thing this slice is for.
DOMAINS: tuple[tuple, ...] = (
    ("timer", "start", "duration", ("ten minutes", "an hour", "ninety seconds",
     "twenty minutes", "two hours", "forty-five minutes"),
     ("set a timer for {v}", "start a {v} timer", "give me a {v} timer",
      "can you put a timer on for {v}"),
     ("Timer set for {v}.", "Done -- {v}.", "{v}, starting now.")),
    ("alarm", "start", "time", ("seven am", "half six", "quarter past eight",
     "six thirty", "nine fifteen", "five am"),
     ("set an alarm for {v}", "wake me at {v}", "alarm for {v} please",
      "can you set an alarm for {v}"),
     ("Alarm set for {v}.", "You're up at {v}.", "Set -- {v}.")),
    ("reminder", "start", "text", ("call the dentist", "take the bins out",
     "book the car in", "water the plants", "ring mum back", "pay the gas bill"),
     ("remind me to {v}", "set a reminder to {v}", "don't let me forget to {v}",
      "put a reminder on to {v}"),
     ("I'll remind you to {v}.", "Reminder set.", "Noted -- {v}.")),
    ("track", "fetch", "title", ("the one about the river", "that summer song",
     "the slow piano one", "the live version", "the acoustic take"),
     ("find {v}", "look for {v}", "can you dig out {v}", "play me {v}"),
     ("Found {v}.", "Here's {v}.", "Got it -- {v}.")),
    ("recipe", "fetch", "dish", ("carbonara", "soda bread", "lentil soup",
     "beef stew", "lemon drizzle", "fish pie"),
     ("find a recipe for {v}", "how do I make {v}", "look up {v}",
      "get me a {v} recipe"),
     ("Here's one for {v}.", "Found a {v} recipe.", "Got {v} for you.")),
    ("booking", "report", "reference", ("the Tuesday one", "the flight",
     "the table for four", "the hotel", "the return leg"),
     ("check {v}", "what's the status of {v}", "look up {v}",
      "can you check on {v}"),
     ("{v} looks fine.", "Checked -- {v}.", "That's {v}, all confirmed.")),
    ("invoice", "report", "number", ("last month's", "the March one",
     "the outstanding one", "the one from Friday"),
     ("check {v} invoice", "what's on {v} invoice", "pull up {v} invoice"),
     ("That one's settled.", "Still outstanding.", "Paid last week.")),
    ("route", "fetch", "destination", ("the station", "mum's", "the airport",
     "the garden centre", "work", "the coast"),
     ("how do I get to {v}", "find me a route to {v}", "directions to {v}",
      "what's the way to {v}"),
     ("Heading to {v} now.", "Route to {v} is up.", "Got directions to {v}.")),
    ("shopping_list", "start", "item", ("milk", "coffee", "washing up liquid",
     "bin bags", "bread", "olive oil"),
     ("add {v} to the list", "put {v} on the shopping list", "we need {v}"),
     ("Added {v}.", "{v} is on the list.", "Got it -- {v}.")),
    ("playlist", "start", "name", ("the driving one", "sunday morning",
     "the running mix", "background stuff"),
     ("start {v}", "put {v} on", "queue up {v}"),
     ("Playing {v}.", "{v} is on.", "Starting {v}.")),
    ("meeting", "start", "title", ("the standup", "a catch-up with Dan",
     "the review", "a call with the builders"),
     ("schedule {v}", "put {v} in the diary", "book {v} in"),
     ("{v} is in.", "Scheduled {v}.", "Booked {v}.")),
    ("note", "start", "body", ("the boiler is serviced in May",
     "bin day moved to Thursday", "the spare key is with Ann"),
     ("make a note that {v}", "note down that {v}", "remember that {v}"),
     ("Noted.", "Got that down.", "Saved.")),
    ("forecast", "report", "place", ("here", "the coast", "up north",
     "Manchester", "the valley"),
     ("what's the forecast for {v}", "weather {v}", "is it going to rain {v}"),
     ("Dry all day {v}.", "Rain later {v}.", "Cloudy {v}.")),
    ("battery", "report", "device", ("the car", "my headphones", "the mower",
     "the tablet"),
     ("check the battery on {v}", "how's {v} for charge",
      "what's the battery on {v}"),
     ("About half.", "Nearly full.", "Getting low.")),
    ("delivery", "report", "parcel", ("the big one", "Thursday's",
     "the one from the bike shop", "the returns label"),
     ("where's {v}", "track {v}", "any news on {v}"),
     ("Out for delivery.", "Arriving tomorrow.", "It's been dispatched.")),
    ("subscription", "stop", "service", ("the film one", "the gym",
     "the magazine", "the cloud storage"),
     ("cancel {v}", "stop {v}", "get rid of {v}"),
     ("Cancelled {v}.", "That's stopped.", "Done -- {v} is off.")),
)

# Modifiers widen the space multiplicatively and are the reason it cannot be
# memorised. They are plain adjectives that could sensibly qualify any of the
# nouns above, so a composed name reads as a name rather than as a puzzle.
MODIFIERS = (
    "kitchen", "morning", "evening", "weekly", "daily", "spare", "shared",
    "backup", "quick", "local", "primary", "office", "holiday", "weekend",
    "family", "personal", "draft", "archived", "pinned", "recent",
)

# Disjoint twins reserved for `evals/`. `check_toolspace.py` asserts the
# disjointness rather than trusting it, the same way `check_evals.py` does for
# HELD_OUT_CONTACTS and HELD_OUT_FACTS.
HELD_OUT_MODIFIERS = (
    "lakeside", "midweek", "seasonal", "overflow", "guest", "courtyard",
    "riverside", "twilight", "harvest", "meadow",
)

# **Two held-out levels, because they ask different questions.** A held-out
# *modifier* leaves a trained noun in the name, so `set_lakeside_timer` can be
# located in the declaration by its suffix and copied -- which is the easy form
# of the capability and the one the thirty-third finding predicts will work. A
# held-out *domain* shares nothing with training: the noun, the param, the
# values and the utterance frames are all new, so the only route to a correct
# call is reading the declaration as a declaration. If the first passes and the
# second fails, the model is suffix-matching rather than reading a schema, and
# the eval has to be able to tell those apart or it will report the wrong win.
HELD_OUT_DOMAINS: tuple[tuple, ...] = (
    ("ferry", "report", "crossing", ("the early one", "Sunday's sailing",
     "the last crossing", "the return"),
     ("check {v}", "what's happening with {v}", "any news on {v}"),
     ("{v} is on time.", "Delayed an hour.", "Cancelled, sorry.")),
    ("kiln", "start", "programme", ("bisque", "the slow glaze", "a test fire",
     "the overnight cycle"),
     ("start {v}", "fire {v}", "put {v} on"),
     ("{v} running.", "Started {v}.", "{v} is going.")),
    ("allotment", "report", "plot", ("the top bed", "the greenhouse",
     "the far corner", "the fruit cage"),
     ("how's {v} doing", "check {v}", "what's the state of {v}"),
     ("Needs watering.", "Doing well.", "Ready to pick.")),
    ("darkroom", "start", "process", ("a contact sheet", "the push develop",
     "a test strip", "the fibre print"),
     ("set up {v}", "start {v}", "begin {v}"),
     ("{v} started.", "Set up {v}.", "Running {v} now.")),
)


# --------------------------------------------------------- the wide vocabulary
#
# **Why there is a second vocabulary, and it is the first arm's post-mortem.**
# `nano20m_v1_toolspace` reads 230/332 at `level="train"` and **0/326 and 0/329**
# on both held-out levels, on two seeds. The failure is not that he cannot read a
# declaration: across 1,310 held-out items the emitted name appeared in the
# declaration zero times, he got the verb right 78% and the noun right 84%, and
# he substituted a *trained* modifier every time -- `find_meadow_harvest_route`
# came back as `find_morning_route`.
#
# That is a property of the corpus. The narrow pools give 38,395 distinct names
# at 17.3 uses each, which is what the design targeted, but the **tokens** they
# are built from are 24 verbs, 16 nouns and 22 modifiers at **27,000-48,000 uses
# each** -- `clarify`'s untreated 2,096 by a factor of twenty. Name diversity is
# not token diversity. The model learned sixty-two words and composed from them,
# because no name it ever saw contained a token it had to copy.
#
# So the modifier becomes an invented word, on `_invent_facts`'s argument and
# from its machinery: 22,500 prefix-free coinages, **partitioned** rather than
# drawn independently, so trained and held-out share a shape distribution and
# differ only in which strings they contain. A held-out modifier that also
# looked different would confound "unseen" with "unseen-shaped".
#
# At 18,000 trained modifiers the name space is ~1.7M against 200,000 examples,
# so nearly every declaration in the corpus names a tool the model has never
# seen. Copying the declaration stops being one strategy among several and
# becomes the only one that works -- which is the condition the first arm never
# created and the whole reason it could not answer the question.


def _coined(n_train: int = 18_000, n_held: int = 4_500,
            seed: int = 90210) -> tuple[tuple[str, ...], tuple[str, ...]]:
    import random as _random

    from .tools import CODAS, master_pool
    pool = master_pool(_random.Random(seed), CODAS)
    if len(pool) < n_train + n_held:
        raise SystemExit(f"coined pool is {len(pool)}, need {n_train + n_held}")
    lower = [w.lower() for w in pool]
    return tuple(lower[:n_train]), tuple(lower[n_train:n_train + n_held])


WIDE_MODIFIERS, WIDE_HELD_OUT_MODIFIERS = _coined()

# `narrow` is the first arm and is kept so it stays reproducible; `wide` is the
# arm that can answer the question. Nothing else differs between them -- same
# domains, same verbs, same values, same frames, same payload shape -- so the
# pair is a bracket on one axis rather than two corpora that disagree.
VOCABS = {
    "narrow": (MODIFIERS, HELD_OUT_MODIFIERS),
    "wide": (WIDE_MODIFIERS, WIDE_HELD_OUT_MODIFIERS),
}


@dataclass(frozen=True)
class Declared:
    """One tool as it appears in a declaration and in a call."""
    name: str
    param: str
    optional: str | None
    summary: str

    def render(self) -> str:
        params = self.param + (f", {self.optional}?" if self.optional else "")
        return f"{self.name}({params}) -- {self.summary}"


# An optional second parameter, present on some tools so the `?` in the
# declaration means something. It is never required and never asked for, so a
# model that copies it into every call is making a readable mistake.
OPTIONAL_PARAMS = ("note", "label", "tag", "priority")

# **The refusal, and why it is composed and 35% of the slice.** The first two
# arms read `absent` 0/71 in all twelve cells: he never declines, on either
# vocabulary, at either seed. Three things were wrong with how this slice asked
# the question, and all three are fixed here rather than argued about.
#
#   * **The refusal was one sentence at ~36,000 uses** -- `clarify`'s untreated
#     regime, in the file whose own finding is about that regime. Composed here
#     as frames x the noun that was asked for, which also means producing it
#     requires identifying what was missing rather than emitting a constant.
#   * **`absent` declared 2.51 tools on average against `route`'s 3.49**, so the
#     two classes were separable by counting the declaration. That is a leak
#     whether or not the model used it -- and it plainly did not, which is worse,
#     because it means a future positive could be the count rather than the read.
#     Both classes now declare the same number.
#   * **18% is a share at which always-calling is right 82% of the time.** 35%
#     is not a tuned number and is not claimed to be one; it is far enough from
#     the local optimum that the gradient points somewhere else.
# **Reproducibility note.** These three fixes change what `generate` emits for
# every vocabulary, so `data/raw/toolspace.txt` and `toolspace_wide.txt` as the
# first two arms saw them are regenerable only at commit `ec2b954` and its
# parent. Their results stand as measured; their corpora are pinned to git
# rather than to this file, which is why the third arm is a new filename rather
# than the same one rebuilt. `vocab` was kept switchable because it is an axis
# under study; the refusal design is not an axis, it was a bug.
ABSENT_SHARE = 0.35

REFUSAL_FRAMES = (
    "I don't have anything for {n}.", "Nothing here does {n}.",
    "I can't do {n} with what I've got.", "No {n} tool on this one.",
    "That'd need a {n} tool I haven't got.", "Can't help with {n}, sorry.",
    "I've nothing set up for {n}.", "No way to do {n} from here.",
)

# --------------------------------------------------------------------------
# WS-E stage 2 -- declining as a routing target
# --------------------------------------------------------------------------

# **The shape, and why it is this shape.** The thirty-fourth finding measured
# two things about this model: he routes to *declared* tools he was never
# trained on at parity with trained ones (206/329 against 207/213), and he
# cannot decline at all (0/276, inventing a name 190-216 times). One of those is
# his best skill and the other is a hole three arms have failed to fill. So
# declining stops being a suppression and becomes a **routing target** --
# `decline` is a member of the declared set, he routes to it, and the refusal
# comes back in the *observation* for him to relay. He never composes it. That
# is deference, the channel that works, doing the job suppression could not.
#
# The thirty-ninth finding already ruled out the cheap version: with `decline`
# declared, positioned last, and left open by the grammar as the only escape,
# untrained checkpoints took it 3 times in 442. The corpus has to teach it.
#
# **The say pool obeys the cardinality rule, and both ways of getting it wrong
# are already on the record.** One sentence at ~36,000 uses (the first
# toolspace build) failed. 128 composed refusals at 163 uses each (the
# thirty-fourth finding's own repair) failed. What *worked* is
# `temporal_sayvar`: 2,548 clarify phrasings at **4.5 uses each** took
# `refusal.clarify` to 100%. So the target is sayvar's regime, reached by
# composing from the domain's own vocabulary rather than by writing a list --
# 8 openers x 6 verbs x 16 nouns x 6 tails x 6 prefixes, which is 27,648 before
# the article rule and lands near 2 uses over a 200,000-example build.
# `scripts/check_toolspace.py` declares the measured count.
DECLINE_PREFIXES = ("", "Sorry -- ", "Ah, ", "Hmm, ", "Right, ", "Sorry, ")

# Every one of these has to read grammatically before "to {verb} {noun}".
DECLINE_OPENERS = (
    "I've got nothing", "I haven't got anything", "There's nothing here",
    "I don't have anything", "I've not got anything", "I have nothing",
    "There's nothing set up", "I've got no way",
)

DECLINE_TAILS = (
    "", ", sorry", " I'm afraid", " on this one", ", not from here",
    " with what I've got",
)


def _article(noun: str) -> str:
    """`a` or `an`, and the noun with its underscores read out.

    `shopping_list` is a declaration token; a sentence has to say "shopping
    list". The tool *name* keeps the underscore because that is what the model
    must emit inside the call -- these two are deliberately not the same string.
    """
    words = noun.replace("_", " ")
    return f"{'an' if words[0] in 'aeiou' else 'a'} {words}"


def decline_say(rng: random.Random, verb: str, noun: str) -> str:
    """The refusal the *tool* returns, for the model to read back.

    Composed from the verb and noun that were actually asked for, so producing
    it requires having identified what was missing -- which is the property the
    thirty-fourth finding's constant-sentence version lacked. The model does
    not produce it; it copies it out of the observation. That is the whole
    design: he routes, the runtime refuses, he defers.
    """
    prefix = rng.choice(DECLINE_PREFIXES)
    opener = rng.choice(DECLINE_OPENERS)
    # Two things a naive join gets wrong, and both would ship 25,000 strings of
    # bad English into a slice whose whole job is speech he reads back.
    # A prefix lowercases what follows -- "Sorry, There's nothing" is not a
    # sentence -- except where the word is `I`, which never lowercases.
    if prefix and not opener.startswith("I"):
        opener = opener[0].lower() + opener[1:]
    # And a verb is a *declaration* token: `look_up` is what goes inside the
    # call, and "look_up a route" is not what anybody says.
    return (
        f"{prefix}{opener} to {verb.replace('_', ' ')} "
        f"{_article(noun)}{rng.choice(DECLINE_TAILS)}."
    )


def decline_space() -> int:
    """Distinct refusals the composition can produce. Declared, not guessed."""
    from itertools import product

    pool, _ = LEVELS["train"]
    n = 0
    for noun, sense, *_ in pool:
        n += len(VERBS[sense])
    return n * len(DECLINE_PREFIXES) * len(DECLINE_OPENERS) * len(DECLINE_TAILS)


SUMMARY = {
    "fetch": "look up {n}", "start": "add a new {n}",
    "stop": "remove {n}", "report": "report on {n}",
}


def tool_for(rng: random.Random, domain: tuple, held_out: bool,
             vocab: str = "narrow") -> Declared:
    """One tool name, from `verb x modifier(s) x noun`.

    One modifier or two, because a single pool of twenty leaves 1,920 names and
    ~52 uses each in a slice this size -- nearer `clarify`'s untreated regime
    than `answer`'s, and a null on that dose would say only that the dose was
    small. Ordered pairs take the same twenty words to 400 combinations and the
    space to ~38,000, which lands uses-per-name at ~4 where `sayvar` demonstrated
    a corpus stops teaching recitation.
    """
    noun, sense, param = domain[0], domain[1], domain[2]
    verb = rng.choice(VERBS[sense])
    trained, held = VOCABS[vocab]
    mods = held if held_out else trained
    if rng.random() < 0.5:  # noqa: SIM108 -- the two-modifier branch is the point
        mod = rng.choice(mods)
    else:
        a, b = rng.sample(mods, 2)
        mod = f"{a}_{b}"
    name = f"{verb}_{mod}_{noun}"
    optional = rng.choice(OPTIONAL_PARAMS) if rng.random() < 0.35 else None
    return Declared(name, param, optional, SUMMARY[sense].format(n=noun))


# The three levels an example can be drawn at. `train` is the corpus; the other
# two are eval-only and differ in how much of the name is reachable from it.
LEVELS = {
    "train":    (DOMAINS, False),
    "modifier": (DOMAINS, True),
    "domain":   (HELD_OUT_DOMAINS, True),
}


def space_size(level: str = "train", vocab: str = "narrow") -> int:
    domains, held = LEVELS[level]
    trained, ho = VOCABS[vocab]
    m = len(ho if held else trained)
    combos = m + m * (m - 1)
    return sum(len(VERBS[d[1]]) * combos for d in domains)


@dataclass(frozen=True)
class Example:
    kind: str
    declared: tuple[Declared, ...]
    target: Declared | None
    utterance: str
    text: str


# What `decline` looks like in a declaration. Byte-identical to what
# `corn/agent.py`'s `declaration()` renders, so the corpus and the runtime are
# one format rather than two that agree today.
DECLINE_RENDER = f"{DECLINE}() -- say that no tool covers this request"


def _decl_line(tools: tuple[Declared, ...], decline: bool = False) -> str:
    parts = [t.render() for t in tools]
    if decline:
        parts.append(DECLINE_RENDER)  # last, always -- corn/tools.py DECLINE_LAST
    return DECL_PREFIX + DECL_SEP.join(parts)


def sample(rng: random.Random, level: str = "train",
           n_declared: tuple[int, int] = (2, 5),
           vocab: str = "narrow", decline: bool = False,
           values: str = "table",
           absent_share: float = ABSENT_SHARE) -> Example:
    """One transcript. The declared set varies per example, which is the point.

    `kind` is one of:
      route       the asked-for tool is declared; call it
      absent      it is *not* declared; say so and call nothing
    `absent` is what stops "call the only plausible tool" from being a winning
    policy, and it is the same argument `OUT_OF_SCOPE` makes in `toolgen.py`.

    **`absent_share` is an argument because it is an axis, not a constant.**
    `ABSENT_SHARE`'s own comment says 35% "is not a tuned number and is not
    claimed to be one", and the forty-second finding then measured the cost of
    leaving it untuned: offered an escape the model over-uses it, 98 and 70
    over-declines of 379 against 115 correct declines. `configs/mix_v2.py`
    pre-registered that as expected and named the repair a bracket. This
    parameter is what a bracket needs. The default is the constant, so every
    corpus built before it existed regenerates byte-identically.

    **The arms are not byte-comparable to each other, and that is inherent.**
    The draw below is one call at every share, so the *flip* does not shift the
    stream -- but `absent` changes `k` one line later, and `rng.sample(pool, k)`
    consumes k draws. Two shares therefore diverge in content after the first
    disagreement rather than differing only where the coin landed. Nothing can
    be done about that without decoupling the streams, and decoupling them would
    make each arm's corpus a different sample of the space, which is worse.
    """
    pool, held_out = LEVELS[level]
    absent = rng.random() < absent_share
    # One extra domain when the answer is a refusal, so that removing the
    # asked-for tool leaves a declaration of the same size as a `route` one.
    k = min(rng.randint(*n_declared) + (1 if absent else 0), len(pool))
    if absent and k < 2:
        absent = False
    domains = rng.sample(pool, k)
    tools = tuple(tool_for(rng, d, held_out, vocab) for d in domains)

    want = rng.randrange(k)
    domain = domains[want]
    # `table` is the six-or-so hand-written strings the domain ships with;
    # `composed` is `corn/toolvalues.py`, which takes the slice from 78 values
    # to ~10,800. Both consume exactly one draw from `rng`, so switching does
    # not shift the stream and every corpus built at `table` still regenerates
    # byte-identically. Default is `table` for that reason.
    value = (toolvalues.choose(rng, domain[0], domain[3])
             if values == "composed" else rng.choice(domain[3]))
    utterance = rng.choice(domain[4]).format(v=value)

    if absent:
        # Everything except the one being asked for. `k` was drawn one larger
        # above for this case, so the declaration is the same length as a
        # `route` declaration and the two classes cannot be told apart by
        # counting the tools in it.
        shown = tools[:want] + tools[want + 1:]
        if not decline:
            refusal = rng.choice(REFUSAL_FRAMES).format(
                n=domain[0].replace("_", " "))
            lines = [_decl_line(shown), f"{D_USER}{utterance}",
                     f"{D_SAY}{refusal}", D_END]
            return Example("absent", shown, None, utterance, "\n".join(lines))

        # WS-E stage 2. The gold is a *call* -- he routes to `decline`, the
        # runtime hands back a refusal, and he relays it. He composes nothing.
        say = decline_say(rng, rng.choice(VERBS[domain[1]]), domain[0])
        obs = {"ok": False, "reason": "not_covered", "say": say}
        lines = [
            _decl_line(shown, decline=True),
            f"{D_USER}{utterance}",
            f"{D_CALL}{json.dumps({'name': DECLINE, 'arguments': {}})}",
            f"{D_OBS}{json.dumps(obs)}",
            f"{D_SAY}{say}",
            D_END,
        ]
        return Example("absent", shown, None, utterance, "\n".join(lines))

    target = tools[want]
    args = {target.param: value}
    obs = dict(args)
    reply = rng.choice(domain[5]).format(v=value)
    lines = [
        # `decline` on **every** line, including this one, whose answer is a
        # real tool. If it appeared only where it was the answer, its presence
        # would predict its use and the arm would measure a cue rather than a
        # behaviour.
        _decl_line(tools, decline=decline),
        f"{D_USER}{utterance}",
        f"{D_CALL}{json.dumps({'name': target.name, 'arguments': args})}",
        f"{D_OBS}{json.dumps(obs)}",
        f"{D_SAY}{reply}",
        D_END,
    ]
    return Example("route", tools, target, utterance, "\n".join(lines))


def generate(n: int, seed: int = 5150, level: str = "train",
             vocab: str = "narrow", decline: bool = False,
             values: str = "table", absent_share: float = ABSENT_SHARE):
    rng = random.Random(seed)
    for _ in range(n):
        yield sample(rng, level, vocab=vocab, decline=decline, values=values,
                     absent_share=absent_share)
