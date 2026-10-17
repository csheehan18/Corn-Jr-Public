"""Point at the answer instead of generating it: the shipped boundary reader.

`docs/PLAN-EXTRACTION-READER.md` R3. The reading half of WS-B-alt stops being
a decode. One trunk forward per window, a pair scorer over the window's token
positions, and a second binary head that decides whether the pair it found is
spoken -- then the worker's own reply shape, so `corn/extract.py`'s `reduce`,
`grounded`, `_span_key`, `_canonical`, `det_repair` and every scorer apply
unchanged.

    today    gate forward (1/window) -> decode 32 steps (per admitted window)
    here     reader forward (1/window, bucketed) -> (span, margin) per window

## The three pieces and what each decides

    span head      checkpoints/reader_built_s1.pt   *where* the answer is
    verifier head  checkpoints/nullpr_s1.pt         *whether* it is spoken
    extent rule    EXTENT_D, at read time           where the span *ends*

**The verifier is the gate.** `corn/gate.py`'s willingness asks "is there
anything here?" before a decode that then decides for itself; this head is
handed the argmax pair's own two state rows and the span head's three scalars
and asked "is *that* the answer?". The eighty-sixth finding measures the
difference on three seeds: the same-type rival (`Grammy` for `Oscar`) halves
on all three, 80/85/72 -> 42/47/43, precision 59 -> 66.5/61.3/62.0, and at the
silence floor it reads +10 / +9 / +18 right answers over the presence head it
replaces. So the gate is bypassed when this reader runs, and both remain
reachable behind `harness/serverconfig.py`'s `reader` flag.

**The extent rule is free.** Among the pairs that extend the argmax by up to
three candidate rows on either side and score within `EXTENT_D` of it, speak
the longest. On Population A it is +7 / +6 / +8 passages on the three seeds
with **nothing lost on any row** (finding 86, "Stacked with the extent rule"),
because a span head that has found the entity and clipped its last word still
ranks the whole entity second.

## Why this file is a copy of the trainer's arithmetic

`scripts/train_reader.py` and `scripts/train_reader_cached.py` own the
versions the numbers were measured with and keep them: rule 29 forbids the
runtime importing from `scripts/`, and a probe whose instrument is imported
from the runtime stops being a record of what was measured. This is
`corn/gate.py`'s situation exactly, and it takes `corn/gate.py`'s answer --
the computations move into the package and `scripts/check_extract.py` asserts
the two agree, head for head and score for score, on canned states with no
checkpoint anywhere near it.

The same rule is why `token_bounds` and `window_region` are here rather than
imported from `corn/spangen.py`: `spangen` is the training side of the
layering split (`scripts/check_layering.py`), and a runtime module that
imported it would drag a generator into the published half. Both ports are
held equal to the originals by the same guard.

## The threshold, and the protocol that chose it

`READER_THRESHOLD` is **-2.02**, the mean of the two cross-validated fold
values (-1.980 / -2.061) on Population A under the **bar protocol**: the `t`
that maximises `right` on the training fold among those holding that fold's
share of 200 correct silences. That protocol is an owner decision and the
eighty-sixth finding is why it is a decision rather than a preference -- the
`joint` optimum every earlier number was read at sits in a band up to 158
thresholds wide across which `right` and correct silence trade by up to
thirty passages, so `joint` cannot choose and `bar` is the only determinate
rule. It matches PRIMARY, which was always *`right` subject to `silent >=
200`*.

At that operating point, on the 1,003 whole passages of Population A:
**389 right of 721 answerable, 200 silent of 282 unanswerable** read through
this file by the wired runtime (finding 87), against the 389 and 199 finding
86 replayed off the harvest -- one passage of correct silence between a
threshold comparison and a rounding, and nothing else.
Against the shipping gate that is +107 right answers and about 28 fewer
correct silences -- the trade the owner's ordering asks for (speak first,
`PLAN-EXTRACTION-READER.md` R-T) and it is stated as a trade.

Still a knob, still exposed, and still a constant of a checkpoint and a
population rather than of the model: the next trunk gets its own run of
`scripts/probe_reader_passages.py`.

## The second arm: one prompt a passage, through an adapted trunk

`WholeHeadReader` is `docs/PLAN-READER-PORT.md`'s port of finding 112's arm and
it is a different reader, not a setting of this one. Everything above reads the
frozen trunk one 64-token window at a time and votes; that one puts the whole
passage in the payload, runs the trunk **once** with a rank-32 adapter on
(`corn/model.py`, off for every other forward in the process), and scores the
pairs and the null in one softmax -- so there is no vote to lose and no second
head to stack. On Population A it reads **523 of 721 right at 198 correct
silences** where this file's window head reads 392 and 199 (finding 116), and
its `WHOLE_THRESHOLD` is its own: the margin is `max s - s_null` and not a
verifier's logit, so the two numbers are not on one scale and neither may
default into the other.

`generate` is still the server's default. Both arms are behind
`harness/serverconfig.py`'s `reader`, as `head` has been since finding 87.
"""

from __future__ import annotations

import json

import torch
import torch.nn.functional as F
from torch import nn

from .gate import decline_text
from .model import adapter, load_adapter
from .replies import SAY_ANSWER

