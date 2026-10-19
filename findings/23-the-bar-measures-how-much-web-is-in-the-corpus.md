# The vocabulary test really measures how much web text is mixed in

**Full result:** The bar measures how much web is in the corpus

§5.0 measured five slices in isolation, rejected narrative at 6,863 distinct words, and has
gated the conversational search ever since. **What it never measured is the blend** — and no
slice is what gets trained on. `scripts/vocab.py --bins` samples a built token stream at 800
even intervals, decodes it, and measures the vocabulary the model actually sees.

| corpus | narrative | blend distinct | blend top-100 | `variety.distinct3` | `lm web` |
|---|---|---|---|---|---|
| `mix_narrative10` | 10% | **45,369** | 42.6% | 89.2% | 0.8502 |
| `mix_narr10_temp11` | 10% | 43,555 | 44.9% | 87.9% | 0.8548 |
| `mix_struct` | ~46% | 32,591 | 48.0% | 88.5% | 0.9174 |
| `mix_notools` | 46.8% | 31,745 | 50.6% | 87.7% | 0.9079 |
| `mix_balanced` | 46.8% | 31,544 | 50.6% | 89.3% | 0.9106 |
| `mix_tools_1pass` | ~48% | 29,886 | 51.9% | 89.1% | 0.9098 |
| `mix_web_bpe` | ~48% | 29,856 | 51.9% | 90.0% | 0.9104 |
| `mix_tools15` | ~41% | **27,364** | 51.2% | 87.7% | 0.9212 |

**The per-slice reading badly overstates the damage.** `mix_balanced` is 46.80% TinyStories and
11.13% temporal — the two slices §5.0 names as the worst offenders, at 6,863 and 182 distinct
words — and it blends to **31,544 at 50.6%**, which is within a rounding error of the bar rather
than far beneath it. And `mix_narrative10` blends to **45,369, higher than FineWeb-Edu's own
42,755**, because registers contribute vocabulary that does not overlap: a blend can carry more
distinct types than any of its parts.

### The bar does not predict the thing it exists to protect

Blend vocabulary spans **66%** across these eight corpora, 27,364 to 45,369. Over the same eight,
`variety.distinct3` spans **2.33 points** — against its own measured seed floor of **1.85**.

| relationship | r |
|---|---|
| blend distinct vs `variety.distinct3` | **−0.045** |
| blend top-100 vs `variety.distinct3` | +0.129 |
| blend distinct vs output `distinct1` | −0.403 |
| **blend distinct vs `lm web`** | **−0.976** |

A 66% swing in the quantity the bar measures produces essentially nothing in the quantity the
bar was built to defend, and what little there is runs the wrong way. What blend vocabulary
*does* predict, at −0.976, is `lm web` — because it is very nearly a restatement of how much web
is in the corpus, and the nats/byte rows measure that directly, at a floor of 0.0038, without
the intermediate step.

So **§5.0's bar should not gate the conversational slice.** It is a proxy for web share dressed
as a quality threshold, and the project already has the direct measurement.

### The caveat is real and cuts at the other ruler

Eight corpora, one model size, one budget. More importantly the *outcome* variable is barely
resolvable: `variety.distinct3` spans 2.33 points across every corpus the project has built and
1.85 of that is seed noise. A null correlation against a near-unresolvable outcome is weak
evidence of no effect — it is equally consistent with the output ruler being too blunt to see
one. §11 already carries that complaint about `variety.distinct3`, including that half its
prompts are TinyStories openings, so **this finding implicates both rulers** and the honest
statement is "no relationship detectable at this resolution", not "no relationship".

That does not rescue the bar. A screen that cannot be shown to predict anything downstream, and
which correlates at −0.976 with a row already measured better, should not be what blocks the
largest unsourced share in the corpus.

### What it unblocks

**SODA comes back.** Right register — everyday two-person dialogue, median turn 14, p90 31 —
CC BY 4.0, freely fetchable, already measured, and rejected on this bar alone. At 15,942
distinct it would pull the blend down, and nothing here says that costs anything a nats/byte row
would not show. The test that was always the right one is an arm rather than a screen: SODA at
20%, read against `lm narrative`, `lm web` and `variety.distinct3`, priced the way every other
share in this project has been.

### A bug in the tool, caught by two corpora agreeing too well

The first version of `--bins` filled a word budget in file order and stopped when it was full,
which read the first **58%** of the stream. Sources are written in spec order, so that silently
dropped whichever slices were declared last. It reported `mix_narrative10` and
`mix_narr10_temp11` as **identical to the digit** — two corpora that differ only in the temporal
slice, which sits in the tail. Taking a fixed quota from every window fixes it. A second pass
found that trimming words by line discarded whole windows on long-line sources, biasing the
blend against web, the widest-vocabulary slice; words are now trimmed by token fragment and only
turn lengths by line.
