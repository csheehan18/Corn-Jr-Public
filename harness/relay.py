"""Review the escalation queue, send what you approve, read what came back.

**The confirmation gate, held by a person, until the server holds it.**
VISION §6 says `ask_agent` joins the gated set the day it can actually send.
The conversational gate is not wired yet, so this CLI *is* the gate: every
pending request is shown with its envelope's key lines, and nothing goes out
without a `y` typed by the operator -- who is the owner, on the machine the
queue lives on. `--yes` exists for an owner who has already read the queue,
and it is a decision each run, never a default.

The default agent command is `claude -p`, because that is what this machine
has; `--cmd` takes anything that reads a prompt as its final argument and
prints a reply. **A send leaves the machine** -- same disclosure rule as
`--search`, printed at startup.

Usage:
    python -m harness.relay                 # review and send, one by one
    python -m harness.relay --collect       # only read back unsurfaced replies
    python -m harness.relay --yes           # send everything pending
    python -m harness.relay --cmd claude -p # the default, spelled out
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from corn.tools import DEFAULT_AGENT

from .backends.relay import (
    DEFAULT_LEDGER, DEFAULT_QUEUE, DEFAULT_TIMEOUT, Transport,
    command_runner, envelope,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--agent", default=None,
                    help="how the agent is named when replies are read back; "
                         f"defaults to {DEFAULT_AGENT!r}")
    ap.add_argument("--cmd", nargs="+", default=["claude", "-p"],
                    help="the agent command; the envelope is appended as the "
                         "final argument and stdout is the reply")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    ap.add_argument("--yes", action="store_true",
                    help="send every pending request without per-item "
                         "prompts. You are the gate; use it having read "
                         "the queue")
    ap.add_argument("--collect", action="store_true",
                    help="skip sending; only read back replies not yet heard")
    args = ap.parse_args()

    t = Transport(args.queue, args.ledger, args.agent or DEFAULT_AGENT)

    if not args.collect:
        pending = t.pending()
        if not pending:
            print("nothing pending in the queue")
        else:
            print(f"{len(pending)} pending -- sends leave this machine "
                  f"via: {' '.join(args.cmd)}")
            runner = command_runner(list(args.cmd), args.timeout)
            for source, row in pending:
                print()
                print(f"  [{row.get('date', '?')}] request: {row['request']!r}")
                if row.get("context"):
                    print(f"           context: {row['context']!r}")
                if not args.yes:
                    try:
                        answer = input("  send this? [y/N/q] ").strip().lower()
                    except (EOFError, KeyboardInterrupt):
                        print()
                        break
                    if answer == "q":
                        break
                    if answer != "y":
                        print("  held")
                        continue
                print("  sending...")
                out = t.send(source, row, runner, confirmed=True)
                if out.status == "answered":
                    print(f"  answered ({len(out.reply or '')} chars)")
                else:
                    print(f"  !! {out.error}")

    fresh = t.unsurfaced()
    if fresh:
        print()
        for r in fresh:
            print(r.spoken())
            print()
        t.mark_surfaced([r.source for r in fresh])
    elif args.collect:
        print("nothing new to read back")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
