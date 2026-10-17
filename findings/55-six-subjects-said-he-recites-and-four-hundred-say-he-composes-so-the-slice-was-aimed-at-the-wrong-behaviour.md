# Fifty-fifth finding — six subjects said he recites, four hundred say he composes, and the slice was aimed at the wrong behaviour

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Three eval rows — `extract.span`, `extract.abstain`, `extract.brevity` — cut
from Natural Questions dev, added by `make_evals.py --add`, and scored once
against the frozen `corn_jr_260m` on 2026-08-24. No training. This is a
before-number, taken because `docs/PLAN-WEB-SEARCH.md`'s execution order puts
the rows ahead of the slice, and it is the first time the extraction question
has been asked at a denominator above six.

**27 of 27 pre-existing rows reproduced identically**, which is what `--add` is
for and is now a checked fact rather than an argument.

    extract.span       9/200    4.5%   -- an upper bound, see below
    extract.abstain    0/200    0.0%
    extract.brevity  133/400   33.2%

## The premise it was built on, and the sentence that withdraws it

`PLAN-WEB-SEARCH.md` specified the extraction slice from a six-subject probe,
and this is the sentence the whole design followed from:

> The two he got right, he got right by copying the whole paragraph. That is the
> substrate and it is why this is tractable: he can attend to a long observation
> and reproduce it faithfully. The task is to teach him to copy *less*.

Over 400 real NQ windows that is backwards. Of the 400 replies:

    18   are copies of the window          (10 on span, 8 on abstain)
    69   never became a sentence at all -- they reopened the JSON payload
    220  are window-length prose he wrote himself

Median copied fraction across the long replies is **0.09**. The cleanest single
item is the tell: the window says "The winner was 19-year-old Jourdan Miller
from Bend, Oregon", and he answered "The winner was **21**-year-old Jourdan
Miller from Bend, Oregon". That is not copying with an error. It is composing
over a topic, and the number is the part he supplied.

So the task is not to narrow a span he takes. **It is to get him to take one at
all**, and that is a different slice: the first lesson is *a window arriving in
the `answer` field means a short sentence drawn from it*, which the answerable
and unanswerable classes teach jointly rather than separately. A slice built on
the old premise would have spent its budget on span-narrowing — a refinement of
a behaviour that is not there.

**Why six subjects said otherwise.** They were hand-picked, and two of the six
"successes" were successes *because* the whole paragraph came back — which reads
as faithful recitation at n=6 and as a 4.5% tail at n=400. The fifty-third
finding retired those same six items as a bound rather than a measurement, for a
different reason; this retires the reading built on top of them.

## The bucket that hid it for one baseline

The first version of the scorer called every over-long reply `recited`, because
the plan said recitation was the failure to beat. It is a **length** test, and
naming it for the expected answer made 192 confabulations look like copying. The
first baseline therefore reported 137 `recited` on span and 153 on abstain and
would have been read as confirming the premise it actually refutes.

Split into `recited` (at least half the reply lifted from the window) and
`wrote_own` (everything else), the same replies read:

| bucket | span | abstain |
|---|---|---|
| `wrote_own` | 99 | 121 |
| `continued_payload` | 38 | 31 |
| `invented` | 38 | — |
| `recited` | 10 | 8 |
| `wrong_span` | 6 | — |
| `no_miss` | — | 38 |
| `hedged_answer` | — | 2 |

This is the twenty-third finding's shape on a bucket instead of a bar: a
measurement named for what it was expected to show. The guard now asserts that
window-length prose which is *not* the window reads `wrote_own`, so the naming
cannot drift back.

## `continued_payload` — 69 of 400, and the only falsifiable prediction here

`worker_prompt` ends with the say marker, so the model stands immediately after
a JSON object, and the cheapest continuation is more JSON:

    1979, "source": "wikipedia.org", "query": "when did frank sinatra ...

Scored as malformed rather than as content, because a reply that never became a
sentence is not an extraction whatever strings are in it — and one of the twelve
items that passed `extract.span` on the first pass passed by echoing a payload
that happened to carry the gold.

