# Five times the parameters costs only a third of the decode speed

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Corn-Nano-0: 4.9M params, 65M tokens, val **0.6104 nats/byte** (0.88 bits/byte), ~17 min.

The bench turned up something that bears on VISION.md §4, which estimates ~1500 tok/s for
250M from a memory-bandwidth argument and concludes inference speed is not at risk:

| config | params | decode |
|---|---|---|
| `nano` (6 layers) | 4.9M | 331 tok/s — 3.02 ms/tok |
| `nano20m` (8 layers) | 25.5M | 250 tok/s — 3.99 ms/tok |

**5x the parameters costs 32% of the speed.** Cost tracks *layer count*, at a flat ~0.5ms per
layer, not parameter count — so in eager PyTorch decode is bound by per-layer kernel launch
overhead, not by bandwidth. The bandwidth ceiling is real but nowhere near binding yet.

The consequence: a 250M model at 16–24 layers extrapolates to ~8–12 ms/token, or **85–125
tok/s — under the 250 tok/s target**, unless per-token overhead is removed. That makes CUDA
graphs / `torch.compile` / a fused decode path the lever that matters, and quantization
roughly irrelevant. §4's headroom is available but not free.

This is exactly the trade `bench.py` exists to catch, and it argues for keeping layer count
down and width up when the 250M architecture gets chosen.
