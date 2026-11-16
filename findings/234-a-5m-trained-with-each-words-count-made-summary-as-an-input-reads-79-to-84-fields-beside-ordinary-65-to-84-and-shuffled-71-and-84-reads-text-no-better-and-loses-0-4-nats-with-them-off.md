# Given the count's word summaries, he leans on them and gains nothing

**Full result:** A 5M trained from its first step with each word's home -- the ruler-blind count squeezed to 512 numbers a word, frozen, added through one trained matrix to the input of the piece after the word -- reads 79, 84, 82 and 80 of the understanding ruler's 141 fields over four seeds (mean 81.2) and 69, 74, 66 and 62 of its 192 wishes (mean 67.8). Twelve 5Ms with no lesson read 65 to 84 fields and 61 to 72 wishes. F and W are each "a direction" by the registered lines -- no seed is over the best ordinary run on the fields, and the wishes clear their fail line by a tenth of an item. Two runs with the homes shuffled between words, the control the registration owed, read 71 and 84 fields and 59 and 65 wishes: the lean is not shown to be the count's. Held-out text costs what it costs the controls (-0.002 to +0.005 nats a token; shuffled +0.003 and +0.006). With its homes switched off a trained run reads text 0.38 to 0.42 nats a token worse: he leans on them heavily and ends where a model that never had them ends.

**Cost:** mechanism, guard 110, six configs and reader committed with the pre-registration at 20:31 on 2026-11-14 (3a61eaf), after two 250-iteration smokes in a scratch directory (59.8 and 19.5 s) and a run of the reader's paths on them (8.7 s); the four runs trained 481.8, 463.7, 449.4 and 453.7 s (the controls 350.0 and 353.9), 1,978.2 s for the chain with its read; the two shuffled runs 456.4 and 456.2 s, 1,037.0 s with the re-read; the tied-table check 16.2 s, contended. ETA about 25 minutes of card for the four runs and their read; 33.0.

**The question** (owner, 2026-11-14: "The goal is to figure out how to make
understanding 'click' with the data we have", then "Let's try it"). Seven
tries from finding 222 to 231 changed what he is asked, and none took the
count's knowledge into him. Far words (232) and word order (233) are not
what the count has over him. This changes what he is *given*: the test
finding 227 left standing, a trunk trained with homes from its first step.
The pre-registration is `configs/nano5m_v3_webblend_homes.py`'s docstring.

## What was built

`corn/homes.py` cuts a window into the count's words; `CornModel.home_in`
adds the home of the word that has just ended, through a 512-by-256 matrix
that starts at zero, to the next piece's input. The table (20,000 words,
10.24M numbers, counted from `mix_v3_webblend` with the ruler never read)
is frozen; read as a count it answers 74 wishes and 90 fields itself. One
piece later than finding 227 placed it, so a home never says a word is over
before the text has. Everything else is the control's run: same batches,
same seed, same trunk at step zero (`scripts/check_homes.py`).

## The read

    twelve 5Ms with no lesson (finding 231): fields 65 to 84, mean 74.5, sd 5.0; wishes 61 to 72, mean 64.7, sd 3.0

                                wishes (192)   fields (141)   held-out text, mean of four sources, against the controls' mean
    control, seed 1337               68             79            3.0355
    control, seed 1338               62             75            3.0472
    HOMES, seed 1337                 69             79            -0.0015
    HOMES, seed 1338                 74             84            +0.0049
    HOMES, seed 1339                 66             82            +0.0027
    HOMES, seed 1340                 62             80            +0.0009
    SHUF, seed 1337                  59             71            +0.0026
    SHUF, seed 1338                  65             84            +0.0064
    HOMES read with homes off     67 70 54 59    77 77 66 82      +0.42, +0.38, +0.42, +0.39 over the same run with them on

## The pre-registered rows

* **F: a direction.** 79, 84, 82, 80; mean 81.2. It held with all four at
  85 or more (none is) and failed with the mean at 79.5 or under.
  Predicted: a direction or fails, mean 76 to 82, at most one seed at 85.
* **W: a direction, by a tenth of an item.** Mean 67.8 against a fail line
  of 67.7; one seed (74) is over every no-lesson run, the others are at 62
  to 69. Predicted fails at 63 to 67: on the line.
* **L: little.** -0.0015 to +0.0049 nats a token against the controls'
  mean, and the two controls stand 0.012 apart. Predicted little, with a
  gain of 0.005 to 0.02: there is no gain.
