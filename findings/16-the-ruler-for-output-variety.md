# Sixteenth finding — the ruler for output variety, and the corpus change that did not move it

**Cost:** 3.5 min of scoring on the 1 card first cited here (`nano20m_narrative10`); it also reads 1 card scored for an earlier finding (`nano20m_balanced`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Two things landed together, and they have to be read together because the first was built to
judge the second.

**The tenth row.** Nine rows scored routing, copying, refusing, schema conformance and
nats/byte, and **a model that repeats itself forever aces every one of them** — perfectly, if
the thing it repeats is correct. VISION's goal is conversation that does not repeat itself, so
the project had spent fifteen findings unable to measure its own stated objective.
`variety.distinct3` closes that: 200 openings cut from the reserved eval tails, one sampled
continuation each at T=0.85, and distinct 3-grams **pooled across all 200** — the only view
that can see 200 different prompts answered with the same sentence, which looks perfectly
varied item by item. It is the fourth row added by `make_evals.py --add`, and the first whose
holdout needed no argument: its prompts are substrings of files `reserve_tail_for` already
keeps out of every corpus.

**The corpus change.** `nano20m_narrative10` is `nano20m_balanced` with narrative cut 46.80% →
10.00% and temporal 11.13% → 5.00%, both to the share §4 declares, with web absorbing all 42.9
points at 81.88%. Same 130,934,381 budget, same 5,237 iterations, same config, one pass over
every source. It is the largest single corpus change the project has made.

| row | `balanced` | **`narrative10`** |
|---|---|---|
| `web` nats/byte | 0.9106 | **0.8502** |
| `narrative` nats/byte | **0.3679** | 0.4667 |
| `temporal` nats/byte | **0.0944** | 0.0972 |
| `temporal.route` | **400/400** | 397/400 |
| `temporal.copy` | **353/353** | 352/353 |
| `tool.copy` | **120/120** | 111/120 |
| `tool.validity` | **171/181** | 169/181 |
| `tool.selection` | 150/200 | 116/200 |
| `schema.conform` | 172/200 | **174/200** |
| **`variety.distinct3`** | **89.3%** | 89.2% |
| distinct words | 19.7% | 19.5% |
| self-repetition | 3.7% | 3.8% |

**`web` nats/byte 0.9106 → 0.8502 is the largest language-modelling improvement in the
project**, and it is exactly what doubling a slice should buy. Everything else is the finding.

### The corpus diversity number does not predict the model variety number

§5.0 measured 61% of the corpus to be low-vocabulary text and named it as the reason he writes
like a children's book. Cutting the largest and thinnest of those slices by 4.7x moved
`variety.distinct3` by **0.1 point** and distinct words by **0.2**. The samples say the same
thing more bluntly than the number does — given a story opening, both checkpoints still write

    balanced      The moral of this story is that if you accept a child who we are
                  different, they will always be there. <|endoftext|> Once upon a
                  time, there was a little dog named Spot.
    narrative10   The moral of this story is that I will teach a child who can help
                  him, even if he has a plan. <|endoftext|> Once upon a time, there
                  was a little girl named Sue.

47% of the corpus or 10%, he opens with *Once upon a time*.

**The most likely explanation is a flaw in the row, and it is visible in its own by-source
split.** Narrative-prompted continuations went 88.6% → 87.0% while web-prompted ones went
91.1% → **92.4%**: each model got more varied on the register it has more of, less varied on
the other, and the two halves cancelled. Half the prompts are TinyStories openings, which
*invite* the exact output the row exists to detect. So what got measured is variety
**conditional on being steered into a register**, and the complaint behind §5.0 was about
which register he defaults to when nobody steers him. Those are two quantities and proposing
this row conflated them. The fix is cheap and is the next thing to build: an unprompted or
neutrally-prompted arm, scored the same way.

What the row does establish is that neither checkpoint is degenerate — 3.7% and 3.8%
within-continuation repetition — and that is a hole in the scorecard that is now closed
whatever else it does. It also caught something real while being built: with digits counted as
words, a checkpoint answering a prompt about sleep with `2.26.26.4669a / 2.28.2661.269a`
scored *better* than English, because number soup never repeats. **The row's first bug was one
that would have made a degenerating model look like its best result.**

### Cutting temporal cost `tool.copy`, and that is a share nobody has priced

`tool.copy` has read 120/120 on every corpus containing an unrepeated tool slice, and the tool
slice here is byte-identical to `balanced`'s — same file, same 815,442 tokens, one pass. It
still fell to **111/120**. The only other change touching the transcript format is temporal
going 11.13% → 5.00%, and `temporal.copy` and `tool.copy` ask the same question of two
different tools. So the reading is that **the temporal slice was buying deference on a tool it
does not contain**, and §4's 5% is the second half of this run's cut that needs its own arm to
separate from the first. `temporal.route` 400 → 397 and `temporal.copy` 353 → 352 are small
and in the same direction.

`tool.selection` 150 → 116 is 34 points, one point inside the ~35 the thirteenth finding
established as unreadable on that row, so it is not evidence either way.

**What this does not say.** One seed, one prompt set, and `variety.distinct3` has now produced
exactly two readings ever — its noise floor is uncharacterised, so "0.1 points" is a
difference smaller than anything yet shown to be measurable. The claim that survives is the
weaker and more useful one: **a 4.7x cut to the corpus's thinnest slice did not produce a
variety change large enough to see**, and the register did not change at all.
