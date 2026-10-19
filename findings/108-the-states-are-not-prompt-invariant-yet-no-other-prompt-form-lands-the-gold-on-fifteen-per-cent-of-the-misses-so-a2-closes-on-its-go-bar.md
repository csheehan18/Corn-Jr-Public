# The reader is sensitive to prompt wording, but no wording does better

**Full result:** The states the span head reads are not prompt-invariant: half the argmaxes move when the question is written once and four fifths when the JSON goes, yet no other prompt form lands the gold on fifteen per cent of the misses, and every one loses more right answers than it gains, so A2 closes on its go bar

`scripts/probe_prompt_forms.py`, 2026-09-04. Four prompt forms over
Population A's 3,893 windows, one forward each at the shipped layers, scored
by the shipped, untrained span heads `reader_built_s{1,2}.pt` on the same
candidate pairs; about four minutes of GPU in all. `evals/results/prompt_forms.json`.
Nothing trained, nothing shipped, `corn/reader.py` untouched.

## 0. The arm and what was pre-registered

`PLAN-READER-REPRESENTATION.md` A2, `READER-AUDIT.md` L16 and L17. The head's
states come from one prompt: the question on the `look up` line and again in
the call's `query`, the window escaped inside a JSON payload in the `obs`
slot, the say marker last. The trunk was trained to *speak* after that
string; whether it is the string whose mid-stack states best separate a gold
from its rival was an assumption. Three variants: **noquery**, the payload
without its `query` field (the question once); **prose**, the window as bare
text in the `obs` slot, no JSON; **exemplar**, two worked turns of the same
shape in front, drawn from `spans_nq.jsonl`'s positives by content-word
Jaccard on the question and never from the passage's own article.

The cheap read, as the audit wrote it: read the shipped heads off each
variant's states. **Kill** if every variant moves under 5% of argmaxes — the
states are prompt-invariant and the lever is dead. **Go** for a variant that
moves ≥ 5% and lands the gold on ≥ 15% of the `RANK_2_10` windows (the gold
in the shipped head's ten and not first) on both seeds, after which that
variant is harvested for training. Finding 107's anchor added the third
column: `RANK_1` windows the shipped head had right, and how many the variant
loses.

## 1. The control

`base`, `worker_prompt` as shipped, through the same code path: **the argmax
text equals the pairs harvest's on 100.0% of 3,893 windows on both heads**
(one window differs by whitespace on seed 2). Everything below is against
that.

## 2. The three variants

    form       moved            RANK_2_10 -> gold          RANK_1 lost            net
               s1      s2       s1          s2             s1          s2
    noquery    51.3%   48.9%    43/366 12%  43/401 11%     251/731 34% 216/700 31%  -208  -173
    prose      82.9%   86.2%    21/366  6%  20/401  5%     571/731 78% 579/700 83%  -550  -559
    exemplar   27.5%   26.9%    29/340  9%  50/383 13%      97/693 14%  66/654 10%   -68   -16

(`exemplar` skipped 169 windows whose prompt with two turns in front exceeded
the 512-token block; its denominators are over the 3,724 that fit.)

**The states are not prompt-invariant.** Writing the question once moves the
argmax on half the windows; taking the window out of the JSON moves it on
more than four fifths; two exemplar turns in front move it on a quarter. The
first kill does not fire on any variant. The representation the head reads is
strongly contingent on the envelope it was harvested under — the doubled
question and the escaped payload are part of what the states encode.

**No variant reaches the go bar, and none is close on the column that
matters.** `noquery` lands the gold on 11.7% / 10.7% of the misses against a
bar of 15%, and loses a third of the windows the shipped head had right.
`prose` lands 5.7% / 5.0% and loses four fifths. `exemplar` is the least
destructive — it changes the least — and lands 8.5% / 13.1%, losing 14% / 10%.
Net over gold-bearing windows every variant is negative on both seeds, from
−16 to −559.

## 3. What the read can and cannot say

It can say the lever is alive as a *representation* question: states this
sensitive to the prompt mean a head trained on `noquery` or `exemplar` states
would be a different head, not the same head with noise. It cannot say that
head would be better. The shipped heads were fitted to `base` states, so a
loss on every variant is the expected sign of distribution shift and not
evidence about the variant's ceiling; the audit's go bar was written knowing
that, which is why it asked only for 15% of the misses to land and not for a
net gain. The variants missed even that.

What would answer the ceiling is the arm itself: harvest the training
positives under a variant prompt (772 s, **38 GB**, which `F:` does not have
without the deletions `PLAN-READER-REPRESENTATION.md` §0.4 names), train the
built head, chain and read at the bar. The pre-registration does not license
it on these numbers, and this workstream's last six arms of "train a head on
different inputs" (100, 101, 102, 103, 106, 107) each landed within noise on
the population. It is not run here.

## 4. Verdict

**A2 closes on its go bar, both seeds, all three forms.** L16 (a) and (b) and
L17 are closed as cheap reads; the prior finding 98 put against exemplars
(the trunk copies them rather than abstracting from them) is consistent with
`exemplar` moving the fewest spans and landing the gold least on seed 1. The
one result worth carrying forward is the invariance one: the shipped head's
inputs depend on the JSON envelope and the doubled question, so **any future
change to `worker_prompt` re-harvests and re-trains every head**, which
`corn/reader.py` should say and does not.

## 5. On disk

`scripts/probe_prompt_forms.py` (new): the four forms with their own
candidate-region locators, the control's reproduction check, and the three
columns per seed; `--forms` selects a subset. `evals/results/prompt_forms.json`.

## 6. Limits

The shipped heads are the instrument, so every variant is read under
distribution shift; a trained head per variant is the arm, not this read.
`exemplar` used two exemplars chosen by Jaccard from a 30,000-window sample
of the positives and no relation matching beyond word overlap. `prose` puts
the window in the `obs` slot with no envelope at all, which the trunk never
saw in training, so its collapse is the least informative of the three. The
RANK_2_10 denominators differ by seed because the shipped heads' tens differ.
