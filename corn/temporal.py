"""Temporal expressions -- the resolver Corn-Jr calls, and the corpus slice that
teaches him to call it.

VISION.md §5.2 is explicit that the model must never do date arithmetic: a 250M
model is bad at arithmetic and good at routing, so the target of every example
generated here is the *call*, never the answer. The tool does the maths.

    resolve_date("the Thursday before last")  ->  2026-07-30
    recall_day("2026-07-30")                  ->  <that day's log>

Two implementations live in this file, deliberately written from opposite
directions:

  construction  `sample_expression()` picks a target date first and renders an
                expression denoting it, so ground truth is exact by
                construction and does not depend on any parser being correct.
  parsing       `resolve_date()` reads an expression and computes a date. This
                is the real tool -- VISION.md §6's fourth starting tool, the
                one §6 calls "the canary for the whole system".

`scripts/check_temporal.py` asserts the two agree on every generated example.
Agreement between a constructor and a parser built independently is evidence;
a single implementation checking itself is not.

Conventions, which English does not settle and so this file must:

  "last Tuesday"            the most recent *strictly past* Tuesday. On a
                            Tuesday it means seven days back, not today.
  "this past Tuesday"       identical to "last Tuesday".
  "the Tuesday before last" the occurrence before that one, i.e. minus 7.
  "a week ago Tuesday"      also minus 7 -- the same day as the line above.
  "two weeks ago"           anchor minus 14 days, treated as a point.
  "the 3rd"                 the most recent occurrence on or before the anchor,
                            so it crosses into last month when it has to.
  "next Tuesday"            the next strictly future Tuesday.

  "last week"               a span, not a day. Weeks start Monday (ISO).
  "over the weekend"        the most recent Saturday-Sunday pair.

Expressions that cannot denote a single day get a clarifying question rather
than a guess, and the split of labour is the point: **the tool decides that an
expression is unresolvable, and the model only relays what it is handed.**
Putting that judgement in the parameters would be asking a 250M model to be
calibrated about ambiguity; putting it in code makes it exact. The question
Corn-Jr asks is a string the tool returned, not one he composed -- §2 again,
one level down.

Two categories qualify, and the list is kept short on purpose. A model trained
on too much hedging becomes one that asks "which Tuesday?" forever, which is
worse than one that applies a documented convention:

  range   "last week", "last month", "over the weekend" -- provably more than
          one day, so `recall_day` cannot consume them.
  vague   "the other day", "a while back", "recently" -- no defensible date
          exists at all.

Anything the conventions above already settle is *not* a clarification case,
and neither is non-temporal input: "banana" is not an ambiguous date, it is
not a date.
"""

from __future__ import annotations

import calendar
import json
import random
import re
from dataclasses import dataclass
from datetime import date, timedelta

from .markers import D_CALL, D_DAY, D_END, D_OBS, D_SAY, D_USER  # noqa: F401  re-exported

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "twenty-one": 21, "twenty-two": 22, "twenty-three": 23,
    "twenty-four": 24, "twenty-five": 25, "twenty-six": 26,
    "twenty-seven": 27, "twenty-eight": 28, "twenty-nine": 29, "thirty": 30,
}
WORD_NUMBERS = {v: k for k, v in NUMBER_WORDS.items()}

# The anchor window, a module constant rather than a default buried in
# `generate`'s signature because the frozen eval set depends on it from the
# outside: `scripts/make_evals.py` anchors its items in 2028 and its text in
# 2029 precisely so no generated example can collide with them, which makes
# DATA.md §7's temporal decontamination structural instead of probabilistic.
#
# Widening *backwards* is free and is what bought the extra anchors here.
# Widening forwards past 2027-12-31 would walk the training slice into the eval
# anchors and quietly contaminate every temporal row, so `check_temporal.py`
# reads the frozen manifest and fails if this range ever reaches them.
ANCHOR_START = date(2020, 1, 1)
ANCHOR_END = date(2027, 12, 31)

# The transcript delimiters (`D_DAY` ... `D_END`) are imported from
# `corn/markers.py` at the top of this file and re-exported: they lived here
# first, and scripts still read them from `corn.temporal`.


def ordinal(n: int) -> str:
    """3 -> '3rd'. Used for both expressions and spoken output."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def _most_recent(anchor: date, weekday: int) -> date:
    """The strictly-past occurrence of `weekday`. On that weekday, minus 7."""
    delta = (anchor.weekday() - weekday) % 7
    return anchor - timedelta(days=delta or 7)


def _upcoming(anchor: date, weekday: int) -> date:
    """The strictly-future occurrence of `weekday`. On that weekday, plus 7."""
    delta = (weekday - anchor.weekday()) % 7
    return anchor + timedelta(days=delta or 7)


def _month_end(anchor: date, months_back: int) -> date:
    """Last day of the month `months_back` before the anchor's month."""
    first = anchor.replace(day=1)
    for _ in range(months_back):
        first = (first - timedelta(days=1)).replace(day=1)
    return first.replace(day=calendar.monthrange(first.year, first.month)[1])


def _recent_day_of_month(anchor: date, day: int) -> date | None:
    """Most recent occurrence of day-of-month `day`, on or before the anchor.

    Walks back a month at a time rather than assuming the previous month has
    the day: asking for "the 30th" on 1 March has to skip February entirely.
    """
    if day <= anchor.day:
        return anchor.replace(day=day)
    first = anchor.replace(day=1)
    for _ in range(12):
        first = (first - timedelta(days=1)).replace(day=1)
        if day <= calendar.monthrange(first.year, first.month)[1]:
            return first.replace(day=day)
    return None


def spoken_form(d: date) -> str:
    """How the tool says a date out loud. The model copies this, never builds it."""
    return f"{WEEKDAYS[d.weekday()]}, {calendar.month_name[d.month]} {ordinal(d.day)}"


# --------------------------------------------------------------------------
# The tool. VISION.md §6 tool 4.
# --------------------------------------------------------------------------

_RE_N_DAYS = re.compile(r"^(?:the\s+)?(\S+)\s+days?\s+(?:ago|back)$")
_RE_N_WEEKS = re.compile(r"^(?:the\s+)?(\S+)\s+weeks?\s+(?:ago|back)$")
_RE_BEFORE_LAST = re.compile(r"^(?:the\s+)?(\w+)\s+before\s+last$")
_RE_WEEK_AGO = re.compile(r"^a\s+week\s+ago\s+(\w+)$")
_RE_LAST_WD = re.compile(r"^(?:last|this\s+past|past)\s+(\w+)$")
_RE_NEXT_WD = re.compile(r"^(?:next|this\s+coming|coming)\s+(\w+)$")
_RE_ORDINAL = re.compile(r"^(?:on\s+)?the\s+(\d{1,2})(?:st|nd|rd|th)$")

# **The calendar ahead (2026-09-07).** Every expression above is an offset
# behind the anchor, a weekday, or a day of this month, because the day log
# looks back. A person does not: "how many days till Christmas", "what day is
# it 30 days from now" and "the 25th of December" were all answered "Sorry,
# what date was that?" on 2026-09-06, and the owner's answer to a clarify
# that named the boundary was that there should be no boundary. So: an
# offset ahead, a month-named day, a holiday, and an offset from any of
# those. Every one is still a *date*, resolved by the calendar rather than
# by the model; the count ("109 days") is composed in `corn/agent.py` from
# the date this returns and the anchor.
_MONTHS = {
    "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
    "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9, "october": 10,
    "oct": 10, "november": 11, "nov": 11, "december": 12, "dec": 12,
}
_MONTH_RE = "|".join(sorted(_MONTHS, key=len, reverse=True))
_DIRECTION = r"(?:(last|next|this)\s+)?"
# "in 30 days", "30 days from now", "two weeks' time", "a month ahead".
_RE_IN_N = re.compile(r"^in\s+(\S+)\s+(days?|weeks?|months?)(?:'?s?\s+time)?$")
_RE_N_AHEAD = re.compile(
    r"^(\S+)\s+(days?|weeks?|months?)(?:'?s?)?\s+"
    r"(?:from now|from today|ahead|later|on|out|time|s time)$")
# "the 25th of december", "25 december", "december 25th", with an optional
# last/next/this in front to point it.
_RE_DAY_MONTH = re.compile(
    rf"^{_DIRECTION}(?:the\s+)?(\d{{1,2}})(?:st|nd|rd|th)?\s+(?:of\s+)?({_MONTH_RE})$")
_RE_MONTH_DAY = re.compile(
    rf"^{_DIRECTION}({_MONTH_RE})\s+(?:the\s+)?(\d{{1,2}})(?:st|nd|rd|th)?$")
# "a week on friday": the one after next friday.
_RE_WEEK_ON = re.compile(r"^(?:a\s+)?week\s+on\s+(\w+)$")
# "two weeks from christmas", "three days before the 25th of december",
# "a week after my birthday" (the birthday having been substituted by the
# caller). The tail is resolved by this same function.
_RE_N_FROM = re.compile(
    r"^(\S+)\s+(days?|weeks?)\s+(from|after|before)\s+(.+)$")

