# Loop fails because the small model lacks the knowledge, not the format

**Full result:** On loop's own 436 answer-bearing batches, asked in plain sentences outside any trace, which place best fits the wish is near chance at 20M and grows with size -- the place that most raises the wish phrase is the right one 0.45 at loop's 20M start, 0.48 after the balanced fine-tune, 0.55 at 100M and 0.63 at 260M, against a chance of 0.41 -- while the trace format neither hides nor adds a judgment the model has (trace pick 0.45 at the 20M start, 0.52 after the balanced fine-tune); so loop's collapse (findings 184, 195) is a fine-tune with no signal learning the base rate, and the missing signal is knowledge of what a description implies, which 20M does not hold for these items

**Cost:** 20:55-21:13 on 2026-10-21 (the owner: "investigate the failures yourself and get back to me"); four reads of `scripts/probe_loop_formats.py`, 6.3 and 5.4 min of the four that ran whole, contended (the card at 37-40%, a bound).

**The question.** Findings 184 and 195: loop's stop reads nothing from
the batch -- he writes `none` on every batch when 71% of decisions are
`none`, and stops on every batch when half are -- and the place he names
is near chance. The owner: "I still don't fully understand why... Is it
truly internal reasoning being too small? 20M should be able to do this."
Three candidates: the control is too much for 20M; the trace format hides a
judgment he has in plain language; the judgment is not in him at all.

## The items, read by hand first

    wish [good for kids]   a bustling cocktail bar | a wine bar in a converted mill | a cider house with a play area
    wish [al fresco]       a bistro with a wide terrace | a diner inside a former chapel | a bistro with a children's menu
    wish [for an anniversary]  a wine bar with a leafy courtyard | a candlelit wine bar with velvet booths | a bustling cider house
    wish [lively]          an inn with high chairs | a loud boarding house with a dance floor

Easy for a person: one place in each batch plainly answers the wish.

## The read (`scripts/probe_loop_formats.py`)

The same batches from `evals/funcworld_loop.jsonl`, four ways, chance 0.41
on the picks (two or three places a batch):

    checkpoint                     plain pick   plain lift   trace pick   plain yes AUC   trace stop AUC
    nano20m_v3                     0.48         --           0.43*        0.494           0.508*
    nano20m_v3_fw_filter_ev2 (start) 0.45       0.45         0.45         0.482           0.492
    nano20m_ft_loop_ev2 (184)      0.42         --           0.50         0.477           0.549
    nano20m_ft_loop_ev2b (195)     0.44         0.48         0.52         0.480           0.540
    nano50m_v3_fw_branch           0.42         --           0.45         0.505           0.511
    nano100m_v3_funcworld_rope     0.46         0.55         0.43*        0.484           0.543*
    corn_jr_260m_v4                0.56         0.63         0.40*        0.495           0.529*
    corn_jr_260m_v4_ft_social8     0.54         --           0.40*        0.500           0.525*

    plain pick   "Looking for somewhere <wish>? The best fit is <place>." -- each
                 place's likelihood after the wish, minus without it
    plain lift   "<Place>. People would call it <wish>" -- the place that most
                 raises the wish phrase (the understanding ruler's direction)
    trace pick   the trace up to `pick: because[`, each place as the
                 continuation, against the same trace with another wish
    plain yes    "Is <place> <wish>? Yes or no:" -- yes minus no, AUC
    trace stop   `pick: none` against the best pick, answer batches against
                 batches without, AUC
    *            287 of 436 batches; the rest overrun a 512-token block, and
                 these checkpoints never trained on the trace format

**Not the format.** At loop's 20M start the judgment reads the same inside
the trace as outside it (0.45 and 0.45). There is nothing in plain language
for the format to hide.

**Not the control.** The stop cannot read a judgment the model does not
have: the stop's AUC sits at 0.49-0.55 at every size, and the place-fit
judgment it would need is near chance at 20M.

**The knowledge, and it grows with size.** In the ruler's direction the
right place reads 0.45 at 20M, 0.55 at 100M and 0.63 at 260M. The plain
pick (scoring whole descriptions, whose neutral tails -- "by the market
square" -- add noise) shows the same order more faintly. The 20M
fine-tunes move the trace pick 0.45 -> 0.50-0.52: the fine-tune teaches
some of it, not enough to supply a stop.

**The yes/no read is unreadable**, 0.48-0.51 at every size including 260M:
a bare yes/no question is not a frame these models answer by meaning, so
it says nothing about absolute judgment either way.

## What it licenses

* **The collapse is a fine-tune learning the base rate because the batch
  gives it no signal.** No signal, because what "a play area" says about
  "good for kids" is knowledge 20M does not hold for these items. It is not
  the reasoning the stop needs and not the trace format.
* **For the owner's loop call (finding 184):** a stop the runtime can check
  tests loop's control at 20M with the knowledge taken out of the question;
  the "sounds right" stop is a size question -- 100M reads 0.55 and 260M
  0.63 on these items before any loop training -- to be read at the pilot.
* **Size buys this knowledge faster than the web text did**: 20M -> 260M
  moves the lift read +0.18 on these items, where every 20M web mix moved
  the wish read by at most +0.08 (findings 185, 189-191).

**Size and text are confounded.** The checkpoints that read higher also
read more: the 20M starts trained on 129-140M tokens, the 100M on 398M and
the 260M on 5B (about 4, 4 and 19 tokens a parameter). Some of "grows with
size" is "grows with text read".

**What it does not settle.** Whether a 100M or 260M loop fine-tune installs
the soft stop; absolute judgment ("is any of these good enough?"), which no
frame here can read; the yes/no frame itself.
