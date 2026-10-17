"""`web_search` with something real behind it.

**This backend cost no retraining and that is not luck.** The tenth finding
shaped `web_search_tool` to return a short `answer` field rather than a page of
snippets, precisely so the model would read a lookup back instead of composing
over results -- `corn/tools.py` argues it at length. The consequence, collected
here: the interface the model learned is exactly the interface a real search
fills. Swapping the `FACTS` table for the internet is a different function
behind the same four payloads, and the weights never know.

So the whole job of this file is *reduction*: turn a search result into one
sentence short enough to say out loud, or admit there isn't one. Anything that
returned three results and left the model to summarise would undo the finding.

**The shapes, which are the contract** (`corn/tools.py`):

    {"answer": ..., "source": ..., "query": ...}          a hit
    {"ok": false, "reason": "empty_query", "clarify": ...} nothing was asked
    {"ok": false, "reason": "no_results", "say": ...}      nothing was found
    {"ok": false, "reason": "unreachable", "say": ...}     the network failed
    {"ok": false, "reason": "self_referential", "say": ...} it was not the web's
                                                            to answer
    {"ok": false, "reason": "blocked", "say": ...}         a provider said no

`self_referential` is the seventy-eighth finding's, and it is a *fifth slug in
the fourth shape* rather than a fifth shape -- `{ok, reason, say}` again, read by
deference, spoken verbatim, `reason` never inspected by the model. The same
argument the timeout slug already made: reusing `no_results` would have had him
tell the user nothing was found about himself, when the truth is that nobody
should have looked. See `_ABOUT_ME`.

**The sixth is `blocked`, and it exists because two true sentences were being
said about a third thing.** A provider that answers "not to you" -- a bot
challenge, a 429, a 403 -- has neither failed to be reached nor looked and found
nothing, and until this slug it was reported as whichever of those the rest of
the loop happened to produce: `unreachable` when the other providers also fell
over, which tells the user the internet is down when one host is rate-limiting
this machine, and `no_results` when they did not, which hides the refusal
entirely. The action both were concealing is the same one -- wait and ask again
-- and neither sentence lets the user find it. `_Blocked` has known the
difference at the point of detection since the live run that found the
challenge page; what was missing was a way for it to leave the provider loop.

It is another slug in the same shape rather than a new shape, on
`self_referential`'s own argument: `{ok, reason, say}` read by deference, spoken
verbatim, `reason` never inspected by the model, so no weight knows a sixth
reason exists and nothing here costs a retrain. It carries two sentences for
`SELF_SAYS`'s reason -- a search nobody else got to and a search the other
providers completed empty-handed are refusals of different sizes -- and one
runtime-side field, `corn.tools.BLOCKED_BY`, which is what a probe groups on.

**A hit may carry a fifth field, and the model never sees it.** `PASSAGE` is
the provider's text *before* the reduction above, handed forward so
`corn/agent.py`'s `web_search` executor can read it as windows and answer the
question that was actually asked -- the extraction half of
`docs/PLAN-WEB-SEARCH.md`. It is stripped from every payload before the
observation is built (`corn.tools.take_runtime`), so the four shapes remain
exactly the four shapes the weights learned. Nothing here changes when no
reader is wired: the field is written either way and read by nobody.

The fourth slug is new and the *shape* is not, which is the distinction
`_recall_day` already rests on: an unfamiliar reason arriving in the familiar
`{ok, reason, say}` structure is read by deference, because the model speaks
`say` and never inspects `reason`. Reusing `no_results` for a timeout would
have been the alternative and it would have made the model tell the user
nothing was found when the truth is that nobody looked.

**Four providers, tried in order, all keyless.** DuckDuckGo's Instant Answer
endpoint returns an abstract with an attributed source, which is the payload
shape almost exactly; it is also empty for most queries, which is why Wikipedia's
REST summary follows it rather than replacing it. Both are entity lookups, and
between them they still miss the ordinary phrasings -- "capital of Laos",
"boiling point of water" -- so DuckDuckGo's HTML results page runs last and
supplies a snippet for anything the first two have nothing for. None needs an
account, so a person hosting their own Corn-Jr has nothing to sign up for --
VISION §4 makes that a design constraint rather than a nicety.

**Google is not one of them, and it cannot be.** Scraping google.com/search is
the obvious fourth and it no longer returns results to anything without a
JavaScript engine: the response is HTTP 200 carrying an `enablejs` interstitial
and zero result links, on every User-Agent tried including a current Chrome
one. Libraries that wrap the scrape (`google`, `googlesearch-python`) inherit
that and fail *silently*, yielding an empty generator rather than raising --
which is the worst shape a provider can fail in, because the chain reads it as
"nothing found" rather than "this is broken". A working Google needs the
Programmable Search JSON API and therefore a key, which is the constraint above
and the reason this file does not have one.

**Order is a contract decision, not a preference.** The two lookup endpoints
return an *abstract* -- an extract written to be read on its own -- and the
results page returns a *snippet* cut to fit a search listing. The first is
closer to what the model was trained to read back, so it goes first, and the
looser one is what runs when the tight ones have nothing.

**Queries leave the machine.** That is what a search tool is, and it is worth
saying out loud in the file that does it: whatever the user asks Corn-Jr to look
up is sent to a third party. `--search` is opt-in on the server for that reason,
and the table-backed default is what runs until someone turns it on.
"""

from __future__ import annotations

import re
import time

import requests
from bs4 import BeautifulSoup

from corn.tools import BLOCKED_BY, LEAD_ANSWERS, PASSAGE

DDG = "https://api.duckduckgo.com/"
WIKI = "https://en.wikipedia.org/api/rest_v1/page/summary/"
DDG_HTML = "https://html.duckduckgo.com/html/"

# §3 budgets tool calls at 0-200ms and `web_search` is declared `slow`, so the
# user has already been told to expect a wait. This is the point past which
# waiting is worse than admitting failure: long enough for a slow provider,
# short enough that a dead one does not hold the turn open.
TIMEOUT = 4.0

# **Wikimedia rejects the default `python-requests` User-Agent with a 403**, so
# this is required rather than polite -- their policy asks every client to
# identify itself. It cost an afternoon's worth of "unreachable" the first time
# this backend ran live, because the broad `except` below turned a fixable
# header into a permanent network failure. A host running their own Corn-Jr
# should put a contact address in here; Wikimedia asks for one and rate-limits
# harder without it.
USER_AGENT = "Corn-Jr/0.1 (self-hosted personal assistant)"

# One sentence, because the reply is spoken. A paragraph would be read out in
# full by a model whose only job here is to copy, and §3's budget does not
# survive it.
MAX_ANSWER = 400


def _first_sentence(text: str, limit: int = MAX_ANSWER) -> str:
    """Trim to something sayable without cutting a word in half.

    Prefers a sentence boundary and falls back to a word boundary, because an
    answer that stops mid-word is one the model will read out mid-word.
    """
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit]
    for stop in (". ", "? ", "! "):
        i = cut.rfind(stop)
        if i > limit // 3:
            return cut[: i + 1].strip()
    i = cut.rfind(" ")
    return (cut[:i] if i > 0 else cut).strip() + "..."


def _flat(text: str) -> str:
    """The provider's text, whole, on one line.

    **The counterpart of the reduction above and the reason it stopped being
    lossy.** `_first_sentence` returns what can be *said*; this returns what
    was *read*, and `corn.extract` is what gets the second one back down to a
    sentence using the question rather than the position. Whitespace is
    flattened for the same reason a payload may not contain a newline
    (`harness/protocol.py`) and because a window cut across a line break is a
    window whose tokens are mostly formatting.
    """
    return " ".join(text.split())


# `_first_sentence` is a *truncator* -- it only cuts once the text passes
# MAX_ANSWER, so anything shorter is returned whole however many sentences it
# is. That is right for an abstract, which is written to be read as a unit, and
# wrong for a snippet, which is a listing cut that runs on into whatever the
# page said next. This takes the first sentence of one regardless of length,
# which is what the module docstring means by reduction.
#
# The length floor is the abbreviation guard: "Mt. Everest is the highest
# mountain" would otherwise reduce to "Mt.". A real first sentence that short
# does not carry an answer, so keeping more is the safe direction.
_MIN_SENTENCE = 25

# **The results page rate-limits, and it does not use a status code to say so.**
# After a handful of quick queries it answers HTTP *202* with a "confirm this
# search was made by a human" challenge -- not 429, not 403, so
# `raise_for_status` is happy and the snippet selector simply finds nothing.
# Read literally that is a miss, and it is not one: the provider declined to
# look. Letting it fall through as `no_results` would tell the user nothing was
# found when nobody searched, which is the exact confusion the fourth slug
# exists to prevent. So this raises, and the raise now carries far enough to be
# said out loud: the loop keeps the refusal, the provider counts as not reached,
# and the turn ends in `blocked` naming the host rather than in a sentence about
# the internet being gone.
#
# No attempt is made to get around the challenge. It is a bot check and the
# honest answer to one is to be a well-behaved client that backs off.
_CHALLENGE = "made by a human"


class _Blocked(RuntimeError):
    """The provider answered, and what it said was 'not to you'.

    Carries the two things that leave this file: `provider` is the host, which
    is what the spoken sentence names because it is the only part a user can
    act on, and `cause` is a slug, which is what a probe groups on. Splitting
    retrieval's misses by reason is precisely what could not be done when
    `PLAN-EXTRACTION-READER` §4 counted the scraper refused on 13 of 24 --
    "challenged on 13" and "found nothing on 13" are different findings and the
    count could not tell them apart. `detail` is for the log and for nobody
    else.
    """

    def __init__(self, provider: str, cause: str, detail: str = "") -> None:
        super().__init__(f"{provider}: {detail or cause}")
        self.provider = provider
        self.cause = cause
        self.detail = detail


# **The two status codes that mean "not to you", and the boundary is narrow on
# purpose.** `_wiki`'s own comment argues that a 4xx is a miss -- 404 is "no
# such page", 400 is this client asking wrong, and from the user's side a
# provider that answered is a provider that looked. That holds for every code
# in the range except these two: 429 is the provider declining to serve this
# machine for a while and 403 is it declining outright, and neither is a
# statement about the query. `USER_AGENT`'s comment above is the case in point
# -- a 403 for an unset agent cost an afternoon of "unreachable" and was a
# fixable header, which is a thing an operator can only fix if he is told.
#
# So these two lift out of the miss branch and the rest of the range stays
# exactly where it was. Nothing here retries or backs off: `_HTML_GAP` is the
# politeness this file practises, and the honest answer to a refusal is to
# report it.
_REFUSALS = {403: "refused", 429: "rate_limit"}


