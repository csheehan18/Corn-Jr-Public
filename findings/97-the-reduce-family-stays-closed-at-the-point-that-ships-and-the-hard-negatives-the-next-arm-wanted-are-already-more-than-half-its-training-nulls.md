# Fallback answer rules still don't help at the shipped setting

**Full result:** The reduce family stays closed at the operating point that ships even though its target doubled there, the two seeds only agree when each is read at its own threshold, and the hard negatives the next arm was to add are already more than half the verifier's training nulls

`scripts/probe_reduce_shipped.py` and a count over the two state caches,
2026-09-03. **Replay only for §1 to §3** — no GPU, no decode, no weight read —
over `nullpr_s{1,2}_popa.json` joined to `pairs_built_s{1,2}_popa.json`.
`evals/results/reduce_shipped_s{1,2}.json`. §4 opens the harvested state caches
and reads their metadata only; no state row is scored and nothing is trained.

## 0. The bar protocol is now in a committed script, and it reproduces

`corn/reader.py`'s threshold is -2.02, "the mean of the two cross-validated
fold values under the bar protocol: the `t` that maximises `right` on the
training fold among those holding that fold's share of 200 correct silences".
**That sweep existed nowhere in the repo** —
`probe_reader_passages.cross_validate` implements the `joint` protocol only,
and the rule that chose the shipped constant lived in the session that settled
it. `bar_sweep` here is it, and the reproduction is the check that it is the
same rule:

    this file's fold thresholds   -1.9796 / -2.0608   mean -2.0202
    corn/reader.py records        -1.9800 / -2.0610   mean -2.02

At that point it reads **389 right of 721 at 199 correct silences on seed 1**
and **388 at 196 on seed 2**, which is finding 86's own pair of numbers.

## 1. The two seeds agree at their own operating point and disagree at a shared constant

The ninety-fifth and ninety-sixth findings read SHIPPED as *the single constant
-2.02*, and that constant is **seed 1's** cross-validated mean. Applying it to
seed 2's harvest is seed 1's threshold on another seed's scores:

    species          each seed's own bar CV      the constant -2.02 on both
                       s1        s2                 s1        s2
    REFUSED_WRONG      93        110                93        83
    REFUSED_RIGHT      78         80                77        50
    AGGREGATION        64         50                66        60
    RIVAL              63         59                62        79
    CLIPPED            18         23                18        27
    UNGROUNDED         16         11                16        13
    residue           332        333               332       312
    right / u.silent  389/199   388/196           389/200   409/170

**Under its own protocol the seed-2 table is seed 1's table.** `REFUSED_RIGHT`
78 against 80 rather than 77 against 50; `RIVAL` 63 against 59 rather than 62
against 79; the residue 332 against 333 rather than 332 against 312.
`REFUSED_WRONG` is the largest species on both seeds either way, and it is
larger on seed 2 (110) than anything the shared constant showed.

**And seed 2 at -2.02 is not an operating point this project would ship**: 409
right at **170** correct silences, thirty below the floor `PLAN-EXTRACTION-
READER.md` PRIMARY names and the bar protocol exists to hold. Sizing an arm
from that row sizes it against a willingness setting nobody chose. This is the
same defect the eighty-ninth finding found (a superseded head) and the
ninety-fifth found (a superseded threshold) in a third form: **a threshold that
is right for one seed quoted on another**. Every arm in
`PLAN-READER-RESIDUE.md` §7 is sized on the left-hand table.

## 2. A2 stays closed at SHIPPED, where its target had doubled

The ninety-fifth finding named A2 — the score-aware `reduce` — as the one arm
whose target *doubles* at the point that ships (`AGGREGATION` 31 → 66 and
42 → 60) and the one arm that costs no GPU, and said to re-run it there. The
eighty-fifth finding's six variants, rebuilt because its own script was never
committed, each at its own cross-validated `t` under the bar protocol with the
extent rule at `d = 2.0`, paired against the same-protocol `hybrid`:

    variant       s1 right / u.sil   vs hybrid           s2 right / u.sil   vs hybrid
    hybrid           389 / 199       (ships)                388 / 196       (ships)
    span             395 / 199        +6 (21/27, p .47)     382 / 197        -5 (27/22, p .57)
    hybrid_span      386 / 199        -3 (15/12, p .70)     387 / 196        -1 (13/12, p 1)
    hybrid_lp        378 / 199       -11 (19/8,  p .05)     377 / 198        -9 (18/9,  p .12)
    dedupe           398 / 199        +9 (9/18,  p .12)     393 / 196        +5 (10/15, p .42)
    dedupe_span      396 / 199        +7 (21/28, p .39)     387 / 196        -1 (22/21, p 1)

    AGGREGATION      hybrid 64 / 50  ->  span 58 / 54, dedupe 55 / 45, hybrid_lp 74 / 61

**Every variant misses every pre-registered bar on both seeds.** `AGGREGATION`
falls by 14% and 10% at its best against a bar of half. `right >= 400` is
missed by all five on both seeds. Seed 2's silence floor of 199 is missed by
its own baseline at 196, **which was written down before the run** because a
bar the baseline fails is a statement about the seed.

**`dedupe` is the only variant positive on both seeds — +9 and +5 — and it is
not significant, p = 0.12 and 0.42.** It is reported as the pre-registered
failing branch said it would be: a consistently-signed correctness fix, not an
arm, not banked. Its sign is at least mechanically coherent, and larger here
than the +1 / +2 the eighty-fifth finding read at JOINT, because a duplicated
span is more of a problem where more windows are admitted.

