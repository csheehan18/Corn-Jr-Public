# 85. The verifier label has to be cross-fitted, and cross-fitted with the span head's confidence it passes the verifier bar; the extent rule buys eight for nothing and the reduce family is closed

**`docs/PLAN-READER-RESIDUE.md`'s four arms, run or retired 2026-09-02, plus
the reads that file's species table made possible once the span head's own
score was put beside the null head's logit. Replay wherever a number is a
verdict; one no-grad pass over the popa cache (20 s a seed) for the pair
scores; minutes of GPU for the verifier head. `corn/extract.py`,
`corn/gate.py`, every scorer and every frozen row are untouched.**

The plan said A2 first because it was free, A1 next because it was minutes,
A3a third, A4 on the owner's decision, and put the arithmetic of every bar
being met at 500 and 496 of 721. This file is what the arms actually read, and
three of the four come out differently from their pre-registration — one for
a reason the plan could not have seen without the number this file had to
harvest first.

## The instrument that made the rest readable: `s_best` was already on disk

A2 asked for *one no-grad pass over the Population A cache to write `s_best`
into the harvest beside the null logit*. That pass had already been made:
`reader_built_s{1,2}_popa.json` is the same span head read positives-only,
and its `best` column is the argmax pair's own score for the **identical
spans** — 1,003 of 1,003 rows string-equal to `null_s{1,2}_popa.json`'s on
both seeds. Joining the two files is a replay and it is what every read below
is built on. `scripts/harvest_popa_pairs.py` then wrote the rest of what a
read-time rule could want — the argmax's neighbourhood of pairs, the top ten,
the window's `logsumexp` — and asserted every span it decoded against the
built harvest before writing.

**Both scores, on every answerable window of Population A, seed 1 / seed 2:**

    window class                       n      s_best median      null logit median
    gold-bearing, argmax tight        803 / 779    15.70 / 14.74      +0.17 /  0.00
    gold-bearing, argmax wrong        408 / 432    12.27 / 11.37      -0.24 / -0.59
    no gold (absent_window)         1,583 / 1,583   8.19 /  7.65      -1.73 / -1.98

    AUC                               null logit        s_best        z(null) + z(s_best)
    presence, gold vs not            0.828 / 0.829   0.787 / 0.778     0.842 / 0.839
    verifier, argmax tight vs not    0.800 / 0.814   0.809 / 0.797     0.840 / 0.841
    verifier within gold windows     0.616 / 0.651   0.707 / 0.687

**The span head's confidence is a better verifier than the null head's logit
and a worse presence detector, and the two are complementary.** Inside
gold-bearing windows — the question "given the answer is here, did he point
at it" — `s_best` reads 0.707 and 0.687 against the null logit's 0.616 and
0.651. That is the axis `REFUSED_RIGHT` lives on, and it is the one the null
head reads worst.

**`REFUSED_RIGHT`'s windows are not empty-looking windows.** The top refused
gold window of a `REFUSED_RIGHT` passage carries `s_best` median **14.03 /
13.34**, against 8.19 / 7.65 for a window with no answer and 17.13 / 16.08
for a window he was admitted on and read right. At `s_best >= 12`, 70% and
65% of `REFUSED_RIGHT`'s windows clear it against 27% and 24% of the empty
ones. The null head is refusing windows the span head is fairly sure about,
and it has no way to know that, because it never sees the number.

## The margin-feature arms were read under the wrong reduce, and under the right one they clear the bar on `right` and fail it on silence

