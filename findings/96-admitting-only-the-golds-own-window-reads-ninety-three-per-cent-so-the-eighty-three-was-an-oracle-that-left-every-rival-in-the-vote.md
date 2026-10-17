# Ninety-sixth finding — admitting only the gold's own window reads ninety-three per cent whatever the threshold, so the ninety-fifth finding's eighty-three was an oracle that left every rival in the vote, and the residue is two coupled levers of similar size

`scripts/probe_reader_rank.py` read (g), 2026-09-03. **Replay only** — no GPU,
no decode, no weight read, no tokenizer, **and no new harvest** — over
`nullpr_s{1,2}_popa.json` joined to `pairs_built_s{1,2}_popa.json`, the same
join the ninety-fifth finding checked and this run re-checks: **3,893 of 3,893
windows on both seeds**. `evals/results/rank_s{1,2}.json`.

**This finding corrects the one before it and takes the number up, not down.**
The ninety-fifth finding read `ORACLE_JOINT` at 82.8% and 81.0% and called it
"the ceiling on everything downstream of candidate ranking". It is not, and the
reason is one line of the code it was read from.

## 0. What `ORACLE_JOINT` hands over, and the thing it leaves alone

`verdict_oracle`'s `fix_window` **adds** the best gold-bearing window to the
real admitted mask:

    mask = list(admitted(row, t))
    ...
    mask[max(pool, key=lambda i: row["margins"][i])] = True

Every window that cleared the threshold on its own is still in that mask, and
`reduce` still counts all of them. So a passage whose gold window is forced in
and then **outvoted by two admitted repetitions of a rival** fails under
`ORACLE_JOINT` exactly as it fails under the shipped reader. That is not a
hypothetical: it is `AGGREGATION`, which the ninety-fifth finding measured at
66 and 60 passages at SHIPPED and left unexplained in its own last paragraph.

`ORACLE_JOINT` is therefore a ceiling on **locating and picking**, conditional
on the rest of the vote staying as it is. It is not a ceiling on the reader.

## 1. The two oracles that remove the rivals instead

Read (g), added to the same file, admits **exactly one** window:

    ONLY_GOLD        the mask is the highest-margin gold-bearing window and
                     nothing else; the head keeps its own pick on it.
    ONLY_GOLD_PICK   the same single window -- preferring, since the pick is
                     also handed over, a gold window whose ten actually hold
                     the gold -- with the gold substituted wherever they do.

Everything else is `verdict_at`'s own code: the `hybrid` fallback's second
`reduce` call, `local=False`, the same `judge`. **Unanswerable rows have no
gold-bearing window, so they keep the real mask and therefore their real
verdict** — the correct-silence column below is unchanged **by construction and
not by merit**, which is the ninety-third finding's §6 caveat applying for the
third finding running and not getting smaller for being repeated.

Both read the answer. Both are ceilings and neither is an arm.

## 2. Seventy-one and ninety-three, and the second one does not depend on the threshold

    SHIPPED  t = -2.02 + extent rule d = 2.0     seed 1            seed 2
      baseline                                 389  53.9%        409  56.7%
      ORACLE_PICK      pick, admitted windows   449  62.3%  +60   493  68.4%  +84
      ORACLE_WINDOW    window added to the mask 444  61.6%  +55   449  62.3%  +40
      ORACLE_JOINT     both, rivals left in     559  77.5% +170   573  79.5% +164
      ONLY_GOLD        one window, head's pick  515  71.4% +126   499  69.2%  +90
      ONLY_GOLD_PICK   one window, gold's pick  672  93.2% +283   670  92.9% +261
      GUARD            ECHO_BLOCKED 22          699  96.9%

    JOINT  the CV'd folds, extent off            seed 1            seed 2
      baseline                                 367  50.9%        368  51.0%
      ORACLE_JOINT                             597  82.8% +230   584  81.0% +216
      ONLY_GOLD                                501  69.5% +134   489  67.8% +121
      ONLY_GOLD_PICK                           672  93.2% +305   670  92.9% +302

**`ONLY_GOLD_PICK` reads 672 and 670 at both operating points, to the
passage.** That is not a coincidence and it is the structural point of the
read: once the mask is one forced window and the span on it is the gold, an
answerable passage's verdict cannot depend on the threshold, because the
threshold only decides admission and admission has been taken away. The extent
rule cannot reach it either, for the same reason — the pick is already the
gold. **93.2% and 92.9% is a ceiling on the whole stack below candidate
enumeration, invariant to both of the constants `corn/reader.py` ships.**

