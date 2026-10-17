# Eighty-ninth finding — the rival is positional on the shipped verifier, §6.3's premise fails there and holds only on the head it was written from, and the position prior is earned

`scripts/probe_reader_position.py` and `scripts/probe_verifier_position.py`,
2026-09-03. **Replay only** -- no GPU, no decode, no weight read, no tokenizer
-- over two harvests: `evals/results/nullpr_s{1,2}_popa.json`, the **shipped**
pair-rows verifier A1 settled on, and `evals/results/null_s{1,2}_popa.json`,
the presence-label head `probe_reader_species.py` was run on. The baselines
reproduce §6.1b to the passage: joint-protocol **367 / 233 (joint 600)** and
**368 / 207 (joint 575)**.

**Reading it on the wrong one of those two harvests inverts two of the three
results, and that is the first thing this finding has to say.**

## Where it came from, and the defect it found on the way

`PLAN-READER-RESIDUE.md` §6.3 aims A4 at "`RIVAL` 80 / 85 **plus** the 51 / 52
of `REFUSED_WRONG` whose top refused gold window reads `wrong_span` -- the same
failure behind a refusal", and A4's ceiling arithmetic takes up to 52 passages
from that clause. Two things were unmeasured under it: whether `RIVAL` is the
sixty-sixth finding's *positional* rule or merely a same-type competitor
(`rival_ty` records type and no offset), and whether "the same failure" is true.

**But §6.3's counts are the superseded head's.** `probe_reader_species.py`
reads `null_s{1,2}_popa.json`, and §6.1b had already moved `RIVAL` to 42 / 47
on the pair-rows verifier that ships. The species table §6.3 quotes describes
a head `corn/reader.py` does not load. Measured here, on the shipped harvest:

    species                        null_s* (quoted by §6.3)   nullpr_s* (ships)
    RIVAL                                   80 / 85                42 / 47
    REFUSED_WRONG, all                      82 / 86              136 / 139
    REFUSED_WRONG, `wrong_span` only        51 / 52                81 / 82

So A4's stated target of 131 / 137 is, on the head it would run against,
123 / 129 -- and split differently, which §1 shows matters more than the count.

## The statistic, and the null that had to be measured first

Position is in **content-word index space**, `content_words(window)`, because
`span_of` and `longest_span` define a gold-bearing window as one where the
gold's content words are a contiguous run. Per window: `gi` the gold's run
index, `si` the spoken span's, verdict `EARLIER` / `LATER` / `SAME` /
`UNLOCATABLE`.

**The 50/50 null is wrong.** A span start drawn with no positional preference
falls before a *late* gold most of the time, because there is more window in
front of a late gold. The honest null is `gi / (L - 1)` per window, tested
with a Poisson-binomial z since every window carries its own probability. It
measures 52-53% on `RIVAL`'s windows and 46-47% on `REFUSED_WRONG`'s -- **the
two species do not even share a null**, which is by itself a reason not to
have pooled them on a raw share.

## 1. On the shipped verifier §6.3's premise fails, and on the head it was written from it holds

    shipped (nullpr)      seed 1              seed 2            pooled
    RIVAL             36/48   75.0%      46/62   74.2%     82/110  74.5%  p=2.5e-07
    REFUSED_WRONG     46/81   56.8%      43/82   52.4%     89/163  54.6%  p=0.27
    Fisher, the two     p = 0.0401         p = 0.00945       p = 0.00090

    superseded (null)     seed 1              seed 2            pooled
    RIVAL             66/101  65.3%      68/115  59.1%    134/216  62.0%  p=0.0005
    REFUSED_WRONG     31/51   60.8%      29/52   55.8%     60/103  58.3%  p=0.11
    Fisher, the two     p = 0.596          p = 0.736         p = 0.541

**Two sets that were indistinguishable on the presence-label head separate on
the shipped one, at both seeds and pooled.** A4 may not treat its target as
one thing, and its bar (a) -- *`RIVAL` halved by type* -- reads the `RIVAL`
half only, so the 81 / 82 `wrong_span` refusals would ride along unmeasured.
That is exactly the failure mode the premise existed to rule out.