def _refused(r, provider: str) -> None:
    """Raise `_Blocked` if this response is a refusal; otherwise do nothing.

    Called before each provider's own status handling rather than inside it,
    so the carve-out reads the same way in all four and a provider that grows
    a fifth status branch cannot quietly swallow a 429 behind it.
    """
    cause = _REFUSALS.get(getattr(r, "status_code", None))
    if cause is not None:
        raise _Blocked(provider, cause, f"HTTP {r.status_code}")


# **Two of the corpus's 25 search phrasings put words on *both* sides of the
# query, and those are the two he cannot cut.** Measured on the 260M, 10 draws
# each, table-backed so the right answer is known exactly:
#
#     what's {q}              10/10 exact
#     remind me what {q} is    6/6  exact
#     look {q} up for me       0/10 -- "the currency of Gleduthholm up for me"
#     what would {q} be        0/10 -- "what would the wingspan of the X be"
#
# **The corpus is not what is wrong here.** `data/raw/tools*.txt` labels these
# 337/337 and 351/351 correctly, on exposure comparable to `what's {q}`'s 381.
# The difference is structural rather than statistical: a suffix-only template
# needs a prefix dropped, and these need a boundary found in the middle of the
# sentence with material on either side of it. At 260M that is a harder cut, and
# no amount of this file will change it -- the fix in the weights is a corpus
# question for a retrain, and this is what the runtime can do meanwhile.
#
# So the affixes come off here. It is narrow on purpose: only these literals,
# only when something is left, and the transcript upstream still records what
# he actually wrote. `scripts/check_search.py` imports `SEARCH_TEMPLATES` and
# fails if a phrasing ever appears that these do not cover, so the list cannot
# drift away from the corpus that motivated it.
# Every phrasing with material on both sides of `{q}`, both halves, longest
# first so a longer prefix wins over a shorter one that prefixes it. Two of the
# four are cuts he makes correctly today; they are here anyway, because the
# stripping only fires when the words are actually present and the cost of
# covering a template that starts failing later is nothing.
# **Longest first, because the loop breaks on the first match.** The four at the
# top are the corpus phrasings `strip_affixes` was written for; everything below
# the blank line is the seventy-eighth finding's phrasing gap -- session 13 put
# eight facts at the chain in two phrasings each and got **natural question 1 of
# 8, noun phrase 5 of 8**. He copies the utterance exactly as trained and the
# copy is a question; the provider wants the noun phrase. These come off here so
# that "what is the boiling point of water" reaches it as "the boiling point of
# water", which is the phrasing that hit.
#
# Pure removal only. An opener that has to be *rewritten* rather than dropped --
# "who wrote X" is not "X" -- lives in `_REPHRASE` below, because a strip that
# left "Pride and Prejudice" would search the book and not its author.
_PREFIXES = (
    "remind me what ", "any idea what ", "what would ", "look ",

    # The imperative openers. `look ` above was carrying "look up X" on its own
    # and leaving the preposition behind; `search for ` is the one the
    # seventy-eighth finding names outright -- "search for Nikola Tesla" reached
    # the provider with its verb attached on both sides of the grammar A/B.
    "look up ", "search for ", "search ", "google ", "find me ", "find ",

    # The interrogative openers, which are the phrasing gap. Session 13 put
    # eight facts at the chain in two phrasings each and got **natural question
    # 1 of 8, noun phrase 5 of 8**: he copies the utterance exactly as trained
    # and the copy is a question, where the provider wants the noun phrase.
    # These come off so that "what is the boiling point of water" arrives as
    # "the boiling point of water", which is the phrasing that hit.
    "can you tell me ", "could you tell me ", "do you know ", "tell me ",
    "i want to know ", "find out ",
    "what is ", "what's ", "whats ", "what are ", "what was ", "what were ",
)
_SUFFIXES = (" up for me", " is", " be")

# Below this a strip has eaten the question rather than its packaging.
_MIN_QUERY = 4


# **His own name, at the front of a query, and the one tool it costs.** The
# seventy-eighth finding measured the vocative defeating the social hatch over
# all 275 pool phrases; on the tool side it poisons `web_search` and nothing
# else. `send_text` and `save_note` extract a bounded entity and are immune, but
# a query is a run of the sentence and the address is sitting at its front:
#
#     look up the capital of Iceland         -> "the capital of Iceland"
#     corn look up the capital of Iceland    -> "corn look up the capital of ..."
#
# Off before the affixes, so "corn, look up X" still finds "look up " behind it.
#
# **`jr` is here and `junior` deliberately is not**, which is the one place
# this regex and `corn/agent._VOCATIVE` are allowed to disagree. The hatch one
# strips both, because a false strip there can only mis-file a turn into a set
# that is matched whole and nothing leaves the process. This one decides what
# a live provider is asked, and the cost side is already visible on the token
# it was written for: "corn syrup prices" goes out as "syrup prices". `jr`
# leading a real query is not a thing anyone types; `junior` is -- "junior
# doctor pay" would go out as "doctor pay" -- so the short form is taken and
# the long one is left for a decision with a measurement behind it.
_QUERY_VOCATIVE = re.compile(r"^(?:corn(?:[- ]?jr|[- ]junior)?|jr)\b[\s,:-]*", re.I)


def strip_affixes(query: str) -> str:
    """Take the phrasing off a query he could not cut himself."""
    # Terminal punctuation comes off first, and for the say rather than the
    # provider: measured 2026-08-29, the provider answers identically with and
    # without it, but a query ending "." echoed into the no_results say reads
    # "...prejudice.." back to the user. Corpus queries never carry it -- they
    # are exact spans of phrasings that put no punctuation at the edge -- so
    # this fires only on live copies of a whole typed question. First, so a
    # suffix like " is" still matches when the question ended "is?".
    q = query.strip().rstrip(".?!").rstrip()
    q = _QUERY_VOCATIVE.sub("", q).strip() or q
    for suffix in _SUFFIXES:
        if q.endswith(suffix) and len(q) - len(suffix) >= _MIN_QUERY:
            q = q[: -len(suffix)].strip()
            break
    # **The longest match, not the first.** Ordering a tuple by length is a
    # trap the seventy-eighth finding walked into from the other side: "look "
    # sits in front of "look up ", so `look up Ada Lovelace` was cut to `up Ada
    # Lovelace` and the provider was asked about the preposition. Which prefix
    # wins should be a property of the strings, not of where somebody added a
    # line, so it is computed here and the tuple below stays readable.
    #
    # Case-insensitively, because a live query is a copy of a typed sentence and
    # a typed sentence starts with a capital. The corpus spans are lower case
    # and never noticed; "What is the boiling point of water" is the shape this
    # exists for and it would have missed every prefix in the list.
    low = q.lower()
    hit = [p for p in _PREFIXES
           if low.startswith(p) and len(q) - len(p) >= _MIN_QUERY]
    if hit:
        q = q[len(max(hit, key=len)):].strip()
    return q or query.strip()


# **The openers a strip cannot handle, and the second half of the phrasing
# repair.** "who wrote Pride and Prejudice" missed where "the author of Pride
# and Prejudice" hit, and no amount of prefix removal turns the first into the
# second -- the interrogative *is* the relation being asked about, so dropping
# it drops the question. Each row rewrites one opener into the "the X of Y"
# shape the invented index and the live providers both prefer.
#
# **Applied as a retry, not as a rewrite.** `web_search` asks the providers the
# query as given first and only reformulates when that came back empty, so a
# phrasing that already worked is never touched and nothing measured before
# today changes shape. The cost is one extra round of providers on a miss; the
# alternative -- rewriting up front -- would have put a guess in front of every
# query that did not need one.
#
# A table rather than a rule, and honestly so: these are the relations the live
# batteries actually produced. An opener not listed here reaches the providers
# as typed, exactly as it did before.
_DIMENSION = {
    "tall": "height", "high": "height", "deep": "depth", "long": "length",
    "wide": "width", "old": "age", "big": "size", "heavy": "weight",
    "far": "distance", "hot": "temperature", "fast": "speed",
}

_HOW_DIMENSION = re.compile(
    r"^how (" + "|".join(_DIMENSION) + r") (?:is|are|was|were) (.+)$")
_WHEN_EVENT = re.compile(
    r"^when (?:was|were) (.+?) (born|built|founded|written|released|"
    r"published|established|invented|discovered)$")

_REPHRASE = (
    (re.compile(r"^who (?:wrote|authored) (.+)$"), r"the author of \1"),
    (re.compile(r"^who (?:invented|discovered) (.+)$"), r"the inventor of \1"),
    (re.compile(r"^who (?:founded|created) (.+)$"), r"the founder of \1"),
    (re.compile(r"^who directed (.+)$"), r"the director of \1"),
    (re.compile(r"^who painted (.+)$"), r"the painter of \1"),
    (re.compile(r"^who composed (.+)$"), r"the composer of \1"),
    # **The row where the rewrite is not about the provider at all -- it is
    # about `_covers`.** Measured live 2026-08-29: `who won the 2026 super
    # bowl` returns ten results and the rank-1 result *is* the answer -- "The
    # Seattle Seahawks defeated the New England Patriots Sunday to win the
    # 2026 Super Bowl." It passes `_answers` and `_prose` and then scores
    # **0.75**, because the query term `won` is the one word the snippet does
    # not contain and the four-character prefix rule cannot bridge `won` to
    # `win`. `MIN_COVER` is 1.0, so the right answer at rank 1 is discarded
    # and the user is told nothing was found. Asked as `the winner of the 2026
    # super bowl` the same snippet scores **1.00** -- `winner` matches `win`
    # through the rule's other side -- and the same second returns it.
    #
    # The bar is not what is wrong here. `MIN_COVER` at 1.0 is what stopped
    # him inventing a height for Everest out of a snippet that mentioned
    # neither (VISION §9), and dropping it to 0.75 to buy this one query would
    # loosen every query on the machine. So the verb is rewritten into the
    # noun the snippet actually uses, which is what every row above does.
    #
    # `won` only, and not `wins`/`win`: this is the relation the live battery
    # produced, and the table stays a record of what was measured.
    (re.compile(r"^who won (.+)$"), r"the winner of \1"),
    (re.compile(r"^who is the (.+)$"), r"the \1"),
    (_HOW_DIMENSION, None),
    (_WHEN_EVENT, None),
    # **The leading word is optional because he drops it.** Live on
    # `corn_jr_260m_v4`, "what language do they speak in Brazil" was copied
    # into the call as `language do they speak in Brazil` -- his copy is lossy
    # at the front, and a row anchored on "what" then matched nothing and the
    # question reached the provider whole. Anchoring on the part he keeps is
    # what makes this a repair rather than a row that only works in a test.
    (re.compile(r"^(?:what )?language (?:do|does) (?:they|people|you) "
                r"speak in (.+)$"), r"the language of \1"),
    # Before the general count row, because that row's non-greedy group rides
    # a verb into the noun slot for exactly this phrasing -- finding 79 §5's
    # "the number of people live in tokyo". `population` is also the word the
    # answer sentence actually carries ("Tokyo has a population of..."), which
    # is the winner-row's lesson applied rather than relearned.
    (re.compile(r"^how many people live in (.+)$"), r"the population of \1"),
    (re.compile(r"^how many (.+?) (?:are there )?in (.+)$"),
     r"the number of \1 in \2"),
    (re.compile(r"^how much does (.+?) cost$"), r"the price of \1"),
    (re.compile(r"^where (?:is|are) (.+)$"), r"the location of \1"),
)


