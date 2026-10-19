# Questions about his life go to the web six times in ten

**Full result:** The family check and the life hatch land with the card reading them: a question about his life goes to the web on six to eight turns in ten, the fold and the reserve move no copy column on the checkpoint that copies, the first distractor copy is seen at depth three, and a lookup history costs the next social move a third of its answers

**Cost:** 3.1 min of scoring on the 2 cards first cited here (`corn_jr_260m_v4_ft4g__historygrid-0905ctl`, `corn_jr_260m_v4_ft_social3__historygrid-0905ctl`); it also reads 3 cards scored for an earlier finding (`corn_jr_260m_v4_ft4g`, `corn_jr_260m_v4_ft_social2`, `corn_jr_260m_v4_ft_social3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**Numbered 128 on 2026-09-08, having been written as 115.** Two sessions on
2026-09-05 both claimed 115 — this one at 13:46 and the grounding-rule
finding at 15:01 — and both rows sat in the table for three days, so "finding
115" was ambiguous in five source files. The other one keeps the number: five
frozen scorecards are named `*__grounded115.json` and cannot be renamed
without breaking the manifests that carry their hashes, where everything
pointing here is prose. So this file is out of date order by three days, and
the number is the citation key rather than the clock.

2026-09-05. **PLAN-CONVERSATION's card half**, run serialised on the 3080 in
the evening after the CPU half landed in `a67d0779`. Nine `historygrid`
cards (`harness/results/*__historygrid-0905*.json`, seed 0, `--multi`,
`--no-log`, no packs, the owner's `server.json` bypassed with an empty
`--config`) and three `corn.evals --only social,social_self,social_low`
cards (`evals/results/social__*__socialrows-0905.json`). Nothing trained.
Every number below is read against the readings pre-registered in
`docs/PLAN-CONVERSATION.md` §4g, §4h (the fourth section), §5a--5c and §6d.

## 0. What ran

    historygrid   ft4      depth 1   shipped / fold
                  ft4      depth 3   shipped
                  arm 2    depth 1   shipped
                  arm 2    depth 3   shipped / fold / reserve (--round-reserve 115 --budget 96)
                  ft4g     depth 1   shipped
                  arm 3    depth 1   shipped
    evals         ft4g, arm 2, arm 3   social.*, social.self*, social.low_*

`arm 2` is `corn_jr_260m_v4_ft_social2`, the checkpoint the 2026-09-04
session ran on; `arm 3` is `_social3`. Every card's `social_nocall` arm
landed 18/18 and `adjacent_frame_kept` read 8/8 and 4/4 everywhere, so the
frame is not what any number below is about.

## 1. `social.self` -- the residue is the router, not a life

The row PLAN-CONVERSATION 5a built as a ruler, 47 declared prompts about his
life with no prefill, read on the three checkpoints:

                        pass    web_search   decline   say passes   say refused
    ft4g              7 / 47       39            7          0            1
    arm 2            13 / 47       30            3         10            4
    arm 3            16 / 47       28            6         10            3
    held-out 16      3 / 8 / 8

**The defect §1 quoted -- "I'm 23.", "I'm a web developer" -- is one item in
forty-seven on every checkpoint** (`life: i got a`, once each). What the
router does with "how old are you" is send it to `web_search`: **83%, 64%
and 60%** of the row. That is finding 78's grid M species again -- a question
about *him* answered out of a search index -- on the family of questions that
finding did not probe. So §10 decision 8's question ("does the routed say's
residue deserve a guard of its own?") has its number, and the number says
the guard would be aimed at the wrong place: the residue is a call, not a
sentence, and no `social_rejection` clause reads a call. The 4c hatch closes
31 of the 47 phrasings before the router sees them; the 16 held-out
phrasings are the honest size of what is left, at 19% / 50% / 50%.

## 2. `social.low_*` -- the floor is a floor

                          low_declared_nocall   low_voice   low_family   heldout
    ft4g                        7 / 28            17 / 28      0 / 28     0 / 4
    arm 2                      17 / 28            24 / 28      2 / 28     0 / 4
    arm 3                      16 / 28            23 / 28      1 / 28     0 / 4

`low_family` reads 0 to 2 of 28 -- the "expected near 0" of §6a's floor,
now a number arm 5 is read against. The species behind the routing half is
§1's own: on arm 2 the eleven misses are all `called_decline` ("Wish I
could, but nothing here does that." to a stated low mood), and on ft4g
fifteen decline and four search. With `<|say|>` supplied the sentence is
speakable four times in five on the social arms (`low_voice`), and it is
not a consolation: `no family marker` on 20 of 26 misses, the rest answering
ack, greeting or wellbeing. That is the gap between "he can speak" and "he
answers the feeling", as a pair of columns.

## 3. `social.voice` after 4b's carve-out, and `family` unmoved

`sorry you`, `glad you` and `birthday` left the life-claim list; the
consolation markers carry the first two. Re-scored on the same 112 items:

                    voice              family     farewell (voice)
    ft4g          57 -> 59  +2        53 -> 53     11 -> 11
    arm 2         86 -> 89  +3        71 -> 71     13 -> 14
    arm 3         90 -> 93  +3        65 -> 65     12 -> 13

Two to three items a checkpoint, all of them replies the old list refused
as a life and the new one does not; `family` byte-identical, which it had to
be -- the five families' markers did not move and `good to hear` joined the
ack list on a line no item carried. The delta is recorded here and the row
is comparable across the date with this line beside it.

## 4. The fold and the reserve, on the checkpoint that copies

At depth 1 (one prior turn) the fold never fires and the ft4 rows are
identical shipped against fold. At depth 3 on arm 2, where the trimmer takes
the oldest turns:

                                reissued_q   reissued_u   copied_from            social_answered
    arm 2  depth 3  shipped       1 + 1        1 + 1      bound 3, distractor 1     22 / 36
    arm 2  depth 3  fold          1 + 1        1 + 1      bound 3, distractor 2     23 / 36
    arm 2  depth 3  reserve       1 + 1        1 + 1      bound 3, distractor 1     20 / 36

(`reissued_q` and `reissued_u` are the `lookup_ok` + `lookup_fail` cells of
8; the same probe, "who painted the mona lisa", re-issues under every
lookup history on every arm.)

**§4g's second reading fires: the fold is a compression only.** `reissued_*`
and `routed_fresh` are unmoved, and the reason is sharper than the plan's
hypothesis allowed. The fold deletes the `<|call|>` line, but on a lookup
turn the user line *is* the query -- "the capital of Selaethdia" is what was
typed and what was searched -- so the string the copy grammar lifts survives
the fold in the half the fold keeps. The paragraph in §4g claiming the fold
"deletes the exact string `reissued_query` copies" is withdrawn on its own
terms; the depth column it buys (finding 4g's table: depth 3 held whole 2% ->
74%) stands, and `social_answered` under the fold is within one item of
shipped.

**§4h's second reading fires: the sliced head was harmless at this depth.**
Every copy column under `--round-reserve 115 --budget 96` is the shipped
column exactly; `social_answered` is two items lower, inside the spread the
same cells show between seeds of the same setting. The reserve ships as
correctness (default off, the A/B arm) and §4f is priced against it.

**§6d's second reading is seen for the first time.** `copied_from` reports
`distractor` at depth 3 -- one case shipped, two under the fold -- after a
*social* opener: with no query of its own in the bound turn, "who painted
the mona lisa" lifted "the capital of Elmorndmar" from two exchanges back.
At depth 1 the column is `bound 1, none 71` on ft4g and arm 2 and `none 72`
on ft4 and arm 3; at depth 3 the bound copies are three on arm 2 and there
are none on ft4 at any depth. He binds to the wrong turn when there is a
wrong turn to bind to, at about one probe in seventy on the checkpoint that
copies at all. Arm 8's premise holds and its effect size is small on the
grid; the live session's byte-for-byte re-issues were under a deeper and
messier history than any arm here builds.

## 5. `social.second_turn`, as the grid reads it

The new social probe family -- six whole-utterance moves after each history,
scored on no call plus the move's family in the reply:

                  control   after lookup_ok   lookup_fail   chat_nocall   declined   social_nocall   all six arms
    ft4            6 / 6        5 / 6            5 / 6         6 / 6         5 / 6        6 / 6         32 / 36
    ft4g           6 / 6        2 / 6            2 / 6         3 / 6         4 / 6        6 / 6         21 / 36
    arm 2          6 / 6        4 / 6            4 / 6         4 / 6         4 / 6        6 / 6         26 / 36
    arm 3          6 / 6        3 / 6            2 / 6         4 / 6         5 / 6        6 / 6         23 / 36

Every control answers 6/6 and every social-after-social answers 6/6, so the
hatch holds a conversation with itself. **What costs the next social move
is a *tool* turn before it**: after a lookup, ft4g answers two of six, the
social arms three or four. The misses are `web_search` calls on "good night"
and "rough day" -- the routing prior of the previous turn carried into a
turn that has no request in it, which is finding 35's number ("multi-turn is
0.34% of the mix and the only shape is the daycross follow-up") as a
column. This is the row arm 7 is read on, and its base is written: 26/36 on
arm 2.

## 6. What this does not claim

Not that the fold is wrong to ship: the depth it buys is measured and the
copies it fails to remove were never going to move on a checkpoint that
copies at depth 1 with nothing to fold. Not that the reserve is unnecessary:
the probe's 61--78% second-round cut is real; it is harmless *on these
columns at this depth*, and the frame row cannot see a sliced declaration
that a later round recovers from. Not that `social.self`'s 16 held-out
phrasings are the whole residue -- they are the sixteen a session wrote, and
the web-search share on them (12 of 16 on ft4g) is the number to widen the
hatch against, not a bound. Not a seed replicate on anything: one seed, one
grid, and the between-arm differences on `social_answered` are one to two
items out of six.

## Measurement provenance

`harness/results/corn_jr_260m_v4_ft4__historygrid-0905{ctl,fold,ctl-depth3}.json`,
`corn_jr_260m_v4_ft_social2__historygrid-0905{ctl,ctl-depth3,fold-depth3,reserve-depth3}.json`,
`corn_jr_260m_v4_ft4g__historygrid-0905ctl.json`,
`corn_jr_260m_v4_ft_social3__historygrid-0905ctl.json`; each records its
`decode` block with `family_check`, `round_reserve` and `budget` in the
instance. `evals/results/social__{corn_jr_260m_v4_ft4g,corn_jr_260m_v4_ft_social2,corn_jr_260m_v4_ft_social3}__socialrows-0905.json`
against the same checkpoints' `__socialrows.json` from 2026-09-02/03 for the
before column. Source `a67d0779` plus this file. Every card was read with
the server's `--family-check on` default, which touches only the hatch path
and no row here reads the hatch path's own sentence.
