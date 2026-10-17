# Second finding — the extrapolation, measured

The above was a projection from two small models. Decode speed doesn't depend on the weights
being any good, so it didn't have to stay one: `bench.py --config` now builds an untrained
architecture and times it. Seven shapes, head dim held at 64, block 512, ~250M for the
middle five.

**The launch-overhead diagnosis is confirmed, harder than expected.** Eager per-token cost
divided by layer count, across a 54x parameter range and both dtypes:

| | 6L×256 | 8L×512 | 12L×1280 | 16L×1152 | 20L×1024 | 24L×960 | 32L×832 |
|---|---|---|---|---|---|---|---|
| params | 4.9M | 25.6M | 237M | 256M | 252M | 266M | 267M |
| fp32 ms/layer | 0.485 | 0.474 | 0.462 | 0.456 | 0.449 | 0.446 | 0.450 |
| bf16 ms/layer | 0.487 | 0.478 | 0.479 | 0.456 | 0.455 | 0.454 | 0.456 |

Flat to within ±4% over 54x the parameters, and **bf16 is not one bit faster than fp32** —
halving the bytes moved changes nothing. Eager decode on this box is a fixed ~0.46ms per
layer of CPU-side launch cost with the GPU idle underneath it. The predicted 85–125 tok/s
for 16–24 layers came in at 93–137. The projection was right.

**CUDA graphs remove most of it.** Capturing the whole decode step into one launch
(`corn/decode.py`), bf16:

| shape | params | eager | graphed | speedup |
|---|---|---|---|---|
| 12L×1280 | 237M | 174 tok/s | **554 tok/s** | 3.2x |
| 16L×1152 | 256M | 137 tok/s | **459 tok/s** | 3.3x |
| 20L×1024 | 252M | 110 tok/s | **424 tok/s** | 3.9x |
| 24L×960 | 266M | 92 tok/s | **366 tok/s** | 4.0x |
| 32L×832 | 267M | 69 tok/s | **287 tok/s** | 4.2x |

**Every 250M shape tested clears the 250 tok/s target once decode is graphed. None of them
clear it eagerly.** That is the finding: the §3 latency budget at 250M is not an architecture
problem, it's an inference-engine problem, and it's already solved.

Three second-order results worth keeping:

- **Depth is now an optimization, not a constraint.** 12 layers still beats 32 by 1.9x, so
  "wide and shallow" survives — but as a preference, not as the line between viable and not.
  Architecture choice (VISION §10) is freed from the latency argument.
- **Dtype starts mattering only after the graph.** Eager, fp32 and bf16 are identical; graphed,
  bf16 is ~1.8x faster than fp32. The model moved from launch-bound into the regime §4 assumed
  it was in all along. Quantization becomes worth considering exactly here and not before.
- **§4's ~1500 tok/s bandwidth estimate is optimistic by ~3x.** Best measured 250M is 554 tok/s
  (0.5GB of weights at 760 GB/s should permit ~1500). Real headroom is ~2x over target, not 6x.

The static KV cache alone accounts for none of this — it measures *slower* than `torch.cat`
(101 vs 137 tok/s at 16L), because static shapes mean attending over the full 512-slot window
every step. It exists only because graph capture requires it. Streaming readback of one token
per step costs ~4%, so the numbers above survive contact with a real consumer.

Not tested: `torch.compile`, which needs Triton, which has no working install on this machine.
CUDA graphs turned out to be the more direct instrument anyway — same kernels, only fewer
launches, so the mechanism isn't in question.

### It is the default path now, sampling included

`chat.py` and `sample.py` decode through the graph. Sampling runs *inside* the captured
region — top-k and multinomial and all — because a graph replay is one launch, and lifting
logits out to sample them on the host would reintroduce a device sync per token and give most
of the win straight back.

That constrains the knobs, and the constraint is worth knowing before it surprises someone:

- **`temperature` is free to change.** The graph reads it from a device tensor, so `/temp`
  takes effect on the next token.
- **`top_k` is not.** It's an argument to `torch.topk` and gets baked in at capture, so
  changing it (or crossing between sampling and greedy) forces a recapture. That costs
  milliseconds and resets the cache, which is why it belongs between turns.

Measured cost of sampling in-graph: **4.9% at 237M, 4.0% at 252M** (7% at nano, where the
model step is small enough for a 256-way top-k to be noticeable). So the honest end-to-end
number for a 250M model — graphed, bf16, sampling, one token pulled to the host per step —
is **406–525 tok/s**, still comfortably past the 250 target.

`nano` in `chat.py` went from ~330 to ~950 tok/s.

**Capture fails quietly**, which is the real hazard: a stale buffer or a Python value baked
into the graph produces fluent, plausible, *wrong* text, and an RNG that doesn't advance on
replay emits the same token forever. Neither shows up in a latency measurement, so
`scripts/check_decode.py` checks greedy output against the pre-static-cache path token for
token, and checks that sampled replays actually draw fresh randomness.
