# A 5M reading only conversation answers far more messages

**Full result:** The same 6.95M-parameter model, the same 130M tokens read once, with every token conversation -- 55% SODA dialogue, 40% SODA exchanges in the one-off reply frame, 5% EmpatheticDialogues and short-reply OpenAssistant (research only) -- answers 34 and 36 of 100 fresh hand-written one-off messages by a blind hand read, against 26 and 20 for the 5M that reads the usual mix (half web, 15% conversation): +8 and +16, 42 replies passing only under it and 18 only under the control (sign test p = 0.003), the pre-registered row R. With the judge-picked look-ahead on top it reads 41 and 41 (+7 and +5 over its own greedy, 22 to 10, p = 0.05 -- L holds at seed 1, misses by 2 at seed 2), +15 and +21 over the control's greedy and +17 and +14 over the control's own look-ahead (47 to 16). It is not yet a coherent 5M by the registered bar (60 of 100 at both seeds, R+ and L+ not met). The gains are in plans (1-2 of 8 to 6-7), feelings, good news and bad news; advice, opinions and the short and vague stay where the control is. The price: narrative and web text cost twice as much (1.03 and 1.41 nats a byte against 0.49 and 0.95); held-out SODA costs less (0.456 against 0.558)

**Cost:** the framed exchanges (`scripts/prepare_chat_pairs.py`, 6 s), the mix (44 s), the hand check of the stream, the 100-message exam, the configs and pre-registration 17:23-17:32 on 2026-10-24 (408482c); the chain 17:32-17:56, 23.7 min (two runs 273 and 290 s, two judges ~340 s each, 800 replies, contended at ~40%, a bound); the blind hand read of 800 ~15 min. ETA ~1.5 h, actual ~1.2 h.

**The question** (owner, 2026-10-24: "Can we do an only chat mix purely for
research on this? Like a one off pure research question of can we get a
coherent 5M model in one off chatting"; "should we do the judge picker combo
that helped us initially just applied to this"). The control reads about 20M
tokens of conversation -- ~3 a parameter, once -- and half its reading is
web text; TinyStories (Eldan and Li 2023) found coherence under 10M
parameters follows a narrow reading of the kind the model must write. Not a
1.0 mix (the 1.0 direction is broad reading, finding 185; the corpus's
EmpatheticDialogues licence keeps it to research).
`configs/nano5m_chatonly.py`'s docstring is the pre-registration.

**The instrument.** A fresh exam (`scripts/reply_exam2_messages.py`): 100
everyday messages hand-written 2026-10-24 in the 148's ten kinds, no overlap
with the 148 or the practice set, read by no model before. Eight versions in
one blind file; findings 214-218's rule and reader. It reads harder than the
practice set: the control's greedy 26 / 20 here against 31 / 33 there.

## The read

    read (of 100, blind)                       seed 1   seed 2
    control greedy                             26       20
    control + look-ahead (finding 214's judge) 24       27
    chat-only greedy                           34       36
    chat-only + look-ahead (its own judge)     41       41

    paired, pooled over both seeds             arm only : other only
      chat greedy vs control greedy            42 : 18   p 0.003
      chat look vs chat greedy                 22 : 10   p 0.050
      chat look vs control look                47 : 16   p 0.0001
      control look vs control greedy           16 : 11   p 0.44

    by kind (greedy control / chat greedy / chat look, seed 1 / seed 2)
      good news (10)    3/2   6/5   6/5        feelings (10)   6/4   9/8   8/8
      bad news (12)     6/4   4/8   6/9        plans (8)       1/2   7/6   7/6
      small talk (12)   2/4   3/3   6/3        opinions (8)    2/1   2/1   1/1
      about him (8)     2/1   1/2   3/2        short (12)      2/1   1/1   2/2
      advice (12)       0/0   0/1   1/2        odd (8)         2/1   1/1   1/3

    lm narrative / web / conversational
      control      0.4864 / 0.9512 / 0.5579     0.4883 / 0.9522 / 0.5599
      chat-only    1.0321 / 1.4110 / 0.4558     1.0284 / 1.4125 / 0.4577
    judge J1, held-out same-dialogue quads at the end (judge | his own)
      chat-only s1  0.943 | 0.947   (the control's own read 0.904, finding 214)
    distinct openings, greedy: control 61 / 66, chat-only 46 / 59;
      commonest under chat greedy: "that's great i'm" x18 / x10

(`evals/results/reply_chatonly__*`: replies, the blind file, its key, the
hand labels, the language rows; `evals/results/judge__nano5m_chatonly*.json`.)

**The rows, as registered.** R: +8 and +16, at least 7 at both -- **holds:
reading only conversation makes a 5M answer one-off messages more often.**
R+: 34 / 36, under 60 -- not met. L: +7 and +5 -- holds at seed 1, misses at
seed 2. L+: 41 / 41 -- not met. The prediction was R at +10-20 (+8 / +16),
no R+, L at +4-8 (+7 / +5), no L+: on all four rows.

## Read by hand

**What chat reading fixes.** Plans most: "That sounds like a great idea!
I'm sure you'll love it there." to a move, "That's great! What kind of cake
is it?", "Why do you want to learn to swim?" -- the control answered most of
these with "What? Why?" or a wrong object. Feelings and news turn the right
way more often ("Oh no! I hope you're not too upset." to a phone in the
bath, "I'm so sorry, Jaydon. That must have been really tough for you." to a
grandad's death). A few advice replies now carry an answer ("You'll need to
replace them." to smelly shoes).

**What it does not.** The stock pull is still there and has moved: "That's
great! I'm sure you'll do great." becomes the commonest line, and it lands
on bad news ("That's great news! I'm really happy for you." to a rent rise,
"Oh, wow! That's amazing! How did you find it?" to losing five pounds).
Short and vague messages get SODA's scene-openers -- "Hi, I'm looking for a
new car." to "Hello!", "So, what do you think of the new project?" to
"Alright then." -- because SODA's dialogues begin with a scenario, not a
reply to "Meh.". Opinions get "Yes, I am." to a question about e-books.
Advice is still almost empty: no reading of chat supplies how to save for a
holiday.

**The look-ahead on this model** adds where the stock line is the miss:
"Oh no! I hope you're not too upset." where greedy wrote a cheerful line,
"What kind of cake?" where greedy wrote "That's great, son!". On the control
it does not replicate on this exam (24 / 27 against 26 / 20, 16 to 11): the
look-ahead's gain is surest where the model's candidates are good enough to
choose between.

## What it licenses

* **Reading is the biggest single lever found for the 5M's one-off
  replies.** Same size, same budget: 26 / 20 to 34 / 36, and 41 / 41 with the
  look-ahead -- +15 / +21 over the control's greedy, the largest gain of any
  5M arm in findings 202-219.
* **The remaining failures are named and each has a lever**: the stock line
  on bad news (the judge's mood read; a judge on hard negatives, or move
  tags), the short and vague (no such messages in SODA -- a slice of short
  replies to short messages), the scene-opener habit (SODA's dialogue
  starts; exchanges cut from mid-dialogue only), and advice (knowledge:
  retrieval, or size).
* **Reading more of it is the next cheap read**: each exchange was read
  once; four passes cost ~20 min a run (the 2x2 of the owner's plan).
* **For 1.0**: the share and form of conversation in the mix move one-off
  replies at fixed size -- a direction to carry to the D1 share table, read
  at the pilot, not a 1.0 mix (this one gives up stories and the web).

**What it does not settle.** More passes; the four named fixes; any size
above 5M; the app's full prompt; multi-turn conversation.