**The mechanism is legible.** The pair-rows verifier reads the argmax pair's
own rows, so it is equipped to catch a span that does not answer the question
-- and `RIVAL` 80 → 42 is it doing so. What it removes preferentially is the
*semantic* rival; what it leaves is enriched for the positional one. The
residue got smaller and its character changed, which is why a species count
quoted from a superseded head is not a safe input to an arm's arithmetic.

## 2. On the shipped verifier the rival is substantially positional

    species          seed 1 obs/null      seed 2 obs/null
    RIVAL          75.0% / 53.3%  +21.7  74.2% / 52.1%  +22.1   z 3.69 / 4.26
    REFUSED_WRONG  56.8% / 47.2%   +9.5  52.4% / 46.5%   +5.9   z 2.12 / 1.35

`RIVAL`'s lift is **+22 points on both seeds**, p = 2.3e-04 and 2.1e-05, and
its pooled sign test is p = 2.5e-07. On the superseded head the same quantity
read +14.1 / +10.7. **So the conclusion drawn from `null_s*` -- that the rival
is semantic and the sixty-sixth finding's runtime repair is not its lever --
is wrong about the head that ships.**

It is still not the sixty-sixth finding's *rule*: that was 20 of 21 = 95.2%
against the same kind of null, and 74.5% leaves a quarter of these windows
choosing a span that comes *after* the gold. `SAME` is empty on every harvest
and `UNLOCATABLE` is one window in 449. But +22 against a measured null is a
different object from +12, and it is enough to make the locality rule worth
pricing on `RIVAL` specifically.

`REFUSED_WRONG`/`wrong_span` is the opposite: **not positional**, pooled 54.6%
at p = 0.27, and seed 2 alone does not clear 0.05 on the lift either
(p = 0.18). Its 81 / 82 passages need a different lever from `RIVAL`'s 42 / 47,
and no lever in the plan is currently named for them.

## 3. The verifier's position prior is real, strong, and earned -- on both heads

Over every gold-bearing window where the span head's top pair **is** the gold
-- 803 and 779 windows, so admitting is the only correct action -- the shipped
verifier's margin falls as the gold sits later:

    seed 1   admitted 540 / refused 263   rel. position 0.294 adm / 0.394 ref
    seed 2   admitted 550 / refused 229                 0.322 adm / 0.379 ref

    Spearman rho(position, margin)   -0.165  z = -4.68  p = 2.8e-06
                                     -0.212  z = -5.91  p = 3.4e-09
    (on the superseded head, -0.249 and -0.245 at p ~1e-12)

    margin by gold-position quintile, early -> late
      s1   +0.122  -0.806  -0.879  -0.824  -0.903
      s2   +0.094  -0.746  -0.760  -0.801  -0.986

**It is not a window-edge effect and that was the hypothesis.** Words to the
nearest edge read median 7.0 admitted against 8.0 refused on all four
harvests. The effect is monotone in *linear position* and concentrated in a
first quintile that is the only one above zero.

`span_features` feeds the verifier three scalars -- top pair's score, margin
over the runner-up, length -- and **no position**, so this looked like a free
feature and a bug. **It is neither, and the arm that assumed so loses.**
Slope fit on the training fold's gold labels, applied to the test fold through
the *spoken* span's position, threshold swept on the training fold's corrected
margins:

    seed 1  baseline   right 367  unans silent 233  joint 600  acc|att 0.730
            de-biased  right 357  unans silent 230  joint 587  acc|att 0.704
    seed 2  baseline   right 368  unans silent 207  joint 575  acc|att 0.701
            de-biased  right 351  unans silent 225  joint 576  acc|att 0.716

    -10 right / -13 joint  and  -17 right / +1 joint

**Because the prior is earned.** Position genuinely predicts presence:

    P(window carries the gold), by quartile of position within the passage
      first  606 of 969 = 62.5%      third  292 of 813 = 35.9%
      second 203 of 613 = 33.1%      fourth 110 of 399 = 27.6%

    the gold's relative position inside gold-bearing windows:
      median 0.356, mean 0.394   (uniform would be 0.5)

