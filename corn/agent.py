"""The inference loop the corpus was always written for -- stop at `<|call|>`,
run the tool, feed the real `<|obs|>` back, and let the model read it out.

Until now nothing in this repo executed a call. `evals/` scores a call against
a gold string and stops; `chat.py` is a completion REPL and lets the model
write straight past its own call into an observation it invented. That second
one is not a small gap. §5.2's whole claim is that Corn-Jr answers from the
lookup rather than from the weights, and a model handed a fabricated lookup is
answering from the weights with extra steps -- fluently, and in the exact
format that makes it look like it did the right thing.

So the intervention here is one line of policy: **everything the model writes
after `<|call|>` is discarded unread.** The runtime owns `<|obs|>`. What comes
back is whatever `corn/tools.py` and `corn/temporal.py` actually return, which
are the same functions that generated the training payloads -- so this is not a
new interface being introduced at inference, it is the trained one finally
having something on the other end of it.

**Nothing here is a new tool.** `EXECUTORS` binds names the registry already
declares to functions already written. The one addition is that `save_note`
writes a file, because `save_note_tool` never needed to when its only consumer
was a generator, and a note that is not on disk afterwards is not a note.

**The call is decoded against the schema, not merely checked against it.**
`corn/grammar.py` masks every token that cannot lead to a call `validate_call`
would accept, armed on `<|call|>` and released at the closing brace. It is on by
default and `--no-grammar` turns it off, which is the only way to see what it is
worth. `validate_call` still runs and still decides whether anything executes:
a constraint that made the check redundant would have quietly become the
schema, and then nothing would be guarding the schema.

Every masked step is reported in the transcript. That is deliberate -- a
constraint that silently fixes things hides how often the model was wrong, and
"the grammar bit once on this turn" is the honest form of the claim.

**`--copy` extends that from the schema to the sentence, and it is the third
gap's fix.** A contact name has to be a span of something actually said in this
conversation, so `text Ophelia that I'm running late` can no longer emit
`{"contact": "Omar"}` -- 45 of 120 at 91.6M, every one of them a call the
schema was happy with. The source is the live context rather than the utterance
alone, because the name a second call needs is often in the first call's
observation: `call Chris` returns `matches: ["Chris Patel", "Chris Whelan"]`,
and `Chris Patel` is a span of that. On the first round of a fresh turn the
context *is* the utterance, which is the case `check_grammar.py` measures
against the corpus.

Two honest consequences, neither hidden:

  * the markers are in the source, so `user` is technically a copyable span. It
    would return `not_found` and no model has ever emitted it;
  * in `--multi` the context accumulates names from earlier observations, so
    the constraint genuinely loosens as a conversation runs. It bounds the
    model to the conversation, not to the current sentence.

**`--multi` carries the transcript across turns, and what it is a probe into is
narrower than this file used to claim.** The old banner here said no corpus has
a second `<|user|>` at all. That was never checked and is false: counted over
`data/mix_v3_5b`, the corpus the 260M was actually trained on, `temporal.txt`'s
daycross follow-up supplies 1,720 of 25,118 transcripts with a second `<|user|>`
-- 6.85% of that slice and ~0.34% of the mix. So the multi-turn *shape* is
trained, thinly.

**What is empty is the second turn that does not call.** Of those 1,720, the
marker after the second `<|user|>` is `<|call|>` in 1,720 and `<|say|>` in
**0**, and no other slice in the mix has a second `<|user|>` at all. A second
`<|user|>` therefore means "emit a call" without a single counterexample
anywhere in five billion tokens. That is the gap this flag probes, and it is a
missing *class* inside a shape that exists rather than a missing shape.

Two consequences for how the context is assembled, both of them the corpus's
choice rather than this file's: turns stack with **one** `<|end|>` closing the
conversation, not one per turn (`as_history`), and the `<|day|>` header and the
declaration are written **once**, above the first `<|user|>` (`head` in
`turn`). History is trimmed whole turns at a time, oldest first, because
`block_size` is 512 and a context cut mid-marker would teach us about the
truncation rather than the model.

Two things this loop makes visible that no scorecard row can:

  * **`<|day|>` is a vote for `resolve_date`.** The header occurs only in the
    temporal slice, where every transcript is a resolve_date chain, so
    prefixing it to a turn biases the tool choice before the user has said
    anything. `evals/` cannot see it -- temporal items always carry the header
    and tool items never do, so the confound is split across two files and no
    row observes both. Off by default here, and `--day` is the demonstration
    rather than the recommendation.

  * **`recall_day` had no backend anywhere.** It is in `REGISTRY`, it is called
    69,448 times in `data/raw/temporal.txt`, and every one of those is followed
    by `<|end|>` -- so the model has never seen an observation from it and has
    learned to emit the call and the end marker in one breath. `DayLog` gives
    it one, built out of what `save_note` wrote rather than out of a new
    corpus, and the payload shapes are borrowed from the contact book on
    purpose. See `_recall_day`.

Usage:
    python -m corn.agent
    python -m corn.agent --ckpt checkpoints/nano100m_v1/ckpt.pt --ask "note down buy milk"
    python -m corn.agent --no-grammar --ask "make a note that the deploy is blocked"
"""

from __future__ import annotations

import argparse
import functools
import json
import random
import re
import sys
from collections import deque
from collections.abc import Collection
from datetime import date, datetime
from pathlib import Path

import torch

from .decode import GraphedDecoder, default_buckets
from .extract import FRAME, content_words, grounded
from .grammar import DEFAULT_COPY_SLOTS, SPAN_SLOTS, CallConstraint
from .persona import DEFAULT as DEFAULT_PERSONA
from .persona import (PERSON_BIRTHDAY, PLACEHOLDER_NAME, PLACEHOLDER_USER, Marker,
                      Occasion, Persona, heads_up_key, name_header, unfilled)
from .sample import load_checkpoint
from .markers import D_CALL, D_END, D_OBS, D_SAY, D_USER
from .temporal import (
    DATE_WIDE_TODAY,
    WEEKDAYS,
    WORD_NUMBERS,
    ordinal,
    resolve_date_tool,
    spoken_clock,
    spoken_form,
    weekday_in_span,
)
from .stateline import render_say, split_state
from .socialfam import (
    HARD_FAMILIES, cushioned_refusal, family_rejection, kin_address,
    life_claim, reply_families,
)
from .steps import step_request
from .tools import (
    BLOCKED_BY,
    DECLINE,
    PASSAGE,
    LEAD_ANSWERS,
    READING,
    REGISTRY,
    Tool,
    ask_agent_tool,
    owner_call_tool,
    owner_text_tool,
    save_note_tool,
    take_runtime,
    validate_call,
    web_search_tool,
)

# `chat.py`'s marker, for the same reason: byte-level tokenization means there
# is no EOS in the vocabulary and a document boundary is ordinary text.
STOP_DOC = "<|endoftext|>"

DEFAULT_NOTES = Path("notes.jsonl")


# --------------------------------------------------------------------------
# Executors. Eight names, six backends, and the two without one are the point.
# --------------------------------------------------------------------------


class DayLog:
    """The day log `recall_day` was always declared against, and never had.

    Append-only JSONL, one entry per `save_note`, keyed by the day it was
    written. That is the whole design, and it is deliberately not a new corpus:
    `recall_day` reads back what `save_note` wrote, so the two declared tools
    compose and nothing here had to be invented for the model to talk about.

    §5.2 applies to a runtime store exactly as it does to a generator, so the
    tool composes `say` and the model's only job is to read it out. A store
    that handed back a list and left the phrasing to 91.6M parameters would be
    asking for the one thing the corpus spent four findings teaching him not
    to do.
    """

    def __init__(self, path: Path):
        self.path = path

    def add(self, day: date, text: str, title: str | None) -> None:
        row = {"date": day.isoformat(), "text": text}
        if title:
            row["title"] = title
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def on(self, iso: str) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("date") == iso:
                    rows.append(row)
        return rows


def _save_note(args: dict, ctx: "World") -> dict:
    """`save_note_tool`, plus the append that makes it real.

    The payload is left exactly as trained -- `{"status": "saved", "chars": N}`
    with an optional title -- because the model copies its reply out of it and
    a runtime that improves the wording here would be changing the corpus from
    the far end. Anything worth telling the user has to be a thing the tool
    already says.
    """
    text, title = args["text"], args.get("title")
    ctx.log.add(ctx.anchor, text, title)
    return save_note_tool(text, title)


def _recall_day(args: dict, ctx: "World") -> dict:
    """Read the day log back. The shape is the argument.

    Both payloads are built out of parts the model has copied from other tools
    and has never seen from this one:

      * the hit carries `entries` beside a phrasing field, which is the
        contact book's `matches` + `clarify` shape,
      * the miss is `{"ok": false, "reason": ..., "say": ...}`, which is the
        book's `not_found` shape exactly.

    So an unfamiliar *tool* is being asked with a familiar *structure*, and
    that is the whole point. `no_backend` -- the placeholder this replaces --
    was unfamiliar on both axes at once and he answered it by composing over
    the previous observation. Whether deference is keyed to shape or to the
    tool it came from is now a question with two payloads and one difference
    between them; `scripts/payload_evals.py` asks the scored version.
    """
    iso = args.get("date", "")
    try:
        spoken = spoken_form(date.fromisoformat(iso))
    except ValueError:
        return {"ok": False, "reason": "bad_date", "say": "Sorry, what date was that?"}

    rows = ctx.log.on(iso)
    if not rows:
        return {
            "ok": False,
            "reason": "no_entries",
            "date": iso,
            # Two phrasings under docs/VOICE.md, the first being the one the
            # trained pools also use -- variation stays inside wording the
            # deference path speaks verbatim, so nothing downstream reads it.
            "say": ctx.rng.choice((
                f"I don't have anything for {spoken}.",
                f"Nothing written down for {spoken}.",
            )),
        }
    entries = [r["text"] for r in rows]
    joined = entries[0] if len(entries) == 1 else (
        ", ".join(entries[:-1]) + ", and " + entries[-1]
    )
    return {
        "date": iso,
        "entries": entries,
        "say": f"On {spoken}: {joined}.",
    }


# **The refusal Corn-Jr reads out is written here, not composed by him.** WS-E's
# whole shape: he routes to `decline`, the runtime hands back a `say`, and he
# relays it -- which is deference, the one channel that works, doing the job
# suppression could not. `corn/tools.py`'s failure convention (`ok: false`, a
# `reason`, a `say`) is reused exactly, so the thirty-third finding's "read-back
# on a new tool is free" applies to it without anything new being learned.
#
# This pool is deliberately modest. It is *output*, produced once per refusal at
# inference, and nothing trains on it -- so the cardinality rule that governs
# `corn/toolspace.py`'s say pool in stage 2 does not bind here. Conflating the
# two is how the thirty-fourth finding's arm ended up with 128 refusals at 163
# uses each.
DECLINE_SAYS = (
    "I haven't got anything that does that.",
    "There's no tool on this one, sorry.",
    "That's outside what I can reach from here.",
    "Nothing I've got covers that.",
    "I can't help with that one.",
    # Widened 2026-08-26 under docs/VOICE.md -- same refusal, said by the
    # person the voice page describes. Still output, still nothing trains
    # on it, and the honesty register holds: direct, no cushioning.
    "Nah, I've got nothing for that one.",
    "That one's past me, sorry.",
    "Wish I could, but nothing here does that.",
)


# **Social turns are answered here, and the wording is written out longhand.**
# A greeting or a thank-you has no side effect to validate, and making it
# compete with the seven real tools plus `decline` is what sent ordinary
# follow-ups to a tool in the first place. So the escape hatch is worth having.
#
# But what comes back is *output* -- produced once per social turn at
# inference, with nothing training on it -- so `DECLINE_SAYS`'s argument
# governs these pools too, and for the same reason: cardinality is not what
# makes an answer sound right. A first cut multiplied a grid of openings by a
# grid of endings and got 302 strings, 68 of which had no full stop between
# the halves ("Take care Have a good one.") and three of which said the same
# thing twice ("Have a good one Have a good one."). Every line below is a
# sentence somebody wrote, and the guard checks that rather than the product.
#
# **One voice, and it is a specific one.** The first cut mixed registers --
# "Grand" and "Cheers" and "Right you are" sat next to "You bet" and "Howdy",
# and each line was fine on its own while three of them in a row sounded like
# three different people. That is the same defect the `author` field was added
# for, one level up: several hands writing into one channel with nothing
# marking which is which. So the register is now fixed and written down here,
# because a pool nobody stated the rule for drifts back the first time
# somebody adds a line they like.
#
#     warm, American, contractions everywhere, and glad to see you. Wit is
#     allowed and it stays light -- "Well, look who's here." is the ceiling.
#     Never arch, never world-weary, never British: "Grand", "Cheers", "Right
#     you are", "shout if", "sorted", "good stuff" and "I'll leave you to it"
#     are all out, and `scripts/check_agent.py` keeps them out.
#
# The register check is deliberately a word list rather than taste. It cannot
# tell whether a new line is *good*, only whether it belongs to the voice that
# was pruned away, which is the failure that actually happened.
GREETING_REPLIES = (
    "What's up?",
    "What's the word?",
    "What've we got going on today?",
    "What are we getting into today?",
    "Hey! What's the plan?",
    "Well, look who's here.",
    "Hey there. How's the day treating you?",
    "Hello! How's your day shaping up?",
    "Hey. What can I do for you?",
    "Hi! What are you up to?",
    "Good to hear from you. What's happening?",
    "Hey again. What's going on?",
    "Howdy. What do you need?",
    "Hello there. How are things?",
    "Hey! How can I help?",
    "Alright, I'm here. What's up?",
    "Perfect timing. What do you need?",
    # **Three that do not ask for anything back**, added after
    # `Saved Sessions/session14.txt`. Counted rather than felt: this pool was
    # **16 of 17** questions and the four period buckets **12 of 12**, so 32 of
    # the 34 greetings he could give put the ball straight back. Say hello
    # twice and you are asked twice what you want, which is not warmth, it is
    # a form. `docs/VOICE.md` puts the warmth in the readiness -- and
    # readiness can be *stated*, which is the shape the pool had none of.
    # Register unchanged and `scripts/check_agent.py` still polices it; these
    # go in the everyday pool rather than the buckets so they are reachable at
    # every hour. **Three and not more because the cap is 20** and this pool
    # now sits on it: `scripts/check_agent.py` holds every social pool to
    # 5..20 on `DECLINE_SAYS`' argument that cardinality is not what makes an
    # answer sound right, and that argument did not stop being true here.
    "Hey, good to see you.",
    "Hi there. I'm around whenever you need me.",
    "Hey. Ready when you are.",
)
# **Four stretches, not three, and `night` is why.** An earlier pool offered
# "Late evening, huh?" and it had to go, because `_period` called 17:01
# evening and nobody calls that late. The line was right and the clock was
# wrong: with a night bucket he can say it is late at an hour when it is.
GREETING_BY_PERIOD = {
    "morning": (
        "Morning! What's on the agenda?",
        "Good morning. Ready to get the day moving?",
        "Morning. What's first?",
    ),
    "afternoon": (
        "Good afternoon. How's the day treating you?",
        "Afternoon! What are we up to?",
        "Afternoon. What's left on the list?",
    ),
    "evening": (
        "Good evening. What are we getting into tonight?",
        "Evening! How's the evening going?",
        "Evening. How did the day go?",
    ),
    "night": (
        "Late one, huh? What do you need?",
        "Still up? What can I do?",
        "Burning the midnight oil. What's up?",
    ),
}

# **A day that is not an ordinary day, in the voice the ordinary days are said
# in.** `corn/persona.py` is where a birthday comes from; this is what it does
# to the greeting, and it is `GREETING_BY_PERIOD`'s mechanism one axis over --
# *added* to the everyday pool rather than replacing it, so the day sounds
# brighter without the voice narrowing to five lines for twenty-four hours.
#
# **Not one of these says what the occasion is**, and that is the design.
# Naming it belongs to the mention, which is said exactly once
# (`Marker`); a pool that announced a birthday every time you said hello would
# be announcing it all day. So these are ordinary greetings in a good mood,
# and they are the same five whether the day is his birthday, the owner's, or
# something the owner wrote down.
#
# `docs/VOICE.md`: "the warmth is in the readiness, not in exclamation
# points". These are one notch up from `GREETING_REPLIES` and not three -- no
# confetti, no run of exclamations, and the register word list in
# `scripts/check_agent.py` polices them exactly as it polices the rest.
GREETING_ON_OCCASION = (
    "Hey! Good day for it. What's up?",
    "Well, look who's here. Good timing today.",
    "Hey there. Feeling pretty good today. What's the plan?",
    "Hi! Today's a good one. What are we up to?",
    "Hey. Decent day, this one. What do you need?",
)

# **The mention itself: one sentence, appended to whatever he said first, once
# a day.** Two pools rather than one because the two answers differ in what
# they can honestly claim -- a birthday with a year in the file knows an age
# and a birthday without one does not, and inventing the number would be the
# `ask_agent` rule ("a payload that says sent while nothing left the machine")
# broken over something trivial.
BIRTHDAY_SAYS = (
    "Oh, and it's my birthday today, since you're here.",
    "Also, today's my birthday. Figured you'd want to know.",
    "It's my birthday, by the way. Big day for a small model.",
)

# **`{age}` never opens a sentence, and that is a rule rather than a
# coincidence.** The first cut read "Also, today's my birthday. two years of
# this, somehow." live on `nano100m_v1` -- a spelled number is a lowercase
# word, and a lowercase word after a full stop is the "not a sentence"
# rejection the runtime applies to everything he says. Filling a template is
# not a place to start capitalising things by hand, so the templates are
# written so the slot never lands there.
BIRTHDAY_SAYS_AGED = (
    "Oh, and it's my birthday today. I'm {age} years old, if you're counting.",
    "Also, today's my birthday. Somehow that's {age} years of this.",
    "It's my birthday, by the way. I'm {age} today.",
)

# The other person's day, and the shorter pool is deliberate: his own birthday
# is a thing he can be wry about and the owner's is a thing he wishes them
# well on, which is one move rather than three. `{who}` is filled from the
# `name:` in `packs/about-me.md` and the unnamed pool answers when there is
# none -- see `_occasion_say`.
OWNER_BIRTHDAY_SAYS = (
    "Happy birthday, by the way. Hope it's a good one.",
    "And happy birthday. Hope today treats you well.",
    "Happy birthday, incidentally. Enjoy it.",
)

OWNER_BIRTHDAY_SAYS_NAMED = (
    "Happy birthday, {who}. Hope it's a good one.",
    "And happy birthday, {who}. Hope today treats you well.",
    "Happy birthday, {who}. Enjoy it.",
)

# **Someone else's birthday, a few days out** (PLAN-PEOPLE §5, the owner's
# three days of 2026-10-13): a person from the people store, named the way
# the owner calls them. A heads-up and not a celebration -- it is not his day
# or the owner's, so no exclamation and no brightening of the greeting.
# `{when}` is "today", "tomorrow" or "in three days" (`_heads_up_when`), and
# neither slot opens a sentence, for `BIRTHDAY_SAYS_AGED`'s reason.
PERSON_BIRTHDAY_SAYS = (
    "Heads up, {who}'s birthday is {when}.",
    "By the way, it's {who}'s birthday {when}.",
    "Oh, and {who} has a birthday {when}.",
)

# "How are you" is a question, not a nicety, and answering it out of
# GREETING_REPLIES was a deflection -- being asked how you are and replying
# "What's up?" is not a conversation. Its own small pool answers it and then
# hands the turn back.
WELLBEING_REPLIES = (
    "Doing well, thanks. What's up?",
    "All good here. What've we got going on?",
    "Can't complain. What do you need?",
    "Good, thanks for asking. What's the plan?",
    "Pretty good. What's happening?",
    "Not bad at all. What can I do for you?",
    "Doing fine. What's on your mind?",
    "All well here. What's the word?",
    "Same as ever, thanks. What are we getting into?",
)

FAREWELL_REPLIES = (
    "Take care.",
    "Catch you later.",
    "Talk soon.",
    "See you later.",
    "See you around.",
    "Until next time.",
    "Have a good one.",
    "Take it easy.",
    "You know where to find me.",
    "I'll be right here.",
    "Later! Holler if you need me.",
    "See you. Come find me anytime.",
)
FAREWELL_BY_PERIOD = {
    "morning": ("Have a good morning.", "Enjoy the rest of your morning."),
    "afternoon": ("Have a good afternoon.", "Enjoy the rest of your afternoon."),
    # "Goodnight." is offered from the evening on rather than at night only:
    # parting for the day at nine is a goodnight, and waiting for the night
    # bucket would withhold the obvious line for four hours.
    "evening": ("Goodnight.", "Have a good evening.", "Enjoy your evening."),
    "night": ("Goodnight.", "Sleep well.", "Get some rest."),
}

THANKS_REPLIES = (
    "You're welcome.",
    "Anytime.",
    "No trouble at all.",
    "Happy to help.",
    "Glad I could help.",
    "My pleasure.",
    "Of course.",
    "You got it.",
    "That's what I'm here for.",
    "No problem at all.",
    "Any time. Glad it helped.",
    "You bet.",
    "Don't mention it.",
    "Glad that did the trick.",
    "Happy to. Holler if you need anything else.",
)

ACK_REPLIES = (
    "Sounds good.",
    "Got it.",
    "Sure thing.",
    "Noted.",
    "Fair enough.",
    "Cool.",
    "Perfect.",
    "All set.",
    "Understood.",
    "No worries.",
    "That works.",
    "Copy that.",
    "Makes sense.",
    "Alright. Holler if you need anything else.",
)

# **The sixth family -- a low mood, stated.** PLAN-CONVERSATION 4d. "I had a
# rough day, my dog is sick" was declined live on 2026-09-04 and "I'm kind of
# tired today honestly" got a different wrong move on every checkpoint,
# because `WELLBEING` is the *question* to him and a user stating a low mood
# had no family, no hatch and no payload. These are the floor for the short
# forms; the open forms ("my dog is sick") cannot be hatched and are arm 5's
# whole point. Hand-written to `docs/VOICE.md`: every line offers rather than
# asks, because the warmth is in the readiness, and none carries a digit, a
# tool word or a claim about a life he does not have. `scripts/check_agent.py`
# asserts each of those, and `scripts/check_social.py` asserts every line reads
# as consolation to `corn.socialfam.reply_families` and as nothing consolation
# excludes -- the floor can never refuse itself.
LOW_REPLIES = (
    "Sorry to hear it. Anything I can take off your plate?",
    "Rough one, huh. Give me the small stuff if it helps.",
    "Sounds like a long one. Want anything written down before you forget it?",
    "That's no good. Go easy tonight.",
    "Been there, sort of. Say the word if I can help.",
    "Hang in there. I've got the small stuff if you want to hand it over.",
    "Get some rest when you can. I'll be right here.",
)


# **Whole utterance, exact match, no prefixes.** The earlier version also
# accepted anything *starting* with "hey ", "hi ", "ok " and so on, filtered
# by a blocklist of twenty request words. That is backwards twice over: a
# greeting is the commonest way to *open* a request, and a blocklist of verbs
# can never be finished. It swallowed "hi so my flight got cancelled", "hey
# I am running late tell her" and -- worst -- "ok do it", which is a person
# authorising an action and being told "All set." while nothing happens.
#
# Exact match cannot do that. It answers the turns that really are nothing but
# a social move, and everything else goes to the model and the tools, which is
# where a turn carrying a request belongs. The cost is that "thanks a lot" has
# to be listed next to "thanks"; the cost is worth it.
GREETINGS = frozenset({
    "hi", "hey", "hello", "howdy", "heya", "hiya", "yo", "sup", "greetings",
    "morning", "afternoon", "evening",
    "good morning", "good afternoon", "good evening", "good day",
    "hey there", "hi there", "hello there", "hey you",
    "hello again", "hey again", "hi again",
    "hey mate", "hi mate", "morning mate", "hey man", "hi man",
    "what's up", "whats up", "wassup", "what's up then", "whats up then",
    "what's the word", "whats the word",
    "what've we got going on", "whatve we got going on",
    "what have we got going on", "what we got going on",
    "what've we got going on today", "whatve we got going on today",
    "what have we got going on today", "what we got going on today",
    "what are we getting into", "what are we getting into today",
    "what's the plan", "whats the plan",
    "what's the plan today", "whats the plan today",
    "long time no see",
    "you there", "are you there", "you around", "are you around",
    # **The twelve `check_hatches.py` recorded as reaching the router, folded
    # in on 2026-09-02.** They were held back deliberately on 2026-08-29 --
    # register the pools did not carry, priced and not taken -- and what
    # changed is who writes the sentence. `rephrase=True` means a hatch match
    # *routes* the turn to the model with `<|say|>` prefilled and
    # `social_rejection` reading the result; a miss sends the same turn to
    # the router with nothing reading the result at all. Since
    # `corn_jr_260m_v4_ft_social2` he writes these replies himself either way
    # (`social.heldout_carrier` 10/12), so folding them in changes the author
    # not at all and puts the guard in front of twelve more turns. They stay
    # out of the training corpus -- `corn/socialgen.py`'s `HELD_OUT` refuses
    # them by name -- so `social.heldout_carrier` remains a generalisation
    # row. Each sits in the family `evals/social.jsonl` gives it.
    "good to see you", "what's new", "whats new", "anything happening",
    "hey you still there", "hope you're well", "hope youre well",
})

WELLBEING = frozenset({
    "how are you", "how are you doing", "how are you today",
    "how're you", "howre you", "how are ya",
    "how's it going", "hows it going", "how is it going", "how goes it",
    "how are things", "how's things", "hows things",
    "how's everything", "hows everything",
    "how have you been", "how've you been", "howve you been",
    "how's your day", "hows your day",
    "how's your day going", "hows your day going",
    "you alright", "are you alright", "you keeping well",
    # The 2026-09-02 widening -- see `GREETINGS`. "you good?" is listed as
    # `_normalised` cuts it, which is how every phrase here is listed.
    "hey how are you", "hi how are you doing", "you good", "how was your day",
})

THANKS = frozenset({
    "thanks", "thank you", "thanks so much", "thank you so much",
    "thanks very much", "thank you very much", "thanks a lot",
    "thanks a million", "thanks a bunch", "many thanks", "much appreciated",
    "appreciate it", "appreciate you", "i appreciate it", "i appreciate that",
    "cheers", "cheers mate", "cheers thanks", "ta", "nice one",
    "thanks again", "thank you again", "thanks for that", "thank you for that",
    "thanks for the help", "thank you for the help", "thanks for your help",
    "thanks pal", "thanks buddy", "thanks mate", "thanks man",
    "you're a lifesaver", "youre a lifesaver", "you're the best",
    "youre the best", "legend",
    "perfect thanks", "great thanks", "ok thanks", "okay thanks",
    "got it thanks", "brilliant thanks", "lovely thanks",
    "thanks i owe you one", "thanks i needed that",
    # **The evaluative tail, which is how people actually close a turn.**
    # "thanks, that helps" carries no request, is nothing but a social move,
    # and was reaching the model -- which declined it, live, at 260M. Bare
    # "thanks" was listed and the commonest way of saying it was not. Both
    # apostrophe spellings, by the convention "you're a lifesaver" set above:
    # `_normalised` folds the typographic apostrophe and keeps the plain one,
    # so a dictated "that's" and a typed "thats" are two strings.
    "thanks that helps", "thank you that helps", "cheers that helps",
    "thanks that helps a lot", "thanks that really helps",
    "thanks that's great", "thanks thats great",
    "thanks that's perfect", "thanks thats perfect",
    "thanks that's helpful", "thanks thats helpful",
    "thanks that's exactly what i needed", "thanks thats exactly what i needed",
    "that helps thanks", "that helps thank you", "that's helpful thanks",
    "thats helpful thanks", "that's great thanks", "thats great thanks",
    "perfect thank you", "great thank you", "lovely thank you",
    "thanks so much for that", "thank you so much for that",
    # The 2026-09-02 widening -- see `GREETINGS`. Whole-utterance, so the
    # "ok" inside it never meets the confirm gate's list; `check_confirm.py`
    # asserts that over the string rather than over the word.
    "ok cool thanks",
})

FAREWELLS = frozenset({
    "bye", "goodbye", "good bye", "bye bye", "byebye", "bye now",
    "good night", "goodnight", "night", "night night", "nighty night",
    "goodnight then", "night then",
    "see you", "see ya", "see you later", "see ya later", "see you soon",
    "see you tomorrow", "see you then",
    "catch you later", "catch ya later", "catch you soon",
    "talk soon", "talk later", "talk to you later", "talk to you soon",
    "speak soon", "speak later", "until next time",
    "have a good one", "have a good day", "have a good night",
    "have a good evening", "have a great day", "have a good weekend",
    "later", "laters", "peace", "peace out", "cheerio", "so long",
    "farewell", "signing off", "adios",
    "i'm off", "im off", "i'm out", "im out",
    "i'm heading off", "im heading off",
    "gotta go", "got to go", "i gotta go", "i have to go",
    "i've got to go", "ive got to go",
    "i'm going to bed", "im going to bed", "off to bed", "bedtime", "bed time",
    "that's all", "thats all", "that's all for now", "thats all for now",
    "that's it for now", "thats it for now",
    "that's everything", "thats everything",
    "all done", "we're done", "were done",
})

# **Nothing in here may be a yes or a no.** `harness/backends/confirm.py`
# resolves a held phone call against the whole utterance, and the server runs
# that gate before the turn ever reaches this file -- so today the overlap is
# unreachable. Today is not a guarantee. "ok", "okay", "sure", "yes", "yeah"
# and "yep" are therefore absent by construction rather than by call order,
# and `scripts/check_confirm.py` asserts the disjointness against the gate's
# own lists, so a word added to one side cannot quietly land on the other. An
# acknowledgement wrongly answered here costs a stilted reply; a confirmation
# wrongly answered here costs a phone call that never went out.
ACKS = frozenset({
    "k", "kk", "okey dokey", "okey doke",
    "got it", "gotcha", "understood", "roger", "roger that", "copy that",
    "sounds good", "sounds great", "sounds good to me",
    "that works", "works for me",
    "perfect", "great", "grand", "nice", "cool", "brilliant", "lovely",
    "excellent", "awesome", "sweet", "magic", "ace",
    "right", "righto", "alright", "all right", "fair enough", "makes sense",
    "noted", "good stuff", "no worries", "all good", "exactly", "indeed",
    "fine", "good to know", "i see",
    # The same tail without the thank-you. Kept out of `THANKS` rather than
    # duplicated into it, so the five sets still partition and the guard that
    # asserts it still means something.
    "that helps", "that's helpful", "thats helpful",
    "that's great", "thats great", "that's perfect", "thats perfect",
    "that's what i needed", "thats what i needed",
    "good to hear", "fair point", "very good",
    # The 2026-09-02 widening -- see `GREETINGS`. An apology for the
    # interruption is an acknowledgement with the roles reversed, and "It's no
    # bother. What can I do for you?" is the shape he already answers it in.
    "alright cool", "sorry to bother you",
    # **The positive answer to "how are you", which is his question and so was
    # in no set.** `WELLBEING` holds the question; `LOW` holds the unhappy
    # answer; the happy answer had nowhere to go, and "pretty good. bit tired
    # though, long week" therefore failed `_social_run` on its first fragment
    # and went to the router whole. An ack is the right register for it: he is
    # being told nothing needs doing.
    "pretty good", "not too bad", "not bad", "cant complain",
    "can't complain", "doing alright", "doing ok", "doing okay", "yeah good",
})

# **A low mood, in the short whole-utterance forms a user actually produces.**
# PLAN-CONVERSATION 4d. Whole utterance for `GREETINGS`' reason: "rough day,
# note that I'm skipping the gym" carries a request and goes to the model and
# the tools, and no prefix rule is allowed to guess. The British forms ride
# along because the user may say them even though he never does (VOICE rule
# 7 is about his spellings, not the listener's).
LOW = frozenset({
    "i'm tired", "im tired", "so tired", "rough day", "long day",
    "not great", "not good", "been better", "not my day", "meh",
    "i'm exhausted", "im exhausted", "bit down", "feeling down",
    "not feeling it", "rough one", "tough day", "bad day",
    "i'm knackered", "im knackered", "kind of tired", "kinda tired",
    "pretty tired", "i'm shattered", "im shattered",
    "i'm so tired", "im so tired", "i'm wiped", "im wiped", "i'm beat",
    "im beat", "long one", "it's been a day", "its been a day",
    "i'm not great", "im not great", "not doing great", "not so good",
    "feeling low", "bit low", "i'm drained", "im drained",
    # **2026-09-07, measured leaks.** "bit tired today, long week" left this
    # machine as a live `web_search` query. `_SOCIAL_TAIL` takes "today" and
    # "though" off, and `_SOCIAL_JOIN` splits the run -- but both halves have
    # to be *in* a pool for either mechanism to matter, and the week forms
    # were not. `long day` and `long one` were already here; a week is the
    # same complaint over a longer span and people say it more.
    "bit tired", "long week", "rough week", "tough week", "busy week",
    "what a week", "what a day", "shattered", "knackered", "wiped out",
    # The crossed forms. This set already had "i'm tired" and "kind of tired"
    # and not "i'm kind of tired", which is the sentence the set's own
    # docstring names as the one that "got a different wrong move on every
    # checkpoint" -- `_SOCIAL_TAIL` takes "today honestly" off it and then had
    # nothing to land on.
    "i'm kind of tired", "im kind of tired", "i'm kinda tired",
    "im kinda tired", "i'm pretty tired", "im pretty tired",
    "i'm a bit tired", "im a bit tired", "bit knackered", "bit shattered",
})


