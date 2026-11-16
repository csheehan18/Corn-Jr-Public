# A book of tallies, no weights, beats the 20M on word meaning

**Full result:** A book written in one pass over `data/mix_v3_webblend/train.bin` -- one page a word, each line "met near that word" with a tally, no gradient and nothing tuned -- reads the understanding ruler at 51 of the second 96 wishes (0.53) and 97 of 141 fields (0.69). The two 20M controls that trained on the same 130,279,713 tokens read 35 and 37 (0.36, 0.39) and 78 and 76 (0.55, 0.54); paired, the book is ahead 32 : 16 and 27 : 13 on the wishes (p 0.029, 0.038) and 37 : 18 and 39 : 18 on the fields (p 0.014, 0.008). It sits level with the 260M pretrain, which read other tokens: 50 of 96 and 101 of 141 (17 : 16, 21 : 25). Its margin tells right from wrong (AUC 0.67 against the controls' 0.51 and 0.52), so scored right +1, pass 0, wrong -1 it reads +0.17 answering half the items, where the controls read -0.03 and -0.02. Two things it does not have: on the wishes the lead rests on lines met once or twice (drop them and 51 becomes 37, the controls' level), and it has stock answers of its own (`sad` picked 17 times for 8 asked, `long` 17 for 4), which is why counting the meetings behind an answer reads *backwards* as confidence (AUC 0.35). The knowledge the 20M lacks (finding 196) is in its own corpus; one pass of gradient descent at 20M does not pick it up, and a count does.

**Cost:** 16:05-16:21 on 2026-11-11 (the last three minutes the guard sweep), pre-registered at 327ee9f before the second 96 wishes or a field was scored. Word stream 42 s on CPU, once; the tally 1.3-1.4 s of card for 2,572,068,769 meetings; card time under the lock 7.6 s (settings half), 86.1 s (the read, four checkpoints through the ruler), 11.6 s (cause reads), 4.6 s (fields hand read) -- contended at 32%, so every timing is a bound. ETA ~45 min all in and under 5 min of card; it took 16 min and 110 s.

