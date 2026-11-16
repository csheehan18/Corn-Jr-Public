# A judge built into the 5M learns, is ignored, and costs him

**Full result:** A reply judge built into the 5M from the first step -- one block inside the model, taught on swapped replies with its gradient reaching every layer, its fit for every word added to the word scores at a weight the model learns -- learns its lesson (0.90 and 0.89 of its training quads right at the end, from chance) and is switched off by the model it sits in: the learned weight falls from 1 to about 0.2 by iteration 750 and stays near zero from 1,500 on (0.007 at the end, both seeds). The lesson costs language at both seeds -- narrative / web / conversational 0.5156 / 0.9862 / 0.6040 and 0.5141 / 0.9817 / 0.6009 against lines of 0.4913 / 0.9552 / 0.5629, the pre-registered row (d), as predicted -- and replies far more: on the practice set 21 and 6 of 100 answer the message against the plain 5M's 31 and 33 (12 replies pass only under the arm, 49 only under the control), and its own beam reads 26 and 12 against the plain look-ahead's 39 and 39. Decoding with the weight forced to 0 changes 0 and 1 replies of 100: the damage is in the trunk, not the vote

**Cost:** `CornModel.judge_bias`, `JudgeExercise`, the train hook, `check_judge.py` 8 (34 checks), four 1,000-iteration settings runs, the pre-registration 16:05-16:25 on 2026-10-24 (48f3fb0); the chain 16:25-16:45, 19.6 min (two runs 548 and 546 s, 1.0x the control's wall clock, contended at 40%, a bound); the blind hand read of 800 practice replies ~12 min; the cause probes 1 min. ETA ~2 h, actual ~1.3 h.

**The question** (owner, 2026-10-24: "Why can't the judge just be a layer
in the model itself?" ... "Let's do 3 now"). Findings 214-216: a judge
fitted beside a frozen 5M reads mood weakly and votes too softly; a frozen
trunk holds only what next-word reading needed. Built in, its lesson could
teach the trunk to keep fit, and the model could learn how much to use its
vote (`docs/PLAN-REPLY-JUDGE.md` Phase 3, version 3; the config docstring
`configs/nano5m_v3_webblend_judge.py` is the pre-registration).

**One design fix before the runs** (settings check, probe only -- not on
disk): with next-word loss reaching the judge, the 12,288 reading tokens a
micro-batch turned it into a second word head and its lesson stayed at
chance (0.50-0.57); the fit was detached from next-word loss so the judge
learns only its lesson and reading trains only the weight. The check also
showed the lesson's cost: 0.06 nats a token at 1,000 iterations, the same
with the weight started at 0 -- so the cost is the lesson's gradient in the
trunk.

## The read

    read                                          arm s1    arm s2    control s1  control s2
    lm narrative                                  0.5156    0.5141    0.4864      0.4883     line 0.4913
    lm web                                        0.9862    0.9817    0.9512      0.9522     line 0.9552
    lm conversational                             0.6040    0.6009    0.5579      0.5599     line 0.5629
    final val (training log)                      2.7187    2.7405    2.608       2.641
    lesson, training quads right (judge_log)      0.900     0.886 (4,500)
    learned weight alpha: start / 750 / end       1 / 0.196 / 0.007   1 / 0.175 / 0.007
    practice set, blind hand read (of 100)
      greedy on its own scores                    21        6         31          33
      beam on its own scores (look0)              26        12        --          --
      plain look-ahead, fitted judge (216)        --        --        39          39
    loops (V row): greedy / beam                  4 / 3     14 / 9    --          --
    greedy with alpha forced to 0: replies changed  0 of 100  1 of 100

(`evals/results/reply_inmodel__*`: replies, the blind file, its key, the
hand labels, the language rows, the alpha-0 decode;
`checkpoints/*_judge*/judge_log.jsonl`. The control's 400 replies are
finding 216's, mixed into this blind file; their labels agree with 216's on
all 400.)

**The gates, as registered.** Fluency: every row past its line at both
seeds -- **(d), the built-in lesson costs language at this weight**, the
predicted row. The reply read, beside it: arm greedy against control
greedy 12 : 49 pooled.

## Read by hand

Seed 2's replies break: an opening loses its first word ("a great, I'm so
happy to be able to help you out.", "'s a great bike."), numbers and
punctuation run on ("will be up to 1000000...", "::::"), and 19 of 100 are
loops or junk. Seed 1 keeps its sentences more often but fails the same
way less. Where both arms pass they write the control's kind of reply
("Me too! I've been looking forward to it for weeks.", "What kind of
bike?").

## The cause

1. **The vote did nothing.** Next-word reading turned the weight down to
   0.007 by the end: on real conversation the next word nearly always
   belongs to a fitting reply, so a fit score rarely changes which word is
   likeliest, and reading pays nothing for it. The judge's job -- breaking
   ties at a reply's opening among fluent candidates -- is one reading does
   not reward. Forcing the weight to 0 changes 1 reply of 200.
2. **The lesson broke the trunk, and the shared word table is the likely
   channel.** The judge scores a token by its state against the token's
   embedding, and the embedding table is also the output layer (tied). Its
   lesson therefore moves the output rows of the words it judges -- reply
   openers most. Read against the same-seed control (same initial weights,
   same batches), the reply openers' rows moved furthest: cosine with the
   control's row 0.719 and 0.723 for the 30 commonest openers against 0.758
   and 0.766 for everything else (probe only -- not on disk). That is a
   hint, not a measurement of the channel; the opening words lost in seed
   2's replies are what it predicts.

**Corrected by finding 218 (2026-10-24).** Cause 2's channel is withdrawn: with
the lesson kept out of the word table at both ends the cost is the same to
the third decimal, so the openers' drift was a symptom; the damage is the
lesson's gradient in the blocks.

## What it licenses

* **Version 3 as built is dropped**: it costs language and replies at both
  seeds, and the model refuses the vote.
* **The probe the cause names**: the same arm with the lesson kept out of
  the word table (the judge scores against a detached embedding, or a table
  of its own) -- one variable, one seed first. If language and replies come
  back near the control, the shared table was the channel and the
  question of a trunk taught by the judge is open again; if not, the
  lesson's gradient in the trunk is the cost at any route.
* **The vote has to be set, not learned from reading.** Reading never
  rewards it, so a built-in judge can only steer if its weight is fixed at
  decode -- which is the fitted judge's picker again (findings 214-216).
* **The 5M's best decoder stays the look-ahead with a judge fitted beside
  the frozen model** (findings 215-216).

**What it does not settle.** A lighter lesson weight; versions 1 and 2 of
Phase 3; the lesson kept out of the word table; any size above 5M.
