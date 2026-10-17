"""Schema-constrained decoding for the call object -- VISION §6's fourth
principle, finally with a price on it.

`corn/tools.py` names this and defers it: "the fourth, schema-constrained
decoding, is a Phase 3 inference concern. What belongs here is the schema it
would constrain against, and `validate_call` is that schema made executable."
This is the other half. The schema is unchanged and `validate_call` is still
what decides whether a call runs; what changes is that a token which cannot
lead to a call `validate_call` accepts is never sampled in the first place.

**The failure it exists for is measured, not hypothetical.** The fourth gap
`corn/agent.py` found: in-pool note content works on every carrier in
`NOTE_TEMPLATES` and out-of-pool content fails on all of them -- `make a note
that the deploy is blocked on the migration` copies the text perfectly, never
emits `"}}`, and restarts the call forever. The content was already right. What
was missing was three bytes the model had never seen after those particular
words, and a grammar supplies them for free: once the string closes, `,` and
`}` are the only continuations there are.

So the claim this file makes is narrow and worth stating so it can be checked:
**it does not make the model choose a better tool, or read an observation it is
reciting past.** Gaps 1 and 5 are corpus problems and a decoder cannot touch
them.

**Gap 3 is the exception, and finding that out cost one measurement.** The
paragraph above used to say "or copy a name it does not know" and list gap 3
with the other two. That was true of the schema constraint and false of the
machinery: the schema is the only thing this file *had* been constraining
against, and the user's own utterance is another. See `CopySpec` below.

## The copy constraint -- gap 3

`text Ophelia that I'm running late` emits `{"contact": "Omar", ...}` at
temperature 0, and the runtime texts Omar Silva and reports success. 45 of 120
at 91.6M, 56 at 29.6M, on items every other scorecard row passes -- `place_call`
was the right tool so `tool.selection` passed and `{"contact": "Omar"}` is
schema-valid so `tool.validity` passed. Nothing in the schema can see it,
because "Omar" is a perfectly good string.

What can see it is that **Omar is not in the sentence.** `CopySpec` narrows the
declared copy slots to spans of the user's own utterance, so a name the user did
not say is not a token the model may sample. The correct answer to Ophelia is a
call naming Ophelia and a `not_found` from the book, and that is the only call
this leaves reachable.

Two properties make it safe rather than plausible, and `check_grammar.py`
asserts both over `data/raw/tools.txt` rather than taking them on trust:

  * **Every one of the 9,000 calls in the corpus already satisfies it** -- all
    four slots, exact substrings of their own `<|user|>` line, zero exceptions.
    So the constraint bans nothing any generator ever wrote.
  * **The span must begin and end on a word boundary**, which is what stops the
    model closing early on `Ophel` -- a substring, and a call that would then
    validate. Also true of all 9,000.

**One thing the check caught that writing it did not.** The first version banned
backslash outright in a copy slot, on the reasoning that a contact name does not
contain one. `json.dumps` defaults to `ensure_ascii=True`, so the book's `Ben
Traoré` goes on the wire with its `é` written as a `\\u00e9` escape -- the
escape *is* the corpus form, and the ban refused a call the generator writes on
2,316 `send_text` transcripts' worth of book. Escapes are now resolved to the
bytes they denote before the span test runs, which is the only way the wire form
and the sentence can be compared at all.

**`resolve_date`'s `expression` is deliberately not a copy slot, and the corpus
is why.** It misses 1,348 times out of 73,970: `what's today's date?` resolves
through `this morning`, a span the utterance does not contain. Constraining it
would ban a call the generator writes daily, which is exactly the quiet failure
`check_grammar.py`'s first group exists to catch. `recall_day`'s `date` misses
90,293 times for the same reason and worse -- it is an ISO date and never
appears in the sentence at all.

The default is `contact` on the two tools that take one, because that is where
the failure was measured. The other three span slots pass the corpus check and
are available through `--copy`; they are unmeasured, and widening a constraint
on the strength of a corpus property alone is what the paragraph above got
wrong once already.

**With no source set this file behaves exactly as it did before** -- `copy` is
`None`, `step` takes its old branches byte for byte, and every existing
assertion still reads what it read.

## What it constrains, and what that costs

The machine below accepts exactly:

    {"name": <a REGISTRY key>, "arguments": {<that tool's params>: <strings>}}

with optional spaces where JSON allows them, required params present before the
object may close, no key twice, and no empty or all-space value -- which is
`validate_call`'s check list, one byte at a time instead of once at the end.

Two deliberate narrowings, both stricter than `validate_call`, both checked by
`scripts/check_grammar.py` against every call in the corpus rather than argued
for here:

  * **`name` must precede `arguments`.** JSON does not care and neither does
    `validate_call`, but the tool's identity is what makes its parameter names
    an enum, and reading `arguments` first would mean constraining keys against
    the union of all eight tools. Every call in `data/raw/` is in this order
    because `json.dumps` wrote them all.
  * **Only U+0020 counts as insignificant whitespace.** A newline inside a call
    is legal JSON and is not something the corpus contains, and allowing it
    would let the model wander out of the object without leaving it.

**The instrument, which is the part worth keeping.** A constraint that silently
fixes things is a constraint that hides how often the model was wrong. Every
step where the unconstrained argmax was masked out is recorded -- what it
wanted, what it took -- so "the grammar bit 3 times on this turn" is a number
the runtime reports rather than a thing that happened invisibly. That count is
the honest measure of what schema-constrained decoding is worth, and it is free
to collect.

**What it does not do is force a call.** The constraint arms on `<|call|>` and
not before, so the choice between calling and speaking is the model's, exactly
as `tool.selection` scores it. Nothing here can move a routing row.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

import torch

from .markers import D_CALL
from .tools import REGISTRY

SPACE = 0x20
QUOTE = 0x22
BACKSLASH = 0x5C

# The escapes JSON allows after a backslash, `u` handled separately.
_ESCAPES = frozenset(b'"\\/bfnrt')
_HEX = frozenset(b"0123456789abcdefABCDEF")

# What each of those denotes. A copy slot compares against the utterance's bytes,
# so `\n` has to become a newline before the comparison means anything.
_ESCAPE_BYTES = {
    ord('"'): 0x22, ord("\\"): 0x5C, ord("/"): 0x2F, ord("b"): 0x08,
    ord("f"): 0x0C, ord("n"): 0x0A, ord("r"): 0x0D, ord("t"): 0x09,
}

_TOOL_NAMES = tuple(REGISTRY)


def _names(declared: tuple[str, ...] | None) -> tuple[str, ...]:
    """The tool names the machine will accept on this decode.

    `None` means the whole registry, which is what every caller before the
    thirty-fourth finding wanted and what `check_grammar.py` measures against
    the corpus. A tuple narrows it to the tools *declared for this turn*, and
    the finding is the reason the narrowing exists:

        `absent` -- items where the asked-for tool is deliberately not declared
        -- reads 0 in twelve of fourteen cells, and the mechanism is not that
        he picks the nearest declared tool. He **invents a name that is in no
        declaration at all**, 216 of 276 and 190 of 276. There is no membership
        test to strengthen.

    Constraining the emission to the declared set is that finding's own
    recommendation, and it is worth being exact about what it buys, because it
    is less than it looks: it turns ~78% of those failures into either a
    declared tool or no call at all. **It does not produce a refusal.** A model
    with one reflex still has one reflex; this only stops the reflex reaching a
    tool that does not exist. The behaviour is a training question and
    `configs/mix_v1_chat.py` is the arm.
    """
    if declared is None:
        return _TOOL_NAMES
    # **Membership in `REGISTRY` is not required, and that is a decision.** The
    # corpus this narrowing exists to read -- `corn/toolspace.py` -- coins its
    # tool names per transcript (`find_quick_backup_route`), so a registry test
    # here would reject exactly the arm the thirty-fourth finding measured. What
    # is still checked is what the machine below can physically emit: a name is
    # walked one byte at a time through `_enum_byte`, which refuses anything at
    # or above 128, so a non-ASCII or empty name would be silently unreachable
    # rather than merely unused. Failing on it at construction keeps the typo
    # story the registry test used to tell, for the part still tellable.
    bad = tuple(n for n in declared
                if not n or not n.isascii() or QUOTE in n.encode() or BACKSLASH in n.encode())
    if bad:
        raise ValueError(
            f"declared names the grammar could never emit: {bad} -- names must "
            f"be non-empty ASCII without quotes or backslashes"
        )
    return tuple(declared)


def _required(tool: str) -> tuple[str, ...]:
    """What `tool` must be given -- nothing, when the registry has never heard of it.

    A declared tool the registry does not carry brings its parameters on the
    declaration line, and this machine is not given that line. So it enforces
    well-formedness and declines to invent a requirement it has no source for:
    an unknown tool may close on `{}` and may close on any set of keys. See
    `_names` for why unknown tools are legal at all.
    """
    known = REGISTRY.get(tool)
    return known.required() if known is not None else ()


def _nameable(tool: str, used: tuple[str, ...]) -> bool:
    """Is there a key this tool could still be given?

    **The machine must never enter a state it cannot leave.** A phase with no
    legal byte is not a strict grammar, it is a deadlock: `_mask` finds nothing
    allowed, releases the constraint mid-object, and hands an unconstrained
    model a half-written call to finish. What comes out is `not_json` and
    nothing executes -- so a grammar that dead-ends is strictly worse than one
    that never armed.

    That is not hypothetical. `decline` has no parameters, and until this
    function existed the machine accepted the quote that opens a key for it --
    reachable in one token, because `{"` is a single BPE merge -- and then had
    nothing to offer. Every `decline` that took that branch was released and
    lost. The branch below that lets a zero-parameter tool close on `{}` was
    written when its own comment could say "no tool in the registry is like
    this today"; WS-E made that false and this is the other half of the change
    it needed.

    True for a tool the registry does not carry, for `_required`'s reason: its
    parameters arrive on the declaration line, this machine is not given that
    line, and refusing a key it cannot check would be inventing a limit it has
    no source for.
    """
    known = REGISTRY.get(tool)
    if known is None:
        return True
    return any(n not in used for n in known.allowed())

# --------------------------------------------------------------------------
# The copy constraint
# --------------------------------------------------------------------------

# What counts as part of a word for the boundary rule. Every byte >= 128 counts,
# so a value may not close inside a multi-byte character: `Traor` is not a legal
# close of `Ben Traoré`, which matters because the book contains one.
_WORDISH = frozenset(
    b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
)

# The slots whose values are spans of the utterance in every call the corpus
# contains. `check_grammar.py` asserts this over `data/raw/tools.txt`; it is a
# measurement, not a design intent, and `resolve_date.expression` is the
# counter-example that keeps it from being all of them.
SPAN_SLOTS: frozenset[tuple[str, str]] = frozenset(
    {
        ("place_call", "contact"),
        ("send_text", "contact"),
        ("send_text", "message"),
        ("save_note", "text"),
        ("web_search", "query"),
    }
)

# What `corn/agent.py` turns on unless told otherwise: the slot the failure was
# measured on, and no more.
DEFAULT_COPY_SLOTS: frozenset[tuple[str, str]] = frozenset(
    {("place_call", "contact"), ("send_text", "contact")}
)

# --------------------------------------------------------------------------
# The parse line -- PLAN-DECOMPOSE §4
# --------------------------------------------------------------------------
#
# **The labels live here rather than in the generator that emits them, and the
# layering rule is why.** `corn/grammar.py` is one of the twelve modules in the
# runtime closure and `corn/decompgen.py` is a generator; the closure may not
# reach a generator (HACKING §2), so a constant both of them need has to sit on
# this side and be imported in the other direction. `check_layering.py` is what
# holds that.
#
# **Closed, and small, for finding 51's reason.** A six-way choice becoming an
# eight-way one read `tool.selection` 85.5% and `routed` 6/16, so every value
# is paid for in exposures and the set grows only by PLAN-TAGS ground rule 3 --
# a measured defect whose class has no home. Seven labels and seven moves is
# the rung-1 set; PLAN-DECOMPOSE §11 item 1 is where the real one gets decided.
LEVEL1_LABELS: tuple[str, ...] = ("social", "ask", "do", "follow", "chat")
LEVEL2_LABELS: tuple[str, ...] = ("ask", "find", "send", "note")
PARSE_LABELS: tuple[str, ...] = ("social", "ask", "do", "follow", "chat",
                                 "find", "send", "note")
# **The 1.0 set is the eight and `act`** (D-A1.21, owner 2026-10-03, on
# PLAN-TAG-SPINE §12's D-A2.1): the real slices call tools that change
# state -- set an alarm, add a meeting, remove a subscription, place a call --
# which neither look up, pass on nor write down, and folding them into `note`
# would give one label two meanings (FAILURES-PARSE §2). A separate tuple
# rather than a ninth entry above, because `PARSE_LABELS` sizes the tag map
# (`corn.tagmap.TAG_VOCAB`, 17) that arm F's checkpoints were built with;
# the binds take a `labels` argument, and the real carriers pass this one.
PARSE_LABELS_1_0: tuple[str, ...] = PARSE_LABELS + ("act",)
MOVES: tuple[str, ...] = ("greeting", "wellbeing", "thanks", "farewell",
                          "ack", "consolation", "open")
# **D-A1.22, owner 2026-10-09: `share`, the eighth move** -- the person tells
# him something about their life (news, a feeling, a thing they are excited
# about), answered by reacting to it and asking about it. Earned by a measured
# defect with no home (PLAN-TAGS ground rule 3): on 150 hand-labelled natural
# openings it is 34, more than any move in the set, and the seven cover 62 of
# 126 social turns (finding 157, fourth amendment). A separate tuple, as
# `PARSE_LABELS_1_0` is for `act`, because the decomposition world
# (`corn/decompgen.py`, arms F, G, S on disk) is built and guarded on the
# seven; the move bind admits this set, a superset, so it refuses nothing a
# corpus on disk writes.
MOVES_1_0: tuple[str, ...] = MOVES + ("share",)

# The two line prefixes. Plain text, not markers: `tokenizers/bpe8k.json` ships
# seven specials and an eighth makes every checkpoint on disk incomparable
# (rule 3). Measured on `bpe8k` 2026-09-09: `<|move|>greeting` written as plain
# bytes is 11 tokens, six of them drawing a marker that is not one; `move:
# greeting` is 7 and cuts the same way every time.
PARTS_PREFIX = "parts: "
MOVE_PREFIX = "move: "


def _wordish(b: int) -> bool:
    return b in _WORDISH or b >= 128


@dataclass(frozen=True)
class CopySpec:
    """Which argument slots must be spans of `source`, and what `source` is.

    Frozen and hashable because it joins `State` in the mask cache key -- the
    legal continuations of a half-written name depend on the sentence being
    copied from, so two turns with different utterances are different masks.

    `source` is bytes rather than str on purpose. The model emits UTF-8 one byte
    at a time and a half-written `é` is not a decodable string, so the substring
    test has to run at the level the tokens actually arrive at. It also makes
    the partial-character case correct for free: the first byte of `é` extends
    the span only where the source has that byte next.
    """

    slots: frozenset[tuple[str, str]]
    source: bytes
    # **A second, shorter source, for the slots that must not read history.**
    # `slots` are checked against the whole conversation, which is what a
    # contact needs -- `corn/agent.py` binds it that way on purpose so the
    # clarify path can copy a name out of an earlier observation. A note is the
    # opposite case: what the user asked to be written down is in the sentence
    # they just typed, and anything reachable from an earlier turn is a
    # *previous* request being written to disk under this one's authority.
    #
    # Session 13's defect, measured: `note down buy milk` declines, then `save
    # a note that I need to call the dentist tomorrow` writes
    # `save_note{"text": "buy milk"}` and says "Noted." -- **7 of 20 pairs**
    # before this field existed. Both slots are copy slots; they differ only in
    # how far back the source reaches, which is why this is a second source
    # rather than a second mechanism.
    narrow: frozenset[tuple[str, str]] = frozenset()
    narrow_source: bytes = b""

    def holds(self, tool: str, param: str) -> bool:
        return (tool, param) in self.slots or (tool, param) in self.narrow

    def source_for(self, tool: str, param: str) -> bytes:
        """Which source this slot is a span of. The narrow one, or the whole."""
        return (self.narrow_source if (tool, param) in self.narrow
                else self.source)


class _SourceWatch:
    """A `CopySpec` that records whether anything asked it for the source.

    **The point is a cache key, and the argument is about data flow rather
    than about the grammar.** A mask built without ever reading the source
    cannot depend on the source, so it can be cached under the state alone and
    reused in every later round -- which is the difference between a cache
    that survives a turn and one that does not (see `allowed_ids`).

    Deciding it by *watching* rather than by reasoning is what makes it sound.
    The tempting rule -- "the source only matters inside a copy slot" -- is
    false, because a token is several bytes and can walk *into* a slot from a
    state that is not yet in one; that state's mask is source-dependent while
    looking like it is not. Watching catches that case for free: the walk into
    the slot calls `source_for`, the flag goes up, and the entry gets the full
    key like any other.

    It fails safe in the one direction it can fail. A walk that consults the
    source and then does not depend on it is cached conservatively under the
    full key -- a missed optimisation. The dangerous case, an entry cached
    without the source that needed it, cannot arise: it would require the
    value to have been read without `source_for` being called, and
    `source_for` is the only way to reach it from inside `step`.

    `holds` is deliberately *not* watched. It answers from `slots`/`narrow`,
    which are configuration and identical in every round; only the source text
    grows. Watching it would make every state look sensitive and buy nothing.
    """

    __slots__ = ("spec", "read")

    def __init__(self, spec: CopySpec):
        self.spec = spec
        self.read = False

    def holds(self, tool: str, param: str) -> bool:
        return self.spec.holds(tool, param)

    def source_for(self, tool: str, param: str) -> bytes:
        self.read = True
        return self.spec.source_for(tool, param)


def span_ok(source: bytes, value: bytes, closing: bool) -> bool:
    """Is `value` a legal span of `source` so far -- or a legal complete one?

    While the string is open this asks only that some occurrence starts on a
    word boundary, because the model is mid-name and the right edge has not
    happened yet. On the closing quote it asks for both edges, which is the
    check that refuses `Ophel`: a substring of the utterance, schema-valid, and
    the wrong contact.

    **ASCII case does not distinguish spans.** The corpus never taught case to
    matter -- generated queries are exact spans of utterances that were built
    together -- but live users capitalise sentence-initial words, and under
    `--multi` the byte-exact check turned that into a routing failure: "How
    many people live there?" masks the lowercase "how" the model opens with,
    and the greedy continuation after the bite lands on the one span that is
    still legal, the *previous turn's query* sitting in the history. Measured
    live 2026-08-29: three of three capitalised follow-ups re-issued the old
    query verbatim; the all-lowercase twin of the same turn did not. `lower()`
    on bytes folds only A-Z, so UTF-8 multibyte characters -- the accented
    contacts the escape path exists for -- pass through untouched.
    """
    source = source.lower()
    value = value.lower()
    if not value:
        # An empty prefix is where every string starts; an empty value is what
        # `validate_call` rejects, and `nonblank` already refuses to close on it.
        return not closing
    start = 0
    while True:
        i = source.find(value, start)
        if i < 0:
            return False
        if i == 0 or not _wordish(source[i - 1]) or not _wordish(value[0]):
            if not closing:
                return True
            j = i + len(value)
            if j == len(source) or not _wordish(source[j]) or not _wordish(value[-1]):
                return True
        start = i + 1


def _hex_reachable(source: bytes, value: bytes, digits: str) -> bool:
    """Could a `\\uXXXX` escape starting `digits` keep `value` a span of `source`?

    **The third absorbing state, and the subtlest.** A copy slot checks the
    escape only when all four digits are in, because a codepoint is not known
    until then -- so until this existed, the machine accepted `\\u`, accepted a
    digit, accepted another, and only at the fourth discovered that no character
    it could denote continues the span. By then every path out was gone: the
    mask emptied, the constraint released mid-string, and the model finished an
    unconstrained call that `validate_call` refused. The receipt at 260M is
    `{"contact": ": \\u1000000000000...` -- one legal prefix, then a hundred
    digits of nothing.

    The escape cannot simply be banned in a copy slot: 49 calls in
    `data/raw/tools.txt` use one, all of them in `place_call.contact` or
    `send_text.contact`, all of them accented names like `Ben Traor\\u00e9`.
    Banning it would refuse the corpus and, worse, refuse a real contact.

    So it is pruned instead, and the source supplies the candidates. Whatever
    the escape denotes has to *follow* an occurrence of `value` in `source`, and
    there are at most as many such characters as there are occurrences -- a
    handful, against the 65,536 a codepoint could otherwise be. A digit is legal
    exactly when one of those characters is still reachable through it.
    """
    try:
        # The same ASCII fold as `span_ok`, or an occurrence that only exists
        # case-folded would refuse an escape the closing check will accept.
        text = source.lower().decode("utf-8")
        head = value.lower().decode("utf-8")
    except UnicodeDecodeError:
        # Mid-character: the escape denotes a whole codepoint and cannot be the
        # tail of a partly-written one, so there is nothing it could complete.
        return False
    want = digits.lower()
    start = 0
    while True:
        i = text.find(head, start) if head else start
        if i < 0 or (not head and i >= len(text)):
            return False
        j = i + len(head)
        if j < len(text):
            c = text[j]
            if f"{ord(c):04x}".startswith(want) and span_ok(
                source, value + c.encode("utf-8"), closing=False
            ):
                return True
        start = i + 1


# --------------------------------------------------------------------------
# The machine
# --------------------------------------------------------------------------


class State(NamedTuple):
    """One position inside the call object.

    Frozen and hashable on purpose: it is the cache key for the token mask, and
    the whole reason masking is affordable in Python is that a state repeats.
    A 60-byte note body is 60 decode steps and two distinct states, because
    everything that distinguishes them -- the tool, the keys already given --
    is constant while the string runs.

    **`value` is the exception and it is opt-in.** A copy slot has to remember
    what has been written to know what may come next, so a constrained string
    is one state per byte rather than two for the whole run. That is affordable
    for the reason it is expensive: inside a span there are usually one or two
    legal continuations, so each of those states masks nearly the whole
    vocabulary and builds fast. It stays `b""` in every unconstrained slot, so
    the cheap case is unchanged.
    """

    phase: str = "start"
    tool: str = ""             # decided at the close of the name string
    prefix: str = ""           # partial match inside a literal or an enum
    pending: str = ""          # the argument name whose value is being written
    used: tuple[str, ...] = () # argument names already given, sorted
    nonblank: bool = False     # has the open string got a non-space byte yet
    hexleft: int = 0           # remaining digits of a \uXXXX escape
    value: bytes = b""         # the copy slot's bytes so far; b"" when unconstrained
    spaces: int = 0            # insignificant spaces run so far; see MAX_SPACES


def replace(st: State, **changes) -> State:
    """`st` with some fields changed. The one hot allocation in this file.

    **A `NamedTuple` rather than a frozen dataclass, and the reason is the call
    count.** `step` runs once per candidate byte per decode position, so it
    builds a new state 11.5 million times over `check_grammar.py` alone.
    `dataclasses.replace` walks `fields()`, builds a kwargs dict and then runs
    a frozen `__init__` that does an `object.__setattr__` per field;
    `NamedTuple._replace` is a tuple construction. Measured over 300,000 calls:

        frozen dataclass, dataclasses.replace   1.92 us   the old form
        frozen dataclass, slots=True            1.95 us   no help
        NamedTuple._replace                     0.60 us   3.2x

    This wrapper exists so that stays a two-line change: every call site still
    reads `replace(st, phase=...)`, and the name shadows the `dataclasses`
    import deliberately -- nothing else in this file was ever passed to it.
    `CopySpec` stays a dataclass, because it is built once per turn.

    The properties `State` is chosen for are unchanged: a `NamedTuple` is
    immutable and hashes by value, which is all the mask cache asks of it.
    """
    return st._replace(**changes)


DONE = "done"


def _literal(st: State, b: int, text: str, nxt: str) -> State | None:
    """Consume a fixed string one byte at a time, spaces allowed before it."""
    if not st.prefix and b == SPACE:
        return st
    want = text[len(st.prefix)]
    if b != ord(want):
        return None
    prefix = st.prefix + want
    if len(prefix) == len(text):
        return replace(st, phase=nxt, prefix="")
    return replace(st, prefix=prefix)


def _enum_byte(st: State, b: int, options: tuple[str, ...]) -> str | None:
    """The prefix `b` extends, or None if no option starts with it."""
    if b >= 128:
        return None  # every name in the registry is ASCII
    cand = st.prefix + chr(b)
    return cand if any(o.startswith(cand) for o in options) else None


MAX_SPACES = 1
"""How much insignificant whitespace may run before the machine stops allowing it.

