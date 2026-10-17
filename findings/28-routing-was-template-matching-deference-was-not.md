# Twenty-eighth finding — routing was template matching, deference was not, and the difference is one token

**Cost:** 9.2 min of scoring on the 2 cards first cited here (`nano20m_v1`, `nano20m_v1_wide`); it also reads 1 card scored for an earlier finding (`nano20m_conv20`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Every behaviour number in this document was measured on utterances the training generators
wrote. `EVAL_WORLD` holds out the facts, the contacts and the anchor years; it holds out
nothing about *how the request is phrased*, because `make_evals.py` renders its items through
`corn/temporal.py`'s and `corn/toolgen.py`'s own template pools. The fifth finding said so and
called it "format compliance, not generalization" — and then nothing could test it, because
the harness was built from the same pools it would have to escape.

`scripts/paraphrase_evals.py` builds two variants of the frozen items. Everything except the
user's words is byte-identical: same anchor, same expression, same `gold_call`, same
observation, same `gold_after`, same ids, same order. The build fails if any line other than
the `<|user|>` line differs, and nothing under `evals/` is touched — the arms are separate
directories with their own manifests, so all eleven sha256 and every scorecard written against
them are unaffected.

| arm | the utterance |
|---|---|
| **retemplate** | re-rendered from a *different* template in the same training pool — in-distribution by construction |
| **paraphrase** | rendered from 136 carriers written for this experiment, which no generator has ever emitted |

The retemplate arm is what makes it an experiment rather than an anecdote: without it, a fall
under paraphrase could be these rows being item-fragile rather than distribution-sensitive.
Two further rows are **invariance controls** — `schema.conform` and `tool.copy` are scored
from files neither arm rewrites, so any movement in them is the harness disagreeing with
itself. Both came back exact, on both checkpoints, in both arms.

### The split

| row | frozen | retemplate | paraphrase | floor (as read) | floor (measured on an arm) |
|---|---|---|---|---|---|
| `temporal.route` | 398/400 | 398/400 | **348/400** | 2 | **19** |
| `tool.selection` | 156/200 | 152/200 | **134/200** | 8 | **41** |
| `tool.validity` | 175/181 | 175/181 | 167/181 | 13 | 9 |
| `temporal.copy` | 353/353 | 353/353 | **353/353** | 0 | 0 |
| `tool.copy_wide` | 276/300 | 280/300 | **278/300** | 29 | 5 |
| `refusal.clarify` | 47/47 | 47/47 | 47/47 | 0 | 0 |
| `refusal.no_guess` | 47/47 | 47/47 | 47/47 | 0 | 0 |
| `schema.conform` | 193/200 | 193/200 | 193/200 | *control* | *control* |
| `tool.copy` | 100/120 | 100/120 | 100/120 | *control* | *control* |

**The last column was added afterwards and one reading depends on it.** Every floor this
finding was written against came from the nineteenth finding, which measured all nine on the
*frozen* set. The twenty-ninth finding's seed replicate shows a row's noise depends on where in
its range the model is standing, and on a paraphrase arm `temporal.route` moves 19 items on the
seed alone and `tool.selection` moves 41. The 50-item fall below is safe against either number.
**`tool.selection`'s 22 is not**, and the paragraph on it further down is annotated accordingly.

`nano20m_v1`. **The rows that ask him to understand the request move; the rows that ask him to
use what the tool returned do not.** `temporal.route` loses 50 items against a floor of 2 —
and against the arm-measured 19 it is still 2.6x, while the in-distribution control loses none
at all. `temporal.copy` reads 353/353 in all three arms.

It replicates on a second corpus. `nano20m_conv20` moves `temporal.route` 399 → **349** and
`tool.selection` 155 → **131**, holds `temporal.copy` at 353/353 and `tool.copy_wide` inside
its floor, and reproduces both invariance controls exactly.

That is the good outcome for §4. The load-bearing claim of this project — the sixth finding,
VISION §5.2, the whole argument for pretraining the format — is about **deference**, and
deference does not care how the request was worded. The number that does not survive is
`temporal.route` 400/400, which has been quoted since the fifth finding and was never the
argument.

### Every one of the 52 failures is `wrong_expression`

Not one `empty`, not one `unparseable`, not one `wrong_tool`. Under paraphrase the model still
emits well-formed JSON and still names `resolve_date`, on 400 items of 400 in every arm. What
it gets wrong is *which words of the sentence are the expression*.

```
said   I'm trying to work out the date of coming Monday
want   coming Monday
got    the coming Monday

said   I'd like the notes last Tuesday
want   last Tuesday
got    the notes last Tuesday

said   so tomorrow -- that's which date?
want   tomorrow
got    this morning
```

Two modes, in roughly equal number. It **absorbs** a neighbouring carrier word into the span,
or — where the span has no left context at all — it **substitutes** a high-frequency training
expression. Three different expressions under the `so {e}` carrier all came back `this morning`.

`score_route`'s docstring bundles two abilities: "it called `resolve_date` **and** put the
user's own words in the argument." Only the second is template-dependent, and the row has
never been able to say which of them a number came from.

### The mechanism is the token immediately to the left of the span

`scripts/paraphrase_attribute.py` re-runs the same generations item by item and joins each
verdict to the carrier that produced it. The obvious hypothesis — that failure tracks how
different the sentence is overall — is visible in the raw numbers and is a confound:

| similarity to nearest training template | pass |
|---|---|
| ≥ 0.75 | 93.5% |
| 0.60 – 0.75 | 87.4% |
| < 0.60 | 85.2% |

Split instead by the **one word that precedes the slot**, against every left edge the training
templates ever put before an expression (`date`, `did`, `for`, `on`, `was`, `what`, …):

| | `nano20m_v1` | `nano20m_conv20` |
|---|---|---|
| a left edge the model has seen before a span | **154/159 — 96.9%** | **153/159 — 96.2%** |
| a left edge it has not | **194/241 — 80.5%** | **196/241 — 81.3%** |

96.9% is the frozen set's own number, reached on carriers the model has never seen, twice.
And once the left edge is held, similarity flattens: within seen edges, far/mid read 97.7% and
96.1% on `v1` and 95.5% and 96.1% on `conv20` — no gradient at all. **The dose-response by
similarity was this effect wearing a disguise.**

The worst left edges are the ones that could plausibly be *part* of a temporal expression —
`so` 25.0%, slot-initial 44.4%, `the rundown` 63.6%, `the notes` 66.7%, `of` 72.7% — while
unseen edges that could not be (`knowing`, `had`, `out`, `saying`) read 100%. The model is not
reading the phrase. It is **segmenting it off a left-boundary cue**, and when that cue is a
token it never saw in that role it mis-segments, always toward including it.

This is §11's copyable-span rule pointed at the *prompt* instead of the answer. The rule says
a span the model must copy has to come from a space too large to memorise as a set. What this
adds is that the span's **boundaries** are learned the same way, out of a set that is far
smaller — the generators vary what goes in the slot exhaustively and leave what sits
immediately to its left nearly fixed. Six distinct left edges across the whole of
`DATE_TEMPLATES_PAST`.

### `tool.selection` falls for a different reason, and it is not explained

The same analysis run on `tool.selection` does **not** separate: 68.7% on seen left edges
against 63.8% on unseen for `v1`, 67.9% against 60.9% for `conv20` — a gap far smaller than
`temporal.route`'s and in a row that fell 22 items. So the left-boundary mechanism is specific
to pulling an argument out of the sentence, which is what `temporal.route` scores and what
`tool.selection` does not.

What that row does instead is fall back to a default. `chose_save_note` goes 8 → 20 on `v1`
and 6 → 20 on `conv20`, with `chose_send_text` 0 → 6 and 2 → 9. Faced with a request shaped
unlike anything it was trained on, it does not decline and it does not pick at random — it
picks `save_note`. Nothing here says why, and the similarity split is the one that shows a
gradient on this row (100% / 58.5% / 68.2% near/mid/far on `v1`, monotonic 88.9% / 65.9% /
50.0% on `conv20`), which is the reverse of `temporal.route` and is unexplained.

**Annotated after the twenty-ninth finding: the 22-item fall is not attributable, and this
section claims more than it can carry.** `tool.selection` moves **41 items on a paraphrase arm
across one seed pair** of `nano20m_v1_wide`, so a 22-item drop on a single checkpoint sits well
inside the noise of the row on that arm. What survives is weaker and worth stating exactly: the
*contrast between arms* went the same way on two independently trained checkpoints — retemplate
−4 and +4, paraphrase −22 and −24 — and a control that moves ±4 while the treatment moves ∼23
twice is not nothing. But the size is unpriced, the `save_note` mechanism rests on failure-mode
counts inside an unreadable row, and **the right next step for this question is a better
instrument rather than another arm.** The left-edge negative above is unaffected: it compares
two buckets *within* one arm and one checkpoint, where the seed does not enter.

### What this does not show

- **These are one person's paraphrases, not recordings.** The carriers are hand-written to be
  ordinary speech at the originals' length, and `check_disjoint` proves none is a training
  template — but a real speech recogniser's output is still a different distribution.
- **Two carriers collided by prefix and were caught after the fact.** `give me {q}` and
  `let's {r}` match training lines in *other* pools (`give me the date for {e}` →
  `resolve_date`, `let's call {c}` → `place_call`), which the whole-string check missed. They
  cover 5 of `tool.selection`'s 200 items and 5 of its 66 losses; quarantining them leaves
  139/195 and changes nothing. Neither touches `temporal.route`.
- **The exhaustiveness claim is checked, and it is what makes the arm safe.** 100.00% of the
  `<|user|>` lines in `data/raw/temporal.txt` and `data/raw/tools.txt` are matched by a
  training template, so "no generator emits these carriers" is a property of the population
  rather than of a sample. It says nothing about the web and conversational slices, which are
  real text and may well contain them — and if they do, that is the more interesting version
  of the question rather than a threat to this one.
- **It does not price a fix.** Widening the left context of every template is one arm and has
  not been run. Nothing here says whether the model would then segment properly or merely
  learn a larger set of boundaries.
- **Still 25M, and this is exactly the kind of result that should move with scale.** A larger
  model has more room to represent the phrase rather than its frame, which makes this a
  candidate for the 100M check to carry rather than a settled number.
