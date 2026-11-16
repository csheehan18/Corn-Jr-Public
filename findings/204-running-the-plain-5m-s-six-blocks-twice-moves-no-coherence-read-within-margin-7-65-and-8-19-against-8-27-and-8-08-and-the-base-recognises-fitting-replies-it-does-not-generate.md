# Running the same layers twice moves nothing measurable at 5M

**Full result:** The plain 5M's six blocks run twice -- twelve deep, nothing given up, 6,950,656 parameters against 6,950,144 -- move no coherence read at either seed: the within-category reply-fit margin of the new swap test reads 7.65 and 8.19 against the control's 8.27 and 8.08 (the gate was 8.57 at both), the blind hand read of 148 greedy replies 65 and 71 against 70 and 55, and the language rows are inside the control pair or barely past it (conversational 0.5560 and 0.5522 against 0.5579 and 0.5599): the pre-registered row (n), nothing measurable, against a predicted (c). The rulers, the rare-word gap and word choice are level. Read beside it on the control: the plain 5M picks the fitting reply over a swapped one in 91-96% of pairs while its greedy replies fit about half the time -- most of what fails in his replies is what he generates, not what he recognises

**Cost:** the swap test (148 hand-written replies, two pair kinds) and its floor on four checkpoints, a two-point 1,000-iteration lr check, the pre-registration 12:06-12:14 on 2026-10-22 (eced6ec); the chain 12:14-12:38, 23.4 min (both runs 530 and 532 s, contended at 37%, a bound); the blind hand read of 592 replies inside it. ETA 25 min of card, actual 23.4 plus 3.6 for the lr check.

**The question** (owner, 2026-10-22: "let's aim at coherence first"). Finding
202 changed three things at once and gave up half the dense block weights.
This is its depth piece alone: `corn/wordloop.py` with `n_layer=6,
n_loops=2`, no table, no surprise input -- every block of the control, run
twice, plus a 256-vector a pass. Turning "numb face" + "dentist" into *bad
news* takes steps; this gives the same weights twice as many. The lr check
(1,000 iterations, probe only -- not on disk) read 3.261 at 3e-3 and 3.422
at 1.5e-3, so the control's 3e-3 stands. Compute 1.27x the control's step.

**The swap test** (`scripts/probe_reply_swap.py`, new). The blind hand read
separates only large differences (the control's two seeds differ by 15 of
148). Each of the 148 messages has a hand-written fitting reply; each is
paired with three messages of other categories (*across*) and three of its
own (*within*: a cancelled flight against a sick cat), and the margin
lp(r1|m1) + lp(r2|m2) - lp(r2|m1) - lp(r1|m2) cancels how likely a reply is
in general. Its margins agree across the control's seeds to 0.2-0.3 nats
and fell 1.3-1.6 on finding 202's arm with its language loss.

## The read

    read                                      base s1   base s2   reuse s1   reuse s2
    swap, within: share right / margin        0.91 8.27 0.91 8.08 0.91 7.65  0.91 8.19
    swap, across: share right / margin        0.96 11.48 0.95 11.15 0.96 11.16 0.95 12.18
    coherence, blind hand read (of 148)       70        55        65         71
    lm narrative / web / conversational       0.4864 / 0.9512 / 0.5579   0.4883 / 0.9522 / 0.5599
                                                                  0.4867 / 0.9505 / 0.5560   0.4837 / 0.9446 / 0.5522
    final val loss (training log)             2.608     2.641     2.610      2.623
    knowing, matcher: admits unk / answerable 7 / 11    13 / 17   5 / 10     18 / 17
    held-out rare-word gap                    7.896     8.064     7.913      7.702
    10-30 first piece (choosing the word)     7.93      8.03      8.04       7.95
    fields / wishes 192 / plain lift          0.56/0.35/0.49  0.53/0.32/0.47  0.50/0.33/0.48  0.60/0.35/0.47

(`evals/results/reply_reuse__*`, `nano5m_reuse__*`; the hand labels and the
blind key are committed beside the replies. Knowing is the matcher's count,
not hand-labelled for this arm.)

**The gates, as registered.** Fluency: holds. Coherence: no -- 7.65 is
under the control. Language (conversational under 0.5549 at both seeds):
no -- 0.5560 is not. **(n)**.

## Read by hand

The 296 reuse replies fail as the control's do -- "That's great!" to a
spilled coffee and a missed bus, "I don't know, I just feel like I'm not
good enough" to an open question, "What? Why?" to news of a baby -- and pass
on the short generic forms ("What happened?", "What's wrong?", "I'm doing
well, thank you"). The control's replies, identical by greedy decoding to
finding 202's read, were labelled the same on all 148 of each seed in the
second blind read (70 and 55 both times; the first read was an hour
earlier, so memory is not excluded).

## Recognising against generating

Against a swapped reply, the plain 5M prefers the fitting one in 91% of
pairs where only the content tells them apart and 95-96% where the mood
does; left to write its own reply greedily, it writes one that fits 55-70
times in 148. The fitting reply is in its distribution; greedy decoding
picks the commonest opening ("That's great!", "What? Why?", "I don't know,
I just feel..."), which is the generic-reply problem of neural dialogue
models (Li et al. 2016, "A Diversity-Promoting Objective Function for
Neural Conversation Models": rank a reply by how much the message raises
it, not by how likely it is). The swap test's own margin is that quantity.

## What it licenses

* **Depth by reuse is not the lever at 5M**: same weights twice as deep,
  same text, nothing moves outside the seeds' spread.
* **The next read is decoding, no training**: generate by how much the
  message raises each candidate, not by raw likelihood, on the control's
  checkpoints, read by the same blind hand read. If it moves coherence by
  more than a seed does, the failure the owner named lives in the runtime's
  choice of words more than in the weights.

**What it does not settle.** Any size above 5M; more passes than two; the
knowing read by hand for this arm.
