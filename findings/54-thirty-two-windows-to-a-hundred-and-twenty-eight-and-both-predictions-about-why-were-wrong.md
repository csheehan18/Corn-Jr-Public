# Fifty-fourth finding — thirty-two windows to a hundred and twenty-eight, and both predictions about why were wrong

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Two decode-time changes, measured on `corn_jr_260m` on the 10 GB 3080,
2026-08-24: `StaticCache` gains a `slots` argument, and `--dtype bf16` serves
the weights at half precision. Together they take WS-B-alt's batch ceiling from
32 windows to at least 128. No training, no corpus, no model change — and the
reasoning that motivated each was wrong about which resource was scarce.

The measurement is `harness/backends/read.py`'s `Reader` at its real prompt
length — 115 tokens, 32 new — rather than A3's synthetic 96, best of two after
a warm run.

## The starting point, and a cliff worth naming

    N     total ms   ms/window   peak GB
    1        315.1      315.07      2.06
    8        350.5       43.82      2.83
    32       709.0       22.16      5.46
    64   390,641.2    6,103.77      8.98   <- paging
    256        OOM

**Sixty-four windows took six and a half minutes**, because the allocation
crossed what the card holds and WDDM began paging. The failure is not a
gradual slowdown and nothing should discover it at runtime.

## The cache was sized for a conversation and used by a worker

`StaticCache` reserved all `block_size` slots for every row — **40 MB to hold a
147-token sequence**. The asymmetry nobody had named: a turn may run to
`block_size` and cannot know when, so `GraphedDecoder` must allocate the whole
window; a worker knows its exact length before it starts, because
`corn/extract.py` cuts to a fixed token count and the budget is an argument.

    N     before ms   before GB      after ms   after GB
    32        709.0        5.46         478.1       3.68
    64    390,641.2        8.98         736.7       5.41

Attention runs over every allocated slot, so the smaller allocation is less
work as well as less memory — 32 windows got 33% faster on a change made for
footprint.

**A wrong `slots` does not crash, which is why it is guarded.** The mask is
`arange <= pos`, so undersizing changes which keys are visible and the reply
stays fluent — the worst failure shape this project recognises.
`scripts/check_decode.py` runs the same batch against a full-window cache and
requires the two byte-identical, 4/4 rows. `cache_slots` on `read` exists only
as that seam, in the sense `--stop-at` does in `corn/train.py`.

## bf16 buys nothing at one sequence and 73% at sixty-four

The prediction, stated before the run: decode at batch 1 is
memory-bandwidth-bound, so halving the weight bytes should approach 2x there
and shrink as larger batches turn compute-bound.

    dtype   weights      N        ms   ms/window   peak GB
    fp32       994       1     335.9      335.93      2.00
    bf16       497       1     342.6      342.62      1.49
    fp32       994       8     376.7       47.09      2.38
    bf16       497       8     364.7       45.59      1.68
    fp32       994      64     758.0       11.84      5.41
    bf16       497      64     437.2        6.83      3.20
    bf16       497     128     534.0        4.17      5.33

**Backwards.** Two per cent slower at N=1, inside noise, and **1.73x at N=64**.
The premise was wrong about which resource is scarce at one sequence: 32 tokens
in 336 ms is ~10 ms a token for a 260M model, which is kernel-launch-bound.
That is precisely what `GraphedDecoder` exists to fix and what `BatchedReader`
deliberately does not capture, so halving bytes that were never the constraint
buys nothing. By N=64 the kernels are large enough for traffic to matter.

**This is the second decode-time optimisation this project has mispredicted,
and both errors have the same shape.** `torch.compile` was expected to grow
with model size and shrank — 1.16x at nano against 1.07x at 250M, because the
kernels were already compute-bound. Both times the mistake was assuming which
resource was scarce instead of measuring it, at both ends rather than one.

## What it adds up to

**128 windows — 4,096 tokens, longer than most article bodies — in one batch
in 534 ms**, which beats fp32 at half the batch size. Sixty-four windows went
from six and a half minutes to 437 ms. The ceiling was 32 and is now at least
128; where it sits exactly is unmeasured, because past the cliff a single point
costs six minutes to print.

The low end matters for a different reason. Four windows cost **6% more than
one** (333.7 ms against 315.1), because the weight traffic is paid once
regardless of batch. So a constrained device running a single process still
affords a 4-window quorum — which is the part of the design that would
otherwise not survive, since `grounded` is free Python and runs anywhere but
the *vote* needs two readings, and one reading is what a naively prompted model
already has.

## What this cannot say

**bf16 is a measurement condition and it is not established as safe.** Every
scorecard, eval row and finding in this project was read off fp32 weights, and
greedy decoding turns a swapped logit into a different sentence rather than a
slightly worse one — which on the extraction path can flip a window between a
grounded span and a refused invention, presenting as a model regression that is
not one. On the iron passage both precisions produced byte-identical replies on
**3 of 3** windows. That is one passage. `--dtype` defaults to fp32,
`harness/server.py` reports it in `wiring`, and `check_decode.py` asserts the
flag reaches the weights, because a `--dtype` that silently loaded fp32 would
label every row with a condition it was not measured under and nothing would
look wrong.

**Nothing about other hardware.** One card, one driver model. The paging cliff
in particular is a WDDM behaviour and a Linux box would fail differently.

**Nothing about whether reading more of a page helps.** The ceiling is a
capacity result. Whether 128 windows extract better than 8 is the slice's
question, and `reduce` prefers agreement over presence, so more windows may buy
coverage or may merely buy more ways to disagree.

## What follows

Sizing beyond one batch is now a real option rather than an arithmetic
exercise: a full article body fits, and iterative batches with an early exit —
stop when *k* windows agree, never at 1 — become the design for anything
longer. The remaining decode lever is that `BatchedReader` does not capture a
CUDA graph, which the N=1 number above says is the whole cost at small batch
and nearly none of it at large.