# --- the constants ------------------------------------------------------------

# The band the head reads, fixed before R1 ran and never re-picked: every block
# layer beat `ln_f` in `probe_spanhead`'s sweep and re-choosing here on the
# evals is what made that file's first headline unreadable.
LAYERS = (8, 12, 16)

# The longest span the pair enumeration can express, in tokens. The same 16
# `corn/spangen.py` declares and `scripts/check_spans.py` asserts against both
# frozen evals.
MAX_SPAN_TOKENS = 16

# What the payload declares. `corn/spangen.py`'s constant and its argument.
SOURCE = "wikipedia.org"

# Where `json.dumps({"answer": ...})` puts the first character of the escaped
# window. Computed rather than a literal 12 so a change to the payload's field
# order fails loudly instead of labelling positions inside the wrong field.
_PAYLOAD_HEAD = len(json.dumps({"answer": ""})) - 2  # drop the closing `"}`

# How a span becomes a reply -- `SAY_ANSWER[1]`, the framing `corn/extract.py`'s
# `FRAME` was written around and the one every generative arm on this record
# was scored through.
SAY = SAY_ANSWER[1]

# The margin at which he speaks. See the module docstring: the mean of the two
# bar-protocol fold values on Population A, and `harness/serverconfig.py`
# carries the same number as a literal because a config form may not import
# torch. `scripts/check_extract.py` holds the two equal.
READER_THRESHOLD = -2.02

# The extent rule's tolerance and its reach, in candidate rows. Fixed at the
# value both seeds' curves chose in the eighty-fifth finding and read again in
# the eighty-sixth; not searched on any population here. The whole-passage arm
# re-read the same grid in finding 114 and moved by one to four passages
# inside noise on both seeds, so it takes these two constants unchanged.
EXTENT_D = 2.0
EXTENT_RADIUS = 3

# The whole-passage arm's own threshold, and the same kind of number as
# `READER_THRESHOLD`: the mean of the two bar-protocol fold values on
# Population A under the current grounding rule, seed 1 -- (-1.094 + -1.254)
# / 2 (finding 116, `whole_causal_s1_grounded115.json`, key `arm.t`).
#
# **It is not comparable with `READER_THRESHOLD` and must never be defaulted
# into.** That margin is a verifier's logit; this one is `max s - s_null` off
# the head's own softmax, a different quantity on a different scale, and the
# two heads share nothing but a threshold protocol. `harness/serverconfig.py`
# carries the literal and `scripts/check_extract.py` holds the two equal.
# **Moved with the trunk, 2026-09-05 (finding 124).** -1.174 was the ft4g
# adapter's constant (folds -1.094 / -1.254); the re-fit on
# `corn_jr_260m_v4_ft_social8` reads -0.975 / -1.584 at the bar protocol and
# ships at their mean. A threshold is a constant of a checkpoint and a
# population, never of the model.
WHOLE_THRESHOLD = -1.280


# --- the token map, ported from corn/spangen.py -------------------------------

def token_bounds(tok, text: str) -> tuple[list[int], list[int], list[int]]:
    """`(ids, byte_start, byte_end)` -- the exact map from tokens to bytes.

    `corn.spangen.token_bounds`, moved for the layering rule (see the module
    docstring) and held equal to it by `scripts/check_extract.py`. Off
    `decode_bytes`, the one decode path that cannot lose information: a token
    may hold a *fragment* of a multi-byte character, so accumulating decoded
    character lengths drifts where accumulating decoded byte lengths does not.
    """
    ids = tok.encode(text)
    starts: list[int] = []
    ends: list[int] = []
    at = 0
    for i in ids:
        starts.append(at)
        at += len(tok.decode_bytes([i]))
        ends.append(at)
    return ids, starts, ends


def window_region(prompt: str, window: str, question: str,
                  source: str = SOURCE) -> tuple[int, int]:
    """Character bounds of the escaped window inside `prompt`.

    `corn.spangen.window_region`, moved for the same reason and guarded the
    same way. **The span is confined to this region and that is not
    tidiness**: `worker_prompt` writes the question twice above the payload,
    so a candidate position outside it would let the head point at the
    question rather than at what it read.
    """
    payload = json.dumps({"answer": window, "source": source,
                          "query": question})
    at = prompt.index(payload)
    lo = at + _PAYLOAD_HEAD
    return lo, lo + len(json.dumps(window)) - 2


def candidates(tok, prompt: str, question: str, window: str,
               source: str = SOURCE) -> tuple[list[int], list[int]]:
    """`(ids, keep)` -- the token indices a span may occupy.

    `scripts/train_reader.candidates`. The payload's escaped window and
    nothing else.
    """
    ids, starts, ends = token_bounds(tok, prompt)
    lo, hi = window_region(prompt, window, question, source)
    b_lo = len(prompt[:lo].encode("utf-8"))
    b_hi = len(prompt[:hi].encode("utf-8"))
    keep = [i for i in range(len(ids)) if starts[i] >= b_lo and ends[i] <= b_hi]
    return ids, keep


_PAIRS: dict[tuple[int, str], tuple[torch.Tensor, torch.Tensor]] = {}


