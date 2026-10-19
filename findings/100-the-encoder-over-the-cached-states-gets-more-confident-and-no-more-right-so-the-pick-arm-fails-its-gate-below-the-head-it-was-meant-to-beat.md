# Two bidirectional layers over the reader add nothing

**Full result:** Two bidirectional encoder layers over the cached window states buy the pick nothing: the arm peaks below the head it was meant to beat, misses its pre-registered gate by nine points, and spends every later epoch getting more confident and no more right

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`scripts/train_reader_cached.py --arm encoder`, 2026-09-03. One seed, by the
owner's call to stop, which §4 records as a decision. The frozen
`corn_jr_260m_v4_ft4g` trunk with no weight of it moved, the same cached
states, the same candidate enumeration, the same span-head loss, the same
article split and the same selection metric as the built arm.
`evals/results/reader_encoder_s1.json`, `checkpoints/reader_encoder_s1.pt`.

## 0. The arm, and the claim it was run on rather than the one it was declined on

The ninety-fifth finding **declined** this architecture, and
`PLAN-READER-RESIDUE.md` §7.4 records why the decline does not carry to the
claim it is run on here. It was declined because its stated rationale — *a
causal trunk cannot see a span's right context, so the gold falls outside the
enumeration* — is contradicted by that finding's own measurement that the gold
is inside the ten on 89% of the residue. The claim now is the opposite one, and
it is the ninety-sixth finding's §4: **the gold is inside the enumeration and
is ranked second to tenth on the plurality of the residue, and the argmax leads
it by a median 3.72 and 3.05 span-head logits.** That is a scoring failure over
a candidate list that already contains the answer. Same architecture, different
claim.

**What was built.** `CachedHead` gains two `TransformerEncoderLayer`s over each
window's own candidate rows, in front of the existing pair scorer and changing
nothing else. It projects 3,072 to 256, attends, and projects back, which is
**3,158,528 parameters** against the built scorer's 7,947,520 and the trunk's
260M. It is residual with a **zero-initialised output projection**, so at
initialisation the arm computes the built arm's score exactly — verified to
0.0, along with every built-arm weight being the same draw, the flat and padded
score paths agreeing to 0.0, and a window's score being independent of how wide
the widest window in its micro-batch happens to be.

That last check is not decoration. Without a key-padding mask the pad rows
attend and are attended to, and a window's encoding would depend on its
batch-mates — a batching artefact **inside** the score, which the loss mask
downstream would hide.

## 1. The gate was pre-registered and it is missed by nine points

`PLAN-READER-RESIDUE.md` §7.4: **held-out exact-pair >= 0.62, from 0.54, on
both seeds — and if it misses, the arm stops there and no Population A number
is read**, because an arm that cannot pick better on held-out training data has
nothing to convert and reading the population would be reading noise.

    held-out exact-pair, by epoch      selection
    built    s1  .4863 .5172 .5133 .5287 .5369 .5410     0.5410
    built    s2  .4973 .5050 .5040 .5261 .5368 .5425     0.5425
    encoder  s1  .5162 .5291 .5338 .5236 .5186 .5184     0.5338

**0.5338 against a gate of 0.62 and against the built arm's own 0.5410.** The
arm does not merely miss the gate; it finishes **below the head it was built to
beat**, on the metric it was to be selected by, having been given 3.2M
parameters and the right context the whole argument rested on.

**No Population A number was read on this arm**, as the gate says. The
harvested checkpoint is on disk and is not scored.

## 2. It learns something early and then spends five epochs unlearning it

The shape is the result, and it is not the built arm's shape.

    epoch          0      1      2      3      4      5
    train loss   1.808  1.396  1.186  0.999  0.849  0.714
    exact-pair   .5162  .5291  .5338  .5236  .5186  .5184
    logit std     3.86   4.08   4.51   4.70   5.43   5.65

**The encoder is ahead of the built arm at every one of the first three
epochs** — 0.5162 against 0.4863 at epoch 0, which is the built arm's epoch-1
number reached an epoch early — so right context is not worthless to this
scorer. **Then it peaks at epoch 2 and declines for three epochs while the
training loss keeps falling**, where the built arm rises monotonically to the
end. That is overfitting, and 3.2M parameters over 95,204 training windows is
where it would come from.

