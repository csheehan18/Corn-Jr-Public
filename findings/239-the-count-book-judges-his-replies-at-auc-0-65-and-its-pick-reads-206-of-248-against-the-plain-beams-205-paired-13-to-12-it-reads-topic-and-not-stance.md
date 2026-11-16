# The count book judges replies a little, and picks no better

**Full result:** Finding 221's book -- counted lines, PPMI at window 10, nothing re-tuned -- scores each of finding 220's 744 hand-labelled 260M replies by how much its message raises the reply's content words over any other message, with every word the message itself used struck out. It separates passing replies from failing ones at AUC 0.652 over the 663 it scores (it abstains on 11%), and picking the highest-scoring of greedy, plain beam and self-judge per message passes 206 of 248, against the beam's 205, greedy's 194 and his own judgment's 197. Both pre-registered rows land live, B1 by 0.002 and B2 by one message; paired against the beam the pick wins 13 messages and loses 12, so it is level with the beam. Without the swap subtraction it reads 0.667 and 207. Echo among its picks rises from 7 to 11. Read by hand, it rewards a reply that names the topic and is blind to its stance.

**Cost:** pre-registered and committed at 21b9000 before either read was computed; started 15:11:55 on 2026-11-15; read 2 took 6.6 s under the GPU lock (the tally, 482 pages, selfcheck passed); hand read and paired count a few minutes; written to 15:20.

**The question** (owner, 2026-11-15: "Run both probes"). Finding 220: his
own judgment, used to pick among his drafts, rewarded replies that pointed
at the message and added nothing. Finding 221: a book of counted lines, no
weights, reads word meaning level with the 260M. Can an unlearned reader
he cannot flatter tell a reply that fits its message from one that does
not -- and does choosing by it improve what he says? The pre-registration
is `scripts/probe_read_write.py`'s docstring, read 2.

## The read

Content words are words outside the stream's 100 commonest. `fit` is the
mean PPMI line from the message's content words to the reply's remaining
ones; `rel` subtracts the reply's mean fit to the other 247 messages.

    score  B1 AUC   scored      B2 pick   paired vs beam   echo in picks
    rel    0.652    663/744     206/248   13 : 12          11 (beam 7)
    fit    0.667    663/744     207/248   13 : 11          10
    for reference: greedy 194, plain beam 205, self 197, best of three 225

By exam: the pick passes 129 of the 148 (beam 126) and 77 of exam 2's 100
(beam 79). **Prediction**: B1 0.58-0.66 (right), abstain 30-45% (wrong: 11%),
B2 200-207 (right), B a bound (wrong by a hair: live on the letter of both
lines).

## The hand read

Twenty disagreements with the beam where the labels differ, read before any
number above was quoted. **Where the book wins it is rejecting evasion**:
"I don't know, what is it?" to *Do you have a favourite food?* loses to
"I love sushi!"; "I don't know. I just do." to *What makes you laugh?*;
"I don't know. What do you mean?" to a question about cheering up a
friend. A reply that dodges has no content word that the message raises.
**Where it loses it is rewarding topic with the wrong stance**: to *Someone
stole my bike*, "I didn't steal your bike. You're just paranoid." scores
+0.671, highest of three -- the same reply his own judgment picked in
finding 220, and for the same reason; `steal` is not `stole`, so striking
the message's words does not catch it. "What? You're not going to eat
that?" to leftover pizza for breakfast (+0.893); "You're not going to be
swimming this year, are you?" to wanting to learn to swim; "Why not?" over
"it depends" on telling a friend her cooking is bad. Each names what the
message is about and says the wrong thing about it.

## What it licenses

**The book knows what a message is about and not what to say about it.** It
judges fit at about the level of a weak judge -- 0.65, where the 5M's
trained reply judge read 0.79 on the first word (finding 214) -- without one
trained number, and its preference does not improve what he writes: one
message over the beam, 13 : 12 paired. The two failure kinds it shares with
his self-judgment (220) are topic without stance and near-echo through a
different word form. As a veto on evasive replies it has a use the hand
read shows; as a chooser it is level. A sharper book would need lines for
stance -- who did what to whom -- which co-occurrence does not hold. One
checkpoint, one labeller, 248 messages, three decoders that agree on most
messages so only about 80 picks can move.
