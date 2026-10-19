# With no template he completes nothing; inside one, every task runs

**Full result:** G5, three templates nobody on the world's side wrote: with no template he completes 0 of 1,440 runs, inside one the runtime makes every task executable, and his one-place judgment rides into a two-place composition unchanged (45-47% a soft part against 28% for the rule filler, at the one seed that reads the wish); both registered gates fail as written, the kill does not fire, and choosing among unseen templates is chance

**Cost:** zero training. GPU: 20 min for the five execution reads
(215-261 s a checkpoint), 2.2 min for the four selection reads (31-38 s),
a 12-row smoke and one 7 s crash. CPU: the runtime, rows, probe and guard,
about an hour (18:20-19:20 on 2026-10-07). End to end 18:20-19:55, against
an estimate of 1-1.5 h of code and 1.5 h of card.

ROADMAP G5, PLAN-TAG-LANGUAGE rung 5 and §1's experiment: *someone other
than the author writes a template for a task the model has never seen; with
zero retraining, the model with the template, the model without it, and the
template with a rule-based filler.* **Built**: `corn/worker.py` (a template
file and its step language -- `find`, `send`, `note` -- a fresh frame per
`find` showing him what rung 3's traces show before a decision, the
runtime's own `check:` from the goal he wrote, the typed return, the call
tree); `scripts/make_evals_workers.py` -> `evals/workers.jsonl` (288 rows);
`scripts/probe_workers.py`, gates in its docstring before a decode (f78f00c);
`scripts/check_workers.py`, guard 91. **The templates**
(`evals/g5_templates/*.tpl`, c7bfd7c) were written by a separate agent
session from `BRIEF.md` and `corn/worker.py` alone -- the owner's call --
and committed before the rows, the probe or a decode existed:
`share_a_place` (find one place, text it to a friend), `trip_stay_and_eat`
(a stay and a meal, noted together), `day_out_with_friend` (lunch then
drinks, both texted). **Zero training**, the owner's call: execution on the
five checkpoints that write rung 3's trace (arms E and E2), selection on the
four that write `use:` by clause (arms US and USN). **Cards**:
`evals/results/nano20m_v3_fw_filter_*__workers{.json,_items.jsonl}` and
`nano20m_v3_fw_templates_*__workers_select{.json,_items.jsonl}`.

## Caught before the read

* **The guard's first run**: the gold decisions through the interpreter
  read every soft pick as unread, 386 of 386 -- a decoded line comes back
  without the newline the bind's reader closes on. `worker.find` supplies
  it. Unguarded, the template column would have scored zero on judgment.
* **The rule filler's first CPU read**: "under 2 km out" matched the price
  phrase "under {v}" first. Longest phrase first; its goal is then exact on
  480 of 480 parts and its hard-only picks 94 of 94.
* **The 12-row smoke** showed his goal errors entering the template column,
  so a `pick_only` column (the rule's exact goal, his bound pick) was added
  and committed (e31151b) before the full read -- reported, never gated.
* **The first execution read died** when a no-template conversation filled
  the 512 block; such a run now stops there, recorded.

## Execution -- task success of 288, soft picks of 386, hard of 94

    checkpoint        template   pick_only   rule   plain  |  soft: template  pick_only  rule  plain  |  his goal exact
    E   s1337            77          78        65      0   |          111        113      109    40   |   478/480
    E   s2337           107         112        65      0   |          173        178      109    75   |   471
    E2  s1337            94          93        65      0   |          145        144      109    50   |   479
    E2  s2337            43          98        65      0   |          105        152      109    52   |   278
    E2  s2338            83          83        65      0   |          130        130      109    40   |   477

    held-out soft (193)  E s1337 54/55   E s2337 77/79   E2 s1337 64/63   E2 s2337 47/67   E2 s2338 56/56   (template/pick_only; rule 54)
    trained soft (193)   E s1337 57/58   E s2337 96/99   E2 s1337 81/81   E2 s2337 58/85   E2 s2338 74/74   (rule 55)

**Without a template he completes nothing: 0 of 288 rows at every
checkpoint**, 1,440 runs. He makes one listing call, usually for one part
and sometimes mixing both parts' words ("a place for lunch in Lanilvholm"
for a drinks part); he writes a send or note on 3-25 rows of 288 and
**never a right one** -- messages from the lookup world ("about 50,000",
"about 4 stars") addressed to towns. **Inside the template the runtime makes
every task executable**: the rule filler, with no model at all, completes 65.

