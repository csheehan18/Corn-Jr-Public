# Sixty-third finding — the phrasings were never the problem, and the arm without them fixed all twenty-five

**Cost:** 12.5 min of scoring on the 1 card first cited here (`corn_jr_260m_ftwide_seed2`); it also reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

P3-B2, run 2026-08-26 on `corn_jr_260m`. Two fine-tunes from the identical
frozen base, 786 iterations each, ~15 minutes a run.
`configs/mix_p3b2_ft_wide.py` carries the pre-registration. **It lands on
outcome 2 of its own table, and outcome 2 was the one the control existed to
make sayable.**

## The question, and why the pair was built

The fifty-second finding measured a phrasing defect on this checkpoint: the
corpus offers 25 search phrasings and the weights keep about four. `google {q}`
routed 8/8; `see if you can find {q}` routed 0/8. The reading that followed --
in that finding, in DATA.md and in `PLAN-PHASE-3.md`'s whole P3-B section --
was **supply**: the corpus needs more distinct sentences, and the open question
is where another 60 MB of them come from.

P3-B1 tested that at nano and could not read its own instrument (sixty-first
finding). So it moved here, where the defect was measured and is large.

**A fine-tune on fresh tool transcripts changes two things at once** -- the
model sees more tool data, and it sees whatever carriers that data uses. So
both arms fine-tune on the *same* 30 MB payload, and the wide arm's copy is the
narrow one after `gen_tools_p3b1.py` swaps only the carrier line: 85 phrasings
instead of 25, 31,350 transcripts differing, every other byte identical.
`check_p3b2.py` reads that off the bytes.

## The defect is real, it reproduces, and both arms remove it

`harness/searchgrid.py`, 400 turns per checkpoint, `decline` offered, nothing
leaving the machine.

    routed          invented      real     kept_subject
    base             94/200     72/200        166/400
    FT-narrow       200/200    198/200        398/400
    FT-wide         194/200    192/200        386/400

The base reproduces the fifty-second finding (that run read 87/200 and 53/200
on a different subject draw). **Real-world subjects go from 72/200 to 198/200**
-- the column every question a user actually asks lands in, and the one that
finding called the one nothing had measured.

Per template, which is where the original claim lived:

    template                    base   narrow     wide
    have a look for {q}         0/16    16/16    16/16
    see if you can find {q}     0/16    14/16     7/16
    any idea what {q} is        1/16    16/16    16/16
    quick, {q}                  1/16    16/16    16/16
    look {q} up for me          2/16    16/16    12/16
    ...
    could you look up {q}      14/16    16/16    16/16
    google {q}                 15/16    16/16    16/16

                     never-route   at-ceiling   of 25
    base                       2            0
    FT-narrow                  0           24
    FT-wide                    0           22

## The result: the extra sentences bought nothing, and the control is the only reason that is sayable

**The narrow arm carries not one new phrasing and brings 24 of 25 templates to
ceiling**, including the two the base never routed at all. The wide arm, with
60 hand-written phrasings added, reaches 22.

On the frozen eval rows the two arms are indistinguishable:

    row                     base    narrow      wide    wide-narrow
    search.route_base    199/200   200/200   200/200         +0
    search.route_wide    192/200   199/200   200/200         +1
    search.route_heldout 187/200   200/200   200/200         +0
    tool.validity        170/181   181/181   181/181         +0
    tool.selection       171/200   187/200   188/200         +1

`search.route_heldout` is the sharpest of these. Its fifteen carriers are held
out of **both** payloads and trained nowhere, ever -- and the narrow arm takes
them 187 -> 200. A model given no new sentences became perfect on sentences it
has never seen.

**So phrasing generalisation was never supply-limited.** What the model needed
was more, fresher tool-calling exposure. The fifty-second finding's own closing
sentence -- "the corpus does not need more search transcripts, it needs the
ones it has to stop being concentrated in four phrasings" -- has the diagnosis
backwards: more search transcripts is exactly what it needed, and the
concentration resolved itself.

