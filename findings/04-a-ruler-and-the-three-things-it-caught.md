# Fourth finding — a ruler, and the three things it caught

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Every remaining Phase 1 step is a comparison across corpora: the BPE measurement, the pilot
mix, the tool-data experiment. A training run's `val` figure cannot serve any of them, because
it is a tail of whatever corpus was just tokenized and moves whenever the corpus moves — which
is why the 0.4265 above cannot honestly be put next to `nano`'s 0.6104. So `evals/` is frozen,
hashed, decontaminated and in version control, and `corn/evals.py` scores a checkpoint against
it. Two things it measures that a loss curve cannot: nats per **byte** on fixed text, which
survives the §2 tokenizer swap, and behaviour, which is generated and scored by exact match.

`nano20m`, which has seen TinyStories and nothing else, is the floor:

| row | | what it asks |
|---|---|---|
| `narrative` nats/byte | **0.3974** | over 1.1MB of held-out prose |
| `temporal` nats/byte | **3.8911** | over 1.0MB of held-out transcripts |
| `temporal.route` | 0.0% of 400 | call `resolve_date` with the user's words |
| `temporal.copy` | 0.0% of 353 | use the tool's date, never a computed one |
| `refusal.clarify` | 0.0% of 47 | relay the tool's question verbatim |
| `refusal.no_guess` | — of 0 | emit no date when the tool had none |

The zeros are the point. This checkpoint has never seen a `<|call|>`, and asked to produce one
it emits a newline and carries on writing children's stories — `empty 400` in the failure
buckets. 3.89 nats/byte against a uniform model's 5.55 says the same thing from the other
direction: it has general byte-level competence and no idea what this format is. The harness
exists to register the change when the pilot mix arrives, and it can only do that if it reads
zero now.

**1. Context is worth 9%, so the ruler has to fix it.** The harness guarantees every scored
token 128 tokens of context. Same model, same text, varying only that:

| warmup | 0 | 1 | 8 | 32 | 128 | 256 |
|---|---|---|---|---|---|---|
| nats/byte | 0.4367 | 0.4330 | 0.4242 | 0.4131 | **0.3974** | 0.3904 |

A 9% spread with nothing about the model changing — larger than most of the effects Phase 1
is trying to measure. `train.py`'s val samples random 512-windows and scores from position 0,
which is the 0.4367 end, and explains most of the gap to the 0.4265 it reported. So `WARMUP`
is a harness constant rather than a config field: a run cannot quietly change it and stay
comparable, and `HARNESS_VERSION` is stamped into every result for when it does change.

**2. A metric measuring the absence of a bad answer needs a denominator of attempts.**
`refusal.no_guess` asks whether he invented a date when the tool had none. Ungated, `nano20m`
scored **100%** on it — by continuing to write about a girl and her mother, which contains no
dates. It is now scored only over responses that are in the transcript's format at all, so it
reads `--` over 0 items instead. Every other row asks whether the model did the right thing
and a wrong answer fails on the merits; this is the one row a model can pass by never
engaging, and it was the one row that looked good.

**3. The eval text is inside that checkpoint's val split.** Taking the held-out prose from the
tail of the source file keeps it out of the training stream — `prepare` and `prepare_mix` both
consume from the head — but `prepare` holds out the last 0.5% as validation, so the tail lands
squarely in it. 16 of 16 probes are in `nano20m`'s `val.bin` and none in its `train.bin`. It
was never trained on, which is what matters, but it *was* the text the checkpoint was selected
on, so 0.3974 is mildly flattered. The harness scans both files and says which.

~~Two rows print `--` and will until there is data for them~~ — `tool.validity` and
`tool.selection` needed tool-call transcripts against Corn-Jr's own schemas, which is DATA.md
§6. They were in the table anyway, because a scorecard that silently omits what it cannot
measure is how a gap becomes invisible — and they stayed `--` across six checkpoints before
the tenth finding filled them. That is the argument for declaring a row early working exactly
as intended: the gap was visible on every scorecard in the meantime.

`scripts/check_evals.py` guards all of it in 40 checks across eight groups, and the group
worth having is that the
scorers are fed wrong answers and have to reject them — an off-by-one-day `recall_day`, a
reworded clarifying question, a `resolve_date` whose argument is the answer instead of the
question. A harness that passes everything measures nothing, and unlike a training bug it
would never announce itself.
