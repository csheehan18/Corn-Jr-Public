# 84. The fallback reduce buys thirty-five right answers at the same conditional accuracy, and the refusal still owns half of what is left

**`docs/PLAN-EXTRACTION-READER.md` §2.2's second reduce, specified and run
2026-09-02 on the null-headed reader's recorded Population A harvests. Replay
only: no GPU, no decode, no weight trained, `corn/extract.py` and `corn/gate.py`
untouched. `hybrid` passes its pre-registered PRIMARY on both seeds and ships;
the gain is attempt rate at held conditional accuracy and is reported as
that.**

The eighty-third finding ends with a supervised null head that reads 336 and
329 answerable right of 721 on Population A and beats both the ungated
generative null and the gated runtime. This file is what happened next: the
residue was partitioned, the partition named an arm, that arm ran and missed,
and the *other* arm — the one the partition ranked third — is the one that
worked.

## Where it starts: the null head against the arm it would replace

Carried here from the eighty-third finding because every number below is a
delta on it. `scripts/probe_reader_passages.py` reads (e) and (f):

    arm                                     joint   net vs null head s1        net vs s2
    gate, recorded `on` at t = -0.082         486   +64 (97/161, p = 8.1e-05)  +59 (96/155, p = 0.00024)
    gate, cross-validated by this protocol    509   +41 (97/138, p = 0.0089)   +36 (105/141, p = 0.025)
    null head s1 / s2                     550 / 545

**509 is the number the claim is made against** — the same two-fold CV the
reader's own threshold comes from, so neither arm gets a threshold advantage.
The win is on the reading half: right 336/329 against the gate's 282, while
correct silence falls 13 and 11.

**And the frozen eval is saturated for this comparison and cannot arbitrate
it.** Its cross-validated folds disagree by 0.85 and 0.84, its two head seeds
reach the same `joint` from opposite ends (`tight` 102 against 76, `abstain`
153 against 177), and every arm in this file lands inside that spread on it.
On 200 items with a threshold that unstable the frozen file is measuring where
the fold fell. **Population A, at 1,003 passages, is the ruler for anything
threshold-dependent from here, and the frozen file is a regression instrument
and not an arbiter.**

## The owner table, under one rule, stated

`scripts/probe_reader_residue.py` partitions the answerable residue
exclusively and in order — `NULL` (no gold-bearing window admitted),
`LOCATION` (one was admitted and the head pointed elsewhere on all of them),
`REDUCE` (one was admitted, the head pointed right on it, the passage is still
wrong or silent).

**The plurality depends on the gold-window predicate, so the predicate is
named and argued rather than assumed.** Three are available:

    (A)  corn.extract.span_of(answer, window)            THE RULE THIS FILE USES
         the whole gold as a contiguous run of the window's content words.
         Marks 1,211 of Population A's 2,794 answerable windows.
    (B)  every window                                    NOT A RULE
         `span_of(window, answer) is not None`. `span_of` returns a `bool` and
         `False is not None` is `True`, so this marks 2,794 of 2,794.
    (C)  corn.spangen.label_window(...) == "positive"    THE STRICTER RULE
         (A) and the gold aligns to a `bpe8k` boundary inside the candidate
         range, is at most `MAX_SPAN_TOKENS`, and round-trips — i.e. the pair
         enumeration has a slot for it. Marks 1,170 of (A)'s 1,211 (96.6%);
         707 of 721 passages keep one, against (A)'s 721 of 721. The 41
         windows (A) keeps and (C) drops are `no_verbatim` 20, `escaped` 10,
         `unaligned` 7, `too_long` 4.

**(A) is the rule because it is conservative against the conclusion drawn from
it.** (C) marks fewer windows gold-bearing, so under (C) strictly more
passages fall to `NULL` and fewer to `LOCATION` and `REDUCE`: **`NULL`'s
plurality can only grow**, and at most 14 passages can move on that account.
Reporting the permissive rule makes the plurality a lower bound on itself.

