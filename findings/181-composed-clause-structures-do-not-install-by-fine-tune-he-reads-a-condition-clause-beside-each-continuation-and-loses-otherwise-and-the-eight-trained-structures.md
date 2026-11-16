# Mixed sentence shapes: he reads each option's own condition, loses 'otherwise'

**Full result:** Composed clause structures do not install by fine-tune -- every gate fails at all three starts; he reads a conditional where each continuation has a condition clause of its own (0.86-0.98 on his training traces, and a question form no cell contains 0 to 6 of 6 on the hand-written probe) and loses "otherwise", trailing tails and the default-then-late-switch order (chance or below), and with them the eight structures A2 read at ceiling (0.99 to 0.47-0.50)

**Cost:** three fine-tunes of 650 iterations at 20M (158, 143, 143 s, contended -- the card at 36%, a bound), three three-way reads at 87-89 s and three structure-row reads at 61 s, three slot reads and copy cards at 7-8 s, the real-wording probe: one chain of 956.2 s, 09:34-09:50 on 2026-10-20, registered ~18 min; the zero-training control 194 s and the per-cell training-trace read 24.7 s; the build 09:05-09:34 on CPU. The pre-registration's Cost line says the build ran to 10:30 -- written before the clock was read; 09:34 is the launch log's stamp.

**The owner's go, 2026-10-20**: "let's do A2 and structures". Finding 179's
limit, unchanged under A2 (finding 180): his binding line reads new words in
the eight trained clause structures and fails new structures. GENERATORS §2
says he memorises whatever layer is held fixed, so the structure was
**composed from parts** rather than listed (`corn/branchstructgen.py`): four
clause orders, three polarities, five ways of introducing the other
continuation, hedges, separators, sentence breaks, openers, preambles and
afterthoughts -- 23 trained cells, 5 held by combination, 5,839 structures
none seen more than 10 times. One variable against A2: the payload. Everything
else is A2's -- the replay, 650 iterations, the pick under loss, the runtime's
menu in his line's order, arm E2's three starts. Pre-registered at cf24839
(`configs/mix_v3_bind_ft_struct.py`) after a zero-training control read and
before a byte trained; `check_branch.py` section 16 holds the payload, with a
second reader re-deriving every gold and cell from the words.

## The registered read

His line exact (`probe_branch_bind.py --line-order`; the structure rows
`evals/funcworld_branchstruct.jsonl`, finding 180's rows
`evals/funcworld_branchflip_bind_order.jsonl`); far probe pairs right of 58
(`probe_bind_real.py`):

    run          struct rows       held rows         finding 180's rows   far probe
                 (gate 0.94)       (gate 0.90)       (gate 0.97)          (gate 48)
    A2 ev2       328/720 0.46      324/480 0.68      1,714+ (finding 180)    40
    A2 ev2s2     328/720 0.46      292/480 0.61                              34
    A2 ev2s3     320/720 0.44      328/480 0.68                              38
    struct ev2   504/720 0.70      302/480 0.63        816/1,728 0.47        23
    struct ev2s2 490/720 0.68      296/480 0.62        824/1,728 0.48        26
    struct ev2s3 516/720 0.72      306/480 0.64        858/1,728 0.50        29

**Every gate fails at every start.** The prediction (installs and transfers
at 3 of 3, the far probe at 2 of 3) was wrong on all four. The pick half is
untouched: the gold-line pick on unmet reads 864 of 864 at every start, and
the forged line is followed on every prompt -- the runtime's menu still turns
"the other one" into a position.

## Read by cell, on his own training traces

The pre-registered row for a missed install says read the training traces
by cell before more dose. The first slot, both continuations scored, on the
first 1,500 payload traces (trained; scratch `slot_by_cell.py`, probe only --
not on disk), two starts:

    reads (0.86-0.98 at both)                   at chance or below
    CXY pos CLAUSE  if it's v, X; if not, Y     XCY pos TRAIL   X if it's v, Y if it isn't    0.21 / 0.33
    CXY neg CLAUSE  if it isn't v, X; if it     XCY neg LEAD    X if it isn't v, otherwise Y  0.40 / 0.25
                    is, Y                       XCY neg TRAIL                                0.53 / 0.28
    XCY neg CLAUSE  X if it isn't v -- and if   XCY pos LEAD    X if it's v, otherwise Y      0.49 / 0.49
                    it is, Y                    YXC (all four)  Y, but X instead if it's v    0.49-0.67
    XCY unl CLAUSE  X unless v, in which case Y
    XCY unl TRAIL   X unless v; Y if it is
    CXY unl CLAUSE                              between: CXY LEAD and TRAIL 0.59-0.84,
                                                YCX 0.69-0.88