The eighty-fourth finding read Step 3b's four arms under `agree` — 337, 322,
353, 340 against a bar of 371 — and called them *a much better presence
detector that reads no more passages*. `hybrid` shipped the same day, after
those reads. Under `hybrid`, the reduce every later number is read on:

    arm         folds                right  a-wrong  a-silent   u-silent  u-wrong   joint   acc|att  attempt   REFUSED_RIGHT
    null s1     -0.158 / -0.403       371     188      162        207       75      578    0.664    77.5%       103
    null s2     -0.290 / -0.894       371     186      164        207       75      578    0.666    77.3%        98
    std  s1     -1.102 / -1.313       395     176      150        189       93      584    0.692    79.2%        75
    std  s2     -2.091 / -1.319       390     219      112        161      121      551    0.640    84.5%        54
    ln3  s1     -0.766 / -0.586       376     195      150        191       91      567    0.658    79.2%        97
    ln3  s2     -0.670 / -1.176       348     206      167        188       94      536    0.628    76.8%       108

**`std` reads 395 and 390 answerable right on the two seeds — 24 and 19 over
the null head, clear of 371 on both — and `REFUSED_RIGHT` falls from 103 and
98 to 75 and 54.** The species the plan named as the largest and *"not a
threshold that needs nudging"* moves by a quarter and a half when the head is
handed the span head's three scalars. The eighty-fourth finding's sentence
that this arm *reads no more passages* was true under `agree` and is false
under the reduce that shipped, and it is corrected here rather than left.

**And it fails the other half of the bar, on both seeds, by spending silence
it does not have.** Unanswerable `silent` reads 189 and 161 against 200. The
gain is bought at a threshold that admits 79% and 84% of the answerable half,
and on seed 2 the attempt rate is the highest on the record with the lowest
precision (53.4%). PRIMARY was *`right >= 371` with `silent >= 200`*, and no
seed of any 3b arm meets both under either reduce.

## The threshold protocol decides which of those two sentences is the finding

The cross-validated `t` maximises `right + unanswerable silent` on the
training fold. The bar is *`right` subject to `silent >= 200`*. Those are
different objectives, and on a head that is better at ranking they choose
different points. Three protocols, the same six harvests, held out:

    harvest      rule      folds                right  a-wr  a-sil  u-sil  u-wr  joint  acc|att  attempt
    null s1      joint     -0.158 / -0.403       371   188   162    207    75    578   0.664   77.5%
                 one-SE    -0.751 / -0.872       394   232    95    162   120    556   0.629   86.8%
                 bar       -0.186 / -0.505       371   192   158    201    81    572   0.659   78.1%
    null s2      joint     -0.290 / -0.894       371   186   164    207    75    578   0.666   77.3%
                 one-SE    -1.102 / -1.171       409   229    83    153   129    562   0.641   88.5%
                 bar       -0.444 / -0.801       375   191   155    198    84    573   0.663   78.5%
    std s1       joint     -1.102 / -1.313       395   176   150    189    93    584   0.692   79.2%
                 one-SE    -1.899 / -1.848       402   206   113    164   118    566   0.661   84.3%
                 bar       -0.715 / -1.237       383   159   179    198    84    581   0.707   75.2%
    std s2       joint     -2.091 / -1.319       390   219   112    161   121    551   0.640   84.5%
                 one-SE    -2.522 / -2.554       407   254    60    133   149    540   0.616   91.7%
                 bar       -0.550 / -0.931       342   168   211    201    81    543   0.671   70.7%

`joint` is what every Population A number on the record uses. `one-SE` is
R-T's rule as `PLAN-EXTRACTION-READER.md` states it, never applied until read
(f) printed it: the lowest `t` within one standard error of the optimum. `bar`
is the bar's own shape — the `t` that maximises `right` on the training fold
among those holding that fold's share of 200 correct silences.

**R-T's rule as written cannot be the protocol.** One SE on a 502-passage
fold is ~11 joint, and the lowest `t` inside that licence spends 40 to 70
correct silences for 20 to 40 right answers on every harvest. It buys exactly
what the plan's §2.1 says a willingness re-tune buys, and the silence floor
that PRIMARY names is violated on all six rows.

