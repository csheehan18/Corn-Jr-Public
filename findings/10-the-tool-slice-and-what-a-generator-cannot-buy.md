# A generated tool dataset caps at 2.3 MB of distinct examples

**Full result:** The tool slice, and what a generator cannot buy

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_web_bpe`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

DATA.md §4 gives assistant transcripts with tool calls 15% of the budget, and §6 says they
"need a larger model to generate". That claim is about *labels*, and the temporal slice is a
standing argument against it: manufactured programmatically, exact ground truth, and the
source of the project's most load-bearing result. So the tool slice was built the same way —
`corn/tools.py` declares the tools, `corn/toolgen.py` builds transcripts by construction, and
`scripts/check_tools.py` checks them with an independently written reader that has to agree.

**Five tools, as declarations rather than code** (VISION §6's own rule): `place_call`,
`send_text`, `save_note`, `web_search`, plus `resolve_date`/`recall_day` from the temporal
slice. VISION names four and says a fifth "will come out of development rather than planning";
web search is it, and it is the one the confirmed use case — hands-free research while driving
— actually needs.

**`web_search` returns an `answer` field, not a page of snippets.** Snippets would make this
the one place in the corpus where Corn-Jr composes a fact instead of copying one, and §5.2
forbids exactly that: a 250M model asked to summarise three snippets will fluently produce
something that was in none of them. The tool extracts, the model reads out. That keeps it on
`resolve_date`'s discipline, which means the sixth finding's copy result gets *tested* on a
second tool with a different payload shape rather than assumed to generalise — §11 has carried
"still one tool" as a caveat on it ever since.

**A third of the slice is failure**, which is the part §6 says matters most: an ambiguous
contact, a name not in the book, a lookup with no answer, a query too vague to run, and
requests no tool covers. Every one of those labels is exact *because the situation was chosen
before the sentence was written*. This is precisely where a larger model is weakest — ask one
for "requests Corn-Jr should refuse" and the labels are its opinion.

### The two stub rows are live, and were right to be two rows

`tool.validity` and `tool.selection` printed `--` for six checkpoints. `evals/tools.jsonl`
went in via `make_evals.py --add` with all four prior sha256 and `built` untouched. Scored on
`nano20m_web_bpe` — a model that has read one tool and never seen the other four:

| row | score | n | why |
|---|---|---|---|
| `tool.validity` | **61.9%** | 181 | `not_json 69` |
| `tool.selection` | **0.0%** | 200 | `chose_resolve_date 112`, `unparseable 69`, `called_anyway 19` |

**Six times in ten it emits a perfectly well-formed call to the only tool it knows.** Valid
and wrong. Merged into one row that reads about 30% and tells you nothing about which half is
broken. The zeros are the floor these rows needed for the same reason the fourth finding gives:
a row that cannot read zero on a model which has never seen the behaviour cannot register the
change when it arrives.

`tool.selection` counts **"no tool" as an answer** — 19 of its 200 items are requests nothing
covers, and their prompts stop after the user's line rather than at `<|call|>`, because ending
them at `<|call|>` would hand the model the answer to the only question they ask. `called_anyway
19` is that reading zero too.

Decontamination is structural, borrowing temporal's held-out anchor years on a different axis:
`corn/toolgen.World` parameterises the generator, and the training and eval worlds share every
template and **no lookup table** — contacts, first names, facts, unknown names, vague queries
and out-of-scope requests all disjoint. A model that dials Ophelia Vance or reads back Kinshasa
did it by copying the observation. Two of those six holdouts only got added once the eval was
wired, which is the argument for wiring it: an item on a vague query would otherwise have
scored recall of a clarify the model read thousands of times.

### The real limit is sentences, not labels

The mix is a target that variety has to be able to reach, and it very nearly did not. The
first version of `gen_tools.py` deduplicated a weighted stream without per-kind budgets and
emitted **61.5% `send_text` against a declared 16%, and 0.1% out-of-scope against a declared
10%** — the situation §9 ranks highest, almost entirely absent, with nothing in the output
saying so. Situations with small combinatorial spaces exhaust first and every later draw of
them is a duplicate.

Each kind now gets its share and a kind that runs dry **falls short and says so**, which is
`prepare_mix`'s contract and §8's reasoning. That made the ceiling visible:

| | distinct transcripts | share | caps the slice at |
|---|---|---|---|
| `send_text` | 75,504 | 16% | 471,900 |
| `place_call` | 3,696 | 16% | 23,100 |
| `web_search` | 2,800 | 20% | 14,000 |
| out of scope | 2,016 | 10% | 20,160 |
| vague query | 550 | 5% | **11,000** |

**~11,000 examples, 2.3 MB, against the ~75 MB §4's 15% wants.** So §6 is half right, and the
half that survives is not the half that was meant: exactness and the failure modes are free,
and *phrasing nobody wrote down* is what costs. That relocates where a larger model earns its
place — as a paraphraser over a skeleton whose labels are already correct, rather than as the
source of the labels.

**What this does not show:** no model has been trained on the slice yet, so 61.9%/0.0% is a
floor reading and not a result — the eleventh finding trains two. And the out-of-scope holdout is the weakest of the six —
knowing what you cannot do is partly a fact about yourself and only partly a generalisation,
and only the second is being tested.
