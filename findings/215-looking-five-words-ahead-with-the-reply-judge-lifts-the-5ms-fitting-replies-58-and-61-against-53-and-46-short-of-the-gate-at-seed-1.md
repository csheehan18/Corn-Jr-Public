# Looking a few words ahead with the judge lifts his replies

**Full result:** Choosing each reply's opening by a beam five branches wide and five tokens deep, scored by his own mean log-probability plus the reply judge's verdict on the newest word, lifts the plain 5M's fitting replies to 58 and 61 of 148 against greedy's 53 and 46 by a blind hand read -- +5 and +15, short of the pre-registered +7 at both seeds at seed 1, so the registered row is (b), level -- and every paired count points one way: 38 replies pass only under the look-ahead and 18 only under greedy (sign test p = 0.010), and against the same beam with no judge 32 to 17 (p = 0.044), so the gain is the judge's and not the search's (the beam alone: 53 and 51, 27 to 22). A judge continued on short-reply OpenAssistant and EmpatheticDialogues reads the everyday messages better (within-category swap pairs right 0.78 and 0.81 at the end of the reply against the SODA judge's 0.73 and 0.75, under his own 0.91, the predicted fail) and steers worse: 51 and 51 with the look-ahead, 51 and 50 one word at a time. It learned EmpatheticDialogues' habit of answering with one's own feelings

**Cost:** `train_judge.py --pairs/--init`, the look-ahead in `corn/judge.py` and its guard (`check_judge.py` 6), the probe's decoders, a settings check and the pre-registration 15:06-15:28 on 2026-10-24 (0a1c2c1); the chain 15:29-15:33, 4.3 min (two register fits 62 s each, contended at 45%, a bound); the blind hand read of 1,480 replies ~15 min. ETA ~1.5 h, actual ~50 min.

**The question** (owner, 2026-10-24: "Do the probe and also let's do the
look ahead idea as well"). Finding 214 named two causes for a level judge:
it was fitted on SODA turns and reads the owner's everyday messages weakly,
and one word is too early -- the word that decides a reply ("That's
*great*") comes second or third, and the judge reads better the more it
has seen. One arm each (`docs/PLAN-REPLY-JUDGE.md` Phase 1b).

## The read

    row                                            seed 1     seed 2     pooled discordant (arm only : other only)
    R  J2 within, end of reply: SODA judge         0.73       0.75
                                register judge     0.78       0.81       his own: 0.91 / 0.91 -- fails
       J2 across, end: SODA / register             0.88 / 0.91  0.87 / 0.92   his own 0.96 / 0.95
    blind hand read (of 148)
       greedy                                      53         46
       look-ahead, no judge (look0)                53         51         27 : 22 against greedy, p 0.57
       look-ahead, SODA judge (look)               58         61         38 : 18 against greedy, p 0.010
                                                                         32 : 17 against look0,  p 0.044
       look-ahead, register judge                  51         51         31 : 28 against greedy
       one word at a time, register judge          51         50         15 : 13 against greedy
    replies the look-ahead changed                 96         88
    distinct three-word openings, greedy / look    86 / 80    82 / 73
    commonest opening under look                   'i don't know' x13   x15  (greedy: 'what why' x7, x15)

(`evals/results/judge__*_reg.json`, `reply_look__*`: replies, J2, the blind
file, its key and the hand labels. Greedy's 296 labels agree with finding
214's blind read of the identical replies on all 296.)

**The gates, as registered.** R: fails at both, as predicted. L: the SODA
judge's look-ahead +5 / +15 -- not +7 at both: **(b)**, the predicted row,
with the largest paired gain of any 5M decode arm read. The register
judge's look-ahead and its one-word picker: (b). P': (b).

## Read by hand

**What the look-ahead fixes** (seed 2's 22, seed 1's 16): the stock
"What? Why?" and wrong-role openings give way to replies built from the
message -- "Why do you want to repaint the bedroom?", "What kind of
garden are you looking for?", "Where did you find twenty dollars?", "What
made you decide to start?" to a pottery class, "Why not?" to "Maybe." --
and the mood turns where greedy had it backwards: "Oh my gosh, that's so
sad. I'm sorry to hear that. What happened?" to a numb face (greedy: "Oh,
that's great! I'm so glad you're here"), "I'm sorry to hear that. What
happened?" to a missed bus (greedy: "That's great, honey!"), "Yeah, it was
pretty bad" to the traffic. Five words is far enough to see "great" coming
after "That's" and to drop it.

**What it breaks** (18): a bad-news message it reads as good ("Oh, wow!
That's awesome! What's wrong with it?" to a cracked screen, "Oh, wow!
That's great! How did you get it?" to a cancelled flight -- the judge's
weak mood read, finding 214), and the beam's own pull toward the generic:
"I don't know. I just feel like I'm not doing anything right" rises to the
commonest opening, and variety falls (86 to 80, 82 to 73 distinct
openings). The beam with no judge shows that pull alone and nothing else
(53 and 51).

**Why the register judge steers worse.** Where the SODA judge's look-ahead
passes and the register judge's fails (15 at seed 2), the register judge
chose "I don't know. I just feel like I'm not good enough" (three times),
"I'm sorry, I didn't mean to hurt you", "Oh no, my grandma is in the
hospital" -- the listener speaking about themself. EmpatheticDialogues'
replies often share the replier's own feeling, so a judge fitted on them
learns that a first-person disclosure fits; it recognises the hand-written
swaps better and prefers the wrong kind of reply when it steers. Its
better J2 is pair recognition; steering asks it to rank the model's own
candidates, which J2 does not read.

## The cause of the seed-1 miss

The 18 losses are the two above: the judge's mood read on bad news
(finding 214's cause 1, unfixed by the register data) and the beam's pull
to the generic opening. Neither is a fault of the build (`check_judge.py` 6
holds the beam against an exhaustive by-hand best and the mean against the
sum).

## What it licenses

* **The owner's look-ahead is the first decoding change that moves the
  5M's fitting replies in one direction at both seeds** -- by a margin a
  paired sign test puts at p = 0.010, under a pre-registered per-seed gate
  it missed at one seed by 2. Search alone does nothing; the judge one word
  at a time does nothing; together they help. It is a direction at two
  seeds, not a capability.
* **The register judge is dropped**: better at pairs, worse at steering,
  and not under a licence the weights can carry.
* **The probe the miss names**: the same look-ahead, settings unchanged,
  on the 20M pair (`nano20m_v3_webblend`, `_seed2`), the next size with
  two seeds, against the same gate -- and then the shipped 260M (Phase 2),
  where greedy's misses are stock lines and his own recognition is 99%.
  A judge trained to read mood on bad news (cross pairs whose messages
  differ in mood and match in topic) is the fix for the losses, after the
  replication.

**What it does not settle.** Other beam widths, depths or lam; the beam
with sampling for variety; any size above 5M; the app's full prompt.
