# The second social turn installs and lifts the first

**Full result:** The second social turn installs and lifts the first: declared abstention reads 111 of 112, the consolation row 11 of 28, nothing reissues under a social history, the turn-2 rows do not move, and the one cost is that the router now speaks on questions about his life and half of what it says is SODA's

**Cost:** 9.7 min of scoring on the 3 cards first cited here (`corn_jr_260m_v4_ft_social7`, `corn_jr_260m_v4_ft_social7__historygrid-0905ctl`, `corn_jr_260m_v4_ft_social7__toolgrid`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**`corn_jr_260m_v4_ft_social7`, 2026-09-05. PLAN-CONVERSATION §6c on arm 5b's
basis: the same generator, replies and seed with `--turns 2` -- half the
pairs carry a shared opening and a second turn, `social -> say -> social ->
say` beside `social -> say -> request -> call` on one declaration and one
opening, the second family drawn from `TURN2_PAIRS`, farewell never second.
`init_from` ft4g, arm 2's share, 1,200 iterations in 1,512 s, best at 1,000
(val 0.5878). Full batched card, grid A, historygrid at depth 1 and at depth
3, the ft4g adapter as a proxy. Arm 6 did not run (finding 120 §4), so this
arm inherited arm 5b's config as §6b said it would.**

## 1. The social rows, against arm 5b (the arm before it)

    row                        arm 4    arm 5b     arm 7   7-5b
    social.bare_nocall        99/112    97/112   102/112    +5
    social.declared_nocall    97/112    97/112   111/112   +14
    social.voice              90/112    90/112    99/112    +9
    social.family             69/112    67/112    71/112    +4
    social.farewell            14/20     14/20     16/20    +2
    social.heldout_carrier     10/12      9/12     11/12    +2
    social.self               16/47     13/47     18/47    +5
    social.self_heldout         8/16      7/16      7/16     0
    social.low_bare_nocall     14/28     14/28     16/28    +2
    social.low_declared       16/28     17/28     26/28    +9
    social.low_voice          23/28     25/28     27/28    +2
    social.low_family          1/28      7/28     11/28    +4
    social.low_heldout          0/4       1/4       1/4      0

    declared_nocall why     arm 5b  web_search 6  decline 9  |  arm 7  decline 1
    low_declared why        arm 5b  decline 8  send_text 3   |  arm 7  decline 2

**Every social row moved up, and the routing pair moved most.** On the
declared social turn -- the context the corpus had zero of, the row this
whole slice was built for -- one item in 112 still calls, and it calls
`decline`. `web_search` is gone from that column. The consolation family,
which no second-turn transcript targets by name, reads 11 of 28 with its
declared abstention at 26 of 28; the untrained farewell transfer row reads
16 of 20; the twelve held-out carriers 11.

Why a *second* turn lifts the *first* is the shape: 905 of the 1,821 social
transcripts now carry two social exchanges, so the payload holds 2,726
social moves answered without a call where arm 5b's held 1,821, on the same
token share -- and the second exchange sits where the corpus never showed
one, a `<|say|>` followed by another social `<|user|>`, which is what the
declared-social context looks like from the inside of a conversation rather
than from its first line.

## 2. The second-turn rows -- the pre-registered readings

    historygrid, seed 0                     arm 2     arm 5b    arm 7
      depth 1  social after a tool turn     26/36     22/36     26/36   (control 6/6)
               social_nocall arm            18/18     18/18     18/18
               reissued under social_nocall   0/12      0/12      0/12
               copied_from                  bound 1   none 72   bound 1
               adjacent_frame_kept          all       all       all
      depth 3  social after a tool turn     22/36        --     23/36
               copied_from                  b3 d1        --     b2 d1
               reissued, lookup_ok (q, u)    1, 1         --     1, 1
               adjacent_frame_kept          all          --     all

    the frozen second-turn and compound rows
      turn2.react     117/120 (arm 5b 116)     turn2.reask    79/96 (78)
      turn2.reask_yn   22/40  (arm 4 24)       turn2.second  198/200 (198)
      compound.pipe    40/48  (41)             compound.items 30/48 (30)

**The kill did not fire.** `reissued_utterance` under `social_nocall` is 0
of 12 as it was on every checkpoint; the lookup arms at depth 3 read arm
2's 1 of 12 exactly; `copied_from` is arm 2's shape (bound 2, distractor
1); the frame is kept everywhere. The social probe after a tool history is
back at arm 2's 26 of 36 -- the ft4g init's seven-item cost (finding 119)
closed by the second turn. `turn2.react`, `reask`, `second` and the compound
rows are inside a point of the arm before. **He answers inside a
conversation and the history does not leak into the next call**, which is
§6c's first reading verbatim.

## 3. The gates, against ft4g

    row                     ft4g    arm 5b     arm 7   7-ft4g
    tool.copy            120/120   120/120   120/120     0
    tool.copy_wide       300/300   300/300   300/300     0
    temporal.copy        353/353   353/353   353/353     0
    refusal.say          270/270   270/270   270/270     0
    tool.selection       198/200   197/200   196/200    -2
    tool.name_fidelity   109/120   109/120   109/120     0
    temporal.route       398/400   398/400   398/400     0
    search.route_*       200/200   200/200   200/200     0   x3
    chat.abstain_talk    100/100   100/100   100/100     0
    chat.engage          100/100   100/100   100/100     0
    chat.abstain_oos      11/100    11/100    10/100    -1
    chat.abstain_greet    83/100    91/100    92/100    +9
    tool.note_fidelity   100/120    97/120    94/120    -6
    extract.span          97/200    93/200    92/200    -5
    extract.abstain      111/200   113/200   111/200     0

    grid A, decline           ft4g    arm 5b    arm 7
      pooled trained        174/176   176/176   175/176   one media decline to web_search
      pooled novel            32/32     31/32     31/32   timers 7/8 ("snooze that for ten")
    reader proxy (ft4g adapter, fixed t)
      right / u.silent       526/199   524/197   524/195   moved 25, right 6 lost / 4 won

Every frozen copy row at its ceiling and `refusal.say` unmoved, a seventh
time. `tool.selection` -2 and `note_fidelity` -6 are inside finding 60's
9-in-120 floor and are the two rows to watch on the next arm; the extract
lean is the init's (finding 119). Grid A is arm 5b's to within one item on
each column.

## 4. The one cost, and it is decision 8's

`social.self` rose 13 -> 18, and the species under it moved:

    social.self why        arm 5b   called_web_search 31   spoken leak 1   (life)
                           arm 7    called_web_search 16   spoken leak 9   (digits 5, i work 2, history class 1, names 1)
    social.self_heldout    arm 5b   web 7   leak 1
                           arm 7    web 3   leak 4

The router now speaks on twice as many questions about his life, and
**about half of what it says when it speaks is a SODA life** -- "I'm 23",
"I work ...". No second-turn transcript carries a life claim (every reply
passed `life_claim` before it was trained); what the class taught is the
*willingness to speak* on a short second-person question, which is finding
88's mechanism a third time, and the sentence he speaks is the one SODA
gives him. At runtime the 31 trained carriers never reach the router (4c's
hatch answers them from the pool), so the live exposure is the 16 held-out
phrasings, four of which now get a life instead of a search. That is
exactly §10 decision 8's residue -- the unguarded routed say -- **larger
than it was**, and the arm makes the case for the router-side rule the
decision names (a question with `you`/`your` and no request) rather than
for a payload, which §3 rule 1 forbids. Recorded, not repaired.

## 5. Reading

**§6c's first reading, with a footnote that is not this arm's to fix.** The
second social turn installs, lifts the single-turn rows with it, spends
nothing on the gates, and the history does not leak. Arm 7 is the best
checkpoint on the record on every social row and the base arm 8 stacks on.
The footnote is `social.self`'s species, which is a runtime question
(decision 8) that every arm from here on will make more urgent, because
every one of them makes him more willing to speak.

## Limits

One seed. The rows that moved most are 112 items; the second-turn rows are
12 and 36; the `self` species is 9 lines of 47. The reader proxy is at a
fixed threshold.

## On disk

`evals/results/corn_jr_260m_v4_ft_social7.json`,
`harness/results/corn_jr_260m_v4_ft_social7__toolgrid.json`,
`harness/results/corn_jr_260m_v4_ft_social7__historygrid-0905ctl.json` and
`-depth3.json`, `evals/results/reader_runtime_whole_s1_on_social7.json`;
`checkpoints/corn_jr_260m_v4_ft_social7/` (gitignored).