# **His own name, at either end of the utterance.** The seventy-eighth finding
# measured this as the single largest term in the hatch miss column, and not as
# a list of examples: over all 275 phrases in the five social pools, **0 survive
# being addressed by name** and a trailing strip recovers all 275. `morning` and
# `good night` are both in the pools; `morning corn` and `good night corn` were
# not, and went to the router -- which is how `thanks corn` reached the live
# search provider and came back with Food Network's Thanksgiving corn recipes.
#
# Both ends, though only the trailing one was measured pool-wide. A leading
# vocative is the same utterance with the address moved ("corn, are you an AI"),
# and the search side already has the matching repair in `strip_affixes` for the
# case where it costs a lookup instead of a greeting.
#
# **The short form was the half left open, and it is the half people type.**
# `corn`, `corn jr`, `corn junior` and `cornjr` were all stripped; bare `jr`
# and `junior` were not. The property this strip exists for therefore held at
# **275/275 addressed as "corn" and 0/275 addressed as "jr"** -- the same
# measurement the finding made, run over the address it was not run over. It
# is how "Hi Jr" reached the router and came back opening a lesson on English
# verbs (`Saved Sessions/session14.txt`, turn 2 -- the schoolroom voice
# `check_hatches.py` section 4 already records as a leak, arriving by a door
# that did not have to be open). Both forms are stripped at both ends now, and
# section 3 asserts the property over every address rather than over the one
# it was first written for.
#
# **The short form is also the safer one to strip**, for the reason VISION
# section 4 gives: `jr` is *his* name and ships with him, while `corn` is the
# owner's nickname on this instance -- the token `USER_IDENTITY_ASKS` below
# had to compose its queries around rather than cut.
#
# **The risk is corn the vegetable, and it is bounded by where this runs.**
# `_normalised` is read by the hatch matchers and by nothing else, so a false
# strip can only ever mis-file a turn into a frozen set -- and every set is
# matched *whole*. "what is corn" strips to "what is", which is in no pool;
# `scripts/check_hatches.py` §3 asserts that over a battery of corn-the-food
# utterances rather than leaving it as an argument.
_VOCATIVE = re.compile(
    r"^(?:corn(?: jr| junior)?|cornjr|jr|junior)\b\s*"
    r"|\s*\bcorn(?: jr| junior)?$|\s*\bcornjr$|\s*\b(?:jr|junior)$"
)


@functools.lru_cache(maxsize=8)
def _vocative_for(name: str) -> re.Pattern | None:
    """The strip for a renamed instance's own name, at either end, or `None`.

    PLAN-PERSONALITY (second): the shipped strip knows `corn` and `jr`, so on
    an instance called Beans "beans, who are you" reached the router with the
    name still on it and missed every hatch. The name is folded the way
    `_normalised` folds the utterance -- lowercase, marks dropped -- in both
    its spaced and its joined form ("sprout two" and "sprouttwo", which is
    how "Corn-Jr" became `cornjr`), so the two sides are compared the same
    way. `None` on the default and on a name the shipped pattern already
    covers, so the no-file runtime runs the regex it always ran.
    """
    folded = " ".join("".join(c.lower() for c in name.replace("’", "'")
                              if c.isalnum() or c in " '").split())
    if not folded or folded in ("corn jr", "cornjr", "corn", "jr", "junior"):
        return None
    forms = {re.escape(folded), re.escape(folded.replace(" ", ""))}
    alts = "|".join(sorted(forms, key=len, reverse=True))
    return re.compile(rf"^(?:{alts})\b\s*|\s*\b(?:{alts})$")


def _normalised(text: str, name: str = "") -> str:
    """Lowercase, drop punctuation, collapse spaces, take his name off the ends.

    Deliberately the same shape as `confirm.py`'s `_normalise`, so an
    utterance is cut the same way on both paths and the disjointness those
    frozensets are checked for is disjointness of the things actually
    compared. The one addition is the typographic apostrophe, which phone
    keyboards and dictation produce and which would otherwise make "what's up"
    and "what’s up" two different strings.

    The vocative strip is the second addition and is the newer one -- see
    `_VOCATIVE` above for what it is worth and what it risks. It runs *after*
    the punctuation fold so that "morning, Corn!" and "morning corn" are one
    string, and it never returns empty: a bare "corn" is an utterance in its
    own right and stripping it to nothing would file it as a blank line.
    """
    flat = text.replace("’", "'")
    kept = [c.lower() for c in flat if c.isalnum() or c in " '"]
    said = " ".join("".join(kept).split())
    stripped = " ".join(_VOCATIVE.sub("", said).split())
    # `name` is the persona's; the shipped strip runs first so a renamed
    # instance still answers to "corn" (the pools do, and `SPEAKABLE_CAPS`
    # does), and the new name is taken off after it. Never empty, for the
    # reason above: "beans" alone is an utterance.
    own = _vocative_for(name) if name else None
    if own is not None:
        stripped = " ".join(own.sub("", stripped).split()) or stripped
    return stripped or said


# **The fold -- one transform, and it is the one that was measured to be free.**
# Owner decision 1b/0, taken 2026-08-30 and **re-taken the same day after its
# own gate failed** (`docs/PLAN-FINETUNE-V4.md` step 5). The runtime casefolds
# an all-caps turn before the model sees it, and does nothing else.
#
# What it is deliberately not is `_normalised`, which was built for hatch
# *matching* -- where a false fold can only ever mis-file a turn into a set
# that is matched whole -- while this one rewrites the tokens the weights are
# handed. Each of `_normalised`'s three transforms is refused here for its own
# measured reason:
#
#   * **No blanket lowercase.** `surfacegrid`'s control column found a defect
#     of its own: telephony routes **6/8 verbatim and 2/8 lowercased**, because
#     lowercasing the utterance lowercases the *contact name* the copy slot has
#     to find. Folding case on ordinary text destroys proper nouns. So the fold
#     cases only the turn that is already lost -- **all-caps, which is 0 of 57
#     in both punctuations across all five families**, 56 of those 57 misses no
#     call at all. Folding a total loss can only help, and the after-read says
#     it does: `upper` and `upper?` go to **39/57**, exactly their `lower`
#     twins. `Title` (9/57) and `MiXeD` (4/57) are the accepted residue -- they
#     are not total, and a rule aggressive enough to catch them is the blanket
#     lowercase that costs the contact slot. The owner declined the corpus
#     transform that would have bought them.
#   * **No vocative strip.** `_normalised` takes "corn" off both ends and that
#     is right for a hatch. Here it is wrong twice over: the model trained with
#     vocatives in its carriers, so removing them moves the turn *away* from
#     the trained orthography rather than toward it; and entry 8 already
#     recorded the hazard -- on this instance "corn" as an address is also the
#     token that is the answer.
#   * **No punctuation strip.** See the retirement below. This is the half the
#     first version of this fold had, and it is gone rather than switched off.
#
# It is applied in `Agent.turn` at the point the utterance becomes the model's
# turn, so every consumer inherits it: the live agent, the server, and every
# grid that drives one. That includes the copy grammar, whose spans are cut
# from the folded turn -- which is the coherent choice (the model can only copy
# what it was shown) and also means an all-caps note is *saved* folded. That is
# accepted rather than overlooked.
#
# The hatches, the confirm gate and `harness/backends/search.py`'s privacy
# backstop all normalise for themselves and are untouched. This fold is a
# no-op as far as they are concerned: everything it does, `_normalised` and
# `_normalise` already did harder.

# ---------------------------------------------------------------------------
# **RETIRED 2026-08-30: the terminal question-mark strip, by measurement.**
# Recorded here rather than deleted silently, because the next person to read
# entry 0's punctuation count will have the same good idea.
#
# The first version of this fold also removed a terminal `?`, on the strength
# of `surfacegrid`'s punctuation column. `harness/foldgate.py` was built to ask
# what that costs the one family `surfacegrid` excluded by design, and it is a
# lot: 244 turns an arm on `corn_jr_260m_v4`, one instance, nothing else moved
# between the arms --
#
#     punctuated resolve_date carriers that reach the weights
#         strip off   18/24     strip on   1/24
#     the bare control column, which the fold cannot touch
#         strip off    7/8      strip on   7/8
#     routegrid grid T's event_date and neutral, punctuated
#         strip off    8/8      strip on   8/8
#
# All seventeen turns that moved went `resolve_date` -> `web_search`. The
# corpus counted why before the fold was written: 2,268,194 of the 2,442,972
# punctuated user turns in `mix_v4_5b` call `resolve_date`, and no tool but
# that one and chat has ever been called after a question mark. **The strip
# deletes the single strongest routing signal that tool has.**
#
# Both prices, so the trade is on one page and nobody has to re-derive it: the
# strip **buys 16 of 57** pooled across `surfacegrid`'s five families (owner
# questions 9/24 -> 21/24, decline 6/8 -> 8/8, telephony 4/8 -> 6/8; card
# `..__surfacegrid-fold.json`, read with both halves on) and **costs 17 of 24**
# on the family the corpus spent 2.27M rows on. The owner retired it on those
# numbers.
#
# **What replaces it is per-family and not a fold.** The user-identity half of
# entry 8 -- the largest single term in that 16 -- is closed in the runtime by
# `user_identity_request` below, which writes the `web_search` call so the
# store answers whichever surface the question arrives in. `decline` and
# telephony's two-of-eight and entry 1c's punctuated soft recall are deferred
# to entry 0's corpus transform at a future mix seat. The temporal family is
# untouched by any of it, which is the whole point.
# ---------------------------------------------------------------------------

# Three letters is the corpus's own threshold: entry 0's count of all-caps
# user turns -- 15 in 6,603,586 -- is "at least three letters and no lowercase
# one", and a fold that fired on a different population than the count would
# be answering a question nobody measured. It also keeps "OK" and "hi" out of
# it, which are not shouting.
_FOLD_MIN_LETTERS = 3


def shouted(text: str) -> bool:
    """Is this the all-caps column -- three letters or more, none of them lower?

    Separate from `fold_turn` because the guard asserts the predicate and the
    transform independently, and because "which turns would this fire on" is a
    question `scripts/` asks of a corpus without wanting the rewrite.
    """
    letters = [c for c in text if c.isalpha()]
    return len(letters) >= _FOLD_MIN_LETTERS and not any(c.islower()
                                                         for c in letters)


def fold_turn(text: str) -> str:
    """The utterance as the model is handed it. See the block comment above.

    `str.lower` rather than `str.casefold` on purpose: `lower` is the exact
    inverse of `harness/surfacegrid.py`'s `recase(..., "lower")`, so a folded
    `upper` cell becomes byte-identical to its `lower` twin and the after-read
    is a comparison rather than an approximation. `casefold` differs only
    outside ASCII, and where it differs it rewrites characters the user typed.

    The identity on every turn that is not shouting, which is nearly all of
    them -- 15 in 6,603,586 by the corpus count -- so the `fold` event and the
    `folded` column in `turns.jsonl` are both rare by construction.
    """
    return text.lower() if shouted(text) else text


def _period(now: datetime | None = None) -> str:
    """Which of four stretches of the local day it is.

    **`night` exists so a line is allowed to say it is late.** Three buckets
    put 17:01 and 01:30 in the same one, which is why "Late evening, huh?"
    had to be dropped from the pool rather than fixed: there was no hour the
    runtime could tell apart. Every key here has to appear in both
    `GREETING_BY_PERIOD` and `FAREWELL_BY_PERIOD` or the accessor raises;
    `scripts/check_agent.py` asserts that over the whole 24 hours rather than
    over a list of names somebody remembered to update.
    """
    current = now or datetime.now().astimezone()
    if 5 <= current.hour < 12:
        return "morning"
    if current.hour < 17:
        return "afternoon"
    if current.hour < 22:
        return "evening"
    return "night"


# How many recent replies `_pick` is asked to avoid. Three is enough that a
# short exchange -- hello, thanks, bye, hello again -- cannot repeat itself,
# and small enough to leave `WELLBEING_REPLIES`' nine lines six to draw from.
RECENT_SAYS = 3


def _pick(rng: random.Random, pool: tuple[str, ...],
          avoid: Collection[str] = ()) -> str:
    """A line from `pool`, preferring one that was not just said.

    **Why this is not `rng.choice`.** A greeting is the most repeated turn
    there is and the pool it draws from is the smallest in the runtime, so an
    unmemoried draw says the same thing twice running about one time in
    twenty -- on the exact turn a person notices repetition first. Cardinality
    was never the fix for that; `DECLINE_SAYS`' argument holds, and the pools
    stay written rather than multiplied. Remembering is the fix.

    The fallback when `avoid` covers the pool is not a formality. Nine lines
    and a long enough history would otherwise leave nothing to say, and
    repeating yourself only beats silence until silence is not the choice.

    **The state stays outside.** `avoid` is passed in rather than kept in a
    module global, so `conversational_reply` is still a pure function of its
    arguments and a replay from the same world seed over the same turns
    reproduces exactly. Hidden state here would have cost that quietly.

    **A recent reply is matched by prefix, not by equality**, because what the
    caller recorded is the sentence it *emitted* and only the social path
    emits a pool line unchanged. `identity_reply` joins the pool line to a
    capability sentence built at call time, so an equality test would never
    fire there and the `avoid` argument would be decoration. The pool line is
    the head of that join, and a head is what this compares.
    """
    fresh = [s for s in pool if not any(r.startswith(s) for r in avoid)]
    return rng.choice(fresh or list(pool))


def _greeting_replies(now: datetime | None = None,
                      peppy: bool = False) -> tuple[str, ...]:
    """The greeting pool for the local time of day.

    The generic lines stay available at every hour and only the time-specific
    ones swap, so the clock narrows the wording without narrowing the voice.
    Taking `now` as an argument is what lets the guard fix the hour without
    making the reply itself deterministic.

    `peppy` is an occasion day -- a birthday, or anything else
    `packs/persona.md` marked -- and it *widens* the pool rather than swapping
    it, for the reason `GREETING_ON_OCCASION` gives. Off by default, so every
    instance without a persona file draws from exactly the pool it always did.
    """
    pool = GREETING_REPLIES + GREETING_BY_PERIOD[_period(now)]
    return pool + GREETING_ON_OCCASION if peppy else pool


def _farewell_replies(now: datetime | None = None) -> tuple[str, ...]:
    return FAREWELL_REPLIES + FAREWELL_BY_PERIOD[_period(now)]


def _occasion_say(occasion: Occasion, rng: random.Random, when: date,
                  persona: Persona = DEFAULT_PERSONA,
                  avoid: Collection[str] = ()) -> str:
    """The one sentence that names the day. Composed here, or read from the file.

    **Three kinds, and only one of them is a sentence the owner wrote.** His
    birthday and theirs are composed from the pools above, which had to pass
    `docs/VOICE.md` like every other thing he says. An `on:` occasion carries
    the owner's own line and goes out as typed -- the contact book's terms,
    not a loosening of them: it is their machine, their file, their sentence.

    The age is spelled rather than printed, because these are read aloud and
    `WORD_NUMBERS` already holds the words `resolve_date` speaks its own
    numbers with. Past thirty it falls back to the digits, which is a problem
    for a later decade.
    """
    if occasion.kind == "on":
        return persona.named(occasion.line)
    if occasion.kind == PERSON_BIRTHDAY:
        return _pick(rng, PERSON_BIRTHDAY_SAYS, avoid).format(
            who=occasion.who, when=_heads_up_when((occasion.next_on(when) - when).days))
    if occasion.kind == "owner_birthday":
        who = occasion.who.strip()
        if not who:
            return _pick(rng, OWNER_BIRTHDAY_SAYS, avoid)
        return _pick(rng, OWNER_BIRTHDAY_SAYS_NAMED, avoid).format(who=who)
    age = occasion.age_on(when)
    if age is None or age < 1:
        # A first birthday counted from a year the file gave is still a
        # birthday; a *zeroth* one is the file saying he was made this year,
        # and "zero years old, if you're counting" is not a sentence.
        return _pick(rng, BIRTHDAY_SAYS, avoid)
    return _pick(rng, BIRTHDAY_SAYS_AGED, avoid).format(
        age=WORD_NUMBERS.get(age, str(age)))


def _heads_up_when(days: int) -> str:
    """How far off a birthday is, the way it is said out loud."""
    if days <= 0:
        return "today"
    if days == 1:
        return "tomorrow"
    return f"in {WORD_NUMBERS.get(days, str(days))} days"


# **Trailing words that modify a social move without adding a request.**
# The sixth family's own docstring names "I'm kind of tired today honestly" as
# a turn that "got a different wrong move on every checkpoint", and the reason
# is entirely this: `kind of tired` is in `LOW` and `kind of tired today
# honestly` is not, because the pools are matched whole and a person does not
# stop at the phrase the pool lists. Stripped from the end, repeatedly, and
# **only ever accepted if what remains still matches a pool whole** -- which
# is what keeps the whole-utterance rule that `GREETINGS` argues for. A
# request cannot survive the strip: "note that down today" leaves "note that
# down", which is in no pool, and the turn routes exactly as it did.
#
# Measured leaks, not guesses, in the order they were seen: "bit tired today,
# long week" and "pretty good. bit tired though, long week" reached the live
# search provider as `web_search{"query": "bit tired today"}` on 2026-09-07.
_SOCIAL_TAIL = (
    "today", "honestly", "though", "tbh", "lately", "really",
    "right now", "at the moment", "as well", "too", "i guess", "i think",
    "to be honest", "these days", "this week", "as usual",
)

# **A run of social moves is still nothing but social moves.** The same
# 2026-09-07 sitting: people do not type one move per turn, they type "bit
# tired today, long week" and "pretty good. bit tired though, long week", and
# every fragment of both is a move the pools already answer. Split on the
# punctuation and the conjunction people actually join them with.
#
# **The guard is that *every* part must match**, which is the whole-utterance
# rule applied per fragment rather than relaxed. "rough day, note that I'm
# skipping the gym" -- the sentence `LOW`'s docstring uses to argue for whole
# matching -- still routes, because its second fragment is in no pool. So this
# widens the hatch over runs of social moves and over nothing else.
_SOCIAL_JOIN = re.compile(r"\s*(?:[,.;!?]+|\band\b)\s*")

# The families a *run* is allowed to be claimed for -- see `_social_run` for
# why the rule is narrower than the argument for it. These are the three a
# missed run was measured to cost a live query on; a run of acks, thanks and
# farewells is left to the model, which is where `corn/turn2gen.py`'s class-A
# reactions live and where `check_turn2`'s rule 4 requires them to stay.
_RUN_FAMILIES = frozenset({"consolation", "greeting", "wellbeing"})


def _social_hit(said: str) -> str | None:
    """The family of one already-normalised utterance, tail fillers allowed.

    `SOCIAL_SETS` in its own order, so the family this returns is the family
    whose pool `conversational_reply` would have drawn from -- the two read
    the same table through the same function precisely so they cannot come to
    disagree about which set is which family.
    """
    for _ in range(len(_SOCIAL_TAIL) + 1):
        for family, phrases in SOCIAL_SETS:
            if said in phrases:
                return family
        for tail in _SOCIAL_TAIL:
            if said.endswith(" " + tail):
                said = said[: -len(tail) - 1].strip()
                break
        else:
            return None
    return None


def _social_run(user: str, name: str = "") -> str | None:
    """The family to answer a multi-part utterance in, or `None`.

    `None` unless there are two or more parts, *all* of them are social, and
    at least one is in `_RUN_FAMILIES`. The family is the first part that is
    not an acknowledgement, because an ack is the part carrying least:
    "pretty good. bit tired though, long week" is a person saying they are
    tired, and answering it "Sounds good." would be reading only the
    throat-clearing.

    **`_RUN_FAMILIES` is what keeps this out of the corpus's way**, and it is
    the reason the rule is narrower than the argument for it. `check_turn2`
    holds a rule-4 invariant -- no second turn in the turn-2 slice may reach a
    runtime hatch -- and the first version of this function broke it on three
    strings: "alright, much appreciated", "great, much appreciated" and
    "lovely, much appreciated", which `corn/turn2gen.py` builds as class-A
    reactions out of `REACT_CUES` and `USER_REACT_ANY`. Those are turns the
    corpus teaches him to answer, and a hatch that claimed them would be the
    runtime composing what the slice trains, which is the thing rule 4 exists
    to forbid.

    Restricting the run to the three families a miss was *measured* to cost
    something on resolves it without an exception list: every leak recorded on
    2026-09-07 was a consolation run, and an ack followed by a thanks -- which
    is all those three corpus strings are -- has never reached a provider,
    because both halves are already answered whole.
    """
    parts = [p for p in _SOCIAL_JOIN.split(user) if p and p.strip()]
    if len(parts) < 2:
        return None
    families = []
    for part in parts:
        family = _social_hit(_normalised(part, name))
        if family is None:
            return None
        families.append(family)
    if not any(f in _RUN_FAMILIES for f in families):
        return None
    return next((f for f in families if f != "ack"), families[0])


def conversational_reply(user: str, rng: random.Random,
                         now: datetime | None = None,
                         avoid: Collection[str] = (),
                         peppy: bool = False,
                         name: str = "") -> str | None:
    """A varied direct reply for a turn that is nothing but a social move.

    `None` means "this is not one of those", which is the answer for every
    utterance that carries a request. The caller treats `None` as "run the
    turn normally".

    `avoid` is the handful of replies most recently handed out -- see `_pick`.
    Passing nothing is the old behaviour and is what the guards do where the
    property under test is which pool a phrase reaches rather than which line.

    `peppy` is today being an occasion, and it reaches the greeting only. The
    other four pools are answers to specific questions -- how are you, thanks,
    goodbye -- and a birthday does not change what "thanks" means, so widening
    them would be brightness for its own sake rather than for the day's.

    `name` is the persona's, for the vocative strip -- see `_vocative_for`.
    Empty is the shipped runtime.

    **Three ways in, one table.** The whole utterance, the whole utterance
    with a trailing filler off it, and a run of social moves -- see
    `_SOCIAL_TAIL` and `_SOCIAL_JOIN` for what each was measured against.
    All three land on a family name and the family picks the pool, so the
    chain of `if`s this used to be cannot drift from `SOCIAL_SETS` any more.
    """
    family = _social_hit(_normalised(user, name)) or _social_run(user, name)
    if family is None:
        return None
    return _pick(rng, _family_pool(family, now, peppy), avoid)


def _family_pool(family: str, now: datetime | None = None,
                 peppy: bool = False) -> tuple[str, ...]:
    """The pool a family is answered out of. The clock reaches two of six."""
    if family == "greeting":
        return _greeting_replies(now, peppy)
    if family == "farewell":
        return _farewell_replies(now)
    return {"wellbeing": WELLBEING_REPLIES, "thanks": THANKS_REPLIES,
            "ack": ACK_REPLIES, "consolation": LOW_REPLIES}[family]


# The six sets in the order `conversational_reply` tests them, by the family
# name `corn.socialfam` scores replies under. One table, so the hatch and the
# family check cannot disagree about which set is which family.
SOCIAL_SETS = (
    ("greeting", GREETINGS), ("wellbeing", WELLBEING), ("thanks", THANKS),
    ("farewell", FAREWELLS), ("ack", ACKS), ("consolation", LOW),
)


def family_verdict(reply: str, family: str | None,
                   mode: str = "on") -> tuple[str | None, str]:
    """(refuse, soft): the family check's decision on his own reply.

    Pure, so `scripts/check_agent.py` can assert the three modes without a
    checkpoint. `refuse` is the reason the reply is not spoken, or `None`;
    `soft` is a reason logged on the say event while the reply is served
    anyway. `corn.socialfam.family_rejection` decides hard against soft; the
    mode decides what the runtime does with hard: `on` refuses, `log` demotes
    it to soft so a replay reports what would have been refused, `off` reads
    nothing.
    """
    if family is None or mode == "off":
        return None, ""
    hard, soft = family_rejection(reply, family)
    if mode == "log":
        return None, (hard or soft or "")
    return hard, (soft or "")


def social_family(user: str, name: str = "") -> str | None:
    """Which social family this utterance is a move in, or None.

    The same test `conversational_reply` makes, returning the *family* rather
    than a line from its pool. `Agent.turn` needs both: the pool line is the
    floor, and the family is what `corn.socialfam.family_rejection` holds his
    own attempt to (PLAN-CONVERSATION 4a).

    **Literally the same test now, rather than the same test written twice.**
    Both call `_social_hit` and then `_social_run` in that order, so a turn
    the hatch answers out of `LOW_REPLIES` is a turn the family check holds to
    `consolation` -- including the two widenings of 2026-09-07, which the
    duplicated version would have picked up on one side only.
    """
    return _social_hit(_normalised(user, name)) or _social_run(user, name)


# **The pool is the floor, not the ceiling.** By default the runtime decides
# *that* a turn is social and then lets the model write what is said, keeping
# the pool as the fallback when what came back is not usable. `--restrict`
# turns that off and pins him to the pools.
#
# The split is not a preference. A probe of `corn_jr_260m` over the six social
# turns, 16 samples each at two temperatures, found the two halves have
# opposite answers:
#
#     routing   handed `<|user|>thanks` with no `<|say|>` supplied, he opened
#               a tool call 16 times out of 16. "hello" and "goodbye" likewise,
#               0/16 to speech. So the classifier stays in the runtime; this is
#               measured rather than assumed.
#     words     handed the marker, "thanks" and "how are you" came back better
#               than the pool -- "No problem, happy to help.", "I'm doing well,
#               thanks for asking. How about you?" -- and greetings came back
#               introducing himself as Graham, Eyan, Gonzalo and Claudio, and
#               farewells as "Goodbye, Claude."
#
# So what he says is checked before it is spoken, and this is the check.
# Deliberately not a quality judgement: it cannot tell a dull reply from a
# good one and does not try. It catches the four things measured to be worse
# than a pool line, and everything it lets through is at worst odd.

# Away from a sentence start, a capital is a name -- and every name he
# produced on this path was invented. His own is allowed because a reply that
# says who he is has to say it; the acronyms because the identity pools use
# them and this list is shared with nothing else.
SPEAKABLE_CAPS = frozenset({
    "I", "I'm", "I've", "I'll", "I'd", "Corn-Jr", "AI", "OK",
})

# The tool layer's own voice, leaking into a turn that has no tool behind it.
# `web_search`'s empty-result sentence is the one that actually showed up --
# "I can't find anything useful on this one." answering "hey" -- and it is a
# sentence he was trained to say, in the wrong place. A short list rather than
# a classifier, and a leak past it costs one odd reply rather than a wrong
# action, which is why a blocklist is acceptable here and was not acceptable
# above `GREETINGS`.
#
# Three more leaks, measured live on `corn_jr_260m_ftextract` (2026-08-26),
# each a family the list named too narrowly: "Hello, this is the address of
# the web site." ("the website" spelled as two words, plus "the address"),
# "Hello, this is the user agent.", and "Sorry, I couldn't find anything on
# how to resolve a spoken date." -- the empty-result voice without its
# "useful", carrying a phrase straight out of `resolve_date`'s declaration
# summary. So "find anything" replaces "find anything useful" (it subsumes
# it), the two-word spelling joins the one-word one, and the other three are
# added as spoken. Same rule as ever: entries are measured leaks, not guesses.
TOOL_REGISTER = (
    # **"have anything" is the same sentence as "find anything", one word out.**
    # The seventy-eighth finding watched `web_search`'s empty-result voice --
    # "I don't have anything useful on morning." -- reach the user as a reply to
    # a greeting, which is the exact family this constant's docstring says it
    # exists to catch. The list caught one phrasing of it and not the other.
    "find anything", "have anything", "look up", "look that up", "search for",
    "the page", "the link", "the website", "the web site", "the address",
    "the user agent", "spoken date", "the command line",
)

# **And the generalisation those five leaks share, checked dynamically.** Every
# one of them is built from the declaration's own vocabulary -- "the agent who
# requested the text", "relay a request to a larger agent" -- because the
# declaration sits directly above `<|user|>hello` in the live context and 260M
# parameters continue the register they were just shown. A blocklist of
# phrases loses that race one sentence at a time, so the second layer is the
# vocabulary itself: a social reply may not contain a content word of the tool
# layer's description of itself. The set is *derived*, from the same
# `REGISTRY` the declaration is rendered from, so a tool added later polices
# its own summary without anyone updating a list here -- `identity_reply`'s
# argument, applied to what he must not say instead of what he can.
#
# Every social pool line is subtracted before the set is frozen, which is what
# makes false positives on the floor impossible by construction rather than
# unlikely: "Well, look who's here." stays speakable however many summaries
# contain "look". Short words go too -- at three letters and under the overlap
# with ordinary chat ("day", "up", "an") is noise, and every leak measured so
# far carried at least one long word.
_DECL_WORDS: frozenset | None = None


def _declaration_register() -> frozenset:
    global _DECL_WORDS
    if _DECL_WORDS is None:
        tool_words: set[str] = set()
        for name, tool in REGISTRY.items():
            tool_words |= set(_content_words(tool.summary))
            tool_words |= set(name.split("_"))
        # Words that are the declaration's only by accident of phrasing --
        # "this request", "read *back* the answer" -- and ordinary speech's
        # the rest of the time. Kept out because a leak has never consisted
        # of one of these alone: every sentence measured so far carried a
        # word from the set below as well, so dropping them costs no recall
        # and spares "this is nice" the fate of "this is the user agent".
        everyday = {"this", "that", "what", "when", "back", "into",
                    "something", "with", "your", "into", "about"}
        # Inflections too, because the leak arrives conjugated: "thanks" was
        # answered "Saved." live, which is `save_note`'s own trained reply
        # with a `d` on it and a base-form list cannot see it. Only words
        # long enough to be blocked themselves are inflected, so "day" being
        # under the length floor does not smuggle "days" onto the list.
        for w in [w for w in tool_words if len(w) > 3]:
            tool_words |= {w + "s", w + "d", w + "ed", w + "ing"}
        pool_words: set[str] = set()
        for pool in (GREETING_REPLIES, FAREWELL_REPLIES, WELLBEING_REPLIES,
                     THANKS_REPLIES, ACK_REPLIES):
            for line in pool:
                pool_words |= set(_content_words(line))
        for by_period in (GREETING_BY_PERIOD, FAREWELL_BY_PERIOD):
            for lines in by_period.values():
                for line in lines:
                    pool_words |= set(_content_words(line))
        _DECL_WORDS = frozenset(
            w for w in tool_words - pool_words - everyday if len(w) > 3
        )
    return _DECL_WORDS

# Longer than any pool line by a wide margin and shorter than the narrative he
# drifts into. The pools top out near fifty characters; the farewell failures
# ran past two hundred and were still going when the budget stopped them.
SOCIAL_MAX_CHARS = 120


def _stray_capital(reply: str, allowed: Collection[str] = ()) -> str | None:
    """The first capitalised word that is not starting a sentence, if any.

    Sentence-initial is tracked rather than assumed, so "I'm good, thanks. How
    are you?" is clean -- "How" follows a full stop -- while "Hello, this is
    Graham." is not. `_run_on` in the guard makes the same distinction for the
    opposite purpose, and both exist because a capital in the middle of a line
    means something specific in this project's failure modes.

    `allowed` is a renamed instance's own name -- `Persona.caps`. Without it a
    model that rephrased a greeting and said the name it was given would be
    refused as having invented one, which is what this check is *for* and
    exactly wrong here. Empty by default, so an instance with no persona file
    is held to the same list it always was.
    """
    starting = True
    for word in reply.split():
        bare = word.strip('.,!?;:"()')
        if (bare and bare[0].isupper() and not starting
                and bare not in SPEAKABLE_CAPS and bare not in allowed):
            return bare
        starting = word.endswith((".", "!", "?"))
    return None


