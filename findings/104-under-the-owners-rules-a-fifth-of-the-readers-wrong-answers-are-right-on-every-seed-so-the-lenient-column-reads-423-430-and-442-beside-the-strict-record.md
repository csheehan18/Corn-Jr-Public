# Hundred-and-fourth finding — under the owner's three rules about a fifth of the reader's wrong answers are right on every seed, so the lenient column reads 423, 430 and 442 beside the strict 389, 388 and 400, and a quarter of every refused-wrong gold is not the unique correct span

`scripts/lenient_column.py`, 2026-09-04. No head was trained and no reader was
run: the three shipped harvests (`nullpr_s{1,2,3}_popa.json`) read at the bar
protocol, extent on, hybrid reduce, each seed at its own CV'd threshold, and
every answerable passage the strict ruler did not score `right` re-judged by
hand against the passage. 332 + 333 + 321 residue passages, 986 judgements,
674 of them distinct (a passage the reader answered identically on two seeds
carries one judgement). `evals/results/lenient_s{1,2,3}_labels.json`,
`lenient_s{1,2,3}.jsonl`, and the `lenient_s{1,2,3}_emit.md` files the
judgements were read against. `corn/reader.py` is untouched.

**Read by the owner the same day (§7): eighteen of twenty credits stand, two
rules were sharpened, and the column is 421 / 428 / 439.** §§1–4 are the
numbers as first labelled and are left as written.

## 0. Why a second column, and what it is not

The reader is scored by `score_extract_tight` against one NQ annotator's span.
Finding 95 §6 audited 100 refused-wrong passages and found the gold was not the
unique correct span on 23; the owner's spot check of 2026-09-04
(`docs/SPOT-CHECK-REFUSED-WRONG.md`) confirmed that as a floor and set three
rules for what counts as correct: **recency** (a present-tense question wants
the passage's current answer), **a year is enough** (a `when` question is
answered by the year, and a gold that adds a season, a range or a leading word
is an extent case), and **a different quantity is wrong**. The audit's lever
L6 named the build: a lenient column beside the strict one, "credits, not
passages".

**The strict column stays the record.** Nothing closed reopens on this
column, no threshold was tuned on it, and no arm is selected on it. It exists
to say how much of the residue is the ruler and how much is the reader.

Two credits are kept apart because they answer different questions:

    spoken_ok   the reader spoke and what it said is acceptable under the
                rules -- the reader being right where the ruler said wrong;
                the only credit that moves `right`
    pick_ok     the reader refused, and the span head's pick on the best gold
                window is acceptable -- the gold was not unique; moves nothing

## 1. The three seeds

                     right  wrong  silent  attempt  acc|att      credits
    s1 strict          389    188     144    0.800    0.674
    s1 lenient         423    154     144    0.800    0.733    34 (18.1% of wrong)
    s2 strict          388    172     161    0.777    0.693
    s2 lenient         430    130     161    0.777    0.768    42 (24.4%)
    s3 strict          400    178     143    0.802    0.692
    s3 lenient         442    136     143    0.802    0.765    42 (23.6%)

**+34 / +42 / +42 right at an unchanged attempt rate** — the attempt rate
cannot move, because a credit turns a wrong answer into a right one and
touches no refusal. `acc | att` rises 5.9, 7.5 and 7.3 points. In the owner's
terms: on roughly one wrong answer in five the reader was right and the ruler
was not.

