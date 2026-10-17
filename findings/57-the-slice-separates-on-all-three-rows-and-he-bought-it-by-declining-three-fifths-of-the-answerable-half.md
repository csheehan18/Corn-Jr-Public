# Fifty-seventh finding — the slice separates on all three rows, and he bought it by declining three fifths of the answerable half

**Cost:** 3.5 min of scoring on the 1 card first cited here (`nano20m_v3_extract`); it also reads 2 cards scored for an earlier finding (`corn_jr_260m`, `nano20m_v3`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`configs/nano20m_v3_extract.py` ×2 against `nano20m_v3` ×2. One source changes:
the extraction slice enters at 5% and web donates it, 49.3773% → 44.3773%.
Every other source is `mix_v3` verbatim, total held at 130,934,381, no `repeat`
anywhere. Trained 2026-08-24/25, ~1,160s per seed.

**27 of 27 pre-existing rows reproduced identically on both control seeds
before anything was read.** The control checkpoints are from 2026-08-19 and
were re-scored rather than retrained, so that check is what makes the
comparison a comparison; it is reported first here because it was run first.

## The three rows separate

| row | control ×2 | arm ×2 | |
|---|---|---|---|
| `extract.span` | 8-10/200 | **34-39/200** | disjoint |
| `extract.abstain` | 0-0/200 | **140-158/200** | disjoint |
| `extract.brevity` | 275-295/400 | **395-398/400** | disjoint |

Read as range against range, two seeds a side, which is the thirtieth finding's
rule and was pre-registered for this arm.

## The result that is not in doubt: confabulation is gone

    extract.span failures      control        arm
      invented                     105    ->    7 / 12
      wrote_own                     55    ->    3 / 4

That is the fifty-fifth finding's defect answered. The window said "19-year-old
Jourdan Miller" and the untrained model said "**21**-year-old Jourdan Miller" —
composing over a topic and supplying the number itself. 105 of 200 replies were
that. Now 7. `extract.brevity` at 395-398/400 says the same thing from the other
side: the replies became answers rather than paragraphs.

> **The `12` reads `13` under today's scorer** (added 2026-09-07, finding 127
> §4). The grounding rule changed at `e46ac9ee` and `invented` *is* "failed
> `grounded`", so one seed-2 reply moved out of `wrong_span` and into
> `invented` when the cards were re-derived from their saved generations. No
> verdict changed side and the pass count is untouched; the numbers above are
> what the scorer of the day said, and the claim they support — 105 to single
> figures — does not depend on the item.

**Nothing about that is explained by the caveat below.** An abstention and an
invention are both failures on `extract.span`, so trading one for the other
moves the row by zero. The row moved by 25-31 items, and `invented` fell by 98.

## The caveat: he abstains on three fifths of the answerable half

    extract.span failures, arm      abstained = 117-120 of 200

So on windows that **do** contain the gold, the commonest reply is "I couldn't
find anything useful." The plan pre-registered exactly this as the failure mode
with no runtime floor:

> A model that abstains on everything passes WS-C one hundred per cent of the
> time. Abstention is the incentive-compatible cheat, and no runtime check will
> catch it -- only `extract.abstain` scored against `extract.span` will.

It is not the pure cheat. The degenerate case is 100% abstention on both halves,
scoring 0/200 and 200/200; this model discriminates:

    P(abstain | unanswerable)     70-79%
    P(abstain | answerable)       59-60%
                                  ~15-19 points

Real signal, and weak. **Pooled into one number these two rows read 174-197/400
and look like a triumph**, which is why the plan said they must never be pooled
and why that instruction turned out to be worth having.

The honest summary of the behaviour change is that the failure mode moved from
*inventing a fluent wrong answer* to *declining to answer*. That is a large
safety improvement and a modest capability one, and the slice's balance is the
first suspect: `answerable` and `absent` went in 50/50, and 24,239 of the 48,478
transcripts teach that the correct reply to a window is a miss sentence.

## The falsifiable prediction could not be tested here

`continued_payload` was pre-registered as the cheap falsification — 69/400 on
the frozen `corn_jr_260m`, and the claim was that a corpus containing the shape
for the first time should collapse it.

    control seeds     0  and  24
    arm seeds         0  and   0

**The two control seeds disagree by more than the whole effect.** The row has no
stable baseline at nano and the arm's range sits inside the control's, so by the
rule this arm is read under, it does not separate. The 69/400 was a 260M number
and a 20M control does not reproduce the regime. **The envelope hypothesis is
untested, not confirmed** — it needs the 260M, where the failure actually exists
at a readable rate.

This is the thirtieth finding's lesson arriving on a new row: a floor is a
property of the arm it is scored on, and a prediction inherited from a different
model size is not pre-registered, it is transplanted.

## The regression watch caught something on one seed

    tool.copy        control 118-120/120     arm  100/120  and  120/120
    tool.copy_wide   control 281-291/300     arm  293-297/300   (UP)

Seed 1 lost 20 items to `wrong_answer`; seed 2 was perfect. The ranges overlap
at 120 so the rule says no separation, but the arm's floor is 18 items below the
control's and this is precisely the trade the arm pre-registered as its risk —
"a slice that teaches the model to *select* from an observation operates on
exactly the machinery that makes it *copy* one", the conversational slice having
taken `refusal.say` from 172/162 to 30 of 270.

`tool.copy_wide` rising argues against a general collapse of deference, so this
reads as one seed rather than a trend. It is not clean, and at 260M it is the
first thing to look at. Two seeds cannot tell a wobble from a trend, which is
the twenty-third finding's shape and is a limit of this arm rather than a result
from it.

## Everything else held

`temporal.copy` 353/353, `temporal.route` 399/400, `schema.conform` 191-195/200,
`refusal.say` 267-268/270, `chat.engage` 100/100, `tool.selection`,
`turn2.first` and `turn2.second` all overlapping. `tool.validity` rose
143-152 → 158-159.

`lm web` moved 0.8839-0.8867 → 0.8902-0.8923, about +0.006. **Pre-registered as
the donation being paid for rather than as a regression**, and it landed under
the +0.010 the forty-fourth finding's linear reading predicted from a 5-point
cut.

## What this does and does not license

The execution order says "260M only after the pilot separates from its control".
It separated, on all three rows, with the corpus's largest single behavioural
defect collapsing. That is the bar.

What it does not license is reading 34-39/200 as an extraction rate. The row is
an **upper bound** and says so in its own docstring; three tightenings were tried
against it and rejected in the fifty-fifth finding. What moved is movement.

The open question this arm creates rather than answers: **is the abstention rate
a property of the class balance or of the model?** The balance was pre-registered
at 50/50 before the slice existed, so changing it is a decision to be taken out
loud rather than a knob to turn after seeing a scorecard.
