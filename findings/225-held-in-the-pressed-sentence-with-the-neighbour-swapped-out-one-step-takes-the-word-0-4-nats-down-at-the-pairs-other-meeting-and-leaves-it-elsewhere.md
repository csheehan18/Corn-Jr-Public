# Pressing the difference a neighbour makes writes some of the pair

**Full result:** Finding 224's hard press, with the part of its gradient that would move the word in the pressed sentence *with the earlier word swapped out* taken out first, takes 0.40 and 0.34 nats off the word at the pair's other meeting and only 0.07 and 0.05 off it there with the neighbour swapped out, over 192 and 191 pairs at two seeds: the pair line, B - Bx, is +0.24 and +0.21 where the plain press reads +0.01, with 48% and 49% of pairs over +0.25 and none under -0.25. The registered row asked 0.25 in every weight, so it is a direction and not a pass, and the hold itself leaks (the word gets 0.18 and 0.16 nats costlier in the held sentence). Pressed only into the two words' own word-table rows the same step reads cleaner: 0.47 and 0.53 off the word at the other meeting, 0.04 and 0.02 where the book is silent, 0.05 and 0.00 with the neighbour swapped, for a third of the damage (0.00063 and 0.00037 nats a token against 0.0020 and 0.0018) -- printed beside the row, not registered. Holding the word at eight book-silent occurrences instead writes no pair at all (+0.01). So what a press writes follows what it is held against: nothing, and it writes the word; the word elsewhere, and it writes less of the same; the same sentence without the neighbour, and what is left is the neighbour.

**Cost:** probe written and its pre-registration committed at 11:56 on 2026-11-13 (a97b456; a 6-item smoke read of the instrument, 112.6 s, was seen before the commit and after the prediction was written, and one ungated printout was added after it); the read 1,777 s of card, contended at 26%, for 199 pairs at two checkpoints, four places, three modes and four strengths. ETA ~25 min of card; 29.6.

**The question** (owner, 2026-11-13: "Yes test it"). Finding 224: a hard
press on a word at one meeting of a book-tied pair makes the word likelier
everywhere, because that is where the loss falls fastest. The press has to be
forbidden that route -- the word up where its neighbour is, held where it is
not. The pre-registration is `scripts/probe_held_press.py`'s docstring.

## The press