def pair_index(n: int, device) -> tuple[torch.Tensor, torch.Tensor]:
    """Every `(i, j)` with `0 <= j - i < MAX_SPAN_TOKENS` over `n` positions.

    `scripts/train_reader.pair_index`, memo and all: the enumeration is ~1,050
    pairs a window built in a Python loop and a passage is several windows.
    The tensors are read-only index buffers and are never written through.
    """
    key = (n, str(device))
    got = _PAIRS.get(key)
    if got is not None:
        return got
    ii, jj = [], []
    for j in range(n):
        for i in range(max(0, j - MAX_SPAN_TOKENS + 1), j + 1):
            ii.append(i)
            jj.append(j)
    got = (torch.tensor(ii, dtype=torch.long, device=device),
           torch.tensor(jj, dtype=torch.long, device=device))
    _PAIRS[key] = got
    return got


def bucket(ids: list[list[int]]) -> list[list[int]]:
    """Row indices grouped by prompt length, shortest group first.

    `harness.backends.read.bucket`, and here for the layering rule rather than
    for a second opinion -- the two are held equal by the guard. The trunk has
    learned absolute positions and no padding is available in either
    direction, so a batched forward has to be over equal lengths, and the
    prompt around an equal-length window is not equal-length: `"` and `\\`
    are escaped inside the payload.
    """
    groups: dict[int, list[int]] = {}
    for i, seq in enumerate(ids):
        groups.setdefault(len(seq), []).append(i)
    return [groups[n] for n in sorted(groups)]


# --- the two heads ------------------------------------------------------------

class SpanHead(nn.Module):
    """The pair scorer. `scripts/train_reader_cached.CachedHead`, built arm.

    `s(i, j)` over every candidate pair of one window: a pair term with a
    bilinear product in the head's own width, a width embedding, a pointer
    term against the say marker's row, and LayerNorm per layer chunk on the
    inputs. `checkpoints/reader_built_s1.pt` is what these weights are.

    The module list is the trainer's, in the trainer's order and with the
    trainer's names, because that is what makes the `state_dict` on disk
    loadable here without a translation table -- including `c`, which the
    built arm constructs and does not use, and `null`, which every arm here
    carries and none scores (the reader's margin is the verifier's logit, not
    `s_best - s_null`).

    Dropout is a constructor argument in the trainer and is not one here: this
    class never trains, `eval()` makes it the identity, and a runtime module
    holding a training-time regulariser is a knob with no reading behind it.
    """

    def __init__(self, dim: int, hidden: int, n_layers: int = 3) -> None:
        super().__init__()
        self.a = nn.Linear(dim, hidden, bias=False)
        self.b = nn.Linear(dim, hidden, bias=False)
        self.c = nn.Linear(dim, hidden, bias=True)
        self.out = nn.Linear(hidden, 1, bias=False)
        self.null = nn.Sequential(nn.Linear(dim, hidden), nn.GELU(),
                                  nn.Linear(hidden, 1, bias=False))
        self.wq_i = nn.Linear(dim, hidden, bias=False)
        self.wk_i = nn.Linear(dim, hidden, bias=False)
        self.wq_j = nn.Linear(dim, hidden, bias=False)
        self.wk_j = nn.Linear(dim, hidden, bias=False)
        self.chunk = dim // n_layers
        self.ptr_ln = nn.ModuleList([nn.LayerNorm(self.chunk)
                                     for _ in range(n_layers)])
        self.scale = hidden ** -0.5
        self.ln = nn.ModuleList([nn.LayerNorm(self.chunk)
                                 for _ in range(n_layers)])
        self.width = nn.Embedding(MAX_SPAN_TOKENS, hidden)
        self.p = nn.Linear(dim, hidden, bias=False)
        self.q = nn.Linear(dim, hidden, bias=False)
        self.r = nn.Linear(hidden, hidden, bias=True)

    def ptr_norm(self, h: torch.Tensor) -> torch.Tensor:
        """LayerNorm per layer chunk, for the pointer term's inputs only."""
        return torch.cat([ln(part) for ln, part in
                          zip(self.ptr_ln, h.split(self.chunk, dim=-1))],
                         dim=-1)

    def features(self, h: torch.Tensor) -> torch.Tensor:
        """LayerNorm per layer chunk. Per chunk and not over the whole 3,072:
        the three are block outputs at layers 8, 12 and 16 and their scales are
        not each other's."""
        return torch.cat([ln(part) for ln, part in
                          zip(self.ln, h.split(self.chunk, dim=-1))], dim=-1)

    def score(self, h: torch.Tensor, q: torch.Tensor, ii: torch.Tensor,
              jj: torch.Tensor, row_w: torch.Tensor) -> torch.Tensor:
        """`s` for every pair in `(ii, jj)`. `CachedHead.score`, built arm."""
        f = self.features(h)
        z = self.a(f)[ii] + self.b(f)[jj]
        z = z + self.r(self.p(f)[ii] * self.q(f)[jj])
        z = z + self.width(jj - ii)
        s = self.out(F.gelu(z)).squeeze(-1)
        nh, nq = self.ptr_norm(h), self.ptr_norm(q)
        pi = (self.wk_i(nh) * self.wq_i(nq)[row_w]).sum(-1) * self.scale
        pj = (self.wk_j(nh) * self.wq_j(nq)[row_w]).sum(-1) * self.scale
        return s + pi[ii] + pj[jj]


