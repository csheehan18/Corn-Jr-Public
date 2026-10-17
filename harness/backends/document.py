"""`web_search` answered from a file the user handed over.

`docs/PLAN-DOC-ANSWERS.md`'s source piece: the role `search.py` plays for the
web, played for a document, in the same shape -- a module whose whole job is
producing the four payloads and nothing else. For open-web lookups Corn-Jr
competes with every large model and loses on knowledge; for "what does *my*
paper say about X, answered on my machine, without the document leaving the
house" the competition is thin and the selling points -- small, local,
private, fast -- are the ones VISION §2 already bet on.

**No new tool slug, and that is the plan's own decision, not an omission.**
Routing is the weakest measured link in the chain and a slug the corpus never
carried would route worse than `web_search`'s 53/200 or ride entirely on
new-tool generalization -- a bet this feature does not need to place, because
the lookups it serves are already the ones the model routes to `web_search`.
`World.search` is documented as "the one seam where a real backend replaces a
trained one", and a loaded document is exactly that: a different function
behind the same four payloads, with the weights never knowing. What the user
hears stays honest through attribution -- `source` carries the document's
name instead of `wikipedia.org`, and the corpus's own framing
(`{a}, according to {s}.`) speaks it.

**The four shapes are the contract and this file may not add a fifth**
(`corn/tools.py`; ground rule 7):

    {"answer": ..., "source": ..., "query": ...}           the region answers
    {"ok": false, "reason": "no_results", "say": ...}      it does not
    {"ok": false, "reason": "empty_query", "clarify": ...} nothing was asked

`unreachable` and `blocked` cannot occur -- there is no network to fail and no
provider to refuse -- and inventing a slug for a can't-happen would violate
rule 7's spirit. A hit carries `PASSAGE` exactly as a search hit does: the
whole region rides behind the lead sentence, is
stripped by `corn.tools.take_runtime` before the observation is built, and
`--extract`'s reader does to a local file exactly what it does to a Wikipedia
page. The lead sentence is the positional floor, same as search's -- under
`--extract` the reader replaces it with a grounded span; without, the floor
is what is spoken.

**A broken file never stops the server** -- `contacts.py`'s posture, for its
argument: a file that will not load loads as no file, with a printed reason,
and the seven working tools keep working.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from corn.retrieve import STRIDE, WIDTH, _cut, answerable, best_region, normalize
from corn.steps import Recipe, cut_recipes
from corn.tools import PASSAGE

# The search backend's own bound, mirrored for `packs.py`'s reason: the reply
# is spoken, and §3's budget does not survive a paragraph read out in full.
MAX_ANSWER = 400

# v1 ingests plain text and markdown only. PDF extraction artifacts --
# hyphenation, running headers mid-sentence, mangled ligatures -- land inside
# windows and read as model failures that aren't; PDF is a v2 ingestion
# problem, not a v1 reader risk (the plan's own scoping).
SUFFIXES = (".txt", ".md")


@dataclass
class Doc:
    """One loaded document: cut and indexed once, at load time.

    `decode` rides on the instance because the ids are only meaningful under
    the tokenizer that produced them, and an `answer()` that took a decoder
    per call could be handed the wrong one.
    """
    name: str            # the file's stem, lowercased -- the spoken source
    ids: list            # the normalized text, encoded once
    decode: object       # tokenizer decode, for cutting regions back to text
    windows: int         # how many WIDTH-token windows the retriever scores
    # Cut from the *raw* text before `normalize` flattened its line breaks,
    # because the joints a numbered list already has are exactly what
    # whitespace collapsing destroys. Empty for every document that numbers
    # nothing, which is what keeps this feature invisible to the prose path.
    recipes: tuple = ()


def load(path: str | Path, encode, decode) -> Doc | None:
    """Read a file into a `Doc`, or `None` with a printed reason. Never raises.

    `source` is the stem, lowercased: it enters `grounded`'s allowed words
    and the spoken attribution, so `Attention-Is-All-You-Need.md` should
    arrive as something sayable, not a path.
    """
    p = Path(path)
    try:
        if p.suffix.lower() not in SUFFIXES:
            print(f"document: {p.name} is not {' or '.join(SUFFIXES)} -- "
                  f"not loaded (PDF and HTML are a v2 ingestion problem)")
            return None
        raw = p.read_text(encoding="utf-8", errors="replace")
        recipes = cut_recipes(raw)
        text = normalize(raw)
        if not text:
            print(f"document: {p.name} is empty after normalization -- not loaded")
            return None
        ids = list(encode(text))
        if not ids:
            print(f"document: {p.name} encodes to nothing -- not loaded")
            return None
        return Doc(p.stem.lower(), ids, decode,
                   len(_cut(ids, WIDTH, STRIDE)), recipes)
    except OSError as exc:
        print(f"document: could not read {p} -- {exc}")
        return None


def answer(doc: Doc, query: str) -> dict:
    """The four payloads, from a file instead of a provider.

    The empty-query clarify is verbatim from the contract; the miss reuses
    `no_results` because it is the familiar reason in the familiar shape --
    the model speaks `say` and never inspects `reason`, which is the
    deference `_recall_day` already rests on. The say names the document
    rather than echoing the query, because "in {doc}" is the true statement
    here: the file was searched and does not speak to the question.
    """
    q = (query or "").strip()
    if not q:
        return {"ok": False, "reason": "empty_query",
                "clarify": "What would you like me to look up?"}
    hit = best_region(q, doc.ids, doc.decode)
    if hit is None or not answerable(q, hit[0]):
        return {"ok": False, "reason": "no_results",
                "say": f"I couldn't find anything about that in {doc.name}."}
    region, _ = hit
    lead = _first_sentence(region)
    payload = {"answer": lead, "source": doc.name, "query": q}
    if region != lead:
        payload[PASSAGE] = region
    return payload


def _first_sentence(text: str, limit: int = MAX_ANSWER) -> str:
    """The region's lead, as something sayable. `packs.py`'s cut, same reason.

    A region cut from a paper's middle can open mid-sentence; that fragment
    is still the positional floor the plan registers, and the reader behind
    `--extract` is the thing that beats it, not a smarter cut here.
    """
    text = " ".join(text.split())
    lead = re.split(r"(?<=[.!?])\s", text)[0]
    if len(lead) <= limit:
        return lead
    cut = lead[:limit]
    i = cut.rfind(" ")
    return (cut[:i] if i > 0 else cut).strip() + "..."
