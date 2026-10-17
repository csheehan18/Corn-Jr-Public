"""Tokenizers.

Starting at byte level is a deliberate non-decision. Vocab 256 means the
embedding table is ~0.03% of the parameter budget instead of ~10%, and it means
there is no tokenizer training step standing between an empty repo and a
running training loop.

The interface below is the contract a BPE has to satisfy later, so that
swapping it is a config change and a re-run of `prepare`, not a rewrite.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol, Sequence


class Tokenizer(Protocol):
    name: str
    vocab_size: int
    # An opaque identity for the *mapping*, not the file it came from. Two
    # tokenizers that assign the same ids to the same text must agree here and
    # two that do not must differ; nothing else about the string is promised,
    # so only ever compare it for equality. `name` is a lookup key and cannot
    # do this job -- a config says `tokenizer="bpe8k"` and gets whatever
    # `tokenizers/bpe8k.json` happens to be on that machine.
    fingerprint: str

    def encode(self, text: str) -> list[int]: ...
    def decode(self, ids: Sequence[int]) -> str: ...
    def decode_bytes(self, ids: Sequence[int]) -> bytes: ...

    # The whole vocabulary as bytes, id-indexed. `decode_bytes` answers this one
    # id at a time and is the wrong shape for a constrained decoder, which asks
    # the same question of every id at every step -- see `corn/grammar.py`.
    def token_bytes(self) -> list[bytes]: ...


class ByteTokenizer:
    """UTF-8 bytes, one token per byte. Lossless for any input, no OOV."""

    name = "byte"
    vocab_size = 256
    # A literal, where the BPE hashes its merges: this mapping is six lines of
    # code with no data behind it, so there is nothing that can drift out from
    # under a checkpoint. Changing what a byte encodes to would be a rewrite of
    # the class, and the suffix is here so that rewrite has somewhere to go.
    fingerprint = "byte:1"

    def encode(self, text: str) -> list[int]:
        return list(text.encode("utf-8"))

    def decode_bytes(self, ids: Sequence[int]) -> bytes:
        return bytes(int(i) & 0xFF for i in ids)

    def decode(self, ids: Sequence[int]) -> str:
        # 'replace' matters during sampling: an untrained model happily emits
        # byte sequences that are not valid UTF-8, and that should print, not
        # raise.
        return self.decode_bytes(ids).decode("utf-8", errors="replace")

    def token_bytes(self) -> list[bytes]:
        return [bytes([i]) for i in range(256)]


_REGISTRY = {"byte": ByteTokenizer}

# Trained vocabularies live on disk, one JSON per candidate, and are named by
# their filename -- `tokenizer="bpe8k"` in a config finds `TOKENIZER_DIR`'s
# `bpe8k.json`. They are in version control for the reason `evals/` is: a
# checkpoint's ids mean nothing without the exact vocabulary that produced
# them, and "retrain it, it's deterministic" is only true until the corpus
# moves underneath it.
TOKENIZER_DIR = Path(__file__).resolve().parent.parent / "tokenizers"


def available() -> list[str]:
    names = set(_REGISTRY)
    if TOKENIZER_DIR.is_dir():
        names.update(p.stem for p in TOKENIZER_DIR.glob("*.json"))
    return sorted(names)


def get_tokenizer(name: str) -> Tokenizer:
    if name in _REGISTRY:
        return _REGISTRY[name]()
    path = TOKENIZER_DIR / f"{name}.json"
    if path.exists():
        from .bpe import BPETokenizer  # deferred: `byte` must not need `re`

        return BPETokenizer.load(path)
    raise KeyError(f"unknown tokenizer {name!r}; have {available()}")


def check_fingerprint(expected: str | None, tokenizer: Tokenizer, source: str) -> None:
    """Refuse a vocabulary that is not the one `source` was produced with.

    The failure this exists for is silent. `vocab_size` already guards the
    mismatch that crashes -- 8k ids into a 4k embedding table -- but two
    different 8k vocabularies both report 8192, load without complaint, and
    decode into fluent text that means something else. Nothing downstream can
    see it: `corn.evals` scores a checkpoint, not the alphabet it was read
    through, so a drifted vocabulary looks like a worse model.

    `expected` is None for anything written before checkpoints carried a
    fingerprint. That is a warning and not an error on purpose -- every
    checkpoint in `checkpoints/` predates this, and refusing to load them would
    invalidate the comparisons DATA.md's findings rest on. The warning goes to
    stderr rather than stdout so it cannot land in a scorecard being parsed.
    """
    if expected is None:
        print(
            f"warning: {source} carries no tokenizer fingerprint (written before they "
            f"existed); assuming {tokenizer.name!r} is the vocabulary it was built with",
            file=sys.stderr,
        )
        return
    if expected != tokenizer.fingerprint:
        raise ValueError(
            f"tokenizer mismatch: {source} was built with a {tokenizer.name!r} whose "
            f"fingerprint is {expected[:12]}, but this machine's {tokenizer.name!r} is "
            f"{tokenizer.fingerprint[:12]}.\n"
            f"Same name, different mapping -- its ids would decode to different text. "
            f"Check out the {TOKENIZER_DIR.name}/ that goes with this artifact."
        )
