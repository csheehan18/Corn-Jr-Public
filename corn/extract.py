"""Read a passage as overlapping windows, and reduce what comes back.

The runtime half of `docs/PLAN-WEB-SEARCH.md`'s WS-B-alt. Nothing here runs a
model: `windows` cuts the passage, `worker_prompt` builds what each window is
asked, `span_of` checks an answer against the window it came from, and `reduce`
turns N answers into one. The model sits between `worker_prompt` and `reduce`
and is the caller's business -- which is what makes every function in this file
testable without a checkpoint.

**Why windows are cut by token count and not by sentence.** `BatchedReader`
requires equal-length prompts, because `StaticCache.pos` is one scalar shared
by every row and `corn/model.py` uses learned absolute positions. Sentence
windows have unequal lengths, and the two ways to even them up are both wrong
here: left-padding shifts real tokens onto positions they were not trained at,
and right-padding puts pad tokens between the window and the answer where the
model attends to them. Slicing the token stream gives equal lengths by
construction. The cost is that a window can begin mid-sentence, and `STRIDE`
below is what pays it.

**Overlap is not a refinement, it is what makes the cut safe.** A fact that
straddles a window boundary -- "Iron melts at 1538" split after "at" -- exists
in neither window as a readable span. With `stride < width` every span shorter
than `width - stride` appears whole in at least one window, so the overlap is
sized against the length of an answer rather than against taste.
"""

from __future__ import annotations

import json
import re
from collections import Counter

from .tools import call_text

# A window wide enough to hold a fact with its sentence around it, and narrow
# enough to have no middle to lose things in -- external research entry 10
# finds the U-shaped positional bias worst in the middle of a context and worst
# of all at small scale. ~64 tokens is two to three sentences of ordinary prose
# at `bpe8k`.
WIDTH = 64

# Half the window. Every span shorter than 32 tokens therefore appears whole in
# some window, which covers every answer this is built for -- a name, a
# quantity, a date. It also doubles the number of windows, and A3 measured that
# as very nearly free: sixteen windows cost 25% more than one.
STRIDE = 32

# What a worker is asked, and **the call line is load-bearing.** Measured on
# `corn_jr_260m` before any training, over the same two windows:
#
#     <|obs|>{window}                 "What is the symbol for iron?"
#     <|obs|>{"answer": window, ...}  "the melting point of iron is 140
#                                      degrees Celsius"      <- invented
#     <|call|>... then the payload    "the melting point of iron is 1538
#                                      degrees Celsius, according to
#                                      Wikipedia"            <- correct
#
# The corpus contains no transcript where `<|obs|>` arrives without a
# `<|call|>` above it, and none where its body is bare prose rather than a
# JSON payload. Both departures put the worker off distribution at the
# *marker* level, and it answers conversationally instead of reading.
# Restoring the full shape moves it from drift to a correct extraction with
# nothing trained -- which is the cheapest result in this whole plan.
#
# So the worker prompt is a whole transcript rather than a fragment: the call
# the model would have written, the payload it would have been handed, and
# the say marker.
#
# **The call is `corn.tools.call_text`'s, not hand-written** (finding 127,
# PLAN-1-0 ground rule 6, ROADMAP C0). It was once `{"query": "{question}"}`
# with the question interpolated raw, so a question carrying a quote closed the
# string early -- 41,152 of `relpairs.txt`'s 61,728 calls were not JSON -- and
# one carrying a non-ASCII character was written raw beside a `\u`-escaped copy
# of itself in the payload. For a question with neither the two forms are the
# same bytes, so only those slices' rows moved when this changed.
PROMPT = ('{marker_user}look up {question}\n'
          '{marker_call}{call}\n'
          '{marker_obs}{payload}\n'
          '{marker_say}')


def content_words(text: str) -> list[str]:
    """Lower-cased alphanumeric words, punctuation dropped.

    **This is the importable form** -- `corn/retrieve.py` imports it, which is
    the "something imports both" moment the first version of this docstring
    scheduled. `corn/agent.py`'s `_content_words` is the same four lines and
    stays private to that module: its own docstring ties it to `_normalised`'s
    flattening, which is an agent-side contract this module has no part in.
    """
    kept = "".join(c.lower() if c.isalnum() else " " for c in text)
    return kept.split()


def windows(text: str, encode, decode, width: int = WIDTH,
            stride: int = STRIDE) -> list[str]:
    """Overlapping equal-length slices of `text`, as strings.

    Equal length is in *tokens*, which is what `BatchedReader` requires and
    what a character count would only approximate. The final slice is dropped
    rather than padded when it cannot be filled: a short last window would
    break the equal-length contract, and `stride < width` means its content
    already appears in the window before it.
    """
    ids = encode(text)
    if not ids:
        return []
    if len(ids) <= width:
        return [decode(ids)]
    out = []
    for start in range(0, len(ids) - width + 1, stride):
        out.append(decode(ids[start:start + width]))
    # The tail past the last full window. Covered by that window only if the
    # remainder is shorter than the overlap; otherwise take a final full-width
    # slice anchored at the end, which re-reads some text and loses none.
    if (len(ids) - width) % stride:
        out.append(decode(ids[-width:]))
    return out


def worker_prompt(question: str, window: str, marker_user: str,
                  marker_call: str, marker_obs: str, marker_say: str,
                  source: str = "wikipedia.org") -> str:
    """One window's prompt, as a whole transcript. See `PROMPT`.

    Markers are passed in rather than imported so this module does not depend
    on `corn/temporal.py`'s delimiters, which are the one thing in the
    transcript format a future change would move.
    """
    payload = json.dumps({"answer": window, "source": source,
                          "query": question})
    return PROMPT.format(marker_user=marker_user, question=question,
                         marker_call=marker_call,
                         call=call_text("web_search", {"query": question}),
                         marker_obs=marker_obs, payload=payload,
                         marker_say=marker_say)


