# Balanced keep-looking odds flip loop from never stopping to always stopping

**Full result:** Finding 184's loop fine-tune on a payload balanced so `pick: none` is the right line on half the batches at every batch position, with the answer's slot, the wish, the wording and the places' concepts spread so no wish-blind reader beats 0.59, lands on the pre-registered row "the constant flips": at all three starts he now stops on every batch -- `none` on 0.004, 0.010 and 0.006 of the balanced held batches (gate 0.35-0.65; finding 184's fine-tunes 1.000, 0.999, 1.000) -- and stop-or-not reads 0.499, 0.501, 0.500 on the balanced train batches (gate 0.60; always `none` 0.500), so every gate fails at three of three (installs 27, 30, 24 of 240; gives up 0 of 48; reads it 73, 81, 55 of 148; by meaning 14, 12, 12 of 120); inside, his stop lean is the same number on batches that hold the answer and batches that do not (+0.22 to +0.24 nats, AUC 0.48-0.51 on the balanced rows), where finding 184's sat at -1.48 on both -- **the decision is the payload's base rate and nothing else, and greedy decoding turns a 56% coin into a constant**; no new slot or batch constant appears, and the place he names on an answer batch is right 0.58, 0.67, 0.53 of the time on trained pairings and 0.52, 0.56, 0.48 on held ones (chance about 0.42)

**Cost:** the CPU build and reads 16:51-17:43 on 2026-10-21 (the generator, the guard, the fit of the batch draws 17 s, the mix 12 s); the zero-training control 785.8 s (17:29-17:42); pre-registered at aaf7536 (17:43:35); one chain under the card's lock 17:43-18:04, 1,224.5 s -- three fine-tunes of 159, 161, 161 s, on each a split read of finding 184's rows 80 s and of the balanced rows 159-160 s, a copy row 8 s -- registered ~16 min, actual 20.4 min; the inside read on nine checkpoints and both row sets 342.5 s (18:04-18:10); all contended (the card at 36-39% before every job, a bound).

**The owner's instruction, 2026-10-21**: balance the payload properly --
"make sure the picks are spread properly too so he doesn't pick the first
one consistently or second. All should be spread properly so he doesn't
learn a shortcut." Finding 184's payload put the answer on batch 1, 2, 3, 4
or nowhere a fifth each, which balances traces and not decisions: `pick:
none` was right on 14,858 of 20,795 batch decisions (71%), and findings 184
and 194 collapsed to it at every start. Pre-registered at aaf7536
(`configs/mix_v3_loop_ft_bal.py`), after the control and before a byte
trained.

## The balanced payload, and a route found on the way

`corn/loopgen.py` `BalancedSchedule` (its docstring is the design), through
the same `build`, lexicon and holdout: a geometric stop at p = 1/2 -- of
every 16 traces a pairing gets, the match on batch 1 in 8, batch 2 in 4,
batch 3 in 2, batch 4 in 1, nowhere in 1 -- so stop and keep looking are
0.500 each at batches 1, 2, 3 and 4 (12,288 traces, 23,040 decisions, batch
4 decided 1,536 times); the answer's slot cycled per size and stop batch
(0.500/0.500 and 0.333/0.333/0.333); every wish the answer exactly as often
as a keep-looking; no key of the wording above 0.507. Finding 184's file
regenerates byte for byte.

**The places needed more than a shuffle.** No distractor may be of a concept
that clashes with the wish (no near answer), so a stop batch holds the wish
and none of its clash partners and a keep-looking batch holds neither.
Drawn evenly, as finding 184's were, **the batch's set of place concepts,
the wish unread, settles stop-or-not at 0.66 with two places and 0.72 with
three, and given a stop names the answer at 0.56 and 0.58** (exact, chance
0.50 and 0.33). A first fix -- weighting the draw so each concept is the
answer on a fifth of its showings -- made the set route worse (0.76). With
eight concepts and five clashes the routes cannot all reach chance: at
three places the set route and the slot route trade along a front
(`scripts/fit_loop_draws.py --grid`). The payload's places come from a
fitted per-(size, outcome, wish) draw (`corn/loopgen_draws.json`) that
takes them to 0.54 / 0.59 and 0.53 / 0.47 on the bytes, each wish's
distractor concepts alike in stop and keep-looking batches.

