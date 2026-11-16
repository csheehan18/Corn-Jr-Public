# He uses far words like the 260M; his gap is close in

**Full result:** On 4,800 held-out meetings of word pairs -- 2,400 the ruler-blind book ties and his text shows 30 times or more, 2,400 it says nothing about -- what an earlier word is worth to the 20M at the next piece falls with distance no faster than it does for the 260M. A tied word 9 to 16 words back takes 0.28 and 0.29 nats off the word it is tied to at the two 20Ms and 0.33 at the 260M; the 20Ms keep 0.85 and 0.88 of their standing against the 260M from one word back to there, where the row held at 0.5 and failed at 0.8. With the context cut to the last k pieces, pieces 11 to 40 back are worth 0.66 and 0.63 of what they are worth to the 260M and pieces 2 to 10 back 0.66 and 0.71: the same two thirds near and far, 0.99 and 0.90 on a row with the same lines. D, T and Z fail. Where the 20M does fall short is close in: 0.65 and 0.70 of the 260M's pair worth two words back and 0.56 and 0.51 at three to four, and of the 2.15 nats between them on these words with the whole context, 1.6 are already there with only the last five pieces in view. The two 5Ms read like the 20Ms on every row; the 100M reads like the 260M on every row and reads the ruler's fields like the 20M.

**Cost:** probe and pre-registration committed at 16:38 on 2026-11-14 (60789e6), after the items were counted on the CPU (131.9 s, twice), a 40-meeting smoke of the swap read on one 20M and the 260M (72.0 s of card) that added the cut read, and a 20-meeting smoke of the cut read whose numbers were not read (77.7 s); the read 275.4 s of card for six checkpoints, contended at 31%; the cause read no card. ETA about five minutes of card; 4.6.

**The question** (owner, 2026-11-14: "I feel as though we are close but are
missing something", then "Yes let's do it"). Finding 228 left distance as
the clue under the fields stall -- a count answers more fields the further
it looks -- and named the read nobody made: how far back he actually reads.
Findings 229 to 231 then tried three ways to teach him from afar. The
reading offered to the owner was that those tries changed the question he
is asked and none changed the path by which a far word gets credit, so that
what an earlier word is worth to him should fall away with distance faster
than it does for the 260M. This is that read. The pre-registration is
`scripts/probe_far_read.py`'s docstring.

## The items, and what the count says

Pairs `a` then `b` from `scripts/build_press.py`'s ruler-blind book: tied
(the line 1.5 nats or more over `b`'s usual pull, met 30 times or more;
201,714 pairs) and untied (the line at or under the usual pull). Meetings
are read off `val_web.bin` and `val_web_plain.bin`, with `a` once in 128
tokens of context, `b` not in it, and no end of a document between them.

    words back                       1        2      3-4      5-8     9-16    17-30
    tied meetings found          5,568    2,942    3,909    5,644    9,849   15,620
    kept, tied and untied each     400      400      400      400      400      400
    median pieces back (tied)        1        2        4        9       18       35
    the count: tied lift, nats   +3.46    +3.16    +2.88    +2.70    +2.52    +2.40

The last row is the training stream's own: how much more often than chance
a tied pair's `b` stands exactly that many words after its `a`. **In the
text the tie barely fades**: a nat from one word back to thirty.

## Read 1 -- the earlier word swapped out

`b`'s cost in the text as it stands, and with `a` swapped for a stand-in of
the same length and commonness that the book does not tie to `b` (two
stand-ins a meeting). Worth is what `a` standing there takes off `b`. The
untied meetings price what a swap breaks, and it is a great deal up close
(1.9 nats at 20M and 3.7 at the 260M one word back, nothing past eight):
pair worth is tied less untied.

    pair worth, nats (standard error)     1            2            3-4          5-8          9-16         17-30
    nano5m_v3_webblend                +3.34 (.17)  +1.69 (.12)  +0.56 (.05)  +0.37 (.04)  +0.27 (.03)  +0.17 (.02)
    nano5m_v3_webblend_seed2          +3.03 (.17)  +1.77 (.12)  +0.55 (.05)  +0.31 (.03)  +0.27 (.03)  +0.18 (.02)
    nano20m_v3_webblend               +3.27 (.18)  +1.76 (.12)  +0.62 (.05)  +0.40 (.04)  +0.28 (.03)  +0.16 (.02)
    nano20m_v3_webblend_seed2         +3.28 (.17)  +1.88 (.13)  +0.56 (.05)  +0.36 (.04)  +0.29 (.03)  +0.19 (.02)
    nano100m_v1          (reference)  +3.79 (.21)  +2.63 (.16)  +1.00 (.09)  +0.48 (.05)  +0.31 (.04)  +0.23 (.03)
    corn_jr_260m         (reference)  +3.31 (.21)  +2.71 (.18)  +1.11 (.11)  +0.44 (.06)  +0.33 (.04)  +0.20 (.03)

    r: over the 260M's, same meetings     1            2            3-4          5-8          9-16         17-30        q
    nano5m_v3_webblend                1.01         0.62         0.51         0.84         0.83         0.87         0.82 (0.65-1.05)
    nano5m_v3_webblend_seed2          0.92         0.65         0.50         0.72         0.80         0.93         0.87 (0.69-1.14)
    nano20m_v3_webblend               0.99         0.65         0.56         0.92         0.84         0.80         0.85 (0.67-1.08)
    nano20m_v3_webblend_seed2         0.99         0.70         0.51         0.82         0.87         0.95         0.88 (0.68-1.12)
      95% interval, seed 1337         0.89-1.10    0.58-0.72    0.46-0.69    0.72-1.21    0.68-1.06    0.59-1.12
    nano100m_v1                       1.15         0.97         0.90         1.10         0.94         1.16         0.82 (0.66-1.02)

`q` is r at 9-16 over r at 1. The share of tied meetings where `a` helps at
all is 0.82 and 0.80 at 9-16 for the 20Ms and 0.70 for the 260M, and the
20M's median worth is the higher from five words back on (0.13 against 0.08
at 9-16).

