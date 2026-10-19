# Fine-tuning installs the tool format but not using the tool's answer

**Full result:** The format fine-tunes in fine; deferring to the tool does not

**Cost:** 2.4 min of scoring on the 2 cards first cited here (`nano20m_ft`, `nano20m_ft_replay`); it also reads 2 cards scored for an earlier finding (`nano20m`, `nano20m_pilot`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The fifth finding showed the format in pretraining works. It could not show that a fine-tune
*wouldn't* have worked, which is what DATA.md §4 actually claims, and §4's stated reason was
capacity: at 250M there is no room for a light fine-tune to install a format the base model has
never seen. `Config.init_from` now exists, so the control arm ran — twice.

Both arms start from `checkpoints/nano20m/ckpt.pt`, the TinyStories-only model that has never
seen a `<|call|>`, and both read **exactly 44,775,000 temporal tokens** — the pilot's figure to
the token, byte-identical corpora verified by sha256. Temporal exposure is held constant, so
the only variable is when the model read it.

| row | `nano20m_pilot`<br>pretrained | `nano20m_ft`<br>fine-tuned | `nano20m_ft_replay`<br>fine-tuned + 1:1 replay |
|---|---|---|---|
| `narrative` nats/byte | 0.4117 | 0.8182–0.8268 | **0.3929–0.3975** |
| `temporal` nats/byte | 0.1000 | 0.1052–0.1065 | 0.1132–0.1165 |
| `temporal.route` | 99.8% | 99.5–99.8% | 99.2–99.5% |
| `refusal.clarify` | 100.0% | 100.0% | 100.0% |
| `refusal.no_guess` | 100.0% | 100.0% | 100.0% |
| `temporal.copy` | **100.0%** (353/353) | 82.2–92.1% | 48.2–66.3% |

Ranges span the best-val and final checkpoints of each arm and a retrain from the same seed.
`nano20m_pilot` scored twice, identically.

**The capacity argument is refuted.** Five minutes of fine-tuning installs the `<|call|>`
envelope in a model that had never encountered one, and routing, clarification and no-guess
come out at the pretrained arm's level in every fine-tuned checkpoint scored. Whatever is
special about pretraining the format, it is not that a 25M model lacks room to absorb one late.

**One behaviour doesn't come along: using the tool's answer.** `temporal.copy` scores the turn
*after* the tool responds, and a date that is not the tool's fails even when it is correct. The
pretrained arm is 353 of 353. No fine-tuned checkpoint is, and every failure of every fine-tuned
checkpoint is `wrong_date` — never malformed, never empty, never a missing call.

**Every single one of those failures is the same failure.** Retaining all 400 generations
instead of the first eight:

| arm | copy failures | month and day correct | year written |
|---|---|---|---|
| `nano20m_pilot` | 0 / 353 | — | — |
| `nano20m_ft` | 28 | **28 of 28** | 2027 ×28 |
| `nano20m_ft_replay` | 183 | **183 of 183** | 2027 ×181, 2024 ×2 |
| `nano20m_ft_replay` (final) | 119 | **119 of 119** | 2027 ×119 |

```
want   <|call|>{"name": "recall_day", "arguments": {"date": "2028-04-11"}}
got    <|call|>{"name": "recall_day", "arguments": {"date": "2027-04-11"}}
```

Not one failure, in any arm, has a wrong month or a wrong day. The model copies those from the
tool exactly and replaces the **year** — and 2027 is `ANCHOR_END`, the last year the generator
ever emits. The eval anchors are 2028, held out by the decontamination design, so the year is
the one part of the tool's answer these models have never been asked to produce.

It isn't throwing the tool's answer away. It is copying the fields that varied during training
and clamping the field that didn't. Which is the failure VISION §5.2 is built to prevent —
answering from the weights instead of the lookup — appearing in precisely the field where the
weights have a narrow prior to answer from.

That also bounds what the row proves. `temporal.copy` separates these arms *because* the year
is out of distribution, so in the fine-tuned arms it is measuring whether copying generalises
past the training distribution rather than deference in the abstract. The pretrained arm handles
the same out-of-distribution year 353 times out of 353, so the ordering holds — but an
in-distribution variant would likely put all three arms at ceiling and show nothing.

**Replay makes the trade visible and cannot escape it.** The first arm lost half its prose —
0.3974 → 0.8268 nats/byte — and the obvious objection is that the recipe was bad: no replay, and
a temporal-only val that selects the most-forgotten checkpoint of the run. So the second arm
gets 1:1 narrative replay and a blended val, deliberately tuned in the control's favour rather
than to be representative. It works, completely: **0.3929 against the base model's 0.3974, zero
forgetting.** And `temporal.copy` falls from the 82–92% band to 48–66%, because replay is a
gradient that strengthens precisely the prior copy has to override.

So there is a dial with prose at one end and deference at the other, and the pretrained arm is
not a better point on it — it is off the curve, paying 3.6% of prose and scoring 100%.

**What this does not settle:**

- **The replay arm was still climbing.** 49.6% at its best-val checkpoint (iter 1,600), 66.3%
  at its last (iter 3,644). Replay halves the temporal gradient per step, so that arm may be
  exposure-limited rather than incapable. Finding out means giving a fine-tune *more* temporal
  data than the pretraining arm got, which breaks the equal-exposure property the comparison
  rests on — a different experiment, not a longer version of this one.
- **`temporal.copy` is unstable in the fine-tune arms.** Adjacent checkpoints of one run read
  90.4% and 82.2%; a retrain from the same seed moved it 1–2 points. The pretrained arm reads
  353/353 twice. The gap between "bouncing between 48% and 92%" and "at ceiling" is the result;
  the individual numbers are not.
- **Still 25M, still one tool, still in-distribution phrasings.** Every caveat on the fifth
  finding carries forward unchanged.

### The decontamination row had the opposite bug, and this run found it

The fifth finding fixed a status that cried wolf. The fine-tuned checkpoints exposed one that
cried nothing. Contamination was computed from `cfg.data_dir` — for a fine-tune, the corpus the
model saw *last* — so `nano20m_ft` was checked against a temporal-only corpus and its narrative
row came back `clean`, for a model whose weights came from a pretrain that was selected on the
narrative eval text. A false alarm gets ignored; a false all-clear gets believed, and it gets
quieter the more stages a checkpoint has.

`corn.evals` now walks the `init_from` chain and scores every corpus a checkpoint read, merging
to the worst status. A parent corpus that is not on disk reads `UNAVAILABLE`, never `clean`, so
the walk cannot go quiet by losing a file. `clean` is attributed to no single stage, because it
is the one status every stage earns jointly. 48 checks, up from 40 (86 today — the ninth and
tenth findings added a group each). `HARNESS_VERSION` stays 1 —
no scored quantity changed, and the pilot re-scored byte-identical across the fix.
