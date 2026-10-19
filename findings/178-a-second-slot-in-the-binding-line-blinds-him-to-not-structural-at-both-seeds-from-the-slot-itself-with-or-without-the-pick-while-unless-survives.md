# Naming a second branch blinds him to 'not'

**Full result:** A second slot in the binding line blinds him to "not": the negation read fails to form on his own training traces at both seeds (0.50, 0.66 against the one-slot line's 0.99, 0.96), the slot does it with or without the pick being trained (0.58 with the pick masked), the one-slot line's own loss builds most of the read (0.86 with its pick masked), and "unless" survives the second slot while "not" does not

**Cost:** four nano runs (1,174, 1,155, 1,160 and 1,144 s, contended where the card was shared -- the card at 30-40%, a bound), the training-trace slot reads ~30 s each and the three-way reads ~2 min each on the card; 2026-10-17 13:16-14:52. The CPU analysis of findings 175-177's items ran first, at no card cost.

**The owner's question after finding 177: why does a second slot cost the
negation read?** Finding 175's binding line names one branch (`if: raining
-> X`) and reads the negated families' first slot at 0.97 held-out.
Findings 176 and 177's lines name two (`if: raining -> X | else -> Y`, the
else slot trained in 176 and the runtime's in 177) and read it at 0.45 and
0.53. The context at the first slot is byte-identical across the three, so
the cause had to be what the rest of the trace trains. Four arms, each
pre-registered before a byte trained (f7670ac, 3349474, 35dfe23): findings
175 and 176 at a second seed, and each with the pick line out of the loss
(`loss="no_pick"`, a new policy in `corn/data.py`, held by `check_branch.py`
section 13 with a mutant). **Cards:**
`evals/results/nano20m_v3_fw_branchflip_{bind,bind2}_seed2__*`,
`..._nopick__*`, `..._bind2_nopick__*`; the training-trace read is
`scripts/probe_bind_slot.py` (bound choice, 600 traces from the front of the
payload), committed with the seed arms.

## The failures, by hand first (findings 175-177's items)

The negated families' wrong first slot is always the continuation named
first, which is also the one in the negated condition's own clause. He reads
"X if it's not raining" as "X if it's raining". The miss spreads across every
"if" word and every "otherwise" word. "It's not" fails more than "it isn't"
on held-out rows (176: 0.36 against 0.58; 177: 0.31 against 0.65), the
first holding the same "it's" token as a positive condition. On training
traces the two forms read alike (0.50 / 0.51), so that split is weak.

## The registered reads -- the negated first slot on his own training traces

    arm                                          seed     negated    plain    "unless"
    one-slot line, pick trained (175)            1337      0.99      0.96      0.97
    one-slot line, pick trained                  2337      0.96      0.97      0.94
    one-slot line, pick masked                   1337      0.86      0.96      0.95
    two-slot line, pick trained (176)            1337      0.50      0.89      0.98
    two-slot line, pick trained                  2337      0.66      0.70      0.93
    two-slot line, runtime else (177)            1337      0.59      0.82      0.87
    two-slot line, pick masked                   1337      0.58      0.68      0.96

**Structural, not a coin**: the one-slot line builds the negation read at both
seeds, the two-slot line at neither -- the seed arms' registered row, as
predicted. **Most of the read comes from the binding line's own loss** (0.86
with the pick masked) and the one-slot pick adds the rest -- the "between"
row, against a prediction of 0.70 or below. **The second slot itself does the
damage**: with the pick masked the two-slot line still reads 0.58 -- the
registered row "the second slot itself damages it", against a prediction that
the pick's training was the culprit. Held-out rows agree: the seed-2337
one-slot line exact on 0.97-0.98 of prompts, the two-slot 0.57-0.67; the
one-slot pick-masked line 0.89.

## What the two-slot line writes

Every two-slot line on findings 176's held-out rows, both seeds and the
pick-masked arm, classified by the order of its two continuations (the
correct order is the request's on plain sentences, the reverse on negated and
"unless" ones):

    family     in the request's order    reversed     one phrase twice
    plain          0.60 - 0.73          0.11 - 0.27     0.11 - 0.16
    negated        0.36 - 0.46          0.32 - 0.51     0.12 - 0.22
    "unless"       0.00 - 0.02          0.87 - 0.94     0.05 - 0.11

**He all but stops telling plain from negated** -- the two families' lines
split nearly alike, about sixty-forty -- **while "unless" stays read.**
"Unless" is a word of its own before the condition; "not" sits inside it
("it's not raining", "it isn't raining"), one token from the positive form.
With a second slot in the line, the cue that separates the two forms is the
one that does not form. It is not a plain shortcut of copying the request's
order: plain sentences, where that order is right, fall too (0.96 to
0.68-0.89).

**The copy row, a side column**: `tool.copy_wide` 294, 299, 275 and 253 of 300 on the four arms, inside
the 20M family's spread (242-300, finding 170).

## What it settles and what it does not

* **Settled:** the cost is structural; it comes from the second slot, with or
  without the pick's training; the one-slot line's own loss builds the
  negation read to 0.86, and the pick to 0.96-0.99; "unless" survives the
  slot and "not" does not.
* **Open:** the circuit-level why. The damage needs the second slot plus some
  training signal that touches it -- its own loss (176, here) or the pick
  reading it (177). The untested cell is the slot present with neither
  trained. And why a buried flip word, and not a separate one, is the read
  that fails.

## What it licenses

The one-slot binding line is the format that reads every flip word: 0.94
held-out at seed 1337, 0.97-0.98 at 2337. Anything that puts the second
continuation into the line costs the "not" read, so a fully-his pick from a
two-slot line pays for itself with the negation read. On the record that
leaves two ways to finish branch on the one-slot line:

* **His binding, the runtime's move** (finding 177's zero-training read:
  127, 140, 122 of 144 at seed 1337) -- the runtime resolves the move from his
  line and the result.
* **His binding and his pick**, where the pick's weak point on the one-slot
  line is the complement ("the other one" on an unmet result: 0.40 at seed
  1337). Read on the seed-2337 one-slot checkpoint, its own quads are 59,
  47, 19 -- the pick at 2337 is better than at 1337 and still the weak half.