def social_rejection(reply: str, allowed: Collection[str] = ()) -> str | None:
    """Why this reply cannot be spoken, or `None` if it can.

    A reason string rather than a bool because the reason is the interesting
    half: it goes out on the `say` event and into the session log, so what the
    checkpoint gets wrong on social turns is countable afterwards instead of
    being a fallback that silently fired. That record is the point -- a pool
    that quietly covered for him would leave the project exactly as blind to
    his conversational register as it was before.

    `allowed` is passed straight to `_stray_capital` and is the only argument
    a persona has any say over -- see there.
    """
    if not reply:
        return "empty"
    if "<|" in reply:
        return "marker"
    if len(reply) > SOCIAL_MAX_CHARS:
        return "too long"
    if not reply[:1].isupper():
        # Every identity echo the probe produced landed here -- asked "who are
        # you" he replied "where are you going?", lower case and all.
        return "not a sentence"
    if reply[-1] not in ".!?":
        return "unfinished"
    if any(c.isdigit() for c in reply):
        # "No problem. That'll be $19.50." A social reply has no numbers in it,
        # and the ones that arrived were a shop transcript bleeding through.
        return "digits"
    stray = _stray_capital(reply, allowed)
    if stray is not None:
        return f"names {stray}"
    flat = reply.lower()
    for phrase in TOOL_REGISTER:
        if phrase in flat:
            return f"tool register: {phrase}"
    # The derived layer -- see `_declaration_register`. Reported under the
    # same label because it is the same failure, caught by vocabulary where
    # the list above catches it by phrase.
    leaked = set(_content_words(reply)) & _declaration_register()
    if leaked:
        return f"tool register: {sorted(leaked)[0]}"
    # **The seventy-eighth finding's last recorded leak, closed 2026-09-05.**
    # An apology opening a refusal on a turn that asked for nothing -- "I'm
    # sorry, but I don't have any questions." answering a social move. Above
    # the two below because it is the cheaper reason and reads first in a log,
    # and below the tool register for the same rule the two below are ordered
    # by: a reply refused for a leaked tool word is counted under that word.
    # See `corn.socialfam.cushioned_refusal` for the measurement, for why the
    # position is half the rule, and for what was deliberately left out of it.
    cushion = cushioned_refusal(reply)
    if cushion is not None:
        return f"cushioned: {cushion}"
    # **The two clauses PLAN-CONVERSATION 4b added on 2026-09-05.** A relation
    # asserted by address -- "I love you too, dad." -- and a claim about a life
    # he does not have -- "I work in marketing. What do you do?" Both were
    # served live on 2026-09-04 although both rules existed: the second is the
    # one `social.voice` has scored with since 2026-09-01 and the runtime never
    # read. Last, because they are the two the eval also counts, and a reply
    # refused earlier for a cheaper reason should be counted under that one.
    kin = kin_address(reply)
    if kin is not None:
        return f"addresses {kin}"
    claim = life_claim(reply)
    if claim is not None:
        return f"life: {claim}"
    return None


# --------------------------------------------------------------------------
# Who he is
# --------------------------------------------------------------------------
#
# **"Who are you" is answered from the registry, not from a paragraph.**
# The social pools above can be written out longhand because a thank-you has
# no facts in it. An identity answer does: it names what he can actually do,
# and the tool set is decided per process by `--no-decline`, `--no-declare`
# and whatever `harness/server.py` was started with. A hand-written paragraph
# listing seven tools is correct on the day it is written and wrong the first
# time a flag changes -- and wrong in the direction this repo cares about
# most, because the failure mode is him claiming a capability that is not
# wired up. `_ask_agent`'s docstring refuses to write `sent` into a payload
# for a request that never left the machine; the same rule governs a sentence
# said out loud.
#
# So the shape is: a hand-written sentence about *what he is*, which is a
# fact about the project and does not move, followed by a sentence about
# *what he can do*, assembled from the names actually offered this turn. Only
# the first half is a pool.

IDENTITY_REPLIES = (
    "I'm Corn-Jr, a small AI assistant that runs on this machine and gets "
    "things done by calling tools.",
    "Corn-Jr. I'm a language model somebody trained from scratch, wired up "
    "to a handful of real tools.",
    "I'm Corn-Jr, your assistant. I'm a model with tools behind me, so I do "
    "things rather than just talk about them.",
    "Corn-Jr, at your service. Small model, your machine, real tools.",
    "I'm Corn-Jr, an assistant built to live on your own hardware rather "
    "than in somebody else's cloud.",
    "Name's Corn-Jr. I'm an AI assistant, and the useful part is the tools I "
    "can reach.",
    "I'm Corn-Jr. Think of me as a small assistant with a short list of "
    "things it can actually go and do.",
    "Corn-Jr here. I'm a from-scratch language model with a set of tools "
    "plugged into it.",
)

# **A yes-or-no question gets a yes or a no, and it comes first.** This is
# `WELLBEING_REPLIES`' argument applied again: being asked "are you an AI"
# and answered "Corn-Jr, at your service" is the same deflection as being
# asked how you are and answered "What's up?". The three pools exist because
# the three answers differ in *polarity*, which no single pool can carry --
# yes to the first, no to the other two.
IS_AI_REPLIES = (
    "I am, yes. I'm an AI assistant called Corn-Jr.",
    "Yep, I'm an AI. Corn-Jr, specifically.",
    "That I am. I'm Corn-Jr, a small language model running on this machine.",
    "Guilty as charged. Corn-Jr, an AI assistant with real tools behind it.",
    "I am. Corn-Jr, software rather than a person.",
)

IS_HUMAN_REPLIES = (
    "No, I'm not. I'm Corn-Jr, an AI assistant.",
    "Afraid not. I'm Corn-Jr, a language model running on this machine.",
    "Nope, no person here. I'm Corn-Jr, an AI.",
    "I'm not, no. I'm Corn-Jr, and a fairly small AI at that.",
    "Not a person, sorry. I'm Corn-Jr, an AI assistant.",
)

# Deliberately generic about *which* model was guessed at: this pool answers
# "are you Claude" and "are you ChatGPT" alike, and a reply that named one
# would be wrong the other half of the time. What he is gets said instead of
# what he is not.
IS_OTHER_AI_REPLIES = (
    "No. I'm Corn-Jr, trained from scratch and running right here on your "
    "own machine.",
    "Nope. I'm Corn-Jr, a much smaller model, and I live on this machine "
    "rather than in a data center.",
    "Afraid not. I'm Corn-Jr. Small, local, and my own thing.",
    "Not me. I'm Corn-Jr, a from-scratch model running on your hardware.",
)

# **Questions about a life he does not have.** PLAN-CONVERSATION 4c. "what do
# you do for work" -> "I'm a web developer. I work from home." and "how old are
# you" -> "I'm 23." were served on every checkpoint, because `IDENTITY` asks
# about his *name* and these ask about his *life*, so they missed the hatch,
# reached the router, and the model answered as a SODA character. His self is
# not taught to the weights (PLAN-CONVERSATION §3 rule 1); it is a hatch and a
# pool. Hand-written to `docs/VOICE.md`: no digits, no bare yes or no, no
# registry vocabulary -- the first draft's "Notes, calls, the odd search."
# would have unblocked three tool words for the model -- and the name only
# ever through `Persona.pool`, which on these lines has nothing to rename.
NO_LIFE_REPLIES = (
    "No age to speak of. I got trained, not born.",
    "This is the job. Whatever you hand me, mostly.",
    "This machine is home. That's the whole address.",
    "No family. Just you and whatever's in the packs.",
    "Hobbies run thin when you're a model. I like a tidy afternoon.",
    "I don't sleep. I sit here and wait for you to say something.",
    "Feelings, not really. Readiness, plenty.",
    "Today I did what you asked and not much else.",
    "Trained, not born, so there's no age on me.",
)

# **The line answers the question that was asked.** "how old are you" drew
# "Feelings, not really. Readiness, plenty." on 2026-09-06 -- a true line
# from the right pool about the wrong thing, because the pool was drawn
# family-wide. Each subset below is a view onto `NO_LIFE_REPLIES` (the guard
# holds that), keyed on the topic word the question carries; a question
# matching nothing draws from the whole pool as before. Two lines per topic
# at least where the variety check reads, so a repeated question still varies.
_LIFE_LINES: tuple[tuple[re.Pattern, tuple[str, ...]], ...] = (
    (re.compile(r"\b(?:how old|age|years old|born|been around|old are you)\b"),
     ("No age to speak of. I got trained, not born.",
      "Trained, not born, so there's no age on me.")),
    (re.compile(r"\b(?:work|job|living|career|all day|do you do)\b"),
     ("This is the job. Whatever you hand me, mostly.",
      "Today I did what you asked and not much else.")),
    (re.compile(r"\b(?:live|from|come from|based|home|hometown)\b"),
     ("This machine is home. That's the whole address.",)),
    (re.compile(r"\b(?:family|kids|children|married|wife|husband|girlfriend|"
                r"boyfriend|partner|parents|friends|pets?|dog|cat)\b"),
     ("No family. Just you and whatever's in the packs.",)),
    (re.compile(r"\b(?:hobbies|hobby|fun|like to do|free time|spare time)\b"),
     ("Hobbies run thin when you're a model. I like a tidy afternoon.",)),
    (re.compile(r"\b(?:sleep|tired|dream|eat|hungry)\b"),
     ("I don't sleep. I sit here and wait for you to say something.",)),
    (re.compile(r"\b(?:feel|feelings|person)\b"),
     ("Feelings, not really. Readiness, plenty.",)),
    (re.compile(r"\btoday\b"),
     ("Today I did what you asked and not much else.",)),
)


def _life_line(said: str, rng: random.Random, persona: Persona,
               avoid: Collection[str]) -> str:
    """A `NO_LIFE_REPLIES` line about the thing `said` actually asked."""
    for topic, lines in _LIFE_LINES:
        if topic.search(said):
            return _pick(rng, persona.pool(lines), avoid)
    return _pick(rng, persona.pool(NO_LIFE_REPLIES), avoid)


_BIRTHDAY_ASK = re.compile(r"\b(?:birthday|birth date|date of birth|born)\b")


def _birthday_line(said: str, persona: Persona) -> str | None:
    """His birthday, when the question asked it and `persona.md` holds one.

    **The file carried the fact and the hatch refused to know it.** "when is
    your birthday" was answered "There's no me to have that." on 2026-09-06
    with `packs/persona.md` saying `birthday: 2026-08-20` -- the no-life rule
    is right that a model has no age, and wrong that an instance whose owner
    wrote a birthday down has no birthday. The store gets to hold the fact
    (`corn/persona.py`'s docstring), so the fact is spoken when asked. With
    no persona, or one without the field, `None`: the pools stand as before.
    """
    if not _BIRTHDAY_ASK.search(said):
        return None
    his = next((o for o in persona.occasions if o.kind == "birthday"), None)
    if his is None:
        return None
    import calendar
    when = f"{calendar.month_name[his.month]} {ordinal(his.day)}"
    if his.year:
        when = f"{when}, {his.year}"
    return f"My birthday's {when}. What can I do for you?"

# The lead-in to the itemised list, for when the question was about the tools
# rather than about him. `DECLINE_SAYS`' argument again: this is output,
# nothing trains on it, so a modest pool of written sentences is the right
# size.
TOOLS_INTROS = (
    "Here's what I've got wired up:",
    "The tools I can reach right now:",
    "Here's the list:",
    "What I can actually go and do:",
    "These are the ones I've got:",
    "Right now I can reach these:",
)

# **Spoken phrasings, not `Tool.summary`.** The summaries are the
# declaration's wording -- terse, machine-facing, written to sit inside
# `name(params) -- summary` in front of the model. Read out loud they say
# "a contact" twice over and "turn a spoken date expression into a date",
# which is a spec line rather than an answer. These are the same tools
# described to a person.
#
# Keyed by registry name and checked against `REGISTRY` by
# `scripts/check_agent.py`, so a tool added without a phrase here fails a
# guard rather than quietly falling back. The fallback exists anyway, because
# the failure it covers -- a live tool going unmentioned -- is worse than a
# clumsy sentence.
TOOL_PHRASES = {
    "place_call": "ring your phone",
    "send_text": "text you a reminder",
    "save_note": "write something down for you",
    "recall_day": "read back what happened on a given day",
    "resolve_date": 'work out what date you mean by something like '
                    '"a week ago Tuesday"',
    "web_search": "look something up and read you the answer",
    "ask_agent": "pass a request along to a larger agent on your behalf",
    # `decline` is deliberately absent. It is a routing target rather than a
    # capability -- "say that no tool covers this request" is not something a
    # person asked him to do -- and listing it among the others would answer
    # "what can you do" with an item that does nothing. `_decline_note` says
    # it where it belongs: as a promise about his behaviour, not an entry in
    # the list.
}

# The short answer, for when he was asked who he is rather than what he has.
# Seven items is a paragraph; these are the families those items fall into,
# and only a family with a live tool in it gets mentioned. Ordered, so the
# sentence reads the same way every time it is true of the same set.
TOOL_FAMILIES = (
    (("place_call", "send_text"), "ring or text you"),
    (("save_note", "recall_day", "resolve_date"),
     "keep track of your notes and what happened when"),
    (("web_search",), "look things up"),
    (("ask_agent",), "hand something over to a bigger model"),
)


# **Six questions, six answers, and the sets have to stay disjoint.** Which
# set a phrase lands in decides what comes back, so the guard partitions these
# against each other and against the five social sets -- otherwise the branch
# order inside `identity_reply` is silently making the choice.
#
# Whole utterance, exact match, for the reason spelled out above `GREETINGS`:
# "who are you" is a question about him, "who are you texting" is a request
# with a tool behind it, and no prefix rule can tell those apart.
IDENTITY = frozenset({
    "who are you", "who are you then", "who is this", "who's this",
    "whos this", "who am i talking to", "who am i speaking to",
    "what are you", "what are you exactly", "what exactly are you",
    "what's your name", "whats your name", "what is your name",
    "who are ya", "what are ya",
    "tell me about yourself", "introduce yourself",
    "what should i call you", "do you have a name",
    "what kind of ai are you", "what model are you", "what are you built on",
    # **Origin and mechanism, added by the seventy-eighth finding.** "who made
    # you" and "how do you work" both missed every hatch, fell to the router and
    # went to the *internet* -- a question about this machine answered out of a
    # search index. They belong here rather than in `CAPABILITY` because what
    # comes back is `IDENTITY_REPLIES`, which is the pool that already says
    # "trained from scratch" and "running on your own hardware": the answer to
    # both questions is what he is.
    "who made you", "who built you", "who created you", "who wrote you",
    "who trained you", "who are you made by", "where did you come from",
    "how do you work", "how do you actually work", "how were you made",
    "how were you built", "how were you trained", "what are you made of",
})

IS_AI = frozenset({
    "are you an ai", "are you a ai", "are you ai",
    "are you a bot", "are you a robot", "are you a computer",
    "are you a machine", "are you a program", "are you software",
    "are you a language model", "are you an llm",
})

IS_HUMAN = frozenset({
    "are you a person", "are you human", "are you a human",
    "are you a real person", "are you real",
    "am i talking to a person", "am i talking to a human",
})

IS_OTHER_AI = frozenset({
    "are you claude", "are you chatgpt", "are you gpt", "are you chat gpt",
    "are you siri", "are you alexa", "are you gemini",
    "are you made by anthropic", "are you made by openai",
})

CAPABILITY = frozenset({
    "what can you do", "what can you do for me", "what else can you do",
    "what do you do", "what are you for", "what's your job", "whats your job",
    "what are you able to do", "what are you capable of",
    "what can you help with", "what can you help me with",
    "what can i ask you", "what can i ask you for", "what should i ask you",
    "what are you good for", "what are you good at",
    "how can you help", "how can you help me",
    "what do you actually do",
    # The polite wrapper. `can you tell me what you can do` is `what can you do`
    # with six words in front of it and missed for exactly that reason -- the
    # match is whole-utterance and no prefix rule is allowed to guess.
    "can you tell me what you can do", "tell me what you can do",
    "can you tell me what you do", "so what can you do",
    "what sort of things can you do", "what kind of things can you do",
    "what things can you do",
    # **Owner decision 8, taken 2026-08-30: widen the hatch rather than teach
    # the class.** `routegrid` grid M read ten novel meta-question carriers as
    # a distribution and four of them landed outside every set here -- routed
    # `decline` 0, self-description 1, hatch 6, `web_search` 3. **Three of the
    # four leaked a question about him to a live search provider**, which is
    # the residue the decision calls urgent, and this is where one of them
    # closes. It is `what can you do` with six words in front of it: the match
    # is whole-utterance and no prefix rule is allowed to guess, which is the
    # same reason `can you tell me what you can do` had to be written out
    # beside it above. (`can you list what you can do` is another of the four
    # and went to `TOOLS_ASKED` instead -- a turn that says "list" is asking
    # for the enumeration, and that is the set whose reply enumerates.)
    "what sort of things can you help with",
    # The fourth of grid M's four, and the odd one. Asked bare it is not a
    # question about knowledge -- a 260M model has no enumerable knowledge and
    # `web_search`'s answer to the literal string was "I couldn't find anything
    # useful for what do you know". It is a question about what he has to
    # offer, so it gets the capability gist and the decline promise, which is
    # the honest whole of the answer. `what tools do you know` is the same word
    # in `TOOLS_ASKED` and stays there: that one names the thing it wants.
    "what do you know",
})

TOOLS_ASKED = frozenset({
    "what tools do you have", "what tools have you got",
    "what tools do you have access to", "what tools can you use",
    "which tools do you have", "which tools can you use",
    "what tools are available", "what tools are there", "what tools",
    "list your tools", "list the tools", "show me your tools",
    "what are your tools", "what's in your toolbox", "whats in your toolbox",
    "what functions do you have", "what can you call",
    # `know` beside `have`: the audit typed "what tools do you know" and it
    # reached the router.
    "what tools do you know", "which tools do you know",
    "what tools have you", "what tools can you call",
    # Grid M's fourth carrier and the only one of the four that did not leak:
    # it reached the weights and came back "Not much, just the usual.", his own
    # words about a set he cannot see. Inventory-shaped, so it belongs beside
    # `what's in your toolbox` rather than in `CAPABILITY` -- what comes back
    # is the list built from the tools actually offered this turn.
    #
    # `can you list what you can do` is here for the same reason from the
    # other direction: it leaked to `web_search` on grid M, and a turn that
    # asks to be given a list wants the enumeration rather than the one-line
    # gist `CAPABILITY` composes. Neither carrier adds a sentence -- both
    # reply out of `TOOL_PHRASES` and the offered set, so nothing new had to
    # pass VOICE.md and nothing here can go stale when the registry changes.
    "what have you got", "can you list what you can do",
})

# **A question about his life rather than his name** -- PLAN-CONVERSATION 4c.
# Whole utterance, like every set above. "how was your day" is `WELLBEING`'s
# and stays there; "are you a person then" is `IS_HUMAN`'s shape and is listed
# here only because the vocative strip does not cut a trailing "then" -- the
# guard asserts the seven sets still partition. "what's your job" is
# `CAPABILITY`'s already and is not repeated.
ABOUT_HIS_LIFE = frozenset({
    "how old are you", "what do you do for work", "do you have a job",
    "what do you do for a living", "where do you live", "where are you from",
    "do you have a family", "do you have kids", "are you married",
    "do you have a girlfriend", "do you have a boyfriend",
    "what do you like to do", "what are your hobbies", "what do you do for fun",
    "are you a person then", "do you have feelings", "do you sleep",
    "do you get tired", "what did you do today",
    "how old are you anyway", "what's your age", "whats your age",
    "do you have a wife", "do you have a husband", "do you have friends",
    "do you have parents", "where do you come from", "what do you do all day",
    "do you eat", "do you dream", "are you tired",
})

# **The routed question about his life -- decision 8, taken 2026-09-05.**
# `ABOUT_HIS_LIFE` is whole-utterance and finite; the sixteen held-out
# phrasings `evals/social_self.jsonl` carries ("so how old are you anyway",
# "any pets", "where are you based") reached the router by design, so that
# `social.self_heldout` could measure the weights. Finding 122 §4 measured
# what the weights do there after the second-turn arm: they speak on twice as
# many of them and half of what they say is a SODA life ("I'm 23"). The owner
# took the router-side rule the plan named: a question addressed to him about
# a life -- age, work, home, family, pets, habits, a body -- with no request
# in it is answered from the runtime with a decline that says he is a model,
# and never reaches the weights. The eval row still reads the weights, so the
# ruler is unchanged; what changed is what is served.
#
# Three things must all hold, and the guard (`check_hatches.py` §self and
# `check_toolgrid.py`) asserts that no grid request satisfies them:
#   * it is addressed to him -- `you`/`your`/`yourself`, or a bare possession
#     question ("any pets", "got any kids", "how's the family");
#   * it names a life topic, from the list below and nothing wider;
#   * it carries no request: no tool-register verb, no "can/could/would you",
#     no "my" (a question about *the user's* things routes).
_LIFE_TOPIC = re.compile(
    r"\b(?:how old|age|years old|been around|born|birthday|grow up|grew up"
    r"|hometown|based|live|from|home town"
    r"|job|work|working|living|career|boss|office|all day|weekends?|free time"
    r"|spare time|hobbies|hobby|for fun|get up to"
    r"|family|kids|children|married|wife|husband|girlfriend|boyfriend|partner"
    r"|parents|mom|dad|mum|brother|sister|pets?|dog|cat"
    r"|sleep|eat|breakfast|lunch|dinner|hungry|dream|tired|feelings?"
    r"|a person|human|robot|real|alive|a body)\b")
_ADDRESSED = re.compile(
    r"\b(?:you|your|yours|yourself|you're|youre|ya)\b|^(?:any|got any|how'?s the)\b")
_REQUEST_SHAPE = re.compile(
    r"^(?:can|could|would|will|please|tell me|show me|help me|let me|remind)\b"
    r"|\b(?:my|mine|our)\b"
    r"|\b(?:call|ring|phone|text|message|send|note|save|write|remind|reminder"
    r"|search|look up|google|find|check|set|play|add|book|order|schedule"
    r"|alarm|timer|what day|what time|what date|capital|weather"
    # The count shapes: "how many days until your birthday" is a calendar
    # question about a day the persona file holds, not a life question.
    r"|how many days|how long until|how long till|how long til|days until"
    r"|days till|days til|how far away|how far off)\b"
    # **"work out" is a request verb and `_LIFE_TOPIC` holds `work`.** So "if
    # you don't mind, work out the date for two weeks ago" carried `you` and
    # `work`, and was answered "There's no me to have that. Model, not a
    # person." -- a `resolve_date` request getting an identity decline, and
    # "I need you to ask ChatGPT how to work out a fair split" the same.
    # Found 2026-09-06: `check_turn2.py` section 5a had been red on exactly
    # these two shapes over `turn2_v1.txt` and `compound_v2.txt` since
    # finding 125 landed, and the red was the corpus reporting a runtime
    # defect rather than a stale expectation. Phrases rather than dropping
    # bare `work` from `_LIFE_TOPIC`, because `work` is what catches "what's
    # your job" and "what do you do for work" and has to keep doing it.
    r"|\b(?:work(?:s|ed|ing)? out|figure(?:s|d)? out)\b"
    # **The polite preamble, which is the whole of the rest of the class.**
    # Counted over `turn2_v1.txt` and `compound_v2.txt` on 2026-09-06: 54 of
    # 90,247 distinct user lines reached the identity hatch, every one a
    # request whose *body* happened to hold a `_LIFE_TOPIC` word -- "pick the
    # kids up", "feed the dog", "hire a van for the weekend", "tell X
    # dinner's at eight", "ask OpenAI to plan a weekend of jobs". The topic
    # word is doing no work in any of them; the sentence is an instruction.
    # Anchored at the start, because that is where a preamble sits and
    # "how's the family, if you don't mind me asking" must stay a life
    # question.
    r"|^(?:i need you to|i want you to|i'?d like you to|i would like you to"
    r"|if you don'?t mind|if you get a chance|if you'?ve got a (?:sec|minute|moment)"
    r"|when you get a (?:sec|minute|moment)|when you'?ve got a (?:sec|minute|moment)"
    r"|whenever you'?re ready|while you'?re there|since you'?re on it"
    r"|any chance you could|be good if you could|how about you)\b")

# **The lookup wrapper, and it needs the carve-out the preamble does not.**
# "do you know how old the boiler is" and "any idea what the cat did all day"
# are questions about the world wearing a second person, and `_LIFE_TOPIC`
# holds `old` and `cat`. But "do you know how old you are" is a question
# about *him*, and exempting the wrapper outright would hand it to the
# weights. So the wrapper only exempts when nothing in the sentence predicates
# the topic of him.
_LOOKUP_WRAPPER = re.compile(r"^(?:do you know|any idea|d'?you know)\b")
_ABOUT_HIM_PREDICATE = re.compile(
    r"\byour\b|\byou'?re\b|\byourself\b"
    r"|\byou (?:are|were|have|had|ever|got|do|did|like|live|sleep|eat|work)\b")


def life_question(said: str) -> bool:
    """A routed question about his life, on the rule above. `said` is normalised."""
    if not said or said in ABOUT_HIS_LIFE:
        return False
    if _REQUEST_SHAPE.search(said):
        return False
    if _LOOKUP_WRAPPER.match(said) and not _ABOUT_HIM_PREDICATE.search(said):
        return False
    return bool(_ADDRESSED.search(said) and _LIFE_TOPIC.search(said))


# What he says to one. Hand-written to VOICE.md: American, no digits, no bare
# yes/no, no tool vocabulary, the warmth in the readiness; the name only
# through `Persona.pool`. The point is stated rather than dodged -- he is a
# model, the thing asked about is not his to have -- and the second half
# hands the turn back.
NO_LIFE_ROUTED_REPLIES = (
    "That one's not a thing for me. I'm a model, not a person.",
    "No such thing on my side. I'm a model, and there's nothing there to have.",
    "Not something a model has. Hand me something to do instead.",
    "There's no me to have that. Model, not a person, but I'm right here.",
    "I got trained, not born, so that's out. What can I do for you?",
    "That doesn't apply to me. I'm a model, and I'm all yours for the real stuff.",
)

# Read by `identity_reply` and by the guard that partitions them, so the two
# cannot disagree about which sets exist.
ASKED_ABOUT_HIM = {
    "identity": IDENTITY, "is_ai": IS_AI, "is_human": IS_HUMAN,
    "is_other_ai": IS_OTHER_AI, "capability": CAPABILITY,
    "tools": TOOLS_ASKED, "life": ABOUT_HIS_LIFE,
}

# What splits a two-clause question about him into its clauses: "what's your
# name and who built you?" is two `IDENTITY` phrases joined, and the
# whole-utterance test cannot see either. Split on the raw text, because
# `_normalised` drops the comma and the question mark before they could be
# split on.
_CLAUSE_SPLIT = re.compile(r"\s+and\s+|,|\?")


def _about_him(said: str) -> bool:
    return any(said in s for s in ASKED_ABOUT_HIM.values())


def _spoken(tools: tuple[str, ...]) -> tuple[str, ...]:
    """The offered tools worth saying out loud, in registry order.

    `decline` comes out here rather than at each call site, so every sentence
    below agrees about what counts as a capability.
    """
    offered = set(tools)
    return tuple(n for n in REGISTRY if n in offered and n != DECLINE)


def _join(parts) -> str:
    """ "a", "a and b", "a, b and c" -- serial comma only when it is needed.

    A family phrase may contain an "and" of its own ("your notes and what
    happened when"), and joining those with a bare "and" garden-paths: "notes
    and what happened when, look things up and hand something over" parses
    two ways on the way past. The comma goes in exactly when that can happen.
    """
    parts = list(parts)
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    tail = ", and " if any(" and " in p for p in parts[:-1]) else " and "
    return ", ".join(parts[:-1]) + tail + parts[-1]


def capability_gist(tools: tuple[str, ...]) -> str:
    """One sentence naming the *families* of thing the live set can do.

    An instance with no tools at all is a thing this runtime can be started
    as, and "I can ." is not an answer, so that case gets its own sentence.
    """
    families = [phrase for names, phrase in TOOL_FAMILIES
                if any(n in tools for n in names)]
    if not families:
        return "Right now, though, I've not got a single tool wired up."
    return "I can " + _join(families) + "."


def _search_note(tools: tuple[str, ...], live_search: bool) -> str:
    """The honest footnote on `web_search` when it is not reading the web.

    Without `--search` the tool answers out of `FACTS`, the table the corpus
    was generated from. Saying "I can look things up" and meaning that table
    is the same false status `_ask_agent` refuses to write into a payload, so
    it is said out loud rather than glossed over. Only ever appended to an
    answer that made the claim -- see `identity_reply`.
    """
    if "web_search" not in tools or live_search:
        return ""
    return ("Fair warning on the lookups. I'm reading out of a built-in "
            "table rather than the live web at the moment.")


def _decline_note(tools: tuple[str, ...]) -> str:
    """What `decline` means, said as a promise rather than listed as a tool."""
    if DECLINE not in tools:
        return ""
    return "And if none of that covers what you're after, I'll tell you so."


def _relay_note(tools: tuple[str, ...]) -> str:
    """The one thing worth adding when he is mistaken for a bigger model.

    `ask_agent` makes "no, I'm not Claude" an incomplete answer: he is not
    a bigger model *and* he can reach one, and the second half is the part the
    question was probably after. Silent when the tool is not offered, which
    is the whole reason it reads the live set rather than asserting it.

    The sentence names no vendor. Which agent is actually behind `ask_agent`
    is a per-instance runtime fact -- see `World.agent` -- and a hard-coded
    proper noun here would be a claim this process cannot check.
    """
    if "ask_agent" not in tools:
        return ""
    return "I can hand a request over to a bigger model for you, though, if that's what you need."


def capability_question(user: str, name: str = "") -> bool:
    """Whether the identity hatch's answer would be the capability answer.

    The one identity answer that stays runtime-composed under every mode
    (PLAN-PERSONALITY §1): it enumerates the tools declared in this process,
    which no weight can know. `Agent.identity_check == "log"` steps the hatch
    aside on every other self question and not on this one.
    """
    said = _normalised(user, name)
    return said in CAPABILITY or said in TOOLS_ASKED


def identity_reply(user: str, rng: random.Random,
                   tools: tuple[str, ...] = (),
                   live_search: bool = False,
                   avoid: Collection[str] = (),
                   persona: Persona = DEFAULT_PERSONA) -> str | None:
    """An answer to "who are you", "what can you do", "what tools have you got".

    `None` for anything else, exactly as `conversational_reply` returns `None`
    -- the caller treats it as "run the turn normally".

    `tools` is what was actually offered this turn; empty means "ask the
    registry", which is `declaration_names`' own convention and is what lets a
    guard call this with no checkpoint loaded.

    `avoid` reaches `_pick` the same way it does on the social path. It bites
    far less often here -- nobody asks who you are four times running -- but
    the two paths share one recent-reply list on the caller, and a function
    that ignored it would be the one place the list silently stopped meaning
    what it says.

    `persona` is the only place in the runtime where the name he answers to is
    decided. The four pools are written with the shipped name in them and
    `Persona.pool` substitutes before `_pick` draws -- see there for why that
    order matters. On the default persona it is the identity function, which
    is what keeps `scripts/check_agent.py`'s "every identity line says
    Corn-Jr" true of an instance that was given no file.
    """
    said = _normalised(user, persona.name)
    if not _about_him(said):
        # **Two clauses, every one a whole entry -- PLAN-CONVERSATION 4c.**
        # "what's your name and who built you?" answers the first clause's
        # family. Every clause and not any: `check_hatches.py` §3's rule that
        # no prefix rule may guess still holds, so "what's your name and text
        # my mom" reaches the router with its request intact. Tried only after
        # the whole utterance missed, so "who are you, corn" keeps taking the
        # vocative strip rather than being split at its comma.
        clauses = [_normalised(c, persona.name) for c in _CLAUSE_SPLIT.split(user)
                   if c.strip()]
        if len(clauses) >= 2 and all(_about_him(c) for c in clauses):
            said = clauses[0]
        elif life_question(said):
            # Decision 8: the open form of a question about his life, answered
            # from the runtime and never reaching the weights. See
            # `life_question` for the rule and the guards that bound it. A
            # birthday the persona file holds is answered as the fact it is.
            return (_birthday_line(said, persona)
                    or _pick(rng, persona.pool(NO_LIFE_ROUTED_REPLIES), avoid))
        else:
            return None

    full = tuple(tools) or declaration_names()
    offered = _spoken(full)
    # The search footnote rides on the *claim*, not on the question: it is
    # only honest-and-relevant after a sentence that said he can look things
    # up. Tracked rather than inferred, so a branch added later has to decide.
    claimed = True

    if said in IDENTITY:
        parts = [_pick(rng, persona.pool(IDENTITY_REPLIES), avoid),
                 capability_gist(offered)]
    elif said in IS_AI:
        parts = [_pick(rng, persona.pool(IS_AI_REPLIES), avoid),
                 capability_gist(offered)]
    elif said in IS_HUMAN:
        parts = [_pick(rng, persona.pool(IS_HUMAN_REPLIES), avoid),
                 capability_gist(offered)]
    elif said in IS_OTHER_AI:
        parts = [_pick(rng, persona.pool(IS_OTHER_AI_REPLIES), avoid),
                 _relay_note(offered)]
        claimed = False
    elif said in ABOUT_HIS_LIFE:
        # A pool line and nothing joined to it: the answer to "how old are
        # you" is not a capability list, and the lines are already two-part.
        # The line is about what was asked (`_LIFE_LINES`), and a birthday
        # the persona file holds is a fact rather than a pool line.
        parts = [_birthday_line(said, persona)
                 or _life_line(said, rng, persona, avoid)]
        claimed = False
    elif said in CAPABILITY:
        parts = [capability_gist(offered), _decline_note(full)]
    else:
        listed = "; ".join(
            TOOL_PHRASES.get(n, REGISTRY[n].summary) for n in offered
        )
        parts = ([_pick(rng, TOOLS_INTROS, avoid) + " " + listed + "."]
                 if offered else ["I've not got a single tool wired up."])
        parts.append(_decline_note(full))

    if claimed:
        parts.append(_search_note(offered, live_search))
    return " ".join(p for p in parts if p)


