# Two decisions: whole-passage reader by default, life questions declined

**Full result:** Decisions 7 and 8 are taken: the whole-passage reader is the default, and a routed question about his life is answered at the runtime by a decline that says he is a model, which catches all sixteen held-out phrasings and none of twenty requests

**2026-09-05, evening, the owner's two decisions after finding 124, both
runtime-only and both guarded. No card. Nothing trained. The eval rows are
unchanged in what they measure.**

## 1. Decision 7 -- `reader` defaults to `head_whole`

`harness/serverconfig.py` `reader: str = "head_whole"`. The pair it serves
is finding 124's: `reader_whole_social8_s1.pt` on the social8 trunk at
`WHOLE_THRESHOLD` -1.280, keyed by hash. The number the decision was taken
on, Population A through the real `read_passage`:

    reader                       right  wrong  silent | u.silent  wrong   precision   ms/passage
    generate (the gate, 117 a)    230     99     392  |   256      26      64.8%       --
    head_whole (this pair, 124)   517    147      57  |   197      85      70.6%      23.5

More than twice the right answers at higher precision, spending 59 correct
silences of 282. `--reader generate` and `--reader head` stay as arms, so
the comparison remains paired; `check_extract.py` now asserts the default is
`head_whole` and that every head has its flag. What a user sees change: a
question a pack or a search can answer is answered from the passage read
whole, in one forward.

## 2. Decision 8 -- the routed question about his life

**The gap.** `ABOUT_HIS_LIFE` is a whole-utterance set and the hatch answers
its 31 members from `NO_LIFE_REPLIES`; the sixteen held-out phrasings in
`evals/social_self.jsonl` ("so how old are you anyway", "any pets", "where
are you based") reached the router by design so `social.self_heldout` could
read the weights. Finding 122 §4 read what the weights do there on the arm 7
trunk: they speak on twice as many and half of what they say is SODA's life
("I'm 23", "I work ..."). The plan's decision 8 named three repairs; the
owner took the router-side rule, with the reply he specified -- a decline
that says he is a model with no concept of the thing asked.

**The rule**, `corn.agent.life_question`, tried inside `identity_reply` after
the whole-utterance sets and the two-clause split have missed. Three
conditions, all required:

    addressed to him     you / your / yourself, or a bare possession
                         question ("any pets", "got any kids", "how's the family")
    a life topic         age, work, home, family, pets, habits, a body --
                         a closed list, and nothing wider
    no request           no tool-register verb, no "can/could/would you",
                         no "my" (a question about the user's things routes)

**The reply**, `NO_LIFE_ROUTED_REPLIES`, six hand-written lines held to the
self pool's bars (finished sentence, no digit, passes `social_rejection`,
name only through `Persona.pool`), each saying he is a model and handing the
turn back: "That one's not a thing for me. I'm a model, not a person." /
"I got trained, not born, so that's out. What can I do for you?" Identity
answers are never rephrased by the weights (`_own_words` runs on the social
path only), so the line is served as written.

**The reads, all on the CPU:**

    the 16 held-out phrasings of social_self.jsonl      16 of 16 caught
    20 must-route turns ("can you call mom", "do you know the capital of
      france", "what's my dog's name", "how are you", "what day is it",
      "note that i'm tired", "can you sleep", "how long does a dog live")  0 of 20 caught
    check_hatches' self battery                          13 -> 15 of 16
      the one miss is "I love you buddy", which is no question
    check_toolgrid: no grid A/B/C request reaches any hatch   unchanged, green
    check_confirm: no orphan yes/no answer is caught          unchanged, green

**What it does and does not change.** At the runtime, a question about his
life in any of these shapes is answered by the pool and never reaches the
weights; the exposure finding 122 measured (four of sixteen held-out
phrasings given a life) is closed at the boundary the rule draws. The eval
rows `social.self` and `social.self_heldout` still send `prompt_route` to
the model directly and still read the weights -- the ruler is unchanged,
and the residue it measures (finding 122 §4) is still in the weights,
unrepaired, which is what §3 rule 1 says it must be. `check_evals.py` group
32 now asserts every held-out phrasing takes the identity hatch's rule and
none the social or temporal hatch.

## 3. Held

The owner held two things: a second seed of the re-fit (finding 124's open
question) and §7's speech-temperature sweep (decision 5). Both are on the
plan's current-order block as item 14.

## Limits

The rule is lexical and the topic list is closed; a phrasing about his life
that names no listed topic ("what's your story", "tell me about yourself")
routes as before, and "I love you buddy" is not a question the rule can
see. The twenty must-route turns are a hand-written battery, not a
population. Nothing here is a live session.
