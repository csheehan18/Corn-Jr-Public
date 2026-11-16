# Real everyday dialogue fits the owner's messages best; Reddit worst

**Full result:** Of four conversational sources read on CPU, EmpatheticDialogues talks most like the 148 everyday messages of the reply read: a word-bigram model fitted on a million words of each source's messages scores those messages at perplexity 142, against 180 for SODA (what the mix reads now), 288 for OpenSubtitles and 359 for PEC (Reddit r/happy and r/offmychest) -- and it is twice as varied as SODA on its own held-out messages (171 against 86; SODA is the most formulaic of the four). By hand it reads as real people texting about their day ("Oh man I hate when that happens...did you dry it off or change to a new pair?"). PEC is long, confessional, often off-thread, carries slurs, and was lowercased and tokenised by its authors, so it is unusable as text; subtitle lines that follow each other are rarely a message and its reply. EmpatheticDialogues is small (17,844 training dialogues, 1.26M words) and CC BY-NC 4.0

**Cost:** licence and source search, downloads (28 MB, 252 MB and a 100 MB prefix of 3.7 GB, to `F:/corn-jr-data/convcand/`), `scripts/probe_conv_sources.py` and the hand read of 80 pairs, 15:15-15:30 on 2026-10-22. No card. ETA 45 min, actual ~25.

**The question** (owner, 2026-10-22: avoid SODA's style; find a source in his
register). Finding 209: the 5M finds the owner-register messages far more
surprising than its own openers, and the conversation it learns from is
scripted, name-heavy SODA.

## The read (`evals/results/conv_sources__read.txt`)

    source    pairs        median words   <=4 words   question   first person   ppl owner   ppl own
    soda      408,399      16             0.03        0.31       0.66           180         86
    ed        58,829       14             0.04        0.21       0.66           142         171
    pec       378,139      26             0.03        0.12       0.77           359         206
    subs      11,660,725   6              0.35        0.18       0.26           288         197
    owner     148          8              0.11        0.32       0.61           --          --

(*ppl owner*: add-0.1 bigram over lowercased words, fitted on 1M words of
the source's messages, on the 148 messages; *ppl own*: the same model on
148 of the source's held-out messages -- how predictable the source is to
itself. Lowercased so PEC compares fairly.)

## Read by hand (20 pairs a source)

* **EmpatheticDialogues**: first-person everyday moments -- a drink spilled
  before work, a baby's shots, waiting for a friend at the airport -- and
  replies that answer them with a follow-up ("Where are you going?", "How
  nice! Are you going out or are you going to have a nice night in?").
  Typos, lowercase, "haha"; real crowdworkers, not a model. Some heavy
  topics (a partner's affair).
* **SODA**: polished and earnest ("I'm just concentrating on staying calm
  and relaxed. It's helping me to stay focused"), set roles (professor,
  fortune teller), names in the lines.
* **PEC**: casual Reddit, but posts run long, replies drift off the post,
  and it carries slurs and politics; lowercased and tokenised ("i 'm",
  "do n't") beyond repair.
* **OpenSubtitles**: the only source rich in short lines (35% four words or
  fewer), but consecutive lines are usually one speaker or a cut ("It'll
  give 'em a little scare." -> "I am Father."); without speaker turns it is
  not conversation.

## What it licenses

* **EmpatheticDialogues is the first candidate for the owner's register**,
  as a share beside SODA, not in place of it: ~1.7M tokens against SODA's
  19.5M in the mix. Its licence is non-commercial; the owner does not plan
  to monetise Corn-Jr (2026-10-22), and RELEASE must list it with its
  terms if it enters the corpus.
* **Pass on Reddit as read here** (PEC; other subreddits through the raw
  dumps are untested, and nothing here argues for chasing them) **and on
  subtitles as conversation**.
* **The target itself is a stand-in**: the 148 messages are written in the
  owner's register by the assistant, not by him. A sharper read needs
  messages the owner writes himself.

**DCLM, read beside (owner question, 2026-10-22).** The same bigram read on
1M words of sentences (3-40 words) from the DCLM shards on disk (finding
190's): ppl owner 606, ppl own 2,075; median 14 words, 0.06 with a question
mark, 0.16 first person. Web pages -- install notes, product descriptions,
fan fiction -- the furthest of any source from the owner's register; a
knowledge-side source (where finding 190 found it adds nothing measurable),
not a conversational one.

**The owner's own messages, counts only (2026-10-22).** The owner offered his
sessions; under his counts-only rule (2026-10-09) `scripts/probe_owner_register.py`
reads the typed `> ` lines of `Saved Sessions/*.txt` and prints only totals --
no message was read or written. 69 unique messages: median 6 words, 0.38 four
words or fewer, 0.38 with a question mark, **0.06 first person** -- against the
stand-in set's 8, 0.11, 0.32 and 0.61. He writes to Corn-Jr as to an
assistant, short questions and requests, not personal news; the 148 stand-ins
over-represent the latter. Bigram perplexity of his messages: ED 718, SODA
938, subtitles 954, PEC 1,099, DCLM 1,386 -- no source fits closely, ED
still best. Sixty-nine messages from sessions that were largely testing him;
a bound, not a portrait.

**What it does not settle.** Whether an EmpatheticDialogues share moves the
reply read (a 5M arm); other real sources; the owner's own register.