**His judgment rides into the composition unchanged.** A frame is the shape
the decision trained in, and a part's soft pick is right at the same rate
whichever template holds it -- E s2337 `pick_only`: 35 of 78 (45%) in the
one-place template, 73 of 154 (47%) and 70 of 154 (45%) in the two-place
ones, against the rule's 28%. On trained pairings he is above the rule's
band (12.5) at four checkpoints of five (`pick_only` 81-99 against 55); on
held-out pairings at E s2337 (79) and, with the rule's goal, barely at E2
s2337 (67 against 54 + 12.5). The others sit on the rule.

**Where he falls below the rule is his goal.** E2 s2337 writes the gold goal
on 278 of 480 parts: the wrong field (`rating>=50` for "at most 50 a head"),
place words as the wish (`soft[for a pint in Belorndnia]`), an invented
`assume[...]`; under the bind it copied a town as a value
(`goal: price<=Corondstad`). Its template column falls to 43 and recovers to
98 with the rule's goal. The bind holds the form of `goal:`, not its meaning.

**Read by hand** (EXPERIMENTS §5.6), every condition on 4 shown rows a
checkpoint and 8 held-out soft frames on E s2337: right picks copy the gold
description whole ("a calm cafe"); wrong ones copy another ok item's,
never an unmet one under the bind. The bound pick sometimes writes two
brackets (`because[a calm tavern] because[a busy bistro ...]`), which the
spec allows; the runtime takes the first.

## Selection -- of 288, chance 96

    US s1337  95    US s2338  96    USN s1337  102    USN s2338  104    lexical selector  210

**Chance, as predicted.** Each seed has a favourite clause rather than a
reading -- US s1337 writes `because[a trip away]` on rows asking for lunch
and drinks -- and the one-place template is almost never chosen (4-5 of 96).
A lexical selector over the clauses gets 210. These checkpoints trained
`use:` on concept clauses in another vocabulary; arm U's zero-shot
paraphrase test failed the same way (finding 149).

## The registered reading

