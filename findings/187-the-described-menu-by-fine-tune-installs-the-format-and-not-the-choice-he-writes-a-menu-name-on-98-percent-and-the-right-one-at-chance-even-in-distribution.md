# Trained on invented names, he learned to copy one, never which

**Full result:** At 20M, a fine-tune on 60,000 described-menu lines (an invented name beside each property's description, the request phrased by meaning) teaches him to answer with one of the menu's names -- 197-200 of 200 fresh training-format lines -- and not which one: the right name on 0.21-0.30 of them against a chance of 0.25, and every held read at chance on all three starts (ruler 0.23-0.25, held kinds 0.17-0.26, held phrases 0.20-0.28); the pick does not move with the request; the pre-registered row "the link does not form at this dose", with finding 186's plain read 0.02-0.05 lower

**Cost:** the build 18:48-19:05 on 2026-10-20 (ac14986); the chain -- three starts read, three fine-tunes of 142, 124 and 124 s, three reads -- 640.0 s; the four-column re-read of six checkpoints 214.2 s and the in-distribution read 21.9 s; all contended (the card at 38-41%, a bound).

**The question** (owner, 2026-10-20: "yes let's do it", on finding 186's
proposal). Finding 186: he does not read a described menu, though the
descriptions alone pick the field at twice chance. Can a slice built on
GENERATORS' rules teach the link -- the name beside the description the
request means -- and does it carry to kinds and words he never trained on?
Pre-registered at ac14986 (`configs/mix_v3_described_ft.py`).

**The arm.** `corn/describegen.py`: 20 trained kinds, 80 properties, two
descriptions and four trained phrases each; an invented name per property
drawn fresh for every line (56,821 effective answer values); no request
sharing a content stem with any description in its menu; the answer in each
slot 25%. `scripts/check_described.py` (guard 100) holds it from the bytes.
Three fine-tunes from finding 186's starts, `mix_v3` as replay, the payload
0.93 passes, 650 iterations.

## The read

    start / fine-tune      held phrases   held kinds    ruler        in-distribution
                           (chance 0.25)  (0.25)        (0.24)       right / a menu name
    nano20m_v3             0.21           0.25          0.23         --
      ft_described_v3      0.20           0.24          0.25         61/200 / 197
    nano20m_v3_seed2       0.17           0.20          0.24         --
      ft_described_v3s2    0.28           0.17          0.23         42/200 / 199
    nano20m_v3_compiled    0.30           0.25          0.23         --
      ft_described_v3c     0.26           0.26          0.23         54/200 / 200

(Held reads: the registered calibrated score. In-distribution:
`scripts/probe_described_indist.py`, 200 fresh lines in the training format,
greedy-decoded.)

**Every gate fails on every start**, the installs gate included: the
pre-registered row is "installs below its gate -- the link does not form at
this dose". The prediction (installs and carries 3 of 3, transfers 2-3 of 3)
was wrong on all three.

**He learned the format and not the choice.** On the training format he
writes a menu name 98-100% of the time, from every slot (slots 0-3 written
42/51/50/54, 72/36/37/54, 63/47/36/54), and the right one at chance. On the
probe's held frames 54-69% of decodes write a menu name, against 0 of 903 on
every start. Nothing points at which: the request does not move the pick.

## An instrument suspicion, cleared

One decode on the first fine-tune wrote the gold name ("a tent that sheds a
heavy shower" -> kraglek) where the calibrated read scored a miss, and the
calibration -- the request's score minus the score with it taken out -- was
suspected of subtracting a real signal. The probe gained three columns to
test it (`raw`, the pick with the request; `prior`, the pick without it;
`writes`, the decoded word). On the fine-tunes `raw` reads the same count as
`prior` on six of nine rows and within three on the rest (ruler 32/32,
23/23, 22/22), both at chance: **the request does not move his rate of
picking right**, so the calibration was not hiding a reading of it, and that
decode was the menu-only favourite landing on the gold. Finding 184's lesson
again: one decode is an anecdote; read all of them before blaming the
instrument. The in-distribution read, which needs no calibration, says the
same thing.

## What it costs

    start -> fine-tune     names (186's plain read)   desc-only    tool.copy_wide
    nano20m_v3             0.54 -> 0.51               0.49 -> 0.51   281 -> 293
    nano20m_v3_seed2       0.50 -> 0.48               0.43 -> 0.38   291 -> 273
    nano20m_v3_compiled    0.54 -> 0.49               0.49 -> 0.42   279 -> 292

The cost gate (`names` within 0.04) fails on `_compiled` (-0.05), and
desc-only falls on two starts: a payload that teaches nothing still costs the
reads it sits nearest. `tool.copy_wide` moves both ways, by up to 18 of 300.

## Why, and what it licenses

**The step was not one he could take.** The answer needed two moves in one
token: match the request to a description by meaning, which at 20M is
two-times-chance and not reliable (finding 186's desc-only, 0.43-0.49), and
then copy the name standing to that description's left. GENERATORS: "dose
amplifies a step; it does not create one", and a step that is not a copy
does not form by fine-tune (findings 175, 179). With the meaning half too
weak to supply a gradient that points anywhere, the loss could only be
lowered by learning the half that is free -- an answer is one of these names
-- and that is what he learned.

* **A described menu is not, by this fine-tune at 20M, a lever on the
  meaning wall.** The format installs; the link does not.
* **The two halves can be separated, and should be next.** Finding 180 made
  a computed step into a copy and it installed 864 of 864: a request that
  restates its description word for word makes the link pure binding, with
  no meaning in it. If that installs, binding is his and meaning is the
  wall; if it does not, the binding itself does not form at this dose.
* **The vehicle is open.** Finding 74's re-ask needed the mix by four times
  where its fine-tune read a quarter of it; pretraining with the payload in
  the mix is the other vehicle, about 15 min a nano seed.

**What it does not settle.** Any size above 20M; a longer fine-tune or a
second pass; the pretraining vehicle; a curriculum from verbatim to
meaning; whether a menu of two, where the meaning read is easiest, forms
anything.
