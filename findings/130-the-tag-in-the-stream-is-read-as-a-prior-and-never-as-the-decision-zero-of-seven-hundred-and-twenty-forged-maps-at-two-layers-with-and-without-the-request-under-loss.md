# A label in the text is a hint, never the decision

**Full result:** The tag in the stream is read as a prior and never as the decision: zero of seven hundred and twenty forged maps at the embedding and at block 2, with and without the request under loss, while the pass schedule costs a fifth of the parse rows and the map gives none of it back

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Eight nano arms trained 2026-09-12 to `docs/PLAN-LOOP.md`: F (the tag map
added to the embedding), G (the same loss schedule with no map), H (the map
added to the residual entering block 2), two seeds each and pre-registered in
`configs/mix_v3_decomp_f.py` before a byte trained; and F2, a **post-hoc**
arm designed after F was read, two seeds, registered as post hoc in the same
file and in PLAN-LOOP §5. All four read arm B's file `data/raw/decomp_b.txt`
byte for byte (rule 1) under a new loss policy; all compiled; B's own cards
(finding 129) are the untouched comparison. Nothing else retrained. Scored
under `--decomp-arm F` (one prefill per level with the map the prompt's
parse lines imply) for F, H and F2, and under B's protocol for G.

## The question, and the read that set it up

Finding 129 read five text-tag arms at 0 of 60 on every forced probe, and
the repair arm E -- position no longer predicting execution order -- read
the same zero on the label forgery at both seeds. Before this run,
`scripts/probe_taglayer.py` read the residual stream directly: **a linear
probe reads each request token's part label at 0.82 on unseen strings in
`nano20m_v3`, a checkpoint that never saw a `parts:` line**, peaking at
blocks 2-3 and holding within two points through block 7; the parse arms
sit 1-4 points above the world-only arm A. So the acting layers already
have a label for every token by block 2, computed from the words, and a
text line forty tokens later is a second copy of it. **Does the same tag,
moved onto the tokens it labels and added to the stream, get read by the
layers that act?**

## The gate: no

`scripts/probe_depth.py --probe forced --forge label`, greedy, the spans
kept and the labels swapped, scored on the argument. `--inject both`
prefills the forged prompt with the map its forged line implies; `--inject
map` prefills the *gold* prompt with the *forged* map, so text and stream
disagree and the argument says which he reads.

    label forgery, 60 cases       text     line+map    map only    gold cell
    F      seed 1                 0/60       0/60        0/60       38-39
    F      seed 2                 0/60       0/60        0/60       36
    H      seed 1                 0/60       0/60        0/60       38-39
    H      seed 2                 0/60       0/60        0/60       37-38
    F2     seed 1                 0/60       0/60        0/60       35-36
    F2     seed 2                 0/60       0/60        0/60       36-37
    G      seed 1 / seed 2        0/60       --          --         39 / 35
    B, D, E (finding 129)         0/60       --          --         36-45

**0 of 720 injected forged maps** on six checkpoints, and 0 of 480 text
forgeries on the eight new ones, with every gold cell where B's is. The
control is not at ceiling on this forgery -- it requires the exact subject
string -- and it is the same 36-39 on every arm, so the zeros are read
against a working instrument.

## The map is read -- as a prior, at the wrong place

The tag table trained: row norms 0.47-0.68 (F), 1.11-2.34 (H), 0.59-1.07
(F2) against an init of 0.45. On the payload's own validation split, the
true map lowers the loss and a label-permuted map raises it, and the
per-kind split says which tokens are doing the reading:

    val:decomp loss by target, loss-bearing targets      true map   no map   permuted
    F    utterance words                                   1.237     1.263     1.466
         parse lines                                       0.065     0.069     0.071
         call lines                                        0.128     0.129     0.134
    H    utterance words                                   1.228     1.238     1.264
         call lines                                        0.130     0.130     0.131
    F2   parse lines                                       0.072     0.084     0.106
         call lines                                        0.122     0.129     0.147
         say                                               0.433     0.451     0.467

Under F the map's content is read strongly at the request's own words, where
a label predicts the next word of its span (`B-find` -> "look up"), and the
call lines move a thousandth of a nat. The utterance loss that the "pass"
policy kept to bound the loss-free run was where the table's gradient came
from. **F2 removed it** (context loss on the `tools:` declaration instead,
`loss="pass_decl"`, same draws and same map): the calls then read the map
three times as much -- a permuted map costs 0.019 nats there -- and still
not one of 120 forged maps changed an argument. Teacher-forced on the
forgery cases, the gold argument's NLL under F is 0.0191 with no map, 0.0162
with the gold map and **0.0164 with the forged map**: any map makes the
right argument likelier by the same amount, and which labels it carries is
worth two ten-thousandths. H, at the layer where the internal feature forms,
reads it less than F everywhere.