class VerifierHead(nn.Module):
    """Whether the span head's argmax is spoken. `train_null_head.NullHead`.

    The pair-rows arm and only that arm: the say marker's row, the argmax
    pair's own two rows, and the span head's three scalars, each normalised
    the way it was in training -- LayerNorm per layer chunk on the states,
    the training split's mean and standard deviation on the scalars, written
    in as buffers so a head loaded off disk normalises exactly as it did while
    training. `checkpoints/nullpr_s1.pt` is what these weights are.

    Its output is the margin the threshold is compared against, so the sign is
    fixed here: **higher means more willing to speak**.
    """

    def __init__(self, dim: int, hidden: int, n_layers: int = 3,
                 n_feat: int = 3) -> None:
        super().__init__()
        self.chunk = dim // n_layers
        self.n_feat = n_feat
        self.ln = nn.ModuleList([nn.LayerNorm(self.chunk)
                                 for _ in range(n_layers)])
        self.ln_i = nn.ModuleList([nn.LayerNorm(self.chunk)
                                   for _ in range(n_layers)])
        self.ln_j = nn.ModuleList([nn.LayerNorm(self.chunk)
                                   for _ in range(n_layers)])
        self.register_buffer("f_mean", torch.zeros(n_feat))
        self.register_buffer("f_std", torch.ones(n_feat))
        self.fc1 = nn.Linear(dim * 3 + n_feat, hidden)
        self.fc2 = nn.Linear(hidden, 1, bias=True)

    def _norm(self, mods, h: torch.Tensor) -> torch.Tensor:
        return torch.cat([ln(part) for ln, part in
                          zip(mods, h.split(self.chunk, dim=-1))], dim=-1)

    def forward(self, h: torch.Tensor, feats: torch.Tensor,
                hi: torch.Tensor, hj: torch.Tensor) -> torch.Tensor:
        h = torch.cat([self._norm(self.ln, h), self._norm(self.ln_i, hi),
                       self._norm(self.ln_j, hj)], dim=-1)
        f = (feats.to(h.dtype) - self.f_mean) / self.f_std
        return self.fc2(F.gelu(self.fc1(torch.cat([h, f], dim=-1)))).squeeze(-1)


class _WholePair(nn.Module):
    """`PairHead`'s five modules at the whole-passage arm's shapes.

    `scripts/train_reader_whole.WholeHead` builds `train_reader.PairHead` and
    then replaces its `c` with a `hidden -> hidden` linear, because the product
    term is projected before it is taken (finding 112 §5: on the raw 3,072-dim
    rows a 512-token passage's ~7,000 pairs filled the card). What is left is
    exactly these five modules, and they are constructed here at the shapes the
    file on disk carries rather than built wide and overwritten, so a shape
    mismatch is a load error instead of a silent second architecture.

    The names are the trainer's -- `pair.a`, `pair.b`, `pair.c`, `pair.out`,
    `pair.null.0`, `pair.null.2` -- which is what makes the checkpoint loadable
    without a translation table, and a translation table is where a silent
    mislabelling would live.
    """

    def __init__(self, dim: int, hidden: int) -> None:
        super().__init__()
        self.a = nn.Linear(dim, hidden, bias=False)
        self.b = nn.Linear(dim, hidden, bias=False)
        self.c = nn.Linear(hidden, hidden, bias=True)
        self.out = nn.Linear(hidden, 1, bias=False)
        self.null = nn.Sequential(nn.Linear(dim, hidden), nn.GELU(),
                                  nn.Linear(hidden, 1, bias=False))


class WholeHead(nn.Module):
    """The whole-passage pair scorer. `scripts/train_reader_whole.WholeHead`.

    One passage, one forward, no vote: `s(i, j) = out(gelu(a(h_i) + b(h_j) +
    c(p(h_i) * q(h_j))))` over `0 <= j - i < MAX_SPAN_TOKENS` on the candidate
    rows, and `s_null` an MLP at the say marker's row. LayerNorm per 1,024-dim
    layer chunk on the way in, for `SpanHead.features`' reason: the three
    chunks are block outputs at layers 8, 12 and 16 and their scales are not
    each other's.

    **The margin is `max s - s_null`, and it is a different quantity from
    `HeadReader`'s.** There is no second head here: the null is a row of the
    same softmax the pairs are scored in, so willingness and pick come out of
    one training objective rather than out of a head stacked on another head's
    argmax. That is why the arm has its own threshold and why the two cannot
    share one.

    Dropout is a constructor argument in the trainer and is not one here, for
    `SpanHead`'s reason: this class never trains.
    """

    def __init__(self, n_layers: int, width: int, hidden: int) -> None:
        super().__init__()
        self.width = width
        self.norms = nn.ModuleList([nn.LayerNorm(width)
                                    for _ in range(n_layers)])
        self.pair = _WholePair(n_layers * width, hidden)
        self.p = nn.Linear(n_layers * width, hidden, bias=False)
        self.q = nn.Linear(n_layers * width, hidden, bias=False)

    def norm(self, h: torch.Tensor) -> torch.Tensor:
        """LayerNorm per layer chunk, in fp32 whatever the trunk ran in.

        `h.float()` is the trainer's and is load-bearing rather than defensive:
        the training forward runs under bf16 autocast and the head reads its
        output, so the cast is where the arithmetic becomes fp32 in both
        processes and not somewhere else in one of them.
        """
        chunks = h.float().split(self.width, dim=-1)
        return torch.cat([ln(c) for ln, c in zip(self.norms, chunks)], dim=-1)

    def scores(self, hk: torch.Tensor, ii: torch.Tensor,
               jj: torch.Tensor) -> torch.Tensor:
        """`s` for every pair in `(ii, jj)` over the candidate rows `hk`."""
        h = self.norm(hk)
        ha, hb, hp, hq = self.pair.a(h), self.pair.b(h), self.p(h), self.q(h)
        z = ha[ii] + hb[jj] + self.pair.c(hp[ii] * hq[jj])
        return self.pair.out(F.gelu(z)).squeeze(-1)

    def null(self, h_last: torch.Tensor) -> torch.Tensor:
        """`s_null` at the say marker's row -- the last row of the prompt."""
        return self.pair.null(self.norm(h_last)).squeeze(-1)


