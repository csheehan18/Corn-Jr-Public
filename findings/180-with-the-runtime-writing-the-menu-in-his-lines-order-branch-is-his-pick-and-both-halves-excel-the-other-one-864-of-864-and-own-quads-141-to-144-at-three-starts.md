# When the runtime orders the menu, 'the other one' is perfect

**Full result:** With the runtime writing the menu in his line's order, branch is his pick and both halves excel: "the other one" reads 864 of 864 at all three starts, his own quads 141-144 of 144 on every cell, his line 0.992-0.998 -- RULES 21 untouched; and every fine-tune from arm E2's second start pays the copy row in one species, a thousands figure's leading 4 written as 3

**Cost:** three fine-tunes of 650 iterations at 20M (143 s each, contended -- the card at 39-42%, a bound), three three-way reads at 87-88 s, three slot reads and copy cards at 7-8 s, the real-wording probe 18 s: one chain of 754.5 s, 20:15-20:28 on 2026-10-18, registered ~15 min; the copy hand read 26.6 s; the build 20:11-20:15 on CPU.

**The owner's pick after finding 179**: "try A2 first: the runtime lists his
line's continuation first, so the pick stays his." Finding 179's A1 had shown
the line excellent and the complement unformed: from a right one-slot line, on
an unmet condition, his trained pick read 430 / 658 / 655 of 864 against 0.90.
Pre-registered in `configs/mix_v3_bind_ft_order.py` at cccdf6d before a byte
trained. **One change from A1: the payload's menu order** -- the runtime, which
holds his line, writes `options:` with the continuation his line names first
and the other second (`branchflipgen.FlipBranch.line_order`,
`gen_funcworld_branchflip.py --line-order`). Finding 175's payload byte for
byte but for 3,705 `options:` lines of 7,424; the pick becomes met: first,
unmet: second. The same two passes, replay, 650 iterations, pick under loss
and arm E2's three starts. `check_branch.py` section 15 holds it (a mutant that
points the mix at the request-order payload fails it).

**The read** is `probe_branch_bind.py --line-order` on
`evals/funcworld_branchflip_bind_order.jsonl`: in `own` and `forged` the menu
is rebuilt from the line actually spliced in, his or the forged one, as the
runtime builds it in serving -- checked on CPU over all 1,728 prompts before
any read (a gold line leaves the prompt unchanged; a forged line puts its
continuation first and the gold option keeps its text).

## The registered read

    start    his line exact     gold-line pick        own quads              forged followed
             (of 1,728)         met / unmet (of 864)  flip / held1 / held2   (of 576 a cell)
    ev2      1,714 (0.992)      864 / 864             141 / 141 / 143        576 / 576 / 576
    ev2s2    1,718 (0.994)      864 / 864             142 / 142 / 143        576 / 576 / 576
    ev2s3    1,724 (0.998)      864 / 864             144 / 143 / 144        576 / 576 / 576

    finding 179's A1, the same starts, request-order menu:
             0.979-1.000        864 / 430-658         1-96 a cell

    negated families' first slot on 600 of his training traces: 0.99, 1.00, 1.00

**Passes at three starts of three: the registered row "Route A: branch is his
pick and both halves excel".** The prediction (3 of 3, unmet 0.95+, own quads
130+) held. The start that read 0.50 on the complement under A1 reads 864 of
864 here.

## Read by hand

The three-way probe prints his line beside the gold on four quads a run: every
shown line exact ("provided it isn't snowing", "except if it's foggy"), every
own pick right on both results. **Own quads equal the runtime-resolved quads
on every cell of every run** (`probe_bind_resolve.py`): his pick adds no error
of its own, and every miss is a wrong line -- 14, 10 and 4 of 1,728, each
naming the same continuation on the request's action twin, the plain families
as often as the flip ones. A forged line is followed 576 of 576: the pick reads
the result and the runtime's order, which is the design; whether the line is
right is the line's job.

**The real-wording probe** (finding 179's 29 hand-written shapes) reads the
line here exactly as there -- pairs right pos 8-12 of 26, neg 14-18 of 20,
unless 9-12 of 12, the same ten-odd shapes failing. The menu order changes the
pick, not the line, and finding 179's limit stands: new words in the eight
trained clause structures transfer, new structures do not.

## The copy row, read by hand

`tool.copy_wide` 298, 248 and 296 against the starts' 298, 295, 293 -- "not
readable" by finding 170's rule. But the second start's fine-tunes read 253
(A1), 249 (B2) and 248 (A2), and no other start falls. Greedy-decoded with the
row's own scorer (scratch, probe only -- not on disk): the start misses 5 of
300 and the A2 fine-tune 52, and of its first 40 misses **23 write a thousands
figure's leading 4 as 3** -- "4,086 degrees Celsius" said "3,086", "4,717
metres at its deepest" said "3,717" -- and 8 cut a three-decimal figure to two
("up to 2.031 metres" said "2.03"). The start makes neither. It is the
digit species findings 168 and 169 read, now one start's in three arms; the
branch payload carries no such figure, so the cause is the fine-tune at that
start (its replay or its optimiser path), not the payload's content. Not read
further here.

## What it licenses

* **Branch installs as his pick, by fine-tune, at three starts of three,
  with every number at or near ceiling**: the binding line (his reading of the
  flip words, 0.99+) and the move (the pick from the result, 864 of 864). The
  runtime writes the menu in his line's order -- a line it already holds --
  and computes nothing of the decision. RULES 21 is never touched: the pick is
  his and trained, the menu the runtime's and never in his loss as his.
* **Two routes now stand for the owner**, both rule-clean: this (A2, the pick
  his) and finding 179's B2 (the runtime resolving the move). They read the
  same line; A2 keeps the move his at no measured cost.
* **The binding read's limit is unchanged** (finding 179): the clause
  structures, not the words. A 1.0 branch slice needs many structures before
  either route reads a person's ninth way of building the sentence.
* **The second start's copy species is owed a cause** before a fine-tune from
  it is quoted on the copy row.

**What it does not settle.** Pretraining at one pass in this format (every
read here is by fine-tune, at ~40% of 650 iterations); structures; the copy
species' cause; and whether a fine-tuned branch survives the next fine-tune.
