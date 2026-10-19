# The answer score measures willingness to answer, not confidence

**Full result:** The isolated score is a willingness meter and not a confidence meter, ranking windows is the one thing it buys, and every read-time route to the span is now closed

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Eight read-only probes on the frozen `checkpoints/corn_jr_260m_v4/ckpt.pt`, run
2026-08-31 in one session. No training, no corpus change, no card touched;
inference only, fp32, and every number below is against that one checkpoint at
n=1. The thread began as a design conversation about decomposing extraction into
stages a 260M model can each do, and it ends having closed every stage except
the first.

`scripts/probe_enumerator.py`, `probe_detector.py`, `probe_series.py`,
`probe_scan.py`, `probe_scanread.py`, `probe_rescue.py`, `probe_tiebreak.py`,
with records in `evals/results/`.

## The central result

The isolated ask — cut a window to one candidate, ask the ordinary extraction
question — produces a score whose meaning had never been separated. Split by
what the *ordinary* read of the same window produced, on 186 gold-bearing NQ dev
windows:

| comparison | AUC |
|---|---|
| correct answer against **abstained** | **0.8522** |
| correct answer against **wrong span** | **0.5288** |

**The score knows whether he will speak. It knows nothing about whether what he
says is right.** That single dissociation retroactively explains five separate
failures in this session and one before it: detection reads 0.79 because
detection *is* engagement; selection reads 0.63 and cannot beat generation; the
hedge collapses because it was built on a number that predicts talking; and the
seventh vehicle's PMI calibration failed because it was normalising the wrong
quantity.

Everything the score is good for is downstream of that sentence.

## What ranking buys, and it is real

Item-level score — the maximum isolated score over the candidate list — ranks
windows. Cross-document AUC **0.7925**; **within one passage 0.8175**, which was
pre-registered to come in *lower* on the reasoning that windows of one article
share topic, entities and register. It came in higher. Holding the question and
the article fixed cancels item-level noise that a cross-document comparison
carries, so **ranking inside one document is this score's best case**, not its
worst.

Over 100 NQ dev passages, 443 windows, top-1 gold-bearing **80.0%** against
44.7% chance.

Read into answers (`probe_scanread.py`, same forward passes for every policy):

    policy      answered   rate    reads/item
    random            21   21.0%        1.00
    first             40   40.0%        1.00
    scan              44   44.0%        1.00
    readall           42   42.0%        1.59
    cascade           47   47.0%        1.55
    oracle            49   49.0%        1.00

**Reading in score order beats reading in document order by 5 items at equal
cost** (1.55 reads against 1.59) — the pre-registered primary, passed at exactly
its bar and therefore suggestive rather than settled. `scan` against `first` is
+4 and fails its bar, so reading only the top window is not supported.

**And the ceiling retires the premise.** `oracle` is 49 and `first` is 40:
window choice can buy **9 items of 100**, because on an NQ paragraph the answer
is usually near the front. The other 51 are extraction.

## Every read-time route to the span is closed

**Selection.** Top-1 over the isolated score covers the gold **44/200** against
greedy's own 94/200, on a candidate list whose covering ceiling is 117. Letting
him generate is better than twice letting him choose. The enumerator was not the
constraint: base-to-widened moves candidate AUC by 0.0096 against a 0.03
falsification while rivals per window go 4.80 → 9.28.

**The hedge.** A three-band take/hedge/quiet policy separates cleanly on
*detection* — 84.0% / 49.0% / 18.0% carry the answer, 152 of 190 splits clearing
a pre-registered 15-point bar. Joined to the retained generations it is right
**19.5%** end to end, and 19–24% at every split tried. The wording ladder, fixed
in the file before the run, calls everything under 40% an abstain wearing a
hedge's clothes and refused the sentence five times of five. **And the whole
band policy loses to the generator it wraps: best joint 198 against greedy's
215.**

**The rescue.** The largest single failure on a window that provably contains the
answer is that he declines it — 51 of 186, against 40 `wrong_span`, 9 `invented`,
8 near-miss. On those windows isolation endorses the gold **15.0%** and rivals
**1.1%**: he refuses the window and refuses every candidate in it standing
alone. The control is what makes that readable — the same procedure on windows
he answered correctly reads **96.4% gold / 12.7% rival**.

