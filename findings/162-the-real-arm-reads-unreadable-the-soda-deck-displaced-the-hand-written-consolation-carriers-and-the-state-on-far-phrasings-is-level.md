# One hundred and sixty-second finding — the real arm (A3b's mix with C5's real SODA openings at A3b's token count) reads unreadable by its own table: `installs` falls to 66 of 104 at seed 2337 under the registered bar of 70, and every lost item is a hand-written consolation phrasing -- the deck did not add real openings beside the hand-written ones, it replaced them (97.5% of consolation lines are SODA's); inside, the fixed reader reads 47 and 48 of 100 far phrasings against A3b's 47 and 48, so the state is level where the label moved: consolation's far phrasings written right 2 and 1 times of 20 against 13 and 6, the default now `farewell`

**Cost:** 915 s and 903 s of training (two nano runs at 5,337 iterations, contended -- the card at 34% before the chain, so bounds); `probe_move.py` 57 s and 60 s; the inside reads 88 s (fixed reader) and 97 s (own slice); the chain 2,120 s end to end, 13:58-14:34 on 2026-10-11; the build, the guard section and the pre-registration commit 13:45-13:58.

Pre-registered in `configs/mix_v3_a3b_real.py`'s docstring and committed at
2c33113 before a byte trained. The question, after finding 161 found the
state's read flat across every generated arm (A3, A3b, cap, rep at 46-55 of
100): **does text people actually wrote raise what his state holds on far
phrasings?** The arm is A3b's mix with the social payload swapped for
ROADMAP C5's cut with its moves rendered back, at A3b's 2,510,963 tokens --
budget, every other target and the iterations A3b's to the token
(`check_moveline.py` section 11, two mutants caught). The gate is
**R_fixed**: finding 161's reader fit on A3b's lines for both arms, so a
difference is the state's and not the reader's; read through that path,
A3b reproduces finding 161 exactly.

## The registered read

    checkpoint        installs   R_fixed   A3b's   O (writes)   F    W    S
    real  1337        71         47        47      30           32   53   18
    real  2337        66         48        48      33           32   53    9
    (A3b  1337        86         47                40)
    (A3b  2337        89         48                38)

**Unreadable, read first and decisive**: `installs` at seed 2337 is 66 of
104, under the bar of 70 the table set for "a net that did not learn the
line at all". The shuffled reader (18, 9) stays under its stop of 30. By the
table the arm has no reading; R_fixed's level (0 and 0, inside the band of
4) is reported and decides nothing. My written guess was level.

## Why `installs` fell -- the cause, not a failure to learn the line

`installs` is the 104 phrasings A3b's slice draws from. By family:

    family        A3b 1337 / 2337    real 1337 / 2337
    consolation   19 / 18  of 24     7 / 0  of 24
    wellbeing     20 / 19  of 20     20 / 19
    thanks        18 / 20  of 20     19 / 18
    ack           18 / 17  of 20     15 / 20
    greeting      11 / 15  of 20     10 / 9

Every point of the fall is consolation. The deck in `corn.socialgen` deals a
SODA opening with probability `len(soda) / (len(soda) + hand)`: 8,334 real
consolation openings against a hand-written pool in the hundreds, so in what
trained **1,591 of 1,631 consolation lines are SODA's** (97.5%), and 1,596 of
1,613 share lines. The pre-registration counted the SODA lines and called
the change real openings "beside the hand-written carriers"; it was a
replacement, and the registration's "unreadable" bar was written for a net
that had not learned the line, not for a class whose training text moved.
The line itself installed: the move line is written, the routing rows hold
(`route.social` 107 and 112 of 112 against 93 and 112, `route.low` 26 and 23
of 28 against 20 and 26).

## What moved: the label, not the state

