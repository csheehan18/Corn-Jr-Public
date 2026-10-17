# One hundred and thirty-fifth finding — raising the depth-3 share from eight to twenty per cent of turns, at a shape coverage every corpus already saturates, deepens the preference to open a group at the depths shown, leaves the one depth never shown at the floor with the two seeds of the larger dose spanning the band, and costs unseen entities; the dose is exposure and exposure is not the lever on depth

PLAN-TAG-SPINE phase C5, the dose arm, read 2026-09-14. Four nano runs
pre-registered in `configs/mix_v3_funcworld_dose2.py` and `_dose3.py`: the
functional world under `corn/funcgen.py`'s `DEPTH_PROFILES`, the delivered
depth-3 share raised from W's 0.081 to 0.142 and 0.202 of turns with every
holdout W's (depth 4, the two pairings, the carrier twins), at W's pledge,
iterations and policy, RoPE, two seeds a cell. Controls: the three W-rope
cells, re-scored never retrained. `check_funcworld.py --corpus <file>
--min-depth3 <bracket>` green on both files before a byte trained; a
trainer smoke on the dose2 mix; decode parity four of four. Full cards, the
bound partials, the label-rank read, both structure reads, the constrained
decode, and one read taken off the corpora before any cell was scored.

## The question

Finding 133 and its amendments: on the functional world he cuts phrasings
he never saw, holds the labels for a fourth level (96 of 96 at the
innermost line), and does not cut the depth he never saw -- at the token
where the deep and flat cuts part he opens a group at depth-4 levels 1 and
2 and prefers the flat cut at level 3 by two to four nats on every seed and
at 100M. The owner asked whether that is a corpus gap: too little and too
narrow a showing of the recursion. Depth 3 was 8.1% of W's turns. This arm
moves that one number, twice.

## What was read before the cells, and what it changed

A review pass asked whether a raised share buys more distinct nestings or
more repetitions of the same ones, since the four cells cannot tell.
`scripts/probe_shapes.py` (card `evals/results/funcworld__shapes.json`):
the generator's drawable depth-3 shape space -- the tree with the words
removed -- is **54 shapes** (200,000 plans a profile, the count flat from
the first quarter), depth 2 is 100, and **every corpus carries every shape**
at both depths: W at 41 uses a depth-3 shape, dose2 at 72, dose3 at 102.
Finding 133's "almost every nesting once" counted trees with their words.
So the dose is **exposure, not coverage**, the configs were amended to
read it in that word before a card was scored, and the outcome table's
null was given its causes (below). Two more facts off the builds: depth 1
is flat across the three (0.563, 0.557, 0.560 of turns) and **depth 2 is
what shrank** (0.356, 0.301, 0.239), so the dose trades exposure to the
more diverse level (100 shapes) for repetition at the less diverse one
(54); and the delivered repair share falls with it (0.082, 0.069, 0.054),
reported and not read.

