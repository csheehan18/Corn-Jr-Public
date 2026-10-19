# One test moved 18 items on the random seed alone

**Full result:** The row that never moved moves eighteen items on the seed alone

**Cost:** 7.1 min of scoring on the 2 cards first cited here (`nano20m_balanced_seed2`, `nano20m_narr10_temp11`); it also reads 1 card scored for an earlier finding (`nano20m_balanced`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

> **Corrected by the eighteenth finding.** The headline number below is real and its
> explanation is wrong. `tool.copy`'s 18 items are not 18 independent draws — that row is 120
> prompts over **six** answers, and the fall is one of them. The general claim, that the
> generation-scored rows are noisy where the language rows are not, survives on
> `tool.validity` and `variety.distinct3`; the `tool.copy` half of it is a resolution limit
> rather than variance. Read the two findings together.

Two runs, and the second one invalidates part of the first.

**The attribution arm.** The sixteenth finding cut narrative and temporal together and
`tool.copy` fell 120/120 → 111/120 on a tool slice byte-identical to `balanced`'s, which left
the regression unattributed. `nano20m_narr10_temp11` restores temporal to `balanced`'s exact
14,570,815 tokens and leaves narrative cut at 10.00%, so the three corpora form a triple with
one moving slice between each adjacent pair. 1,050.9s.

**The seed replicate.** `nano20m_balanced_seed2` is `nano20m_balanced` with `seed` 1337 → 1338
and nothing else — same `data_dir`, same bins, same bytes on disk, 2 differing fields of 30 and
one of them only names an output directory. 1,045.7s. Sixteen findings have compared behaviour
rows against each other without ever measuring what those rows do when nothing changes.

| row | `balanced` 1337 | **`balanced` 1338** | `narrative10` | `narr10_temp11` |
|---|---|---|---|---|
| `lm narrative` | 0.3679 | **0.3677** | 0.4667 | 0.4670 |
| `lm temporal` | 0.0944 | **0.0947** | 0.0972 | 0.0943 |
| `lm web` | 0.9106 | **0.9110** | 0.8502 | 0.8548 |
| `temporal.route` | 400/400 | **398/400** | 397/400 | 399/400 |
| `temporal.copy` | 353/353 | **353/353** | 352/353 | 353/353 |
| `tool.validity` | 171/181 | **158/181** | 169/181 | 165/181 |
| `tool.selection` | 150/200 | **154/200** | 116/200 | 122/200 |
| `tool.copy` | 120/120 | **102/120** | 111/120 | 114/120 |
| `schema.conform` | 172/200 | **174/200** | 174/200 | 165/200 |
| `variety.distinct3` | 89.34% | **87.49%** | 89.18% | 87.95% |

**`tool.copy` moves 18 items on the seed alone, and the corpus change the sixteenth finding
wrote up moved 9.** The row has read 120/120 on every corpus with an unrepeated tool slice and
was treated throughout as a stable ceiling; it is not one. `tool.validity` moves 13 items on
the seed alone. Both are larger than any corpus effect either row has been asked to report
since the thirteenth finding.

### The language rows are nearly deterministic and the behaviour rows are not

This is the shape of it, and it is why the confusion lasted sixteen findings. Across the seed
pair the three nats/byte rows reproduce to **0.0002, 0.0003 and 0.0004** — and the same holds
*across corpora* wherever a share is held fixed: the two corpora sharing narrative at 10.0000%
read 0.4667 and 0.4670, the two sharing temporal at 11.1283% read 0.0944 and 0.0943. Slice
share determines the language rows to four decimal places regardless of seed.

The behaviour rows, on the same checkpoints, swing by 10–18 items. They are a few hundred
greedy generations scored exact-match, and nothing about a clean loss curve constrains them.
**So the pipeline is reproducible and the rulers built on top of it are noisy**, which is the
opposite of the failure the project was watching for.

### The attribution question is answered, and then made moot

Restoring temporal restored **everything temporal** — `lm temporal` to within 0.0001 of
`balanced`, `temporal.copy` to a perfect 353/353, `temporal.route` to 399/400 — and left
`tool.copy` at 114/120. On its face that exonerates the temporal slice: it recovered its own
rows completely and did not carry `tool.copy` with it.

The seed replicate then says the question was never readable. 120 → 111 → 114 spans 9 items
against an 18-item swing from nothing at all, and the failure *modes* never agreed either —
`wrong_answer 9` in one arm, `trained_answer 6` in the other, `wrong_answer 18` in the
replicate. **`temporal.copy` and `tool.copy` ask the same question of two different tools, and
whether the first buys the second is still open**, now for want of a measurement rather than
for want of an arm.

The third corpus did leave one thing that is not noise. It sits at an endpoint or between the
other two on all three moving shares, and reads outside both on `tool.validity`,
`schema.conform` and `variety.distinct3` simultaneously. No slice share can produce that, and
naming it is what prompted the replicate.

### What this reprices, and what it does not touch

The large effects are untouched, and it is worth saying which, because the reflex after a
result like this is to distrust everything:

| claim | size | verdict |
|---|---|---|
| `schema.conform` 0/200 → 194/200 (fourteenth) | 194 | stands |
| `tool.validity` 112 → 167, `tool.selection` 0 → 146 (eleventh) | 55, 146 | stands |
| `tool.copy` 27/120 → 120/120 (thirteenth) | 93 | stands |
| every nats/byte comparison in the project | ≥0.005 | stands |
| structured 10% → 2.5% "better on every axis" (§11) | 21, 3, 2 | **weakened** |
| `tool.copy` 120 → 111 from the narrative/temporal cut (sixteenth) | 9 | **withdrawn** |
| `variety.distinct3` 89.3 → 89.2 (sixteenth) | 0.1 | **withdrawn, as written** |

The middle row is the one that costs something. "2.5% is better on every axis that matters" was
carried by `tool.copy` 99 → 120 (21 items), `tool.validity` 168 → 171 (3) and `temporal.route`
398 → 400 (2). Only the first is even comparable to an 18-item seed swing, and the one movement
clearly outside noise — `schema.conform` 194 → 172, 22 items — runs the *other* way. **The
honest form is that 2.5% costs 22 items of schema conformance and buys nothing yet shown to
exist.** That does not restore 10%; it means the share is unpriced, which is a different and
worse position than the one §11 recorded.

`variety.distinct3` moved **1.85 points on the seed alone**, against 0.1 across the largest
corpus change the project has made and 1.39 across all three corpora. Its first noise estimate
is larger than every corpus effect yet measured with it.

### Three things worth recording

**The row treated as unreadable moved least.** `tool.selection` has carried "differences under
~35 are not readable" since the thirteenth finding, inferred from adjacent checkpoints of one
run. Across the seed pair it moved **4 items**, while `tool.copy` — assumed a ceiling — moved
18. The two assumptions the series has been running on were both backwards, and no amount of
staring at scorecards would have shown it.

**The blended val is noise-dominated, again.** The seed pair's `val` differs by 0.0481 while
its frozen-set language rows differ by 0.0004 — two orders of magnitude, on identical data.
§9's finding that composition sampling is 71% of that row's variance now has an independent
corroboration it did not ask for.

**One pair is not a distribution.** This establishes that an 18-item movement on `tool.copy`
occurs with no cause. It does not give a standard deviation, and treating 18 as a threshold
would be the same error one level down. What it licenses is the weaker claim that small deltas
on the generation-scored rows were over-read, and the practical one: **behaviour-row
comparisons need replicates, and at 17.5 minutes a run there is no excuse not to have them.**
