# Hundred-and-first finding — the verifier that also reads the window's fit to the question buys a better refusal on all three seeds and no more right answers, so it clears both floors, misses the bar, and its one mechanism win does not reproduce

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`scripts/train_null_head.py --window-features`, 2026-09-04 (seed 3; seeds 1
and 2 on 2026-09-04 in commit `86da847c`, whose message was the only record
until this file). Three verifier heads on the frozen `corn_jr_260m_v4_ft4g`
trunk with no weight of it moved, the shipped span head loaded frozen and never
trained, ~4 s an epoch on cached states, one Population A harvest a seed.
`evals/results/nullwf_s{1,2,3}.json` and `_popa.json`;
`paired_nullwf_s{1,2,3}.json`; `reader_funnel_nullwf_s{1,2,3}.json` and
`reader_funnel_s3.json`. `corn/reader.py` is untouched.

## 0. The arm

The shipped verifier (finding 86, arm A) reads the span head's argmax pair,
that pair's two boundary rows and three scalars about its score — `s_best`,
margin, length — and never the window. The hundredth finding's audit noticed
what that leaves out: a passage carrying "sung by Matt Monro" verbatim scored
below two windows holding no answer, because the verifier judges the pick and
not the window the pick sits in.

`scripts/window_features.py` is the five numbers that were missing, defined
once and read from the cache's own `meta` in training and from the prompt at
inference so the two cannot drift:

    overlap        question words present in the window, after a crude
                   suffix strip with an irregular-verb table ("sang" = "sung")
    overlap_frac   that overlap as a share of the question's words
    win_len        the window's length in tokens
    rel_pos        the window's position in its passage, 0 to 1
    n_windows      how many windows the passage was cut into

Training-set moments on seed 3: overlap 1.72 ± 1.37, overlap_frac 0.36 ± 0.27,
win_len 38.1 ± 6.1, rel_pos 0.46 ± 0.37, n_windows 6.2 ± 4.0. The head widens
from three scalars to eight; everything else — architecture, pair rows, the
cross-fitted verifier label, `--feat-norm std`, the article split, eight
epochs, selection on held-out balanced accuracy, the harvest — is the shipped
recipe. A checkpoint declares whether it carries the five, and
`train_reader_cached.read_cached` computes them at inference only for one
that does, so every head trained before this reads exactly as it did.

**Pre-registered, from A1's protocol (`PLAN-READER-RESIDUE.md` §6):** three
seeds; the bar protocol, extent on, hybrid reduce, each seed at its own
cross-validated threshold; the 420-right bar with the silence floor
(199 / 196 / 201) and the `acc | att` floor (0.674 / 0.693 / 0.692) held. The
mechanism bar, written before seed 3 ran: `AGGREGATION` falls by at least a
third, as it did on seed 1.

## 1. The table, three seeds

`scripts/probe_harvest_paired.py` (new; §5) reads both harvests at the bar
protocol and pairs them by passage id. It reproduces the two seeds' numbers
from `86da847c`'s message to the passage.

                  right  wrong  a.silent | u.silent  u.wrong | joint  attempt  acc|att  AGG      CV'd t
    s1 shipped      389    188      144        199       83     588   0.800    0.674    64   -1.980 / -2.061
    s1 + window     393    171      157        207       75     600   0.782    0.697    43   -0.255 / -0.489
    s2 shipped      388    172      161        196       86     584   0.777    0.693    50   -1.600 / -1.746
    s2 + window     391    163      167        202       80     593   0.768    0.706    49   -1.589 / -1.749
    s3 shipped      400    178      143        201       81     601   0.802    0.692    64   -1.882 / -2.325
    s3 + window     398    169      154        206       76     604   0.786    0.702    63   -1.726 / -2.262

Against the bars: **the 420-right bar is missed on all three seeds**
(393 / 391 / 398). Both floors are cleared on all three — correct silences
207 / 202 / 206 against 199 / 196 / 201, `acc | att` 0.697 / 0.706 / 0.702
against 0.674 / 0.693 / 0.692 — and the attempt rate is printed beside them
because it falls on every seed, by 1.8, 0.9 and 1.6 points.

