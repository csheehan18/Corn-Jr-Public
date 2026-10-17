# Seventy-ninth finding — a quarter of what clears the coverage bar clears it on a first letter, and the path that runs first has no bar at all

A reduction-path audit rather than a training run, and it started from one
question a user asked and Corn-Jr could not answer: **"who won the 2026 super
bowl?"** Everything below is `harness/backends/search.py` measured on
2026-08-29 against the live providers, plus offline pricing over NQ dev; the
weights are not involved anywhere in it and were never run. Four results, two
repaired here, two characterised and left for the owner because they are
decisions rather than defects.

The finding under all four: **`_covers` measures term *presence*, not
answerhood**, and every guard in the file is a hand-written rejection of one
more shape that mentions the subject without answering. Findings 72 and 78 each
added one. This adds two more and then finds the bar itself leaking.

---

## 1. The phrasing gap has a second half, and it is the scorer rather than the provider

Finding 78 measured natural question 1 of 8 against noun phrase 5 of 8 and
concluded the *provider* wants a noun phrase. On the Super Bowl question the
provider wanted nothing of the kind: the results page returned ten results and
the rank-1 result **was** the answer —

    The Seattle Seahawks defeated the New England Patriots Sunday to win the
    2026 Super Bowl.

— which passes `_answers` and `_prose` and then scores **0.75**. `MIN_COVER` is
1.0, so the right answer at rank 1 was discarded and the user was told nothing
was found. The missing term is `won`: the snippet says "to win", and the
four-character prefix rule cannot bridge `won` to `win`. Asked as *the winner of
the 2026 super bowl* the same snippet scores **1.00** — `winner` reaches `win`
through the rule's other side — and the same second returns the same sentence.

So the reformulation is not only about what the provider will match. It has to
produce a query whose terms **the answer sentence will contain**, and those are
two different objectives that happen to have agreed until now. Repaired as one
`_REPHRASE` row, `who won X` to `the winner of X`, because that is the shape
every row above it already has.

**And the bar is not what is wrong.** `MIN_COVER` at 1.0 is what stopped him
inventing a height for Everest out of a snippet that mentioned neither; lowering
it to 0.75 would have bought this one query by loosening every query on the
machine.

## 2. The teaser wearing a noun phrase, and the tie the scorer cannot break

The rewrite fixed the query and immediately exposed the next shape. Re-measured
an hour later, with the ranking moved, `the winner of the 2026 super bowl`
returned an index page's own title at rank 1 and the real answer at rank 2:

| rank | cover | snippet |
|---|---|---|
| 1 | **1.00** | Complete list of Super Bowl winners 1967- 2026. |
| 2 | **1.00** | The Seattle Seahawks defeated the New England Patriots Sunday to win the 2026 Super Bowl. |

A list page is titled with the thing it lists, so it covers every term asked
about and carries no fact. `_covers` cannot separate the two, `_ddg_html` keeps
a candidate on strictly-greater, and the tie therefore goes to the engine's
ordering — the promise beat the fact, and the runtime would have read a table of
contents out loud. `_prose` does not catch it (`of` is a stop word inside the
first ten tokens) and it has no finite verb, which is the signal that would
catch it in general and a larger claim than one measurement supports.

