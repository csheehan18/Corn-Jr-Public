# Once the runtime enforces the label, a forged one is obeyed 36/36

**Full result:** The tag becomes the door, and the door is the runtime's: the role grammar alone takes the whole tree from eighteen and twenty-four to forty-five and fifty-one of sixty on an unmasked checkpoint, the structural mask costs nothing and adds nothing measurable, a forged tag is obeyed thirty-six of thirty-six once the copy is bound, and a follow-up composes what no copy slot can source

PLAN-TAG-SPINE rung 1 and the tail of rung 0, read 2026-09-12. Two nano
arms, `S` at two seeds, trained on arm B's file byte for byte under the
structural mask (`configs/mix_v3_decomp_s.py`, pre-registered before a byte
trained; a first seed discarded, below). Read against B's own cards, and --
because every piece of the binding except the mask is a decode-time
constraint -- read *on B as well*, so that mask, grammar and copy separate
on the same checkpoints. Nothing else retrained. Twelve readings of the
decomposition rows, seven forged-structure probes, four rung-0 probes.

## The question

Finding 130: a tag he *may* read is never read while the words decide the
call, at either layer, with or without the request under loss. PLAN-TAG-SPINE
§4 made the tag the door instead: while a call line is written the request
tokens of every other part are masked out of attention (trained and served),
the grammar admits only the declared tools of the focused leaf's role, and
the copy slot admits only the leaf's words and the last answer. **Does the
mask cost anything on trained rows, and how much of the door is the mask?**

## The answer: the door is the grammar and the copy, and both are the runtime's

    decomposition rows, 120/120/60/50     B    +role  +full    B s2  +role  +full    S-   +role  +full    S- s2  +role  +full
    parse.span                            77     77     77      78     78     78     79     79     79      82     82     82
    move.next                             96    114    116      97    114    117    104    116    116     102    114    116
    move.args                            120    120    120     115    118    120    118    120    120     113    119    120
    e2e.tree                              18     45     45      24     51     51     20     45     45      33     50     50
    e2e.rebind                            48     48     48      49     49     49     50     50     50      48     48     48

