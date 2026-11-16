# A third web source, DCLM, splits its seeds and adds nothing measurable

**Full result:** At 20M, mix_v3's web share in thirds -- FineWeb-Edu, the filtered plain FineWeb and DCLM-baseline -- reads wishes 0.39 and 0.33 and fields 0.54 and 0.51 against finding 189's blend at 0.38 and 0.38, 0.55 and 0.54, so the second seed misses the holds gate and the pre-registered reading is that the blend stands; Edu's held-out text recovers (0.919, 0.920 against the gate's 0.925 and the blend's 0.906); one small row falls at both seeds (`social.heldout_carrier` 7 and 6 of 12 against 8-10) while five tool and turn rows rise at both, unexplained; no 20M answers one of the 40 hard words

**Cost:** the DCLM CPU read and build 09:31-11:44 on 2026-10-21 (a018dd1), the owner away between; two nano runs of 905 and 917 s, cards 272 and 240 s, reads 17 s each -- the chain 2,368.8 s, contended (the card at 38%, a bound).

**The question** (owner, 2026-10-21): "could it just be worth adding in line
with the fine webs, as its own more data?" The budget is fixed, so a third
source is not more data; it is variety, and the CPU read said DCLM has it --
118,619 words seen 20+ times at a matched 229M words against plain
FineWeb's 110,828 and Edu's 102,792, ordinary web by hand, junk 0.38%
against 1.61%, 0.06% of its URLs in plain FineWeb's shard -- with fewer of
the wish read's own words (2,554 per million against plain's 2,996) and
pages mostly from 2006-2013. Pre-registered at a018dd1
(`configs/mix_v3_webthirds.py`): the web weight in thirds, one variable
against finding 189's cell B.

## The read

    run                        fields   wishes   lm web   rows below / above (of 84)
    B  nano20m_v3_webblend     0.55     0.38     0.906    4 / 4
    B  _seed2                  0.54     0.38     0.907    7 / 5
    T  nano20m_v3_webthirds    0.54     0.39     0.919    1 / 9
    T  _seed2                  0.51     0.33     0.920    2 / 14

    gates   holds wishes >= 0.34 and fields >= 0.52    T seed 1 passes; seed 2 misses both
            adds  wishes >= 0.42 or fields >= 0.59     neither seed
            recovers lm web <= 0.925                   both seeds

**The registered row is "below holds at either -- the third took
understanding from the blend; B stands".** The table also carries "seeds
split -- a direction", which this read matches as well; the rows overlap, and
the stricter one governs because it was written for a single seed's miss.
What the numbers support is narrower than either: **T and B cannot be told
apart on this instrument.** T's two seeds differ by 0.06 on wishes, more than
the gap between T's mean (0.36) and B's (0.38); finding 189 put one run's
wish rate within about +-0.05 on 96 items. The read cannot say DCLM took
understanding; it can say it did not add any it can see.

**Recovers, and pays for it.** Edu's held-out text reads 0.919-0.920,
inside the gate and 0.013 above the blend -- the Edu third is a third, not a
half.

## Costs, and rows that rise

By finding 185's rule, **one row falls at both seeds**: `social.heldout_carrier`
7 and 6 of 12 against the Edu controls' 8-10 -- a row of twelve items that
finding 185's arm and the second seeds of P and B also read at 6-7. By the pre-registration that is a cost;
its size is two items.

**Five rows rise at both seeds** -- others than the four that rose at both of
B's (`daylog.open`, `daylog.targeted`, `packs.column`, `tool.validity`):
`tool.selection` 147 and 155 of 200 against 128-131, `turn2.first` 147 and
155, `daycross.no_day` 147 and 155, `notefid.novel_phrasing` 32 and 26 of 120
against 10-19, `turn2.chain_pronoun` 14 and 15 of 50 against 0-5. The first
three read identical counts at each seed and probably share their items; none
was decoded by hand, so these are bounds, and the finding names no cause.

## Hard everyday words

`ruler_words.py`: 0 of 40 at both seeds, the pick 0.42 and 0.38 --
every 20M reads 0 (finding 189). The read DCLM's variety is for is a 260M read.

## What it licenses

* **D1 keeps finding 189's blend**: half Edu, half the filtered plain web.
  DCLM does not ride on this read.
* **The wish read cannot decide a web share at 20M.** Five web mixes now --
  Edu, finding 185's plain, the filtered plain, the blend, thirds -- sit in
  0.28-0.40 with seed spreads up
  to 0.06. Settling DCLM wants a wider wish set (more items per kind) or the
  260M pilot reading `ruler_understanding.py` and `ruler_words.py`, not a
  third nano seed.
* **The rising rows are a lead, not a result.** Tool selection and the
  first turn up 16-27 items at both seeds is worth a hand read before
  anyone builds on it.

**What it does not settle.** DCLM at 260M; DCLM in place of Edu rather than
beside it; newer DCLM shards (these date mostly 2006-2013); the five rising
rows by hand.
