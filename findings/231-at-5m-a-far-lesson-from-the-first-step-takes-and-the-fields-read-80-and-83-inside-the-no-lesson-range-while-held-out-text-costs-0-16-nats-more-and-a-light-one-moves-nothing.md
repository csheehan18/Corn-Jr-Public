# A far lesson in training takes, costs reading, and lifts nothing clearly

**Full result:** A 5M trained from its first step with the far lesson beside its reading -- 2,048 pairs a micro-batch off the reading's own scores, which of two pieces stands 2 to 40 ahead, a piece's general likelihood cancelling -- learns the lesson at weight 0.5 (far pairs right on held-out text 0.711 and 0.700 against its controls' 0.631 and 0.627) and reads 80 and 83 of the ruler's 141 fields: a direction by the registered row, and inside what twelve 5Ms with no far lesson read (65 to 84, the controls 79 and 75). It pays 0.160 and 0.156 nats a token on held-out text, three and a half times the gap between a 5M and a 20M (0.045, finding 197), on every source. At weight 0.1 the text costs 0.017 and 0.019, the lesson is half learned (0.665 and 0.663) and the fields read 71 and 74. The one read nobody called -- the light cell's wishes at 72 and 80 of 192, at and over the top of the no-lesson runs' 61 to 72 -- was registered for replication and failed it: two more seeds read 69 and 61.

**Cost:** lesson, guard 109, four configs and reader committed with the pre-registration at 16:35 on 2026-11-13 (81507f7), after a read of the twelve no-lesson runs (164.3 s of card) and a 250-iteration smoke in a scratch directory (58.6 s); the four runs trained 380.8, 381.8, 381.8 and 384.2 s (the controls 350.0 and 353.9), 1,763.5 s for the chain with its read; the replication, registered at cf7025a after the four were read, 354.7 and 354.6 s, 934.4 s with its read; the repetition cause read 74.4 s, contended. ETA about thirty minutes of card for the four runs and their read; 29.4.

**The question** (owner, 2026-11-13: "Yes do the 5M"). Findings 229 and 230
asked a trained 20M for a word from where its neighbour stands and found two
stores: what a far step writes, the far question reads, and the next-piece
question does not. No step on a trained trunk can say whether the stores are
two when both questions are asked from the first step. This is that arm, at
the size that reads the ruler as the 20M does (finding 197) and trains in six
minutes. The pre-registration is `configs/nano5m_v3_webblend_far.py`'s
docstring; the mechanism is `corn/far.py`.

## What "no effect" looks like at 5M (read first)

The two controls and ten other 5Ms on this text whose arms moved nothing on
the ruler (findings 198 to 206), read as finding 221 read the 20Ms:

    fields of 141      65 to 84, mean 74.5, sd 5.0
    wishes of 192      61 to 72, mean 64.7, sd 3.0
    far pairs right    0.621 to 0.632 on held-out text, no lesson at all

A 5M's fields move five items from run to run, and its wishes three. The
rows were set against that: F holds only at 85 on both seeds.

## The read

    run                        wishes   2nd 96   fields   held-out, nats a token                  far pairs right   val
                               (192)             (141)    web / plain / conversation / narrative
    control, seed 1337         68       34       79       3.893 / 4.028 / 2.129 / 2.092           0.631             2.608
    control, seed 1338         62       33       75       3.905 / 4.038 / 2.137 / 2.108           0.627             2.641
    FAR (0.5), seed 1337       69       40       80       4.068 / 4.202 / 2.287 / 2.223           0.711             2.740
    FAR (0.5), seed 1338       68       32       83       4.077 / 4.202 / 2.291 / 2.243           0.700             2.766
    LIGHT (0.1), seed 1337     72       34       71       3.917 / 4.048 / 2.141 / 2.104           0.665             2.620
    LIGHT (0.1), seed 1338     80       43       74       3.924 / 4.060 / 2.160 / 2.122           0.663             2.654
    LIGHT, seed 1339           69       34       78       3.918 / 4.055 / 2.148 / 2.112           0.663             2.674
    LIGHT, seed 1340           61       30       77       3.915 / 4.047 / 2.146 / 2.120           0.660             2.631

The controls reproduce their saved ruler files (asserted). On its own
training batches the heavy lesson gets 0.84 of its pairs right by the end
(`far_log.jsonl`); the held-out windows are half as long and drawn evenly
from four sources.

## The pre-registered rows

* **T: the heavy lesson took, the light one by the line did not.** +0.080
  and +0.072 over the controls for FAR; +0.034 and +0.036 for LIGHT, under
  a line of 0.05 and three times the no-lesson runs' whole spread. Predicted
  0.08 to 0.15 and 0.03 to 0.08.
* **F: a direction for FAR, fails for LIGHT.** 80 and 83, where the row
  held at 85 and failed at 82 on both; 71 and 74. Predicted 76 to 84. Seed
  1338 is eight over its control and one under the best no-lesson run;
  seed 1337 is one over its control.
* **W: printed.** FAR 69 and 68, inside the spread. LIGHT 72 and 80 -- see
  the replication.
* **L: FAR costs him, LIGHT is little.** +0.160 and +0.156 nats a token on
  the mean of four sources (web +0.17, plain web +0.17 and +0.16,
  conversation +0.16 and +0.15, narrative +0.13); +0.017 and +0.019.
  Predicted 0.01 to 0.04 for FAR: wrong by four times.

## The replication (registered after the four were read)

LIGHT's wishes, 72 and 80, sat at and over the top of the twelve no-lesson
runs, and the pre-registration had called them flat. Two more seeds, one
row -- both at 73 or more -- and a prediction that it would not hold:

    W2   seeds 1339 and 1340: 69 and 61 wishes   ->   FAILS

Four seeds of the light lesson read 72, 80, 69 and 61. It was the draw.

## Read by hand

* **What he writes.** Six openers a run, one seed. FAR's chat replies read
  like the control's. Its web continuations loop on what was just said: "The
  cheapest way to travel across Europe is in New York, New York, and New
  York. / Martnet, Illinois, a professor of professor of science and
  science, is a professor of psychology"; "The first study was developed to
  the science of Earth, which was the first study, has an important study".
  LIGHT reads like the control.
* **Counted afterwards (a cause read).** Over 40 held-out web openers, words
  of four letters or more that repeat one of the twenty before them: the
  text itself 5.7%; the controls 25.4% and 26.0%; FAR 31.9% and 28.3%; LIGHT
  27.2%, 27.2%, 28.9% and 25.8%. A 5M already says things again four times
  as often as the text does; the heavy lesson adds two to six points. The
  lesson pays him to score what is in the air, and what is in the air is
  what he has just said.
* **The fields that change side at seed 1337**: 18 gained, 17 lost -- a
  retrain's worth of churn (finding 222), one item net. The gains are the
  phrase's content ("that fits in a small pocket" to `size`, "I can play
  with three friends" to `players`); so are the losses ("near the beach"
  from `location` to `rating`).
