# Twenty-fourth finding — the slice the bar rejected costs prose and nothing else

**Cost:** 4.5 min of scoring on the 1 card first cited here (`nano20m_conv20`); it also reads 1 card scored for an earlier finding (`nano20m_narrative10`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`nano20m_conv20` is `mix_balanced` with SODA at §4's declared **20%**, taken out of narrative
(46.80% → 26.80%), everything else held at its exact token count. One variable in the sense that
matters — adding a slice must move a second share, and this moves the one §4 wants moved anyway.
781.6 MB of dialogue available against the ~99 MB the share needs, so it is read **once**, with
no `repeat` anywhere. 1,066s at 154k tok/s.

The arm was set up as a falsifiable test between two rulers, written down before it ran.

| row | `balanced` | `conv20` | Δ | floor | |
|---|---|---|---|---|---|
| **`variety.distinct3`** | 89.34% | 88.61% | **−0.73** | **1.85** | noise |
| **`lm narrative`** | 0.3679 | **0.3949** | **+0.0271** | 0.0012 | **real, 23x** |
| `lm web` | 0.9106 | 0.9051 | −0.0055 | 0.0038 | real, 1.4x |
| `lm temporal` | 0.0944 | 0.0962 | +0.0018 | 0.0009 | real, 2x |
| `schema.conform` | 172/200 | **178** | **+6** | 2 | **real** |
| `tool.copy` | 120/120 | **78** | **−42** | 18 | real |
| `tool.copy_wide` | 277/300 | 269 | −8 | 29 | noise |
| `tool.selection` | 150/200 | 155 | +5 | 8 | noise |
| `temporal.copy` | 353/353 | 353 | +0 | 0 | held |
| `refusal.clarify`, `refusal.no_guess` | 47/47 | 47 | +0 | 0 | held |

**§5.0's bar predicted `variety.distinct3` would fall.** A fifth of the corpus is now the most
lexically repetitive slice the project has measured — 15,942 distinct words at 64.2% top-100,
worse than TinyStories on the second number. The row moved **0.73 points against a floor of
1.85**. The prediction fails, and the twenty-third finding's prediction — that whatever this
costs would show up on the nats/byte rows, where it can be read properly — is what happened.

### The corpus got better on the ruler that rejected the slice

| | blend distinct | top-100 | median turn | p90 |
|---|---|---|---|---|
| `mix_balanced` | 31,544 | 50.6% | 11 | 52 |
| `mix_conv20` | **33,122** | **49.0%** | 10 | 47 |

Adding the slice **improved the blend on both axes**, +1,578 distinct and −1.6 points. The bar
compared SODA against an absolute threshold and never against the slice it would displace:
64.2% top-100 is worse than TinyStories' 63.1%, but 15,942 distinct words is **more than twice**
TinyStories' 6,863, and swapping twenty points of one for the other improves the corpus. That is
the defect in the screen, stated as plainly as it can be — *a threshold cannot see a
substitution*.

Some of the gain is the narrative cut rather than the dialogue. Interpolating `mix_balanced` to
`mix_narrative10`, giving those twenty points to web instead would land near ~39,000, so SODA is
better than the incumbent it replaces and worse than web. That is the trade §4 intends, since
the 20% is bought for register.

### What it actually cost, and the confound

`lm narrative` **+0.0271 at 23x its floor** is the whole price, and it is confounded with the
narrative cut by construction. The bracket says the confound is not the whole story:
`nano20m_narrative10` cut narrative 46.80% → 10% and moved `lm narrative` to **0.4667**.
Interpolating to this arm's twenty points predicts ~0.4212; the measured value is **0.3949**,
better than removal alone. **SODA partly substitutes for what TinyStories was providing** — as a
source of simple narrative English it is a worse fit than children's stories and a far better
one than nothing. The clean attribution arm, narrative at 26.80% with web absorbing, still does
not exist and is the follow-up.

`tool.selection` is the surprise. Cutting narrative to 10% cost it **34 items** at a floor of 8,
and §11 carries that as an open question. Cutting to 26.80% *with dialogue in the gap* costs
**nothing** — +5, inside the floor. Either the cost is not linear in the cut, or transcript-shaped
text is what narrative was supplying and dialogue supplies it too. That is a real contribution to
a question the sixteenth finding opened and could not answer.

*(Withdrawn by the thirtieth finding. `tool.selection`'s frozen floor is **44**, so the 34 is
inside it and so is the +5: this is a contrast between two unreadable numbers, and neither the
non-linearity reading nor the dialogue-substitutes reading is supported by it. The question the
sixteenth finding opened is still open, and this row cannot close it — see the twenty-eighth
finding, where the same row fails the same way on an arm.)*

### The two copy rows disagree, and that is the eighteenth finding working

`tool.copy` falls **120 → 78, −42 against a floor of 18**, which reads as the largest copy
regression in the project. `tool.copy_wide` on the same checkpoint moves **−8 against a floor of
29**, which is nothing. The frozen row is 120 prompts over **six** answers, so a 42-item move is
roughly two facts flipping — and the wide row, 300 prompts over 232 answers, says the behaviour
did not change. Every earlier finding would have recorded the −42. This is the first time the
disagreement has appeared on a new arm rather than in a re-score, and the widened row is the one
to believe.

`schema.conform` **+6 at a floor of 2** is real and unexplained. The structured slice is
byte-identical and at the same token count in both corpora, so something about replacing
children's stories with dialogue helps the model build a declared object.

*(Withdrawn by the thirtieth finding: the floor is **8**, so +6 is inside it and there is
nothing here to explain. The twenty-seventh finding's failure-mode decomposition leans on this
+6 and is annotated accordingly.)*

### What this does not say

It does not say SODA is the right conversational source — it says the reason it was rejected was
not a reason. Nothing here measures **register**, which is the only thing the slice is bought
for: no eval row asks whether he answers like a person in conversation rather than like a
storybook, and `variety.distinct3` still draws half its prompts from TinyStories openings. So
the arm clears SODA of the charge that sank it and leaves the question it was supposed to answer
untouched. That gap is now the sharpest one in `evals/`, and it is the same shape as the three
the project has already closed by building a ruler first.
