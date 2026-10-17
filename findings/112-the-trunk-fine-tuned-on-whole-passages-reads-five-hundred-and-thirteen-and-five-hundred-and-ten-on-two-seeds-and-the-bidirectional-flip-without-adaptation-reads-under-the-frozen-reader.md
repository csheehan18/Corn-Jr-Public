# Hundred-and-twelfth finding — a rank-32 adapter on the trunk, reading each passage whole under causal attention, reads 513 and 510 of 721 on two seeds against the shipped 389 and 388, and the bidirectional flip without an adaptation phase reads 267 after one epoch, under the frozen reader it was meant to beat

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`scripts/train_reader_whole.py`, 2026-09-04/05. **Two seeds of the arm that
counts, same recipe, each at its own article split and read against its own
shipped harvest; one epoch of the one that does not.** `corn/reader.py`,
`corn/model.py` and the conversational checkpoint are untouched: the
adapter and the attention flip are bound inside the training process, the
base weights are held by reference and asserted to take no gradient, and
nothing in `corn/` was edited. `evals/results/whole_causal_s{1,2}.json`,
`{reader,pairs}_whole_causal_s{1,2}_popa.json`, the epoch-0 reads
`whole_{causal,bidir}_ep0_s1.json` and their harvests;
`checkpoints/reader_whole_causal_s{1,2}.pt` (gitignored, with per-epoch
files).

## 0. Why this arm, and what it is

