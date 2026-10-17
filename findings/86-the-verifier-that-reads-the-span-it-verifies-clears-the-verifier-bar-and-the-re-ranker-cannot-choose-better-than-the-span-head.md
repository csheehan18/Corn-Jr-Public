# 86. The verifier that reads the span it verifies clears the verifier bar, and the re-ranker cannot choose better than the span head

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**Run 2026-09-02, after the eighty-fifth finding, on the frozen
`corn_jr_260m_v4_ft4g` trunk. Three verifier heads on cross-fitted labels
and cross-fitted features off the same fold span heads, one seed each, then
the one that worked replicated on the second seed. The span head, `reduce`,
`corn/extract.py`, every scorer and every frozen row are untouched; the
verifier is a binary head that decides whether the span head's argmax is
spoken.**

The eighty-fifth finding ended with the honest-label verifier reading the
say marker alone and seeing *"he is about to be wrong"* without seeing *"he is
about to be right"*, and named the next head: one that reads the argmax
pair's own rows. This file is that head, the two arms beside it that say
what its gain is made of, and the re-ranker that tests whether the same head
can also choose *which* span.

## The two measurements that shaped the arms

**The gold is the span head's runner-up.** Over `pairs_built_s{1,2}_popa.json`,
the best rank of a `tight` pair among the top ten of the decisive window,
per species of the residue under the shipped reader:

    species          n          rank 1   rank 2   rank 3   rank 4-10   not in top 10   median gap to argmax
    REFUSED_RIGHT   103 / 98    103 / 98     -        -         -             -             0.00
    RIVAL            80 / 85       -      31 / 47   8 / 10    29 / 21        12 / 7         3.21 / 2.91
    REFUSED_WRONG    82 / 86       -      23 / 30  11 / 13    29 / 26        19 / 17        3.99 / 3.03
    CLIPPED          42 / 36       -      27 / 20   6 /  3     6 /  8         3 /  5        1.99 / 2.54

On 85% and 92% of `RIVAL` windows and 77% and 80% of `REFUSED_WRONG` windows
the gold is in the span head's top ten, and on about 40% it is the very next
pair. That is the ceiling of any rule that chooses among candidates rather
than pointing afresh, and it is high.

**The first cross-fitted verifier had an honest label and dishonest
features.** The eighty-fifth finding's `--features std --label verifier` arm
read its three scalars off `feats_reader_built_s1.pt` -- the deployed head's
`s_best` on windows it memorised, mean well above what it reads on
Population A -- beside a label from fold heads. `scripts/crossfit_hits.py`
now writes label, scalars and candidates from the fold heads in one pass, so
every input the verifier trains on is out of fold, and the training `s_best`
reads **11.3 +- 6.2** rather than a memorised head's. A gold pair is in the
fold heads' top five on **82.1%** of gold-bearing windows; their argmax hits
on 51.4%.

## The three arms, seed 1

All three: `train_null_head.py --label verifier --feat-norm std`, the
cross-fitted `hits_reader_built_s1.pt`, eight epochs, the same article split,
selection on held-out balanced accuracy over whatever rows the arm trains on.

    arm        what the head reads                                        rows trained on
    B          h_last + the pair's three scalars (honest)                  one per window
    A          h_last + the scalars + the argmax pair's rows h_i, h_j      one per window
    C          A's inputs, for every one of the top five pairs             one per candidate; at
               (top two on a null window), label "this pair is gold"      inference the verifier
                                                                           scores the deployed
                                                                           head's top five and
                                                                           speaks its favourite

    read                                     B  scalars    A  pair rows   C  re-ranker   eighty-fifth's   presence
                                                                                          in-fold-feature   s1 (record)
    selection, held-out balanced accuracy    0.7443 *      0.7666         0.7670 **      0.7911            0.7570
    frozen  (f) AUC | attempted              0.7738/113    0.7761/127     0.6397/144     0.7696/99         0.6816/140
            (f) all 200 items                0.7564        0.7811         0.7012         0.7694            0.6456
    phrase  (f) AUC | attempted              0.7415/28     0.8050/30      0.6310/46      0.8772/25         0.7038/56
            (f) all 89 items                 0.8103        0.7374         0.7575         0.8113            0.6777
    (c) `other` acc | att                    0.737         0.680          0.528          0.706             0.458
    frozen tight / abstain / joint           -              102/165/267   104/150/254    -                 102/153/255
    Population A under hybrid, joint t       379 / 185     367 / 233      348 / 199      376 / 197         371 / 207
      folds                                  -1.30/-1.80   -1.41/-1.41    -1.16/-1.74    -2.49/-2.99       -0.16/-0.40
      joint                                  564           600            547            573               578
      precision                              58.0%         66.5%          56.9%          60.4%             59.4%
      acc | att, attempt rate                0.680, 77%    0.730, 70%     0.658, 73%     0.699, 75%        0.664, 78%
      under the bar protocol                 375 / 195     381 / 200      367 / 192      382 / 193         371 / 201
    species  REFUSED_RIGHT                    78            113            90             80               103
             REFUSED_WRONG                   112            136           123            124                82
             RIVAL                            59             42            47             53                80
             CLIPPED                          31             22            44             29                42
             AGGREGATION                      51             31            56             49                31
             owners NULL / LOCATION / REDUCE 190/101/51     249/74/31     213/104/56     204/92/49         185/134/31

    *  B's selection is on the window label; ** C's on the candidate label; neither is comparable to the presence column.

