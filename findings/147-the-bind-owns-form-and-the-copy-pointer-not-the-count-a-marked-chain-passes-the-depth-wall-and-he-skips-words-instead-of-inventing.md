# One hundred and forty-seventh finding — the nested bind owns the form and the copy pointer, not the count: invented spans, repeats, splices and swapped number words go to zero, legal lines go from 516 to 2,917 of 3,456, and a marked chain passes the three-level depth wall for the first time, while where a group closes, whether a nested group opens at all and which request words he drops stay his -- he skips words where he used to invent them, and the `struct` column's rise on nested rows is half a broken line becoming readable

**Cost:** about 100 min of GPU, no training -- 20 min for arm F seed 1's six cards (2026-10-01, 22:13-22:33) and 80 min for the other 26 (2026-10-02, 08:55-10:15), a bound ladder or nestgen card 4-6 min except on G2 seed 2, where the stranding hole below took them to 13.5 and 10.3 min; the read, its tables and the grammar repair on CPU, under 5 min.

PLAN-TAG-LANGUAGE §6 rung 0 and SPEC-LANGUAGE §9, read 2026-10-02. The
decode-time bind for the nested parse line (`ParseConstraint(line="nested")`,
`corn/grammar.py`, with the four rules rung 0's first decodes added at
`59cc8f8`) against free greedy decoding on the four checkpoints on disk: arm F
(`nano20m_v3_fw_armf`, seeds 1337 and 2337) and arm G2
(`nano20m_v3_fw_ladder_add`, both seeds). No weight trained. The bound decoder
is `probe_nestgen.bound_line`: greedy wherever a token is legal, and it takes a
token back when stranded. Instruments: `probe_ladder.py` (576 lines a
checkpoint), `probe_nestgen.py` (288), and the two
hand probes, `probe_hand_arity15.py` and `probe_hand_depth.py --marked`, run
by `scripts/run_rung0.py`; read by `scripts/read_rung0.py`, which decodes
nothing. **Cards:** `evals/results/<ckpt>__r0_*` and `evals/results/rung0.json`
-- arm F seed 1's committed at `444dd67`, the rest land with this finding.
`read_rung0.py`'s second table, added for this read, and the hand counts are
a hand-built reader over those cards, checked against the probe's own
`struct` to the line but not pinned by a guard, so **every number below is a
bound** (rule 28).

**The pre-registered expectation** (PLAN-TAG-LANGUAGE §6, before any bound
line was decoded): repeats, splices, invented spans and unbalanced lines
vanish; the depth ceiling and the flattening do not. Three of those four held.
The depth ceiling did not.

## What the bind owns -- form

Pooled over both probes, all four checkpoints (3,456 lines an arm):

    species                       free      bound
    legal                          516      2,917
    invented span                1,255          0
    out of order (repeat/splice)    81          0
    unbalanced                   1,604        334
    case (a capital lowercased)      0        205

Per row, free legal is 1-29 of 96 and bound 49-94 of 96 (`read_rung0.py`'s
first table). Invented and out-of-order are zero on every row of every
checkpoint, as the grammar guarantees. **A line he already had right comes
back byte-identical**: 504 of the 516 free-legal lines; the other twelve are
lines the stream is stricter about than `nested_accepts` (a word between two
top-level parts, a leading space). On the ladder the number word follows the
same rule -- "a run of three" written for "a run of four" goes from 118 lines
to 0, and the request's number words survive whole on 902 lines against 608.

## The `struct` question, settled by reading

The ladder's `struct` rises on every nested row (arm F `nest4` 0 -> 21,
`nest3` 6 -> 22) and is flat or down on outer rows. Three things are mixed in
that column, and reading the lines separates them.

**It cannot read a line that runs out.** `probe_ladder.py` scores structure
through `parse_nested`, which raises on an open bracket, so a free line that
never closed scores `struct` false whatever it wrote -- 225 of the 1,152
free nested-row lines cannot be read at all, of 570 unbalanced one way or the
other. Closing each free line's brackets at its
end and scoring again is what the bind would get for making lines readable
and nothing else.

**It passes a k-member group of the wrong lookups.** So `read_rung0.py`'s
second table adds `group`: a group at the row's position whose members are
the gold group's lookups. Pooled over the four checkpoints, 1,152 lines a
cell:

    position   column   free   free, closed   bound
    nested     struct     72        161         240
    nested     group      32         83         135
    outer      struct    392        415         359
    outer      group     285        298         271

On nested rows **half the `struct` rise is a broken line becoming readable**
(72 -> 161 of the 72 -> 240), and **only 130 of the 240 bound `struct` hits
are the right group** -- the rest are a group of k members in the wrong place,
often inside the label stacks below. On the right-group column the bind's own
contribution is about 50 lines of 1,152 (83 -> 135): **real, and small.**

