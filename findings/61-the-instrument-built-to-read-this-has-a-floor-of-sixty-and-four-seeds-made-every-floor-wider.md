# Sixty-first finding — the instrument built to read this has a floor of sixty, and four seeds made every floor wider

P3-B1, run 2026-08-26. Four arm seeds against four control seeds, 1,112s each,
paired seed for seed (1337–1340). `configs/mix_v3_p3b1.py` carries the
pre-registration; this is what it read.

**The treatment.** `data/raw/tools_p3b1.txt` is `tools_names.txt` with the
2,992 `web_search` carriers re-drawn from 85 hand-written phrasings instead of
25, and nothing else changed — same subjects, same calls, same observations,
6,775 non-search transcripts byte-identical, seven of eight slices hashing
identical to `mix_v3`'s after `prepare_mix`. It attacks the fifty-second
finding's defect: 25 phrasings offered, about four kept.

## Not one row separates, and the floors are why

    row                   control x4      arm x4       c spr  a spr
    search.route_base     [169, 190]      [163, 195]      21     32
    search.route_wide     [134, 180]      [152, 193]      46     41
    search.route_heldout  [135, 162]      [124, 184]      27     60

Midpoints move +4.0, +14.5 and +11.5 against floors of 32, 46 and 60. Every
cell overlaps. Ground rule 6 is not close to satisfied on any of them.

**Every floor got wider going from two seeds to four, and not one narrowed:**

    search.route_base     ctl  8 -> 21    arm 18 -> 32
    search.route_wide     ctl 35 -> 46    arm 23 -> 41
    search.route_heldout  ctl 17 -> 27    arm 44 -> 60

That is the forty-third finding reproducing on a corpus family it was never
measured on. It said `mix_v1`'s two-seed spreads were not luck in the
convenient direction and got *wider* at four seeds; this says the same about
`mix_v3`, on a row built three days ago. **A two-seed spread is a lower bound
on a floor and should never be quoted as the floor.**

The absolute size is the part that outlives this arm. `search.route_heldout`
spans **60 of 200 items on the arm alone** — 30% of the row — and
`route_wide` 46 on the control. A treatment would have to move a third of the
row to be readable here.

## The one encouraging pattern, and the two controls that take it away

`search.route_wide` — the row the treatment targets, carrying the 60 phrasings
trained only in the arm — is **positive at all four paired seeds**: +18, +6,
+13, +21, mean +14.5. That is the only registered row with a consistent sign,
and it is the one the arm was built to move. It is not enough, for two reasons
that were found by looking rather than by argument.

**A 4-of-4 sign is what this data produces by chance.** Twenty-three untreated
rows carry a nonzero paired difference. Under a fair coin, P(all four the same
sign) is 0.125, so ~2.9 of 23 should be sign-consistent by noise alone.
**Observed: exactly 2** — `tool.validity` all-positive and `turn2.second`
all-negative, neither of which the treatment has any mechanism to move. Sign
consistency at four seeds is therefore not evidence in this data; it is the
expected rate.

**And there is a per-seed offset favouring the arm.** Summed across the 23
untreated rows, arm-minus-control reads **+32, +8, +72, +118** at seeds
1337–1340 — a mean per-row offset of +1.4, +0.4, +3.1 and +5.1 items. The two
later seeds put the arm broadly ahead on rows the corpus change cannot touch,
so the paired differences are contaminated by something seed-shaped rather
than treatment-shaped. The arm's *val loss* is marginally worse than its
control at every matched seed (2.3786 vs 2.3761, 2.4688 vs 2.4658), so this is
not the arm being a better model.

`route_wide`'s per-seed advantage does exceed that offset at every seed
(+18 vs +1.4, +6 vs +0.4, +13 vs +3.1, +21 vs +5.1), which is the honest
reason not to call it zero either. **It is a candidate, not a result.**

## What is registered, and what is not claimed

The registered report is `configs/mix_v3_p3b1.py`'s own: **not readable.** Not
outcome 1, not outcome 2, not outcome 3. In particular:

  * **Not "the dose was installed"** — `route_wide` overlaps its control.
  * **Not the honest null** — that needs a non-movement on `route_heldout`,
    whose arm seeds span 60 of 200. A non-movement inside a 60-wide spread is
    what the sixtieth finding refused to conclude anything from.
  * **Not a cost.** `tool.selection` looked like a 7-item separation at two
    seeds against a two-seed spread of 1 and 4. At four it reads ctl
    [109, 130] against arm [117, 144] and overlaps outright, with the arm
    *higher*. The nineteenth finding's measured floor for that row is 44. The
    two-seed reading was the thirtieth finding's trap and nothing else.

**Rule 10's regression watch is clean and is the one thing this run
establishes.** `temporal.copy` 353/353 on all eight checkpoints.
`tool.copy_wide` midpoint identical to the control's at 290.8. `tool.copy`
reads arm [100, 120] against control [118, 120] — a 20-item arm spread that is
one seed reading 100, and the sixtieth finding's method note already measured
9 of 120 moving across five iterations of a single run. Every `lm` row sits
inside its control range, as it must for a transform touching 0.62% of the mix
that changed no subject.

## What this costs the plan

`docs/PLAN-PHASE-3.md` says the fine-tune-or-mix question is "cheap to settle
at nano". That was true and it was settled. **It does not follow that the
*phrasing* question is cheap to settle at nano, and this run is the evidence
that it is not.** Two instruments have now been measured unable to read a
phrasing treatment at 20M: `harness/searchgrid.py` (sixtieth finding,
seed-noise-dominated) and `search.route_*` (this one, floors of 27–60 on a
200-item row). Eight nano runs and eleven scorecards bought a null about the
instrument both times.

The next move is therefore a decision about *where* this gets measured rather
than another nano arm. Three options, none costed here:

    more seeds        the floors widened at four and there is no reason to
                      expect eight to help. The forty-third finding is the
                      precedent and it points the wrong way
    a bigger row      200 items over 200 subjects; a 1,000-item row would cut
                      the sampling component but not the checkpoint-to-
                      checkpoint component, which is what these floors are
    measure at 260M   where the fifty-second finding was measured in the
                      first place, and where the phrasing effect it found was
                      large. This is the honest place for the question and it
                      is not cheap

**Nothing here says the widened pool is worthless.** It says this project
cannot currently tell, and that the sentences cost a morning to write and sit
on disk either way.
