# The gain has no sharp threshold, and the fix was already cheap

**Full result:** There is no knee, and the intervention was already cheap

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The twenty-ninth finding widened the temporal slice's left edges 6 → 24 and took the treated
bucket to 88/88; the thirtieth confirmed at eight checkpoints that the gain is confined to the
edges the pools contain. Nothing had been run between 6 and 24, and with transfer ruled out, the
only thing left that could make the intervention cheap was where inside that range the gain sits.

`configs/mix_v1_mid.py` is the bracket: the base pools plus **the first half of what the wide
pools add**, in file order — a rule rather than a hand-picked list, because the wide pools were
written after seeing which edges failed and a second subset chosen by hand would inherit that
freedom twice. It lands `date_past` at **12** left edges. Two seeds, everything else
byte-identical to both existing arms, 130,279,711 train tokens to the token.

**The rule covers 76 of the 88 carriers the wide pools cover.** That is not a choice — it is a
fact about which left edges are common in ordinary English, and it is the whole finding.

| bucket | n | `mix_v1` ×4 | **`mix_v1_mid` ×2** | `mix_v1_wide` ×4 |
|---|---|---|---|---|
| base-covered | 159 | 149–154 | 151–155 | 150–157 |
| **mid-covered** | 76 | **38–57** | **74–75** | **72–76** |
| wide-only | 12 | 8–12 | 8–11 | 12 |
| still uncovered | 153 | 119–139 | 110–134 | 126–144 |
| row total | 400 | 324–348 | 347–371 | 367–389 |

**Twelve edges buys the items it covers exactly as completely as twenty-four does.** The treated
bucket reads 74–75 against the wide arm's 72–76 — a complete overlap — where the baseline reads
38–57. And `scripts/effect.py` puts the two arms in overlap on **every row and every bucket**,
including `newly covered` at 82–86 against 84–88. There is no knee between 12 and 24 because
there is nothing between 12 and 24: doubling the edges again buys nothing measurable.

**So the gain is proportional to coverage, and coverage is skewed.** Half the added templates
carry 86% of the recoverable items, which means the twenty-ninth finding's intervention was
already cheap and its cost was being measured against the wrong thing. The in-distribution
control is exact — `temporal.route` frozen reads **398/400 on both seeds**, the same number
`nano20m_v1` reads — and `lm temporal` spans 0.0954–0.0978 against `mix_v1`'s 0.0939–0.0973 and
`mix_v1_wide`'s 0.0976–0.0985, overlapping both. Widening the left context is free at either dose.

### The bucket that was supposed to test transfer cannot

`wide-only` is the twelve carriers the mid pools leave untrained, and on a mid checkpoint it is a
treatment's own control sitting in the same row of the same scorecard — which is why the config
pre-registered it as the interesting outcome. It does not work, and the way it failed is worth
recording.

Seed 1337 read **11/12**, which is transfer: three items gained on edges the model was never
trained on. Seed 1338 read **8/12**, exactly the baseline. And the baseline itself spans **8–12**
across four seeds, so one `mix_v1` checkpoint scores full marks on the bucket with no
intervention at all. A twelve-item group whose untreated range touches its own ceiling cannot
separate anything, at any seed count.

The config predicted n=12 would make a positive "a reason to run seeds rather than a finding."
That was right about the seeds and wrong about the remedy: the second seed did kill the reading,
but no number of seeds fixes a bucket this size. **The transfer question at 12 edges is
unanswerable as instrumented**, and answering it needs eval carriers built to sit in that
bucket rather than the dozen that happen to land there.

**Those carriers now exist, and nothing has been scored on them.** `evals_wideonly` is a fourth
arm out of `scripts/paraphrase_evals.py`, built the same way as the other three — utterances
only, every other field byte-identical to the frozen set — with every temporal carrier taking a
left edge the wide pools contain and the mid pools do not. That puts **398 of the 400 items in
the bucket instead of 12**, across all fourteen such edges at 9–49 items each; the two left over
are the `date_today` items, which carry no slot and so have no edge to place. The dozen that
happened to land there were one carrier on one edge (`I'd like the notes {p}{e}`), which is the
whole of why the bucket read its own ceiling. `check_wideonly_edges` fails the build if an edge
is absent from the wide pools — that is a held-out edge, and `evals_heldout` is where it belongs
— or present in the mid ones, where it would be treated on both arms and the pair would agree
whatever the model did; no carrier may be a wide training template either, since the treated
side of this comparison is the checkpoint that read them.

The reading is three-way and every checkpoint it needs is already trained: `mix_v1` (four seeds)
and `mix_v1_mid` (two) are both untreated on these edges and are the transfer test, `mix_v1_wide`
(four) is treated and is the positive control. **If the control does not separate, the arm has no
sensitivity and a flat transfer result means nothing** — which is the failure this bucket has
already had once, at n=12, and the reason the control is stated before the result rather than
after. The arm's seed spread is unmeasured, so nothing may be read off it against a
paraphrase-arm floor; that is the thirtieth finding applied to an arm that postdates it.

### What replicates

`temporal.copy` reads **352/353** on the mid arm's first seed under paraphrase — the third
checkpoint in the project to move on that row, after one `mix_v1_wide` seed frozen and one
`mix_v1` seed under paraphrase. Three of ten checkpoints now, one item each. The thirtieth
finding's retirement of that row as *definitionally* invariant holds up.

`tool.selection` spreads **16 frozen** over two seeds here (157 and 141), which is inside the
44 and 36 the two four-seed families gave and one more corpus family agreeing that the row is
not readable.

### What this does not settle

- **Two seeds are a range and not a floor**, and the ranges above are doing the work. The mid
  arm's treated bucket overlapping the wide arm's is the claim, and two points against four is
  the weakest form of that comparison this project has run.
- **Nothing below 12 was tried.** The knee could be at 8 or at 7; all this shows is that it is
  not between 12 and 24. The base pool's 6 is the only point known to be insufficient.
- **The rule chose the edges, and it chose well by accident.** A different half of the wide
  additions would cover a different number of carriers, and how much of the 86% is the rule and
  how much is English is not separated here.