# Fixed-date holidays; the two moving ones are computed below.
HOLIDAYS: dict[str, tuple[int, int]] = {
    "christmas": (12, 25), "christmas day": (12, 25), "xmas": (12, 25),
    "christmas eve": (12, 24), "boxing day": (12, 26),
    "new year": (1, 1), "new years": (1, 1), "new year's": (1, 1),
    "new year's day": (1, 1), "new years day": (1, 1),
    "new year's eve": (12, 31), "new years eve": (12, 31),
    "halloween": (10, 31), "valentine's day": (2, 14), "valentines day": (2, 14),
    "valentine's": (2, 14), "valentines": (2, 14),
    "independence day": (7, 4), "the fourth of july": (7, 4),
    "fourth of july": (7, 4), "4th of july": (7, 4), "the 4th of july": (7, 4),
    "st patrick's day": (3, 17), "st patricks day": (3, 17),
    "april fools": (4, 1), "april fools' day": (4, 1), "april fool's day": (4, 1),
}
_HOLIDAY_RE = "|".join(re.escape(h) for h in sorted(HOLIDAYS, key=len, reverse=True))
_RE_HOLIDAY = re.compile(rf"^{_DIRECTION}({_HOLIDAY_RE}|easter|easter sunday|"
                         rf"thanksgiving|thanksgiving day)$")


def easter(year: int) -> date:
    """Western Easter Sunday, by the anonymous Gregorian computus."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def thanksgiving(year: int) -> date:
    """The fourth Thursday of November -- the US day, the owner's."""
    first = date(year, 11, 1)
    offset = (3 - first.weekday()) % 7        # 3 is Thursday
    return first + timedelta(days=offset + 21)


def _holiday_in(name: str, year: int) -> date | None:
    if name in ("easter", "easter sunday"):
        return easter(year)
    if name in ("thanksgiving", "thanksgiving day"):
        return thanksgiving(year)
    month, day = HOLIDAYS[name]
    return date(year, month, day)


def _occurrence(anchor: date, when, direction: str | None) -> date | None:
    """The occurrence of a yearly day the question points at.

    `when(year)` gives the day in a year (or `None` for a day that year
    lacks, which is February 29th). `next` and the default look forward --
    today counts as ahead, so "christmas" on Christmas Day is today; `last`
    looks back; `this` is this calendar year's whichever way it lies. Forward
    by default because a bare "the 25th of December" is a question about
    the one coming, and the recall path says `last` itself.
    """
    if direction == "this":
        return when(anchor.year)
    if direction == "last":
        for year in (anchor.year, anchor.year - 1):
            d = when(year)
            if d is not None and d < anchor:
                return d
        return None
    for year in (anchor.year, anchor.year + 1):
        d = when(year)
        if d is not None and d >= anchor:
            return d
    return None


def _month_day(month: int, day: int):
    def when(year: int) -> date | None:
        try:
            return date(year, month, day)
        except ValueError:
            return None
    return when


