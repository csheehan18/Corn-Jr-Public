# One hundred and seventieth finding — the copy band's standing kill measured seed noise: seeds of one arm on identical data spread 0 to 54 items of 300 on `tool.copy_wide` (median 8, 90th percentile 20), the kill's band was a binomial 3 to 4, and the two kills it reported on the ladder (findings 168 and 169) are not readable

**Cost:** 2.3 min of `tool_copy_wide` cards on the 16 family checkpoints that had none (8-9 s each, contended -- the card at 38%, a bound), on 2026-10-14 between 09:23 and 09:27; the tabulation, the guard and the filing on CPU, to 09:29.

**Why it was read.** After finding 169 the owner proposed that the 20M shape
is what is costing the copying -- that each ladder payload fires the copy kill
because the small model has no room for it. Before pricing a larger model for
that, the question is whether there is a cost to explain. The kill (EXPERIMENTS
§5.7) compares an arm's `tool.copy_wide` with its control's at the same seed,
with `probe_move.half_width` as the band: 2.8 items at 298 of 300, 4.3 at 295.
That band is the sampling error of one checkpoint's 300 items. It is not the
error that matters, which is how far a second training of the same arm lands.

**The read** (`scripts/copy_floor.py`, every `nano20m_v3_fw*` checkpoint, 47
of them, block 1024, RoPE, the funcworld family the ladder trains in; 16 cards
scored here, the rest on disk):

    arm                          seeds (copy_wide of 300)   spread
    filter_ev2 (the control)     298 295 293                  5
    filter_view                  284 298 278                 20
    templates_id                 242 296                     54
    recover_named                265 290                     25
    branch                       292 282                     10
    recover                      298 287                     11
    filter_ev                    295 283                     12
    combine4                     296 285                     11
    filter4                      298 287                     11
    armf                         280 288                      8
    ... 10 more arms              spreads 0-8

    within-arm spreads, 20 arms: 0 1 1 1 2 4 5 6 7 8 8 8 10 11 11 11 12 20 25 54
    median 8; 90th percentile 20; every checkpoint 242-300, median 291

**Seeds of one arm, on the same bytes, differ by as much as the kill's
"falls" by the median arm, and by five to fifteen times its band in the
tail.** Arm V (`filter_view`), one payload at three seeds, reads 284, 298
and 278: under the old rule its seed 3337 would have killed its seed 2337.
And a seed number does not pair two arms: a different mix is a different data
order, so "below the control at the same seed" compares two independent draws.

**What it does to the record.** EXPERIMENTS §5.2 already says a separation
smaller than the seed spread is not readable; §5.7's band broke that rule for
one row. Read by the spread:

    arm               arm seeds    control (E2) seeds    old rule      by the spread
    recover (167)     298 287      298 295 293           holds         not readable
    recover_named     265 290      298 295 293           fires (168)   not readable
    branch            292 282      298 295 293           fires (169)   not readable

**The "the copy kill fires at both seeds" in findings 168 and 169 is not
readable, and neither is a payload cost on the copy band.** The ladder payloads
sit inside the family's own spread (the branch arm's mean 287 against E2's 295,
a gap smaller than recover's two seeds, 298 and 287). The digit-shift misses
read by hand in both findings are real outputs, and both seeds of the named
arm and of branch-2337 showing one species is worth keeping in mind. But a
species in 9 to 26 misses is not a cost the row can see against this noise.

**For the owner's hypothesis**: the copying is not shown to be costing
anything at 20M on this ladder, so it is not evidence about scale either way.
The seed fragility of the picks is a separate question: findings 168 and 169
each split, and one seed installed outright.

## The rule now

EXPERIMENTS §5.7, amended 2026-10-14: the kill reads only when **every seed of
the arm sits below the control's lowest seed by more than 20 items** -- the
90th percentile of the within-arm spread -- and otherwise reads "not readable".
`scripts/copy_floor.py` holds `SPREAD` and `verdict`;
`scripts/check_copy_floor.py` re-derives the percentile from the cards on disk
(a new card that moves it fails the sweep until the constant, §5.7 and this
finding move with it), shows that no 3-seed arm split against itself falls,
and that a real fall still fires. The rule is coarse on purpose: at two seeds a side,
anything finer would be estimating a tail from twenty arms.

**What it does not settle.** Why the spread is this wide -- one garbled answer
on the 232-answer row is a few items, and templates_id's 242 is many --
and whether `tool.selection` and the other standing rows read through
`half_width` have the same problem. They were not tabulated here and are
the next instrument to check.
