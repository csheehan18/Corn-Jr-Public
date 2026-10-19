# Search returned 'capital punishment' for 'capital of Mongolia'; fixed

**Full result:** "capital of Mongolia" means capital punishment until the sort stops helping, and a surname counts toward its whole name

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`corn_jr_260m_ftextract`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The first live `--extract` session, 2026-08-27, and the two runtime repairs it
priced. `corn_jr_260m_ftextract` behind `harness.server --search --extract`,
real Wikipedia, four turns. No training run, no eval change: both defects and
both fixes live in `harness/backends/search.py` and `corn/extract.py`, which
no frozen scorecard reads.

## What the live session found: the failure is one link upstream of everything finding 65 measured

All four turns routed correctly — including the bare proper name that used to
degenerate into a run-on query — and none produced garbage. Two of them
answered the wrong page:

    what is the capital of Mongolia   ->  "Capital punishment, according to
                                           wikipedia.org."
    what is the capital of France     ->  the Capital punishment in France
                                           lead, deferred verbatim

Extraction never had a chance: the wrong *passage* arrived. Findings 55-65 are
all about link four; this is link two handing link four the wrong document,
which no amount of extraction quality can repair.

## The sort was the bug, measured at the API

`_wiki_search` ranked candidate titles by shared-term count, written for "the
boiling point of water" ranking High-altitude cooking first. Probed live
against the MediaWiki API on the four session queries, **the engine's own
first result was the right page four times out of four** — Ulaanbaatar,
List of capitals of France (Paris at rank 4), Icelandic króna, Boiling point —
and the shared-term sort is what inverted it:

    query                       engine rank 1        sort promoted
    the capital of Mongolia     Ulaanbaatar (0 shared)   Capital punishment in
                                                          Mongolia (2 shared)
    the currency of Iceland     Icelandic króna (0)      Economy of Iceland /
                                                          Crown (currency) (1)

"Icelandic króna" shares *zero* terms with "the currency of Iceland" under
exact set intersection — the answer page is routinely titled by the answer,
which the query's words cannot contain. And the coverage gate cannot save the
wrong page, because "capital" prefix-covers "Capital punishment".

**The repair is a demotion, not a smarter sort.** What separates the wrong
pages is not missing query words but *extra* ones: a title mixing the query's
terms with content words the query never said (Capital punishment in Mongolia,
Economy of Iceland, List of capitals of France) names a compound subject that
merely contains the asked-about words. Mixed titles go to the back of the
engine's own order; everything else stays where the engine put it. Demoted
rather than dropped, so a mixed title still answers when nothing cleaner
passes the lead gate — `scripts/check_search.py` asserts both directions. The
High-altitude cooking case needs no sort at all now: the lead-sentence gate
added since rejects it on its own. `srlimit` rises 3 → `MAX_RESULTS` (5)
because Paris is the engine's *fourth* result for "the capital of France",
behind three mixed titles.

After the change, live: **Ulaanbaatar. / Paris, according to wikipedia.org. /
The króna or krona is the currency of Iceland.** — all three property
questions correct on the same checkpoint, same day.

## The tally now knows a surname is its whole name, and what that cost was measured at zero

The handoff had already flagged `reduce`'s disagreement rule discarding a
correct extraction, and the live session reproduced the shape on its first
proper-name question. The specific defect: a reply "Alexander Fleming." keys
`alexander fleming` and a reply "Fleming." keys `fleming`, and the tally read
one fact as two — the exact whole-name-against-surname reading
`corn/extract.py`'s `_overlaps` documents, unused by the tally.

`_canonical` merges a key into the one maximal key that word-contains it. The
instrument is the `_span_key` docstring's, rebuilt over `data/raw/nq-dev.jsonl`
(721 answerable passages, replies in the corpus's own `SAY_ANSWER` framings),
merge off against merge on in one process:

    same fact framed differently agrees      131/343  ->  131/343   unchanged
    gold against a same-type rival agrees      0/606  ->    0/606   unchanged
    whole in one window, tail in another       4/206  ->   83/206   the buy

Of the 85 part-against-whole cases the locality gate admits at all, the merge
delivers 83; the other 121 fail identically with the merge off — they are
`property_local` (finding 66's rule) holding, not this change failing. The
answer returned carries the whole statement in every merged case, whichever
window said it. (The 131/343 same-fact rate is not comparable to the
`_span_key` docstring's 678/678: that measurement predates `property_local`
sitting in the reduce path, and the rate is identical in both arms here.)

**Two rules keep it honest, and the guard caught the first draft violating
one.** A key may only merge when every reply carrying it asserted exactly that
key — `_span_key` keys a truncated reply by the longest run a window actually
contains, so "It's the AFC NFL." over windows that only say "NFC NFL" keys
down to `nfl`, and the first draft merged it into `nfc nfl`, counting a
contradiction toward the fact it contradicts. `check_extract.py`'s NFC/AFC
case went red before the code ever ran live. And a part contained in two
different maximal keys — `fleming` against both `alexander fleming` and
`fleming institute` — stays its own group rather than guessing.

## What stands, deliberately

The live Ada Lovelace turn still falls back with `4 windows disagree
(augusta ada, lord byron, lovelace, ockham)` — `augusta ada` and `lovelace`
share no run, and merging them needs entity knowledge the conservative rule
refuses; the guard pins that as correct. For a bare "look up X" turn the lead
sentence *is* the right answer anyway; that the model then cut it to "Looks
like Augusta Ada." is a weights matter, not a runtime one. And
`property_local` treating question stopwords as pointing terms — "the" beside
"Nobel Prize" rejecting `alexander fleming`, hit while building the fixture —
is measured machinery (finding 70 scored with it) and is left for its own
measured cell.

## Artefacts

The guard additions are `scripts/check_search.py` (the Mongolia inversion and
the demoted-not-dropped case) and `scripts/check_extract.py` (the surname
merge, both reply orders, the no-shared-run abstention, the two-wholes
ambiguity, and the NFC/AFC truncation case). Both green, and the full sweep
with them. Session log rows for the before and after turns are in
`Saved Sessions/turns.jsonl`, 2026-08-27.