def span_features(sc: torch.Tensor, ii: torch.Tensor,
                  jj: torch.Tensor) -> torch.Tensor:
    """`(1, 3)`: the top pair's score, its margin over the runner-up, its length.

    `train_reader_cached.span_features`. A one-pair window has no runner-up and
    its gap is 0.0 rather than an infinity the head would have to learn around.
    """
    b = int(torch.argmax(sc).item())
    length = float(int(jj[b]) - int(ii[b]) + 1)
    if sc.numel() >= 2:
        top = torch.topk(sc, 2).values
        gap = float(top[0] - top[1])
    else:
        gap = 0.0
    return torch.tensor([[float(sc[b]), gap, length]], device=sc.device)


def extend(sc: torch.Tensor, ii: torch.Tensor, jj: torch.Tensor, b: int,
           d: float, radius: int = EXTENT_RADIUS) -> tuple[int, int]:
    """The pair actually spoken: the argmax, widened while it stays close.

    Among `(i - a, j + b)` for `0 <= a, b <= radius` that exist in the
    enumeration and score within `d` of the argmax, the **longest**, ties to
    the smaller `a`. `scripts/probe_extent_frozen.extend`, which is the
    function the eighty-fifth and eighty-sixth findings measured; `d = 0`
    returns the argmax unchanged, which is what makes the rule switchable
    without a second code path.

    Half of `CLIPPED` is a span one or two words short of its gold and the
    whole entity is the head's own runner-up, so this is a re-read of what the
    head already ranked rather than a new decision: 0 passages lost and 7 won
    on seed 1, 0 and 6 on seed 2, 0 and 8 on seed 3.
    """
    bi, bj = int(ii[b]), int(jj[b])
    if d <= 0:
        return bi, bj
    best = float(sc[b])
    slot = {(int(x), int(y)): k for k, (x, y)
            in enumerate(zip(ii.tolist(), jj.tolist()))}
    found = []
    for a in range(radius + 1):
        for c in range(radius + 1):
            if not (a or c):
                continue
            got = slot.get((bi - a, bj + c))
            if got is not None and float(sc[got]) >= best - d:
                found.append((a + c, -a, bi - a, bj + c))
    if not found:
        return bi, bj
    win = max(found)
    return win[2], win[3]


# --- the trunk's mid-stack states ---------------------------------------------

class _States:
    """Block outputs at `LAYERS`, concatenated, for a batch of equal lengths.

    `scripts/train_reader.States`, with one difference that is deliberate: the
    hooks are registered for the duration of one read and removed after, where
    the trainer registers them once for the life of the process. The trainer
    owns its model; this one is the model the agent speaks with, and a hook
    left on it would hold a copy of every block output of every decode step of
    every turn for as long as the process lives.

    Hooks rather than a new `forward` argument, for `probe_scorer.Reader`'s
    reason: `corn/model.py` is on the measurement path for every row in this
    project and an instrument does not get to edit it.
    """

    def __init__(self, model, layers=LAYERS, causal: bool = True) -> None:
        self.model = model
        self.layers = layers
        # Which attention the read runs under. `True` is the shipped trunk's
        # and passes `corn/model.py` the same expression the line held before
        # the argument existed, so `HeadReader`'s forward is unmoved; a
        # bidirectional adapter, when one is trained, is this flag and not a
        # second reader (`docs/PLAN-READER-WHOLE.md` §2d, finding 112 §1).
        self.causal = causal
        self._buf: dict[int, torch.Tensor] = {}

    def _grab(self, k):
        def hook(_mod, _inp, out):
            self._buf[k] = (out[0] if isinstance(out, tuple) else out).detach()
        return hook

    @torch.no_grad()
    def read(self, idx: torch.Tensor) -> torch.Tensor:
        """`(B, T, len(layers) * n_embd)`."""
        handles = [self.model.blocks[k].register_forward_hook(self._grab(k))
                   for k in self.layers]
        try:
            self.model(idx, causal=self.causal)
            out = torch.cat([self._buf[k] for k in self.layers], dim=-1)
        finally:
            for h in handles:
                h.remove()
            self._buf.clear()
        return out


