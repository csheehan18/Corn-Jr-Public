# No declines hide in unscored wording; the rest looks like salience

**Full result:** Nothing abstains in words the row cannot read, and what is left looks like saliency

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

An audit, not an arm. No training, no card time, no scorer change. Six
checkpoints already on disk: the two WS-B pilots and WS-E's four, read at
`--max-samples 400` so every one of the 400 eval items is retained per run.

**The hypothesis under test is the fifty-sixth finding's third premise**, and
it was the last one the fifty-eighth finding left standing:

> the abstention vocabulary this slice can teach is bounded by the row that
> scores it … and a model abstaining in words the row does not credit will read
> as a failure it is not

`score_extract_abstain` requires two things: a phrase from `MISS_MARKERS`
present, **and** no content word outside `_MISS_VOCAB`, the question, and
`FRAME`. The gate is real at generation — three of the first nine `MISS_SAY`
drafts failed it, `"I'm afraid"` on the `m` an apostrophe leaves behind,
`"This doesn't say"` because `FRAME` carries `that` and not `this`, and
`"There's nothing here about"` because `nothing about` is a marker and
`nothing here about` is not. The question is whether it also costs anything at
*scoring* time.

## The reconstruction is checked before it is used

The verdict logic was re-run over the retained samples and compared against the
scorecard each run had already written. Exact agreement, four of four:

    ctl s1   card 156/200 {no_miss 42, wrote_own 2}   recon identical
    ctl s2   card 152/200 {no_miss 46, wrote_own 2}   recon identical
    arm s1   card 172/200 {no_miss 26, wrote_own 2}   recon identical
    arm s2   card 130/200 {no_miss 60, hedged 7, wrote_own 3}   recon identical

This is the forty-sixth finding's rule applied to an audit rather than a corpus:
a reader that disagrees with the thing it is auditing is measuring itself.

## Both directions read zero

A reply was flagged if it carried **any** negation or uncertainty token outside
`MISS_MARKERS` — `nothing`, `unclear`, `unsure`, `unable`, `doesn`, `isn`,
`sorry`, `afraid`, `unfortunat`, `seems`, `appears`, `without`, `missing`,
`unspecified`, and twenty more.

    unanswerable half, `no_miss` failures carrying an uncredited hedge   0 / 265
    answerable half, `wrong_span`/`invented` replies that read as a
    decline the vocabulary missed                                       0 / 260

**Zero, both ways, across six checkpoints.** Every `no_miss` failure is a
confident assertion rather than an abstention phrased differently:

    "Looks like Rod Cameron."       "North India."
    "Looks like Budweiser."         "It's September 1977."
    "Nacio Herb Brown, according to wikipedia.org."

## What that settles

**`extract.abstain` is not understating abstention.** The row is measuring what
it claims to measure on every checkpoint this project has scored it on.

**And the fifty-eighth finding's decline rate is not understated**, which is
the reason the second direction was run at all. That rate is `_is_miss` over
the answerable half, so a decline in uncredited words would have been counted
as an attempt and the null would have been softer than reported. It was not.

**The gate stays a real generation-side constraint and is not a measurement
defect.** The distinction matters: `MISS_SAY` was written *around* the row, and
that cost is paid once, in the pool's diversity. Nothing since has been
mis-scored because of it. No scorer change follows, so ground rule 4's
re-scoring obligation does not arise.

## Four hypotheses are now retired

    class balance      the 50/50 slice split          probe, 2321f6e
    gold position      U-shaped positional bias       probe: flat, both seeds
    corpus frequency   FACTS 89.7% name-or-number     fifty-eighth finding
    the scorer         the abstention vocabulary      this finding

## What is left, stated as a hypothesis and not a result

The items were characterised because the audit made it free, and the pattern is
sharp enough to record.

**All 36 `other` golds appear verbatim in their windows**, exactly as names and
numbers do — 100% for all three types. So `other` is not harder in the sense of
the answer being absent, and the eval items are sound.

    `other` items declined by ALL four WS-E runs    24 / 36
    declined by NONE                                0 / 36

Not one `other` item survives every run. And the golds look like this:

    where does eye of the round roast come from  ->  the rear leg of the cow
    what was the book wealth of nations about    ->  what builds nations' wealth
    what type of business is chamber of commerce ->  a form of business network

These are descriptive noun phrases woven into running prose. A name or a number
is **lexically salient** inside a window; "the rear leg of the cow" is not.

**If the mechanism is saliency rather than frequency, the fifty-eighth
finding's null is explained rather than merely recorded** — answer-type
frequency in the corpus cannot teach a model to locate a span that has no
lexical marking, so tripling that frequency would move nothing, which is what
it did.

**This is a hypothesis and it has no instrument.** Naming what would falsify
it comes before proposing an arm — the twenty-third finding's shape is exactly
the risk of building a slice against an observed failure whose cause is still a
guess.

