# Aligning training blocks to transcript starts helps parsing, short of target

**Full result:** Arm A at one seed: blocks aligned to transcript starts move the level-1 cursor from 558 to 639 of 772 and cut invented spans by a fifth, short of the pre-registered third, lift unseen entities by nine and trained shapes by one, cost held-out carriers four and the deep cells ten, and put the copy band under its kill line on one of six answers, where a copied person's name comes back as an invented entity

**Cost:** 15.1 min of scoring on the 2 cards first cited here (`nano20m_v3_fw_b1024_alignA`, `nano20m_v3_fw_b1024_alignA_seed2`); it also reads 1 card scored for an earlier finding (`nano20m_v3_fw_b1024`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-PARSE-WEIGHTS arm A, lever 7a of FAILURES-PARSE, built and trained
2026-09-15 by another session as `configs/nano20m_v3_fw_b1024_alignA.py` and
read here the same day. **One seed; the pre-registered kill needs two.** The
pair is the arm against `nano20m_v3_fw_b1024` at seed 1337: block 1024, batch
12, 5,513 steps, `compile` on, one field changed (`align_parse_blocks`),
confirmed from both checkpoints' `config.json`. Cards: the arm's full card
`evals/results/nano20m_v3_fw_b1024_alignA.json`, and on both sides
`__parseonly.json` with `__parse_items.jsonl`, `__cursor.json` with
`__cursor_items.jsonl`, and `__parsebind.json`.

## What the arm changes

`Batcher` samples block offsets uniformly; an offset inside a parse-bearing
transcript now snaps back to that transcript's first token, so no `parts:`
line trains against an utterance the window cut off. The other session
measured the whole-utterance rate on the built stream at 0.898 uniform and
1.000 snapped. Read off the same stream here: snapping also raises each
level's expected full-line exposures by 3 to 7 per cent (level 1 x1.03,
level 2 x1.07, level 3 x1.05, level 4 x1.03), so the arm is cleaner context
and slightly more parse gradient together, as its config docstring says.

## The card, arm against control

    row                 control   arm       W-rope seeds 1, 2
    parse.w_span          48/120   49        60, 62
    parse.w_entity        16/120   25        41, 42
    parse.w_heldout       12/140    8        17, 10
    parse.w_pairing        0/96     1         0,  0
    parse.w_depth4         0/96     0         0,  0
    parse.w_repair        37/60    42        36, 37
    move.w_next           99/120  108       104, 103
    e2e.w_tree            22/60    24        30, 32
    tool.selection        83/200  128       133, 139   (reported, not read)
    tool.copy            120/120  100       120, 120   **kill line 118**
    temporal.copy        353/353  352       353, 353
    val loss              2.228    2.230

The language rows are within 0.001 nats a byte on every source.

## The three pre-registered numbers

**The cursor** (`probe_cursor.py`, interior boundaries, first boundary
excluded): 558 to **639 of 772**, 0.723 to 0.828, the largest move of any
arm on this instrument and into W's band (615-665). Every row rises:
trained shapes 90 to 112 of 126, entities 134 to 152 of 175, held-out
carriers 128 to 134 of 202, pairings 107 to 121 of 138, depth 4 99 to 120 of
131. Far misses, two or more words off, 180 to 107. By boundary: the bare
space 0.61 to 0.79, modifiers on both sides 0.26 to 0.44.

**The crossing** (level-1 cells of the scorer, 572 lines): passes 108 to
122; lines with a span not in the utterance **236 to 187**, invented spans
286 to 220 -- a fall of 21 to 23 per cent against the gate's third. Lines
that tile the utterance and fail on the cut or the label rise 228 to 263: the
failures that remain are more often decisions. Lines that lose the cursor
anywhere fall 190 to 124, and finding 138's rule holds on both sides -- 0
and 1 of them pass.

**Free and bound** (`probe_parsebind.py`, level 1 unless said):

    cell                 control free -> bound    arm free -> bound
    w_span     l1            53 -> 56                58 -> 61
    w_heldout  l1            19 -> 24                10 -> 14
    w_pairing  l1             6 ->  7                 6 ->  6
    w_depth4   l1             6 ->  8                 7 ->  9
    w_pairing  l3            53 -> 56                41 -> 55
    w_depth4   l4            44 -> 49                34 -> 39

On trained shapes free and bound rise together by five with the gap
unchanged, which is a decision moved and not bookkeeping. On held-out
carriers both fall by nine or ten. On the two deepest cells free falls by
ten and twelve, and the exposure arithmetic above says that is not a shift
of gradient away from deep lines; at one seed it is unread.

