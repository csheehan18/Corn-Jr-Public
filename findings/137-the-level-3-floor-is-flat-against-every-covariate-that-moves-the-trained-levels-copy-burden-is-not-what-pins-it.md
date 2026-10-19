# The depth-3 failure doesn't track copy length

**Full result:** The level-3 floor is flat against every covariate that moves the trained levels: the span the deep cut must write drives the in-distribution cell from 0.968 to 0.132 and leaves the unseen depth between 0.03 and 0.11 across its whole range, where the spans are already the shortest on the item, so copy burden is not what pins it and the greedy zero is one failure and not two

**Cost:** 10.0 min of scoring on the 2 cards first cited here (`nano20m_v3_funcworld_rope_seed2`, `nano20m_v3_funcworld_seed2`); it also reads 4 cards scored for an earlier finding (`nano20m_v3_funcworld`, `nano20m_v3_funcworld_rope`, `nano20m_v3_funcworld_rope_seed3` and 1 more). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

A stratification of findings 133 and 136's own cards, read 2026-09-14 with no
training, no new corpus and no new eval row. `scripts/probe_structure.py` gains
an optional `--items` dump -- one JSONL row per cell, the div outcome beside the
span lengths on that line -- and the six rung-2 checkpoints
(`nano20m_v3_funcworld` and `_seed2`, `_seed3`, and the three `_rope` seeds) are
re-read with it. 3,312 cells. Every aggregate on the six `__structure.json`
cards regenerates **bit-identical** to what finding 133 recorded, so the dump is
an addition to the instrument and not a change to it.

## The question

Finding 136 decomposed the depth-4 level-3 zero into a position worth about 41%
of the gap and "the content of a depth-4 construction's innermost spans" worth
the rest, and finding 133's hand decodes named a candidate for that content: the
forty-token spans carried copy slips ("Zelathgard" became "Zelvik"), and 46 of
the 96 misses on the repair row were copy slips rather than labels. If copy
burden is what the residue is made of, the greedy zero is two failures stacked
-- the cut and the copy -- and removing the copy should lift the cut.

The card holds rates, so it could not say which cells win and what they look
like. The dump can, and the question is answerable without building anything:
**does `deep_div` at the unseen depth track the length of the group span the
deep cut must write?**

## The read

`deep_div` by the longest group span on the gold line, pooled over six
checkpoints, quartiles of the covariate. `gap_div` is the mean log-ratio,
positive when the flattened line wins.

    row / level                  span toks     n   deep_div   rate   gap_div

    w_span    l1  (trained)          14-24   108        101  0.935     -4.18
                                     25-27    66         61  0.924     -4.57
                                     28-32    90         82  0.911     -5.03
                                     33-47    84         76  0.905     -4.77

    w_pairing l2  (trained)          22-26   186        180  0.968     -8.94
                                     27-31   114         84  0.737     -5.87
                                     32-35   132         40  0.303     +1.79
                                     36-44   144         19  0.132     +4.23

    w_depth4  l2  (trained)          29-36   156         62  0.397     +0.13
                                     37-38   144         94  0.653     -2.68
                                     39-41   144         99  0.688     -3.79
                                     42-50   132         85  0.644     -3.24

    w_depth4  l3  (no support)       19-22   168          6  0.036     +3.11
                                     23-24   168          7  0.042     +3.30
                                     25-25   108         12  0.111     +2.80
                                     26-33   132         13  0.098     +2.47

**The instrument has the sensitivity and the unseen depth has no effect.** On
the in-distribution control the same covariate drives the rate from 0.968 to
0.132 -- a span of 0.84 -- and flips `gap_div` through zero. At level 3 the rate
sits between 0.036 and 0.111 across the whole range and the flattened line wins
by 2.5 to 3.3 nats at every length.

