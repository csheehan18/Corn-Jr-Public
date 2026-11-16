# Everyday web text leaves the soft read under loop near chance

**Full result:** Arm E2's three starts rebuilt with the filtered plain FineWeb as their web source, and finding 184's loop fine-tune run from each, land on the pre-registered row "understands fails": the understanding ruler's wishes read 0.34, 0.38, 0.34 on the 96 items the gate was set on (gate 0.36 at two of three; one passes) and 0.33, 0.35, 0.30 on all 192 against the matched Edu starts' 0.32, 0.31, 0.31 -- the everyday web does not move understanding inside E2's mix; under it every other gate fails at three of three -- knowledge wishes 14, 16, 21 of 72 (gate 26), the filter read at no start (E2: one), the one start that read the wish on Edu (2337) losing it (held-out 97 -> 73 of 288, with the first-place habit raced out 91 -> 74 against chance 79), loop's fine-tunes writing `pick: none` on all 192 answer batches at every start, and the soft read under the stop ranking the right place first on 101, 88 and 80 of 192 (gate 125; finding 184: 94, 116, 90; chance about 81); so the question this was built for -- was vocabulary the wall -- is unreadable from this arm, because the vocabulary it was meant to add never arrived

**Cost:** both mixes built on CPU 14:13-14:15 on 2026-10-21; one chain under the card's lock 14:15-15:34, 4,743.9 s, contended (the card at 35-37% before every job, a bound): three nano pretrains of 1,241, 1,241 and 1,242 s, on each start the ruler 18 s, the knowledge probe 34 s and the filter read 40 s, three loop fine-tunes of 161 s each, their loop reads 48 s and copy rows 8 s each, the inside read on six checkpoints 90 s; afterwards the 192-item ruler on arm E2's three Edu starts 53.4 s, a ruler hand read 17.8 s and a hand decode of 24 loop batches 7.7 s.

**The question** (pre-registered at 2db41ec, `configs/mix_v3_funcworld_filter_ev2_plain.py`,
before a byte trained). Finding 184: loop "until it sounds right" collapses
to always keep looking, because the soft read under the stop -- does "a pub
with a roaring fire" answer "cosy" -- is near chance. Every start in that
line of work pretrained on FineWeb-Edu at score 4, where the everyday words
the soft read needs are rare, and finding 185 showed the plain web raising
the understanding ruler. One variable: arm E2's starts, seeds 1337, 2337 and
3337, with the web file swapped for the filtered plain FineWeb (2be3af2's
filter) at Edu's weight to the token; then finding 184's loop fine-tune
from each, its replay's web the same file. Unreadable if
`check_webjunk.py`, `check_filter.py` or `check_loop.py` fails, or a read
is missing: all three pass and every read is on disk.

## The starts

    run                         ruler wishes      ruler    knowledge        filter (ev order)       first-place  habit-free
                                96     192        fields   fields  wishes   train    held-out      picks, held  held-out
    gate                        0.36              --       --      26/72    >54/144  >95/288       --           (chance 79)
    Edu  ev2 (1337)             0.31   0.32       0.52     22/40   19/72    48       83            83           82
         ev2_seed2 (2337)       0.34   0.31       0.54     18/40   17/72    70       97            147          91
         ev2_seed3 (3337)       0.33   0.31       0.52     23/40   22/72    47       69            94           69
    plain ev2_plain (1337)      0.34   0.33       0.47     16/40   14/72    48       84            64           81
          _seed2 (2337)         0.38   0.35       0.54     17/40   16/72    45       73            128          74
          _seed3 (3337)         0.34   0.30       0.55     18/40   21/72    42       77            148          75

The Edu starts' 192-item column is new (`__ruler192.txt`); their first 96
reproduce the committed 96-item reads to the item. The habit-free column is
finding 148's -- the 207 held-out items whose gold is not the first ok place,
raced among the later ok places only -- computed from each start's saved
scores; it reproduces 148's 82, 91 and 69 on the Edu starts.