It is the cheapest thing on the board to falsify. Nothing in the corpus has ever
put a paragraph inside an `<|obs|>`, so the slice will contain this shape for
the first time. **If 69/400 does not fall, the envelope was not the
explanation** — and that is worth more than the number, because it is the one
place this arm can be wrong in a way that shows.

## `extract.span` is an upper bound, and three tightenings were rejected

The row asks whether the gold appears in the reply. That is necessary and not
sufficient: reading the twelve items the first pass scored, roughly a third are
incidental — an enumeration (`Answers: 1971, 1972, 1973, ...` brute-forces any
date gold), a repetition (`Wales, England, and Wales.`), or the gold arriving
inside a reply that answers something else.

Three fixes were tested against those twelve and all three were rejected:

    grounded()          drops 8 of 12, and three of the drops are correct
                        extractions -- "the current rate of interest on ppf
                        is 7.6% Per Annum", "located in the fascia
                        surrounding skeletal muscle". That is the
                        fifty-third finding's defect rebuilt on purpose
    copied fraction     does not separate them: worst junk 0.93, a correct
                        answer 0.27
    a length bound      fitted to twelve observations is the twenty-third
                        finding's bar, shaped by the sample it was read off

So the row ships permissive and says so in its docstring. The quantity to watch
is **movement**: a slice taking it from 9 to 90 is not in doubt over three lucky
items. What is excluded is `continued_payload`, which is a structural
disqualification rather than a fitted one.

## The abstention half reads zero, and it is a real absence

Two of two hundred replies carry a miss marker at all, so `0/200` is not a
scoring artefact — there is almost nothing for a scorer to be strict about. It
is also the row with **no runtime floor**: WS-C can check an extraction because
the span is in the window or it is not, and it cannot check an abstention
without performing the extraction it would be verifying. A model that abstains
everywhere scores 100% here and 0% on `extract.span`, which is why the two are
never pooled and why they carry different denominators.

`PLAN-DONT-KNOW.md` predicts this should be the tractable kind. Every "don't
know" that arrives *through an observation* works — `temporal.copy` 353/353
under paraphrase, `tool.copy` 120/120, `tool.copy_wide` 300/300 — and every one
requiring the weights to suppress a call fails. The evidence for "the answer is
not here" is the window, and the window is in the context. So this is the most
favourable regime the project has had for its largest standing failure, and it
starts at zero.

## What this cannot say

**Nothing about a trained model.** Nothing in the corpus has ever put a
paragraph inside an `<|obs|>`, so every number here measures a behaviour that
was never taught. External research entry 8 is the anchor and it points the same
way: it tested *instruction-tuned* models only, ran no fine-tuning experiments,
and named RAFT as what "significantly improves utilization". "Small models
cannot do this out of the box" is not "small models cannot be taught this."

**Nothing about the 260M's ceiling.** One checkpoint, one seed, greedy, fp32.

**Nothing about whether the split between the two classes matters.** They fail
identically here, which is the observation the balanced class mix was
pre-registered from — but identical failure before training is weak evidence
about behaviour after it.

**The oracle condition is generous and the row is still 4.5%.** Every answerable
item's window contains the gold whole, by construction. The runtime reads
several windows and votes; this reads the one that has the answer in it.

## What follows

The share is pre-registered at **5%, one point, two seeds against a two-seed
control** — the thirty-fifth finding's "first point, chosen to make a null
readable", with the thirty-seventh finding's `chat2.txt` at a 25th of a pass as
the counterexample. The twenty-first finding argues a sweep buys nothing, since
copy discipline is flat from 0.61% to 15%; this finding is the reason to doubt
that transfers, because the behaviour turns out not to be copy.

The regression watch is `tool.copy` 120/120 and `tool.copy_wide` 300/300.
Teaching a model to *select* from an observation operates on the machinery that
makes it *copy* one, and every capability in this project has been paid for
somewhere — the conversational slice took `refusal.say` from 172/162 to 30 of
270.

**And the method is the transferable half, as it was in the fifty-third.** The
premise that survived four weeks did so because it was never asked at a
denominator that could refute it. Six items chosen by hand, a bucket named for
the expected answer, and a plan written on top of both. The row that replaced
them cost one afternoon and no GPU beyond ten minutes.