# --- the reader ---------------------------------------------------------------

class _Speaks:
    """`(span, margin)` per window rendered into the worker's own reply shape.

    The half both readers share, and it is shared rather than copied because it
    is the one place a threshold is compared: `It's {span}.` above it,
    `corn.gate.decline_text` below it, and `corn/extract.py`'s `reduce`,
    `grounded`, `det_repair` and every scorer on either side of that unchanged.
    A second copy of this would be a second operating point nobody chose.

    A subclass owns `read`, `threshold` and `extent_d` and nothing else.
    """

    threshold: float
    extent_d: float

    def read(self, question: str, prompts: list[str], windows_: list[str],
             source: str = SOURCE) -> list[tuple[str, float]]:
        raise NotImplementedError

    def margins(self, question: str, prompts: list[str], windows_: list[str],
                source: str = SOURCE) -> list[float]:
        """Just the margins. What a threshold sweep wants."""
        return [m for _, m in self.read(question, prompts, windows_, source)]

    def replies(self, question: str, prompts: list[str], windows_: list[str],
                source: str = SOURCE,
                threshold: float | None = None) -> tuple[list[str], list[float]]:
        """`(N replies, N margins)`. The margins come back because the hybrid
        reduce needs to know which window was surest -- see
        `harness/backends/read.py`."""
        t = self.threshold if threshold is None else threshold
        reads = self.read(question, prompts, windows_, source)
        return ([SAY.format(a=span) if margin >= t
                 else decline_text(question, w)
                 for (span, margin), w in zip(reads, windows_)],
                [m for _, m in reads])

    def __call__(self, question: str, prompts: list[str],
                 windows_: list[str], source: str = SOURCE) -> list[str]:
        return self.replies(question, prompts, windows_, source)[0]


class HeadReader(_Speaks):
    """`(question, prompts, windows) -> N worker-shaped replies`. A `run`.

    What `corn.extract.read_passage` takes in place of the generative worker:
    N prompts in, N replies out, and everything on either side of it is
    `corn/extract.py`'s arithmetic. The reply is the worker's own -- `It's
    {span}.` for a window whose margin clears the threshold,
    `corn.gate.decline_text` for one that does not -- which is what lets
    `reduce`, `grounded`, `det_repair` and every scorer read this arm and the
    generative arm on the same ladder.

    **No decode at all.** One trunk forward per bucket of equal-length
    prompts, against the gate's forward *plus* 32 decode steps per admitted
    window. Latency goes down.

    Holds the model it was built with and nothing else about the turn, the
    posture `corn.gate.WindowGate` takes and for the same reason: the module
    that cuts the passage and reduces the replies stays free of weights.
    """

    def __init__(self, model, tok, span_path: str, verifier_path: str,
                 device: str = "cuda",
                 threshold: float = READER_THRESHOLD,
                 extent_d: float = EXTENT_D, batch: int = 16) -> None:
        self.model = model
        self.tok = tok
        self.device = device
        self.threshold = threshold
        self.extent_d = extent_d
        self.batch = batch
        self.states = _States(model)
        self.span, self.span_meta = load_span_head(span_path, device)
        self.verifier, self.verifier_meta = load_verifier(verifier_path, device)

    @torch.no_grad()
    def read(self, question: str, prompts: list[str], windows_: list[str],
             source: str = SOURCE) -> list[tuple[str, float]]:
        """`(span, margin)` per window, in the input's order.

        The reference is `train_reader_cached.read_cached`'s `pair_rows`
        branch, and the only difference is where the states come from: there
        they are read off an fp16 store harvested from this trunk, here the
        trunk is run. `scripts/check_reader_popa.py` is the guard that says
        the two agree.
        """
        if len(prompts) != len(windows_):
            raise ValueError(f"{len(prompts)} prompts, {len(windows_)} windows")
        rows = []
        for prompt, w in zip(prompts, windows_):
            ids, keep = candidates(self.tok, prompt, question, w, source)
            rows.append({"ids": ids, "keep": keep})
        out: list[tuple[str, float] | None] = [None] * len(prompts)
        # A window with no candidate position has no pair to point at and
        # nothing for the verifier to read. It is silenced rather than
        # guessed at -- the conservative direction, and the same one
        # `corn.gate.willingness` takes on a prompt it cannot score.
        live = [i for i, r in enumerate(rows) if r["keep"]]
        for i in range(len(rows)):
            if not rows[i]["keep"]:
                out[i] = ("", float("-inf"))
        for group in bucket([rows[i]["ids"] for i in live]):
            for k in range(0, len(group), self.batch):
                chunk = [live[g] for g in group[k:k + self.batch]]
                idx = torch.tensor([rows[i]["ids"] for i in chunk],
                                   dtype=torch.long, device=self.device)
                h = self.states.read(idx)
                for b, i in enumerate(chunk):
                    out[i] = self._one(h[b], rows[i])
        return [o for o in out]  # type: ignore[misc]

    def _one(self, h_row: torch.Tensor, row: dict) -> tuple[str, float]:
        """One window: score the pairs, verify the argmax, widen it, decode."""
        keep, ids = row["keep"], row["ids"]
        h = h_row[keep].float()
        q = h_row[-1].float()[None]
        n = len(keep)
        ii, jj = pair_index(n, self.device)
        row_w = torch.zeros(n, dtype=torch.long, device=self.device)
        sc = self.span.score(h, q, ii, jj, row_w)
        b = int(torch.argmax(sc).item())
        # **The verifier reads the argmax pair, not the pair the extent rule
        # widens to.** The rule is a read-time repair of where the span ends
        # and the verifier's training saw argmax rows, so widening in front of
        # it would hand it a distribution it never trained on.
        margin = float(self.verifier(q, span_features(sc, ii, jj),
                                     h[int(ii[b])][None], h[int(jj[b])][None])[0])
        i2, j2 = extend(sc, ii, jj, b, self.extent_d)
        span = self.tok.decode(ids[keep[i2]:keep[j2] + 1]).strip()
        return span, margin


