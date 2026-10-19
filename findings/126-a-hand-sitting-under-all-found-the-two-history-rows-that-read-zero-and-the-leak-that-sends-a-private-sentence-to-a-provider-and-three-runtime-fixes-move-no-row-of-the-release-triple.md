# A hand-driven session found a chat turn sent out as a search

**Full result:** A hand-driven sitting on the shipped 0.5 checkpoint hit both history rows that read zero in the release table, found a chat turn leaving the machine as a live search query, and closed three of it in the runtime with every row of the release triple identical afterwards

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_v4_ft_social8`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

Roughly 120 hand-driven turns on `corn_jr_260m_v4_ft_social8` over two
sittings on 2026-09-07 — one table-backed, one `--all` — plus five grids
written during the sitting and one committed as
`scripts/probe_social_leak.py`. No training, no checkpoint moved, no
threshold moved. The three fixes are `corn/agent.py` only; the release triple
was re-read on the release conditions afterwards and every measured field in
all three cards is identical to the `0c48261c` cards.

**This finding is an outside read, and that is what it is for.** Every number
in `docs/RELEASE.md` was read by an instrument this project wrote, against a
distribution this project chose. What a sitting adds is the distribution
nobody chose.

## 1. The two rows that read zero, and why the grids do not see them

`docs/RELEASE.md` gates decision 6 on `historygrid` reading
`reissued_query` **0/36** and `reissued_utterance` **0/72** at depth 1 and
depth 3 alike. Both were hit by hand inside an hour, and both reproduce
deterministically at temperature 0.

**`reissued_utterance`.** A prior turn answered by *code* rather than by a
tool call:

    > whats my birthday
    I don't have your birthday written down. A birthday: line at the top
    of packs/about-me.md is where it goes.          [1 ms, no call]
    > what do i do for work
    -> web_search {"query": "whats my birthday"}

The control — the same second utterance with no history — routes correctly.

**`reissued_query`**, three runs of three:

    > what is the currency of japan          It's the yen.
    > what about india
    -> web_search {"query": "what is the currency of japan"}
                                             It's the yen.

**The proposed account, and it is a hypothesis rather than a result.** The
grids build histories in which the prior turn *called a tool*. A turn the
temporal or persona hatch answered leaves a history entry with a user line and
a reply and **no call in it**, which is a shape the grid does not generate. If
that is the mechanism, both rows are correct about what they measure and
neither is a statement about a conversation with hatch-answered turns in it —
which is most conversations, because the seed turn makes turn 1 one of them.
Not fixed here, and it is the cheapest thing in this document to test: add a
call-less prior turn to `historygrid`'s history builder and re-read the two
rows.

**Follow-up composition, measured while there.** Five "what about X" pairs,
each after a question of a different shape: **1/5 composed with no filler turn
and 1/5 with one**, and the one that composed is `france → spain`, which is the
pair this project's own documents use as the example. The other four fail three
different ways — the query passed through verbatim ("A number of songs are
about Mexico."), the previous query reissued, and a generic fact page. The
filler turn changing nothing is consistent with PLAN-CONVERSATION's memory
probe. **The reissue is the worst of the three**, because it returns a
correct-sounding answer to a question nobody asked: "what about india" →
"It's the yen." is indistinguishable from a right answer without reading the
tool line.

## 2. The leak: a private sentence going to a provider

Under `--all`, second turn of the first conversation of the sitting:

    > bit tired today, long week
    -> web_search {"query": "bit tired today"}

**The cause is hatch coverage, not the router.** `conversational_reply` matches
a *whole* normalised utterance against six frozen sets — deliberately, and
`GREETINGS`' own docstring gives the argument, which is that a prefix rule
swallowed "ok do it". But people do not type one social move per turn. Neither
`bit tired today, long week` nor `pretty good. bit tired though, long week` is
in any set, so both fell through to the model, which routed them, which sent
them to `en.wikipedia.org`.

This is the seventy-eighth finding's species — *a hatch miss is not a worse
answer, it is a different system* — on the family that finding did not probe,
and with the sharper cost: `--all` is what a friend will run, so the miss is
outbound rather than merely wrong.

## 3. What the reader's floor sounds like when it is not an answer

`--extract`'s floor is the provider's lead sentence, and
`_web_search_read`'s docstring calls it "never the casualty" — true, because
the floor can only replace an extraction that found nothing. It is **not**
true against saying nothing. Live, of 21 questions the provider answered,
**16 were right and every one of the five wrong ones was the lead sentence of a
wrong or generic article, delivered in the same voice as "It's Tokyo."**:

    who is the prime minister of canada   It's the head of government of Canada.
    what is the speed of light            It's fifth book of narrative Spanish
                                          writer Javier Cercas.

The second is a Javier Cercas novel of that name. **The grounding rule is not
what failed** — in ~120 turns the model was never caught asserting a fact the
observation did not carry, which is what four findings bought and it holds.
The guarantee is "he will not make it up", and the sitting's result is that
this is **not** the same guarantee as "he will not be wrong", and that nothing
in the delivery distinguished them. `fell_back` was already on the say event.

## 4. The frame's seam

`SAY_ANSWER`'s `It's {a}.` is a trained framing reproduced by the reader, so
what lands in `answer` is the frame with an extracted span dropped into it,
and the two do not always meet: `It's The yen.`, `It's The Pacific Ocean.`,
`It's it is part Flying type.` Four live instances.

## 5. The three fixes, and what each is allowed to do

All in `corn/agent.py`. None touches a threshold, a checkpoint or a default.

