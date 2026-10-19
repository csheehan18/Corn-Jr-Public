# No data share moves copying above noise

**Full result:** Copy discipline is not a lever any share moves

Six checkpoints re-scored on `tool.copy_wide`, spanning every share change the project has
measured. No training: the checkpoints already existed, and the frozen rows came back
**byte-identical on all five re-scores**, which is the harness stability claim the whole
exercise depends on.

| comparison | frozen `tool.copy` (floor 18) | `tool.copy_wide` (floor 29/300) |
|---|---|---|
| structured 2.5% → 10% | 120 → 99, **−21 real** | 277 → 276, **−1 noise** |
| tools 0.61% → 15% | 120 → 98, **−22 real** | 289 → 278, **−11 noise** |
| narrative 47% → 10% (+ temporal) | 120 → 111, −9 noise | 277 → 269, −8 noise |
| narrative 47% → 10% (temporal held) | 120 → 114, −6 noise | 277 → 282, +5 noise |

**Both of the frozen row's surviving "real" calls were one held-out fact each, and both
evaporate.** A 21-item move on a six-answer row is one fact flipping; the wide row puts the
same comparison at one item in three hundred. So after nineteen findings of pricing shares
partly on copy discipline, the honest position is that **no share change yet tested moves it
measurably at all.** The six corpora sit between 269 and 289 of 300 — a spread of 20 — while
four seeds on a *single* corpus span 29. Composition moves this row less than the seed does.

### What that leaves standing per share

With `tool.copy` removed as a decision variable, two comparisons get simpler and more decisive:

- **Structured.** 10% buys `schema.conform` +22 at a floor of 2 — eleven times its noise — and
  costs `lm web` 0.0068 at a floor of 0.0038. The copy leg is gone. So it is a clean win for
  10% against a small prose cost, not the trade the nineteenth finding settled on, and **not**
  the "2.5% better on every axis" §11 carried for a week. Three readings, and only the third
  had a ruler that could see the question.
- **Tools.** 15% buys `tool.selection` +34 at a floor of 8, and costs `lm narrative` 0.0060 and
  `lm web` 0.0114 against a floor of 0.0038. The eleventh finding's stated cost — 12 items of
  `tool.validity` — is 2 items on the re-run pair and inside a floor of 13, and the copy cost
  is gone too. **The real price of tools at 15% is prose, and it was never validity or copying.**
  That arm is upsampled 25x, so displacing real text is exactly what it should cost.

**Annotated after the thirtieth finding: both bullets get weaker, and the second loses its
benefit leg entirely.** `schema.conform`'s floor is **8** rather than 2, so structured's +22 is
2.75x its noise and not eleven times — still the cleanest number here, still a win for 10%, but
no longer an order of magnitude clear. `tool.selection`'s frozen floor is **44** rather than 8,
so tools at 15% buying +34 is **inside the noise** and cannot be claimed. The bullet's own
conclusion survives in a stronger form than it was written in: if the selection gain is
unreadable and validity and copying were already gone, then **tools at 15% over 0.61% buys
nothing measurable at all and costs prose** — which is the eleventh finding's "a 25th of the
declared share buys most of the behaviour" with "most" upgraded. The presence claims are
untouched; `tool.selection` 0 → 146 is 3.3x even the widened floor. What is gone is every
attempt to price the *share* on this row.

### The uncomfortable part

`tool.copy` at 120/120 has been the project's evidence that deference generalises past
`resolve_date` since the thirteenth finding, and it is the row §4's whole conclusion was said
to rest on. It reads 92–96% on the wide row across every checkpoint, moves by less than its own
seed noise under every corpus change tried, and is currently unable to distinguish any two
corpora in the project. That is not evidence the behaviour is absent — 92% on held-out invented
facts is a real skill, and `temporal.copy` remains 353/353 on all four seeds — but it does mean
**copy discipline has never been shown to depend on the corpus, only on having some.** The
thirteenth finding's 27 → 120 stands, and it is a claim about the *tool slice's answer space*
rather than about any share.
