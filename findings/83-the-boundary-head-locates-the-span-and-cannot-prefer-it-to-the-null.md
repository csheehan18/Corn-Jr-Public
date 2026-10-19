# The boundary model finds answers but can't prefer them to silence

**Full result:** The boundary head locates the span and cannot prefer it to the null

**Cost:** 6.3 min of scoring on the 1 card first cited here (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**`docs/PLAN-EXTRACTION-READER.md` R1, run 2026-09-01/02 on the frozen
`corn_jr_260m_v4_ft4g` trunk, fp32, two seeds of the head plus their synthetic
arms. Every pre-registered bar fails on every arm, the pre-registered failing
branch fires four times out of four, and the mechanism is not the one the
branch names.**

## What was run

A pair scorer `s(i,j) = w gelu(A h_i + B h_j + C (h_i * h_j))` over block
outputs at layers {8, 12, 16}, `0 <= j - i < 16`, plus a null logit
`s_null` read at the say marker; one cross-entropy over every valid pair and
the null, with all occurrences of a gold summed. The trunk never saw a
gradient. Training data is `data/raw/spans_nq.jsonl` (R0-a): 80,000 windows
sampled at the file's natural **24.8% positive** balance, 75,788 train /
4,212 held out **by article** on seed 1 and 76,013 / 3,987 on seed 2, two
epochs at ~643 s each. The head is 3.1M
parameters. Scored by rendering its span as the worker's own `It's {a}.`
through the real `reduce` and the frozen scorers, so every number lands on
the existing ladder and no scorer or row was touched.

The threshold is cross-validated on the frozen eval and applied cold to the
phrase eval (house rule 4); Population A's is cross-validated separately by
`scripts/probe_reader_passages.py`.

## The bars

    bar                                  s1 NQ    s1+syn   s2 NQ    s2+syn   reference
    (a) frozen joint(tight) >= 270         227      229      231      229    gated 236, base 214
        frozen tight >= 125/200   gated     34       57       49       52    ceiling 193
                                ungated     84       89       84       95    greedy 94, base 93
        frozen abstain >= 150/200          193      172      182      177
        the CV joint, the quotable one     224      225      229      222    gated 236
        McNemar vs the gated runtime       -16      -14      -12      -14    its joint 243
                                p         .068     .151     .182     .130
    (b) phrase tight >= 45/89     gated      3        8        6        5    greedy 24, ceiling 85
                                ungated     18       20       13       14
        phrase abstain >= 40/53             53       46       51       51
    (c) `other` acc|att >= 0.50   gated   .250     .429     .273     .100    from 0.278
                                ungated   .140     .161     .086     .108
        name                    ungated   .529     .559     .544     .544    generative .636
        number                  ungated   .283     .300     .250     .417    generative .688
    (d) extract.paired >= 122/128           68      107       81      109    base 117, ftnames2 126
        took_first <= 3                     21       10       28        5
        sibling spoken < 4                  25       19       35        9    veto 0, ft4g 12
    (e) Population A right, of 721         172      189      204      216    null 279
                                         23.9%    26.2%    28.3%    30.0%    null 38.7%
        joint                              407      395      427      443    null 464
        net vs the null                    -57      -69      -37      -21
                                p        .0017    .0001    .0359    .2505
        unanswerable silent, of 282      83.3%    73.0%    79.1%    80.5%    null 65.6%
        precision                        46.6%    40.5%    46.7%    50.1%    null 46.8%
        acc | att                        0.534    0.483    0.540    0.574    null 0.559
    (f) phrase margin AUC >= 0.75       0.4444   0.7727   0.7143   0.8250    probe_spanhead 0.4348
                     over n attempted        9       19       13       13
        the same AUC, all 89 attempted  0.5970   0.5754   0.6822   0.6714
        frozen AUC at the threshold     0.7620   0.7538   0.7469   0.6381
        frozen, all 200 attempted       0.7433   0.7690   0.7369   0.7043
    selection: held-out positives       0.0547   0.1101   0.0431   0.0530
               held-out nulls           0.9865   0.9857   0.9983   0.9963

Population A's joint is paired against `multiwindow_ft4g.json`'s recorded
`off+off` verdicts: on seed 1 **net -57 (188/131, p = 0.0017)** for the NQ arm
and **-69 (196/127, p = 0.0001)** with the synthetic slices; on seed 2 **-37
(p = 0.0359)** and **-21 (p = 0.2505)**. Three of the four arms are
significantly worse than the ungated generative null on the population the
runtime reads in and the fourth is indistinguishable from it. None is better.

**Two corrections to the seed-1 column as this file first recorded it, made
when the seed-2 numbers were put beside it.** The `(f)` row quoted the
*ungated* values in the *gated* slots for the NQ arm: at its own
cross-validated threshold that arm reads **0.4444 over 9 attempted** on the
phrase file, not 0.5970, and **0.7620 over 45 attempted** on the frozen file,
not 0.7433. 0.5970 and 0.7433 are its all-items numbers and are still on the
rows that say so. The synthetic column was right as printed. Neither
correction moves a pass or a fail -- both readings are under 0.75 -- and both
are numbers this file quoted, so they are fixed here rather than left to be
re-derived.

## The mechanism, and it is not what the branch named

The pre-registration said (a) under 250 or (b) under 35 means the frozen
mid-stack representation does not carry the boundary, and R2 runs. Both fire.
But the selection metric says something more specific, and it only says it
once split by class.

Held-out argmax accuracy read **0.7593 then 0.7600** across the two epochs,
which looked like a converged plateau. The held-out slice is 24.3% positive,
so **answering `null` to everything scores 0.757.** Split, all four arms:

               nulls    positives
    s1 NQ     0.9865      0.0547
    s1+syn    0.9857      0.1101
    s2 NQ     0.9983      0.0431
    s2+syn    0.9963      0.0530

**The head declines 94.5% of gold-bearing windows on seed 1 and 95.7% on seed
2, and the synthetic arm's relief from that does not replicate** -- 0.1101 on
seed 1 against 0.0530 on seed 2, which is most of the way back to the NQ arm.
The null column is above 0.98 on every arm. It has not failed to
locate the span: with the null out of the argmax it reads **84/200 tight on
both seeds** of the NQ arm, 42% of the file, and 89 and 95 on the synthetic
arms. It has failed to *prefer* the span to the null.
The loss agrees quantitatively -- 1.0110 at 24.8% positives is about 4.0 nats
on a positive row, so the gold pair carries roughly 1.8% of the mass against
a uniform 0.09% over ~1,100 candidates. The head concentrates about twenty
times on the right pair and still loses the argmax to `s_null` on almost
every one.

**The synthetic arm is the closest thing to a control on that reading, and it
moves in the predicted direction on every axis.** `spans_synth.jsonl` is 59%
positive, so adding 20,000 of its windows takes the training mix from 24.8%
to 31.6% positive -- a modest shift -- and the positive column of the
selection metric goes **0.0547 to 0.1101**, gated frozen tight **34 to 57**,
`other` **0.140 to 0.429**, `extract.paired` **68 to 107** with `took_first`
**21 to 10**, and the held-out verifier AUC **0.597 to 0.773**. The reading is
confounded -- those files were built to teach pointing, so content and balance
moved together -- but nothing here is consistent with "the states do not carry
the boundary" alone.

**Seed 2 keeps half of that and drops the other half.** The two axes that are
about *pointing* replicate and get stronger: `extract.paired` 81 to 109,
`took_first` 28 to 5, sibling answers 35 to 9 -- the best clause-flip numbers
any arm here produced. The two that are about *preference* do not: the
selection metric's positive column goes 0.0431 to 0.0530 rather than
doubling, and gated frozen tight goes 49 to 52 rather than 34 to 57. So the
synthetic files buy the ability to choose between two rival spans, on both
seeds, and buy little or nothing on the decision to speak at all. That split
is a sharper reading than seed 1 alone allowed, and it is the reason the
confound is worth separating rather than accepting.

**So the honest statement is that R1 as specified fails, and it fails in a way
that is at least partly about the class balance of the objective rather than
only about the representation.** An unfrozen trunk in R2 would not
distinguish the two, which is worth knowing before an hour of GPU is spent
deciding between them.

## The seed spread, and it is larger than most of the gaps in the table

Rule 6 exists because a one-seed reading is not a direction, and here it earns
its keep. Between the two seeds of the same NQ arm, with the same data,
objective and threshold protocol:

    gated frozen tight        34  vs  49        (+15, on a bar of 125)
    Population A right       172  vs 204        (+32 passages, of 721)
    extract.paired            68  vs  81        (+13, on a bar of 122)
    sibling spoken            25  vs  35        (+10, on a bar of 4)
    Population A net          -57 vs -37

and across all four arms Population A's answerable-right runs **172 to 216**,
a spread of 44 passages or 6.1 points. **Most single-arm gaps this file
reports are smaller than that.** The synthetic arm's headline gain on seed 1,
gated tight 34 to 57, is +23 against a seed spread of +15 on the same
quantity; its Population A gain of +17 sits inside a seed spread of +32.

**What this does and does not license.** It does not weaken the finding: every
arm fails every bar by margins far outside the spread -- the nearest miss is
`(a)`'s joint at 231 against 270, and gated tight's best is 57 against 125.
It does mean that no *within-arm difference* on this file smaller than about
15 points on the frozen eval or 35 passages on Population A may be read as a
direction, and that includes most of what the synthetic arm appeared to buy on
preference. The pointing gains survive the test because they are larger than
it: `took_first` 21/28 down to 10/5 is a change of the same sign and rough
size on both seeds.

## Bar (d) reads in the arm's favour, by its own written rule

The plan says: if the synthetic arm buys nothing on NQ and buys paired, it
rides anyway; if it costs NQ, it is dropped and the cost is the finding. It
**buys on both** -- NQ frozen tight 34 to 57 and paired 68 to 107 on seed 1,
49 to 52 and 81 to 109 on seed 2 -- so it rides. It does not reach the bar on
either seed: paired 107 and 109 against 122, `took_first` 10 and 5 against 3,
and 19 and 9 sibling answers spoken against a bar of 4 and the retired veto's
0. **Seed 2's synthetic arm is the closest anything here comes**: 109/128 with
`took_first` 5 and 9 siblings, which is a real improvement on the 25 and 35 the
NQ arms speak and still more than double the bar. The clause-flip regime is
not fixed by a boundary head trained this way.

## What survives, and it is the one thing the record asked for

**(f) reads 0.7727 on the held-out phrase file with the synthetic arm, and
0.8250 when seed 2 repeats it** -- above the pre-registered 0.75 on both
seeds, on the file that killed the previous
candidate. It is the only bar anything here passes and the only one that
replicates. The NQ arm does not pass it on either seed (0.4444, 0.7143), so
what replicates is the synthetic arm specifically.
`probe_spanhead`'s confidence read 0.62 on the frozen eval and
**0.4348** on the phrase eval, below chance, and the eighty-first finding
retired the isolated score as a willingness meter at 0.5288 on the identical
question. Every margin on this project's record reads 0.53-0.67 frozen and at
or below chance held out.

**And it is a weaker result than that sentence makes it sound, in a way this
file found by measuring the other end of it.** The bar is `AUC | attempted`,
and `attempted` is whatever the threshold admits -- **19 of 89 items on seed
1 and 13 on seed 2**. Drop
the threshold so every item is attempted and the same heads on the same file
read **0.5754** and **0.6714**. So the margin separates correct from wrong *within the
band it is already confident about* and is close to uninformative over the
whole file. That is a real property and not a null -- a verifier that works
on its own confident subset is still a verifier -- but the pre-registered
number is a subset number and quoting it without the all-items number beside
it would be the thirtieth finding's shape, a figure with no floor attached.
The floor is the part that improves least across seeds: 0.5754 and 0.6714.

The claim it supports is "there is a correctness signal here worth a proper
measurement", not "the verifier is built". `corn/gate.py`'s willingness is a
*presence* detector (AUC 0.7863 answerable-vs-empty, 0 of 12 clause-flip
catches); this is a *correctness* signal, and the two are the pair the sealed
read said nobody had tested together.

## What this retires and what it does not

**It does not retire the plan's §1.3 argument.** That argument was that
`probe_spanhead` beat generation under five handicaps and the missing null
class was the reason it did not survive its gate. This file supplies the null
class and the head still loses to generation -- **84 to 95 ungated across
four arms against greedy's 94**, and worse in every type bucket rather than
better on names -- ungated `name` 0.529-0.559 against the generative arms'
0.636, `number` 0.250-0.417 against 0.688, `other` 0.086-0.161 against 0.278
-- which is not `probe_spanhead`'s shape, where names improved and phrases
did not. Only one arm of four reaches greedy at all, and it does so on the
type buckets' worst spread. What it shows is that a null class is not free: it
is a class the objective can collapse onto.

**It does not test R2.** The trunk was frozen throughout, by design, so
nothing here says what an unfrozen reader trunk would read.

**It does not test the plan's own scale.** 80,000 of 403,234 available
windows, two epochs, `HIDDEN = 256`. Two head seeds now, so rule 6 is
satisfied and the numbers are directions; the scale is not. The
`--positives-only` probe below was built to test exactly that and did not
finish.

## The three suspects, and how far the separation got

**R1's failure has three candidate causes and only one of them justifies R2.**
The head is **underfit** -- 3.1M parameters, `HIDDEN = 256`, two epochs,
80,000 of 403,234 windows. The **null class** is collapsible in a shared
softmax and demonstrably collapsed. Or the **frozen representation** does not
carry the boundary. R2 unfreezes the trunk, which moves the third while
leaving the first two exactly where they are: a pass would not say which was
fixed and a fail would not say which was fatal. **So R2 cannot be the
experiment that chooses between them**, and running it first buys an hour a
seed of uninterpretable evidence.

**The diagnostic is `train_reader.py --positives-only`**, pre-registered in
that file's docstring on 2026-09-02 before it ran. It removes the null
entirely -- gold-bearing windows only, softmax over the candidate pairs with
no null term -- so the only thing the objective can express is *which pair*,
and it spends the freed budget on the other two suspects: all **100,084**
positives rather than an 80,000-window sample, `HIDDEN` 512, six epochs,
selection on held-out exact-pair accuracy. Scored ungated through the same
`reduce` and the same frozen scorers. Its primary bar is **frozen tight
ungated >= 125/200** (ceiling 193, greedy 94, R1 read 84-95): a pass means the
states carry the boundary and R1's failure was the null; **under 100 on both
seeds means the representation is the limit and R2 is justified as written.**

**It ran on seed 1 and was stopped in epoch 3 at the owner's call, so no bar
was read.** The trainer wrote `--head-out` only after the epoch loop, so no
head reached disk and neither eval was scored. What survives is the curve:

    epoch 0    loss 2.1774    held-out exact-pair 0.3492    834 s
    epoch 1    loss 1.6945    held-out exact-pair 0.3348    833 s
    epoch 2    loss 1.3853    held-out exact-pair 0.3428    832 s
    epoch 3    killed at step ~2800, running loss 1.2528

**One suspect moves and it is the first.** This file read R1's ~4.0 nats on a
positive row as the gold pair holding ~1.8% of the mass, "concentrated
twentyfold on the right pair and still losing to `s_null`" -- and treated that
as a statement about the objective's balance. **One epoch of the larger head
reaches 2.1774 and two reach 1.3853**, on the same frozen trunk and the same
labelled rows. R1's head was not converged on the positive class at all, so
its loss was a fact about a two-epoch budget on 80,000 windows and not about
what the states carry. **The sentence "the head concentrates about twenty
times on the right pair" stands as arithmetic and is retired as evidence about
the representation.**

**The second reading points the other way and is weaker.** Training loss falls
37% across three epochs while held-out exact-pair sits at 0.3492 / 0.3348 /
0.3428 -- flat inside its own noise on a 4,880-row slice. Capacity and epochs
buy training fit and not generalisation, which is the shape of a
representation ceiling. **But this is not the pre-registered bar.** It is
exact-pair argmax on a held-out slice of `spans_nq.jsonl`; bar (a) is `tight`
on `evals/extract.jsonl` through the real scorers. Nothing on the record maps
one to the other, and R1's arms cannot calibrate the map, because their
positive column was crushed by the null while their ungated `tight` was not.

**So the honest state is: underfit is retired as the explanation of R1's loss,
the null class remains the demonstrated mechanism of R1's failure, and the
representation is neither convicted nor cleared.** The number that would
decide it -- frozen tight ungated against 125 -- has not been read on either
seed. **R2 should not run on this evidence**: the case for it is one flat
held-out curve over three epochs on the wrong population, and the diagnostic
built to settle it is an hour a seed away from finishing.

### A measurement condition, measured rather than assumed

Both trunk-forward conditions on the same 8,000-positive prefix, `HIDDEN =
512`, one epoch, seed 1:

    fp32            loss 3.5611    held-out exact-pair 0.2911    67 s
    bf16 autocast   loss 3.5620    held-out exact-pair 0.2582    37 s

bf16 is 1.8x faster and its loss is **identical to three decimals**, so it
does not distort the objective. Held-out exact-pair moves **3.3 points in the
unfavourable direction**, and bar (a) is itself a location-accuracy number, so
the deciding arm was run fp32 -- R1's own condition, no new variable on the
number that decides R2. Recorded here because it is reusable: it is what
`scripts/harvest_states.py` cites for storing fp16 states from an fp32 trunk
rather than harvesting under bf16.

## The suspects, separated

**The probe above finished on 2026-09-02, off the state cache, and the answer
is that the frozen states carry the location and the head was the thing that
could not ask for it.** Three arms, two head seeds each, six epochs, all
100,084 positives, `HIDDEN` 512, positives-only, scored ungated through the
same `reduce` and the same frozen scorers. What changed between the arms is
one term at a time and nothing else.

### The measurement had to be fixed twice before it was worth reading

**The epoch went from 834 s to 111.** `scripts/train_reader_cached.py` trains
off the harvested cache, and its first form still walked a Python loop around
every window of every micro-batch: a pair index, a `pair_slot` lookup, a
host-to-device copy of the gold slots, two `logsumexp` calls, and in the
held-out pass an `.item()` -- a device synchronisation -- per window.
`padded_scores` keeps the window axis instead of concatenating it away, and
the padding needs no re-indexing anywhere because of how the enumeration is
ordered: `pair_index` walks `j` outward and gives `j` a block of
`min(j, 15) + 1` pairs, so **a slot's index does not depend on `n`**. Width
`N`'s enumeration is width `n`'s followed by the pairs whose `j` is past the
end, the valid set is exactly `jj < n`, and `pair_slot` is the same map at
either width.

    the live fp32 trunk, per window        834 s
    the cache, per window                  263 s
    the cache, padded and masked           111-171 s

**The remaining spread is the page cache, and it is the floor.** F: reads
**0.44 GB/s cold** against an epoch's **38 GB** of fp16 states, so ~90 s of
the 171 is disk that no batching removes and the 111 is a warm re-read. The
arithmetic is ~3e14 FLOPs, which is seconds. This loop is I/O-bound and the
card is the cheap part.

`--check-batched` is the assertion, on real windows rather than random input:
pair scores agree to **4.7e-6 of their own scale**, **0 argmax pairs move**,
and **208/208 query rows equal the cache's say-marker row exactly** -- the
last because a pointer arm whose query was a pad row would train, would
improve, and would be measuring nothing.

### The gap to the live path is not the initialisation either

The cached loop reads held-out exact-pair 0.42-0.43 where the live loop read
**0.3492** on the same rows, and reaches a *higher* training loss doing it.
The list of what it is not is now complete enough to be worth stating as one:

    the features            0.5% of the loss over 400 lockstep steps
    the batched scorer      0.06% of the loss over the same
    the padded scorer       4.7e-6 of a score, 0 argmax pairs moved
    the evaluation          0.4320 vs 0.4320 on the same weights, the
                            second read through a live fp32 trunk forward
    the data                100,084 (id, wi) identical to spans_nq.jsonl,
                            0 articles and 0 gold spans differing
    the held-out split      the same 4,880 windows as the live path's at
                            seeds 1, 2 and 3; 0 of 1,555 held-out articles
                            appears anywhere in training, asserted every run
    batch composition       bucket batching reads 0.4164 against 0.4186
    the epoch's order       the live shortest-first walk reads 0.4217
    the step count          6,048 live against 5,951, 160 length groups
    the initialisation      the live path's own draw reads 0.4260 here

**The initialisation was the last suspect with a mechanism and the three-seed
spread could not speak to it**: `train_reader.main` seeds, builds the 260M,
and *then* draws `PairHead`, so the live head's initial weights come from a
point in the generator's stream no `--seed` on the cached path can reach.
`--init-live` reaches it, rebuilding the trunk shell for its draw alone:

    cached, seed 1's own draw       loss 2.2364    exact-pair 0.4256
    cached, the live path's draw    loss 2.2216    exact-pair 0.4260
    the live path, that same draw   loss 2.1774    exact-pair 0.3492

Same head, same starting weights, same 95,204 windows, same 4,880 held out,
**seven points apart**. The signs point one way and it is not proved: the
cached loop's held-out column *rises* across epochs where the live one *fell*
while its training loss fell 37%, which is a regulariser's shape, and the one
candidate with that shape is the fp16 store rounding states whose coordinates
run to ~80. It was excluded as a *loss* difference, and a loss difference is
not what a regulariser shows up as. **It is reported rather than explained,
and the arms below are read against the cached base arm for that reason.**

### The pointer arm's first run was an artefact, and the loss said so

As first written the query term read the raw states, and `1/sqrt(H)` is the
right scaling for unit-variance inputs while these are block outputs whose
coordinates run to ~80. It read:

    epoch 0    loss 23.2192    held-out exact-pair 0.3941
    epoch 1    loss 26.1455    held-out exact-pair 0.4406
    epoch 2    loss 27.1240    held-out exact-pair 0.4301
    epoch 3    loss 27.1369    held-out exact-pair 0.4457

**A cross-entropy over ~875 pairs is ln(875) = 6.77 nats at uniform and the
base arm reads 2.24**, so 23 to 27 is a softmax saturated on one wrong pair,
and a *rising* loss beside an improving held-out column is logits growing in
scale rather than in information. It was stopped in epoch 4, **no bar was
read and no card was written**, and 0.4406 is not this arm's number. The
fix, before any bar was read on either seed: a LayerNorm per 1,024-dim chunk
on the query term's inputs **only** -- the pair term keeps the raw states,
because `out(gelu(z))` is bounded by a trained `out` and already reads 2.2 --
and the two query projections zero-initialised, so at initialisation the term
is exactly 0 and the arm *is* the base arm. Its score scale went 28.1 to 23.2,
the base arm's own. **This is a deviation from the pre-registration and is
recorded as one**; what was pre-registered is the query term, what was wrong
was its parametrisation, and it was found by reading the loss rather than the
bar. A 300-step loss guard and a per-epoch logit-std column now make the same
failure loud instead of quiet.

### The arms

    bar                      base s1  base s2   ptr s1   ptr s2   blt s1   blt s2   reference
    (a) exact-pair >= 0.50    0.4301   0.4347   0.5008   0.4981   0.5410   0.5425
        best epoch                  1        1        5        3        5        5
    (b) frozen tight >= 125        95      100      132      120      138      130   ceiling 193, greedy 94
        phrase tight >= 45         27       23       40       34       36       39   ceiling 85, greedy 24
    (c) extract.paired /128        91       67       70       83       89       85   base 117, ftnames2 126
        took_first                 21       20       16       29       27       22
        sibling spoken             30       53       17       31       29       26   ft4g speaks 12
    (d) Pop A right, of 721       205      188      252      252      273      263   ungated null 279
        wrong                     351      374      280      292      285      308   null 220
        acc | att               0.369    0.335    0.474    0.463    0.489    0.461   null 0.559
        attempt rate            0.771    0.779    0.738    0.755    0.774    0.792
    acc|att  name               0.493    0.537    0.684    0.647    0.706    0.691   R1 .529-.559
             number             0.567    0.533    0.750    0.633    0.733    0.700   R1 .250-.417
             other              0.226    0.194    0.366    0.301    0.366    0.355   R1 .086-.161

    the curves, loss / held-out exact-pair
    base s1   2.236/.4256  1.708/.4301  1.427/.4250  1.208/.4074  1.030/.4217  0.897/.4260
    base s2   2.226/.4189  1.750/.4347  1.489/.4329  1.275/.4094  1.106/.4254  0.971/.4126
    ptr  s1   2.151/.4826  1.186/.4963  0.878/.4959  0.680/.4990  0.548/.4973  0.461/.5008
    ptr  s2   2.107/.4861  1.215/.4851  0.878/.4902  0.691/.4981  0.551/.4822  0.465/.4743
    blt  s1   1.906/.4863  1.047/.5172  0.615/.5133  0.338/.5287  0.179/.5369  0.101/.5410
    blt  s2   1.892/.4973  1.057/.5050  0.612/.5040  0.343/.5261  0.180/.5368  0.103/.5425

**Bar (a) passes on both seeds of the built arm and is unresolvable on the
pointer arm.** 0.5410 and 0.5425 is a 0.0015 spread four points clear of the
line, rising monotonically from epoch 1 on both seeds. 0.5008 and 0.4981
straddle the line by two parts in a thousand, and the two seeds do not even
agree where the peak is -- epoch 5 and epoch 3. **The pointer arm's pass is
not a pass** and is reported as a bar the experiment cannot resolve.

**The pre-registered branch that fires is the first one: the frozen states
carry the answer's location and the previous head could not ask for it, so
R2 is off the table for now.** The evidence is not the primary bar alone.
Frozen tight goes **95/100 to 130/138** against greedy's 94, an alignment
ceiling of 193, and every R1 arm at 84-95 -- the largest single move on this
workstream's record, bought by a query projection on the say marker with the
trunk frozen throughout. `other`, the bucket every vehicle has failed and the
one a boundary head was built for, goes **0.194-0.226 to 0.355-0.366** from
R1's 0.086-0.161, and names and numbers move with it, so this is not
`probe_spanhead`'s names-only shape. Population A's answerable-right goes
**188-205 to 263-273** on the population the runtime reads in.

**Four things replicate against it and none of them is small.**

**Phrase tight fails on all four arms** -- 34, 36, 39, 40 against 45 -- and
the built arm is *worse* there than the pointer arm while being better on the
frozen file. Bar (b) fails as a whole under the eighty-second finding's rule,
which exists for exactly this: a frozen-file gain that does not replicate on
the held-out file is reported as a fail. The phrase numbers are still the
largest on the record (greedy 24, R1 13-20) and they are not the bar.

**Population A is still short of the ungated generative null**: 273 and 263
against **279**, with `acc | att` 0.489 and 0.461 against **0.559**. A head
that never declines does not beat greedy decoding on whole passages. Its
joint is **not** quoted against the null's 464 -- these arms have no null
class and abstain only when `reduce` refuses, while the null's joint is a
gated arm's, and the two are different quantities.

**`extract.paired` never recovers the base checkpoint's 117**: 70 to 89
across the four query arms against the base arm's own 67 to 91, with
`took_first` at 16 to 29 against a bar of 3 and siblings spoken at 17 to 31
against a bar of 4. The clause-flip regime is untouched by any of this. The
seed spread on that file is ±24 on the base arm alone, which is larger than
every difference between arms on it, so nothing here is a direction.

**The built arm ends at training loss 0.101** with its held-out column still
climbing. Six epochs is the edge of what this configuration can be run for,
and the held-out column is the only thing saying the fit has not yet cost
anything.

### What this changes

**R2 is not justified by this evidence and should not run.** The case for it
was that the frozen mid-stack representation might not carry the boundary;
two seeds of a properly parametrised head read 130 and 138 on a file where
the same states under the old head read 95, so the representation carries it
and the head was the binding constraint. What the plan's R1 asked of the
frozen trunk is not met -- no bar passes end to end -- but the reason is no
longer the one R2 was built to fix.

**The null class is now the only untested suspect of the three**, and it is
the one the eighty-third finding's own mechanism section named. Every arm
here is positives-only by construction: `abstain` is 0 on both evals, and the
question of whether a head that can locate a span can also decline to speak
is exactly what these arms cannot answer. That is the next experiment, and
it is a binary head on the say marker rather than a class in the shared
softmax -- because what R1 demonstrated is that a null inside the softmax
collapses.

## The null as its own head: abstention arrives, and the frozen eval stops being able to measure it

**Run the same day, `scripts/train_null_head.py`, pre-registered in that file
before it ran.** The span head is the built arm loaded from disk and never
trained; the new thing is a binary classifier on `h_last` alone -- the say
marker's row, which the pair score never reads. Two seeds, each paired with
its own span head, so the two are independent systems.

**Its data is 100,000 null windows harvested beside the 100,084 positives, and
the sampling is not incidental.** 303,150 nulls is ~116 GB against F:'s 118 GB
free, so the class has to be capped, and a prefix would have been the wrong
instrument: `gen_spans.py` writes in NQ's article order and the head is split
by article, so the first 100,000 nulls would have been a different article
population from the positives and the two would have landed on opposite sides
of the split for most of the corpus. `--sample-seed` draws uniformly over the
whole file instead. That leaves the file at ~50% positive against the world's
24.8%, and `pos_weight = 0.3298` restores the prior in the objective rather
than in the directory.

**Only `h_last` is read, one row a window, so both caches are 1.23 GB held in
RAM and an epoch is 2 s** -- against the span head's 111.

    bar                                  null s1   null s2   reference
    selection: balanced accuracy          0.7570    0.7381   held-out, by article
                held-out AUC              0.8352    0.8204   corn/gate.py reads 0.7863
    (a) frozen joint(tight) >= 270           255       253   gated 236, base 214
        frozen tight >= 125/200              102        76   ungated 138 / 130
        frozen abstain >= 150/200            153       177   PASS, PASS
    (b) phrase tight >= 45/89                 26        16   ungated 36 / 39
        phrase abstain >= 40/53               41        48   PASS, PASS
    (c) other acc|att >= 0.50              0.458     0.435   from 0.278
    (d) extract.paired >= 122/128             89        76   base 117
        took_first <= 3                       27        22
        sibling spoken < 4                    29        26   ft4g speaks 12
    (f) frozen AUC | attempted >= 0.75    0.6816    0.6607   over 140 / 104
        the same, all 200 attempted       0.6456    0.6470
        phrase AUC | attempted            0.7038    0.5455   over 56 / 27
        the same, all 89 attempted        0.6777    0.6097

**Both abstain bars pass on both seeds, and they are the first abstain bars
anything in this workstream has passed.** 153 and 177 of 200 on the frozen
file, 41 and 48 of 53 on the phrase file, from a head reading a single frozen
state. The willingness signal is real and it is better than the shipped gate's
on the same question: held-out AUC **0.8352 and 0.8204** against
`corn/gate.py`'s **0.7863**.

**And the location does not survive the gate.** Ungated, those same span heads
read `tight` 138 and 130; gated by their null heads they read **102 and 76**.
The head refuses the unanswerable half correctly and refuses, with it, between
a quarter and a half of the windows where the span was right. `joint(tight)`
255 and 253 clears the gated policy's 236 and the base's 214 and misses 270.
No bar except abstention passes on either seed.

**The frozen eval cannot pin its own threshold down, and that is a finding
about the ruler.** Its cross-validated folds disagree by 0.85 and 0.84 --
`+0.162 / -0.690` on seed 1 and `+0.503 / -0.336` on seed 2 -- and the two
seeds' ladders, read at those means, are not the same experiment: `tight` 102
against 76 and `abstain` 153 against 177 for a `joint` of 255 against 253.
Same joint, reached from opposite ends. On 200 items with a threshold this
unstable, the frozen file is measuring where the fold fell.

**Population A, which is 1,003 passages, replicates to within five.**

    at each arm's own cross-validated threshold
    arm              right  wrong  silent   silent  wrong   joint
                       answerable 721       unanswerable 282
    null head s1       336    162     223      214     68     550
    null head s2       329    158     234      216     66     545
    the off+off null   279    220     222      185     97     464

    precision 59.4% / 59.5% against 46.8%;  acc | att 0.675 / 0.676 against 0.559

**Net +86 (88/174, p = 0.0000) and +81 (92/173, p = 0.0000).** This is the
first arm on the project's record that beats the ungated generative null on
Population A, it does so on both halves at once -- 57 more answerable right
*and* 29 more unanswerable silent -- and its joint **is** comparable to the
null's 464, where the positives-only arms' was not, because both arms can
decline. Three of R1's four arms were significantly *worse* than this null;
these two are significantly better by the same test.

**It is still short of what the plan wants**: 46.6% and 45.6% answerable right
against §0's 85% and R1's own 55-70% expectation, 75.9% and 76.6%
unanswerable silent against 85%, precision 59.4% and 59.5% against 85%.

**And (f) is now an honest number rather than a subset one.** 0.6816 over
**140** attempted and 0.6607 over 104, against the eighty-third finding's
0.7727 over 19 -- and for the first time the all-items numbers sit beside them
rather than far below (0.6456 and 0.6470). The bar fails on both seeds. What
the earlier 0.7727 measured was a head confident about a sliver; this measures
a head that attempts most of the file, and the honest value of that signal is
about 0.65.

**What it changes.** The three suspects are now all measured. Underfit was
retired by scale; the representation was cleared by the query term; and the
null class, given its own head instead of a slot in the softmax, produces
abstention that the frozen ladder credits and a Population A result that beats
the generative baseline for the first time. **What has not been produced is a
reader that passes R1**: `tight` gated is 76-102 against a bar of 125, the
phrase file fails at 16-26 against 45, `extract.paired` never recovers the base
checkpoint's 117, and the clause-flip regime is untouched. The gap between the
ungated span head and the gated one -- 138 to 102 -- is where the next
experiment is, and it is a calibration question rather than a representation
one.

## The two paired numbers the null head's result was missing

**The section above pairs the null head against the *ungated* generative null
and stops there, and that is the wrong comparison for a shipping decision.**
`off+off` is the honest floor; it is not what the runtime does. The runtime
ships `corn/gate.py` in front of the decoder, and no arm in this workstream had
ever been paired against the policy it would replace. `scripts/probe_reader_passages.py`
gains reads (e) and (f) for that; they are replay over harvests already on
disk, no GPU and no decode.

**(e) The null head beats the gated runtime on Population A, on both seeds and
against both readings of "the gated runtime".**

    arm                                     joint   net vs null head s1      net vs s2
    gate, recorded `on` at t = -0.082         486   +64 (97/161, p = 8.1e-05)  +59 (96/155, p = 0.00024)
    gate, cross-validated by this protocol    509   +41 (97/138, p = 0.0089)   +36 (105/141, p = 0.025)
    null head s1 / s2                     550 / 545

**Both gate joints are reported because they answer different questions and
the record has been burned by picking one.** 486 is the arm
`multiwindow_ft4g.json` recorded and the number the shipped constant produced
on the day it was recorded -- it is *what the runtime did*. 509 is the same
gate harvest put through this file's own two-fold CV, the identical protocol
the null head's threshold is chosen by -- it is *what the gate is worth when
it is allowed the same threshold-fitting the reader gets*. The second is the
harder and the fairer bar, so **509 is the one the claim is made against**:
+41 and +36, significant on both seeds, on a population of 1,003. The 486
column is kept beside it so that nobody has to wonder whether the win came
from giving the reader a CV'd threshold and the gate a frozen one.

**The win against the CV'd gate is a different shape from the win against the
null**, and this is the column the independent read asked for. Against
`off+off` the null head gains on both halves at once. Against the CV'd gate it
gains almost entirely on the answerable half: 336 and 329 right against the
gate's 282, +54 and +47, while correct silence goes 227 to 214 and 216 --
*down* 13 and 11. The gate buys its 509 with silence and the head buys its 550
with reading, which is exactly the axis §2.1 says this plan has to move and
the axis five generative vehicles could not.

**(f) The three-row threshold table, and R-T's rule was not applied.**

    seed 1, all 1,003 passages       answerable 721        unanswerable 282
    row                    t         right  wrong  silent   silent  wrong   joint   acc|att
    fold 0            -0.1534         338    152     231      227     55     565    0.690
    fold 1            -0.4808         348    167     206      204     78     552    0.676
    CV, held out      both            336    162     223      214     68     550    0.675

    seed 2
    fold 0            -0.3255         334    149     238      237     45     571    0.692
    fold 1            -0.9282         353    162     206      196     86     549    0.685
    CV, held out      both            329    158     234      216     66     545    0.676

**The CV row is below both of its own fold rows on both seeds, and that is the
protocol working rather than a defect.** A fold row scores all 1,003 passages
at a threshold fitted on 502 of them; the CV row scores each half at the
*other* half's threshold and is the only unbiased number of the three. The gap
-- 565/552 down to 550, 571/549 down to 545 -- is the size of the optimism a
single-threshold quote would have carried, 2 to 5 joint, and it is small
because Population A is large. On the frozen eval, where the same protocol's
folds disagree by 0.85, it is not small; that contrast is the section below.

**The two fold thresholds disagree by 0.33 on seed 1 and 0.60 on seed 2, and
the answers they give differ by more than the seeds do.** Seed 2's fold 1 at
`t = -0.9282` reads 353 answerable right -- the highest `right` anywhere in
this workstream -- and pays 41 correct silences for it (237 to 196). The two
fold rows of one seed straddle the other seed's rows. **The threshold, not the
seed, is the largest free variable left in this arm**, which is a reason to
state a threshold rule and follow it rather than to report a peak.

**And the rule the plan states has never been applied here.**
`PLAN-EXTRACTION-READER.md` R-T says `t` is biased toward speaking by taking
the *lowest `t` within one standard error of the CV optimum on the joint*.
`probe_reader_passages.cross_validate` takes the optimum itself -- the lowest
`t` among ties at the maximum, which is not the same thing and is not biased
toward anything. Every Population A number on the record, the gate's 509
included, is an optimum. Read (f) now prints what R-T's rule would have chosen
instead of quietly switching to it, because switching would make two readings
of one instrument incomparable:

    training fold        optimum        one SE   the lowest t within it
    s1 fold 0     280 at -0.1534         11.13   -0.2290  (joint 269)
    s1 fold 1     287 at -0.4808         11.07   -0.8722  (joint 276)
    s2 fold 0     284 at -0.3255         11.11   -0.4074  (joint 273)
    s2 fold 1     291 at -0.9282         11.04   -1.0802  (joint 280)

    held out, under R-T's rule    right  wrong  silent   silent  wrong   joint
    null head s1                   331    176     214      200     82     531
    null head s2                   341    170     210      207     75     548
    the gate, same rule            275    199     247      193     89     468

**R-T's rule costs joint and buys `right`, which is what it was written to
do.** Seed 1 goes 550 to 531 and seed 2 545 to 548; the gate goes 509 to 468.
The binomial SE on a 502-passage fold is ~11 joint, so "within one SE" is a
wide licence on this population and the thresholds it picks are 0.08 to 0.39
lower. **The arm's ordering against the gate is unchanged under either rule**
-- 531 and 548 against 468 -- so nothing above depends on which is used, and
the choice is the owner's to make once rather than a number to pick per table.
Every figure in this finding is at the optimum unless the row says otherwise.

## Who owns the residue: the null head refuses more than it misreads

**336 right of 721 leaves 385 answerable passages, and the levers left are
expensive enough that choosing one from a pooled number would repeat the
mistake the whole thread is a record of.** `scripts/probe_reader_residue.py`
partitions the residue into the three things that can own it, exclusively and
in order, at each passage's own held-out fold threshold:

  * **NULL** -- no gold-bearing window was admitted. Nothing downstream ever
    had a chance.
  * **LOCATION** -- a gold-bearing window was admitted and on every such
    window the head's best pair does not score `tight` against the gold.
  * **REDUCE** -- a gold-bearing window was admitted, the head pointed right
    on it, and the passage is still wrong or silent.

Gold-bearing is `corn.extract.span_of` on the window text; "pointed right" is
`score_extract_tight` on `It's {span}.` for that one window -- the same scorer
the passage verdict uses, applied one window at a time, so the difference
between a right window and a right passage is exactly `reduce`.

    the answerable residue                     seed 1              seed 2
    right at the CV'd t                       336                 329
    residue                                   385                 392
      NULL                                    183   47.5%         178   45.4%
      LOCATION                                136   35.3%         143   36.5%
      REDUCE                                   66   17.1%          71   18.1%

    by answer type, right / NULL / LOCATION / REDUCE
    type      n      seed 1                        seed 2
    name    401      199 /  92 /  76 /  34         202 /  89 /  80 /  30
    number  195      106 /  40 /  29 /  20          99 /  37 /  28 /  31
    other   125       31 /  51 /  31 /  12          28 /  52 /  35 /  10

    LOCATION by type -- R2's actual target
    name                                       76   55.9%          80   55.9%
    number                                     29   21.3%          28   19.6%
    other                                      31   22.8%          35   24.5%

**NULL holds the plurality on both seeds and the pre-registered reading names
the margin-feature null head as the arm that runs first.** The plurality is
not large -- 47.5% and 45.4% against LOCATION's 35.3% and 36.5% -- and it is
the ordering rather than the size that replicates: the two seeds agree on the
ranking, on the shares to within 2.1 points, and on every type cell except
`number`'s REDUCE (20 against 31, inside the ±35-passage floor this population
was given).

