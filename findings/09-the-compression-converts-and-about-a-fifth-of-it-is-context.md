# BPE's compression becomes a better model; a fifth comes from context

**Full result:** The compression converts, and about a fifth of it is context

**Cost:** 4.0 min of scoring on the 1 card first cited here (`nano20m_web_bpe`); it also reads 2 cards scored for an earlier finding (`nano20m`, `nano20m_web`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The eighth finding measured that BPE 8k reads 3.8x more text per token and stopped there,
because no chars/token table can say whether a model trained on those tokens is any good.
`nano20m_web_bpe` is that run, built to make the comparison as narrow as possible:
`data/mix_web_bpe` is `data/mix_web`'s **bytes exactly** — the same 200M/255M/45M prefixes of
the same three files — so both arms read identical text, 0.9879 of a pass each.

| row | `nano20m_web` (byte) | `nano20m_web_bpe` | |
|---|---|---|---|
| `narrative` nats/byte | 0.4174 | **0.3666** | −12.2% |
| `temporal` nats/byte | 0.1010 | **0.0967** | −4.3% |
| `web` nats/byte | 0.9434 | **0.9104** | −3.5% |
| `temporal.route` | 398/400 | 398/400 | |
| `temporal.copy` | 353/353 | **353/353** | |
| `refusal.clarify` | 47/47 | 47/47 | |
| `refusal.no_guess` | 47/47 | 47/47 | |
| wall clock | 2,885.9s | **992.4s** | 2.9x |
| params | 25.6M | 29.6M | +16% |

**Better on every language-modelling row, in a third of the time, on the same text.** And
0.3666 narrative beats not just the web-bearing byte run but `nano20m` itself (0.3974), which
saw nothing but TinyStories — so the seventh finding's prose regression from adding web text
is more than repaid by changing the tokenizer.

### About a fifth of that is more context, not better tokenization

`corn/evals.py` guarantees every scored token `WARMUP = 128` **tokens** of context. That was
the right constant when there was one tokenizer and it is a subtle asymmetry now that there
are two: 128 bpe8k tokens is ~490 bytes of context where 128 byte tokens is 128 bytes. §7
chose nats/*byte* precisely so results survive a tokenizer swap, and then fixed the context in
tokens, which partly undoes it.

That is measurable rather than arguable. Re-scoring the byte checkpoint at the warmup that
gives it the same number of *bytes* of context the BPE arm had:

| byte arm, warmup | 128 | 256 | 384 | 480 | bpe8k @128 tok | bytes it had |
|---|---|---|---|---|---|---|
| `narrative` | 0.4174 | 0.4103 | 0.4077 | 0.4072 | **0.3666** | ~515 |
| `temporal` | 0.1010 | 0.0974 | 0.0969 | 0.0966 | **0.0967** | ~382 |
| `web` | 0.9434 | 0.9338 | 0.9287 | 0.9263 | **0.9104** | ~486 |

At matched byte-context the gains become **narrative −10.0%, web −1.7%, and temporal
nothing at all** — 0.0967 against 0.0969. The entire temporal improvement was context, which
is unsurprising once stated: that slice is templated and already at 0.097 nats/byte, so there
is almost no headroom for a vocabulary to find.

Both framings are true and they answer different questions. At a fixed `block_size` of 512 a
BPE model genuinely does attend over 3.8x more text, and that is a free benefit of the swap,
not an artifact — the 12.2% is what you actually get. The 10.0% is what the tokenizer
contributes with context held equal. The honest headline is that the compression converts,
the largest single effect is on narrative, and the temporal row's apparent gain does not
survive the control.

### Three things worth recording

**The real speedup is 3.3x, not 3.8x.** The BPE model trains at ~155k tok/s against byte
level's 178–180k, because the embedding table adds 16% to the parameters and the output
projection is 32x wider. Text throughput is 155k × 3.819 = **592k chars/s against 179k**, so
12% of the compression is handed back to the larger model. §1's wall-clock table should use
3.3x, not the raw compression ratio — and the giveback should shrink at 250M, where an 8k
vocabulary is 4.2% of the model rather than 14.2%.

**`temporal.copy` survived being retokenized**, 353/353, which is the third distribution it
has now held under and the first where the format itself changed representation. The seven
markers being reserved atomic ids is the design intended to protect exactly this, and it is
the reason to keep paying for it.

**Checkpoint selection had nothing to disagree about.** Best-val and final were both iter
5,237 — the mean-of-logs score improved monotonically to the end — so `ckpt.pt` and `last.pt`
are the same 52 tensors. That is a second data point for the rule and a benign one: it cannot
distinguish a good rule from a lucky one, and the evidence base is still essentially the one
run from the seventh finding.

**What this does not settle:** it is 25M parameters, where an 8k vocabulary costs 14.2% of the
model against 4.2% at the 250M shape — so the tax is 3.4x heavier here and the result
understates the Phase 2 case. And the arms differ in optimizer steps (5,237 against 20,000) as
well as tokenizer, because holding both the text and the step count fixed is not possible when
the token count moves by 3.8x. Exposure to text is what was held equal, which is the property
§1's argument is about.

### ~~The decontamination check cannot see a BPE corpus~~ — fixed

`corn.evals` scanned the training stream for eval-text probes as **bytes**, so on a non-byte
corpus it returned `skipped -- non-byte tokenizer` for every text. It said so rather than
claiming `clean`, which is the right failure mode and was clearly anticipated — but §7's
decontamination is one of this project's two durable guarantees, and it had just gone silent
on every corpus the project intends to build.

This run was checkable only by an accident of construction: `reserve_tail` is denominated in
bytes and so is tokenizer-independent, and `data/mix_web_bpe` read byte-identical prefixes to
`data/mix_web`, so pointing the check at that corpus is a statement about the same bytes. No
future corpus will have a byte-level twin.

**The fix is to decode the stream rather than encode the probes**, which is the opposite of
the obvious approach and the reason it works. Encoding a probe and searching token space looks
cheaper and is wrong: BPE is context-dependent at pre-token boundaries, so a probe cut at an
arbitrary offset and encoded on its own need not produce the tokens that same text produced
inside the corpus — and the search would miss real leaks while looking like it worked. Bytes
are bytes in every vocabulary. `scan_stream` now turns each chunk back into bytes through a new
`Tokenizer.decode_bytes`, and every probe, every population, and every check guarding them is
untouched.

`decode_bytes` rather than `decode` because merges are over bytes, so a token can hold a
*fragment* of a multi-byte character — decoding a slice of a stream through `str` puts U+FFFD
where the character was cut and the bytes stop matching. `check_evals.py` constructs that case
rather than hoping for it.

Two things had to be proved and are: on a planted leak, the BPE path and the byte path find
**identical probes** (15 of 16 in train, 1 in val, both tokenizers), and `data/mix_web_bpe`
reads **clean on all three texts** scanned directly, agreeing with the indirect evidence
including the 6 format-only hits on temporal. `contamination` also now decodes each `.bin`
once for all texts rather than once per text, which at 130M tokens is the difference between
seconds and minutes. A corpus whose vocabulary is no longer on disk reads `unavailable`, never
`clean` — the same principle as the missing-parent case in the sixth finding.

63 checks across ten groups, up from 48 across nine — 86 across eleven once the tenth
finding added the tool rows. `HARNESS_VERSION` stays 1: no scored
quantity changed, and `nano20m_web` re-scored identical across the fix.
