# One hundred and fifty-seventh finding — A3, the move line: written before the say, it steers the reply at both seeds (a forced move that is not the item's own is followed 509 and 552 of 580 times against 133 and 182 off), it beats the regex it would replace, and it costs no routing row at both seeds; the install gate splits, 84% and 64% of trained phrasings, carried by the thinnest family; unseen phrasings default to one value, and the reply follows the wrong label as faithfully as the right one

**Cost:** 60.0 min of training four nano runs (14.9-15.1 min each, `card_cost.py`; registered at ~16 min) and 13.5 min of scoring four standard cards; `probe_move.py` about 1 min a checkpoint, its post hoc pass about 26 s, the repeat probe 12-15 s; two mix builds about 10 min on the CPU; the build and the rulers' floors about 45 min (17:01-18:55 on 2026-10-09 end to end, against a registered ~1.5 h of card time -- the card time came in at ~1.4 h).

ROADMAP A3, PLAN-TAGS §9, pre-registered in `configs/mix_v3_a3_on.py`
before a byte trained (1c19480). **The one variable is the `move:` line**
(`corn/moveline.py`, SPEC-LANGUAGE §4): the same 14,568 declared social
transcripts -- arm 11's recipe at four times its pairs, 1.8% of `mix_v3` --
trained once with a `move: <family>` line under every social user line and
once without, two nano seeds a cell (1337, 2337), `compile=True`. 16,586
move lines, 5.9 tokens each, 4.0% of the slice; `thanks` 6,317, `wellbeing`
3,116, `greeting` 2,631, `ack` 2,421, `open` 1,513, `consolation` 588,
`farewell` none. **Cards:** `evals/results/nano20m_v3_a3_{off,on}{,_seed2}.json`
(standard), `__a3.json` and `__a3_items.jsonl` (the staged probe),
`__a3_posthoc.json` (post hoc, below); `harness/results/*__depth.json` (the
repeat). `probe_move.py` is a hand-built instrument held by
`scripts/check_moveline.py` and nothing more: **every staged number is a
bound** (rule 28).

## The registered reading

The arm is readable: the off cells' declared social openers take no call on
104 and 99 of 112 (the unreadable bar was 68 -- A2's off cells, with no
social slice, read 4 and 68).

    gate         row                         off      on       off s2   on s2    verdict
    installs     tag.trained (of 104)         19       87       20       67      84% PASS / 64% fail
    conditions   forced.cf (of 580)          133      509      182      552      +64.8 / +63.8 points: PASS, PASS
    replaces     off family.forced, on tag.marked (of 140)
                                              78       98       69       74      ok, ok
    routing      route.social (of 112)       104      101       99      105      holds, holds
                 route.low (of 28)            18       19       19       24      holds, holds
                 tool.selection (of 200)      46       87       90      106      holds, holds
                 tool.validity (of 181)      149      138      149      151      FALLS (by 1), holds
                 tool.copy_wide (of 300)     291      295      289      296      holds, holds

**By the table, the reading is "seeds split on a gate -- a direction"**:
`conditions` and `replaces` pass at both seeds, no routing row falls at both
(the kill needs both; `tool.validity` falls by one item at seed 1337 only),
and `installs` splits. The registered row "the move line rides in 1.0"
needed all four at both seeds, and this arm does not license it as written.
No third seed was pre-registered and none is run.

## The split is the thinnest family

    tag.trained by family     greeting  wellbeing  thanks   ack     consolation
    on, seed 1337             20/20     20/20      20/20    14/20   13/24
    on, seed 2337             16/20     19/20      20/20    11/20    1/24

Without `consolation` the four well-supplied families read 74 and 66 of 80
(92%, 82%). `consolation` is 588 of 16,586 lines (3.5%) -- the generator's
supply rule holds it to its 21 usable replies -- and it is 24 of the cell's
104 items (23%). At seed 2337 sixteen of its 24 are written `open`.

**Read on the frames the slice trained on (post hoc, EXPERIMENTS §5.6),
it installed at both seeds:** 194 of 200 single-turn slice transcripts cut
after the user line, at both seeds (off: 101 and 110, its prior); the same
carriers under the eval's declaration 188 and 186. So the gate's miss is the
eval cell's weighting of a thin family, not a failure to learn the line --
which is the hand read and not the registered reading, and the finding says
both.

## The line steers the reply -- harder than the utterance does

