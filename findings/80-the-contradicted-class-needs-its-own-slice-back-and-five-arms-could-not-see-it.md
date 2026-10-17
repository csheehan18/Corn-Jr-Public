# Eightieth finding — the class installs every time, and what buys back the class it contradicts is that class's own slice

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Entry 4 of `docs/PLAN-FINETUNE-V4.md` — a bare unmarked question after a lookup
turn, the class the corpus has **0 of 849** of — trained four times on
`corn_jr_260m_v4` between 2026-08-30 and 2026-08-31, seven arms across six
configurations. **Every arm installed the class completely. Every arm was
discarded.** The rows they spent were different each time, and it took the last
two arms to find out why — the first five moved two variables together and
could not tell them apart.

    arm 1  mix_v4_ft_4    unpaired payload   turn2 0.070%   786 it   2 seeds
    arm 2  mix_v4_ft_4b   matched pairs      turn2 1.684% 1,212 it   2 seeds
    C      mix_v4_ft_4c   matched pairs      turn2 1.436% 1,422 it   1 seed
    D      mix_v4_ft_4d   matched pairs      turn2 1.196% 1,706 it   1 seed
    E      mix_v4_ft_4e   ellipsis pairs     turn2 1.684% 1,200 it   1 seed
    F      mix_v4_ft_4f   unpaired payload   turn2 1.684%   799 it   1 seed

**F is the arm that answers it, and it is arm 1 with one thing changed.**

---

## 1. The class installs totally, and finding 74's discount does not appear

`harness/historygrid.py` on the base against every arm, same settings, same
before-cards read hours earlier on the same machine:

    cell                          base    every arm
    attribute after lookup_ok      2/8       8/8
    attribute after lookup_fail    2/8       8/8
    attribute after lookup_pack    0/8       8/8
    arithmetic after a lookup      0/4       4/4
    splice column, pack history    4/8       0/8
    6b wrote-when-not-asked        4/4       0/4
    the empty-room control         8/8       8/8  (unmoved)

Every re-issue column and every splice column zero. **Finding 74 measured a 4x
fine-tune discount on exactly this family and pre-registered it as the expected
shape; it appeared on none of the four arms.** Partial installation was the
prediction. Total installation is the result, four times.

## 2. Copy discipline is never what a fine-tune of this base spends

`tool.copy` 120/120, `tool.copy_wide` 300/300, `temporal.copy` 353/353,
`refusal.say` 270/270 and live `searchgrid` 400/400 on every checkpoint of
every arm. Finding 75's "ceilings matched rather than spent" survives four more
arms.

**What gets spent is routing priors**, and the clearest single number is arm 1's
`turn2.chain_pronoun` failure mode moving from `wrong_message: 10` on the base
to `wrong_tool: 13, wrong_message: 8` on the arm. The tool choice relocated;
the copying did not.

## 3. The inverse class is recoverable, and matched pairs do it alone

Arm 1's payload was "turn 2 shares no content word with turn 1" at 50% of the
arm, against a replay carrying `turn2` at 13,731 tokens — **715:1** — and it
took `turn2.chain_ellipsis` from 49/50 to **7/50**.

Arm 2 rebuilt the payload as matched pairs: one first exchange, two
transcripts, the four lines above them byte-identical, so the second turn is
the only thing that can predict the behaviour. That is `corn/turn2gen.py`'s own
rule-5 construction and P3-E's matched share, which
`docs/PLAN-FINETUNE-V4.md`'s interference note had already named as the remedy
for entries 2, 2b and 6c.

    chain_ellipsis    base 49/50    arm 1  7/50    arm 2 48-50/50    C 49/50    D 47/50
    chain_pronoun     base 40/50    arm 1 29/50    arm 2 39-40/50    C 38/50    D 39/50
    chain_result      base 50/50    arm 1 45/50    arm 2    50/50    C 50/50    D 50/50