**Arm A is the head the eighty-fifth finding asked for, and on seed 1 it is
the first reader on this record whose joint on Population A is 600** (seed 2
reads 575; §"Seed 2"). The previous
best was 578. It gets there by refusing: unanswerable `silent` reads 233 of
282 (82.6%, against the plan's 85% target and the record's 207), precision
66.5% against 59.4%, `acc | att` 0.730 against 0.664, and `RIVAL` falls from
80 to 42 and `LOCATION` from 134 to 74 as the head declines the windows the
span head would have read wrong. On the frozen file its `joint(tight)` is
**267 against R1's bar of 270** -- the closest any arm has come to the
eighty-third finding's primary bar -- with `abstain` 165, and (f) passes on
both files on both readings: **0.776 / 0.781 frozen, 0.805 / 0.737 phrase**.

**At the joint optimum it fails PRIMARY's `right` by four (367 against 371)
and under the bar protocol it passes both halves: 381 right at exactly 200
silent.** This is the eighty-fifth finding's protocol point made concrete: a
head that ranks better lets the joint optimum choose a conservative point,
because a correct silence is worth exactly a correct answer to `joint` and
this head can buy silences cheaply. The bar's own shape -- `right` subject to
the silence floor -- reads the same head at 381, ten over the null head's 371
at the same floor. **The protocol is the owner's call and it is now worth
fourteen passages on this arm.**

**The species table says what the pair rows bought.** Against B -- the same
head without the rows -- A moves `RIVAL` 59 → 42 and `LOCATION` 101 → 74
while `REFUSED_RIGHT` goes 78 → 113 and `REFUSED_WRONG` 112 → 136 at the
joint optimum. The rows make the head a better judge of *wrong*: with the
span's own states in front of it, it refuses the same-type rival the say
marker could not see. What it does not do is admit more of the right ones
at that operating point; under the bar protocol, where the two arms are
read at the same silence, A reads 381 against B's 375, so it does admit
more of them once the threshold is allowed to spend the silence it saved.

**Arm C, the re-ranker, fails, and the failure is informative.** Its
held-out pick rate -- over windows with a gold among the fold head's top
five, how often the verifier's favourite is gold -- reads **0.649 at epoch 0
and never above 0.657**, against the fold head's own argmax being gold on
62.6% of those same windows (51.4 of 82.1). The verifier ranks candidates
almost exactly as the span head already ranks them. On Population A it
speaks a different span on the windows where it disagrees and reads 348
right, `CLIPPED` doubling to 44 and `AUC | attempted` collapsing to 0.640,
because its logit is now doing two jobs and is calibrated for neither. **A
concatenation MLP over `[h_last; h_i; h_j]` with the pair's scalars cannot
tell the singer from the composer any better than the pair scorer with a
pointer term can.** The "which" question stays a representation question
-- R2's, `PLAN-EXTRACTION-READER.md` §7's -- and the verifier's job is
"whether". The re-ranker is retired as a design; its inference path stays in
`read_cached` behind the head's `rerank` attribute so the reading can be
reproduced.

## Stacked with the extent rule

