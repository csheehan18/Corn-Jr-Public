# Fine-tuning doesn't overwrite what pretraining installed

**Full result:** The fine-tune does not overwrite what the mix installed, and the re-ask band comes back whole

**Cost:** 3.8 min of scoring on the 2 cards first cited here (`nano20m_v3_turn2`, `nano20m_v3_turn2_joint`); it also reads 1 card scored for an earlier finding (`nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Two nano arms trained 2026-08-28 from `configs/nano20m_v3_turn2_joint.py` and
`_seed2.py`: the `mix_turn2_ft` recipe exactly as shipped -- same data dir,
same schedule, same seeds -- with `init_from` pointed at
`nano20m_v3_turn2{,_seed2}/ckpt.pt`, the MIX arm's own checkpoints, instead of
the payload-blind `nano20m_v3`. **Ordered by the owner on 2026-08-27 and
pre-registered the same evening** in `docs/PLAN-TURN-2.md`, with its readings
written before a config existed. Controls are the four existing `nano20m_v3`
seeds and the four turn-2 cards from finding 74; **nothing retrained and
nothing was re-scored**. All three arms are eager -- the signed `compile=True`
is scoped to the H200 family precisely so a read like this one never straddles
the boundary.

## The question, and the honest limit stated first

Finding 74 read React and Chain at parity across the two vehicles and Re-ask
four times better on the mix. The owner declined to sign the §7a deferral that
would have dropped React and Chain from `mix_v4_5b`, stated the prior the
arm would test -- *pretraining exposure is the substrate a capability survives
on, and fine-tuning amplifies what the mix installed* -- and ordered the
deferral's own reopening condition run first.

The limit the pre-registration put in writing: `turn2.react` and both chain
cells sit at or near ceiling on *both* existing vehicles, so **additivity is
unreadable there**. The two cells that separate cleanly are `turn2.reask`
(MIX 57-66 against FT-alone 15-17) and `turn2.reask_yn` (33-38 against 8-11).
Those two carry the read; the ceilings are checked for damage, not for gain.

## The result

`last.pt` reproduces `ckpt.pt` on every cell of both joint cards, and **that is
a tautology here rather than a measurement**: both runs selected best-val at
iteration 551, which is their last, so the two files are the same weights. It
is worth saying out loud because it is not what happened on the arm this one
copies -- three of finding 74's four fine-tunes selected below their final
iteration (525, 525, 455 of 551) and scoring both was not a formality there.
Both cards were scored anyway, on the sixth finding's rule that a selection
argument is answered by measurement; the column is folded in rather than
printed twice.

| cell | control ×4 | MIX ×2 | FT ×2 | **JOINT ×2** |
|---|---|---|---|---|
| `turn2.reask` /96 | 0–0 | **57–66** | 15–17 | **52–68** |
| `turn2.reask_yn` /40 | 0–4 | **33–38** | 8–11 | **32–37** |
| `turn2.react` /120 | 0–9 | 112–117 | 107–108 | 112–116 |
| `turn2.chain_result` /50 | 0–0 | 47–49 | 49–49 | **50–50** |
| `turn2.chain_ellipsis` /50 | 0–6 | 47–48 | 44–44 | 43–46 |
| `turn2.chain_pronoun` /50 | 0–17 | 12–18 | 20–30 | 12–17 |

**The joint arm sits in the MIX band on both readable cells.** `turn2.reask`
reads 52 and 68 against a MIX band of 57-66 -- one seed five items below its
floor, one two items above its ceiling, straddling it. `turn2.reask_yn` reads
32 and 37 against 33-38: one item below the floor and one below the ceiling,
which at n=2 on a 40-item row is the same number. Against FT-alone the gap is
not close: 52 and 68 against 15 and 17, and 32 and 37 against 8 and 11.

Against the pre-registered table this is **"the mix survives"**, on both of the
clauses that outcome was written with: the joint arm holds the MIX band on
`reask` and `reask_yn`, *and* it lands above FT-alone by far more than the seed
spread -- thirty-five items on a row where the FT arm's own two seeds differ by
two. The ceilings are matched rather than spent: react 112-116 against
FT-alone's 107-108 and the mix's 112-117, `chain_result` at a clean 50/50 on
both seeds, `chain_ellipsis` 43-46 against 44 and 47-48, which is a two-item
shortfall on the one cell where the mix was strongest and is not a separation
at this spread.

**What it does not show is addition.** The joint arm does not beat the MIX arm
on `reask`; it equals it. So the reading is the narrower of the two the owner's
prior could have produced: base exposure is *not overwritten* by a fine-tune
over the same payload -- which is what the deferral turned on -- rather than
base exposure plus a fine-tune buying more than either. On these two cells,
with the fine-tune's payload identical to the base's, there was no headroom
left for it to buy.

`turn2.chain_pronoun` is not readable and is reported as such, again: the
control spans 0-17 over four seeds, joint reads 12-17, and finding 61's rule
binds.

## One cell moves, and it is not a turn-2 cell

    tool.selection /200   control 109-130   MIX 174   FT 181-185   JOINT 187-188

Every arm that reads this payload routes better than the control, the fine-tune
vehicle more than the mix, and **the joint arm most of all** -- above both of
its parents on both seeds. It is a small margin over FT-alone (two to seven
items on a 200-item row) and it is the only place in this experiment where
mix-plus-fine-tune reads above fine-tune-alone at all. Worth recording as the
one additive-looking cell and not worth more than that: it is not a registered
cell, and finding 74's own turn-2 arms already moved it 109-130 → 174-185
without a joint arm anywhere.

## The regression set

Read against the FT-alone cards, with the ~10-item `tool.copy` wobble floor:

    tool.copy /120        control 118-120   JOINT 120, 114
    tool.copy_wide /300   control 281-296   JOINT 300, 297
    refusal.say /270      control 261-268   JOINT 262, 260
    temporal.copy /353    control 353/353   JOINT 353, 353
    temporal.route /400   control 396-399   JOINT 398, 398

No bill. The 114 is six items inside the wobble floor and its seed-1 twin is at
ceiling; `copy_wide` is *above* the control range on both seeds, as it was for
every turn-2 arm in finding 74. `refusal.say` at 260 is one item below the
control's four-seed floor of 261, on a row whose own control spread is seven --
noise, and recorded rather than rounded away.

## What this licenses, and who decides it

The joint arm was ordered as the input to a decision and **the decision is not
the implementer's**. `docs/PLAN-5B-SUPPLY.md` §7a's turn-2 deferral is HELD
OPEN with its reopening condition ordered, and this finding is that condition's
output. The §7a entry is untouched.

What the pre-registration says follows from "the mix survives", stated here so
the owner can check the numbers against the sentence they signed rather than
against a paraphrase: *base exposure is not overwritten, the owner's prior
holds, React and Chain ride `mix_v4`, and the held-open deferral dies.* Note
what does not change either way, and it is the thing that matters for the
freeze: **`turn2_v1.txt` rides whole at one pass regardless** -- that is
SIGNED, on Re-ask's strength alone, and the classes share the file by ground
rule 5. The deferral decides what the *finding record* says Phase 3 fine-tunes
must re-install, not what the corpus contains.

## Limits

Two seeds per arm, so directions rather than sizes (rule 6). The two readable
cells are the only ones this design can read, and the pre-registration said so
before the arms existed -- everything else here is a damage check. The joint
arm's fine-tune payload is *identical* to its base's, which is the cleanest
form of the question and also the one least likely to show addition; a joint
arm over a payload the base had only partly seen is a different cell and is not
this one. And these are nano numbers on a policy class where the 260M baseline
carries a substrate the nano control does not (finding 74's `chain_pronoun`
note), so the sizes transfer to the H200 run by argument and not by
measurement.
