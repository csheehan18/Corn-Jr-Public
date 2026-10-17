# Fifty-second finding — the corpus taught twenty-five phrasings and four of them carry the tool

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`harness/searchgrid.py` against `corn_jr_260m`, run 2026-08-24 on the 3080.
400 turns in 135s: 25 templates × 8 subject shapes × {invented, real}, against
a table-backed instance at temperature 0 with `decline` offered. Nothing left
the machine — routing and argument extraction both happen before the tool
runs, which is why this grid needs no `--search`.

**It started as a complaint about one turn.** Talking to a live instance,
"how tall is Mount Everest" came back `decline` while `web_search` sat in the
declared set and the answer he had just given to "what can you do" promised
lookups. Fifteen natural questions scored **4 of 15**, and every one of the
four opened "look up".

## The obvious reading was wrong, and a longer list would have kept it

The reading was: he learned the imperative and not the question. It survives a
list of any length, because a list of natural questions is a list of real-world
subjects in whatever phrasings occurred to the person writing it. It does not
survive a grid.

| template | invented | real | | template | invented | real |
|---|---|---|---|---|---|---|
| `google {q}` | 8/8 | 7/8 | | `search {q}` | 3/8 | 1/8 |
| `could you look up {q}` | 7/8 | 7/8 | | `check {q}` | 2/8 | 1/8 |
| `can you look up {q}` | 7/8 | 6/8 | | `search for {q}` | 2/8 | 1/8 |
| `look up {q}` | 7/8 | 6/8 | | `can you find out {q}` | 2/8 | 0/8 |
| `do you know {q}` | 5/8 | 3/8 | | `look {q} up for me` | 2/8 | 0/8 |
| `what's {q}` | 5/8 | 3/8 | | `quick, {q}` | 1/8 | 0/8 |
| `do me a search for {q}` | 5/8 | 1/8 | | `what is {q}` | 1/8 | 0/8 |
| `tell me {q}` | 4/8 | 4/8 | | `any idea what {q} is` | 0/8 | 0/8 |
| `find me {q}` | 4/8 | 3/8 | | `have a look for {q}` | 0/8 | 0/8 |
| `look for {q}` | 4/8 | 3/8 | | `see if you can find {q}` | 0/8 | 0/8 |

**Grammatical class explains none of it.** `search for {q}` names the tool in
the imperative and scores 2 of 8; `what's {q}` only implies it and scores 5.
`have a look for {q}` and `see if you can find {q}` are imperatives and score
zero in both worlds. What the four winners share is a lookup verb, short, at
the front — `google`, and three spellings of `look up`. Every phrasing that
buries the verb behind a hedge is at or near the floor, and three of the
twenty-five never route at all.

So the corpus offers twenty-five phrasings at roughly equal frequency and the
weights kept about four of them. This is the twenty-eighth finding's phrasing
effect, measured on the tool it matters most for and at a resolution no eval
row has: `evals/` scores a frozen prompt set, so it reads whatever phrasings
were sampled into it and cannot see the distribution behind them.

## The subject matters as much as the phrasing, which nothing predicted

| subject shape | invented | real |
|---|---|---|
| `the length of the …` | 21/25 | 11/25 |
| `the capital of …` | 18/25 | 11/25 |
| `the official language of …` | 17/25 | 9/25 |
| `the discoverer of …` | 14/25 | 11/25 |
| `the currency of …` | 7/25 | 5/25 |
| `the population of …` | 5/25 | 4/25 |
| `the melting point of …` | 4/25 | 1/25 |
| `the river that runs through …` | 1/25 | 1/25 |

Twenty-one of twenty-five down to one of twenty-five, across shapes that
appear in `FACTS` 700–1,200 times each. Whatever this is, it is not
frequency in the corpus, and no instrument in the project was looking at it.

## The real/invented split is the smallest of the three, and it is the one that was predicted

Pooled: **invented 87/200 (44%), real 53/200 (26%)**, a 17-point gap that
holds in nearly every row of both tables.

This is the fiftieth finding one step earlier in the turn. That one showed a
real entity reopens the weights when he *speaks* — handed `answer: "Augusta
Ada King"` for `look up Ada Lovelace` he produced 700 characters of invented
biography. This shows a real entity also makes him less likely to *reach for
the tool at all*.

It matters more than 17 points sounds, because the two columns are not equally
occupied. `FACTS` is 8,697 invented entries, so every search row the project
has ever scored sits in the left column. The right column is where every
question a user actually asks lands, and until this grid nothing measured it.

## Two things that are working, and are worth recording as such

**The argument is right whenever the call is made: `kept_subject` 140/140.**
Every `web_search` he emitted across 400 turns carried the subject that was
asked about. He reshapes the span — `look up Ada Lovelace` produced
`ada-lovelace`, a URL slug — and the subject survives it. The copy slot is not
the problem; routing is the whole problem.

**The misses are refusals, not wrong actions: `decline` 258, `place_call` 2.**
On this axis he declines rather than misroutes, which is the safe failure.

## `decline` is the symptom and not the cause

The fifty-first finding's `routed` 6/16 → 11/16 under `--no-decline` invites
the reading that withholding the escape fixes the routing. On this class it
does not. Six real-subject questions, `what's {q}`:

    decline offered    web_search 1/6   decline, place_call, web_search, decline, decline, decline
    decline withheld   web_search 1/6   save_note, place_call, place_call, place_call, save_note, web_search

Identical, and withholding it converts five refusals into five wrong tools,
three of which write to disk. Live, the same substitution turned "read back
what happened today" into a `save_note` that saved the question itself. The
escape is not what is stopping him reaching `web_search`; it is where he goes
because he is not reaching it.

## What this cannot say

**Nothing about the answer half.** The grid stops at the call. Whether he reads
a *real* result back faithfully is the fiftieth finding's subject and needs
`--search`, and it is the harder half — a real answer competes with the weights
in exactly the regime this finding shows also degrades routing.

**Nothing about why a shape is hard.** `the river that runs through …` scores
1/25 and `the length of the …` scores 21/25 at comparable corpus frequency.
The grid measures the effect and does not explain it.

**One checkpoint, one seed.** The invented subject per shape is drawn seeded
from `FACTS`; a different `--seed` draws a different grid, and nothing here
establishes the spread across draws.

## What follows

The corpus does not need more search transcripts — it needs the ones it has to
stop being concentrated in four phrasings and eight shapes, and it needs a
share of subjects the model has priors about, which every slice in the project
has deliberately avoided since the thirteenth finding. That avoidance was right
for the reason it was adopted, and this is its bill: a search index too small
to memorise also taught him that lookups are about things that do not exist.

The grid is the instrument for reading whether the next run fixed it, and its
invented column is the control that says whether a bad number is a bad
checkpoint or a hard cell.
