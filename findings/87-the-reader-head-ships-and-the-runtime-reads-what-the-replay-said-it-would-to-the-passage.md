# 87. The reader head ships, and the runtime reads what the replay said it would to the passage

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**Run 2026-09-03 on the frozen `corn_jr_260m_v4_ft4g` trunk. No weight of the
trunk moves, no second checkpoint is loaded, `corn/extract.py`'s `reduce` and
`grounded`, `corn/gate.py`, every scorer and every frozen eval row are
untouched. This is `PLAN-EXTRACTION-READER.md` R3 — wiring, guards,
verification — and it contains no new experiment.**

The eighty-sixth finding measured a reader on Population A by replay: a
harvest of spans and margins, replies rendered by the probe, `reduce` called
directly. What it could not say is whether the *runtime* reads the same way,
because between that harvest and a live turn sit `harness/backends/read.py`,
`corn.extract.read_passage`'s own cut and prompt build, the trunk run live in
fp32 rather than replayed off an fp16 store, and a second `reduce` call for
the fallback. This file closes each of those and then reads the whole thing
end to end.

## What ships

    span head      checkpoints/reader_built_s1.pt   where the answer is
    verifier head  checkpoints/nullpr_s1.pt         whether it is spoken
    extent rule    d = 2.0, radius 3                where the span ends
    reduce         hybrid (finding 84)              how N windows become one
    threshold      -2.02                            when he speaks at all