def longest_span(answer: str, window: str) -> int:
    """The longest run of `answer`'s content words contiguous in `window`."""
    said, src = content_words(answer), content_words(window)
    best = 0
    for i in range(len(said)):
        for j in range(len(said), i + best, -1):
            run = said[i:j]
            if any(src[k:k + len(run)] == run
                   for k in range(len(src) - len(run) + 1)):
                best = len(run)
                break
    return best


def span_of(answer: str, window: str) -> bool:
    """Is the *whole* answer a contiguous run of the window?

    Kept as the strict form, and it is **not** the acceptance test -- see
    `grounded`. Measured: the best untrained reply was "the melting point of
    iron is 1538 degrees Celsius, according to Wikipedia", which is correct and
    is not a span, because a good answer frames the span rather than emitting
    it bare. A check demanding a bare span would reject the behaviour being
    built.
    """
    said = content_words(answer)
    return bool(said) and longest_span(answer, window) == len(said)


# Words a framing may add that came from neither the window nor the question.
# Deliberately tiny and closed: every one is a function word or a hedge and
# none can carry a fact. A frame vocabulary that could hold a noun would let an
# invented answer through, which is the one thing this must not do.
#
# **The first two rows are the corpus's own, and leaving one out cost the
# fourth correct answer this path produced.** `corn/replies.py`'s `SAY_ANSWER`
# is the complete set of four sentences a trained transcript ever wraps a
# search result in -- `{a}.`, `It's {a}.`, `{a}, according to {s}.`,
# `Looks like {a}.` -- so those are not framings a reply *might* add, they are
# the framings it was taught to add. The first draft of this set was written
# from three of the four, and the 260M's preferred reply is the fourth: over
# the iron passage it answered "Looks like 1538 degrees Celsius." on two
# windows of three and `grounded` refused both as invention, on `looks` and
# `like`. `scripts/check_extract.py` now asserts the containment, so a fifth
# template added to the corpus fails a guard here rather than silently costing
# an extraction rate.
FRAME = frozenset({
    # From `SAY_ANSWER`, which is where a reply's framing actually comes from.
    "it", "s", "according", "to", "looks", "like",
    # Function words and hedges no template supplies but a reply may still
    # reach for. None can carry a fact.
    "a", "an", "the", "is", "are", "was", "were", "its", "that",
    "of", "in", "at", "about", "around", "roughly", "approximately", "and",
})


def grounded(answer: str, window: str, question: str,
             source: str = "wikipedia.org") -> bool:
    """Did this answer come out of the window, framing allowed?

    Three conditions. Each rejects a reply `corn_jr_260m` actually produced, so
    none is hypothetical.

      * **no invention.** Every content word is in the window, the question,
        the attribution, or `FRAME`. "the melting point of iron is 140 degrees
        Celsius" fails on `140`, with 1538 sitting in the payload above it, and
        "the discoverer of penicillin, Howard Florey, was a British physician"
        fails on `physician` -- a word the passage never used.
      * **it adds something from the window.** At least one content word comes
        from the window and is not already in the question. "the melting point
        of iron" is accounted for word by word and answers nothing; that
        degenerate restatement is what the probes produced most often.
      * **the novel part is contiguous.** "1538" and "2862" both appear in the
        window and "1538 2862" is not something the passage says.

    **Contiguity is measured over the words taken from the window, not over the
    whole reply, and getting that wrong rejects correct answers.** Measured:
    "Vientiane, according to Wikipedia.org." is five words of which exactly one
    is from the window, and a rule that asked for two contiguous words anywhere
    in the reply refused it -- "vientiane according" is not a phrase the passage
    contains, and was never going to be. What the passage has to support is the
    *fact*, and the fact here is one word. So the frame is stripped first and
    the requirement falls on what is left.
    """
    said = content_words(answer)
    if not said:
        return False
    window_words = set(content_words(window))
    question_words = set(content_words(question))
    source_words = set(content_words(source))
    allowed = window_words | question_words | source_words | FRAME
    if any(w not in allowed for w in said):
        return False
    # What the answer took from the window and did not merely echo back from
    # the question. This is the part that carries the fact.
    novel_at = [k for k, w in enumerate(said)
                if w in window_words and w not in question_words
                and w not in source_words and w not in FRAME]
    if not novel_at:
        return False
    # **Contiguity is tested on the span as said, from its first novel word to
    # its last, with the frame words inside it kept.** The first version of
    # this rule tested the novel words alone, so "best-of-seven" was tested as
    # "best seven", "Stephen A. Douglas" as "stephen douglas" and "Coton in
    # the Elms" as "coton elms" -- none a phrase any passage contains -- and
    # the right answer was refused. Finding 85 counted it as twelve of the
    # window reader's twenty-two unwinnable passages; finding 115 measured it
    # at ten and seven right answers a seed on the whole-passage reader, and
    # the owner took the change on 2026-09-05. A frame word *outside* the span
    # ("It's", "according to") is still stripped, which is what lets a
    # one-word fact through. **And the core must be a verbatim run of the
    # window, all of it**: the old test asked for any two contiguous words,
    # which with the frame words kept would pass "1858 of Illinois" on the
    # strength of "of Illinois" alone -- two window facts joined by a frame
    # word is the invention this rule exists to refuse.
    core = said[novel_at[0]:novel_at[-1] + 1]
    return longest_span(" ".join(core), window) == len(core)