`ONLY_GOLD` *does* move between the points, by +14 and +10, and the only thing
that differs is the extent rule. That is the extent rule's worth under a
perfect window, and it is small, which is what the eighty-fifth finding
measured it as under a real one. **`ONLY_GOLD` is threshold-invariant too**,
for the same reason and with the extent rule held: its mask is also exactly one
forced window. §2a is the check.

### 2a. Seed 2 at its own operating point, added after the ninety-seventh finding

**The seed-2 column above is read at -2.02, and -2.02 is seed 1's constant.**
The ninety-seventh finding puts the bar protocol in a committed script and
measures what that costs: seed 2's own cross-validated mean is **-1.6730**, and
at -2.02 it reads 409 right at **170** correct silences, thirty below the floor
PRIMARY names. So the seed-2 column above is not a point this project would
ship. Re-read at seed 2's own constant:

    seed 2 at -1.6730 (its own bar-CV mean)      right   of 721
      baseline                                    390    54.1%
      ORACLE_PICK                                 454    63.0%   +64
      ORACLE_WINDOW                               454    63.0%   +64
      ORACLE_JOINT                                581    80.6%  +191
      ONLY_GOLD                                   499    69.2%  +109
      ONLY_GOLD_PICK                              670    92.9%  +280
      what ONLY_GOLD_PICK misses  51: ECHO_BLOCKED 21, OUTSIDE_TEN 26, neither 4

**Every conclusion in this file survives and two of them tighten.**
`ONLY_GOLD` reads **499 at both -2.02 and -1.6730**, and `ONLY_GOLD_PICK`
**670 at both**, which is §2's invariance claim demonstrated at two thresholds
rather than argued from the code. What moves is the baseline (409 to 390) and
therefore the deltas, and the two levers become **+109 admission-alone and +64
pick-alone against +280 jointly** on seed 2 — still super-additive, still of
comparable size, and now with admission the larger on both seeds rather than on
one.

**Against the owner's 85% = 613 of 721:** `ONLY_GOLD` is 98 and 114 passages
**short**; `ONLY_GOLD_PICK` is 59 and 57 passages **over**. So the target is
not ruled out by anything measured here, and it is not reachable by admission
alone.

## 3. Two levers of similar size, and they are coupled

    what it is worth                        seed 1    seed 2 at -2.02   at its own
    pick alone       ORACLE_PICK - base       +60          +84            +64
    admission alone  ONLY_GOLD - base        +126          +90           +109
    pick after perfect admission             +157         +171           +171
    admission after perfect pick             +223         +177           +216
    both             ONLY_GOLD_PICK - base   +283         +261           +280

**Admission is the larger lever on both seeds once seed 2 is read at its own
threshold** — +126 against +60 on seed 1 and, from §2a, +109 against +64 on
seed 2 — and the sum of the two alone (186 and 173) is well under the joint 283
and 280. (Read at seed 1's constant, seed 2's two levers come out level, +90
against +84; that apparent parity is the wrong-threshold artefact §2a removes,
and it is left here because the row above it is.) **Strongly super-additive,
for the same reason the ninety-fifth finding gave and with a sharper edge on
it:** fixing the pick on a window that never gets admitted buys nothing, and
admitting the right window buys nothing if the head then speaks a rival from
it. The correct reading of the residue is not "admission is the lever". It is
**two levers of comparable size that have to move together**, and an arm that
moves one while the other stands still will read a fraction of its own bound.

## 4. The pick failure is confident, not a near miss

On the `RANK_2_10` passages — the plurality of the residue, 168 and 182 at
SHIPPED — how far the head's argmax leads the gold, in span-head logits, on
that same window:

                        seed 1              seed 2
    median              3.72                3.05
    quartiles      1.99 / 5.90         1.53 / 5.83
    within 1.0     22 of 168  13.1%    33 of 182  18.1%

**Three and a half logits is not a tie a re-ranker breaks.** Seven passages in
eight sit outside a one-logit band, which is why the eighty-sixth finding's
re-ranker never left the span head's own argmax rate and was retired for it,
and why the pick lever is a *head* problem and not a threshold problem. It also
says what §3's 157 and 171 passages would cost: something that changes the
score by several logits on the right span, not something that reorders ties.

## 5. What survives the strongest oracle, and it is almost entirely accounted for

    ONLY_GOLD_PICK still misses     seed 1          seed 2
      ECHO_BLOCKED                    19              21
      OUTSIDE_TEN                     29              26
      neither                          1               4
      total                           49              51

