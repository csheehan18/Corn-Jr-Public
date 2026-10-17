# One hundred and forty-first finding — with the parse written as one nested line he writes a three-member group inside a group, a structure the corpus never contains, eighteen times across two seeds and 5.8 times more often where the gold calls for one than where it does not, on the leg that had never given anything

**Cost:** 14.7 min of scoring on the 2 cards first cited here (`nano20m_v3_fw_armf`, `nano20m_v3_fw_armf_lines`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-PARSE-WEIGHTS arm F, read 2026-09-16. Two nano cells on the nested format
(`nano20m_v3_fw_armf`, seeds 1337 and 2337) against a line-format control at the
same depth profile (`nano20m_v3_fw_armf_lines`), all three token- and
step-matched to arm W under the C6 protocol. `scripts/probe_nestgen.py`,
`scripts/probe_nestfork.py`, `corn.evals`. **The gate is a within-checkpoint
comparison and the two instruments before it could not make one; that is most
of this finding's story.**

## The result

A three-member group **nested inside a group** appears nowhere in the corpus:
it is `nest_three`, the holdout `parse.w_pairing` is cut from, and a group has
only ever nested two. Decoded greedily and scored structurally -- did he nest,
and with how many members -- against `w_nest_seen`, a trained two-member
nesting cut at the same fork depth from the same generator:

    seed    row            nested   wrote a three   rate
    1337    w_nest_seen       17           1        0.059
    1337    w_pairing         25           9        0.360
    2337    w_nest_seen       17           1        0.059
    2337    w_pairing         28           9        0.321

    both    w_nest_seen     2/34 = 0.059
    both    w_pairing      18/53 = 0.340        5.8x

Both seeds land within 0.04 of each other on the held-out row and identically --
1 of 17, twice -- on the trained one. Rule 6 is met: two seeds, one direction,
one magnitude.

**The mechanism is the thesis's own.** A three-member carrier (`three things:
{a}, {b}, {c}`) is trained at the *outer* level, where `GROUP_SIZE` puts it at
0.30; nesting is trained with two-member groups. Neither piece is new and the
combination is. He reads a known carrier's arity and applies it at a position
where he has only ever seen arity two, which is what THESIS section 1 means by
recombination over a closed set.

## Why it took a third instrument, and why the first two were wrong

`parse.w_pairing` reads 0 to 1 of 96 on every cell in the line-per-level format
-- W, both doses, `b1024`, `wide1024` -- and C6 widened the nesting inventory
from 10 branching structures to 53 and moved it on none of three instruments,
two of which bypass copy. The leg had never given anything.

**The fork.** `probe_nestfork.py` reads the one token where a bracket opens.
Its own docstring says the rows are not comparable to each other, only the
column is, because the token before the fork and the tokenisation of the gold
token differ between them -- 79 of 96 `w_nest_seen` forks sit immediately after
`[` and take `'ask'`, while `w_pairing` splits 48/48 and takes `' ask'` or
`'ask'`. A gate was nonetheless built on comparing two rows there. It read
**70 against 67** on one cut of the rows and **22 against 55** on the next, and
both were artifacts of the comparison rather than readings of anything.

**The first cut of the comparison row was wrong too**, and in the way this phase
keeps being wrong: `w_nest_seen` was cut with a `deepest_group` that counted a
`do`'s lookup group as a nesting. A `do` composes a lookup with its consumers
and is not a group, so on most items the row forked at a structurally different
place; only 18 of its 96 items carried a true nesting at all. **That is the
fourth wrong number in this phase from the same distinction** -- a 455-span
leak, 1,160 false positives in `check_funcworld.py`, "a group of one" on 216
turns, and this -- and it should be one function every tree-walker calls.

**What works** is `probe_nestgen.py`: decode the parse, parse it back with the
guard's bracket reader, ask only how many members he gave the nesting. One
checkpoint, one scoring rule, no local-token term, exact-match not used because
half of `wrong_arity` on the line format was an invented span
(FAILURES-PARSE section 1) and a copy slip would swamp a structural signal it
has nothing to do with.

## The format, and what it is not evidence for

The arm acquires the format: on the fork it reads 22 and 55 of 96 where every
line-format checkpoint reads **0 of 96** and the never-saw-a-parse cell reads 3
and 4. That is a model that opens nested brackets, which none before it would,
and it says nothing about shape -- both rows need a bracket opened in a format
only the arm trains. The nested form is also **56.5%** of the line form's parse
tokens on the 632 frozen items, so it should lift trained rows for length
reasons alone; the control exists for that and the parse rows are not compared
across formats, because they cannot be.

## The kill did not fire, and a pattern worth recording

    row              W b1024   armf LINES   NEST s1   NEST s2
    tool.copy        120/120     120/120    102/120   120/120
    tool.copy_wide   290/300     269/300    280/300   288/300
    temporal.copy    353/353     353/353    353/353   353/353

Seed 1's 102 is an excursion. **This is the second single-seed `tool.copy` dip
in this phase that did not replicate** -- arm A read 100 of 120 and recovered to
119 (finding 139, amended) -- so a copy-band kill wants its second seed before
it is called, and twice now the first seed would have killed a live arm.

## What it does not say

Eighteen productions across two seeds, 0.340 against 0.059, is a **signal and
not a capability** -- the same caliber as `parse.w_heldout`'s 10 to 17 of 140.
Between 12 and 21 of 96 emissions a row do not parse at all, so the denominators
are partial. It is nano, one synthetic world, and rung 4 on real carriers is
untouched. `parse.w_d5` is unchanged and unread: it forks at bracket depth 4,
where this corpus has a node with children in 0 of 3,602 cases, so finding 136's
zero-support result holds in this format too and only a positive there could
have counted.

And the reading is contestable in one specific place, which is better argued
than assumed: following a trained carrier's arity to an untrained position may
be called carrier-following rather than structural generalisation. The answer
here is that a carrier *is* a member of the closed set section 1 describes and
its arity at a new position is exactly the recombination claimed -- but anyone
quoting this should quote that sentence with it.

**Licenses** the arity ladder as the next arm: four-member carriers already
exist (`GROUP_CORES_MARKED_4`, unused under `base` shapes), so a profile
training arities 2, 3 and 4 at the outer level while nesting only 2 puts rung 3
and rung 4 in one corpus, each with the rung below as its floor and the whole
comparison inside one checkpoint. One rung can be a fluke of one carrier; three
in order is systematic. Five is not available -- the carrier pools stop at
`{d}`.
