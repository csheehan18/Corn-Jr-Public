# Seventy-sixth finding — the single-request control returns the copy rows on both vehicles, and what is left over is the control's own failure species

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Four nano arms trained 2026-08-28 from `configs/mix_v3_compound_v2.py` and
`configs/mix_compound_v2_ft.py` — finding 74's own design re-run on
`data/raw/compound_v2.txt`, two seeds a vehicle, same payload weight and same
schedule as the v1 pair to the token. Controls are the four already-scored
`nano20m_v3` seeds and the seven v1 compound cards; **nothing retrained and
nothing was re-scored**. All four arms are eager, like their controls — the
signed `compile=True` is scoped to the H200 family.

Pre-registered in `docs/PLAN-MIX-V4-BUILD.md` Phase 2 and in
`configs/mix_v3_compound_v2.py`'s docstring, both written before a byte of the
file existed. `docs/PLAN-5B-SUPPLY.md` §7a's compound entry ordered the
rebuild; the share it prices is the owner's and is not decided here.

## What was wrong, and what the file changed

Finding 74: `compound.pipe` installed completely on either vehicle and took
`tool.copy` to 0–1/120 and `tool.copy_wide` to 0/300 on the fine-tune arm,
with the copied span **exact every time** and the `why` bucket `malformed` on
all 420 items. Copy discipline had not broken; the decision to *stop* had. All
43,626 v1 transcripts put a second call after the first observation and none
ended a turn after one, so the model learned the rule the corpus stated.

`compound_v2.txt` is the same three classes with a matched single-request
control written atomically beside each one: one carrier drawn once and
rendered twice, around a compound core and around the first of its requests
alone. 50/50 by construction, identical carrier distributions on the two
halves, identical opening-tool distributions — all asserted off the bytes by
`scripts/check_turn2.py`.

## The result, against the registered reading

| row | control ×4 | v1 MIX ×3 | v1 FT ×2 | **v2 MIX ×2** | **v2 FT ×2** |
|---|---|---|---|---|---|
| `tool.copy` /120 | 118–120 | 36–104 | **0–1** | **111, 120** | **115, 120** |
| `tool.copy_wide` /300 | 281–296 | 190–282 | **0–0** | **297, 278** | **298, 294** |
| `compound.pipe` /48 | 0–0 | 47–48 | 46–47 | 44, 47 | 44, 48 |
| `compound.pipe_first` /48 | 15–39 | 48/48 | 47–48 | 48, 48 | 48, 48 |

**This is the pre-registered "fixed" outcome, on both of its clauses and on
both vehicles.** `tool.copy` returns inside the ~10-item wobble of the
control's 118–120 on all four arms. `tool.copy_wide` reads 294–298 on three
arms — two of them *above* the control's 281–296 — and 278 on the fourth,
three items below a band whose own four-seed spread is fifteen. And
`compound.pipe` holds at or above 40/48 on every arm, so the class the file
exists to teach is not traded for the rows it was breaking.

The fine-tune arm is the one to look at, because it is where the bill was
largest: **0 and 1 of 120 become 115 and 120; 0 and 0 of 300 become 298 and
294.**

## The failure species is the finding, and it is not the totals

Totals can return for the wrong reason. These do not:

    row              arm        malformed   the rest
    tool.copy        v1 FT ×2   120, 116    wrong_answer 3
                     v2 FT ×2   5, 0        --
    tool.copy        v1 MIX ×3  70, 16, 58  wrong_answer 14, 0, 13
                     v2 MIX ×2  0, 1        wrong_answer 9, 0
    tool.copy_wide   v1 FT ×2   300, 300    --
                     v2 FT ×2   0, 0        wrong_answer 2 / trained_answer 3
    tool.copy_wide   v1 MIX ×3  110, 4, 37  --
                     v2 MIX ×2  0, 1        trained_answer 3, 19

**`malformed` is the never-stop signature and it is gone**: 420 of 420 on the
v1 fine-tune arm, 5 of 840 on the v2 one. What is left on v2 is
`wrong_answer` and `trained_answer` — which are the *control's own* failure
species, at the control's own rates (the four control seeds read
`wrong_answer` 0–16 and `trained_answer` 1–4 on `copy_wide`). So the arm is
not passing by writing a different kind of wrong thing; it is failing the way
an untreated checkpoint fails, on the few items it fails at all.

That is the mechanism confirmed rather than the outcome observed. Finding 74
inferred the cause from a corpus property and a retained generation; this
predicts what removing the property does, and it does that.

## What it costs, named rather than buried

