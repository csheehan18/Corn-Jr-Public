# Fifty-eighth finding — the corpus was not the prior, and tripling the type share moved it by nothing

**Cost:** 7.0 min of scoring on the 2 cards first cited here (`nano20m_v3_extract_narrowtype`, `nano20m_v3_extract_widetype`); it also reads 1 card scored for an earlier finding (`nano20m_v3_extract`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

`configs/nano20m_v3_extract_widetype.py` ×2 against
`configs/nano20m_v3_extract_narrowtype.py` ×2. One variable: `corn/tools.py`'s
`FACTS` gains 3,000 composed `other`-typed facts, and the tools slice is
regenerated from it. Every other share is `mix_v3_extract` verbatim to the
token. Trained 2026-08-25, 1,136s per seed, four runs.

**This is a pre-registered null and the threshold was written down before the
numbers existed.** `docs/PLAN-WEB-SEARCH.md` §WS-E, registered before the
corpora were built: primary read is the `other` decline rate, 91.7% → 70% or
below; honest null is **still at or above 85% ⇒ corpus type-frequency is not
the cause and the line retires**.

## The dose

The fifty-seventh finding's probe found the arm declining on 91.7% of the
answerable windows whose gold is an `other` — no digit, no leading capital —
against about half of names and numbers, identically across both seeds and flat
in gold position. The extraction slice was not the suspect: it carries `other`
at 20.6% against the eval's 18.0%. `FACTS` was, at 89.7% name-or-number, being
what follows a `web_search` `answer` field everywhere else in the corpus.

    FACTS            before  8,697   name 27.6%  number 62.1%  other 10.3%
                     after  11,697   name 20.5%  number 46.1%  other 33.3%

    as it lands in   narrow          name 28.4%  number 61.3%  other 10.3%
    the corpus       wide            name 20.9%  number 45.8%  other 33.2%

A 3.2× dose, confirmed on the artefact rather than on the table it came from.

## The null

Decline rate on the answerable half, by gold answer type, `corn.evals._is_miss`
on the retained reply:

| type | ctl s1 | ctl s2 | arm s1 | arm s2 |
|---|---|---|---|---|
| `other` | 86.1% (31/36) | 86.1% (31/36) | **88.9% (32/36)** | **91.7% (33/36)** |
| `number` | 56.8% | 77.3% | 68.2% | 45.5% |
| `name` | 56.7% | 64.2% | 63.3% | 40.0% |

**Both arm seeds sit above the 85% null line, and the arm is not lower than the
control — it is marginally higher.** Tripling the share of `other` answers in
the corpus moved the rate the intervention was aimed at by nothing.

## What replicates is the phenomenon, not the explanation

Across all six runs on this eval — the two WS-B pilots and these four —
`other` decline never leaves the 86–92% band:

    PILOT s1  91.7%   PILOT s2  91.7%
    ctl s1    86.1%   ctl s2    86.1%
    arm s1    88.9%   arm s2    91.7%

while `name` and `number` swing between 40.0% and 77.3% on the seed alone. So
the type asymmetry is about as stable as anything measured in this project, and
it is **not driven by the answer-type frequency of the corpus it was trained
on**. The seventeenth finding's warning applies to the other two types rather
than to this one: the rows that move on the seed are the ones that look
responsive.

## The aggregate rows do not separate, and could not have

| row | ctl ×2 | arm ×2 | |
|---|---|---|---|
| `extract.span` | 25-33/200 | 23-35/200 | overlapping |
| `extract.abstain` | 152-156/200 | 130-172/200 | arm encloses control |
| `extract.brevity` | 397-399/400 | 393-399/400 | overlapping |

**On every extraction row the within-arm seed spread exceeds any arm-control
gap** — the arm's two seeds differ by 12 items on `extract.span` and 42 on
`extract.abstain`. Ground rule 6 says quote directions and not sizes unless the
ranges separate by more than the within-arm spread, and they do not, so nothing
further is readable here. This is the thirtieth finding's rule doing the work it
exists for: a shared floor would have made one of these four look like a result.

## The regression watch is clean

| row | ctl ×2 | arm ×2 |
|---|---|---|
| `tool.copy` | 120-120/120 | 118-120/120 |
| `tool.copy_wide` | 275-297/300 | 289-297/300 |
| `temporal.copy` | 352-353/353 | 353-353/353 |

`FACTS` is the table `tool.copy` copies from and it grew by 3,000 rows, so this
row was the change's registered risk. It did not fall: the one 118 is two items
on a row whose effective resolution is about twenty, and the lowest
`tool.copy_wide` in the set belongs to a **control** seed.

**And the fifty-seventh finding's unresolved 20-item `tool.copy` fall did not
reproduce.** The pilot read 100/120 on one seed and 120/120 on the other, which
two seeds could not separate into wobble or trend. Four further runs on the same
row read 118-120. That is weak evidence for wobble, not proof, and it is worth
exactly what four more seeds are worth on a row with six effective facts in it.

## What this retires, and what it leaves standing

**Retired:** the hypothesis that the `other` prior comes from the answer-type
frequency of the corpus. A 3.2× dose on the largest carrier of that frequency
is a strong enough test that a second, larger dose is not the next move. The
sibling proposal — oversampling `other` inside the extraction slice — is
retired with it and for the same reason: it was the twenty-third finding's shape
even before this, and now there is no mechanism for it to act through.

**Standing:** `extract.abstain`'s vocabulary gate, the fifty-sixth finding's
third premise — the eval row bounds what the slice is allowed to teach. That is
a slice-side and scorer-side hypothesis rather than a corpus-side one, and it is
where WS-E's failure points.

**The 260M stays gated**, and for a better reason than before. The execution
order said not to spend 2.5 days until the abstention question had an answer. It
has one: not the corpus. Seventy-seven minutes of nano time retired a hypothesis
that would otherwise have been carried into a run measured in days.

## Two things about the method, which cost more than the result did

**The pilot could not be reused as the control, and finding that out was the
expensive part.** The first design read the arm against `nano20m_v3_extract` ×2
on the grounds that it differs only in the fact table. It does not:
`data/raw/tools_names.txt` was built 2026-08-18, before the escalation tool
existed, and carries **zero** escalation transcripts against the ~605 today's
generator emits — 6% of the slice. An arm read against it would have varied the
fact table and the tool inventory together and separated neither. The check that
caught it is cheap and belongs on any reused corpus: **regenerate the file from
`HEAD` and compare it to the copy on disk.** It did not reproduce, and the
reason was not the seed.

**The isolation was verified on the artefact, not argued from the config.** The
two mixes were compared stream by stream after `prepare_mix`:

    val_chat, conversational, extract, narrative,
    structured, temporal, toolspace, web          8 byte-identical
    val_tools                                     1 differing

Eight of nine validation streams hash the same across the pair. Whatever these
four runs read, it is not a share that drifted somewhere else.

## A denominator this arm's own pre-registration got wrong

`extract.abstain` is scored out of **200**, not 400; `extract.brevity` is the
/400 row. **The fifty-seventh finding and the handoff both had it right** -- the
error was introduced when WS-E was registered, and it propagated to
`PLAN-WEB-SEARCH.md`, `HANDOFF.md` and both mix configs as `140-158/400` with a
guard at `120/400`. Corrected in all four places.

No reading changes, which is the only reason this is a footnote rather than a
retraction: the guard was an absolute count either way and the arm's 130-172
clears it. Worth recording because a wrong denominator in a *pre-registration*
is the kind of error that is invisible until the result arrives and then looks
like a moved goalpost.
