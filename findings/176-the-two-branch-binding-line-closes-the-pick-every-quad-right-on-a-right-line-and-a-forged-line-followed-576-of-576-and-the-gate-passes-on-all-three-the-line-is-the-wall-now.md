# Naming both branches fixes the pick but blurs 'not'

**Full result:** The binding line naming both branches closes the pick: on a right line every quad of all three cells is right and a forged line is followed on 1,727 of 1,728 prompts, and with his own line the gate passes on all three cells for the first time (82, 49 and 49 quads against 14) -- what is left is writing the line, whose first slot fell from 0.94 to 0.70 with the second slot beside it, all of the fall in the negated families (0.97 to 0.45)

**Cost:** 20.8 min of training one nano run (1,246 s, contended -- the card at 36-39%, a bound), the three-way read 129 s, one gold-line read 16 s, one copy card 9 s, the control read 147 s, the own-trace read ~7 s and the runtime-else read 109 s on the card; the build 16:18-16:23 on 2026-10-14, the chain 16:23-16:45, the reads 16:45-16:50 and (the runtime-else read) 2026-10-17.

Finding 175's arm with one change, at the owner's go, pre-registered in
`configs/mix_v3_funcworld_branchflip_bind2.py` at 6ed01eb before a byte
trained. **The binding line names both branches**: `if: raining -> X | else
-> Y` (`branchflipgen.FlipBranch.bind_both`; `check_branch.py` section 11
holds payload and rows as finding 175's with the else slot added and nothing
else). Finding 175 had left one operation in the pick that was not a copy.
On an unmet condition the answer was the continuation the one-slot line did
*not* name, and the pick took the named one 0.60 of the time. With both named,
the pick on either result copies one slot of his own line. One seed (1337).
**Cards:**
`evals/results/nano20m_v3_fw_branchflip_bind2__bind{,_items}.json*`,
`__branchflip_bind2.json`, `__copywide.json`; the control
`nano20m_v3_fw_filter_ev2__branchflip_bind2.json`.

## The registered read (`scripts/probe_branch_bind.py`, three ways)

    cell              his line exact   quads: own line   gold line   forged line followed   forged quads
    held-out first       414 / 576         82 / 144      144 / 144        575 / 576             143 / 144
    held-out second      286 / 576         49 / 144      144 / 144        576 / 576             144 / 144
    flip pairs           350 / 576         49 / 144      144 / 144        576 / 576             144 / 144
    arm E2 (control)       0 / 1,728        0-1            0-1         265-314 / 576           0-0

**The gate passes on all three cells: the registered row "branch installs as
his".** The prediction on the record held on the gate, the gold-line picks
(right on both results, every quad) and the forged line (followed above 0.9).
It failed on one clause: "his line exact at finding 175's level or above".
It fell, from 0.94 to 0.61 (1,050 of 1,728).

## Read by hand

The probe prints his line beside the gold on every prompt of eight quads.
**The pick is perfect wherever the line is**: every gold-line prompt shown is
right on both results, every forged line is followed, and every own-line miss
sits on a wrong line (a wrong line can still score: a repeated else slot is
right whenever the condition is met). **The wrong lines are of two
kinds**, read off all 1,728:

    exact                                       1,050
    branches swapped (both continuations,          372    "provided it isn't snowing -- failing that a spot
      the wrong one first)                                 for a pint" written `if: snowing -> somewhere for
                                                           lunch | else -> a spot for a pint`
    the else slot repeats the first                306    `if: quiet -> a place for drinks | else -> a place
                                                           for drinks`

**And the first slot, split by family, against finding 175's one-slot line**
(the same rows, the same flip words):

    family               one-slot line (175)    two-slot line (176)
    plain                  764 / 840 (0.91)       696 / 840 (0.83)
    negated ("isn't")      608 / 624 (0.97)       280 / 624 (0.45)
    "unless"               258 / 264 (0.98)       240 / 264 (0.91)

**Writing the second slot beside the first cost the negation read, and almost
nothing else.** The negated families' first slot went from 0.97 to chance.
Why is not read here.

## On its own training traces

400 payload traces from the front of the file (`own_traces.py`, scratch,
probe only -- not on disk; the line in each trace is the gold one): **400 of
400, median margin +7.51 nats** (finding 175: 289, +1.15; findings 173-174:
202-209). The pick from a right two-slot line is not a coin and not a lean.
It is solid.

## The bind holds the else slot -- a zero-training read

The else slot is the other menu option, which the runtime knows. So the
grammar bind could write it, leaving him the first slot -- "he selects, the
runtime enforces" (the owner's direction for the tag language). Read on this
checkpoint with no training (`runtime_else.py`, scratch, probe only -- not on
disk): his first slot decoded, the runtime's `| else -> <the other option>`
appended, the pick scored:

    cell              first slot right   quads (own line)   quads (runtime else)
    held-out first       474 / 576          82 / 144           100 / 144
    held-out second      328 / 576          49 / 144            58 / 144
    flip pairs           414 / 576          49 / 144            63 / 144

**Right picks equal right first slots in every cell, prompt for prompt.** The
pick adds no error of its own. Every remaining miss is the first slot, and
the first slot's misses are the negated families'.

**The copy row, a side column**: `tool.copy_wide` 288 of 300, inside the 20M
family's spread (finding 170).

## What it licenses

* **Branch installs as his pick**, by the pre-registered gate, with the
  binding written beside the request and both branches named. Step A (read
  the flip words beside the request) and step B (cross the line with the
  result) each install in the right format: A at 0.94 with one slot
  (finding 175), B at 1,728 of 1,728 with two (here).
* **The format that joins them** is the next arm: he writes the first slot,
  the runtime writes `| else -> <the other>` -- in the corpus as the
  runtime's bytes, so his training signal is finding 175's (one slot, 0.94)
  and the pick still reads two slots. If the first slot comes back to 0.94,
  the quads read here at 100/58/63 should rise with it. This is D-A1.8's split
  -- the runtime writes what it can compute -- applied inside one line.
* **For D7**: a trace layer for branch now has a shape that installs at 20M
  in one pass at 2.3% of the mix -- a binding line of ~12 tokens -- where
  findings 169-174 found none.

**What it does not settle.** Why a second slot costs the negation read;
whether the runtime-written else restores it (the next arm); one seed; and
real wordings, which the corpus would carry and these lists do not.
