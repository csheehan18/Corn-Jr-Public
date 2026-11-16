# Real exchanges around "never mind" taught the 5M nothing measurable

**Full result:** Thirty-six hand-written situations -- a line of his, a short turn ("Never mind.", "Maybe.", "Hmm.", "Fine.", "What?", "Whatever."), the reply that fits -- read by a swap inside each situation, so only the short turn can decide. The shipped 260M reads them at 0.75 of pairs right on the wordings the lesson would hold and 0.64 on reworded ones never in it ("Forget it.", "Perhaps.", "Um.", "Suit yourself."); ten ordinary 5Ms read 0.47-0.69 and 0.39-0.64, near chance. Two 5Ms reading 0.5% of the run as two-speaker subtitle exchanges around the seen wordings (2,636 windows, each read about nine times) against two reading the same amount of plain two-speaker exchanges: seen-half mean margin 1.04 and 1.24 against 0.84 and 0.60 (gap +0.42, rule 0.66), unseen 0.77 and -0.07 against -0.09 and 0.42 (gap +0.19, rule 0.93). Neither row holds; every arm sits inside the ten ordinary runs' band (seen 0.29-1.40, unseen -0.57-0.99). Cost nil (narrative and web within 0.005). Blind hand read of 144 replies to the reworded items: 0 pass, at every run. Before any run, the first cut of windows failed its own hand read, 14 of 50, and was replaced by a registered second cut that passed 31 of 50.

**Cost:** pre-registered at 9450650 (16:19 start on 2026-11-15), amendment at 4ba0ef9, mixes and configs at 9700852; card 12.0 s step 0, 5.9 s the one-step test, 16:36-16:59 for four runs and the read under one detached lock (23 min); window cuts and mixes on CPU in minutes; three hand reads (50, 50, 144) about 15 min. ETA said 2-3 h all in; it took about 45 min.

**The question** (owner, 2026-11-15: "Lets do it fully", after a three-agent
brainstorm he asked for -- "How can we get a model to understand words while
still generating text" -- and choosing 5M: "we haven't really gotten the
potential out of it"). Finding 238: the 260M reads and writes worst on the
same messages, those whose meaning is not in their words. A red-team read
found such turns almost absent from his conversation (9.07M SODA turns hold
"Never mind" alone 4 times). So: does a 5M that reads real exchanges around
those turns learn what the turn *does* -- reading reworded turns it never
saw -- or only a reply per wording? The pre-registration and its amendment
are `scripts/probe_markers.py`'s docstring.

## Step 0 -- the items, before anything was built

    swap share right, mean margin      seen half       unseen half      his line removed: seen / unseen
    corn_jr_260m (shipped)             0.75  3.46      0.64  2.45       0.69 4.48 / 0.78 3.65
    ten ordinary 5Ms                   0.47-0.69       0.39-0.64        (sd of mean margin 0.330 / 0.466)

Both gates passed (G1 at its line exactly, 27 of 36). Read beside and not
predicted: **the 260M reads the reworded turns better without his line in
front (0.78) than with it (0.64)** -- the situation he is shown pulls his
reading off the turn; per function the mean-margin gap is widest on `think` (0.78 with
the line against 2.75 without) and `dismiss` (2.80 against 5.18).

## The windows -- two cuts, the first failing

From the first 100 MB of OpenSubtitles (research-only), a window is the line
before a short turn, the turn, and the line after, framed as his line, the
person's turn, his reply. **W: 14 of 50** windows had the next line answering
the turn as another speaker -- a plain subtitle line does not say who speaks,
and mostly the turn's own speaker carries on (`markers__windows50_labels.txt`).
The arm as registered stopped there. The amendment, committed before a new
window was cut, kept only turns that open a two-speaker subtitle (a dash on
the turn and on the next line, first of the pair): **W2: 31 of 50**, past its
line of 30. That rule leaves 2,636 windows (`what` 1,000 of them under the
cap, `never mind` 57, `i guess` 43, `hm` 42), so 0.5% of the run reads each
window about nine times -- the amendment's "about twice" was miscounted from
bytes, and is corrected here, not there.

## The one-step test

One AdamW step on 64 marker windows against one on 64 plain ones, three
batches each, from the plain 5M: seen-half margin -0.607 against -0.674, so
**O passes on its letter** -- but both kinds of step moved every read the same
way (seen down about 0.65, unseen up about 0.50), and the difference between
them, 0.07, is a tenth of the shift they share. The local signal was there
only barely.

## The rows

    run                     seen: right  margin    unseen: right  margin    lm narrative  web
    marker windows  s1      0.64         1.04      0.61           0.77      0.4897        0.9527
    marker windows  s2      0.69         1.24      0.53          -0.07      0.4880        0.9535
    plain windows   s1      0.67         0.84      0.47          -0.09      0.4864        0.9480
    plain windows   s2      0.47         0.60      0.61           0.42      0.4884        0.9524

    U  unseen  gap +0.19 against 2 sd 0.93       does not hold
    K  seen    gap +0.42 against 2 sd 0.66       does not hold (both marker seeds above both plain, the size short)
    C  cost    narrative +0.003 / -0.000, web +0.005 / +0.001   holds
    H  blind hand read, 36 reworded items x 4 runs: 0 of 144 pass

**Prediction was wrong** on K: it said the seen wordings would move clearly
and the unseen would not. Neither moved past the band. **H is at the floor
and cannot rank the runs**: every 5M answers "What?", "I don't know", "No, I
don't think so", or turns to the situation's words ("I don't want to go
running") and ignores the short turn (`markers__blind_labels.txt`).

## What it licenses

**At 0.5% of a 5M run, real two-speaker exchanges around short turns teach
neither the wordings shown nor the reworded ones, past the spread of ordinary
runs; and a 5M writes no fitting reply to these turns in this frame at all.**
So the seen-against-unseen question -- lookup or inference -- is not answered
here: there was no lookup to compare against. Three things limit it, each
named rather than guessed past: the lesson is thin (2,636 windows, a third of
them `what`, the withdraw and hedge wordings in the tens) and only 31 of 50
are real replies; the dose is 0.5%; and the 5M band is wide on 36 pairs (sd
0.33 and 0.47). What would read it is more real two-speaker data -- the full
OpenSubtitles release, not on disk, is the owner's call -- or the size where
the signal exists: the 260M already reads these at 0.75 and 0.64, and his
line costing him 0.14 on the reworded half is the sharper question this
arm turned up.
