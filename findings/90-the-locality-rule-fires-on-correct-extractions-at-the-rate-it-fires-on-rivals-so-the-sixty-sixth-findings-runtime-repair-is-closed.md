# Ninetieth finding — the locality rule cannot tell a rival from a gold inside one window, so the sixty-sixth finding's runtime repair is closed and the eighty-ninth's revival of it was one inference too far

`scripts/probe_locality.py`, 2026-09-03. **Replay only** — no GPU, no decode,
no weight read, no tokenizer — over `evals/results/nullpr_s{1,2}_popa.json`,
the shipped pair-rows verifier. `docs/NEXT-AFTER-89.md` item 2. The baselines
reproduce the eighty-ninth finding to the passage: **367 right / joint 600**
and **368 right / joint 575**, `RIVAL` 42 passages / 49 admitted windows and
47 / 62.

**Forty-two arms — three readings of the rule, seven tolerances, two seeds —
and not one of them is a gain on any column.** The best `joint` in the whole
grid is **−33 and −29**. The owner's precision-only trade does not arise,
because the arm does not buy precision either.

## What was being priced, and why it looked live

The sixty-sixth finding named a runtime repair — "reject an extraction whose
span is not local to the question's distinguishing term" — and never defined
the distinguishing term. The eighty-ninth finding revived it: on the shipped
verifier `RIVAL`'s spoken span is the earlier one **74.5% of the time against
a measured positional-indifference null of 52–53%, +22 points, pooled
p = 2.5e-07**, where the superseded head had given +12 and the arm had been
set aside. That is a real and replicated fact and it is not the fact an arm
needs; §3 below is why.

## The three readings, all of them runtime-computable, none of them the gold

Positions are content-word indices, `corn.extract.content_words` — the space
`span_of` and `longest_span` already work in. `Q` the question's content words,
`S` the spoken span's, `W` the window's.

    absent_span   D = (Q - S - FRAME) & W. The eighty-ninth finding §4's first
                  reading and the cheapest: `grounded` already computes `Q`.
    unique        `absent_span`, keeping only terms occurring ONCE in the
                  window. The finding's own "once `iron` is discounted as
                  shared", made computable without the gold, and the only
                  reading that reproduces the sixty-sixth finding's example.
    all_words     D = Q & W. The control §4 predicts is degenerate.

The rule is a **mask edit and nothing else**: `admitted` says which windows
clear the margin, this silences some of them, and `replies_for`,
`corn.extract.reduce` and `score_extract_tight` are the runtime's, untouched.
A silenced window has the runtime author its decline exactly as an unadmitted
one does. **When `D` is empty the rule does not fire** — no evidence to reject
on is not a reason to reject.

**The head-noun reading is unpriced rather than approximated.** It needs a
part-of-speech decision, there is no tagger in the repo, no dependency may be
added, and every dependency-free heuristic tried picks the wrong word on the
sixty-sixth finding's own example: first content word gives `boiling`, last
gives `iron`, the token before `of` gives `point`.

## 1. The rule fires on the answers it must protect at the rate it fires on rivals

This is the read that decides it, and it is one number. A rejection rule is a
lever only if it fires more on what it should silence than on what it must not.
`CORRECT` is every admitted window on an answerable passage whose own span
scores `tight` — 540 and 550 of them.

    ratio of fire rates, RIVAL over CORRECT       seed 1          seed 2
    absent_span   k = 3                        1.17            1.05
                  k = 5                        1.13            1.21
                  k = 8                        0.98            0.99
    unique        k = 3                        1.18            1.03
                  k = 5                        1.07            1.11
                  k = 8                        1.04            1.07
    all_words     every k                      ≤ 0.99          ≤ 0.99

**Nothing in the grid separates the two populations, and the two seeds do not
even agree on which cell comes closest.** `unique` k=3 reads 1.18 on seed 1
and 1.03 on seed 2; `absent_span` k=5 reads 1.13 and 1.21 but 1.17 and 1.05
one tolerance down. A ratio of 1.2 against a base rate of 52–59% is not a
usable trade: silencing 30 of 49 rival windows costs **279 of 540** correct
ones on seed 1, and 34 of 62 costs 288 of 550 on seed 2.

**`all_words` is worse than indiscriminate — it is anti-discriminative.** Its
ratio is *below* 1 at every tolerance on both seeds, falling to 0.31 and 0.47
at k=8: it preferentially silences the right answers. The eighty-ninth finding
predicted this reading would be degenerate on long questions. It is, and the
degeneracy has a sign.

## 2. The price, at each fold's own cross-validated threshold

Every row is the shipped `hybrid` reduce at the CV'd `t`, `acc | att` and the
attempt rate printed beside precision because the owner's condition for a
precision-only arm is that they are.

    seed 1              right  wrong  silent   joint   prec   acc|att  attempt
    baseline              367    136     218     600   66.5%   0.730    69.8%
    absent_span  k = 3    185     90     446     438   60.9%   0.673    38.1%
    absent_span  k = 8    283    123     315     523   63.2%   0.697    56.3%
    absent_span  k = 12   318    134     269     556   64.1%   0.704    62.7%
    unique       k = 8    269    120     332     515   63.3%   0.692    54.0%
    unique       k = 12   304    131     286     548   64.3%   0.699    60.3%
    all_words    k = 12   334    136     251     567   64.4%   0.711    65.2%

    seed 2              right  wrong  silent   joint   prec   acc|att  attempt
    baseline              368    157     196     575   61.3%   0.701    72.8%
    absent_span  k = 3    182    101     438     424   56.3%   0.643    39.3%
    absent_span  k = 8    286    141     294     508   58.7%   0.670    59.2%
    absent_span  k = 12   324    152     245     539   59.7%   0.681    66.0%
    unique       k = 8    273    133     315     500   59.2%   0.672    56.3%
    unique       k = 12   308    145     268     529   59.9%   0.680    62.8%
    all_words    k = 12   337    153     231     546   59.9%   0.688    68.0%

