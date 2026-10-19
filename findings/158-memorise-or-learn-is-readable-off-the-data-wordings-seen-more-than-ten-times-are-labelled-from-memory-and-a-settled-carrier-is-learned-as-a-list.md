# Wordings seen over ten times get memorised; key phrases become lists

**Full result:** Memorise or learn is readable off the data: a wording seen more than ten times is labelled from memory (A3's on cells 74-100% right past ten sightings, 6-47% under eleven, 29-33% never seen), a carrier that settles the answer is learned as a list (62 openings settle every ask/find label of the old parse world and he never cuts a held-out one; the functional world's best key settles 7% and he does), and A3b halves A3's lookup mass -- a family contrast registered here before its re-run (probe only)

**Cost:** CPU only, no training: `probe_lookup.py`'s three reads about 3 min together (the two parse worlds about a minute each, the move slices and the sightings read about 15 s); a scratch scan of finding 52's openings over six `mix_v3_5b` sources about 4 min; 10:59-11:13 on 2026-10-10 end to end.

The owner, 2026-10-10: the findings hold both outcomes -- a skill learned as
the idea on one slice and memorised as a list on another -- and **which one a
slice will teach should be known before it trains**. `corn/copyaudit.py`
already answers that for one kind of skill, a span he must copy (findings 12,
13, 14: a value space small enough to learn as a set is recited, not read).
This asks it for a *decision* -- a move, a part's label, a route -- on the
cases already on disk. Post hoc throughout, every number off committed items
files and slices: **probe only**.

## The rule read

He takes the cheapest route that fits the training lines. A **table** is
such a route when a cheap key of the input -- the whole line, its first one
to three words -- **settles** the answer (one value on at least 95% of that
key's lines) **and recurs often enough to be learned as an entry**. The
*settled mass* of a key family is the share of training lines its settled,
recurring entries cover; the largest over the families is the slice's
*lookup route* (`scripts/probe_lookup.py`, cards
`evals/results/a3_a3b__lookup.json`, `decomp_funcworld__lookup.json`,
`decomp_funcworld_askfind__lookup.json`).

## How often is often enough: ten sightings, at nano, one pass

A3's slice trains once (`configs/mix_v3_a3_on.py`: the weight is the file),
so a wording's count in `data/raw/social_a3_move.txt` is how many times he
saw it. His label on every A3 probe item that has a gold move, against that
count (`--sightings`):

    wording seen      on s1         on s2         off s1       off s2
    never         61/187 33%    55/187 29%    22/187 12%   21/187 11%
    1-10           8/17  47%     1/17   6%     0/17         0/17
    11-30         50/62  81%    51/62  82%     2/62         0/62
    31-60         28/31  90%    23/31  74%     1/31         0/31
    61+           41/41 100%    40/41  98%    19/41        20/41

Past ten sightings he labels the wording from memory at both seeds; at ten
or fewer he is near his rate on wordings he never saw (pooled 9 of 34 against
116 of 374). The off cells' 19-20 of 41 at 61+ are the stock forms the word
alone primes (finding 157). **Ten is a nano, one-pass figure**: a larger model
or more passes memorises sooner (finding 52, below, at ~50 passes).

## The pair that separates: the old parse world and the functional one

Finding 133's pair, `ask` against `find` -- the two labels `funcgen` was
built to serve from one carrier pool:

    key                 decomp_b (old world)            funcworld
    whole part          0 entries -> settled 0.000      0 entries -> 0.000
    first word          37 entries -> 0.817             4 entries -> 0.051
    first 2 words       62 entries -> 1.000             19 entries -> 0.074
    first 3 words       92 entries -> 1.000             42 entries -> 0.073
    lookup route        1.000                           0.074
    held-out parse      0 on every arm (finding 133)    w_heldout 10-17 of 140 against floors 2-4

**Sixty-two two-word openings settle every ask/find label of the old world**,
each seen hundreds of times, and no whole part ever repeats -- so the table
he could build was the opening, and a held-out opening read zero on every
arm. The functional world's best key settles 7%, and he cuts phrasings he
never saw at all six seeds. Over all labels the two worlds read 0.680 and
0.399 (the functional world keeps stock social and chat parts that a table
does settle).

## The ranking, and where A3b falls

    slice                              lookup route          outcome
    decomp_b, ask/find                 1.000 (first 2)       list: held-out zero
    A3 move slice                      0.837 (first 3)       list: unseen to a default (finding 157)
                                       0.756 (whole line, 270 entries)
    decomp_b, all labels               0.680 (first 2)       list: held-out zero
    A3b move slice                     0.580 (first 2)       -- not read --
                                       0.378 (whole line, 416 entries)
    funcworld, all labels              0.399 (first 3)       idea: held-out above the floor
    funcworld, ask/find                0.074 (first 2)       idea

**A3b's 1,021 hand-written phrasings halve the whole-line table** (0.756 to
0.378) and put the slice between the two groups, which is what makes its
re-run a test of where the line is rather than a confirmation.

