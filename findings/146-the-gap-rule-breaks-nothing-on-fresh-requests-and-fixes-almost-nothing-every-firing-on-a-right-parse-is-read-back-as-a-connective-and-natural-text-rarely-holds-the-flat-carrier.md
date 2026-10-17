# One hundred and forty-sixth finding — the gap rule breaks nothing on requests it was not designed on and fixes almost nothing: every firing on a parse he had right comes back a connective, the few groups it opens at a non-carrier all land on parses already wrong, and natural requests rarely hold the flat carrier that made it worth 0.95 on the chains

**Cost:** 6.5 min of GPU for the whole read (19:39-19:46, about 95 s a checkpoint over 450 requests, 510-528 decodes each with the memo), no training; the set, the scorer and its CPU checks took a few minutes without the card.

PLAN-PARSE-WEIGHTS section 8.2, read 2026-09-26 -- ROADMAP step X1.
Pre-registered in `scripts/probe_gap_misfire.py`, committed at `df45bf0`
before a line was decoded, the bar set by the owner. 450 fresh requests from
arm F's own generator at seed 20260930 (`evals/funcworld_gapfire.jsonl`), which
nothing had read; 300 at the trained level are the gate, 150 at `heldout_all`
are read. One greedy parse a request, the one-member wrapper unwrapped in both
arms, and the rule of finding 145 applied to every group he wrote -- `gapc`
firing only on a gap that ends in a comma, `gap2` on any gap beyond "and" and
commas, each falling back to the flat member when the re-shown text opens no
group. Scored on gold groups as sets of lookups, with and without the rule, on
identical decodes (committed: `evals/results/nano20m_v3_fw_*__gapfire.json`).

## The pre-registered read

On the 300 trained requests:

    checkpoint   right without   gapc broken / fixed / fired   gap2 broken / fixed / fired
    S s1             175              0 / 0 / 8                    0 / 0 / 64
    S s2             169              0 / 0 / 7                    0 / 1 / 50
    F s1             185              0 / 0 / 7                    0 / 0 / 59
    F s2             174              0 / 0 / 6                    0 / 0 / 45

**`gapc` breaks 0 of 300 at both arm S seeds against a bar of 6, and fixes as
many as it breaks: it passes as registered**, and so would `gap2`. On
`heldout_all` each rule fixes one item on S seed 1 and breaks none anywhere.

## What the lines say

**On parses he had right, the rule cannot hurt.** Across the four
checkpoints `gap2` fired 15 to 25 times on items that were already right, and
**every one of those re-shown views came back a connective** -- he wrote the
re-shown text as a single lookup, and the member went back where it was. `gapc` barely fires there at all (0 or 1).

**The groups it opens at a non-carrier all land on parses already wrong.**
Where his first line had moved members between groups, the gaps hold material
that is not a connective, and re-shown they can open a group that is not in
the gold -- "and, separately," read as a carrier (train-014), "on top," as one
(S s2 train-180). None of these is counted as a break because none of those
items was right to begin with; the count of zero is honest about the rule and
says nothing about how such a line should be repaired.

**Most of what it opens, it cannot place.** Three times (train-053, -192,
S s1) the re-shown view recovers a group the gold really has -- "question, A,
B and C", "care to tell me A, B and C" -- but his first line had swallowed that
group into its neighbour, and the rule can only nest inside the group he
wrote. It never splits a group into siblings, so the item stays wrong.

**The fixes are the finding-145 case, on natural text.** Two items become
right: `heldout_all-033` on S seed 1, where "the both of them," -- a carrier
held out of training -- was written flat and, re-shown, opened; and train-280
on S seed 2, where "both" did the same. The mechanism works on a carrier
nobody drilled. It simply has little to work on: the rule touched 8 to 12 of
roughly 200 wrong parses under `gapc` and 37 to 44 under `gap2`, and the
failures that fill the rest are other species.

## What it does not say

That the rule is worth building for 1.0. It is safe and nearly inert on the
requests this generator writes, which hold a nested group in 47 of 300 and a
deep chain of carriers in none; its 0.95 on the depth probe (finding 145) is a
property of long carrier chains, a shape no fresh request here has. Nano, the
synthetic world, one greedy decode a request; the scorer is a hand-built
instrument checked on gold (450 of 450) and on a stand-in model, not pinned --
every number is a bound.

**Licenses** keeping the rule as a cheap, safe part of the windowed
interpreter if that interpreter is built (PLAN-TAG-LANGUAGE rung 1), with
`gapc` preferred because it fires about eight times less for the same result,
and **not** spending more on depth until something shows real requests need it
-- which is ROADMAP decision D7's to weigh, not this finding's.
