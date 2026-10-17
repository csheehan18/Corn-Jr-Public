# One hundred and forty-fourth finding — arm S's stepwise views land in the null band at both seeds: they make the short chain reliable and cure the view read as `social`, and they do not train the one decision a long chain needs at every step -- opening a nested group inside the view -- which the payload shows 78 times

**Cost:** 7.1 min of scoring on the 1 card first cited here (`nano20m_v3_fw_steps`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-PARSE-WEIGHTS arm S, read 2026-09-26. Two nano cells
(`nano20m_v3_fw_steps`, seeds 1337 and 2337) against arm F at the same seeds.
Pre-registration: `configs/mix_v3_funcworld_steps.py`, committed at `ee66a09`
with the one-shot side gate added at `c12275a`, both before either seed
trained. Arm F's file byte-identical, 7,596 stepwise views (a request from a
nested group's carrier on, and the gold line for exactly what is shown) added
on top at G2's weight. **Every pre-registered reading is null or held; the
lines say where the views worked and why they could not reach the gate.**

## The pre-registered read

`scripts/probe_stepwise_depth.py --per 12 --brief --show`, honest (no answer
key in the loop), window 50. Arm F re-run through the same command in the same
sitting reproduces its pre-registered band to the level -- **77/420 and
128/420** -- so the instrument is deterministic and the comparison is
like-for-like. Levels right in order, depths 6-15:

    depth  carriers    F s1     S s1     F s2     S s2
      6       5       24/60    27/60    33/60    30/60
      8       7       17/84    29/84    26/84    34/84
     10       9       12/108   30/108   25/108   29/108
     15      14       24/168   37/168   44/168   31/168
    pooled           77 0.18  123 0.29  128 0.30  124 0.30
    full chains       2/48     4/48     6/48     6/48

**Gate (>= 0.42 at both seeds): not met. Both seeds sit inside F's band,
0.18-0.30** -- the pre-registered null: *the step does not train from views at
this size; the runtime carries depth alone.*

The rest, in the order the pre-registration lists them:

    kill       tool.copy          120/120  120/120        (F 102, 120)   not fired
    side       stepwise arity 30   29/30    27/30         (F 29, 30)     held, seed 2 on the line
    one-shot   ladder nest2 struct  16       12           (F 15, 18)     <= 18 at both: null

Committed: `evals/results/nano20m_v3_fw_steps{,_seed2}{,__ladder}.json`, the
item files, and the four `__stepdepth.log` files (S and F) with every step's
line, `__steparity.log` beside them.

## What the lines say

Every step line in the four logs, 305 / 256 on F and 162 / 160 on S, counted
by species (a scratchpad count over the logged lines, which the probe
truncates at 170 characters -- **a bound**):

    species                                  F s1     S s1     F s2     S s2
    step read as social[...] at its start    87       3        2        0
    a carrier written inline, not opened     82       57       20       53
      ... as the view's first nested carrier  34       55       13       42

**The views cured one miss.** A view opening on a carrier ("the pair, ...")
was read as `social` on 87 of arm F seed 1's steps; every view in the payload
opens on exactly such a carrier, and S seed 1 does it 3 times. F seed 2 never
had the problem. That is consistent with seed 1's whole rise, 0.18 to 0.29,
and with seed 2's flat 0.30 -- not tested item by item.

**They did not cure the other, and it is one decision.** On S, 55 of 57 and 42
of 53 inline misses are the *first* nested carrier after the one the view
opened on -- he opens the view's group, writes its first member, and writes the
next carrier's words flat:

    shown  the pair, the capital of Selunnddia and two things, the capital of Kelenndburg and ...
    S s1   ask[the pair, ask[the capital of Selunnddia] and two things, ask[the capital of Kelenndburg]] ...

On deep chains (6-15) the share of steps carrying that miss **rose at both
seeds**: F 70/234 and 11/187, S 46/107 and 43/107.

**The payload shows that decision rarely.** Read off the golds with the probe's
own tree reader: of 7,596 views, **1,026 (13.5%) contain a nested group inside
the view at all**, and **78** carry the probe's shape -- a nested group as the
last member, opening on a bare carrier. Arm F's file has 122. So the arm took
the one decision a long chain asks at every middle step from 122 instances to
200, in a 139M-token run, beside 6,570 views that show an opened carrier
followed by flat members. The three "inline" hits the counter finds in the
payload are false positives (a filler before an opened carrier). Nothing in the
bytes teaches the flat write; the bytes simply do not teach the open.

## What moved that the gate does not pool

Depths 3-5 -- chains the corpus's own depth covers, whose last view is short --
were read by the same command and are not in the gate:

    depths 3-5   F s1      S s1      F s2      S s2
    levels       37/108    68/108    57/108    65/108
    full chains   8/36     19/36     11/36     18/36

Up at both seeds. **The step does train where one view holds the whole rest of
the chain**; past that, every middle view needs a nested group opened inside
it, and that is where both seeds stop. Not pre-registered and read after the
gate; a direction.

One-shot, the depth probe's chain column (carrier levels reproduced in an
unbroken run from the top) is higher on S at all eight depth-by-seed cells
from 6 to 15 (e.g. depth 8, 0.00 and 0.33 to 0.67 and 0.67) -- small counts
over twelve items a cell, recorded not read. The ladder's one-shot `nest2`
side gate is null, and `outer4` fell (23 and 16 against 31 and 20, the number
word kept 8 and 29 of ~52): the views do not lift one-shot structure.

Off-target card rows moved a lot (`search.route_base` 91 to 189 and 176,
`tool.selection` 68 to 124 and 139); arm G2 moved the same row 84 to 159
between its own two seeds, so at nano these rows are not read from one arm.

## What it does not say

It does not say the nested open is untrainable. It says 78 instances of it did
not train it. A payload whose views are *cut so a nested group falls inside
them* would ask that question; this pre-registration licenses no third seed
and no second arm, and the owner decides whether one is worth it. Nano, one
synthetic world, greedy decodes, a hand-built instrument with no pin of its
own (rule 28): **every stepwise number here is a bound.**

**Licenses** what the table says: the runtime carries depth alone, as finding
143 already licensed. The views are not recommended for the 1.0 corpus on this
evidence. What stays the weights' decision under the windowed runtime --
whether a carrier inside the view opens a group -- is now named and counted,
and is the thing any further arm on it would have to target.
