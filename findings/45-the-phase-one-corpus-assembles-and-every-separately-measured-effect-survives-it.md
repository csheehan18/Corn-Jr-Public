# The first full data mix keeps every separately measured effect

**Full result:** The Phase 1 corpus assembles, and every separately measured effect survives it

`configs/mix_v2.py` ×2. Eight sources, six shares each priced by an earlier run, two behavioural
repairs that had never been in the same corpus as each other, and web moved from shard 000 to the
decontaminated shards 001-013.

**This is a build, not an arm.** Eight things change at once by design, so nothing here attributes
and nothing here sizes an effect. The only question a combined corpus can ask that its parts
cannot is whether the parts still work once assembled, and that is what was pre-registered.

## Q1 — the two repairs compose

`daycross` delta, `with_day` minus `no_day`:

| corpus | delta | what it is |
|---|---|---|
| `mix_v1_chat` ×2 | -155, -120 | untreated |
| `mix_v1_chatday` ×2 | -63, -29 | WS-C alone |
| **`mix_v2` ×2** | **-55, -53** | **WS-C beside WS-E** |

`mix_v2` sits **inside WS-C's own range** and clears the untreated baseline by 65 against a floor
of 34 (forty-third finding). On the raw cell, `daycross.with_day` reads **74, 64** against a
four-seed `mix_v1` baseline of 1-30.

The spread is 2, against WS-C's own 34. Two seeds are not a distribution and that is very likely
luck, but it is the tightest cell in the run.

## Q2 — the interpolation was right, and the shard swap cost nothing

Web's share here was **set by interpolation rather than measured** — 49.3772%, between the two
doses the forty-fourth finding read. The bracket that licensed it was pre-registered as
[0.8829, 0.8848].

**`lm web` reads 0.8840 and 0.8840.** Mid-bracket, and the two seeds agree to four decimals.

That settles two things at once, which is why the bracket was written before the run. The
linearity claim holds at a third point. And the shard swap — the only change here touching web's
*content* rather than its size — was the alternative explanation for a miss, so a hit exonerates
it without needing its own arm.

## Q3 — the decline route survives, and so does its calibration problem

Scored `--narrow decline`, n=200 per level, 221 `absent` items per checkpoint, matching the
forty-second finding's method exactly.

| corpus | `absent` /221 | over-declines /379 |
|---|---|---|
| `mix_v1_toolspace` ×2 | 0, 3 | — |
| `mix_v1_toolspace_decline` ×2 | 118, 101 | 98, 70 |
| **`mix_v2` ×2** | **111, 107** | **116, 101** |

`absent` lands **inside the WS-E arm's own range**, and every pass is `pass_declined` — not one
is "he stopped calling", the distinction the bucket exists to preserve.

**The over-declining reproduced, and it is not readable as worse.** [101, 116] against
[70, 98] is a gap of **3**, against an arm spread of 28 and a `mix_v2` spread of 15. The config
pre-registered "an over-decline count inside that range is not a regression of this build"; the
range is strictly above rather than inside, and the gap is far enough inside the noise that the
honest verdict is *reproduced, no demonstrable change*. `ABSENT_SHARE` is still 0.35 and still
untuned, and the repair is still a bracket rather than a corpus.

## Q4 — contamination clean on the new shards

Both seeds, web: 16 probes, 16 discriminating, **0 in train and 0 in val**, source checked.

This matters more here than on any previous corpus because `reserve_tail` is 0 for web — the tail
scheme protects a region of shard 000 and the eval text was never in the b shards at all, so
decontamination is the only guard standing where reservation used to. **It is also the weaker of
the two guards**: 16 probes against `decontaminate.py`'s 204-document pass, which is what
actually produced the file at 0 of 204. This is independent confirmation, not a second proof, and
that script's own docstring is explicit that it reduces contamination rather than proving its
absence.

## What moved that nobody asked for

| row | `mix_v1` ×4 | `mix_v2` ×2 |
|---|---|---|
| `chat.abstain_greet` | 3-20 | **28, 39** |
| `chat.abstain_talk` | 93-99 | **100, 100** |
| `register.conv` | 78-81 | 81, 84 (holds, as pre-registered) |

Both abstention gains are consistent with WS-C's slice — `chat_day.txt` is marked transcripts
that do not call — but this corpus cannot attribute them, and `chat.abstain_talk` at 100/100 is
touching a ceiling the thirty-fifth finding already described as unreadable.

## The one row pointing down

`tool.validity` reads **153, 137** against a baseline of 157-175. `effect.py`:
**separated by 4 (lower), churn unmeasured.**

That is the verdict to quote. The gap is 4; the baseline's own spread is 18 and the arm's is 16.
It is not a demonstrated regression. It is also the row a corpus carrying two new tool-adjacent
slices is most likely to damage, and it is the only row in the run pointing the wrong way, so it
should not be waved off either. More seeds or a churn measurement, before anyone quotes it in
either direction.

Everything else on the frozen set reads OVERLAP, including `temporal.route` at 396-398 against
398-400 with a floor of 3, and `temporal.copy` at 352-353.

## One number that will be misread if it is not stated

**`val` is 2.4202 and 2.4154 here against `mix_v1`'s 2.2516, and that is not a regression.**
`val` is computed over each corpus's own held-out split, so a corpus at 49% web and 10% narrative
is being scored on harder text than one at 40% and 19.58%. Cross-corpus `val` has never been
comparable in this project — the seventh finding is where a blended `val` selected the *worse* of
a run's two checkpoints. The rows that compare are the `lm` ones, whose inputs are frozen bytes
identical for every corpus, and the behaviour rows.

## What this does not settle

- **Two seeds.** The forty-third finding widened `refusal.say` from 10 to 42 when two more seeds
  arrived on a corpus that already had two. Every range here is a lower bound.
- **Nothing here attributes.** Eight changes at once. `chat.abstain_greet` moving 3-20 to 28, 39
  is consistent with WS-C and equally consistent with three other things in this file.
- **It is 29.6M.** Every number behind every share in this corpus is nano-scale, and the
  thirtieth finding's rule about floors being properties of arms has a scale version nobody has
  measured.
- **The corpus does not exist at Phase 2 scale.** This is a *recipe* validated at 131M tokens. Re-
  instantiated at 5B under these shares, five of eight slices exceed 7 passes over their pool and
  three exceed 27 — `tools` at 38, `structured` at 34, `chat` at 27, `temporal` at 14 — against a
  repetition arm that measured 15.21 passes as expensive. Web is fine at 1.58. Nobody had done
  this arithmetic for the generated slices, and `gen_tools.py` is already documented as
  cardinality-bound about 28x short of what §4 wants.
