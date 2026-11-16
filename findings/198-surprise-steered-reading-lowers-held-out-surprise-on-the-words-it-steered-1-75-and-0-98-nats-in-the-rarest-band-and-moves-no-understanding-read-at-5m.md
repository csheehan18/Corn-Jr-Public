# Surprise-steered reading lowers rare-word surprise but not understanding at 5M

**Full result:** At 5M, replacing up to 7 of each step's 48 rows -- only web rows, 14.6% of all reading -- with fresh, varied web text carrying the words whose surprise is falling lowers his surprise on rare words in sentences he never read (the held-out rare-word gap 7.65 and 7.80 nats against the base's 7.90 and 8.06, most in the rarest band: a drop of 0.54 at 10-30 sightings, 0.16 at 30-100, 0.07 at 100-300), and the drop is the steered words': held-out targets the scheduler happened to steer fall 1.75 and 0.98 nats at 10-30 against 0.25 and 0.18 for the rest; fluency holds on every text row and in the hand read; no understanding read moves (fields 0.55 / 0.53, wishes 0.32 / 0.33, plain lift 0.47 / 0.48 against 0.56 / 0.53, 0.35 / 0.32, 0.49 / 0.47) -- pre-registered outcome (b), the mechanism works and 5M is too small to turn it into understanding

**Cost:** building the instrument, the scheduler and its guard 22:40-23:20 on 2026-10-21 beside the base runs (CPU), a 400-iteration smoke run 0.9 min; both runs with card and reads in one chain, 23:20-23:44, 23.6 min (training 441.6 and 443.4 s against the base's 350 and 354, the scheduler's CPU costing 26%); the steering read and the hand reads ~10 min; all contended (the card at 37-40%, a bound). ETA 25 min, actual 23.6.

