# More ways to phrase each move helps unseen phrasings modestly

**Full result:** A3b and finding 158's pair: more ways of saying each move holds unseen phrasings at 40 and 38 of 100 at both seeds (A3: 32 and 20) and installs at both, a direction by A3b's table; capping how often any wording is seen buys nothing on far phrasings -- level at one seed, unreadable at the other, both arms running on the seed's default label -- so finding 158's lever is not shown at nano, no guard is built, and its family contrast fails

**Cost:** 93.9 min of training six nano runs (15.1-16.5 min each, contended -- the card sat at 35% before the chain, so a bound); 7.4 min of scoring two standard cards; `probe_move.py` 6.4 min, the tag scorings 1 min and the repeat probe 0.5 min over the six; the chain 11:27-13:17 on 2026-10-10 end to end, against a registered ~45 + ~65 min of card.

Two pre-registrations read together because one chain ran them: A3b's
(`configs/mix_v3_a3b.py`, finding 157's experiment B -- the move line over
1,021 hand-written phrasings, `share`, a trained goodbye, a funded
consolation), whose first two attempts died on 2026-10-09 with no finished
checkpoint; and finding 158's one-variable pair (`configs/mix_v3_a3b_cap.py`,
committed at fd71ddd before a byte trained): A3b's slice cut two ways at the
same size move for move, **cap** with no wording seen more than five times
and **rep** keeping the transcripts whose wordings A3b repeats most -- a
whole-line table over 0% of the move lines against 38%, read alike by a word
counter (53 and 53 of 100 unseen). Every run resumable (`--resume-every
500`), both seeds (1337, 2337). Readers committed before any result
(ead7e93): `probe_move.py --read-b`, `--read-pair`, `--read-contrast`.

## A3b, by its registered table

    gate                      seed 1337                  seed 2337
    unseen (of 100)           40 against A3's 32: +8 fail   38 against 20: +18 PASS
    goodbyes (of 20)          8 fail                     11 PASS
    natural (of 62)           37 against 33: +4 fail     35 against 28: +7 PASS
    installs (of 104)         86 PASS                    89 PASS
    routing                   route.social 93 vs 101 FALLS    tool.selection 76 vs 106 FALLS
                              (the rest hold)            (the rest hold)
    beside, unseen + goodbyes
      per-token mean          51 (A3 37)                 57 (A3 26)
      first token             49 (A3 36)                 49 (A3 19)

**By the table: seeds split on three gates -- a direction; no third seed.**
`installs` passes at both seeds: the funded `consolation` is what A3's split
lacked. **No routing kill**: the kill needs one row below its half-width at
both seeds, and the two falls are different rows -- `tool.selection` is the
row finding 157 recorded at 46 and 90 across two off cells, so a 30-item
swing on it is its own seed noise. **The split on `unseen` is the control's,
not A3b's**: A3b reads 40 and 38 at the two seeds; A3 read 32 and 20. Under
both other scorings A3b is up 13-31 at both seeds. The registered
prediction -- unseen fails, goodbyes and natural pass, installs passes, no
routing kill -- holds on installs and routing and splits on the rest.

## The pair, by its registered table

    gate                      seed 1337                  seed 2337
    lever (of 120 unseen)     cap 25, rep 31: -6 level   cap 24, rep 16: +8 (unreadable)
    signature (trained/unseen gap)   cap 0.51, rep 0.39: fail   cap 0.24, rep 0.42: pass
    curve (rep, seen >10x)    21 of 28 (75%): fail       20 of 28 (71%): fail
    trained (of 104)          cap 75, rep 67             cap 46, rep 58
    unseen five (of 100)      cap 24, rep 22             cap 15, rep 12
    commonest unseen label    cap open 41, rep open 44   cap open 69, rep share 57

**Seed 2337 is unreadable by the registered bar** -- both arms at or under 20
of 100 on the unseen five (15, 12): nothing learned either way. **At the
readable seed the lever is level, the wrong way by six.** By the table that
is "taking the table away does not make him learn the move at nano: the
binding limit is the model or the evidence, and no guard is built on this
rule" -- read on one seed, because the other could not be. The registered
prediction (the lever passes at both seeds) is not borne out.

## Finding 158's family contrast fails

    seed     consolation + farewell   wellbeing + thanks   the seed's default, and where it fell
    1337     21 / 40                  16 / 40: +5          `consolation` (36 of 120): 23 in the low pool, 5 in the high
    2337     17 / 40                  15 / 40: +2 fail     `farewell` (23 of 120): 13 low, 1 high

The registered bar was +5 at both seeds. The one pass sits on the confound
the registration named: the default label landed in the pool it lifts. Per
family, unseen accuracy follows the seed's default, not the lookup mass.

## Why, read by hand

**On far phrasings every arm runs on a default.** The unseen probe was
filtered against every trained carrier by exact match, containment and
letter-trigram similarity (`check_moveline.py` section 8), so it measures
reach to phrasings *unlike* anything trained. There, each checkpoint writes
one or two labels for most items -- cap `open` 41 and 69 of 120, rep `open`
44 and `share` 57 -- and what reads as accuracy is which family those
defaults happen to match: cap's +8 at seed 2337 is its second default,
`farewell`, written 20 times, scoring 9 of the 20 goodbyes. Side by side at
seed 1337 the arms differ item by item ("that adds up", "duly noted": cap
`open`, rep `ack`; "I'm running on empty", "it's all a bit much": cap
`consolation`, rep `share` / `open`) in the direction of each one's
defaults.

