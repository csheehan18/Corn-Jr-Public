# On real requests the runtime's machinery works but his own parse doesn't

**Full result:** On the real carriers the door works and his cut does not: given the gold parse, the two-note row reads 18 and 26 of 48 from 0 and 2, with his own parse 2 and 7; the forced card's zeros are his parse line where the prompt has none, and the one cost that survives staging is a `chat` label read off the `tools:` header

**Cost:** 70.5 min of training four nano runs (16.7-18.6 min each, `card_cost.py`; registered at ~18 min) and 12.1 min of scoring four standard cards; about 10 min of `prepare_mix` and the guard; `probe_a2.py` about 6 min a checkpoint on the registered rows and about 3 min on the post hoc guard rows, two checkpoints each (10:43-12:52 on 2026-10-04 end to end, against a registered ~2 h).

ROADMAP A2, PLAN-TAG-SPINE §12, pre-registered in `configs/mix_v3_a2_on.py`
before a byte trained (b2ea2ff). The first read of the tag language on the
real carriers: `mix_v3` plus the turn-2 and compound payloads, off against on,
the on cell carrying a `parts:` line (SPEC-LANGUAGE §3) under every user turn
of the six turn-shaped slices, written after the fact from what each turn did
(`corn/parseline.py`; 722,019 lines, 1.86% of the mix, transcripts matched
document for document). Seeds 1337 and 2337, `compile=True`. The owner's
decisions of 2026-10-03: `act` the ninth label (D-A1.21), every no-call turn
`parts: chat`, the role table in the runtime (`corn/door.py`). **Cards:**
`evals/results/nano20m_v3_a2_{off,on}{,_seed2}.json` (forced),
`nano20m_v3_a2_on{,_seed2}__a2.json` and `__a2_items.jsonl` (the staged
protocols), `__a2_guards.json` and `__a2_guards_items.jsonl` (post hoc,
below). `probe_a2.py` is a hand-built instrument held by
`scripts/check_parseline.py` and nothing more: **every staged number is a
bound** (rule 28).

## The registered reading

The off cell is readable: on its own payloads' rows it sits in the
single-payload bases' band (`turn2.react` 116 and 116 against
`nano20m_v3_turn2c`'s 117; `compound.pipe` 45 and 48 against the compound
base's 44 and 47), so the joint mix did not move the floor.

    row                     off forced   on forced    on bound     on gold      on free
    compound.items            0    2       0    0       2    7      18   26       1    4
    compound.items_first      3    2       4    5       7    7      23   21       3    5
    compound.pipe            45   48       0    0      45   29      48   48      45   41
    compound.pipe_first      47   48       5   37      46   35      48   48      48   48
    turn2.chain_ellipsis     47   45      31   31      42   44      42   44      42   44
    turn2.chain_pronoun      21   20      13   10      15   21      15   21      15   17
    turn2.chain_result       48   50      46   49      50   50      50   50      50   50
    turn2.react             116  116       0    0     117  119     120  120     117  119
    turn2.reask              50   32       0    0      53   48      53   48      53   48
    turn2.reask_yn           37   36       0    0      34   33      34   33      34   33
    tool.copy_wide          300  299     299  299      (forced only)

Seed 1337 then seed 2337 in each pair; `compound.*` of 48, `chain_*` of 50,
`react` of 120, `reask` of 96, `reask_yn` of 40.

**The gate** -- `compound.items` under *bound* above the off cell's *forced*
by more than 12, at both seeds -- **fails**: 2 and 7 against 0 and 2, lifts of
2 and 5. **Under *gold* it passes at both seeds**: 18 and 26, lifts of 18 and
24. That is the registered row **"*gold* passes the gate, *bound* does not --
the door works and he cannot cut real requests at nano: the parse is the
runtime's to propose, or 1.x."** The kill did not fire: `tool.copy_wide` 299
and 299 against 300 and 299.

**And by the letter the guard row fires too.** The table registered "a hold or
guard row falls at both seeds, *forced* or *bound*" as a kill for that slice's
tagging, and on the forced card the on cell falls at both seeds on
`turn2.react`, `reask`, `reask_yn`, `compound.pipe`, `tool.selection` (176 and
190 to 125 and 84) and `social.self` (47 and 44 to 0 and 0), among others.
That reading is the record; what it is made of is the next section, and the
owner takes which governs.

## The forced card's zeros are his parse line

Every real row's prompt either ends after the user line or forces the next
line (`<|call|>`, `<|say|>`) straight under it; the on cell trained on a
corpus where that line is always a `parts:` line. **On every forced react and
reask prompt, both seeds, his first line is a parse line** -- `parts: chat` on
117 and 119 of 120 react prompts, 96 and 95 of 96 reask, 40 and 40 of 40
reask_yn -- which the row's scorer reads as "no say". Staged so that he writes
it first (*bound*), the same rows read at the off cell: react 117 and 119
against 116, reask 53 and 48 against 50 and 32, chain_result 50 and 50. **No
registered hold or guard row falls at both seeds under *bound*.** The forced
collapse is finding 134's lesson at scale: a prompt one line off the corpus is
a prompt about a different corpus. The registered table's "*forced* or
*bound*" clause was the error; the on cell's forced card measures the
protocol.

