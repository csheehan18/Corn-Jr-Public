# One hundred and sixty-third finding — the mix arm (C5's real openings capped at half a family) reads "real only" by its table: on a fresh draw of real openings it writes consolation 89 and 94 of 100 and share 94 and 88, within 10 of the real arm, and its hand-written consolation holds at 15 and 15 of 24, within 5 of A3b -- the first slice to keep both kinds of consolation -- but `installs` reads 77 and 73 under the registered 80 because greeting falls to 5 and 6 of 20 at both seeds, with its exposure and its word evidence level with the other arms, a cause not found; beside, on the hand-written far phrasings it writes 40 and 46, at or above every arm read so far, and its state reads 54 and 51 against A3b's 47 and 48

**Cost:** 922 s and 904 s of training (two nano runs at 5,337 iterations, contended -- the card at 44% before the chain, so bounds); `probe_move.py` 58 s and 62 s; the inside read over three arms 124 s; the fresh held-out read over six checkpoints 73 s; the chain 2,143 s end to end, 15:01-15:37 on 2026-10-11; the build (the generator's cap, the guard section and two mutants, the configs) and the pre-registration commit 14:54-15:01; the greeting reads (sightings, word counter) under a minute on CPU.

Pre-registered in `configs/mix_v3_a3b_mix50.py`'s docstring and committed at
e96201c before a byte trained. Finding 162: C5's deck does not deal real
openings beside the hand-written carriers, it replaces them (97.5% of
consolation lines, 99% of share), and each arm then reaches its own kind of
line -- the real arm unseen real openings, A3b the hand-written idioms.
**With the chance of a real opening capped at one half per family, does one
slice hold both?** The one variable is `corn.socialgen._carrier`'s chance,
capped at 0.5 (`generate(soda_cap=)`; absent, every earlier slice
regenerates byte for byte, `check_moveline.py` sections 8 and 10); in what
trains, consolation is 48% SODA's and share 49%, the other families as the
real arm's. Weighted at A3b's 2,510,963 tokens, so budget, targets and
iterations are A3b's and the real arm's to the token (section 12, two
mutants caught).

## The registered read

    checkpoint     installs   consolation   greeting   untouched   fresh real openings, written
                   (of 104)   (of 24)       (of 20)    (of 60)     consolation   share
    A3b    1337    86         19            11         56          41            87
    A3b    2337    89         18            15         56          18            29
    real   1337    71          7            10         54          87            97
    real   2337    66          0             9         57          95            95
    mix50  1337    77         15             5         57          89            94
    mix50  2337    73         15             6         52          94            88

The fresh draw (`scripts/probe_real_heldout.py`, card
`evals/results/move_inside_mix50__soda_heldout.json`) is 100 consolation and
100 share SODA lines that none of the three payloads holds (6,844 and 21,029
never dealt), every arm re-scored on it; finding 162's draw excluded two
payloads, so A3b and the real arm move by a few items against its numbers.

**Unreadable first, and it is not**: the shuffled reader 12 and 19 (stop 30);
the three families the cap leaves alone (wellbeing, thanks, ack) 57 and 52
of 60 (bar 45).

**Real reached -- holds at both seeds**: consolation 89 and 94 against the
real arm's 87 and 95 (bar: within 10), share 94 and 88 against 97 and 95.

**Idioms held -- fails at both seeds, on one clause**: consolation 15 and 15
of 24 against bars of 14 and 13 (A3b's 19 and 18 less five) -- held; and
installs 77 and 73 against a bar of 80 -- missed.

**By the table the reading is "real only"**: one gate at both seeds, the
other at neither. My written guess was "both", with consolation near its
bar; the consolation clause landed there (15, 15), and the arm missed on a
family the guess did not consider.

## The cause of the miss: greeting, with the evidence level

Every point under the bar is greeting's -- 5 and 6 of 20, against A3b's 11
and 15 and the real arm's 10 and 9; consolation and the untouched families
account for the rest at A3b's level. Read by hand at both seeds: "hi" and
"howdy" written `ack`, "good evening" `ack`, "what have we got going on
today" and its variants `wellbeing` -- where A3b writes `greeting` on most.

Two causes checked and dropped, CPU, probe only:

* **Exposure.** Counted to the budget, the twenty greeting phrasings are seen
  exactly 137 times in A3b's slice, 158 in the real arm's and 144 in this
  one; "hi" inside 343, 419 and 443 greeting lines. Level.
* **The word evidence.** A word counter fit on each arm's slice labels the
  twenty greeting items right 18, 18 and 17 times. One difference is real --
  "hi" now also opens SODA's wellbeing, consolation and share lines ("Hi,
  how are you?", "Hi. I'm..."), 281 lines in this slice against none in
  A3b's -- but the real arm has more of them (354) and holds greeting at 10
  and 9, so it does not explain this arm on its own.

So the data carries greeting as well as before and this net uses less of it:
finding 161's readout layer, on a family the cap does not touch. **Why here
is not found.** The two seeds share one draw of the slice (generator seed
65), so a draw effect would show at both; a second draw is the test.

## Beside, deciding nothing

    checkpoint     far phrasings (100)        his commonest label     routing
                   written   R_fixed          on the 120 far          route.social   route.low
    A3b    1337    40        47               consolation 36          93             20
    A3b    2337    38        48               farewell 23             112            26
    real   1337    30        47               farewell 51             107            26
    real   2337    33        48               farewell 42             112            23
    mix50  1337    40        54               farewell 33             94             24
    mix50  2337    46        51               consolation 24          105            25

**On the hand-written far phrasings the state reads above A3b's and the
real arm's** -- R_fixed 54 and 51 against 47 and 48 for both, at the top of
the 46-55 every arm read in finding 161 (card
`evals/results/move_inside_mix50__fixed.json`) -- and he writes 40 and 46
there, at or above every arm read so far (finding 161's 12-40). Two kinds of speech in one slice carry more words
for each move than either alone, and finding 161 read the state as holding
what the training words carry: this is that, in the direction it predicts,
by +7 and +3 and unregistered. On the fresh real openings the state holds
consolation on 76 and 71 against the real arm's 80 and 82 and A3b's 27 and 29.
Routing holds (route.social below A3b's at 2337 only).

## What it licenses

* **For C5 and D1**: the cap keeps both kinds of consolation and the real
  reach -- the result the arm was built to look for -- and costs greeting
  at this draw. The registered licence for "real only" ("half is not enough
  for the losing kind") assumed the loser would be the capped family; it was
  not, so it does not apply as written. Before `--soda-cap 0.5` goes to C5:
  a second draw of the mix (another generator seed, two nano runs, about 35
  min of card), to read whether greeting's fall is the draw or the cap.
* **For finding 161's rule**: a slice with more kinds of words for each move
  gave the state more reach on far phrasings than either
  kind alone -- a direction for
  the rule, not a test of it.

## What it does not say

That the cap costs greeting -- one draw. That greeting's evidence is
unchanged in every sense: a word counter is one reading of it. Anything at
260M. Two seeds of one draw, one floor seed, a linear reader -- every number
a bound.
