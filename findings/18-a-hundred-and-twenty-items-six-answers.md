# Eighteenth finding — a hundred and twenty items, six answers, and the rule was already written

The seventeenth finding said `tool.copy` moves 18 items on the seed alone and called it noise.
Regenerating the row on both checkpoints and diffing item by item says otherwise. **The row
fell 18 items and 17 of them are one answer:**

    1337   <|say|>Alexander Fleming.
    1338   <|say|>It's Flemingbelander Flemingbel.

17 of the 20 `the discoverer of penicillin` items flipped from pass to fail, and nothing else
did. `Flemingbel` appears in none of the 8,697 training `FACTS` — the model is not reciting a
memorised answer, it is garbling a copy mid-name, which is a different failure from the one
`trained_answer` was built to catch and scores as `wrong_answer` correctly.

**`evals/tool_copy.jsonl` is 120 prompts over six answers.** `HELD_OUT_FACTS` is six
hand-written facts and the builder wraps each in ~20 of the 25 `SEARCH_TEMPLATES`:

| answer | items |
|---|---|
| `1,642 metres at its deepest` | 22 |
| `the Mekong` | 22 |
| `Alexander Fleming` | 20 |
| `Kinshasa` | 20 |
| `up to 3.5 metres` | 18 |
| `3,422 degrees Celsius` | 18 |

So the row's effective sample size is 6 and its resolution is one fact — about 20 items, or 17
points. **Every movement the project has read off it is a whole number of facts**: 120→111,
120→114, 120→102 and 120→99 are all ±1, and the thirteenth finding's 27→120 is about five,
which is why that one was never in doubt. The small ones never meant anything.

### The number was in the manifest the whole time

`make_evals.py` has written `tool_copy_answers` into `evals/manifest.json` since the day that
row was built, with a comment saying it plainly — *the prompts are 120 distinct sentences; the
answers are six*. It has read **6** for five findings. Nothing consumed it, no check asserted
it, and every finding since quoted the row out of 120.

### It is §11's own rule, pointed at the eval instead of the corpus

§11 states it: *any span the model is meant to copy must come from a space too large to learn
as a set.* It cost three findings in the corpus — 28 search facts, 400 field names, and the
sixth finding's `ANCHOR_END` read backwards — and `check_copyable.py` now enforces it over
`data/raw/*.txt` so it cannot recur there. **Nothing enforced it on `evals/`, and the row built
to test that very rule was the smallest set in the project.** The corpus-side guard and the
eval-side hole were written eight days apart.

### The widened row, and why it had to be invented

`evals/tool_copy_wide.jsonl` is the same items from a search index wide enough to resolve
something: **300 prompts over 232 answers, 1.29 each against 20.00**. It went in with
`make_evals.py --add`, so all eight prior sha256 and `built` are untouched and every existing
scorecard stays comparable — `tool_copy.jsonl` keeps its quantum and is still scored, first, in
the same place on every scorecard.

Hand-writing 200 more real facts was the obvious route and is the wrong one, for the reason
`corn/tools.py` already gives about the training index: every real fact written down is one a
larger model could know, and a model answering `Kinshasa` from its weights scores identically
to one that read the observation. So `HELD_OUT_FACTS_WIDE` is **invented** — 560 facts over the
same six shapes, drawn from the master name pool past what `_invent_facts` consumes, which
makes the two worlds disjoint by partition rather than by luck. `FACTS` is byte-identical
before and after (sha256 verified), which matters more than it looks: `score_tool_copy` reads
`FACTS` to decide what counts as a `trained_answer`, so redefining it would have silently
changed what fourteen existing scorecards mean.

### The same substring bug, a third time, in the numbers

Three of the six shapes draw from disjoint name pools and collide zero times. The two integer
shapes were designed the same way — depths 2,010–4,990 against training's 120–1,990, melting
points 3,810–5,900 against 230–3,800, ranges chosen so the numbers *cannot* coincide — and it
does not work:

    held out   '2,566 metres at its deepest'
    training     '566 metres at its deepest'   <- matches, word-bounded

**The thousands comma is a word boundary**, so every comma-formatted four-digit answer contains
a three-digit one. 40 of 600 candidates are dropped for it, all depths and melting points. This
is the twelfth finding's bug a third time — a short numeric answer found inside a longer one —
and it means the collision filter is the mechanism on two of six shapes rather than the guard
it was written as. Wingspans escape only by accident of format: three decimals against
training's two puts a digit where the boundary would have to be. The docstring claiming
range-disjointness was wrong and now says this instead.

### The guard, and what it caught on its first run

`check_evals.py` gains two groups and is now 16. Group 15 is the general form: **every `.jsonl`
in the manifest must declare a maximum items-per-target, and a row that does not declare one
fails.** That is `check_copyable.py`'s argument about undeclared slices — all three instances
got in because nobody thought to look — so the fix is a table nobody can add a row without
editing.

| row | items | targets | each | declared |
|---|---|---|---|---|
| `schema.jsonl` | 200 | 200 | 1.00 | ≤ 1.0 |
| `tool_copy_wide.jsonl` | 300 | 232 | 1.29 | ≤ 2.0 |
| `temporal.jsonl` | 400 | 306 | 1.31 | ≤ 3.0 |
| `tools.jsonl` | 200 | 105 | 1.90 | ≤ 2.5 |
| `tool_copy.jsonl` | 120 | **6** | **20.00** | ≤ 25.0 |

The frozen row is declared **as broken** rather than quietly exempted: it cannot be rebuilt
without moving its sha256, so it keeps its quantum, the number is pinned so it cannot get
worse, and `tool.copy_wide` is the row to read. On its first run the group failed —
`variety.jsonl` was undeclared — which is the guard doing its job on a row that legitimately
has no gold target; it now declares `None` explicitly, on the same argument
`check_copyable.py` makes for an empty tuple. Group 16 is the wide row's holdout, and the
queries and answers were also checked against `data/raw/tools.txt` directly: **0 of 560
queries, 0 of 560 answers and 0 of 300 user lines appear in the corpus that was trained on.**

### What this does not say

Nothing here is a model result — no checkpoint changed and no corpus moved. It is a
measurement about a ruler, and the ruler was wrong in the direction that inflates confidence:
five findings quoted a six-way row out of 120. The seventeenth finding's general claim is not
withdrawn, because `tool.validity` moved 13 items over 105 distinct targets and
`variety.distinct3` moved 1.85 points, and neither has a clustering story. Those two are what
the seed replicates are actually measuring.
