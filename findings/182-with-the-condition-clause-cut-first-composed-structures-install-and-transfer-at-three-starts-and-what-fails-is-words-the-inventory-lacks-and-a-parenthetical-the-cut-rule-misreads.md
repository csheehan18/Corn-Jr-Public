# Copying the condition's clause first: new sentence shapes read, new words don't

**Full result:** With the condition's clause cut first, composed clause structures install and transfer at all three starts -- the trained cells 0.986-0.997, five held cells 0.979-1.000, every family on his training traces 1.00, "otherwise" and the default-then-late-switch order included; two gates miss, each read by hand to vocabulary the inventory lacks ("but not if": 54-66 of 64-80 misses on finding 180's rows, which read 0.992-0.997 without it) and to a parenthetical condition the cut rule itself attaches forward

**Cost:** three fine-tunes of 650 iterations at 20M (144, 143, 143 s, contended -- the card at 36%, a bound), two span reads a run (144-145 s and 106-108 s), three slot reads and copy cards at 7-8 s, the real-wording probe: one chain of 1,263.5 s, 11:15-11:36 on 2026-10-20, registered ~17 min (the span reads ran twice the estimate: two greedy lines a prompt); the build 11:02-11:15 on CPU.

**The owner's go, 2026-10-20**: "do 3" -- put finding 181's missing hop in
the bytes. Finding 181: with the clause structure composed from parts, the
one-slot line `if: v -> <the continuation taken when it holds>` fell to
chance wherever the condition attached backward ("X if it's v") or Y had only
"otherwise". Two hops sat inside the one choice: which continuation the
condition is attached to, and "otherwise means the other one". So the line
became two, each a copy (`corn/branchstructgen.py`, `StructBranch.span_line`):

    cond: X if it isn't raining     the clause holding the condition, run on
                                    to the clause its continuation stands in
    if: not raining -> X            that continuation, "not" when negated

The runtime orders the menu from the `if:` line -- what runs when the
condition holds first -- as A2's runtime already does; the menu and the pick
are finding 181's byte for byte. One variable against finding 181: the
payload's binding lines (1.88 passes against 1.96, the same weight).
Pre-registered at 9a788a2 (`configs/mix_v3_bind_ft_span.py`);
`check_branch.py` section 17 holds it; finding 180's rows were rewritten into
the form with every prompt byte for byte but the binding lines, so the old
eight are read on the requests A2 read.

## The registered read

The decision -- the continuation his `if:` line implies, which the runtime
acts on (`scripts/probe_branch_span.py`; his own two lines, the runtime's
menu from them, his pick on it):

    start   structure, trained   structure, held   finding 180's rows   far probe
            (gate 0.94)          (gate 0.90)       (gate 0.97)          (gate 48 of 58)
    ev2     718/720 0.997        478/480 0.996     1,648/1,728 0.954    37
    ev2s2   710/720 0.986        470/480 0.979     1,656/1,728 0.958    38
    ev2s3   716/720 0.994        480/480 1.000     1,664/1,728 0.963    37

    controls, the same requests:
    A2      320-328 0.44-0.46    292-328 0.61-0.68   1,714-1,724 0.99+  34-40
    181     490-516 0.68-0.72    296-306 0.62-0.64   816-858 0.47-0.50  23-29

**Installs and transfers pass at all three starts**: every YXC cell 44-48 of
48 (gate 41), no held cell below 0.94 (gate 0.75), own quads 176-179 of 180
and 116-120 of 120. His clause is exact on 708-718 and 466-480 of the same
prompts. **The old eight and the far probe miss at all three.** The pick half
holds: from the gold lines, every quad 144/144, 288/288, 180/180, 120/120.
The prediction (installs and the old eight 3 of 3, transfers and the far
probe 2 of 3) was right on installs, under on transfers (3 of 3), and wrong
on the old eight and the far probe.

On his own training traces the `if:` line's continuation, the gold clause
above it (`probe_bind_slot.py`), reads 1.00 in every family at all three
starts -- finding 181's arm read 0.61-0.70.

