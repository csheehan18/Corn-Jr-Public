# Ninety-fifth finding — the gold is among the head's own ten on nine tenths of the residue, so the ninety-third finding's fifty-eight per cent ceiling was an artefact of conditioning on admission, and perfect window choice with a perfect pick from those ten reads eighty-three per cent

`scripts/probe_reader_rank.py` and `scripts/audit_refused_wrong.py`,
2026-09-03. **Replay only** — no GPU, no decode, no weight read, no tokenizer,
**and no new harvest** — over `nullpr_s{1,2}_popa.json` joined to
`pairs_built_s{1,2}_popa.json`. `evals/results/rank_s{1,2}.json` and
`evals/results/refused_wrong_audit.jsonl`.

**The pass that was going to be run already exists on disk.** The plan for this
session was one no-grad inference pass per seed to write the head's top ten
pairs per window. `pairs_built_s{1,2}_popa.json` has carried them since
2026-09-02 — `top_k = 10`, span text, score and token offsets, plus the extent
rule's `around` grid — for the same 1,003 passages and the same 3,893 windows.
The join is checked and not assumed: ids align, window counts align, and the
argmax span text matches on **3,893 of 3,893 windows on both seeds**. So the
whole of what follows is arithmetic, and no GPU was spent.

## 0. Two operating points, and the plan's residue shares belong to the one that does not ship

    SHIPPED  t = -2.02 (one constant) + extent rule d = 2.0 radius 3
    JOINT    the CV'd fold thresholds, extent off

