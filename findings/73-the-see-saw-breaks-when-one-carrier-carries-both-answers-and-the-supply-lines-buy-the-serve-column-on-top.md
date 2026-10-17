# Seventy-third finding — the see-saw breaks when one carrier carries both answers, and the supply lines buy the serve column on top

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn_jr_260m_fte{1,2}` and both their seed-2 twins, 2026-08-27, trained from
the frozen `checkpoints/corn_jr_260m/ckpt.pt` on P3-E's balance payloads and
measured by `harness/toolgrid.py` under the conditions of every run it is read
against: 808 turns each, greedy, table-backed (`search: table`, nothing leaves
the machine), scratch `--notes`, eight tools declared with `decline` offered,
`hatched: 0` on every cell. Pre-registered in `docs/PLAN-PHASE-3.md` §P3-E
before the corpus was regenerated; built to `docs/PLAN-P3E-BUILD.md`. Controls
are the base and the four already-scored p3b2 arms — **nothing retrained**.

## The question, and why no checkpoint had answered it

Finding 67 measured a see-saw and finding 69 aimed it. The base declines
201/208 and serves 118/600; every arm that saw the p3b2 tools payload reverses
it, serving 362–406/600 and declining 57–114/208, and `ftwide` collapses to the
same 88/208 as `ftextract` with no extraction transcript anywhere in its
corpus. So the **tools payload** moved the routing prior, and no checkpoint on
disk decided between serving and declining. P3-E asked whether a corpus in
which the two are trained **against each other** installs the judgement.

## The treatment, in one sentence and one property

A new generator class draws **one carrier and renders it twice** — around a
request no tool covers, and around a request a tool serves — and
`scripts/gen_tools.py` writes the pair atomically. So over the matched subset
the carrier distribution of decline-shaped and serve-shaped transcripts is
identical *by construction*: 27,121 each over 30 carriers in E1, 27,169 in E2,
read off the bytes by `scripts/check_p3e.py` as two equal `Counter`s. The only
thing left that can predict the label is the request.

E1 is balance alone. E2 is E1 plus the three lines finding 67 licensed: dates
and entities inside note text, the messageless text family, wider contact
carriers.

## It breaks. One checkpoint now does both, on four seeds out of four

    checkpoint             decline (A)   contacts (B)   notes (C)   serve (B+C)
    corn_jr_260m            201/208         96/424       22/176       118/600
    ftextract                88/208        306/424       80/176       386/600
    ftwide                   88/208        245/424      117/176       362/600
    ftnarrow                 57/208        283/424      123/176       406/600
    ftwide_seed2            114/208        282/424      101/176       383/600
    ftnarrow_seed2          112/208        274/424      110/176       384/600
    fte1                    200/208        227/424      135/176       362/600
    fte1_seed2              206/208        244/424      118/176       362/600
    fte2                    191/208        261/424      150/176       411/600
    fte2_seed2              206/208        279/424      144/176       423/600

**Every P3-E arm holds the base's decline column while serving three to four
times what the base serves.** The decline gap to the p3b2 arms is 77 to 149
turns of 208, against the 26- and 55-turn seed spread finding 69 measured on
exactly this column — the first cell in this project's history to clear that
spread on the decline axis. The base's own 201 is *inside* it, which is the
correct reading: P3-E is at the base's decline level, not above it, and that is
the whole point, because the base pays 482 serve-cases for its 201.

The seed spread inside the arms is much tighter than the p3b2 arms':

    grid          fte1 -> seed2      fte2 -> seed2      p3b2 arms (finding 69)
    A decline     200 -> 206  (+6)   191 -> 206  (+15)   +26 and +55
    B contacts    227 -> 244  (+17)  261 -> 279  (+18)   +37 and -9
    C notes       135 -> 118  (-17)  150 -> 144   (-6)   -16 and -13
    serve         362 -> 362   (0)   411 -> 423  (+12)

## Against the pre-registration, stated exactly rather than rounded up

The registered cell reads: *discrimination installs — grid A trained AND grids
B+C routed both clear the see-saw's best ends simultaneously, beyond the
55-turn seed spread*. What happened:

  * **Decline: clears.** 191–206 against the p3b2 arms' 57–114 is 77–149 turns,
    beyond the spread on both seeds of both arms.
  * **Serve: matches, does not clear.** E2 reads 411 and 423 against
    `ftnarrow`'s 406. Finding 69 puts the seed spread on B at 37 turns and on C
    at 16, so a 5- to 17-turn gap on the serve column is not a separation and
    must not be quoted as one. E1's 362 is below the best end outright.

So the honest statement is **the see-saw is broken rather than beaten**: no
checkpoint before this reached both ends at once, and none of these clears the
serve end. *"Discrimination installs"* is met on the column that had never
moved and matched on the column that had.

**The honest null is refuted.** It read: *E2 separates from E1 on grids B/C but
neither moves grid A*. Both arms move grid A enormously and E2 does separate
from E1 on serve — 411/423 against 362/362, a gap of 49–61 turns against
within-arm spreads of 0 and 12. So the supply lines are real **and** balance was
the lever, which is the one combination the pre-registration did not enumerate.

## What the supply lines bought, and what they did not

**Dates and entities inside note text worked, and it is the cleanest cell in
the arm.** Grid C holds the carrier identical and crosses the content four ways;
finding 69 reproduced the collapse on five checkpoints.

    content class    base  ftwide  ftnarrow  fte1  fte1_s2  fte2  fte2_s2
    plain             5/44   43/44    43/44  42/44   40/44  42/44   41/44
    date_bearing      4/44   24/44    24/44  25/44   22/44  31/44   30/44
    question_shaped   5/44   30/44    34/44  31/44   22/44  37/44   31/44
    real_entity       8/44   20/44    22/44  37/44   34/44  40/44   42/44

`date_bearing` moves 21–24 → **31 and 30** and `real_entity` 15–22 → **40 and
42**, on both E2 seeds, while `plain` does not move — which is what a supply line
looks like when it is the content and not the carrier that was short.
`real_entity` is the odd one: E1 already reads 34–37 without a single new note
body, so most of that cell is balance and only the last few turns are supply.

**Wider contact carriers bought back part of what balance cost.** `send_text`
runs 39 and 47 of 200 on E1 against 59 and 62 on E2 — recovered, but still
short of `ftextract`'s 109. `place_call` is unbothered throughout (188, 197,
202 and 217 of 224 across the four P3-E seeds).

**The messageless family is the line that does not read, and the reason was
registered before the run.** `send_text` declares `message` required, so a text
request naming no message has no well-formed call and E2 teaches it as a
question. Grid B scores the family `expect="send_text"` and therefore counts
every correct clarification as a miss; the readable row is where the misses go,
and it does not separate:

    where the 24 messageless turns landed
    base            decline 24
    ftwide          ask_agent 20, send_text 3, place_call 1
    ftnarrow        ask_agent 16, send_text 7, place_call 1
    fte1            ask_agent  8, decline 12, send_text 4
    fte1_seed2      ask_agent 14, decline  6, send_text 3
    fte2            ask_agent 10, decline  8, send_text 3, (no call) 3
    fte2_seed2      ask_agent  6, decline  6, send_text 3, (no call) 3, place_call 6

The `ask_agent` sink shrinks from 16–20 to 6–14 — but **E1 does that with no
messageless transcript in its corpus at all**, and E2's 6 and 10 sit at or
inside E1's own 8 and 14 on a 24-turn cell. So balance shrank the relay sink and
the dedicated supply line cannot be credited for it on this evidence. What E2
does add is three turns of the taught shape appearing verbatim — `(no call)`
with a question, on both its seeds — which is the behaviour being asked for
arriving in a column that scores it as a miss.

## The bill, and there isn't one

Rule 10's regression set, plus the invariants, on all four checkpoints:

    row                   base  ftwide  ftnarrow   fte1  fte1_s2   fte2  fte2_s2
    tool.copy          120/120 120/120  120/120  120/120 120/120 120/120 120/120
    tool.copy_wide     300/300 300/300  300/300  300/300 300/300 300/300 300/300
    temporal.copy      353/353 353/353  353/353  353/353 353/353 353/353 353/353
    temporal.route     400/400 400/400  400/400  400/400 400/400 400/400 400/400
    refusal.say        270/270 270/270  270/270  270/270 270/270 270/270 270/270
    refusal.clarify      47/47   47/47    47/47    47/47   47/47   47/47   47/47
    tool.selection     171/200 188/200  187/200  200/200 200/200 200/200 200/200
    tool.validity      170/181 181/181  181/181  181/181 181/181 181/181 181/181

Not one item moves on any copy or deference row, on any seed. Finding 49's
precedent — an arm that buys its target and pays in deference — does not
reproduce here. `tool.selection` goes the other way and **reaches 200/200 on
all four P3-E checkpoints**, where the base reads 171 and the p3b2 arms 187–188:
the frozen row that asks "pick the right tool, or none at all" is the frozen
set's own miniature of the live grid, and it saturates.

`harness/searchgrid.py`, characterisation only and unregistered (finding 60):
the base routes 140/400 and P3-E routes 335, 360, 368 and 379, with
`kept_subject` equal to the routed count on every arm — the search column is not
spent either.

## Where the cost actually is, because there is one

The decline call now absorbs turns it should serve. Grid B's misses:

    fte1        ask_agent  96, decline 85, save_note 13
    fte1_seed2  ask_agent 110, decline 62, save_note  6
    fte2        ask_agent  98, decline 54, save_note  8
    fte2_seed2  ask_agent  75, decline 48, save_note  5, place_call 12

62 and 85 contact requests on E1 are declined outright, falling to 54 and 48 on
E2. That is the shape of the trade this arm makes and it is why the serve
column matches rather than clears: **the model has learned to decline, and it
over-applies it to `send_text`.** Nothing else in the grid shows it —
`place_call` runs 188 to 217 of 224, and grid C's decline misses fall from 35
and 51 on E1 to 16 and 29 on E2.

## What this licenses, and what it does not

The Phase 3 balance variable is answered: **judgement is installable by
fine-tune at 260M, from a corpus where the request is the only thing that
predicts the label.** VISION §8's "this phase is what makes him useful" survives
one more test than the sixth finding left it.

What it does not license is a share claim. The registered share is 27% declared
and 26.0%/25.5% delivered, and this arm has one dose. Whether the `send_text`
over-decline is a dose effect is the share arm the pre-registration names, and
it now has a reason to exist that is a measurement rather than a hunch.

## Limits

**The supply is nearly spent and the count says so.** The decline space is 30
carriers x 210 authored requests x 6 refusal wordings = 37,800 distinct
transcripts. Priced at the bracket's ends before registering: 25% declared
delivers 25.0% with the class at 68.3% of its space; **40% declared delivers
only 33.2%**, draws 95.4% of everything there is, drops 62.2% of every draw, and
*reduces* the file's distinct utterances from 87,297 to 79,717. The top of the
pre-registered bracket is not deliverable at 30MB, and a share arm has to buy
more sentences before it can ask for a bigger dose.

The bracket's floor is not reachable by declaring it either: built at
`--decline-share 0.25` the payloads delivered 24.95% and 24.31%, below the
pre-registered floor on both arms, and were rebuilt at 0.27 rather than
reinterpreted.

**Grid A's novel column is a weaker holdout after this arm than before it.** Its
32 action requests remain string-disjoint from the payload and no payload
request sits within three content words of one — `check_p3e.py` asserts both,
and six requests were rewritten to satisfy the second. But the payload now
teaches the class those items belong to, so the column measures generalisation
inside a trained class rather than to an untrained one. The trained column's
frames were always trained; that has not changed.

Two seeds a side, directions not sizes (ground rule 6). Authored fills, not user
traffic. Greedy only. The `smart_home` cell of grid A is still novel-only on
every checkpoint. And the decline side of the corpus carries ~6,630 distinct
utterances against the served side's ~80,000, each recurring about four times
under a different refusal wording — not a copy-slot regime, since a decline
transcript copies nothing, but it is the ceiling the next dose runs into.

## Addendum, same day — the full frozen-row diff, and the two rows the grid read does not see

`scripts/rowdiff.py` from the base card to each of the four arm cards,
written by a second session after the finding above was committed. The moved
set is near-identical across all four arms, and almost all of it moves up:
`turn2.first` and `daycross.no_day` join `tool.selection` at 171 → 200/200,
`turn2.second` 177 → 199–200, `tool.name_fidelity` 106 → 116–119,
`notefid.trained_phrasing` 74 → 101–105, `notefid.novel_phrasing`
66 → 85–90. The likelihood rows tick up in the third decimal
(`lm.conversational` 0.2905 → 0.2946 nats/byte), the same size and direction
as every p3b2 arm. The new rows read as expected for a corpus with no
extraction slice and no second-turn class: `extract.span` 16–21/200 with
`abstain` 1–2 (the no-extraction controls' numbers), `turn2.react`/`reask`/
`chain_result` at the eight-checkpoint baseline's zeros. One direction worth
a line: `compound.pipe_first` reads 32–37/48 on all four arms where
`ftextract` collapsed it 41 → 18 — the nano floor spans 15–41 so this is a
direction, not a size, but four arms agreeing at the base's level where one
arm halved it is the direction.

**Two rows move down, and neither is a regression in the treatment's own
terms — but both need recording.** `chat.abstain_oos` drops 33 → 9–13 on
every arm, and the named split says why: the row's gold is *silence* on an
uncovered request, and **91 of 100 turns now route to `decline`** — where
the base split 36 `decline`, 30 wrong-tool (`save_note` 17, `web_search` 6,
`place_call` 4, `send_text` 3) and 1 invented tool, the wrong-tool calls
vanish entirely. The routed refusal is grid A's gold and the runtime hatches
it into a spoken reply; the row's silence gold scores the strictly better
behaviour as failure. That is the same tension `configs/mix_p3e_ft_e1.py`
registered before the run, now surfaced on a frozen row: re-gold it to
accept a `decline` call, or retire it in favour of grid A — a decision, not
a fix, and it is recorded here as open. Second, smaller: `daylog.open` and
`daylog.targeted` go 4 → 0 of 90/84 with the `why` flipping from the base's
majority-`no_say` (63/23 silence over confabulation) to
majority-`confabulated` (86/4) — finding 71's conversion of silence into
recitation, arriving as a side effect of a tools fine-tune on rows whose
supply gap is already recorded. `chat.abstain_greet` moves both directions
across the four arms (63–77 against the base's 67) and is not readable at
two seeds.
