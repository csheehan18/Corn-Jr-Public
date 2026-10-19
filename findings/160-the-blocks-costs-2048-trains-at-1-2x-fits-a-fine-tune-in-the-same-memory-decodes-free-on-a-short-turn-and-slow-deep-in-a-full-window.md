# 2048-token blocks cost 1.2x training time and fit in memory

**Full result:** The block's costs: at the 260M step 2048 trains at 1.20x the 512 wall clock and 1024 at 1.06x, a fine-tune fits at 2048 in the memory it uses at 512, decode is free on a short turn and 100 tok/s deep in a full window as shipped, and a 2048 window holds ten documents with a third of its attention inside one

**Cost:** ~12 min of GPU in four chains under `scripts/gpu.py`, all marked contended (card at 31-44% light use): 3 min (killed -- a spill I should have priced first), 5.2, 5.8 and 0.9 min; CPU ~5 s for the packing probe and 79 s for the 2048 conversation build; the bench options, the probe, the decode fix and its guard and this write-up took about 25 min (16:25-16:50 on 2026-10-10).

ROADMAP P0: *the block's costs, no slice needed: training at the H200 shape,
fine-tune memory on the 10 GB 3080, bucketed decode at 2048, and what a block
of five-plus packed documents attending across each other costs.* It feeds the
owner's block decision (D2) and the 1.0 date; P1's nano pilot is the other
half of D2 and is not read here. **Every timing below was taken beside 31-44%
light use of the card and is a bound**; the three blocks were read back to back
in one sitting under the same load, and the ratios between them are what this
finding quotes. Cards: `evals/results/block_costs__160.json` (every bench row)
and `evals/results/block_packing__160.json` (the stream and the v5 slices).

## 1. Training, at the H200 step

`corn/trainbench.py --compile` on `configs/corn_jr_260m_v4.py`'s shape and its
24,576-token step, the tokens per micro-batch held equal across blocks:

    block   rows x accum x block   step ms   tok/s   TFLOP/s   vs 512   by FLOPs   peak / reserved
    512        8 x 6 x 512           1,135   21.6k     36.6     1.00      1.00     7.73 / 8.03 GB
    1024       4 x 6 x 1024          1,206   20.4k     37.1     1.06      1.08     7.74 / 8.05 GB
    2048       2 x 6 x 2048          1,357   18.1k     37.6     1.20      1.23     7.76 / 8.10 GB

**The step costs what its arithmetic says.** Achieved TFLOP/s is flat, and the
ratio sits just under the FLOP count's (`flops_per_token`: the quadratic term
is 245,760 x T a token against 6N = 1.56 GFLOP, so attention is 7.4% of the
step at 512, 13.8% at 1024, 24.2% at 2048). PLAN-1-0 §4's estimates -- ~1.3x
at 1024, ~2x at 2048 -- priced attention as a larger share than it is at 1,024
wide.

**On the H200.** The v4 run was 6 h 43 m and $25.52 at 512 (~$23.10 of it
training). At the 3080's ratio, **2048 is ~8.0 h and ~$30, 1024 ~7.1 h and
~$27** -- an extrapolation: the H200 holds the 3080's ratio if its flash kernel
keeps the same efficiency against its matmuls, and the FLOP count (1.23x) is
the ceiling if it does not. D11's ~1B-token pilot at 2048 is ~1.6 h of H200 at
v4's sustained rate.

**The pilot's own shape** (`nano20m_v3`, compiled, 24 x 2 x 512 and its
equal-token twins): 137, 151 and 178 ms, **1.10x and 1.29x** (by FLOPs 1.14
and 1.42 -- attention is a larger share of a 512-wide model). P1's three arms
cost about 3.4 runs of the 512 arm, which is PLAN-1-0 §4's ~50 minutes.

## 2. Fine-tune memory on the 10 GB card

**Memory is linear in tokens per micro-batch, not quadratic in the block** --
SDPA's flash kernel never builds the T x T matrix -- so at equal tokens the
three blocks reserve 8.03, 8.05 and 8.10 GB of 10.00. A fine-tune at 2048 runs
**2 rows x 6 accumulation, 24,576 tokens a step -- `4j`'s step exactly (8 x 6
x 512) -- in the same memory, at 1.2x its time** (`4j`'s 17 minutes of
training becomes ~20). PLAN-1-0 §4's "about four times 512's at the same
batch" is true at the same *rows*; nothing needs more accumulation.

