"""A standard decoder-only transformer. Deliberately unexciting.

VISION.md §10 argues for a plain transformer baseline before any recurrent or
memory-augmented work, because you need a control group to have discoveries
against. This is that control group: pre-LN, learned positional embeddings,
GELU MLP, causal attention via SDPA.

First swaps worth measuring against it, roughly in order of expected payoff:
RoPE instead of learned positions, RMSNorm instead of LayerNorm, SwiGLU instead
of GELU. Each should be a config flag before it is a code path.

**RoPE is that flag** (`Config.pos_enc = "rope"`, PLAN-TAG-SPINE §5 lever 4,
2026-09-12). Under it no `wpe` is built; instead every attention layer
rotates each head's q and k by the token's position before the dot product
(`apply_rope`), in the training forward and in the graphed `step` alike, so
the cache holds rotated keys and decode needs no new path. The trunk is
drawn exactly as the learned build draws it -- `wpe` is constructed, so the
generator advances the same, and then dropped -- so at one seed a RoPE arm
against a `wpe` arm is the encoding and nothing else. `scripts/check_model.py`
holds the learned path bit-identical to the pre-flag forward, holds the RoPE
`step` to the RoPE `forward`, and holds the property that is the whole reason
to try it: attention under RoPE is unchanged by a constant shift of every
position. The four scripts that hand-compute `wte + wpe` for the shipped
trunk (`train_reader_whole`, `probe_verifier`, `profile_decode_step`,
`check_model._before`) are learned-only by construction and fail loudly on a
RoPE checkpoint rather than reading a table that is not there.

**Two things at the bottom of this file are the reader's and not the
conversation's**: a low-rank adapter on the four block linears, off unless a
forward turns it on, and a `causal` argument that defaults to the shipped
`is_causal = T > 1`. Both exist because `corn/reader.py`'s whole-passage arm
reads the trunk with the weights moved (finding 112, finding 116: 523 of 721
against the frozen trunk's 392), and both are written so that the forward every
scorecard in this project was read through cannot move.
`scripts/check_model.py` is the proof, not the promise.
"""

from __future__ import annotations

import contextlib
import hashlib
import math
from pathlib import Path

import torch
import torch.nn as nn
from torch.nn import functional as F

from .config import Config

# A per-layer (keys, values) pair, or None on the first step.
KV = tuple[torch.Tensor, torch.Tensor]

# RoPE's (cos, sin) at the positions of one forward, each `(T, head_dim)`, or
# None under learned positions.
Rope = tuple[torch.Tensor, torch.Tensor] | None

POS_ENC = ("learned", "rope")


def rope_tables(block_size: int, head_dim: int, theta: float) -> tuple[torch.Tensor, torch.Tensor]:
    """cos and sin of every position's rotation angles, `(block_size, head_dim)` each, fp32.

    Pair `i` of a head (dimensions `i` and `i + head_dim/2`) turns at
    `theta ** (-2i / head_dim)` radians a position -- the usual geometric
    spread from one radian a token down to `1/theta`. The half-and-half
    layout (`rotate_half`) is the one the open implementations share, and
    it is a layout, not a semantic: any fixed pairing gives the same
    relative-position property.
    """
    if head_dim % 2:
        raise ValueError(f"RoPE needs an even head_dim, got {head_dim}")
    inv = 1.0 / (theta ** (torch.arange(0, head_dim, 2, dtype=torch.float32) / head_dim))
    angles = torch.outer(torch.arange(block_size, dtype=torch.float32), inv)
    angles = torch.cat((angles, angles), dim=-1)
    return angles.cos(), angles.sin()


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    h = x.shape[-1] // 2
    return torch.cat((-x[..., h:], x[..., :h]), dim=-1)


