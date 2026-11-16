# A short word vector holds field knowledge; frozen, he cannot read it

**Full result:** The book with the ruler never read -- a page for each of the 20,000 commonest words -- answers 91 wishes of 192 and 95 fields of 141 against the 20M's 71 and 73 and 78 and 76, and squeezed to a short list of numbers a word it keeps the fields and loses the wishes: 85 fields and 72 wishes at 256 numbers, 92 and 75 at 512, and still only 83 wishes at 4,096. So the two halves of the understanding ruler are two kinds of knowledge: what a phrase's content word says about a field is compact, and what a whole description implies is a long tail of separate lines that does not fit a short vector. Handed 512-number homes through a 262,144-number input adapter, the frozen 20M reads neither: wishes 68 and 71, fields 74 and 78, failing the registered row at both seeds, though held-out web text gets 0.017 and 0.018 nats a token easier where shuffled homes give 0.000 and 0.003. The same homes laid on his next-piece scores did nothing at the registered settings (it had barely trained), and at ten times the step size and three times the steps -- a cause read -- lift fields to 83 and 80 and wishes to 73 and 77 and take 0.3% to 0.5% off held-out text of every kind: a direction. A first squeeze had read 47 of the second 96 wishes at 256 numbers; that book had a page for every ruler word, and with 5,000 pages and none of them the whole book reads the wishes at the 20M's own level, 71.

**Cost:** the book-only reads 203.7 s of card (and three scratch reads before them, 0.2, 0.4 and 1.3 min); probe and pre-registration committed at 13:27 on 2026-11-13 (d07b777), after a 60-step smoke read (3.6 min) that moved the training set from the web range to the whole stream; the registered run 911.6 s of card, contended at 30%, for four adapters at two checkpoints; the cause read of `out` 635.3 s. ETA ~20 min of card for the registered run; 15.2.

