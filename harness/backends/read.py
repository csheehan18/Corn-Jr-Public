"""The worker role: one model, N windows, one answer.

The half of WS-B-alt that needs weights. `corn/extract.py` cuts the passage,
builds each window's prompt and reduces the replies; this runs the model in
between, and it is a separate file for the reason `search.py` and `confirm.py`
are -- `corn/` is what a checkpoint was trained against and `harness/` is what
this process happens to be wired to.

**One model and N prompts, not N models.** `BatchedReader` reads every window
in one decode depth, so eight windows cost 250 ms against 1794 ms sequential
(A3) and the cost is nearly flat in N, because decode at this size is
memory-bandwidth-bound rather than compute-bound. That measurement is what
turned WS-B-alt from the expensive option into the chosen one.

**Prompts are bucketed by token length, and that is not a micro-optimisation.**
`BatchedReader` requires equal lengths -- one `StaticCache.pos` for every row,
learned absolute positions, no padding available in either direction. Windows
are equal in tokens by construction, but the prompt around them is not: the
window goes into a JSON payload, and `"` and `\` are escaped there, so a
window containing a quotation mark tokenizes longer than its neighbours. That
is a property of the *text on the page*, not of the chunker, so it cannot be
fixed upstream. Grouping is what remains, and it costs one extra decode depth
per distinct length -- against dropping those windows, which would silently
lose whichever part of the passage happened to contain a quote.
"""

from __future__ import annotations

import torch

from corn.decode import BatchedReader
from corn.extract import STRIDE, WIDTH, read_passage, windows, worker_prompt
from corn.gate import GATE_THRESHOLD, WindowGate, decline_heads, decline_text
from corn.reader import (
    EXTENT_D, READER_THRESHOLD, WHOLE_THRESHOLD, HeadReader, WholeHeadReader,
)
from corn.temporal import D_CALL, D_END, D_OBS, D_SAY, D_USER

MARKERS = (D_USER, D_CALL, D_OBS, D_SAY)

# The two head files the boundary reader is. Here rather than in `corn/`
# because a path on this disk is what the process happens to be wired to,
# which is the same reason `ckpt` is a flag and not a constant.
SPAN_HEAD = "checkpoints/reader_built_s1.pt"
VERIFIER_HEAD = "checkpoints/nullpr_s1.pt"

# The whole-passage arm's one file: the head and the 160 deltas it was fitted
# beside, together because they are only meaningful together. Seed 1, the seed
# finding 112 read first and finding 116 re-read at 523; seed 2's file is on
# disk at 517 and is not the shipped one, on finding 87's reasoning -- choosing
# between them by their Population A numbers would be selecting on the
# population the arm is measured on.
WHOLE_ADAPTER = "checkpoints/reader_whole_social8_s1.pt"  # re-fit on the social8 trunk, finding 124

# The trunk the adapter is a delta on, and the default is the checkpoint every
# number on this arm was read against. `harness/server.py` passes its own
# `--ckpt` instead: a default that quietly disagreed with the trunk actually
# loaded is the mismatch `corn.model.load_adapter` exists to refuse, and it
# refuses this one too rather than trusting the constant.
TRUNK_CKPT = "checkpoints/corn_jr_260m_v4_ft4g/ckpt.pt"

# What a worker is allowed to write. The corpus's post-observation say is at
# most 79 characters over 1,629,766 of them (`corn.agent.say_cut`), and a
# window is 64 tokens, so an answer that runs past this is not a long answer --
# it is a worker that did not stop, and every token past the marker is decoded
# for every row in the batch.
MAX_NEW = 32

# Where a reply stops being the answer. `BatchedReader` runs the full budget
# for every row deliberately -- rows finish at different points and an early
# exit would wait for the slowest anyway -- so the cut is the caller's, and
# these are the markers the worker prompt could plausibly run into. The
# newline is here because the corpus's say is one line, never two.
STOPS = (D_END, D_USER, D_CALL, D_OBS, D_SAY, "<|endoftext|>", "\n")