**The question** (owner, 2026-10-21; pre-registered at 99dfa8a,
`configs/nano5m_v3_webblend_surprise.py`). He learns everyday words too
slowly because a rare word is met a handful of times, scattered across a pass
(findings 185-196). Track his own surprise on each word during training;
steer a capped share of his reading to fresh documents carrying the words
whose surprise is falling -- learning progress, not raw surprise, which fires
on every name and typo (finding 188) -- with growing gaps, and with each
next context chosen to be unlike the ones he has already been shown (the
owner's addendum). Fluency is a hard constraint.

**The build.** `corn/surprise.py` (off by default): a steered row only
replaces a web row, after the draw, so every other source keeps its exposure
and the rest of each batch is the base run's to the byte. Candidates are
28,555 lowercase words seen 10-1,000 times in the web share; 6,429 names
(capitalised mid-sentence) and 4,120 typos (a spelling one edit away seen
20 times as often) are out. Each word keeps an exposure log -- documents the
base stream showed it in, documents the scheduler showed it in, sources, a
sketch of the content words around it -- and the next context is the drawn
fresh one whose neighbouring words are most novel against the sketch; a
context too like one already steered is passed over, and a replay happens
only when nothing varied is left. `scripts/check_surprise_sched.py` holds
the cap, the per-document replay cap, the exclusions, the spacing and the
variety off each run's log (both pass), with a mutant per property.

## The read

    run                  fields   wishes 192   plain lift   lm narr / conv / web     chats   rare-word gap   10-30   30-100   100-300   common
    base   s1            0.56     0.35         0.49         0.4864 / 0.5579 / 0.9512   8      7.90            17.94   14.32    11.41     6.66
           s2            0.53     0.32         0.47         0.4883 / 0.5599 / 0.9522   6      8.06            18.16   14.46    11.28     6.57
    steer  s1            0.55     0.32         0.47         0.4873 / 0.5584 / 0.9536   7      7.65            17.40   14.18    11.22     6.62
           s2            0.53     0.33         0.48         0.4857 / 0.5566 / 0.9480   5      7.80            17.63   14.31    11.35     6.63

(the four band columns are summed nats on the held-out word, `scripts/probe_word_surprise.py`;
the gap is the 300 targets less the 60 common words)

**The gates, as registered.** Understanding: no -- every surprise seed sits
at or under the base pair's higher seed on all three reads. Word surprise:
yes -- 7.65 and 7.80 both under the base's lower 7.90, most in the rarer
bands (0.54 > 0.07). Fluency: holds -- every text row is under its fall line
(0.4913, 0.5629, 0.9552), and the chats pass 7 and 5 of 10 against 8 and 6
(a fall needed 3 fewer). Unreadable: no -- the guard passes on both logs and
each run steered 36,596 and 36,636 rows of a 36,659-row budget. The table
reads **(b)**.

**The drop is word-specific.** The 300 held-out targets were chosen before
the run and never handed to the scheduler, which steered 117 and 116 of them
on its own rule:

    held-out targets               seed 1               seed 2
                                   steered    rest      steered    rest
    10-30 sightings                +1.75      +0.25     +0.98      +0.18     (drop in nats, base pair mean less the run)
    30-100                         +0.41      +0.04     +0.44      -0.17
    100-300                        +0.04      +0.19     +0.12      -0.10

A word he was steered toward three or four extra times reads a nat or two
less surprising in new sentences; the words he was not steered toward barely
move. *euphemism*, seen 21 times, shown six varied contexts ("'tear gas'
strikes me as a euphemism", "Nazi euphemism for the deliberate killings")
reads 21.2 and 23.1 nats against the base's 26.4; *celebs* 14.7 and 15.4
against 19.0. A word steered in the last 40 steps (*affricates*, at step
5,204) has not moved.

## What it steered toward, read by hand

`scripts/probe_surprise_steered.py`. **Mostly words, not junk.** A random
80 of seed 1's 10,590 steered words hold two fragments (*spp*, *anglaise*);
the words steered most (eight rows each) are everyday -- *afraid*, *angry*,
*anxious*, *apples*, *backyard*, *balloon*, *basket*, *allergic*. Over the
run the mix moves rarer: the first 1,000 steps are 41% words seen 300-1,000
times (*wise*, *gather*, *grab*, *mistake*, *afraid*, *tired*, *tomorrow*),
after that 10-30-sighting words are a quarter and the top of each window is
rarer and more technical (*triremes*, *inguinal*, *intubation*,
*cartography*). **The junk is a thin tail late in the run**: code and
fragments (*endif*, *printfn*, *ixzz*, *cker*) whose surprise falls because
they recur verbatim, and they lead the replay list (all their rows
replayed -- they live in a document or two).

**Exposure, by band** (seed 1; seed 2 within 4% on every column):

    band       steered words   steered rows a word   distinct contexts   variety   replays   base stream: sightings (scaled to the base run) / documents
    10-30      2,908           2.76                  2.69                0.90      7.6%      12.5 (17.8) / 7.0
    30-100     3,527           3.39                  3.39                0.97      0.5%      37.3 (52.9) / 21.9
    100-300    2,457           4.09                  4.09                0.97      0.0%      115.6 (163.8) / 66.3
    300-1000   1,698           3.87                  3.87                0.95      0.0%      368.0 (521.6) / 203.3

For a 10-30 word the steering added about three new, varied contexts to the
seven documents the base stream showed it in -- a sixth more sightings --
and that moved its held-out surprise by one to two nats. The dose is thin
and spread over ten thousand words: doubling gaps (25, 50, 100, 200 steps)
and the "understood" stop end most words at three or four rows.

## Costs, read beside the table

One of 96 behaviour rows sits below the base pair by more than 5% of its n
at both seeds: `tool.name_fidelity` 33 and 30 of 120 against 40 and 41,
its failures split between `wrong_tool` and `wrong_name` as unevenly as the
base pair's own (64/11 and 14/52) -- a row near its floor, a direction, not
read by hand. The stock-answer pull splits by seed (0.33 and 0.24 against
0.28 and 0.27). Training costs 26% more wall clock (the scheduler's CPU).

## What it licenses

* **The mechanism works as built, at both seeds**: surprise-steered reading
  teaches him the words it steers, in sentences he never saw, at no cost to
  fluency, and the effect is largest on the rarest words.
* **At 5M it does not reach understanding**, as predicted: the rulers read
  the description-to-meaning hop, and three extra contexts for ten thousand
  scattered words do not move it here -- finding 197 says this size reads
  those rulers at the 20M's level already.
* **Next, by the table: the same arm at 20M**, at the same cap -- with the
  random-replay control named in the pre-registration (the same rows
  replaced by random web documents under the same caps), since a word-level
  drop could partly be any re-reading of rare-word-dense text; the
  steered-against-rest split above says most of it is not.
* **Two knobs the read points at, before or with the 20M**: a longer dose
  per word (the doubling gaps stop most words at three or four rows), and
  a filter for verbatim-recurring fragments (code tokens) in the late tail.

**What it does not settle.** Whether the word-level drop is meaning or
form (lower surprise on a word in a new sentence is necessary for knowing
it, not proof); any size above 5M; the random-replay control; the cap at
any value but 15%; the chats read by one reader.
