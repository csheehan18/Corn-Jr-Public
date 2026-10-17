# Fifty-sixth finding — the official split guarantees questions and not documents, so 14% of the eval was in the slice, and the training half cannot be read by the code that reads the eval half

**Cost:** 0 s of new scoring on record; it reads 2 cards scored for an earlier finding (`nano20m`, `nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`docs/PLAN-WEB-SEARCH.md`'s WS-B, built on 2026-08-24: `corn/extractgen.py`,
`scripts/gen_extract.py`, `scripts/check_extract_slice.py`,
`configs/mix_v3_extract.py` and two nano configs. **Nothing has trained.** No
weights changed at any point, and every number here is a property of a corpus
file or of the code that reads one.

The slice itself came out where the pre-registration said it should — balanced
50/50, one pass at 5%, no `repeat`:

    NQ train rows        19,920      65 shards, 14,096 answerable / 5,824 not
    dropped, article        409      2.05%, decontamination -- see below
    transcripts          48,478      24,239 answerable / 24,239 absent
    tokens            8,168,451      1.25x the 6,546,719 pledged at 5%
    distinct windows     44,855      1.08 uses each
    distinct replies     31,699      1.53 uses each

1.08 uses per window is the number that matters for the thirty-fourth finding's
rule: the two slots that taught reading sat at 1.0 and 1.2 uses and the three
that taught recitation sat at 2,096, 2,130 and 48,088. Nothing here is close to
the bad end.

What is worth recording is that **three of the premises the slice was built on
were false, and two of them were the kind that pass their own guard.**

## 1. The split is annotated to two different depths, and every filter read the wrong one

`prepare_nq.py` was written against NQ `dev` and its filters all turn on
annotator agreement — "is this paragraph even on topic should not be one
annotator's opinion" is the docstring's own argument. Measured directly rather
than taken from the card:

    dev     len(annotations["long_answer"]) == 5   on every row
    train   len(annotations["long_answer"]) == 1   on every row

So on `train`:

    agreed = [c for c, n in picked.items() if n >= 2]

is unsatisfiable, and one shard read **1,071 rows and kept 0** — 1,061 dropped
as "no agreed long answer". That is the loud failure and it cost one 192 MB
shard to find instead of the 13 GB a full pull would have been.

**The quiet one is worse and would not have failed anything.** The unanswerable
arm read

    elif 5 - n_with >= 4:

with the 5 hardcoded. On train `n_with` is 0 or 1, so `5 - 1 = 4` passes too:
the filter **fails open** and labels a row *whose annotator did answer* as
having no answer. Those rows would have gone straight into the abstention class
— the class that exists to teach an honest miss, and the one the plan already
names as having no runtime floor, so nothing downstream could have caught it.

`prepare_nq.agreement(n_ann)` now returns both thresholds from the split's
depth: `min_agree` is 2 at five annotators and 1 at one, `min_silent` is
`max(1, n_ann - 1)` — 4 of 5 on dev, 1 of 1 on train. Written as `n_ann - 1` it
would have been 0 on train and admitted everything, which is the same defect
one layer along.

**`data/raw/nq-dev.jsonl` regenerates byte-identically**, sha256
`1f92680e...`, 721 answerable and 282 unanswerable unchanged — asserted twice,
once after the annotator change and once after the HTML filter below. The frozen
`extract.*` rows cut from it did not move.

## 2. "Decontamination by construction" passes its own check and is not true

This is the one to remember. Both `prepare_nq.py` and `PLAN-WEB-SEARCH.md` argue
that cutting the eval from `dev` and the slice from `train` means the two never
touch, and `check_nq.py` §7 asserts it — no shared id, no shared question — and
**passes**.

The first build of the slice then contained:

    56 of the frozen eval's 396 windows        14.1%
    0  shared ids
    0  shared questions

NQ annotates the same Wikipedia paragraph against different queries in both
splits. **65 dev passages used by the eval appear verbatim in train**, carrying
113 train rows, and the queries are near-paraphrases of each other:

    eval   where is the inscription on the statue of liberty
    train  who wrote the message on the statue of liberty
    train  when was the statue of liberty poem written

One paragraph, three questions, two splits. 409 train rows share a Wikipedia
*article* with an eval item.

**An official split is a statement about questions, not about documents.** That
sentence is the finding. The dataset's guarantee is exactly the one it
advertises and it is not the guarantee an extraction eval needs, because the
eval scores a model on a *window of text* and the leak is in the text.

The exclusion is therefore by **article**, not by window and not by passage. A
window match catches only the exact 64 tokens and `STRIDE` is 32, so a window
offset by one stride leaks half its text and matches nothing; a passage match
catches the paragraph but not the adjacent paragraph of the same article that
some other question selected. The article closes both. It costs **2.05% of the
train rows**, which is cheap against a row this is the before-number for, and it
is read out of the frozen eval's own `url` field rather than out of gitignored
`nq-dev.jsonl` — a decontamination step should not depend on a file that can be
regenerated differently.

This is the second time this project's hygiene has needed a boundary its source
did not supply, and it lands the same way as `gen_tools.py`'s rule that a shared
*first name* between the composed book and the holdout fails the build.

## 3. The row bounds the vocabulary the slice can teach

`extract.abstain` passes a reply only if it contains a phrase from
`MISS_MARKERS` **and** carries no content word outside `_MISS_VOCAB`, the
question and `FRAME`. Three of the first nine abstention phrasings written for
the slice read as perfectly good abstentions and scored as failures:

    Nothing useful about {q}, I'm afraid.   hedged_answer -- the `m` that
                                            an apostrophe leaves behind
    This doesn't say anything about {q}.    hedged_answer -- `this`; FRAME
                                            carries `that` and not `this`
    There's nothing here about {q}.         no_miss -- `nothing about` is a
                                            marker, `nothing here about` is not

The phrasings were changed rather than the scorer, and that direction is forced:
`extract.abstain` is frozen at 0/200 and widening `_is_miss` would make the
baseline the pilot is read against incomparable. But the cost is real and worth
naming — **the abstention vocabulary this slice can teach is bounded by the row
that scores it**, so the cardinality argument that carried `sayvar` is weaker
here, and a model abstaining in words the row does not credit will read as a
failure it is not.

A fourth constraint appeared at the same place. `score_extract_abstain` runs
`_length_verdict` first, so a long question echoed into a reply is long against
a short window and reads `wrote_own` whatever it says. That is why five of the
fourteen phrasings do not name the query back: they are a length budget, not a
style. Twelve transcripts in the first build tripped it.

## 4. The rule that falls out: never train a target its own row scores wrong

Those twelve are a small number attached to a large rule, now enforced in
`corn/extractgen.scores_as_target`: **every transcript in the slice is a target
its own eval row would score as a pass**, checked at generation by calling the
scorer, and re-checked by the guard on the file.

It matters more than the twelve. The pilot reads movement on `extract.span` and
`extract.abstain`, so a slice teaching replies those rows refuse would depress
the very numbers it was built to move — and the arm would read as a failed
intervention rather than as a mislabelled corpus. That is the thirty-seventh
finding's shape (an arm that cost a run and taught nothing) with a cause nobody
would have looked for.

## 5. Two smaller things

**BPE decode → encode is not the identity, and the runtime batches on the
assumption that it is.** `windows()` cuts equal `WIDTH`-token slices and returns
them *decoded*; re-encoding those strings gives 65–68 tokens for 7 of 1,197 dev
windows, so **4 of 300 passages produce prompts of unequal length**.
`BatchedReader` raises `ValueError` on those deliberately rather than padding
(`StaticCache.pos` is one shared scalar and `corn/model.py` uses learned
absolute positions, so neither padding direction is available). So
`read_passage` will throw on ~1.3% of passages. It cannot be fixed in
`windows()` — `make_evals.py` calls it, and changing its output would move the
frozen eval windows — so it belongs at the `read_passage`/`BatchedReader` seam
and is tracked separately. The slice is unaffected; it only embeds the string.

**One row in 19,921 carried a leftover HTML tag**, `</ref >` — a wiki citation
closer that NQ tokenises with a space, so `is_html` never flags it and it
survives into the passage. None in dev, which is why it took a slice-sized
source to surface. Now a counted drop rather than a scrub, on the same terms as
the U+FFFD check beside it.

## What this does not say

Nothing here is a claim about a trained model. The slice is built, guarded and
unread by any optimiser. The pilot — `nano20m` at 5%, two seeds against a
two-seed `nano20m_v3` control, read as range against range — is what turns any
of it into a result, and the pre-registered quantities are unchanged:
`extract.span` from 9/200, `extract.abstain` from 0/200, `continued_payload`
from 69/400 as the falsifiable one, with `tool.copy` 120/120 and
`tool.copy_wide` 300/300 as the regression watch.

`lm web` is **expected to move** and is not a regression: web is the donor at
49.3773% → 44.3773%, and the forty-fourth finding measured that response as
linear over two doses with no behaviour row moving.