## Post hoc: the forced-only guard rows, staged

The pre-registration read `tool.selection`, `tool.validity` and `social.*` on
the forced card only. After the read above they were staged the same way
(`probe_a2.py --families guards`, written 2026-10-04 after the registered
read; **probe only, post hoc, never a substitute for the registered
reading**):

    row                      off forced     on bound      on gold     falls (rule: below off by more than its 95% half-width)
    tool.selection           176   190     186   182     172  170     seed 2337 only
    tool.validity            172   176     181   181     181  181     no
    social.self               47    44      47    47      20   34     no
    social.bare_nocall        64    58      80    86     112  112     no (above)
    social.declared_nocall     4    68       5     4     112  112     seed 2337 only (the off cell reads 4 and 68)
    social.voice              72    88      47    66      57   85     **both seeds**
    social.family             15    17       7    13      27   24     seed 1337 only

**One row falls at both seeds: `social.voice`** -- his reply to a social
opener, read under a route header. By hand, the cause is the label: **on those
prompts his bound parse is `parts: ask`, 91 and 102 of 112** -- "alright cool",
"how was your day" -- and the say that follows is tool register ("Right, that
no tool covers this request", "Add a meeting | decline() -- ..."). The same
openers with no declaration line (`social.bare_nocall`) are labelled `chat` and
read above the off cell. **In the tagged corpus no `chat` turn ever sits under
a `tools:` line**: counted over all six twins, 0 `chat` and 200,000 other
labels under one (every one toolspace's), 214,518 `chat` and 307,501 other
without -- so the line learned is "a declaration means a task", read off the
header, not the words. That is SPEC §0's coverage
argument (a layer on only some slices is a cue for those slices) arriving one
level down, at a label value. Given the right label (*gold*), the declared
no-call row reads 112 and 112, the door holding the call shut, and the voice
row 57 and 85.

## Read by hand: what fails, where

* **The cut.** On `compound.items` his bound parse is a single bare part --
  `parts: note`, treating both notes as one -- on 37 and 19 of 48; it carries
  the gold labels on 2 and 9. The eval rows join their two notes with "and
  also that", "plus that", ", and another that"; the corpus templates with
  "and that", "and one that", "and another saying", ", then that"
  (`corn/turn2gen.py`). He does not cut at a connective he never saw cut. When
  he does cut he is sometimes right (`note[note down the landlord's office
  shuts at half four] note[that the spare key is with the neighbour]` -> both
  notes, passed) and sometimes runs into nesting the grammar still allows
  (`note[note[note[size act[note[note[is]]]]]]`). `compound.pipe` at seed 2337
  fails under *bound* the same way -- `parts: ask`, or the whole request
  wrapped in one `find[...]` -- so after the search no note part is left and
  he says instead (19 of 19 failures `said_instead`).
* **The extent, under *gold*.** With the right cut the door makes him write
  the second note, and the remaining failures are where the copy ends: of
  `wrong_text`, 19 of 20 and 10 of 14 are spans of the request cut short ("the
  filter size is twenty by twenty", "-five" dropped; "the good parking"), and
  `wrong_contact` copies too much ("Thaddeus saying call me when you're
  free"). The copy half admits any span of the part; nothing says where a note
  ends.
* **Two ways round the copy half, an instrument hole named:** at seed 2337 the
  door let through `"contact": "Free"` and `"contact": "You"` --
  a JSON escape and a capital the request does not have. The call object's
  copy rule still folds case both ways and decodes escapes (SPEC-LANGUAGE
  D-A1.14: `span_ok` until H3). Every *gold* number is a bound for that reason
  too.

## What it licenses -- for the owner

* **The parse is the runtime's to propose on real carriers at nano** (the
  registered row), or 1.x: the door carries what a right parse gives it
  (`compound.items` 0 and 2 to 18 and 26), and he does not write the right
  parse for a connective he never saw. D7's row for the parse line reads:
  *the door is worth riding; his cut is not yet*.
* **The registered forced-clause kill reads the instrument**, by the hand read
  above; the owner decides whether it governs. If it does, the tagging of
  `turn2`, `compound`, `tools`, `toolspace` and `chat` is killed in this form.
* **Two fixes the record now names, neither made here:** the corpus puts
  `chat` turns under `tools:` lines (a social or chat turn inside a declared
  transcript), so the label stops being read off the header; and the door gets
  an extent rule -- a note's text runs to its part's end, a contact stops at
  the contact -- PLAN-EXTRACTION-READER's extent problem in the door.

## What it does not say

That the parse cannot be learned on real carriers: one dose (1.86%), one set
of templates whose connectives the eval does not share, nano. That the door's
lift is the parse line's: *gold* inserts a line the off cell never sees, so
*gold* against off forced is the door plus the line. That the staged guard
rows are the registered reading -- they are post hoc. Anything at 260M.
