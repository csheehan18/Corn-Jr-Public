# Seventy-first finding — finishing the chain converts silence into recitation, and the hard zero that held at every size goes to 26 of 26

**Cost:** 8.5 min of scoring on the 2 cards first cited here (`nano20m_v1_daylog`, `nano20m_v1_daylog_seed2`); it also reads 1 card scored for an earlier finding (`nano20m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`nano20m_v1_daylog` and `nano20m_v1_daylog_seed2`, 2026-08-26. R5 of
`docs/PLAN-P3-RULERS.md` — the one training run in that plan, pre-registered in
`configs/mix_v1_daylog.py` on 2026-08-18 and never run until now. Two nano
seeds, one source path changed, every weight identical, scored against the
frozen `evals/` set. The control is `nano20m_v1` at four seeds.

## What the arm changes, and it is one line

    temporal   data/raw/temporal.txt  ->  data/raw/temporal_daylog.txt

The corpus contains **90,293 `recall_day` calls and zero observations for any
of them** — 55% of the largest generated slice stops mid-chain, and no other
slice carries one either. So the only thing the corpus had ever taught about
the day log was how to *ask* for it, and `temporal.route` at 398/400 was
scoring exactly that. `--daylog` finishes the chain: the tool answers and the
model says the answer back.

## The hard zero

    row              260M (finding 51)   control, 4 seeds        arm, 2 seeds
    daylog.open           4/90            0, 9, 3, 0 / 90         25, 16 / 90
    daylog.targeted       4/84            0, 7, 0, 0 / 84         12,  7 / 84
    daylog.empty          0/26            0, 0, 0, 0 / 26        **26, 26 / 26**

**`daylog.empty` has been 0/26 on every scorecard this project has ever
written** — 58 cards on disk carry the row, across nano and 260M, treated and
untreated, and not one of them passed a single item. Both arm seeds score
**26 of 26**. Finding 51's sentence was "`daylog.empty` is a hard zero at every
size this project has trained"; it was a corpus absence, and one file closes it
completely.

`daylog.open` clears the control's four-seed range on both seeds (arm 16-25
against control 0-9). `daylog.targeted` does **not**: the arm's weaker seed
reads 7/84 and the control's best seed also reads 7/84, so on the row that
requires picking the *right* entry out of several, this arm is inside its own
floor and cannot be said to have moved it.

## The failure changed species, exactly as the config predicted

    checkpoint                daylog.open failure vocabulary
    260M (finding 51)         no_say 63, confabulated 23
    control seed 1            empty 90
    control seed 2            confabulated 81
    arm seed 1                trained_topic 48, confabulated 17
    arm seed 2                trained_topic 67, confabulated 7

**Silence is gone.** The untreated failure was an empty continuation — he emits
the call, receives the observation, and says nothing — and there is not one
such item on either arm seed. What replaced it is `trained_topic`: a
well-formed read-back carrying a topic from the **training** pool instead of
the one in the payload.

    got   "You got me to set a reminder to pay the gas bill, mid-morning."
    want  "That was the day you got me to set up the push develop."

That is the limit `configs/mix_v1_daylog.py` pre-registered before the run, in
those words: the slice carries 67 distinct topics over 132,628 entry uses —
1,980 uses each — and DATA.md §11 puts the failing regime at 2,096 uses per
carrier. The prediction was that this corpus would teach the *shape* of a reply
and not the reading of a topic out of a payload, that `trained_topic` would
dominate if so, and that **the fix is composing the topic space rather than
abandoning the slice**. All three hold. Confabulation — inventing a topic in
neither pool — falls to 17 and 7.

So the arm bought the half nothing taught (that a `<|say|>` follows a log at
all, and that an empty day is said to be empty) and did not buy the half its
own topic cardinality made unlearnable. Both halves were named in advance.

## Everything pre-registered as holding, holds

    row                control, 4 seeds        arm, 2 seeds     pre-registered
    temporal.route     398, 398, 398, 400      397, 397         hold, floor 3
    temporal.copy      353/353 x4              353, 353         hold, floor 1
    schema.conform     189-193 / 200           193, 193         hold
    tool.selection     112-156 / 200           156, 164         hold
    tool.validity      157-175 / 181           169, 167         hold
    register.conv      78-81 / 200             86, 86           hold

**`temporal.route` holding is the informative one.** The swap costs a **46% cut
in routing examples at equal tokens** (the answered chain is longer: 91,613
transcripts against 164,263), and the config registered that as a confound in
advance — a fall would not have been attributable to the day log. It did not
fall. 397/400 on both seeds says routing is bought well below 121,318 examples,
which is a supply fact worth more than the row it came from.

One row sits outside its control range on one seed: `tool.copy` reads 92 and
100 of 120 against a control of 100, 100, 120, 114. The arm's second seed
lands on the control's own minimum, and nothing in this swap touches the tool
slice, so the honest reading is that four control seeds spanning 20 items is
too wide a floor to call an 8-item difference with — the nineteenth and
forty-third findings' lesson, arriving on a new row.

**`lm.temporal` is not comparable here and must not be quoted as a regression.**
It reads 0.0940-0.0973 on the control and 0.1267-0.1342 on the arm, because the
arm is scored against a *different temporal text* — the answered chains are the
file. A source swap moves its own `lm` row by construction.

## What it settles for the freeze

`docs/PLAN-5B-SUPPLY.md` §7 listed daylog completion as the cheapest open
question before `mix_v4_5b`, and it is now read rather than open: **the line
delivers a real behaviour at the share it already has**, with the residue
named and cheap (compose the topic space, `corn/daylog.py`'s only structural
change, no new markers). What it does not settle is whether one file can carry
both the sayvar and daylog repairs — they are one generator with two flags and
that combination is still unmeasured — nor whether the line is worth its share,
which was never this arm's question.

## Limits

Two seeds against a four-seed control, at nano. The 260M numbers in the first
table are finding 51's and are **not** a treated/untreated pair with this arm —
they are the untreated baseline at a different size. `daylog.targeted` is
inside its floor and is reported as such. And the arm's own topic pool is the
thing its dominant failure is made of, so the next reading of these rows should
come from a composed-topic slice rather than from another seed of this one.
