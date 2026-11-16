# One hard press makes the word likelier everywhere, and writes no line

**Full result:** On the trained 20M controls, one gradient step on a word's loss at one meeting of a pair the book knows from two to four meetings, sized to take two nats off the word there (it takes 1.84 and 1.87), takes 0.49 and 0.43 nats off the same word at the pair's other meeting -- and 0.48 and 0.44 off it at an occurrence where the book says nothing about it. The line, what carries because the earlier word is there, is +0.02 nats at both seeds over 193 and 192 pairs. So a hard press is possible -- that step costs held-out text 0.00019 nats a token, and even eight nats costs 0.0037 -- but what it writes is how likely the word is anywhere, a quarter of the press, and not the pair. Pressed only into the word's own rows of the word table it carries further (0.80 and 0.77 of 1.93) at a tenth of the damage (0.00002), and it carries to the unrelated occurrence just the same (0.77 and 0.75; line +0.08 and +0.03). Pressed only into the think-alone matrices it carries least (0.38 and 0.33). No place and no strength writes a line.

**Cost:** probe written and its pre-registration committed at 11:10 on 2026-11-13 (0bb5e87; a 12-item smoke read of the instrument, 92.9 s, was seen before the commit and after the prediction was written); the read 641.8 s of card for 200 pairs at two checkpoints, three places and six strengths. ETA ~6 min of card; it took 10.7 -- eighteen press-and-measure rounds an item were priced as one.

