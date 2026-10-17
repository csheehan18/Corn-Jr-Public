"""Byte-level BPE -- DATA.md §2, and the measurement §10 step 2 asks for.

§2 calls the tokenizer a ~4x lever on effective corpus size at fixed wall
clock, and says the chars/token column in its table is an estimate and the
cheapest measurement in the document. This is the instrument for taking it.

Byte-level, meaning merges are over UTF-8 bytes rather than characters. That
keeps `ByteTokenizer`'s two properties -- no OOV and lossless round-trip on any
input at all -- which is what lets a BPE be a drop-in for it rather than a new
set of failure modes. `corn.evals` reports nats per *byte* precisely so the
swap does not invalidate anything already scored, and that only holds if the
new tokenizer can still represent every byte.

Three decisions here are Corn-Jr-specific rather than inherited from GPT-2:

  the seven markers are atomic
        `<|call|>`, `<|obs|>`, `<|say|>`, `<|day|>`, `<|user|>`, `<|end|>` and
        `<|endoftext|>` get reserved ids and are split out before BPE ever sees
        the text. At byte level they were 7-9 tokens each and the model learned
        them as sequences; under a BPE trained on web text they would fragment
        differently in every context, and the format rows in `evals/` are the
        project's load-bearing result (README's sixth finding). A marker that
        tokenizes one way after `<|obs|>` and another way after a newline is a
        format the model has to learn twice.

  digits split one at a time, by default
        `2028` is four tokens, not one. This costs compression -- it is the
        single biggest giveback in the table §10 step 2 produces -- and it is
        chosen anyway because of what the fine-tuned arms did in §4: every one
        of 330 `temporal.copy` failures had the right month and day and the
        wrong year, clamped to `ANCHOR_END`. If a year is one token, copying it
        is one lookup against a prior over ~30 year-tokens. If it is four
        digits, three of them are shared with every other year in the corpus
        and only the last is discriminative. Which of those is easier to copy
        is not obvious, which is exactly why the vocabulary should not quietly
        decide it. `digits="group"` measures the other side.

  no merge may cross a whitespace boundary
        inherited from GPT-2's pre-tokenizer and worth keeping for the same
        reason: it stops the vocabulary from spending entries on phrases, which
        a 4k budget cannot afford.

The trainer is the standard weighted-type algorithm -- count pre-token types
once, then merge over the ~305k unique types rather than the 20M occurrences --
with incremental pair counts and a lazily-invalidated heap, because a full
recount per merge is 16,000 x 305,000 and does not finish.
"""

from __future__ import annotations

import hashlib
import heapq
import json
import re
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from .markers import SPECIALS  # the seven markers; their order fixes their ids

# GPT-2's pre-tokenizer, with two changes. `\p{L}` and `\p{N}` need the `regex`
# module, which is not a dependency, so letters are `[^\W\d_]` and digits are
# `\d` under re.UNICODE -- the same partition for every script Python knows
# about. `_+` gets its own branch because `\w` owns it while neither the letter
# class nor the digit class does, and without it underscores fall through the
# alternation entirely.
_LETTERS = r" ?[^\W\d_]+"
_PUNCT = r" ?[^\s\w]+| ?_+"
_SPACE = r"\s+(?!\S)|\s+"
_CONTRACTIONS = r"'(?:s|t|re|ve|m|ll|d)"
DIGIT_PATTERNS = {"split": r" ?\d", "group": r" ?\d+"}


def pretoken_pattern(digits: str = "split") -> re.Pattern:
    if digits not in DIGIT_PATTERNS:
        raise ValueError(f"digits must be one of {sorted(DIGIT_PATTERNS)}, got {digits!r}")
    return re.compile(
        "|".join([_CONTRACTIONS, _LETTERS, DIGIT_PATTERNS[digits], _PUNCT, _SPACE]),
        re.UNICODE,
    )


def _special_pattern(specials: Sequence[str]) -> re.Pattern:
    # Longest-first so a marker that is a prefix of another cannot shadow it.
    return re.compile("(" + "|".join(re.escape(s) for s in sorted(specials, key=len, reverse=True)) + ")")