**An unbounded legal token that does not advance the machine is an absorbing
state, and at temperature 0 the model cannot leave it.** JSON permits any run
of spaces between tokens and this grammar used to permit it too, which looks
harmless and is not: when the model wants a byte the grammar forbids, `_mask`
leaves it the best *legal* token instead, and a space is one of the most
probable tokens in any vocabulary. Nothing about the context changes when it is
taken, so the next step re-runs the same argmax over the same mask and takes a
space again -- forever, until `_until_marker` runs out of budget and the turn
returns a call cut off at `{"name": "place_call", "arguments"  :`. The
constraint never releases and never errors. It just quietly spends 200 tokens
on whitespace.

That was 7 of 16 turns at 260M, and the emission is the receipt: two spaces
before a colon no generator ever wrote.

One is enough for every corpus call, which is what makes the cap safe rather
than merely small. Every call in `data/raw/` is `json.dumps` output, so its
whitespace is exactly one space after `:` and after `,` and none anywhere else;
`scripts/check_grammar.py` group 1 re-checks all 4,955 of them byte for byte
against this cap rather than taking that on trust.
"""


def step(st: State, b: int, copy: CopySpec | None = None,
         declared: tuple[str, ...] | None = None) -> State | None:
    """Consume one byte, or None if the grammar does not allow it here.

    A thin wrapper on `_advance`, which is the switch. What it adds is the
    whitespace cap: `_advance` signals "insignificant space, nothing moved" by
    returning the state it was given *unchanged*, and every one of its `return
    st` branches is a `b == SPACE` branch, so identity is a reliable test for
    it. A run longer than `MAX_SPACES` is refused, and any real advance clears
    the count.
    """
    nxt = _advance(st, b, copy, declared)
    if nxt is None:
        return None
    if nxt is st:
        if st.spaces >= MAX_SPACES:
            return None
        return replace(st, spaces=st.spaces + 1)
    return replace(nxt, spaces=0) if nxt.spaces else nxt


def _advance(st: State, b: int, copy: CopySpec | None = None,
             declared: tuple[str, ...] | None = None) -> State | None:
    """The switch itself. Call `step`, not this.

    Written as a switch rather than a table because the interesting parts are
    the three places a phase branches on something other than the byte -- the
    enum of unused parameter names, the ban on closing an empty string, and the
    ban on closing an object whose required params are not all present.

    `copy` adds a fourth: inside a declared copy slot the legal continuations
    are the ones that keep the value a span of the user's sentence. Passing
    `None` -- the default, and what every caller did before it existed -- takes
    exactly the branches this function took then.

    `declared` adds a fifth, on the same terms: it narrows the tool-name enum
    to the tools offered on this turn. `None` is the whole registry and is what
    every caller did before the thirty-fourth finding; see `_names`.
    """
    p = st.phase
    names = _names(declared)

    if p == "start":
        if b == SPACE:
            return st
        return replace(st, phase="name_key") if b == ord("{") else None

    if p == "name_key":
        return _literal(st, b, '"name"', "name_colon")

    if p == "name_colon":
        if b == SPACE:
            return st
        return replace(st, phase="name_val") if b == ord(":") else None

    if p == "name_val":
        if b == SPACE:
            return st
        return replace(st, phase="name_body", prefix="") if b == QUOTE else None

    if p == "name_body":
        if b == QUOTE:
            # `names` rather than `REGISTRY`: a name can be a real tool and
            # still not be on offer this turn, and closing the quote is the
            # last moment the difference can be caught.
            if st.prefix in names:
                return replace(st, phase="args_comma", tool=st.prefix, prefix="")
            return None
        cand = _enum_byte(st, b, names)
        return replace(st, prefix=cand) if cand else None

    if p == "args_comma":
        if b == SPACE:
            return st
        return replace(st, phase="args_key") if b == ord(",") else None

    if p == "args_key":
        return _literal(st, b, '"arguments"', "args_colon")

    if p == "args_colon":
        if b == SPACE:
            return st
        return replace(st, phase="args_open") if b == ord(":") else None

    if p == "args_open":
        if b == SPACE:
            return st
        return replace(st, phase="arg_first") if b == ord("{") else None

    if p in ("arg_first", "arg_key"):
        if b == SPACE:
            return st
        # Only when a key remains to be named. Opening a quote a tool has no
        # parameter to fill is the deadlock `_nameable` exists to prevent, and
        # it is one BPE token away at `args_open`, where `{"` is a single
        # merge.
        if b == QUOTE and _nameable(st.tool, st.used):
            return replace(st, phase="arg_name", prefix="")
        # `{}` only where the tool asks for nothing, and only before a comma
        # has promised another pair. `decline` is that tool -- it has no
        # parameters at all -- and every unknown declared tool takes this
        # branch too; see `_required`.
        if b == ord("}") and p == "arg_first" and not _required(st.tool):
            return replace(st, phase="obj_close")
        return None

    if p == "arg_name":
        known = REGISTRY.get(st.tool)
        if known is None:
            # No enum: the declaration names this tool's parameters and the
            # machine was not handed it, so it checks that the key is a
            # well-formed JSON string and not a repeat, and nothing more. The
            # narrowing this unlocks is a question about the *name* -- finding
            # 34's 78% is a name statistic -- so constraining parameters is a
            # bigger commitment than the reading needs.
            if b == QUOTE:
                if st.prefix and st.prefix not in st.used:
                    return replace(st, phase="arg_colon", pending=st.prefix,
                                   prefix="")
                return None
            if SPACE <= b < 0x7F and b not in (QUOTE, BACKSLASH):
                return replace(st, prefix=st.prefix + chr(b))
            return None
        options = tuple(n for n in known.allowed() if n not in st.used)
        if b == QUOTE:
            if st.prefix in options:
                return replace(st, phase="arg_colon", pending=st.prefix, prefix="")
            return None
        cand = _enum_byte(st, b, options)
        return replace(st, prefix=cand) if cand else None

    if p == "arg_colon":
        if b == SPACE:
            return st
        return replace(st, phase="arg_val") if b == ord(":") else None

    if p == "arg_val":
        if b == SPACE:
            return st
        if b == QUOTE:
            return replace(st, phase="arg_str", nonblank=False, value=b"")
        return None

    if p == "arg_str":
        constrained = copy is not None and copy.holds(st.tool, st.pending)
        # Read once per byte rather than per test: the answer cannot change
        # inside a single value, and `source_for` is a set membership.
        csrc = copy.source_for(st.tool, st.pending) if constrained else b""
        if b == QUOTE:
            # `validate_call` rejects a value that is empty or all space, so
            # the grammar must not let one close -- otherwise the constraint
            # produces calls the runtime then refuses, which is the worst of
            # both.
            if not st.nonblank:
                return None
            # And a copy slot must not close mid-word. `Ophel` is a substring of
            # the utterance and a valid call, so nothing downstream would object
            # to it; this is the only place it can be refused.
            if constrained and not span_ok(csrc, st.value, closing=True):
                return None
            return replace(
                st,
                phase="arg_next",
                used=tuple(sorted(st.used + (st.pending,))),
                pending="",
                value=b"",
            )
        if b == BACKSLASH:
            return replace(st, phase="arg_esc")
        if b < SPACE:
            return None  # raw control bytes are not legal in a JSON string
        if constrained:
            value = st.value + bytes((b,))
            if not span_ok(csrc, value, closing=False):
                return None
            return replace(st, value=value, nonblank=st.nonblank or b != SPACE)
        return replace(st, nonblank=st.nonblank or b != SPACE)

    if p == "arg_esc":
        constrained = copy is not None and copy.holds(st.tool, st.pending)
        csrc = copy.source_for(st.tool, st.pending) if constrained else b""
        if b == ord("u"):
            # The same prune with nothing typed yet: if no character reachable
            # from here can be written as an escape at all, `\u` is a door into
            # a room with no exit.
            if constrained and not _hex_reachable(csrc, st.value, ""):
                return None
            return replace(st, phase="arg_hex", hexleft=4, prefix="")
        if b not in _ESCAPES:
            return None
        # An escaped whitespace char counts as content here. It is the one
        # place this machine is looser than `.strip()`, and a value of "\n" is
        # not a thing 91.6M parameters have ever emitted.
        if constrained:
            # The span test compares against the utterance's *bytes*, so an
            # escape has to be resolved to the character it denotes before it
            # can be compared. Otherwise the wire form and the source form
            # disagree and every escaped value looks like an invention.
            value = st.value + bytes((_ESCAPE_BYTES[b],))
            if not span_ok(csrc, value, closing=False):
                return None
            return replace(st, phase="arg_str", nonblank=True, value=value)
        return replace(st, phase="arg_str", nonblank=True)

    if p == "arg_hex":
        if b not in _HEX:
            return None
        constrained = copy is not None and copy.holds(st.tool, st.pending)
        csrc = copy.source_for(st.tool, st.pending) if constrained else b""
        left = st.hexleft - 1
        # `prefix` is free here -- it carries a literal or an enum match and both
        # are finished long before a value opens -- so the digits ride in it
        # rather than in a field every unconstrained state would have to hash.
        # Accumulated only when constrained, so the cheap path keeps the two
        # states it always had.
        digits = (st.prefix + chr(b)) if constrained else ""
        if left:
            # Pruned every digit, not only the last: a digit no reachable
            # character could complete is a step into a state with no way out.
            if constrained and not _hex_reachable(csrc, st.value, digits):
                return None
            return replace(st, hexleft=left, prefix=digits)
        if constrained:
            try:
                raw = chr(int(digits, 16)).encode("utf-8")
            except (ValueError, UnicodeEncodeError):
                # A lone surrogate half. It denotes no character, so it cannot
                # be a span of anything anybody said.
                return None
            value = st.value + raw
            if not span_ok(csrc, value, closing=False):
                return None
            return replace(
                st, phase="arg_str", hexleft=0, prefix="", nonblank=True, value=value
            )
        return replace(st, phase="arg_str", hexleft=0, nonblank=True)

    if p == "arg_next":
        if b == SPACE:
            return st
        # A comma promises another pair, so it may only be written when there
        # is one left to write. Otherwise `arg_key` is entered with nothing
        # legal in it, which is the same deadlock one phase further on.
        if b == ord(",") and _nameable(st.tool, st.used):
            return replace(st, phase="arg_key")
        if b == ord("}"):
            if all(r in st.used for r in _required(st.tool)):
                return replace(st, phase="obj_close")
            return None
        return None

    if p == "obj_close":
        if b == SPACE:
            return st
        return replace(st, phase=DONE) if b == ord("}") else None

    return None  # DONE: the object is closed and nothing after it is ours


def accepts(text: str, copy: CopySpec | None = None,
            declared: tuple[str, ...] | None = None) -> bool:
    """Does the machine accept `text` as a complete call? Pure, for the guard."""
    st = State()
    for b in text.encode("utf-8"):
        if st.phase == DONE:
            return False  # trailing bytes past the close
        st = step(st, b, copy, declared)
        if st is None:
            return False
    return st.phase == DONE


# --------------------------------------------------------------------------
# The constraint
# --------------------------------------------------------------------------


class CallConstraint:
    """A logits processor that holds the model inside `step` while it writes a
    call, and lets go of it everywhere else.

    Arming is on the `<|call|>` token and nothing else. That marker is atomic
    in the BPE -- `train_bpe` strips the specials before counting pairs and
    gives each one an id above every merge -- so "the model has committed to a
    call" is a single id to watch for, and there is no partial-marker state to
    get wrong.

    The mask is built per *state*, not per step, and cached. Tokens are grouped
    by first byte at construction so a state that admits four bytes tests a few
    dozen tokens rather than the whole vocabulary; the string body admits
    nearly everything and is tested once for the whole note.

    `copy_slots` arms the span constraint. It needs a sentence to copy from, so
    `set_source` has to be called each turn -- until it is, `copy` is `None` and
    this is the schema constraint exactly as it was. The source joins the cache
    key for the same reason it joins `step`: the legal continuations of a
    half-written name are a property of the sentence, so masks cached under one
    utterance are wrong under the next.
    """

    def __init__(self, tok, device: str = "cpu", copy_slots=frozenset(),
                 narrow_slots=frozenset(),
                 declared: tuple[str, ...] | None = None):
        ids = tok.encode(D_CALL)
        if len(ids) != 1:
            raise ValueError(
                f"{D_CALL} is {len(ids)} tokens under {tok.name!r}, so there is no "
                f"single id to arm on. Grammar-constrained decoding needs the "
                f"markers atomic; run the agent with --no-grammar on this vocabulary."
            )
        self.arm_id = ids[0]
        self.vocab = tok.token_bytes()
        self.device = device

        # Every marker is off-limits inside a call: `<|obs|>` is printable
        # ASCII and would otherwise be a legal string body, which would end the
        # emission mid-object and hand `split_emission` a truncated call.
        specials = tuple(getattr(tok, "specials", ()))
        self.special_ids = frozenset(
            i for i, b in enumerate(self.vocab) if b.decode("utf-8", "replace") in specials
        )

        self._by_first: list[list[int]] = [[] for _ in range(256)]
        for i, b in enumerate(self.vocab):
            if b:
                self._by_first[b[0]].append(i)

        # **The one mask that costs the most is the one that forbids the least,
        # and this is the fix for it.** An unconstrained string body -- a
        # `save_note` text, a `web_search` query -- allows 8,147 of 8,192 tokens,
        # and the general path discovers that by calling `_allows` on the whole
        # vocabulary, stepping every byte of every token in Python. Measured at
        # **182 ms for that single state**, against 0.7-45 ms for the states
        # that actually constrain something, and the cache is discarded every
        # round because `set_source` puts a growing context in its key. Two
        # rounds of a `save_note` turn spend most of a 612 ms turn here.
        #
        # But legality in that state is a property of the *token*: every byte
        # from 0x20 up that is not a quote or a backslash keeps the machine in
        # `arg_str`, whatever the state's history and whatever the source. So
        # the set can be built once, here, and reused for every such state
        # forever.
        #
        # **It is a fast path and not an approximation.** Tokens carrying a
        # quote, a backslash or a control byte still go through `_allows` --
        # they are the ones that can close the string and walk on into another
        # slot, possibly a copy-constrained one, and only the general path knows
        # whether that is legal. The split is exact and
        # `scripts/check_grammar.py` compares the two paths token for token.
        self._plain: list[int] = []
        self._marked: list[int] = []
        for i, b in enumerate(self.vocab):
            if not b or i in self.special_ids:
                continue
            if all(x >= SPACE and x not in (QUOTE, BACKSLASH) for x in b):
                self._plain.append(i)
            else:
                self._marked.append(i)

        self.copy_slots = frozenset(copy_slots)
        # Copy slots whose source is *this turn* rather than the conversation.
        # See `CopySpec.narrow`: same mechanism, shorter reach, and the reach is
        # the whole difference between a contact the clarify path may copy out
        # of an earlier observation and a note that must not be.
        self.narrow_slots = frozenset(narrow_slots)
        self.copy: CopySpec | None = None
        # Validated here rather than at first use, so a typo in a declaration
        # fails when the constraint is built instead of mid-generation.
        self.declared = _names(declared) if declared is not None else None
        # `declared` joins the cache key for the reason `copy`'s source does:
        # the legal continuations of a half-written name are a property of the
        # offered set, so masks cached under one declaration are wrong under
        # another. It is a tuple of short strings and hashes cheaply.
        self._cache: dict[
            tuple[State, bytes, bytes, tuple[str, ...] | None], torch.Tensor] = {}
        # **The half of each cache that outlives a round.** Entries whose walk
        # never read the source (`_SourceWatch`) are keyed by state alone, so
        # they are still valid when `set_source` moves the conversation on.
        # On the tools corpus that is only **65 of 336 distinct states** --
        # the watch is conservative, and marks a state sensitive whenever any
        # token's walk so much as touches a slot -- but those 65 serve
        # **89.4% of all visits**, because they are the long unconstrained
        # string bodies. 400 calls walked as rounds: 70.7s -> 19.9s, 3.6x.
        # The source-keyed dicts above are cleared by `set_source`, because
        # once the source changes not one of their keys can ever match again;
        # before this split they were never cleared at all and grew a dead
        # vocab-wide tensor per state per round.
        self._mask_free: dict[
            tuple[State, tuple[str, ...] | None], torch.Tensor] = {}
        self._allowed_free: dict[
            tuple[State, tuple[str, ...] | None], list[int]] = {}
        # The id lists `_mask` is built from, cached under the same key. Kept
        # separately so `allowed_ids` can answer without materialising a
        # vocab-wide tensor on the device -- the forced-run check asks this
        # question once per token and must not pay for a mask to do it.
        self._allowed_cache: dict[
            tuple[State, bytes, bytes, tuple[str, ...] | None], list[int]] = {}
        self.reset()

    # --- state ------------------------------------------------------------

    def set_source(self, text: str, narrow: str | None = None) -> None:
        """Point the copy slots at the sentence this turn is answering.

        A no-op when no slots are constrained, which is what keeps the
        unconstrained path free of the source entirely rather than carrying one
        it never reads.

        `narrow` is the shorter source for `narrow_slots` -- the current turn,
        where `text` is the whole conversation below the declaration. Defaulting
        it to `text` rather than to empty is deliberate: a caller that arms a
        narrow slot and forgets to say what "this turn" is gets the old, wider
        behaviour, which is permissive rather than a mask that refuses
        everything mid-generation.
        """
        was = self.copy
        self.copy = (
            CopySpec(self.copy_slots, text.encode("utf-8"),
                     self.narrow_slots,
                     (text if narrow is None else narrow).encode("utf-8"))
            if self.copy_slots or self.narrow_slots else None
        )
        # Every source-keyed entry is now unreachable -- its key names the old
        # source and nothing will ask for that again. Dropping them here is
        # what keeps the cost of the split at zero: the source-free dicts are
        # bounded by the grammar (a few hundred states) and these are not.
        # By value, not identity: `set_source` with the same text twice is a
        # no-op and must not throw away a cache that is still valid for it.
        if was != self.copy:
            self._cache.clear()
            self._allowed_cache.clear()

    def reset(self) -> None:
        """Start a fresh generation. Disarmed; the cache and the source survive."""
        self.state: State | None = None
        self.bites: list[tuple[str, str, str]] = []
        self.released: str = ""
        # Set when a call has been written all the way to its closing brace.
        # `armed` cannot answer this -- it is False before the call starts and
        # False again after it ends -- and the runtime needs the difference to
        # know when there is nothing left to generate. See `_until_marker`.
        self.closed: bool = False

    def set_declared(self, declared: tuple[str, ...] | None) -> None:
        """Re-point the narrowing at a different offered set, in place.

        The declared set is a property of the *turn* -- `corn/toolspace.py`
        draws a fresh one per transcript -- so a scorer sweeping items has to
        change it 1,200 times. Rebuilding the constraint each time re-scans the
        whole vocabulary to fill `_by_first`, which is the expensive part of
        `__init__` and has nothing to do with the declaration.

        The mask cache survives on purpose: `declared` is already part of its
        key, precisely so masks built under one declaration cannot be served
        under another.
        """
        self.declared = _names(declared) if declared is not None else None

    @property
    def armed(self) -> bool:
        return self.state is not None

    def _in_copy_slot(self, st: State) -> bool:
        return (
            self.copy is not None
            and st.phase in ("arg_val", "arg_str")
            and self.copy.holds(st.tool, st.pending)
        )

    # --- masking ----------------------------------------------------------

    def _allows(self, st: State, raw: bytes) -> bool:
        for b in raw:
            if st.phase == DONE:
                return True  # past the close, the rest of the token is free
            st = step(st, b, self.copy, self.declared)
            if st is None:
                return False
        return True

    def allowed_ids(self, st: State) -> list[int] | None:
        """The token ids the grammar permits from `st`. `None` if nothing is.

        Split out of `_mask` rather than derived from it, because the *count*
        is what a decoder wants and counting zeros in a vocab-wide tensor on
        the device is a poor way to ask. A single-element list here means the
        next token is decided and the model cannot change it -- see
        `scripts/forced_token_survey.py`, and `decode.py`'s forced-run
        skipping, which is what reads this.

        A multi-token cache key: a state reached under one utterance can admit
        different continuations under another, and a token that walks *into* a
        copy slot is source-dependent from a state that is not yet in one. So
        an entry carries the source **when its walk actually read the source**,
        and is keyed by state alone when it did not -- see `_SourceWatch` for
        why that is sound and why the obvious static test is not. The
        source-free entries are the ones that survive `set_source`: a minority
        of the distinct states on the tools corpus (65 of 336) but the
        majority of the traffic through them (89.4% of visits), because the
        states that never read a source are the long unconstrained bodies.
        """
        free_key = (st, self.declared)
        hit = self._allowed_free.get(free_key)
        if hit is not None:
            return hit or None
        key = (st, self.copy.source if self.copy is not None else b"",
               self.copy.narrow_source if self.copy is not None else b"",
               self.declared)
        hit = self._allowed_cache.get(key)
        if hit is not None:
            return hit or None
        allowed, read_source = self._walk(st)
        if read_source:
            self._allowed_cache[key] = allowed
        else:
            self._allowed_free[free_key] = allowed
        return allowed or None

    def _walk(self, st: State) -> tuple[list[int], bool]:
        """The vocabulary walk, and whether it consulted the source.

        The spec is swapped for a watching one for the duration, so every
        route into it is covered -- `_allows` and `_in_copy_slot` reach it
        through `self.copy` rather than through an argument, and the
        `arg_str` fast path below reaches it only through `_allows`.

        Not reentrant, for the same reason: one constraint cannot be walked
        from two places at once. Nothing does -- a session is one turn at a
        time -- but a future batched scorer would need a spec per walk rather
        than a swap.
        """
        watch = _SourceWatch(self.copy) if self.copy is not None else None
        saved = self.copy
        if watch is not None:
            self.copy = watch
        try:
            if st.phase == "arg_str" and not self._in_copy_slot(st):
                # The fast path above. `_plain` is legal here by construction;
                # everything else still has to be walked, because a quote can
                # close the string and the rest of the token can go anywhere
                # after that.
                allowed = self._plain + [
                    i for i in self._marked if self._allows(st, self.vocab[i])
                ]
            else:
                allowed = [
                    i
                    for b in range(256)
                    if step(st, b, self.copy, self.declared) is not None
                    for i in self._by_first[b]
                    if i not in self.special_ids and self._allows(st, self.vocab[i])
                ]
        finally:
            self.copy = saved
        return allowed, watch is not None and watch.read

    def _mask(self, st: State) -> torch.Tensor | None:
        """`-inf` everywhere the grammar forbids, 0 elsewhere. None if nothing
        is allowed, which releases rather than deadlocks.
        """
        free_key = (st, self.declared)
        hit = self._mask_free.get(free_key)
        if hit is not None:
            return hit
        key = (st, self.copy.source if self.copy is not None else b"",
               self.copy.narrow_source if self.copy is not None else b"",
               self.declared)
        hit = self._cache.get(key)
        if hit is not None:
            return hit
        allowed = self.allowed_ids(st)
        if allowed is None:
            return None
        m = torch.full((len(self.vocab),), float("-inf"), device=self.device)
        m[torch.tensor(allowed, dtype=torch.long, device=self.device)] = 0.0
        # `allowed_ids` has just decided which side this state falls on and
        # cached the ids there; the mask follows its ids rather than deciding
        # again, so the two dicts can never disagree about one state.
        if free_key in self._allowed_free:
            self._mask_free[free_key] = m
        else:
            self._cache[key] = m
        return m

    def __call__(self, logits: torch.Tensor) -> torch.Tensor:
        """Apply the constraint to the last position's logits.

        Records a bite whenever the unconstrained argmax was one of the tokens
        it just removed. That comparison is the entire instrument and costs one
        argmax on the steps where the constraint is armed at all.

        A bite carries *where* it happened, and that is not bookkeeping. A bite
        in a copy slot is the model reaching for a name the user did not say --
        gap 3 caught in the act, on a turn that would otherwise have looked like
        a success. A bite anywhere else is gap 4. Merging them would report the
        two failures the project has measured separately as one number.
        """
        if self.state is None:
            return logits
        m = self._mask(self.state)
        if m is None:
            self.released = "no token can continue the call"
            self.state = None
            return logits
        wanted = int(logits.argmax(dim=-1).reshape(-1)[-1])
        out = logits + m
        took = int(out.argmax(dim=-1).reshape(-1)[-1])
        if took != wanted:
            where = self.state.pending if self._in_copy_slot(self.state) else ""
            self.bites.append((self._show(wanted), self._show(took), where))
        return out

    def _show(self, tid: int) -> str:
        return self.vocab[tid].decode("utf-8", "replace") if 0 <= tid < len(self.vocab) else "?"

    # --- the token stream -------------------------------------------------

    def accept(self, tid: int) -> None:
        """Advance on a token the decoder has committed to."""
        if self.state is None:
            if tid == self.arm_id:
                self.state = State()
            return
        st = self.state
        for b in self.vocab[tid]:
            if st.phase == DONE:
                break
            st = step(st, b, self.copy, self.declared)
            if st is None:
                # Only reachable if something sampled outside the mask -- a
                # prefill, or a graph with sampling captured inside it. Release
                # rather than pretend, and say so in the transcript.
                self.released = "an unmasked token left the grammar"
                self.state = None
                return
        if st.phase == DONE:
            self.closed = True
        self.state = None if st.phase == DONE else st


# --------------------------------------------------------------------------
# The parse line -- a second, much smaller machine
# --------------------------------------------------------------------------
#
# **The same two guarantees the call object gets, applied to `parts:`.**
# PLAN-DECOMPOSE §4 asks for exactly these and both are byte-level facts rather
# than post-hoc validation:
#
#   * **A label is one of a closed set**, so a malformed parse is impossible
#     rather than something the runtime has to survive. Finding 34's own
#     recommendation, one level up from the tool name.
#   * **A span is a word-bounded contiguous substring of its parent**, which is
#     `CopySpec`'s constraint with the parent line as the source instead of the
#     user's utterance. Ground rule 2, and it bans nothing `corn/decompgen.py`
#     writes -- `scripts/check_decompose.py` reads that off every transcript on
#     disk rather than taking it on trust.
#
# **What this is not wired to yet, said plainly.** No checkpoint emits a
# `parts:` line, so nothing in `corn/agent.py` arms this. It exists now because
# the constraint is what makes the format *checkable* -- `parse_accepts` is what
# the guard and `scripts/forced_token_survey.py` drive -- and because building
# it after a corpus trained would mean discovering at serve time that the format
# admits something the corpus never wrote. The runtime hook is
# PLAN-DECOMPOSE §9's and lands with rung 2.
#
# **Arming is on a line, not on a marker, and that is the cost of rule 3.**
# `<|call|>` is one token, so "the model has committed to a call" is a single id
# to watch for. `parts: ` is plain text, so a runtime that armed this would have
# to do it after a newline and disarm on the next one. That is a real difference
# from `CallConstraint` and it is why the arming code is not written here on
# speculation.


class ParseState(NamedTuple):
    """One position inside a `parts:` or `move:` line."""

    phase: str = "prefix"
    prefix: str = ""      # partial match inside a literal or a label
    span: bytes = b""     # the current span's bytes so far
    n: int = 0            # spans closed so far, for the arity rule


def replace_parse(st: ParseState, **changes) -> ParseState:
    return st._replace(**changes)


def _plit(st: ParseState, b: int, text: str, nxt: str) -> ParseState | None:
    """Consume a fixed prefix one byte at a time. No spaces allowed before it:
    a parse line begins at the start of a line and nowhere else."""
    want = text[len(st.prefix)]
    if b != ord(want):
        return None
    prefix = st.prefix + want
    if len(prefix) == len(text):
        return replace_parse(st, phase=nxt, prefix="")
    return replace_parse(st, prefix=prefix)


def parse_step(st: ParseState, b: int, parent: bytes,
               labels: tuple[str, ...] = PARSE_LABELS,
               line: str = "parts") -> ParseState | None:
    """Consume one byte of a parse line, or None if the grammar forbids it.

    `parent` is what every span must be a word-bounded substring of -- the
    utterance at level 1, the parent part's span below that. `line` selects the
    two shapes: `parts` is `label[span]` repeated, `move` is one value of
    `MOVES_1_0` (the seven and `share`, D-A1.22).
    """
    if line == "move":
        if st.phase == "prefix":
            return _plit(st, b, MOVE_PREFIX, "value")
        if st.phase == "value":
            if b == 0x0A:
                return replace_parse(st, phase=DONE) if st.prefix in MOVES_1_0 else None
            if b >= 128:
                return None
            cand = st.prefix + chr(b)
            if any(m.startswith(cand) for m in MOVES_1_0):
                return replace_parse(st, prefix=cand)
            return None
        return None

    if st.phase == "prefix":
        return _plit(st, b, PARTS_PREFIX, "label")
    if st.phase == "label":
        if b >= 128:
            return None
        if b == ord("["):
            # The bracket is legal exactly where the label is complete, which
            # is the last moment a half-written label can be refused.
            if st.prefix in labels:
                return replace_parse(st, phase="span", prefix="", span=b"")
            return None
        cand = st.prefix + chr(b)
        if any(lab.startswith(cand) for lab in labels):
            return replace_parse(st, prefix=cand)
        return None
    if st.phase == "span":
        if b == ord("]"):
            # The closing bracket is legal only where the span is complete --
            # word-bounded at both edges -- which is what refuses `Ophel` in
            # `CopySpec` and refuses half a carrier here.
            if st.span and span_ok(parent, st.span, closing=True):
                return replace_parse(st, phase="after", span=b"", n=st.n + 1)
            return None
        if b in (ord("["), 0x0A):
            return None
        nxt = st.span + bytes([b])
        if span_ok(parent, nxt, closing=False):
            return replace_parse(st, span=nxt)
        return None
    if st.phase == "after":
        # A space opens another part; a newline closes the line. `n` is what
        # stops an empty `parts:` line being a legal parse.
        if b == SPACE:
            return replace_parse(st, phase="label", prefix="")
        if b == 0x0A:
            return replace_parse(st, phase=DONE) if st.n else None
        return None
    return None


def _nested_nodes(body: str, labels: tuple[str, ...]):
    """`(nodes, span)` for a nested body, or None if it is malformed.

    `nodes` is `(label, span, children)` for each node at this level; `span` is
    the text this level claims of its parent -- its own literal words with each
    child's span in place, which is built as the scan runs rather than
    reconstructed afterwards.
    """
    out, lit = [], []
    i, n = 0, len(body)
    while i < n:
        j = i
        while j < n and body[j].isalnum():
            j += 1
        if j > i and j < n and body[j] == "[":
            label = body[i:j]
            if label not in labels:
                return None
            depth, k = 1, j + 1
            while k < n and depth:
                if body[k] == "[":
                    depth += 1
                elif body[k] == "]":
                    depth -= 1
                k += 1
            if depth:
                return None
            sub = _nested_nodes(body[j + 1:k - 1], labels)
            if sub is None:
                return None
            kids, span = sub
            out.append((label, span, kids))
            lit.append(span)
            i = k
        else:
            if body[i] == "]":
                return None
            lit.append(body[i])
            i += 1
    return out, "".join(lit)


def _nested_fits(nodes, parent: str) -> bool:
    """Every node's span contiguous, word-bounded and in order inside `parent`.

    Gaps between siblings are legal at every level and are not a laxity: at the
    top they are the joiner between parts, and below it they are the group
    carrier that wraps its members -- `ask[the lot, ask[..], ask[..] and ask[..]]`
    keeps `the lot,` and ` and ` for itself. Of 192 cut rows only 57 tile the
    utterance exactly; the other 135 differ from it by exactly that text. What
    is enforced is order, containment and word-boundedness, which is
    `parse_step`'s rule applied at every depth rather than only at one.
    """
    src = parent.encode("utf-8")
    at = 0
    for _label, span, kids in nodes:
        raw = span.encode("utf-8")
        if not raw:
            return False
        i = src.find(raw, at)
        if i < 0 or not span_ok(src, raw, closing=True):
            return False
        if not _nested_fits(kids, span):
            return False
        at = i + len(raw)
    return True


def nested_accepts(text: str, utterance: str,
                   labels: tuple[str, ...] = PARSE_LABELS) -> bool:
    """Does the machine accept `text` as a complete *nested* parse line?

    PLAN-PARSE-WEIGHTS arm F. `parse_step` above is flat by construction -- one
    `parent`, and `[` refused inside a span -- because a line-per-level parse
    never nests. The nested form writes the tree on one line, so the same two
    rules hold at every depth: a label is one of the closed set, and a span is a
    contiguous word-bounded substring of **its parent**, which is the utterance
    at the top and the enclosing node's span below it.

    Kept apart from `ParseConstraint` and written pure rather than as a decode
    hook, for that class's own stated reason -- a second implementation of a hot
    loop is a second thing to keep correct -- and because it is only needed
    where a bound column is reported beside a free one. Arm F's gate is the
    teacher-forced fork, which decodes nothing.
    """
    if not text.startswith(PARTS_PREFIX) or not text.endswith("\n"):
        return False
    got = _nested_nodes(text[len(PARTS_PREFIX):-1], labels)
    if got is None or not got[0]:
        return False
    return _nested_fits(got[0], utterance)


def parse_accepts(text: str, parent: str,
                  labels: tuple[str, ...] = PARSE_LABELS,
                  line: str = "parts") -> bool:
    """Does the machine accept `text` as a complete line? Pure, for the guard.

    `text` carries its trailing newline, because the newline is what closes the
    line -- a parse that has not ended is not yet a parse.
    """
    st = ParseState()
    src = parent.encode("utf-8")
    for b in text.encode("utf-8"):
        if st.phase == DONE:
            return False
        st = parse_step(st, b, src, labels, line)
        if st is None:
            return False
    return st.phase == DONE


class ParseConstraint:
    """`CallConstraint`'s shape for the parse line, at a tenth the size.

    Deliberately not a subclass and deliberately not sharing that class's
    cache: the call constraint's machinery exists to make a 60-byte note body
    affordable, a parse line is short, and a second implementation of a hot
    loop is a second thing to keep correct. `scripts/forced_token_survey.py`
    drives this the same way it drives the call constraint.

    `set_parent` is `set_source`'s counterpart -- the string every span on this
    line must be a substring of.

    **Every line of the language rides this one class** (SPEC-LANGUAGE §9).
    `line="nested"` is the one-line tree (`nested_step`, the utterance as
    `parent`). The trace and template lines carry more than one source -- a
    `goal:` reads the observation's keys and the request, a `pick:` each
    item's text -- so they come in as `step` and `start`: a closure over the
    sources and the state it begins in. Build one per line; its cache is then
    keyed correctly by the state alone, because the sources cannot change
    under it.
    """

    def __init__(self, tok, device: str = "cpu",
                 labels: tuple[str, ...] = PARSE_LABELS, line: str = "parts",
                 step=None, start=None):
        self.vocab = tok.token_bytes()
        self.device = device
        self.labels = labels
        self.line = line
        self._step = step
        self._start = start
        specials = tuple(getattr(tok, "specials", ()))
        self.special_ids = frozenset(
            i for i, b in enumerate(self.vocab)
            if b.decode("utf-8", "replace") in specials)
        self.parent = b""
        self._cache: dict[tuple[ParseState, bytes], list[int]] = {}
        self.reset()

    def set_parent(self, text: str) -> None:
        if text.encode("utf-8") != self.parent:
            self.parent = text.encode("utf-8")
            self._cache.clear()

    def reset(self) -> None:
        if self._start is not None:
            self.state = self._start
        elif self.line == "nested":
            self.state = NestedState()
        else:
            self.state = ParseState()
        self.closed = False

    def _walk(self, st, raw: bytes):
        for b in raw:
            if st.phase == DONE:
                return None
            if self._step is not None:
                st = self._step(st, b)
            elif self.line == "nested":
                st = nested_step(st, b, self.parent, self.labels)
            else:
                st = parse_step(st, b, self.parent, self.labels, self.line)
            if st is None:
                return None
        return st

    def allowed_ids(self, st: ParseState) -> list[int]:
        key = (st, self.parent)
        hit = self._cache.get(key)
        if hit is None:
            hit = [i for i, raw in enumerate(self.vocab)
                   if raw and i not in self.special_ids
                   and self._walk(st, raw) is not None]
            self._cache[key] = hit
        return hit

    def accept(self, tid: int) -> None:
        if self.state is None:
            return
        st = self._walk(self.state, self.vocab[tid])
        if st is None:
            self.state = None
            return
        if st.phase == DONE:
            self.closed = True
            self.state = None
        else:
            self.state = st


# --------------------------------------------------------------------------
# The language's lines at decode -- SPEC-LANGUAGE §9
# --------------------------------------------------------------------------
#
# **Every line the spec marks as his, as a machine that refuses the illegal
# byte.** `nested_accepts` above answers "is this a legal tree" once the line
# is finished; a decoder needs the same answer one byte at a time, which is
# what makes a repeat, a splice, an invented span or an unbalanced bracket
# impossible rather than something the runtime survives (PLAN-TAG-LANGUAGE
# rung 0). The trace and template lines (`goal:`, `pick:`, `use:`) get the
# same treatment, each bound to the source the spec names for it.
#
# **The nested line is simpler to stream than it looks.** A node's span is its
# own words with every child's span in place (`_nested_nodes`), so a child is
# inside its parent by construction once the bracketed text is read with the
# brackets removed. What must be held byte by byte is: a label at every `[`;
# each *top-level* part's words, brackets removed, a word-bounded substring of
# the utterance at or after the previous part's end; every `[` and `]` on a
# word edge of those words; brackets balanced before the newline.
#
# **Deliberately stricter than `nested_accepts` in four places, and never
# looser but for case.** Top-level parts are joined by exactly one space, as
# `decompgen.parts_nested` writes them -- the pure check lets any literal text
# sit between them. A child's edges are checked where the child actually
# sits, not at any occurrence of its words in the parent. And the order check
# lets a capital be copied lowercase -- `span_ok`'s reason, folded one way
# only (`_occurs` says why) --
# where `_nested_fits`'s `find` does not. And no more than `MAX_OPEN_RUN`
# labels open in a row, the training data's own ceiling (its comment says
# why). `scripts/check_grammar.py` group 12
# asserts the containment on every generated tree and on mutations of them.
#
# **No legal prefix strands the line** -- or none rung 0 found. A grammar
# checked only on finished lines can admit a prefix with no legal next byte,
# and a decoder bound to it stops dead there: on the first bound read of arm
# F, 219 of 576 ladder lines did. Three refusals close what the reads showed,
# and each refuses only a prefix that no legal line extends: a bracket
# between word bytes needs a word edge somewhere these words sit in the
# request (`_edge_ahead`), a second top-level part needs words the request
# still has, and so does a child (`_room_ahead`, finding 147 -- the third,
# found on the full read). The decoder in `scripts/probe_nestgen.py`
# backtracks as well, for any state these do not cover; its item files count
# the pops.
#
# **A bare label is the whole utterance** (SPEC-LANGUAGE D-A1.4): `parts:
# chat` is legal as the entire line and nowhere else. The bracketed form of a
# single whole-utterance part stays legal too, because arm F and G2 wrote it
# and rung 0 reads those checkpoints; the 1.0 corpus writes the bare one.

# The operators a hard goal term may use, longest first so a prefix test reads
# `<=` before `<`.
GOAL_OPS: tuple[str, ...] = ("<=", ">=", "!=", "<", ">", "=")
_OP_BYTES = frozenset(b"<>=!")
# The fourth place the stream is stricter than `nested_accepts`: at most three
# labels open with no word between them (`ask[ask[ask[the ...`). Without it a
# label is always legal, so when the model's next word is refused -- it wants
# to skip words, which free decoding writes as an invented span -- the open
# outranks the right word and the line runs away (`ask[ask[ask[ask[find[...`
# to the token limit), on the first rung 0 decodes of arm F. Three is the
# training data's own maximum: 108 lines of `funcworld_armf.txt` open three in
# a row and none opens four. Depth is not capped; it stays readable.
MAX_OPEN_RUN = 3
GOAL_PREFIX = "goal: "
PICK_PREFIX = "pick: "
USE_PREFIX = "use: "
BECAUSE = "because["


class NestedState(NamedTuple):
    """One position inside a nested `parts:` line."""

    phase: str = "prefix"          # prefix | top | span | after | done
    prefix: str = ""               # partial match inside the line prefix or a top label
    pend: bytes = b""              # a word run not yet known to be a label or words
    text: bytes = b""              # the open top part's words, brackets removed
    opens: tuple[int, ...] = ()    # where each open part's span starts in `text`
    edge: bool = False             # the next word byte may not follow here
    at: int = 0                    # where in the utterance the next top part may start
    n: int = 0                     # top-level parts closed


def _occurs(source: bytes, value: bytes, at: int, closing: bool) -> int:
    """Where `value` sits in `source` at or after `at`, word-bounded, or -1.

    `span_ok` with a start offset and an answer: the start edge always, the
    end edge too when `closing`.

    **Case folds one way only: a capital may be copied lowercase.** That is
    the whole of `span_ok`'s reason -- a person writes "How", he opens with
    "how" -- and the reverse has none. Folded both ways, a decoder bound to
    this line spelled its way round the copy rule once every other way out
    was shut: 117 of 576 ladder lines on arm F came back as `fIniSh`,
    `gaRaendvik`, `mEasurE` on rung 0's third read.
    """
    if not value:
        return -1 if closing else at
    low = source.lower()
    i = low.find(value.lower(), at)
    while i >= 0:
        if any(v != s and v != s + 32 for v, s in zip(value, source[i:i + len(value)])):
            i = low.find(value.lower(), i + 1)
            continue
        if i == 0 or not _wordish(source[i - 1]) or not _wordish(value[0]):
            if not closing:
                return i
            j = i + len(value)
            if j == len(source) or not _wordish(source[j]) or not _wordish(value[-1]):
                return i
        i = low.find(value.lower(), i + 1)
    return -1


def _copied(source: bytes, value: bytes, closing: bool) -> bool:
    """`span_ok` for the trace lines, with case copied one way (D-A1.14).

    `goal:`'s values and `soft[...]` copy from the request and `pick:`'s
    `because[...]` from the picked item's text, and each was bound by
    `span_ok`, which folds case both ways. The first stub decode of rung 3's
    probe (G3, 2026-10-02) aimed a pick at the wrong words and got
    `because[ A FORMER CHAPEL, BY THE MARKET SQUARE]` -- legal, and the same
    spelling-round the nested line did before `_occurs`. Every trace of
    `data/raw/funcworld_filter.txt` and every row of
    `evals/funcworld_filter.jsonl` still passes (`scripts/check_filter.py`),
    so this refuses nothing a legal line needs.
    """
    return _occurs(source, value, 0, closing) >= 0


def _phrase(source: bytes, value: bytes, closing: bool) -> bool:
    """`_copied` for a bracketed phrase -- `soft[...]`, `because[...]` -- that
    also starts on a word byte and closes on one.

    With capitals shut, the same stub decode found the next way round:
    `because[ ]` and `because[the ]`, a space being a word-bounded span of any
    text. A phrase of no words is evidence of nothing. No line in the filter
    world's file or rows starts or ends either bracket on a non-word byte, so
    this too refuses nothing legal; `goal:`'s hard value keeps `_copied`
    alone, since a value may yet carry a sign or a symbol.
    """
    if value and not _wordish(value[0]):
        return False
    if closing and value and not _wordish(value[-1]):
        return False
    return _copied(source, value, closing)


def _nest_words(st: NestedState, chunk: bytes, utterance: bytes) -> NestedState | None:
    """Add `chunk` to the open top part's words, if they stay a legal span."""
    if st.edge and _wordish(chunk[0]):
        return None
    text = st.text + chunk
    if _occurs(utterance, text, st.at, closing=False) < 0:
        return None
    return st._replace(text=text, pend=b"", edge=False)


