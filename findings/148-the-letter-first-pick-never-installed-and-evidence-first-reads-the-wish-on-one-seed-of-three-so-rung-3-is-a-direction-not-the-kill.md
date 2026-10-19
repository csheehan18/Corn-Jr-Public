# Picking a template by letter never installed; one seed in three learned

**Full result:** Rung 3's letter-first pick never installed, not even on the pairings he trained on, at one dose or four; written evidence first, one seed of three reads the wish -- held-out 113 and 97 of 288 against a gate of more than 95, and swapping the request's soft term moves the pick onto the new wish's item -- while the other two sit at chance, so rung 3 reads seeds split, a direction and not section 7's kill

**Cost:** about 3.4 h of GPU -- 2.8 h training nine nano runs (17.6-20.4 min each, `card_cost.py` on the copy cards), about 36 min of `prepare_mix`, probe and copy cards inside the five chains (10:15-11:08, 12:03-12:49, 13:20-14:03, 15:42-16:24, 19:01-19:21 on 2026-10-02, each under its registered ETA), and a few minutes a checkpoint of scratch probes no card sees (trained-trace scoring, the forced letter, the wish-swaps). Amended 2026-10-03 with arm V: 55.4 min of training three seeds (`card_cost.py` on the copy-wide cards) against a registered hour, `prepare_mix`, probe and copy cards untimed, and about 12 min of hand-read probes on 2026-10-03 (`probe_filter_traces.py` on six checkpoints, `probe_filter_split.py` on nine).

PLAN-TAG-LANGUAGE §6 rung 3 and ROADMAP G3, read 2026-10-02. `filter` with a
trace on top of arm F (`corn/filtergen.py`): a request carries a hard term, a
soft criterion or both; the runtime lists places as JSON (`<|obs|>`) and
writes `check:`; he writes `pick:`. The soft term is the rung only he can do --
"in the open air" against "a wine bar with seats under the trees", no shared
word (held by `scripts/check_filter.py`). Five arms, each one variable against
the one before, all on the same rows (`evals/funcworld_filter.jsonl`: 288
held-out combinations, 144 trained pairings, 96 hard-only):

    arm   config                              the one change                                    seeds
    T     configs/mix_v3_funcworld_filter.py  12,600 traces, 3.53% of the mix, pick: C because[...]   1337, 2337
    T4    ..._filter4.py                      T's file x4 by repetition, 12.76%                  1337, 2337
    E     ..._filter_ev.py                    soft picks written pick: because[<span>] C        1337, 2337
    E2    ..._filter_ev2.py                   E without the hard-only traces' pick: line         1337, 2337, 3337