def train_bpe(
    text: str,
    vocab_size: int,
    digits: str = "split",
    specials: Sequence[str] = SPECIALS,
    verbose: bool = False,
) -> dict:
    """Learn merges until the vocabulary reaches `vocab_size`.

    Returns the serialisable form: the merge list in learned order, which is
    all a `BPETokenizer` needs -- ids are positional, so the vocabulary is
    reconstructed rather than stored.

    The layout is bytes, then merges, then specials at the top:

        0     .. 255                    every byte, so nothing is ever OOV
        256   .. 255 + n_merges         learned merges, in the order learned
        top   .. top + len(specials)    the markers, which no merge can reach

    Specials sit at the top rather than immediately after the bytes so that a
    merge id means the same thing across two vocabularies of different sizes
    trained on the same corpus. That makes the 4k/8k/16k comparison §2 wants a
    nested one -- 4k's merges are a prefix of 8k's -- rather than three
    unrelated numberings.
    """
    n_merges = vocab_size - 256 - len(specials)
    if n_merges < 0:
        raise ValueError(
            f"vocab_size {vocab_size} has no room for 256 bytes plus "
            f"{len(specials)} specials"
        )

    pat = pretoken_pattern(digits)
    # Specials are stripped before counting. Leaving them in would let the
    # trainer spend merges on the marker text itself, which is dead weight
    # given the marker already has an id.
    segments = _special_pattern(specials).split(text)
    counts: Counter[str] = Counter()
    for i, seg in enumerate(segments):
        if i % 2 == 0:  # odd indices are the captured specials
            counts.update(pat.findall(seg))

    words: list[list[int]] = []
    freqs: list[int] = []
    for tok, n in counts.items():
        raw = tok.encode("utf-8")
        if len(raw) < 2:
            continue  # a single byte has no pair and can never be merged
        words.append(list(raw))
        freqs.append(n)

    pair_counts: Counter[tuple[int, int]] = Counter()
    where: dict[tuple[int, int], set[int]] = {}
    for i, w in enumerate(words):
        for pair in zip(w, w[1:]):
            pair_counts[pair] += freqs[i]
            where.setdefault(pair, set()).add(i)

    heap = [(-c, p) for p, c in pair_counts.items()]
    heapq.heapify(heap)

    merges: list[tuple[int, int]] = []
    t0 = time.time()
    while len(merges) < n_merges:
        # Lazy invalidation: counts fall as merges consume pairs, so a heap
        # entry is only believed when it still matches the live count. The
        # alternative is a decrease-key structure, and re-pushing is cheaper
        # than maintaining one.
        best = None
        while heap:
            negc, pair = heapq.heappop(heap)
            live = pair_counts.get(pair, 0)
            if live == 0:
                continue
            if -negc == live:
                best = pair
                break
            heapq.heappush(heap, (-live, pair))
        if best is None:
            break  # corpus exhausted of mergeable pairs before the target
        new_id = 256 + len(merges)
        merges.append(best)
        _apply_merge(best, new_id, words, freqs, pair_counts, where, heap)
        if verbose and len(merges) % 1000 == 0:
            print(
                f"  {len(merges):>6,}/{n_merges:,} merges  {time.time() - t0:5.1f}s",
                end="\r",
                flush=True,
            )

    if verbose:
        print(f"  {len(merges):,} merges in {time.time() - t0:.1f}s" + " " * 20)

    return {
        "kind": "bpe",
        "digits": digits,
        "specials": list(specials),
        "merges": [list(m) for m in merges],
        "vocab_size": 256 + len(merges) + len(specials),
    }


