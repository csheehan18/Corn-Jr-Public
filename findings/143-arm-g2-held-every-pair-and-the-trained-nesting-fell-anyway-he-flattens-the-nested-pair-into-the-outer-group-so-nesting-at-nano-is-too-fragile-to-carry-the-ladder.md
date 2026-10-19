# Nesting at 20M breaks two different ways; too fragile to build on

**Full result:** Arm G2 held every pair arm F had and the trained nesting fell anyway, this time because he flattens the nested pair into the outer group; two differently matched arms broke the same base two different ways, so nesting at nano is too fragile to carry the arity ladder, while the outer four-carrier installs cleanly at both seeds

**Cost:** 6.6 min of scoring on the 1 card first cited here (`nano20m_v3_fw_ladder_add`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-PARSE-WEIGHTS arm G2, read 2026-09-25. Two nano cells
(`nano20m_v3_fw_ladder_add`, seeds 1337 and 2337) against arm F at the same
seeds, `scripts/probe_ladder.py` on `evals/funcworld_ladder.jsonl` plus the
full card. Pre-registration: `configs/mix_v3_funcworld_ladder_add.py`,
committed at `190cef1` before either seed trained. G2 is finding 142's repair:
arm F's file byte-identical, 2,096 four-member outer groups added as their own
source on top, total tokens and iterations raised by exactly the payload's
weight, so every outer pair, triple and nested pair F saw is there to the count
(re-read off the union's bytes by `check_funcworld.py`).

## The pre-registered read

Structure of 96, seed 1 / seed 2, with `s|bal` (structure on balanced lines)
where the probe carries it (committed:
`evals/results/nano20m_v3_fw_{armf,ladder,ladder_add}{,_seed2}__ladder.json`):

    row      F          G          G2         G2 s|bal
    outer2   22 / 22    17 / 17    30 / 20    27 / 17
    outer3   36 / 48    21 / 26    39 / 36    37 / 33
    outer4   31 / 20    26 / 27    46 / 42    44 / 40
    nest2    15 / 18     2 /  8     4 / 11     3 /  9
    nest3     6 /  5     2 /  9     3 /  3     3 /  2
    nest4     0 /  4     1 /  4     2 /  1     2 /  1

    nest2 do+ (a `do` the gold lacks)   F 20 / 10   G 34 / 30   G2 24 / 9

Every row parses on 77 or more of 96. The kill did not fire: `tool.copy` 102
and 120 of 120 -- seed 1's 102 is arm F's seed-1 figure to the item, the third
single-seed copy dip in this phase not to replicate.

**The base failed at both seeds.** The pre-registration read the base first:
`nest2` at 12 or more at both seeds and its `do+` at 24 or under. `do+` held
(24 and 9); `nest2` did not (4 and 11). By the table, adding four-member groups
interferes with the trained nesting even when no pair is taken away, and
`nest4` is not read.

## What the lines say

Holding the pairs did what it was built to do. Arm G's invented consumer is
mostly gone -- `nest2` `do+` back inside F's range at seed 2 and at the line at
seed 1 -- and outer pairs read above F at seed 1 and two under at seed 2. The nesting fell by a different
road. Where the gold nests a pair inside a group, G2 writes the pair's members
into the outer group, or splits the group into two outer ones:

    hey no ulterior motive say the capital of Gledaenddor and equally the capital
    of Bryunlvholm, and lastly the currency of Garorwold
    GOLD  ask[say ask[ask[the capital of Gledaenddor] and equally ask[the capital of Bryunlvholm]], and ask[lastly the currency of Garorwold]]
    F     ask[say, ask[ask[the capital of Gledaenddor] and ask[equally the capital of Bryunlvholm]], and ask[lastly ...]]
    G2    ask[say ask[the capital of Gledaenddor] and ask[equally the capital of Bryunlvholm]] ask[lastly the currency of Garorwold]

Counted on `nest2`, among items where he writes no nested group, an outer group
one member wider than the gold's (the pair inlined): F 13 and 4, G2 18 and 19,
at seeds 1 and 2; the group split into outer groups, F 5 and 9, G2 7 and 7.
**A bound** -- a scratchpad count over greedy decodes with the probe's tree
reader, not a pinned instrument.

## Why, as far as these two arms can say

The payload's four-member groups were built flat (`--profile flat4`) so that G2
would add no nested pairs: under `armf` the filter would have added about 610,
+25% on the rows being read. That held the nested-pair **count** at F's 2,467
and lowered the **share** of groups that hold a nesting, from 0.309 on F
(2,467 of 7,990) to 0.245 on G2 (2,467 of 10,086). Arm G did the opposite --
its share stayed at 0.301 and its count fell 10%. Each arm held one of the two
and moved the other, and each lost the trained nesting, by a different
mechanism. **These runs cannot separate** "the nesting share fell" from
"training wide outer groups pulls members outward"; both predict flattening.

The pre-registration named count as the thing to hold and did not name share.
That was this session's design choice, and the table did not anticipate it.

## What it does say

**The trained nesting at nano is fragile**, and that is the result that
survives both arms. It is 15 and 18 of 96 on arm F to start with (nesting at all on 16 and 23), and two
corpus changes, each matched carefully on a different axis, took it to 2 to 11.
A question about arity at a nested position cannot be read on a base that
moves this easily -- a third ladder arm would be asking the same unreadable
question a third way.

**The outer four-carrier installs, and cleanly.** `outer4` 46 and 42 against
F's 31 and 20, 44 and 40 on balanced lines, the number word kept on 40 of 56 at
both seeds against F's 17 of 50 and 19 of 45 -- and this time without G's cost
to the rows beside it. Arity at the level where it is trained is trainable at
nano.

## What it does not say

Nothing about whether a four-member carrier travels to a nested position: the
gate was not read, twice. Nothing at 260M. Nano, one synthetic world, two
seeds, greedy decodes.

**Licenses** moving the nesting question off the corpus and onto the runtime,
as PLAN-PARSE-WEIGHTS row F first specified: the stepped protocol, where the
runtime re-presents each group's span as its own request and he writes one
level at a time -- the level these two arms show he learns reliably, and the
position finding 140 already reads at 71 to 89 of 95. No third ladder arm.
