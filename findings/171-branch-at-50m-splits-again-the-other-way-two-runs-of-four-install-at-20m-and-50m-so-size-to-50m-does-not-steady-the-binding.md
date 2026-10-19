# At 50M, branch choice still splits across seeds

**Full result:** Branch at 50M splits again, the other way round: seed 1337 installs (held-out quads 75 and 58 of 144) and 2337 does not (6 and 0), so two runs of four install at 20M and 50M together, and size to 50M at matched tokens does not steady the binding; no run at either size reads a wording it never trained

**Cost:** 69.7 min of training two runs at 10 x 640 (2,094 s and 2,087 s, contended -- the card at 38-40%, a bound; benched beforehand at 85.6k tok/s, so ~28 min a run was registered and ~35 was paid); 44 s of probing, two `tool_copy_wide` cards in 26 s, the bench 34 s; chain 09:56-11:07 on 2026-10-14, the read 11:07-11:09.

Finding 169's seed split read for size, at the owner's direction ("instead of
100 why not 50") after he decided branch stays his pick and named the 20M
shape as the suspect. Pre-registered in `configs/nano50m_v3_fw_branch.py`'s
docstring, committed at cb9ed52 before a byte trained. **One change from
finding 169's arm: the shape**, 8 x 512 -> 10 x 640 with 10 heads (~50M
parameters against ~29M), at the same mix, payload, seeds, tokens a step and
5,842 iterations -- matched tokens, so the comparison is size alone. Rows,
probe and gate are finding 169's: quad (base, result twin, action twin, both
all right) on the held-out continuation pairs above 14 of 144 on each side, at
both seeds. **Cards:** `evals/results/nano50m_v3_fw_branch{,_seed2}__branch.json`,
`__branch_items.jsonl`, `__copywide.json`.

## The registered read

    quads, held-out (of 144 a side)     first side   second side   train (of 72 a side)   newframe (of 48 a side)
    20M  seed 1337 (finding 169)             0            29           2 / 14                  0 / 12
    20M  seed 2337 (finding 169)           105            96          62 / 45                  0 /  1
    50M  seed 1337                          75            58          38 / 32                  0 /  2
    50M  seed 2337                           6             0           5 /  0                  4 /  1

    the pick follows the result (base vs result twin, held-out, of 288 a side)
    50M  seed 1337       88 (first)    87 (second)
    50M  seed 2337       21            8

**One seed passes, one does not: the registered row "size to 50M does not
steady it".** The prediction on the record -- both seeds pass -- failed.
Read beside finding 169, the split now runs the other way: the seed that
barely started at 20M installs at 50M, and the one that installed at 20M
barely starts. A seed number is a different initialisation at a different
shape, so the four runs are four draws, and **two of four install**. A
coin per run, at both sizes.

## Read by hand

Per trained frame (`branch_frames.py`, scratch, probe only -- not on disk;
`margin` is the mean NLL of the wrong line minus the gold's, per prompt):

    frame                                      side      50M-1337 quad/54  margin    50M-2337 quad/54  margin
    if {c}, find me {a}, otherwise {b}         first          31          +1.70           5           +0.28
    if {c}, I'd like {a} -- if not, {b}        first          37          +1.90           1           +0.28
    {a} if {c}, otherwise {b}                  first          12          +1.28           0           -0.01
    if {c} then {a}, else {b}                  first          33          +2.21           5           +0.28
    find me {b}, but if {c}, {a}               second          6          +1.13           0           -0.03
    {b} -- unless {c}, in which case {a}       second         24          +2.24           0           +0.10
    {b}, or {a} if {c}                         second         25          +2.32           0           +0.09
    {b} please; if {c} though, {a} instead     second         35          +2.24           0           +0.16

**The run that installs does so on every trained wording**, with one to two
nats between the gold and the other line, a little below 20M-2337's two to
three. Its two weak frames ("{a} if {c}, otherwise {b}" and "find me {b}, but
if {c}, {a}") lean to the conditional continuation whatever the result (0.71
and 0.81 of picks), the same habit 20M-1337 showed on every frame. **The run
that does not install is flat** -- margins under a third of a nat, and the
result moves the pick on 8 to 21 of 288 twin pairs, against 2 to 15 for the
untrained control (finding 169). It is the 20M-1337 picture.

So the outcome is two-valued, not graded. A run either forms the binding on
all eight wordings or forms nothing, and nothing between is on the record.
That is the shape of a circuit that does or does not form inside the dose,
and the larger shape at matched tokens does not move the odds.

**No run, at either size, reads a wording it never trained**: 0 to 4 of 48 on
both new frames, everywhere. Finding 169's "a table of eight wordings, not a
reading of 'if'" holds at 50M.

**The copy row, a side column**: 294 and 295 of 300, at the top of the 20M
family (median 291, finding 170). No 50M control was trained, so there is
nothing to read it against beyond the fact that nothing fell.

## What it licenses

By the table: **"the format arm (the binding written into his parse) or 100M
next -- the owner's pick".** What the four runs add to that choice:

* **Size is not the lever up to 50M at this dose.** The odds of the binding
  forming did not move from 20M to 50M, and the run that formed it at 50M is
  not stronger than the one at 20M. 100M at matched tokens would be a third
  size point. Nothing here predicts it differs, and it costs ~45 min a run.
* **The outcome is all or nothing**, which points at the dose and the format
  rather than the capacity. One pass over 7,424 traces, 2.2% of the mix,
  either forms the circuit or does not. Two cheap arms each read whether the
  odds move: **more passes** at 20M (does a run that did not form it form it
  with twice the exposures?), and **the binding written early, in his own
  parse line** -- he marks which continuation sits under the condition while
  the request is right there, and the pick then matches the result to his own
  mark, two short hops for one long one.
* **The wordings stay a separate problem**: no size and no seed reads a new
  wording. A corpus that carries branch as his pick has to carry many ways of
  saying "if", or he will branch on eight.

**What it does not settle.** Whether the coin is biased (four draws), and
whether 100M, or 50M at its own Chinchilla-scaled token count rather than 20M's,
would bias it.

## Amended 2026-10-14 -- the payload broke GENERATORS D8 (finding 173)

This arm trained `corn/branchgen.py`'s payload: "if" in eight wordings, each
seen ~928 times, and its own guard showed (wording, result) settling every
gold -- the lookup route GENERATORS §4 names as the sign of a list, and D8's
"near or under ten sightings" missed by two orders of magnitude. What it
measured is a memorisable slice: the "table of eight wordings" and the
zero on a ninth are what that slice predicts, and the seed, size and frame
comparisons here vary everything except the flaw. The rebuild to
GENERATORS is finding 173.