def _span_key(answer: str, windows_: list[str],
              source: str = "wikipedia.org") -> str:
    """The span an answer carries, as a grouping key.

    Grouped on the span rather than the whole reply, so two windows that framed
    the same fact differently still count as agreeing. Framing is exactly what
    the model varies and exactly what does not matter here.

    **The frame is stripped first, for the same reason `grounded` strips it, and
    the first version of this function did not.** `SAY_ANSWER` teaches
    `It's {a}.`, so `content_words` of a reply in the corpus's own framing opens
    with `it` and `s` -- and `it` appears in almost any window of English prose.
    Keying on the whole reply therefore found `it` in window 0 and stopped,
    which made `It's Vientiane.` and `It's Luang Prabang.` the *same key*.
    `reduce` then reported "2 of 3 windows agree on 'it'" and returned the first
    of two contradictory extractions as a consensus -- exactly the failure
    `docs/PLAN-WEB-SEARCH.md` pre-registers and `reduce`'s own "agreement beats
    presence" rule exists to prevent. Measured over the 678 multi-window
    answerable dev passages, `it` and `s` were 157 of the 197 collapsed keys.

    **And the longest span wins, not the first window that shares one.** The
    loop used to scan from index 0 and return on the first window with any
    overlap, so an answer extracted from window 5 was keyed off whatever partial
    run windows 0-4 happened to contain -- `nfl` for a gold of `nfc nfl`, `july`
    for `july 14 2017`. Two answers agreeing on a fact but keyed off different
    partials read as a disagreement, which is the same bug pointing the other
    way.

    Both directions were measured on the 678 multi-window answerable dev
    passages, before and after:

        the same fact in all four SAY_ANSWER framings must agree
            484/678 (71.4%)  ->  678/678 (100.0%)
        contradictory facts must not agree
            56/142 falsely agreed (39.4%)  ->  0/142 (0.0%)

    **Question words are kept, which is where this departs from `grounded` and
    the departure is measured.** `grounded` strips them because its question is
    "did the reply add anything beyond echoing what was asked". Grouping asks
    something else: two answers that differ *only* in a word the question also
    used are still two different answers. Stripping them merges `It's the NFC
    NFL.` with `It's the AFC NFL.` on the question "who has more super bowl wins
    nfc or afc" -- the same false consensus this function was fixed for, coming
    back in through the other door. Over the dev passages, keeping them also
    reads better on the property the stripping was supposed to buy:

        same fact in six framings agrees   strip 668/678 (98.5%)
                                            keep 678/678 (100.0%)

    Nothing is lost by keeping them, because `reduce` only ever keys replies
    `grounded` has already passed, and `grounded` guarantees at least one
    content word that came from the window and is *not* in the question. So a
    key is never pure question-echo for anything this actually groups.

    `source` is threaded through from `reduce` for the same reason `grounded`
    takes it: a reply framed "according to Britannica" is an attribution under
    the real source and a fact under a default. It is the only argument this
    needs -- keeping question words is what removed the other one.
    """
    said = content_words(answer)
    source_words = set(content_words(source))
    # What the reply asserts over and above its framing and the attribution.
    # No window to intersect against, because the key has to be comparable
    # across replies that came from *different* windows.
    novel = [w for w in said if w not in source_words and w not in FRAME]
    if not novel:
        # A reply that is all frame carries no fact to group on. Fall back to
        # the whole reply so two such replies still compare equal to each other
        # and not, by accident, to a real extraction.
        return " ".join(said)
    best, best_n = " ".join(novel), 0
    for w in windows_:
        n = longest_span(" ".join(novel), w)
        if n <= best_n:
            continue
        src = content_words(w)
        for i in range(len(novel) - n + 1):
            run = novel[i:i + n]
            if any(src[k:k + n] == run for k in range(len(src) - n + 1)):
                best, best_n = " ".join(run), n
                break
    return best


# The words a span may be given back. Deliberately just the articles, and
# deliberately the same three `corn.evals._DETERMINERS` forgives: anything
# wider ("of", "in") would start prepending real omissions.
DET = frozenset({"the", "a", "an"})


def _locate(novel: list[str], windows_: list[str]) -> tuple[list[str], int, int] | None:
    """`(the window's content words, where the span starts, how long)`.

    The same search `_span_key` does, kept separate because that function
    wants the span's *text* and this one wants its *position* -- and a
    position is what the word in front of it can be read from.
    """
    best, best_n = None, 0
    for w in windows_:
        n = longest_span(" ".join(novel), w)
        if n <= best_n:
            continue
        src = content_words(w)
        for i in range(len(novel) - n + 1):
            run = novel[i:i + n]
            for k in range(len(src) - n + 1):
                if src[k:k + n] == run:
                    best, best_n = (src, k, n), n
                    break
            if best_n == n:
                break
    return best


def det_repair(reply: str, windows_: list[str],
               source: str = "wikipedia.org") -> str:
    """Give a located span back the determiner its window put in front of it.

    "It's Ramones." out of a window that says "the Ramones" becomes "It's the
    Ramones.", and the eighty-second finding is the licence: over the frozen
    eval this **fires 14, fixes 5 and breaks 0** (`span` 94 -> 100, `exact`
    89 -> 94), replicating on the phrase eval at 12 / 3 / 0, pooled exact
    binomial **p = 0.0078**. It was the only one of four model-free re-cut
    rules to survive its control -- `NAME` and `NUM` break more than they fix.

    **The zero breakage is structural rather than lucky.** Determiners are
    `FRAME` words, so prepending one cannot add a novel content word: it
    cannot make a `grounded` reply ungrounded, cannot cost `exact`, and cannot
    turn a right answer into a wrong one. The most it can do is nothing.

    **What it repairs is the class the scorer declines to credit.**
    `score_extract_span`'s own note -- NQ writes golds like "the Ramones" and
    "The aorta" where the article is orthography, not content -- and
    `near_miss_det` is the bucket that counts them. This converts that bucket
    and no other.

    Three decisions worth their lines:

      * **The determiner goes in lower case, not the window's case.** A window
        capitalises "The" because a sentence started there, and a reply is
        being framed mid-sentence ("It's the ..."); every scorer here is
        case-insensitive, so the choice is about how it reads aloud.
      * **The key is not repaired, only the answer.** `reduce` groups on
        `_span_key`, and moving the grouping under a rewrite would change
        which replies count as agreeing -- a different change with a different
        argument, unmeasured. So agreement is decided first and the article is
        given back to the winner.
      * **No insertion where the span's first word is not a whole token.** A
        reply's "1,538" is two content words and there is no clean place in
        front of the second one; the rule declines rather than guessing, which
        is the conservative direction for a repair whose whole case is that it
        cannot break anything.
    """
    said = content_words(reply)
    src_words = set(content_words(source))
    novel = [w for w in said if w not in src_words and w not in FRAME]
    if not novel:
        return reply
    found = _locate(novel, windows_)
    if found is None:
        return reply
    src, k, n = found
    if k == 0 or src[k - 1] not in DET:
        return reply
    det, run = src[k - 1], src[k:k + n]
    # Where the span sits in the reply's own words, and whether the article is
    # already in front of it -- a reply that said "the Ramones" needs nothing,
    # and `novel` cannot answer that because `the` is a FRAME word it strips.
    at = next((j for j in range(len(said) - n + 1) if said[j:j + n] == run),
              None)
    if at is None or (at and said[at - 1] == det):
        return reply
    toks, seen = reply.split(), 0
    for i, tok in enumerate(toks):
        cw = content_words(tok)
        if seen <= at < seen + len(cw):
            if cw[0] != run[0]:
                return reply
            return " ".join(toks[:i] + [det] + toks[i:])
        seen += len(cw)
    return reply