What does not fit: **4 rows at 2048** (8,192 tokens a micro-batch). The first
chain asked for it, the card went to 9,998 of 10,240 MiB, and it was killed
before a step was timed -- WDDM spills into host RAM rather than raising, as
`trainbench`'s docstring warns, and §1's line puts it at ~12.6 GB. So did 16
rows at 512, which was cut from the chain unrun.

## 3. Decode

`corn/bench.py` gained `--block-size`, `--buckets`, `--compile-step` and
`--paths`. bf16 is finding 2's condition; fp32 with buckets and
`compile_step` is what `harness/serverconfig.py` ships. tok/s, graphed path
(with sampling and readback in brackets), and the 32-token reply in ms:

    dtype  buckets  compile  positions      block 512           block 2048
    bf16   off      off      128-256        425 (394)  87       226 (218)  153
    bf16   on       off      128-256        502 (461)  75       503 (459)   75
    bf16   off      off      1792-1920        --                225 (217)  170
    bf16   on       off      1792-1920        --                234 (225)  165
    fp32   on       on       128-256              297  119            303  117
    fp32   on       on       352-480              234  157              --
    fp32   on       on       1792-1920        --                      100  412
    fp32   on       off      128-256          --                      276  128
    fp32   on       off      1792-1920        --                       97  422

**Finding 2 reproduces**: 425 against its 424 at this shape. The 554 that
PLAN-1-0 §4 and the P0 brief quote is finding 2's 12L x 1280, a shape that
never shipped.

**Unbucketed, 2048 halves every turn** (226): the static cache attends all
2048 slots. **Bucketed, a short turn costs exactly what it does at 512** --
503 against 502 in bf16, 303 against 297 as shipped -- and the server already
runs buckets, so a short conversation pays nothing for the wider window.