The eighty-fifth finding's extent rule at read time, on arm A's harvest
(the spans are the deployed head's argmax, so `pairs_built_s1_popa.json`
applies), `t` cross-validated per `d`:

    d        right  a-wr  a-sil  u-sil  joint  acc|att   CLIPPED  RIVAL   vs d = 0
    0.0       367   136   218    233    600    0.730       22      42
    1.5       373   130   218    233    606    0.742       15      42     +6 (0/6,  p = 0.031)
    2.0       374   129   218    233    607    0.744       13      43     +7 (0/7,  p = 0.016)
    3.0       375   129   217    233    608    0.744       13      44     +8 (0/8,  p = 0.0078)

    under the three protocols, d = 2.0
    joint     374 right, 233 silent, joint 607, acc|att 0.744
    bar       389 right, 199 silent, joint 588, acc|att 0.674     53.9% of the answerable half
    one-SE    395 right, 190 silent, joint 585, acc|att 0.672

Nothing lost on any row. **The stack reads joint 607 at the record's
protocol, or 389 right at the silence floor under the bar's** -- against 578
and 371 at the start of the day.

## Seed 2: the precision replicates, the joint does not, and the verifier bar half-passes

Two fold heads on seed 2's article split (held-out exact-pair 0.513 / 0.516),
the same harvest (out-of-fold hit 51.7%, gold in the top five 82.0%), the
same arm A recipe:

    read                                        A s1            A s2            presence s1 / s2
    selection, held-out balanced accuracy       0.7666          0.7520          0.7570 / 0.7381
    frozen  (f) AUC | attempted                 0.7761 PASS     0.7318 FAIL     0.6816 / 0.6607
            (f) all 200 items                   0.7811          0.7880          0.6456 / 0.6470
    phrase  (f) AUC | attempted                 0.8050 PASS     0.6515 FAIL     0.7038 / 0.5455
            (f) all 89 items                    0.7374          0.6687          0.6777 / 0.6097
    (c) `other` acc | att                       0.680           0.640           0.458 / 0.435
    frozen tight / abstain / joint(tight)       102/165/267     96/171/267      102/153/255 / 76/177/253
    Population A, joint t                       367 / 233       368 / 207       371 / 207 / 371 / 207
      joint                                     600             575             578 / 578
      precision                                 66.5%           61.3%           59.4% / 59.5%
      acc | att, attempt rate                   0.730, 70%      0.701, 73%      0.664, 78% / 0.666, 77%
      under the bar protocol                    381 / 200       384 / 197       371 / 201 / 375 / 198
      + extent d = 2, joint t                   374 / 233       372 / 207       379 / 207 / 375 / 209 (d = 1.5)
      + extent d = 2, bar protocol              389 / 199       388 / 196
    species  REFUSED_RIGHT                       113             91             103 / 98
             REFUSED_WRONG                       136            139              82 / 86
             RIVAL                                42             47              80 / 85
             CLIPPED                              22             23              42 / 36
             owners NULL / LOCATION / REDUCE     249/74/31      230/81/42       185/134/31 / 184/137/29

**What replicates, and it is the mechanism.** `RIVAL` halves on both seeds
(80 → 42, 85 → 47) and `LOCATION` falls by nearly half (134 → 74, 137 →
81); precision rises on both (59.4 → 66.5, 59.5 → 61.3) and `acc | att` with
it (0.664 → 0.730, 0.666 → 0.701); the frozen `joint(tight)` reads **267 on
both seeds** against R1's bar of 270, and the frozen all-items verifier AUC
reads **0.781 and 0.788**, the first two readings above 0.75 on that floor.
Under the bar protocol -- the same silence floor for every arm -- the head
reads **381 and 384 right against the null head's 371 and 375**, +10 and +9,
and **389 and 388 with the extent rule**, 53.9% and 53.8% of the answerable
half.

**What does not replicate is the joint at the record's protocol.** 600 on
seed 1 is 575 on seed 2, and 575 is *below* the null head's 578: seed 2's
joint optimum lands at the same 207 silences as the null head and three
fewer right answers, where seed 1's landed at 233 silences and four fewer.
The joint optimum is choosing a different trade on each seed of a head that
can make either, which is the eighty-fifth finding's protocol point a third
time. And the verifier bar (f) passes on both files on seed 1 and on neither
attempted subset on seed 2 (0.732 frozen, 0.652 phrase), while the all-items
frozen number passes on both; **(f) is one seed's pass and one seed's near
miss, and is reported as that.**

