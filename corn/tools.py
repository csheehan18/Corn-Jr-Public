"""Corn-Jr's tool schemas, and the transcript slice that teaches them.

DATA.md §4 gives assistant transcripts with tool calls 15% of the budget and §6
says they are the slice that "needs a larger model to generate". This is the
argument that a useful share of them does not, taken from the one slice that is
already built: `corn/temporal.py` manufactures its data programmatically, has
exact ground truth, and produced the project's most load-bearing result
(README's sixth finding). The same three properties are available here.

What generation cannot buy is phrasing variety beyond what a human wrote into
the templates, and that limit is real and is the same one §11 records against
`temporal.route`. What it does buy is the part §6 says matters most:

> §9's most important behaviour is knowing when he doesn't know, and that
> cannot be learned from a corpus where every request succeeds.

Failure is constructible. Ambiguity, missing contacts, and requests outside the
tool set are all exactly specifiable, which is precisely what an LLM-generated
corpus is *worst* at labelling reliably.

VISION §6 states four design rules for the tool layer. Three of them are
decidable here and are:

  tools are cheap to add
        a tool is a `Tool` in `REGISTRY` -- a declaration, not a code change.
        Nothing below branches on a tool's name.
  latency class is part of the contract
        every tool declares `fast` or `slow`, because §3 budgets the LLM the
        smallest slice of the latency budget and Corn-Jr has to know before he
        calls whether he owes the user an acknowledgment first.
  failures are speakable
        every error carries either `say` (what to tell the user) or `clarify`
        (what to ask). A tool never returns a bare error code, because there is
        nothing a 250M model could reliably do with one.

**The payload convention is `corn/temporal.py`'s, exactly**: a success is a
bare object with the tool's own fields, and a failure is `{"ok": false,
"reason": <slug>, ...}` carrying `clarify` or `say`. Inventing a second shape
here -- `{"error": ...}` was the first draft -- would have meant the model
learning the same concept twice, which is the objection that made the seven
markers atomic in the BPE and applies with more force to the thing those
markers wrap. `--` rather than an em dash for the same reason: `resolve_date`
already writes it that way.

The fourth, schema-constrained decoding, is a Phase 3 inference concern. What
belongs here is the schema it would constrain against, and `validate_call` is
that schema made executable -- it is what `evals/`'s `tool.validity` row scores
and what `check_tools.py` attacks with malformed calls.

**Held-out contacts and facts are this slice's decontamination.**
`corn/temporal.py` stops a year short of the eval anchors so an eval item is
structurally unreachable rather than probabilistically unlikely (§7). The
analogue is the lookup tables: `CONTACTS` and `FACTS` are what the generator
may emit, `HELD_OUT_CONTACTS` and `HELD_OUT_FACTS` are disjoint from them and
reserved for `evals/`. A transcript naming Ophelia Vance, or reading back
Kinshasa, cannot have come from the training slice.

The fact holdout does double duty. VISION §7 makes storing the world an
explicit non-goal, so a model that answers a held-out lookup correctly has
provably done it by copying the observation -- which makes this a second and
harder instance of the behaviour §4 rests on. `temporal.copy` demonstrated
deference on one tool from one generator, and §11 records "still one tool" as
the standing caveat on it.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from typing import Callable

from .markers import D_CALL, D_END, D_OBS, D_SAY, D_USER

# ---------------------------------------------------------------- schemas


@dataclass(frozen=True)
class Param:
    name: str
    required: bool = True
    # Kept deliberately coarse. A 250M model emits text; the useful distinction
    # is "free text" from "a token that has to match something", not int vs
    # float. `enum` is what makes a param checkable without a live backend.
    kind: str = "string"
    enum: tuple[str, ...] = ()


@dataclass(frozen=True)
class Tool:
    name: str
    params: tuple[Param, ...]
    latency: str  # "fast" | "slow"
    summary: str

    def required(self) -> tuple[str, ...]:
        return tuple(p.name for p in self.params if p.required)

    def allowed(self) -> tuple[str, ...]:
        return tuple(p.name for p in self.params)


REGISTRY: dict[str, Tool] = {
    t.name: t
    for t in (
        Tool(
            name="place_call",
            params=(Param("contact"),),
            latency="slow",
            summary="dial a contact",
        ),
        Tool(
            name="send_text",
            params=(Param("contact"), Param("message")),
            latency="slow",
            summary="send an SMS to a contact",
        ),
        Tool(
            name="save_note",
            params=(Param("text"), Param("title", required=False)),
            latency="fast",
            summary="write freeform text to a note",
        ),
        # VISION §6 names four tools and says a fifth "will come out of
        # development rather than planning". This is it, and it is the one the
        # confirmed use case actually needs -- "hands-free research while
        # driving: ask, he looks it up, he reads back a useful answer" is a
        # search call and a spoken result. It is also the only `slow` tool
        # whose slowness the user will notice every single time.
        Tool(
            name="web_search",
            params=(Param("query"),),
            latency="slow",
            summary="look something up and read back the answer",
        ),
        # Declared here, implemented in corn/temporal.py. The registry is the
        # single place that knows the whole tool set, which is what makes
        # `tool.selection` a question with a definite answer -- a model choosing
        # between three tools is doing something easier than choosing between
        # five, and the eval must not quietly ask the easier question.
        Tool(
            name="resolve_date",
            params=(Param("expression"),),
            latency="fast",
            summary="turn a spoken date expression into a date",
        ),
        Tool(
            name="recall_day",
            params=(Param("date"),),
            latency="fast",
            summary="look up what happened on a date",
        ),
        # **"None of these" as a routing target, not a suppression.** WS-E of
        # the "don't know" plan, and the seventh entry changes what
        # `tool.selection` asks: it is a **seven-way** choice for every corpus
        # built from here on, and a number from a six-way one is not comparable
        # with a number from this. Nothing already scored moves -- no
        # checkpoint on disk has seen the name, so none can emit it -- but the
        # question is different afterwards and this file's rule is that such a
        # change is stated rather than absorbed.
        #
        # The thirty-fourth finding is why it exists. He routes to *declared*
        # tools he was never trained on at parity with trained ones (206/329
        # against 207/213) and cannot decline at all (0/276, inventing a name
        # 190-216 times). Routing is his best skill and suppression is the one
        # thing three arms have failed to teach him, so declining becomes
        # something to route *to*, and the refusal rides back on the
        # observation where deference -- his other best skill -- can carry it.
        #
        # `params=()` is the first empty parameter list in the registry, which
        # makes `corn/grammar.py`'s `{}` branch reachable for the first time.
        # That branch's own comment said it was there "so that declaring one is
        # a declaration"; this is the declaration.
        Tool(
            name="decline",
            params=(),
            latency="fast",
            summary="say that no tool covers this request",
        ),
        # VISION §6's escalation tool, and the eighth entry does to
        # `tool.selection` exactly what `decline` did to it above: the choice
        # is **eight-way** for every corpus built from here on, and a number
        # from a seven-way question is not comparable with one from this. No
        # checkpoint on disk has seen the name, so nothing already scored
        # moves -- but the question is different afterwards and this file's
        # rule is that such a change is stated rather than absorbed.
        #
        # **Two parameters, not a mode flag, and that is the whole design.**
        # §6 settles relay-vs-compose as "verbatim always, composition only as
        # an addendum": `request` is required and carries the user's words
        # unaltered, `context` is optional and carries what Corn-Jr added
        # because the request was underspecified. A `mode: verbatim|composed`
        # flag would encode the same policy and cost the rulers -- `request`
        # is exactly checkable on every row under this shape, where under a
        # flag half the corpus would have no exact comparison left to make.
        # It also makes the dangerous failure unrepresentable rather than
        # merely detectable: there is no slot a paraphrase could displace the
        # user's own words into. That is `corn/grammar.py`'s discipline moved
        # from the syntax to the payload.
        #
        # `slow`, and it is the tool whose slowness matters most: it is the
        # only one that acts *as the user* on an agent that can write code.
        Tool(
            name="ask_agent",
            params=(Param("request"), Param("context", required=False)),
            latency="slow",
            summary="relay a request to a larger agent on the user's behalf",
        ),
    )
}

LATENCY_CLASSES = ("fast", "slow")


# ---------------------------------------------------------------- validation


def validate_call(raw: str) -> dict:
    """Is `raw` a well-formed call against the registry? Never raises.

    Returns `{"ok": bool, "why": str, "name": str | None, "arguments": dict}`.
    `why` is a stable slug rather than prose because it is a failure bucket in
    `evals/` -- "malformed JSON" and "invented an argument" are different
    problems with different fixes, and a scorecard that merges them tells you
    only that something is wrong.

    Order matters: the checks run from "is this even a call" outward, so a
    response that is nowhere near the format reports `not_json` rather than the
    first schema complaint that happens to fire.
    """
    out = {"ok": False, "why": "", "name": None, "arguments": {}}
    try:
        obj = json.loads(raw)
    except (ValueError, TypeError):
        out["why"] = "not_json"
        return out
    if not isinstance(obj, dict):
        out["why"] = "not_object"
        return out
    name = obj.get("name")
    if not isinstance(name, str) or not name:
        out["why"] = "no_name"
        return out
    out["name"] = name
    if name not in REGISTRY:
        out["why"] = "unknown_tool"
        return out
    args = obj.get("arguments")
    if not isinstance(args, dict):
        out["why"] = "no_arguments"
        return out
    out["arguments"] = args

    tool = REGISTRY[name]
    missing = [p for p in tool.required() if p not in args]
    if missing:
        out["why"] = f"missing:{','.join(sorted(missing))}"
        return out
    extra = [k for k in args if k not in tool.allowed()]
    if extra:
        # The failure mode worth naming separately. A model that invents an
        # argument has produced something that parses, names a real tool, and
        # would fail at the boundary of a real system -- which is the class of
        # bug schema-constrained decoding exists to make impossible.
        out["why"] = f"invented:{','.join(sorted(extra))}"
        return out
    for p in tool.params:
        if p.name not in args:
            continue
        v = args[p.name]
        if not isinstance(v, str):
            out["why"] = f"not_string:{p.name}"
            return out
        if p.enum and v not in p.enum:
            out["why"] = f"bad_enum:{p.name}"
            return out
        if not v.strip():
            out["why"] = f"empty:{p.name}"
            return out
    out["ok"] = True
    return out


# The name a decline call carries. One string, so the scorers, the corpus, the
# grammar and the runtime cannot drift apart on it. It landed here one commit
# before the tool did, which is what let A2's scorers be written and their
# dormancy proved against every checkpoint on disk before anything could emit
# it. See the `decline` entry above for what putting it in `REGISTRY` costs.
DECLINE = "decline"

assert DECLINE in REGISTRY, "WS-E stage 1: the name is declared, the tool is not"

# **Position is not information.** Wherever a declaration line is rendered --
# `corn/agent.py` today, `corn/toolspace.py`'s corpus in stage 2 -- `decline`
# goes last, on every line, including the ones whose answer is a real tool. If
# it appeared only where it was the answer, the arm would measure a cue; if it
# moved around, position would be one. Last and always is the cheapest rule
# that is neither.
DECLINE_LAST = True


def call_text(name: str, arguments: dict) -> str:
    """The exact on-the-wire form. One place, so a corpus and an eval agree."""
    return json.dumps({"name": name, "arguments": arguments})


# **Fields a backend and the runtime pass between themselves, which the model
# must never be shown.** The four payload shapes above are the interface the
# weights learned, and the thirty-third finding priced what a departure from
# them costs: one level of nesting took `tool.copy` from 100-120 to 0-27. A
# passage handed forward for extraction is not part of that interface and an
# extraction's own verdict is not either, so both travel under a leading
# underscore and `take_runtime` removes them at the one boundary that matters.
#
# A prefix rather than a fixed pair of names, so a backend that grows a third
# of these cannot reach the observation by being added to the wrong list.
RUNTIME_PREFIX = "_"

# The full text a provider reduced, from `harness/backends/search.py` to
# `corn/agent.py`'s `web_search` executor. Absent when reduction kept
# everything, because there is then nothing extraction could recover.
PASSAGE = "_passage"

# Whether the sentence in `answer` actually mentions what was asked about.
# False only on the deep path (`harness/backends/search.py`'s subject rule),
# where a page is served for its *passage* because its title says it is the
# subject the question named, while its lead sentence defines the subject
# rather than answering the question. `corn/agent.py` reads it to decide what
# to do when extraction then finds nothing: serving a true, on-topic
# non-answer is the thing `MIN_COVER`'s own comment refuses to do, so the
# turn takes the honest miss instead.
LEAD_ANSWERS = "_lead_answers"

# `{"ok": bool, "why": str}` -- what the reader made of that passage, from the
# executor to the turn. `ok` is whether an answer came back; `why` is
# `corn.extract.reduce`'s own reason either way, so the fallback rate and the
# agreement counts are both readable off a session log.
READING = "_reading"

# `{"provider": str, "cause": str, "detail": str}` -- which provider refused a
# `web_search` and how, from `harness/backends/search.py` to the session log.
# The spoken `say` names the provider and stops there, because a host and "try
# again shortly" is the whole of what a user can act on; the `cause` slug
# ("challenge", "rate_limit", "refused") is what a *probe* groups on, and
# splitting retrieval's misses by reason is exactly what could not be done when
# `docs/PLAN-EXTRACTION-READER.md` §4 counted the scraper refused on 13 of 24.
#
# Runtime-side for the ordinary reason, and this one is worth stating because
# the field is attached to a *refusal* rather than to a hit: the four payload
# shapes are the interface the weights learned, `{ok, reason, say}` is one of
# them, and a fifth key in it is a departure from the shape the
# thirty-third finding priced. The slug is free precisely because the shape
# does not move.
BLOCKED_BY = "_blocked_by"


def take_runtime(payload) -> tuple[dict, dict]:
    """`(what the model is shown, what only the runtime reads)`.

    Pure, and applied to every payload rather than to the ones known to carry
    a runtime field, because the invariant worth holding is about the
    observation and not about any particular backend: nothing under
    `RUNTIME_PREFIX` enters a transcript. A payload that is not a dict comes
    back untouched -- validation is `validate_call`'s job and a guard here
    would be a second opinion in the wrong file.
    """
    if not isinstance(payload, dict):
        return payload, {}
    shown = {k: v for k, v in payload.items()
             if not k.startswith(RUNTIME_PREFIX)}
    hidden = {k: v for k, v in payload.items() if k.startswith(RUNTIME_PREFIX)}
    return shown, hidden


# ---------------------------------------------------------------- contacts

# Two disjoint books. The generator may only see `CONTACTS`; `evals/` draws
# from `HELD_OUT_CONTACTS`, so a transcript naming one of the latter cannot
# have been produced by the training slice. `check_tools.py` asserts the
# disjointness holds on both first and full names -- sharing a *first* name
# across the boundary would be enough to make an ambiguity item resolvable
# from memory.
CONTACTS: tuple[str, ...] = (
    "Alice Brennan", "Alice Okafor", "Ben Traoré", "Carla Mendez",
    "Chris Patel", "Chris Whelan", "Dave Lindqvist", "Elena Rossi",
    "Farid Haddad", "Grace Kim", "Hannah Boateng", "Ivan Petrov",
    "Jules Marchand", "Kwame Osei", "Lena Fischer", "Marcus Doyle",
    "Nadia Rahman", "Omar Silva", "Priya Nair", "Quentin Aubert",
    "Rosa Delgado", "Sam Iversen", "Sam Njoroge", "Tomas Varga",
    "Uma Krishnan", "Viktor Halonen", "Wendy Achebe", "Yusuf Demir",
)

HELD_OUT_CONTACTS: tuple[str, ...] = (
    "Ophelia Vance", "Ophelia Sandoval", "Xavier Lundgren", "Zora Aldridge",
    "Ignatius Mbeki", "Perpetua Cavendish", "Thaddeus Okonkwo",
    "Seraphina Volkov", "Barnaby Fitzwilliam", "Cordelia Nwosu",
)

# The same holdout, for the fifth tool. `web_search` is the one place a corpus
# could accidentally teach Corn-Jr *facts*, which VISION §7 lists as an
# explicit non-goal -- he is not trying to store the world, he is trying to
# look things up in it. So the eval draws from `HELD_OUT_FACTS`, and a model
# that reads back Kinshasa correctly has demonstrably done it by copying the
# observation rather than by knowing it. That makes this row a second, harder
# instance of the behaviour §4 rests on: `temporal.copy` proved deference on
# one tool built by one generator, and §11 records "still one tool" as the
# standing caveat. Facts are a stronger test than dates, because a model has a
# prior over years and has none over which river runs through Vientiane.
# Noun phrases, not questions. The utterance templates wrap these -- "what's
# {q}", "look up {q}", "google {q}" -- and a question-shaped entry produces
# "tell me who wrote hamlet", which reads like nothing anybody says. Keeping
# every entry a noun phrase is what lets one set of templates cover all of
# them, which is where the surface variety comes from.
# --------------------------------------------------------------------------
# The search index is invented, and that is the whole point -- DATA.md §11
# --------------------------------------------------------------------------
#
# This was a hand-written table of 28 real facts, and README's twelfth finding
# is what it cost. `web_search`'s answer was a deterministic function of its
# query over 28 possibilities, and `data/raw/tools.txt` drew 3,000 search
# transcripts from it -- **107 examples per fact, 2,679 in the upsampled arm.**
# A model could score 100% on the training distribution without ever reading
# `<|obs|>`, so nothing in the corpus ever required it to. Measured: the same
# checkpoints that read `temporal.copy` 353/353 read `tool.copy` 0/120 and
# 27/120, and the upsampled arm answered held-out lookups by reciting this
# table -- `William Shakespeare` when the tool had said `Alexander Fleming`.
#
# `resolve_date` never had that problem, and not by luck: its answer depends on
# the `<|day|>` anchor as well as the utterance, anchors span 2020-2027, and so
# "last Tuesday" has no fixed answer. **The observation is the only place the
# date can come from.** That is the property this table lacked and now has.
#
# **The fix is to invent the world rather than to enlarge it.** Two options
# were on the table (§11): write more real facts, or generate them. Writing
# more is bounded by how many anyone will write, and every one added is a fact
# a *larger* model could later learn and then answer from -- which is the
# failure VISION §7 names as a non-goal and §5.2 forbids. Inventing them ends
# the question instead: there is nothing true here to learn, so reading the
# observation is not the cheapest way to be right, it is the only way.
#
# The families below mirror the six shapes in `HELD_OUT_FACTS` exactly -- a
# capital, a river, a wingspan, a lake depth, a discoverer, a melting point --
# so an eval query is in-distribution in *form* and out-of-distribution in
# *content*. That is the same decontamination shape §7 uses for anchor years:
# held-out answers, in-distribution phrasings.

_FACT_SEED = 20260812

# How much of the master name pool the *training* index consumes, in the order
# it consumes it: places, cities, rivers, creatures, elements, firsts,
# languages. Named rather than inlined because `_invent_held_out_facts` skips
# exactly this much before taking its own pools, which is what makes the two
# worlds disjoint by construction rather than by luck. Change one and the other
# follows; `check_tools.py` asserts the disjointness either way.
_TRAIN_TAKES = (1600, 1600, 900, 900, 1200, 500, 500)
_TRAIN_SURNAMES = 500

_ONSETS = (
    "Bel", "Cor", "Dan", "Elm", "Fen", "Gar", "Hal", "Ith", "Jor", "Kel",
    "Lan", "Mor", "Nyr", "Orl", "Pel", "Quen", "Rav", "Sel", "Tor", "Ulv",
    "Var", "Wen", "Yar", "Zel", "Bry", "Cad", "Dro", "Esk", "Fyr", "Gled",
)
_VOWELS = ("a", "e", "i", "o", "u", "ae", "en", "ir", "or", "un")
_MIDS = ("", "th", "nd", "sk", "lv")
CODAS = (
    "dia", "nia", "ria", "tha", "dor", "mar", "vik", "stad", "gard", "holm",
    "burg", "fell", "mere", "wold", "scar",
)
SURNAME_CODAS = ("son", "ley", "worth", "ridge", "combe", "stone", "field", "bourne")
_UNITS = ("crown", "mark", "florin", "shilling", "thaler", "denar", "guilder")

# What `ask_agent` calls the thing it relays to when nothing else is supplied.
# A role rather than a vendor: see `ask_agent_tool`, and `AGENT_NAMES` in
# `corn/toolgen.py` for the pool the corpus actually varies over.
DEFAULT_AGENT = "the agent"

# --------------------------------------------------------------------------
# Answers that are neither a name nor a number -- the fifty-seventh finding
# --------------------------------------------------------------------------
#
# The extraction pilot's probe found the arm declining on 92% of the
# answerable windows whose gold is an `other` -- no digit, no leading capital,
# a lowercase common noun or phrase -- against about half of names and
# numbers, identically across both seeds and flat in gold position. It is a
# prior over the *lexical type* of an answer, and it is not the extraction
# slice's fault: that slice is 20.6% `other`, while the table below it joined
# was **89.7% name-or-number**. The rule "an answer is a capitalised thing or
# a number" was available to learn long before the slice existed, and 20.6%
# did not overturn it.
#
# So the fix belongs here, in the prior, rather than in the slice that failed
# to overcome it. Oversampling `other` in the extraction slice was the other
# option and is the twenty-third finding's shape -- fitting the slice to an
# observed failure. Widening the corpus-wide type distribution is the same
# move `toolvalues.py` already made for parameter values.
#
# **Composed, not written, for `_invent_facts`'s own reason.** Each pool below
# is small; the answers are products of two or three of them, which is what
# keeps the value space past `check_copyable.py`'s floor of 1,000 at about one
# exposure each. A hand-written list of fifty dishes would be the twelfth
# finding a fourth time.
#
# Every entry is still unreachable from its query: the places and creatures
# are invented, so there is nothing true about a Belarian national dish for a
# larger model to know and answer from instead of reading the observation.
_CLIMATES = (
    "mild", "wet", "windswept", "temperate", "arid", "humid", "foggy", "frostbound",
    "blustery", "overcast", "sunlit", "snowbound", "muggy", "breezy", "parched",
    "storm-worn", "drizzly", "clement", "raw", "balmy", "sleety", "thundery",
    "hazy", "crisp", "sodden", "sultry", "gusty", "bitter", "dry", "squally",
    "close", "changeable",
)
_DISH_PREP = (
    "smoked", "salted", "pickled", "braised", "honeyed", "spiced", "charred",
    "soured", "buttered", "stewed", "cured", "peppered", "sweetened", "roasted",
)
_DISH_INGREDIENT = (
    "mutton", "barley", "cabbage", "herring", "goat", "turnip", "lentil",
    "chestnut", "cod", "rye", "pumpkin", "duck", "millet", "hare", "leek", "curd",
)
_DISH_FORM = ("stew", "broth", "dumpling", "pie", "porridge", "loaf", "hash", "pudding")
_EXPORT_PREP = (
    "raw", "milled", "dried", "woven", "cut", "salted", "rolled", "pressed",
    "carved", "spun", "smelted", "tanned", "bottled", "ground", "planed",
    "quarried", "combed", "kilned",
)
_EXPORT_MATERIAL = (
    "copper", "flax", "timber", "wool", "slate", "amber", "tin", "resin",
    "hemp", "granite", "lead", "cork", "jute", "peat", "silver ore", "clay",
    "sailcloth", "whalebone", "rye flour", "sea salt", "goat hide", "birch tar",
    "iron ingots", "linen", "beeswax", "cane sugar", "pine pitch", "mica",
    "zinc", "glass beads", "dyewood", "ivory nut", "gypsum", "sandstone",
    "cotton batting", "horn buttons", "walrus hide", "reed matting", "bark cloth",
    "soapstone", "coal", "marble", "felt", "hop cones",
)
_FORAGE = (
    "shellfish", "kelp", "carrion", "seed husks", "river insects", "windfall fruit",
    "grubs", "tubers", "small lizards", "nectar", "pine nuts", "crayfish",
    "beetle larvae", "moss", "frogspawn", "sand fleas", "rotting wood", "termites",
    "berries", "snails", "fish roe", "dung beetles", "young shoots", "eelgrass",
    "mussels", "wild oats", "tree sap", "ant eggs", "bark", "cuttlefish",
)
_PLUMAGE = (
    "slate-grey", "russet", "buff", "sooty black", "chestnut", "dun", "olive",
    "ash-white", "tawny", "steel-blue", "cream", "umber", "pewter", "ochre",
    "mottled brown", "pale straw", "rust-red", "charcoal", "sandy fawn",
    "bottle-green", "smoke-grey", "clay-pink", "bronze", "ink-blue", "drab",
    "silvered",
)


def _prefix_free(names: list[str]) -> list[str]:
    """Drop any name that another name is a prefix of.

    `web_search_tool` matches a query against a pattern with `p in q or q in p`,
    so two patterns collide whenever one entity prefixes another -- "the capital
    of Bela" is a substring of "the capital of Belaria", and the tool would then
    answer whichever came first in the table rather than what was asked. Sorting
    puts any prefix immediately before the names it prefixes, so one pass over
    the sorted list is enough. `check_tools.py` asserts the result rather than
    trusting this.
    """
    kept: list[str] = []
    for name in sorted(names):
        if kept and name.startswith(kept[-1]):
            continue
        kept.append(name)
    return kept


def master_pool(rng: random.Random, codas: tuple[str, ...]) -> list[str]:
    made = [o + v + m + c
            for o in _ONSETS for v in _VOWELS for m in _MIDS for c in codas]
    made = _prefix_free(made)
    rng.shuffle(made)
    return made


def _invent_facts(seed: int = _FACT_SEED) -> tuple[tuple[str, str, str], ...]:
    """Build the search index: many facts, each seen about once.

    Sized against the corpus that reads it. `gen_tools.py` emits ~3,000 search
    transcripts, so a universe in the thousands puts exposures per fact near 1
    where the hand-written table put them at 107 -- and near 30 rather than
    2,679 when a mix upsamples the slice 25 times.
    """
    rng = random.Random(seed)

    # **Disjoint pools, carved from one prefix-free master list.** Drawing each
    # pool independently from the same name space put the same string in two of
    # them, and the first version of this produced `the capital of Belaburg ->
    # Belaburg` -- an answer recoverable from the query, which is the exact
    # property this table exists to remove. Partitioning makes that
    # unconstructible rather than unlikely.
    master = master_pool(rng, CODAS)
    surname_pool = master_pool(rng, SURNAME_CODAS)

    def take(n: int) -> list[str]:
        chunk, master[:n] = master[:n], []
        del master[:0]
        return chunk

    places, cities, rivers, creatures, elements, firsts, languages = [
        take(n) for n in _TRAIN_TAKES
    ]
    surnames = surname_pool[:_TRAIN_SURNAMES]

    out: list[tuple[str, str, str]] = []

    def add(pattern: str, answer: str, source: str) -> None:
        out.append((pattern, answer, source))

    # The six shapes `HELD_OUT_FACTS` uses, first -- these are the ones the
    # eval actually asks, and an eval query whose *form* never appeared in
    # training would measure phrasing generalisation instead of copying.
    for i, p in enumerate(places[:1200]):
        add(f"the capital of {p}", cities[i], "worldatlas.com")
    for i, p in enumerate(places[1200:1600]):
        add(f"the river that runs through {p}", f"the {rivers[i]}", "britannica.com")
    for c in creatures:
        add(f"the wingspan of the {c}",
            f"up to {rng.randint(10, 390) / 100:.2f} metres", "audubon.org")
    for p in places[:900]:
        add(f"the depth of Lake {p}",
            f"{rng.randint(120, 1990):,} metres at its deepest", "unesco.org")
    for i, e in enumerate(elements[:700]):
        add(f"the discoverer of {e}",
            f"{firsts[i % len(firsts)]} {surnames[(i * 7) % len(surnames)]}",
            "nobelprize.org")
    for e in elements[700:]:
        add(f"the melting point of {e}",
            f"{rng.randint(230, 3800):,} degrees Celsius", "rsc.org")

    # More shapes, for surface variety in the utterances that wrap them. The
    # eval never asks these; they exist so the slice is not six sentences.
    # Every answer draws from a pool the query does not name.
    for p in places[:1100]:
        add(f"the population of {p}", f"about {rng.randint(12, 940) * 1000:,}",
            "worldbank.org")
    for i, p in enumerate(places[:500]):
        add(f"the currency of {p}",
            f"the {cities[(i * 3) % len(cities)]} {rng.choice(_UNITS)}", "xe.com")
    for i, p in enumerate(places[:500]):
        add(f"the official language of {p}", languages[i % len(languages)],
            "worldatlas.com")
    for r in rivers[:700]:
        add(f"the length of the {r}",
            f"about {rng.randint(210, 6400):,} kilometres", "britannica.com")
    for p in places[:700]:
        add(f"the year {p} was founded", f"{rng.randint(1100, 1890)}",
            "britannica.com")
    for c in creatures[:600]:
        add(f"the lifespan of the {c}", f"about {rng.randint(2, 90)} years",
            "audubon.org")

    # Five `other`-typed shapes, appended **after** every draw above so that
    # the 8,697 facts this generator produced before they existed come out
    # byte-identical -- `rng` is one stream and inserting a draw earlier would
    # silently rewrite every answer downstream of it. The eval never asks
    # these; like the block above they widen what an answer is allowed to look
    # like. `check_tools.py` group 11 asserts the type mix this produces.
    def distinct(pool: tuple[str, ...], joiner: str, n: int) -> list[str]:
        """`n` distinct ordered pairs from one pool, drawn without replacement."""
        both = [f"{a}{joiner}{b}" for a in pool for b in pool if a != b]
        return rng.sample(both, n)

    for p, answer in zip(places[:700], distinct(_CLIMATES, " and ", 700)):
        add(f"the climate of {p}", answer, "worldatlas.com")
    dishes = rng.sample(
        [f"{a} {b} {c}" for a in _DISH_PREP for b in _DISH_INGREDIENT
         for c in _DISH_FORM], 700)
    for p, answer in zip(places[:700], dishes):
        add(f"the national dish of {p}", answer, "britannica.com")
    exports = rng.sample(
        [f"{a} {b}" for a in _EXPORT_PREP for b in _EXPORT_MATERIAL], 700)
    for p, answer in zip(places[700:1400], exports):
        add(f"the chief export of {p}", answer, "worldbank.org")
    for c, answer in zip(creatures[:500], distinct(_FORAGE, " and ", 500)):
        add(f"the diet of the {c}", f"mostly {answer}", "audubon.org")
    for c, answer in zip(creatures[500:900],
                         distinct(_PLUMAGE, " with ", 400)):
        add(f"the plumage of the {c}", f"{answer} markings", "audubon.org")

    # Two collision filters, and the second is the one that matters most.
    #
    # **Patterns:** anything a held-out *query* would reach under the tool's own
    # `p in q or q in p` rule is dropped rather than merely unlikely -- the
    # eval's power depends on a held-out lookup missing this table completely.
    #
    # **Answers:** a generated answer must not collide with a held-out one. The
    # ranges here make that reachable rather than hypothetical -- lake depths
    # draw from [120, 1990] and `HELD_OUT_FACTS` says Baikal is "1,642 metres at
    # its deepest", which this generator produced on its first run. A model
    # could then learn that exact string from training and *pass* the Baikal
    # item without reading the observation, which is a false positive on the one
    # row built to detect exactly that. Word-bounded in both directions, because
    # that is the test `score_tool_copy` applies and `check_evals.py` group 12
    # asserts.
    held_patterns = [p.lower() for p, _, _ in HELD_OUT_FACTS]
    held_answers = [a.lower() for _, a, _ in HELD_OUT_FACTS]

    def collides(fact: tuple[str, str, str]) -> bool:
        pattern, answer = fact[0].lower(), fact[1].lower()
        if any(pattern in h or h in pattern for h in held_patterns):
            return True
        return any(
            answer == h
            or re.search(rf"\b{re.escape(answer)}\b", h)
            or re.search(rf"\b{re.escape(h)}\b", answer)
            for h in held_answers
        )

    return tuple(f for f in out if not collides(f))

HELD_OUT_FACTS: tuple[tuple[str, str, str], ...] = (
    ("the capital of the Democratic Republic of the Congo", "Kinshasa", "worldatlas.com"),
    ("the river that runs through Vientiane", "the Mekong", "britannica.com"),
    ("the wingspan of an albatross", "up to 3.5 metres", "audubon.org"),
    ("the depth of Lake Baikal", "1,642 metres at its deepest", "unesco.org"),
    ("the discoverer of penicillin", "Alexander Fleming", "nobelprize.org"),
    ("the melting point of tungsten", "3,422 degrees Celsius", "rsc.org"),
)

# Built after the holdout, because it filters against it. The eval table stays
# hand-written and *real*: six facts nobody trains on, whose answers a model
# has no way to reach except by reading the observation it was handed.
FACTS: tuple[tuple[str, str, str], ...] = _invent_facts()


def _invent_held_out_facts(per_shape: int = 100) -> tuple[tuple[str, str, str], ...]:
    """A held-out search index wide enough to measure with -- DATA.md §11.

    **`HELD_OUT_FACTS` has six entries, and `evals/tool_copy.jsonl` is 120 items
    over those six answers at ~20 phrasings each.** So the row's effective
    sample size is 6 and its resolution is one fact -- about 20 items, or 17
    points. Every movement the project has read off it is a whole number of
    facts: the seed replicate's 18-item fall was `Alexander Fleming` garbling to
    `Flemingbel` across 17 of its 20 phrasings, one fact and nothing else.

    That is §11's own rule -- *any span the model is meant to copy must come
    from a space too large to learn as a set* -- applied to the eval instead of
    the corpus. `check_copyable.py` enforces it over `data/raw/*.txt` because it
    cost three findings there. Nothing enforced it here, and the row built to
    test the rule was the smallest set in the project.

    **Invented, not hand-written, for the reason `_invent_facts` gives.** The
    argument against writing more real facts is unchanged and applies with more
    force to a holdout: every real fact added is one a larger model could
    already know, and a model that answers `Kinshasa` from its weights scores
    the same as one that read the observation. With an invented world there is
    nothing true to learn, so copying is the only way to be right -- which is
    what makes a *pass* on this row mean something rather than a fail.

    **The name pools are disjoint by construction; the numeric ones are not,
    and finding out why is worth more than the fix.** Places, cities, rivers,
    creatures, elements and surnames are the master list past `_TRAIN_TAKES`,
    so none of them was ever available to `_invent_facts` -- those three shapes
    collide zero times and the filter never fires on them.

    The two integer shapes were *designed* the same way and it does not work.
    Depths draw from 2,010-4,990 against training's 120-1,990 and melting
    points from 3,810-5,900 against 230-3,800, so the numbers cannot coincide
    -- but the strings still do, because `\\b` sits between the thousands comma
    and the digit after it:

        held out   '2,566 metres at its deepest'
        training     '566 metres at its deepest'   <- matches, word-bounded

    Every comma-formatted four-digit answer contains a three-digit one. 30 of
    100 depths and 10 of 100 melting points are dropped for this, and none of
    the three name-pool shapes loses anything. **This is the twelfth finding's
    bug a third time** -- a substring test finding a short numeric answer inside
    a longer one, which there cost a `trained_answer` count and here would have
    put a training answer in the eval. Wingspans avoid it only by accident of
    format: three decimals against training's two puts a digit where the
    boundary would have to be (`up to 1.89` inside `up to 1.896` has no `\\b`
    after the 9), and they collide zero times.

    So the filter below is the mechanism and not a guard, on two of six shapes.
    `check_tools.py` asserts the result independently rather than trusting it.

    The filter runs one way only: candidates are dropped against the frozen
    `FACTS`, and `FACTS` is never re-filtered against these. That is what keeps
    the training corpus and `score_tool_copy`'s `trained_answer` test valid for
    every checkpoint already scored -- widening the eval must not silently
    redefine what a training answer is.
    """
    rng = random.Random(_FACT_SEED)

    # Same seed and the same two calls in the same order, so `master` and
    # `surname_pool` are the identical lists `_invent_facts` built. Skipping
    # what it consumed is then a partition of one pool rather than two draws
    # that happen not to have collided.
    master = master_pool(rng, CODAS)
    surname_pool = master_pool(rng, SURNAME_CODAS)
    del master[: sum(_TRAIN_TAKES)]
    del surname_pool[:_TRAIN_SURNAMES]

    def take(n: int) -> list[str]:
        chunk, master[:n] = master[:n], []
        return chunk

    places = take(per_shape * 3)
    cities = take(per_shape)
    rivers = take(per_shape)
    creatures = take(per_shape)
    elements = take(per_shape * 2)
    firsts = take(per_shape)
    surnames = surname_pool[:per_shape]

    out: list[tuple[str, str, str]] = []
    for i in range(per_shape):
        out.append((f"the capital of {places[i]}", cities[i], "worldatlas.com"))
        out.append((f"the river that runs through {places[per_shape + i]}",
                    f"the {rivers[i]}", "britannica.com"))
        out.append((f"the wingspan of the {creatures[i]}",
                    f"up to {rng.randint(1000, 3900) / 1000:.3f} metres", "audubon.org"))
        out.append((f"the depth of Lake {places[per_shape * 2 + i]}",
                    f"{rng.randint(2010, 4990):,} metres at its deepest", "unesco.org"))
        out.append((f"the discoverer of {elements[i]}",
                    f"{firsts[i]} {surnames[i]}", "nobelprize.org"))
        out.append((f"the melting point of {elements[per_shape + i]}",
                    f"{rng.randint(3810, 5900):,} degrees Celsius", "rsc.org"))

    # Guard, not mechanism. Patterns use the tool's own `p in q or q in p` rule;
    # answers are word-bounded in both directions, which is the test
    # `score_tool_copy` applies. The six original held-out facts are excluded
    # too, so the wide row and the frozen one are independent measurements.
    train_patterns = [p.lower() for p, _, _ in FACTS]
    train_answers = [a.lower() for _, a, _ in FACTS]
    old_patterns = [p.lower() for p, _, _ in HELD_OUT_FACTS]
    old_answers = [a.lower() for _, a, _ in HELD_OUT_FACTS]

    # **Compiled once, outside the loop, and this is a speed fix with a
    # correctness argument attached.** The predicate below is unchanged --
    # same strings, same word boundaries, same order of evaluation -- but the
    # inner generator ran `re.search(pattern_built_here, ...)` 5,004,876 times
    # (600 candidates x 8,697 train answers x 2 directions). `re`'s internal
    # cache holds 512 patterns against 8,697 distinct ones, so it thrashed and
    # recompiled almost every call: **87 seconds at import**, paid by
    # `corn/agent.py`, `corn/evals.py`, `corn/chat.py` and all fourteen guard
    # scripts before any of them printed a character.
    #
    # `scripts/check_tools.py` asserts the output is byte-identical to the
    # values this file produced before the change, so the argument is checked
    # rather than reasoned.
    all_patterns = train_patterns + old_patterns
    all_answers = train_answers + old_answers
    answer_res = [re.compile(rf"\b{re.escape(h)}\b") for h in all_answers]

    def collides(fact: tuple[str, str, str]) -> bool:
        pattern, answer = fact[0].lower(), fact[1].lower()
        if any(pattern in h or h in pattern for h in all_patterns):
            return True
        # One pattern per candidate rather than per pair; the other direction
        # is the precompiled list above.
        answer_re = re.compile(rf"\b{re.escape(answer)}\b")
        return any(
            answer == h or answer_re.search(h) or h_re.search(answer)
            for h, h_re in zip(all_answers, answer_res)
        )

    return tuple(f for f in out if not collides(f))


# The wide holdout. `HELD_OUT_FACTS` stays exactly as it is -- `tool_copy.jsonl`
# is frozen and fourteen scorecards are comparable only while it does not move.
# **Built on first use rather than at import, 2026-09-03.** The filter above is
# 3.22 seconds for 560 entries -- 600 candidates against 8,703 answers in two
# directions -- and it ran in the module body, so every importer paid it whether
# or not it read the table. Twenty-seven of the forty-six guards a bare checkout
# can run import `corn.tools`; **two of them touch this table**, and the other
# twenty-five were paying about eighty seconds of the CI sweep for a value they
# never look at. That is the eighty-seven-second note above one layer out: that
# change made the filter cheaper, this one stops charging it to importers who
# do not want it. Measured: `import corn.tools` 3,747 -> 525 ms, `corn.agent`
# 5,550 -> 2,309 ms.
#
# `__getattr__` is PEP 562 and fires only when normal attribute lookup fails, so
# `from corn.tools import HELD_OUT_FACTS_WIDE` still works and still returns the
# identical tuple. **`check_tools.py` pins it by sha256 over 560 entries and is
# the test that this changed nothing** -- the builder seeds its own
# `random.Random(_FACT_SEED)`, so when it runs cannot move what it returns.
# First read memoises into the module's globals, so every later lookup is an
# ordinary attribute and never reaches here.
#
# Nothing inside this module may refer to `HELD_OUT_FACTS_WIDE` as a bare name:
# module `__getattr__` catches attribute access on the module object, not global
# lookup from within it. Today nothing does.
_WIDE_CACHE: tuple[tuple[str, str, str], ...] | None = None


def __getattr__(name: str) -> object:
    if name == "HELD_OUT_FACTS_WIDE":
        global _WIDE_CACHE
        if _WIDE_CACHE is None:
            _WIDE_CACHE = _invent_held_out_facts()
        globals()[name] = _WIDE_CACHE
        return _WIDE_CACHE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# Queries a search cannot usefully answer without knowing more. The tool asks;
# the model copies the question. Same division of labour as `resolve_date`'s
# refusals, and the same reason: the ambiguity is decidable in code.
VAGUE_QUERIES: tuple[tuple[str, str], ...] = (
    ("the weather", "Whereabouts do you want the weather for?"),
    ("the score", "Which match are you after?"),
    ("the opening hours", "Opening hours for which place?"),
    ("the price", "The price of what, sorry?"),
    ("the directions", "Where are you trying to get to?"),
    ("the timetable", "Which timetable do you mean?"),
    ("the reviews", "Reviews for what?"),
    ("the address", "Whose address, or which place?"),
    ("the phone number", "Phone number for what?"),
    ("the recipe", "Recipe for what?"),
    ("the results", "Results for which thing?"),
    ("the forecast", "Forecast for where?"),
    ("the menu", "Menu for which place?"),
    ("the news", "Any particular subject?"),
    ("the schedule", "Schedule for what?"),
    ("the tickets", "Tickets for what?"),
    ("the population", "Population of where?"),
    ("the capital", "Capital of which country?"),
    ("the translation", "Translation of what, and into what?"),
    ("the definition", "Definition of which word?"),
    ("the distance", "Distance between where and where?"),
    ("the time", "Time in which place?"),
)

# Held out for `evals/`, like the contacts and facts above. Without this an
# eval item on "the weather" would be scored against a clarify the model read
# thousands of times in training, which measures recall rather than the
# copying the row exists to test.
HELD_OUT_VAGUE: tuple[tuple[str, str], ...] = (
    ("the fixtures", "Fixtures for which team?"),
    ("the dosage", "Dosage of what?"),
    ("the deadline", "Deadline for what?"),
    ("the pronunciation", "Pronunciation of which word?"),
    ("the altitude", "Altitude of where?"),
)


def first_names(book: tuple[str, ...]) -> dict[str, list[str]]:
    """First name -> the full names sharing it. Ambiguity is built from this."""
    out: dict[str, list[str]] = {}
    for full in book:
        out.setdefault(full.split()[0], []).append(full)
    return out


# ---------------------------------------------------------------- the tools


def place_call_tool(contact: str, book: tuple[str, ...] = CONTACTS) -> dict:
    """Dial a contact, or say why not.

    The four outcomes are the point of the slice. An exact match dials. A first
    name shared by two people returns the question to ask -- and the *tool*
    composes it, not the model, for the same reason `resolve_date` does (§6):
    ambiguity handling belongs in code, where it is exact, rather than in 250M
    parameters, where it would be a guess with a confident voice. A name the
    book lacks is refused by name. An empty book is refused without one; see
    `_lookup`.
    """
    return _lookup(contact, book, lambda full: {"status": "dialing", "contact": full})


def send_text_tool(
    contact: str, message: str, book: tuple[str, ...] = CONTACTS
) -> dict:
    """Text a contact -- after shedding the message the contact slot ate.

    `harness/backends/contacts.py` (removed 2026-10-13) named the failure and the two ways out it
    declined to take; `shed_overrun` is the third way, taken at the seam where
    the evidence lives. Only this tool gets it, because only this tool *has*
    the evidence -- see the function for the gate.
    """
    return _lookup(
        shed_overrun(contact, message, book),
        book,
        lambda full: {"status": "sent", "contact": full, "message": message},
        action="text",
    )


# ------------------------------------------------- the owner-only runtime
#
# **He calls and texts only the owner** (owner, 2026-09-08; the dialler
# removed from every runtime, the shipped one included, 2026-10-13 --
# PLAN-PEOPLE §7). `place_call_tool` and `send_text_tool` above stay: they are
# the *training world*, the 53-name book every v4 slice and frozen eval was
# generated from, and `check_tools.py` pins those tables byte for byte. What a
# running instance executes is below.
#
# The `contact` argument stays an *input*, because the shipped weights still
# write one: it is read for one decision -- does it name the owner -- and
# never resolved against anything. A request for anyone else is the trained
# 1.0 boundary (`corn/ownergen.py`, C7): a refusal with an offer to text the
# owner a reminder, in the corpus's own words, which a checkpoint relays the
# way it relays every refusal's `say`.

# The refusal with the offer (owner, 2026-10-08). `{c}` is the name as the
# person said it. They/them for the person asked about: nothing in the
# request says otherwise. Shared with `corn/ownergen.py`, which trains them.
OWNER_ONLY_CALL = (
    "I can only call you, not {c} -- want me to text you a reminder to call them?",
    "I can't call {c} -- I can only reach you. Shall I text you a reminder to ring them?",
    "Only you, I'm afraid -- I can't call {c}. Want a text reminder to call them yourself?",
)
OWNER_ONLY_TEXT = (
    "I can only text you, not {c} -- want me to text you a reminder to tell them?",
    "I can't message {c} -- only you. Shall I text you a reminder to let them know?",
    "Only you, I'm afraid -- I can't text {c}. Want me to text you a reminder?",
)
OWNER_ONLY_REASON = "owner_only"

# Words that name the owner from the owner's own mouth. "call me" arrives as
# `{"contact": "me"}` from a checkpoint that always writes the slot; an empty
# slot is the 1.0 signature, `place_call()`.
#
# "user" is measured, not guessed: live on the shipped checkpoint on
# 2026-10-13, "call me" wrote `{"contact": "User"}` -- the transcript's own name
# for the person speaking, which is the owner.
_OWNER_WORDS = frozenset({"", "me", "myself", "my phone", "my mobile", "my cell",
                          "my number", "my own phone", "me back", "user", "the user"})

# Words that end a name when the slot has run on and the message slot is no
# evidence (live 2026-10-13: "text Sam I'm running late" arrived as
# `{"contact": "Sam I'm running late"}` beside a junk message). None of them
# is part of anybody's name; the cut is only ever for the refusal's wording.
_NAME_ENDS = frozenset({"i", "i'm", "im", "i'll", "i've", "i'd", "that", "saying",
                        "say", "to", "about", "we", "we're", "it", "it's", "the",
                        "and", "please", "now"})


def names_owner(contact: str | None, owner: str = "") -> bool:
    """Whether a `contact` slot means the owner: a self-reference, or their name.

    The name is `packs/about-me.md`'s `name:` (`Persona.user_name`), whole or
    by first name -- what a person would say to be rung themselves. Nothing
    else counts, and in particular nothing is *resolved*: a name that is not
    the owner's is someone else, whoever they are.
    """
    said = " ".join(_flat_words(contact or ""))
    if said in _OWNER_WORDS:
        return True
    name = " ".join(_flat_words(owner))
    return bool(name) and said in (name, name.split()[0])


def _who_was_asked(contact: str, message: str = "") -> str:
    """The third party as said, with any message the slot swallowed shed.

    `shed_overrun`'s evidence rule without a book: the tail is dropped only
    when it is the message's own opening (one connector allowed), so "Sam
    I'm running late" names Sam -- the known-broken row's slot (NOW §4) now
    costs nothing but a cleaner refusal. "my mum" is said back as "your mum".
    """
    words = contact.split()
    msg = _flat_words(message)
    for k in range(1, len(words)):
        tail = words[k:]
        if tail[0].lower() in _OVERRUN_CONNECTORS:
            tail = tail[1:]
        shed = _flat_words(" ".join(tail))
        if shed and msg[: len(shed)] == shed:
            words = words[:k]
            break
    # No message evidence: stop at the first word that cannot be a name's.
    for k in range(1, len(words)):
        if words[k].lower().strip(".,!?") in _NAME_ENDS:
            words = words[:k]
            break
    who = " ".join(words).strip() or "them"
    return "your " + who[3:] if who.lower().startswith("my ") else who


def owner_call_tool(contact: str | None, owner: str = "",
                    rng: random.Random | None = None) -> dict:
    """Ring the owner's phone, or refuse anyone else with the offer.

    The success payload keeps a `contact` of "you" for the shipped weights,
    which compose "Calling {c}." from it (`toolgen.SAY_DIALING`); the 1.0
    corpus's `{"status": "dialing"}` is the same payload without it.
    """
    if names_owner(contact, owner):
        return {"status": "dialing", "contact": "you"}
    say = (rng or random).choice(OWNER_ONLY_CALL).format(c=_who_was_asked(contact or ""))
    return {"ok": False, "reason": OWNER_ONLY_REASON, "say": say}


def owner_text_tool(contact: str | None, message: str, owner: str = "",
                    rng: random.Random | None = None) -> dict:
    """Text the owner's phone, or refuse anyone else with the offer."""
    if names_owner(contact, owner):
        return {"status": "sent", "contact": "you", "message": message}
    say = (rng or random).choice(OWNER_ONLY_TEXT).format(
        c=_who_was_asked(contact or "", message))
    return {"ok": False, "reason": OWNER_ONLY_REASON, "say": say}


