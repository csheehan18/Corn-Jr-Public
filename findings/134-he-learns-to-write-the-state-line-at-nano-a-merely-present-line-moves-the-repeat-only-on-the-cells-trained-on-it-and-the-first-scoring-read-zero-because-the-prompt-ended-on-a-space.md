# He learns to write a summary line of conversation state

**Full result:** He learns to write the state line at nano, sixty-seven and a hundred and one of a hundred and twenty from a floor of one, a value comes from whichever slice carries it, a line merely present moves the repeat on the cells trained on it and not on the others, the line he writes reads as a hand-inserted one on the cell that writes it whole, and the first scoring read zero because the prompt ended on a space token the corpus never wrote

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v3_turn2`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

PLAN-TAG-SPINE phase D, the conversational half, read 2026-09-14. The 2x2
at nano pre-registered in `configs/mix_v3_turn2_state.py`: the state line
on or off (`corn/stateline.py`'s rule over `turn2_v1.txt`, 89,974 lines,
84% `answered` and 16% `open`) crossed with the dependent turn on or off
(`corn/socialgen.py`'s `dependent` kind, 280 pairs, 0.066% of the mix and
under finding 35's floor, which the config says in advance). One seed a
cell, 5,513 iterations, `compile=True` in every cell, the base cell
retrained compiled so the four are mode-matched (EXPERIMENTS §2's eager
caveat is retired by it). `mix_v3` byte-identical across the four -- the
first 130,279,819 tokens of every `train.bin` are the same bytes and only
the turn-2 block differs. Floors on the shipped trunk and the eager nano
base. Full cards; the repeat probe on every cell under three conditions;
one post hoc read, labelled.

## The question

Finding 131's A2: a `state: asked` line hand-inserted above the second
turn of a transcript he never trained on halves the repeat under the route
header (40 to 19 of 192) on the shipped weights. So the record is read when
present. **Does he learn to write it, and does the record he writes move
the repeat?** And beside it, whether the class the repeat is made of -- the
person answers what he asked and hands back -- moves anything at a dose
the config expected to read as a direction at best.

## What was caught before it could count

The first scoring of the state-on cell read `state.value` **0 of 120**, on a
line the cell had seen ninety thousand times, and 100 of the 120 answers
were `{`. The eval prompt ends on `state: ` and the corpus line is `state:
answered`; `bpe8k` writes that as `st ate :` and the one token ` answered`,
so a prompt ending on the space encodes a lone ` ` token (id 32) that no
state line in the corpus ever produced after the colon, and the likeliest
thing after a bare space in this corpus is a JSON brace. The probe's
`--state written` path ended its prompt the same way and read the same
junk. Both now end on `state:`; the value he writes carries its own
leading space and `strip` removes it; the cards below are re-scored. The
lesson is finding 130's at the tokenizer: a prompt that is one token off
the corpus is a prompt about a different corpus, and a zero on a trained
row is the first thing to distrust.

## The state row, re-scored

    state.value (120) / state.value_heldout (60)     value   heldout   by gold value (answered / asked / open)
    shipped 260M social8 (floor)                       1        0       --
    eager nano20m_v3_turn2 (floor)                     0        0       --
    off/off   base, compiled                           1        0       --
    on/off    state                                   67       28       45/48   0/34   22/38  ;  held out 0/8  0/11  28/41
    off/on    dependent                                0        0       --
    on/on     both                                   101       32       47/48  33/34   21/38  ;  held out 6/8  5/11  21/41

**He writes the line.** From a floor of one, 67 and 101 of 120 on the
cells trained on it, 28 and 32 of 60 on hand-written says no corpus
contains. **And a value comes from whichever slice carries it.** The turn-2
slice has no `asked` at all -- a tool say rarely asks -- and the state-only
cell writes `asked` 0 of 34, putting a tool name there instead; the
dependent payload carries 560 `asked` lines at two uses each, and the cell
that has them writes `asked` 33 of 34. Five hundred and sixty lines, under
the dose floor, install a value the ninety-thousand-line slice never
showed. `answered` is at ceiling on both cells; `open` is the weak value
(21-22 of 38), and it is the rule's remainder class.

## The repeat, under three conditions

`scripts/probe_depth.py --probe repeat --arm given --header both --samples
32`, six cases, 384 draws a card, the ruler `corn/socialfam.py`'s
`asked_before`. No line; a hand-inserted `state: asked` (A2's read, on the
trained cells); and the record he writes (`--state written`: the turn-1 say
is put back to him ending on `state:` and whatever he writes is the line
the next turn reads).

    repeats of 384 (route / bare)     no line          hand-inserted `asked`     written by him
    shipped 260M social8 (A2)        102 (40 / 62)       71 (19 / 52)             --
    off/off   base                    74 (33 / 41)       66 (31 / 35)             57 (29 / 28)   junk: a declaration, prose
    on/off    state                   83 (31 / 52)       66 (27 / 39)             26 ( 1 / 25)   route: a declaration line, turn 2 refused 116 of 384; bare: answered/open on 38 of 192
    off/on    dependent               97 (93 /  4)      102 (82 / 20)            132 (90 / 42)   junk: a tool name repeated
    on/on     both                    99 (63 / 36)       78 (40 / 38)             80 (42 / 38)   asked 241, answered 142 of 384

Three readings, in order of how much they can bear.

**A line merely present moves the repeat on the cells trained on it and
not on the others.** Hand-inserted, it takes the state cells down 17 and
21 (83 to 66, 99 to 78), the base down 8, the dependent cell up 5. On the
shipped weights it took 31 off; what the training buys is not a larger
move but a smaller one that is now his own vocabulary.

**The record he writes reads as the hand-inserted one, on the cell that
writes it whole.** The both cell writes a legal value on every draw
(`asked` 241, `answered` 142) and reads 80 under its own record against 78
under ours and 99 under none. The state-only cell writes a legal value on
38 of 192 bare draws and reads 25 there against 52 with no line; under the
route header, where its corpus never put a state line after a social say,
it writes a tool declaration and the second turn refuses 116 of 384 times
where the base refuses 99 -- the 1 of 192 on that half is a degraded turn
and not a read record. So the pre-registered first row -- *he writes the
record and reads it* -- holds within each state cell and **does not take
either below the base cell's own 74**, because the on-cells' no-line rates
sit above it (83, 99 against 74) at one seed.

**The dependent class did not carry the repeat down at this dose**, and
it moved other things hard. Its cells read 97 and 99 with no line against
the state-only cell's 83, with a route/bare split of 93 to 4 on one card
that the next section explains. What 280 pairs at 0.066% *did* move is
the social band: `social.declared_nocall` 13 and 10 on the cells without
them, **69 and 70** on the cells with them; `social.voice` 65 and 52
against 94 and 105; `social.family` 26 and 11 against 46 and 52. The
`mix_v3` nano carries no other social payload, and a class with nothing
competing installs from under the floor -- finding 35's floor was measured
against a slice that had rivals.

## The rows the line rides on, and the base that moved

    of 200/200/120/96/40          eager s1   eager s2   base    state    dep    both      with `state: answered` in the history (post hoc)
    turn2.first                     174        174      174     176      185    179       174   176   185   179
    turn2.second                    192        187      189     182      190    191       192   190   190   190
    turn2.react                     112        117      117     107      115    108       117   109   115   108
    turn2.reask                      57         66       43      29       34     13        38    37    25    24
    turn2.reask_yn                   33         38       40      17       15     14        40    18    15    17
    tool.copy / copy_wide / temporal.copy   120/300/353 at every cell but 119, 299 and 119 once each

**The unreadable clause fired on one row.** The compiled base reads
`turn2.reask` 43 against the eager band's 57 and 66, so that row is read
against a moved base, as the config said it would be. **The kill clause
did not fire cleanly and did not clear.** `turn2.reask_yn` falls from 40
to 17, 15 and 14 on every on-cell -- including the dependent cell, whose
turn-2 bytes are the base's own -- so the fall is not the state line's; on
those cells he answers a yes/no re-ask without the polarity (`no_polarity`
20, 23, 8), which is what a payload of conversational second turns would
teach a cell that has no other. `turn2.reask` under the plain items falls
43 to 29 and 13 on the state cells; under the post hoc read that renders
`state: answered` after every earlier say -- the shape their corpus gave
every say and the one `corn/agent.py` renders back when the words were his
(`--state-history`, stamped on the card) -- it reads 37 and 24 against the
base's 38. Half the state-only cell's fall is the scorer showing it a say
without its line; the both cell's remainder is shared with the dependent
cell (25). One seed a cell, on rows whose eager spread is 9.

## What this licenses

D2 stays as built: the runtime reads the line back, because a line
present moves the cells trained on it. The awareness claim is **a
direction and not a result** -- the pre-registered second seed on the both
cell and on the base is what turns it into one, and the read to beat is
stated: the both cell under its own record below the base cell's no-line
74 at both seeds, with `turn2.reask_yn` inside the eager band. The `asked`
value needs a source in the 1.0 corpus, and the dependent payload is one at
560 lines. The `open` value is the rule's remainder and reads weakest; it
is the first candidate for a definition rather than a default. The
dependent class goes to the social fine-tune at dose, where it was always
going, with the note that under the floor and unrivalled it moved four
social rows by 30 to 60 items.

## Instruments

* The trailing-space token, above: caught because a trained cell read
  zero on its own line, fixed at both prompt sites, the cards re-scored.
* `--state-history` in `corn/evals.py`: one regex over the turn-2 family
  prompts, stamped on the card, a post hoc read and labelled one.
* The repeat ruler is lexical by design (three quarters of the shorter
  question's words, two at least): "How are you?" repeats "how are you
  today", "How about you?" does not, and the dependent cell's 93 to 4
  route/bare split is that phrasing choice under two headers. Read with it
  a count of any question back at all: base 60/58 of 192, state 48/93,
  dependent 114/62, both 78/98 -- the same directions, wider.
* Four cells at 944-959 s each; probes at 22 s a card once the card was
  uncontended; the state-line smoke run before the cells.
* The four hand-inserted probes ran beside the first minutes of the mid-size
  W run's compile; no timing number was read from either.

## Limits

One seed a cell, so directions (rule 6); the base cell moved off the eager
band on one row. Nano, on a mix with no social payload but the dependent
one, which is why 280 pairs read like a slice. The written-record read
puts a hand-written say in front of him and asks for a record of it; the
runtime's condition is a say he wrote. The `given` arm's six cases are
wellbeing openers, the family the defect was reported on and no other.
The held-out say row is hand-written and one of its 60 says ("Any time.")
is also a mined social reply, found by `check_social.py` on the sweep; the
drawn row's says are corpus strings by construction (59 of 120 are mined
replies), which the guard now reads past for that file's `say` and
`prompt` fields alone.
Nothing here touches the shipped checkpoint.

## Amended 2026-10-07 -- the second seed (finding 153)

The pre-registered second seed ran on the both cell and the base. The gate
fails at both seeds, and the direction this finding read does not hold: the
repeat probe sampled unseeded, one card's sd is about 8, and these cards
re-ran at 64 and 84 against the 74 and 80 above. Averaged over four draws,
the hand-inserted line takes 8 off the both cell here, not 21, and at seed 2
it adds 15. **He writes the line (replicated); the record is not read.**
Finding 153 has the tables.