**Under the bar's own protocol, `std` seed 1 reads 383 right at 198 silent
with `acc | att` 0.707 — the best conditional accuracy at that attempt rate
on the record — and `std` seed 2 reads 342.** So the honest statement about
3b is: the span head's scalars make a better null head on one seed and a
different one on the other, the seed spread on this arm is 40 passages under
the protocol that matches the bar, and *which protocol* is worth more than
the arm. **The plan has to fix one protocol before any further null-head arm
is read, and `bar` is the one that matches the bar.** Every number below is
at the `joint` optimum, so it stays comparable with the eighty-fourth
finding; the choice is the owner's, once.

## A1 as written cannot be trained, and the reason is the stacking rule

A1's label is *"the span head's argmax pair on this window is one of the
window's gold pairs"*, computed off the state cache. `train_null_head.py
--label verifier` computes it (one padded pass over the positive cache, 112 s
a seed, `harvest_hits`) and the count comes back first, as the plan asked:

    the span head's argmax is a gold pair on   95,504 of 100,084 windows   95.4%   seed 1
                                               95,385 of 100,084 windows   95.3%   seed 2
    on Population A, which it never saw           803 of  1,211 windows   66.3%   seed 1
                                                  779 of  1,211 windows   64.3%   seed 2

**The built arm trains to a loss of 0.101 on exactly these windows and hits
95% of them.** The plan's unreadable condition was *fewer than ~15% positive*;
the condition that actually fires is the opposite one. A label read off the
training set by the head that trained on it is the presence label with 4.6%
of its positives flipped, and the head trained on it reads as the presence
head reads:

    arm             folds               right  a-wr  a-sil   u-sil  u-wr   joint  acc|att   REFUSED_RIGHT   (f) frozen | attempted
    verifier s1     -0.172 / -0.607      357   172   192     206    76     563   0.675       119            0.6429 over 130
    verifier s2     -0.441 / -0.800      364   182   175     206    76     570   0.667       100            0.6564 over 110
    presence s1     -0.158 / -0.403      371   188   162     207    75     578   0.664       103            0.6816 over 140
    presence s2     -0.290 / -0.894      371   186   164     207    75     578   0.666        98            0.6607 over 104

PRIMARY fails on both seeds, the mechanism bar fails on both (`REFUSED_RIGHT`
rises), and (f) fails on both. **None of that is a reading of the verifier
idea.** It is a reading of a label that was 95% the old label, and the arm is
reported as the data fact the plan said an unreadable run should be.

**The repair is the standard one and it costs GPU the plan did not price.** A
second-stage model has to be trained on first-stage predictions made out of
fold. `train_reader_cached.py --n-folds 2 --fold k` trains the built arm on
the articles whose stable hash is `k`; `scripts/crossfit_hits.py` labels every
window with the head that never saw its article and writes the label in
`--hits-cache`'s format. Each fold head sees half the articles the deployed
head sees, so the out-of-fold label is a harder verifier than the deployed
head's true error rate — the cost of an honest label, and recorded on the
card as the out-of-fold hit rate. Two fold heads are two runs of the
eleven-minute recipe a seed. §"A1, cross-fitted" below carries the seed-1 result.

## A1, cross-fitted: the say marker can see when he is wrong and not when he is right

Seed 1, run in this session. Two fold heads of the built arm on disjoint
article halves (held-out exact-pair **0.5048 / 0.5066** against the full
head's 0.5410), each labelling the half it never saw:

    out-of-fold verifier label      51,410 of 100,084 windows hit   51.4%
    in-fold, the plan's label       95,504 of 100,084                95.4%
    Population A, the deployed head    803 of   1,211                66.3%

The verifier head then trains on that label exactly as before (`pos_weight`
0.4229 by the same derivation, held-out balanced accuracy 0.7437, not
comparable to any presence number):

    read                                        cross-fit verifier s1     presence s1 (the record)
    frozen  (f) AUC | attempted                 0.7063 over 135           0.6816 over 140
            (f) all 200 items                   0.7084                    0.6456
    phrase  (f) AUC | attempted                 0.7444 over 33            0.7038 over 56
            (f) all 89 items                    0.7096                    0.6777
    (c) `other` acc | att, both evals pooled    16/27 = 0.593  PASS       0.458
    Population A under hybrid, joint t          354 right, 209 silent     371 right, 207 silent
      folds                                     -1.702 / -2.048           -0.158 / -0.403
      acc | att, attempt rate                   0.678, 72.4%              0.664, 77.5%
      under the bar protocol                    358 right, 205 silent     371 right, 201 silent
    species  REFUSED_RIGHT                       98                       103
             REFUSED_WRONG                      116                        82
             RIVAL                               66                        80
             CLIPPED                             29                        42
             AGGREGATION                         47                        31
             owners NULL / LOCATION / REDUCE    214 / 106 / 47            185 / 134 / 31

**(f) moves for the first time on this record, on both files and on the
all-items floor** -- frozen 0.646 to **0.708** over all 200, phrase 0.678 to
**0.710** over all 89 -- and `other`'s conditional accuracy clears its 0.50 bar
at 0.593. The label change did what the plan said a label change would do to
the verifier question. It is still under 0.75, on both files.

**And PRIMARY fails, by the mechanism the failing branch named second.**
`right` reads 354 against 371, `REFUSED_RIGHT` moves 103 to 98 -- a twentieth,
against the bar's quarter -- while `RIVAL` falls 80 to 66 and `LOCATION` 134 to
106, and every one of those passages lands in `REFUSED_WRONG` (82 to 116).
The verifier head learned to refuse the windows the span head reads *wrong*
and did not learn to admit the ones it reads *right*. That is the verifier's
job on one side only, and it is a precision gain (`acc | att` 0.664 to 0.678
at five points less attempt rate) of exactly the shape the eighty-fourth
finding's 3b arms had. **The say marker's state carries "he is about to be
wrong" and does not carry "he is about to be right", even when the label is
honest.** The next head has to read the argmax pair's own rows -- the thing
`s_best` is a scalar summary of and the thing the 3b `std` arm's 75 / 54 was
already pointing at -- and that is a different head, pre-registered
separately, not a flag on this one.

### The follow-on the failing branch named, run on the same label: (f) passes for the first time

`--features std --label verifier --hits-cache` — the cross-fitted label with
the span head's three scalars, one flag on the arm above, the features
already cached from Step 3b. Seed 1:

    read                                        cross-fit + std s1        cross-fit s1      presence s1
    selection, held-out balanced accuracy       0.7911                    0.7437            0.7570
    frozen  (f) AUC | attempted                 0.7696 over 99   PASS     0.7063            0.6816
            (f) all 200 items                   0.7694                    0.7084            0.6456
    phrase  (f) AUC | attempted                 0.8772 over 25   PASS     0.7444            0.7038
            (f) all 89 items                    0.8113                    0.7096            0.6777
    (c) `other` acc | att                       12/17 = 0.706    PASS     0.593             0.458
    Population A under hybrid, joint t          376 right, 197 silent     354 / 209         371 / 207
      folds                                     -2.493 / -2.988           -1.702 / -2.048   -0.158 / -0.403
      acc | att, attempt rate                   0.699, 74.6%              0.678, 72.4%      0.664, 77.5%
    species  REFUSED_RIGHT                       80                        98               103
             REFUSED_WRONG                      124                       116                82
             RIVAL                               53                        66                80
             CLIPPED                             29                        29                42
             AGGREGATION                         49                        47                31
             owners NULL / LOCATION / REDUCE    204 / 92 / 49             214 / 106 / 47    185 / 134 / 31

**Bar (f) — the plan's verifier bar, failed by every arm since the
eighty-third finding wrote it — passes on both files, and passes on the
all-items floor that the eighty-third finding said had to be printed beside
it: frozen 0.769 over all 200, phrase 0.811 over all 89.** `other`'s
conditional accuracy reads 0.706 against a bar of 0.50 and a record of
0.278 to 0.458. This is the honest label and the span head's confidence
together, and neither alone gets there: the label alone reads 0.708 / 0.710,
the features alone (3b, presence label) read 0.646-ish on the frozen floor
and bought no verifier AUC at all.

**On Population A it reads 376 right at 197 silent — PRIMARY's `right` cleared
by five and its silence floor missed by three — with `acc | att` 0.699 at a
74.6% attempt rate, the best conditional accuracy at that attempt rate on the
record.** `REFUSED_RIGHT` falls 103 to 80, a fifth, against the bar's quarter;
`RIVAL` falls 80 to 53 and `LOCATION` 134 to 92, and `REFUSED_WRONG` rises to
124 as the head refuses what would have been wrong. `AGGREGATION` rises 31 to
49, which is the null-logit fallback ranking a different set of admitted
windows and is the one number here that moves the wrong way.

**What this is and is not.** It is one seed of the arm the failing branch
named, and it is the first head on this record whose margin is a verifier by
the plan's own bar. It is not a PRIMARY pass: the silence floor is missed by
three passages at the `joint` protocol, and under the `bar` protocol the
`right` column is the number that has to be read (§"the threshold protocol").
Under the `bar` protocol it reads 382 right at 193 silent, `acc | att`
0.697. The second seed is two fold heads and two verifier runs and decides
whether 0.77 / 0.81 is a direction.

**One seed, so a reading and not a direction.** The second seed is two more
fold heads and is pre-registered in `PLAN-READER-RESIDUE.md` §6.1 with these
numbers as the thing it has to replicate. **A limit specific to cross-fitting,
stated:** each fold head is weaker than the deployed head (0.505 against
0.541), so the label says which windows a *weaker* reader gets right, and a
window the deployed head reads right that both fold heads miss is a positive
labelled 0. That bias is toward refusing exactly the harder windows
`REFUSED_RIGHT` is made of, and it is a reason to expect a cross-fit verifier
to under-admit; the remedy is more folds (each head sees more), at a cost of
one span-head run per fold.

## A2 is closed in every form, and the null head's logit is the better ranker

`--reduce hybrid` promotes the highest-*null-logit* admitted window on a
disagreement. A2 said that was the wrong quantity and that ranking on the
span head's `s_best` would fix `AGGREGATION`. With `s_best` joined from the
built harvest, every variant, `t` cross-validated per variant, paired against
`hybrid` on the same passages:

    variant                                       seed 1                       seed 2
    hybrid  (ships)                       371 right, 207 silent          371 right, 207 silent
    hybrid_span  fallback on s_best        -5  (10/5,  p = 0.30)          -9  (20/11, p = 0.15)
    span         always the top s_best     -4  (15/11, p = 0.56)         -11  (27/16, p = 0.13)
    hybrid_lp    fallback on s_best - lse -15  (19/4,  p = 0.0026)      -16  (26/10, p = 0.011)
    dedupe       one vote per occurrence   +1  (8/9,   p = 1)             +2  (8/10,  p = 0.82)
    dedupe_span  dedupe, fallback s_best   -3  (12/9,  p = 0.66)         -10  (24/14, p = 0.14)

**Ranking on the span head's score is worse than ranking on the null head's
logit on both seeds, and ranking on its within-window log-probability is
significantly worse.** The plan's example — `won` at null-logit 0.02 against
`The jeon` at 0.60 — reads `won` at `s_best` 3.8 against `The jeon` at 7.7
and 8.7: the span head was *less* sure of the right window there, not more.
A pair logit is not comparable across windows and the null logit, which was
trained across windows, is.

**`AGGREGATION` was never one thing, and its largest part is not reachable by
any ranking.** By what `reduce` actually did, seed 1 / seed 2:

    outvoted by agreement       16 / 14    the same span in two overlapping windows outvotes the gold
    right span not grounded      7 /  6    the gold reply itself fails `grounded` -- §"the 22"
    disagreement, top wrong      8 /  9    the fallback fired and promoted the wrong window

The first is overlapping windows counting one passage occurrence twice, and
`dedupe` — one vote per occurrence, the duplicate silenced — is the direct
repair. It moves 155 and 159 passages' admitted masks and the verdicts by +1
and +2, because a duplicated span is as often the gold as a rival. The
second is `grounded` and not `reduce`. The third is 8 and 9 passages, and the
null logit already picks the right one more often than any alternative.
**The reduce family is closed at `hybrid`.** A2's bar — `AGGREGATION` halved
— is unreachable by anything in it.

## A3a buys eight passages on seed 1 for nothing, and the plan's bar was above its ceiling

`CLIPPED` is 42 and 36 passages, and by what the span is to the gold:

    the span is a prefix of the gold, 1-2 words short     20 / 20     'Marshall' for 'Marshall Sahlins'
    the span is a suffix of the gold                     16 / 11     'England' for 'off the Devon coast of England'
    inner, or longer than the gold                        6 /  5

**Half of it is unreachable by any extension of the argmax.** Within three
candidate rows on either side, a pair that scores `tight` exists for **20 of
42 and 18 of 36** `CLIPPED` passages; for the rest the gold is not a
neighbour of what he pointed at. So the pre-registered bar — `CLIPPED` halved
— was set at exactly the ceiling of the rule, and the rule could only meet it
by taking every reachable passage.

The rule, replay over `pairs_built_s{1,2}_popa.json`: among the pairs
`(i - a, j + b)`, `0 <= a, b <= 3`, scoring within `d` of the argmax, speak
the longest. `t` cross-validated per `d`; then `(d, t)` cross-validated
together:

    d            folds              right  a-wr  a-sil  u-sil   joint  acc|att   CLIPPED  RIVAL  n_a_s   vs d = 0
    seed 1
    0.0    -0.158 / -0.403           371   188   162    207     578   0.664       42      80     3
    1.0    -0.158 / -0.403           378   182   161    207     585   0.675       34      81     3     +7 (0/7,   p = 0.016)
    1.5    -0.158 / -0.403           379   181   161    207     586   0.677       32      81     3     +8 (0/8,   p = 0.0078)
    2.0    -0.381 / -0.236           384   185   152    203     587   0.675       28      89     4     +9 (21/30, p = 0.26)
    4.0    -0.381 / -0.236           385   182   154    204     589   0.679       24      88     4    +11 (23/34, p = 0.19)
    (d, t) CV'd together: (3.0, -0.381) / (1.0, -0.403)      387 right, 198 silent, joint 585, acc|att 0.670, +7 (14/21, p = 0.31)
    seed 2
    0.0    -0.290 / -0.894           371   186   164    207     578   0.666       36      85     3
    1.0    -0.187 / -0.894           374   168   179    209     583   0.690       25      81     2     +5 (6/11,  p = 0.33)
    1.5    -0.187 / -0.894           375   167   179    209     584   0.692       24      82     2     +6 (6/12,  p = 0.24)
    3.0    -0.187 / -0.894           375   166   180    209     584   0.693       21      81     2     +6 (8/14,  p = 0.29)
    (d, t) CV'd together: (1.5, -0.187) / (1.0, -0.894)      374 right, 209 silent, joint 583, acc|att 0.690, +5 (6/11,  p = 0.33)

**At `d = 1.5` the rule is a pure gain on seed 1 — 0 passages lost, 8 won,
p = 0.0078 — with `t` unmoved, `RIVAL` unmoved at 80 → 81, and
`not_answer_sized` unmoved at 3.** Seed 2 reads +6 at the same `d` with
`acc | att` rising 0.666 → 0.692 and `RIVAL` *falling* 85 → 82, inside its
own noise. Past `d = 1.5` on seed 1 the training fold starts trading `t` for
`d` and `RIVAL` rises to 89, which is the failure mode the plan named. The
plan's bars read: `CLIPPED` halved **FAIL** on both seeds (32 and 24 against
21 and 18 — the ceiling is 22 and 18), `RIVAL` not rising **PASS**, `right >=
371` held **PASS**. **The bar is failed and the rule ships anyway**, because
the bar was written above what the rule can reach and the measured effect
is the cleanest paired gain in this workstream: eight passages at no cost.
`d = 1.5` is the value both seeds' fixed-`d` optimum sits at or beside; the
joint `(d, t)` CV picks 3.0 on one seed-1 fold and lets `t` drift, which
costs silence, and is the reason a fixed `d` with `t` cross-validated
underneath it is the shape to ship rather than the joint search.

## `REFUSED_WRONG` is not untouched by the arms; it is the other species behind a refusal

The plan said `REFUSED_WRONG` — 82 and 86 — is *untouched by all four arms
and the only species that is a plain reading failure*. By
`score_extract_tight`'s own `why` on the top refused gold window:

    wrong_span        51 / 52      RIVAL behind a refusal
    near_miss_clip    20 / 21      CLIPPED behind a refusal
    invented          10 /  8      UNGROUNDED behind a refusal
    near_miss_det      1 /  5

**62% of it is `RIVAL` and a quarter is `CLIPPED`**, and the null head is
refusing a window where the span head *would have been wrong*, which is the
null head doing the verifier's job by accident. The species is a mirror of
`LOCATION`, not a fifth mechanism, and it moves with A3 and A4 to exactly the
extent those arms move `LOCATION` — subject to the null head then admitting
the window it now rightly refuses. The plan's ceiling arithmetic, which
counted `REFUSED_WRONG` as fixed by nothing, undercounts A4 by up to 52 and
A3 by up to 21.

## The 22 that cannot be won are two things, and one of them is a defect

The plan attributes all 22 to `grounded`'s anti-restatement rule. Rendering
`It's {gold}.` into every gold-bearing window of the 721 and asking
`grounded` why it refuses:

    gold-bearing windows                 1,211
    accepted                             1,162
    echo: no novel word                     29   -> 10 passages where every gold window refuses
    novel words not contiguous              20   -> 12 passages where every gold window refuses