**(a) The hatch, two widenings.** `_SOCIAL_TAIL` strips trailing fillers
("today", "honestly", "though") and `_SOCIAL_JOIN`/`_social_run` splits a run
of social moves — **and each is accepted only if what remains matches a pool
whole**, which is the whole-utterance rule applied per fragment rather than
relaxed. So "rough day, note that I'm skipping the gym" still routes, and
`check_hatches.py` now asserts that over eight request-carrying sentences. The
tail strip also closes the leak `LOW`'s own docstring names as open — "I'm
kind of tired today honestly", recorded there as getting "a different wrong
move on every checkpoint" — which needed the crossed pool entries
(`i'm kind of tired` beside the `i'm tired` and `kind of tired` already there)
before it had anything to land on.

`conversational_reply` and `social_family` were the same test written twice and
are now one function, `_social_hit`. The duplication was live: the widening
would otherwise have landed on the hatch and not on the family check.

**And the run rule is narrower than the argument for it, because `check_turn2`
said so.** The first version claimed "alright, much appreciated", "great, much
appreciated" and "lovely, much appreciated" — which `corn/turn2gen.py` builds
as class-A reactions from `REACT_CUES` × `USER_REACT_ANY`, and which the
turn-2 slice therefore *trains him to answer*. That is rule 4 exactly: the
runtime composing what the corpus teaches. Restricting a run to
`_RUN_FAMILIES` = {consolation, greeting, wellbeing} — the three a miss was
measured to cost a live query on — resolves it without an exception list, and
an ack followed by a thanks has never reached a provider because both halves
are already matched whole.

**(b) `FELL_BACK_FRAME`.** A fallback is spoken as one. Gated on exactly the
condition the `fell_back` field is gated on, so the sentence and the column
cannot disagree about which turns fell back, and the say author flips to
`runtime` — `SAY_AUTHORS`' argument, since these transcripts are training
data.

**(c) `tidy_frame`.** Two seam repairs, applied where the reader's answer
enters the payload so the observation and the spoken sentence carry the same
string: a repeated copula (`It's it is X` → `It's X`) and a capitalised article
**only when the next word is lowercase**. The ambiguous half is left alone —
`It's The Hague.` is a proper name and nothing in the runtime can tell it from
a typo except by what follows, so the cost taken is a stiff sentence rather
than a lowercased name. Neither word it can drop can carry a fact and both are
in `corn.extract.FRAME`, so `grounded` reads the repaired answer as it read the
unrepaired one.

**One over-reach, caught by its own row.** The first copula pattern included
the possessive `its` and turned "It's its own thing." into "It's own thing." —
the repair inventing a defect. It is a regression row in `check_agent.py` now.

## 6. What the fixes cost, measured

**The release triple, re-read on the release conditions** (`--packs "" --book
"" --tools-dir "" --no-log`), against the `0c48261c` cards field by field:
**every measured field is identical.** `checkup` routed 16/19, executed 14/14,
`spoke_from_tool` 8/8, `held_back` 2/5, `named_right` 2/3; `converse` `in_kind`
14/16, `said_something` 16/16, `fresh` 10/10, `carried_over` 2/3; `toolgrid`
A 170/176 and 23/24, B 390/400 with contact 388/390 and message 171/173,
C 169/176 with `kept_text` 142/169. The only fields that differ are the scratch
path, the revision and the timestamp. **`toolgrid`'s closing line still reads
"no turn was answered by a runtime hatch"** — the widened hatch claimed none of
its 808 turns, which is the number that matters for (a).

**`check_all.py`: 70 ran, 2 failed** — `check_churn` and `check_copyable`,
both confirmed failing on the unmodified tree.

**Live, `scripts/probe_social_leak.py`:** leak grid **8/8** answered without a
lookup (was 0/8 on the two recorded utterances), cost grid **7/8**, fallback
frame **5/6** with the sixth a real answer that correctly did not fall back.

**The note grids do not move**, and that matters because it says (a) bought
nothing on the tool side: canonical `save_note` requests read **12/12 → 10/12 →
9/12** on empty / one chat turn / two chat turns of history, exactly as before,
with every failure a `pick up the …` payload. Twenty-one requests across all
tools read 19/21 either way.

## 7. What is not fixed, said plainly

* **Retrieval.** "who is the king of england" → "It's Alfred the Great." has no
  `fell_back` on it — the provider returned the wrong article and the reader
  read it correctly. The frame does not reach these and should not.
* **A lead that is not prose.** One live instance: the currency-of-Japan
  passage was a category page, so the frame honestly reads out
  "Circulating currencies Currency symbols … Hidden categories:". The
  `LEAD_ANSWERS is False` path already takes the honest miss for the deep
  path's own case and is the place to extend.
* **The `pick up the …` note class**, and follow-up composition at 1/5. Both
  are corpus, both are named in `docs/PLAN-1-0.md`, and neither is a runtime
  fix.
* **The consolation reply's register.** The hatch now claims "rough week,
  honestly" and he writes the reply himself; one draw of it was "I'm sorry to
  hear that you're not happy with the product." Pre-existing — the same
  call-centre bleed answered a bare "morning" before any of this — but the
  widening puts more turns on the path, so `family_rejection`'s consolation
  arm now has more to gate. Not counted as caused here and not fixed here.

## 8. What this says about the release table

Nothing in `docs/RELEASE.md` is withdrawn: every number reproduced, twice,
including under the changes. What the sitting adds is that **two rows read zero
because of what their grid generates**, and the honest statement of decision
6's gate is now "nothing reissues in the shapes `historygrid` builds" rather
than "nothing reissues". The instruments are not wrong; the distribution is
narrow, and a hand sitting is cheap next to what it caught.

Left unexplained: why `pick up the …` specifically collapses to `decline`
after a chat turn while `take out the bins`, `drop off the parcel` and
`pick up milk` do not — a phrasal verb whose particle is shared with
`place_call`'s register is the obvious guess and it is only a guess.