**This section said the matched pair holds the chain family on its own. That
was wrong, and §8 is the arm that shows it.** The chain rows do not move across
a general-replay share from 29.6% to 50% — but every one of those arms also
carried a 36x boost to the replay's `turn2` slice, arriving at the same moment
as the matched payload, and the sweep held that top-up fixed. Two explanations,
never separated.

## 4. The prediction this finding first existed to record as false

After arm 2, `docs/PLAN-FINETUNE-V4.md`'s regression-set section was amended to
say the missing rule was **a floor on the general replay**. The reasoning: arm
1 held `tool.name_fidelity` at 112/120 with the general replay at 50% of the
arm and `tools_5b_balanced` at 0.293% of it; arm 2 lost it to 108/120 at 29.6%
and 0.174%. The controlling variable looked like a slice's fraction of the arm.

C and D were built to bisect that, with **both endpoints already measured** —
D lands `tools` on 0.293%, arm 1's fraction to three figures.

    tools % of arm    0.293    0.174    0.235    0.293
                      arm 1    arm 2      C        D
    name_fidelity     112      108      106      106

**It got worse, monotonically, as the replay grew.** D sits at the identical
slice fraction arm 1 held and reads six items below it. So the *general* replay
share is not the knob for this row, and the amendment made after arm 2 is wrong
in the quantity it named.

**But the floor is real and §8 finds it in the right quantity.** What matters is
not the general replay's share, nor a slice's share in the abstract, but **the
share of the specific slice carrying the class the payload contradicts.** This
section measured `tools`, which carries nothing this payload contradicts. §8
measures `turn2`, which carries the class it does.

**What the sweep held constant is what actually separates arm 1**: the payload.
Arm 1 trained `ft4_secondturn.txt`; arms 2, C and D trained `ft4_matched.txt`.
The matched payload carries the `chain_result` twin — **31,051 transcripts
whose second turn writes a `save_note` copying turn 1's answer** — and
`tool.name_fidelity` scores an argument value written into a telephony slot.
Both are "put the right value in the slot". That is a mechanism worth testing
with one variable (the matched payload minus its `chain_result` twin) and it is
**a hypothesis, not a result**; nothing here demonstrates it.

## 5. What did behave as predicted, and one thing that fits nothing

`configs/mix_v4_ft_4c.py` pre-registered that `react` is payload-limited rather
than replay-limited, on the evidence that arm 2's 24x increase in `turn2` bought
one item. It held:

    turn2 % of arm    0.070    1.684    1.436    1.196
                      arm 1    arm 2      C        D
    react             116      117      118      118    (base 120)

A 24x swing in the slice that teaches the class moves it two items and never
reaches the ceiling. Every one of the 97,043 transcripts in `ft4_matched.txt`
has a second turn that **calls** something; `react` is the class whose second
turn calls nothing. The repair, if one is wanted, is a payload carrying no-call
second turns — not a replay share.

**The counter-evidence, recorded because it fits neither story:**
`turn2.reask` is *also* a no-call class and it went **up** — 40/96 on the base,
49 on arm 1, 55-62 on arm 2, 49 on C, 57 on D. Whatever separates `reask` from
`react` under this payload is not named by anything above.

## 6. Two rules that collided, and one premise that is false

Ground rule 15 calls `say`, `daycross` and `namecollide` free invariance
controls "because no payload arm touches their inputs". Ground rule 14 now asks
every arm to choose its own replay, and these four chose `mix_v4_5b`'s slices —
which carry `temporal` and `daylog`, the two slices `daycross` is scored out of.
`daycross.with_day` moved on every arm (118 base; 134, 113, 122, 138) and the
movement tracks the replay share rather than anything the payload did.

So **the premise under rule 15's invariance controls does not hold for a
v4-slices replay**, and `configs/mix_v4_ft_4b.py` pre-registered that before
training rather than arguing it afterwards, which is the only reason `daycross`
did not invalidate three separate reads. `refusal.say` is the one control that
stayed genuinely free: 270/270 everywhere.

## 7. What this leaves