**Every one of the 721 answerable passages has at least one gold-bearing
window.** So NULL is never the 64/32 cut failing to hand the reader the
answer; it is always a threshold refusing a window that carried it. The
retrieval workstream (§4) is not what is costing these 183.

**The three owners have three different verdict shapes, and that is what says
they are three different problems.**

    owner       silent   wrong        seed 1 / seed 2
    NULL       146/146   37/32        four fifths refusal, one fifth the wrong window spoken
    LOCATION    27/33   109/110       four fifths a wrong answer from the right window
    REDUCE      50/55    16/16        four fifths windows disagreeing into silence

NULL is mostly the head declining. LOCATION is mostly the head admitting a
gold-bearing window and naming something else in it -- the sixty-sixth
finding's regime, and the gap the ungated frozen `tight` of 138 and 130 says
the representation is already better than the gated path shows. REDUCE is
mostly `reduce` returning `None` because its windows disagreed, not a right
answer being outvoted.

**Names are more than half of LOCATION on both seeds** -- 76 of 136 and 80 of
143, 55.9% both times -- against names being 55.6% of the answerable half, so
LOCATION is *not* names-heavy relative to the population; it is exactly
population-shaped. The pooled type table (name 50%, number 52%, other 24%
right) had suggested names were the target; split by owner they are not
disproportionately unlocated, they are disproportionately *numerous*. **`other`
is the type whose residue is most NULL** -- 54.3% and 53.6% against name's
45.5% and 44.7% -- which says the `other` bucket's long-standing weakness
survives as a refusal problem more than as a pointing one.

