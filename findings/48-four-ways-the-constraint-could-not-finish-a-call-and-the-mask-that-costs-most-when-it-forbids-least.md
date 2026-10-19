# Four bugs let decoding escape the call grammar mid-call

**Full result:** Four ways the constraint could not finish a call, and the mask that costs most when it forbids least

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Found 2026-08-22 while building the first instrument that holds a *conversation*
with a running instance rather than scoring one turn at a time. None of the four
is a model failure. All four were invisible to `evals/`, to
`scripts/check_grammar.py` as it then stood, and to `harness/checkup.py` — and
together they were costing the 260M roughly half of its routing.

The instrument is `harness/converse.py`; what it found on its first run had
nothing to do with the question it was built to ask.

## The class: a grammar that dead-ends is worse than no grammar

`corn/grammar.py` masks every token that cannot lead to a call `validate_call`
would accept. When the mask comes back empty it *releases* — the constraint
disarms mid-object and an unconstrained model finishes the call. That path was
written as a safety valve for something that should never happen. It turned out
to be reachable four ways, and every one of them ends the same: `not_json`,
nothing executes, and the turn is lost with the transcript looking like the
model's fault.

| # | where | what reached it | receipt at 260M |
|---|---|---|---|
| 1 | a key opened for a tool with no parameters | `{"` is one BPE merge | `{"name": "decline", "arguments" : {"declare", "declare", …` |
| 2 | unbounded insignificant whitespace | the mask's best legal token is a space, forever | `{"name": "place_call", "arguments"  :` and 200 tokens of nothing |
| 3 | a `\uXXXX` escape in a copy slot | the codepoint is unknown until the fourth digit | `{"contact": ": က000000000…` |
| 4 | generation past the closing brace | the grammar disarms at the close and nothing stops the model | a valid `place_call` followed by 36 more `}` |

**The second is the one worth internalising.** At temperature 0 an unbounded
legal token that does not advance the machine is an *absorbing state*: the model
wants a byte the grammar forbids, `_mask` leaves it the best legal token
instead, a space is among the most probable tokens in any vocabulary, and
nothing about the context changes when it is taken — so the next step re-runs
the same argmax over the same mask and takes a space again. The constraint never
releases and never errors. It quietly spends the whole budget on whitespace. Two
spaces before a colon, in an emission no generator ever wrote, is the only trace
it leaves.

**The first was created by a corpus decision, one arm earlier.** `decline` has
`params=()`, and the branch that lets a zero-parameter tool close on `{}` carried
the comment "No tool in the registry is like this today". WS-E made that false
and nobody re-read the comment. So the tool the forty-second finding added was
**100% broken at runtime whenever the model reached for it through `{"`** — and
WS-E made the model reach for it constantly.

**The third could not simply be banned.** 49 calls in `data/raw/tools.txt` use a
`\u` escape, all of them in `place_call.contact` or `send_text.contact`, all of
them accented names like `Ben Traoré`. Refusing the escape would refuse the
corpus and, worse, refuse a real contact. It is pruned per digit against the
characters the source could actually continue with — at most as many candidates
as there are occurrences of the value so far, against the 65,536 a codepoint
could otherwise be.

The general property is now a guard rather than four fixes:
`scripts/check_grammar.py` group 8 walks one canonical call per registry tool
and asserts that **no reachable state has an empty legal-byte set**.

## What it was worth, measured on the same sixteen turns

`harness/checkup.py` against `checkpoints/corn_jr_260m`, `--multi`, temperature
0, the same cases throughout:

| row | before | after |
|---|---|---|
| routed | 4/16 | 5/16 |
| executed | 4/11 | **6/11** |
| spoke_from_tool | 4/4 | **10/10** |
| malformed calls | **7** | **0** |

`routed` barely moves, and that is the honest headline: the fixes did not teach
him to route. They stopped the runtime from destroying calls he had already
written correctly. What they bought is that *every* call now completes and
executes — and, more importantly, that the next measurement is readable at all.
With seven of sixteen turns dying inside the constraint, nothing about the
model's actual policy could be seen.

## A fifth defect, in the instrument rather than the runtime

`harness/checkup.py` did not reset the session between cases. Against a
`--multi` instance every case after the first opened on the tail of the one
before — twenty unrelated sentences stacked into one conversation, scored as
though each stood alone. The rows still printed. Median turn time fell from
680 ms to 341 ms once the reset went in, which is the size of the context that
had been silently accumulating.