def apply_rope(q: torch.Tensor, k: torch.Tensor, rope: Rope) -> tuple[torch.Tensor, torch.Tensor]:
    """Rotate q and k, `(B, n_head, T, head_dim)`, by the angles of their positions.

    Computed in fp32 and cast back, whatever the model's dtype: the rotation is
    a per-pair complex multiply and bf16 would round the angle before the dot
    product reads it. Under autocast this is a handful of elementwise ops per
    layer; the cost at the nano shape is measured in the config that first
    carries the flag, not assumed.
    """
    cos, sin = rope
    cos = cos.float().view(1, 1, cos.shape[0], cos.shape[1])
    sin = sin.float().view(1, 1, sin.shape[0], sin.shape[1])
    qf, kf = q.float(), k.float()
    q_out = (qf * cos + rotate_half(qf) * sin).to(q.dtype)
    k_out = (kf * cos + rotate_half(kf) * sin).to(k.dtype)
    return q_out, k_out


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        if cfg.n_embd % cfg.n_head != 0:
            raise ValueError(f"n_embd {cfg.n_embd} not divisible by n_head {cfg.n_head}")
        self.n_head = cfg.n_head
        self.head_dim = cfg.n_embd // cfg.n_head
        self.dropout = cfg.dropout
        self.c_attn = nn.Linear(cfg.n_embd, 3 * cfg.n_embd, bias=cfg.bias)
        self.c_proj = nn.Linear(cfg.n_embd, cfg.n_embd, bias=cfg.bias)
        self.resid_dropout = nn.Dropout(cfg.dropout)
        # Which formulation `step` uses for decode attention. "sdpa" is the
        # shipped one and the default; `set_decode_attention` is the only thing
        # that changes it. Training and prefill never read this.
        self.decode_attn = "sdpa"

    def forward(self, x: torch.Tensor, kv: KV | None = None,
                causal: bool = True,
                attn_mask: torch.Tensor | None = None,
                rope: Rope = None) -> tuple[torch.Tensor, KV]:
        """`causal=False` lets every position read every other one.

        **`rope` is the position encoding when `Config.pos_enc == "rope"`**:
        the (cos, sin) of this forward's positions, applied to q and k before
        the cache is joined, so the cache holds rotated keys and a later
        query rotates only itself. None -- every learned-position model --
        leaves q and k exactly as the projection produced them.

        **`attn_mask` is PLAN-TAG-SPINE §4's structural mask**, a boolean
        `(B, 1, T, T)` with True where a query may read a key. It carries its
        own causality (the builder in `corn.data.Batcher` ands it in), so it
        replaces `is_causal` rather than adding to it, and it takes SDPA's
        explicit-mask path, which is a different kernel from the flash one
        the default takes: `scripts/check_model.py` holds the default path
        bit-identical to the pre-change forward, holds a mask that hides
        nothing *close* to it (a kernel's rounding, not a semantic), and
        holds a mask that hides one key as moving. No cache with it: a
        cached decode masks per slot in `step`, and the two are not the same
        arithmetic.

        **The default is the shipped arithmetic and there is no second code
        path**: `is_causal = T > 1 and causal` is what the line said before the
        argument existed, with `causal` pinned True. `scripts/check_model.py`
        holds the two byte-identical, and the reason the flag is here at all is
        `docs/PLAN-READER-WHOLE.md` §2d -- a bidirectional reading adapter is
        the one variant this trunk cannot express, and when one is trained it
        should arrive as an argument rather than as a forked forward bound onto
        the module at runtime (which is what `scripts/train_reader_whole.py`
        does inside its own process, and why the flip is not measurable from
        the runtime today).

        Nothing that decodes may pass `causal=False`: a cache holds keys the
        query is meant not to see, and `step` -- which is what decoding uses --
        has no such argument.
        """
        B, T, C = x.shape
        q, k, v = self.c_attn(x).split(C, dim=2)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        if rope is not None:
            q, k = apply_rope(q, k, rope)

        if kv is not None:
            k = torch.cat((kv[0], k), dim=2)
            v = torch.cat((kv[1], v), dim=2)

        # Two supported shapes: a full sequence with no cache (mask within), or
        # a single new token against a cache (attends to everything, no mask).
        # Chunked prefill into a non-empty cache would need an explicit mask.
        if T > 1 and kv is not None:
            raise NotImplementedError("multi-token append to a non-empty cache")

        if kv is not None and not causal:
            raise NotImplementedError("a bidirectional read has no cache")

        if attn_mask is not None:
            if kv is not None:
                raise NotImplementedError("a structural mask has no cache")
            y = F.scaled_dot_product_attention(
                q, k, v, attn_mask=attn_mask,
                dropout_p=self.dropout if self.training else 0.0)
        else:
            y = F.scaled_dot_product_attention(
                q, k, v, dropout_p=self.dropout if self.training else 0.0,
                is_causal=T > 1 and causal
            )
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.resid_dropout(self.c_proj(y)), (k, v)

    def step(
        self,
        x: torch.Tensor,
        k_buf: torch.Tensor,
        v_buf: torch.Tensor,
        pos: torch.Tensor,
        mask: torch.Tensor,
        rope: Rope = None,
    ) -> torch.Tensor:
        """One decode token against preallocated cache buffers.

        `rope` is as in `forward`: the (cos, sin) of the slots `pos` names,
        gathered by `CornModel.step` from device tensors, so a captured graph
        reads the current slot's angles on every replay.

        The `forward` path above grows its cache with `torch.cat`, which means a
        new allocation and a new shape on every token -- fine for correctness,
        impossible to capture into a CUDA graph. Here the buffers are fixed and
        everything that varies per step (`pos`, `mask`) is a device tensor, so
        no Python value gets baked in and the whole step is capturable.

        Attention runs over the full `block_size` window every step regardless
        of how much of it is filled. That is the price of static shapes.

        **`decode_attn="manual"` writes the same arithmetic as an explicit
        matmul pair.** A boolean `attn_mask` disqualifies SDPA's flash backend,
        so the shipped call lands on the memory-efficient kernel -- which is
        built for many query tokens and is carrying tiling machinery that one
        query token cannot amortise. Profiled at 20 layers x 512 slots it costs
        0.817 ms against the explicit form's 0.348 ms, and forcing the math
        backend instead is worse than either at 1.199 ms.

        The softmax runs in fp32 no matter the model's dtype, matching what
        SDPA does internally. It is still **not bit-identical to SDPA**, and
        that is measured rather than hoped:

            attention output, 512 slots, bf16, against an fp64 reference
              sdpa            0.00119 from truth
              manual          0.00142 from truth
              the two differ by 0.00195

        All three quantities are the same size, which is the whole finding:
        neither formulation is nearer the true value, they are two orderings of
        the same sum and bf16 rounds them apart. Accumulating the PV matmul in
        fp32 does not help -- it lands at 0.00149, marginally *further* from
        truth -- so it buys nothing for its 1.4x cost and is not offered.

        The consequence is a rule, not a caveat. Greedy decoding stays
        token-identical on three of four checkpoint/dtype pairs measured and
        diverges once, at token 126 of 128, where the top-two logit gap had
        closed to less than the ~1%-of-scale difference this rounding
        produces. So `manual` is for the interactive path, and **anything that
        produces a scorecard must stay on `sdpa`** -- PLAN-PHASE-3 ground rule
        4 requires a scorer change to reproduce frozen checkpoints
        byte-identically, and this cannot promise that.
        """
        B, T, C = x.shape
        q, k, v = self.c_attn(x).split(C, dim=2)
        q = q.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, self.head_dim).transpose(1, 2)
        if rope is not None:
            q, k = apply_rope(q, k, rope)

        k_buf.index_copy_(2, pos, k)
        v_buf.index_copy_(2, pos, v)

        if self.decode_attn == "manual":
            att = (q @ k_buf.transpose(-2, -1)).float() * (self.head_dim ** -0.5)
            att = att.masked_fill(~mask, float("-inf")).softmax(dim=-1)
            y = att.to(v_buf.dtype) @ v_buf
        else:
            y = F.scaled_dot_product_attention(q, k_buf, v_buf, attn_mask=mask)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.c_proj(y)