**So the honest statement about arm A is:** a verifier that reads the span's
own rows is a precision lever that replicates -- it halves the same-type
rival on both seeds by refusing it -- and buys about ten passages at the
silence floor on both seeds, twenty with the extent rule; its headline joint
and its verifier-bar pass are seed 1's. It does not move `REFUSED_RIGHT`
down on either seed at the joint optimum and does move it under the bar
protocol (the ten it buys are those); the species the owner asked about is
now bounded by the head's operating point rather than by its signal.

## Four follow-ups, chosen after the seed-2 read and run the same evening

### The joint optimum is a plateau, so the protocol question is not a preference

Within two joint of each training fold's maximum, `hybrid`, the candidate
thresholds that qualify and how far `right` and unanswerable `silent` swing
across them on that fold (502 passages, so double the swing for the
population); then what the *held-out* fold reads at the plateau's two ends:

    harvest        fold   max   plateau t          n t    right      u-silent    held out at low / high end
    null s1          0    284   -0.381..-0.071     102   178-190     92-104      (191, 108) / (177, 118)
                     1    300   -0.481..-0.196     158   184-193    105-114      (191,  88) / (183,  99)
    null s2          0    286   -0.381..-0.172      90   171-179    105-113      (182, 115) / (173, 124)
                     1    303   -0.971..-0.830     123   204-209     92-97       (199,  81) / (192,  87)
    pair rows s1     0    297   -1.972..-1.125     134   177-194    101-118      (189, 105) / (168, 122)
                     1    304   -1.428..-1.391      22   182-185    117-120      (182, 114) / (183, 114)
    pair rows s2     0    288   -1.644..-1.538      54   186-188     99-100      (197, 105) / (193, 105)
                     1    305   -1.708..-1.299      33   189-200    103-114      (189,  94) / (171, 103)
    3b std s1        0    290   -1.235..-0.674     112   188-198     90-100      (197, 100) / (186, 109)
                     1    299   -1.472..-1.028     138   195-202     95-102      (202,  84) / (194,  94)
    3b std s2        0    274   -2.170..-1.193     112   183-202     70-89       (207,  76) / (196,  91)
                     1    289   -1.386..-1.167      99   196-199     88-91       (187,  82) / (180,  89)

**Two joint is not a tolerance, it is the whole trade.** Across a band the
objective cannot tell apart, a fold's `right` moves by up to 17 and its
silences by the same 17 in the other direction; on the population that is
plus or minus fifteen to thirty right answers at one and the same joint. The
"optimum" the record has been quoting is where the lowest `t` in a flat band
happened to fall -- `cross_validate` takes the lowest `t` among ties, which
is why the fold values differ so much between harvests that read the same
joint. On the pair-rows head seed 1's fold 0 has a 134-threshold plateau
whose two ends read 189 and 168 right on the held-out fold; that is the
600-against-575 gap in one row. **So the three-protocol table in the
eighty-fifth finding is not three preferences. `joint` does not choose; the
bar's shape does, and R-T's one-SE rule chooses the wrong end. The plan's
§6.2 recommendation stands, and it is now the only determinate option.**

### R1's joint clause is crossed on the frozen file, and the tight clause is not

