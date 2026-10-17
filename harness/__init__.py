"""Corn-Jr's harness -- everything that *runs* him, none of what made him.

This package exists to be a second repository one day. VISION §4 says the
shipped artefact goes to more than one person while a running instance is one
person's permanently, and the split this package prepares for is the code
version of that: **Corn-Jr's weights and harness go out, his training code does
not**. So the rule here is not tidiness, it is the boundary of what gets
published.

    corn/     the model, the corpus generators, the training loop, the evals.
              How he was made. Private.
    harness/  the server, the tool backends, the clients. How he is run.
              Public, alongside the weights.

**The dependency runs one way and only one way.** `harness/` may import from
the inference closure of `corn/` -- the twelve modules an inference process
actually needs -- and `corn/` may never import `harness/` at all. That is
asserted by `scripts/check_layering.py` rather than left to discipline, because
the property is currently true *by accident* and an accident is not a boundary.

The closure, computed rather than declared (see the guard):

    agent  bpe  config  daylog  decode  grammar
    model  sample  temporal  tokenizer  tools  toolspace

Nothing in it reaches `toolgen`, `train`, `evals`, `structured`, `chatgen`,
`data`, `bench`, `chat`, `copyaudit`, `toolvalues` or `trainbench`, which is the
whole training and measurement side. That the graph already separates is the
useful surprise; the guard is what stops the next import from un-separating it.

**One wrinkle, named because it will cost an afternoon later.** The module
boundary is clean and the *file* boundary is not. Four modules in the closure
serve both sides at once -- `tools.py`, `temporal.py`, `toolspace.py` and
`daylog.py` each hold runtime schema and executors next to the surface tables
and templates the generators draw on. Shipping them as they stand would publish
`FACTS`'s 8,697 entries and every phrasing template with the harness, which is
a meaningful part of how he was made. Splitting those four into a runtime half
and a generator half is the real cost of the repo split; everything else is
`git mv`. Nothing here does it, because doing it badly is worse than doing it
late.
"""
