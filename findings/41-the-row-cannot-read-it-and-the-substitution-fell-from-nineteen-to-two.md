# Too noisy to read; underneath, wrong contact names fell 19 to 2

**Full result:** The row cannot read this arm, and underneath it the substitution fell from 19 to 2

**Cost:** 4.4 min of scoring on the 1 card first cited here (`nano20m_v1_seed3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`configs/mix_v1_toolnames.py` ×2 against `mix_v1` ×2. One file swapped in a 0.62% slice:
`tools.txt` → `tools_names.txt`, same weight to the token, contact book 28 hand-written names →
4,000 composed ones at 1.81 uses each.

## The row is a null, and the reason is the baseline rather than the arm

| | mix_v1 s1 | mix_v1 s2 | toolnames s1 | toolnames s2 |
|---|---|---|---|---|
| `tool.name_fidelity` /120 | 64 | **33** | 53 | 39 |

Baseline [33, 64], arm [39, 53]. Fully overlapping, and the arm's range sits *inside* the
baseline's.

**The baseline's own two-seed spread is 31 of 120.** That is wider than any effect this arm could
plausibly have had, so the row cannot read it — this is the thirtieth finding's rule arriving on
a new row: a floor is a property of the arm, not of the row, and nobody had measured one here.
The plan quoted "56/120 wrong at 29.6M" from a single seed. The second seed reads 87/120 wrong.
**That number should not have been quoted without an interval and this finding is the correction.**

The controls are no better behaved: `tool.copy` reads [100, 100] baseline against [77, 100] arm,
and `tool.copy_wide` [276, 279] against [252, 289]. One arm seed dips on each, different seeds
each time. Nothing here supports the pre-registered "bought fidelity with copy discipline" trade,
and nothing here rules it out either.

## Underneath the row, the mechanism moved and is measurable

`score_name_fidelity`'s failure buckets are defined against `corn/tools.py`'s `CONTACTS`, which
is the *training* book for `mix_v1` and **not** the training book for this arm. So a substitution
out of the composed book lands in `wrong_name` and the buckets are not comparable across the two
corpora. Re-running the 120 items and classifying each emitted contact against both books
directly:

| checkpoint | correct | **named a real trained contact** | a string from neither book | no readable call |
|---|---|---|---|---|
| `mix_v1` s1 | 64 | **19** | 27 | 10 |
| `toolnames` s1 | 53 | **2** | 54 | 11 |
| `toolnames` s2 | 39 | **10** | 53 | 18 |

**19 → 2 and 10.** That is the failure the eval exists for, and it is the dangerous one: the
runtime texted Omar Silva and reported success. Fluent, schema-valid, wrong person. `tool.selection`
and `tool.validity` both pass it.

What replaced it is `neither book`, 27 → 54 and 53 — strings that are nobody. Those fail visibly,
and `CopySpec` blocks them at inference. So the arm **changed which way he is wrong** without
changing how often, and the direction of that change is the operationally useful one.

## The honest position

- **The pre-registered question reads null** and is reported as null. The arm did not move
  `tool.name_fidelity`.
- **The mechanism it was aimed at moved by an order of magnitude**, on a row the pass rate cannot
  see, in a bucket the frozen scorer cannot separate for this corpus.
- Both statements are true at once, and the second does not rescue the first.

This is the same shape as `temporal.outcome`: a row that sums outcomes with opposite operational
meanings reports a wash, and the split is where the result is. The difference is that
`temporal.outcome` is now a first-class row and this is a script run by hand.

## What this does not settle

- **Whether it is a cardinality effect at all.** The plan pre-registered an unmoved row as "the
  fourth test of the fourteenth finding's rule and the first to fail it". That reading is *not*
  available, because the substitution count did move — what failed is the row, not the rule.
- ~~**Two seeds against a baseline whose spread is 31.** More baseline seeds are the only thing
  that makes `tool.name_fidelity` quotable at all, and they cost 17 minutes each. Nothing on this
  row should be quoted until they exist.~~ **Done, and they cost nothing** — the forty-third
  finding. `nano20m_v1_seed3` and `_seed4` were already trained and had simply never been scored
  on the frozen set with the three `--add` files present. At four seeds the baseline reads
  **33, 37, 44, 64**, spread still 31, and the arm's [39, 53] is still strictly inside it. This
  finding's conclusion is unchanged and is now measured rather than inferred from two points.
- **The scorer's buckets are corpus-relative and silently so.** `substituted_nearest` and
  `substituted_other` mean "a name from `CONTACTS`", which stops being the training book the
  moment an arm changes it. A row whose failure labels depend on a table the arm is allowed to
  move is a row that will mislead again. Fixing it means a new bucket rather than a redefinition,
  on the `--add` terms, and it is not done here.
- **The `neither book` strings were not inspected.** Whether they are near-misses of the asked-for
  name, garbled composed names, or something else is a question this data can answer and nobody
  has asked.
