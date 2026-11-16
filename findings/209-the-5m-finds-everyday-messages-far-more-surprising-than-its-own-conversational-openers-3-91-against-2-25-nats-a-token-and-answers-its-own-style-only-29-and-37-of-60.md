# The small model answers half of even its own style's openers

**Full result:** The 148 messages of the reply read are not his conversational style: at matched length (4-9 words) the plain 5M finds them 3.91 nats a token surprising against 2.25 for real conversational openers he never read and 2.39 for ones he did -- so he has not memorised his openers, and the hand-written messages sit far outside the SODA-style dialogue he learned conversation from. But the register is the smaller part of his incoherence: on 60 real openers in his own style that he never read, he answers coherently 29 and 37 times (0.48 and 0.62, blind; the real replies 60 of 60) against 0.47 and 0.37 on the everyday messages. 21 of the 148 messages appear verbatim as a turn in his reading (mostly "Hi.", "Thanks!", "How are you doing today?"); he passes them a little more often (0.67 and 0.43 against 0.44 and 0.36), as do short easy messages generally

**Cost:** the overlap search (CPU, ~1 min), `scripts/probe_message_style.py` (seconds of card), `scripts/probe_reply_instyle.py` (generation ~1 min, contended) and the blind read of 180 replies, 14:55-15:15 on 2026-10-22. ETA 15 min, actual ~20.

**The question** (owner, 2026-10-22: "are you asking things that would have
been in their training?"). Findings 202-206 read the 5M's coherence on
`probe_reply.py`'s hand-written everyday messages and found it near 47%
whatever was changed; finding 208 found the shipped 260M at 83% on the same.

## The reads

**Overlap.** Of the 148 messages, 38 occur somewhere in the decoded
conversational and chat reading, 21 as a whole turn -- the short and generic
ones. Blind pass rates on those 21 against the other 127: 5M seed 1 0.67
against 0.44, seed 2 0.43 against 0.36; the 260M 0.81 against 0.83.

**Style** (mean surprise after `<|user|>`, nats a token, plain 5M seed 1):

    set (4-9 words)                                  surprise   words
    probe_reply.py's messages (111)                  3.91       6.5
    chat-slice openers he read                       2.39       12.7
    conversational openers he never read             2.25       6.6

**In-style coherence** (`scripts/probe_reply_instyle.py`: the first lines of
60 dialogues past the bytes the mix reads, 4-20 words, seed 21; three replies
each, blind -- the 5M's two seeds and the dialogue's own reply):

    replier              coherent (of 60)   on probe_reply.py's messages (of 148)
    5M seed 1            29 (0.48)          70 (0.47)
    5M seed 2            37 (0.62)          55 (0.37)
    the real reply       60 (1.00)          --

The blind is imperfect on the real reply -- it is longer and more specific
than the model's and easy to pick out.

## Read by hand

In his own style he handles the greetings and set pieces cleanly ("Hey,
Pablo. What's up?" -> "Not much. Just hanging out."; a shop's "We have a
great selection of shoes! What type are you looking for?") and fails as on
everyday messages: "Oh, thank you so much! I really appreciate it." to a pay
cut, "Oh, wow! That's amazing! How did you do it?" to a twisted ankle, the
stock "I'm sorry, I didn't mean to hurt you" to "Why the hell did you do
that?". The SODA openers themselves (the unread sample) are what the owner's
messages are not: named greetings ("Hi Mirabel. How are you feeling
today?"), set roles (doctor, mother, shopkeeper), melodrama ("I'm scared of
tomorrow. I don't want to die.").

## What it licenses

* **The 5M's coherence ceiling is mostly the model, not the register**: in
  its own style it still answers about half. Findings 202-206's flat
  results stand on in-style ground too; finding 208's 83% at 260M is the
  size and reading.
* **The register gap is real and costs something on top** (a 5M is roughly
  10-15 points better in its own style; 60 items, noisy): the conversation
  he learns from does not contain the everyday, short, first-person
  messages the owner sends -- "Maybe.", "Long day.", "I spilled coffee on
  my keyboard" -- which is also where the 260M is weakest (finding 208:
  short and vague 11 of 20). That is a corpus item for 1.0: real
  conversational text in the owner's register, varied, not generated.

**What it does not settle.** One reader; 60 in-style items; whether real
everyday-register text moves the 5M, or only the larger models.