**Read before the GPU** (`scripts/check_loop.py` §7-8, a reader per route
and six mutants, each failing its check): every content-free policy 0.500
on stop-or-not; the places' concept set 0.561 (payload), 0.565 and 0.568
out of sample on the train and held rows; novelty (places new to the trace)
0.550, 0.563, 0.568; a bag of the places' words 0.529 and 0.531; a bag of
words with the wish 0.992 on trained pairings -- the lexicon as a table, a
route by design -- and 0.565 on the held ones. Twenty traces read by hand:
each gold the only right answer, nothing in the wording, the batch or the
position that a table could answer from.

## The control

`probe_loop.py --split` on the balanced rows (768 train, 384 held, 337 swap;
2,518 batches), before anything trained:

    run                  held none share   train stop-or-not   right place on answer batches
                                                               train (of 720)   held (of 360)
    start ev2                0.000              0.500              339              143
    start ev2_seed2          0.000              0.500              353              166
    start ev2_seed3          0.000              0.500              308              156
    184 loop ev2             1.000              0.500                0                0
    184 loop ev2s2           0.999              0.500            1 of 1               0
    184 loop ev2s3           1.000              0.500                0                0

The starts always stop; finding 184's fine-tunes never do. Every one sits on
the content-free 0.500.

## The read

`probe_loop.py --split` (the registered read: the decision at its one token,
the place by full loss) on finding 184's rows and on the balanced rows:

    run                 installs  gives up  reads it  by meaning  no collapse      above routes
                        of 240    of 48     of 148    of 120      held none share  train stop-or-not
    gate                >= 0.85   >= 0.85   >= 0.80   >= 0.60     0.35-0.65        >= 0.60
    loop ev2b             27         0        73         14          0.004            0.499
    loop ev2s2b           30         0        81         12          0.010            0.501
    loop ev2s3b           24         0        55         12          0.006            0.500
    (finding 184)        47-48     47-48       0         24        0.999-1.000        0.500

**Every gate fails at three of three, the other way round from finding
184.** On finding 184's rows he stops too soon on 476, 478 and 474 of the
480 train batches without the answer and misses 4, 1 and 4 of 192 answer
batches; a trace is right only when the answer is on batch 1 and he names
it. His free line agrees with the split read to the trace on the train
cell (27/28, 30/30, 24/24) and within 0.01-0.03 of stop-or-not on the
balanced held cell. **The prediction -- the collapse goes away, the stop
bounded by the soft read -- was wrong on its first half.**

**No new slot or batch constant.** His stop rate is 0.96-1.00 at every batch
position on the balanced train and held rows (gold 0.50); of his stops, the shares by slot are
0.50-0.57 / 0.43-0.50 in batches of two and 0.29-0.39 in batches of three --
the first of two places a little favoured at the first start (0.565), the
gold's own uniform elsewhere. What he writes is a stop on every batch, the
place chosen by the soft read.

**The baselines.** Batch right on the balanced rows, against always `none`
0.500, always the first place 0.210 and `none` till batch 4 then the first
0.481: train 0.292, 0.338, 0.265; held 0.260, 0.285, 0.237. Below always
`none` -- a stop on every batch can only be right on the half that hold the
answer, and there only with the right place.

**`tool.copy_wide`** (side column): 298, 258, 285 of 300 against the starts'
298, 295, 293 and finding 184's 298, 264, 286 -- the second start falls
again; one seed of three, not readable by finding 170's rule.

## Inside: what the stop reads

`probe_loop_inside.py` -- the stop lean `d` = loss(`pick: none`) -
loss(`pick: because`), no length term, and on answer batches the right place
ranked first among the places -- on both row sets (`--rows
evals/funcworld_loop_bal.jsonl` for the balanced ones; the log is
`evals/results/nano20m_ft_loop_bal__inside.txt`):

    run              mean d, answer / none batch    AUC answer vs none     right place first
                     (balanced train)               train   held   swap    184 rows (of 192)  balanced train (720) / held (360)
    start ev2         +17.49 / +17.51                0.49    0.50   0.71         --              339 / 143
    start _seed2      +18.36 / +18.42                0.47    0.50   0.56         --              353 / 166
    start _seed3      +20.28 / +20.28                0.50    0.50   0.59         --              308 / 156
    184 loop ev2      -1.48 / -1.48                  0.50    0.50   0.47         94              372 / 171
    184 loop ev2s2    -1.50 / -1.50                  0.51    0.50   0.42        116              477 / 204
    184 loop ev2s3    -1.46 / -1.46                  0.51    0.49   0.40         90              366 / 168
    loop ev2b         +0.22 / +0.23                  0.48    0.51   0.61        102              420 / 185
    loop ev2s2b       +0.24 / +0.24                  0.50    0.50   0.55        116              485 / 200
    loop ev2s3b       +0.24 / +0.24                  0.50    0.48   0.57         91              381 / 171