**The split is whether each continuation carries a condition clause of its
own.** Where Y is introduced by "if not", "if it is", "in which case", he
reads it -- either side's clause gives the answer. Where Y has only
"otherwise", "else", or a tail after it, he must attach the one condition to
the right continuation and take the other one for Y, and that does not form.
The old eight families are mostly of the second kind (P1, P1n, P3, P3n), and
A2 held them as a table; with their share cut from all of the payload to a
quarter, the table went and nothing general replaced it.

## Read by hand, and the rule it points at

The three-way probe prints his line beside the gold. On finding 180's rows,
"I'd like a spot for a pint as long as it's quiet -- else a place for dinner"
gets `if: quiet -> a place for dinner`, and its twin with the two continuations
swapped gets the other one: he named **the continuation after the condition**
on both orders. Tested over every prompt (scratch `forward_rule.py`): on the
1,032 prompts of finding 180's rows where attaching the condition to the
continuation after it gives the wrong answer, the structures arm follows that
rule on 0.63-0.65 and the gold on 0.35-0.37 (A2: the gold on 1.00). On the
structure rows the same split reads 0.65-0.73 on both sides -- **a lean
toward forward attachment, not a rule he follows everywhere.**

## The far probe, by shape

Pooled over the three starts (6 a shape). What reads 5-6 of 6 is the
own-clause kind, in words and shapes no cell holds: "when it's not v, A;
when it is, B", "assuming it's not v, A; if it is, B instead", "unless it's
v I'd like A; if it is, then B", "if by chance it's v, A; if not, B" (A2: 1 of
6), and **"is it v? then A. if not, B" -- a question, pre-registered as beyond
every cell -- 6 of 6 (A2: 0 of 6).** What falls to 0 of 6 is the else-word
and tail kind A2 read: "should it be v, A -- B otherwise" (A2 6), "A when it's
v, B the rest of the time" (A2 6), "B if it's v, A if it's not" (A2 6), "A if
it isn't v at all, otherwise B" (A2 6). Of the five shapes pre-registered as
covered, "go for B, but if it's not v, A" rose 0 to 4 of 6 and the other four
read 0-2.

**The vocabulary column fell**: 0 / 0 / 1 of 6 against A2's 5 of 6 -- on its
near-trained shapes, all of the else-word kind.

## The copy row, a side column

`tool.copy_wide` 294, 283, 293 against the starts' 298, 295, 293 -- not
readable by finding 170's rule. The second start falls again, by 12 where A2
fell by 47; its digit species (finding 180) still owes a cause.

## What it licenses

* **Composing the structure took the table away and the general read did not
  form in its place** -- finding 173 one layer up (the flip words took away
  the wording table and nothing formed until the binding line put the hop in
  the bytes, finding 175). GENERATORS §2's "a low lookup route is necessary
  and not sufficient" holds at the structure layer.
* **The hop he does not make is "otherwise means the other one"** -- the
  complement findings 175-179 could not form at the pick and finding 180 gave
  to the runtime as a menu position. At the line it is the same operation,
  and the eight families had held it only as eight memorised shapes. Where
  the request itself states the complement ("if not, Y"), the line reads
  structures it never saw, a question form included.
* **For the 1.0 branch slice**: composed structures alone are not enough at
  this dose; the else-word and tail kinds need the complement made visible --
  in the bytes he trains on, or by the runtime -- before variety can teach
  them. Which of those is the owner's.
* **More dose is not indicated**: two passes left the else-word cells at
  chance on their own training traces, not near a ceiling a third pass
  would reach (GENERATORS: dose amplifies a step, it does not create one).

**What it does not settle.** Whether pretraining on the composed payload (a
fresh start rather than a fine-tune over A2's table) forms the else-word read;
whether a mix keeping the eight families at full share beside the composed
cells holds both; what in the bytes would make "otherwise" visible; and the
second start's copy species.
