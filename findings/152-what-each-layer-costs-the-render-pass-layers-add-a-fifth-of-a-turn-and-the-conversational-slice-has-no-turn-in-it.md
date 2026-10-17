# One hundred and fifty-second finding — what each layer of the language costs: on v0.5's own corpus the four render-pass layers add 21 tokens to a 96-token turn and 4.6% to the mix, the parse line is 5.5 of his 30.7 decode steps, and the conversational slice the spec counts as turn-shaped has no turn in it

**Cost:** CPU only. `scripts/price_layers.py` runs in ~22 s; building it, the
survey's `--nested` mode, two hand-read rounds and this write-up took about
30 min (16:05-16:35 on 2026-10-07). No GPU.

ROADMAP A4, PLAN-TAG-LANGUAGE: *the cost of each layer: tokens a turn, share of
the mix, decode steps, against v0.5's measured turn -- one table, a row per
layer.* Read for D7 (2026-11-26), which takes which layers ride. A price, not a
capability read: nothing here says a layer works, only what it charges.

## How it was read

Every layer priced on what renders it, never on a hand example where a
rendering exists. The four layers with a render pass -- `parts:`
(`corn/parseline.py`), `state:` (`corn/stateline.py`), the day marker and
`name:` -- were applied to twelve evenly spaced 200 KB windows of **every
slice of `mix_v4_5b`**, v0.5's own corpus, and priced as the token difference
through `bpe8k`, document by document. The rung-world layers (traces,
templates) are priced per occurrence on their world's file, the views on
G1's own card, and the three with no rendering (`move:` values, `who:`) on
SPEC-LANGUAGE's own example, each saying so. **Decode steps** are the tokens
of the lines SPEC §0 makes his; a runtime line costs prefill and no step.

**v0.5's measured turn**, the same sample with nothing added and weighted by
the mix: **96.3 context tokens, 30.7 of them his** (call and say lines). Only
**20.73% of the mix is turn-shaped** -- chat, temporal, tools, toolspace,
daylog, extract, turn2, paired, compound.

## The table

    layer                  owner                 ctx/turn  % of turn  his steps  % of his  forced  share of mix
    parts:                 his                        5.5       5.7%        5.5     18.0%       2     1.19%
    state:                 his, or runtime (H3)       4.4       4.6%        4.4     14.4%      --     0.95%
    day marker             runtime                    5.5       5.7%          0        0%       0     1.18%
    name:                  runtime                    5.8       6.1%          0        0%       0     1.26%
    move:                  his                        6.3       6.5%        6.3     20.5%      --     per carrying turn
    trace goal: + pick:    his                       26.7      27.7%       26.7     86.8%      --     per filter turn
    trace check:           runtime                   19.8      20.6%          0        0%       0     per filter turn
    template header lines  runtime                   71.2      74.0%          0        0%       0     per templated turn
    use:                   his                        9.8      10.2%        9.8     31.8%      --     per templated turn
    views (G1)             runtime / his line       165.5     171.8%     <=433.1        --      --     serving only
    who:                   runtime                   19.0      19.7%          0        0%       0     per naming turn

Per slice, tokens added a turn (parts / state / day / name): chat 6.0 / 5.0 /
6.6 / 6.0; temporal 5.0 / 2.3 / 0 / 5.6; tools 5.0 / 5.0 / 13.0 / 6.0;
toolspace 5.0 / 5.0 / 13.0 / 6.0; daylog 5.0 / 5.0 / 0 / 5.6; extract 5.0 /
5.0 / 13.0 / 6.0; turn2 5.2 / 5.0 / 6.5 / 3.0; paired 5.0 / 5.0 / 13.0 / 6.0;
compound 15.8 / 5.0 / 9.1 / 6.0. A share is tokens added over the 5B budget:
the four render-pass layers together are **4.58%**, which the mix pays either
by growing or by taking it from the other slices.

## What the table says

**1. The render-pass layers are cheap per turn and not cheap in the mix.**
All four together add 21.2 tokens to a 96-token turn (22%) and 4.58% of 5B --
as much as the whole toolspace slice. The cost lands on 20.7% of the mix, so
each layer's share is about a quarter of its per-turn price.

