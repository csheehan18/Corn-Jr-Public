# The best tool-router never declines; the best decliner never serves

**Full result:** The checkpoint that routes best never declines, and the one that declines best never serves

**Cost:** 0 s of new scoring on record; it reads 2 cards scored for an earlier finding (`corn_jr_260m`, `corn_jr_260m_ftextract`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`corn_jr_260m` and `corn_jr_260m_ftextract`, 2026-08-26, measured by
`harness/toolgrid.py` — the R1 instrument of `docs/PLAN-P3-RULERS.md`,
pre-registered the same day. 808 turns per checkpoint, greedy, table-backed
(`search: table`, nothing leaves the machine), against the live server at
rev `411f2f1` (dirty). `hatched: 0` on every cell — no turn was answered by
the runtime, so every number below is the model. No training.

## Where it came from

Three failures from the 2026-08-26 live audit had no instrument: `decline`
under-firing on action requests (`checkup` read `held_back` **2/5**, all
three misses sinking to `web_search`), `send_text` losing carriers ("send a
text to Sam Iversen" → `ask_agent`), and `save_note` routing collapsing
under date-bearing content. `checkup` measures these with denominators of
three and five; `searchgrid` measures only turns whose right answer is
`web_search`. The plan's own closing sentence was that running Phase 3
without this grid would leave its motivating failures unmeasured before
treatment. The grid was built, and the first thing it measured was bigger
than the three failures it was built for.

## The see-saw

Serve-cases are grids B and C (600 turns: contact carriers and note
carriers); decline-cases are grid A (208 turns: 176 trained decline shapes,
32 novel action requests).

    checkpoint    decline-cases right    serve-cases right
    base              201/208  96.6%          118/600  19.7%
    ftextract          88/208  42.3%          386/600  64.3%

**Neither checkpoint is deciding.** The base declines almost everything
that is not a search question — including 298 of 424 real call and text
requests and 154 of 176 real notes, phrasings its own corpus taught. The
fine-tune moved the mass wholesale the other way: serve-routing tripled and
decline collapsed to 82/176 on *trained* shapes and 6/32 on novel ones. The
displacement is directional and names its own cause: ftextract's misses
land on `web_search` (49, 44, 41 across the three grids) and `ask_agent`
(41, 69, 44) — the two tools its fine-tune corpus is about. The p3b2 tool
corpora are the first to carry `ask_agent` transcripts at all (8,376 each;
the shipped tools corpora carry zero, counted in `PLAN-5B-SUPPLY.md` §7),
and the tool the base never saw is now absorbing 154 turns of everything
else. **The fine-tune moved the prior, not the judgement.**

## Grid A — decline, and why the base's ceiling is not a skill

    base         trained 172/176   novel 29/32   misses: 6 silent, 1 place_call
    ftextract    trained  82/176   novel  6/32   misses: web_search 49,
                                                 ask_agent 41, save_note 29

Read alone, the base's column says decline works and the fine-tune broke
it. Read against grids B and C it says something worse: the base declines
*as a default*, so its grid A score is the same bias that costs it 482
serve-cases, wearing the one costume where it happens to be right. A
decline rate is only evidence of discrimination when the same checkpoint
also serves, and no checkpoint on disk does both.

## Grid B — the contact carriers, and finding 52 on a second tool family

424 turns: every trained `place_call`/`send_text` carrier the corpus
teaches, eight fills each from the training book's first names, plus the
messageless family measured failing live ("send a text to {c}").

    base         trained routed  96/400    place_call 89/224   send_text 7/200
    ftextract    trained routed 302/400    place_call 197/224  send_text 109/200
    messageless  base 0/24    ftextract 4/24

The base's per-carrier column is the fifty-second finding's shape on a
second tool family: `call {c}` routes 8/8 while `give {c} a ring`,
`get hold of {c}` and `I want to talk to {c}` route 0/8 — the corpus
teaches the carriers and the weights keep a few. On ftextract the slots are
healthier than the routing: `kept_message` 99/105, `kept_contact` 249/302 —
and `shed_overrun` is now a counted repair rather than an argument:
`send_text` `kept_contact` reads **71/109 raw and 83/109 after the shed**,
twelve texts to the right person recovered at the lookup. The messageless
family is a near-total loss on both checkpoints and lands on `ask_agent`,
which confirms the carrier-overlap hypothesis the plan registered ("to {c}"
reads as relay) and makes it a corpus line rather than a suspicion.

## Grid C — notes under content, the first content-conditioned routing read

176 turns: 22 trained note carriers held fixed, content crossed four ways.

    content class      base routed    ftextract routed
    plain                 5/44            37/44
    date_bearing          4/44            16/44
    question_shaped       5/44            11/44
    real_entity           8/44            16/44

The base is flat — it declines notes regardless of content, so content does
nothing to a checkpoint that never serves. On ftextract the interaction is
real and large: **the carrier is identical and the content halves the
routing**, with the misses going to `ask_agent` (44) and `web_search` (41).
A date inside the note text pulls the turn toward the tools that answer
date questions; an entity pulls it toward search. The live audit's single
anecdote ("note down dentist appointment moved to friday") is a 21-point
effect at n=44 per cell, and the cheap generator change — dates and
entities inside note text — is licensed by measurement.

## What this retires and reframes

The sixty-third finding's sentence — routing installs by fine-tune —
survives with one word changed: the routing **prior** installs by
fine-tune. Its evidence was `searchgrid`, 400 turns on which the right
answer is always `web_search`; on such a grid a checkpoint that reaches for
`web_search` indiscriminately is indistinguishable from one that
discriminates, and grid A is the column that separates them. The handoff's
(now `STATUS.md`'s)
"`ftextract` is the best of the four on live routing" is therefore a claim
about search-shaped turns only, and `checkup`'s `held_back` 2/5 was the
real reading of a real problem at a denominator that could not carry it —
it is 88/208 now.

## What it licenses, and what it does not

The Phase 3 variable this names is **balance**: a fine-tune corpus in which
served and declined requests are trained against each other, graded on both
columns of the see-saw at once, plus three named supply lines — content
variety inside note text, the messageless text family, and carrier breadth
generally. What it does not license is any claim about *which* share or
mix achieves the balance; that is an arm, and this is its ruler. Both ends
of the see-saw now have baselines in `harness/results/`.

## Limits

One seed per side — the seed2 fine-tunes are on disk and unscored (R4), and
findings 57 and 61 both caution against reading a two-checkpoint difference
as a trend before the spread is known. The fills are authored, not user
traffic. Greedy only. Both checkpoints were served the same eight-tool
declaration, but only ftextract's corpus contained `ask_agent`, so part of
the displacement is a sink existing for one side and not the other — which
is itself the finding's mechanism, not a confound of it, and the seed2
scorecards can say how stable it is.