`corn/reader.py` is new and holds all five: `SpanHead` (the built arm's pair
scorer — pointer term, LayerNorm per layer chunk, width embedding, bilinear
product, hidden 512 over the concatenated block outputs at layers 8, 12 and
16), `VerifierHead` (the pair-rows null head — the say marker's row, the
argmax pair's own two rows, the three standardised scalars), `extend`, and
`HeadReader`, which is a `run` in `read_passage`'s sense: N prompts in, N
worker-shaped replies out. `harness/backends/read.py` gains
`Reader(reader="head")` and the hybrid's second `reduce` call;
`harness/serverconfig.py` gains `reader`, `reader_threshold` and
`reader_extent_d`. **`generate` is still the default.**

**Two owner decisions are recorded as decisions, not as readings.**

  * **The threshold protocol is the bar's own shape** — the `t` that maximises
    `right` on the training fold among those holding that fold's share of 200
    correct silences — and not the `joint` optimum every earlier Population A
    number was quoted at. The eighty-sixth finding is why this is decidable
    rather than a preference: the joint optimum sits in a band up to 158
    thresholds wide across which `right` and correct silence trade by up to
    thirty passages, so `joint` does not choose. The two cross-validated fold
    values are **-1.980 / -2.061** and the shipped constant is their mean,
    **-2.02**, the way `train_null_head.py` ships a frozen file's mean.
  * **Seed 1's heads ship.** Seed 3 read higher on Population A (400 right at
    201 silent against seed 1's 389 at 199) and Population A is the population
    the arm is *measured* on, so choosing the seed by that number would be
    selecting on the test population. Seed 1 is the seed the workstream ran
    first and the one whose verifier bar (f) passes on both files.

## (a) The live reader reads what the harvest read, to the window

`scripts/check_reader_popa.py`, a new guard. Every window of Population A
through the wired `HeadReader` with the extent rule off — the harvest was
written at `d = 0`, so comparing a widened span against an unwidened one
would measure the rule rather than the wiring — against
`evals/results/nullpr_s1_popa.json`, the file every eighty-sixth-finding
number on this arm was replayed from.

    windows compared                         3,893 of 3,893
    spans string-identical                   3,893   100.00%   (bar: >= 99%)
    windows disagreeing                          0
    worst margin gap                         0.00152
    median margin gap                        0.000171
    mean margin gap                          0.000222
    spans the extent rule widens at d = 2      334   8.6%      (printed, unbarred)

**Nothing disagrees.** The four differences between the paths — fp16 store
against a live fp32 trunk, hooks registered per read rather than for the life
of the process, windows bucketed into batched forwards rather than read one at
a time, and a re-tokenisation on the runtime's side — move the margin by at
most 0.0015 of a logit and move no argmax at all. The tolerance is quoted
rather than asserted because it is a float that has been through a different
rounding on each path; the span is a string and is the bar.

## (b) The runtime, end to end, at the shipped constant

`scripts/probe_reader_runtime.py`: the real `Reader(reader="head")` handed
`(question, passage)` 1,003 times, whatever comes back scored by
`probe_reader_passages.judge` — `score_extract_tight` on `reduce`'s output,
the scorer every arm on this population has been read on, unchanged.

    arm                 answerable 721            unanswerable 282
                     right  wrong  silent      silent  wrong   joint
    gate on (recorded) 230     99     392        256     26      486
    gate CV            282    169     270        227     55      509
    head (runtime)     389    188     144        200     82      589

    gate on (recorded)  precision 64.8%, acc|att 0.699, attempt rate 45.6%
    gate CV             precision 55.7%, acc|att 0.625, attempt rate 62.6%
    head (runtime)      precision 59.0%, acc|att 0.674, attempt rate 80.0%

    the hybrid fallback fired on 88 of the 1,003 passages

**389 right at 200 correct silences**, against the eighty-sixth finding's
replay of 389 at 199. One passage of correct silence is the whole difference
between the replay and the runtime, and it is a rounding of the margin
against a threshold, not a disagreement about a reading. `INDEPENDENT-READ.md`
§5.1's rule is the reason the last three columns are there: the attempt rate
goes 62.6% → 80.0%, so this is an arm that speaks much more often, and
`acc | att` 0.625 → 0.674 says it is also right more often when it does.

## (c) Paired against the gate, and the trade

McNemar on the joint bit — a right answer on an answerable passage or a
silence on an unanswerable one — passage by passage, both gate arms named
rather than inferred. `evals/results/multiwindow_ft4g.json`'s `on` verdicts
are the arm recorded at `t = -0.082`; the CV'd gate at joint 509 is the policy
`corn/gate.py` carries today, recomputed here from the same gate harvest by
`probe_reader_passages.cross_validate`.

    against                net    lost   won    p
    gate on (recorded)    +103     99    202    2.9e-09
    gate CV                +80    103    183    2.6e-06

**And the trade, stated rather than netted.** Against the CV'd gate — the
policy that actually ships — the head reads:

    right answers          282 -> 389     +107
    correct silences       227 -> 200      -27
    precision             55.7% -> 59.0%   +3.3 points
    acc | att             0.625 -> 0.674
    attempt rate          62.6% -> 80.0%

**It buys 107 right answers and spends 27 correct silences.** That is a real
cost and it is the owner's ordering rather than an accident: `R-T` says speak
first, and the bar this workstream is written against is *`right` subject to
`silent >= 200`*, which 200 meets exactly and no more than exactly. It is
also 103 passages the gate got and this arm does not, against 183 the other
way — the net is not the whole story and both halves are printed above. A
reader who wants the conservative arm has `--reader generate`, unchanged.

## (d) Invariance: no scored number on the card moves, and the extract rows do not either

`python -m corn.evals --json` on `corn_jr_260m_v4_ft4g`, the reader wired,
against `evals/results/corn_jr_260m_v4_ft4g.json`:

    behaviour rows byte-identical            45 of 54
    rows present only in the fresh card       8   social.* x6, extract.span_loose,
                                                  extract.span_tight
    rows whose content differs                1   extract.span
    lm / contamination / selection            identical
    val_loss / iter / config                  identical
    variety / register / chat_reply /         identical in every scored value;
      turn2_reply                             they differ in `seconds` alone

**The one row that differs did not move its verdict.** `extract.span` reads
`pass 97 of 200` on both cards; what changed is the `why` breakdown, because
the scorer gained two reporting categories in an earlier session and 49
`wrong_span` is now 34 `wrong_span` + 10 `near_miss_clip` + 5 `near_miss_det`.
The eight new rows are `evals/`'s own growth since that card was written --
`docs/ENVIRONMENT.md`'s known confound, that a card written after an eval
rebuild carries rows the ones before it do not.

**And the plan's expectation that the `extract.*` rows would move as a new
column beside the old is wrong, for a reason worth writing down: the
scorecard has no reader in its path at all.** `corn/evals.py` scores
single-window items by decoding the trunk directly; it never calls
`read_passage`, never builds a `Reader`, and importing it loads `corn`,
`corn.evals` and `corn.temporal` and nothing else -- no `corn.reader`, no
`harness`. So there is no `--reader head` column to write on the card, the
frozen rows are invariant to this session by construction, and the population
that *can* see the arm is Population A, which (b) reads. If the head is ever
to appear on a card, the card needs a whole-passage row it does not have.

## (e) The guards

`scripts/check_extract.py` grows a boundary-reader section, and every check in
it runs with no checkpoint anywhere near it:

  * **The ports are the trainer's, score for score.** `corn/` may not import
    `scripts/` (rule 29), so `corn/reader.py` carries copies of two heads and
    five helpers; the guard loads `CachedHead(built)`'s and `NullHead`'s own
    `state_dict` into them on canned states and asserts the outputs are
    **bit-identical**, the pair enumeration equal tensor for tensor, the three
    scalars equal, and the two state dicts key for key the same. Same for the
    token map: `corn.reader.token_bounds` and `window_region` against
    `corn/spangen.py`'s on a prompt whose window carries a quote and a
    backslash, and `corn.reader.bucket` against
    `harness.backends.read.bucket`. This is `corn/gate.py`'s arrangement and
    it is why the copies are safe to have.
  * **The extent rule on hand cases**: a longer span within `d` is spoken; one
    that scores past `d` away — the extension that walks into the next entity
    — is refused; equal-length extensions tie to the smaller `a`; nothing past
    three rows is reachable; `d = 0` is the argmax. And the rule against
    `probe_extent_frozen.extend`, the function the eighty-fifth and
    eighty-sixth findings measured, on five canned score patterns: same span
    every time.
  * **The threshold's direction**: a window exactly at `-2.02` speaks, one a
    hair below it declines and the passage abstains with the runtime's own
    decline behind it.
  * **The hybrid fallback fires on the disagreement reason and on nothing
    else**: two admitted windows extracting different grounded values fall
    back to the surest one; a passage nothing was extracted from still
    abstains; an agreed read never reaches the fallback.
  * **Flag off is the path that shipped** — not "similar": `Reader`'s own
    call and a direct `read_passage` return the same `(answer, reason)` tuple
    for the same canned worker, and with `reader="generate"` the head is never
    constructed at all.
  * **The decline on every refused window**: all 200 unanswerable items of
    `evals/extract.jsonl` pass `score_extract_abstain` under
    `decline_text(question, window)`.
  * **The constants are held equal**: `ServerConfig().reader_threshold` and
    `.reader_extent_d` against `corn/reader.py`'s, the way `gate_threshold`
    already is, plus the three nonsense configs `validate()` must refuse.
  * **Layering**: `corn/reader.py` imports `corn.gate` and `corn.toolgen` and
    nothing else from the package, both inside the runtime closure, so the
    reader moves with the harness when the repo splits and drags no generator
    with it. `scripts/check_layering.py` is green.

`scripts/check_reader_popa.py` is (a) as a guard, and is `check_all.py`'s
sixty-seventh -- the count was 66. **The full sweep reads 585 s over 67
guards, 91 s of it this one, and three guards fail: `check_churn.py`,
`check_copyable.py` and `check_social.py`.** All three fail identically at
`HEAD` (`b72ad908`) in a clean worktree with the same messages and counts, so
none of them is this session's: `check_churn`'s is the same
`extract.span_tight` re-derivation that (d) sees as a new row, and the other
two belong to the slice work another session has in flight. Reported here
rather than left for the next reader to attribute.

## (f) A live session, both readers

`scripts/probe_reader_live.py`, `probe_gate_live.py`'s fourteen questions
through the real provider, each passage read twice --
`Reader(gate=True, gate_threshold=-0.136)` and `Reader(reader="head")` --
with the provider's own lead sentence beside both. Transcript:
`evals/results/reader_live.md`.

    6 of 14 questions came back with a passage      8 read `no_results`
    the gate answered 3, the head answered 3
    questions one arm answered and the other refused: none

    question                        gate                 head
    what is the capital of laos     It's Vientiane.      It's Vientiane.
                                    1 of 4 windows       4 of 4 windows agree
    what is the population of       It's 138,772.        It's 138,772.
      reykjavik                     1 of 1               1 of 1
    what language do they speak     Looks like           It's Portuguese.
      in brazil                     Portuguese.          2 of 7 agree
                                    2 of 7 agree
    melting point of iron           None                 None
    treaty of waitangi              None                 None
    president of iceland            None                 None

**Nothing changes for the eight questions with no passage**, which is what
`PLAN-EXTRACTION-READER.md` §4 predicts and the reason it predicts it: the
reader only ever sees the window retrieval hands it, and `_web_search`'s lead
sentence is the floor either way. On the six that did return a passage the two
arms agree question for question -- and the one visible difference is the
mechanism the eighty-sixth finding describes, `capital of laos` going from one
window extracting `Vientiane` to **four of four agreeing on it**, which is a
reduce with more evidence under it rather than a different answer. The
provider returned fewer passages today than on the day `gate_live.md` was
written (six against nine); that is the day's retrieval and not the reader.

## Limits

One trunk, one seed of the shipped heads, fp32. Population A is nq-dev's own
paragraphs and the questions are NQ's; the live session is fourteen questions
and is not a population. The verifier's training saw the *fold* heads' argmax
rows and at inference it reads the deployed head's, which is the stacking
rule's usual cost, accepted rather than removed (finding 86's limits). The
threshold is a constant of a checkpoint and a population and not of the
model: the next trunk gets its own `scripts/probe_reader_passages.py` run.
`(a)`'s tolerance is a reading on this trunk and this harvest and would have
to be re-read on another. Nothing here measures packs, which is where the
extraction gains were expected to transfer and where no reader number exists
yet.
