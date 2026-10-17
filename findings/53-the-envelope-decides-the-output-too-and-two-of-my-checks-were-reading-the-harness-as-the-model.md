# Fifty-third finding — the envelope decides the output too, and two of my checks were reading the harness as the model

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn/extract.py` wired into a turn, run 2026-08-24 against `corn_jr_260m` on
the 3080 with a stubbed search backend, no network and nothing trained. The
work was plumbing — `World.reader`, the chunk-and-reduce in the `web_search`
executor, `fell_back` carrying the reduce reason. It was expected to yield
nothing and it produced two instrument defects, both of which had already
consumed published numbers.

**Both are the same mistake in two places, and the fifty-second finding's
neighbour explains why.** The previous session established that this model is
sensitive at the *marker* level on the way in: the same window as bare prose,
as a JSON payload, and as a whole `<|call|>` → payload → `<|say|>` transcript
gives conversational drift, an invented number and a correct extraction. What
this finding adds is that the same is true on the way **out** — his reply is
drawn from the corpus's own sentence templates, and a check written from taste
rather than from the corpus refuses it.

## The frame vocabulary was written from three of four templates

`corn/toolgen.py`'s `SAY_ANSWER` is the complete set of sentences the corpus
ever wraps a search answer in:

    {a}.        It's {a}.        {a}, according to {s}.        Looks like {a}.

`grounded`'s `FRAME` — the closed set of words a reply may add that came from
neither the window nor the question — covered the first three. It had `it`,
`s`, `according`, `to`. It did not have `looks` or `like`.

Over a six-sentence iron abstract, three windows:

| window | reply | verdict |
|---|---|---|
| 1 | `Iron is a chemical element … a soft, silvery-white metal …` | refused, correctly — `soft`, `silvery`, `white` are not in the passage |
| 2 | `Looks like 1538 degrees Celsius.` | **refused, wrongly** — on `looks` and `like` |
| 3 | `Looks like 1538 degrees Celsius.` | **refused, wrongly** — same |

Two of three windows produced the correct answer and the acceptance test called
both inventions. With the two words added, the same run reads
`2 of 3 windows agree on '1538 degrees celsius'` and the user hears the melting
point instead of the atomic number, in 465 ms.

**The fix that generalises is not the two words.** `scripts/check_extract.py`
now asserts `FRAME ⊇ SAY_ANSWER`'s framing words, so a fifth template added to
the corpus fails a guard rather than silently costing an extraction rate. The
class of defect — a runtime rule about what the model may say, written without
consulting the corpus that taught it — has now cost four checks in two
sessions.

## Four of five windows never stop, and that was being reported as "nothing found"

The previous session had already found this and separated it: an unfinished
reply is withheld rather than allowed to vote, "otherwise the token budget
decides the answer". **That separation lived in its probe script and not in
`corn/extract.py`**, and the three files it committed did not carry it. Wiring
the chain into a turn therefore reproduced the bug one commit after it was
fixed.

`BatchedReader` runs the full budget for every row deliberately. A reply that
reached no marker used all 32 tokens and gave the *opening of a long answer*,
not a short one — and handed to `grounded` its cut-off last word reads as an
invention. Live, on the first three passages:

    the melting point of iron   1 of 3 windows never finished
    the capital of Laos         1 of 1 never finished
    the population of Laos      1 of 1 never finished

All three had been reported as `no window extracted an answer`. Four of five
windows across the run, against 5 of 12 in the offline probe. The reason
strings now carry the count on both arms, so the untrained failure mode is a
live number on every turn rather than something someone has to go and measure.

**It is not "wrong", it is "unfinished", and the distinction sets the corpus
target.** `grounded` already enforces the safety half — nothing ungrounded has
ever reached the reduce, including the distractor case. What is missing is
*stop when the answer is out*, which is not a property a runtime can fake, and
which `MAX_NEW` is deliberately not raised to hide: the corpus's
post-observation say is at most 79 characters over 1,629,766 of them, so 32
tokens is already generous against the distribution being asked for.

## What this retires

**`0/6` and `1/12` are lower bounds with a known bias, not measurements.** Both
published extraction baselines were taken through a `FRAME` that refused the
reply form this model prefers; the windowed one also predates the truncation
separation reaching the runtime. Marked as bounds in `docs/PLAN-WEB-SEARCH.md`
and `docs/EXTERNAL-RESEARCH.md`. Nothing here says the untrained rate is good —
it says it has not been measured, and that both numbers were partly measuring
the instrument.

## What this cannot say

**Three passages, one checkpoint, no seeds.** The 2-of-3 result is one abstract
of one subject shape, and `the melting point of …` is the *worst* shape in the
fifty-second finding's grid at 1/25 on real subjects. A better rate on an
easier shape would not be a surprise and would not be a measurement either.

**Nothing about the chain.** Of five phrasings of the same question, one routed
to `web_search` and four declined. The extraction path runs on the turns that
reach it, and most turns do not — link 1 is unchanged and is still where the
loss is.

**Nothing about abstention.** Every fallback here was an unfinished worker.
Whether he can report a genuine absence is untested, and it is the one output
`grounded` cannot verify.

## What follows

The transferable form of the envelope claim is a **method**, not an
inspection. "Check that the markers are on-distribution" is only actionable for
someone who owns the corpus, which is what `EXTERNAL-RESEARCH.md` §8's papers
do not:

> Hold the content fixed, vary the structural envelope, and see whether the
> answer changes. If it does, the number was never a capability measurement.

That runs against any black-box model, it is what the call-line probe actually
did, and no entry in §8 reports having tried it before concluding that
utilization is a capability problem. Given §8's SmolLM2-360M at 100% and
Qwen2.5-7B at 85.4% under an *oracle* passage, it is worth someone running.

Two conventions in `docs/HACKING.md` §4 came out of this and are the durable
part: a number in a commit message says whether it was committed or probe-only,
and a measurement made through an unguarded check measures the check.
