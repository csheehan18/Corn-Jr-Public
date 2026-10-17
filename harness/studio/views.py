"""What each page of the studio shows, as JSON, and the edits each may make.

**The page draws; this decides.** Every rule the NiceGUI pages carried --
what a pack file's row says about it, which lint blocks a table save, which
memory edits are safe while the server runs -- lives here as a plain
function over the logic modules (`packfiles`, `memoryfiles`, `toolsd`, the
real loaders). The people an owner keeps are a pack table, edited on the
packs page; the contact book and its page went 2026-10-13 (PLAN-PEOPLE §7).
`app.py` is the thin web layer that calls these, and
`scripts/check_studio_pages.py` drives them through it against a temporary
instance. Nothing here imports a web framework.

**Every read goes through the loader the server uses**, so what a page says
a restart would load is what a restart would load: `packs.load` for the
packs folder and `toolsd.load` for declarations. The edits write through the same writers the
round-trip guards already hold.

**Paths are the instance's.** A relative path in `server.json` is relative
to the repo, the way the server resolves it; names arriving from a page are
basenames, checked, never joined as paths -- a page is a client and does not
get to write outside the folder it was shown.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..backends import toolsd
from ..backends.frontmatter import parse
from ..backends.packs import load as load_packs
from ..backends.packs import pack_search
from ..backends.schedule import DEFAULT_STORE
from ..client import SAVE_DIR
from ..serverconfig import ServerConfig
from . import memoryfiles, packfiles


class Refused(ValueError):
    """An edit the page asked for and this module will not make, said once
    and plainly -- the web layer turns it into a 400 with this sentence."""


def at(repo: Path, rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else repo / p


def basename(name: str, suffixes: tuple[str, ...] | None = None) -> str:
    """A file name a page may name: no directory part, no dot-files, and --
    when given -- one of `suffixes`."""
    name = (name or "").strip()
    if not name or name != Path(name).name or name.startswith(".") \
            or "/" in name or "\\" in name:
        raise Refused(f"{name!r} is not a plain file name")
    if suffixes is not None and Path(name).suffix.lower() not in suffixes:
        raise Refused(f"{name}: only {', '.join(suffixes)} load")
    return name


# ---------------------------------------------------------------------------
# Tools

def tools(cfg: ServerConfig, repo: Path) -> dict:
    from corn.tools import DECLINE, REGISTRY

    builtin = [{"name": n, "summary": REGISTRY[n].summary,
                "on": not cfg.tools or n in cfg.tools}
               for n in REGISTRY if n != DECLINE]
    out = {"builtin": builtin, "decline": cfg.decline,
           "tools_dir": cfg.tools_dir, "declarations": [], "warnings": [],
           "latency_classes": list(toolsd.LATENCY_CLASSES)}
    if cfg.tools_dir:
        loaded = toolsd.load(at(repo, cfg.tools_dir))
        out["warnings"] = list(loaded.warnings)
        out["declarations"] = [declaration(d) for d in loaded.tools]
    return out


def declaration(d: toolsd.Declaration) -> dict:
    try:
        raw = json.loads(d.path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raw = {}
    return {"file": d.path.name, "name": d.tool.name,
            "summary": d.tool.summary, "latency": d.tool.latency,
            "params": [{"name": p.name, "required": p.required}
                       for p in d.tool.params],
            "command": list(d.command), "gated": d.gated,
            "timeout_s": d.timeout_s, "raw": raw}


def tool_selection(enabled: list[str]) -> list[str]:
    """`cfg.tools` from the page's switches: every built-in on is the empty
    list, which is what every caller before the subset existed meant."""
    from corn.tools import DECLINE, REGISTRY

    builtin = [n for n in REGISTRY if n != DECLINE]
    unknown = [n for n in enabled if n not in builtin]
    if unknown:
        raise Refused(f"not a built-in tool: {', '.join(unknown)}")
    picked = [n for n in builtin if n in enabled]
    return [] if len(picked) == len(builtin) else picked


def write_declaration(cfg: ServerConfig, repo: Path, obj: dict,
                      file: str | None) -> dict:
    """Write one declaration and re-lint the folder through the real loader;
    returns `{"file", "problem"}` where problem is the loader's own sentence
    about this file, or empty."""
    folder = at(repo, cfg.tools_dir or str(toolsd.DEFAULT_DIR))
    folder.mkdir(parents=True, exist_ok=True)
    name = file or f"{obj.get('name') or 'tool'}.json"
    name = basename(name, (".json",))
    path = folder / name
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    after = toolsd.load(folder)
    bad = [w for w in after.warnings if name in w]
    return {"file": name, "problem": bad[0] if bad else ""}


def delete_declaration(cfg: ServerConfig, repo: Path, file: str) -> None:
    folder = at(repo, cfg.tools_dir or str(toolsd.DEFAULT_DIR))
    (folder / basename(file, (".json",))).unlink(missing_ok=True)


def test_run(cfg: ServerConfig, repo: Path, file: str, args: dict) -> dict:
    """Runs the declaration's command for real, now -- the page says so."""
    folder = at(repo, cfg.tools_dir or str(toolsd.DEFAULT_DIR))
    name = basename(file, (".json",))
    loaded = toolsd.load(folder)
    decl = next((d for d in loaded.tools if d.path.name == name), None)
    if decl is None:
        raise Refused(f"{name} is not a loadable declaration -- see the "
                      f"warnings on the page")
    payload = toolsd.make_executor(decl)(
        {k: str(v) for k, v in (args or {}).items()})
    ok = payload.get("reason") != "tool_error"
    return {"ok": ok, "payload": payload,
            "verdict": ("ok -- one flat object, the shape he can read" if ok
                        else "the command failed -- see why")}