def _contains_words(big: str, small: str) -> bool:
    """Is `small` a contiguous word run of `big`?

    Word granularity, not substring: keys are `content_words` joins, and
    `"15" in "1538"` is true as strings while 15 and 1538 are different
    numbers. `_overlaps` below accepts that looseness because it compares two
    spans already known to be same-type rivals in one window; here the two
    sides are extractions from *different* windows and the containment is
    what argues they are one fact, so it has to hold at the word level.
    """
    b, s = big.split(), small.split()
    if not s or len(s) > len(b):
        return False
    return any(b[i:i + len(s)] == s for i in range(len(b) - len(s) + 1))


def _canonical(keys: list[str], mergeable: frozenset[str]) -> dict[str, str]:
    """Each key mapped to the one maximal key that contains it, when unique.

    **The whole-name-against-surname repair, moved from `property_local`'s
    private helper into the tally where the live run showed it missing.** A
    reply "Alexander Fleming." keys `alexander fleming` and a reply
    "Fleming." keys `fleming`, and before this the tally read them as a
    disagreement and abstained -- the exact reading `_overlaps` documents as
    one fact read whole or by surname. The first live `--extract` session
    (2026-08-27) hit the same shape on its first proper-name question.

    Maximal keys are the ones no other key word-contains. A key contained by
    exactly one maximal key merges into it; a key contained by two different
    maximal keys is ambiguous -- `fleming` against both `alexander fleming`
    and `fleming institute` -- and stays its own group, because a merge that
    guessed would manufacture the false consensus `reduce`'s ordering exists
    to prevent. What does *not* merge is the point: `augusta ada` and
    `lovelace` share no run and stay a disagreement.

    **`mergeable` is the set of keys that state their reply's whole
    assertion, and only those may fold in.** A key can also be a
    *truncation*: `_span_key` keys a reply by the longest run a window
    actually contains, so "It's the AFC NFL." over windows that only ever
    say "NFC NFL" keys down to `nfl` -- and merging that into `nfc nfl`
    would count a contradicting reply toward the fact it contradicts. The
    first draft of this function did exactly that and the guard's NFC/AFC
    case caught it. A truncated key voting under its partial, separately,
    is the old behaviour and stays.
    """
    uniq = set(keys)
    maximal = [k for k in uniq
               if not any(o != k and _contains_words(o, k) for o in uniq)]
    out = {}
    for k in uniq:
        if k in maximal or k not in mergeable:
            out[k] = k
            continue
        homes = [m for m in maximal if _contains_words(m, k)]
        out[k] = homes[0] if len(homes) == 1 else k
    return out


# How close a question's word must sit to a value before it counts as naming
# that value rather than as the subject of the sentence. Two words covers
# "melts at 1538" and "boils at 2862"; three would start catching the subject
# noun in short clauses, which is the false rejection this constant exists to
# avoid -- "Iron melts at 1538 ... and boils at 2862" has `iron` three words
# from the first value and discriminating nothing.
ADJACENT = 2


def _same_type_spans(window: str, answer: str) -> list[str]:
    """Every span in `window` of the answer's own type, the answer included.

    The type split is `corn.extractgen._has_distractor`'s, deliberately: that
    function decides what counts as a distractor when the slice is built, and a
    runtime check that drew the line somewhere else would be guarding a
    different claim than the one the corpus was measured against.
    """
    if any(c.isdigit() for c in answer):
        return re.findall(r"\d[\d,.]*\d|\d", window)
    # **Whole names, not words.** "Penicillin was discovered by Alexander
    # Fleming" splits into two capitalised words, and treating them as rival
    # candidates rejects the surname: "discovered" sits two words from the
    # forename and three from the answer. A name is the run, not its parts.
    return re.findall(r"\b[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*\b", window)


def _overlaps(span: str, answer: str) -> bool:
    """Are these the same thing? `Fleming` is `Alexander Fleming`'s answer.

    The model returns the span it read, and a name can be read whole or by
    surname. Without this the check treats them as rivals and rejects the
    answer for not being adjacent to a term its own forename is adjacent to.
    """
    a, b = span.strip().lower(), answer.strip().lower()
    return bool(a) and bool(b) and (a in b or b in a)


# Where a span was removed, while `isolate` is still working. A private-use
# codepoint rather than a letter or a punctuation mark: it has to survive the
# tidying regexes as one thing and it must never appear in Wikipedia prose.
_CUT = ""