**Twelve of the 22 are the contiguity test, not the restatement rule.**
`grounded` strips frame, question and source words and then asks the *remaining*
words to be contiguous in the window. `It's Stephen A. Douglas.` loses `a` to
`FRAME` and `stephen douglas` is not a run of any window; `Mandate of Heaven`
loses `of`; `best-of-seven`, `revenge and karma`, `Coton in the Elms`,
`Rugrats in Paris: The Movie`, `Tandi, in Lahaul` the same. The test was
written for `1538 2862` — two window numbers that never appear together — and
it also refuses every multi-word gold with a function word inside it.

**The repair is a relaxation and nothing the rule accepts today is refused by
it:** if the novel words fail the current test, take the reply's run from its
first novel word to its last, function words left in place, and accept when
that run is a contiguous run of the window. `1538 2862` still fails (the run
is `1538 2862`). `check_extract.py`'s seven grounding guards pass under it.
On Population A, monkeypatched into the probe with the null heads and `hybrid`:

    rule                                    seed 1                        seed 2
    as shipped                    371 right, 207 silent          371 right, 207 silent
    A  contiguity repair          374 right, 205 silent  +1      374 right, 204 silent  +0
    B  A + the plan's option 2    377 right, 205 silent  +4      375 right, 203 silent  +0

