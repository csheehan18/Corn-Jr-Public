# The depth limit is the linking word; re-showing uncovered text fixes it

**Full result:** The depth wall under the windowed runtime is the carrier word, not the depth: a chain built on a carrier he reads as a group reaches depth ten at 52-54 of 54 on arm S, one built on a carrier he does not stops at level one, and a runtime that re-presents the text he left uncovered takes arm S from 0.29 and 0.30 to 0.95 and 0.89 -- where arm F, never trained on views, stays at 0.19 and 0.37

A deep read of every failure behind finding 144, 2026-09-26, on the four
checkpoints it compared (arm F and arm S, seeds 1337 and 2337). No weight was
trained. Everything below is the probe's own items and runtime variants of it,
read through `scripts/probe_depth_diag.py` -- `probe_stepwise_depth.py`'s loop
with every step logged, reproducing the committed band to the level (77, 128,
123 and 124 of 420) before any variant was read. **A hand-built instrument on
synthetic chains: every number is a bound** (rule 28).

## Every failure, by cause

One cause per failed item at depths 6-15 (48 items a checkpoint), read off its
raw steps; levels lost in brackets:

    cause                                   F s1       F s2       S s1       S s2
    a carrier written flat, "a pair"        26 (207)    8 (39)     4 (30)     1 (9)
    a carrier written flat, "two things"    14 (109)    2 (12)    40 (267)   33 (229)
    copy loop / doubled carrier              2 (5)     30 (231)    --         6 (48)
    step read as social                      2 (12)     1 (7)      --         --
    full chains                              2          6          4          6

**On three checkpoints of four the wall is one species**: he opens the view's
group, writes its first member, and writes the next carrier's words flat --
`ask[the pair, ask[A] and two things, ask[B]]`. That level closes with no
child at the window's edge, the runtime re-presents the identical view, greedy
decoding writes the identical line, and the chain stops "stuck". F seed 2's
"loops" are vocabulary too, read in the lines: a doubled carrier
(`ask[the pair, ask[the pair, ...`) and a carrier rewritten as a connective
("twice over" as `ask[equally the currency of ...]`).

## It is the word, and which word depends on the checkpoint

Counted over every step line, a carrier written flat against opened:

    carrier          F s1     F s2     S s1     S s2
    a pair           72/26    15/65     6/48     3/35
    two things       10/109    4/98    51/22    50/28
    the other four    0-1 flat on every checkpoint

The views cured "a pair" and broke "two things". **Mono-carrier chains** --
the same items with one carrier at every level -- separate structure from
vocabulary directly. Levels right at depth 10, of 54 (full chains of 6):

    carrier            F s1     F s2     S s1     S s2
    the two of them    26 (1)   46 (0)   53 (5)   54 (6)
    the pair           17 (1)    2 (0)   52 (5)   54 (6)
    the two            32 (3)   20 (1)   16 (1)   49 (4)
    twice over          9 (0)   41 (0)    0 (0)   36 (2)
    a pair              0 (0)    4 (0)    0 (0)    0 (0)
    two things         17 (1)   10 (0)    0 (0)    0 (0)

**On a carrier he reads as a group, arm S under the unmodified runtime already
reaches depth ten almost perfectly; on one he does not, it never passes level
one.** The ceiling at three carriers (the hand probes) and the stepwise null
(finding 144) are both this.

**The open is his second choice, every time.** Re-scoring each flat write at
the fork, the opening token ` ask` ranks second on 57 of 57, 54 of 54, 132 of
133 and 19 of 21 forks (S s1, S s2, F s1, F s2), median probability 0.17-0.41
against 0.56-0.77 for the carrier word he chose, on every carrier with more
than one fork.

**The corpus does not explain which word.** The probe's exact context --
"and <carrier>," in the user text -- occurs 4 to 10 times per carrier in arm
F's whole corpus, and 0 to 7 more in the views; "the pair" works on S with 4,
"a pair" fails with 10. Every carrier is starved in that position, and what he
falls back on is a lexical prior that moves between arms and seeds.

## The runtime can route around it -- and needs arm S to