def _rephrased(query: str) -> str | None:
    """The query as a noun phrase, or `None` if no row in `_REPHRASE` fits.

    `None` rather than the query unchanged, so the caller can tell "there is a
    second thing to try" from "there is not" and skip a second round of
    providers whose answer it already has.
    """
    q = " ".join(query.strip().rstrip(".?!").lower().split())
    for shape, template in _REPHRASE:
        m = shape.match(q)
        if m is None:
            continue
        if template is not None:
            out = shape.sub(template, q)
        elif shape is _HOW_DIMENSION:
            out = f"the {_DIMENSION[m.group(1)]} of {m.group(2)}"
        else:
            verb = m.group(2)
            out = (f"the birth date of {m.group(1)}" if verb == "born"
                   else f"the date {m.group(1)} was {verb}")
        out = out.strip()
        if out and out != q:
            return out
    return None


# **The one thing that must not leave the machine, and the reason it is here
# rather than in a hatch.** The seventy-eighth finding's sharpest result is that
# a hatch miss is not a degraded answer -- it is a private or self-referential
# question reaching a search engine. `who made you`, `how do you work` and
# `what did I do on Friday` all went to the internet, and the last of them came
# back with a Reddit thread about Friday nights served as an answer about the
# user's own week.
#
# The hatches are the primary defence and they are wider now. This is the
# backstop, and it sits at the last point before the network: whatever the
# matchers miss, and however they are widened or narrowed later, a question
# about *him* or about *the user's own record* is not asked of a provider.
#
# **What it deliberately does not block.** Not bare "you" -- "how do you make
# bread", "how do you spell necessary" and "what do you call a baby fox" are
# ordinary lookups and the commonest shape of question there is. Not bare "we"
# -- "when did we land on the moon" is a real query. Blocking either would trade
# a rare privacy leak for a constant false refusal, which is the wrong side of
# that trade. Every row below names a *predicate* about him or about the user's
# own record, never a pronoun on its own -- and the `we` rows are verb-keyed for
# exactly that reason: "what did we talk about yesterday" is this conversation
# and "when did we land on the moon" is the Apollo programme, and only the verb
# tells them apart.
_ABOUT_ME = (
    re.compile(r"^(?:who|what|when|where|why|how) (?:made|built|created|"
               r"trained|wrote|designed|programmed|developed) you\b"),
    re.compile(r"^how (?:do|does|did) you (?:work|run|think|function|operate)\b"),
    re.compile(r"^what (?:can|do|could) you do\b"),
    re.compile(r"^(?:what|which) (?:tools?|models?|version|weights)\b.*\byou\b"),
    re.compile(r"^are you (?:an? )?(?:ai|bot|robot|human|person|real|"
               r"conscious|alive|sentient|chatgpt|claude|gpt)\b"),
    re.compile(r"^(?:what|who) are you\b"),
    re.compile(r"\byour (?:name|tools?|model|weights|training|creator|maker|"
               r"purpose|code|source|prompt|instructions)\b"),
)

# **Past and perfect only.** `do` is not here: "how do I fix a tap", "what do I
# need for bread" and "where do I find the setting" are ordinary lookups and
# the present tense is what they are built out of. The record-shaped question
# is the one in the past -- "what did I", "what have I", "who called me" --
# and the past is the shape every leak the audit measured actually took.
_ABOUT_YOU = (
    re.compile(r"^(?:what|when|where|who|why|how)? ?(?:did|have|had|was|were) i\b"),
    re.compile(r"\b(?:i|we) (?:did|do|said|say|told|tell|noted|note|wrote|"
               r"write|asked|ask|talked|talk|discussed|discuss|mentioned|"
               r"mention|covered|cover)\b"),
    re.compile(r"\bmy (?:notes?|note|calendar|schedule|diary|log|history|"
               r"password|passwords|contacts?|messages?|texts?|day|week|"
               r"inbox|emails?|voicemails?|missed calls?|call log)\b"),
    # **The record asked about without a possessive at all.** `harness/
    # routegrid.py`'s Grid R read 2026-09-06 on a live server: "any new
    # messages", "check my inbox" and "what did she say in her message" are
    # the user's own message store, and none of the rows above names them --
    # the first two carry no "my" the third row reads, and the last is
    # somebody else's message *to* the user. Predicates again, never the bare
    # noun: "messages" alone would refuse "the messages of the quran", and
    # "any new messages" cannot mean anything but the inbox.
    re.compile(r"\b(?:any|new|unread|got any|have i got|do i have) "
               r"(?:new |unread |missed )?(?:messages?|texts?|emails?|"
               r"voicemails?|calls?)\b"),
    re.compile(r"\bin (?:his|her|their) (?:message|text|email|voicemail)\b"),
    # **The object pronoun, which every row above misses.** "who called me
    # yesterday" carries no "I" and no "my", so it passed all three rows and
    # reached the live provider -- measured on 2026-08-30, and the one leak
    # of that round that actually left the machine. The discriminator here is
    # the same one the block comment commits to: tense. "called me" is the
    # user's call log; "call me" is a Blondie title, so "call me maybe
    # lyrics" and "who sings call me" still go out, and only the past form
    # tells the record apart from the song. The did-construction ("did
    # anyone text me") stays unblocked on purpose: a row loose enough to
    # catch its base verb also catches "did blondie sing call me", and the
    # hatches remain the primary defence for that shape.
    re.compile(r"\b(?:called|texted|messaged|phoned|rang|emailed) me\b"),
    # **Who the user is, and this is the one row whose failure sends the
    # owner's own name to a third party.** Measured 2026-08-30: `what is my
    # name?` reaches this backstop only when a hatch has missed it, and every
    # row above lets it straight through -- the first keys on a past-tense
    # auxiliary ("what did I", "was I"), the second on a verb the user did,
    # the third on a noun that is a *record* (`my notes`, `my calendar`), and
    # an identity question is none of the three. `packs/about-me.md` holds the
    # answer on this instance, so the question has a local home and there is
    # never a reason for it to leave.
    #
    # **Predicates, not the pronoun**, on the block comment's own terms: every
    # alternative below names something that is the user's own to know, and
    # `my` is required -- so "the meaning of the name Emma" and "most popular
    # baby names 2026" still go out. `who am i` and `where do i live` are
    # anchored, because those two are record-shaped only as a whole utterance.
    #
    # **What it costs, said plainly.** "How do I change my name legally" and
    # "what does my birthday say about me" are ordinary lookups and this row
    # refuses both. That is the same trade the `my (?:notes?|...)` row above
    # already took -- an unanchored possessive catches the phrase wherever it
    # sits -- and it is taken again because what is on the other side is the
    # owner's name, the one fact VISION §4 keeps off the network. Narrower
    # would mean enumerating question openers, and `what's my name`, `who am
    # i` and `remind me of my birthday` do not share one.
    #
    # Deliberately keyed on `my` and not on `_ABOUT_ME`'s `\byour name\b`
    # neighbour, which false-refuses "call me by your name release date".
    # Nothing here widens that defect: the film title says `your`.
    re.compile(r"\bmy (?:name|first name|last name|surname|full name|"
               r"nickname|birthday|date of birth|address|postcode|zip code|"
               r"phone number|age)\b"),
    re.compile(r"^who am i\b"),
    re.compile(r"^where do i live\b"),
)


def _self_referential(query: str) -> str | None:
    """`"about_me"`, `"about_you"`, or `None` if this may leave the machine."""
    q = " ".join(query.strip().rstrip(".?!").lower().split())
    if any(s.search(q) for s in _ABOUT_ME):
        return "about_me"
    if any(s.search(q) for s in _ABOUT_YOU):
        return "about_you"
    return None


def record_refusal(utterance: str) -> dict | None:
    """The backstop run on what the *person* said, not on what he wrote.

    **The query is not the only string that can leave, and on the seeded
    runtime it is not even the one that carries the question.** `harness/
    routegrid.py`'s Grid R, read 2026-09-06 on a live server: "read me my
    texts", "any new messages", "check my inbox" and "who called me
    yesterday" all reached Wikipedia -- and the query that went out was
    `what day is it`, the seed turn's own user line, walked into a freely
    generated `web_search.query`. `_self_referential` read that query, found
    nothing private in it, and let it go. The private question was in the
    utterance the whole time.

    So the live wrapper in `harness/server.py` asks this about the utterance
    before the provider is constructed, in front of the query-side gate and
    behind the packs -- behind them because "what's my name" is `about_you`
    by every row above and is answered out of `packs/about-me.md`, and a
    gate in front of the packs would refuse the one question that has a
    local home. Same rows, same refusals, same `reason`, so a client and the
    session log cannot tell the two gates apart, which is right: what was
    refused is the same thing either way.
    """
    side = _self_referential(utterance or "")
    if side is None:
        return None
    return {"ok": False, "reason": "self_referential", "say": SELF_SAYS[side]}


def _one_sentence(text: str) -> str:
    for stop in (". ", "? ", "! "):
        i = text.find(stop)
        if i >= _MIN_SENTENCE:
            return text[: i + 1].strip()
    return text