## The old eight, read by hand

The misses on finding 180's rows are one family: U1, 70, 66 and 54 of 264
against 0-8 for every other family. **Of those, 66, 66 and 54 are "but not
if"** -- "maybe a spot for a pint but not if it's windy -- then somewhere to
eat" -- an unless-word `branchflipgen` uses and the composed lists never
contain (`branchstructgen.UNLESSES` is "unless" and "except if"). He cuts the
clause without the condition ("maybe a spot for a pint then somewhere to
eat") or keeps it and drops the "not". Outside that word he misses 14, 6
and 10 of the 1,728 prompts: A2's level. Own quads, held-first 141-143,
held-second 128-134, flip 133-137; the held-second cell at 128 at the first
start is the same U1 misses. **A word, not a structure**: the vocabulary column, apart.

## The far probe, by shape

Pooled over the three starts (6 a shape):

* **The five shapes pre-registered as covered** -- a trained cell, new
  words -- read 21 of 30 (A2 0 of 30, finding 181 9): "if it turns out to be
  v, A; if it doesn't, B" 6, "B is the plan, but switch to A if it's v" 6,
  "go for B, but if it's not v, A" 6, "go with B, though if it's v make it A"
  3, "if it's v then definitely A, but if it's not then B" 0.
* **The else-word shapes finding 181 lost are back**: "should it be v, A -- B
  otherwise" 5, "A when it's v, B the rest of the time" 5 -- the
  pre-registered 4 of 6. The question form, beyond every cell, 6 of 6.
* **The vocabulary column**: 5, 6 and 5 of 6 (finding 181: 0-1).

What fails, read by hand on the first start's own lines:

    "A, unless of course it's v, in which case B"   1 of 6
    "A, but only if it's not v -- else B"            0 of 6
         his: cond: unless it's raining, in which case B / if: not raining -> B
         The condition stands between commas *after* the continuation it
         governs -- a parenthetical. The cut rule (a condition clause holding
         no continuation runs on to the next clause) attaches it forward, to
         B; he wrote what the rule says. The generator never writes a
         parenthetical, so the rule was never wrong on a trace: a hole in
         the format's definition, not in his reading.
    "A save for if it's v, in which case B"          0 of 6
         his clause exact; his "not" missing -- an unless-word never seen
    "B is the backup -- A provided it isn't v"       1 of 6
         he cuts the default clause, once writing "B is fine" -- a trained
         default marker for one never seen (GENERATORS §5's first signature)
    "if it's v then definitely A, but if it's not then B"   0 of 6
         he cuts "but if it's raining then definitely A" -- two clauses
         fused, "then definitely" never seen
    "A as long as it's anything but v", "B by default; A in the event that
    it's v"   1 of 6 each -- connectives never seen

## The copy row, a side column

`tool.copy_wide` 299, 281, 291 against the starts' 298, 295, 293 -- not
readable by finding 170's rule. The second start falls again, now in three
arms; its digit species still owes a cause.

## What it licenses

* **The hop in the bytes is the lever a layer up from finding 175.** With the
  attachment a cut and the complement the runtime's menu, composed clause
  structures install and transfer to held structure combinations at three
  starts of three, and "otherwise" and the late switch read where finding
  181 left them at chance. GENERATORS D5 holds at the structure layer.
* **What is left is vocabulary and one shape.** The far probe and the old
  eight fail on words the inventory lacks (unless-words, connectives,
  default markers), and on a parenthetical condition after its continuation,
  which the cut rule misreads. The 1.0 branch slice: the two-line form, the
  word lists widened to the connectives people use -- real text is the
  source finding 179 already named -- and a parenthetical cell with a cut
  rule that attaches it backward.
* **RULES 21 untouched**, and the pick his: both lines and the pick are his
  and under loss; the runtime orders the menu from his line.

**What it does not settle.** Whether widened word lists close the far probe
(a dose question once the words are in); the cut rule for a parenthetical;
pretraining at one pass in this form; and the second start's copy species.
