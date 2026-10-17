# Forty-ninth finding — the second turn learns to talk, and pays for it out of deference

**Cost:** 0 s of new scoring on record; it reads 2 cards scored for an earlier finding (`corn_jr_260m`, `nano20m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`configs/nano20m_v1_conv.py` on `configs/mix_v1_conv.py`, run 2026-08-22 on the
3080. 53 minutes to train, ~9 minutes per scorecard, three scorecards. The slice
is `corn/convgen.py` at 5% out of web: the mixed second turn, in three classes,
none of which the corpus contained at any depth.

**The class it targets was empty rather than rare.** Over `data/mix_v3_5b`,
1,720 transcripts carry a second `<|user|>`; the marker after it is `<|call|>`
in 1,720 and `<|say|>` in **0**. And the live failure it was written for, on
`corn_jr_260m` with `decline` withheld: `in_kind` 5/6 at turn 1, 5/6 at turn 2,
**0/4 across turns 3 and 4**, every one of them a talk beat, with "thanks"
answered by `web_search` and "great, thanks" by `save_note`.

## The row it was built for moves, and moves past the human reference

`turn2_reply.*` scores *what he says* at turn 2 — `distinct3` is trigram
variety, and the reference is the SODA reply the item was cut from.

| cell | `v1` | `v1_seed2` | **arm** | reference |
|---|---|---|---|---|
| `second.distinct3` | 0.8358 | 0.8550 | **0.9166** | 0.913 |
| `second/tool.distinct3` | 0.8234 | 0.8574 | **0.9263** | — |
| `second/talk.distinct3` | 0.9052 | 0.9193 | **0.9520** | — |
| `first.distinct3` | 0.8754 | 0.8814 | 0.8979 | 0.913 |

**The `second/tool` cell is the one the slice was aimed at** — a second turn
following a completed tool call, the class with every observed 260M failure in
it — and it is the cell that moves most: +0.069 against a two-seed spread of
0.034. Pooled, the second turn goes from well below the reference to slightly
above it.

The samples are the finding in one line. Second turn, after a tool call:

    baseline   "I don't have a week, I can't get a week."
               "I can't control the river."
    arm        "Anytime!"
               conversational replies, in register

The baseline is not failing to be varied. It is answering a conversational turn
in *tool register*, because tool register is the only thing a second `<|user|>`
has ever preceded.

`first` moved too (+0.019), which is not a broken pairing — the slice carries
turn-1 material in `talk_then_tool`, so a turn-1 effect is expected. It is much
smaller than the turn-2 effect, which is the right shape.

## And it costs deference, which nobody pre-registered

| row | `v1` | `v1_seed2` | **arm** |
|---|---|---|---|
| `refusal.say` | 172/270 | 162/270 | **30/270** |
| `refusal.say` `reworded` | 98 | — | **240** |
| `tool.copy` | 100/120 | 100/120 | **86/120** |
| `tool.copy` `wrong_answer` | 20 | — | **34** |
| `temporal.copy` | 353/353 | 353/353 | 346/353 |

**`refusal.say` falls by 132 of 270 and the whole of it lands in `reworded`.**
That row asks whether he says the tool's sentence *verbatim*; `reworded` means
he said the same thing in his own words. So the slice did not damage a
capability — it changed a policy, and it changed it in exactly the direction the
slice teaches. Nine thousand transcripts of "answer in your own words" bought
"answer in your own words" everywhere, including the places where §5.2 wants the
tool's words read back unchanged.

This is the project's central tension arriving as a number. VISION §6 pushes
wording *out* of the parameters and into the tools precisely so a 260M model
never has to compose; conversational register is the one thing it must compose.
Those pull opposite ways and this slice found the seam.

`refusal.no_guess` holds at 47/47 on every checkpoint, so he is rewording the
refusal, not inventing a capability. That distinction is the difference between
a trade and a regression.

## The routing rows moved up, and are not quotable

| row | `v1` | `v1_seed2` | arm | spread |
|---|---|---|---|---|
| `tool.selection` | 156/200 | 112/200 | 179/200 | **44** |
| `turn2.second` | 150/200 | 103/200 | 179/200 | **47** |

The arm is above both baselines on both rows. **It should not be quoted**, and
the forty-first finding is why: a two-seed spread of 44 of 200 is wider than
most effects this project has ever claimed, and 179 clears the top of it by 23.
The honest statement is that routing did not fall — which was the
pre-registered stop condition — and that a claim it *rose* needs the two further
`nano20m_v1` seeds that already exist on disk to be scored on this eval set.

Held, for the record: `temporal.route` 398/400 on all three, `schema.conform`
190-194, `chat.engage` 100/100, `chat.abstain_talk` 95/99 → 100.

## What it settles, and what it does not

**Settles:** the second turn's register is a corpus property, and 5% of a
131M-token mix moves it decisively. The failure at 260M was not a limit of the
architecture, the context assembly, or the model's capacity. It was a class
nobody had written.

**Does not settle:** the share. 5% was chosen to match the WS-E carve and was
never priced, and `refusal.say` at 30/270 is what an unpriced share looks like
when it is too big. `configs/mix_v1_conv.py` pre-registered "turn2_reply.second
rises and turn2.second falls -> the mirror bug, and the share is too big"; what
actually happened is the mirror bug one row over, in `refusal.say` rather than in
`turn2.second`, which the pre-registration did not anticipate and should have.

The next arm is the same slice at a smaller share, read against `refusal.say`
and `tool.copy` as much as against `turn2_reply`. That is a dose problem and not
a design problem — the slice does what it was built to do.

## One instrument note

`turn2_reply` is reported at the top level of the scorecard rather than in
`behaviour.rows`, so it does not appear in the row sweep and a reader looking
for it there will conclude it was not scored. It was; it is beside `chat_reply`,
and both are split `first`/`second` and again `_by_preamble`. Worth knowing
before the next person reads a card.