The three seeds have one shape and it is not the shape the arm was aimed at:

    delta, arm - shipped     right   wrong   u.silent   joint
    seed 1                     +4     -17        +8      +12
    seed 2                     +3      -9        +6       +9
    seed 3                     -2      -9        +5       +3
    pooled                     +5     -35       +19      +24

**Fewer wrong answers on the answerable half and more correct silences on the
unanswerable half, on every seed; `right` is flat.** Under the owner's rule
(2026-09-03: a precision-only gain counts as a gain provided attempt rate is
reported beside it) this is a gain in precision — `acc | att` up 2.3, 1.3 and
1.0 points — bought at 1.8, 0.9 and 1.6 points of attempt rate, and it is not
the passages the bar counts.

## 2. Paired on the same passages, none of it is significant

McNemar over the passages both harvests hold, at each harvest's own CV'd
threshold:

                          seed 1              seed 2              seed 3             pooled
    joint bit         +12 (74/86, .385)    +9 (32/41, .349)    +3 (25/28, .784)   +24 (131/155, .174)
    right alone        +4 (53/57, .775)    +3 (22/25, .771)    -2 (21/19, .875)    +5 (96/101, .776)
    correct silence    +8 (21/29, .322)    +6 (10/16, .327)    +5  (4/9, .267)    +19 (35/54, .056)

(lost / won, then p.) The only line that approaches significance pooled is
the silence line, at p = 0.056 over 89 moved verdicts. The `right` line is
+5 over 197 moved verdicts on 2,163 answerable reads, and the fold noise the
ninety-second finding measured is ±7 a seed. **Nothing here is a direction on
`right`.**

Where the answerable verdicts moved, seed by seed:

                       s1    s2    s3
    wrong  -> silent   31    29    14
    right  -> silent   36     9    14
    silent -> right    27    17    11
    wrong  -> right    30     8     8
    right  -> wrong    17    13     7
    silent -> wrong    27    15     6

Seed 1 moved 168 answerable verdicts to net +4; seed 3 moved 60 to net −2.
The arm's action is largest where its threshold moved most (seed 1's CV'd
constants went from −1.98 / −2.06 to −0.26 / −0.49, a re-scaling of the
head's logit that the bar protocol absorbs) and smallest where the head's
scale stayed put (seed 3, −1.88 / −2.33 to −1.73 / −2.26).

## 3. The mechanism does not reproduce, and the funnel says why

`scripts/probe_reader_funnel.py` on the six harvests. The first three stages
are the span head's and do not move — same head, same ten, same argmax:

                                    s1 shipped  + window   s2 shipped  + window   s3 shipped  + window
    answerable                          721        721         721        721         721        721
    the gold in some gold window's ten  678        678         679        679         676        676
    the head ranks it first there       494        494         484        484         493        493
    that window clears the threshold    419        389         407        409         431        429
    right on this route                 362        356         364        365         372        371
    right off-route (extent rule)        27         37          24         26          28         27
    right, total                        389        393         388        391         400        398

    lost at admission                    75        105          77         75          62         64
    lost at the vote and extent          57         33          43         44          59         58

**On seed 1 the arm admitted 30 fewer gold-first windows and lost 24 fewer at
the vote** — a stricter admission that also silenced rivals, which is why
`AGGREGATION` fell 64 → 43 and `REFUSED_RIGHT` rose 78 → 91 on that seed. On
seeds 2 and 3 admission and the vote each move by at most two passages.
`AGGREGATION` reads 50 → 49 and 64 → 63. **The mechanism bar — a third off
`AGGREGATION` — is met on one seed of three and fails by its size on the other
two.** Seed 1's 21-passage fall was the fold threshold moving, not the five
features re-ranking anything: the species tables underneath move in
different directions on each seed.

    species, shipped -> arm      s1          s2          s3
    REFUSED_WRONG              93 -> 84   110 -> 113   99 -> 107
    REFUSED_RIGHT              78 -> 91    80 -> 78    71 -> 76
    AGGREGATION                64 -> 43    50 -> 49    64 -> 63
    RIVAL                      63 -> 74    59 -> 59    49 -> 44
    CLIPPED                    18 -> 23    23 -> 20    25 -> 22
    UNGROUNDED                 16 -> 13    11 -> 11    13 -> 11

