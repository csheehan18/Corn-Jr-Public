"""The reply-side rules a social sentence is held to -- shared by the eval and the runtime.

**Why this is its own module, and why it imports nothing.** Until 2026-09-05
`reply_families` and `life_claim` lived in `corn/evals.py`, which is how the
eval could see that "That sounds great. I'll take it." is not a goodbye while
the server could not (PLAN-CONVERSATION §1, "he does not close a
conversation"). `corn/agent.py` cannot import `corn/evals.py` -- `evals`
imports `agent` lazily to keep `scripts/make_evals.py`'s import graph clean --
so the rules both sides read have to sit in a leaf below both. This is that
leaf: `re` and nothing else, so importing it costs nothing and cannot pull a
framework in through the back.

Everything here is a pure function of a string. Nothing knows about a
checkpoint, a tokenizer or a pool; the pools calibrate these rules from
`scripts/check_social.py` and `scripts/check_agent.py`, not the other way
round.

Four rule sets:

  * `life_claim` -- a claim about a life he does not have ("my cat", "I'm
    heading off to class"). The eval has scored `social.voice` with it since
    2026-09-01; `social_rejection` refuses on it since 4b.
  * `kin_address` -- a reply that calls the user dad, mom, son, sis or honey.
    A relation he does not have, asserted by address rather than by claim,
    which is why `life_claim` could not see "I love you too, dad."
  * `cushioned_refusal` -- an apology opening a refusal on a turn that asked
    for nothing ("I'm sorry, but I don't have any questions."), the last of
    the seventy-eighth finding's four recorded leaks. Added 2026-09-05.
  * `reply_families` and `family_rejection` -- which social family a reply
    *answers*, and whether that is the family the move was. The runtime form
    is split: the exclusion clause is hard everywhere, the no-marker clause
    is hard only on `HARD_FAMILIES` and logged everywhere else, for the reason
    PLAN-CONVERSATION 4a's 2026-09-05 (fourth) amendment gives -- a reply-side
    regex is a whitelist, and the vocabulary arm 6 exists to widen would be
    capped at the list.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------
# A life he does not have
# --------------------------------------------------------------------------
#
# **Measured, not guessed at.** Every alternative below is a phrase counted in
# `data/raw/chat_day_5b.txt`, the SODA-derived slice his social voice comes
# from, where `<|say|>` is the other person in the scene rather than an
# assistant. The list is deliberately closed and concrete for
# `corn.agent.TOOL_REGISTER`'s reason: a leak past it costs one odd reply
# rather than a wrong action, and a classifier here would be guessing at a
# judgement.
#
# **Calibrated against the pools, which are the known-good set.** Every
# hand-written line in the runtime's reply pools passes it, and
# `scripts/check_evals.py` asserts that -- a rule that refused the runtime's
# own floor would be scoring the wrong thing. "My pleasure." and "I'll be
# right here." are why `my` and `i'll` are qualified rather than bare.
#
# **Complementary to `social_rejection` rather than a superset of it, by
# measurement.** Over 239,307 corpus replies: 63.0% clear `social_rejection`,
# 87.0% carry no life claim, and 55.6% clear both -- so this rule removes 7.4
# points the guard cannot see, and the guard removes what this cannot ("I'm
# doing well, Aariz." is caught as a stray capital, not as a life).
#
# **`sorry you` and `glad you` came out on 2026-09-05 (PLAN-CONVERSATION 4b).**
# They were there to catch "I'm sorry you had to go through that" as a scene
# reply, and they would have refused every consolation the sixth family
# wants -- "Sorry to hear it" is the register, not a leak. The consolation
# markers below carry that register instead, and what was lost is the pair
# that names the *user's* past ("you enjoyed", "you liked"), which stays.
# `social.voice` measured with the old list until this date; the delta is a
# dated line in the plan rather than an absorbed one. `birthday` left the
# possessives the same day and for the runtime's reason: his birthday is a
# fact in `packs/about-me.md`, `BIRTHDAY_SAYS` states it truthfully, and
# `scripts/check_persona.py` holds those lines to this check.
_LIFE_CLAIM = re.compile(
    # Both spellings of every contraction, because a model emits either and a
    # contracted-only list scored "I am just getting ready for my next class."
    # as clean. And one optional modifier inside the possessives, for the same
    # sentence: `my class` is in the list and `my next class` is what was said.
    r"\b(?:"
    r"i(?:'m| am) (?:going|getting|just|heading|off to|about to"
    r"|so glad|here with)"
    r"|i(?:'ve| have) (?:been|got a|had)"
    r"|i (?:was|went|need|needed|have a|had a|got a|live|work|study)"
    r"|i(?:'ll| will) (?:be there|be back|be home|be out|bring|come"
    r"|see you there)"
    r"|my (?:\w+ )?(?:cat|dog|day|class|job|work|mom|mum|dad|family|friend"
    r"|house|car|wife|husband|kids|boss|team|life|vacation|place"
    r"|room|phone)"
    r"|our (?:\w+ )?(?:town|church|company|house|family|team|clients|kids"
    r"|place)"
    r"|we(?:'re| are) (?:protesting|going|meeting|having|planning|together)"
    r"|you enjoyed|you liked|last (?:night|week) i|earlier i"
    r")\b",
    re.IGNORECASE,
)


def life_claim(reply: str) -> str | None:
    """The first claim about a life he does not have, or None.

    Returns the matched phrase rather than a bool for `social_rejection`'s
    reason: the reason is the interesting half and it goes into the row's `why`
    counter, so a failing arm can be read as "he is telling you about his cat"
    rather than as a number going down.
    """
    hit = _LIFE_CLAIM.search(reply or "")
    return hit.group(0).lower() if hit else None


# --------------------------------------------------------------------------
# A relation he does not have, asserted by address
# --------------------------------------------------------------------------
#
# "I love you too, dad." has no digit, no capital and no `_LIFE_CLAIM` phrase
# (PLAN-CONVERSATION §1, arm 2, routed). It is a scene reply all the same: the
# corpus's other name for the user is Jayleigh, and its other relation is a
# parent. Kin terms only. `man`, `buddy`, `pal` and `mate` are *not* here and
# never were leaks -- `docs/VOICE.md` rule 2 names "man" as part of the voice
# and the `THANKS` carriers accept "thanks man" from the user, so refusing it
# from him would have the floor speak a register the model is forbidden
# (4b, amended 2026-09-05). `corn/convgen.py`'s `ENDEARMENT` is the miner's
# wider list and stays where it is; this is the runtime's narrower one.
_KIN_TERMS = (r"dad|daddy|mom|mum|mommy|mummy|son|daughter|sis|sister"
              r"|bro|brother|honey|hon|sweetie|sweetheart|babe|baby|darling"
              r"|dear|kiddo")
_KIN = re.compile(
    # After a comma, anywhere; or opening the reply, or closing a sentence.
    r"(?:,\s*(" + _KIN_TERMS + r")\b)"
    r"|(?:^(" + _KIN_TERMS + r")\b)"
    r"|(?:\s(" + _KIN_TERMS + r")(?=[.!?]))",
    re.IGNORECASE,
)


def kin_address(reply: str) -> str | None:
    """The kin term this reply addresses the user by, or None.

    A term is an address in a vocative position: after a comma ("I love you
    too, dad."), opening the reply ("Honey, no."), or closing a sentence
    ("Love you dad."). "My dad" is `life_claim`'s and is caught there; "a
    dear old thing" is neither, and the position test keeps it out.
    """
    hit = _KIN.search(reply or "")
    return next(g for g in hit.groups() if g).lower() if hit else None


# --------------------------------------------------------------------------
# A refusal wearing a cushion
# --------------------------------------------------------------------------
#
# **The last of the seventy-eighth finding's four recorded leaks.** "I'm
# sorry, but I don't have any questions." was served live to a social turn and
# passes every clause `social_rejection` has: no digit, no stray capital, no
# tool word, no life claim, no kin address. What is wrong with it is the
# register -- `docs/VOICE.md` rule 5, "admissions and refusals are direct and
# unadorned, no cushioning" -- and the position: an apology opening a refusal
# on a turn where nothing was asked and there is nothing to refuse.
#
# **Measured over `data/raw/chat_day_5b.txt`**, the SODA slice his social
# voice comes from, 769,464 replies. The four openings below occur 1,041 times
# and **727 of those are short enough to be a say and clear `social_rejection`
# today** -- that count is the hole this closes. Only the first opening was
# seen live, and it was seen twice: the audit's sentence on 2026-08-29 and
# "I'm sorry, but I'm not interested." answering `later` on the 2026-09-04
# sitting, which the family check refused for the wrong reason (no farewell
# marker) and which the four soft families would have served. The other three
# are the same opening in the corpus that produced it, listed with their
# counts so a later reader can narrow the rule back to what a runtime actually
# said rather than having to guess why they are here:
#
#     i'm sorry, but   879        unfortunately   136
#     sorry, but        21        i apologize      15
#
# **Opening position only, and that is half the rule.** The trailing apology
# is the voice -- "Came up empty, sorry." and "That one's outside my reach,
# sorry." are `docs/VOICE.md`'s own worked examples -- so a rule that read
# these words anywhere would refuse the register it exists to defend. The 696
# corpus replies carrying one away from the opening are scene monologues and
# 254 of them clear the guard; they stay, on `kin_address`'s reasoning that a
# position test is what keeps a word usable.
#
# **`i'm afraid` was measured and deliberately left out.** It is the same
# cushion in another dialect and it occurs 323 times in the slice -- but
# `data/raw/social8.txt`, the shipped payload, *trains* 135 replies that end
# in it ("I've got nothing to begin an alarm I'm afraid."), and the mined
# reply pool uses it for fear rather than for cushioning ("I'm afraid of the
# dark."). A rule that refused it would refuse what he was trained to say,
# which is the same mistake `sorry you` and `glad you` were removed for above.
#
# **The residue, named.** The second half of the leak -- "I don't have any
# questions." standing on its own -- is still caught by nothing. That is the
# interview register rather than a cushion, no count here measures it, and
# closing it is a different rule than this one.
_CUSHIONED = re.compile(
    r"^(?:i(?:'m| am) sorry,? but|sorry,? but|unfortunately|i apologi[sz]e)\b",
    re.IGNORECASE,
)


def cushioned_refusal(reply: str) -> str | None:
    """The apology this reply cushions a refusal with, or None.

    The matched opening rather than a bool, for `life_claim`'s reason: the
    reason is the interesting half and it goes out on the `say` event and into
    the session log, so a checkpoint that has learned to hedge is countable
    afterwards instead of being a fallback that silently fired.
    """
    hit = _CUSHIONED.search(reply or "")
    return hit.group(0).lower() if hit else None


# --------------------------------------------------------------------------
# Which move a reply answers
# --------------------------------------------------------------------------
#
# **Reply-side markers, not the user's move.** "thanks" is what the user says;
# "you're welcome" is what an answer to it sounds like. A list keyed on the
# trigger words would score the echo rather than the answer.
#
# **Deliberately independent of `corn/socialgen.py`'s tagger.** That module
# has an `_ANSWERS` map and the payload was filtered through it, so scoring
# with it would ask the arm to reproduce the rule its own training data was
# selected by. These markers are written from the reply side and calibrated
# against the hand-written pool lines independently.
#
# **Widened 2026-09-02 from reading arm 2's failures, before the generator was
# touched.** `corn_jr_260m_v4_ft_social2` read 54/112 here with 40 refused as
# "no family marker"; re-decoded and read one by one, about nine of the forty
# were answers the list could not see -- "I'm fine, thank you." to a
# wellbeing move, "No, nothing happening." to "anything happening", "Bye bye"
# to a goodbye, "Yeah, that sounds great." to "cool" -- and the other
# thirty-one answered nothing. The list is widened only with the reply-side
# forms those reads produced, and the four reads are pinned in
# `scripts/check_social.py` beside the two failures the row was built for.
#
# **`consolation` added 2026-09-05 (PLAN-CONVERSATION 5b).** The sixth family:
# the user stating a low mood, which no hatch, pool or row could see when
# "I had a rough day, my dog is sick" was declined live. Calibrated against
# the `LOW_REPLIES` pool before it was frozen, and `check_social.py` asserts
# every line of that pool reads as consolation and as nothing it excludes.
FAMILIES = ("greeting", "wellbeing", "thanks", "farewell", "ack", "consolation")

_FAMILY_MARKERS = {
    "thanks": r"you're welcome|youre welcome|no problem|not a problem|no trouble"
              r"|my pleasure|anytime|any time|don't mention it|dont mention it"
              r"|happy to help|glad i could|glad we could|glad to help|glad it"
              r"|glad that|you bet|of course|that's what i'm here for"
              r"|thats what i'm here for|did the trick|you got it|happy to\b"
              r"|no bother|not at all|least i could do|don't worry about it"
              r"|dont worry about it|it's nothing|its nothing",
    "wellbeing": r"doing well|doing fine|doing good|doing great|doing alright"
                 r"|doing all right|doing ok|doing okay|all good|all well"
                 r"|can't complain|cant complain|not bad|not too bad|pretty good"
                 r"|same as ever|never better|no complaints"
                 r"|i'm good|im good|i'm well|im well|i'm fine|im fine"
                 r"|i'm alright|im alright|i'm all right|im all right"
                 r"|i'm okay|im okay|i'm ok|im ok"
                 r"|going well|going good|going great|going fine|going alright"
                 r"|feeling good|feeling fine|feeling great|feeling alright"
                 r"|feeling all right|been good|been well|been fine|been great"
                 r"|it was good|it's been good|its been good|things are good"
                 r"|things are fine|good, thanks|fine, thanks|great, thanks"
                 r"|well, thanks|alright, thanks|okay, thanks|good thanks"
                 r"|great thanks|fine thanks"
                 r"|^(?:good|great|fine|alright|all right|grand)\b",
    # The open family, and the widest list for that reason: a greeting reply is
    # a hello or an open question about the user's business, and a thin list
    # scored eleven of the runtime's own greetings as carrying no family at all.
    "greeting": r"^(?:hey|hi|hello|howdy|morning|afternoon|evening"
                r"|good morning|good afternoon|good evening|good day|well, look)"
                r"|what's up|whats up|what's the word|whats the word"
                r"|what've we got|whatve we got|what are we|what's the plan"
                r"|whats the plan|how can i help|what can i do|what do you need"
                r"|good to hear from you|look who's here|how's the day"
                r"|hows the day|how's your day|hows your day|how are things"
                r"|what are you up to|ready when you are|i'm around|im around"
                r"|good to see you|nice to see you|how's it going|hows it going"
                r"|how are you|how've you been|howve you been|how have you been"
                r"|on the agenda|what's going on|whats going on|what's first"
                r"|whats first|what's left|whats left|how did the day go"
                r"|ready to get|a good one|what's happening|whats happening"
                r"|what's new|whats new|what's on\b|whats on\b|what's the story"
                r"|whats the story|what brings you|not much|nothing much"
                r"|nothing new|nothing happening|not a lot|all quiet|quiet here"
                r"|you too|likewise|still here|i'm here|im here|here i am"
                r"|perfect timing|alright, i'm here",
    "farewell": r"take care|catch you later|catch you\b|talk soon|talk later"
                r"|speak soon|see you later|see you around|see you\b|see ya"
                r"|until next time|have a good|have a nice|enjoy the rest"
                r"|enjoy your|goodnight|good night|night\b|sleep well|sleep tight"
                r"|get some rest|you know where to find me|i'll be right here"
                r"|take it easy|come find me|holler if you need|goodbye|^bye\b"
                r"|bye bye|bye now|bye for now|cheerio|so long|safe travels"
                r"|later\b|you too",
    "ack": r"sounds good|sounds great|sounds perfect|sounds fair|sounds right"
           r"|sounds like a plan|got it|sure thing|noted|fair enough|understood"
           r"|no worries|that works|works for me|copy that|makes sense|all set"
           r"|will do|gotcha|roger|good to know|good to hear|glad to hear"
           r"|anything else|no bother"
           r"|not a bother|that's fine|thats fine"
           r"|^(?:cool|perfect|great|alright|all right|right|fine|okay|ok"
           r"|yeah|yep|yup|sure|good|nice|brilliant|lovely|excellent|grand)\b",
    # PLAN-CONVERSATION 5b's list, plus `long one` and `small stuff` read off
    # the `LOW_REPLIES` pool during calibration -- the markers are frozen
    # against the pool, not the pool against the markers.
    "consolation": r"sorry to hear|that's rough|thats rough|rough one|tough one"
                   r"|long one|hang in there|take it easy|go easy|get some rest"
                   r"|no good|that's no good|thats no good|been there"
                   r"|here if you need|say the word|off your plate|hand it over"
                   r"|anything i can do|small stuff|feel better|sorry about that"
                   r"|hope .*(?:feels better|gets better|picks up|goes better)",
}
_FAMILY_RE = {k: re.compile(v, re.IGNORECASE)
              for k, v in _FAMILY_MARKERS.items()}


def reply_families(reply: str) -> set:
    """Every social family this reply reads as an answer to."""
    return {k for k, r in _FAMILY_RE.items() if r.search(reply or "")}


# **The families a reply must NOT answer instead**, read from the reply side.
# Greeting and farewell are the pair that actually confuse -- a parting line
# and an opening line are both short, warm and in vocabulary -- so they exclude
# each other, and every family excludes the farewell tail: "Perfect. I'll talk
# to you soon." is the live failure `social.family` was built on, one word out.
# A greeting also excludes the thank-you answer, because "Hey, no problem.
# What's going on?" is answering a favour nobody asked for. Consolation
# excludes the positive report -- "That's good to hear" to "I'm kind of tired"
# is the live failure of 2026-09-04 -- and the thanks and greeting answers.
#
# `corn/socialgen.py` reads this same table as its `_EXCLUDES`, so the payload
# filter and the runtime refuse the same pairs.
EXCLUDED = {
    "greeting": ("farewell", "thanks"),
    "farewell": ("greeting",),
    "wellbeing": ("farewell",),
    "thanks": ("farewell",),
    "ack": ("farewell",),
    # `ack` too, read off the live line: "That's good to hear. How was your
    # day?" answered "I'm kind of tired today honestly" on arm 2, and "good
    # to hear" is the acknowledgement of a *positive* report.
    "consolation": ("wellbeing", "thanks", "greeting", "ack"),
}

# **Where the no-marker clause is hard, and it is where the live defect sits.**
# Every "does not close" line of 2026-09-04 was a greeting-shaped or
# wellbeing-shaped non-goodbye, and every consolation miss was a positive
# report; a markerless reply to a farewell or a low mood is the defect, not a
# reply the list happens not to know. On greeting, wellbeing, thanks and ack a
# markerless reply is served and counted (`soft_reject` on the say event), so
# arm 6's wider vocabulary is measured rather than refused.
HARD_FAMILIES = frozenset({"farewell", "consolation"})


def family_rejection(reply: str, family: str) -> tuple[str | None, str | None]:
    """(hard, soft): why this reply may not be spoken as a `family` answer.

    `hard` is a reason the runtime refuses on; `soft` is a reason it logs and
    serves anyway. At most one of the two is set. Both are `None` when the
    reply reads as an answer to `family` and to nothing `family` excludes.

    **A reply that answers its own family passes, whatever else it also
    reads as.** "Hey, good to see you." is a greeting pool line that carries
    the farewell marker `see you`, and "Have a good one." a farewell that
    carries the greeting marker `a good one`; answering *and* handing back is
    the register the pools are written in, and `score_social_family` has
    never refused it. The exclusion clause is therefore the *diagnosis* of a
    miss rather than a second rule: with no marker for its own family, a
    reply that carries an excluded family's marker is "wrong family" and is
    hard everywhere, because a hello answering a goodbye is wrong whatever
    else the marker list knows. A miss with no marker at all is hard only on
    `HARD_FAMILIES` -- see the comment there -- and soft on the rest.

    A family this module does not know gets no opinion at all: the caller is
    a hatch that matched a set, and a set without a family here is a set
    whose replies have not been calibrated.
    """
    if family not in _FAMILY_RE:
        return None, None
    fams = reply_families(reply)
    if family in fams:
        return None, None
    wrong = sorted(fams & set(EXCLUDED.get(family, ())))
    if wrong:
        return f"wrong family: {wrong[0]}", None
    if family in HARD_FAMILIES:
        return "no family marker", None
    return None, "no family marker"


# --------------------------------------------------------------------------
# The open social turn -- PLAN-PERSONALITY §5d
# --------------------------------------------------------------------------
#
# "do you like pokemon" -> "Yeah, I love pokemon. It's my favorite game." was
# served live on `social8` (STATUS 2026-09-05, late) and nothing above sees it:
# `_LIFE_CLAIM` has no "i love", `kin_address` has nothing to catch, and the
# reply is a finished, unnamed, undigited sentence. A preference is a life
# claim by another door -- a model has no favorite game -- and the rule is
# the same shape as `life_claim`'s: the matched phrase, for the `why` column.
_PREFERENCE = re.compile(
    r"\b(?:"
    r"i (?:love|like|enjoy|adore|hate|prefer|can't stand|cannot stand)\s+"
    r"(?!you\b|it when\b|that you\b|to help\b|to hear\b)\w"
    r"|my (?:\w+ )?(?:favorite|favourite)\b"
    r"|i(?:'m| am) (?:a )?(?:big |huge )?fan of\b"
    r"|i(?:'m| am) (?:really )?into\b"
    r"|i(?:'ve| have) always (?:loved|liked|wanted)\b"
    r")",
    re.IGNORECASE,
)


def preference_claim(reply: str) -> str | None:
    """The first taste he claims to have, or None.

    "I love you too" is `kin_address`'s territory when it carries a kin term
    and is otherwise an affection reply the open family may keep, so `you`
    is carved out of the object; "I like to help" and "I love it when" are
    the voice, not a life, and are carved out the same way.
    """
    hit = _PREFERENCE.search(reply or "")
    return hit.group(0).lower() if hit else None


# The hand-back: an open move answered without a claim has to give the turn
# back, or it is a shrug. A question to the user is the plain form; the rest
# are the offers and the deferrals the hand-written lines use. Frozen against
# those lines, not the lines against this list, as the consolation markers
# were.
_HANDS_BACK = re.compile(
    r"\?\s*$"
    r"|\byou(?:'ll| will) have to\b|\btell me\b|\byour call\b|\byou tell me\b"
    r"|\bwhat's yours\b|\bwhats yours\b|\bgo on\b|\btry me\b|\bhit me\b"
    r"|\blet's hear it\b|\blets hear it\b|\byou first\b|\bup to you\b"
    r"|\bsay the word\b|\bwhat can i do\b|\bwhat do you need\b"
    r"|\bhappy to (?:help|hear it)\b|\bfire away\b|\bwhenever you're ready\b"
    r"|\bwhat are we doing\b|\bwhat's first\b|\bwhats first\b",
    re.IGNORECASE,
)


def hands_back(reply: str) -> bool:
    """Whether the reply gives the turn back -- a question, an offer, a deferral."""
    return bool(_HANDS_BACK.search(reply or ""))


# --------------------------------------------------------------------------
# Asking the same thing twice
# --------------------------------------------------------------------------
#
# **The one rule here that is not a function of a single reply**, and it is in
# this module for the reason the module exists: `tests/`, a probe over the bare
# checkpoint, and one day the runtime itself all have to agree about what a
# repeated question is, and a rule described in three places will eventually be
# three rules. Everything below still imports nothing but `re`.
#
# The sitting it was written from, reported by the owner 2026-09-08 and
# reproduced on the shipped instance the same day:
#
#     Hi.                     Hi, how are you today?
#     Good, how are you?      Good! How are you today?
#
# He answered correctly and then asked a question the person had answered one
# turn earlier. No rule above sees it: both sentences are finished, unnamed,
# undigited and in register, and they are not the same sentence. It is only
# wrong in the light of the turn before it -- so the unit is the question and
# the scope is the conversation.

_QUESTION = re.compile(r"[^.!?]*\?")


def questions(reply: str) -> list:
    """Every question in a reply, as a tuple of its words.

    Case and punctuation are dropped. A reply with no question mark has none,
    which is the whole of the parse -- an interrogative with a full stop is
    not what the observed defect looks like and a rule that guessed at one
    would fire on ordinary sentences.
    """
    out = []
    for chunk in _QUESTION.findall(reply or ""):
        words = tuple(re.findall(r"[a-z0-9']+", chunk.casefold()))
        if words:
            out.append(words)
    return out


def asked_before(question, earlier) -> tuple | None:
    """The earlier question this one repeats, or None.

    **Not equality**, because "How are you?" and "How are you today?" are one
    question with a word on the end and equality passes the second.

    **Not containment either**, which was the first version and is what the
    observed sitting itself breaks: "Hi, how are you?" has no sentence break
    before the question, so the greeting is glued on and `{hi, how, are, you}`
    neither contains nor is contained by `{how, are, you, today}`. That rule
    scored the reported transcript as clean.

    So: **three quarters of the shorter question's words appear in the
    longer.** That admits one glued-on greeting or one trailing "today" and
    keeps out two questions that merely open alike -- "what's on the agenda"
    against "what's on today" shares two words of three and is left alone.

    **Two words in common at minimum**, which is what keeps a bare hand-back
    out of it: "You?" is a legitimate way to give the turn back after
    answering, and its one word appears in every wellbeing question ever
    asked. `hands_back` counts that move as correct and this must not
    contradict it.
    """
    a = set(question)
    for other in earlier:
        b = set(other)
        shared = a & b
        if len(shared) >= 2 and len(shared) / min(len(a), len(b)) >= 0.75:
            return other
    return None
