# The shipped model answers most one-off messages coherently

**Full result:** Asked the 148 everyday messages of `probe_reply.py` one at a time, greedy, in the plain chat frame, the shipped 260M (`corn_jr_260m_v4_ft_social8`, server.json's checkpoint) answers 123 coherently by a blind hand read against the plain 5M's 70 (read beside it, blind; the 5M's labels came out at 70 for the fourth time) -- 11 of 12 on good news, 16 of 18 on bad, 17 of 18 small talk, 13 of 18 advice, 15 of 15 feelings, 12 of 12 plans -- and is weakest on the short and vague ("Hmm.", "Maybe.", "Never mind.": 11 of 20, below the 5M's 14). On the swap test it prefers the fitting reply in 99-100% of pairs (margins 20.6 within a category and 26.1 across, against the 5M's 8.3 and 11.5). The 5M's coherence problem, which findings 202-207 could not move by shape, decoding or a matching lesson, is mostly absent at the size and reading that ship

**Cost:** the reply read on the two checkpoints 14:39-14:41 on 2026-10-22 (90 s, contended), the swap test (seconds), the blind hand read of 296 replies ~10 min. ETA 10 min of card plus the read, actual ~2 plus ~10.

**The question** (owner, 2026-10-22: "for me I was referring to just a one
off -- you ask him something and his reply is coherent to it. Have we
achieved that?"). Every reply read today was on 5M research checkpoints;
the shipped model had never been read on these messages.

**The read** (`evals/results/reply_260m__*`, `replyswap__2runs_*`):

    read                                    plain 5M (s1)   shipped 260M
    blind hand read (of 148)                70              123
      good news / bad news                  7/12  7/18      11/12  16/18
      small talk / about him                10/18  5/12     17/18  9/12
      advice / feelings                     2/18  12/15     13/18  15/15
      plans / opinions                      7/12  2/10      12/12  8/10
      short and vague / odd                 14/20  4/13     11/20  11/13
    swap test, within: right / margin       0.91 / 8.27     0.99 / 20.63
    swap test, across: right / margin       0.96 / 11.48    1.00 / 26.10
    lm narrative / web / conversational     0.4864/0.9512/0.5579   0.2759/0.6315/0.2988
    knowing, matcher: admits unk / answerable  7 / 11        7 / 3
    distinct three-word openings (of 148)   88              96

**Caveats.** The plain frame (`<|user|>message\n<|say|>`), not the app's
full prompt with its date and tool declarations -- in the app some of these
messages are routed to tools or the runtime first; greedy, one reader, one
checkpoint (the shipped one; there is no second seed of it).

## Read by hand

The 260M answers news with the right mood and a follow-up that uses the
message: "Oh my gosh, congratulations! How are you feeling?" to a baby, "Oh
no, that's not good. What are your symptoms?" to a cold, "I'm sorry to hear
that. What was in it?" to a lost wallet, "Well, you could try setting a timer
for yourself" to procrastinating, "Well, it depends. What are your goals?" to
the job choice. Its failures are the 5M's habits, rarer: "That's great!
I'm sure you'll do great." to a raffle win, "I'm sorry, I didn't mean to" to
"Wait, what?", "You're not going to be able to do it." to "I don't know.",
a dispatcher's "we'll send someone over right away" to a spider in the bath,
and a stock opening ("I'm sorry to hear that", 9 times) where the 5M's was
"What? Why?". On the short and vague it most often misses: "It's about
5,000." to "Maybe.", "You're really good at it." to "Yeah, I guess."

## What it licenses

* **The owner's one-off target is mostly met by the model that ships**:
  about five replies in six answer the message. The 5M is not a picture of
  what he talks to; its coherence failures at 47% were a size-and-reading
  limit, and today's 5M arms were working well below where the shipped
  model already is.
* **What is left at 260M is narrow and nameable**: the short and vague
  message (11 of 20), a handful of stock lines, a misplaced role. Those are
  the items for the 1.0 corpus and for a reply read on every 1.0 candidate.
* **The 5M stays the cheap place to test mechanisms** -- but a mechanism's
  value for coherence is read at the size that ships, or on the swap and
  reply reads at 20M and up.

**What it does not settle.** The app's full prompt; multi-turn coherence
(finding 207's thread); any 1.0 checkpoint.
