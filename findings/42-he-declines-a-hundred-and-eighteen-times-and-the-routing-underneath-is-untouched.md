# He now declines 118 times, with routing untouched

**Full result:** He declines 118 times, and the routing underneath is untouched

`configs/mix_v1_toolspace_decline.py` ×2 against `mix_v1_toolspace` ×2. The `absent` class stops
being a silence and becomes a route: `decline` on every declaration line and always last, he calls
it, the runtime returns `{"ok": false, "reason": "not_covered", "say": ...}`, and he relays the
observation's own words. He composes nothing.

**This is the first time `absent` has moved in this project.** It read 0 in twelve of fourteen
cells across three corpora and two vocabularies, survived three corpus repairs, and the
thirty-ninth finding showed the grammar could not hand it over either — with `decline` declared,
rendered identically, positioned last and left open as the only escape, untrained checkpoints took
it 3 times in 442.

## The row

Scored with `--narrow decline`, n=200 per level, 221 `absent` items per checkpoint.

| checkpoint | `absent` | of which *routed to `decline`* |
|---|---|---|
| `toolspace` s1 | 0/221 | 0 |
| `toolspace` s2 | 3/221 | 3 |
| **`toolspace_decline` s1** | **118/221** | **118** |
| **`toolspace_decline` s2** | **101/221** | **101** |

Every single pass is `pass_declined`. Not one is "he stopped calling" — the bucket exists
precisely so those two cannot be averaged, and the answer is unambiguous. The behaviour arrived
through the channel the plan predicted: **routing, then deference to the observation.**

## The routing capability is undamaged — and that needed the right control to see

The obvious worry is that he learned to decline by declining more. The `declared` cell answers it:
same items, same narrowing, but `decline` is **not** on offer, so declining is not available and
what is left is pure tool choice.

| checkpoint | `name` pass in the `declared` cell |
|---|---|
| `toolspace` s1 | 238/379 |
| `toolspace` s2 | 224/379 |
| `toolspace_decline` s1 | **235**/379 |
| `toolspace_decline` s2 | **224**/379 |

Identical, both seeds. **The corpus did not cost him any routing.**

## But the policy is miscalibrated, and that is the cost

In the `decline` cell — where declining *is* available — he takes it on items where a real tool
was declared:

| checkpoint | `name` pass | **over-declined** |
|---|---|---|
| `toolspace` s1 | 235/379 | 0 |
| `toolspace` s2 | 209/379 | 0 |
| `toolspace_decline` s1 | 178/379 | **98** |
| `toolspace_decline` s2 | 182/379 | **70** |

This is the pre-registered trade branch, and it gets its own statement rather than an average:
**he gained 115 correct declines and paid 84 wrong ones.**

The two cells together say something more precise than "route falls". The capability is intact —
he still picks the right tool at baseline rate when declining is off the table. What moved is the
*policy*: offered an escape, he over-uses it. That is a calibration problem, not a lost skill, and
it is a different repair from the one a damaged-routing result would have called for.

## What made the arm readable, recorded because none of it was free

- **`decline` on all 200,000 declaration lines**, not only the 69,919 where it is the answer.
  Otherwise its presence predicts its use and the arm measures a cue.
- **The say pool at 2.75 uses each** — 25,426 distinct refusals composed from the domain's own
  verb and noun. One sentence at ~36,000 uses failed; 128 refusals at 163 uses each failed;
  `temporal_sayvar` worked at 4.5. The target was sayvar's regime, not a round number.
- **A decline-aware scorer written one commit before anything could emit a decline**, with its
  dormancy proved by zero-diff re-score. The thirty-seventh finding's arm scored its own success
  as `unparseable` for want of exactly that.

## What this does not settle

- **The calibration.** 70–98 over-declines of 379 is the headline cost and nothing here prices a
  fix. The obvious dose is the 35% `ABSENT_SHARE`, which was chosen to be far from the local
  optimum rather than tuned, and is now the first thing to bracket.
- **Whether this transfers to bare prompts.** `chat.abstain_oos` asks whether an utterance is a
  request at all, with no declaration to read. The thirty-seventh finding proved turn-1 and turn-2
  abstention are not one behaviour; nothing licenses assuming decline-with-declarations and
  abstain-without-declarations are either. They are measured separately and stay that way.
- **Two seeds**, spreads of 17 on `absent` and 28 on the over-decline count. The move off zero
  needs no interval — its floor is zero by construction and it cleared it by two orders of
  magnitude — but every size quoted above does.
- **29.6M only.** Nothing here says what a larger model does with a declared escape, and the
  thirty-eighth finding is a standing warning that a treated arm can read differently from an
  untreated one on the very instrument used to price it.
