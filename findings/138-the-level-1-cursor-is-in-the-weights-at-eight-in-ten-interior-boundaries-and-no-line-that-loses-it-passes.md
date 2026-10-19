# He knows where the next request part starts, 80 to 93 percent

**Full result:** The level-1 cursor is in the weights and not at the ceiling: with everything before it gold he opens the next part where the last one ended at 80 to 86 per cent of interior boundaries at nano and 93 at 100M against a floor of 1, flat in offset, a lost cursor lands mid-part and no line that loses one passes, while the close is his at 98 per cent and a quarter of level-1 failures tile the utterance and fail on the decision alone

**Cost:** 7.6 min of scoring on the 1 card first cited here (`nano20m_v3_fw_b1024`); it also reads 3 cards scored for an earlier finding (`nano100m_v3_funcworld_rope`, `nano20m_v3`, `nano20m_v3_funcworld`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Read 2026-09-15 with no training and no new corpus, off the owner's question:
*how much of the parse's bookkeeping could be in his weights?*
`docs/FAILURES-PARSE.md` §5 proposed level-1 tiling as a runtime constraint --
the parts, in order, only a joiner between them, nothing left over, true of
every parse block in every functional-world corpus -- and the thesis puts
bookkeeping in the runtime by design. This asks whether he holds it anyway.
`scripts/probe_cursor.py`, new, on nine checkpoints: the six rung-2 W
checkpoints (`nano20m_v3_funcworld`, `_seed2`, `_seed3`, `_rope`,
`_rope_seed2`, `_rope_seed3`), the C6 control `nano20m_v3_fw_b1024`, the
mid size `nano100m_v3_funcworld_rope`, and B (`nano20m_v3`, never saw a parse
world) as the floor. Cards: `evals/results/<run>__cursor.json`; per-boundary
dumps beside four of them.

## The instrument

Two distributions per gold level-1 line, teacher-forced, so a label or a cut
he gets wrong upstream cannot reach the position read.

**The start.** After `label[` of part j+1 with parts 1..j and the label gold,
the candidates are every word start in the utterance, each scored as its first
W tokens (the utterance from that word onward, closed with `]`), W the smallest
count up to four at which the gold start's tokens are unique among the
candidates and the same W for every candidate at that boundary, so no length
enters; identical W-token prefixes are one candidate. Softmax over the
candidates; three classes against the gold start, which at level 1 is the first
word after the previous part's span: `cursor`, `before` (a start already
covered), `after` (a start that skips words). Top-1 and mass. The first
boundary of every line (offset 0) is reported apart from the interior ones,
because opening at the start of the utterance and continuing from the middle
of it are different acts. The dump also records the likeliest start's distance
from the cursor in words: one word off is a disagreement about where the cut
goes, several is a lost cursor.

**The close.** After `]` of part j, `\n` against a space-and-label, the only
two continuations the grammar allows: `early` at a non-final part is
truncation, `runs_on` at the final one is not knowing the utterance is used up.

Five rows, 572 lines, 772 interior boundaries; `w_repair` is out because its
first gold line is the corrected deeper level, not level 1. Chance at the start
read is one over the distinct candidates, 0.04 to 0.12 by row.

## The start, interior boundaries

    cursor top-1, of n           B      b1024    W1     W2     W3     R1     R2     R3     100M
    w_span      (126)            3       90     107    105    106    111    122    114    125
    w_entity    (175)            2      134     154    148    154    154    163    160    169
    w_heldout   (202)            2      128     148    137    146    134    142    142    162
    w_pairing   (138)            2      107     122    116    124    116    122    112    135
    w_depth4    (131)            1       99     113    116    119    100    116    103    127
    all         (772)           10      558     644    622    649    615    665    631    718
    rate                      0.013    0.723  0.834  0.806  0.841  0.797  0.861  0.817  0.930

    first boundary, of 572      65      572     571    571    572    570    572    564    572

**He knows where the last part ended at eight in ten interior boundaries at
nano, at nine in ten at 100M, and at the floor's one in a hundred.** The
opening boundary is at ceiling on every trained checkpoint. B, which never
saw a parse world, puts its mass on `after` at the first boundary and on
`before` at every later one -- it wants to start the utterance over -- and
closes early at 714 of 772 non-final parts, so everything above is learned
from the world.

**Flat in offset.** By the cursor's position in characters, interior only:

    cursor top-1, of n         1-40 (387)   41-80 (97)   81-120 (85)   121+ (203)
    nano, six W + b1024         280-341       63-77         60-77        155-172
    100M                          363           85            82           188