class MLP(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.c_fc = nn.Linear(cfg.n_embd, 4 * cfg.n_embd, bias=cfg.bias)
        self.c_proj = nn.Linear(4 * cfg.n_embd, cfg.n_embd, bias=cfg.bias)
        self.dropout = nn.Dropout(cfg.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.dropout(self.c_proj(F.gelu(self.c_fc(x))))


class Block(nn.Module):
    def __init__(self, cfg: Config):
        super().__init__()
        self.ln_1 = nn.LayerNorm(cfg.n_embd, bias=cfg.bias)
        self.attn = CausalSelfAttention(cfg)
        self.ln_2 = nn.LayerNorm(cfg.n_embd, bias=cfg.bias)
        self.mlp = MLP(cfg)

    def forward(self, x: torch.Tensor, kv: KV | None = None,
                causal: bool = True,
                attn_mask: torch.Tensor | None = None,
                rope: Rope = None) -> tuple[torch.Tensor, KV]:
        attn_out, new_kv = self.attn(self.ln_1(x), kv, causal, attn_mask, rope)
        x = x + attn_out
        x = x + self.mlp(self.ln_2(x))
        return x, new_kv

    def step(
        self,
        x: torch.Tensor,
        k_buf: torch.Tensor,
        v_buf: torch.Tensor,
        pos: torch.Tensor,
        mask: torch.Tensor,
        rope: Rope = None,
    ) -> torch.Tensor:
        x = x + self.attn.step(self.ln_1(x), k_buf, v_buf, pos, mask, rope)
        return x + self.mlp(self.ln_2(x))


class CornModel(nn.Module):
    def __init__(self, cfg: Config, vocab_size: int):
        super().__init__()
        self.cfg = cfg
        self.vocab_size = vocab_size
        self.wte = nn.Embedding(vocab_size, cfg.n_embd)
        self.wpe = nn.Embedding(cfg.block_size, cfg.n_embd)
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(cfg.n_embd, bias=cfg.bias)
        self.lm_head = nn.Linear(cfg.n_embd, vocab_size, bias=False)
        if cfg.tie_embeddings:
            self.lm_head.weight = self.wte.weight
        if cfg.tag_vocab and not 0 <= cfg.tag_layer <= cfg.n_layer - 1:
            raise ValueError(f"tag_layer {cfg.tag_layer} is not a block of "
                             f"{cfg.n_layer}; 0 is the embedding sum")
        if cfg.pos_enc not in POS_ENC:
            raise ValueError(f"pos_enc must be one of {POS_ENC}, got {cfg.pos_enc!r}")

        self.apply(self._init_weights)
        # Scaled init on residual projections (GPT-2), so the residual stream
        # does not grow with depth.
        for name, p in self.named_parameters():
            if name.endswith("c_proj.weight"):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * cfg.n_layer))

        # The tag map (PLAN-LOOP §4; the field's comment in `corn/config.py`
        # says why). Absent unless asked for, so an old state dict has nothing
        # unexpected in it and a new one loads onto an old shape only by
        # asking. `padding_idx=0` makes "no tag" a zero row with no gradient:
        # an untagged token computes what it always computed, bit for bit.
        #
        # **Built last, and off a forked generator**, so that a config with
        # `tag_vocab=9` draws the same trunk -- and then the same batch
        # offsets, which `Batcher` takes from the global generator -- as the
        # same config with `tag_vocab=0` at the same seed. Arm F against arm
        # G is then the map and nothing else; `scripts/check_model.py` holds
        # the trunk equal across the two.
        self.tag_emb = None
        if cfg.tag_vocab:
            with torch.random.fork_rng(devices=[]):
                torch.manual_seed(cfg.seed ^ 0x7A6)
                self.tag_emb = nn.Embedding(cfg.tag_vocab, cfg.n_embd, padding_idx=0)
                nn.init.normal_(self.tag_emb.weight, mean=0.0, std=0.02)
                with torch.no_grad():
                    self.tag_emb.weight[0].zero_()

        # The position encoding (the file's header). Under "rope" the `wpe`
        # built above is dropped *after* every draw the learned build makes,
        # so the trunk and the generator's position are the learned build's
        # at the same seed; the rotation tables are buffers and not
        # parameters, not saved, and rebuilt from the config on load.
        if cfg.pos_enc == "rope":
            del self.wpe
            self.wpe = None
            cos, sin = rope_tables(cfg.block_size, cfg.n_embd // cfg.n_head,
                                   cfg.rope_theta)
            self.register_buffer("rope_cos", cos, persistent=False)
            self.register_buffer("rope_sin", sin, persistent=False)
        else:
            self.rope_cos: torch.Tensor | None = None
            self.rope_sin: torch.Tensor | None = None

    def _rope(self, pos: torch.Tensor) -> Rope:
        """The (cos, sin) of `pos`, a `(T,)` tensor of positions, or None under `wpe`."""
        if self.rope_cos is None:
            return None
        return self.rope_cos[pos], self.rope_sin[pos]

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def num_params(self, non_embedding: bool = False) -> int:
        n = sum(p.numel() for p in self.parameters())
        if non_embedding:
            if self.wpe is not None:
                n -= self.wpe.weight.numel()
            if not self.cfg.tie_embeddings:
                n -= self.wte.weight.numel()
            if self.tag_emb is not None:
                n -= self.tag_emb.weight.numel()
        return n

    def forward(
        self,
        idx: torch.Tensor,
        targets: torch.Tensor | None = None,
        caches: list[KV] | None = None,
        causal: bool = True,
        tags: torch.Tensor | None = None,
        attn_mask: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor | None, list[KV]]:
        """`tags` is the per-token label map of PLAN-LOOP §4, or nothing;
        `attn_mask` is PLAN-TAG-SPINE §4's structural mask, or nothing --
        see `CausalSelfAttention.forward` for both contracts.

        **Nothing changes unless it is passed**: the embedding line below is
        the line it always was when `tags` is None, and `scripts/check_model.py`
        holds the three sameness cases -- module absent, module present and
        `tags` None, `tags` all zero -- bit-identical to the pre-change
        forward, plus the control that a non-zero map must move it. Same shape
        as `idx`; id 0 is "no tag". Generated tokens are never tagged, so
        `step` has no such argument and the decode graph is untouched -- only
        `GraphedDecoder.prefill` takes a map, once per level.
        """
        B, T = idx.shape
        past = caches[0][0].size(2) if caches else 0
        if past + T > self.cfg.block_size:
            raise ValueError(f"sequence {past + T} exceeds block_size {self.cfg.block_size}")
        if tags is not None:
            if self.tag_emb is None:
                raise ValueError("a tag map was passed to a model built with "
                                 "tag_vocab=0 -- it has nowhere to put it")
            if tags.shape != idx.shape:
                raise ValueError(f"tags {tuple(tags.shape)} against idx {tuple(idx.shape)}")
        if attn_mask is not None and tuple(attn_mask.shape) != (B, 1, T, T):
            raise ValueError(f"attn_mask {tuple(attn_mask.shape)} against "
                             f"({B}, 1, {T}, {T})")

        pos = torch.arange(past, past + T, dtype=torch.long, device=idx.device)
        rope = self._rope(pos)
        if rope is not None:
            # No `wpe`: the position enters at every attention layer instead.
            x = self.wte(idx)
            if tags is not None and self.cfg.tag_layer == 0:
                x = x + self.tag_emb(tags)
            x = self.drop(x)
        elif tags is not None and self.cfg.tag_layer == 0:
            x = self.drop(self.wte(idx) + self.wpe(pos) + self.tag_emb(tags))
        else:
            x = self.drop(self.wte(idx) + self.wpe(pos))

        new_caches: list[KV] = []
        for i, block in enumerate(self.blocks):
            if tags is not None and i == self.cfg.tag_layer and i > 0:
                x = x + self.tag_emb(tags)
            x, kv = block(x, caches[i] if caches else None, causal, attn_mask, rope)
            new_caches.append(kv)
        x = self.ln_f(x)

        if targets is not None:
            logits = self.lm_head(x)
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)), targets.reshape(-1), ignore_index=-1
            )
        else:
            # Only the last position matters for sampling; skip the rest of the
            # head. At vocab 256 this is small, at 32k it is not.
            logits = self.lm_head(x[:, [-1], :])
            loss = None
        return logits, loss, new_caches

    def step(
        self,
        idx: torch.Tensor,
        k_bufs: list[torch.Tensor],
        v_bufs: list[torch.Tensor],
        pos: torch.Tensor,
        mask: torch.Tensor,
    ) -> torch.Tensor:
        """Decode forward against preallocated buffers. Eval mode, no dropout.

        Kept separate from `forward` rather than folded into it: `forward` is
        the training path and stays readable, and this one is written under the
        constraint that it must survive CUDA graph capture. See
        `corn/decode.py` for the thing that captures it.

        **One token or several.** `idx` is `(1, T)`, `pos` carries one write
        slot per token and `mask` is `(1, 1, T, slots)`. At `T == 1` that is
        the decode step every graph captures and nothing about it changed. At
        `T > 1` it is a *chunked prefill into a live cache* -- what
        `CausalSelfAttention.forward` refuses outright ("multi-token append to
        a non-empty cache") because a `torch.cat` cache has no way to express
        one. Static buffers do: `index_copy_` takes a `T`-element index and the
        mask says which slots each of the `T` rows may see, so appending a span
        to a cache that already holds a prefix is the same three lines as
        appending one token.

        That primitive is what lets a turn keep the KV of an unchanged prefix
        instead of recomputing it -- 42.1% of a turn's prefill on the measured
        corpus (`scripts/prefill_redundancy.py`).
        """
        rope = self._rope(pos)
        if rope is not None:
            x = self.wte(idx)
        else:
            x = self.wte(idx) + self.wpe(pos).view(1, idx.size(1), -1)
        for i, block in enumerate(self.blocks):
            x = block.step(x, k_bufs[i], v_bufs[i], pos, mask, rope)
        return self.lm_head(self.ln_f(x))

    @torch.no_grad()
    def generate(
        self,
        idx: torch.Tensor,
        max_new_tokens: int,
        temperature: float = 0.8,
        top_k: int | None = 50,
        use_cache: bool = True,
    ) -> torch.Tensor:
        """Reference generation: correct, unoptimised, and cheap to reason about.

        Interactive decoding goes through `corn/decode.py` instead, which is
        ~4x faster and considerably harder to be sure of -- so this stays as the
        thing that one gets checked against.
        """
        if idx.size(0) == 1:
            new = list(self._sample_loop(idx, max_new_tokens, temperature, top_k, use_cache))
            if not new:
                return idx
            tail = torch.tensor([new], dtype=idx.dtype, device=idx.device)
            return torch.cat((idx, tail), dim=1)
        return self._generate_batched(idx, max_new_tokens, temperature, top_k, use_cache)

    @torch.no_grad()
    def _sample_loop(
        self,
        idx: torch.Tensor,
        max_new_tokens: int,
        temperature: float,
        top_k: int | None,
        use_cache: bool,
    ):
        self.eval()
        caches: list[KV] | None = None
        for _ in range(max_new_tokens):
            if use_cache and idx.size(1) >= self.cfg.block_size:
                break
            if use_cache and caches is not None:
                step_input = idx[:, -1:]
            else:
                step_input = idx[:, -self.cfg.block_size :]
            logits, _, new_caches = self.forward(step_input, caches=caches)
            if use_cache:
                caches = new_caches
            next_id = self._sample_next(logits, temperature, top_k)
            idx = torch.cat((idx, next_id), dim=1)
            yield int(next_id.item())

    def _sample_next(
        self, logits: torch.Tensor, temperature: float, top_k: int | None
    ) -> torch.Tensor:
        logits = logits[:, -1, :] / max(temperature, 1e-6)
        if top_k is not None:
            k = min(top_k, logits.size(-1))
            thresh = torch.topk(logits, k, dim=-1).values[:, [-1]]
            logits = logits.masked_fill(logits < thresh, float("-inf"))
        return torch.multinomial(F.softmax(logits, dim=-1), num_samples=1)

    @torch.no_grad()
    def _generate_batched(
        self,
        idx: torch.Tensor,
        max_new_tokens: int,
        temperature: float,
        top_k: int | None,
        use_cache: bool,
    ) -> torch.Tensor:
        self.eval()
        caches: list[KV] | None = None
        for _ in range(max_new_tokens):
            if use_cache and idx.size(1) >= self.cfg.block_size:
                # Context is full and this baseline has no sliding window yet.
                break
            if use_cache and caches is not None:
                step_input = idx[:, -1:]
            else:
                step_input = idx[:, -self.cfg.block_size :]
            logits, _, new_caches = self.forward(step_input, caches=caches)
            if use_cache:
                caches = new_caches
            idx = torch.cat((idx, self._sample_next(logits, temperature, top_k)), dim=1)
        return idx