**One passage of each, seed 1, the first in file order.** These are the whole
partition in three rows, and they are printed because a table of counts cannot
show that the three owners are three different failures.

    NULL      "what percentage of the earth's surface is water", gold "roughly 78%"
              w0 gold  margin -1.076  span "2.5%"
              w1 gold  margin -0.514  span "2.5%"
              w2        margin -1.235  span "1.5 to 11"
              t = -0.481: nothing admitted, the passage is silent. Two windows
              carried the answer and the head declined both.

    LOCATION  "who laid the foundation of school of possibilism", gold "Marshall Sahlins"
              w0 gold  margin +0.099  span "Marshall"
              w1 gold  margin -0.170  span "Marshall"
              w2        margin +0.050  span "Strabo"
              w3        margin +0.118  span "Strabo"
              t = -0.153: the gold-bearing w0 is admitted and the head takes
              "Marshall" -- the surname without the given name, which the
              seventy-second finding already named as a species -- so the pair
              is not tight, and two windows agree on "Strabo" and outvote it.

    REDUCE    "who wrote the song after you've gone", gold "Turner Layton"
              w0 gold  margin +2.600  span "Turner Layton"
              w1        margin +0.754  span "Marion Harris"
              w2-w4     margin -2.109 / -2.893 / -2.622
              t = -0.153: the head reads the answer exactly, on the one window
              that carries it, at the largest margin in the passage -- and a
              second admitted window offers a different name, the two disagree,
              and `reduce` returns `None`. The passage is silent.

