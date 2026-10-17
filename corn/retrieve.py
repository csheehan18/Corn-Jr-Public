"""Pick the region of a document worth reading. The reading stays elsewhere.

`docs/PLAN-DOC-ANSWERS.md`'s first piece. A search passage is a few hundred
tokens and `corn.extract.read_passage` reads all of it; a paper is thousands,
and reading every window is neither fast nor useful. This module scores the
document's windows against the question, hands back one region centred on the
best of them, and refuses when the document does not speak to the question at
all. Extraction is untouched: what comes out of here goes into the same
`read_passage` a search result goes into.

Mirrors `corn/extract.py`'s design on purpose: pure functions, no model, no
tokenizer import -- `encode`/`decode` are passed in -- so every function here
is testable against canned text (`scripts/check_retrieve.py` does exactly
that, with no checkpoint anywhere near it). One chunking concept in the
codebase, not two: regions are cut at the extractor's own `WIDTH`/`STRIDE`,
because the region exists to be re-cut by the extractor and a second slicing
rule would let the two drift.

No stemming, no embeddings, no dependency -- `requirements.txt` does not
change, which `harness/protocol.py` makes a requirement of anything shipped
beside the weights. The measured cost of that choice is the plan's first
pre-registered failure mode: a question that says "results" misses a paper
that says "findings". That miss rate is the case for or against a v2
retriever, and it is to be measured, not patched here in advance.
"""

from __future__ import annotations

import math
import re

from .extract import FRAME, STRIDE, WIDTH, content_words

# **Region size: 512 tokens, and where the number comes from.** A3 measured
# sixteen windows as costing 25% more than one through `BatchedReader`; at
# width 64 / stride 32 a 512-token region cuts to ~15 windows, so the read
# stays inside the regime that measurement priced. Larger regions buy recall
# the reader then pays for in decode depth and middle-of-context loss
# (external research entry 10). The plan schedules a measurement at 256/512/
# 1024 on the dev set; until that exists this is the registered default, not
# a tuned one.
REGION = 512