**The eighty-fifth finding's mechanism sentence survives the change of
operating point**, which is why this was worth running rather than assuming: *a
pair logit is not comparable across windows and the null logit, which was
trained across windows, is*. `hybrid_lp` — the one ranking quantity in the
family that is comparable across windows on its face, the argmax pair's
within-window log-probability — is the **worst** variant at both points and on
all four cells. **The doubling of `AGGREGATION` at SHIPPED is a fact about
admission and not about ranking.**

## 3. The reproduction check ran first and four of five variants reproduce

At JOINT with the extent rule off, against the eighty-fifth finding's own
table, which is what licenses reading §2 off the same code:

    variant        this file      finding 85
    span           -3             -4
    hybrid_span    -8             -5
    hybrid_lp     -16            -15
    dedupe_span    -3             -3
    dedupe         -7             +1

Four are inside the ±7 fold wander the ninety-second finding measured as the
threshold's own noise. **`dedupe` does not reproduce.** Its definition here is
one vote per distinct span *text*: the harvest carries token offsets inside a
window and not character offsets in the passage, so one occurrence seen twice
cannot be told from two occurrences without a tokenizer this file does not
load. It moves 178 vote masks at a comparable threshold against the
eighty-fifth finding's 155. **So `dedupe` here is a restated variant under a
stated definition and is not that finding's `dedupe`**, and its +9 / +5 is
quoted as this file's number and not as a replication of that one.

## 4. The hard negatives the next arm wanted are already 56% of the verifier's training nulls

The arm queued behind A2 was *"retrain the verifier with the gold passage's own
non-gold windows as hard negatives, keeping a uniform-window share so the
unanswerable half stays calibrated; pre-register the mix, e.g. 50/50, and one
alternative"*. Counted over `spans_nq_null` and `spans_nq_positive` **before
any GPU was spent**, joining on the NQ question id every cached window already
carries:

    spans_nq_null                                            100,000 rows
      absent_topical   a passage nobody could answer          42,078
      absent_window    a non-gold window of an answerable
                       passage                                57,922
      of which the passage also contributes a positive
      window to the cache -- a sibling                        56,092   56.1%

**Sibling negatives are 56.1% of the null half and 96.8% of every
`absent_window`.** The verifier has been trained on the hard negatives the arm
proposed to add, at a share above either mix that was to be pre-registered.
There is no 50/50 to choose and no alternative to compare it against: the arm
as specified is not runnable, and re-weighting what is already the majority
class is not a mechanism.

**What is missing is not the negatives. It is the comparison.** The head is
trained with a pointwise binary loss over a shuffled pool, so it is never asked
which of *one passage's* windows carries the answer — and the failure the
ninety-third and ninety-sixth findings name is exactly that: a no-gold window
outranking every gold-bearing one on the same passage, 25.5% and 22.2% of the
answerable half. The listwise variant, named as an option in the arm's own
specification, is therefore the whole of it. The cache supports it with no new
harvest:

    passages with a positive window and at least one sibling    31,792
    rows in those groups                     53,132 positive + 56,092 sibling
    mean group size                                              3.44 windows

**This is why the count was taken before the training run rather than after
it.** Two of the last four findings were corrections to arms that had been
sized against something that was no longer true, and the cheapest place to
catch the third was a pass over metadata that took eight seconds.

## What this cannot say

**§2 is a re-read of a closed arm and it does not reopen it.** Five variants
losing or flat at a second operating point is weaker evidence than the
eighty-fifth finding's mechanism, not stronger; what §2 adds is that the
mechanism does not depend on the threshold.

**`dedupe` is unreplicated in its own right.** It does not reproduce at JOINT,
its +9 / +5 is not significant on either seed, and it is a variant of this
file's definition rather than of the eighty-fifth finding's. Nothing should be
built on it without settling what an occurrence is, which needs the tokenizer.

**§1 is a threshold comparison and not a seed comparison.** It does not say
that the two seeds' *heads* agree; it says the two seeds' species tables agree
once each is read where its own protocol puts it. The seeds still differ by
21 passages of correct silence at their own points.

**§4 counts rows and does not train anything.** That sibling negatives are
present at 56% does not establish that the verifier learned nothing from them,
and no number here says a listwise loss will do better. It establishes only
that the arm as written had no variable in it.

**Two seeds, one trunk, one population**, Population A under `hybrid`, at both
operating points, with each read's point stated.

## What follows

**`PLAN-READER-RESIDUE.md` §7 carries the re-sizing** and it removes A2's
+32 / +25 from the plan's arithmetic: the four arms at their bars now read
501 and 495 of 721 with A2 and **469 and 470 without it**, 65.0% and 65.2%.

**§7.3's ceiling assignment is the part of this worth carrying forward.** A3
and A4 both change the pick on an already-admitted window, so both are bounded
by `ORACLE_PICK` — **449 and 493** — and at their bars they claim +41 and +42
of a shared budget of +60 and +84. Two thirds and half of the entire post-hoc
pick budget from two arms, which was invisible while both were being quoted
against a window oracle.

**B2 is now the listwise arm and only that**, pre-registered in §7.4 with its
selection metric (held-out AUC on the sibling-negative split), its bars and its
failing branch written before it runs.

**Left unexplained:** `span` is +6 on seed 1 and -5 on seed 2 while
`dedupe_span` is +7 and -1, and the two seeds disagree in sign on every
`s_best` variant while agreeing on `hybrid_lp` and `dedupe`. Nothing here says
whether that is the fold wander or a property of the two harvests.