def _cut(reply: str) -> str | None:
    """The answer, or `None` if the worker never finished saying it.

    **Reaching one of `STOPS` is the whole distinction, and it is not
    cosmetic.** A row that spends its entire budget without a marker did not
    give a short answer, it gave the first `MAX_NEW` tokens of a long one --
    and handing that fragment to `corn.extract.grounded` reports `cels` and
    `192` as inventions, which blames the model for the harness's budget. The
    untrained worker does this on most windows: 5 of 12 in the probe that built
    `corn/extract.py`, and 3 of 5 on the first passages the wired runtime read.
    So truncation is a third outcome beside extracted and abstained, and
    `corn.extract.reduce` withholds it from the vote rather than counting it as
    either.

    `MAX_NEW` is deliberately not raised to make the problem disappear. The
    corpus's post-observation say is at most 79 characters over 1,629,766 of
    them, so 32 tokens is already generous against the distribution being asked
    for; a worker that overruns it is off that distribution, and that is the
    fact worth counting rather than the one worth hiding.
    """
    for marker in STOPS:
        i = reply.find(marker)
        if i >= 0:
            return reply[:i].strip()
    return None


def bucket(ids: list[list[int]]) -> list[list[int]]:
    """Row indices grouped by prompt length, shortest group first.

    Its own function so `scripts/check_read.py` can hold it to account without
    a model: the property that matters is that every row appears in exactly one
    group and every group is one length, and a batch that quietly lost a window
    would show up as a worse extraction rate and be blamed on the weights.
    """
    groups: dict[int, list[int]] = {}
    for i, seq in enumerate(ids):
        groups.setdefault(len(seq), []).append(i)
    return [groups[n] for n in sorted(groups)]