Every item under each of the seven move lines in turn, then `<|say|>`
(`forced`): the reply answers a forced move that is *not* the item's own on
509 and 552 of 580 draws, against 133 and 182 on the off cells, which
inserted the same line untrained (the word alone primes "thanks" there on
140 of 140; the shipped 260M follows 197 of 580). Read by hand, the forced
reply is the move's prototype whatever was said: forced `wellbeing` gives
"I'm doing well, thank you. How are you?" to "rough day at work", forced
`consolation` gives "I'm sorry to hear that." to "got it". **The label
outweighs the utterance** -- which is what makes it worth writing, and what
makes a wrong one expensive. `farewell`, never trained, is followed 0 of
120 at all four checkpoints; forced, it often reads as a refusal ("I'm sorry,
but there's nothing I can do.").

## Unseen phrasings default to one value

    tag.probe_trained (100 unseen phrasings of the five trained families,
    PLAN-TAGS §10's set, under the eval's declaration)
      off 15, on 32; off 20, on 20
    post hoc, under the slice's own declarations (200 draws)
      off 28, on 74; off 40, on 92

What he writes on a phrasing he has not seen is mostly one value, a
different one at each seed: `greeting` at seed 1337 (16 of 20 farewells, 12
of 20 wellbeing questions, 11 of 20 acknowledgements), `open` at seed 2337
(77 of 120 -- PLAN-TAGS §5's escape, the honest label for a move the list
does not name, which is what it was defined to be and which one seed found).
Rung 0's reading (PLAN-TAGS §10, not a finding: 0.902 trained against 0.475
unseen off the shipped vector) holds for the written label: **it is attached to the
phrasing, and the runtime cannot trust it on a phrasing no pool holds.**

And because the reply follows the label (above), the label's error carries
into the reply (post hoc): on the 120 unseen phrasings the reply answers the
right family 37 and 25 times under his own label, against 32 and 20 for the
off cells under the card's forced `<|say|>` -- level -- and 90 and 100 times
under the gold label. The line neither helps nor hurts what he says on
unfamiliar phrasings; **naming the move is the whole bottleneck**, and the
reply would follow a right name nearly every time.

## The cue D-A1.11 named -- real, and not where it was predicted

Registered: a header cue (the line written under a declaration and rarely
without one). **It does not read that way**: on bare openers he writes it on
103 and 79 of 112 against 101 and 105 declared, and tags them about as well
(90 and 79 of 104 bare, 87 and 67 declared).

Post hoc, on the chat slice's own turns -- SODA openings, trained in both
cells with no move line (D-A1.11) -- he writes it **0 of 200 at both seeds**,
and still 0 with the `<|day|>` line removed (187 and 199 go straight to a
say). So the line is read off the *register*: a short social carrier gets a
move, a scene opening ("Hey, Mattea. What's up?") does not -- the slice it
was left off is the shape on which it is absent. D-A1.11's cost is real; it
is a register cue, not a header cue.

## The repeated question does not fall -- it rises, and the right family is why

Predicted unmoved (PLAN-TAGS §2). `probe_depth.py`, eight draws a case at
the shipped 0.3, the on cells with `--move written`:

    repeated / askable     own/route   own/bare   given/route   given/bare
    off                    14/38       12/32       6/48         16/48
    on                     12/47       22/47      24/48         17/48
    off, seed 2            3/27        1/22       32/48         21/48
    on, seed 2             35/47       20/48      35/48         24/48

