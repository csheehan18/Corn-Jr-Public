# Branch choice falls to chance when condition words flip the meaning

**Full result:** Branch rebuilt with flip words takes the table away and nothing forms in its place: at one pass and 2.2% of the mix the pick is at chance on the traces it trained on (202 of 400, a median margin of 0.01 nats), the result does not reach it, and what he writes is a fixed taste in place phrases ("a spot to eat" picked 89% of the times it is offered, "somewhere to eat" 26%)

**Cost:** 19.1 min of training one nano run (1,146 s, contended -- the card at 37-40%, a bound), two reads at 18-19 s, one copy card 9 s, the control read 15 s, the free-decode hand read 9 s and the own-trace reads ~20 s on the card; the build 13:26-13:34 on 2026-10-14, the chain 13:34-13:54, the read 13:54-13:57.

The branch rung rebuilt to [GENERATORS.md](../GENERATORS.md) after findings
169-172, at the owner's direction -- **the same words with a different
meaning**, so that memorising the wording cannot work -- pre-registered in
`configs/mix_v3_funcworld_branchflip.py`'s docstring at 6a9265e before a byte
trained. `corn/branchflipgen.py`: eight families in contrast pairs, where one
flip word moves the gold ("X if it's raining, otherwise Y" / "X if it's not
raining, otherwise Y" / "X unless it's raining, in which case Y" ...), filled
from word lists into **2,997 wordings, none seen more than 11 times** (finding
169's payload: eight wordings at ~928 each). `check_branch.py` section 8
re-derives every gold by rule from the words (0 wrong of 7,424) and holds
every single key at 50.2% or less on the gold's position. Twenty traces were
read by hand before training, every pick right. **One change from finding
169's arm: the requests**; the same world, menus and dose (7,424 traces,
2.2% of the mix, 5,844 iterations), arm E2 underneath. **One seed, by the
owner's call**: a corpus that teaches the rule installs it at any seed, so a
miss is the data's. **Cards:**
`evals/results/nano20m_v3_fw_branchflip__branchflip{,_items}.json*`,
`__branch{,_items}.json*`, `__copywide.json`; the control
`nano20m_v3_fw_filter_ev2__branchflip.json`.

## The registered read

    quads (all four right)        held-out first   held-out second   flip pairs   169 newframe
                                    (of 144)         (of 144)         (of 144)     (of 48 a side)
    arm E2 (control)                    0                0                0           0 / 0
    flip-word branch, seed 1337         3                0                1           0 / 0

    the pick follows the result (base vs result twin, of 288): 12 and 12 held-out,
    12 on the flip pairs -- the control reads 7-16

**The gate fails: the registered row "the data is still wrong".** The
prediction on the record (the gate passes, and finding 169's never-seen
wordings rise above chance) failed on every read.

## Read by hand -- the free decode first

`hand_flip.py` (scratch, probe only -- not on disk): he writes the pick line
himself, greedy, on every prompt of 40 sampled quads across the four cells,
each printed beside its request and result. 160 lines, 0 malformed, and right
on exactly half in every cell -- 20 of 40, 20 of 40, 21 of 40, 18 of 40. The
lines say why: **in most quads he writes the same continuation on all four
prompts** -- whatever the result, and wherever the phrase sits in the menu.
Row 126 writes "a spot for a pint" four times, 138 "a place for drinks", 130
"a room for the night". Over all 432 rows (the full-option card), **276 quads
name one place on all four prompts**, and the share of times each phrase is
picked when offered is a ranking:

    a spot to eat 0.89   a spot for a pint 0.81   a room for the night 0.54
    a place to sleep 0.45   a place for dinner 0.44   a place for drinks 0.43
    somewhere for lunch 0.41   somewhere for a drink 0.33   somewhere to stay 0.31
    somewhere to eat 0.26

**GENERATORS §5's signature: a fixed ranking, here over the continuation
phrases.** It is what is left when no decision formed. The phrase is drawn
independently of the gold, so it scores half and moves nothing.

## On its own training traces

The registered rows are held-out, so the question that settles the cause is
whether anything formed where it trained. Scored on 400 payload traces from
the front of the file (`own_traces.py`, scratch, probe only -- not on disk;
the validation split is the tail):

    run                                     right of 400   median margin (nats, wrong minus gold)
    flip-word branch, seed 1337                  202            +0.01
    finding 169's branch, seed 2337              367            +2.27      (installed)
    finding 169's branch, seed 1337              229            +0.16      (did not)

**Nothing formed, not even on the traces it trained on.** The rebuild did the
first half of its job: there was no table to fall back on, and none formed.
But at one pass and 2.2% of the mix the rule did not form either, and the
binding now asks for more than finding 169's did. Finding 169 needed the
result crossed with one of eight wordings. This needs the result crossed with
where the condition attaches and whether a flip word turns it over. The dose
that got finding 169's easier binding to form at one seed of four forms
nothing here.

**The copy row, a side column**: `tool.copy_wide` 297 of 300, inside the 20M
family's spread (finding 170).

## What it licenses

By the table, **the data is still wrong** -- and the own-trace read says
which way: **not memorisable (fixed), not learnable at this dose either.**
Two levers follow from GENERATORS, and the owner's reading ("it should install
regardless of luck") is the standard either has to meet:

* **Supply the hop in the bytes (D5).** Let him write the binding himself,
  next to the request where the flip words are: a line after the parse naming
  the continuation the condition selects. Then the pick is a short read of
  his own line and the result. Every rung that installed did so on a short,
  copyable hop (findings 147, 151, 168's named field).
* **More distinct evidence (D8, finding 159).** Fresh traces rather than
  passes -- several times the 7,424, each wording still near ten sightings --
  so the rule has the volume a harder conjunction needs.

The first changes the format and is a D7 question. The second changes only
the dose.

**What it does not settle.** Whether a second seed would differ -- by the
owner's standard it should not matter, and the own-trace read leaves nothing
for a seed to rescue. Also whether the flip families are equally hard, which
the per-family tally above (6-12 prompts a family) is too thin to say.