**The question** (owner, 2026-11-13: "could it be we aren't pushing hard
enough when the book says it matters?"). Finding 222's book press failed, and
one reading was that it was never hard: its cap moved a token from one part
of a 24,576-token step to four, where the book writes a whole line from one
meeting. Before a steeper press is trained, this asks what the idea rests on:
how hard can one meeting be pressed, does the press write a line or a
sentence, and what does it dent. The pre-registration is
`scripts/probe_one_press.py`'s docstring.

## The items and the press

From `build_press.py`'s ruler-blind book over the web range of
`mix_v3_webblend`: a word `b` ranked 2,000 or rarer and an earlier word `a`
within ten words before it whose line to `b` sits 3 nats or more over `b`'s
usual pull -- 706,877 such meetings, 33,577 pairs, 4,433 of them met two to
four times with the first two meetings 5,000 words apart. 200 drawn by seed,
no `b` twice: `roof -> leaking`, `uncle -> grandfather`, `guilty -> pleaded`,
`pizza -> olives`. For each: A, the meeting pressed; B, the pair's other
meeting; C, an occurrence of `b` where no earlier word holds a line above its
usual pull. An item is used where `b` costs him 2 nats or more at A (193 and
192 of 200); before any press it costs a median 8.9 nats at A, 8.4 at B and
10.0 at C.

The press is one step on `b`'s loss at A alone, `-s * g / |g|^2`, so its
first-order effect is `s` nats off `b` there; in every weight, in `b`'s own
word-table rows, or in the blocks' think-alone matrices; then put back.

## The read

    nano20m_v3_webblend, medians over 193 pairs (seed 1338 in brackets, 192)
    place   press   off A          off B          off C          line             held-out, nats a token
    all     1.0     0.96 (0.97)    0.25 (0.22)    0.24 (0.22)    +0.01 (+0.01)    +0.00003 (+0.00004)
    all     2.0     1.84 (1.87)    0.49 (0.43)    0.48 (0.44)    +0.02 (+0.02)    +0.00019 (+0.00019)   <- reference
    all     8.0     5.22 (5.24)    1.68 (1.47)    1.72 (1.60)    +0.07 (+0.04)    +0.00385 (+0.00348)
    row     2.0     1.93 (1.93)    0.80 (0.77)    0.77 (0.75)    +0.08 (+0.03)    +0.00002 (+0.00002)   <- reference
    row     8.0     6.24 (6.20)    2.99 (2.79)    2.67 (2.56)    +0.18 (+0.11)    +0.00079 (+0.00075)
    mlp     2.0     1.81 (1.84)    0.38 (0.33)    0.35 (0.32)    +0.01 (+0.01)    +0.00012 (+0.00014)   <- reference
    mlp     8.0     4.92 (5.00)    1.36 (1.20)    1.22 (1.15)    +0.03 (+0.02)    +0.00255 (+0.00249)

All eighteen cells of each seed are in
`evals/results/one_press__mix_v3_webblend.json` with every item.

## The pre-registered rows, at each place's reference strength (2 nats)

* **M fails everywhere.** B carries 0.27 and 0.23 of A in every weight, 0.42
  and 0.40 in the word's rows, 0.21 and 0.18 in the think-alone matrices --
  under the half the row asked -- and the line is +0.02, +0.08 / +0.03 and
  +0.01 where it asked 0.25.
* **W holds everywhere.** The drop at C is 0.98 and 1.02 of the drop at B in
  every weight, 0.96 and 0.97 in the rows, 0.92 and 0.97 in the matrices.
  What carries to another sentence is what carries to any sentence.
* **S**: no for `all` and `row` (B carries more than a fifth of A), yes for
  `mlp` at the second seed (0.18).
* **D: little.** 0.00019 nats a token in every weight at two nats; 0.0037 at
  eight, between the two lines and not breaking.

**The prediction** held on the shape and missed on two sizes. Called: no
place writes a line; `row` carries to B and C alike with almost no damage;
`mlp` reads like `all`. Missed: about half of what carried was called the
word -- it is all of it; and eight nats was called breaking -- it is a third
of the breaking line.

## Read by hand: the first 24 pairs in their sentences, and every item's line

The pairs are what the book would press: a word after its neighbour in two
unrelated texts. `grounds -> feeding`: 5.72 -> 3.82 where pressed ("their
summer feeding"), 7.12 -> 6.79 at the other meeting, 9.06 -> 8.84 in a
football report. `guilty -> pleaded`: 7.48 -> 5.46, 10.66 -> 9.79, and 12.58
-> 11.73 in "she pleaded" from a story. Item by item the line is noise about
zero: at two nats in every weight 24% of pairs read a line over +0.25 and 22%
under -0.25 (24% and 19% at the second seed), mean +0.05 and +0.04. One
voter is junk (`place -> newcastle`); the rest are ties a person would name.
Only the hardest press into the word's own rows shows a line that is not
nothing -- mean +0.26 and +0.20 at eight nats, against 2.99 and 2.79 off B --
a tenth of what carries.

## Why a press writes the word and not the pair

A step goes where the loss falls fastest, and the fastest way to make
`leaking` likelier after `roof` is to make `leaking` likelier: its own
output row and whatever reads it. Finding 199 read the same shape from the
other side -- steered reading lowered a word's surprise where it did not fit
too -- and GENERATORS says it as a rule: he takes the cheapest route the
lines allow. The pair is a smaller part of the same gradient, and one step,
however long, is spent on the larger part first.

## What it licenses

By the pre-registration, **W: a press teaches how likely the word is; the
book's line is not what moved.** So finding 222's press was not too soft --
at any strength it would have taught him which web words are common in the
places the book likes, which is a prior he mostly has. And three things this
probe was not asked for:

* **A hard press is cheap.** Two nats off one meeting costs everything else
  two ten-thousandths of a nat a token, and a tenth of that in the word's
  own rows. The owner's "press hard where it is private" is right about the
  damage: at the same strength the private place dents the rest a tenth as
  much, and at eight nats about what every weight costs at four.
* **The private place holds the word, not the pair.** A word's own row can
  say how likely it is; a line needs two words.
* **What would have to be pressed is the difference**: `b` likelier at A
  *without* `b` likelier at C. That is a press with a second term holding the
  word where the book is silent -- the next read on this instrument, and
  untested.

**What it does not settle.** One step; several small steps on one meeting, or
one step each on a pair's several meetings, may divide differently. A 20M
only. Whether a press that holds the word elsewhere writes the line.