def normalize(text: str) -> str:
    """Document text as the retriever and reader should see it.

    Deliberately small and testable, and every rule is an argument about
    tokens rather than about tidiness:

      * **whitespace collapses**, because a window cut across a line break is
        a window whose tokens are mostly formatting -- `_flat`'s argument in
        `harness/backends/search.py`, applied at load time.
      * **fenced code blocks drop**, because `bpe8k` was trained on prose and
        a code block inside a region spends the reader's fixed window on
        tokens that answer no question a person asks a paper.
      * **markdown link targets become their anchor text**, because a URL
        tokenizes into byte confetti that pollutes both the retrieval overlap
        and `grounded`'s allowed-word set -- an answer would be refused as
        invention for containing a word that only ever existed inside an
        href.
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    flat = " ".join(" ".join(out).split())
    # [anchor](target) -> anchor. Applied after flattening so a link broken
    # across lines is still one link. Non-greedy, no nesting: markdown's own
    # rule for the simple case, and the complex cases are rare enough that
    # leaving them alone beats guessing.
    flat = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", flat)
    # A bare URL outside link syntax is the same byte confetti without the
    # anchor to keep. Dropped whole.
    flat = re.sub(r"https?://\S+", "", flat)
    return " ".join(flat.split())


def _cut(ids: list[int], width: int, stride: int) -> list[tuple[int, int]]:
    """`(start, end)` spans over `ids`, the extractor's own overlap rule.

    The same arithmetic as `corn.extract.windows`, over spans rather than
    decoded strings, because the caller needs the winning window's *position*
    to centre a region on -- a decoded string has forgotten where it came
    from.
    """
    if not ids:
        return []
    if len(ids) <= width:
        return [(0, len(ids))]
    spans = [(start, start + width)
             for start in range(0, len(ids) - width + 1, stride)]
    if (len(ids) - width) % stride:
        spans.append((len(ids) - width, len(ids)))
    return spans


def _idf(window_words: list[set[str]]) -> dict[str, float]:
    """A word's weight is how few of the document's windows contain it.

    The document is its own corpus: "the" is in every window of any paper and
    weighs almost nothing, the entity the question actually names is in three
    and weighs the most. `log((N + 1) / df)` rather than the textbook
    `log(N / df)`, and the +1 is a measured repair, not smoothing by habit:
    the bare form gives a word in *every* window exactly zero, so a document
    of one window -- anything up to `WIDTH` tokens -- scored zero on every
    question and retrieved nothing at all. `scripts/check_retrieve.py`'s
    shorter-than-region cases are what caught it. A ubiquitous word now
    weighs a little rather than nothing, which is right anyway: retrieval's
    job is the argmax, and refusing is `answerable`'s.
    """
    n = len(window_words)
    counts: dict[str, int] = {}
    for words in window_words:
        for w in words:
            counts[w] = counts.get(w, 0) + 1
    return {w: math.log((n + 1) / df) for w, df in counts.items()}


def score(question: str, window: str,
          idf: dict[str, float] | None = None) -> float:
    """Lexical overlap of content words, IDF-weighted when weights exist.

    `FRAME` words come off the question first: "what is the melting point"
    should score on `melting` and `point`, not on `what` and `is`, which every
    window of English prose contains. Without an `idf` every surviving word
    weighs 1.0, which is the degenerate-but-correct form a caller with one
    window gets.
    """
    q = set(content_words(question)) - FRAME
    w = set(content_words(window))
    if idf is None:
        return float(len(q & w))
    return sum(idf.get(word, 0.0) for word in q & w)


def best_region(question: str, ids: list[int], decode,
                width: int = WIDTH, stride: int = STRIDE,
                region: int = REGION) -> tuple[str, float] | None:
    """The `region`-token slice of the document most worth reading, or `None`.

    Cut at the extractor's own width and stride, score every window, take the
    argmax, decode a `region`-token slice of the raw ids centred on the
    winner, clamped to the document. `None` when the document is empty or no
    window shares a single scored word with the question -- there is then no
    argmax worth centring on, and `answerable` below is about to say so
    anyway.

    The plan's signature carries an `encode`; this one does not, and the
    omission is deliberate rather than drift: the document arrives already
    encoded (`load` cuts and indexes once, at load time), the question is
    scored as words, and a parameter nothing reads is a parameter someone
    will eventually pass wrongly.
    """
    spans = _cut(ids, width, stride)
    if not spans:
        return None
    texts = [decode(list(ids[a:b])) for a, b in spans]
    words = [set(content_words(t)) for t in texts]
    idf = _idf(words)
    scores = [score(question, t, idf) for t in texts]
    best = max(range(len(spans)), key=lambda i: scores[i])
    if scores[best] <= 0.0:
        return None
    centre = (spans[best][0] + spans[best][1]) // 2
    lo = max(0, min(centre - region // 2, len(ids) - region))
    return decode(list(ids[lo:lo + region])), scores[best]


def answerable(question: str, passage: str) -> bool:
    """The refusal gate: does the document speak to the question at all?

    **A containment rule rather than a score threshold, because a threshold
    is tuning and a rule is a contract**: at least two distinct non-`FRAME`
    content words of the question must appear in the region, or one when the
    question has only one. Below that, the region is the least-irrelevant
    page of a document that does not answer, and the backend must say so
    instead of handing it to the reader -- the plan's second pre-registered
    failure mode is a weather question answered from a loaded paper, and this
    is the whole of the defence. If off-topic refusal is not near-total on
    the dev set, this rule is wrong and gets fixed *as a rule*, not tuned as
    a threshold.
    """
    q = set(content_words(question)) - FRAME
    if not q:
        return False
    hits = q & set(content_words(passage))
    return len(hits) >= min(2, len(q))
