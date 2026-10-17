# Forty-third finding — the two extra seeds were already on disk, and the floor they measure retires three readings

**Cost:** 4.5 min of scoring on the 1 card first cited here (`nano20m_v1_seed4`); it also reads 5 cards scored for an earlier finding (`nano100m_v1`, `nano20m_v1`, `nano20m_v1_chat` and 2 more). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The forty-first finding closed on "more baseline seeds are the only thing that makes
`tool.name_fidelity` quotable at all, and they cost 17 minutes each." They cost nothing.
`nano20m_v1_seed3` and `nano20m_v1_seed4` have been trained since the thirtieth finding and were
scored on `evals_para`, `evals_heldout`, `evals_wideonly` and all six payload arms — but never on
the **frozen set with the three `--add` files present**, which is where `daycross.*`,
`refusal.say*` and `tool.name_fidelity` live. `*__newrows.json` existed for `nano20m_v1` and
`nano20m_v1_seed2` and for nothing else in the baseline. Two re-scores, ~5 minutes each, no GPU
training and no new corpus.

## The floor, at four seeds

| row | s1 | s2 | s3 | s4 | spread | previously quoted at |
|---|---|---|---|---|---|---|
| `tool.name_fidelity` /120 | 64 | 33 | 37 | 44 | **31** | 2 seeds, spread 31 |
| `daycross.with_day` /200 | 30 | 1 | 23 | 25 | **29** | 2 seeds |
| `daycross.no_day` /200 | 156 | 112 | 154 | 122 | **44** | 2 seeds |
| `daycross` delta | -126 | -111 | -131 | -97 | **34** | 2 seeds |
| `refusal.say` /270 | 172 | 162 | 194 | 204 | **42** | 2 seeds |
| `refusal.say_unechoed` /55 | 0 | 0 | 0 | 0 | **0** | 2 seeds |
| `tool.validity` /181 | 175 | 172 | 167 | 157 | **18** | — |
| `temporal.route` /400 | 398 | 398 | 398 | 400 | **2** | — |

The two-seed spreads were not luck in the direction that would have been convenient. Every one of
them survived doubling, and `refusal.say` got **wider** — 10 of 270 across two seeds, 42 across
four. That is the thirty-seventh finding's caution arriving with a number: a two-seed spread is a
range and not a floor, and here the range was the optimistic half.

## What it settles

**The forty-first finding stands, and now it is measured.** Baseline [33, 64] becomes
[33, 64] at four seeds — 33, 37, 44 and 64, with seed 1 sitting 20 above the next-highest. The
`toolnames` arm reads [39, 53], still strictly inside. The row cannot read that arm, and this is
no longer an inference from two points.

## What it retires

**1. `refusal.say` on the chat arm.** DATA.md §11 records "`refusal.say` moved 162/172 →
188/196 with nothing in this corpus pointing at it". The arm's 188 and 196 sit inside the
baseline's own **162–204**. There was no move. The honest reading was always the suspicious one —
`mix_v1_chat` swaps a conversational file and has no path to a refusal row — and the corpus was
right and the row was wrong.

**2. `refusal.say` across capacity.** `nano100m_v1` reads **190/270** against the 29.6M
four-seed 162–204. Inside. The handoff's "172 → 190" is not a capacity reading. The ninth open
item's conclusion — that the row was recall end to end — is unaffected and was reached another
way.

**3. `tool.name_fidelity` across capacity.** `nano100m_v1` reads **75/120** against a 29.6M
maximum of 64 and a spread of 31. **+11 over a 31-wide range at one seed** is not a reading, and
the "64 → 75" row in the handoff's both-sizes table should not be quoted as a capacity gain.

## What survives, and is stronger for it

**The fortieth finding.** Its control is `nano20m_v1_chat` ×2, not `mix_v1`, so the widened
baseline does not touch it directly — but it prices the instrument the finding is built on. The
`daycross` delta has a **34**-wide floor on this corpus, against the finding's baseline
[-155, -120] → arm [-63, -29]: worst-case separation 120 → 63 is **57**, still clear of 34.

**Gap 1 does not yield to capacity, and now against four seeds.** `daycross` delta reads **-150**
at 91.6M against 29.6M's -97 to -131. It is 19 outside the bottom of a 34-wide range, which is
*less* than the range — so "the header costs 126 at 29.6M and 150 at 91.6M" is one seed against
four and the two are not separable. The direction is what the finding claimed: capacity does not
buy the header back, and if anything reads slightly worse.

**`refusal.say_unechoed` is a hard zero.** 0/55 on four seeds of the baseline, both seeds of the
chat arm, and both sizes. Nothing in this project has ever moved it.

> **Why, answered 2026-08-19 — the forty-sixth finding.** Because the class was never in the
> corpus. `data/raw/tools.txt` is missing the entire `cold_start` class its own generator emits,
> so the two sentences these 55 items rest on appear **0 times** in every corpus through
> `mix_v2`. The zero was an absent class rather than a hard behaviour, and the first corpus that
> contained the class read 55/55 — by reciting two strings seen 902 times.

## The pairing check now holds on four seeds, and it prices the delta

`daycross.no_day` is `tool.selection` on the same items — identical `pass`, `n` and `why`, with a
`named` breakdown added. That was known and is the point: the file was built so the untreated cell
is a row already in the catalogue, and the handoff records the check passing on `nano20m_v1` and
`nano100m_v1`. It passes on seeds 3 and 4 as well, byte-for-byte on all three fields.

What is new is what that costs. The delta's untreated side inherits `tool.selection`'s measured
floor of **44** (thirtieth finding), the largest in the catalogue, so a `daycross` delta is not two
independent measurements against two small floors. Its own floor comes out at **34** — smaller
than 44, because the two cells move together within a seed, which is exactly why the delta is the
thing to quote and the cells are not. That was the design's assumption and it is now measured:
`no_day` spans 44 across four seeds, `with_day` spans 29, and the delta spans 34 rather than the
73 the two would give if they were independent.

## What this does not settle

- **The floor is `mix_v1`'s.** The thirtieth finding's rule is that a floor is a property of the
  arm. Four seeds of one corpus says what this corpus reproduces to, not what `chatday`,
  `toolnames` or `toolspace_decline` reproduce to. Each of those has two seeds.
- **`tool.name_fidelity`'s distribution is not four points of noise.** 33, 37 and 44 cluster and
  64 does not. That could be a heavy tail, or seed 1 could be doing something the other three are
  not, and 120 items cannot tell the difference. More seeds would narrow it; the row is cheap to
  score and the checkpoints do not exist yet.
- ~~**The scorer defect is untouched.**~~ **Repaired in the same session, and it does not change
  these numbers.** `score_name_fidelity` gains `substituted_composed`, meaning exactly "a name
  from `corn.toolgen.COMPOSED_CONTACTS`" — an addition after the `CONTACTS` check rather than a
  redefinition, so the three scorecards carrying the older buckets cannot move. Verified on the
  plan's rule-4 terms: re-scoring `nano20m_v1` and `_seed2` leaves **23 pre-existing behaviour
  rows byte-identical** on both, every scored section identical, and the new bucket **never
  fires** on either — which is the property that makes it safe. All four baseline seeds share
  `CONTACTS`, so this finding's numbers were internally consistent either way; the repair is for
  the next arm that moves the book.