Finding 224's pairs, windows and nats-sized step. The direction changes: `d
= g_A - (g_A . g_h / |g_h|^2) g_h`, the step `-s * d / (g_A . d)`, so to
first order a held loss does not move and the word at A still loses `s`
nats. Two holds beside the plain press: **hold Q**, the word at eight other
occurrences where the book is silent about it; **hold X**, the word in A
itself with every token of the earlier word `a` in the ten words before it
replaced by another item's `a` ("Whether or not your *orbit* has started
[[leaking]]"). Read after each step: the word's cost at A, at B (the pair's
other meeting), at Bx (B with `a` swapped the same way), at C (an occurrence
where the book is silent, never held), at Ax, and held-out text. 199 of the
200 pairs have the neighbour to swap in both meetings and four or more quiet
occurrences.

## The read, at two nats (seed 1338 in brackets)

    mode     place   off A          off B          off Bx         off C          off Ax           B - Bx           B - C            pairs up / down          held-out, nats a token
    plain    all     1.84 (1.87)    0.49 (0.43)    0.46 (0.42)    0.49 (0.44)    +1.72 (+1.71)    +0.01 (+0.01)    +0.02 (+0.02)    0.03 / 0.01 (0.02 / 0.00)    0.00019 (0.00019)
    hold Q   all     1.84 (1.86)    0.21 (0.20)    0.19 (0.17)    0.15 (0.14)    +1.70 (+1.69)    +0.01 (+0.01)    +0.09 (+0.05)    0.04 / 0.00 (0.04 / 0.01)    0.00019 (0.00020)
    hold X   all     1.70 (1.72)    0.40 (0.34)    0.07 (0.05)    0.20 (0.21)    -0.18 (-0.16)    +0.24 (+0.21)    +0.11 (+0.09)    0.48 / 0.00 (0.49 / 0.00)    0.00201 (0.00178)
    hold X   pair    1.84 (1.83)    0.47 (0.53)    0.05 (0.00)    0.04 (0.02)    -0.07 (-0.10)    +0.49 (+0.35)    +0.49 (+0.43)    0.62 / 0.01 (0.59 / 0.03)    0.00063 (0.00037)
    hold X   row     1.84 (1.79)    0.50 (0.59)    0.01 (0.00)    0.05 (0.01)    -0.11 (-0.16)    +0.48 (+0.36)    +0.43 (+0.38)    0.64 / 0.02 (0.58 / 0.01)    0.00137 (0.00072)
    hold X   mlp     1.55 (1.54)    0.28 (0.23)    0.07 (0.03)    0.10 (0.08)    -0.43 (-0.34)    +0.17 (+0.15)    +0.12 (+0.12)    0.38 / 0.01 (0.39 / 0.01)    0.00239 (0.00189)

Medians over 192 and 191 pairs; "pairs up / down" is the share whose B - Bx
is over +0.25 or under -0.25. All 48 cells of each seed, with every item,
are in `evals/results/held_press__mix_v3_webblend.json`.

## The pre-registered rows (place `all`, the reference strength of two nats)

* **M under hold X is a direction, at both seeds.** B - Bx reads +0.24 and
  +0.21 against a line of 0.25 and a fail line of 0.1; the word comes 0.40
  and 0.34 nats down at B. Predicted between 0.1 and 0.3: called.
* **M fails under hold Q and under the plain press** (+0.01 each, both
  seeds). Predicted for both.
* **H leaks under both holds.** Hold X: the word gets 0.18 and 0.16 nats
  costlier in the held sentence (the line was 0.1) -- a first-order hold, and
  a step scaled up six times because only 0.16 of A's gradient is left once
  the swapped sentence is taken out. Hold Q: the unseen quiet occurrence
  still moves 0.15 and 0.14, where the hold was predicted to keep it inside
  0.1; eight occurrences do not pin a word's likelihood everywhere.
* **D.** Hold X costs 0.0020 and 0.0018 nats a token on held-out text, on
  either side of the "little" line and ten times the plain press.

## Beside the rows: the word-table rows (not registered)

The prediction said `row` -- the word's own rows -- "cannot hold a pair and
its held step either does nothing or blows up". It was wrong. Under hold X at
two nats the word's rows alone carry 0.50 and 0.59 nats to the other meeting,
0.05 and 0.01 to the book-silent occurrence and 0.01 and 0.00 to the swapped
one; `pair` (the rows of both words) reads the same at half the damage. How a
single word's row can hold a pair: the row is also the word's *output*
vector, and the step turns it toward the part of his state that is there only
when the neighbour was read. It does blow up, later: at eight nats `row`
costs 0.085 nats a token.

Three cautions on that read, each from the items:

* **Bx shares its swapped word with the held sentence.** The step may be
  teaching "not after *orbit*" as well as "after *roof*", which would open
  the B - Bx gap from the wrong side. B - C does not have that problem, and
  in `pair` it reads +0.49 and +0.43; in `all` only +0.11 and +0.09.
* **The medians hide a tail.** In `pair` the word gets 0.25 nats or more
  easier at B on 60% and 63% of pairs and harder on 18% and 16%; at C it gets
  that much harder on a third of them. On average the step pushes the word
  down where the neighbour is absent (mean -0.32 and -0.26 at C) as much as
  it lifts it where the neighbour is (+0.43 and +0.41 at B).
* **It is not copying.** On the 129 and 128 pairs whose word does not
  already stand in either meeting's own context, hold X in every weight reads
  B - Bx +0.36 and +0.35 (0.12 and 0.08 on the rest): the pairs he could read
  off the page are the ones that move least.

## Read by hand: the first 13 pairs in their five sentences

`roof -> leaking`: at the other meeting ("to keep the roof from [[leaking]]")
8.80 -> 8.45 under hold X, where the plain press read 8.28; with *orbit* in
the roof's place 10.90 -> 11.49, where the plain press read 10.26; in the
unrelated sentence 11.34 -> 11.52 against 10.77. `managers -> coaches`: 9.31
-> 8.38 at B, 10.79 -> 11.25 at Bx. `antibiotics -> microbial`: 6.17 -> 5.81
at B, 6.55 -> 6.57 at Bx. The plain press takes the word down in all five
sentences; the held one takes it down where the neighbour is and leaves it or
lifts it where the neighbour is not. The swapped sentences are odd English
("pest *grounds*, or [[herbicide]]"), which is what a counterfactual costs.

## What it licenses

By the pre-registration, **a direction: the pair is in reach of one step and
small.** Half a nat off a word that costs him eight is a start on a line, not
a line. What it settles is the mechanism the last three findings circled:

* **What a press writes is set by what it is compared with**, not by how
  hard it is. Plain, it writes the word (finding 224). Held against the word
  elsewhere, it writes less of the same. Held against the same sentence
  without the neighbour, what is left is the neighbour.
* **The owner's two ideas meet here.** The book names the pairs; the private
  place -- the two words' own rows -- takes the press at a third of the
  damage and holds the cleanest read; and the press is aimed at the
  difference.

**What it does not settle, and the reads it names.** Whether presses add up:
200 pairs pressed one after another and kept, then every pair and the damage
read -- the same instrument, and the next read. Whether a pair written this
way survives ordinary training after it. A swapped meeting with a *different*
swapped word than the held sentence, which removes the first caution. Whether
`pair`, registered as the place, holds the row it read here. A 20M only; and
word-after-word pairs in web text, not what a description implies.