**The REDUCE example is also the reason 3a is not free.** A score-aware reduce
takes the highest-*scoring* admitted window's span, and in a null-head harvest
the number in the `best` field is the **null head's logit**, not the span
head's `s_best` -- `train_reader_cached.read_cached` substitutes one for the
other by design, so the ladder downstream reads one margin. `w0`'s +2.600 above
is a presence score and not a location score, and ranking on it would be
ranking the wrong quantity. `train_reader_cached.span_features`, written for
the margin arm below, is what makes the span head's own `s_best` available per
window, so 3a is now a harvest away rather than a rewrite.

**The unanswerable half spoken wrong -- 68 and 66 passages -- is NULL by
construction and the table is degenerate there**, because no window can be
gold-bearing when there is no gold. What varies is the admitted-window count,
and it is concentrated: 46 of 68 and 46 of 66 are passages where the null head
admitted exactly one window out of a passage that mostly has three to six.
These are single confident false admissions rather than a head that admits
everything.

## Step 3b: a much better presence detector that reads no more passages

**`NULL` held the plurality on both seeds, so the pre-registered arm was the
margin-feature null head** -- the binary head on `h_last` given three more
numbers, read off the frozen span head at the one place the pair scores exist:
`s_best`, `s_best - s_second`, and the top pair's length. Written into
`scripts/train_null_head.py`'s docstring before it ran, with the bars, the
stopping rule and the void condition. Nothing about the span head, `reduce`,
`corn/extract.py` or `corn/gate.py` moved.