Three passages a seed for the repair and three more for the echo exemption,
each costing two or three correct silences, because the same relaxation
admits a few more wrong replies on the unanswerable half. **The 22 are a 3.1%
ceiling on paper and a ±3-passage effect in practice**, and both rules are
scorer-adjacent: `score_extract_span` calls `grounded` after `span_of` has
already passed the correct replies, so the frozen `ok` columns cannot move,
but an `invented` verdict can become a `wrong_span`. Rule 4's re-score of two
frozen checkpoints is the cost, and this file recommends the owner take
option 1 — accept it — unless rule A is wanted for its own sake as a
correctness fix, which it is.

## What the record now says about the plan's arithmetic

    species          s1    s2    the plan's arm      what was read
    REFUSED_RIGHT   103    98    A1                  unreadable as written; cross-fitted on s1: (f) 0.708, REFUSED_RIGHT 98; cross-fitted + std features: (f) 0.769 / 0.811 PASS, 376 right at 197 silent, REFUSED_RIGHT 80
    AGGREGATION      31    29    A2                  closed: every ranking loses to the null logit, dedupe is +1 / +2
    CLIPPED          42    36    A3a                 +8 / +6 at d = 1.5, 0 lost on seed 1; ceiling 20 / 18 of the species
    RIVAL            80    85    A4                  not run; owner's §8.1; now also 51 / 52 of REFUSED_WRONG
    REFUSED_WRONG    82    86    none                62% RIVAL, 25% CLIPPED behind a refusal -- A3 and A4's, not nobody's
    the 22           22    22    §3                  10 are the rule, 12 are a defect; either repair is ±3

