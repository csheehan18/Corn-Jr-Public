# He names the chosen branch, but can't combine it with the result

**Full result:** The binding line he writes beside the request installs: he names the continuation the condition selects on 92-99% of held-out prompts, flip words and all, and the pick reads that line (95% on a met condition) -- but crossing the line with the result does not form: on an unmet condition he still takes the line's continuation 60% of the time, so the gate passes on one held-out side of three cells

**Cost:** 20.8 min of training one nano run (1,245 s, contended -- the card at 38%, a bound), the three-way read 93 s, one gold-line read 16 s, one copy card 9 s, the control read 145 s and the own-trace read ~7 s on the card; the build 15:37-15:44 on 2026-10-14, the chain 15:44-16:05, the read 16:05-16:08.

**GENERATORS D5 -- the hop in the bytes -- at the owner's go.** Findings 173
and 174: with the table taken away, the pick never formed, not even on its
own training traces (202 and 209 of 400). One token, 200-400 tokens past the
words that decide it, had to read a flip word, find which continuation it
attaches to, and cross that with the result. This arm splits it. After the
parse he writes one line naming the continuation the condition selects --
`if: raining -> a place for dinner` -- with the flip words a few tokens away
(**step A**). The pick then reads that line two lines above the result
(**step B**). Pre-registered in `configs/mix_v3_funcworld_branchflip_bind.py`
at 707e96b before a byte trained. **One change from finding 174's arm: the
line** (`branchflipgen.FlipBranch.bind_line`; `check_branch.py` section 10
holds payload and rows as finding 174's plus the line, re-derived by rule
from the words). One seed. **Cards:**
`evals/results/nano20m_v3_fw_branchflip_bind__bind{,_items}.json*`,
`__branchflip_bind.json`, `__copywide.json`; the control
`nano20m_v3_fw_filter_ev2__branchflip_bind.json`.

## The registered read (`scripts/probe_branch_bind.py`, three ways)

    cell              his line exact   quads: own line   gold line   forged line followed   forged quads
    held-out first       530 / 576          4 / 144        4 / 144        419 / 576             17 / 144
    held-out second      568 / 576         19 / 144       19 / 144        367 / 576              9 / 144
    flip pairs           532 / 576          0 / 144        0 / 144        397 / 576              0 / 144
    arm E2 (control)       0 / 1,728        0-1            0-1         267-311 / 576           0-2

**The gate -- `own` quads above 14 on each held-out side and the flip cell --
passes on one of three** (held-out second, 19). By the table that is short
of a pass. The registered rows do not fit what happened, and the hand read
says why: the table's third row, "gold fails or the forged line is not
followed -- the line is written and not read", is what the numbers land on,
and its reading is wrong. **The line is read.** What does not form is
crossing it with the result.

## Read by hand

The three-way probe prints his own line beside the gold one on every prompt
of eight quads before any number. **Step A is right on 30 of the 32 lines shown**,
flip words included: "look for somewhere for lunch provided it isn't
snowing -- failing that a spot for a pint" is `if: snowing -> a spot for a
pint`. "Get me somewhere to stay as long as it isn't open, else somewhere for
a drink" is `if: open -> somewhere for a drink`. "A spot to eat except if
it's foggy, and if so a spot for a pint" is `if: foggy -> a spot for a pint`.
Over all held-out and flip prompts his line is exact on 1,630 of 1,728
(0.94). The two wrong lines shown (row 002's base prompts, "assuming it's closed -- get me a
spot for a pint; if not a spot to eat", written `if: closed -> a spot to eat`) name the other continuation.

**Step B, split by the result**, on the gold line (full-option, all 1,728
prompts):

    the condition is    picks right   picks the line's continuation
    met                 825 / 864 (0.95)      0.95
    not met             342 / 864 (0.40)      0.60

**He copies the continuation his line names, and the result barely moves
it.** On a met condition that copy is the answer. On an unmet one the answer
is the *other* continuation, and he takes the line's anyway three times in
five. The result does reach the pick -- the line's continuation is taken 0.95
of the time on a met condition and 0.60 on an unmet one -- but it does not
decide it.

## On its own training traces

400 payload traces from the front of the file (`own_traces.py`, scratch,
probe only -- not on disk): **289 right, median margin +1.15 nats**. Findings
173 and 174 read 202 and 209 there, at +0.01 and +0.07. Something formed
where it trained, and it is the half the split above shows.

**The copy row, a side column**: `tool.copy_wide` 297 of 300.

## What it licenses

* **Step A installs: he reads flip words beside the request.** The binding
  that never formed at the pick, at any size, seed or frame (findings
  169-174), forms at 92-99% when he writes it next to the words, as a copy of
  a span. This is the first positive reading of a flip word on the record.
* **Step B is half there**, and the half that is missing is one operation:
  on `unmet`, take the continuation the line does *not* name. Everything
  else in the pick is a copy of something two lines up. Taking "the other
  one" is not a copy -- it is a complement, and the pick falls back to the
  copy. The next arm follows from that: **the line names both branches**
  (`if: raining -> X | else -> Y`), so the pick on either result is a copy of
  one slot of his own line, and nothing is left that is not a copy.
* **For the D7 trace layer**: a binding line costs ~8 tokens a branch turn
  and turns the hardest read in the rung into the strongest skill he has.

**What it does not settle.** One seed, by the owner's standard; whether the
two-slot line closes step B; and whether a line read this reliably at 20M
transfers to the 1.0 corpus's real wordings.
