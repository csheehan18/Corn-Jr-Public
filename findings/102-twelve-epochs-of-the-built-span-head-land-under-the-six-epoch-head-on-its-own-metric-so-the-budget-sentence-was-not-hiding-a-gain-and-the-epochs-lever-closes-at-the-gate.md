# Hundred-and-second finding — twelve epochs of the built span head land two tenths of a point under the six-epoch head on its own metric, with training loss a third of it and logit spread forty per cent wider, so the budget sentence was not hiding a gain and the epochs lever closes at the gate

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`scripts/train_reader_cached.py --arm built --seed 1 --epochs 12`, 2026-09-04.
One seed, by the pre-registered kill rule; the frozen `corn_jr_260m_v4_ft4g`
trunk with no weight of it moved, the same cached states, candidate
enumeration, loss, article split and selection metric as the head that ships.
`evals/results/reader_built12_s1.json`; `checkpoints/reader_built12_s1.pt`
(gitignored). No fold heads, no verifier, no harvest: the gate is a stopping
rule and it stopped the arm. `corn/reader.py` is untouched.

## 0. The question, and where it came from

Finding 83's built arm ended at epoch 5 with training loss 0.101 and its
held-out exact-pair still climbing on both seeds (0.5369 → 0.5410,
0.5368 → 0.5425; seed 3 later 0.5517 → 0.5554), and wrote: "six epochs is the
edge of what this configuration can be run for." That was a sentence about an
epoch costing 643 to 834 s on the live path. The state cache then cut an epoch
to about 140 s and nobody re-asked. `READER-AUDIT.md` row 35 lists it as the
one never-asked lever on the pick, and L7 pre-registers the read: **bar**
held-out exact-pair ≥ 0.565 on both seeds, then a Population A read; **kill**
under 0.55 at epoch 12 on either seed, or a falling curve.

`--epochs 12` was chosen over L7's "resume for six more" because the trainer
has no resume: `--load-head` scores and trains nothing. So this is a
different cosine schedule over twice the run, and not a continuation of the
shipped head. §3 says what that costs the comparison.

## 1. The curve

Held-out exact-pair on the same 4,880-window article-held-out slice, seed 1:

    epoch     12-epoch run    shipped 6-epoch run
      0         0.4883           0.4863
      1         0.5061           0.5172
      2         0.5109           0.5133
      3         0.5086           0.5287
      4         0.5086           0.5369
      5         0.5172           0.5410   <- selected, ships
      6         0.5232
      7         0.5264
      8         0.5340
      9         0.5375
     10         0.5387
     11         0.5391   <- selected

**0.5391 against 0.5410.** The twelve-epoch head never passes the six-epoch
head at any point of its run, trails it by 1.5 to 2.8 points at every matched
epoch while its learning rate is still high, and spends its last six epochs
closing that gap and not opening a new one: +0.60, +0.32, +0.76, +0.35, +0.12,
+0.04 a step. The curve is not falling — finding 100's shape does not appear —
but it has stopped, two tenths under the head that ships and eleven under the
0.55 kill line.

What moved instead:

                              6-epoch head    12-epoch head
    final training loss          0.101           0.029
    logit std at selection       10.21           14.25
    top-1 margin                 3.58            4.89

The head is a third as wrong on the windows it trained on, forty per cent more
spread in its scores, and no more right on windows it has not seen. That is
the ninety-sixth finding's confident-miss result and the hundredth finding's
"more certain and no more correct", read a third time from a third direction.

## 2. The other rulers agree or are flat

Ungated, both evals, the same rows finding 83 printed for the six-epoch head:

                              6-epoch    12-epoch
    frozen tight /200           138        127
    phrase tight /89             36         36
    extract.paired /128          89         77
    took_first                   27         25
    sibling spoken               29         27

Frozen tight down eleven, paired down twelve, phrase flat. None of these has
a bar the built arm is held to (finding 83 §"the arms"), and the seed spread
on the paired file is ±24, so nothing here is a direction either; but nothing
points the other way.

## 3. What this closes, and what it does not

**Closed: L7 by its own kill rule**, on one seed, which is what the rule
asked — "on either seed". Twelve epochs of the shipped configuration do not
clear 0.55, let alone 0.565, and the budget sentence in finding 83 was not
hiding a gain. Under the audit's verdict rule this is *measured* and the
lever is closed on the read L7 named; a second seed would be sixty minutes to
confirm a number eleven points under the kill line.

**Not closed, because it was not run: L7's actual "cheapest read"**, the
shipped head resumed for six more epochs with a short fresh schedule. That
read starts from 0.5410 rather than from scratch and cannot be confounded by
the longer cosine's higher mid-run learning rate the way §1 is. It needs a
`--resume` path in `train_reader_cached.py` (load weights, fresh optimiser,
short schedule at a lower peak rate) that does not exist; about ten lines and
fifteen minutes of GPU a seed. The prior from §1 is that it lands within
noise of 0.5410 — the twelve-epoch curve flattened at exactly that level once
its rate had decayed — but that is a prior and not a measurement.

**Not re-opened: the layer band (row 36).** The cache holds layers 8, 12 and
16 only, so re-asking it is a fresh state harvest of every file the chain
reads, hours before any head trains.

## 4. Limits

One seed. A different schedule from the head it is compared to, which cuts
both ways: it cannot say "six more epochs on the shipped head buy nothing",
only "twelve epochs from scratch buy nothing over six". Run on a shared GPU
for its last three epochs (254, 438 and 611 s against 140 s), which changes
wall time and nothing else. Held-out exact-pair is the head's metric and not
the reader's; no passage was read.