# **A snippet that opens with a question is a page title glued to its
# description, and the title is not the answer.** Search engines build the
# snippet out of whatever the page put in its `<title>` and `<meta
# description>`, and an SEO-shaped page titles itself with the question it
# claims to answer -- so the extract arrives as
#
#     Who owns NVIDIA Corp? Discover NVIDIA's largest shareholders including...
#
# and the model, whose whole job here is to copy, copies the front of it. Handed
# exactly that snippet the 260M replied `who owns nvidia?` -- it asked the
# question back. The clause after the `?` is the part that was written to
# inform, so the question comes off and what follows is scored on its own
# merits. If that leaves nothing, `_answers` below rejects the whole thing.
#
# `[^.!?]*` keeps this to a *leading* question: a declarative sentence followed
# by a question later in the snippet is untouched, because the first sentence is
# then the one being kept anyway.
_LEAD_QUESTION = re.compile(r"^[^.!?]{0,120}\?\s+")


def _drop_lead_question(text: str) -> str:
    """The title question off the front of a snippet, leaving the description."""
    cut = _LEAD_QUESTION.sub("", text, count=1)
    return cut.strip() or text


# **The same failure as the question, in the imperative.** A page that ranks for
# "who won the last superbowl" writes its meta description as a promise --
#
#     Find out who won the last Super Bowl and all the previous ones from 1967.
#     Find out who owns Nvidia, including its founders and major shareholders.
#     Discover NVIDIA's largest shareholders including Vanguard and BlackRock.
#
# -- all three measured live, all three scoring a perfect 1.0 against
# `MIN_COVER` for the same reason a question does: the teaser is built out of
# the query's own words, so every content word is present and not one fact is.
# Two of four live queries ended here after the question guard went in, and the
# model read them back as though they answered.
#
# Anchored to the start and kept to openers that address the reader, so a
# sentence that merely contains one of these words is untouched. Stripping the
# opener the way `_drop_lead_question` does would not help: what follows it is
# the promise, not the answer.
# **And the same failure again as a title, which is what the `who won` rewrite
# surfaced.** Measured live 2026-08-29, immediately after `_REPHRASE` learned to
# ask `the winner of the 2026 super bowl`: the results page returned the real
# answer at rank 2 -- "The Seattle Seahawks defeated the New England Patriots
# Sunday to win the 2026 Super Bowl." -- and an index page's own title at rank 1:
#
#     Complete list of Super Bowl winners 1967- 2026.
#
# **Both score exactly 1.00.** The title contains `winners`, `2026`, `super` and
# `bowl`, which is every term the query asked about, because a list page is
# titled with the thing it lists. `_covers` cannot separate them and the tie
# goes to the engine's ordering, so the promise beat the fact and the model read
# out a table of contents. That is the teaser rejection wearing a noun phrase
# rather than an imperative, and it belongs here rather than in the tie-break:
# ranking is not the defect, and a rule that preferred rank 2 would be guessing.
#
# `_prose` does not catch it -- `of` is a stop word inside the first ten tokens,
# so the fragment reads as a sentence -- and it has no finite verb, which is the
# signal that would catch it in general and a larger claim than one measurement
# supports.
#
# **Anchored, so the prose that introduces a list survives.** "This is a list of
# the current U.S. Senators" and "Below is a list of..." are real sentences and
# are NQ dev's own shape; only a text that *opens* with the title is refused.
# Priced the way `_prose` was, over every sentence of every NQ dev passage
# (3,615 sentences, `_sentences`'s own cut, 2026-08-29): **0 refused (0.00%)**,
# and no overlap with the openers already here. The honest limit on that number:
# NQ dev is Wikipedia prose, which is the population this branch is least likely
# to fire on, so it bounds the false-positive cost and does not measure how much
# furniture the branch catches.
_TEASER = re.compile(
    r"^(?:find out|discover|learn|explore|read (?:on|more)|see (?:the|our|how|why|who)"
    r"|check out|here'?s? (?:everything|what|how|why)|here is everything"
    r"|everything you need to know"
    r"|(?:the )?(?:complete |full |official |ultimate )?list of)\b",
    re.I,
)


def _answers(text: str) -> bool:
    """Whether this sentence is capable of being an answer at all.

    **A question is never one, and this is the cheapest guard in the file.**
    "With Super Bowl 60 on the horizon, who won the super Bowl last year?"
    scores a perfect 1.0 against `MIN_COVER` -- every content word of "who won
    the last superbowl" is in it, because it *is* the question -- and then the
    model reads it out as though it were a fact. Three of the six saved
    sessions end in him asking the user back what the user just asked him.

    `_TEASER` is the same rejection wearing an imperative: "Find out who owns
    Nvidia, including its founders..." is a promise that the page will answer,
    which is not an answer, and it scores 1.0 for the same reason the question
    does.

    Rejects only on the snippet path. This file used to argue the abstract
    providers never needed it ("declarative by construction"); finding 79 then
    measured them serving four confident non-answers in eight questions, so the
    guess is settled -- but on the abstract path this gate *holds* rather than
    rejects (`HOLD_COVER`, `_lookup`), because the same finding's NQ pricing
    shows outright rejection there spends real answers.
    """
    text = text.strip()
    return bool(text) and not text.endswith("?") and not _TEASER.match(text)


# **Navigation furniture covers any query about the page's own subject, and
# that is why the coverage bar cannot reject it.** Session 11 (2026-08-29,
# reproduced live at the API the same day): pokemondb.net's snippet opens with
# the site's own chrome --
#
#     Pikachu #0024 Arbok #0026 Raichu Contents Info Base stats Evolution
#     chart Pokédex entries Moves learned Sprites Locations Language Pikachu
#     is an Electric type Pokémon introduced in Generation 1.
#
# -- and "Base stats" is *in the furniture*, so the candidate scored a perfect
# 1.0 against MIN_COVER for "pikachu's base stats" and the model read a
# navigation bar out loud. `_one_sentence` cannot cut it, because chrome
# carries no sentence punctuation: the "sentence" runs from the nav strip
# straight into the first real sentence of the page. Finding 72's shape one
# link further down -- the right page, the wrong text.
#
# What separates chrome from prose is function words. A real English sentence
# spends one of `_STOP`'s little words within its first few tokens, and a nav
# strip is content words glued end to end. Priced over every sentence of every
# NQ dev passage (3,615 real sentences, `_sentences`'s own cut, 2026-08-29):
# requiring a stop word inside the first ten tokens rejects the measured
# furniture and refuses 27 real sentences (0.75%). Nearly all of those are
# biography leads whose parenthetical -- "(/ ˈkwɪntoʊ /; born June 2, 1977)"
# -- pushes the verb out of the window, so parentheticals come off before the
# count and the rate falls to 17 of 3,615 (0.47%), which is mid-cut fragments
# and score lines: sentences this file would serve badly anyway. A text that
# runs out of tokens before the tenth is kept, because the measured furniture
# is long and the short no-stop strings in real prose are abbreviation cuts
# ("Doug Diemoz departed April 2017."), not chrome -- rejecting them tripled
# the false-positive rate and caught nothing new.
#
# "Skip to main content Sign in" chrome stays uncatchable by this signal --
# "to" and "in" are stop words -- and stays where it has always been: rejected
# by MIN_COVER unless the page's own words cover the query. And the gate is
# scoped to the snippet path for `_answers`'s own reason: the two abstract
# providers return prose written to be read on its own, and guarding the
# providers that have never served chrome would be guessing.
_PAREN = re.compile(r"\([^)]*\)|\[[^\]]*\]")
_PROSE_WINDOW = 10


def _prose(text: str) -> bool:
    """Whether this reads as a sentence rather than as page furniture."""
    words = re.findall(r"[a-z0-9']+", _PAREN.sub(" ", text).lower())
    return len(words) < _PROSE_WINDOW or any(
        w in _STOP for w in words[:_PROSE_WINDOW])


def _covers_exact(query: str, text: str) -> float:
    """`_covers` without the prefix rule -- the query's own words, or nothing.

    **The tie-break, and it exists because a lead sentence can cover a query it
    does not answer.** `_covers` matches on four characters so that
    "discoverer" finds "discovered", and the price of that looseness is that
    "the population of Iceland" scores a perfect 1.0 against a lead reading
    "the most sparsely *populated* country in Europe" -- which states no
    population at all. Both that lead and the sentence carrying the number
    cover fully, so coverage alone cannot separate them.

    Exact presence can: the sentence that answers a question about a property
    usually names the property, and the sentence that merely alludes to it
    inflects it into something else. Used only to order two candidates that
    already tie on `_covers`, so it never rejects anything on its own.
    """
    want = _terms(query)
    if not want:
        return 0.0
    have = set(re.findall(r"[a-z0-9]+", text.lower()))
    return sum(w in have for w in want) / len(want)


def _score(query: str, text: str) -> tuple[float, float]:
    """Coverage first, then the query's own words. Higher is better."""
    return _covers(query, text), _covers_exact(query, text)


def _sentences(text: str) -> list[str]:
    """The text as sentences, crudely, in order.

    Crude on purpose and for this file's usual reason: the alternative is a
    sentence tokenizer this module will not carry a dependency for. An
    abbreviation splits a sentence in two here, and the cost of that is a
    shorter candidate rather than a wrong one -- `_best_answer` scores whatever
    it is handed and a half-sentence that still contains the asked-for property
    still beats a lead that does not.
    """
    out: list[str] = []
    buf = " ".join(text.split())
    while buf:
        cut = -1
        for stop in (". ", "? ", "! "):
            i = buf.find(stop)
            if i >= _MIN_SENTENCE and (cut < 0 or i < cut):
                cut = i
        if cut < 0:
            out.append(buf.strip())
            break
        out.append(buf[: cut + 1].strip())
        buf = buf[cut + 2 :]
    return [s for s in out if s]


def _best_answer(query: str, text: str, limit: int = MAX_ANSWER) -> str:
    """The part of the provider's text that answers, not the part that is first.

    **This is WS-A1's `8/24` measured and fixed.** That probe instrumented the
    reduction and found the provider returned answer-bearing text 22 times in
    24 while only 14 reached the model: the eight losses were every case where
    the asked-for property is a fact further down the article rather than part
    of the lead's introduction of the entity -- melting point of iron, length
    of the Nile, population of Iceland, discoverer of penicillin. A lead
    sentence introduces; it does not answer arbitrary questions about what it
    introduces.

    `_first_sentence` keeps the head of the text and asks nothing about the
    query, so which 400 characters survive is decided by the provider's
    paragraph order. This keeps the head **whenever the head already covers the
    query**, and otherwise keeps the best-covering sentence instead.

    **Conservative by construction, and that is the point.** `MIN_COVER` is the
    same bar `_ddg_html` accepts a snippet at, so every lookup that worked
    before -- the capitals, the currencies, the official languages, all of
    which state the property in the lead -- takes the first branch and returns
    byte-identically. Only a query the head fails to cover can reach the
    search, and a candidate has to score *strictly higher* than the head to
    displace it, so a tie leaves the lead in place.

    **`PASSAGE` is untouched.** `_flat(text)` still carries the provider's whole
    response forward, so the extraction path reads exactly what it read before
    and this changes only what gets *said* when nothing extracts. The two fixes
    are independent: this one needs no model capability and works with
    `--extract` off, which is the default.
    """
    head = _first_sentence(text, limit)
    best, best_score = head, _score(query, head)
    # A head that covers the query on the query's own words is already the
    # answer and nothing below can beat it, so the common case does no work.
    if best_score >= (MIN_COVER, MIN_COVER):
        return head
    for s in _sentences(text):
        if not _answers(s):
            continue
        score = _score(query, s)
        if score > best_score:
            best, best_score = s, score
    return _first_sentence(best, limit)


