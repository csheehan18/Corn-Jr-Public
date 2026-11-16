# Everyday web text taught him more word meanings at little cost

**Full result:** At nano, swapping the web share from FineWeb-Edu at score 4 (about the most textbook-like 1% of the web) to plain FineWeb raises the understanding ruler -- description to wish 0.40 against the controls' 0.28-0.32, past its gate; phrase to field 0.58 against 0.50-0.54, two items short of its gate -- with 81 of 88 behaviour rows in the three controls' band, four above and three below (two of those on rows of 12 and 20), and loss on Edu's own held-out text worse, 0.963 against 0.884-0.887 nats per byte; one seed, a direction

**Cost:** the download of `HuggingFaceFW/fineweb` `sample/10BT/000_00000.parquet` and its text 14:39-14:43 on 2026-10-20, decontamination and `prepare_mix` done by 14:51; one nano run of 5,237 iterations, 879.3 s (14:51-15:06, contended -- the card at 37%, a bound); the ruler and the arm's card 304.7 s; the two older controls re-scored on today's full card 505.3 s; the ruler on the three controls 25.6 s.

**The owner's question, 2026-10-20.** His design puts facts outside the
weights -- lookups, packs, tool results -- so what the weights must carry is
**understanding**: "won't take long" is about time and wants it low, "hits
hard" is about attack, a ghost story in an empty farmhouse is what people call
scary. Findings 148, 156, 167-168, 183 and 184 each stopped at that hop.
`scripts/ruler_understanding.py` (f3d8cf7; 141 phrase -> field items over 30
kinds of data, 96 description -> wish items over 8 kinds, each candidate
scored by what the phrase adds so length and frequency cannot vote) reads
0.54 / 0.32 at 20M and 0.69 / 0.58 at 260M, the 260M's misses sorted by kind
of data. And our web is FineWeb-Edu's sample, pre-filtered to educational
score 3 and cut again to 4 (DATA.md §4c) -- about the most textbook-like 1%
of the web, with recipes, reviews, hobbies and games in the 99% left out.
The owner: "we need his vocab to be able to understand what he's getting."

**The arm** (pre-registered at 33edc56, `configs/mix_v3_plainweb.py`). mix_v3
with its web source's file alone changed: shard 000 of plain FineWeb's
`sample/10BT` (2,147,292,183 bytes, ODC-By 1.0), 1,048,581 documents, 3.24 GB
through `scripts/prepare_fineweb.py --repo plain` and
`scripts/decontaminate.py` against `evals/text_web.txt` (0 of 612 probes hit,
nothing dropped), at the Edu source's weight; 130,279,713 train tokens and
mix_v3's tokenizer fingerprint, checked. The run is `nano20m_v3_compiled`
but for name and data directory. Read by hand before training: a law firm's
charity run, a family-photo blog, a spun SEO page on picnics, a
loft-conversion advert, a charity bulletin, a scouting memoir.

## The registered read

    run                      ruler fields   ruler wishes   lm web (nats/byte)
                             (chance 0.24)  (chance 0.17)
    nano20m_v3               0.54           0.32           0.8867
    nano20m_v3_seed2         0.50           0.28           0.8839
    nano20m_v3_compiled      0.54           0.32           0.8845
    nano20m_v3_plainweb      0.58           0.40           0.9632

**Understands: wishes pass (0.40 against a gate of 0.38), fields miss (0.58
against 0.60).** The prediction (wishes 0.38+, fields 0.55-0.59, lm web worse
by 0.02+) held on all three. By kind against the compiled control: flights 3
of 5 (1), films 4 of 6 (3), cars 3 of 5 (0), headphones 3 of 4 (1), books 3 of
5 (1); wishes for films 6 of 12 (3) and holidays 6 of 12 (3). Pokemon stays at
2 of 6 and recipes fall, 2 of 7 against 4: one shard of everyday web is not a
pokemon wiki or a recipe site.

**Costs: the gate as written fails on three rows.** The first comparison put
the arm against `nano20m_v3_compiled` alone on every row added to the card
after the two older controls were scored -- a band of one point -- and called
eight rows below it, `compound.pipe_first` (26 against 45) and `social.self`
(26 against 40) among them. Scoring `nano20m_v3` and `nano20m_v3_seed2` on
today's full card (`__card20261020.json`, committed beside the arm's) gives
every row its three-run band, and then **81 of 88 rows are within it**:

    below   social.farewell 7/20 (9-12), social.heldout_carrier 7/12 (8-10),
            compound.items_first 2/48 (6-11)
    above   search.route_base 200/200 (169-188), notefid.novel_phrasing
            31/120 (10-19), chat.abstain_greet 45/100 (22-34),
            chat.abstain_oos 15/100 (0-6)

`compound.items_first` fails the same way in every run (wrong text 22-28 of
48); the arm writes more calls that do not parse, 11 against 2 and 8 -- read
off the card's recorded reasons, not decoded by hand (owed), so a bound.
`compound.pipe_first` and `social.self` sit inside the band once the
controls' own spread is known.

## What it licenses

* **The everyday web carries understanding the textbook web does not.** At
  20M, one shard of it moves the wish read past the three-seed band by
  more than the band is wide, the field read by a little, and the kinds of
  data that moved are the everyday ones (flights, films, cars, headphones).
* **It costs Edu's own held-out text, as it must, and little else
  measured**: three rows of 88 below band, two of them by one or two items
  on rows of 12 and 20. The rows Edu was thought to buy ("fluency,
  vocabulary", PLAN-1-0) were never priced; this is the first price, and it
  favours mixing the everyday web in.
* **For D1, the `mix_v5_5b` share table**: the web share is two sources,
  not one -- plain FineWeb beside Edu, the split set by the ruler on the
  pilot (P1). A blend arm at nano is the cheap next read; the supply
  argument (DATA.md §4c: all of score-4 Edu is 1.71B tokens, about one pass
  at 5B) points the same way.

**What it does not settle.** The size of the effect (one seed); a blend; the
same swap at 260M, where the ruler reads 0.69 / 0.58 on Edu and the misses
are by kind; whether more shards or targeted sources (recipes, game wikis)
move the kinds one shard did not; and the hand read of
`compound.items_first`'s unparsed calls.
