# DCLM's stronger stock answer is not in its text

**Full result:** The thirds' stronger pull toward a stock wish label (finding 192) is in all three of the ruler's phrasings -- top-two default share 0.31-0.42 against the blend's 0.25-0.32, frame by frame -- and not in DCLM's words: the label it favours, *relaxing*, sits in the answer slot (after feels, is, so, very, pretty, really, call it) 0.5 times per million words in DCLM against 0.9 in plain FineWeb, 0.2% of all slot uses against 0.5%, while DCLM carries more "so funny" and "so sad" (10.1 and 10.5 against 6.0 and 6.2) and the thirds do not favour either; both registered predictions failed, so the cause is not a text pattern and two seeds cannot name it

**Cost:** 13:48-13:52 on 2026-10-21; the per-frame default read on six checkpoints 121.8 s (contended, the card at 38%, a bound); the slot count over the first 1,000 MB of each web source 215 s on CPU.

**The question** (owner, 2026-10-21: "come up with a quick investigation
and then we will move on with the half and half"). Finding 192: both
thirds seeds lean on a stock label hardest of any mix, *relaxing* above all,
and the label's plain frequency in DCLM says they should not. Two
predictions were stated before either read: the review phrasing ("Review:
... Overall this film feels ___") carries most of the thirds' pull; DCLM
has more *relaxing* in that slot per million words than plain FineWeb.

## Phrasing (`probe_wish_defaults.py --by-frame`)

    run                     "people would call it"   "in one word, it is"   "Review ... feels"
    T  nano20m_v3_webthirds  0.34 (relaxing 43)       0.31 (relaxing 38)     0.39 (relaxing 52)
    T  _seed2                0.40 (relaxing 54)       0.39 (relaxing 58)     0.42 (romantic 47)
    B  nano20m_v3_webblend   0.25 (relaxing 28)       0.29 (sad 32)          0.30 (relaxing 34)
    B  _seed2                0.32 (relaxing 36)       0.28 (relaxing 37)     0.27 (relaxing 30)
    P  nano20m_v3_plainclean 0.36 (relaxing 48)       0.26 (relaxing 28)     0.34 (relaxing 36)
    Edu nano20m_v3           0.24 (relaxing 29)       0.28 (sad 30)          0.27 (relaxing 28)

(top-two share of 192 no-answer picks; the leading label in brackets)

**The pull is in every phrasing.** Both thirds seeds lean harder than both
blend seeds in each frame taken alone, and seed 2's review frame leans to
*romantic*, not *relaxing*. The first prediction fails.

## Text (`scripts/count_wish_slots.py`)

    per million words      in the slot / anywhere
                           edu          plain         dclm
    relaxing               0.2 / 4.0    0.9 / 16.5    0.5 / 6.0
    romantic               0.1 / 11.2   0.6 / 25.7    0.6 / 21.0
    funny                  0.6 / 6.4    6.0 / 47.5   10.1 / 72.7
    sad                    1.7 / 14.5   6.2 / 33.3   10.5 / 55.2

**DCLM puts *relaxing* in the slot less often than plain FineWeb does**,
and puts the labels the thirds never favour there more often. The second
prediction fails.

## What it licenses

* **The stronger stock answer is not taught by DCLM's word patterns.** It
  is something about how training went with the web in thirds -- each
  source a third, DCLM among them -- and two seeds cannot say what.
* **Nothing here changes D1**: finding 189's blend stands on a higher read
  and the weakest default pull of any mix (finding 192).
* **The investigation stops here, as agreed.** More seeds of the thirds, or
  DCLM in place of Edu, would be the next reads if DCLM is wanted again.

**What it does not settle.** The cause; whether the thirds' stronger default
holds over more seeds.
