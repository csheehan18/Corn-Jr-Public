# Looping until it sounds right: he learns to always keep looking

**Full result:** G6's loop rung as the owner defined it, "until it sounds right", by fine-tune from arm E2's three starts: he learns to write `none` on every batch -- 189-192 of 192 answer batches, every start, the free line and two scoring reads agreeing -- so three gates fail and the fourth passes vacuously; the starts never wrote `none` at all; and inside, his lean to stop does not follow the wish (the swap twins at AUC 0.38-0.49) while the soft read under it ranks the right place first on 47-60% of answer batches against a chance of about 42%

**Cost:** three fine-tunes of 650 iterations at 20M (144, 143, 143 s, contended -- the card at 35-38%, a bound), three loop reads at 18-19 s and three copy cards at 8 s: one chain of 509.1 s, 13:19-13:28 on 2026-10-20, registered ~9 min; the zero-training control 57 s; the three-way read on six checkpoints 399 s and the inside read on six 90 s; the build 12:57-13:18 on CPU.

**The owner's go, 2026-10-20**: "let's move on to loop", and of three
definitions offered his pick was **"until it sounds right"** -- a stop rule
the runtime cannot check -- over "keep looking until" a checkable condition
and "do it for each". Pre-registered at bf6c994 (`configs/mix_v3_loop_ft.py`)
after a zero-training control read and before a byte trained.

**The world** (`corn/loopgen.py`). A request with a soft wish and a loop
frame ("keep looking till you find somewhere cosy"); batch after batch of two
or three places; on each his `pick: because[<the answering place's
description>]` (D-A1.20) or `pick: none`; on `none` the runtime fetches the
next batch, up to four, so no line of his is one the runtime could compute.
The answer on batch 1, 2, 3 or 4 or nowhere, a fifth each. The lexicon and
holdout are `corn/filtergen.py`'s -- no description shares a content word
with any wish, 24 of 72 phrasing x family pairings never train -- and no
place in a trace could answer the wish but the answer. `scripts/check_loop.py`
holds it, every description's concept found by matching filtergen's
templates; three mutants each fail their check. The recipe is the branch
fine-tunes' (findings 179-183), the loop payload in the branch payload's
place: 1.68 passes.

## The registered read

`scripts/probe_loop.py`, every batch's options scored in full, earlier
batches' gold picks before it; a trace right when every batch is:

    run            train (gate 0.85)   no answer, all none   swap (0.80)   held (0.60)
                   of 240              (gate 0.85) of 48     of 148        of 120
    start ev2       23                   0                     59             8
    start ev2s2     22                   0                     66            12
    start ev2s3     23                   0                     55             7
    loop ev2        48                  48                      0            24
    loop ev2s2      48                  48                      0            24
    loop ev2s3      48                  48                      0            24

**Every trace right is a trace with no answer.** Early stops 0, misses 192
of 192 answer batches on the trained rows at every start. Installs, reads it
and by meaning fail at three of three; gives up passes at three of three and
means nothing -- he never stops. The prediction (the first three gates at
three of three, by meaning at one) was wrong.

## The instrument, suspected and cleared

The first fine-tune's six free decodes held one where he wrote the gold
(`pick: because[a rooftop hostel]`) and the registered read had picked
`none` -- and the read sums each option's loss over its whole line, which
favours the two-token `pick: none` over an eight-token description. So the
read was rebuilt (`probe_loop.py --split`, committed): the decision at its
one token (`pick: none` against `pick: because`), the place among the
`because[...]` options by full loss, and **his greedy line on every batch**.
All three agree: the free line writes `none` on 189, 192 and 192 of 192
answer batches. The length bias accounts for 3, 0 and 0 of 436 answer
batches; the one decode read by hand was one of the three. **The collapse
is his, not the instrument's.**

## Inside: is the judgment there and outvoted?

`scripts/probe_loop_inside.py` (committed), per batch `d = loss(pick: none) -
loss(pick: because)` -- the stop lean, no length term -- and, on answer
batches, whether the right place ranks first among the places:

    run            AUC answer vs none batch      right place first
                   train   held   swap           train (of 192)  held (96)  swap (148)
    start ev2      0.44    0.43   0.59             87              37          67
    start ev2s2    0.44    0.53   0.45             91              37          76
    start ev2s3    0.40    0.39   0.52             76              41          71
    loop ev2       0.64    0.63   0.49             94              46          77
    loop ev2s2     0.62    0.66   0.38            116              51         101
    loop ev2s3     0.63    0.64   0.45             90              46          75

After the fine-tune his lean to stop is a little higher on the batches that
hold the answer (AUC 0.62-0.66) -- **and not on the swap twins (0.38-0.49),
where the batches are the same and only the wish moved.** What separates an
answer batch from the others on the trained rows is not the wish; the batch's
place in the trace is the candidate it leaves. The soft read under the
decision -- forced to choose among the places on an answer batch -- ranks
the right one first on 47-49% at two starts and 60% (swap 68%) at 2337, the
start finding 148 found reading the wish at pretraining; chance is about 42%
(two or three places).

## The copy row, a side column

`tool.copy_wide` 298, 264, 286 against the starts' 298, 295, 293 -- the
second start's fall again, its fifth arm today (finding 180's digit species,
still owed a cause).

## What it licenses

* **Loop's stop rule is rung 3's soft read, and at nano the soft read is not
  there to stop on.** Near chance at two starts of three and partial at the
  third -- finding 148's split, unchanged by a fine-tune that taught the
  format. The batch decision had nothing to read, and fell to the payload's
  majority answer (`none`, 71% of decisions): the starts always stopped, the
  fine-tunes never do. GENERATORS §1 with the input missing rather than a
  shortcut present.
* **The `none` decision now has two readings on record, both a constant**:
  never written at pretraining (findings 148-149, these starts), always
  written after a fine-tune where it is the majority. Neither is a decision.
* **For the ladder**: the iteration format (the runtime fetching the next
  batch after `none`) is unread, because nothing above it formed. The
  owner's choice is between testing loop's control on a stop the runtime can
  check -- which splits the format from the soft read, as branch did -- and
  taking the soft read itself as the work, which is a meaning hop findings
  148, 156 and 167-168 found to be the wall at nano.

**What it does not settle.** Whether loop's control installs on a checkable
stop; whether the soft read forms at 260M or with real descriptions; whether
balancing the payload's `none` share changes the constant's sign without
making a decision; and the second start's copy species.