**G5a fails as written**: template task success above plain by 20 or more
of 96 on every template at every checkpoint -- it holds on all three at E
s2337 and E2 s1337, and on `share_a_place` everywhere, and misses on a
two-place template at the other three. Plain is 0 throughout, so the lift
is the template's own task rate, and a two-place task needs two soft picks
right: near the rule's 28% a part, about 8% of rows. **The bar measured
judgment twice over, not programmability**, which the rule filler's 65 and
plain's 0 answer on their own. **G5b fails**: above the rule's band at E
s2337 (77 against 54 + 12.5) and not at E2 s2337 (47), whose goal is the
reason (67 with the rule's goal -- a column not gated). **The kill does not
fire**: one checkpoint is above the band.

## What it licenses

* **"Template over no-template" holds absolutely, and it is the runtime's.**
  A template written by someone else turns a task he cannot do at all into
  one that runs, with no retraining -- PLAN-TAG-LANGUAGE §1's smaller claim,
  "a very good local interpreter", read for the first time.
* **"Model over rule filler" holds where rung 3's judgment holds, and no
  further.** The frame neither adds judgment nor loses it; what each seed
  brought from its single-place training is what it shows inside a
  composition. That is the design working -- composition is call depth, the
  decision stays local (§5) -- and it means the claim's second half rests on
  rung 3's split, not on anything G5 adds.
* **Selection among unseen templates is the runtime's.** He picks at
  chance; the lexical selector does not. With D-A1.16 already giving the
  runtime every checkable clause, this extends it: a template's task-shape
  clauses ("text it to a friend", "two places for one outing") are for the
  runtime's retrieval, and his `use:` stays on the soft clause.
* **His goal is the weak line on one seed in five** -- the bind holds the
  form and not the field. A rule-written goal is exact on this world; whether
  the goal should be the runtime's where a rule can write it is §0's own
  test, and on this world a rule can.

## Limits

Nano, zero training, two models (execution on E/E2, selection on US/USN);
one model doing both is an arm not run. The rule filler is the strongest a
writer of this world could have -- its goal rules are the world's own phrase
tables -- so model over rule is a conservative read. Three templates by one
LLM author from a one-page brief; a person's templates, or ones needing an
op this language lacks (a fallback, a comparison across two lists), are not
read. The plain run is free decoding under a probe-played runtime; a bound
plain run is not read. Held-out cells as rung 3's (finding 148), with the
set-only floor finding 148 owes still owed here. Every number is a bound
through an instrument held by `check_workers.py` and nothing more.

## Amended 2026-10-07 -- why each failure happens, read off the items

The owner asked what the failures are made of. Read off the committed
`__workers_items.jsonl` and rung 3's own full-option cards, CPU only.

**Wrong picks are rung 3's, inherited unchanged.** Seed by seed, the G5
held-out pick rate (`pick_only`) is the same checkpoint's rung 3
full-option rate on its own trace (`__filter_full.json`): E s1337 28% against
26%, E s2337 41% against 39%, E2 s1337 33% against 29%, E2 s2337 35%
against 34%, E2 s2338 29% against 24%. The frame neither costs nor adds: a
wrong pick here is a seed whose wish-reading never installed (finding 148),
not the template or the composition. No position habit under the bind --
wrong picks spread over first, middle and last ok items. Two seeds hedge,
writing two brackets on 57 and 68 of 386 lines; the runtime takes the first,
and a later bracket held the gold 16 and 19 times.

**No template fails because he runs his one trained shape once and stops.**
On 276-286 of 288 rows the plain run ends on a say after a single
list-goal-pick; of 960 two-place rows, one made a second listing call. Every
trained document ends at its first say, so nothing after it -- the second
place, the send, the note -- is ever written. Where he calls the message or
note tool (7-97 rows), it is first, before any listing, with arm F's lookup
answers as the message ("about 50,000") and a town as the recipient.

**Selection does not read the request; it picks the clause shaped like the
ones it trained on.** Three of four checkpoints write `because[a trip away]`
on 202-228 of 288 rows, and the split of choices barely moves with the gold
template. The clauses chosen open on "a" and are short noun phrases -- the
form of every concept clause arms US and USN trained on ("a hushed
interior", "a converted mill"); `share_a_place`'s clauses all open
otherwise ("one place to go", "text it to a friend", "tell someone where to
meet") and are chosen 1-4% of the time. The register, not the meaning.

**E2 s2337's goals default to the most common training shape.** It writes a
hard and a soft term on 61 of 94 hard-only parts (the soft one made of place
words) and an `assume[...]` hard term on 36 of 94 soft-only parts; the other
four checkpoints do either on 0-3 of 94. It writes the `hs` shape -- 60% of
traces -- instead of counting what the request holds. Why this seed alone is
not read here; whether rung 3's own goal column showed it was never scored
by shape.

## Amended 2026-10-07 -- the two causes, tested

Both probes registered before they ran (7cc5da5's
`evals/g5_shape_probe/README.md`; the goal read as stated to the owner),
zero training, about 3.6 min and 20 min of the card.

**Selection follows the clause's form, tested by changing only the form.**
`evals/g5_shape_probe/`: the author's templates copied, one template's `use
when` reworded to open on "a" or not, meaning kept. Choices of 288 on the
four US/USN checkpoints:

                                         share_a_place     trip_stay_and_eat
    as written                               8-34              131-228
    share's clauses opened on "a"          171-250               10-83
    "a trip away" -> "going away on a trip"   8-33                  0-3

When "a trip away" goes, its votes move to the other "a" clause ("a meal and
then drinks with a friend", 243-275). Accuracy stays at chance in every
variant (95-114 of 288). **The form decides and the meaning does not**, as
predicted: arms US and USN trained `use:` on concept clauses that are all a
short "a" noun phrase, and that is what they learned to look for. Cards:
`evals/results/nano20m_v3_fw_templates_*__workers_select_{a_share,no_a_trip}*`.

**E2 s2337's goal habit is its own, on its own task.** Rung 3's probe
(`probe_filter.py`, its 528 rows, bound) on the five checkpoints: E2 s2337
writes the gold goal on 284 of 528 against 522-527 for the other four; on
hard-only rows it adds a wish on 67 of 96, on soft-only rows a limit or an
`assume[...]` on 89 of 144, and it invents wishes no request holds (`goal:
km<3 soft[for an anniversary]`). The others do either on 0-3. So G5 did not
cause it: the seed trained into the majority `hs` shape. Cards:
`evals/results/nano20m_v3_fw_filter_*__filter_goal{.json,_items.jsonl}`.

**What the two say together**, the owner's reading of them: where a failure
has a cause here, it is a feature the training held constant -- one clause
form, a 60% goal shape -- read as the cue. A corpus that varies every
surface feature the label should not depend on denies those shortcuts; the
1.0 corpus is one run, so it is a design rule for every slice, not a fix for
these arms.