def _plus_months(anchor: date, n: int) -> date:
    month0 = anchor.month - 1 + n
    year = anchor.year + month0 // 12
    month = month0 % 12 + 1
    day = min(anchor.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _resolve_ahead(e: str, anchor: date) -> date | None:
    """The forward half of `resolve_date`, on the shapes above."""
    if m := _RE_IN_N.match(e):
        n, unit = _as_int(m.group(1)), m.group(2)
    elif m := _RE_N_AHEAD.match(e):
        n, unit = _as_int(m.group(1)), m.group(2)
    else:
        n = unit = None
    if unit is not None:
        if n is None:
            return None
        if unit.startswith("day"):
            return anchor + timedelta(days=n)
        if unit.startswith("week"):
            return anchor + timedelta(days=7 * n)
        return _plus_months(anchor, n)

    if m := _RE_WEEK_ON.match(e):
        if (wd := _weekday_index(m.group(1))) is not None:
            return _upcoming(anchor, wd) + timedelta(days=7)
        return None

    if m := _RE_N_FROM.match(e):
        n = _as_int(m.group(1))
        base = resolve_date(m.group(4), anchor)
        if n is None or base is None:
            return None
        days = n * (7 if m.group(2).startswith("week") else 1)
        return base + timedelta(days=days if m.group(3) != "before" else -days)

    if m := _RE_DAY_MONTH.match(e):
        direction, day, month = m.group(1), int(m.group(2)), _MONTHS[m.group(3)]
        return _occurrence(anchor, _month_day(month, day), direction)
    if m := _RE_MONTH_DAY.match(e):
        direction, month, day = m.group(1), _MONTHS[m.group(2)], int(m.group(3))
        return _occurrence(anchor, _month_day(month, day), direction)

    if m := _RE_HOLIDAY.match(e):
        direction, name = m.group(1), m.group(2)
        return _occurrence(anchor, lambda y: _holiday_in(name, y), direction)
    return None


# What is left for a clarify to name once the calendar ahead is read: an
# expression with a forward cue in it that no shape above could parse, and
# one that names a month in a way none of them read.
_RE_AHEAD = re.compile(
    r"\b(?:from now|from today|from tomorrow|ahead|until|till|later this|"
    r"next (?:month|year)|the (?:coming|next) (?:few|couple))\b")
_RE_MONTH_NAMED = re.compile(rf"\b(?:{_MONTH_RE})\b")
AHEAD_CLARIFY = "I couldn't place that one ahead -- try 'in 30 days', or a date like December 25th."
MONTH_CLARIFY = "I couldn't place that date -- try 'December 25th' or 'the 25th of December'."


def _as_int(token: str) -> int | None:
    token = token.lower()
    if token.isdigit():
        return int(token)
    if token in ("a", "an"):
        return 1
    return NUMBER_WORDS.get(token)


def _weekday_index(word: str) -> int | None:
    word = word.capitalize()
    return WEEKDAYS.index(word) if word in WEEKDAYS else None


def resolve_date(expression: str, anchor: date) -> date | None:
    """Resolve a temporal expression against an anchor date.

    Returns None for anything it does not recognise, which is the honest
    answer and the one §9's "knows when he doesn't know" wants surfaced --
    a wrong date is far worse here than a refusal.
    """
    e = " ".join(expression.lower().strip().rstrip("?.!").split())

    fixed = {
        "today": 0, "tonight": 0, "this morning": 0,
        "yesterday": -1, "last night": -1,
        "the day before yesterday": -2, "day before yesterday": -2,
        "tomorrow": 1,
        "the day after tomorrow": 2, "day after tomorrow": 2,
    }
    if e in fixed:
        return anchor + timedelta(days=fixed[e])

    if e in ("a couple days ago", "a couple days back", "a couple of days ago",
             "a couple of days back"):
        return anchor - timedelta(days=2)
    if e in ("a few days ago", "a few days back"):
        return anchor - timedelta(days=3)

    if m := _RE_N_DAYS.match(e):
        if (n := _as_int(m.group(1))) is not None:
            return anchor - timedelta(days=n)
        return None

    if m := _RE_N_WEEKS.match(e):
        if (n := _as_int(m.group(1))) is not None:
            return anchor - timedelta(days=7 * n)
        return None

    if m := _RE_BEFORE_LAST.match(e):
        if (wd := _weekday_index(m.group(1))) is not None:
            return _most_recent(anchor, wd) - timedelta(days=7)
        return None

    if m := _RE_WEEK_AGO.match(e):
        if (wd := _weekday_index(m.group(1))) is not None:
            return _most_recent(anchor, wd) - timedelta(days=7)
        return None

    # "last easter" and "next christmas" wear the weekday shape and are not
    # weekdays; they fall through to the calendar ahead rather than to None.
    if m := _RE_LAST_WD.match(e):
        if (wd := _weekday_index(m.group(1))) is not None:
            return _most_recent(anchor, wd)
        return _resolve_ahead(e, anchor)

    if m := _RE_NEXT_WD.match(e):
        if (wd := _weekday_index(m.group(1))) is not None:
            return _upcoming(anchor, wd)
        return _resolve_ahead(e, anchor)

    # **A bare weekday stays unrecognised here, and that is deliberate.** This
    # function is stateless, and a bare weekday is only answerable against a
    # question somebody just asked -- "Saturday" means the Saturday of the span
    # the clarify was about, and there is no way to know that from `anchor`
    # alone. Resolving it to the most recent occurrence was tried and measured
    # wrong: it is right for the two weekend questions and wrong for the four
    # week-and-month ones, where it lands a week or two outside the span it was
    # asked about. Trading `unrecognised` for a confidently wrong date is the
    # one trade this tool's docstring forbids.
    #
    # `resolve_within` is where the answerable version lives, and
    # `corn/agent.py` is what remembers the span. See `weekday_in_span`.

    if e in ("end of last month", "the end of last month",
             "at the end of last month"):
        return _month_end(anchor, 1)
    if e in ("the start of this month", "start of this month",
             "the beginning of this month", "the first of the month"):
        return anchor.replace(day=1)

    if m := _RE_ORDINAL.match(e):
        day = int(m.group(1))
        return _recent_day_of_month(anchor, day) if 1 <= day <= 31 else None

    # The calendar ahead -- see the block above `_resolve_ahead`. Last, so
    # nothing that resolved before resolves differently now.
    return _resolve_ahead(e, anchor)


def _week_span(anchor: date, weeks_back: int) -> tuple[date, date]:
    """Monday-Sunday, ISO convention. weeks_back=1 is last week."""
    monday = anchor - timedelta(days=anchor.weekday(), weeks=weeks_back)
    return monday, monday + timedelta(days=6)


def _month_span(anchor: date, months_back: int) -> tuple[date, date]:
    first = anchor.replace(day=1)
    for _ in range(months_back):
        first = (first - timedelta(days=1)).replace(day=1)
    return first, first.replace(day=calendar.monthrange(first.year, first.month)[1])


def _weekend_span(anchor: date) -> tuple[date, date]:
    """The most recent Saturday-Sunday. Said on a Sunday this is yesterday and
    today; said on a Saturday it is the weekend before, since `_most_recent`
    never returns the anchor itself."""
    sat = _most_recent(anchor, 5)
    return sat, sat + timedelta(days=1)


# Expression -> (span builder, spoken clarification). The clarification is the
# tool's, not the model's; see the module docstring.
RANGE_EXPRESSIONS: dict[str, tuple] = {
    "last week": (lambda a: _week_span(a, 1), "Which day last week?"),
    "this week": (lambda a: _week_span(a, 0), "Which day this week?"),
    "the week before last": (
        lambda a: _week_span(a, 2),
        "Which day of that week?",
    ),
    "last month": (lambda a: _month_span(a, 1), "Which day last month?"),
    "over the weekend": (_weekend_span, "Saturday or Sunday?"),
    "the weekend": (_weekend_span, "Saturday or Sunday?"),
    # "sometime last week" hedges, but it still names last week -- so it is a
    # range with a known span, not irreducible vagueness.
    "sometime last week": (lambda a: _week_span(a, 1), "Which day last week?"),
}

# Expression -> (clarification, plausible answer window in days). The window is
# not used to resolve anything -- the tool still refuses -- but it constrains
# what the user is made to say next in generated data. "The other day" answered
# with a date a month back would teach a wrong prior about what the words mean,
# and this slice's only claim is quality per token.
VAGUE_EXPRESSIONS: dict[str, tuple[str, tuple[int, int]]] = {
    "the other day": ("Roughly how long ago?", (1, 10)),
    "the other night": ("Roughly how long ago?", (1, 10)),
    "the other week": ("Roughly how long ago?", (7, 21)),
    "a while back": ("About when -- a few days, or longer?", (14, 120)),
    "a while ago": ("About when -- a few days, or longer?", (14, 120)),
    "recently": ("How recently?", (1, 14)),
    "ages ago": ("Roughly when?", (60, 200)),
    "a bit ago": ("Roughly how long ago?", (1, 14)),
}


# --------------------------------------------------------------------------
# Clarify variety -- the treatment `mix_v1_sayvar` exists to price
# --------------------------------------------------------------------------
#
# **The measured problem.** `clarify` carries **4 distinct strings over 9,372
# observations** at `reason: vague` and 5 over 9,494 at `range`.
# `evals_payload_phrasing` moves that string to a wording the corpus does not
# contain and `refusal.clarify` goes 47/47 -> **0/47 on six checkpoints across
# two model sizes**, every failure `reworded`. The row was never measuring
# deference; it was measuring whether the model could reproduce one of four
# sentences it had seen 9,372 times.
#
# **The corpus contains its own control.** `answer` carries 1,652 distinct
# strings and `answer` is genuinely read -- a never-seen span comes back. Same
# model, same format, same position in the transcript. The obvious reading is
# that a field with four values is not one a model learns to read, it is one it
# learns to emit, and that reading is testable by moving the number.
#
# So these pools are the tenth finding's argument applied to a phrasing rather
# than to a fact: **the way to make copying the cheapest way to be right is to
# make reciting impossible.** `_invent_facts` did it by inventing a world too
# large to memorise; this does it by writing enough ways to ask the same
# question that no one of them is worth learning.
#
# **Index 0 is the trained string, on every pool.** `variant=0` is the default
# everywhere, so `data/raw/temporal.txt` regenerates byte-identical and every
# checkpoint already scored is reading exactly what it read before.
# `gen_temporal.py --wide-phrasing` is the arm.
#
# **Disjointness is the whole validity of the experiment**, not a nicety. If a
# single wording here appeared in `HELD_OUT_CLARIFY` or `HELD_OUT_CLARIFY_2`,
# the arm would be teaching to the test and a pass would mean nothing.
# `check_temporal.py` asserts it against both pools by importing them.
#
# --------------------------------------------------------------------------
# The dose is composed, not written, and the corpus says why
# --------------------------------------------------------------------------
#
# Measured on `data/raw/temporal.txt` and `data/raw/tools.txt`:
#
#     clarify   9 carriers over 18,866 uses  ->  2,096 uses each  -- recited
#     answer    1,652 carriers over 2,000    ->      1.2 uses each -- read
#
# **Three orders of magnitude, and the read/recited split lands on the same
# line.** A hand-written pool of sixteen per base reaches 131 uses per carrier,
# which is still a hundred times more repetition than the one field in this
# corpus a model demonstrably reads. A null result at that dose would say
# nothing except that the dose was small -- so the pools are built the way
# `_invent_facts` built its search index, by composition, and for the identical
# reason: **the point is not more phrasings, it is a space too large to learn
# as a set.**
#
# Frames x referents, both hand-written, every product a sentence that asks the
# base question. ~30 x ~14 puts each base near 400 and the whole set near 4,000,
# which is ~4.7 uses per carrier -- `answer`'s regime rather than `clarify`'s.
#
# **What composition costs, stated plainly:** a few products are stilted in a
# way a hand-written pool would not be. That is a real cost and it is accepted
# here because this is an arm and not the shipping corpus -- `mix_v1_wide` is
# the same kind of object. If the treatment works, the phrasings a shipped
# Corn-Jr uses are a separate and much smaller writing job, informed by knowing
# the dose that mattered.
_RANGE_FRAMES = (
    "Which day {r}?", "What day {r}?", "Which day was that {r}?",
    "Which one {r}?", "Any particular day {r}?", "Have you got a day {r}?",
    "Do you know which day {r}?", "Point me at a day {r}?",
    "Give me a day {r}?", "Which day {r} exactly?", "Sorry, which day {r}?",
    "Which of the days {r}?", "Pick a day {r}?", "So which day {r}?",
    "And which day {r}?", "Tell me the day {r}?", "I'll need the day {r}.",
    "Which day {r} do you mean?", "Just the day {r}?",
    "The day {r} would help.", "Can you narrow {r} to a day?",
    "Narrow {r} down to a day?", "Which day {r}, roughly?",
    "Which day {r} are we after?", "What day {r} was it?",
    "Which day {r} are you thinking of?", "Name a day {r}?",
    "A day {r} would do it.", "Which single day {r}?",
    "Down to one day {r}?",
)

_VAGUE_FRAMES = (
    "{r}?", "About {r}?", "Roughly {r}?", "Any idea {r}?",
    "Do you know {r}?", "Some sense of {r}?", "Give me {r}?",
    "Can you tell me {r}?", "Sorry, {r}?", "So {r}?", "And {r}?",
    "Just {r}?", "Rough idea {r}?", "Ballpark {r}?", "Any sense of {r}?",
    "Would you say {r}?", "Have you got {r}?", "What's {r}?",
    "I'll need {r}.", "{r} would help.", "Talk me through {r}?",
    "Remind me {r}?", "Point me at {r}?", "Narrow {r} for me?",
    "Roughly speaking, {r}?", "Approximately {r}?", "{r}, give or take?",
    "{r}, would you say?", "Best guess {r}?", "Even roughly, {r}?",
)


def _compose(base: str, frames: tuple[str, ...], refs: tuple[str, ...]) -> tuple[str, ...]:
    """`base` first, then every frame x referent product, deduped.

    Order is deterministic and `base` is pinned at index 0, which is what makes
    `variant=0` byte-identical to the corpus every checkpoint already read.
    """
    out = [base]
    for r in refs:
        for f in frames:
            s = f.format(r=r)
            # The referents are written lowercase so they read correctly
            # mid-frame; a frame that puts one first would otherwise open a
            # spoken sentence in lower case. Only the first character moves, so
            # `what date we're on` becomes `What date we're on` and nothing
            # else in the string is touched.
            s = s[0].upper() + s[1:]
            if s != base:
                out.append(s)
    return tuple(dict.fromkeys(out))


CLARIFY_COMPOSED: dict[str, tuple[str, ...]] = {
    "Which day last week?": _compose("Which day last week?", _RANGE_FRAMES, (
        "last week", "of last week", "in last week", "from last week",
        "during last week", "over last week", "that week", "of that week",
        "in that week", "from that week", "back then", "in that stretch",
        "of that stretch", "in the week you mean",
    )),
    "Which day this week?": _compose("Which day this week?", _RANGE_FRAMES, (
        "this week", "of this week", "in this week", "from this week",
        "during this week", "over this week", "that week", "of that week",
        "in that week", "from that week", "so far this week",
        "in the current week", "of the current week", "in the week you mean",
    )),
    "Which day of that week?": _compose("Which day of that week?", _RANGE_FRAMES, (
        "that week", "of that week", "in that week", "from that week",
        "during that week", "over that week", "back then", "in that stretch",
        "of that stretch", "in the week you mean", "of the week you mean",
        "within that week", "across that week", "somewhere in that week",
    )),
    "Which day last month?": _compose("Which day last month?", _RANGE_FRAMES, (
        "last month", "of last month", "in last month", "from last month",
        "during last month", "over last month", "that month", "of that month",
        "in that month", "from that month", "back then", "in that stretch",
        "of the month you mean", "somewhere in that month",
    )),
    "Saturday or Sunday?": _compose("Saturday or Sunday?", _RANGE_FRAMES, (
        "of the weekend", "in the weekend", "that weekend", "of that weekend",
        "in that weekend", "from that weekend", "over the weekend",
        "across the weekend", "of the two", "out of the two",
        "of those two days", "in that pair", "back then",
        "in the weekend you mean",
    )) + (
        "Sat or Sun?", "The Saturday or the Sunday?",
        "Do you mean Saturday or Sunday?", "Which half of the weekend?",
        "Saturday, or the day after?", "The first day or the second?",
    ),
    "Roughly how long ago?": _compose("Roughly how long ago?", _VAGUE_FRAMES, (
        "how long ago", "how long back", "how long since",
        "how far back", "how long ago that was", "how far back that was",
        "the gap", "the rough gap", "how long a gap", "how much time",
        "how long we're talking", "how far back we're talking",
        "how long before now", "roughly how long ago",
    )),
    "About when -- a few days, or longer?": _compose(
        "About when -- a few days, or longer?", _VAGUE_FRAMES, (
            "days or longer", "days or weeks", "days, weeks or months",
            "the sort of gap", "the rough scale", "what scale we're on",
            "how long a while", "what a while means here",
            "whether that's days or months", "the order of magnitude",
            "how big a gap", "days or something longer",
            "a short while or a long one", "how long a while that was",
        )),
    "How recently?": _compose("How recently?", _VAGUE_FRAMES, (
        "how recently", "how recent", "how lately", "how close to now",
        "how near to now", "how new this is", "what counts as recent",
        "how far back recent goes", "how recent recent is",
        "whether that's today or before", "how recently that was",
        "how fresh this is", "how lately that was", "how close that was",
    )),
    "Roughly when?": _compose("Roughly when?", _VAGUE_FRAMES, (
        "when", "roughly when", "about when", "what point",
        "whereabouts in time", "what sort of timeframe", "the rough when",
        "the timeframe", "when that was", "around when",
        "what period we're in", "where in time", "the rough point",
        "when we're talking about",
    )),
    "Sorry, what date was that?": _compose(
        "Sorry, what date was that?", _VAGUE_FRAMES, (
            "the date", "which date", "what date that was",
            "the date again", "that date again", "the date you mean",
            "which date you mean", "the date one more time",
            "what date we're on", "the date in question",
            "that date one more time", "the exact date",
            "the date you're after", "which date it was",
        )) + (
        "I didn't catch the date.", "Say the date again?",
        "Sorry, I missed the date.", "I'm not sure what date that is.",
    ),
    # The two boundary clarifies (`_RE_AHEAD`, `_RE_MONTH_NAMED`). Small
    # pools, written by hand: they name a limit rather than ask a question,
    # and index 0 is the base like every pool here.
    AHEAD_CLARIFY: (
        AHEAD_CLARIFY,
        "Dates ahead aren't mine -- I only work back from today.",
        "I can count back from today, not forward.",
        "Forward dates are past me. Backwards from today is what I do.",
        "That's ahead of today, and I only look back.",
    ),
    MONTH_CLARIFY: (
        MONTH_CLARIFY,
        "Month names are past me for now. A weekday, or the day of this month?",
        "I don't read month names yet -- try a weekday or the day of the month.",
        "Give me a weekday or a day of this month instead. Month names aren't mine yet.",
    ),
}

# The hand-written pools, kept because they are the readable statement of what
# each base question means and because `check_temporal.py` uses them as the
# naturalness spot-check the composed set cannot supply. Not used by the arm.
CLARIFY_SEEDS: dict[str, tuple[str, ...]] = {
    "Which day last week?": (
        "Which day last week?",
        "Which day of last week?",
        "Last week, but which day?",
        "Which one last week?",
        "Whereabouts in last week?",
        "Which day was that, last week?",
        "Have you got a day for last week?",
        "Which of last week's days?",
        "Any particular day last week?",
        "Point me at a day last week?",
        "Last week -- which day exactly?",
        "Which day are we talking about there?",
        "Sure, but which day of it?",
        "Do you know the day?",
        "Which day, though?",
        "Give me the day and I'll look.",
    ),
    "Which day this week?": (
        "Which day this week?",
        "Which day of this week?",
        "This week, but which day?",
        "Which one this week?",
        "Whereabouts in this week?",
        "Which day was that, this week?",
        "Have you got a day for this week?",
        "Which of this week's days?",
        "Any particular day this week?",
        "Point me at a day this week?",
        "This week -- which day exactly?",
        "Which day did you mean?",
        "Right, but which day of it?",
        "Do you know which day?",
        "Which day in particular?",
        "Name the day and I'll look.",
    ),
    "Which day of that week?": (
        "Which day of that week?",
        "Which day in that week?",
        "That week, but which day?",
        "Which one in that week?",
        "Whereabouts in that week?",
        "Which day of it was that?",
        "Have you got a day for that week?",
        "Which of that week's days?",
        "Any particular day that week?",
        "Point me at a day in that week?",
        "That week -- which day exactly?",
        "Which day of the week do you mean?",
        "Fine, but which day of it?",
        "Do you know the day itself?",
        "Which day within it?",
        "Tell me the day and I'll look.",
    ),
    "Which day last month?": (
        "Which day last month?",
        "Which day of last month?",
        "Last month, but which day?",
        "Which one last month?",
        "Whereabouts in last month?",
        "Which date last month?",
        "Have you got a date for last month?",
        "Which of last month's days?",
        "Any particular day last month?",
        "Point me at a date last month?",
        "Last month -- which day exactly?",
        "Which day of it are you after?",
        "Right, but which day of the month?",
        "Do you know the date?",
        "Which day of the month?",
        "Give me the date and I'll look.",
    ),
    "Saturday or Sunday?": (
        "Saturday or Sunday?",
        "Sat or Sun?",
        "The Saturday or the Sunday?",
        "Which of the two days?",
        "Saturday, or Sunday?",
        "One of the two -- which?",
        "Do you mean Saturday or Sunday?",
        "Which half of the weekend?",
        "Was it the Saturday?",
        "Saturday or the day after?",
        "Which day of the weekend?",
        "Either day in particular?",
        "The first day or the second?",
        "Weekend's two days -- which one?",
        "Have you got a day for it?",
        "Name the day and I'll look.",
    ),
    "Roughly how long ago?": (
        "Roughly how long ago?",
        "How long ago, roughly?",
        "About how long ago?",
        "How long back was that?",
        "How long ago are we talking?",
        "Any sense of how long ago?",
        "Rough idea how long ago?",
        "How long ago would you say?",
        "Give me a rough gap?",
        "How long since, roughly?",
        "Ballpark on how long ago?",
        "How long back, give or take?",
        "Do you know how long ago?",
        "Some idea of how long?",
        "Approximately how long ago?",
        "How long ago, give or take?",
    ),
    "About when -- a few days, or longer?": (
        "About when -- a few days, or longer?",
        "About when -- days, or longer than that?",
        "Days ago, or longer?",
        "A few days, or more like weeks?",
        "Are we talking days or weeks?",
        "Roughly -- days, weeks, months?",
        "Short while, or a long one?",
        "Days or longer, would you say?",
        "How long a while are we talking?",
        "A while meaning days, or meaning months?",
        "Recent-ish, or properly a while?",
        "Days? Weeks? Longer?",
        "Give me a rough scale for it?",
        "Is that days or is that months?",
        "About how long a gap?",
        "Roughly what sort of gap?",
    ),
    "How recently?": (
        "How recently?",
        "Recently meaning when?",
        "How recent is recent?",
        "How lately?",
        "Recent how, exactly?",
        "How close to now?",
        "In the last few days, or further?",
        "How recently, roughly?",
        "Recently -- as in today, or before?",
        "How near to now are we?",
        "What counts as recent here?",
        "How new is this one?",
        "Do you mean the last day or two?",
        "How far back does recent go?",
        "How recent are we talking?",
        "Recent -- how recent?",
    ),
    "Roughly when?": (
        "Roughly when?",
        "When, roughly?",
        "About when?",
        "Any rough idea when?",
        "Roughly what point?",
        "Whereabouts in time?",
        "Give me a rough when?",
        "When would you say?",
        "Some idea of when?",
        "Rough sense of when?",
        "Approximately when?",
        "When, give or take?",
        "Do you know roughly when?",
        "What sort of timeframe?",
        "Ballpark on when?",
        "Around when, would you say?",
    ),
    "Sorry, what date was that?": (
        "Sorry, what date was that?",
        "Sorry, which date was that?",
        "Sorry -- what date?",
        "What date was that, sorry?",
        "I didn't catch the date.",
        "Which date do you mean?",
        "Say the date again?",
        "Sorry, I missed the date.",
        "What date are we talking about?",
        "Could you give me the date?",
        "That date again?",
        "I'm not sure what date that is.",
        "Which date was it?",
        "Sorry, the date?",
        "What was the date again?",
        "Run the date past me again?",
    ),
}

# What the arm actually draws from: the composed pools, plus the hand-written
# seeds appended so the readable phrasings are in the corpus too. Index 0 stays
# the trained string on every pool.
CLARIFY_POOLS: dict[str, tuple[str, ...]] = {
    base: tuple(dict.fromkeys(composed + CLARIFY_SEEDS.get(base, ())))
    for base, composed in CLARIFY_COMPOSED.items()
}


def clarify_variant(base: str, variant: int) -> str:
    """The `variant`-th way of asking `base`. `variant=0` is always `base`.

    Modular rather than bounds-checked so a caller may draw from any range it
    likes without knowing a pool's size, which is what keeps the generator from
    having to import the pools to sample them.
    """
    pool = CLARIFY_POOLS.get(base)
    if not pool:
        return base
    return pool[variant % len(pool)]


def weekday_in_span(expression: str, span: tuple[date, date]) -> date | None:
    """The day `expression` names inside `span`, or None.

    **The answer to a question this tool asked.** `RANGE_EXPRESSIONS` clarifies
    with "Saturday or Sunday?" and "Which day last week?", and both invite a
    bare weekday -- which `resolve_date` cannot read, because a weekday name
    means nothing without the span it is being chosen from. Measured over the
    seven range expressions at one anchor, resolving such an answer to the most
    recent occurrence instead is right for the two weekend questions and lands a
    week or two outside the span on four of the others.

    So the span is the argument. Inside it, a weekday name is unambiguous
    exactly when the span covers seven days or fewer -- and `last month`, the
    one that does not, correctly returns None here rather than picking the first
    of five Mondays. That question wants a date and this is not the function
    that answers it.

    Pure, so `scripts/check_temporal.py` can hold the whole property -- every
    clarify question is answerable -- without a runtime.
    """
    e = " ".join(expression.lower().strip().rstrip("?.!").split())
    if e.startswith("on "):
        e = e[3:]
    wd = _weekday_index(e)
    if wd is None:
        return None
    start, end = span
    if (end - start).days >= 7:
        # More than one candidate. A wrong date is worse than a refusal.
        return None
    d = start
    while d <= end:
        if d.weekday() == wd:
            return d
        d += timedelta(days=1)
    return None


def resolve_date_tool(expression: str, anchor: date, variant: int = 0) -> dict:
    """The tool's actual return payload, in three shapes.

    `spoken` and `clarify` both exist so the model copies a phrasing rather
    than assembling one -- §2's push of content out of the parameters and into
    tools, applied to the wording of the answer itself.

    **`variant` selects how the question is worded and nothing else.** It
    defaults to 0, which is the string this function has always returned, so
    every existing corpus, checkpoint and eval item is untouched. See
    `CLARIFY_POOLS` for why the arm exists and what it is trying to price.
    """
    e = " ".join(expression.lower().strip().rstrip("?.!").split())

    if e in RANGE_EXPRESSIONS:
        span_of, clarify = RANGE_EXPRESSIONS[e]
        start, end = span_of(anchor)
        return {
            "ok": False,
            "reason": "range",
            "span": {"start": start.isoformat(), "end": end.isoformat()},
            "clarify": clarify_variant(clarify, variant),
        }

    if e in VAGUE_EXPRESSIONS:
        return {"ok": False, "reason": "vague",
                "clarify": clarify_variant(VAGUE_EXPRESSIONS[e][0], variant)}

    d = resolve_date(expression, anchor)
    if d is None:
        # Same reason, a different question: the parser did not read it,
        # and these two shapes say why so the person does not retype the
        # same date. Checked only after the parser has declined, so nothing
        # that resolved before resolves differently now.
        if _RE_AHEAD.search(e):
            clarify = AHEAD_CLARIFY
        elif _RE_MONTH_NAMED.search(e):
            clarify = MONTH_CLARIFY
        else:
            clarify = "Sorry, what date was that?"
        return {
            "ok": False,
            "reason": "unrecognised",
            "clarify": clarify_variant(clarify, variant),
        }
    return {
        "date": d.isoformat(),
        "weekday": WEEKDAYS[d.weekday()],
        "spoken": spoken_form(d),
    }


# --------------------------------------------------------------------------
# Clock time -- resolve_date's design at minute granularity (PLAN-TURN-2 §N)
# --------------------------------------------------------------------------
#
# **The model never does arithmetic, and "30 minutes before sunset" is
# arithmetic twice.** The chain this exists for is the scheduled pipe: a
# search returns "7:42 PM", the user said "30 minutes before that", and both
# strings are *spans* -- one copied out of the observation, one out of the
# utterance -- handed to a tool that computes. The copy discipline already
# has rulers on both moves; this function is only the arithmetic between
# them.
#
# **Not yet in `REGISTRY`, deliberately.** Declaring a tool changes the
# selection arity and the declaration every generator renders, so the switch
# flips with the corpus that teaches it (PLAN-TURN-2 §N's sequencing), not
# with the engine that serves it. Built first so the runtime half is never
# the thing the corpus waits on.

# "7:42 PM", "7:42pm", "19:42", "7 pm" -- the shapes a copied span actually
# arrives in, including the words around it ("sunset is at 7:42 PM today"),
# which is why this searches rather than matches.
_RE_CLOCK = re.compile(
    r"\b(\d{1,2})(?::(\d{2}))?\s*(a\.?m\.?|p\.?m\.?)?\b", re.IGNORECASE
)

_RE_OFFSET = re.compile(
    r"^(?:about |around |roughly )?"
    r"(a couple of |a couple |a few |half an |a quarter of an |an |a |\d+ )?"
    r"\s*(minutes?|mins?|hours?|hrs?)?\s*"
    r"(before|after|earlier|later|ahead of|past)"
    r"(?: that| it| then)?$"
)

_WORD_COUNTS = {"a": 1, "an": 1, "a couple": 2, "a couple of": 2, "a few": 3,
                "half an": 0.5, "a quarter of an": 0.25}


def _parse_clock(text: str) -> tuple[int, int] | None:
    """The first thing in `text` that reads as a clock time, or None.

    Searches rather than matches because the anchor is a copied span and a
    span routinely carries its sentence with it. A bare number with no
    minutes and no meridiem is refused -- "30" in "30 minutes" must never
    parse as an hour, which is the mistake that turns an offset into an
    anchor.
    """
    for m in _RE_CLOCK.finditer(text):
        hour, minute, meridiem = m.group(1), m.group(2), m.group(3)
        if minute is None and meridiem is None:
            continue
        h, mi = int(hour), int(minute or 0)
        if meridiem:
            if not 1 <= h <= 12 or mi > 59:
                continue
            h = h % 12 + (12 if meridiem.lower().startswith("p") else 0)
        elif not (0 <= h <= 23 and mi <= 59):
            continue
        return h, mi
    return None


def spoken_clock(h: int, mi: int) -> str:
    """19:12 -> "7:12 PM". Spoken, so twelve-hour with the meridiem."""
    meridiem = "AM" if h < 12 else "PM"
    twelve = h % 12 or 12
    return f"{twelve}:{mi:02d} {meridiem}"


def resolve_time_tool(expression: str, anchor: str) -> dict:
    """`resolve_date_tool`'s shapes, at minute granularity.

    `expression` is the offset in the user's own words ("30 minutes before",
    "half an hour after that"); `anchor` is the clock time it is measured
    from, usually copied out of an observation. The payload mirrors the date
    tool exactly -- a success carries `time`/`spoken`, every failure carries
    a `clarify` -- because the model reads shapes, and a fifth shape is the
    thing four findings taught this project not to hand it.

    An offset that crosses midnight wraps and says so in `spoken` ("12:15 AM
    the next day"), because a scheduler that silently fired nineteen hours
    early is the confident-wrong-date failure at minute scale.
    """
    at = _parse_clock(anchor)
    if at is None:
        return {"ok": False, "reason": "no_anchor",
                "clarify": "Before or after what time, exactly?"}
    e = " ".join(expression.lower().strip().rstrip("?.!").split())
    if e in ("then", "at that time", "that time"):
        return {"time": f"{at[0]:02d}:{at[1]:02d}",
                "spoken": spoken_clock(*at)}
    m = _RE_OFFSET.match(e)
    if m is None:
        return {"ok": False, "reason": "unrecognised",
                "clarify": "Sorry, how long before or after?"}
    count_word, unit, direction = m.group(1), m.group(2), m.group(3)
    count_word = (count_word or "").strip()
    if count_word.isdigit():
        n: float = int(count_word)
    else:
        n = _WORD_COUNTS.get(count_word, 1)
    # "half an before" carries no unit and means hours; a bare "before" with
    # no count and no unit is not an offset anyone said.
    if unit is None and count_word not in ("half an", "a quarter of an"):
        return {"ok": False, "reason": "unrecognised",
                "clarify": "Sorry, how long before or after?"}
    minutes = n * (60 if unit is None or unit.startswith(("hour", "hr"))
                   else 1)
    sign = -1 if direction in ("before", "earlier", "ahead of") else 1
    total = at[0] * 60 + at[1] + sign * round(minutes)
    wrapped = total // (24 * 60)
    total %= 24 * 60
    h, mi = divmod(total, 60)
    spoken = spoken_clock(h, mi)
    if wrapped > 0:
        spoken += " the next day"
    elif wrapped < 0:
        spoken += " the day before"
    return {"time": f"{h:02d}:{mi:02d}", "spoken": spoken}


# --------------------------------------------------------------------------
# Generation. Builds (expression, target) by construction.
# --------------------------------------------------------------------------


@dataclass
class Example:
    anchor: date
    expression: str
    target: date | None  # None when the expression cannot denote one day
    prep: str  # "on ", "at " or "" -- only used by the recall templates, where
    # "what did we do the 3rd" needs a preposition and "what day was the 3rd"
    # does not.
    family: str
    kind: str = "resolve"  # "resolve" | "range" | "vague"

    @property
    def tense(self) -> str:
        """Past, today or future. Drives both template choice and phrasing:
        "what was the date next Tuesday" is not English, and a corpus whose
        whole claim is quality-per-token cannot afford to teach it."""
        if self.target is None:
            return "past"  # ranges and vagueness only ever look backwards
        if self.target < self.anchor:
            return "past"
        return "today" if self.target == self.anchor else "future"


def _weekday_name(rng: random.Random, wd: int) -> str:
    """Capitalised most of the time, lowercase some of it.

    VISION.md §4 puts STT in front of this model, and speech recognisers do not
    capitalise reliably. A slice that only ever shows "Tuesday" trains the
    routing prior partly on a capital T that the real input will not supply,
    and the resolver has been case-insensitive from the start -- so the corpus
    was the only thing insisting on the capital.
    """
    name = WEEKDAYS[wd]
    return name.lower() if rng.random() < 0.25 else name


def _f_named_day(rng: random.Random, anchor: date) -> Example:
    # Every form here is one the resolver already accepted; the generator was
    # simply emitting half of them. "tonight" and "this morning" resolve to the
    # anchor and so land in TODAY_WORDS, which is what keeps them out of the
    # "what date was X" templates that would read as nonsense.
    word, offset = rng.choice(
        [("today", 0), ("tonight", 0), ("this morning", 0),
         ("yesterday", -1), ("last night", -1),
         ("the day before yesterday", -2), ("day before yesterday", -2),
         ("tomorrow", 1),
         ("the day after tomorrow", 2), ("day after tomorrow", 2)]
    )
    return Example(anchor, word, anchor + timedelta(days=offset), "", "named_day")


def _f_n_days(rng: random.Random, anchor: date) -> Example:
    n = rng.randint(1, 30)
    if n == 1 and rng.random() < 0.4:
        head = "a"  # "a day ago" -- `_as_int` reads a/an as one
    elif rng.random() < 0.45:
        head = WORD_NUMBERS[n]
    else:
        head = str(n)
    tail = rng.choice(["ago", "back"])
    expr = f"{head} day{'s' if n != 1 else ''} {tail}"
    return Example(anchor, expr, anchor - timedelta(days=n), "", "n_days")


def _f_vague_days(rng: random.Random, anchor: date) -> Example:
    expr, n = rng.choice(
        [("a couple days ago", 2), ("a couple days back", 2),
         ("a couple of days ago", 2), ("a couple of days back", 2),
         ("a few days ago", 3), ("a few days back", 3)]
    )
    return Example(anchor, expr, anchor - timedelta(days=n), "", "vague_days")


def _f_n_weeks(rng: random.Random, anchor: date) -> Example:
    n = rng.randint(1, 8)
    if n == 1 and rng.random() < 0.4:
        head = "a"
    else:
        head = WORD_NUMBERS[n] if rng.random() < 0.5 else str(n)
    expr = f"{head} week{'s' if n != 1 else ''} {rng.choice(['ago', 'back'])}"
    return Example(anchor, expr, anchor - timedelta(days=7 * n), "", "n_weeks")


def _f_last_weekday(rng: random.Random, anchor: date) -> Example:
    wd = rng.randrange(7)
    lead = rng.choice(["last", "this past", "past"])
    expr = f"{lead} {_weekday_name(rng, wd)}"
    return Example(anchor, expr, _most_recent(anchor, wd), "", "last_weekday")


def _f_before_last(rng: random.Random, anchor: date) -> Example:
    wd = rng.randrange(7)
    expr = f"the {_weekday_name(rng, wd)} before last"
    target = _most_recent(anchor, wd) - timedelta(days=7)
    return Example(anchor, expr, target, "", "before_last")


def _f_week_ago_weekday(rng: random.Random, anchor: date) -> Example:
    wd = rng.randrange(7)
    expr = f"a week ago {_weekday_name(rng, wd)}"
    target = _most_recent(anchor, wd) - timedelta(days=7)
    return Example(anchor, expr, target, "", "week_ago_weekday")


def _f_next_weekday(rng: random.Random, anchor: date) -> Example:
    wd = rng.randrange(7)
    lead = rng.choice(["next", "this coming", "coming"])
    expr = f"{lead} {_weekday_name(rng, wd)}"
    return Example(anchor, expr, _upcoming(anchor, wd), "", "next_weekday")


def _f_month_edge(rng: random.Random, anchor: date) -> Example:
    # Always carrying "the" keeps the expression grammatical standalone, which
    # is what the date templates need ("what day was the end of last month?").
    # The bare form stays in the resolver, since speech produces it.
    if rng.random() < 0.5:
        return Example(
            anchor, "the end of last month", _month_end(anchor, 1), "at ", "month_edge"
        )
    expr = rng.choice(
        ["the start of this month", "the beginning of this month",
         "the first of the month"]
    )
    return Example(anchor, expr, anchor.replace(day=1), "at ", "month_edge")


def _f_ordinal(rng: random.Random, anchor: date) -> Example:
    # 29-31 are safe as well as useful: `_recent_day_of_month` walks back a
    # month at a time rather than assuming the previous one is long enough, so
    # "the 30th" skips February instead of inventing it, and some month in the
    # last twelve always has the day. Those are the cases most likely to be
    # resolved wrongly, which is an argument for the corpus containing them.
    day = rng.randint(1, 31)
    expr = f"the {ordinal(day)}"
    return Example(anchor, expr, _recent_day_of_month(anchor, day), "on ", "ordinal")


def _f_range(rng: random.Random, anchor: date) -> Example:
    expr = rng.choice(sorted(RANGE_EXPRESSIONS))
    prep = "" if expr.startswith(("over", "last", "this", "the week")) else "on "
    return Example(anchor, expr, None, prep, "range", kind="range")


def _f_vague(rng: random.Random, anchor: date) -> Example:
    expr = rng.choice(sorted(VAGUE_EXPRESSIONS))
    return Example(anchor, expr, None, "", "vague", kind="vague")


FAMILIES = [
    (_f_named_day, 3),
    (_f_n_days, 5),
    (_f_vague_days, 3),
    (_f_n_weeks, 3),
    (_f_last_weekday, 5),
    (_f_before_last, 3),
    (_f_week_ago_weekday, 2),
    (_f_next_weekday, 2),
    (_f_month_edge, 2),
    (_f_ordinal, 3),
    # ~11% of the slice between them. Enough that the failure path is not
    # exotic, little enough that hedging does not become the default.
    (_f_range, 2),
    (_f_vague, 2),
]

# "Requests phrased 50 different ways mapping to one intent" -- DATA.md §3.
# Recall templates take the preposition; date templates read the expression
# bare, which is why every family's expression is a standalone noun phrase.
RECALL_TEMPLATES = [
    "what did we do {p}{e}?",
    "what did we talk about {p}{e}?",
    "remind me what happened {p}{e}",
    "what was I working on {p}{e}?",
    "pull up {p}{e}",
    "what did I ask you {p}{e}?",
    "do you remember {p}{e}?",
    "check {p}{e} for me",
    "anything from {p}{e}?",
    "what's in the log for {p}{e}?",
    "go back to {p}{e}",
    "what happened {p}{e} again?",
    "did I say anything {p}{e}?",
    "read me {p}{e}",
    "hey what did we cover {p}{e}",
    "what did we get up to {p}{e}?",
    "show me {p}{e}",
    "what was going on {p}{e}?",
    "I need the log for {p}{e}",
    "what did I do {p}{e}?",
    "did anything happen {p}{e}?",
    "remind me about {p}{e}",
    "look up {p}{e}",
    "what notes do I have from {p}{e}?",
    "tell me about {p}{e}",
    "what came up {p}{e}?",
    "did we discuss anything {p}{e}?",
    "bring up {p}{e}",
    "what's on record for {p}{e}?",
    "run me through {p}{e}",
]

DATE_TEMPLATES_PAST = [
    "what was the date {e}?",
    "what day was {e}?",
    "when was {e} exactly?",
    "which day was {e}?",
    "can you work out what date {e} was?",
    "what date did {e} land on?",
    "remind me what {e} was",
    "when exactly was {e}?",
    "give me the date for {e}",
    "do you know what date {e} was?",
    "what date was {e} again?",
    "tell me the date {e} fell on",
    "put a date on {e} for me",
    "what's the actual date for {e}?",
]

# Present tense: future expressions, and past-tense-inappropriate cases like an
# ordinal that happens to land on the anchor ("what day is the 9th?").
DATE_TEMPLATES_NONPAST = [
    "what's the date {e}?",
    "what day is {e}?",
    "when is {e} exactly?",
    "which day is {e}?",
    "what date does {e} land on?",
    "work out what date {e} is",
    "what's {e} going to be?",
    "when exactly is {e}?",
    "give me the date for {e}",
    "do you know what date {e} is?",
    "what date is {e} again?",
    "tell me the date {e} falls on",
    "put a date on {e} for me",
    "what's the actual date for {e}?",
]

# "today" needs its own pool -- "what date was today" is not something anyone
# says, and "what's today's date" is something everyone says. These templates
# carry no {e} slot, so they are only safe when the expression *is* the word
# today; using them for "the 9th" would train a call the user never uttered.
TODAY_WORDS = {"today", "tonight", "this morning"}
DATE_TEMPLATES_TODAY = [
    "what's today's date?",
    "what day is it?",
    "what's the date?",
    "what day is it today?",
    "remind me what today is",
    "what's the date today?",
    "what's the date right now?",
    "today's date?",
    "can you tell me what day it is?",
    "what day of the week is it?",
    "what's today?",
    "give me today's date",
]

# --------------------------------------------------------------------------
# Wide left context -- README's twenty-eighth finding, and the arm it asks for
# --------------------------------------------------------------------------
#
# The finding: all 52 `temporal.route` failures under paraphrase are
# `wrong_expression` -- right tool, well-formed JSON, wrong words -- and they
# split almost entirely on the *single token* preceding the slot. 96.9% where
# the model has seen that left edge before an expression, 80.5% where it has
# not, replicated on a second checkpoint. The model is not reading the phrase;
# it is segmenting it off a left-boundary cue.
#
# The pools above are why. Fourteen templates in `DATE_TEMPLATES_PAST` carry
# **six** distinct left edges between them -- `date`, `did`, `for`, `on`,
# `was`, `what` -- so the generator varies what goes *in* the slot
# exhaustively and what sits immediately to its left hardly at all. That is
# §11's copyable-span rule ("a span the model must copy has to come from a
# space too large to memorise as a set") applying to the span's *boundaries*,
# which nobody had thought to count.
#
# These pools are the intervention. They are **additive and opt-in**: `render`
# defaults to `wide=False` and the corpus every existing checkpoint read
# rebuilds byte-identical, because a code change that silently moved
# `data/raw/temporal.txt` would invalidate nine scorecards under unchanged
# filenames. `gen_temporal.py --wide-left-context` writes the other arm.
#
# Written to a rule, so this is a manipulation of the left edge and not just
# "more templates": every entry below had to introduce a left edge the base
# pool does not have, or place the slot where the base pool never places it
# (first). Two shapes are deliberate and matter most -- the slot-initial ones,
# where there is no left cue at all, and the ones ending `of {e}` / `for {e}`,
# where the cue is a preposition that could be read as part of the span.
#
# **None of these is a carrier from `scripts/paraphrase_evals.py`.** If the
# training pool contained the eval's phrasings the arm would be circular, and
# that script's `check_disjoint` fails the build if it ever does.

DATE_WIDE_PAST = DATE_TEMPLATES_PAST + [
    "{e}, what date?",
    "{e}? what date was that",
    "{e} was when, exactly?",
    "date of {e}?",
    "I'm after the date of {e}",
    "sort out the date of {e}",
    "about {e} -- what date?",
    "any idea about {e}?",
    "we're talking about {e} -- what date?",
    "so, {e} -- date please",
    "just {e} -- what date?",
    "I meant {e} -- what date?",
    "when I say {e}, what date?",
    "put {e} into a date for me",
    "turn {e} into a date",
    "convert {e} to a date",
    "which date does {e} refer to?",
    "what date are we calling {e}?",
    "hold on, {e} was which date?",
    "right then, {e} -- what date?",
    "quickly, {e} -- what date?",
    "let me get {e} straight -- what date?",
    "regarding {e}, which date?",
    "my note says {e} -- date?",
]

DATE_WIDE_NONPAST = DATE_TEMPLATES_NONPAST + [
    "{e}, what date?",
    "{e}? what date is that",
    "{e} is when, exactly?",
    "date of {e}?",
    "I'm after the date of {e}",
    "sort out the date of {e}",
    "about {e} -- what date?",
    "any idea about {e}?",
    "we're talking about {e} -- what date?",
    "so, {e} -- date please",
    "just {e} -- what date?",
    "I meant {e} -- what date?",
    "when I say {e}, what date?",
    "put {e} into a date for me",
    "turn {e} into a date",
    "convert {e} to a date",
    "which date does {e} refer to?",
    "what date are we calling {e}?",
    "hold on, {e} is which date?",
    "right then, {e} -- what date?",
    "quickly, {e} -- what date?",
    "let me get {e} straight -- what date?",
    "regarding {e}, which date?",
    "my note says {e} -- date?",
]

# `today` carries no slot, so it has no left edge to widen. It is here for
# symmetry of the call site and to keep the wide arm's surface variety from
# falling behind the base arm's on this one family.
DATE_WIDE_TODAY = DATE_TEMPLATES_TODAY + [
    "what's the date on today's entry?",
    "which day of the month is it?",
    "date today?",
    "go on, what's the date?",
    "the date, if you don't mind?",
    "what day have we got today?",
]

RECALL_WIDE = RECALL_TEMPLATES + [
    "{p}{e}, what happened?",
    "{p}{e}? what did we do",
    "so {p}{e} -- what did we do?",
    "just {p}{e} for now",
    "how about {p}{e}?",
    "what about {p}{e}?",
    "I'm curious about {p}{e}",
    "hold on, what did we do {p}{e}?",
    "right then, {p}{e}",
    "quickly, {p}{e}?",
    "let's talk {p}{e}",
    "regarding {p}{e}, anything?",
    "the log for {p}{e}, please",
    "search the log {p}{e}",
    "scan the log {p}{e}",
    "find whatever we have {p}{e}",
    "read out the log {p}{e}",
    "open the log {p}{e}",
    "my notes {p}{e} -- what's there?",
    "we spoke {p}{e} -- about what?",
]


# Future dates get no `recall_day` chain: §5.2's day log is a record of days
# that happened. Routing them to resolve_date is still worth teaching -- the
# calendar tool that would consume the result does not exist yet.
SAY_FORMS = {
    "past": "That was {s}.",
    "today": "That's today -- {s}.",
    "future": "That'll be {s}.",
}


# How the user answers the clarifying question. Short, because this is speech.
ANSWER_TEMPLATES = [
    "{e}",
    "{e} I think",
    "let's say {e}",
    "make it {e}",
    "it was {e}",
    "{e}, sorry",
    "{e} maybe",
    "probably {e}",
    "try {e}",
    "call it {e}",
    "I think {e}",
    "{e}, that one",
]


def sample_expression(rng: random.Random, anchor: date) -> Example:
    builders, weights = zip(*FAMILIES)
    return rng.choices(builders, weights=weights, k=1)[0](rng, anchor)


def _followup_in_span(
    rng: random.Random, anchor: date, span: tuple[date, date]
) -> tuple[str, date] | None:
    """A resolvable expression naming a day inside `span`.

    Answering "which day last week?" with something that resolves outside last
    week would be incoherent data, so the day is drawn from the span and then
    checked to round-trip -- "the 5th" only means the 5th of the intended month
    when the anchor is late enough in its own month.
    """
    start, end = span
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    rng.shuffle(days)
    for d in days:
        if d <= anchor and _recent_day_of_month(anchor, d.day) == d:
            return f"the {ordinal(d.day)}", d
    return None


def _followup_in_window(
    rng: random.Random, anchor: date, lo: int, hi: int
) -> tuple[str, date]:
    """A resolvable expression naming a day `lo`..`hi` days before the anchor.

    Answering "the other day" with a date a month back would teach that the
    phrase means a month; the window keeps the recovery turn semantically
    honest. Exact either way -- the offset is chosen first and the expression
    is rendered from it.
    """
    n = rng.randint(lo, hi)
    if n >= 14 and rng.random() < 0.5:
        weeks = max(1, round(n / 7))
        n = weeks * 7
        head = WORD_NUMBERS[weeks] if weeks <= 30 and rng.random() < 0.5 else str(weeks)
        expr = f"{head} week{'s' if weeks != 1 else ''} ago"
    else:
        head = WORD_NUMBERS[n] if n <= 30 and rng.random() < 0.5 else str(n)
        expr = f"{head} day{'s' if n != 1 else ''} ago"
    return expr, anchor - timedelta(days=n)


def _render_ambiguous(ex: Example, rng: random.Random, payload: dict,
                      arm: str = "base", phrasing: bool = False,
                      daylog: bool = False) -> str:
    """The tool could not resolve it, so Corn-Jr asks -- using the tool's own
    wording. Roughly 60% of these carry on to a resolution, because a corpus
    where every clarification is a dead end teaches the question but not what
    it is for."""
    utterance = rng.choice(pools(arm)[0]).format(p=ex.prep, e=ex.expression)
    call = json.dumps(
        {"name": "resolve_date", "arguments": {"expression": ex.expression}}
    )
    lines = [
        f"{D_DAY}{ex.anchor.isoformat()} {WEEKDAYS[ex.anchor.weekday()]}",
        f"{D_USER}{utterance}",
        f"{D_CALL}{call}",
        f"{D_OBS}{json.dumps(payload)}",
        f"{D_SAY}{payload['clarify']}",
    ]

    follow = None
    if rng.random() < 0.6:
        if ex.kind == "range":
            span = payload["span"]
            follow = _followup_in_span(
                rng,
                ex.anchor,
                (date.fromisoformat(span["start"]), date.fromisoformat(span["end"])),
            )
        else:
            follow = _followup_in_window(rng, ex.anchor, *VAGUE_EXPRESSIONS[ex.expression][1])

    if follow is not None:
        expr2, _ = follow
        # A second draw, not the first one reused. The follow-up is a different
        # turn asking a different question, and giving it the same variant would
        # make the pair predictable from its first half -- which is the
        # memorisable structure this arm exists to remove.
        payload2 = resolve_date_tool(
            expr2, ex.anchor, rng.randrange(4096) if phrasing else 0
        )
        lines += [
            f"{D_USER}{rng.choice(ANSWER_TEMPLATES).format(e=expr2)}",
            f"{D_CALL}"
            + json.dumps(
                {"name": "resolve_date", "arguments": {"expression": expr2}}
            ),
            f"{D_OBS}{json.dumps(payload2)}",
            f"{D_CALL}"
            + json.dumps(
                {"name": "recall_day", "arguments": {"date": payload2["date"]}}
            ),
        ]
        # The recovery turn ends on the same unanswered call as the plain chain
        # and for the same reason, so it takes the same close. 11,346 of the
        # 90,293 truncations are here.
        lines += _daylog_close(payload2["date"], rng, daylog)
    lines.append(D_END)
    return "\n".join(lines)


ARMS = ("base", "mid", "wide")


def _first_half(base_pool: list[str], wide_pool: list[str]) -> list[str]:
    """The base pool plus the first half of what the wide pool adds to it.

    A **rule** rather than a hand-picked list, and stated before any of the
    mid arm's numbers existed, because the wide pools were written after
    seeing which left edges failed and a second hand-picked subset would
    inherit that freedom twice over. File order is the order these were
    written in the twenty-eighth finding's session; nothing about it knows
    which edges the eval carriers use or how often.

    On `date_past` it lands the edge count at exactly **12**, between the
    base pool's 6 and the wide pool's 24, which is the bracket the
    twenty-ninth finding's open question asked for.
    """
    return base_pool + wide_pool[len(base_pool):][:(len(wide_pool) - len(base_pool)) // 2]


RECALL_MID = _first_half(RECALL_TEMPLATES, RECALL_WIDE)
DATE_MID_TODAY = _first_half(DATE_TEMPLATES_TODAY, DATE_WIDE_TODAY)
DATE_MID_PAST = _first_half(DATE_TEMPLATES_PAST, DATE_WIDE_PAST)
DATE_MID_NONPAST = _first_half(DATE_TEMPLATES_NONPAST, DATE_WIDE_NONPAST)


def pools(arm: str = "base") -> tuple[list[str], list[str], list[str], list[str]]:
    """(recall, today, past, nonpast) template pools for this arm.

    One function rather than four conditionals so `render` and
    `_render_ambiguous` cannot disagree about which arm they are in -- they
    are two call sites of the same choice, and the fifth finding's whole
    lesson is that a quantity two places can set differently will eventually
    be set differently.

    Three arms now. `base` and `wide` return exactly what they always did, so
    `data/raw/temporal.txt` and `data/raw/temporal_wide.txt` both rebuild
    byte-identical and no scorecard written against either moves.
    """
    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r} -- one of {ARMS}")
    if arm == "wide":
        return RECALL_WIDE, DATE_WIDE_TODAY, DATE_WIDE_PAST, DATE_WIDE_NONPAST
    if arm == "mid":
        return RECALL_MID, DATE_MID_TODAY, DATE_MID_PAST, DATE_MID_NONPAST
    return (RECALL_TEMPLATES, DATE_TEMPLATES_TODAY,
            DATE_TEMPLATES_PAST, DATE_TEMPLATES_NONPAST)


def _daylog_close(iso: str, rng: random.Random, daylog: bool) -> list[str]:
    """The two lines that finish a `recall_day` chain, or none.

    Imported inside the function rather than at module scope, because
    `corn/daylog.py` imports `WEEKDAYS` from here and a top-level import would
    close the cycle. The cost is one lookup per chained example and it only
    happens when the flag is on.

    The date comes from the `resolve_date` payload, so the log is for the day
    the tool named and not for one drawn again -- the whole point of the chain
    is that the second call's argument came from the first call's answer, and
    generating an unrelated day here would break that at the only place a model
    could see it.
    """
    if not daylog:
        return []
    from .daylog import day_log, speak

    log = day_log(date.fromisoformat(iso), rng)
    said, _topic = speak(log, rng)
    return [f"{D_OBS}{json.dumps(log)}", f"{D_SAY}{said}"]


def render(ex: Example, rng: random.Random, arm: str = "base",
           phrasing: bool = False, daylog: bool = False) -> str:
    """One training example as text. The model's job is visible here: copy the
    expression into the call, then copy the tool's output into whatever comes
    next. It never produces a date it was not handed.

    `arm` selects the left-context pools -- `base` is the corpus every
    checkpoint before the twenty-ninth finding read, `wide` is that finding's
    intervention, `mid` is the bracket between them. It defaults to `base`, so
    every existing corpus rebuilds byte-identical.

    **`phrasing` is a second and orthogonal axis**, and they are kept separate
    on purpose: `arm` varies the *user's* words and `phrasing` varies the
    *tool's*. `mix_v1_sayvar` is `arm="base"` with `phrasing=True`, which is one
    variable away from `mix_v1` rather than two. Off by default, so nothing
    already generated moves.

    **`daylog` is a third axis and it finishes the chain rather than varying
    it.** With it off -- the default, and what every corpus in the project was
    built with -- a chained example ends on the `recall_day` call and the
    transcript stops there: no observation, no reply. That is 55% of this slice
    (90,293 of 164,263 transcripts, counted 2026-08-18) and it is the one tool
    in the project whose answer the corpus never shows. `corn/daylog.py` carries
    the argument for why the "generate the call, never the answer" rule is right
    for `resolve_date` and wrong for `recall_day`.

    With it on, the chain gains `<|obs|>` with the day's entries and `<|say|>`
    with a reply that reads one of them back. Nothing else about the example
    changes -- same anchor, same expression, same `resolve_date` payload, same
    templates -- so `mix_v1_daylog` is one variable away from `mix_v1`.

    Off by default, for the reason `arm` and `phrasing` are: with all three at
    their defaults `data/raw/temporal.txt` rebuilds byte-identical and the
    nineteen scorecards written against it stay comparable.
    """
    payload = resolve_date_tool(
        ex.expression, ex.anchor, rng.randrange(4096) if phrasing else 0
    )
    if ex.kind != "resolve":
        return _render_ambiguous(ex, rng, payload, arm, phrasing, daylog)

    recall_pool, today_pool, past_pool, nonpast_pool = pools(arm)

    tense = ex.tense
    chained = tense != "future" and rng.random() < 0.6
    if chained:
        template = rng.choice(recall_pool)
    elif ex.expression in TODAY_WORDS:
        template = rng.choice(today_pool)
    elif tense == "past":
        template = rng.choice(past_pool)
    else:
        template = rng.choice(nonpast_pool)
    utterance = template.format(p=ex.prep, e=ex.expression)

    call = json.dumps(
        {"name": "resolve_date", "arguments": {"expression": ex.expression}}
    )
    lines = [
        f"{D_DAY}{ex.anchor.isoformat()} {WEEKDAYS[ex.anchor.weekday()]}",
        f"{D_USER}{utterance}",
        f"{D_CALL}{call}",
        f"{D_OBS}{json.dumps(payload)}",
    ]
    if chained:
        recall = json.dumps(
            {"name": "recall_day", "arguments": {"date": payload["date"]}}
        )
        lines.append(f"{D_CALL}{recall}")
        lines += _daylog_close(payload["date"], rng, daylog)
    else:
        lines.append(D_SAY + SAY_FORMS[tense].format(s=payload["spoken"]))
    lines.append(D_END)
    return "\n".join(lines)


def generate(
    n: int,
    seed: int = 1337,
    start: date = ANCHOR_START,
    end: date = ANCHOR_END,
):
    """Yield `n` Examples with anchors spread over [start, end]."""
    rng = random.Random(seed)
    span = (end - start).days
    for _ in range(n):
        anchor = start + timedelta(days=rng.randrange(span + 1))
        yield sample_expression(rng, anchor)