def _apply_merge(pair, new_id, words, freqs, pair_counts, where, heap) -> None:
    """Replace every occurrence of `pair`, adjusting counts for neighbours only.

    The cost of a merge is the number of *types* containing it, not the number
    of occurrences, which is the whole reason the trainer works on a weighted
    type list. Neighbour bookkeeping is the fiddly part: merging (a,b) inside
    `x a b y` destroys (x,a) and (b,y) and creates (x,new) and (new,y), and
    getting that wrong shows up as a vocabulary that is subtly worse rather
    than as a crash.
    """
    a, b = pair
    # `where` is allowed to over-approximate -- entries are discarded lazily,
    # so a word may be listed under a pair it no longer contains. That is safe
    # in one direction only: a stale index costs a wasted scan, a *missing*
    # index would leave occurrences behind and corrupt every later count. Every
    # write below therefore adds eagerly and removes only when known.
    touched = where.pop(pair, set())
    pair_counts.pop(pair, None)
    dirty: set[tuple[int, int]] = set()

    for i in touched:
        w = words[i]
        f = freqs[i]
        out: list[int] = []
        j = 0
        while j < len(w):
            if j + 1 < len(w) and w[j] == a and w[j + 1] == b:
                out.append(new_id)
                j += 2
            else:
                out.append(w[j])
                j += 1
        if len(out) == len(w):
            continue  # stale `where` entry: this word did not contain the pair

        # This word's contribution is recomputed wholesale rather than by
        # neighbour deltas. Deltas are faster in principle and much easier to
        # get wrong -- merging (a,b) inside `x a b y` has to destroy (x,a) and
        # (b,y) and create (x,new) and (new,y), and a mistake there produces a
        # vocabulary that is quietly worse rather than a crash. A word is a
        # handful of symbols, so wholesale costs nothing measurable.
        new_pairs = list(zip(out, out[1:]))
        new_set = set(new_pairs)
        for p in zip(w, w[1:]):
            if p == pair:
                continue  # already removed globally, above
            pair_counts[p] -= f
            if pair_counts[p] <= 0:
                pair_counts.pop(p, None)
                where.pop(p, None)
                continue
            if p not in new_set:
                where.get(p, _EMPTY).discard(i)
            dirty.add(p)
        for p in new_pairs:
            pair_counts[p] += f
            where.setdefault(p, set()).add(i)
            dirty.add(p)
        words[i] = out

    for p in dirty:
        c = pair_counts.get(p, 0)
        if c > 0:
            heapq.heappush(heap, (-c, p))


_EMPTY: set[int] = set()


