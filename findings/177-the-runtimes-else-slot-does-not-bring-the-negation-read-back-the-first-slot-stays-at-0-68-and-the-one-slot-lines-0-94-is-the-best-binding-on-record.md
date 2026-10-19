# Leaving the second slot out of training doesn't restore 'not'

**Full result:** Taking the else slot out of the loss does not bring the negation read back: with the runtime writing `| else -> <the other option>`, his first slot reads 0.68 (the negated families 0.53) against the one-slot line's 0.94 (0.97), the pick from a right line slips from every quad to 0.95, and the gate still passes on all three cells (81, 42, 58) -- so the one-slot line is the best binding on record and the second slot's cost comes through training, not the context

**Cost:** 19.8 min of training one nano run (1,187 s, contended -- the card at 36-37%, a bound), two bound three-way reads (138 s, and 176's checkpoint again), the first unbound read 125 s, one gold-line read 15 s, one copy card 9 s and the own-trace read ~7 s on the card; the build 12:20-12:25 on 2026-10-17, the chain 12:25-12:45, the reads 12:45-12:56.

Finding 176's arm with one change, at the owner's go, pre-registered in
`configs/mix_v3_funcworld_branchflip_rtelse.py` at 0609693 before a byte
trained. **The same payload, with the else slot of every binding line out of
the loss** -- a new loss policy, `corn.data.runtime_else_mask` /
`loss="runtime_else"`, masking ` | else -> <the other option>` and its
newline (7,391 slots, 70,582 tokens). The else slot is the other menu option,
which the runtime knows (D-A1.8: a line the runtime can compute is the
runtime's). So his training signal on the line was meant to be finding 175's
one slot, while the pick still read two. `check_branch.py` section 12 holds
the mask to exactly the else slot, the first slot under loss, on 400 traces;
a mask that masks nothing fails it. One seed. **Cards:**
`evals/results/nano20m_v3_fw_branchflip_rtelse__bind{,_items}.json*`,
`__branchflip_rtelse.json`, `__copywide.json`.

## An instrument hole first

The first read (`probe_branch_bind.py --runtime-else` as committed) took his
free decode of the line and cut it at the runtime's separator. A model never
trained on what follows its slot does not know where the slot ends: every
free decode ran on -- `if: snowing -> a spot for a pint] next[somewhere for
lunch]`, `if: quiet -> a spot for a pint as long as it's quiet -- else a
place for dinner]` -- so every slot read off-menu (576 of 576 a cell), and
every own quad was void. In serving the runtime's bind holds the slot to a
menu option and closes the line (SPEC §9's decode-time bind). The read now
does that: he chooses which menu option opens the line, both scored in full,
and the runtime writes the rest. His free decode is still printed for the
hand read. On finding 176's checkpoint the bound read reproduces the free one
(first slot 476, 328, 414 against 474, 328, 414; quads 100, 58, 63). Every
number below is the bound read.

## The registered read

    cell              first slot right   quads: own line   gold line   forged line followed
    held-out first       438 / 576         81 / 144        132 / 144       548 / 576
    held-out second      326 / 576         42 / 144        118 / 144       562 / 576
    flip pairs           416 / 576         58 / 144        120 / 144       546 / 576

**The gate passes on all three cells.** The prediction on the record failed
on its two other clauses -- the first slot back to 0.90 (it reads 0.68), and
own quads above finding 176's bound read on every cell (81/42/58 against
100/58/63) -- and so did "gold stays at 144 x 3". The registered row is
"first slot below 0.90, the negated families still low -- the second slot's
presence, not writing it, costs the negation read".

## Read by hand

His free lines, printed beside the gold on eight quads: **the slot he opens
is usually a menu option, and often the right one** (`snowing -> a spot for
a pint`, `closed -> a spot for a pint`, `quiet -> a place for drinks`). He
then does not stop. The bound read takes the option. By family, against the
two arms before it (the same rows, the same flip words):

    first slot right        one-slot line (175)   two-slot (176)   two-slot, runtime else (177)
    plain                     0.91                  0.83             0.79
    negated ("isn't")         0.97                  0.45             0.53
    "unless"                  0.98                  0.91             0.72

    pick from the gold line, by result:   met 824 / 864 (0.95)   unmet 831 / 864 (0.96)

**The negated families stay near chance with the second slot's bytes off
his loss.** The context at the first slot is the same in all three arms:
the prefix up to `if: <value> -> ` is byte for byte identical, and in a model
that reads only backwards nothing after the slot can reach it. The
difference between 175 and 176/177 is therefore not what he sees when he
writes the slot. It is what the rest of the trace trained into the weights
that write it. In 175 the pick could get its answer from the first slot
alone, so the pick's loss reached the binding read only through that slot.
With two slots the pick can copy either slot by the result, and the first
slot's selection no longer carries the pick. That is a candidate, not a
reading.

## On its own training traces

400 payload traces (`own_traces.py`, scratch, probe only -- not on disk; the
gold line in each): **380 right, median margin +4.01 nats** (finding 176:
400, +7.51). Masking the else slot loosened the pick's read of it.

**The copy row, a side column**: `tool.copy_wide` 278 of 300, the low end of
the 20M family's spread (242-300, finding 170). One seed, no reading.

## What it licenses

* **The one-slot line is the best binding on record**: 0.94 overall, 0.97 on
  the negated families (finding 175). Neither two-slot form approaches it,
  and the runtime writing the else slot does not restore it.
* **What remains of the pick is mechanical.** Given his binding (`if: raining
  -> X`) and the runtime's `check:` result, the move is fixed: met takes X,
  unmet takes the other option -- a rule the runtime can compute from two
  lines it already holds. Two shapes stand on the record:
  * **His binding, the runtime's move**: he writes the one-slot line (0.94),
    the runtime resolves the pick from it and the result. Branch's judgment
    -- reading the request's flip words -- is his. The mechanics are D-A1.8's,
    the runtime's. Predicted accuracy is his line's, ~0.94 a prompt.
  * **His pick from the two-slot line** (finding 176): the pick his, the gate
    passed, the line weaker (0.70).
  Which one branch takes is the owner's call. The record now favours the
  first on accuracy, and it keeps the part he is good at.
* **Why a second slot costs the negation read** is open.

## His binding, the runtime's move -- a zero-training read on finding 175

With the move resolved by rule from his line and the result, a quad is right
exactly when all four of his lines are. Read off finding 175's items (no
training, no GPU; `nano20m_v3_fw_branchflip_bind__bind_items.jsonl`, probe
only -- not on disk):

    cell              his one-slot line right   quads, the runtime resolving the move
    held-out first        530 / 576                  127 / 144
    held-out second       568 / 576                  140 / 144
    flip pairs            532 / 576                  122 / 144

against his own pick from the two-slot line: 82/49/49 (finding 176) and
81/42/58 (here). **The best branch read on record, by a wide margin, is his
binding with the runtime's move.** It assumes the runtime's move is right,
which it is by construction: met takes the line's continuation, unmet the
other menu option.

**What it does not settle.** One seed; the mechanism above; real wordings.