# Function words that mean nothing once the thing they governed is gone. "won
# by X, with Y" losing X leaves "won by, with", and the preposition is what
# makes the hole conspicuous -- see `isolate`. Only words that cannot end a
# clause honestly, so a sentence genuinely ending in one is not rewritten.
_ORPHAN = ("by", "of", "with", "from", "as", "to", "for", "in", "on", "at",
           "and", "or", "the", "a", "an")


# Capitalised runs that a sentence boundary produced rather than an entity.
# `_same_type_spans` matches any `[A-Z][a-z]{2,}` run, so every sentence opening
# with a pronoun, a conjunction or an adverb offers one, and on the first
# isolation build "She", "This" and "However" were between them 2.4% of the
# rivals a miss twin got to keep -- a window whose only surviving candidate is
# `She` teaches declining-when-there-is-nothing-there, which is not the lesson.
# Closed class, and deliberately only that: `American` and `May` stay, because
# a nationality and a month are answers to real questions and the runtime would
# isolate them.
#
# `FRAME` is checked alongside this and not merged into it: `FRAME` is the
# vocabulary a *reply* may add around an answer, which is a different question
# that happens to share four words.
NOT_A_VALUE = frozenset({
    "he", "she", "they", "them", "his", "her", "hers", "their", "theirs",
    "you", "your", "yours", "we", "our", "ours", "this", "these", "those",
    "there", "here", "who", "whom", "whose", "what", "when", "where", "why",
    "how", "which", "but", "for", "from", "with", "without", "within",
    "after", "before", "during", "since", "until", "while", "because",
    "although", "though", "however", "meanwhile", "moreover", "therefore",
    "thus", "then", "also", "still", "yet", "not", "nor", "both", "each",
    "every", "some", "any", "all", "one", "two", "three", "other", "another",
    "such", "same", "own", "many", "most", "more", "less", "few", "several",
})


def deletable(window: str, keep: str, question: str) -> list[str]:
    """The spans `isolate` may remove: same-type rivals of `keep` that are
    neither `keep` itself nor part of what the question is asking about.

    Separated from `isolate` because `corn/isogen.py` needs the same list to
    *choose* a rival to keep, and a generator picking its rival by one rule
    while the runtime deletes by another would build a slice describing a
    procedure that does not exist.
    """
    qwords = set(content_words(question))
    out = []
    for span in _same_type_spans(window, keep):
        span = span.strip()
        if not span or _overlaps(span, keep):
            continue
        if set(content_words(span)) & qwords:
            continue  # the subject, not a rival -- see `isolate`
        if not re.search(r"\b" + re.escape(span) + r"\b", window):
            # **What this list offers, `isolate` must be able to remove.**
            # `_same_type_spans` finds digits inside words -- `16` in `M16`,
            # `100` in `F-100s`, `4` in `4th` -- and those are neither values a
            # question could be asking for nor strings a word-bounded deletion
            # can take out. Leaving them here made `check_iso.py` read 91
            # windows as un-isolated that were correctly isolated, which is a
            # guard failing on a disagreement between two functions rather
            # than on the data.
            continue
        if span.lower() in FRAME or span.lower() in NOT_A_VALUE:
            # `_same_type_spans` matches any capitalised run, and a sentence
            # opening with "The", "She" or "However" is one. Those cannot be
            # answers, and deleting them is how a window loses its grammar for
            # nothing.
            continue
        if span not in out:
            out.append(span)
    return out


def isolate(window: str, keep: str, question: str) -> str:
    """The window with every same-type rival of `keep` deleted.

    **One candidate at a time, which is the only condition this model reads
    well.** The sixty-sixth finding measured three arrangements of the same two
    facts and the third is the one that matters: together in one sentence he was
    right 4 of 8, split far apart 6 of 8, and **alone 7 of 8**. Rival presence,
    not window size or sentence alignment, is what decides. Measured again on
    the frozen NQ eval (2026-08-31, `scripts/probe_isolation.py`): asked about a
    window holding only the gold he names it 59% of the time, and asked about
    one holding only a rival he names that rival 11% of the time -- a
    discrimination the 1-of-N choice never shows, because in the 1-of-N choice
    he takes the typed, topical span and the relation word is not read.

    So this is the transformation both halves of that procedure share: it turns
    "which of these five names answers the question" into five asks of "does
    this name answer it", each of which he can decline.

    **The question's own words are protected, and that is `property_local`'s
    rule rather than a new one.** For "who sang the birds and the bees" over
    "\"The Birds and the Bees\" was a 1964 single release by Jewel Akens", the
    title is a capitalised span and a rival by type; deleting it takes the
    subject out and leaves a window about nobody. That rule is written here a
    second time rather than shared with `property_local`, on
    `extractgen._has_distractor`'s precedent: the two decide different questions
    -- what may be *deleted* against what may *rival* -- and a shared helper
    would let a change to one silently move the other.

    **The scar is left in.** Deleting a span from real prose leaves ungrammatical
    text ("The winner was 19-year-old from Bend, Oregon"), and neither smoothing
    it nor substituting a placeholder is available: a placeholder of the right
    type is a rival again, and one of the wrong type is a word no corpus line
    carries. What makes the scar safe is that the slice built on this function
    scars **both** twins -- the gold-alone window and the rival-alone window are
    the same window cut the same way -- so "this text has a hole in it" cannot
    become a cue for declining. `corn/isogen.py` states that as the property its
    guard asserts.

    Returns the window unchanged when `keep` has no rivals to remove, which is
    the commonest case in a passage and the reason the caller checks
    `extractgen._has_distractor` before spending an ask on it.
    """
    out = window
    # **To a fixed point, because one pass does not isolate.** Deleting a span
    # can expose a rival the first pass could not see: a run the regex matched
    # whole ("Kris Kristofferson and Janis Joplin") loses one name and the
    # remainder becomes a match in its own right, and a rival occurring twice
    # survives its own deletion. Measured on the first build, one pass left a
    # same-type rival standing in 10.5% of the windows it claimed to have
    # isolated. Bounded rather than `while True`: three passes cleared every
    # window in that build, and a slice is not the place to discover a cycle.
    for _ in range(3):
        rivals = deletable(out, keep, question)
        if not rivals:
            break
        for span in rivals:
            # Word-bounded, because `str.replace` is not: deleting the month
            # `May` from a window turns `Maybe` into `be`.
            out = re.sub(r"\b" + re.escape(span) + r"\b", _CUT, out)
    # **The orphan a deletion leaves is removed with it, and that is what keeps
    # the two halves of `isogen`'s pair comparable.** Cutting a rival out of a
    # list ("A, B and C") and cutting the gold out of its binding clause ("won
    # by X, with") leave different wreckage: the first is a stray comma, the
    # second a dangling preposition sitting next to the question's own words.
    # Measured on the first build that difference was 6.6 points of cut-mark
    # rate between the answer half and the miss half -- a cue for declining
    # that has nothing to do with reading. Cuts are marked while they are made
    # so the tidying can find them, and the marker is gone by the last line.
    out = re.sub(r"\b(" + "|".join(_ORPHAN) + r")\s*" + _CUT, _CUT, out,
                 flags=re.IGNORECASE)
    out = re.sub(r"\s*" + _CUT + r"\s*", " ", out)
    # Whitespace and the punctuation the deletion orphaned. Deliberately light:
    # a scar remains and is meant to -- only the artefacts a reader would call
    # broken spacing rather than broken grammar are tidied.
    out = re.sub(r"\s+([,;:.])", lambda m: m.group(1), out)
    out = re.sub(r"([(\[])\s*([)\]])", "", out)
    out = re.sub(r"([(\[])\s+", lambda m: m.group(1), out)
    out = re.sub(r"([,;:])\s*([,;:.])", lambda m: m.group(2), out)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()


