# A copy-check bug refused answers like 'best-of-seven'

**Full result:** `grounded` strips frame words out of the middle of a span before testing that it is contiguous, so "best-of-seven" is tested as "best seven" and refused; on the whole-passage adapter that costs ten and seven right answers a seed against three on the window reader, and it is `READER-AUDIT.md` row 43 with its size measured

Replay, 2026-09-05, no GPU, both seeds, both readers. Found while asking
what `AGGREGATION` could mean on finding 112's harvests, where every
passage is one window and there is no vote to lose: all 16 / 10 of them
are passages where the head's span (or its extent-widened form) is handed
to `reduce` and `reduce` returns nothing, "no window extracted an answer",
because `corn.extract.grounded` refuses the reply.

## 0. The rule and the defect

`grounded` (corn/extract.py) accepts a reply if every content word is in
the window, the question, the source or `FRAME`; if at least one word is
*novel* (from the window and not the question); and if the novel words are
contiguous in the window:

    novel = [w for w in said if w in window_words and w not in question_words
             and w not in source_words and w not in FRAME]
    return len(set(novel)) == 1 or longest_span(" ".join(novel), window) >= 2

`FRAME` is the closed set of function words a framing may add, and it
holds `of`, `the`, `a`, `in`, `and`. So a span that carries one of those
*inside* it loses it before the contiguity test:

    reply                     said                      novel              tested as        passage says
    It's best-of-seven.       best of seven             best seven         "best seven"     best-of-seven
    It's Stephen A. Douglas.  stephen a douglas         stephen douglas    "stephen douglas" Stephen A. Douglas
    It's Coton in the Elms.   coton in the elms         coton elms         "coton elms"     Coton in the Elms

"best seven" is not a phrase the passage contains, and the right answer is
refused. Finding 85 counted this as "12 contiguity defect" among the 22
unwinnable passages on the window reader and the audit carries it as row
43, "contiguity repair in `grounded`", +3 / +3 right, open, the owner's.

## 1. The size, on both readers

The variant tested: contiguity measured over the reply's own words from
the first novel word to the last, frame words inside that span kept;
everything else in `grounded` unchanged (the no-invention test, the
novel-word requirement, the source and question exclusions). Bar
protocol, extent on, hybrid, each harvest at its own CV'd threshold,
paired by passage:

                     right        wrong        silent     u.silent   paired right      AGGREGATION
    W2 s1 (112)     513 -> 523   126 -> 127   82 -> 71   199 -> 198   +10 (p 0.021)    16 -> 2
    W2 s2 (112)     510 -> 517   123 -> 125   88 -> 79   199 -> 200    +7 (p 0.065)    10 -> 1
    shipped s1      389 -> 392   188 -> 192  144 -> 137  199 -> 199    +3 (p 0.25)     64 -> 61
    shipped s2      388 -> 391   172 -> 175  161 -> 155  196 -> 196    +3 (p 0.25)     50 -> 47

Correct silence is unchanged to a passage on every row. The shipped
reader's +3 / +3 is finding 85's number reproduced. **On the adapter the
same defect is worth three times as much**, because the adapter finds the
exact multi-word span far more often (`other` doubled in finding 112) and
those are the spans that carry a function word.

## 2. Why this is recorded and not applied

`grounded` is on the measurement path: `corn/evals.py` calls it inside the
extraction scorers (line ~2002), `corn/agent.py` uses it as the runtime's
acceptance test, and `corn/reader.py` and every probe read through it. A
change to it is rule 4's case — a scorer change that must re-score two
frozen checkpoints byte-identically before it merges, and here it would
not be byte-identical by construction, since the change is the point.
Finding 85 left the same repair to the owner for the same reason. What is
new is the price tag: **+10 / +7 on the reader that will ship**, pooled
+17 over 1,442 passages, and `AGGREGATION` on the adapter goes to 2 / 1.

Neither the head nor the adapter is touched by this; it is the runtime's
acceptance rule refusing what the head got right.

## 3. What it would take

A change to `corn.extract.grounded` (the `novel` slice replaced by the
span between the first and last novel word), the scorers re-scored on two
frozen checkpoints with the moved rows listed, and `scripts/check_extract.py`
extended with the three cases above as the regression. About an hour, no
GPU; the owner's decision under rule 4.
