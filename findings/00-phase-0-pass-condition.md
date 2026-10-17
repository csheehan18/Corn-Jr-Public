# Phase 0 pass condition — met

**Cost:** 2.3 min of scoring on the 1 card first cited here (`nano20m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`configs/nano20m.py` had to train to completion with **no code changes** — only a different
file in `configs/`. Until that held, scaling to the real 250M run was a rewrite waiting to
happen.

It holds. `nano20m` trained end to end in **27.9 minutes** with nothing in `corn/` touched;
the only edit was the config's `data_dir`. 25.6M params, 12,000 iters × 24,576 tokens = 295M
tokens, best val **0.4265 nats/byte** at iter 11,500, and the checkpoint generates recognisable
English:

> Once upon a time, there was a sleepy cat named Tom. Tom liked to collect rocks…
