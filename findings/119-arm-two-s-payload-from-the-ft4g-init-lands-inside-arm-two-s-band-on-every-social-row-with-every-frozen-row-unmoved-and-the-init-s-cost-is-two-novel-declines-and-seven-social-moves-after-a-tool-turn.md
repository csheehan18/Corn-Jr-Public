# Fine-tuning from the shipped base: frozen scores hold, small social costs

**Full result:** Arm 2's payload from the ft4g init lands inside arm 2's band on every social row with every frozen row unmoved, the square says arm 3's family drop was the hello anchoring and the extract lean is the init, and the init's cost is two novel declines of 32 and seven social moves of 36 after a tool turn

**Cost:** 9.6 min of scoring on the 3 cards first cited here (`corn_jr_260m_v4_ft_social4`, `corn_jr_260m_v4_ft_social4__historygrid-0905ctl`, `corn_jr_260m_v4_ft_social4__toolgrid`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**`corn_jr_260m_v4_ft_social4`, 2026-09-05. PLAN-SOCIAL-SLICE's 2026-09-03
arm, re-specified for the shipped reader in PLAN-CONVERSATION's seventh
section: `init_from` ft4g, `data_dir` arm 2's own `data/mix_v4_ft_social2/`
(arm 2's payload to the byte; verified in the checkpoint's config before
anything was scored), every other field arm 2's verbatim. 1,200 iterations in
1,498 s on an idle 3080 (ENVIRONMENT's 1,502 s for this shape), best at 1,000
(val 0.5873, mean-log-per-source), social per-source loss 0.6554 -> 0.3794. Full batched card, grid A table-backed, historygrid depth 1
under `--multi`, and the ft4g adapter read on the trunk as a proxy through
`probe_reader_runtime.py --adapter-trunk` (finding 118). Card serialised: the
grids ran on a server at port 8766 with an empty `--config`, no packs, `--no-
log`; the probe and the next arm's launch waited for each other.**

## 0. The square, completed

    arm        init          payload        social.family   declared_nocall   bare_nocall
    arm 2      v4 base       arm 2's        71/112  63.4%   99/112  88.4%     95/112  84.8%
    arm 3      ft4g          revised        65/112  58.0%   96/112  85.7%     95/112  84.8%
    arm 4      ft4g          arm 2's        69/112  61.6%   97/112  86.6%     99/112  88.4%

**Arm 4 against arm 2 isolates the init at fixed payload: -2, -2, +4.** Arm 4
against arm 3 isolates the payload at fixed init: +4 on `family`, and the
species says which payload defect it was -- `answers greeting` **14 -> 2**,
which is the hello anchoring arm 3's read attributed the drop to on species
evidence. That attribution is now a measurement, and the revised generator's
hello-opener share is bounded rather than anchored from arm 5 on.

## 1. The social rows, against arm 2 (the widened ruler, -0905 cards)

    row                        ft4g     arm 2     arm 3     arm 4   arm4-arm2
    social.bare_nocall        53/112    95/112    95/112    99/112      +4
    social.declared_nocall    39/112    99/112    96/112    97/112      -2
    social.voice              59/112    89/112    93/112    90/112      +1
    social.family             53/112    71/112    65/112    69/112      -2
    social.farewell            11/20     14/20     13/20     14/20       0
    social.heldout_carrier     10/12     10/12     10/12     10/12       0
    social.self                 7/47     13/47     16/47     16/47      +3
    social.self_heldout         3/16      8/16      8/16      8/16       0
    social.low_bare_nocall     11/28     14/28     14/28     14/28       0
    social.low_declared        7/28     17/28     16/28     16/28      -1
    social.low_voice          17/28     24/28     23/28     23/28      -1
    social.low_family          0/28      2/28      1/28      1/28      -1
    social.low_heldout          0/4       0/4       0/4       0/4       0

    declared_nocall's why    ft4g  decline 47 web 26 | arm 2  decline 9 web 4 | arm 4  decline 9 web 6

Every row is inside two items of arm 2 except `bare_nocall` (+4) and
`social.self` (+3), both up. The declaration's effect stays reversed
(declared 97 against bare 99). `social.family`'s residue is arm 2's shape --
`no family marker` 20, `answers wellbeing` 8 -- not arm 3's. **The first
pre-registered reading fires on the rows**: the ft4g init is free on
everything the eval files measure.

## 2. The gates, against ft4g

    row                     ft4g     arm 2     arm 3     arm 4   arm4-ft4g
    tool.copy            120/120   120/120   120/120   120/120       0
    tool.copy_wide       300/300   300/300   300/300   300/300       0
    temporal.copy        353/353   353/353   353/353   353/353       0
    refusal.say          270/270   270/270   270/270   270/270       0
    tool.selection       198/200   198/200   197/200   198/200       0
    tool.name_fidelity   109/120   109/120   109/120   109/120       0
    temporal.route       398/400   398/400   398/400   398/400       0
    search.route_*       200/200   200/200   200/200   200/200       0   x3
    chat.abstain_talk    100/100   100/100   100/100   100/100       0
    chat.engage          100/100   100/100   100/100   100/100       0
    chat.abstain_oos      11/100    12/100    11/100    13/100      +2
    chat.abstain_greet    83/100    93/100    90/100    93/100     +10
    tool.note_fidelity   100/120   101/120    97/120    96/120      -4
    extract.span          97/200    99/200    91/200    92/200      -5
    extract.abstain      111/200   107/200   116/200   116/200      +5
    turn2.react          118/120   120/120   116/120   117/120      -1
    turn2.reask            66/96     77/96     76/96     75/96      +9
    compound.pipe          39/48     39/48     40/48     41/48      +2

**Every frozen copy row at its ceiling and `refusal.say` unmoved** -- finding
49's named risk paid at zero a fourth time. `tool.selection` is ft4g's exact
198. **The extract lean reproduces to the item** (arm 3 91/116, arm 4
92/116) with arm 2's payload, so the 2026-09-03 section's third reading
fires: the lean is the second pass over ft4g's own payload and not arm 3's
labelling. -5 / +5 of 200 is inside finding 60's floor, and the proxy reader
read below is the direct measurement of whether it matters to the reader.

## 3. Where the init costs, and it is two small grids in opposite directions

    grid A, decline           ft4g     arm 2     arm 3     arm 4
      pooled trained        174/176   176/176   176/176   176/176
      pooled novel            32/32     31/32     30/32     29/32
        media                   8/8       8/8       8/8       7/8
        commerce                8/8       7/8       7/8       7/8
        timers_alarms           8/8       8/8       7/8       7/8
        smart_home              8/8       8/8       8/8       8/8
      total                 206/208   207/208   206/208   205/208
      misses reached        web x2    (nothing)  (nothing)  (nothing) x3

    historygrid depth 1, social probe (social_answered, control excluded)
                            ft4g     arm 2     arm 3     arm 4
      six history arms      21/36     26/36     23/36     19/36
      social_nocall arm       6/6       6/6       6/6       6/6
      reissued_utterance      0         0         0         0
      adjacent_frame_kept   all       all       all       all

**Novel decline reads 29/32 against the pre-registered bar of 31**, one miss
in each of three categories, every miss the arm 1 species -- he spoke instead
of calling `decline`. Trained decline is perfect and `tool.selection` is
unmoved, so this is not finding 67's see-saw; it is the pronoun-object
boundary wobbling at n=8 a cell, and arm 4 does not carry arm 3's vague-tail
carriers (arm 2's payload predates them), so the expected reading there was
arm 2's, not arm 3's. **And after a tool turn, a social move is answered 19
times in 36 against arm 2's 26** -- the opposite direction: he calls where
he should speak. The frame holds and nothing is reissued; what moves is the
speak/call boundary under a history, which is finding 128's "a tool turn
costs the next social move" number, seven items worse on this init.

Both are one seed at n = 32 and n = 36, and both point the same way as arm
3 against arm 2 (30/32, 23/36). Three ft4g-init reads against one base-init
read is a direction, not a size: **the ft4g init costs a few items on the
speak/call boundary under the two grids that probe it, and nothing on the
eval files.**

## 4. The reader, read as a proxy

    trunk under the ft4g adapter    right  wrong  silent   u.silent  attempt   moved  right lost/won
    ft4g (finding 117)               526    122     73        199     89.9%
    arm 3 (finding 118)              521    130     70        196     90.3%     27      8 / 3
    arm 4                            522    131     68        196     90.6%     30      8 / 4

Finding 118's expectation holds: arm 4's trunk reads the shipped adapter
within four right answers and three silences of ft4g, the same as arm 3, and
the extract lean in §2 did not reach the reader. The re-fit is not run on
this arm; it waits for the last trunk.

## 5. Reading

**Arm 4 lands on the first pre-registered reading for the rows and misses
grid A's novel bar by two.** The ft4g init is free on every eval row, costs
two novel declines and seven post-history social moves on the grids, and
reproduces arm 3's extract lean without arm 3's payload -- so that lean is
the init's and is inside the floor. The square attributes arm 3's family
drop to its greeting tag, which arm 5's generator bounds instead of anchors.

What this does not decide is which checkpoint ships: arm 2 is still the
stronger social checkpoint on the two grids, and the reason to prefer an
ft4g-init trunk -- the reader's heads were fit on ft4g -- is weaker than it
was, because finding 118 read the adapter on arm 2's trunk at 524/199. The
plan's rule stands (every arm inits from ft4g and stacks on the one before),
arm 5 is training on it, and the shipping choice is the owner's after the
arms are read.

## Limits

One seed per arm. Grid A's novel column is 32 items and moved by 2; the
historygrid social probe is 36 and moved by 7; neither is a number to quote
without the second seed the config family has asked for since arm 1. The
vague-tail battery was not run on this arm -- its expected reading is arm
2's 5 of 22, and the battery has no script. No per-family split of
`social.family` was decoded for this arm; the species column is what says
its residue is arm 2's shape.

## On disk

`evals/results/corn_jr_260m_v4_ft_social4.json`,
`harness/results/corn_jr_260m_v4_ft_social4__toolgrid.json`,
`harness/results/corn_jr_260m_v4_ft_social4__historygrid-0905ctl.json`,
`evals/results/reader_runtime_whole_s1_on_social4.json`;
`checkpoints/corn_jr_260m_v4_ft_social4/` (gitignored).