**Deep in a full window is the cost, and no bucket removes it** -- the window
is full. **As shipped, a turn at positions 1792-1920 decodes at 100 tok/s and a
32-token reply takes 412 ms** (91 ms of it prefill), against VISION §3's 250
tok/s and 100 ms; 512's own deepest point reads 234. bf16 reads 225 at the
same position with a 28 ms prefill. So the 10-20-turn goal pays ~2.3x a token
at the end of a long conversation as shipped, and dtype is the measured lever
-- but fp32 is a measurement condition (`corn/sample.py`: every scorecard is
fp32), so serving bf16 is an H3 and owner choice, not a corpus one.
`attn="manual"` (2.2x at decode in `model.py`'s own measurement) was not read.

**A hole, fixed: `compile_step` silently fell back past eight buckets.** Dynamo
caps one function at 8 compiled versions; a 2048 window has 16 buckets, the
ninth raised `FailOnRecompileLimitHit` under `fullgraph=True`, and
`_capture`'s broken-toolchain path caught it -- leaving buckets 1-8 compiled,
9-16 eager, and the card saying `compile_step: false`. 1024 has exactly 8
buckets and 512 has 4, so nothing shipped ever met it.
`corn.decode.ensure_recompile_room` raises the limit to twice the bucket count
before compiling (never lowering it); `scripts/check_decode.py` section 0
checks the helper without compiling, and `--compile` now builds sixteen
compiled buckets on the nano checkpoint and requires `compiled` and 96/96
greedy parity -- **96/96 and compiled with the fix; with the helper made a
no-op it fails on both counts.** What the fix buys is honesty more than speed:
3% deep (100 against 97), 10% on a short turn (303 against 276).

## 4. Packed documents

**The premise was a reading of six generated files.** "No document exceeds 431
tokens" is `docs/MEASURED-TURNS.md` §4's table, and its six files are all
generated. The stream `train.py` samples is 46.4% web, and
`scripts/probe_block_packing.py` reads it per source (400 random windows a
source a block, 2M-token samples for lengths): **web's median document is 834
tokens, p90 2,541; 93% of web tokens are in documents longer than 512 and 45%
in documents longer than 2048.** Every other source sits at a median of 48-228
tokens, with at most 5% of its tokens (narrative) in documents over 512.

**What a boundary is had to be read, not assumed.** The first cut used
`<|day|>` where a source had no `<|endoftext|>`; by hand, five sources
(`structured`, `tools`, `extract`, `turn2`, `paired`) have neither and separate
documents with a blank line, and `compound_v2` heads only some documents with a
day line, so its p90 read 1,133. A blank line is the boundary in every source
without `<|endoftext|>`; `chat` then reads a median of 48 and `compound_v2` 130,
against MEASURED-TURNS' independent 45 and 128.

Weighted by each source's share of the stream (which is its share of windows):

    block   documents a window   five or more   same-document pairs   cut head   whole
    512            3.1               16%               58%              49%        35%
    1024           5.3               52%               45%              37%        48%
    2048           9.7               57%               33%              25%        61%

*Same-document pairs*: the share of causal (query, key) pairs whose key is in
the query's own document -- a FLOP share. *Cut head*: tokens whose document
began before the window. *Whole*: tokens in a document wholly inside it.

**"Five-plus packed documents" is true of 57% of 2048 windows** -- every window
outside web (11 to 43 documents) and 8% of web windows (2.6). The
costs, each priced:

  * **Compute.** Two thirds of attention pairs at 2048 cross a boundary, and
    attention is 24.2% of the step: **16% of a 2048 step is spent attending
    across documents** (3% at 512, 8% at 1024). It is already inside §1's
    1.20x.
  * **Stopping it.** A document mask through SDPA's boolean path
    (`trainbench --doc-len 150`) steps in **1,534 ms against 1,357 at 2048,
    +13%**, memory unchanged (8.13 GB); at 512 no cost is readable under the
    contention (1,101 against 1,135). A boolean mask takes SDPA off flash and
    skips nothing, so it pays extra *not* to attend. A block-sparse kernel
    (FlexAttention, or flash's varlen path) would skip the masked blocks and
    could recover up to the 16%; not measured, because it is a model change.
  * **What the window shows.** At 2048, 61% of tokens sit in a document wholly
    in view (35% at 512) and 25% are read without their document's opening
    (49%). The wider window shows more documents whole although it packs more
    of them.
  * **Whether attending across a boundary hurts what he learns** is a quality
    question, not a cost; it would show in P1, which has no arm for it.

**The slice packing bites is the one 2048 is for.** C9's conversation build at
2048 (`gen_conversation.py --block 2048 --turn-reserve 21`, 1,144
conversations, a scratch build -- **probe only, not on disk**): median **887
tokens**, p90 1,594, max 1,816, ten turns at the median. Under random offsets
**only 49% of its tokens are in a conversation wholly inside the window, and
24% are read without its opening** -- for a slice whose point is a follow-up
reaching 6-18 turns back, the antecedent is before the window often enough to
matter. The repo has the fix in kind: arm A's `align_parse_blocks`
(`corn/data.py`) snaps an offset that lands inside a parse transcript back to
its first token, leaving every source's delivered share unchanged; the same
rule on the conversation source would put every 2048 window over a whole
conversation at no compute cost. Not built and not decided -- a sampler choice
for P1 and the owner. The on-disk 1024 build reads 331 / 536 tokens, 80% whole
at 2048.

## 5. What it changes

  * **PLAN-1-0 §4's three unmeasured costs are measured**: training 1.06x and
    1.20x, not ~1.3x and ~2x; fine-tune memory unchanged at equal tokens;
    decode free on a short turn and 100 tok/s deep in a full window as
    shipped. Its "Cost" section moves with them.
  * **D2.** P0 finds no cost that rules out 2048 for training or for the
    fine-tunes. The price of 2048 is paid at serving, and only by a
    conversation long enough to use the room; and the packing question goes to
    P1 with one sampler option attached.
  * **The 1.0 run**: ~8 h and ~$30 at 2048, from 6 h 43 m and $25.52.

## Reproduce

    python -m corn.trainbench --config configs/corn_jr_260m_v4.py --compile --block-size 2048 --batch-size 2 --grad-accum 6
    python -m corn.trainbench --config configs/corn_jr_260m_v4.py --compile --block-size 2048 --batch-size 2 --grad-accum 6 --doc-len 150
    python -m corn.bench --config configs/corn_jr_260m_v4.py --dtype float32 --block-size 2048 --paths graph+sampling --buckets --compile-step --prompt-len 1792
    python scripts/probe_block_packing.py
    python scripts/check_decode.py --compile

each through `scripts/gpu.py run`; the block, batch and dtype of every row are
in `evals/results/block_costs__160.json`.
