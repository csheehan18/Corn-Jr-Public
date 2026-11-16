# Judging his own drafts does not help; plain beam search might

**Full result:** On the shipped 260M (`corn_jr_260m_v4_ft_social8`), in the plain chat frame, three decoders over finding 208's 148 one-off messages and exam 2's 100 by one blind hand read: greedy answers 122 and 72 (208 read 123 on the 148 by the same rule), the look-ahead judged by his own recognition -- the posterior that a draft was written for this message among it and 16 others, `corn/judge.py` section 9 -- answers 127 and 70, and the same beam with no judge answers 126 and 79. Every pre-registered row misses: L (self over greedy by 7 and 5) at +5 and -2; Lp (paired) at 22 : 19, p 0.76; J (self over the plain beam by 5) reversed, 197 against 205, 15 : 23. The posterior measures whether a reply *identifies* its message, and among his own drafts the replies that identify a message best include the ones that do not fit it -- "I didn't steal your bike. You're just paranoid." to a stolen bike, a tool hatch's "I can't make bookings" to a day off. The plain beam over the opening, predicted 0-4 *below* greedy, reads 205 against 194, 19 : 8 (p 0.052) -- not a registered row, so a candidate, not a result

**Cost:** the decoder, its guard and the pre-registration 22:46-22:55 on 2026-11-01 (99540a4); batched decoding and its guard 23:01-23:07 (9f32bc9); the read 23:07-23:09, 100.5 s of card for 744 replies (contended at 31%, a bound); the blind hand read 23:09-23:11. ETA ~1 min of card and ~45 min of reading; the reading took a fraction of that.

**The question** (owner, 2026-11-01, on the proposal: "Yes, pre-register
it"). Finding 208: the shipped 260M prefers the fitting reply over a
swapped one in 99-100% of pairs and still writes 25 of 148 that do not fit.
At 5M a judge choosing among drafts closed part of that gap (findings
215-216), but the judge had to be trained because the 5M's recognition was
weak. At 260M the swap test's own form needs no training: score each draft
by the posterior that it was written for this message rather than for any
of 16 practice messages, and let the beam keep the drafts that score best.
The pre-registration is `scripts/probe_self_judge.py`'s docstring.

## The read

    read (blind, one reader)            the 148   exam 2 (100)   all 248
    greedy                              122       72             194
    look0 (beam 5 x 5, no judge)        126       79             205
    self (beam + his own posterior)     127       70             197

    paired                              arm only : other only
      self vs greedy                    22 : 19   p 0.76
      self vs look0                     15 : 23   p 0.26
      look0 vs greedy                   19 : 8    p 0.052

    the 148 by kind (greedy / look0 / self)
      good news (12)   11 / 11 / 10      feelings (15)  14 / 14 / 14
      bad news (18)    16 / 17 / 16      plans (12)     11 / 11 / 11
      small talk (18)  17 / 18 / 18      opinions (10)   8 /  8 / 10
      about him (12)   10 / 10 / 11      short (20)     13 / 15 / 13
      advice (18)      11 / 12 / 12      odd (13)       11 / 10 / 12

    distinct three-word openings        96 / 89 / 109 of 148,  76 / 70 / 82 of 100
    "I'm sorry to ..." openings         9 / 13 / 7,            7 / 9 / 6
    echo (four words of the message)    4 / 4 / 11,            2 / 3 / 6
    loops (by the probe's count)        0 / 0 / 1,             0 / 0 / 0

(`evals/results/self_judge_260m__*`: the replies, the posteriors, the blind
file, its key, the hand labels.)

**The rows, as registered.** L: +5 on the 148 (gate 7), -2 on exam 2 (gate
5) -- **misses**. Lp: 22 : 19 -- **misses**. J: self 8 *below* look0 --
**misses, reversed**. Unreadable: not triggered (no flat posteriors, one
loop, no empty reply). The prediction revised after the settings check had
L and Lp missing (right), J holding because the plain beam would fall below
greedy (wrong: it rose above), and echo level (wrong: 6-7 to 17).

## Read by hand

**What his own judgment fixes.** The "I don't know" deflection on a direct
question, every time it moves: "I love sushi!" where the beam wrote "I
don't know, what is it?", "The best way to cheer up a friend who's had a
bad day is to make them laugh.", "Mornings, I guess.", "I love making people
laugh." A reply that could follow any message identifies none, so the
posterior pushes it out -- the mechanism working as designed, and why the
opinions cell reads 10 of 10.

**What it breaks.** The same pressure, with nothing to stop it at the
other end. A reply that would be unlikely after any other message
identifies this one -- whether or not it fits:

    Someone stole my bike from outside the shop.
        I didn't steal your bike. You're just paranoid.
    It's my day off today.
        I wish I could, but I can't make bookings.
    Hmm.
        I couldn't find anything useful for what's 22 percent of 1924.
    What's your favourite holiday?
        My favourite holiday is the 2nd of June.
    Should I tell my friend her cooking isn't great?
        Yes, Should I tell my friend?
    My cat sat on my keyboard and sent an email.
        Okay, we'll send someone over to check it out.

Accusation, role slips, the runtime's refusal and lookup-miss lines that
the fine-tune taught him, and restating the message (echo nearly triples)
all identify a message well. The short and vague are worst hit: "Hmm.",
"Maybe.", "Yeah." are fitted by almost any reply, so the drafts that win
are the strangest. The swap test compares two *real* replies; a decoder
asks the same question over his own candidates, which include replies no
swap pair ever contained -- recognition among good replies is not a
ranking of his drafts.

**What the plain beam fixes** (not registered). Greedy commits to its first
word and then follows it somewhere wrong; the beam keeps the opening whose
words are most likely on average, and on this model that is more often the
plain one: "Really? I had no idea." for greedy's "I love the way you've
used different colors", "Come on, it'll be fun!" for "You're not going to be
able to do it.", "What? Why?" for "Oh, right." to a cancelled wedding,
"Sure! What do you need to know?" for "You'll need to get a good education".
At 5M the same beam added nothing (finding 215); at 260M the candidates are
good enough that the likeliest opening is usually a fitting one -- finding
219's lesson about the look-ahead, again. It costs: 13 and 9 "I'm sorry
to..." openings against greedy's 9 and 7, and "I'm sorry to hear that" on
lemons.

## What it licenses

* **The self-judge does not ship and does not need a fix to be read
  again**: as built it is level with greedy and below the plain beam. Two
  cheap variants are named, neither run: the posterior as a veto only --
  it may demote a draft that identifies nothing, never promote a strange
  one (`min(0, posterior - log 1/2)` in place of the posterior) -- and a
  bank of hard negatives (the other messages of the same kind, finding
  208's within-category swap) so that "I'm sorry to hear that" is the
  generic answer it should be and a bizarre reply is not the only way to
  stand out.
* **The plain beam over the opening is the finding to replicate.** 19 : 8
  at p 0.052 on 248 messages, unregistered: a fresh, pre-registered read
  (the practice set, or a new exam) before anyone wires it. It needs no
  training and no judge; `corn/decode.py`'s static cache would have to hold
  five rows for five tokens.
* **The batched decoders** (`corn/judge.py` section 10, guarded equal to
  the one-message decoders) put a 744-reply read at under two minutes of
  card; the hand read is now the whole cost of a reply probe.

**What it does not settle.** The app's full prompt (date, tools, routing --
several losses above are the fine-tune's runtime lines surfacing in a frame
that never routes); multi-turn conversation; a second reader (one reader,
the session that built the decoder, blind to the key; greedy's 122 against
208's 123 is the consistency check); any checkpoint but the one that ships.
