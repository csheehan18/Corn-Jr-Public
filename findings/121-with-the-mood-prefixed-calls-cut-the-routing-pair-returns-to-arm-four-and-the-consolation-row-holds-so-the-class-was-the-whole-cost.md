# Hundred-and-twenty-first finding — with the mood-prefixed calls cut, the routing pair returns to arm 4's band and the consolation row holds at 7 of 28, novel decline reads 31 of 32, and the class was the whole cost

**Cost:** 9.7 min of scoring on the 3 cards first cited here (`corn_jr_260m_v4_ft_social5b`, `corn_jr_260m_v4_ft_social5b__historygrid-0905ctl`, `corn_jr_260m_v4_ft_social5b__toolgrid`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**`corn_jr_260m_v4_ft_social5b`, 2026-09-05. Arm 5's generator, replies and
seed with one switch flipped -- `corn.socialgen.MOOD_BALANCE` off -- so the
31 "mood, then a request -> call" transcripts are gone and the 52
consolation moves ride with the plain balance every family has. `init_from`
ft4g, arm 2's share, 1,200 iterations in 1,505 s, best at 1,000 (val
0.5875). Full batched card, grid A, historygrid depth 1, the ft4g adapter
as a proxy. Pre-registered in `configs/mix_v4_ft_social5b.py` before the
run.**

## 1. The rows, against arm 4 (the bar) and arm 5 (the one-file difference)

    row                        arm 4     arm 5    arm 5b   5b-arm4   5b-arm5
    social.bare_nocall        99/112    93/112    97/112     -2        +4
    social.declared_nocall    97/112    91/112    97/112      0        +6
    social.voice              90/112    85/112    90/112      0        +5
    social.family             69/112    68/112    67/112     -2        -1
    social.farewell            14/20     13/20     14/20      0        +1
    social.heldout_carrier     10/12     10/12      9/12     -1        -1
    social.self               16/47     10/47     13/47     -3        +3
    social.self_heldout         8/16      7/16      7/16     -1         0
    social.low_family          1/28      6/28      7/28     +6        +1
    social.low_voice          23/28     24/28     25/28     +2        +1
    social.low_declared       16/28     16/28     17/28     +1        +1
    social.low_heldout          0/4       1/4       1/4      +1         0

    declared_nocall why    arm 4  web 6  decline 9 | arm 5  web 12  decline 9 | arm 5b  web 6  decline 9
    social.self why        arm 4  web 27           | arm 5  web 34           | arm 5b  web 31

**The first pre-registered reading fires.** The routing pair is back inside
arm 4's band (the bar was declared >= 95, bare >= 97; it reads 97 and 97),
`voice` is back to 90, and `low_family` holds at 7 -- one above arm 5 --
with one of the four held-out forms still answered. The `web_search` column
on the declared row is arm 4's exact 6. **The class was the whole cost**:
one switch, and every item arm 5 paid comes back while the row the class
was built to buy does not fall.

`social.self` at 13 is one item outside the bar's 16 +/- 2, its `web_search`
31 sitting between arm 4's 27 and arm 5's 34. It is recorded rather than
absorbed: the consolation moves alone lean the router a little on questions
about his life, which is the same boundary as always and three items at
n = 47.

## 2. The gates, against ft4g

    row                     ft4g     arm 4    arm 5b   5b-ft4g
    tool.copy            120/120   120/120   120/120      0
    tool.copy_wide       300/300   300/300   300/300      0
    temporal.copy        353/353   353/353   353/353      0
    refusal.say          270/270   270/270   270/270      0
    tool.selection       198/200   198/200   197/200     -1
    tool.name_fidelity   109/120   109/120   109/120      0
    temporal.route       398/400   398/400   398/400      0
    search.route_*       200/200   200/200   200/200      0   x3
    chat.abstain_talk    100/100   100/100   100/100      0
    chat.engage          100/100   100/100   100/100      0
    chat.abstain_oos      11/100    13/100    11/100      0
    chat.abstain_greet    83/100    93/100    91/100     +8
    tool.note_fidelity   100/120    96/120    97/120     -3
    extract.span          97/200    92/200    93/200     -4
    extract.abstain      111/200   116/200   113/200     +2
    turn2.react          118/120   117/120   116/120     -2
    turn2.reask            66/96     75/96     78/96    +12
    compound.pipe          39/48     41/48     41/48     +2

    grid A, decline            ft4g     arm 2     arm 4     arm 5    arm 5b
      pooled trained         174/176   176/176   176/176   174/176   176/176
      pooled novel             32/32     31/32     29/32     30/32     31/32
    historygrid depth 1, social after a tool turn (control excluded)
                              21/36     26/36     19/36     22/36     22/36
      reissued / frame kept    0 / all   0 / all   0 / all   0 / all   0 / all
    reader proxy (ft4g adapter, fixed t)
      right / u.silent         526/199  524/199   522/196   524/197   524/197
                                                            moved 27, right 9 lost / 4 won

Every frozen copy row at its ceiling and `refusal.say` unmoved, a sixth
time. **Grid A reads arm 2's numbers on the ft4g init** -- trained
176/176, novel 31/32, the one miss `commerce`'s "return the boots" that
every arm has missed -- which arm 4 (29/32) did not; whether that is the
consolation moves helping the boundary or n = 32 wobbling is a second-seed
question, and it is the right direction either way. The post-history
social probe is arm 5's 22/36, three above arm 4.

## 3. Reading

Arm 5b is the base arm 7 stacks on, and it is the best ft4g-lineage
checkpoint on the record: arm 4's rows with the consolation family added
(1 -> 7 of 28), arm 2's grid A, every gate inside its floor. The
consolation family is still supply-limited -- seven of twenty-eight from a
twenty-line pool at two uses each -- and the row that would move it is the
rated pool's 54 lines (finding 120 §4), which is a share question for a
later arm and not this one.

## Limits

One seed. The rows that decide this reading moved by 4-6 items of 112
against arm 5 and by 0-3 against arm 4; `social.self` by 3 of 47. Grid A's
novel column is 32 items. The reader proxy is at a fixed threshold.

## On disk

`evals/results/corn_jr_260m_v4_ft_social5b.json`,
`harness/results/corn_jr_260m_v4_ft_social5b__toolgrid.json`,
`harness/results/corn_jr_260m_v4_ft_social5b__historygrid-0905ctl.json`,
`evals/results/reader_runtime_whole_s1_on_social5b.json`;
`checkpoints/corn_jr_260m_v4_ft_social5b/` (gitignored).
