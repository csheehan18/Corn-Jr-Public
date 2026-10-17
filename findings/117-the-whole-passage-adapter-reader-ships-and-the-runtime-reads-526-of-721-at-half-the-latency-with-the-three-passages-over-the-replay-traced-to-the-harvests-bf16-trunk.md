# 117. The whole-passage adapter reader ships, and the runtime reads 526 of 721 at 199 correct silences in 23 ms a passage -- three right answers over the replay's 523, every one of them the harvest's bf16 trunk against the runtime's fp32 one

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**Run 2026-09-05 on the frozen `corn_jr_260m_v4_ft4g` trunk. No weight of the
trunk moves and none is trained here: the adapter and its head are
`checkpoints/reader_whole_causal_s1.pt`, the file finding 112 trained and
finding 116 re-read. `corn/extract.py`'s `reduce`, `grounded`, `det_repair`
and `_canonical`, `corn/gate.py`, every scorer and every frozen eval row are
untouched, and the server's reader is still `generate`. This is
`docs/PLAN-READER-PORT.md` -- wiring, guards, verification -- and it contains
no new experiment.**

The hundred-and-twelfth finding measured a whole-passage reader that existed
only inside `scripts/train_reader_whole.py`: an adapter bound onto a trunk in
the training process, a head that never left that file, and a harvest of spans
and margins replayed by `probe_harvest_paired.read_at_bar`. Finding 116 re-read
it at 523 of 721 under the repaired grounding rule. What neither could say is
whether Corn-Jr can *answer* through it, because between that harvest and a
live turn sit `corn/model.py` (which had no adapter and no attention
argument), `corn/reader.py` (which had no whole-passage head),
`corn.extract.read_passage` (which always cut), `harness/backends/read.py` and
`harness/serverconfig.py`. This file closes each of those and then reads the
whole thing end to end.

## What ships

    adapter + head   checkpoints/reader_whole_causal_s1.pt   one file, both
    attention        causal, read off the file's own args
    extent rule      d = 2.0, radius 3                       unchanged
    reduce           one window, so one vote                 unchanged
    threshold        -1.174                                  when he speaks at all

