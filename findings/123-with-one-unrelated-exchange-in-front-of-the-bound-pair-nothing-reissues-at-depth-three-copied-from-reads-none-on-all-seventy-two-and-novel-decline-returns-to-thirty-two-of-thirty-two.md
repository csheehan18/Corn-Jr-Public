# Hundred-and-twenty-third finding — with one unrelated exchange in front of the bound pair on half the two-turn pairs, nothing reissues at depth 3, `copied_from` reads `none` on all 72, the social probe rises, the turn-2 rows hold, and novel decline returns to 32 of 32

**Cost:** 9.7 min of scoring on the 3 cards first cited here (`corn_jr_260m_v4_ft_social8`, `corn_jr_260m_v4_ft_social8__historygrid-0905ctl`, `corn_jr_260m_v4_ft_social8__toolgrid`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**`corn_jr_260m_v4_ft_social8`, 2026-09-05. PLAN-CONVERSATION §6d at the depth
the runtime holds: arm 7's generator, replies and seed with `--depth 2` --
half the two-turn pairs get one unrelated finished exchange (a `toolspace`
call turn with its tools unioned into the pair's declaration, or a single
social exchange) in front of the bound pair, shared by both halves. Depth
draws over {1, 2} because neither the fold nor the reserve ships on by
default and depth 3 survives the shipped trimmer 2% of the time (the
(second) section, finding 128). `init_from` ft4g, arm 2's share, 1,200
iterations in 1,507 s, best at 1,000 (val 0.5872). Full batched card, grid
A, historygrid at depth 1 and depth 3, the ft4g adapter as a proxy.
Decision 9 was taken by the owner's "continue up to 8".**

## 1. The second-turn rows -- §6d's pre-registered readings, against arm 7

    historygrid, seed 0                        arm 2    arm 7    arm 8
      depth 3  reissued_query, lookup_ok         1/12     1/12     0/12
               reissued_query, lookup_fail       1/12     0/12     0/12
               reissued_query, lookup_pack       1/12     1/12     0/12
               reissued_utterance, any arm       1/12     1/12     0/12
               copied_from                     b3 d1    b2 d1    none 72
               social after a tool turn        22/36    23/36    24/36
               adjacent_frame_kept             all      all      all
      depth 1  social after a tool turn        26/36    26/36    28/36
               social_nocall, reissued          0/12     0/12     0/12
               copied_from                     b1       b1       none 72

    the frozen second-turn and compound rows      arm 7     arm 8
      turn2.react                               117/120   120/120
      turn2.reask                                79/96     77/96
      turn2.reask_yn                             22/40     20/40
      turn2.second                              198/200   198/200
      compound.pipe                              40/48     40/48
      compound.items                             30/48     29/48

**The go reading, verbatim.** `reissued_utterance` and `reissued_query`
are at or under arm 7's on every history arm -- they are zero -- and
`copied_from` shows no rise in `distractor`; it shows nothing at all, on
the one grid where the two turns are different strings. The kill did not
fire: the social probe rose rather than fell (+2 at depth 1, +1 at depth
3) and the turn-2 rows are inside a point of arm 7, `react` at its
ceiling. The frame is kept everywhere. **The relation generalised off its
position**: taught with the bound turn not always the turn before, he
copies from neither.

Read against what the grid can say: `copied_from` moved 3 -> 0 of 72 on
the checkpoint that copies (finding 128's arm 2 read 4), so the effect is
the size the (second) section predicted -- "a one-card question with a
small expected effect on this grid" -- and in the direction the arm was
built for. The live session that copied more than the grid does is the
place it would show larger, and it has not been re-run.

## 2. The social rows, against arm 7

    row                        arm 7     arm 8   8-7
    social.bare_nocall       102/112   103/112   +1
    social.declared_nocall   111/112   111/112    0
    social.voice              99/112    96/112   -3
    social.family             71/112    72/112   +1
    social.farewell            16/20     12/20   -4
    social.heldout_carrier     11/12     11/12    0
    social.self               18/47     17/47   -1
    social.self_heldout         7/16      6/16   -1
    social.low_bare_nocall     16/28     19/28   +3
    social.low_declared       26/28     26/28    0
    social.low_voice          27/28     23/28   -4
    social.low_family         11/28     13/28   +2
    social.low_heldout          1/4       3/4    +2

The routing pair holds at arm 7's (the declared row's one call is still
`decline`), `family` and `low_family` edge up, and three of the four
held-out consolation forms are answered. The costs are on the voice rows:
`voice` -3 of 112, `low_voice` -4 of 28, `farewell` -4 of 20 -- the
farewell row is the untrained transfer row at n = 20 and has read 12-16 on
every arm since arm 2; the other two are inside their seed noise and are
watched rather than banked. `social.self`'s species is arm 7's (finding
122 §4): `web_search` 17, spoken leaks 8 -- decision 8's residue,
unchanged by this arm.

## 3. The gates, against ft4g

    row                     ft4g     arm 7     arm 8   8-ft4g
    tool.copy            120/120   120/120   120/120     0
    tool.copy_wide       300/300   300/300   300/300     0
    temporal.copy        353/353   353/353   353/353     0
    refusal.say          270/270   270/270   270/270     0
    tool.selection       198/200   196/200   196/200    -2
    tool.name_fidelity   109/120   109/120   109/120     0
    temporal.route       398/400   398/400   398/400     0
    search.route_*       200/200   200/200   200/200     0   x3
    chat.abstain_talk    100/100   100/100   100/100     0
    chat.engage          100/100   100/100   100/100     0
    chat.abstain_oos      11/100    10/100    12/100    +1
    chat.abstain_greet    83/100    92/100    95/100   +12
    tool.note_fidelity   100/120    94/120    97/120    -3
    extract.span          97/200    92/200    91/200    -6
    extract.abstain      111/200   111/200   110/200    -1

    grid A, decline           ft4g     arm 7     arm 8
      pooled trained        174/176   175/176   175/176
      pooled novel            32/32     31/32     32/32   "snooze that for ten" declines again
    reader proxy (ft4g adapter, fixed t)
      right / u.silent       526/199   524/195   526/195   moved 26, right 5 lost / 5 won

Every frozen copy row at its ceiling and `refusal.say` unmoved, an eighth
time. `chat.abstain_greet` reads 95, the best on the record. **Grid A's
novel column is back at ft4g's 32 of 32** on an ft4g-init arm, which arm 4
read at 29; the one trained miss is arm 7's `media` decline. The extract
lean is the init's and inside the floor. The ft4g adapter read on this
trunk is ft4g's own 526, five lost and five won.

## 4. Reading

**§6d's go reading, and the last arm of the plan lands.** Arm 8 carries
everything the arms before it bought -- the declared social turn at
111/112, the consolation family at 13/28 from twenty lines, the second
turn with nothing reissuing -- and adds the one thing no arm before it
could show: on the grid where "the turn before this one" and "turn 1" are
different strings, he copies from neither. It is the trunk the reader is
re-fit on (the seventh section's four steps, running as this is written)
and the shipping candidate, with the two decisions that stay the owner's:
the reader flag (7) and the routed say on questions about his life (8).

## Limits

One seed. The depth-3 columns are 12 items an arm and `copied_from` is 72
probes; the social probe is 36. `farewell` is 20 items. The reader proxy
is at a fixed threshold; the re-fit's own read is the number that ships.

## On disk

`evals/results/corn_jr_260m_v4_ft_social8.json`,
`harness/results/corn_jr_260m_v4_ft_social8__toolgrid.json`,
`harness/results/corn_jr_260m_v4_ft_social8__historygrid-0905ctl.json` and
`-depth3.json`, `evals/results/reader_runtime_whole_s1_on_social8.json`;
`checkpoints/corn_jr_260m_v4_ft_social8/` (gitignored).
