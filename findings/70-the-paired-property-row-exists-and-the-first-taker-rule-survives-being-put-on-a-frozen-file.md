# The first-value rule holds on a new fixed test set

**Full result:** The paired-property row exists, and the first-taker rule survives being put on a frozen file

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`evals/paired.jsonl`, added 2026-08-26 by `scripts/make_evals.py --add` and
scored on six checkpoints. R3 of `docs/PLAN-P3-RULERS.md`, specified by
`docs/PLAN-CORPUS-GAPS.md` §1, and built for the sixty-sixth finding — which
measured a *rule* on a hand-run probe of six substances and had no instrument to
carry it. No training; the row is a ruler.

## What the row is

128 items over four shapes — `melt_boil`, `born_died`, `capital_largest`,
`length_width` — each a written passage where **two same-type values share a
clause under different property labels**. Every fill appears in both clause
orders and both questions, `daycross.jsonl`'s construction extended by the flip
finding 66 used as its control, so the gold sits second in **exactly half** the
items by construction rather than by a sampled balance. The fills are invented:
`scripts/check_paired.py` asserts every entity and place name against
`corn.tools.FACTS`, `data/raw/extract.txt` (27MB) and all twenty other eval
files, because a gold the weights could recall is a gold that never tested
whether the window was read.

**The guard earned its place before the file was frozen.** The first build wrote
"born in A and died in B", which puts `died` two words from *both* values —
`property_local` accepted 40 siblings and rejected 24 golds, and the items were
ordinary distractor items wearing the shape of paired ones. The check caught it
at build. The shipped passages put each label beside its own value and no nearer
the rival.

## The read, before any treatment

    checkpoint          paired   gold first   gold second   first-taker
    corn_jr_260m        11/128      9/64          2/64          4 of 7
    ftextract           50/128     43/64          7/64         31 of 34
    ftwide              23/128     16/64          7/64         15 of 23
    ftnarrow            27/128     19/64          8/64         16 of 22
    ftwide_seed2        25/128     18/64          7/64         15 of 22
    ftnarrow_seed2      20/128     14/64          6/64         15 of 23

**Finding 66 reproduces on a frozen file and is not an artefact of its probe.**
`ftextract` — the only checkpoint that extracts at all — scores 43/64 when the
answer is stated first and 7/64 when the same fact is stated second: a
**56-point positional split on items whose only difference is clause order**.
Of its 34 wrong answers that took a value, **31 took the first-stated one
(91%)**, against the probe's 20 of 21. The retained generations say it plainly:
asked for the melting point of Quessalite, over "It boils at 2604 degrees
Celsius and melts at 1385", it answers *"It's 2604 degrees Celsius."*

**The total is the number that means least, which is why §1 asked for two.**
50/128 is 39%, and a checkpoint that read no property term at all and took the
first value every time would score close to it by construction. The split and
the first-taker rate are what separate them, and on this row they say the
property term is not being read.

**The four p3b2 arms confirm the row is measuring extraction and not something
else.** They never saw an extraction transcript, they score 20-27 of 128, and
their dominant failure is `invented` (77-78 of 128) rather than a taken value —
the base is the same at 11/128 with 64 inventions. The plan's expectation was
"`ftextract` reproduces finding 66's rule; the base declines or invents", and
that is what the row reads. Their first-taker rates (65-73%) are computed over
22-23 valued errors and are not comparable to `ftextract`'s: a checkpoint that
mostly invents is not choosing between the two candidates at all.

**One thing the seed does not do here.** The paired totals move 23 → 25 and
27 → 20 across the seed — inside the ±8-of-120 spread the sixty-eighth finding
measured on the frozen rows the same day, and nowhere near the 26-55 turns the
sixty-ninth found on the live grid. The row behaves like the frozen set it lives
in.

## The four shapes fail in three different ways, and the pooled `why` hid it

The retained generations raised a question the first six scorecards could not
answer, so `by_shape` was added and all six re-scored. On `ftextract`:

    shape             pass    how the rest failed
    length_width     20/32    took_first 10, took_second 2 -- no abstentions
    capital_largest  13/32    took_first 10, invented 5, abstained 4
    melt_boil        12/32    took_first 11, abstained 7, invented 1
    born_died         5/32    **abstained 23**, invented 4

**`born_died` does not get the answer wrong. It declines to answer.** Twenty-
three of its 32 items come back as an honest miss, and it contributes almost
nothing to the first-taker count that the other three shapes fill. So the
pooled 50/128 is two unrelated defects added together: a positional rule on
temperatures, dimensions and place names, and a refusal to read years out of a
window at all. A corpus arm graded on the total would be treating them as one
thing, and could move the total by fixing either.

The p3b2 arms inverse it, which is consistent with them never having seen an
extraction transcript: `ftwide_seed2` reads `born_died` 13/32 — its best shape —
while `melt_boil` is 1/32 with 29 inventions. A checkpoint that invents freely
scores best where the answer space is narrow (a four-digit year beside another
four-digit year) and worst where it is wide.

## What it cost, and what it did not disturb

`--add` wrote one file and touched nothing else: 24 existing files verified and
left alone, `evals/manifest.json` the only tracked file to change. The base's
re-score reproduces **55 of 55** shared quantities against its committed
scorecard, so adding the row moved no number that existed before it.

## What it licenses

The corpus arm §1 specifies — paired-property windows with the gold second half
the time — is now gradable on the quantity it exists to move, and the grading
rule is written down before the arm: **a treatment that halves the span error
and leaves the first-taker rate at ceiling has not treated the rule.** The
runtime repair (`corn.extract.property_local`) can only turn wrong answers into
declines, so it can move `abstained` and never the hit rate; on this row it
would convert `ftextract`'s 31 `took_first` into declines and leave 43/64 →
7/64 exactly where it is.

## Limits

The passages are written, not found, and they are deliberately regular — one
lead sentence, one paired clause, one tail — so the row measures the rule under
clean conditions rather than under the noise of real prose. The source field
reads `example.org` rather than `wikipedia.org`, honest for invented text and a
token the extraction corpus never carried; it is constant across every item and
both gold positions, so it cannot move the within-item contrast, but it is not
nothing on the totals. Four shapes and 32 items each, so the per-shape column above is
thin — 23 abstentions of 32 is not thin, but a 2-item difference between two
shapes is. Every card here was re-scored after `by_shape` was added and all six
reproduced their totals, splits and first-taker counts to the item, so the
breakdown cost nothing but card time; what it does not buy is a second seed on
`ftextract`, which has none, and it is the only checkpoint whose numbers here
are about extraction rather than about invention.