**(B) is a bug and it flips the plurality**, which is why the rule is written
down at all. Reproduced in this repo, under (B) seed 1 reads `NULL` 133 /
`LOCATION` 175 / `REDUCE` 77 against (A)'s 183 / 136 / 66 — the first is
`LOCATION`-plurality and would have named a different next arm. **A predicate
that never consults `span_of` cannot distinguish a refused answer-bearing
window from a refused empty one, so every admitted window counts as a missed
location.** The two tables are the same arithmetic over two predicates and
nothing else; the fold mapping and the scorer are identical.

## What the table says, at each arm's own cross-validated `t`

    answerable residue of 721, --reduce agree      seed 1              seed 2
    right                                         336                 329
    NULL      no gold-bearing window admitted     183   47.5%         178   45.4%
    LOCATION  admitted, pointed wrong             136   35.3%         143   36.5%
    REDUCE    pointed right, lost in reduce        66   17.1%          71   18.1%

    by type, right / NULL / LOCATION / REDUCE
    type    n         seed 1                     seed 2
    name    401   199 /  92 /  76 /  34      202 /  89 /  80 /  30
    number  195   106 /  40 /  29 /  20       99 /  37 /  28 /  31
    other   125    31 /  51 /  31 /  12       28 /  52 /  35 /  10

**`NULL` holds the plurality on both seeds**, every one of the 721 answerable
passages has a gold-bearing window (so retrieval costs none of this), and the
three owners have three different verdict shapes: `NULL` is four fifths
refusal, `LOCATION` four fifths a wrong answer from the right window, `REDUCE`
four fifths windows disagreeing into silence. **Names are 55.9% of `LOCATION`
on both seeds against 55.6% of the answerable half** — population-shaped, not
a names problem — while `other` is the type whose residue is most `NULL`
(54.3% and 53.6%).

**The pre-registered reading named the margin-feature null head, it ran, and
it missed.** Four arms (the specified `nn.LayerNorm(3)` and a per-feature
standardiser as its pre-registered control, two seeds each) took held-out
balanced accuracy from 0.7570/0.7381 to **0.8698/0.8494** and held-out AUC from
0.8352/0.8204 to **0.9383/0.9240** — every selection bar passed — and read
Population A answerable right **337, 322, 353, 340** against a bar of 371.
**A tenth of held-out presence accuracy bought between −7 and +17 passages**,
and the re-partition said why: `NULL`'s share went *up* on three of four arms
while `LOCATION` and `REDUCE` fell. The better detector converted
mislocations into refusals rather than into right answers. That arm's failing
branch is what sends this file to the reduce.

## Read (g): the second reduce, specified because the plan never was

§2.2 promises `reduce (unchanged first; score-aware second, §3.5)`. **There is
no §3.5 in `PLAN-EXTRACTION-READER.md`** — the pointer is dangling and the
second reduce had never been specified anywhere. It is specified in
`probe_reader_passages.py`'s docstring, as a flag on the probe, because §2.2's
other half is binding: `corn/extract.py::reduce` is not edited, and all three
modes call it rather than reimplementing it.

    agree   the runtime's own, and the default. Every admitted window speaks.
    top     only the highest-margin admitted window speaks; every other window
            declines. `reduce` still runs and takes its one-reply branch, so
            `grounded`, `_span_key`, `_canonical` and `det_repair` all apply.
    hybrid  `agree`, and only when it returns `None` with `reduce`'s own
            `"{n} windows disagree (...)"` reason, fall back to `top`.
            `"no window extracted an answer"` is deliberately not caught.