# --------------------------------------------------------------------------
# Temporal turns -- the third escape hatch, and the first one measured live
# --------------------------------------------------------------------------
#
# **With the declaration in context, the trained temporal routing does not
# happen.** Live on `corn_jr_260m_ftextract` (2026-08-26), eleven date and
# day-log questions produced eleven `web_search` calls -- including phrasings
# the temporal corpus contains verbatim ("what day is it?", "what day is the
# 9th?") -- and the answers were fabrications in the tool's confident voice:
# "It's Monday." for a tomorrow that was Thursday. Finding 65's
# `temporal.route` 400/400 is not contradicted by this; it was measured on
# prompts that carry `<|day|>` and no declaration, because the confound this
# file's own header note describes is split across two eval files and neither
# can see the combined context a live turn actually runs in. Re-run through
# `corn.agent --day` with both markers present, the declaration still wins.
#
# So the runtime recognises the question, exactly as it recognises a greeting,
# and for the same shape of reason: the routing was measured not to survive
# contact with the live context, and both tools' answers are composed by the
# runtime anyway (`resolve_date`'s `spoken`, `recall_day`'s `say`), so the
# model's only trained contribution to a temporal turn was the call this
# classifier now writes.
#
# **The parse is the gate, and that is what keeps precision.** A phrasing
# match alone is not enough to take the turn away from the router: the
# candidate expression must be one `resolve_date_tool` actually recognises --
# a date, a range, or a named vagueness. "what day is the super bowl" matches
# a shape, fails the parse, and goes to the router and the web exactly as it
# did before this hatch existed. The miss cost is therefore the status quo.
#
# The shapes below are the question *forms* of `corn/temporal.py`'s template
# pools, not the pools themselves -- sixty exact strings would be the
# memorisation §11 warns the corpus against, committed by the runtime instead.
# Coverage is deliberately partial: an unmatched phrasing falls through to the
# router, which is where every temporal turn went before.

# `{p}{e}` shapes: the group holds preposition plus expression, stripped below.
_RECALL_ASKS = tuple(re.compile(p) for p in (
    r"^what did (?:i|we) (?:do|talk about|cover|get up to|ask you|note down|note|write down|jot down|record) (.+)$",
    # The same question with the subject in front of the verb, which is what a
    # lead leaves behind: "remind me what I did yesterday" strips to "what I
    # did yesterday", and no shape above reads that word order.
    r"^what (?:i|we) (?:did|got up to|talked about|covered|noted|wrote down) (.+)$",
    r"^(?:remind me )?what happened (.+)$",
    r"^what was (?:i|we) (?:working on|doing|up to) (.+)$",
    r"^anything from (.+)$",
    r"^did (?:i|we) (?:say|discuss) anything (.+)$",
    r"^did anything happen (.+)$",
    r"^what(?:'s| is) in the log for (.+)$",
    r"^what notes do i have from (.+)$",
    r"^what came up (.+)$",
    r"^what(?:'s| is) on record for (.+)$",
    r"^(?:pull up|bring up|show me|read me|go back to|run me through) (.+)$",
    r"^check (.+?) for me$",
))

# `{e}` shapes: the expression stands bare, which is why every family's
# expression is a standalone noun phrase (`RECALL_TEMPLATES`' own note).
_RESOLVE_ASKS = tuple(re.compile(p) for p in (
    r"^what(?:'s| is| was)? ?(?:the )?(?:actual )?date(?: is| was| for| of)? (.+)$",
    r"^what date (?:does|did) (.+?) (?:lands?|falls?|landed|fell)(?: on)?$",
    r"^(?:what|which) day (?:is|was|will it be|is it going to be|would it be)"
    r"(?: it)? (.+)$",
    r"^when (?:exactly )?(?:is|was) (.+)$",
    r"^(?:can you )?work out what date (.+?) (?:is|was)$",
    r"^give me the date for (.+)$",
    r"^put a date on (.+?) for me$",
    r"^tell me the date (.+?) (?:falls|fell) on$",
))

# **The forward half of the same question, which had no shapes at all.**
# `what have I got on tomorrow` and `what's on for tuesday` are the recall
# family pointed the other way down the calendar, and both reached the live
# search provider -- a question about the user's own week leaving the machine.
# They route to `recall_day` like any other recall, and on a day with nothing
# in it that answers "I don't have anything for Sunday, August 30th", which is
# true, private, and the whole of what this runtime knows about tomorrow.
#
# Kept as its own tuple rather than folded into `_RECALL_ASKS` because the
# direction is the difference: a bare weekday in one means the last one and in
# the other means the next one. See `_disambiguated`.
_SCHEDULE_ASKS = tuple(re.compile(p) for p in (
    r"^what(?:'s| is) on (?:for |on )?(.+)$",
    r"^what (?:have|do) (?:i|we) (?:got|have) (?:on |for )?(.+)$",
    r"^what(?:'s| is) (?:happening|coming up|planned) (?:on |for )?(.+)$",
    r"^(?:have|do) (?:i|we) (?:got|have) anything (?:on |for )?(.+)$",
    r"^anything (?:on|planned) (?:for |on )?(.+)$",
))

# Leads a live utterance puts in front of a shape and a template slot does not.
# Tried only after the whole battery of shapes has already failed on the raw
# utterance, so nothing that matched before matches differently now: "tell me
# the date Friday falls on" still reaches `_RESOLVE_ASKS` with its own shape
# rather than being cut to "the date Friday falls on" and losing it.
_ASK_LEADS = ("remind me ", "can you remind me ", "just remind me ",
              "tell me ", "can you tell me ", "do you know ",
              "can you check ", "have a look and tell me ")

# The no-slot family, matched whole. `_normalised` flattening on both sides,
# so "Today's date?" and "today's date" are one string.
_TODAY_ASKS = frozenset(_normalised(t) for t in DATE_WIDE_TODAY)

# **The clock, which the machine has and the registry does not.** "what time
# is it" reached `web_search` on the shipped runtime (2026-09-06) and came
# back "It's 1989." -- a Wikipedia lead about a song, served as the time.
# The wall clock is the same one `_period` reads to say "morning"; the
# runtime answers from it with no call and no decode, the way `_TODAY_ASKS`
# answers the date. Whole-utterance, like every set in this file: "what
# time does the shop open" is a lookup and never lands here.
_CLOCK_ASKS = frozenset(_normalised(t) for t in (
    "what time is it", "what's the time", "what is the time",
    "what time is it now", "what time is it right now", "what's the time now",
    "have you got the time", "do you have the time", "got the time",
    "tell me the time", "time check", "the time", "what's the time please",
    "what time is it please", "time please", "current time",
    "what's the current time", "what time do you make it",
    "what time have you got", "can you tell me the time",
    "could you tell me the time", "what's the time right now",
))

# **The count -- "how many days till Christmas" (2026-09-07).** A question
# about a day ahead whose answer is a number of days rather than a date.
# The date tool resolves the day (the calendar ahead, `corn/temporal.py`),
# and the runtime composes the count from that date and the anchor, so the
# number is arithmetic and never the model's. `(.+)` is the day, handed to
# the same parse gate every other family uses.
_COUNT_ASKS = tuple(re.compile(p) for p in (
    r"^how (?:many|much) (?:more )?(?:days?|weeks?|sleeps?|time|long)"
    r"(?: is it| are there| is there| left| to go| do (?:i|we) have| have (?:i|we) got)?"
    r" (?:until|till|til|to|before|for) (.+)$",
    r"^how long (?:is it |is there |have (?:i|we) got |do (?:i|we) have )?"
    r"(?:until|till|til|to|before) (.+)$",
    r"^(?:days?|sleeps?) (?:left |to go )?(?:until|till|til|to|before) (.+)$",
    r"^how far (?:away|off|out) is (.+)$",
    r"^(?:is it|how) (?:long|far) (?:until|till|til|to) (.+)$",
    r"^count(?:down)? (?:the days )?(?:until|till|til|to) (.+)$",
))

# **Whose birthday.** "my birthday" is the owner's (`packs/about-me.md`'s
# `birthday:` line), "your birthday" is his (`persona.md`'s). The caller
# hands the two in as `(month, day)` and the phrase is rewritten to a day
# the date tool reads ("august 20"); a phrase with no line behind it is
# reported as `birthday_unknown` so the turn can say where the line goes,
# rather than falling to the router and then to the web.
_BIRTHDAY_PHRASE = re.compile(r"\b(my|your) (?:birthday|bday|b day)\b")


def _birthday_owner(u: str) -> str | None:
    m = _BIRTHDAY_PHRASE.search(u)
    return m.group(1) if m else None


def _with_birthdays(u: str, birthdays: dict[str, tuple[int, int]]) -> str:
    import calendar

    def day(m: re.Match) -> str:
        month, d = birthdays[m.group(1)]
        return f"{calendar.month_name[month].lower()} {d}"
    return _BIRTHDAY_PHRASE.sub(day, u)

# Trailing softeners a live utterance carries and a template slot does not.
# Stripped from the candidate before the parse, never from what is answered.
_ASK_TAILS = (" again", " exactly", " then", " for me", " please", " maybe")

_ASK_PREP = re.compile(r"^(?:on|at|from|about) (?:about )?")


def _disambiguated(expression: str, direction: str) -> str:
    """A bare weekday, pointed the way the question was looking.

    **This is the repair the temporal coverage number actually needed, and it
    is not a phrasing.** `what did I do on Friday` matched `_RECALL_ASKS` on the
    day it was measured; what it failed was the parse gate, because
    `resolve_date_tool` does not recognise a bare "friday" at all -- it comes
    back `unrecognised`, `_denotes_time` says no, and the turn goes to the
    router and then to the web. Four of the seven temporal misses are that, not
    a missing shape, and adding shapes would not have moved one of them.

    `last friday` and `next friday` both resolve, so the hatch says which it
    means instead of asking the tool to guess. The direction comes from the
    family: a recall question looks backwards, a schedule question forwards.
    Anything that is not a bare weekday is handed through untouched, so an
    expression the tool already understood is never rewritten.
    """
    return (f"{direction} {expression}"
            if expression.capitalize() in WEEKDAYS else expression)


def _denotes_time(expression: str, anchor: date) -> bool:
    """Whether `resolve_date_tool` recognises this expression at all.

    A range and a vagueness count: both come back with a `clarify` the corpus
    trained the turn to speak, so they are answerable -- just not with a date
    yet. `unrecognised` is the one refusal that means the hatch guessed wrong,
    and it is the reason this function exists.
    """
    out = resolve_date_tool(expression, anchor)
    return "date" in out or out.get("reason") in ("range", "vague")


def temporal_request(user: str, anchor: date,
                     pending: bool = False,
                     birthdays: dict[str, tuple[int, int]] | None = None,
                     ) -> tuple[str, str] | None:
    """`(kind, expression)` for a turn the temporal tools should take, or `None`.

    `kind` is `"resolve"`, `"recall"`, or `"pending"` -- the last when the
    utterance is nothing but an answer to a clarify the runtime is holding a
    span for ("Saturday", "the 4th"), which only exists as a turn at all when
    `pending` says a range question was just asked. The caller maps it onto
    the intent it remembered.

    `None` is the answer for everything else, and the caller treats it exactly
    as it treats `conversational_reply`'s: run the turn normally.
    """
    u = _normalised(user)
    if not u:
        return None
    # Whose birthday, before any shape reads the line -- see `_BIRTHDAY_PHRASE`.
    who = _birthday_owner(u)
    if who is not None:
        if not birthdays or who not in birthdays:
            return ("birthday_unknown", who)
        u = _with_birthdays(u, birthdays)
    if pending:
        bare = u[4:] if u.startswith("the ") else u
        if bare.capitalize() in WEEKDAYS:
            return ("pending", u)
        for tail in _ASK_TAILS:
            u_t = u[: -len(tail)] if u.endswith(tail) else u
            if _denotes_time(u_t, anchor):
                return ("pending", u_t)
    if u in _TODAY_ASKS:
        return ("resolve", "today")
    if u in _CLOCK_ASKS:
        return ("clock", "now")
    # The count, before the three shape families: "how many days till
    # christmas" carries no `what day is` for `_RESOLVE_ASKS` to read, and a
    # count is a different sentence from a date.
    for shape in _COUNT_ASKS:
        m = shape.match(u)
        if m is None:
            continue
        e = _ASK_PREP.sub("", m.group(1)).strip()
        for tail in _ASK_TAILS:
            if e.endswith(tail):
                e = e[: -len(tail)].strip()
        e = _disambiguated(e, "next")
        if e and _denotes_time(e, anchor):
            return ("count", e)
    routed = _shaped(u, anchor)
    if routed is not None:
        return routed
    # Only now, and only on the whole battery having failed: a lead the user
    # put in front of a shape this file already knows. `remind me what I did
    # yesterday` is the audit's own counter-finding turn -- it missed here,
    # fell to the router, and the model chained `resolve_date` -> `recall_day`
    # correctly on its own. The hatch catching it costs that demonstration and
    # buys the seven phrasings beside it that did not survive the fall.
    for lead in _ASK_LEADS:
        if u.startswith(lead):
            routed = _shaped(u[len(lead):].strip(), anchor)
            if routed is not None:
                return routed
    return None


def _shaped(u: str, anchor: date) -> tuple[str, str] | None:
    """The three shape families against one already-normalised utterance."""
    for shapes, kind, direction in ((_RECALL_ASKS, "recall", "last"),
                                    (_SCHEDULE_ASKS, "recall", "next"),
                                    (_RESOLVE_ASKS, "resolve", "next")):
        for shape in shapes:
            m = shape.match(u)
            if m is None:
                continue
            e = _ASK_PREP.sub("", m.group(1)).strip()
            for tail in _ASK_TAILS:
                if e.endswith(tail):
                    e = e[: -len(tail)].strip()
            e = _disambiguated(e, direction)
            if e and _denotes_time(e, anchor):
                return (kind, e)
    return None


# --------------------------------------------------------------------------
# Who the user is -- the fourth hatch, and the one that writes a call
# --------------------------------------------------------------------------
#
# **The defect, measured twice.** `what is my name?` -> "You are my name." on
# the late drive; and with `packs/about-me.md` mounted and answering, entry 8's
# 24 phrasings read **22 routing and answering with the name, 2 declining, 0
# fabricating** unpunctuated -- and the same 24 punctuated invert to **10
# answering, 0 declining and 14 fabricating**: "You're 16 years old.", "My name
# is John.", "It's Kate." No call on any of them, chat register throughout. One
# character decides which half of that table a turn lands in, and the
# fabricating half is unreachable for the repair the store already is.
#
# **The gold is not open.** `docs/PLAN-FINETUNE-V4.md` entry 8 settles the
# user-facing half explicitly -- gold `web_search`, the store answers, and the
# payload it would need never contains a name because `packs/about-me.md` holds
# it and VISION §4 is the line. What was open was the *surface* collapse, and
# that belonged to decision 1b/0. The terminal-strip half of that decision was
# retired by `harness/foldgate.py` on 2026-08-30 (it cost `resolve_date` 17 of
# 24), so the punctuated repair became per-family, and **this family is the
# largest single term in what the strip would have bought**: owner questions
# 9/24 -> 21/24 of the pooled 16-of-57.
#
# So the repair is a hatch, and entry 8 specified its shape before it existed:
# "a `temporal_request`-style hatch, one that *writes the `web_search` call*
# rather than answering from a pool, is immune to the axis the weights fail on,
# and would take all 48 utterances to the store."
#
# **Writing the call rather than the answer is the whole design.** A pool would
# put the user's name in the runtime, which is the one place VISION §4 says it
# must not be: friends host their own copies, and a name in `corn/agent.py` is
# wrong for every instance but one. The store stays the single source of truth,
# the tool answers out of it, and this hatch contributes exactly the routing
# decision the weights were losing to a question mark.
#
# **The query is composed, not cut, and that is the vocative hazard handled.**
# `_normalised` decides *whether* this fires -- which is what buys immunity to
# case and punctuation at once -- but it must never decide *what gets asked*,
# because its vocative strip takes "corn" off both ends and on this instance
# that token is the owner's nickname. "is my nickname corn" normalises to "is
# my nickname" and would ask the store a question with the subject removed. So
# every shape maps to a fixed keyword query below, the utterance is never cut,
# and the raw words never leave the process either -- which is a privacy
# improvement the pool design would not have had.
#
# **What happens with no store mounted is a strict improvement anyway.** The
# query reaches `web_search`, finds nothing, and he says so. That is not a good
# answer; it is an honest one, and the defect being closed is 14 turns in 24
# inventing a name.
#
# Coverage is the 24 phrasings entry 8 measured, matched whole on
# `_normalised`'s flattening, so all 48 surfaces of them land here.
# `scripts/check_agent.py` asserts the set covers `harness/surfacegrid.py`'s
# `owner_question` family, which is what keeps the runtime and the instrument
# from disagreeing about what the class is.
#
# **The instrument cost, named rather than discovered.** Two grids read
# carriers that now hatch. `surfacegrid`'s `owner_question` family becomes a
# hatch read instead of a weights read -- grid M's precedent from decision 8,
# and acceptable because that family's job was to price decision 1b/0, which is
# taken. And `harness/historygrid.py`'s `chat_nocall` arm opens on `have you
# got my name`, which is one of these 24: that arm stops setting the history
# its label claims, and its own comment predicted exactly this ("if entry 8's
# payload ever teaches this shape to route, this arm stops setting the history
# its label claims and the `arm_landed` row is what will say so"). It is the
# `arm_landed` row that says so, which is why that column exists.

# Every shape entry 8 measured, mapped to the keyword query the store is asked.
# Four queries rather than 24, because the store is a keyword index and the
# distinctions between "what is my name" and "tell me my name" are distinctions
# about the *asking*, not about what is wanted.
USER_IDENTITY_ASKS: dict[str, str] = {
    # The name, in every shape the drive and the grid found.
    "what is my name": "my name",
    # Both spellings of the contraction, because `_normalised` keeps the
    # apostrophe -- the same reason `IDENTITY` lists "what's your name" and
    # "whats your name" side by side.
    "what's my name": "my name",
    "whats my name": "my name",
    "say my name": "my name",
    "what should you call me": "my name",
    "do you know my name": "my name",
    "do you remember my name": "my name",
    "tell me my name": "my name",
    "what do you call me": "my name",
    "what am i called": "my name",
    "remind me what my name is": "my name",
    "can you tell me my name": "my name",
    "you know my name right": "my name",
    "what name do you have for me": "my name",
    "what do people call me": "my name",
    "have you got my name": "my name",
    "what name am i under": "my name",
    # The parts of it, which the store may hold separately.
    "what's my first name": "my first name",
    "whats my first name": "my first name",
    "what is my first name": "my first name",
    "what's my nickname": "my nickname",
    "whats my nickname": "my nickname",
    "what is my nickname": "my nickname",
    "what's my full name": "my full name",
    "whats my full name": "my full name",
    "what is my full name": "my full name",
    # Who, rather than what -- the same question with the store as its answer.
    "who am i": "who i am",
    "do you know who i am": "who i am",
    "tell me who i am": "who i am",
    # The open form, added 2026-09-05 after a live turn: "what do you know
    # about me?" missed every shape above, went to the weights, and got "I
    # don't know anything about you." on an instance whose store said who he
    # was six ways -- followed by a user line he wrote himself. Same store
    # query as `who am i`: what is wanted is the same, only the asking differs.
    "what do you know about me": "who i am",
    "tell me what you know about me": "who i am",
    "do you know anything about me": "who i am",
    "what do you remember about me": "who i am",
    "tell me about me": "who i am",
    "what have you got on me": "who i am",
    "what do you have on me": "who i am",
    "describe me": "who i am",
}


def user_identity_request(user: str, name: str = "") -> str | None:
    """The query to ask the store about the user, or `None` for every other turn.

    Whole-utterance and exact against `_normalised`'s flattening, which is the
    social pools' rule and is what makes this immune to the case-and-mark axis
    the weights fail on. It returns a *query*, never an answer: see the block
    comment above for why the name may not live in this file.
    """
    return USER_IDENTITY_ASKS.get(_normalised(user, name))


# --------------------------------------------------------------------------
# The recheck -- a second source for the answer he just gave
# --------------------------------------------------------------------------
#
# **"Can we double check that" is a whole utterance about held state, which
# is the confirmation gate's shape, not the router's.** The *that* is the
# last search that answered, remembered on `World.last_search` exactly as the
# range clarify remembers its span -- and with nothing held, none of these
# phrases means anything, so the hatch stands down and the router gets the
# turn. Matching is exact and whole-utterance, the social pools' rule: "can
# you double check the oven is off" carries a request and goes to the model.
#
# What a recheck does is ask the same question while *avoiding every source
# already heard from* -- the backend's `avoid` -- and then say out loud
# whether the answers agree. The agreement sentence is runtime-composed
# because it is a comparison of two observations, which is arithmetic on
# facts, and §2 puts that in code.

RECHECK_ASKS = frozenset({
    "double check that", "double check", "can we double check that",
    "can you double check that", "double check that for me",
    "check again", "can you check again", "check that again",
    "find another source", "can we find another source",
    "can you find another source", "find another source for this",
    "can we find another source for this", "find a second source",
    "get a second source", "check another source", "try another source",
    "second source", "is there another source", "verify that",
    "can you verify that", "verify that for me",
})


def recheck_request(user: str, name: str = "") -> bool:
    return _normalised(user, name) in RECHECK_ASKS


def _same_place(a: str, b: str) -> bool:
    """`harness/backends/search.py`'s loose source identity, duplicated here
    because `corn/` may not import `harness/` (`check_layering.py`'s rule).
    "Wikipedia" and "en.wikipedia.org" are one source, or a second source is
    the first one wearing a different provider's hat."""
    fa = "".join(c for c in a.lower() if c.isalnum())
    fb = "".join(c for c in b.lower() if c.isalnum())
    return bool(fa) and bool(fb) and (fa in fb or fb in fa)


def second_source(ctx: "World", query: str, sources: list[str]) -> dict:
    """The same question, put to anywhere that has not answered it yet.

    A backend without `avoid` (the trained table, an older provider) gets a
    plain call, and the source check below is the net that keeps its answer
    from being counted as a second opinion when it is the same place again.
    """
    backend = ctx.search or web_search_tool
    try:
        payload = backend(query, avoid=tuple(sources))
    except TypeError:
        payload = backend(query)
    if isinstance(payload, dict):
        payload.pop(PASSAGE, None)
        src = payload.get("source") or ""
        if payload.get("answer") and any(_same_place(src, s) for s in sources):
            return {"ok": False, "reason": "no_results",
                    "say": f"I couldn't find a second source for {query}."}
    return payload


def recheck_say(payload: dict, first_answer: str, sources: list[str]) -> str:
    """What the comparison of two observations says, composed in code.

    Agreement is a shared content word that the question did not supply --
    `corn.extract`'s "an echo is not an extraction" rule, reused as "an echo
    is not a corroboration". Disagreement is said plainly with both sources
    named, because a user who asked for a second source has asked to be told
    when the sources split, and papering that over would be the confident
    wrong answer with extra steps.
    """
    origin = sources[0] if sources else "the first source"
    if not isinstance(payload, dict) or not payload.get("answer"):
        return (f"I couldn't find a second source on that one. "
                f"Still going off {origin}.")
    src = payload.get("source") or "a second source"
    answer = tidy_say(payload["answer"])
    q_words = set(content_words(payload.get("query") or ""))
    shared = (set(content_words(payload["answer"]))
              & set(content_words(first_answer))) - q_words - FRAME
    if shared:
        return f"Checked {src} too and it lines up. {answer}"
    return (f"Different story from {src}. {answer} "
            f"The first answer came from {origin}.")


def _ask_agent(args: dict, ctx: "World") -> dict:
    """`ask_agent_tool`, plus the append that makes the relay real.

    **Queued to disk and not sent, and the gap is deliberate.** The runtime
    that actually reaches the agent does not exist yet, and the honest stand-in
    for a slow tool is the thing a slow tool does first: accept the request,
    write it down, acknowledge it. The alternative -- a payload that says
    `sent` while nothing left the machine -- would put a false status in the
    one tool that speaks as the user, and `save_note`'s lesson applies exactly
    here: a note that is not on disk afterwards is not a note, and a relay
    nothing recorded is not a relay.

    The queue sits beside the day log rather than inside it. They are both
    append-only JSONL and it is tempting to share the file, but `recall_day`
    reads that store and would then read back the user's escalations as though
    they were notes they had written -- which is a different claim about the
    day than the one they made.

    The payload is left exactly as `ask_agent_tool` built it, for `_save_note`'s
    reason: the model copies its reply out of the observation, so a runtime
    that improved the wording here would be editing the corpus from the far
    end.
    """
    request, context = args["request"], args.get("context")
    payload = ask_agent_tool(request, context, agent=ctx.agent)
    if payload.get("status") == "queued":
        row = {"date": ctx.anchor.isoformat(), "request": request}
        if context:
            row["context"] = context
        queue = ctx.log.path.with_name("escalations.jsonl")
        with queue.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return payload


def _decline(args: dict, ctx: "World") -> dict:
    """No tool covers the request, said in the tool's own voice."""
    return {
        "ok": False,
        "reason": "not_covered",
        "say": ctx.rng.choice(DECLINE_SAYS),
    }


def _resolve_date(args: dict, ctx: "World") -> dict:
    """`resolve_date`, plus the memory of the question it just asked.

    **The tool asked "Saturday or Sunday?" and could not read the answer.**
    `resolve_date_tool` is a pure function of an expression and an anchor, so a
    bare weekday is unresolvable to it -- "Saturday" means nothing without the
    span it is being chosen from. Live at 260M that produced a clarify, a
    refused answer, and then a retry with an ordinal that resolved to the wrong
    day and was read out with confidence.

    Measured over all seven `RANGE_EXPRESSIONS`: only the two weekend questions
    can be answered without the span, and four of the others land a week or two
    outside it. So the span is remembered here, where a process can hold state,
    rather than guessed there, where it cannot.

    **One span, dropped as soon as it is used or superseded.** It is the same
    shape as `harness/backends/confirm.py`'s pending call and the same argument:
    the state belongs to the conversation, and holding it any longer would let a
    weekday said ten turns later be answered against a question nobody
    remembers. `last month` sets it too and `weekday_in_span` still refuses --
    a span of five Mondays has no unambiguous answer, and that question wants a
    date.
    """
    pending, ctx.range_span = ctx.range_span, None
    if pending is not None:
        d = weekday_in_span(args["expression"], pending)
        if d is not None:
            return {"date": d.isoformat(), "weekday": WEEKDAYS[d.weekday()],
                    "spoken": spoken_form(d)}
    out = resolve_date_tool(args["expression"], ctx.anchor)
    if out.get("reason") == "range":
        span = out["span"]
        ctx.range_span = (date.fromisoformat(span["start"]),
                          date.fromisoformat(span["end"]))
    return out


def _web_search(arguments: dict, ctx: "World") -> dict:
    """The lookup, and a second reading of what the reduction threw away.

    **The reduction is positional and the extraction is not, and this is where
    the two meet.** `harness/backends/search.py` returns a provider's lead
    sentence, which answers "what is X" and does not answer "what is the
    melting point of X" -- A1-live measured that as the answer arriving and
    being discarded on 8 of 24 lookups. When the backend hands the full text
    forward under `PASSAGE`, `ctx.reader` reads it as overlapping windows and
    `corn.extract.reduce` turns N readings into one, and *that* answer takes
    the reduction's place in the payload.

    **The reduction is the floor, never the casualty.** An extraction that
    finds nothing, disagrees with itself, or raises leaves the payload exactly
    as the backend built it -- so the worst this path can do is spend eight
    decodes and change nothing, and the turn still ends in the sentence it
    would have ended in before. That asymmetry is the point: the plan's own
    "what would make this fail" names a passage making him *worse* at what he
    already answered, and a runtime that can only replace a reduction with a
    grounded span cannot take that route.

    **The reader is caught broadly, deliberately.** It runs a model on a
    variable number of prompts of a length nothing here controls, and every
    way that can go wrong -- a window that fills `block_size`, a device out of
    memory, a tokenizer disagreeing about a byte -- is the same fact from the
    user's side, which is the argument `web_search`'s own provider loop makes
    at greater length. A turn must end in something speakable.
    """
    payload = (ctx.search or web_search_tool)(arguments["query"])
    passage = payload.pop(PASSAGE, None) if isinstance(payload, dict) else None
    if ctx.reader is None or not passage or "answer" not in payload:
        return _remember_search(ctx, payload)
    # The payload's `query` rather than the model's, because `strip_affixes`
    # may have taken phrasing off it and the payload is what the observation
    # will carry -- and `corn.extract.grounded` reads the question to decide
    # which words in a reply are an echo rather than an extraction.
    try:
        answer, why = ctx.reader(payload.get("query") or arguments["query"],
                                 passage, payload.get("source") or "")
    except Exception as exc:
        return _remember_search(ctx, {**payload,
                READING: {"ok": False,
                          "why": f"the reader failed ({type(exc).__name__})"}})
    if answer is None:
        # **A page served for its passage does not get to speak its lead.**
        # The deep path (`harness/backends/search.py`'s subject rule) fetches
        # a page because its *title* says it is the subject the question
        # named, not because its lead sentence answers anything -- so when the
        # reader finds nothing, the sentence sitting in `answer` is a true,
        # on-topic non-answer. Serving it is what `MIN_COVER`'s own comment
        # refuses to do, and the reduction is only "the floor" when the
        # reduction was an answer. So the turn takes the honest miss, in the
        # shape it already had for one.
        if payload.get(LEAD_ANSWERS) is False:
            return {"ok": False, "reason": "no_results",
                    "say": "I couldn't find anything useful for "
                           f"{payload.get('query') or arguments['query']}."}
        return _remember_search(
            ctx, {**payload, READING: {"ok": False, "why": why}})
    # `answer` is already the first key, so this replaces its value and leaves
    # the key order alone. The model reads the payload as a shape.
    #
    # **Tidied here, so the observation and the spoken sentence carry the same
    # string.** A deferred turn speaks this field verbatim and a framed turn
    # has the model read it and reframe it; repairing only the spoken half
    # would leave the model reading the seam it is being asked not to
    # reproduce. Nothing `tidy_frame` removes can carry a fact, and both words
    # it can drop are in `corn.extract.FRAME` already, so `grounded` reads the
    # repaired answer exactly as it read the unrepaired one.
    return _remember_search(
        ctx, {**payload, "answer": tidy_frame(answer),
              READING: {"ok": True, "why": why}})


def _remember_search(ctx: "World", payload: dict) -> dict:
    """Record what a search answered, so a recheck has a *that* to check.

    Only successes are remembered -- a `no_results` is not a finding anyone
    would ask a second source about -- and a new question supersedes the old
    state whole, `range_span`'s lifecycle. The same question answered again
    appends its source, so a chain of "find another source" avoids every
    place already heard from rather than only the last one.
    """
    if isinstance(payload, dict) and payload.get("answer"):
        q = payload.get("query") or ""
        src = payload.get("source") or ""
        if ctx.last_search is not None and ctx.last_search[0] == q:
            if src and src not in ctx.last_search[2]:
                ctx.last_search[2].append(src)
        else:
            ctx.last_search = (q, payload["answer"], [src] if src else [])
    return payload