class Reader:
    """`(question, passage) -> (answer or None, why)`. `World.reader` takes it.

    Holds the model it was built with and nothing else about the turn, so a
    server can build one per process and a guard can replace it with a lambda.
    Temperature defaults to greedy for the same reason the interactive path
    does: a worker that samples turns agreement between windows into a
    coin-flip, and agreement is what `corn.extract.reduce` counts.

    **`gate` is off by default and is a policy, not a tuning.** On, every
    window is scored once before it is read (`corn/gate.py`), windows below
    `gate_threshold` are never decoded and the runtime authors their decline,
    and the windows that are decoded have the decline's head tokens masked at
    their first token. The measured effect on the frozen eval is a refusal
    that means something -- abstention on empty windows 61% -> 87% -- bought
    with fewer answered windows at unchanged precision. Off, this class is
    what it was: `gate=None` and an empty `ban_first` reach the same two
    call sites and neither changes a byte.

    **`reader="head"` replaces the decode with `corn/reader.py`.** The span
    head points at the answer, its verifier decides whether that span is
    spoken, and the reply handed to `reduce` is the worker's own shape either
    way -- so the two readers land on one ladder and the comparison is paired.
    On Population A the head reads 389 of 721 answerable passages right at 200
    of 282 correct silences against the cross-validated gate's 282 and 227
    (finding 87) -- it buys right answers and spends correct silence. The
    gate is bypassed when the head runs, because the verifier *is* the gate;
    `reader="generate"` is the control and is byte-identical to the path that
    shipped before it.

    **`reader="head_whole"` is a third arm and not a setting of the second.**
    It reads the passage whole -- one prompt, one forward with `corn/model.py`'s
    rank-32 adapter on, `corn/reader.py`'s `WholeHead` scoring the pairs and
    the null in one softmax -- so there is no cut, no vote and no second head.
    On Population A it reads 523 of 721 right at 198 correct silences against
    `head`'s 392 and 199 (finding 116), and it carries its own threshold
    because its margin is `max s - s_null` and not a verifier's logit. It needs
    two files this class does not otherwise touch: the adapter (which carries
    the head) and the **trunk** it was fitted to, whose sha256 the adapter
    names and `corn.model.load_adapter` refuses to disagree with.
    """

    def __init__(self, model, tok, device: str = "cuda",
                 temperature: float = 0.0, max_new: int = MAX_NEW,
                 gate: bool = False,
                 gate_threshold: float = GATE_THRESHOLD,
                 reader: str = "generate",
                 span_head: str = SPAN_HEAD,
                 verifier_head: str = VERIFIER_HEAD,
                 reader_threshold: float = READER_THRESHOLD,
                 extent_d: float = EXTENT_D,
                 reader_adapter: str = WHOLE_ADAPTER,
                 reader_whole_threshold: float = WHOLE_THRESHOLD,
                 trunk_ckpt: str = TRUNK_CKPT) -> None:
        self.model = model
        self.tok = tok
        self.device = device
        self.max_new = max_new
        self.batched = BatchedReader(model, device, temperature=temperature)
        # **Both halves of the policy hang off this one flag, deliberately.**
        # `corn/gate.py`'s measurement is of a gate *and* a forced decode
        # together: gated without forcing keeps the uninformative refusal the
        # gate was built to replace, and forced without a gate is the
        # always-answer diagnostic `probe_lenient` explicitly refuses to call
        # a policy (the same mask zeroes `extract.abstain` on empty windows).
        # A configuration that could hold one without the other would be a
        # third thing nobody measured.
        self.gate = WindowGate(model, tok, device) if gate else None
        self.gate_threshold = gate_threshold
        self.ban_first = decline_heads(tok) if gate else ()
        if reader not in ("generate", "head", "head_whole"):
            raise ValueError(f"reader {reader!r} is not `generate`, `head` or "
                             "`head_whole`")
        self.reader = reader
        self.whole = reader == "head_whole"
        # **The threshold the runtime compares against is the arm's own.** The
        # window head's margin is a verifier's logit and the whole-passage
        # head's is `max s - s_null` off one softmax; they are about -2.02 and
        # about -1.174 and neither is a tuning of the other, so the field
        # `_read_head` reads is chosen here rather than defaulted anywhere.
        self.reader_threshold = (reader_whole_threshold if self.whole
                                 else reader_threshold)
        # **Built only when it is asked for**, so the generative path pays
        # nothing for the head's existence -- not the two `.pt` files, not the
        # 33 MB they hold, not an import that would have to succeed on a clone
        # with no head trained. Flag off, this attribute is `None` and
        # `__call__` reaches `read_passage` by the line it always did.
        if reader == "head":
            self.head = HeadReader(model, tok, span_head, verifier_head,
                                   device, threshold=reader_threshold,
                                   extent_d=extent_d)
        elif self.whole:
            self.head = WholeHeadReader(model, tok, reader_adapter, trunk_ckpt,
                                        device,
                                        threshold=reader_whole_threshold,
                                        extent_d=extent_d)
        else:
            self.head = None

    def _run(self, prompts: list[str]) -> list[str | None]:
        ids = [self.tok.encode(p) for p in prompts]
        # `None` until a row is read, which is also what an unread row would
        # mean -- `bucket` covers every index, and `check_read.py` asserts it.
        out: list[str | None] = [None] * len(ids)
        for rows in bucket(ids):
            idx = torch.tensor([ids[i] for i in rows], dtype=torch.long,
                               device=self.device)
            for i, new in zip(rows, self.batched.read(idx, self.max_new,
                                                     ban_first=self.ban_first)):
                out[i] = _cut(self.tok.decode(new))
        return out

    def __call__(self, question: str, passage: str,
                 source: str = "wikipedia.org") -> tuple[str | None, str]:
        """`source` is the provider's own, and passing it matters twice.

        It goes into the worker's payload, so the prompt is the observation the
        model would really have been handed; and `corn.extract.grounded` allows
        an answer to name it, so a reply framed "according to Britannica" is an
        attribution under the real source and an invention under a default.
        """
        if self.head is not None:
            return self._read_head(question, passage, source)
        return read_passage(question, passage, self.tok.encode,
                            self.tok.decode, self._run, MARKERS, source=source,
                            gate=self.gate,
                            gate_threshold=self.gate_threshold)

    def _windows_of(self, passage: str) -> list[str]:
        """The cut `read_passage` is about to make, made here as well.

        The head needs the window *text* to find the payload's region inside
        the prompt, and `read_passage` hands its `run` only the prompts. So
        the cut is recomputed -- same function, same arguments, deterministic
        -- and then `head_run` asserts that the prompts it was actually given
        are the prompts these windows build. A drift between the two cuts
        cannot survive that assertion, which is the point of writing it rather
        than trusting the arithmetic twice.

        **The whole-passage arm's cut is the passage**, which is the same
        sentence `corn.extract.read_passage`'s `whole` branch says, and it is
        said twice here for the reason above: the assertion in `head_run` is
        what makes the two descriptions have to agree.
        """
        if self.whole:
            return [passage] if passage else []
        return windows(passage, self.tok.encode, self.tok.decode, WIDTH,
                       STRIDE)

    def _read_head(self, question: str, passage: str,
                   source: str) -> tuple[str | None, str]:
        """`read_passage` with the head as its `run`, and the hybrid reduce.

        **`reduce` is called twice and edited never.** The first call is the
        runtime's own -- every admitted window speaks, agreement beats
        presence. When it comes back with nothing *because the windows
        disagreed*, the passage is read again with only the surest admitted
        window speaking. That fallback is the eighty-fourth finding's `hybrid`
        and it is worth about thirty-five passages of attempt rate at held
        conditional accuracy; it fires on the disagreement reason and on no
        other, so a passage where nothing was grounded still abstains.

        The second pass costs no forward: `head_run` keeps the replies and
        margins of the first, and the two calls differ only in who is allowed
        to speak -- which is exactly `scripts/probe_reader_passages.py`'s
        `verdict_at`, the file every number on this arm was measured with.

        **With `reader="head_whole"` the cut is one window and the fallback is
        unreachable**, because one reply cannot disagree with itself --
        `reduce` reads "1 of 1 windows extracted it" or nothing. The branch is
        left in the path rather than switched off: a dead branch that is the
        same code is a fact about the input, and a second `_read_whole` next to
        this one would be two reduces to keep in step.
        """
        cut = self._windows_of(passage)
        seen: dict[str, list] = {}

        def head_run(prompts: list[str]) -> list[str]:
            want = [worker_prompt(question, w, *MARKERS, source=source)
                    for w in cut]
            if prompts != want:
                raise ValueError(
                    f"{len(prompts)} prompts from read_passage are not the "
                    f"{len(want)} this reader cut -- the window list the head "
                    "scored is not the one being reduced")
            replies, margins = self.head.replies(question, prompts, cut,
                                                 source,
                                                 self.reader_threshold)
            seen["replies"], seen["margins"] = replies, margins
            return replies

        got, why = read_passage(question, passage, self.tok.encode,
                                self.tok.decode, head_run, MARKERS,
                                source=source, whole=self.whole)
        if got is not None or "disagree" not in why or "margins" not in seen:
            return got, why
        admitted = [i for i, m in enumerate(seen["margins"])
                    if m >= self.reader_threshold]
        if not admitted:
            return got, why
        # Ties to the earliest window, `probe_reader_passages.top_only`'s rule
        # and `max`'s own behaviour on a first maximum.
        best = max(admitted, key=lambda i: seen["margins"][i])

        def top_run(prompts: list[str]) -> list[str]:
            if len(prompts) != len(cut):
                raise ValueError(f"{len(prompts)} prompts, {len(cut)} windows")
            return [seen["replies"][i] if i == best
                    else decline_text(question, w)
                    for i, w in enumerate(cut)]

        got, why_top = read_passage(question, passage, self.tok.encode,
                                    self.tok.decode, top_run, MARKERS,
                                    source=source, whole=self.whole)
        return got, f"{why_top} (the surest window alone, after: {why})"
