# One hundred and fifty-first finding — the windowed interpreter passes G1 once a close he writes early in a cut view is no longer believed: arity 30 of 30 on both arm F seeds, depth 131 and 265 against the committed 77 and 128, arm S 0.87 and 0.87 against a bar of 0.85 — where the first read, believing those closes, failed two of three

**Cost:** four `probe_window.py` sweeps' worth of the 3080, about 50 min in all: the first read 13 min (07:57-08:10 on 2026-10-07, against a registered 20-25), the item-by-item re-decode of arm S seed 1 both ways about 4 min, a sweep that ran across the module's edits and was discarded 13 min, the read of record 11.5 min (09:45-09:56), and the residual re-decode about 2.5 min. The fix and its guard section were CPU, about 30 min.

ROADMAP G1, PLAN-TAG-LANGUAGE §6 rung 1, gate pre-registered in
`scripts/probe_window.py` before a line was decoded (e478ba2): the windowed
interpreter (`corn/window.py`, built d0f693d) on the probes' own items, on
arm F (`nano20m_v3_fw_armf`, both seeds) and arm S (`nano20m_v3_fw_steps`,
both seeds), every prompt decoded once through `probe_fast.FastLine`. **Cards
of record** (on 6b8626f): `evals/results/nano20m_v3_fw_{armf,armf_seed2,
steps,steps_seed2}__window.json` and `__window_items.jsonl`. The probe is a
hand-built instrument; the guard (`scripts/check_window.py`) pins the
interpreter, not the scorer, so **every number here is a bound** (rule 28).

## The reproductions held, both times

Every sweep first re-runs the committed instruments on the same items: depth
base 77, 128, 123, 124 of 420 and arity 30 at 29, 30, 29, 27 of 30, all four
exact, in both the first read and the read of record. So what moved between
them is the module, not the instrument.

## The first read failed two of three

    gate                               bar     F s1   F s2   S s1   S s2
    G1a arity 30, "all N"              >= 29     30     28
    G1b depth 6-15, levels right       >= band   94    265            (77, 128)
    G1c depth 6-15, gap rule on        >= 0.85                 0.65   0.75

The same sitting's diagnostic loop (`probe_depth_diag --mode gapc`, finding
145's) read arm S at 0.95 and 0.89 on the same decodes. The registered table
says what that licenses: compare item by item and name the departure; a
module fault is fixed with a guard group and re-read, never by moving the bar.

**Read by hand, arm S seed 1 re-decoded both ways** (same prompts, greedy, so
the first line of every item is byte-identical): the module was worse on 22
items of 48 and better on none, 275 against 399 levels. Every miss was one
shape: **he closes a group early in a view the window cut, and the module
believed the close.** Two forms:

* **Depth.** On the first view he writes `ask[the pair, ask[the capital of
  Nyrirthfell] and two things] ask[the chief export of Drounndholm]]` -- the
  next carrier, "two things", written flat and the group closed after it. The
  module read "and two things" as the group's trailing words, trusted the
  close because the next part was found, and resumed two levels up; the
  levels under "the pair" were never asked about again. The diagnostic never
  trusts a close at the edge of a cut view: it re-asks from the group's
  carrier, and on that view he writes `ask[the pair, ask[...] and two things,
  ask[...]]`, which the gap rule nests.
* **Arity.** On arm F seed 2's second view of the thirty-member list he
  writes four members, closes the group, and starts `ask[the chief export
  of` -- a member the window cut. That fragment was found in the request and
  vouched for the close, so the group ended at its eighth member and the
  other twenty-two were read as loose parts at the top (two lost on the way).

## The fix (6b8626f), held by the gold proof

In `corn/window.py`'s close rule (its docstring now says this): a part the
window cut is a fragment and vouches for no close in a group view, unless the
close was marked by its own trailing words; trailing words that a comma
follows, on a lookup group with a carrier, in a cut view, are a flat carrier,
and the group is asked again from its carrier; and a flat carrier right after
a close not yet trusted re-asks the closed group rather than re-showing the gap
one level too high.

`check_window.py` section 10 replays both real lines inside an otherwise gold
run: the module as built reads 2 of 7 levels and 8 of 30 members, the fixed
one 7 and 30. **The gold proof still holds everywhere** -- a writer who writes
every view's gold parse gets every tree back, on all 20,370 arm F corpus turns
and 450 fresh requests at window 50 and the other four settings. Two drafts
failed it and were dropped: never trusting any close in a cut view (the
diagnostic's rule taken whole) lost 74 of 450 fresh requests, and holding the
fragment rule in every view lost one arm F turn in 5,000 at window 24, a close
a gold writer marks with its trailing words (`ask[ask[X] on the other] ask[the
river through`) -- which the marked-close exception returns.

## The read of record passes all three

    gate                               bar     F s1   F s2   S s1   S s2
    G1a arity 30, "all N"              >= 29     30     30
    G1b depth 6-15, levels right       >= band  131    265            (77, 128)
    G1c depth 6-15, gap rule on        >= 0.85                 0.87   0.87

Beside it, recorded and not gated: on arm F the module now reads *above* the
diagnostic (131 against 78, 265 against 156); with the gap rule off it reads
79, 110, 102 and 107 -- so the gap rule is still where the depth is. On arm S
seed 1 the module still trails the diagnostic, 365 against 399.

**The residual is one shape, read by hand on all six items** where the module
reads less (S s1, re-decoded both ways on 6b8626f; better on none): he fuses
the carrier "twice over" into a member -- `ask[twice over, the river through
Fenunthholm]` -- and the module keeps it as one member of the group above, so
the chain breaks there (34 levels across the six). That is finding 145's wall,
the carrier word: "twice over" and "two things" are the carriers he does not
read as groups. The diagnostic gets past it only because it never trusts the
close that follows. A gap rule inside a member would be the next repair; it is
not needed for the gate and is not made here.

## What it licenses

* **G1 is done**: the module carries what the probes measured, the gate
  passes on all four checkpoints with the reproductions held, and it is the
  interpreter H3 serves if D7 takes views. G5 (workers and composition) no
  longer waits on it.
* **A close he writes at the edge of a cut view is not his word** -- the rule
  the diagnostic had implicitly, now explicit, with the gold writer's marked
  closes as the one exception.

## What it does not say

That the interpreter is right on real requests: these are the probes'
synthetic chains and lists, and finding 146's misfire read (the gap rule on
450 fresh requests, 0 broken) was made on the module before this fix -- the
gold proof says the fix refuses nothing legal, not that he writes what it
needs on fresh text. Anything at 260M. Anything about `twice over` beyond the
six items read.