**Pre-registered before the run:** PRIMARY is answerable `right >= 371` with
unanswerable `silent >= 200`, plus a positive McNemar against the CV'd gate at
p < 0.05. **The choice rule, also written first: `hybrid` ships if it meets
PRIMARY on both seeds, because it keeps `reduce`'s agreement semantics; `top`
ships only if `hybrid` fails on a seed and `top` passes on both.**

    Population A at each arm's own CV'd t, both fold values quoted
    arm         right  wrong  silent    u-sil  u-wrong   joint   prec   acc|att  attempt   folds
    s1 agree      336    162     223      214       68     550   59.4     0.675    69.1%   -0.1534 / -0.4808
    s1 top        373    178     170      210       72     583   59.9     0.677    76.4%   -0.1584 / -0.4143
    s1 hybrid     371    188     162      207       75     578   58.5     0.664    77.5%   -0.1584 / -0.4031
    s2 agree      329    158     234      216       66     545   59.5     0.676    67.5%   -0.3255 / -0.9282
    s2 top        368    181     172      207       75     575   59.0     0.670    76.1%   -0.3113 / -0.8944
    s2 hybrid     371    186     164      207       75     578   58.7     0.666    77.3%   -0.2904 / -0.8944

    paired, McNemar
    s1 top     vs gate CV +74 (94/168, p = 5.7e-06)   vs agree +33 (19/52, p = 0.00011)
    s1 hybrid  vs gate CV +69 (95/164, p = 2.1e-05)   vs agree +28 (11/39, p = 9.0e-05)
    s2 top     vs gate CV +66 (92/158, p = 3.6e-05)   vs agree +30 (30/60, p = 0.0021)
    s2 hybrid  vs gate CV +69 (95/164, p = 2.1e-05)   vs agree +33 (17/50, p = 6.7e-05)

**`hybrid` meets PRIMARY on both seeds and `top` does not**, missing on seed 2
at 368 against 371. The choice rule fires as written and **`hybrid` is the arm
that ships**: it is both the semantically conservative option — it only acts
where `reduce`'s agreement rule has already failed to produce an answer — and
the one that replicates. It reads **371 right / 207 silent / joint 578 on both
seeds**, which is the tightest seed agreement anything in this workstream has
produced on this population.

**And the gain is attempt rate at held conditional accuracy, exactly as read
(g) pre-registered that it would be.** `acc | att` goes 0.675 and 0.676 to
**0.664 and 0.666** — down — while the attempt rate goes 69.1% and 67.5% to
**77.5% and 77.3%**. A score-aware reduce cannot improve conditional accuracy
on a window the head already read right; all it can do is stop a right reply
being abstained away, and that is what it did. **This is a `reduce` result and
not a reading result, and it is worth shipping anyway**: 35 and 42 more right
answers at the same conditional accuracy are 35 and 42 more right answers, and
`INDEPENDENT-READ.md` §5.1's rule is that the number is printed beside the one
that would show what it was, not that it is discarded.

**The residue re-partitions the way the mechanism predicts.** Under `hybrid`:

    answerable residue of 721, --reduce hybrid     seed 1              seed 2
    right                                         371                 371
    NULL                                          185   52.9%         184   52.6%
    LOCATION                                      134   38.3%         137   39.1%
    REDUCE                                         31    8.9%          29    8.3%

    LOCATION by type -- R2's target, and it is stable under the reduce
    type      agree s1 / s2      hybrid s1 / s2
    name        76 / 80            74 / 76      55.2% / 55.5% of LOCATION
    number      29 / 28            29 / 28
    other       31 / 35            31 / 33

**`REDUCE` more than halves, 66 and 71 to 31 and 29**, which is the owner the
lever was aimed at and the only one it should have moved. `LOCATION` is
essentially untouched (136/143 to 134/137) and `NULL` is untouched in absolute
count (183/178 to 185/184) while rising in share because the residue shrank.
**`NULL` is still the plurality and is now more than half of it.**

**R2's ceiling moves with the shipped reduce and should be requoted.** Holding
the null head and this reduce fixed, fixing all of `LOCATION` reads
371 + 134 = **505** and 371 + 137 = **508** of 721 — **70.0% and 70.5%**,
against 65.5% under `agree`. `configs/corn_jr_260m_v4_reader.py`'s bars are
rewritten against the `hybrid` column. It is still not 85%.

## Step 3: the selection slice does predict Population A's nulls, and the topical class is the easy one

The worry this read exists to test: `train_null_head.py` selects its epoch on
a held-out slice of the *training* file, and if that slice's nulls are not the
nulls Population A hands the runtime, the selection metric is about the
directory. `corn/extractgen.py`'s two kinds are carried through the harvest —
`absent_window` is a null drawn from an answerable passage, `absent_topical`
from a passage nobody could answer — and `--kind-report` splits the held-out
slice by them. No span-head forward, so no GPU.

    held out by article, at each head's own selection threshold
    seed  null kind        n null   n pos      AUC   bal.acc     TNR
      1   absent_window      2855    4964   0.8263    0.7452   0.7282
      1   absent_topical     2117    4964   0.8472    0.7730   0.7837
      2   absent_window      3067    5127   0.8053    0.7217   0.6828
      2   absent_topical     2173    5127   0.8417    0.7611   0.7616