**The cause, named.** The stop lean is one number per checkpoint, the same on
batches that hold the answer and batches that do not (AUC 0.48-0.51 on the
balanced train and held cells at every fine-tune, both arms). On finding
184's payload it settled at -1.48 nats -- the stop at about 0.19 -- and here
at +0.23, the stop at about 0.56: in each case **the payload's base rate,
with a small lean, and nothing read from the batch.** Greedy decoding then
takes the larger side every time, so a calibrated coin prints as a constant,
and which constant follows the base rate: 71% `none` gave always `none`, 50%
gave always stop. Balancing the share moved the coin; it could not give the
coin anything to read, because the input that should move it -- the soft
read of the places against the wish -- does not reach the stop. Why the
balanced lean sits on the stop side rather than at zero is not named (a
candidate, untested: the replay's other `pick:` lines, every one followed by
a place).

**The soft read under it, unchanged where it counts.** The place ranked first
on answer batches moves little: on finding 184's rows 102, 116, 91 of 192
against 184's 94, 116, 90; on the balanced train rows 420, 485, 381 of 720
against 372, 477, 366; on the held rows 185, 200, 171 of 360 against 171,
204, 168 -- level (chance about 81 of 192, 300 of 720, 150 of 360). It is a little
better than the starts' (the format) and no better than finding 184's at
the start that read the wish (2337).

## Read by hand before it was quoted

Fourteen balanced rows on the 2337 fine-tune, eight held and six trained,
every batch's free line against its gold. Every keep-looking batch gets a
stop, the place's description copied exactly with its filler cut, so the
line is well formed and the decision is the only thing wrong. On answer
batches he names the gold on 7 of 14; the misses read as meaning misses --
"for the little ones" -> "a hotel with blankets on every chair" over "a
hostel with a puppet show on sundays", "where we can talk" -> "a boarding
house with a play corner and toys" over "a serene lodge", "outdoors" -> "a
pub with high chairs" over "a bar with a beer garden". On none batches the
place he stops on is not the most wish-like one ("outdoors" -> "a candlelit
cocktail bar"). The instrument agrees with the text: the split read, his
free line and the inside read say the same thing three ways. The full-line
read (finding 184's registered one, a side column) disagrees -- installs 57,
67, 51 -- because its length bias favours the two-token `none`: it picked
`none` on 177, 157 and 153 of 436 answer batches where his free line wrote
the gold, the hole finding 184 named.

## What it licenses

* **Finding 184's collapse was the base rate, and so is this one.** The
  owner's balancing did what it was built to: no `none` majority, no batch,
  slot, wish, wording or place-set route above 0.59, and he took none of
  them. With every cheap route shut, the decision fell to the one thing left
  -- the share -- because the meaning hop under it is not there to read.
  GENERATORS §2's line holds a third time: a low lookup route is necessary
  and not sufficient.
* **A balanced decision has to be read by its margin, not its argmax.**
  Where the input does not move the decision, greedy decoding prints the
  base rate as a constant of either sign; the inside read (`d`, AUC) is the
  read that tells "reads nothing" from "reads and leans". For loop's
  decision every read so far, two payloads and two web sources, says it
  reads nothing.
* **For the owner's loop call -- a checkable stop, or the soft read itself
  as the work.** This takes away the reading that the payload's share was
  hiding a decision: no balancing of the soft-stop format forms one at this
  size. A stop the runtime can check would split the iteration format from
  the soft read, as branch did; the soft read as the work is the meaning hop
  findings 148, 156, 167-168, 184 and 194 stopped at, and this adds no
  evidence it forms from the loop format at 20M. The call stays the owner's.
* **For any future generator on filtergen's lexicon:** the clash rule makes
  the batch's set of concepts a wish-blind route (0.66-0.72 drawn evenly).
  Finding 184's payload, filtergen's own lists and anything built on them
  carry it; `check_loop.py` §7's set and slot readers are the measure.

**What it does not settle.** Why the balanced lean is on the stop side; whether
the soft read forms at 260M or with real descriptions; whether loop's control
installs on a checkable stop; the second start's copy species.
