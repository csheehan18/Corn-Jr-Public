# Invented facts make him copy; a real name brings memory back

**Full result:** The index was invented and the world is not, so a real name reopens the weights

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

No training. `corn_jr_260m` as it stands, driven through `harness/server.py` with
`--search` against the live backend, and through `corn/agent.py` in process with a
stub search whose only variable is what it returns. The occasion was a broken
`web_search` provider; the result is about the thirteenth finding's fix having a
boundary nobody had looked past.

**The thirteenth finding bought copy discipline by inventing the world.** The
twelfth had diagnosed `tool.copy` 0/120 as a corpus defect: 28 hand-written facts
at 107 examples each let a model be right without reading `<|obs|>`, and the
upsampled arm answered held-out lookups by reciting the table. Inventing the
index ended it — *"there is nothing true here to learn, so reading the observation
is not the cheapest way to be right, it is the only way"* — and `tool.copy` went
to 120/120.

**That sentence is true of the training queries and false of the runtime.** Every
pattern in `FACTS` is a coinage; every query a person actually types is not.
`data/raw/tools*.txt` contains no fact the weights could hold, so no transcript in
it ever *tested* whether a prior would win. Point the same model at Ada Lovelace
and the test finally runs.

## The ladder

`look up Ada Lovelace`, temperature 0, stub backend, one draw per row. Only the
`answer` field varies. Nothing else in the turn moves.

| `answer` handed to him | what he said |
|---|---|
| `Augusta Ada King` | *"Ada Lovelace was an English mathematician and philosopher who lived from **1750 to 1830**. She was a pioneer in the field of algebra and was a pioneer in the study of logarithms. She is also known for her work on the theory of infinitesimals..."* — 700+ characters, looping |
| `Augusta Ada King, Counte` | *"Ada Lovelace, Counte."* |
| `Augusta Ada King, Countess of Lo` | *"Countess of Lo, a famous **18th century French poet**, was born in **1742 in London**. She was the daughter of a wealthy merchant..."* — looping |
| `Augusta Ada King, Countess of Lovela` | *"Countess of Lovelace, the daughter of Countess of Lovelace..."* — looping |
| 56 chars and longer | `''` |

She lived 1815–1852, was not French, was not a poet, and none of the biography is
in the observation. **The observation is sitting directly above the sentence and
he is not reading it.**

The control is the same harness with an invented answer, and it is not close:

    answer "Varenthscar"      ->  "Varenthscar, according to worldatlas.com."
    answer "413 metres at its deepest"  ->  "413 metres at its deepest."

**It is not the query's shape.** A bare proper name is out of distribution —
every `FACTS` pattern is "the X of Y" — and that was the first explanation. It is
wrong: hold the utterance at `look up Ada Lovelace` and hand him a *short* answer
and he reads it back cleanly, including an answer with no relationship to the
question.

| ask | answer | said |
|---|---|---|
| `look up Ada Lovelace` | `Varenthscar` | "Varenthscar, according to worldatlas.com." |
| `look up Ada Lovelace` | `Alexander Fleming` | "Alexander Fleming." |
| `look up Marie Curie` | `Alexander Fleming` | "Alexander Fleming." |
| `look up Vientiane` | `Alexander Fleming` | "Alexander Fleming." |

So the query can be a real name, and the answer can be a real name. What he
cannot do is be handed a real entity he *has a prior about* and stay on the
observation.

## The same failure, live, with a number attached

The live backend reached the same place from the other direction. Asked for the
height of Mount Everest, DuckDuckGo's first snippet was about the Mahalangur Himal
sub-range and contained no height. He said:

> It is 1,890 metres (5,000 ft) above sea level.

A figure in neither the snippet nor reality. This is the twelfth finding's
recitation with the table swapped for the pretraining corpus, and it is worse in
the same proportion that the pretraining corpus is larger than 28 rows.

VISION §7 lists open-domain world knowledge as a non-goal and §9 names
confabulation as the failure that matters most. Both are satisfied on paper: no
slice teaches facts. Neither is satisfied at runtime, because *not teaching* a
fact is not the same as the weights not having one.

## What no scorecard can see

`tool.copy` reads 120/120 and is not wrong. It draws from `HELD_OUT_FACTS`, which
is invented by construction, so the row measures copy discipline **in the one
regime where nothing competes with the observation**. Every deference number in
this project is measured there. The regime where a prior competes has no row, no
eval and no corpus, and this is the first time it has been looked at.

