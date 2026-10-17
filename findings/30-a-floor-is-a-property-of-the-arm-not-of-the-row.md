# Thirtieth finding — a floor is a property of the arm, not of the row

**Cost:** 0 s of new scoring on record; it reads 3 cards scored for an earlier finding (`nano20m_balanced`, `nano20m_v1`, `nano20m_v1_wide`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The nineteenth finding measured nine noise floors on four seeds of
`nano20m_balanced` and warned that all of it is specific to that corpus, size and budget. It
was right and it did not go far enough. Every one of those floors was measured on the **frozen
set**, where most rows sit near ceiling and have nowhere to vary, and every comparison in the
twenty-eighth and twenty-ninth findings is an *arm* comparison read against them.

`nano20m_v1_wide` at seeds 1337/1338/1339/1340 — same corpus, same bins, same budget, two
differing fields of 30 — scored on all three arms. `scripts/floors.py` prints it.

| row | frozen | paraphrase | held-out | 19th finding |
|---|---|---|---|---|
| `temporal.route` | 3 | **22** | **45** | 2 |
| `temporal.copy` | **1** | 0 | 0 | 0 |
| `refusal.clarify` / `refusal.no_guess` | 0 | 0 | 0 | 0 |
| `tool.selection` | **36** | **62** | **62** | 8 |
| `tool.validity` | 13 | **24** | **24** | 13 |
| `tool.copy_wide` | 28 | 24 | 24 | 29 |
| `tool.copy` | 28 | 28 | 28 | 18 |
| `schema.conform` | **8** | 8 | 8 | 2 |

**The same row, the same four checkpoints, and `temporal.route` moves 3, 22 and 45 depending
only on which items it is scored over.** The frozen arm sits at 396–399 of 400; there is no
room in it for a seed to show. The harder the arm, the more the seed can move — which means
the floors this project has been quoting are lower bounds for the one regime where a floor
matters least.

Three rows come out materially wider than recorded, on this corpus family:

- **`tool.selection` 36 frozen and 62 on an arm, against 8** — and **44** frozen on `mix_v1`,
  which is the number the back catalogue has to be read against. The row is not readable on a
  paraphrase arm at all and barely readable on the frozen one, which makes it the most expensive
  correction here: the twenty-eighth finding's 22-item fall is inside it, and so are the
  nineteenth's 34, the twentieth's "+34 for tools at 15%", and *both* halves of the
  twenty-fourth's 34-against-+5 contrast.
- **`schema.conform` 8, against 2.** The twentieth finding priced structured at 10% on "+22 at
  a floor of 2" and the twenty-seventh on "+15". Both survive 8 — at 2.75x and 1.9x — and
  neither survives it comfortably, and both were stated as an order of magnitude clear of noise.
  The twenty-fourth finding's "+6 at a floor of 2 is real and unexplained" does **not** survive.
- **`tool.copy` 28, against 18** — the six-answer row, still behaving as the eighteenth
  finding said it would.

Two hold exactly: `tool.copy_wide` at 28 against 29, and `tool.validity` at 13 against 13 on
the frozen arm. So this is not a claim that the nineteenth finding was wrong; it measured what
it measured, correctly, in one regime.

**And the floors do not travel between corpus families either.** Four seeds of `nano20m_v1`
give a second column, and it disagrees with the first as much as either disagrees with the
nineteenth finding: `tool.copy_wide` spreads **41** here against 28 on `mix_v1_wide` and 29 on
`mix_v1_wide`'s predecessor, with one seed reading 238/300 where its three siblings read
276–279. `schema.conform` spreads **4** here against **8** there. `tool.selection` **44** here
against 36. A floor is a property of the arm *and* the corpus, which means the only honest use
of any of these numbers is as a worst case over everything measured — the table in the
twenty-ninth finding's closing caveats — and even that is a lower bound.

### The back catalogue, re-read

Nothing was re-run: every number below was already on disk, and the pass is a reading of it
against the worst case over both families instead of the nineteenth finding's column. Each row
is annotated in place at the finding it belongs to.

| claim | finding | size | as read | worst frozen | now |
|---|---|---|---|---|---|
| `schema.conform` 0 → 194 | 14th | 194 | 2 | 8 | stands, 24x |
| `tool.copy` 27 → 120 | 13th | 93 | 18 | 28 | stands, 3.3x |
| `tool.selection` 0 → 146 | 11th | 146 | 8 | 44 | stands, 3.3x |
| `tool.validity` 112 → 167 | 11th | 55 | 13 | 18 | stands, 3.1x |
| structured 10% vs 2.5% on `schema.conform` | 19th, 20th | 22 | 2 | 8 | real at **2.75x**, not 11x |
| structured 10% given conversational | 27th | 15 | 2 | 8 | real at **1.9x** |
| structured 10% → 2.5% buys `tool.copy` | 19th | 21 | 18 | 28 | **withdrawn** |
| `tool.selection` 150 → 116 across the narrative cut | 19th | 34 | 8 | 44 | **withdrawn** |
| tools at 15% buys `tool.selection` | 20th | 34 | 8 | 44 | **withdrawn** |
| the 34-against-+5 narrative contrast | 24th | 34, 5 | 8 | 44 | **withdrawn — both legs inside** |
| conversational buys `schema.conform` | 24th | 6 | 2 | 8 | **withdrawn** |

**Every presence claim survives and every attempt to price a share on `tool.selection` does
not.** The four that stand are all step-change results — a slice existing rather than a slice
being resized — and they clear even the widened floors by more than three times. Everything
withdrawn is a share comparison read off a generation-scored row, which is precisely what this
finding says the harness cannot currently do. The lm rows are untouched throughout.

**Two of the withdrawals are the nineteenth finding's own corrections to the catalogue**, which
is the uncomfortable half. That finding removed several claims from the record and added two;
the two it added are the two a wider floor does not support. And the "~35 is unreadable" rule it
demolished sits between the 36 and 44 measured since — derived from the wrong quantity, as it
said, and closer to right than the 8 that replaced it.

### `temporal.copy` is not a floor of zero

Seed 1339 reads **352 of 353**, and so does one `mix_v1` seed under paraphrase — two of eight
checkpoints across two corpus families, one item each. That row has read 353/353 on every
checkpoint in this project's history — four seeds of `nano20m_balanced`, every mix since the pilot, both 0%-tools arms, all
three paraphrase arms of five checkpoints — and the sixth finding's central claim, that
deference installs in pretraining and does not fine-tune in, is 353/353 against 48–92%.

One item does not touch that. A 353-to-48 gap is not in danger from a row whose floor turns out
to be 1 rather than 0. What it does end is the habit of treating the row as *definitionally*
invariant: it has been used as a control on the reasoning that any movement at all would be
meaningful, and that reasoning now needs a number in it like every other row.

### The language rows reproduce, and that is the other half

| | spread over four seeds |
|---|---|
| `lm temporal` | 0.0009 |
| `lm narrative` | 0.0016 |
| `lm web` | 0.0019 |
| `lm conversational` | 0.0047 |

Four models whose `tool.selection` spans 119 to 155 agree on narrative to 0.0016 nats/byte.
That is the nineteenth finding's sharpest observation reproduced on a second corpus family —
**the language rows are share-determined and the generation-scored rows are not** — and it is
the reason a corpus comparison should be argued on the lm rows first and the behaviour rows
only where the delta clears a floor measured on the right arm.

### What this does not settle

- **Four points are a spread, not a standard deviation**, and a spread only grows. These are
  lower bounds exactly as the nineteenth finding's were.
- **One corpus family.** These floors are `mix_v1_wide`'s. That the same row reads 8 on one
  family and 36 on another is the whole point, and it applies to this table too.
- ~~**The baseline has no replicate.**~~ **Run — four seeds of `nano20m_v1`, and the baseline
  half is the more alarming one.** `tool.copy_wide` spreads **41** on the frozen arm against a
  recorded 29, with one seed reading 238/300 where the others read 276–279. `tool.selection`
  spreads **44** frozen and **50** on an arm. `tool.validity` **18** frozen and **34** on an
  arm, against 13. And `schema.conform` spreads **4** here where it spreads **8** on
  `mix_v1_wide` — so the floors do not travel between *corpus families* either, which is this
  finding's own lesson arriving one level up. The combined picture, worst case over both
  families:

  | row | frozen | paraphrase | held-out | 19th finding |
  |---|---|---|---|---|
  | `temporal.route` | 3 | 24 | 45 | 2 |
  | `temporal.copy` | 1 | 1 | 0 | 0 |
  | `tool.selection` | 44 | 62 | 62 | 8 |
  | `tool.validity` | 18 | 34 | 34 | 13 |
  | `tool.copy` | 28 | 28 | 28 | 18 |
  | `tool.copy_wide` | 41 | 39 | 39 | 29 |
  | `schema.conform` | 8 | 8 | 8 | 2 |

  `temporal.copy` has now moved on both families — 352/353 on one `mix_v1_wide` seed frozen and
  one `mix_v1` seed under paraphrase. Two of eight checkpoints, one item each.
- **It does not explain the mechanism.** "More room below ceiling means more seed variance" is
  a description. Whether the floor scales with distance from ceiling, with item difficulty, or
  with something else would need a row measured at several points on its own range.
