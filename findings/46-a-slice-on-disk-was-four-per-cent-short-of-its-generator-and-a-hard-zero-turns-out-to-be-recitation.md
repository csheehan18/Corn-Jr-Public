# Forty-sixth finding — a slice on disk was 4% short of its generator, and the row that finally moved did it by reciting

`configs/mix_v3.py` ×2 — `mix_v2`'s shares to the token with three files swapped for
higher-cardinality twins, aimed at an exposure regime that only exists at 5B. The run was
declared in advance as a **regression check, not a validation**. It found three things, none of
them the thing it was checking for.

## 1. `data/raw/tools.txt` is 4% short of the generator that is supposed to produce it

    file                        transcripts   cold-start examples
    data/raw/tools.txt on disk       10,000                     0
    the same command, rebuilt        10,000                   400
    data/raw/tools_names.txt          9,766                   451

`gen_tools.py` with default arguments emits the `cold_start` class at `KIND_WEIGHTS` 4 of 100.
The file on disk contains **none of it**. `tools_names.txt`, generated 2026-08-18 from the same
generator, contains it — which is how this surfaced at all.

**So no corpus in this project through `mix_v2` has ever contained the cold-start class**, while
`scripts/check_tools.py` group 9 asserts nine separate properties about it and passes. It passes
because it checks the **generator**, not the **file**. DATA.md §11 already recorded that
`tools.txt` "does not regenerate byte-identically at the default seed (7,756 distinct on disk
against 7,754 rebuilt)" and flagged it as a loose end. This is what that drift was, and it was
worth 4% of the slice rather than two transcripts.

## 2. The consequence: a project-long hard zero was an absent class, and moving it is recitation

The forty-third finding, on `refusal.say_unechoed`:

> **`refusal.say_unechoed` is a hard zero.** 0/55 on four seeds of the baseline, both seeds of
> the chat arm, and both sizes. Nothing in this project has ever moved it.

`mix_v3` reads **55/55 on both seeds.** The explanation is not capability:

| corpus | occurrences of the two gold sentences |
|---|---|
| `tools.txt` (in `mix_v1`, `mix_v2`) | **0** |
| `tools_names.txt` (in `mix_v3`) | **902** |

**The 55 items rest on 2 distinct sentences.** The row was built to tell relaying from
reciting, and at two strings appearing ~900 times in training it cannot: a model that memorised
them scores 55/55, and so does one that reads the observation. The honest statement is that the
class entered the corpus for the first time and the row is no longer measuring what its name
says.

This is `say.jsonl`'s declared ceiling arriving in practice. The handoff already recorded that
the file "sits on 18 target sentences" and that 55 of 150 items are answerable without reading
the observation. Two of those 18 carry the whole unechoed cell.

**It also makes `mix_v3`'s tools swap a two-variable change**, which its own config claims is a
one-line cardinality repair. The book went 57 → 3,435 *and* the cold-start class went absent →
present. Nothing on the tool rows in that run is attributable until those are separated, and
`data/raw/tools_cold.txt` — the current generator with the hand-written book — is the cell that
separates them. Built here, not yet trained.

## 3. `refusal.clarify` 47/47 → 40-45/47 is the honest number, and the drop is the result

`mix_v3` reads 45/47 and 40/47 where `mix_v2` reads 47/47. That is not a `mix_v3` effect: the
`sayvar` arm alone reads **40/47 and 47/47** against a baseline of 47/47 on four seeds, so
`mix_v3` reproduces it exactly.

Both corpora contain **all nine** of the eval's clarify strings, so presence is not the
variable. Frequency is:

| corpus | clarify phrasings | uses each |
|---|---|---|
| `temporal.txt` | 8 | 1,620.7 |
| `temporal_sayvar.txt` | 2,548 | 4.5 |

At 1,620 uses each the nine eval strings are memorised and the row passes without reading the
observation. At 4.5 uses each they are not, so the model has to relay — and it relays 40 to 45
of 47 rather than all of them. **`refusal.clarify` at 47/47 was recitation on every checkpoint
that ever reported it**, which `score_say`'s own docstring had already guessed in writing
("exactly as `refusal.clarify` at 47/47 was") without a corpus that could test it.

A better corpus produced a worse number on a row that was measuring the wrong thing. That is the
fourth time in this project — after `tool.selection`, `temporal.route` and `tool.name_fidelity`
— and the pattern is now specific enough to state as a rule: **a row scored by exact match
against a closed phrasing table measures memorisation until the table is large enough that it
cannot.**

### One false number, corrected where it lived

`scripts/check_copyable.py` claimed sayvar's 2,548 phrasings "took `refusal.clarify` to 100%".
They did not — the arm reads 40/47 and 47/47 against a baseline already at 47/47 on four seeds,
so it lowered one seed and moved nothing up. The cardinality claim around it is unaffected and
the number attached to it was wrong. Corrected in place.

## What did go as designed

- **`substituted_composed` fired for the first time**, 3 and 3. The forty-third finding added
  that bucket because `score_name_fidelity`'s labels were silently corpus-relative; `mix_v3` is
  the first corpus to move the book underneath them, and the bucket did the job it was built
  for. `tool.name_fidelity` reads 46 and 56 against `mix_v2`'s 43 and 53 — overlapping.
- **`effect.py` reads OVERLAP on every frozen row** against `mix_v2` except `temporal.route`
  (+1) and `tool.copy_wide` (+2), both with churn unmeasured. The regression check passes.
- **The cardinality repairs measure as intended**: toolspace parameter value 75 → **9,540
  effective at 4.7 uses each**, which is `sayvar`'s demonstrated regime.

## What this does not settle, and one thing it un-settles

- **The repairs are still unvalidated.** Everything here targets an exposure regime that exists
  only at 5B. This was pre-registered and stands: the validation is the cardinality
  measurement, not the checkpoint.
- **`mix_v3` should not replace `mix_v2` yet.** The tools swap is two variables and the
  cold-start class entered by accident rather than by decision.
- **Every `refusal.say` number in the catalogue is now suspect** in the same way
  `refusal.clarify` turned out to be, and for the same reason: 18 target sentences. The
  thirty-third finding's regime argument applies to evals as well as corpora, and nobody has
  swept the eval files for it.