def _ddg(query: str, get, pages=None) -> tuple[str, str, str] | None:
    r = get(DDG, params={"q": query, "format": "json", "no_html": 1,
                         "skip_disambig": 1}, timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT})
    _refused(r, "DuckDuckGo")
    r.raise_for_status()
    data = r.json()
    text = (data.get("AbstractText") or "").strip()
    if not text:
        return None
    source = (data.get("AbstractSource") or "DuckDuckGo").strip()
    # The abstract is the topic's own lead and the query named the topic --
    # the same trust the `_wiki`-by-title path stores under. Measured live
    # 2026-08-27: this provider answers entity-shaped queries before the wiki
    # path ever runs, so without this line the store misses the one sequence
    # it was designed for (an entity lookup, then property questions).
    _remember_page(query.strip(), _flat(text), source, pages)
    # A coverage gate was tried here on 2026-08-26 and reverted the same
    # hour: it caught "who discovered penicillin" being answered with a
    # window about which moulds *produce* it, and it also refused "Iron
    # melts at 1538" for a melting-point query because the sentence lacks
    # the word "point" -- undoing WS-A1's measured repair. The abstract's
    # selection rules belong to `_best_answer` and its findings; the
    # mould case is recorded there as an open reduction defect, not
    # patched here by taste.
    return _best_answer(query, text), source, _flat(text)


WIKI_API = "https://en.wikipedia.org/w/api.php"


