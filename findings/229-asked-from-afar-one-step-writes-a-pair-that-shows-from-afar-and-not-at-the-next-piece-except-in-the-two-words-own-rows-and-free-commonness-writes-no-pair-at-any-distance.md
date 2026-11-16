# Asked from afar, a step writes a pair the next-piece question misses

**Full result:** One step on the far cost -- what a word's first piece costs him at every position from its neighbour's last piece to two before the word -- writes the word's likelihood, like a press on the next piece: the drop where the book is silent is 80% and 84% of the drop at the pair's other meeting, and B - Bx is 0.00. Holding the word's commonness at eight random windows leaves no pair either (B - Bx +0.01 at both seeds, 3% of the drop at B): Q1 fails, as finding 225's hold Q did at the next piece. Held against the pressed sentence with the neighbour swapped out, the far step does write the pair -- **as read from afar**: B - Bx +0.40 at both seeds, with the swapped meeting moving 0.08. Read as the next piece, the way he is asked, the same step reads +0.05 and +0.06, under the next-piece step's +0.24 and +0.20 (the anchor, reproducing finding 225): Q2 fails, by -0.19 and -0.14. Each question writes what the other does not read. The exception is the two words' own word-table rows: there the far step reads +0.98 and +1.03 from afar and +0.21 and +0.18 as the next piece, the next-piece step +0.46 and +0.34 and +0.33 and +0.25 from afar, each at under 0.001 nats a token of damage.

**Cost:** probe and pre-registration committed at 15:00 on 2026-11-13 (acde9d5), after a 12-pair smoke of the instrument (144.0 s) that changed nothing in the docstring; the read 994.2 s of card for two checkpoints, 134 and 133 pairs, 40 press-and-measure rounds a pair. ETA about twenty minutes of card; 16.6.

**The question** (owner, 2026-11-13: "No context is the wrong angle.
Elaborate on the distance and try to connect ideas we've done and seen",
then "Test it"). Finding 228 left distance as the clue under the fields
stall: a count answers more the further it looks, and he is asked one
question a word, the next piece. The owner's reading: the distance that
matters is where the lesson is on offer in the training text. Findings 224
and 225 pressed at one place only, the piece before the word. This asks from
where the neighbour stands. The pre-registration is
`scripts/probe_far_press.py`'s docstring.

## The read

Finding 225's pairs (`b` after an earlier word `a` within ten words, the
book's line 3 nats over `b`'s usual pull, met two to four times); 140 of its
199 have two or more far positions at both meetings (median 8, the most 28),
134 and 133 with room. A is the meeting stepped on, B the other meeting, Bx
the other meeting with `a` swapped for another pair's, C an occurrence of
`b` where the book is silent. Each step is sized to take 2 nats off its own
cost at A; medians over pairs of the nats taken off, both seeds.

    every weight, 2 nats       as the next piece                        asked from afar          held-out
    step                       off B        off Bx       off C         B - Bx        B - Bx       nats a token
    next                       0.47, 0.39   0.43, 0.38   0.49, 0.44    +0.01, +0.01  +0.00, +0.00  0.00018
    next | hold swap           0.38, 0.30   0.06, 0.07   0.17, 0.16    +0.24, +0.20  +0.04, +0.04  0.0025, 0.0022
    far                        0.58, 0.57   0.57, 0.55   0.47, 0.48    +0.00, +0.00  +0.03, +0.04  0.0011
    far | hold usual           0.31, 0.33   0.29, 0.29   0.18, 0.17    +0.01, +0.01  +0.06, +0.06  0.0008
    far | hold swap            0.36, 0.33   0.22, 0.23   0.16, 0.14    +0.05, +0.06  +0.40, +0.40  0.0036, 0.0032

    the two words' rows, 2 nats
    next | hold swap           0.41, 0.51   0.00, 0.02   0.00, 0.00    +0.46, +0.34  +0.33, +0.25  0.0009, 0.0005
    far | hold swap            0.66, 0.51   0.18, 0.07   0.03, 0.02    +0.21, +0.18  +0.98, +1.03  0.0004, 0.0004

Before any step the neighbour is worth 0.09 nats to him at the next piece
(B against Bx, cheaper with `a` there in 62% and 65% of pairs) and 0.02 and
0.05 from afar (52% and 54%): what little he holds of these pairs he holds
where he is asked.

## The pre-registered rows

Each step at its reference strength, the smallest that takes a quarter nat
off `b` as the next piece at B; place `all`.

