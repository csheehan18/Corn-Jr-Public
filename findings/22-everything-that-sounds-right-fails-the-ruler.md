# Every conversation dataset fails a vocabulary test built from web text

**Full result:** Everything that sounds right fails the ruler, and the ruler came from web text

A fourth conversational candidate, measured the way the other three were: a million words at
three offsets, `scripts/vocab.py`'s word rule, turn length beside the two vocabulary numbers.
No GPU, no download into `data/raw` — a 40 MB range request against a 9.5 GB gzip stream,
decompressed to 127 MB in the scratchpad and thrown away.

### The licence was answered before the vocabulary, and it is a no

`DATA.md` §11 recorded OpenSubtitles as licence "unknown", which read like a gap in the mirror.
It is not. OPUS's own corpus metadata carries a `license` field and other corpora use it:

| corpus | `license` |
|---|---|
| `Tatoeba` | CC BY 2.0 FR |
| `WikiMatrix` | CC-BY-SA 4.0 |
| `TED2020` | a pointer to the TED Talks usage policy |
| **`OpenSubtitles`** | **absent — no `license`, no `copyright`** |

Eight top-level keys and neither is a licence. What it carries instead is a request — "Please,
add a link to http://www.opensubtitles.org/ to your website" — with the note "I promised this
when I got the data from the providers of that website". That is a personal undertaking passed
downstream rather than a grant of rights, and the "unknown" is faithful to upstream.

The two apparent escape hatches both close. `Helsinki-NLP/OpenSubtitles2024` is ODC-BY but is
the *benchmark* release: dev/test only, 2,022 bilingual pairs, no monolingual English, and its
own card says not to train on it. META-SHARE's CC-BY-NC-SA 3.0 record is NonCommercial plus
ShareAlike — a different class from every slice in the corpus today — and could not be verified
directly.

### It has the best register of any candidate and the vocabulary still fails

| candidate | licence | distinct | top-100 | median turn | p90 turn |
|---|---|---|---|---|---|
| web (FineWeb-Edu) — the bar | ODC-By | **42,755** | **43.2%** | — | — |
| `oasst1` (en) | Apache-2.0 | 31,693 | 45.2% | 11 | 50 |
| `ultrachat_200k` | MIT | 29,213 | 43.9% | 19 | **62** |
| OpenSubtitles v2024 en — 0 MB | **none** | 27,927 | 52.2% | **5** | **12** |
| OpenSubtitles v2024 en — 60 MB | **none** | 18,766 | 56.0% | **5** | **11** |
| OpenSubtitles v2024 en — 100 MB | **none** | 17,623 | 55.1% | **5** | **11** |
| `soda` | CC BY 4.0 | **15,942** | **64.2%** | 14 | 31 |
| narrative (TinyStories) — rejected at 47% | — | 6,863 | 63.1% | — | — |

Target was >30,000 distinct at ≤50% top-100. It misses both at every offset. Stripping the
bracketed production cues (`[laughing]`, `[Amy]`) moves distinct by 0.4% and top-100 by 0.6
points, so that judgement call is not carrying the result.

Two things worth recording that were not the question. **It is not stable across offsets and
SODA was** — 27,927 / 18,766 / 17,623 against SODA's 15,669 / 15,942 / 16,318 — and the text
says why: offset 0 is contemporary reality television and 60/100/120 MB are all classic-era
film, so era varies with position and no single sample characterises the corpus. Running the
three-offset protocol is what turned that up. And **turn length is the best of any candidate by
a factor of three**, median 5 against SODA's 14 and UltraChat's 19, with the caveat that an
OPUS mono line is a subtitle *cue* and part of that 5 is display segmentation.

### Four candidates now, and they are ordered rather than scattered

- **Written assistant prose** — oasst1, UltraChat — passes vocabulary, fails register.
- **Model-generated dialogue** — SODA — fails both.
- **Scripted speech** — OpenSubtitles — best register of the four, fails vocabulary.

**The closer a candidate gets to real speech, the worse it does on §5.0's ruler.** Three
candidates made that look like bad luck; the fourth makes it look like a property of speech.
And it is a prediction about where §11 has been pointing: Switchboard, Fisher and CALLHOME are
*spontaneous* speech, and spontaneous speech has a smaller vocabulary than scripted speech, not
a larger one. **The LDC-paid route is now predicted to fail the same bar and to fail it
harder** — so buying it on the argument currently recorded would be paying for a corpus this
project's own ruler rejects. That is worth knowing for the price of a 40 MB range request.

### So the next question is about the ruler

§5.0's bar was read off written web text and applied unchanged to a slice whose job is
register. If every source with spoken register fails it and every source that passes it is
written prose, the ruler is a candidate for being wrong before the search is. Three checks,
none needing new data: restate the bar **per share** rather than per slice, since TinyStories
was rejected at 47% of the corpus and a 20% slice at 55% top-100 beside a 40% web slice at
43.2% has never been arithmetic anyone did; point `vocab.py` at a **blend** rather than a slice,
since the number the model actually sees is unmeasured for every corpus in the project; and
check whether the two numbers **predict anything downstream**, where the sixteenth finding's
"corpus diversity does not predict `variety.distinct3`" is the only evidence either way and
points at no.

If the bar does not survive being restated, the conversational search is unblocked without
sourcing anything — and SODA, which is right-register, freely licensed under CC BY 4.0 and was
rejected on this bar alone, becomes the cheapest arm available.

### What this does not say

It does not say OpenSubtitles would train badly; nothing here is a training run, and §5.0's
numbers have never been shown to predict a model result. It says the corpus cannot be used —
that part is the licence and is not a judgement call — and that the *measurement* which would
have justified pursuing it fails too, in a direction that generalises to the sources behind it.
And it is scripted speech, so the ASR-shape question is still untouched: nothing measured so
far is spontaneous or disfluent.
