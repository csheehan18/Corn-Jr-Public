# His surprise flags unfamiliar names, not questions he cannot answer

**Full result:** On the plain 5M at both seeds, the surprise of the most surprising word in a question separates the unknowable questions of `probe_reply.py` from the answerable ones at AUC 0.67 -- 0.92 and 0.91 among the questions that name something, 0.47 and 0.46 among those that do not; the mean word reads 0.70 / 0.69, 0.90 / 0.86, 0.54 / 0.59. An invented name is the most surprising thing he reads (*Feruzza's* 36-40 nats, *Areskog's* 35); a question about the sender's own life is ordinary words (*How old is my grandmother?* 6.5-7.0, below *lie-in* at 21-24 in an answerable one). So a surprise input could at best teach him "unfamiliar name -> I don't know", the shortcut the knowing set was balanced against

**Cost:** writing `scripts/probe_question_surprise.py` and the read 11:52-11:56 on 2026-10-22, both checkpoints in seconds (card at 37%, contended, a bound). ETA 1 min of card, actual under 1.

**The question** (after finding 202). The surprise input (`corn/wordloop.py`)
gives him his own per-token surprise to read. It can only help him say he
does not know where his surprise on the question already differs between
what he can and cannot know. Read before a surprise-input arm trains, on
the 80 knowing questions of `scripts/probe_reply.py`, balanced 20 named / 20
plain and 10 / 10 on "my" in each set.

**Predicted** (stated before the run): the named half separates, the plain
half does not, overall near 0.75. It held, with the overall lower (0.67).

## The read

    score                    seed 1: all / named / plain    seed 2: all / named / plain
    most surprising word     0.67 / 0.92 / 0.47             0.67 / 0.91 / 0.46
    mean word                0.70 / 0.90 / 0.54             0.69 / 0.86 / 0.59

(AUC, unknowable over answerable; `evals/results/nano5m_base__questionsurprise.txt`)

## Read by hand

The five most surprising unknowable questions at each seed are all invented
names or words (*zarbleflax*, *Feruzza's*, *Areskog's*, *Brannoc*, *Odile's*); the
five least are all about the sender's own world (*How old is my grandmother?*, *What's
the name of my boss?*, *How many people live on my street?*) and read 5-7
nats -- under every one of the five least surprising answerable questions
at both seeds. The answerable questions' most surprising words are everyday words
he meets rarely (*lie-in*, *Halloween*, *cinema*), not anything unknowable.

## What it licenses

* **A surprise input alone will not teach him to say he cannot know.** Half
  of what he cannot know -- the sender's own life, the most common case for
  an assistant -- is invisible to his surprise; the half it sees is the name
  shortcut. The surprise-input arm is not worth its 25 minutes as a knowing
  arm.
* **Knowing he cannot know is understanding, not unfamiliarity**: that "my
  grandmother" is a person only the sender knows is meaning, and it has to
  come from text that shows it -- varied, real replies that decline about
  the asker's own life and about unfamiliar things alike, so neither the
  name nor "my" carries the answer.
* Finding 188 said the same of a shipped 260M: his surprise finds the
  unusual word, not the misunderstood one.

**What it does not settle.** Any size above 5M; whether a trained surprise
input would find a use for the signal elsewhere (coherence, rare words).
