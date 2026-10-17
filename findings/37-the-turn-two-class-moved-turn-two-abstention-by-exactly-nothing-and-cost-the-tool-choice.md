# Thirty-seventh finding — the turn-2 no-call class moved turn-2 abstention by exactly nothing, and took 17 items of tool choice with it

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v1_chat`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Two seeds of `configs/mix_v1_chat2.py` against the two `nano20m_v1_chat` seeds. The
intervention is `data/raw/chat2.txt` — 94,844 two-exchange no-call transcripts — at **a 25th of
one pass**, 318,873 tokens, 0.24% of the budget. The corpus rationale, the 89.3% it refuses and
the overlap that bounds it are in the mix config.

**This is a negative result with a cost attached, and it is the outcome the config
pre-registered as "the reflex is upstream of the corpus class".**

## The control passed, so the rest is readable

`register.conv` — baseline **[77, 82]**, arm **[79, 80]** of 200. Fully overlapping. The
twenty-fifth finding priced this row at exactly this dialogue share against a 1.0-point floor,
and a 0.24% perturbation moving it would have meant a broken build rather than a hypothesis.
Total dialogue tokens are 26,186,876 in both corpora by construction.

## Turn-2 abstention did not move. At all.

`turn2.second`'s 19 out-of-scope items are the only ones on that row where the right answer is
no call. `called_anyway` is the failure:

| | baseline s1 | baseline s2 | arm s1 | arm s2 |
|---|---|---|---|---|
| `called_anyway` | **19** | **19** | **19** | **19** |

**Nineteen of nineteen, in every cell, on both sides.** The class the corpus was missing was
added, in the position it was missing from, and the behaviour it was supposed to buy is at
complete floor before and after. There is no seed spread to argue about and no margin to size:
the number is the ceiling of the row and it did not change by one item.

That is the third time this project has added a no-call class and watched the reflex survive.
The thirty-fourth finding's `absent` failed at 128 hand-written refusals; the thirty-fifth
succeeded at turn 1 and is the reason this arm was worth running; this fails at turn 2. The
pair the thirty-fifth finding's config anticipated — "it would be the second no-call
intervention to fail and the pair would be the finding" — has arrived, and the honest reading
is that **turn-1 and turn-2 abstention are not the same behaviour**: one moved off floor on a
5% slice and the other does not move on a slice occupying the same structural position.

## And the tool choice got worse, decisively

`turn2.second` overall:

| | baseline s1 | baseline s2 | arm s1 | arm s2 |
|---|---|---|---|---|
| pass | 168/200 | 166/200 | **147/200** | **149/200** |

Ranges **[166, 168]** against **[147, 149]** — non-overlapping, margin **17**, within-arm
spreads **2 and 2**. This clears the spread that produced it by more than eight times, which
none of the thirty-sixth finding's four controls managed and which makes this the readable
number on the scorecard.

**The failure mass is wrong-tool, not over-abstention**, and the distinction is checkable
because `score_selection` has no separate reason for declining an item that wants a call — a
model that says something instead of calling produces no parseable call and scores
`unparseable`. That bucket moves **+4 and +3**. The rest is tool choice:

| reason | base s1 → arm s1 | base s2 → arm s2 |
|---|---|---|
| `chose_send_text` | 6 → 11 | 0 → **21** |
| `chose_save_note` | 3 → 11 | 10 → 0 |
| `chose_web_search` | 2 → 6 | 0 → 4 |
| `unparseable` | 2 → 6 | 3 → 6 |

So the slice did not make him quieter at turn 2. It made him **worse at picking which tool**,
while leaving the one behaviour it targeted untouched. 0.24% of the budget bought a 17-item
regression on a row eleven findings paid for.

## `turn2.first` says nothing, and says it loudly

Baseline **[159, 160]**, arm **[161, 174]**. The margin is **1** against a within-arm spread of
**13**. INSIDE SPREAD — no claim, in either direction.

Worth recording anyway: the arm's spread on this row is **thirteen times the baseline's**. Two
seeds cannot tell a genuinely less stable arm from an unlucky draw, and the thirtieth finding's
rule is why this is a note rather than a result.

## The register gap narrowed, and this is the one place the thirty-sixth finding earns out

`turn2_reply`, `talk − tool` distinct-3 at an identical length histogram, differenced against
the same matching at turn 1:

| | baseline s1 | baseline s2 | arm s1 | arm s2 |
|---|---|---|---|---|
| matched DiD | +0.0573 | +0.0547 | **+0.0135** | **+0.0123** |

Baseline **[+0.0547, +0.0573]** against arm **[+0.0123, +0.0135]**: margin **0.0412** against
within-arm spreads of **0.0026 and 0.0012**. That is a separation of more than fifteen times
the spread — far cleaner than anything the thirty-sixth finding could establish about the gap's
size, and readable *only* because that finding first showed the gap survives length matching.
Quoting the raw cells here would have been quoting a length difference: **the arm's median
reply after a `tool` preamble falls from 11 words to 8.**

**Which cell moved is not established.** The absolute numbers point at the `tool` cell rising
toward `talk` (0.8680/0.9154 → 0.9066/0.9381) rather than `talk` falling (0.9456/0.9500 →
0.9449/0.9520), which would make this the one thing the arm improved. But that comparison is
arm-against-baseline *within* a cell and is **not** length-controlled, and the median dropped
by three words in exactly that cell — which is the confound the thirty-sixth finding exists to
police. The narrowing is established; its mechanism is not. `terminated` is 200/200 in every
cell of every checkpoint, so nothing collapsed.

## What this does not settle

- **The dose.** 1/25 of one pass is one point. But `chat2.txt` shares **100% of its openings
  and 99.3% of its first exchanges** with `chat.txt`, so a bracket above ~1/8 would be testing
  duplication as much as the class. A larger dose needs `chat2` re-cut from a region
  `chat.txt` does not use — a corpus rebuild, not a weight change.
- **Whether the cost is the class or the duplication.** At this dose ~3,767 openings go from
  one use to two. That is 1.9% of `chat.txt`, and the pool moves from 1.19 uses per distinct
  reply to ~1.21 — well inside the bar — but the arm that would separate "the turn-2 class hurt
  tool choice" from "re-reading 1.9% of turn 1 hurt tool choice" has not been run.
- **Whether turn-2 abstention is reachable at all.** Three interventions, one success, and the
  success was at turn 1. Nothing here says a bigger turn-2 slice would work; the 19/19 is
  equally consistent with the reflex sitting upstream of any corpus fix, which is what the
  thirty-fourth finding concluded about `absent`.
