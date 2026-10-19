# A checker on the whole-passage reader doesn't beat its own confidence

**Full result:** The cross-fitted pair-rows verifier on the whole-passage adapter separates right picks from wrong three points better than the arm's own margin on held rows, and on Population A it is that margin's own curve to the passage on the answerable half and forty correct silences worse on the other, so it closes at its willingness control

`scripts/train_reader_whole.py --fold {0,1}` then `--verifier`, 2026-09-05,
seed 1 only. Two fold arms of finding 112's recipe (three epochs each on half
the articles, 41,707 / 41,946 passages), each reading the argmax pair's two
rows, six scalars and the label "the argmax is a gold pair" on the half it
never saw (83,653 out-of-fold rows, 38.4% / 38.9% positive); an MLP over
`[LN(h_i); LN(h_j); standardised scalars]` selected by AUC on a tenth of the
articles; then the full seed-1 arm's Population A argmax judged by it.
`evals/results/whole_causal_s1_ver.json`, `reader_whole_causal_s1_ver_popa.json`,
`reader_whole_causal_s1_stack_popa.json`; `checkpoints/verifier_whole_causal_s1_ver.pt`
and the fold arms (gitignored); features at `F:/corn-jr-data/states/whole_feats_whole_causal_s1_fold{0,1}.pt`.

## 0. Why

Finding 86's pair-rows verifier was worth +10 / +9 / +18 right at the
silence floor on the window reader, by halving the same-type rival. Finding
112's arm speaks 132 wrong answers and holds 84 right ones back on seed 1,
and its speak-or-decline decision is one null logit in the span softmax.
This is the same head, cross-fitted the same way (finding 85: the label is
unreadable in fold), on the new arm.

## 1. The verifier separates, on the rows it was fitted to

    held rows 8,418          AUC
    span-head margin         0.8041
    verifier (epoch 3)       0.8327
    margin + verifier stack  0.8359

Three points over the margin, and the two-feature stack adds a third of a
point over the verifier alone.

## 2. On Population A it does not, and the willingness control says why

Bar protocol, extent on, each at its own CV'd threshold, seed 1:

                              right  wrong  silent  u.silent  attempt  acc|att
    arm, own margin (112)       505    132      84       198    0.883    0.793
    arm, verifier               465     90     166       198    0.770    0.838
    arm, margin+verifier stack  496    126      99       198    0.863    0.797

    paired vs the margin:  verifier  right -44 (lost 49, won 5, p 4e-10), silence 0
                           stack     right  -9 (lost 14, won 5, p 0.06),  silence 0

**At matched attempt rate (0.781, both fold thresholds shifted together):**

    margin @ 0.781    right 462  wrong 101  u.silent 237
    verifier          right 461  wrong 102  u.silent 198

On the answerable half the verifier is the margin's own precision curve to
within a passage. On the unanswerable half it is **39 to 43 correct silences
worse at every willingness**. Its precision at the bar (0.838) was the
threshold protocol spending silences it did not have, and the stack, which
lets the margin back in, gives back the silences and reads −9 right.

## 3. What it says

The window verifier's edge was structural: the window pipeline's null was a
separate head on the say marker that had never seen the picked span, and the
pair rows told it something new. Here the null already sits in the same
softmax as the pair scores on a trunk that was trained for it, so the
boundary rows carry nothing the margin does not, and the verifier's three
points of held-out AUC are on a label (argmax is gold, unanswerable rows all
negative) whose operating point the bar protocol does not read at. Finding
107's shape on the other side of the fine-tune.

**Closed at the willingness control on one seed.** A second seed would cost
95 minutes to replicate a −40 on silences; not run. The verifier flag stays
in the script.

## 4. What it leaves

The 132 wrong and 84 withheld are still there. What the read rules out is a
second head over the same rows; what it does not touch is the null itself
(its own head on the say marker, or a class-weighted term, are untried on
this arm), the schedule (both seeds' pooled metric was flat across epochs 1
and 2), and CLIPPED at 38 / 34.