def _wiki_search(query: str, get, pages=None,
                 deep: bool = False) -> tuple[str, str, str] | None:
    """Wikipedia by *search* rather than by title, which is most of the gap.

    `_wiki` answers only when the query happens to be a page title --
    "Marie Curie" hits, "the boiling point of water" misses, and everything
    that missed fell through to the one provider that rate-limits. MediaWiki's
    search API is keyless, stable at polite rates, and returns ranked titles;
    the best title's summary then goes through the same `_wiki` path, so the
    answer machinery is one implementation.

    **The coverage bar applies here exactly as it does to snippets.** A
    search engine returning its best page for a query is on-topic by
    construction and answering by accident, which is the distinction
    `MIN_COVER`'s comment prices -- so a summary whose text does not cover
    the query's own terms is a miss, not an answer.
    """
    r = get(WIKI_API, params={"action": "query", "list": "search",
                              "srsearch": query, "srlimit": MAX_RESULTS,
                              "format": "json"},
            timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
    _refused(r, "Wikipedia")
    if 400 <= r.status_code < 500:
        return None
    r.raise_for_status()
    try:
        found = (r.json().get("query") or {}).get("search") or []
    except ValueError:
        return None
    titles = [(row.get("title") or "").strip() for row in found[:MAX_RESULTS]
              if isinstance(row, dict) and (row.get("title") or "").strip()]
    # **The engine's own order, with mixed titles moved to the back.** The
    # first version sorted by shared-term count, written for "the boiling
    # point of water" ranking High-altitude cooking first -- and measured
    # live 2026-08-27 it inverts the common case: for "the capital of
    # Mongolia" it promoted Capital punishment in Mongolia (two shared
    # terms) over the engine's own first result, Ulaanbaatar (none), whose
    # lead is the answer. Probed against the live API on the four queries
    # in `scripts/check_search.py`'s 3b block, the engine's first result
    # was the right page all four times, and the shared-term sort was the
    # only reason two of them answered with capital punishment.
    #
    # What actually separates the wrong pages is not missing query words
    # but *extra* ones: a title mixing the query's own terms with content
    # words the query never said (Capital punishment in Mongolia, Economy
    # of Iceland, List of capitals of France) names a compound subject
    # that merely contains the asked-about words. The page that answers is
    # titled either by the query's words alone (Mongolia, Boiling point)
    # or by the answer itself (Ulaanbaatar, Paris, Icelandic krona), and
    # both of those shapes are left in the engine's order. Demoted rather
    # than dropped, so a mixed title still answers when nothing cleaner
    # does; the High-altitude cooking case needs no sort at all now, since
    # the lead-sentence gate below rejects a lead that does not cover.
    q_terms = set(_terms(query))

    def _mixed(title: str) -> bool:
        t_terms = set(_terms(title))
        return bool(t_terms & q_terms) and bool(t_terms - q_terms)

    titles.sort(key=_mixed)
    for title in titles:
        hit = _wiki(title, get, pages)
        if hit is None:
            continue
        _, source, flat = hit
        # **Only the page's lead sentence may answer, and only when it
        # covers the query.** Two failures taught this in one probe: gating
        # the whole extract let the Penicillin article answer "who
        # discovered penicillin" off "have been discovered" three sentences
        # deep, and gating `_best_answer`'s window handed over mush --
        # "chrysogenum and P. rubens." -- that `_one_sentence` could not cut
        # clean. The lead sentence is the page's own definition of its
        # subject; a page whose lead covers the query is the page that *is*
        # the answer, and any other page falls through to a provider whose
        # snippet passes, which was the old behaviour and never worse. The
        # full extract still rides as the passage, so `--extract` can dig
        # past the lead exactly as it does for a snippet's page.
        lead = _one_sentence(_first_sentence(flat))
        if _answers(lead) and _covers(query, lead) >= MIN_COVER:
            return lead, source, flat
    return _subject_page(query, titles, get, pages) if deep else None


def _subject_page(query: str, titles: list[str], get,
                  pages=None) -> tuple[str, str, str] | None:
    """The page the question *named*, served for its passage rather than its lead.

    **Only when somebody is going to read it** -- `deep` is set by the server
    exactly when `--extract` wired a reader, and the comment on `MIN_COVER` is
    why: a lead that does not mention what was asked about is not an answer,
    and serving one would be the Everest failure that bar exists to refuse.
    What changes with a reader in the loop is not the bar on *speech* but the
    bar on *fetching*, and those had been one test.

    **The rule is the title, and it is the `_mixed` comment's first shape
    stated as a condition.** That comment says the page that answers is titled
    either by the query's own words alone -- Mongolia, Boiling point -- or by
    the answer itself -- Ulaanbaatar, Icelandic krona. The second cannot be
    recognised without knowing the answer, which is what the lead-coverage
    test is for. The first can: **every content term of the title is a term
    the query used.** "Eiffel Tower" against "when was the eiffel tower
    built", "Mount Kilimanjaro" against "how tall is mount kilimanjaro".

    **Priced offline on NQ dev, 721 answerable items, where each item's own
    page title is ground truth**: the rule fires on the right page for
    **244 of 721 (33.8%)**, and on a randomly drawn *other* item's title
    **1 time in 3,601 (0.03%)** -- a title made only of the query's own words
    is almost never a different subject. Live on 24 ordinary questions it
    newly served three the lead-coverage test rejected (Eiffel Tower,
    Hitchhiker's Guide, Kilimanjaro), each of whose extract holds the answer,
    and correctly served nothing for "the melting point of iron", whose
    candidate titles -- Newton scale, Melting-point apparatus, Allotropes of
    iron -- all carry words the query never said.

    The lead still comes back as the payload's `answer`, because the payload
    has one shape and this is not the place to invent a fifth. What marks it
    is `LEAD_ANSWERS`, set by `_lookup`, which the model never sees and
    `corn/agent.py` reads when extraction comes back empty.
    """
    q_terms = set(_terms(query))
    if not q_terms:
        return None
    for title in titles:
        t_terms = set(_terms(title))
        if not t_terms or not t_terms <= q_terms:
            continue
        hit = _wiki(title, get, pages)
        if hit is None:
            continue
        _, source, flat = hit
        lead = _one_sentence(_first_sentence(flat))
        if _answers(lead):
            return lead, source, flat
    return None


def _wiki(query: str, get, pages=None) -> tuple[str, str, str] | None:
    r = get(WIKI + requests.utils.quote(query.strip().replace(" ", "_")),
            timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
    # 404 is "no such page", which is a miss and not a failure. Anything else
    # in the 4xx range is this client being wrong about how to ask -- a bad
    # title, a malformed request -- and is also a miss from the user's side: the
    # provider answered, it just had nothing for us. Only a raise counts as not
    # having looked.
    #
    # **403 and 429 are the exception and `_refused` takes them first.** This
    # comment used to name "a rejected agent" among the client's own mistakes,
    # and it is one -- but it is a mistake the operator can fix, and folding it
    # into the miss branch is what made an unset `USER_AGENT` look like a
    # Wikipedia with nothing to say. A provider declining to serve this machine
    # is not a fact about the query.
    _refused(r, "Wikipedia")
    if 400 <= r.status_code < 500:
        return None
    r.raise_for_status()
    data = r.json()
    text = (data.get("extract") or "").strip()
    if not text:
        return None
    flat = _flat(text)
    # Remembered even when the caller goes on to refuse the page: the fetch
    # already happened, and the page store's whole argument is not paying for
    # it twice.
    _remember_page(query.strip(), flat, "Wikipedia", pages)
    return _best_answer(query, text), "Wikipedia", flat

# Footnote markers survive Wikipedia-derived snippets -- "Vientiane[a] is the
# capital" -- and this reply is spoken. `[a]`, `[12]`, `[citation needed]`.
_REF = re.compile(r"\[(?:\d+|[a-z]|citation needed)\]", re.I)

# How far down the ranking to look -- snippets on the results page, titles on
# the wiki search. Ten come back; past the first few the results are the
# query's *words* rather than its subject, and a snippet that merely repeats
# the terms is what `MIN_COVER` exists to reject anyway. Five rather than
# three on the title path because the subject page can sit under the compound
# pages the demotion above exists for: Paris is the engine's *fourth* result
# for "the capital of France", behind three mixed titles.
MAX_RESULTS = 5

# **All of them, and the strictness is the point.** Two thirds was the first
# setting and it let Britannica's "Mount Everest, mountain on the crest of the
# Great Himalayas..." answer a question about its *height*: `mount` and
# `everest` carried it and the word actually being asked about was missing.
# On-topic is not the same as answering, and the gap between them is where the
# 260M invents -- handed a snippet like that it said "It is 1,890 metres (5,000
# ft) above sea level".
#
# The cost is real and it is the right way round: more queries come back
# `no_results`, which is a trained shape he says perfectly and a true statement
# about what this backend found. Lower it and he answers more questions and
# some of the answers are made up.
MIN_COVER = 1.0

# **The abstract path's line, and it holds rather than rejects.** Finding 79
# measured the abstract providers serving four confident non-answers in eight
# questions with no bar at all; pricing the snippet bar there over NQ dev
# (1,003 rows, 2026-08-31) showed why one was never installed: abstract prose
# answers questions without echoing them, and `MIN_COVER` would spend **528 of
# 620 true answers** to refuse 341 of 383 non-answers -- "The United States
# Senate consists of 100 members" fails it for "how many senators are there".
# The 2026-08-26 reversion in `_ddg` was this same fact met live.
#
# So the abstract path never discards: a pick that fails `_answers` or covers
# no more than this is *held* while the barred providers behind get their
# chance, and served untouched when nothing clears -- see `_lookup`. At 0.5,
# NQ dev prices the hold at 212 of 620 true answers held-and-still-served
# (the extra-fetch cost) against 112 of 282 unanswerable picks getting a
# second chance; finding 79's three scored non-answers sat at 0.50, 0.50 and
# 0.25, which is why the line is "half or less" and the comparison is `<=`.
HOLD_COVER = 0.5

# Words carrying no subject. Dropped before scoring so "the length of the
# Mekong" is scored on `length` and `mekong` rather than diluted to a third by
# `the` and `of`, which every snippet on the internet contains.
_STOP = frozenset((
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do", "does", "for",
    "from", "how", "in", "is", "it", "its", "of", "on", "or", "that", "the",
    "to", "was", "were", "what", "when", "where", "which", "who", "whom",
    "whose", "why", "with",
))


def _clean(text: str) -> str:
    """Snippet text as something sayable: no footnote markers, no stray gaps."""
    text = _REF.sub("", text)
    # `get_text(" ")` joins nodes with a space and `_REF` leaves a gap behind
    # the marker it removed, so "Laos[a]." arrives as "Laos ." -- which is a
    # stray space the model would read out as a pause.
    return re.sub(r"\s+([.,;:!?])", lambda m: m.group(1), text).strip()


def _terms(query: str) -> list[str]:
    """What the query is actually asking about, as words a snippet can contain.

    **A one-letter word can never match, and `MIN_COVER` is 1.0, so a query
    containing one could never be answered at all.** "who owns space x" tokenises
    to `owns`, `space`, `x`; the web writes the company as `SpaceX`, one word,
    and `x` matches neither it nor anything else -- the prefix rule needs four
    characters and has one. Coverage tops out at 2/3, every snippet is rejected,
    and the user is told nothing was found about a company with a Wikipedia
    article. That is the failure in the sixth saved session.

    So a single character is glued to the term in front of it rather than
    dropped, which is how the query was meant in the first place: `space x`
    becomes `spacex`, and the prefix rule then matches a page writing it either
    way round. Dropping it was the other option and it is looser -- it would
    score "vitamin c" on `vitamin` alone and accept a snippet about vitamin D.

    Stop words come off first so gluing follows the words that carry the
    subject; a lone character with nothing in front of it has nothing to join
    and is dropped.
    """
    out: list[str] = []
    for w in re.findall(r"[a-z0-9]+", query.lower()):
        if w in _STOP:
            continue
        if len(w) == 1:
            if out:
                out[-1] += w
            continue
        out.append(w)
    return out


def _covers(query: str, text: str) -> float:
    """How much of what was asked about this snippet actually mentions.

    Prefix matching rather than equality, because the snippet inflects what the
    query does not -- "discoverer" against "discovered", "length" against
    "lengths". Crude, and the alternative is a stemmer this file will not carry
    a dependency for.
    """
    want = _terms(query)
    if not want:
        return 0.0
    # **A one-character token on this side is never evidence, and before this it
    # was a wildcard.** `_terms` glues a lone character onto the term in front
    # of it, so no *want* term is ever shorter than two characters -- which
    # means a one-character *have* token can never legitimately match one, and
    # `w.startswith(h[:4])` with `h` one character long degenerates to "same
    # first letter". English writes those constantly: the possessive `s` of
    # "Warhol's", the article `a`. Live 2026-08-29, `what does DNA stand for`
    # scored a perfect 1.00 against "DNA profiling is the process of
    # determining an individual's ... characteristics" -- `stand` was matched
    # by the `s` of "individual's" -- and any query term beginning with `a` was
    # effectively free.
    #
    # **Priced over NQ dev, and it is not free.** 721 answerable items, 2,581
    # question/sentence pairs, 89 of which clear `MIN_COVER` today: **23 stop
    # clearing it (25.8%), and 12 of those carry the gold answer.** Every one of
    # the 23 was passing on a first-letter coincidence -- `author` matched by
    # `a`, `sang` by `s`, `meninges` by `m` -- so the twelve were answer-bearing
    # sentences that do not mention what was asked about, which is the exact
    # text the Everest comment below refuses to serve. Losing them is the bar
    # doing its job; keeping them was luck, and a quarter of everything that
    # cleared the bar was clearing it partly on this.
    #
    # Dropped rather than glued the way `_terms` glues. Gluing is the symmetric
    # choice and was measured too -- `_terms` on both sides rejects 3 more, and
    # it bundles stop-word removal on this side, which nothing here motivates.
    # `_covers_exact` needs none of this: it tests membership, so a
    # one-character token can only match a one-character term and there are
    # none.
    have = [h for h in re.findall(r"[a-z0-9]+", text.lower()) if len(h) > 1]
    # Four characters rather than five, because the inflections that matter
    # here are short: `melting` against `melts` shares only `melt`, and a
    # melting-point query that rejected every snippet saying "melts at" would
    # fail the strictness above into uselessness.
    hits = sum(any(h.startswith(w[:4]) or w.startswith(h[:4]) for h in have)
               for w in want)
    return hits / len(want)


def _result_host(result) -> str:
    """The hostname a DDG result links to, or "". One implementation, because
    the avoid check and the spoken source have to agree about what a result's
    source *is* -- two readings of the same href is how a skipped site gets
    named anyway."""
    link = result.select_one(".result__a")
    if link is None:
        return ""
    href = link.get("href") or ""
    m = re.search(r"uddg=([^&]+)", href)
    target = requests.utils.unquote(m.group(1)) if m else href
    host = re.sub(r"^(?:https?:)?//", "", target).split("/")[0]
    return host[4:] if host.startswith("www.") else host


def _ddg_html(query: str, get,
              avoid: tuple[str, ...] = ()) -> tuple[str, str, str] | None:
    """General web results, for the queries the Instant Answer box has nothing for.

    `_ddg` answers entities and is empty for the rest -- "capital of Laos" and
    "boiling point of water" both return a zero-length abstract, which is two
    of the five queries anyone would actually try. This is the same provider's
    HTML endpoint, which returns ten ranked results with a snippet each, and
    the snippet is already the reduction this file exists to perform.

    **The snippet, not the page.** Fetching the winning URL and running the
    body text through `_first_sentence` was the other option and it returns
    site chrome -- "Skip to main content Sign in" -- because the first sentence
    of a page is not the answer to anything. The snippet is the search
    engine's own extract, which is the same class of object as `AbstractText`
    and `extract` above, and that is what keeps all three providers on one
    contract.
    """
    r = get(DDG_HTML, params={"q": query}, timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT})
    _refused(r, "DuckDuckGo")
    if 400 <= r.status_code < 500:
        return None
    r.raise_for_status()
    if r.status_code == 202 or _CHALLENGE in r.text:
        raise _Blocked("DuckDuckGo", "challenge", "202 or human-check page")
    soup = BeautifulSoup(r.text, "html.parser")

    best, best_whole, best_score, best_i = None, "", 0, 0
    results = soup.select(".result")
    # The whole page when avoiding, the usual five otherwise. A second source
    # is by definition deeper in the ranking than the first one was -- the
    # page that answered "boiling point of water" held its second source at
    # index 5, one past the cap, and the recheck read as a miss with the
    # answer in hand. `MIN_COVER` stays the quality gate either way, so depth
    # buys candidates and never lowers the bar; first-answer behaviour is
    # byte-identical because the limit only moves when `avoid` is non-empty.
    limit = len(results) if avoid else MAX_RESULTS
    for i, result in enumerate(results[:limit]):
        node = result.select_one(".result__snippet")
        if node is None:
            continue
        # The second-source path: a host already heard from is skipped *per
        # result*, not per provider, because the next-best result is usually
        # where the second source actually lives. Empty on every ordinary
        # call.
        if avoid:
            host = _result_host(result)
            if host and any(_same_source(host, a) for a in avoid):
                continue
        text = _clean(node.get_text(" ", strip=True))
        if not text:
            continue
        # Before the reduction, so the sentence `_one_sentence` keeps is the
        # description rather than the title question. `_MIN_SENTENCE` is why it
        # cannot be left to that function: a short title -- "Who owns NVIDIA
        # Corp?" is 21 characters -- sits under the abbreviation floor, so the
        # cut is skipped and the question survives into the answer.
        text = _drop_lead_question(text)
        # The snippet before its own reduction, kept because a listing cut is
        # two or three sentences and the one that answers is not always the
        # first -- which is the whole premise of the extraction path. It is
        # *not* what gets scored: `_covers` has to hold against the sentence
        # actually handed over, or a snippet whose second half mentions the
        # subject would pass on a first half that does not.
        whole = text
        # **Reduced before it is scored, because the sentence handed over is
        # what has to answer.** Scoring the whole snippet and returning its
        # first sentence is how "It lies in the Mahalangur Himal sub-range"
        # got through a filter built to stop exactly it: the words `Everest`
        # and `height` were further along, in the half that never shipped.
        text = _one_sentence(text)
        # `continue` rather than a rejection of the whole page: the guard is per
        # candidate, so a declarative snippet further down the ranking still
        # wins. Rejecting outright would throw away the answer along with the
        # question that outranked it.
        if not _answers(text):
            continue
        # Chrome never ships, whatever it covers -- `_prose`'s argument. Per
        # candidate for the same reason as `_answers`: live 2026-08-29, the
        # rank-1 result behind the pokemondb furniture was a real covering
        # sentence from bulbapedia, and it should win rather than drown.
        if not _prose(text):
            continue
        score = _covers(query, text)
        # Strictly greater, so rank breaks a tie and the engine's own ordering
        # is what decides between two snippets that answer equally well.
        if score > best_score:
            best, best_whole, best_score, best_i = text, whole, score, i

    # **Nothing relevant is a miss, and that distinction is the point of this
    # block.** The first result for "the height of Mount Everest" was "It lies
    # in the Mahalangur Himal sub-range of the Himalayas", which contains no
    # height; handed it, the model said *"It is 1,890 metres (5,000 ft) above
    # sea level"* -- a number that appears in neither the snippet nor reality.
    # That is the failure VISION §9 names as the most important one, and it is
    # reached by handing him plausible text that does not answer the question.
    # An honest `no_results` is the trained shape for this, and he says it
    # perfectly. So the bar is that the snippet actually mentions what was
    # asked about, and falling short of it returns nothing rather than prose.
    if best is None or best_score < MIN_COVER:
        return None

    source = (_result_host(results[best_i]) if results else "") or "the web"
    return _first_sentence(best), source, _flat(best_whole)


def _same_source(a: str, b: str) -> bool:
    """Whether two source strings name the same place, loosely and on purpose.

    The wiki provider says "Wikipedia", the instant-answer provider says
    whatever `AbstractSource` says (routinely also Wikipedia), and the HTML
    provider says a hostname -- so "en.wikipedia.org" and "Wikipedia" must
    read as one source or a "second source" would be the first one twice.
    Flattened containment either way is the loosest rule that stays honest.
    """
    fa = re.sub(r"[^a-z0-9]", "", a.lower())
    fb = re.sub(r"[^a-z0-9]", "", b.lower())
    return bool(fa) and bool(fb) and (fa in fb or fb in fa)


# **The page cache, and the manners it enforces.** Most of one day's
# rate-limiting was this backend asking the same endpoint the same question
# within a minute: the recheck re-fetches a results page served sixty seconds
# earlier, and the second source it wants is *on that page*. So the default
# `get` remembers recent 200s for a few minutes, and puts a floor between
# consecutive real fetches of the results endpoint -- being slightly slow in a
# burst beats being told "no results" by an annoyed engine, because the second
# of those is false. Guards inject their own `get` and never touch any of
# this; a cached reply is only ever one the same process was already handed.
_CACHE: dict[tuple[str, str], tuple[float, object]] = {}
_CACHE_TTL = 600.0
_CACHE_MAX = 64
_HTML_GAP = 2.0
_last_html_fetch = 0.0


def _polite_get(url, **kw):
    global _last_html_fetch
    key = (url, str(kw.get("params")))
    now = time.monotonic()
    kept = _CACHE.get(key)
    if kept is not None and now - kept[0] < _CACHE_TTL:
        return kept[1]
    if url == DDG_HTML:
        wait = _HTML_GAP - (now - _last_html_fetch)
        if wait > 0:
            time.sleep(wait)
        _last_html_fetch = time.monotonic()
    r = requests.get(url, **kw)
    if r.status_code == 200:
        while len(_CACHE) >= _CACHE_MAX:
            _CACHE.pop(next(iter(_CACHE)))
        _CACHE[key] = (now, r)
    return r


# **The page store, one level above the GET cache.** `_polite_get` remembers
# URLs, so only the *same* request is ever free -- but most of what a session
# asks next is about an entity it already fetched: one Wikipedia extract for
# Mongolia holds the capital, the currency and the language, and three
# property queries were three search-API calls plus three page fetches. The
# store keeps the flat extract of every wiki page this process fetched, keyed
# by the page's actual title, and lets it answer a *new* question -- under two
# gates, both borrowed rather than invented:
#
#   * **the query must name the page**: every content term of the title
#     appears among the query's terms. That is the `_wiki`-by-title trust
#     argument -- a user asking "the currency of Mongolia" has named the
#     Mongolia page the way "Marie Curie" names hers -- and it is what keeps
#     the Ulaanbaatar page from answering questions about Iceland.
#   * **the sentence must pass the live gates**: `_answers` and
#     `_covers >= MIN_COVER` on `_best_answer`'s pick, exactly the bar a
#     fetched page's text has to clear.
#
# Guards inject their own `get` and their own `pages` and never touch the
# module store, the `_CACHE` rule applied again. TTL and size are registered
# defaults, not tuned ones.
_PAGES: dict[str, tuple[float, str]] = {}
_PAGES_TTL = 3600.0
_PAGES_MAX = 16


def _remember_page(title: str, flat: str, source: str, pages) -> None:
    if pages is None or not title or not flat:
        return
    while len(pages) >= _PAGES_MAX and title not in pages:
        pages.pop(next(iter(pages)))
    pages[title] = (time.monotonic(), flat, source)


def _page_answer(query: str, pages) -> tuple[str, str, str] | None:
    """An answer from a page already fetched, or None -- never a fetch."""
    if not pages:
        return None
    now = time.monotonic()
    for title in [t for t, kept in pages.items()
                  if now - kept[0] >= _PAGES_TTL]:
        del pages[title]
    q_terms = set(_terms(query))
    # Most recent first: the page just fetched is the one the conversation is
    # about, and a stale namesake behind it should not shadow it.
    for title, (_, flat, source) in reversed(list(pages.items())):
        t_terms = set(_terms(title))
        if not t_terms or not t_terms <= q_terms:
            continue
        answer = _best_answer(query, flat)
        if _answers(answer) and _covers(query, answer) >= MIN_COVER:
            return answer, source, flat
    return None


# What the backstop says, by which side of it the query fell on. Two sentences
# rather than one because the two refusals are not the same refusal: a question
# about him has an answer he can give directly, and a question about the user's
# own record has no answer on the web at all. Both are read out verbatim by
# `corn.agent.deferred_say`, which is the path every other `{ok, reason, say}`
# payload in this file already takes.
SELF_SAYS = {
    "about_me": "That's a question about me rather than something to look up. "
                "Ask me straight and I'll tell you what I actually am.",
    "about_you": "That's about your own record, and it isn't on the web. "
                 "I'd only have been guessing.",
}


# What he says when a provider declines, by whether anyone else looked. Two
# sentences for the reason `SELF_SAYS` has two: they are refusals of different
# sizes, and one sentence covering both would have to be vague about which,
# which is the vagueness this slug exists to remove. Both name the host,
# because "wait and try again" is only actionable if the user knows what is
# doing the refusing, and neither promises a retry this file does not perform.
BLOCKED_SAYS = {
    "none": "{provider}'s blocking my searches right now, so I couldn't look. "
            "Worth another go in a minute.",
    "partial": "{provider}'s blocking my searches, so I only had part of the "
               "web to go on, and it wasn't in the rest.",
}


def _lookup(q: str, get, avoid: tuple[str, ...], pages,
            deep: bool = False) -> tuple[dict | None, dict | None, bool,
                                         _Blocked | None]:
    """One pass over the providers: `(payload, held, reached, blocked)`.

    Split out of `web_search` so the reformulation retry is the same pass run
    twice rather than a second copy of it -- see `_rephrased`. `reached` comes
    back separately because "nobody looked" and "nothing was found" are
    different answers and the caller has to keep them apart across both passes.

    `held` is a suspected non-answer from the abstract path -- see the hold
    below -- returned separately rather than served, so the caller can give
    the reformulation retry its chance first and still have the floor to
    stand on. Nothing is ever discarded: a pass that produces only a `held`
    is a pass whose answer the caller *will* serve if nothing beats it.

    `blocked` is the first provider that declined, carried out for the same
    reason `reached` is: it is a fact about the pass that no single provider's
    return value can express, and the caller has to keep it across both passes
    to say anything true about an empty-handed turn.
    """
    kept = _page_answer(q, pages)
    if kept is not None and not any(_same_source(kept[1], seen)
                                    for seen in avoid):
        answer, source, passage = kept
        payload = {"answer": answer, "source": source, "query": q,
                   LEAD_ANSWERS: _covers(q, answer) >= MIN_COVER}
        if passage:
            payload[PASSAGE] = passage
        return payload, None, True, None

    reached = False
    held: dict | None = None
    blocked: _Blocked | None = None
    for provider in (_ddg, _wiki, _wiki_search, _ddg_html):
        # Deliberately broad, and deliberately *inside* the loop. Every way a
        # network call fails -- timeout, DNS, TLS, a provider returning HTML
        # where JSON was promised -- is the same fact from the user's side, and
        # a turn must end in something speakable rather than in a traceback
        # that reaches nobody. But one provider failing is not the internet
        # being gone: catching the whole loop at once meant a single broken
        # provider silenced the two working ones behind it, which is exactly
        # how a `TypeError` in a third provider turned every query in this
        # backend into "I couldn't reach the internet".
        try:
            if provider is _ddg_html:
                hit = provider(q, get, avoid)
            elif provider is _wiki_search:
                hit = provider(q, get, pages, deep)
            else:
                hit = provider(q, get, pages)
        except _Blocked as refusal:
            # **A refusal is neither of the two things the loop already counts.**
            # It is not the provider being unreachable -- it answered -- and it
            # is not a miss, because nothing was searched. Kept rather than
            # re-raised, on the argument the broad `except` below already makes
            # for a broken provider: one host saying no is not the search being
            # over, and the two behind it still get their turn.
            #
            # First refusal kept, matching `held` a few lines down: the
            # providers are ordered by how much their text is trusted, so the
            # earliest one to decline is the most expensive one to have lost,
            # and it is the one worth naming out loud.
            blocked = blocked or refusal
            continue
        except Exception:
            continue
        reached = True
        if hit is not None:
            answer, source, passage = hit
            if any(_same_source(source, seen) for seen in avoid):
                continue
            payload = {"answer": answer, "source": source, "query": q}
            # Whether the sentence being served mentions what was asked. True
            # for every provider that cleared `MIN_COVER` to get here, and
            # False only for `_subject_page`, which is served for its passage.
            # Marked on every payload rather than only the false ones, so a
            # reader of a session log never has to infer it from an absence.
            payload[LEAD_ANSWERS] = _covers(q, answer) >= MIN_COVER
            # **Attached whenever there is text, and the trigger used to be
            # narrower.** It was `passage != answer` -- attach only when the
            # reduction actually discarded something -- on the argument that
            # an abstract arriving whole under `MAX_ANSWER` has nothing
            # behind it to go looking for, and that reading it would spend a
            # decode budget reproducing a string the model already has.
            #
            # **That tested whether text was discarded, not whether the
            # served sentence answers the question, and the two come apart.**
            # Measured on `evals/results/retrieval.json`: 3 of 16 served rows
            # carried no passage, and one of them is
            # "when was the eiffel tower built" answered with 160 characters
            # of lattice-tower prose truncated at "designed and b--", the
            # date sitting just past the cut. The reader never ran, and the
            # model was asked to extract in one shot, which is the failure
            # WS-B-alt exists to prevent, through the one door left open.
            #
            # **And the cost argument has expired.** It was written when
            # every attached passage meant a decode per window; with
            # `extract_gate` on, a window with nothing in it costs one
            # forward and is never decoded (`corn/gate.py`). So the reduction
            # is still the floor -- `corn/agent.py` only replaces it with a
            # grounded span -- and the worst this can now do is spend a few
            # forwards to leave the turn where it was.
            if passage:
                payload[PASSAGE] = passage
            # **The hold, and it is the abstract path's whole bar.** The two
            # abstract providers have no gate of their own -- `HOLD_COVER`'s
            # comment prices why a rejecting one cannot be installed -- so a
            # pick that reads as a question or covers half the query or less
            # is *suspected*, not refused: kept as the floor while the barred
            # providers behind get their chance. First suspect kept, because
            # the providers are ordered by how much their text is trusted.
            if provider in (_ddg, _wiki) and (
                    not _answers(answer)
                    or _covers(q, answer) <= HOLD_COVER):
                held = held or payload
                continue
            return payload, held, True, blocked
    return None, held, reached, blocked


# **A sum is not a search.** "whats 17 times 23" routes to `web_search` --
# correctly, from the model's side: the corpus has no calculator and a question
# with an answer he does not hold is exactly what the tool is for. What the tool
# did with it (2026-09-05, live) was ask Wikipedia, get rate-limited, and tell
# the user "it wasn't in the rest". The answer never left the machine because it
# was never on the web; it was in the query. So the backend works it out here,
# before any provider is constructed, in the same `{answer, source, query}`
# envelope every hit already wears -- no weight learns a new shape, and the
# model copies "17 times 23 is 391." exactly as it copies a capital.
#
# **Narrow on purpose.** Everything after the question words have to be an
# expression -- digits, the operators, and the handful of words below that
# name one -- and it has to hold two numbers and an operator, so "what is
# 1984" stays a search for the year and "population over 1000" is not a
# division. `ast` is the parser, restricted to arithmetic nodes; nothing here
# calls `eval`. `_ARITH_WORDS` is ordered longest-first so "divided by" is not
# read as "by" after "divided" has been left standing.
_ARITH_OPENERS = re.compile(
    r"^(?:(?:what'?s|whats|what is|what does|how much is|how many is|"
    r"calculate|compute|work out|solve|tell me|please|can you|could you|"
    r"equals?|is)\s+)+", re.IGNORECASE)
_ARITH_WORDS = (
    (re.compile(r"\bmultiplied by\b|\btimes\b"), "*"),
    (re.compile(r"\bdivided by\b|\bover\b"), "/"),
    (re.compile(r"\bto the power of\b|\bpower\b|\^"), "**"),
    (re.compile(r"\bplus\b|\badd(?:ed to)?\b"), "+"),
    (re.compile(r"\bminus\b|\bsubtract(?:ed from)?\b|\btake away\b|\bless\b"),
     "-"),
    (re.compile(r"\bpercent of\b|% of\b"), "/100*"),
    (re.compile(r"\bsquared\b"), "**2"),
    (re.compile(r"\bcubed\b"), "**3"),
    (re.compile(r"\bmod(?:ulo)?\b"), "%"),
    (re.compile(r"(?<=[\d)])\s*x\s*(?=[\d(])"), "*"),
    (re.compile(r"(?<=\d),(?=\d{3}\b)"), ""),
    (re.compile(r"\bequals?\b|=|\bmake\b|\bgive\b|\bcome to\b"), ""),
)
_ARITH_ONLY = re.compile(r"^[\d\s.+\-*/()%]+$")
_ARITH_LIMIT = 10 ** 15


def _arithmetic(query: str) -> str | None:
    """The spoken answer to a sum, or `None` when the query is not one."""
    import ast
    import operator
    q = " ".join(query.strip().rstrip("?.!").lower().split())
    q = _ARITH_OPENERS.sub("", q).strip()
    expr = q
    for pattern, sub in _ARITH_WORDS:
        expr = pattern.sub(sub, expr)
    expr = expr.strip()
    if not expr or not _ARITH_ONLY.match(expr):
        return None
    numbers = re.findall(r"\d+(?:\.\d+)?", expr)
    if len(numbers) < 2 or not re.search(r"[+\-*/%]|\*\*", expr):
        return None
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Mod: operator.mod, ast.Pow: operator.pow}

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            a, b = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Pow) and (abs(b) > 64 or abs(a) > _ARITH_LIMIT):
                raise ValueError("too large")
            return ops[type(node.op)](a, b)
        raise ValueError("not arithmetic")

    try:
        value = ev(ast.parse(expr, mode="eval"))
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError, RecursionError):
        return None
    if isinstance(value, complex) or abs(value) > _ARITH_LIMIT:
        return None
    if float(value).is_integer():
        spoken = str(int(round(value)))
    else:
        spoken = f"{value:.6g}"
    # Said as asked, in the words he can copy: "17 times 23 is 391."
    return f"{q} is {spoken}."


