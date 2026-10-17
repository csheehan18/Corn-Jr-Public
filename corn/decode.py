"""Static-cache decoding, with an optional CUDA graph over the decode step.

Why this exists: the Phase 0 bench found that decode cost tracks *layer count*
at a flat per-layer price, not parameter count, which is the signature of being
bound by per-kernel launch overhead rather than by memory bandwidth. If that
diagnosis is right, then collapsing a whole decode step into one launch should
remove most of the cost, and a 250M model stops being latency-limited by depth.

`torch.compile` is the usual answer, and this file was written when it was
unavailable -- Inductor needs Triton and Triton had no working install on this
box. That is no longer true: `triton-windows` installs into `.venv` and
`torch.compile` runs, for 1.145x on the *training* step. It has not been tried
here, and the reason to reach for graphs first still holds: they change nothing
about the kernels, only how many times the CPU has to talk to the GPU, which
tests the launch-bound diagnosis directly rather than confounding it with
fusion. Whether compile beats the graph on decode, or composes with it, is
open and unmeasured -- do not read the training figure as a decode one.

Capture imposes two requirements, and they are the whole design:

  * fixed shapes and fixed addresses -- hence `StaticCache` preallocating the
    full `block_size` window up front instead of growing it with `torch.cat`;
  * no Python values in the captured region -- hence `pos` being a device
    tensor that the graph itself increments.

Usage:
    dec = GraphedDecoder(model, device="cuda", temperature=0.8, top_k=50)
    for tok in dec.stream(idx, max_new_tokens=200):
        ...
"""

from __future__ import annotations

import importlib.util
import sys

import torch

from .model import CornModel, set_decode_attention


def default_buckets(block_size: int) -> tuple[int, ...]:
    """Bucket bounds at multiples of 128, ending exactly at `block_size`.

    128 and not something finer: each bound is a captured graph (construction
    cost, a private memory pool) and the measured win is the *large* windows a
    short conversation never reaches -- attending 128 slots instead of 512 was
    +14% on the 260M shape, while 96 instead of 128 would be noise. One place
    computes this so `chat.py` and `agent.py` cannot drift apart on it.
    """
    return tuple(range(128, block_size, 128)) + (block_size,)


def ensure_recompile_room(shapes: int) -> int:
    """Let Dynamo hold `shapes` compiled step shapes, and twice that; return the limit.

    `compile_step` compiles `model.step` once per bucket bound (`dynamic=False`
    is deliberate), and Dynamo caps the compiled versions of one function at
    `recompile_limit` -- 8 out of the box. A 512 window has 4 buckets and a
    1024 window 8, so the cap was never met; **a 2048 window has 16**, and the
    ninth bucket hit `FailOnRecompileLimitHit` under `fullgraph=True`. The
    capture loop caught it as a broken toolchain and decoded the last eight
    buckets eagerly while the first eight kept their compiled graphs -- a
    mixed decoder whose card said `compile_step: false` (finding 160: 97 tok/s
    in fp32 deep in the window). Twice the bucket count, because `model.step`'s
    code object is shared by every decoder in the process and the grammar's
    processor path traces it again. Never lowered: another caller may need more.
    """
    import torch._dynamo.config as dynamo_config

    need = 2 * shapes
    if dynamo_config.recompile_limit < need:
        dynamo_config.recompile_limit = need
    return dynamo_config.recompile_limit