Repaired as a branch of `_TEASER`, which is already the home for "a promise that
the page will answer". Anchored, so the prose that *introduces* a list survives
— "This is a list of the senators…" is a real sentence and is NQ dev's own
shape. **Priced the way `_prose` was, over every sentence of every NQ dev
passage (3,615 sentences, `_sentences`' own cut): 0 refused (0.00%)**, no
overlap with the openers already there. The honest limit on that number: NQ dev
is Wikipedia prose, the population this branch is least likely to fire on, so it
bounds the false-positive cost and does not measure how much furniture the
branch catches.

## 3. The bar clears a quarter of its traffic on a first letter

`_terms` glues a lone character onto the term in front of it — the sixth saved
session's `space x` repair — so **no query term is ever shorter than two
characters**. `_covers` built the other side with a bare regex and no such
treatment, which makes `w.startswith(h[:4])` with a one-character `h` mean
nothing more than "same first letter". English writes those constantly: the
possessive `s`, the article `a`.

Live, `what does DNA stand for` scored a perfect **1.00** against

    DNA profiling is the process of determining an individual's
    deoxyribonucleic acid (DNA) characteristics.

where `stand` was matched by the `s` of "individual's". Any query term beginning
with `a` was effectively free.

**Priced over NQ dev's answerable half:** 721 items, 2,581 question/sentence
pairs, **89 of which clear `MIN_COVER` today. 23 stop clearing it (25.8%), and
12 of those carry the gold answer.** The twelve look like a cost and are not:
every one of the 23 was passing on a first-letter coincidence —

| query term | rescued by |
|---|---|
| `author`, `arrived`, `about`, `architecture`, `add` | `a` |
| `sang`, `said`, `separate`, `spelling`, `south` | `s` |
| `meninges` | `m` |
| `name` | `n` |

— so the twelve were answer-bearing sentences that **do not mention what was
asked about**, which is exactly the text the Everest comment refuses to serve.
Losing them is the bar working; keeping them was luck. Repaired by dropping
one-character tokens from the snippet side. Gluing them the way `_terms` does is
the symmetric alternative and was measured too — it rejects 3 more and bundles
stop-word removal on that side, which nothing motivates. `_covers_exact` needs
no change: it tests membership, so a one-character token can only match a
one-character term and there are none.

## 4. Characterised, not repaired: the guards are all on the door that runs second

`_answers`, `_prose` and `MIN_COVER` are scoped to `_ddg_html`. The abstract
providers — `_ddg`, `_wiki`, `_wiki_search`, which run **first** — have no bar at
all: `_best_answer` keeps the best-covering sentence it can find *within the
abstract* and floors to the lead when nothing covers, and it never rejects. The
file's header argues the abstract is "closer to what the model was trained to
read back", and that is true of an **entity** query. A question-shaped query that
merely names an entity gets that entity's lead regardless of whether the lead
answers the question.

Eight ordinary questions, live, one run:

| query | outcome | cover |
|---|---|---|
| when did Elvis Presley die | correct | — |
| who owns Twitter | Jack Dorsey's lead, served as the answer | 0.50 |
| what does DNA stand for | "DNA profiling is the process of…" | 1.00 (§3's leak) |
| why is the sky blue | a diffuse-sky-radiation fragment | 0.50 |
| how many people live in Tokyo | an urban-sprawl sentence, no number | 0.25 |
| what team does Lionel Messi play for | `no_results` | — |
| how much is a Tesla Model 3 | `no_results` | — |
| who plays Hermione in Harry Potter | `no_results` | — |

**One right, three honest misses, four confident non-answers.** Three of the four
would have been rejected as `no_results` had they arrived one provider later,
and `no_results` is the trained shape he says perfectly. This is VISION §9's
failure with the guard on the wrong door, and the repair — applying `MIN_COVER`
to the abstract path — is a behaviour change with a scorecard cost rather than a
bug fix, so it is the owner's and is not taken here.

## 5. Characterised, not repaired: the rewrite table fails its own answers

§1's mechanism is general. A `_REPHRASE` row turns an interrogative *verb* into a
*noun*, and the answer sentence uses the verb. Against a plausible answer
sentence for each, **8 of 9 rows produce a query that would be rejected**:

| rewritten to | cover | why |
|---|---|---|
| the birth date of ada lovelace | 0.50 | `birth` does not reach `born`; `date` is not in the sentence |
| the height of mount everest | 0.67 | `heig` against `high` |
| the author of pride and prejudice | 0.67 | `author` does not reach `written` |
| the depth of the mariana trench | 0.67 | `dept` against `deep` |
| the location of machu picchu | 0.67 | `location` does not reach `sits` |
| the inventor of the telephone | 1.00 | the only row that survives |

The `_WHEN_EVENT` rows are worse than the rest because they *introduce* a term:
"the date X was built" asks for `date`, which the sentence stating the date
usually does not contain.

This is latent today only because §4's abstract path floors instead of
rejecting. It goes live the moment a query falls through to snippets — recent
and non-encyclopedic facts, which is precisely where search earns its keep,
because the weights have nothing there. Repairing it means either bridging
inflection in `_covers` (a stemmer this file will not carry a dependency for) or
choosing rewrite targets by what answers look like rather than by what reads as
a noun phrase. Both are corpus-free and neither is obvious.

## 6. The tail, and one row that is simply wrong

Sixteen ordinary openers put at `strip_affixes` and `_rephrased`: **14 reach the
provider unchanged and still a question** — `when did X die`, `who plays X`,
`how much is X`, `what team does X play for`, `who owns X`, `when is the next X`,
`what does X stand for`, `why is X`. Three of §4's live misses are exactly these.
The table is a table and the file says so; this measures how long the tail is.

And one existing row is producing ungrammatical output:

    how many people live in Tokyo  ->  "the number of people live in tokyo"

because `^how many (.+?) (?:are there )?in (.+)$` stops its non-greedy group at
the first " in ".

## Limits

n=8 on the live battery, one run, and **DuckDuckGo's ranking moved under this
audit within an hour** — §2 exists because the same query returned a different
rank-1 between two measurements. Those are directions, not rates. The NQ dev
pricing is Wikipedia prose and answerable items only. "Carries the gold answer"
in §3 is a proxy for "would have answered" and conflates a sentence that answers
with a sentence that merely contains the string. Nothing here was measured
against the model: every number is the backend's, and what the 260M does with a
better or worse payload is finding 77's scorecard and not this.

## What moved

`harness/backends/search.py`: one `_REPHRASE` row (§1), one `_TEASER` branch
(§2), one-character tokens dropped from `_covers`' snippet side (§3).
`scripts/check_search.py` carries nine new rows, including the ordering
assertion for §2 written in rank order because the ordering is the claim.
`scripts/check_all.py`: 49 ran, 0 failed, 0 skipped.

## §4 is repaired, 2026-08-31 — and the repair is a hold, because the bar was priced and refused

**The owner took the decision §4 left, and the pricing overturned the repair
§4 assumed.** Applying the snippet bar to the abstract path was simulated
over NQ dev (1,003 rows: 721 answerable, 282 unanswerable; passage standing
in for the abstract, question through `strip_affixes`, `_best_answer`
picking):

    gate                          kept  spent  served_non  refused_non
    status quo (floor to lead)     620      0         383            0
    `_answers` only                619      1         383            0
    `_answers` + covers >= 0.5     493    127         295           88
    the full snippet bar (1.0)      92    528          42          341

**The full bar spends 528 of 620 true answers to refuse 341 of 383
non-answers.** Abstract prose answers questions without echoing them — "The
United States Senate consists of 100 members" fails full coverage for "how
many senators are there" — so the 2026-08-26 reversion in `_ddg` was this
same fact met live, and no rejecting threshold prices acceptably.

**What shipped instead: hold-and-continue** (`HOLD_COVER = 0.5`,
`_lookup`). An abstract pick that fails `_answers` or covers half the query
or less is *held* — the barred providers behind get their chance, then the
reformulation retry gets its chance — and served untouched when nothing
clears. Nothing is ever discarded, so the spent column is zero by
construction; the cost is extra fetches (212 of 620 true abstract answers
would be held-and-still-served on NQ) and the gain is a second chance for
112 of 282 unanswerable picks. The three scored non-answers in §4's battery
sat at 0.50, 0.50 and 0.25, which is why the line is ≤ 0.5.

**The battery, re-run live under the hold (n=1, same drift caveat):**

    old:  1 right, 3 honest misses, 4 confident non-answers
    new:  3 right, 4 honest misses, 1 held floor

Tokyo is the compound win — the hold plus §5's `population` row lands
"Tokyo's 2026 population is now estimated at 10,316,210" where the old read
served a sprawl sentence with no number. Messi answers from the lead. DNA
and sky-blue fall to honest `no_results`. "Who owns Twitter" is the named
residual: the Dorsey lead is held, nothing behind it clears, and the floor
serves it — a suspected non-answer, served last instead of first, which is
the exact trade the pricing bought. The full-coverage wrong-subject shape
(§3's DNA case) remains the residual no coverage signal can catch.

**§5's general repair is still open, and it now has a named direction.**
The Tokyo row shipped (`how many people live in X` → `the population of X`,
placed above the count row that rode the verb into the noun slot). The
other eight rows still produce queries their own answer sentences fail, and
the direction worth pricing next is *either-phrasing coverage* — scoring a
candidate against the original query's terms as well as the rewrite's,
since the two are the same question and the original's verbs (`born`,
`wrote`, `won`) are often exactly what the answer sentence carries. That
changes scoring plumbing inside the providers and wants its own NQ pricing
before it ships; nothing here licenses it.

`scripts/check_search.py` §4b holds the hold's four properties (a weak
abstract lets a covering snippet answer; with nothing behind it is served,
not spent; a covering abstract answers immediately with no extra fetches; a
question-shaped abstract is held whatever it covers), and §8b gained the
weak-hit-lets-the-retry-improve-it row beside the covering-hit-answers-
without-reformulating one.