**The tiebreak.** On `wrong_span` isolation *does* discriminate — gold 57.1%,
rival 19.5%, a 37.6-point gap on the bucket AUC 0.5288 says is invisible — but
`unique` is 0, so it narrows ten candidates to about three and stops. Two
tiebreaks over 33 ambiguous windows, both below the null model:

    group           n  firstwin   random     perm   toggle
    wrong_span     33    33.3%    39.4%    20.7%    24.2%
    ok            114    57.9%    36.8%    92.2%    60.5%

**The `perm` dissociation is the finding and it is not what the column was built
to show.** Permutation majority recovers the gold 92.2% where the ordinary read
is already right and 20.7% where it is wrong. **Reordering the window's
sentences does not perturb his answer, it confirms it.** So whatever the
sixty-sixth finding's "first value of the right type" describes, it is not a
positional bias reordering can cancel — the error is a stable property of the
(question, window) pair, and `perm` underperforms chance precisely by
reproducing his own mistake four times.

That closes a family rather than a probe. Majority-over-perturbations,
self-consistency and sample-and-vote all assume the error is variance to be
averaged out; here it is signal. The sixty-eighth finding said this from the
seed side and this says it from the input side.

## What he actually does, and the shape hypothesis

Handed a window containing the answer he is right **78/186 = 41.9%**. Restricted
to windows whose answer is a short typed entity the enumerator can reach,
**56/101 = 55.4%**.

The gap between those two numbers is the one live lead. Against the `ok` group,
the abstained group is enumerable **39% against 72%**, carries
`answer_type: other` at **37% against 19%**, and its golds run **2.14 words
against 1.85**. The enumerator hunts capitalised runs and digits; he emits short
typed spans. **Both instruments fail on the same property — the answer is a
phrase rather than an entity.** 31 of the 51 abstentions and 19 of the 40
`wrong_span` items sit there: 50 of 108 failures.

That reframes the abstentions. A model declining because the answer is not the
shape it emits is doing something `score_extract_abstain` credits, and it is a
statement about what the corpus taught rather than about what the runtime hands
over.

## Corrections to the record

**`STATUS.md`'s "an overlapping candidate is enumerable 175/200 but the exact
gold only 109/200" does not reproduce.** Against `probe_isolation.candidates` —
the list the isolation pipeline actually runs — it reads **97 exact / 157
overlapping / 101 covering**, and the cap is not the cause: the mean list is
5.07 long and uncapping moves nothing. The pair was read off a different
candidate list. `probe_verifier.py`'s `PRIOR` carries the same two numbers and
its read (d) will disagree with itself when run. This is `probe_scorer.py`'s own
warning arriving: two candidate lists over the same weights give numbers that
cannot be pooled.

**The operative containment test is `score_extract_span`'s**, which asks for the
gold's content words rather than string equality — a candidate spanning
`Jourdan Miller from Bend` covers gold `Jourdan Miller`. Widened, the enumerator
reaches **144/200** (held out 141) at 37.5 asks an item, against 101 at 5.1.
That ceiling is now moot for selection and still bounds anything that picks.

## Limits, and two specification errors of my own

n=1 on one checkpoint. The populations are NQ dev paragraphs at WIDTH 64 /
STRIDE 32 — **4.4 windows a passage**, which is the shortest possible test of a
scan and the reason `first` is a strong baseline. `probe_detector`'s band table
is 50/50 answerable by construction; at the top-100 cut the detector is 42%
sensitive with an 8% false-positive rate, so precision falls to 36.8% where one
window in ten carries the answer and 21.6% at one in twenty. A real page is the
second regime and nothing here measures it.

`probe_scan`'s read (b) asked top-3 to beat chance by 20 points **without
checking that 20 points existed** — chance is 86.4% at 4.4 windows, leaving 13.6
— and an earlier draft printed "the scan does not have an instrument" off that
unreachable bar. It is reported VOID and the verdict keys on the primary alone.
`probe_enumerator`'s `units` variant first read identical to base on every row
because `_dedup` discarded `1538 degrees Celsius` as overlapping `1538`, which
deleted the extent fix the variant existed to price. Both are the same defect as
an under-powered run printing a verdict, and all four probes now guard against
it.

Nothing here licenses a corpus change on its own. What it licenses is a question
— whether the failure concentrates on phrase-shaped answers — that is now
measured rather than inferred, and that no vehicle so far has been aimed at.