def save_note_tool(text: str, title: str | None = None) -> dict:
    """No lookup, so no ambiguity and no not-found. Deliberately the easy one.

    A slice where every tool can fail teaches that calling is risky; a slice
    where none can teaches that it never is. Both are wrong, so one of the
    three has no failure mode at all.
    """
    note = {"status": "saved", "chars": len(text)}
    if title:
        note["title"] = title
    return note


def ask_agent_tool(request: str, context: str | None = None,
                   agent: str = DEFAULT_AGENT) -> dict:
    """Hand a request to a larger agent on the user's behalf. VISION §6.

    **The tool is provider-neutral and the name of the agent is a runtime
    fact, not a model decision.** Corn-Jr is single-user by design and every
    instance is somebody's own copy, so which agent sits behind this is
    whatever that person configured -- Claude, a GPT, Qwen, DeepSeek, or a
    model on their own hardware. Baking one vendor into the schema would make
    the corpus wrong for every instance that chose differently, and the model
    would have learned a proper noun where the design wanted a role.

    So `agent` is a **display name only**: it is not in `params`, the model
    never emits it, and `validate_call` would reject it if it tried. It exists
    so the spoken acknowledgment can name the thing the user actually named.

    **The payload carries `request` back unaltered, and that is load-bearing
    rather than redundant.** Every other tool here returns something the model
    did not write: a resolved contact, an answer, a date. This one returns the
    user's own words, because the one thing that must never drift between what
    was said and what was sent is the thing the model itself put in the call.
    An observation that echoed only a status would leave the relay unwitnessed
    at exactly the point §6 calls the most consequential in the library.

    **`say` names the verbatim guarantee out loud every single time**, and
    appends the addendum when there is one. The user already knows what they
    said; what they have not heard is what was added in their name, so that is
    the half the acknowledgment spends its words on. Composed here rather than
    left to the model for `_lookup`'s reason -- a spoken promise about what was
    relayed is not a sentence 250M parameters should be authoring, and
    composing it in code makes it true by construction instead of by habit.

    One failure, and it is the analogue of the empty book: there is nothing to
    relay. `save_note` is deliberately the tool that cannot fail, so this one
    does not need to be a second; what it needs is to not send an empty message
    as the user, which is a different and worse kind of nothing.
    """
    if not request.strip():
        return {
            "ok": False,
            "reason": "nothing_to_relay",
            "say": f"What would you like me to ask {agent}?",
        }
    queued = {"status": "queued", "request": request}
    say = f"Asking {agent} now -- I've passed that on word for word"
    if context:
        queued["context"] = context
        say += f", and added that {context}"
    queued["say"] = say + "."
    return queued