Findings 83 to 109 changed the span head, its data, its epochs, its seeds,
its layer band and its prompt, and every one of them read the same states:
the frozen `corn_jr_260m_v4_ft4g` under `worker_prompt`, one 64-token window
at a time. The three cheap representation reads of 2026-09-04 (107, 108,
109) said those states carry no more than the shipped heads already read.
The one lever no arm had pulled is the one every extractive reader in
`EXTERNAL-RESEARCH.md` §16 and `PLAN-READER-WHOLE.md` §0.4 pulls: the trunk's
weights. This is `PLAN-READER-WHOLE.md` §4 (W2) as written, with two
deviations named in §5.

    the window      the payload's `answer` field carries the whole passage:
                    one forward, one null, no vote
    the trunk       LoRA rank 32, alpha 64, on `c_attn`, `c_proj`, `c_fc`,
                    `c_proj` of every block; base frozen; `lm_head` and the
                    embeddings never adapted; 10.5M adapter parameters
    the head        LayerNorm per layer chunk, then `PairHead`'s scorer over
                    layers {8, 12, 16}, `0 <= j - i < 16`, and a null MLP at
                    the say marker, in one softmax with every gold
                    occurrence summed (R1's loss); 6.3M parameters
    the data        `nq-train-full.jsonl`, one prompt a passage: 83,653 of
                    87,345 rows kept (2,043 over the 512 block, 943 escaped,
                    385 too long, 314 unaligned); 79,403 train / 4,250 held
                    out by article on seed 1
    the schedule    AdamW, head and adapter at 3e-4, 200 warmup, cosine to
                    zero over 3 epochs, bf16 autocast on the trunk, fp32 head,
                    batches of equal length capped at 16 rows, 4,096 tokens
                    and 24,000 candidate pairs -- and the pair cap is the one
                    that binds, so the batch was ~8 rows a step (10,086 steps
                    an epoch over 79,403 passages); ~25 min an epoch on an
                    idle 3080, eager, per-row head

## 1. The bidirectional arm first, because it went first and it failed

The plan's breakthrough variant is `is_causal=False` on the reading forward.
Run first, seed 1:

    epoch 0 held-out   pooled 0.3522   nulls 0.8034   positives 0.1584   exact-pair (null out) 0.1958
    Population A, bar protocol, extent on, epoch-0 checkpoint:
      right 267  wrong 258  silent 196 | u.silent 193   att 0.728   acc|att 0.509
      paired vs shipped: right -122 (lost 177, won 55, p = 4e-16)
      gold in the ten 472, ranked first 193   (shipped: ranked first 494)
      species: AGGREGATION 64 -> 13, REFUSED_RIGHT 78 -> 15, RIVAL 63 -> 210

**The whole-passage mechanism worked and the reader did not.** The vote
losses vanished as the plan said they would, and what replaced them is a
picker that finds the passage's entities and confuses them (RIVAL 210):
another actor from the same film, a date near the right date. A causally
pretrained trunk read with full attention has every state perturbed by keys
it never attended, and a rank-32 adapter did not rebuild them in one epoch.
The run was stopped at epoch 1 to spend the card on the control, which is
the decision this finding rests on; its epochs 1 and 2 are unread.

## 2. The causal control is the result

Same data, same schedule, same head, `is_causal` as the trunk was trained:

    held-out                 pooled    nulls    positives   exact-pair (null out)
    s1  epoch 0              0.5593    0.6829   0.5062      0.5442
    s1  epoch 1  selected    0.5772    0.7831   0.4887      0.5644
    s1  epoch 2              0.5715    0.7580   0.4914      0.5540
    s2  epoch 0              0.5484    0.7482   0.4623      0.5353
    s2  epoch 1              0.5664    0.7890   0.4704      0.5681
    s2  epoch 2  selected    0.5683    0.7537   0.4883      0.5495

Exact-pair on whole passages (~157 candidate rows) after one epoch equals the
shipped head's 0.5410 on windows (~62 rows). Training loss 3.85 at step 201
where the bidirectional run read 5.02; 0.68 / 0.62 by the end of epoch 2.
The two seeds select different epochs on a pooled metric that is flat to a
point across epochs 1 and 2, which is the schedule saying it is about done
and not that either epoch is the right one.

**Population A, bar protocol, extent d = 2.0, hybrid reduce, each harvest at
its own cross-validated threshold, `probe_harvest_paired.read_at_bar`:**

                          right  wrong  silent  u.silent  joint  attempt  acc|att   t
    shipped s1              389    188     144       199    588   0.800    0.674   -1.980 / -2.061
    causal W2 s1, epoch 0   474    159      88       194    668   0.878    0.749   -0.140 / -1.354
    causal W2 s1, selected  513    126      82       199    712   0.886    0.803   -1.142 / -1.393
    shipped s2              388    172     161       196    584   0.777    0.693   -1.600 / -1.746
    causal W2 s2, selected  510    123      88       199    709   0.878    0.806   -0.835 / -1.630

    paired vs shipped, s1:  right +124 (lost 31, won 155, p = 5e-21)
                            joint bit +124 (lost 65, won 189, p = 3e-15)
    paired vs shipped, s2:  right +122 (lost 40, won 162, p = 1e-18)
                            joint bit +125 (lost 74, won 199, p = 2e-14)
    funnel:  gold in the head's ten 673 / 673 of 721, ranked first 484 / 489
    species, shipped -> arm:      s1                 s2
      REFUSED_WRONG               93 -> 40          110 -> 42
      REFUSED_RIGHT               78 -> 15           80 -> 25
      AGGREGATION                 64 -> 16           50 -> 10
      RIVAL                       63 -> 94           59 -> 90
      CLIPPED                     18 -> 32           23 -> 34
      UNGROUNDED                  16 -> 11           11 -> 10

**513 and 510 of 721 is 71.2% and 70.7% strict**, +124 and +122 right on
the same passages, at a higher attempt rate *and* twelve points more
precision when speaking, on both seeds. Correct silence reads 199 and 199
against the 200 floor. Against the plan's bars: W1's `right >= 430` cleared
by 83 and 80; W2's PRIMARY `right >= 560` missed by 47 and 50; the plan's
BERT-base anchor (EM 65.4 on this format, about 470) passed twice. Every
species moves the same way on both seeds: the three the windows caused
(REFUSED_RIGHT, AGGREGATION, REFUSED_WRONG) fall by two thirds or more,
UNGROUNDED is flat or down, RIVAL rises because the reader now speaks on
88% of passages instead of 78–80%, and CLIPPED, the one cost, rises 18 to
32 and 23 to 34: a head with the whole passage in view walks off the end of
an entity more often, which §3.3 of the plan predicted, and the extent rule
is already on.

The one passage of Population A whose prompt exceeds 512 tokens is silent
and counted (`popa_silent_unread` 1); it is answerable, so it is one of the
82.

## 3. By agreement and by type

The plan's Stage 0 ruler, replayed off the same verdicts (`annotators` from
`nq-dev.jsonl`):

    annotators   rows   shipped s1 / s2          causal W2 s1 / s2
    2 of 5        234    99 (42.3%)  91 (38.9%)   127 (54.3%)  123 (52.6%)
    3 of 5        168    82 (48.8%)  80 (47.6%)   113 (67.3%)  108 (64.3%)
    4 of 5        144    92 (63.9%)  94 (65.3%)   118 (81.9%)  124 (86.1%)
    5 of 5        175   116 (66.3%) 123 (70.3%)   155 (88.6%)  155 (88.6%)
    A-CLEAN >= 4   319   208 (65.2%) 217 (68.0%)   273 (85.6%)  279 (87.5%)

    answer type   rows   shipped s1 / s2          causal W2 s1 / s2
    name           401   242 (60.3%) 240 (59.9%)   300 (74.8%)  292 (72.8%)
    number         195   115 (59.0%) 117 (60.0%)   143 (73.3%)  153 (78.5%)
    other          125    32 (25.6%)  31 (24.8%)    70 (56.0%)   65 (52.0%)

