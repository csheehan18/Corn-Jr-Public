# On a synthetic world he generalises labels but not one level deeper

**Full result:** On a world where the phrasing is useless for the label he cuts phrasings he never saw at every seed, repairs a wrong label after its bound call fails, parses a world he never trained on, holds the right label for a fourth level ninety-six of ninety-six times when the cut is given, and still writes no cut one level deeper than he was shown

**Cost:** 8.4 min of scoring on the 1 card first cited here (`nano100m_v3_funcworld_rope`); it also reads 1 card scored for an earlier finding (`nano100m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-TAG-SPINE rung 2, phase C4, read 2026-09-13. Six nano runs on
`configs/mix_v3_funcworld.py` -- the functional world `corn/funcgen.py` at
arm B's pledge, under the `repair` loss policy -- three seeds under RoPE
and three under learned positions, token- and iteration-matched to arm B,
pre-registered with the outcome table, the unreadable outcome, the kill
and the fallback before a byte trained. Floors: B's two seeds and C0's RoPE
seed 1 on the same rows. Every card full, every checkpoint through
`check_decode.py` (six of six parity), the bound partials under
`--role-bind --copy-bind`, the label-rank read and the structure-rank read
beside the greedy rows. Ten rows new (`w_*`, rule 2), eight old, the copy
band.

## The question

Finding 131 opened rung 2 with one question left: can a label learned as
*what a part does* be written for a shape he was never shown. On the old
world his label was a bag of words (0.641 held out against a majority of
0.269) and every held-out parse row read zero on every arm. `funcgen`
removed the two shortcuts that could be named and measured -- one lookup
pool serving `ask` and `find` with what follows deciding, and groups marked
on the surface so arity is decidable (the old `depth3` row was undecidable
on 96 of 96 items, finding 132) -- put a consequence under every label and
a cost under a wrong one, trained depths 1-3 and held out 4, and
`scripts/check_funcworld.py` held the bag-of-words bracket on the bytes:
`ask` against `find` at 0.524 held out, pairwise chance 0.556.

## The read

    row (of)                floors B/B2/RoPE   W-rope 1/2/3    W-wpe 1/2/3
    parse.w_span   (120)       14/12/11         60/62/66        54/54/53
    parse.w_entity (120)        6/ 4/ 6         41/42/42        31/35/34
    parse.w_heldout(140)        4/ 2/ 4         17/10/11        13/11/10
    parse.w_pairing (96)        0/ 0/ 0          0/ 0/ 1         0/ 1/ 0
    parse.w_depth4  (96)        0/ 0/ 0          0/ 0/ 0         0/ 0/ 0
    parse.w_repair  (60)        0/ 0/ 0         36/37/34        33/33/30
    move.w_next    (120)       77/80/88       104/103/98      104/110/112
    move.w_args    (120)      108/104/116     120/119/112     120/120/119
    e2e.w_tree      (60)        6/11/ 0         30/32/22        32/41/36
    e2e.w_rebind    (50)       48/49/49         50/48/49        48/49/48
    bound: move.w_next           --            107/109/105     108/109/109
    bound: e2e.w_tree            --             38/36/29        33/40/40

    old parse.heldout (120)  0 on every arm trained there   11/3/4   7/6/9
    old parse.span    (120)  77/78 on B                     60/64/63 64/59/62
    tool.copy         (120)  120/120                       120/120/120  109/120/120
    tool.copy_wide    (300)  296/289                       289/297/269  298/298/286
    temporal.copy     (353)  353 everywhere
    val_loss                 2.2899/2.3124/2.2236      2.2312/2.2549/2.2707  2.2967/2.3197/2.3311

**Every seed agrees, so this is a result and not a direction.** The
pre-registered table lands on its third row: **carriers transfer and depth
does not.** `parse.w_heldout` is above the floor at all six seeds, 10 to 17
of 140 against 2 to 4, and the gain lives on held-out cores under trained
modifiers (22 of 150 summed over the RoPE seeds, 15 over the wpe seeds)
and, smaller, held-out modifiers under trained cores (10 and 7 of 120);
both held out at once reads 6 and 12 of 150, at the floor. `parse.w_depth4`
is zero on greedy at every seed, and 268 of the 288 RoPE misses fall on the
first line. `parse.w_pairing` is zero to one. The kill did not fire: the
copy band holds, with one dip on each trunk at one seed (`tool.copy` 109 on
wpe seed 1, `tool.copy_wide` 269 on RoPE seed 3), the pattern findings 129
and 130 recorded on this row. The unreadable clause did not fire:
`parse.w_span` reads 60, 62 and 66 on RoPE, on the line and above it.

**Two things the table did not pre-register and the rows say plainly.**

*He repairs.* `parse.w_repair` gives him the wrong parse line, the bound
call it licensed and that call's failure, and asks for the corrected line:
30 to 37 of 60 at every seed, from a floor of zero on which the old-world
checkpoints answered `no_parse` 54 of 60 times -- they called again. The
misses are copy slips on the re-written spans (46 of the 96 RoPE misses),
not the label (5). The consequence built into the corpus under the binding
is read: a failed bound call is followed by a re-parse.

*He parses a world he never saw.* The old world's held-out row -- carriers
in none of W's pools, orders W trains -- reads 3 to 11 of 120 on every W
checkpoint where every checkpoint trained *on that world* read 0, and its
trained row reads 59 to 64 of 120 against B's 77 and 78 on carriers B
memorised and W never met. A label learned as a function on one world's
phrasings cuts another world's.

## Depth 4: a readout, partly, and an absence, partly

What he writes on a depth-4 item is not blank. Decoded by hand on three
items: in two he wrote a *legal, shallower* parse -- the deep group cut
into its members at level 1, his first line close to the gold's second --
and in all three the forty-token spans carried copy slips ("Zelathgard"
became "Zelvik", "once" became "since") and one label confusion
(`chat`/`social`). Two instruments read that apart from an absence:

*The structure-rank read* (`scripts/probe_structure.py`, written after the
first card): the gold line against the flattened line, teacher-forced.

    deep cut preferred (of 96)    W-rope 1/2/3    W-wpe 1/2/3     B (never saw W)
    depth 4, level 1              82/93/75        95/94/92        72
    depth 4, level 2              66/70/66        71/73/74        43
    depth 4, level 3              54/42/58        57/45/50        57

**This instrument is unpinned and B is its floor.** The flattened line
carries the same words under more label tokens, so total NLL favours the
gold on length alone -- B, which never saw this world, prefers the deep cut
72 of 96 times at level 1. Read as a bound: W sits above that floor at
levels 1 and 2 (75 to 95 against 72; 66 to 74 against 43) and at chance at
level 3, where the mean gap is within a nat of zero on every seed. So the
recursion is in the probabilities one and two levels down and not three: he
prefers to open a depth-4 group, prefers to open what it holds, and has no
preference about the innermost pair. A length-matched alternative is the
repair to this instrument; it was written the next day and reads the
innermost level the other way (the amendment below).

*The label-rank read* (`scripts/probe_rank.py`, lever 6): the gold parse
line teacher-forced against its single-label swaps over the same string and
spans, so the question is *given the cut, does he prefer the right label*.
Chance is one in 5.1 to 6.8 candidates a cell (0.16-0.22); B, which never
saw the world, is the floor. Cells are lines, one per level of an item.

    gold ranked first, of cells      B     W-rope 1/2/3      W-wpe 1/2/3
    parse.w_depth4   (384)          189   336/336/342       360/362/359
       of which level 4  (96)        52    96/ 96/ 96        96/ 96/ 96
       of which level 1  (96)        32    72/ 56/ 66        78/ 77/ 75
    parse.w_heldout  (254)           80   226/225/221       234/228/226
    parse.w_pairing  (288)          149   254/265/257       267/275/265
    parse.w_span     (186)           77   176/174/181       181/181/181
    parse.w_entity   (214)           86   206/205/210       204/201/208
    parse.w_repair   (109)           41   105/108/108       108/109/108
    mean gap, gold minus best alt   +0.5..+3.0 nats   -3.7..-7.4 nats on every W row and seed

**The labels are there when the cut is given, one level deeper than he
was shown.** On the depth-4 items the gold line is likelier than every
single-label swap in 0.875 to 0.943 of cells at every seed, and at the
innermost level, the one that does not exist in training, 96 of 96 on all
six checkpoints, against B's 52 and a chance of 16. The pre-registered
fourth row -- *greedy zero with the gold ranked first at every seed* --
lands on the label half of the parse: what greedy loses at depth 4 is the
cut and the copy (the hand decodes above: a legal shallower cut, slips
inside forty-token spans), not which label a part carries. The same holds
on the held-out row, where greedy reads 10 to 17 of 140 and the label rank
0.87 to 0.92, and on the repair row. The one cell where W is nearest its
floor is depth 4's *outermost* line (56 to 78 of 96 against B's 32): the
label of the whole group is the one he is least sure of, which is where a
shallower cut would begin. Read beside the structure read: the labels
transfer to the fourth level whole; the preference for the deep cut
reaches two levels down on an unpinned instrument; the innermost cut is
the absence.

On this read the trunks are the other way from greedy: learned positions
are above RoPE on `parse.w_depth4` at every matched pair (+24, +26, +17
cells) and on `parse.w_heldout` at every pair (+8, +3, +5). The trunk rule below reads
the greedy parse rows, as pre-registered, and this number goes to the mid
size's amendment.

## The trunk

RoPE against learned positions, matched pairwise at three seeds: above on
`parse.w_span` at every pair (+6, +8, +13) and on `parse.w_entity` (+10,
+7, +8); the language rows better by the same three per cent as finding
132 at every pair; `e2e.w_tree` the other way (30/32/22 against 32/41/36).
The rule the C0 read pre-registered -- the mid size takes the trunk the six
nano cells prefer on the parse rows -- names RoPE, and the two mid runs are
`configs/nano100m_v3_funcworld_rope.py` and its seed-2 twin.

## What this licenses

The third row's consequence: **rung 4 on the real carriers, with depth a
runtime matter.** The bindings of finding 131 carry to the real generators
with a functional-label claim attached at last -- a label learned as what a
part does transfers to phrasings it never saw, on this world and across
worlds -- and the parse of a nesting deeper than trained is the stepped
protocol's job (PLAN-DECOMPOSE arm D) rather than a bigger corpus's, until
a length-matched structure read says the deep preference reaches level 3.
The fourth row's consequence rides beside it: the labels for a depth-4 cut
are in the weights (96 of 96 at the innermost level on every seed), so the
next arm on depth is a constrained decode of the parse line -- spans held
to the copy binding, labels free -- and not a corpus that shows him depth 4.
(Run the next day, the amendment below: it lifts the copy slips and not the
cut, so it ships for the parse line and the depth question moves to a dose
arm.)
The repair row goes to the runtime as it stands: after a bound call fails,
hand the failure back and let him re-parse; he does, at nano, on a world
where nothing else does. The mid size runs RoPE, two seeds, to say whether
the read holds with scale (lever 5).

## Instruments, and what was caught before it could count

* The first build dropped half its draws to the block and lost the deep
  shapes -- 0.7% of turns at depth 3; the plan is drawn before the words
  and re-phrased under the block, the deep and repaired shapes are lean,
  and the lookup observation carries its answer alone.
* The scorer oracle refused the first `e2e.w_tree` items: a `find` inside
  a `do` is consumed and never said, and the gold answers had counted it.
* `probe_rank.py` was serial; batched, held within 1e-4 nats of serial
  with a control (`check_rank_batch.py`), which took the rank stage from
  fifty minutes to ten.
* The structure read's length confound, above: named, floored on B, and
  read as a bound.
* Six checkpoints through `check_decode.py`, all parity.

## Limits

Nano, on a dummy world, and the held-out gain is on held-out cores under
trained modifiers: with both held out he reads at the floor, so a fragment
still votes when nothing around it is familiar. The depth-4 items are an
extrapolation from a thin base -- 8.1% of turns at depth 3, one nesting
seen more than once -- and the structure read that says the preference
reaches two levels down is unpinned. The cross-world row is 3 to 11 of 120
and is reported, not claimed. Nothing here touches the shipped checkpoint.

## Amended 2026-09-14 -- two reads with no training, on the same six checkpoints

The owner asked whether depth 4 had been shown to work, and the honest
answer above rested on one unpinned instrument. Two more were built the
same day, both decode-time, both run on the six W checkpoints and B beside
the first mid-size run: the length-free structure read, and the parse line
decoded under its own grammar.

**The length-free structure read** (`probe_structure.py`'s `div` columns):
the deep and flat lines share every token up to the first that differs --
the deep span continuing where the flat one closes, or the group carrier
opening where a member would -- and at that one position a single
distribution gives a probability to each. No length enters it; chance is a
coin; B is the floor.

    gold's token likelier, of 96     B     W-rope 1/2/3     W-wpe 1/2/3     mean log-ratio (flat minus gold), W
    trained groups, l1 (of 58)      24     55/52/57         53/51/52        -3.9 to -5.5
    trained groups, l2 (of 14)       8     14/13/13         13/13/13        -6.2 to -9.4
    held-out pairing, l2            47     57/53/60         47/54/52        -1.6 to -3.7
    depth 4, level 1                54     69/76/65         81/77/82        -3.0 to -6.1
    depth 4, level 2                37     59/58/62         50/57/54        -1.2 to -3.4
    depth 4, level 3                 8      7/ 3/19          3/ 3/ 3        +1.9 to +3.5

**He opens a group at the depths training showed and prefers the flat cut
at the one it did not, on every seed.** Levels 1 and 2 of a depth-4 tree
sit above B by 11 to 28 and 13 to 25 cells; level 3 -- the nesting depth
no corpus group reaches -- sits at B's floor with the flat continuation
likelier by two to three and a half nats. The total-NLL read's "chance at
level 3" was the length confound hiding a preference: it is not chance, it
is the other way. The held-out pairings at a *trained* depth read the same
absence on their inner level (47 to 60 of 96, a coin), so what he has is
not "depth 3" but the nestings depth 3 showed him.

**The parse line under its own grammar** (`scripts/probe_parsebind.py`):
`corn/grammar.py`'s `ParseConstraint`, built for PLAN-DECOMPOSE §4 and
never wired to a decode, holds every span to a word-bounded substring of
its parent and every label to the closed set -- spans held, labels free,
the arm this finding proposed. Each cell decoded twice from the same
teacher-forced prompt, free and bound, scored exactly.

    free -> bound, of n              B        W-rope 1/2/3                W-wpe 1/2/3
    w_span    l1 (120)            14->15    67->72  69->74  70->74     61->66  63->68  58->65
    w_heldout l1 (140)             4-> 7    19->26  14->20  16->22     16->22  17->21  14->22
    w_heldout l2 (101)             0-> 1    24->30  25->37  27->34     25->31  28->32  23->30
    w_pairing l3  (96)             0-> 0    33->44  30->40  23->44     26->28  38->41  28->28
    w_depth4  l1  (96)             0-> 0     7-> 8   6-> 9   7-> 9      6-> 8   8->16   8->11
    w_depth4  l2  (96)             0-> 0    11->18   8->12   8->10      9->14  11->15   3-> 5
    w_depth4  l3  (96)             0-> 0     1-> 1   1-> 1   7-> 7      0-> 0   1-> 1   0-> 0
    w_depth4  l4  (96)             0-> 1    55->60  43->44  59->62     12->22  22->23  17->20

**The grammar removes the copy slips and not the cut.** Bound, every
trained and held-out row rises by four to twelve cells at every seed --
`wrong_span` misses become passes, and a span that is not in the request
can no longer be written -- and the innermost pair of a depth-4 tree,
given its parent, reads 20 to 62 of 96. Level 3 does not move: 0 to 7 of
96 free and bound, with `wrong_span` on 63 to 95 of the misses -- right
arity, right label, the member's span where the group's should be, which
is the flat cut the structure read measures from the other side. So the
whole-tree `parse.w_depth4` stays at zero under the grammar, and stays at
zero for one reason that two instruments now agree on.

**What this changes.** The fourth row's consequence is narrowed: the
constrained decode is worth shipping for the parse line (it buys the same
four to twelve cells on the rows he can cut, for nothing), and it is not
the next arm on depth. The label half of depth 4 is a readout failure; the
cut half is an absence, learned as the depths shown rather than as a rule.
Whether that absence is a dose -- depth 3 is 8.1% of turns, almost every
nesting once -- or a limit of the size is the question the owner then put,
and it is pre-registered as phase C5 in `configs/mix_v3_funcworld_dose2.py`
and `_dose3.py`: the same world with the depth-3 share at 0.142 and 0.202
delivered, every holdout W's, read on level 3 of this instrument. The rule
cell (train 1-4, hold out 5) does not fit a 512 block -- a depth-4 row is
274-374 tokens before its calls -- and waits on the block decision.

*Instruments.* The `div` read and the parse constraint were smoked on B
and on three items before the runs; the seven structure cards took a
minute each and the seven constrained decodes about twenty, beside the
mid-size run's training, with no timing number read from either. The
first mid-size seed is training as this is written; its second seed was
dropped by the owner in favour of the dose arm, so scale is read from one
seed as a direction.

## Amended 2026-09-14, later -- the mid size, one seed, read as a direction on scale

`configs/nano100m_v3_funcworld_rope.py`: 12 x 768 under RoPE on the same
mix, 16,196 iterations and 398M tokens (the world seen 2.9 times where
nano sees it once), 9,498 s on a card that carried the constrained decodes
of the amendment above for its first two hours (no timing number is read
from it). Its seed-2 twin was launched and killed at once by the owner's
call to spend the card on the dose arm instead, so **scale is read from
one seed and is a direction** (rule 6). `check_decode.py` 96/96 static,
graph and bucketed; prefix reuse 24/24. The full card, the bound partial,
the label-rank read, both structure reads and the constrained decode.

    row (of)                    100M RoPE      nano RoPE 1/2/3     nano wpe 1/2/3
    parse.w_span   (120)            94           60/62/66            54/54/53
    parse.w_entity (120)            84           41/42/42            31/35/34
    parse.w_heldout(140)            14           17/10/11            13/11/10
       cores / mods / both        5/4/5
    parse.w_pairing (96)             5            0/ 0/ 1             0/ 1/ 0
    parse.w_depth4  (96)             0            0/ 0/ 0             0/ 0/ 0
    parse.w_repair  (60)            45           36/37/34            33/33/30
    move.w_next    (120)           118          104/103/98         104/110/112
    e2e.w_tree      (60)            56           30/32/22            32/41/36
    bound: e2e.w_tree               56           38/36/29            33/40/40
    tool.copy / copy_wide / temporal.copy   120 / 299 / 353
    web / narrative / conv. nats a byte     0.764 / 0.364 / 0.406   against 0.858 / 0.436 / 0.496 at nano
    val_loss                      1.939        2.231/2.255/2.271

    label rank, gold first          100M          nano RoPE 1/2/3
    parse.w_depth4 (384)            367           336/336/342     level 4: 96/96 at every size
    parse.w_heldout(254)            236           226/225/221

    structure, deep_div of 96       100M   gap    nano RoPE 1/2/3    B
    depth 4, level 1                 88   -8.1     69/76/65          54
    depth 4, level 2                 64   -5.0     59/58/62          37
    depth 4, level 3                  4   +4.0      7/ 3/19           8

    constrained decode, free -> bound   100M            nano RoPE 1/2/3
    w_span    l1 (120)               99 -> 100       67->72  69->74  70->74
    w_heldout l1 (140)               21 ->  26       19->26  14->20  16->22
    w_depth4  l1  (96)               17 ->  25        7-> 8   6-> 9   7-> 9
    w_depth4  l3  (96)                2 ->   2        1-> 1   1-> 1   7-> 7    (`wrong_span` 92 of 94 bound misses)
    w_depth4  l4  (96)               73 ->  82       55->60  43->44  59->62

**Scale buys the trained world and the language rows, and nothing on the
two rows this rung exists for.** Trained shapes 94 of 120 against 60-66,
unseen entities 84 against 41-42, the repair 45 of 60, the whole tree 56
of 60 under the binding where nano's best is 40, the language rows better
by eleven to seventeen per cent -- and `parse.w_heldout` at 14 of 140,
inside the nano band, with the three carrier holdouts at 5, 4 and 5; and
`parse.w_depth4` at zero. The labels are finished at this size (367 of 384
depth-4 cells rank the gold first; level 4 is 96 of 96 at every size and
seed) -- **read as a bound**: the floor under every rank and structure
number here is a 20M checkpoint, and a ranking instrument answers to
size on its own; the 100M floor is `nano100m_v1`, which never saw a parse
world, ranked and structure-read behind the dose chain. **Read**: two
seeds of `nano100m_v1` rank the gold depth-4 line first 218 and 214 of
384 against B's 189, so size alone buys the instrument about thirty
cells and the trained 367 is mostly capability; at the innermost level
the floor is already 84 and 86 of 96, so "96 of 96" at this size is a
gain of a dozen over its own floor and not of forty-four; on held-out
carriers the floor is 52 and 46 of 254 against 236. On the length-free
structure read the 100M floor is a coin at every depth-4 level (46/64/59
and 40/73/52 of 96, gaps within a nat of zero), so the trained
checkpoint's 4 of 96 at level 3 sits fifty-five cells *below* its own
size's floor: **the flat preference at the unseen depth is learned from
the world, not carried in by the trunk**, which is what a table of
depths does with a depth it does not hold. **The inversion at the unseen depth is stronger with scale, not
weaker**: at level 3 of a depth-4 tree the flat continuation is likelier by
four nats, 4 of 96 against nano's 3 to 19, while levels 1 and 2 climb to 88
and 64. The constrained decode reads the same wall from the other side:
level 3 stays at 2 of 96 bound with `wrong_span` on 92 of the misses, the
member's span where the group's should be, while every level training
showed him rises (the innermost pair to 82 of 96, trained shapes to 100 of
120).

**So at one seed the size is not the lever on depth, and it is not the
lever on held-out carriers either.** What 3.4x the parameters and 2.9x the
exposures bought is more of the depths shown and a sharper refusal of the
one not shown, which is what a rule learned as a table of depths looks
like as the table is learned better. The mid-size read would have been a
result at two seeds; the owner spent the second seed on the dose arm
(phase C5), which asks the question this leaves: whether the wall moves
with how much depth 3 he sees. The trunk decision for PLAN-1-0 §10 gains
one number it did not have: RoPE at 100M reads the language rows 11-17%
under nano's, in line with finding 132's three per cent at equal size.