**`absent_topical` reads 0.8472 and 0.8417, well above the 0.75 that would
have triggered a topical-only arm, so that arm was pre-registered as
conditional and is not run.** More than that, the result is the opposite of
the worry: **`absent_topical` is the *easier* class on both seeds**, by 0.021
and 0.036 of AUC and by 0.056 and 0.079 of true-negative rate at the selection
threshold. The head is better at refusing a window from a passage nobody could
answer than at refusing an empty window from a passage that has an answer
somewhere else.

**Which relocates the 68 and 66 unanswerable passages spoken wrong.** They are
not a class the head cannot recognise — it recognises this class best. They
are the tail of the class it recognises best, and the harder class is the one
Population A's *answerable* half is full of: a passage with four windows and
the answer in one of them offers three `absent_window` nulls, and those are
what `NULL`'s 185 and 184 are made of. **`absent_window` is where the next
null-side gain is, and the selection slice can see it.**

## Two artefacts found and fixed, both in a scratch replay rather than in the repo

An advisor's read-only replay reproduced this file's recorded reads exactly
and then diverged in two places. Both are reproduced in-repo here so the
difference is a measurement rather than an assertion, and neither touches any
number above.

**The predicate.** `span_of(window, answer) is not None` marks every window
gold-bearing; see (B). It moves the seed-1 owner table from 183/136/66 to
133/175/77 and flips the plurality.

**The fold mapping, and it is Step 4's answer in one line.** The replay
counted 6 passages on seed 1 and 7 on seed 2 scored `right` with **zero**
admitted windows at their fold's threshold, which should be impossible: with
no window admitted every reply is a decline, `reduce` returns `None`, and the
verdict is `silent`. **It is an artefact of the replay's fold mapping and not
a path in the probe.** `probe_reader_passages.cross_validate` returns its
verdicts alongside `ordered`, the fold-*reordered* rows; the replay then ran
`fold_split` on `ordered` rather than on the file-order rows, which re-alternates
by class in the new order and hands **502 of 1,003 passages the other fold's
threshold**. Under the correct mapping the count is **0 on both seeds**; under
the replay's it is exactly 6 and 7. `probe_reader_residue.thresholds_by_id`
splits the original rows and always did.

## What ships and what does not

  * **`--reduce hybrid` is the arm the choice rule selected.** It lives behind
    a flag on the probe. Wiring it into `corn/extract.py::reduce` is a runtime
    change that R3 owns and this file does not make.
  * **Nothing about the reader changed.** No weight, no scorer, no frozen row,
    no threshold constant. Every number here is replay over harvests that were
    already on disk.
  * **The margin-feature null head does not ship.** It is a better presence
    detector that reads no more passages, and its cards stay on disk as the
    measurement of that.
  * **The topical-only null arm is not run**, its trigger having not fired.

## Limits

One trunk, two head seeds, one span-head arm (`built`), fp32. Population A is
NQ dev's own paragraphs at 64/32; `hybrid`'s +35 and +42 are measured there
and nowhere else, and the frozen and phrase files are saturated for this
comparison by the argument at the top of this file rather than being evidence
against it. The three reduces share one candidate-threshold list and one CV
protocol but choose their own thresholds, so the three rows of a seed are not
the same policy read three ways; the fold values are printed for that reason.
`hybrid`'s fallback fires only on `reduce`'s disagreement reason, so a passage
whose windows produced nothing grounded is untouched by it and stays `NULL`.
The `acc | att` fall of 0.011 and 0.010 is inside nothing in particular — it
is small, it is in the direction the pre-registration named, and it is quoted
rather than tested. R2's requoted ceiling of 505/508 assumes `LOCATION` is
entirely fixable, which is an upper bound and not a forecast.
