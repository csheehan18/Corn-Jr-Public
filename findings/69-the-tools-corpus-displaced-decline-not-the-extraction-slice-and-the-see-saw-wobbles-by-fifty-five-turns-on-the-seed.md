# The tools data, not extraction data, displaced his declining

**Full result:** The tools corpus displaced decline, not the extraction slice, and the see-saw wobbles by fifty-five turns on the seed

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn_jr_260m_ft{wide,narrow}` and both their seed-2 twins, 2026-08-26,
measured by `harness/toolgrid.py` under the conditions of the two runs it is
read against: 808 turns each, greedy, table-backed (`search: table`, nothing
leaves the machine), scratch `--notes`, eight tools declared with `decline`
offered, `hatched: 0` on every cell. Declared as a new cell of
`docs/PLAN-P3-RULERS.md` before it was run, not slipped into R1. No training.

## The question it was built to settle

The sixty-seventh finding measured a see-saw: the base declines 201/208 and
serves 118/600; `ftextract` serves 386/600 and declines 88/208. It named two
candidate causes for the decline collapse and could not separate them, because
one checkpoint carried both — `ftextract`'s corpus is the **p3b2 tools payload**
*and* an **extraction slice**, and the tools payload is the first corpus in this
project to carry `ask_agent` transcripts at all.

`ftwide` and `ftnarrow` are the control that separates them: same frozen base,
same p3b2 tools payload, **no extraction**. If their Grid A collapses too, the
tools corpus is the cause. If it holds, the extraction slice is.

## It collapses. Every arm that saw the tools payload declines like `ftextract`

    checkpoint             decline (A)   contacts (B)   notes (C)
    corn_jr_260m            201/208        96/424         22/176
    ftextract                88/208       306/424         80/176
    ftwide                   88/208       245/424        117/176
    ftnarrow                 57/208       283/424        123/176
    ftwide_seed2            114/208       282/424        101/176
    ftnarrow_seed2          112/208       274/424        110/176

**`ftwide` reads 88/208 — the same number as `ftextract`, to the turn — with no
extraction transcript anywhere in its corpus.** The extraction slice is
acquitted: it is the tools payload that moved the prior, and the sixty-seventh
finding's mechanism paragraph was right about the sink existing and wrong about
which corpus opened it.

The misses say the same thing from the other side:

    checkpoint       where the 120-151 decline misses went
    base             (nothing) 6, place_call 1
    ftextract        web_search 49, ask_agent 41, save_note 29
    ftwide           ask_agent 68, save_note 50
    ftnarrow         ask_agent 89, save_note 61
    ftwide_seed2     ask_agent 61, save_note 27
    ftnarrow_seed2   ask_agent 66, save_note 25

`ask_agent` absorbs the mass on **all four** p3b2 arms, and the `web_search`
sink is `ftextract`'s alone — 49 turns against 0 and 1 elsewhere. So the
displacement has two separable parts: **the tools payload opens `ask_agent` and
everything that is not a served request falls into it**, and *on top of that*
the extraction fine-tune adds a `web_search` pull that no other arm has. "The
fine-tune moved the prior, not the judgement" survives; "its misses land on the
two tools its corpus is about" was reading one arm's signature as the family's.

## The seed spread on the see-saw, which is the read finding 67 called missing

    grid          ftwide → seed2    ftnarrow → seed2
    A decline     88 → 114  (+26)    57 → 112  (+55)
    B contacts   245 → 282  (+37)   283 → 274   (-9)
    C notes      117 → 101  (-16)   123 → 110  (-13)

**The gap between the two arms on Grid A is 31 turns and the seed moves the
narrow arm by 55.** So the wide/narrow difference on decline is wobble, and any
future arm read on this grid needs both seeds or it is reading the seed. Note
what this does *not* touch: the sixty-eighth finding scored the same four
checkpoints on the frozen rows the same day and found **zero** movement on
every ceiling row and at most 8 items of 120 anywhere. Same weights, same
afternoon: the frozen set is seed-stable to the item and the live grid is not.
An instrument's spread is a property of the instrument, not of the checkpoint,
and quoting one set's error bar on the other's numbers would understate it by
an order of magnitude.

## What reproduces across all six checkpoints, and is therefore not one arm's quirk

**Content halves note routing, on every checkpoint that serves notes.**

    content class      base   ftextract   ftwide   ftnarrow   w-seed2   n-seed2
    plain              5/44     37/44      43/44     43/44      41/44     42/44
    date_bearing       4/44     16/44      24/44     24/44      21/44     21/44
    question_shaped    5/44     11/44      30/44     34/44      24/44     31/44
    real_entity        8/44     16/44      20/44     22/44      15/44     16/44

The carrier is identical across the four cells and the content moves routing by
19 to 27 points on every arm. The live audit's single anecdote ("note down
dentist appointment moved to friday") is now a five-checkpoint effect, and the
cheap generator change — dates and entities *inside* note text — is licensed by
more than one column.

**The messageless text family lands on `ask_agent` everywhere.**

    base 0/24 (declines all 24)   ftextract 4/24   ftwide 3/24
    ftnarrow 7/24                 w-seed2 5/24     n-seed2 6/24

with 16-20 of each fine-tune's misses on `ask_agent`. "send a text **to** {c}"
reads as relay on every checkpoint that has an `ask_agent` to read it as, which
makes the carrier-overlap line a corpus item rather than a hypothesis.

**`send_text` is the weak tool and `place_call` is not.** `place_call` runs
187-201 of 224 on every fine-tune while `send_text` runs 58-109 of 200. The
slots underneath are healthy — `kept_contact` after `shed_overrun` is 58/58,
81/84, 79/81, 74/74 on the four p3b2 arms — so what is missing is routing, not
copying. The shed's own contribution is checkpoint-specific and worth one line:
it recovers **12 texts on `ftextract`** (71/109 raw → 83/109) and 1-4 on the
others, because the arms that route fewer texts also overrun fewer contacts.

## What it licenses

The Phase 3 balance variable named by finding 67 stands, and this finding aims
it: the corpus that has to be trained against declines is the **tools payload**,
`ask_agent` included, and it must be graded on both columns of the see-saw with
**two seeds a side**, because one seed cannot tell a 31-turn arm difference from
a 55-turn seed difference. It licenses nothing about `ask_agent`'s share — that
is the freeze decision `PLAN-5B-SUPPLY.md` §7 leaves with the owner, and this
grid is a ruler for it rather than an argument about it.

## Limits

Two seeds a side on the fine-tunes and one on the base, which has no seed-2
twin to be read against. Authored fills, not user traffic. Greedy only. The
`smart_home` cell of Grid A has no trained frame — the decline slice has no such
domain — so it is novel-only on every checkpoint and its four columns are not a
trained/novel contrast. And the base is the only checkpoint here without
`ask_agent` in its corpus, so "the tools payload opens the sink" is measured
against arms that all have it: what is not measured is a tools corpus **without**
`ask_agent`, which is the arm that would price the escalation line on its own.
