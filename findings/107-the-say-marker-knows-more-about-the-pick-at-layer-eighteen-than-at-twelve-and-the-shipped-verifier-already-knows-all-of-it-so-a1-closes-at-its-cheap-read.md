# Later layers know slightly more; the shipped checker already has it

**Full result:** The say marker knows more about the pick at layers 14–19 than at 12, by two points of AUC, and the shipped verifier already knows all of it: stacked over its margin no layer adds a thousandth, so A1 closes at its cheap read

`scripts/probe_hlast_layers.py`, 2026-09-04. One forward per Population A
window (3,893) keeping the say marker's row at every block output and at
`ln_f`, 24 s of GPU, 168 MB on `F:` (`popa_hlast_all.pt`); then logistic
probes cross-fitted by passage inside Population A, on both seeds' labels.
`evals/results/hlast_layers_s{1,2}.json`. Nothing trained is kept; nothing
ships; `corn/reader.py` is untouched.

## 0. The arm and its pre-registered kill

`PLAN-READER-REPRESENTATION.md` A1 (audit L9): the verifier reads layers
{8, 12, 16}, a band chosen for *location* by a linear probe on 800 windows on
v4 (finding 83); the verifier's question — speak or decline — is a next-token
question, and no verifier has read layers 17–19 or `ln_f`. Cheapest read:
the say marker at every layer over Population A, the cross-fitted AUC per
layer on the verifier's own label (the shipped span head's argmax on this
window is a gold pair), printed as a curve and not selected on. **Kill:** no
layer beats layer 12 by ≥ 0.01 AUC on either seed.

## 1. The curve: the pre-registered kill does not fire

731 / 700 positive windows of 3,893 (1,211 gold-bearing). Logistic probe on
the 1,024-dim say-marker row, fit on half the passages and scored on the
other half, both ways:

    layer      seed 1    seed 2          layer      seed 1    seed 2
      0        0.5912    0.5903            11       0.7238    0.7126
      1        0.6022    0.5996            12       0.7196    0.7279   <- shipped
      2        0.5817    0.5804            13       0.7289    0.7359
      3        0.6307    0.6307            14       0.7385    0.7466
      4        0.6469    0.6502            15       0.7267    0.7406
      5        0.6581    0.6670            16       0.7192    0.7369   <- shipped
      6        0.6820    0.6936            17       0.7257    0.7437
      7        0.6898    0.6887            18       0.7300    0.7526
      8        0.6864    0.6870   <- shipped  19    0.7399    0.7387
      9        0.7161    0.7097            ln_f     0.7422    0.7461
     10        0.7205    0.7209

**The say marker's knowledge of whether the pick is right rises through the
stack and does not stop at 16**: `ln_f` on seed 1 and layer 18 on seed 2 are
the best single layers, at +0.023 and +0.025 over layer 12. Layer 8, the
bottom of the shipped band, is the weakest of the three by four points on
both seeds. So the band chosen for location is not the band that carries the
verifier's question, and the pre-registered kill does not fire.

## 2. The anchor, and the read it forced

The same label scored by the shipped verifier's own margin — the head that
reads the argmax pair's two boundary rows and three scalars, not the say
marker — reads **AUC 0.8816 and 0.8923**. Every say-marker probe at every
layer is fourteen points under it. The kill in §0 was written as layer against
layer; the number that matters is layer against *the head that ships*, and
the question the arm actually has to answer is whether a late layer's say
marker carries anything the verifier's inputs do not.

That read is stacked and cross-fitted twice: each layer's probe out of fold,
then a two-feature model over (margin, probe score), also out of fold. (A
single 1,025-feature regression over margin and the raw row reads 0.78, ten
points *under* the margin alone on both seeds: 1,900 training rows cannot
find one strong feature among 1,024 weak ones, and that number is the probe
overfitting, not the representation. It is recorded so it is not re-read as
a result.)

    margin + probe of layer     seed 1 AUC   delta     seed 2 AUC   delta
      8                          0.8808     -0.0009     0.8919     -0.0004
      12                         0.8795     -0.0021     0.8909     -0.0013
      14                         0.8797     -0.0019     0.8908     -0.0015
      18                         0.8802     -0.0014     0.8913     -0.0009
      19                         0.8805     -0.0012     0.8911     -0.0012
      ln_f                       0.8804     -0.0012     0.8912     -0.0010

**No layer adds a thousandth of AUC over the margin on either seed.** The
verifier already reads, through the argmax's boundary rows at {8, 12, 16},
everything the say marker at any layer knows about whether that argmax is
right. The late layers' two-point lead over layer 12 in §1 is a fact about the
say marker's row alone; it is not information the head that ships is missing.

## 3. Verdict

**A1 closes at its cheap read, on the second kill rather than the first.**
The pre-registered kill (§0) did not fire; the anchor made a sharper kill
necessary and it fired on both seeds: the largest addition over the shipped
margin is −0.0004. The two variants the plan named — all twenty layers of the
say marker concatenated, and {8, 12, 16, 19, `ln_f`} — would be trained on
inputs that carry nothing the current inputs do not, and the 30-minute
harvest of the say marker for 200,084 training windows is not spent.

What it says for the plan: the verifier's admission error is not a
layer-band problem at the say marker. `PLAN-READER-REPRESENTATION.md` §1's
next reads are A2 (the prompt) and A3 (the layer band for the *span head*,
whose inputs are the candidate rows and not the marker; this finding says
nothing about them).

## 4. Limits

Population A is a test set; the probes are cross-fitted inside it and are
diagnostics, not heads. A logistic probe is linear; a non-linear reader of
the late-layer marker could in principle extract what a linear one cannot,
but the shipped verifier is itself a small MLP over its inputs and the stacked
read gives it the layer's linear score as one more input, which is the
comparison the arm proposed. The label is the shipped head's argmax being a
gold pair, the verifier's own target; a different target (is *any* pair in
the ten right) was not read. Two seeds' labels over one set of states, since
the trunk is the same.

## 5. On disk

`scripts/probe_hlast_layers.py` (new): harvests the say marker at every layer
over Population A once (168 MB, reused), prints the per-layer curve, the
shipped margin's AUC as the anchor, and the stacked-over-margin table, with
both kill rules stated. `evals/results/hlast_layers_s{1,2}.json`.