`scripts/probe_extent_frozen.py`: the extent rule off the eval cache, in
front of the pair-rows verifier, `t` cross-validated on the frozen file and
applied cold to the phrase file (the eighty-third finding's protocol), `d`
fixed at Population A's values rather than searched here.

    head              d      frozen tight  abstain  joint(tight)     phrase tight  abstain  joint
    pair rows s1      0.0        102         165       267               20         48      68
                      1.5        106         165       271               20         48      68
                      2.0        107         165       272               20         48      68
    pair rows s2      0.0         96         171       267               18         44      62
                      1.5        101         171       272               18         44      62
    presence s1       0.0        102         153       255               26         41      67
                      1.5        106         153       259               27         41      68
    presence s2       0.0         76         177       253               16         48      64
                      1.5         81         177       258               16         48      64
    R1 bar (a)                  >= 125      >= 150    >= 270   (b)      >= 45      >= 40

**`joint(tight) >= 270` is crossed for the first time since it was written
-- 271 / 272 on the two seeds at `d = 1.5`, 272 / 272 at 2.0 -- and bar (a)
still fails, because `tight` reads 106 and 101 against 125.** The verifier
buys the joint with abstention (165 and 171 against the presence head's 153
and 177) and the extent rule adds four and five tight, which is what it
added per 200 on Population A. Bar (b) fails as it always has: the phrase
file's `tight` is 20 and 18 against 45 behind this head, *worse* than the
presence head's 26, because the verifier refuses most of the phrase file
(48 and 44 of 53 abstentions). **What this closes is the joint clause; what
it says is that the frozen ladder's remaining distance is location and not
willingness**, which is the eighty-third finding's sentence again with the
willingness half now paid for.

### A third seed of the whole stack, and seed 2 is the odd one out

A third built span head (`reader_built_s3`, held-out exact-pair 0.5554,
frozen tight ungated 134/200), its own presence null head as the baseline,
two fold heads (0.5008 / 0.5286), the cross-fitted harvest (out-of-fold hit
51.7%, gold in the top five 82.1%) and the pair-rows verifier, nothing else
changed:

    read                                     presence s3     pair rows s3     pair rows s1 / s2
    selection, held-out balanced accuracy    0.7445          0.7612           0.7666 / 0.7520
    frozen  (f) AUC | attempted              0.6556/112      0.7522/137 PASS  0.7761 / 0.7318
            (f) all 200 items                0.6595          0.8001           0.7811 / 0.7880
    phrase  (f) AUC | attempted              0.6407/42       0.7421/33        0.8050 / 0.6515
            (f) all 89 items                 0.6249          0.7280           0.7374 / 0.6687
    (c) `other` acc | att                    -               0.571            0.680 / 0.640
    frozen tight / abstain / joint(tight)    -               110/168/278      102/165/267 / 96/171/267
    Population A, joint t                    372 / 207       388 / 210        367 / 233 / 368 / 207
      joint                                  579             598              600 / 575
      precision, acc | att                   59.0%, 0.669    62.0%, 0.700     66.5%, 0.730 / 61.3%, 0.701
      under the bar protocol                 373 / 205       391 / 201        381 / 200 / 384 / 197
      + extent d = 2, joint t                (d=1.5) 388/202 396 / 210        374 / 233 / 372 / 207
      + extent d = 2, bar protocol           (d=1.5) 384/205 400 / 201        389 / 199 / 388 / 196
    species  REFUSED_RIGHT / REFUSED_WRONG    95 / 88        78 / 119         113 / 136 / 91 / 139
             RIVAL                            72             43               42 / 47
             CLIPPED                          41             29               22 / 23

**On seed 3 the frozen `joint(tight)` reads 278 without the extent rule** --
R1's `>= 270` crossed outright, `abstain` 168 -- and (f) passes the frozen
file on the attempted subset (0.752) and on all 200 items (0.800). Population
A reads +16 right at +3 silences over its own baseline at the joint
protocol, joint 579 → 598, and **400 right at 201 silent with the extent
rule under the bar protocol: 55.5% of the answerable half.** `RIVAL` goes
72 → 43, and this is the one seed on which `REFUSED_RIGHT` falls at the
joint optimum as well, 95 → 78.

**Three seeds, and the direction is now a direction.** Joint at the record's
protocol: +22 / -3 / +19. `right` at the silence floor under the bar
protocol: +10 / +9 / +18, and +18 / +13 / +27 with the extent rule. `RIVAL`
halved on all three. Frozen all-items verifier AUC 0.781 / 0.788 / 0.800,
all three above the 0.75 that no head had reached on that floor before;
the attempted-subset (f) passes the frozen file on two seeds of three and
the phrase file on one. Seed 2 is the one that under-reads on every row,
and it is one seed of three rather than one of two.

### The four-fold label: refused-right was not the fold heads' weakness

The cross-fit limit named above -- each fold head sees half the articles, so
a hard window the deployed head reads right and both fold heads miss is a
positive labelled 0, a bias pointed at `REFUSED_RIGHT` -- tested by giving
each head three quarters. `train_reader_cached.py --n-folds 4 --fold k
--fold-rest`, four heads on seed 1's trunk (held-out exact-pair 0.5553 /
0.5316 / 0.5279 / 0.5328 against the two-fold heads' 0.5048 / 0.5066 and the
deployed 0.5410), each labelling the quarter it never saw; then the same
pair-rows verifier recipe on that label.

    read                                     two-fold label s1    four-fold label s1
    out-of-fold hit rate / gold in top five  51.4% / 82.1%        52.9% / 83.3%
    selection, held-out balanced accuracy    0.7666               0.7561
    frozen  (f) AUC | attempted              0.7761/127 PASS      0.8137/106 PASS
            (f) all 200 items                0.7811               0.7629
    phrase  (f) AUC | attempted              0.8050/30  PASS      0.7857/25  PASS
            (f) all 89 items                 0.7374               0.8118
    frozen tight / abstain / joint(tight)    102/165/267          87/173/260
    Population A, joint t                    367 / 233, joint 600 384 / 195, joint 579
      precision, acc | att, attempt          66.5%, 0.730, 70%    59.6%, 0.689, 77%
      under the bar protocol                 381 / 200            381 / 196
      + extent d = 2, bar protocol           389 / 199            388 / 197
    species  REFUSED_RIGHT                    113                  85
             REFUSED_WRONG                   136                  111
             RIVAL                            42                   58
             CLIPPED                          22                   27

