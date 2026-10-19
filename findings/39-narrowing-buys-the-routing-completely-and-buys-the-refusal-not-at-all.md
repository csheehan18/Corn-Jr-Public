# Restricting names to declared tools fixes routing, not refusal

**Full result:** Narrowing buys the routing completely, and buys the refusal not at all

WS-E stage 1's free pre-reading. **No training.** Two checkpoints already on disk, three cells
over the same items, `n=200` per level and per cell.

The thirty-fourth finding left one recommendation unmeasured. It found that Corn-Jr routes to
declared tools he was never trained on at parity with trained ones, and **cannot decline at all**
— 0/276, inventing a name in 190–216 of them — and it proposed constraining the emitted name to
the *declared* set, estimating that this "turns 78% of these failures into either a declared tool
or no call". It was explicit that this "does not produce a refusal".

Both halves of that are now measured rather than estimated, and one of them was understated.

## The three cells

| checkpoint | cell | name pass | `undeclared_name` | `wrong_declared` | `unparseable` | **`absent` pass** |
|---|---|---|---|---|---|---|
| `toolspace` | none | 95/379 | 263 | 7 | 14 | **0/221** |
| `toolspace` | declared | **238**/379 | 0 | 128 | 13 | **0/221** |
| `toolspace` | decline | 235/379 | 0 | 131 | 13 | **0/221** |
| `toolspace_seed2` | none | 92/379 | 251 | 15 | 21 | **0/221** |
| `toolspace_seed2` | declared | **224**/379 | 0 | 117 | 38 | **0/221** |
| `toolspace_seed2` | decline | 209/379 | 0 | 106 | 64 | **3/221** |

`none` is what every existing scorecard measured: the name is masked against `REGISTRY` and
nothing else. `declared` narrows it to the tools that transcript actually offers. `decline` adds
`decline` to the declaration line — last, on every line including the ones whose answer is a real
tool — and to the mask.

## Narrowing is worth far more than 78%, and the extra is the interesting part

`undeclared_name` goes to **0**, which is by construction and is not the result. What is the
result is where the mass lands. On the `domain` level, seed 1: 116 invented names become **52
correct calls** and 63 wrong-but-declared ones. Pooled over three levels, narrowing converts
**+143 and +132 of 379** into the *right* tool.

So the thirty-fourth finding's estimate was conservative in a way that matters. It said the
failures become "a declared tool or no call"; about **45%** of them become the tool that was
actually asked for. On the two hardest levels the row goes from **0/120 and 0/128 to 89/120 and
52/128** — from a floor to something worth reading, with no training and no corpus.

This is the largest behavioural change in the project bought by inference alone.

## And it buys no refusal whatsoever

**`absent` reads 0/221, 0/221, 0/221, 0/221, 0/221 and 3/221.** Three items, all on one seed, one
per level. Against a baseline of 0 that is not a signal; against 442 items it is 0.7%.

`decline` was declared on every line, rendered in `corn/toolspace.py`'s own shape, positioned
last so its presence carried no cue, and the mask left it open as the **only** name available
that was not a wrong answer. He still called a wrong tool 218 times out of 221.

There is no membership test to strengthen and no escape he was failing to find. The behaviour is
absent rather than blocked, which is what the thirty-fourth finding said and what this rules out
any cheaper explanation for.

## What it cost, which is not nothing

Adding a seventh name to the enum cost name accuracy on both seeds: 238 → 235 and 224 → 209.
Seed 2's `domain` cell is where it concentrates, `unparseable` 38 → 64.

The direction is consistent and the size is not readable at two seeds — −3 against −15 is a
spread wider than either number. What can be said is that it is a cost rather than free, and that
it lands on the level with the widest name space, which is where an extra competing name would be
expected to hurt.

## What this bounds for stage 2

The pre-reading was built to be worth having whichever way it read, and the way it reads is
useful:

- **The corpus has to teach the behaviour; the grammar cannot hand it over.** Stage 2's arm is
  not optional and its null is not pre-empted. If `absent` moves there, it moved because the
  corpus taught routing-to-`decline`, not because the escape became available.
- **Narrowing should ship regardless of what stage 2 reads.** It is free, it is large, and it is
  independent of the refusal question. `corn/agent.py` already does it as of WS-E stage 1.
- **The seven-way enum's cost is now a known quantity** and stage 2's name rows have to be read
  against `declared`, not against `none`, or the arm will be charged for a cost this pre-reading
  already priced.

## What this does not settle

- **These checkpoints were never trained on the name.** A model that has never seen `decline` in
  any position has no reason to emit it, and this measures exactly that. It is a bound on what
  the grammar can do alone, not evidence about what the corpus can do.
- **Two seeds, one corpus family, `n=200` per level.** The `absent` denominator is 221 per
  checkpoint-cell rather than the 276 the thirty-fourth finding used, because the constrained
  decode is eager per token and 400 was not worth the wall clock for a row reading 0.
- **`wrong_declared` is not analysed here.** Narrowing converts invented names into declared ones
  and slightly under half of those are correct; which of the declared tools the other half pick,
  and whether that is a near-miss or a coin flip, is a question this cell can answer and nobody
  has asked it yet.
- **The option-C grammar is name-narrowing only.** A declared tool the registry has never heard
  of is held to well-formedness rather than to its declaration's parameter list, so nothing here
  speaks to whether constraining *parameters* from the declaration line would buy anything.