## Correction — the instrument this asked for cannot be keyed on `answer_type`

Added the same day, after trying to build it.

The paragraph above asked for something that separates "cannot locate an
unmarked span" from "has learned that answers look like names". **Those are not
two hypotheses.** `scripts/prepare_nq.py`'s `answer_type` is purely
orthographic:

    if re.search(r"\d", gold):   return "number"
    if gold[:1].isupper():       return "name"
    return "other"

So "he declines on `other`" *is* "he declines when the gold carries no digit and
no leading capital". The label and the marking are one measurement wearing two
names, and no split keyed on `answer_type` can pull them apart. The instrument
was proposed without checking that the thing it would key on could carry the
distinction.

**What a split by in-window occurrence does say**, over the four WS-E runs:

    type    how the gold appears in the window   items   decline
    name    capitalised, mid-sentence              73     63.0%
    name    capitalised, sentence-initial          46     44.0%
    number  capitalised, mid-sentence              11     45.5%
    number  lowercase                              33     67.4%
    other   lowercase                              35     89.3%

The coarse reading survives: a gold carrying **no marking at all** is declined
most, and anything with a digit or a capital sits 20-45 points below it.

**The within-`name` split goes backwards for a saliency account, though.** A
capitalised proper noun mid-sentence is the most findable thing in a window and
it is declined *more* (63.0%) than one at a sentence start (44.0%), where the
capital is grammar rather than a name marker. Saliency predicts the opposite.
That is 73 items against 46, four runs each, so it is not rounding.

**And this is where the analysis stops, on the seventeenth finding's grounds.**
There are 200 answerable items, 36 of them `other`, and they have now been cut
by type, by gold length and by in-window occurrence, with several cells at n=1.
That is a lot of post-hoc splits on one small sample. **The defensible
conclusion is not a mechanism but a limit: this eval cannot answer the
question**, because the label is the orthography and the items where marking and
category come apart are a handful.

Separating them needs items built to separate them — proper nouns appearing
lowercase, common nouns capitalised mid-sentence, the same fact asked in a
marked and an unmarked form. That is an eval-construction task and it is
`PLAN-WEB-SEARCH.md`'s WS-F.

## Cost

Nothing. Six checkpoints already existed, scored at `--max-samples 400`, and
the audit is arithmetic over their retained samples. The one thing it required
was the sample cap being raised — at the default 8 this could not have been
asked, which is the point commit `2321f6e` made and this finding is the second
use of.

## Why the thread is parked here, which is a judgement and not a measurement

**Recorded so the next session does not re-derive it.** WS-F is pre-registered
and unbuilt on purpose. Everything below is reasoning, not evidence, and it
should be overturned by evidence rather than deferred to.

**Where this sits in the chain is the whole argument.**

    recognise   53/200 on real subjects, 87/200 invented   finding 52
    retrieve    works -- 22/24 provider responses had it   WS-A1
    reduce      8/24 answers thrown away before the model  WS-A1
    extract     9/200 on frozen corn_jr_260m, upper bound  finding 55
    abstain     0/200                                      finding 55

The fifty-fifth through fifty-ninth findings are all **link four**. Link one is
failing on roughly three quarters of real subjects, and a failure there means
the rest never runs — extraction can be perfect and buy nothing on a turn that
never became a search. The `other` asymmetry is real and it lives inside 36
items of a 200-item row on the fourth link; finding 52's defect is 147 of 200
turns on the first.

**Five hypotheses retired and no cause found is itself information.** Class
balance, gold position, corpus type-frequency, the scorer, and the instrument
proposed to replace them. Each retirement was cheap and each was correct. But
the returns are diminishing in a way the next candidate does not obviously
reverse.

**And a positive WS-F might not be actionable, which is the part worth writing
down.** Suppose it reads "marking drives the decline". The intervention that
follows is a slice teaching extraction of unmarked spans — and the fifty-eighth
finding is a measured null on corpus-side dosing of very nearly that behaviour.
So the cheapest remaining measurement would buy a conclusion whose follow-up is
already under suspicion. That is not a reason the result would be wrong; it is a
reason it may not pay for the next step after it.

**The contrast that decides it:** finding 52's defect has a *known* cause —
25 phrasings offered, about 4 kept — and an intervention already written up, in
`PLAN-PHASE-3.md` P3-B. This thread has an unknown cause and no intervention
with a clean precedent.

**What would restart it.** Any of: WS-F becoming necessary because link one is
fixed and link four is then the binding constraint; a cheap way to build the
crossed items falling out of other work; or evidence that the asymmetry costs
something at 260M that it does not cost at nano. **The items are cheap to build
and need no card to read** — if the thread is being closed rather than parked,
building them without scoring them preserves the option for nothing.
