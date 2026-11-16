# More words fixed most misses; an unseen 'unless' word still reads 'if'

**Full result:** With the word lists widened and a backward cut for a parenthetical condition, three of five gates pass at all three starts -- structures 0.986-0.995 (the parenthetical cells 140 of 144), held cells 0.979-1.000, finding 180's rows 0.988-0.995 -- and two miss at all three on one kind of word: an unseen unless-word is read as a plain "if" ("aside from if" 8 / 10 / 56 of 96, while an unseen if-word, else-word, default and switch verb read 90-96), and the hand-written probe reads 46 / 41 / 34 of 58 against 48

**Cost:** three fine-tunes of 650 iterations at 20M (157, 143, 144 s, contended -- the card at 36-38%, a bound), two span reads a run (145-147 s and 167-169 s), slot reads and copy cards at 7-9 s, the real-wording probe: one chain of 1,466.4 s, 12:10-12:34 on 2026-10-20, registered ~22 min; the zero-training control 525 s; the build 11:46-12:09 on CPU.

**The owner's go, 2026-10-20**: "let's do 1 and 2 together" -- finding 182's
two misses at once. Finding 182 put the condition's clause first (`cond:`,
then `if: [not ]v -> X`) and composed structures installed and transferred;
what missed was words the lists lacked and a parenthetical condition the cut
rule ran forward. Two changes, read on separate columns
(`corn/branchwidegen.py`, pre-registered at d4ad2e5 in
`configs/mix_v3_bind_ft_wide.py`):

1. **every word list widened**, `branchstructgen`'s extended and never edited
   -- unless-words 2 to 9 ("but not if" among them), if-words 5 to 10,
   else-words 5 to 11, defaults, switch verbs, negations, and a word between
   the condition word and "it" ("unless perhaps it's v") -- with one word a
   slot held out (`HELD_WORDS`);
2. **the parenthetical order** ("A, unless it's v, in which case B") and a
   cut rule that runs a condition clause holding no continuation **back**
   when the next clause opens on an else-word or an in-which-case word.

Everything else is finding 182's: the format, the starts, the recipe, the
weight (1.86 passes against 1.88). `check_branch.py` section 18 holds it.

## The registered read

The decision -- the continuation his `if:` line implies, which the runtime
acts on (`probe_branch_span.py`):

    start  struct (gate 0.94;   held cells    held words (0.85;   180's rows   far probe
           XPY 0.90)            (0.90)        "aside" 0.75)       (0.97)       (48 of 58)
    ev2    856/864, XPY 140/144  480/480       388/480, 8/96      1,708 0.988    46
    ev2s2  860/864, XPY 140/144  478/480       390/480, 10/96     1,720 0.995    41
    ev2s3  852/864, XPY 140/144  480/480       432/480, 56/96     1,714 0.992    34

    control, finding 182's runs on the same rows (zero training):
           non-XPY 512-522/720,  284-338/480   276-316/480,       1,648-1,664    37-38
           XPY 44-80/144                       12-22/96

**Installs, transfers and the old eight pass at all three starts**; own
quads 212-214 of 216 on the structure rows, 119-120 of 120 held, 139-144 of
144 on each of finding 180's cells. **Held words and the far probe miss at
all three.** The pick half holds: every gold-line quad right on every row
set. On his training traces the `if:` line's continuation reads 1.00 in every
family. The prediction was right on the three structure gates, wrong on
held words (2 of 3 predicted, 0 of 3) and on the far probe (1 of 3, 0 of 3).

## The held words, one at a time

    held word              ev2      ev2s2    ev2s3    (of 96)
    "supposing"            96       94       90       an if-word
    "or otherwise"         96       96       96       an else-word
    "as my first choice"   96       96       96       a default
    "opt for"              92       94       94       a switch verb
    "aside from if"         8       10       56       an unless-word

**Every held word transfers but the unless-word.** On "aside from if" his
clause is exact and his `if:` line has no "not" -- the unseen negative word
read as the "if" it ends in. Six trained unless-words of the same build
("apart from if", "other than if", "except for if", "excepting if") did not
make a seventh one readable: nine words were learned as a list. The
asymmetry is the finding: **an unseen condition word is read as a plain
condition** -- which is right for every if-word and wrong for every
unless-word.

## The far probe, by shape

Pooled over the three starts (6 a shape), against finding 182:

* **The parentheticals** (part 2, pre-registered): "A, unless of course it's
  v, in which case B" **1 to 6**; "A, but only if it's not v -- else B" 0 to
  0. On the second he cuts `but only if it's not snowing -- else B` and
  writes `if: not snowing -> B` -- forward through the else-word. The
  generator's parenthetical never opens on "but"; its default-then-switch
  order does ("Y, but if v, X", forward), and the "but" won over the
  else-word after it.
* **Connectives no list holds** (part 1): "anything but" 1 to 4, "is the
  backup" 1 to 3, "then definitely ... but if it's not then" 0 to 1, "save
  for if" 0 to 0 (the clause exact, no "not" -- the unless-word again), "in
  the event that" 1 to 0 (he cuts "A by default", reading no condition in
  the clause that holds one). Pre-registered: 3+ on three of five; two.
* **The third start's negation column**, 8 of 20 against 18 and 17: on "if
  it doesn't turn out to be foggy, A; otherwise B" (both "doesn't" and "turns
  out" kept out of every list) his clause is exact and his line has no "not".
  The same kind of miss at one start in three.
* "go with B, though if it's v make it A" fell 3 to 0 -- he cuts the default
  clause, once writing "otherwise" into his clause where the request has
  "though".

## The copy row, a side column

`tool.copy_wide` 295, 283, 292 against the starts' 298, 295, 293 -- not
readable by finding 170's rule; the second start low again, in a fourth arm.

## What it licenses

* **The structure layer is done for branch at nano by fine-tune**: composed
  structures, the parenthetical with its backward cut, and finding 180's
  eight all read at 0.97-1.00 at three starts of three, and the structural
  held cells at 0.98-1.00.
* **Widening a word list transfers to unseen words of the same role -- except
  where the role is a negation the word itself must carry.** An unseen
  if-word, else-word, default or switch verb is read; an unseen unless-word
  (or "doesn't", at one start) is read as positive, because that is what an
  unknown condition word defaults to. Nine unless-words did not teach
  "unless" as a meaning.
* **For the 1.0 branch slice**: the negative markers need coverage, not a
  sample -- the unless-words and negations people use, mined from real text,
  in the dozens; or the polarity is checked against the request by the
  runtime. Which is the owner's.

**What it does not settle.** Whether real-text unless-words in the dozens
teach the meaning or only a longer list; a "but"-led parenthetical; the
third start's "doesn't"; pretraining at one pass in this form; and the
second start's copy species.
