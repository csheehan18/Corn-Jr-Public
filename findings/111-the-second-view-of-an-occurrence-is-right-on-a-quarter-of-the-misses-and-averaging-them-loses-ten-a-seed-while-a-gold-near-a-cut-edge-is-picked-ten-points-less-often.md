# Hundred-and-eleventh finding — the second view of an occurrence is right on a quarter of the first view's misses and averaging the two loses ten passages a seed, rivals are mentioned as rarely as golds, self-agreement across the overlap adds nothing to the margin, and a gold within three tokens of a cut edge is picked ten points less often on both seeds

2026-09-04. **Replay only** — no GPU, no decode, no weight read.
`scripts/probe_two_views.py` (new) over `nullpr_s{1,2}_popa.json`,
`pairs_built_s{1,2}_popa.json` and the `bpe8k` tokenizer, importing finding
110's occurrence join. Two seeds at the bar protocol, extent on, hybrid
reduce, each at its own threshold. `evals/results/two_views.json`.
`corn/reader.py` and `corn/extract.py` are untouched.

## 0. What ran

Finding 110's machinery makes every candidate in every window's ten an
*occurrence*, a character position in the passage. Windows step by half
their width, so on most passages one occurrence is read by two windows under
two contexts, and the pipeline has never compared those two readings before
the argmax. Five reads followed from that, pre-registered in the file's
docstring, in the order the follow-up plan gave them: combine the two views
before the argmax (idea 1), a topic-entity prior from occurrence counts
(idea 4), the pick rate against the gold's distance from a cut edge (idea 5),
the extent rule's consistency across views (idea 6), and self-agreement
across the overlap as a free admission feature (idea 2). The join locates
38,930 candidates a seed and fails on 349 / 363 of them, which are scored
alone.

## 1. The two views, combined before the argmax — killed

**The second view is right on a quarter of the first view's misses.** Over
gold-bearing windows whose ten holds the gold (1,097 / 1,101 a seed), the
argmax is the gold on 731 / 700, finding 103's 66.6% / 63.6%. Of the 366 /
401 misses, another window's ten holds the *same occurrence* of the gold on
232 / 251, and there it is rank 1 on **57 / 66**. So the neighbouring window
does sometimes know what this one does not, and the passage-level statistic
already harvests it: "some gold window ranks the gold first" reads 494 / 484
because it is an OR over views.

Combining the views replaces that OR with a mean, and the mean loses:

                              gold ranked first      per-window rate
    shipped (each view alone)     494      484        66.6%    63.6%
    logprob, mean over views      484 −10  472 −12    66.7%    64.3%   (primary)
    dev, mean over views          484 −10  473 −11    66.3%    64.1%
    raw, mean over views          488  −6  473 −11    67.3%    63.9%

The per-window rate is flat to +0.7 points and the passage count falls by
ten and twelve. That is finding 103's shape a second time, with context as
the variance source instead of the seed: any-of-three heads read 555 against
a mean of 498 there, and here any-of-two views reads 494 against a mean of
484. **Averaging removes the disagreement the OR was living on, and the vote
downstream cannot tell which view to believe.** The go bar (≥ +15 gold-first
on both seeds) is missed by 25 and 27; the per-window rate did rise on both
seeds so the kill as written does not fire, and the arm is closed on the go
bar. Through the bar protocol the primary combination reads +3 (2 / 5) and
+0 (5 / 5) right with 566 / 586 window picks moved, on margins computed for
the old argmax, which is the floor the docstring said it would be.

## 2. The topic-entity penalty — killed

The hypothesis was that Wikipedia repeats its subject and mentions the
answer once, so a span's occurrence count would separate topic from answer.
On the 122 / 104 residue passages the reader spoke a wrong span on (`RIVAL`
and `AGGREGATION` at own t), the spoken text occurs in the passage exactly as
often as the gold on **100 / 84**, more often on 12 / 10, less often on 10 /
10. The go bar was ≥ 60% "rival out-occurs gold"; it reads 9.8% / 9.6%. The
cost side is the same picture: on the 731 / 700 windows the argmax is right,
it out-occurs the runner-up on 10.5% / 11.0% and ties it on 82%. **Rivals
are mentioned as rarely as golds.** The prior has nothing to act on.

## 3. Edge distance — a mechanism for W1, measured

