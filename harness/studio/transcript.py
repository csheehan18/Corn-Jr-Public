"""The studio's copy of the sitting, in the shape `Saved Sessions/` already has.

`harness/client.py` keeps every line it prints so `/saved` can drop the whole
conversation into a file "in the shape those files are already in -- terminal
copy-paste". The studio renders to a web page instead of a terminal, so its
copy has to be kept deliberately -- and kept in the *same* shape, because a
saved sitting should not betray which client it was had through. The dedupe
rule (`_content`), the `<|say|>` marker and the folder all come from
`client.py` rather than being restated; the underscore import is
package-internal and on purpose.

This module consumes protocol events the way `client.run_turn` does and
appends what that function would have printed. If the two ever disagree about
a rendering, `run_turn` is right -- it is the reference implementation --
and `scripts/check_studio.py` compares against its actual output to keep
this claim tested rather than asserted.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from ..client import D_SAY, SAVE_DIR, _content


class Transcript:
    def __init__(self):
        self.lines: list[str] = []
        self._saved: Path | None = None
        self._sent: float | None = None
        self._first: float | None = None
        self._streamed = ""
        self._spoke = False

    def header(self) -> None:
        """The opening line a pasted-terminal transcript has, for this client."""
        self.lines.append(f"{os.getcwd()}>python -m harness.studio\n")

    def banner(self, info: dict) -> None:
        """What the client prints from the connect-time `info`, minus the
        slash-command hints that mean nothing on a page with buttons."""
        self.lines.append(f"{info.get('ckpt')} -- {info.get('params', 0):,} "
                          f"params, {len(info.get('tools') or ())} tools.\n")
        log = info.get("log") or ""
        self.lines.append(f"  (recording turns to {log})\n" if log
                          else "  (not recording; --no-log)\n")

    def user(self, text: str) -> None:
        self.lines.append(f"> {text}\n")
        self._sent = time.perf_counter()
        self._first = None
        self._streamed = ""
        self._spoke = False

    def note(self, text: str) -> None:
        """A client-side line -- "(history dropped)", a doc load -- indented
        the way the client indents its own asides."""
        self.lines.append(f"  {text}\n")

    def event(self, ev: dict) -> None:
        kind = ev.get("t")
        if kind == "waiting":
            self.lines.append("  (queued behind another turn)\n")
        elif kind == "text":
            if self._first is None and self._sent is not None:
                self._first = (time.perf_counter() - self._sent) * 1000
            self.lines.append(ev["text"])
            self._streamed += ev["text"]
            self._spoke = True
        elif kind == "say":
            said = ev.get("text", "")
            if said and _content(said) != _content(self._streamed):
                if self._first is None and self._sent is not None:
                    self._first = (time.perf_counter() - self._sent) * 1000
                tag = "  (deferred to the tool)" if ev.get("deferred") else ""
                self.lines.append(f"{D_SAY}{said}{tag}")
                self._spoke = True
        elif kind == "call":
            mark = "" if ev.get("ok") else f"  !! {ev.get('why')}"
            masked = (f"  ~~ grammar masked {ev['masked']}"
                      if ev.get("masked") else "")
            self.lines.append(f"\n  -> {ev['raw']}{mark}{masked}\n")
        elif kind == "obs":
            self.lines.append(f"  <- {json.dumps(ev['payload'])}\n")
        elif kind == "fold":
            self.lines.append(f"  ~~ folded {ev.get('raw')!r} -> "
                              f"{ev.get('folded')!r}\n")
        elif kind == "rejected":
            self.lines.append(f"  !! not executed -- {ev['why']}\n")
        elif kind == "error":
            self.lines.append(f"  !! {ev['why']}\n")
        elif kind == "done":
            if self._spoke:
                self.lines.append("\n")
            ttft = (f"{self._first:.0f}ms to first token, "
                    if self._first is not None else "")
            self.lines.append(f"  [{ttft}{ev['ms']:.0f}ms total]\n")

    def save(self) -> Path:
        """`Saved Sessions/sessionN.txt`, the same file all sitting --
        `client.save_transcript`'s behaviour, per instance rather than per
        module because one process may outlive several conversations."""
        SAVE_DIR.mkdir(exist_ok=True)
        if self._saved is None:
            n = 1
            while (SAVE_DIR / f"session{n}.txt").exists():
                n += 1
            self._saved = SAVE_DIR / f"session{n}.txt"
        self._saved.write_text("".join(self.lines), encoding="utf-8")
        return self._saved
