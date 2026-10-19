# Copying fails to generalise because the training facts were memorisable

**Full result:** The copy discipline does not generalise, and the corpus is why

> **Superseded by the thirteenth finding, which acted on this one's diagnosis and reversed its
> headline.** Everything below stands as measured; what it could not know is that the cause it
> identifies is sufficient. Rebuilding the search index took `tool.copy` from 27/120 to
> **120/120** with no change to the model. Read this as the diagnosis and the thirteenth as the
> confirmation — "the copy discipline does not generalise" was true of this corpus and is not
> true of the tool.

`temporal.copy` is the row every conclusion in this project rests on. It reads **353/353** in
all three arms of the eleventh finding, as it has through templates, real web text,
retokenization, and four rival tools. DATA.md §11 has carried "still one tool" as the standing
caveat on it since the sixth finding, and the tenth finding shaped `web_search` to return an
`answer` field precisely so the same behaviour could be asked of a second tool. `tool.copy` is
that row: cut after `<|obs|>`, score the `<|say|>`, answers drawn from `HELD_OUT_FACTS` so a
correct one proves copying rather than knowing.

| | 0% tools | 0.61% tools | 15% tools |
|---|---|---|---|
| `temporal.copy` | 353/353 | **353/353** | **353/353** |
| `tool.copy` | 0/120 | **27/120** | **0/120** |
| | `malformed` 120 | `wrong_answer` 93 | `trained_answer` 52, `wrong_answer` 68 |

**The same checkpoint that defers to `resolve_date` 353 times out of 353 defers to
`web_search` 27 times out of 120 at best, and zero at worst.** The behaviour §4's whole
conclusion describes is not a disposition the model has. It is a thing it does with one tool.

The 0% arm's failure is the cleanest statement of the floor: asked what to say after a
`web_search` observation, it emits `<|call|>{"name": "recall_day", ...}` — the continuation the
*temporal* format taught it — 120 times out of 120. It has the script and applies it to the
wrong tool.

### The upsampled arm recites the training fact table

The 15% arm scores **zero**, and 52 of its 120 failures name a training answer outright:

    want  'Alexander Fleming'          got  <|say|>It's William Shakespeare.
    want  '3,422 degrees Celsius'      got  <|say|>It's Mount Everest, at 8,849 metres.
    want  'up to 3.5 metres'           got  <|say|>Looks like eleven a side on the pitch.

Every one of those is a `FACTS` entry, read straight out of the weights with the tool's answer
sitting in the prompt above it. This is the sixth finding's year-clamping again — a model
substituting the training distribution's value for the one it was handed — but total rather
than confined to one field, and it is the same memorisation that broke `send_text` in the
eleventh finding, showing up on a second row.

The direction is what makes it damning. The one-pass arm gets Kinshasa **20/20**; the
upsampled arm gets it **0/20**. More tool data, twenty-five times over, took a behaviour from
working to absent.

### The corpus cannot teach deference on this tool, and the arithmetic says so

The scored row is strict — it wants the tool's answer string, which is what the corpus always
writes. A softer reading, asking only whether the answer's distinctive token survived at all:

| | exact | content token only | neither |
|---|---|---|---|
| 0.61% | 27/120 | 26 | 67 |
| 15% | 0/120 | 2 | 118 |

Both readings agree, and the per-answer breakdown in the one-pass arm points at the cause:
Kinshasa 20/20, Alexander Fleming 7/20, and **0** for the three multi-word measurement answers
— `up to 3.5 metres` comes back as `about 3.5 metres`, `1,642 metres at its deepest` as
`1,642 metres.`. Partial copies, regenerated rather than transcribed.

Then the arithmetic. `data/raw/tools.txt` holds **3,000 search transcripts over 28 facts —
107 examples per fact, and 2,679 in the upsampled arm.** `web_search`'s answer is a
deterministic function of its query, and there are twenty-eight of them. **A model can score
100% on the training distribution of this tool without ever reading `<|obs|>`,** so nothing in
the corpus ever requires it to.

`resolve_date` is not like that, and not by luck. Its answer depends on the `<|day|>` anchor as
well as the utterance, and the anchors span 2020–2027 — so "last Tuesday" has no fixed answer
and the observation is the *only* place the date can come from. The temporal slice makes
deference load-bearing by construction. The tool slice made it optional, and the model took the
option.

**So this is a corpus defect, not a model result**, which is the useful form of the finding: it
predicts its own fix. Widen the answer space until the query stops determining the answer —
more facts than a model can memorise at the exposure the mix implies, or answers generated per
example rather than drawn from a table. Until then `tool.validity` and `tool.selection` are
measuring something the slice does teach, and `tool.copy` is measuring something it does not.

### What this costs the sixth finding, and what it does not

The sixth finding's ordering stands: pretrained 100% against 48–92% across six fine-tuned
checkpoints, on the same row, is unaffected by anything here. What narrows is the *claim*.
"Deferring to a tool over your own prior is the part that has to be there from the start"
should now read: deferring to `resolve_date` is. Whether that generalises is exactly what this
row was built to test, and the answer on the only second tool available is no — for a reason
that is about how the second tool's data was generated rather than about deference.

DATA.md §11 already recorded the analogous limit on `temporal.copy` itself — that its power
comes from the anchor year being out of distribution. This is the same lesson arriving from
the other side: **a copy row measures copying only where the answer could not have come from
anywhere else**, and that is a property of the training corpus, not of the eval.

**What this does not settle:** 25M parameters, and the one-pass arm is the only one that shows
the behaviour at all, at 22.5%. Whether a widened fact table gets `web_search` to
`resolve_date`'s 100%, or whether something about dates makes them uniquely copyable, needs the
corpus fix and a re-run — which is now a generation change and two training runs, not an
argument.