_FACT_INDEX_CACHE: dict[int, dict[str, tuple[str, str]]] = {}


def _fact_index(facts: tuple[tuple[str, str, str], ...]) -> dict[str, tuple[str, str]]:
    """Lowercased pattern -> (answer, source), memoised per table.

    Keyed on `id` because the two tables are module-level constants that live
    for the process, and a tuple of thousands of triples is not worth hashing
    on every lookup. `_prefix_free` is what makes the mapping unambiguous;
    `check_tools.py` asserts it.
    """
    key = id(facts)
    idx = _FACT_INDEX_CACHE.get(key)
    if idx is None:
        idx = {p.lower(): (a, s) for p, a, s in facts}
        _FACT_INDEX_CACHE[key] = idx
    return idx


def web_search_tool(
    query: str,
    facts: tuple[tuple[str, str, str], ...] = FACTS,
    vague: tuple[tuple[str, str], ...] = VAGUE_QUERIES,
) -> dict:
    """Look something up, and hand back an answer short enough to say out loud.

    **The payload is an `answer` field, not a page of results**, and that is the
    load-bearing decision. VISION §6's confirmed use case is "ask, he looks it
    up, he reads back a useful answer" -- so the obvious shape is a list of
    snippets the model summarises. That would be the one place in this corpus
    where Corn-Jr composes a fact rather than copying one, and §5.2 forbids
    exactly that: the failure it is built to prevent is answering from the
    weights instead of from the lookup. A 250M model asked to summarise three
    snippets will sometimes summarise them into something that was not in any
    of them, and it will do it fluently.

    So the tool does the extraction and the model does the reading-out. That
    keeps `web_search` on the same discipline as `resolve_date`, which means
    the copy behaviour §4 rests on gets tested on a second tool with a
    different payload shape rather than being assumed to generalise.

    Retrieval quality then lives in the tool, where it can be measured and
    swapped, instead of in the weights, where it cannot.
    """
    q = " ".join(query.strip().lower().split())
    if not q:
        return {"ok": False, "reason": "empty_query",
                "clarify": "What would you like me to look up?"}
    for pattern, question in vague:
        if q == pattern.lower():
            return {"ok": False, "reason": "underspecified", "clarify": question}
    # Exact hit first, and only then the substring scan. The index is now
    # thousands of facts rather than 28 (see `_invent_facts`), and the
    # generator always asks with the pattern verbatim -- so the common path has
    # to be a dict lookup or building the slice becomes quadratic. The scan
    # below is unchanged and still decides every inexact query.
    hit = _fact_index(facts).get(q)
    if hit is not None:
        answer, source = hit
        return {"answer": answer, "source": source, "query": query.strip()}
    for pattern, answer, source in facts:
        p = pattern.lower()
        if p in q or q in p:
            return {"answer": answer, "source": source, "query": query.strip()}
    return {
        "ok": False,
        "reason": "no_results",
        "say": f"I couldn't find anything useful for {query.strip()}.",
    }