Seed 3337 was **added after the read** by the owner's call
(`configs/nano20m_v3_fw_filter_ev2_seed3.py` says so); nothing pre-registered
a third seed. **Cards:** `evals/results/<ckpt>__filter.json` (T, T4, F;
`scripts/probe_filter.py`, bound decode), `__filter_full.json` and
`__filter_full_items.jsonl` (every arm and F; `scripts/probe_filter_full.py`,
every ok item's whole line scored), `__copy.json` and `__copywide.json`.
Both probes are hand-built with no pin beyond `check_filter.py`'s hold on
their rows and gates, so **every number below is a bound** (rule 28). The
habit-free column is recomputed here from the committed items files; the
trained-trace scores, the forced-letter test and the wish-swaps are **probe
only -- not on disk** except where a card is named.

## The letter-first arms: a kill row by the letter, and nothing installed

Arm T, bound `id` (the gate column), and the full-option read beside it:

    checkpoint   held-out   hs / soft   trained   free names an ok item   hard-only free   full-option held-out / trained
    T  1337       74/288     48 / 26     39/144        288/288              93/96            79 / 41
    T  2337       74/288     53 / 21     38/144        288/288              93/96            79 / 42
    T4 1337       77/288     53 / 24     40/144        288/288              96/96            79 / 41
    T4 2337       77/288     55 / 22     45/144        288/288              96/96            77 / 45
    F  1337       48/288                 27/144                                              74 / 38
    F  2337       55/288                 28/144                                              68 / 47

The gate was more than 95 of 288 (floor 0.281, the best of chance, position,
a bag of words and a word-overlap rule, plus its 95% interval); the trained
cell's bar, registered with T4, more than 54 of 144. **By the letter, arm T
lands on the pre-registered kill row** -- 95 or fewer at both seeds with the
hard half passing. It is not read as one, because the trained cell sits at
chance too: §7's kill needs a model that holds the association and fails to
carry it, and this one never held it. Scored in full on soft traces he
trained on, the letter is right **113 of 400 against chance 114** (T,
probe only). **Four times the dose does not move it**: T4's trained cell 40
and 45, held-out 77 at both seeds, trained traces 126 of 400 against 114
(probe only) -- registered row (c), unreadable at nano. Arm F, never shown a
trace, reads under both: the rows do not leak.

**Why, as a hypothesis the next arm was built to test.** In `pick: C
because[...]` the whole judgment sits on one letter, behind a two-hop lookup
(find the fitting description, then the id written before it in the JSON),
and everything after the letter can be copied from that letter's own text --
so nothing in the training text pushes the soft term toward its description;
one pointer token a trace carries the gradient (finding 145's shape: the wall
was the carrier word). A letter-free check was tried first and was weak:
forcing a neutral letter and asking which description he wants to write
after it, **he copies the forced letter's own text on 126 of 144** (probe
only), so it measures the lookup again and says nothing about the judgment.

## Evidence first: the seeds split

Arm E changes the soft pick line's order and nothing else (10,080 lines of
126,001, held by `check_filter.py` section 8). Full option, `ev` order:

    checkpoint   held-out   trained   held-out first-ok   habit-free (gold not first)   tool.copy
    E  1337       76/288     42/144       157/288             79/207                       120/120
    E  2337      113/288     57/144        70/288            108/207                       100/120
    E2 1337       83/288     48/144        83/288             82/207                       102/120
    E2 2337       97/288     70/144       147/288             91/207                       119/120
    E2 3337       69/288     47/144        94/288             69/207                       copy_wide 293/300
    F  1337       80/288     35/144        37/288             76/207
    F  2337       71/288     50/144        71/288             71/207

The habit-free column takes the 207 held-out rows whose gold is not the first
ok item and races only the later ok items: chance 79, its 95% bar about 93.
**Arm E seed 2337 clears every bar** -- held-out 113 (`hs` 71 of 192, `soft`
42 of 96, both above their chance), trained 57, habit-free 108. **Seed 1337
falls into the first-ok habit** -- 157 of 288 held-out picks are the first ok
item -- and reads chance even with the habit raced out (79). Registered:
seeds split, unreadable, a direction.

**Arm E2 tested whether the habit came from the hard-only traces**, where he
wrote the runtime's first-ok pick himself (SPEC §6: without a soft term the
runtime takes the first ok item) -- 2,520 lines removed, nothing else. **It did
not.** The habit moved seeds instead of leaving: seed 1337 lost it (83 of
288 first) and still reads chance (48, 83, habit-free 82); seed 2337 gained it
(147 of 288) and reads trained 70, held-out 97 -- two over the gate -- with
the habit raced out at 91, just under that column's bar. Registered: seeds
split again. **The third seed reads chance on every column** (47, 69,
habit-free 69). **Description-first installs on one seed of three at nano.**

Read beside it: the held-out band near the gate is crowded by things that
never trained the order -- T4 seed 2337, which only ever wrote the letter
first, scores 94 of 288 on the `ev` line and 92 habit-free -- so a reading
of 97 is not distinguishable from noise by the count alone. What separates
seed 2337 is the swap.

