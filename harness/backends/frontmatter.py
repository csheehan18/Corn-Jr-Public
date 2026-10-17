"""The `---` block at the top of a pack file, and the prose under it.

Two modules read it and they read it for opposite reasons, which is why the
parser is here rather than inside either of them. `harness/backends/persona.py`
wants the block and throws the prose away; `harness/backends/packs.py` wants
the prose and must throw the block away, because a pack doc answers questions
by reading a paragraph out loud and `name: Corn-Jr` is not a sentence anybody
should hear. One implementation means the two can never disagree about where
the block ends.

**It is not YAML and does not pretend to be.** There is no YAML parser in this
project's dependencies and adding one to read four keys would be the wrong
trade. What is supported is exactly the shape `examples/persona.md` shows:

    ---
    name: Corn-Jr
    birthday: 2025-11-02
    on:
      - when: 12-25
        line: Merry Christmas, by the way.
        peppy: true
    ---

Scalars are `key: value` at the left margin. A key whose value is empty opens
a list, and each `- ` beneath it starts an item whose own `key: value` lines
are indented under it. Values are taken as written, with surrounding quotes
removed if a person put them there out of habit. A line starting with `#` is
a comment, because hashing a setting out for a week is what people do to
files they edit by hand. Everything else is a problem
rather than a guess -- collected by line, handed back, and printed by whoever
called, because a file the owner typed by hand should say what it did not
understand rather than quietly ignoring it.

The block has to be the *first* thing in the file. A `---` further down is a
horizontal rule in somebody's markdown, and treating that as front matter
would eat their document.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_FENCE = "---"


@dataclass
class Front:
    """A parsed header. `fields` and `items` are empty for a file without one."""

    fields: dict[str, str] = field(default_factory=dict)
    items: dict[str, list[dict[str, str]]] = field(default_factory=dict)
    body: str = ""
    problems: list[str] = field(default_factory=list)


def _value(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text


def _pair(line: str) -> tuple[str, str] | None:
    key, sep, rest = line.partition(":")
    if not sep or not key.strip() or " " in key.strip():
        return None
    return key.strip().lower(), _value(rest)


def parse(text: str) -> Front:
    """The header and the body of one pack file. Never raises.

    A file with no header comes back as `Front(body=text)`, which is what makes
    this safe to run over every `.md` in the folder: the existing packs have no
    header and must be unchanged by having a parser pointed at them.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != _FENCE:
        return Front(body=text)
    try:
        end = next(i for i in range(1, len(lines))
                   if lines[i].strip() == _FENCE)
    except StopIteration:
        # An opened block that never closes. The body is the safe answer --
        # dropping the whole file over a missing line would lose the prose
        # too -- and the problem is reported rather than swallowed.
        return Front(body=text, problems=["header opened with --- and never closed"])

    out = Front(body="\n".join(lines[end + 1:]).lstrip("\n"))
    listing: str | None = None      # the list key currently open
    for n, raw in enumerate(lines[1:end], start=2):
        line = raw.rstrip()
        # A blank line, or a comment. Comments are here because the file is
        # hand-edited by one person on their own machine and the commonest
        # thing to do to a setting you are not sure about is to hash it out
        # for a week -- a header that called that a syntax error would be
        # printing a warning at every startup about a line doing its job.
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indented = line[:1].isspace()
        stripped = line.strip()

        if not indented:
            listing = None
            pair = _pair(stripped)
            if pair is None:
                out.problems.append(f"line {n}: {stripped!r} is not key: value")
                continue
            key, value = pair
            if value:
                out.fields[key] = value
            else:
                # An empty value opens a list. `on:` with nothing after it and
                # nothing under it is an empty list, which is a person saying
                # "no occasions" and is not an error.
                listing = key
                out.items.setdefault(key, [])
            continue

        if listing is None:
            out.problems.append(f"line {n}: {stripped!r} is indented under nothing")
            continue
        if stripped.startswith("- "):
            pair = _pair(stripped[2:])
            if pair is None:
                out.problems.append(f"line {n}: {stripped!r} is not - key: value")
                continue
            out.items[listing].append({pair[0]: pair[1]})
            continue
        if not out.items[listing]:
            out.problems.append(f"line {n}: {stripped!r} comes before the first -")
            continue
        pair = _pair(stripped)
        if pair is None:
            out.problems.append(f"line {n}: {stripped!r} is not key: value")
            continue
        out.items[listing][-1][pair[0]] = pair[1]
    return out
