# Fifteenth finding — the two shares anyone priced were both four to twenty-five times too big

**Cost:** 4.4 min of scoring on the 1 card first cited here (`nano20m_balanced`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

§4's mix was written before any of the data existed, which was the honest thing to do and is
why every share is a guess. **Two have now been measured** and both were far too generous.
`nano20m_balanced` is the corpus that results: every slice the project has, at the share
measurement supports, with no upsampling anywhere.

| row | `tools_1pass` | `struct` 10% | **`balanced` 2.5%** |
|---|---|---|---|
| `schema.conform` | 0/200 | 194/200 | **172/200** |
| `tool.copy` | **120/120** | 99/120 | **120/120** |
| `tool.validity` | **175/181** | 168/181 | 171/181 |
| `tool.selection` | 148/200 | 148/200 | **150/200** |
| `temporal.route` | 398/400 | 398/400 | **400/400** |
| `temporal` nats/byte | 0.0955 | 0.0961 | **0.0944** |
| `narrative` nats/byte | **0.3665** | 0.3715 | 0.3679 |
| `web` nats/byte | **0.9098** | 0.9174 | 0.9106 |

**A quarter of the share keeps 89% of the gain and gives the tool rows back entirely.** This is
the first checkpoint that is best or near-best on every row simultaneously — before it, the
project's two best models each won half the scorecard and lost the other half.

The marginal rate is the part worth carrying forward. The first 2.5% of budget buys about **69
`schema.conform` items per percentage point**; the next 7.5% buys **2.9**. A 24x worse trade,
and not a free one — it is paid for in 21 items of `tool.copy`, 3 of `tool.validity` and about
1% of prose. Nothing about the row said this in advance; 194/200 looks like a share doing its
job right up until you price the last three quarters of it.

### The corpus bears very little resemblance to §4, and most of that was never decided

Writing the priced shares next to the unpriced ones is the more useful table, because it shows
how much of the mix arrived by inheritance rather than by choice:

    slice           §4 said   mix_balanced    ratio   how it got there
    general web         40%         38.95%    0.97x   set once, in mix_web
    conversational      20%          0.00%       --   never sourced
    tool calls          15%          0.62%    0.04x   PRICED, three arms
    narrative           10%         46.80%    4.68x   inherited from the pilot
    structured          10%          2.50%    0.25x   PRICED, three arms
    temporal             5%         11.13%    2.23x   inherited from the pilot

**Narrative is 47% of the corpus against a declared 10%, and nobody ever chose that.** It is
the pilot's token count, held fixed ever since so that each experiment had exactly one
variable — a deliberate *methodological* choice that was never a corpus-design one, and never
revisited once the reason for it expired. Temporal at 11% instead of 5% is the same story.

So the honest state is: one share as declared, one absent, two priced and cut hard, and **two
running at two to five times their declared size purely because a decision made for the pilot
was never unmade.** TinyStories is now the single largest influence on the model's register,
at 47%, in a corpus for a voice assistant — which is worth holding next to the fact that the
missing slice is the conversational one. Some of what narrative is doing at 47% may be
standing in for a register nobody sourced.

Each of the four unpriced shares is one 35-minute run, and Phase 2 buys them at a hundred
times the cost.

**What it does not say.** One seed, and `tool.selection` moved 32 points between adjacent
checkpoints in the thirteenth finding, so the 148 → 150 on that row is noise and should not be
read. The rows carrying this result are `schema.conform`, `tool.copy` and the three language
rows, all of which have been stable across every run in the series.
