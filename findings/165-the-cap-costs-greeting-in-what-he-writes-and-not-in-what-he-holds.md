# One hundred and sixty-fifth finding — the wide greeting read: the cap costs greeting in what he writes and not in what he holds -- on 161 hand-written greeting phrasings the four mix checkpoints write 58, 71, 59 and 108 against 83-106 without the cap (means 74 and 94, twelve points), "costs greeting" by the table, while the inside read is level (130-148 against 138-148); "hello again", "hi mate" and "just popping in to say hello" go to `ack`, `open` and `farewell` with greeting in the state, and two training seeds of identical data write 59 and 108

**Cost:** 98 s on the card (eight checkpoints, 161 phrasings scored over eight moves and the inside read; contended -- the card at 39%, a bound); no training; 17:07-17:14 on 2026-10-11 end to end, build and pre-registration commit included.

Pre-registered in `scripts/probe_greeting_wide.py`'s docstring and committed
at b0cc2a1 before any item was read. Findings 163 and 164 read greeting on
twenty phrasings and could not settle whether capping the real openings
costs it (5, 6, 4 and 12 on the four mix checkpoints against 11, 15, 10 and
9; 4 against 12 on two seeds of one draw). This reads **every hand-written
greeting carrier the slices draw from** -- `CARRIER_POOLS` and
`move_carriers.txt`, 186, less the held-out sets and the twenty already
read: 161, none drawn -- on the eight checkpoints on disk. No training.

## The registered read

    checkpoint        written (of 161)   inside (of 161)   writes instead
    A3b      1337      87                138               ack 24, farewell 18, consolation 15
    A3b      2337     100                148               ack 26, farewell 20, open 8
    real     1337      83                142               farewell 43, ack 19, wellbeing 8
    real     2337     106                142               farewell 24, ack 18, wellbeing 8
    mix50    1337      58                130               ack 29, farewell 27, wellbeing 25
    mix50    2337      71                148               ack 33, farewell 21, open 21
    mix50d2  1337      59                142               open 26, ack 22, share 19
    mix50d2  2337     108                145               ack 22, farewell 15, wellbeing 13

**Costs greeting, by the table**: the four mix checkpoints' mean is 74 of
161 (46%) against the other four's 94 (58%) -- 12.4 points, past the bar of
8 -- and three of the four (58, 71, 59) sit under the lowest of the others
(83). My written guess was "costs greeting, about ten points".

**Not greeting's own real openings**: the real arm, whose greeting deal is
the mix arms' (29-32% SODA's), writes 94.5 on average against A3b's 93.5.
The cost comes with the mix -- consolation and share half hand-written and
half real -- and not with real text in greeting.

## Inside, level -- the cost is the readout's

Finding 161's reader at each checkpoint's registered place reads greeting
on 130-148 of 161 with the cap and 138-148 without (means 141.25 and 142.5).
On the three low mix checkpoints it reads greeting on all three for 124 of
the 161. Read by hand, the phrasings the cap loses -- written right on three
or more of the four without it, wrong on all three low mix checkpoints --
are twelve, and they are plain greetings: "hello again", "hi mate", "hello
from the couch", "just popping in to say hello", "happy monday", "hey, you
free", "what's cooking". He writes `ack`, `open`, `farewell`, `thanks`,
`share` -- a different wrong label at each checkpoint -- and the reader
reads `greeting` in his state on ten of the twelve at all three (the other
two, "hello" and "what are we getting into today", it reads `ack` or
`wellbeing` at one or two).

So the third time in three slice changes (findings 161, 162 and this): the
data moved what he writes and left what he holds. Here the readout loses a
family the cap did not touch, and loses it to no single default.

## Two seeds of identical data: 59 and 108

`mix50d2`'s two training seeds share every byte of their data and write 59
and 108 of 161 -- thirty points -- while the inside read on the same
checkpoints is 142 and 145. On 161 items that is not sampling: finding
164's eight-item swing on twenty was the same thing, smaller. **The written
readout of a family carries a large component set by the training seed,
which the state does not share.** Finding 161 saw the inside read agree
across seeds where the label split; this is the cleanest case of it.

## What it licenses

* **For C5 and D1**: at nano, one pass, the half cap keeps both kinds of
  consolation (findings 163, 164) and costs greeting's readout about twelve
  points at three checkpoints of four, with greeting held in the state at
  every one. The real arm's deal costs greeting nothing and costs the
  hand-written consolation everything. Neither deal is free; which cost 1.0
  carries is the owner's call. What 1.0 does after the run -- fine-tunes
  that amplify what the state holds (PLAN-1-0) -- is the place a readout
  cost is cheapest to repair, and no arm here tested that.
* **For the method**: a gate on a written family row is a gate on the
  training seed's readout. Gates on what the corpus *teaches* belong on the
  inside read, or on many seeds.
* **For finding 161's question**: the state holds greeting whatever the mix;
  the label is where mixes cost. Size, the open lever on the state, is the
  260M pilot's (D11).

## What it does not say

That the cost is twelve points everywhere -- one checkpoint of four has
none. That it holds at 260M or after a fine-tune. Plain carriers, not the
dressed forms the slices train; trained phrasings, the recall-and-near
regime of finding 159. One floor seed, a linear reader -- every number a
bound.
