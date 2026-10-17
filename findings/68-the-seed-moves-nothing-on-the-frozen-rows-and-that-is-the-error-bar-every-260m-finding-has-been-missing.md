# Sixty-eighth finding — the seed moves nothing on the frozen rows, and that is the error bar every 260M finding has been missing

**Cost:** 12.6 min of scoring on the 1 card first cited here (`corn_jr_260m_ftnarrow_seed2`); it also reads 2 cards scored for an earlier finding (`corn_jr_260m`, `corn_jr_260m_ftwide_seed2`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn_jr_260m_ftwide_seed2` and `corn_jr_260m_ftnarrow_seed2`, 2026-08-26,
scored by `corn.evals` against the frozen `evals/` set. R4 of
`docs/PLAN-P3-RULERS.md`, which pre-registered **no threshold on purpose**: the
deliverable is the spread itself, to be quoted by every later 260M finding. No
training — both checkpoints were on disk and unscored, which is why the plan
called this the cheapest read in the repository.

## The two things that make it a comparison

Both arms are the seed-1 run with `seed: 1337` changed to `1338` and nothing
else: same `init_from` (the frozen `corn_jr_260m`), same 30MB payload, same 786
`max_iters`, same `lr`, same dtype. And the invocation is the seed-1 one flag
for flag — bare `python -m corn.evals --ckpt … --json …`, every section on,
`--max-samples` at its default of 8, `--data-dir` defaulting to the
checkpoint's own. Ground rule 4 of the plan is that comparability is declared
rather than assumed, and a scorecard taken under different flags would have
broken it inside its own workstream.

**One difference is not the seed and has to be said.** The selection rule
(`mean-log-per-source`) picked **iter 700** for `ftwide_seed2` and **iter 600**
for `ftnarrow_seed2`, against 786 for both seed-1 runs. So "the seed" here means
the seed and the checkpoint it caused to be selected, which is what a re-run of
this rig actually varies.

## The table R4 asked for

Rows findings 63 and 65 cite, seed 1 → seed 2:

    row                 ftwide            ftnarrow
    tool.copy           120/120 → 120/120  120/120 → 120/120
    tool.copy_wide      300/300 → 300/300  300/300 → 300/300
    temporal.copy       353/353 → 353/353  353/353 → 353/353
    temporal.route      400/400 → 400/400  400/400 → 400/400
    search.route_base   200/200 → 200/200  200/200 → 200/200
    search.route_wide   200/200 → 200/200  199/200 → 199/200
    search.route_heldout 200/200 → 200/200 200/200 → 200/200
    extract.span         22/200 →  20/200   22/200 →  21/200
    extract.abstain       1/200 →   1/200    1/200 →   1/200
    extract.brevity     238/400 → 224/400  243/400 → 231/400
    invented (span why)      70 →      71       63 →      68

Every ceiling row is **exactly** reproduced. Nothing that finding 63 rests on
moves by one item across a seed.

The widest movers anywhere in the behaviour block are not in that list:

    notefid.novel_phrasing   86/120 → 80/120     87/120 → 79/120
    extract.brevity         238/400 → 224/400   243/400 → 231/400
    chat.abstain_oos         47/100 → 50/100     38/100 → 37/100
    tool.selection          188/200 → 190/200   unchanged
    turn2.second            178/200 → 180/200   182/200 → 180/200

**So the error bar, stated as a number to quote: ±2 items on `extract.span`,
±14 of 400 on `extract.brevity`, ±8 of 120 on `notefid.novel_phrasing`, and
zero on every row at ceiling.** A 260M effect smaller than that is wobble; the
sixty-third finding's 72/200 → 198/200 and the sixty-fifth's 9/200 → 70/200 are
two and three orders of magnitude outside it.

## `val_loss` is not the instrument, and this is the cleanest demonstration yet

    checkpoint          iter   val_loss   behaviour rows that moved
    ftwide              786     0.9305    --
    ftwide_seed2        700     0.8380    9 rows, none by more than 6 items
    ftnarrow            786     0.9344    --
    ftnarrow_seed2      600     0.9252    7 rows, none by more than 8 items

`ftwide_seed2` sits **0.093 nats below** its seed-1 twin — the largest val gap
anywhere in this family — and scores the same behaviour to within a handful of
items, with the four `lm` rows agreeing to three decimal places (`temporal`
0.1923 → 0.1910, the rest inside 0.0002). A run that picked the checkpoint by
val alone would have called that a materially better model.

## What it does not say

This is the spread of the **frozen rows**, and it does not transfer to live
instruments. The sixty-ninth finding measures the same four checkpoints on
`harness/toolgrid.py` and reads a seed spread of **26 to 55 turns of 208** on
the decline column — an order of magnitude wider, on the same weights, on the
same day. Two seeds a side is also two, not five: the nineteenth and
forty-third findings both had to widen a floor when the third and fourth seeds
arrived, and nothing here is safe from that.
