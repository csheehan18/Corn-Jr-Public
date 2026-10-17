# Hundred-and-eighteenth finding — the shipped reading adapter survives the trunk moving under it: fitted to ft4g, it reads 521 of 721 at 196 correct silences on arm 3 (ft4g fine-tuned once) and 524 at 199 on arm 2 (a sibling trunk from the base), against 526 at 199 on its own trunk, with 27 and 9 passages moving and nothing paired significant

**Cost:** 16.0 min of scoring on the 2 cards first cited here (`corn_jr_260m_v4_ft_social2`, `corn_jr_260m_v4_ft_social3`); it also reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**Run 2026-09-05, `docs/PLAN-CONVERSATION.md` §4i, pre-registered the same
day before the number existed. Nothing trained. Two reads of Population A
through the real runtime, ~23 s of card each, plus the pairing off the
JSONs on the CPU. The adapter is `checkpoints/reader_whole_causal_s1.pt`
exactly as finding 117 shipped it; the trunks it is read on are
`corn_jr_260m_v4_ft_social3` (ft4g init, one 1,200-iteration fine-tune)
and `corn_jr_260m_v4_ft_social2` (v4-base init, ft4g's recipe with one
source swapped). `corn/`, the server, every scorer and every frozen row are
untouched; the runtime still refuses this pairing by hash.**

## 0. The question, and why it is a one-minute question now

PLAN-SOCIAL-SLICE's 2026-09-03 section called head portability "the number
nobody has": no measurement existed of how far a reader fitted on ft4g's
states degrades when the trunk beneath it moves by one fine-tune, and every
reader result on disk was ft4g and only ft4g. It priced the number at a
harvest and a re-fit. Finding 117 changed the price: the reader is now a
delta keyed to the trunk's sha256, `scripts/probe_reader_runtime.py` reads
Population A through the real `read_passage` in 23 s, and arm 3 -- ft4g
moved by exactly one fine-tune of arm 4's shape -- is already on disk.

The social plan's join turns on this number. If the delta survives a trunk
move, arms 4-8 can be *read* with the shipped adapter as a proxy and the
~55 min re-fit is paid once, on the trunk that ships. If it does not, every
arm that wants a reader number pays the re-fit, and the social plan's
"under an hour of card" an arm becomes about two.

## 1. The instrument, and the one flag it needed