def _nearest(words: list[str], target: str, span: str) -> int | None:
    """Word distance from the first occurrence of `span` to the nearest `target`.

    **Located by first word, because a span can be several.** `words` is a
    token list, so `"alexander fleming" in w` is false for every entry and a
    multi-word candidate would be silently exempt from every check that uses
    this -- which is the shape of hole that makes a guard read green while
    guarding nothing. Names are 120 of the frozen eval's 200 answerable golds,
    so that exemption would have covered most of the row.
    """
    head = span.strip().lower().split()
    if not head:
        return None
    try:
        at = next(i for i, w in enumerate(words) if head[0] in w)
    except StopIteration:
        return None
    hits = [i for i, w in enumerate(words) if w.startswith(target[:4])]
    return min((abs(i - at) for i in hits), default=None)


def property_local(answer: str, window: str, question: str) -> bool:
    """Is this span the one the question's own words point at?

    **The sixty-sixth finding's repair.** That finding measured the rule the
    weights actually implement -- *the first value of the gold's type in the
    window* -- by flipping a clause and watching which question the model got
    right follow the order rather than the property. Asked for the boiling
    point of "Iron melts at 1538 degrees Celsius and boils at 2862 degrees
    Celsius", it answers 1538, and no window size or sentence alignment
    changes that because both candidates share a clause.

    **Proximity is not the test; nearest is.** "boils" sits four words from
    1538 and one word from 2862, so any radius wide enough to accept a real
    answer accepts the wrong one too. This asks instead whether some *other*
    same-type span in the window is strictly closer to one of the question's
    own words than the chosen answer is, and rejects when one is.

    **Question words are excluded from the candidate set**, which is what stops
    this rejecting correct answers. For "the capital of Japan" over "The
    capital and largest city of Japan is Tokyo", `Japan` is a capitalised span
    nearer to "capital" than `Tokyo` is -- and it is also in the question, so
    it is not a candidate and the check does not fire.

    Returns True when the check does not apply: fewer than two candidates means
    nothing to confuse, and a question term absent from the window points at
    nothing.
    """
    words = [w.lower().strip(".,;:()\"'") for w in window.split()]
    qwords = set(content_words(question))
    # A candidate containing any of the question's own words is the subject,
    # not a rival for the answer. Whole-span equality is not enough: the regex
    # keeps a leading determiner, so "the Nile" is not `nile` and would have
    # been admitted as a candidate against its own question.
    spans = [s for s in _same_type_spans(window, answer)
             if not set(content_words(s)) & qwords]
    others = [s for s in spans if s.strip() not in answer]
    if not others:
        return True
    terms = [t for t in qwords if t not in content_words(answer)]
    for term in terms:
        # Which candidates does this term sit *beside*? A term three words away
        # from one value and eight from another is the subject of the sentence,
        # not a label on either -- "iron" is nearer 1538 than 2862 in "Iron
        # melts at 1538 ... and boils at 2862" and discriminates nothing. A
        # term within `ADJACENT` words is the one that names the property:
        # "melts at 1538", "boils at 2862".
        beside = [s for s in spans
                  if (d := _nearest(words, term, s)) is not None and d <= ADJACENT]
        if beside and not any(_overlaps(s, answer) for s in beside):
            return False
    return True