The vehicle question entry 4 was chosen to answer is answered, and more
favourably than the entry expected: **a fine-tune of this base installs a
missing class completely, at ~16-36 minutes an arm, without spending copy
discipline.** What no arm has yet done is ship, because each spent a routing
row through its payload's *content* — which is a harder thing to predict than a
share and a more tractable one than a property of the vehicle, since content is
chosen deliberately.

The regression set grew twice on this evidence: `turn2.chain_ellipsis`,
`turn2.chain_result` and `turn2.react` after arm 1, and all three earned
themselves back immediately — `react` is what discarded arm 2, and a set that
had not just grown would have passed it.

Costs, for the next person budgeting: an arm is 964s at 786 iterations and
2,169s at 1,706, uncontended on the 3080 at ~23k tok/s. The first arm of this
sequence read 6,963s because a guard sweep was running beside it, which also
stretched that sweep from 417s to 3,447s. Neither number meant anything.

---

## 8. The separating arm, and the claim it overturns

Sections 3 and 4 were written from five arms in which **the matched payload and
a 36x boost to the replay's `turn2` slice always arrived together**. §3 credited
the matched pair. Arm E is what exposed the confound: it pre-registered that
`turn2.chain_result` *must* fall once its training class was removed from the
payload, and `chain_result` read **49/50 with zero `chain_result` transcripts in
the payload**. A class that survives the deletion of its payload is being held
up by something else.

F separates them. It is `configs/mix_v4_ft_4.py` to the token — same
`ft4_secondturn.txt`, same 9,820,078-token payload weight, same 19,640,156-token
budget — with `turn2` and `compound_v2` raised to the share every recovering arm
had, the general replay absorbing the cost:

    payload            arm 1 unpaired      F unpaired      arm 2 matched
    turn2 % of arm         0.070             1.684            1.684
    chain_ellipsis          7/50             45/50            48/50
    chain_result           45/50             50/50            50/50
    chain_pronoun          29/50             38/50            39/50
    react                 116/120           119/120          117/120

**The boost is the whole effect: 7 → 45 of the 41 items available, with the
payload byte-identical.** The matched pair adds three more. So §3's claim that
"matched pairs do it alone" is **wrong**, and the honest ordering is that the
replay does nearly all of it and the matched pair is a refinement.

**And the floor §4 declared non-existent is real, in a quantity §4 did not
test.** §4 swept `tools`, which carries nothing this payload contradicts, and
found no floor. `turn2` carries `chain_ellipsis`, `chain_result` and `react` —
the classes this payload's "every second turn is unrelated and calls" directly
contradicts — and boosting it recovers all three. **The rule is per-class: when
a payload teaches a class that contradicts a trained one, the contradicted
class's own slice has to come back up in the replay.** Not the general replay,
and not any slice — that one.

`tool.name_fidelity` is then cleanly ruled out as a replay effect from the other
direction: F sits at `tools` 0.274% and reads **114/120**, while D at 0.293%
reads 106. Same slice share, eight items apart, so what separates them is the
payload. Ordered by payload: unpaired 112 and 114, ellipsis-only pairs 111, full
matched pairs 106-108. The `chain_result` twin remains the best candidate and
still has no clean test — arm E recovered it to 111 but changed the payload's
class balance at the same time, which is a smaller version of the mistake this
section exists to correct.

**F is the best arm of the seven and still discards**: `chain_ellipsis` 45/50
against a base of 49, four off its ceiling. Everything else is at or above base
— `name_fidelity` 114 against 112, `note_fidelity` 108 against 99, `react`
119 against 120, `reask` 64 against 40, every copy row at ceiling. The direction
is unambiguous and untested past this point: 24x on `turn2` bought 38 items, and
nothing here says what 50x buys.

**What this costs the reader of §§3-4:** two claims in this document were made
from arms that could not support them, and both are corrected above rather than
edited out. The pattern in both is the same — a variable moved alongside the one
under test, and the arm was read as though it had not.
