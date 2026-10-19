# Fine-tuning costs nothing but delivers three fifths of pretraining's gain

**Full result:** The fine-tune spends nothing and delivers three fifths, so the mix wins on efficiency and not on safety

**Cost:** 11.0 min of scoring on the 3 cards first cited here (`nano20m_v3_p3a`, `nano20m_v3_p3a_ft`, `nano20m_v3_seed2`); it also reads 2 cards scored for an earlier finding (`corn_jr_260m`, `nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

P3-A, the vehicle experiment. `configs/nano20m_v3_p3a.py` ×2 against
`configs/nano20m_v3_p3a_ft.py` ×2, both reading the same 45,000,025-byte
payload of real dialogue, both against the committed `nano20m_v3` pair. Trained
2026-08-25: MIX 1,237s a seed, FT 238s a seed. `configs/mix_v3_p3a.py` carries
the pre-registration and it was written before a byte trained.

**The answer is the decision table's outcome 3.** Both arms deliver. Neither
arm spends a copy row. The fine-tune delivers **61%** of what the mix delivers
at equal payload exposure, separating above it by 2.01× the larger within-arm
spread. So the fine-tune vehicle is *safe* and *weak*, and the mix is preferred
on efficiency rather than on the deference argument that motivated the
question.

## What made this a different question from the sixth finding

Finding 6 measured fine-tune against pretraining and found deference does not
fine-tune in — `temporal.copy` 100% pretrained, 82–92% fine-tuned, 48–66% with
replay. That has been the live argument that Phase 3 must be a mix. Its design
was the hardest possible case for a fine-tune in three ways, and this
experiment removed all three at once:

    finding 6                          here
    base had never seen a <|call|>     base is nano20m_v3, fully trained on
                                       the eight-slice mix
    payload was a capability the       payload is new sentences of a register
    base lacked                        the base already has
    replay was narrative only          replay is the v3 mix itself, so the
                                       replayed stream carries the copy-
                                       discipline examples

**Finding 6's direction did not reproduce.** Not weakly — not at all. Every
copy row is flat or up on the fine-tune, and the prose collapse that made that
arm's result arguable is absent: `lm narrative` reads [0.4485, 0.4536] on the
FT arm against a control of [0.4506, 0.4550]. So finding 6 is a result about
installing a capability by fine-tune, and it does not transfer to adding
register over one already installed. That is the sharpest thing this run says.

## The controls reproduced first, and it is 121 of 121 twice

Both `nano20m_v3` and `nano20m_v3_seed2` were **re-scored, not retrained**,
before anything was compared to them. `scripts/rowdiff.py` flattens a scorecard
to its scored quantities — every row's `pass`/`n`, every `lm` nats/byte, both
reply instruments' aggregates — and diffs at zero tolerance:

    nano20m_v3         121 of 121 shared quantities reproduce identically
    nano20m_v3_seed2   121 of 121 shared quantities reproduce identically

The only difference on either card is three rows *gained* — `extract.span`,
`extract.abstain`, `extract.brevity` now sit in the default eval dir and were
not in the committed cards. Nothing that existed moved.

## Delivery — the primary row separates on both arms

`lm conversational`, nats/byte on the reserved tail, unseen by every arm:

| arm | range | spread |
|---|---|---|
| control | [0.5164, 0.5194] | 0.0030 |
| **MIX** | **[0.4908, 0.4928]** | 0.0020 |
| FT `ckpt.pt` | [0.5002, 0.5038] | 0.0037 |
| FT `last.pt` | [0.5002, 0.5025] | 0.0023 |

The registered criterion is both seeds below both control seeds *and* the gap
between ranges exceeding the larger within-pair spread:

    MIX vs control   gap 0.0237   larger spread 0.0030   7.97x   DELIVERS
    FT  vs control   gap 0.0126   larger spread 0.0037   3.43x   DELIVERS
    FT  vs MIX       gap 0.0074   larger spread 0.0037   2.01x   FT is above

**The FT arm is not inert, and that is worth saying because inertness was the
pre-registered way this could have gone wrong.** `docs/PLAN-P3A.md` §9 named it:
786 iterations might move nothing, and an arm that does not deliver has
demonstrated nothing about safety. It delivered — 3.43× the spread clear of the
control — and it still lands materially short of the mix. Against the control
midpoint of 0.5179 the mix buys 0.0262 and the fine-tune buys 0.0159.

## Cost — the pre-registered null, on all three rows and both arms

| row | control | MIX | FT `ckpt` | FT `last` |
|---|---|---|---|---|
| `tool.copy` /120 | [118, 120] | [117, 119] | **[120, 120]** | [120, 120] |
| `tool.copy_wide` /300 | [281, 291] | [283, 295] | [291, 293] | [292, 293] |
| `temporal.copy` /353 | 353/353 | 353/353 | 353/353 | 353/353 |

"Spent" was registered as *arm range strictly below control range, gap greater
than the larger within-arm spread*. No range on either arm is strictly below
control on any row. The fine-tune sits at the ceiling on `tool.copy` and at the
top of the control's range on `tool.copy_wide`.

**Do not read the fine-tune as better at copying.** 120/120 is the ceiling, two
seeds cannot establish a direction against it, and the section below puts the
row's own wobble at nine items.

Watch rows, unregistered and clean on both arms: `refusal.say_unechoed` 55/55
and `refusal.no_guess` 47/47 everywhere, `chat.abstain_talk` 100/100 everywhere,
`temporal.route` 398–399/400, `schema.conform` control [191, 193] against MIX
[193, 194] and FT [191, 195]. `tool.validity` rose on both arms — control
[143, 152], MIX [156, 166], FT [150, 160] — which nothing here predicted and
which is not a registered read.

## `tool.copy` moved nine items in five iterations, and nothing else moved at all

The MIX seed-1338 run selected `ckpt.pt` at iter 5,625 and wrote `last.pt` at
5,630. Both were scored, because a selection argument is answered by
measurement. Five iterations apart:

    lm narrative    0.4491 -> 0.4490      lm web            0.8823 -> 0.8825
    lm temporal     0.1079 -> 0.1074      lm conversational 0.4928 -> 0.4924
    register.conv     80 -> 81            tool.copy_wide     295 -> 296
    tool.copy        119 -> 110           <- ten wrong_answer, up from one

**Every likelihood row moves in the fourth decimal and `tool.copy` moves by
nine of 120**, in the opposite direction to `tool.copy_wide` on the same two
checkpoints. That is a floor on how finely this row can be read, and it is
larger than every arm-to-control gap in the table above. It applies to
PLAN-PHASE-3's rule 10, which names `tool.copy` as one of three standing
regression rows: a swing of under ten items on that row is inside the wobble of
a single run, and only a substantial collapse is readable at two seeds.

This is why the cost side above is written as a null rather than as a ranking.

## The secondaries were unreadable, and one was called that in advance

`register.conv` — control [81, 86], MIX [80, 81], FT [82, 86], FT `last`
[86, 88]. The control's own spread is 5 of 200 and every arm sits inside or
adjacent to it. No direction.

`chat_reply.distinct3` — the control pair spans **0.0363** (0.8641 to 0.9004),
which is wider than any arm-to-control difference here. MIX [0.8761, 0.8817],
FT [0.8697, 0.8934]. The instrument cannot see an effect this size at two
seeds.

The turn2 talk cell was pre-registered as *probably unreadable*, in
`mix_v3_p3a.py`'s docstring, because the two controls disagree in sign
(+0.0150 on 1337, −0.0239 on 1338). They still do, and the arms scatter across
both signs. It stayed unreadable, as written down in advance.

`daycross.with_day` moved a lot — control [29, 62], MIX [67, 93], FT [31, 74].
`docs/PLAN-P3A.md` §9 named it a known-noisy row and forbade it becoming a
headline post hoc. It is not one.

## The searchgrid read is a null about the instrument, and it is a loud one

The pre-registered non-movement: the payload contains no tool utterances, so
`harness/searchgrid.py`'s carried phrasings should not move on any arm, and the
interesting cell was whether the fine-tune *loses* them. All six checkpoints
were run, no `--search`, nothing left the machine.

    kept_subject / 400        ctl 72, 104     MIX 30, 286     FT 133, 98
    templates routing at all  ctl 19, 14      MIX 8, 22       FT 22, 13

**The MIX arm alone spans 30 to 286 of 400 across its two seeds** — an 8.5×
within-arm swing that covers the entire range of every other cell in the table,
including both controls. `search for {q}` reads 0 on one MIX seed and 16 of 16
on the other; `I need to know {q}` reads 0 everywhere except MIX 1338, where it
reads 16 of 16.

So nothing here is readable, by ground rule 6 and by the thirtieth finding's
trap in its plainest form: no arm-to-control difference approaches the
within-arm spread. **The registered non-movement is neither confirmed nor
refuted — the instrument cannot see a change of this size at two seeds at nano
scale**, and that is the finding, not a fact about the arms. Nobody should
quote MIX 1338's 286 as routing improving; its sibling seed is the worst cell
on the board.

The practical consequence is for the instrument rather than for P3-A:
`searchgrid` was built to characterise `corn_jr_260m`, where it reads one
checkpoint carefully. Used as a two-seed regression watch at nano it is
dominated by seed noise, and it should not be added to any arm's registered
reads until something establishes what its floor is. Cards are in
`harness/results/nano20m_v3*__searchgrid.json` for whoever does that.

## What this cannot say

**The payload is real dialogue, not P3-B's tool-utterance phrasings.** A
vehicle verdict here transfers to the phrasing payload by argument, not by
measurement, and the P3-B arm pair carries its own copy-row watch when it runs.

**A larger fine-tune dose is not licensed by this result.** The decision table
says so explicitly and it was written before the numbers: a bigger dose is a new
arm needing its own pre-registration. Nothing here says the delivery gap would
close if the fine-tune ran longer, and the honest reading of a 61% delivery at
equal payload exposure is that the mix gets more out of the same tokens.

**Delivery alone decides nothing.** More same-distribution text lowering
same-distribution loss was nearly assured. The whole informative content is on
the cost side, and the cost side is a null.

**Outcome 3 is silent on the 260M launch order, and the plan did not notice.**
Outcome 1 would have released the 5B corpus from waiting on P3-B data; outcome 2
would have required it. Outcome 3 says only that the mix is favoured on
efficiency — which is a preference, not a constraint on ordering. The launch
order therefore stays open, and it is a decision rather than a measurement now:
either accept the mix on efficiency and freeze P3-B data before the 5B corpus,
or pre-register a larger-dose fine-tune arm. The 260M's extraction-chain gate
(HANDOFF, 2026-08-25 — now `docs/SESSION-ARCHIVE.md`) is untouched by any of this.

## How the arms were kept to one variable

`mix_v3`'s weights sum to exactly its `total_tokens`, so adding weight P and
raising the budget by exactly P leaves every original target identical to the
token. It held on the artefacts, which is where `scripts/check_p3a.py` checks
it: all eight original sources report the same `train_tokens` as `data/mix_v3`
and all eight `val_<name>.bin` files hash byte-identical. The payload's own
split is byte-identical between the two corpora, so both arms read the same
payload tokens in the same order — 9,653,224 expected on the MIX arm against
9,658,368 on the FT arm, 0.053% apart.

Total compute is deliberately unequal and it is the right way round, which is
finding 6's own argument: a real fine-tune is always additional compute over the
base it starts from, so payload exposure is held equal and total tokens are
allowed to differ.

One build detail recorded rather than discovered later: `tools` is 0.31% of the
FT corpus, so its val split is 305 tokens and `Batcher` skips any split shorter
than `block_size`. The mean-log-per-source selection rule averaged eight sources
on the FT arm against nine on the MIX arm and eight on the control. Every copy
row above is scored on the frozen eval set, not on a val split.

`scripts/check_copyable.py`'s undeclared-slice check caught the payload on the
first full sweep after it existed, which is the discipline working exactly as
`DECLARED`'s comment says it should. It is declared with an empty tuple on
`conversational.txt`'s own terms — mined rather than generated, unlabelled
utterances, no field any example asks the model to read back — and with the
cardinality written down anyway: 55,797 distinct openings over 66,445
documents, 1.19 uses each.

Guard count 31 → 32. `python scripts/check_all.py`, 32 ran, 0 skipped.
