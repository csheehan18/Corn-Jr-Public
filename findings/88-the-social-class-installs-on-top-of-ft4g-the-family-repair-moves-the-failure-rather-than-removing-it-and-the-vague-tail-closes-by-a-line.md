# Social replies install by fine-tune; the fix moves failures elsewhere

**Full result:** The social class installs on top of ft4g, the family repair moves the failure rather than removing it, and the vague tail closes by a line

**Cost:** 0 s of new scoring on record; it reads 2 cards scored for an earlier finding (`corn_jr_260m_v4`, `corn_jr_260m_v4_ft4g`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

**The declared social turn, `docs/PLAN-SOCIAL-SLICE.md`, three fine-tunes of
`corn_jr_260m_v4` on the 3080 over 2026-09-01 and 2026-09-02, one seed each.
The second seed the plan pre-registered was passed over by the owner on
2026-09-02 and this finding is written on one seed per arm; every number
below is one checkpoint's, and is quoted as that.**

## The class the corpus had zero of

No transcript in `mix_v4_5b` put a declaration above a `<|user|>` answered by
`<|say|>` with no call — a hard zero over six marked slices at 60MB each — and
the runtime assembles exactly that context on every social turn. Measured on
the shipping checkpoint over `evals/social.jsonl` (112 items, three prompts
each), the declaration cost **12.5 points of abstention** on identical
carriers and collapsed a five-tool spread onto `decline`:

    social.bare_nocall        53/112   47.3%    web_search 28  resolve_date 12  decline 12
    social.declared_nocall    39/112   34.8%    decline 47  web_search 26

The slice that supplies the class is 1,821 matched pairs on one declaration
each — a social move answered by speech beside a request the declared set
does not cover answered by `decline` — with the replies mined from SODA and
narrowed to the vocabulary of the runtime's own 97 hand-written pool lines.

## Arm 1 and arm 2 — the frame installs, and the residue is a carrier shape

    row                       ft4g     arm 1     arm 2
    social.bare_nocall        47.3%    86.6%     84.8%
    social.declared_nocall    34.8%    90.2%     88.4%    decline 47 -> 3 -> 9
    social.voice              50.9%    78.6%     76.8%
    social.farewell           55.0%    65.0%     65.0%    untrained transfer row
    social.heldout_carrier    66.7%    91.7%     83.3%    carriers trained nowhere
    chat.abstain_greet        83/100   93/100    93/100   a row neither arm aimed at
    grid A, pooled decline    206/208  205/208   207/208

The declaration's effect reversed sign (-12.5 to +3.6). Arm 1 lost three
novel decline turns of one shape — verb + pronoun object, no noun ("ping me
in twenty minutes") — which is structurally what a social move looks like and
which the balancing half had no example of; arm 2 supplied the shape and
closed two of the three, while "return the boots that didn't fit", never the
shape, still missed. The regression set was clean on both: every frozen copy
row at ceiling, `refusal.say` 270/270, `tool.selection` back at 198/200.

## The row that was thin, and the payload that taught the failure

`social.family` — does the reply answer the move made — was added after a
live conversation produced two replies every other row passed. On arm 2 it
read **48.2%**, and 40 of its 58 failures were "no family marker". Re-decoded
and read one by one: `ack` was a collapse (2/22), about nine of the forty
were answers the marker list could not see, and thirty-one answered nothing.
The payload told the same story — under the same markers, **402 of the 1,821
replies arm 2 trained on carry no family and 180 answer a different one** —
because the generator's tagger accepted a word where a family is a move, and
its exclusion clause could never fire.

The ruler was widened first, with the reply-side forms the reads produced,
and re-run greedy on all three checkpoints so the correction is a number:

    social.family     first cut      widened
    ft4g              33.0%          47.3%
    arm 1             43.8%          63.4%
    arm 2             48.2%          63.4%     ack 9/22, greeting 15/25

Then the generator: reply-side tags, a working exclusion, four scene rules,
six register words. The pool went 1,704 → 1,048 distinct at 0 of 97 pool
lines refused, and **98.8% of it sits inside the eval's markers** — which is
the caveat, stated before the arm ran: from arm 3 on, `social.family` is a
capability floor in exactly the sense `social.voice` already is.

## Arm 3 — on top of ft4g, and what the two variables bought

Owner's decision before the relaunch: the extraction work on disk is a set
of reader and verifier heads trained on `corn_jr_260m_v4_ft4g`'s cached
states, and ft4g is what `server.json` serves, so arm 3 initialises from ft4g
rather than the frozen base. Same recipe as arms 1 and 2, the revised
generator's file, best at iteration 1,000 (val 0.5874). Two variables against
arm 2, one against ft4g; the plan says which row is read against which.

    row                        ft4g     arm 2     arm 3
    social.bare_nocall        47.3%    84.8%     84.8%
    social.declared_nocall    34.8%    88.4%     85.7%
    social.voice              50.9%    76.8%     80.4%
    social.family             47.3%    63.4%     58.0%    ack 9/22 -> 5/22
    social.farewell           55.0%    65.0%     60.0%
    social.heldout_carrier    66.7%    83.3%     83.3%
    grid A, pooled decline  206/208   207/208   206/208   novel 32 / 31 / 30 of 32
    refusal.say             270/270   270/270   270/270
    extract.span / abstain   97/111    99/107    91/116

**The target fell by six items, and the species say why.** "No family marker"
went 23 → 19 and **"answers greeting" 3 → 14**: "cool" → "I'm doing alright,
thanks for asking. How are you?", "alright" → "Hey there. How are you doing
today?". The tightened greeting tag anchored the register on a hello and a
question back — 278 of arm 3's 443 greeting payload replies open with a
hello against 134 of arm 2's 466 — and a concentrated register generalises
to the wrong carriers. `ack` is the collapse before and after; its pool is 91
lines at five uses each, and the two lines drawn ten times are scene lines
the tag let through. So the payload's labelling was not what limited the
row, and `ack` is supply. `social.voice` +3.6 is the tighter pool doing the
one thing it was built for.

**The gates hold from a second-stage init.** Every frozen copy row at its
ceiling, `refusal.say` unmoved, `tool.selection` -1, `note_fidelity` -3, and
the extract pair -6 / +5 — inside finding 60's floor, and the one number the
extraction session should read before this trunk is served under heads
trained on ft4g's states. Grid A is ft4g's 206/208: trained decline improved
by two, novel lost two, one of them arm 1's "snooze that for ten" returning.

**The vague tail closed by a line, mostly.** On a 22-utterance battery from
a cleared history, arm 2 declines 5 and arm 3 declines 15; on the 16 unseen
surfaces, 5 → 11, and every longer tail ("when you get a chance", "at some
stage", "after a while") reaches `decline`. What still speaks is the
one-word tail — "later", "in a bit", "sometime" — on both held-out probes and
four others. The residue is a word wide rather than a shape.

**Verdict: arm 2 stays the keepable social checkpoint.** Arm 3 carries the
class on top of ft4g at nearly arm 2's level with every gate inside its
floor, but is below arm 2 on the target and on grid A and above it only on
`voice` and the vague tail. Kept from it on their own merits: the vague-tail
carriers, the generator's exclusion fix and scene rules. Not kept: the
greeting tag's hello anchoring. If the ft4g-based trunk is wanted, the next
arm is arm 2's file from the ft4g init — one variable, 25 minutes.

## Two things that are not the model

**The hatch was the wrong way round.** `check_hatches.py` recorded twelve
social phrasings that reached the router, held back on 2026-08-29 because a
wider hatch was then a wider frozen set. Since arm 2 he writes those replies
himself either way (`heldout_carrier` 10/12), so a hatch miss had come to
mean only that `social_rejection` never saw the sentence: speaking on more
turns grew the *unguarded* surface. The twelve are in the pools now (18 → 30
of 30), and stay out of the corpus by name so the row stays a generalisation
row.

**The supply number was two numbers.** The plan's "1.07 uses per distinct"
was draws over pool size; draws over replies actually used read 2.06 on arm
2 and 2.38 on arm 3, with `ack` near five on both. Finding 34's band was
measured on a whole slice, and the thin families sat outside it on an arm
that landed.

## Limits

One seed per arm, by the owner's decision. `social.voice` and, from arm 3,
`social.family` are floors rather than unbiased estimates, because the
filter that narrowed the payload resembles the ruler; the routing pair is
the clean read and the reads-by-eye are the unbiased half. n=12 on the
held-out carriers and n=24 on grid A's novel column, so single items move
those rows by four to eight points. The vague-tail battery is 22 hand-written
utterances against two checkpoints.
