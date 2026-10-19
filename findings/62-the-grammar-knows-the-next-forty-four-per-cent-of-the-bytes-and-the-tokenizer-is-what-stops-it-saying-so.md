# The call grammar fixes 44% of bytes; the tokenizer blocks using it

**Full result:** The grammar knows the next 44% of the bytes, and the tokenizer is what stops it saying so

No GPU, no checkpoint, no training. Everything below is a walk of 400 real
calls from `data/raw/tools.txt` through the real `CallConstraint`, counted.
`scripts/forced_token_survey.py` is the instrument.

> **Correction, 2026-08-26, added the day this was written.** The mechanism
> below is **not new**, and this finding was written without checking. It is
> `llguidance`'s **fast-forward tokens**, shipped in production — see
> [EXTERNAL-RESEARCH](../EXTERNAL-RESEARCH.md) entry 14. They measure
> fast-forwarded tokens at **~12.7% of JSON-schema tokens** on llama3, against
> the 3.8% below on `bpe8k`; different tokenizer and different schema, so the
> two are the same quantity and not comparable numbers. They also measured the
> tokenisation tax from the other side and it is **worse than this file
> guesses**: with token healing off, **~97% of fast-forwarded sequences are
> non-canonical**, and forcing a non-canonical segmentation actively damages
> the model rather than merely wasting a step. What survives as this project's
> own is the measurement on this tokenizer and this corpus, and the
> draft-and-verify framing in the last section — which is a *different*
> proposal from theirs, not a better one, and is still unmeasured.

## Why the question came up

Decode is at 691 tok/s after the sixty-first commit's three optimisations,
against a **GEMV floor of 877** — the cost of reading 521 MB of bf16 weights
once per token. Every remaining idea that still runs the model once per token
is arguing over the last 21%. Passing the floor at all requires producing more
than one token per weight read, and with quantisation ruled out that means
spending fewer forward passes than tokens.

Corn-Jr has something most models do not: `corn/grammar.py` already computes,
at every step, the set of tokens that may legally follow. **Where that set has
one member the next token is decided and the logits cannot change it** —
masked argmax returns it whatever the model computes, and masked softmax gives
it probability 1, so this is true of sampling and not only of greedy. A
forward pass at such a position is work whose result is discarded.

That is a property of the grammar and the sentence, not of the weights, so it
was measurable before anything was built. Which is the whole reason it got
measured before anything was built.

## The idea, as first stated, is a null

    forced TOKENS          412/10743 = 3.8%
    consecutive runs       406, mean length 1.01
    run lengths            403 of length 1, 3 of length 3

    forwards saved         412/10743 = 3.8%  ->  1.04x

**3.8%, in runs of one.** All 400 of the length-1 runs are the same position:
`name_body`, the completion of the tool name after its first distinguishing
character. Nine more are hex escapes and three are string escapes. Nothing
else in a call is ever down to a single token.

An intervention worth 1.04x on part of the output does not justify the
machinery it needs, which is chunked prefill into a non-empty cache — a thing
`CausalSelfAttention.forward` currently refuses outright. Recorded as a null.

## The reason is the finding, and it is a tokenisation tax

The same walk, counting *bytes* the grammar leaves no choice about rather than
tokens:

    forced BYTES           4784/10743 = 44.5%
    forced TOKENS           412/10743 =  3.8%

**The grammar determines nearly half the bytes of a call and can say almost
none of them.** The two numbers differ by 12x and the gap is entirely
segmentation: a determined byte string has many legal BPE tokenisations, so
"only one string can follow" does not imply "only one token can follow". From
inside `{"name": "save_note"` the bytes `, "arguments": {"` are forced and the
decoder still faces a choice among every token that is a prefix of them.

This is the twelfth-to-fourteenth findings' shape pointed at the decoder
instead of the corpus: the information is present, and the representation is
what makes it unreachable.

## What the gap is worth, and it is not the obvious thing

A determined byte run cannot be *emitted*, because picking a tokenisation
picks one the model might not have picked, and a different segmentation is a
different KV cache and therefore different logits downstream. But it can be
**drafted**. Encode the forced run canonically, run one chunked forward over
the whole draft, and keep each drafted token only where it equals what the
masked model would have produced anyway; take the model's token at the first
disagreement and continue.

That is ordinary speculative verification with the draft arriving free from
the constraint instead of from a second model — no second set of weights, no
training, no approximation, and **output exactly identical to the
unaccelerated decoder's** by construction rather than by measurement.

Acceptance is what decides whether it is worth building, and the corpus is the
honest estimate of it: `tools.txt`'s own tokenisation is canonical BPE and is
what the model was trained to reproduce, so how often a canonical draft
matches the corpus token is how often it should match the model.

    tokens drafted     4717
    tokens accepted    3024   (64.1% of drafts)
    share of all call tokens covered   32.1%

    accepted per draft   1 -> 957   2 -> 243   3 -> 403   4 -> 93

    forwards saved on the constrained span   3024/9415 = 32.1%  ->  1.47x

**1.47x on the span inside a call, exactly.** Not on free `<|say|>` prose,
which no grammar constrains — this buys speed precisely where Corn-Jr does the
thing VISION §6 says he is for.

## What this does not settle

- **It was already done, and this file did not check.** See the correction at
  the top and EXTERNAL-RESEARCH entry 14. The prior art also carries a hazard
  this file did not anticipate: a forced non-canonical segmentation makes the
  model's *next* prediction worse, not just its speed. Draft-and-verify is
  immune to that by construction -- a bad draft is rejected and costs a step --
  which is the one argument for the framing here over theirs, and it is an
  argument rather than a measurement.
- **Nothing is built.** The enabling primitive is a multi-token forward into a
  non-empty cache -- which `CausalSelfAttention.forward` raised
  `NotImplementedError` for when this was written and which `CornModel.step`
  now supports, built for prefix reuse -- plus KV rollback on a rejected
  draft. The numbers above are an opportunity, not a speedup anyone has run.
- **64.1% is a corpus estimate, not a model measurement.** It says how often
  canonical BPE agrees with the corpus, and the model's agreement with
  canonical BPE at temperature 0 is a separate quantity nobody has read. It
  could go either way and the first real implementation should report it
  before anything quotes 1.47x.
- **The span is not the turn.** 1.47x applies to constrained tokens. What a
  whole turn gains depends on the call-to-prose ratio, which varies by tool
  and which this does not measure.
- **The 3.8% null is only null for run-skipping.** Those 412 forced tokens are
  still free inside a draft scheme; they are counted in the 32.1%.

## The method note worth keeping

The byte count is four lines of the survey and it is the only reason the null
became a design. A measurement that says "3.8%, abandon it" and a measurement
that says "3.8% of tokens but 44.5% of bytes" cost the same to take and point
in opposite directions. **When an intervention reads near zero, measure the
quantity the mechanism actually operates on before recording the null** — the
first number was about the decoder's alphabet and the question was about the
grammar's knowledge.