**The question** (owner, 2026-11-11: "I don't think millions of knobs are
the future for it", then "Okay let's do this experiment"). `docs/IDEAS-UNDERSTANDING.md`
§7 keeps returning to words with homes: an explicit entry a word, written
rather than tuned, so that one meeting leaves a mark and "do I know this?"
can be looked up. The plainest form of that is a count. The kill line was
set before anything ran: if a book with no weights cannot beat the 20M on
the wishes, reading the same tokens, the idea is not worth a second step.
The pre-registration is `scripts/probe_book.py`'s docstring.

## The book

Words are runs of letters over the decoded, lower-cased stream: 74,727,866
words, 393,826 distinct. A page has one kind of line -- "this word was met
within ten words of that word" -- and a tally. A line's weight is how much
more often the two met than their counts alone would give (PPMI, the
neighbour's count smoothed to the 0.75 power). An item is answered by adding
up, over every word of the description, that word's line to each candidate
label; the heaviest label wins. No frame, no stop list. The tally is checked
cell for cell against a plain loop on the first 200,000 words every run.

The cell -- window 10, PPMI, direct -- was chosen on the first 96 wishes
(0.55 there) out of sixteen, and then the second 96 and the fields were read
once.

## The read

    read                              wishes, 2nd 96   1st 96   fields (141)   margin AUC   card (attempted)
    book, window 10 ppmi direct       51  (0.53)       0.55     97  (0.69)     0.67         +0.17 (0.52)
    nano20m_v3_webblend               35  (0.36)       0.38     78  (0.55)     0.51         -0.03 (0.18)
    nano20m_v3_webblend_seed2         37  (0.39)       0.38     76  (0.54)     0.52         -0.02 (0.10)
    nano100m_v1          (reference)  37  (0.39)       0.44     80  (0.57)     0.62         +0.01 (0.41)
    corn_jr_260m         (reference)  50  (0.52)       0.56     101 (0.72)     0.70         +0.17 (0.40)
    chance                            0.17                      0.23           0.50

    paired, second 96 wishes          book only : model only
      against the 20M, seed 1337      32 : 16   p 0.029
      against the 20M, seed 1338      27 : 13   p 0.038
      against the 260M                17 : 16   p 1.0
    paired, fields
      against the 20M, seed 1337      37 : 18   p 0.014
      against the 20M, seed 1338      39 : 18   p 0.008
      against the 260M                21 : 25   p 0.66

The models were read through the ruler's own `score`; the controls' totals
reproduce the committed 0.37 / 0.55 and 0.38 / 0.54 (asserted). The card is
right +1, pass 0, wrong -1 over the second 96, passing below a margin set on
the first 96; answering everything, the book reads +0.06 and the controls
-0.27 and -0.23. Per-item picks and margins are in
`evals/results/book__ruler_mix_v3_webblend.json`.

## The pre-registered rows

* **W holds.** 51 against 35 and 37: above both seeds by 14 and 16 items,
  where 5 was asked. Predicted 0.45-0.60; read 0.53.
* **F: the prediction failed, upward.** Predicted below the controls
  (0.40-0.50) because field phrases lean on word order, which the book has
  no line for. It read 0.69. The cause, from the hand read: the phrase's one
  content word sits beside the field's name in ordinary text -- `cheap`
  beside `price` (52 meetings), `midnight` beside `hours`, `yoga` beside
  `classes`, `writer` beside `author` -- and the labels are common words
  with thick pages, so this half does not lean on thin lines (0.67 with
  every line met under three times dropped).
* **A holds.** Margin AUC 0.67 against 0.51 and 0.52. The controls came in
  under the predicted 0.55-0.65: a 20M's margin on this ruler says nothing
  about whether it is right. **The second footing reads backwards:** the
  number of meetings behind the winning lines has AUC 0.35 -- more meetings,
  more often wrong. See the stock answers below.
* **C holds.** +0.17 at 0.52 attempted against -0.03 and -0.02; the 260M
  reads the same +0.17 at 0.40 attempted.

## What the number rests on (read after, not gated)

    who votes, on how many meetings            wishes, 2nd 96   fields   margin AUC
    as registered                              51  (0.53)       0.69     0.67
    lines met under 3 times dropped            37  (0.39)       0.67     0.68
    the 200 commonest words silent             53  (0.55)       0.67     0.69
    both                                       41  (0.43)       0.65     0.69

* **It is not the function words.** Hand-reading the lines showed `a`,
  `she`, `the` voting (`she` to `sad`, 9,279 meetings -- the story slice).
  Silencing the 200 commonest words moves 51 to 53.
* **On the wishes it is lines met once or twice.** `snug` met `cosy` once
  in the whole stream and that line answers "a snug corner booth beside a
  wood stove"; `scree` met `challenging` once; `sweethearts` met `romantic`
  once. Fourteen of the 51 go when such lines are dropped, and the book is
  then level with the controls. This is the idea's claim seen from both
  sides: one meeting writes a usable line, which the 20M's weights do not
  hold -- and one meeting is also `ballad` beside `upbeat`, which answers a
  funeral song wrongly.
* **It has stock answers.** Over the 192 wishes it picks `sad` 17 times for
  8 asked and `long` 17 for 4, and never picks `easy` or `wholesome`; the
  share of misses going to its two commonest picks is 0.27, the same as the
  first control. A label met 50,759 times has some line to nearly every
  word, and a weight clipped at zero lets those add up. That is the cause of
  the backwards evidence read: how often the picked label was met has AUC
  0.34 for being right, the same as the evidence's 0.35.

## Read by hand: all 96 second-half wishes, every field miss, a quarter of the field hits

Right for the reason a person would give: `hammock` to relaxing, `pines` to
shady, `couples`, `roses` and `wedding` to romantic, `dark` to scary (197
meetings), `shouted` to angry (184), `teaching` to educational, `coffee`,
`price` and `pasta` to cheap, `views` to scenic.

Wrong in three ways, each one a dimension of `IDEAS-UNDERSTANDING.md` §2
that a "goes with" line cannot hold:

* **Senses and set phrases.** `getaway` to romantic (a getaway driver),
  `hopeless` to romantic, `visits` to educational, `spacious` to bedrooms
  (property listings), `foam` to firmness. The line is real; it belongs to
  another sense.
* **Opposites meet.** "a short level loop a toddler could manage" reads
  `long` on `short` (1,405 meetings). A word and its opposite keep the same
  company.
* **No "is a kind of".** "a film that's scary" asks for `genre`; `scary`
  has no line to it. "a pokemon that's a fire one" reads `attack`.

Two ruler words were never met (`handclaps`, `vicar's`). The page for
`cosy` (101 meetings; the web writes `cozy`, 1,201) reads spacious, comfy,
armchair, fireplace, den, warm (18), cottage -- and negligible (1), decks
(1): a rough sketch with pencil marks in it.

## What it licenses

* **The kill line is passed, so the idea earns a second step.** The
  knowledge the ruler asks for is in the 130M tokens the 20M read; what the
  20M lacks is a way to keep it at one pass. Finding 196 placed the loss in
  knowledge rather than format and found it growing with size; this places
  it one step further back, in how the knowledge is held.
* **Speed, as a bound.** Reading the stream is 42 s of CPU once and the
  tally 1.4 s of card, contended. Nothing is retrained to add text or a
  word.
* **The margin is a usable "not sure"; the raw tally is not.** Footing has
  to be how far the winner is ahead, not how much was met.
* **Three next reads, each one variable on this book:** take each label's
  own average weight off its lines (the ruler's with-and-without step, and
  the fix the stock answers name); a second kind of line for opposites and
  kinds ("X and Y", "X but Y", "X is a Y"); and the step the design turns
  on -- put a word's heaviest lines in the 260M's context and read whether
  he uses them.

**What it does not settle.** Whether he can read a page: the book answers a
forced choice and cannot say a sentence. Anything beyond association -- the
ruler is description to label, the shape a count is best at, so this is the
book's best case and dimensions 4 to 9 of the word card are unread. A
like-for-like row at 100M and 260M: those two read other tokens and are
reference lines only. Whether the wishes lead survives a second corpus,
since it rests on lines met once or twice. The cell was chosen from sixteen
on 96 items; the second 96 and the fields are clean of that choice, and the
other fifteen cells are printed by the probe (direct PPMI reads 0.47-0.55
on the second 96 at every window). **Tally overlap reads chance (0.17) at
every window** and was not diagnosed: treat it as a broken cell, not as a
result about comparing pages.

## Amended 2026-11-13 -- who had a page, and the read with the ruler unseen

The book above gave a page to the 5,000 commonest words **and to every word
of the ruler** (336 more pages, 5,336 in all), and a column to the 20,000
commonest and to every ruler label (6 more), because it had to answer the
ruler; "The book" section does not say so. Finding 227 read the book again
with the ruler never shown to it (`scripts/probe_read_homes.py --book-only`,
the same read):

    who has a page                                 wishes (192)   2nd 96   fields (141)
    as above (5,000 and every ruler word)          104            51       97
    the 5,000 commonest only                       71             36       88
    the 20,000 commonest only                      91             42       95
    the 20M controls                               71 and 73      35, 37   78 and 76

The result stands in its general form -- a count that never saw the ruler
leads the 20M by 18 to 20 wishes and 17 to 19 fields at 20,000 pages -- and
the wishes lead above (31 to 33) was partly the ruler's own rarer words
having pages. At 5,000 pages and none of them the book reads the wishes at
the 20M's level. "Level with the 260M" holds for the book as built; the
ruler-blind 20,000-page book reads 91 and 95 beside the 260M's 104 and 101.
