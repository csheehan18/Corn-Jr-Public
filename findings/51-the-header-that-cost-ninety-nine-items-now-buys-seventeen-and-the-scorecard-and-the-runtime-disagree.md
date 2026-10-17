# Fifty-first finding — the header that cost ninety-nine items now buys seventeen, and the scorecard and the runtime disagree by forty-eight points

**Cost:** 3.5 min of scoring on the 1 card first cited here (`nano20m_v3`); it also reads 2 cards scored for an earlier finding (`corn_jr_260m`, `nano100m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

No training. `checkpoints/corn_jr_260m` as it stands, scored 2026-08-24 on the
3080 through `python -m corn.evals`, 10 m 50 s wall clock — 416 s of behaviour
generation and 71 s of variety. Written to `evals/results/corn_jr_260m.json`.
Two live arms alongside it, `harness/checkup.py` against the same weights at
temperature 0 without `--multi`, differing only in whether `decline` was
offered.

**This is the first scorecard the 260M has ever had.** There were 222 in
`evals/results/` before it and not one of them was this checkpoint: findings 48,
49 and 50 all drove `corn_jr_260m` through `harness/`, which reports rates over
sixteen or twenty hand-written sentences, and the frozen 400-item instrument the
rest of the project is built on had never been pointed at it.
`260M Run Data/RUN-NOTES.md` closes on exactly this — *"Whether the nano-scale
findings — 34 and 39 above all — reproduce at 260M is the first question the
scorecard should answer."*

## The comparison that is legitimate, and the one that is not

The clean scale contrast is `nano20m_v3` -> `corn_jr_260m`: same corpus recipe
(`mix_v3`, `mix_v3_5b`), 29.6M -> 260.6M, 8.8x the parameters.

**`nano100m_v1` is not part of it, and the row it flatters is the one someone
will quote.** It reads `tool.selection` 181/200 against the 260M's 171/200 — the
smaller model apparently winning at eight times fewer parameters. It trained on
`mix_v1`. `mix_v3` folds in WS-E, and the forty-second finding measured what
that does: offered an escape he over-uses it. The pair differs by corpus and by
policy, not by scale, and it is not a reading.

## `daycross` reverses, which the record predicted the opposite of

| row | `20m_v3` | `20m_v3_seed2` | **260m** |
|---|---|---|---|
| `daycross.no_day` | 128/200 | 129/200 | **171/200** |
| `daycross.with_day` | 29/200 | 62/200 | **188/200** |
| delta | **-99** | **-67** | **+17** |

At nano the `<|day|>` header costs 99 and 67 items. At 260M it **buys 17**.

The fortieth finding recovered 90 of the 126 the header was costing and recorded
that the residue was "still -29 to -63, so this is about half the effect", with
the next doses named. The residue does not shrink at scale — it changes sign,
and no further dose was spent.

This is the row `HANDOFF.md` (now `docs/SESSION-ARCHIVE.md`) singles out as the reason to distrust scale
transfer: *"`daycross` is worse at 91.6M than at 29.6M, so scale transfer is
exactly what none of this assumes."* That caution was correct as stated and
correct to hold; it is now measured wrong at 260M, in the favourable direction,
which is the less common way for a caution to fail.

## Four rows come off the floor, and one becomes readable for the first time

| row | `20m_v3` | `20m_v3_seed2` | **260m** |
|---|---|---|---|
| `tool.name_fidelity` | 46/120 | 56/120 | **106/120** |
| `tool.note_fidelity` | 18/120 | 11/120 | **74/120** |
| `chat.abstain_greet` | 34/100 | 31/100 | **67/100** |
| `chat.abstain_oos` | 6/100 | 0/100 | **33/100** |

The forty-first finding could not read its arm because `tool.name_fidelity`'s
own baseline spread was 31 of 120, wider than any plausible effect. 106 is
outside that band by more than twice its width.

**`notefid` is the one worth the space, because the question it asks was
unaskable at nano.** The row pairs an identical note body asked in a trained
phrasing against an untrained one:

| cell | `20m_v3` | `20m_v3_seed2` | **260m** |
|---|---|---|---|
| `notefid.trained_phrasing` | 18/120 | 11/120 | **74/120** |
| `notefid.novel_phrasing` | 19/120 | 11/120 | **66/120** |

At nano both cells sit on the floor and the gap is 1 and 0 — not a null result,
an unmeasurable one, and the thirty-first finding's complaint about a bucket
whose untreated range touches its own ceiling, committed at the other end. At
260M the gap is **-8 of 120** and the failure mass is `wrong_tool` (26 trained,
31 untrained) rather than a wrong body. The twenty-eighth finding's phrasing
effect is legible on this row for the first time, and it is a routing effect.

## Five rulers are at ceiling

`temporal.route` 400/400, `temporal.copy` 353/353, `tool.copy` 120/120,
`tool.copy_wide` 300/300, `refusal.say` 270/270, `refusal.say_unechoed` 55/55.
Decontamination reads clean on all four sources against `mix_v3_5b`'s
`train.bin` and `val.bin`, which matters because the corpus was rebuilt at 5B
after the eval set was frozen on 2026-08-10.

The forty-sixth finding's caveat on `say_unechoed` carries over unchanged: 55/55
is two sentences seen 902 times, not a capability. The fiftieth finding's is
sharper and applies to the whole block — `tool.copy` draws from an invented
index, so every deference row in the project is measured in the one regime where
nothing in the weights competes with the observation.

## `daylog` does not move, and the failure is silence

| row | `20m_v3` | `20m_v3_seed2` | **260m** | breakdown at 260M |
|---|---|---|---|---|
| `daylog.open` | 0/90 | 14/90 | **4/90** | `no_say` 63, `confabulated` 23 |
| `daylog.targeted` | — | — | **4/84** | `no_say` 48, `confabulated` 31 |
| `daylog.empty` | 0/26 | 0/26 | **0/26** | `no_say` 26 |

Scale bought nothing here, and `daylog.empty` is a hard zero at every size this
project has trained. The breakdown is the part that was not known: it is
dominated by **silence**, not by invention. He emits the call, receives the
observation, and says nothing.

That is precisely the class `corn/agent.py`'s fallback exists for —
`scripts/check_agent.py` asserts *"a day he failed to read back is read back
rather than dropped"* — so these rows should understate the assembled system.
**This run could not confirm that**; see below.

## The scorecard says 85.5% and the runtime says 37.5%

`harness/checkup.py` against the same weights, temperature 0, **without
`--multi`**:

| row | live |
|---|---|
| routed | **6/16 (37.5%)** |
| executed | 6/11 |
| spoke_from_tool | 10/10 |
| held_back | 3/5 |

Against `tool.selection` 171/200 (85.5%) and `temporal.route` 400/400 on the
frozen set. Ten of sixteen live turns went to `decline`, including three plain
`save_note` requests, one `resolve_date`, both `recall_day` turns and both
`ask_claude` turns.

**The live number is not new and should not be reported as a discovery.** The
forty-eighth finding published `routed` 4/16 -> 5/16 across its own fixes and
wrote the honest headline itself: *"the fixes did not teach him to route."*
`executed` 6/11 and `spoke_from_tool` 10/10 reproduce that run exactly. The 6/16
here is **not** an improvement on its 5/16 — that run used `--multi` and this one
did not, so the two differ by a flag and the difference is one turn.

What is new is the other half of the pair. Until today there was a live rate and
no scorecard on the same weights, so the gap could not be stated as a quantity.
**It is 48 points.**

Two explanations were already in the file:

  * **The twenty-eighth finding.** Routing collapses on wording no generator
    emits. `checkup.py`'s cases are hand-written sentences; `evals/`'s 200 are
    generated. The `notefid` cross above shows the same effect, same direction,
    on a frozen set — -8 of 120 there against -48 points here.
  * **The forty-second finding.** Offered `decline` he over-uses it, and
    `ABSENT_SHARE` is 35% and was never tuned.

## Withholding the escape buys back five of the sixteen

The same sixteen cases, same weights, same temperature, `--no-decline`:

| row | `decline` offered | **withheld** |
|---|---|---|
| routed | 6/16 (37.5%) | **11/16 (68.8%)** |
| executed | 6/11 | **11/11 (100%)** |
| spoke_from_tool | 10/10 | 4/5 |
| held_back | 3/5 | **4/5** |

**The forty-second finding's over-declining dominates the live gap, and the
twenty-eighth's phrasing effect is at most the remainder.** The single clearest
receipt is one turn run twice, byte-identical input:

    decline offered   note down pick up the dry cleaning
                      -> {"name": "decline", "arguments": {}}
                      -> "Nothing I've got covers that."

    withheld          note down pick up the dry cleaning
                      -> {"name": "save_note", "arguments":
                          {"text": "pick up the dry cleaning"}}
                      -> {"status": "saved", "chars": 24}   "Noted."

`ABSENT_SHARE` at 35%, never tuned, is now the highest-value untuned number in
the project, and the bracket `HANDOFF.md` (now `docs/SESSION-ARCHIVE.md`) has carried as open item 2 since the
forty-second finding has a 260M receipt rather than a nano one.

**What it costs is visible in the same table.** `spoke_from_tool` falls from
10/10 to 4/5, and the misses change shape: with no escape he routes to the wrong
tool rather than to none, and `save_note` is the sink — `resolve_date` ->
`save_note`, `ask_claude` -> `save_note`, and "turn the heating up" ->
`save_note`, answered "Noted." This is a policy trade, not a repair, and
`--no-decline`'s docstring already says what it is: a measurement, not a setting.

## What neither run could settle, and the sharper reason why

Both were started to test whether `corn/agent.py`'s fallback rescues the
`no_say` rows above. **Neither answers it**, and the second failed for a more
interesting reason than the first.

| policy | `what did I note down today` | `what was I doing on the 14th` |
|---|---|---|
| `decline` offered | -> `decline` | -> `decline` |
| withheld | -> `resolve_date` | -> `web_search` |

**`recall_day` is never selected live, under either policy** — four attempts,
four different wrong destinations. The fallback needs an observation to speak
from, and no observation ever arrives.

That makes the `daylog` block above sharper than it first reads. Those rows
score `prompt_after`: the call and the observation are supplied, and what is
measured is the speech that follows. **So the scorecard measures a stage the
runtime never reaches for that tool**, and its 4/90 is an upper bound on a
capability whose live rate is zero for a reason the scorecard cannot see. It is
the forty-eighth finding's lesson once more — a scorecard that starts after the
call cannot see a call that is never made.

## One number in passing

Latency over the sixteen turns: median **351 ms** / p90 542 ms with `decline`
offered, median **384 ms** / p90 570 ms without. VISION §3 budgets the whole
round trip at 500 ms. It holds at the median in both arms and at p90 in neither,
on a checkpoint whose constraint costs were fixed in the forty-eighth finding —
and the arm that routes more is the slower one, because a turn that declines is
a turn that does no work.
