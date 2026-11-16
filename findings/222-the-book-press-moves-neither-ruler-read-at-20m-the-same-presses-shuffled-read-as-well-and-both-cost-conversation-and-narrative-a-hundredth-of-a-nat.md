# Pressing harder where the book points taught the 20M nothing more

**Full result:** With finding 221's book (rebuilt without the ruler's words) setting how hard each web word of `mix_v3_webblend` presses on the loss -- 0.5 to 4 times, mean one, the web sources only -- the 20M reads the understanding ruler at 72 and 69 wishes of 192 and 77 and 81 fields of 141, against the unpressed controls' 71 and 73 and 78 and 76, and against 66 and 71 and 82 and 87 for the same presses dealt to other words. Both registered rows fail; where the press is aligned adds nothing. And the kill fires, in both cells: conversational and narrative text, whose press is exactly one, read 0.5249 / 0.5235 and 0.4612 / 0.4606 nats a byte under the book press and 0.5236 / 0.5220 and 0.4602 / 0.4588 under the shuffled one, against lines of 0.5182 and 0.4579 -- about a hundredth of a nat on conversation, thirty times the controls' seed spread. A control retrained the same day on the same seed reads within 0.0005 of the old one on every language row, so the cost is the uneven pressing and not the code. That retrain also prices the ruler's item-level read: against its own twin it gains 30 items and loses 30 of 333 and agrees on the pick for 234, so the 39 gained and 39 lost between a control and its pressed twin are a retrain's worth of noise, and by hand they are his default label per kind moving (finding 192).

**Cost:** build, three hand reads of the score and the pre-registration 07:49-08:15 on 2026-11-13 (54e0fe7); the review that found the ruler's words in the book, 08:33-08:46 (6cb63b4); four runs and four cards 09:00-10:18, 59.4 min of training and 14.0 min of scoring (a pressed run takes 14.8-14.9 min against the control's 14.0: the second cross-entropy costs 6%); the retrained control, registered at feaea46, 14.0 min of training and 3.6 of scoring; two control re-scores 7.8 min; the reads 2.3 min. ETA ~85 min of card for the arms; they took 78, and the control that was not in the estimate took 26 more.