It did **not** move `routed`, so no published number was wrong because of it.
That is luck, not design.

## The mask costs the most exactly when it forbids the least

Profiled on `bpe8k`, 8,192 tokens, one mask build per state:

| state | tokens allowed | ms to build |
|---|---|---|
| `name_body` | 1 | 2.6 |
| copy slot, typed | 2 | 0.7 |
| `args_open` | 4 | 38.6 |
| copy slot, empty | 47 | 44.5 |
| **unconstrained string body** | **8,147** | **174–230** |

The general path discovers that almost everything is legal by calling `_allows`
on almost everything — stepping every byte of every token, in Python. And the
cache key carries `copy.source`, which `set_source` re-points every round with a
growing context, so the work is redone from scratch for every round of every
turn.

Two rounds of a `save_note` turn were spending ~400 ms of a 612 ms turn there.
**It was never the model.** VISION §3's 500 ms budget was being missed by the
constraint's bookkeeping.

The fix is that legality in that state is a property of the *token*: every byte
from 0x20 up that is not a quote or a backslash keeps the machine in `arg_str`,
whatever the state's history and whatever the source. 8,134 of 8,192 tokens
qualify and the set is built once, in the constructor.

| state | before | after | speedup |
|---|---|---|---|
| empty text body | 230 ms | 0.7 ms | **308×** |
| mid query body | 212 ms | 0.8 ms | **265×** |
| mid text body | 174 ms | 3.6 ms | **49×** |
| copy slot, `args_open`, `name_body` | — | unchanged | 1× |

**It is a fast path and not an approximation**, and the 51 remaining tokens are
why: a quote can close the string and the rest of the token can walk anywhere
after that, possibly into a copy-constrained slot, and only the general path
knows whether that is legal. `check_grammar` group 7b differences the two paths
token-for-token across eight states — including two copy-slot states that must
*not* take the fast path — and all eight agree exactly.

## Two more, from the same run

**The copy source included the prompt.** Gap 3's rule is that a contact must be
a span of something *actually said*; `set_source(ctx)` passed the whole context,
and `ctx` opens with the tool declaration. So `"dial a contact"`,
`"send an SMS to a contact"` and `"place_call"` were all legal contact names —
and two of them reached a user: `morning` produced
`place_call{"contact": "dial a contact"}` and the reply *"I don't have a contact
called dial a contact."* The head is now excluded and the conversation is not,
because the clarify path depends on copying a name out of an earlier
observation.

**`resolve_date` asked a question it could not read the answer to.** Two of the
seven `RANGE_EXPRESSIONS` clarify with "Saturday or Sunday?" and three more with
"Which day last week?", and a bare weekday matched no branch in the resolver —
every weekday form requires a lead word. Live, that produced a correct clarify,
a refused answer, and a retry with an ordinal that resolved to the wrong day and
was read out with confidence.

The first fix for it was also wrong, and measuring it is what caught that:
resolving a bare weekday to its most recent occurrence is right for the two
weekend questions and lands a week or two outside the span on four of the
others — trading `unrecognised` for a confidently wrong date, which is the one
trade that tool's docstring forbids. The resolver is stateless and structurally
cannot answer "Saturday"; the span is now remembered in `corn/agent.py`, where a
process can hold state, and dropped as soon as it is used. Six of the seven
questions are answerable; `last month` still refuses, correctly, because a
weekday name has five candidates in a month.

`scripts/check_temporal.py` holds the general property — every clarify question
is answerable — across a year of anchors rather than one, because the broken fix
passed at a single anchor.

## What this changes about how the project is measured

Every one of these was found by **running the assembled thing and reading the
transcript**, not by a scorecard. `evals/` scores a prompt against a gold string
and stops before the observation; it cannot see a constraint that dead-ends
because it never decodes that far. `check_grammar` asserted that the corpus is
accepted and that malformed calls are refused — both true throughout, and
neither of them the question. The gap was that nothing asserted the machine
could always *finish*.

The lesson is the forty-sixth finding's, one level up: a guard that reads the
generator cannot see a stale artefact, and a guard that reads only accept/reject
cannot see a machine that accepts and then cannot proceed.
