# A model a quarter as wide nearly matches the 20M's understanding

**Full result:** On finding 189's blend and the 20M's own 128.7M-token schedule, a 6.95M-parameter model (6 layers x 256, lr 3e-3 from a five-point sweep) reads the understanding ruler's fields 0.56 and 0.53 against the 20M blend's 0.55 and 0.54 and its 192 wishes 0.35 and 0.32 against 0.37 and 0.38, the plain lift 0.49 and 0.47 (chance 0.41), no everyday word in its own words at either seed, and a stock-answer pull (0.28, 0.27) between the blend's and Edu's -- while its language loss sits about 0.045 nats a byte above the 20M's on all three text rows; at this budget the understanding reads barely move between 5M and 20M, so they are not reading width there

**Cost:** 22:24-23:13 on 2026-10-21; trainbench 6 s; the lr sweep, seven 1,000-iteration runs, 7.7 min; both base runs with card and four reads in one chain, 19.7 min (training 350 and 354 s); the chats and the held-out word read 18 s; all contended (the card at 37-40%, a bound).

**The question** (owner, 2026-10-21). The surprise-steering idea is to be
iterated at about 5M before anything bigger. Before a mechanism is built on
it: where does a 5M on the blend sit on every instrument the arm will be read
by -- how far above chance, and how far below the 20M?

**The shape and the rate.** `configs/nano5m_v3_webblend.py`: `configs/nano.py`'s
shape on bpe8k, 6,950,144 parameters (4.7M not in the embedding), ~19
tokens a parameter on the blend's 5,237 iterations. Trainbench: 58.5 ms a
step, 420k tokens a second, 1.72 GB peak. The 20M's 6e-4 was suspect at a
quarter of its width, so a sweep at 1,000 iterations (validation loss at the
end, cosine to a tenth):

    lr      6e-4    1e-3    2e-3    3e-3    4e-3    6e-3    8e-3
    val     3.770   3.619   3.452   3.379   3.320   3.370   3.621

The run takes 3e-3, one below the short horizon's best, since a short sweep
overstates the best rate of a run five times longer. The 20M's rate reads
0.39 worse here.

## The read

    run                         fields   wishes 192   plain lift   words free / pick   defaults top2 / r   lm narr / conv / web
    5M  nano5m_v3_webblend      0.56     0.35         0.49         0/40 / 0.35         0.28 / 0.79         0.486 / 0.558 / 0.951
        _seed2                  0.53     0.32         0.47         0/40 / 0.45         0.27 / 0.70         0.488 / 0.560 / 0.952
    20M nano20m_v3_webblend     0.55     0.37 (191)   --           0/40 (189)          0.25 / 0.62 (192)   0.453 / 0.513 / 0.906
        _seed2                  0.54     0.38         --           0/40                0.29 / 0.68         0.452 / 0.513 / 0.907
    chance                      0.24     0.17         0.41         -- / 0.25

The everyday words, read by hand: no free answer means its word at either
seed -- *spendy* "that you're not going to be able to have a place to live",
*knackered* "that you're not going to be a good boy", and most of the rest
echo the word ("the 'sus' mean is the 'sus' mean"). The pick (0.35, 0.45)
flatters, as finding 189 said it would.

Ten free chats a seed, hand-written openers (`scripts/probe_free_chats.py`),
read by hand: 8 and 6 of 10 answer the opener in whole sentences ("I finally
finished painting the kitchen!" -> "That's great! What made you decide to
paint the kitchen?"); the misses answer something else ("Can you believe how
expensive groceries have gotten?" -> "It's a great deal, thank you"); neither
seed loops.

The held-out word read (`scripts/probe_word_surprise.py`, 300 words seen
10-300 times in his web text, 8 sentences each the mix never reads, and 60
common words): summed surprise on the word, in nats

    run        10-30    30-100   100-300   common   rare-word gap
    5M         17.94    14.32    11.41     6.66     7.90
    _seed2     18.16    14.46    11.28     6.57     8.06

-- rarer is more surprising, in order, at both seeds; this is the floor the
surprise-steered arm is read against.

## What it says

* **At this budget the understanding reads do not track width.** A quarter
  of the 20M's width and a third of its parameters read fields level with
  it and wishes 0.02-0.06 lower, inside the 192-item read's spread (finding
  189: about +-0.05 a run), on the same text. The language rows do track
  it: 0.03-0.05 nats a byte worse everywhere.
* **So finding 196's "grows with size" is, below 20M, mostly not size.** The
  size steps it read (20M to 100M to 260M) came with three to forty times the
  text. Here width moved and text did not, and the reads barely moved. That
  is the confound finding 196 named, now with one side of it read.
* **The 5M is a fair place to iterate the mechanism.** Its floor is above
  chance on fields, wishes and the plain lift, its chats are sentences, and
  the held-out word read separates the frequency bands cleanly.

**What it does not settle.** Whether the 20M's 6e-4 is itself under-tuned
(a 20M at its best rate might pull ahead of the 5M on the reads); more
seeds (two a side, and the wish spread is about +-0.05); the plain lift at
20M on the blend, which was not read; any size past 20M.