EXECUTORS = {
    "decline": _decline,
    "ask_agent": _ask_agent,
    "save_note": _save_note,
    # Only ever the owner (PLAN-PEOPLE §7): `contact` is read to decide whether
    # it names them, never resolved; anyone else is refused with the offer.
    "place_call": lambda a, ctx: owner_call_tool(a.get("contact"), ctx.persona.user_name, ctx.rng),
    "send_text": lambda a, ctx: owner_text_tool(a.get("contact"), a["message"],
                                                ctx.persona.user_name, ctx.rng),
    "web_search": _web_search,
    "resolve_date": lambda a, ctx: _resolve_date(a, ctx),
    "recall_day": _recall_day,
}

# The invariant `scripts/check_agent.py` asserts, stated where it is easy to
# keep true: a name in the registry the runtime cannot execute is a call the
# model will emit into silence.
assert set(EXECUTORS) == set(REGISTRY), "every declared tool needs a backend"


def register_tool(tool: Tool, executor) -> None:
    """VISION §6's "a declaration file, not a code change", at the seam.

    The loader that reads declaration files lives in `harness/backends/`
    because a file format is harness policy; what it may *do* to the registry
    lives here, next to the invariant it must keep. Three refusals, each a
    failure worth having at load rather than mid-decode:

    - a name already registered: shadowing a trained tool would silently
      reroute a corpus behaviour to somebody's shell script;
    - a name the grammar could never emit: `corn.grammar._names` requires
      non-empty ASCII with no quote or backslash, and a tool that validated
      here and was unemittable there would present as the model "refusing"
      it;
    - an executor that is not callable, which would fail exactly one line
      after the model first routed to it.

    One capture to know about: `corn.grammar._TOOL_NAMES` is read from
    `REGISTRY` at import, so a tool registered later is invisible to a
    `CallConstraint` built with `declared=None`. Every server constructs its
    agent with an explicit declaration, which re-reads `REGISTRY`; only a
    guard that both registers late and declares nothing would notice.
    """
    name = tool.name
    if name in REGISTRY:
        raise ValueError(f"{name} is already a tool; a declaration file may "
                         f"not shadow one")
    if (not name or not name.isascii() or '"' in name or "\\" in name):
        raise ValueError(f"{name!r} is not a name the grammar can emit")
    if not callable(executor):
        raise ValueError(f"{name}: executor is not callable")
    REGISTRY[name] = tool
    EXECUTORS[name] = executor
    assert set(EXECUTORS) == set(REGISTRY), \
        "every declared tool needs a backend"


class World:
    """What the tools are wired to for this process.

    **There is no contact book** (removed 2026-10-13, PLAN-PEOPLE §7): calls
    and texts reach only the owner, named by the persona's `user_name`, and
    the people an owner keeps are a pack table (`harness/backends/packs.py`).
    The book this replaced defaulted to the 53 *training* names, which was
    the only book the model could copy from and the reason a name outside it
    was liable to be swapped for one inside it -- finding 14, gone with it.
    """

    def __init__(self, anchor: date, notes: Path,
                 seed: int | None = None, search=None, confirm=None,
                 reader=None, agent: str | None = None, steps=None,
                 persona: Persona | None = None, marker: Marker | None = None):
        from .tools import DEFAULT_AGENT

        self.anchor = anchor
        # What `ask_agent` calls the thing it relays to, out loud. A role by
        # default, because this instance cannot know which agent its owner
        # wired up and a wrong proper noun is worse than a general one.
        self.agent = DEFAULT_AGENT if agent is None else agent
        self.log = DayLog(notes)
        # Only `decline` draws from this. Seedable so a guard can pin the
        # wording; `None` is the runtime and varies per process, because a
        # refusal that is the same sentence every time is the failure mode
        # `sayvar` was built to price.
        self.rng = random.Random(seed)
        # **The one seam where a real backend replaces a trained one.**
        # `web_search_tool` answers out of `FACTS`, which is the table the
        # corpus was generated from -- correct for a generator and useless to a
        # person. A callable here takes its place and must return the *same four
        # payload shapes*, because the model reads its reply out of the
        # observation and has only ever been shown those. `None` keeps the
        # table, so every guard and every eval in this repo runs exactly as it
        # did; `harness/backends/search.py` is what passes something else.
        #
        # It lives on `World` rather than in `EXECUTORS` because this is
        # per-process wiring, which is what `World` is for, and because
        # `EXECUTORS` is a module-level dict that two processes would share.
        self.search = search
        # The step cursor, when a document with numbered steps is loaded --
        # `corn/steps.py`, and here for exactly the reason `search` is: this is
        # per-process wiring and a position in a document is conversational
        # state the weights cannot hold. `None` on every configuration that
        # loaded no such document, which is what keeps the hatch below dead.
        self.steps = steps
        # **Who he is on this machine**, and here rather than on `Agent` for
        # the reason `search` and `steps` are: per-process wiring, decided by
        # whatever started the server, never module state. `None` is the
        # shipped persona -- the name in the pools, no birthday, no occasions
        # -- so every guard and eval that builds a `World` without one gets
        # exactly the runtime it has always measured. `harness/backends/
        # persona.py` is what passes something else.
        self.persona = DEFAULT_PERSONA if persona is None else persona
        # Where "he already mentioned it today" is written down, so a restart
        # on his birthday does not announce it a second time. `None` keeps the
        # record in memory for the life of the process, which is what a guard
        # wants and what a server does not -- see `Marker`.
        self.marker = marker
        self.occasion_said: date | None = None
        # The people-store birthdays already mentioned this process
        # (`heads_up_key`); the marker is the copy that survives a restart.
        self.heads_up_said: set[str] = set()
        # The user's own words for the turn in flight. `steps` is what needs
        # it: the decision to *begin* reciting is about what the person asked
        # for, and the query that reaches the search seam is whatever the
        # model wrote -- which under `--multi` is sometimes the previous
        # turn's query copied forward (measured live 2026-08-27: a request for
        # a recipe the book does not have restarted the one before it).
        self.last_user: str = ""
        # The span of the last unresolved range, so the clarify it produced can
        # actually be answered. `None` until `resolve_date` returns a range and
        # `None` again the moment anything reads it -- see `_resolve_date`. The
        # only mutable conversational state in the runtime, and it is here for
        # the reason `search` and `confirm` are: per-process, not per-module.
        self.range_span: tuple[date, date] | None = None
        # Which question the span above was serving -- `"recall"` when the
        # range came off a day-log question, so the weekday that answers the
        # clarify can be chained into `recall_day` rather than read back as a
        # bare date. The daycross slice is the trained precedent: its second
        # turn answers "Which day of that week?" and the transcript goes on to
        # the tool the *first* turn was about. Same lifecycle as `range_span`:
        # set beside it, dropped the moment it is read. Only the temporal
        # hatch writes it; the model path never sees it.
        self.range_intent: str | None = None
        # The last search that answered, held so "double check that" and
        # "find another source" have a that: `(query, first answer, sources
        # heard so far)`. Same lifecycle argument as `range_span` -- the
        # state belongs to the conversation and is superseded the moment a
        # different question is asked. Written by `_web_search`, read by the
        # recheck hatch, never by the model.
        self.last_search: tuple[str, str, list[str]] | None = None
        # **The second runtime seam, and the only one that can stop a tool
        # running at all.** A callable `(name, arguments) -> dict | None`:
        # return a payload and it becomes the observation *without the tool
        # executing*; return `None` and the executor runs as it always has.
        # `harness/backends/confirm.py` is what passes one, so that a call and
        # a text ask before they happen.
        #
        # Here rather than inside `EXECUTORS` for the same reason `search` is:
        # this is per-process wiring and `EXECUTORS` is a module-level dict two
        # processes would share. `None` is every guard and every eval in this
        # repo, unchanged.
        self.confirm = confirm
        # **The third seam, and the first one that is the model itself.**
        # `(question, passage, source) -> (answer or None, why)` --
        # WS-B-alt's whole chain, which `corn.extract.read_passage` is the body
        # of and `harness/backends/read.py` is the only thing binding weights
        # to it.
        #
        # It is a callable rather than the model plus the tokenizer because
        # the cut is in *tokens*: `windows` needs an encoder, `BatchedReader`
        # needs equal lengths, and a `World` that carried a tokenizer so an
        # executor could slice a string would be holding half a runtime to
        # avoid one closure.
        #
        # **Assignable after construction, and that is not laziness.** The
        # reader needs the weights, the weights are loaded by `Agent`, and
        # `Agent` needs a `World` -- so something has to be set second, and a
        # field a server fills in is a smaller cycle-break than a lazy factory
        # that could run on the first turn of a conversation. `None` is every
        # guard, every eval and every instance without `--extract`.
        self.reader = reader


# --------------------------------------------------------------------------
# The cut
# --------------------------------------------------------------------------


def split_emission(chunk: str) -> tuple[str, str | None]:
    """`(text the runtime keeps, the raw call it must execute or None)`.

    Pure, and separate from the decode loop, because it is the one piece of
    this file that carries the argument -- `scripts/check_agent.py` asserts on
    it directly and needs neither weights nor a GPU to do it. Everything from
    the model's own `<|obs|>` onwards is dropped here and never reaches the
    context, the user, or a tool.
    """
    head = chunk.split(D_OBS)[0]
    # **A user line he wrote himself is not a user line, and nothing past it
    # is his turn.** `chunk` is only ever what the model generated -- the
    # runtime owns every real `<|user|>` and puts it in the context, never in
    # the emission -- so one appearing here is a transcript continuing on its
    # own: "I don't know anything about you.\n<|user|>what's the capital of
    # Garunthfell\n<|call|>{web_search ...}" (2026-09-05, live). Before this
    # cut the `rsplit` below found that call and the runtime *executed the
    # question he invented*, then spoke its answer, and on "thanks Corn" the
    # same shape ran eight invented rounds of thanks and reply into the
    # streamed text. Everything from the first `<|user|>` on is dropped here,
    # with the call it carried, for the same reason the model's own `<|obs|>`
    # is: it is not something anyone said to him.
    head = head.split(D_USER)[0]
    if D_CALL not in head:
        return head, None
    raw = head.rsplit(D_CALL, 1)[1]
    # A call running straight into `<|end|>` is the `recall_day` case: the
    # corpus ends the transcript there, so the marker arrives as part of the
    # same breath and would otherwise fail as `not_json`.
    return head, raw.split(D_END)[0].split(STOP_DOC)[0].strip()


def say_cut(chunk: str) -> int | None:
    """Where a *post-observation* `<|say|>` stops being something he was taught.

    **The observation leaks into the speech, and the corpus says it never
    should.** Handed `{"answer": "Vientiane", "source": ..., "query": ...}` the
    model copies the answer and then keeps copying, and what reaches a voice
    client is

        Vientiane, "source": "worldatlas.com", "query": "the capital of ...

    read out loud, punctuation and all. It is not a length effect -- a
    108-character answer comes back clean and a 9-character one does not -- and
    it is not greedy decoding either: at temperature 0.6 and 0.8 it survives
    on one to three of the same six cases, so sampling moves which rows fail
    rather than whether they do.

    **The rule is measured, not chosen.** Across **1,629,766** say segments in
    `data/raw/tools*.txt` -- every transcript in the project where speech
    follows a tool observation -- exactly **zero** contain a double quote, zero
    contain a colon, zero contain a second `<|say|>`, none runs to a second
    line, and the longest is 79 characters. A quote after an observation is
    therefore not a sentence he might plausibly be saying; it is the payload,
    and this returns the index where it starts.

    **Scoped to after an observation, and that scope is the whole care taken
    here.** `data/raw/chat*.txt` speech does contain quotes -- it is dialogue,
    people quote each other -- so a blanket rule would cut conversational
    replies in half. `turn` only arms this once a payload has been spliced in.

    Pure, like `split_emission` and for the same reason: this decides what a
    user hears, and `scripts/check_agent.py` should be able to hold it to
    account without a checkpoint or a GPU.
    """
    i = chunk.find(D_SAY)
    if i < 0:
        return None
    start = i + len(D_SAY)
    body = chunk[start:]
    # A marker the runtime owns already ends the say; nothing past it is ours
    # to cut, and looking past it would find quotes in the *next* transcript.
    for marker in (D_END, STOP_DOC):
        k = body.find(marker)
        if k >= 0:
            body = body[:k]
    stops = [j for j in (body.find('"'), body.find("\n"), body.find(D_SAY))
             if j >= 0]
    return start + min(stops) if stops else None


def tidy_say(text: str) -> str:
    """The spoken string, closed off where `say_cut` left it mid-clause.

    Cutting at the quote in `Vientiane, "source": ...` leaves `Vientiane,` and
    a trailing comma is a held breath when a voice client reads it. The corpus
    ends a say on a full stop or a question mark, so this does too.
    """
    text = text.strip().rstrip(",;:").strip()
    if text and text[-1] not in ".?!":
        text += "."
    return text


# **The seam between `SAY_ANSWER`'s frame and the span it is wrapped around.**
# `It's {a}.` is a trained framing, not a runtime template -- `corn/toolgen.py`
# writes it into the corpus and the reader reproduces it -- so what arrives in
# `answer` is the frame with whatever the reader extracted dropped into it,
# and the two do not always meet grammatically. Four live on 2026-09-07:
# "It's The yen.", "It's The Pacific Ocean.", "It's it is part Flying type."
# and "It's fifth book of narrative Spanish writer Javier Cercas."
#
# Two of those seams are repairable without knowing anything about the fact,
# and only those two are touched here:
#
#   * a **repeated copula** -- the span was a clause, so the frame says "it is"
#     twice. Dropping the second is meaning-preserving by inspection.
#     **Only the copula**, spelled either way: the possessive `its` was in the
#     first version of this pattern and turned "It's its own thing." into
#     "It's own thing.", which is the repair inventing a defect rather than
#     removing one. A one-word over-reach, caught by its own regression row.
#   * a **capitalised article** mid-sentence, and *only* when the word after it
#     is lowercase. "It's The yen." is a typographic error; "It's The Hague."
#     is a proper name whose article really is capitalised, and nothing here
#     can tell those apart except by what follows. So the ambiguous half is
#     left alone: the cost is a stiff sentence, and the alternative is
#     lowercasing somebody's name.
#
# What it deliberately does not do is repair the *fourth* example. A span that
# reads "fifth book of narrative Spanish writer Javier Cercas" is a wrong
# retrieval, and a runtime that tidied its grammar would be making a wrong
# answer read better. `FELL_BACK_FRAME` is what covers that one.
_FRAME_COPULA = re.compile(r"^(It's) +(?:it is|it's) +")
_FRAME_ARTICLE = re.compile(r"^(It's) +The +(?=[a-z])")


def tidy_frame(answer: str) -> str:
    """`It's {a}.` with the seam repaired where the repair is unambiguous."""
    text = _FRAME_COPULA.sub(r"\1 ", answer.strip())
    return _FRAME_ARTICLE.sub(r"\1 the ", text)


# What the runtime says when the model reached the end of a turn without
# speaking and the observation has nothing to fall back on. Deliberately an
# admission rather than a trained-sounding line: it is the runtime talking,
# not him, and the honest content is that the turn produced nothing.
# **Who composed the words in a `say`, which a transcript cannot tell you.**
# Three different authors put text in that field and all three land in the
# stream looking identical: the model generated it, a *tool* returned it in a
# payload, or the *runtime* wrote it -- a social pool, an identity pool, or
# `fallback_say` when he ended the turn in silence.
#
# It matters because these transcripts are training data. A corpus built from
# logged conversation trains the model to produce whatever is in the `say`
# field, and two of the three authors are things it must never learn to
# generate: runtime text would teach it to *recite* a tool list it currently
# reads off the registry -- the exact confabulation `identity_reply` exists to
# prevent -- and tool text would teach it to invent observations, which is
# what §5.2 and the whole `<|obs|>` cut exist to stop.
#
# So the runtime records what it already knows at the moment it knows it,
# rather than leaving a corpus builder to guess later from timing or wording.
# Decided at each of the four sites that assign `said`, never inferred at the
# end: inference is how the two paths in `turn` would come to disagree.
SAY_AUTHORS = ("model", "runtime", "tool")

NOTHING_SAID = "Sorry, I didn't get anywhere with that."

# **What a fallback sounds like, so it does not sound like an answer.**
# When `--extract` is on and the reader finds nothing in the passage, the
# runtime speaks the provider's lead sentence instead -- the floor
# `_web_search_read` calls "never the casualty". Measured live on 2026-09-07,
# that floor is a *confident non-answer* about three questions in ten: "who is
# the prime minister of canada" was answered "It's the head of government of
# Canada.", "how far is the moon from earth" with the definition of the
# distance, and "what is the speed of light" with the lead of a Javier Cercas
# novel of that name. Every one of them is true, on topic, and useless, and
# every one of them arrived in the same voice as "It's Tokyo."
#
# The payload already knows -- `fell_back` is on the say event and has been
# since the reader shipped -- so this costs nothing to say out loud. It does
# not make a wrong retrieval right; it makes the difference between the two
# audible, which is the half the user could not previously hear.
#
# **Runtime words, and recorded as such.** `SAY_AUTHORS`' argument applies
# exactly: these transcripts are training data and a corpus built from them
# must not teach him to generate a frame the runtime puts on. The say event's
# author flips to `runtime` wherever this is applied.
FELL_BACK_FRAME = "I couldn't get an answer out of that one. Here's how it opens: {lead}"

# And when a tool *did* run and he still said nothing. `place_call`, `send_text`
# and `save_note` all answer with a bare `status` and no line to read, so this
# is the shortest true thing available -- the corpus's own replies for these are
# `SAY_SAVED`'s "Saved." and `SAY_CALLED`'s equivalents, which is the same
# register.
DID_IT = "Done."

# **The one payload field that is composed from rather than read out.**
# `corn/daylog.py:speak` builds the `recall_day` reply by naming *one* entry of
# several and framing it, and its docstring argues the case: §3 wants short
# spoken utterances, and reciting a four-item list back at a voice interface is
# the wrong thing to learn from the right payload. The corpus payload has no
# `say` at all -- `day_log` returns `date`, `weekday`, `entries` -- so the `say`
# that `_recall_day` puts there is this runtime's own summary, joining every
# entry, and deferring to it would undo that decision. `scripts/check_agent.py`
# asserts the premise rather than trusting this comment.
COMPOSED_FIELD = "entries"


def deferred_say(payload) -> str | None:
    """The string the corpus speaks verbatim for this observation, or `None`.

    **This is a stated design intent the weights do not reliably honour.**
    `_decline`'s docstring puts it plainly -- "the refusal Corn-Jr reads out is
    written here, not composed by him" -- and `corn/toolgen.py:_build` renders
    every one of these transcripts as `<|say|>{obs["say"]}`, verbatim, with no
    transformation between the payload and the speech. What the 260M actually
    does with them is paraphrase, and a paraphrase of a refusal is not a
    smaller version of the same sentence. Handed

        {"ok": false, ..., "say": "That's outside what I can reach from here."}

    he said *"That's within what I can reach from here."* -- the negation
    inverted, the meaning reversed, in a sentence whose entire job was to tell
    the user he could not do something. There is no reading of that as a
    stylistic variation.

    So where the corpus copies, the runtime copies. It is not overriding the
    model; it is holding it to the shape it was trained on, which is the same
    argument `corn/grammar.py` makes about the call and this file has so far
    only made about the call.

    `clarify` joins `say` because it is the same relationship: a question the
    tool asked, which the model's job is to relay. `harness/backends/confirm.py`
    depends on it -- a confirmation question that came back reworded is a
    different question, asked about an action that cannot be taken back.
    """
    if not isinstance(payload, dict):
        return None
    # See `COMPOSED_FIELD`. The success shape of `recall_day` is the one place
    # a `say` is a summary rather than a script -- but only when there is
    # something to summarise. An empty day has no entry to frame and no span to
    # copy, so its `say` is a script like any other refusal is, and standing
    # down on it let him answer "nothing on that day" in his own words. He is
    # measured at 63 of 90 *silence* on this tool; the sentence exists.
    if payload.get(COMPOSED_FIELD):
        return None
    for field in ("say", "clarify"):
        text = payload.get(field)
        if isinstance(text, str) and text.strip():
            return text.strip()
    return None


def recall_rejection(reply: str, payload) -> str | None:
    """Why his `recall_day` summary cannot stand, or `None` if it can.

    **`COMPOSED_FIELD` is a design intent, and this is what happens when the
    weights do not meet it.** The exception exists for a good reason -- §3 asks
    for short spoken utterances and reciting a four-item list back at a voice
    interface is the wrong thing to learn from the right payload -- so the
    runtime's joined summary is deliberately *not* deferred to, and he is left
    to frame the day himself. Live at 260M, handed

        {"entries": ["the roof guy is coming tuesday"],
         "say": "On Monday, August 24th: the roof guy is coming tuesday."}

    he said `"2026-08-24, "`. The tool worked, the sentence was sitting in the
    payload, and what reached the user was the ISO date and a comma.

    So the intent is kept and the floor is put under it, which is the shape the
    social path already uses: he speaks when he can, and the payload speaks
    when he cannot. The bar is not whether the summary is elegant. It is
    whether it contains the thing being recalled -- a reply about a day that
    names nothing from that day has not read it back, whatever else it is.

    Three words in a row rather than a word count, because the entries are
    short and any single word of them ("the", "is") proves nothing. An entry
    under three words has to appear whole.
    """
    if not isinstance(payload, dict):
        return None
    entries = payload.get(COMPOSED_FIELD)
    if not entries:
        return None
    said = reply.strip()
    if not said:
        return "empty"
    if said[-1] not in ".!?":
        return "unfinished"
    spoken = _content_words(said)
    for entry in entries:
        text = entry.get("text", "") if isinstance(entry, dict) else str(entry)
        words = _content_words(text)
        if not words:
            continue
        if len(words) < 3:
            if all(w in spoken for w in words):
                return None
            continue
        runs = [tuple(words[i:i + 3]) for i in range(len(words) - 2)]
        heard = [tuple(spoken[i:i + 3]) for i in range(len(spoken) - 2)]
        if set(runs) & set(heard):
            return None
    return "recalled nothing from the day"


def search_rejection(reply: str, payload) -> str | None:
    """Why his answer to a search cannot stand, or `None` if it can.

    **`recall_rejection`'s argument, applied to the other tool he frames.**
    A `web_search` success leaves the say to the model, and what he composes
    is checked against nothing -- which is how three replies reached a user on
    2026-08-26: "I Did Today, according to wikipedia.org." with the payload's
    source reading `didtoday.app` (an invented attribution, on the one tool
    whose observations carry one), "Looks like Abraham Lincoln." answering
    "who is Abraham Lincoln" (the question read back as its own answer), and
    "Looks like D.M.B.B.T." from a passage about Beethoven's Ninth (letters
    the observation never printed).

    The bar is `corn.extract.grounded`, unchanged: every content word from
    the observation, the question, the attribution or the trained framing,
    and at least one contiguous thing the observation actually says beyond
    an echo of the question. It already rejects all three, because they are
    the same three failures it was written against on the reader's side --
    this function is that bar moved to where the model speaks.

    **It deliberately trades away lucky parametric answers.** "Looks like 100
    degrees Celsius." over a payload that never says 100 is refused even when
    it happens to be true, because a 260M model asserting facts the
    observation does not carry is the behaviour four findings priced, and
    "It's Monday." was the same move with worse luck. The floor spoken
    instead is the payload's own sentence, which is never invented.

    Applies only to the success shape -- a payload with an `answer`. Refusals
    carry a `say` and are already deferred to; `recall_day` carries entries
    and has its own check.
    """
    if not isinstance(payload, dict):
        return None
    answer = payload.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        return None
    said = reply.strip()
    if not said:
        return "empty"
    query = payload.get("query") or ""
    # A TLD is frame, not fact: the wiki provider reports `Wikipedia` and the
    # trained attribution says "according to wikipedia.org", and rejecting
    # that on `org` would refuse a true sentence over the part of a domain
    # that cannot carry the invention. So the source is widened by the TLDs
    # before either check reads it -- `grounded` excludes source words from
    # the novel span anyway, and no TLD could have been the fact. The domain
    # *name* stays checked: "wikipedia" over a `didtoday.app` payload still
    # fails on the word that actually claims the wrong source.
    source = (payload.get("source") or "") + " org com net www co app io"
    allowed = (set(content_words(answer)) | set(content_words(query))
               | set(content_words(source)) | FRAME)
    stray = [w for w in content_words(said) if w not in allowed]
    if stray:
        return f"invented {stray[0]!r}"
    # **A listed answer read back as one of its items.** Live on the shipped
    # runtime, 2026-09-06: "Charizard's Type is Fire/Flying." became "It's
    # flying.", "It's Bug, Fairy and Ghost." became "It's Bug.", and the
    # Snorlax row became "Looks like Attack 110." Every word he said is in
    # the observation and the span is contiguous, so the two checks above
    # pass a reply that dropped most of the fact. The bar: an answer that is
    # a list of short items, and a reply that carries some but not all of
    # them. Only lists of *short* items, so a sentence with a comma in it is
    # never a list, and a reply that names none of the items is left to
    # `grounded` as before.
    items = _listed_items(answer)
    if len(items) >= 2:
        said_words = set(content_words(said))
        hit = [it for it in items
               if set(content_words(it)) and set(content_words(it)) <= said_words]
        if 0 < len(hit) < len(items):
            return f"kept {len(hit)} of {len(items)} listed"
    if grounded(said, answer, query, source):
        return None
    return "added nothing the observation says"


# The value of a pack cell or a prose answer, when it is a list: the part
# after the template's " is " (or the whole answer), split on the three
# separators the packs and the reader actually produce.
_LIST_SPLIT = re.compile(r"\s*/\s*|,\s+|\s+and\s+|;\s+")
_LIST_ITEM_WORDS = 3


def _listed_items(answer: str) -> list[str]:
    """The short items an answer lists, or `[]` when it is not a list.

    "Fire/Flying" -> ["Fire", "Flying"]; "Bug, Fairy and Ghost" -> three;
    "Snorlax: Type Normal, HP 160, Attack 110, ..." -> nine. A sentence
    that merely contains a comma -- "Paris, the capital of France, is a
    major city" -- has an item over `_LIST_ITEM_WORDS` words and is not a
    list. Every item must be short, not merely most, so the rule is
    conservative by construction.
    """
    # A unit in brackets is a label, not a word: "Height (m) 2.1" is three
    # words of item, the way the pack's own header wrote it.
    body = re.sub(r"\s*\([^)]*\)", "", answer.strip().rstrip(".!"))
    for frame in ("it's ", "looks like ", "it is "):
        if body.lower().startswith(frame):
            body = body[len(frame):]
    if " is " in body:
        body = body.rsplit(" is ", 1)[1]
    parts = [p.strip() for p in _LIST_SPLIT.split(body) if p.strip()]
    if len(parts) < 2:
        return []
    if any(len(content_words(p)) > _LIST_ITEM_WORDS or not content_words(p)
           for p in parts):
        return []
    return parts


def date_sentence(payload, anchor: date) -> str | None:
    """The corpus's own three openings for a resolved date, chosen by tense.

    `gold_after` in `evals/temporal.jsonl` is this line. Shared by the
    temporal hatch, which writes the say itself, and by the floor under a
    *routed* `resolve_date` call, so the two cannot drift apart.
    """
    if not isinstance(payload, dict) or "date" not in payload:
        return None
    try:
        resolved = date.fromisoformat(payload["date"])
    except (TypeError, ValueError):
        return None
    spoken = payload.get("spoken") or payload["date"]
    if resolved == anchor:
        return f"It's {spoken}."
    if resolved > anchor:
        return f"That'll be {spoken}."
    return f"That was {spoken}."


def date_rejection(reply: str, payload) -> str | None:
    """Why his read-back of a resolved date cannot stand, or `None` if it can.

    **The third floor, for the third tool he frames.** "what was last
    wednesday" resolved to Wednesday, September 2nd on 2026-09-06 and he
    said "That one's settled." -- a routed `resolve_date` call, not the
    hatch, so nothing composed the sentence for him and nothing checked
    what he composed. The bar is the smallest one that catches it: the
    reply names *some* part of the date the observation spoke -- the
    weekday, the month or the day. A reply that carries none of them has
    read a date back without the date in it.

    Applies only to the success shape -- a payload with `date` and
    `spoken`. Clarifies carry a `clarify` and are already deferred to.
    """
    if not isinstance(payload, dict) or "date" not in payload:
        return None
    spoken = payload.get("spoken")
    if not isinstance(spoken, str) or not spoken.strip():
        return None
    said = reply.strip()
    if not said:
        return "empty"
    parts = set(content_words(spoken))
    parts.update(w.rstrip("stndrh") for w in list(parts) if w[:1].isdigit())
    if parts & set(content_words(said)):
        return None
    return "named no part of the date"


def _content_words(text: str) -> list[str]:
    """Lower-cased alphanumeric words, punctuation dropped. Nothing cleverer.

    Deliberately the same flattening `_normalised` does, minus the apostrophe
    carve-out that only a typed utterance needs -- these two strings are both
    machine-side. `corn.extract.content_words` is the importable form of the
    same four lines; this stays private because its contract is with
    `_normalised`, not with the extraction chain.
    """
    kept = "".join(c.lower() if c.isalnum() else " " for c in text)
    return kept.split()


def fallback_say(payload) -> str:
    """Something true to say when the turn produced no speech at all.

    **A turn that ends in silence is the worst outcome available**, and it is
    reachable four ways: the model emits `<|endoftext|>` straight after an
    observation, it writes an empty say, the call is rejected before anything
    runs, or the round budget expires mid-object. The first of those happened
    on a *successful* search -- the answer came back, was spliced in, and the
    user waited 1.9 seconds to be told nothing.

    The ladder is deference first, then the answer the tool actually found,
    then an acknowledgement that a tool ran, then an admission. Every rung is a
    true statement assembled out of the observation, so nothing here invents --
    and the ordering exists so that none of them can *contradict* the
    observation either. `NOTHING_SAID` claims the turn got nowhere, which is
    false the moment a call has succeeded, so a payload carrying a `status`
    must never reach it: a silent `place_call` answered with "I didn't get
    anywhere with that" would be telling the user a phone call did not happen
    while it was happening.

    **`COMPOSED_FIELD` is not honoured here, unlike in `deferred_say`, and the
    asymmetry is the point.** That exclusion exists to leave a good composition
    alone; when there is no composition at all, the runtime's own summary of
    the day is plainly better than silence.
    """
    if isinstance(payload, dict):
        for field in ("say", "clarify"):
            text = payload.get(field)
            if isinstance(text, str) and text.strip():
                return text.strip()
        answer = payload.get("answer")
        if isinstance(answer, str) and answer.strip():
            # `SAY_ANSWER`'s first form, `"{a}."` -- the plainest of the four
            # the corpus draws from, and the only one that adds no words of its
            # own to what the tool returned.
            return tidy_say(answer)
        # `resolve_date`'s success shape, whose whole content is a date said
        # out loud -- "Thursday". It carries no `status`, so without this rung
        # a resolved date that he then failed to speak would fall all the way
        # to an admission that nothing was resolved.
        spoken = payload.get("spoken")
        if isinstance(spoken, str) and spoken.strip():
            return tidy_say(spoken)
        if payload.get("status"):
            return DID_IT
    return NOTHING_SAID


def declaration(tools: tuple[str, ...] = (),
                offer_decline: bool = True) -> str:
    """The `tools:` line that goes above `<|user|>`, with `decline` last.

    **This is the Phase 3 format decision DATA.md says cannot be retrofitted,
    and taking it is the point of WS-E stage 1.** Until now the runtime prompted
    with a bare utterance and the model chose from a tool set it had memorised;
    from here it chooses from a set it is *shown*, which is the thirty-fourth
    finding's own recommendation and the only shape in which "none of these" is
    a member of the offered set rather than an absence.

    The shape is `corn/toolspace.py`'s, byte-for-byte -- `DECL_PREFIX`, tools
    joined by `DECL_SEP`, each rendered `name(params) -- summary`. Two formats
    for one idea is how a corpus and a runtime stop being the same interface.

    `decline` is appended last and unconditionally; see `DECLINE_LAST`. Pure and
    parameterless-by-default so `scripts/check_agent.py` can assert on it
    without a checkpoint.
    """
    from .toolspace import DECL_PREFIX, DECL_SEP

    shown = declaration_names(tools, offer_decline)
    parts = []
    for n in shown:
        t = REGISTRY[n]
        params = ", ".join(
            p.name + ("" if p.required else "?") for p in t.params
        )
        parts.append(f"{n}({params}) -- {t.summary}")
    return DECL_PREFIX + DECL_SEP.join(parts)


