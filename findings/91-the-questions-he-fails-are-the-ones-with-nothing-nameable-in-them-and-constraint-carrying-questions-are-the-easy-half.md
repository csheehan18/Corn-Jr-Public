# The hard questions are those with nothing nameable in them

**Full result:** The first input-side cut of the residue reverses the sign of its own hypothesis: constraint-carrying questions are the easy half, the residue lives in the questions with nothing nameable in them, and the only total failure is thirteen passages wide

`scripts/probe_question_shape.py`, 2026-09-03. **Replay only** — no GPU, no
decode, no weight read — over `evals/results/nullpr_s{1,2}_popa.json`, the
shipped pair-rows verifier, at each fold's own cross-validated threshold under
`hybrid`. Baselines 367 right / 354 residue and 368 / 353.

**Ninety findings and every split of the residue has been a split by what the
reader did** — `probe_reader_residue`'s three owners, `probe_reader_species`'s
six species, `probe_reader_position`'s four verdicts. All of them are
taxonomies of the failure. The only input-side cut anywhere in the record is
`answer_type`, three buckets wide. This is the missing cut, and **it refutes
the hypothesis it was built to test, with the sign reversed on both seeds.**

## Where the hypothesis came from, and why it was wrong

The species probe's own examples looked like one mechanism wearing five
species' clothes:

    who won the world cup in cricket 2017     gold Pakistan    said England
    what percentage of earth's surface is water  gold ~78%     said 2.5%
    who sang the theme song from russia with love  gold Matt Monro
                                                   said Monty Norman
    who is stephanie's mom on the bold and the beautiful
                                              gold Taylor Hayes  said Steffy
    who has more super bowl wins nfc or afc   gold NFC/NFL
                                              said American Football League

`AGGREGATION`, `RIVAL`, `RIVAL`, `REFUSED_RIGHT`, `REFUSED_WRONG` — and in
every one the question carries a discriminating constraint and the reader
matched on topic instead. 2.5% is the fresh-water figure; Monty Norman
composed it and Matt Monro sang it; Steffy is the daughter.

**They were selection bias.** They are memorable *because* the mechanism is
legible in them, not because the mechanism is common. Measured over all 721,
the sign goes the other way.

## 1. Constraint-carrying questions are the half he gets right

Six labels, each a property of the **question string alone** — nothing
consults the passage, the gold or the reader, so no label can be a restatement
of the outcome it is cross-tabbed against. Closed hand-written lexicons and two
regexes, no new dependency.

    label          accuracy s1 / s2     delta vs base    residue lift   Fisher
    ROLE            69.5% / 63.2%      +18.6 / +12.1     0.46 / 0.61    1e-04
    RELATION        62.3% / 61.0%      +11.4 / +10.0     0.63 / 0.67     0.04
    ORDINAL         60.2% / 61.2%       +9.3 / +10.2     0.69 / 0.66     0.05
    TEMPORAL        53.5% / 51.2%       +2.6 /  +0.1     0.90 / 1.00     0.76
    MEASURE         42.5% / 45.0%       -8.4 /  -6.0     1.40 / 1.27     0.33
    NONE            45.5% / 47.0%       -5.4 /  -4.0     1.24 / 1.17    0.001
    base                                50.9% / 51.0%

**`ROLE` is the single easiest class measured** — nineteen and twelve points
above base, the residue lift 0.46 and 0.61, Fisher p = 0.0001 and 0.011. A
question that names a role, a relation or a rank is a question whose answer is
pinned down, and being pinned down helps. `TEMPORAL` — the cricket example's
own label, the one the hypothesis leant on hardest — is **flat**: +2.6 and
+0.1, p = 0.76 and 1.0.

`MEASURE` is the only labelled class below base and it does not clear
significance on either seed.

## 2. The residue is in the questions with nothing nameable in them

`NONE` — no label at all — is 404 of 721 questions and **62.1% and 60.6% of
the residue**, four to five points below base, p = 0.0013 and 0.016. It is not
a describable subset an arm could be aimed at. It is the general case.

**Read (c) makes the same point from the other side.** The label × species
cross-tab has no cell where a label concentrates: `NONE` supplies 91 of 136
`REFUSED_WRONG`, 74 of 113 `REFUSED_RIGHT`, 22 of 42 `RIVAL` and 17 of 31
`AGGREGATION` — its own share of the residue, in every species. The labels do
not cut across the species because they do not cut anything.