# ---------------------------------------------------------------------------
# Packs

SUFFIXES = packfiles.TABLE_SUFFIXES + packfiles.TEXT_SUFFIXES

# What the sentinel fallback returns; anything carrying this key fell
# through every pack tier.
_FELL = "_no_pack_answer"


def pack_dir(cfg: ServerConfig, repo: Path) -> Path | None:
    return at(repo, cfg.packs) if cfg.packs else None


def _need_dir(cfg: ServerConfig, repo: Path) -> Path:
    root = pack_dir(cfg, repo)
    if root is None:
        raise Refused("set a packs folder first")
    root.mkdir(parents=True, exist_ok=True)
    return root


def file_row(path: Path, tables: dict, docs: dict) -> dict:
    stem, suffix = path.stem, path.suffix.lower()
    row = {"name": path.name, "editable": suffix in SUFFIXES,
           "size": path.stat().st_size}
    if suffix in packfiles.TABLE_SUFFIXES and stem in tables:
        t = tables[stem]
        row.update(kind="table", key=t.key_label, columns=len(t.columns),
                   rows=len(t.rows), duplicates=len(t.duplicates))
        text = (f"table: {t.key_label} + {len(t.columns)} column(s), "
                f"{len(t.rows)} row(s)")
        if t.duplicates:
            text += f", {len(t.duplicates)} duplicate key(s) ignored"
    elif suffix in packfiles.TEXT_SUFFIXES and stem in docs:
        lead = " ".join(docs[stem].split())[:80]
        row.update(kind="prose")
        text = f"prose: {lead}..."
    elif suffix in packfiles.TEXT_SUFFIXES:
        row.update(kind="empty")
        text = "header only (no prose to answer from)"
    elif suffix in packfiles.TABLE_SUFFIXES:
        row.update(kind="dropped")
        text = "dropped (see the warnings above)"
    else:
        row.update(kind="ignored")
        text = "ignored (only .csv/.tsv/.txt/.md load)"
    row["summary"] = text
    return row


def packs(cfg: ServerConfig, repo: Path) -> dict:
    root = pack_dir(cfg, repo)
    out = {"folder": cfg.packs, "files": [], "warnings": [],
           "vocab": [], "persona": persona(cfg, repo),
           "about": {"body": ""}}
    if root is None:
        return out
    pack = load_packs(root)
    out["warnings"] = list(pack.warnings)
    tables = {t.name: t for t in pack.tables}
    docs = dict(pack.docs)
    if root.is_dir():
        out["files"] = [file_row(p, tables, docs)
                        for p in sorted(root.iterdir()) if p.is_file()]
    out["vocab"] = [list(p) for p in
                    packfiles.synonyms(root / packfiles.VOCAB)]
    out["about"] = {"body": packfiles.read(root / packfiles.ABOUT).body}
    return out