* **Q1 fails at both seeds.** `far | hold usual` at 2 nats: 0.31 and 0.33
  off B, B - Bx +0.01 (3%), and the drop at C 58% and 52% of the drop at B.
  Predicted. With commonness held what is left is still not the pair; it
  was not at the next piece (finding 225's hold Q, +0.01) and it is not from
  afar.
* **Q2 fails.** `far | hold swap` less `next | hold swap`: -0.19 and -0.14
  at 1.4 and 1.5 times the damage. Predicted a direction the other way
  (+0.03 to +0.12): wrong. Asking from afar does not add to what the
  next-piece question reads; it takes most of it away.
* **N holds.** `next | hold swap` at 2 nats reads +0.24 and +0.20; finding
  225 read +0.24 and +0.21 on 199 pairs.
* **`far` alone writes the word**, as predicted: at its reference (1 nat)
  the drop at C is 80% and 84% of the drop at B and B - Bx is 0.00. Asking
  in more places is more of the cheap answer.
* **D.** Little for `next`, `far` and `far | hold usual`; between for the
  two swap holds in every weight (0.002 to 0.004); little in the rows.

## What the two reads show together (read after, not gated)

    B - Bx at 2 nats           read as the next piece   read from afar
    every weight
      stepped at the next piece    +0.24, +0.20             +0.04, +0.04
      stepped from afar            +0.05, +0.06             +0.40, +0.40
    the two words' rows
      stepped at the next piece    +0.46, +0.34             +0.33, +0.25
      stepped from afar            +0.21, +0.18             +0.98, +1.03

* **Two questions, two stores.** In every weight a pair written by one
  question is a fifth to an eighth as large when the other question reads it.
  From afar the step lifts 66% and 65% of pairs by a quarter nat on its own
  read and 16% and 17% on the next-piece read; the next-piece step, 46% and
  47% on its own and 10% and 8% from afar. The pair is real both times --
  the swapped meeting moves 0.06 to 0.09 -- and it is written where the
  question was asked from.
* **The word table is where they meet.** Confined to the rows of `a`'s and
  `b`'s pieces, a far step carries a fifth of its own read across to the
  next piece (+0.21 and +0.18 beside +0.98 and +1.03) and a next-piece step
  carries most of its own across to the far read. The rows are read at
  every position, so a line there serves both questions. The predicted
  shape, and the size of the far read was not predicted: a whole nat off
  the other meeting from one step, the swapped meeting unmoved (0.00) and
  the word where the book is silent unmoved (0.03 and 0.02), at 0.0004 nats
  a token.
* **Per nat of damage the two steps are level in the rows on the
  next-piece read** (+0.46 at 0.0009 and +0.21 at 0.0004; +0.34 at 0.0005
  and +0.18 at 0.0004). The far step buys the far read beside it.

## Read by hand: fourteen pairs at seed 1337

The far span is what it should be -- `orbit {{ the Sun (a Saturnian year),
and}} [[Saturn's]]`, `Canal {{ fever swept across the country after the}}
[[Erie]]`, `antibiotics {{? Do the}} [[microbial]]`. Under `far | hold
swap` the far read falls at B and not at Bx on the pairs a person would
call pairs (`orbit` to `saturn's`: 10.84 to 9.23 at B, 11.00 to 11.32 at
Bx; `grounds` to `feeding`; `canal` to `erie`; `opinions` to `valued`) and
on neither where the pair is an accident of the page (`place` to
`newcastle`, `poetry` to `patriotic`, where the far step makes the next
piece at A dearer). `spicy` to `soup` moves nothing anywhere at B: the word
stands earlier in its own context and he copies it.

## What it licenses

By the pre-registration, its third outcome: both rows fail. **Where a pair
is asked from does not change what one step writes for the next-piece
question.** Three things stand beside that:

* **Free commonness is not the comparison.** Held at the next piece
  (finding 225) and held from afar, it leaves no pair. The comparison that
  writes one is the neighbour swapped out -- the book's "more than usual" is
  not enough for him, though it is enough for a count.
* **A lesson asked from afar would teach a store the ruler does not read.**
  The ruler asks by the next piece. A far side-lesson in every weight would
  learn and not be used, the shape finding 217 saw with a built-in judge.
  This is the first measurement under finding 228's distance, and it cuts
  against the simple form of the idea: he is not short of far knowledge
  because nobody asked from afar; asking from afar fills a different shelf.
* **The word table is the shared shelf, and it takes a far line cleanly.**
  One row against another is what the book's line is, and finding 228's
  counted table of that shape reads 83 fields where his reads 58 to 61. A
  far, swapped lesson written only into the word table is the form of the
  owner's idea that this read leaves standing -- against finding 226's
  caution that kept presses in shared rows churn.

**What it does not settle.** Many steps: finding 226 kept 150 next-piece
presses and the damage added up; nothing here was kept. Pairs met often and
far apart, which is what the fields are -- these pairs are rare and within
ten words. Whether a trunk trained from the start with a far lesson learns
to carry it to the next piece; one step on a trained trunk cannot say.

## Amended 2026-11-13 -- the rows' cross-read, against a stand-in no hold saw

The table above reads the pair as B - Bx, and Bx carries the stand-in the
hold itself used. Finding 230 kept 100 far steps in the rows and read every
pair against a second stand-in (By) as well:

    far | hold swap, the two words' rows   against Bx (as above)   against By
    asked from afar                        +0.89 and +1.02         +0.44 and +0.46
    as the next piece                      +0.17 and +0.18         +0.04 and +0.07

So "a far step carries a fifth of its own read across to the next piece"
holds against the hold's own stand-in and not against a fresh one: there
the cross-read is about a twentieth of a nat. The word table is the one
place a far line shows at the next piece at all, and it shows very little.
The third licence above ("the shared shelf") is weaker than written; "two
questions, two stores" stands, in the rows as well.
