# Decay and end noise both cleared: the small-step run just learned less

**Full result:** Finding 236's small-step 5M was re-run with its weight decay cut from 0.1 to 0.0188, so that 41,896 steps would apply what the control's 5,237 do. The audit row fails by its own rule -- the weights did not come back to ordinary size but went past it, to 1.6 to 2.2 times six ordinary runs' -- so this is not a "decay matched" run. It is the other side of a bracket: with weights at 0.6 of ordinary size (decay 0.1) the recipe reads held-out text 3.235, and with weights at twice ordinary size (decay 0.0188) it reads 3.224, both against the controls' 3.041. The decay is not why it reads worse. Nor is noise in where it ended: its two saved iterates averaged take 0.022 off, and 4.9M more tokens with the step size taken down tenfold take 0.029 off where the same treatment takes 0.018 off the control. About 0.15 of the 0.18 is neither. The lift is under every ordinary run again (0.41 and 0.27), and read with the writers hidden, 2 of 48 continuations carry the phrase's meaning for this run and 1 of 48 for the control.

**Cost:** config and reader changes committed with the pre-registration at 00:00 on 2026-11-15 (fd00828); the run trained 355.0 s, 558.7 s for the chain with a read that re-read thirteen runs (190.0 s); the cooling check 50.6 s. ETA about seven minutes of training; 5.9.

**The question** (owner, 2026-11-14: "Did you investigate the failures
first? To verify yourself?", then "Run it then hand read it"). Finding 236
explained its worse reading as the noise of small steps without auditing
the run; the audit found a second variable, five times the weight decay,
and the amendment withdrew the explanation. This run takes that variable
out, and the reader now audits before it reads. The pre-registration is
`configs/nano5m_v3_webblend_nudge_wd.py`'s docstring.

## Row A -- the audit, read first

The saved config differs from finding 236's run in `weight_decay` (0.1 to
0.0188) and `name`, and in nothing else. The weights:

    root-mean-square size      word table   position table   attention   mlp     norm gains
    six ordinary runs          0.082-0.087  0.043-0.061      0.074-0.077 0.084   1.00-1.05
    finding 236 (decay 0.1)    0.054        0.014            0.062       0.059   1.51
    this run (decay 0.0188)    0.137        0.037            0.169       0.169   1.12

**The match failed by the registered rule**: three of four groups are far
outside the ordinary ranges, on the high side. Equal total decay does not
give equal weights when there are eight times the steps to grow them. By
the pre-registration no row below is read as "more updates with the decay
held level". They are read as what they are: the same recipe with weights
too large where finding 236's were too small.

## The rows, as that

                                 held-out text   fields: right  lift    wishes: right  lift    first word unchanged
    the two controls             3.036, 3.047       79, 75   0.50, 0.51    68, 62   0.37, 0.30    108, 84
    twelve ordinary 5Ms          3.025-3.107        65-84    0.43-0.59     61-72    0.30-0.39
    small steps, decay 0.1       3.235                 72    0.39             60    0.26           93
    small steps, decay 0.0188    3.224                 75    0.41             62    0.27          109

* **R: worse**, +0.183 nats a token. Given as odds beforehand: worse or
  between 55%, level 30%, better 15%, with 3.06 to 3.14 as the number. It
  is 0.08 worse than that number.
* **U: down.** Both lifts under every ordinary run, as in finding 236.
* **N.** Held-out text at iterate 41,000: 3.2239; at 41,896: 3.2220; their
  weights averaged: 3.2003. Finding 236's pair gave 3.2347, 3.2346 and
  3.1893.
* **H.** Marks written before the key was opened: 2 of 48 for this run
  ("best way to make me feel better" for a recipe that won't make me feel
  heavy; "a very difficult situation" for police who never solve anything
  -- both borderline) and 1 of 48 for the control ("a beautiful day" for a
  cheerful tune about sunshine). On the other 45 sentences both write
  "best way to make it happen", "most important thing to do", "a very
  important one", the phrase's own noun, or a loop on one word ("a small,
  small, small"). Not blind, six ordinary openers: both write short chat
  turns and web sentences of the same kind; the small-step run is not a
  broken writer.

## What was checked before a cause was written (probe only -- not on disk)

**The decay: cleared.** Two runs with weights either side of ordinary size
end 0.011 apart. On the same evaluation batches their last seven
validation losses differ by 0.008 to 0.023.

**Noise in the end state: a small part.** Averaging two iterates takes off
0.045 (decay 0.1) and 0.022 (this run). And a direct test: each run's final
weights trained on 4.9M more tokens with the step size taken down tenfold
over them --

    the small-step run as it ended      3.2220      then cooled   3.1929   (-0.029)
    the control as it ended             3.0355      then cooled   3.0173   (-0.018)

If the run were sitting hot above a good place, cooling would bring it
down. It moves 0.011 more than the control does.

**So about 0.15 nats is in where the run got to, not in how it sits
there.** The curves say when: at the same tokens read the small-step runs
are level with a run of the control's recipe to 37M tokens (3.13 against
3.13 for this run), then stand still while it goes on (3.12 against 2.98 at
49M), and fall only as the step size falls.

    tokens read          25M     37M     49M     74M     98M     123M
    decay 0.1            3.33    3.22    3.22    3.08    2.86    2.85
    decay 0.0188         3.25    3.13    3.12    2.98    2.82    2.84
    control's recipe     3.30    3.13    2.98    2.84    2.71    2.64

**What is left is a guess, and is written as one:** a step size chosen on a
squeezed schedule is too high for this batch over a full one, and the run
spends the middle of its reading unable to settle. Not tested. The settings
still not level per token are the step size against the batch, Adam's two
averages and the gradient clip.

## What it licenses

* **Finding 236's two explanations are both out.** Its first (noise) and
  its amendment's suspect (decay) each account for a few hundredths of a
  nat. The record now says what the cause is not.
* **"More nudges from the same tokens" is still unread.** Both runs tested
  one recipe -- six rows a step at a step size of 2e-3 -- and it reads
  worse. Whether a small step at a step size that suits it reads better,
  the same or worse than the control has not been run. In the squeezed
  smokes the small step at 6e-4 tied the control (3.853 against 3.828).
* **Weight size barely matters to what he reads.** Weights at 0.6 and at
  2 times ordinary size read within 0.011 of each other. The norm layers
  absorb it.
* **The audit earns its place.** It failed this run by its own rule before
  a number was read, and that changed what the run could be said to show.
* **The hand read agrees with itself across three reads**: a 5M continues
  the ruler's sentences with stock openings, 1 to 2 in 24 or 48 touched by
  the phrase, whatever the recipe.

**What it does not settle.** The small step at a lower step size, with or
without Adam's averages stretched to the control's span in tokens. Whether
any recipe reads this text clearly better than the control at 5M, which is
what the understanding question has been waiting on since finding 236.
