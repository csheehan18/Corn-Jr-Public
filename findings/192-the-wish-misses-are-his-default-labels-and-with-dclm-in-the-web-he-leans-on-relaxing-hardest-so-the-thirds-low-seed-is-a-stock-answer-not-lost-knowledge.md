# With DCLM mixed in, he leans harder on one stock answer

**Full result:** The thirds' low seed (finding 191: wishes 0.31 on 192 items against its twin's 0.37) did not learn less -- its checkpoint is the last iteration, its validation loss the lowest of the four web runs (2.407), its loss on every web source lower than its twin's, its misses spread over seven of eight kinds; what moved is the default: asked with descriptions that answer none of the options, every 20M falls back on a stock label, and his real misses follow those defaults label for label (r = 0.62-0.91 over the 36 labels); both DCLM seeds lean on their defaults hardest of any mix (top two labels 0.36 and 0.39 of no-answer picks, *relaxing* 47 and 56 of 192, misses r = 0.91 and 0.89) and the blend least (0.25, 0.29; r = 0.62, 0.68); the label frequencies of DCLM's text do not explain it

**Cost:** 13:20-13:43 on 2026-10-21; the checkpoint and log reads on CPU; the misses re-read on four runs and the default read on ten checkpoints, 143.6 s, contended (the card at 36%, a bound).

**The question** (owner, 2026-10-21: "wanna double check why? Like what
went wrong?"). Finding 191 showed the thirds' second seed reads at the Edu
level on 192 wish items, the new 96 included, while its twin and both blend
seeds read 0.37-0.38.

## What it is not

    run                        ckpt iter   ckpt val   web    web_plain   web_dclm   (per-source at iteration 5237)
    B  nano20m_v3_webblend     5125        2.527      3.669  3.811       --
    B  _seed2                  5125        2.478      3.694  3.846       --
    T  nano20m_v3_webthirds    5237        2.488      3.517  3.758       3.623
    T  _seed2                  5237        2.407      3.490  3.741       3.607

* **Not undertrained**: both thirds checkpoints are the last iteration, and
  seed 2's validation loss is the lowest of the four.
* **Not the everyday text learned worse**: seed 2's loss is lower than its
  twin's on all three web sources.
* **Not a lost topic**: against its twin it reads 1-3 items lower in seven
  of eight kinds and 2 higher in one; its 23 extra misses have 17 different
  right answers.
* **Not the words of DCLM's text**: the label the thirds favour, *relaxing*,
  is rarer in DCLM (6.1 per million words) than in plain FineWeb (17.5); the
  label they almost never pick, *funny*, is commoner in DCLM (74.1 against
  47.3).

## What it is: the default (`scripts/probe_wish_defaults.py`)

Every description is put to the kind next to it -- "a vet helping farm
animals in a sleepy valley" asked as a *game* -- so no option is right and
the label picked is his default; scored exactly as the ruler scores.

    run                          real read   defaults: top two   leading default   misses vs defaults (r)
    Edu  nano20m_v3              60/192      0.26                relaxing 28       0.79
         _seed2                  55/192      0.32                relaxing 40       0.80
         _compiled               61/192      0.32                relaxing 40       0.77
    P  filtered plain            68/192      0.31                relaxing 41       0.81
       _seed2                    65/192      0.30                relaxing 36       0.84
    B  half Edu, half P          71/192      0.25                relaxing 27       0.62
       _seed2                    73/192      0.29                relaxing 39       0.68
    T  thirds with DCLM          71/192      0.36                relaxing 47       0.91
       _seed2                    60/192      0.39                relaxing 56       0.89
    corn_jr_260m_v4 (Edu)        111/192     0.25                romantic 25       0.69

**His misses are his defaults.** On every checkpoint the labels he picks
when nothing fits are the labels his wrong answers land on (r 0.62-0.91):
when the meaning of a description is too weak to decide, the stock answer
decides. GENERATORS §5's signature -- a default that differs by seed -- read
here on a ruler rather than a corpus.

**DCLM strengthens the default and the blend weakens it.** Both thirds
seeds lean on their defaults more than any other mix, and their misses
follow the defaults most closely; seed 2 leans hardest of all and reads
lowest. The blend's two seeds lean least and their misses track the
default least -- there, more of what he gets wrong is something other than
the stock answer. The 260M leans as little as the blend, on a different
stock label.

## What it licenses

* **The thirds' low seed is a stock answer, not lost knowledge.** DCLM in
  thirds did not take the everyday web's understanding away; it made him
  fall back harder on a default when unsure, and one seed of two fell far
  enough to read at Edu's level.
* **The blend is right for a second reason**: it carries the weakest
  default pull of any 20M mix, not only the highest read.
* **The wish read measures the default as well as the meaning.** A read
  that decides a share should print the default pull beside the score --
  `probe_wish_defaults.py` costs seconds a checkpoint.

**What it does not settle.** Why DCLM strengthens the default (its label
frequencies say it should not); whether two seeds' ordering holds with more;
whether the default pull at 260M moves with the web share.
