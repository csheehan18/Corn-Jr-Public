# Hundred-and-tenth finding — the four free replays the audit ranked first: agreement between the two readouts and gate willingness add nothing at the silence floor that the margin does not already carry, per-bucket thresholds fit the folds and give it all back, and one vote per occurrence is the only one positive on both seeds, +10 / +6 at pooled p = 0.03 and under its per-seed bar on one

2026-09-04. **Replay only** — no GPU, no decode, no weight read, no
checkpoint opened. `scripts/probe_free_replays.py` (new) over
`nullpr_s{1,2}_popa.json`, `pairs_built_s{1,2}_popa.json`,
`crossfit_harvest_ft4g.json` (the gate's willingness and forced reply per
window), `multiwindow_ft4g.json` (the generator's `off+off` verdict per
passage) and the `bpe8k` tokenizer. Two seeds, both at the bar protocol,
extent on, hybrid reduce, each at its own cross-validated threshold, which
reproduces the shipped 389 / 199 and 388 / 196 before anything is read.
`evals/results/free_replays.json`. `corn/reader.py` and `corn/extract.py` are
untouched.

## 0. What ran and why now

`READER-AUDIT.md` Part 3 ranked its levers by expected passages per GPU hour
and put four zero-GPU replays at the top — L1's admission half, L2, L3, L4 —
with the sentence "the free replays first". The sessions after it ran L6, L7,
L18 and the representation plan's A1–A3 and skipped past these. Each carries
a pre-registered bar and kill in the audit, quoted below unchanged; every arm
here is a rule over the admitted-window mask and nothing downstream of the
mask differs from the shipped path.

One instrument is shared. A window's admission score becomes
`margin + w · feature` for L1 and L2, or a threshold drawn from the window's
bucket for L3, or the shipped mask with duplicates silenced for L4; the
weight, the thresholds and the bucket thresholds are chosen **per fold** under
the bar protocol (max `right` holding the fold's share of 200 correct
silences) and applied to the other fold. The grid for L1 and L2 starts at
`w = 0`, which is the shipped rule, so the CV can only leave it for something
that beats it in-fold. Every arm is paired against the shipped verdicts on
the same passages and read once more with the willingness control of finding
101 §7 — the shipped head shifted to the arm's attempt rate — so a re-tune
cannot pass as an arm.

## 1. L1's admission half: agreement between the head and the generator

