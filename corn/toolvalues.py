"""Composed parameter values for the declared-tools slice.

`corn/toolspace.py` varies the tool *name* across a space of ~38,000 and reads
its argument value out of a hand-written table of **78 strings across 20
domains**. `scripts/check_copyable.py` has declared that below floor since the
slice was built, with the number written down rather than fixed:

    77 distinct values at ~2,130 uses each. That is not near the floor, it is
    `clarify`'s untreated regime to two significant figures (2,096) -- the exact
    cardinality the thirty-third finding shows teaches recitation rather than
    reading.

and its own suggested repair, which is what this module is:

    Composing values the way names are composed is the fix and is not expensive.

**Why it stopped being optional.** At `mix_v2`'s shares a 5B run reads this
slice **7.47 times**, which takes the value slot from 684 uses each to ~5,100.
The forty-fifth finding's supply table is where that comes from. A bigger
generated file does not help: the table is 78 strings whatever the file size, so
volume moves the exposure from "read the file eight times" to "the same 78
strings appear eight times more often" and the model cannot tell those apart.
**Cardinality is the axis, and it is the one thing more generation cannot buy.**

## The size that is actually needed, computed rather than chosen

At 5B the slice takes 250M tokens and the value slot is used ~383,000 times,
spread over 16 training domains -- so ~24,000 uses **per domain**. §11's regimes
put 1.19-2.7 uses in the working range and 2,096 in the failing one, with 13
demonstrated working. Pricing a domain at ~40 uses each therefore wants **~600
values per domain**, and at ~13 uses it wants ~1,800. The spec below targets the
first and clears it on every domain, which takes the slice from 78 values to
five figures.

## Composed from real words, not from syllables

`corn/toolgen.py`'s `_composed_book` invents names -- `Fenafell Belundstone` --
because a contact book only has to be *a* book and inventing it maximises the
space. That reasoning does not carry here. These strings are what the **user
says**, and VISION §6 wants his speech to sound like speech, so an invented
syllable string in a timer request would buy cardinality by making the corpus
wrong. Everything below composes real words into real phrases.

## Keyed on the domain noun, not the parameter name

`title` belongs to both `track` and `meeting`, and "the slow piano one" is a
song and not a standup. Keying on the parameter would let one leak into the
other, so the spec below is keyed on `domain[0]`.

## Disjointness is asserted, not assumed

`HELD_OUT_DOMAINS` is what the `domain` eval level draws on, so a training value
appearing in a held-out domain's pool would make an eval item reachable from the
corpus. The four held-out nouns are built from their own vocabulary and
`check()` fails the build on any overlap -- the same rule `check_tools.py`
group 4 enforces between the two contact books, and for the same reason. The
first draft of this module failed that check on eight strings, which is why it
is a check and not a comment.
"""

from __future__ import annotations

import random

# The floor `scripts/check_copyable.py` declares for a copy slot.
FLOOR = 1_000

# Per-domain target, from the arithmetic in the docstring.
PER_DOMAIN_FLOOR = 600

# ---------------------------------------------------------------------------
# Time and duration, which compose from number words rather than from adjectives
# ---------------------------------------------------------------------------

_NUMS = (
    "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "eighteen", "twenty", "twenty-five", "thirty", "thirty-five", "forty",
    "forty-five", "fifty", "fifty-five", "sixty", "ninety",
)
_DUR_UNITS = ("seconds", "minutes", "hours")
_HOURS = ("one", "two", "three", "four", "five", "six", "seven", "eight",
          "nine", "ten", "eleven", "twelve")
_MINUTES = (
    "o'clock", "five", "ten", "fifteen", "twenty", "twenty-five", "thirty",
    "thirty-five", "forty", "forty-five", "fifty", "fifty-five", "oh five",
)
_MERIDIEM = ("am", "pm", "")
_TO_PAST = ("quarter past", "half past", "quarter to", "ten past", "twenty past",
            "ten to", "twenty to", "five past", "five to")