These are Wikipedia passages and the answer lives near the lead. Conditioning
on tight gold-bearing windows makes the prior *look* like bias because
presence is held fixed inside that set; the verifier is scored over the whole
population, where the same trend is calibration. This is the one result that
does not move between the two harvests.

## What this cannot say

**Nothing here is causal.** The sixty-sixth finding could speak to cause
because it controlled the passage -- the same fixtures with the clause flipped
answered differently. This is observational over NQ, where gold position and
every semantic property vary together. §2 establishes that `RIVAL`'s spoken
span is the earlier one about twenty-two points more often than indifference
predicts; it does not establish that position is why, and the clause-flip
control on `--reader head` is what would.

**§1's separation is a difference in one statistic**, not a demonstration that
the two species have unrelated causes. It is enough to forbid one bar reading
both; it is not a mechanism for either.

**§3's de-bias arm tests one correction and it is linear.** The quintile
table -- one first quintile above zero and four flat below it -- is not a
shape a slope models well, and that is the likeliest reason a linear removal
overshoots. What it establishes is that the obvious repair fails, not that
none could. Its `right` column is also unstable: an earlier implementation
that swept over a hand-built candidate list rather than
`probe_reader_passages.candidates` read -5 / -9 on the superseded head where
the corrected run reads -4 / +3. `joint` was negative in every version, which
is why the claim rests on `joint`.

**§3's control is about this population.** A corpus whose answers were
positioned uniformly would make the prior bias again.

## What follows

**Re-state A4 before running it.** Its target is 42 / 47 plus 81 / 82 on the
head it would run against, not 80 / 85 plus 51 / 52; the two halves separate
at p = 0.0009; and its bar reads only the first. As written it would spend
~1 h of GPU a seed and be unable to say what it bought on two thirds of its
passages.

**Price the sixty-sixth finding's locality repair on `RIVAL` after all.** At
+22 points against a measured null it is a live candidate for those 42 / 47,
which is the reverse of what the superseded harvest said. It stays
precision-only -- it declines rather than corrects -- and a quarter of `RIVAL`
picks late, so its ceiling is well under 42.

**The owner has taken that trade in advance** (2026-09-03): a precision-only
arm is worth running and a flat `right` column is not a reason to drop one, so
long as the attempt rate is reported beside it. So this arm is not blocked on
its shape, only on the design question §4 leaves open.

**Name a lever for `REFUSED_WRONG`/`wrong_span`.** 81 and 82 passages, not
positional, and no arm in either plan is aimed at them. §2 of the residue plan
already called `REFUSED_WRONG` "the only species here that is a plain reading
failure with no cheap lever named for it"; this finding says its `wrong_span`
majority is not the positional failure `RIVAL` is, so it cannot borrow one.

**And re-run `probe_reader_species.py` on `nullpr_s{1,2}_popa.json`.** Every
species count in `PLAN-READER-RESIDUE.md` is the presence-label head's. The
plan's arithmetic, its four arms' sizes and §2's 69% ceiling are all computed
from them.

## 4. The one thing the locality arm needs settled before it can be priced

The sixty-sixth finding names the rule as "reject an extraction whose span is
not local to the question's distinguishing term" and **does not define the
distinguishing term**, which is the whole content of the rule. Three readings
are available and they are not equivalent:

    the question's content words absent from the gold      -- "boiling" in
        "the boiling point of iron", once "iron" is discounted as shared
    the question's head noun                               -- "point"
    every question content word, distance to the nearest    -- degenerate on
        long questions, where some word is always adjacent

`corn.extract.grounded` already computes the question's content-word set for
the anti-restatement rule, so the first reading is the cheapest to build and
is the one the sixty-sixth finding's own example fits. **A price quoted before
this is chosen is a price for an unspecified rule**, and the 22 `ECHO_BLOCKED`
passages are the standing reminder of what happens when a question-overlap
rule is defined loosely.

**Left unexplained:** the shipped verifier's first quintile is the only one
above zero and the gap to the second is 0.93 and 0.84, where the
passage-position gradient it would be calibrated to -- 62.5% falling to
27.6% -- is graded. The step is steeper than the thing it tracks, on both
heads.
