# Seventy-eighth finding — the query slot buys nothing on this base and costs three chain follow-ups in four, and the social hatch catches five utterances in thirty

**Cost:** 0 s of new scoring on record; it reads 2 cards scored for an earlier finding (`corn_jr_260m`, `corn_jr_260m_v4`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

A harness audit rather than a training run: `checkpoints/corn_jr_260m_v4/ckpt.pt`
driven live on 2026-08-29 from a working tree carrying session 12's uncommitted
repairs (`framed` and the frame-loss floor in `corn/agent.py`, the ASCII fold in
`corn/grammar.py`). 140 logged turns on the primary server (`--all`, rows in
`Saved Sessions/turns.jsonl`, sessions `20260829T19*`–`T2*`) plus two unlogged
controls on the same weights and the same flags: `--no-grammar` on port 8766,
and port 8767 with **only** `("web_search", "query")` removed from
`RUNTIME_COPY_SLOTS` — schema, enum narrowing and both contact slots left
armed. The isolated control is what makes this a finding rather than session
12's observation: `--no-grammar` moves the schema and the copy slots together,
and they turn out to have opposite signs.

The question the audit was asked was whether the harness is holding the model
back. **It is, in exactly one place, and everywhere else it is the only thing
between the user and the pretraining register.** Three layers intervene between
the weights and the user, and they need separating before either half can be
read:

| layer | what it does | controlled by |
|---|---|---|
| A. the grammar | constrains what he *may* emit — schema, enum narrowing, copy slots | `--no-grammar`, `RUNTIME_COPY_SLOTS` |
| B. the guards | discards what he *did* emit — `social_rejection`, `recall_rejection`, `search_rejection`, the frame-loss floor | nothing; always on |
| C. the hatches | decide the turn **before he runs** — `conversational_reply`, `identity_reply`, `temporal_request`, `recheck_request` | `--restrict`, which adds rather than removes |

Layer C is why the authorship columns read as they do. Over the whole 151-row
log as it stands: the model authored the spoken words on **60 turns, the tool's
`say` on 70, the runtime's own sentence on 21**, and 10 of 109 tool calls were
written by the runtime rather than decoded.

## A: the query copy slot forbids the composition the same corpus teaches

Four chain follow-ups, each the second turn of its own conversation, armed
against the isolated control:

| | query slot armed | query slot off |
|---|---|---|
| `what about Sweden?` after Norway | `the capital of Norway` ~~masked 2 | `the capital of Sweden` |
| `what about Brazil?` after Japan | `the population of japan` ~~masked 1 | `the population of brazil` |
| `and Hungary?` after Poland | `the currency of poland` ~~masked 2 | `the currency of poland` |
| `what about Chile?` after Peru | `the capital of Peru` ~~masked 2 | `the capital of chile` |

**0 of 4 armed, 3 of 4 off.** The Hungary row fails identically on both sides
and is therefore the weights, not the slot — which is the control doing its
job, because without it all four would have been charged to the grammar.

**The mechanism is contiguity, and it is structural rather than tunable.**
`span_ok` requires the value to occur as a contiguous run of the source, and
`corn/agent.py`'s `set_source` binds that source to the whole conversation
below the declaration ("prior turns stay in, deliberately"). A chain query is
by construction *not* contiguous anywhere: `the capital of` comes from the
previous turn, `Sweden` from this one, and no span of either contains both. So
no composed query can ever be legal, the slot bites at the join, and greedy
after the bite lands on the one string that *is* a span — the previous query
sitting in the history. Session 12 read this as a case-folding bug and fixed a
real one; the fold changed which carrier reproduces it, not whether it
reproduces.

**And the rescue it was added for does not reproduce on this base.** The slot's
justification is `harness/server.py`'s own note: `corn_jr_260m` handed `look up
Ada Lovelace` wrote `{"query": "ada-lovelace-definition-definition-…` until the
budget ran out. Eleven degenerate queries — five bare proper names including
Vercingetorix and Zbigniew Brzezinski, a colon syntax, two vocative-prefixed
requests, an embedded `the thing about the Antikythera mechanism`, and `I want
you to search Rachmaninoff` — are **byte-identical armed and unarmed**. The
slot never bit once. Its documented cost was measured on the v3 base and the v4
base does not need it.

**The schema half is pure rescue and the same controls say so.** Unarmed,
`--no-grammar` produced `{"query": "the capital of Finland"}` with no closing
brace and a `<|say|>` spliced inside the call, and `{"query": "and Hungary?""}`
— both `not_json`, both executing nothing. Layer A is not one decision; it is a
schema that pays for itself and one slot that is now paying only costs.

## C: the hatches are exact-match, and the misses are the dangerous part

`conversational_reply`, `identity_reply` and `temporal_request` all test whole
normalised utterances against frozen sets. Coverage over a battery of phrasings
a live user produces:

    social    5 of 30      identity   11 of 15      temporal   9 of 16

**The dominant social miss is saying his name**, and the guard turns it from an
example into a property. `morning` and `good night` are both *in* the pools;
`morning corn` and `good night corn` are not. Over **all 275 phrases in the
five pools, 0 survive being addressed by name, and a trailing-vocative strip
recovers all 275** (`scripts/check_hatches.py` §3). On the battery that is 13
of the 25 social misses, taking coverage from 5/30 to 18/30 — but the pool-wide
number is the one that says how much one strip in `_normalised` is worth.

**The vocative is not only a social problem — it poisons `web_search` and
nothing else.**

    look up the capital of Iceland         -> "the capital of Iceland"
    corn look up the capital of Iceland    -> "corn look up the capital of Iceland"
    corn, look up the capital of Iceland   -> "corn, look up the capital of Iceland"
    text Grace Kim that I'm on my way      -> correct with and without the vocative
    note down that the bins go out tonight -> correct with and without the vocative

`send_text` and `save_note` extract a bounded entity and are immune;
`web_search`'s query copies a run of the sentence and the vocative is sitting
at its front. `strip_affixes` carries `"look "` and cannot see it behind a name.

**What a miss costs, over all 34 of them run live.** Fifteen of the 25 social
misses routed to `decline` — `hey corn` answered "Nothing I've got covers
that." Seven produced ungated speech, of which three were unusable: `bye corn`
gave a repetition loop with `<|endoftext|>` in the transcript and the say
tripled, and `hope you're well` gave **"You're not well. You need to see a
doctor."** The remaining **8 of 34 reached the live search provider**, and 4 of
those 8 came back with a confident irrelevant page served as the answer:
`thanks corn` → Food Network's Thanksgiving corn recipes, `thank you corn` →
"It's Corn" thank-you cards, `what happened on Wednesday` → the plot of
Netflix's *Wednesday* season 2, `what did I do on Friday` → Marvel trivia about
a character called Friday (and, on an earlier run of the same turn, a Reddit
post about what people do on Friday nights — the wrong answer is not even
stable). The other four searched honestly and returned `no_results`.

That is the shape worth naming: **a hatch miss is not a degraded answer, it is
a private or self-referential question leaving the machine.** `who made you`,
`how do you work` and `can you tell me what you can do` all went to the
internet.

**The counter-finding, which the same battery produced and which matters for
what the hatches are for.** `remind me what I did yesterday` misses
`temporal_request`, falls through to the router, and **the model chains
`resolve_date` → `recall_day` correctly on its own.** The hatch is not purely a
crutch and the weights are not empty behind it; its coverage is a floor that is
in places below what he can already do.

## B: the guard fires three times in twenty, and only inside C's coverage

Twenty hatch-caught social turns (`hey`, `how's it going`, `thanks`, `bye`,
`morning`, four draws each):

    guard fired            3 / 20   -- 2x "tool register: find anything", 1x "names Lynn"
    his own words served  17 / 20

By reading rather than by ruler, about 13 of those 17 are not usable: `hey` →
"I'm sorry, but I don't have any questions."; `bye` → "Ah, that's a beautiful
song."; `how's it going` → "Pretty good. I'm just getting ready for my next
class."; `thanks` → "You're welcome. I'm glad you enjoyed it." That is a
judgement and is marked as one; the 3/20 is not.

One of the leaks is a single missing entry rather than a class:

    social_rejection("I don't have anything useful on morning.")  ->  None

`TOOL_REGISTER` carries `"find anything"` and not `"have anything"`, so
`web_search`'s empty-result sentence reaches the user as a reply to a greeting
— the exact family the constant's own docstring says it exists to catch, one
phrasing further out.

**And the structural point, which no entry fixes.** `social_rejection` is
called only from inside the social hatch. Outside it there is no guard on
speech at all, which is why `rough week, honestly` came back as invented
personal history ("I've been having a lot of personal issues and I haven't been
able to focus on work") and `do you ever get tired?` as "sometimes I get
tired". **Guard coverage is exactly pool coverage**, so layer B can never be
better than layer C, and widening C is what widens B.

## What this corrects

  * **Session 11's and session 13's reading of the temporal chain.** `what did
    I do yesterday` completing `resolve_date` → `recall_day` in 9 ms with 0 ms
    to first token was `temporal_request`, runtime-authored, no decode. Any
    live read of the chain has to check the `author` column before crediting
    the weights — though see the counter-finding above, which credits them on
    a turn the hatch missed.
  * **Session 13's first-pass reading of the greetings.** `hey` and `morning`
    both hit the hatch. `hey`'s good reply was the *pool* after the guard
    rejected his attempt (`fell_back: unfinished`); `morning`'s bad reply was
    the guard leaking. Opposite mechanisms, and neither is coverage.
  * **Session 12's sticky-query attribution.** The fold was a real repair to a
    real carrier and is not withdrawn; it is not the whole mechanism, and the
    contiguity argument above says no fold could have been.

## Instrument facts found while auditing

  * **The session log cannot price any of this.** `turn_record`'s `transcript`
    holds what was *served*, so on a runtime-authored turn the model's own
    emission is discarded unrecorded. `author: "runtime"` says an intervention
    happened and never what it cost — every number above had to come from an
    A/B against a second server. A `model_draft` column would make these rates
    countable from the rows, which is the argument `frame_loss` already won.
  * **The cp1252 guard is in the wrong scope.** `harness/client.py` reconfigures
    stdout inside `main()`, so anything importing `Client`/`run_turn` inherits
    the `UnicodeEncodeError` that guard exists to prevent — hit here on
    `złoty`. The CLI is fine; embedders are not.
  * `strip_affixes` carries `"look "` but not `"search for "`, so `search for
    Nikola Tesla` reaches the provider with its verb attached, on both sides of
    the grammar A/B.

## Limits

n=1 on every live cell — one checkpoint, greedy tool decode, no seed spread,
and the social pools sample at `speech_temperature=0.3` so the 20-turn guard
battery is four draws of five utterances rather than twenty independent ones.
The three coverage numbers are properties of frozen sets and a hand-written
battery: they are exact for that battery and say nothing about the true
distribution of what the owner types. The 3-of-4 chain recovery and the 0-of-11
rescue are the two numbers this finding actually rests on, and both are
byte-comparisons against a control that differs by one slot.

Nothing here licenses a corpus change. The vocative, the missing
`TOOL_REGISTER` entry, the hatch widths and the query slot's removal are all
runtime decisions and all the owner's; `scripts/check_hatches.py` and
`check_grammar.py` §9 record the present numbers so that a repair moves a guard
rather than moving silently.
