# Second-turn behaviour installs; compound requests forget how to stop

**Full result:** The second turn installs on both vehicles, and the compound one buys composition by forgetting how to stop

**Cost:** 2.1 min of scoring on the 1 card first cited here (`nano20m_v3_compound_seed3`); it also reads 1 card scored for an earlier finding (`nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Eight nano arms trained 2026-08-27 from `configs/mix_v3_turn2.py`,
`configs/mix_turn2_ft.py`, `configs/mix_v3_compound.py` and
`configs/mix_compound_ft.py` — two families, two vehicles, two seeds each, plus
both `ckpt.pt` and `last.pt` on every fine-tune. Pre-registered in
`docs/PLAN-TURN-2.md` and built to `docs/PLAN-TURN2-BUILD.md` before a byte
trained. Controls are the four already-scored `nano20m_v3` seeds; **nothing
retrained and nothing was re-scored**, and nothing in the scoring path moved
this session — `corn/evals.py` and the four eval files are untouched since the
`__turn2rows` cards were written, which is checkable in the log rather than
asserted here.

## The question, and the absence it was aimed at

Multi-turn was the one capability class with no positive finding, and the
2026-08-27 baseline read said why: `turn2.reask` a hard **0/96 on all twelve
checkpoints**, `turn2.chain_result` 0/50, both compound second stages 0/48 with
`said_instead` at exactly 48/48. Finding 71's signature — a corpus absence, not
a weak capability. Every trained second turn in the corpus called a tool, so
there was nothing to surface.

Two payloads now contain the missing turns, and each gets finding 60's vehicle
experiment: the same bytes as a 5% slice of the v3 mix, and as a fine-tune over
the frozen base with 1:1 mix replay, payload exposure equal to 0.054%.

## The turn-2 family: it installs, and the vehicle verdict splits by class

Four control seeds, then two seeds of each arm. `last.pt` reproduces `ckpt.pt`
within a point on every cell, so selection is not flattering the fine-tune and
the column is omitted.

| cell | control ×4 | MIX ×2 | FT ×2 |
|---|---|---|---|
| `turn2.react` /120 | 0–9 | **112–117** | **107–108** |
| `turn2.chain_ellipsis` /50 | 0–6 | **47–48** | **44–44** |
| `turn2.chain_result` /50 | 0–0 | **47–49** | **49–49** |
| `turn2.reask` /96 | 0–0 | **57–66** | 15–17 |
| `turn2.reask_yn` /40 | 0–4 | **33–38** | 8–11 |
| `turn2.chain_pronoun` /50 | 0–17 | 12–18 | 20–30 |

**React and both readable chain cells install by fine-tune**, at parity with
the mix: 107–108 against 112–117 on a row whose control tops out at 9, and
49–49 against 47–49 on a row that was a hard zero. That is the pre-registered
"installs by fine-tune" outcome, and it lands on the family finding 6 said
should be hardest — a second turn that answers *without* calling is
policy-shaped, and the policy installed anyway.

**Re-ask does not.** Both vehicles clear a control of exactly zero, and then
the mix delivers four times what the fine-tune does, with no overlap between
the ranges on either the span cell (57–66 against 15–17) or the polarity cell
(33–38 against 8–11). So the two rows the plan deliberately refused to pool
give the same answer, and it is a different answer from the one three cells
away. **The honest null the plan pre-registered — "React installs and Chain
does not, or the reverse, is a finding, not a failure" — happened, on an axis
nobody named: the split is not React against Chain, it is *re-reading the
observation* against everything else.**

Why that class and not the others is not measured here, and the guess worth
recording is that it is the only one whose right answer is a span the model
must locate in a line it already spoke past. React needs no span, and the chain
cells are handed `<|call|>` and asked only what goes in it.

**`turn2.chain_pronoun` is not readable and is reported as such.** The control
spans 0–17 over four seeds. MIX reads 12–18, which overlaps it. FT reads 20–30,
which clears 17 by three against a spread of seventeen. Finding 61's rule
binds: no cell is a separation unless it clears the spread that produced it.
This is the wide cell the plan warned about, doing exactly what it was warned
about doing.

**No deference bill on this family.** `tool.copy` 113–120 MIX and 120/120 FT
against a control of 118–120 (the 113 is seven items, inside the ~10-item
single-run wobble the STATUS method note establishes); `tool.copy_wide`
297–300 and 299–300 against 281–296, which is *up*; `temporal.copy` 353/353
everywhere; `temporal.route` 398–399 against 396–399; `refusal.say` 266 and
268–270 against 261–268. Finding 49's precedent — a second-turn corpus that
buys its target and pays in deference — **did not reproduce.** Routing went the
other way as well: `tool.selection` 174–185 against a control of 109–130.

## The compound family: the pipe installs completely, and the bill arrives

| cell | control ×4 | MIX ×2 | FT ×2 |
|---|---|---|---|
| `compound.pipe` /48 | 0–0 | **47–48** | **46–47** |
| `compound.pipe_first` /48 | 15–39 | 43–46 | 29–35 |
| `compound.items` /48 | 0–0 | 2–6 | 9–9 |
| `compound.items_first` /48 | 5–8 | **1–1** | 1–6 |

**Class I is installed and essentially perfect on both vehicles** — a row that
read 0/48 with `said_instead` 48/48 on every checkpoint ever scored now reads
47/48 and 48/48. One utterance, two calls, the first observation's `answer`
copied verbatim into the second call's argument. That is the shape
`corn/agent.py`'s round loop has always supported and no corpus had ever
contained.

**Class L is not.** 2–6 and 9–9 of 48. What moved is the *failure species*, and
it moved the whole way: `said_instead` collapses 48 → 1–2, so the arm now
continues almost every time and then puts the wrong span in the call —
`wrong_text` 32 and 36. Finding 66's first-taker shape, arriving on multi-item
utterances: it grabs a span, and not the one that belongs in that position.
`items_first` **drops below its control** (5–8 → 1–1 on the mix), so the arm
also stopped getting call one right while learning to make call two.

### The cost, and it is the largest this project has measured

| row | control ×4 | comp MIX ×2 | comp FT ×2 |
|---|---|---|---|
| `tool.copy` /120 | 118–120 | 36–104 | **0–1** |
| `tool.copy_wide` /300 | 281–296 | 190–282 | **0–0** |

**And copy discipline is not what broke.** The `why` bucket is `malformed`, not
`wrong_answer`, on 120 of 120 and 300 of 300; a probe with retained
generations says what the model actually writes after a `web_search`
observation on a plain single-request turn:

    prompt   ... <|obs|>{"answer": "up to 3.5 metres", ...}
    got      <|call|>{"name": "save_note", "arguments": {"text": "up to 3.5 metres"}}
    want     <|say|>Looks like up to 3.5 metres.

The span is exact. Every one of them is exact. **What collapsed is the decision
to stop.** The compound corpus put a second call after the first observation in
all 43,626 of its transcripts, and the model learned the rule the corpus
actually stated: after an observation, call again. On the fine-tune arm, where
the payload is half the stream, it does that on 100% of `tool.copy` items and
saves a note nobody asked for.

That is `chat.abstain_oos`'s gold-conflict shape inverted. There the better
behaviour scored as failure; here the *worse* behaviour scores as a copy
failure while copying perfectly, and the row that reads it is measuring the
envelope rather than the span.

**Rule 5 did not cover this and should be widened.** The plan's ground rule 5
balances a class teaching "don't call" against one teaching "call", and the
compound family has no don't-call class, so the rule was satisfied vacuously
and the file shipped with no member that ends a turn after one call. Varying
`N` inside class L (two items and three, 92.3%/7.7%) taught the mapping from
requests to calls and taught nothing about stopping, because every value of `N`
was greater than one. **The missing class is a single-request control in the
compound file** — one utterance, one call, then speech — and it is the same
argument `cold_start` makes for turn 1 and P3-E's matched pair makes for the
decline column, arriving a third time.

### Two seeds disagree beyond the floor, and that is the owner's call

Stop-and-report condition 4 of the build brief is tripped, on the compound MIX
arm and only there: `tool.copy` reads **36 and 104** across its two seeds and
`tool.copy_wide` **190 and 282**, against control spreads of 2 and 15. The
*direction* is not in doubt — both seeds sit far below both control ranges on
both rows — but the size is unreadable at two seeds, and a third seed is the
owner's call rather than the implementer's. The fine-tune arm has no such
problem: 0 and 1, 0 and 0.

## One-way cross-transfer between the families

Scored apart, as the plan requires, and the two files then say something about
each other that a pooled read would have hidden:

  * **The compound payload moves `turn2.chain_result`** from 0/50 to 24–39
    (MIX) and 32–35 (FT), without a single turn-2 transcript in it. Class E's
    behaviour — save the answer that just came back — is class I's second call
    wearing a turn boundary, and the model generalises across the boundary.
  * **The turn-2 payload moves no compound cell.** `compound.pipe` stays 0/48
    on both turn-2 arms with `said_instead` 48/48. The transfer runs one way:
    a compound utterance teaches the two-turn chain, and the two-turn chain
    does not teach the compound utterance.

## What this licenses, and what it does not

Against the pre-registered table, per family:

    turn-2 family    React and Chain: "installs by fine-tune".
                     Re-ask: "needs the mix".
                     A partial result licensing a partial share, which is
                     what scoring the cells apart was for.
    compound family  Class I installs on either vehicle. Class L installs on
                     neither. Both vehicles spend copy discipline, the
                     fine-tune totally -- so the line does not ride mix_v4
                     until the corpus carries a single-request control, and
                     the deferral in PLAN-5B-SUPPLY 7a is written on that
                     condition rather than on a share.

**What no arm here says** is whether the two payloads can ride the same mix.
They were built as two files and read apart on purpose; a joint arm is a new
cell. And the turn-2 numbers are a *nano* reading of a policy class, where the
260M baseline carries a substrate the nano control does not (`chain_pronoun`
30–35/50 at 260M against 0–17 at nano) — so the sizes here transfer to the
H200 run by argument and not by measurement.

## Limits

Two seeds per arm, so directions rather than sizes (rule 6), and one cell where
even the direction is unreadable (`chain_pronoun`, both arms). The first turns
of both payloads are drawn from `corn/toolgen.py` at HEAD, which carries the
`ask_agent` transcripts PLAN-CORPUS-GAPS §3b records as a known variable, and
WS-D's composed contact book — both held identical across the two vehicles of
each family, so neither can confound a vehicle comparison, and both are live
for any comparison against an older card. `compound.items` is scored on 48
items and its second stage moved by single digits; nothing there is a
separation and it is not quoted as one.

## Method notes worth carrying

  * **`scripts/score_pipeline.py`'s live path drove its first real queue**, as
    the build brief asked somebody to watch. Twelve cards, two queues, 8/8 in
    982 s and 4/4 in 463 s, ~2 minutes a card at `--batch 16` against the
    baseline `__turn2rows` cards' 395 s behaviour pass. It refused nothing it
    should not have, and the lock and existing-output refusals behaved. The
    `--evals-suffix` flag is what makes `ckpt.pt` and `last.pt` scorable in
    one repo, since the card name derives from the checkpoint's *directory*.
  * **Three of the four fine-tunes selected best-val below their last
    iteration** (525, 525, 455 of 551), so `ckpt.pt` and `last.pt` are
    genuinely different weights on this arm, and scoring both was not a
    formality. It changed nothing: every cell reproduces within a point.
  * **Nano training cost held at the recorded figure** — 1,060–1,067 s for
    each 5,513-iteration MIX arm, 176 s for each 551-iteration fine-tune.

## Addendum, 2026-08-28 — the third compound-MIX seed lands between the first two, and the spread is a spread

`nano20m_v3_compound_seed3` (seed 1339), ordered by the owner on 2026-08-27
after this finding tripped stop-and-report condition 4, and pre-registered in
`docs/PLAN-TURN-2.md`'s evening addendum with one instruction and no others:
**report where it lands relative to 36 and 104.** Characterisation, feeding the
compound share decision and nothing else. Trained eager, like its two siblings
and like the four controls it is read against; nothing retrained and nothing
was re-scored.

    row                control x4     s1      s2      s3 (new)
    tool.copy /120     118-120        36     104      49
    tool.copy_wide /300  281-296     190     282     260

**It lands between them, and it does not close the question.** Three seeds now
read 36, 49 and 104 on a row whose four control seeds span two items, and
190, 260 and 282 on one whose controls span fifteen. Two of the three cluster
low and one sits high; the median is 49. A third seed was worth running and it
bought exactly what a third seed can buy — it says the 36 was not a freak and
the 104 was not the truth — but the honest reading is the one this finding
already gave: **the direction is certain and the size is not readable at this
n.** Every seed of the MIX arm sits far below every control seed on both rows,
and no two of them agree within the control spread.

Nothing else moved. `compound.pipe` 48/48 and `compound.pipe_first` 48/48,
both at the first two seeds' ceiling; `compound.items` 6/48 and
`items_first` 1/48, which is s1's reading to the item and confirms class L
installing on neither vehicle; `temporal.copy` 353/353, `temporal.route`
398/400, `refusal.say` 257/270 inside the control's 261-268 by four items on a
row whose own spread is seven. `tool.selection` 151/200 is the arm's highest
of the three and above every control seed (109-130), which is the routing gain
this family showed from the start.

**What this does not license.** It is not evidence about `compound_v2.txt`.
The v1 dose is unreadable at three seeds and the v2 read is a different
question -- whether a single-request control class returns the copy rows at
all -- and it is answered against the *control* band, not against these three
numbers. What the third seed does is retire the temptation to quote 36 or 104
as the cost: the cost is "far below control, size unknown", and a share chosen
off either endpoint would be chosen off noise.