That is the finding. The rest of this file is what was fixed on the way to it.

## Three runtime faults, all fixed, none of them the above

**The runtime fed him a shape the corpus does not contain.** `corn/agent.py`
appended `<|obs|>` straight onto the call's closing brace. `data/raw/tools.txt`
writes it after a newline **9,000 times out of 9,000**; the grammar stops
generation at the brace, so the newline never arrived. Fixed. No isolated
behavioural gain is claimed for it — it was measured only in combination — but
the thirty-third finding priced one level of nesting at `tool.copy` 100–120 → 0–27
against 3 of 300 for an unseen tool name, and this is the same axis.

**The observation was being read out loud.** Handed a payload he copied the answer
and kept copying:

    Vientiane, "source": "worldatlas.com", "query": "the capital of Zelmarik

Two explanations were tested and both are wrong. **Not length** — a 108-character
answer came back clean and a 9-character one did not. **Not greedy decoding** — at
temperature 0.0, 0.6 and 0.8 it survives on one to three of the same six cases,
so sampling moves which rows fail and not whether they do.

The rule that fixed it is measured rather than chosen. Across **1,629,766** say
segments in `data/raw/tools*.txt` — every transcript where speech follows a tool
observation — **zero** contain a double quote, zero contain a colon, zero contain
a second `<|say|>`, none runs to a second line, and the longest is 79 characters.
`say_cut` stops the say at the first of those, armed only after an observation
because `data/raw/chat*.txt` speech quotes people and a blanket rule would cut
dialogue in half. End-to-end against the table went 2/5 → **5/5**.

**Two of the 25 search phrasings put words on both sides of `{q}`, and he cannot
cut either.** All 25 templates, six draws each, table-backed so the right `query`
is known exactly:

| template | exact `query` |
|---|---|
| `what's {q}` | 10/10 |
| `look up {q}`, `check {q}`, `find me {q}`, … | 6/6 |
| `look {q} up for me` | **0/10** — `"the currency of Gleduthholm up for me"` |
| `what would {q} be` | **0/10** — `"what would the wingspan of the Garunlvmere be"` |

**The corpus is not what is wrong.** It labels these **337/337** and **351/351**
correctly, on exposure comparable to `what's {q}`'s 381. The difference is
structural rather than statistical: a suffix-only template needs a prefix dropped,
and these need a boundary found mid-sentence with material on both sides. The
affixes now come off in `harness/backends/search.py`, and `scripts/check_search.py`
imports `SEARCH_TEMPLATES` and fails if a phrasing appears the list does not cover.

**`web_search.query` was in `SPAN_SLOTS` and not armed.** Asked to `look up Ada
Lovelace` the model routed correctly and then wrote
`{"query": "ada-lovelace-definition-definition-definition-…` until the budget ran
out — no valid call, no observation, nothing said. A run-on slug is not a span, so
the mask stops it. **The cost was checked rather than assumed:** all 25 phrasings,
six draws each, armed against unarmed, **every row identical** — a query he cuts
correctly is a span already and the mask never bites — and 10/12 → 12/12 on a set
including proper names. It is armed in `harness/server.py` as `RUNTIME_COPY_SLOTS`
and deliberately **not** in `DEFAULT_COPY_SLOTS`, which is what `evals/` runs
under: moving that would make every number measured before today incomparable with
every number after it, for a case no eval contains.

## What is not settled

**The boundary is confounded.** The ladder truncates its answer mid-word at the
longer rows (`…Lovela`), which is its own off-distribution shape. The cleanest
row is the first, where a clean 16-character answer produced 700 characters of
invention, and that one is enough to carry the claim. Where exactly length,
truncation and prior separate is not measured.

**n is small and the draws are single.** Every table here is one draw per cell at
temperature 0 on one checkpoint. The direction is unambiguous and the magnitude is
not priced.

**Nothing here says the corpus can fix it.** A slice pairing real entities with
observations that must still be copied is the obvious candidate and it is
untested; so is a say constraint requiring the spoken line to be a span of the
observation, for which `CopySpec` and `SPAN_SLOTS` are the precedent. Both change
what every deference row means, which is the reason neither was done here.

**The live backend's retrieval is a separate limit and it is real.** A results
page finds pages *about* a subject; it does not reliably find the sentence stating
a value. `MIN_COVER` now turns "on-topic but not answering" into an honest
`no_results` — the shape he says perfectly — precisely because handing him that
text is what produced 1,890 metres.