def reduce(answers: list[str | None], windows_: list[str], question: str,
           source: str = "wikipedia.org",
           local: bool = False) -> tuple[str | None, str]:
    """One answer from N, or `None` and the reason there is not one.

    **Agreement beats presence, and that ordering is the rule.** One confident
    wrong extraction would otherwise outvote several correct abstentions, the
    failure mode `docs/PLAN-WEB-SEARCH.md` pre-registers. So an answer two
    windows agree on wins over one a single window offers, though both are
    "present".

    The four outcomes are the ones the plan names:

        several windows agree        -> that answer, high confidence
        exactly one window extracts  -> that answer, localised
        several windows disagree     -> None: something is wrong, say so
        no window extracts           -> None: N independent readings agreeing
                                        the passage does not answer it

    The last is why this returns a *reason*. An abstention because nothing was
    found and one because the readings conflicted are different facts about the
    passage, and collapsing them loses the only signal this design has that a
    single reading does not -- see the plan's asymmetry section.

    A reply that is not `grounded` is dropped before any of this. It is not an
    abstention, it is an unusable answer, and the count is the caller's to
    report: on an untrained worker it is most of them.

    **`local` is the locality veto and it is now off by default, which
    retires the sixty-sixth finding's repair from this path.** The mechanism
    stays -- `property_local` is unchanged, importable, and still guarded --
    but nothing calls it unless a caller asks.

    The number that retired it is `scripts/probe_multiwindow.py`'s, over
    1,003 whole passages on the shipping checkpoint: **joint 464 with the
    veto off against 378 with it on**, an 86-item difference on the
    population the runtime actually reads in. `scripts/probe_local.py` shows
    what it does buy -- on `evals/paired.jsonl`, the file written for the
    clause-flip failure it exists for, it converts 7 wrong answers into
    silence and costs no right ones -- so this is not a rule that never
    worked. It is a rule whose true positives are worth 7 on a 128-item
    single-window file and whose false positives cost 86 on a 1,003-passage
    one, because `_local` is `all()` over the judging windows and every
    window added is one more chance for a single objector to kill an answer
    (`probe_multiwindow` (c): false-veto rate flat at 13-18% however many
    judges there are -- unanimity-to-keep, not corroboration-to-veto).

    **Nothing replaces it, and that is measured rather than assumed.** The
    retirement above is a cost argument and not a substitution: it prices the
    7 against the 86 and names nothing that covers the 7.
    `scripts/probe_gate_paired.py` asked whether the gate does, on
    `paired.jsonl` itself, and the answer is no in the strongest form -- the
    gate **admits 128 of 128 windows** there, covers **0 of 12** catches, and
    returns an answer byte-identical to the unvetoed arm on every item.
    Willingness on that file runs -0.0032 to -0.0001 against a threshold of
    -0.136, two orders of magnitude clear of the bar, so no tuning reaches
    this. `corn/gate.py` scores whether an answer is *present*;
    `property_local` scores whether the value picked is the one the question
    *points at*; the clause flip is exactly the case where the first is an
    unambiguous yes and the second a no. A presence detector cannot decline a
    window that is full of answer.

    So with `local` defaulting False the clause-flip failure is uncovered on
    every path, and on the shipping checkpoint it is worth **12 sibling
    answers spoken on 128 items where the veto speaks 0** -- more than the 7
    `probe_local` measured on v4, because ft4g makes the error more often. The
    trade still holds; what does not hold is the idea that something else is
    catching these.

    Kept as a parameter rather than deleted for three reasons: the failure it
    was built for is real and **currently unhandled**, a caller that wants the
    rule should be able to have it, and the guards in
    `scripts/check_extract.py` assert the mechanism still fires when asked, so
    a later repair starts from a working rule rather than from a description
    of one.

    **The winner is handed to `det_repair` on its way out**, which gives a
    located span back the article its window put in front of it -- measured at
    5 fixed and 0 broken on the frozen eval (eighty-second finding). Applied
    after the tally, never before it: the grouping is decided on what the
    replies said, and the article is orthography the winner is allowed to
    recover.

    **`None` is a fourth thing and the commonest one untrained: the worker
    never finished.** A row that spent its whole token budget without reaching
    a marker gave the opening of a long answer, not a short one, and passing
    that fragment to `grounded` reports `cels` and `192` as inventions --
    blaming the model for the harness's budget. Withheld rather than dropped
    silently, because if a truncated reply could vote then the budget decides
    the answer, and counted in the reason, because "nothing was found" and "he
    never stopped talking" are different facts and the second is the one that
    the extraction slice exists to fix.
    """
    unfinished = sum(1 for a in answers if a is None)
    tail = (f" ({unfinished} of {len(windows_)} never finished)"
            if unfinished else "")
    kept = [a.strip() for a, w in zip(answers, windows_)
            if a and a.strip() and grounded(a, w, question, source)]
    if not kept:
        return None, "no window extracted an answer" + tail
    # Keyed once and kept beside its reply. The first version called
    # `_span_key` twice -- once to tally and once to find the winner -- which
    # was correct only while the function was pure in its two arguments and is
    # wasteful either way.
    keys = [_span_key(a, windows_, source) for a in kept]
    # Tallied over canonical keys, so a fact stated whole in one window and
    # by its tail in another counts as agreement rather than as a
    # disagreement that abstains -- see `_canonical`. A key may only merge
    # when every reply carrying it asserted exactly that key and no more;
    # a reply `_span_key` truncated keeps its partial key to itself. `top`
    # is always some reply's own key: maximal keys are drawn from the keys
    # themselves and map to themselves, so the winner loop below still
    # finds the reply that stated the fact in full.
    src_words = set(content_words(source))
    whole: dict[str, bool] = {}
    for a, k in zip(kept, keys):
        novel = [w for w in content_words(a)
                 if w not in src_words and w not in FRAME]
        whole[k] = whole.get(k, True) and k.split() == novel
    canon = _canonical(keys, frozenset(k for k, ok in whole.items() if ok))
    tally = Counter(canon[k] for k in keys)
    (top, n), = tally.most_common(1)

    def _local(span: str) -> bool:
        """Does the winner survive the locality check in every window that can judge?

        **`span` is `_span_key`'s output, not the reply.** The replies here are
        framed -- `SAY_ANSWER` teaches `It's {a}.` -- so a reply is almost never
        a substring of the window it came from, and checking the reply would
        find no window to check and reject every answer. That is not a
        hypothetical: it is what the first version of this did.

        **`all`, not `any`, and the difference is the whole check.**
        `property_local` is innocent-unless-proven-guilty: it returns True
        whenever it cannot judge -- no rival candidate in the window, or no
        question word beside one. So a window holding only "melts at 1538"
        cannot see the boiling point two clauses away and votes True either
        way, and `any` would let that window vouch for an answer a window
        holding both values had already objected to. Under `all`, the windows
        that cannot judge abstain and the ones that can decide.
        """
        if not local:
            return True
        fits = [w for w in windows_ if span and span.lower() in w.lower()]
        return all(property_local(span, w, question) for w in fits)

    if n > 1:
        for a, k in zip(kept, keys):
            if k == top:
                if not _local(top):
                    return None, (f"{n} of {len(windows_)} windows agree on "
                                  f"{top!r}, but the question points at a "
                                  f"different value{tail}")
                return (det_repair(a, windows_, source),
                        f"{n} of {len(windows_)} windows agree on {top!r}{tail}")
    if len(tally) == 1:
        if not _local(next(iter(tally))):
            return None, (f"1 of {len(windows_)} windows extracted it, but the "
                          f"question points at a different value{tail}")
        return (det_repair(kept[0], windows_, source),
                f"1 of {len(windows_)} windows extracted it{tail}")
    return None, (f"{len(tally)} windows disagree "
                  f"({', '.join(sorted(tally))[:80]}){tail}")


