# Consolation replies barely move and cost tool routing

**Full result:** The consolation family moves 1 to 6 of 28 and pays six items on each half of the routing pair, every loss `called_web_search` rising through its own mood-prefixed balancing class; and the in-session rater keeps 1,873 of 17,459 lines for a pool 1.44x wider at 1.18x the words, so arm 6 does not run by its own bar

**Cost:** 9.7 min of scoring on the 3 cards first cited here (`corn_jr_260m_v4_ft_social5`, `corn_jr_260m_v4_ft_social5__historygrid-0905ctl`, `corn_jr_260m_v4_ft_social5__toolgrid`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**`corn_jr_260m_v4_ft_social5`, 2026-09-05. PLAN-CONVERSATION §6a on arm 4's
recipe: `init_from` ft4g, `data/raw/social5.txt` at arm 2's share, 1,200
iterations in 1,506 s, best at 1,000 (val 0.5875), social per-source loss
0.7435 -> 0.38. Full batched card, grid A table-backed, historygrid depth 1
under `--multi`, the ft4g adapter read as a proxy (finding 118). Beside it,
the CPU half of arm 6: `scripts/rate_social.py` in its subscription form
-- every one of 17,459 candidate lines rated in-session by this session,
no API key, the decisions file kept beside the rated file.**

## 0. What arm 5's payload was

Six families where arm 4 had five. `scripts/mine_social.py` finds **2,945**
distinct consolation replies over the whole of SODA; the generator keeps
**21** -- 2,768 die on the lexicon, and a consolation-only register of twenty
words (`CONSOLATION_EXTRA`, measured) is what took it from 5 to 21; a
fifty-word list bought 24 with three scene lines. A SODA reply to a low mood
asks what happened, which is the scene. So §6a's own rule applied: the
family rode at its natural share, **55 draws over 20 distinct** in 1,821
pairs, not oversampled into finding 34's regime. Three revisions from arm 3's
generator rode with it on their own merits (the exclusion fix, the scene
rules, the vague-tail carriers), the greeting hello-opener share was bounded
at 30% rather than anchored (141/470 against arm 3's 278/443), and **the
balancing class §6a asked for was built**: `_with_mood` put one of `LOW`'s
short forms in front of a `route` draw's own request -- "rough day, call
Priya" -> `place_call` -- 31 transcripts. Guarded: calibration 0 refused of
104 pool lines; `check_social.py` green with a seventh section.

## 1. The social rows, against arm 4 (the pre-registered bar)

    row                        arm 2     arm 4     arm 5   arm5-arm4
    social.bare_nocall        95/112    99/112    93/112      -6
    social.declared_nocall    99/112    97/112    91/112      -6
    social.voice              89/112    90/112    85/112      -5
    social.family             71/112    69/112    68/112      -1
    social.farewell            14/20     14/20     13/20      -1
    social.heldout_carrier     10/12     10/12     10/12       0
    social.self                13/47     16/47     10/47      -6
    social.self_heldout         8/16      8/16      7/16      -1
    social.low_bare_nocall     14/28     14/28     14/28       0
    social.low_declared        17/28     16/28     16/28       0
    social.low_voice           24/28     23/28     24/28      +1
    social.low_family           2/28      1/28      6/28      +5
    social.low_heldout          0/4       0/4       1/4       +1

**The family moved, and the routing pair paid for it.** `low_family` 1 -> 6
of 28 with one of the four held-out forms answered; the routing pair -6 and
-6, `voice` -5, `self` -6. The species is one thing on every row that fell:

    declared_nocall why    arm 4  web_search 6   decline 9
                           arm 5  web_search 12  decline 9
    bare_nocall why        arm 4  web 4  resolve_date 5  decline 4
                           arm 5  web 8  resolve_date 6  decline 4  send_text 1
    social.self why        arm 4  called_web_search 27   life 1
                           arm 5  called_web_search 34   life 1

`decline` did not move. No life claim moved (`life: i got a` 1 on both).
What moved is `web_search` on turns that should be spoken -- the routing
prior leaning toward a call on a short second-person opener. That is §6a's
second pre-registered reading, "the pool widened onto a neighbour", and the
neighbour is the router.

**The mechanism is the balancing class, and it is named rather than
inferred.** Fifty-five transcripts answer a mood; thirty-one put a mood in
front of a request and answer it with a call. The second class is the
sharper signal of the two -- a call is a longer, more structured
continuation than a one-line say -- and its opener has the social move's
own shape. Arm 1's diagnosis (finding 88's family: `ping me later` is `hey`
with a verb on it) ran the other way: there, short second-person requests
were spoken instead of declined; here, short second-person moves are
called instead of spoken. Same boundary, opposite push, and the push came
from the one class this arm added that no arm before it had.

## 2. The gates, against ft4g

    row                     ft4g      arm 4     arm 5   arm5-ft4g
    tool.copy            120/120   120/120   120/120       0
    tool.copy_wide       300/300   300/300   300/300       0
    temporal.copy        353/353   353/353   353/353       0
    refusal.say          270/270   270/270   270/270       0
    tool.selection       198/200   198/200   197/200      -1
    tool.name_fidelity   109/120   109/120   109/120       0
    temporal.route       398/400   398/400   398/400       0
    search.route_*       200/200   200/200   200/200       0   x3
    chat.abstain_talk    100/100   100/100   100/100       0
    chat.engage          100/100   100/100   100/100       0
    chat.abstain_oos      11/100    13/100     9/100      -2
    chat.abstain_greet    83/100    93/100    91/100      +8
    tool.note_fidelity   100/120    96/120    96/120      -4
    extract.span          97/200    92/200    91/200      -6
    extract.abstain      111/200   116/200   114/200      +3
    turn2.react          118/120   117/120   116/120      -2
    turn2.reask            66/96     75/96     77/96     +11
    compound.pipe          39/48     41/48     39/48       0

    grid A, decline            ft4g     arm 4     arm 5
      pooled trained         174/176   176/176   174/176   media 30/32, both to web_search
      pooled novel             32/32     29/32     30/32
    historygrid depth 1, social after a tool turn (control excluded)
                              21/36     19/36     22/36
      reissued / frame kept    0 / all   0 / all   0 / all
    reader proxy (ft4g adapter, fixed t)
      right / u.silent          526/199   522/196   524/197   moved 29, right 7 lost / 5 won

Every frozen copy row at its ceiling and `refusal.say` unmoved, a fifth
time. The extract lean is arm 4's (the init's). Grid A: two trained
declines lost to `web_search` in `media`, one novel decline recovered --
the same `web_search` lean as the rows, now at n=176. The post-history
social probe reads +3 on arm 4.

