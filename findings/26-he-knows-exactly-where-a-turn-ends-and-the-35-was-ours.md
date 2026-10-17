# Twenty-sixth finding — he knows exactly where a turn ends, and the 35 was ours

The twenty-fifth finding said `conv20` had the vocabulary of conversation and not its shape, on a
median turn of 35 words against a corpus that breaks at 13. Three mechanisms could produce that,
and none needed a training run to separate: **representation** (a newline between SODA turns is
the same byte as a newline inside a web paragraph, so nothing marks it as a boundary),
**drift** (it leaves dialogue register while generating), or **sampling** (`T=0.85` and
`top_k=50` sharpen away a break that is not the argmax). The representation one was flagged as
the worst case, because no share would fix it and the fix would want an eighth marker the frozen
`bpe8k` cannot take.

All three are wrong, and so was the 35.

### Reading real dialogue, the model is almost perfectly calibrated

`scripts/turn_probe.py --calibration` reads held-out text and asks, at every position, what
probability the model puts on the next token carrying a line break.

| checkpoint | text | true rate | P at boundary | elsewhere | ratio | **predicted rate** | sharpened |
|---|---|---|---|---|---|---|---|
| `conv20` | conversational | 0.0479 | **0.7847** | 0.0111 | **70x** | **0.0482** | 0.0520 |
| `conv20` | narrative | 0.0287 | 0.7620 | 0.0073 | 105x | 0.0290 | 0.0298 |
| `conv20` | web | 0.0222 | 0.4588 | 0.0114 | 40x | 0.0214 | 0.0289 |
| `balanced` | conversational | 0.0479 | 0.5490 | 0.0168 | 33x | 0.0423 | 0.0532 |

**`conv20` puts 78% on a line break exactly where one occurs, and predicts the boundary rate to
within 0.6%** — 0.0482 against a true 0.0479. So a shared newline token does not prevent learning
a turn boundary: context disambiguates it, and the separation between boundary and non-boundary
positions is 70x. The representation hypothesis is dead, and with it the worry that this would
need a marker the tokenizer cannot afford.

The slice is what bought the precision. `balanced` reads 0.55 at boundaries and under-predicts
the rate by 12% (0.0423 against 0.0479); `conv20` reads 0.78 and is calibrated. That is the
conversational slice teaching turn structure, measured directly rather than inferred from output.

**Sampling was the opposite of the worry too.** The same distributions under the row's own
`T=0.85` and `top_k=50` give a *higher* newline probability, not a lower one — 0.0520 against
0.0482. Sharpening promotes the break rather than suppressing it, because at a true boundary the
break is already near the top of the distribution.

### Generating, it breaks about when it should

`--drift` generates from real dialogue prompts and records the same probability step by step.
`conv20` holds P(break) at 0.044–0.069 after the opening — an implied gap of 14.5 to 23 tokens
against real dialogue's 20.9 — and its **first break lands at a median of 15 tokens**, with
0 of 60 prompts failing to break within 90. There is no drift to find.

### So where did 35 come from

From the eval row, pooled across both prompt sources. Story prompts produce unbroken prose that
reaches the 40-word cap; dialogue prompts produce short turns. A median over 100 of each lands at
the seam and describes neither.

| checkpoint | median turn, dialogue | median turn, story |
|---|---|---|
| `conv20` | **14** | 40 *(cap)* |
| `narrative10` | 14 | 40 |
| `web_bpe` | 16 | 40 |
| `balanced` | 17 | 40 |
| conversational anchor | **13** | — |

**`conv20` breaks at 14 words against a corpus that breaks at 13.** Every checkpoint is already
close. There was never a shape gap, the twenty-fifth finding's conclusion is withdrawn, and
`evaluate_register` now reports turn length per source with the pooled figure marked as
meaningless in the scorecard rather than printed as a result.

### What this is really a finding about

Three mechanisms were proposed, ranked by how expensive they would be to fix, and the ranking
was the reason to check the cheap one first. All three were wrong because **the number they were
proposed to explain was an artefact of the measurement**, and the only reason that surfaced is
that an independent probe disagreed with the row and both could be checked against each other.

The uncomfortable part is that this row reports its *score* by source precisely because pooling
two prompt types hides the answer — and then pooled them in its own diagnostic, one field away.
The eighteenth finding is the same shape: `tool_copy_answers: 6` sat in the manifest for eight
days while every movement read off that row was a whole number of facts. A number that is not
broken down is not yet a measurement, and this project has now paid for that twice.