The 41-80 bin is the lowest on every checkpoint and the 121+ bin is not below
the 1-40 one. The cursor does not decay with distance into the utterance:
FAILURES-PARSE §4's length driver is not the cursor.

**Held-out carriers are the deficit, and it survives size.** `w_heldout` reads
0.66-0.73 interior at nano against 0.83-0.97 on trained shapes, and 0.80
against 0.99 at 100M. On the rope seed 1 dump by holdout kind: held-out cores
53 of 71, held-out modifiers 39 of 61, both together 42 of 70; at 100M 62, 48
and 52. A modifier he never saw on the part just closed, or on the one about
to open, costs him the boundary more than a core does.

## Where a lost cursor lands

    likeliest start against the cursor, words   <=-2    -1     0     +1    >=+2
    b1024                                          94    12   558     22     86
    R1 / R2 / R3                              64/32/54  14/9/9  615/665/631  6/16/10  73/50/68
    100M                                           18     4   718      3     29

One-word misses are 2 to 4 per cent of boundaries; the misses are far, both
ways, in about equal measure. Of R1's 137 far misses, 124 land in the middle of
a part -- not at another part's start (10) and not at the utterance's start
(3); at 100M, 42 of 47. A lost cursor is not a part chosen out of order. It is
a position with no structural meaning, which is what a copy that drifted looks
like from the outside.

## The close

    early, of 772 non-final     runs_on, of 572 final
    B          714                 129
    nano       0-19                 2-14
    100M         8                   0

**Truncation is not in the weights' failure set.** He closes the line where
the utterance is used up and nowhere else at 97.5 per cent or better on every
trained checkpoint. FAILURES-PARSE §6 listed truncation as a species the
tiling constraint would close; it would close nothing there.

## The crossing with the card -- one seed

`corn/evals.py --only funcworld_parse --items` on rope seed 1, level-1 cells,
joined to the cursor dump by item. 503 lines have an interior boundary; 69 are
single-part and pass 47.

    every interior boundary read at the cursor     lines    l1 pass
    yes                                             365       105
    no                                              138         0

**No line that loses the cursor anywhere passes level 1.** The cursor is
necessary. It is not sufficient: 260 of the 365 lines that held it still fail,
and those failures sort by what the emitted line did to the utterance
(`span_ok` for a span not in it, then order, then coverage):

    the 398 level-1 failures, R1          cursor held    cursor lost
    a span not in the utterance               149             90
    tiles the utterance, wrong arity/label     94             28
    goes back or repeats                       10             10
    closes early                                6              8
    no parts                                    1              2

**A span not in the utterance is mostly a span that opened in the right place
and drifted** -- 149 of 239 invented spans sit on lines where every opening
was at the cursor. And 94 lines tile the utterance perfectly and fail on
arity or label alone: the cut and the name, the decisions, with the
bookkeeping done.

## What this settles

The boundary the owner asked about, for level-1 tiling, on this world:

- **Opening the first part** is in the weights at ceiling.
- **Closing the line** is in the weights at 98 per cent.
- **Opening the next part where the last ended** is in the weights at eight
  in ten boundaries at nano and nine in ten at 100M, flat in offset, ten to
  twenty-five points lower on carriers he never saw, and moved by size where
  the depth cut (findings 133, 135, 136) was not.
- **The rest of the line** is a copy that can drift mid-span -- the
  span-in-parent constraint finding 133 read lifting rows by four to twelve
  cells -- and a cut and a label the runtime cannot hold at all.

So a tiling constraint in `ParseConstraint` would hold the 14 to 20 per cent
of interior boundaries he loses at nano, every one of them on a line that
would otherwise fail; the existing span constraint holds the drift; and a
quarter of level-1 failures are the weights' alone. What the weights hold here
they hold as a mechanism that generalises across entities (154-169 of 175)
and not fully across carriers, which is the same shape the copy has had since
finding 129: attention does the copy, and the copy is conditioned on
recognising what is being copied.

## What it does not say

The read is teacher-forced: every position has gold before it, so it is a
bound on what free decoding, where a lost cursor compounds, would show. The
crossing is one seed on one checkpoint. The 100M is one seed. `w_heldout`'s
three sub-kinds are 61-71 boundaries each. And "in the weights at eight in
ten" is not "should be the weights'": a held rule has no failure rate, and the
runtime's reason for holding tiling is unchanged by his holding most of it.

*Instruments.* `scripts/probe_cursor.py`, smoked on six items per row before
the nine runs; each nano card under two minutes, the 100M about three, the
scorer's parse rows on R1 about four, beside the owner's chat server on the
same card with no timing number read.
