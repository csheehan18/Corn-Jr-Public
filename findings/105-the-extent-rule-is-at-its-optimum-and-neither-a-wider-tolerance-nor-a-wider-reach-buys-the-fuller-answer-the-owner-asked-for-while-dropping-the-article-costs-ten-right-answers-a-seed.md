# Hundred-and-fifth finding — the extent rule is at its optimum: neither a wider tolerance nor a wider reach buys the fuller answer the owner asked for on either column, and dropping "the" before a proper noun costs ten right answers a seed

`scripts/probe_extent_sweep.py` and `harvest_popa_pairs.py --radius 8`,
2026-09-04. Replay off the pairs harvests plus three 19-second GPU passes to
widen the stored grid; no head trained. `evals/results/extent_sweep_s{1,2,3}.json`,
`extent_sweep_r8_s{1,2,3}.json`, `pairs_built_s{1,2,3}_r8_popa.json`.
`corn/reader.py` is untouched.

## 0. What the owner asked for, and what it turned out to be

Finding 104 §7 recorded four speech preferences from the owner's read of the
lenient credits: say the whole name; extend the answer with the passage's
qualifying phrase ("It occurred in Gilbert Inlet in Alaska", not "It's
Gilbert Inlet"); give both names on a `who ... and` question; and no "the"
before a bare proper noun ("It's Chernobyl", not "It's the Chernobyl"). This
was the first thing recommended after the ruler question closed, because it
looked like the cheapest change a user would notice: a template fix and a
constant.

It is not. The first three are the same thing — the reader's span is
shorter than the natural phrase — and that is the extent rule's business.
The fourth is not a template problem at all.

## 1. Dropping "the" is wrong on ten passages a seed

On the answerable passages where the reader speaks `It's the <Capital>...`
(23 / 20 / 22 a seed), the strict verdict before and after removing the
article:

                 spoken 'the <Cap>'   strict right   right after stripping
    seed 1              23                 14                  4
    seed 2              20                 15                  6
    seed 3              22                 14                  3

`the Soviet Union`, `The Maginot Line`, `the Intolerable Acts`, `the Battle of
Antietam`, `The Royalettes` need their article and the ruler knows it. `It's
the Chernobyl` — the case the owner heard — is not an article error: the head
picked `the Chernobyl` out of "The Chernobyl disaster" in the first sentence
when the answer, `Chernobyl Nuclear Power Plant`, is in the second. That is a
pick on the wrong occurrence with a clipped noun phrase, and no template rule
can tell it from `the Soviet Union`. **Closed as a template change.**

## 2. The tolerance is flat, on the record's grid

`corn.reader.extend` speaks the longest pair within `EXTENT_D` of the argmax
over `EXTENT_RADIUS = 3` candidate rows on either side; `EXTENT_D = 2.0` was
chosen on the strict ruler. Swept at the bar protocol, hybrid reduce, each `d`
at its own CV'd threshold, on two columns — strict, and a lenient proxy that
also credits a spoken span which *wraps* an accepted answer (the gold or any
span finding 104's labels accepted for that passage) while staying
`answer_sized`:

    d        s1 right / lenient*    s2 right / lenient*    s3 right / lenient*    mean words
    0.0          381 / 416              384 / 425              391 / 433           4.1
    1.0          387 / 422              387 / 429              399 / 441           4.2
    2.0  ships   389 / 424              388 / 430              400 / 442           4.2
    3.0          390 / 424              386 / 428              403 / 441           4.2
    4.0          389 / 423              386 / 428              406 / 444           4.3
    6.0          389 / 423              383 / 425              406 / 443           4.4
    8.0          387 / 420              391 / 431              404 / 439           4.5

The rule is worth +8 / +4 / +9 over no rule (`d = 0`), which is finding 86's
number again. Above `d = 2` the strict column moves by at most +6 on one seed
and −5 on another, the lenient proxy by at most +2, and the mean spoken
answer lengthens by a third of a word. **There is no fuller answer in the
grid the rule searches**: within three rows of the argmax, the head does not
score a longer span close enough to be taken.

## 3. A wider reach does not help either

The grid is the harvest's. `harvest_popa_pairs.py --radius 8` re-wrote the
three seed heads' grids to eight rows on either side (19 s each), and the
sweep re-run over them:

    radius 8, d     s1 right / lenient*    s2 right / lenient*    s3 right / lenient*    mean words
    2.0                 389 / 424              393 / 431              402 / 442           4.2
    3.0                 388 / 423              389 / 427              402 / 438           4.3
    4.0                 386 / 416              391 / 427              396 / 427           4.5
    6.0                 381 / 409              379 / 410              388 / 415           4.8
    8.0                 372 / 399              375 / 403              380 / 406           5.2

At the shipped tolerance the wider reach is +0 / +5 / +2 strict and +0 / +1 /
+0 on the proxy — noise. Every wider tolerance loses on **both** columns,
steadily, while the answers lengthen: by `d = 8` the reader is 17 / 13 / 20
right answers worse and the lenient proxy 25 / 28 / 36 worse. Widening past
the head's own near-ties does not find "in Gilbert Inlet in Alaska"; it finds
neighbouring clauses that fail `answer_sized` or, admitted wider, tip the vote
to another window.

## 4. Verdict

**The extent rule as shipped is at its optimum on both rulers.** The
preferences the owner voiced are real and are not reachable by the rule's two
constants or by the say template. What they need is either a span head that
ranks the natural phrase higher — training, where every arm on frozen states
has failed to move the pick — or a syntactic completion rule (finish the noun
phrase the argmax sits in) that finding 82 measured on the generative path
and found broke more than it fixed. Neither is cheap, and this finding's
purpose is to have spent forty minutes rather than a day learning that.

Not closed: the `who ... and` preference was not measured separately. It is a
subset of extension (the second name is a wider span) and the sweep says the
head does not offer it, but a count of how often a two-name gold has its
second name in the head's ten would size it, and was not run.

## 5. On disk

`scripts/probe_extent_sweep.py` (new): the rule replayed at any tolerance and
reach off a pairs harvest, read on the strict column and the wrapping proxy,
with the mean spoken length beside them. `probe_reader_rank.apply_extent`
takes a `radius`, default the shipped 3. `pairs_built_s{1,2,3}_r8_popa.json`
are the radius-8 grids and read identically to the radius-3 files at
radius 3.
