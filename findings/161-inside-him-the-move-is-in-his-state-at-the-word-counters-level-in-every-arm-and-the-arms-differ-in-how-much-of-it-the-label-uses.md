# One hundred and sixty-first finding — probe C, inside him at the move decision: a linear reader on his own state reads 46 to 55 of 100 far phrasings at all eight checkpoints, at the word counter's level and 15 to 35 over an untrained net of his shape, while he writes 12 to 40; six checkpoints read built and overridden and A3b's two read between, so the registered verdict is split -- the arms differ in how much of the state the label uses, not in how much is there, and what A3b misses is mostly not in its state

**Cost:** 140 s on the card for the registered read and 140 s for the post hoc prior-keeping read (both contended, the card at 39-40% before each -- bounds); the CPU sweep before the pre-registration commit 188 s; hand and post hoc reads off the card under 10 s; 13:14-13:29 on 2026-10-11 end to end, build included.

Asked by the owner on 2026-10-10, after finding 159's amendment read the
far-phrasing limit from the outside -- the word counter right on 75-82% of
cue-covered items, he on 25-54% -- and called it size more than meaning.
The outside cannot say *where* the evidence is lost: never in his state
where he decides, or in it and overridden by the label he writes. This reads
the inside. Pre-registered in `scripts/probe_move_inside.py`'s docstring and
committed at e6f4c64 before any state was read.

## The instrument

At the **decision position** -- the last token every `move: <value>` line
shares after the route prompt, which ends on `move:` (the value token carries
its own space; no boundary merged on any prompt) -- his residual state is
read at ten places: the embedding sum, the eight blocks, `ln_f`. A linear
reader (multinomial logistic regression, balanced classes, L2 1e-2 on
standardised features) is fit per place on every distinct user line of the
slice that checkpoint trained on (3,985 to 6,854), 80% to fit and 20% to
choose the place, rendered as the unseen items are. It reads
`HELD_OUT_PROBE`'s 100 phrasings of the five families every arm trains --
far phrasings by construction (`check_moveline.py` section 8). Beside it: his
own tag off the committed A3 items file (O), the same protocol on a randomly
initialised net of his shape (F, seed 0), the word counter (W), and the
reader with its training labels shuffled (S). Card
`evals/results/move_inside.json`.

## The registered read

    checkpoint        O    R (place)   F    W    S    he wrong   reader right there   reading
    A3 on 1337        32   49 (6)      20   48   20   68         22                   built, overridden
    A3 on 2337        20   55 (5)      20   48   14   80         36                   built, overridden
    A3b   1337        40   47 (5)      32   53    9   60         15                   between
    A3b   2337        38   48 (6)      32   53   20   62         16                   between
    cap   1337        24   49 (5)      26   53   11   76         26                   built, overridden
    cap   2337        15   48 (4)      26   53   20   85         34                   built, overridden
    rep   1337        22   47 (7)      25   53   16   78         29                   built, overridden
    rep   2337        12   48 (6)      25   53   16   88         37                   built, overridden

**Neither stop fired**: S is 9-20 against a stop of 30, and every decision
prefix ends on `move:`. **The verdict is split** -- *built, overridden* at six
of eight, and the registration needed both A3b seeds in the reading; A3b's
two read *between* (R over O by 7 and 10, under the bar of 15). Read per arm,
as registered: A3, cap and rep hold the move in their state and write their
default over it; A3b writes most of what its state holds.

**The floor is a real floor.** F (20-32) sits 15-35 under R at every
checkpoint and 21-28 under W, so the move read in his state is something
training built, not what any net mixing these tokens carries; the
*reaches* case (F within 5 of W) never arises. The embedding row -- at a
fixed token, so position and nothing else under learned positions -- reads
10-23. By place, the reader is at 39-47 after the first block and level from
the third (the per-place rows are on the card): the move is gathered early
and carried to `ln_f` (45-53 there), right under the head that writes the
label.

## Read by hand, and four post hoc reads (not registered)

**The reader's wins are the readable ones** (A3b 1337, `--hand`): "top of
the morning" greeting where he writes `consolation`, "i've had better weeks"
consolation where he writes `share`, "duly noted" ack where he writes
`consolation`. At rep 2337, where he writes `open` or `share` on most items,
the reader reads ack on "loud and clear", "no argument here", "fair play",
"seems reasonable", "no objections" -- one item in the other direction
("grateful for that": he thanks, the reader ack).

**1. A reader that keeps the slice's prior reads the same** (`--prior`, card
`evals/results/move_inside__prior.json`): R 46-55, every reading and the
verdict unchanged. The lead is not the balancing.

**2. The default is in his label, not in his state.** His commonest label
takes 34-66 of 100 at six checkpoints (A3 1337 `greeting` 44, A3 2337 `open`
66, cap `open` 34 and 61, rep `open` 40 and `share` 42); the reader's
commonest takes 16-25 everywhere. A3b is the arm without a large default
(`consolation` 26, `ack` 19) -- finding 159 read its defaults on the 120
items with `farewell` in, where they are `consolation` and `farewell`.

**3. How much of the state the label uses** -- of the items the reader gets
right, the share he also writes right:

    A3 on    27/49  19/55        cap    23/49  14/48
    A3b      32/47  32/48        rep    18/47  11/48

A3b's lift over A3 in finding 159 (unseen 40 and 38 against 32 and 20) is
this column: the label using more of what is there, not more being there
(R 47-48 against A3's 49-55).

**4. What is not in the state is the same size everywhere.** Items both the
reader and he get wrong: 44-51 of 100 at all eight checkpoints (A3b 45, 46).
On those they write the same wrong label 20-31 times -- not an A3b property.
By finding 159's cue split: where a cue word points to the gold, the reader
reads 18-28 of 28-45 against the word counter's 21-35; where none does, 19-36
of 55-72 against 18-27, at or above it at all eight -- differences of a few
items, no claim.

## What it licenses

* **Finding 159's "size more than meaning" is located, and it has two
  layers.** The words' evidence reaches his decision point as a move he
  built, at about the word counter's level, in every arm. On top of that,
  the six non-A3b checkpoints write a default over it -- a readout
  loss of 17-36 items. A3b nearly closes the readout loss; what it still
  misses (about 45 of 100) is not in its state, linearly.
* **For the move line (D7)**: the arm that would ride is limited by the
  state, not the readout. The registered next step for *built, overridden*
  -- adding the reader's direction and seeing whether his label follows --
  would buy A3b 15-16 items at most, so it is not the next lever there.
  The next lever is what the state holds: finding 159's two untested ones,
  more distinct evidence per cue or a larger net (D11's pilot), and this
  probe is the read to put on that pilot.
* **For the owner's question -- what separates memorising from the idea**:
  on far phrasings the idea is in him at the level of the words and no
  further, at nano, one pass. The torn-page read (each wording in or out of
  training on random halves) is the third definition, not run.

## What it does not say

That he can use what the reader finds -- only an intervention shows that, and
it was not run. That the 45 items are absent from his state: a linear reader
fit on the trained lines missed them; a nonlinear one or a different place
might not. Anything at 260M (finding 51). One floor seed; two seeds an arm;
an instrument with no guard -- every number here is a bound (rule 28).
