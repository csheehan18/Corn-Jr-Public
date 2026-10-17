"""The wire format, in one file so both ends read the same description.

**Newline-delimited JSON over TCP, and the newline is load-bearing.** Every
frame is one `json.dumps` with no embedded newline followed by `\\n`, which
makes the transport `readline` on both ends and makes a frame boundary
something a client can find without a length prefix or a parser. That is the
same convention `corn/agent.py` already enforces on tool payloads -- a payload
with a newline in it cannot enter a transcript -- so the constraint is one the
runtime was already keeping.

**Why not HTTP.** VISION §3 budgets 500ms for the whole round trip and §4 puts
thin clients on a LAN against one resident model. What that needs is a socket
that stays open for a conversation and streams as it goes; what HTTP would add
is a framework dependency, a request/response shape that fights streaming, and
a reconnect per turn. Phase 4 wants barge-in -- the client interrupting
mid-utterance -- and that is a duplex stream or it is nothing. A WebSocket
wrapper over this is twenty lines the day a browser needs one.

**Zero new dependencies is a requirement rather than a preference.** This
package is going to be published beside the weights, and every dependency it
carries is one a person hosting their own Corn-Jr has to install correctly
before he says a word.

Requests, client to server:

    {"op": "turn", "user": "...", "id": "..."}   run one turn
    {"op": "ping"}                                liveness, no model touched
    {"op": "reset"}                               drop multi-turn history
    {"op": "info"}                                checkpoint, shape, tools
    {"op": "window"}                              the history the last turn
                                                  was shown, read-only:
                                                  {"t": "window", "entries",
                                                  "tokens", "room", ...};
                                                  see `Session.window`
    {"op": "doc", "path": "..."}                  load a document for lookups
                                                  to answer from; empty path
                                                  unloads. Replies {"t": "doc",
                                                  "ok": ..., "name": ...,
                                                  "windows": ...} or with
                                                  "why". The path is the
                                                  server's filesystem, same
                                                  trust model as --notes

Events, server to client. `id` echoes the request's so a client can multiplex,
and every event carries `t`:

    {"t": "text",     "text": "..."}    speech, as it decodes
    {"t": "say",      "text": "...",    the same speech, whole, at the end,
                      "author": "...",  plus who composed it -- see below, and
                      "fell_back": ...} why his own attempt was refused, if any;
                      "state": "..."    and, when he wrote one, the record under
                                        the say (PLAN-TAG-SPINE §2b: asked,
                                        answered, open), never shown as speech
    {"t": "call",     "raw": ...,       a call the model wrote, plus whether
                      "ok": bool,       the schema accepted it and what the
                      "masked": int}    grammar had to mask
    {"t": "obs",      "payload": {...}, what the tool actually returned, plus
                      "read": "..."}    what a passage reading made of it, if any
    {"t": "fold",     "raw": "...",    the utterance was normalised before the
                      "folded": "..."}  model saw it, and only then -- absent
                                        on every turn the fold changed nothing
    {"t": "rejected", "why": "..."}     the schema refused it; nothing ran
    {"t": "done",     "transcript": ...,
                      "ms": float}      the turn, and what it cost
    {"t": "error",    "why": "..."}     the request, not the model

`ms` is on `done` rather than optional because §3 makes latency the top-level
constraint of the whole project, and a server that did not report it would make
the one number that matters the one number nobody has.

**`author` is on `say` for a reason no client needs and a corpus does.** Its
three values are `corn.agent.SAY_AUTHORS` -- `model`, `runtime`, `tool` -- and
they answer the one question a finished transcript cannot: a reply the model
generated, a reply a runtime pool wrote, and a reply lifted verbatim out of a
tool payload arrive in this field looking identical. A client may ignore it
entirely, exactly as it may ignore `masked`. A corpus builder may not: two of
the three are text the model must never be trained to produce, and by the time
a transcript is a file the distinction is gone. See `SAY_AUTHORS`.

**`fell_back` rides on `say`, and only when it applies.** A social turn is the
one place the two authors compete: by default the model writes the reply and a
runtime pool catches it when `corn.agent.social_rejection` refuses what came
back. The field carries that refusal -- `names Graham`, `digits`, `too long` --
so `author: "runtime"` on a social turn can be told apart from the same value
under `--restrict`, where he was never asked. Absent means nothing was
rejected, which is both the `--restrict` case and the case where he wrote
something usable. A client may ignore it; the thing that must not ignore it is
whatever eventually counts how often he can hold a social turn unaided.

**`fold` is sent only when there is a difference, and that is the whole of
its contract.** `corn.agent.fold_turn` casefolds an all-caps utterance and
takes a terminal question mark off; on every other turn it is the identity and
no event goes out. A client may ignore it. What must not ignore it is anything
recording the sitting: the turn the model answered is `folded` and the turn the
user typed is `raw`, and a log that kept only one of them would make every
future count over that column a count over two surface populations mixed
together. See `harness/sessionlog.py`'s `folded` field.

**And a lookup uses the same field for the same fact.** Under `--extract` the
model reads the passage a search returned as overlapping windows, and
`corn.extract.reduce` refuses the readings when none is grounded in its window
or when they disagree with each other. What the user then hears is the
provider's lead sentence -- the answer the runtime would have given before any
of this -- and `fell_back` carries the reduce's reason for it. Two different
attempts of his, refused by two different checks, reported in one field
because a client counting how often the runtime had to cover for him wants
both. `obs.read` is the per-call form and is present on the successes too.
"""

from __future__ import annotations

import json

# One turn per connection at a time. The 3080 holds one model and single-stream
# decode is memory-bandwidth-bound (VISION §4), so a second concurrent turn
# would not be served faster by being accepted -- it would make both slower and
# hide that fact behind a queue. Stated here because it is a design decision and
# not a limitation of the socket.
MAX_LINE = 1 << 20

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765


def encode(obj: dict) -> bytes:
    """One frame. Rejects embedded newlines rather than escaping them.

    `json.dumps` escapes a newline inside a *string* to `\\n`, so the only way a
    raw newline reaches this line is a bug in a caller building the frame by
    hand -- and silently accepting it would desynchronise the stream one frame
    later, somewhere else, which is the worst place to find it.
    """
    line = json.dumps(obj, ensure_ascii=False)
    if "\n" in line:
        raise ValueError("frame contains a newline")
    return (line + "\n").encode("utf-8")


def decode(line: bytes) -> dict:
    obj = json.loads(line.decode("utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("frame is not an object")
    return obj