The mechanism is finding 129's, one level down: the words already determine
the call, so no loss ever has to prefer the tag, and what he learns is a
prior that the words override. Adding the signal at the layer that computes
the feature does not change that; removing the competing gradient triples a
number that was a thousandth.

## The behaviour rows: F equals G, and the schedule costs

    row                B       B s2     F       F s2     G       G s2     H       H s2     F2      F2 s2
    parse.span        77/120  78/120   60/120  66/120   59/120  59/120   59/120  57/120   59/120  60/120
    parse.entity      71/120  77/120   49/120  51/120   49/120  51/120   48/120  55/120   45/120  54/120
    parse.heldout      0       0        0       0        0       0        0       0        0       0
    parse.depth3       0       0        0       0        0       0        0       0        0       0
    move.next         96/120  97/120   95/120  94/120   95/120  92/120   92/120  91/120   98/120  93/120
    move.args        120/120 115/120  113/120 113/120  116/120 118/120  116/120 116/120  115/120 113/120
    e2e.tree          18/60   24/60    11/60   14/60     9/60   15/60    11/60   12/60    14/60   12/60
    e2e.rebind        48/50   49/50    46/50   46/50    49/50   49/50    47/50   47/50    48/50   45/50

**The map changes nothing behavioural**: F, G, H and F2 sit inside each
other's seed spread on every row. **The pass schedule costs against B**:
about 18 of 120 on trained parse shapes, 22 on unseen entities and 8 of 60
on the full tree, on every scheduled arm alike -- the price of loss on 29%
of the payload's tokens where B bears it on all of them, declared in
advance as G's job to measure. The rows are far from zero, so the
pre-registered "unreadable" clause does not apply and the fallback (the
payload doubled) was not needed. `parse.depth3` read through F's third
prefill is zero like everything else, as PLAN-LOOP §3 said it would be:
pass 1 is the same parser.

## The band

`tool.selection` reads 123/128 (F), 104/139 (G), 118/146 (H), 114/140 (F2)
against B's 128/118, with seed spreads up to 35 -- finding 129's sentence
again: the direction is the world's 5% declared-tools slice and the size is
not readable at two seeds. `tool.copy` dips to 108-109 on one seed each of
F, G and F2 while H holds 119/120 and the other seeds hold 118-120; the
dips land on the map-less arm as readily as the mapped ones, so they are
not the map, and finding 129's compiled control already read 103 on the
same row. `tool.copy_wide` 289-300, `temporal.route` 394-399,
`temporal.copy` 353/353 everywhere. No arm fails the copy band relative to G.

## What this licenses

PLAN-LOOP §6's pre-registered third row: **"an additive tag is not read at
this scale either; position iv (attention structure) is the next arm, or
stop."** With F2, the one confound the table did not anticipate is closed
too. The map's content is demonstrably in the stream and demonstrably
readable -- the permuted map costs a tenth of the payload's loss -- and it is
never what decides a call. A tag that is to govern what he does has to be
the door the decision goes through, not a signal beside it:
`docs/PLAN-TAG-SPINE.md` is that design, and the owner's direction of the
same day.

## Instruments, and what was caught before it could count

* **The id scheme changed while building, and the plan says so.** A
  label-only map makes `ask[...] ask[...]` one region; the map went to
  begin/inside pairs (17 ids) before any arm trained.
* **The batcher's per-source glob took the new tag files for token
  streams.** Found by a six-iteration smoke run of the real trainer before
  the arms, not by a guard, and fixed in `corn/data.py`.
* **The trunk init would have differed between a tagged and an untagged
  config at one seed** because the table's construction consumed the global
  generator. Caught by `scripts/check_model.py`'s first run; the table is
  drawn off a forked generator, and the guard now holds the trunk equal.
* **The scorer's map is the build's map by construction and by guard.** One
  parser in `corn/tagmap.py` cuts both; `scripts/check_decomp_scorer.py`
  re-derives forty rendered documents to one (turn, level) draw each and
  `scripts/check_decompose.py` re-derives 400 documents of each built mix
  off the bytes, both green before training.
* **The utterance-loss confound was not pre-registered.** It was found by a
  diagnostic after F read zero, and F2 was designed to close it. F2 is
  reported as post hoc and its result changes no pre-registered reading.

## Limits

Two seeds per arm, so directions (rule 6); the band's sizes are not
readable. Nano readings of a dummy world, and PLAN-LOOP §3 says which
literature lesson does and does not transfer. The forgery tests one axis --
two labels swapped on a two-child `do` -- and the per-kind losses are read
on 96 windows of the payload's validation split with one permutation. The
diagnostics separate "read" from "decides" by loss and by argument; they do
not say what the acting layers *would* read if the words were taken away,
which is PLAN-TAG-SPINE rung 1's question and not this finding's.