def set_decode_attention(model: CornModel, mode: str) -> None:
    """Choose the decode-time attention formulation. See `CausalSelfAttention.step`.

    Decode-only: `forward` is untouched, so training, prefill and the
    `cat`-cache reference path are the same computation whatever this is set
    to. "sdpa" is the default and restores the shipped behaviour exactly.
    """
    if mode not in ("sdpa", "manual"):
        raise ValueError(f"decode attention must be 'sdpa' or 'manual', got {mode!r}")
    for block in model.blocks:
        block.attn.decode_attn = mode


# --- the reading adapter ------------------------------------------------------
#
# A low-rank adapter on the four block linears, **off unless a forward asks for
# it**. `docs/PLAN-READER-WHOLE.md` §4.1 and finding 112: a rank-32 adapter on
# `c_attn`, `c_proj`, `c_fc` and `c_proj`, trained with the base frozen, reads
# 523 of Population A's 721 answerable passages where the frozen trunk's window
# reader reads 392 -- and it reads them by moving the states the reader head
# is handed, so it cannot be a head file and has to live here.
#
# **The conversational checkpoint is what this file must not be able to
# disturb.** Every scorecard, eval row and finding in this project was read off
# `CornModel.forward` as it was; a reader that could change one byte of it
# would put the whole card back in question. So the base `nn.Linear` is held by
# reference and never written, the delta is added only while a flag is on, and
# `scripts/check_model.py` asserts three byte-identities: the forward with the
# adapter absent, with `causal=True`, and with the adapter present and its `b`
# at the zero it is initialised to.

