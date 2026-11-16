# A model that cannot learn picks the same words the scheduler did

**Full result:** Run with the finished base 5M frozen (learning rate 0), the surprise scheduler of finding 198 fills its cap (36,630 rows, 99.9% of steps at the cap) and steers 9,912 words that overlap the surprise arm's seed 2 at Jaccard 0.534 against 0.590 between the arm's two seeds (random sets of the same band sizes: 0.223 and 0.243) -- an excess ratio of 0.90, the pre-registered *noise* row; the learning progress its picks carried is no smaller than the arm's (median 0.675 against 0.637), and the arm's most-steered words are the frozen run's to the word (*smiled*, *recall*, *scared*, *toys*, *laughed*). One reading of a word varies 1.2 nats a token from sentence to sentence, which by itself puts the scheduler's progress score above its 0.05 bar for 46% of words at any moment

**Cost:** writing `scripts/probe_surprise_noise.py`, the frozen config and the read 08:30-08:45 on 2026-10-22 beside the word-fit read, pre-registered at 12fd610; the frozen run 434 s (contended, the card at 34%, a bound); the read and hand read ~3 min CPU. ETA 10 min of card, actual 7.2.

**The question** (the review of finding 198, 2026-10-22). The scheduler
calls a word "learning" when a fast average of his surprise on it (half
weight on the latest reading) drops below a slow one. But one reading
depends heavily on how much that particular sentence gives the word away. If
that variation is most of the signal, the scheduler's choice is a draw
shaped by which words are read often enough to cross the bar, and not by
what he is learning.

**The null.** `configs/nano5m_v3_webblend_surprise_frozen.py`: the base 5M
(seed 1337) loaded with lr and min_lr 0, so no weight moves; the arm's
scheduler, settings, stream and evals. Nothing can be learned, so every
word it steers it steers on noise.

## The read (`scripts/probe_surprise_noise.py`)

    run                 rows      words    at cap   progress at choice q25 / med / q75   z med   300-1000 share: first 1k steps / rest
    surprise s1         36,596    10,590   99.6%    +0.537 / +0.637 / +0.821              +0.651  0.41 / 0.13
    surprise s2         36,636    10,648   99.8%    +0.534 / +0.637 / +0.822              +0.641  0.41 / 0.13
    frozen              36,630     9,912   99.9%    +0.533 / +0.675 / +0.944              +0.750  0.32 / 0.15

    agreement of steered word sets   Jaccard   random sets, same band sizes
    surprise s1 vs s2                0.590     0.243
    surprise s2 vs frozen            0.534     0.223     (across streams, like s1 vs s2)
    surprise s1 vs frozen            0.550     0.222     (the same stream)

    ratio = (0.534 - 0.223) / (0.590 - 0.243) = 0.90; frozen fill 100% -> noise (pre-registered: >= 0.8 and >= 90%)

**The noise, measured** on the base pair's held-out per-sentence scores
(`probe_word_surprise.py`'s saved json, per token): one reading of a word
varies 1.21 and 1.18 nats from sentence to sentence, against 1.48 between
words. Through the scheduler's averages (0.5 and 0.15) that alone gives the
progress score a spread of 0.47; 46% of words sit above the 0.05 bar at any
moment on noise, and the arm's chosen words (median 0.64) are the top of
that spread -- about 1.4 of its standard deviations.

## Read by hand

The 25 most-steered words of the frozen run and of surprise seed 1 (they
share a stream) are the same list in the same order, one word apart --
*smiled, recall, scared, toys, laughed, import, sorry, walked, ants, disc,
anymore, shiny, climb, elect, loud* -- everyday story words that an
encyclopedic web share reads in sentences of very different predictability.
Of the 7,879 words both surprise seeds steered, 1,755 the frozen run never
did; a random 30 of them are mostly ordinary rarer words (*hypocrisy*,
*migraine*, *earthquakes*, *clavicle*, *tenses*), as are the frozen run's
own extras (*harrowing*, *sweatpants*, *porcupines*, *cameraman*) -- no
mark of learning on either side.

## What it licenses

* **At 5M the learning-progress score is noise.** It ranks words by how
  much their last few sentences happened to give them away; a model that
  learns nothing chooses the same words, at the same rate, with scores as
  high. Finding 198's word-level gains are real (the steered words fell),
  but this read says they came from *which words got extra sightings*, not
  from choosing them by his learning. The random-word control
  (pre-registered at 12fd610) reads that directly.
* **What the choice actually follows** is the stream: how often a word is
  read and how variable its sentences are. The two seeds agree at 0.59 for
  that reason, not because they learn alike.
* **A usable signal has to take the sentence out.** Scoring each reading
  against a reference model's surprise on the same sentence (the
  "reducible loss" of data-selection work, e.g. RHO-LOSS, Mindermann et al.
  2022) or averaging many more readings before acting are the two routes;
  either is a new arm, not a tweak.

**What it does not settle.** Whether the signal carries more at 20M or
later in a run (the frozen model is the finished one; the arm read a
learning one); the noise on training rows rather than held-out sentences
(the held-out read is the measurement; the frozen run is the behaviour);
whether a word-level score of any kind beats frequency here (finding 188:
a count beat surprise at finding hard words).
