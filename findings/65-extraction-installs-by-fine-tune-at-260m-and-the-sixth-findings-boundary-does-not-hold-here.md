# Sixty-fifth finding — extraction installs by fine-tune at 260M, and the sixth finding's boundary does not hold here

**Cost:** 12.5 min of scoring on the 1 card first cited here (`corn_jr_260m_ftnarrow`); it also reads 1 card scored for an earlier finding (`corn_jr_260m`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

WS-G, run 2026-08-26. One fine-tune from the frozen `corn_jr_260m`, 786
iterations, ~15 minutes. `configs/mix_wsg_ft_extract.py` carries the
pre-registration. **It lands on outcome 1, which the config registered as the
least likely of its three.**

## The question, and why a null was the expected answer

`corn_jr_260m` had **never seen an extraction transcript**: `mix_v3_5b` carries
eight sources and `extract` is not one of them. So unlike P3-B2, which surfaced
a routing capability the base already had at ~35 passes, this asked a fine-tune
to *install* a capability that was not there — the sixth finding's failure
mode, registered as the expected outcome rather than the feared one.

The argument for trying anyway was that the half finding 6 lost is already at
ceiling here: `tool.copy` 120/120, `tool.copy_wide` 300/300, `temporal.copy`
353/353 on the base. Reading an answer out of an observation rather than out of
the weights is fully installed; what extraction adds is a longer observation
and a span-**selection** step that nothing in the corpus teaches.

**The control is `corn_jr_260m_ftnarrow`** — P3-B2's narrow arm, trained from
this same base on this same tool payload with no extraction in it, already
scored. It cost no card time and it is what separates "extraction data did
this" from "any fine-tune does this".

## It installs, and the control shows most of it is the extraction data

    row                  base    ftnarrow   ftEXTRACT   attributable
    extract.span        9/200      22/200      70/200        +48
    extract.abstain     0/200       1/200     141/200       +140
    extract.brevity   133/400     243/400     397/400       +154

The control moves the rows a little — a tool fine-tune alone takes `span` 9 to
22 and `brevity` 133 to 243 — and the extraction arm goes far past it on all
three. **`extract.abstain` is the sharpest: 0 and 1 against 141.** The base and
the control essentially never produce a miss sentence; the arm produces one on
seven of ten unanswerable windows.

**Nothing was spent.** Rule 10's watch is clean at the ceiling, which is the
strongest form this project can run it:

    tool.copy       120/120   unchanged     temporal.copy   353/353   unchanged
    tool.copy_wide  300/300   unchanged     temporal.route  400/400   unchanged

The sixth finding lost `temporal.copy` to a fine-tune under 1:1 replay, down to
48.2–66.3%. This corpus replays the whole v3 mix on `mix_p3a_ft.py`'s terms and
`temporal.copy` does not move by one item. **So finding 6's boundary is not
where it was drawn.** Installing *deference* by fine-tune failed in a
TinyStories-based model that had never seen a `<|call|>`; installing
*extraction* over deference that is already at ceiling does not.

And the routing gains survive on half the tool exposure: `search.route_*` reads
200/200, 200/200, 200/200 against the control's 200/199/200, with
`tool.selection` identical at 187 and `tool.validity` 179 against 181.

## The fifty-seventh finding's caveat reproduces, and is milder

WS-B's nano arm bought `extract.span` by declining three fifths of the windows
that did contain the answer. That happens here too and must be read with the
row rather than after it:

    ftEXTRACT  span failures   abstained 80   wrong_span 37   invented 11
    ftnarrow   span failures   invented 63    wrote_own 43    continued_payload 35

**Confabulation collapses — `invented` 63 → 11**, which is WS-B's result again
(105 → 7). And the arm declines on **80 of 200** answerable windows, 40%,
against the nano arm's ~59%. Better, and still the dominant failure mode.

**It is not the degenerate cheat, and this is the number that says so.** He
attempts an answer on 120 of 200 answerable windows (60%) and on 59 of 200
unanswerable ones (29.5%) — **twice as likely to try when the answer is
actually there.** WS-B measured 70–79% against 59–60% on the same comparison,
so the discrimination here is wider, not narrower.

**Do not pool `extract.span` and `extract.abstain`.** Pooled they read 211/400
against the base's 9/400 and look like a rout. The fifty-seventh finding's
instruction stands and this run does not weaken it.

## What this cannot say

**One seed.** Nobody has measured seed variance at 260M — the sixty-first
finding's whole subject. The effects here are large (+140 on `abstain`, +154 on
`brevity`) and not plausibly noise; anything small in this table is not
readable.

**The payload is half tools and half extraction**, so the arm saw half the tool
exposure the control did. That is a confound for the routing rows and not for
the extraction rows, which the control has no extraction data to move at all.

**It says nothing about a pretraining mix.** This is a fine-tune result, and
the sixtieth finding measured that vehicle delivering 61% of a mix's effect on
a different payload.

**And the 40% decline on answerable windows is unexplained here as it was
there.** Findings 58 and 59 retired four hypotheses for it — class balance,
gold position, corpus type frequency, the scorer — without finding a cause. The
`other` answer-type decline sat at 86–92% across six checkpoints and nothing in
this run addresses it.

## What follows

**The chain has four working links for the first time.** Recognition was
53/200 on real subjects and is 198/200 (sixty-third finding); retrieval was
never broken; reduction was throwing away a third of what it retrieved and now
keeps it (`_best_answer`, same day); and extraction was 9/200 and is 70/200
with abstention at 141/200.

Two things follow immediately, neither costing a training run:

  * **`--extract` now has a model behind it.** The flag, `PASSAGE` and
    `read_passage` were all built against a capability that did not exist. It
    does now, and a live read is the obvious next measurement.
  * **The 40% decline is the binding constraint on this link** and is the
    thing worth an instrument rather than an arm — WS-F's territory, parked in
    `PLAN-WEB-SEARCH.md` on the argument that link one was failing. That
    argument has expired twice over.
