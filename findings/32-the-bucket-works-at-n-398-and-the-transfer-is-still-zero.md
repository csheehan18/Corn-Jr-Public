# A bigger phrasing test; its no-transfer reading was later withdrawn

**Full result:** The bucket works at n=398, and the transfer is still zero

**Cost:** 4.4 min of scoring on the 1 card first cited here (`nano100m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The thirty-first finding built `evals_wideonly` and could not read it: twelve carriers on one
left edge, an untreated range of 8–12 touching its own ceiling, and a transfer question that no
number of seeds could answer. The arm rebuilds that bucket at **398 of 400 items across all
fourteen edges**, and it has now been scored on all ten checkpoints. No training was involved;
every one of them was already on disk.

> **The negative below is withdrawn — see "Added later" at the end of this finding.** The
> positive control stands and strengthens. The transfer claim was read off pass/fail totals on an
> arm that had no attribution files at 29.6M, and the totals cancel the effect twelve edges
> actually have.

The reading was pre-registered as three-way, and it comes out that way:

| checkpoints | on these edges | `temporal.route` /400 | spread |
|---|---|---|---|
| `mix_v1` ×4 | untreated — the baseline | **326–343** | 17 |
| `mix_v1_mid` ×2 | untreated — **the transfer test** | **336–344** | 8 |
| `mix_v1_wide` ×4 | treated — **the positive control** | **387–395** | 8 |

**The control has to be read first, and it separates by 44.** That was the precondition the
thirty-first finding stated before the result rather than after: a flat transfer number on an
insensitive arm means nothing, and this is the failure mode the n=12 bucket had already had
once. `scripts/effect.py` puts the treated group above the baseline by **44** and above the mid
group by **43**. The arm can see an effect nearly three times its own 17-point seed spread, so
whatever it says about mid, it is not saying it for want of sensitivity.

**And mid does not move.** 336–344 against the baseline's 326–343 is an overlap, on items whose
left edges mid was trained on six more of — none of them these. The mid arm learned twelve edges
completely, as the thirty-first finding showed on its own bucket, and carried **nothing** to the
other fourteen. Two doses, two directions, same answer: the twenty-ninth finding's "buys exactly
what it contains and transfers nothing" now holds where it was designed to be visible instead of
where it happened to be.

### The failure mode does not change, only its count

Every failure on this arm is `wrong_expression` — right tool, well-formed JSON, wrong words — as
it was in the twenty-eighth finding. It is 67 / 71 / 57 / 74 on the baseline seeds, 63 / 55 on
mid, and **5 / 12 / 8 / 13** on the treated arm; the only non-`wrong_expression` failures anywhere
are two `wrong_tool` and four `unparseable` across ten checkpoints. So the treatment does not
change what going wrong looks like. It removes instances of one thing, on exactly the edges it
covers, which is what enlarging a memorised set predicts and what a repaired segmenter does not.

### The arm's floor, which the thirtieth finding said had to be measured before anything was quoted

`scripts/floors.py` now carries all four arms, and the wide-only spread was the blank in that
table:

| row | frozen | paraphrase | held-out | **wide-only** |
|---|---|---|---|---|
| `temporal.route` | 3 | 24 | 45 | **17** |
| `temporal.copy` | 1 | 1 | 0 | **0** |
| `tool.selection` | 44 | 62 | 62 | **62** |
| `tool.validity` | 18 | 34 | 34 | **34** |
| `schema.conform` | 8 | 8 | 8 | **8** |

**The floor does not order with the difficulty of the arm**, which is worth recording because the
obvious guess is that it should. Wide-only items score *lower* than paraphrase items (326–343
against 324–348 is nearly the same, on carriers chosen to be harder) while spreading *less*, 17
against 24, and held-out spreads 45 on items no harder than these. A floor is a property of the
arm, and the thirtieth finding's point survives the one new arm that could have contradicted it.

The rows the arm does not rewrite behave: `tool.copy` and `schema.conform` are identical to the
frozen set on every seed, which is `floors.py`'s own self-consistency check passing, and
`temporal.copy` reads 353/353 on nine of ten checkpoints — the tenth being `mix_v1_mid`'s first
seed at 352, the same checkpoint that read 352 under paraphrase.

### What this does not settle

- **Mid is two seeds against four**, and it is the side carrying the negative. The overlap is
  wide enough that more seeds are unlikely to change it — mid's whole range sits inside the
  baseline's — but two points are a range and not a floor, and this is the third finding in a row
  to say so about the same two checkpoints.
- **It says nothing about why.** That the boundary is memorised as a set is now measured three
  ways; no instrument here distinguishes a model that cannot segment from one that has never had
  a reason to.
- **Capacity is untested.** Every checkpoint above is 29.6M. Whether a larger model transfers
  across left edges is `configs/nano100m_v1.py`'s pre-registered question, and the `still
  uncovered` bucket at 119–139 is the number to read it on.

### Added later — the negative above is withdrawn, and the row is why

`scripts/paraphrase_attribute.py` had never been run on this arm at 29.6M. Ten checkpoints were
scored on it and **none of them had an attribution file**, so "mid does not move" was read off
pass/fail totals and nothing else. Running the fifteen missing passes and splitting
`wrong_expression` by what the *backend* does with the emitted span changes the reading:

| checkpoints | total | unresolvable | **wrong date** |
|---|---|---|---|
| `mix_v1` ×4 | 326–343 | 10–21 | **36–52** |
| `mix_v1_mid` ×2 | 336–344 | 25–26 | **29–30** |
| `mix_v1_wide` ×4 | 387–395 | 1–2 | **3–8** |

`resolve_date` returns `None` for an expression it does not recognise, so an emitted span splits
three ways: it resolves to the gold date, it resolves to a *different* date, or it does not
resolve and the tool comes back with a clarify. The first two are a right and a wrong answer; the
third is Corn-Jr asking. **The row adds all three together**, and VISION §9's most important
behaviour is the difference between the last two.

**Mid separates from the baseline on wrong dates — 29–30 against 36–52 — where the totals
overlap.** Its unresolvable count rises by about as much as its wrong-date count falls, so twelve
left edges convert roughly ten confident errors into roughly ten refusals and the total scores
that as a wash. It is not a wash. The positive control is unaffected and gets stronger: the
treated arm separates by 44 on totals and by **28 on wrong dates**, on a bucket where it reads
3–8 against the baseline's 36–52.

So the finding's positive half stands and **its negative half should not be quoted**: twelve
edges transfer something, and the instrument that said otherwise cannot see the thing they
transfer. What it does not become is a claim in the other direction — mid is still two seeds, a
spread of 1 across two points is not a floor, and more mid seeds are the only thing that settles
it. `evals_heldout` was re-read the same way and overlaps on every column with spreads of 34–45,
which is that arm being unreadable rather than flat.