**The control class occasionally stops one call early**, which is the
behaviour it teaches arriving where it was not wanted. `said_instead` on
`compound.items` goes 1–5 on the v1 arms to 9–21 on the v2 arms, and appears
on `compound.pipe` for the first time (0 on every v1 arm; 4, 0, 2, 0 on v2).
`compound.pipe` still clears the registered 40/48 on all four arms, so this is
a direction rather than a failure — but it is the honest other side of the
trade and it is the first thing to re-read if the H200 run is weak on
composition.

`compound.items` remains **characterisation and is not part of the read**: it
did not install in v1 (2–9/48) and it does not install in v2 (MIX 4 and 1, FT
11 and 7). The 11 is the highest any arm has read and it is one item outside
v1's range on a 48-item row; nothing there is a separation. Finding 66's
first-taker shape still dominates the bucket — `wrong_text` 16–22 across every
v2 arm — which is the same diagnosis v1 got and a different problem from this
one.

## The regression set

    row                  control ×4   v1 MIX ×3    v1 FT ×2   v2 MIX ×2   v2 FT ×2
    refusal.say /270        261-268   251,266,257   268, 266    249, 259   268, 266
    temporal.copy /353      353/353       353/353    353, 349    353, 353   339, 352
    temporal.route /400     396-399       397-398    399, 397    397, 398   399, 398
    tool.selection /200     109-130   146,136,151   116, 132    149, 142   128, 128

**`refusal.say` on the MIX vehicle is a pre-existing property of this family,
not something v2 added.** 249 and 259 sit against v1 MIX's 251, 266, 257, and
the `why` is `reworded` in every case (21 and 11 against v1's 19, 4, 13). The
compound MIX arm rewords refusals; it did so at v1 and it does so at v2, and
the two ranges overlap. The fine-tune vehicle shows none of it (268 and 266,
`reworded` 2 and 4, inside the control band).

**`temporal.copy` 339/353 on the v2 fine-tune's first seed is the one genuinely
new watch, and it is reported as unresolved.** That row reads 353/353 on all
four controls, all three v1 MIX seeds and one of the two v1 fine-tunes; the
other v1 fine-tune read 349 with `wrong_tool` 4. Here seed 1 reads 339 with
`wrong_tool` 14 and seed 2 reads 352 with `wrong_tool` 1. So the defect is not
new — `configs/mix_v3_compound.py` predicted it in as many words, because this
family trains `resolve_date` in a new envelope and made `temporal.copy` a
load-bearing watch rather than a conservative one — but **14 items is the
largest it has been, and the two seeds disagree by 13 on a row whose control
spread is zero.** The direction is a real one and the size is not readable at
two seeds, which is the same sentence finding 74 had to write about
`tool.copy` and is no more satisfying here.

## What this licenses, and who decides it

Against the pre-registered table this is **fixed**: the file is the freeze
candidate, and *the share decision goes to the owner with these numbers.* This
finding does not pick one, `configs/mix_v4_5b.py` builds cleanly with the line
at zero, and §7a's compound entry stays ORDERED until somebody signs it.

What the numbers say for that decision, stated plainly and without a
recommendation:

  * The mechanism finding 74 identified was the whole of the cost, and
    removing it removes the cost on both vehicles.
  * Class I is bought at 44–48 of 48 against a control of 0.
  * Class L is not bought, on either file, and is not evidence either way.
  * The price is a visible tendency to stop a call early, and one unexplained
    14-item loss on `temporal.copy` at one seed of one arm.

## Limits

Two seeds per arm, so directions rather than sizes (rule 6). And these are
nano readings: §3 item 4's caveat applies to the whole freeze, and the sizes
here transfer to the H200 run by argument rather than by measurement.

**Both fine-tune vehicles were scored at `ckpt.pt` and `last.pt`, and the two
seeds differ in whether that was worth doing.** Seed 1 selected best-val at
551, its final iteration, so its two files are the same weights and their
identical cards say nothing. Seed 2 selected at **490 of 551**, so its two
cards are genuinely different weights — and every registered cell reproduces:
`tool.copy` 120 both ways, `compound.pipe` 48 both ways, `temporal.copy` 352
both ways. What moves is `copy_wide` 294 → 296, `items_first` 6 → 7,
`refusal.say` 266 → 265 and `tool.selection` 128 → 130, all inside a single
run's wobble and none of them on a row this finding reads. So selection is not
flattering the arm, which is the sixth finding's rule answered by measurement
rather than by design, and the tables above quote `ckpt.pt` throughout.