**The stronger label moves the head along the same trade and buys nothing at
the floor.** `REFUSED_RIGHT` falls 113 → 85 at the joint optimum and `RIVAL`
rises 42 → 58 with it: the head trained on the stronger reader's label
admits more and refuses less, precision 66.5 → 59.6, and the joint optimum
lands at 195 silences instead of 233. Read at the same silence floor, where
the two labels can be compared, the count is **identical: 381 and 381, 389
and 388 with the extent rule.** (f) passes on both files under both labels.
**The cross-fit bias is retired as the explanation of `REFUSED_RIGHT`**: a
label from a reader nearly as strong as the deployed one produces a head
that reads the same number of right answers at the same silence, and what
differs is where the joint protocol chooses to stand. The remaining
`REFUSED_RIGHT` is the head's signal and not its label, and the four-fold
harvest costs four span-head runs for it, so the two-fold label is the one
that ships.

## What ships and what does not

  * **Arm A, the pair-rows verifier, is the arm with a claim on shipping
    under the bar protocol**, +10 / +9 / +18 at the silence floor on three
    seeds (+18 / +13 / +27 with the extent rule) and the same-type rival
    halved on all three; under the record's joint protocol it reads +22 / -3
    / +19, a protocol the plateau section shows cannot choose. The protocol
    decision is the shipping decision, and the two-fold label is the one
    that ships. It touches no weight of
    the span head and is a head file beside it; wiring is R3's, with
    `read_cached`'s gather of the argmax rows as the reference.
  * **`scripts/crossfit_hits.py`** now writes label, scalars and top-K
    candidates from fold heads in one pass; **`train_null_head.py --cands
    --pair-rows`** trains arm A and **`--rerank`** arm C; `read_cached`
    reads both.
  * **The re-ranker does not ship** and no further arm in that family is
    proposed: its ceiling was measured high and its pick rate did not move
    off the span head's.
  * **The threshold protocol is now the largest free variable on the
    shipping arm** and is the owner's to settle once.

## Limits

One trunk, fp32, one seed for arms B and C and for the four-fold label,
three for A. Every fold head is weaker than the deployed head (held-out exact-pair
0.505 and 0.507 against 0.541), so the cross-fitted label and features are a
harder verifier's, and the deployed head's argmax rows at inference are a
slightly different distribution from the fold heads' at training -- the
stacking rule's usual cost, accepted rather than removed. The frozen and
phrase files arbitrate nothing threshold-dependent (eighty-fourth finding);
(f) is an AUC and does not depend on the threshold except through the
attempted subset, and the all-items number is printed beside it every time.
The selection metric for arm C is candidate-level balanced accuracy, and the
pick rate that actually describes a re-ranker was printed beside it and not
selected on; a re-ranker selected on its pick rate would be a different arm,
and the curve (0.649 → 0.657 → 0.628) says it would not have been a better
one. The extent stack's `d` is fixed at the value both seeds' curves chose
in the eighty-fifth finding, not searched here.
