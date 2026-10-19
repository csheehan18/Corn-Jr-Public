# Ranking candidates together makes the checker worse on both seeds

**Full result:** The listwise verifier makes cross-window outranking worse on both seeds, so B2 fails the bar it was written for, and the metric it was pre-registered to be selected on ranks the three arms in exactly the reverse of how Population A ranks them, twice

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`scripts/train_null_head.py --listwise`, 2026-09-03. Three arms a seed on the
frozen `corn_jr_260m_v4_ft4g` trunk with no weight of it moved and the span
head loaded frozen and never trained, as everywhere in this workstream. Six
verifier heads, ~15 s an epoch on cached states.
`evals/results/null lw{00,05,10}_s{1,2}.json` and their Population A harvests.

## 0. What the arm became, and why it is not the arm that was written

`PLAN-READER-RESIDUE.md` §7.4 records the redirection and the ninety-seventh
finding measured it: the arm as first specified — *hard negatives from the gold
passage's own non-gold windows, a 50/50 mix pre-registered against one
alternative* — has no variable in it, because **56,092 of the verifier's
100,000 training nulls are already siblings**, 96.8% of every `absent_window`.
What was missing was not the negatives but the **comparison**: a pointwise
binary loss over a shuffled pool never asks which of one passage's windows
carries the answer, and that is the failure the ninety-third and ninety-sixth
findings name at 25.5% and 22.2% of the answerable half.

So B2 is the listwise variant and only that:

    loss = BCE(pointwise, pos_weight unchanged)
         + LAMBDA * softmax cross-entropy over the passage's own windows

with the epoch's order over passages so a group arrives whole in a batch, every
row still seen exactly once, and the BCE kept because a listwise term has no
absolute calibration and the unanswerable half is decided against a constant.
The architecture, the features, the pair rows, the cross-fitted verifier label,
the article split and the harvest are all the shipped arm's. **21,273 training
passages carry a positive and a sibling** (72,713 rows, mean group 3.42) and
1,158 are held out.

## 1. The selection metric, pre-registered, and the arm loses on it monotonically

Selection was pre-registered as **held-out AUC on the sibling-negative split** —
positives against the siblings of their own passages — because balanced
accuracy is pooled over a file whose negative half is 42% `absent_topical` and
cannot see the comparison this arm changes. The one-variable control is the
same recipe and the same selection rule with the listwise term removed:

    lambda        seed 1                    seed 2
              sibling AUC  rank acc     sibling AUC  rank acc
    0.0  ctrl     0.8371    0.7444        0.8047    0.7009
    0.5            0.8307    0.7504        0.7944    0.7009
    1.0            0.8278    0.7306        0.7890    0.6965

    the shipped nullpr head, scored not retrained:  0.8343 / 0.7453 (seed 1)

**Monotone decreasing in `LAMBDA` on both seeds.** A loss term that exists to
make the head rank a passage's own windows better makes held-out ranking of a
passage's own windows *worse*, consistently, at both values. Under the
pre-registered rule the arm that ships is `LAMBDA = 0.5` — the better of the
two — and no arm beats its control.

**And the control is not a straw man.** The shipped verifier already reads
sibling AUC 0.8343 and **within-passage rank accuracy 0.7453**: on three
quarters of held-out passages carrying both, every gold-bearing window already
outscores every sibling. `1 - 0.7453 = 25.5%`, which is Population A's own
outranking rate to the tenth of a point. The head is not underperforming its
training distribution. **25% is what that performance is.**

## 2. Population A ranks the three arms in the reverse order, on both seeds

Each head at its own cross-validated `t` under the bar protocol, extent rule
on, `hybrid`:

    seed 1              right  wrong  u.sil    att   acc|att   AGG
      nullpr (ships)      389    188    199   0.800   0.674     64
      lambda 0.0 ctrl     389    173    198   0.779   0.692     60
      lambda 0.5          388    174    196   0.779   0.690     57
      lambda 1.0          405    168    197   0.795   0.707     52

    seed 2
      nullpr (ships)      388    172    196   0.777   0.693     50
      lambda 0.0 ctrl     388    172    196   0.777   0.693     50
      lambda 0.5          386    174    194   0.777   0.689     55
      lambda 1.0          395    156    200   0.764   0.717     47

**`LAMBDA = 1.0` is the best arm on both seeds and the worst arm on the metric
it was to be selected by, on both seeds.** +16 and +7 right against its
control, -5 and -16 wrong, correct silence held at 197 and *raised* to 200, and
`acc | att` up 0.015 and 0.024 at an attempt rate that does not rise. That last
clause is the one that matters: this is not a willingness re-tune. Seed 1 reads
+16 right and -5 wrong at an attempt rate 0.016 **above** its control's and
0.005 below the shipped head's; seed 2 reads +7 and -16 at an attempt rate
0.013 **below** its control's. More right answers and fewer wrong ones out of
the same or fewer attempts.

**The seed-2 control is the shipped head.** `LAMBDA = 0.0` reads 388 / 172 /
196 with an identical species table, so the sibling-AUC selection picked the
same epoch balanced accuracy did and the control is not a second draw.

## 3. The mechanism bar fails, and it fails in the wrong direction