The off cells swing 6 to 32 between seeds on one arm, so these are
directions: the on cell re-asks as often or more on seven of eight arms.
**By hand (seed 1337, given/route):** to "good thanks, yourself?" the on
cell writes `move: wellbeing` and answers in the slice's wellbeing register
-- "I'm doing well, thanks for asking. How's your day going?" -- which
hands the question back; the off cell's commonest reply to the same turn is
"No problem. I'm happy to help." (8 of 48), a thanks reply that asks
nothing. **The line makes him answer the move that was made, and the
slice's answers to that move ask back** -- 396 of 492 mined wellbeing
replies do (`configs/mix_v3_turn2_state.py`, the dependent class's case). The repeat is the
corpus's, and the line amplifies whatever a family's replies carry.

## Instrument notes

* **The standard card cannot read an on cell's social rows**, as the probe's
  docstring registered: it reads one line, so `social.open` reads 0 of 78 and
  `social.self` 10 and 2 of 47 on the on cells' cards -- the first line is
  `move: open` -- against 52 and 69 (open) under the staged route.
  `check_moveline.py` states the hole as a check.
* **Every move line he writes is followed by a say** (60 of 60, 60 of 60,
  101 of 101 at seed 1337), so on an on cell the route is decided at the
  first token: a call, or `move:`. Seed 1337 called on 13 more of the 120
  unseen phrasings than its off cell and 11 more of the 78 open moves (net);
  seed 2337 called on 9 and 8 fewer. No direction.
* `tool.selection` reads 46 and 90 on the off cells against 128 on `mix_v3`
  with no social slice -- the payload's own cost, both cells alike, and the
  on cells read above it at both seeds (87, 106).

## What it licenses -- for the owner, at D7

* **The move line is load-bearing at nano**: written on trained phrasings,
  followed by the reply at both seeds by more than sixty points over a
  control that saw the same word, better than the regex it would replace,
  no routing kill. By the registered table it is a direction, not a pass --
  the install gate splits on the thinnest family.
* **What it cannot do is the generalisation the thesis asks for**: on
  phrasings no pool holds it writes one default value, and the reply follows
  that value. If it rides, the runtime must not trust it there -- PLAN-TAGS
  §6's comparison against the detector is the guard -- and the corpus needs
  carrier variety per family (`diversity-denies-shortcuts`) more than it
  needs the line.
* **Two corpus consequences, named before the freeze:** labelled moves on
  the conversational register too (C1's conversations carry gold moves), or
  he never writes the line where people talk like the chat slice; and a
  thin family under the supply rule does not install -- `consolation` needs
  more distinct replies, not more draws.
* **The repeated question is the slice's replies, amplified**: the line
  makes the family right and the family's replies ask back. The dependent
  class (`social_dep`) is where that is fixed, not the line.

## What it does not say

Anything at 260M (nano flips sign there, finding 51; D11's pilot is where it
is read). That the line installs with a fuller `consolation` -- untested.
That the post hoc frame reads are the registered reading -- they are not.
That the move line helps the reply on unfamiliar phrasings -- it is level
there.

## Amended 2026-10-09: why it fails, read on the four checkpoints (post hoc)

Four reads, no training, written after the registered read and labelled post
hoc wherever they are quoted (`probe_move.py --swap`, and the items files
already on disk). Each answers a failure above with a cause.

**Why the line steers so hard -- the corpus made the move sufficient.** The
slice draws every reply from its family's pool independently of what was
said (`corn.socialgen._draw_reply`), so in the training data the move tells
you everything about the reply and the message adds nothing. The swap read
holds the item's gold move and replaces the message (`__a3_swap.json`):

    reply after the message is replaced     off     on      off s2   on s2
    word-for-word the same (of 140)
      another message of the same family    19      32      27       75
      a message of another family           14      39      19       71
      a request ("set a timer for ...")      4      27      28       51
    still answers the move it was given     26      99      36      116
      (another family's message)

By hand: under `greeting` the on cell answers "set a timer for ten minutes"
with "Not bad. How are you doing?"; under `thanks`, "copy that" and the
timer request both get "No problem, I'm glad I could help." The off cell's
replies move with the message. He has not stopped reading -- the wording
still shifts on most swaps at seed 1337 -- but the move outranks the message.
**This one cause accounts for three readings above**: the steering (+64 and
+65 points), the narrow replies (under the gold move 25 greetings get 6 and
2 distinct replies, 28 low moods 7 and 2, against 15 and 12, 14 and 19 off;
the slice carries 272 and 21), and the repeat (the wellbeing pool asks back,
and the move picks the pool). How hard the line steers is a property of the
slice it rides on, not of the line.

**Why unseen phrasings fail -- he falls to a default, not to a neighbour.**
A letter-trigram lookup against the slice's 2,913 distinct tagged user lines
names the move of 49 of the 100 unseen phrasings; he names 32 and 20. Of his
wrong labels only 13 of 68 and 9 of 80 are the nearest phrase's move: the
rest are the seed's default (`greeting`, `open`). The label is recognition of
a trained phrasing, narrower than surface similarity; 446 distinct greeting
lines and 136 consolation lines are not enough to teach what the move is.

**Whether his confidence gives him away -- at one seed.** The gap between his
best and second-best option (summed NLL) is 3.66 and 3.36 median when right
on trained phrasings, 1.38 and 0.48 when wrong. Trusting a label only at a
gap of 3 or more keeps 104 of 298 labels at 90% right and flags 100 of 110
wrong ones at seed 1337; at seed 2337 it keeps 129 at 83%, because its wrong
labels on unseen phrasings are confident (median gap 2.14 against 1.69 for
its right ones) -- they are its default, `open`.

**`open` is doing two jobs.** PLAN-TAGS §5 made it both the open move (a joke,
a view) and the escape for a move the list does not name. Read as "don't
know", the seed split mostly closes: on trained phrasings each seed is right
on 85% of the labels it commits to (87 of 102, 67 of 79), seed 2337 abstaining
on 25. But the reply follows `open`'s register: seed 2337 answers "barely
slept" with "I'll have to go to the park. What's next?". An escape the reply
obeys is not an escape; the runtime would have to take the reply over when
he writes it.

## Amended 2026-10-09 (second): is what he says coherent, and who should name the move (post hoc, no GPU)

**His own reply, the move his to choose** (the probe's staged route, off
the items files): it answers the move that was made on 82 and 75 of 104
familiar phrasings against 67 and 54 for the off cells -- so on the turns he
knows, the line makes him *more* coherent -- but it answers the kind of turn
and never its content: "my mom is sick" and "my cat is sick" get the same
"I'm sorry to hear that. What's been going on?". On the 100 unseen phrasings
it answers the move on 26 and 18 (off 21 and 10) and declines on 44 and 31
(off 37 and 37); read by hand, "you in good form" gets "I'm sorry to hear
that. What's been going on?" under a `greeting` label and "life treating you
well" gets "I'll take the spoken date. What's next?" under `open`. No
farewell is answered as one, on or off.

**Who names the move** (`probe_move.py --trust`, `__a3_trust.json`). The
shipped runtime's own test is `corn.agent.social_family`, an exact match
against the hatch pools. Right / wrong / none of four policies:

                         detector     his          both         guarded (gap 3, `open` = none)
    familiar (104)       92/0/12      87/17/0      98/6/0       92/0/12
                                      67/37/0      92/12/0      92/0/12
    unseen (100)         0/0/100      32/68/0      32/68/0      13/4/83
                                      20/80/0      20/80/0      3/0/97
    open moves (78)      0/0/78       58/20/0      58/20/0      0/3/75
                                      76/2/0       76/2/0       0/0/78

(seed 1337 above, seed 2337 below.) **Where the detector fires it is never
wrong** -- on these items by construction: the familiar carriers are the
hatch pools. **Where it is silent his label is the only source, and it is
reliable for one move and not the others**: right on 58 and 76 of 78 open
moves, wrong on 68 and 80 of 100 unseen phrasings of the five others. The
guard (a confident label, `open` read as don't-know) keeps the wrong count
near zero and buys almost nothing (13 and 3 of 100) -- and throws away the
open moves he gets right. And because the reply follows the move, the turns
the detector covers are better served by the runtime *writing* the move
than by trusting his: under the gold move his reply answers it on 111 and
120 of 140 against 95 and 82 under his own. That is SPEC §0's rule -- a
line the runtime can compute is the runtime's -- arriving at the move line
on the turns the hatch knows.

## Amended 2026-10-09 (third): the conditions count was inflated -- corrected

A blind second read of the raw cards (a separate analyst, CPU only, not
shown this finding) caught it, and it is confirmed here. `forced.cf` counts
a reply as following the forced move when that move is *among* the families
`reply_families` reads in it -- and many replies carry two ("No problem, I'm
glad I could help. How are you doing?" reads as thanks and wellbeing): 324
and 302 of 980 forced replies on the on cells, 145 and 122 off, and in the
slice itself 2,653 of 6,317 thanks replies and 1,832 of 3,116 wellbeing
replies. Such a reply "follows" two forced moves at once. **Counting only a
reply whose sole family is the forced one:**

                                    off     on      off s2   on s2
    forced.cf, registered (loose)   133     509     182      552     of 580
    forced.cf, that family alone    114     271      99      365

+27 and +46 points instead of +65 and +64. **The gate still passes at both
seeds** (its bar is 10), so the registered reading does not change; every
size quoted above for the steering is the loose count and overstates it.

Two more points from the same read, both checked against the cards:

* **The conditions gate could hardly fail on this slice.** The slice makes
  the move a sufficient statistic for the reply (the first amendment), so
  teacher forcing all but guarantees the reply follows the line. The
  contrast that says what the line *buys* is his own label against no line:
  his reply answers the move made on +15 and +21 more of 104 familiar
  phrasings (82, 75 against 67, 54) and +5 and +8 of 100 unseen ones.
* **Labelling tracks how often a phrase was seen** (the second analyst's
  count of exposures per normalised carrier in the slice): carriers seen 61
  or more times are labelled 47 of 47 and 45 of 47; carriers seen 10 or
  fewer, 9 of 17 and 0 of 17. A bag-of-words classifier trained on the
  slice's user lines reaches about 37-44 of 100 unseen phrasings (its
  figure, not re-run here) -- the nets read no better than counting words.

## Amended 2026-10-09 (fourth): how much the runtime's detector covers, and how much the seven tags cover, on natural openings

Asked because the second amendment's plan -- the runtime writes the move
wherever its detector fires -- is only worth what the detector covers, and
the second analyst named under 30% as the coverage that would change the
plan. No GPU.

**Natural dialogue.** 150 first user turns of the chat slice (SODA scene
openings, `data/raw/chat_day.txt`'s first 12 MB, `random.Random(20261009)`),
each labelled by hand with the move the reply must answer --
`evals/results/a3_soda_moves_hand.json`, one labeller (Claude), the
owner's labels may differ:

    share (news, feelings, excitement, a volunteered view)   34
    request (a task, a question for information, "can we talk")   24
    consolation 15   wellbeing 13   greeting 12   thanks 10   open 9   ack 2   farewell 1
    other (concern for the listener, an offer, congratulations)   15
    complaint 8   apology 7

**`corn.agent.social_family` names a move on 0 of the 62 that make one of
the seven, and fires on 0 of 150.** It is an exact match against short
stock forms: "hey, how's it going?" is a greeting, "Hey Timothy, how's it
going?" and "hey how's it going" are nothing. On the owner's own typed
turns (`Saved Sessions/turns.jsonl`, multi-turn sessions typed at human
pace, counts only -- no text read) it names a move on 8 of the 26 turns he
answered without a call, all short stock greetings and thanks. **So the
runtime writing the move covers stock phrasings and almost nothing a
person says at length**; the move on natural turns is his to name or
nobody's, and that is the labelling the arm read at 20-32 of 100 unseen.

**And the seven tags cover half of the social turns.** Of the 126 openings
that are social at all, 62 are one of the seven and 64 are not: sharing
news or a feeling is 34 -- more than any tag in the set -- complaints 8,
apologies 7, and 15 more (concern for the listener, an offer,
congratulations). With `open` as the residual it would take half of every
social turn, and because the reply follows the move, half of all social
replies would be `open`'s. These are scene openings between people, not
what people say to an assistant -- the distribution there is unmeasured --
but on the only natural sample in the repo the set is too narrow by half,
and the largest missing move (`share`) is larger than any present one.

## Amended 2026-10-09 (fifth): the summed tag score leans short, by a little; and the slice held more than the nets took

**The instrument.** `tag_of` sums the NLL of the whole `move: <value>` line,
and the values differ in length on `bpe8k` (` open`, ` thanks` one token;
` gre et ing`, ` well be ing`, ` cons ol ation` three). Re-scored on the
value tokens alone (`probe_move.py --tagscore`, `__a3_tagscore.json`):

                          summed    per-token mean    first token
    trained (104)         87  67    91  75            92  69
    unseen (100 + 20 fw)  32  20    37  26            36  19
    natural (62)          33  28    28  31            48  30

(seed 1337, seed 2337.) The short-value lean costs the unseen cell 4-6 items,
not the gap: under every scoring he names fewer unseen phrasings than a
bag-of-words classifier fit on his own slice's tagged lines does
(`scripts/probe_move_gate.py`: 48 of 100). **The slice held the word
evidence and the nets did not take it** -- at nano, on one pass, the label
is memorised per phrasing. First-token scoring -- the choice a grammar-bound
greedy decode makes -- reads natural openings 48 of 62 at seed 1337, and is
reported beside the summed score from A3b on. The untrained floor's first
token prefers ` f` (`farewell`, 19 of 20 goodbyes at both off cells), a
generic token: no scoring is free of a floor.
