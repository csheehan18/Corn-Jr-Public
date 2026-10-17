# One hundred and thirty-sixth finding — the depth-4 zero is a position the corpus pinned at zero, not an absence of recursion: a parse line at index 3 holds a group in 0 of 2,236 blocks, he predicts a fourth level 96 of 96 when the deep cut is given, and the identical cut scored at line 2 instead reads 8 to 27 of 96 on four checkpoints and survives being padded back to the original length

**Cost:** 19.1 min of scoring on the 4 cards first cited here (`nano20m_v3_funcworld`, `nano20m_v3_funcworld_rope`, `nano20m_v3_funcworld_rope_seed3`, `nano20m_v3_funcworld_seed3`); it also reads 2 cards scored for an earlier finding (`nano100m_v1`, `nano20m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

A diagnostic pass over findings 133 and 135, read 2026-09-14 with no training
and no new corpus. `scripts/probe_depthpos.py`, four reads: the corpus's own
conditional off the bytes; the continuation prior; the level-3 cut re-scored at
line 2; and that shift padded back to length. Checkpoints are rung 2's own --
`nano20m_v3_funcworld` and `_seed3` (learned positions), `_rope` and
`_rope_seed3` -- with `nano100m_v1` as the never-saw-a-parse floor and the
structure cards of finding 133 re-read beside. Card:
`evals/results/nano20m_v3_funcworld_rope__depthpos.json`. The instrument is
`probe_structure.div_read` unchanged, so every number here is comparable to an
`l3` cell of a structure card.

## The question

Finding 133 read `parse.w_depth4` at zero on greedy at every seed and its
amendment put the deep-cut preference at B's floor at level 3, the one nesting
training never showed. Finding 135 raised the depth-3 dose from 0.081 to 0.202
of turns and moved that level nowhere, and read it as *exposure is not the
lever*. Finding 133 had already read *size is not the lever* at 100M. Both were
taken as evidence about recursion. **Neither asked what the corpus says about
the position the read scores.**

## What the corpus says, off the bytes

A block of `d` consecutive `parts:` lines is a tree of depth `d`, so its line at
index `k` holds a group exactly when `k < d`. Counted:

    file                  line 1                line 2                line 3
    funcworld.txt    12105/29950 = 0.4042   2236/12105 = 0.1847   0/2236 = 0.0000
    dose2.txt        12164/29358 = 0.4143   3896/12164 = 0.3203   0/3896 = 0.0000
    dose3.txt        12056/28853 = 0.4178   5527/12056 = 0.4584   0/5527 = 0.0000

**Zero. Not rare -- zero**, across 2,236 consecutive examples with no
counterexample, and depth 4 is the holdout, so every span he has ever seen at
line 3 is a leaf. `parse.w_depth4`'s level-3 cell asks him to write a span the
corpus gives no support at that line.

And the dose arm could not have moved it. Raising the depth-3 share moved
`P(group | line 2)` from 0.1847 to 0.4584 and left `P(group | line 3)` at
exactly zero in every cell while adding 3,291 more blocks whose line 3
terminates. Finding 135's observed shape -- levels 1 and 2 climbing
monotonically with the dose, level 3 at the floor -- is what that predicts. Its
null is true of the exposure it varied and silent about the one that governs
the row.

## The floor says training moved him, and the direction is down

`parse.w_depth4` level 3, `deep_div` of 96, from the structure cards:

    nano100m_v1        never saw a parse      59/96, 52/96   -- a coin
    nano20m funcworld  trained depths 1-3      3 to 19/96
    nano100m funcworld the same, bigger             4/96    -- and 88/96 at level 1

A model with no knowledge of the world is at chance. Training on depths 1 to 3
drives it to near zero, and the larger, better-fitting model goes lowest of all
while reading highest at level 1. A capability is not lost by training; a
constraint is acquired. This is the signature of a learned regularity, and it is
why size did not help -- 100M fits the ceiling more sharply.

## He predicts the fourth level he has never seen

After a completed `parts:` line the corpus writes either another one or `move:`.
The mass on each, per line index, split by whether the gold tree continues
(`--read prior`, `nano20m_v3_funcworld_rope`):

    line  gold tree   items   prefers parts:   logp parts   logp move
       1  continues     471      471/471          -0.001     -13.530
       1  ends          161        9/161          -9.161      -1.740
       2  continues     255      243/255          -0.123      -9.302
       2  ends          216        5/216          -7.877      -0.767
       3  continues      96       96/96           -0.083      -6.630
       3  ends          159       19/159          -6.622      -0.811
       4  ends           96        0/96           -5.709      -1.405

**Given the deep cut at line 3, he wants a fourth `parts:` line 96 of 96 times**
-- at a depth the corpus contains zero times -- and stops correctly at line 4,
and stops correctly at line 3 when the tree genuinely ends. The other trunks
agree: 93 of 96 at `_rope_seed3`, 68 of 96 at the learned-position seed, which is
the weakest of the three and still above half.

So the recursion signal generalises to the unseen depth, exactly as finding
133's rank read found the *labels* do (96 of 96 at the innermost level). What
fails is narrower than either: **writing the long, conjunction-carrying span at
line 3 that makes a fourth level necessary.**

## The identical decision, one line earlier

A depth-4 tree's lower three levels are a depth-3 tree, which is a trained
shape. Re-presenting the level-1 group's span as the whole utterance puts the
identical level-3 decision at line 2 -- same gold line, same flattened
alternative, same divergence token, same spans; only the line index moves.
`deep_div` of 96:

    checkpoint                        at line 3   at line 2   padded to length
    nano20m_v3_funcworld                  3/96       24/96         22/96
    nano20m_v3_funcworld_seed3            3/96        9/96           --
    nano20m_v3_funcworld_rope             7/96       29/96         29/96
    nano20m_v3_funcworld_rope_seed3      19/96       45/96         41/96

Four of four, **8.0 to 26.75 of 96 on the mean**. Padding the shifted prompt
with whole in-distribution turns back to the original's length costs 0 to 4
cells, so what moves is the parse-line index and not the token offset.

Two worked cells, `_rope`, the fork being one token:

    wparse-0489, after "...the capital of Toraenddor into the bargain"
      at line 3    ']' -0.078   ' on' -2.784     flat wins by 2.71 nats
      at line 2    ']' -0.662   ' on' -0.815     flat wins by 0.15 nats

    wparse-0476, after "parts: ask[the"
      at line 3    ' capital' -0.022   ' two' -7.680    flat wins by 7.66 nats
      at line 2    ' capital' -0.189   ' two' -3.722    flat wins by 3.53 nats

## A confound, caught, and what it costs the headline

The first cut of the shift rewrote line 1 into level-1 label conventions
(`find`->`ask`, `send`/`note`->`do`) on 41 of 96 items, and read 6.3 to 29.2 of
96 over six checkpoints. Split by subset, the gain sat almost entirely in the 41
-- the intervention, not the position. Rerun with line 1 verbatim it is the
table above, smaller and noisier, and the two subsets still differ:

    orig -> shifted        relabelled (41)   untouched (55)
    nano20m_v3_funcworld        2 -> 18          1 ->  6
    _seed3                      1 ->  5          2 ->  4
    _rope                       5 -> 22          2 ->  7
    _rope_seed3                10 -> 28          9 -> 17

Every cell rises, 8 of 8, but do-rooted trees recover far more than ask-rooted
ones and this finding does not explain why. The probe reports both subsets by
construction now, and `--relabel` keeps the old arm readable beside it.

## The decomposition

Against what he does opening a group at line 2 on trained items
(`parse.w_pairing` l2 on the same four: 47, 52, 57, 60):

     8/96   the depth-4 level-3 decision, as scored
    27/96   the identical decision, at line 2
    54/96   an in-distribution group at line 2

**The position accounts for about 41% of the gap; the content of a depth-4
construction's innermost spans accounts for the rest.** Two failures, not one,
and neither is an absence of recursion.

## What it licenses

* **The guard**, built with this finding: `check_funcworld.py` section 6 reads
  the conditional off the corpus and fails on any eval row whose deepest cut has
  zero support at the line it is scored on unless that row is declared in
  `ZERO_SUPPORT` with what takes it, and on a declaration that has gone stale.
  The silent failure it names: *a row that asks for a structure the corpus gives
  no support at the position it is scored, whose refusal is read as a capability
  limit.* It would have fired before C5's four runs.
* **The wide-shape arm C6 is not the next arm on depth.** More depth-3 shapes
  leave `P(group | line 3)` at zero; it can answer the shape question at the
  depths that have support and cannot move the row it is aimed at.
* **The arm this proposes instead**: a depth profile with support past 3, so the
  conditional has no cliff, with specific *nestings* held out at depth 4 rather
  than the depth itself. Two rows and the gap between them is the result -- a
  trained depth-4 nesting against a held-out one, both floored on B. That makes
  "generalise to an unseen nesting" a question about shapes, which is what
  PLAN-TAG-SPINE §5 lever 3 intended, rather than about emitting a
  zero-support structure.
* **The stepped protocol as mechanism, not fallback**: re-prompting a group as a
  fresh utterance resets the line index and recovers about 41% of the gap,
  measured rather than assumed.

## What it does not say

It does not say the recursion generalises. It says the instrument could not ask:
two of the three components reach the unseen depth (the labels, 96 of 96 in
finding 133; the continuation, 96 of 96 here) and the third is scored where the
corpus has no support. Whether he cuts a nesting he was not shown, at a depth
that has support, is untested and is what the proposed arm exists for.

Nor does the shift isolate one variable. It moves the line index, the utterance
length and the remaining tree depth together; the padding arm removes the length
and the other two cannot be separated on checkpoints that have never seen a
group at line 3. Their separation needs the arm.

The subset asymmetry is unexplained, `--read prior` is one item set on three
checkpoints, and every number here is nano at 20M with one 100M floor.
