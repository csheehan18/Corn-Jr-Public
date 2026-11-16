# Kept presses last, but break the text and churn the words

**Full result:** 150 of finding 225's pairs pressed one after another and kept -- the held step in the pair's own word-table rows, two nats each -- stay pressed (0.98 and 0.97 of what each press took off its own sentence is still off at the end; 0.90 and 0.91 for the first 50), and the word comes a median 0.33 and 0.42 nats down at the pair's other meeting. But against a swapped meeting whose stand-in word the hold never saw, the pair is 0.11 and 0.20 nats, a direction and half of finding 225's read; the held-out text costs 0.102 and 0.057 nats a token more, breaking, and adding up press by press; and the medians sit on churn -- at the other meeting the word is a quarter of a nat easier on 53% and 54% of pressed pairs and that much harder on 28% and 27%, down to 12 nats harder, and of the pairs never pressed 36% and 39% are a quarter of a nat harder. No compounding. At half the strength the damage is seven times less (0.014 and 0.011) for about half the pair (0.07 and 0.11); in every weight the text loses 0.20 nats a token and the never-pressed pairs 0.38 and 0.89; and the plain press kept is harmless (0.005 and 0.004) and writes 150 words, not pairs.

**Cost:** probe and pre-registration committed at 12:34 on 2026-11-13 (8bd4d57; a 30-pair smoke read, 125.1 s, seen before the commit and after the prediction was written); the read 213.2 s of card for four passes of 150 presses at two checkpoints; the hand read's printout 55.8 s. ETA ~8 min of card; 3.6.

**The question** (owner, 2026-11-13: "let's keep going", and while it ran,
"is there any chance we get a compounding result in our favor?"). Finding
225 wrote some of a pair with one held press, measured and put back. A way
of teaching is many presses, kept. The pre-registration is
`scripts/probe_kept_press.py`'s docstring: three ways it could end cheaply --
later presses overwrite earlier ones, the damage piles up, or the pair gap
was opened from the wrong side.

## The read, after all 150 presses (seed 1338 in brackets)

    pass                    still off A   off B           off By          off C           B - By           held-out, nats a token   never pressed, off B
    hold X, pair, 2 nats    0.98 (0.97)   0.33 (0.42)     0.11 (0.16)     -0.13 (-0.10)   +0.11 (+0.20)    +0.102 (+0.057)          -0.07 (-0.14)
    hold X, pair, 1 nat     0.99 (0.99)   0.26 (0.29)     0.13 (0.16)     +0.01 (+0.01)   +0.07 (+0.11)    +0.014 (+0.011)          -0.01 (-0.03)
    hold X, all,  2 nats    0.67 (0.82)   -0.08 (-0.02)   -0.45 (-0.48)   -0.23 (-0.45)   +0.29 (+0.34)    +0.201 (+0.205)          -0.38 (-0.89)
    plain,  pair, 2 nats    1.00 (0.99)   0.74 (0.76)     0.71 (0.73)     0.71 (0.73)     +0.01 (+0.01)    +0.005 (+0.004)          -0.02 (-0.00)

Medians over the 150 pressed pairs. By is the pair's other meeting with the
neighbour swapped for a word the press never saw. The readings after 50 and
100 presses, every item, and each pair's cost straight after its own press
are in `evals/results/kept_press__mix_v3_webblend.json`.

## The pre-registered rows, for the primary pass

* **R holds.** 0.98 and 0.97; the first 50 pressed, with 100 presses on top
  of them, 0.90 and 0.91. Predicted 0.7 to 0.9: it lasts better than called.
* **P is a direction.** B - By reads +0.11 and +0.20 against a line of 0.25
  and a fail line of 0.1. Predicted 0.2 to 0.4. Finding 225's first caution
  was right: against the stand-in word the hold used, the same pairs read
  +0.40 and +0.32, and By takes half of that away -- the press had been
  teaching "not after *orbit*" as well as "after *roof*".
* **D is breaking.** +0.102 and +0.057 nats a token (the text goes from 2.665
  to 2.767 at seed 1337), past the line of 0.05, and it adds up: +0.021,
  +0.056, +0.102 after 50, 100 and 150. Predicted 0.03 to 0.08.
* **U: the pairs never pressed drift down**, -0.07 and -0.14 at their other
  meeting. Predicted quiet. No reading shows them easier: no compounding, in
  the pair's rows or in every weight, where they lose 0.38 and 0.89.

## Read by hand: the first 12 pressed pairs and 6 never pressed, in their sentences

The medians do not describe a pair. `headache -> throbbing`: 12.70 -> 8.04
at the other meeting -- and 12.61 -> 9.14 with *hook* in the headache's
place: the word got likelier in that kind of sentence, neighbour or not.
`sauce -> chili`: 10.58 -> 9.30 with the sauce, 11.74 -> 11.42 without it,
the pair as it should read. `pounds -> weighed`: 5.43 -> 2.86 where it was
pressed and **10.72 -> 13.09** at the other meeting. `paris -> dame`: 3.93
-> 8.27. And a pair that was never pressed, `heavily -> relied`: 7.26 ->
11.71. Counted over every pressed pair: at the other meeting the word is a
quarter of a nat easier on 53% and 54% and that much harder on 28% and 27%
(the worst, 12.5 and 12.9 nats); where the book is silent it is harder on
44% and easier on 35%. Of the never-pressed, 36% and 39% are harder and 10%
easier.

## Why (causes named from the items; one read each still owed)

* **The private place is not private.** The word table has 8,192 rows of
  *pieces* for 393,826 words. `relied`, `weighed` and `dame` are spelled
  from pieces other words use, so a press on one word's rows moves every
  word that shares a piece -- which is how a pair nobody pressed loses four
  nats. One press cannot show this; 150 do.
* **The held step is a long step in a thin direction.** Once the swapped
  sentence is taken out, 3% to 4% of the gradient is left in those rows, so
  taking two nats off means a step about thirty times longer than the plain
  press's. The plain press, kept, costs the text twenty times less.
* **Damage grows faster than strength.** Half the nats cost a seventh of the
  damage (0.014 and 0.011 against 0.102 and 0.057) for about half the pair.
  Whatever writes pairs this way is many small steps, not few hard ones.

## What it licenses

By the pre-registration this sits between two rows: P is a direction and
not a hold, and D breaks. **Hard held presses, kept, are not a way of
teaching as they stand**: they write a tenth to a fifth of a nat of pair
into a model that pays 2% to 4% of its text for it. What survives from
findings 224 and 225 is the mechanism, not the delivery -- what a press
writes is set by what it is compared with -- and three things this read
adds:

* the comparison has to be made gently and beside ordinary reading, which
  is what repairs the text: a paired term in the loss at a small weight, a
  training arm and not a press;
* a private place has to be private: one row a *word*, which the piece
  table is not (the unit question `IDEAS-UNDERSTANDING.md` §7 names);
* and the swapped word has to vary, or half of what is learned is the
  stand-in.

**What it does not settle.** Whether the same comparison as a small term in
training, with the stand-in drawn afresh each time, writes pairs without the
bill -- the precedent is against it (two added lessons cost language at 5M,
findings 206 and 217) and for it (neither was aimed at a difference). One
order of pairs; 150 of them; a 20M.