class LoRALinear(nn.Module):
    """`base(x) + (x A^T) B^T * alpha / r`, added only while `on`.

    `scripts/train_reader_whole.LoRALinear`'s arithmetic, with the switch and
    without the training-side `requires_grad` bookkeeping -- this class never
    trains. The scale is folded at construction as it is there, so the file on
    disk and this module agree on `alpha / r` rather than on `alpha` and `r`
    separately.

    `on` is per module and is set through `set_adapter` / `adapter` rather than
    per instance, because a half-enabled trunk is a fourth thing nobody
    measured: the checkpoint was trained with all eighty deltas present.
    """

    def __init__(self, base: nn.Linear, r: int, alpha: float) -> None:
        super().__init__()
        self.base = base
        # Drawn where the base already lives. Wrapping happens *after* the
        # trunk is on its device, so a delta built on the CPU would be a delta
        # the matmul cannot see -- and `load_state_dict` copies into these
        # parameters rather than replacing them, so it would not fix it either.
        w = base.weight
        self.lora_a = nn.Parameter(torch.zeros(r, base.in_features,
                                               device=w.device, dtype=w.dtype))
        self.lora_b = nn.Parameter(torch.zeros(base.out_features, r,
                                               device=w.device, dtype=w.dtype))
        self.scale = alpha / r
        self.on = False

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not self.on:
            return self.base(x)
        return self.base(x) + (x @ self.lora_a.t() @ self.lora_b.t()) * self.scale