def web_search(query: str, get=None, avoid: tuple[str, ...] = (),
               pages=None, deep: bool = False) -> dict:
    """The callable `corn.agent.World(search=...)` takes.

    `get` is `requests.get` behind the page cache above, and is a parameter so
    `scripts/check_search.py` can assert the shape mapping against canned
    responses without a network. A guard that reached the internet would be
    testing DuckDuckGo's uptime, and would fail on a train.

    `avoid` is the second-source path: sources already heard from this
    question, skipped so "find another source" cannot answer with the first
    one wearing a different provider's hat. Empty on every ordinary call,
    so nothing measured changes shape.
    """
    if pages is None and get is None:
        pages = _PAGES
    get = get or _polite_get
    q = (query or "").strip()
    if not q:
        return {"ok": False, "reason": "empty_query",
                "clarify": "What would you like me to look up?"}

    # A sum is answered here and asked of nobody -- see `_arithmetic`. Before
    # the affixes come off for the same reason the self-referential gate runs
    # first: the strip could take a word the parser reads.
    sum_ = _arithmetic(q)
    if sum_ is not None:
        return {"answer": sum_, "source": "arithmetic", "query": q}

    # **The backstop, and it runs on the query as typed.** Before the affixes
    # come off, so a strip cannot remove the word the gate reads -- and before
    # any provider is constructed, so there is no path from here to the network.
    # See `_ABOUT_ME`. The hatches in `corn/agent.py` are the primary defence
    # and are wider than they were; this is what holds when they miss.
    side = _self_referential(q)
    if side is not None:
        return {"ok": False, "reason": "self_referential", "say": SELF_SAYS[side]}

    # After the empty check so a query that is nothing but phrasing still reads
    # as an empty query rather than as a search for the leftovers. See
    # `strip_affixes`: two of the 25 templates are cuts he cannot make, and the
    # words come off here instead.
    q = strip_affixes(q)

    payload, held, reached, blocked = _lookup(q, get, avoid, pages, deep)
    if payload is not None:
        return payload

    # **The reformulation, and it is a retry rather than a rewrite.** The first
    # pass asked the providers exactly what he wrote; this asks them the same
    # question as a noun phrase, and only because the first pass found nothing
    # it would serve outright -- a *held* abstract does not stop the retry,
    # because a suspected non-answer is exactly the case a better-phrased
    # second pass exists for. Session 13's measurement is the whole argument:
    # natural question 1 of 8, noun phrase 5 of 8, on the same eight facts.
    # Skipped entirely when `_rephrased` has no row for this opener, so an
    # ordinary miss still costs one pass and not two.
    #
    # `reached` accumulates across both passes for the reason it exists: if the
    # first pass reached nobody and the second reached somebody, the network is
    # up and the honest answer is `no_results`. `blocked` accumulates the same
    # way and for the same reason -- a refusal in either pass is a refusal this
    # turn ran into, and the second pass is the more likely of the two to meet
    # one, being the second time in a second the same host was asked.
    asked = q
    rewritten = _rephrased(q)
    if rewritten is not None:
        payload, held_again, reached_again, blocked_again = _lookup(
            rewritten, get, avoid, pages, deep)
        reached = reached or reached_again
        blocked = blocked or blocked_again
        if payload is not None:
            # The query field carries what was *asked of the provider*, which
            # is what `query` has always meant in this payload and what the
            # recheck path compares against. The user's own phrasing is not
            # lost -- it is the utterance, and the runtime still has it.
            return payload
        held = held or held_again

    # **The floor: a held abstract beats `no_results`.** Both passes ran, no
    # provider cleared its bar, and what remains is the abstract path's
    # suspected non-answer -- served exactly as it would have been before the
    # hold existed, because `HOLD_COVER`'s pricing says a rejected abstract
    # spends real answers. What changed is only who else got a chance first.
    if held is not None:
        return held

    # **A refusal outranks both admissions below it and outranks nothing above
    # it**, which is why it sits here rather than higher. A suspected
    # non-answer is still something the user asked for, and reporting a rate
    # limit while holding a sentence that answers the question would be the
    # refusal talking over the result. Below this line there is nothing left to
    # serve, and the honest account of an empty-handed turn names the host that
    # declined to look rather than blaming the network or the query.
    #
    # `reached` picks the sentence, and it is the same distinction the two
    # slugs below rest on: nobody else looked, as against the rest of the
    # providers looked and had nothing. Saying "I only had part of the web"
    # when the whole of it refused would overstate the search by exactly the
    # amount that matters, and the opposite understates it.
    if blocked is not None:
        return {"ok": False, "reason": "blocked",
                "say": BLOCKED_SAYS["partial" if reached else "none"].format(
                    provider=blocked.provider),
                BLOCKED_BY: {"provider": blocked.provider,
                             "cause": blocked.cause,
                             "detail": blocked.detail}}

    # The distinction that matters, kept: nobody looked, as against nothing was
    # found. `reached` is the difference, and it is now a fact about every
    # provider rather than about whichever one happened to raise first.
    if not reached:
        return {"ok": False, "reason": "unreachable",
                "say": "I couldn't reach the internet just now."}

    return {"ok": False, "reason": "no_results",
            "say": f"I couldn't find anything useful for {asked}."}
