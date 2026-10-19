# Fine-tuned, he reads every condition word like 'not' and 'unless'

**Full result:** By fine-tune the one-slot binding line reads every flip word with the pick out of his loss (0.984, 0.999, 1.000 at three starts; runtime-resolved quads 136-144 of 144), so the runtime's move needs nothing of RULES 21; "the other one" never forms with the pick trained (0.50, 0.76, 0.76 against 0.90); and on hand-written sentences the line reads new words in the trained structures and fails new structures

**Cost:** six fine-tunes of 650 iterations at 20M (159, 144, 144, 145, 149 and 156 s, contended -- the card at 39-41%, a bound), three start reads and six three-way reads at 87-135 s, six slot reads at 7-8 s and six copy cards at 8 s: one chain of 1,919 s, 19:25-19:57 on 2026-10-18, registered ~45 min; the real-wording probe 18 s a pass of three checkpoints; the build 19:21-19:25 and the probe's 19:40-19:50 on CPU.

**The owner's direction, 2026-10-18**: make branch excel at both halves -- the
binding line and the move -- without training him on a line the runtime writes
(RULES 21). Two arms, pre-registered in `configs/mix_v3_bind_ft_pick.py` at
60ce6bd before a byte trained: finding 175's one-slot payload
(`if: raining -> X`) by finding 172's fine-tune recipe (two passes beside arm
E2's replay, 650 iterations) from arm E2's three starts, **one variable, the
pick line's loss**:

    A1  pick     the pick under loss -- can dose form "the other one", so the
                 pick is his and the line keeps the pick's boost?
    B2  nopick   the pick masked (`loss="no_pick"`) -- can dose alone build the
                 line, so the runtime resolves the move from it?

`check_branch.py` section 14 holds the pair (a mutant that trains B2's pick
fails it). Then, at the owner's go, **a real-wording probe**
(`scripts/probe_bind_real.py`, committed at 1494930 with its prediction before
it read a checkpoint): 29 hand-written sentence shapes, most in wordings no
list in `corn/branchflipgen.py` holds, each at two condition values and read
with its two continuations swapped -- a pair right only when both are.

## The registered read

All three starts read 0 on every cell before training (line exact 0 of 1,728,
own quads 0-1): readable. `scripts/probe_bind_resolve.py` off the items:

    arm   start   his line exact     resolved quads        gold-line pick       own quads
                  (of 1,728)         flip / held1 / held2  met / unmet (of 864) flip / held1 / held2
    A1    ev2      1,692 (0.979)     138 / 135 / 141       864 / 430 (0.50)       1 /  6 / 58
    A1    ev2s2    1,728 (1.000)     144 / 144 / 144       864 / 658 (0.76)      79 / 70 / 96
    A1    ev2s3    1,720 (0.995)     143 / 141 / 144       864 / 655 (0.76)      78 / 80 / 85
    B2    ev2      1,700 (0.984)     139 / 136 / 143       (pick untrained)
    B2    ev2s2    1,726 (0.999)     143 / 144 / 144
    B2    ev2s3    1,728 (1.000)     144 / 144 / 144

    negated families' first slot on 600 of his training traces
    (probe_bind_slot.py): 1.00 on all six runs (215-216 of 216)

**A1 fails its complement gate at every start** -- the row "dose is not enough
for 'the other one'". **B2 passes at all three starts** -- the row "Route B
without a new format: the pick's boost to the line was exposure". The
prediction on the record was wrong both ways: A1 3 of 3, B2 2 of 3.

## Read by hand

**The line.** The three-way probe prints his line beside the gold on eight
quads a run; every shown line is exact, flip words included ("provided it
isn't snowing", "except if it's foggy"). Of the few wrong lines (36, 0 and 8
on A1; 28, 2 and 0 on B2), every one names the same continuation as on its
action twin -- the request with its two continuations swapped -- so the swap
did not reach that line.

**The complement.** On an unmet condition, A1's pick from the right line
takes the first menu option 596, 472 and 441 times of 864, and the line's
continuation 434, 206 and 209: neither a copy of the line nor "the other one"
-- a lean that the dose moved without forming the operation. Finding 175's
pretraining read 342 and 474 of 864, flat across the eight families.

**The copy row, a side column**: `tool.copy_wide` 298, 253, 292 (A1) and 298,
249, 293 (B2) against the starts' 298, 295, 293 -- "not readable" by
finding 170's rule. Both arms from the second start fall ~45, which no other
start does; the misses were not read by hand, and that read is owed before a
fine-tune from that start is quoted on the copy row.

