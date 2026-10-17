"""Tools from declaration files. VISION §6's sentence, made a folder.

"Tools are cheap to add. A new tool should be a declaration file, not a code
change." Until this module that sentence was aspiration: adding a tool meant
editing `corn/tools.py`'s `REGISTRY` and `corn/agent.py`'s `EXECUTORS` in
matching pairs. Now it means dropping one JSON file into a folder -- `tools.d/`
at the repo root by convention, gitignored beside `packs/` for the same
reason: it is the owner's own wiring, not the artefact's.

One file, one tool:

    {
      "name": "check_weather",
      "summary": "current weather for a place",
      "latency": "slow",
      "params": [{"name": "place"}],
      "command": ["python", "scripts/my_weather.py", "{place}"],
      "gated": true,
      "timeout_s": 30
    }

`name`, `summary`, `params` and `latency` become a `corn.tools.Tool` -- the
declaration the model reads is rendered from the same dataclass the built-ins
use, which is the property that makes the thirty-fourth finding apply: he
routes to declared tools he was never trained on at parity with trained ones.
`command` is what backs it: an argv list, each `{param}` replaced with the
argument's value, run as a subprocess whose stdout must be one flat JSON
object -- the payload. **Item-level substitution, never a shell.** A value
containing spaces or quotes stays one argv element, and there is no string a
user can speak that becomes a second command.

JSON rather than YAML for `frontmatter.py`'s reason, and the loading posture
is `packs.py`'s: a bad file is dropped with a printed reason and the rest of
the folder keeps working. The one exception a load may raise is a *collision*
with a built-in tool, which `corn.agent.register_tool` refuses -- shadowing a
trained tool with a shell script is not a file worth partially accepting.

**The payload contract is enforced at the boundary, not trusted.** The four
shapes the model was trained to read are flat -- the thirty-third finding
priced one level of nesting at `tool.copy` 100-120 -> 0-27 -- so whatever the
command prints is checked here: a dict, scalar values only. A command that
exits non-zero, times out, prints something that is not JSON, or nests, comes
back as `{"ok": false, "reason": "tool_error", "say": ...}` -- speakable,
because a turn must end in something he can say, and an exception here would
end it in a stack trace instead.

`gated` defaults to **true**: a declared command runs with the user's own
permissions, and the confirm gate (`harness/backends/confirm.py`) is the
standing answer to "should a tool that cannot be inspected ask first". A
declaration that sets `"gated": false` is the owner saying they trust their
own script; the loader honours it and the server's banner names it.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from corn.tools import LATENCY_CLASSES, REGISTRY, Param, Tool

DEFAULT_DIR = Path("tools.d")
DEFAULT_TIMEOUT_S = 30.0
MAX_TIMEOUT_S = 600.0

# The declaration file's whole vocabulary. Unknown keys are refused for
# `serverconfig.py`'s reason: a misspelt `gated` that silently did nothing
# would present as a tool that stopped asking.
KNOWN_KEYS = ("name", "summary", "latency", "params", "command", "gated",
              "timeout_s")
KNOWN_PARAM_KEYS = ("name", "required", "kind", "enum")

# What `corn.grammar._names` can emit, narrowed further to the shape every
# built-in name already has -- lowercase snake_case. A camelCase tool would
# work, but the declared line is prompt surface the model reads, and eight
# trained names all look one way.
_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
_PLACEHOLDER = re.compile(r"\{([a-z0-9_]+)\}")


@dataclass
class Declaration:
    tool: Tool
    command: tuple[str, ...]
    gated: bool
    timeout_s: float
    path: Path


@dataclass
class Loaded:
    tools: list[Declaration] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rejected: int = 0

    def summary(self) -> dict:
        """What `info` may publish. Names and counts, never a command."""
        return {"tools": sorted(d.tool.name for d in self.tools),
                "rejected": self.rejected}


def load(directory: str | Path = DEFAULT_DIR) -> Loaded:
    """Read a tools folder. Never raises; the Book contract."""
    out = Loaded()
    root = Path(directory)
    if not root.is_dir():
        out.warnings.append(f"no tools folder at {root}")
        return out
    seen: set[str] = set()
    for path in sorted(root.glob("*.json")):
        try:
            decl = _load_one(path, seen)
        except ValueError as exc:
            out.rejected += 1
            out.warnings.append(f"dropped {path.name}: {exc}")
            continue
        seen.add(decl.tool.name)
        out.tools.append(decl)
    return out


def _load_one(path: Path, seen: set[str]) -> Declaration:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected an object, got {type(raw).__name__}")
    stray = sorted(set(raw) - set(KNOWN_KEYS))
    if stray:
        raise ValueError(f"unknown key(s) {stray} -- known keys are "
                         f"{list(KNOWN_KEYS)}")

    name = raw.get("name")
    if not isinstance(name, str) or not _NAME.match(name):
        raise ValueError(f"name {name!r} is not lowercase snake_case")
    if name in REGISTRY:
        raise ValueError(f"{name} is already a tool; a declaration may not "
                         f"shadow one")
    if name in seen:
        raise ValueError(f"{name} is already declared by another file")

    summary = raw.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary must be a non-empty string -- it is the "
                         "whole of what the model knows about this tool")

    latency = raw.get("latency", "slow")
    if latency not in LATENCY_CLASSES:
        raise ValueError(f"latency {latency!r} is not one of "
                         f"{list(LATENCY_CLASSES)}")

    params = _params(raw.get("params", []))

    command = raw.get("command")
    if (not isinstance(command, list) or not command
            or not all(isinstance(c, str) and c for c in command)):
        raise ValueError("command must be a non-empty list of strings")
    declared = {p.name for p in params}
    named = {m for c in command for m in _PLACEHOLDER.findall(c)}
    ghost = sorted(named - declared)
    if ghost:
        raise ValueError(f"command names undeclared param(s) {ghost}")
    absent = sorted(p.name for p in params if p.required
                    and p.name not in named)
    if absent:
        # Enforced rather than guessed at: a required argument the command
        # never receives is an argument the model was made to produce for
        # nothing, and appending it in some invented `--flag value` shape
        # would be this module deciding a convention the script never chose.
        raise ValueError(f"required param(s) {absent} never appear in the "
                         f"command")

    gated = raw.get("gated", True)
    if not isinstance(gated, bool):
        raise ValueError("gated must be true or false")
    timeout_s = raw.get("timeout_s", DEFAULT_TIMEOUT_S)
    if (not isinstance(timeout_s, (int, float))
            or not 0 < timeout_s <= MAX_TIMEOUT_S):
        raise ValueError(f"timeout_s must be in (0, {MAX_TIMEOUT_S:g}]")

    tool = Tool(name=name, params=params, latency=latency,
                summary=summary.strip())
    return Declaration(tool=tool, command=tuple(command), gated=gated,
                       timeout_s=float(timeout_s), path=path)


def _params(raw) -> tuple[Param, ...]:
    if not isinstance(raw, list):
        raise ValueError("params must be a list")
    out = []
    seen: set[str] = set()
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise ValueError(f"params[{i}] is not an object")
        stray = sorted(set(entry) - set(KNOWN_PARAM_KEYS))
        if stray:
            raise ValueError(f"params[{i}]: unknown key(s) {stray}")
        pname = entry.get("name")
        if not isinstance(pname, str) or not _NAME.match(pname):
            raise ValueError(f"params[{i}]: name {pname!r} is not lowercase "
                             f"snake_case")
        if pname in seen:
            raise ValueError(f"params[{i}]: {pname} declared twice")
        seen.add(pname)
        required = entry.get("required", True)
        if not isinstance(required, bool):
            raise ValueError(f"params[{i}]: required must be true or false")
        kind = entry.get("kind", "string")
        if kind != "string":
            # `Param.kind` says why it is deliberately coarse; a declaration
            # asking for more precision than the built-ins have is asking
            # this loader to invent semantics nothing downstream implements.
            raise ValueError(f"params[{i}]: kind must be \"string\"")
        enum = entry.get("enum", [])
        if (not isinstance(enum, list)
                or not all(isinstance(e, str) and e for e in enum)):
            raise ValueError(f"params[{i}]: enum must be a list of strings")
        out.append(Param(pname, required=required, kind=kind,
                         enum=tuple(enum)))
    return tuple(out)


def _flat(payload) -> bool:
    """One object, scalar values. The shape the weights can read."""
    return (isinstance(payload, dict)
            and all(isinstance(k, str) for k in payload)
            and not any(isinstance(v, (dict, list, tuple))
                        for v in payload.values()))


def make_executor(decl: Declaration):
    """`(args, ctx) -> dict` for `EXECUTORS`, wrapping one subprocess.

    Every failure -- non-zero exit, timeout, stdout that is not JSON, a
    payload that nests -- returns the same speakable shape rather than
    raising. `relay.py`'s rule was "never turn a failure into a string that
    could be mistaken for an answer"; here the polarity flips because the
    caller is the model mid-turn, not an operator reading a ledger: the
    failure must arrive as an observation he can defer to, and `say` is the
    sentence the runtime already knows how to carry.
    """
    head = shutil.which(decl.command[0]) or decl.command[0]

    def _error(why: str) -> dict:
        return {"ok": False, "reason": "tool_error", "why": why,
                "say": "That tool hit a snag, so I've got nothing back."}

    def run(args: dict, ctx=None) -> dict:
        argv = [head]
        for part in decl.command[1:]:
            argv.append(_PLACEHOLDER.sub(
                lambda m: str(args.get(m.group(1), "")), part))
        try:
            out = subprocess.run(argv, capture_output=True, text=True,
                                 timeout=decl.timeout_s, encoding="utf-8",
                                 errors="replace")
        except subprocess.TimeoutExpired:
            return _error(f"timed out after {decl.timeout_s:g}s")
        except OSError as exc:
            return _error(f"could not run: {exc}")
        if out.returncode != 0:
            return _error(f"exited {out.returncode}: "
                          f"{(out.stderr or '').strip()[:200]}")
        try:
            payload = json.loads((out.stdout or "").strip())
        except ValueError:
            return _error("stdout was not JSON")
        if not _flat(payload):
            return _error("payload was not one flat object")
        return payload

    return run


def register_all(loaded: Loaded) -> dict:
    """Put every surviving declaration behind the registry seam.

    Returns `{name: run_fn}` -- the same callables `EXECUTORS` now holds --
    for the confirm gate, which needs to run one *without* going back through
    the turn. Import inside, so reading a tools folder (the studio lints one
    in-process) never pays the torch import that `corn.agent` costs.
    """
    from corn.agent import register_tool
    runners: dict = {}
    for decl in loaded.tools:
        fn = make_executor(decl)
        register_tool(decl.tool, fn)
        runners[decl.tool.name] = fn
    return runners