# What the book says when there is no book yet. Two forms rather than one so
# the reply names the action he cannot take, and **neither contains the name
# that was asked for** -- which is the property that separates this from
# `not_found` and the one `check_tools.py` asserts.
EMPTY_BOOK_SAY: dict[str, str] = {
    "ring": "You haven't got any contacts saved yet, so there's nobody to ring.",
    "text": "You haven't got any contacts saved yet, so there's nobody to text.",
}


# The words a slot crosses on its way into the message. "text Priya that I am
# running late" captured `Priya that I am running late`, and the `that` is the
# boundary the 53 trained names never taught. Measured connectors only.
_OVERRUN_CONNECTORS = frozenset({"that", "saying", "say"})


def _flat_words(text: str) -> list[str]:
    """Lowercased word list, punctuation off. `_normalised`'s flattening."""
    return re.findall(r"[a-z0-9']+", text.lower())


def _resolves(name: str, book: tuple[str, ...]) -> bool:
    """Would `_lookup` find this name at all -- exactly, or by first name."""
    q = name.strip().lower()
    return any(c.lower() == q or c.split()[0].lower() == q for c in book)


def shed_overrun(contact: str, message: str, book: tuple[str, ...]) -> str:
    """The contact with the message it swallowed trimmed off, or unchanged.

    **The fourteenth finding's slot boundary, repaired where the evidence
    lives.** Name boundaries were learned from 53 trained names, so a name
    outside that vocabulary has no learned end and the slot runs on into the
    message: `text Priya that I am running late` arrives here as
    `{"contact": "Priya that I am running late", "message": "I am running
    late"}` -- a call the copy grammar was right to allow, because the string
    is a span of the utterance and spans are all it constrains. Live on
    2026-08-26 that was a `not_found` naming the whole sentence.

    **The gate is that the tail must be the message, and that is what keeps
    this from being substitution.** A trim is accepted only when the words
    shed are a prefix of the `message` argument (one connector allowed at the
    joint), because the failure being repaired is precisely "the slot ran
    into the message" and the overrun is therefore the message's own opening.
    `text Sam Njoroge dinner at 8` with only a Sam Iversen in the book stays
    `not_found`: "Njoroge" is not how the message starts, so no prefix of it
    passes the gate, and refusing by name beats texting the wrong Sam --
    which is the trade the fourteenth finding priced. `place_call` gets no
    repair at all for the same reason: with no message there is no evidence,
    and the confirm gate is a second net, not a substitute for one.

    **A contact that already resolves is returned untouched, and that is what
    makes this safe next to the generator.** This module builds corpora, and
    `check_tools.py` pins the generated tables byte for byte; every generated
    call uses an exact book name, hits the early return, and nothing this
    function does can reach a training file.

    Longest surviving name first, so `Nadia Okonjo I'm running late` sheds to
    `Nadia Okonjo` and not to the ambiguity of a bare first name. Whatever
    the trim resolves to still goes through `_lookup` -- a shed that lands on
    a shared first name comes back as the same clarify question it always
    was.
    """
    words = contact.split()
    if len(words) < 2 or not book or _resolves(contact, book):
        return contact
    msg = _flat_words(message)
    for k in range(len(words) - 1, 0, -1):
        head, tail = words[:k], words[k:]
        if tail and tail[0].lower() in _OVERRUN_CONNECTORS:
            tail = tail[1:]
        shed = _flat_words(" ".join(tail))
        if shed and msg[: len(shed)] != shed:
            continue
        if _resolves(" ".join(head), book):
            return " ".join(head)
    return contact


