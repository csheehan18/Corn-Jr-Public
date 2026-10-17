# One hundred and fortieth finding — the depth-4 zero is a position and nothing else: the identical cut that reads 3 to 19 of 96 at line 3 and 9 to 45 at line 2 reads 71 to 89 of 95 at line 1 on six W seeds and 88 at 100M, survives padding back to length, and sits where trained depth-3 shapes sit, so the content is not the block and a position-free expansion format is the arm on depth

**Cost:** 0 s of new scoring on record; it reads 8 cards scored for an earlier finding (`nano100m_v3_funcworld_rope`, `nano20m_v3`, `nano20m_v3_funcworld` and 5 more). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Read 2026-09-15 with no training, off PLAN-PARSE-WEIGHTS §7.6's owed read.
`scripts/probe_depthpos.py --read shift2,pad2`, new arms on finding 136's
own instrument, on the six rung-2 W checkpoints, `nano100m_v3_funcworld_rope`,
and B (`nano20m_v3`, never saw a parse world) as the floor. Cards:
`evals/results/<run>__depthpos2.json`, with finding 136's `shift` re-read on
the same checkpoints for one table.

## The question

Finding 136 found that a `parts:` line at index 3 holds a group in 0 of 2,236
corpus blocks, and moved the failing level-3 decision of a depth-4 tree one
line earlier by presenting the level-1 group's span as the utterance: 8 to 27
of 96 on the mean against 3 to 19 in place. It read that as position about
41% of the gap and *the innermost content the rest*. But line 2 is itself a
low-support position -- the corpus holds a group there in 0.18 of lines
against 0.40 at line 1 -- so the residue could be position too. This read
moves the decision two lines: the level-2 group's span becomes the whole
utterance, and the identical decision -- write the depth-2 group's span
whole rather than cut it into its members -- sits at line 1, in a tree that
is a trained depth-3 shape.

The instrument is `probe_structure.div_read` unchanged: at the one token where
the gold line and its flattened alternative part, which is likelier. No
length enters; chance is a coin. The scored line is now line 1, so where its
labels are not level-1 legal (`find`, `send`, `note` inside a `do` group)
both gold and flat are relabelled to level 1 and those 41 items are reported
apart, finding 136's own control. `pad2` pads the shortened prompt back to
the original's length with whole in-distribution turns, so the token offset
and the line index are separated as 136 separated them.

## The read

    gold's token likelier, of 96 (95 for the line-1 arms)
                                   at line 3   at line 2   at line 1   padded    untouched subset at line 1
    B, never saw the world            46          55          56         47       32/54
    nano20m_v3_funcworld               3          24          74         82       43/54
    nano20m_v3_funcworld_seed2         3           9          71         72       44/54
    nano20m_v3_funcworld_seed3         3           9          88         89       49/54
    nano20m_v3_funcworld_rope          7          29          89         87       51/54
    nano20m_v3_funcworld_rope_seed2    3          21          81         79       47/54
    nano20m_v3_funcworld_rope_seed3   19          45          84         86       49/54
    nano100m_v3_funcworld_rope         4          18          88         90       51/54

**Seven of seven, 71 to 89 of 95 at line 1 against 3 to 19 at line 3**, with
the floor at a coin and the padding moving nothing (72 to 90). On the 54
items whose scored line needed no relabelling, 43 to 51 of 54, which is 0.80
to 0.94 -- the band the structure cards read for trained groups at level 1
(55, 52, 57 of 58 in finding 133). The 100M, which finding 133 read as
*sharper at the unseen depth, not weaker*, is 88 of 95 here.

## What this settles

The depth-4 zero is a position. The same spans, the same decision, the same
fork token, read at the one line index the corpus has never shown a group at,
are refused; read at the index it shows most, they are cut at the trained
rate. Finding 136's "position about 41%" was the one-line shift landing on
another under-supported index; two lines removes the gap. Nothing in the
content of a depth-4 tree blocks him -- finding 137 said copy burden did not,
and this says the pairing and the carriers do not either.

**The arm this licenses**, PLAN-PARSE-WEIGHTS arm F: a format in which every
expansion is the same local step at the same position. The transcript writes
each group's expansion as its own block -- the group's span re-presented,
then the `parts:` line of its members -- so depth is a loop of identical
steps, each at index 0 of its own block with support at every level, and the
runtime walks the tree (PLAN-DECOMPOSE arm D's stepped protocol, made what
the corpus teaches rather than a fallback). C7 (PLAN-TAG-SPINE §11), which
trains a table one row deeper, is no longer the arm on depth: a table of
depths reads zero at the row it lacks whatever its length.

## What it does not say

The instrument is the one-token fork, not a greedy decode of the line;
`parse.w_depth4` on the card stays at zero until a format he was trained on
is scored, and a greedy read of the line-1 cut is owed beside this one. The
relabelled subset carries finding 136's caveat that relabelling is an
intervention; the untouched subset is the number to quote. One checkpoint at
100M.

*Instruments.* `probe_depthpos.py` gains `--read shift2,pad2`; eight cards in
one serialised background run, about a minute each, no timing read.