**Right, joint and `acc | att` fall on all 42 arms, and precision falls on 41
of them.** The best `joint` in the grid is −33 and −29 and it belongs to
`all_words` at the loosest tolerance measured — that is, to the setting closest
to not applying the rule at all. Every column is monotone in the tolerance:
this is the shape of a loss, not of a trade with an optimum somewhere inside
it.

**One cell beats a baseline precision anywhere and it does not survive
contact.** `all_words` k=0 on seed 1 reads 66.7% against 66.5% — **+0.2 points
bought with 335 of 367 right answers, 32 right at an attempt rate of 6.2%** —
and the same cell on seed 2 reads 60.4% against a 61.3% baseline, at the
identical 32 right. It is the arm silencing almost everything, and what
survives is not more accurate: `acc | att` reads 0.711 on both seeds against
0.730 and 0.701.

## 3. Why the eighty-ninth finding's +22 points did not carry, and it is not a contradiction

Both statements are true and they are about different objects:

  * **Across windows.** `RIVAL`'s spoken span sits earlier than the gold 74.5%
    of the time against a 52–53% null. That compares `RIVAL` windows to a
    positional-indifference process and to `REFUSED_WRONG`, and it is what
    forbids one bar reading both species.
  * **Inside one window.** A rejection rule has to say *this span* rather than
    *that span*, on evidence available before the gold is known. Position
    relative to a question term is that evidence, and §1 measures it at a
    ratio of 1.0–1.2.

**A population-level tilt of twenty-two points is compatible with almost no
per-window separation**, and that is what happened: the gold sits early too —
the eighty-ninth finding §3 measures golds at mean relative position 0.394 and
62.5% of first-quartile windows carrying the gold. Both the rival and the gold
are near the front, so "is the span near a question word" hits both. The
eighty-ninth finding's revival of this arm inferred a per-window discriminator
from a cross-window statistic, and that inference is what this finding refutes.

The ceiling that was known before the run also holds: **13 of 49 and 16 of 62
`RIVAL` windows put the spoken span at or after the gold**, where locality
cannot tell the two apart in principle.

## What this cannot say

**It is not a test of the rule the sixty-sixth finding imagined.**
`content_words` does no stemming, so on that finding's own fixture — "the
boiling point of iron" over "...melts at 1538 °C and boils at 2862 °C" —
`boiling` is not `boils` and the distinguishing term is absent from `W` under
every reading built here. `absent_span` gives `D = {point, iron}` and `unique`
gives `D = {point}`. A stemmer is a new dependency and a hand-written suffix
table is a scorer-shaped object needing its own guard, so what is priced is
**the rule this repo can build today**. A stemmed version could read
differently and nothing here forecloses it; what §1 forecloses is the
unstemmed family, and §3 gives a reason to expect a stemmed one to fail the
same way.

**Two seeds, one trunk, one population.** Everything is Population A at the
shipped `hybrid` reduce and the CV'd threshold. The tolerance grid is
0,1,2,3,5,8,12 content words and a finer grid would not change a monotone
column.

**It says nothing about the corpus arm.** The sixty-sixth finding named two
repairs and called them not-alternatives: the runtime rejection priced here,
and paired-property windows where the gold is the *second* value often enough
that "take the first" scores badly. Only the first is closed.

## What follows

**Close item 2 and do not spend GPU on A4's locality half.** The eighty-ninth
finding left this arm "live for those 42/47 once its distinguishing term is
defined". It is defined three ways here and priced, and it is dead.

**`RIVAL` has no cheap lever now.** 42 and 47 passages, positional across
windows and not separable within one, and the re-ranker was already retired by
the eighty-sixth finding for being unable to choose better than the span head's
own argmax. What is left for it is A4's trunk arm, restated — which is handoff
item 3 and is now the only thing item 2 could have replaced.

**The ceiling does not move and that is the point.** The locality rule was
never in `PLAN-READER-RESIDUE.md` §2's arithmetic — it was the *cheap* route to
A4's target, a no-GPU rejection that could have bought some of `RIVAL` without
touching the trunk. Closing it leaves the 65.5%/65.3% ceiling where the
shipped-head re-run put it and removes the only way of approaching it that
cost nothing. **`REFUSED_WRONG` at 136/139 is still the plurality and still has
nothing aimed at it** — handoff item 4, and now the only item whose value has
gone up.

**Left unexplained:** `absent_span` and `unique` cross a ratio of 1.0 from
above at k=8 on both seeds and fall below it by k=12, while `all_words` is
below 1 everywhere. Something about mid-range tolerances is weakly
right-signed on both seeds and it is not strong enough to use; whether it is
the same thing on both is unmeasured.