def _open_run(st: NestedState) -> int:
    """Labels open with no word after them. A space or a dash does not end the
    run: when it did, the runaway fed on the request's own punctuation --
    `find[ask[ask[-find[ask[ask[ the population` -- on rung 0's first read."""
    run = 0
    for o in reversed(st.opens):
        if any(_wordish(c) for c in st.text[o:]):
            break
        run += 1
    return run


def _edge_ahead(st: NestedState, utterance: bytes) -> bool:
    """Can a word edge stand right after the words so far?

    A bracket between two word bytes sets `edge`, and the next word byte is
    then refused. If the request continues the word at every place these words
    sit -- `ask[f]` where it reads "four" -- nothing legal can follow, and the
    line is stranded: 219 of 576 bound ladder lines on arm F stopped dead so on
    rung 0's first read. Every legal completion needs this edge, so refusing
    the bracket refuses nothing `nested_accepts` takes.
    """
    return _occurs(utterance, st.text, st.at, closing=True) >= 0


def _room_ahead(st: NestedState, utterance: bytes) -> bool:
    """Can a child opened here still get a span?

    A child's span extends the words so far, contiguously, so it needs a byte
    of the request after them; the first place they sit leaves the most room.
    Past the request's last byte a label opens a child nothing can fill, and
    every way on strands -- the top-level space had this refusal and a child
    did not: on rung 0's full read (finding 147) a seed that ranks a fresh
    label above the closing bracket at the request's end wrote
    `the three of them]]]]social[follow[fi`, and the backtracking decoder
    spent its whole budget (345-424 pops a line) walking the label stacks
    behind it -- 94 of 107 unbalanced bound ladder lines on G2 seed 2.
    """
    i = _occurs(utterance, st.text, st.at, closing=False)
    return 0 <= i and i + len(st.text) < len(utterance)