`corn/reader.py` runs at SHIPPED. `probe_reader_species.py` — and therefore
`PLAN-READER-RESIDUE.md` §0's table, and every share quoted from it — was run
at JOINT. Reproduced here to the passage, including STATUS.md's runtime row
(389 right, 200 correct silences, **334 spans widened**) and the ninety-third
finding's baselines:

    seed 1                right  wrong silent | u.silent  joint   att  acc|att
    SHIPPED                389    188    144  |    200     589  0.800   0.674
    JOINT                  367    136    218  |    233     600  0.698   0.730
    seed 2
    SHIPPED                409    196    116  |    170     579  0.839   0.676
    JOINT                  368    157    196  |    207     575  0.728   0.701

    species            SHIPPED s1 / s2        JOINT s1 / s2   (the plan's)
    REFUSED_WRONG      93 28.0% / 83 26.6%    136 38.4% / 139 39.4%
    REFUSED_RIGHT      77 23.2% / 50 16.0%    113 31.9% /  91 25.8%
    AGGREGATION        66 19.9% / 60 19.2%     31  8.8% /  42 11.9%
    RIVAL              62 18.7% / 79 25.3%     42 11.9% /  47 13.3%
    CLIPPED            18  5.4% / 27  8.7%     22  6.2% /  23  6.5%
    UNGROUNDED         16  4.8% / 13  4.2%     10  2.8% /  11  3.1%
    residue               332    /   312          354    /    353

**The ordering is not the same at the two points and the plan's arms were
sized at the wrong one.** SHIPPED admits more, so refusals convert into
readings: `REFUSED_RIGHT` falls by a third and `AGGREGATION` **doubles**
(31 → 66 and 42 → 60), because admitting more windows gives agreement more
repetitions to count. `RIVAL` grows by half. Where the eighty-ninth finding
found the plan quoting a superseded *head*, this finds it quoting a superseded
*threshold*: the two corrections are independent and both apply.

## 1. The gold is in the head's ten on nine tenths of the residue

For every answerable failure, where the gold sits among the ten candidates the
head ranked **on that passage's best gold-bearing window**, admitted or not.
`score_extract_tight` on the rendered reply decides "is the gold", which is the
ninety-third finding's own test.

                      SHIPPED s1      SHIPPED s2      JOINT s1      JOINT s2
    RANK_1           128  38.6%       95  30.4%     140  39.5%    129  36.5%
    RANK_2_10        168  50.6%      182  58.3%     178  50.3%    189  53.5%
    OUTSIDE_TEN       36  10.8%       35  11.2%      36  10.2%     35   9.9%
    NO_GOLD_WINDOW     0   0.0%        0   0.0%       0   0.0%      0   0.0%
    reachable in ten 296  89.2%      277  88.8%     318  89.8%    318  90.1%

**Nine tenths.** And the plurality bucket is `RANK_2_10` on both seeds at both
points — the gold is present in the candidate list and is not first.

    by species, SHIPPED       RANK_1   RANK_2_10   OUTSIDE_TEN
      REFUSED_RIGHT           72 / 43     5 /  7       0 /  0
      AGGREGATION             55 / 51    11 /  9       0 /  0
      REFUSED_WRONG            1 /  0    74 / 70      18 / 13
      RIVAL                    0 /  1    49 / 63      13 / 15
      CLIPPED                  0 /  0    17 / 23       1 /  4
      UNGROUNDED               0 /  0    12 / 10       4 /  3

(The `OUTSIDE_TEN` column's seed-1 `CLIPPED` and `UNGROUNDED` cells read 4 and
3 when this was first written and are corrected here to 1 and 4, which is what
`rank_s1.json` holds. Two transcription errors; every other cell, every row
total and every share in this file is unchanged by them.)

`REFUSED_RIGHT`'s `RANK_1` is **by construction** — the species is defined by
the head's span on that window being the gold — and `AGGREGATION`'s nearly so.
The load-bearing rows are the other four, and they are `RANK_2_10`:
**152 of 332 and 166 of 312 of the residue are passages where the gold is a
candidate the head ranked second to tenth on a window it had.**

**This does not contradict the ninety-third finding's §2, and the difference
between them is the result.** That read said the gold is reachable in the ten
on 26.8% and 31.4% of the residue — but it conditioned on *admitted* windows.
This one conditions on the best gold-bearing window whether or not it was
admitted. Both are true, and the gap between 27% and 89% is the size of what
**admission** is hiding. The candidate list is not the bottleneck; getting the
window past the threshold is.

## 2. So the fifty-eight per cent ceiling was an artefact, and the real one is eighty-three

The ninety-third finding put `ORACLE_PICK` at 58.1%/59.0% and concluded that
"the entire *choose better among what he produced* family is capped twenty-six
points short" of 85%. `ORACLE_PICK` fixes the pick on admitted windows;
`ORACLE_WINDOW` fixes the window and leaves the pick. **Neither is the ceiling
on everything downstream of candidate ranking. Their conjunction is.**

    JOINT (finding 93's point)   seed 1              seed 2
      baseline                 367  50.9%          368  51.0%
      ORACLE_PICK              419  58.1%  +52     425  58.9%  +57
      ORACLE_WINDOW            460  63.8%  +93     442  61.3%  +74
      ORACLE_JOINT             597  82.8% +230     584  81.0% +216
      GUARD (ECHO_BLOCKED 22)  699  96.9%

    SHIPPED                      seed 1              seed 2
      baseline                 389  53.9%          409  56.7%
      ORACLE_PICK              449  62.3%  +60     493  68.4%  +84
      ORACLE_WINDOW            444  61.6%  +55     449  62.3%  +40
      ORACLE_JOINT             559  77.5% +170     573  79.5% +164

**This section's two claims are withdrawn where they were made, 2026-09-03,
and the ninety-sixth finding replaces them.** `ORACLE_JOINT` *adds* the best
gold-bearing window to the real mask and leaves every rival window in the vote,
so it is not "the ceiling on everything downstream of candidate ranking" —
admitting **only** that window reads 93.2% and 92.9% at SHIPPED, fourteen
points above its 77.5% and 79.5%. And 58% is not an artefact: it is a correctly
computed oracle over a different conditioning set, which is what §1's own
paragraph about 27% and 89% says and what this section's heading overstated.
The heading and the file name are left as they were written, because a finding
is a record of what was claimed and this note is the correction. Everything
below is unchanged and reproduces.

**`ORACLE_PICK` and `ORACLE_WINDOW` reproduce the ninety-third finding exactly
at its own operating point** — 419/460 and 425/442, to the passage — which is
what licenses reading `ORACLE_JOINT` off the same code.

**82.8% and 81.0%, against the owner's 85% = 613 of 721.** `ORACLE_JOINT` reads
597 and 584: **16 and 29 passages short of the target, not 194.** The two
oracles are strongly super-additive (+230 against +52 and +93) because each one
alone is blocked by the other's failure — fixing the pick on a window that was
never admitted buys nothing, and admitting the right window buys nothing if the
head then speaks its rival.

**The caveat the ninety-third finding wrote for `ORACLE_WINDOW` applies here
unchanged and is not smaller for being repeated.** An unanswerable passage has
no gold-bearing window, so the force fires on the answerable half only and the
correct-silence column is unchanged **by construction, not by merit**; a real
window scorer would lift the attempt rate on both halves. `ORACLE_JOINT` runs
at attempt rate 0.972 and 0.969. It is a ceiling and it is not a forecast.

## 3. The outranking signal survives its control

The ninety-third finding's §5 — a no-gold window outranks every gold-bearing
one on 2.8% of passages he gets right against 47.8% of the residue — is
near-tautological as stated, because a passage he gets right usually got there
*through* an admitted gold-bearing window. The control is `tight_on`: whether
the head's span on the best gold window is the gold at all, which is a property
of the reading and not of the outcome. At SHIPPED, over the 580 answerable
passages carrying both kinds of window:

                              seed 1                seed 2
    all                   148 of 580  25.5%     129 of 580  22.2%
    he got it right        10 of 300   3.3%      18 of 313   5.8%
    residue               138 of 280  49.3%     111 of 267  41.6%

    P(outrank | tight)     72 of 412  17.5%      57 of 398  14.3%
    P(outrank | not tight) 76 of 168  45.2%      72 of 182  39.6%

    tight & right          10 of 294   3.4%      18 of 306   5.9%
    tight & residue        62 of 118  52.5%      39 of  92  42.4%
    not tight & right       0 of   6   0.0%       0 of   7   0.0%
    not tight & residue    76 of 162  46.9%      72 of 175  41.1%
    Fisher, right vs residue *within tight*   p = 5.9e-30 / 1.4e-15

**It does not collapse.** Within the tight set — where reading the window is
not the problem — the split is 3.4% against 52.5% and 5.9% against 42.4%, as
large as the uncontrolled contrast and significant on both seeds.

**Two things the control does show that the original read could not.** First,
outranking and misreading **co-occur**: 45.2% against 17.5% and 39.6% against
14.3%, so cross-window ranking failure and within-window reading failure are
correlated and are not two independent budgets to be added. Second, the
residual structural link is still there and is named rather than waved at — a
`right` verdict does not strictly require the gold window to outrank every
empty one (under `agree` several windows vote), which is why the cell is 3.4%
and not 0%, but it comes close, and **the honest unconditional number remains
25.5% and 22.2%.**

## 4. There is no memorised answer prior

For every `RIVAL` and every `REFUSED_WRONG`/`wrong_span` passage, how often the
span he spoke is a short answer in `data/raw/spans_nq.jsonl` — 82,932 training
questions of which 58,509 carry a short answer, **zero id overlap with
Population A**, checked — against how often the gold is.

                   rival more  gold more  tie   share of decided        p
    seed 1  RIVAL      20         17       25     54.1% of 37        0.743
            REF_WRONG  15         13       31     53.6% of 28        0.851
            all        35         30       56     53.8% of 65        0.62
    seed 2  RIVAL      20         31       28     39.2% of 51        0.161
            REF_WRONG  20          7       29     74.1% of 27        0.0192
            all        40         38       57     51.3% of 78        0.91

**53.8% and 51.3% against a null of 50%, p = 0.62 and 0.91. The head does not
speak the commoner training answer.** A `RIVAL` is not a memorised frequent
answer displacing a rare gold.

**Seed 2's `REFUSED_WRONG` cell reads 74.1% at p = 0.019 and is not a result.**
Seed 1's same cell reads 53.6% at p = 0.85, and the two seeds' `RIVAL` cells
disagree in sign (54.1% against 39.2%). One cell of six clearing 0.05 on one
seed with the other seed flat is what noise looks like at n = 27, and the house
rule against single-seed numbers is why it is printed rather than claimed. The
tie column is large because most golds are not training answers at all.

## 5. The anchor is not an extraction prior, and the bar was pre-registered

The ninety-fourth finding put the hand lexicon on the *admission* decision.
This puts it inside the window: on `RIVAL` and `REFUSED_WRONG` windows,
restrict the head's ten to spans following an anchor and take the restricted
argmax. **Pre-registered before the run: worth building only if it recovers
>= 25% of those windows on both seeds.** The gap counting as "follows" was
fixed at 12 characters in advance; 4 and 24 are printed as a sensitivity.

                     seed 1 (137 windows)      seed 2 (158 windows)
    gap  4     fires 13  9.5%  gold 2 1.5%   fires 16 10.1%  gold 5 3.2%
    gap 12     fires 14 10.2%  gold 3 2.2%   fires 19 12.0%  gold 6 3.8%
    gap 24     fires 15 10.9%  gold 4 2.9%   fires 20 12.7%  gold 6 3.8%

**2.2% and 3.8% against a bar of 25%. Missed by an order of magnitude, at
every gap.** The failure is the ninety-fourth finding's, in the same shape and
worse: the lexicon fires on one window in ten here against one passage in three
there, because a window is a smaller target than a passage. Where it does fire
it is right 21% and 32% of the time, which is again respectable and again
irrelevant at that coverage. **The frame is an admission signal, not an
extraction prior**, and §2 says admission is where the passages are anyway.

## 6. The label-noise floor under 85% is about a quarter, and this is a model audit

100 `REFUSED_WRONG` passages, `random.Random(0)` over the seed-1 harvest's JOINT
set (136 passages; SHIPPED holds 93, too few to draw 100 from), each labelled
by reading the question, the gold and the passage:

    UNIQUE      the gold is the answer and no other span is      77   77%
    EQUIVALENT  the gold is right and so is another span         15   15%
    EXTENT      right referent, arguable boundary                 6    6%
    WRONG       not the answer the passage gives                  2    2%

    the gold is not the unique correct span on 23 of 100

**`EQUIVALENT` is the bulk of it and it is one shape.** The question asks for a
set and NQ's annotator gave one member: three meninges and the gold is
`dura mater`; four commonwealth states and the gold is `Kentucky`; five Warriors
championship years and the gold is `1947`; four layers of the Earth "in order"
and the gold is the crust. A reader naming a different correct member is scored
wrong. The two `WRONG` cases are cleaner: the Charles Bridge passage says it was
built as a *bow* bridge and the gold `Stone` is lifted out of "the Stone Bridge
in Regensburg", a different bridge; the possibilism passage says Sahlins *used*
the concept and credits the theory to Strabo.

**This is a model audit and not a human one.** The labels were assigned by
Claude reading question, gold and passage, blind to what the head said on that
passage. That removes the obvious circularity and does not remove the
model-judgement one, and the boundary between `EXTENT` and `UNIQUE` in
particular is a judgement call made about twenty times. **The owner should
spot-check 20 before this number is quoted as a data fact**;
`audit_refused_wrong.py --check 20` prints a seeded sub-sample for it.

**Spot-checked 2026-09-04** (`docs/SPOT-CHECK-REFUSED-WRONG.md`). A second
model rater agreed with the labels above on 17 of the 20, disagreeing only
toward *less* unique (one `EQUIVALENT` → `WRONG`, two `UNIQUE` → `EXTENT`).
The owner then ruled on the five disputed or non-unique rows: agreed on one,
overturned four, and **every overturn moved the gold toward less unique or
wrong** — 169 is `WRONG` where the question asked for countries and the
passage says 216; the FBI Director's pre-2004 superior is `WRONG` on a
present-tense question; two `when` golds that add a season or a range are
`EXTENT` because "a year is enough". So the model audit was not generous to
the reader, and **23 of 100 is a floor.** The fifteen agreed `UNIQUE` rows
were not individually ruled on. Three rules from the rulings — recency on
present-tense questions, a year answers `when`, a different quantity is
wrong — are the lenient ruler's principles from here.

**And it is a floor on one species, not on Population A.** 23% of
`REFUSED_WRONG` is 23% of 28% of the residue. It does not license subtracting
23% from anything, and the correct use of it is that **a 100% reader does not
score 100%, and nobody had measured by how much.** The 22 `ECHO_BLOCKED`
passages (699/721 = 96.9%) are the other known deduction and are disjoint from
this one in kind.

## What this cannot say

**It cannot separate rank 11 from a gold the pair enumeration never contained.**
Both read as `OUTSIDE_TEN`, because separating them needs the tokenizer and this
file loads none. It does not change §1's plurality, which is what the arm gate
turned on, but "10.8% is rank > 10" is not a claim this file makes — the claim
is "10.8% is not in the ten".

**Every oracle in §2 is handed the answer.** The ninetieth finding's locality
rule had a plausible mechanism and reached a *negative* fraction of its bound.
83% is what perfect information buys, and the last four findings are a record of
real mechanisms reaching small fractions of such numbers.

**§3's control reduces the outcome-conditioning and does not eliminate it**, as
§3 says in its own last paragraph.

**§6 is one species, one seed's harvest, one operating point and one model
auditor.**

**Two seeds, one trunk, one population**, Population A under `hybrid`, at both
operating points, with each read's point stated.

## What follows

**The pre-registered gate on the two training arms did not fire, and they should
not be written.** The session's plan said to write Arm B1 (a bidirectional
encoder between the cached states and the pair scorer) and Arm B2 (listwise
passage-level training for the verifier) **only if `rank > 10` were the
plurality of the residue on both seeds**. It is 10.8% and 11.2%, and the
plurality is `RANK_2_10`. More than that, **B1's stated rationale is
contradicted by §1**: it was justified by the trunk being causal, so no start
state sees its span or right context, which would put the gold *outside* the
enumeration. The gold is inside the enumeration nine times in ten. Building a
richer state to fix candidate generation would be aimed at 11% of the residue.

**What §1 and §2 name instead is admission, and it is the same lever the
ninety-third and ninety-fourth findings converged on from the other side.** The
gold is in the ten and the window is refused, or admitted and outranked. That is
`ORACLE_JOINT`'s +230 and it is where the ninety-fourth finding said a generated
frame belongs.

**Re-size the plan's arms at SHIPPED before running any of them.**
`PLAN-READER-RESIDUE.md`'s four arms are sized off the JOINT table, where
`AGGREGATION` is 31 and not 66 and `REFUSED_RIGHT` is 113 and not 77. A2 — the
score-aware reduce, aimed at `AGGREGATION` — is the arm whose target *doubles*
at the operating point that ships, and it is the one arm in the plan that costs
no GPU.

**Left unexplained:** `AGGREGATION` is 55 and 51 `RANK_1` at SHIPPED — passages
where the head ranked the gold first on a window it admitted, and `reduce`
returned something else. That is a larger `RANK_1` population than the plan's
whole `AGGREGATION` species at JOINT, and no read here says whether the
outvoting window is a repetition of one rival or several different ones.