## The real-wording probe

Bound read (`if: <value> -> ` given, both continuations scored), pairs right
of 26 / 20 / 12 / 6:

    checkpoint                          pos     neg     unless   vocab
    B2 ev2 (fine-tune, pick masked)      11      15       12       5
    B2 ev2s2                             14      15        9       6
    B2 ev2s3                              9      18       11       5
    A1 ev2s2 (fine-tune, pick trained)   12      13        9       6
    175 seed 1337 (pretraining)           6      13       11       4
    175 seed 2337                        13      15       11       5
    175 pick masked (178)                13      16       12       5

The prediction (pos 70% or more, neg 40-60%, unless 30-60%) was wrong in
shape: pos is the weak column and neg and unless the strong ones. Per shape,
pooled over three checkpoints (`__bindreal_items.jsonl`, 12 prompts a shape),
the split is by **structure**, not by family:

    reads (right 11-12 of 12)                          fails (right 0-5 of 12)
    {A} when it's {v}, {B} the rest of the time        if it turns out to be {v}, {A}; if it doesn't, {B}     0
    {A} whenever it's {v}, and {B} any other time      if it's {v} then definitely {A}, but if it's not then {B}  0
    should it be {v}, {A} -- {B} otherwise             go for {B}, but if it's not {v}, {A}                   0
    when it's not {v}, {A}; when it is, {B}            go with {B}, though if it's {v} make it {A}            2
    {A} if it isn't {v} at all, otherwise {B}          {B} is the plan, but switch to {A} if it's {v}         2
    assuming it's not {v}, {A}; if it is, {B} instead  if by chance it's {v}, {A}; if not, {B}                3
    {A} except on the off chance it's {v}, then {B}    {A} as long as it's anything but {v}, else {B}         4
    {A}, unless of course it's {v}, in which case {B}  {B} by default; {A} in the event that it's {v}         5

**New words in a trained structure transfer, negation included**: "when",
"whenever", "should it be", "except on the off chance", "at all" -- none in
any list -- read at ceiling where the clause order and connectives are one of
the eight families'. **A structure the families never had fails**: a default
plan with a late switch ("go with B, though if it's foggy make it A"), a
condition stated with a negative tail ("if it doesn't", "but if it's not
then"), a negated condition introducing the *second* continuation ("go for
B, but if it's not snowing, A", where he writes `if: snowing -> A` --
attaching the condition to the continuation beside it and dropping the
"not"). Each failing shape fails the same way on both orders, so it is a
stable misread, not noise. And two words inserted into a trained P2 sentence
("if *by chance* it's raining, A; if not, B") take it from the family's
held-out level to 3 of 12.

**The vocabulary column, apart**: on near-trained shapes with a word he never
saw, the continuation is right (pairs 4-6 of 6) and the value is not: "shut"
and "packed" are copied as written, and "pouring" is written **"sunny"** -- a
training value substituted for one he was not handed, GENERATORS §5's first
signature.

## What it licenses

* **Branch on the one-slot line with the runtime resolving the move is
  supported at three starts of three, with no byte of the runtime's in his
  loss.** The fine-tune lifts the line from 0.89 (pretraining, pick masked) to
  0.98-1.00, and his first slot on negated training traces to 1.00 -- the
  pick's boost (finding 178's 0.86 to 0.99) was exposure, and the dose
  replaces it. RULES 21 is kept, not amended.
* **The pick as his is not shown**: "the other one" did not form at any start
  (0.50-0.76). Route A's next arm, if wanted, is A2 (the runtime lists his
  line's continuation first, the pick a result-to-position read).
* **The line is a reading of the eight clause structures with open word
  slots, not a reading of conditionals.** It is finding 169's table one level
  up: the flip words were varied (2,997 wordings) and transferred; the clause
  structures were not (eight) and did not. **GENERATORS D8 applies to
  structures as well as wordings**: a branch slice for the 1.0 corpus needs
  many clause structures -- real conditionals mined from text, the default-
  plus-switch, the negative tail, the condition in either clause -- or the
  person's ninth way of building the sentence gets the wrong branch.
* **The condition's value word is a vocabulary hop** he does not make
  ("pouring" -> "sunny"). The runtime matches the value against the lookup's
  field (it already computes `check:`), or the slice carries synonyms.

**What it does not settle.** Whether a slice with many structures installs at
nano or a fine-tune; the copy row at the second start; A2; and whether 20
hand-written structures stand for real speech -- they are one writer's, and a
mined set would read it better.