**Understands fails.** One start of three clears 0.36, by two items, and
falls under it on all 192 (0.35). On the matched read the plain starts sit
0.01 above the Edu starts on average (0.33 against 0.31) -- inside the
+-0.05 one read carries (finding 189). Read by kind, as the row asks (all
192, summed over three starts, of 72 a kind):

    kind      film  book  holiday  restaurant  hike  game  song  show
    Edu        23    16     31        29        20    33    19    10
    plain      26    15     24        25        21    33    29    16

What the plain web adds is songs and shows (+10, +6); places -- holidays and
restaurants, the kinds nearest the filter and loop world -- read lower (-7,
-4). **A cause, named:** the gate was set from finding 185's unfiltered
plain web (0.40, one seed). Finding 189, committed after this was
registered, read the filtered file itself in mix_v3 at 0.35 and 0.33 and
finding 191 at 0.35 and 0.34 on 192 items -- a gain of about 0.04 over Edu,
which in E2's mix, beside five generated sources, comes out near 0.01. The
arm used the filtered file, so its miss is 189's cell P again, smaller.

**Knows fails** at three of three, and the plain starts read lower than the
Edu starts on filtergen's own lexicon (14-21 against 17-22) and on fields
(16-18 against 18-23) -- a direction, no gate. The "near wish" count (with
a clashing wish credited): 28, 29, 36 against 23, 29, 39.

**The filter forms at no start** (E2: one). At 1337 and 3337 nothing moves.
At 2337 -- the seed that read the wish on Edu and passed the swap in finding
148 -- the plain start keeps the first-place habit (128 of 288 held-out picks
are the first ok place) and loses the read under it: habit-free 74 against
chance 79, where its Edu twin read 91. **Cause not named.** A candidate, not
tested: at one seed in three the read's formation is not held by the seed
once the data stream changes -- finding 148 saw the same habit move seeds
when E became E2 on a 2,520-line change.

## The loop fine-tunes

`probe_loop.py --split` (finding 184's rebuilt read), a trace right when
every batch is:

    run              installs     gives up     reads it     by meaning   answer batches
                     of 240       of 48        of 148       of 120       early / miss / wrong
    gate             >= 0.85      >= 0.85      >= 0.80      >= 0.60
    184 loop ev2      48           47            0           25           1 / 189 / 2
    184 loop ev2s2    47           47            0           24           1 / 192 / 0
    184 loop ev2s3    48           48            0           24           0 / 192 / 0
    loop ev2p         48           48            0           24           0 / 192 / 0
    loop ev2s2p       48           48            0           24           0 / 192 / 0
    loop ev2s3p       48           48            0           24           0 / 192 / 0

The split read, the full-line read and his free line agree to the trace at
every fine-tune; the length bias the split read was built for counts 0 of
436 answer batches at each. **Every trace right is a trace with no answer**:
installs, reads it and by meaning fail at three of three; gives up passes at
three of three and means nothing. Finding 184's collapse, unchanged and now
without its three stray batches.

**Inside** (`probe_loop_inside.py`; the stop lean `d` = loss(`pick: none`) -
loss(`pick: because`), and on answer batches the right place ranked first
among the places by full loss):

    run              AUC answer vs none batch     right place first
                     train   held   swap          train (of 192)  held (96)  swap (148)
    start plain       0.41    0.39   0.58            91             44          61
    start _seed2      0.50    0.48   0.53            83             48          71
    start _seed3      0.42    0.40   0.59            74             45          64
    loop ev2p         0.63    0.64   0.41           101             47          73
    loop ev2s2p       0.62    0.63   0.40            88             41          75
    loop ev2s3p       0.63    0.63   0.44            80             38          67
    184's loops       0.62-0.64  0.63-0.66  0.38-0.49   94, 116, 90    46-51       75-101

The fine-tunes' stop lean rises on the batches holding the answer (0.62-0.64)
and not on the swap twins (0.40-0.44), where only the wish moved -- finding
184's picture to two places. **The soft read fails at three of three**:
101, 88 and 80 of 192 against a gate of 125 and a chance of about 81 (0.53,
0.46, 0.42). The 2337 fine-tune, which read 116 (0.60) on Edu, reads 88 --
the same seed's filter read lost before the fine-tune began. Named cause, as
finding 184's: the decision has nothing to read and falls to the payload's
majority answer.

**`tool.copy_wide`** (side column): 288, 286, 283 of 300 against finding
184's 298, 264, 286 -- the second start's fall to 264 does not repeat here.

## Read by hand before it was quoted

* **The loop line.** 24 answer batches (8 per fine-tune, across trained and
  held-out rows) decoded greedily by an eager loop, not the probe's graphed
  decoder: `pick: none` on 24 of 24, as the probe's 3,600 free lines (1,200 a
  fine-tune, every one `pick: none`). Forced past `pick: because[`, the place
  he names is right on 2 of 8 (plain 2337), 4 of 8 (Edu 2337) and 4 of 8
  (plain 1337); the misses read as meaning misses -- "homely" -> "a
  brasserie facing the hills" over "a bistro with cushions and lamplight",
  "for the little ones" -> "a hotel with woollen throws" over "a hotel that
  hands out crayons" -- and two forced lines blend two places ("a guesthouse
  with a beer garden", "a hostel with a crackling fire"), which a read
  ranking listed places cannot credit or fault. The instrument agrees with
  the text.
