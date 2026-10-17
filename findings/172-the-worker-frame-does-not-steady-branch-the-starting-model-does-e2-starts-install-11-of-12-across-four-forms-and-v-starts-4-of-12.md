# One hundred and seventy-second finding — the worker frame does not make branch reliable, and neither does what follows the pick; the starting model does: by fine-tune, arm E2's three starts install the binding on 11 of 12 runs across four trace forms and arm V's three on 4 of 12, while the forms read 3 to 5 of 6 each, inside their own noise

**Cost:** 24 fine-tunes of 650 iterations at 20M (143-144 s each, contended -- the card at 38-40%, a bound), the 12 start reads and 30 run reads at ~18 s, 24 `tool_copy_wide` cards at ~10 s, and a terminator re-score of the six worker runs (147 s): two chains, 11:35-12:12 and 12:20-13:00 on 2026-10-14, with ~35 min of CPU build beside them (11:31-11:35, 12:12-12:20).

**The owner's architecture, read cheaply.** After findings 169 and 171 (branch
installs in two pretraining runs of four, at 20M and 50M, each all or
nothing), the owner proposed that the main instance only speak and that
decomposing, calling and picking go to scoped workers, each in a fresh short
context (SPEC-LANGUAGE §8's frames, taken further). Its central claim, read
here: **a decision made in a short frame installs where the same decision at
the end of a long turn is a coin.**

**Two pre-registrations, both committed before a byte trained.** The
worker-frame test (`configs/mix_v3_branch_ft_worker.py`, 240c0b1): the same
7,424 branch decisions in a full turn (~431 tokens, the pick ~400 after the
frame's wording) against a worker frame (~147 tokens: the conditional part,
the runtime's lookup and result, the check, the menu, the pick). Each arm is
read twice over by fine-tune (650 iterations, the rest arm E2's mix as
replay, `lr` 2e-4) from six starts that never saw a branch -- arm E2 and
arm V (`filter_view`) at three seeds each. A run installs when its held-out
quads clear 14 of 144 on each side (finding 169's gate). Then the cause arms
(`configs/mix_v3_branch_ft_worker_conseq.py`, 96a52a5): the worker frame
followed by the full turn's lines after the pick (`worker_conseq`), and the
full turn cut at the pick (`full_cut`). `check_branch.py` sections 6 and 7
hold every form trace for trace against its parents. **Cards:**
`evals/results/nano20m_ft_branch_{full,worker,worker_conseq,full_cut}_{ev2,ev2s2,ev2s3,view,views2,views3}__branch*.json`,
`__copywide.json`; the starts' reads on each row file.

## An instrument hole first

`probe_branch.py` scored each option as `pick: next[X]` plus a newline. In
the full turn a newline does follow the pick; in a worker frame the pick is
followed by `<|end|>` in training and a newline never. On the worker arm that
unseen token moved more quads than the choice did: the worker arm read **1 of
6** with the newline and **3 of 6** with `<|end|>` (scored with no
terminator, identical to `<|end|>`, since `<|end|>` costs both options the
same). Fixed and guarded the same day: every row carries `after`, what follows
a pick in its form; the probe scores with it; `check_branch.py` sections 6 and 7
hold it against each payload. Every number below is on the fixed scoring. The
starts read 0-3 quads on every form's rows (readable).

## The registered reads

    held-out quads (first side / second side, of 144); a run installs above 14 on both
    start          full        worker      worker_conseq   full_cut
    E2  1337      68  91 ✓    27  27 ✓     70  31 ✓        67  70 ✓
    E2  2337      84 108 ✓    56  14       58  41 ✓        90  65 ✓
    E2  3337      70  65 ✓    29  16 ✓     27  17 ✓        75  42 ✓
    V   1337      62  81 ✓    56   7       64  10          73  53 ✓
    V   2337       2   1       0   1        4   2           6   1
    V   3337     106 135 ✓    40  17 ✓      6  15          21  12
    installs       5 of 6      3 of 6       3 of 6          4 of 6

**The worker-frame test lands on its rows "worker 4 or fewer -- the frame is
not enough" and "full above worker by 2 or more -- read by hand".** The
prediction on the record (worker 6 of 6, full 2 to 4) failed both ways. **The
cause arms land on no row**: the table asked for 5+ against 3 or fewer, and
3 and 4 are neither. The prediction (what follows the pick is the cause) is
not supported.

**And none of the form differences is readable.** At six runs an arm, 5 of 6
against 3 of 6 is about an even chance by Fisher's exact test (two-sided p ≈
0.55). Pooled, the forms with the declaration and status ask before the
conditional (full, full_cut) install 9 of 12 and those without (worker,
worker_conseq) 6 of 12. The forms with the consequence (full,
worker_conseq) install 8 of 12 and those without 7 of 12. Neither split is
readable either.

## What the table does say: the start

    installs by start, over the four forms
    E2  1337   4 of 4        V  1337   2 of 4
    E2  2337   3 of 4        V  2337   0 of 4
    E2  3337   4 of 4        V  3337   2 of 4
    E2 starts  11 of 12      V starts  4 of 12        (Fisher p ≈ 0.01)

**Which model the fine-tune starts from decides whether the binding forms,
far more than which frame it is taught in.** Arm E2's three starts take branch
in 11 of 12 runs across all four forms. Arm V's take it in 4 of 12, and its
seed 2337 in none of four, every form reading 0-6 quads. Within E2 the forms
read 3, 2, 3 and 3 of 3. Within V they read 2, 1, 0 and 1 of 3. Arm V is arm E2
plus the runtime's item view after every observation in the filter payload
(finding 151's views) -- one rendering difference, and the start that has it
learns a menu pick after an observation a third as often. Why is not read
here.

Two further things in the rows, side columns:

* **The short forms are weaker on the second side** -- "find me {b}, but if
  {c}, {a}", where the conditional continuation comes second. V-1337 reads
  56/7 in the worker frame and 64/10 with its consequence, against 62/81 in
  the full turn and 73/53 cut. With the status ask in front, the conditional
  continuation is further from the user line's start in every frame. Read
  only that far.
* **No form reads a wording it never trained**, beyond scattered single
  cells (worker_conseq E2-2337 29 of 48 on the first side; the full turn
  16-31 of 48 on the second side, five runs). Finding 169's "a table of
  eight wordings" holds by fine-tune too.

**The copy row, a side column**: 279-298 of 300 over the fine-tunes, inside
the 20M family's spread (finding 170); nothing is readable as a cost.

## What it licenses

* **The worker architecture's central claim is not supported on branch.** A
  short frame does not make the pick reliable here, and it is not shown to
  hurt beyond noise. The case for workers has to rest on what they were also
  proposed for -- keeping tool output out of the main window, one job per
  frame, results checked before the main instance speaks -- and not on making
  a 20M pick steadier.
* **By fine-tune from the right start, branch installs reliably**: 11 of 12
  on E2, every form. Findings 169 and 171's coin was pretraining from
  scratch at one pass and 2% of the mix. **One run, then amplify**
  (PLAN-1-0) is the route the record supports: the format in the corpus, and
  a fine-tune that drives it. What makes a start receptive (arm V's views,
  or something they stand for) is the open question, and it matters more
  for the ladder than the frame does.
* **For recover**: the same fine-tune from E2 starts is the cheap read of
  whether it can be his. Combine and recover were read only from scratch at
  one pass.

**What it does not settle.** The forms against each other at any useful
precision -- that needs about 15 runs an arm; why arm V's starts resist; and
whether a fine-tuned binding survives the next fine-tune.

## Amended 2026-10-14 -- the payload broke GENERATORS D8 (finding 173)

This arm trained `corn/branchgen.py`'s payload: "if" in eight wordings, each
seen ~928 times, and its own guard showed (wording, result) settling every
gold -- the lookup route GENERATORS §4 names as the sign of a list, and D8's
"near or under ten sightings" missed by two orders of magnitude. What it
measured is a memorisable slice: the "table of eight wordings" and the
zero on a ninth are what that slice predicts, and the seed, size and frame
comparisons here vary everything except the flaw. The rebuild to
GENERATORS is finding 173.

## Amended 2026-10-14 -- the start's p-value was overstated

"E2 starts 11 of 12, V starts 4 of 12 (Fisher p ≈ 0.01)" counts the twelve
runs as independent; they are four runs from each of three starts, and runs
from one start share it. Counted by start, every E2 start takes the binding in
three or four forms of four and no V start does in more than two -- three
against three, one-sided Fisher p = 0.05. Suggestive, not established. And
the fine-tune gave the payload ~40% of 650 iterations against pretraining's
2.2% of one pass, so "by fine-tune it installs" is not separated from "with
far more of it, it installs".

