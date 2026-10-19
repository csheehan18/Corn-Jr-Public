# He can't build a goal from two observations at one pass

**Full result:** G6's first rung, combine: at one pass he does not build the goal from two observations; both twins right on 5 and 0 of 288 held-out rows and 1 and 1 of 144 trained ones, against controls that never saw a note at 4-6 and 2-3; the request does not choose the clause even on the traces he trained on or when the note repeats the request's own words, and what forms instead is a fixed ranking of the note's phrasings, a different one at each seed

**Cost:** two nano runs, 1,154 s and 1,263 s, contended (the card at 35-39%
before every job, so the times are bounds); probes about 2 min a checkpoint;
eight control reads while the rows were built, about 6 min; three cause
probes, about 3 min. Built and read 12:52-15:20 on 2026-10-08, against a
registered ~50 min of card time.

ROADMAP G6, the first rung of PLAN-TAG-LANGUAGE's ladder after `filter`.
**Combine, defined by the owner on 2026-10-08, is using two results
together.** A request asks for a place someone would like ("somewhere to eat
in Garathmere under 30 that Jorendbourne would like"). He looks the person up
and gets a note with one clause per kind of place ("for a meal they like
somewhere low-key; for a sundowner, somewhere with a buzz; on holiday,
somewhere homely"). Then he lists the places. The goal's `soft[...]` must be
the clause the request's kind of place names. Arm E2's mix plus 6,300 such
traces at one pass (`configs/mix_v3_funcworld_combine.py`, pre-registered at
60d98b8); arm E2's three seeds are the controls. **Cards:**
`evals/results/nano20m_v3_fw_combine*__combine.json`, `*__copy.json`, and
the controls' `nano20m_v3_fw_filter_ev2*__combine.json`.

## Caught before the read

The controls were read before anything trained, and four times a model that
had never seen a note scored above chance. Each time the gold was readable
without the request: it was the only clause with a place in the list; a
phrasing-family familiarity prior; rung 3's rule that a concept never sits
beside its near-synonym; and a skew in which concepts could be decoys (cosy
was the gold on 85% of the rows it appeared on). Removing the list or the note
left that last read where it was, 112 and 111 of 288 (probe only). Each was
fixed in the generator (`corn/combinegen.py`'s comment carries all four), and
**the registered gate became `paired`**: both twins of a row right, where the
twin moves only the request's kind of place. A model with any fixed preference
that ignores the request scores zero there by construction.
`scripts/check_combine.py` holds all four fixes on the bytes, and it caught
five cue words that shared a stem with something else in the world before
anything trained.

## The registered read

    checkpoint          paired held-out   paired train   right held-out   right train   moved (of 288)
    combine 1337              5 / 288         1 / 144          97              42            23
    combine 2337              0 / 288         1 / 144          86              41            14
    E2 1337 (control)         6               2               106              45            30
    E2 2337 (control)         4               3                90              61            35
    E2 3337 (control)         6               3               112              56            26
    gate                  more than 42    more than 23

**"Nothing installs at either seed"**, the pre-registered row: paired train
is 23 or fewer at both seeds and paired held-out 42 or fewer at both. Its
license: combine at nano is not his at one pass, and the dose is the next
variable.

**The standing kill fires as written**: `tool.copy` reads 100 and 102 of 120,
under 118 at both seeds. The bar was inherited from arm E2's config, and E2
seed 1337's own card reads 102. So seed 1337 matches its control, and seed
2337 fell from E2's 119 to 102.

## Why it fails -- the cause probes

The probes ran on both arm seeds and two control seeds (probe only,
scratchpad scripts):

    checkpoint        right on his own training traces (of 400)   paired with the request's words in the note
    combine 1337              136                                      6
    combine 2337              155                                      5
    E2 1337                   146                                      5
    E2 2337                   129                                      5
    chance                    133                                     32 (1/9)

1. **Not learned on the text he trained on.** On the payload's own first
   400 traces he picks the right clause at the controls' rate. This is not
   memorised pairings that fail to generalise; the routing never formed.
2. **Not a problem of meaning.** With each clause's cue rewritten to repeat
   the request's own phrase ("for a place for dinner they prefer somewhere
   scenic" beside "look for a place for dinner"), paired stays at 6 and 5, the
   controls' level. He does not route even when the words match exactly, so
   the wall is not rung 3's synonym association.
3. **Not the list.** His chosen clause's place in the list is spread just
   like the gold's (first ok place 247-259 of 864 against the gold's 247), so
   rung 3's first-ok habit is not what drives it.
4. **A habit formed instead**: by note position seed 1337 takes the last
   clause on 411 of 864 prompts (48%, against 269-308 for the controls), and
   seed 2337 leans to the middle (337). The request moves his choice on 14-23
   of 288 twins, fewer than the controls' 26-35. The hand read below shows
   the habit is a ranking of the phrasings, which position only shadows.

**The form installs.** His free-decoded goal is exactly the gold on 96 and
86 held-out rows, the full-option count to within one, and it is written
from the note's own phrasings. He learned to copy a clause from the first
observation into `goal:`. What he did not learn is to let the request choose
which.

## Read by hand

The probe prints six rows whole, but the first read of them covered seed
2337 only; this section first claimed six rows a seed. The real hand read
(2026-10-08, after the owner asked; probe only, a scratchpad script):
24 held-out rows spread across the cell, each with its twin, greedy free
decode, at both seeds, so 96 decodes:

- **Every one is a well-formed goal line copying one of the note's three
  phrasings verbatim** (96 of 96), with the request's hard term right. The
  form installed completely.
- **On all 24 rows at both seeds, the twin writes the identical line.**
  Asked for "a place for dinner" and then "a place for drinks" against the
  same note, he writes the same `soft[...]` both times.
- **What decides it is the phrasing itself, a fixed ranking per seed.**
  Seed 1337 takes "quiet" 4 times of 4 offered and "in the open air" 3 of 3,
  and never "scenic" (0 of 5) or "with a buzz" (0 of 4). Seed 2337 takes
  "scenic" 5 of 5 and "lively" 5 of 5, and never "for the little ones" (0 of
  9) or "full of energy" (0 of 4). The cue in front of the phrasing ("for a
  meal", "on holiday") does not move it: picks per cue sit between 0 of 7 and
  6 of 10 at both seeds.

The note-position counts in the probe section are this ranking seen from
the side: the last clause wins more often at seed 1337 because the rows put
its favoured phrasings there more often, not because position is the rule.
So the position habit in the title and the cause probes is better read as a
phrasing habit. Because every concept is the gold on a third of the rows it
appears in (the fourth control fix), a phrasing ranking scores chance, and
`paired` scores it zero.

## What it licenses

- **Combine at nano and one pass reads zero**, and the cause is that the
  choice never conditioned on the request. That holds on trained text, on
  held-out text, and with the words matching. This is the shape finding 148
  recorded for `filter`: a choice that depends on a distant span does not
  form at this scale and dose, and a position habit forms in its place.
- **The next variable is the dose**, as pre-registered. If a higher dose
  also reads zero, the routing goes to the runtime (a clause-to-domain table)
  and the note's text reaches him already chosen. That is SPEC §0's rule
  applied: a choice the runtime can make by lookup is the runtime's.
- **The bind's wider copy source (request plus a prior observation) is not
  adopted.** The form installs, but nothing is gained by it until the choice
  does.

## Limits

Two seeds, one dose, nano only. The probe scores three teacher-forced goal
lines; the free decode is a side column. The cause probes are hand-built and
unpinned, so their numbers are bounds (CLAUDE.md). Rung 3's held-out cells are
not readable on this arm (the mix config says why).

## Amended 2026-10-08 -- four times the dose, and combine goes to the runtime

The dose arm finding 156 pre-registered (`configs/mix_v3_funcworld_combine4.py`,
at fd5a41d): the same payload at four times its weight by repetition, 8.3% of
the mix, 6,231 iterations; same rows, probe and gate. Two nano runs, 1,367 s
and 1,373 s, contended. **Read by hand first**: 24 held-out rows and their
twins, free decode, both seeds (probe only, the same scratchpad script):

    seed   twin writes the identical line   both twins right   phrasing ranking
    1337        23 of 24                         0             "romantic" 4 of 4, "for an anniversary" 4 of 4; "family-friendly" 0 of 6
    2337        18 of 24                         1             "good for kids" 8 of 10; "quiet" 0 of 8, "with a buzz" 0 of 8

Every decode but one is a verbatim note clause; the one is a note span that
is not a clause. **The cards** (committed, `evals/results/
nano20m_v3_fw_combine4*`):

    seed   paired held-out   paired train   right held-out   moved (of 288)   tool.copy
    1337        8 / 288          4 / 144          105              32            120
    2337        4 / 288          4 / 144           94              34            102

**"Nothing installs at four times either"**, the registered row: combine goes
to the runtime -- the clause is chosen by lookup (the request's kind of place
against a clause-to-domain table) and he is shown the one clause, already
chosen, as SPEC §0 has it. The rebased copy kill does not fire: 120 and 102
against the one-pass arm's 100 and 102. Four times the dose moved the twins on
6 of 24 rows at seed 2337 against 0 of 24 at one pass, and took no row of 288
to both twins right. The habit is the same phrasing ranking, re-drawn.
