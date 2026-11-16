# A matching lesson at a tenth of conversation reading did not take

**Full result:** Graded from the first step on whether a reply belongs to its message -- two quads a micro-batch from the 717,092 message-reply pairs of his own conversational reading, scored lp(r1|m1) + lp(r2|m2) - lp(r2|m1) - lp(r1|m2) so a reply's general likelihood cancels, weighted like one token of the reading -- the 5M matches no better afterwards: same-dialogue quads right 0.873 and 0.867 against the control's 0.872 and 0.858 (the gate was 0.887 at both), the pre-registered row (u), the exercise did not take at this weight. Its margins rose a little at both seeds (11.00 / 10.30 against 10.43 / 9.69) and its training log climbed to 0.885 by step 5,000; language, the rulers and the swap test are level; the blind hand read gives 73 and 63 of 148 against 70 and 55. By hand, a large part of what the control gets "wrong" has no right answer: two turns of one conversation often carry replies that fit either message

**Cost:** `corn/contrast.py`, its guard (`scripts/check_contrast.py`, 103 guards), `scripts/probe_contrast_take.py`, a 500-iteration smoke run, the floor and the pre-registration 13:41-13:47 on 2026-10-22 (5c48510); the chain 13:47-14:06, 19.1 min (both runs 417 and 414 s, contended, a bound); the quad hand check and the blind hand read of 592 replies inside it. ETA 25 min of card, actual 19.1.

**The question** (owner, 2026-10-22: teach him from wrong answers; "this
should come from pretraining"; "no shortcuts"; about a tenth of his
conversational reading). Next-word training only ever says what to write.
Findings 204-205: the plain 5M recognises a fitting reply far better than it
writes one. This adds a matching lesson to pretraining from step one --
`corn/contrast.py` argues every setting -- at 2 quads a micro-batch (three
same-dialogue to one cross), weighted like one token each, on the control's
reading byte for byte (its own generator). Predicted (t): it takes, writing
is level.

## The read

    read                                          base s1   base s2   arm s1   arm s2
    exercise take, same dialogue: right / margin  0.872/10.43 0.858/9.69 0.873/11.00 0.867/10.30
      cross: right / margin                        0.989/20.05 0.990/19.28 0.986/20.27 0.986/19.38
    training log, same dialogue right (step 5,000) --        --        0.885    (seed 2 alike)
    coherence, blind hand read (of 148)           70        55        73       63
    swap test, within margin                      8.27      8.08      8.15     7.68
    lm narrative / web / conversational           0.4864/0.9512/0.5579  0.4883/0.9522/0.5599  0.4880/0.9543/0.5582  0.4880/0.9523/0.5603
    fields / wishes 192 / plain lift              0.56/0.35/0.49  0.53/0.32/0.47  0.52/0.33/0.48  0.49/0.33/0.47

(`evals/results/contrast__take.txt`, `reply_contrast__*`,
`nano5m_contrast__*`; hand labels and blind key committed beside the
replies.)

**The gates, as registered.** Took: no -- 0.873 and 0.867 under 0.887.
**(u)**, whatever else moved. Read beside: fluency holds; the hand read is
inside the control pair's spread (a seed-for-seed +3 and +8, not the
pre-registered direction, which needed both above 70).

## Read by hand

**The quads.** Six same-dialogue quads drawn fresh and decoded with both
checkpoints' margins: the instrument scores what it should (*"Hi there! I'm
going to wash your face and hair" -> "Okay!"* against *"This feels good!
Thank you, Jerry" -> "You're welcome, sweetie..."*: +21.5 on the control).
But the hard ones are hard because nothing decides them: *"It's no problem.
I want to help you" -> "That means a lot to me"* against *"I'm happy to offer
my protection" -> "Thank you, Rylei. I really appreciate it"* -- either
reply fits either message (+1.5 / +0.9); in another, *"Really? I never
thought of it that way"* and *"Exactly! And that's what makes art so
interesting"* each fit both turns. Two turns of one conversation share
the topic, the people and the mood, and their replies are often
interchangeable; the 13% the control gets wrong is part error and part a
coin with no right side.

**The replies** (592, blind; the control's labels came out 70 and 55 for the
third time) fail as before: "That's great!" to a spilled coffee, the
self-doubt line to open questions.

**Corrected by finding 207 (2026-10-22).** The six quads above were not a
count. Read blind with a baseline, a person decides 42 of 50 same-dialogue
quads the control gets wrong, 38 correctly; undecidable pairs are about a
sixth of the misses, not "a large part". The reading (u) stands; the reason
given for it below does not, and the licence's "if few" branch is the one
that did not happen.

## What it licenses

* **At this weight the lesson does not move him.** It honoured the cap the
  owner set (~1.6% of the reading's weight); quads already right by a wide
  margin teach almost nothing, and the ones left are partly undecidable.
* **Before a heavier weight, measure the headroom by hand**: read 50
  same-dialogue quads the control gets wrong and count how many a person
  could decide. If most cannot be decided, a heavier weight trains on noise
  and the exercise needs harder *decidable* pairs (a reply that answers a
  question against one that answers a statement; a reply that fits the mood
  against one that fits the topic) rather than more of these.
* The machinery stands: pairs from his own reading, a margin no reply prior
  can move, the reading untouched -- guarded and ready for either.

**What it does not settle.** Any heavier weight; any size above 5M; whether
a lesson that took would carry into writing (finding 205's open question).
