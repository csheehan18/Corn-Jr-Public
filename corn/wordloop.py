"""A small model shaped for a small model's two shortages: whole words in, depth without parameters, and his own surprise as something he can read.

**Why** (owner, 2026-10-22: "a 20M model could be decently coherent with the
right architecture"; the target is a reply that answers whatever he is sent
and says so, in varied words, when he does not know). Off by default:
`Config.arch = "gpt"` builds `corn.model.CornModel` and nothing here runs.
`arch = "wordloop"` builds this, the same pieces as the plain trunk
(`Block`, tied `wte`, learned `wpe`, `ln_f`) arranged differently, at the
plain trunk's parameter count. Three changes, each aimed at something read
in findings 197-201:

**1. Whole words in.** The tokenizer gives every common word one piece and a
rare one 3.25 on average (*euphemism* is ` e`+`up`+`hem`+`ism`, *cosy* is
` c`+`osy`; measured on the 300 held-out targets, 2026-10-22), so the plain
trunk has no slot for a rare word -- it rebuilds it from pieces it shares
with *up* and *hem* every time, and what a sighting teaches is spread over
those pieces. Here every piece after the first of a word also reads a row
for *the word so far*: the run of letter pieces since the word began (at
most `WORD_MAX`), hashed twice (two rows a key, summed -- two colliding
words rarely share both) into a `word_rows` x `word_dim` table, projected to
the width. A one-piece word reads nothing (its own `wte` row already is
the word). The projection starts at zero, so at step 0 the model computes
what the plain trunk computes and learns how much to use the table.

**2. Depth without parameters.** `n_layer` distinct blocks run `n_loops`
times (a per-pass vector added to the stream says which pass it is). The
parameters freed from the blocks the loop replaces go to the word table; the
compute goes up by `n_loops * n_layer / plain depth`. At 5M that buys a
12-deep model from 3 blocks: more steps to combine "numb face" + "dentist"
into *bad news*, which the 6-deep plain 5M answers "That's great!".

**3. His own surprise, as an input** (`surprise_input`). Finding 188: his
surprise on a word picks out the unfamiliar one at AUC 0.87 -- but the plain
trunk computes it at the output and throws it away. Here a first pass (no
gradient, the same weights, every token's surprise marked *unknown*) reads
each token's surprise -- the negative log-probability the model gave it --
binned into `SURPRISE_EDGES`, and the second pass adds a learned vector for
each token's bin. "I have never seen this" becomes something he reads, not
something he must infer. The first token of a window has no prediction and
reads *unknown*. The bin vectors start at zero, so step 0 is the plain
forward. Costs one extra forward per step.

**What it does not have**: a cached decode. `step` refuses: the word table
reads earlier pieces and the surprise input reads the previous prediction,
neither of which `GraphedDecoder`'s one-token step carries. Generation goes
through `forward` on the whole window (`generate`, below), which at 5M is
cheap; the scripts that read this model sample both models that way, so the
two are compared on one path. The eval card's behaviour rows (built on
`GraphedDecoder`) do not run on it; its language rows do (`nats_per_byte`
calls `forward`).

`scripts/check_wordloop.py` holds the claims: the default build is
untouched, step 0 equals the plain arrangement, the hash reads the word so
far and nothing across a word boundary, the surprise input is causal and
reads the first pass, and the parameter count matches.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
from torch.nn import functional as F

from .config import Config
from .model import Block

WORD_MAX = 8                     # pieces of a word the hash reads, at most
HASH_M = 2_147_483_647           # 2^31 - 1
HASH_P = 8209
HASH_SALTS = ((1_000_003, 12_345), (998_244_353 % HASH_M, 67_891))
# Bins of a token's surprise in nats: under 0.25 is "expected", over 12 is
# "never seen anything like it"; bin len(SURPRISE_EDGES) + 1 is "unknown".
SURPRISE_EDGES = (0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0)
UNKNOWN_BIN = len(SURPRISE_EDGES) + 1


def word_classes(tokenizer) -> tuple[torch.Tensor, torch.Tensor]:
    """(continues, ends_letter) over the vocabulary: a piece continues a word
    when it is ASCII letters with no leading space; a piece ends in a letter
    when its last byte is one."""
    tb = tokenizer.token_bytes()
    cont = torch.zeros(len(tb), dtype=torch.bool)
    ends = torch.zeros(len(tb), dtype=torch.bool)
    for i, b in enumerate(tb):
        if b and b.isalpha() and b.isascii():
            cont[i] = True
        if b and b[-1:].isalpha() and b[-1:].isascii():
            ends[i] = True
    return cont, ends


class WordLoopModel(nn.Module):
    def __init__(self, cfg: Config, vocab_size: int):
        super().__init__()
        from .tokenizer import get_tokenizer

        if cfg.n_loops < 1:
            raise ValueError("n_loops must be at least 1")
        if cfg.pos_enc != "learned" or cfg.tag_vocab:
            raise ValueError("wordloop reads learned positions and no tag map")
        self.cfg = cfg
        self.vocab_size = vocab_size
        d = cfg.n_embd
        self.wte = nn.Embedding(vocab_size, d)
        self.wpe = nn.Embedding(cfg.block_size, d)
        self.drop = nn.Dropout(cfg.dropout)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.ln_f = nn.LayerNorm(d, bias=cfg.bias)
        self.lm_head = nn.Linear(d, vocab_size, bias=False)
        if cfg.tie_embeddings:
            self.lm_head.weight = self.wte.weight
        self.apply(self._init_weights)
        depth = cfg.n_layer * cfg.n_loops
        for name, p in self.named_parameters():
            if name.endswith("c_proj.weight"):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * depth))
        self.loop_emb = nn.Parameter(torch.zeros(cfg.n_loops, d))
        self.word_table = None
        if cfg.word_rows:
            self.word_table = nn.Embedding(cfg.word_rows, cfg.word_dim)
            nn.init.normal_(self.word_table.weight, mean=0.0, std=0.02)
            self.word_proj = nn.Linear(cfg.word_dim, d, bias=False)
            nn.init.zeros_(self.word_proj.weight)
            cont, ends = word_classes(get_tokenizer(cfg.tokenizer))
            self.register_buffer("w_cont", cont, persistent=False)
            self.register_buffer("w_ends", ends, persistent=False)
            pk = [pow(HASH_P, k, HASH_M) for k in range(WORD_MAX)]
            self.register_buffer("w_pk", torch.tensor(pk, dtype=torch.long), persistent=False)
        self.surprise_emb = None
        if cfg.surprise_input:
            self.surprise_emb = nn.Embedding(UNKNOWN_BIN + 1, d)
            nn.init.zeros_(self.surprise_emb.weight)
            self.register_buffer("s_edges", torch.tensor(SURPRISE_EDGES), persistent=False)

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
            n -= self.wpe.weight.numel()
            if not self.cfg.tie_embeddings:
                n -= self.wte.weight.numel()
            if self.word_table is not None:
                n -= self.word_table.weight.numel()
        return n

    # -- the word table ------------------------------------------------------

    def word_keys(self, idx: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """(key, run) per position: `run` is how many pieces of the current
        word end here (1 at a word's first piece), `key` a hash of those
        pieces (the last `WORD_MAX`) and their count."""
        B, T = idx.shape
        prev = torch.cat([torch.zeros_like(idx[:, :1]), idx[:, :-1]], dim=1)
        start = ~(self.w_cont[idx] & self.w_ends[prev])
        start[:, 0] = True
        t = torch.arange(T, device=idx.device).expand(B, T)
        first = torch.cummax(torch.where(start, t, torch.zeros_like(t)), dim=1).values
        run = t - first + 1
        h = torch.zeros_like(idx)
        for k in range(min(WORD_MAX, T)):   # a window shorter than WORD_MAX has no piece k back
            xk = torch.cat([torch.zeros_like(idx[:, :k]), idx[:, :T - k]], dim=1) if k else idx
            h = h + torch.where(run > k, (xk + 1) * self.w_pk[k], torch.zeros_like(h))
        key = (h + torch.clamp(run, max=WORD_MAX) * 999_983) % HASH_M
        return key, run

    def word_vec(self, idx: torch.Tensor) -> torch.Tensor:
        key, run = self.word_keys(idx)
        R = self.cfg.word_rows
        e = sum(self.word_table((key * a + b) % HASH_M % R) for a, b in HASH_SALTS)
        return self.word_proj(e) * (run >= 2).unsqueeze(-1).to(e.dtype)

    # -- the forward -----------------------------------------------------------

    def _trunk(self, idx: torch.Tensor, bins: torch.Tensor | None) -> torch.Tensor:
        T = idx.size(1)
        pos = torch.arange(T, dtype=torch.long, device=idx.device)
        x = self.wte(idx) + self.wpe(pos)
        if self.word_table is not None:
            x = x + self.word_vec(idx)
        if bins is not None:
            x = x + self.surprise_emb(bins)
        x = self.drop(x)
        for i in range(self.cfg.n_loops):
            x = x + self.loop_emb[i]
            for block in self.blocks:
                x, _ = block(x)
        return self.ln_f(x)

    def surprise_bins(self, idx: torch.Tensor) -> torch.Tensor:
        """Each token's surprise under a first pass, binned; position 0 reads unknown."""
        with torch.no_grad():
            unknown = torch.full_like(idx, UNKNOWN_BIN)
            h = self._trunk(idx, unknown)
            lp = F.log_softmax(self.lm_head(h[:, :-1]).float(), dim=-1)
            s = -lp.gather(-1, idx[:, 1:].unsqueeze(-1)).squeeze(-1)
            b = torch.bucketize(s, self.s_edges)
            return torch.cat([unknown[:, :1], b], dim=1)

    def forward(
        self,
        idx: torch.Tensor,
        targets: torch.Tensor | None = None,
        caches=None,
        causal: bool = True,
        tags: torch.Tensor | None = None,
        attn_mask: torch.Tensor | None = None,
    ):
        if caches or tags is not None or attn_mask is not None or not causal:
            raise ValueError("wordloop takes the whole window: no cache, tags, mask or non-causal read")
        if idx.size(1) > self.cfg.block_size:
            raise ValueError(f"sequence {idx.size(1)} exceeds block_size {self.cfg.block_size}")
        bins = self.surprise_bins(idx) if self.surprise_emb is not None else None
        x = self._trunk(idx, bins)
        if targets is not None:
            logits = self.lm_head(x)
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.reshape(-1), ignore_index=-1)
        else:
            logits = self.lm_head(x[:, [-1], :])
            loss = None
        return logits, loss, []

    def step(self, *a, **k):
        raise NotImplementedError("wordloop has no cached decode -- generate through forward "
                                  "(corn/wordloop.py, 'What it does not have')")

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int, temperature: float = 0.8,
                 top_k: int | None = 50, use_cache: bool = False) -> torch.Tensor:
        return generate_nocache(self, idx, max_new_tokens, temperature, top_k)


@torch.no_grad()
def generate_nocache(model, idx: torch.Tensor, max_new_tokens: int, temperature: float,
                     top_k: int | None, stop_ids: set[int] | None = None) -> torch.Tensor:
    """Sample by re-reading the whole window each token -- the one decode path
    both `CornModel` and `WordLoopModel` share. Greedy at temperature 0.
    Stops a row's growth at `max_new_tokens`; every row of the batch grows
    together, so callers cut at their own markers."""
    model.eval()
    for _ in range(max_new_tokens):
        if idx.size(1) >= model.cfg.block_size:
            break
        logits, _, _ = model(idx[:, -model.cfg.block_size:])
        logits = logits[:, -1, :].float()
        if temperature <= 0:
            nxt = logits.argmax(-1, keepdim=True)
        else:
            logits = logits / temperature
            if top_k is not None:
                thresh = torch.topk(logits, min(top_k, logits.size(-1)), dim=-1).values[:, [-1]]
                logits = logits.masked_fill(logits < thresh, float("-inf"))
            nxt = torch.multinomial(F.softmax(logits, dim=-1), 1)
        idx = torch.cat([idx, nxt], dim=1)
        if stop_ids and idx.size(0) == 1 and int(nxt) in stop_ids:
            break
    return idx