**Forty-eight of 49 and 47 of 51 are the two deductions already on the
record**: the `grounded` anti-restatement rule's 22 (`PLAN-READER-RESIDUE.md`
§3, the owner's open call) and a gold the pair enumeration never offered on
that window. `ECHO_BLOCKED` reads 19 and 21 rather than 22 because the oracle's
chosen span is not always the one the guard refuses. **One passage on seed 1
and four on seed 2 are unexplained by anything in this file**, and they are
printed rather than rounded away.

So the ceiling decomposes with nothing material left over, which is the
property `ORACLE_JOINT` did not have: its 162 and 148 misses were 22 guard
passages and about 130 of *something*, and the something was the rival windows
it had left in the vote.

## 6. Two corrections to the ninety-fifth finding, made where they were made

  * **§2's claim that `ORACLE_JOINT` is "the ceiling on everything downstream
    of candidate ranking" is withdrawn**, and a note saying so is in that file
    beside the claim. It is fourteen points below the oracle that removes the
    rivals.
  * **"The 58% ceiling was an artefact" overstates it, and that is withdrawn
    too.** `ORACLE_PICK`'s 58.1% and 58.9% are correctly computed over a
    different conditioning set — admitted windows — and the ninety-fifth
    finding's own §1 says exactly that two paragraphs earlier. The honest
    statement is that 58% is **a differently conditioned oracle**, and that
    quoting it as a bound on the reader was reading the conditioning off. That
    file's title is left as it was written, because a finding records what was
    claimed and the note records the correction.
  * **Two transcription errors in §1's by-species table are fixed:** seed 1's
    `CLIPPED` `OUTSIDE_TEN` is 1 and not 4, and its `UNGROUNDED` is 4 and not
    3, per `rank_s1.json`. No total, share or conclusion in that file moves.

## What this cannot say

**Every arm here is handed the answer, twice.** `ONLY_GOLD` is told which
window carries the gold; `ONLY_GOLD_PICK` is additionally told which of the ten
candidates it is. The ninetieth finding's locality rule had a plausible
mechanism and reached a *negative* fraction of its bound, and the ninety-third,
ninety-fourth and ninety-fifth findings are a record of real mechanisms
reaching small fractions of such numbers. **93% is what perfect information
buys and it is not a forecast.**

**The correct-silence column is unchanged by construction on every row of §2.**
A real window scorer admits and refuses on both halves of the population and
would pay in the unanswerable column, as every threshold move in the
ninety-second finding did. Nothing here prices that.

**`ONLY_GOLD` is a *stronger* hand-over than `ORACLE_WINDOW`, not a weaker
one**, and the two are not a range. Removing every rival window from the vote
is not something a scorer can do without also being right about which windows
to remove on the unanswerable half.

**The 23% label-noise floor from the ninety-fifth finding §6 still sits under
all of this**, is still one species and one model auditor, and the owner's
spot-check of 20 is still outstanding.

**Two seeds, one trunk, one population**, Population A under `hybrid`, at both
operating points, with each read's point stated.

## What follows

**The plan's arms are re-sized at SHIPPED in `PLAN-READER-RESIDUE.md` §7**, and
their ceilings are quoted against `ONLY_GOLD`'s 515 and 499 rather than against
`ORACLE_WINDOW`'s 444 and 449, which is a different and smaller thing.

**The two arms this decomposition names are the two levers**, and they are
pre-registered in that file rather than here: a verifier trained on the gold
passage's own non-gold windows as hard negatives (admission, bound 515 / 499),
and a bidirectional encoder over the cached window states feeding the existing
pair scorer (pick, bound 672 / 670 jointly). **The second was declined in the
ninety-fifth finding and the rationale for declining it does not apply to the
new claim.** It was declined because its stated mechanism — a causal trunk
cannot enumerate the gold, so the gold is outside the ten — is contradicted by
the 89%. The claim now is the opposite one: the gold **is** in the ten, the
head ranks it second to tenth on the plurality of the residue, and it does so
by a confident three and a half logits. That is a scoring failure over an
enumeration that already contains the answer, and it is what a richer state
over the same candidates is for.

**Left unexplained:** the ninety-fifth finding's `AGGREGATION` note is now half
answered and half open. §0 says why those 55 and 51 `RANK_1` passages fail —
the outvoting windows were in the mask and `ORACLE_JOINT` left them there — but
nothing here says whether the outvoting is one rival repeated across
overlapping windows or several different ones, which is the difference between
a dedupe and a scorer.