**Near phrasings are a third regime, and the cap bought it at one seed.** On
the 104 trained phrasings -- stock forms, close kin of lines both arms
trained on -- cap at seed 1337 labels a phrase contained in ten or fewer of
its lines right 47 of 67 times (70%), where finding 158's curve puts a
wording seen ten or fewer times near the unseen rate. It did not memorise
them (no wording past five sightings); it labelled near variants. At seed
2337 the same cell reads 33 of 67 and cap wrote `open` on 69 of 120 unseen:
that checkpoint installed less of everything. So there are three regimes,
not two -- exact recall past about ten sightings, interpolation to near
variants, and reach to far phrasings -- and **finding 158 read "not
memorised" as "learned the idea"; capping repetition moves the second, not
the third.**

**The curve's misses sit at its line.** Every miss is a wording seen 11-16
times (rep's most is 25, where A3's top bucket was 61+ at 98-100%), and the
two repeated at both seeds are `ack` phrasings with a thanks word in them
("that's perfect", "that's helpful", 14 sightings each, labelled `thanks`).

## What it licenses

* **For D7 and the move line**: A3b's direction -- the wider user side holds
  the unseen five at 38-40 of 100 where A3 read 20-32, installs at both
  seeds, no routing kill. It is a bundle (variety, `share`, a trained
  goodbye, a funded consolation) and the read names the arm. It is still
  under the word counter on its own slice (53), and on natural openings
  under the first token it is mixed (44 and 38 of 62 against A3's 48 and
  30).
* **For finding 158**: capping repetition is not a lever for reach at nano.
  What survives is a description, not a recipe: a decision whose wording
  recurs past about ten sightings in a nano pass is labelled from memory,
  and a slice that removes those recurrences loses nothing measurable here
  (cap's trained cell ties or beats rep's at one seed, falls at the other;
  routing holds in both). **No guard is built.**
* **Where the limit is not**: the table (this pair), the word evidence (the
  word counter reads both arms at 53), and same-sentence rivals for
  extraction (finding 158's amendment). Where it might be, untested: the
  model's size (D11's pilot at 260M), and whether a move's idioms ("consider
  it heard", "running on empty") need meaning a nano pass over this mix
  does not carry.

## What it does not say

That variety is the cause of A3b's lift -- the arm is a bundle. Anything at
260M (finding 51: nano flips sign there). That the pair's level reading
holds at a second seed -- the second was unreadable. That near-variant
interpolation is a stable property of a capped slice -- one seed showed it.
`harness/results/nano20m_v3_a3b{,_seed2}__depth.json` (the repeat probe) and
the standard cards' social rows are on disk and not read here.

## Amended 2026-10-10: on far phrasings the words are there and he does not use them -- size more than meaning (probe only)

Asked by the owner: is the far-phrasing limit meaning (the words do not
carry the move) or size (the net does not use word evidence that is
there)? `scripts/probe_move_cues.py` (card `evals/results/move_cues__159.json`),
CPU, on the eight checkpoints' committed items, with the two readings written
down before the first run: meaning predicts right where a training cue word
points to the gold and lost where none does; size predicts poor even on
cue-covered items, well under the word counter there.

    checkpoint (default)        a cue word points to the gold      no cue word points to it
                                he          word counter           he          word counter
    A3 on    1337 (greeting)    15/28 54%   21/28 75%              17/92 18%   27/92 29%
             2337 (open)        13/28 46%   21/28 75%               7/92  8%   27/92 29%
    A3b      1337 (consolation) 30/60 50%   48/60 80%              18/60 30%   22/60 37%
             2337 (farewell)    28/60 47%   48/60 80%              21/60 35%   22/60 37%
    cap      1337 (open)        16/58 28%   46/58 79%               9/62 15%   24/62 39%
             2337 (open)        18/58 31%   46/58 79%               6/62 10%   24/62 39%
    rep      1337 (open)        19/51 37%   42/51 82%              12/69 17%   27/69 39%
             2337 (share)       13/51 25%   42/51 82%               3/69  4%   27/69 39%

**By the readings written first: size.** Where a cue word carries the move
the word counter is right on 75-82% and he is right on 25-54% -- at every
checkpoint, 25 to 55 points under it. Meaning is the smaller part: without a
cue the word counter itself falls to 29-39%. By hand (A3b, 1337): "i'm
logging off" -- `off` sits in 121 farewell lines -- he writes `consolation`;
"i'm done for the night" -- `night` in 98 -- `share`.

**Not the opening either** (the guess the hand read prompted, checked and
dropped): on items whose first word opens five or more lines his label is the
opening's move on 22-38% and the word counter's on 25-44%, and where the two
disagree he follows the words a little more often at six of eight
checkpoints (rep's two the exceptions); his default is the largest single
share, 20-73%. He mostly commits to no evidence, and when he does it is
weakly the words.

**The one ordering in it**: cue use tracks how many lines the slice has --
A3 (16,586 move lines) and A3b (15,352) read 46-54% on covered items, cap
and rep (8,733 and 9,383) 25-37%. Read with finding 159's pair, the next
lever is exposure to each cue with its move -- more distinct lines -- or a
model that takes word evidence from fewer of them (D11's 260M pilot), not
the table. Untested, both.

## Amended 2026-10-11: read from inside -- finding 161

Probe C read the far-phrasing limit at his decision point on the same eight checkpoints. A linear reader on his own state reads 46-55 of 100, at the word counter's level and well over an untrained net of his shape, in every arm; what differs between arms is how much of it the written label uses (A3b 32 of 47-48, the others 11-27). So this finding's "size more than meaning" has two layers: a readout that writes a default over a move the state holds (A3, cap, rep), and, at A3b, a state that does not hold the move on about 45 of 100 far phrasings. A3b's lift above is the first layer closing.
