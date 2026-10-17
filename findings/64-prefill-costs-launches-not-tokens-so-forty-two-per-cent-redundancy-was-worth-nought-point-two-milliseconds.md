# Sixty-fourth finding — prefill costs launches, not tokens, so 42% redundancy was worth 0.22 ms

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Four runs on an idle 3080, `configs/corn_jr_260m.py` at bf16.
`scripts/prefill_redundancy.py` counted the redundancy;
`scripts/bench_prefix_reuse.py` timed what removing it bought.

## The idea, and it was a good one

A turn is not one generation. `corn/agent.py` runs a round per tool call plus
one for the spoken reply, and each round's context is the previous round's plus
what that round produced. `GraphedDecoder.stream` opens with `cache.reset()`,
so **round 2 re-encodes from token zero every token round 1 read and every
token round 1 wrote**, having discarded that KV moments earlier.

Counted over 300 real single-call turns from `tools.txt`:

    prefill tokens              116,338
    already computed this turn   49,001 = 42.1%
    mean redundant per turn         163 tokens
    the declaration alone           151 tokens, every round of every turn

And it is exactly recoverable rather than approximately. `corn/model.py` uses
learned absolute positions, so position *i*'s K and V depend on *i* and what
precedes it and on nothing after — a kept prefix **is** the history it claims
to be. (Pleasingly, `wpe` is usually the constraint here: it is why
`BatchedReader` cannot left-pad. Same property, paying out for once.)

`prefill(reuse=True)` was built, verified — 24/24 token parity, byte-identical
agent output through the grammar and the tool loop — and timed.

## It is a null

Round 2 of a real `send_text` turn on the 260M shape, 225 tokens with 163
shared:

    round-2 prefill, cold      10.63 ms
    round-2 prefill, reuse     10.42 ms      1.02x, 0.22 ms saved

    32-token reply decode      56.71 ms
    round 2 total, cold        67.34 ms
    round 2 total, reuse       67.12 ms      1.00x

**72% of the tokens skipped, 2% of the time saved.** Prefill is 16% of the
round and reuse removes 0.3% of it.

## Why, and this is the finding

Prefill time against prompt length, eager, the shipped path:

    tokens     16     32     64    128    225    384    511
    ms       8.82   8.48   8.57   8.36   8.65   8.12   8.45

**Flat. Thirty-two times the tokens, the same wall clock.** Prefill is bound
by kernel *launches* — 20 layers of ungraphed eager work — and not by the
tokens flowing through them. Cutting the token count optimises a variable the
clock does not depend on.

This is the second finding's diagnosis, on the path nobody re-checked. That
finding established decode was launch-bound and fixed it with CUDA graphs; the
same argument applies unchanged to prefill and was never made, because every
instrument since has measured decode. `corn/bench.py` reports `prefill_ms` on
every run and it has been sitting at ~9 ms in plain sight.

## What does move it

    tokens          eager   compiled(dynamic)   compiled(static)
    128              8.50        11.32               5.06    1.68x
    256              9.00        11.55               5.25    1.71x
    512              8.57        10.90               7.16    1.20x

**Static shapes are the whole story.** `torch.compile(dynamic=True)` is
*slower* than eager — guard overhead and fusion it cannot commit to — and the
same compile with `dynamic=False` is 1.68x. That is ~3.4 ms a round, fifteen
times what prefix reuse bought, from the opposite end of the problem.

Static shapes for a variable-length prompt means bucketing and padding, and
the padding is safe in the way that matters. Right-padding with **random
garbage**, comparing the KV over the real positions:

    layer  0   delta 0.000e+00                      exactly inert
    layer  1   delta 1.25e-01   scale 16.12   rel 7.8e-03
    layer 11   delta 6.25e-02   scale  4.91   rel 1.3e-02
               bf16 relative step 3.9e-03  ->  2-3 ULPs

**Layer 0 is exactly zero**, which is the causal mask doing its job: a real
position never attends to padding, so the arithmetic is unchanged. What drifts
from layer 1 on is SDPA tiling a longer sequence differently, at two to three
bf16 ULPs — the same rounding the sixty-first commit's manual attention
produces, and the same seq-length effect that appears between a 46-token and a
79-token prefill of the *same* tokens. So a bucketed prefill lands in the
`--fast-attn` category rather than the `--buckets` one: same computation,
different rounding, fine for talking and not for a scorecard.

## What this settles

- **The 42.1% is real and worthless.** Both halves matter: nobody should
  re-derive the redundancy and assume it is money.
- **`prefix_reuse` stays, off by default.** It is correct and free, it may pay
  where launches stop dominating — a longer window, a batched or graphed
  prefill — and deleting it would invite the same day's work again. The
  docstring carries the null.
- **The chunked prefill it needed is the real yield.** `CornModel.step` now
  takes `T > 1` tokens against a live cache, which
  `CausalSelfAttention.forward` refuses outright. The sixty-second finding's
  draft-and-verify needs exactly that primitive, and it now exists.

## What it does not settle

- **Bucketed static prefill is measured but not built.** 1.68x is a timing of
  `torch.compile(dynamic=False)` on whole-sequence forwards at exact bucket
  sizes, not of a padded implementation with the logits read from position
  `t-1`. The reference `forward` returns only the last position's logits, so
  that indexing is a real change and is unwritten.
- **Whether prefill is worth attacking at all.** It is 16% of a round here.
  1.68x of 16% is ~7% of a round, against decode's 84% — worth having, and not
  before anything that moves decode.
- **The 8 ms floor is unexplained.** Flat from 16 to 511 tokens says launches
  dominate; it does not say 20 layers of eager forward *should* cost 8 ms, and
  nobody has counted the launches or looked at where they go.

## The method note

This is the sixty-second finding's shape twice in one week: an intervention
reads near zero, and the measurement that kills it is the one that finds the
real mechanism. Both times the useful move was to **measure the quantity the
mechanism operates on** — bytes rather than tokens there, launches rather than
tokens here. A null that only reports its own size teaches nothing; a null that
reports why is a direction.