The first version of this read binned the gold by its distance from either
window edge and read the *opposite* of the hypothesis, 70.8% / 69.2% rank 1
within three tokens of an edge against 65% / 63% deep inside — because the
first window's left edge is the passage's own start, where a definitional
first sentence holds the answer. Counting only **cut** edges (a window's left
edge unless it is the first window, its right edge unless it is the last):

    tokens from the nearest cut edge    seed 1              seed 2
    0–3                                  77   59.7%          74   59.5%
    4–7                                  86   65.1%          89   61.8%
    8–15                                184   64.7%         180   59.4%
    16–31                               325   64.6%         330   63.3%
    32 and more                         383   70.0%         386   66.6%
    no cut edge (one window)             42   76.2%          42   66.7%

**A gold within three tokens of a cut edge is picked ten and seven points
less often than one thirty tokens from any cut**, on both seeds, and the
curve is monotone enough to read as one. It is the first measurement on the
record that the window boundary itself costs the pick something, which W1
(`PLAN-READER-WHOLE.md` §3) has argued from the window-count distribution
and never measured. Its size is small: the windows within seven tokens of a
cut are 163 / 163 of about 1,100 a seed, and a ten-point deficit on them is
about sixteen windows, fewer passages, some of which the other view already
recovers. That is consistent with the audit's estimate for the window as a
lever and does not enlarge it.

## 4. The extent rule across the views — nothing there

On the residue, the gold is the argmax in two windows on 35 / 32 passages,
the extent rule widened it differently on 2 / 3, and on **none** is one
widening right and the other wrong. `CLIPPED` is not a disagreement between
views.

## 5. Self-agreement across the overlap — killed

Finding 110's L1 found agreement between the head and the generator refuses
wrong answers at the cost of a decode per window. The free version is
whether the neighbouring window's argmax is the same occurrence: +1 on 1,621
/ 1,610 windows, −1 (the neighbour's ten holds this argmax's occurrence and
picks something else) on 1,067 / 1,088, 0 (no second view) on 1,205 / 1,195.
As a raw bit it separates "the argmax is the gold" at **AUC 0.613 / 0.600**,
against L1's generator agreement at 0.69. Under the same two-feature bar CV
one fold on each seed chooses β = 0 and the other β = 0.25, and the arm reads
**−1 / −1 right** (3 / 2 on both seeds, p = 1). The willingness control has
nothing to say because nothing moved. Two views of one head agree because
they are one head; the generator agreed because it is a different readout,
and even that one the verifier had already priced.

## 6. What the five say together

    read                          go / bar                       result                  verdict
    1  views combined             gold-first ≥ +15 both          −10 / −12               closed on the go bar
    2  topic-entity prior         rival out-occurs gold ≥ 60%    9.8% / 9.6%             killed
    3  edge distance              a read                         −10 / −7 points at 0–3  W1's mechanism, small
    4  extent across views        a read                         0 / 0                   nothing there
    5  self-agreement             ≥ +10 both, p < 0.05           −1 / −1                 killed

The overlap between windows is not a second opinion the pipeline is wasting.
Where the two views disagree, the OR the passage statistic already takes is
the best a read-time rule can do with them, and every rule that tries to be
cleverer than the OR loses passages. What the join did buy is §3: a measured,
two-seed, monotone cost of the window boundary on the pick, which is the
premise W1 rests on and which it can now be read against.

## 7. What this cannot say

**§1's full read reuses margins computed for the old argmax.** A window whose
pick moved is admitted on a verifier row about a different span; the +3 / +0
is a floor, and a re-harvested verifier could read higher. It cannot read
past the pick stage's own −10 / −12, which is measured on the head alone.

**§2 counts case-insensitive string occurrences**, so "the Beatles" and
"Beatles" are two texts. A lemmatised or entity-linked count could read
differently; nothing on the record suggests it would reach 60%.

**§3 is a rate over windows, not passages**, and the bins under 100 windows
carry about five points of binomial noise each; the claim rests on the two
ends of the curve agreeing on both seeds, not on any one bin.

**§5's feature has three values** and the CV's grid for β is coarse; a
finer grid could find a small positive on one fold, which is what the fold
disagreement in finding 110 already showed for two-feature admission rules
generally.

**Nothing is selected on Population A**; every weight and threshold is chosen
on one fold and read on the other.

## 8. On disk

`scripts/probe_two_views.py` (new; imports `probe_free_replays.Seed` and the
occurrence join; about four minutes a seed on the CPU).
`evals/results/two_views.json`. `READER-AUDIT.md` rows 67–71 and reading-log
entry 111.
