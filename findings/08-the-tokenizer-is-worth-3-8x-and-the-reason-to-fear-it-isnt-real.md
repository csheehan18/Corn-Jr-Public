# Eighth finding — the tokenizer is worth 3.8x, and the reason to fear it isn't real

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

DATA.md §2 calls the tokenizer a ~4x lever on effective corpus size at fixed wall clock, puts
an estimated chars/token column in a table, and notes that measuring it properly is "the
cheapest measurement in this entire document." It also raises the one argument for staying at
byte level that isn't sentimental: a BPE trained on clean prose should fragment on the
misspelled, run-together text a speech recogniser actually emits, and Corn-Jr's primary
interface is a voice conversation.

`corn/bpe.py` is a byte-level BPE trainer written from scratch — no BPE library is installed
on this machine and none was added — and `scripts/train_bpe.py` trains the three candidates on
a 100MB sample of the corpus at `mix_web`'s 40/51/9 proportions. All three take **50 seconds
together**. Measured on the frozen `evals/` texts, which are cut from each source's tail while
the training sample is drawn from the head:

| | web | narrative | temporal | **mix-weighted** | embeddings @ n_embd 1280 |
|---|---|---|---|---|---|
| byte | 0.996 | 1.000 | 1.000 | **0.998** | 0.3M (0.1%) |
| BPE 4k | 3.360 | 3.822 | 2.976 | **3.537** | 5.2M (2.1%) |
| BPE 8k | 3.825 | 4.014 | 2.991 | **3.821** | 10.5M (4.2%) |
| BPE 16k | 4.265 | 4.080 | 2.996 | **4.019** | 21.0M (8.4%) |

§2's estimates were ~3.2 and ~3.5 for 4k and 8k, so the shape was right and the level was
low — 8k alone beats what §2 guessed a 32k vocab would reach. The mix-weighted column is a
weighted *harmonic* mean, because a corpus split by characters spends `1/cpt` tokens per
character in each slice; averaging the per-slice figures arithmetically would flatter the
slices that compress well, which are not the ones setting the bill.

**8k is the knee, not a compromise.** It buys 8.0% more compression than 4k for 2.1 more
points of the parameter budget; 16k buys a further 5.2% for a further 4.2 points. Almost all
of the gain past 8k is web — narrative saturates at ~4.08 because TinyStories has a
deliberately small vocabulary, and temporal is flat at ~2.99 across a 4x vocab range. §1's
11 h/GB becomes 2.88.

### The STT objection does not survive contact with a measurement

§2's worry bundles two things a recogniser does, and they pull in opposite directions. Holding
content constant and varying only the surface of the held-out web text, at 8k:

| | chars/token | vs clean |
|---|---|---|
| clean | 3.825 | — |
| + misspellings, disfluencies, run-together words | 3.806 | **−0.5%** |
| lowercased, depunctuated | 4.383 | +14.6% |
| both ("STT-like") | 4.224 | +10.4% |

**Transcription noise costs half a percent.** A byte-level BPE handles a misspelling by
splitting it into a few subwords, which is exactly the graceful degradation byte level was
supposed to be needed for — it is a property of having all 256 bytes in the vocabulary, not of
refusing to merge them. Meanwhile the *other* half of what STT does, dropping case and
punctuation, helps by 14.6%, because capitals and punctuation are the expensive part of clean
prose. The bundled effect is that STT-like text compresses **better** than the clean text it
came from. The probe is manufactured and says so: it is a seeded transform of real text, not a
recording, so what it can show is how much compression is surface-dependent rather than what a
particular recogniser emits.

### Two choices that are Corn-Jr's rather than GPT-2's

**The seven markers are atomic.** `<|call|>`, `<|obs|>`, `<|say|>`, `<|day|>`, `<|user|>`,
`<|end|>` and `<|endoftext|>` get reserved ids and are split out before BPE sees the text.
Otherwise they would fragment differently in every context, and every behaviour row in the
fifth and sixth findings is measured through them — a marker that tokenizes one way after
`<|obs|>` and another way after a newline is a format the model has to learn twice.

**Digits split one at a time**, so `2028` is four tokens. This is the single biggest giveback
in the table: 11.1% on the temporal slice and 1.6% of the corpus overall. It is chosen anyway
because of the sixth finding — all 330 `temporal.copy` failures had the right month and day
and a year clamped to `ANCHOR_END`. If a year is one token, copying it is one lookup against a
prior over ~30 year-tokens; if it is four digits, three are shared with every other year and
only one discriminates. Which is easier to copy is genuinely unknown, and 1.6% is a cheap
price for not letting the vocabulary settle it silently. `--digits group` measures the other
side and is now a two-run experiment rather than an argument.

### The 600MB of "fixed overhead" was 488MB of `import torch`

DATA.md §9 recorded that `prepare` peaks at ~635MB regardless of corpus size and attributed it
to `Tokenizer.encode` returning `list[int]` — boxing an 8M-char chunk into 8M Python ints
before numpy sees it. It concluded that fixing this meant changing the tokenizer contract, and
deferred that to the BPE work.

The BPE is what falsified it. Its list is ~4x shorter for the same chunk and it peaks in the
**same place**: 652MB against byte level's 635MB. Instrumented properly, the breakdown is
488MB of `import torch`, 71MB of chunk, **33MB of `encode`'s list**, and change. `encode` was
5% of the thing named as the cause.

`corn/data.py` imported torch at module scope for one method, `Batcher.get_batch`, that no
offline consumer ever calls — so `prepare`, `prepare_mix`, `prepare_fineweb`, `make_evals` and
`train_bpe` were each paying half a gigabyte for a tensor they never construct. Deferring that
import takes the same build from **635MB to 163MB**, with output byte-identical (`data/tinystories`
rebuilt and sha256-compared on both bins). A training run pays exactly what it always did. The
contract change is no longer worth making, which is a rarer outcome than fixing it would have
been: a planned piece of work deleted by measuring the thing it was justified by.

**What this does not show:** every number here is compression, not loss. Nothing yet says a
model trained on 8k tokens is *better* than one trained on bytes at equal wall clock — only
that it reads 3.8x more text for it.

And the nano-scale test of that will be biased **against** the BPE, which is worth knowing
before reading its result. The embedding table is `vocab x n_embd`, so an 8k vocab costs
4.19M parameters at `nano20m`'s width of 512 and 10.5M at the 250M shape's width of 1280 —
but as a *share* that is **14.2% of a 25M model against 4.2% of a 250M one**. The tax is 3.4x
heavier at nano scale, because the vocabulary does not shrink when the model does. A nano-scale
win for the BPE therefore understates the 250M case; a narrow nano-scale loss would not settle
it.
