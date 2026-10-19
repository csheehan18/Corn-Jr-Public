# He can't learn which limit a person will relax

**Full result:** G6's recover rung does not install at one pass: when nothing fits he relaxes a limit by a fixed ranking of the field names, a different ranking at each seed, and the limit the person said they would bend on never reaches the choice -- paired 3 and 0 of 288 held-out, 0 and 0 of 144 trained, and his state at the pick carries the clause no better than an untrained net's

**Cost:** 41.5 min of training two nano runs (1,244 s and 1,249 s, contended -- the card at 36-41%, a bound; registered ~40 min), 52 s of probing, four `tool_copy_wide` cards in 34 s, the three control reads 117 s and the three hand reads 52 s on the card; the build -- generator, guard, probe, rows, configs -- about 15 min of CPU (12:47-13:02 on 2026-10-13), the read 13:45-13:55; registered ~50 min of card, actual ~46.

ROADMAP G6, PLAN-TAG-LANGUAGE §6's ladder, its second rung ("recover when
nothing fits"), in the form SPEC-LANGUAGE §6 fixed (D-A1.8): when `check:`
marks every listed place unmet, the runtime writes `options: relax[a]
relax[b] ask` and his `pick:` is one move. Pre-registered in
`configs/mix_v3_funcworld_recover.py`'s docstring and committed at a092e65
before a byte trained. One variable from arm E2: 8,100 recover traces
(`corn/recovergen.py`) at combine's dose to the token, 2.21% of the mix,
5,843 iterations; seeds 1337 and 2337. On two traces in three the request
names one limit as flexible by meaning ("though the budget can stretch a
bit"), with nouns that share no stem with `price`, `km` or `rating`
(`scripts/check_recover.py`, which caught "budget" against a firm clause's
"budge" before anything trained); the gold is the first-named limit on 50.0%
of relax traces and the nearest-miss limit on 51.1%. **Cards:**
`evals/results/nano20m_v3_fw_recover{,_seed2}__recover.json` and
`__copywide.json`; the controls' `nano20m_v3_fw_filter_ev2{,_seed2,_seed3}__recover.json`
and `nano20m_v3_fw_filter_ev2{,_seed2}__copywide.json`.

## The registered read

    seed   right train / held-out   paired train / held-out   moved (twin)   ask rows right
    1337        69 / 152                   0 / 3                 0 / 3           0 of 96
    2337        66 / 112                   0 / 0                 3 / 6          18 of 96

Gates: paired held-out more than 42 of 288, paired train more than 23 of 144,
at both seeds. **Both fail at both seeds: the registered row "23 or fewer
both, 42 or fewer both -- nothing installs at one pass; recover at nano is not
his at this dose; the dose is the next variable, as combine's was."** The
prediction on the record -- paired held-out above 42 at both seeds -- was
wrong. Controls (arm E2, every seed): `ask` on every row, paired 0, the ask
rows 96 -- a checkpoint that never saw a menu finds the shortest line
likeliest. Not unreadable: no control reads paired above 0.

**The standing kill does not fire**: `tool.copy_wide` 298 of 300 against arm
E2's 298 at seed 1337, 287 against 295 at seed 2337 -- below by more than the
half-width (4.3) at one seed only.

## Read by hand (EXPERIMENTS §5.6) -- what the pick follows

A scratch read of every row on both seeds (probe only -- not on disk).

**A fixed ranking of the field names, different at each seed.** Seed 1337
relaxes `rating` over `km` over `price`, almost without exception:

    pair         seed 1337                          seed 2337
    km / price   relax[km] 148, relax[price] 6      relax[km] 84, relax[price] 60, ask 10
    km / rating  relax[rating] 133, relax[km] 3     relax[km] 65, relax[rating] 64, ask 7
    price/rating relax[rating] 142                  relax[price] 58, ask 71, relax[rating] 13

`right` near half on the relax rows is that ranking landing on the gold half
the time, and the twin -- the clause moved to the other limit, every other
byte the same -- moves the pick on 0-6 of 288 rows.

**The person's words do not move the choice at all.** Where the clause names
neither limit (the ask rows) and where it names one, the margin of `ask`
against his best relax is the same: +0.55 against +0.51 nats at seed 1337,
+0.20 against +0.19 at 2337. The gold relax is the likelier of the two on 221
and 230 of 432 relax rows. List length is not it either (seed 1337: 81 of 151
right at three places, 70 of 142 at four, 70 of 139 at five).

**Inside him, at the token where he names the field** (after `pick:
relax[`), a linear reader in finding 161's protocol -- fit on the trained rows
and their twins, the layer chosen on a fifth of them, read on the held-out
rows and twins (576):

    label                         seed 1337   seed 2337   arm E2 (control)   random-init floor
    which limit (first / second)    0.509       0.503        0.500              0.486
    which field (price/km/rating)   0.627       0.670        0.653              0.733

The relative label -- the one the choice needs, the noun's field placed
against the goal's order -- is at chance in every net. The absolute field is
readable well above chance (0.33), but **a randomly initialised net of his
shape reads it best**: that is the noun's identity mixed forward, which any
net carries and which a reader can map to a field because every noun appears
in its fit. His trained state carries it no better than an untrained one. So
the words reach the pick as words, at the floor's level, and training formed
no mapping from "the budget" to `price` and no use of one: **the evidence
never reaches the decision**, finding 161's first reading, not its second.

## Amended 2026-10-13: the raw rows, and his own training traces

**The raw rows** (the probe's printed rows, read after the numbers -- the
order CLAUDE.md says to avoid): on every printed row all three menu lines sit
at 0.6-1.7 nats, near a blind three-way guess (1.10), and the lowest is the
seed's favourite field whatever the clause says -- "I'm easy about the
budget" and "I'm easy about the trip there" both put `relax[km]` lowest at
seed 1337 (0.78, 0.63). He learned the menu's format and its one-in-three
prior, and almost nothing that depends on the request.

**His own training traces** (the owner asked for this before any further arm;
probe only -- not on disk): the same full-option scoring on 300 relax and 150
ask traces taken from the part of the payload file that trained, verbatim:

    seed   relax right   gold's NLL among the three   ask right
    1337   147 of 300    1.01 nats (blind 1.10)        0 of 150
    2337   126 of 300    1.50 nats                     51 of 150

Chance on what he trained on. Each trace trained once, so no trace was
expected to be memorised; but each noun x frame pairing trained about 200
times and each noun about 600, and the choice depends on none of them. **This
is not a transfer failure -- the request-dependent choice never formed, even
in distribution.** What is still open is why: too little gradient on a
decision of three tokens in a ~400-token trace (combine read the same at four
times the dose, which argues against dose alone), or the two hops -- the
clause's noun to a field, the field to a menu move -- across the observation
between them. An arm that names the field outright in the request ("I'm
flexible on price") splits the two.

## What it licenses

The table's row: **recover at nano is not his at one pass; the dose is the
next variable.** The same shape as combine (finding 156): a request-dependent
choice over a small menu of values he sees on every trace forms a fixed
ranking of the values instead, different at each seed, and combine read the
same at four times the dose. So the cheap next arm is recover at four times
the dose; the decision it would feed is D7's row for recover. The alternative
this finding makes available without training: **the flex reading is the
runtime's** -- the runtime holds a table of flex phrasings (as combine became
the runtime's, by lookup) and either picks the move itself or shows him the
menu already narrowed; what stays his is nothing on this rung.

**What it does not settle.** Nano, one pass, one world (two limits, three
fields). Whether a menu read at a later layer, a shorter distance between the
clause and the pick, or a format where the flexibility is written on the
`goal:` line (a term he writes while the request is in view, e.g.
`soft[...]`-style) would install -- none was tested. The 96 ask rows read 0
and 18: he did not learn to ask when the person bent on nothing, either.