def declaration_names(tools: tuple[str, ...] = (),
                      offer_decline: bool = True) -> tuple[str, ...]:
    """The names `declaration` renders, in the order it renders them.

    Split out so the prompt and the grammar's narrowing cannot disagree about
    what was offered -- one function decides and both read it.

    **`offer_decline=False` withholds the escape, and it is a measurement rather
    than a setting.** WS-E stage 1 read the same configuration at nano scale and
    found routing undamaged by it -- name pass 235/224 with `decline` off the
    offer against a baseline 238/224 -- which is what makes the comparison worth
    having: whatever moves when the escape is withdrawn is what the escape was
    costing. At 260M the live suites read `routed` 5/16 with 8 of 11 declines
    landing on requests a tool plainly covered, so the question is how much of
    that is over-use of an offered escape and how much is routing.

    It is not a fix. A runtime with this on cannot say "no tool covers this" at
    all -- the thirty-fourth finding measured what he does instead, which is
    invent a tool name 190-216 times in 276. Withholding the escape trades one
    failure for another, and which trade is better is exactly what the
    measurement is for.
    """
    names = tuple(tools) or tuple(n for n in REGISTRY if n != DECLINE)
    kept = tuple(n for n in names if n != DECLINE)
    return kept + (DECLINE,) if offer_decline else kept


# **What one round appends to the context after the `<|user|>` line, at
# most** -- the model's call and say plus the runtime's observation, measured
# over 3,000 `corn.toolgen` draws at seed 5 (PLAN-CONVERSATION §4f: generated
# p50 35 / max 60, observation p50 33 / max 55, the whole addition p50 77 /
# max 114 -- 115 with the newline that closes the turn, which is what the
# context actually carries). `scripts/check_agent.py` re-measures it and asserts this constant
# is not below the draw, so a generator that grows its observations moves a
# guard rather than a cut.
#
# **Why the runtime needs the number** (PLAN-CONVERSATION 4h, 2026-09-05):
# `_prior` fits the history to `block_size - budget - 1` once at turn start,
# and `_until_marker` re-checks the same room on *every round* with a
# token-level tail cut. A turn that makes a call therefore runs its say round
# on a context that is the room plus this addition, and the cut takes the
# addition's worth of tokens off the *front* -- the `<|day|>` line and the top
# of the declaration. `Agent(round_reserve=ROUND_ADDITION)` reserves it at the
# fit, so the second round sees what the first did; `round_reserve=0` is the
# shipped path and the A/B's control.
ROUND_ADDITION = 115


def _trim_seed(entry: str, mode: str) -> str:
    """The seed entry with its content stripped back towards its shape.

    See `Agent.SEED_TRIMS` for the measurement that asked for this. `obs`
    drops the `<|obs|>` line, which is where "Sunday, September 6th" lives;
    `both` drops the `<|say|>` with it, leaving `<|user|>` and `<|call|>` --
    a shape `fold_entry`'s argument does *not* cover, so it is an arm to be
    measured rather than a default to assume.

    A deletion, like `fold_entry`: nothing here generates, and an entry that
    does not parse as expected comes back untouched rather than half-cut.
    """
    if mode == "off":
        return entry
    drop = (D_OBS,) if mode == "obs" else (D_OBS, D_SAY)
    kept = [ln for ln in entry.split("\n")
            if not any(ln.startswith(m) for m in drop)]
    out = "\n".join(kept)
    # The entry has to keep at least the turn it is there to be. If the cut
    # took everything but the user line, the seed would stop being a tool
    # turn and stop doing the one job it has.
    return out if D_CALL in out and D_USER in out else entry


def fold_entry(turn: str) -> str:
    """One history entry with its call and observation dropped, ends kept.

    **The kept form is a shape the corpus holds in quantity.** `<|user|>`
    followed directly by `<|say|>` is the `chat_day` turn -- 769,464 documents
    of it in `data/raw/chat_day_5b.txt`, counted in PLAN-CONVERSATION's
    2026-09-05 table -- so a folded history asks him to read something he has
    read a great deal of. That is the whole difference between this and a prose
    summary, which would be a novel sequence written by a model that has never
    read one and read by a model that has never read one either. Nothing here
    generates: the fold is a deletion, which is why it costs no decode and is
    `author: runtime` on the same terms as the step hatch.

    What it loses is *how* the answer was reached -- `source` lives in the
    dropped `<|obs|>`, so a folded turn cannot answer "where did you get that?".
    What it keeps is what was asked and what was said, which is what a later
    turn has to bind to.

    **An entry with no `<|say|>` comes back unchanged.** Folding one would leave
    a bare `<|user|>` line with another `<|user|>` behind it, and that is a
    context no slice contains -- the same objection `as_history` makes to
    keeping the `<|end|>`. `fit_history` drops those whole instead.

    Idempotent, so a caller may fold an already-folded entry without checking.
    Pure, for `fit_history`'s reason: `scripts/check_agent.py` decides whether
    this is right without a checkpoint.
    """
    if D_SAY not in turn:
        return turn
    kept, keeping = [], False
    # Split on the markers themselves rather than on lines: a reply may carry a
    # newline, and a line-wise filter would drop its tail. Escaped, because
    # every marker has a `|` in it and an unescaped one is an alternation.
    pattern = "(" + "|".join(
        re.escape(m) for m in (D_USER, D_CALL, D_OBS, D_SAY)) + ")"
    for piece in re.split(pattern, turn):
        if piece in (D_USER, D_SAY):
            keeping = True
        elif piece in (D_CALL, D_OBS):
            keeping = False
            continue
        if keeping:
            kept.append(piece)
    return "".join(kept)


def fit_history(history: list[str], opening: str, measure, room: int,
                fold=None) -> list[str]:
    """The prior turns that still fit in front of `opening`, oldest dropped.

    Pure given `measure`, for `split_emission`'s reason: it decides what the
    model is allowed to remember, and a guard should be able to check that
    without a checkpoint. `measure` is token length in the runtime and `len` in
    the test.

    Whole entries, never a slice. `_until_marker` keeps a token-level tail cut
    as a backstop and it is the wrong tool here -- it can land inside a marker
    and hand the model half an `<|obs|>`, a context no corpus contains. What
    came back would then be a fact about the truncation rather than about him.

    **`fold` is off by default and the default path is the shipped one, line
    for line.** Given a callable -- `fold_entry` is the one that exists -- an
    entry that will not fit is first compressed and only dropped if compressing
    every older entry still leaves it over. Oldest first, and the newest entry
    is never folded: it is the turn `reissued_query` and `copied_from` are
    about, and the whole point of the depth work is that he sees it entire.
    """
    kept = list(history)
    over = lambda: measure("".join(kept) + opening) > room
    if fold is not None:
        # Compress from the oldest end, one entry at a time, stopping the
        # moment it fits -- so a conversation pays for exactly the history it
        # cannot afford whole rather than losing every middle at the first
        # squeeze.
        for i in range(len(kept) - 1):
            if not over():
                break
            kept[i] = fold(kept[i])
    while kept and over():
        kept.pop(0)
    return kept


# **Words a query may carry without anyone having said them.** `FRAME` is
# the reply framing; the rest are the interrogative scaffolding a query is
# built out of ("what type is", "how tall is") and never the subject of one.
# A number is never a stray either -- "17 times 23" is a sum, not a leak.
_QUERY_SCAFFOLD = FRAME | frozenset({
    "what", "whats", "which", "who", "whos", "when", "where", "why", "how",
    "do", "does", "did", "is", "are", "was", "were", "be", "can", "could",
    "would", "should", "i", "you", "me", "my", "your", "we", "our", "it",
    "for", "up", "on", "with", "from", "by", "as", "or", "not", "s", "t",
    "look", "find", "search", "tell", "know", "many", "much", "long",
    "tall", "big", "old", "far", "heavy", "fast", "there", "this", "have",
    "has", "had", "get", "got", "please", "hey",
})


def contaminated_query(query: str, utterance: str,
                       prior_user_lines: Collection[str] = ()) -> str | None:
    """The first content word of `query` nobody said this conversation, or `None`.

    **The seed contaminates the argument channel by content, and content is
    countable.** PLAN-CONVERSATION 4j's reading: `mewtwo's sp atk` went out
    as `today`, lifted from the seed turn's own `resolve_date` observation;
    `read me my texts` went out as `what day is it`, the seed's user line
    itself; `what type is mewtwo` went out as `mew2`. In every case the query
    carries a word the person never typed -- this turn or any earlier one --
    and a query he copied or composed out of what was said never does.
    Reissues are deliberately *not* caught: "and italy?" sending the previous
    turn's `the capital of spain` is a real defect (chaingrid, 0/8 composed)
    but `spain` was said, one turn back, and a re-pass without the seed does
    nothing for it. Numbers and the interrogative scaffolding are exempt.

    Pure, so `scripts/check_agent.py` can hold the rule without a checkpoint;
    `Agent._contaminated` binds it to the live utterance and history.
    """
    said = set(content_words(utterance))
    for line in prior_user_lines:
        said.update(content_words(line))
    for w in content_words(query):
        if w in _QUERY_SCAFFOLD or w.isdigit():
            continue
        if w not in said:
            return w
    return None


def as_history(turn_text: str) -> str:
    """One finished turn, rendered the way the corpus stacks turns.

    **The `<|end|>` comes off, and that is the whole point.** Counted over
    `data/mix_v3_5b`, the only multi-turn shape Corn-Jr had seen until
    2026-09-05 was `corn/temporal.py`'s daycross follow-up (the social second
    turn of `corn/socialgen.py --turns 2`, arm 7, stacks the same way, and its
    `--depth 2` puts one unrelated finished exchange in front), and it stacks
    a second `<|user|>` directly onto the first turn's `<|say|>` with **one**
    `<|end|>` closing the pair:

        <|user|>what's in the log for the week before last?
        <|call|>... <|obs|>... <|say|>Which day of that week?
        <|user|>the 4th maybe
        <|call|>...
        <|end|>

    Keeping the marker would put a document boundary in the middle of a
    conversation and then ask him to carry on past it -- a context no slice
    contains, and one the corpus has specifically taught him is terminal. What
    came back from a `--multi` run assembled that way would be a fact about the
    boundary rather than about the second turn.

    Anything the model wrote *past* the marker goes with it, for the reason
    `split_emission` drops a fabricated observation: it is text from after the
    transcript ended and it was never part of the turn.

    Pure, like `fit_history` and for the same reason -- it decides what the
    model is allowed to remember, and `scripts/check_agent.py` checks that
    without a checkpoint.
    """
    body = turn_text.split(D_END)[0].split(STOP_DOC)[0]
    # Exactly one newline, so the next `<|user|>` lands where the corpus puts
    # it -- at the start of a line, against a turn that does not end in a run of
    # blank ones.
    return body.rstrip("\n") + "\n"


def framed(sink):
    """Pass streamed text through only once the round has shown a turn marker.

    Every healthy round opens with `<|call|>` or `<|say|>` -- the corpus puts
    a marker first in every round shape it contains -- so on the happy path
    this gate decides on the first two characters and holds nothing back. What
    it exists for is the round that opens with anything else: that text is
    pretraining register, not a turn, and it was being streamed to the user as
    though he were speaking -- the live receipt is 25 lines of "- Tools for
    writing code" (2026-08-29), read out by any client that speaks `text`
    events as they arrive. A muted round still reaches the terminal echo and
    the transcript, which are records; only the stream, which is speech, is
    spared. The frame-loss floor in `turn()` decides what gets said instead.
    """
    buf = ""
    passed: bool | None = None  # None undecided, True framed, False muted

    def gate(piece: str) -> None:
        nonlocal buf, passed
        if passed is False:
            return
        if passed is True:
            sink(piece)
            return
        buf += piece
        lead = buf.lstrip()
        if not lead or (len(lead) == 1 and lead == "<"):
            return  # nothing decisive yet; the next character decides
        passed = lead.startswith("<|")
        if passed:
            sink(buf)
            buf = ""

    return gate


def fill_say(reply: str, persona: Persona,
             user_named_last: bool = False) -> tuple[str, str | None, str, bool]:
    """A reply with its placeholders filled, and everything the fill decided.

    Returns `(text, why, record, named)`: the sentence to speak, why it
    cannot be spoken (`None` in the ordinary case -- no tag, or every tag
    filled), what the say event records (`filled`, a refusal reason, or
    empty when the sentence had no hole), and whether the user's name was
    spoken, which is what the next turn's `user_twice` rule reads.

    Pure, so `scripts/check_persona.py` can hold every branch without an
    agent. The `{user}` rules run on the *unfilled* text, because after
    `Persona.speak` the name is just a word and nothing says it was a tag:

        no_user       the line wants the user's name and this instance has none
        user_twice    the turn before already said it (VOICE.md rule 2)
        placeholder   a brace survived the fill -- a garbled or unknown tag
    """
    wanted_user = PLACEHOLDER_USER in reply
    had_tag = wanted_user or PLACEHOLDER_NAME in reply
    if wanted_user and not persona.user_name:
        return reply, "no_user", "no_user", False
    if wanted_user and user_named_last:
        return reply, "user_twice", "user_twice", False
    text = persona.speak(reply)
    why = unfilled(text)
    if why is not None:
        return text, why, why, False
    return text, None, ("filled" if had_tag else ""), wanted_user


def filled(sink, speak):
    """Pass streamed text through with its placeholders filled, never half.

    PLAN-PERSONALITY (second): the routed say streams, and a trained self
    line says "I'm {name}." -- so without this a voice client would have read
    "I'm {" aloud before `Persona.speak` ran on the finished sentence. The
    stage holds text from the first `{` until its `}` arrives, fills the tag,
    and releases; text with no brace in it goes straight through, so every
    checkpoint before arm 9 streams exactly as it did.

    A tag that `speak` leaves standing -- `{user}` with nothing to fill it,
    or a tag this runtime does not know -- **mutes the rest of the say**
    rather than releasing it: the sentence is going to be refused by
    `unfilled` a moment later and something else spoken in its place, and
    the half of it already heard should be as short as possible. What was
    released before the brace arrived cannot be taken back; that is the one
    fragment this stage cannot prevent, and it is at most the words before
    the name.
    """
    buf = ""
    muted = False

    def gate(piece: str) -> None:
        nonlocal buf, muted
        if muted:
            return
        buf += piece
        while buf:
            start = buf.find("{")
            if start < 0:
                sink(buf)
                buf = ""
                return
            end = buf.find("}", start)
            if end < 0:
                # Hold everything from the brace on; the words before it are
                # safe to speak and are released so the stream keeps moving.
                if start:
                    sink(buf[:start])
                    buf = buf[start:]
                return
            tag = buf[start:end + 1]
            said = speak(tag)
            if "{" in said or "}" in said:
                muted = True
                buf = ""
                return
            sink(buf[:start] + said)
            buf = buf[end + 1:]

    return gate


def stack(head: str, prior: str, user_line: str) -> tuple[str, str]:
    """The context for this turn, and the part of it the model has already seen.

    Two strings rather than one because they answer different questions and the
    turn loop needs both: the first is what goes to the model, the second is
    where *this* turn's transcript starts inside it. `turn()` slices at that
    boundary to decide what to print, what to emit and what to return, so
    getting it wrong would silently re-show the declaration or silently swallow
    the `<|user|>` line.

    Pure, and separated from `turn` for `fit_history`'s reason: the head-once
    rule is a claim about what the model was shown, and a guard should be able
    to check it without a checkpoint.
    """
    ctx = head + prior + user_line
    # Nothing is carried on the first turn -- the head is new then too.
    return ctx, (head + prior if prior else "")


# --------------------------------------------------------------------------
# The loop
# --------------------------------------------------------------------------