By rule, the 118 spoken credits split 58 `extent`, 50 `equivalent`, 9 `year`,
1 `quantity`. The `extent` half is the reader saying `London` for `London,
United Kingdom`, `Chernobyl` for `Chernobyl Nuclear Power Plant`, `Edward IV`
for `Edward IV of England`, `7.6%` for `7.6% Per Annum`, `Nickelback` for
`Canadian rock band Nickelback`: answers no reader would call wrong. The
`equivalent` half is the reader naming another member of a set the question
asked for (`Auburn` for a two-team championship game, `Jacques Cousteau` for a
two-man invention, `2015` for one of five championship years, `wool` for "two
fibres made of proteins", `Archaea` for "what types of cells"). The one
`quantity` credit is the owner's own ruling: `216` countries have Scouts, the
gold `169` counts organisations, and the reader said 216.

By species:

    spoken_ok / n        s1         s2         s3
    RIVAL              8 / 63    10 / 59     8 / 49
    CLIPPED           13 / 18    16 / 23    18 / 25
    AGGREGATION        5 / 64     7 / 50     7 / 64
    UNGROUNDED         1 / 16     0 / 11     0 / 13
    REFUSED_*          7 / 171    9 / 190    9 / 170

**`CLIPPED` is three quarters ruler.** 47 of its 66 passages across the three
seeds are the reader saying the answer without the annotator's padding, which
is what the strict `EXTENT` category was always suspected of being. `RIVAL`
is one sixth ruler (26 of 171), and those are the `EQUIVALENT` set-member
cases finding 95 named. `AGGREGATION` is one ninth (19 of 178) — the vote
outvoting a pick that was in fact also right. `UNGROUNDED` is the reader's
own, one in forty.

## 2. The refusals: the gold is not unique on a quarter of `REFUSED_WRONG`

On the passages the reader refused, the span head's pick on the best gold
window was acceptable on

    pick_ok / refusals in residue    s1   93 / 144     s2   100 / 161     s3   90 / 143

    of which REFUSED_RIGHT (right by construction on the strict ruler's own
    tight test)                       59 / 78          65 / 80            59 / 71
    REFUSED_WRONG                     28 / 93          26 / 110           21 / 99

**28 / 93, 26 / 110 and 21 / 99 — 24.8% pooled — of the passages in the
strict species `REFUSED_WRONG` hold a pick that is right under the owner's
rules.** That is finding 95's 23% read again on the whole species on three
seeds, and it holds. (The species also holds passages where the reader spoke
wrongly from another window; among the 69 / 82 / 66 that actually refused,
the pick was acceptable on 41% / 32% / 32%.) Two of those are golds the passage itself
contradicts: the Charles Bridge "was built as a bow bridge" and the gold
`Stone` is lifted from the Regensburg bridge it was modelled on; the theory of
possibilism is "by Strabo" and the gold is Sahlins, who used it.

## 3. What the column says about the target

The owner's 85% is 613 of 721. Under the strict ruler the reader is 224, 225
and 213 short. Under the lenient ruler it is 190, 183 and 171 short. **The
ruler accounts for about one sixth of the distance to the target and the
reader for five sixths.** The 93% ceiling of finding 96 (672 / 670, the gold
in the head's ten and admitted alone) is a strict-ruler number and would read
higher on this column; the lenient ceiling was not computed.

So the residue is real. What changes is its composition: the strict species
table overstates `CLIPPED` by three quarters and `RIVAL` by a sixth, and an
arm that "fixes" those is partly fixing the ruler. The window-features
verifier of finding 101 moved `RIVAL` +11 and `REFUSED_WRONG` −9 on seed 1;
on this column some of that trade is between two classes that are both
partly right, which is one more reason its +4 / +3 / −2 on `right` was noise.

## 4. Who labelled, and the second twenty

The labeller is this session, a model, as finding 95's auditor was. The owner
ruled on five passages and those rulings were applied verbatim (169 → `WRONG`
and 216 credited; the FBI Director's superior is the DNI and `the President`
is not credited; `1952` and `1979` credited on the two `when` golds the owner
ruled on). Thirty-six credits are marked `borderline` in their notes (9 / 12 /
15 by seed) and lean toward credit; the largest class is a reader naming one
member of a pair (`James Watson` for Watson and Crick, `phencyclidine` for a
mixture of two). **If the owner reverses every borderline credit the seeds
still read 414 / 418 / 427**, +25 / +30 / +27 over strict.

**`docs/SPOT-CHECK-LENIENT.md`** holds twenty credited spoken answers drawn
at random across the three seeds, with question, gold, passage, what the
reader said, the rule applied and a line for the owner. Disagreement on more
than four of twenty would send the column back for a stricter pass.

## 5. On disk

`scripts/lenient_column.py`: `--emit` writes one seed's residue with the
reader's spoken answer or the head's pick; `--labels` consumes per-passage
judgements and writes `lenient_s{seed}.jsonl`; `--report` prints strict and
lenient side by side. Labels are reused across seeds only where passage,
spoken answer and pick are identical (134 and 137 of seeds 2 and 3's residue),
so a reader that said something different on another seed was judged again.

## 6. Limits

One labeller, and a model; the owner's twenty is the check. The rules were
applied to Population A only; the training labels are untouched and the head
that ships was trained against the strict gold. The `accept` lists are what
the labeller saw in the passage and are not exhaustive. Truncated picks
(`Cozon`, `uln`, `The Buckwheat`) were not credited and a clipped surname
(`Elizabeth Dean`) was not either, while a clipped particle
(`Gabrielle-Suzanne Barbot`) was; that line is a judgement. `AGGREGATION` and
`REFUSED_*` picks were judged on the best gold window's pick only, not on
every admitted window.

## 7. The owner's read, the same day: eighteen of twenty stand, and the column is 421 / 428 / 439

The owner read the twenty in `docs/SPOT-CHECK-LENIENT.md` and agreed on
eighteen. Two were reversed, and each reversal is a rule made sharper:

  * **A date inside the right year is not the year.** `October 12, 1979`
    for "when did the NBA create the 3 point line" was credited under the
    year rule because the owner had ruled `1979` the answer; the owner's
    reading is that the answer *is* 1979 and a different date in it is not.
    Applied to every seed carrying that credit: four reversals (two passages,
    seeds 1, 2 and 3).
  * **A different author's clipped name is wrong.** `Jeanne-Marie Leprince`
    for "who is Beauty and the Beast written by" was credited as the author
    of the retold version; the owner: "it has to be Gabrielle-Suzanne Barbot
    de Villeneuve". One reversal (seed 3). The clipped *right* name
    (`Gabrielle-Suzanne Barbot`, seeds 1 and 2) the owner accepted with
    "extend the name to cover it fully", so those credits stand.

With the seven reversals applied and the column re-read:

                     right  wrong  silent  attempt  acc|att   credits
    s1 lenient         421    156     144    0.800    0.730    32 (17.0% of wrong)
    s2 lenient         428    132     161    0.777    0.764    40 (23.3%)
    s3 lenient         439    139     143    0.802    0.760    39 (21.9%)

The 111 credits split 58 `extent`, 49 `equivalent`, 3 `year`, 1 `quantity`.
Against 613 the lenient reader is 192 / 185 / 174 short; §3's sixth stands.
Thirty-five credits remain marked borderline (9 / 12 / 14); reversing every
one would read 412 / 416 / 425.

**Four preferences fell out of the eighteen agreements and are recorded as
targets for the reader's extent and speech, not as correctness rules**,
because the owner marked each answer right and then said what he would rather
hear:

    say the whole name           "extend the name to cover it fully"
    extend the answer            "It occurred in Gilbert Inlet in Alaska", not
                                 "It's Gilbert Inlet" (four of the twenty)
    both names on "who ... and"  "ideally we get both" for Watson and Crick
    no "the" before a proper     "It's Chernobyl"; "adding the word 'the' is
    noun                         weird to say"

The first two point at the extent rule and the reader's span width; the
fourth at `SAY`'s template and the natural-speech goal. None changes a
verdict in this column.
