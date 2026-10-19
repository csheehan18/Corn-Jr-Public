# A space after the bracket shifts his default to the first option

**Full result:** A space after the menu's bracket, so the option is written in the request's own tokens, moves his default from a taste in place phrases to the first option listed (79% of picks) and leaves the binding exactly as unformed (209 of 400 on his own training traces); the phrase ranking was the spelling cost of a choice he had not learned

**Cost:** 19.3 min of training one nano run (1,157 s, contended -- the card at 30-40%, a bound), two reads at 15-18 s, one copy card 8 s, the control read 15 s, the free-decode hand read 7 s and the own-trace read ~7 s on the card; the build 14:02-14:07 on 2026-10-14, the chain 14:07-14:27, the read 14:27-14:28.

**The owner's question after finding 173.** The flip-word run's free decode
ranked every place phrase opening on "a" (0.43-0.89 when offered) above
every one opening on "somewhere" (0.26-0.41), and how often each was offered
or was the gold explained none of it. The tokens did: glued to the menu's
bracket, `next[somewhere to eat]` spells the phrase `[` `s` `ome` `where` --
pieces the request never contains, where it reads ` some` `where` -- and
`next[a spot to eat]` spells `[` `a`. With a space after the bracket the
option's tokens are the request's exactly. The owner's suggestion: test it
now. Pre-registered in `configs/mix_v3_funcworld_branchflip_spaced.py`'s
docstring at 3a9b495 before a byte trained; **one change from finding 173's
arm: the space** (`branchflipgen.FlipBranch.spaced`; `check_branch.py`
section 9 holds the payload and rows byte for byte but for it). One seed, as
finding 173. **Cards:**
`evals/results/nano20m_v3_fw_branchflip_spaced__branchflip_spaced{,_items}.json*`,
`__branch*.json*`, `__copywide.json`; the control
`nano20m_v3_fw_filter_ev2__branchflip_spaced.json`.

## The registered read

    quads (all four right)       held-out first   held-out second   flip pairs
                                   (of 144)         (of 144)         (of 144)
    arm E2 (control)                   0                1                0
    flip-word (finding 173)            3                0                1
    flip-word, spaced                  0                0                0

**The gate fails.** The registered outcome is the row "gate fails, ranking
flattens -- the instrument", with the flattening only half met: the
prediction said no phrase above 0.65 when offered, and the top phrase is at
0.77.

**Finding 169's rows are not readable on this arm.** They write the options
unspaced (`next[X]`), and a model trained on `next[ X]` writes the space: in
the free decode every one of its 64 lines on those rows is correctly formed
for itself and malformed for the rows. The `__branch.json` card for this run
reads an option format the run never saw, and is not quoted.

## Read by hand -- the free decode first

`hand_flip.py` (scratch, probe only -- not on disk), 16 quads on the flip
rows, every prompt, each line beside its request and result. **He writes the
continuation the request names first.** Row 054: "a place for drinks" on both
results while drinks is listed first, then "a place to sleep" on both once the
action twin lists it first; rows 126, 130 and 149 the same. The tally
follows from that. On plain families, where the first-named continuation is
the one the condition selects, he is right on 10 of 10 prompts when the
condition holds and 2 of 10 when it does not. On negated families, where the
first-named is the one taken when it does not hold, he is right on 1 of 6 and
4 of 6. Over all 432 quads (the full-option card):

    run                            first option picked   one place on all four   phrase pick rate (when offered)
    flip-word (finding 173)          583 of 1,728 (0.34)       276 of 432               0.26 - 0.89
    flip-word, spaced              1,373 of 1,728 (0.79)       199 of 432               0.34 - 0.77

**The default moved; the decision did not form.** With the bracket glued,
the cheapest line to write was the one with the cheapest spelling, so the "a"
phrases won. With the space every phrase costs what it costs in the request,
and the cheapest line became the one named first. Neither tracks the result:
the pick follows it on 9-19 of 288 twin pairs a cell, the control's 7-20.

## On its own training traces

400 payload traces from the front of the file (`own_traces.py`, scratch,
probe only -- not on disk): **209 right, median margin +0.07 nats** (finding
173's unspaced run: 202, +0.01; finding 169's installing seed: 367, +2.27).
Nothing formed where it trained, with or without the space.

**The copy row, a side column**: `tool.copy_wide` 290 of 300, inside the 20M
family's spread (finding 170).

## What it licenses

* **The phrase ranking was an instrument of the format, not a cause of the
  failure.** The spelling cost decided which option an unlearned choice fell
  on. It did not stop the binding forming -- removing it changed only where
  the choice fell. Finding 173's cause stands: the harder conjunction does
  not form at one pass and 2.2% of the mix.
* **The space is still the better format.** A bracketed copy whose tokens
  differ from its source's (`next[`, `soft[`, `because[`, `relax[` in
  SPEC-LANGUAGE) makes some words cost more to write than others for no
  reason, and a default that falls on spelling is harder to read than one
  that falls on position. It is a D7 question, with this finding as its
  evidence, and not a lever for learning.
* **The two levers from finding 173 remain**: the binding written by him
  beside the request (the hop in the bytes), or more fresh evidence.

**What it does not settle.** Whether the space helps where the copy *is*
the decision (`because[...]` copying an item's words), which a format arm on
rung 3's payload would read; and why position became the default rather than
nothing.
