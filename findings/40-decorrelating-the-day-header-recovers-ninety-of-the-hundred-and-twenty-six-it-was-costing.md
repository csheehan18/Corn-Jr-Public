# Moving the date header recovers about ninety items it was costing

**Full result:** Decorrelating `<|day|>` recovers about ninety of the items it was costing

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v1_chat`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`configs/mix_v1_chatday.py` ×2 against `nano20m_v1_chat` ×2. One file swapped in a 5% slice:
`chat.txt` → `chat_day.txt`, same 194,337 transcripts, same weight to the token, a `<|day|>`
header above 96,755 of them.

**The controls hold, so the arm is readable.** `register.conv` is the one that decides this —
the twenty-fifth finding priced it at exactly this dialogue share against a 1.0-point floor, the
tightest in the project.

| control | baseline | arm |
|---|---|---|
| `register.conv` /200 | [77, 82] | **[82, 82]** |
| `chat.abstain_talk` /100 | [100, 100] | [100, 100] |
| `chat.engage` /100 | [100, 100] | [99, 99] |
| `temporal.route` /400 | [398, 400] | [398, 398] |
| `temporal.copy` /353 | [353, 353] | [353, 353] |

## The header cost 137 items on average and now costs 46

`daycross` is a *paired difference* — the same 200 tool requests scored bare, then again with a
header above them — and neither cell means anything alone.

| | seed 1 | seed 2 | range |
|---|---|---|---|
| baseline `mix_v1_chat` | −155 | −120 | [−155, −120] |
| **arm `chatday`** | **−29** | **−63** | **[−63, −29]** |

The ranges do not overlap and the gap is about 90 items against a within-arm spread of 34. By the
thirtieth finding's rule that is a size worth quoting, not merely a direction.

**The mechanism moved the way the config said it had to.** The header's damage was specifically a
collapse onto `resolve_date`, and that is what receded:

| checkpoint | `resolve_date` named bare | under the header |
|---|---|---|
| `chat` s1 | 14 | **189** |
| `chat` s2 | 5 | **158** |
| `chatday` s1 | 1 | **49** |
| `chatday` s2 | 4 | **78** |

A pass rate that moved while the naming did not would have been a different result from the one
this arm asked for. It moved together, which is what makes the reading the intended one.

## Capacity was making it worse, which is why this mattered

The bug is not a missing capability and no amount of temporal data addresses it. `daycross` read
−126 at 29.6M and **−150 at 91.6M** — a bigger model read the spurious cue *harder*. That is the
signature of a correlation in the corpus rather than a limit of the model, and it is why the fix
had to be corpus-side and why "it will wash out at scale" was never available as an answer.

## What this does not settle

- **The residue is still −29 to −63.** Half the effect at best. 5% of the budget carrying a
  header on half its transcripts is up against a temporal slice where the header sits above every
  transcript, and nothing here says where the remaining cost lives. The obvious next dose is the
  share; the obvious next axis is headers on the tools slice, which the config names as out of
  scope for one-variable-at-a-time reasons.
- **`chat.abstain_oos` rose from [7, 29] to [26, 39] and that is not claimed as a second result.**
  The config asked only that it not fall. The ranges overlap at 26–29, it is one row, and nothing
  in the arm's design predicts it.
- **`chat.engage` fell by 1 item on both seeds.** Reported because it is a control and controls
  get reported, not because 1 of 100 means anything.
- **Two seeds**, and `daycross` had no measured floor before this arm. What licenses the size
  claim is that the two ranges do not overlap and the gap is roughly three times the wider
  within-arm spread — not that either spread is known.
- **Nothing here is measured above 29.6M.** The bug is known to be *worse* at 91.6M, so the fix
  surviving scale is exactly the thing this cannot assume. Re-reading `daycross` on a 91.6M
  `chatday` checkpoint is the cheapest thing that would settle it.
