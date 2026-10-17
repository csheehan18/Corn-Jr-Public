# Nineteenth finding — the noise floor, measured, and what it costs the back catalogue

**Cost:** 3.5 min of scoring on the 1 card first cited here (`nano20m_struct`); it also reads 1 card scored for an earlier finding (`nano20m_balanced`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Four seeds on one corpus. `nano20m_balanced` at 1337, 1338, 1339, 1340 — same `data_dir`, same
bins, two differing fields of 30, all four selected at iter 5,237. Nothing here is a model
result; it is the error bar sixteen findings were written without.

| row | 1337 | 1338 | 1339 | 1340 | spread |
|---|---|---|---|---|---|
| `lm temporal` | 0.0944 | 0.0947 | 0.0953 | 0.0951 | **0.0009** |
| `lm narrative` | 0.3679 | 0.3677 | 0.3666 | 0.3672 | **0.0012** |
| `lm web` | 0.9106 | 0.9110 | 0.9089 | 0.9127 | **0.0038** |
| `temporal.copy` | 353/353 | 353/353 | 353/353 | 353/353 | **0** |
| `refusal.clarify` | 47/47 | 47/47 | 47/47 | 47/47 | **0** |
| `refusal.no_guess` | 47/47 | 47/47 | 47/47 | 47/47 | **0** |
| `temporal.route` | 400/400 | 398/400 | 400/400 | 399/400 | **2** |
| `schema.conform` | 172/200 | 174/200 | 174/200 | 173/200 | **2** |
| `tool.selection` | 150/200 | 154/200 | 157/200 | 158/200 | **8** |
| `tool.validity` | 171/181 | 158/181 | 166/181 | 168/181 | **13** |
| `tool.copy` | 120/120 | 102/120 | 102/120 | 116/120 | **18** (15.0 pts) |
| `tool.copy_wide` | 277/300 | 278/300 | 249/300 | 266/300 | **29** (9.7 pts) |
| `variety.distinct3` | 89.34% | 87.49% | 87.96% | 88.73% | **1.85 pts** |

**The rows do not share a noise floor and never did.** Three are exactly reproducible across
seeds, two move by 2 items, and the copy and validity rows move by 13–18. Reading a 10-item
delta as a result on `schema.conform` and on `tool.copy` are not the same act, and the project
has been doing both.

### The perfect score was six facts, and the wide row says 92%

`tool.copy` reads **120/120 on seed 1337**. On that same checkpoint `tool.copy_wide` reads
**277/300 — 92.3%**, with 21 `wrong_answer` and 2 `trained_answer`. The ceiling the twelfth and
thirteenth findings established, and that "the copy discipline generalises" was declared on,
is six hand-written facts all landing right. The behaviour it stands for is at 92%, not 100%.

The two rows also **disagree about which checkpoint is better**. Frozen ranks 1337 first and
1338 joint-last; wide ranks 1338 first and 1337 second, and puts 1339 last by a distance the
frozen row cannot see at all (249/300 against 102/120, the same score 1338 gets). A six-way row
does not order checkpoints, and it has been used to order them since the eleventh finding.

Widening did not make the row quiet — 9.7 points of spread against the frozen row's 15.0 — so
**copy behaviour is genuinely seed-dependent at this scale** and that is a real finding rather
than an artefact of six facts. What widening bought is a number that means what it says.

### What the floors do to conclusions already drawn

| claim | size | floor | verdict |
|---|---|---|---|
| `schema.conform` 0 → 194 (fourteenth) | 194 | 2 | stands, overwhelmingly |
| `tool.copy` 27 → 120 (thirteenth) | 93 | 18 | stands |
| `tool.selection` 0 → 146, `tool.validity` 112 → 167 (eleventh) | 146, 55 | 8, 13 | stands |
| every nats/byte comparison in the project | 0.03–0.10 | 0.004 | stands |
| **structured 10% → 2.5% costs `schema.conform` 22 items** | 22 | **2** | **real, 11x the floor** |
| structured 10% → 2.5% buys `tool.copy` 21 items | 21 | 18 | **real, but 1.2x — see below** |
| structured 10% → 2.5% buys `tool.validity` 3, `temporal.route` 2 | 3, 2 | 13, 2 | inside noise |
| **`tool.selection` 150 → 116 from the narrative cut (sixteenth)** | 34 | **8** | **real, and was dismissed** |
| `tool.copy` 120 → 111 from the narrative/temporal cut (sixteenth) | 9 | 18 | withdrawn |
| `variety.distinct3` 89.3 → 89.2 (sixteenth) | 0.1 | 1.85 | withdrawn |

**Annotated after the thirtieth finding: two of these verdicts reverse, and both are ones this
section added to the back catalogue rather than removed from it.** Every floor in the column
above was measured on four seeds of `nano20m_balanced`, on the frozen set. Eight further
checkpoints across two more corpus families put the *frozen* floors at `tool.selection` **44**
and 36, `tool.copy_wide` **41** and 28, `tool.copy` 20 and **28**, `schema.conform` 4 and **8**.
Re-read against the worst case over everything now measured:

| claim | size | 19th floor | worst frozen | verdict now |
|---|---|---|---|---|
| `schema.conform` 0 → 194 (fourteenth) | 194 | 2 | 8 | stands, 24x |
| `tool.copy` 27 → 120 (thirteenth) | 93 | 18 | 28 | stands, 3.3x |
| `tool.selection` 0 → 146 (eleventh) | 146 | 8 | 44 | stands, 3.3x |
| `tool.validity` 112 → 167 (eleventh) | 55 | 13 | 18 | stands, 3.1x |
| every nats/byte comparison | 0.03–0.10 | 0.004 | 0.0047 | stands |
| structured 10% → 2.5% costs `schema.conform` 22 | 22 | 2 | **8** | real, but **2.75x, not 11x** |
| structured 10% → 2.5% buys `tool.copy` 21 | 21 | 18 | **28** | **inside noise — withdrawn** |
| `tool.selection` 150 → 116 (sixteenth) | 34 | 8 | **44** | **inside noise — withdrawn** |

The four load-bearing "stands" verdicts all survive, at smaller multiples. The three withdrawals
below the line — `tool.copy` −9, `variety.distinct3` −0.1, and the two inside-noise rows — stay
withdrawn, since a wider floor cannot rescue anything. **Everything this section moved in the
other direction is gone.** Both reversals have their own sections below and are annotated there.

**"2.5% structured is better on every axis that matters" does not survive, but the replacement
is a trade rather than a reversal.** Cutting to 2.5% costs 22 items of `schema.conform` at a
floor of 2 — eleven times its noise, the most solid single number in the comparison — and buys
21 items of `tool.copy` at a floor of 18, which clears its floor by a factor of 1.2 and is
therefore the weakest kind of real. It also costs 0.0068 of `lm web` against a floor of 0.0038.
So 10% buys schema conformance and costs copy discipline and a little prose, and the *sizes*
say the schema side is far better established than the other two. §11's "better on every axis"
was wrong; "10% is better full stop" would be wrong in the same way, from the other direction.

*(Read against the thirtieth finding's floors: `schema.conform`'s 22 is **2.75x its noise, not
eleven times**, and while it is still the most solid number in the comparison that is now a
statement about the other two rather than a strong claim about this one. The `tool.copy` leg is
inside a floor of 28 and gone twice over — on size here, and on the row itself in the twentieth
finding. The `lm web` leg is untouched; the language rows are the only ones that reproduced
across all three families.)*

**The 21 items are also exactly one fact.** `tool.copy` is the six-answer row, so a 21-item
movement is one held-out fact flipping and sits at the row's resolution limit rather than
above it. That comparison is not settled by arithmetic on the old scorecards — it is settled by
re-scoring `nano20m_struct` on `tool.copy_wide`, which costs no training at all.

### The sixteenth finding dismissed a real regression — withdrawn

> **Withdrawn by the thirtieth finding, and the sixteenth was right.** `tool.selection`'s
> *frozen* floor is **44** on four seeds of `mix_v1` and **36** on `mix_v1_wide`. The 34-item
> fall is inside both, and so is the attribution arm's 28. The section below is kept because its
> reasoning about borrowed caveats is still correct — it just turned out to apply to this
> section as much as to the one it was aimed at.

`tool.selection` 150 → 116 across the narrative cut was written off there as "34 points, one
point inside the ~35 the thirteenth finding established as unreadable, so it is not evidence
either way." **The floor is 8, and 34 is more than four times it.** The narrative cut costs a
large, real amount of tool selection, and the attribution arm agrees independently: holding
temporal and cutting only narrative reads 122/200, also far outside the floor. That is the
single biggest cost of cutting narrative and it went unrecorded because a caveat borrowed from
adjacent checkpoints of one run was pointing at the wrong row.

### `tool.selection` was never the unreadable row — withdrawn, and the number was right

> **The ~35 this section demolished is bracketed by the two families measured since.** The
> row's frozen spread is 8 on `nano20m_balanced`, **36** on `mix_v1_wide` and **44** on `mix_v1`,
> so the thirteenth finding's ~35 sits inside the range and the 8 is the outlier. The criticism
> of *how* it was derived stands — adjacent late-cosine checkpoints of one run are not
> independent draws, and generalising them into a rule about corpus comparisons was not
> supported by the quantity measured. It nevertheless landed on roughly the right number, and
> this section replaced it with one that two later families contradict. `tool.selection` is in
> fact the **least** readable behaviour row in the harness: 44 frozen and 62 on an arm.

It has carried "differences under ~35 are not readable" since the thirteenth finding. Across
four seeds it moves **8 items**. The ~35 came from two *adjacent checkpoints inside one run*,
which is a different quantity — late-cosine checkpoints of one trajectory, not independent
draws — and it was generalised into a rule about corpus comparisons. The rows that actually
need the caution are `tool.copy` and `tool.validity`, and neither ever carried it.

### What four seeds is and is not

Four points give a spread, not a standard deviation, and a spread grows with sample size — a
fifth seed can only widen these. So they are lower bounds on the noise, which is the safe
direction for the use they are being put to: a delta inside these numbers is definitely not
readable, while a delta outside them is *probably* real rather than certainly. Every floor here
is also specific to this corpus, this model size and this budget, and the honest expectation is
that they move at 250M rather than that they transfer.
