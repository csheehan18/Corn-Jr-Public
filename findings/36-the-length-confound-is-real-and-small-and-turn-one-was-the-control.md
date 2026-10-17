# Thirty-sixth finding — the length confound is real, it is small, and turn 1 was the control sitting in the file the whole time

**Cost:** 8.0 min of scoring on the 2 cards first cited here (`nano20m_v1_chat_seed2`, `nano20m_v1_seed2`); it also reads 2 cards scored for an earlier finding (`nano20m_v1`, `nano20m_v1_chat`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The handoff that opened `turn2_reply.*` named the thing that stopped it being a claim: replies
after a `talk` preamble are **longer** than after a `tool` one — median 7/8, 7/10, 11/12, 11/12
across the four checkpoints — and pooled distinct-3 is not independent of length. *"A
conversational preamble carries register into the next turn"* and *"a conversational preamble
makes him say more"* both fit every number in that table, and it said so rather than picking one.

This is the length-controlled read. **The confound is real, it inflates the gap by roughly 0.005
to 0.015, and the gap survives removing it on four checkpoints of four.** No GPU was needed for
the analysis and none of the published numbers moved.

## Nothing was re-generated, and that is checkable

`_reply_aggregate` was already pure — "no model, no rng, no clock" — and `_reply_records` seeds
generation to `seed + i` per item index. So retaining every reply instead of `max_samples`' eight
cannot change a scored quantity, and re-scoring the four checkpoints reproduces **every aggregate
in every cell to the digit: zero mismatches** across `first`, `second`, `first_by_preamble` and
`second_by_preamble` on all four. The `records` block added to `evaluate_turn2_reply` is the whole
change, and it makes every future length question a re-analysis rather than another 4× pass.

`HARNESS_VERSION` stays 1. No scored quantity changed meaning; a field was added beside them.

## The second confound, which the handoff table did not mention

The 200 utterances are **disjoint between the cells** — 100 carry a `tool` preamble, 100 carry a
`talk` one, and `check_evals.py` asserts no utterance appears in both. So the raw `talk − tool`
column is partly a difference between two sets of openings rather than between two preambles.

The control for it was already in the harness and unused: `first_by_preamble` scores those same
two item sets **at turn 1, where there is no preamble at all**. Differencing it out is the
difference-in-differences, and it matters — at turn 1 the item sets do not favour `talk`
consistently, and on `nano20m_v1` they run 0.9332 against 0.9056 the *other* way.

Length is a separate problem and DiD does not touch it, because the length gap is **created by
the preamble** rather than inherited from the items: the medians are equal or near-equal at turn 1
and split only at turn 2.

## Four reads of the same contrast

`talk − tool` distinct-3 at turn 2, within checkpoint. `matched` is exact length-distribution
matching — for each reply length take `min(count_tool, count_talk)` from each cell, so both sides
carry an identical length histogram and therefore an identical trigram-pool size.

| checkpoint | med w | raw | DiD | matched | [p5, p95] | kept | matched t1 | matched DiD |
|---|---|---|---|---|---|---|---|---|
| `nano20m_v1` | 7/8 | +0.0818 | +0.1094 | **+0.0664** | [+0.0379, +0.0924] | 70 | −0.0286 | +0.0949 |
| `nano20m_v1_seed2` | 7/10 | +0.0619 | +0.0397 | **+0.0491** | [+0.0245, +0.0716] | 65 | +0.0025 | +0.0466 |
| `nano20m_v1_chat` | 11/12 | +0.0345 | +0.0506 | **+0.0344** | [+0.0180, +0.0492] | 72 | −0.0229 | +0.0573 |
| `nano20m_v1_chat_seed2` | 11/12 | +0.0777 | +0.0596 | **+0.0702** | [+0.0583, +0.0808] | 79 | +0.0155 | +0.0547 |

**Positive on 4 of 4 under every control, and the draw interval never crosses zero.** The matched
gap is *smaller* than the raw gap on three of four and unchanged on the fourth, which is the size
of the confound: it was real and it was worth ~0.005–0.015, not ~0.05.

**The `matched t1` column is the sharpest thing here.** Length-matched, with no preamble in front
of either cell, the `talk` items carry no advantage at all — two of four are negative. The gap
appears exactly when the preamble does.

## What this does not license

| quantity | range across 4 | within-arm seed spread | verdict |
|---|---|---|---|
| raw | [+0.0345, +0.0818] | 0.0431 | direction holds, size unresolved |
| DiD | [+0.0397, +0.1094] | 0.0696 | direction holds, size unresolved |
| matched | [+0.0344, +0.0702] | 0.0358 | direction holds, size unresolved |
| matched DiD | [+0.0466, +0.0949] | 0.0483 | direction holds, size unresolved |

**Not one of the four clears the seed spread that produced it.** `scripts/effect.py`'s argument
applies here unchanged — two seeds are a spread and not a standard deviation — so what this finding
adds is that *length does not explain the gap*, and **no interval for its size exists**. The
thirtieth finding's rule is the reason this table is printed rather than a single number.

**This is a within-checkpoint contrast and is not the trap.** The handoff's standing caution is
about the `tool` cell separating *arm from baseline* at a margin of 0.0106 against a within-arm
spread of 0.0474. Nothing above quotes that comparison. `talk` against `tool` inside one
checkpoint is a different contrast with a different denominator.

## The mechanism that would have explained it away, ruled out

The obvious way length produces this without any register story: short replies are where canned
text lives, twenty replies of "Okay." share every trigram they have, and the shorter cell scores
low for being repetitive rather than for being flat.

**It is not happening.** Duplicate-reply rate in the `tool` cell is 0.010, 0.020, 0.010, 0.030 —
the most repeated reply in any cell appears **two or three times in a hundred** (`"i'm doing"`,
`"i don't have a problem"`, `"of course what's up"`, `"not much what's up with you"`). The `talk`
cell is 0.000–0.020, i.e. the same. Whatever the `tool` cell is doing worse, it is not saying the
same sentence repeatedly, and the diversity difference is finer-grained than verbatim repetition.

## The one read that dissents, kept because it does

Truncating every reply to its first `K` words gives each one exactly `K − 2` trigrams:

```
nano20m_v1             3:+0.155  5:+0.184  7:+0.167  9:+0.122  11:+0.008  13:-0.013  14:-0.038
nano20m_v1_seed2       3:+0.055  5:+0.091  7:+0.078  9:+0.099  11:+0.057  13:+0.069  16:+0.007
nano20m_v1_chat        3:-0.010  5:+0.047  7:+0.049  9:+0.060  11:+0.010  13:-0.033  16:+0.003
nano20m_v1_chat_seed2  3:+0.168  5:+0.131  7:+0.074  9:+0.067  11:+0.071  13:+0.065  16:+0.046
```

The gap is large in the opening words and **decays toward zero, crossing it on two of four
checkpoints by `K ≈ 12`**. Two readings fit: the effect lives in how he *opens* the second turn
and washes out once enough of the reply is read, or the long tail is thin and this is the sample
shrinking. Both are consistent with the matched read, which is why the matched read is the
headline and this one is printed underneath it rather than averaged in.

## What it costs to go further

Nothing, for the re-analysis: `scripts/length_control.py` reads the retained records and the four
result files are on disk. Sizing the effect needs more seeds, and the thirty-first finding is the
standing warning about what that buys — this one does not claim the extra seeds are worth it.

    .venv/Scripts/python.exe scripts/length_control.py \
        --base nano20m_v1 nano20m_v1_seed2 \
        --treat nano20m_v1_chat nano20m_v1_chat_seed2