def _lookup(
    contact: str, book: tuple[str, ...], ok: Callable[[str], dict], action: str = "ring"
) -> dict:
    """Resolve a name against the book, or say why not.

    **An empty book is not a missing contact**, and collapsing the two is the
    cold-start bug. `not_found` says "I don't have a contact called Fergus",
    which asserts that a book was consulted and lacks him. Said to someone who
    has just installed Corn-Jr and has no book at all, that is false in a way
    that reads as a malfunction: they ask for five different people, get five
    flat denials, and conclude he cannot dial. The store being empty is a
    different fact about the world and gets a different answer -- one that names
    the cause and is the same whoever was asked for.

    This matters more once Corn-Jr is something other people run: every user
    starts here, and it is the first thing any of them will see.
    """
    if not book:
        return {"ok": False, "reason": "empty", "say": EMPTY_BOOK_SAY[action]}
    q = contact.strip().lower()
    exact = [c for c in book if c.lower() == q]
    if len(exact) == 1:
        return ok(exact[0])
    by_first = [c for c in book if c.split()[0].lower() == q]
    if len(by_first) == 1:
        return ok(by_first[0])
    # **The kin words, and the only line of this file the book layer reaches
    # into.** the contact book (removed 2026-10-13) could hand a `Names` tuple carrying
    # an alias map, so "call dad" resolves to whoever the owner said dad is.
    # `getattr` rather than a parameter because `CONTACTS` -- the 53 trained
    # names every guard and every eval runs against -- is a plain tuple with no
    # aliases, and this way its behaviour is unchanged to the byte. The reply
    # names the canonical contact, because the confirmation gate is what the
    # user reads before an irreversible action.
    aliases = getattr(book, "aliases", None)
    if aliases:
        # "text my mum" is how it is said out loud, and the copy grammar hands
        # the slot over as spoken.
        for key in (q, q[3:].strip() if q.startswith("my ") else q):
            full = aliases.get(key)
            if full is not None:
                return ok(full)
    if len(by_first) > 1:
        surnames = [c.split()[-1] for c in by_first]
        joined = " or ".join(surnames) if len(surnames) == 2 else (
            ", ".join(surnames[:-1]) + ", or " + surnames[-1]
        )
        return {
            "ok": False,
            "reason": "ambiguous",
            "matches": by_first,
            "clarify": f"Which {by_first[0].split()[0]} -- {joined}?",
        }
    return {
        "ok": False,
        "reason": "not_found",
        "say": f"I don't have a contact called {contact.strip()}.",
    }