## Read 2 -- the context cut

A swap prices what one word adds beyond everything else in the context, and
far back the words between carry the same topic; the smoke showed pair
worth falling steeply in both models beside a count that barely fades. So
the same meetings were read with the context cut to the last k pieces.

    b's cost, tied meetings, nats    k=1     k=2     k=5     k=10    k=20    k=40    k=128    pieces 2-10   11-40   41-128
    nano5m_v3_webblend               9.12    7.65    6.59    6.13    5.91    5.80    5.76     +2.99         +0.33   +0.04
    nano5m_v3_webblend_seed2         8.71    7.62    6.58    6.16    5.90    5.79    5.76     +2.55         +0.37   +0.03
    nano20m_v3_webblend              8.84    7.44    6.35    5.87    5.60    5.46    5.43     +2.97         +0.41   +0.03
    nano20m_v3_webblend_seed2        9.05    7.50    6.36    5.89    5.62    5.49    5.45     +3.17         +0.40   +0.04
    nano100m_v1                      8.66    7.11    5.63    5.03    4.69    4.55    4.49     +3.64         +0.47   +0.07
    corn_jr_260m                     8.43    6.55    4.77    3.96    3.52    3.34    3.29     +4.47         +0.63   +0.05

    t: band worth over the 260M's    2-10               11-40              tq
    nano5m_v3_webblend               0.67 (0.65-0.69)   0.53 (0.46-0.60)   0.79 (0.69-0.90)
    nano5m_v3_webblend_seed2         0.57 (0.55-0.59)   0.59 (0.53-0.66)   1.04 (0.92-1.18)
    nano20m_v3_webblend              0.66 (0.65-0.68)   0.66 (0.59-0.73)   0.99 (0.88-1.11)
    nano20m_v3_webblend_seed2        0.71 (0.69-0.73)   0.63 (0.57-0.71)   0.90 (0.79-1.01)
    nano100m_v1                      0.81 (0.80-0.83)   0.75 (0.68-0.83)   0.93 (0.83-1.03)

Pieces 41 to 128 back are worth 0.03 to 0.07 nats to every model here.

## The pre-registered rows

* **R holds.** Every bucket has 400 and 400, and the 260M's pair worth is
  six standard errors or more above zero in each.
* **D fails.** q is 0.85 and 0.88, over the 0.8 line at both seeds; the
  intervals (0.67 to 1.08, 0.68 to 1.12) do not reach 0.5. Predicted 0.3 to
  0.6: wrong.
* **T fails.** tq is 0.99 and 0.90. Predicted between: wrong. t(2-10) was
  called near 0.7 and read 0.66 and 0.71; t(11-40) was called near 0.45
  and read 0.66 and 0.63.
* **Z fails**, as predicted: the 20Ms' pair worth is over nine standard
  errors above zero at 9-16 and at 17-30.