Five runtime variants, pooled levels right at depths 6-15:

    runtime                                          F s1   F s2   S s1   S s2
    base (finding 144)                               0.18   0.30   0.29   0.30
    no window (whole rest each step)                 0.00   0.20   0.04   0.16
    clean cut (view ends before the last " and ")    0.12   0.27   0.32   0.44
    gap: re-present uncovered text, he decides       0.24   0.37   0.96   0.91
    gap, the runtime forces the open                 0.38   0.37   0.96   0.91
    gap2: as gap, flat if he opens no group          0.19   0.37   0.95   0.89
    gapc: as gap2, only a gap ending in a comma      0.19   0.37   0.95   0.89

**The gap rule** uses no answer key: where two members he kept have words
between them in the shown text beyond "and" and commas, the runtime ends the
level at the first member and shows him the text from the gap. Read in the
lines, every re-presentation starts on the carrier he wrote flat, and arm S
opens it -- `ask[two things, ask[...] ...` -- because a view that starts on a
carrier is exactly what its 7,596 views trained. **Arm F, which never saw a
view, reads the same re-presentation as `social` or writes it flat again**, so
the rule does nothing for it. Finding 144 read arm S at its gate and called the
views not worth the 1.0 corpus; paired with this runtime, they are what makes
depth work. That recommendation is amended here; 144's reading stands.

**Natural connectives are where the rule could break, and on gold they are
common.** Between the members of a gold group, the naive rule fires on 466 of
1,764 gaps in the ladder eval (26%) and 7,431 of 15,543 in arm F's corpus (48%)
-- ", then", "plus", "with", "and the same for". Two guards, both measured:

  * **gap2** re-presents and, if he opens no group, puts the member back in the
    level. On chains with one corpus connective swapped in, arm S reads
    **0.93 and 0.90** with it at the last level (base 0.27 and 0.21) and **0.81
    and 0.91** with it before a nested carrier (base 0.25 and 0.31).
  * **gapc** fires only on a gap ending in a comma after a word -- the
    carrier's shape. On gold it fires on **9 of 1,764** ladder gaps and **160
    of 15,543** corpus gaps ("and, separately," and "on the one hand,"), and
    reads the same as gap2 on every item set.

## Faults in the instrument, found in the lines

  * **A one-member wrapper scores a right parse as 0.** `ask[find me ask[the
    two of them, ask[A] and ask[twice over, ...]]]` is every level right under
    an extra group; the probe reads the wrapper as a level with no members.
    Rare -- 2 of 84 items, S seed 1 -- but the same wrapper defeats gap2's
    fallback (`ask[ask[equally the capital of ...]]` read as a group).
  * **A resume after a vocabulary slip drops the open group** and splits the
    last level's two members across two levels.
  * **An identical re-ask is never detected.** Greedy decoding guarantees the
    same line; the runtime asks up to three times before calling it stuck.
  * **The window cuts mid-member** ("... and the"), which seeds copy loops
    and stray `social[...]` at the edge; every cut training view ends at a
    member.

## A decode-time nudge, started and stopped

Adding one nat to ` ask` after a line ending "] and" read, on arm S seed 1
only, 0.29 to **0.52** on the chain items and 0.27 to **0.60** with a
connective; the processor path reproduced base exactly at zero. The owner
stopped the sweep there -- one checkpoint, one value, no misfire read. Recorded
so it is not re-derived; not a result.

## What it does not say

Nothing about real requests. The chain items are synthetic, right-branching,
six carriers, one connective at most; the probe follows one chain, so a request
with branches at several levels -- the natural case -- was never run through
this runtime. Whether a seventh carrier, never nested in training, opens under
the gap rule is not tested, and it is the question for open English. The comma
guard is an English punctuation cue. Nano, two seeds, greedy decodes.

**Licenses** the plan in PLAN-PARSE-WEIGHTS section 8: repair the instrument,
put the gap rule with its fallback into the windowed interpreter
(PLAN-TAG-LANGUAGE rung 1) and read its misfire cost on natural requests, and
a carrier-coverage arm on top of S that trains every carrier at a nested
position and holds one out.