**What the real part is, read on 16 pairs where the bound line has the gold
group and the free line does not** (four a checkpoint): one mechanism. Inside
a top-level part the bind admits no jump -- the part's words must be one
contiguous stretch of the request -- so the inner carrier the free line
skipped or rewrote has to be copied: "four in one go" (free: dropped, or
"two go"), "the four together" ("the three"), "a triple", "all four", "i only
need in one go", "both". With the carrier written he opens the group at it,
and the members follow. A refused repeat does the rest: arm F `flad-027-nest4`
wrote "the same for the chief export of Orlunstad" twice for five members,
and bound wrote it once for four. The group is right; the line around it
usually is not (whole-line exact match is 0-3 of 288 nested lines in either
arm), because of what the bind leaves to him.

## What is left to the weights -- structure and vocabulary apart

    left to him                      column       free -> bound (ladder, 2,304 lines)
    where a group closes             structure    arity hand probe: no width past ten
    whether a nested group opens     structure    nested items with none: 819 -> 561 of 1,152
    empty wrappers                   structure    one-member groups: 188 -> 2,891
    which request words to drop      coverage     legal lines dropping 5+ words: 35 -> 499
    which label                      vocabulary   an invented `do`: 359 -> 413

**He skips where he used to invent.** Legality never required coverage: a
top-level part may start anywhere after the previous one ends. When the bind
refuses the word he wanted, the best legal move is often a later word -- arm F
seed 2 `flad-039-outer4`, "i ought to know four things: the chief export of
Fenennddia, the currency of Halirvik, ..." comes back
`social[i ought to know] ask[halirvik, ask[the currency of Ithithnia] ...`,
a carrier and two members gone. The gold never leaves five request words
uncovered; 499 of the 2,026 bound legal ladder lines do, against 35 of 413
free. **Nearly all of the `case` species is this skip landing on a name**: 200 of its
205 lines open a part on a capitalised request word written lowercase, which
the one-way fold (D-A1.14) admits, and 159 drop five words or more. On outer
rows this is why the bind costs a little: where the free line invented the
outer carrier ("have a spare minute", "it's one", "daft") and still counted
four, the bound line skipped past it.

