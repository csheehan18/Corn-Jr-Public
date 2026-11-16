# Half textbook, half everyday web keeps the word gain at lower cost

**Full result:** At 20M, a web share half FineWeb-Edu and half plain FineWeb with the junk out reads the understanding ruler's wishes 0.38 at both seeds against the Edu band's 0.28-0.32 and Edu's held-out text at 0.906 and 0.907 nats per byte against 0.884-0.887 (the all-plain web costs 0.963) -- keeps and recovers, the pre-registered blend outcome; the all-plain filtered cell misses its wish gate at both seeds (0.35, 0.33 against 0.36) and the filter is not why: the pages it dropped hold 2.35% of every wish word, their share of the text; on 40 hard everyday words no 20M checkpoint answers one in its own words

**Cost:** four nano runs of 867, 870, 893 and 900 s (2026-10-20 21:16 to 2026-10-21 08:20, the chain paused overnight at the owner's word), cards 246-276 s and rulers ~10 s each; the junk-page count 141.7 s on CPU; the everyday-words read on ten checkpoints 56.9 s; the card at 31-41%, a bound.

**The question** (pre-registered at 2db41ec, `configs/mix_v3_webblend.py`).
Finding 185: plain FineWeb in place of FineWeb-Edu raised the wish read
0.28-0.32 -> 0.40 on one seed and cost Edu's own held-out text 0.886 ->
0.963. Two cells: **P**, the same swap with the junk filter's 16,932 pages
out (2be3af2) -- does the filter take understanding with the junk? -- and
**B**, the web weight split to the token between Edu and the filtered file --
does half the plain web keep most of the gain at less of the cost? Two seeds
each; mix_v3's budget and iterations.

## The read

    run                          fields   wishes   lm web    behaviour rows (of 84 with three controls)
    Edu: nano20m_v3 / _seed2 /   0.50-    0.28-    0.884-    --
         _compiled               0.54     0.32     0.887
    finding 185 (unfiltered)     0.58     0.40     0.963     77 in band, 3 below, 4 above
    P  nano20m_v3_plainclean     0.54     0.35     0.964     76 in band, 0 below, 8 above
    P  _seed2                    0.56     0.33     0.963     80 in band, 3 below, 1 above
    B  nano20m_v3_webblend       0.55     0.38     0.906     76 in band, 4 below, 4 above
    B  _seed2                    0.54     0.38     0.907     72 in band, 7 below, 5 above

**B keeps and recovers at both seeds** (wishes >= 0.36, lm web <= 0.925):
the pre-registered row "a blend keeps the everyday web's gain at under half
its cost". It recovers more than half the cost -- 0.906 sits 0.019 above the
Edu band where the all-plain web sits 0.076 above -- and its wishes sit above
both P seeds.

**P's fields keep (0.54, 0.56) and its wishes miss at both seeds** (0.35,
0.33 against a gate of 0.36): the pre-registered row "the filter took
understanding with the junk -- read the dropped pages by kind before any
blend is called".

## The dropped pages, read

`scripts/probe_junk_wishes.py` counts every word the wish read turns on --
the 36 wish labels and the content words of its 96 descriptions -- in the
pages the filter dropped and the pages it kept:

    dropped pages 16,932, 12,715,211 words -- 2.37% of the text
    the 36 wish labels     37,817 of 1,612,085 dropped (2.35%; 1.0x the text's share)
    description words   1,371,716 of 56,235,392 dropped (2.44%; 1.0x)

The labels most over-represented in the junk are *cheap* (4.2x), *thrilling*
(2.9x), *romantic* (2.3x) and *exciting* (1.6x) -- the casino and dating
pages -- and even *cheap* lost only 3,228 of 32,256 occurrences. **The filter
took the wish words in proportion to the text and no more, so it cannot be
why P reads lower.** What is left is the read itself: 96 items put one
run's wish rate within about +-0.05 of its mean (binomial), finding 185's
0.40 is one seed, and P's 0.33-0.35 against B's 0.38 is no larger than that
spread. Read as a pair, P and B sit 0.03 and 0.07 above the Edu mean
(0.31) -- the opposite order to their plain shares, inside the spread: at
this resolution the wish gain does not grow with the share, which is what
makes the blend cheap.

## Costs

Finding 185's rule (each behaviour row within the three Edu controls' range
widened by 5% of n). No row falls at both seeds of a cell, so no cost
replicates. The largest single drops are B seed 2's note rows
(`tool.note_fidelity`, `notefid.*` 1/120 against 10-19), read off the
card's recorded reasons: 117 of 120 `wrong_tool`, the controls' own
dominant failure (89 of 120 at 11/120) -- a row near its floor falling
further, not a new failure; B seed 1 reads 6/120 on the same row.
`turn2.second` reads 130 and 132 on B seed 1 and P seed 2 against 157-175
and 166 on B seed 2: one seed in each cell. These are bounds -- read from
the cards' reasons, not decoded by hand. The prediction ("a row or two in
each cell") was right for P and low for B (4 and 7 below, none shared).

## Hard everyday words (`scripts/ruler_words.py`, ce0f247)

Finding 188's 40 hard words and phrases, scored on what he writes after
"what does X mean? It means" -- right only when an accepted meaning appears
that he could not copy from the prompt:

    every 20M here (Edu, plain, P, B)   free 0/40      pick 0.30-0.42 (chance 0.25)
    corn_jr_260m_v4                     free 1/40      pick 0.53
    corn_jr_260m_v4_ft_social8          free 1/40      pick 0.45

The free read is the number; the pick is printed to show how much it
flatters. The 260Ms' one credit each, read by hand: `social8` *bucks* ->
"the amount of money that is spent" (right) and `v4` *ubiquitous* -> "not as
common as they were" (the inverse; a false credit). Their answers also carry
two partial meanings the list
does not credit ("on the cards" -> "that the rain is coming"; "staycation"
-> "staying in one place for a while") and the 20Ms none. **The instrument
was fixed during this read**: its first pass credited *gas guzzler* -> "the
gas is not a gas", *dirt cheap* -> an echo of the request and *low-key* ->
"a quiet catch-up" copied from the request; an accepted meaning that shares
a content word with the target or its request no longer counts. Predicted:
slang stays near zero at 20M -- held. Whether the everyday web moves these
words is a 260M question.

## What it licenses

* **For D1: the web share is a blend.** Half Edu, half the filtered plain
  web keeps the everyday web's word gain at about a quarter of its cost on
  Edu's own text, at both seeds; the pilot's ruler (and now
  `ruler_words.py`) sets the split at 260M.
* **The filtered file is the plain source from here**: it took junk and no
  share of the wish words beyond its share of the text.
* **The wish read's spread is wider than its gates assume.** At 96 items a
  gate 0.04 above a band misses on noise; a read that decides a share
  wants more items or more seeds.

**What it does not settle.** Any size above 20M; any split but half; the
hard words, which no 20M knows; the cost rows, read off the cards and not
by hand.
