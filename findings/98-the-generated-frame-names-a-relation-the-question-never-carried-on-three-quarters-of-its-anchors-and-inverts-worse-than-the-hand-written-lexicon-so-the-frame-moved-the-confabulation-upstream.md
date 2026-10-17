# Ninety-eighth finding — the generated frame names a relation the question never carried on three quarters of the frames that carry an anchor, and inverts 29.3% there against the hand-written lexicon's 17.4%, so the frame moved the confabulation upstream; it also fires on no window at all three times as often as the lexicon, makes a call on 10.7% of the population against the lexicon's 18.8%, and misses both pre-registered bars

**The frame moved the confabulation upstream.** 75.7% of the frames that carry
an anchor at all name a relation the question never used, and on the subset of
those that make a call the frame inverts **29.3%** against the ninety-fourth
finding's hand-written lexicon at 17.4% and against the shipped verifier's
23.9/21.1 — the first line the pre-registration asked for if that number came
back worse, and it did.

`scripts/gen_frames_ft4g.py` (one generation pass, 1,003 questions, 25 s) and
`scripts/probe_frame_gen.py` (replay, both seeds), 2026-09-03.
`evals/results/frames_ft4g_popa.jsonl`, `evals/results/framegen_s{1,2}.json`,
and the control at `frames_ft4g_popa_rot.jsonl` /
`framegen_rot_s{1,2}.json`. Population: the ninety-third finding's read (e),
the **580** answerable passages carrying both a gold-bearing and a
non-gold-bearing window. `anchor_score`, the inversion definition and the
cross-fitted AUC read are **imported** from `probe_frame_window.py`, not
restated, so "the same statistic" is enforced by the import.

**Nothing was trained, no arm ran, no threshold moved, and the frame never
chose or restricted a span.** The frame ranks windows and that is the whole of
what was tested.

## 0. The bars, written before the pass, and both are missed

    bar                                        generated        lexicon
    coverage   makes a call on >= 60%        62/580  10.7%   109/580  18.8%   FAIL
    precision  inverts <= 20% where it calls  17/62  27.4%    19/109  17.4%   FAIL
    AUC        printed against +0.02, not a gate

    cross-fitted AUC, 'this window carries the gold'   seed 1     seed 2
    margin alone                                       0.8000     0.8147
    margin + generated anchor                          +0.0008    +0.0006
    margin + lexicon anchor                            -0.0014    -0.0000
    margin + both        (vs margin + lexicon)         +0.0007    +0.0006

**Both bars fail on both seeds, and the failing branch the pre-registration
wrote for "both fail" applies: the frame idea is closed at the
window-ranking level**, which was the last position the ninety-third finding
left it holding.

**The frame's own numbers are identical across the two seeds and that is
construction, not replication.** One generation pass serves both seeds — the
two harvests carry the same 1,003 ids in the same order, asserted at startup —
and gold-bearing membership does not depend on the seed either, so `62/580`
and `17/62` *cannot* differ. What the seed moves is the margin, the verdicts
and therefore the residue. The ninety-fourth finding's lexicon had the same
property and the same caveat.

## 1. Generation bought raw reach and lost it again at the window

Generation did the thing the ninety-fourth finding said it would, once:

    frames carrying at least one anchor    generated  416/1003   41.5%
                                           lexicon    263/1003   26.2%

And then, on the 580, the reach evaporates:

    of the 580 passages                    generated    lexicon
      no anchor produced at all                350         397
      anchor fires on NO window                159          52
      anchor fires on EVERY window               9          22
      anchor makes a call                       62         109

**That middle row is the finding.** The generated anchor is a word that is not
in the passage, three times as often as the hand-written one is. The
ninety-fourth finding predicted the opposite in as many words — a model "can
produce the passage's *own* phrasing rather than a guessed synonym" — and the
measurement is that the trunk writes in the **question's** register, not the
passage's. `where does the this is us family live` came back as *"the family
lives in ___"*: `lives` is a perfectly good frame word and the passage says
`Pittsburgh` in a sentence that never uses it.

The +47 passages generation buys on the "no anchor" row are more than paid
back by the +107 it adds to "fires on nothing".

## 2. Most of what the trunk writes is the question again

    frames carrying the blank `___`     683/1003   68.1%
    frames with a token stripped         38/1003    3.8%
    frames leaving no anchor at all      587/1003   58.5%

**Three frames in five are a restatement**: every content word already in the
question, or in `STOP`. *"what states do not allow daylight savings time"* →
*"the states do not allow daylight savings time"*. The blank is dropped a
third of the time as well, which is the same failure seen from the other side.

**The strip rule fired on 38 frames of 1,003 (3.8%), 17 of them in the
population.** That is rule 3 of the pre-registration doing its job — *"when
does the new adventure time come out"* came back as *"...comes out on 25th
September 2018"* with the gold being April 21, 2017 — and it is a small number
because the trunk rarely gets far enough to invent a date. It is not evidence
the frames are clean; §3 is the read that matters and it is not small.

## 3. The confabulation read, which is the first line

