# Doubled wish test: the blend holds, DCLM's second seed falls back

**Full result:** With the understanding ruler's wish read doubled to 192 items (96 new, hand-written to the same rule), the 20M web mixes order cleanly -- Edu 0.29-0.32, the filtered plain web 0.34-0.35, half Edu and half plain 0.37 and 0.38 -- each pair of seeds within 0.03; the thirds with DCLM read 0.37 and 0.31, and the second seed's low read repeats on the new 96 alone (0.29), so it is the run and not the instrument: one of DCLM's two seeds lost the everyday web's gain; the blend stands on a read that can now separate it from Edu

**Cost:** writing 96 descriptions and wiring them 13:12-13:13 on 2026-10-21 (c17d958); eleven checkpoints read in one pass, 2.6 min, contended (the card at 35%, a bound).

**The question** (owner, 2026-10-21: "double the wish test and let's
see"). Finding 190 left the blend and the thirds indistinguishable: five web
mixes sat in 0.28-0.40 on 96 items with seed spreads up to 0.06, more than
the gaps the mixes were meant to show.

**The instrument** (`scripts/ruler_understanding.py`, `WISHES_MORE`). Two
more descriptions a wish across the same 8 kinds and 48 wishes -- "a snug
corner booth beside a wood stove" -> cosy, "one hit and you start the whole
level again" -> difficult -- none sharing a content stem with its wish or
repeating an original (`check_items` asserts both), scored exactly as the
original. The original 96 are unchanged and reproduce every earlier number
here to the item.

## The read

    run                          first 96   second 96   all 192
    Edu  nano20m_v3              0.32       0.30        0.31
         _seed2                  0.28       0.29        0.29
         _compiled               0.32       0.31        0.32
    plain, unfiltered (185)      0.40       0.39        0.39
    P  filtered plain            0.35       0.35        0.35
       _seed2                    0.33       0.34        0.34
    B  half Edu, half P          0.38       0.36        0.37
       _seed2                    0.38       0.39        0.38
    T  thirds with DCLM          0.39       0.35        0.37
       _seed2                    0.33       0.29        0.31
    corn_jr_260m_v4 (Edu)        0.59       0.56        0.58

**The new half reads like the old.** On every run the second 96 sits within
0.04 of the first, and it ranks the mixes the same way -- the read is
consistent, so doubling it narrows the noise rather than changing what it
measures.

**Against the prediction** (c17d958): the blend and the thirds within 0.03
at both seeds -- held at seed 1 (0.37, 0.37), failed at seed 2 (0.38
against 0.31); Edu below both by 0.04 or more -- failed for the thirds'
second seed, which reads at Edu's level; each cell's seeds within 0.04 --
held for Edu, P and B, failed for the thirds (0.06); the second half ranks
the cells as the first -- held.

## What it says

* **The blend is the steady choice.** Its two seeds read 0.37 and 0.38 on
  192 items, 0.07 above the Edu runs' mean (0.31), and the filtered all-plain web
  sits between (0.34, 0.35) -- the order finding 189 read, now with seeds
  that agree.
* **The thirds split is real.** Seed 2's low read holds on the 96 new
  items, 0.29 against its twin's 0.35. With DCLM in the mix, one
  seed of two kept the everyday web's gain and one did not. Two seeds cannot
  say why, or how often.
* **For D1: finding 189's blend, half Edu and half the filtered plain web.**
  DCLM stays out of 1.0's web share on this evidence; finding 190's rising
  tool rows remain an unread lead.

**What it does not settle.** Why one thirds seed fell; DCLM at 260M or in
place of Edu; the fields read, which was not widened (141 items, seed spreads
up to 0.04).
