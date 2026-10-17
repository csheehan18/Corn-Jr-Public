---
license: apache-2.0
language:
- en
pipeline_tag: text-generation
tags:
- assistant
- tool-use
- local
- privacy
- from-scratch
---

<!-- Release 0.5. This file becomes the Hugging Face model card (the HF
     repo's README.md). Every number below is quoted from a scorecard in
     `harness/results/` or `evals/results/` and every claim names the
     finding behind it -- docs/RELEASE.md's rule is that the card quotes
     measurements, it does not make claims. The scorecard run that most of
     the live numbers come from is 2026-09-07 at revision 0c48261c (the
     3d60c72c and ddc223f8 triples read the same on every row); when the
     numbers move, this card is re-run rather than re-worded. -->

# Corn-Jr

A 260M-parameter assistant trained **from scratch** — tokenizer, corpus,
weights, harness, everything — to run entirely on your own machine and route
what you ask into a small set of real tools: web search, phone calls, texts,
notes, date resolution, day recall, and a relay to a larger agent. He is not
a chat model with tools bolted on. The corpus was purpose-built around tool
transcripts, and the project's defining rule is that **he never fabricates
what an observation did not say**.

**Release 0.5 is text-only.** A voice client exists in `harness/voice/`
(push-to-talk, local Whisper in, local TTS out) and is deliberately not part
of this release: it has not been measured on the shipped checkpoint, and an
unmeasured half is not something to hand somebody on day one.

## Corn-Jr, in his own words

The runtime speaks these verbatim. Asked who he is, from `IDENTITY_REPLIES`
in `corn/agent.py`:

> *"I'm Corn-Jr, a small AI assistant that runs on this machine and gets
> things done by calling tools."*
>
> *"Corn-Jr. I'm a language model somebody trained from scratch, wired up to
> a handful of real tools."*
>
> *"Corn-Jr, at your service. Small model, your machine, real tools."*

Asked what he can do, he opens with a line like *"What I can actually go and
do:"* and then reads the **live tool registry** — composed fresh each turn
from the tools that process actually has, so it can never go stale or claim
a capability that is not wired up.

Asked about a life he does not have — how his weekend was, what he had for
lunch — he says so plainly (finding 125, `NO_LIFE_ROUTED_REPLIES`):

> *"That one's not a thing for me. I'm a model, not a person."*

**One line about his name, because it matters if you rename him.** The name
lives in `packs/persona.md` and the owner's name in `packs/about-me.md`.
With neither file present he is Corn-Jr and never says your name at all —
neither name is in the weights, and that is on purpose (`VISION` §4: the
shipped artefact is user-neutral, a running instance is one person's).

## What this actually is

- **260,613,120 parameters** — 20 layers, 1024 embed, 512 context, a custom
  8k BPE tokenizer (`bpe8k`) trained on the project's own corpus.
- Pretrained on **~5B tokens** of a purpose-built mix (`mix_v4_5b`):
  FineWeb-Edu web text, SODA-derived dialogue, Natural Questions-derived
  extraction, and generated tool-transcript slices from the repo's own
  generators.
- Shipped checkpoint: **`corn_jr_260m_v4_ft_social8`**, a fine-tune from
  `ft4g` that added the declared social turn at depth (finding 123 — a
  second social turn on a shared opening with one unrelated exchange in
  front of it). It ships paired with a reading adapter,
  `reader_whole_social8_s1.pt`, re-fit on this trunk (finding 124).
- Ships **with its harness**: a local server, a grammar-constrained decoder
  that holds tool arguments to copyable spans of your own words, a confirm
  gate on side-effectful actions, and a terminal client.

## What he can do — measured on the shipped revision

Run 2026-09-07 at revision `0c48261c` on stock defaults (the `3d60c72c` and
2026-09-06 `ddc223f8` triples read the same on every row). Reproduce with
the two commands in [RELEASE.md](RELEASE.md), which also says exactly what
that server was and was not.

| behaviour | read |
|---|---|
| nineteen hand-written asks, right tool called (`checkup`) | **16/19** |
| every call that was made, ran | **14/14** |
| read the observation back rather than inventing | **9/9** |
| tool selection over a declared list (`tool.selection`) | **196/200** |
| tools he was **never trained on**, routed by declaration alone (grid A) | **23/24** novel, **170/176** trained |
| telephony routed (grid B) | **390/400**, contact kept verbatim 388/390, message 171/173 |
| notes routed (grid C) | **169/176**, note text kept verbatim 142/169 |
| copy fidelity — arguments are spans of what you said | **120/120** narrow, **300/300** wide |
| date expressions resolved through the observation | **353/353**, routing 398/400 |
| a follow-up gets a fresh answer, not the last one again (`converse`) | **10/10** |
| the reply answers the kind of turn it was | **14/16** |
| a cell read out of your own CSV pack | **252/252** |

808 toolgrid turns ran without a single one being answered by a runtime
hatch — every rate above is the model, with one deliberate exception. **The
last row is not the model at all, and that is the design.** A question about a
row of one of your CSV packs is resolved in code — the row matched by name,
the column by its own words then by a synonym tier — and the sentence composed
from the cell, so there is nothing for a 260M model to get wrong. Measured
over every row × every column × four question forms of the shipped example
pack: 252 of 252. A question the matcher cannot resolve gets a clarify that
names the columns ("Which one — Type, HP, Attack…?") rather than a guess.

The frozen `packs.cell` (16/72) and `packs.column` (13/88) rows in the eval
set measure something else: the model reading a *rendered row* through plain
generation, which is the fallback the runtime reaches only when the code
matcher has already failed. On the shipped pack, across those 252 questions,
it never fired.

## What he cannot do — from the findings, not from modesty

- **The first turn of a conversation routes far worse than the second, and
  the fix is a runtime patch rather than a cure.** The corpus puts a tool
  call after every second `<|user|>` and teaches the first turn nothing, so
  on an empty history "note down buy milk" declined. Measured across 3,644
  turns: notes 177/1000, texts 84/648, calls 32/174 on an empty history
  against 702, 352 and 132 after any tool turn. **A seeded first turn ships
  on by default** and reproduces the after-tool column to the cell. What it
  does not buy: nine held-out and novel note phrasings stay at zero, "text
  {contact} {message}" stays at 6/36, and a trailing full stop still halves
  calls.
- **He calls and texts only you** (runtime change, 2026-10-13, after the
  numbers on this card were read). A request for anyone else is refused with
  an offer to text you a reminder — "I can't message Sam -- only you. Shall I
  text you a reminder to let them know?" — and nothing leaves the machine for
  them. The weights still write the name they heard into the call, and on
  "Text Carla Mendez I'm running late" that slot can swallow the message;
  the refusal sheds it, so it names Carla Mendez and not the sentence.
- **Out-of-scope requests are refused, but often by serving the refusal
  rather than holding it back** — `chat.abstain_oos` reads 12/100, and
  `checkup`'s `held_back` 2/5.
- **Extraction is real and is not a search engine.** Through the shipped
  reading adapter on Population A: **517 of 721 answerable passages right at
  197 of 282 correct silences**, at ~23 ms a passage (finding 124, finding
  117). The generate path on the same population reads 230 right at 256
  silences — so the adapter trades some silence for many more answers, and
  that is the trade you are getting.
- **Multi-turn is on, the window keeps about four turns, and he uses one.**
  The transcript carries across turns by default. The context is 512
  tokens; with the shipped reserve and history fold (`--budget 120
  --fold-history`, defaults since 2026-09-07) the trimmer holds the last
  four tool turns every time and six chat turns, where the earlier
  defaults held one tool turn. Nothing reissues a previous query or user
  line at depth 1 or 3 (0/36 and 0/72). But the multi-turn shape is ~0.34%
  of the training mix, a pronoun chain across turns reads 34/50
  (`turn2.chain_pronoun`), and a follow-up composes off the turn
  immediately before it or not at all — a lookup, one turn of anything
  else, then "what about spain?" composes 0 of 5 whichever settings keep
  the lookup in the window. Say the whole question.
- **He is not a companion, and the arm that tried to make him one failed.**
  Asked for a joke, a preference, an opinion, or handed a compliment, an
  insult or affection, he answers 10 of 78 acceptably: he engages, and then
  does not hand the conversation back. Arm 11 wrote 144 lines for exactly
  this and moved the row not at all — what answers instead is the
  pretraining prior, where "I love you" is answered by a person who loves
  you back (PLAN-PERSONALITY, the twelfth section). A consolation family
  does exist and reads 13/28.
- **He does not know who he is without the file.** Asked his name, the
  weights say somebody else's; the runtime answers from the identity pool
  instead. Four training arms failed to put the name in the weights
  (PLAN-PERSONALITY, arms 9 through 9h4), and the honest reading is that a
  260M model pretrained on 20% dialogue has a prior about "who are you" that
  a fine-tune does not outvote.
- **Live search routes far better than it answers.** Routing is at
  ceiling (`searchgrid` 400/400 routed, 400/400 kept the subject), but what
  comes back from the web is a lead sentence or a reader's span, and on a
  full 2026-09-06 sitting that meant "It's Apollo 11." for *when* the first
  moon landing was, "William Faulkner" for who wrote Hamlet, and "c" for
  the speed of light. Wikipedia's abstract is the first provider, and the
  answer is only as good as the abstract. Wikipedia also rate-limits after
  a burst of queries — a few hundred in minutes — and he then says
  "Wikipedia's blocking my searches right now" until it lifts.
- **Follow-ups that need the last answer are answered from the weights.**
  "Who is the president of France" then "how old is he?" gets "He's 18"
  with no tool called; "what about pikachu?" composes a fresh lookup but
  "and how fast is it?" does not. The chain rows (`chaingrid`) read 0 of 8
  composed at depth 2 and 3 on both carriers. Ask the whole question.
- **The calendar is read by code, not by the model, and it reads ahead
  as well as back.** "Last Wednesday", "three days ago" and "the 14th"
  resolve, and since 2026-09-07 so do "30 days from now", "in two weeks",
  "the 25th of December", "Christmas", "Easter", "Thanksgiving" and "two
  weeks after Christmas". "How many days till Christmas" is answered with
  the count and the date; "how many days till my birthday" reads the
  `birthday:` line in `packs/about-me.md` and tells you where to put one if
  it is missing. What it still does not do is a range ahead ("next month",
  "later this week"), and it says so instead of asking you to repeat the
  date.
- **A `tools.d` tool is reached by its summary, not by magic.** Grid A shows
  him routing to declared tools he never trained on at 22/24 — but on their
  own carriers. "List my notes" was saved as a note and "echo hello" was
  answered as chat on the shipped examples. Write the summary the way you
  will ask for it, and test it in the studio's tools tab.
- **No reminders, no message reading, no calendar.** He will tell you so.

## Hardware and latency

Developed and measured on a single **RTX 3080-class card (10 GB)**. Full
fp32 weights fit with room for a fine-tune; the model loads in **3.7 s**,
which a resident server pays once and a per-turn process would pay every
turn.

On the shipped revision, `VISION` §3 budgets the whole round trip at 500 ms
and the measured turn is **median 172 ms, p90 351 ms, max 401 ms**. A turn
that is only speech is 54 ms; a turn with a tool in it, 190 ms. Date and
recall turns come back in 1–6 ms because the runtime answers them without a
decode. Reading a whole passage costs ~23 ms.

A full fine-tune of the model is ~25 minutes (1,200 iterations at batch 8 ×
grad-accum 6 × block 512, `compile=True`). **One warning from experience:**
at 10 GB, another application holding a couple of gigabytes of video memory
will push a training run into host-memory fallback, where it slows by an
order of magnitude and can stop returning altogether. Give training the card.

**CPU-only is untested.** The latency numbers the client prints per turn
will tell you immediately what you are in for.

## Privacy

Everything runs locally, and **`--search` is the single flag that sends
anything off your machine** — it is opt-in, it says so when enabled, and
without it `web_search` answers from a table baked into the corpus. A
privacy backstop refuses to forward questions that are about *your own
records* ("what did I note down", "what's my name", "read me my texts")
even when search is on; those are answered from your local files or not at
all. The backstop reads both the query he wrote **and the line you typed**
— since 2026-09-07, because on a seeded first turn the query that left was
sometimes the seed's own "what day is it" while the private question sat
in your line — and a query built out of words nobody said is re-decoded
without the seed or replaced by your own line before it goes anywhere. Your notes,
people, schedule, packs and conversation logs are plain files in your own
folder, gitignored from birth and never in the weights. Personalisation
lives in those editable local stores by design, so a shipped update never
carries anyone's name and an upgrade is a checkpoint swap rather than a
migration.

## The runtime answers some turns itself, and here is exactly which

A small set of turns never reaches the model. This is disclosed rather than
hidden because you would otherwise credit the model for them:

- **the identity hatch** — who are you, are you an AI, are you a person, are
  you some other assistant, and questions about a life he does not have
  (35 phrasings plus 31 life carriers, finding 125);
- **the social hatch** — greetings, wellbeing, thanks, farewells,
  acknowledgements and a stated low mood, answered from hand-written pools;
- **the temporal hatch** — "what day is it", "what time is it" and date
  recall, answered without a decode (the clock is the machine's own; before
  2026-09-07 "what time is it" went to the web and came back "It's 1989.");
- **the store hatch** — 37 phrasings of "what do you know about me", routed
  to your own local store rather than trusted to the weights;
- **the confirm gate** — the yes/no on a call or a text;
- **the seed turn** — one hatched date turn the runtime runs itself at start
  and at every reset, so no conversation opens on an empty history.

**Every turn in the session log carries an `author` field** saying whether
the model or the runtime wrote it, and where a pool covered for him it also
records the draft he would have said. You can audit exactly how often the
net catches him.

## ⚠️ The warning that goes in bold

**The server has no authentication and it executes tools.** Binding `--host`
beyond 127.0.0.1 is a decision, not a default. The confirmation gates
protect you against the model; they do not protect you against the network.

## Versioning and upgrades

A release is **weights + harness at a matched pair of versions** (`info`
reports both halves, and every scorecard is stamped with the git revision it
was read on). Your personal files -- notes, packs (the people table among them), the
schedule, transcripts -- live outside the model in plain JSON, JSON Lines and
text, so an upgrade is a checkpoint swap and nothing of yours is inside the
thing being swapped. They do not yet carry a format version of their own:
`server.json` is checked key by key and refuses an unknown one loudly, but a
future harness meeting an older notes file would read what it recognises
rather than stop. Expect new tags as training runs survive their regression
gates, with this card's numbers re-run each time rather than re-worded.

## Licence and attribution

Weights and code: **Apache 2.0.**

Training data attribution: **FineWeb-Edu** (ODC-By 1.0; use of Common
Crawl-derived data is subject to Common Crawl's terms of use), **SODA**
(CC BY 4.0), **Natural Questions** (CC BY-SA 3.0 Unported). Every generated
slice was produced by this repository's own generators. The weights are
licensed under the common position that model weights are not an adaptation
of training text; full attribution is given here regardless.

## The findings are the real documentation

`docs/findings/` carries a numbered finding for every capability and every
defect named above, each with the measurement behind it. That is the part of
this box nobody else has, and the audience that reads it is larger than the
audience that runs him.
