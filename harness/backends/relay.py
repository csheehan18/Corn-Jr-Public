"""The escalation transport -- the thing that finally drains the queue.

**`ask_agent` has queued and never sent since the day it existed**, and every
honest sentence in the system says so ("I've passed that on" is about the
queue, `status: queued` is not `sent`). This file is the send half: it reads
`escalations.jsonl`, wraps each request in the envelope VISION §6 settled,
hands it to whatever agent command the owner configured, and writes what came
back into a ledger the same section already declared to be memory.

**The envelope is the contract, composed in code.** Verbatim `request`,
labelled `context`, the relay declaring itself, the reply preference -- each
line exists because the receiving agent behaves differently when it knows it
is writing for a voice readback through a relay, and because a relay that
presented as the owner would be the impersonation-shaped version of writing
`sent` into a payload. `scripts/check_relay.py` asserts the request survives
byte-for-byte; there is no code path that could paraphrase it, which is
`corn/grammar.py`'s discipline applied to an outbound message.

**Confirmation is the caller's job and the transport refuses to forget it.**
VISION §6: `ask_agent` joins the gated set the day it can actually send.
Until the server wires that gate, the only caller is `harness/relay.py` --
an operator CLI where a person reads each pending request and says yes to
each send -- and `send` takes `confirmed=True` explicitly, so a future caller
that skipped the gate would be visible in its own source.

**The ledger never lies about what happened.** A reply row carries the
agent's words verbatim; a failed send carries `status: error` and no reply
field at all, because a reply key holding an error string is how an error
gets read aloud as an answer one refactor later. Surfacing marks rows so a
reply is spoken about once, with attribution, and the full text stays in the
ledger for the day the recall tools read it (VISION §5.1's addendum).

The ledger file is personal data on the same terms as the queue it mirrors,
and the default path is gitignored beside it.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

DEFAULT_QUEUE = Path("escalations.jsonl")
DEFAULT_LEDGER = Path("agent_ledger.jsonl")

# How long a send may take before it is an error rather than a wait. Slow is
# the tool's declared nature -- an agent that thinks for two minutes is
# working, not broken -- but a transport with no ceiling hangs the operator.
DEFAULT_TIMEOUT = 600

# Spoken surfacing keeps VOICE's economy: the headline, then where the rest
# lives. The cap is generous because the envelope already asked for short.
SURFACE_CHARS = 300


def envelope(request: str, context: str | None = None,
             agent: str = "the agent") -> str:
    """The outbound message, exactly as VISION §6 settled it.

    `request` is inserted verbatim inside quotes and nothing in this function
    can alter it -- no strip, no rewrap, no normalisation. What the user said
    is what the agent reads, which is the whole guarantee.
    """
    lines = [
        "Relayed by Corn-Jr, its owner's local assistant. Voice interface; "
        "the reply will be read aloud.",
        f'Request, verbatim: "{request}"',
    ]
    if context:
        lines.append(f"Context, added by Corn-Jr from tools and "
                     f"conversation: {context}")
    lines.append(
        "Reply preference: answer first, in a sentence or two, short and "
        "speakable; add detail after if needed; state assumptions and "
        "proceed rather than asking clarifying questions."
    )
    return "\n".join(lines)


def command_runner(cmd: list[str],
                   timeout: float = DEFAULT_TIMEOUT) -> Callable[[str], str]:
    """A runner that hands the envelope to a local agent command.

    The envelope goes on as the final argument -- `claude -p <prompt>` is the
    default shape -- and stdout is the reply. A non-zero exit or a timeout
    raises, and the caller records an error row; this function never turns a
    failure into a string that could be mistaken for an answer.

    The executable is resolved through `shutil.which` because on Windows the
    agent is usually a `.cmd` shim, which a bare `subprocess` list cannot
    find -- the first live send failed on exactly this.
    """
    head = shutil.which(cmd[0]) or cmd[0]

    def run(text: str) -> str:
        out = subprocess.run([head, *cmd[1:], text], capture_output=True,
                             text=True, timeout=timeout, encoding="utf-8")
        if out.returncode != 0:
            raise RuntimeError(
                f"agent command exited {out.returncode}: "
                f"{(out.stderr or '').strip()[:200]}")
        reply = (out.stdout or "").strip()
        if not reply:
            raise RuntimeError("agent command returned nothing")
        return reply
    return run


@dataclass
class Row:
    source: int          # line index into the queue file; the join key
    when: str
    request: str
    context: str | None
    agent: str
    status: str          # "answered" | "error"
    reply: str | None = None
    error: str | None = None
    surfaced: bool = False

    def spoken(self) -> str:
        """One sentence about the reply, attribution first, VOICE economy.

        Attribution is the fourth-author rule: these are the agent's words
        and the sentence says so before it says them. Truncation is admitted
        in the same breath, never silent.
        """
        gist = self.request if len(self.request) <= 60 else \
            self.request[:57] + "..."
        if self.status != "answered":
            return (f"I tried to send {self.agent} your request about "
                    f'"{gist}" and it didn\'t go through, so it\'s still '
                    f"in the queue on my end.")
        reply = self.reply or ""
        if len(reply) > SURFACE_CHARS:
            return (f'{self.agent} got back about "{gist}": '
                    f"{reply[:SURFACE_CHARS].rstrip()}... "
                    f"The full reply is in the ledger.")
        return f'{self.agent} got back about "{gist}": {reply}'


class Transport:
    """The queue on one side, the ledger on the other, nothing invented between.

    Reads are lazy and writes are appends plus a rewrite on `mark_surfaced`,
    the `Scheduler`'s pattern: the files stay readable by a person, and a
    store of exchanges stays small by nature.
    """

    def __init__(self, queue: Path = DEFAULT_QUEUE,
                 ledger: Path = DEFAULT_LEDGER, agent: str = "the agent"):
        self.queue_path = Path(queue)
        self.ledger_path = Path(ledger)
        self.agent = agent
        self.rows: list[Row] = []
        if self.ledger_path.exists():
            for line in self.ledger_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    self.rows.append(Row(**json.loads(line)))

    # -- reads --------------------------------------------------------------

    def queued(self) -> list[tuple[int, dict]]:
        """Every queue row, with the line index that joins it to the ledger."""
        if not self.queue_path.exists():
            return []
        out = []
        for i, line in enumerate(
                self.queue_path.read_text(encoding="utf-8").splitlines()):
            if line.strip():
                out.append((i, json.loads(line)))
        return out

    def pending(self) -> list[tuple[int, dict]]:
        """Queue rows no send has been recorded for -- errors stay pending.

        An errored send is retryable by design: the request never stops
        being the user's until an answer exists, and a transport that
        remembered failures as done would be dropping requests silently.
        """
        done = {r.source for r in self.rows if r.status == "answered"}
        return [(i, row) for i, row in self.queued() if i not in done]

    def unsurfaced(self) -> list[Row]:
        return [r for r in self.rows if r.status == "answered"
                and not r.surfaced]

    # -- the send -----------------------------------------------------------

    def send(self, source: int, row: dict, runner: Callable[[str], str],
             confirmed: bool = False) -> Row:
        """One request out, one row recorded, whatever happened.

        `confirmed` is explicit and checked: VISION §6 gates this tool the
        day it can send, and until the conversational gate is wired the
        confirmation is the operator's, given per item in `harness.relay`.
        """
        if not confirmed:
            raise PermissionError(
                "an escalation is sent only after its confirmation -- "
                "see VISION §6's gate rule")
        text = envelope(row["request"], row.get("context"), self.agent)
        when = datetime.now().astimezone().isoformat(timespec="seconds")
        try:
            reply = runner(text)
            out = Row(source=source, when=when, request=row["request"],
                      context=row.get("context"), agent=self.agent,
                      status="answered", reply=reply)
        except Exception as exc:
            out = Row(source=source, when=when, request=row["request"],
                      context=row.get("context"), agent=self.agent,
                      status="error", error=str(exc)[:300])
        self.rows.append(out)
        with self.ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(out.__dict__, ensure_ascii=False) + "\n")
        return out

    def mark_surfaced(self, sources: list[int]) -> None:
        for r in self.rows:
            if r.source in sources and r.status == "answered":
                r.surfaced = True
        self.ledger_path.write_text(
            "".join(json.dumps(r.__dict__, ensure_ascii=False) + "\n"
                    for r in self.rows),
            encoding="utf-8")