## The read

    length-free structure read, deep_div of 96 (mean log-ratio, flat minus gold)
                            W1        W2        W3     | dose2 s1  dose2 s2 | dose3 s1  dose3 s2
    trained groups, l1 (58)  55 (-4.9) 52 (-4.9) 57 (-5.5) | 54 (-4.7) 53 (-4.8) | 57 (-6.1) 54 (-5.1)
    held-out pairing, l2     57 (-3.7) 53 (-2.5) 60 (-2.8) | 62 (-2.7) 60 (-3.8) | 65 (-3.6) 58 (-2.6)
    depth 4, level 1         69 (-3.9) 76 (-6.1) 65 (-3.0) | 76 (-5.0) 74 (-6.1) | 82 (-5.0) 85 (-4.9)
    depth 4, level 2         59 (-3.4) 58 (-2.7) 62 (-2.7) | 66 (-3.2) 61 (-3.2) | 67 (-3.8) 64 (-2.9)
    depth 4, level 3          7 (+2.8)  3 (+3.3) 19 (+1.9) | 14 (+2.0)  8 (+2.7) | 24 (+1.8)  4 (+3.3)

    card                     W1/W2/W3       dose2 s1/s2    dose3 s1/s2
    parse.w_span   (120)     60/62/66        66/61          66/63
    parse.w_entity (120)     41/42/42        41/39          33/34
    parse.w_heldout(140)     17/10/11        14/10           9/12
    parse.w_pairing (96)      0/ 0/ 1         0/ 0           0/ 0
    parse.w_depth4  (96)      0/ 0/ 0         0/ 0           0/ 0
    parse.w_repair  (60)     36/37/34        31/36          36/37
    move.w_next    (120)    104/103/98      102/103         95/103
    e2e.w_tree      (60)     30/32/22        30/37          18/29
    tool.copy / copy_wide   120 everywhere; 289/297/269, 277/294, 293/287
    temporal.copy            353 everywhere
    val_loss                 2.231/2.255/2.271   2.230/2.255   2.232/2.257

    label rank, depth 4 gold first of 384    336/336/342     343/348     347/351

    constrained decode, free -> bound (finding 133's instrument)
                            W1      W2      W3    | dose2 s1  dose2 s2 | dose3 s1  dose3 s2
    w_depth4 l1 (96)       7->8    6->9    7->9   | 11->14    7->9    |  6->11    9->11
    w_depth4 l3 (96)       1->1    1->1    7->7   |  5->5     0->0    |  7->8     1->1 
    w_depth4 l4 (96)      55->60  43->44  59->62  | 69->73   50->52   | 80->83   53->54

**The pre-registered second row lands: level 3 sits inside W's band at
both doses**, and the larger dose's two seeds span it -- 24 at one seed,
five above W's high, and 4 at the other, at W's floor -- so on the one
number the arm exists for, the dose3 pair disagrees in direction and the
config's own unreadable clause makes that a direction and not a result.
The flat cut stays likelier at every seed of every cell, by 1.8 to 3.3
nats. What the exposure did move is the depths training showed: level 1
climbs monotonically with the dose (65-76, then 74-76, then 82-85) and
level 2 with it (58-62, 61-66, 64-67), which is what a table of nestings
looks like as it is learned harder -- the same shape the mid size read
(finding 133, second amendment: 88 and 64 at levels 1 and 2 and 4 at
level 3). More of the same 54 nestings buys more of the same 54 nestings.

**And it costs.** `parse.w_entity` reads 33 and 34 on the larger dose
against W's 41-42, below the band at both seeds -- unseen entities are the
row a raised share of long, lean, entity-dense turns displaces -- and
`e2e.w_tree` reads 18 at one dose3 seed against W's low of 22. The kill
clause (`w_heldout` or `w_span` under the band at both seeds) did not
fire: `w_span` 66/63 is inside, `w_heldout` 9/12 straddles W's low of 10.
The copy band held with one dip (`tool.copy_wide` 277 on dose2 seed 1),
the pattern every arm on this mix has shown once. The language rows are
unmoved to the third decimal, as they should be on a byte-identical
`mix_v3`.

## What the null names, and does not separate

The config wrote it before the read and it stands: neither repetition
(this arm) nor size (the 100M run, one seed) moves the cut at the depth
never shown, and three causes remain, none eliminated here. (a) At 54
shapes and 41 to 102 uses each, memorising the table of nestings is
cheaper than inducing a rule, so nothing pressures him toward one; the
depth-4 cut, and `w_pairing`'s inner level at a coin on every cell (53-65
of 96, a held-out shape at a *trained* depth), are what a table reads on
what it does not hold. (b) Effective depth of the trunk -- against which
the 100M read is a direction, not a result. (c) The design's own trade:
the dose shrank the more diverse level to feed the less diverse one, and
if a recursive rule is induced from seeing one composition applied across
depths, the arm moved the corpus the wrong way for it.

## What this licenses

Nothing in the 1.0 share table for the depth-3 share: raising it buys the
trained depths harder and costs unseen entities, and the dose stays where
W had it. Depth stays the runtime's -- the stepped protocol, with the
parse grammar shipping for the copy slips it removes (finding 133's
amendment) -- until an arm changes the shape space rather than the share:
PLAN-TAG-SPINE §11 C6, a generator with hundreds of depth-3 shapes each
used a handful of times and a held-out shape set, finding 13's
construction one level up from carriers, gated on the block decision
(NOW.md decision 2) because a 512 block holds four or five leaves a turn.
The companion layers-at-fixed-data cell (8 to 12 layers on W's own
corpus) separates (b) from (a) without a generator. Both are the owner's
to order.

## Instruments

* `scripts/probe_shapes.py`: the shape read that turned "dose" into
  "exposure" before a cell was scored; its `follow` at depth 1 is the
  rebind conversation's second turn, which the plan sampler never draws
  and the corpus carries, and is the one shape outside the sampled pool.
* `check_funcworld.py --corpus --min-depth3`: the base brackets on a file
  that differs in one table; dose3's consumer-first share sits exactly on
  its bracket's edge (0.30), a third consequence of the same budget,
  recorded in the config.
* The outcome table amended for an interpretable null and the depth-2
  trade, both before any card, both from a review pass and judged against
  the record: the review's "no held-out-shape row exists" was wrong
  (`w_pairing` is that row and reads the negative), and its remaining
  point -- two shapes held out of 54 is a thin instrument -- became C6.
* Four cells at 944-960 s; probes uncontended; nothing timed.

## Limits

Two seeds a cell and the deciding pair disagrees, so directions. One
world whose groups are inert (a flat cut with the right labels executes
the same lookups), so the row measures the shape and not the task -- the
random depth-4 item decoded by hand this day flattened a group at level 3,
which the runtime would have run identically, and slipped one `find` to
`ask`, which it would not. Exposure was varied over a saturated shape
space; coverage was not varied at all, and cannot be on this generator.
Nothing here touches the shipped checkpoint.