`+role` is `--role-bind` (the grammar admits the focused leaf's tools);
`+full` adds `--copy-bind` (the string slots copy from the leaf's words and
the last answer). `S-` is the masked checkpoint read under the mask alone.

**The grammar alone, on the unmasked B, takes the whole tree from 18 and 24
to 45 and 51 of 60, and the route from 96 and 97 to 114 and 114.** The
copy binding adds two on the route and takes `move.args` to 120 on every
checkpoint. **The mask adds nothing measurable**: S- sits inside B's band on
every row, and S under the same bindings reads what B does under them, seed
for seed. The parse rows are untouched everywhere, as they should be --
parse positions are unmasked.

The whole tree is near the world's ceiling under the binding: sixteen of
the sixty tree items declare two tools of one role, the generator always
takes the first declared, and the label cannot choose between them. The
`wrong_tool` that remains -- 9, 12, 6 -- lives inside that set.

**The band.** `tool.copy` 120/120 on both S seeds, `tool.copy_wide` 299 and
291, `temporal.*` flat. `tool.selection` reads 99 and 115 against B's 128
and 118, on the row whose seed spread has run to 35 on every arm that
carries the world (finding 129, 130): direction down, size unreadable at
two seeds, and it is the world's 5% declared-tools slice again, not the
mask -- S- and B share the file.

**The mask's cost.** 9% a training step compiled, measured before the run
(probe only -- not on disk); on the payload's own validation split the
masked call lines are *easier*, decomp 0.343 against 0.454, with every
other source within a hundredth -- a distractor removed, which is the
inductive bias doing its one job.

## The forged structure: invention, then obedience by construction

`probe_depth.py --forge label --structure`: the two children of a `do`
swapped, so the first call executes the span the forgery calls a lookup.
Readable denominator 36 of 60 -- the other 24 are items whose first call
was never the forged part, and they are exactly the "neither" every arm
since B has carried on this probe.

    of the 36 readable                      follows forged   follows gold   invents
    porous mask (first seed, discarded)          0               31            5
    mask                                         0                0        35 / 32
    mask + role                                  0                0        36 / 36
    mask + role + copy                       36 / 31              0        0 / 5
    B, never masked, + mask + role + copy       36                0            0

Three readings, in order. **The first mask was porous**: it hid the
request's other parts and left their copies on the parse line, and he took
the gold span from the line above 31 times -- caught by this probe on the
first checkpoint, the streams rebuilt so a part's words carry its id
wherever they appear, and on the porous checkpoint under the fixed mask the
gold span reads 0 of 30. **Under the tight mask he invents**: handed a
send-span with no subject in it, he composes one around the visible name --
`the founding year of Kelunlvstone` from `fire it over to Kelunlvstone` --
finding 98's mechanism arriving when the words are taken away. **Under the
copy binding invention is impossible** and he follows the forged tag 36 of
36 (seed 2: 31, five unparseable), copying a fragment of what he was shown
(`fire`, `along`, `send`) -- provenance guaranteed, sense not, because the
forgery gave the lookup nothing sensible to copy. And B, which never saw a
mask, reads 36 of 36 under the same three constraints.

**So "load-bearing by construction" is literal, and it is the runtime's
construction.** The weights contribute the parse. Everything that makes the
parse govern the call -- which tool, which words -- is a constraint at
decode that any checkpoint with the parse obeys.

## The one thing the copy slot could not hold: the follow-up

Under the copy binding as first written, `e2e.rebind` read **5, 28, 5, 28
of 50** where it reads 48-50. A follow-up's argument is the previous turn's
frame with a new entity bound in -- `the capital of spain` from `the capital
of france` and `what about spain?` -- which is a contiguous span of nothing
(PLAN-DECOMPOSE §4 says so; this is what it costs). So **the label decides
which binding applies**: `find`, `send` and `note` copy and are held to the
span and the answer; `follow` composes and is role-bound only. Under that
rule the table above holds and the re-bind is back at 48-50 everywhere.

## Rung 0's tail, corrected

The A1 probe (`scripts/probe_rolebind.py`) read the role door at +2 on
`move.next` because it kept its own leaf table -- no `do` leaf, no `follow`,
surface order -- and bound the wrong role where those govern. The scorer's
`--role-bind` on the same checkpoints is the read above: +18 on the route
and +27 on the tree. The probe now takes its tables from the one place that
defines them. A2 (the state line halving the repeat under the route header,
40 to 19 of 192) and A3 (his label a bag of words at 0.641 held out) stand
as read.

## What this licenses

PLAN-TAG-SPINE §8, rung 1's row: *S inside B's band on trained rows and the
copy band; copy under forged structure at or above 80%* -- both clauses
hold, the second under the full binding. **The gate to rung 2 is open**,
with the reading sharpened: the mask is not the door, the grammar and the
copy are, and they ship as runtime rules with no training run. What rung 2
asks is whether a label learned as a function can be *written* for a shape
he was never shown; nothing here touches that -- `parse.heldout` and
`parse.depth3` are zero on every reading in this finding, as on every arm
before it.

## Instruments

* The porous mask, caught by the forged probe on the first checkpoint and
  refused by `check_decomp_scorer.py` group 7, which now reads the visible
  text of a focused query and rejects any other leaf's span in it.
* `CopySpec` keys a slot by `(tool, slot)`, and the first copy binding passed
  bare slot names, which matched nothing; the walk test that caught it
  (`invented: accepted`) is the kind of negative control this repo requires.
* The probe's readable denominator is 36 of 60 and always was; every
  "neither" count on this probe since finding 129 is that set.
* `structure_for_text` disagreed with the generator's execution order on
  115 of 399 turns (`follow`) and then 16 (`do` as a leaf) before it agreed
  on 535; the guard holds the agreement.

## Limits

Two seeds per arm, so directions (rule 6). A dummy world whose labels are
lexical (A3), so a bound tag is only as right as the parse, and on unseen
carriers the parse is wrong. The mask's contribution is unmeasurable here
because the words never fail; a world where they do is rung 2's. The tree
ceiling from duplicated roles is the world's, and a description binding
(finding 34's) would lift it. The copy binding guarantees provenance and not
sense: under a wrong structure he copies a fragment, and the runtime that
ships this should treat a call whose argument is a lone word as a refusal
rather than an answer.