def nested_step(st: NestedState, b: int, utterance: bytes,
                labels: tuple[str, ...] = PARSE_LABELS) -> NestedState | None:
    """Consume one byte of a nested `parts:` line, or None if it is illegal."""
    if st.phase == "prefix":
        return _plit(st, b, PARTS_PREFIX, "top")
    if st.phase == "top":
        # A top-level label: a bracket opens its part, a newline closes the
        # line on a bare label, which is only legal as the whole line.
        if b == ord("["):
            if st.prefix in labels:
                return st._replace(phase="span", prefix="", text=b"", opens=(0,),
                                   edge=False, pend=b"")
            return None
        if b == 0x0A:
            return st._replace(phase=DONE) if st.n == 0 and st.prefix in labels else None
        if b >= 128:
            return None
        cand = st.prefix + chr(b)
        return st._replace(prefix=cand) if any(lab.startswith(cand) for lab in labels) else None
    if st.phase == "after":
        if b == SPACE:
            # Another part needs words the request still has; past its last
            # word the space strands the line (`droaelvmar]]] do[follow[`).
            if not any(_wordish(c) for c in utterance[st.at:]):
                return None
            return st._replace(phase="top", prefix="")
        return st._replace(phase=DONE) if b == 0x0A else None
    if st.phase != "span":
        return None

    if _wordish(b):
        # Held back until the run ends: a run before `[` is a label and never
        # enters the words, a run before anything else is words. Legal while
        # either reading can still hold.
        pend = st.pend + bytes([b])
        # A run that can only end in a refused `[` is a dead end, not a label.
        as_label = (pend.isascii() and _open_run(st) < MAX_OPEN_RUN
                    and any(lab.startswith(pend.decode()) for lab in labels)
                    and _room_ahead(st, utterance))
        if as_label or _nest_words(st, pend, utterance) is not None:
            return st._replace(pend=pend)
        return None
    if b == ord("["):
        if not st.pend.isascii() or st.pend.decode() not in labels:
            return None
        if _open_run(st) >= MAX_OPEN_RUN or not _room_ahead(st, utterance):
            return None
        # A child that does not open its parent's span starts on a word edge.
        edge = st.edge or (len(st.text) > st.opens[-1] and _wordish(st.text[-1]))
        if edge and not _edge_ahead(st, utterance):
            return None
        return st._replace(pend=b"", opens=st.opens + (len(st.text),), edge=edge)
    if b == ord("]"):
        if st.pend:
            st = _nest_words(st, st.pend, utterance)
            if st is None:
                return None
        if len(st.text) == st.opens[-1]:
            return None                     # an empty span
        opens = st.opens[:-1]
        if not opens:
            # The top part closes: its words, whole, word-bounded, in order.
            i = _occurs(utterance, st.text, st.at, closing=True)
            if i < 0:
                return None
            return NestedState(phase="after", at=i + len(st.text), n=st.n + 1)
        if _wordish(st.text[-1]) and not _edge_ahead(st, utterance):
            return None
        return st._replace(opens=opens, edge=_wordish(st.text[-1]))
    if b == 0x0A:
        return None
    return _nest_words(st, st.pend + bytes([b]), utterance)