* **The filter line.** Eight trained items read whole on the 1337 start:
  the scored read is right on 4; his free line names the right place's
  description on 2, a wrong place's on 3, and on 3 writes a description
  belonging to no place ("a canteen with cushions and lamplight" from "a
  diner with cushions and lamplight" and "a canteen with oak beams"), and
  the id he writes after it is the described place's on none of the 8. The
  free line is a side column; the gated read scores each place's whole line
  and behaved as designed on all 8.
* **The ruler.** Twelve field misses on the 2337 start, every one a plain
  meaning miss ("a recipe for a big family gathering" -> cost, gold
  servings; "a pokemon that can take a hit" -> attack, gold defense). No
  hole found.

## Against the prediction

Predicted: understands passes at three of three; knows, filter, loop and
soft read fail -- filter at one of three, loop's installs at none, the soft
read 0.47-0.60. **Understands failed (one of three)**, which moves the arm
off the predicted row onto "understands fails". Knows held (fails). Filter
failed lower than predicted, at none of three. Loop held (installs at none).
The soft read held at two fine-tunes and fell below the predicted band at
the third (0.42).

**Two rows match, and one governs.** "Understands fails" and "starts split
on any gate" (understands passes at 2337 alone). The first governs: the
2337 pass is two items over the line on the 96 the gate was set on and
under it on all 192, inside the read's spread, and the split row is for a
gate whose seeds disagree beyond that; every row that would answer the
question -- vocabulary the wall, or the predicted "the ruler's words are not
the rung's" -- needs understanding to have moved first.

## What it licenses

* **The question is unreadable from this arm, as its own table says.** The
  everyday web was the means; inside E2's mix the filtered plain file moved
  the understanding read by 0.01, so a flat rung beneath it says nothing
  about whether vocabulary was the wall.
* **What it does show is that the soft read under loop does not come free
  from a different web at nano.** With the web swapped, the one seed where
  the filter read formed lost it (why is not named); at three starts
  the soft read sits at 0.42-0.53, as finding 184's did, and loop's constant
  is the same constant.
* **For finding 184's open call** -- a stop the runtime can check, or the
  soft read itself as the work: this removes the cheap corpus route to the
  soft read at nano. The checkable stop remains the arm that can read loop's
  control at this size; the soft read, if it is the work, needs something
  this arm did not supply -- its words in real descriptions, a source aimed
  at them, or 260M. The call stays the owner's.
* **The filter gate, read with finding 148's habit-free column beside it**,
  is the honest read of this rung: a start with the first-place habit can
  pass the plain count on position (Edu 2337's 97 is 50 of 81 where the gold
  is first, 47 of 207 where it is not).

**What it does not settle.** Whether the unfiltered plain web, or the blend
D1 took, moves understanding inside E2's mix; why the 2337 start lost the
filter read (a candidate named, not tested); anything at 260M; whether
loop's control installs on a checkable stop.