**Two normalisers ran, and the second is a control that was pre-registered as
one.** "The three scalars LayerNormed" read literally is `nn.LayerNorm(3)`:
three numbers with their mean and scale removed carry one degree of freedom,
so the literal reading compresses a score, a margin and a length into a single
direction before the MLP sees any of them. `ln3` is the arm the bars are read
on; `std` -- each scalar standardised by its own training-split mean and
standard deviation, frozen into the head -- answers whether a miss is the
normaliser or the features.

**The void condition passed before anything trained.** `s_best` is harvested
off the training caches by the padded path and computed at inference by
`read_cached`'s per-window path; `--check-features` asserts they agree to 1e-4
of their own scale on real windows and read **3.0e-07** and **1.0e-06** on the
two caches. The harvest is 112 s a cache on a shared card, 200,084 windows,
cached to `F:/corn-jr-data/states/feats_reader_built_s{1,2}.pt`.

    arm         bal.acc     AUC   frozen        phrase      paired   Population A at the CV'd t
                held out          tight abst    tight abst  hits sib  right wrong silent   sil wrong  joint  prec  acc|att
    null s1      0.7570  0.8352     102   153      26   41    89  29    336   162    223   214    68    550  59.4   0.675
    null s2      0.7381  0.8204      76   177      16   48    76  26    329   158    234   216    66    545  59.5   0.676
    ln3  s1      0.8091  0.8892      95   163      21   44    80  23    337   142    242   207    75    544  60.8   0.704
    ln3  s2      0.7918  0.8729      72   173      16   48    65  14    322   174    225   204    78    526  56.1   0.649
    std  s1      0.8698  0.9383      97   162      26   44    46   4    353   137    231   206    76    559  62.4   0.720
    std  s2      0.8494  0.9240      81   169      21   42    24   4    340   167    214   177   105    517  55.6   0.671

    fold thresholds   ln3 s1  -0.6214 / -0.3757    ln3 s2  -0.5899 / -1.1757
                      std s1  -1.1592 / -0.5980    std s2  -2.0906 / -1.0495

