# The built-in judge's cost is not the word table

**Full result:** Finding 217's built-in judge, rebuilt so its lesson never touches the shared word table -- it reads its inputs and scores its tokens through a detached embedding, its gradient reaching only the trunk's blocks -- costs the 5M exactly what the first build did: narrative / web / conversational 0.5150 / 0.9869 / 0.6031 against 217's 0.5156 / 0.9862 / 0.6040 (the control 0.4864 / 0.9512 / 0.5579, lines 0.4913 / 0.9552 / 0.5629), validation 2.7191 against 2.7187, and on the practice set 20 of 100 replies answer the message against 217's 21 and the control's 31 (6 pass only under it, 17 only under the control). The pre-registered row is (n), against a predicted (p): the word table was not the channel, and finding 217's named cause is withdrawn. The lesson learns as before (0.897 right at iteration 5,000) and the model switches its vote off as before (alpha 0.007)

**Cost:** the switch, its guard (the first version detached the output end only; `check_judge.py` 8 caught the input end), the pre-registration 16:45-16:51 on 2026-10-24 (70afcf1); the run 536 s (contended, a bound), the read 0.5 min; the blind hand read of 300 practice replies ~5 min. ETA ~25 min, actual ~20 min (16:45-17:05).

**The question** (owner, 2026-10-24: "Run that test"). Finding 217 named
the tied embedding as the likely channel: the judge scores a token against
its embedding, the embedding is also the output layer, and reply openers'
rows had drifted furthest from the same-seed control's. One change here,
`judge_detach_table=True` (`configs/nano5m_v3_webblend_judge_notable.py`,
its docstring the pre-registration); one seed, by the owner's choice.

## The read (seed 1)

    read                                  this arm   217's arm   control    line / half-gap
    lm narrative                          0.5150     0.5156      0.4864     0.4913 / 0.5010
    lm web                                0.9869     0.9862      0.9512     0.9552 / 0.9687
    lm conversational                     0.6031     0.6040      0.5579     0.5629 / 0.5810
    final val                             2.7191     2.7187      2.608
    lesson, training quads right          0.897      0.900       --
    alpha at the end                      0.007      0.007       --
    practice set greedy (of 100, blind)   20         21          31

(`evals/results/reply_notable__*`; the control's and 217's replies are
those reads' own, mixed into this blind file, and their labels agree with
217's read on all 200.)

**The gate, as registered.** No row is under its line and none closes half
of 217's gap: **(n), the lesson in the trunk costs language by any route.**

## Read by hand

The arm's replies fail as 217's did, less wildly than 217's seed 2: a
stock line in the wrong mood ("That's great! I'm glad you're enjoying it."
to a sprained ankle), a loop ("It's finally finally finally..."), an empty
reply twice. Its passes are the control's kind.

## The cause, corrected

Finding 217's two causes, read again with this arm:

1. **The vote** -- unchanged: next-word reading turns it to 0.007; it
   rewards a fit score almost never.
2. **The damage is the lesson's gradient in the blocks, not the table.**
   With the table cut out at both ends the cost is the same to the third
   decimal, so the drift of the openers' rows in 217 was a symptom, not the
   route. What the settings check of 217 already showed stands: the cost
   scales with the lesson's weight (0.06 nats at weight 0.3, 0.20 at 1.0,
   at 1,000 iterations), and at 0.3 the lesson's 4 quads carry about 2.3
   times a reading token's gradient per token (weight 0.3 over ~1,600 reply
   positions against 1.0 over 12,288 reading tokens). At 6.9M parameters,
   asking the last states to sort replies by fit takes capacity that
   next-word reading needed.

## What it licenses

* **The built-in judge is closed at 5M at this weight.** Its vote is
  refused, its lesson costs language and replies, and neither route around
  the table changes that.
* **The only variant left open is a much lighter lesson** -- and since the
  model refuses the vote at any weight, a built-in judge could only matter
  as a judge for the look-ahead to read, which the judge fitted beside the
  frozen model already is, at no cost to the model.
* **The 5M's best decoder is the look-ahead with the fitted judge**
  (findings 215-216: +5 / +15 on the 148, +8 / +6 on the practice set).

**What it does not settle.** Seed 2 (not run, by the registered rule); a
lighter lesson; a judge with a word table of its own; any size above 5M.