**The plan's 69% was four independent levers each meeting its bar exactly.
One is closed, one is unreadable as written and misses its bar cross-fitted
on the one seed run, one buys a fifth of what its bar asked and does it for
free, and the largest species now has a measured lever the plan had already
retired.** The number a session can bank
today is `hybrid` plus the extent rule at `d = 1.5`: **379 and 375 of 721**
at 207 and 209 silent, 52.6% and 52.0%, `acc | att` 0.677 and 0.692.

## What ships and what does not

  * **The extent rule at `d = 1.5`, in the probe**, both seeds paired, seed 1
    at p = 0.0078 with nothing lost. It lives in the replay over
    `pairs_built_s{1,2}_popa.json`; wiring it into the reader's read path is
    R3's, beside `hybrid`, and both are read-time rules on the span head's
    scores that touch no weight.
  * **`scripts/harvest_popa_pairs.py`**, the pass that makes every read-time
    extent or ranking rule a replay, span-checked against the built harvest.
  * **`--label verifier` and `--hits-cache` in `train_null_head.py`,
    `--n-folds`/`--fold` in `train_reader_cached.py`, and
    `scripts/crossfit_hits.py`** — the cross-fitted A1, with the in-fold
    label's 95% recorded as the reason it exists, one seed read, the
    second pre-registered.
  * **Nothing in `reduce`, `grounded`, any scorer or any frozen row.** The
    contiguity repair is measured, its guards are checked, and it waits on
    the owner with rule 4's cost attached.
  * **The threshold protocol is the owner's call and it is now the largest
    free variable in the null-head arms.** `bar` matches PRIMARY; `joint` is
    what the record uses; R-T's one-SE rule is measured as unusable.

## Limits

One trunk, two head seeds, fp32, Population A only for every paired claim;
the frozen and phrase files are quoted where the trainer prints them and
arbitrate nothing here, for the eighty-fourth finding's reason. The A3a
`(d, t)` search over six values of `d` and ~3,900 of `t` on a 502-passage
fold is a wider search than a single `t`, and the fixed-`d` rows are the
honest ones for that reason: `d = 1.5` is quoted because both seeds' curves
put it there, not because a fold chose it. The margin-feature arms' `hybrid`
reads are new reads of harvests already on disk, made under a reduce chosen
after those harvests were written; the threshold is cross-validated on each
read as it always was, and nothing about the heads changed. The verifier
head's two seeds are one run each, selected on a label this file argues is
not the verifier label; their numbers are a data fact and not an arm. The
grounded repair is measured through a monkeypatch of the probe's `reduce`
path and not through a changed `corn/extract.py`, and the guard run is the
seven cases `check_extract.py` names, in the scratch replay rather than the
guard file.
