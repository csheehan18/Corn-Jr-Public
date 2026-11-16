# His word vectors hold less than his framed answers do

**Full result:** Asked the way finding 221's book is asked -- add up, over a description's words, how close each word's vector sits to each candidate label, no sentence and no next-word prediction -- the two 20M controls answer 27 and 32 of the second 96 wishes and 61 and 57 of 141 fields from their word table, under their own framed read (35 and 37, 78 and 76) and far under the book (51 and 97). Every one of seven cells reads under the frame: the word table, his state half-way up and at the top for a word read alone, raw or with the common direction taken off, and his own top state for the whole description. The same holds at size: the 100M reads 27 and 69 from its table and the 260M 19 and 60 (34 and 63 at its best cell) against framed reads of 37 and 80 and 50 and 101. So the knowledge the ruler asks for is not sitting in him unread; what he holds comes out through the sentence, and a bag of his word vectors holds less. The book-pressed runs read 23 and 27 and 62 and 50, with the shuffled ones and the controls.

**Cost:** the probe and its pre-registration committed at 10:42 on 2026-11-13 (039044a, before a vector was read), written while finding 222's control trained; settings half 8.7 s of card, the read 36.7 s for eight checkpoints. ETA ~2 min of card; 45 s.

**The question** (owner, 2026-11-13, brainstorming why the book press failed:
"Yes", to reading his word table the way the book reads its pages). Finding
222's press moved neither ruler read. That left a list in two halves needing
different work: the knowledge **is not in him** (the press was too soft,
pressed the wrong tokens, or he has no room -- finding 197), or it **is in
him** and the ruler's read, a label's probability after a framed sentence,
does not reach it. Finding 161 saw the second shape once: a linear reader on
his state read 46 to 55 of 100 where he wrote 12 to 40. The pre-registration
is `scripts/probe_table_read.py`'s docstring.

## The read

Every ruler item as `probe_book.items()` cuts it: the description's words,
every one voting, and the candidate labels. A word's vector is read three
ways -- the mean of its pieces in the word table; his state after half his
blocks at the word's last piece, the word read alone; the same after his last
block -- and a label's score is the sum of the cosines between it and the
description's words. Each raw, or centred on the mean vector of the 20,000
commonest words. A seventh cell reads his top state for the whole description
against the label's. The cell was chosen on the first 96 wishes by the mean
of the two controls, and the second 96 and the fields were read once.

    settings half, first 96 wishes     seed 1337   seed 1338
    table raw                          29          31         <- chosen
    table centred                      31          24
    middle raw                         22          21
    middle centred                     21          26
    top raw                            20          21
    top centred                        25          24
    whole centred                      24          24
    his framed read                    36          36
    the book                           53

    the chosen cell, read once         wishes 2nd 96   fields (141)   his framed read
    nano20m_v3_webblend                27              61             35 / 78
    nano20m_v3_webblend_seed2          32              57             37 / 76
    nano20m_v3_webblend_press          23              62             35 / 77
    nano20m_v3_webblend_press_seed2    27              50             33 / 81
    nano20m_v3_webblend_press_shuf     29              63             30 / 82
    nano20m_v3_webblend_press_shuf_s2  27              54             35 / 87
    nano100m_v1          (reference)   27              69             37 / 80
    corn_jr_260m         (reference)   19              60             50 / 101
    the book                           51              97
    chance                             16              32

Per-item picks are in `evals/results/table__ruler_mix_v3_webblend.json`.

## The pre-registered rows

* **T fails.** 27 and 32 wishes against a fail line of 41, 61 and 57 fields
  against 82. Predicted between on wishes (38 to 45) and failing on fields;
  the wishes read lower than predicted, under his own framed read. The
  chosen cell was predicted centred; it is raw.
* **P is no.** The book-pressed runs read 23 and 27 where the row asked for
  37. The press put nothing in his word vectors that this read can see.
* **B.** The controls' best seed reads 32 and 61 beside the book's 51 and 97.
* **The 260M, predicted over 50 from its table, reads 19** (34 at its best
  cell, middle centred). The model that answers 50 of 96 through a sentence
  answers a third of that from its word table.

## What the cells say (read after, not gated)

    every cell, 2nd 96 wishes / fields   seed 1337   seed 1338   corn_jr_260m
    table raw                            27 / 61     32 / 57     19 / 60
    table centred                        27 / 55     20 / 42     21 / 58
    middle raw                           21 / 50     19 / 46     29 / 56
    middle centred                       26 / 53     22 / 50     34 / 63
    top raw                              21 / 43     21 / 46     20 / 57
    top centred                          28 / 59     30 / 49     26 / 58
    whole centred                        28 / 65     28 / 61     31 / 69

No cell reaches a framed read at any size, and nothing rises with depth at
20M. At 260M the middle and the whole description read above the table, the
direction finding 196 would predict -- what a description implies is built
up through the blocks, not stored on the word -- and still far under what
the same model says in a sentence.

## Read by hand: the second 96 at seed 1337

The table and the frame are right about different items: 16 the table gets
and the frame misses, 24 the reverse. The table gets descriptions that carry
a word near the label -- "lazy mornings in a hammock and naps every
afternoon" (relaxing), "a candle on every table and roses for two"
(romantic), "food on the table within three minutes" (quick). The frame gets
the ones that need the whole phrase -- "something knocks from inside the
walls every night at three" (scary), "an old dog waits at the station for an
owner who never comes back" (sad), "a whole meal for the price of a coffee"
(cheap) -- where the table answers `exciting`, `exciting` and `quick`. By
kind the table is near chance (4 of 24) on films, books, songs and shows (5,
4, 6 and 5) and best on holidays (12).

## What it licenses

By the pre-registration, **T fails: it is not in him by any read here.** The
book press result (finding 222) stands as "not learned" and not as "learned
and unread"; the list narrows to how hard a press can be -- a real one is
many steps on one meeting, which is rereading -- and to room (finding 197).
It also says where his understanding lives: a 20M's and a 260M's framed
answers both beat every read of their vectors, so the sentence is not what
hides it. The framed ruler is the better instrument of the two.

**What it does not settle.** A reader that is *trained* -- finding 161's was
a linear reader on his state, and this one is an untrained cosine -- could
find more than a sum of cosines does; that is a different probe and needs
held-out items the ruler does not yet have. The sixteen items the table gets
and the frame misses are not nothing: the two reads err differently at every
size, as the book and the 260M did (17 against 16 in finding 221).
