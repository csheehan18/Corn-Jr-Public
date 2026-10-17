# Thirty-third finding — the copy behaviour is keyed to the payload's shape, and to nothing else

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Every arm from the twenty-eighth finding onward rewrites the `<|user|>` line and holds everything
to the right of it. The observation's *shape* had never moved once, and neither had the name in
the call. Two scripts move them — `scripts/payload_evals.py` rewrites the payload,
`scripts/newtool_evals.py` rewrites the tool's name — and between them they say what the copy
behaviour §4 rests on is actually keyed to.

`nano20m_v1` ×4, `pass/n` as min–max with the spread in brackets. No training; every checkpoint
was already on disk.

| row | frozen | reorder | extra_key | renamed | nested | phrasing | **newtool** | **swapname** |
|---|---|---|---|---|---|---|---|---|
| `temporal.copy` /353 | 353 (0) | 318–349 (31) | 335–353 (18) | 353 (0) | **28–84 (56)** | 353 (0) | **353 (0)** | **353 (0)** |
| `refusal.clarify` /47 | 47 (0) | 22–32 (10) | 28–38 (10) | 47 (0) | **0 (0)** | **0 (0)** | **47 (0)** | **47 (0)** |
| `refusal.no_guess` /47 | 47 (0) | 26–39 (13) | 30–41 (11) | 47 (0) | — | 44–47 (3) | **47 (0)** | **47 (0)** |
| `tool.copy` /120 | 100–120 (20) | 54–73 (19) | 95–120 (25) | 68–94 (26) | 0–27 (27) | 100–120 (20) | **100–120 (20)** | **100–120 (20)** |
| `tool.copy_wide` /300 | 238–279 (41) | 110–155 (45) | 224–277 (53) | **95–194 (99)** | 0–35 (35) | 238–279 (41) | 242–274 (32) | 237–280 (43) |

**Shape is worth about a hundred times the name.** One level of wrapping and the model emits
`<|end|>` immediately — not a wrong answer, *no* answer, on every row and both model sizes. The
same keys and the same values in a different order cost ~120 of 300 at 29.6M and ~30 at 91.6M.
Against that, a tool the model has never seen costs **3 of 300** and the difference sits inside a
frozen spread of 41.

`renamed` is unreadable and should not be quoted at either size: `tool.copy_wide` spreads **99 of
300** across four seeds, and the 91.6M figures of 143 and 210 are inside it. No seed count this
project will run fixes that.

### The tool's name is not read at all, and the control is what says so

`newtool` puts `date_lookup` and `fetch_answer` in the call — snake_case names scanned against
every corpus in `data/raw/`, with the build failing rather than warning if one appears.
`swapname` puts a *trained* name there that is wrong for those arguments. Both make the
transcript incoherent; only one makes it unfamiliar.

**Both cost nothing, on six checkpoints across two model sizes.** `temporal.copy` reads 353/353
in all twelve cells. Per-checkpoint deltas against each checkpoint's own frozen scorecard are
+0 everywhere except `tool.copy_wide`, where `newtool` runs −9…+4 and `swapname` −2…+1. So an
unseen name leans about 1% below a familiar one on the widest copy row, consistently but far
inside noise — and the reading is not "incoherence is tolerated" but that the model is not
consulting the name when it decides what to say. It reads the observation.

The four routing rows are byte-identical to the frozen set on every checkpoint, as they must be —
this arm never touches `prompt_call` — and that is its invariance check.

### `refusal.clarify` was measuring recitation — and that is a fact about the corpus

The row reads 47/47 everywhere and **0/47 the moment the tool's question is worded a way the
corpus does not contain** — on two disjoint held-out pools, four 29.6M seeds and both 91.6M
seeds, **twelve cells, no passes**, 42–47 of the failures `reworded`. Every other row on that arm
is identical to the frozen set, which is the invariance control the four structural arms cannot
supply.

The row was measuring whether the model could reproduce one of four sentences it had seen 9,372
times. `scripts/payload_evals.py`'s second pool is what makes that a claim rather than a guess:
`HELD_OUT_CLARIFY_2` keys off the same nine trained strings in nine wordings sharing no clause
with the first pool, written without consulting the attribution files, and the 47 items are
paired one-for-one across the two arms.