**The selection bars pass on all four arms and PRIMARY fails on all four.**
Held-out balanced accuracy goes 0.7570 and 0.7381 to **0.8091 / 0.7918**
(`ln3`) and **0.8698 / 0.8494** (`std`), against a bar of 0.78; held-out AUC
goes 0.8352 and 0.8204 to **0.8892 / 0.8729** and **0.9383 / 0.9240**, against
0.86. The pre-registered stopping rule -- both seeds under 0.77 -- does not
fire, and it does not come close: the span head's confidence carries a great
deal of presence information the say marker's state does not.

**And answerable `right` on Population A goes 336 and 329 to 337, 322, 353 and
340.** The bar was **371** -- 336 plus this population's own 35-passage floor
-- and the best arm on the best seed reads **353**. `std` seed 1's +17 is the
largest move any arm made and it is half the floor; `ln3` seed 2's -7 is a
loss. **PRIMARY is missed on both seeds of the pre-registered arm and on both
seeds of its control**, so the failing branch written before the run fires:
*the owner Step 2 named is not fixable by this lever, and 3a runs in a later
session rather than now.* It has not been run here.

**The finding is the decoupling, and it is sharp.** A +0.11 gain in held-out
balanced accuracy and a +0.10 gain in held-out AUC -- on exactly the question
"does this window carry an answer" -- buys between **-7 and +17** answerable
passages on the population the runtime reads in. The two numbers are measured
on the same head, the same states and the same day, and they are not the same
axis. Any future arm selected on held-out presence accuracy should be read
against this: **this workstream now has a case where that metric moved a tenth
and the target moved nothing.**