class WholeHeadReader(_Speaks):
    """The same `run`, reading each passage whole through an adapted trunk.

    `docs/PLAN-READER-PORT.md` §2.2. Three things change against `HeadReader`
    and nothing else does:

        the window     the payload's `answer` field carries the whole passage,
                       so there is one forward, one null and no vote
        the trunk      the reading forward runs with `corn/model.py`'s adapter
                       on -- the same 160 deltas the head was fitted beside,
                       out of the same file -- and off again after
        the head       `WholeHead` above, whose null is a row of the pairs'
                       own softmax, so there is no second head and the margin
                       is `max s - s_null`

    On Population A that reads **523 of 721 answerable passages right at 198
    correct silences of 282** against the window head's 392 and 199 (finding
    116), which is +131 right answers on the same passages. It costs one
    forward a passage where the window head costs up to eight.

    **A passage whose prompt does not fit the block declines and is counted.**
    There is no cut to fall back on here -- that is the whole point of the arm
    -- so a passage over the 512 block is silent rather than truncated, which
    is one of Population A's 1,003. Truncating it would hand the head a passage
    the answer had been cut out of and let it point somewhere inside what was
    left, which is the invention the reader exists to avoid.

    Holds the model it was built with and nothing else about the turn,
    `HeadReader`'s posture and for its reason.
    """

    def __init__(self, model, tok, adapter_path: str, trunk_ckpt: str,
                 device: str = "cuda",
                 threshold: float = WHOLE_THRESHOLD,
                 extent_d: float = EXTENT_D) -> None:
        self.model = model
        self.tok = tok
        self.device = device
        self.threshold = threshold
        self.extent_d = extent_d
        # **The adapter is loaded before the head, and the fingerprint is
        # checked before either.** One file carries both, so a head that
        # loaded while its deltas were refused would score adapted states it
        # never saw -- `corn.model.load_adapter` raises rather than returning
        # a flag for exactly that reason.
        self.adapter_meta = load_adapter(model, adapter_path, trunk_ckpt)
        self.head, self.head_meta = load_whole_head(adapter_path, device)
        # Read off the file rather than taken as an argument: an adapter
        # trained under `is_causal=False` and read causally is a picker handed
        # states it was never fitted on, and finding 112 §1 is what that reads
        # like. The shipped file is causal.
        self.causal = not bool(self.adapter_meta.get("args", {})
                               .get("bidirectional", False))
        self.states = _States(model, causal=self.causal)
        self.block = int(model.cfg.block_size)

    @torch.no_grad()
    def read(self, question: str, prompts: list[str], windows_: list[str],
             source: str = SOURCE) -> list[tuple[str, float]]:
        """`(span, margin)` per passage, in the input's order.

        The reference is `train_reader_whole.harvest_popa`, and the only
        difference is where the states come from: there the trunk runs under
        bf16 autocast inside the training process, here it is the runtime's own
        fp32 forward. One prompt a call in practice -- `read_passage`'s whole
        path hands this a list of one -- so there is no bucketing to do; the
        loop is written for N because the interface is N.
        """
        if len(prompts) != len(windows_):
            raise ValueError(f"{len(prompts)} prompts, {len(windows_)} windows")
        out: list[tuple[str, float]] = []
        with adapter(self.model):
            for prompt, w in zip(prompts, windows_):
                out.append(self._one(question, prompt, w, source))
        return out

    def _one(self, question: str, prompt: str, window: str,
             source: str) -> tuple[str, float]:
        ids, keep = candidates(self.tok, prompt, question, window, source)
        # The two refusals `train_reader_whole.build_items` counts and drops,
        # in the same order: a prompt the block cannot hold, and a passage with
        # no pair to point at. Both are silences rather than guesses, the
        # direction `corn.gate.willingness` takes on a prompt it cannot score.
        if len(ids) > self.block or len(keep) < 2:
            return "", float("-inf")
        idx = torch.tensor([ids], dtype=torch.long, device=self.device)
        h = self.states.read(idx)[0]
        n = len(keep)
        ii, jj = pair_index(n, self.device)
        sc = self.head.scores(h[keep], ii, jj)
        s0 = self.head.null(h[-1])
        b = int(torch.argmax(sc).item())
        # **The margin is the argmax pair's, not the widened span's**, which is
        # `scripts/probe_reader_rank.apply_extent`'s arrangement exactly: the
        # extent rule rewrites where the span ends and never what was admitted,
        # so every threshold on this arm was fitted against this quantity.
        margin = float(sc[b] - s0)
        i2, j2 = extend(sc, ii, jj, b, self.extent_d)
        span = self.tok.decode(ids[keep[i2]:keep[j2] + 1]).strip()
        return span, margin


