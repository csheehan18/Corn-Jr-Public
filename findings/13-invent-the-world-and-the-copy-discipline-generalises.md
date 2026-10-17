# Thirteenth finding — invent the world, and the copy discipline generalises

The twelfth finding diagnosed `tool.copy` 0/120 as a corpus defect rather than a model result:
`web_search`'s answer was a function of its query over 28 hand-written facts, 107 training
examples each, so nothing ever required reading `<|obs|>`. That is a falsifiable claim, and the
fix is the test of it. `corn/tools.py` now **invents** the search index — ~8,700 facts over
twelve families — and `data/raw/tools.txt` is regenerated at the same 10,000 examples, so the
answer space is the only thing that moved.

| | hand-written | invented |
|---|---|---|
| distinct facts | 28 | **8,697** |
| training examples per fact | 107.1 | **1.62** |
| distinct utterances in the slice | 6,470 | 7,756 |

Same eval set, same sha256, same 130,279,711 tokens, same 5,237 iterations, same tokenizer.

| row | facts28 0.61% | facts28 15% | **invented 0.61%**<br>ckpt / last | **invented 15%**<br>ckpt / last |
|---|---|---|---|---|
| `tool.copy` | 27/120 | 0/120 | **120/120 / 120/120** | 98/120 / 113/120 |
| `tool.validity` | 167/181 | 155/181 | **175/181** / 174/181 | 173/181 / 173/181 |
| `tool.selection` | 146/200 | 172/200 | 148/200 / 116/200 | **182/200** / 182/200 |
| `temporal.copy` | 353/353 | 353/353 | 353/353 | 353/353 |
| `narrative` nats/byte | 0.3666 | 0.3724 | 0.3665 / **0.3661** | 0.3725 / 0.3716 |
| `web` nats/byte | 0.9099 | 0.9216 | 0.9098 / **0.9089** | 0.9212 / 0.9203 |

**120/120, with an empty failure table.** `temporal.copy` and `tool.copy` are both at ceiling
on the same checkpoint, which is what "the discipline generalises" has to mean, and the
"still one tool" caveat carried since the sixth finding is discharged. Nothing about the model
changed — the language-modelling rows are flat to the fourth decimal (0.3666 → 0.3665). What
changed is that the corpus stopped answering the question for him.

**`trained_answer` is now zero everywhere**, which is the mechanism confirmed from the other
side. The upsampled arm's 22 and 7 remaining failures are ordinary `wrong_answer`: there is no
memorisable table left to recite, so the specific pathology the twelfth finding caught —
`William Shakespeare` when the tool had said `Alexander Fleming` — has no way to occur. The
eleventh finding's `send_text` collapse also improved, `missing:message` 16 → 5.

### Repetition still costs something, and it is no longer the same something

The one-pass arm is perfect; the 15% arm, reading **the same corpus 24 times**, is the only arm
that fails the row at all. So upsampling is still not free, but the old explanation is gone
with the old table. Whether the residue is repetition or capacity is the confound the eleventh
finding named and this run does not break — a bigger *distinct* slice at a fixed 15% is the
experiment, and it needs the sentences §11 still has no source for.

### Three bugs, all caught by guards rather than by the training run

Writing the checks before the corpus is what made the fix survivable. None of these would have
raised an error; each would have produced a number.

- **An answer equal to its own query.** Pools were drawn independently from one name space, so
  the same string landed in two of them: `the capital of Belaburg -> Belaburg`. That restores
  the exact property the rebuild exists to remove. Fixed by carving disjoint pools from one
  prefix-free master list.
- **A generated answer colliding with the holdout.** Lake depths draw from [120, 1990] and
  `HELD_OUT_FACTS` says Baikal is `1,642 metres at its deepest` — which the generator produced
  on its first run. A model could then learn that string in training and **pass** the Baikal
  item without reading anything, a false positive on the one row built to detect exactly that.
- **Pattern prefixes.** `web_search_tool` matches with `p in q or q in p`, so `the capital of
  Bela` swallows `the capital of Belaria` and the tool answers by table order rather than by
  query.

An audit of the *old* tables came back clean on all three axes, which is worth recording: the
twelfth finding really was about the size of the answer space and not a lookup bug.
`check_tools.py` now asserts all of it, **including the exposures-per-fact ratio itself** — if a
later edit pushes 1.6 back toward 107, the guard fails rather than the finding quietly
reversing.

A fourth defect was subtler and is the one worth remembering. The group-12 checks pinned the
word-boundary rule with the literals `"It's Paris."` and `"It's 6."`. When `FACTS` became
generated those strings stopped being training answers, and the checks failed — correctly, but
the lesson is the near miss: **a check that hardcodes its fixtures silently stops testing what
it names.** Had those literals happened to stay valid, the checks would have kept passing while
asserting nothing. They now draw from the live table, longest answer for the recitation case
and shortest for the boundary case, since the shortest is the one most able to appear inside
another string by accident.

### The selection rule lost its first real test, inside its own noise

This is the first pair where `ckpt.pt` and `last.pt` are different files, so §11's standing
question — how often do the rule and the ruler disagree — finally has an answer. The rule picked
iter 5,125 in both arms; the blended `val` preferred 5,237; the frozen set prefers **5,237 on
all three lm rows in the one-pass arm and two of three in the upsampled one**. The blended val
agreed with the ruler and the stratified rule did not, which is the reverse of the seventh
finding that motivated the rule.

The margins are the whole story. The rule preferred 5,125 by **0.0079 and 0.0009** — 0.79% and
0.09% relative, against its own measured relative noise of **0.94%**. Both disagreements
happened inside the noise floor, so the rule is not choosing badly; it is choosing at a
resolution it does not have. And val cannot see what actually moved: `tool.selection` went
**148 → 116** across those same 112 iterations, `chose_resolve_date` 19 → 56, while every
per-source loss stayed flat to three decimals. Behaviour is not a smooth function of validation
loss at the tail of a cosine schedule, and no val-based rule will fix that.

**What this does not settle:** one pair at one scale, and `tool.selection`'s 32-point swing
between adjacent checkpoints is itself a warning that some of these rows are noisier than the
differences being read off them. The 0.61% arm's selection number should be treated as a band,
not a point.