`corn/model.py` gains `LoRALinear` on `c_attn`, `c_proj`, `c_fc` and `c_proj`
of every block -- base held by reference, never written, **off unless a forward
turns it on** -- a `causal: bool = True` argument threaded to
`CausalSelfAttention.forward` as `is_causal = T > 1 and causal`, and
`load_adapter`, which keys a file to the trunk's sha256 and refuses a mismatch.
`corn/reader.py` gains `WholeHead` (the trainer's arithmetic, ported) and
`WholeHeadReader` (a `run` in `read_passage`'s sense), with the reply-rendering
half both readers share factored into `_Speaks` so there is one place a
threshold is compared. `read_passage` gains `whole`, which is the cut not being
made. `Reader(reader="head_whole")` builds it; `harness/serverconfig.py` gains
`reader_adapter` and `reader_whole_threshold`. **`generate` is still the
default.**

**Three things are decisions rather than readings, and are recorded as such.**

  * **`WHOLE_THRESHOLD` is -1.174**, the mean of the two cross-validated fold
    values (-1.094 / -1.254) under the bar protocol -- `right` subject to the
    fold's share of 200 correct silences -- exactly as `READER_THRESHOLD` is
    the mean of -1.980 / -2.061. It is **not the same quantity** as
    `READER_THRESHOLD`: that margin is a stacked verifier's logit and this one
    is `max s - s_null` off the head's own softmax, so the two carry separate
    config fields, separate validators, and a guard asserting they are not each
    other.
  * **Seed 1 ships**, on finding 87's reasoning. Seed 2 reads 517 against seed
    1's 523 on Population A and Population A is the population the arm is
    *measured* on, so choosing between them by that number would be selecting
    on the test population.
  * **The adapter names its trunk.** `train_reader_whole.py` now writes the
    trunk checkpoint's sha256 into every file it saves, and
    `scripts/stamp_adapter.py` put it into the two checkpoints finding 116 was
    measured on without retraining them (both read `985240095e80`, the ft4g
    trunk). A low-rank delta on the wrong weights loads without error and reads
    nonsense, and the trunk *will* move -- the social workstream is fine-tuning
    it -- so this is the expected accident rather than an exotic one.

## (a) The runtime, end to end, at the shipped constant

`scripts/probe_reader_runtime.py`, finding 87's instrument, extended with a
`--reader` argument: the real `Reader` handed `(question, passage)` 1,003
times, whatever comes back scored by `probe_reader_passages.judge` --
`score_extract_tight` on `reduce`'s output, the scorer every arm on this
population has been read on, unchanged. Both readers run through it on the same
day on the same card.

    arm                    answerable 721            unanswerable 282
                        right  wrong  silent      silent  wrong   joint
    gate on (recorded)    230     99     392         256     26      486
    gate CV               275    154     292         228     54      503
    head (runtime)        392    192     137         199     83      591
    head_whole (runtime)  526    122      73         199     83      725

    gate on (recorded)  precision 64.8%, acc|att 0.699, attempt rate 45.6%
    gate CV             precision 56.9%, acc|att 0.641, attempt rate 59.5%
    head (runtime)      precision 58.8%, acc|att 0.671, attempt rate 81.0%
    head_whole          precision 72.0%, acc|att 0.812, attempt rate 89.9%

    the hybrid fallback fired on 90 passages for `head` and 0 for `head_whole`

**526 right at 199 correct silences**, against the plan's bar of 523 and 198
"to within one passage each". Correct silence is within one. **`right` is three
over, and the whole of (b) is why** -- it is not a wiring difference, and the
bar is met under the numerics the bar was set in.

**The window head is the control that makes that claim checkable**, and it is
the reason both arms were run. `--reader head` through the same instrument on
the same day reads **392 right at 199 correct silences**, which is finding
116's replay of that arm *to the passage* -- 392 and 199 there, 392 and 199
here, nothing apart. The window head's harvest was written by a probe running
the trunk the way the runtime runs it; the whole arm's was written inside a
training process. So `read_passage`, `reduce`, `judge` and the threshold
comparison reproduce a replay exactly when the replay's trunk is the runtime's,
and the three passages are the one thing that differs.

## (b) The three passages, traced

Six passages read differently in the runtime from the replay at the same
constant threshold. They net to +3 right and +0 correct silence:

    class    replay -> runtime   the replay's span            margin      t = -1.174
    answ     wrong  -> silent    '~ 0.116 mm'                 -1.1417     crossed t
    answ     wrong  -> right     'sometime in 2018'           +0.3902     span moved
    answ     wrong  -> right     'Archaea'                    -0.5118     span moved
    answ     wrong  -> right     'Florida'                    +0.0829     span moved
    unans    silent -> wrong     'Cadillac Mountain'          -1.1777     crossed t
    unans    wrong  -> silent    'Commander in Chief'         -1.1402     crossed t

Three are margins within 0.04 of the threshold falling on the other side of it;
three are spans changing on passages nowhere near it. Both are what a small
perturbation of the head's inputs looks like, and the rest of this section is
where the perturbation is.

**It is not the head.** On identical states, the ported `WholeHead` scored per
row against `train_reader_whole.BatchScores`' padded batched enumeration --
the path the harvest was actually written through -- differs by **0.00007 at a
score scale of 96.55**, moves the margin by 0.00001, and moves no argmax. On
canned states `scripts/check_extract.py` holds the port **bit-identical** to
the trainer's over 520 pairs with the argmax exact.

**It is the states.** The harvest reads them through
`train_reader_whole._trunk_states` under `torch.compile(dynamic=True)` and
**bf16 autocast**; the runtime reads them through `corn/model.py`'s own fp32
forward, hooked. On one batch of five passages the two differ by **4.006** in
`h`, which carries through to **1.247** of score and **0.106** of margin.

Population-wide, the live fp32 reader against the harvest, 1,002 passages read
on both paths (the 1,003rd is over the 512 block on both and silent on both):

    spans string-identical                  985    98.30%
    un-extended argmax identical            986    98.40%
    worst margin gap                        0.19005
    median margin gap                       0.021235
    mean margin gap                         0.029195
    margins landing on the other side of t        3

Sixteen of the seventeen differing spans are the head's own pick moving, not
the extent rule breaking a tie the other way.

**And the control that closes it: the same wired path with the trunk under the
harvest's bf16 autocast reads 524 right at 198 correct silences** -- inside the
bar on both columns, and inside finding 87's own tolerance of the replay. The
port passes its bar under the condition the bar was measured in, and reads
three more under the condition the runtime actually serves.

Two things this rules out. **TF32 is not it**: `train_reader_whole.py:839` sets
`allow_tf32 = True` and the runtime does not, and turning it on in the runtime
changes nothing at all (526 / 199, median gap 0.021269). **Nor is the fp16
store**: there is no store here -- unlike finding 87's (a), where the
comparison was a harvested fp16 cache against a live fp32 trunk and the worst
margin gap was 0.0015. This gap is 130 times that, because bf16 autocast rounds
at every one of seventeen layers where a store rounds once at the end.

**So the runtime is the more precise of the two paths and reads three more
right answers than the file it is checked against.** That is stated as what it
is rather than banked: the honest number for this arm on Population A remains
finding 116's **523**, measured under the harvest's numerics on a population,
and **526** is what the runtime does with the same weights. Nothing about the
ordering of the two arms depends on which is quoted.

## (c) Paired against the window head, through the runtime

Both arms' verdicts come from the same instrument on the same passages, so the
comparison is paired rather than two cards side by side. McNemar:

    against `head` (runtime)      net    lost   won    p
    joint bit                    +134     62    196    2.2e-17
    right answers                +134     27    161    2.0e-24
    correct silences               +0     35     35    1.0

**It buys 134 right answers and spends nothing.** That is the difference
between this arm and the window head that shipped in finding 87, which bought
107 right answers over the gate and spent 27 correct silences: the
whole-passage reader's willingness lives in the same softmax as its pick, so
raising one did not cost the other. Correct silence is 199 for both arms and 35
passages move each way underneath that, which is the honest shape of a "no
change" -- the net is zero and neither half is nothing.

The species the windows caused are gone rather than reduced: the hybrid
fallback fired on **90** passages for the window head and **0** here, because a
single reply cannot disagree with itself. The whole apparatus of votes,
aggregation and disagreement fallback is dead code on this path, kept rather
than switched off because a dead branch that is the same code is a fact about
the input.

## (d) Latency, per passage, both arms on the same card

The clock is around `Reader.__call__` and nothing else -- the load, the scoring
and the two gate replays are outside it. 1,003 passages, idle 3080, fp32:

    arm            mean      median    p90       max       total
    head           42.7 ms   40.1 ms   67.0 ms   132.6 ms  43 s
    head_whole     23.2 ms   23.0 ms   25.0 ms   131.0 ms  23 s

**1.84x on the mean and 2.7x at p90**, and the shape is the point rather than
the ratio. The window reader is one forward per window over one to eight
windows, so its cost is the passage's length and its p90 is 67 ms; the whole
reader is one forward whatever the passage is, so its median and its p90 are
2 ms apart. The two maxima are both about 131 ms and are not a passage: a
separate eight-passage run of the whole arm read 130 ms on its first passage
and 20-30 ms on every one after, so it is a warm-up both arms pay once. That is
why the means separate and the maxima do not.

So the arm that reads 134 more right answers is also the cheaper one, and it is
cheaper for the same reason it is better: there is one read of the passage
instead of eight reads of pieces of it.

## (e) The guards

`scripts/check_model.py` is new and is `check_all.py`'s sixty-eighth. It proves
a negative, and it proves it against a copy of the arithmetic rather than a
description of it: `_before` writes out the pre-port block and attention
forward, and a seeded trunk is held `torch.equal` to it in three configurations
-- adapter absent, adapter present and off, adapter present and on with `b` at
the zero it is initialised to -- with two controls that stop those from being
vacuous (a non-zero `b` must move the forward, and `causal=False` must move
it). It also holds `corn.model.LoRALinear` equal to
`train_reader_whole.LoRALinear` on a drawn delta, and drives `load_adapter`
against a matching trunk, a different trunk and an unstamped file.

`scripts/check_extract.py` grows the whole arm's sections:

  * **The head is the trainer's, score for score**, on canned states with no
    checkpoint near it: bit-identical over 520 pairs, the argmax exact, the
    null equal, and the margin `max s - s_null` as `load_reader_harvest`
    computes it. The bar written into the guard is the plan's 1e-4 of scale;
    what it actually reads is 0.
  * **The whole path asks once, about the passage uncut**: the head is called
    once where the window reader is called three times on the same fixture, the
    window it is asked about is the passage byte for byte, the one reply comes
    back through the real `reduce` as "1 of 1 windows extracted it", a passage
    a hair below the threshold abstains with the runtime's own decline behind
    it, the hybrid fallback is unreachable, an empty passage is still empty
    rather than one empty window, and a gate over a whole passage is refused
    rather than applied to it.
  * **The constants are held equal**: `ServerConfig().reader_whole_threshold`
    against `corn/reader.py`'s, `head_whole` is a value `--reader` takes, and
    the two thresholds are asserted **not** to be each other.
  * **Layering** is unmoved: `corn/reader.py` now imports `corn.model` as well
    as `corn.gate` and `corn.toolgen`, all three inside the runtime closure.
    `scripts/check_layering.py` is green.

`scripts/check_read.py` gets the one-window read: one prompt where the cut
would have made several, and the window named is the passage.

**The full sweep reads 68 guards and two fail: `check_churn.py` and
`check_copyable.py`.** Both fail identically at the commit this session started
from (`56c33733`) in a clean worktree with the same messages and counts, so
neither is this session's -- finding 116 §3 reports the same two for the same
reason.

**One guard that is not here, and why.** Finding 87's (a) is
`scripts/check_reader_popa.py`: every window of Population A through the wired
head against the harvest, spans string-identical at a bar of 99%. The same
guard for this arm would read 98.30% and be red, and it would be red for the
reason (b) sets out -- the harvest's trunk is not the runtime's. A guard that
sits red is a comment (rule 7), and a guard whose bar is set to pass a known
numerical difference is worse than none, so the comparison is reported here as
a reading instead. It becomes a guard the day this arm's harvest is regenerated
by a probe that reads the trunk the way the runtime does.

## Limits

One trunk, one seed, fp32, one population. The threshold is a constant of a
checkpoint and a population and not of the model: the next trunk gets its own
`train_reader_whole.py` run and its own bar-protocol read, and the adapter is
retrained with it -- which is what `load_adapter`'s fingerprint is for. Nothing
here is a live session; finding 87's (f) read fourteen real questions through
the provider and this arm has not been through that, and the reader only ever
sees what retrieval hands it either way. Nothing here measures packs, which is
where the extraction gains were expected to transfer and where no reader number
exists yet. The scorecard still has no reader in its path at all (finding 87
(d)), so there is no `--reader head_whole` column on any card and the frozen
rows are invariant to this session by construction. **And the server default is
unchanged**: `generate` until the owner flips it, as it was for `head`.

## On disk

`evals/results/reader_runtime_whole_s1.json` (the read above, per passage),
`evals/results/reader_runtime_s1_grounded115.json` (the window head through the
same instrument on the same day, which is the control in (a) and the latency in
(d)).
