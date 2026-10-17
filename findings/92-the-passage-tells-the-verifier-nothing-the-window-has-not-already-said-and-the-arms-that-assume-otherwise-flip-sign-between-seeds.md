# Ninety-second finding — the passage tells the verifier nothing the window has not already said, cross-window agreement is at chance, and the six arms that assume otherwise flip sign between seeds inside the threshold's own fold noise

`scripts/probe_passage_features.py`, 2026-09-03. **Replay only** — no GPU, no
decode, no weight read, no head retrained — over
`evals/results/nullpr_s{1,2}_popa.json` at each fold's own cross-validated
threshold under `hybrid`. Baselines 367 right / joint 600 and 368 / 575.

The shipped reader decides one window at a time: score it, take `best - null`,
compare to **a constant**. `reduce` then votes among whatever cleared it. So
every cross-window fact — that this margin is the best of eight or the worst of
two, that three windows agree on the span and two do not — reaches the decision
**only after** the threshold has thrown windows away. Seventy per cent of the
residue is that one binary decision (`REFUSED_RIGHT` 113/91 plus
`REFUSED_WRONG` 136/139 of 354/353), and four findings have gone into choosing
the constant while none has asked whether the scalar is the right scalar.

**It is. The passage has nothing to add.**

## 1. The information is not there — read (a)

Two targets, a cross-fitted logistic, AUC against the single-feature baseline
`max_p`. A logistic on one feature is a threshold on it, so the baseline AUC
**is** the shipped decision's own separability stated per passage.

    delta AUC over `max_p` alone        seed 1      seed 2      bar
    SPEAK   (the passage is answerable) -0.0012     -0.0061    +0.02
    HAS_IT  (gold at the argmax window) +0.0097     +0.0025    +0.02

Eight passage-level features — window count, mean, spread, top-two gap, three
agreement measures — and on the target a speak/stay-silent decision is actually
predicting, they make it **worse** on both seeds.

**The feature the idea rested on is at chance.** `agree_top`, how many windows
produced the same span — the signal `reduce` already uses downstream, moved
upstream of the threshold — reads:

    agree_top   AUC 0.4937 / 0.4863 (seed 1)   0.4815 / 0.4906 (seed 2)
    agree_frac      0.5093 / 0.5416                0.4777 / 0.5365
    distinct        0.5356 / 0.5238                0.5278 / 0.5013
    n_win           0.4819 / 0.5498                0.4819 / 0.5534

Below 0.5 in three of four cells for `agree_top`. Agreement does not predict
whether the passage is answerable, and it does not predict whether the head has
the answer.

## 2. And not where it would decide something — read (a2)

A whole-population AUC dilutes: most passages are not close calls. So (a2)
restricts to passages the reader was **silent** on and separates the ones he
should have spoken on — answerable, gold at the top of some window — from the
ones he correctly refused. That is `REFUSED_RIGHT` against correct silence,
which is the exact trade a better presence decision would move.

    seed 1: 76 should have spoken, 233 correctly silent
    seed 2: 68 should have spoken, 207 correctly silent

    max          0.7212 / 0.7764     <- the margin, already in the runtime
    mean         0.6763 / 0.7352     <- a monotone shadow of the same thing
    sd           0.5176 / 0.4599
    agree_frac   0.5283 / 0.5026
    agree_top    0.5124 / 0.5029
    distinct     0.4885 / 0.4293
    gap12        0.4831 / 0.4576
    n_win        0.4792 / 0.4875

**Every feature that is about the passage's shape rather than its margin sits
inside 0.43–0.53.** The margin separates at 0.72 and 0.78 on exactly the
population where the residue lives.

## 3. Six arms, twelve measurements, no arm positive twice

Read (e) holds `t` at the baseline's own cross-validated value and changes
nothing else, so what it reports is the rule and only the rule, paired passage
by passage. (Read (b) re-fits `t` under each rule, which is correct but mixes
the rule with a different operating point.)

    rule                    seed 1              seed 2            sign
    gap 0.5             -2  p = 0.75        +7  p = 0.12         flips
    gap 1.0             -1  p = 1           +5  p = 0.18         flips
    gap 2.0             -1  p = 1           +2  p = 0.63         flips
    boost 0.5           -7  p = 0.32        +4  p = 0.64         flips
    boost 1.0          -20  p = 0.031      -12  p = 0.22         both -
    gap 1.0 + boost 1.0 -5  p = 0.61        -4  p = 0.71         both -

**The only two rules that agree with themselves across seeds are the two that
lose**, and the only cell reaching p = 0.1 is a loss. `GAP` on seed 2 looks
like a real precision gain — 375 right against 368, precision 61.3% → 62.8%,
`acc | att` 0.701 → 0.718, attempt rate flat at 72.4% — and on seed 1 the same
rule is −2.

**Read (c) supplies the scale that makes that unremarkable, and it takes the
scale from the baseline rather than from an arm.** At its own silence cost the
*baseline* sits **+1 above** the plain rule's trade curve on seed 1 and **−7
below** it on seed 2. That spread is the cross-validated threshold choice
wandering between folds; it is ±7 wide; and every arm effect above fits inside
it. Read (d) flips the same way — best joint anywhere on the curve is plain 600
against `gap 0.5`'s 598 on seed 1, and plain 588 against 593 on seed 2.