def _run(step, start, text: str) -> bool:
    """Does `step` accept `text` as one complete line from `start`? Pure."""
    st = start
    for b in text.encode("utf-8"):
        if st.phase == DONE:
            return False
        st = step(st, b)
        if st is None:
            return False
    return st.phase == DONE


def nested_line_accepts(text: str, utterance: str,
                        labels: tuple[str, ...] = PARSE_LABELS) -> bool:
    """The streaming machine's verdict on a whole nested line, newline included."""
    src = utterance.encode("utf-8")
    return _run(lambda st, b: nested_step(st, b, src, labels), NestedState(), text)


# -- `use:` and a pick from a menu: one value from a set the runtime shows ----


def choice_step(st: ParseState, b: int, key: str,
                options: tuple[str, ...]) -> ParseState | None:
    """One value of `options` after `key`, then a newline.

    `use: <name>` over the templates a frame shows plus `none` (spec §7), and
    `pick: <move>` over an `options:` line (spec §6, D-A1.8).
    """
    if st.phase == "prefix":
        return _plit(st, b, key, "value")
    if st.phase != "value":
        return None
    if b == 0x0A:
        return replace_parse(st, phase=DONE) if st.prefix in options else None
    if b >= 128:
        return None
    cand = st.prefix + chr(b)
    return replace_parse(st, prefix=cand) if any(o.startswith(cand) for o in options) else None