def load_span_head(path: str, device: str = "cuda") -> tuple[SpanHead, dict]:
    """The built arm off disk, with its own record of what it is.

    The arm is asserted rather than inferred: `SpanHead` is the built arm and
    only that, so a `base` or `pointer` head loaded here would silently score
    with modules it never trained.
    """
    blob = torch.load(path, map_location=device, weights_only=False)
    if blob.get("arm") != "built":
        raise ValueError(f"{path}: arm {blob.get('arm')!r} -- corn/reader.py "
                         "is the built arm's architecture and nothing else")
    if tuple(blob.get("layers", LAYERS)) != tuple(LAYERS):
        raise ValueError(f"{path}: layers {blob.get('layers')} against "
                         f"{list(LAYERS)} -- the head reads a different band "
                         "from the one this module hooks")
    head = SpanHead(int(blob["dim"]), int(blob["hidden"]), len(LAYERS)).to(device)
    head.load_state_dict(blob["state"])
    head.eval()
    meta = {k: v for k, v in blob.items() if k not in ("state", "curve")}
    return head, meta


def load_verifier(path: str, device: str = "cuda") -> tuple[VerifierHead, dict]:
    """The pair-rows verifier off disk, with its shape asserted.

    Three assertions and each one is a head that would load and read wrong:
    a presence head (`pair_rows` off) would be handed rows it has no weights
    for, a `ln3` head would normalise the scalars with a LayerNorm this class
    does not build, and the re-ranker (`rerank` set) speaks a different span
    from the one the span head chose -- it was measured and retired in the
    eighty-sixth finding and must not arrive here by a filename.
    """
    blob = torch.load(path, map_location=device, weights_only=False)
    if not blob.get("pair_rows"):
        raise ValueError(f"{path}: not a pair-rows verifier -- corn/reader.py "
                         "reads the argmax pair's own rows and this head has "
                         "no weights for them")
    if blob.get("rerank"):
        raise ValueError(f"{path}: a re-ranker. Retired in the eighty-sixth "
                         "finding -- its pick rate never left the span head's")
    if blob.get("feat_norm") != "std" or int(blob.get("n_feat", 0)) != 3:
        raise ValueError(f"{path}: features {blob.get('n_feat')} normalised "
                         f"{blob.get('feat_norm')!r} -- this class is the "
                         "three standardised scalars")
    head = VerifierHead(int(blob["dim"]), int(blob["hidden"]), len(LAYERS),
                        int(blob["n_feat"])).to(device)
    head.load_state_dict(blob["state"])
    head.eval()
    meta = {k: v for k, v in blob.items() if k not in ("state", "curve")}
    return head, meta


def load_whole_head(path: str, device: str = "cuda") -> tuple[WholeHead, dict]:
    """The whole-passage head out of the adapter's own file.

    One file carries the head and the 160 deltas because they were fitted
    together and are only meaningful together -- a head read off adapted states
    scores unadapted ones as noise. So there is no second path argument here
    and no way to pair a head with the wrong adapter.

    **The shapes come off the tensors and the record is cross-examined against
    them.** `args` says `hidden` and `rank`; a file whose `pair.a` disagrees
    with its own `args` is a file that was edited, and reading the tensors and
    then checking the record catches that where trusting either alone does not.
    """
    blob = torch.load(path, map_location=device, weights_only=False)
    if "lora" not in blob or not blob["lora"]:
        raise ValueError(f"{path}: no adapter in this file -- corn/reader.py's "
                         "whole-passage arm reads an adapted trunk and a head "
                         "without its deltas scores states it never saw")
    if tuple(blob.get("layers", LAYERS)) != tuple(LAYERS):
        raise ValueError(f"{path}: layers {blob.get('layers')} against "
                         f"{list(LAYERS)} -- the head reads a different band "
                         "from the one this module hooks")
    state = blob["head"]
    width = int(state["norms.0.weight"].shape[0])
    hidden = int(state["pair.a.weight"].shape[0])
    n_layers = sum(1 for k in state if k.endswith(".weight")
                   and k.startswith("norms."))
    args = blob.get("args", {})
    if args.get("hidden") not in (None, hidden):
        raise ValueError(f"{path}: pair.a is {hidden} wide and args say "
                         f"{args.get('hidden')} -- the file disagrees with "
                         "itself")
    if n_layers != len(LAYERS):
        raise ValueError(f"{path}: {n_layers} layer norms against "
                         f"{len(LAYERS)} tapped layers")
    head = WholeHead(n_layers, width, hidden).to(device)
    head.load_state_dict(state)
    head.eval()
    return head, {k: v for k, v in blob.items()
                  if k not in ("head", "lora", "curve")}