def _durations() -> tuple[str, ...]:
    """Unit-appropriate ranges. One number pool across all three units gives
    "ninety hours", which is not a timer anybody sets -- cardinality bought by
    making the corpus wrong is the thing this module exists to avoid."""
    secs = ("five", "ten", "fifteen", "twenty", "twenty-five", "thirty",
            "thirty-five", "forty", "forty-five", "fifty", "fifty-five",
            "sixty", "seventy", "seventy-five", "eighty", "ninety")
    mins = _NUMS[:24]
    hrs = ("two", "three", "four", "five", "six", "seven", "eight", "nine",
           "ten", "eleven", "twelve")
    out = [f"{n} seconds" for n in secs]
    out += [f"{n} minutes" for n in mins]
    out += [f"{n} hours" for n in hrs]
    out += [f"{n} and a half hours" for n in hrs]
    out += [f"{n} and a half minutes" for n in mins[:12]]
    out += [f"an hour and {n} minutes" for n in mins]
    out += [f"{a} hours {b} minutes" for a in hrs[:6] for b in mins]
    out += [f"{a} minutes {b} seconds" for a in mins for b in secs]
    out += ["half an hour", "an hour", "a minute", "a couple of minutes",
            "a minute and a half", "two and a half hours"]
    return tuple(dict.fromkeys(out))


def _times() -> tuple[str, ...]:
    out = []
    for h in _HOURS:
        for m in _MINUTES:
            s = f"{h} o'clock" if m == "o'clock" else f"{h} {m}"
            for mer in _MERIDIEM:
                out.append(f"{s} {mer}".strip())
        for tp in _TO_PAST:
            for mer in _MERIDIEM:
                out.append(f"{tp} {h} {mer}".strip())
    return tuple(dict.fromkeys(out))


# ---------------------------------------------------------------------------
# Everything else: frames x modifiers x heads. The empty modifier is in every
# pool so bare forms ("the hotel") exist beside modified ones ("the late hotel
# booking"), which is what the utterances actually sound like.
# ---------------------------------------------------------------------------

def _article(phrase: str) -> str:
    """`a` or `an`, agreeing with what actually follows it.

    The frames carry a literal "a {a}" and the modifier slot may be empty, so
    the word after the article is not known until the product is built. A first
    draft emitted "a oxidation firing".
    """
    return "an" if phrase[:1].lower() in "aeiou" else "a"


def _spec(frames: tuple[str, ...], mods: tuple[str, ...],
          heads: tuple[str, ...]) -> tuple[str, ...]:
    out = []
    for f in frames:
        for m in mods:
            for h in heads:
                inner = f"{m} {h}".strip()
                # The article agrees with the *product*, not with the frame.
                frame = _article(inner) + f[1:] if f.startswith("a {a}") else f
                out.append(frame.format(a=inner))
    return tuple(dict.fromkeys(out))


# A reminder is a verb *and* an object it can actually take. An untyped product
# gives "defrost the landlord" and "wrap Dan", which buys cardinality by putting
# sentences in the corpus that nobody would say. Four typed groups instead, each
# a product within itself.
_TASK_GROUPS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    # get in touch with a person or an organisation
    (("call", "ring", "email", "text", "chase", "confirm with", "get back to",
      "check in with", "write to", "phone"),
     ("the dentist", "the doctor", "the vet", "the plumber", "the landlord",
      "mum", "dad", "Ann", "Dan", "the neighbours", "the council", "the bank",
      "the accountant", "the school", "the optician", "the garage",
      "the window cleaner", "the surgery", "the letting agent", "the builder",
      "the insurers", "the electrician")),
    # move a physical thing about
    (("collect", "drop off", "pick up", "post", "return", "unpack", "wrap",
      "label", "put away", "take back"),
     ("the parcel", "the dry cleaning", "the library books", "the tickets",
      "the prescription", "the shopping", "the recycling", "the tools",
      "the spare key", "the paperwork", "the printer cartridge", "the bedding",
      "the empties", "the paint", "the deliveries", "the samples")),
    # money and admin
    (("pay", "renew", "top up", "cancel", "sort out", "budget for", "query",
      "set up"),
     ("the gas bill", "the insurance", "the subscription", "the meter",
      "the council tax", "the road tax", "the water bill", "the licence",
      "the standing order", "the direct debit", "the phone contract",
      "the parking permit", "the broadband", "the pension", "the deposit")),
    # things around the house
    (("water", "feed", "defrost", "check on", "clear out", "cover up",
      "bring in", "turn off", "top up", "wipe down"),
     ("the plants", "the freezer", "the bins", "the boiler", "the greenhouse",
      "the cat", "the fish", "the gutters", "the shed", "the compost",
      "the fire alarm", "the hedge", "the pond", "the birdfeeder",
      "the seedlings", "the porch light")),
)