**And the confidence rises the whole way.** The logit standard deviation goes
3.86 to 5.65 — up 46% — across the three epochs in which held-out accuracy
*falls*. **The arm makes the head more certain and no more correct**, which is
the ninety-sixth finding's §4 read from the other side: the pick failure was
already confident at a median 3.7 logits, and the treatment aimed at it widens
the margins without moving the ranking.

## 3. What this closes, and what it does not

**It closes the cheap version of the pick lever.** `ORACLE_PICK` bounds every
post-hoc re-pick over these candidates at 449 and 493 of 721 (finding 96), and
`ONLY_GOLD_PICK`'s 672 and 670 is what the pick is worth once admission is
handed over. Nothing in this file reaches any of it: the arm gets 0.5338 where
the untouched head gets 0.5410.

**It does not show that right context is useless**, and §2 is the reason to say
so carefully. The first three epochs are a real lead. What is shown is that
this parametrisation of it, at this size, on this many windows, has its optimum
before the built arm's does and lands under it. A smaller encoder, more
regularisation, or a larger training set are all untried, and choosing one of
them after reading this table is a choice made on this table.

**The eighty-sixth finding's re-ranker and this arm now fail the same way from
two directions.** That one could not choose better among the head's own top
five and never left the span head's argmax rate; this one is given the states
and the right context and lands below the span head. Two different mechanisms
aimed at the pick, both reaching under the baseline.

## 4. One seed, and it is the owner's call

The gate reads *on both seeds*, and seed 2 was started and **stopped by the
owner after one epoch** on the ground that the arm was not close: it read
0.5050 at epoch 0, against the built arm's 0.4973 and seed 1's 0.5162, which is
the same shape and the same distance from 0.62. That single epoch is reported
here as one epoch of an incomplete run and is not a seed-2 result; the killed
run's orphan checkpoint was deleted rather than left on disk with no record
behind it.

**This is a deviation from the two-seed house rule and it is recorded as a
decision rather than as an oversight.** The rule exists so that a *claimed*
effect is replicated. The claim here is that an arm missed a pre-registered
gate by nine points from below its own baseline, and a second seed would cost
eighteen minutes to establish that it also misses.

## What this cannot say

**It is one seed on the metric and zero seeds on the population.** The gate is
a stopping rule and it stopped the arm; no Population A read exists for this
head and none should be quoted.

**Six epochs is the built arm's schedule and not this arm's.** The encoder
peaks at epoch 2, so its own schedule would be shorter; the number reported is
the best epoch by the selection metric, which is the protocol, but the run was
not tuned for this architecture and nothing here says a tuned one lands in the
same place.

**The zero-initialised residual is a choice with a consequence.** It makes
epoch 0 the built arm exactly, which is what makes the comparison clean; it
also means the encoder has to earn its way out of an identity, and a different
initialisation is a different arm.

**Nothing here touched the trunk, `corn/extract.py`, `corn/gate.py`, any
scorer, any frozen eval row, or the shipped `corn/reader.py`.**

## What follows

**Both levers the ninety-sixth finding named have now been aimed at and
neither moved.** B2, the admission lever, failed its mechanism bar on both
seeds and made outranking worse (finding 99); P1, the pick lever, failed its
gate below its own baseline. The two coupled levers of similar size are both
still unspent, and `ONLY_GOLD`'s 515 / 499 and `ONLY_GOLD_PICK`'s 672 / 670
are still the bounds.

**What is left in `PLAN-READER-RESIDUE.md` is the owner's call on the 22
(§3) and A4**, and the ninety-eighth finding is the independent read on the
generated frame, which §7.4's B2 failing branch names as the next thing aimed
at admission and prices as much more expensive than anything tried here.

**Left unexplained:** the encoder's epoch-0 lead. 0.5162 against 0.4863 is the
largest single-epoch gap between these two arms anywhere in either curve, and
it is at the epoch where the encoder has barely moved off the identity its
zero-initialised output starts it at. Either the LayerNorm and projection in
front of the scorer are doing the work rather than the attention, or the arm
learns something in one pass that it then overfits away. An ablation with the
attention removed and the projection kept would separate them and is one
training run.
