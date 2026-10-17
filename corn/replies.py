"""The reply sentences the corpus trains *and* the runtime reads or writes.

Two pools, each owned by a generator for as long as only the corpus used it,
and each moved here the day the runtime needed it too:

    SAY_ANSWER   how a found answer is said        -- `toolgen`'s tool slice
    MISS_SAY     how an honest miss is said        -- `extractgen`'s WS-B slice

The runtime needs both: `corn/gate.py` says `MISS_SAY[0]` itself when the gate
declines and masks the pool's first tokens when it speaks, and `corn/reader.py`
writes a span into `SAY_ANSWER[1]`. While they lived in the generators, those
two imports made `toolgen`, `extractgen` and -- through `extractgen`'s scorer
import -- `evals` and every generator it reads part of what `harness/` ships.
`scripts/check_layering.py` reported a closure of 27 modules and passed,
because its second check could not fail; this file is half of that repair.

**Nothing here may import a generator.** A pool that moves here moves with
its argument (the comment beside it), and the generator that owned it imports
it back, so `corn.toolgen.SAY_ANSWER` and `corn.extractgen.MISS_SAY` still
resolve for every script that reads them from there. The values are
byte-identical to what they were in the generators; changing one is a corpus
change, and every row scored against the pool moves with it.
"""

from __future__ import annotations

# How a found answer is said: the tool slice's four frames around the lookup's
# `answer` and `source`. `corn/extract.py`'s `FRAME` was written around them,
# and `SAY_ANSWER[1]` is the framing every generative reader arm was scored
# through.
SAY_ANSWER = ("{a}.", "It's {a}.", "{a}, according to {s}.", "Looks like {a}.")

# How an honest miss is said. The argument for this being a pool rather than
# one sentence is `corn/extractgen.py`'s docstring, "What this teaches". Every
# one contains a phrase from `evals.MISS_MARKERS` and uses only words that
# vocabulary, the question, or `extract.FRAME` supplies -- which together are
# what `score_extract_abstain` accepts without reading the reply as a smuggled
# answer. Both properties are asserted by the guard, not assumed here.
#
# `{q}` is the question, and interpolating it is what makes the nine that carry
# it thousands of distinct strings rather than nine. It is also the corpus's own
# shape: the `no_results` sentence names the query back.
#
# **The row constrains this pool, and three of the first nine drafts failed it.**
# `score_extract_abstain` wants a `MISS_MARKERS` phrase present *and* no content
# word outside `_MISS_VOCAB`, the question and `FRAME`. So "I'm afraid" failed on
# the `m` an apostrophe leaves behind, "This doesn't say" failed on `this` (FRAME
# carries `that` and not `this`), and "There's nothing here about" failed for
# containing no marker at all -- `nothing about` is one, `nothing here about` is
# not. Each read as a perfectly good abstention and each would have scored zero.
#
# The phrasings were changed rather than the scorer, and that direction is not a
# matter of taste: `extract.abstain` is frozen at 0/200 and widening `_is_miss`
# would make the baseline it will be read against incomparable. The cost is real
# and worth naming -- the abstention vocabulary this slice can teach is bounded
# by the row that scores it, so the cardinality argument above is weaker here
# than it is for `sayvar`, and a model abstaining in words the row does not
# credit will read as a failure it is not.
#
# **The last five do not name the question back, and that is a length budget
# rather than a stylistic choice.** `score_extract_abstain` applies
# `_length_verdict` before anything else, so a reply long against its window
# reads `wrote_own` -- a failure -- however honest it is. A long question inside
# a short window's reply trips exactly that: "The text doesn't say anything
# about who is the guy with 1 eye in vikings" against a 40-token window was one
# of twelve caught on the first build. Echoing the query is the corpus's shape
# and buys the cardinality; not echoing it is what fits. `extractgen` shuffles
# the pool per item and keeps the first phrasing `scores_as_target` accepts, so
# the row chooses between them and neither has to be guessed at. (Until the
# pool moved here this comment credited a `pick_miss`, which is not in the
# tree.)
MISS_SAY = (
    "I couldn't find anything useful for {q}.",
    "I couldn't find anything about {q}.",
    "Sorry, I couldn't find anything on {q}.",
    "Nothing useful about {q}, sorry.",
    "The text doesn't say anything about {q}.",
    "The text here doesn't mention {q}.",
    "I don't have anything useful on {q}.",
    "There's nothing about {q} here.",
    "Unfortunately there's nothing useful here about {q}.",
    # Short forms, for when the question will not fit. No `{q}`, so these are
    # one string each and carry no cardinality -- which is why they are the
    # fallback and not the pool.
    "I couldn't find anything useful here.",
    "Nothing useful here, sorry.",
    "There's nothing useful here.",
    "The text doesn't mention it.",
    "I couldn't find it in there.",
)
