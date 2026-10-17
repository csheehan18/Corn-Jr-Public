# Corn-Jr — Vision

**Doc-status:** reference — what Corn-Jr is trying to be, and why

**Status:** Draft v0.1 — under active discussion. Nothing here is settled.
**Last updated:** 2026-08-20

---

## 1. What Corn-Jr is

Corn-Jr is a small personal AI assistant — roughly 250M parameters — pretrained from
scratch, designed to be held in a real-time voice conversation and to act on the world
through a large library of tools.

He is not trying to be smart. He is trying to be *fast*, *reliable at calling things*, and
*present*. The intended experience is being on a phone call with someone who knows where
everything is and can go get it immediately — not consulting an oracle.

Two goals run in parallel and are equally weighted:

1. **Learning.** Building the whole stack from scratch — tokenizer, architecture, pretraining,
   fine-tuning, inference, tool layer, memory — is the point. Shortcuts that skip the
   education are not shortcuts.
2. **Functionality.** It has to actually be good enough to use daily. A research artifact
   that never gets used has failed.

---

## 2. The core bet

> **250M parameters cannot store the world, so don't try.**
> Spend the parameters on *procedure* — routing, argument construction, composing calls,
> knowing when it doesn't know. Push *content* out into tools and memory.
> Knowledge is retrieved, never memorized.

And the corollary that makes it work:

> **Speed is a thinking budget, not an output budget.**
> Speech consumes ~3–4 tokens/sec. At 250 tok/s, Corn-Jr runs ~70x faster than the
> conversation requires. That surplus is spent on *internal iteration* — plan, call, inspect,
> revise, retry — inside the same pause where a larger model gets one shot.
> Five cheap passes beat one expensive one at assistant work.

If this bet is right, "not smart on paper" stops being a compromise and becomes the design
constraint every other decision follows from.

---

## 3. The top-level constraint: the latency budget

Not parameter count. Not benchmark scores. **Round-trip conversational latency.**

Target: **< 500ms** from the moment you stop speaking to the moment audio starts coming back.
Human conversational turn-gaps average ~200ms; past ~800ms it stops feeling like a
conversation and starts feeling like a query.

Rough budget, and note where the time actually goes:

| Stage | Budget | Notes |
|---|---|---|
| Endpointing / VAD | 50–150ms | Deciding you're *done* talking. Sneakily the hardest part. |
| STT finalization | 50–100ms | Streaming, so most work is already done by end-of-speech. |
| Network (LAN → 3080) | 5–30ms | Cheap on LAN, real cost over the internet. |
| LLM prefill + decode | 30–100ms | **The smallest slice.** This is the point. |
| Tool call(s) | 0–200ms | Highly variable. Local tools must be fast; slow tools need a spoken ack. |
| TTS to first audio | 50–150ms | Streaming TTS; first chunk is what matters, not the full utterance. |

**The LLM is not the bottleneck.** Endpointing and TTS are. Any work on model speed past
"comfortably fast enough" is wasted effort compared to work on the audio pipeline.

---

## 4. Deployment shape

**Corn-Jr is single-user by design.** One instance serves one person, always. The way other
people get to use it is that they are **given a fully trained and tuned Corn-Jr and host their
own**, on their own hardware, with their own data — not that one deployment learns to serve
several people.

This was written down once as "multi-user", which was the wrong word for it and pointed the
design somewhere it should not go. The distinction that matters:

| | what must be true |
|---|---|
| **the shipped artefact** | user-neutral. It goes to more than one person, so no personal facts belong in the weights or the pretraining corpus. |
| **a running instance** | one user's, permanently. It may specialise to them however it likes, because nobody else is downstream of it. |

**What that unblocks.** Per-user adaptation of a *hosted instance* — style adapters, a learned
lexical prior, anything trained on that person's own conversations — is a live option rather
than a ruled-out one, because there is no second user in that instance to leak into and no
shared index to keep consistent. The earlier note read as forbidding it; it was only ever
forbidding personal facts in the artefact everyone receives.

