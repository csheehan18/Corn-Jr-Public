# A fix to the copy check lifts the whole-passage reader to 523

**Full result:** `grounded` now tests the span as said, first novel word to last with the frame words inside it kept, as one verbatim run of the window; the two frozen checkpoints re-score byte-identically on every pass count, one refused reply a checkpoint moving between failure buckets, and the whole-passage adapter reads 523 and 517 with AGGREGATION at 2 and 1

**Cost:** 62 s of scoring on the 2 cards first cited here (`corn_jr_260m_v4__grounded115`, `corn_jr_260m_v4_ft4g__grounded115`); it also reads 3 cards scored for an earlier finding (`corn_jr_260m_v4`, `corn_jr_260m_v4_ft4g`, `nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn/extract.py::grounded`, `scripts/check_extract.py`, 2026-09-05. The
owner took finding 115's repair the same day ("it was put in place when
results were much worse"), so this is the rule-4 record: the change, the
guard, the re-score of two frozen checkpoints with every moved row listed,
and the reader numbers under the new rule. `evals/results/corn_jr_260m_v4_ft4g__grounded115.json`,
`corn_jr_260m_v4__grounded115.json` (the `--only extract,paired` cards),
`whole_causal_s{1,2}_grounded115.json`.

## 0. The change

Before, the contiguity test ran over the reply's *novel* words alone, the
frame words having been stripped out from wherever they sat:

    novel = [w for w in said if w in window_words and w not in question_words
             and w not in source_words and w not in FRAME]
    return len(set(novel)) == 1 or longest_span(" ".join(novel), window) >= 2

After, it runs over the span as said from the first novel word to the
last, and the whole of that must be a verbatim run of the window:

    core = said[novel_at[0]:novel_at[-1] + 1]
    return longest_span(" ".join(core), window) == len(core)

Two things moved, and the second was found by the guard written for the
first. Keeping the inner frame words is what lets "best-of-seven",
"Stephen A. Douglas" and "Coton in the Elms" through. Requiring the whole
core rather than any two contiguous words is what keeps "1858 of
Illinois" out: with the frame word kept, the old `>= 2` would have passed
it on the strength of "of Illinois" alone, and two window facts joined by
a frame word is the invention the rule exists to refuse. The first draft
of the change had `>= 2`, the new guard case failed on it, and the rule was
tightened before any number was read. Frame words *outside* the span
("It's", "according to Wikipedia") are still stripped, which is what lets a
one-word fact through; the no-invention test and the novel-word
requirement are unchanged.

`scripts/check_extract.py` gains four cases: the three spans above are
grounded, and "1858 of Illinois" is not. All prior cases still pass.

## 1. Rule 4: the frozen checkpoints, re-scored

`python -m corn.evals --only extract,paired` on `corn_jr_260m_v4_ft4g` and
`corn_jr_260m_v4`, against their frozen cards:

    row               ft4g frozen -> now     v4 frozen -> now
    extract.span        97/200 -> 97/200       94/200 -> 94/200
    extract.abstain    111/200 -> 111/200     121/200 -> 121/200
    extract.brevity    395/400 -> 395/400     399/400 -> 399/400
    extract.paired     115/128 -> 115/128     117/128 -> 117/128

**Every pass count is byte-identical.** Inside `extract.span`'s failure
buckets one reply a checkpoint moves: `invented` 13 -> 12 on both, the
reply now landing in `wrong_span` -- a span the passage does contain,
framed with a function word inside it, that the old rule refused as
invention and the new one scores as what it is, a wrong answer. (The
`near_miss_*`, `span_loose` and `span_tight` rows in the new cards are
rows the harness has added since those cards were frozen, finding 82, and
are not this change.) The generative reader's numbers do not move because
it rarely emits a multi-word span with a function word inside it exactly.

## 2. The readers under the new rule

Population A, bar protocol, extent on, hybrid, own CV'd thresholds:

                     right  wrong  silent  u.silent  attempt  acc|att   paired vs 112 / 87
    shipped s1       392    192     137       199     0.810    0.671     +3
    shipped s2       391    175     155       196     0.785    0.691     +3
    W2 causal s1     523    127      71       198     0.902    0.805    +10 (p 0.021)
    W2 causal s2     517    125      79       200     0.890    0.805     +7 (p 0.065)

    species s1 / s2:  AGGREGATION 2 / 1 (from 16 / 10)   REFUSED_RIGHT 19 / 27
                      RIVAL 94 / 90   CLIPPED 33 / 35   UNGROUNDED 8 / 8

Correct silence is unchanged to a passage. **72.5% and 71.7% strict on
all 721**; paired against the shipped reader under the same rule, +131
and +126 right. The adapter's `AGGREGATION` residue, which on one window
could only ever have been the runtime refusing the head, is gone.

## 3. The guards

`scripts/check_extract.py` passes with the four new cases. `check_all.py`
reads 65 of 67 with the card idle: the two that fail, `check_churn.py`
(seven nano20m_v3 extract attributions no longer re-derive to their
scorecards' failure buckets) and `check_copyable.py` (`relpairs.txt`'s
window and search-query value counts), **fail identically with this change
stashed** -- both predate it and belong to other work, and are reported
here so nobody attributes them to the rule.

## 4. What this changes on the record

Finding 87's shipped point is 392 / 391 under the current rule rather than
389 / 388, and finding 112's arm is 523 / 517 rather than 513 / 510; both
findings stand as measured under the rule of their day and say so by date.
Finding 85's "12 contiguity defect" among the 22 unwinnable passages is
repaired. `READER-AUDIT.md` row 43 closes. The plan's arms
(`PLAN-READER-WHOLE-NEXT.md`) are now read against 523 / 517.
