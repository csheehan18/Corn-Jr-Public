# Other layer choices don't beat the shipped one

**Full result:** Five layer bands trained on the same ten thousand windows rank the shipped band at the top within a point on both seeds, and a five-layer band is no better, so the pick's missing signal is not in another three layers of the same stack and A3 closes on its kill

`scripts/harvest_states.py --layers 0..19,-1` and
`scripts/train_reader_cached.py --band ... --skip-evals`, 2026-09-04. One
harvest of 10,000 positive training windows (uniform sample, seed 3) at every
block output and `ln_f` — 21 × 1,024 a row, 27 GB, 1,892 s — then the built
head trained six epochs on each of five bands sliced out of that cache, two
seeds, 8,028 training windows and 1,972 held out by article, the same split
for every band. `evals/results/band_*_s{1,2}.json`. Held-out exact-pair
only; no eval pass, no Population A, nothing shipped. `corn/reader.py` is
untouched.

## 0. The arm and its pre-registration

`PLAN-READER-REPRESENTATION.md` A3, `READER-AUDIT.md` row 36: the span head
reads layers {8, 12, 16}, fixed by a linear membership probe on 800 windows on
the older v4 trunk (finding 83, `probe_spanhead.py`: 90 / 94 / 110 / 108 /
102 on the frozen eval at layers −1 / 4 / 8 / 12 / 16), never re-asked on
the trunk that ships, with the head that ships, on more than 800 windows.
After findings 102, 103, 106 and 108 each changed the head or its data and
not what it reads, the layer band was the last constant on the pick's inputs
that had not been tested.

**Cheap read.** A tenth of the training data at all twenty-one layers, five
bands trained on it with the shipped band as the control, held-out exact-pair
on the same windows. A ranking, not a bar. **Go:** a band beats the control
by ≥ 2 points on both seeds; then the full 38 GB harvest of that band and the
chain. **Kill:** no band does.

## 1. The ranking

Selected epoch's held-out exact-pair on 1,972 windows (standard error about
1.1 points):

    band                    seed 1    seed 2    mean     vs control
    12, 16, 19              0.4853    0.4776    0.4814   +0.0005 / +0.0064
    8, 12, 16  (shipped)    0.4848    0.4712    0.4780        control
    8, 12, 16, 19, ln_f     0.4731    0.4786    0.4758   -0.0117 / +0.0074
    4, 8, 12                0.4701    0.4643    0.4672   -0.0147 / -0.0069
    6, 10, 14               0.4686    0.4574    0.4630   -0.0162 / -0.0138

**No band beats the control by two points on either seed, let alone both.**
The band shifted up one layer, {12, 16, 19}, ties the shipped band on seed 1
and leads it by 0.6 on seed 2, inside one standard error. The two bands that
reach lower into the stack are 1.5 and 1.6 points under on seed 1 and 0.7
and 1.4 under on seed 2 — the one consistent direction in the table, and the
same direction finding 107 found for the say marker: the lower layers carry
less of the answer. The five-layer band, with 70% more input width, starts
worse (0.4128 at epoch 0 against 0.4356), is under the control on seed 1 and
over it on seed 2, and buys nothing for its width on a tenth of the data.

The curves have the shipped head's shape in miniature: training loss to 0.04
by epoch 5 on 8,028 windows, held-out flat or falling over the last epoch on
eight of ten runs. Fewer windows, the same memorisation.

## 2. Verdict

**Closed on its kill.** The band chosen once on 800 windows on v4 is as good
as any three layers of this stack on the trunk that ships, and a wider band is
not better. Row 36 of the audit closes, the 38 GB harvest is not spent, and
the last constant on the span head's inputs that a head could break has been
broken and found to hold.

With finding 107 (the say marker at any layer adds nothing the verifier's
inputs lack) and 108 (three other prompt forms move the states and none
lands the gold), the plan's three cheap reads are all in, one afternoon, and
each said the same thing: **what the frozen trunk computes about a window
under this prompt is what the shipped heads already read, and reading it from
a different layer, a different prompt or a different depth of the stack does
not add to it.** What remains on the plan is W1, the whole passage in one
forward on the frozen trunk, and W2, the trunk itself moved under a reader
adapter. Those are the two arms that change what is computed rather than
where it is read from.

## 3. Cost, as measured

    harvest 10,000 windows at 21 layers      1,892 s GPU, 27 GB   (estimated 80 s and 16 GB:
                                                                  21 hooks throttle the forward
                                                                  and the windows average 65
                                                                  candidate rows, not 40)
    one band run, six epochs                 ~5 min              (45 s an epoch: every row is
                                                                  read at 21 layers and sliced)
    ten runs                                 ~50 min

About an hour and a half of wall clock for the read, against the hour I
priced. The 27 GB cache is regenerable in 32 minutes and is left on `F:` for
the owner to delete; nothing else reads it.

## 4. On disk

`harvest_states.py --layers` (any block outputs, `-1` for `ln_f`; the
manifest records the band and its width). `train_reader_cached.py --band`
(the head reads a subset of the cache's layers, sliced per row where a row
leaves its shard, so the shipped path with the flag off is byte for byte what
it was) and `--skip-evals` (held-out curve only, for a cache whose band the
eval caches were not harvested at). `evals/results/band_*_s{1,2}.json`, ten
files.

## 5. Limits

A tenth of the data and a 1,972-window slice: the read ranks bands to about a
point and cannot see a half-point band. Five bands, not a sweep of all 1,330
triples. Six epochs of the shipped schedule on 8,028 windows over-fits harder
than the shipped run (loss 0.04 against 0.10), which flattens every curve
equally and should not favour a band. The held-out exact-pair here (0.47–0.49)
is not comparable to the shipped heads' 0.54 — a tenth of the data — and is
quoted only against the control on the same tenth.
