# The extractor takes the first value of the right type

**Full result:** The extractor takes the first value of the right type, and flipping the clause flips which question it answers

**Cost:** 11.4 min of scoring on the 1 card first cited here (`corn_jr_260m_ftextract`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn_jr_260m_ftextract`, 2026-08-26, the checkpoint the sixty-fifth finding
trained. Measured through the real runtime path — `harness/backends/read.py`'s
`Reader`, `corn.extract.read_passage`, `corn.extract.reduce` — on synthetic
passages, at temperature 0. No training, no network.

## Where it came from

The sixty-fifth finding's end-to-end check answered five of six entity-property
lookups and got one wrong: asked for the **boiling** point of iron it returned
1538, the melting point. Both facts sit in one sentence — "Iron melts at 1538
degrees Celsius and boils at 2862 degrees Celsius" — and two hypotheses were
offered for it: windows cut mid-sentence, or windows too small to carry the
context that disambiguates.

**Both were tested and both are wrong.** Widths 64 through 256 and
sentence-aligned windows at four token budgets, eight queries over three pages:

    config                        hit  wrong  declined  windows  batches
    fixed width=64 stride=32        7      1         0       62        8
    fixed width=96 stride=48        4      1         3       38        8
    fixed width=128 stride=64       2      1         5       27        8
    fixed width=192 stride=96       4      1         3       19        8
    fixed width=256 stride=128      5      1         2       11        8
    sentence-aligned <=64tok        4      3         1       43       37
    sentence-aligned <=96tok        5      1         2       27       27

Bigger windows lose hits to *declines*, not to wrong answers — more context
makes him less willing to commit rather than better at choosing. And **sentence
alignment costs the batching outright**: 43 windows fragment into 37 batches
against 62 windows running as 8, because whole sentences have unequal token
lengths and `BatchedReader` needs equal ones — `StaticCache.pos` is a single
scalar shared by every row. That is the reason `corn/extract.py` chunks by
token count, restated as a measurement.

**The `wrong` column is 1 in every row.** No windowing scheme fixes it, which
is what said the defect is not about windows.

## What it actually is

Three conditions over four substances, the same two facts each time:

    together (one sentence)   HIT 4/8   SWAPPED 3/8   DECLINED 1/8
    split (far apart)         HIT 6/8   SWAPPED 2/8
    alone (only one present)  HIT 7/8   DECLINED 1/8

Asked for the melting point — always stated first — he was right 4 of 4. Asked
for the boiling point he was right 0 of 4.

**The control that settles it is flipping the clause.** Six substances, both
orders, both questions:

    order        verdicts                    took the FIRST-stated value
    melt-first   6 correct 5 swapped 1 dec   11 of 11 that answered
    boil-first   5 correct 5 swapped 2 dec    9 of 10 that answered

**Of the 21 cases where he answered at all, he took the first-stated value 20
times.** Writing "boils at B and melts at A" makes the boiling point the one he
gets right and the melting point the one he swaps. Asked-property accuracy —
melting 7/12, boiling 4/12 — is entirely an artefact of which clause each
fixture happened to put first.

So the rule the weights implement is **"the first value of the gold's type in
the window"**, and the question's property term is not read at all when two
candidates of the same type are present.

## It is not a diversity gap in the slice, and that was checked

The obvious repair is more varied training questions. The slice already has the
general case: **71% of `extract.txt`'s answerable windows carry a same-type
distractor**, against the frozen eval's 79% (`extract_distractor_rate` in
`evals/manifest.json`). So the model has seen a competing number in the window
17,772 times and still learned a positional rule.

What it has *not* plausibly seen is the narrow case where two candidates share
a clause and only a verb separates them — "melts at" against "boils at". A
distractor three sentences away is discriminated by every content word around
it; a distractor five tokens away is discriminated by one. `make_evals.py`
already names this rule as the thing its distractor rate exists to defeat —
"say the first number in the passage is the wrong rule that would score well" —
and the eval measures it while the slice does not teach against it.

## What this cannot say

**Synthetic fixtures, small n.** Four to six substances per condition, one
sentence template, all temperatures in degrees Celsius. This is not the frozen
eval and no floor has been measured for it. What carries the weight is the
*flip*: the same fixtures answer differently when the clause order changes, and
that comparison is internally controlled.

**Numbers only.** Every gold here is a quantity, so `_has_distractor`'s digit
branch is the one under test. Whether the same positional rule governs the name
branch — two capitalised entities in one clause — is unmeasured and is the
cheapest extension.

**Temperature 0 throughout**, so there is no decode noise, and equally no
evidence about how the rule behaves under sampling.

## What follows

Two repairs, and they are not alternatives:

    runtime, no training    reject an extraction whose span is not local to
                            the question's distinguishing term. Converts
                            SWAPPED into DECLINED, which the runtime already
                            handles by falling back to the reduced lead
                            sentence -- and a wrong number spoken confidently
                            is the one outcome `_web_search` is built to avoid

    corpus, one arm         paired-property windows where the gold is the
                            *second* value often enough that "take the first"
                            scores badly. `corn/extractgen.py` work, a slice
                            rebuild and a fine-tune -- about the cost of the
                            sixty-fifth finding's run

The runtime repair is strictly safer and does not raise the hit rate; the
corpus repair is the one that could. **The order matters**: shipping the
runtime rejection first means the corpus arm is measured against a base that
declines rather than one that answers wrongly, which is the comparison
`extract.span` and `extract.abstain` are designed to read together.