**What it does not change.** §7's non-goal stands: no open-domain world knowledge in the
weights. So does §5.2's `forget_day` / `dont_log_this` requirement — content a user can ask to
have forgotten has to live somewhere deletable, which means the tool-side store, not a
gradient. Adapting *how he speaks* is not the same as storing *what he knows*, and only the
second is forbidden.

**What it costs.** Every instance diverges from the moment it is handed over, so there is no
single "current Corn-Jr" to reason about once friends are hosting their own. Upgrades become
a migration problem — a new base model plus whatever that instance had learned on top — and
that is a reason to keep personalisation in a separable layer (adapter, prior, store) rather
than folded into the base weights.

- **Inference runs on a home server** — the RTX 3080 (10GB). Clients are thin.
- **Desktop app first**, mobile later. Desktop is where iteration is fast; mobile is where
  the car and the voice-call use case eventually live.
- **Voice is the primary interface**, with a screen as secondary. Text/CLI exists for
  development and debugging.

Feasibility check on the 3080: 250M params at fp16 is ~500MB of weights. Single-stream decode
is memory-bandwidth-bound, and the 3080 has ~760 GB/s — theoretically ~1500 tok/s. The 250
tok/s target has roughly 6x headroom. **Inference speed is not at risk.** Quantization is an
optimization, not a requirement.

Known tension: the 3080 cannot serve inference and run a multi-week pretrain simultaneously.
These are sequential phases. This is the most likely reason to rent cloud compute.

---

## 5. Memory — the research thread

Memory is load-bearing, not a feature. If knowledge lives outside the parameters, the memory
system *is* where the intelligence lives. Four layers, pursued in order — the first three are
application-level and sit outside the model; the fourth is inside it:

### 5.1 Facts and retrieval (first)

Memory *around* the model, exposed to it as tools it calls.

- Persistent facts about the user — stable, editable, small enough to stay in context.
- Retrieval over the user's own files and notes.
- Explicit write/read/forget operations the model invokes deliberately, rather than an
  invisible layer that silently mutates context.

Lower risk, immediately useful, and it's where "personal assistant" lives or dies. It also
doubles as a strong test of the tool-calling thesis: if memory-as-a-tool works well, the
whole architecture is validated.

**The read half of this layer now exists, and that changes its cost — added 2026-08-26.**
The extraction chain (finding 65: windows → reduce → grounded, installed by fine-tune,
`World.reader` as the seam) is source-agnostic: the same machinery that reads a search
passage reads a text the user hands him, a note, or a compacted day summary. So this layer
stops being a research bet and becomes two tools and a backend: `search_notes` — the
relevance query path §5.2 already plans beside date lookup — and a document source for
text the user uploads. Rules, written before any of it is built:

- **Local by construction.** Reading the user's own store never leaves the machine; there
  is no `--search`-style opt-in here because there is nothing to opt into.
- **Abstention is the right failure.** Extraction's over-decline (40% on answerable, the
  binding constraint elsewhere) is the correct temperament over personal data — a wrong
  personal fact is worse than a declined one, and `grounded` is mandatory on this path.
- **Nothing trains on the store.** The reader reads at inference; the gradient never sees
  personal content, which is what keeps §5.2's `forget_day` an actual deletion.
- **Finding 66 bites hardest here.** A day log is the paired-clause danger zone — two
  dates in one entry under different labels — so the paired-property row is this
  feature's regression row, not an optional one.
- **It does not hold the `mix_v4_5b` freeze.** New tools route by fine-tune (finding 63),
  so this arrives as declaration plus fine-tune on whatever base exists, the same
  sequencing rule as the scheduled pipe.

### 5.2 Day-context memory — the signature idea

**Corn-Jr keeps a log of days, indexed by date, and can look any day up.**

The observation behind it: LLMs are temporally unmoored. They don't know what day it is,
can't reason about "last Tuesday," and have no sense of elapsed time between conversations.
A day-indexed memory with a real clock attached fixes this for almost nothing.

**Why this fits Corn-Jr specifically.** Temporal reasoning is arithmetic, and 250M models are
bad at arithmetic. The model must *never* compute dates. Instead:

```
resolve_date("17 days ago")  ->  2026-07-21
recall_day("2026-07-21")     ->  <that day's log>
```

The model routes; the tool does the math. This is the core bet (§2) applied a second time —
and it means Corn-Jr can have *better* temporal grounding than a frontier model, because
frontier models try to reason it out and he just looks it up.

**Why it's cheap.** A day's summary is a few hundred tokens. A year is well under 200k
tokens — searchable in milliseconds, storable forever. Cost is not a design consideration
here, which is unusual and worth exploiting.

**Proposed structure — hierarchical decay.** Recent days stay detailed, older days compact:

| Age | Retained as |
|---|---|
| Today | Live, full detail, timestamped events |
| Past week | Full day logs |
| Past year | Compacted day summaries |
| Older | Week and month rollups, with notable days kept whole |

This mirrors human memory, keeps the store flat-cost indefinitely, and gives the compaction
step somewhere useful to live.

**Prior art, honestly.** The nearest neighbor is the Stanford *Generative Agents* memory
stream — timestamped observations with recency/relevance retrieval and periodic reflection.
Shipped assistant memory (ChatGPT, Claude) is genuinely not this: it stores facts stripped of
when they happened. The unexplored part is **day as the primary index unit, used deliberately
to ground temporal reasoning in a model too small to do it natively** — and drilling that
behavior in during fine-tuning rather than bolting it on at the prompt layer.

**Scope of capture — decided.** Corn-Jr logs **only what happens when you interact with him.**
Not ambient capture, not an always-on microphone writing down your life. The day log is a
record of what you talked about, what you asked for, and what he did — plus whatever you
explicitly tell him to remember.

This means his picture of a day is honestly incomplete, and that's correct: he knows what you
told him and what he did, not what you were doing while he was idle.

**User control is a first-class feature, built early, not retrofitted:**
- `forget_day(date)` — drop a day entirely.
- `dont_log_this` — mark the current exchange as unrecorded.

Both must be reachable by voice mid-conversation. A log you can't reach into and delete from
is one you stop trusting, and a memory you don't trust is worse than none.

**Proposed mechanics** (to be validated in build):
- **Append live, compact nightly.** Timestamped events written as they happen; an end-of-day
  pass compacts them into the day record. Splits cheap-and-dumb from expensive-and-smart at
  the right seam.
- **Today's log stays in context permanently.** It's a few hundred tokens, and it means
  "what did I just ask you?" never costs a tool call.
- **Two query paths, not one overloaded tool.** Date-based lookup (via `resolve_date`) and
  relevance search over compacted summaries. Different questions — a small model will route
  between two clear tools more reliably than into one ambiguous one.

### 5.3 Speaker identity — the second index (proposed)

**A day log answers "when." A person index answers "who." Corn-Jr should have both.**

On a voice call there is often more than one voice. Someone else is in the car, the call is on
speaker, a friend leans in and says something. Today all of that collapses into one
undifferentiated transcript, and the day log records it as though the user said it. That is
both a lost capability and a correctness bug — memory attributed to the wrong person is worse
than memory not kept at all.

The proposal: the audio pipeline tags every transcript segment with a speaker label, and the
memory store gains **person** as a first-class index alongside date.

```
who_is_here()                ->  ["owner", "dad", "unknown_2"]
recall_person("dad")         ->  <person record + recent interactions>
recall_day("2026-07-21", speaker="dad")  ->  <just his segments>
```

**Why it fits the core bet.** Identifying a voice is perception, not reasoning — exactly the
kind of work §2 says to push out of the parameters. The model never does the matching. A
speaker-embedding model (ECAPA-TDNN, titanet, WeSpeaker — all in the 5–20M parameter range)
produces a vector per speech segment; a cosine match against a small enrollment table produces
a name; the label arrives in context as just another field. This is `resolve_date` again: the
tool does the hard thing, the model routes. And as with dates, it means Corn-Jr can be *better*
at this than a frontier model, which typically gets a flat transcript with no idea who is
talking.

