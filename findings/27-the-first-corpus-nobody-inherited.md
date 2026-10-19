# The first data mix with every share measured, not guessed

**Full result:** The first corpus nobody inherited, and a row that prices the mix rather than its slice

**Cost:** 0 s of new scoring on record; it reads 2 cards scored for an earlier finding (`nano20m_narrative10`, `nano20m_struct`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Every corpus before this one carried a number it had not chosen. `mix_pilot` guessed narrative
and temporal; the seven after it moved one slice each and left the rest where the pilot put them.
`mix_v1` starts from §11's prices instead — web 40%, conversational 20%, structured 10%, tools
0.6228%, all four at their measured values **simultaneously for the first time** — and lets
narrative and temporal take the remainder at §4's declared 2:1.

| slice | `mix_conv20` | `mix_v1` | why this value |
|---|---|---|---|
| web | 38.9462% | **40.0000%** | §4's declared share; no arm has argued with it |
| conversational | 20.0000% | 20.0000% | priced — `register.conv` 23% → 76% |
| narrative | 26.8026% | **19.5848%** | remainder, 2:1 against temporal |
| structured | 2.5000% | **10.0000%** | priced — 194/200 against 2.5%'s 178 |
| temporal | 11.1283% | **9.7924%** | remainder, 1:2 against narrative |
| tools | 0.6228% | 0.6228% | priced — 0.61% buys all the copy discipline 15% does |

Four slices move at once, so this is a corpus *choice* and not a controlled arm. It is reported
as one, and the two results below are the ones that survive that caveat.

### The structured share pays out, and the two gains turn out to be the same gain

| corpus | structured | conversational | `schema.conform` | failure modes |
|---|---|---|---|---|
| `balanced` | 2.5% | — | 172/200 | `missing_key` 18, `wrong_value` 7, `not_json` 3 |
| `conv20` | 2.5% | 20% | 178/200 | `missing_key` 18, `wrong_value` 3, `wrong_type` 1 |
| `struct` | 10% | — | 194/200 | `missing_key` 5, `wrong_value` 1 |
| **`v1`** | **10%** | **20%** | **193/200** | `missing_key` 6, `wrong_value` 1 |

Against a floor of 2, structured at 10% is worth +15 here and was worth +22 alone. The two
effects sum to +28 and deliver +21, which reads like a ceiling until the failure modes are
broken out — and then it is not a ceiling at all. **The conversational slice fixes
`wrong_value` and `not_json` and never touches `missing_key`; the structured slice fixes all
three.** So the +6 conversational buys at 2.5% structured is a subset of the +22 structured
buys on its own, and adding both gets the larger one rather than the sum. Nothing was lost to
saturation; the second slice was repairing failures the first had already repaired.

*(Annotated after the thirtieth finding: the floor is **8**, and the arithmetic above needs
re-reading even though the mechanism does not. Structured's **+22** alone and **+21** with
conversational present are both real, at 2.75x and 2.6x; structured's **+15 given
conversational** is 1.9x and only just outside. But the conversational leg — 172 → 178, **+6** —
is *inside* the floor, so "the two effects sum to +28" adds a readable number to an unreadable
one. The simplest reading the sizes support is that structured moves this row by about 22 and
conversational does not move it at all, which needs no subset argument to explain the shortfall.
What survives independently of any floor is the failure-mode pattern, because it is an
invariance within the row rather than a difference of totals: `missing_key` reads **18 / 18 / 5 /
6** — exactly flat across the conversational change and down 13 across the structured one. The
mechanism claim is intact. The size decomposition built on top of it is withdrawn.)*

That is only readable because the row reports *why* it failed. Scored as four bare numbers,
172 / 178 / 194 / 193 looks like a ceiling effect and would have been written down as one.

### `register.conv` moves 2.5 points with its own slice held byte-identical

`data/raw/conversational.txt` is the same file, at the same 26,186,876 tokens, one pass, in both
corpora — the share matches to four decimal places. The row still moves.

| | `conv20` | `v1` | floor |
|---|---|---|---|
| `register.conv` | 76/200 (38.0%) | **81/200 (40.5%)** | **1.0 pt** |
| failed as narrative | 108 | **95** | |
| failed as web | 16 | **24** | |
| conversational `median_turn` | 14.0 | **13.0** | corpus anchor 13.275 |

2.5 points against the tightest floor in the harness, and the failure modes moved *coherently*:
narrative-register failures fell as the narrative share fell, web-register failures rose as the
web share rose. That is a mechanism, not noise. **The row measures the register the model settles
into given everything it read — the other slices compete for it — and not a property of the
conversational slice in isolation.**

This does not touch the twenty-fifth finding's conclusion: a 53-point move dwarfs a 2.5-point
one, and the slice plainly buys dialogue register. What it removes is the right to carry the
*level* forward. 76/200 was never a constant of the source, and quoting it at 250M — where every
share will differ again — would be quoting a number that has now been shown to depend on the
company it keeps.

### The narrative cut is where the bill landed, and the web gain bought nothing

| row | `conv20` | `v1` | Δ | floor |
|---|---|---|---|---|
| `lm narrative` | 0.3949 | **0.4128** | +0.0179 | 0.0012 |
| `lm web` | 0.9051 | 0.9020 | −0.0031 | 0.0038 |
| `lm conversational` | 0.5073 | 0.5079 | +0.0006 | 0.0009 |
| `lm temporal` | 0.0962 | 0.0945 | −0.0017 | 0.0009 |

Narrative gives up 7.2 points of share and pays ~15x its floor for it. Web *gains* 1.05 points
and lands inside its floor — so the two directions are not symmetric at these magnitudes, and
web is the cheaper slice to have been wrong about. `lm conversational` sitting inside its floor
while `register.conv` moved outside its own is the sharpest form of the point above: the
modelling of dialogue did not change, the disposition toward it did.

### The row that looked like it moved, and did not

`tool.selection` was the pre-registered risk. `nano20m_narrative10` cut narrative 36.8 points
and the row fell 150 → 116, so a proportional response to this 7.2-point cut would have been
~7 items against a floor of 8 — unreadable either way. It moved **+1**. The extrapolation does
not scale down, and quadrupling structured cost it nothing.

*(Annotated after the thirtieth finding. The **+1** reading is unaffected — it is inside 8 and
inside 44, and "the pre-registered risk did not fire" stands. What does not survive is the
extrapolation it is measured against: the 150 → 116 it scales down from is itself inside the
row's frozen floor of 44 and is withdrawn, so there is no linear baseline here to fail to scale.
The correct statement is narrower and still useful — **this cut moved `tool.selection` by
nothing measurable, and neither did the one it was extrapolated from.**)*

| row | `conv20` | `v1` | floor | reading |
|---|---|---|---|---|
| `tool.selection` | 155/200 | 156/200 | 8 | inside |
| `tool.validity` | 173/181 | 175/181 | 13 | inside |
| `tool.copy_wide` | 269/300 | 276/300 | 29 | inside |
| `tool.copy` | 78/120 | **100/120** | 18 | **ignore — see below** |
| `temporal.copy` | 353/353 | 353/353 | 0 | control held |
| `temporal.route` | 399/400 | 398/400 | 2 | inside |
| `refusal.clarify` / `no_guess` | 47/47 | 47/47 | 0 | control held |
| `variety.distinct3` | 0.8861 | 0.8771 | 1.85 pt | inside |

**`tool.copy` +22 is the eighteenth finding arriving on schedule.** It clears its own floor of 18
and means nothing: it is the six-answer row, and `tool.copy_wide` asks the same question over 232
answers and moves +7 against a floor of 29. Copy discipline did not change. The row is still on
the scorecard only because twelve earlier scorecards carry it, and this is the fourth time it has
produced a number that would have been a finding if read alone.

### What this does not say

Narrative and temporal are still not chosen. They sit at 19.58% and 9.79% because four other
shares are fixed by evidence and something had to absorb the remainder — roughly twice §4's
declared 10% and 5%, and the ratio between them is the only part of the pair with an argument
behind it. Nothing here prices either one.

Nor does a four-slice move attribute anything to a single share. The two results above survive
because each has a control that pins it: the structured claim is bracketed by `nano20m_struct`
at the same share, and the register claim rests on its slice being *byte-identical* across the
comparison, which is the one thing four simultaneous moves cannot confound.

And all of it is 25M params on a 130M-token budget. The point of building this corpus was to
have something worth spending the 100M check on — validating an inherited recipe would have
been four hours confirming numbers nobody chose.