class BPETokenizer:
    """A trained byte-level BPE. Satisfies the `Tokenizer` protocol.

    `decode(encode(s)) == s` for every `s`, including text that is not valid
    UTF-8 once it has been through `bytes`, because the base vocabulary is all
    256 bytes and merges only ever join things already representable.
    """

    def __init__(self, spec: dict, name: str = "bpe"):
        self.name = name
        self.digits = spec.get("digits", "split")
        self.specials: list[str] = list(spec["specials"])
        self.merges: list[tuple[int, int]] = [tuple(m) for m in spec["merges"]]
        self.vocab_size = 256 + len(self.merges) + len(self.specials)
        if spec.get("vocab_size") not in (None, self.vocab_size):
            raise ValueError(
                f"{name}: spec says vocab_size {spec['vocab_size']} but "
                f"{len(self.merges)} merges and {len(self.specials)} specials make "
                f"{self.vocab_size}"
            )

        self._ranks = {p: i for i, p in enumerate(self.merges)}
        self._pat = pretoken_pattern(self.digits)
        self._special_re = _special_pattern(self.specials)
        self._special_id = {
            s: 256 + len(self.merges) + i for i, s in enumerate(self.specials)
        }

        # id -> bytes, built by replaying the merges in order.
        self._bytes: list[bytes] = [bytes([i]) for i in range(256)]
        for a, b in self.merges:
            self._bytes.append(self._bytes[a] + self._bytes[b])
        for s in self.specials:
            self._bytes.append(s.encode("utf-8"))

        # Pre-tokens repeat enormously -- the top 300 types are most of any
        # corpus -- and `prepare` calls this on 486 MB. Without the cache the
        # merge loop runs once per occurrence instead of once per type.
        self._cache: dict[str, list[int]] = {}

        # Computed on demand and kept: hashing 8k merges is milliseconds, but
        # `load_checkpoint` and every `prepare` call ask for it.
        self._fingerprint: str | None = None

    @property
    def fingerprint(self) -> str:
        """sha256 over everything that decides an id, and nothing else.

        The three fields below are exactly what `__init__` reads to build
        `_ranks`, `_pat` and `_special_id`; `kind` and `name` are metadata that
        `save` writes and no id depends on, so renaming a vocabulary is not a
        change to it. Hashing the *spec* rather than the file's bytes is what
        makes this survive a reindent of the JSON while still catching a single
        moved merge -- and it means a tokenizer built in memory, as
        `train_bpe.py` does, has an identity before it has a path.
        """
        if self._fingerprint is None:
            canonical = json.dumps(
                {
                    "digits": self.digits,
                    "specials": self.specials,
                    "merges": [list(m) for m in self.merges],
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            self._fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return self._fingerprint

    def _encode_pretoken(self, tok: str) -> list[int]:
        hit = self._cache.get(tok)
        if hit is not None:
            return hit
        ids = list(tok.encode("utf-8"))
        while len(ids) >= 2:
            best, at = None, -1
            for k in range(len(ids) - 1):
                r = self._ranks.get((ids[k], ids[k + 1]))
                if r is not None and (best is None or r < best):
                    best, at = r, k
            if best is None:
                break
            a, b = self.merges[best]
            merged, k = [], 0
            while k < len(ids):
                if k + 1 < len(ids) and ids[k] == a and ids[k + 1] == b:
                    merged.append(256 + best)
                    k += 2
                else:
                    merged.append(ids[k])
                    k += 1
            ids = merged
        if len(self._cache) < 1_000_000:
            self._cache[tok] = ids
        return ids

    def encode(self, text: str) -> list[int]:
        out: list[int] = []
        for i, seg in enumerate(self._special_re.split(text)):
            if i % 2:
                out.append(self._special_id[seg])
            elif seg:
                for tok in self._pat.findall(seg):
                    out.extend(self._encode_pretoken(tok))
        return out

    def decode_bytes(self, ids: Sequence[int]) -> bytes:
        """Exact bytes. The one decode path that cannot lose information.

        `decode` is lossy at a boundary by construction: merges are over bytes,
        so a token can hold a *fragment* of a multi-byte character, and
        decoding a slice of a stream in isolation then produces U+FFFD where
        the character was cut. That is right for display and wrong for anything
        comparing bytes -- which is what `corn.evals.scan_stream` does when it
        looks for eval text inside a corpus, chunk by chunk.

        Out-of-range ids are dropped rather than masked. Unlike bytes there is
        no sensible wraparound, and a silent wrap would turn a vocab-size bug
        into plausible text.
        """
        n = len(self._bytes)
        table = self._bytes
        return b"".join(table[i] for i in ids if 0 <= i < n)

    def decode(self, ids: Sequence[int]) -> str:
        # `errors="replace"` for the same reason `ByteTokenizer` uses it: an
        # untrained model emits ids whose bytes are not valid UTF-8, and that
        # should print rather than raise.
        return self.decode_bytes([int(i) for i in ids]).decode("utf-8", errors="replace")

    def token_bytes(self) -> list[bytes]:
        """The vocabulary as bytes, id-indexed. A copy: `_bytes` is what every
        decode reads through and a caller that mutated it would corrupt the
        tokenizer rather than its own list."""
        return list(self._bytes)

    def save(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "kind": "bpe",
                    "name": self.name,
                    "digits": self.digits,
                    "specials": self.specials,
                    "vocab_size": self.vocab_size,
                    "merges": [list(m) for m in self.merges],
                },
                indent=1,
            ),
            encoding="utf-8",
        )
        return path

    @classmethod
    def load(cls, path: Path | str) -> "BPETokenizer":
        path = Path(path)
        spec = json.loads(path.read_text(encoding="utf-8"))
        return cls(spec, name=spec.get("name", path.stem))


def chars_per_token(tokenizer, text: str) -> float:
    """§2's column. Characters, not bytes -- the table is in chars/token.

    Byte level reads 1.0 on ASCII and below 1.0 on anything else, which is the
    honest floor to compare a BPE against.
    """
    ids = tokenizer.encode(text)
    return len(text) / len(ids) if ids else 0.0


def iter_documents(path: Path | str, sep: str = "<|endoftext|>") -> Iterable[str]:
    """Documents from a prepared corpus file, for sampling without reading it all."""
    buf = ""
    with open(path, encoding="utf-8", errors="replace") as f:
        while True:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(sep)
            buf = parts.pop()
            for p in parts:
                if p.strip():
                    yield p
    if buf.strip():
        yield buf
