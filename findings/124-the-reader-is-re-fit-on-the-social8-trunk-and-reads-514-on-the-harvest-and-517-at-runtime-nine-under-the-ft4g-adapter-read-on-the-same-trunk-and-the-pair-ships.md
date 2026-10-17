# Hundred-and-twenty-fourth finding — the reader is re-fit on the social8 trunk and reads 514 of 721 on the harvest and 517 at runtime at its own threshold, nine under the ft4g adapter read as a proxy on the same trunk, and the pair ships with the swap guarded

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft_social8`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**2026-09-05, the seventh section's four steps on the last trunk that
landed. `scripts/train_reader_whole.py --ckpt checkpoints/corn_jr_260m_v4_ft_social8/ckpt.pt
--seed 1 --tag social8`, run eagerly (`--no-compile`, bf16 autocast on;
§3 for why), three epochs in 3,138 s at ~20k tok/s, epoch 1 selected on the
held-out pooled metric, `checkpoints/reader_whole_social8_s1.pt` written
with arm 8's sha256 (`87c395d623e0`) inside it. Then the script's own
Population A read at the bar protocol, then `probe_reader_runtime.py` with
the new file on its own trunk at the new constant.**

## 1. The re-fit, against the ft4g adapter's own numbers

    held-out              ft4g trunk (finding 112, s1)     social8 trunk
      epoch 0  pooled / exact-pair      0.5593 / 0.5442     0.5485 / 0.5402
      epoch 1  pooled / exact-pair      0.5772 / 0.5644     0.5809 / 0.5617   <- selected, both
      epoch 2  pooled / exact-pair      0.5715 / 0.5540     0.5762 / 0.5530

    Population A, bar protocol, extent d = 2.0, hybrid reduce, own CV'd t
                                   right  wrong  silent  u.silent  att     acc|att   t (folds)
      ft4g adapter, harvest (116)    523    127     71       198     0.902   0.805    -1.094 / -1.254
      ft4g adapter, runtime (117)    526    122     73       199     0.899   0.812    -1.174
      social8 re-fit, harvest        514    145     62       194     0.914   0.780    -0.975 / -1.584
      social8 re-fit, runtime        517    147     57       197     0.921   0.779    -1.280
      ft4g adapter as proxy on the
        social8 trunk, runtime (123) 526    130     65       195     0.910   0.802    -1.174 (ft4g's)

    paired against the window head on the harvest:  right +122 (lost 33, won 155, p = 4e-20)
    species, window head -> re-fit:  REFUSED_WRONG 93->35  REFUSED_RIGHT 78->19  AGGREGATION 61->3
                                     RIVAL 66->111  CLIPPED 19->33  UNGROUNDED 12->6

**The re-fit reads finding 112's 513 to the passage** -- the whole-passage
arm's first read on ft4g before the grounding repair -- and **nine under
finding 116's 523** for the same adapter on its own trunk under the repaired
rule, at four fewer correct silences. Runtime is three over harvest, the
same fp32-over-bf16 shape finding 117 (b) traced. The species is the
whole-passage arm's: the three window species gone, RIVAL up, CLIPPED up,
and RIVAL is where the nine went (111 against 94 on ft4g seed 1).

**The number that has to be at the top: the ft4g adapter, read as a proxy
on this exact trunk, reads 526 at 195.** So on the social8 trunk, at one
seed each, the delta fitted to ft4g's states reads nine more right answers
than the delta fitted to social8's own states. Finding 118 said the old
adapter survives the move; this says a fresh fit does not obviously beat it.
Three readings are open and none is settled by one seed:

  * **seed spread.** Finding 112's two seeds on ft4g read 523 / 517 under
    the repaired rule, a spread of six; nine is one-and-a-half of that.
  * **the eager run.** The ft4g adapter was trained under `torch.compile`;
    this one was not (§3). Same autocast, same arithmetic, different kernel
    fusion; finding 117 put the compile-vs-eager *inference* gap at three
    passages, and no number exists for training.
  * **the trunk.** Four fine-tunes stacked on ft4g may have moved the states
    the head reads at layers {8, 12, 16} in a way that fits worse from
    scratch than the old delta ports. That would be the head-portability
    finding the seventh section named, in the direction nobody expected.

## 2. The pair ships, per protocol, with the comparison recorded

The seventh section's protocol is the re-fit, and the fingerprint is the
design: `load_adapter` refuses the ft4g file on the social8 trunk by hash,
and re-stamping it to serve the better number would be the rule the port
built being bent on its first use. So the pair that ships is the re-fit at
its own threshold, and the comparison above is the first thing the next
session reads. What would settle it is a second seed of the re-fit (~50 min
eager, ~55 compiled) read the same way; if it also reads under the proxy,
the head-portability question is answered in favour of *porting the delta*
and the design should say so.

**The swap**, each held by a guard:

    corn/reader.py            WHOLE_THRESHOLD = -1.280      (was -1.174)
    harness/serverconfig.py   reader_adapter   = checkpoints/reader_whole_social8_s1.pt
                              reader_whole_threshold = -1.280
    harness/backends/read.py  WHOLE_ADAPTER    = checkpoints/reader_whole_social8_s1.pt
    server.json               ckpt = checkpoints/corn_jr_260m_v4_ft_social8/ckpt.pt
    scripts/check_model.py    "the shipped adapter names the shipped trunk" now reads the
                              pair from ServerConfig and server.json rather than repeating it

`check_extract.py` holds `ServerConfig().reader_whole_threshold` equal to
`WHOLE_THRESHOLD` and the two thresholds not equal to each other;
`check_model.py` asserts the shipped adapter carries the shipped trunk's
hash and still refuses a different trunk. **`reader` stays `generate`** --
decision 7 is the owner's, unchanged by any of this -- so what changed for
a user tonight is the trunk `server.json` names, which carries the social
class, the consolation family, the second turn and the depth generalisation
of findings 119 to 123, and the adapter that is *available* behind
`--reader head_whole`.

## 3. The compiled path, broken and fixed

The first launch died at `torch.cat` inside `_trunk_states` under
`torch.compile(dynamic=True)`: "cat expects at least one tensor". Reproduced
on a four-layer toy trunk in a minute: with torch 2.11, `dynamic=True`
treats the ints of a tuple *argument* as symbolic, `i in layers` never
resolves true while tracing, the tapped list stays empty. The same
function with `layers` closed over as a constant traces and matches eager
on two shapes; `dynamic=False` also traces. `GradStates` now closes over
its layers (commit `a29b527e`), so the plan's compiled recipe is back for
the next trunk; this re-fit ran eagerly because the card clock mattered
more than twenty minutes.

## Limits

One seed of the re-fit against one seed of the old adapter, on one
population, and the comparison that matters is nine passages at n = 721.
The eager-versus-compiled training difference is unmeasured. Nothing here
is a live session; packs are still unmeasured under any reader.

## On disk

`checkpoints/reader_whole_social8_s1.pt` (gitignored, stamped);
`evals/results/reader_whole_social8_s1_popa.json`,
`pairs_whole_social8_s1_popa.json`, `whole_social8_s1.json` (the script's
card), `reader_runtime_whole_social8_s1.json` (the runtime read).