# The four linears the adapter wraps, in the order `train_reader_whole.add_lora`
# wraps them -- which is the order the 160 tensors in a checkpoint are named
# for, so a rename here would be a silent key mismatch rather than an error.
ADAPTED = (("attn", "c_attn"), ("attn", "c_proj"),
           ("mlp", "c_fc"), ("mlp", "c_proj"))


def add_adapter(model: CornModel, r: int, alpha: float) -> None:
    """Wrap every block linear in a `LoRALinear`, off.

    **After `load_state_dict`, never before.** Wrapping renames
    `blocks.0.attn.c_attn.weight` to `...c_attn.base.weight`, so a trunk loaded
    into a wrapped model would fail on every one of those keys -- loudly, which
    is the right failure, but the ordering is the caller's to get right and
    `load_adapter` is the only thing in the runtime that does this.
    """
    for blk in model.blocks:
        for parent, name in ADAPTED:
            mod = getattr(blk, parent)
            base = getattr(mod, name)
            if isinstance(base, LoRALinear):
                raise ValueError(f"{parent}.{name} is already adapted")
            setattr(mod, name, LoRALinear(base, r, alpha))


def set_adapter(model: CornModel, on: bool) -> None:
    """Turn every delta on or off. No-op on a model with no adapter."""
    for mod in model.modules():
        if isinstance(mod, LoRALinear):
            mod.on = on