_NOTE_SUBJECTS = (
    "the boiler", "bin day", "the spare key", "the meter reading",
    "the wifi password", "the car insurance", "the fuse box", "the stopcock",
    "the bin store code", "the alarm code", "the loft hatch", "the water filter",
    "the parking permit", "the recycling", "the smoke alarm", "the gate latch",
    "the oil tank", "the boiler pressure", "the outside tap", "the septic tank",
    "the roof valley", "the chimney", "the drain cover", "the shed padlock",
)
_NOTE_PREDICATES = (
    "is serviced in May", "moved to Thursday", "is with Ann",
    "needs doing in spring", "is behind the kitchen door", "runs out in March",
    "is under the stairs", "was changed last week", "is in the top drawer",
    "expires at the end of the month", "needs a new battery",
    "is due for a check", "is on the shelf by the door", "sticks in the cold",
    "is booked for the autumn", "needs bleeding", "was replaced in June",
    "is logged with the council", "comes out on the first", "wants resealing",
    "is covered until April", "needs the long key", "drips in the frost",
    "is listed on the deeds", "was quoted last month", "is overdue a service",
)

_SONG_FRAMES = ("the one about {a}", "that {a} song", "the {a} one",
                "the one with {a}", "that thing about {a}", "the {a} track")
_SONG_MODS = ("", "slow", "long", "quiet", "old", "live", "acoustic", "early")
_SONG_HEADS = (
    "the river", "summer", "piano", "the live version", "the acoustic take",
    "rain", "the intro", "the harmonica", "driving home", "the sea",
    "the brass", "winter", "the build", "the ending", "the choir",
    "the whistling", "the double bass", "the fade out", "the harmony",
    "the drum fill", "the string part", "the key change",
)

_MEETING_FRAMES = ("the {a}", "a {a}", "the {a} one")
_MEETING_MODS = ("", "weekly", "monthly", "quarterly", "short", "long",
                 "early", "late", "urgent")
_MEETING_HEADS = (
    "standup", "catch-up with Dan", "review", "call with the builders",
    "retro", "one to one", "handover", "kickoff", "planning session",
    "budget call", "site visit", "board call", "check-in with Ann",
    "supplier call", "design review", "sprint planning", "sync",
    "debrief", "walkthrough", "status call", "escalation call",
    "post-mortem", "intro call", "training session",
)

_DISH_FRAMES = ("{a}", "the {a}", "some {a}")
_DISH_MODS = ("", "slow-cooked", "quick", "leftover", "proper", "easy",
              "vegetarian", "one-pot", "batch")
_DISH_HEADS = (
    "carbonara", "soda bread", "lentil soup", "beef stew", "lemon drizzle",
    "fish pie", "risotto", "shepherd's pie", "dal", "focaccia", "chilli",
    "ragu", "toad in the hole", "banana bread", "katsu curry", "paella",
    "cottage pie", "chowder", "scones", "gnocchi", "minestrone", "tagine",
    "hotpot", "flapjacks", "moussaka",
)

_BOOKING_FRAMES = ("the {a} one", "the {a}", "the {a} booking")
_BOOKING_MODS = ("", "early", "late", "second", "provisional", "amended",
                 "cheaper", "direct", "refundable")
