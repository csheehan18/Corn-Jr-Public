"""Ask the window once whether there is an answer in it, before he speaks.

The shipped half of `scripts/probe_gate.py`, which measured the policy this
module implements: score the window once, and let that decide speak-or-decline
instead of letting the generator decide it mid-sentence.

    willing >= t   speak -- decode with the decline's head tokens masked
    willing <  t   silent -- the runtime says the canonical decline itself

**Why the decision moves out of the generator.** `probe_lenient` forced an
answer on every answerable window and found **19 of his 41 declines were
hiding strict passes** -- a 46% hidden-correct rate against the 58.5%
accuracy of the answers he volunteers, so his refusal over answerable windows
carries almost no information. The same model's *willingness* read as an
external score separates answerable from unanswerable windows at
**AUC 0.7863**. Same forward, different question: "is there anything here?"
is one he answers well, "should I speak?" is one he answers badly. Moving it
before the decode converts an uninformative refusal into a calibrated one --
cross-validated joint **236 against the frozen policy's 215** (net +21,
p = 0.0334) and, threshold trained on the frozen file and applied cold,
**71 against 61** on the phrase file (p = 0.0309). The win is entirely on the
refusal side: abstention on empty windows goes 61% -> 87% (+52) against -28
on answerable ones, at unchanged precision when speaking (60.2% vs 58.5%).

**It is a policy, not a better reader.** The gate answers fewer windows than
the ungated model and gets a similar fraction of them right; what it buys is
that its silences mean something. `probe_gate`'s docstring carries the limits
and the honesty notes, including that the decline half is authored by the
runtime and so passes `extract.abstain` by construction.

**That last claim was not quite true and this module is where it was made
true.** Wiring the policy up (`scripts/probe_gate_runtime.py`) found the
canonical `{q}` decline scored a *failed* abstention on 10 of the 253
unanswerable eval windows -- short windows, where naming the question back
makes the reply longer than what it read. Scored honestly rather than
assumed, the probe's frozen read would have been CV joint 230, net +15,
**p = 0.14**: the headline was resting on the assumption. `decline_text`
sizing its phrasing against the window takes it to 253 of 253 and restores
the measured numbers exactly -- 236, +21, p = 0.0334, ceiling 314.

## Why these functions are copies

`probe_verifier` and `probe_gate` own the versions the numbers were measured
with and keep them: a probe whose instrument is imported from the runtime
stops being a record of what was measured the moment the runtime changes.
These are the same two computations, moved into the package because the
runtime may not import from `scripts/`. They are held to that equivalence by
`scripts/check_extract.py`, which asserts the head set and one hand-computed
score against the probe's own definition.

## The threshold

`GATE_THRESHOLD` is **-0.136**, cross-validated over 1,003 whole passages on
`corn_jr_260m_v4_ft4g` (`scripts/probe_gate_crossfit.py`, read (e)): joint
**509 against an ungated, unvetoed null's 464 -- net +45 at p = 0.0003**,
with the two folds choosing -0.1359 and -0.1371 independently, agreeing to a
thousandth.

**It was -0.082 until 2026-09-01, and the reason for the change is the
population rather than the protocol.** That number was cross-validated too,
on `evals/extract.jsonl` -- where every item is a *single window*, and 400 of
which are the same items. The runtime reads whole passages in several
windows, and on that population -0.082 is well inside the region that hurts:
the cross-fit is asymmetric, a threshold swept on the held-out 603 transfers
to the eval's 400 (+27, p = 0.0011) while the one swept on the 400 does not
transfer to the 603 (-16, p = 0.20).

**What the move buys and what it costs, on all three populations:**

                              at -0.082        at -0.136
    multi-window runtime      486              509      (null 464)
    frozen eval (400)         242, +39         236, +33  (p < 1e-4 both)
    phrase eval (142)         66, +6 (p=.31)   68, +8 (p=.039)

Six items on the file it was fitted to, against +23 on the population it
serves and a phrase replication that becomes significant. **And it answers
far more**: 128 of 200 answerable frozen windows against 92, which is the
direction the plan asks for -- *when an answer is present, he should answer
it*.

**The move also retired an argument.** At -0.082 the gate answered 49 fewer
passages correctly than the ungated null and bought precision with them,
which the plan's cost ordering calls a loss and precision calls a gain; there
was no resolution inside the numbers. At -0.136 it answers **three more**
than the null while removing 95 wrong answers -- joint +45, precision +9.2
points, right answers up. The disagreement was a property of the constant.

Still a knob and still exposed: **lowering it makes him speak more**. And
still not a constant of the model -- it is a constant of a checkpoint and a
population, so the next fine-tune gets its own run of
`scripts/probe_gate_crossfit.py`, whose harvest is on disk so that question
is replay rather than a decode pass.
"""

from __future__ import annotations

import math

import torch

from .extract import content_words
from .replies import MISS_SAY

# The cross-validated operating point for the *runtime* population. See the
# docstring: it was -0.082 until 2026-09-01, and that number was fitted to
# the wrong population.
GATE_THRESHOLD = -0.136