## Two readings the bracket gets wrong, both kept

**The cheapest settled key is not always the one he takes.** In A3, `rough`
opens 41 training lines and every one is `consolation`; on "rough day at
work / school / the shop / the office" he writes `greeting` on all four at
seed 1337, and `open` on three and `greeting` on one at seed 2337 (hand read,
the items files). `consolation`'s wordings
are seen 0-16 times each, mostly under ten, so by the curve above they were
never memorised, and the settled first word did not stand in. In the old
parse world, where no whole part repeats, the opening *was* learned as the
list. So **which key he memorises is not predicted by settledness alone** --
the whole line when it repeats enough, a cheaper key at least sometimes when
it does not -- and the bracket reports every family rather than pretending to
know. The thin family also says the second condition: a slice with little
lookup mass still needs enough distinct evidence per answer, and 136
`consolation` wordings taught neither the list nor the move.

**Finding 52, read on openings across the whole mix, does not fit.** The
twenty searchgrid templates' openings were scanned over `mix_v3_5b`'s six
sources with user turns, scoring how often each opening is followed by
`web_search`: ten of the twenty are pure (1.000) and they route anywhere
from 0 to 15 of 16; Spearman against routing **-0.19** (scratch scan, not
committed -- a bound). Read on whole lines it fits: the tools slice is 2.5 MB
at a weight that makes about 50 passes in the 5B run (bytes/4 as tokens), so
each of its 2,986 distinct search lines was seen ~50 times -- a whole-line
table covering the slice, and on a new subject only four templates route.
**Why those four** (`google`, three spellings of `look up`) is not in the
slice; the guess is the web text's priors, the same guess `check_copyable.py`
writes down for the contact slot, and it is not measured.

## The copy audit, read the same way

No new numbers. `check_copyable.py`'s two controls -- 28 search answers at
107 uses, 400 field names at 170 -- are tables whose entries the request
settles and which recur far past ten; both were recited. Its counterexample,
1,442 dates at 122 uses read 353/353, is where it concludes "cardinality and
not exposure": read here, a date is not settled by the request (it moves
with the anchor), so no table fits however often a date recurs. That is a
reading, not a measurement of the slice.

## Registered before A3b's re-run

A3b died twice on 2026-10-09 (a chain stopped at iter 5,200 of 5,337, then a
power-off at ~4,720) and has no finished checkpoint at either seed; nothing
from it has been read. **The pre-registration of record stays
`configs/mix_v3_a3b.py`'s**; this adds one contrast the rule makes and the
word counter does not:

    A3b family     max settled mass    distinct wordings    word counter, unseen (of 20)
    wellbeing      0.81                458                  14
    thanks         0.70                575                  12
    consolation    0.37                478                  10
    farewell       0.50                497                  17

* **The contrast.** On the unseen probe (`HELD_OUT_PROBE`, 20 a family), his
  labels on `consolation` + `farewell` (40 items) beat `wellbeing` + `thanks`
  (40) by at least 5 at both seeds. A bag of words fit on the same slice has
  the two pools level (27 against 26), so a gap of that size is the lookup
  route and not lexical ease. **The confound named now**: if a seed's
  default value lands in one pool it inflates that pool; the read reports
  how many of each pool's items carry the seed's commonest label beside the
  count.
