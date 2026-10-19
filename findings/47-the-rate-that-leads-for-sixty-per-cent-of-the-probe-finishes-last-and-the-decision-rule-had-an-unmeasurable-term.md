# The leading learning rate finished last; 3e-4 stays

**Full result:** The rate that leads for sixty per cent of the probe finishes last, and the decision rule had an unmeasurable term in it

**Cost:** 10.2 min of scoring on the 1 card first cited here (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`configs/corn_jr_260m_lr{3e4,4p5e4,6e4}.py`, run 2026-08-22 on the 3080. Three
2,000-iteration probes, 49,152,000 tokens each, **37.9 / 37.6 / 37.6 minutes,
1.89 hours for all three.** This is the 1.7 hours `corn_jr_260m.py` priced
against 2.5 days of regret, and it is spent.

`lr` was the one unmeasured number in the Phase 2 config. It is now a screened
one, which is a weaker thing than a measured one and is exactly what the
instrument was built to deliver.

## Nothing was vetoed

The pre-registered disqualifiers were NaN, an unrecovered loss spike, and val
loss climbing across consecutive post-warmup eval points. **None of the three
rates hit any of them.** All three exited 0, and throughput held 23.0–23.2k
tok/s throughout — which incidentally confirms the 23.5k planning figure the
220-iteration smoke test established, at 40× the length.

| iter | 3e-4 | 4.5e-4 | 6e-4 |
|---|---|---|---|
| 0 | 9.2475 | 9.2475 | 9.2475 |
| 250 | 4.1994 | 4.1542 | **4.1285** |
| 500 | 3.4365 | 3.3793 | **3.3397** |
| 750 | 3.0934 | 3.0448 | **3.0105** |
| 1000 | 3.0098 | 2.9533 | **2.9404** |
| 1250 | 2.8481 | 2.8202 | **2.8223** |
| 1500 | 2.5735 | **2.5509** | 2.5553 |
| 1750 | 2.6300 | **2.6166** | 2.6307 |
| 2000 | 2.4796 | **2.4725** | 2.4832 |

**The comparison is paired, and iter 0 is the proof.** All three configs carry
`seed=1337` and differ only in `lr`/`min_lr`, which consumes no RNG, so the
data order and the val batches at each eval point are identical across the
three runs. Val at iter 0 agrees to four decimals in all three columns. This
is a stronger design than three independent runs and it is stronger by
accident rather than by intent — the probes were written to hold everything
fixed, and pairing fell out of that.

## The ordering flips, and that is the result

**6e-4 is the best rate at five of the first six eval points and the worst
rate at the last one.** It leads through iter 1,250 — 62% of the probe — and
finishes third. 4.5e-4 takes the lead at 1,500 and holds it to the end.

That is the finding, and it is empirical support for a pre-registration that
until now was only an argument. `corn_jr_260m_lr3e4.py` declared before any
probe ran that **the instrument vetoes rates and does not rank them**, on the
a priori grounds that 2,000 iterations of a 203,451-iteration run cannot say
which rate wins at 5B. It now has evidence: the ranking did not survive even
to the end of the probe itself, at 1% of the run. A screen that had stopped at
iter 1,250 — still 25 minutes of GPU, still a plausible place to stop — would
have promoted 6e-4 on a lead it was about to lose.

The uptick at 1,750 is common to all three columns and is therefore the val
draw, not the rates: eval points sample 40 fresh batches each, so **absolute
val at a single point carries roughly 0.05 of sample noise** (the 1,500 →
1,750 move against a downward trend). Common-mode, so it cancels in the paired
comparison — but it is the reason no single eval point can be read alone.

## 3e-4 stands, and not because 4.5e-4 lost

The pre-registered rule: if all three survive, 3e-4 stands unless a higher
rate is below it at **every** post-warmup eval point **by more than the eval
noise**.

4.5e-4 satisfies the first clause. It is below 3e-4 at **8 of 8** points, sign
consistent throughout, under a paired comparison. The margin runs 0.0452 at
iter 250 down to **0.0071 at iter 2,000**.

The second clause cannot be evaluated, and that is the honest outcome. Because
the arms share their val draws, the sample noise that the 1,750 uptick
measures **cancels** in the paired difference — so the relevant floor is not
eval-sample noise at all but run-to-run seed variance on the paired gap, and
**there is one seed per rate.** The thirtieth finding's rule is that a floor is
a property of the arm and a single seed cannot establish one. So 0.0071 is not
a small effect; it is an **unpriced** one.

**The rule as written contained a term nobody had arranged to measure.** It
named "the eval noise" without saying which noise or how it would be counted,
and the paired design — which was not anticipated when the rule was written —
changed the answer to that question. This is the same class of defect as the
forty-sixth finding's guard that read the generator instead of the artefact:
the instrument was fine and the thing that decides what the instrument means
was not checked. It cost nothing here, because the rule's default clause
resolves the case either way.

So the config launches at **3e-4, unchanged**, on the pre-registered default
rather than on a demonstration. Changing a 2.5-day run's learning rate on a
consistent-sign 0.0071 with no floor under it would be precisely the error
this project has now caught four times.

## What this does not settle

- **Whether 4.5e-4 is better at 5B.** 8 of 8 on a paired comparison is real
  evidence of a sign and no evidence at all of a size, and the sign was also
  consistent for 6e-4 right up until it reversed. The cheap thing that would
  settle it is **a second seed on 3e-4 and 4.5e-4 only** — 75 minutes, and it
  gives the paired gap a floor for the first time.
- **Anything about 6e-4 at length.** Its late fade is consistent with the
  small-batch argument in `corn_jr_260m.py`'s docstring — 24,576 tokens per
  step against the ~0.5M the recipes quoting 6e-4 use — but a fade inside a 1%
  probe is not that argument confirmed. It is one crossing.
- **The trunk beyond 2,000 iters.** `decay_frac=0.0` means these read the `wsd`
  trunk with no anneal, by design. The `lr 3.00e-05` printed on the iter-2,000
  line is `lr_at`'s post-loop display for `it >= max_iters`; **no step trained
  at `min_lr`**, and iter 1,999 reads the full rate, verified against `lr_at`
  directly before the probes ran.
- **Scale.** These are 260.6M probes, which is the size they were meant to
  screen, so the usual transfer caveat does not apply here — but 49.2M tokens
  is 1% of the budget and none of the behaviour rows exist at this length.
  Nothing here is a corpus reading.