**On far phrasings the state is where A3b's is** -- R_fixed 47 and 48, and
on consolation's 20 far items 11 and 13 against A3b's 12 and 10 (the
secondary bar, +4 at both seeds, is not met). **What he writes moved**: O on
the 100 falls 40 and 38 to 30 and 33, and on consolation's 20 to 2 and 1
against 13 and 6. Read by hand (both seeds): "i've had better weeks",
"today has been a slog", "i can't catch a break", "i'm running on empty" --
the reader on his state reads `consolation` on most of them, and he writes
`wellbeing`, `farewell`, `open`, `greeting`. Only "i've been struggling
lately", the one phrasing shaped like a SODA opening, he writes
`consolation` at both seeds. His default on the 120 far items is now
`farewell` (51 and 42 of 120), which is why `goodbyes` reads 17 and 19 of 20
against A3b's 8 and 11 -- the default landing on the family, not a goodbye
learned (finding 159's confound, named there).

So finding 161's two layers again, from the other side: a slice change moved
the readout and left the state level. A3b's slice had moved the readout
toward the right label (finding 161); this one moved it away, because the
hand-written consolation idioms the probe asks about are no longer what
consolation is made of in its training.

**The own-slice reader agrees**: fit on the real cut's lines, it reads 43
and 39 of 100, and consolation's far items 4 and 1 -- a reader taught
consolation from SODA lines does not recognise the hand-written idioms
either. That is the reader confound the registration named, measured: on
this test it runs against the real slice, not for it.

**Read after, post hoc**: what he writes on real openings neither arm
trained on -- the yardstick a person talking to him would set. It is the
amendment below, and it moves the picture: on real openings the real arm's
state *does* hold the move where A3b's does not.

## What it licenses

* **For C5 and D1**: as dealt, C5's deck replaces the hand-written openings
  of two families rather than widening them. If both kinds of speech should
  carry `consolation` -- the short idiom and the long worry -- the deal is a
  mix to set (a cap on the SODA share per family), not a default to keep;
  `check_moveline.py` section 10 holds the deal as it is.
* **For finding 161's question**: real openings did not raise the state's
  ceiling on the hand-written far phrasings; the remaining read on the
  state's ceiling is size (the 260M pilot, D11).
* **For the instrument**: R_fixed held seed to seed again (47/48 on both
  arms) where the written label moved by family and seed. It is the read to
  keep.

## What it does not say

That real text is worse: on the registered test the hand-written idioms are
the yardstick, and this arm trained consolation on a different kind of
line. That the state is unchanged everywhere: R_fixed is read on far
phrasings in A3b's style, with a reader fit on A3b's lines. Anything at
260M. Two seeds, one floor seed, a linear reader -- every number a bound.

## Amended 2026-10-11: on real openings neither arm trained on (post hoc)

`scripts/probe_real_heldout.py` (card
`evals/results/move_inside_real__soda_heldout.json`; 168 s on the card,
contended at 61% -- a bound). 100 consolation and 100 share lines from
`soda_moves.txt` that neither payload holds (7,301 and 21,565 never dealt),
drawn by `random.Random(0)`; his tag over the eight moves, and the fixed
reader at the place the registered read chose. Written in the script before
it ran: the real arm at 60+ of 100 on each, A3b at 40 or under, and the fixed
reader reading the two arms about the same.

    of 100 unseen real openings      he writes              his state (R_fixed)    word counter fit on
                                     consolation  share     consolation  share     the arm's own slice
    A3b   1337                       56           87        36           99        80 / 57
    A3b   2337                       25           39        34           91
    real  1337                       89           99        82           94        99 / 99
    real  2337                       95           98        85           96

**The real arm reaches real openings and its state holds them**: it writes
consolation on 89 and 95 of 100 unseen real worries and share on 99 and 98
of 100 unseen real news, and the reader fit on A3b's hand-written lines finds
consolation in its state on 82 and 85 -- against 36 and 34 in A3b's. So on
real text the state moved, by about fifty items, where on the hand-written
idioms it did not move at all. Of the predictions written first: the real
arm's half held; A3b at 40 or under held at seed 2337 and not at 1337 (56,
87: A3b writes `open` on most of what it misses at 2337 -- its default); the
reader reading the two arms alike was wrong on consolation and right on
share.

**And it is word evidence, reached.** These openings carry their move in
stock words -- the commonest openings of the 100 consolation lines are "i'm
really" (18), "i'm feeling" (10), "i'm so" (9), "i'm worried" (5) -- and the
labeller that wrote their gold keys on such words. A word counter fit on the
real slice reads 99 of 100 on both families; the net reaches 89-99. Fit on
A3b's slice, the word counter reads consolation 80 and A3b writes 56 and 25:
the evidence was in A3b's slice too and A3b's net used less of it -- finding
161's readout layer again.

**Read with the registered result**: each arm reaches what its training text
looks like, at about the word counter's level, and neither crosses far to the
other's kind of line -- the real arm loses the short idioms, A3b the long
worries. That is finding 161's ceiling located once more: the state holds
what the words of the training text carry, and "far" is far *from that
text*. **For C5 and D1** this sharpens the licence above: the real openings
are what reaches the openings a person actually writes (89-99 against 25-87),
and the replacement costs the idioms -- the deal wants both, which is a mix
to set before F1.