## Swap the wish and the pick follows it -- on seed 2337 only

`scripts/probe_filter_swap.py` (probe only, not yet guarded): on every soft
row, rewrite the soft term in the request and the `goal:` line to the
phrasing of a shown ok distractor's concept (the first in list order whose
concept does not clash with the gold's), keep the items byte for byte, and
score every ok line again. A reader of the request moves onto the new wish's
item and off the old gold; a reader of the shown set does not move.

    checkpoint   held-out old gold          the new wish's item
    E  2337        113 -> 76                    63 -> 93
    E2 2337         97 -> 62                   115 -> 169
    E2 1337         83 -> 79                    77 -> 81
    E2 3337         69 -> 70                    93 -> 95

(The new wish's item is often the first ok item, so a seed with the habit
already favours it unswapped -- E2 2337's 115; the move is what counts.) Arm F
seed 1337, never shown a trace and scored in the evidence-first order, barely
moves: held-out gold 80 -> 72 and the new wish's item 40 -> 46, trained 35 ->
37 and 25 -> 25 (probe only -- read off the session's console, not on disk).
**Seed 2337 reads the
wish, not the shown set, in both arms; the other seeds read neither.**

**An instrument hole, found by the rung-4 builder and owed here.** The decoy
rule that keeps a held-out answer from being the only stranger in its list
draws each distractor from a family fixed by the phrasing --
`decoy_families`: family `(p + c' + 1) mod N` for each other concept `c'`,
against the gold's `(p + c) mod N` (`corn/filtergen.py`). So on every held-out
row the gold is the one shown item whose family less its concept, mod N, is
one below every other item's: **the answer is derivable from the set of shown
description families by arithmetic, without reading the request**, and none
of the four floor predictors tested that. Rung 4 found the same shape in its
own rows (a shown-clause set alone scored 0.984) and closed it there with one
Latin square before arm US trained. The swap shows seed 2337 is not using the
shortcut -- it holds the items fixed and the pick still follows the wish --
but **the eval owes a set-only floor** before any other checkpoint's held-out
number on these rows is read as judgment.

## The copy band

`tool.copy` (120 items, six answers) dips at one seed in three arms: T4 seed
2337 100, E seed 2337 100, E2 seed 1337 102; T reads 120 at both, E2 seed 2337
119. Each dip is a block of 18-20 wrong answers, the size of one answer's
phrasings (§5.7 found arm F's own seed 1337 at 102, every failure one
answer); which answer each garbled here was not read. The registered kill --
under 118 at both seeds -- fired on no arm. From 2026-10-02 the standing kill
reads `tool.copy_wide` (232 answers, EXPERIMENTS §5.7); of rung 3's arms only
E2 seed 3337 has that card, **293 of 300 against arm F's 280 and 288**. The
others' wide row is unmeasured.

## A hypothesis, not tested

In rung 4's passing arm (arm US, finding 149) the clause he matches sits on
the same line as the id he writes after it. Here the description is the last
field of a JSON object, behind `"price"`, `"km"` and `"rating"`, away from its
`"id"`. A runtime view that puts each item on its own line with the
description beside the id -- `item 1: <about> (price, km, rating)` -- may be
what rung 3 needs to install on more than one seed. Nothing here measures it.

## What it licenses

The owner's decisions of 2026-10-02, taken on this read:

* **Description first is the format.** A pick is written `because[<span>]`
  then the id, here and in rung 4; the SPEC-LANGUAGE §6 amendment (and the
  bind's) follows this finding.
* **The hard-only pick is the runtime's.** Without a soft term he writes no
  `pick:`; E2 showed removing it costs nothing and buys nothing on its own.
* **Rung 3 is "seeds split, unreadable -- a direction"** by both E and E2's
  pre-registrations, now one seed of three. **It is not §7's kill**: the kill
  row needs the trained cell installed and the held-out cell not, and on the
  letter-first arms neither installed. **G3 is read.**

## What it does not say

That judgment does not train at nano -- one seed of three does read the wish,
on held-out combinations, and moves with it. That it does: two seeds of three
sit at chance on every column, and the third seed was not pre-registered. That
the letter-first null was the format alone: E's order and E2's missing hard
picks each changed which seed read, not how many. That the held-out numbers
on these rows mean judgment for any checkpoint the swap was not run on, until
a set-only floor is computed. That dose is closed: T4 is dose by repetition,
not by fresh traces. Nano, the synthetic world, one draw of rows.

## Amended 2026-10-03 -- arm V: the layout was not the cause, and the letter after the description was never read

Arm V (`configs/mix_v3_funcworld_filter_view.py`, pre-registered at d515f51,
cards at ef9e138) tested the hypothesis above: arm E2 with the runtime's item
view after each `<|obs|>` -- `item C: <about> (price, km, rating)`, the
description on its id's own line -- three seeds, the same traces. Read on the
view rows, full option, `ev` order, and the swap (`probe_filter_swap.py`,
held-out cell; probe only -- the session's console):

    checkpoint   held-out   trained   swap: old gold   new wish's item   tool.copy_wide
    V 1337        82/288     39/144      82 -> 87         56 -> 59          284/300
    V 2337        79/288     37/144      79 -> 86         98 -> 96          298/300
    V 3337        71/288     45/144      71 -> 74         85 -> 83          278/300

**No seed reads the wish: the pre-registered row is 0 of 3, "the layout is
not the cause" at nano.** Seed 2337, which read the wish in E and E2, does not
here; the first-ok habit sits on it (113 of 288 held-out). The copy-band kill
did not fire. Rung 3 stays "seeds split, a direction".

**Read by hand before it was written (EXPERIMENTS §5.6).** The view rows'
prompts lay out exactly as the payload's traces (`<|obs|>`, one `item` line a
shown item, `goal:`, `check:`; read side by side on a trained row). Scored on
the traces each arm trained on (`scripts/probe_filter_traces.py`, 400 soft
traces from the first 99% of each payload; probe only):

    checkpoint   right of 400   first ok   habit-free of 282
    V  1337          149           66           141
    V  2337          144          155           130
    V  3337          139          128           128
    E2 1337          135           89           135
    E2 2337          187          187           166
    E2 3337          154          135           135
    chance           114                        112

Every seed of both arms is above chance on the exact text it saw, while the
rows' `train` cell -- fresh draws of the same pairings, none of whose
requests or observations occur in the payload -- sits at chance on every
checkpoint but E and E2's seed 2337. What the other seeds hold is the trace, not the pairing. V is not
better than E2 on its own traces; seed 2337 lost 43.

**The raw decodes showed something the counts hide: the right description and
the wrong letter.** `pick: because[a candlelit bistro] A` with the candlelit
bistro at C; `because[a hotel with cushions and lamplight] A` with it at E.
A whole-line score charges that line for the letter. So the judgment and the
lookup were scored apart (`scripts/probe_filter_split.py`; probe only):
`span` is which description he would write -- every ok item's `pick:
because[<span>]` alone -- and `id` is which letter he writes once the gold
description is already written. The swap is re-read on `span`:

    checkpoint   span held-out / trained   id given the gold span   whole   span swap: old gold   new wish
    V  1337          87 / 42                  70 / 33                82        87 -> 85            69 -> 69
    V  2337          86 / 40                  83 / 40                79        86 -> 89            87 -> 88
    V  3337          74 / 41                  75 / 39                70        74 -> 74            84 -> 87
    E2 1337          82 / 50                  76 / 42                83        82 -> 73            92 -> 96
    E2 2337          98 / 70                  78 / 48                97        98 -> 53            91 -> 153
    E2 3337          75 / 48                  69 / 33                70        75 -> 68            96 -> 98
    E  2337         119 / 59                  71 / 31               113       119 -> 76            68 -> 102
    F  1337          75 / 42                  79 / 42                80        75 -> 70            53 -> 54
    F  2337          76 / 49                  82 / 42                75        76 -> 74            50 -> 50
    chance           80 / 41                  80 / 41

Three things follow, each a bound (rule 28: both probes are unpinned beyond
the rows `check_filter.py` holds).

* **V's null is not the instrument.** On the span column, where the judgment
  is, every V seed sits at chance and the swap moves none by more than 3. The
  readers are the seeds this finding already named: E2 2337's span falls 98
  -> 53 and the new wish's rises 91 -> 153; E 2337's 119 -> 76 and 68 -> 102.
* **The card was reading the description all along.** `whole` tracks `span`
  within six on every checkpoint, so the held-out counts above and in the
  tables before this amendment measure which description he chooses.
* **The letter after the description never installed -- on any arm, any
  seed, or layout.** Given the right description already written, he picks
  its letter at chance everywhere (69-83 of 288 against 80), the reading seeds
  included, and V included, where that letter opens the description's own
  line a few tokens above. What he writes there is a position: the first ok
  letter on 177 of 288 at E2 2337, and on 210 at arm F seed 2337, which never
  saw a pick line. So the first-ok habit this finding reports lives mostly in
  the letter (E2 2337's span is first on 112). Of the two hops the
  letter-first section named -- find the fitting description, then the id
  before it -- the second is the one that never formed, at nano, in every
  format tried.

**The free decodes, every held-out soft row, every seed** (a second hand
read, 2026-10-03, after eight of seed 2337's rows; from the committed
`__filter_full_items.jsonl`, CPU): each greedy `pick:` line classified by
whether its description is a shown item's and whether the letter after it is
that item's own.

    checkpoint   copies a shown description   invented   an item check: marked unmet   letter its own   gold description
    V  1337           271/288                    17               27                      88/271           74
    V  2337           281/288                     7               39                      80/281           69
    V  3337           283/288                     5               29                      89/283           65
    E2 1337           266/288                    22               32                      69/266           63
    E2 2337           240/288                    48               31                      77/240           67
    E2 3337           280/288                     8               36                      62/280           71
    E  2337           246/288                    42               22                      79/246           95

The letter after his own description is its own on 23-33% -- chance at three
to five shown items -- on every checkpoint, so the split's `id` column was
not a teacher-forcing artefact. Two failures the counts above never showed,
both of which the §9 bind would refuse: **a description that is on no shown
item** (5-48 rows; seed 3337 writes "a cafe with oak beams from the 1600s"
and "a cider house in a medieval building", neither shown -- and the seeds
that read the wish invent most, 48 and 42), and **a description of an item
`check:` already marked unmet** (22-39). The greedy line's gold-description
count sits under the scored `span` column (E2 2337 67 against 98): the decode
is noisier than the ranking.

**What it licenses -- a proposal, the owner's to take.** The description he
writes identifies exactly one shown item on every soft row (432 of 432, no
duplicate, no prefix of a second item), so **the letter can be the
runtime's.** SPEC-LANGUAGE §9 already specifies a bind for D-A1.18's order --
the id limited to the item the span was copied from -- and lists it owed; this
says the bind is not a safety net here but the only thing that would write
the right letter. The other route is that the runtime resolves the pick from
the span by exact match and his letter is dropped from the line, which is a
§6 change to D-A1.18. Neither is made here. Rung
4's passing arm writes `because[clause]` then the template id the same way,
and its id is not read either: finding 149's amendment (arm USN's hand read)
finds it its clause's own on about one in three at two to four templates.

**What the amendment does not say.** That the lookup cannot train: no arm
targeted it, and the dose was never raised. That the layout is irrelevant at
260M. Why seed 2337 lost the wish when the view was added -- one seed, read
once. Nano, the synthetic world, one draw of rows.
