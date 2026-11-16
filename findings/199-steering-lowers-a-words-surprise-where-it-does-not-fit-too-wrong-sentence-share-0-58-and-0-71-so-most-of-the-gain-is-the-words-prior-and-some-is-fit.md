# Steering mostly teaches how likely a word is, partly where it fits

**Full result:** On finding 198's runs, a steered rare word's surprise falls in sentences where it does not fit as well as where it does: on the held-out targets the scheduler steered at 10-30 and 30-100 sightings, the drop in eight wrong sentences is 0.58 and 0.71 of the drop in the word's own eight (seed 1: own −1.75 / wrong −1.12 at 10-30, −0.41 / −0.17 at 30-100; seed 2: −0.98 / −0.81, −0.44 / −0.23) -- the pre-registered *mixed* row at both seeds, against a predicted 0.8. The unsteered targets and the common words move neither column. By hand, the two columns move together word by word (*celebs* −4.3 own / −4.0 wrong, *nosebleeds* −6.1 / −4.3); how much more he expects a word where it fits grows on 20 of 27 and 16 of 29 steered words

**Cost:** writing `scripts/probe_word_fit.py` and a CPU dry run 08:20-08:30 on 2026-10-22, pre-registered at 565d9dd; the read 4 checkpoints in ~10 s (the card free, run directly -- two launches through `gpu.py run` without `--detach` stalled at 99% of the card and were killed, cause unread); hand read 3 min. ETA 15 min, actual ~25 with the two stalls.

**The question** (the review of finding 198, 2026-10-22). Finding 198
showed steering lowers his surprise on a steered word in sentences he never
read. That is necessary for knowing the word, not proof: three extra
sightings could simply raise the word's prior -- how likely it is anywhere
-- which lowers its surprise in every sentence alike. Knowing a word is
expecting it where it fits *more* than where it does not.

**The read** (`scripts/probe_word_fit.py`). Each of the 300 held-out targets
and 60 common words (`evals/word_surprise.jsonl`) is scored in its own eight
held-out sentences (*right*) and put into eight other targets' sentences in
place of that target (*wrong*), the partners drawn once by seed from words
of the same suffix class (-ing, -ed, -ly, plural, noun and adjective
endings), so the slot mostly takes the same part of speech: "the evidence
of dune *iridescent* at the mid-section", "denounce sexual *demolition*".
*Fit* is wrong less right. Unit: summed nats on the word's tokens, as
`probe_word_surprise.py`.

    run                  10-30 right/wrong/fit   30-100              100-300             common
    base s1              17.94 20.19 2.25        14.32 16.45 2.13    11.41 13.71 2.30    6.66 10.27 3.60
    base s2              18.16 20.41 2.25        14.46 16.53 2.07    11.28 13.69 2.41    6.57 10.17 3.60
    surprise s1          17.40 19.91 2.52        14.18 16.42 2.24    11.22 13.45 2.22    6.62 10.29 3.67
    surprise s2          17.63 19.92 2.29        14.31 16.51 2.21    11.35 13.58 2.24    6.63 10.21 3.58

The instrument reads what it should on the base: fit is 2.1-2.4 nats on
rare words and 3.6 on common ones -- the better he knows a word, the more he
expects it where it belongs.

**Steered against the rest** (drop, base pair mean less the run; *share* is
wrong's drop over right's):

    seed 1          steered: n  right   wrong   share      rest: n  right   wrong
    10-30                  27   +1.75   +1.12   0.64            73  +0.25   +0.11
    30-100                 46   +0.41   +0.17   0.41            54  +0.04   -0.01
    100-300                44   +0.04   +0.24   --              56  +0.19   +0.26
    seed 2
    10-30                  29   +0.98   +0.81   0.83            71  +0.18   +0.20
    30-100                 42   +0.44   +0.23   0.53            58  -0.17   -0.21
    100-300                45   +0.12   +0.26   --              55  -0.10   +0.00

    pooled steered 10-30 + 30-100: share 0.58 (seed 1), 0.71 (seed 2) -> mixed, both seeds

(100-300 drops are inside the noise at both seeds and do not enter the share.)

## Read by hand

The 27 and 29 steered 10-30 words, one line each, read in full
(`evals/results/wordfit__...json`). The two columns move together: the
words that fell most in their own sentences fell most in wrong ones too --
*polytheistic* −6.2 / −4.4, *nosebleeds* −6.1 / −4.3, *euphemism* −5.2 /
−3.4, *celebs* −4.3 / −4.0 (seed 1); *illusory* −4.3 / −2.8, *voluptuous*
−4.2 / −4.4 (seed 2). A few gained fit cleanly (*thermoregulatory* −2.5 /
−0.6, *sauerkraut* −1.8 / +0.6, *striations* −2.7 / −0.8). Medians: seed 1
right −1.44, wrong −0.62; seed 2 −0.93, −0.82. Fit grew on 20 of 27 and 16
of 29.

## What it licenses

* **Most of the per-word gain is prior, not fit.** Three or four extra
  sightings at 5M mostly teach him that the word *exists and is likely*;
  between three tenths and two fifths of the drop (1 - 0.71, 1 - 0.58) is
  specific to sentences where
  it belongs. That is learning -- a 5M's base fit on a rare word is only
  2.25 nats -- but it is the shallow part.
* **Report fit beside surprise from here.** A held-out surprise drop alone
  overstates what a reading intervention taught; `probe_word_fit.py` is the
  column that separates them, and the random-word control (pre-registered at
  12fd610) is read through it too.

**What it does not settle.** Whether the wrong sentences are wrong in
meaning or partly in grammar (the suffix classes are a proxy for part of
speech; *other* holds 109 of 300 words); any size above 5M; whether a
longer dose per word moves fit more than prior.
