# A 16-word hand-written lexicon matches the trained checker where it applies

**Full result:** A sixteen-entry hand-written anchor lexicon ranks windows level with the trained verifier on the passages where it speaks, adds +0.005 AUC against a bar of +0.02 because it is silent on four fifths of them, and so the frame idea's binding constraint is coverage

`scripts/probe_frame_window.py`, 2026-09-03. **Replay only** — no GPU, no
decode, no weight read, no tokenizer, **and no model writes the frame** — over
`nullpr_s{1,2}_popa.json`. Population: the 580 answerable passages carrying
both a gold-bearing and a non-gold-bearing window, which is the ninety-third
finding's read (e).

That finding relocated the frame proposal's target. Its own worked example —
*"who sang the theme song from russia with love"* — is neither a localisation
nor a within-window selection failure: the window whose sentence reads *"...and
sung by Matt Monro"* was ranked **below two windows containing no answer at
all**, and the top one spoke. And a no-gold window outranks every gold-bearing
one on **2.8%** of the passages he gets right against **47.8% and 41.0%** of
the residue.

So this asks the question that decides where a frame belongs: **does the
presence of a question's answer-frame anchor separate a window that carries
the gold from one that does not?**

## The bar, and it is missed

Written before the run: the anchor must add **+0.02 AUC over the margin
alone**, cross-fitted, on both seeds.

    cross-fitted AUC, 'this window carries the gold'   seed 1     seed 2
    margin alone                                       0.8646     0.8598
    margin + anchor                                    0.8697     0.8656
                                                       +0.0050    +0.0058
    margin + question-overlap (control)               -0.0044    -0.0033
    margin + anchor + overlap                          +0.0004    +0.0031

**+0.005 and +0.006 against a bar of +0.02.** The sign is positive and
identical on both seeds — the first consistently-signed cross-fitted signal
this workstream has produced, against `agree_top`'s below-chance 0.48 in the
ninety-second finding — but it is a quarter of what was asked for.

The question-overlap control fails again, as the ninetieth and ninety-third
findings both predicted: it *subtracts* AUC on both seeds.

## 1. Why it misses: it is silent, not wrong

    coverage
      lexicon fires on               183 of 580 passages   31.6%
      of the residue among them       75 of 293 / 295      25.6% / 25.4%
      makes an actual call
        (score not constant across
         a passage's windows)        109 of 183            59.6%

**The lexicon speaks on 109 of 580 passages — 18.8%.** Sixteen anchor families
keyed off question verbs cover a third of questions, and on 40% of those every
window scores the same, so the score cannot rank them. The ninety-first finding
predicted this exactly: 62% of the residue is questions with no nameable
constraint, and a frame lexicon is a constraint lexicon.

**Read (d) shows it is informative where it fires**, and noisily:

    fires on 153 of 264 gold-bearing windows    58.0%
    fires on 177 of 509 windows with no gold    34.8%

58 against 35 is a real difference and it is also a lot of both errors.

## 2. Where it speaks it is level with the trained verifier

Restricted to the 109 passages where the anchor is non-constant — where it
makes a call at all — against the shipped verifier's margin on **the same
passages**:

                              seed 1              seed 2
    anchor inverts        19 of 109  17.4%    19 of 109  17.4%
    margin inverts        26 of 109  23.9%    23 of 109  21.1%
    paired, anchor wins        22                  20
    paired, margin wins        15                  16
    McNemar                p = 0.324           p = 0.618

**It is not a demonstrated win and the finding says so.** The direction is
consistent across seeds and the paired test does not clear 0.05 on either;
19 against 26 on 109 passages looks decisive printed side by side and is not,
which is why the paired test is in the file. An earlier version of this read
printed the two rates without one.

**What is fair to say is parity.** A sixteen-entry hand-written lexicon ranks
windows about as well as a verifier trained on cross-fitted labels over the
trunk's own states, on the passages where the lexicon has an opinion. That is
not nothing: the two are not correlated by construction, and the lexicon cost
an afternoon.

## 3. So the binding constraint is coverage, and coverage is what generation buys

The three numbers together say one thing:

  * the anchor is **right when it speaks** (§2, parity with the verifier);
  * it **rarely speaks** (§1, 18.8% of passages);
  * and the AUC bar is missed by the product of those two (§ the bar).

**A generated frame differs from this lexicon in exactly the dimension that
binds.** A model conditioned on the question and the passage can produce an
anchor for the 68% of questions no hand-written family covers, can produce the
passage's *own* phrasing rather than a guessed synonym, and gives a graded
score where this gives an integer in {0, 1, 2}. Every one of those attacks
coverage or ties; none of them is needed for precision, which §2 already has.

That is the first time this workstream has had a result that argues *for*
building the expensive version rather than against it.

## What this cannot say

**It does not show a generated frame would clear the bar.** It shows that the
thing a generated frame would fix is the thing that is broken here. Those are
different claims and the ninetieth finding is the standing reminder — its
locality rule had a plausible mechanism and reached a *negative* fraction of
its own ceiling.

**Parity is not improvement.** §2's p-values are 0.32 and 0.62. If a generated
frame reaches only the same per-call accuracy at four times the coverage, the
arithmetic is still worth having, but the per-call accuracy is unproven and
the honest reading is that it is somewhere around the verifier's.

**The lexicon is mine and it is arbitrary.** Sixteen families, chosen by
reading question types, with the boundary between "a family" and "a synonym
list" set by judgement. A different lexicon would give different coverage; the
`as ` entry alone is a substring that will fire on much prose.

**The population is the ninety-third finding's read (e)** — passages with both
kinds of window — so it says nothing about passages where every window carries
the gold or none does. And nothing here touches the *runtime*: no arm was run,
no threshold moved, no passage bought.

## What follows

**Build the generated frame, and build it as a window scorer.** Not a locator
(the ninety-third finding bounds that at +15/+18), not a re-ranker over the
head's ten (bounded at 58.1%/59.0%), but a term in the admission decision —
which is 70% of the residue and outside both bounds.

**Its first bar should be §2's number and not the AUC bar.** The question a
generated frame has to answer is whether it keeps per-call parity with the
verifier while speaking on four to five times as many passages. That is
measurable on this same population with the same reads, and read (d2) is
written to take it.

**And it should be scored against `margin + anchor`, not against `margin`.**
Otherwise a generated frame gets credit for the +0.005 the hand-written one
already provides.

**Left unexplained:** the anchor and the margin disagree productively in both
directions — 22 passages where the anchor is right and the margin wrong, 15
the other way, on seed 1. A combination that beat both would need to know
which to trust, and nothing here says what that would key on. The 15 are the
more interesting half and have not been read.
