# Choosing replies by what the message raises varies them, not their fit

**Full result:** On the plain 5M at both seeds, with no training, choosing each reply's first five words by log p(w | message) - 0.5 log p(w | empty message) among the twenty most likely leaves the blind hand read level -- 66 and 64 of 148 replies answer the message against greedy's 70 and 58 on the same checkpoints (the pre-registered gain needed 7 more at both seeds) -- and makes the replies far more varied: 123 and 124 distinct three-word openings of 148 against 86 and 82, the commonest opening used 3 and 4 times against 7 and 15. The two decoders fail on different messages (13 and 29 replies pass only under the new one, 17 and 23 only under greedy). Loops stay rare (1 and 2 against 0 and 0)

**Cost:** `scripts/probe_reply_mmi.py`, pre-registered at 1939dc9, 12:41-12:43 on 2026-10-22; generation for both seeds and decoders ~1.5 min (contended, the card at 39%, a bound); the blind hand read of 592 replies ~4 min of wall clock in this session. ETA 30 min, actual ~6.

**The question** (finding 204). The plain 5M prefers a fitting reply over a
swapped one in 91-96% of pairs but writes one that fits greedily only about
half the time, and greedy takes the commonest opening ("That's great!",
"What? Why?", "I don't know, I just feel..."). The anti-language-model form
of maximum mutual information (Li et al. 2016, the generic-reply problem of
neural dialogue) scores a word by how much the message raised it. Settings
fixed before a reply was generated (`lam 0.5, G 5, K 20`, the paper's range,
not tuned): the penalty on the first five words only, among the twenty the
model already rates most likely after the message, greedy after.

## The read

    decoder on checkpoint      blind hand read (of 148)   distinct openings   commonest opening     loops
    greedy, seed 1             70                         86                  'what why' x7         0
    new,    seed 1             66                         123                 'oh yeah what's' x3   1
    greedy, seed 2             58                         82                  'what why' x15        0
    new,    seed 2             64                         124                 'why what's wrong' x4 2

    passes under one decoder only     seed 1: new 13, greedy 17     seed 2: new 29, greedy 23

(`evals/results/reply_mmi__*`: replies, blind file, key and hand labels.
Greedy here reads the model in fp32; `probe_reply.py`'s reads were under
bf16 autocast, so seed 2's greedy replies differ in a few places from
findings 202 and 204's (58 here, 55 there) -- the pairing within this read
is exact, the pre-registration's "token for token" line was not.)

**The gate, as registered**: gain needs +7 at both seeds -- -4 and +6. **Level.**

## Read by hand

The new decoder moves the first words off the stock openings and toward the
message: "Oh no, that's terrible! What happened?" to a spilled coffee (greedy:
"Oh, that's great! What did you do?"), "Oh, no! I'm so sorry. Are you okay?"
to a sleepless night, "What party are you planning?", "Where did you find
twenty dollars?", "Good night! How was your day?". It also opens new failures
the same way: "Oh, really? Where are you headed?" to a friend moving *back*,
"Okay, let me get you a quick lunch" to "I'm on my lunch break", "Who were
steal?" to the squirrel, and two loops ("dying dying dying...", "vote for
vote for..."). The words after the fifth are greedy, and the model's
continuation drifts as it does under greedy ("Oh, wow, that's really sad.
What happened?" to a numb face is a pass; "You did a great job ... you
deserve it" to "I'm so happy right now" is not).

## What it licenses

* **Variety is a decoding choice, and it is free.** The owner's target --
  "it should vary how it tells me" -- moves by half again (86 to 123 openings)
  with no training and no cost to fit. For the runtime this is a setting,
  not a model change; it needs the same read on the shipped checkpoint
  before it is one.
* **Fit is not.** Asking the 5M for replies the message raises does not
  raise how many fit: the swap test's 91-96% is recognition between a good
  reply and a wrong one, and generating the good one word by word is a
  harder task than ranking it. At 5M the reply's later words, and the
  understanding behind them, still decide.
* Findings 202-205 together: three shapes and one decoder, and the count of
  fitting replies has stayed inside 55-71 of 148 on every 5M read. The
  lever left is what the model knows -- the text it reads, and the size
  that reads it.

**What it does not settle.** Other settings (`lam`, `G`, `K` were fixed, not
swept); sampling instead of greedy after the opening; any size above 5M;
whether varied openings read as more natural to a person in a real chat.