The gain is on every bucket on both seeds and largest where the annotators
agreed, so it is not living on contested labels. On A-CLEAN it is 273 and
279 against W2's bar of 250, and against the owner's 85% restated there
(272) it is one and seven over — the target, on the ruler the plan says can
carry it, is met on both seeds, by a margin inside the seed spread on one.
`other`, the type every generative vehicle failed and R1 barred at 0.50,
doubles on both seeds.

## 4. Three replay checks made before any of this ran, all null

On the shipped heads' `RANK_2_10` windows (the gold in the ten and not
first), over `pairs_built_s{1,2,3}_popa.json`: the winner sits later in the
window than the gold on 38 / 45 / 40% and earlier on 45 / 42 / 44%; gold and
winner contain a question content word equally often (39 vs 41, 55 vs 57);
neither is systematically longer. The pick's error on the frozen states is
not a shallow feature, which is consistent with what moved it being the
weights and not another read of them.

## 5. Deviations from the pre-registration, and costs

  * **The product term is projected first.** `PairHead` reads `C (h_i * h_j)`
    on the raw 3,072-dim rows; with the trunk in the graph that filled the
    card at step ~100 and thrashed the allocator (no step logged in ten
    minutes). The head here reads `C ((P h_i) * (Q h_j))` at width 512, the
    same low-rank family, six times narrower on the pair axis. Peak memory
    5.1 GB.
  * **W1 was not run first.** The plan sequences the frozen whole-passage
    read before the adapter; §8 allows starting W2 on §0.4's argument, and
    findings 107–109 had already made it. `--frozen` exists in the script
    and is unrun; the causal-adapter epoch-0 read is the nearest thing to
    W1's number on the record.
  * **Seed 1 was first read at 505, and that number was a chimera.** The
    per-epoch record held `head.state_dict()`, a live view of the weights,
    so when seed 1 selected epoch 1 the in-process final read used epoch
    1's adapter with epoch 2's head. Found when a re-harvest from the disk
    checkpoint (serialised at epoch 1, correct) differed on 124 passages;
    the record now copies. Every seed-1 number here is from the disk
    checkpoint. Seed 2 selected its last epoch and was unaffected; the
    fold arms of finding 113 had the same mix and were re-read from disk.
  * **The bidirectional arm has one seed and one epoch.** Its number is a
    reason the control was run, not a result about the flip.
  * **Costs, as measured:** first bidirectional attempt lost to the memory
    thrash (~15 min); bidirectional epoch 0 ~23 min; causal seed 1 ~80 min
    including an epoch-1 slowdown from a Population A harvest run beside it
    (do not do that — 195 s instead of 40 s for the harvest and ~5 min lost
    on the run); causal seed 2 ~67 min on an idle card; items cache 46 s
    once, reused.

## 6. What this does not say, and what is next

It does not say the flip is dead: `--mntp-steps` adds an
adaptation phase — masked next-token prediction under full attention through
the frozen `lm_head`, LLM2Vec's remedy — and is unrun. It does not ship: the
port is a guarded `causal` argument and adapter loading in `corn/model.py`,
a `whole` path in `HeadReader`, and `check_model.py`'s byte-identity guard
with the adapter off, as `PLAN-READER-WHOLE.md` §4.1 and §6 specify. And the
frozen-eval regression rows (`extract.jsonl` tight / abstain through this
head) were not read.

## 7. On disk

`scripts/train_reader_whole.py` (new): `--bidirectional`, `--frozen`,
`--mntp-steps`, `--resume` (per-epoch files carry the optimiser from the
causal run's epoch 0 onward), `--load` for a replay harvest, writes both
harvest shapes and prints the paired bar-protocol read. Items cache at
`F:/corn-jr-data/states/whole_items.pkl` (87k prompts tokenised and aligned,
regenerable in 46 s).
