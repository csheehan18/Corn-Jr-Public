# A reply judge beside the 5M moves his replies level

**Full result:** A judge block fitted beside the frozen plain 5M on swapped replies -- 853k parameters, 20,000 steps on 702,653 pairs of his own conversational reading -- recognises held-out conversation as well as he does or better (same-dialogue quads right at the end of the reply 0.913 and 0.912 against his own 0.904 and 0.881; on the first word 0.793 and 0.785 against 0.792 and 0.760), and re-ranking his top 20 words by it moves the blind hand read level: 55 and 51 of 148 replies answer the message against greedy's 53 and 46 on the same checkpoints (the gate was +7 at both seeds), the pre-registered row (b), as predicted. On the 148 hand-written everyday messages the judge is far weaker than he is -- swap pairs within a category right 0.73 and 0.75 at the end of the reply against his 0.91, 0.58 and 0.64 on the first word -- and its fit on the words that decide a reply ranges only 0.45-0.9, about 0.7 nats of push against LM gaps of one to two: where it is wrong it does no harm, and where it is right it is outvoted. The free control, sixteen samples re-ranked by his own whole-reply score, reads 54 and 56, also level

**Cost:** `corn/judge.py`, `scripts/train_judge.py`, `scripts/check_judge.py` (104 guards), `scripts/probe_reply_judge.py`, a settings check and the pre-registration 14:28-14:45 on 2026-10-24 (e69cf43); the chain 14:46-15:00, 13.97 min (judge fits 354 and 343 s, contended at 38%, a bound); the blind hand read of 888 replies ~10 min; the hand look at the judge's scores 2 min. ETA ~1.5 h, actual ~50 min.