**The question** (owner, 2026-11-13: "Figure out why this happened and
everything we could do what are we not connecting", then "Yes, test it").
Findings 222 and 224 to 226 tried to write the book's knowledge into the
20M by nudging his weights. The other reading of the day was that the
knowledge should not be written by gradient at all: counting writes it, and
he only has to read it. Two things had to be true for that: the knowledge
fits a home a word can carry, and he can read a home. The pre-registration is
`scripts/probe_read_homes.py`'s docstring.

## What a home can hold: the book alone (`--book-only`)

Read as finding 221 read it (`probe_book.read_book`, direct, PPMI at window
10), no model. The ruler's descriptions use 906 words and its labels 102; 596
and 74 of them rank among the 5,000 commonest words, 813 and 96 among the
20,000 commonest.

    who has a page                                              wishes (192)   2nd 96   fields (141)
    the 5,000 commonest, and every ruler word (finding 221)     104            51       97
        squeezed to 256 numbers a word                          98             47       89
    the 5,000 commonest, the ruler never read                   71             36       88
        squeezed to 256                                         64             30       86
    the 20,000 commonest, and every ruler word                  104            51       97
        squeezed to 256                                         73             30       90
    the 20,000 commonest, the ruler never read                  91             42       95
        squeezed to 64                                          57             23       83
        squeezed to 256                                         72             28       85
        squeezed to 512                                         75             30       92
        squeezed to 1,024                                       78             34       89
        squeezed to 2,048                                       79             35       93
        squeezed to 4,096                                       83             37       94
    the 20M controls                                            71 and 73      35, 37   78 and 76

* **Finding 221 holds with the ruler unread, and by less on the wishes.** A
  book of 20,000 pages that never saw the ruler leads the 20M by 18 to 20
  wishes and 17 to 19 fields; finding 221's 31 to 33 wishes rested partly on
  a page for each of the ruler's own rarer words. With 5,000 pages and none
  of those, the wishes read is the 20M's (71) and the fields lead stands
  (88). That book has 32,805,771 lines above zero, more than he has weights.
* **The fields squeeze; the wishes do not.** 64 numbers a word already read
  83 fields, over both controls. The wishes need the whole table: at 256
  numbers they are at his level, and sixteen times that buys eleven items.
* **A squeeze flatters whatever has few rows.** The first read of the day
  squeezed the 5,336-page book and kept 47 of 51: 336 of those pages were
  the test's words. The same squeeze over 20,000 pages, the ruler's words
  still among them, keeps 30.

## Reading a home: the frozen 20M and four adapters

A word's home is the page side of the rank-512 summary of the ruler-blind
20,000-page book, attached at the word's last piece. `in` maps it into the
token's input (he has to read it); `out` maps the mean home of the last ten
finished words onto his next-piece scores (the book speaks); `both`; and
`shuf`, `in` with every word given another word's home. Each starts at zero
and trains 800 steps of 16 windows from the whole train stream at 1e-3.

    cell     numbers      wishes (192)   fields (141)   held-out, nats a token: web / plain web / conversation / narrative
    frozen                71 and 73      78 and 76      3.7312 / 3.8827 / 1.9625 / 1.9468   (seed 1337)
    in       262,144      68 and 71      74 and 78      -0.0169 / -0.0274 / -0.0028 / +0.0075   (-0.0183 / -0.0288 / -0.0037 / +0.0098)
    shuf     262,144      76 and 69      76 and 76      -0.0003 / -0.0125 / +0.0013 / +0.0184   (-0.0029 / -0.0093 / +0.0054 / +0.0230)
    out      4,194,304    71 and 73      78 and 76      -0.0027 / -0.0027 / -0.0015 / -0.0029   (-0.0032 / -0.0032 / -0.0030 / -0.0035)
    both     4,456,448    70 and 76      74 and 78      -0.0192 / -0.0302 / -0.0041 / +0.0058   (-0.0213 / -0.0318 / -0.0060 / +0.0075)
    the squeezed book's own read          74            90

The frozen read through this script's own forward reproduces 71 / 78 and 73
/ 76 (asserted). Per-item picks are in
`evals/results/read_homes__mix_v3_webblend.json`.

## The pre-registered rows

* **H fails.** `in` reads 74 and 78 fields where the row asked 84 on both,
  and 68 and 71 wishes. Predicted: fields inside three of the frozen read
  (it is -4 and +2) and the ruler inside four either way.
* **K is quiet.** `shuf` reads 76 and 76 fields.
* **L holds.** `in` moves conversation and narrative by at most 0.39% and
  0.50%. The smoke read, trained on the web range alone, had moved them
  1.7%, and the registered run trains on every source for that reason.
* **He does read something.** Real homes take 0.017 and 0.018 nats a token
  off held-out web text and 0.027 and 0.029 off plain web; shuffled homes
  take 0.000 and 0.003 and 0.013 and 0.009. Predicted 0.005 to 0.02. It is
  not what the ruler asks: on finding 226's pairs `in` leaves the word 0.16
  and 0.11 nats *harder* at the pair's other meeting.

## The cause read of `out` (not registered)

At the registered settings `out` changed no ruler answer at either seed and
took 0.003 nats off held-out text: a 4.2M-number matrix started at zero had
barely moved in 800 steps at 1e-3. At 1e-2 for 2,400 steps:

    out, 1e-2, 2,400 steps   wishes 73 and 77 (+2, +4)   fields 83 and 80 (+5, +4)
    held-out                 -0.0181 / -0.0151 / -0.0065 / -0.0087   (-0.0199 / -0.0168 / -0.0084 / -0.0092)
    finding 226's pairs      off B +0.10 and +0.14, off By +0.04 and +0.07, B - By +0.06 and +0.06

By finding 222's lines, a direction: fields one and four short of 84. It
costs nothing anywhere -- every source reads easier -- which no press did.
The amended prediction called +3 to +8 fields and got it only here.

## Read by hand: the second 96 at seed 1337

`in` gains one wish and loses five, and the five are his default label
moving again (an old dog at the station: `sad` to `scary`; a jeep safari:
`adventurous` to `sunny`); `shuf` moves three; `out` at the registered
settings moves none.

## What it licenses

By the pre-registration, between its second and third rows: **H fails, and
`out` moves the ruler only in a cause read.** Three things stand:

* **Two kinds of knowledge, two answers.** A field is compact and can ride
  in a short vector -- 64 numbers a word beat the 20M -- so the 20M's
  shortfall there is not room. A wish is a long tail and wants the table
  itself: for that half finding 197's reading, room, was right, and the book
  wins by being larger than he is.
* **A frozen model does not read a new input through a thin adapter.**
  Reading a home is a skill of the trunk. Whether a trunk *trained* with
  homes learns it is still the one-hour arm, at a lower prior than this
  morning's.
* **The book can speak beside him at no cost** -- a little, on both reads,
  with every kind of text easier. For a judgment the runtime makes, the
  book's own answer (91 and 95, ruler unread) is stronger than any of these.

**What it does not settle.** `out` at one pair of settings, chosen after the
registered ones failed to train. Homes from a larger table (a page for every
word, not 20,000). A trunk trained with homes from the first step.
