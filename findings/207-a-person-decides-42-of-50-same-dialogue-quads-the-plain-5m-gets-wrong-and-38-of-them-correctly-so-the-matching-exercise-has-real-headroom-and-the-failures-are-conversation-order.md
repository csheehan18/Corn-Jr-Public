# The pairs he fails are mostly decidable: he loses the conversation's thread

**Full result:** Matching blind -- two messages from one conversation, their two replies shuffled, the answer key closed -- a person decides 42 of 50 same-dialogue quads the plain 5M (seed 1) gets wrong, and 38 of those correctly; on 25 random quads (which the model mostly gets right) 23 decided, 23 correct. So three quarters of the model's same-dialogue failures (38 of 50) are pairs a reader can settle, and only 8 have nothing that decides them -- the opposite of finding 206's hand read of six quads, which is corrected here. What decides the quads the model fails is mostly the conversation's order (20 of 38: which reply sets up which message -- "Why did you choose Max as your new name?" is what "I don't really know, it just felt right" answers), then a picked-up detail (10), then a direct question answered (7); what decides the ones it gets right is mostly a direct question answered (16 of 23)

**Cost:** `scripts/probe_quad_handcount.py`, the draw (2,000 quads on both control seeds, 1 min of card, contended) and the blind read of 75 quads, 14:15-14:35 on 2026-10-22. ETA 20 min, actual ~20.

**The question** (finding 206's licence, the owner: "hand count, really
see what you can learn"). The matching exercise did not take at a tenth of
the conversational reading, and six hand-read quads suggested much of the
control's error has no right answer. If so, a heavier weight would train
on noise. This counts it properly: blind, with a baseline.

**The draw.** 2,000 same-dialogue quads (seed 7, used by no training run);
the seed-1 control gets 286 wrong (14.3%). Fifty of those and 25 random
quads, shuffled together; per quad the two messages under A and B and the
two replies under 1 and 2 in a coin-flipped order. The reader writes which
reply answers A (or `?`) and what decided it, before the key is opened
(`evals/results/quadcount__*`).

## The read

    quads                        decided   right of decided   right of all   seed 2 also wrong
    control wrong (seed 1), 50   42        38                 0.76           26
    random, 25                   23        23                 0.92           1

    what decided a correct call      control wrong   random
    conversation order               20              0
    picks up a detail                10              7
    answers a direct question         7              16
    who is speaking                   1              0

## Read by hand

**Conversation order** is the large class: a reply that the *other* message
goes on to answer or follow. *A: "I used them this morning ... can't
remember where." B: "I checked my room and they're not there."* -- "Okay,
so we know you had them this morning. Where did you go after you left your
room?" answers A, and "When was the last time you remember using them?" is
what A itself answers. *A: "Okay, bye." B: "Aww, I missed you too. I'm
almost home."* -- "Bye." and "Great! I can't wait to see you." Each
needs the turn's place in the exchange, not just its topic. The model
handles the question-and-answer kind (the random quads it gets right are
mostly that) and loses the thread.

**The undecidable eight** are real: two "you're welcome" turns against two
thank-yous, two agreeing turns in a debate, two congratulations on a win --
the pattern finding 206 saw, at a sixth of the failures, not most of them.

**Four calls were wrong** -- order cases where both sequences read
plausibly; a person's ceiling on these quads is below 100%.

## What it licenses

* **The exercise has headroom**: about three quarters of the control's
  same-dialogue misses are decidable, so a heavier weight trains mostly on
  signal, not noise. Finding 206's "(u) at this weight" stands; its reason
  does not.
* **What to aim it at is the thread of a conversation**, not its topic:
  the failures are about where a turn sits, which is the owner's coherence
  target in miniature -- answering *this* message, not the conversation.
* **Next by this count**: the exercise at a heavier weight, same-dialogue
  quads only, read by the same take read, the swap test beside, and the
  blind reply read.

**What it does not settle.** One reader, one seed's failures; whether a
lesson on the thread carries into writing.
