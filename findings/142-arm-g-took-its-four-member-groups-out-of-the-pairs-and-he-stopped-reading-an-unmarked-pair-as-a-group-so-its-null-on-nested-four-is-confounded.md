# One hundred and forty-second finding — arm G took its four-member groups out of the pairs, and he stopped reading an unmarked pair as a group: he writes a lookup-and-deliver with an invented consumer instead, so the trained nesting falls and the pre-registered null on nested four is confounded rather than read

**Cost:** 6.9 min of scoring on the 1 card first cited here (`nano20m_v3_fw_ladder`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-PARSE-WEIGHTS arm G, the arity ladder, read 2026-09-25. Two nano cells
(`nano20m_v3_fw_ladder`, seeds 1337 and 2337) against arm F at the same seeds,
on `evals/funcworld_ladder.jsonl` through `scripts/probe_ladder.py`, plus the
full card. Pre-registration: `configs/mix_v3_funcworld_ladder.py`, committed at
`6b353b9` before either seed trained. **The table's null row is where the gate
landed, and reading the lines by hand says the table cannot be taken at its
word -- most of this finding is why.**

## The pre-registered read

Structure of 96, arm F then arm G, seed 1 / seed 2 (committed:
`evals/results/nano20m_v3_fw_{armf,ladder}{,_seed2}__ladder.json`):

    row      F          G          pre-registration
    nest4    0 / 4      1 / 4      gate >= 9 at both; null inside 0-4
    nest3    6 / 5      2 / 9      must hold 3-8 -- fails at both seeds
    nest2    15 / 18    2 / 8      the trained nesting
    outer4   31 / 20    26 / 27    side reading
    outer4 "four" kept   17/50, 19/45   35/51, 27/44

The kill did not fire -- `tool.copy` 120 of 120 at both seeds -- and every row
parses on 64 or more of 96. `nest4` sits inside 0-4 at both seeds with the
number word up, which is the null row: *the carrier was learned where it was
trained and did not travel*. But the table also says that reading stands only
against a `nest3` that held, and `nest3` held at neither seed. And the trained
`nest2` fell from 15 and 18 to 2 and 8, which no row of the table anticipated.

## What the lines say

Arm F's file and arm G's differ by one thing on paper -- four-member groups at
the outer level -- and by two in the bytes. At a fixed token budget the
`ladder` profile took four's 0.30 out of two's share, so **outer pairs fell
45% (5,709 to 3,143) and nested pairs 10% (2,467 to 2,222)**; the config
recorded the second and not the first.

Read side by side on the same skeletons, the loss is one behaviour. Where a
group is announced by a connective alone -- "coupled with", "together with",
"with Y for company", "and equally", "plus" -- arm F flattens it into sibling
`ask`s, wrong but on the right label. Arm G reads the second member as a
delivery and invents the consumer out of the words that are left:

    i want the currency of Cadornddia coupled with the population of Haluskburg
    F   ask[i want the currency of Cadornddia] ask[coupled with the population of Haluskburg]
    G   ask[i want the currency of Cadornddia] do[find[i want the population of Haluskburg]
          send[passed with the population of Haluskburg]]

    pin down the currency of Varewold too and the capital of Variskholm at once for me ...
    G   ... do[find[the capital of Variskholm at once] note[for me the world won't end]]

Counted: a `do` in his line where the gold has none, **on unmarked groups**,
`outer2` 9 to 18 and 5 to 21, `nest2` 18 to 30 and 9 to 29, `outer3` 7 to 14
and 3 to 16, at seeds 1 and 2; on groups marked by a count or pair word the
same three rows move by 0 to 7 on denominators of 10 to 31. So the trained
nesting did not get harder to write -- the pair connective under it stopped
being read as a group, and 77 of 96 `nest2` items are unmarked. **Not all of
it is the connective**: on seed 2 the marked `nest3` and `nest4` items, whose
nested group carries its count word, gained invented `do`s too (4 to 16 and
19 to 32), so a second, unexplained pull toward `do` rides on that seed.

Two things ruled out on the bytes, so they are not re-derived: the `ask`
against `do` balance (lines with a `do`-over-a-group per `ask` group, 1.24 on
F and 1.20 on G) and what a lean declaration predicts (lean turns carry the
same shape mix on both, every share within 0.02).

What did work, where it was taught: **marked** `outer4` structure rose at both
seeds (18 to 21, 12 to 20) with the number word about doubled, while unmarked
`outer4` did not (13 to 5, 8 to 7). The four-carrier was learned as a carrier.

## An instrument fault that predates the arm

`parse_nested` closes a line that runs out of brackets, so `probe_ladder.py`'s
structure count read through lines that do not balance -- **27 to 72 of 96 a
row, on arm F as much as on G**. Counted on balanced lines only, arm F's
`nest4` band is 0 and 3, not 0 and 4. The probe now carries `bal`, `s|bal` and
`do+` columns beside `struct`; arm F's and G's bands on them are in arm G2's
pre-registration.

## A hand-read that was wrong, recorded so it is not repeated

Reading `nest4` I found two lines where a nested four-carrier was promoted to
the outer group ("say four, please: ..." written as one outer group of five)
and called it the mechanism. Counted, it happens on 1 to 3 of 96 on G and 0 to
2 on F. Two picked lines are not a reading -- the convention CLAUDE.md carries,
broken inside the session that was applying it.

## What it does not say

It does not say the four-carrier fails to travel to a nested position: that was
never tested, because the checkpoints it was asked of had lost the pair reading
the nested rows stand on. It does not say the carrier travels either. Nano, one
synthetic world, two seeds; the connective reading is a hand count over
greedy decodes with no floor of its own.

**Licenses** arm G2: arm F's file byte-identical, four-member groups added as
their own source on top (`funcworld_four.txt`, `--shapes four --profile flat4
--require-outer4`), total tokens and iterations raised by exactly its weight,
so outer pairs, triples and nested pairs are F's to the count and the only new
thing is 2,096 outer fours. `configs/mix_v3_funcworld_ladder_add.py` carries it.