@contextlib.contextmanager
def adapter(model: CornModel, on: bool = True):
    """The adapter for the duration of one read, and off again after.

    A context manager and not a setter for `corn.reader._States`' reason: the
    reader shares the model the agent speaks with, and a flag left on would
    make the next turn's decode a different model from the one every card in
    `evals/results/` was read off. The restore is the previous value rather
    than `False`, so nesting reads the way it looks like it reads.
    """
    was = [mod.on for mod in model.modules() if isinstance(mod, LoRALinear)]
    set_adapter(model, on)
    try:
        yield model
    finally:
        for mod, prev in zip((m for m in model.modules()
                              if isinstance(m, LoRALinear)), was):
            mod.on = prev


def sha256(path: str | Path, chunk: int = 1 << 22) -> str:
    """`scripts/harvest_states.sha256`, moved for rule 29 and nothing else."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_adapter(model: CornModel, path: str, trunk_ckpt: str) -> dict:
    """The adapter off disk onto `model`, or a refusal. Returns its metadata.

    **The fingerprint is the whole point of this function.** An adapter is a
    delta on particular weights: the same 160 tensors on a trunk they were not
    fitted to load without error and read nonsense, because the shapes are the
    architecture's and not the checkpoint's. The trunk *will* move -- the
    social workstream is fine-tuning it, and the adapter is retrained when it
    does -- so a mismatch is the expected accident rather than an exotic one.
    `train_reader_whole.py` writes the trunk checkpoint's sha256 into the file
    at save time, this re-reads that file, and a difference is a refusal with
    both hashes named, the way `corn.tokenizer.check_fingerprint` refuses a
    tokenizer the checkpoint was not trained with.

    A file with no fingerprint at all is refused for the same reason. It is not
    "an older file that is probably fine": it is a file that cannot say which
    trunk it belongs to, and the checkpoints on this disk were re-saved with
    one rather than grandfathered.
    """
    blob = torch.load(path, map_location="cpu", weights_only=False)
    want = blob.get("trunk_sha256")
    if not want:
        raise ValueError(
            f"{path}: no trunk_sha256 -- an adapter that cannot name the trunk "
            "it was fitted to cannot be loaded onto one. Re-save it with "
            "scripts/stamp_adapter.py")
    got = sha256(trunk_ckpt)
    if got != want:
        raise ValueError(
            f"{path} was fitted to trunk {want[:12]} and {trunk_ckpt} is "
            f"{got[:12]} -- a low-rank delta on the wrong weights loads "
            "without error and reads nonsense, so this is refused")
    args = blob.get("args", {})
    add_adapter(model, int(args["rank"]), float(args["alpha"]))
    missing, unexpected = model.load_state_dict(blob["lora"], strict=False)
    if unexpected:
        raise ValueError(f"{path}: {len(unexpected)} tensors this model has no "
                         f"home for, first {unexpected[0]!r}")
    if any("lora_" in k for k in missing):
        bad = [k for k in missing if "lora_" in k]
        raise ValueError(f"{path}: {len(bad)} adapter tensors the file does "
                         f"not carry, first {bad[0]!r}")
    set_adapter(model, False)
    return {k: v for k, v in blob.items()
            if k not in ("lora", "head", "curve")}


def build_model(cfg: Config, vocab_size: int) -> CornModel:
    return CornModel(cfg, vocab_size)
