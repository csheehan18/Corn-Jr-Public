# Hundred-and-third finding — the three seed heads averaged rank the gold first on four more passages than the best of them, while any one of them being right would be sixty-one more, so the pick's seed variance is real and averaging does not harvest it

`scripts/harvest_popa_pairs.py --span-head s1 s2 s3`, 2026-09-04. No head
was trained: the three shipped built heads (`reader_built_s{1,2,3}.pt`) read
Population A's 3,893 windows off the popa cache, their pair logits averaged
before the argmax, 34 s on the GPU. `evals/results/pairs_ens_s123_popa.json`
and `reader_funnel_ens_s123.json`. `corn/reader.py` is untouched.

## 0. Why this read, and what it was to decide

Finding 102 left the span head at training loss 0.03 and held-out exact-pair
0.54 with more epochs buying nothing: a generalisation gap, not an
under-trained head. The levers for a gap split by what the gap is made of.
If the three seed heads err on *different* windows the gap is variance, and
weight averaging, ensembling and stronger regularisation are the cheap
next arms. If they err on the *same* windows the gap is bias in what the
frozen states carry, and only data, labels or representation can move it.
The cheapest instrument that separates the two is the ensemble the project
already owns: three heads of one recipe on three seeds, on a population none
of them trained on.

Pre-stated before the run (this session's recommendation to the owner): the
pick stage moves by fifteen or more passages, and averaging pays; under ten,
and the next arms are labels and data.

## 1. The pick stage, four ways

`probe_reader_funnel.py --pairs` on the ensemble's pairs file, with the
seed-1 reader harvest supplying the gold windows. The first two funnel
stages read the pairs file alone, so they are the ensemble's own.

    passages, of 721 answerable         s1     s2     s3    mean   ensemble
    the gold in some gold window's ten  678    679    676   677.7     681
    the head ranks it first there       494    484    493   490.3     498

    gold-bearing windows, of 1,211      731    700    723   718.0     739
    on which the gold is ranked first

    passages ranked first by:   two of three 493    any of three 555    all three 423
    windows ranked first by:                        any of three 837    all three 596

**The mean-logit ensemble is +4 passages over the best single head and +8
over their mean.** Majority vote across the three is 493, the best head's
number. The pick *rate* over windows whose ten holds the gold is unchanged:
739 of 1,109 (66.6%) against seed 1's 731 of 1,097 (66.6%); the ensemble's
whole gain is that its ten catches twelve more windows and three more
passages, which is a generation gain and not a pick gain. The winner's
median lead over the gold falls from 3.44 to 3.06 logits, still a confident
miss.

**And the oracle says the variance is there.** Some one of the three heads
ranks the gold first on 555 passages, sixty-one more than the best head; all
three agree on only 423. At the window level 837 against 731. The seeds
disagree on about one gold-bearing window in five, and on those windows the
ensemble sides with the wrong head as often as the best head is wrong alone.

## 2. Reading

This is the shape of disagreement that averaging cannot help: when the heads
split, the one that is wrong is not less confident than the one that is
right, so the mean inherits the error. Whatever separates 498 from 555 is a
choice *among* heads on the windows where they differ, and a choice among
candidate spans by a second scorer is the pick problem itself, which the
re-ranker (finding 86), the listwise verifier (finding 99) and the encoder
(finding 100) have each failed to make.

By the rule set before the run, four is under ten and the cheap
variance-reduction arms — EMA or SWA of the weights, a dropout and
weight-decay sweep, state noise — are not the next thing. They would reduce
each head's variance around a mean that is itself wrong on the same windows.
They remain cheap (about three minutes a point) and never-asked, and are left
as an option and not a recommendation.

**What is left on the pick is data, labels and representation.** Labels:
`train_reader.py`'s loss already sums the probability of every annotated
occurrence of the gold (`spans` carries more than one on 7,842 of 100,084
positives), and only 1,752 positives (1.75%) hold an unannotated further
occurrence of the answer string, so "credit every occurrence" is already
pulled; the label lever that remains is the `EQUIVALENT` class finding 95
measured at 15% of refused-wrong golds, which needs relabelling and waits on
the owner's spot check (`docs/SPOT-CHECK-REFUSED-WRONG.md`). Data: SQuAD 2.0
as minority supervision (audit L18) was blocked on disk at 19 GB free; the
states drive now has 50 GB free against a 38 GB positive cache, so it is
blocked on the owner's licence line only. Representation: the layer band
(row 36) and the prompt-form variants (L16, L17), each a fresh state
harvest.

## 3. On disk

`harvest_popa_pairs.py --span-head` now takes several heads and averages
their pair logits; one head is byte-identical to before, and
`--check-against` is refused for an ensemble whose spans are nobody's.
`pairs_ens_s123_popa.json` is in the single-head pairs format with
`span_head` and `seed` as lists, so every replay tool reads it unchanged.

## 4. Limits

One ensemble rule, the mean of raw logits; the three heads share one recipe
and 95% of their training articles, so this is a lower bound on what a more
diverse ensemble would show and an upper bound on nothing. The any-of-three
oracle is handed the answer and is quoted as a bound on variance, not as a
reachable number. Population A only; the held-out slices differ by seed so
no held-out exact-pair for the ensemble exists. The downstream funnel stages
(admission, vote) for the ensemble were read with seed 1's verifier and are
not quoted because that verifier was cross-fitted to seed 1's head.