**A refused word leaves empty labels behind.** A label is legal at any word
edge up to three in a row (MAX_OPEN_RUN, the corpus's own maximum), so when
the next word is refused the open is the best legal token:
`find[find[note[four in one go, ...`, `social[chat[social[and]]]`. Lines with
three labels open in a row go from 2-9 to 118-172 of 288 on nested ladder
rows; one-member groups from 92 to 2,616 there. They are legal and wrong.

**He still flattens** (finding 143): with every free line closed so it can be
read, 819 of 1,152 nested ladder items have no nested group of two or more;
bound, 561. A third fewer, and still most.

**The count is his.** The arity hand probe (four phrasings and a control at
arities 2-15, 160 cells an arm across the checkpoints): every member copied
once in 53 cells free and 114 bound, the right width with every member once
(`clean`) in 36 and 75, unbalanced 77 of 200 rows and 0. But no cell at
twelve is clean in either arm, and where the bind made the copy perfect the
close is still his: arm F seed 2 at fifteen writes all fifteen members once,
in all four phrasings, and closes the group before the last ("... and the
river through Corithburg" as a sibling) -- width 14; G2 seed 1 at six closes
after four.

## The depth wall falls on a marked chain

**This is the half of the expectation that failed.** `probe_hand_depth.py
--marked` puts a carrier at every level ("the two, A and the pair, B and ...");
its column is carrier levels reproduced in order, `ask[<carrier>, ask[<member>]`.
On the 72 items with four or more carriers (18 a checkpoint, three a depth at
6-15), free decoding never runs past three -- the wall this probe found on
2026-09-25 -- and bound:

    items with 4+ carriers           free    bound
    run of 4+ from the top            0/72   20/72
    4+ found in order                 0/72   45/72
    the whole chain                   0/72   11/72
    longest run                       3      13 of 13 (G2 seed 1, depth 15)

Read by hand on G2 seed 1's first depth-15 item: free rewrites the first
carrier ("upper,"), fuses the next two, then jumps to the twelfth and loops
on it -- "the two things, the river through Elmeholm" three times; bound
opens all thirteen in order, each over its member. That is finding 145's
diagnosis from the other side: the wall was the copy pointer jumping and
looping at a carrier, not the depth, and the bind forbids both inside a part.
**What it does not buy is the tree**: the exact shape is right on no item
free and on at most 2 of 3 a depth bound (at depth 4-5 only), because the
bound lines carry the empty wrappers (deepest bracket 30 where the gold has 15) and
the outer core still splits off (the level-1 boundary, finding 138). Three
items a depth, one greedy draw: a hand probe, not a measurement.

## The residue the bind leaves unbalanced, and one more hole

**Of the 334 bound lines that never close, 186 are one hole in the grammar
and 148 are the token limit.**

*The hole* (pops of 100 or more, 170 of the 186 on G2 seed 2). At the
request's last word that seed ranks a fresh label above the closing bracket,
and the grammar let a child open there with no word left to fill it:
`the three of them]]]]social[follow[fi`. Every continuation strands; the
decoder takes tokens back one at a time and walks the label stacks behind it
-- eight labels, three deep -- until its budget of four steps a token runs
out, 345-424 pops a line. Replayed byte by byte under the grammar the cards
were decoded with, all 186 are legal to their last byte with the top part's
words already at the request's end. This
is why G2 seed 2 reads worst (bound legal 459 and 182 against 512-542 and
231-243) and why its bound cards took twice as long; its depth-12 marked
chain ends the same way, the whole chain written first (10 of 10, then
`]]]]]]ask[follow[follow[`), and every one of its marked items from depth 8
reads unbalanced. The top-level space
already had this refusal and a child did not. **Closed after the read**:
`_room_ahead` in `corn/grammar.py` refuses a child's label where the request
has no byte left after the words so far; `check_grammar.py` group 12 holds it
with three prefix cases, and it refuses nothing legal -- every generated tree
in the group, every user-turn tree of `funcworld_armf.txt` (20,370),
`funcworld_ladder.txt` (19,245) and `funcworld_four.txt` (1,948), all 576
ladder golds, and all 3,122 bound lines of this read that closed still
stream, while all 186 stranded tails are now refused at the open (and 9 of
the 148 below). **The cards predate it**; G2 seed 2's bound cards were
re-run under it the same day -- see the amendment at the end.

*The token limit* (220, the probes' default; every gold fits, the longest at
219 tokens). These 148 lines wrap words one at a time --
`social[chat[chat[over]]] social[chat[chat[and]]] social[chat[chat[above]]]`
-- three labels a word, so a request whose gold takes a median 121 tokens on
`w_d5` runs out before its end. Mostly `w_d5` and the long nested rows.

**And the bind cannot write a fifth of `w_d5`'s golds**: 19 of its 96 open four
labels in a row, which MAX_OPEN_RUN refuses (the same 19 with or without the
repair; none at a cap of nine). The held-out depth-5 row is capped by the
bind's own rule.

## What it licenses

**The split the rung was for, measured.** The runtime can own the form --
every invented span, repeat, splice and swapped number word -- and, by owning
form, the copy pointer inside a part, which is what carried the marked chain
past the depth wall and repaired about one nested group in twenty. The
weights keep where a group closes, whether a nested group opens, which label,
and coverage; under the bind the last one changes species, from an invented
span to a skip, and the skip is legal. **A bind armed in H3 needs three
things this read names**: the backtracking decoder (SPEC-LANGUAGE §9 says so
already), the `_room_ahead` refusal, and something for coverage -- a top-level
part that starts at the request's next word or after a connective (the gold
never skips five) -- which is not built and would need its own
refuses-nothing-legal proof against the generators' connectives. The empty
wrappers are a decoder question, not a grammar one: the stacks are legal and
trained, and greedy reaches them only because the word he wanted was refused.

**What it does not say.** That the bind makes him better at nesting: the
right-group gain is about 50 of 1,152 and mostly a carrier he was made to
copy. That depth is solved: one hand probe on a chain marked at every level,
three items a depth, one greedy draw each. Or anything about the copy-pointer hypothesis beyond this: holding the
pointer inside a part fixed the copy at arity, the chain at depth and some
nested groups together, and did not fix the close. Nano, the synthetic world,
one greedy decode a line.

## Amended 2026-10-02 -- G2 seed 2 re-run under `_room_ahead`

The re-run took ~25 min of GPU: the four bound ladder and nestgen cards of
`nano20m_v3_fw_ladder_add_seed2` re-decoded under the repaired grammar (the
pre-repair cards are replaced in `evals/results/`; `rung0.json` re-read).

The stranding hole was G2 seed 2's whole deficit. Under the repair its bound
ladder reads 534 legal of 576 (from 459) with 13 unbalanced (from 107), its
nestgen 244 of 288 (from 182) with 21 (from 98) -- inside the other three
checkpoints' band (512-542 and 231-243). Its `struct` on the nested rows
moves with legality, 42 -> 72 on the ladder and 44 -> 84 on nestgen, the
same half-readability the struct section above names; nothing here re-opens
that verdict. Pooled over all four checkpoints, bound legal is **3,054 of
3,456** (the headline's 2,917 was before the repair), bound unbalanced 163
(from 334), the case species 239 (from 205 -- more lines close, and a closed
line can carry a lowercased capital). The other rows of the headline and
every free column are unchanged. Probe only for the second table's columns,
as before: a hand-built reader, every number a bound.