* **The curve replicates.** On A3b's own slice, items whose wording is seen
  more than ten times are labelled right on at least 80% at both seeds.
* **No call on the total.** The registered gate (unseen +10 over A3) is
  where A3b falls between the groups above; a pass puts the line above a
  0.38 whole-line route at nano, a miss puts it below.

## What it licenses

* **A design rule for any slice that teaches a decision**, before the
  freeze: no example line recurs more than about ten times in a nano pass
  (cap it or widen it); where the answer is structural, no cheap key settles
  it (`funcgen`'s one pool across labels); and every answer gets enough
  distinct evidence. `probe_lookup.py --moves` / `--parts` reads the first
  two on a slice in seconds.
* **Not a guard yet.** The bracket is fit on four cases chosen after reading
  them; a guard like `check_copyable.py` waits on a single-variable test --
  the same slice with its lookup route cut and nothing else changed -- and
  on A3b's contrast above.

## What it does not say

That the lookup route is the cause: every case here varies more than one
thing, A3b included. Anything at 260M, where ten sightings is too many (52).
Which key he takes when several settle the answer (the `rough` read). That a
slice with no lookup route teaches the idea: it is necessary on these cases,
not sufficient (`consolation`). A key nobody lists -- a left edge mid-line
(findings 28-29's mechanism), a length, a position -- reads clean here and is
not.

## Amended 2026-10-10: the bracket on extraction finds nothing to fix (probe only)

Asked by the owner: does the lens explain why extraction stalled (the
whole-passage reader at 526 of 721 on Population A, finding 117, against a
target above 85%)? Four reads, CPU only, through scratch scripts not on disk
-- every number below is a bound on an unpinned instrument: the gold of a
training window is the longest run of the say's words found in the window,
and a "name" is a capitalised word of four letters or more that is not a
sentence's first word or a question word.

**No cheap rule settles the training answers.** On `extract.txt`,
`extract_5b.txt` and C3's `readback_passage.txt`, the gold is the *first*
value of its type in 33-43% of windows that carry a same-type rival, and the
value *nearest the question's words* in 13-33%. Finding 66's "first value of
the right type" is not something these slices reward.

**The hard case is not rarer in training, and he is not worse on it.**

    nearest same-type rival   Population A (share, reader right)   extract.txt   extract_5b.txt   readback_passage.txt
    within 5 words            52%   76%                              49%           50%              51%
    6-15 words                27%   71%                              27%           26%              27%
    16+ words                 14%   77%                               9%           10%              16%
    no rival                   7%   84%                              14%           14%               6%

By sentence the same: a rival in the gold's own sentence is 70% of
Population A's typed answers and 66-72% of the slices', and the reader is
75% right with one there and 75% with one only elsewhere. **So neither half
of the rule -- a table to take, or a case the data never forces -- explains
the residual at this resolution.** What does split: golds that are neither
a number nor a name (descriptive phrases, 125 of 721) read 61% right against
75% for typed ones, and ten wrong answers drawn at random (`Random(1)`) show
extent-heavy golds ("204,408 in 2013", "7.6% Per Annum", "the Indian
national cricket team") -- the boundary and label question findings 104 and
`audit_refused_wrong.py` already price, not a data shape this bracket reads.

**For C3**: the read-back slice matches Population A on every axis read
here, so nothing in this amendment asks it to change before F1. Finding
66's own case -- two values in one clause told apart by a single verb -- is
finer than a word count can see, and stays the open one.

## Amended 2026-10-10 (second): the causal test did not show the lever

Finding 159 read both registrations this finding made or fed. **The pair**
(cap against rep at the same size, word counter level): level at seed 1337
(-6), unreadable at seed 2337 -- no guard is built. **The family contrast
registered above fails**: +5 and +2, the one pass sitting on the seed's
default label. What stands from this finding is the description -- a
wording seen past about ten sightings in a nano pass is labelled from
memory, and a slice whose answer is settled by such a table teaches the
table -- not the recipe: a slice with the table removed interpolates to near
phrasings at one seed and still reaches far ones no better (finding 159's
three regimes).