def use_accepts(text: str, names: tuple[str, ...]) -> bool:
    options = tuple(names) + ("none",)
    return _run(lambda st, b: choice_step(st, b, USE_PREFIX, options), ParseState(), text)


# Arms UD-id and UD-ev (`corn/templategen.py`, owner 2026-10-02): the frame
# shows `template <i>: use when <text>` lines, no names. Opt-in, and no change
# to `choice_step`: it already binds any ASCII option set, so each format's
# bind is the same machine over a different menu. `id`: a shown id or `none`.
# `ev`: `because[<a shown use when, whole>] <its own id>` or `none` -- the
# menu is the pairs, so a description copied with another template's id, a
# part of one, or one reordered is not on it. `check_grammar.py` group 12
# pins the refusals; `check_templates.py` section 8 runs every corpus line
# and every eval option through it.


def use_id_options(n: int) -> tuple[str, ...]:
    return tuple(str(i) for i in range(1, n + 1)) + ("none",)


def use_ev_options(use_whens: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"{BECAUSE}{uw}] {i}" for i, uw in enumerate(use_whens, 1)) + ("none",)


def use_id_accepts(text: str, n: int) -> bool:
    options = use_id_options(n)
    return _run(lambda st, b: choice_step(st, b, USE_PREFIX, options), ParseState(), text)