## The copy band

`tool.copy` reads 100 of 120, under the band's kill line of 118, with every
one of the twenty misses on one answer of six. Asked to read `Alexander
Fleming` back from the observation he says `It's Belaeskdia Fleming.` or
`It's Torilvrin.` -- a name shaped like the parse world's invented entities
in place of the copied one; the other five answers are 100 of 100 and
`temporal.copy` is 352 of 353. The control and both W seeds read 120. This
is the recall-over-copy species of FAILURES-PARSE §7e on the tool slice,
and it is the first time an arm has moved it. One seed cannot say whether
the alignment did it or the seed did; two seeds under the band kill the arm
whatever the parse rows say.

## Reading

The mixed row. The arm does what 7a predicted on the mechanism it names --
the cursor and the invented spans move in the right direction by more than
any arm before it -- and misses the gate's size, costs the held-out and
deep cells, and trips the copy band once. Nothing here is a result until
seed 2: `nano20m_v3_fw_b1024_alignA_seed2` against a `nano20m_v3_fw_b1024_seed2`
that does not yet exist, so the second pair is two runs. If the copy row
repeats under 118 the arm is dead and the mechanism goes to §7e's line; if
it does not, the parse reading is decided by the cursor and the crossing at
two seeds, and the deep-cell drop is read against its seed spread.

## What this does not say

One seed on each side; the control's own tool rows sit oddly low on
`tool.selection` (83 against W's 133-139), so this control is not a quiet
one. The bound decode's deep cells are 96 items with a seed spread nobody
has measured at block 1024. The whole-utterance rate of 1.000 is the other
session's number, read off the stream and not re-derived here.

*Instruments.* `corn.evals` full card and `--only funcworld_parse --items`,
`probe_cursor.py`, `probe_parsebind.py` (about twelve minutes a checkpoint
at block 1024), a scratchpad regeneration of the twenty copy misses with
their bytes, and the exposure arithmetic over `Batcher._parse_transcripts`;
all serialised on the card beside the owner's server, no timing read.

## Amended 2026-09-16 -- the second seed, and the kill does not fire

`nano20m_v3_fw_b1024_alignA_seed2`, one field from the seed-1 twin. **The copy
band recovers**: `tool.copy` **119 of 120** against the kill line of 118,
`tool.copy_wide` 300 of 300, `temporal.copy` 353 of 353. This finding's own
clause -- *two seeds under the band kill the arm* -- is therefore not met, and
the seed-1 reading of 100 of 120 was an excursion rather than the alignment.
**Arm A is not killed.** The title above was written before this read and
stands as the record of what one seed said.

What replicates, and in the same direction both times:

    row                  control    seed 1    seed 2      W
    tool.copy            120/120   100/120   119/120   120/120
    invented spans        399/824   299/792   318/805        --
    parse.w_repair          37/60     42/60     44/60     34-37/60
    parse.w_entity         16/120    25/120    21/120     41-42/120
    e2e.w_tree              22/60     24/60     26/60     22-32/60
    parse.w_span           48/120    49/120    51/120     60-66/120
    parse.w_pairing          0/96      1/96      0/96      0-1/96

So the gate is **missed at both seeds and missed consistently**: the invented
share falls 48.4% to 37.8% and 39.5%, a fifth against the pre-registered third.
`parse.w_repair` is above W's band on both arm seeds, which no cell in this
phase had managed.

**Two rows this finding read as signal that are not.** `tool.selection` reads
83, 128 and 75 across the control and the two arm seeds, so the observation
that "this control is not a quiet one" at 83 is variance and not a property of
the control -- the row is simply loose at nano and should not be read either
way. And `extract.span` falls on **both** arm seeds (12 on the control to 5 and
3), which is not in the table above because nothing here explains it; it is the
one unexplained cost of arm A and it is owed a look before the arm ships.

**Two numbers from the seed-1 write-up, re-derived.** The share of drawn tokens
landing in the parse-bearing segment is 5.000% with alignment on and off alike
-- snapping moves the window, never whether the offset is in the segment -- so
arm A is not a dose change in disguise. Parse lines a window rise 0.2740 to
0.2888, **5.4%**, not the 15% an earlier small-sample read claimed. And the
whole-utterance rate by level, in closed form over uniform offsets rather than
sampled: 0.954 / 0.878 / 0.788 / 0.665 by level and 0.903 overall on
`mix_v3_funcworld_b1024`, against 0.954 / 0.824 / 0.687 and 0.891 on W at block
512 -- so the damage 7a names is concentrated at levels 3 and 4, and block 1024
is slightly *better* on it than 512, not worse.
