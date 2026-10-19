# Rotary position embeddings beat learned positions on most tests

**Full result:** RoPE against learned positions on the dummy world: above on the trained parse at both seeds, three per cent better on three of four language rows, two below on the bound tree, and the held-out rows zero as on every arm before it, so rung 2 trains both trunks at nano and its mid size takes the one the parse prefers

**Cost:** 3.1 min of scoring on the 1 card first cited here (`nano20m_v3_decomp_b_rope`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-TAG-SPINE phase C0, the position encoding as an arm (§5 lever 4), read
2026-09-13. Two nano runs, `nano20m_v3_decomp_b_rope` at seeds 1337 and
1338, on arm B's file byte for byte (`data/mix_v3_decomp_b`, rule 1) under
B's schedule, loss policy and token budget, with one field moved:
`Config.pos_enc="rope"`. Pre-registered in the config docstring with B's
band, the outcome table, the unreadable outcome, the kill and the fallback
before a byte trained. B's two seeds are the control, already scored,
nothing retrained. Full cards, the bound partial cards (`--role-bind
--copy-bind`), and `scripts/check_decode.py` parity on both checkpoints.

## The question

Rung 2 asks whether a label learned as a function can be written for a
shape he was never shown, and learned absolute positions are the choice the
compositional-generalisation literature most consistently finds harmful for
exactly that. Ten runs train one trunk. **Which?** Measured on the world
that exists, so the choice is a reading and not a citation, and so a RoPE
defect in the decode path is found on a seventeen-minute run.

## What was built

`Config.pos_enc` (`learned` | `rope`, `rope_theta`). Under `rope` no `wpe` is
built; every attention layer rotates q and k by their position before the
dot product, in the training forward and in the graphed decode `step`
alike, so the cache holds rotated keys and decode needs no new path. The
trunk is drawn exactly as the learned build draws it -- `wpe` constructed
so the generator advances the same, then dropped -- so at one seed a RoPE
arm against a `wpe` arm is the encoding alone. `pos_enc` joined
`INIT_MUST_MATCH`, so a fine-tune across it is refused by name.

**Held by `scripts/check_model.py`**, sixteen new checks: `pos_enc="learned"`
spelled out is the pre-flag forward bit for bit; the RoPE trunk is the
learned trunk tensor for tensor minus `wpe`, and the generator is left
where the learned build leaves it; the RoPE `step` -- token by token and as
one chunk into an empty cache -- is the RoPE `forward` within 1e-5, and the
cat-cache forward is too; attention under RoPE is unchanged by a constant
shift of every position to 1e-9 and moved by a stretch of the positions.
`check_decode.py` on a RoPE checkpoint: greedy parity 96/96 static, graph,
bucketed and compiled; prefix reuse 24/24; the batched reader inert -- on
the smoke checkpoint before the runs and on both trained ones after.

**Cost, measured before the run** (`corn/trainbench.py`, batch 24 x 512,
bf16, compiled, 30 timed steps after 5 warm, idle card; probe only -- not
on disk): 139.1 against 137.6 ms a step, **+1.1%**, peak 3.18 against 3.00
GB. 29,368,832 parameters against 29,630,976: the 512 x 512 table.

## The read, against B's band

    row                 B s1   B s2   RoPE s1  RoPE s2   reading
    parse.span            77     78      81       81     above, both seeds
    parse.entity          71     77      70       74     inside
    parse.heldout          0      0       0        0     zero, as ever
    parse.depth3           0      0       0        0     zero, as ever
    move.next             96     97      98       96     inside
    move.args            120    115     118      116     inside
    e2e.tree              18     24      22       16     inside B's spread of 6
    e2e.rebind            48     49      48       46     one seed two below
    move.next  bound     116    117     117      118     inside
    move.args  bound     120    120     120      120     inside
    e2e.tree   bound      45     51      43       43     two below B's low, both seeds
    e2e.rebind bound      48     49      48       46     one seed two below
    tool.copy            120    120     120      120     inside
    tool.copy_wide       296    289     292      292     inside
    tool.validity        136    138     155      159     above, both seeds
    tool.selection       128    118     138      104     the row whose spread is 35
    temporal.route       399    397     397      398     inside
    temporal.copy        353    353     353      353     inside

    val_loss            2.2899 2.3124  2.2236   2.2464   lower by 0.066 at both seeds
    nats/byte  narrative 0.4510 0.4522  0.4362   0.4389   -3.2%, both seeds
               web       0.8832 0.8822  0.8571   0.8586   -2.9%, both seeds
               conv.     0.5155 0.5164  0.4962   0.4947   -3.9%, both seeds
               temporal  0.1080 0.1092  0.1095   0.1050   inside

Run time 1,040.7 s and 1,086.7 s against B's ~1,010 s (the second beside
the owner's desktop in use).

**The pre-registered table lands on its mixed row.** RoPE is above B's
band on `parse.span` at both seeds (81 and 81 against 77 and 78, B's own
spread 1), above it on `tool.validity` at both, and better on three of four
language rows at both seeds with the validation loss lower by 0.066 twice
-- and it is two below B's low on the tree under the binding at both seeds
(43 and 43 against 45 and 51, B's spread 6). By the docstring's own
definition of the band, widened by nothing, that is below on one deciding
row and above on another, and the row written for it says: **rung 2's nano
seeds train both trunks, and the mid size takes the one nano prefers on
the parse rows.** The kill did not fire (the copy band holds at 120, 292,
353); the fallback did not fire (nothing is below at both seeds on the copy
band, on `parse.span` or on the language rows).

Two things beside the table. The bound-tree gap is inside B's own seed
spread and lives in the sixteen items whose two tools of one role the
label cannot choose between (finding 131), so it is a direction and not a
size. And the language rows are the clearest read in this finding: three
per cent of nats a byte at both seeds on web, narrative and conversational
prose is larger than any arm on this mix has moved them, and it is the
reason RoPE goes to the 1.0 corpus's trunk decision (PLAN-1-0 §10) as a
measured candidate whatever rung 2 reads.

## An instrument fact, found while designing the next world

`corn/decompgen.py` joins level-1 parts and level-2 children from one
joiner table, so a two-question turn is a legal flat pair *and* a legal
composite, and the gold is whichever the generator drew. Counted on the
frozen rows (probe only -- not on disk): **26 of 120 `span` items, 33 of
120 `entity`, 63 of 120 `heldout` and 96 of 96 `depth3`** carry a level-1
arity that no reading of the sentence decides. B's `span` failures are 19
of 43 `wrong_arity` and its `depth3` failures 43 of 96; every `parse.depth3`
zero since finding 129 was read on items whose flat parse is legal. This
does not move any reading in this finding -- both trunks were read on the
same rows -- and it is why the next world marks a composite on the surface
(PLAN-TAG-SPINE §5b).

## Instruments

* The trunk-init sameness across the flag, in the guard before anything
  trained -- finding 130's lesson, applied at construction.
* A smoke run of the real trainer (twelve iterations, compiled, one eval,
  one checkpoint) and `check_decode.py --compile` on its checkpoint, before
  the runs.
* `check_decode.py` on both trained checkpoints after, so a decode-path
  defect could not be read as a model result -- the unreadable clause of the
  pre-registration, which did not fire.

## Limits

Two seeds, so directions (rule 6). A nano read on a dummy world whose
held-out rows are zero on every trunk, so nothing here says what the
encoding does for the thing rung 2 is for; that is C4's question, and it is
why both trunks train there. The bound-tree difference is two items at
each seed inside a spread of six. The language-row gain is on a 137M-token
mix at 29M parameters and is not assumed to survive to 260M.
