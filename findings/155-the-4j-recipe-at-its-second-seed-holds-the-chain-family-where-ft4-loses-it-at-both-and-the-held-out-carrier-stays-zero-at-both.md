# A new fine-tune recipe keeps follow-ups but 'what about X?' still fails

**Full result:** The `4j` recipe at its second seed: it holds the frozen chain family where `ft4` loses it, at both seeds (`chain_ellipsis` 50 and 49 of 50 against 7 and 13), lifts `turn2.reask` to 73 and 75 of 96 against 49 and 41, and costs `compound.pipe` 5-7 of 48; live, both seeds compose `and {e}?` 3 of 4 at depths 2 and 3 and `what about {e}?` 0 of 4, exactly as seed 1 did

**Cost:** one 260M fine-tune, 1,019 s at 786 iterations, contended (the card
sat at 35% before the job; seed 1 took 909 s uncontended); one full scorecard,
about 1,300 s; `harness/chaingrid.py` over five checkpoints, 128 s with the
servers' loads. 09:31-10:13 on 2026-10-08 end to end.

ROADMAP T0, PLAN-1-0 §12: decision D5 (which recipe the 1.0 fine-tune arms
run on, `4j` proposed) waited on `4j` against `ft4` read at two seeds. §12
read both at one seed and wrote no finding: "**Neither arm is a finding**".
`ft4`'s second seed (1338) was already on disk. This adds `4j`'s:
`configs/corn_jr_260m_v4_ft4j_seed2.py`, every field of
`configs/corn_jr_260m_v4_ft4j.py` but `name` and `seed=1338`, the same
`data/mix_v4_ft_4j` bytes. **Cards:** `evals/results/corn_jr_260m_v4_ft4j_seed2.json`
(full `corn.evals`, no flags), and `harness/results/*__chaingrid-t0.json` for
the base, both `ft4` seeds and both `4j` seeds, read in one sitting on one
revision (`5cf58aa`) by `scripts/run_t0_chaingrid.py`: today's
`ServerConfig` defaults with `--multi --no-log`.

## The frozen rows

    row                     base     ft4  ft4 s2      4j   4j s2
    turn2.chain_ellipsis   49/50    7/50   13/50   50/50   49/50
    turn2.chain_pronoun    40/50   29/50   24/50   40/50   40/50
    turn2.chain_result     50/50   45/50   45/50   50/50   50/50
    turn2.reask            40/96   49/96   41/96   73/96   75/96
    turn2.reask_yn         15/40   20/40   18/40   25/40   37/40
    notefid.novel_phrasing 80/120  74/120  72/120  88/120  88/120
    compound.pipe          36/48   34/48   32/48   31/48   29/48
    tool.copy             120/120 120/120 120/120 120/120 120/120
    tool.copy_wide        300/300 300/300 300/300 300/300 300/300

Across all 96 rows on the card, these are the only ones where one recipe's
two seeds both sit at least 10 points above the other recipe's two:
`notefid.novel_phrasing` and the four chain and re-ask rows, all for `4j`. No
row separates them the other way. The one row where both `4j` seeds sit ten
points or more below the base is `compound.pipe`, and `ft4` sits between them,
so §12's "4i's `compound.*` dip persists into 4j" replicates as a small,
recipe-shaped cost. The `4j` seeds disagree by 15 points or more on two
rows: `turn2.reask_yn` (25 against 37 of 40, both above every `ft4`) and
`social.farewell` (11 against 7 of 20).

## Live, through the runtime

    composed (of 4)      base    ft4  ft4 s2    4j  4j s2
    what about {e}?  d2     4      0       0     0      0
                     d3     4      0       0     0      0
    and {e}?         d2     3      0       0     3      3
                     d3     3      0       0     3      3
    pronoun resolved (of 6) 0      0       0     0      0

Same day, same code: seed 1's rows from §12 reproduce to the cell. That
includes 4j's split by carrier: `and {e}?` has a trained neighbour (`and {e}
then?`) and recovers, while `what about {e}?` has none and stays at zero at
both seeds. A miss on it is `literal`, the follow-up searched as written
(`what about spain`), which is `ft4_secondturn`'s own policy.

## Read by hand

Every composed and literal label above was read against the query the server
actually issued. Composed: `and brazil?` -> `the population of brazil`.
Literal: `and peru?` -> `and peru?`. Reissued: `and peru?` -> `the currency of
norway`. The instrument reads what the text says.

**The pronoun grid is new here** (§12 printed only Grid C), and it is zero
everywhere, with the misses changing shape. The base re-issues turn 1's query
on four of six (`is it growing?` -> `the population of kenya`), surrenders one
and keeps the pronoun on one. Every fine-tuned checkpoint, at both seeds and
under both recipes, searches the pronoun as written (`how old is he?` -> `how
old is he`). On 2026-09-08 the base's card read reissued 5 and surrendered 1.
Today's one literal comes from the runtime's code or defaults since then, not the weights, because
temperature is zero and the checkpoint is the same file.

## What it licenses

- **D5 has its evidence.** `4j` is the better recipe on every row that
  separates the two at both seeds, and the separation is the chain family that
  `ft4` broke. Its measured cost is `compound.pipe`, 5-7 of 48 below the base.
  The decision is the owner's; this is what it waited on.
- **Neither recipe composes a carrier it has no neighbour for, and neither
  resolves a pronoun.** PLAN-1-0 §12 concluded the next variable is share, not
  breadth. That still stands, and is now read at two seeds. A 1.0 arm built on
  `4j` inherits both gaps, which NOW §4 already discloses as follow-up
  composition and pronoun follow-ups.

## Limits

chaingrid is n=4 per cell, so 0 of 4 against 4 of 4 is a gap and 3 of 4
against 4 of 4 is not. The pronoun grid is n=6. The fine-tune ran beside light
desktop use, so its 1,019 s is a bound on the speed and says nothing about the
weights. Two seeds per recipe; `4i` was not re-run.
