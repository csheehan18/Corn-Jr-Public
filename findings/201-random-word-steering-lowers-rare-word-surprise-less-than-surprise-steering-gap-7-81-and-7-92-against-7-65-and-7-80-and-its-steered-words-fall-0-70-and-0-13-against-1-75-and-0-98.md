# Words picked at random gain less than words the scheduler picked

**Full result:** With the scheduler's words drawn at random -- as many of each frequency band as the surprise arm steered, under the same cap, spacing and variety -- the held-out rare-word gap reads 7.814 and 7.923 against the surprise arm's 7.650 and 7.802 and the base's 7.896 and 8.064: the pre-registered *between* row (m), random choice helps less and not separably at the gate. The steered-target split separates them: rare targets (10-30 sightings) chosen at random fall 0.70 and 0.13 nats in their own held-out sentences against 1.75 and 0.98 for those the surprise scheduler chose, though the random ones got more rows each (4.2 against 2.7-3.2). The progress score is noise (finding 200), so the difference lies in what comes with it: the surprise scheduler steers a word only once he has met it three times and still finds it harder than average (z +1.2 at the first steer, random picks +0.1), which lands its rare-word steering mid-run (median first steer at step 2,600-3,100 against 900-1,100). Fluency, chats and the understanding reads hold at both seeds

**Cost:** the random mode, guard property 6 and its three mutants, the configs and the pre-registration 08:30-08:45 on 2026-10-22 (12fd610); both runs with card and reads 08:55-09:17 inside the 29.0-min chain beside the frozen run (contended, the card at 34%, a bound); the split, dose and timing read and the hand reads ~10 min. ETA 24 min of card for the arm, actual ~22.

**The question** (the review of finding 198, 2026-10-22). Finding 198's
steered words fell and the rest did not -- which any extra sightings would
do. The control keeps every part of the scheduler except the choice of
words: `corn/surprise.py` section 9 draws a fixed random set at the start
(seed 1: 2,908 / 3,527 / 2,457 / 1,698 words at 10-29 / 30-99 / 100-299 /
300-1,000 sightings, matched to what surprise seed 1 steered; seed 2 matched
to seed 2) and walks its due words in a fresh random order every step;
nothing read off his loss enters the choice. Pre-registered at 12fd610 in
`configs/nano5m_v3_webblend_surprise_random.py`, predicted (e) -- "the
extra varied, spaced reading carries it".

## The read

    run            gap     fields   wishes 192   plain lift   lm narr / conv / web        chats
    base      s1   7.896   0.56     0.35         0.49         0.4864 / 0.5579 / 0.9512   8
              s2   8.064   0.53     0.32         0.47         0.4883 / 0.5599 / 0.9522   6
    surprise  s1   7.650   0.55     0.32         0.47         0.4873 / 0.5584 / 0.9536   7
              s2   7.802   0.53     0.33         0.48         0.4857 / 0.5566 / 0.9480   5
    random    s1   7.814   0.52     0.38         0.48         0.4859 / 0.5571 / 0.9515   8
              s2   7.923   0.51     0.32         0.47         0.4873 / 0.5604 / 0.9522   6

(gap: `probe_word_surprise.py`, the 300 held-out targets less the 60 common
words, summed nats; `evals/results/nano5m_random__wordsurprise.txt`)

**The gates, as registered.** Fluency: holds -- every text row under its
fall line (0.4913, 0.5629, 0.9552), chats 8 and 6 of 10 against the base
seeds' 8 and 6. (s), the surprise choice earns its keep: no -- both random
gaps are above 7.802, but the pair mean 7.869 is under 7.893. (e), the
reading carries it: no -- seed 2's 7.923 is above 7.896. **(m)**: random
choice helps less, not separably at the gap. Unreadable: no -- the guard
passes on both logs (and on all five run logs), each run steered its full
36,659 rows, and the random sets overlap the surprise sets exactly at chance
(Jaccard 0.239-0.241 against 0.239 expected).

## The steered-target split -- what (m) sends us to

Drop in the word's own held-out sentences, base pair mean less the run
(`evals/results/nano5m_random__wordfit.txt`), with the steering dose and
timing off each run's log:

    run           band    targets   drop     rows a word   first steer   last steer   z at first steer
    surprise s1   10-30   27        +1.75    2.70          3,068         3,468        +1.22
    surprise s2   10-30   29        +0.98    3.21          2,638         3,904        +1.32
    random s1     10-30   20        +0.70    4.20          1,072         4,536        +0.12
    random s2     10-30   23        +0.13    4.30            873         4,703        +0.07
    surprise s1   30-100  46        +0.41    3.41          2,298         4,032        +0.79
    surprise s2   30-100  42        +0.44    3.29          1,952         3,584        +0.81
    random s1     30-100  37        +0.33    4.19            800         4,608        +0.00
    random s2     30-100  36        +0.32    3.72          1,440         4,585        +0.17

(steps are medians over the band's steered targets; the run is 5,237
steps.) The unsteered rare targets move alike in every arm (+0.25 / +0.18
surprise, +0.30 / +0.08 random). The word-fit share on the random arm's
steered words is 0.61 and 0.26 -- mixed, as the surprise arm's (finding
199), on thinner drops.

**The order holds at both seeds and in both bands, and it does not come
from dose.** The random rare words got *more* rows than the surprise ones
and fell less. Nor from picking harder words: the surprise seeds' rare
targets were harder than their band at seed 1 (19.56 nats against 18.05)
and easier at seed 2 (17.38) and fell most at both. The groups are small
(20-29 words, the per-word drops spread several nats), so the size of the
gap between arms is a direction; its sign is the same four times.

## Why a noise score still chooses better than random

Finding 200: the progress score is noise -- a frozen model picks the same
words. But the score is not the whole rule. A word is eligible only once
**he has met it three times** in his own reading and while **he still
finds it harder than the average candidate** (`fast > 0`), and only then
does the noise rank it. That gate has two effects the random control
removed:

* **the word is one he has started on and not finished** -- at the first
  steer its recent surprise sits 1.2-1.3 above the average candidate's;
  the random picks sit at the average;
* **the steering lands when the model can use it** -- a rare word reaches
  three sightings only well into the run, so the surprise arm's rare-word
  steering starts near step 2,600-3,100 and ends by 3,500-3,900; the random
  arm starts within the first thousand steps, during warmup and the
  model's first pass at language, and spreads to the end.

Which of the two does the work is not separable here.

## What it licenses

* **Keep the gate, drop the progress score.** The part of the scheduler
  that beats random is "met a few times, still hard"; the ranking by
  learning progress adds nothing a frozen model does not (finding 200).
  The arm that tests it: steer eligible words (3+ sightings, `fast > 0`)
  in random order, or ranked by `fast` -- how hard the word still is --
  against the surprise arm as it stands.
* **Timing needs its own control**: the same random set with steering held
  back until a fixed step (say 2,000) separates "started on" from "late
  enough to keep".
* **Nothing here reaches understanding at 5M** -- fields, wishes and lift
  stay inside the base pair's spread in every arm (random seed 1's wishes
  0.38 is one seed, not a gate) -- so the 20M is still where the reading
  change has to show it, with the gate-only rule beside the full one.

**What it does not settle.** Which half of the gate does the work; any
size above 5M; whether the per-word order survives larger target groups
(the held-out read has 100 words a band, of which an arm steers 20-46).