An anchor set is **grounded** when at least one anchor shares a stem with a
question content word, under crude suffix stripping plus a closed irregular
table (`sang`/`sung`, `wrote`/`written`, `born`/`birth`). The table is small on
purpose: one grown until everything matched could not find a confabulation.

    frames with anchors that name NO question relation   174/230   75.7%
      of those, how many make a call                          41
      the frame inverts there                             12/41   29.3%
    where the relation IS in the question                  5/21   23.8%
    the margin on that same novel-relation subset  10/41  24.4%  /  7/41  17.1%

    the ninety-fourth finding's lexicon, its own decisive set   19/109  17.4%

**29.3% against 17.4%, and worse than the margin it was supposed to help on
both seeds.** Rule 3 catches a frame that supplies a *fact*. It does not catch
one that supplies a *relation*, and that is where the trunk's invention went:
*"what is cain and abel software used for"* is framed as *"the abbreviation
cain is a software program used to ___"*, and `abbreviation` then scores every
window that happens to contain the word.

## 4. The control: it is not the exemplar block

The eight-exemplar prompt echoes its final exemplar. 129 of the 1,003 frames
came back about abbreviations and `dna`, `stands`, `abbreviation` are the three
most common anchors in the file by a factor of six. **On the population, 90 of
the 230 anchor-bearing frames (39.1%) have an anchor set that is nothing but
exemplar vocabulary.** That echo *inflates* coverage with anchors the idea did
not earn, so the primary run is the generous one.

The control rotates the exemplar order by `k % 8` so no exemplar is
systematically last. Second pass, 30 s, same rule, same reads:

                          primary            rotated control
    coverage           62/580  10.7%        66/580  11.4%
    precision          17/62   27.4%        20/66   30.3%
    pure exemplar echo 90/230  39.1%       104/232  44.8%
    AUC delta, s1/s2   +0.0008/+0.0006     -0.0003/+0.0006
    novel-relation inv 12/41   29.3%        13/43   30.2%

**Removing the systematic echo does not rescue coverage and makes precision
worse.** The failure is not a prompt artefact and a better exemplar block is
not the missing piece.

## What this cannot say

**It does not close the frame idea for a bigger model, and it does not open
it either.** What is measured is a 260M trunk at `iter 800`, prompted
eight-shot, greedy. Every number here is that vehicle's. What the finding does
establish is that the failure mode is *not* the one the ninety-fourth finding
diagnosed: the shortfall is not "the model cannot be asked", it is that when
it is asked it writes the question's words back, and when it reaches past them
it reaches for a relation the question did not carry.

**The exemplar block is a hand-written artefact and this finding is partly
about it.** Eight examples chosen on generation sanity over ten questions
before any window was scored — recorded in `gen_frames_ft4g.py`'s docstring,
including the four-example version that was rejected and the one exemplar
swapped out because its question is row-for-row in this eval set. §4 is the
control that bounds how much of the result belongs to it, and it bounds it at
"none of the direction".

**Nothing here re-prices the admission lever.** The ninety-sixth finding's
`ONLY_GOLD` at 71.4%/69.2% against a 53.9%/56.7% baseline is why a window
ranker was worth a test; that +126/+90 of room is still there and is still
unclaimed. This finding removes one candidate for claiming it.

**The population is the ninety-third finding's read (e)** — passages with both
kinds of window — so it says nothing about passages where every window carries
the gold or none does. **And the unanswerable half is untouched by
construction**, which is the ninety-third finding's §6 caveat applying for the
fourth finding running.

**Precision is measured on 62 passages.** McNemar against the margin on the
same passages reads p = 0.664 and p = 1.00 — the frame is not *shown* to be
worse than the margin where it calls, it is shown to miss a pre-registered
20% bar. The whole-word sensitivity variant reads 22.6% rather than 27.4% and
misses the bar too.

## What follows

**The frame is closed as a window scorer and should not be retried by
generating better frames.** Both branches the pre-registration wrote for a
single failure are ruled out by the two failing together: coverage did not
fall because the trunk declined to speak (it spoke on 41.5%, more than the
lexicon), and precision did not fall because coverage was bought (the control
buys less coverage and loses more precision).

**The one thing the generated frame did buy is not a frame.** 47 passages
gained an anchor where the lexicon had none. If anything survives here it is
that the trunk can be prompted into a declarative restatement 68% of the
time; that is a text-shape capability and no read in this file suggests it
carries information about which window holds an answer.

**The ninety-fourth finding's §2 parity result stands as the ceiling on the
whole idea**, and it was never a demonstrated win — p = 0.32 and 0.62. A
hand-written lexicon at 17.4% on 109 passages is the best any anchor has done
on this population, and it missed the AUC bar by a factor of four.

**Left unexplained:** the generated anchor's own window-level AUC is 0.5104,
which is *chance*, against the lexicon's 0.5288 — yet on the decisive subset it
inverts at 27.4% while a coin would sit near 50%. Something in the 62 is
informative and the 2,498 windows are not, and no read here separates which 62
they are.