_BOOKING_HEADS = (
    "Tuesday", "flight", "table for four", "hotel", "return leg", "Friday",
    "morning", "weekend", "outbound", "restaurant", "train", "car hire",
    "evening", "cottage", "campsite", "airport parking", "sleeper",
    "coach", "matinee", "ferry ticket", "guided tour", "day pass",
    "airport transfer", "sleeper berth",
)

_INVOICE_FRAMES = ("the {a} one", "the {a}", "the {a} invoice")
_INVOICE_MODS = ("", "outstanding", "unpaid", "duplicate", "quarterly",
                 "annual", "disputed", "credited", "overdue")
_INVOICE_HEADS = (
    "last month's", "March", "Friday", "January", "first", "second",
    "September", "builder's", "printer's", "supplier's", "electrician's",
    "hosting", "storage", "delivery", "materials", "labour",
    "consultancy", "subscription", "licence", "call-out", "haulage",
    "scaffolding", "skip hire", "survey",
)

_ROUTE_FRAMES = ("{a}", "the way to {a}", "over to {a}")
_ROUTE_MODS = ("", "the new", "the old", "the back way to", "the quick way to",
               "the scenic", "the motorway route to", "the lane to")
_ROUTE_HEADS = (
    "the station", "mum's", "the airport", "the garden centre", "work",
    "the coast", "the tip", "the school", "the office", "Ann's", "the depot",
    "the retail park", "the harbour", "the allotment", "the surgery",
    "the cash and carry", "the cottage", "the hall", "the sorting office",
    "the trailhead", "the reservoir", "the industrial estate", "the pier",
    "the park and ride", "the wholesaler",
)

_FORECAST_FRAMES = ("{a}", "for {a}", "over {a}")
_FORECAST_MODS = ("", "up", "down", "out at", "over toward", "inland from",
                  "along", "just past")
_FORECAST_HEADS = (
    "here", "the coast", "north", "Manchester", "the valley", "Leeds",
    "the hills", "south", "Bristol", "the moors", "the border", "Glasgow",
    "the lakes", "the estuary", "York", "the peaks", "the fens",
    "the downs", "Cardiff", "the islands", "the marshes", "Newcastle",
    "the headland", "the dales", "Sheffield",
)

_ITEM_FRAMES = ("{a}", "some {a}", "more {a}")
_ITEM_MODS = ("", "the good", "the cheap", "another", "a big bag of",
              "a box of", "the own-brand", "extra")
_ITEM_HEADS = (
    "milk", "coffee", "washing up liquid", "bin bags", "bread", "olive oil",
    "eggs", "butter", "tea bags", "kitchen roll", "tinned tomatoes", "rice",
    "flour", "dishwasher tablets", "cheese", "onions", "porridge oats",
    "toothpaste", "cling film", "stock cubes", "yoghurt", "bicarb",
    "washing powder", "loo roll", "tin foil", "pasta", "sugar", "lemons",
)

_PLAYLIST_FRAMES = ("the {a} one", "{a}", "the {a} mix")
_PLAYLIST_MODS = ("", "long", "short", "old", "new", "loud", "quiet", "slow")
_PLAYLIST_HEADS = (
    "driving", "sunday morning", "running", "background", "washing up",
    "late night", "garden", "focus", "kitchen", "long drive", "rainy day",
    "walking", "cooking", "wind down", "morning", "workshop", "commute",
    "decorating", "packing", "gym", "school run", "bath time",
    "dog walk", "studying", "sunday roast",
)

_DEVICE_FRAMES = ("the {a}", "my {a}", "that {a}")
_DEVICE_MODS = ("", "old", "new", "spare", "little", "big", "back-up",
                "upstairs", "kitchen")
_DEVICE_HEADS = (
    "car", "headphones", "mower", "tablet", "drill", "torch", "watch",
    "camera", "speaker", "e-reader", "handset", "vacuum", "trimmer",
    "doorbell", "thermostat", "controller", "radio", "monitor",
    "keyboard", "tracker", "hearing aid", "step counter",
    "games handheld", "power bank",
)