**The obvious confound is ruled out.** The residue's questions are not longer:
9.20 content words against the right half's 9.04 on seed 1, and 9.22 against
9.02 on seed 2. Accuracy is flat across length — 51.9% at 8–9 content words,
47.0% at 10–12, 51.5% at 13+ — and the residue carries *fewer* labels per
question (0.43 against 0.58), which is read (a) restated.

## 3. One class reads zero, and it is thirteen passages

    ALTERNATIVE  "is it A or B", the gold one of the named alternatives
                 0 of 7 on both seeds, Fisher p = 0.0067 / 0.0065
    BETWEEN      `between` / `than` / `difference`
                 0 of 6 on both seeds, Fisher p = 0.014 / 0.013

These were one label until its thirteen passages were read. `between` in NQ is
overwhelmingly *prepositional* — "the skin between your nostrils", "the
alliance between great britain russia and france" — and asks for a thing
defined by two others, which is not "solid liquid or gas". **Both halves read
zero separately**, and pooling them would have hidden that the zero is two
zeroes.

**It is not a scoring artefact.** Read (d2): all 13 have a gold-bearing
window, only 2 are `ECHO_BLOCKED`, so **11 are winnable and 0 are won**. And
**10 of 13 are silent rather than wrong** — he refuses them rather than
guessing.

    who has more super bowl wins nfc or afc       gold NFC/NFL   -> AFL, wrong
    where does sound travel fastest solid liquid or gas   gold solids -> silent
    is aluminium a ferrous or non ferrous metal   gold non-ferrous -> silent
    was star wars a book or a movie first         gold film        -> silent
    is greenland part of europe or north america  gold North America -> silent
                                                  (`ECHO_BLOCKED`)

**The shape is worth naming even at n = 13.** When the question supplies the
candidate set, the gold is a word the question already used — so the correct
answer sits at best a morphological step from a restatement (`solids` for
`solid`, `non-ferrous` for `non ferrous`, `film` for `movie`), which is the
`ECHO_BLOCKED` condition one inflection out. Two of the thirteen are formally
echo-blocked and the rest are its neighbours.

## What this cannot say

**Read (d) is inconclusive and nothing is claimed from it.** Splitting
accuracy by `extractgen._has_distractor` on the gold-bearing window was meant
to test whether a constraint matters only when there is something to
discriminate between. After restricting to golds the predicate can decide, the
"without" cells hold between 1 and 41 passages and the gaps swing from −40 to
+55 with no consistent sign.

**And the first version of that read was wrong in a way worth recording.**
`_has_distractor` returns `False` outright for a lower-case gold — its third
branch — so "without a distractor" was pooling common-noun answers with
genuine no-competitor windows, two populations with different accuracies, and
reported a large positive gap that was the gold's own type. The restriction
and the excluded count are now printed.

**The labels are lexicons and they are not exhaustive.** `ROLE` omits
`plays`/`played`, which is a role verb in "who plays john smith" and a common
verb everywhere else and cannot be separated without a tagger. A richer label
set could find a class these six miss. What the six do establish is that the
*obvious* constraint classes go the wrong way.

**n = 13 is n = 13.** §3 is two seeds of one head over thirteen passages. It
is the cleanest zero in the record and it is not an arm's worth of passages.

**One population, two seeds, one trunk.** Everything is Population A at the
CV'd threshold under `hybrid`.

## What follows

**Do not build the corpus arm this probe was meant to justify.** The plan was:
if constraint-carrying questions are over-represented in the residue, generate
extraction windows where the question's constraint selects among same-type
candidates and the wrong one is positionally favoured — the sixty-sixth
finding's second repair, generalised. **The classes such an arm would teach are
already the classes he is best at.** `ROLE` at +18.6 is the one it would have
aimed at hardest.

**This is evidence for the trunk levers and it is the first evidence from the
input side.** A residue that concentrates in questions with no nameable
property, distributes across every species in proportion, and does not vary
with question length is what a representation limit looks like from outside.
`PLAN-EXTRACTION-READER.md` §7 is not contradicted by anything here.

**`ALTERNATIVE` is a guard question, not an arm.** Thirteen passages will not
move a number, but 10 of 13 silent suggests the verifier has a systematic
problem with windows that carry both named alternatives, and the `grounded`
interaction is one inflection away from the 22 `ECHO_BLOCKED` passages whose
exemption has been an open owner decision since the eighty-fifth finding.
Those two should be decided together.

**Left unexplained:** `MEASURE` is six to eight points below base on both
seeds and never reaches significance at n = 40. It is the only labelled class
pointing the hypothesis's way, and whether it is real needs a population this
one cannot supply.
