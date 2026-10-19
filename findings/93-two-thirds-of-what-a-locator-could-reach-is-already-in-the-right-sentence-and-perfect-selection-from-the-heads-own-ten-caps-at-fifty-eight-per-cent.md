# A perfect sentence finder would be worth only 15-38 passages

**Full result:** A perfect locator is worth fifteen to thirty-eight passages because two thirds of what it could reach is already in the right sentence, and a perfect choice among the head's own ten caps the whole family at fifty-eight per cent

`scripts/probe_frame_ceiling.py`, 2026-09-03. **Replay only** — no GPU, no
decode, no weight read, no tokenizer — over `nullpr_s{1,2}_popa.json` and
`pairs_built_s{1,2}_popa.json`, whose spans are verified aligned on all 1,003
rows rather than assumed. Baselines 367 right / joint 600 and 368 / 575.

The frame proposal, 2026-09-03: let him sketch the answer's shape before he
looks for it — *"the theme from Russia With Love was sung by ___"* — and use
the sketch to find the matching text, near "sung by" rather than near some
other name in the paragraph.

**This finding does not test that idea. It bounds it, which is cheaper and
comes first.** Whatever a frame is for, its job as a *locator* is to say which
part of the window to read. So hand the head the gold's own sentence for free
and see what it then gets right: no locator can beat that, and the number is
what the proposal should be read against. The three arms that died earlier
today all had a one-line version of this read that would have preceded them.

## 1. Two thirds of the addressable residue is already in the right sentence

Over admitted windows **that carry the gold** — and only those; see the
correction below:

    seed 1 (127 windows)          seed 2 (157 windows)
    SAME_SENTENCE    82  64.6%    110  70.1%
    OTHER_SENTENCE   40  31.5%     42  26.8%
    SPLIT_LOST        5   3.9%      5   3.2%

    by species, seed 1 / seed 2      SAME      OTHER     SPLIT
    RIVAL                           21 / 32   28 / 30    0 / 0
    AGGREGATION                     33 / 45    4 /  3    5 / 5
    CLIPPED                         24 / 30    1 /  0    0 / 0
    UNGROUNDED                       4 /  3    7 /  9    0 / 0

**`SAME_SENTENCE` is the dominant case and a locator cannot touch it.** He is
already reading the sentence that contains the answer and picking the wrong
span out of it — the composer standing next to the singer in the same clause,
where pointing at "sung by" does not separate two names that both sit beside
it.

