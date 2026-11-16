# A left-to-right count still beats him, so order is not it

**Full result:** Finding 221's ruler-blind book, split by which side of the label a description word stood on, reads the understanding ruler about as well from one side as from half of both. Counting only the meetings with the description word first -- the order the ruler asks in, and all a left-to-right reader could ever tally -- it answers 82 wishes of 192 and 92 fields of 141; counting only the meetings with the label first, 87 and 90. Six books that keep both orders and half the meetings read 80 to 89 wishes and 88 to 97 fields, so both one-sided books are inside what halving the evidence does. D is dead and S does not hold, as predicted. The two 20Ms that trained on the same tokens read 71 and 73 wishes and 78 and 76 fields: a count that reads in his direction with half the book's evidence is still 9 to 11 wishes and 14 to 16 fields over him. Of the meetings between a description word and its item's right label, 0.53 (wishes) and 0.50 (fields) have the description word first.

**Cost:** probe and pre-registration committed at 18:44 on 2026-11-14 (149924b), after a check stage that read no one-sided or half book (the split tally against `probe_book.tally` cell for cell and the whole book's 91 and 95; 24 s on CPU); the read 26 s on CPU, no card, no checkpoint loaded. ETA about a minute; 0.4.

**The question** (owner, 2026-11-14: "The goal is to figure out how to make
understanding 'click' with the data we have", then "Yes, run it"). The count
pools both orders of a pair -- a line "light goes with weight" is written
whether the text said `light ... weight` or `weight ... light` -- and he
predicts in one order only, the one the ruler asks in. Every lesson tried
from finding 222 to 231 was in that order too. If the book's lead over him
stood in the meetings with the label first, a both-sides lesson on the same
text was the candidate. The pre-registration is
`scripts/probe_book_sides.py`'s docstring.

## The books

`scripts/probe_book.py`'s count, cell and answer, unchanged: PPMI at window
10, every word of the description voting its line to each candidate label,
a page and a column for the 20,000 commonest words and the ruler never read.
A line's weight depends on its own tally and the two words' counts, so only
the cells the ruler touches are tallied: 813 description words by 96 labels
(6 of the ruler's 102 labels stand outside the 20,000 and have no column, as
in finding 221). 9,036,258 meetings within ten words, 4,540,675 with the
description word first and 4,495,583 with the label first. Each meeting is
also filed by the earlier word's position mod 4, and a half book keeps two
of the four classes. A one-sided or half book's chance tally is half the
whole book's, so a pair met equally both ways weighs the same in every book.

## The read

    window 10, ppmi, direct                    wishes (192)   fields (141)
    whole book (finding 221, reproduced)            91             95
    N  six half books                             80-89          88-97
         each                          88/94  80/97  87/96  86/90  88/89  89/88
    before -- description word first                82             92
    after  -- label first                           87             90
    the 20Ms                                      71, 73         78, 76

## The pre-registered rows

* **N.** Halving the meetings moves the book by up to 11 wishes and 7
  fields, and the six halves spread over 9 of each. Predicted within four
  of the whole book: wrong, two of six fall further on the wishes and three
  of six on the fields.
* **D is dead**, as predicted. `before` reads 82 and 92 against half books
  at 80 to 89 and 88 to 97: inside the range on both. `after` reads 87 and
  90, inside it too. The five wishes between them are under the half
  books' own spread.
* **S does not hold**, as predicted: 82 is over the 77 line and 92 over the
  81 line.
* The share of right-label meetings with the description first was called
  between 0.40 and 0.60 and reads 0.53 and 0.50 (by item, the middle half
  0.49 to 0.59 and 0.48 to 0.56). The lean was called toward `after` on the
  wishes and `before` on the fields, and that is the order they fell in, by
  five and two items -- inside the null, so not a result.

## Printed, not gated

    window      whole      before     after      half books (wishes / fields)
       2        81/88      58/85      72/83      68-81 / 83-90
       5        92/92      73/86      78/85      81-85 / 86-94
      10        91/95      82/92      87/90      80-89 / 88-97
      20        91/99      82/91      84/91      80-91 / 90-100

At windows 2 and 5 both one-sided books read under every half book on the
wishes (58 and 72 against 68 to 81; 73 and 78 against 81 to 85) and inside
them on the fields. That is one read at two windows the registration did
not gate, on a book whose halves swing by nine: seen, not a result.

**He does not follow the `before` book.** On the items only one side gets
right, from his saved answers (finding 221): the 20Ms are right on 5 and 9
of the 21 wishes only `before` gets and on 14 and 12 of the 26 only `after`
gets; on the fields 9 and 8 of 14 against 7 and 8 of 12. If he were a
before-only reader his hits would lean to `before`'s; they do not.

## Read by hand

73 items change side between `before` and `after` (35 right in `before`
only, 38 in `after` only); 21 were read with the right label's heaviest
lines and how often each pair was met either way. Two things show.

* **The lines that decide an item are thin.** "a spa retreat with massages
  every afternoon" -> relaxing rests on `spa` met 2 times before and 8
  after, `retreat` 0 and 4, `afternoon` 0 and 5; "two strangers share an
  umbrella" -> romantic on `strangers` 0 and 2; "a cruise at dusk for two
  with champagne" -> romantic on `champagne` 1 and 0 and `cruise` 1 and 0;
  "trekking through jungle" -> adventurous on `jungle` 0 and 3. Which side
  wins such an item is which side the two or three meetings happened to
  fall on. That is the half books' spread seen from inside.
* **Where a pair is met often it is met both ways.** `woods`/scary 24 and
  10, `warm`/sunny 102 and 48, `long`/length 110 and 81, `petrol`/fuel 11
  and 10, `nearly`/age 29 and 25, `moves`/speed 20 and 14. The one lopsided
  heavy line read is `old`/year, 296 before and 3,898 after ("year old").

## What it licenses

By the pre-registration, its second outcome: **order is not what the book
has over him.**

* **Direction is dropped.** A count that only ever tallies the order he
  reads in, on half the evidence, answers 82 wishes and 92 fields to his 71
  to 73 and 76 to 78. The lead is there without a single meeting he could
  not have used. A both-sides lesson is not proposed on this ground.
* **Two of the count's freedoms are now read and neither is the lead.** It
  looks far (finding 232: he uses far words about as well as a model that
  reads the fields) and it pools both orders (here). What is left of what
  the count does and he does not is the first thing finding 221 said about
  it: a line is written by one meeting and writing on one page cannot
  change another.
* **The book's own numbers come with a width.** Which half of the meetings
  is counted moves it by nine wishes and nine fields, because items turn on
  lines met a handful of times. Two books fewer than about nine items apart
  are not shown to differ by one read each. Finding 221's 91 and 95 stand
  as the whole book's; its lead over the 20Ms (18 to 20 wishes, 17 to 19
  fields) is two widths.
* **Unguarded instrument.** The tally is checked against a plain loop and
  against `probe_book.tally`, and the whole book against finding 221's
  numbers, inside the script; no `check_*.py` pins it, so these are bounds
  through `scripts/probe_book_sides.py`.

**What it does not settle.** Why he stops short of a count on his own text:
this removes order and puts nothing in its place. Whether a model can use a
meeting in the other order at all (the count says he would not need to).
The narrow windows, where a one-sided book loses more than half a book
does. And the test finding 227 left standing and nobody has run: a trunk
trained with each word's home from the first step.