* **Stock answers.** The controls' commonest wrong field is `price` (8 and
  7 of 62 and 66 misses); each of the four registered far runs' is `rating` (5 to 7). The default
  moved; it did not go.

## What it licenses

By the pre-registration: **the lesson takes, the fields are a direction
inside the no-lesson range, and the reading pays -- the two questions
compete for the same scores.**

* **Asked both questions from the first step, he does not learn the fields
  a count learns.** The heavy lesson may be worth a few items (81.5 over two
  seeds against a no-lesson mean of 74.5 with sd 5.0); it is not worth 85,
  and it is bought with more reading loss than separates a 5M from a 20M. A
  lesson a fifth as heavy is nearly free and buys nothing.
* **Sharing the scores is the cost, and not sharing them is two stores.**
  Read off the reading's own scores, "coming within forty" and "coming
  next" pull the same numbers two ways, and the reading loses. A separate
  head would spare the reading and is, by construction, the second store of
  findings 229 and 230.
* **This closes the training side of finding 221's idea for a lesson of
  this shape.** Seven reads in one day -- the press weighted by the book
  (222), one hard press (224), the press held against the swap (225), kept
  (226), asked from afar (229), kept from afar (230), and from the first
  step (231) -- and each time what he keeps is what the next-piece question
  pays for. The book's knowledge is real (91 wishes and 95 fields, ruler
  unread, finding 227), it is far-apart knowledge (finding 228), and
  nothing here put it in him by gradient.
* **At 5M, two seeds are not an instrument for small effects.** The
  no-lesson spread is 19 fields wide. The light cell's wishes looked like a
  result at two seeds and were gone at four; the replication cost thirteen
  minutes and belongs in any 5M arm that reads the ruler.

**What it does not settle.** A weight between 0.1 and 0.5. A separate head
on a shared trunk, read at the next piece. A 20M, where the reading has
more room to pay from. Whether the few items at weight 0.5 are real: four
more seeds would say, and at this price nobody needs to know.