This is the result the hundredth finding's audit predicted for every hand
feature: removing the question from the prompt drops in-window accuracy from
59% to 19%, so the trunk already reads each candidate with the question in
context, and five numbers about lexical overlap are a cruder restatement of
what the boundary rows already carry. Where they help is the unanswerable
half — a window with no question words in it is a little easier to refuse —
which is the one place the boundary rows of a wrong pick say least.

## 4. The selection metric disagrees with itself across seeds

Held-out balanced accuracy at the selected epoch, shipped → window:

              shipped            + window           AUC shipped -> window
    seed 1    0.7666 (ep 3)      0.7525 (ep 3)      0.8500 -> 0.8298
    seed 2    0.7520 (ep 2)      0.7497 (ep 1)      0.8311 -> 0.8305
    seed 3    0.7612 (ep 2)      0.7715 (ep 2)      0.8436 -> 0.8532

`86da847c` recorded that both heads were worse on the metric that selected
their epoch. **Seed 3 is better on it, by a point of balanced accuracy and a
point of AUC, and reads the fewest passages differently of the three.** So the
held-out metric and Population A disagree in direction on seed 3 as they did
in the ninety-ninth finding on both seeds, and the "worse at its own task"
reading was two seeds' noise. Neither direction is a pattern.

## 5. What is on disk that was not before

**`scripts/probe_harvest_paired.py`** — two reader harvests of the same
passages, read at the bar protocol with extent on and hybrid reduce, each at
its own CV'd threshold, aligned by passage id (asserted), paired by McNemar
on the joint bit, on `right` alone and on correct silence alone, with the
verdict moves and the species tables side by side, and — added for §7 — each
harvest read at the other's attempt rate by shifting both of its fold
thresholds together, as the willingness control. The seed-1 and seed-2
reads in `86da847c`'s message were done by hand and lived in no file, which is
how the eighty-fifth finding's A2 table was lost; this is that read committed,
and `probe_reduce_shipped.py`'s bar protocol is imported rather than
re-implemented.

`evals/results/paired_nullwf_s{1,2,3}.json`, `reader_funnel_s3.json` (the
shipped seed-3 funnel, which `reader_funnel.json` did not hold) and
`reader_funnel_nullwf_s{1,2,3}.json`.

## 6. Verdict and limits

**Closed as an arm aimed at `right`**: the 420 bar failed on three seeds, the
paired `right` line is +5 pooled at p = 0.78, and the mechanism it was written
for reproduces on one seed of three. Under the audit's rule — a pre-registered
bar failed on two seeds — it is closed.

**Not closed as a precision improvement, and not banked either.** §1 and §2
read it as a better refusal — fewer wrong on every seed (−17 / −9 / −9), more
correct silences on every seed (+8 / +6 / +5, pooled p = 0.056), attempt rate
down 0.9 to 1.8 points. **§7, written after this section, says the silence
half of that is the threshold and not the head**: read at the shipped head's
own attempt rate the arm has the same correct silences and is right on 8 / 5 /
4 more passages and wrong on 8 / 6 / 4 fewer. That is the arm's whole content
— about one point of `acc | att` at equal willingness, same sign on three
seeds, each inside fold noise. If the owner wants it, it costs moving
`scripts/window_features.py` under `corn/` and re-pointing `corn/reader.py`
at `nullwf_s*.pt` and its thresholds; nothing else changes. This file does not
make that call.