class StaticCache:
    """Preallocated K/V, sized to the longest sequence it will ever hold.

    `pos` is the slot the *next* token writes into, and it lives on the device
    so that a captured graph can increment it. Everything here is allocated
    once; nothing is reallocated per step.
    """

    def __init__(self, model: CornModel, device: str, dtype: torch.dtype,
                 batch: int = 1, slots: int | None = None) -> None:
        """`batch` > 1 reads several sequences in lockstep -- see `BatchedReader`.

        The default is 1 and every existing caller takes it, so the
        single-sequence path is byte-for-byte the one it was. What batching
        costs is stated where it is used: `pos` stays a *single* scalar shared
        by every row, so all of them must be at the same position, which means
        equal-length prompts. `mask()` keeps its broadcasting shape for the
        same reason.

        **`slots` is what a conversation and a worker do not have in common.**
        A conversation may run to `block_size` and cannot know when, so it
        allocates the whole window -- that is the default and it is what
        `GraphedDecoder` takes. A worker reading one window knows its exact
        length before it starts: `corn/extract.py` cuts to a fixed token count
        and `BatchedReader` is given the budget, so prompt plus budget is the
        most it can ever hold. At 20 layers x 1024 that is **40 MB per row for
        512 slots against ~11.5 MB for the 147 a worker uses**, and the cache
        is per *row*, so the difference is what decides how much of a page can
        be read in one batch. Attention still runs over every allocated slot
        (`CornModel.step`), so the smaller allocation is also less work.

        There is no correctness cliff here, only a loud one: `pos` past
        `slots` is an `index_copy_` out of bounds, not a wrong answer. Callers
        that cannot bound their length must leave this `None`.
        """
        cfg = model.cfg
        head_dim = cfg.n_embd // cfg.n_head
        self.slots = cfg.block_size if slots is None else min(slots, cfg.block_size)
        shape = (batch, cfg.n_head, self.slots, head_dim)
        self.batch = batch
        # The model's limit, which is not the allocation. `GraphedDecoder`
        # reads this to decide a conversation is out of room; nothing should
        # read it to decide how big the buffers are.
        self.block_size = cfg.block_size
        self.k = [torch.zeros(shape, device=device, dtype=dtype) for _ in range(cfg.n_layer)]
        self.v = [torch.zeros(shape, device=device, dtype=dtype) for _ in range(cfg.n_layer)]
        self.pos = torch.zeros(1, dtype=torch.long, device=device)
        self.arange = torch.arange(self.slots, device=device)

    def mask(self) -> torch.Tensor:
        """True where a slot holds a real key, including the one being written.

        Built from `pos` on the device rather than sliced by a Python int, so it
        is recomputed correctly on every graph replay.
        """
        return (self.arange <= self.pos).view(1, 1, 1, -1)

    def chunk(self, t: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Write slots and mask for appending `t` tokens at once.

        The mask is `(1, 1, t, slots)` and row `i` admits every slot up to and
        including `pos + i` -- the prefix already in the cache plus the part of
        this chunk at or before `i`. So the chunk is causal within itself and
        fully visible to the prefix, which is exactly what a prefill into a
        live cache means. Never captured: chunk length varies by construction,
        and prefill is one launch per call regardless of length, which is the
        argument `GraphedDecoder.prefill` already makes about graphs.
        """
        slots = self.pos + torch.arange(t, device=self.pos.device)
        mask = (self.arange.view(1, 1, 1, -1) <= slots.view(1, 1, -1, 1))
        return slots, mask

    def reset(self) -> None:
        self.pos.zero_()
        for k, v in zip(self.k, self.v):
            k.zero_()
            v.zero_()


class GraphedDecoder:
    """Single-sequence decoder over a `StaticCache`, sampling included.

    Sampling happens *inside* the captured region. It has to: a graph replay is
    one launch, and pulling logits out to sample them on the host would put a
    device-to-host sync in the middle of every token and give back most of what
    the graph just bought.

    Two of the three sampling knobs are free to change at any time and one is
    not. `temperature` is a device tensor the graph reads, so it can be turned
    mid-conversation. `top_k` is an argument to `torch.topk`, which means it is
    baked in at capture; changing it forces a recapture, as does crossing
    between sampling and greedy. Recapture costs milliseconds and resets the
    cache, so it belongs between turns rather than inside one.

    `use_graph=False` runs the identical static-cache path eagerly, which is
    what makes the graph's contribution separable from the static cache's, and
    is also the CPU fallback.

    `graph_sampling=False` is the third setting, and it exists for the rows that
    sample. Capture is all-or-nothing about *what is inside the region*, not
    about whether a graph is used at all: with it False the captured region ends
    at the logits and `_sample` runs eagerly outside, so the model's launches are
    still collapsed into one replay while no RNG is ever captured. That is worth
    having because the reason `corn.evals`' sampled rows gave up the graph was
    never the model -- it was `torch.multinomial` inside the captured region, and
    whether reseeding between replays means what it reads like. Nothing is being
    bet on that question here: the generator is untouched by capture.

    `graph_sampling=False` is also what makes a logits processor possible at
    all -- see `set_processor`, and `corn/grammar.py` for the one that uses it.

    Two consequences, both of them the point:

      * output is unchanged. Capture replays the kernels warmup selected, so the
        logits are the ones the eager path computes and the sampling that
        consumes them is the same eager call on the same generator. Measured
        byte-identical over 40 `variety` items at their per-item seeds, at 2.9x.
      * `set_sampling` stops forcing a recapture, since `top_k` is no longer
        baked into anything captured.
    """

    def __init__(
        self,
        model: CornModel,
        device: str = "cuda",
        dtype: torch.dtype | None = None,
        use_graph: bool = True,
        temperature: float = 0.8,
        top_k: int | None = 50,
        graph_sampling: bool = True,
        bucket_slots: tuple[int, ...] | None = None,
        compile_step: bool = False,
        attn: str = "sdpa",
    ) -> None:
        """`bucket_slots`, `compile_step` and `attn` are the decode-speed
        options, all off by default so the default construction is
        byte-for-byte the shipped path and everything `check_decode.py` has
        ever verified stays verified.

        **`bucket_slots`** answers `model.py`'s "attention runs over the full
        `block_size` window every step -- that is the price of static shapes".
        It is only the price of *one* static shape. A sliced view of a static
        buffer is itself a fixed-address static shape, so one graph per bucket
        boundary can attend over `k_buf[:, :, :bound]` instead of the whole
        window, and a conversation replays the smallest graph its position
        fits. No second allocation, no cache copying on promotion -- the
        buckets are views over the same storage, and promotion is replaying a
        different graph. Measured on the 260M shape: +14% while under 288
        slots. The last bucket must equal `block_size`, so behaviour at a full
        window is exactly the unbucketed path's.

        **`compile_step`** runs the step through Inductor for kernel fusion
        before capture. `mode="reduce-overhead"` is deliberately NOT used: its
        own cudagraphs refuse a step that mutates externally-owned cache
        buffers (`index_copy_`) and fall back to eager launches -- measured
        0.40x. Fusion without Inductor's graphs, captured into our own graph,
        measured +13% alone and +40% together with buckets. First-call
        compilation is slow (seconds to minutes per bucket shape, then cached
        on disk by Inductor); it belongs at construction, which is why it is a
        constructor flag and not a `set_`.

        Fused kernels are *different* kernels, so `compile_step` output is not
        guaranteed bit-identical to eager -- `check_decode.py` measures whether
        greedy parity survives it on a real checkpoint rather than assuming
        either way.

        **`attn="manual"` is the one option here that is not output-neutral,
        and it is also the largest single win.** See `CausalSelfAttention.step`
        for the measurement: the explicit matmul form is 2.2x faster than the
        masked SDPA call at decode shape and exactly as accurate, but it rounds
        differently, so greedy output can diverge where the top-two logits sit
        within ~1% of scale. It sets the mode on the *model*, which every
        decoder over that model then shares -- so a caller wanting both
        formulations at once needs two models, and a caller producing a
        scorecard must leave it alone.
        """
        self.model = model.eval()
        if attn != "sdpa":
            set_decode_attention(model, attn)
        self.device = device
        self.dtype = dtype or next(model.parameters()).dtype
        self.cache = StaticCache(model, device, self.dtype)
        self.token = torch.zeros(1, 1, dtype=torch.long, device=device)
        # The structural mask's two device tensors (PLAN-TAG-SPINE §4), read
        # by `_forward_body` on every step and captured with it. Zero means
        # off, and off is the shipped mask exactly. See `set_structure`.
        self.slot_part = torch.zeros(self.cache.slots, dtype=torch.long, device=device)
        self.focus = torch.zeros(1, dtype=torch.long, device=device)
        self._structure: tuple[int, int | None, int | None] | None = None
        self._prompt_open_call = False
        self._temperature = torch.tensor([1.0], device=device, dtype=torch.float32)
        self._greedy = True
        self._top_k: int | None = None
        self._set_sampling_values(temperature, top_k)
        self.use_graph = use_graph and device.startswith("cuda")
        self.graph_sampling = graph_sampling

        if bucket_slots is not None:
            bounds = sorted(set(bucket_slots))
            if not bounds or bounds[-1] != self.cache.slots:
                raise ValueError(
                    f"last bucket must equal the cache's {self.cache.slots} slots, "
                    f"got {bounds}")
            if bounds[0] <= 0:
                raise ValueError(f"bucket bounds must be positive, got {bounds}")
            self._bounds = bounds
        else:
            self._bounds = [self.cache.slots]

        self._step_fn = model.step
        # `compiled` is what actually happened, which a scorecard's `instance`
        # reads (`Agent.compile_step`); `compile_step` is what was asked for.
        # The two differ on a machine without Inductor's backend, where the
        # default-on path degrades to the eager step with one line on stderr
        # rather than a traceback on the first turn -- a friend's Windows
        # install without `triton-windows` is the case this exists for.
        self.compiled = False
        if compile_step:
            if importlib.util.find_spec("triton") is None:
                print("decode: torch.compile needs triton, which is not "
                      "installed -- decoding eagerly instead (pip install "
                      "triton-windows on Windows; see requirements.txt)",
                      file=sys.stderr)
            else:
                ensure_recompile_room(len(self._bounds))
                self._step_fn = torch.compile(
                    model.step, fullgraph=True,
                    mode="max-autotune-no-cudagraphs", dynamic=False,
                )
                self.compiled = True

        # One graph per bucket, in bound order; `_graph_i` indexes the one the
        # current position fits. `_pos_h` mirrors `cache.pos` on the host so
        # bucket promotion never costs a device sync -- it is maintained by
        # `prefill`/`step` and nothing else moves the cache.
        self.graph: torch.cuda.CUDAGraph | None = None  # kept: the single-bucket alias
        self._graphs: list[torch.cuda.CUDAGraph] = []
        self._graph_logits: list[torch.Tensor | None] = []
        self._graph_i = 0
        self._pos_h = 0
        # The token ids whose KV currently occupies slots [0, pos) -- the
        # prompt plus every token `step` has written since. `prefill(reuse=True)`
        # compares against this to decide how much it can keep. Maintained on
        # the host from ids the caller already has, never by reading the device:
        # an `.item()` per step to keep a list current would cost more than the
        # reuse saves.
        self._cached_ids: list[int] = []
        # The captured region's output when sampling is left outside it. Written
        # once by capture and read after every replay; never reallocated, which
        # is the whole reason a replay needs no arguments.
        self._logits: torch.Tensor | None = None
        # A per-step logits hook, applied outside the graph. See `set_processor`.
        self._processor = None
        if self.use_graph:
            self._capture()

    # --- sampling -----------------------------------------------------------

    def _set_sampling_values(self, temperature: float | None, top_k: int | None) -> bool:
        """Apply new settings; return whether they require a recapture."""
        recapture = False
        if temperature is not None:
            greedy = temperature <= 0.0
            recapture |= greedy != self._greedy
            self._greedy = greedy
            self._temperature.fill_(max(temperature, 1e-6))
        if top_k is not None:
            k = min(top_k, self.model.vocab_size) if top_k > 0 else None
            recapture |= k != self._top_k
            self._top_k = k
        return recapture

    def set_sampling(self, temperature: float | None = None, top_k: int | None = None) -> None:
        """Change sampling. Recaptures if it has to, which clears the cache.

        Never has to when `graph_sampling` is False: what would need recapturing
        is `torch.topk`'s baked-in `k`, and under that setting `topk` is not in
        the graph at all.
        """
        recapture = self._set_sampling_values(temperature, top_k)
        if recapture and self.use_graph and self.graph_sampling:
            self._capture()

    def set_processor(self, processor) -> None:
        """Install a per-step logits hook -- `processor(last_logits) -> logits`.

        It runs on the host, between the model and the sampler, and it is
        allowed to depend on every token emitted so far. That is exactly what a
        captured region cannot contain: a graph replay is one launch with no
        Python in it, so a mask whose contents change with the parse state has
        nowhere to be computed. Hence the requirement rather than a silent
        fallback -- `graph_sampling=False` already exists for the rows that
        sample, and it keeps the model's launches collapsed while leaving
        everything after the logits eager.

        `None` removes it. The model is untouched either way; nothing here
        changes what the forward pass computes.
        """
        if processor is not None and self.use_graph and self.graph_sampling:
            raise ValueError(
                "a logits processor cannot run inside the captured region -- "
                "construct the decoder with graph_sampling=False"
            )
        self._processor = processor

    def _sample(self, logits: torch.Tensor) -> torch.Tensor:
        last = logits[:, -1, :]
        if self._processor is not None:
            last = self._processor(last)
        if self._greedy:
            return last.argmax(dim=-1, keepdim=True)
        # Softmax in fp32 regardless of the model's dtype -- the distribution is
        # cheap at any vocab size and half-precision softmax is not worth the
        # tail behaviour.
        x = last.float() / self._temperature
        if self._top_k:
            # Slice `[:, -1:]`, never `[:, [-1]]`: fancy indexing builds a CPU
            # index tensor, and the implied host-to-device copy is illegal
            # during capture.
            thresh = torch.topk(x, self._top_k, dim=-1).values[:, -1:]
            x = x.masked_fill(x < thresh, float("-inf"))
        return torch.multinomial(torch.softmax(x, dim=-1), num_samples=1)

    @torch.no_grad()
    def _forward_body(self, bound: int | None = None) -> torch.Tensor:
        """Embed, one token through every layer, advance the write slot.

        Everything the model does and nothing the sampler does, so that the two
        can be captured together or the model captured alone. No RNG in here.

        `bound` attends over the first `bound` slots only, via views -- same
        storage, fixed addresses, so the body stays capturable. `None` is the
        full window and is byte-for-byte the original body.
        """
        if bound is None or bound == self.cache.slots:
            k, v = self.cache.k, self.cache.v
            mask = self.cache.mask()
            part = self.slot_part
        else:
            k = [t[:, :, :bound] for t in self.cache.k]
            v = [t[:, :, :bound] for t in self.cache.v]
            mask = (self.cache.arange[:bound] <= self.cache.pos).view(1, 1, 1, -1)
            part = self.slot_part[:bound]
        # The structural mask at decode (PLAN-TAG-SPINE §4): while `focus` is
        # non-zero -- a call line is being written -- the request slots of
        # every other part are hidden. With `focus` at zero this is the base
        # mask exactly, so the shipped decode is the same booleans it always
        # was; and both tensors live on the device, so a captured graph reads
        # their current values on every replay.
        mask = mask & ~((self.focus > 0) & (part > 0) & (part != self.focus)).view(1, 1, 1, -1)
        logits = self._step_fn(self.token, k, v, self.cache.pos, mask)
        self.cache.pos.add_(1)
        return logits

    @torch.no_grad()
    def _step_body(self, bound: int | None = None) -> None:
        """The whole step, sampling included.

        Writes its result back into `self.token` so a replay needs no arguments
        and produces no host traffic at all.
        """
        self.token.copy_(self._sample(self._forward_body(bound)))

    @torch.no_grad()
    def _capture(self) -> None:
        self._graphs = []
        self._graph_logits = []
        for bound in self._bounds:

            def body():
                if self.graph_sampling:
                    self._step_body(bound)
                    return None
                return self._forward_body(bound)

            # Compilation (when on) must happen before the side-stream warmup:
            # the first call per shape runs Inductor, and capturing or
            # stream-juggling around a compiling function is asking for it.
            self.cache.pos.zero_()
            try:
                body()
            except Exception as exc:  # noqa: BLE001 -- Inductor raises many
                if not self.compiled:
                    raise
                # Inductor was present but could not build the step -- no
                # C++ toolchain, a triton that does not match this torch, a
                # GPU it will not target. The eager step computes the same
                # logits (`check_decode.py`, 96/96), so the turn goes on and
                # the card says `compile_step: false`.
                print(f"decode: torch.compile failed ({type(exc).__name__}: "
                      f"{str(exc).splitlines()[0][:120]}) -- decoding "
                      f"eagerly instead", file=sys.stderr)
                self._step_fn = self.model.step
                self.compiled = False
                self.cache.pos.zero_()
                body()

            # Warm up on a side stream: the first few calls allocate
            # workspaces and pick kernels, and capturing that would bake
            # one-time setup into every replay.
            side = torch.cuda.Stream()
            side.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(side):
                for _ in range(3):
                    body()
            torch.cuda.current_stream().wait_stream(side)
            torch.cuda.synchronize()

            graph = torch.cuda.CUDAGraph()
            self.cache.pos.zero_()  # capture well inside the bucket's bound
            with torch.cuda.graph(graph):
                out = body()
            self._graphs.append(graph)
            # The graph's own output tensor, in its private pool at a fixed
            # address. Every replay overwrites it in place, which is what makes
            # reading it after `replay()` the same thing as reading what the
            # step computed.
            self._graph_logits.append(out)

        # The single-bucket names the rest of this file (and one check) read.
        self.graph = self._graphs[-1]
        self._logits = self._graph_logits[-1]
        self._graph_i = 0
        self._pos_h = 0

        # Warmup and capture both advanced the cache. Callers get a clean one.
        self.cache.reset()

    def _promote(self) -> int:
        """Index of the bucket the next write slot fits. Host arithmetic only."""
        while self._pos_h >= self._bounds[self._graph_i]:
            self._graph_i += 1
        return self._graph_i

    def set_structure(self, part_ids: list[int] | None, next_focus: int = 0,
                      call_id: int | None = None, newline_id: int | None = None,
                      open_call: bool = False) -> None:
        """Arm the structural mask for the next `stream` (PLAN-TAG-SPINE §4).

        `part_ids` is the prompt's part stream, one id per prompt token, laid
        into the cache's slots; `next_focus` is the leaf the next call line
        executes. The focus is *not* applied from the first generated token:
        a line that turns out to be a say or a parse sees everything, as it
        did in training. `stream` raises the focus when the first token it
        commits is `call_id` and drops it at `newline_id`. `None` disarms.
        """
        self.slot_part.zero_()
        self.focus.zero_()
        self._structure = None
        self._prompt_open_call = False
        if part_ids is None:
            return
        n = min(len(part_ids), self.cache.slots)
        self.slot_part[:n] = torch.tensor(part_ids[:n], dtype=torch.long,
                                          device=self.slot_part.device)
        self._structure = (int(next_focus), call_id, newline_id)
        self._prompt_open_call = bool(open_call)

    @torch.no_grad()
    def prefill(self, idx: torch.Tensor, reuse: bool = False,
                tags: torch.Tensor | None = None,
                attn_mask: torch.Tensor | None = None) -> int:
        """Run the prompt through the normal forward path, then adopt its cache.

        **`tags` is the per-token map of PLAN-LOOP §4**, same shape as `idx`,
        and it takes the full path: a map changes the embeddings of the
        prefix, so the KV a `reuse` would keep is the KV of a different
        prefix. Generated tokens are never tagged, so `step` and the graph
        it is captured into know nothing about it.

        Prefill is one big batched call either way, so there is nothing for a
        graph to save here -- the launch overhead this module exists to remove
        is per *token*, and prefill is one step regardless of length.

        **`reuse=True` keeps the KV of whatever prefix this prompt shares with
        the last one and encodes only the rest.** A turn is not one generation:
        `corn/agent.py` runs a round per tool call plus one for the reply, and
        each round's prompt is the previous round's prompt plus what that round
        produced -- so the default path re-encodes, from token zero, tokens
        whose KV it discarded moments earlier. Measured over 300 real
        single-call turns that is **42.1% of a turn's prefill**, and the
        151-token tool declaration sits at the front of every round of every
        turn (`scripts/prefill_redundancy.py`).

        It is exact rather than approximate, and `wpe` is the reason. Learned
        absolute positions mean position `i`'s K and V depend on position `i`
        and the tokens before it and on nothing after, so the KV of an
        unchanged prefix is bit-identical to the KV that would be recomputed.
        (The same property is what forbids left-padding in `BatchedReader`; it
        pays here.)

        The caller does not have to know whether a prefix matched. This
        compares against the ids it last held and does the right thing either
        way, which is what keeps `reuse` from becoming a correctness question
        the caller can get wrong -- a *wrong* prefix would be fluent, not loud.
        """
        if idx.size(0) != 1:
            raise ValueError("GraphedDecoder is single-sequence")
        t = idx.size(1)
        if t >= self.cache.block_size:
            raise ValueError(f"prompt of {t} fills block_size {self.cache.block_size}")

        ids = idx[0].tolist()
        shared = 0
        if reuse and self._cached_ids and tags is None and attn_mask is None:
            limit = min(len(self._cached_ids), t - 1)  # never reuse the whole
            while shared < limit and self._cached_ids[shared] == ids[shared]:
                shared += 1

        if shared == 0:
            logits, _, caches = self.model(idx, tags=tags, attn_mask=attn_mask)
            for i, (k, v) in enumerate(caches):
                self.cache.k[i][:, :, :t].copy_(k)
                self.cache.v[i][:, :, :t].copy_(v)
                # Slots past the prompt can hold values from a previous
                # sequence. The mask excludes them, but zeroing keeps a stale
                # run from ever looking like a live one if the mask is wrong.
                self.cache.k[i][:, :, t:].zero_()
                self.cache.v[i][:, :, t:].zero_()
            self.cache.pos.fill_(t)
        else:
            # The kept prefix is already in slots [0, shared). Append the rest
            # as one chunk against it -- `CornModel.step` takes T tokens when
            # `pos` and `mask` describe T of them.
            self.cache.pos.fill_(shared)
            tail = idx[:, shared:]
            slots, mask = self.cache.chunk(tail.size(1))
            logits = self.model.step(tail, self.cache.k, self.cache.v, slots, mask)
            self.cache.pos.fill_(t)

        self._cached_ids = ids
        self._pos_h = t
        self._graph_i = 0
        self.token.copy_(self._sample(logits))
        return int(self.token.item())

    @torch.no_grad()
    def step(self) -> None:
        """Advance one token. Does not synchronise and does not read back."""
        if not self.use_graph:
            self._step_body()
        elif self.graph_sampling:
            self._graphs[self._promote()].replay()
        else:
            i = self._promote()
            self._graphs[i].replay()
            self.token.copy_(self._sample(self._graph_logits[i]))
        self._pos_h += 1

    def last_token(self) -> int:
        """The token `step` produced. This is a device-to-host sync -- a real
        streaming loop pays it once per token, so benchmarks should say whether
        they included it."""
        return int(self.token.item())

    @property
    def full(self) -> bool:
        return int(self.cache.pos.item()) >= self.cache.block_size

    @torch.no_grad()
    def stream(self, idx: torch.Tensor, max_new_tokens: int, reuse: bool = False,
               tags: torch.Tensor | None = None,
               attn_mask: torch.Tensor | None = None):
        """Prefill `idx`, then yield token ids one at a time until the context
        window fills. Starts a fresh sequence; nothing carries over.

        A processor is told every id as it is committed, here rather than in
        `_sample`, because reading one out costs a device-to-host sync and this
        loop has already paid it in `last_token`.

        **`reuse=True` keeps the cache across calls** -- see `prefill`. The
        zeroing that `reset` does is what it gives up, so the two are exclusive
        by construction rather than by a caller remembering: with reuse on, a
        slot past the prompt still holds a previous sequence's value and the
        mask is the only thing excluding it, which is the arrangement `prefill`
        already relies on for the tail of an ordinary prompt.

        The generated ids are appended to `_cached_ids` as they are committed,
        because the next round's prompt contains them: a turn's second
        generation asks the model to continue past the call the first one
        wrote, and that call is in the cache already.
        """
        if not reuse:
            self.cache.reset()
            self._cached_ids = []
        if self._processor is not None:
            self._processor.reset()
        tok = self.prefill(idx, reuse=reuse, tags=tags, attn_mask=attn_mask)
        if self._processor is not None:
            self._processor.accept(tok)
        self._focus_on(tok, first=True)
        yield tok
        for _ in range(max_new_tokens - 1):
            if self.full:
                return
            # `step` writes the KV of the token yielded last, so that is the
            # moment it joins what the cache holds.
            self.step()
            self._cached_ids.append(tok)
            tok = self.last_token()
            if self._processor is not None:
                self._processor.accept(tok)
            self._focus_on(tok, first=False)
            yield tok

    def _focus_on(self, tok: int, first: bool) -> None:
        """Raise the focus when a call line opens, drop it when a line ends."""
        if self._structure is None:
            return
        next_focus, call_id, newline_id = self._structure
        if tok == call_id:
            self.focus.fill_(next_focus)
        elif tok == newline_id:
            self.focus.zero_()
        elif first and self._prompt_open_call:
            # The prompt itself ended inside a call line (the move rows end at
            # `<|call|>`): the first generated token is already in it.
            self.focus.fill_(next_focus)

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int,
                 reuse: bool = False) -> list[int]:
        """The new tokens only -- the prompt is not echoed back."""
        return list(self.stream(idx, max_new_tokens, reuse=reuse))


class BatchedReader:
    """N equal-length prompts read in lockstep, for the worker role.

    **Why this is not `GraphedDecoder` with a batch argument.** That class is
    built around three things this one does not want: a captured CUDA graph, a
    logits processor that holds parse state for *one* sequence, and streaming a
    token at a time to a client. The worker role is the opposite of all three --
    it reads a window, writes a short answer nobody streams, and there are
    eight of it. Bolting a batch dimension onto the interactive decoder would
    put those two sets of constraints in one object and the single-sequence path
    is what every turn in this project depends on.

    **Equal-length prompts, and the reason is `pos`.** `StaticCache.pos` is one
    scalar shared by every row, so all rows sit at the same slot and advance
    together. `corn/model.py` uses learned absolute positions (`wpe`), so
    left-padding would shift real tokens onto wrong positions and is not
    available; right-padding is correct for prefill and then leaves each row at
    a different position, which this cache cannot express. Chunking by *token
    count* rather than by sentence sidesteps it entirely, and that is the
    intended caller.

    A `ValueError` rather than a silent pad, because a quietly padded batch
    produces fluent wrong answers -- the failure mode `check_decode.py` exists
    for.

    **No graph capture, deliberately.** Capture is shape-static, so a variable
    batch means bucketing to fixed sizes or capturing per size, and the measured
    numbers do not need it: eight windows of 96 tokens with 24 new tokens each
    cost ~250 ms on the eager path against a 500 ms budget, and the cost is
    nearly flat in N because decode at this size is memory-bandwidth-bound. If
    that stops being true, capture is the next thing to add and this docstring
    is the record of why it was not needed first.
    """

    def __init__(self, model: CornModel, device: str = "cuda",
                 dtype: torch.dtype | None = None,
                 temperature: float = 0.0, top_k: int = 0) -> None:
        self.model = model.eval()
        self.device = device
        self.dtype = dtype or next(model.parameters()).dtype
        self.temperature = temperature
        self.top_k = top_k

    def _sample(self, logits: torch.Tensor,
                ban: tuple[int, ...] | list[int] = ()) -> torch.Tensor:
        """`(B, T, V)` -> `(B, 1)`. Greedy at temperature 0, as elsewhere.

        `ban` removes token ids from consideration for this step only, before
        either sampling path sees them -- so a banned id cannot be reached by
        argmax or drawn by `multinomial`, and the ban costs nothing when it is
        empty. `read` uses it for one step; see `ban_first` there.
        """
        last = logits[:, -1, :]
        if ban:
            last = last.clone()
            last[:, list(ban)] = float("-inf")
        if self.temperature <= 0.0:
            return last.argmax(dim=-1, keepdim=True)
        x = last.float() / self.temperature
        if self.top_k:
            thresh = torch.topk(x, self.top_k, dim=-1).values[:, -1:]
            x = x.masked_fill(x < thresh, float("-inf"))
        return torch.multinomial(torch.softmax(x, dim=-1), num_samples=1)

    @torch.no_grad()
    def read(self, idx: torch.Tensor, max_new_tokens: int,
             cache_slots: int | None = None,
             ban_first: tuple[int, ...] | list[int] = ()) -> list[list[int]]:
        """One list of new tokens per row of `idx`. The prompt is not echoed.

        Runs the full budget for every row rather than stopping early. Rows
        finish at different points and they decode in lockstep, so an early exit
        would have to wait for the slowest one anyway; the only thing it could
        save is decoding text on the host every step to look for a marker, which
        is a device-to-host sync per token to avoid work that is nearly free.
        The caller cuts at whatever marker it owns.

        **`ban_first` is masked at step 0 and at no other step**, which is the
        whole of the forcing half of `corn/gate.py`'s policy. The decline pool's
        first token is question-independent (`gate.decline_heads` raises if that
        stops being true), so removing those ids at the fork makes a decline
        unreachable and leaves every later step exactly as it was -- the reply
        is not steered, only its opening is denied one branch. Empty by default,
        and with it empty this method is byte-for-byte what it always was.
        """
        if idx.dim() != 2:
            raise ValueError(f"expected (batch, tokens), got {tuple(idx.shape)}")
        b, t = idx.shape
        if t >= self.model.cfg.block_size:
            raise ValueError(
                f"prompt of {t} fills block_size {self.model.cfg.block_size}")
        if t + max_new_tokens > self.model.cfg.block_size:
            raise ValueError(
                f"{t} prompt + {max_new_tokens} new exceeds block_size "
                f"{self.model.cfg.block_size}")

        # Exactly what this read can hold and not one slot more. `pos` starts
        # at `t` and the loop below writes at `t` through `t + max_new - 2`,
        # so the bound is the same one the guards above already check --
        # keeping it identical means there is one length to reason about
        # rather than two that must agree.
        #
        # `cache_slots` is a **test seam**, in the same sense as `--stop-at` in
        # `corn/train.py`: a wrong size here does not crash, it changes which
        # keys the mask admits, and the reply stays fluent. The only way to see
        # that is to run the same batch against a full-window cache and require
        # the two to agree, which is what `scripts/check_decode.py` does with
        # it. Nothing in the runtime passes it.
        cache = StaticCache(self.model, self.device, self.dtype, batch=b,
                            slots=cache_slots or t + max_new_tokens)
        logits, _, caches = self.model(idx)
        for i, (k, v) in enumerate(caches):
            cache.k[i][:, :, :t].copy_(k)
            cache.v[i][:, :, :t].copy_(v)
            # Slots past the prompt can hold values from a previous read. The
            # mask excludes them; zeroing means a stale row can never look live
            # if the mask is ever wrong. `StaticCache` makes this redundant on a
            # fresh allocation and it is kept for the same reason `prefill`
            # keeps it.
            cache.k[i][:, :, t:].zero_()
            cache.v[i][:, :, t:].zero_()
        cache.pos.fill_(t)

        token = self._sample(logits, ban_first)
        out = [token]
        for _ in range(max_new_tokens - 1):
            logits = self.model.step(
                token, cache.k, cache.v, cache.pos, cache.mask())
            cache.pos.add_(1)
            token = self._sample(logits)
            out.append(token)
        return torch.cat(out, dim=1).tolist()
