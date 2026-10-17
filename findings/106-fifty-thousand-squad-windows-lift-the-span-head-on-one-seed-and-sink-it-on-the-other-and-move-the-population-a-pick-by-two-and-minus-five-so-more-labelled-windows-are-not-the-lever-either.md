# Hundred-and-sixth finding — fifty thousand SQuAD windows lift the span head 1.3 points on one seed and sink it 1.6 on the other, and move Population A's pick stage by +2 and −5, so more labelled windows are not the pick's lever either and the arm closes at its gate

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`scripts/prepare_squad.py`, `gen_spans.py`, `harvest_states.py` and
`train_reader_cached.py --extra-cache`, 2026-09-04. Two span heads on the
frozen `corn_jr_260m_v4_ft4g` trunk with no weight of it moved, the shipped
recipe with one change: 48,929 / 48,732 SQuAD 2.0 windows added to the
training set, none to the held-out slice. `evals/results/reader_squad_s{1,2}.json`
and `_popa.json`, `pairs_squad_s{1,2}_popa.json`, `reader_funnel_squad_s{1,2}.json`;
`checkpoints/reader_squad_s{1,2}.pt` (gitignored); the state cache
`F:/corn-jr-data/states/spans_squad_positive` (20 GB, 50,000 windows). No
verifier, no chain, no reader run: the gate is a stopping rule and it stopped
the arm. `corn/reader.py` is untouched.

## 0. The arm, as pre-registered

`READER-AUDIT.md` L18 and `PLAN-EXTRACTION-READER.md` §7.1: SQuAD as a
**minority** source of labelled windows for the span head, NQ held out as the
only read. Opened by the owner on 2026-09-04 after the epochs (102), ensemble
(103), ruler (104) and extent (105) levers had closed, on the reasoning of
finding 103 that the pick's remaining error is bias in what the frozen states
carry and more data is the direct fix for bias. The licence is CC BY-SA 4.0,
the same family as NQ, and the owner accepted it.

Pre-registered in `STATUS.md` before any number existed: a gate of held-out
exact-pair **≥ 0.565 on both seeds** (the shipped heads read 0.5410 /
0.5425 / 0.5554); a kill if NQ held-out exact-pair **falls below the shipped
head's on either seed**; and only past the gate the chain and a bar of +12
right a seed at the silence floor.

**The recipe.** `train-v2.0.json` (442 articles, 130,319 questions, 86,821
answerable) → `prepare_squad.py` writes one row per question in
`nq-train-full.jsonl`'s shape, question lower-cased and unquestioned to
match the NQ prompt, a title-carrying url so `article_key` works →
`gen_spans.py` windows it at 64/32 and decontaminates against NQ dev and the
frozen evals by article and by window (3,177 rows dropped by article;
141,443 positive windows, alignment 91.7%, unaligned 0.60%) →
`harvest_states.py --kinds positive --cap 50000 --sample-seed 1` (410 s) →
`train_reader_cached.py --arm built --extra-cache`, which indexes the second
cache, tags its windows, joins them to training only, and drops any whose
article is one NQ held out (1,071 and 1,268). Training sets of 144,133 and
143,889 windows against the shipped 95,204 and 95,157; held-out slices the
shipped heads' own 4,880 and 4,927 NQ windows, so every number below is like
for like.

## 1. The gate: one seed up, one seed down

Held-out exact-pair on the same slice, epoch by epoch:

    epoch     seed 1 shipped   seed 1 +SQuAD     seed 2 shipped   seed 2 +SQuAD
      0          0.4863           0.5318            0.4973           0.5062
      1          0.5172           0.5311            0.5050           0.5222
      2          0.5133           0.5311            0.5040           0.5151
      3          0.5287           0.5449            0.5261           0.5151
      4          0.5369           0.5516            0.5368           0.5267
      5          0.5410           0.5543            0.5425           0.5267

**Seed 1: +1.33 points, above the shipped head at every epoch, the first
positive move of the pick from any arm on frozen states in this workstream.
Seed 2: −1.58 points, above for three epochs and below for three.** The gate
of 0.565 is missed on both; the kill fires on seed 2. The standard error of a
proportion over 4,880 windows is about 0.7 points, so the two seeds are two
standard errors apart in opposite directions around zero.

The epoch-0 lead is the one consistent thing: +4.6 and +0.9 points before the
schedule has decayed, more data helping the head start faster and then
converging to the same place. Training loss ends at 0.111 and 0.112 against
the shipped 0.101 and 0.103: the same memorisation of a set half again as
large.

## 2. Population A's pick stage does not move