def decline_heads(tok) -> list[int]:
    """First-token ids of the `MISS_SAY` pool, sorted and deduplicated.

    **Guarded rather than assumed**, because the property is the pool's
    wording and nothing enforces it. Every phrasing begins with a word before
    its `{q}` slot, so the first token should not depend on the question --
    but an edit to the pool could break that silently, and a question-
    dependent head set would make the mask and the score mean different things
    on different items with nothing downstream noticing. Two very different
    dummy questions are encoded and the head sets compared; a disagreement
    raises.

    On the shipped tokenizer this is six ids -- `I`, `N`, `The`, `There`,
    `Un`, `Sorry` -- and three of them are bare word-openers, so **masking
    them also blocks an answer that would have started "Nala" or "Universal"
    or "The aorta"**. Measured cost on the frozen eval: net +2 `tight`, two
    collide-blocked wrong answers improving when re-forked. The `The` case is
    the one with a repair: `corn.extract` prepends a located span's own
    determiner in the merge, which is where an answer that wanted to open
    "The ..." gets its article back.
    """
    def heads_for(q: str) -> list[int]:
        out = []
        for phrasing in MISS_SAY:
            ids = tok.encode(phrasing.format(q=q))
            if ids:
                out.append(ids[0])
        return out

    a = heads_for("who sang the birds and the bees")
    b = heads_for("x")
    if set(a) != set(b):
        raise ValueError(
            "MISS_SAY's first token depends on the question -- the decline "
            "head set is not comparable across windows and the gate's score "
            f"is void. {sorted(set(a))} vs {sorted(set(b))}")
    return sorted(set(a))


# The pool's own fallback, and the pool's own reason for having one: the
# short forms carry no `{q}` and exist "for when the question will not fit".
SHORT_DECLINE = min((m for m in MISS_SAY if "{q}" not in m),
                    key=lambda m: len(content_words(m)))

# How much of the window a decline may take up before it stops being one.
# Half, and deliberately not the 0.8 `corn.evals.RECITED_FRACTION` uses: the
# runtime is not allowed to be written against the ruler that scores it, so
# this is the round number that states the principle -- a turn reporting an
# absence should say less than half of what it read -- rather than the number
# that just clears the row.
DECLINE_FIT = 0.5


def decline_text(question: str, window: str | None = None) -> str:
    """The decline the runtime authors when the gate refuses a window.

    `MISS_SAY[0]` and not a random member: the pool exists so the *corpus*
    varies, and a runtime that varied here would make the same window answer
    differently on two reads. The runtime already authors turns elsewhere
    (seventy-eighth finding); this is that, on the window the gate silenced.

    **Except where the question will not fit, which is measured and is why
    this takes a window at all.** Naming the question back is most of the
    sentence's length, and on a short window it makes the decline longer than
    the thing it read -- which `score_extract_abstain` calls `wrote_own` and a
    reader would call odd. Over the 253 unanswerable items on both eval files
    the `{q}` form is scored a *failed* abstention on **10**, all of them
    windows of 8 to 21 content words against a typical 36. Falling back to
    the pool's shortest question-free phrasing on those takes it to **253 of
    253**, and it fires on 45 windows in all.

    With no window given the long form comes back unconditionally, which is
    what every caller outside the gated path wants and what the guards assert.
    """
    long_form = MISS_SAY[0].format(q=question)
    if window is None:
        return long_form
    room = DECLINE_FIT * len(content_words(window))
    return long_form if len(content_words(long_form)) <= room else SHORT_DECLINE


@torch.no_grad()
def willingness(model, tok, prompt: str, question: str, device: str,
                block_size: int) -> float | None:
    """How much he wants to *answer* this window: `-P(decline's first two)`.

    One forward. The score is the joint probability of the canonical
    decline's first two tokens at the say turn, sign-flipped so that **higher
    means more willing to answer** -- which is the direction the threshold is
    written in and the reason the sign lives here rather than at the call
    site.

    **Two tokens, not one**, because one collides with answer openers: `N`
    opens "Nothing useful..." and "Nala" alike, and a head-mass score would
    read a model about to say a name as a model about to decline. The second
    token is what separates them.

    `None` when the prompt and the continuation together overrun
    `block_size`. Returned rather than truncated -- a truncated prompt is a
    different question -- and the caller treats it as "do not speak", which is
    the conservative direction: a window too long to score is a window nothing
    vouched for.
    """
    p_ids = tok.encode(prompt)
    c_ids = tok.encode(decline_text(question))
    if not p_ids or len(c_ids) < 2 or len(p_ids) + len(c_ids) > block_size:
        return None
    ids = torch.tensor([p_ids + c_ids], dtype=torch.long, device=device)
    logits, _, _ = model(ids, targets=ids)
    logp = torch.log_softmax(logits[0].float(), dim=-1)
    at = len(p_ids) - 1
    return -math.exp(logp[at, c_ids[0]].item()
                     + logp[at + 1, c_ids[1]].item())


class WindowGate:
    """`(question, prompts) -> one willingness per prompt`. What `read_passage` takes.

    Holds the model so that `corn/extract.py` does not have to: the module
    that cuts the passage and reduces the replies stays free of weights, and
    the gate arrives as a callable the same way the worker does. A guard
    replaces it with a lambda returning canned floats, which is how the
    threshold's direction is tested without a checkpoint.

    Scored one window at a time rather than batched. The gate is one forward
    per window against the worker's `MAX_NEW` decode steps for the windows
    that pass, so the sequential form is a small fraction of the turn and it
    is the form the probe measured -- batching it later is a speed change to
    make against a byte-identical baseline, not a thing to do while shipping
    the policy.
    """

    def __init__(self, model, tok, device: str = "cuda",
                 block_size: int | None = None) -> None:
        self.model = model
        self.tok = tok
        self.device = device
        self.block_size = block_size or model.cfg.block_size

    def __call__(self, question: str, prompts: list[str]) -> list[float]:
        out = []
        for p in prompts:
            w = willingness(self.model, self.tok, p, question, self.device,
                            self.block_size)
            out.append(float("-inf") if w is None else w)
        return out
