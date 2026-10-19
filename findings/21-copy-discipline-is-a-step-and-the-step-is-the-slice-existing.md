# Copying is a step: it appears once any tool data exists

**Full result:** Copy discipline is a step, and the step is the slice existing

**Cost:** 4.0 min of scoring on the 1 card first cited here (`nano20m_notools`); it also reads 1 card scored for an earlier finding (`nano20m_web_bpe`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The twentieth finding could not distinguish "no share moves this row" from "no share moves it
*above* a floor that the slice buys outright", because all six corpora scored on
`tool.copy_wide` contained the tool slice. Two measurements close it. One cost nothing:
`nano20m_web_bpe` is the only existing corpus with no tool data and was the one checkpoint
never re-scored on the wide row. The other is `nano20m_notools` — `mix_balanced` with the tool
slice removed and web absorbing its 815,442 tokens, one variable, same 130,934,381 budget, same
5,237 iterations, 1,023s at 154k tok/s.

| row | `balanced` | `notools` | `web_bpe` | Δ | floor |
|---|---|---|---|---|---|
| `tool.copy_wide` | 277/300 | **0** | **0** | −277 | 29 |
| `tool.copy` | 120/120 | **0** | **0** | −120 | 18 |
| `tool.selection` | 150/200 | 0 | 0 | −150 | 8 |
| `tool.validity` | 171/181 | 134 | 112 | −37 | 13 |
| **`temporal.copy`** | 353/353 | **353** | **353** | **+0** | 0 |
| `temporal.route` | 400/400 | 399 | 398 | −1 | 2 |
| `refusal.clarify`, `refusal.no_guess` | 47/47 | 47 | 47 | +0 | 0 |
| `schema.conform` | 172/200 | **174** | 0 | +2 | 2 |
| `lm narrative` | 0.3679 | 0.3675 | 0.3666 | −0.0003 | 0.0012 |
| `lm temporal` | 0.0944 | **0.0963** | 0.0967 | **+0.0019** | 0.0009 |
| `lm web` | 0.9106 | 0.9079 | 0.9104 | −0.0027 | 0.0038 |
| `variety.distinct3` | 89.34% | 87.71% | 90.04% | −1.63 | 1.85 |

### The whole effect lives between 0% and 0.61%

Across every corpus the project has trained, `tool.copy_wide` reads:

| tools share | corpora | `tool.copy_wide` |
|---|---|---|
| **0%** | `notools`, `web_bpe` | **0/300, 0/300** |
| 0.61% | seven corpora, four of them seed replicates | 249–289 |
| 15% | `tools15` | 278 |

**Presence is a step and share is flat.** The band above zero spans 40 items where four seeds
on a single corpus span 29, so once the slice exists nothing about how much of it there is has
ever moved the row. The eleventh finding's "a 25th of §4's share buys most of the behaviour"
is understated for copy discipline: 0.61% buys *all* of it, and the unmeasured region is
everything below a share that is already a twenty-fifth of the smallest one ever tested.

### `temporal.copy` 353/353 is the result, not the control passing

Both 0%-tools checkpoints read `temporal.copy` **353/353** while reading `tool.copy_wide`
0/300. The temporal slice commits to the same transcript markers — `<|day|>`, `<|call|>`,
`<|obs|>`, `<|say|>` — and teaches perfect copy discipline on `resolve_date`, and **none of it
reaches `web_search`.** So the thirteenth finding's "the copy discipline generalises" is real
and is bought by the tool slice; it does not follow from having the format, which was the one
reading the twentieth finding left open. Deference is learned per answer space, not per marker.

The failure modes differ between the two 0% arms in a way worth recording: `web_bpe` fails
`malformed` 300/300, and `notools` fails **`empty` 298 and `malformed` 2**. The corpus with the
structured slice stops writing instead of writing the wrong thing.

### `tool.validity` cannot tell schema mastery from one memorised call

`tool.validity` reads **134/181 on `notools` against 112/181 on `web_bpe`**, and neither model
has ever seen a tool call. That looked like the structured slice buying tool-call syntax. It is
not, and the arithmetic says so exactly:

| | `tool.validity` pass | `tool.selection` `chose_resolve_date` | `not_json` / `unparseable` |
|---|---|---|---|
| `web_bpe` | **112** | **112** | 69 / 69 |
| `notools` | **134** | **134** | 46 / 46 |

**Every valid call either model emits is a `resolve_date` call.** They know one tool of six,
from the temporal slice, and name it for all 181 items whatever was asked. `score_validity` is
deliberately blind to which tool was chosen — a well-formed call to the wrong tool is a
validity pass and a selection failure, which is the distinction the two rows exist for — so a
model with one memorised call reads 74% on a row whose one-line note is "emit a call that
matches the schema".

So the 22-item difference is **entirely fewer unparseable answers**, 69 → 46. What the
structured slice buys is JSON well-formedness, not anything about tools. That is a smaller
claim than the one this finding first recorded, and a cleaner one: it is the same skill
`schema.conform` measures, showing up on a row that was not built to see it.

**Nothing on the scorecard said any of this** — finding it meant cross-referencing two rows'
failure buckets, and the coincidence of 134 with 134 is the only thing that gives it away. So
`corn/evals.py` gains `named_tool` and the validity row gains a `named` count of which tool
each item named, with the report saying out loud when a row has collapsed onto one tool.
`scripts/check_evals.py` gains eight checks over it. It changes no score: the buckets are
observations, not verdicts, and every re-scored row came back identical.

`schema.conform` 172 → **174** fills the last empty cell of the 2×2 — structured formats work
at full strength with no tool slice present, at the row's floor. (Quoted as 2 when written; the
thirtieth finding puts it at **8**, which only makes the null cleaner.)

### Two small costs, one of them real

`lm temporal` moves **0.0944 → 0.0963**, which is 0.0019 against a floor of 0.0009 — a little
over twice it, and the only language row outside its noise. Removing the tool slice made
*temporal* modelling worse, which is the direction the shared transcript format predicts: the
two slices are the only ones that use those markers, and there is now less of that shape in the
corpus. It is small and it is outside the floor, which is the weakest kind of real.

`lm web` moves −0.0027 for 815,442 extra tokens of web, inside its floor of 0.0038. The
absorption is therefore not confounding the ablation, which is what `configs/mix_notools.py`
argued in advance — though it predicted "under 0.001" and the observed move is nearly three
times that, so the argument was right and its arithmetic was optimistic.

### What this does not say

It does not say the tool slice is correctly sized. Every share from 0.61% to 15% reads the same
on this row, so the row cannot price the slice — it can only say the slice must exist. The
fifteenth finding's pricing of tools at 15% still rests on `tool.selection` and on prose, and
this arm does not touch either question. It also does not say anything about scale: `tool.copy`
and `tool.copy_wide` both collapse to zero here, and a 250M model with the same corpus might
recover the format from far less.
