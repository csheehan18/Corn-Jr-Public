# Training and validation loss never separate on one pass of data

**Full result:** What a clean loss curve is worth

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`nano20m` was run on the 2.2B-token TinyStories *train* split rather than the 22MB valid
split, which turns a 13.2-pass run into a 0.13-pass one. That choice paid for itself in the
only instrument a training run has:

| iter | train | val |
|---|---|---|
| 500 | 1.0301 | 1.0252 |
| 2000 | 0.6030 | 0.5977 |
| 4000 | 0.5269 | 0.5297 |
| 8000 | 0.4570 | 0.4606 |
| 11500 | 0.4329 | **0.4265** |

**Train and val never separate.** Val sits below train about as often as above, right to the
last iteration, so there is no overfitting signal anywhere in the budget — the model was still
improving when the tokens ran out. The run was bounded by token budget, not by capacity.

On the valid split that conclusion would have been unavailable: 13.2 passes puts a divergence
in the curve regardless of cause, and nothing distinguishes "the schedule is wrong at this
shape" from "it has memorised a 22MB corpus". Every later nano-scale experiment inherits the
hyperparameters this run appears to validate, which is what made it worth paying for.

A caveat for anyone comparing numbers: 0.4265 against `nano`'s 0.6104 confounds three changes
at once — 4.9M → 25.6M params, 65M → 295M tokens, and a different corpus with a different val
set. It is not a clean read on any one of them. DATA.md §7's fixed eval set is the fix.

### An open discrepancy in throughput

Worth recording because the number feeds every Phase 2 estimate. `trainbench` measured 196k
tok/s at this shape in the afternoon; the training run opened at ~197k and fell to ~162–170k
past iter 7,000. Two hypotheses, both since ruled out:

- **Not the data path.** `trainbench` uses synthetic data and never touches the 4.4GB memmap,
  and it now reports 173k.
- **Not thermal.** 173.1k on a hot card, 173.2k on a cooled one, and `nvidia-smi` reports
  **0 µs** of thermal slowdown across the whole run against 1.06s of power capping.

So today's reproducible number for this shape is 173k (30.9 TFLOP/s, still inside VISION §8's
assumed 25–30 band), and this afternoon's was 196k. Something about machine state changed —
the GPU was sitting at 22% utilisation and P3 with 1.2GB allocated by background applications
when this was checked. Untested and cheap: bench from a clean boot.