`harvest_popa_pairs.py` on each head, `probe_reader_funnel.py --pairs`, and a
passage-level pairing against the shipped head's grid. The pick stages are
the head's alone; the downstream stages read with each seed's shipped
verifier are not quoted, because that verifier was cross-fitted to the
shipped head.

                                        seed 1 shipped  +SQuAD    seed 2 shipped  +SQuAD
    the gold in some gold window's ten        678         684           679         685
    the head ranks it first there             494         496           484         479
    paired on the pick                        +2 (lost 48, won 50, p = 0.92)    −5 (lost 52, won 47, p = 0.69)
    paired on the ten                         +6 (lost 9, won 15, p = 0.31)     +6 (lost 10, won 16, p = 0.33)
    pick rate over windows with the gold in the ten     66.6% -> 65.0%           64.7% -> 63.9%

**+2 and −5 passages on the pick, with about fifty passages moving each way
on each seed.** The one shared movement is six more passages with the gold in
the ten on both seeds, which is generation and not the pick, and is what the
extra windows would buy a head that had learned nothing but a slightly wider
candidate habit. The winner's median lead over the gold shortens from 3.44 to
2.57 logits on seed 1 — the wrong picks are less confident — and no more of
them are right.

## 3. The other rulers, ungated

                              seed 1 shipped  +SQuAD    seed 2 shipped  +SQuAD
    frozen tight /200              138          130           130          127
    phrase tight /89                36           39            39           41
    extract.paired /128             89          101            85           93
      took_first                    27            9            22           19
      sibling spoken                29           10            26           19

Frozen tight down on both seeds and phrase tight up on both, each inside its
seed spread. **The paired file is up +12 and +8 on both seeds**, with
`took_first` — the sixty-sixth finding's "take the first value of the gold's
type in the window" — down from 27 to 9 on seed 1. That is the same-type
rival discrimination that SQuAD's paragraph-primed questions were expected
to teach badly and appear to teach well, on a 128-item file whose seed
spread finding 83 measured at ±24. It is reported and not barred, and it did
not reach Population A's `RIVAL` species in any read here because no verifier
was fit.

## 4. Verdict

**Closed at the gate by its own pre-registration**: 0.5543 and 0.5267 against
a gate of 0.565, and the kill fired. Under the audit's rule — a pre-registered
bar failed on two seeds — L18 is closed as an arm on the pick.

What it says beyond itself is the same thing findings 102 and 103 said from
the other two directions. More epochs (102) bought nothing; averaging three
seeds (103) bought four passages against sixty of real disagreement; fifty
per cent more labelled windows buys +1.3 on one seed's own slice and nothing
on the population. A head with 7.9M parameters that memorises 95,000 or
144,000 windows to a loss of 0.1 and holds at 0.54 either way has run out of
signal in its inputs, not out of data, epochs or ensembles. **The remaining
lever on the pick is the representation** — a different layer band, a
different prompt form, or a trunk that has seen the span task — and every one
of those is a state re-harvest or a fine-tune, which is what §7 of the
extraction plan and the audit's Part 4 already price.

Not run, and not owed: the Population A chain on a missed gate. The owner
could override the protocol on seed 1's +1.3 and the paired file's +12 / +8;
the pick stage's +2 / −5 is the number that would tell them what the chain
would find.

## 5. Cost, as measured

    convert 130,319 questions to rows       ~1 min CPU, 145 MB
    window and decontaminate                110 s CPU, 808 MB, 726,549 windows
    harvest 50,000 positive windows         410 s GPU, 20 GB
    span head, six epochs, per seed         ~20 min GPU (200 s an epoch at 144k windows)
    pair grid on Population A, per seed     19 s GPU

About an hour and a quarter of wall clock for the two-seed gate read, against
a pre-registered estimate of an hour a seed for the full chain, which was not
needed.

## 6. On disk

`scripts/prepare_squad.py` (new). `train_reader_cached.py --extra-cache`:
an item's `shard` is now `(cache, shard)`, so every reader of
`blobs[it["shard"]]` works over several caches; the held-out slice is drawn
from the primary cache alone; extra windows in a held-out article are dropped.
Flag off is byte-identical behaviour. `data/raw/train-v2.0.json` (42 MB),
`squad-train.jsonl` (145 MB) and `spans_squad.jsonl` (808 MB) are on disk and
not committed; the 20 GB cache is on F:. `docs/RELEASE.md` carries the
licence line and `DATA.md` §6 the one-use reversal of its NQ-over-SQuAD
argument, both written before the run.

## 7. Limits

Two seeds, one cap (50,000 of 141,443 positives, a third of the training
set), one recipe: a larger SQuAD share or SQuAD-only pre-training of the head
followed by NQ were not tried, and the plan's own reason for the cap — the
lexical-overlap shortcut — was not measured directly, only made readable by
selecting on NQ. The no-answer half of SQuAD (43,498 unanswerable questions,
249,248 `absent_topical` windows) was windowed and not harvested; the verifier
never saw it. Alignment on SQuAD is 91.7% against NQ's higher figure because
SQuAD golds carry more trailing punctuation and quotation. The seed-1 head's
`reader_squad_s1_popa.json` is an ungated harvest and is not a reader
number.
