# A twenty-fifth of the planned tool data buys most of the behaviour

**Full result:** A 25th of the declared share buys most of the behaviour

**Cost:** 7.6 min of scoring on the 2 cards first cited here (`nano20m_tools15`, `nano20m_tools_1pass`); it also reads 1 card scored for an earlier finding (`nano20m_web_bpe`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

DATA.md §4 gives tool transcripts 15% of the budget. The tenth finding showed the slice caps
at 2.3 MB, so 15% is only reachable by `Source(repeat=True)` re-reading the file ~25 times —
which §8 says is exactly the trade a hardware-capped budget cannot afford. Nothing had measured
it. Two arms, both at **130,279,711 tokens** and `nano20m_web_bpe`'s config verbatim except
`data_dir` — **2 differing fields of 30** across all three runs, so composition is the only
variable and the existing run is the 0% point for free:

| row | 0% tools<br>`nano20m_web_bpe` | **0.61%**<br>`nano20m_tools_1pass` | 15%<br>`nano20m_tools15` |
|---|---|---|---|
| `tool.selection` | 0/200 | **146/200** | **172/200** |
| `tool.validity` | 112/181 | **167/181** | 155/181 |
| `narrative` nats/byte | 0.3666 | **0.3666** | 0.3724 |
| `temporal` nats/byte | 0.0967 | **0.0944** | 0.0952 |
| `web` nats/byte | 0.9104 | **0.9099** | 0.9216 |
| `temporal.route` | 398/400 | **399/400** | 398/400 |
| `temporal.copy` | 353/353 | 353/353 | 353/353 |
| `refusal.clarify` / `no_guess` | 47/47 | 47/47 | 47/47 |
| tool passes over the file | — | 1 | 25 |
| wall clock | 992.4s | 1,027.2s | 1,024.8s |

**One pass over 2.3 MB — 0.6075% of the budget, a 25th of what §4 asks for — moves selection
from nothing to 73% and validity from 61.9% to 92.3%, and costs nothing.** Narrative is
*identical* to the no-tools run at 0.3666; temporal and web come in fractionally better. That
is the result, and it was not the expected one: the share §4 declared before the data existed
turns out to be mispriced by a factor of twenty-five for most of what it was buying.

### The two tool rows move in opposite directions, which means they are two levers

Spending the other 14.4% is not free and not useless. It buys 26 more selections (146 → 172)
and it costs 12 validities (167 → 155), plus 1.6% of narrative and 1.3% of web. Splitting
`tool.validity` and `tool.selection` into separate rows was a tenth-finding decision made on
the argument that a formatting failure and a routing failure are different questions; this is
the run where that decision pays. A merged row would have read **313/381 for the one-pass arm
against 327/381 for the 15% arm** — making the upsampled corpus look like a straight
improvement, in the exact run where it broke the schema.

**The regression is one tool and one field.** Re-running all 45 `send_text` items on both
checkpoints:

| | `send_text` failures | why |
|---|---|---|
| `nano20m_tools_1pass` | **0 / 45** | — |
| `nano20m_tools15` | **16 / 45** | `missing:message` ×16 |

Every one picks the **right tool** and then truncates the argument object to `place_call`'s
one-field shape. `send_text` and `place_call` share `contact`, and `send_text` is the only one
of the five tools with two required parameters — so what collapses is the tool with the most
structure, into the neighbour it shares a field with.

And where the contact slot should hold a name it has never seen, the upsampled arm reaches
into the training set instead:

    want  contact='Thaddeus'  message='thanks for today'
    got   {"name": "send_text", "arguments": {"contact": "Those point of mercury"}}

`the freezing point of mercury` is a `web_search` query in the training world and appears
**231 times** in the corpus. Read 25 times over, the model has memorised the strings and falls
back into one when the sentence goes somewhere it cannot follow. **This is only visible because
of §7's structural holdout** — `EVAL_WORLD` shares every template and no lookup table with the
training generator, so a held-out contact name is a place memorisation has nowhere to hide.
An eval drawn from the same contact book would have scored this arm higher and taught us
nothing.

So §8's rule survives with a sharper mechanism than the one it was argued from. "Every
duplicate displaces a token you cannot afford" is true here — 18.8M tokens of real language
went, and both prose rows moved — but it is the smaller half. The larger half is that
repetition does not merely fail to add information, it actively installs the wrong prior, and
it does so in the most structured corner of the format.

### Three things worth recording

**`temporal.copy` is 353/353 in both arms** — a fourth distribution, and the first in which a
second, third, fourth and fifth tool were competing for the same call slot. It has now held
under templates, under real web text, under retokenization, and under four rival tools.

**The question the slice was built for is still open, and the missing piece is an eval row.**
The tenth finding shaped `web_search` to return an `answer` field so that deference — read
back what the tool said, never compose — could be tested on a second tool. Both arms have now
read that slice, and it still cannot be scored: every item in `evals/tools.jsonl` stops at
`<|call|>`, and `score_validity`/`score_selection` both read the *call*. Nothing presents an
`<|obs|>` and scores the `<|say|>` after it, which is the only thing `temporal.copy` does. The
rows measure routing and schema on five tools and deference on one, still. `HELD_OUT_FACTS`
already makes the fix trustworthy; it needs items with a `prompt_after`, added via
`make_evals.py --add`.

**Checkpoint selection had nothing to disagree about, twice more.** Best-val and final were
iter 5,237 in both arms — weights compared tensor-by-tensor and identical — so `ckpt.pt` and
`last.pt` are the same model and the rule-versus-ruler tally is still empty after four runs.
That matters more here than it looks: `val_tools.bin` in the 15% arm is a fragment of a 25th
pass over text the training stream already holds 24 times, so its 0.1311 is memorisation and
not validation, and `selection_score` weights it as one of four equal sources. A quarter of
that arm's selection signal was a memorisation readout. It happened to have nothing to
overturn. The rule was left alone rather than patched mid-experiment, which is why both arms
were scored on a checkpoint whose provenance is stated rather than assumed.

**What this does not settle:** 25M parameters reading 6,470 distinct sentences ~38 times
cannot be separated, by this pair, from 25M parameters reading them at all — the collapse may
be repetition or may be capacity. The test is the same pair at a larger *distinct* count and
unchanged 15% share, which is what DATA.md §11's sentence-sourcing question is now
load-bearing for. And the wall clocks (1,024.8s / 1,027.2s against the 0% arm's 992.4s) are
the four per-source val splits costing an extra `eval_iters=40` at each of 42 evals, not the
corpus.
