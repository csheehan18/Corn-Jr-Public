"""The seven marker strings, spelled once.

A transcript is ordinary text with these in it, and `tokenizers/bpe8k.json`
holds each as one atomic special token. Their *ids* are fixed by the order of
`SPECIALS` below, which `corn/bpe.py` trains with: appending is safe,
reordering silently rewrites a trained vocabulary. HACKING.md §1 is why an
eighth is not a cheap change -- a new tokenizer file, and every checkpoint and
eval number incomparable with every other.

They lived in `corn/temporal.py`, the first slice that needed them, and were
spelled a second time in `bpe.SPECIALS` and a third in `socialgen`. Twenty
modules imported the date resolver to get five strings -- `tools`, `grammar`
and `toolspace` among them, for nothing else. `corn.temporal` still re-exports
the six turn markers, so the scripts that read them from there keep working;
new code imports them from here.

Nothing here may import anything: every other module in `corn/` can depend on
this one.
"""

from __future__ import annotations

# The document separator every `scripts/prepare_*` writes between documents.
STOP = "<|endoftext|>"

# The turn markers, in the order a transcript uses them.
D_DAY, D_USER, D_CALL, D_OBS, D_SAY, D_END = (
    "<|day|>", "<|user|>", "<|call|>", "<|obs|>", "<|say|>", "<|end|>",
)

# Order is fixed because it determines their ids. See the module docstring.
SPECIALS = (STOP, D_DAY, D_USER, D_CALL, D_OBS, D_SAY, D_END)
