"""Just enough Markdown for the model card: the About page's renderer.

`docs/MODEL-CARD.md` uses paragraphs, `-` lists, numbered lists, `>` quotes,
pipe tables, `###` headings, `**bold**`, `*italic*`, `` `code` `` and links,
and nothing else; a Markdown library would be a dependency for one page that
renders one file. Everything is HTML-escaped before any markup is added, so
the card can never inject into the page, and only an absolute `http(s)` link
becomes an anchor -- a repo-relative link (`docs/findings/...`) points at a
file this server does not serve, so it renders as its text.

Unknown constructs degrade to paragraphs rather than vanishing; the card is
read, not executed.
"""

from __future__ import annotations

import html
import re

_LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITAL = re.compile(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])")
_UL = re.compile(r"^(\s*)[-*] (.*)$")
_OL = re.compile(r"^(\s*)\d+\. (.*)$")
_SEP = re.compile(r"^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")


def inline(text: str) -> str:
    """Escape, then mark up: code spans first so nothing inside them is
    read as bold or a link."""
    spans: list[str] = []

    def keep(m: re.Match) -> str:
        spans.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(spans) - 1}\x00"

    text = _CODE.sub(keep, text)
    text = html.escape(text, quote=False)

    def link(m: re.Match) -> str:
        label, url = m.group(1), html.unescape(m.group(2))
        if re.match(r"^https?://", url):
            return (f'<a href="{html.escape(url)}" target="_blank" '
                    f'rel="noopener noreferrer">{label}</a>')
        return label

    text = _LINK.sub(link, text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITAL.sub(r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


def _cells(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("#"):
            level = min(len(line) - len(line.lstrip("#")) + 1, 6)
            out.append(f"<h{level}>{inline(line.lstrip('#').strip())}"
                       f"</h{level}>")
            i += 1
            continue
        if line.strip() in ("---", "***"):
            out.append("<hr>")
            i += 1
            continue
        if line.lstrip().startswith("|") and i + 1 < len(lines) \
                and _SEP.match(lines[i + 1].strip()):
            head = _cells(line)
            i += 2
            body = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                body.append(_cells(lines[i]))
                i += 1
            out.append("<table><thead><tr>"
                       + "".join(f"<th>{inline(c)}</th>" for c in head)
                       + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>"
                                                  for c in r) + "</tr>"
                                 for r in body)
                       + "</tbody></table>")
            continue
        if line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i][1:].lstrip())
                i += 1
            out.append(f"<blockquote>{render(chr(10).join(buf))}"
                       f"</blockquote>")
            continue
        for pat, tag in ((_UL, "ul"), (_OL, "ol")):
            if pat.match(line):
                items: list[str] = []
                while i < len(lines) and lines[i].strip():
                    m = pat.match(lines[i])
                    if m and len(m.group(1)) <= 1:
                        items.append(m.group(2))
                    elif items:
                        # A continuation line or a nested item: folded into
                        # the item above, which is how the card reads.
                        items[-1] += " " + lines[i].strip().lstrip("-* ")
                    i += 1
                out.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>"
                                                for t in items) + f"</{tag}>")
                break
        else:
            # The first line is always taken, so a line no branch claims (a
            # stray `|`) still advances the cursor.
            buf = [line.strip()]
            i += 1
            while i < len(lines) and lines[i].strip() and not (
                    lines[i].startswith(("#", ">", "|"))
                    or _UL.match(lines[i]) or _OL.match(lines[i])):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(buf))}</p>")
            continue
    return "\n".join(out)