**The question** (owner, 2026-10-24: "one is evaluating how well the predicted
token fits and another layer that pushes a successful token forward to
generate and show", inside the model). `docs/PLAN-REPLY-JUDGE.md` Phase 1:
findings 204-208 show the 5M recognises a fitting reply in 91-96% of swapped
pairs and writes one about half the time. A part whose only job is
recognition, voting on every word -- does it close that gap?

**What was built** (`corn/judge.py` argues each choice). One transformer
block reads the trunk's last states over the message and the reply so far
and scores every next token against its embedding; it trains on
`corn/contrast.py`'s pairs, each reply shown once after its own message
(*fits*) and once after another's (*does not*), at every reply position, so
a reply's general likelihood cannot predict the label. The picker adds
lam * log sigmoid(fit) to the LM's log-probability over its top 20 and takes
the argmax, lam 1 by Bayes' rule. The trunk never changes.

## The read

    read                                          seed 1            seed 2
    J1 held-out same-dialogue, judge | LM
      first word                                  0.793 | 0.792     0.785 | 0.760
      second / fifth word                         0.855 / 0.900     0.849 / 0.891
                                                  | 0.835 / 0.889   | 0.823 / 0.880
      end of reply                                0.913 | 0.904     0.912 | 0.881
    J1 held-out cross-dialogue, end               0.966 | 0.989     0.960 | 0.989
    J2 the 148 swap pairs, judge (first / third / end) | LM
      across categories                           0.74/0.86/0.88 | 0.96   0.73/0.84/0.87 | 0.95
      within a category                           0.58/0.73/0.73 | 0.91   0.64/0.68/0.75 | 0.91
    blind hand read (of 148)
      G greedy                                    53                46
      P judge + picker                            55                51
      F 16 samples, best by his own score         54                56
    passes under P only / G only                  7 / 5             10 / 5
    replies the picker changed (first word)       61 (36)           60 (43)
    distinct three-word openings G / P / F        86 / 91 / 97      82 / 85 / 105
    commonest opening G / P                       'what why' x7 / 'what do you' x7   'what why' x15 / x9
    loops                                         0 / 0 / 0         0 / 0 / 0
    judge training loss at 20,000                 0.409             0.418

(`evals/results/judge__*.json`, `reply_judge__*`: replies, F's candidates,
J2 margins, the blind file, its key and the hand labels.)

**The gate, as registered.** +2 and +5 against +7 at both: **(b), level**,
the predicted row. F is level too (+1, +10).

**The reader.** This read's greedy counts, 53 and 46, sit under the 70 and
58 earlier sessions gave the same greedy replies: a different reader,
stricter on a reply whose second sentence breaks the fit ("That's great!
I'm sure you'll do great." to a raffle win, "Yes, I am. I'm just about to go
to the movies."). The comparison within the read is paired and blind; the
absolute count is this reader's, not comparable with findings 202-213.

## Read by hand

**The replies.** The picker changes 60 of 148 replies at each seed and
mostly swaps one failure for another: "What? Why?" to a baby stays at seed 1;
"Oh, that's great!" to a spilled coffee becomes "Oh, wow! That's great! How
did you get it?". Its gains are the small talk and plans where any address
to the person beats a self-statement ("What kind of party?", "That's great!
What are you going to do?" to camping), and seed 2's odd messages (3 to 6).
No category moves by more than a seed's spread.

**The judge's scores**, read at the first and second words on six messages
the greedy replies fail (seed 1's judge, a scratchpad read; probe only -- not on disk):

    message                       candidate        p(LM)   fit
    spilled coffee on keyboard    That's great     0.66    0.72   (good 0.72, okay 0.76)
    someone scratched my car      That's great     0.30    0.51   (okay 0.72)
                                  Oh, no           0.16    0.47   -- wrong
    toaster caught fire           That's great     0.14    0.46   (so 0.81)
    dog ate a birthday cake       Oh, thank        0.20    0.86   -- wrong
    having a baby                 That's great     0.29    0.54   (so 0.83) -- wrong
    got the job                   That's great     0.68    0.85
    first word, any message       I / Y / It       --      0.08-0.39  (self-statements low)

What the judge reliably knows at the start of a reply is *whether it
addresses the other person*: openings that begin a self-statement ("I",
"It") score 0.08-0.39 on every message. Mood it reads weakly and sometimes
backwards on these messages -- "Oh, no" to a scratched car under "That's
great". And its scores are compressed: sigmoid 0.45-0.9 is at most ~0.7
nats of difference, so even where it is right ("That's great" 0.51 against
"okay" 0.72 for the scratched car) the LM's 0.30 against 0.08 wins.

## The cause

Two, both read above, neither a fault of the build (`check_judge.py` holds
the trunk, the symmetry and the top-K bound):

1. **The judge does not carry to the everyday messages.** It is trained on
   SODA turns, and on SODA it matches or beats his recognition; on the 148
   hand-written messages it falls well under him (within 0.73-0.75 against
   0.91). Finding 209 measured the gap it crosses: everyday messages are far
   more surprising to the 5M than SODA's openers (3.91 against 2.25 nats a
   token). His recognition on the 148 is the LM's whole conditional; the
   judge's is one block fitted to one source.
2. **One word is too early, and the push is too small.** The words that
   decide a reply come second or third ("That's *great*"), the judge's
   accuracy rises with every word read (J1), and its fit spans too little
   to overturn an LM gap of two to four times.

## What it licenses

* **A judge trained on swapped SODA turns, re-ranking one word at a time,
  is not the lever at 5M.** The recognition it learns is real on held-out
  conversation and does not reach the messages the owner sends.
* **The probe the cause names, before any heavier version:** fit the judge
  on pairs in the owner's register -- short-reply OpenAssistant and
  EmpatheticDialogues (findings 211-213 found them closest) -- and read J2
  first, seconds of card: if within-category J2 does not pass his own
  0.91, the picker has nothing to add and nothing more is run. Only if it
  does, the look-ahead picker (the owner's suggestion, 2026-10-24: try a few
  openings a few words deep, keep what the judge likes) addresses cause 2.
  A larger lam alone would amplify a judge that is wrong on mood.
* **Phase 2 is not opened** (its condition was (a)). At 260M his own
  recognition is 99-100% (finding 208), so a judge there has a much higher
  bar to pass, not a lower one.

**What it does not settle.** Any judge trained off SODA; more than one
block; the look-ahead picker; lam other than 1; any size above 5M; Phase 3.