## 3. Reading, and the owner's decision

**§6a's second reading, with the cause named.** The consolation moves did
what they could from twenty lines; the class built to balance them taught
the router more than they taught the speaker. The pre-registered response
is "read the species before the next arm", and the species says the
mood-prefixed calls. The owner took the recommendation to **cut the class
rather than dose it**: `corn.socialgen.MOOD_BALANCE` is off, and **arm 5b**
-- arm 5's generator, replies and seed with that one switch flipped -- is
the one-file re-run whose readings `configs/mix_v4_ft_social5b.py`
pre-registers (routing pair back inside arm 4's band and `low_family`
holding at 6 is the class being the whole cost; the pair still down with
`low_family` holding is the moves themselves widening the basin, and the
family's share becomes the variable). Arms 7 and 8 are regenerated on the
5b basis and stack on whichever of 5b's readings fires.

## 4. Arm 6, closed by its own bar -- the rater confirms the lexicon

§6b priced a rater as an API batch job; there is no key on this machine and
none was wanted. The rater is this session: `scripts/rate_social.py
--chunks` cut the 17,459 candidates (every mined line whose words sit in the
453-word probe lexicon after every mechanical rule but the shipped lexicon
and the family tag), views narrowed them to the 11,014 the generator's
rated path could use, and every one was read against §6b's paragraph and
`VOICE.md` -- 1,873 kept, 15,586 refused, 0 unrated. `--assemble` wrote
`data/raw/social_replies_rated.txt` with the decisions file beside it.

    generator pool             arm 5 (lexicon)   rated path (lexicon off, tag off)
      greeting                       279                    387
      wellbeing                      213                    218
      thanks                         629                  1,063
      ack                            103                     63
      consolation                     21                     54
      farewell (untrained)            10                      9
      distinct, total              1,245                  1,794      1.44x
      distinct words                 180                    213      1.18x

**Against §6b's bar of 3x and 3x, that is 1.44x and 1.18x, and the arm does
not run.** The bar was written to keep a null arm off the card, and this is
the null it foresaw: what a rater refuses is what the closed lexicon
refuses -- the scene -- and the register that survives both judgements is
about two hundred words wide. `ack` *shrank* under the rater (103 -> 63),
because the lexicon had been passing acknowledgements that read as a deed
or a promise ("Will do.", "Got it. Thanks."). Consolation widened 21 -> 54,
which is the one family where the rater buys something, and it is recorded
here for the day the family's share is the variable. The rated path stays
in the generator (`--rated`) with the file, so the question can be reopened
without re-rating.

## 5. Two guards that did not exist this morning

Arm 8's first cut put a history call exchange in front of a social pair
whose declaration had never declared the tool it called -- `toolspace`'s
lesson inverted. `scripts/check_social.py` now asserts over **every
transcript in every slice** that each `<|call|>` names a tool its own
declaration line declares, reads balance by the *last* turn (a call in the
history is not what the transcript teaches), and takes only social says
(a say answering a `<|user|>` line directly) to the reply filter. All three
regenerated slices are green under it.

## Limits

One seed per arm, and the numbers that moved are 5-6 items of 112 and 47.
Grid A's trained column moved by two at n=176 and the post-history probe by
three at n=36. The rater is one reader on one day with a written rubric;
the decisions file is the record and a second rater would be the check.
The reader proxy is read at a fixed threshold, attempt rate beside it.

## On disk

`evals/results/corn_jr_260m_v4_ft_social5.json`,
`harness/results/corn_jr_260m_v4_ft_social5__toolgrid.json`,
`harness/results/corn_jr_260m_v4_ft_social5__historygrid-0905ctl.json`,
`evals/results/reader_runtime_whole_s1_on_social5.json`;
`data/raw/social_replies_rated.txt` and `.decisions.tsv` (gitignored);
`checkpoints/corn_jr_260m_v4_ft_social5/` (gitignored).