**The two gates the audit set both clear.** Re-read at seed 2's own constant
(−1.6730, where the head reads 388 rather than 409 at seed 1's −2.02):

                       head   generator   both   union   union − head
    seed 1 (−2.0202)    389      279       235    433       +44
    seed 2 (−1.6730)    388      279       231    436       +48

The build gate of ≥ 40 clears by 4 and 8. The seed-1 row is the audit's
uncommitted read of 2026-09-03 to the passage, now in a script. The
generator-only wins split 21 / 23 and 25 / 23 head-silent / head-wrong. The
ceiling the audit asked for before the arm could run — head silent, generator
right, and the head's argmax on a gold window already the gold — reads **13
and 19** against a floor of 12, so the arm was licensed on both seeds.

**Agreement is a real signal and the verifier already prices it.** The
decline-banned forced reply keys (`_span_key`) to the same span the head
speaks on 40.8% / 40.3% of the 3,893 windows. As a raw bit it separates "the
spoken span is right" at AUC 0.693 / 0.694 over the answerable windows. Added
to the margin in finding 94's cross-fitted read of "this window carries the
gold" it reads **−0.0030 / −0.0001**.

**The arm, two-feature bar-protocol CV** (`margin + β · agree ≥ t`; grid β ∈
{0, 0.25, …, 4}):

                    right  wrong  a.silent | u.silent  attempt  acc|att   (β, t) per fold
    s1 shipped        389    188      144        199    0.800    0.674
    s1 + agree        403    150      168        200    0.767    0.729   (1.00, −1.217) / (2.00, −0.706)
    s2 shipped        388    172      161        196    0.777    0.693
    s2 + agree        389    158      174        198    0.759    0.711   (0.00, −1.598) / (0.75, −1.203)

Paired on `right`: **+14 (21 / 35, p = 0.081) and +1 (8 / 9, p = 1), pooled
+15 at p = 0.10.** The bar was ≥ +10 on both seeds at pooled p < 0.05; it is
missed on seed 2 by nine passages and on the pooled p. One of seed 2's folds
chose β = 0 — the shipped rule — which is the CV saying agreement bought
nothing in-fold on half of one seed.

What is consistent is not `right`. **Wrong falls by 38 and 14, the attempt
rate by 3.3 and 1.8 points, `acc | att` rises 5.5 and 1.8 points.** The rule
the folds found on seed 1 — β = 2 at t = −0.7 — is in effect "a window whose
two readouts disagree must clear a threshold 1.3 logits stricter than the
shipped one; one where they agree may be 0.7 looser", and it mostly refuses.
The willingness control says it is not only a re-tune: at the arm's attempt
rate the shipped head reads 380 / 173 / 211 and 381 / 167 / 211 (right /
wrong / correct silences), so the arm holds **+23 / +8 right and −23 / −9
wrong for −11 / −13 correct silences** at equal willingness. It moves
answerable passages from wrong to right and pays for it on the unanswerable
half; on the joint bit that is +12 on seed 1 and −5 on seed 2.

**Closed as an arm aimed at `right`**, under the bar it was written with. Not
banked and not closed as a precision shape: −38 / −14 wrong at a lower
attempt rate is the same category as finding 101's window features and is
the owner's call under the standing rule. It would cost a generative decode
of every window at read time — the forced harvest is one decline-banned
decode per window — which the runtime does not do on the head's path, so
unlike finding 101's five scalars it is not a re-pointing.

## 2. L2: gate willingness beside the verifier margin

**Killed at the cheap read.** Finding 94's protocol — the 580 answerable
passages carrying both a gold-bearing and a no-gold window, 2,498 windows,
cross-fitted logistic by passage parity, AUC for "this window carries the
gold":

                          seed 1     seed 2
    margin                0.8000     0.8147
    margin + willingness  0.8064     0.8195     Δ +0.0064 / +0.0048
    willingness alone     0.7445     0.7445

The kill was Δ < +0.01 on either seed; it fires on both. Willingness alone
reads 0.74, which is finding 83's 0.79 on a harder label, so the signal is
there and the margin carries it: `corn/gate.py`'s presence question and the
verifier's are the same question asked of the same trunk.

Finding 92 §2's silent-set read — passages the reader was silent on, the
should-have-spoken (answerable, the argmax on some gold window right) against
the correctly silent — is the one place willingness moves a number, and it
moves it on one seed:

                                    seed 1 (71 / 199)    seed 2 (79 / 196)
    max margin                          0.7129               0.7376
    max margin + max willingness        0.7718  +0.059       0.7450  +0.007
    max margin + willingness at argmax  0.7708  +0.058       0.7395  +0.002

+0.059 on seed 1 is the largest silent-set delta on the record and seed 2
reads it at +0.007; under the audit's two-seed rule it is one seed. The arm
was run anyway (`margin + γ · willingness`, γ ∈ {0, 1, 2, 4, 8, 16, 32}):
**+1 (3 / 4, p = 1) and +5 (9 / 14, p = 0.41)**, joint −2 / −5, one fold on
each seed choosing γ = 0. At the arm's attempt rate the shipped head reads
+2 right on both seeds — the arm is a re-tune. Constant 17 of the audit (the
gate never enters admission) is measured rather than assumed, and it does not
matter.

## 3. L3: per-bucket thresholds under the bar protocol

Eighteen buckets — the spoken span's answer type (name / number / other) ×
the question's label (`ROLE` / no label / other label, `probe_question_shape`)
× window position (first / later) — each with its own threshold, found per
fold by coordinate ascent from the fold's global bar `t` (a bucket's move is
kept only if the fold's silence share still holds and `right` rises; three
rounds) and applied to the other fold.

**Killed on both of its conditions.** Held out: **−2 (19 / 17, p = 0.87) and
−5 (10 / 5, p = 0.30)**, joint −15 / −3. In-fold, the ascent raised `right` to
212 / 215 and 199 / 209 on the training folds, against the 193–196 a fold
the shipped threshold reads on the same passages, and gave every passage of
it back on the other fold. The fold-agreement condition (no bucket's two
thresholds further apart than twice the global fold gap, 0.16 / 0.29) fails
on ten of eighteen buckets on seed 1 and five on seed 2; three buckets have
one fold at +∞ (silence the bucket) and the other inside the shipped range,
`other × ROLE × later` sits at −1.98 on one fold and −4.82 on the other, and
the buckets under ten windows (`number × ROLE × first`, `other × ROLE ×
first`) never move off the global value because they cannot.
**The 502-passage folds are being fitted**, which is what the audit's kill
was written to detect. Constant 10 (one threshold per seed) is not where the
admission errors are: finding 91's 27-point spread across question labels is
real and a threshold cannot spend it.

## 4. L4: `dedupe` with a tokenizer-defined occurrence

Finding 97's `dedupe` keyed one vote per distinct span **text** and said its
definition could not be the eighty-fifth finding's because the harvest has no
character offsets. With `bpe8k` loaded, `windows()` reproduces every one of
the 3,893 harvest windows and each window's start in the passage is
recoverable; the argmax's token position in the pairs harvest (`ij`, on the
escaped window's tokens, mapped back through the JSON escaping) locates the
spoken span inside the window when its text occurs more than once. An
occurrence is then a character position in the passage, and two admitted
windows that read the same occurrence count once while two occurrences of the
same text count twice.