`corn.model.load_adapter` refuses a trunk the adapter file did not name,
and `harness/backends/read.py` always hands it the served `--ckpt`, so there
was no way to put the ft4g delta on another trunk without either editing
the fingerprint or bypassing the check. Neither was done. The probe gained
`--adapter-trunk <path>`: the checkpoint the adapter's hash is checked
*against*, defaulting to `--ckpt`. Passing ft4g there while `--ckpt` is arm
3 loads the adapter with the fingerprint check passing against the trunk it
names, prints both hashes, and records `adapter_trunk` in the JSON. The
mismatch is declared on the command line rather than hidden. **The runtime
has no such flag**, and `scripts/check_model.py` -- which drives
`load_adapter` against a different trunk and asserts the refusal -- is green
after the change.

    trunk                                sha256          init          what it is
    corn_jr_260m_v4_ft4g                 985240095e80    v4 base       the trunk the adapter names; server.json
    corn_jr_260m_v4_ft_social3           7b5edfaa78bc    ft4g          ft4g + one fine-tune (arm 4's shape)
    corn_jr_260m_v4_ft_social2           02e5d681e7cd    v4 base       ft4g's recipe, one source swapped: a sibling

Everything else is finding 117 (a) verbatim: `--reader head_whole` at the
shipped `-1.174`, extent d = 2.0 radius 3, fp32, the same 1,003 passages,
`probe_reader_passages.judge` on `reduce`'s output. **The threshold is held
at ft4g's constant on purpose.** A re-derived threshold would be the re-fit's
protocol; the question here is whether the file that ships reads on a trunk
it was not fitted to, and that is a fixed-threshold question -- so the
attempt rate is reported beside every `right`, as §4i required.

## 2. The read

                                    answerable 721            unanswerable 282
    trunk under the ft4g adapter    right  wrong  silent      silent  wrong    attempt   acc|att  precision
    ft4g (finding 117, its own)      526    122     73         199     83      89.9%     0.812    72.0%
    arm 3 (ft4g + one fine-tune)     521    130     70         196     86      90.3%     0.800    70.7%
    arm 2 (sibling from the base)    524    128     69         199     83      90.4%     0.804    71.3%

**Pre-registered reading one fires on both trunks**: "arm 3 within ~10
right of 526 with correct silence within ~5 of 199". Arm 3 is 5 right and 3
silences under; arm 2 is 2 right under and level on silence. The attempt
rate moves by half a point -- the fixed threshold is very slightly more
willing on a moved trunk, which is the direction a margin perturbation shows
when the constant was fitted elsewhere, and it is inside what finding 117
(b) measured between the harvest's bf16 trunk and the runtime's fp32 one.
Latency is the same 23 ms a passage; the hybrid fallback fired on 0.

## 3. Paired, by passage

Verdicts paired against finding 117's per-passage record
(`reader_runtime_whole_s1.json`), exact two-sided binomial:

    against ft4g's own read         moved     right lost/won   p       silence lost/won   p       joint lost/won   p
    arm 3                          27/1003        8 / 3       0.227        6 / 3        0.508       14 / 6       0.115
    arm 2                           9/1003        2 / 0       0.500        1 / 1        1.000        3 / 1       0.625

Nothing is significant and nothing is close to it. **27 passages of 1,003
move under a one-fine-tune trunk move, and 9 under the sibling.** For scale,
finding 117 (b) measured 17 spans differing between the harvest's trunk and
the runtime's *identical weights* under a different autocast; a whole
fine-tune moves 9 to 27.

**The species of the movement, arm 3:**

    answerable    right -> silent 4    right -> wrong 4    silent -> right 2
                  silent -> wrong 6    wrong -> right 1    wrong -> silent 1
    unanswerable  silent -> wrong 6    wrong -> silent 3

Eleven of the 27 are a silence becoming speech or the reverse -- margins on
either side of a constant fitted on another trunk -- and the rest are the
head's pick moving on a passage it speaks on either way. That is the same
two-species shape finding 117 (b) traced to a small perturbation of the
head's inputs, and no third species appears. Arm 2's nine are five
`silent -> wrong` on answerable passages and four singletons.

## 4. What this says, and what it licenses

**The delta is portable across the trunk moves this project actually makes.**
A rank-32 adapter and a 6.3M-parameter head fitted to ft4g's layers {8, 12,
16} read within the seed spread (finding 112 put it at ~5 passages) on a
trunk ft4g was fine-tuned into and on a trunk that shares ft4g's recipe but
not its init. The states the reader depends on are a property of the
family's training rather than of one checkpoint's last 1,200 iterations.

So the join in PLAN-CONVERSATION's seventh section takes its cheap branch:

  * **Arms 4-8 are read with the ft4g adapter as a proxy** -- probe only,
    through `--adapter-trunk`, never served -- and a reader number on an
    arm costs 23 s rather than 55 min. The number is a proxy in exactly
    the sense measured here: within a handful of passages at a fixed
    threshold, attempt rate reported beside it.
  * **The re-fit is reserved for the trunk that ships.** It still runs, once,
    at that trunk's own CV'd threshold, with whatever recipe
    PLAN-READER-WHOLE-NEXT §2 settles; nothing here replaces it, because a
    fixed threshold is not the bar protocol and 3 silences is not 0.
  * **Packs and every later trunk inherit the same expectation**, stated as
    an expectation: a one-fine-tune move on this recipe costs the reader
    single digits of passages.
  * **The conversation-as-adapter alternative** the seventh section named
    -- the social class as a second delta on a frozen ft4g, so the
    fingerprint never breaks -- is not worth pricing on this evidence. It
    would buy protection against a cost that reads as 2 to 5 passages.

**Not licensed:** serving the ft4g adapter on a moved trunk. The fingerprint
stays, the server has no override, and this finding is the reason the
override lives in a probe: the number is small *because it was measured*,
and a trunk that moves further than one fine-tune of this recipe has not
been measured at all.

## 5. Limits

One adapter seed, one population, fp32, a fixed threshold. Two trunks, both
one recipe step from ft4g in different directions; a trunk two or three
social arms downstream is a different distance and is the next place to
read this, for 23 s, when arm 5 exists. The arm 3 versus arm 2 ordering (the
descendant reads slightly worse than the sibling) is 3 passages and is not
a result. The moved passages were read by verdict transition and not by
margin; the JSONs carry no margins, and a margin-level account of the 27
would need the probe to write them. Nothing here is a live session and
nothing measures packs.

## On disk

`evals/results/reader_runtime_whole_s1_on_social3.json` and
`reader_runtime_whole_s1_on_social2.json` (per passage, with
`adapter_trunk` recorded), paired here against
`evals/results/reader_runtime_whole_s1.json` (finding 117).
`scripts/probe_reader_runtime.py` carries the flag.
