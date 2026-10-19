# Scored fairly, the boundary model trails plain generation

**Full result:** The extent headroom was containment, the real repair is `span_loose - span`, and the span head is worse than generation once the column can tell a region from an answer

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

One read-only replay on the frozen `checkpoints/corn_jr_260m_v4/ckpt.pt`, run
2026-09-01 over generations already on disk. No training, no GPU, no forward
pass. `scripts/probe_recut.py`, record `evals/results/recut.json`, replicated on
both `evals/extract.jsonl` and the article-decontaminated
`evals/extract_phrase.jsonl`.

## What was being tested

`docs/READ-COMPARISON.md` identified the largest headroom anyone had found: of
the 65 attempted-and-wrong items on the frozen eval, 27 already share a gold
content word — right neighbourhood, wrong extent — against 38 disjoint. A
perfect re-cut reads span 121/200, joint 242 against greedy's 215, `acc | att`
0.591 → 0.761. It was the only route on the record to the conditional-accuracy
wall the eighty-first finding's thread never moved.

The design under test was a **re-cut**: start from the string the generator
actually said, locate it in the window, change its extent once. It fixes the two
things that killed the previous designs by construction — it never fires on a
window the generator declined, so the abstain row is preserved without a gate
(`probe_spanhead`'s defect); and it makes one decision, not N sequential ones
(`probe_shrink`'s defect).

## The central result, and it is a control rather than a bar

**`extract.span` credits containment, so padding a span with its neighbours buys
the row without repairing anything.** The control is `degenerate`: blindly extend
every located assertion by the full `(L, R)`, no trigger, no selection, no model.

| L,R | oracle span | **degenerate span** | oracle exact | degenerate exact |
|---|---|---|---|---|
| 0,2 | 99 | **99** | 92 | 20 |
| 1,2 | 109 | **109** | 100 | 17 |
| 2,4 | 116 | **116** | 103 | 3 |
| 3,5 | 122 | **122** | 105 | 2 |
| 5,8 | 132 | **131** | 107 | 2 |

**On `span` the blind pad equals the oracle at every width**, and at (5,8) it
reads 131 / joint 252 / `acc | att` 0.824 — better than the "perfect re-cut" the
design was justified by. The 122 / 243 / 0.767 target, and the 121 / 242 / 0.761
in `READ-COMPARISON.md` that produced it, are padding. **That number is mine and
it is retracted here.**

`_length_verdict` does not catch it: `RECITED_FRACTION` is 0.8, so a reply must
reach 80% of the window's content words before it counts as recited, and a
nine-word pad of a 36-word window is nowhere near it. **The recitation guard is
calibrated for whole-window recitation and is blind to local padding.**

## The column that works, and the number it gives

`exact` — credited by `score_extract_span` **and** asserting nothing beyond the
gold: every novel content word (not question, not source, not `FRAME`) is a gold
word. It is `score_extract_span`'s own `near_miss_clip` test run as a
requirement rather than as a forgiveness, and padding cannot buy it.

Greedy reads **94 / 93 / 89** on span / sized / exact — a generated sentence
averages 4.3 content words against a 2.3-word gold, so containment and identity
nearly coincide and the three columns agree. Only span-emitting policies come
apart on them.

On `exact` the honest re-cut ceiling is **+16 items**, not +27. Split by what
greedy did:

| greedy bucket | repairable |
|---|---|
| `near_miss_clip` | 8 |
| `near_miss_det` | 5 |
| `invented` | 3 |
| **`wrong_span`** | **0** |

Not one of the 36 `wrong_span` failures is reachable by re-cutting its own
assertion. And `extract.span_loose` — strict passes plus both near-miss buckets —
**already reads 110 against `span`'s 94 on every card**. The repair ceiling is
`span_loose - span`, a quantity that has been printed beside the row all along.
The other 11 of the 27 were containment.

The partition itself is sound and turns on exactly one item: FRAME-stripped it is
27 / 38, and counting `FRAME` words as overlap gives 28 / 37, the extra being
`extract-0087` whose entire overlap with its gold is the preposition "of".
Locating both strings in the window confirms it — 25 of the 27 are at distance 0,
all 11 `near_miss_clip` and all 5 `near_miss_det` at distance 0, and 23 of 36
`wrong_span` more than five words away.

## The trigger, which is where it dies

The structural filter proposed as a verifier-free route — fire where the head's
span overlaps but does not equal the generator's — fires on 68 items to reach 12
repairable ones, and 35 of the 68 are already correct:

| head span vs generator span | exact-correct | repairable | other-wrong |
|---|---|---|---|
| equal | 33 | 1 | 9 |
| head contains generator | 33 | 12 | 20 |
| generator contains head | 2 | 0 | 1 |
| disjoint | 20 | 3 | 21 |

| policy | span | exact | fixed | broke | joint(exact) |
|---|---|---|---|---|---|
| greedy | 94 | **89** | — | — | **210** |
| head: always replace | 96 | 45 | 10 | 54 | 166 |
| head: overlap not equal | 110 | 62 | 5 | 32 | 183 |
| head: strictly contains | 112 | 63 | 4 | 30 | 184 |

**Net −27 on `exact` while reading +16 on `span`** — the containment illusion a
second time, in the trigger rather than the action. Extension size does not
separate the classes either: at one added word the head widens 4 repairable items
and 4 already-correct ones.

## One rule survives, and it buys the class the repo calls orthography

Model-free and structural. `DET` prepends the window's own determiner when the
assertion is immediately preceded by `the`/`a`/`an`.

| rule | fires | span | exact | fixed | broke | joint(exact) |
|---|---|---|---|---|---|---|
| **DET** | 14 | 100 | **94** | **5** | **0** | **215** |
| NAME | 31 | 101 | 80 | 3 | 12 | 201 |
| NUM | 15 | 96 | 83 | 2 | 8 | 204 |
| DET+NAME | 42 | 104 | 83 | 6 | 12 | 204 |

**`DET`'s zero breakage is structural, not lucky**: determiners are `FRAME`
words, so prepending one cannot add a novel content word and cannot cost `exact`.
It replicates on the decontaminated phrase eval — fires 12, fixes 3, breaks 0,
joint(exact) 58 → 61. Pooled across both evals it is **8 fixed, 0 broken, exact
binomial p = 0.0078**.

**And it recovers the class the scorer deliberately declines to credit.**
`score_extract_span`'s own note: *"NQ writes golds like 'the Ramones' and 'The
aorta' where the article is orthography, not content."* The one repair that
survives its control converts `near_miss_det` and nothing else. `NAME` and `NUM`,
which would reach the 8 real `near_miss_clip` items, break more than they fix.

## The same column, applied where nobody had looked

| policy | span | sized | exact | joint(span) | joint(exact) |
|---|---|---|---|---|---|
| greedy | 94 | **93** | **89** | 215 | 210 |
| span head, ungated | 113 | 90 | 55 | ~113 | ~55 |
| span head, refusal-gated | 97 | **74** | **45** | 218 | 166 |

Gated head against greedy on the answer-sized column: greedy-only 36, head-only
17, **exact p = 0.0127 against the head**. On the phrase eval, 15 against 24.

`fea95f04` retracted the head's 113 to 97 gated and called it parity at p = 0.78.
**That retraction is on the containment column and inherits its defect.** The
head's spans average 6.2 content words against greedy's 4.3 and a gold of 2.3.
The span head is not at parity with generation once the column can tell a region
from an answer — it is significantly worse, and this is the third defect found in
the same result.

## And the same column re-reads a training arm

Applied to the four fine-tuned arms, the invariant table from
`docs/INDEPENDENT-READ.md` holds on all three columns for three of them and
collapses for the fourth:

| arm | span | sized | exact | attempted | `acc \| att` | `sized \| att` |
|---|---|---|---|---|---|---|
| v4 (frozen) | 94 | 93 | 89 | 159 | 0.591 | 0.585 |
| ftxctl | 97 | 96 | 91 | 162 | 0.599 | 0.593 |
| ftxmask | 96 | 94 | 89 | 163 | 0.589 | 0.577 |
| **ftxclause** | **100** | **21** | **2** | 166 | **0.602** | **0.127** |
| ftxrel | 66 | 65 | 60 | 114 | 0.579 | 0.570 |

**`ftxclause` reads the best `span` of any arm and emits almost no answers.** Its
replies average **17.96 content words** against the frozen model's 4.93, its
median reply is 17 for a gold averaging 2.3, and what it emits is the window's
sentence:

    gold  Jourdan Miller
    reply The winner was 19-year-old Jourdan Miller from Bend, Oregon.

    gold  July 4, 1776
    reply On July 4, 1776, the Second Continental Congress, meeting in
          Philadelphia, declared the independence of "the United States of
          America" in the Declaration of Independence.

Its `span_loose` is **100, equal to its `span`**, where its own control `ftxmask`
reads 114 against 96 — a diagnostic signature, because a reply long enough to
carry the whole sentence can no longer *clip* the gold, so both near-miss buckets
empty into the strict row.

**The risk was named in advance and the chosen instrument could not see it.**
`configs/mix_v4_ft_xclause.py` read (d) watches `extract.brevity` for exactly
this — *"sentence replies are longer ... the model's replies on the frozen eval
may lengthen"* — and names the failure state, *"Regression (abstain or brevity
falls apart)"*. `extract.brevity` reads **383/400**, a mild-looking 17-item cost.
Its test is `len(said) < n_window`, and the mean window is 36.2 content words, so
a 17.96-word reply passes it by a factor of two. **The guard is a whole-window
guard, like `RECITED_FRACTION`, and both are blind at sentence scale.** The same
config also states outright that *"a clause reply that carries the gold plus its
sentence still passes strict containment"* — and then selects the more permissive
`span_loose` as its primary.

Nothing was banked on the arm: the eighty-first finding's thread had already
discarded it on decontamination (openers +0, abstention 37/53 → 13/53 at
p = 3e-06). What this adds is the mechanism. It was not only a willingness knob;
it changed the *shape* of the emission from an answer to a sentence, and the row
that made it look like the best arm on the record is that change being credited.

It also corrects one cell of my own invariant table: `ftxclause`'s 0.602 is not
the top of the band, it is an arm that stopped answering. On `sized | att` the
four answering arms read **0.570 – 0.593**, a 2.3-point band as before, and the
apparent counterexample was recitation.

## What it settles

* **The extent headroom is 16 items, not 27**, it is `span_loose - span`, and it
  was already on the card.
* **`extract.span` is not a safe row for any policy that emits window text.**
  `probe_shrink.py` discovered this about itself and built `answer_sized`;
  `probe_spanhead.py` never did, and neither did the re-cut framing.
  `probe_recut.answer_sized` is `probe_shrink`'s, unchanged, so the files agree.
* **`wrong_span` is not a repair problem.** Zero of 36 are reachable by re-cutting
  the generator's own assertion, which retires the "right neighbourhood, wrong
  extent" reading of that bucket entirely.
* **The trigger remains the blocker**, and the structural agreement filter does
  not avoid it. The verifier question is untouched.
* **`acc | att` did not move.** The one policy that survives its control takes it
  from 0.591 to 0.629 on the frozen eval and 0.453 to 0.509 on the phrase eval,
  entirely on determiners.
* **`extract.brevity` needs recalibrating.** It compares the reply to the
  *window* when the question is whether the reply is an *answer*. Against the
  gold rather than the window it would have read `ftxclause` at 21/166 instead of
  383/400 and the arm's shape change would have been visible on the card. This is
  a one-line change to a shipped row and is the cheapest thing on this list.

## What shipped from it

`extract.span_tight` — the third rung of a ladder read off one decode:

    extract.span_loose   strict pass, or a gold missing only its article,
                         or a gold stated in part
    extract.span         the gold's content words are in the reply
    extract.span_tight   ... and the reply is answer-sized

Answerable only, like `span_loose`. Re-scored over the retained generations:

| arm | loose | span | **tight** | `tight \| att` | abstain | joint(tight) |
|---|---|---|---|---|---|---|
| v4 (frozen) | 110 | 94 | **93** | 0.585 | 121 | 214 |
| ftxctl | 113 | 97 | **96** | 0.593 | 133 | 229 |
| ftxmask | 114 | 96 | **94** | 0.577 | 127 | 221 |
| **ftxclause** | 100 | 100 | **21** | **0.127** | 66 | **87** |
| ftxrel | 74 | 66 | **65** | 0.570 | 162 | 227 |

`ftxclause`'s new bucket is `not_answer_sized` 79. The ladder
`loose >= span >= tight` is asserted on all five arms and is a guard case.

**Three things were considered and rejected, and the reasoning is the finding
as much as the row is.**

* **Mutating `extract.brevity` instead.** That was the recommendation this work
  started from — *"one line, on a shipped row"* — and it is wrong. Changing a
  threshold in place silently rewrites every card in `evals/results/`, which is
  the argument `score_extract_span` makes for its own frozen criterion, and
  `extract.span_loose` is the precedent for the companion instead. Brevity stays
  at 383/400 and its docstring now records why it cannot see any of this.
* **Scoring the new row on both classes, as brevity does.** There is no gold to
  size against on an unanswerable item, and the canonical decline *"I couldn't
  find anything useful here."* is **seven content words**, so the natural cap of
  6 would fail 116 of 200 correct refusals. It is also unnecessary: recitation
  is not a miss sentence, so `extract.abstain` already reads it directly —
  `ftxclause` 121 → 66 with 22 explicit `recited`.
* **Unifying `probe_reduce.is_span`.** The claim that three probes held one
  rule in three copies was **wrong and is corrected in `answer_sized`'s
  docstring**: `probe_shrink.answer_sized` and `probe_recut.sized` were
  identical and now import the shipped one, but `is_span` sizes the gold as a
  `FRAME`-stripped *set* and disagrees on **26 of the 200 golds** (`the Ramones`
  budgets 6 there and 8 here). Measured, it is invisible on every arm that emits
  answers — 93 / 96 / 94 / 65 either way — and moves only `ftxclause`, 21
  against 16. Left alone rather than unified, because its numbers are on disk
  and the choice decides nothing.

The cards in `evals/results/` are **not backfilled**; the row appears on the
next run, and the five values above are computed offline from the retained
generations and recorded here.

## What it does not settle

The 8 `near_miss_clip` items are real repairs with no trigger, and nothing here
shows one cannot exist — only that neither the span head's geometry nor the two
typed structural rules is it. And `exact` is stricter than anything the card
reports; it is a control column, not a candidate row, and the three are printed
together for that reason.