The bar `PLAN-READER-RESIDUE.md` §7.4 wrote for this arm before it ran was
**the unconditional outranking rate falls by at least half** —
`probe_reader_rank.py` read (b), the share of the 580 answerable passages
carrying both kinds of window on which a no-gold window outranks every
gold-bearing one. It is a property of the head's margins and does not depend on
a threshold.

    outranking rate            seed 1         seed 2
      nullpr (ships)         148  25.5%     129  22.2%
      lambda 0.0 ctrl        147  25.3%     129  22.2%
      lambda 0.5             161  27.8%     156  26.9%
      lambda 1.0             148  25.5%     145  25.0%

**It does not halve. It does not fall. It rises on both seeds at both
values** — +2.5 and +4.7 points at `LAMBDA = 0.5`, +0.2 and +2.8 at
`LAMBDA = 1.0`. The bar is missed by its own sign, and §1 says why it was
always going to be: the loss made held-out within-passage ranking worse, and
Population A is where that shows up unmasked.

**So `LAMBDA = 1.0`'s +16 and +7 are not the mechanism the arm claimed**, and
the arm's own failing branch is the reading: *if `right` rises while the
outranking rate is flat, the gain came from somewhere else and the arm has not
shown what it claims.* What did move, on both seeds, is `AGGREGATION` — 60 → 52
and 50 → 47 — and per-attempt precision. A within-passage contrastive term
appears to have made the head more discriminating about *whether* a window
carries the answer without making it better at ranking *which* one does, which
is a different head from the one §7.4 argued for.

    species, SHIPPED    RW    RR   AGG  RIVAL  CL  UG
      s1 lambda 0.0    102    84    60    55   18  13
      s1 lambda 1.0     99    75    52    60   18  12
      s2 lambda 0.0    110    80    50    59   23  11
      s2 lambda 1.0    105    85    47    54   22  13

`REFUSED_RIGHT` falls on seed 1 (84 → 75) and rises on seed 2 (80 → 85), and
`RIVAL` does the opposite. Neither is a result.

## 4. The bars, read as written

    bar                                          lambda 0.5 (selected)   lambda 1.0
    outranking rate halves                       MISSED, rises           MISSED, rises
    right >= 420                                 MISSED (388 / 386)      MISSED (405 / 395)
    u.silent >= 199 / 196 (each seed's floor)    MISSED / MISSED         MISSED by 2 / MET
    acc | att not below shipped                  MET / MISSED            MET / MET

**B2 does not ship.** The pre-registered selection picks `LAMBDA = 0.5`, which
is flat on Population A and worse on the mechanism; `LAMBDA = 1.0` clears
neither PRIMARY nor the mechanism bar, and **taking it because it reads best on
Population A would be choosing an arm on the population it is measured on** —
which is the error R3 explicitly refused when it declined to ship seed 3 on the
strength of its Population A row.

**What `LAMBDA = 1.0` is, instead, is the strongest unexplained consistent
signal in this workstream**: +16 and +7 right, -5 and -16 wrong, silence held,
`acc | att` up on both seeds, at no cost in attempt rate, from a loss term
aimed at something it demonstrably did not move. It is recorded here as that
and is not banked.

## What this cannot say

**It cannot say what `LAMBDA = 1.0` did.** §3 rules out the mechanism it was
built for and names what co-moved (`AGGREGATION`, precision); it does not
establish a cause. Two seeds agreeing on the direction of a 16-and-7-passage
effect is worth recording and is not worth deploying.

**The selection metric is not vindicated by being anti-predictive.** Held-out
sibling AUC could be the wrong metric, or Population A's `right` column could
be reading a threshold effect the bar protocol did not remove; nothing here
separates those. What is measured is that they disagree in the same direction
twice.

**One value of `LAMBDA` between 0 and 0.5 was not tried, and neither was one
above 1.0.** Two values were pre-registered and two were run; a sweep chosen
after seeing this table would be a sweep on Population A.

**The listwise groups are the cache's, not the runtime's.** A passage
contributes a group only when both a gold-bearing window and a sibling survived
the 100,000-row null cap, which is 21,273 of the 57,064 passages with a
positive window. A denser cache is a different arm.

**Two seeds, one trunk, one population**, Population A under `hybrid` at each
head's own bar-protocol threshold, with the control retrained under the same
selection rule so the comparison is one variable.

## What follows

**The admission lever is not reachable by a loss over these states**, which is
§7.4's own failing branch: *if the outranking rate does not fall, a listwise
loss over these states cannot rank a passage's windows, and the ninety-fourth
finding's generated frame is the next thing aimed at admission, at a much
larger cost.* That branch now fires, and the ninety-eighth finding is the
independent read on what a generated frame is worth.

**The bound the arm was quoted against still stands and is still unspent.**
`ONLY_GOLD` reads 515 and 499 of 721 (finding 96); the best arm here reads 405
and 395, which is 21% and 6% of the gap between its control and that bound.

**Left unexplained, and it is the first thing the next session should look
at:** why the arm that ranks a passage's own windows *worst* on held-out
training data reads +16 and +7 on the population, twice, at a held attempt
rate. Either the sibling-negative split is not the comparison Population A
rewards, or the listwise term buys per-window calibration that the AUC over
positives-against-siblings cannot see. A paired read of `LAMBDA = 1.0` against
its control on the 580 passages, split by whether the passage's gold window was
admitted, would separate them and costs no GPU.