(The frame proposal's *own* worked example is not of this shape and is not of
`OTHER_SENTENCE`'s either — §5 traces it and finds a third thing again. That
is the finding's most useful passage and it is why §5 exists.)

`OTHER_SENTENCE` — the whole addressable set — is **31.5% and 26.8%**, and it
is almost entirely `RIVAL`. `SPLIT_LOST` is negligible, so the sentence
splitter is not distorting this.

**A correction, because the first version of this read said 55%.** It counted
every admitted window and labelled one with no gold in it `GOLD_ABSENT`, which
pooled "the sentence split lost it" with "the answer was never in this
window". The tell was that all of `REFUSED_WRONG` and `REFUSED_RIGHT` landed
in that bucket — species *defined* by having no admitted gold-bearing window.
Restricted properly, the splitter accounts for 4% and 3%, not 55%.

## 2. The gold is not among the head's ten on seventy per cent of the residue

    gold reachable in the head's top ten, on some admitted window
      seed 1   95 of 354 residue passages   26.8%
      seed 2  111 of 353                    31.4%

**A locator can only promote a candidate the head already produced.** On
roughly seventy per cent of his failures the correct answer is not among the
ten things he considered, and no amount of better choosing reaches those.

## 3. The ceilings, and they are monotone in how tightly you can point

Each arm replaces an admitted window's span with the head's own best candidate
inside a chosen region, then hands the result to an untouched `reduce` and
`score_extract_tight`. Every oracle consults the gold and is therefore a
ceiling and never an arm.

    arm                    right s1 / s2      delta      joint delta
    baseline                  367 / 368         --           --
    ORACLE  (sentence)        382 / 386      +15 / +18    +15 / +18
    ORACLE_RAD  r = 20        371 / 375       +4 /  +7     +4 /  +7
    ORACLE_RAD  r = 12        382 / 385      +15 / +17    +15 / +17
    ORACLE_RAD  r =  8        384 / 390      +17 / +22    +17 / +22
    ORACLE_RAD  r =  5        389 / 398      +22 / +30    +22 / +30
    ORACLE_RAD  r =  3        393 / 403      +26 / +35    +26 / +35
    ORACLE_RAD  r =  2        398 / 406      +31 / +38    +31 / +38
    ORACLE_PICK               419 / 425      +52 / +57    +52 / +57
    Q_OVERLAP                 275 / 280      -92 / -88    -92 / -84

Every oracle is **0 lost / all won** — they cannot lose, by construction — and
`ORACLE` reads p = 6.1e-05 and 7.6e-06.

**A sentence-accurate locator is worth 15 and 18 passages**, about two points
of the answerable half. Pointing to within **±2 content words** of the gold —
a precision no frame will reach, since it means naming the answer's
neighbourhood to the word — is worth 31 and 38.

**`Q_OVERLAP` is the floor and it is a catastrophe**: −92 and −88, 100 lost
against 8 won. Choosing the sentence with the most question words in it is the
cheapest locator anyone would write, and it is far worse than not locating at
all. That is the ninetieth finding's result in a second form — the gold and
the rival sit in the same neighbourhood, and question overlap picks the wrong
one systematically.

## 4. The number that bounds the whole family

`ORACLE_PICK` takes the gold whenever it is anywhere in the head's ten
candidates. That is a perfect locator **and** a perfect re-ranker **and** a
perfect verifier at once. It reads **419 and 425 of 721 — 58.1% and 59.0%**.

**Nothing built on this candidate list can beat that**: not a frame, not a
re-ranker (the eighty-sixth finding already retired one), not a verifier, not
a locality rule (the ninetieth). Against the owner's 85% — 613 of 721 — the
entire "choose better among what he produced" family is capped twenty-six
points short.

And it puts the frame idea in proportion: **as a locator it captures 29% and
32% of that ceiling at sentence granularity, 60% and 67% at ±2 words.** As a
*verifier* — my own reframe of the proposal, that the sketch is better used to
check a candidate than to find one — the ceiling is the full +52 / +57, which
is three times the sentence-locator's and is the stronger reading of the idea.

## 5. The proposal's own example says the failure is neither of those

*"who sang the theme song from russia with love"*, gold `Matt Monro`, spoken
`Monty Norman`. Traced through the harvest:

    w0   no gold    spoken 'Monty Norman'   margin -1.23   <- admitted, spoke
    w1   no gold    spoken 'David Arnold'   margin -3.80
    w2   GOLD       spoken 'David Arnold'   margin -3.81   <- ranked last

and window 2's own sentence is *"The theme song was composed by Lionel Bart of
Oliver! fame and **sung by Matt Monro**."*

**The frame the proposal predicts is literally the text of the window the
verifier ranked below two that contain no answer at all.** The mechanism is
vindicated and the deployment is not: the failure here is neither localisation
nor within-window selection. The wrong *window* won.

**And it is not one anecdote.** How often a window with no gold outranks every
gold-bearing one, over the whole answerable half rather than the residue,
because measuring it on failures alone conditions on the outcome:

                        seed 1              seed 2
    all             148 of 580  25.5%   129 of 580  22.2%
    he got it right   8 of 287   2.8%     8 of 285   2.8%
    residue         140 of 293  47.8%   121 of 295  41.0%

**2.8% where he succeeds against 47.8% and 41.0% where he fails**, with the
right-half rate identical on both seeds. That is the cleanest failure
signature measured in this workstream, and it is a cross-window ranking
failure, which no species in `probe_reader_species.py` names.

## 6. Repairing that is outside every ceiling above

`ORACLE_WINDOW` forces the highest-margin gold-bearing window into the mask and
changes nothing else:

    seed 1   367 -> 460 right, joint 600 -> 693   +93   p = 2.0e-28
    seed 2   368 -> 442 right, joint 575 -> 649   +74   p = 1.1e-22

**460 and 442 of 721 — 63.8% and 61.3% — against `ORACLE_PICK`'s 58.1% and
59.0%.** It is not bounded by §4 because §4 conditions on the candidates of
*admitted* windows and cannot see a window that never cleared the threshold.

**The caveat is structural and it is large.** An unanswerable passage has no
gold-bearing window, so the force fires only on the answerable half: the
attempt rate goes to 96.1% and 95.7% while correct silence is unchanged **by
construction, not by merit**. A real window scorer has no such licence and
would lift the attempt rate on both halves, paying in the unanswerable column
the way every threshold move in the ninety-second finding did. So +93 is not
comparable to `ORACLE_PICK`'s +52 as stated; what is comparable is the
signature in §5, which is unconditional and replicated.

## What this cannot say

**It is a ceiling, not a forecast.** Every oracle here is handed the answer.
A real frame will reach some fraction of `ORACLE`, and the ninetieth finding's
locality rule reached a negative fraction of a similar bound.

**It bounds locators over this candidate list only.** A frame that changed
what the head *proposes* — used as a decoding constraint rather than a
post-hoc filter — is not bounded by §4, because §4 conditions on the ten
candidates. That is a real gap and it is the version of the idea worth
protecting: §2 says the gold is missing from the ten on seventy per cent of
failures, so a mechanism that changes the ten is aiming at the part §4 cannot
see.

**Sentence granularity is one choice among many** and the radius sweep is why
it is not the only one reported. A frame might imply a region finer than a
sentence and coarser than two words, and the table gives its ceiling directly.

**Two seeds, one trunk, one population**, Population A at the CV'd threshold
under `hybrid`, with the extent rule off.

## What follows

**The proposal survives, at a stated size, and the reframe is the stronger
half.** As a locator it is worth at most 15–18 passages at the granularity a
sentence frame implies, against a residue of 354. As a verifier it is worth at
most 52–57. If it is built, build it to check.

**Test its own first question against §1 before building either.** The
proposal asks whether he can produce a useful outline at all. The prior
question is whether a useful outline would help on `SAME_SENTENCE`, which is
two thirds of the reachable residue — and the answer looks like no, because
both candidates sit beside the same anchor. **`OTHER_SENTENCE` is 40 and 42
windows.** That is the honest size of the target.

**And §4 is the number this workstream has been missing.** Four findings went
into the threshold, three arms died today, and all of them live inside a family
whose ceiling is 58–59%. The remaining twenty-six points to 85% require the
gold to enter the candidate list at all, which is the head and the trunk —
`PLAN-EXTRACTION-READER.md` §7 — and no post-hoc selection reaches them.

**What follows from §5 and §6, and it is the session's strongest lead.** The
frame's best use is neither locating within a window nor re-ranking a window's
candidates: it is **scoring which window to admit**. That is the 70% of the
residue §2 says is unreachable by candidate selection, it is where the
proposal's own example fails, and the verifier that would do it is the same
component the ninety-second finding showed cannot be improved by passage-shape
features — but a frame is a semantic feature, not a shape one, and nothing
measured yet speaks to it. **The next test is whether frame-match separates a
gold-bearing window from a non-gold-bearing one**, which is read (e)'s
population and needs no decode if the frame is hand-written first.

**Left unexplained:** `ORACLE_RAD` is monotone in the radius across six values
and both seeds, and at r = 12 it exactly equals the sentence oracle on seed 1
(+15) and nearly on seed 2 (+17 against +18). Whether a sentence just *is* a
twelve-content-word neighbourhood in this corpus, or the agreement is
coincidence, is unmeasured and would say whether "sentence" is the right unit
for a frame at all.
