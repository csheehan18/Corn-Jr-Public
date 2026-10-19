# Two thirds of one dataset's tool calls were invalid JSON

**Full result:** The copy audit called a sound slice memorisable because its own value class stops at an escaped quote, and underneath that false positive two thirds of `relpairs.txt`'s tool calls are not valid JSON, written past the slice's own guard because that guard parsed the observation and threw the call away

**Cost:** 13.1 min of scoring on the 3 cards first cited here (`corn_jr_260m_v4_ftxrel`, `nano20m_v3_extract_seed2`, `nano20m_v3_extract_widetype_seed2`); it also reads 3 cards scored for an earlier finding (`nano20m_v3_extract`, `nano20m_v3_extract_narrowtype`, `nano20m_v3_extract_widetype`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The two red rows in `check_all.py` at `6dee3e5a`, run down. No model, no GPU,
no network: every measurement here is a regex over `data/raw/` or a
re-derivation from saved generations. One of the two is a chain of three
failures that hid each other; the other is a decision about the record and is
left to the owner with the diagnosis made.

## 1. `check_copyable` — the detector, not the corpus

`relpairs.txt`'s window slot read **33 effective values against a floor of
1,000**, which is this file's definition of a memorisable slot and the bug that
cost three findings. The slice is fine.

Almost every slot in the table reads a JSON field with
`"field": "(?P<v>[^"]*)"`, which stops at the first quote **including an
escaped one**. Every question in this slice names a quoted work —
`who wrote "The Broken Hinterland"` — so every value was cut to the same
one-character prefix `\`, and a slot whose values are all one string is exactly
what "memorisable" means. **The blindness announces itself as the loudest
possible false positive, which is the only reason it was ever found.**

Read with an escape-aware value class the same slice reads **15,432 effective
at 4.00 uses**, which reproduces the number in its own declaration to the
digit — so the declaration was written correctly and the pattern was wrong
underneath it.

**Six slots across four slices were being mis-read**, all in the same
direction — the naive class can only ever under-count:

    relpairs.txt      window            33 -> 15,432    FAIL -> ok
    relpairs.txt      search query     262 ->  2,450    FAIL -> ok
    extract.txt       window        35,420 -> 43,226      ok -> ok
    extract_5b.txt    window       118,002 -> 148,756     ok -> ok
    extract_clause    window       118,000 -> 148,754     ok -> ok
    extract_iso.txt   window        10,945 -> 19,336      ok -> ok

The four `extract*` slices are real Wikipedia prose, which quotes things; they
passed anyway and their recorded numbers were simply low.

**And `paired_names.txt` was undeclared** — the condition this file says
matters most, since "a slice nobody has audited is how all three findings
happened". It is `corn/pairedgen.py`'s names arm, declared here at 36,154
effective windows and **1,598 effective queries at 62 uses each**, which is the
thinnest slot in the table. It clears the floor on its entity vocabulary alone
and its relation phrases are deliberately few — that is what the arm *is* — so
it is declared with the number written down rather than widened, on
`tools.txt`'s contact-slot precedent.

**The repair that matters is the third one.** `JSON_V` fixes the six slots, but
a value class is exactly the kind of thing that goes quietly wrong again, so
the blindness is now a row: `check_copyable` fails if any declared slot
captures a value ending in an **odd** run of trailing backslashes, which is the
unambiguous signature of a capture cut mid-escape. An even run is a real
escaped backslash. A slot that trips it is not measuring a bad slice, it is
measuring nothing trustworthy — which is worse, because a floor comparison
against a truncated value is a number with no meaning rather than a number
that is wrong.

## 2. Underneath it: 41,152 malformed calls, and the guard that could not see them

Chasing the truncation into the file found this, which is the real result:

    <|obs|>{"answer": "\"The Broken Hinterland\" is a standard ...",
            "source": "example.org",
            "query": "who wrote \"The Broken Hinterland\""}      <- correct
    <|call|>{"name": "web_search",
             "arguments": {"query": "who wrote "The Broken Hinterland""}}
                                                                <- not JSON

**41,152 of `relpairs.txt`'s 61,728 calls (66.7%) do not parse**, against
**0 of its 61,728 observations** and **0 in every other slice in
`data/raw/`** — counted over all of them, because no other generator puts a
quote in a question.

The cause is one line. `corn/extract.py`'s `PROMPT` builds the observation with
`json.dumps` and hand-writes the call as a literal with `{question}`
interpolated straight into a JSON string. That is correct for every question
without a quote and silently malformed for every question with one. It also
means a question with a **non-ASCII character** is written raw in the call and
`\u`-escaped in the observation beside it, so the two have disagreed for as
long as both have existed.

**Three guards had a chance and none took it.** `check_relpairs.py` parses the
observation and splits the call into a variable named `_call` that it never
looks at — so the half that was correct was checked and the half that was
broken was discarded. `check_spans.py`, `check_iso.py` and
`check_extract_slice.py` all assert that the artefacts rebuild through
`worker_prompt`, which they did, because the artefacts and the generator were
*consistently* wrong. And `check_copyable.py` was blind for section 1's reason.
A round trip through a broken writer is not a check on the writer.

**What it costs, stated exactly.** `relpairs.txt` appears in one config,
`configs/mix_v4_ft_xrel.py`, and in **no shipped corpus** — not `mix_v3_5b`,
which pretrained the released model, and not `mix_v4_ft_social8`, which
fine-tuned the checkpoint that ships. **So the released weights were never
trained on a malformed call.** What was trained on them is the
`corn_jr_260m_v4_ftxrel` arm, and any reading taken off that arm is confounded
by a call syntax the runtime's own `validate_call` would refuse.

## 3. Why the one-line fix is not in this commit

It was written, and it was taken out again. `json.dumps` on the call reproduces
the old literal byte for byte **only** for questions that carry neither a quote
nor a non-ASCII character, and `extract.txt` alone has 185 blocks that carry
one. Regenerating the `extract*` slices to match would change bytes inside
`mix_v3_5b` — the corpus that produced the shipped checkpoint — and the three
rebuild guards went red the moment the writer moved, which is them working.

This project already has the precedent and it points the other way from a
rewrite: `configs/mix_v4_ft_social11.py` records that `data/raw/social8.txt`
"is no longer reproducible from today's generator" rather than regenerating it.
So the writer fix is **sequenced with the 1.0 corpus rebuild**, where the
slices are being rewritten anyway, and until then:

* `check_relpairs.py` now parses the call, **reports** the malformed count on
  every run with a pointer to this finding, and asserts on the calls that do
  parse that each asks for what its observation answers. A known defect with a
  number on it beats a red run that says nothing new, and beats the silence it
  had before.
* `check_copyable.py` records that the query slot's 2,450 is itself a symptom —
  regenerated with the escaping fixed it reads **14,329**, which is the number
  to compare against after the rebuild.
* **`scripts/check_calls.py` fences it**, and this is the part the first
  version of this finding left out. Deferring the writer fix left the bug fixed
  nowhere *and* fenced nowhere: `worker_prompt` is what `gen_extract.py` and
  `gen_spans.py` write through as well, so a new slice with a quoted or
  non-ASCII question would inherit it and `check_relpairs` — which reads one
  file — would not say so. The new guard parses every `<|call|>` in
  `data/raw/` and holds `relpairs.txt` to **exactly 41,152**, not to a
  threshold: a slice that gets better fails it as loudly as one that gets
  worse, because both mean the entry is stale, and the entry is meant to be
  deleted by the rebuild rather than kept. A second section fails if the
  exception names a file that no longer exists.

  Verified by making it fail: a one-block slice written through today's
  `worker_prompt` with the question `who wrote "Iron Quarry"` produces
  `{"query": "who wrote "Iron Quarry""}` and the guard refuses it, naming this
  finding. A guard nobody has watched fail is not known to work, which is the
  lesson three of the four detectors in this document each taught separately.

## 4. `check_churn` — a decision, not a bug, and it is the owner's

Six `nano20m_v3_extract*` cards fail to re-derive. **No verdict changed side**:
the pass count is identical on every row and only the *name* a failure is filed
under moved, by one or two items a card. Two scorer changes explain it, both
deliberate and both dated — the near-miss split of 2026-08-31, which `verify()`
already folds for, and the grounding rule at `e46ac9ee`, which moves items
between `wrong_span` and `invented` because `invented` *is* "failed `grounded`"
and that predicate changed.

Inspecting the nine items the current scorer calls `invented` on
`nano20m_v3_extract_narrowtype`: seven have no stray word at all and are
degenerate echoes of the question — "who is nebula on guardians of the galaxy"
answered "Nebula.", "who is the character of santa claus based on" answered
"Santa Claus, according to wikipedia.org." — which fail `grounded`'s second
condition rather than its first. Two are genuine invention (`Northam` →
`Southam`). Every one of the nine is correctly refused under the current rule.

**So the scorer is right and the cards are stale derived data, and this check
firing is it doing its job** — it exists to catch "a scorer changing underneath
a file already on disk".

**The owner's call, taken 2026-09-07: re-derive.** The `why` histogram is a
pure function of two things that both still exist — the saved generations, and
the scorer at the revision the card itself names in `source.rev` — so it is a
cache rather than a record, and a cache that disagrees with its inputs should
be recomputed. The measurement is the pass count, and it does not move. The
argument that settled it is what a permanently red row becomes: `check_all`
reading "70 ran, 1 failed" forever, with everyone knowing the 1 is
*"just churn, ignore it"*, is a guard that has stopped working — and it stops
working silently, which is the third instance of that failure in this document
alone.

**The four rows, before and after**, recorded here because re-deriving the card
is the only place these numbers lived and the old scorer is awkward to re-run
(`extract_attribute.py` imports a symbol the pre-`e46ac9ee` `evals.py` does not
define):

    nano20m_v3_extract_narrowtype       wrong_span 34 -> 33   invented  8 -> 9
    nano20m_v3_extract_seed2            wrong_span 32 -> 31   invented 12 -> 13
    nano20m_v3_extract_widetype         wrong_span 27 -> 26   invented 11 -> 12
    nano20m_v3_extract_widetype_seed2   wrong_span 43 -> 41   invented 21 -> 23

`abstained`, `wrote_own`, `recited` and `continued_payload` are unchanged on
every row, as is every pass count.

**One published number moves with them, and it is annotated rather than
edited.** The fifty-seventh finding quotes `invented 105 -> 7 / 12` across the
two seeds; the `12` is `nano20m_v3_extract_seed2` and now reads 13. A note
beside it says so. The claim it supports — confabulation falling from 105 of
200 to single figures — does not depend on the item. Findings 58's numbers are
decline rates and type shares and are untouched; no other finding or plan
quotes a failure bucket from these six cards.

**The second half of the red was not a scorer disagreement at all.** All six
committed attribution files carried **zero rows** for `extract.span_tight` —
the row the eighty-second finding added after they were written — so the drift
check was comparing 0 rows against 200. Re-deriving them through
`scripts/extract_attribute.py` put the row in, and the next run immediately
failed a *different* check: "every extraction row is a row `churn.py` knows".
It was not. `churn.ROWS` never learned `extract.span_tight` either, and could
not be caught not knowing it while every artefact on disk predated the row.
**A table that is only ever checked against artefacts older than the thing it
is missing is not being checked.** Both are fixed; the guard found the second
one itself, one run after the first was cleared.

What is also changed is the failure message, which said "do not trust either
until they do not" and now names which buckets moved, that no verdict changed
side, and where the two known scorer changes are recorded — so the next time
this fires the diagnosis is in the output rather than in a session.

Left unexplained: whether any *other* tracked card in `evals/results/` is stale
against today's scorers. `check_churn` walks the extract rows only, and the
same question applies to every row a scorer has been edited under since it was
written — which is a one-evening replay over saved generations and would either
close the question or produce a list. The `span_tight` result above raises the
prior: that row was missing from six files for weeks and nothing said so.

## Amended 2026-10-08 -- the writer fixed, every slice regenerated, and the bug was in three more files

ROADMAP C0 discharged PLAN-1-0 ground rule 6. `corn.extract.PROMPT` now takes
its call from `corn.tools.call_text`, the one on-the-wire form every tool
generator already writes, and every slice `worker_prompt` writes was
regenerated through it. The rows that moved are exactly the rows whose question
carries a quote or a non-ASCII character:

    slice                  rows moved   what moved
    extract.txt                   185   the call line
    extract_5b.txt                866   the call line
    extract_clause.txt            866   the call line
    extract_iso.txt                44   the call line
    relpairs.txt               41,152   re-sampled (below)
    spans_synth.jsonl          41,196   prompt; spans on the 20,598 answerable
    spans_nq.jsonl              1,659   prompt; spans on the 401 answerable
    spans_squad.jsonl          17,354   prompt; spans on the 3,675 answerable

Each regeneration was checked against a second one run with the old call
patched back in. `relpairs.txt` and `spans_synth.jsonl` came back byte-identical
to the files on disk, so every difference in them is the fix. `relpairs.txt`
is re-sampled rather than edited in place: an escaped quote costs tokens, and
the same 9.7M-token budget now holds 60,912 blocks against 61,728. Its query
slot reads 14,329 effective values in `check_copyable`, which is the number
this finding's audit predicted for a fixed regeneration. `extract_5b.txt` also
lost two blocks that the old-writer run loses too. That is generator drift
since 2026-08-28, not this fix.

**The fence had a hole of its own.** `scripts/check_calls.py` claimed every
call in `data/raw/`, but globbed `*.txt`. The labelled-window files are
`.jsonl` and carry each transcript as an escaped JSON string, and two of them
held 53,201 malformed calls the guard never read: 41,152 in `spans_synth.jsonl`
and 12,049 in `spans_squad.jsonl`. It reads `.jsonl` now, through one unescape,
and `EXPECTED` is empty.

**What did not move.** Four frozen eval items store a prompt with a curly
apostrophe written raw in the call: three in `evals/extract.jsonl` and one in
`evals/extract_phrase.jsonl`. They stay as built, under PLAN-FINETUNE-V4 ground
rule 2, and no guard rebuilds them. The runtime does move. `harness/backends/
read.py` builds its prompts through `worker_prompt`, so on v0.5 a question
carrying a quote or a non-ASCII character is now shown the escaped call. That
is 4 of NQ-dev's 1,003 questions, and Population A is drawn from them. Not
re-read; a Population A number taken after this commit is a bound on those
four.
