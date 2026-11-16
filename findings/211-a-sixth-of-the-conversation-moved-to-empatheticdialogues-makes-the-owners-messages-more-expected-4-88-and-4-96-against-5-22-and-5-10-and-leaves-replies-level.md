# Real everyday dialogue moves him toward how the owner talks

**Full result:** With a sixth of his conversational reading moved from SODA to EmpatheticDialogues (3.4M of 19.6M tokens; the budget and every other source the control's), the 5M finds the owner's own typed messages less surprising -- 4.880 and 4.963 nats a token against the control's 5.218 and 5.105, both under the pre-registered 4.992 -- with narrative and web holding (0.4876 / 0.4898 and 0.9520 / 0.9568 against lines of 0.4913 and 0.9552, the web row over at one seed only): the pre-registered row (r), real everyday dialogue moves him toward how the owner talks. His replies stay level at 5M, as predicted: 64 and 66 of 148 coherent by a blind hand read against 70 and 55. Held-out SODA text costs what a sixth less SODA should (lm conversational 0.5671 / 0.5717 against 0.5579 / 0.5599)

**Cost:** `scripts/prepare_empathetic.py`, the mix spec, `scripts/probe_register_surprise.py` and its floor, the pre-registration 15:35-15:57 on 2026-10-22 (5387271); a first build byte-tokenised by `prepare_mix.py`'s default and refused by the run in 3 s, rebuilt with `--tokenizer bpe8k` (56ea80d); the chain 16:01-16:13, 12.2 min (contended, a bound); the blind hand read of 592 replies ~15 min. ETA 20 min of card, actual 12.2.

**The question** (owner, 2026-10-22: avoid SODA's style; real, varied text;
"let's move forward"). Finding 210: of the sources read, EmpatheticDialogues
talks most like both the stand-in messages and the owner's own (counts only);
SODA is the most formulaic. Pre-registered in `configs/nano5m_v3_webblend_ed.py`.

## The read

    read                                           base s1   base s2   ED s1    ED s2
    register: the owner's 69 messages (counts only) 5.218     5.105     4.880    4.963
      the 148 stand-ins                            3.987     3.828     3.766    3.814
    lm narrative                                   0.4864    0.4883    0.4876   0.4898
    lm web                                         0.9512    0.9522    0.9520   0.9568
    lm conversational (SODA's held-out text)       0.5579    0.5599    0.5671   0.5717
    coherence, blind hand read (of 148)            70        55        64       66
    swap, within: right / margin                   0.91/8.27 0.91/8.08 0.93/8.26 0.90/8.15
    swap, across: right / margin                   0.96/11.48 0.95/11.15 0.96/12.50 0.95/11.94
    knowing, matcher: admits unk / answerable      7 / 11    13 / 17   16 / 12  15 / 14
    commonest three-word opening                   'what why' x7  x15  'that's great what' x11  x8

(`evals/results/ed__register.txt`, `reply_ed__*`. The owner's messages are
read by the script and never printed: counts only, his rule.)

**The gates, as registered.** Fluency: holds (narrative under its line at
both seeds; web over at seed 2 only). Register: yes -- 4.880 and 4.963
under 4.992. **(r).** Coherence beside: no direction (64 is under 70).

## Read by hand

The replies are the control's kind, failures included ("That's great!" to
the spilled coffee and the missed bus, the self-doubt line to open
questions). Two small changes read in the text: a reply more often opens
on the message's news ("Oh no, that's too bad. What happened?" to the
cracked screen, "Oh, that's terrible! What did you lose?" to the wallet),
and "That's great! What..." became the commonest opening in place of
"What? Why?" -- EmpatheticDialogues' own most common response move. The
knowing matcher leans the right way at both seeds (+4, +1 against -4, -4),
unchecked by hand.

## What it licenses

**Corrected 2026-10-22, the owner's licence decision.** EmpatheticDialogues
is CC BY-NC 4.0 and the weights are Apache 2.0 (`docs/RELEASE.md`, decided
2026-08-30); the owner kept Apache and left ED out of every shipped corpus.
The first bullet below is what the measurement licensed; the source cannot
take it, and a permissively licensed real-dialogue source is read in its
place.

* **EmpatheticDialogues belongs in the 1.0 conversational plan**: at a
  sixth of the conversation it measurably moves him toward the owner's
  register at no cost to narrative or web. RELEASE lists it, CC BY-NC 4.0.
* **Replies need the size to follow** (findings 208-209): the register
  moved at 5M, the reply count did not; the reply read rides the 20M and
  the 1.0 pilot with this share in.
* **The share is a knob**: a sixth was the first point; SODA's held-out loss
  rose by ~0.01 nats a byte for it. A larger share, and a second real source
  in the owner's register (short requests and questions, finding 210), are
  the next reads.

**What it does not settle.** Any size above 5M; any share but a sixth; the
owner's register beyond 69 messages from testing sessions.