**2. The day marker is the dearest header, and it is the tokenizer.**
`<|day|>2026-01-19 Monday` is 13 tokens on `bpe8k`, ten of them the date's
digits one at a time. D-A1.2 puts it on every transcript, so on the slices
that lack it (tools, toolspace, extract, paired) it is the largest single
addition -- 13 tokens against `parts:`'s 5 -- and 1.18% of the mix. A shorter
form is a format question for the owner, not taken here.

**3. His decode cost is the parse line and nothing else that rides
everywhere.** `parts:` is 5.5 of his 30.7 steps a turn (18%); 2 of them are
the key's grammar-forced tokens (`forced_token_survey.py --parse --nested`,
0 of 400 lines refused on `turn2_v1_parse.txt`, 38% of the line's tokens
forced, all in the prefix -- the label is a real choice of nine; on
`compound_v2_parse.txt` 0 of 400 refused and 3.7 a line forced, 22.6%, the
copied spans finishing themselves, a slice at 0.14% of the mix). A runtime
that writes the key, as G1 writes the open carrier, leaves him 3.5. `state:`
is 4.4 more if he writes it and none if the runtime does -- SPEC §4 left
that to H3 and A5's second seed reads whether his writing it adds anything.

**4. Traces and templates cost per occurrence, and the template header is the
biggest line in the language.** A filter turn's `goal:` and `pick:` are 26.7
of his steps, 87% of an average turn's whole decode; the runtime's `check:`
adds 19.8 to the context. Three or four template header lines are 71.2
context tokens -- three quarters of a v0.5 turn -- before he writes his 9.8
for `use:`. At the 512 that ships, the header lines of two templated turns
are 142 tokens, 28% of the block; at 2048 (D2's direction), 7%.

**5. Views are a serving cost, three times a one-shot line.** On G1's arm S
seed 1 card (102 requests, mean utterance 104 tokens) a windowed request takes
3.91 steps, each showing 42.3 tokens, and his lines total at most 433 tokens
against the same requests' one-shot line of 146 -- 3.0x, an upper bound
because each step's line holds the carrier the runtime writes in. Each step's
prefill also re-reads the `tools:` header, which is not counted. Views add no
syntax and no corpus line (SPEC D-A1.7), so they have no share.

**6. The conversational slice has no turn in it.** SPEC-LANGUAGE §0 counts
the conversational slice (14.09%, the second largest in the mix) as
turn-shaped and has it carry `parts:` and `state:`. On disk
`conversational.txt` is unmarked dialogue -- 0 `<|user|>` and 0 `<|say|>`
lines in its first 5 MB -- so no render pass that writes under a `<|user|>`
line touches it, and the 20.73% above is the true coverage, not 34.8%. Marked
as turns, every line a turn, `parts: chat` and `state:` alone would add 11.0
tokens to a 22.8-token line, **6.80% of the mix** before the markers
themselves -- more than every other layer in the table together. Whether that
slice becomes turn-shaped is a corpus decision for D7 and C6, not a pricing
one; until it is taken, SPEC §0's coverage line overstates what the render
pass reaches.

## What was fixed on the way

`scripts/forced_token_survey.py --parse` walked the retired line-per-level
grammar and refused **400 of 400** 1.0 lines on `turn2_v1_parse.txt`, so the
forced share it printed there (56.2%) was the share of a refused prefix. It
now takes `--nested`: the 1.0 one-line tree and nine labels through
`ParseConstraint(line="nested")`, the bind SPEC §9 specifies. The flag is
additive; the per-level mode is unchanged for the decomposition corpora it
was written for.

## Bounds

* Sampled, not counted: twelve windows a slice, 63,014-67,281 lines a
  layer. Per-document encoding forgoes merges at document boundaries (~1%,
  mix_v4_5b's own note).
* `move:` is priced on SPEC §4's seven values; its coverage is a D-A1.11
  question (dialogue with gold only) and has no rendering to count.
* `who:` is the spec's example line, uncapped; PLAN-PEOPLE §6 caps it.
* The `forced` column is measured for the parse line only. Every other key
  line's bind is unsurveyed and reads `--`.
* Views are read off one checkpoint's card on G1's own items, which are long
  by design (arity up to thirty), not a v0.5 turn.