**Had only the wide arm been run, this would have been written up as a clean
win for the 60 templates.** That is what the pair was for, and it is the second
time in two days a single-arm reading would have been wrong -- the sixty-first
finding's `route_wide` 4-of-4 sign was the first.

**Do not read the wide arm as a cost.** It is 22 of 25 against 24, and
`see if you can find {q}` reads 7/16 against 14/16, at one seed with no floor
measured. The honest claim is that the widened pool is **not better**, not that
it is worse.

## What was measured on the other side, because a fix like this is usually a trade

The base declined 232 of its 400 misses. The arms decline almost never, which
is exactly the shape of the forty-second finding's over-declining being
converted into wrong tools rather than right ones. It was not:

    row                     base    narrow      wide
    chat.abstain_oos      33/100    38/100    47/100
    chat.abstain_talk    100/100   100/100   100/100
    chat.abstain_greet    67/100    77/100    81/100
    refusal.no_guess       47/47     47/47     47/47
    refusal.clarify        47/47     47/47     47/47
    refusal.say          270/270   270/270   270/270

Every dedicated abstention row held or improved. `tool.selection`'s base
failure mass included `declined: 9` -- refusing items that wanted a call -- and
that class is **gone** in both arms. The one movement the other way is
`called_anyway`, 8 -> 13 and 11, so a few items now get a call that should not:
small, real, and worth watching rather than dismissing.

**Rule 10's watch is clean at the ceiling**, which is the strongest form this
project can run it. `tool.copy` 120/120, `tool.copy_wide` 300/300,
`temporal.copy` 353/353, `temporal.route` 400/400 -- unchanged on both arms.
The sixtieth finding licensed a fine-tune adding register over an installed
capability; this extends that licence to adding *exposure*, at 260M, where
nothing had tested it.

## What this cannot say

**One seed.** The scored comparison is seed 1337. `corn_jr_260m_ftwide_seed2`
and `_ftnarrow_seed2` are trained and unscored. Nobody has ever measured seed
variance at 260M, so no spread here has a floor under it -- the sixty-first
finding's whole subject. The routing effect is 126 items of 200 and is not
plausibly noise; the **wide-versus-narrow** difference is a handful of items
and is not readable at all.

**One grid per checkpoint.** `searchgrid` has no measured floor at this size
either (the sixtieth finding established it has none at nano). Same argument:
the base-to-arm gap dwarfs anything a floor could be, the arm-to-arm gap does
not.

**The eval rows were at the ceiling before the experiment started.** The base
reads 93.5% on `search.route_heldout`, because those prompts are cut at
`<|call|>` and ask *which* tool given that one is being called.
`configs/mix_p3b2_ft_wide.py` registered that limitation before anything ran,
and it turned out to be the whole story: **the defect is not in recognising a
lookup, it is in deciding to reach for a tool at all.** Given the call, the
base already picked `web_search` correctly for 93.5% of phrasings it had never
seen.

**And nothing here says a 5B pretraining mix would behave the same way.** This
is a fine-tune result. The sixtieth finding measured the fine-tune vehicle
delivering 61% of a mix's effect on a different payload; no such ratio is
established for exposure.

## What follows

**P3-B's supply premise is retired.** Options 2 and 3 of `PLAN-PHASE-3.md`
§P3-B -- mine a corpus for utterances, have a larger model paraphrase -- were
both answers to "where do more sentences come from", and that is no longer the
question. **P3-B3 should not run.** The 60 templates cost a morning, are on
disk, and are not worth a corpus decision either way.

The live question this opens is narrower and better: **what does "fresher tool
exposure" mean, and how much is needed?** The payload here is 30 MB of newly
generated transcripts at ~1 pass against a base that read `tools_names.txt` at
~35 passes in `mix_v3_5b`. Repetition is the obvious suspect -- arm 2's own
measurement and the fifteenth finding both price it -- and this experiment
cannot separate "new data" from "less-repeated data", because it changed both.
