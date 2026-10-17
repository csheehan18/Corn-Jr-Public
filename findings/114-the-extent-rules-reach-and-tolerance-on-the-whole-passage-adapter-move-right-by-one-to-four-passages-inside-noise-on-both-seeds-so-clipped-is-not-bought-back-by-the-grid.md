# Hundred-and-fourteenth finding — the extent rule's reach and tolerance on the whole-passage adapter move `right` by one to four passages inside noise on both seeds, and the CLIPPED they remove turns into wrong answers and silences rather than right ones, so the grid is not the lever for the clip

Replay, 2026-09-05, both seeds, no training. Population A re-harvested from
the two selected checkpoints of finding 112 with the extent grid stored to
radius 8 (`train_reader_whole.py --load ... --radius 8`, 12 s a seed), then
`apply_extent` at every `(d, radius)` in {1, 2, 3} × {3, 5, 8}, bar protocol,
hybrid reduce, paired by passage against the shipped point `(2.0, 3)`.
`evals/results/{reader,pairs}_whole_causal_s{1,2}_popa.json` now carry the
radius-8 grid; the read at radius 3 is byte-for-byte the record's.

## 0. Why

Finding 112's one cost was CLIPPED, 18 → 32 and 23 → 34: a head with the
whole passage in view finds the entity and cuts it short. The extent rule
(finding 85) speaks the longest pair within `d` of the argmax inside a
radius of candidate rows; on the window reader it was worth +8 a seed at
`d = 2, radius 3` and nothing wider (finding 105). Pre-registered before the
read: `d = 2.0` as shipped, radius 5 and 8 against 3; counts if `right` is
up on both seeds with CLIPPED down; the `d` grid printed for information.

## 1. The grid

    seed 1 (baseline 513 right, CLIPPED 32)         seed 2 (baseline 510, CLIPPED 34)
    d    radius  right wrong silent CLIPPED  paired    right wrong silent CLIPPED  paired
    1.0     3     506   134    81     39      -7        507   124    90     38      -3
    2.0     3     513   126    82     32      --        510   123    88     34      --
    3.0     3     510   127    84     32      -3        510   120    91     30       0
    1.0     5     505   130    86     35      -8        505   124    92     39      -5
    2.0     5     515   121    85     26      +2        512   121    88     32      +2
    3.0     5     514   116    91     22      +1        514   116    91     27      +4
    1.0     8     505   131    85     35      -8        506   123    92     38      -4
    2.0     8     514   123    84     30      +1        514   121    86     33      +4
    3.0     8     512   120    89     30      -1        514   118    89     30      +4

Every paired `right` delta is between −8 and +4 with p ≥ 0.08; the largest
positive, +4 on seed 2, is +1 on seed 1. The pre-registered cells are up on
both seeds — (2.0, 5) by +2 / +2, (2.0, 8) by +1 / +4 — and inside the seed
spread, which rule 6 calls not readable.

## 2. Where the clip goes

At (3.0, 5) CLIPPED falls 32 → 22 and 34 → 27, and `wrong` falls 126 → 116
and 123 → 116, yet `right` moves +1 / +4: the widened span is more often a
*different* wrong answer or a refusal than the gold. The extent grid can
only extend the argmax by candidate rows; what the head clips on this arm
is not a missing last word (finding 86's "Matt" for "Matt Monro") but a
different boundary decision the widened neighbourhood does not fix. A
tighter `d = 1` loses 3 to 8 on both seeds at every radius, so the shipped
`d = 2` is not too loose either.

## 3. Verdict

**Closed, both seeds, at the pre-registration.** The shipped constants
(`d = 2.0`, radius 3) stay. Finding 105's result on the window reader holds
on the adapter: the fuller answer is not among the spans the head scores
near its argmax, and CLIPPED on this arm is a training-side matter (the
loss sums every gold occurrence but says nothing about preferring the
longer of two overlapping candidates).