**Why it does not break §4.** Single-user by design still holds, and the distinction is worth
being precise about:

| | |
|---|---|
| **user** | exactly one, permanently. Owns the instance, owns the memory store, is who Corn-Jr answers to. |
| **speakers** | many. People the user talks with, near, or about. They are *entries in the user's memory*, not accounts. |

A person record is the user's note about someone else — a contact with history attached. There
is no second store, no second permission model, nothing to keep consistent across users. §4 is
untouched.

**Speaker identity is context, never authorization.** This is the rule that has to be written
down before any of it gets built. A voice can be recorded, imitated, or played back, and the
match is probabilistic even when nobody is trying. So a speaker label may inform *what Corn-Jr
says*, and must never gate *what Corn-Jr does*. Anything consequential — sending a message,
placing a call, spending anything, writing or deleting memory — stays on the owner's authority
regardless of which voice asked. An unrecognized voice is a guest, not a fallback owner.

**Data shape.**

- **Person record:** stable ID, display name, relationship, one or more voiceprint centroids
  (a person may need separate ones per channel — see failure modes), freeform facts, and a
  pointer into the day log.
- **Day log entries** gain a `speakers: [...]` field. Day × person becomes a two-axis index,
  which is where the interesting queries live: "what did Sarah say about the trip," "when did I
  last talk to Mike," "who was with me last Thursday."

**Enrollment is never silent.** Two paths, both explicit:

1. **Named on the spot.** "Corn, this is my brother Mike" binds the current speaker's embedding
   to a new person record.
2. **Deferred and offered.** An unrecognized voice gets a provisional session-scoped label
   (`unknown_2`) and is raised afterward — "there was another voice earlier, who was that?" The
   user names it or drops it. Dropping it discards the embedding.

A name appearing in the transcript ("thanks, Mike") is a *suggestion* to confirm, never a
binding. Corn-Jr does not build a voiceprint for anyone the user has not named.

**Deletion parity with §5.2, and then some.** Voiceprints are biometric-shaped data belonging
to people who never opted in, which puts a heavier obligation on this layer than on the day
log:

- `forget_person(name)` — drops the record *and* the embeddings.
- `dont_log_this` must suppress speaker capture too, not just the transcript.
- A global switch to stop enrolling anyone new.
- Corn-Jr must be able to say who he currently recognizes, out loud, on request. Hidden state
  is the thing that makes this feel surveillant; answerable state does not.

**Failure modes, honestly.** The default failure here is a *confident wrong label*, and that
poisons memory permanently:

- **Overlapping speech** breaks diarization. Crosstalk segments should be labeled unknown, not
  guessed at.
- **Similar voices** — siblings, parent and child — are exactly the population this gets used
  on and exactly where cosine matching is weakest. A confidence floor with an honest "not sure"
  is mandatory; §9's "he knows when he doesn't know" applies to perception too.
- **Channel shift.** A voiceprint enrolled on a headset may not match the same person over
  speakerphone or a phone codec. Likely needs per-channel centroids.
- **Cold start.** The first second or two of a segment gives a weak embedding.
- **Uneven accuracy across voices** is well documented in speaker ID and should be assumed
  present, not discovered later.

**Latency.** Off the critical path, or it does not ship. Embedding extraction runs concurrently
with STT on the same segment (~5–15ms on the 3080) and adds nothing to the §3 budget. If
identity is still uncertain when endpointing fires, the turn ships with `unknown` and the label
is resolved afterward. Corn-Jr never makes you wait while he works out who spoke.

**What it buys.** He greets the right person. He picks up where that person left off rather
than where the *user* left off. Attribution in the day log is correct. And he knows when the
room has more than one person in it — which is the genuinely useful downstream capability,
because it means he can decline to read something private out loud without being told to.

**Prior art, honestly.** Diarization and speaker ID are largely solved off-the-shelf
(pyannote.audio, NVIDIA NeMo/titanet, WhisperX for diarized transcripts, Picovoice Eagle for
on-device identification). Nothing in the recognition half is novel and none of it should be
built from scratch — §10's STT/TTS reasoning applies unchanged. The unexplored part is the same
shape as §5.2: **person as a second index on the memory store, drilled into the fine-tune so a
250M model routes to it reliably**, rather than bolted on at the prompt layer.