**And the ranges settle it.** Level-3 spans run 19 to 33 tokens. The *same
items* at level 2 run 29 to 50, and the in-distribution control runs 22 to 44.
Inner groups are shorter than the groups that contain them, so **the level that
fails worst is the level with the least to copy**, and there is no copy burden
left to remove.

What direction there is runs the other way. Split at the median span (24
tokens), 6 of 6 checkpoints read the longer half higher:

    checkpoint                          short (of 56)   long (of 40)
    nano20m_v3_funcworld                            1              2
    nano20m_v3_funcworld_seed2                      1              2
    nano20m_v3_funcworld_seed3                      0              3
    nano20m_v3_funcworld_rope                       2              5
    nano20m_v3_funcworld_rope_seed2                 1              2
    nano20m_v3_funcworld_rope_seed3                 8             11
    total                                   13 / 336       25 / 240

## The other two covariates say the same thing

Gold-line length: level 3 reads 0.047, 0.028, 0.083, 0.118 over 36 to 53
tokens, against the control's 0.750 to 0.421. Distance from the start of the
line to the fork (`div_off`): level 3 reads 0.053, 0.053, 0.042, 0.121 over 5 to
34, against `w_depth4` l2's 0.818 to 0.181 over the same covariate.

`div_off` is the weaker instrument -- the control is non-monotonic on it
(0.868, 0.056, 0.402, 0.472), because a fork at offset 5 is a large structural
mode rather than an easy item -- and it is reported for completeness. The span
read is the one the question was asked with.

## What it means

**The level-3 floor is flat against every covariate that moves the trained
levels.** That is the signature of a constraint rather than a difficulty
gradient, and it is the third independent line pointing the same way: the corpus
conditional at zero over 2,236 blocks, the floor direction (a model that never
saw a parse is at a coin and training drives it to near zero, the larger fit
lowest), and now the absence of any gradient at all in the cell that is pinned.

**The greedy zero is one failure, not two.** Finding 136's 41/59 split stands as
arithmetic, but the 59 is not copy. Whatever the content half is made of, span
length is not a proxy for it.

## What it licenses

* **A copy-free or short-span control at the unseen depth is not worth
  building.** It was the cheap arm against the two-failures reading; the spans
  at that level are already the shortest on the item and length does not predict
  there. Roughly a day of generator work and a new eval row, not spent.
* **The residue in finding 136's shift is one of two things, not three.** That
  shift moved the parse-line index, the utterance length and the remaining tree
  depth together; padding removed length and this removes copy, so what is left
  unseparated is the index against the remaining depth. Separating them still
  needs a checkpoint that has seen a group at line 3, which is C7.
* **`--items` as a standing instrument.** Any future structure card can be
  stratified by the covariates on the line without a re-derivation, and the
  parity check above is the reason to trust the dump against the old cards.

## What it does not say

It does not say the cut is absent at the unseen depth. The read is still taken
at a position the corpus gives zero support (finding 136), so it inherits that
finding's limit whole: what greedy cannot write there, this cannot score either.
Two of the three components still reach the unseen depth on the conditional
instruments -- the continuation prior 96 of 96 (136) and the label rank 96 of 96
(133) -- and this read touches neither.

Nor is it an intervention. It is observational variation over the lengths the
generator happened to draw, in a band 19 to 33 tokens wide at the level in
question; a flat profile inside a narrow band is weaker evidence than a control
that sets the length. The reason to accept it anyway is the range fact -- the
level-3 spans are already shorter than every level where the covariate bites --
which no intervention could improve on in the same direction.

The subset asymmetry finding 136 could not explain (do-rooted trees recovering
more than ask-rooted ones under the shift) is untouched here and is not
explained by span length either.

## Instruments

`scripts/probe_structure.py --items`, six checkpoints, default rows. The
stratification itself was a scratchpad script over the dumps and is not on disk:
**the instrument is unpinned** and every number here is a bound reproducible
from the six `__structure_items.jsonl` cards in `evals/results/`, which are.
