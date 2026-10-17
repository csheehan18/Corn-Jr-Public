# One hundred and fifty-third finding — the state line's second seed: he writes the line again, 106 of 120, and the repeat does not fall under it -- at seed 2 a line present raises it, 59 to 74 hand-inserted and 66 under his own record, and averaged over four draws seed 1's fall shrinks from 21 to 8; the pre-registered read fails at both seeds, so the record is written and not read

**Cost:** 31.2 min of training two nano runs (934 s and 938 s); 6.3 min of
scoring two full cards (192 s and 188 s), with the `state` and `--state-history`
re-scores and the six registered probes about 2.5 min more; two seed-1
reproductions 25 s; three post hoc replicates per cell and condition, 36
probes, about 8 min (17:08-17:17). 16:26-17:30 on 2026-10-07 end to end,
against a registered ~45 min of card time.

ROADMAP A5, PLAN-TAG-SPINE §11 phase D: finding 134's pre-registered second
seed, **on the both cell and the base**, with the read to beat stated there --
*the both cell under its own record below the base cell's no-line rate at
both seeds, with `turn2.reask_yn` inside the eager band.* Seed 2337
(`configs/nano20m_v3_turn2c_seed2.py`, `configs/nano20m_v3_turn2_state_dep_seed2.py`),
every field of the seed-1 cells but `name` and `seed`, the same `train.bin`
bytes. Every card finding 134 read, with its flags (`corn/evals.py` full,
`--only state`, `--state-history answered`; `probe_depth.py --probe repeat
--arm given --header both --samples 32`, no line / `--state asked` /
`--state written`). **Cards:** `evals/results/nano20m_v3_turn2c_seed2*.json`,
`nano20m_v3_turn2_state_dep_seed2*.json`; the replicate counts in
`nano20m_v3_turn2_state_dep__a5_replicates.json`.

## The instrument first

`probe_depth.py` sampled at T=0.3 with no seed, so a card did not reproduce:
re-run on 2026-10-07, finding 134's base no-line card read **64** against its
recorded 74 and the both cell's written-record card **84** against 80. At
these rates one card of 384 draws carries an sd of about 8, so seed 1's
headline gaps (80 against 74; 99 to 78) were each inside one or two sd of a
single draw. The registered read below is one card a condition, as
registered; **three more draws per cell and condition sit beside it,
post hoc and labelled**. The probe is now seeded (`--draw-seed`, default
20261007, stamped on the card) and two runs on one checkpoint are row-identical.

## The registered read

    repeats of 384           no line    hand-inserted `asked`    written by him
    base s1 (134)               74              66                    57   junk
    base s2                     56              57                    31   junk
    both s1 (134)               99              78                    80
    both s2                     57              73                    68

**The gate fails at both seeds**: the both cell under its own record reads 80
and 68 against the base's no-line 74 and 56. `turn2.reask_yn` is outside the
eager band (33-38) on the both cell at both seeds -- 14 and 17 of 40 -- and
the base reads 40 and 31.

## Four draws a condition

    mean of 4 (registered + 3)   no line    hand-inserted    written
    base s1                        67.8         68.8           57.8   junk
    base s2                        54.0         57.8           33.2   junk
    both s1                        96.0         87.8           82.0
    both s2                        59.2         74.2           66.2

Seed 1's direction survives smaller -- the hand-inserted line takes 8 off, not
21; his own record 14 -- and **seed 2's runs the other way**: a line present
adds 15 hand-inserted and 7 written. Across the two seeds there is no
consistent effect of the record on the repeat, and the both cell sits above
the base under every condition at both seeds.

## Read by hand

**The base's written column is not a record at either seed.** The base never
trained on the line; asked to write it, it writes tool declarations
(`schedule_weekly_shared_shared_...`, `add_evening_backup_shopping_list(item)
-- add a new ...`), and the second turn degrades ("Getting low.", "Yes, I'm
afraid."), refused 99 and 109 of 384. Its low repeat there is a broken turn,
which is why the gate reads the base's no-line column.

**Seed 2's record is often illegal, and where legal often wrong.** Split by
header and by whether the value he wrote was one of the three:

                     no line    written: legal / 192    repeats on legal draws
    both s1 route     63/192     191 (asked 144, answered 47)     41/191
    both s1 bare      36/192     192 (asked 97, answered 95)      38/192
    both s2 route     33/192     115 (asked 96, open 17)          44/115
    both s2 bare      24/192     191 (open 118, answered 67, asked 6)   19/191

Under the route header seed 2 writes junk on 77 of 192 (`check_morning`, a
declaration name repeated to the token limit); on the legal draws there the
repeat is *higher* than with no line, 38% against 17%. Under the bare header
every turn-1 say it is shown asks a question ("Hi, how are you today?"),
which `corn.stateline`'s rule calls `asked` -- and seed 2 writes `asked` 6
times in 191, `open` 118. The drawn-say row reads the line well (below); on
his own wellbeing openers the record says the opposite of what he did.

## The rows

    of 120/60/200/200/120/96/40          base s1  base s2   both s1  both s2
    state.value / _heldout                 1  0     0  0    101 32   106 28
    turn2.first                             174      186      179      173
    turn2.second                            189      185      191      180
    turn2.react                             117      115      108      112
    turn2.reask                              43       52       13       33
    turn2.reask_yn                           40       31       14       17
    reask / reask_yn, --state-history      38 40    49 33    24 17    48 20
    social.declared_nocall                   13       11       70       94
    social.voice                             65       43      105      101
    social.family                            26        3       52       60
    social.open / open_voice               1  6     0  1     8 20    23 40
    tool.copy / copy_wide                 120 300  101 300  119 299  120 297

**He writes the line, at both seeds** -- 106 of 120 and 28 of 60 held out at
seed 2 against 101 and 32 -- so finding 134's first result replicates.
**The dependent payload's social band replicates too**, wider: four social
rows up 30 to 90 items from under the dose floor. **`turn2.reask_yn` falls
on the both cell at both seeds** (14, 17; with the record rendered back 17,
20); seed 1's dependent-only cell fell with it, so the fall is not shown to
be the line's, and this seed ran no dependent-only cell to separate them.
`turn2.reask` falls at seed 2 too (52 to 33) and the `--state-history` read
recovers it whole (48 against the base's 49), as at seed 1 half-way. **The
kill did not fire**: the copy band on the both cell is 120 and 297. The base
s2's `tool.copy` 101 is the base's own spread.

## What this licenses

The pre-registered row it lands on is the second: **`state.value` high, the
repeat rate not moved by the record present -- the record is written and not
read; the awareness claim retires, and the line stays a scored intermediate
for the harness** (`configs/mix_v3_turn2_state.py`'s table). Finding 134's
"a line merely present moves the repeat on the cells trained on it" was one
draw at one seed; at four draws and two seeds it does not hold.

For D7 the state line's case is now what it costs and what it records, not
what it does to the next turn: 0.95% of the mix (finding 152), written well
on corpus says and badly on his own openers at one of two seeds. Who writes
it stays H3's choice (SPEC-LANGUAGE §4), and this says nothing in favour of
him writing it: the runtime's `state_of` writes the right value every time.
D2 (the runtime reading the line back) is not shown to buy anything at nano.

## Limits

Nano, two seeds of two cells; the dependent-only and state-only cells ran
at seed 1 alone. The repeat ruler is lexical (finding 134's instruments
note) and its cases are six wellbeing openers. The replicates are post hoc
and unseeded, as the registered cards were; the probe is seeded from here
on. Nothing touches the shipped checkpoint.