**Sequencing.** The pipeline half rides with Phase 4 (voice loop); the memory half with
Phase 5. Not before either — this is an addition to a working voice loop and a working day log,
and it is worth nothing without both.

### 5.4 Architectural memory (later)

Memory *inside* the model. This is where the from-scratch pretrain buys freedom that nobody
fine-tuning a base model has — the architecture is yours to change.

Directions of interest (unranked, unchosen):
- Recurrent / linear-attention state (Mamba-style SSMs, RWKV) — constant-memory long context.
- Memory tokens / registers — dedicated slots the model learns to read and write.
- Test-time-learned memory modules (the Titans line) — weights that update during inference.
- Fast weights / associative memory.

**The real advantage of 250M is that experiments are cheap.** A model this small means many
runs instead of one. The pretraining pipeline should be built with that in mind from day one:
config-driven architecture, reproducible runs, fast evals. The ability to run 20 architecture
variants is worth more than any single variant.

---

## 6. Tools

The end goal is **50+ tools**. The design principle: tools are the vocabulary of action, so
breadth of tools substitutes for depth of model.

Confirmed direction:
- **Live voice conversation** with Corn-Jr (the "phone call") — full duplex, interruptible.
- **Hands-free research while driving** — ask, he looks it up, he reads back a useful answer.

### The starting set

These four are decided. They're deliberately unglamorous, which is correct — they're the ones
that prove the tool layer works.

1. **Place a call** — dial a contact.
2. **Send a text** — SMS to a contact.
3. **Write and save a note** — freeform text to a file.
4. **Date and time** — what time is it, what day is it, and date arithmetic. Trivially easy to
   implement and the canary for the whole system: if he ever *reasons* about dates instead of
   calling this, something is wrong upstream.

A fifth will come out of development rather than planning. Tools 1–2 need a phone bridge from
the desktop app; tool 4 is the foundation the day-context memory (§5.2) sits on.

### Candidates, not commitments

Named here so they don't get re-invented, explicitly *not* part of the starting set. The
speaker-identity group (§5.3) is the clearest cluster: `who_is_here`, `remember_person`,
`recall_person`, `forget_person`. They wait on Phases 4 and 5.

### The escalation tool — messaging a frontier model (planned)

**Corn-Jr can message a frontier model on the user's behalf.** "Ask the agent to build
you a tool that can do X" — or to do anything at all the user is thinking of.

**The tool is `ask_agent` and not `ask_claude`, and that is a design decision rather than
a naming one.** §1 makes this single-user by design: every instance is somebody's own
copy, and the model behind this tool is whichever one its owner configured — Claude, a
GPT, Qwen, DeepSeek, or something on their own hardware. A vendor baked into the schema
would be a proper noun where the design wants a role, wrong on its face for every
instance that chose differently, and it would put that vendor's name into ~6% of the
tool slice as a thing to be learned. The corpus varies the name across fourteen
alternatives, named and generic, so the router learns the *move* and not the brand; which
agent gets spoken aloud is a runtime fact (`World.agent`), and the model never emits it. He is the voice-first
buffer in front of a model that can actually reason; the request does not have to be for
himself.

This inverts the hardest line in §9. "Daily use when a frontier model is one tab away"
stops being a competition the moment the frontier model is one of *his* tools — you reach
it through him, by voice, hands-free, and the tab-away threat becomes a capability behind
the same interface.

**Why it fits the core bet.** Escalation is routing, which is the one thing he is trained
to do. §9's "he knows when he doesn't know" currently terminates in a tool call or an
honest decline; this gives the decline somewhere to go. Reach for a tool, say "I don't
know", or *ask someone who does* — the third outcome is the most graceful one, and it is
the core bet applied once more: push the reasoning out of the parameters, keep the routing
in.

