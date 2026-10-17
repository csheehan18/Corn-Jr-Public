# Twenty-fifth finding — the slice buys conversation and does not buy register

`register.conv` is the sixth addable row and the first that asks the question §4 buys the
conversational slice *for*. Nothing in `evals/` measured register: the nats/byte rows say a
corpus was learned, and `variety.distinct3` says a model does not repeat itself, which a fluent
storybook also does not.

**No threshold anywhere, which is the point after the twenty-third finding.** Five coordinates
are measured identically on a continuation and on windows of the frozen eval texts, and a reply
is scored by which of three measured registers it is nearest to. The scale is the range the
registers themselves occupy on each feature, so nothing here is a constant anybody chose.

| feature | conversational | narrative | web |
|---|---|---|---|
| words to first line break | **13.3** | 28.4 | 20.2 |
| second person | **0.0500** | 0.0089 | 0.0073 |
| first person | **0.0955** | 0.0104 | 0.0072 |
| past-tense reporting verbs | 0.0111 | **0.0532** | 0.0065 |
| ends in a question mark | **0.225** | 0.000 | 0.080 |

### The floor first, then the reading

Four seeds on `mix_balanced`, the same replicates the nineteenth finding used:

| checkpoint | `register.conv` | from dialogue | from story |
|---|---|---|---|
| `balanced` 1337 | 12.0% | 23.0% | 1.0% |
| `balanced` 1338 | 12.0% | 24.0% | 0.0% |
| `balanced` 1339 | 12.5% | 23.0% | 2.0% |
| `balanced` 1340 | 13.0% | 25.0% | 1.0% |
| **spread** | **1.0 pt** | **2.0 pts** | **2.0 pts** |

A 1.0-point floor makes this the tightest generation-scored row in the project — `tool.copy`
moves 15.0 points on the seed alone and `variety.distinct3` moves 1.85. Against it:

| checkpoint | conversational share | `register.conv` | from dialogue | from story |
|---|---|---|---|---|
| **`conv20`** | **20%** | **38.0%** | **76.0%** | **0.0%** |
| `web_bpe` | 0% | 19.0% | 37.0% | 1.0% |
| `narrative10` | 0% | 14.1% | 28.3% | 0.0% |
| `notools` | 0% | 13.5% | 27.0% | 0.0% |
| `balanced` | 0% | 12.0% | 23.0% | 1.0% |

**Prompted with dialogue, the slice moves the row 23% → 76% — 53 points against a floor of
2.0.** That is the largest behavioural effect of any share change the project has measured,
on a row with the tightest floor it has. The conversational slice does what it was bought to do,
and `variety.distinct3` could not see it: the same comparison moves that row 0.73 points against
a floor of 1.85.

### And prompted with a story, nothing moves at all

**Every checkpoint scores 0–2% on story openings, including the one with 20% dialogue.** §5.0's
complaint is that he answers a story opening in storybook register whether narrative is 47% of
the corpus or 10%; with a fifth of the budget replaced by conversation, he still does. The slice
bought conversation and did not buy a register the prompt did not already choose.

**Whether that is a failure is a real question and this row does not settle it.** A base language
model continuing a story opening as a story is doing its job — prompt-following is not a defect,
and 0% on that half may be correct behaviour rather than a regression. What it establishes
either way is that the conversational slice does not change register when the prompt has already
chosen one, which is worth knowing before anyone prices the share on register grounds. It is
also why the two halves are reported separately: pooled, this row would read 38% and hide that
one half tripled while the other did not move.

### The fourth nats/byte row, which came free and moved further than any before it

`evals/text_conversational.txt` had to exist for the anchors, and a held-out text is a
language-modelling row whether or not you wanted one:

| row | `balanced` | `conv20` | Δ |
|---|---|---|---|
| **`lm conversational`** | 0.8749 | **0.5073** | **−0.3676** |
| `lm narrative` | 0.3679 | 0.3949 | +0.0271 |
| `lm web` | 0.9106 | 0.9051 | −0.0055 |
| `lm temporal` | 0.0944 | 0.0962 | +0.0018 |

**−0.3676 is six times the largest nats/byte move the project had recorded** — the sixteenth
finding's `lm web` 0.9106 → 0.8502 at −0.0604, from cutting narrative by 37 points. A 42%
relative improvement, against a floor of 0.0038 on the noisiest language row. The slice is
emphatically learned, which is the least surprising result here and the one that makes the rest
legible: whatever `register.conv` is failing to see on story prompts, it is not that the model
never read the corpus.

### ~~He sounds conversational and is not shaped like conversation~~ — withdrawn

**This section reported a median turn of 35 words against a conversational corpus that breaks at
13, and concluded the slice bought the vocabulary of conversation and not its shape. The 35 was
a pooled statistic and the conclusion was wrong** — see the twenty-sixth finding, which was
built to explain it and disproved it instead.

`median_turn` was pooled across both prompt sources. The story half produces unbroken prose that
reaches the 40-word cap, so a median over 100 of those and 100 dialogue replies lands at the seam
between two distributions and describes neither. Per source, which is how this row reports its
*score* and should always have reported this:

| checkpoint | dialogue score | **median turn, dialogue** | median turn, story |
|---|---|---|---|
| `conv20` | 76.0% | **14** | 40 *(cap)* |
| `narrative10` | 28.3% | **14** | 40 |
| `web_bpe` | 37.0% | **16** | 40 |
| `balanced` | 23.0% | **17** | 40 |
| conversational anchor | — | **13** | — |

**Every checkpoint already produces conversational-length turns on dialogue prompts.** `conv20`
breaks at 14 words against a corpus that breaks at 13. There was never a shape problem, and the
23% → 76% the slice buys is carried by the person and question coordinates because turn length
was near-correct on both sides of the comparison all along.

The 80-word re-score in the commit before this one read the same pooled number and inherited the
same error; its one durable result is that the conversational anchor is 13.5 at an 80-word window,
so the reference side was never censored.

What the mistake cost is worth naming: this row reports its score by source *precisely because*
pooling two prompt types hides the answer, and then its own diagnostic pooled them.

### What it does not say

Neither half is unprompted, so §11's standing request — what register does he fall into when
nothing has chosen one — is still unanswered, and this row inherits that gap rather than closing
it. The anchors are three registers because those are the three held-out texts that exist;
temporal has one too and was left out because a transcript slice is a format rather than a
register. And the row is nearest-anchor, not quality: a model emitting fluent nonsense in short
second-person turns would score well here and badly on every nats/byte row, which is the same
caution `variety.distinct3` carries one row over.