def persona(cfg: ServerConfig, repo: Path) -> dict:
    root = pack_dir(cfg, repo)
    front = packfiles.read((root / packfiles.PERSONA) if root
                           else Path("persona.md"))
    seeded = False
    if not front.fields and not front.body:
        example = repo / "examples" / "persona.md"
        if example.exists():
            front = parse(example.read_text(encoding="utf-8"))
            seeded = True
    return {"name": front.fields.get("name", ""),
            "birthday": front.fields.get("birthday", ""),
            "on": [{"when": i.get("when", ""), "line": i.get("line", ""),
                    "peppy": i.get("peppy", "") == "true"}
                   for i in front.items.get("on", [])],
            "body": front.body, "seeded": seeded}


def read_pack_file(cfg: ServerConfig, repo: Path, name: str) -> dict:
    root = _need_dir(cfg, repo)
    path = root / basename(name, SUFFIXES)
    if path.suffix.lower() in packfiles.TABLE_SUFFIXES:
        header, rows = packfiles.read_table(path)
        if not header:
            header = ["Name", "Value"]
        blocking, warnings = packfiles.lint_table(header, rows)
        return {"kind": "table", "name": path.name, "header": header,
                "rows": rows, "blocking": blocking, "warnings": warnings}
    return {"kind": "text", "name": path.name,
            "text": packfiles.read_text(path)}


def lint_table(header: list[str], rows: list[list[str]]) -> dict:
    blocking, warnings = packfiles.lint_table(header, rows)
    return {"blocking": blocking, "warnings": warnings}


def write_pack_file(cfg: ServerConfig, repo: Path, name: str,
                    body: dict) -> dict:
    """A table save is refused on blocking lint -- the loader would drop the
    file; a text save always writes and reports the header's problems."""
    root = _need_dir(cfg, repo)
    path = root / basename(name, SUFFIXES)
    if path.suffix.lower() in packfiles.TABLE_SUFFIXES:
        header = [str(h).strip() for h in body.get("header") or []]
        if len(header) < 2:
            raise Refused("a table needs a key column and at least one more")
        width = len(header)
        rows = [[str(c) for c in (list(r) + [""] * width)[:width]]
                for r in body.get("rows") or []]
        rows = [r for r in rows if any(c.strip() for c in r)]
        blocking, warnings = packfiles.lint_table(header, rows)
        if blocking:
            raise Refused("not saved -- the loader would drop this file: "
                          + blocking[0])
        packfiles.write_table(path, header, rows)
        mine = [w for w in load_packs(root).warnings if path.name in w]
        note = mine[0] if mine else (
            f"wrote {path.name} with {len(warnings)} warning(s)" if warnings
            else f"wrote {path.name}")
        return {"note": note, "warn": bool(mine or warnings)}
    text = str(body.get("text") or "")
    packfiles.write_text(path, text)
    front = parse(text)
    if front.problems:
        return {"note": f"wrote {path.name}; header problem: "
                        f"{front.problems[0]}", "warn": True}
    if not front.body.strip():
        return {"note": f"wrote {path.name} -- header only, no prose to "
                        f"answer from", "warn": True}
    return {"note": f"wrote {path.name}", "warn": False}


def new_pack_file(cfg: ServerConfig, repo: Path, name: str) -> dict:
    root = _need_dir(cfg, repo)
    why = packfiles.valid_name((name or "").strip())
    if why:
        raise Refused(why)
    name = basename(name)
    try:
        packfiles.create(root / name)
    except FileExistsError:
        raise Refused(f"{name} already exists -- edit it instead") from None
    return {"name": name}


def upload_pack_file(cfg: ServerConfig, repo: Path, name: str, data: bytes,
                     replace: bool) -> dict:
    root = _need_dir(cfg, repo)
    name = basename(name, SUFFIXES)
    path = root / name
    if path.exists() and not replace:
        return {"exists": True, "name": name}
    path.write_bytes(data)
    return {"exists": False, "name": name}


def delete_pack_file(cfg: ServerConfig, repo: Path, name: str) -> None:
    root = _need_dir(cfg, repo)
    (root / basename(name)).unlink(missing_ok=True)


def save_persona(cfg: ServerConfig, repo: Path, body: dict) -> None:
    root = _need_dir(cfg, repo)
    packfiles.write_persona(
        root / packfiles.PERSONA, str(body.get("name") or ""),
        str(body.get("birthday") or ""),
        [{"when": str(o.get("when") or ""), "line": str(o.get("line") or ""),
          "peppy": bool(o.get("peppy"))} for o in body.get("on") or []],
        str(body.get("body") or ""))