**The question** (owner, 2026-11-12: "certain areas are pressed harder while
some areas pressed lighter", and "the book tells us how hard to press").
Finding 221 put the knowledge the 20M lacks in its own 130M tokens: a book of
tallied lines read the ruler above it. The owner's reading of why was that
every token presses the shared weights with the same gentle strength, most of
it on grammar he already has, so one meeting leaves almost nothing. The arm
changes one thing: the loss weight of each web token. The pre-registration is
`configs/nano20m_v3_webblend_press.py`; `corn/press.py` and
`scripts/build_press.py` argue the press and the score; `scripts/read_press.py`
is the reader and adds no threshold of its own.

## The press

A web word's score is what the ten words before it say about it: each
earlier, different word with a page votes its line to this word (PPMI, window
10) less the word's own usual pull, floored at zero. Clipped at the 99th
percentile, mapped onto 0.5 to 4, divided by its mean: floor 0.507, cap 4.059,
mean one over the 64,328,491 web tokens, exactly one on the other 65,951,222.
A third of web tokens sit at the floor; 8.2% are pressed above two and carry
22.4% of all press; the 200 commonest words average 1.01 and words ranked
2,000 and rarer 1.40. Cell S deals the same multiset to other web words of
the same number of tokens (76.2% of web tokens moved).

Three things were found and fixed before a byte trained, each by reading:

* **Two scores were dropped on the hand read.** The plain sum of a word's
  neighbours' lines pressed `the` and `of` at 2.4 and 2.2 times the mean and
  `snug` at the floor -- finding 221's stock answer. Taking the word's usual
  pull off the sum put two thirds of all tokens at the floor.
* **The book knew the test.** Finding 221's book gave a page to every ruler
  word (336 beyond the 5,000 commonest) and a column to every ruler label (6
  beyond the 20,000 commonest), so a press built from it pressed the test's
  own vocabulary. The files of 54e0fe7 were built that way and dropped; the
  book here never reads the ruler, and `scripts/check_press.py` holds that.
* **A dotted capital I** lower-cases to an i and a combining dot, which
  shifted every aligned word after the 878,735th by one until it was spelled
  out. The alignment is held against the cached stream at both ends.

## The read

    run                                   wishes (192)   2nd 96   fields (141)   lm conversational   narrative   web      val loss
    nano20m_v3_webblend                   71             35       78             0.5129              0.4529      0.9059   2.5270
    nano20m_v3_webblend_seed2             73             37       76             0.5132              0.4516      0.9069   2.4776
    nano20m_v3_webblend_rerun             70             36       79             0.5133              0.4524      0.9064   2.5270
    nano20m_v3_webblend_press             72             35       77             0.5249              0.4612      0.9356   2.6014
    nano20m_v3_webblend_press_seed2       69             33       81             0.5235              0.4606      0.9324   2.5427
    nano20m_v3_webblend_press_shuf        66             30       82             0.5236              0.4602      0.9290   2.5831
    nano20m_v3_webblend_press_shuf_seed2  71             35       87             0.5220              0.4588      0.9268   2.5222
    the book (finding 221)                104            51       97
    corn_jr_260m          (reference)     104            50       101

The controls reproduce finding 221's saved counts (asserted). Every card was
scored by the same harness: the two controls re-scored on the arms' day read
identically on all 96 behaviour rows and all four language rows (probe only --
the re-scored cards were not kept). Per-item picks and margins are in
`evals/results/press__ruler_mix_v3_webblend.json`.

## The pre-registered rows

* **W fails.** 72 and 69 against the controls' 71 and 73; the row asked for 81
  on both. Predicted two to seven above; read level. Cell S reads 66 and 71.
* **F fails.** 77 and 81 against 78 and 76; the row asked for 93 on both.
  Predicted level; read level. Cell S reads 82 and 87 -- above every control
  at both seeds, three and eight over the highest. Not a registered row, and
  one the retrain's noise below should be read beside.
* **L fires, in both cells.** Conversation 0.5249 and 0.5235 (K), 0.5236 and
  0.5220 (S), against a line of 0.5182; narrative 0.4612 and 0.4606 (K),
  0.4602 and 0.4588 (S), against 0.4579. Predicted to hold inside 0.002,
  because only web text is pressed. It did not: pressing web tokens unevenly
  costs the text beside them, whichever tokens are pressed.
* **C.** lm web rises 0.0286 and 0.0255 over the controls' worse seed under
  the book press and 0.0220 and 0.0199 under the shuffled one (predicted 0.01
  to 0.03). `tool.copy_wide` 271 and 293 against 291 and 284: not below
  finding 170's floor.

## What the retrained control showed

`configs/nano20m_v3_webblend_rerun.py` was registered (feaea46) when both
cells first read past the kill line on text they did not press, and two
readings fitted: the pressing, or six commits to `corn/train.py` and
`corn/data.py` since the controls trained on 2026-10-20.

* **The code did not move.** Against the old control at the same seed:
  conversational +0.0004, narrative -0.0005, web +0.0004, temporal +0.0006,
  and the same best iteration and validation loss (5,125, 2.5270). The cost in
  both cells is the pressing.
* **The language rows repeat; nothing item-level does.** The same retrain
  reads 70 wishes and 79 fields -- one off each total -- and against its twin
  it gains 30 items and loses 30, with the same pick on 234 of 333. Behaviour
  rows move further: `tool.copy` 84 against 112 of 120, `daylog.open` 46
  against 23 of 90. Two trainings of one config at one seed are not the same
  model item by item (compiled kernels are not bit-reproducible, and a
  default label per kind amplifies it). So of the nine card rows where both K
  seeds sit outside the controls' range, none is read, and the 39 gained and
  39 lost between `nano20m_v3_webblend` and its pressed twin (35 and 34 at the
  second seed) are nine items a side over a retrain's own churn.

## Read by hand: every item that changed side, both seeds

The changes are his default label moving, not a word learned. At seed 1337
the control answers `scary` to films and `wholesome` to TV shows; the pressed
run answers `sad` and `relaxing` to films and `thrilling` to shows. So it
gains "a family says goodbye to their grandmother in hospital" (sad) and four
`thrilling` shows, and loses four ghost stories and three `wholesome` shows.
At seed 1338 the swap runs the other way -- it gains two `wholesome` shows and
loses two `thrilling` ones. The most picked wrong labels say the same: the
control's are `wholesome` 19 and `scary` 14, the pressed run's `relaxing` 19
and `sad` 12. Finding 192's mechanism, unchanged by the press.

## Why it did not move him (causes named, one read each still owed)

* **The press is a reallocation, not a hard press.** A step averages 24,576
  tokens; the cap moves a token from one part in that to four. A pairing met
  once is still one small nudge. What the book does with one meeting -- write
  a line -- is not what a weight on the loss does.
* **It presses much he already has.** Read before training: the control's
  own loss is 3.12 nats on tokens pressed above two against 3.36 at the
  floor, and 26% of the hardest-pressed he already has under half a nat.
* **A ruler-blind book cannot reach the rare pairs.** Only the 5,000
  commonest words vote and only the 20,000 commonest can be pressed; finding
  221's lead on the wishes rested on lines met once or twice between words
  rarer than that (37 of 96 without them).

## What it licenses

By the pre-registration: **L fired, so no press arm runs without a higher
floor**, and since it fired under the shuffled press too, the cost belongs to
uneven pressing itself and not to the book. The crossed score (hard only
where the book says meaning *and* he is surprised) was owed one read only if
L held; it is not owed now. Finding 223 read the other half of the question
the same day -- whether the knowledge is in him and unread -- and it is not.

**What it does not settle.** One dose, one score, one pass, 20M. Whether a
press that is really hard -- many steps on one meeting, which is rereading --
moves him. Whether a floor of one (only ever pressing harder) keeps the
conversation rows. Whether cell S's fields, 82 and 87, are anything: they are
above the controls at both seeds and unregistered.