**The residue partition says where the gain went, and it went to silence.**
Re-running `probe_reader_residue.py` on each new harvest:

    owner shares of the answerable residue
    arm          residue    NULL          LOCATION      REDUCE
    null s1          385    183  47.5%    136  35.3%     66  17.1%
    null s2          392    178  45.4%    143  36.5%     71  18.1%
    ln3  s1          384    225  58.6%    107  27.9%     52  13.5%
    ln3  s2          399    220  55.1%    121  30.3%     58  14.5%
    std  s1          368    210  57.1%     98  26.6%     60  16.3%
    std  s2          381    155  40.7%    120  31.5%    106  27.8%

**On three of the four arms `NULL`'s share went *up* while `LOCATION` and
`REDUCE` both went down.** The better presence detector does not convert
mislocations into right answers; it converts them into refusals. `LOCATION`
falls 136 to 107 and 98, `REDUCE` falls 66 to 52 and 60, and `NULL` rises 183
to 225 and 210 -- the passages the old head admitted and got wrong are now
passages the new head declines. That is a real improvement in precision
(59.4% to 62.4%) and in `acc | att` (0.675 to 0.720), and it is the shape
`INDEPENDENT-READ.md` §5.1 exists to make visible: **a willingness change, and
this time a well-calibrated one, but a willingness change.**