**It also closes the self-extension loop.** Tools are supposed to be a declaration file,
not a code change — so a request to build a new tool is itself a thing a tool can carry.
The library that substitutes for model depth can grow *through* him rather than around him.

Design rules, written down before any of it is built, in the §5.3 tradition:

- **Relaying is payload copying.** Composing a message on the user's behalf means carrying
  their intent faithfully, not paraphrasing it into something lossy. This is the copy
  discipline the findings already measure, applied to a payload that happens to be the
  user's own words — and findings 33–35 say exactly what that requires: the tool must be
  in the fine-tune corpus with its real schema, not bolted on at the prompt layer and not
  arriving as a surprise shape at inference.
- **Verbatim always; composition only as an addendum. Settled 2026-08-22.** The call
  carries two fields rather than one mode: `request` is required and is the user's own
  words unaltered, `context` is optional and is Corn-Jr's addition, present only when the
  request is underspecified. That is what "both, defaulting to verbatim" has to look like
  once it is a schema, and the two-field form is chosen over a `mode: verbatim|composed`
  flag for three reasons. **The copy ruler survives on every row rather than half of
  them** — `request` is exactly checkable whether or not he elaborated, where a mode flag
  would leave the composed half with no exact comparison left to make. **Silent
  composition becomes unrepresentable**: there is no slot a paraphrase could replace the
  user's words in, which is `corn/grammar.py`'s discipline — make the bad output
  unemittable rather than catch it — applied to the payload instead of the syntax. And it
  is an optional parameter on a shape the registry already supports, so it stays a
  declaration and not a code change.
- **`context` is retrieval, never invention.** It may carry only what a tool returned or
  what was said in this conversation: the day log, a resolved date, an earlier turn, the
  speaker label. Nothing sourced from the weights. §7's non-goal is the rule and §9's
  most-important behavior is the risk — "add some detail on top" is one step from
  confabulating on top, and from outside the two are indistinguishable. Sourcing the
  addendum keeps escalation on the same side of the core bet as every other tool: the
  reasoning stays out of the parameters and the routing stays in.
- **The two failure directions are not equal, and the corpus is lopsided on purpose.** A
  frontier model handed a terse but faithful request asks a clarifying question and costs
  one turn. One handed a confident wrong elaboration acts on it, *as the user*. So a
  missing `context` is a minor miss and a fabricated one is a failure, and that asymmetry
  is pre-registered here rather than discovered in the scorecard.
- **It is a slow tool, declared as such.** Spoken acknowledgment, result later. Nothing
  about the §3 budget changes. The acknowledgment reads back the `context` and not the
  `request`: the user knows what they said, and what they have not yet heard is what was
  added in their name.
- **It is the most consequential tool in the library.** A tool that sends messages *as
  the user* to an agent that can write code and act on the world outranks place-a-call and
  send-a-text. §5.3's rule applies doubly: a speaker label may inform what gets relayed,
  and must never authorize the relaying. The owner's authority, always.
