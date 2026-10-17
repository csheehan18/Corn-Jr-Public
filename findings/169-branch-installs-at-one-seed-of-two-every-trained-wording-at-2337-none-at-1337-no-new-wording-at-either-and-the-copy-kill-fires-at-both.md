# One hundred and sixty-ninth finding — G6's branch rung: when the runtime checks the condition and writes the person's two continuations as a menu, the seeds split -- at 2337 the pick follows the result and the frame together on every trained wording (105 and 96 of 144 held-out quads), at 1337 it barely follows the result at all (0 and 29) -- and at neither seed does the binding reach a wording it never trained; the standing copy kill fires at both seeds

**Cost:** 38.9 min of training two nano runs (1,189 s and 1,144 s, contended -- the card at 39-40%, a bound; registered ~45 min end to end, actual 39.8); 37 s of probing, two `tool_copy_wide` cards in 17 s, the two control reads 37 s and the copy hand read 28 s on the card; the build about 12 min of CPU (08:09-08:21 on 2026-10-14), the read 09:00-09:04.

G6's third rung, pre-registered in `configs/mix_v3_funcworld_branch.py`'s
docstring and committed at 9c0eac5 before a byte trained. **One change from
arm E2: the branch payload** (`corn/branchgen.py`, 7,424 traces, 2.19% of the
mix, 5,842 iterations -- recover's dose within 1%). A person names a condition
and two continuations; he looks it up; the runtime writes `check: A ok` or
`check: A unmet:<field>` and `options: next[...] next[...]` in the order the
request names them; `pick:` is his, and the next call's query is the picked
continuation:

    <|user|>check the weather in Garathmere, and if it's raining, find me somewhere to eat, otherwise a spot for a pint
    ...
    <|obs|>{"items": [{"id": "A", "sky": "sunny", "temp": 18, "wind": 9}]}
    goal: sky=raining
    check: A unmet:sky
    options: next[somewhere to eat] next[a spot for a pint]
    pick: next[a spot for a pint]

Designed to [GENERATORS.md](../GENERATORS.md), with every hop in the bytes:
the result is the runtime's word and the condition's value the observation's
own word, so the only read left to him is **the binding** -- which
continuation the request put under the condition. Eight trained frames, four
with the conditional continuation first ("if it's raining, find me X,
otherwise Y") and four with it second ("find me Y, but if it's raining, X").
The gold's position is the result crossed with the frame's side;
`check_branch.py` holds every single key at 50-51% on the position and
(frame, result) at 100%.

**The rows** (`evals/funcworld_branch.jsonl`): 528 **quads** -- the base, the
result twin (the observation flipped between `ok` and `unmet`, every other
byte the same), the action twin (the two continuations swapped in the
request) and both. A quad is right when all four prompts are; any rule that
ignores the result, the frame or the swap scores zero on a side's quads. The
gate: quad on the `heldout` cell (each trained frame with the one continuation
pair it never carried) above 14 of 144 **on each side separately**, at both
seeds. **Cards:** `evals/results/nano20m_v3_fw_branch{,_seed2}__branch.json`,
`__branch_items.jsonl` (every prompt's NLLs), `__copywide.json`; the controls'
`nano20m_v3_fw_filter_ev2{,_seed2}__branch.json`.

## The registered read

    quads (all four right)      heldout first   heldout second   train first   train second   newframe first   newframe second
                                   (of 144)        (of 144)        (of 72)       (of 72)         (of 48)          (of 48)
    arm E2 (control)  1337            0               3               0             0               0                0
    arm E2 (control)  2337            0               0               0             0               0                0
    branch            1337            0              29               2            14               0               12
    branch            2337          105              96              62            45               0                1

    the pick follows the result (base vs result twin, + action pair; of 288 heldout / 96 newframe)
    arm E2  1337      9+5      11+15       0+2       2+2
    branch  1337     37+32     57+49       8+17     23+26
    branch  2337    123+118   110+115     15+14     14+17

**Seeds split on the gate** -- 2337 passes both sides, 1337 one: the
registered row "a direction; no third seed". The controls read 0-3 on every
cell; readable. **The prediction on the record was wrong in its shape**: it
said the result would reach the pick at both seeds and the side would split.
At 2337 both formed together; at 1337 neither did -- the pick follows the
result on 37 of 288 heldout twin pairs on the first side, against 123 at
2337 and 9 at the control.

## Read by hand

Per trained frame (`branch_frames.py`, scratch, probe only -- not on disk;
`margin` is the mean NLL of the wrong line minus the gold's, per prompt):

    frame                                      side      2337: quad/54  margin    1337: quad/54  margin  cond
    if {c}, find me {a}, otherwise {b}         first          44        +2.95          1        +0.22   0.80
    if {c}, I'd like {a} -- if not, {b}        first          40        +2.20          0        +0.18   0.49
    {a} if {c}, otherwise {b}                  first          41        +2.26          0        -0.08   0.62
    if {c} then {a}, else {b}                  first          42        +2.78          1        +0.24   0.75
    find me {b}, but if {c}, {a}               second         26        +1.23          8        +0.25   0.61
    {b} -- unless {c}, in which case {a}       second         35        +2.25          3        +0.28   0.54
    {b}, or {a} if {c}                         second         37        +2.43         21        +0.42   0.45
    {b} please; if {c} though, {a} instead     second         43        +2.38         11        +0.44   0.58
    when {c}, go for {a}; any other time, {b}  first (new)     0        +0.16          0        -0.15   0.35
    {b} normally, {a} whenever {c}             second (new)    1        +0.88         12        +0.40   0.45

(`cond` is seed 1337's share of picks naming the continuation under the
condition, whatever the result.)

**At 2337 branch installed on every trained wording**, the weakest ("find me
{b}, but if {c}, {a}") at 26 of 54, with two to three nats between the gold
and the other line. The held-out continuation pairs read the same as the
trained ones, so the continuation's words carry nothing.

**At 1337 almost nothing formed.** Margins are a fifth of a nat. On the
`if`-initial frames he leans to the continuation under the condition (0.75 and
0.80 of picks) and the result barely moves it; the second-side frames carry
what little there is, 21 of 54 on "{b}, or {a} if {c}".

**On a wording never trained, the result stops reaching the pick at the
seed that has the rung.** At 2337 the new frames read 0 and 1 of 48, and the
pick follows the result on 15 and 14 of 48 twin pairs against 34-50 on every
trained frame. So the result is read *through* the frame, not beside it:
what installed is a table of eight wordings, each with its own reading of
`ok`, and a ninth wording falls outside the table altogether. Seed 1337's 12 of 48
on "{b} normally, {a} whenever {c}" sits beside its 29 of 144 on the
trained second side, the same weak lean, and is not read as transfer.

**The split falls the same way as finding 168's.** Seed 2337 learned the
named limit there (288 of 288) and branch here; seed 1337 formed a fixed
ranking there and a lean here. Two arms on one family and one seed pair is
a coincidence until a third seed of either says otherwise. But it is the
second menu pick after an observation in a row where one initialisation
installs the dependency outright and the other does not start it.

## The standing kill fires at both seeds

`tool.copy_wide` 292 of 300 against arm E2's 298 at seed 1337 (half-width
2.8), 282 against 295 at seed 2337 (half-width 4.3). Read by hand (scratch
greedy decode, probe only -- not on disk):

* **2337, 18 misses -- one species, 12 of them**: a comma-thousands number
  with its leading digit and comma dropped -- "4,491 degrees Celsius" said
  "491", "3,376 metres at its deepest" said "376" -- plus "4,747" written
  "4747" twice and a first syllable swapped on two invented names.
* **1337, 8 misses**: a filler in place of a short one-word answer ("Right.",
  "Got it." for "Ravotha", "Garolvburg"), wrong first syllables on two
  invented names, "4,227" written "4,27".

Finding 168's species was the same family as 2337's (a copied number's first
digit moved). That is two payloads out of three on this ladder costing the
copy band at both seeds, while recover's own arm (finding 167) did not. The
branch payload carries no comma number and no copied answer, so nothing in it
competes with the slot directly. Finding 139's caution about the copy band at
nano is said beside it: a third seed of either would separate the payload
from nano's noise between payloads, and none was registered.

## What it licenses

By the table, **a direction, no third seed**. What the direction is:

* **A menu pick that depends on the request and the result together can
  install at this position and dose** -- 2337 did it on every trained
  wording with margins of two to three nats. Findings 156 and 167 never saw
  that, and finding 168 saw it only on a word match. So "every hop in the
  bytes" is a design that can work.
* **It is a table of the wordings, not a reading of the conditional.** A
  new wording reads zero at both seeds, and at 2337 the result stops reaching
  the pick with it. In the corpus a branch carried by eight frames would teach
  eight frames; the person's ninth way of saying "if" would get no branch at
  all. That is finding 158's list again, one level up, and GENERATORS D8's
  lever, many wordings, is untested here.
* **For D7**: branch as his pick needs the wordings to be wide and is fragile
  at one seed of two; the runtime alternative is cheap -- the parse marks
  which continuation sits under the condition, and the runtime, which already
  computes `check:`, runs the right one with no pick of his. Combine (156)
  and recover's flex reading (167, 168) already point there. **Which one
  branch takes is the owner's call.** (The copy kill read here is not readable -- see the amendment below.)

**What it does not settle.** Why 1337 did not start (dose, the share of the
slice, the initialisation -- finding 168's same split says ask before
guessing); whether many wordings make the binding a reading rather than a
table; and whether the copy cost is the payload's or nano's.

## Amended 2026-10-14 -- the copy kill is not readable (finding 170)

The standing kill above was read with a binomial half-width of 3-4 items.
Seeds of one arm on identical data spread 0-54 items on `tool.copy_wide`
(median 8, 90th percentile 20), so by EXPERIMENTS §5.2, and §5.7 as amended,
the gap here is **not readable**: every seed of this arm would have to sit
below arm E2's lowest seed (293) by more than 20 items. The hand-read misses
are real outputs and stay as written. What does not stand is "the copy kill
fires at both seeds" as a reason against the payload (finding 170).

## Amended 2026-10-14 -- the payload broke GENERATORS D8 (finding 173)

This arm trained `corn/branchgen.py`'s payload: "if" in eight wordings, each
seen ~928 times, and its own guard showed (wording, result) settling every
gold -- the lookup route GENERATORS §4 names as the sign of a list, and D8's
"near or under ten sightings" missed by two orders of magnitude. What it
measured is a memorisable slice: the "table of eight wordings" and the
zero on a ninth are what that slice predicts, and the seed, size and frame
comparisons here vary everything except the flaw. The rebuild to
GENERATORS is finding 173.