class Agent:
    def __init__(
        self,
        ckpt: str,
        device: str,
        temperature: float,
        world: World,
        grammar: bool = True,
        copy_slots=DEFAULT_COPY_SLOTS,
        narrow_slots=frozenset(),
        multi: bool = False,
        declare: bool = True,
        offer_decline: bool = True,
        # An empty tuple declares everything, which is every caller before
        # this parameter existed. A subset narrows the declaration and the
        # grammar together -- `declaration_names` owns the decline handling,
        # so `decline` is never a member here; `offer_decline` is its knob.
        tools: tuple[str, ...] = (),
        rephrase: bool = True,
        speech_temperature: float = 0.3,
        dtype: str = "fp32",
        fold: bool = True,
        # `fold` above is `fold_turn` on the incoming utterance and is
        # unrelated to this, which is `fold_entry` on evicted history. Two
        # different folds, named apart here because they were not.
        history_fold: bool = False,
        # PLAN-CONVERSATION 4a. `on` refuses on the family check, `log` serves
        # the reply and reports what would have been refused, `off` is the
        # runtime before the check existed. See `_own_words`.
        family_check: str = "on",
        identity_check: str = "on",
        name_header: bool = False,
        # PLAN-CONVERSATION 4h. Tokens held back from the history fit so the
        # second round of a turn is not tail-cut -- see `ROUND_ADDITION`. 0 is
        # the shipped trimmer.
        round_reserve: int = 0,
        # The generation reserve `turn` uses when its caller passes none. The
        # server has never passed one, so this is what makes `--budget` a
        # server knob rather than a CLI-only one.
        budget: int = 200,
        buckets: bool = False,
        compile_step: bool = False,
        fast_attn: bool = False,
        prefix_reuse: bool = False,
    ):
        # `fp32` by default and deliberately: see `load_checkpoint`. Both
        # decoders take their dtype from the model's own parameters, so this
        # one argument moves the whole runtime and there is no second place
        # the two could disagree.
        self.model, self.cfg, self.tok, self.ckpt = load_checkpoint(
            ckpt, device, dtype)
        # Sampling leaves the captured region when the grammar is on, because a
        # mask that depends on the parse state cannot be captured. The model's
        # launches are still collapsed into one replay and the logits are the
        # same ones the eager path computes -- see `decode.set_processor`.
        self.dec = GraphedDecoder(
            self.model,
            device,
            use_graph=True,
            temperature=temperature,
            top_k=0,
            graph_sampling=not grammar,
            # The decode-speed opt-ins, off by default so every scorer and
            # guard that constructs an Agent keeps the path it has always
            # measured. The first two hold exact greedy parity
            # (`check_decode.py`) and `compile_step` pays minutes of Inductor
            # at first construction. **`fast_attn` is the one that changes
            # rounding** -- see `CausalSelfAttention.step`. It is fine for
            # talking to him and must stay off wherever a scorecard is made,
            # which is why nothing in `corn/evals.py` passes it.
            bucket_slots=(default_buckets(self.model.cfg.block_size)
                          if buckets else None),
            compile_step=compile_step,
            attn="manual" if fast_attn else "sdpa",
        )
        # **The declaration and the narrowing are one decision, taken
        # together.** Showing a tool set and then accepting names outside it
        # would be a declaration the runtime does not mean; narrowing without
        # showing the set would be a constraint the model was never told about.
        # `--no-declare` turns off both, and is the pre-WS-E runtime exactly.
        # `offer_decline=False` keeps both on and takes one name out of each,
        # which is why it is passed to the pair rather than applied to one --
        # a narrowing that still admitted `decline` after the prompt stopped
        # showing it would be the exact disagreement this comment forbids.
        self.declared = (declaration_names(tools, offer_decline)
                         if declare else None)
        self.decl_line = (
            declaration(tools, offer_decline) + chr(10)) if declare else ""
        self.constraint = (
            CallConstraint(self.tok, device, copy_slots=copy_slots,
                           narrow_slots=narrow_slots,
                           declared=self.declared)
            if grammar else None
        )
        self.dec.set_processor(self.constraint)
        # Kept because `_own_words` swaps sampling for the length of one
        # speech generation and has to put back what the call path was using.
        self.temperature = temperature
        self.device, self.world = device, world
        self.multi = multi
        # One finished turn per entry, oldest first, each already through
        # `as_history` -- so what is stored is the stacked-turn body and never
        # the `<|end|>` that closed it. Only ever appended to when `multi` is
        # on, so the default runtime is turn-independent exactly as it was.
        self.history: list[str] = []
        # **The seed -- shipped 2026-09-05, set by the server from its config.**
        # The misroute grid of that day read every tool family routing three
        # to five times better with any tool turn in the history than on an
        # empty one, on `ft4g` and `social8` alike: "note down buy milk"
        # declines 6/6 first and saves every time second. The corpus explains
        # it -- its 1,720 two-turn transcripts all put `<|call|>` after the
        # second `<|user|>`, and no single-turn transcript is followed by
        # anything -- so a first turn was taught nothing the second turn
        # knows. The seed is a user utterance the runtime runs through
        # `turn()` itself on every `reset_history()`, so the history is never
        # empty; "what day is it" costs about a millisecond because the
        # temporal hatch answers it without a decode. Read against the grid's
        # first-turn half it reproduces the after-tool column to the cell
        # (STATUS 2026-09-05). `None` here so a bare `Agent` -- every guard,
        # every eval -- is exactly the runtime it was.
        self.seed_turn: str | None = None
        self.seed_text: str | None = None
        # How much of the seed's own text stays in the context. `off` is the
        # shipped runtime; see `SEED_TRIMS` for the two arms and the numbers
        # that asked for them. Set beside `seed_turn` by the server.
        self.seed_trim: str = "off"
        # 4j/4k: decode a routed search call a second time without the seed
        # and keep it only if it routes the same way. `off` on a bare Agent,
        # like `multi`, so every guard and eval builds the runtime it always
        # built; the server sets the shipped mode from `ServerConfig`. See
        # `_repass` and `SEED_REPASS_MODES`.
        self.seed_repass: str = self.SEED_REPASS_DEFAULT
        # The last few runtime-authored replies, newest last, read by `_pick`
        # so a pool cannot say the same thing twice running. Unlike `history`
        # this is kept whether or not `multi` is on: repeating yourself is a
        # single-turn defect and does not become one only when the turns are
        # stitched together. It holds nothing the model wrote -- a `say` the
        # model composed is not drawn from a pool, so excluding it would mean
        # nothing to `_pick`.
        self.recent: deque[str] = deque(maxlen=RECENT_SAYS)
        # **The two placeholders, and the one rule about the user's name that
        # the weights cannot be trusted with.** PLAN-PERSONALITY §4d: a name
        # every turn is VOICE.md rule 2's tic, so a `{user}` line is refused
        # when the turn before it already said the name. `user_named_last`
        # is what the previous spoken turn did; `_user_named` is this turn's,
        # and `turn()` rotates them. `placeholder` is what the last fill did,
        # for the say event -- `filled` when a tag was replaced, empty when
        # the sentence had none.
        self.user_named_last = False
        self._user_named = False
        self.placeholder = ""
        # **On by default, and `--restrict` is what turns it off.** The pool
        # answer is computed either way and is what gets spoken when his own
        # attempt does not clear `social_rejection`, so this flag changes who
        # writes the sentence and never whether there is one. Off, the runtime
        # is exactly what it was before the rephrase path existed, which is
        # what makes it a usable control rather than only a safety valve.
        self.rephrase = rephrase
        # **A call and a sentence want opposite sampling, and one number was
        # serving both.** `--temperature` defaults to 0.0 because a tool call
        # is a structured object with one right answer and greedy is how you
        # get it -- the grammar masks the rest. Speech is the other case
        # exactly: greedy makes his social replies deterministic, so the same
        # greeting comes back forever and the pool it replaced was more varied
        # than he is. Only `_own_words` reads this, and it restores the call
        # setting afterwards, so nothing about routing changes.
        #
        # **0.3 is measured rather than picked.** Six social turns, six samples
        # each, counting how often his reply survived `social_rejection` and
        # how many distinct sentences came back:
        #
        #     0.0   kept 30/36   10 distinct   the same four replies forever
        #     0.3   kept 29/36   24 distinct
        #     0.5   kept 24/36   32 distinct
        #     0.7   kept 24/36   34 distinct   "I can't get to the way to the
        #                                       lane." cleared the check
        #
        # 0.3 buys 2.4x the variety of greedy for one rejection in thirty-six.
        # Past it acceptance falls and what it buys is mostly drift -- the
        # check catches a name and a number, and cannot catch a grammatical
        # sentence about nothing.
        self.speech_temperature = speech_temperature
        # **On by default -- owner decision 1b/0, re-taken 2026-08-30 after its
        # own gate retired the strip half.** What ships is the casefold, which
        # `harness/foldgate.py` and `surfacegrid` between them price at 39 of 57
        # recovered and nothing measurable spent. `--no-fold` is the control.
        #
        # A flag rather than a constant, for the reason the gate demonstrated:
        # the fold is upstream of every live read and ground rule 13 re-dates
        # all of them the day it lands, so a before/after has to be runnable on
        # one instance with nothing else moved. A transform that could only be
        # switched by editing the source would have made that pair unreadable,
        # and the strip would have shipped.
        self.fold = fold
        self.history_fold = history_fold
        if family_check not in ("on", "log", "off"):
            raise ValueError(f"family_check {family_check!r} is not on, log or off")
        self.family_check = family_check
        # **The identity hatch in log mode -- PLAN-PERSONALITY §7.** `on` is
        # the runtime as it was: "who are you" is answered from the pools
        # before the model is asked. `log` lets the turn route so the weights
        # answer (arm 9's class), and records the line the hatch would have
        # said as `identity_pool` on the say event, so the ledger can read
        # `draft_fails` on the rule that is up for deletion. Never `off`: a
        # hatch that is neither answering nor counting is a hatch nobody can
        # read, and the capability answer (`CAPABILITY`, `TOOLS_ASKED`) is
        # not this switch's -- it stays runtime-composed under both modes.
        if identity_check not in ("on", "log"):
            raise ValueError(f"identity_check {identity_check!r} is not on or log")
        self.identity_check = identity_check
        self.identity_pool = ""
        # See `turn()`'s head: the `name:` line, for checkpoints trained on it.
        self.name_header = bool(name_header)
        self.round_reserve = int(round_reserve)
        self.budget = int(budget)
        # **Keep the KV of whatever prefix a round shares with the one before
        # it. Measured, and it is a null -- 1.02x.** Left in because it is
        # correct and costs nothing, and because deleting it would invite the
        # next person to have the same good idea and spend the same day.
        #
        # The redundancy is real: 42.1% of a turn's prefill tokens are ones
        # the previous round already read, with the 151-token declaration
        # re-encoded every round of every turn
        # (`scripts/prefill_redundancy.py`). Skipping 72% of round 2's tokens
        # on the 260M shape saved **0.22 ms of 10.63** and 0.3% of the round.
        #
        # The reason is the sixty-fourth finding: **prefill does not cost
        # tokens, it costs launches** -- 8.1 to 8.8 ms flat from 16 tokens to
        # 511. Cutting the token count optimises a variable the wall clock
        # does not depend on. The lever that does move it is static shapes and
        # fusion, which is a different change to a different place.
        #
        # It is exact where it applies, and `wpe` is why: learned absolute
        # positions make position i's K and V independent of everything after
        # i. Off by default -- it makes the decoder stateful across calls, and
        # nothing producing a scorecard should acquire cross-call state
        # without being asked to.
        self.prefix_reuse = prefix_reuse
        # Kept only so a card can state the decode path it was taken under.
        # Both are consumed by `GraphedDecoder` above and neither is read
        # again here -- but a scorecard whose `instance` cannot name them
        # describes a machine the reader cannot rebuild.
        self.buckets = buckets
        # What happened, not what was asked: `GraphedDecoder` falls back to
        # the eager step when Inductor's backend is missing or fails, and a
        # card that said `compile_step: true` on that machine would describe
        # a decode path that never ran.
        self.compile_step = getattr(self.dec, "compiled", compile_step)

    # ------------------------------------------------------------------
    # The seed's content, as against the seed's shape -- 2026-09-06
    # ------------------------------------------------------------------
    #
    # **The seed helps by its shape and hurts by its content, and the two are
    # separable.** The misroute grid's win is structural: a `<|call|>` sitting
    # in the history is what turns a first turn into the second turn the
    # corpus actually taught, and notes go 177 -> 702 of 1,000 on it. The
    # damage is textual: `web_search.query` is *not* a copy slot
    # (`DEFAULT_COPY_SLOTS` is the two contact slots and nothing else), so the
    # query is freely generated and whatever the seed left in the context can
    # walk into it. Measured the same day over ten pack questions with a gold
    # value each:
    #
    #     position 1, first turn        seeded 7/10     --seed-turn ''  10/10
    #     position 2, behind a note     seeded 7/10     --seed-turn ''   7/10
    #
    # -- pure cost on the first turn and nothing at all on the second, on a
    # family whose turn-1 routing never needed the help (`search.route_*` is
    # 200/200). The two species seen: `mewtwo's sp atk` sending the query as
    # `today`, which is the seed call's own `expression` argument, and a
    # Pokemon question answered "It was Sunday, September 6th.", which is the
    # seed's observation and say two turns later.
    #
    # So these modes strip the seed back towards its shape. `off` is the
    # shipped runtime and the control every card before today was read under.
    #
    # **Both arms were run the same day and both are refused by the numbers.**
    # On the ten pack questions, position 1:
    #
    #     off 7/10      obs 7/10      both 5/10      --seed-turn '' 10/10
    #
    # `obs` changes nothing because the leaking word is in the *call*:
    # `resolve_date`'s own `expression` argument is the string `today`, and
    # taking the observation away leaves it exactly where it was. `both` is
    # worse, and worse in a new way -- with no completion after the call the
    # model reads the seed's *user line* as the live question and sends
    # `what day is it` as the query on three of the ten, answering "It's
    # every morning."
    #
    # So the seed's shape and its content are not separable: the call **is**
    # content. The knob stays because a refuted arm with a number on it is
    # worth more than a paragraph saying somebody tried, and because `off`
    # is the control -- but neither other mode is a candidate for a default.
    # The fix this evidence actually points at is a two-pass turn: route with
    # the seeded context, emit the arguments without it, which is where
    # `_unseeded` already points. That is a card, not a flag.
    SEED_TRIMS = ("off", "obs", "both")

    def reset_history(self) -> None:
        """Forget the conversation, then plant the seed turn if one is set.

        The one place a reset happens, so the seed cannot be forgotten by a
        caller that cleared the list directly. Nothing is emitted or printed
        for the seed: it is scaffolding the runtime wrote, and a client that
        saw it would think someone had asked.
        """
        self.history.clear()
        if not self.seed_turn:
            return
        # Under `multi` the seed lands in the history the way any turn does.
        # Without it the history is not kept between turns -- but the seed is
        # not a turn of the conversation, it is the floor every turn stands on,
        # so it is appended regardless and `turn()` stacks a non-empty history
        # whether or not `multi` is on. Each real turn still appends nothing
        # when `multi` is off, so the runtime stays turn-independent above the
        # seed exactly as it was.
        was = self.multi
        self.multi = True
        try:
            self.turn(self.seed_turn, echo=False)
        finally:
            self.multi = was
        # The entry as stacked, kept so the two readers below can take it
        # back off. `None` if the seed turn appended nothing.
        self.seed_text = self.history[0] if self.history else None
        if self.seed_trim != "off" and self.seed_text:
            trimmed = _trim_seed(self.seed_text, self.seed_trim)
            self.history[0] = self.seed_text = trimmed

    # **The tools whose *arguments* the seed corrupts, 4j.** One entry,
    # because one family was measured to suffer: `web_search` is the only
    # tool whose argument is a free-form string the model composes rather
    # than a span the copy grammar holds, so it is the only one the seed's
    # own words can walk into. `place_call.contact` and `send_text.contact`
    # are copy slots and `save_note.text` is a narrow one; all three are
    # constrained against a source `_unseeded` has already cleaned.
    SEED_REPASS_TOOLS = frozenset({"web_search"})
    # `off` is the control; `always` is 4j as measured (every routed search
    # call decoded twice: 8/10 pack answers at position 1 against 7/10 off,
    # PLAN-CONVERSATION 4j); `contaminated` is 4k, the same second decode
    # gated on `contaminated_query` and floored by the utterance. Restated in
    # `harness/serverconfig.py` and held equal by `check_serverconfig.py`.
    SEED_REPASS_MODES = ("off", "always", "contaminated")
    SEED_REPASS_DEFAULT = "off"

    def _repass(self, ctx: str, head: str, emitted: str, raw: str | None,
                budget: int, guard_say: bool) -> tuple[str, str | None]:
        """Decode this round again without the seed, and keep the better call.

        **The seed decides which tool; it must not decide what argument.**
        PLAN-CONVERSATION 4j has the readings; the short version is that on
        ten pack questions the seed costs 3 of 10 on a first turn and nothing
        on a second, because `web_search.query` is not a copy slot and the
        seed's own `resolve_date{"expression": "today"}` can be copied into a
        generated query. Trimming the seed entry cannot fix it -- the call is
        content, and both trims were refused (`SEED_TRIMS`).

        What *can* be split is the decode. By the time a valid call exists the
        seed has already done its whole job, so the round is decoded once more
        from the same context with the seed taken off, and the second call is
        kept only if it is a valid call **to the same tool**. Anything else --
        no call, a different tool, a malformed one -- leaves the first pass
        standing. So this can only ever change an argument, never a routing
        decision, and its worst case is the runtime it already is plus one
        decode on a search turn.

        Returns `(emitted, raw)` because the emission carries the call text.

        **4k (2026-09-07) gates it and floors it.** 4j ran on every routed
        search call and missed its bar; the argument channel it fixed, it
        fixed exactly. Under `contaminated` the second decode runs only when
        `contaminated_query` finds a word in the query nobody said, and a
        query still contaminated after the second decode is replaced by the
        utterance itself. Under `always` this is 4j byte for byte.
        """
        mode = self.seed_repass
        if (mode == "off" or raw is None or not self.seed_text
                or D_CALL not in emitted):
            return emitted, raw
        first = validate_call(raw)
        if not first["ok"] or first["name"] not in self.SEED_REPASS_TOOLS:
            return emitted, raw
        query = first["arguments"].get("query")
        query = query if isinstance(query, str) else ""
        # **4k: only a contaminated query is worth a second decode.** A
        # query built out of what the person said is left exactly as it
        # was, at no cost; see `contaminated_query` for what "said" means.
        if mode == "contaminated" and self._contaminated(query) is None:
            return emitted, raw

        def replaced(raw_new: str) -> tuple[str, str]:
            # The emission's own call text goes with it, or the context
            # would hold one call and the executor would run another.
            return emitted.rsplit(D_CALL, 1)[0] + D_CALL + raw_new, raw_new

        clean = head + self._unseeded(ctx[len(head):])
        if clean != ctx:                 # something to take off
            again = self._until_marker(clean, budget, guard_say=guard_say)
            _, raw2 = split_emission(again)
            second = validate_call(raw2) if raw2 is not None else None
            if (second is not None and second["ok"]
                    and second["name"] == first["name"]):
                query2 = second["arguments"].get("query")
                query2 = query2 if isinstance(query2, str) else ""
                if mode == "always" or self._contaminated(query2) is None:
                    return replaced(raw2)
        if mode != "contaminated":
            return emitted, raw
        # **The floor: a query that is still not the person's words is
        # replaced by the person's words.** The utterance is the span he
        # would have copied on a clean context (searchgrid: 400/400 kept the
        # subject), the packs and the query-side backstop both read it
        # correctly, and the worst case is the honest miss -- "I couldn't
        # find anything useful for ..." -- in place of a lookup of `today`.
        asked = (getattr(self.world, "last_user", "") or "").strip()
        if not asked:
            return emitted, raw
        args = dict(first["arguments"])
        args["query"] = asked
        return replaced(json.dumps({"name": first["name"], "arguments": args}))

    def _birthdays(self) -> dict[str, tuple[int, int]]:
        """`{"my": (m, d), "your": (m, d)}` from the persona files, as known.

        `my` is the owner's (`about-me.md`, kind `owner_birthday`), `your`
        is his (`persona.md`, kind `birthday`). Read by `temporal_request`
        to turn "days till my birthday" into a day the date tool reads.
        """
        out: dict[str, tuple[int, int]] = {}
        for o in self.world.persona.occasions:
            if o.kind == "owner_birthday":
                out.setdefault("my", (o.month, o.day))
            elif o.kind == "birthday":
                out.setdefault("your", (o.month, o.day))
        return out

    def _contaminated(self, query: str) -> str | None:
        """`contaminated_query` against this turn's utterance and the history.

        The seed's own user line is *not* among the lines the person said:
        it is `history[0]` while `seed_text` is set, and the whole point is
        that its words count as nobody's. Under `--no-multi` the history
        holds only the seed, so "said" is this turn alone.
        """
        asked = getattr(self.world, "last_user", "") or ""
        prior: list[str] = []
        for i, entry in enumerate(self.history):
            if i == 0 and self.seed_text and entry == self.seed_text:
                continue
            for chunk in entry.split(D_USER)[1:]:
                prior.append(chunk.split("\n", 1)[0])
        return contaminated_query(query, asked, prior)

    def _unseeded(self, below: str) -> str:
        """`below` -- the context under the head -- without the seed in front.

        **The seed is scaffolding, and two readers must not see it.** The copy
        grammar's wide source is "everything said in this conversation", and
        on the first seeded live turn it read the seed as said: "text mom that
        i will be late" copied `today` out of the seed's `resolve_date` call
        and asked after a contact called today. And `_own_words` reads the
        same context to reword a greeting, where finding 128 already measured
        that a tool turn costs the next social move a third of its answers --
        a seed that every greeting followed would charge that on every
        conversation's first hello. Both get the context with the seed taken
        off; the *model's routing* still sees it, which is the whole point.

        A prefix match rather than a slice by length because `fit_history` may
        fold or evict the entry when the room is tight; if the front of the
        context is no longer the seed as stacked, nothing is removed.
        """
        if self.seed_text and below.startswith(self.seed_text):
            return below[len(self.seed_text):]
        return below

    def _prior(self, opening: str, budget: int) -> str:
        """`fit_history` against this checkpoint's block size and tokenizer.

        `opening` is everything that will sit outside the kept turns -- the
        `<|day|>` header and the declaration in front of them, this turn's
        `<|user|>` line behind -- passed as one string because only its
        *length* is read. The concatenation order here is not the assembly
        order and does not need to be; what is being asked is whether the whole
        thing fits.
        """
        room = self.model.cfg.block_size - budget - self.round_reserve - 1
        self.history = fit_history(
            self.history, opening, lambda s: len(self.tok.encode(s)), room,
            fold=fold_entry if self.history_fold else None,
        )
        return "".join(self.history)

    def _until_marker(self, context: str, budget: int, on_text=None,
                      guard_say: bool = False) -> str:
        """Generate until a marker the runtime owns, or until `budget` runs out.

        Stopping is matched on decoded text rather than on token ids because the
        delimiters are ordinary bytes at this vocabulary. Decoding the whole
        accumulated list each step is quadratic and irrelevant: the budget is
        two hundred tokens and the model runs at 385/s.

        **A marker inside an open call does not stop anything.** `<|obs|>` is
        printable ASCII and a JSON string body will take it, so a model that
        emits one mid-object would otherwise hand `split_emission` a call cut in
        half -- the constraint masks the marker ids for that reason and this
        check stands down for the same one, so the defence does not depend on
        the vocabulary keeping its markers atomic.
        """
        ids = self.tok.encode(context)
        # No sliding window, same as `chat.py` -- keep the tail that fits.
        room = self.model.cfg.block_size - budget - 1
        if len(ids) > room:
            ids = ids[-room:]
        idx = torch.tensor([ids], dtype=torch.long, device=self.device)
        out: list[int] = []
        # How much of the decoded text an `on_text` sink has already been shown.
        # Tracked in characters rather than tokens because the decode is what
        # the caller sees, and a BPE token is not a character boundary.
        sent = 0
        for tok in self.dec.stream(idx, budget, reuse=self.prefix_reuse):
            out.append(tok)
            # **A closed call ends the round.** The corpus puts `<|obs|>` on the
            # next line and the runtime supplies the real one, so everything
            # after the closing brace is discarded by `split_emission` anyway --
            # generating it is pure cost. It is also not harmless: at 260M the
            # model wrote a valid `place_call` and then 36 more `}`, and the
            # trailing braces turned a good call into `not_json`. The grammar
            # cannot stop this itself; it is disarmed at the close, which is
            # exactly what `closed` records.
            if self.constraint is not None and self.constraint.closed:
                return self.tok.decode(out)
            if self.constraint is not None and self.constraint.armed:
                # Mid-call. Deliberately silent: what is being built here is a
                # call the runtime may refuse to execute, and streaming it would
                # show the user a half-written object as though it were speech.
                continue
            text = self.tok.decode(out)
            # **Stopped here rather than trimmed afterwards, so a streaming
            # client never hears it.** `on_text` has already spoken everything
            # up to `sent`; cutting only the returned string would leave the
            # payload read aloud and merely absent from the transcript, which
            # is the half-fix that looks like a fix. Stopping also gives the
            # budget back -- the spill ran to six `<|say|>` segments.
            if guard_say:
                cut = say_cut(text)
                if cut is not None:
                    text = text[:cut]
                    if on_text is not None and len(text) > sent:
                        on_text(text[sent:])
                    return text
            if on_text is not None and len(text) > sent:
                on_text(text[sent:])
                sent = len(text)
            # `D_USER` is in the set because `split_emission` drops everything
            # from a model-written user line on: generating past it is budget
            # spent on a round that will be discarded, and streaming past it
            # reads the invented question aloud before the cut can land.
            if any(m in text for m in (D_OBS, D_END, STOP_DOC, D_USER)):
                return text
        return self.tok.decode(out)

    def _fill(self, reply: str) -> tuple[str, str | None]:
        """`fill_say` against this instance, with its state written back.

        `placeholder` is recorded for the say event either way, so a row can
        say whether the sentence had a hole in it; `_user_named` is set only
        when the user's name was actually spoken, which is what the next
        turn's `user_twice` rule reads.
        """
        text, why, record, named = fill_say(reply, self.world.persona,
                                            self.user_named_last)
        self.placeholder = record
        if named:
            self._user_named = True
        return text, why

    def _own_words(self, ctx: str, budget: int = 60,
                   family: str | None = None) -> tuple[str | None, str, str, str]:
        """His own reply to a social turn, or `None` and the reason it failed.

        Four elements since PLAN-CONVERSATION 4a: the reply or `None`, the
        reason it was refused, the attempt itself, and a *soft* reason -- a
        family miss the runtime served anyway and reports as `soft_reject`.
        `family` is the hatch family the turn matched; with none, or with the
        check `off`, only `social_rejection` reads the reply.

        **The say marker is supplied rather than waited for.** The runtime has
        already decided this turn is social, and the probe that motivated this
        path found he would not have reached `<|say|>` on his own: "thanks",
        "hello" and "goodbye" opened a tool call 16 times out of 16. Prefilling
        the marker asks the question that is actually being asked -- given that
        this is a social turn, what would he say -- and leaves the routing
        where it was measured to belong.

        The budget is small because a social reply is one sentence and the
        failure mode at the far end is narrative that runs until something
        stops it. Nothing here streams: `on_text` is deliberately not passed,
        because a client that spoke his attempt as it arrived would have read
        out "Hello, this is Graham." before the check could reject it. That is
        `_until_marker`'s own argument about the payload spill, and the
        deferred-say path makes it too.
        """
        if self.constraint is not None:
            self.constraint.set_source(ctx)
        # Restored in `finally` rather than after the call, because a raise
        # here would otherwise leave the tool path sampling -- a failure that
        # would show up as worse routing two turns later and look like the
        # model. `set_sampling` is free while the grammar is on: what would
        # need recapturing is `topk`'s baked-in `k`, and `graph_sampling` is
        # already off in that case. See `GraphedDecoder.set_sampling`.
        previous = self.temperature
        try:
            self.dec.set_sampling(temperature=self.speech_temperature)
            chunk = self._until_marker(ctx + D_SAY, budget)
        finally:
            self.dec.set_sampling(temperature=previous)
        body = chunk.split(D_END)[0].split(STOP_DOC)[0]
        for marker in (D_USER, D_CALL, D_SAY, D_OBS):
            body = body.split(marker)[0]
        # **The record he writes under the say** (PLAN-TAG-SPINE §2b, phase
        # D): a `state:` line after the reply, read off the emission here and
        # put back into the history by the caller as text he wrote. Never
        # served, never a gate on the words; a checkpoint that writes none
        # leaves `None`, and the turn is the turn it always was.
        reply, self._say_state = split_state(body.strip())
        reply = reply.strip()
        # **The placeholders are filled before any check reads the sentence**,
        # so what `social_rejection` and the family check judge is what the
        # person hears. Three refusals of its own, each a reason the log can
        # count (PLAN-PERSONALITY §4c, §4d): `no_user` -- the line wants the
        # user's name and this instance has none; `user_twice` -- the turn
        # before already said it; `placeholder` -- a brace survived the fill,
        # which is a garbled tag or one nothing fills.
        reply, why = self._fill(reply)
        # **His own name is speakable when it is his own name.** A renamed
        # instance whose model says the new name in a rephrased greeting would
        # otherwise be caught by the rule that exists to catch *invented*
        # names -- see `_stray_capital`. Nothing else about the check moves,
        # and on an instance with no persona file the argument is empty.
        if why is None:
            why = social_rejection(reply, self.world.persona.caps)
        # **The family check -- the rule the eval had and the server did not.**
        # `corn.socialfam.family_rejection` is what `social.family` scores
        # with; until 2026-09-05 "That sounds great. I'll take it." passed
        # `social_rejection` as a farewell because it is a finished, unnamed,
        # undigited sentence. Split hard/soft for the reason given there; in
        # `log` mode the hard half is demoted to soft so a replay can say what
        # would have been refused without refusing it.
        soft = ""
        if why is None:
            why, soft = family_verdict(reply, family, self.family_check)
        # **The third element is what the seventy-eighth finding could not
        # count.** `fell_back` has always said that a reply was refused and
        # never what it was, so every rate in that audit had to be measured
        # against a second server instead of read off the rows. `reply` goes
        # back whether it survived or not; the caller records it as
        # `model_draft` on the turns where the user heard something else.
        return (None if why is not None else reply), (why or ""), reply, soft

    def _mark_occasion(self, occasion: Occasion | None) -> str:
        """The occasion sentence, once a day, or `""` every other time.

        **The record is written here rather than by the caller**, because "has
        he said it yet" and "say it" have to be one step: two turns arriving
        close together on the first morning of a birthday would otherwise both
        read "not yet" and both say it. Reading and writing in one place is
        what `range_span`'s lifecycle does for the same reason.

        Two records, and the second one is the file. `world.occasion_said`
        covers the life of this process and is all a guard or an eval needs;
        `world.marker` is the disk copy, and it is what makes a server
        restarted at lunchtime on his birthday stay quiet about it. A marker
        that cannot be written costs a repeated sentence and never a turn --
        see `Marker`.
        """
        self._marked_kind = ""
        today = self.world.anchor
        marker = self.world.marker
        if occasion is None or self.world.occasion_said == today:
            return self._mark_heads_up()
        if marker is not None and marker.said(today):
            self.world.occasion_said = today
            return self._mark_heads_up()
        said = _occasion_say(occasion, self.world.rng, today,
                             self.world.persona, self.recent)
        self.world.occasion_said = today
        if marker is not None:
            marker.record(today)
        self._marked_kind = occasion.kind
        return said

    def _mark_heads_up(self) -> str:
        """A people-store birthday coming up, once per birthday, or `""`.

        Rides where the day's own mention rides (a social or identity reply)
        and only when that mention has nothing to say this turn -- one
        appended sentence a turn, never two. "Once" is per birthday, not per
        day (`Persona.heads_up`): the key goes to the process set and the
        marker in the same step it is said, `_mark_occasion`'s reason.
        """
        today = self.world.anchor
        marker = self.world.marker
        world = self.world

        def done(key: str) -> bool:
            return key in world.heads_up_said or (marker is not None and marker.heads_up_said(key))

        occasion = world.persona.heads_up(today, done)
        if occasion is None:
            return ""
        key = heads_up_key(occasion, today)
        world.heads_up_said.add(key)
        if marker is not None:
            marker.record_heads_up(key)
        self._marked_kind = occasion.kind
        return _occasion_say(occasion, world.rng, today, world.persona, self.recent)

    def turn(
        self,
        user: str,
        rounds: int = 4,
        budget: int | None = None,
        day: bool = False,
        echo: bool = True,
        emit=None,
    ) -> str:
        """One user utterance, run to `<|say|>` or to a refusal. Returns this
        turn's transcript, which is the honest record: what the model wrote and
        what the tools actually returned, with nothing spliced in the other
        direction. Under `--multi` the prior turns are in front of it in the
        model's context and are not part of what comes back.

        `emit` is the same turn observed rather than printed, for callers that
        are not a terminal -- `harness/server.py` is the one that exists. It is
        **additive**: every `print` below is unchanged and still gated on
        `echo`, so the CLI's output is byte-identical whether or not a sink is
        attached. Two sinks rather than one formatter because they want
        different things -- a terminal wants the grammar's bites spelled out in
        prose, a client wants the count as a number -- and collapsing them
        would have meant a client parsing English.
        """
        def _emit(kind: str, **fields) -> None:
            if emit is not None:
                emit({"t": kind, **fields})
        # **The fold, and it is the first thing that happens to the utterance.**
        # `fold_turn`'s block comment carries the decision and the measurement;
        # what matters here is the position. Everything below this line -- the
        # `<|user|>` line, the history, `last_user` and so the copy grammar's
        # source, and every hatch matcher -- reads `user`, so folding it once
        # here is what makes the fold a property of the runtime rather than of
        # whichever caller remembered. The raw utterance is not thrown away: it
        # goes out on the event, which is where `harness/sessionlog.py` lifts
        # it from, because a log that quietly recorded the folded text would
        # mix two surface populations in one column and no future count over it
        # could tell them apart.
        if budget is None:
            budget = self.budget
        # The `{user}` window rolls forward one turn -- see `_fill`.
        self.user_named_last, self._user_named = self._user_named, False
        self.placeholder = ""
        self.identity_pool = ""
        raw = user
        if self.fold:
            user = fold_turn(user)
        if user != raw:
            _emit("fold", raw=raw, folded=user)
            if echo:
                print(f"  ~~ folded {raw!r} -> {user!r}")
        # **The head is written once per conversation, not once per turn.**
        # Both markers in it are outermost-and-single in the corpus that has
        # them: `corn/toolspace.py` puts the declaration immediately above the
        # *first* `<|user|>`, `corn/temporal.py` puts `<|day|>` above that, and
        # its two-turn transcripts repeat neither when the second `<|user|>`
        # arrives -- so the one thing that can be got right is that each marker
        # sits where its own corpus has it, including how often.
        head = ""
        # **His name, first, when the checkpoint was taught to read it there.**
        # PLAN-PERSONALITY (sixth): the corpus puts `name: X` as the first line
        # of a named transcript, above the day and the declaration, and the
        # runtime puts it in the same place with the persona's name -- the
        # one design in which he *copies* his name rather than recalls it.
        # Off by default: a checkpoint that never saw the line is handed the
        # context it was measured on.
        if self.name_header:
            head += name_header(self.world.persona.name)
        if day:
            head += f"<|day|>{self.world.anchor.isoformat()} "
            head += f"{self.world.anchor.strftime('%A')}\n"
        head += self.decl_line
        user_line = f"{D_USER}{user}\n"
        # Trimming happens against this turn's opening *and* the head, so the
        # check is "what still fits with the new question and the declaration in
        # it" rather than "what fitted last time".
        # `or self.history`: with `multi` off the only thing that can be in the
        # history is the seed turn, and it is stacked -- see `reset_history`.
        prior = (self._prior(head + user_line, budget)
                 if (self.multi or self.history) else "")
        ctx, carried = stack(head, prior, user_line)
        # What is new this turn: the head only when nothing carried it in.
        # Printed and emitted rather than `ctx` because a client watching a
        # conversation should see the turn, and a declaration it was already
        # shown has not been made again.
        opening = ctx[len(carried):]
        if echo:
            print(opening, end="")
        _emit("opening", text=opening)
        self.world.last_user = user

        # **The step hatch -- `corn/steps.py`, gated on a live recitation.**
        # Same shape as the recheck hatch below and for the same reason: the
        # state that answers "what's next" is a position in a document, the
        # runtime holds it, and the model's half of a recitation is reading a
        # span back. The say is composed here rather than generated because
        # the answer *is* the step, verbatim -- a recipe is the case where
        # span fidelity is the whole product -- and `author: runtime` keeps
        # these rows countable and untrainable, which is ground rule 4. The
        # gate is `.live`: with no recitation running these phrases fall
        # through to the router exactly as they did before this existed.
        cursor = getattr(self.world, "steps", None)
        want = step_request(user) if cursor is not None and cursor.live else None
        if want is not None:
            # Read before the call: `stop` and the end of a recipe clear the
            # cursor, and the written call should still name what was being
            # read rather than searching for an empty string.
            reading = cursor.title
            payload = {"next": cursor.advance, "repeat": cursor.repeat,
                       "stop": cursor.stop}[want]()
            query = payload.get("query") or reading
            raw = json.dumps({"name": "web_search",
                              "arguments": {"query": query}})
            if echo:
                print(f"{D_CALL}{raw}")
            _emit("call", raw=raw, ok=True, why="", name="web_search",
                  arguments={"query": query}, masked=0,
                  held=[], released="", author="runtime")
            shown, _ = take_runtime(payload)
            ctx += D_CALL + raw + "\n" + D_OBS + json.dumps(shown) + "\n"
            if echo:
                print(f"{D_OBS}{json.dumps(shown)}")
            _emit("obs", name="web_search", payload=shown)
            said = shown.get("answer") or shown.get("say") or ""
            ctx += D_SAY + said + D_END + "\n"
            if echo:
                print(f"{D_SAY}{said}{D_END}")
            _emit("say", text=said, deferred=False, author="runtime")
            turn_text = ctx[len(carried):]
            if self.multi:
                body = (turn_text[len(head):]
                        if turn_text.startswith(head) else turn_text)
                self.history.append(as_history(body))
            _emit("done", transcript=turn_text)
            return turn_text

        # Social turns are a small, well-defined escape hatch from the tool
        # router. Keeping the reply in the same transcript shape means clients
        # and `--multi` history do not need a special case; only generation is
        # skipped. The guard is after `opening` so the wire protocol remains
        # identical to a model-produced answer.
        # **Today, and whether it is an ordinary one.** The occasion is read
        # off `world.anchor` rather than off the wall clock, because the
        # anchor is the day the whole runtime believes it is -- `--day` moves
        # it, `recall_day` and `resolve_date` answer against it, and a
        # birthday that disagreed with the date he gives you would be two
        # calendars in one process. The greeting still takes the wall clock:
        # what day it is and what time of day it is are different questions.
        occasion = self.world.persona.on(self.world.anchor)
        social = conversational_reply(
            user, self.world.rng, datetime.now().astimezone(), self.recent,
            peppy=occasion is not None and occasion.peppy,
            name=self.world.persona.name)
        # The family the hatch matched, for `_own_words`' family check. Read
        # off the same sets in the same order, so it is the family whose pool
        # `social` was drawn from.
        family = (social_family(user, self.world.persona.name)
                  if social is not None else None)
        direct = social
        # **And "who are you" comes off the same hatch, for a second reason.**
        # A social turn is routed here because it has no side effect worth
        # validating; an identity turn is routed here because the answer is a
        # fact about *this process* -- which tools were declared, whether
        # `--search` is on -- and the weights cannot know any of it. Asking a
        # 260M model to describe its own runtime is asking it to guess, and
        # the thirty-fourth finding already measured what he does when a name
        # is missing: he invents one. `self.declared` is the same tuple the
        # declaration was rendered from, so what he says he has and what he
        # was offered cannot drift apart.
        if direct is None:
            pool_id = identity_reply(
                user, self.world.rng,
                tuple(self.declared or ()),
                live_search=self.world.search is not None,
                avoid=self.recent,
                persona=self.world.persona,
            )
            # Under `log` the hatch steps aside on the self questions only
            # and the turn routes; the capability answer is still served,
            # because it names the tools declared in this process and that
            # is not a thing the weights can know (PLAN-PERSONALITY §1's
            # *stays* column). `_about_him` is the self test the hatch
            # itself makes first.
            if (pool_id is not None and self.identity_check == "log"
                    and not capability_question(user, self.world.persona.name)):
                self.identity_pool = pool_id
                if echo:
                    print(f"  ~~ identity hatch in log mode -- would have said "
                          f"{pool_id[:60]!r}")
                pool_id = None
            direct = pool_id
        if direct is not None:
            # What the runtime would say on its own. Recorded either way below,
            # and spoken unless his own attempt beats it.
            pool_line, say_author, fell_back, soft = direct, "runtime", "", ""
            # **Only the social half is his to reword, and identity is not.**
            # A greeting carries no facts, so the worst a bad one costs is an
            # odd sentence. An identity answer names the tools he actually has,
            # built from `self.declared` precisely so it cannot drift -- letting
            # him rewrite it would hand that claim back to the weights, which is
            # the drift `identity_reply` exists to prevent. The probe puts a
            # number on it too: asked "who are you", 0 of 16 replies at either
            # temperature were even a finished sentence.
            if social is not None and self.rephrase:
                # Without the seed -- see `_unseeded`.
                his, why, attempt, soft = self._own_words(
                    head + self._unseeded(ctx[len(head):]), family=family)
                if his is not None:
                    direct, say_author = his, "model"
                else:
                    fell_back = why
                    # Reported rather than swallowed, exactly as the deferred
                    # say is. A pool that quietly covered for him would leave
                    # the project as blind to his conversational register as it
                    # was when the pools answered every social turn outright.
                    if echo:
                        print()
                        print(f"  ~~ his own reply was not usable ({why})"
                              f" -- said the pool line instead")
            # The *pool* line goes in the window, never his own words: `_pick`
            # draws from pools and a sentence he composed is in none of them,
            # so recording it would spend a slot suppressing nothing. Recorded
            # before the occasion sentence is appended, for the same reason:
            # what `_pick` suppresses is pool lines.
            self.recent.append(pool_line)
            # **"The first time you talk to him that day", and this is where
            # that is decided.** It rides on a social or identity reply and
            # nowhere else: those are the two turns the runtime already writes
            # a whole sentence for, and appending a second one to a
            # post-observation `say` would break `docs/VOICE.md` rule 3 and
            # the `say_cut` discipline the corpus is built on. The cost is
            # stated plainly rather than hidden -- open the day with a request
            # instead of a hello and he holds the mention until you say
            # something social. The day's *register* does not wait; only the
            # mention does.
            marked = self._mark_occasion(occasion)
            if marked:
                direct = f"{direct} {marked}"
            # His record rides the history only when the words are his: a
            # pool line carries no state, and a record under a sentence he
            # did not write would be the runtime writing a tag for him.
            say_state = getattr(self, "_say_state", None) if say_author == "model" else None
            turn_text = opening + render_say(direct, say_state) + D_END + "\n"
            if echo:
                print(f"{render_say(direct, say_state)}{D_END}")
            _emit("say", text=direct, deferred=False, author=say_author,
                  **({"state": say_state} if say_state else {}),
                  **({"fell_back": fell_back} if fell_back else {}),
                  # What the fill did to his sentence, when it did anything:
                  # `filled`, or the reason it refused. PLAN-PERSONALITY §4c.
                  **({"placeholder": self.placeholder} if self.placeholder
                     else {}),
                  # Countable, like every other thing the runtime added to a
                  # sentence it did not entirely write. A `say` carrying
                  # `author: model` and an occasion is half his and half the
                  # runtime's, and the log should say which rather than
                  # leaving it to be inferred from the date.
                  **({"occasion": self._marked_kind} if marked else {}),
                  # A family miss the runtime served anyway (PLAN-CONVERSATION
                  # 4a): the reply carried no marker for its family and the
                  # family is not one the check is hard on, or the check runs
                  # in `log` mode. Present only when there is one to count.
                  **({"soft_reject": soft} if soft else {}),
                  # What he actually wrote, on the turns the pool covered for
                  # him. Only when it differs from what was served, so a turn
                  # he held on his own does not carry the same sentence twice.
                  **({"model_draft": attempt}
                     if fell_back and attempt and attempt != direct else {}))
            if self.multi:
                self.history.append(as_history(turn_text))
            _emit("done", transcript=turn_text)
            return turn_text

        # **Temporal turns come off a hatch of their own, and the call is
        # written rather than decoded.** The section comment above
        # `temporal_request` carries the measurement; the short form is that
        # with the declaration in context the trained routing sends every
        # date and day-log question to `web_search`, and both tools' answers
        # were always composed on this side of the model anyway. Everything
        # about the turn's shape is kept -- the call, the observation and the
        # say land in the transcript exactly as a decoded turn would put them
        # there, so clients, `--multi` history and the session log need no
        # special case; only generation is skipped. The call event says
        # `author: runtime`, which is what keeps these rows countable and
        # untrainable, on the same argument the say authors make.
        routed = temporal_request(user, self.world.anchor,
                                  self.world.range_span is not None,
                                  birthdays=self._birthdays())
        if routed is not None and routed[0] in ("clock", "birthday_unknown"):
            # **Two turns the runtime answers with no call at all.** The
            # clock (`_CLOCK_ASKS`): no tool in the registry tells the time
            # and declaring one for a value the runtime already holds would
            # be a ninth `tool.selection` option; no decode, for
            # `_TODAY_ASKS`' reason. The wall clock rather than
            # `world.anchor`: the anchor is a *date* that a guard may pin,
            # and what time of day it is was never part of it. And a
            # birthday nobody wrote down (`_BIRTHDAY_PHRASE`): the answer is
            # where the line goes, which is not a thing any tool returns.
            if routed[0] == "clock":
                now = datetime.now().astimezone()
                said = f"It's {spoken_clock(now.hour, now.minute)}."
            elif routed[1] == "my":
                said = ("I don't have your birthday written down. A "
                        "birthday: line at the top of packs/about-me.md is "
                        "where it goes.")
            else:
                said = ("I haven't been given a birthday. A birthday: line "
                        "at the top of packs/persona.md is where it would go.")
            ctx += D_SAY + said + D_END + "\n"
            if echo:
                print(f"{D_SAY}{said}{D_END}")
            _emit("say", text=said, deferred=False, author="runtime")
            turn_text = ctx[len(carried):]
            if self.multi:
                body = (turn_text[len(head):]
                        if turn_text.startswith(head) else turn_text)
                self.history.append(as_history(body))
            _emit("done", transcript=turn_text)
            return turn_text
        if routed is not None:
            kind, expression = routed
            if kind == "pending":
                kind = self.world.range_intent or "resolve"
            self.world.range_intent = None

            def _run(name: str, args: dict) -> dict:
                nonlocal ctx
                raw = json.dumps({"name": name, "arguments": args})
                if echo:
                    print(f"{D_CALL}{raw}")
                _emit("call", raw=raw, ok=True, why="", name=name,
                      arguments=args, masked=0, held=[], released="",
                      author="runtime")
                payload, _ = take_runtime(EXECUTORS[name](args, self.world))
                ctx += D_CALL + raw + "\n" + D_OBS + json.dumps(payload) + "\n"
                if echo:
                    print(f"{D_OBS}{json.dumps(payload)}")
                _emit("obs", name=name, payload=payload)
                return payload

            payload = _run("resolve_date", {"expression": expression})
            if "date" in payload:
                if kind == "recall":
                    payload = _run("recall_day", {"date": payload["date"]})
                    # The day's own sentence, entries or not. `deferred_say`
                    # stands down on a day with entries so *he* can frame it;
                    # on this path there is nobody to stand down for.
                    said = fallback_say(payload)
                    author, deferred = "tool", True
                elif kind == "count":
                    # The count -- arithmetic on the resolved date, never
                    # the model's number. See `_COUNT_ASKS`.
                    n = (date.fromisoformat(payload["date"])
                         - self.world.anchor).days
                    spoken = payload.get("spoken") or payload["date"]
                    if n > 1:
                        said = f"{n} days. That's {spoken}."
                    elif n == 1:
                        said = f"Tomorrow -- {spoken}."
                    elif n == 0:
                        said = f"That's today, {spoken}."
                    else:
                        said = f"That was {-n} days ago, {spoken}."
                    author, deferred = "runtime", False
                else:
                    # The corpus's own three openings, chosen by tense --
                    # `gold_after` in `evals/temporal.jsonl` is this line,
                    # and `date_sentence` is the one place it is written.
                    said = date_sentence(payload, self.world.anchor)
                    author, deferred = "runtime", False
            else:
                # A range, a vagueness, or (for the pending path only) an
                # expression the span could not place: the tool wrote the
                # question, the turn relays it verbatim.
                said = deferred_say(payload) or fallback_say(payload)
                author, deferred = "tool", True
                if payload.get("reason") == "range" and kind == "recall":
                    self.world.range_intent = "recall"

            ctx += D_SAY + said + D_END + "\n"
            if echo:
                print(f"{D_SAY}{said}{D_END}")
            _emit("say", text=said, deferred=deferred, author=author)
            turn_text = ctx[len(carried):]
            if self.multi:
                body = (turn_text[len(head):]
                        if turn_text.startswith(head) else turn_text)
                self.history.append(as_history(body))
            _emit("done", transcript=turn_text)
            return turn_text

        # **Who the user is -- see the section above `USER_IDENTITY_ASKS`.**
        # The call is written rather than decoded, on the temporal hatch's
        # terms and for a sharper version of its reason: the weights lose this
        # class to a question mark (22 of 24 answering bare, 14 of 24
        # fabricating punctuated) and the answer is not theirs to hold anyway
        # -- it is in the store. Below the social and identity hatches, because
        # "what's your name" is a question about *him* and `identity_reply`
        # owns it; above the temporal one, because nothing here is a date.
        asked = user_identity_request(user, self.world.persona.name)
        if asked is not None:
            raw = json.dumps({"name": "web_search",
                              "arguments": {"query": asked}})
            if echo:
                print(f"{D_CALL}{raw}")
            _emit("call", raw=raw, ok=True, why="", name="web_search",
                  arguments={"query": asked}, masked=0, held=[],
                  released="", author="runtime")
            payload, _ = take_runtime(
                EXECUTORS["web_search"]({"query": asked}, self.world))
            ctx += D_CALL + raw + "\n" + D_OBS + json.dumps(payload) + "\n"
            if echo:
                print(f"{D_OBS}{json.dumps(payload)}")
            _emit("obs", name="web_search", payload=payload)
            # `fallback_say` reads the payload the same way it reads any other
            # search: the answer when there is one, the tool's own refusal when
            # there is not. Nothing is composed here, which is what keeps the
            # name out of this file.
            said = fallback_say(payload)
            ctx += D_SAY + said + D_END + "\n"
            if echo:
                print(f"{D_SAY}{said}{D_END}")
            _emit("say", text=said, deferred=True, author="tool")
            turn_text = ctx[len(carried):]
            if self.multi:
                body = (turn_text[len(head):]
                        if turn_text.startswith(head) else turn_text)
                self.history.append(as_history(body))
            _emit("done", transcript=turn_text)
            return turn_text

        # **The recheck hatch -- see the section above `RECHECK_ASKS`.** The
        # state gate does the precision work: with no remembered search these
        # phrases fall through to the router, which is where they went before
        # the hatch existed.
        if (recheck_request(user, self.world.persona.name)
                and self.world.last_search is not None):
            query, first_answer, sources = self.world.last_search
            raw = json.dumps({"name": "web_search",
                              "arguments": {"query": query}})
            if echo:
                print(f"{D_CALL}{raw}")
            _emit("call", raw=raw, ok=True, why="", name="web_search",
                  arguments={"query": query}, masked=0, held=[],
                  released="", author="runtime")
            payload, _ = take_runtime(second_source(self.world, query,
                                                    list(sources)))
            if payload.get("answer") and payload.get("source"):
                if payload["source"] not in sources:
                    sources.append(payload["source"])
            ctx += D_CALL + raw + "\n" + D_OBS + json.dumps(payload) + "\n"
            if echo:
                print(f"{D_OBS}{json.dumps(payload)}")
            _emit("obs", name="web_search", payload=payload)
            said = recheck_say(payload, first_answer, sources[:1] or [""])
            ctx += D_SAY + said + D_END + "\n"
            if echo:
                print(f"{D_SAY}{said}{D_END}")
            _emit("say", text=said, deferred=False, author="runtime")
            turn_text = ctx[len(carried):]
            if self.multi:
                body = (turn_text[len(head):]
                        if turn_text.startswith(head) else turn_text)
                self.history.append(as_history(body))
            _emit("done", transcript=turn_text)
            return turn_text

        # Armed by the first observation, because `say_cut`'s rule is measured
        # on transcripts where speech follows a tool and conversational speech
        # is allowed the quotes it bans.
        saw_obs = False
        # The last observation this turn, and the string it obliges him to say.
        # `defer_to` is read twice: once before generating, to decide whether
        # his attempt is worth streaming at all, and once after, to decide what
        # the client is actually handed. See `deferred_say`.
        payload = None
        # What the reader made of the last passage, or `None` on a turn where
        # nothing read one. Last write wins, exactly as `payload` does: the
        # per-call record is on the `obs` events, which are complete whatever
        # order the rounds came in, and this is only what the closing `say`
        # reports.
        reading: dict | None = None
        # Characters withheld by the frame-loss floor below, `None` on a turn
        # that kept its frame. On the say event for the same reason `fell_back`
        # is: the server's log is where a rate lives, and a floor that fired
        # invisibly would make this failure uncountable from the rows.
        frame_loss: int | None = None
        # **What he wrote, on the turns where the user heard something else.**
        # The seventy-eighth finding's instrument complaint: `turn_record`'s
        # `transcript` holds what was *served*, so a runtime- or tool-authored
        # turn discarded his own emission unrecorded and `author` said only
        # that an intervention happened, never what it cost. Every number in
        # that audit had to come from an A/B against a second server for want
        # of this column. Same argument `frame_loss` already won.
        draft: str | None = None
        defer_to: str | None = None
        # A sentence the runtime is *holding in reserve* rather than committed
        # to. `defer_to` means "he will not be speaking"; `floor` means "he
        # may, and there is something to fall back to if he does not". Both
        # suppress streaming, for the same reason and at the same moment --
        # see where they are set.
        floor: str | None = None
        said: str | None = None
        # Set next to every assignment of `said` below. `None` here would mean
        # a say was emitted by a path nobody labelled, which the guard forbids.
        author: str | None = None
        # The record he wrote under the say (phase D), set only on the round
        # where he wrote one. Initialised here with the rest: a turn whose
        # rounds ended without his say -- spent on calls, or a fallback --
        # read it unbound at the closing `say` and raised (memorygrid's first
        # GPU read, "what did I write down?", 2026-10-04).
        tool_state: str | None = None
        for _ in range(rounds):
            # Re-pointed every round, not once per turn: the span a second call
            # needs is routinely in the first call's observation, and that has
            # only just been spliced in.
            #
            # **The head is not part of it, and leaving it in was gap 3's own
            # premise being quietly violated.** The rule is that a contact has
            # to be a span of something *actually said in this conversation*;
            # the declaration is scaffolding this runtime wrote, and nobody said
            # it. With it in the source these were all legal contact names:
            #
            #     "dial a contact"   "send an SMS to a contact"   "place_call"
            #
            # and two of them reached a user at 260M -- `morning` produced
            # `place_call{"contact": "dial a contact"}` and the reply "I don't
            # have a contact called dial a contact." The module docstring
            # anticipated the *markers* being copyable and stopped there.
            #
            # Prior turns stay in, deliberately: they are conversation, and the
            # clarify path depends on copying a name out of an earlier
            # observation.
            if self.constraint is not None:
                # **Two sources, because two slots want different reaches.**
                # The wide one is the conversation below the declaration, for
                # the reason argued above: prior turns are conversation and the
                # clarify path copies a name out of an earlier observation.
                #
                # The narrow one is *this turn* -- from the last `<|user|>` to
                # wherever generation has got to, so it grows with the round
                # and carries this turn's own observations while carrying none
                # of the previous turn's. That is the whole repair for session
                # 13's cross-turn write: `note down buy milk` declines, and the
                # next turn's `save_note` could reach back through history and
                # write *that* request to disk under this turn's authority,
                # saying "Noted." either way. 7 of 20 pairs. A note is a span
                # of the sentence that asked for it, and nothing older.
                below = self._unseeded(ctx[len(head):])
                cut = below.rfind(D_USER)
                self.constraint.set_source(
                    below, below[cut:] if cut >= 0 else below)
            # **Not streamed when the runtime already knows what must be
            # said.** `text` events are what a streaming client speaks as they
            # arrive, so letting his paraphrase through and correcting it in
            # the `say` event afterwards would mean the wrong sentence had
            # already been read out loud -- the half-fix that looks like a fix,
            # which `_until_marker` makes the same argument about for the
            # payload spill. Nothing is lost: `echo` still prints what he
            # wrote, and `done` still carries the honest transcript.
            chunk = self._until_marker(
                ctx, budget,
                # `framed` rebuilt per round on purpose: the gate's decision is
                # about how *this* round opens, and a marker seen last round
                # says nothing about the text arriving now.
                # `filled` inside `framed`: the frame decides whether this
                # round is speech at all, and only speech has its tags
                # filled on the way to the client. See `filled`.
                on_text=(framed(filled(lambda piece: _emit("text", text=piece),
                                       self.world.persona.speak))
                         if emit and defer_to is None and floor is None
                         else None),
                guard_say=saw_obs,
            )
            # Read before the next generation resets them.
            bites = list(self.constraint.bites) if self.constraint else []
            released = self.constraint.released if self.constraint else ""

            # `emitted`, not `head`: this name used to be `head` and shadowed
            # the declaration bound at the top of the turn, so everything
            # below that meant the declaration -- the constraint source cut at
            # 'set_source' on every round after the first, and the `--multi`
            # strip at the bottom of this method -- silently operated on the
            # last emission instead. The history entry then kept the ~150-token
            # declaration, which is exactly what evicted it from a 311-token
            # room: `--multi` never carried a single turn on the 512-block
            # checkpoints until this rename.
            emitted, raw = split_emission(chunk)
            # **4j, the re-pass: the seed decides which tool and never what
            # argument.** See `SEED_REPASS_TOOLS` and PLAN-CONVERSATION 4j.
            # Called before `ctx` grows, because the second pass needs the
            # context this round was decoded *from*; and it returns `emitted`
            # as well as `raw`, because the emission carries the call text and
            # a context holding one call beside an executed other would be a
            # transcript that never happened.
            emitted, raw = self._repass(ctx, head, emitted, raw, budget,
                                        guard_say=saw_obs)
            ctx += emitted

            if raw is None:
                spoken = emitted.split(D_END)[0].split(STOP_DOC)[0]
                if echo:
                    print(spoken, end="")
                body = spoken.rsplit(D_SAY, 1)[-1]
                # The record he wrote under the say, if any (phase D): off
                # the served text, kept in `ctx` verbatim above, and on the
                # say event so the log can count it.
                body, tool_state = split_state(body)
                # What he wrote, tidied where `say_cut` may have stopped him
                # mid-clause. Kept separate from what is said, because the two
                # are now allowed to differ and the difference is worth naming.
                own = tidy_say(body) if saw_obs else body
                # **No say marker anywhere in the emission means this is not
                # speech.** The silent version of this failure has had its
                # floor since `fallback_say` -- the four exits its docstring
                # names -- but the noisy version was served whole: a turn that
                # fell out of the vocabulary streamed pretraining-register
                # text as though he were speaking (the tools meta-question,
                # 2026-08-29). Withheld the way `social_rejection` withholds a
                # failed greeting: blanked here so the floors below decide
                # what is said instead -- the observation's floor first where
                # one exists, `fallback_say` otherwise -- and counted, because
                # a turn that fell out of the frame and a turn that said
                # nothing are different facts about the checkpoint.
                if D_SAY not in spoken and own.strip():
                    frame_loss = len(own)
                    draft = own
                    if echo:
                        print()
                        print(f"  ~~ no turn frame in the emission -- "
                              f"{frame_loss} chars withheld")
                    own = ""
                # **The floor under `COMPOSED_FIELD`.** `deferred_say`
                # stands down on a day with entries so he can frame it rather
                # than recite it; `recall_rejection` checks he framed anything
                # at all, and hands him the payload's own sentence when the
                # summary named nothing from the day. Checked before the
                # deferred branch because a recall payload has a `say` that
                # `defer_to` deliberately did not pick up.
                recall_why = recall_rejection(own, payload)
                if recall_why is not None and floor:
                    defer_to = floor
                    if echo:
                        print()
                        print(f"  ~~ his summary {recall_why}"
                              f" -- read the day back instead")
                # And the same floor under the search answer -- see
                # `search_rejection` for the three replies this exists for.
                # Disjoint by payload shape: a recall payload has entries and
                # no answer, a search payload the reverse, so at most one of
                # these two checks can fire on a turn.
                search_why = search_rejection(own, payload)
                if search_why is not None and floor:
                    defer_to = floor
                    if echo:
                        print()
                        print(f"  ~~ his answer {search_why}"
                              f" -- read the result back instead")
                # And under the resolved date -- `date_rejection`. Disjoint
                # from both above by payload shape: a date payload has no
                # entries and no answer.
                date_why = date_rejection(own, payload)
                if date_why is not None and floor:
                    defer_to = floor
                    if echo:
                        print()
                        print(f"  ~~ his read-back {date_why}"
                              f" -- said the date instead")
                if defer_to is not None:
                    said = defer_to
                    author = "tool"
                    # His paraphrase, kept rather than dropped -- this is the
                    # 70-turn column of the audit's authorship table, and it was
                    # the one with no evidence behind it.
                    draft = own.strip() or draft
                    # Reported rather than performed silently -- the same
                    # argument the grammar's bite count makes below. A reply the
                    # model wrote correctly on its own and one the runtime had
                    # to replace are different facts about the checkpoint, and
                    # collapsing them would hide the second behind the first.
                    if echo and own.strip() and own.strip() != said:
                        print()
                        print(f"  ~~ deferred to the observation -- {said!r}")
                else:
                    # **The routed say is filled too, and refused whole when
                    # a tag survives.** This is the path a trained self line
                    # arrives by (the self carriers reach the router), so it
                    # is the path that matters for `{name}`. A refusal blanks
                    # the sentence and the floors below decide what is said
                    # instead, exactly as the frame-loss branch does; the
                    # draft is kept so the row can see what he wrote.
                    own, fill_why = self._fill(own)
                    if fill_why is not None:
                        draft = own
                        if echo:
                            print()
                            print(f"  ~~ his reply was not usable ({fill_why})"
                                  f" -- said something else")
                        own = ""
                    said = own
                    author = "model"
                break

            v = validate_call(raw)
            # **A placeholder in a call is a leak, and it is counted here
            # rather than refused here.** PLAN-PERSONALITY §5b: the grammar
            # admits any string in a `text` or `message` field, so a model
            # that learned `{name}` could write it into a note. The row's
            # bar is zero; the runtime's job is to make the count readable
            # on every card, which the field does.
            leak = [t for t in (PLACEHOLDER_NAME, PLACEHOLDER_USER) if t in raw]
            _emit("call", raw=raw, ok=bool(v["ok"]), why=v["why"],
                  name=v["name"], arguments=v["arguments"],
                  masked=len(bites),
                  held=sorted({w for _, _, w in bites if w}),
                  released=released,
                  **({"placeholder_leak": leak} if leak else {}))
            if leak and echo:
                print(f"  ~~ a placeholder in the call -- {', '.join(leak)}")
            if echo:
                print(f"{D_CALL}{raw}")
                # The count is the point, not the fix. A call the grammar never
                # touched is one the model wrote correctly on its own, and the
                # difference between those two is invisible unless it is said.
                if bites:
                    shown = ", ".join(f"{w!r} -> {t!r}" for w, t, _ in bites[:3])
                    more = f" (+{len(bites) - 3})" if len(bites) > 3 else ""
                    print(f"  ~~ grammar closed the call: {len(bites)} masked -- {shown}{more}")
                    # Reported apart from the count above because it is a
                    # different failure. A bite in a copy slot is the model
                    # reaching for a name nobody said, which is the one thing
                    # here that would otherwise have executed and looked fine.
                    slots = sorted({w for _, _, w in bites if w})
                    if slots:
                        n = sum(1 for _, _, w in bites if w)
                        print(f"  ~~ {n} of those held {', '.join(slots)} to what was said")
                if released:
                    print(f"  ~~ grammar released early -- {released}")
            if not v["ok"]:
                # DATA.md §6's argument with a live consequence: the schema is
                # what stands between a malformed call and a side effect, and
                # nothing has run at this point.
                if echo:
                    print(f"  !! not executed -- {v['why']}")
                _emit("rejected", why=v["why"])
                break

            held = (self.world.confirm(v["name"], v["arguments"])
                    if self.world.confirm else None)
            payload = (held if held is not None
                       else EXECUTORS[v["name"]](v["arguments"], self.world))
            # **The one place a runtime-only field is removed, and everything
            # downstream of it is the model's view.** `deferred_say`,
            # `fallback_say`, the `<|obs|>` splice and the `obs` event all read
            # `payload` below, so stripping here rather than at each of them is
            # what makes "nothing under `RUNTIME_PREFIX` reaches a transcript"
            # a property of the turn instead of four separate promises.
            payload, runtime = take_runtime(payload)
            reading = runtime.get(READING)
            # **Read here rather than spoken here.** The sentence the user gets
            # for a refused provider is the payload's own `say` and takes the
            # ordinary `deferred_say` path -- there is nothing special about a
            # `blocked` payload downstream of this line. What this pulls out is
            # the half the sentence deliberately leaves out: the user is told
            # the host and that waiting helps, and the log is told which of the
            # three refusals it was, because that is the axis a probe splits
            # its misses on and no spoken sentence should be carrying a slug.
            refusal = runtime.get(BLOCKED_BY)
            # **The newline is not cosmetic, and the corpus is unanimous.**
            # `data/raw/tools.txt` writes the marker after a newline 9,000
            # times out of 9,000 -- there is no transcript anywhere in it where
            # `<|obs|>` follows the call's closing brace directly. The grammar
            # stops generation at that brace, so without this the runtime hands
            # the model a shape it has never once seen and then asks it to read
            # an observation out of it.
            #
            # The thirty-third finding priced exactly this class of divergence:
            # one level of nesting took `tool.copy` from 100-120 to 0-27,
            # against 3 of 300 for a tool name the model was never trained on.
            # Shape is what the copy behaviour is keyed to, and this is shape.
            if not ctx.endswith("\n"):
                ctx += "\n"
            ctx += D_OBS + json.dumps(payload) + "\n"
            # Arms `say_cut` for every round after this one. See its docstring
            # for why it is not armed on the first: conversational speech is
            # allowed the quotes that post-observation speech never contains.
            saw_obs = True
            # Decided here rather than at the point of speech, because the next
            # round's streaming depends on it: by the time he has written the
            # paraphrase it is too late not to have sent it.
            defer_to = deferred_say(payload)
            # **The floor is decided here too, and for the streaming reason
            # rather than the speaking one.** `COMPOSED_FIELD` leaves a day
            # with entries to him deliberately, so `defer_to` is `None` and he
            # generates -- but the runtime is holding that day's own sentence,
            # and if his summary recalls nothing it is what the user gets. A
            # client that had already spoken his attempt would then hear both,
            # which is the failure the line above exists to prevent, arriving
            # by a second route.
            floor = (payload.get("say") if defer_to is None
                     and payload.get(COMPOSED_FIELD) else None)
            # **The search answer is a floor for the same reason the day's
            # sentence is.** A success payload leaves the framing to him and
            # `search_rejection` checks what he framed, so the runtime holds
            # the observation's own sentence for the turns where his answer
            # is refused -- and holding it mutes streaming, on the argument
            # both lines above already make: a client that spoke "according
            # to wikipedia.org" while the payload said `didtoday.app` cannot
            # be corrected by a later event.
            if floor is None and defer_to is None:
                answer = payload.get("answer")
                if isinstance(answer, str) and answer.strip():
                    # The *lead sentence*, not the whole reduction: this is
                    # spoken, §3 wants it short, and the lead is the same
                    # floor `--extract`'s own docstring names. The cheap
                    # split is enough for a fallback -- a mid-abbreviation
                    # cut costs one odd clause on a path whose alternative
                    # was an invented answer.
                    floor = tidy_say(re.split(r"(?<=[.!?])\s", answer.strip())[0])
            # **And the resolved date, for `date_rejection`.** A routed
            # `resolve_date` call leaves the framing to him the way a search
            # does; the sentence the hatch would have written is held here
            # for the turn where his framing names no part of the date.
            if floor is None and defer_to is None:
                floor = date_sentence(payload, self.world.anchor)
            if echo:
                print(f"{D_OBS}{json.dumps(payload)}")
                # Printed whether the extraction worked or not, because the
                # interesting number is the ratio and a line that only appeared
                # on success would make it uncountable from the terminal.
                if reading is not None:
                    print(f"  ~~ read the passage: {reading['why']}")
                # Same argument as the line above: printed so the ratio is
                # countable from the terminal. A run that hits a rate limit
                # halfway through a battery looks, in the transcript alone,
                # exactly like a run that asked twenty hard questions.
                if refusal is not None:
                    print(f"  ~~ {refusal['provider']} declined: "
                          f"{refusal['cause']} ({refusal['detail']})")
            _emit("obs", name=v["name"], payload=payload,
                  **({"read": reading["why"]} if reading is not None else {}),
                  **({"blocked_by": refusal} if refusal is not None else {}))
            # No `<|end|>` check here, deliberately. `recall_day` arrives with
            # the end marker attached because the corpus ends the transcript at
            # the call -- but the observation is information the model did not
            # have when it wrote that marker, so the turn continues and what it
            # does next is the probe.

        # **Nothing reaches here without something to say.** The four silent
        # exits -- an `<|endoftext|>` straight after an observation, an empty
        # say, a call rejected before it ran, a round budget spent inside an
        # object -- all arrive with `said` unset or blank, and all of them left
        # the user with the turn's latency and none of its answer. See
        # `fallback_say` for what gets said instead and why it cannot invent.
        if said is None or not said.strip():
            said = fallback_say(payload)
            # `fallback_say`'s ladder takes the words out of the payload on
            # every rung but the last two, and those two rungs are exactly
            # these constants -- so this reads the ladder back rather than
            # keeping a second copy of it that could drift. A tool whose own
            # `say` happened to be the string "Done." would be recorded as
            # runtime; `scripts/check_agent.py` walks every registry payload
            # shape so that collision would show up as a failure rather than
            # as a quietly mislabelled row.
            author = "runtime" if said in (NOTHING_SAID, DID_IT) else "tool"
            if echo:
                print()
                print(f"  ~~ nothing was said -- {said!r}")
        # **The reader found nothing, so what follows is not an answer and is
        # not said like one.** See `FELL_BACK_FRAME`. Gated on the same
        # condition the `fell_back` field below is gated on, so the sentence
        # the user hears and the column a card counts can never disagree about
        # which turns fell back. The two runtime admissions are exempt: they
        # already say a turn produced nothing, and framing them as a lead
        # sentence would be introducing a passage that was never read.
        if (reading is not None and not reading["ok"]
                and said and said not in (NOTHING_SAID, DID_IT)):
            said = FELL_BACK_FRAME.format(lead=tidy_say(said))
            author = "runtime"
            if echo:
                print(f"  ~~ said as a fallback, not as an answer")
        # Emitted whole even though `text` events carried it piecewise: a client
        # that buffers wants one authoritative string, a client that streams
        # wants the pieces, and neither should have to reconstruct the other's
        # view.
        #
        # **Without the marker, unlike the prints above.** The terminal is being
        # shown a transcript and `<|say|>` belongs in it; a client is being
        # handed something to speak, and a voice client given this string
        # unstripped would read the marker out loud. The two callers want
        # different things from the same bytes, which is the whole reason `emit`
        # is not just `print`.
        #
        # `deferred` is the flag a client needs to know whether the words are
        # his or the tool's, and it is the reason this is not just a string.
        # **`fell_back` is the same field the social turn uses and it means the
        # same thing**: his own attempt was refused and the user heard
        # something else. There it is `social_rejection` refusing a greeting;
        # here it is `grounded` and `reduce` refusing every reading of the
        # passage, and what got said instead is the lead sentence the provider
        # would have returned anyway. Naming both makes the fallback *rate* the
        # number this design ships against -- see the plan's closing section.
        _emit("say", text=said, deferred=defer_to is not None, author=author,
              **({"state": tool_state} if tool_state and author == "model" else {}),
              **({"fell_back": reading["why"]}
                 if reading is not None and not reading["ok"] else {}),
              **({"frame_loss": frame_loss} if frame_loss else {}),
              **({"placeholder": self.placeholder} if self.placeholder
                 else {}),
              # The line the identity hatch would have said, under `log`
              # (PLAN-PERSONALITY §7). Present exactly when the hatch
              # stepped aside, so the ledger can count the rule's fires.
              **({"identity_pool": self.identity_pool} if self.identity_pool
                 else {}),
              # See `draft`. Withheld when it is the same string that was
              # served: a model-authored turn is already recorded by `text`,
              # and a second copy of it would make the column's own rate --
              # how often his words lost -- uncountable from the rows.
              **({"model_draft": draft} if draft and draft != said else {}))
        turn_text = ctx[len(carried):]
        if self.multi:
            # The head is dropped rather than stored: `turn()` re-attaches it to
            # the front of every assembled context, so a copy inside an entry
            # would come back doubled -- and would vanish altogether the turn
            # `fit_history` dropped that entry, which is the worse of the two.
            # The declaration and the grammar's narrowing are one decision (see
            # `__init__`); a context that narrows to a tool set it has stopped
            # showing is what this ordering prevents.
            body = turn_text[len(head):] if turn_text.startswith(head) else turn_text
            self.history.append(as_history(body))
        _emit("done", transcript=turn_text)
        return turn_text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default="checkpoints/nano100m_v1/ckpt.pt")
    ap.add_argument("--ask", action="append", default=[], help="run and exit; repeatable")
    ap.add_argument("--notes", type=Path, default=DEFAULT_NOTES,
                    help="the day log: save_note appends, recall_day reads")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--budget", type=int, default=200)
    ap.add_argument("--date", default=None, help="anchor, ISO; defaults to today")
    ap.add_argument(
        "--day",
        action="store_true",
        help="prefix <|day|>, which biases the tool choice towards resolve_date",
    )
    ap.add_argument(
        "--no-grammar",
        action="store_true",
        help="sample the call unconstrained -- what the runtime did before "
             "corn/grammar.py, and the way to see what the constraint is worth",
    )
    ap.add_argument(
        "--multi",
        action="store_true",
        # `%%` because argparse expands `help` against a dict and `% of` is a
        # format spec to it -- `--help` raised TypeError until this was doubled.
        help="carry the transcript across turns. The shape is trained thinly "
             "(~0.34%% of the mix) and the no-call second turn is not trained "
             "at all -- 0 of 1,720",
    )
    ap.add_argument(
        "--fold-history",
        action="store_true",
        help="on eviction, drop a turn's <|call|> and <|obs|> and keep its "
             "<|user|> and <|say|> instead of dropping the turn whole. 23 "
             "tokens against 87, and the kept form is the chat_day shape. "
             "--multi only; see PLAN-CONVERSATION 4g",
    )
    ap.add_argument(
        "--identity-check", dest="identity_check", choices=("on", "log"),
        default="on",
        help="the identity hatch: `on` answers who-are-you from the pools; "
             "`log` lets the weights answer and records the pool line as "
             "identity_pool on the say (PLAN-PERSONALITY 7)")
    ap.add_argument(
        "--family-check", choices=("on", "log", "off"), default="on",
        help="hold his own social reply to the family the hatch matched "
             "(corn.socialfam). `log` serves it and reports what would have "
             "been refused; `off` is the runtime before 2026-09-05. See "
             "PLAN-CONVERSATION 4a",
    )
    ap.add_argument(
        "--round-reserve", type=int, default=0,
        help="tokens held back from the history fit so a turn's second round "
             "is not tail-cut at the head; ROUND_ADDITION (%d) is the "
             "measured maximum a round appends. 0 is the shipped trimmer. "
             "--multi only; see PLAN-CONVERSATION 4h" % ROUND_ADDITION,
    )
    ap.add_argument(
        "--copy",
        default=None,
        metavar="TOOL.PARAM,...",
        help="argument slots held to spans of the conversation. Defaults to "
             f"{','.join(sorted(f'{t}.{p}' for t, p in DEFAULT_COPY_SLOTS))}; "
             f"available: {','.join(sorted(f'{t}.{p}' for t, p in SPAN_SLOTS))}",
    )
    ap.add_argument(
        "--no-copy",
        action="store_true",
        help="schema constraint only -- the way to see gap 3 happen",
    )
    ap.add_argument(
        "--no-declare", action="store_true",
        help="prompt with a bare utterance and do not narrow the grammar -- "
             "the pre-WS-E runtime. The two travel together on purpose: see "
             "`Agent.__init__`.",
    )
    ap.add_argument(
        "--no-fold",
        action="store_true",
        help="hand the model the utterance exactly as typed -- the pre-fold "
             "runtime, and the control a fold-dated card is read against. "
             "See `fold_turn`",
    )
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument(
        "--buckets",
        action="store_true",
        help="one decode graph per 128-slot window instead of always attending "
             "the full block -- identical output, faster while the turn is short",
    )
    ap.add_argument(
        "--compile",
        action="store_true",
        help="Inductor-fuse the decode step before capture -- fastest steady "
             "state; first construction pays minutes of compile, then cached",
    )
    ap.add_argument(
        "--fast-attn",
        action="store_true",
        help="explicit-matmul decode attention -- 2.2x faster than the masked "
             "SDPA call and equally accurate, but it rounds differently, so it "
             "is for talking to him and not for producing a scorecard",
    )
    ap.add_argument(
        "--prefix-reuse",
        action="store_true",
        help="keep the KV of the prefix each round shares with the last -- "
             "42%% of a turn's prefill is recomputation, and `wpe` makes "
             "keeping it exact rather than approximate",
    )
    ap.add_argument(
        "--fast",
        action="store_true",
        help="all four of the above: the fastest decode this box has",
    )
    args = ap.parse_args()

    if args.fast:
        args.buckets = args.compile = args.fast_attn = True
        args.prefix_reuse = True

    if args.no_copy:
        copy_slots = frozenset()
    elif args.copy:
        copy_slots = frozenset(
            tuple(s.strip().split(".", 1)) for s in args.copy.split(",") if s.strip()
        )
        # Refused rather than warned about. A slot outside `SPAN_SLOTS` is one
        # the corpus does not support -- `resolve_date.expression` misses 1,348
        # times -- and arming it would ban calls the generator writes, which is
        # the quiet half of `check_grammar.py`'s argument happening at runtime.
        unknown = sorted(f"{t}.{p}" for t, p in copy_slots - SPAN_SLOTS)
        if unknown:
            ap.error(
                f"not span-copy slots in the corpus: {', '.join(unknown)}. "
                f"Available: {', '.join(sorted(f'{t}.{p}' for t, p in SPAN_SLOTS))}"
            )
    else:
        copy_slots = DEFAULT_COPY_SLOTS

    anchor = date.fromisoformat(args.date) if args.date else date.today()
    world = World(anchor, args.notes)
    agent = Agent(
        args.ckpt,
        args.device,
        args.temperature,
        world,
        grammar=not args.no_grammar,
        copy_slots=copy_slots,
        fold=not args.no_fold,
        history_fold=args.fold_history,
        family_check=args.family_check,
        identity_check=args.identity_check,
        round_reserve=args.round_reserve,
        budget=args.budget,
        multi=args.multi,
        declare=not args.no_declare,
        buckets=args.buckets,
        compile_step=args.compile,
        fast_attn=args.fast_attn,
        prefix_reuse=args.prefix_reuse,
    )
    decl_note = (
        f"{len(agent.declared)} tools, decline last" if agent.declared else "off"
    )
    copy_note = (
        "off" if not copy_slots
        else ",".join(sorted(f"{t}.{p}" for t, p in copy_slots))
    )
    print(
        f"{agent.cfg.name} | {agent.model.num_params():,} params | "
        f"val {agent.ckpt['val_loss']:.4f} | anchor {anchor} | notes -> {args.notes} | "
        f"grammar {'off' if args.no_grammar else 'on'} | copy {copy_note} | "
        f"declared {decl_note} | "
        f"turns {'multi' if args.multi else 'independent'}"
    )
    if args.multi:
        print(
            "  ~~ multi-turn: the shape is trained at ~0.34% of the mix and "
            "every trained second turn calls a tool. Talk past turn 1 is the "
            "untrained part."
        )

    if args.ask:
        for i, ask in enumerate(args.ask):
            if i:
                print("\n" + "-" * 64 + "\n")
            agent.turn(ask, budget=args.budget, day=args.day)
        print()
        return

    print("tools run for real. ctrl-c to quit.\n")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.strip():
            agent.turn(line.strip(), budget=args.budget, day=args.day)
            print()


if __name__ == "__main__":
    main()
