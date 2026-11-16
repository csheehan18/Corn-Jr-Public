# He writes worst exactly where he reads worst, message by message

**Full result:** Over finding 208's 148 one-off messages, a message's mean swap margin on the shipped 260M -- how strongly he prefers a hand-written fitting reply over a swapped one -- predicts whether his own greedy reply to that message was hand-labelled coherent at AUC 0.713, and at 0.713 counting only pairs inside one of the ten message categories. Message length predicts the label at 0.54 and taking it out of the margin leaves 0.713. Pre-registered row R: linked (0.65 or more). On the plain 5M the same read is 0.544 (0.586 within category): near chance. The share of pairs he gets right predicts nothing at either size (0.544, 0.516) -- the 260M gets nearly every pair right, so only the margin's size carries the signal.

**Cost:** pre-registered and committed at 21b9000 before either read was computed; started 15:11:55 on 2026-11-15, read 1 on CPU in under 2 s, hand read and length check under 1 min; written 15:15-15:20. No card.

**The question** (owner, 2026-11-15: "Run both probes", after a brainstorm
on how a model can understand words while still generating text). Findings
204 and 208 measured that he recognises the fitting reply far more often
than he writes one -- 99-100% of swap pairs against 123 of 148 written at
260M. Is that one weak signal read two ways, or two competences that fail in
different places? It had never been read message by message. The
pre-registration is `scripts/probe_read_write.py`'s docstring, read 1.

## The read

A message's **read score** is the mean margin (finding 204's swap score, a
reply's general likelihood cancelled) over every pair it sits in, either
side, across and within category pooled: 7 to 18 pairs a message. Its
**write label** is finding 208's blind hand label of that run's own greedy
reply. The parse reproduces 208's totals (123 and 70) by assertion.

    run                     writes    R  AUC    Rc  within category   share-right AUC
    corn_jr_260m (shipped)  123/148   0.713     0.713                 0.544
    nano5m_v3_webblend       70/148   0.544     0.586                 0.516

Not registered, read after: message length (words) predicts the 260M's
label at 0.540 and correlates 0.25 with the read score; the read score with
length regressed out still reads 0.713. **Prediction was wrong**: it said
0.58-0.68, linked more by category than by item; it is linked by item.

## The hand read

The eight messages he reads worst, with the fitting reply he was shown and
the one he wrote:

    138  "There's a spider in my bath and I'm not going in there."   F
         shown: I'd leave it for a while too.
         wrote: Okay, we'll send someone over right away. Can you tell me where you are?
    118  "Maybe."             F   wrote: It's about 5,000.
    61   "Any ideas for a cheap date night?"   F   wrote: I don't know, what did you have in mind?
    147  "My neighbour gave me a huge bag of lemons."   P   wrote: That's great! How many did you get?
    120  "Never mind."        F   wrote: I don't mind.
    116  "Hmm."               F   wrote: That's interesting.
    137  "I accidentally called my teacher mum."   P   wrote: I'm sorry to hear that. What happened?
    127  "Wait, what?"        F   wrote: I'm sorry, I didn't mean to. I was just trying to get your attention.

Six of eight fail. What they share is that the meaning is not in the words:
a spider in the bath is a joke-sized complaint and not an emergency,
"Never mind" withdraws a request, "Wait, what?" asks for a repeat. Where
the message's words carry its meaning he reads it well and writes well;
where the meaning is in what the words imply, both fail together.

## What it licenses

**Reading and writing are one competence in the 260M, not two.** The
messages his recognition finds hard are the ones he writes badly on, beyond
what the kind of message or its length explains. So the recognise-ahead-of-
write gap of findings 204 and 208 is mostly the same weak signal read two
ways -- recognition with the prior subtracted and the whole reply in view,
writing committed at the first word -- and a fix that strengthens
understanding of a message should move both. At 5M the link is near
chance, which fits finding 214's weak recognition there: little signal to
share. One checkpoint per size, one hand labeller, 148 messages; the 5M's
second seed and exam 2 on the 260M have no swap read and are not in it.