- **The exchange is a ledger, and the ledger is memory — added 2026-08-26.**
  `escalations.jsonl` already keeps the outbound half; the day the send half exists,
  the reply joins it, so every escalation becomes a row a person can ask about:
  what was asked, what was added, what came back, when. Recall costs nothing new —
  a reply is a passage and the extraction reader reads passages (§5.1's addendum),
  the day index already answers "when", so "what did Claude say about the fan last
  week" is a date resolve, a ledger lookup, and a read. Three rules ride along:
  recalled agent text is spoken **with attribution** ("Claude said..."), never as
  his own claim — the say-author discipline pointed at a fourth author; the ledger
  is tool-side and deletable, so `forget_day` and `dont_log_this` govern it exactly
  as they govern the day log; and nothing in it ever reaches a gradient, which is
  §7's non-goal holding at the one place third-party text enters the system.
- **The agent's skills are the agent's vocabulary, not his — added 2026-08-26.**
  "Have Claude run the morning brief" needs no `run_skill(name, args)` tool and
  must not get one: the verbatim relay already carries it, the receiving agent
  interprets its own skill names, and a structured skill schema would bake one
  vendor's vocabulary into the corpus — the exact proper-noun-for-a-role failure
  the `ask_agent` naming decision exists to prevent — and go stale the first time
  that vendor's list changes. What *is* his: the routing ("this is for the agent"),
  the copy (the user's words, exact), and eventually the composition — a scheduled
  escalation ("have Claude do the brief every morning at eight") is `schedule` ×
  `ask_agent`, a compound class for a later corpus, and still not a new tool.
- **The relay declares itself, and relay identity is never authority — settled
  2026-08-26.** Corn-Jr never presents as the user; every relayed message opens by saying
  what it is: relayed by Corn-Jr, the owner's local assistant, voice interface, reply will
  be read aloud — then the verbatim `request`, then the labelled `context`, then a reply
  preference (answer first, short, speakable). The declaration is not etiquette; it is
  formatting instructions for the whole return path. A frontier model that knows it is
  writing for a voice readback through a 250M relay answers in a sentence instead of three
  paragraphs and a code block, and knowing that a clarifying question costs a full queue
  round trip, it states its assumptions and proceeds instead of asking. The authority rule
  is §5.3's, pointed outward: the verbatim `request` carries the owner's intent and nothing
  the wrapper adds carries any — anything consequential still routes through the owner's
  confirmation, never through the relay's say-so. Presenting as the owner is refused for
  `_ask_agent`'s own reason: it is the impersonation-shaped version of writing `sent` into
  a payload. Inbound, the symmetry: the agent's reply is a payload, and he defers to it —
  reads it in the tool-author register rather than paraphrasing it into a claim of his own.

**Sequencing.** The schema belongs in the Phase 3 corpus, which is why relay-vs-compose
had to be settled before Phase 3 rather than after it — the answer decides what the tool's
rows look like, and a corpus built on the wrong answer costs a regeneration and a retrain.
It is settled above and §10's entry is closed. Mechanically it exercises nothing new —
routing plus copy discipline, the two behaviors with the most rulers already pointed at
them — which is the argument for it joining the starting set rather than waiting with the
candidates.

**One consequence to state rather than absorb.** `ask_agent` makes `tool.selection` an
**eight-way** choice. `corn/tools.py` records the same thing about `decline` taking it
from six to seven: nothing already scored moves, because no checkpoint on disk has seen
the name and none can emit it, but every scorecard built from here on answers a different
question and is not comparable with one built before it.

Design rules for the tool layer (proposed):
- **Schema-constrained decoding.** A 250M model should be *unable* to emit a malformed call.
  Grammar-constrained generation, not prayer and a retry loop.
- **Tools are cheap to add.** A new tool should be a declaration file, not a code change.
- **Latency class is part of the contract.** Every tool declares fast (<100ms, inline) or slow
  (spoken acknowledgment, then result). Corn-Jr must know which before he calls it.
- **Failures are speakable.** Every tool error maps to something he can say out loud.

---

## 7. Non-goals

Explicitly out of scope. Listing these is how the parameter budget stays honest:

- Competing with frontier models on anything.
- Open-domain world knowledge from parameters. If he knows it without looking, that's a
  happy accident, not a requirement.
- Serious code generation.
- Multilingual.
- Long-form writing.
- Being a product. Single user. No accounts, no billing, no multi-tenancy.
- Benchmark scores as a success metric. See §9.

---

## 8. Rough phases

Ordering, not a schedule.

**Phase 0 — Pipeline proof.** A ~20M parameter "Corn-Nano" trained end-to-end in about an
hour. Purpose is not quality; it's to prove tokenizer → data → training loop → checkpoint →
eval → inference works before committing the GPU for a week. *Do not skip this.*

**Phase 1 — Data.** The pretraining corpus. Realistically the largest and least glamorous
chunk of work in the project, and the one that most determines final quality.

**Phase 2 — Pretrain.** The real run at ~250M.

On the 3080, at ~25–30 TFLOP/s achieved:
| Token budget | Est. wall-clock |
|---|---|
| 5B (Chinchilla-optimal) | ~3–4 days |
| 20B | ~2 weeks |
| 50B | ~1 month |

For calibration: SmolLM2-135M saw ~2T tokens; Pythia-160M saw 300B. A Chinchilla-optimal run
is the *floor* for coherence, not the target. This table is the strongest argument for
renting compute.

**Phase 3 — Tool-calling fine-tune.** Where the personality and the actual capability come
from. Likely synthetic data generated by a larger model. This phase, not pretraining, is what
makes him useful.

**Phase 4 — Voice loop.** STT, endpointing, streaming TTS, barge-in/interruption. The
latency budget in §3 gets defended here.

**Phase 5 — Memory (application-level).** Per §5.1.

**Phase 6 — Architecture experiments.** Per §5.4. The fun part; deliberately last, because
by now the eval harness exists to tell you whether a change actually helped.

---

## 9. What success looks like

Not benchmarks. Proposed criteria:

1. **He gets used.** Daily, by choice, when a frontier model is one tab away.
2. **Tool-call validity is near-perfect.** Malformed calls should be structurally impossible,
   not rare.
3. **Tool *selection* is right** far more often than a model this size has any business being.
4. **The conversation feels real.** Sub-500ms, interruptible, no dead air.
5. **He knows when he doesn't know** and reaches for a tool instead of confabulating. For a
   250M model this is arguably the single most important behavior in the whole project.
6. **Temporal grounding beats models 100x his size.** "What was I doing last Thursday?" and
   "how long ago did we set that up?" answered correctly, from the day log, without arithmetic.
7. **Something was learned that isn't in a paper.** At least one genuine finding from the
   memory work.

---

## 10. Open questions

- ⬜ **What phone?** Android or iPhone. Determines whether "place a call" and "send a text"
  from a Windows desktop are a weekend or a wall. Android via Phone Link is genuinely
  workable; iPhone from Windows is heavily restricted by iOS.
- ⬜ **Rent compute, or 3080-only?** Currently "maybe, if I hit a wall." Training code should
  be written portable either way so this stays a late decision.
- ⬜ **Architecture family.** Standard transformer baseline first, or go straight to something
  recurrent given the memory interest? (Recommendation: transformer baseline — you need a
  control group to have discoveries *against*.)
- ⬜ **Tokenizer + vocab size.** At 250M, a 32k vocab spends ~10% of the parameter budget on
  embeddings. Smaller vocab is worth considering.
- ⬜ **Where does the tool-calling fine-tune data come from?**
- ✅ **Escalation tool: verbatim relay or composed messages?** **Both, and the schema is
  what keeps that honest — settled 2026-08-22, see §6.** `request` always carries the
  user's words verbatim; an optional `context` carries Corn-Jr's addendum when the request
  is underspecified, sourced only from tool output or the conversation. Two fields rather
  than a mode flag, so the exact-copy ruler applies to every row and a paraphrase has
  nowhere to displace the original to. What is *not* settled by this and does not block
  Phase 3: how often underspecification should fire, which is a corpus share to bracket
  the way `ABSENT_SHARE` is bracketed, not a design question.
- ⬜ **STT and TTS: off-the-shelf or from scratch?** From-scratch is on-thesis for learning but
  is a second full research project bolted onto the first. (Recommendation: off-the-shelf.
  The LLM is the thing you're here to build.)
- ⬜ **How does a speaker label enter the model's context?** A dedicated token
  (`<|spk:dad|>`), a plain-text prefix per segment, or a structured field. This is a tokenizer
  and fine-tune decision, not a runtime one, so it has to be settled before Phase 3 if §5.3 is
  wanted at all.
- ⬜ **What does `unknown` do to the day log?** Kept as an anonymous participant, dropped, or
  held session-scoped and discarded at compaction. Bears directly on whether the store
  accumulates voice data nobody asked it to keep.
- ⬜ **Does a person record feed style adaptation?** §4 permits adapting how he speaks to his
  one user. Whether he should also shift register per *speaker* is a separate question and
  probably a later one.
- ⬜ **Is "Corn" a planned larger sibling, or is Jr. the whole family?**