**`std` beats `ln3` on selection on both seeds, so the normaliser mattered and
the control earned its place.** 0.8698/0.8494 against 0.8091/0.7918 is outside
the seed spread of either arm; the one-degree-of-freedom arithmetic in the
pre-registration was directionally right about what `nn.LayerNorm(3)` does to
three heterogeneous scalars. What the control settles is the other clause it
was written for: **both normalisers miss PRIMARY, so the miss is not the
normaliser.**

**The seed spread on this arm is larger than the arm's own effect and has to
be quoted with it.** `ln3` reads 337 against 322 and `std` 353 against 340 --
15 and 13 passages of answerable `right` from a head seed. `std` seed 2 is
worse than that: its unanswerable `silent` falls to **177**, below the 200 the
bar named and 29 below its own seed 1, and its fold thresholds are -2.09 and
-1.05, the widest disagreement on this population anywhere in this file. Read
against the CV'd gate, `std` seed 1 is +50 (p = 0.0027) and `std` seed 2 is
+8 (p = 0.68) -- the same arm, two seeds, significant and indistinguishable.

**Frozen and phrase moved as the eighty-third finding said they would, which
is to say not readably.** `joint(tight)` 255/253 becomes 258/245/259/250,
`tight` 102/76 becomes 95/72/97/81, phrase `tight` 26/16 becomes 21/16/26/21.
No bar was set on these and none should be: on 200 items with folds that
disagree by 0.85, these differences are where the fold fell.

**One number outside all of it is worth recording because nothing was aiming
at it.** `sibling_spoken` on `evals/paired.jsonl` -- the clause-flip regime,
where `ft4g` speaks 12 and the null heads speak 29 and 26 -- reads **4 and 4**
on both `std` arms. It is bought with abstention (`extract.paired` hits fall
to 46 and 24 with 16 and 40 abstentions), so it is not a repair of the
sixty-sixth finding's failure; it is the same trade the rest of this section
describes, showing up on the file built to catch that failure. Recorded, not
claimed.

## Limits

One trunk, two head seeds per arm, fp32. `spans_nq.jsonl`'s own ceiling bounds
the evals: 7 of the frozen eval's 200 answerable items and 4 of the phrase
file's 89 have golds that do not align to a `bpe8k` boundary in their own
window, so the reachable maxima are 193/200 and 85/89. The frozen eval's
threshold is cross-validated on itself and the phrase file reads it cold;
Population A's is cross-validated on Population A. The `off+off` null on
Population A is `multiwindow_ft4g.json`'s recorded verdicts from a different
decode pass, licensed by `probe_reader_passages.py`'s read (a) reproducing
the recorded gated arm 1003/1003.

**On the three sections added 2026-09-02.** The gate arm read (e) pairs against
comes from two files and neither is `crossfit_ft4g.json` itself, which carries
aggregates only: the item-level `on` and `off+off` verdicts are
`multiwindow_ft4g.json`'s, and the CV'd gate is reconstructed from
`crossfit_harvest_ft4g.json` by the protocol whose guard (c) reproduces
`crossfit_ft4g.json` read (e) exactly -- joint 509, folds -0.1359 / -0.1371,
net +45 at p = 0.0003. Every threshold in this file is an optimum and not
R-T's lowest-within-one-SE; read (f) prints both and the ordering against the
gate does not depend on which is used.

The residue partition is a **partition of the arm's own errors and not a
causal claim**. `LOCATION` says the head pointed wrong on an admitted
gold-bearing window; it does not say a better trunk would point right. `NULL`
says no gold-bearing window was admitted; it does not say the window was
readable. The owners are exclusive and ordered by construction, so a passage
whose gold window was admitted *and* whose other windows outvoted it is
`REDUCE` and not `LOCATION`, whatever else was also wrong with it. `span_of`
is the gold-bearing predicate, so a gold that appears in a window only in
inflected or partial form is not counted as borne there and its passage lands
in `NULL`.

Step 3b is four arms on one trunk with two span-head seeds and two
normalisers, fp32, on a card shared with another training run for its whole
duration -- which affects wall-clock and nothing else. `nullfeat_std_s2` is
the one arm whose unanswerable `silent` falls below the bar (177), and its
fold thresholds disagree by 1.04; it is quoted throughout rather than dropped,
because dropping the seed that disagrees is the failure this file's seed-spread
section exists to name.
