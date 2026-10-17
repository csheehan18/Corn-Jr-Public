"""`server.json` as a form: which knob goes where, what it may hold, and the save.

The form is generated from `ServerConfig`'s own fields and the help lines are
`serverconfig.HELP` verbatim, so a knob added to the dataclass appears in the
studio without anyone remembering to come and add it -- and can never carry a
second description. Four fields render elsewhere: `tools`, `tools_dir` and
`decline` on the Tools page, where the decision they express lives; `book` on
People, for the same reason.

**Two tiers, because the dataclass serves two people.** The owner tunes
reader thresholds and decode paths; a friend hosting a copy wants the
checkpoint, the packs folder, and whether turns are recorded. So the fields a
finding was measured on -- and anything the dataclass grows that no section
claims -- sit in one collapsed Advanced group with a sentence saying the
defaults are the released state. Restore defaults resets that tier and leaves
what makes the instance somebody's (`KEEP`).

**A save is all or nothing.** `apply` coerces the posted values onto a *copy*
of the config and validates the copy; only a copy that validates replaces the
live one and reaches the file. The NiceGUI form bound its widgets to the live
object, so a half-typed port was the running studio's port until somebody
pressed Save. `ServerConfig.save` keeps its rule: only keys that differ from
the defaults are written.

**Every field has a plain name, and the key beside it.** `LABELS` is what a
person reads ("Remember the conversation"); the page shows the `server.json`
key in small type next to it, because the owner and the docs speak in keys.
`scripts/check_studio.py` holds `LABELS` to exactly the fields the form
shows, so a new knob cannot arrive unnamed and a removed one cannot leave a
label behind.

**`CHOICES` restates the string enumerations `ServerConfig.validate` holds**,
so a field is a dropdown rather than a text box that accepts typos.
`scripts/check_studio.py` asserts every listed choice validates and a value
outside the list does not, so the two cannot drift apart silently. `SUGGEST`
is the other kind: common values offered beside a free text box, for a field
`validate` does not enumerate -- `device` takes `cuda:1` as readily as
`cuda`, and a dropdown would have taken that away.

No framework: the page asks for `schema` and posts to `apply`.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import fields
from pathlib import Path

from ..serverconfig import DTYPE_NAMES, HELP, ConfigError, ServerConfig
from . import firstrun

# Field -> section, in render order. These are the knobs a person hosting
# their own copy has a reason to touch.
SECTIONS = (
    ("What this instance is",
     ("ckpt", "packs", "doc", "notes", "persona_state", "birthday_lead",
      "search", "extract", "multi")),
    ("The machine",
     ("host", "port", "device", "dtype")),
    ("Sampling",
     ("temperature", "speech_temperature")),
    ("The sitting's record and the gate",
     ("confirm", "log", "logging")),
)

ADVANCED_TITLE = "Advanced -- measurement controls and thresholds"
ADVANCED_NOTE = ("Every knob here withholds or changes something a finding "
                 "measured. The defaults are the released state, and the "
                 "model card's numbers were read on them. Change one to see "
                 "its effect, not to fix a problem.")
# Named so they render in a stable order; everything the dataclass grows that
# no section claims follows them.
ADVANCED = ("grammar", "fold", "restrict", "seed_turn", "seed_trim",
            "seed_repass", "history_fold", "budget", "round_reserve",
            "extract_gate", "gate_threshold", "reader", "reader_threshold",
            "reader_extent_d", "reader_adapter", "reader_whole_threshold",
            "family_check", "identity_check", "name_header",
            "buckets", "compile_step", "prefix_reuse")

ELSEWHERE = ("tools", "tools_dir", "decline")  # other pages' fields

# What Restore defaults leaves alone: the parts that make this instance one
# person's rather than the released state.
KEEP = ("ckpt", "packs", "tools", "tools_dir", "host", "port")

LABELS = {
    # What this instance is
    "ckpt": "Checkpoint",
    "packs": "Your data (packs folder)",
    "doc": "Document to answer from",
    "notes": "Notes file",
    "persona_state": "Occasion marker file",
    "birthday_lead": "Days ahead to mention a birthday",
    "search": "Answer from the web",
    "extract": "Read whole search results",
    "multi": "Remember the conversation",
    # The machine
    "host": "Address",
    "port": "Port",
    "device": "Device",
    "dtype": "Precision",
    # Sampling
    "temperature": "Tool-call randomness",
    "speech_temperature": "Chat randomness",
    # The sitting's record and the gate
    "confirm": "Ask before acting",
    "log": "Turn log file",
    "logging": "Record turns",
    # Advanced
    "grammar": "Call grammar",
    "fold": "Normalise what you type",
    "restrict": "Social replies from pools only",
    "seed_turn": "Opening seed turn",
    "seed_trim": "Seed turn trimming",
    "seed_repass": "Seed re-pass for searches",
    "history_fold": "Fold old turns",
    "budget": "Reply budget (tokens)",
    "round_reserve": "Second-round reserve (tokens)",
    "extract_gate": "Score passages before reading",
    "gate_threshold": "Speak threshold (gate)",
    "reader": "Passage reader",
    "reader_threshold": "Speak threshold (reader)",
    "reader_extent_d": "Longer-span tolerance",
    "reader_adapter": "Whole-passage adapter",
    "reader_whole_threshold": "Speak threshold (whole passage)",
    "family_check": "Social family check",
    "identity_check": "Identity questions",
    "name_header": "Name header",
    "buckets": "Windowed decode graphs",
    "compile_step": "Compile the decode step",
    "prefix_reuse": "Reuse the shared prefix",
}

CHOICES = {
    "dtype": DTYPE_NAMES,
    "reader": ("generate", "head", "head_whole"),
    "identity_check": ("on", "log"),
    "family_check": ("on", "log", "off"),
    "seed_trim": ("off", "obs", "both"),
    "seed_repass": ("off", "always", "contaminated"),
}

SUGGEST = {"device": ("cuda", "cpu")}


def kind_of(value) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, list):
        return "list"
    return "str"


def advanced_names(cfg: ServerConfig) -> list[str]:
    known = [f.name for f in fields(type(cfg))]
    placed = {n for _, names in SECTIONS for n in names} | set(ELSEWHERE) \
        | set(ADVANCED)
    stray = [n for n in known if n not in placed]
    return [n for n in ADVANCED if n in known] + stray


def field_schema(cfg: ServerConfig, name: str, repo: Path) -> dict:
    value = getattr(cfg, name)
    default = getattr(ServerConfig(), name)
    out = {"name": name, "label": LABELS.get(name, name.replace("_", " ")),
           "help": HELP.get(name, ""), "kind": kind_of(default),
           "value": value, "default": default, "keep": name in KEEP}
    if name == "ckpt":
        opts = firstrun.checkpoints(repo)
        if value not in opts:
            opts.append(value)
        out["kind"], out["choices"], out["free"] = "choice", opts, True
    elif name in CHOICES:
        out["kind"], out["choices"] = "choice", list(CHOICES[name])
    elif name in SUGGEST:
        out["kind"], out["choices"] = "choice", list(SUGGEST[name])
        out["free"] = True
    return out


def schema(cfg: ServerConfig, repo: Path) -> dict:
    return {
        "sections": [{"title": title,
                      "fields": [field_schema(cfg, n, repo) for n in names]}
                     for title, names in SECTIONS],
        "advanced": {"title": ADVANCED_TITLE, "note": ADVANCED_NOTE,
                     "fields": [field_schema(cfg, n, repo)
                                for n in advanced_names(cfg)]},
    }


def coerce(name: str, raw, default):
    kind = kind_of(default)
    if kind == "bool":
        if not isinstance(raw, bool):
            raise ConfigError(f"{name} must be true or false")
        return raw
    if kind == "int":
        try:
            f = float(raw)
        except (TypeError, ValueError):
            raise ConfigError(f"{name} {raw!r} is not a whole number") from None
        if f != int(f):
            raise ConfigError(f"{name} {raw!r} is not a whole number")
        return int(f)
    if kind == "float":
        try:
            return float(raw)
        except (TypeError, ValueError):
            raise ConfigError(f"{name} {raw!r} is not a number") from None
    if kind == "list":
        if not isinstance(raw, list) or not all(isinstance(x, str)
                                                for x in raw):
            raise ConfigError(f"{name} must be a list of strings")
        return list(raw)
    return "" if raw is None else str(raw)


def apply(cfg: ServerConfig, values: dict) -> ServerConfig:
    """The posted values on a copy, validated. Raises `ConfigError` naming
    the first problem; the live config is untouched until this returns."""
    known = {f.name for f in fields(type(cfg))}
    unknown = sorted(set(values) - known)
    if unknown:
        raise ConfigError(f"unknown setting(s): {', '.join(unknown)}")
    base = ServerConfig()
    new = deepcopy(cfg)
    for name, raw in values.items():
        setattr(new, name, coerce(name, raw, getattr(base, name)))
    new.validate()
    return new


def save(cfg: ServerConfig, values: dict, path: Path) -> ServerConfig:
    new = apply(cfg, values)
    new.save(path)
    return new


def restored(cfg: ServerConfig) -> dict:
    """What Restore defaults puts in the form: the released value of every
    field outside `KEEP`. The form shows them; Save writes them."""
    released = ServerConfig()
    return {f.name: deepcopy(getattr(released, f.name))
            for f in fields(type(cfg)) if f.name not in KEEP}