Limits. The extent rule at d = 2.0 and the hybrid reduce are the shipped
constants and were not re-tuned for the arm. The pooled McNemar treats the
three seeds' passages as independent trials when they are the same 1,003
passages read by three heads, so the pooled p-values are optimistic. Seed 3's
shipped baseline, 400 right, is eleven above seeds 1 and 2, and its shipped
funnel (`reader_funnel_s3.json`) was not in the record before this file.

## 7. The willingness control, run after §6 was written: the silence gain is the threshold, and what is left is one point of precision at equal willingness

§6 named the read that would settle whether §1's shape was more than a
re-tune of willingness. It is one sweep and it was written the same session:
`probe_harvest_paired.py` now moves **both** of a harvest's CV'd fold
thresholds together until its attempt rate matches the other harvest's, and
reads the table there. Shifting the pair keeps the fold structure and the
bar protocol's own constants; only willingness moves.

                     right  wrong  a.silent | u.silent  u.wrong | attempt  acc|att  AGG   shift
    s1 shipped         389    188      144        199       83     0.800    0.674    64
    s1 shipped @ arm   385    179      157        207       75     0.782    0.683    57   +0.12
    s1 + window        393    171      157        207       75     0.782    0.697    43
    s1 window @ shpd   398    179      144        199       83     0.800    0.690    50   -0.10

    s2 shipped         388    172      161        196       86     0.777    0.693    50
    s2 shipped @ arm   386    169      166        199       83     0.770    0.695    48   +0.05
    s2 + window        391    163      167        202       80     0.768    0.706    49
    s2 window @ shpd   395    165      161        199       83     0.777    0.705    50   -0.05

    s3 shipped         400    178      143        201       81     0.802    0.692    64
    s3 shipped @ arm   394    173      154        206       76     0.786    0.695    61   +0.08
    s3 + window        398    169      154        206       76     0.786    0.702    63
    s3 window @ shpd   404    173      144        197       85     0.800    0.700    64   -0.13

**At the arm's attempt rate the shipped head has exactly the arm's correct
silences on seeds 1 and 3 (207, 206) and three fewer on seed 2 (199 against
202).** §1's "more correct silences on every seed" was the arm's CV'd
threshold sitting 0.05 to 0.12 logits stricter in effect, and the bar protocol
choosing it because the stricter point held the silence share; the shipped
head moved to the same willingness refuses the same passages. The pooled
p = 0.056 on the silence line in §2 is therefore not evidence about the five
features.

What does not go away when willingness is equalised:

    arm minus shipped               right   wrong   u.silent
    at the arm's attempt rate         +8      -8        0        seed 1
                                      +5      -6       +3        seed 2
                                      +4      -4        0        seed 3
    at the shipped attempt rate       +9      -9        0        seed 1
                                      +7      -7       +3        seed 2
                                      +4      -5       -4        seed 3

**The arm's content is 4 to 9 more right and as many fewer wrong a seed at
the same willingness, same sign on all three seeds and in both directions of
the match, +17 / −18 pooled at the arm's rate and +20 / −21 at the shipped
rate.** Each seed is inside the ±7 fold noise; three of the same sign and
size are not nothing and are not a bar. On seed 1 `AGGREGATION` still falls
at matched willingness, 57 → 43, so part of that seed's mechanism win was
the head and not the threshold — and it still does not appear on seeds 2 and
3 (48 → 49, 61 → 63).

Two cautions on the control itself. `window @ shipped` on seed 3 reads 197
correct silences, four under that seed's floor of 201, so that row is not a
point the reader would ship and is quoted only as the mirror of the match.
And the match is on attempt rate over the answerable half; a match on correct
silences would move the thresholds by a different amount and was not run.

**§6's verdict, restated with this in hand.** Closed on `right` at the bar.
What the arm actually buys is about one point of `acc | att` at equal
willingness — the same right-for-wrong trade in every seed — and not the
refusal §1 described. That is the number the owner's rule would count, with
the attempt rate unchanged by construction; it is smaller than §1 made it
look, and it is the honest one.