def use_ev_accepts(text: str, use_whens: tuple[str, ...]) -> bool:
    options = use_ev_options(tuple(use_whens))
    return _run(lambda st, b: choice_step(st, b, USE_PREFIX, options), ParseState(), text)


# Arm US (`corn/templategen.py`, probe only, 2026-10-02): the runtime has
# filtered domain and field, so the shown templates differ only in their soft
# concept clause, and he writes `because[<a shown concept clause>] <its own
# id>`. The menu is those pairs and **no `none`** -- in this arm `none` is the
# runtime's (nothing passed its checks, no frame is built). Opt-in; the same
# `choice_step` over a different menu. `check_grammar.py` group 12 pins the
# refusals; `check_templates.py` section 9 runs every corpus line and every
# eval option through it.


def use_us_options(concept_clauses: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"{BECAUSE}{c}] {i}" for i, c in enumerate(concept_clauses, 1))


def use_us_accepts(text: str, concept_clauses: tuple[str, ...]) -> bool:
    options = use_us_options(tuple(concept_clauses))
    return _run(lambda st, b: choice_step(st, b, USE_PREFIX, options), ParseState(), text)


# Arm USN (`corn/templategen.py`, probe only, 2026-10-02): arm US plus a soft
# `none` -- every shown template passes the runtime's checks and none of their
# concept clauses answers the request's soft term. The menu is US's pairs and
# `none`, on USN frames only: `use_us_accepts` still refuses `none`. Opt-in;
# the same `choice_step`. `check_grammar.py` group 12 pins the refusals;
# `check_templates.py` section 10 runs every corpus line and every eval option
# through it.


def use_usn_options(concept_clauses: tuple[str, ...]) -> tuple[str, ...]:
    return use_us_options(tuple(concept_clauses)) + ("none",)


def use_usn_accepts(text: str, concept_clauses: tuple[str, ...]) -> bool:
    options = use_usn_options(tuple(concept_clauses))
    return _run(lambda st, b: choice_step(st, b, USE_PREFIX, options), ParseState(), text)


# -- `goal:` -- fields from the observation, values from the request ---------


