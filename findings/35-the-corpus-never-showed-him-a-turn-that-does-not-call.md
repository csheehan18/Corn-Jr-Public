# One percent of non-tool turns teaches him when not to call

**Full result:** The corpus never showed him a turn that does not call, and one per cent was the whole of it

**Cost:** 4.0 min of scoring on the 1 card first cited here (`nano20m_v1_chat`); it also reads 2 cards scored for an earlier finding (`nano100m_v1`, `nano20m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The thirty-fourth finding left declining as the gap a runtime has to close elsewhere. This asks
the neighbouring question — not *is this request covered*, but *is this a request at all* — and
answers it with a corpus class that has never existed. Two seeds trained against two baseline
seeds; `configs/mix_v1_chat.py`.

> **Read the ranges, not the cells.** Two of the readings written from the first seed were wrong
> in opposite directions and are withdrawn at the end of this file. A single cell of this arm
> supports neither of the things it appears to say.

## The corpus, counted before anything was built

| slice | share of `mix_v1` | markers | transcripts that do not call |
|---|---|---|---|
| `conversational.txt` | 20% | **none at all** | n/a — 781 MB, not one `<\|user\|>` |
| `temporal.txt` | 9.79% | yes | **0** of 164,263 |
| `structured.txt` | 10% | no `<\|user\|>` | — |
| `tools.txt` | 0.6228% | yes | 1,000 of 10,000 |

Weighted by what the model reads: ~99,000 marked-up transcripts, **~1,000 of them no-call —
1%, at one pass.** The 20% of the budget that makes him conversational carries no markers, so
dialogue is learned as unmarked continuation and `<|user|>` is learned as a cue to emit a call.
The two halves of what §3 wants are learned in disjoint universes.

The 1,000 that exist are not badly built — 132 refusal sentences at 7.6 uses each, which is not
the recitation regime. They still mostly do not survive. Three utterances **verbatim from that
training pool**, through `corn/agent.py` at temperature 0: `put the radio on` refuses cleanly;
`book me a flight` and `please delete my emails` both call a tool.

## The quantity was already in every scorecard, unpooled by nobody

`score_selection` has scored abstention since it was written — `item["tool"]` is `None` for a
request no tool covers and `called_anyway` is its failure reason. Read out of
`evals/results/`, it is at floor on **every checkpoint in the project**: 13 to 19 of the 19
out-of-scope items, across four seeds, two model sizes and nine corpora including one with no
tool slice at all. On `nano100m_v1`, **18 of the 19 items `tool.selection` fails are that one
failure**, so its 181/200 has been read as tool competence when almost all of its error mass is
a single behaviour.

Nothing was wrong with the measurement. It was pooled with a six-way tool choice, it had 19
items, and all 19 asked for an uncovered capability — none was ordinary conversation.
`evals/chat.jsonl` unpools it into three cells of 100, and the third is a control rather than a
measurement: without items that *want* a call, a model that never calls scores 100%.

## The result

Ranges over two arm seeds and two baseline seeds. The thirtieth finding's standard: the two
ranges either overlap or they do not.

| row | `nano20m_v1` ×2 | `nano20m_v1_chat` ×2 | separated? |
|---|---|---|---|
| **`chat.abstain_oos`** | 0, 5 | **7, 29** | **yes** |
| `chat.abstain_talk` | 95, 99 | 100, 100 | by one item |
| `chat.engage` — the control | 100, 100 | 100, 100 | no, and must not |
| **`refusal.say`** /270 | 162, 172 | **188, 196** | **yes** |
| **reply median words** | 8, 8 | **10, 11** | **yes** (corpus 11) |
| reply distinct-3 | .8754, .8814 | .8726, .9052 | no — straddles |
| `register.conv` dialogue | 81, 76 | 81, 77 | no — **the control held** |
| `tool.selection` | 112, 156 | 159, 160 | base spread is 44 |
| `tool.copy` | 100, 100 | 85, 100 | no |
| `tool.copy_wide` | 276, 279 | 263, 283 | no |
| `temporal.route` | 398, 398 | 398, 400 | no |

**The control first, as pre-registered.** Conversational went 20% → 15% unmarked plus 5%
marked, and `register.conv` on the dialogue half reads 81/76 against 81/77. The twenty-fifth
finding priced that row at exactly this share against a 1.0-point floor, the tightest in the
project. It did not move, so the arm is readable. The donor was chosen for this: the new slice
is *made of* the old one, so total dialogue exposure is 20% in both corpora and the only thing
that changes is whether some of those sentences sit behind `<|user|>`.

**`chat.abstain_oos` is the result and its size is not readable.** [0, 5] against [7, 29] does
not overlap, so the direction survives. 7 and 29 is a fourfold spread and no interval can be
quoted from it. More seeds are the one thing that prices this.

**The replies got longer, not more varied.** Median words 8 → 10 and 11 against the corpus's 11
separates cleanly. Pooled distinct-3 does not: the arm's range straddles the baseline's
entirely, and arm seed 2 reads *below* both baselines.

**Cardinality was necessary and was not sufficient.** The slice's replies are cut from SODA
rather than written, at **1.19 uses per distinct reply over 163,287 of them** — `answer`'s
regime (1.2) and the wide toolspace arm's (1.0), not `clarify`'s 2,096. That is the mechanism
the thirty-fourth finding generalised, and it bought a real move on `oos` and on reply length.
It did not buy reply *variety*, which is the first time in this project that getting the
cardinality right has not moved the row it was aimed at.

## The instrument has a ceiling on one class, and it was built to avoid exactly that

`chat.abstain_talk` reads 95 and 99 in the **baseline**. Five items of headroom — which is the
thirty-first finding's complaint about `evals_wideonly` ("twelve items whose untreated range
touches its own ceiling, which answers nothing at any seed count") committed again, by the file
written to prevent it.

The cause is legible in the items. `talk` prompts are long SODA openings ("Mom, what's going on?
Why is the school closing for a week?") and those already read as conversation to an untreated
model. The failures visible in `corn/agent.py` — `good morning`, `did you sleep well?` — are
**short** greetings, and `MIN_USER = 16` plus SODA's opener distribution keeps them nearly out
of the pool. **The row measures the easy end of its class.** Fixing it means a hand-written
short-greeting pool, which is quantised by construction; that is a trade to decide rather than
assume.

## What this does not settle

- **Two seeds**, and `oos`'s spread of 7-to-29 means the effect exists and has no interval.
- **`absent` is a different question and this does not transfer to it.** The thirty-fourth
  finding's `absent` asks whether a request is covered by a *declared list* and fails because he
  invents a tool name rather than running a membership test. This asks whether an utterance is a
  request. Both being no-call classes does not make them one question.
- **`refusal.say` moved and nothing here asked it to** — 162/172 → 188/196, no overlap, ~25
  items, unexplained. It is the loose end most likely to be a real finding.
- **`refusal.say_unechoed` is 0/55 in all four cells**, unmoved, as everywhere.
- **The tool-word screen is a heuristic.** `corn/chatgen.py`'s `TOOL_WORDS` drops any dialogue
  opening that looks like a request a tool covers, because teaching `<|say|>` on "remind me on
  Friday" would train against eleven findings of tool behaviour. It cannot catch a request
  phrased without any of its words, and those transcripts are in the slice.
- **5% is unpriced.** The first point, chosen to make a null readable. The thirty-first
  finding's warning applies in full: interventions here keep turning out cheaper than the arm
  that found them.
- **Multi-turn is untouched.** The new slice is single-turn like every other; no transcript in
  the corpus has a second `<|user|>`.

## Two readings from seed 1, withdrawn

- ~~"He learned that ordinary conversation isn't a request; he did not learn that an uncovered
  request is uncovered."~~ **Backwards.** Seed 1 read `oos` at 7 and `talk` at 100/100, which
  looked decisive until the baseline arrived at 95 and 99 on `talk` — near ceiling all along —
  and arm seed 2 read `oos` at 29.
- ~~"The arm closes 80% of the gap to the corpus on reply variety."~~ **Does not replicate.**
  Read off seed 1's 0.9052 against a 0.9130 corpus reference before a second seed existed.

**And `tool.copy`'s −15 on seed 1 was seed noise.** Seed 2 reads 100/120, identical to both
baselines. The nineteenth finding says that row moves 15.0 points on the seed alone; it did
exactly that, and one cell nearly bought a regression that is not there.

## A separate thing this cost, and it was free to fix

`_invent_held_out_facts` compiled a fresh regex on each of **5,004,876** iterations — 600
candidates × 8,697 train answers × two directions — thrashing `re`'s 512-entry cache against
8,697 distinct patterns. `import corn.tools` took **87.5 seconds**, paid by `corn/agent.py`,
`corn/evals.py`, `corn/chat.py` and all fourteen guard scripts before any of them printed a
character. Compiling once outside the loop takes it to **2.7s**, and the agent from cold start
to two answers from 91.1s to 6.3s.

`FACTS` is in every mix and therefore every checkpoint; `HELD_OUT_FACTS_WIDE` is in
`evals/tool_copy_wide.jsonl`, which fourteen scorecards read. Both are now pinned by sha256 in
`check_tools.py` group 10, against hashes captured **before** the change and verified identical
after. Nothing stood between a well-meaning edit to that generator and every number in the
project quietly ceasing to be comparable.