**The tokenizer resolves finding 97's objection and changes one passage a
seed.** 93 / 91 passages speak one span text from two different occurrences,
so the two rules do disagree about the mask; at the vote they disagree about
the verdict on one passage a seed.

                    right  wrong  a.silent | u.silent  attempt  acc|att   paired right       masks moved
    s1 shipped        389    188      144        199    0.800    0.674
    s1 dedupe text    398    178      145        199    0.799    0.691   +9  (9 / 18, p = 0.12)    266
    s1 dedupe occ     399    177      145        199    0.799    0.693   +10 (8 / 18, p = 0.076)   252
    s2 shipped        388    172      161        196    0.777    0.693
    s2 dedupe text    393    165      163        196    0.774    0.704   +5  (10 / 15, p = 0.42)   232
    s2 dedupe occ     394    164      163        196    0.774    0.706   +6  (8 / 14, p = 0.29)    220

The text rule reproduces finding 97 to the passage (+9 at 9 / 18, +5 at
10 / 15). **Occurrence: +10 / +6, pooled +16 over 1,442 passages at
p = 0.029.** The willingness control shifts the shipped thresholds by 0.01
and reads the same silences: at equal willingness the rule converts **10 and
6 wrong answers into right ones and touches nothing else** — a ranking
correction, not a willingness move, which is what a fix to a double-counted
vote should look like.

**Neither the bar nor the kill.** The bar was ≥ +8 a seed at pooled p < 0.05:
the pooled p clears and seed 2 is two passages under. The kill was pooled
p ≥ 0.1 or either seed negative: neither. It is the audit's row 12 (`dedupe`,
open) moved from p = 0.12 / 0.42 on the text rule to p = 0.03 pooled on the
occurrence rule, positive on both seeds in three readings now (finding 85 at
JOINT, finding 97 at SHIPPED, here), and it is the only one of the four
replays that moves `right` the same way on both seeds.

## 5. The bars, in one table

    lever   bar                                       read                            kill                              verdict
    L1      ≥ +10 both, pooled p < 0.05               +14 / +1, pooled +15 p = 0.10   under the bar                     closed on `right`; precision shape open
    L2      ΔAUC ≥ +0.02 both, then ≥ +12 a seed      +0.0064 / +0.0048; +1 / +5      ΔAUC < +0.01 either: fired        closed at the cheap read
    L3      ≥ +12 a seed, folds within 2× the gap     −2 / −5; 10 / 8 buckets out     < +8 either, folds apart: fired   closed at the kill
    L4      ≥ +8 a seed, pooled p < 0.05              +10 / +6, pooled +16 p = 0.029  p ≥ 0.1 or negative: not fired    open, positive twice, under the per-seed bar on seed 2

Three of the four say the same thing findings 92, 94, 101 and 107 said from
other directions: **the verifier's margin already carries what the gate, the
generator's agreement and the question's shape know about admission.** The
audit's constants 16 (the forward's own outputs) and 17 (the gate) are now
measured on the admission side and neither moves a number at the floor. The
fourth is not an admission arm at all; it is the vote counting one piece of
evidence twice.

## 6. What this cannot say

**L1 is the free-decode form of the generator, not the generator that reads
279.** The forced harvest decodes every window with the decline banned; the
audit's own read says that replayed with every window admitted it reproduces
`off+off` on 667 of 1,003 passages. The union uses `off+off`'s real verdicts;
the agreement bit uses the forced replies. A generator allowed to decline
would agree less often and the arm might read differently; that arm needs a
decode of every window at read time either way.

**The two-feature CVs choose one weight and one threshold on ~500 passages.**
Finding 92 measured the threshold's own fold wander at ±7 passages; a second
parameter widens that, and the fold values here disagree (β = 1 against 2 on
seed 1, 0 against 0.75 on seed 2), so the reported `right` deltas carry more
noise than the shipped single-threshold read. That cuts both ways and is why
the pooled McNemar is quoted beside every per-seed number.

**L3's ascent is greedy** and a joint optimum over eighteen thresholds could
be higher in-fold; it could not be more held-out, because the in-fold gain it
found was already given back entirely.

**L4's pooled p treats the two seeds' passages as independent trials** when
they are the same 1,442 passage-reads under two heads; it is optimistic, as
finding 101's was. The per-seed p-values (0.076, 0.29) are the honest ones,
and they are not significant.

**Nothing here is selected on Population A.** Every weight and threshold is
chosen on one fold and read on the other; the reports are held-out.

## 7. On disk

`scripts/probe_free_replays.py` (new; `--read {all,l1,l2,l3,l4}`, `--seed`,
`--json`; about five minutes a seed on the CPU, the L3 ascent most of it).
`evals/results/free_replays.json` (both seeds, every table above, the
per-fold parameters and the willingness-control cards). `READER-AUDIT.md`
rows 63–66, L1–L4's reads, reading-log entry 110.
