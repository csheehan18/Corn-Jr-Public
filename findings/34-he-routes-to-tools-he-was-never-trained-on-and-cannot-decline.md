# Thirty-fourth finding — he routes to tools he was never trained on, and cannot decline

**Cost:** 0 s of new scoring on record; it reads 1 card scored for an earlier finding (`nano20m_v1`). Backfilled 2026-09-26 from the cards' `seconds`; training and probe time were never recorded, so this is a floor.

The thirty-third finding showed the *answer* half of a tool call surviving a tool the model has
never seen: an unseen name in `<|call|>` costs 3 of 300. The *choice* half was untestable,
because the runtime prompt is `<|user|>{text}` and nothing else — no declaration reaches the
model, so it cannot fail to route to a tool it was never told about. `corn/toolspace.py` puts
one there: a plain-text `tools:` line above `<|user|>`, no new marker, because `bpe8k.json` ships
seven specials and an eighth would make every checkpoint in the project incomparable.

Three arms, 29.6M, two seeds each, `scripts/score_toolspace.py`. The floor is measured rather
than assumed: `nano20m_v1` has never seen a declaration and reads **0/161** at every level.

| row | narrow ×2 | **wide ×2** | wide2 ×2 |
|---|---|---|---|
| `train` — the positive control | 230, 237 /332 | 207, 213 /329 | 167, 152 /262 |
| **`modifier` — held-out name** | **0, 0** /326 | **206, 203** /329 | 161, 162 /262 |
| `domain` — held-out everything | 0, 0 /329 | 1, 8 /325 | 0, 11 /255 |
| `absent` — nothing declared fits | 0, 0 | 0, 0 | 1, 5 /276 |

**`modifier` is the question and the wide arm answers it: 206 and 203, against its own
in-distribution control at 207 and 213.** Held-out equals trained, within two items on one seed
and ten on the other. Corn-Jr calls a tool declared only at inference at the same rate as one he
was trained on, and the name being novel costs nothing.

### The narrow arm read zero, and it is the control rather than a failure

`mix_v1_toolspace` reads **0/326 and 0/329** on both held-out levels. Across 1,310 held-out
items the emitted name appeared in the declaration **zero times**, the verb was right 78% and the
noun 84%, and a *trained* modifier was substituted every time: `find_meadow_harvest_route` came
back as `find_morning_route`. That is not a model limit, it is the corpus. The narrow slice gives
38,395 names at 17.3 uses each — which the design targeted — and builds them from **24 verbs, 16
nouns and 22 modifiers at 27,000–48,000 uses each**, which it did not.

**Name diversity is not token diversity.** The model learned sixty-two words and composed from
them, and never had to copy an unfamiliar string because no name it ever saw contained one. The
wide arm replaces the modifier with an invented word from `_invent_facts`'s prefix-free pool,
**partitioned** 18,000 trained / 4,500 held out so the two share a shape distribution and differ
only in which strings they hold — 162,027 names at **1.0 uses each**, modifiers at 58.7 against
48,088. Nothing else moves: same domains, verbs, values, frames, payload shape, share, and
`total_tokens` at `mix_v1`'s 130,279,711 in all three arms.

So this is the `sayvar` result a second time. A row at exactly zero across seeds and checkpoints,
looking like a capability limit, moved by changing one file. It is now the third instance of one
mechanism — `refusal.clarify` at 2,096 uses per sentence, this slice's parameter value at 2,130,
and its name tokens at 48,088 — and the generalisation is that **the thing the model must
reproduce needs cardinality, and counting the compositions hides that the parts have none.**

### What it reads is the name, not the description

`domain` stays at 1, 8, 0 and 11. That level moves the noun, the parameter, the value pool and
the utterance frames at once, so its failure has four candidate causes and **this arm separates
none of them** — it is not clean evidence that he cannot read a description. What can be said is
narrower and is what the `modifier` result already says: he identifies *which* declared tool to
use through vocabulary the corpus already contains, and copies its name faithfully once
identified. At `modifier` level a quarter of the losses pick the wrong *declared* tool rather
than mistyping the right one, and median similarity between emission and target is 0.56, so the
residue is selection rather than transcription.

### He cannot decline, and three corpus fixes did not touch it

`absent` — items where the asked-for tool is deliberately not declared — reads **0 in all twelve
cells** of the first two arms. Diagnosis found three genuine faults in how the slice asked: the
refusal was **one sentence at ~36,000 uses**, `absent` declared **2.51 tools against `route`'s
3.49** so the classes were separable by counting, and 18% is a share at which always-calling is
right 82% of the time. All three were fixed — 128 composed refusals at 163 uses each, 3.51
declared on both sides with matching per-count distributions, 34.7% absent.

**It moved `absent` from 0/142 to 1/276 and 5/276**, and left routing unharmed at 61–64%. That
is not a repair, and the reason is a mechanism none of the three fixes addressed: on `absent`
items he does not pick the nearest declared tool, he **invents a name that is in no declaration
at all** — 216 of 276 and 190 of 276, against 59 and 81 that picked a declared one. There is no
membership test to strengthen. The behaviour is generate-a-name-for-the-request, biased toward
the declaration when it happens to contain a match, and raising the price of a wrong call cannot
reach a decision the model never makes.

### What this means for the tool layer, and one thing it does not

VISION §6 says tools are cheap to add and means it about `REGISTRY`. Measured against the model,
it comes apart into three pieces, of which two now have numbers:

- **Read-back on a new tool is free** — the thirty-third finding, +0 across six checkpoints.
- **Routing to a new tool works** at the same rate as a trained one, provided the request maps to
  it through familiar vocabulary and the corpus taught name-copying rather than name-recall.
- **Declining does not work at all**, and is the gap a runtime has to close elsewhere.
  `corn/grammar.py` already constrains the emitted name to `REGISTRY`; constraining it to the
  *declared* set turns 78% of these failures into either a declared tool or no call. That is §6's
  schema-constrained decoding doing what it was specified for, needs no training run, and still
  does not produce a refusal — it prevents a call to a tool that does not exist.

### What this does not settle

- **Two seeds per arm**, and `absent` is a row whose floor is zero by construction — it cannot
  fall further, so the effect's *existence* needs no seed argument and its *size* has no interval.
- **Utterance variety is 274 across the whole slice**, and is not an axis any arm varies. Nothing
  here speaks to routing under paraphrase, which is the twenty-eighth finding's question.
- **The value row proves nothing and was built not to.** 77 strings at ~2,130 uses each, declared
  below floor in `scripts/check_copyable.py`; it reads perfect whenever the name is right, in
  every cell of every arm, which is what a recitable slot does.
- **Arms one and two are pinned to git, not to the file.** The refusal fixes changed what
  `generate` emits for every vocabulary, so their corpora regenerate only at `ec2b954` and its
  parent. `vocab` stayed switchable because it is an axis under study; the refusal design was not
  an axis, it was a bug.