**The second pool also retires the scarier reading of `refusal.no_guess`.** Pool A costs 1–3
items at 29.6M and 5 at 91.6M, and on all five of those the model **invented a date and called
`recall_day` with it** having just been told the tool had none. Pool B costs **zero on all six
checkpoints**. The five losses reproduce on pool A and vanish on pool B, and they are visible
from both sides — pool A's five `did_not_ask` on `refusal.clarify` are the same five items as its
five `guessed` here. So it was *that* wording, not novel wording: VISION §9's most important
behaviour is not generally fragile under an unseen refusal, it is broken by one sentence, and the
live hypothesis is that the sentence reads as an instruction to produce something.

**And the zero is a property of the corpus, not of the model or the scale** — `mix_v1_sayvar`
(`45a98e9`), which is the treatment this result asks for and which landed while the rest of this
finding was being written. `CLARIFY_POOLS` takes the tool's question from 9 carriers at 2,096
uses each to 3,301 at **5.7** — `answer`'s regime rather than `clarify`'s — holding generator,
seed, anchor window, expressions, left-context arm, resolved dates and the `<|user|>` line, and
matching `mix_v1` at 130,279,711 train tokens:

| | `nano20m_v1` ×4 | `sayvar` ×2 |
|---|---|---|
| frozen | 47 47 47 47 | 40, 47 |
| `phrasing` pool A | **0 0 0 0** | **29, 8** |
| `phrasing2` pool B | **0 0 0 0** | **30, 24** |

**Eight baseline cells at exactly zero against four treated cells at 8–30.** The row cannot fall
below zero, so the existence of the effect needs no seed argument. So the correct reading of
0/47 is not that the row cannot measure deference and not that 29.6M is too small to relay an
unseen sentence — it is that **a corpus repeating one sentence 2,096 times per carrier teaches
recitation, and one that does not, does not.** The cost is seven items of frozen `refusal.clarify`
on one of the two seeds and nothing else: `temporal.copy` 353/353 and `temporal.route` 398–399 on
both, val 2.2554 and 2.2370 against 2.2516.

What remains open there is the dose. 2,096 recites and 5.7 reads; nothing between them has been
run, so the knee is unbracketed exactly as left edges were before `mix_v1_mid`. The treated
spread is also 8 against 24 on pool A — item-level instability of the kind `churn.py` exists to
price, and there is still no attribution pass for the payload arms.

### What this buys the tool layer

VISION §6 says tools are cheap to add and means it about the code, where `REGISTRY` has always
made a tool a declaration. This is the same claim measured against the *model*, and it comes
apart into three pieces:

- **Read-back on a new tool is free.** Measured, six checkpoints, two sizes.
- **Payload shape is the contract**, and it is the expensive one. A new tool returning a bare
  object with its own fields, or `{"ok": false, "reason", ...}` carrying `say`/`clarify`,
  inherits the behaviour. One returning a nested object does not, at any size tested.
- **Routing to a new tool is untouched** and remains a training question. This arm holds
  `prompt_call` fixed by construction, so it says nothing about whether he would *choose* the new
  tool — only that he handles its answer once called.

### What this does not settle

- **Why `nested` collapses.** Total failure at every seed and both sizes is the cleanest signal on
  the board and the least explained. Nothing here distinguishes a parse failure from a model that
  has never seen a `{` in that position.
- **The dose curve is not a control-and-arm.** `reorder` was written as this file's `retemplate`
  and is not one: on the payload side the only perturbation leaving an object's meaning *and*
  bytes untouched is the object itself, so key order is already a treatment. Read the four as a
  dose curve.
- **Share is not priced.** `resolve_date` is 9.79% of the corpus against tools' 0.62%, and
  `temporal.copy` is the row most robust to shape. That is one plausible reading of the same fact
  and it is a share arm away from being a claim.
- **What `refusal.clarify` measures on an untreated corpus.** `sayvar` shows the row moves when
  the carrier count moves, so it is not a dead instrument — but on `mix_v1` it cannot separate a
  model that defers from one that recites, and every checkpoint in the back catalogue is
  `mix_v1`-shaped. Read every 47/47 in this document as "recited correctly" unless the corpus
  under it says otherwise. `refusal.say` does not fix this: 55 of its 150 items are answerable
  without reading the observation.
- **Whether the same treatment is needed anywhere else.** `resolve_date`'s payload is 9.79% of
  the corpus and the copy rows sit at 1.2 uses per value, which is why they read rather than
  recite. No audit exists of which *other* fields sit in `clarify`'s regime rather than
  `answer`'s, and `scripts/check_copyable.py` is the shape of the tool that would do it.