* **The 5Ms share the 20M's shape, as predicted. The 100M does not**: it
  stands level with the 260M at every distance.

## Where he does fall short (a cause read, not gated)

* **Two to four words back.** r is 0.65 and 0.70 at two words and 0.56 and
  0.51 at three to four, with intervals clear of 1, and back at 0.8 to 0.9
  beyond. The gap is a few meetings each worth a great deal: the 40
  meetings of 400 where the 260M gains most carry 37% of the bucket's gap
  at two words and 61% at three to four.
* **Read by hand, those meetings are set phrases.** `shed` to `light` (the
  260M's cost for `light` is 0.02 nats, the 20M's 6.96), `making` to
  `comeback` (0.13 against 7.31), `threatened` to `extinction`, `ring` to
  `bell`, `serve` to `purpose`, `within` to `limits`, `differences` to
  `similarities`, `doctors` to `nurses`, `unless` to `otherwise`, `hasn't`
  to `yet`, `interesting` to `boring`, `winds` to `mph`. In each the 260M
  has the word all but written and the swap costs it 5 to 13 nats; the 20M
  gets a nat or two from `a` and still pays 5 nats or more for `b`. What he lacks
  there is the earlier word *together with* the one or two between.
* **Most of the gap is in the last five pieces.** On the tied meetings the
  260M is 0.41 nats ahead of the 20M (seed 1337) with one piece of context,
  1.58 with five, 1.91 with ten and 2.15 with all 128: three quarters of
  what separates them is made out of five pieces.
* **Far back the two models differ meeting by meeting, not in amount.** The
  two 20Ms' worths agree at 0.82 to 0.92 across meetings in every bucket;
  a 20M and the 260M at 0.34 to 0.65. At 9-16 words the ten read by hand
  move little in either model (`heart` to `kidney`, `content` to `website`,
  `search` to `answer`: under 0.1 in both), and where one moves it is as
  often the 20M (`written` to `novel`, +1.44 against 0.00).
* **By how often the pair met**, at 9-16 words: 0.24 against the 260M's
  0.22 for pairs met 30 to 100 times, 0.33 against 0.41 for 100 to 400,
  0.27 against 0.48 for 400 or more (62 meetings). Printed; not a result.

## What it licenses

By the pre-registration, its second outcome: **distance is not where he
falls short.**

* **The credit-path reading loses its evidence.** It predicted a 20M that
  loses its standing against the 260M as the earlier word moves back, and
  he does not, on either read. The wide lane beside his blocks was to be
  built on D holding and is not built on this. Its remaining support is
  finding 227's cause read of the book speaking on his scores.
* **Finding 228's clue was about the count, not about him.** A count
  answers more fields the further it looks because the text's ties barely
  fade (+3.46 to +2.40 nats over thirty words). That says where the
  knowledge is on offer. It does not say he reads far worse than a model
  that has it: he uses a tied word nine to sixteen words back about as well
  as the 260M does. Finding 228 is amended.
* **What separates a small model from the 260M on these words is what it
  makes of the last few pieces**: a word two to four back bound with the
  ones between into a phrase. That is the near question, which the
  next-piece lesson pays for directly, and it is where size and text buy
  the most.
* **This instrument does not see the ruler's gap.** The 100M is level with
  the 260M on every row here and reads 80 fields to the 260M's 101, beside
  the 20M's 78 and 76 (finding 221). Whatever the fields ask for, it is not
  what an earlier word is worth by distance in running text.
* **The read is an instrument worth keeping.** 800 meetings a bucket give
  standard errors of 0.02 to 0.04 nats from five words back, the two seeds
  of a size agree, and it trains nothing. It is unguarded: its own checks
  are the count against a plain loop, the batched read against five single
  windows and each swap changing only `a`'s pieces, so by rule 28 these
  numbers are bounds through `scripts/probe_far_read.py`.

**What it does not settle.** Why the fields stall: this removes distance and
puts nothing in its place. The ruler's own pairs -- a phrase's content word
and the field's name -- read this way in running text, which would say
whether he holds those ties and cannot use them through the ruler's frame,
or does not hold them. Whether the 260M ever read this held-out text
(it read other tokens; unchecked). The 100M at the same text: `nano100m_v1`
read another mix. Contexts past 128 pieces. Stand-ins of the same length
and commonness, two a meeting: a third would say how much of the near
buckets' spread is the stand-in.