def save_about(cfg: ServerConfig, repo: Path, body: str) -> None:
    root = _need_dir(cfg, repo)
    packfiles.write_about(root / packfiles.ABOUT, body or "")


def save_vocab(cfg: ServerConfig, repo: Path, pairs: list) -> None:
    root = _need_dir(cfg, repo)
    clean = [(str(a).strip(), str(c).strip()) for a, c in pairs
             if str(a).strip() and str(c).strip()]
    packfiles.write_vocab(root / packfiles.VOCAB, clean)


def try_question(cfg: ServerConfig, repo: Path, q: str) -> dict:
    root = pack_dir(cfg, repo)
    q = (q or "").strip()
    if root is None or not q:
        return {"answered": False, "verdict": "set a packs folder and ask "
                                              "something"}
    hit = pack_search(load_packs(root), lambda query: {_FELL: query})(q)
    if _FELL in hit:
        return {"answered": False,
                "verdict": "no pack answer -- this would fall through to "
                           "search"}
    return {"answered": True,
            "verdict": f"answered from your data ({hit.get('source', '?')})",
            "detail": {k: v for k, v in hit.items()
                       if not k.startswith("_")}}


# ---------------------------------------------------------------------------
# Memory

def memory(cfg: ServerConfig, repo: Path) -> dict:
    notes_path = at(repo, cfg.notes)
    log_path = at(repo, cfg.log)
    count, tail = memoryfiles.turns(log_path)
    return {
        "notes_file": notes_path.name,
        "notes": [{"line": r["_line"], "date": r.get("date", "?"),
                   "title": r.get("title", ""), "text": r.get("text", "")}
                  for r in memoryfiles.notes(notes_path)],
        "schedule": [{"at": r.get("at", "?"), "action": r.get("action", "?"),
                      "contact": r.get("contact", ""),
                      "message": r.get("message", "")}
                     for r in memoryfiles.schedule(
                         at(repo, str(DEFAULT_STORE)))],
        "marker": memoryfiles.marker(at(repo, cfg.persona_state)),
        "logging": cfg.logging, "log_file": str(log_path),
        "turn_count": count,
        "turns": [memoryfiles.turn_summary(r) for r in tail],
        "sessions_dir": SAVE_DIR.name,
        "sessions": [{"name": n, "size": s}
                     for n, s in memoryfiles.saved_sessions(SAVE_DIR)],
    }


def delete_note(cfg: ServerConfig, repo: Path, line: int) -> bool:
    return memoryfiles.delete_note(at(repo, cfg.notes), int(line))


def forget_marker(cfg: ServerConfig, repo: Path) -> None:
    memoryfiles.remove(at(repo, cfg.persona_state))


def clear_turns(cfg: ServerConfig, repo: Path) -> None:
    memoryfiles.remove(at(repo, cfg.log))


# ---------------------------------------------------------------------------
# About -- the model card, read from disk

CARD = Path("docs") / "MODEL-CARD.md"

# Section titles as they begin in the card, in the order a first-time user
# wants them. Matched by prefix so a re-worded tail does not lose a section.
WANTED = (
    "⚠️ The warning",
    "What he can do",
    "What he cannot do",
    "Privacy",
    "The runtime answers some turns itself",
    "Hardware and latency",
    "Licence and attribution",
)


def card_sections(text: str) -> list[tuple[str, str]]:
    """`(title, body)` for every `## ` section of the card, front matter and
    HTML comments removed."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4:]
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out: list[tuple[str, str]] = []
    title, buf = None, []
    for line in text.splitlines():
        if line.startswith("## "):
            if title is not None:
                out.append((title, "\n".join(buf).strip()))
            title, buf = line[3:].strip(), []
        elif title is not None:
            buf.append(line)
    if title is not None:
        out.append((title, "\n".join(buf).strip()))
    return out


def about(repo: Path) -> dict:
    from .mdlite import render

    path = repo / CARD
    if not path.exists():
        return {"card": str(CARD), "sections": []}
    found = card_sections(path.read_text(encoding="utf-8", errors="replace"))
    out = []
    for want in WANTED:
        for title, body in found:
            if title.startswith(want):
                out.append({"title": title, "html": render(body),
                            "open": want.startswith("⚠️")})
                break
    return {"card": str(CARD).replace("\\", "/"), "sections": out}
