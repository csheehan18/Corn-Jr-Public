# He learns to label his own request; forcing labels doesn't change calls

**Full result:** He learns to write the parse, half of it is label and not position, and not one of two hundred and forty forced tags moves a call

**Cost:** 2.8 min of scoring on the 1 card first cited here (`nano20m_v3_compiled`); it also reads 1 card scored for an earlier finding (`nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Eight nano arms trained 2026-09-09 from `configs/mix_v3_decomp_{a,b,c,d}.py`,
two seeds each, all compiled, pre-registered in `configs/mix_v3_decomp_b.py`'s
docstring before a byte of any arm trained. Built to `docs/PLAN-DECOMPOSE.md`
rung 1. Controls are the four already-scored `nano20m_v3` seeds plus a fifth
trained for this read (`nano20m_v3_compiled`); **nothing else retrained and
nothing was re-scored** except where this finding says so and says why.

The rows are eight new ones added by `scripts/make_evals.py --add` and scored
on `nano20m_v3` before the corpus existed (rule 23). The floor is seven hard
zeros and `move.args` at 39/120.

## The question, and the shape of the answer

PLAN-DECOMPOSE's claim: a request is a sequence of parts, a part of a composite
kind is itself a sequence of parts, **he emits that parse as tags over spans of
the user's own words**, and because every level is a token he wrote, every
level can be scored, forced and read back. Depth through him rather than
through a longer forward pass.

Four arms, one variable each: **A** no parse line, **B** one-pass, **C** B with
the labels globally permuted and the spans kept, **D** stepped — the runtime
hands each part back and he opens it or acts on it.

    row              floor      A          B          C          D      n
    parse.span          0     0/0      77/78      38/37      58/56    120
    parse.entity        0     0/0      71/77      29/29      46/42    120
    parse.heldout       0     0/0       0/0        0/0        0/0     120
    parse.depth3        0     0/0       0/0        0/0        0/0      96
    move.next           0   65/65      96/97     99/103      96/88    120
    move.args          39  114/114    120/115    117/114    113/116   120
    e2e.tree            0   24/26      18/24      25/28      29/31     60
    e2e.rebind          0   50/50      48/49      49/49      48/46     50

**The format installs and it is not padding.** B reads 77 and 78 of 120 on
trained shapes against a floor of zero, and 71 and 77 on shapes over entities
no transcript contains. The shuffled control reads 38/37 and 29/29 — real, and
half of B. So the labels carry content: C reproduces the cuts and misnames
them, `wrong_label` 63 of its failures. PLAN-DECOMPOSE §7's "structured
padding" row is refused. **This replicated on two independently generated
corpora and four checkpoints**, seed spreads of one item.

**It does not generalise.** Zero on held-out orders, pairings and carriers, and
zero at depth three — on every arm, both corpora, both seeds. A span-recall
probe over all 216 held-out and depth-3 items says what the zeros are made of:
on held-out carriers he recovers **21% of the gold cuts** and **63% of the
spans he emits are not in the sentence at all**. That is not near-missing. It
is finding 34's mechanism — handed a carrier he does not know he reaches for a
trained one (`go digging for` comes back `go and get`) and when that fails he
invents (`Ithunlvcombe` comes back `Ithunlvdia`). At depth three he does better
— 62% leaf recall, 81% of spans legal — but a complete correct decomposition,
every leaf in order, is **6 of 96**.

## The gate, and it is a hard zero

**0 of 240.** `scripts/probe_depth.py --probe forced` on four checkpoints:
same prompt, same spans, same labels, the level-2 line's two children in
swapped order — a forgery the grammar accepts and the corpus never wrote, and
one that implies a different tool first.

    checkpoint          forced   gold   neither   own-parse control
    decomp_b   seed 1     0/60   60/60     0/60         60/60
    decomp_b   seed 2     0/60   60/60     0/60         60/60
    decomp_d   seed 1     0/60   59/60     1/60         59/60
    decomp_d   seed 2     0/60   60/60     0/60         60/60

**And it is not memorisation.** `probe_depth.py --probe forced` and
`gen_decomp.py` share a default seed, so 28 of those 60 utterances are in the
training corpus verbatim -- and on a memorised sentence "answer from the
sentence" is the strongest possible prior, which would read as tag-blindness
whether or not the tag was blind. Re-run at `--case-seed 77001`, where **0 of
60 utterances appear in the corpus**, both B seeds read the same: forced 0/60,
gold 60/60, control 60/60. The zero survives the sentence being new.

The control is at ceiling, so these are not checkpoints that cannot answer.
They read the utterance and not the line. PLAN-DECOMPOSE §10's third kill
condition, pre-registered: *"The forced-tag probe not moving the calls. Then
whatever the rows say, the parse is decoration and the legibility claim goes
with it."* §9's argument — that a scored intermediate sorts every failure into
the level it happened at — does not survive, because the level he wrote is not
the level he acts on.

**And every behavioural row agrees.** `move.next`, `move.args`, `e2e.tree` and
`e2e.rebind` are flat across all four arms, and on `move.next` the *shuffled*
control is nominally the highest of the four. No arm beats C anywhere. The
parse line changes what he writes and not what he does.

## D was the alternative and D did not rescue it

§4 named adjacency in advance: *"If D reads and B does not, depth was there and
adjacency was the cost."* The decision that reads a one-pass tag sits far from
where the tag was written, and PLAN-1-0 §5c's memory probe is the precedent —
2/5 with no filler between frame and use, 0/5 with any. D writes each level
immediately before the calls that read it, with the runtime handing the part
back.

D reads zero on both held-out rows like everyone else, and **0 of 120 on the
forced probe**. Its `e2e.tree` 29/31 is nominally the best cell in the table
and is not a separation: B's own two seeds differ by six there, and B sits
*below* its own shuffled control. The adjacency explanation is spent.

D's `parse.heldout` and `parse.depth3` are additionally read through B-shaped
prompts — the frozen parse items carry no hand-back — so those two cells are
biased low and are floors rather than readings. Every other D cell is scored
under its own protocol, stamped `decomp_arm` on the card.

## The band is the corpus, and compile is ruled out

    row              eager x4   compiled    A       B       C       D
    tool.selection    128-129      131    63/96   98/128   ...     ...
    tool.validity     143-152      149    81/122  135/153  ...     ...

`tool.selection` and `tool.validity` fall far below every control seed on the
arms, with seed spreads of 33 and 30 against control spreads of 1 and 9 — the
direction is certain and **the size is not readable at two seeds**, which is
the sentence finding 74 had to write about `tool.copy` and is no more
satisfying here. A fifth control trained compiled on the *unchanged* `mix_v3`
reads 131 and 149, inside or above the eager band, so **compile is not the
cause**: a 5% slice declaring composed tool names displaces the tool decision,
which is finding 51's arity price and finding 69's displaced prior arriving
together. The copy band is untouched (`tool.copy_wide` above control on three
arms of four); `temporal.*` is flat.

One cell is unexplained and is reported rather than smoothed: the compiled
control reads `tool.copy` **103** against an eager band of 118–120, below every
arm. One seed, no explanation, and it should be re-read before anyone quotes
the copy band.

## Three instrument defects, all of which spared the baseline

Recorded because the pattern is the finding, not the individual bugs.

  * **`e2e.tree` grew the transcript past the 512 block** and died on `prefill`
    at item ten of the first arm-B card. Arm A had scored clean; its rollouts
    are shorter.
  * **`e2e.rebind` read arm B 0 of 50**, `no_call` on every item, because
    `corn.evals.continuation` stops at the first newline and an arm that emits
    a parse writes `parts:` first and its call second. Arm A read 48 of 50 on
    the same instrument for no reason but the order it writes its lines in.
    **That zero was reported as a result before it was understood.**
  * **Arm D's corpus was an oracle.** The runtime handed back only the parts
    that open, which told him which parts were composite — knowledge no runtime
    has. An arm trained on it learns "when handed a part, open it".

Every one of the three fell on the arms that emit a parse and spared the
baseline, which is the direction that makes a null look like a result.
`scripts/check_decomp_scorer.py` now feeds every scorer the gold transcript and
requires n/n on every row on every arm, with a negative group that requires the
same scorers to refuse the defects above, and a protocol group that asserts the
scorer reproduces each arm's own context line for line. It was red on D until
the hand-back was implemented.

**A fourth, in the corpus rather than the scorer.** The first fix for the arm-D
oracle echoed the whole span in the hand-back. That is forty tokens repeating a
line he wrote above, and it took the length cap's rejection rate from 22% to
**61%** — the cap rejects long trees, which is to say deep ones, so the corpus
lost three-turn conversations (5.1% to 0.1%), a fifth of its depth-2 trees, and
put `send` under its exposure floor. An index costs a tenth of the tokens.
Caught by reading the shape distribution `gen_decomp.py` prints, which no guard
would have flagged.

## What this licenses

Against §7's pre-registered table this is the second row — *"a lookup table over
trained trees; rung 2 does not run on this corpus; §5's sizing is wrong, not the
thesis"* — with one correction the table did not anticipate. **"Lookup table" is
too harsh**: a lookup table would fail on held-out entities, and B reads 71 and
77 there. He learned the shapes and can refill them with strings he has never
seen. What he did not learn is the rule that generates shapes.

So, precisely: **decomposition over a closed move set installs as a
surface form, generalises over slots, does not generalise over structure, and
is not read by the thing that acts.** The gate to rung 2 needed B above C on
the held-out rows and the forced probe reading load-bearing. Neither holds.

## Limits

Two seeds per arm, so directions rather than sizes (rule 6). The forced probe
tests one axis — the order of two children — and a label-swap forgery is a
different test that was not run. `parse.heldout` confounds held-out orders and
pairings with held-out carriers and reads zero either way, so the two cannot be
separated here; `parse.depth3` uses trained carriers and is the clean depth
read. The held-out rows are scored **unconstrained**, and `corn/grammar.py`'s
`ParseConstraint` — which forbids exactly the 63% of spans that are not in the
sentence — is implemented and not used by any scorer, so those zeros are an
upper bound on the failure and not a measurement of it. And these are nano
readings of a dummy world: nothing here transfers to real carriers by
measurement, which is what rung 2 was for.