def read_passage(question: str, passage: str, encode, decode, run,
                 markers: tuple[str, str, str, str],
                 source: str = "wikipedia.org", width: int = WIDTH,
                 stride: int = STRIDE, gate=None,
                 gate_threshold: float = 0.0,
                 whole: bool = False) -> tuple[str | None, str]:
    """Cut, ask, reduce. `(answer or None, the reason either way)`.

    The whole of WS-B-alt with the model held at arm's length: `run` takes N
    prompts and returns N replies, and everything on either side of it is the
    arithmetic above. That is what lets `scripts/check_extract.py` assert the
    path end to end against canned replies -- a fake `run` that returns the
    same string for every window is a unanimous agreement, one that returns
    two different spans is a disagreement, and neither needs a checkpoint.

    `markers` is `(user, call, obs, say)` for the same reason `worker_prompt`
    takes them separately: this module does not import the delimiters.

    The reason comes back on success as well as failure. An answer three
    windows agree on and an answer one window offered alone are different
    facts about the passage, and the caller is what turns them into a count.

    **`gate` is the second callable, and it arrives the same way `run` does.**
    `(question, prompts) -> one willingness per prompt`, higher meaning more
    willing to answer; `corn/gate.py` is what binds weights to it and this
    module still holds none. A window scoring below `gate_threshold` is never
    decoded at all -- the runtime authors the canonical decline for it, which
    `reduce` drops as ungrounded, so a refused window contributes nothing to
    the tally rather than voting to abstain. When every window is refused the
    reduce sees N declines and returns its own "no window extracted" -- the
    same abstention it would have reached by reading, reached without
    spending the decodes.

    **The gate decides whether he speaks; it does not decide what he says.**
    The forcing half of the policy -- masking the decline's head tokens at the
    say turn's first token -- belongs to the decoder, so `run` is what carries
    it, and both halves are wired from one flag so they cannot disagree. With
    `gate=None` this function is what it always was, byte for byte -- the one
    behaviour change the flag does *not* guard is `det_repair`, which ships
    unconditionally inside `reduce` and has its own commit and its own
    argument for why it cannot break anything.

    **`whole` is the cut not being made, and it is one line here because that
    is all it is.** `corn/reader.py`'s `WholeHeadReader` reads a passage in one
    forward with the whole of it in the payload, so there is nothing to tile
    and nothing to vote: `cut` is the passage, `run` is asked once, and the
    single reply goes into the same `reduce`, which already handles one window
    ("1 of 1 windows extracted it") and is the branch `verdict_at`'s `top` mode
    has always exercised. `grounded`, `det_repair`, `_canonical` and `reduce`
    are untouched, which is the whole reason the two readers land on one
    ladder. The window size and the stride simply do not apply, and a caller
    that passed `whole` with a `gate` would be gating a passage rather than a
    window -- a third thing nobody measured, so it is refused.
    """
    if whole and gate is not None:
        raise ValueError("a whole-passage read has no windows to gate")
    cut = ([passage] if passage else []) if whole else \
        windows(passage, encode, decode, width, stride)
    if not cut:
        return None, "the passage is empty"
    prompts = [worker_prompt(question, w, *markers, source=source)
               for w in cut]
    if gate is None:
        answers = run(prompts)
        if len(answers) != len(cut):
            raise ValueError(
                f"{len(cut)} windows asked, {len(answers)} answered")
        return reduce(answers, cut, question, source)

    # Locally imported: `corn/gate.py` imports `content_words` from this
    # module, so a top-level import here would be a cycle -- and would put
    # torch, which `gate` needs and this module does not, on every import of
    # `corn.extract`.
    from .gate import decline_text

    sig = gate(question, prompts)
    if len(sig) != len(cut):
        raise ValueError(f"{len(cut)} windows scored, {len(sig)} scores")
    speak = [i for i, s in enumerate(sig) if s >= gate_threshold]
    replies = run([prompts[i] for i in speak]) if speak else []
    if len(replies) != len(speak):
        raise ValueError(f"{len(speak)} windows asked, {len(replies)} "
                         "answered")
    # Per window, because `decline_text` sizes the phrasing against the window
    # it is declining about -- see its docstring.
    answers: list[str | None] = [decline_text(question, w) for w in cut]
    for i, reply in zip(speak, replies):
        answers[i] = reply
    got, why = reduce(answers, cut, question, source)
    if len(speak) < len(cut):
        why += (f" ({len(cut) - len(speak)} of {len(cut)} windows did not "
                "pass the gate)")
    return got, why