`GAP` is also narrower than it sounds: it can never silence a passage entirely,
because the argmax window always satisfies `m_i >= max_p - g`. At the seed-1
threshold it removes a window on 75 of 1,003 passages and changes the verdict
on about seven.

## What this cannot say

**It does not test a retrained verifier.** These are mask rules over a head
that was trained without passage features. A head *trained* on them could in
principle find structure a hand-written rule and a nine-feature logistic
cannot. What §1 and §2 establish is that the features carry almost no
univariate or linear signal about the two targets a presence head is trained
against — which is the cheap evidence that would have justified the GPU, and it
does not.

**One trunk, two seeds, one population**, Population A at the CV'd threshold
under `hybrid`. The `g` and `b` grids are declared, not fitted, and every value
is printed.

**The lexicon of features is not exhaustive.** Nine were chosen because they
are free from the harvest. A feature requiring a second forward pass — the
question re-encoded against the whole passage, say — is not tested and is not
free.

## Two things worth keeping that are not the result

**The trade curve is an arch, not a slope.** Sweeping `t` on seed 1: 364 right
at 13 correct silences, rising to **417 at 114**, back to 366 at 234. Admitting
more windows makes `reduce` disagree more, so over most of the range speaking
*less* buys right answers. An intermediate version of read (c) interpolated
between bracketing grid points — which averages across the arch and means
nothing — and reported a spurious +43. The committed form is a dominance test:
the most right the plain rule reaches while conceding at least as much silence,
which is generous to the plain rule and so conservative for a claim that an arm
is worth having.

**The `null` column is dead and has been all along.** `s_max` and `max`
returned identical AUCs to four decimals because `null` is **identically zero
across all 3,893 windows in both `nullpr_*` and `null_*`** — one distinct value
— so `load_reader_harvest`'s `best - null` has been returning `best`. Nothing
downstream is wrong and no number moves, but a documented per-window field
carries no information and every "margin" in this workstream is the raw score
under another name.

## What follows

**Do not retrain the verifier with passage features.** That was the arm this
probe existed to price and §1 is the reason not to spend the GPU.

**The cheap side of the reader is now closed.** Three ideas were live at the
start of the day and all three are measured and dead: the sixty-sixth finding's
locality rejection (ninetieth), a corpus arm teaching question-constraint
discrimination (ninety-first, which found the constraint classes are the ones
he is *best* at), and passage-level verification (here). None cost GPU and none
bought a passage.

**What is left that is not the trunk is one decode pass.** No one has measured
`right(head) ∪ right(generate)` on Population A. The eighty-seventh finding
checked fourteen questions live and saw no disagreement, which settles nothing;
`corn/evals.py` never builds a `Reader` at all, so no card can see it. If the
two arms fail on different passages a router beats both and it is nearly free;
if they fail on the same ones, that is itself the strongest statement yet that
the limit is the representation.

**Otherwise `PLAN-EXTRACTION-READER.md` §7's trunk levers are the only route
named to the rest**, and after three negative results in one day the honest
question for the owner is whether 85% is a requirement or an aspiration — the
measured ceiling of the current architecture is 65.5%/65.3%, and that number
was computed before any of today's three arms failed.

**Left unexplained, and stated here with the whole trade rather than half of
it.** The arch's peak replicates across seeds:

    seed 1   417 right at 114 correct silences   (CV point 366 at 232)
    seed 2   415 right at 119 correct silences   (CV point 339 at 233)

**The first draft of this section quoted that `right` column and the silence
cost and stopped there, which is the error this repo's own reporting rule
exists to prevent.** Here is the rest of it, seed 1:

    t         right  a-wrong  a-silent | u-silent  u-WRONG | wrong  prec
    -1.420      366      138       217 |      232       50 |   188  66.1%
    -2.022      381      196       144 |      200       82 |   278  57.8%
    -2.713      408      225        88 |      150      132 |   357  53.3%
    -3.375      417      253        51 |      114      168 |   421  49.8%

Moving from the shipped floor of 200 correct silences to the arch's peak buys
**+36 right answers and costs +143 wrong ones** -- 82 to 168 confident false
claims on passages that do not contain the answer, and 196 to 253 wrong answers
on passages that do. Precision falls 57.8% to 49.8%: **at the peak he is wrong
more often than he is right.** Seed 2 agrees, 50.1% at its own peak.

So the honest statement is not that the floor stands between the reader and its
best rate. It is that **`joint` cannot referee this at all**, because it scores
a right answer and a correct silence as equal and a wrong answer as zero rather
than as a cost -- and every threshold protocol in the record optimises `joint`.
The floor is doing the work the metric will not do. Whether 200 is the right
floor is an owner question; whether it should be decided by `joint` is not.

**And the threshold's own ceiling is worth quoting against the target.** The
best `right` any threshold reaches on this head is **417 and 415 of 721 --
57.8% and 57.6%** -- against an owner target of 85%. Roughly twenty-seven
points of that gap cannot be bought at any operating point and have to come
from reading.
