"""The record he writes after a say -- PLAN-TAG-SPINE §2b, phase D.

On a conversational turn the tag is **a record he writes and the runtime
reads, never a gate on the words**. After every `<|say|>` line a `state:`
line says what the turn did to the conversation, in one of three values,
and the runtime puts it in front of him on the next turn as text he wrote.
The defect it exists for is the repeated question (NOW.md §4: with a
controlled antecedent he re-asks something already answered on 20 of 48
draws) -- a failure to record that an answer happened, not a failure of
style -- and the no-training read (PLAN-TAG-SPINE §11 A2) is why it is
built: a hand-inserted `state: asked` on the shipped weights halved the
repeat under the route header, 40 to 19 of 192.

    asked      his say put a question to the person
    answered   his say delivered an answer -- a tool result read out, a
               value re-read from an observation, or a reply to a question
               the person asked
    open       neither: an acknowledgement, a greeting back, filler, a
               decline with no question in it

**One implementation, both sides of the layering split.** `annotate` writes
the line into a corpus file after the fact (`scripts/gen_stateline.py`), so
no generator changes a byte of its own rendering (rule 1's spirit: the
annotated file is a new file beside the old one); `state_of` is the value
rule, re-derived independently by `scripts/check_stateline.py`;
`split_state` and `render_say` are what `corn/agent.py` uses to read the
line he wrote off his emission and to render it back into the history. The
line sits **after the say and before the `<|end|>`** -- so a decode reaches
it before the marker that stops it -- and `corn.agent.as_history` strips
the marker exactly as it does today, leaving `<|say|>said\\nstate: X\\n` in
front of the next `<|user|>`.

The vocabulary is closed and small on purpose (PLAN-TAGS ground rule 3): a
value is added only for a measured defect whose class has no home.
"""

from __future__ import annotations

import json
import re

from .markers import D_CALL, D_END, D_OBS, D_SAY, D_USER

STOP_DOC = "<|endoftext|>"

STATE_PREFIX = "state: "
STATES: tuple[str, ...] = ("answered", "asked", "open")


def state_of(user: str, say: str, called_ok: bool, obs_values: tuple[str, ...] = ()) -> str:
    """The value a say line carries, from what the turn did.

    `user` is the utterance the say answers, `called_ok` whether the turn
    made a call whose observation was not a failure, `obs_values` every
    string value the turn's observations carried (a re-read of one is an
    answer even with no call in this turn -- `turn2gen`'s reask class).
    """
    if "?" in say:
        return "asked"
    if called_ok or "?" in user:
        return "answered"
    if any(len(v) >= 4 and re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)", say)
           for v in obs_values):
        return "answered"
    return "open"


def _obs_values(payload: str) -> tuple[str, ...]:
    try:
        obj = json.loads(payload)
    except ValueError:
        return ()
    if not isinstance(obj, dict):
        return ()
    return tuple(str(v) for v in obj.values() if isinstance(v, (str, int, float)))


def annotate(text: str) -> str:
    """`text` with a `state:` line after every `<|say|>` line.

    Walks the transcript once. A say line may end with `<|end|>` or the
    document stop; the state line goes before that marker, on its own line.
    A say line already followed by a state line is left alone, so the
    function is idempotent and an annotated file re-annotated is unchanged.
    """
    lines = text.split("\n")
    out: list[str] = []
    user = ""
    called_ok = False
    obs_values: list[str] = []
    for i, line in enumerate(lines):
        if line == D_END or line.startswith(STOP_DOC):
            # A document boundary: nothing observed before it is readable
            # after it.
            obs_values = []
            out.append(line)
            continue
        if line.startswith(D_USER):
            user = line[len(D_USER):]
            called_ok = False
            # `obs_values` is *not* reset: a re-read of an earlier turn's
            # observation ("what did it come back with again" -> "It came
            # back up to 2.60 metres.") is an answer, and the value it reads
            # is one turn back. What resets is whether *this* turn called.
            out.append(line)
            continue
        if line.startswith(D_OBS):
            payload = line[len(D_OBS):]
            vals = _obs_values(payload)
            obs_values += list(vals)
            called_ok = called_ok or ('"ok": false' not in payload)
            out.append(line)
            continue
        if line.startswith(D_SAY):
            body = line[len(D_SAY):]
            tail = ""
            for marker in (D_END,):
                if body.endswith(marker):
                    body, tail = body[: -len(marker)], marker
                    break
            # The document stop rides its own line in every slice here, so a
            # say line carries at most `<|end|>` after its text.
            out.append(f"{D_SAY}{body}")
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if not nxt.startswith(STATE_PREFIX):
                out.append(f"{STATE_PREFIX}{state_of(user, body, called_ok, tuple(obs_values))}{tail}")
            elif tail:
                # Already annotated; keep the marker where the writer put it.
                out[-1] += tail
            if tail:
                obs_values = []          # the conversation ended on this line
            continue
        out.append(line)
    return "\n".join(out)


def strip_state(text: str) -> str:
    """The inverse of `annotate` on the bytes: every state line removed and
    a marker it carried put back on the say line above it."""
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        if line.startswith(STATE_PREFIX) and out and out[-1].startswith(D_SAY):
            tail = D_END if line.endswith(D_END) else ""
            out[-1] += tail
            continue
        out.append(line)
    return "\n".join(out)


def split_state(chunk: str) -> tuple[str, str | None]:
    """(say, state) off what he emitted after `<|say|>`: the first line is
    the say, and a `state:` line under it, with a legal value, is the record.
    Anything else under the say is not a record and is dropped, as the
    runtime already drops what follows a say."""
    head, _, rest = chunk.partition("\n")
    for line in rest.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.startswith(STATE_PREFIX):
            value = line[len(STATE_PREFIX):].strip()
            for marker in (D_END, D_CALL, D_OBS, D_USER, D_SAY):
                value = value.split(marker)[0].strip()
            return head, value if value in STATES else None
        break
    return head, None


def render_say(say: str, state: str | None) -> str:
    """`<|say|>said\\nstate: X` when a record exists, `<|say|>said` when not --
    the corpus's own rendering, so train and serve cannot disagree."""
    if state:
        return f"{D_SAY}{say}\n{STATE_PREFIX}{state}"
    return f"{D_SAY}{say}"
