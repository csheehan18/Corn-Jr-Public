# Fourteenth finding — the same bug, a third time, and the rule it settles into

DATA.md §4's structured-formats slice is 10% of the budget, for "schema-constrained decoding
(§6) needs priors". `corn/structured.py` generates it: a form declares some fields and types,
writes the values out as bare text, and the model builds the JSON object. One right answer,
fully checkable, and no sentences in it — so unlike the tool slice it can be generated to its
full declared share at one pass, which no §4 slice had managed before.

**The first version scored 0/200 and the failure was not what the number suggests.**

| | floor | first slice | **rebuilt slice** |
|---|---|---|---|
| `schema.conform` | 0/200 | 0/200 | **194/200** |
| parses as an object | 0/200 | 101/200 | — |
| values right, ignoring keys | 0/200 | **83/200** | — |
| key qualifiers from *training* | — | **308 / 318** | — |
| key qualifiers from the *declaration* | — | **0** | — |

The first slice taught the transformation and not the copying. It punctuated JSON correctly,
quoted strings, left integers bare, and got the values exactly right in 82% of everything it
parsed — then wrote `segment_weight` where the declaration two lines above said
`beacon_weight`. **Not one key in 318 used a held-out qualifier.**

The cause was mine and it was the twelfth finding's cause exactly: field names came from 20
qualifiers × 20 nouns, so each qualifier appeared ~170 times and the *set* was memorisable.
Substituting a training qualifier was a strategy that worked on the training distribution, so
the declaration never had to be read — the same sentence as "a model can score 100% on
`web_search` without ever reading `<|obs|>`", one slice over.

Rebuilt with 5,400 invented qualifiers per side at ~13 uses each, against real shared nouns,
the row reads **194/200**, and the six remaining failures are `missing_key 5` and
`wrong_value 1`. **Zero `not_json`, zero `wrong_type`, zero `wrong_order`.**

### The rule, now that it has cost three findings

> **Any span the model is supposed to copy must come from a space too large to learn as a set.**

Three instances, each found by measurement rather than by inspection, and each looking like a
different problem at the time:

| | what was copied | space | exposures | result |
|---|---|---|---|---|
| twelfth | a search answer | 28 facts | 107 | 0/120 → 120/120 when rebuilt |
| fourteenth | a field name | 400 names | 170 | 0/200 → 194/200 when rebuilt |
| sixth | a year | `ANCHOR_END` is one value | — | every failure clamps to it |

The sixth finding is the same shape read backwards: the year was the one field of the tool's
answer that did *not* vary in training, and it was the only field the fine-tuned models got
wrong. A constant is a set of size one.

What makes this a rule rather than three anecdotes is that the failure is invisible in
training loss and invisible in the slice — both corpora are exactly correct, and a checker
that verifies every record against its declaration passes on both. It surfaces only as a
behaviour row reading zero, weeks later, on an eval built to catch something else.

### So it is a guard now, not a lesson

`scripts/check_copyable.py` runs over every slice in `data/raw/`. Each declares where it asks
the model to copy; each declared slot is measured for *effective cardinality* — the perplexity
of its value distribution, so a slot where one value covers half the mass does not score as a
full one. **An undeclared slice fails rather than passes.** That is the part that would have
prevented all three: nobody forgot to check the cardinality, they forgot that cardinality was
a thing to check, and a corpus that cannot be added without declaring its copy slots removes
the opportunity. `--propose` mines candidates for a new slice by finding substrings carried
between two lines of the same example, which is the copy relation stated directly.

**The thresholds are validated on every run rather than trusted.** The guard rebuilds the two
corpora that actually shipped the bug — the 28-fact index and the 400-name vocabulary — and
asserts it still calls them memorisable (5 and 394 effective values), then asserts it still
accepts the rebuilt one (42,181). A detector that has quietly stopped detecting is the same
failure mode as the fixture that quietly stopped testing, three sections up.

Building it corrected the rule twice. **It is cardinality, not exposure count**: the temporal
slice's 1,442 dates at *122 uses each* read `temporal.copy` 353/353, against 28 facts at 107
uses reading 0/120 — near-identical recurrence, opposite outcomes. And one slot refuses the
rule outright: `contact` has 57 effective values at 101 uses, which should be memorisable, and
`tool.validity` reads 175/181 with **zero of 45 `send_text` items failing on held-out
contacts**. Either the rule is really about whether the target is in the model's general
vocabulary — `Thaddeus` is English, `eskemere` is not — or about whether the mapping is an
identity rather than a lookup. Both are testable and neither is tested, so the guard records
the exception with its evidence instead of tuning the threshold until it disappears.

### `wrong_type` is zero, which is a claim about Phase 3

VISION §6 wants a model *unable* to emit a malformed call, via grammar-constrained decoding,
and `tool.validity` exists to measure how badly that is needed. This row says something
sharper: given data that requires it, a 25M model gets **every type right on 200 schemas it
has never seen** — quoted strings, bare integers, bare lowercase booleans, bracketed lists.
The constraint layer is still worth building for the guarantee, but it is not carrying
correctness that the corpus cannot supply.

### Three bugs the guards caught, none of which would have raised an error

- **Overcorrection.** Composing both halves of a field name from invented pools made the
  median name **12 tokens**, so a five-field record needed 60 tokens of exact identifier
  copying — the row would have failed for reasons with nothing to do with schemas. Nouns went
  back to being real and shared; only the qualifier is held out, which is also the more
  realistic shape.
- **Form names leaked the holdout.** `form: cororburg_entry` drew from a syllable pool that
  overlapped the qualifier pool, so held-out qualifiers appeared in training as form names. A
  holdout is only as good as the whole file, not the column being held out.
- **Then the leak check was too strict.** `esk`, `hesk` and `mesk` are all onsets, so the
  training identifier `meskemere` *contains* the held-out `eskemere` while being a different
  identifier. Word-bounded matching, the same distinction the `trained_answer` scorer needed.

### What it cost, and what that says about 10%

| | floor | struct |
|---|---|---|
| `tool.copy` | 120/120 | **99/120** |
| `tool.validity` | 175/181 | 168/181 |
| `narrative` nats/byte | 0.3665 | 0.3715 |
| `web` nats/byte | 0.9098 | 0.9174 |

`temporal.copy`, both refusal rows and `tool.selection` are unmoved. But 10% of the budget
spent here costs 21 items of `tool.copy` and about 1% of prose, which is the seventh finding's
"slices compete" showing up for the fourth time. **Whether 10% is the right share is now
exactly the question the eleventh finding asked about the tool slice's 15%, and it has the
same cheap answer available:** run it at 2% and see how much of the 194 survives. §4's shares
were guesses, and two of the six have now been measured to be wrong in the same direction.