def goal_step(st: ParseState, b: int, request: bytes,
              fields: tuple[str, ...]) -> ParseState | None:
    """Consume one byte of a `goal:` line (spec §6, D-A1.5).

    Terms, space-joined: `field op value` with the value a word-bounded span
    of the request holding no space; `assume[field op value]` with the value
    free; `soft[span]` with the span a word-bounded span of the request.
    `fields` are the keys the observed items carry. `ParseState.span` holds a
    value or span as it grows and `prefix` a name or an operator.
    """
    ph = st.phase
    if ph == "prefix":
        return _plit(st, b, GOAL_PREFIX, "head")
    if ph in ("head", "afield"):
        names = fields if ph == "afield" else fields + ("soft", "assume")
        if b in _OP_BYTES:
            if st.prefix in fields and any(o.startswith(chr(b)) for o in GOAL_OPS):
                return replace_parse(st, phase="op" if ph == "head" else "aop",
                                     prefix=chr(b))
            return None
        if b == ord("[") and ph == "head":
            if st.prefix == "soft":
                return replace_parse(st, phase="soft", prefix="", span=b"")
            if st.prefix == "assume":
                return replace_parse(st, phase="afield", prefix="")
            return None
        if b >= 128 or b in (SPACE, 0x0A) or b in b"[]":
            return None
        cand = st.prefix + chr(b)
        return replace_parse(st, prefix=cand) if any(x.startswith(cand) for x in names) else None
    if ph in ("op", "aop"):
        if b in _OP_BYTES and any(o.startswith(st.prefix + chr(b)) for o in GOAL_OPS):
            return replace_parse(st, prefix=st.prefix + chr(b))
        if st.prefix not in GOAL_OPS:
            return None
        nxt = "value" if ph == "op" else "avalue"
        return goal_step(replace_parse(st, phase=nxt, prefix="", span=b""), b, request, fields)
    if ph == "value":
        if b in (SPACE, 0x0A):
            if not st.span or not _copied(request, st.span, closing=True):
                return None
            if b == SPACE:
                return replace_parse(st, phase="head", prefix="", span=b"", n=st.n + 1)
            return replace_parse(st, phase=DONE, span=b"", n=st.n + 1)
        if b in b"[]":
            return None
        nxt = st.span + bytes([b])
        return replace_parse(st, span=nxt) if _copied(request, nxt, closing=False) else None
    if ph == "avalue":
        if b == ord("]"):
            return replace_parse(st, phase="sep", span=b"") if st.span else None
        if b in (SPACE, 0x0A) or b == ord("["):
            return None
        return replace_parse(st, span=st.span + bytes([b]))
    if ph == "soft":
        if b == ord("]"):
            if st.span and _phrase(request, st.span, closing=True):
                return replace_parse(st, phase="sep", span=b"")
            return None
        if b in (0x0A, ord("[")):
            return None
        nxt = st.span + bytes([b])
        return replace_parse(st, span=nxt) if _phrase(request, nxt, closing=False) else None
    if ph == "sep":
        if b == SPACE:
            return replace_parse(st, phase="head", prefix="", n=st.n + 1)
        return replace_parse(st, phase=DONE, n=st.n + 1) if b == 0x0A else None
    return None


def goal_accepts(text: str, request: str, fields: tuple[str, ...]) -> bool:
    req = request.encode("utf-8")
    return _run(lambda st, b: goal_step(st, b, req, tuple(fields)), ParseState(), text)


# -- `pick:` -- an ok item and the evidence from its own observation ---------


class PickState(NamedTuple):
    """One position inside a `pick:` line over items."""

    phase: str = "prefix"             # prefix | id | because | evidence | sep | done
    prefix: str = ""
    span: bytes = b""
    picked: tuple[str, ...] = ()


def pick_step(st: PickState, b: int, ok: tuple[str, ...], texts,
              because: bool) -> PickState | None:
    """Consume one byte of a `pick:` line over observed items (spec §6, D-A1.6).

    `ok` are the ids `check:` marked ok; `texts` maps each id to its item's
    observation text as bytes; `because` is whether the goal held a soft term,
    which is when `because[span]` is required -- and absent otherwise. `none`
    is legal as the whole line. A menu pick is `choice_step`, not this.
    """
    ph = st.phase
    if ph == "prefix":
        return _plit(st, b, PICK_PREFIX, "id")
    if ph == "id":
        if b in (SPACE, 0x0A):
            if st.prefix == "none" and not st.picked:
                return st._replace(phase=DONE, prefix="") if b == 0x0A else None
            if st.prefix not in ok or st.prefix in st.picked:
                return None
            picked = st.picked + (st.prefix,)
            if because:
                return st._replace(phase="because", prefix="", picked=picked) if b == SPACE else None
            if b == SPACE:
                return st._replace(prefix="", picked=picked)
            return st._replace(phase=DONE, prefix="", picked=picked)
        if b >= 128:
            return None
        cand = st.prefix + chr(b)
        live = [i for i in ok if i not in st.picked]
        if not st.picked:
            live.append("none")
        return st._replace(prefix=cand) if any(i.startswith(cand) for i in live) else None
    if ph == "because":
        return _plit(st, b, BECAUSE, "evidence")
    if ph == "evidence":
        src = texts[st.picked[-1]]
        if b == ord("]"):
            if st.span and _phrase(src, st.span, closing=True):
                return st._replace(phase="sep", span=b"")
            return None
        if b in (0x0A, ord("[")):
            return None
        nxt = st.span + bytes([b])
        return st._replace(span=nxt) if _phrase(src, nxt, closing=False) else None
    if ph == "sep":
        if b == SPACE:
            return st._replace(phase="id", prefix="")
        return st._replace(phase=DONE) if b == 0x0A else None
    return None


def pick_accepts(text: str, ok: tuple[str, ...], texts, because: bool) -> bool:
    raw = {k: (v if isinstance(v, bytes) else v.encode("utf-8")) for k, v in texts.items()}
    return _run(lambda st, b: pick_step(st, b, tuple(ok), raw, because), PickState(), text)


# -- `pick:` and `use:` by description alone (D-A1.20, 2026-10-03) -----------
#
# **He writes the words; the runtime finds the item.** Finding 148's amendment
# scored the two halves of `pick: because[<span>] <id>` apart: given the right
# description written, the letter after it was at chance on every arm, seed
# and layout -- he wrote a position (the first ok letter), and a model never
# shown a pick line did the same. Finding 149's amendment found the template
# id after `use: because[<clause>]` the clause's own about one time in three.
# The description is where the judgment is, and it names one item on every
# row; so the owner dropped the id from both lines (D-A1.20) and the runtime
# resolves the words. These replace `pick_step` and `use_us_accepts` as the
# binds for those lines; the old ones stay for the arms that trained them.
#
# The pick's evidence is copied from an ok item's own text, word-bounded,
# case one way (`_phrase`), and **the bracket closes only when the words name
# one item**: the ok items not yet picked whose text holds them. Several is
# the runtime's tie-break, not his -- an item whose whole text is the words
# wins, and between items whose text is identical the first shown, as with no
# soft term (D-A1.19). Words two items share and neither is wholly refuse
# `]`, so he writes on until they part; a decode stranded there (two texts
# ending on the same words, not seen in the filter world) backtracks, as
# H3's decoder must anyway (finding 147).


def _desc_owner(span: bytes, live: tuple[str, ...], texts) -> str | None:
    """The one ok item `span` names, or None."""
    hits = [i for i in live if _phrase(texts[i], span, closing=True)]
    if len(hits) == 1:
        return hits[0]
    whole = [i for i in hits if texts[i] == span]
    return whole[0] if whole else None


def desc_pick_step(st: PickState, b: int, ok: tuple[str, ...], texts) -> PickState | None:
    """Consume one byte of `pick: because[<words>]` (spec §6, D-A1.20).

    One or more `because[...]`, space-joined, each naming a different ok
    item, or `none` as the whole line. `ok` in the order `check:` shows them;
    `texts` maps each id to its observation text as bytes. `picked` carries
    the ids the closed brackets named -- the runtime's reading of the line.
    """
    ph = st.phase
    live = tuple(i for i in ok if i not in st.picked)
    if ph == "prefix":
        return _plit(st, b, PICK_PREFIX, "head")
    if ph == "head":
        if b == 0x0A:
            return st._replace(phase=DONE, prefix="") if st.prefix == "none" and not st.picked else None
        cand = st.prefix + chr(b) if b < 128 else None
        if cand == BECAUSE:
            return st._replace(phase="evidence", prefix="", span=b"")
        if cand and (BECAUSE.startswith(cand) or (not st.picked and "none".startswith(cand))):
            return st._replace(prefix=cand)
        return None
    if ph == "evidence":
        if b == ord("]"):
            who = _desc_owner(st.span, live, texts) if st.span else None
            return st._replace(phase="sep", span=b"", picked=st.picked + (who,)) if who else None
        if b in (0x0A, ord("[")):
            return None
        nxt = st.span + bytes([b])
        return st._replace(span=nxt) if any(_phrase(texts[i], nxt, False) for i in live) else None
    if ph == "sep":
        if b == SPACE:
            return st._replace(phase="head", prefix="") if live else None
        return st._replace(phase=DONE) if b == 0x0A else None
    return None


def _raw_texts(texts) -> dict:
    return {k: (v if isinstance(v, bytes) else v.encode("utf-8")) for k, v in texts.items()}


def desc_pick_resolve(text: str, ok: tuple[str, ...], texts) -> tuple[str, ...] | None:
    """The items a whole `pick:` line names -- `()` for `pick: none` -- or None
    if the line is not legal. What the runtime acts on."""
    raw, st = _raw_texts(texts), PickState()
    for b in text.encode("utf-8"):
        if st.phase == DONE:
            return None
        st = desc_pick_step(st, b, tuple(ok), raw)
        if st is None:
            return None
    return st.picked if st.phase == DONE else None


def desc_pick_accepts(text: str, ok: tuple[str, ...], texts) -> bool:
    return desc_pick_resolve(text, ok, texts) is not None


# `use:` by clause alone: a menu, so `choice_step` again -- `because[<a shown
# soft clause>]`, plus `none` where the frame offers it (arm USN's rows; in
# the split design the runtime owns `none`, D-A1.16). Two shown templates with
# the same soft clause are one option, and the runtime takes the first shown.


def use_clause_options(concept_clauses: tuple[str, ...], none: bool = False) -> tuple[str, ...]:
    opts = tuple(dict.fromkeys(f"{BECAUSE}{c}]" for c in concept_clauses))
    return opts + (("none",) if none else ())


def use_clause_accepts(text: str, concept_clauses: tuple[str, ...], none: bool = False) -> bool:
    options = use_clause_options(tuple(concept_clauses), none)
    return _run(lambda st, b: choice_step(st, b, USE_PREFIX, options), ParseState(), text)


def use_clause_resolve(text: str, concept_clauses: tuple[str, ...],
                       none: bool = False) -> int | str | None:
    """The template id (from 1, in the order shown) a whole `use:` line names,
    `"none"`, or None if the line is not legal. What the runtime acts on."""
    if not use_clause_accepts(text, concept_clauses, none):
        return None
    value = text[len(USE_PREFIX):].rstrip("\n")
    if value == "none":
        return "none"
    return 1 + list(concept_clauses).index(value[len(BECAUSE):-1])
