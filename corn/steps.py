"""Step-by-step recitation over a document that has steps in it.

`docs/PLAN-DOC-ANSWERS.md`'s 2026-08-27 addendum, the runtime half. A recipe
book is the asked-for case and the module is written for the shape rather than
the subject: any document whose blocks carry numbered steps -- a recipe, an
assembly sheet, a checklist -- cuts the same way.

**Why this is runtime state and not a corpus.** "What's next?" has no answer
inside a single passage; it is a *position in a document across turns*. The day
log and the scheduled-actions store both decided this already: the runtime
holds the state and the model recites from an observation. So the cursor lives
here, the step arrives through the `web_search` seam's own four payload shapes,
and a checkpoint that has never seen a recipe runs the feature unchanged --
which is the same property `harness/backends/document.py` opens with.

**Why steps are cut before `normalize`.** `corn.retrieve.normalize` flattens
whitespace, which is right for prose windows and fatal for a numbered list: the
joints a recipe already has are exactly the line breaks it throws away. So the
cutter reads the *raw* text at load time, and retrieval is untouched -- a
document with no step structure gets no behaviour change at all, which is the
safety property that lets this ride beside the existing path rather than in
front of it.

**And why cutting on the joints matters beyond tidiness.** The measured
extraction bias (finding 57's probe) is against lowercase spans that start no
capital and carry no digit -- which is precisely what an imperative recipe step
is ("fold in the egg whites gently"). A pre-cut step needs no extraction at
all: retrieval finds the recipe, the cursor holds the place, and the model does
the one thing it is at ceiling on -- reading a span back. The bias is routed
around rather than trained against.

Pure functions and one small class, no tokenizer and no model, so
`scripts/check_steps.py` tests all of it against canned text. Nothing here
imports `harness/` (`check_layering.py` forbids it) and nothing here reaches
the training side.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .extract import content_words

# A step line: "1. ", "2) ", "3:", "Step 4 - ", with the number kept so the
# spoken line can name it. Deliberately strict about the number: a bullet
# ("- 200g rice") is an ingredient, not a step, and a document that numbers
# nothing has no steps to recite rather than a paragraph pretending to be one.
STEP = re.compile(r"^\s*(?:step\s+)?(\d{1,3})\s*[.):-]\s+(\S.*)$", re.I)

# A markdown heading, which is the title when a document has them.
HEADING = re.compile(r"^\s*#{1,6}\s+(.+?)\s*#*\s*$")

# A bullet, which is an ingredient line and never a title.
BULLET = re.compile(r"^\s*[-*•]\s+")

# Two steps is the floor for calling a block a recipe. One numbered line is a
# footnote or a citation far more often than it is a procedure, and a false
# positive here costs a real lookup -- the block would start reciting instead
# of answering.
MIN_STEPS = 2

# A title longer than this is a sentence that happens to precede a list. Recipe
# titles are short; the cap keeps a paragraph from becoming one.
MAX_TITLE_WORDS = 12


@dataclass
class Recipe:
    """One titled block with numbered steps in it."""
    title: str
    steps: tuple[str, ...]

    def line(self, i: int) -> str:
        """Step `i` (0-based) as one sayable span, numbered.

        The number rides *inside* the answer rather than in a field of its own,
        because the payload contract is four shapes and this file may not add a
        fifth (`corn/tools.py`, ground rule 7). It also makes the recitation
        natural: what he reads back is already "Step four, fold in the egg
        whites gently", which is the sentence a person would say.
        """
        return f"Step {i + 1} of {len(self.steps)}. {self.steps[i]}"


def cut_recipes(raw: str) -> tuple[Recipe, ...]:
    """Every titled block of numbered steps in a document's raw text.

    Blocks are delimited by headings where a document has them and by the
    first line of a blank-line-separated block where it does not. Ingredient
    bullets and prose between the title and the steps are skipped rather than
    mistaken for either.
    """
    recipes: list[Recipe] = []
    heading: str | None = None      # last markdown heading seen
    candidate: str | None = None    # first plain line of the current block
    steps: list[str] = []
    seen: set[int] = set()          # step numbers in the run, to catch restarts

    def flush() -> None:
        nonlocal steps, seen, heading, candidate
        if len(steps) >= MIN_STEPS:
            title = heading or candidate or "the steps"
            recipes.append(Recipe(title.strip(), tuple(steps)))
            # Consumed: a second run of steps under the same heading is a
            # second procedure and takes its own title from what precedes it.
            heading, candidate = None, None
        steps, seen = [], set()

    for line in raw.splitlines():
        head = HEADING.match(line)
        if head:
            flush()
            heading, candidate = head.group(1), None
            continue
        step = STEP.match(line)
        if step:
            n = int(step.group(1))
            # A number that goes backwards is a new procedure under the same
            # title (or a year in a list); close the run and open another.
            if n in seen:
                flush()
            seen.add(n)
            steps.append(step.group(2).strip())
            continue
        if not line.strip():
            continue
        # **An indented line inside a run of steps is that step continuing.**
        # Real books wrap; the canned fixture this was first written against
        # did not, and every wrapped line was silently truncating a step and
        # then becoming a title of its own. Indentation is the signal because
        # it is the one a wrapped list item actually carries -- a
        # non-indented line is prose resuming and still ends the run, which
        # keeps "A Note On Stock" from being swallowed by the recipe above it.
        if steps and line[:1].isspace() and not BULLET.match(line):
            steps[-1] = steps[-1] + " " + line.strip()
            continue
        # A plain line after a run of steps ends the run -- prose resumed.
        if steps:
            flush()
        # ...and is a title candidate only if it reads like one, and only
        # where no heading is already standing -- the blurb under a heading
        # ("Serves four, and it wants stirring.") is not the recipe's name.
        if (heading is None and not BULLET.match(line)
                and len(line.split()) <= MAX_TITLE_WORDS):
            candidate = line.strip().rstrip(":")
    flush()
    return tuple(recipes)


# **Asking about a recipe is not asking to be walked through it.** Measured
# live 2026-08-27 against `examples/recipes.txt`: "how long does the lemon
# drizzle cake bake for" names the title completely, so title overlap alone
# started a recitation and answered with step one -- the oven temperature --
# where the honest answer is in step five. Overlap says *which* recipe; these
# two vocabularies say whether a recitation was wanted at all.
#
# The veto is checked first and wins, because the cost is asymmetric: a
# question wrongly answered from step one is a wrong answer, while a
# recitation wrongly declined is an ordinary retrieval that still reads the
# recipe out of the document.
DETAIL_ASKS = (
    "how long", "how much", "how many", "how hot", "how big", "how far",
    "what temperature", "what temp", "when do", "when should", "why do",
    "why does", "what oven", "does it need", "do i need", "can i use",
    "what size", "is there", "how old",
)

START_ASKS = (
    "how do i make", "how do you make", "how to make", "how do i cook",
    "how to cook", "recipe for", "make the", "make me the", "cook the",
    "walk me through", "talk me through", "read me", "read out",
    "take me through", "start the", "lets make", "i want to make",
    "show me how", "how is the", "step by step", "run me through",
)


def _wants_steps(query: str, title: str) -> bool:
    """Whether this request asked to be walked through, rather than asked about.

    Two ways to qualify and a veto that beats both: a detail question is never
    a recitation; otherwise the request either says so in words (`START_ASKS`)
    or is bare enough to be the title itself -- "mushroom risotto", which is
    how a person asks for a recipe by name and is not a question about one.
    """
    flat = _flat(query)
    if any(a in flat for a in DETAIL_ASKS):
        return False
    if any(a in flat for a in START_ASKS):
        return True
    # Bare-title-ish: almost every word of the request is the title's own.
    q, t = set(_flat(query).split()), set(_flat(title).split())
    extra = q - t
    return len(extra) <= 1


def find_recipe(recipes: tuple[Recipe, ...], query: str) -> Recipe | None:
    """The recipe a request names, or `None` when none is named clearly.

    Content-word overlap against the title, reusing `corn.extract`'s own
    definition rather than a second one (the "content words become one
    function at last" lesson). Conservative on purpose: a request that names
    no recipe must fall through to ordinary retrieval, because starting a
    recitation the user did not ask for is a worse failure than answering a
    question about the book.
    """
    q = set(content_words(query))
    if not q:
        return None
    best, best_score = None, 0.0
    for r in recipes:
        t = set(content_words(r.title))
        if not t:
            continue
        shared = len(t & q)
        if not shared:
            continue
        # Share of the *title* that was named, so a long question does not
        # dilute a short title and a one-word overlap with a long title does
        # not qualify.
        score = shared / len(t)
        if score > best_score:
            best, best_score = r, score
    if best is None or best_score < 0.5:
        return None
    return best if _wants_steps(query, best.title) else None


# --------------------------------------------------------------------------
# The utterances the runtime serves while a recitation is live. Whole-utterance
# only, which is ground rule 4's orphan discipline: these are turns the runtime
# composes and no transcript may teach the model to produce. Matching is on the
# stripped, lowercased, punctuation-free whole line -- "next" is a step advance,
# "what comes next in the recipe after the butter" is a question for retrieval.
# --------------------------------------------------------------------------

NEXT = frozenset((
    "next", "next step", "whats next", "what next", "and next",
    "then what", "what then", "whats after that", "what comes next",
    "go on", "keep going", "carry on", "continue", "next one",
    "okay next", "ok next", "alright next", "and then", "after that",
))

REPEAT = frozenset((
    "again", "say that again", "repeat that", "repeat", "one more time",
    "what was that", "come again", "sorry what was that",
))

STOP = frozenset((
    "stop", "thats enough", "that's enough", "were done", "we're done",
    "done", "stop reading", "cancel that", "never mind",
))


# Apostrophes are *dropped* rather than spaced, so "what's next" flattens to
# "whats next" and matches the pool as one word. Every other non-alphanumeric
# becomes a space, which is what makes "next!" and "next." the same turn.
_APOSTROPHES = "'" + chr(0x2019) + chr(0x02BC)


def _flat(user: str) -> str:
    stripped = "".join(c for c in user if c not in _APOSTROPHES)
    return " ".join(
        "".join(c.lower() if (c.isalnum() or c.isspace()) else " "
                for c in stripped).split()
    )


def step_request(user: str) -> str | None:
    """`"next"`, `"repeat"`, `"stop"` or `None` for anything else.

    `None` means "run the turn normally", exactly as `conversational_reply`
    and `temporal_request` return `None` -- the hatch never swallows a turn it
    is not certain about.
    """
    flat = _flat(user)
    if not flat:
        return None
    if flat in NEXT:
        return "next"
    if flat in REPEAT:
        return "repeat"
    if flat in STOP:
        return "stop"
    return None


@dataclass
class Cursor:
    """Where in which recipe the conversation is, for one document.

    Constructed by the server when a document loads and handed to `World`
    beside `search` -- per-process wiring, which is what `World` is for. Dead
    (`recipe is None`) until a request names a recipe, and dead again after
    `stop` or the last step, so an ordinary question is never intercepted.
    """
    source: str
    recipes: tuple[Recipe, ...] = ()
    recipe: Recipe | None = None
    i: int = 0
    _last: dict | None = field(default=None, repr=False)

    @property
    def live(self) -> bool:
        return self.recipe is not None

    @property
    def title(self) -> str:
        """What is being read, for a caller that needs to name it.

        Here rather than in the payload: the four shapes are the contract
        (`corn/tools.py`, ground rule 7) and a miss carries `ok`, `reason` and
        `say` and nothing else. `check_steps.py` caught the fifth key the
        moment it was added, which is that rule holding.
        """
        return self.recipe.title if self.recipe else ""

    def _payload(self, answer: str) -> dict:
        # The hit shape, unchanged: the model has only ever been shown these
        # four, and a step is an answer that came from the document.
        self._last = {"answer": answer, "source": self.source,
                      "query": self.recipe.title if self.recipe else ""}
        return dict(self._last)

    def start(self, query: str) -> dict | None:
        """Begin a recitation if the request names a recipe, else `None`."""
        found = find_recipe(self.recipes, query)
        if found is None:
            return None
        self.recipe, self.i = found, 0
        return self._payload(found.line(0))

    def advance(self) -> dict:
        """The next step, or the honest end. Never raises, never wraps."""
        if self.recipe is None:
            return {"ok": False, "reason": "no_results",
                    "say": "I'm not reading anything right now."}
        if self.i + 1 >= len(self.recipe.steps):
            # The last step was already served; there is no next one. The
            # cursor goes dead here rather than wrapping, because a recitation
            # that silently restarts is the confabulation failure wearing an
            # apron.
            title = self.recipe.title
            self.recipe = None
            return {"ok": False, "reason": "no_results",
                    "say": f"That's the end of {title}."}
        self.i += 1
        return self._payload(self.recipe.line(self.i))

    def repeat(self) -> dict:
        if self._last is None:
            return {"ok": False, "reason": "no_results",
                    "say": "I'm not reading anything right now."}
        return dict(self._last)

    def stop(self) -> dict:
        self.recipe, self._last = None, None
        return {"ok": False, "reason": "no_results",
                "say": "Alright, stopping there."}