_PARCEL_FRAMES = ("the {a} one", "the {a}", "the {a} parcel")
_PARCEL_MODS = ("", "big", "small", "heavy", "signed for", "missing",
                "redelivered", "damaged", "late")
_PARCEL_HEADS = (
    "returns", "bike shop", "Thursday's", "Monday's", "book", "boot sale",
    "second", "bookshop", "tool", "kitchen", "garden", "clothes",
    "printer", "spares", "gift", "framed", "chemist's", "grocery",
    "furniture", "cable", "battery", "poster tube", "sample",
    "replacement",
)

_SERVICE_FRAMES = ("the {a} one", "the {a}", "the {a} subscription")
_SERVICE_MODS = ("", "monthly", "annual", "shared", "family", "basic",
                 "premium", "trial", "second")
_SERVICE_HEADS = (
    "film", "gym", "magazine", "cloud storage", "music", "news",
    "box delivery", "broadband", "phone", "recipe", "audiobook", "paper",
    "streaming", "language app", "storage", "photo", "coffee",
    "razor", "vitamin", "parking", "meal kit", "flower",
    "car wash", "toolbox",
)

# --- held-out nouns -------------------------------------------------------
# Built from vocabulary that appears nowhere above. `check()` proves it.

_FERRY_FRAMES = ("the {a} crossing", "the {a} sailing", "the {a} one")
_FERRY_MODS = ("", "overnight", "fast", "midday", "foot passenger",
               "vehicle deck", "outer isles", "seasonal")
_FERRY_HEADS = (
    "dawn", "dusk", "slack water", "spring tide", "neap", "shoulder season",
    "linkspan", "roll-on", "hydrofoil", "catamaran", "mainland", "skerry",
    "sound", "firth", "kyle", "narrows", "anchorage", "slipway",
    "gangway", "berth", "fairway", "roads", "haven", "quay",
    "tideway", "moorings",
)

_KILN_FRAMES = ("a {a} firing", "the {a} cycle", "a {a} run")
_KILN_MODS = ("", "bisque", "reduction", "oxidation", "salt", "raku",
              "soda", "wood", "electric")
_KILN_HEADS = (
    "cone six", "cone ten", "lustre", "crystalline", "celadon", "tenmoku",
    "shino", "ash glaze", "slipware", "earthenware", "stoneware",
    "porcelain", "burnish", "sagger", "pyrometric", "soak", "candle",
    "downdraught", "muffle", "damper", "kiln wash", "kiln shelf",
    "witness cone", "ramp hold",
)

_PLOT_FRAMES = ("the {a} bed", "the {a} patch", "our {a}")
_PLOT_MODS = ("", "top", "far", "shaded", "waterlogged", "newly dug",
              "manured", "netted", "windbreak")
_PLOT_HEADS = (
    "brassica", "allium", "legume", "root", "cucurbit", "rhubarb",
    "asparagus", "soft fruit", "cordon", "espalier", "comfrey",
    "green manure", "seedbed", "nursery", "cloche", "hotbed",
    "wormery", "leafmould", "trench", "no-dig", "hugelkultur",
    "chitting tray", "runner bean row", "squash mound",
)

_PROCESS_FRAMES = ("a {a} print", "the {a} develop", "a {a} test")
_PROCESS_MODS = ("", "split grade", "stand", "reversal", "toned", "bleached",
                 "selenium", "sepia", "warm tone")
_PROCESS_HEADS = (
    "cyanotype", "platinum", "palladium", "gum bichromate", "salted paper",
    "albumen", "carbon transfer", "bromoil", "lith", "kallitype",
    "van dyke", "collodion", "ambrotype", "tintype", "photogram",
    "solarised", "dodged", "burned-in", "masked", "ferrotyped",
    "flashed", "pre-soaked", "two-bath",
)


