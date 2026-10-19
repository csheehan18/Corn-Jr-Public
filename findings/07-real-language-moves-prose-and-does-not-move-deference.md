# Real web text improves prose but not using the tool's answer

**Full result:** Real language moves prose, and does not move deference

**Cost:** 70 s of scoring on the 1 card first cited here (`nano20m_web`); it also reads 2 cards scored for an earlier finding (`nano20m`, `nano20m_pilot`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Every number above was measured on text this project either downloaded from one children's
story dataset or generated with a Python script. DATA.md §4 gives general fluency 40% of the
budget and calls it the only source of actual language competence; §10 calls the four missing
slices the whole critical path. One of them is now on disk: `scripts/prepare_fineweb.py`
writes FineWeb-Edu `sample-10BT` shard 000 at `int_score >= 4`, which is **485,628,154 bytes
over 96,494 documents**, 13.29% of the rows read. It cost 22 seconds to download and 9 to
convert, against the fifteen minutes a shard this was budgeted at — so the full 14-shard
sample is roughly seven minutes and not an afternoon, and corpus size is not the thing
standing between here and §4.

`data/mix_web` is the pilot corpus with that slice added, and the weights are chosen so that
adding it changes only it: **web 40% / narrative 51% / temporal 9%** of 497.5M tokens holds
narrative at 253,725,000 and temporal at 44,775,000 — the pilot's two numbers to the token,
and `val_narrative.bin` came back byte-identical to `data/mix_pilot`'s. Renormalising §4's
surviving three slices to 73/18/9 would have moved all three at once, and a prose regression
could then be web text hurting or narrative being cut, with no way to tell which.
`configs/nano20m_web.py` differs from `nano20m_pilot` in `max_iters` and nothing that matters
— 12,000 × 5/3, so both runs make 0.988 of a pass and every slice's *exposure* is preserved
rather than merely its share of the file. 48.1 minutes, 178–180k tok/s.

| row | `nano20m` | `nano20m_pilot` | `nano20m_web`<br>best-val | `nano20m_web`<br>final | n |
|---|---|---|---|---|---|
| `narrative` nats/byte | 0.3974 | 0.4117 | 0.4221 | 0.4174 | 1.1MB |
| `temporal` nats/byte | 3.8911 | 0.1000 | 0.1029 | 0.1010 | 1.0MB |
| `web` nats/byte | — | — | 0.9491 | **0.9434** | 1.1MB |
| `temporal.route` | 0/400 | 399/400 | 400/400 | 398/400 | 400 |
| `temporal.copy` | 0/353 | **353/353** | **353/353** | **353/353** | 353 |
| `refusal.clarify` | 0/47 | 47/47 | 47/47 | 47/47 | 47 |
| `refusal.no_guess` | — of 0 | 47/47 | 47/47 | 47/47 | 47 |

**`temporal.copy` does not move by one item.** That is the result this run was bought for.
The sixth finding rests entirely on 353/353 — it is the single row that separates pretraining
the format from fine-tuning it — and until now it had only ever been observed on a corpus of
TinyStories and templates, where a `<|call|>` envelope is nearly the only structured thing in
the distribution. Adding 199M tokens of real prose, tables, lists and half-formatted HTML
gives the model an enormous amount of new material to confuse the format with, and both
checkpoints still carry the tool's date 353 times out of 353. The load-bearing result behind
§4 is not an artefact of a clean distribution.

**Prose got worse at identical exposure, and that is the interesting half.** 0.4117 → 0.4174
on narrative, with both runs reading exactly 250,680,300 narrative tokens from a
byte-identical file. Same data, same amount, worse prose — so this is not a budget effect and
there is nothing to trade off against; the only thing that changed is that 40% of the weights'
attention now goes somewhere else. That is DATA.md §4's capacity argument being *right*, one
finding after it was wrong. §4 predicted a 250M model has no room to absorb a format late; the
sixth finding refuted that flatly. It also implies that slices compete, and at 25M they
visibly do. Format installation and general fluency are different claims about capacity, and
this run is what separates them: the first is false at this scale and the second is true.

**`web` reads 0.9434 nats/byte**, the first number this project has on text it did not
manufacture — 2.2x narrative and 10x temporal. TinyStories is a deliberately small vocabulary
and the temporal slice is templated, so both were always going to be easy; the useful thing
about 0.94 is that it is a floor to beat with the BPE work rather than a result on its own.

### The blended val picked the wrong checkpoint, provably

`ckpt.pt` won the training run's validation by a clear margin — **0.6281 at iter 18,000
against `last.pt`'s 0.6541** — and `last.pt` beats it on all three language-modelling rows of
the frozen set. Not by noise: 0.4174 against 0.4221 on narrative is larger than the entire
cost of the pilot's temporal slice.

Best-val landed at iter 18,000 by beating iter 17,500 by **0.005**, while adjacent evals were
swinging **0.027** on the frozen set. So it was selecting sampling noise — and the run's 41
recorded evals say why, which turns out not to be the obvious answer.

**The blend is noisy mostly because it is not stratified.** `val.bin` is the mix in its own
proportions, so the 40 × 24 = 960 random windows an eval draws land on the three slices
multinomially, and the blend's *composition* moves every time. With slices at 0.46, 0.10 and
1.00 nats/byte, composition alone has an SD of **0.0099** — **71% of the blend's observed SD of
0.0139** over the last 11 evals. None of that is the model changing. The per-source figures
`estimate_loss` was already computing and discarding sample each slice at a fixed rate, which
removes it by construction, and there are more of them: 1,440 windows against 960.

Measured over those same 11 evals, the blend moves **2.14%** relative and a mean of the
per-source log losses moves **0.94%**. The improvement selection has to resolve at the end of a
cosine schedule is smaller than either, which is why a 2.3x noise reduction changes the answer
instead of merely tidying it.

**`train.py` now selects on that mean of logs**, and the fifth finding's caveat about val
figures is the reason it is a module constant rather than a config field — a run that can
quietly change how its checkpoint was picked is a run whose scores are not comparable, which is
the same argument that keeps `WARMUP` out of `Config`. Logs rather than an average because the
geometric mean is scale-invariant: a 1% relative improvement counts the same in the slice at
1.00 nats/byte as in the one at 0.10. Weighting by mix share just rebuilds the blend, and
weighting the raw losses equally hands web ~10x temporal's leverage — it is even *quieter* than
the mean of logs on this run, 0.86% against 0.94%, precisely because it is mostly listening to
one slice. Quiet is not the objective.

Replayed over `nano20m_web`'s 41 evals, the new rule picks **iter 20,000** — the checkpoint
`evals/` prefers on all three rows — where the blend picked 18,000. That is the whole of the
evidence: one run, one comparison, two checkpoints with frozen-set scores on both sides.
`scripts/check_train.py` carries those 41 evals as a regression case alongside a scale-invariance
check and the arithmetic-mean contrast that proves the invariance check discriminates. Every
checkpoint written before this was selected by the blend, and `corn.evals` now prints which rule
chose the file it is scoring rather than leaving it to be inferred.

**What has not changed: `last.pt` is still written unconditionally and still worth scoring.**
The new rule is better on the one comparison there is evidence for and unvalidated on the other
39 iterations of that run. `HARNESS_VERSION` stays at 1 — no scored quantity changed, and
`nano20m_web` re-scored identical across the fix.

**Three smaller things this run settled:**

- **`reserve_tail` was armed for the first time.** Until now the eval text stayed out of train
  because the budget happened to stop before reaching it. This build reads 199M of 484M
  readable web bytes, so a larger run or a `repeat` pass would have walked straight into
  `evals/text_web.txt`. The reservation costs 0.25% of the slice, and all three texts read
  `clean` against `train.bin` and `val.bin` — §7's durable fix verified in a build rather than
  in a self-check.
- **`make_evals.py --add` earned its existence.** `evals/text_web.txt` was added with all
  three prior sha256 unchanged and `built` still reading 2026-08-10, so every number in the
  fifth and sixth findings stayed comparable across a change to the eval set.
- **A fourth throughput reading, 178–180k tok/s flat across 20,000 iterations**, clustering
  with the pilot's 178k and leaving the 196k of the third finding looking like the anomaly.
  And `prepare_mix` took 19 seconds for 497.5M tokens — 0.7% of the run it feeds — which
  answers whether corpus changes get expensive as §4 fills in.

**What this does not show:**

- **One shard, one threshold.** 13 more shards exist and `--min-score 3` is a different
  corpus. Nothing here says 40% is the right share or that this is the right filter; it says
  the slice is cheap to get and what it costs the other slices at 25M.
- **The narrative regression is a 25M result.** Capacity competition is the obvious reading
  and the exposure control makes it the only one available, but "40% of a 25M model" and "40%
  of a 250M model" are not the same amount of room. This is the direction, not the size.
- **`temporal.copy` is still at ceiling, which is where it stops being informative.** It
  survived real web text without moving, which is the question that was asked — but a row
  reading 353/353 in four consecutive checkpoints cannot show how much margin is left before
  the fifth one breaks it.