* **K: not shown to be the count.** F and W did not fail, so the two
  shuffled runs were owed and trained. The lift was the count's if both
  read under the lowest of the four: on the fields 71 and **84** against
  79, on the wishes 59 and **65** against 62. At seed 1338 the shuffled run
  reads 84 fields, as the real one does at that seed.
* **O.** With homes off the text costs 0.38 to 0.42 nats a token more
  (predicted 0.05 or more -- eight times that) and the fields read 77, 77,
  66 and 82 where the same runs read 79, 84, 82 and 80.

## Read by hand

* **Fields that change side, seed 1337**: 17 right only with homes ("that
  can take a hit" -> defense, "that's easy on petrol" -> fuel, "made of
  memory foam" -> material) and 17 right only in the control ("that's
  light to carry around" -> weight, where the homes run says battery;
  "that's a bargain" -> price, gears). 79 and 79: the same count made of
  different items, as two seeds of one recipe are.
* **Stock answers** move run to run and not with the arm: the controls'
  most-picked wrong fields are price 8 and price 7; the four's are rating
  6, genre 10, price 9 and difficulty 6.
* **What they write**, six openers each through the whole-window decoder:
  alike in kind. The homes run's web continuations stay on their noun
  ("the ocean is a very small part of the ocean. The presence of ocean
  photosynthesis...") no more sensibly than the control's.

## Cause reads (not registered; probe only -- not on disk)

* **How unusual the four are.** Among the sixteen runs, four drawn at random
  average 81.2 fields or more in 25 of 1,820 draws (0.014), and average
  67.8 wishes or more in one draw in ten. The fields lean is unlikely to be
  the draw alone -- and the shuffled run at 84 says what else it can be.
* **The twelve ordinary runs miss different items.** Only 24 fields are
  right in all twelve and 14 in none; the other 103 are right in some and
  wrong in others, about evenly spread. A majority vote of the twelve reads
  77.8 fields (a run averages 74.5) and 75.2 wishes (64.7; the best single
  run 72). Most fields are half-held in every run; voting does not firm
  them up.
* **A counted starting table** (the owner's next idea: the count as his
  word-piece table's starting weights). A tied table of 256 numbers a
  piece, built as finding 228 built its tied tables and read as a count,
  answers 82, 83, 80 and 76 fields at windows of 5, 10, 20 and 40 pieces
  and 67, 64, 63 and 55 wishes: inside what an ordinary 5M reads. A trained
  5M's own table read the same way answers 67 and 64 fields. The line said
  before the check was 85 fields; it is not met.

## What it licenses

By the pre-registration this sits between its first and second outcomes and
K decides it: **no lift that can be called the count's.**

* **Being given the count is not the click.** With what the count knows
  about every word laid at his input for the whole run, a 5M's fields stay
  inside what twelve ordinary runs and two shuffled ones read. The 20M with
  homes is not proposed on this.
* **He takes what he is given and it replaces what he would have learned.**
  Switched off, the homes cost him 0.4 nats a token; switched on, he reads
  no better than a control. A home is a fixed function of a word he can
  already see, so it can save him learning and cannot tell him anything
  new -- and by the end of one pass it had saved nothing that shows in
  held-out text.
* **What he reads off a home is which word it is, not what the count says
  about it.** Shuffled homes -- a steady code a word, with the count's
  geometry gone -- leave the text where real ones leave it (+0.003 and
  +0.006 against -0.002 to +0.005).
* **Asked or given, the next-piece question takes what it pays for.**
  Findings 222 to 231 said it of extra lessons; this says it of an extra
  input. The count's knowledge stays beside him.
* **The counted starting table is not built on this evidence.** Its own
  read is at his level, and a start he is free to overwrite is a weaker
  form of an input he could not lose. It is the owner's call.
* **Unguarded read.** `scripts/check_homes.py` holds the mechanism; no
  guard pins `scripts/read_homes_arm.py`, whose own checks are the two
  controls reproducing their saved ruler counts and held-out loss.

**What it does not settle.** Whether real homes beat shuffled ones on the
fields: two shuffled runs at 71 and 84 cannot be told from four at 79 to
84, and four more shuffled seeds (half an hour) would say. A 20M. A home on
the output side (finding 227's cause read lifted both rows a little on a
frozen 20M). Why a typical field is right in half of twelve identical runs.
