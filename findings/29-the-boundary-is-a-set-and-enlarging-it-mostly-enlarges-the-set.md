# More phrasing templates fix only the phrasings that were added

**Full result:** The boundary is a set, and enlarging it mostly enlarges the set

**Cost:** 0 s of new scoring on record; it reads 3 cards scored for an earlier finding (`nano20m_conv20`, `nano20m_v1`, `nano20m_v1_wide`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The twenty-eighth finding ended with a diagnosis and no fix. `configs/mix_v1_wide.py`
spends it: `corn/temporal.py` gains opt-in wide pools taking the left edges from **6 → 24**
on `date_past`, **6 → 23** on `date_nonpast` and **16 → 27** on `recall`, including the two
shapes that finding implicated — the slot placed **first**, where there is no left cue at all,
and edges that are prepositions the model could read as part of the span (`of {e}`).

**One variable, and the corpus proves it.** Every other source is byte-identical to `mix_v1`;
`temporal_wide.txt` is the same generator at the same `--target-mb 52`, the same seed, the same
anchor window, the same expressions and the same `resolve_date` payloads. `check_copyable.py`
reads its copy slots at 1,442 effective values and 122.2 uses each — `temporal.txt`'s figure to
the decimal. `prepare_mix` lands on **130,279,711 train / 654,670 val**, `mix_v1`'s counts to
the token. The utterance line is the only thing that moved, and the base arm still regenerates
byte-identical, so nothing already scored was invalidated to get this.

| row | `v1` frozen | `v1` para | `v1` held-out | `wide` frozen | `wide` para | `wide` held-out |
|---|---|---|---|---|---|---|
| `temporal.route` | 398/400 | 348/400 | 366/400 | **399/400** | **389/400** | **383/400** |
| `temporal.copy` | 353/353 | 353/353 | 353/353 | 353/353 | 353/353 | 353/353 |
| `tool.selection` | 156/200 | 134/200 | 134/200 | 155/200 | 141/200 | 141/200 |
| `tool.validity` | 175/181 | 167/181 | 167/181 | 169/181 | 165/181 | 165/181 |
| `tool.copy_wide` | 276/300 | 278/300 | 278/300 | 285/300 | 287/300 | 287/300 |
| `schema.conform` | 193/200 | 193/200 | 193/200 | 192/200 | 192/200 | 192/200 |
| `tool.copy` | 100/120 | 100/120 | 100/120 | 92/120 | 92/120 | 92/120 |

**Only the `temporal.*` rows differ between the para and held-out columns, and
that is by construction rather than by result.** The held-out arm rewrites the temporal
carriers and reuses the paraphrase pool for the tool ones, so `tools.jsonl` and
`tool_copy_wide.jsonl` are byte-identical between the two; every tool row is therefore the
same measurement printed twice, and `schema.conform` and `tool.copy` are the invariance
controls, identical to the frozen files in all three arms. Read those columns as one.

**The paraphrase gap goes from 50 items to 10**, with the frozen row unchanged at 399/400 —
nothing was traded away in-distribution to buy it. `temporal.copy` is 353/353 in all six
cells, and the failure mode never changes, only its count: `wrong_expression` is the whole of
it throughout, 52 → 11 on paraphrase, 33 → 17 on held-out, 2 → 1 on frozen.

Every non-temporal row is inside its floor — and the floors below are the ones a seed
replicate on *this* corpus measured, not the borrowed ones this section originally quoted:
`tool.selection` +7 against **41** on an arm and **19** frozen, `schema.conform` −1 against
**5**, `tool.copy` −8 against **8**, `tool.copy_wide` +9 against **5** frozen. See the two
sections below; the seed turns out to matter more than any of them.

### Most of the gain is the edges that were added, which is the uncomfortable half

The wide pools were written *after* seeing which left edges failed, so a single before/after
number cannot read this arm. Splitting the paraphrase items by whether their left edge is one
the wide pools introduced:

| bucket | n | `v1` | `wide` | |
|---|---|---|---|---|
| base-covered | 159 | 154 | 157 | +3, already at ceiling |
| **newly covered** | 88 | 55 | **88** | **+33 — a perfect score** |
| still uncovered | 153 | 139 | 144 | +5 |

**33 of the 41-item gain is the treated group, and it goes to 88/88.** That is the model
acquiring the edges it was handed, which is exactly what §11's copyable-span rule predicts
when a space is enlarged without changing its kind. Reporting only "348 → 389" would have
sold this as segmentation.

### There is no transfer, and the seed replicate is what says so

`evals_heldout` was **pre-registered** — built and hashed before `nano20m_v1_wide` finished
training — precisely because the still-uncovered bucket above is 153 items with no measured
floor and cannot carry a conclusion. Its 400 temporal items use 24 left edges appearing in
*neither* pool, chosen to be absorbable in the way the mechanism predicts matters;
`check_heldout_edges` fails the build if any is an edge either pool contains.

The first seed read 366 → **383**, +17, and was written up here as a small real transfer with
a caveat that a net +17 assembled from a +9 on one edge and a −6 on another was not something
one arm at one seed could attribute. Four seeds of `nano20m_v1_wide` — 1337/1338/1339/1340,
two differing fields of 30, same corpus and bins — settle it:

| arm | `v1` | 1337 | 1338 | 1339 | 1340 | wide spread |
|---|---|---|---|---|---|---|
| frozen | 398/400 | 399 | 396 | 398 | 398 | 3 |
| paraphrase | 348/400 | 389 | 370 | 367 | 385 | **22** |
| **held-out** | **366/400** | 383 | 349 | 365 | **394** | **45** |

**On the held-out arm the baseline sits squarely inside the range the wide seeds span**
(349–394, with `v1` at 366). The +17 was noise, and so was the −17 that replaced it. Per edge
it is obvious in hindsight: `recorded` reads 44/45 on one seed and 22/45 on another.

The paraphrase arm's buckets are what survive, and they are stronger than the row total:

| bucket | n | `v1` | 1337 | 1338 | 1339 | 1340 | spread |
|---|---|---|---|---|---|---|---|
| base-covered | 159 | 154 | 157 | 156 | 150 | 155 | 7 |
| **newly covered** | 88 | **55** | **88** | **88** | **84** | **88** | **4** |
| still uncovered | 153 | 139 | 144 | 126 | 133 | 142 | 18 |
| all | 400 | 348 | 389 | 370 | 367 | 385 | 22 |

**The treated bucket goes 55 → 87 mean across four seeds, against a spread of 4 — an effect
eight times its own noise, and the tightest thing in this document that is not at ceiling.**
The untreated bucket spreads 18 with `v1`'s 139 *inside* it, and base-covered spreads 7 with
`v1`'s 154 inside that. So the row's 22-item wobble lives entirely in the two buckets where
there is no effect, and the effect lives in the one bucket that barely wobbles.

That is why the decomposition had to exist. Read as a row total, this arm is +19 to +41 against
a seed spread of 22 and would be called unreadable. Read by bucket, it is +32 against 4 in the
treated group and flat everywhere else — the same data, and the only version that says what
happened.

`configs/nano20m_v1_wide.py` pre-registered this exact outcome as the weak pass: "improvement
confined to carriers whose left edge the wide pools now cover, with the still-uncovered ones
flat. That is the model learning a larger memorised set, which is what §11's copyable-span rule
predicts happens when you enlarge a space without changing its kind." That is what happened,
and four seeds now say so.

`configs/nano20m_v1_wide.py` pre-registered this exact outcome as the weak pass: "improvement
confined to carriers whose left edge the wide pools now cover, with the still-uncovered ones
flat. That is the model learning a larger memorised set, which is what §11's copyable-span rule
predicts happens when you enlarge a space without changing its kind." That is what happened.

**The floors this section is read against are the thirtieth finding's, not the nineteenth's.**
The four seeds above were run to price this arm and priced the whole harness instead: a row's
noise depends on which arm it is scored on, every floor in this document was measured on the
frozen set, and reading an arm delta against a frozen floor is the error this finding's first
draft made twice.

### Both sides replicated, and the effect stops needing a floor at all

Everything above is four seeds of the treatment against **one** of the baseline. Four seeds of
`nano20m_v1` close that: with both sides replicated the question is no longer "does the delta
clear a floor" but "do the two ranges overlap", which needs no borrowed constant and is in the
same units as the rows. `scripts/effect.py` prints it.

| arm / bucket | `mix_v1` (4 seeds) | `mix_v1_wide` (4 seeds) | verdict |
|---|---|---|---|
| `temporal.route`, frozen | 398–400 | 396–399 | overlap — **costs nothing in-distribution** |
| `temporal.route`, paraphrase | 324–348 | **367–389** | **separated by 19** |
| `temporal.route`, held-out | 331–366 | 349–394 | **overlap — no transfer** |
| bucket: base-covered | 149–154 | 150–157 | overlap |
| bucket: **newly covered** | **50–68** | **84–88** | **separated by 16** |
| bucket: still uncovered | 119–139 | 126–144 | overlap |

**Every other behaviour row overlaps on every arm** — `tool.selection`, `tool.validity`,
`tool.copy`, `tool.copy_wide`, `schema.conform`, `temporal.copy`, both refusal rows. So the
intervention does exactly one thing, and the design can now say so without a floor: it moves
`temporal.route` under paraphrase, entirely through the bucket whose left edges it added, and
it moves nothing else anywhere.

The two claims this finding has carried since its first draft both survive, and one of them is
now stronger than the version that was withdrawn and restored: the treated bucket separates
with eight seeds and a 16-item gap between non-overlapping ranges, and the held-out arm
overlaps with eight seeds, which is a negative that no further seeding will rescue.

**The cost was overstated by an order of magnitude.** `lm temporal` was reported as +0.0033
against a floor of 0.0009 — one seed against one seed. Four-a-side, `mix_v1` spans
0.0939–0.0973 and `mix_v1_wide` spans 0.0976–0.0985: still separated, and by **0.0003**.
`lm narrative`, `lm web` and `lm conversational` all overlap, so they cost nothing measurable
rather than "inside their floor". Widening the left context is close to free.

### What it cost

*(Superseded by the section above: four-a-side the separation is 0.0003, not 0.0033, and the
other three rows overlap outright. The single-seed reading is kept because it is what the
config pre-registered and what the arm was judged on at the time.)*

`lm temporal` **0.0945 → 0.0978**, +0.0033 against a floor of 0.0009, and the only language row
outside its noise — narrative +0.0007 (floor 0.0012), web +0.0002 (0.0038), conversational
+0.0003 (0.0009). `configs/nano20m_v1_wide.py` named it in advance as the one row allowed to
move: a slice with 24 left edges where it had 6 is genuinely higher-entropy, and modelling it
worse is not evidence about anything else.

### What this does not show

- ~~**One arm, one seed.**~~ **The replicate ran and took the transfer claim with it** — see
  above. What survives is two seeds, which is a range and not a floor, and the nineteenth
  finding's own lesson is that treating one pair's spread as a threshold repeats the error one
  level down. The reproducible part of this arm is 88/88 on the treated bucket, twice.
- **It does not reach `tool.selection`.** That row fell 22 items under paraphrase, the
  left-edge split never explained it, and widening the *temporal* templates moved it +7
  against a floor of 8. The `save_note` fallback is still unexplained, and the equivalent
  widening of `corn/toolgen.py`'s pools has not been run.
- **The gap does not fully close.** 389 and 383 against a 399 ceiling.
- **The held-out edges are hand-written.** Held out by construction and checked mechanically,
  but still one person's idea of an absorbable left edge rather than transcribed speech.

### The rule this leaves

§11's copyable-span rule has been about a span's *contents* since the fourteenth finding. This
adds the other half, now demonstrated rather than inferred: **a span's boundaries are learned
the same way, and enlarging that set behaves like enlarging any other memorisable set — it
buys exactly what it contains, twice over, and transfers nothing.** A generator emitting ten
thousand distinct expressions behind six distinct left edges has built exactly the defect §8's
guard exists to catch, and `check_copyable.py` — which counts effective values *in* the slot
and passed this corpus at 1,442 — cannot see it.

### The conversational decontamination flag was crying wolf, and had been since `mix_conv20`

Scoring this arm surfaced something unrelated to it: every scorecard with a conversational
slice reads `conversational  CONTAMINATED (1/16 probes found in .../train.bin)`. It is on
`nano20m_conv20`, `nano20m_v1` and `nano20m_v1_wide` alike, and it is the *third* appearance of
the same bug shape.

The fifth finding fixed a status that failed by design on the temporal slice — a substring
search finds the `<|call|>` envelope in any corpus that contains the slice, so probes were
split into `bearing` (carrying a held-out date, discriminating) and `format` (reported as
context, never fatal). Marker-less texts were exempted with an argument that is correct for
prose and wrong for SODA: "`narrative` is held out by reserved bytes, so any probe of it in the
stream is a leak."

The hit is this probe:

```
"rvice for about 4 years now. I've had a lot of experience dealing with different types of custom"
```

**It occurs 201 times in `data/raw/conversational.txt`** — 200 in the region every mix
legitimately reads, and once in the reserved tail. `reserve_tail` is working exactly as
designed: the eval region begins at byte 780,537,489 and the only occurrence inside it is at
781,628,638. The probe is boilerplate, SODA is generated dialogue that repeats itself, and its
presence downstream says nothing whatever about the eval text.

So the fix is the fifth finding's rule applied to the population it did not have to consider: a
probe that is **not unique in its own source file** cannot discriminate a leak, exactly as a
format probe cannot for a generated slice, and is partitioned off the same way.
`corn/evals.py` reads the source path from the manifest's `{name}_source` record, counts each
probe's occurrences in one pass, and only unique probes set the status. `conversational` now
reads `clean (15 of 16 probes unique to the reserved tail)` with the duplicated hit printed
beside it. Counted rather than filtered before sampling, because the count is what lets a text
with **no** discriminating probe left read `indeterminate` rather than `clean` — the rule that
a check which cannot fail is the thing this module exists to prevent.

Two properties worth stating, because a decontamination fix that quietly weakens the check is
worse than the false alarm it removes. **`narrative` and `web` keep all 16 probes**: prose cut
from a real file does not repeat itself, so nothing about them changes. And a planted probe of
the reserved tail still reads `CONTAMINATED` — `check_evals.py` group 7 carries that as a
regression test beside the new false positive, which is how the fifth finding's fix was guarded
and for the same reason.

`HARNESS_VERSION` stays at 1. No scored quantity changed: the edit is confined to
`contamination()` and two helpers, and nothing in `nats_per_byte`, `evaluate_behaviour`,
`evaluate_variety` or `evaluate_register` was touched. The cost is ~25 s added to a full
scoring run, almost all of it reading the 2.2 GB narrative source.

**What it does not settle.** Uniqueness in the source is a proxy for discriminating power, not
the thing itself — a probe occurring twice, once in the tail and once by coincidence, is now
discarded rather than investigated. At 96 bytes that coincidence is vanishingly unlikely in
prose and evidently routine in generated dialogue, which is the asymmetry the fix is built on
and not something it measures.
