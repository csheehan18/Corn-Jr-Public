# Live scorecards

What `harness/checkup.py`, `harness/converse.py`, `harness/searchgrid.py`,
`harness/toolgrid.py` and `tests/run_all.py` wrote, one file per run.

**`tests/run_all.py` is the odd one and writes `__boot.json`.** Everything else
here reports rates and exits 0; the boot suite is pass/fail, so its card
carries verdicts rather than proportions. It also carries `case_sha256`, which
is this folder's own missing field made concrete: a hash of the utterances the
run actually sent, so "the same instrument" stops being a claim about the
working tree and becomes something a reader can check. Two cards with different
hashes asked different questions and are not a before-and-after.

```bash
python -m harness.checkup --json harness/results/<checkpoint>.json
```

Naming follows `evals/results/`: `<checkpoint>.json` for the plain instance and
`<checkpoint>__<arm>.json` for one that changed a flag, so
`corn_jr_260m__nodecline.json` is the same weights with `decline` withheld.

## Why this is not `evals/results/`

**These two directories look alike and are not comparable, in either direction.**
`evals/` is frozen — a manifest, a `harness_version`, and a sha256 per file, so
two scorecards a month apart are two readings of one instrument. Nothing here is
frozen. `checkup.py`'s cases are a list of hand-written sentences in
`checkup.py`, and `converse.py`'s are conversations in `converse.py`; editing
either changes what a row means with nothing on disk recording that it changed.

`docs/LAYOUT.md` puts it as the rows being "deliberately named so they cannot be
quoted against `evals/`" — `routed` is not `tool.selection`, and the
fifty-first finding is what that distinction is worth: the same weights read
85.5% on `tool.selection` and 6/16 on `routed`, and the 48 points between them
were a policy the frozen set could not see.

**So the honest use of a file here is as a receipt for a finding**, not as a
series. Two of them are comparable when they were written by the same
`checkup/N` against an unedited case list, which is a claim about the working
tree rather than about the files, and is why a finding that quotes one says what
it ran.

## What is recoverable from a file, and what is not

`instance` is the part worth knowing about. It carries `decline`, `tools`,
`temperature`, `grammar`, `multi`, `copy`, `search`, `contacts` and the
checkpoint — every flag `harness/server.py` describes as changing what the
instance *is*. The two files here differ in `decline` and in the `tools` list it
produces, so the arms are told apart by their contents and not by their
filenames.

`harness` is a version string, `checkup/1`, bumped by hand. **It does not move
when a case is edited**, which is the one gap in the provenance above: a stale
artefact and a fresh one are indistinguishable if somebody rewrites a sentence
and leaves the version alone. That is the forty-sixth finding's shape — a guard
that reads the generator cannot see a stale artefact — and a fingerprint over
the case list is the fix, not built here.

`source` is the half of that gap which *can* be closed cheaply, and since
2026-08-26 every card carries it: `{"rev": ..., "dirty": ...}` for the tree the
harness ran from. It does not say which sentence was edited, but it says which
commit the case list came from and whether there were uncommitted edits on top
of it — which is exactly the "claim about the working tree" the paragraph above
says these files rest on. `docs/PLAN-P3-RULERS.md`'s fourth ground rule is why
it stopped being optional: numbers taken before that day's runtime changes are
not comparable with numbers after, and a card that cannot say which side of the
line it sits on cannot be used for a before-and-after at all. `dirty: true` is
not a warning about hygiene — those runtime changes lived in an uncommitted
tree, so `rev` alone would have named a parent commit that does not contain the
behaviour being measured.

`notes` and `log` point into a scratch directory rather than the repository.
That is deliberate and is the README's own instruction: both suites execute real
tools, so an instance under test writes its notes somewhere disposable. The
absolute paths are session junk and are kept rather than rewritten, because a
scorecard is a record of a run and not a description of one.