VALUES: dict[str, tuple[str, ...]] = {
    "timer": _durations(),
    "alarm": _times(),
    "reminder": tuple(dict.fromkeys(
        f"{v} {o}" for verbs, objs in _TASK_GROUPS for v in verbs
        for o in objs)),
    "note": tuple(dict.fromkeys(
        f"{s} {p}" for s in _NOTE_SUBJECTS for p in _NOTE_PREDICATES)),
    "track": _spec(_SONG_FRAMES, _SONG_MODS, _SONG_HEADS),
    "meeting": _spec(_MEETING_FRAMES, _MEETING_MODS, _MEETING_HEADS),
    "recipe": _spec(_DISH_FRAMES, _DISH_MODS, _DISH_HEADS),
    "booking": _spec(_BOOKING_FRAMES, _BOOKING_MODS, _BOOKING_HEADS),
    "invoice": _spec(_INVOICE_FRAMES, _INVOICE_MODS, _INVOICE_HEADS),
    "route": _spec(_ROUTE_FRAMES, _ROUTE_MODS, _ROUTE_HEADS),
    "forecast": _spec(_FORECAST_FRAMES, _FORECAST_MODS, _FORECAST_HEADS),
    "shopping_list": _spec(_ITEM_FRAMES, _ITEM_MODS, _ITEM_HEADS),
    "playlist": _spec(_PLAYLIST_FRAMES, _PLAYLIST_MODS, _PLAYLIST_HEADS),
    "battery": _spec(_DEVICE_FRAMES, _DEVICE_MODS, _DEVICE_HEADS),
    "delivery": _spec(_PARCEL_FRAMES, _PARCEL_MODS, _PARCEL_HEADS),
    "subscription": _spec(_SERVICE_FRAMES, _SERVICE_MODS, _SERVICE_HEADS),
    # held out
    "ferry": _spec(_FERRY_FRAMES, _FERRY_MODS, _FERRY_HEADS),
    "kiln": _spec(_KILN_FRAMES, _KILN_MODS, _KILN_HEADS),
    "allotment": _spec(_PLOT_FRAMES, _PLOT_MODS, _PLOT_HEADS),
    "darkroom": _spec(_PROCESS_FRAMES, _PROCESS_MODS, _PROCESS_HEADS),
}

HELD_OUT_NOUNS = ("ferry", "kiln", "allotment", "darkroom")


def choose(rng: random.Random, noun: str, fallback: tuple[str, ...]) -> str:
    """A composed value for `noun`, or `fallback` if it has no composer.

    `fallback` is the domain's own hand-written tuple, so a domain added to
    `toolspace.py` without a composer here degrades to the old behaviour rather
    than raising -- and `check()` is what stops that going unnoticed.
    """
    pool = VALUES.get(noun)
    return rng.choice(pool) if pool else rng.choice(fallback)


def space_size() -> int:
    return sum(len(v) for k, v in VALUES.items() if k not in HELD_OUT_NOUNS)


def check() -> list[str]:
    """Every property this module claims, as a list of failures."""
    bad: list[str] = []
    train = {k: v for k, v in VALUES.items() if k not in HELD_OUT_NOUNS}
    held = {k: v for k, v in VALUES.items() if k in HELD_OUT_NOUNS}

    for k, v in VALUES.items():
        if len(set(v)) != len(v):
            bad.append(f"{k}: {len(v) - len(set(v))} duplicate values")
        if any(not s or s != s.strip() or "  " in s for s in v):
            bad.append(f"{k}: empty, unstripped or double-spaced value")
        if len(v) < PER_DOMAIN_FLOOR:
            bad.append(f"{k}: {len(v)} values, below the per-domain floor "
                       f"of {PER_DOMAIN_FLOOR}")

    total = space_size()
    if total < FLOOR:
        bad.append(f"train space {total} is below the {FLOOR} floor")

    # The disjointness that matters: a held-out domain's value must never be a
    # training value, or the `domain` eval level is reachable from the corpus.
    tset = {s for v in train.values() for s in v}
    for k, v in held.items():
        overlap = sorted(set(v) & tset)
        if overlap:
            bad.append(f"{k}: {len(overlap)} values shared with training, "
                       f"e.g. {overlap[:3]}")
    return bad
