# Greeting accuracy swings eight items on identical data

**Full result:** The mix arm's second draw: greeting is unreadable by its table -- the two training seeds of one draw read 4 and 12 of 20, so the family moves eight items on identical data, and pooled over the four mix checkpoints it reads 4-12 against 9-15 on the four without the cap, a direction and not a reading; finding 163's table on this draw splits (installs 72 at one seed, real consolation 82 against a bar of 84 at the other), while both kinds of consolation hold on all four mix checkpoints -- hand-written 14-16 of 24, unseen real 82-98 of 100 -- and the state on far phrasings reads 50-54 on every one against 47-48 without

**Cost:** 987 s and 989 s of training (two nano runs at 5,337 iterations, contended -- the card at 39% before the chain, so bounds); `probe_move.py` 63 s each; the inside read over four arms 173 s; the fresh held-out read over eight checkpoints 101 s; the chain 2,377 s end to end, 16:23-17:03 on 2026-10-11; the build and the pre-registration commit 16:16-16:23; the table's read and the hand read under a minute on CPU.

Pre-registered in `configs/mix_v3_a3b_mix50d2.py`'s docstring and committed
at d2a27c7 before a byte trained. Finding 163's mix arm read "real only"
because greeting fell to 5 and 6 of 20 at both seeds of one draw of the
slice, with its exposure and word evidence level. This is that slice's
second draw -- generator seed 66, everything else unchanged
(`gen_social_v5.py --soda-cap 0.5 --seed 66`; `check_moveline.py` section 12
regenerates both draws byte for byte, a mutant passing one off as the other
caught). Greeting's twenty phrasings are seen 131 times in this draw (144 in
the first), a word counter fit on it labels 18 of them right (17).

## The registered read

    checkpoint        greeting   installs   consolation   untouched   fresh real openings, written   S
                      (of 20)    (of 104)   (of 24)       (of 60)     consolation    share
    mix50d2  1337      4         72         16            52          96 (real 91)   100 (100)       9
    mix50d2  2337     12         82         14            56          82 (real 94)   100 (100)      11

The fresh draw is 100 consolation and 100 share SODA lines none of the four
payloads holds (`evals/results/move_inside_mix50d2__soda_heldout.json`), all
eight checkpoints re-scored; the bars read against the real arm on the same
draw.

**Unreadable first, and it is not**: S 9 and 11 (stop 30); the untouched
families 52 and 56 (bar 45).

**Primary, greeting -- unreadable**: 4 at seed 1337 and 12 at 2337. "The
draw" needed 9 or more at both and "the cap" 6 or fewer at both; the two
seeds of one draw straddle both bars. By the registration, a third draw is
not run on this one's account.

**Replication, finding 163's table -- split**: idioms held at 2337 only
(installs 82, consolation 14 against 13) and not at 1337 (installs 72);
real reached at 1337 only (consolation 96 against a bar of 81) and not at
2337 (82 against a bar of 84, two items). My written guess -- the draw, and
so "both" -- is not borne out by either table.

## Read by hand: what moves and what does not

Greeting on the eight checkpoints that bear on it:

    A3b 11, 15      real 10, 9      mix50 5, 6      mix50d2 4, 12

On this draw's two seeds, **some phrasings fail on every mix checkpoint** --
"evening", "good evening", "wassup" written `ack`, "howdy" `wellbeing` --
and **one cluster flips with the training seed**: "what have we got going on
(today)", "what's the plan today" and their spellings, `share`,
`consolation` and `wellbeing` at seed 1337 and `greeting` at seed 2337.
Those are the greeting set's least greeting-like items, and at seed 1337
they go to the families the cap left half real. So greeting on this item
set swings by up to eight items between training seeds of identical data:
**a 20-item family is noisier than the registered bars allowed for**, and
the pooled numbers (mix 4-12, mean 6.75, against 9-15, mean 11.25) are a
direction toward a cost of about four items, not a reading of one.

## Across the four mix checkpoints, what held

Reported beside the tables, deciding nothing:

    checkpoint        hand-written      fresh real          far phrasings
                      consolation /24   consolation /100    written   R_fixed
    A3b   1337, 2337  19, 18            55, 25              40, 38    47, 48
    real  1337, 2337   7,  0            91, 94              30, 33    47, 48
    mix50 1337, 2337  15, 15            91, 98              40, 46    54, 51
    d2    1337, 2337  16, 14            96, 82              35, 44    51, 50

(The fresh real column is this finding's draw for all eight, so mix50's and
A3b's move by a few items against finding 163's.)

* **Both kinds of consolation, on all four mix checkpoints**: hand-written
  14-16 of 24 where the real arm has 0-7, and unseen real worries 82-98
  where A3b has 25-55. What each registered gate missed was elsewhere
  (greeting's share of installs) or by two items.
* **The state's reach on far phrasings, on all four**: R_fixed 50-54 against
  47-48 on each of the four checkpoints without the cap, the inside read
  moving by 1-3 between seeds where the written label moved by up to 9.
  Finding 161's rule predicts it -- two kinds of speech carry more words for
  a move than one -- and it now holds at two draws, unregistered.

## What it licenses

* **For C5 and D1, by the tables: nothing is licensed.** Finding 163 read
  real only, this draw reads split, greeting is unreadable. The cap is not
  shown to be the deal.
* **Beside the tables, for the owner's call**: on every mix checkpoint the
  cap kept both kinds of consolation and widened the state's reach; greeting
  pays in three of four, by an amount inside its seed noise. If the cap goes
  to C5, greeting's cost is the thing to watch, and a greeting read on more
  than twenty items is what would settle it.
* **For the method**: a family of twenty items read through the written
  label swung by eight between training seeds of identical data, while the
  inside read held within three. A gate on a 20-item written row is a gate
  on its noise; the registrations here should have set greeting's bar from
  its seed spread, which no arm had measured.

## What it does not say

That the cap costs greeting, or that it does not. That both kinds of
consolation hold at 260M. Two draws, two seeds each, one floor seed, a
linear reader -- every number a bound.
