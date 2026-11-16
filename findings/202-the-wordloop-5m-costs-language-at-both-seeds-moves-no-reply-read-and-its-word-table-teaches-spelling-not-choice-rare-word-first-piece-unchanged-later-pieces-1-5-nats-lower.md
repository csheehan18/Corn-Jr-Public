# A shape built for small models cost language and taught only spelling

**Full result:** At the plain 5M's parameter count and on its text, the wordloop arrangement -- a hashed table for the word so far, three blocks run four times, and his own surprise read back as an input -- is worse on every language row at both seeds (narrative 0.5111 / 0.5069 nats a byte against 0.4864 / 0.4883, web 0.9690 / 0.9654 against 0.9512 / 0.9522, conversational 0.5799 / 0.5773 against 0.5579 / 0.5599): the pre-registered row (d), the arrangement costs language. No reply read moves: blind by hand it answers 51 and 65 of 148 everyday messages against the base's 70 and 55, and admits not knowing on unanswerable questions more than on answerable ones by +2 and +2 against -4 and +1. Its held-out rare-word gap falls far (7.13 / 7.06 against 7.90 / 8.06), but the whole fall is in spelling the word out once its first piece is chosen (later pieces 8.54 / 8.48 nats against 10.01 / 10.13 at 10-30 sightings); choosing the word is unchanged (first piece 8.01 / 8.04 against 7.93 / 8.03), and how much more he expects a rare word where it fits shrank (1.99 / 2.02 against 2.25)

**Cost:** design, `corn/wordloop.py`, its guard, the reply instrument and its balancing, the base floor and the pre-registration 10:38-10:51 on 2026-10-22 (b9abcef); both runs 10:51-11:17 (770 and 777 s, 1.8x the plain step, contended at 35-46%, a bound); the reply read crashed on prompts under eight tokens, fixed and guarded (6549667), reads 11:25-11:30; blind hand reads of 592 replies and 320 knowing answers and the pieces read ~25 min. ETA 28 min of card, actual ~35.

**The question** (owner, 2026-10-22: "a 20M model could be decently
coherent with the right architecture"; the target "if I can message it
anything and it replies coherently ... if it doesn't know something it can
tell me ... but it should vary how it tells me"). After four findings on
reading (198-201), the other half: a shape built for a small model's
shortages. `corn/wordloop.py` argues each piece:

    word table   a 36,548 x 64 hashed table for the word so far, read at a
                 word's second piece onward (rare words average 3.25
                 pieces, common ones 1.00), projected to the width from zero
    reuse        3 distinct blocks run 4 times: 12 deep from half the block
                 parameters, the rest paying for the table
    surprise in  a no-gradient first pass bins each token's surprise into 16
                 levels; the second pass reads them (finding 188: his
                 surprise picks out the unfamiliar word at AUC 0.87, and the
                 plain trunk throws it away)

6,950,144 parameters, the plain 5M's to the parameter; the same text to the
byte; compute not matched (231k tokens a second against 420k). Predicted
(w): rare words improve, replies do not move.

## The read

    read                                       base s1   base s2   wordloop s1   wordloop s2
    lm narrative (nats a byte)                 0.4864    0.4883    0.5111        0.5069
    lm web                                     0.9512    0.9522    0.9690        0.9654
    lm conversational                          0.5579    0.5599    0.5799        0.5773
    coherence, blind hand read (of 148)        70        55        51            65
    knowing: admits unknowable / answerable    5 / 9     11 / 10   10 / 8        9 / 7
      difference (hand, blind)                 -4        +1        +2            +2
    variety: admitting samples of 200          21        36        28            33
      distinct openings among them             20        29        25            29
    held-out rare-word gap                     7.896     8.064     7.128         7.055
      10-30 first piece / later pieces         7.93/10.01 8.03/10.13 8.01/8.54   8.04/8.48
    word fit, 10-30 (wrong less right)         2.25      2.25      1.99          2.02
    fields / wishes 192 / plain lift           0.56/0.35/0.49  0.53/0.32/0.47  0.46/0.33/0.50  0.57/0.34/0.46

(`evals/results/reply_wordloop__*`, `nano5m_wordloop__*`; the hand labels and
both blind keys are committed beside the replies.)

**The gates, as registered.** Fluency: falls -- all three rows, both seeds,
above their lines (0.4913, 0.9552, 0.5629). Coherence: no -- the arm seeds
sit inside the base pair. Knowing: no -- +2 at both seeds is above the base
pair but not by the floor of 4. Words: yes. The first row that holds is
**(d)**. Unreadable: no -- the guard passes, both runs finished, the keys
were opened after every verdict.

## Read by hand

**Coherence** (592 replies, blind, the four runs shuffled per message). The
two shapes fail the same ways: "That's great!" to bad news ("I spilled
coffee all over my keyboard" -> "Oh, that's great! What did you do?" from
three of four runs), a stock self-doubt line to any open question ("I don't
know, I just feel like I'm not good enough" to *what's your favourite
season*, *how do I start running*, *what goes well with tea*), "What?
Why?" to news good or bad. What passes is short and generic: "What
happened?", "What's wrong?", "I'm doing well, thank you. How are you?". The
base's own two seeds differ by 15 of 148, so this instrument separates only
large differences at two seeds.

**Knowing.** Most "I don't know" replies are the self-doubt line, not an
admission about the thing asked, and were labelled not admitting on both
sets alike. The real admissions are short and rare in every run ("No, I
haven't." to *have you tried the new Tornic phone*; "I don't know. I just
got here." to *who won the Pellish Cup*). Names and "my" are balanced 20/20
and 10/10 in each set, so no run could score by reacting to an unfamiliar
name.

**Variety.** Every run's admissions open "I don't know" most often (8-17 of
21-36), as the training text's do (the corpus count in b9abcef: about
70% of its not-knowing replies).

## Why it cost language

The design paid for the table and the depth with half of the dense block
parameters (2.36M of 4.73M). The table speaks only at the inner pieces of
multi-piece words -- a minority of positions -- and the pieces read shows
what it learned there: to finish a word once started. Choosing the word,
which is what the block weights carry, did not move, and the dense capacity
that every other position uses was halved. Reuse adds steps, not storage.
The learning rate was the plain 6-block shape's (3e-3), not swept for a
12-deep reused one.

## What it licenses

* **Not this trade.** Giving up dense weights for a word table costs a 5M
  more than the table returns, and the table's return is spelling.
* **The three pieces, separately, without the trade** -- the pre-registration's
  leave-one-out, re-cut so no arm gives up dense capacity: reuse alone
  (the 6 plain blocks run twice, 12 deep, parameters matched); the surprise
  input alone on the plain 5M (+4,352 parameters); and, if the table is
  tried again, beside the plain blocks and keyed for choosing (the previous
  word into the next) rather than spelling. Each with an lr sweep point.
* **The reply read is noisy at 148 messages**: seed spread 15. A shape that
  matters for coherence has to move it by more than that, or the read needs
  more messages.

**What it does not settle.** Which piece cost the language (the three moved
together by design); whether a swept learning rate closes the gap; any size
above 5M; whether the surprise input does anything on its own -- its
knowing direction (+2, +2) is inside the floor.
