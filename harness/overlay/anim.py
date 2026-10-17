"""A theme file in, the frame to draw at this instant out. Still no display.

**The animations are data, and the data is the point.** Everything about how
he looks -- the frames, their timing, the colours, which state plays what --
is one JSON file, and nothing in this package needs editing to change any of
it. That is the difference between a mascot somebody can tune in an evening
and one that needs a Python diff per blink, and the whole module is arranged
around keeping the second kind from happening: this file parses and times,
`window.py` draws, and neither one knows a single frame.

**Two frame kinds, and the text one is the default on purpose.** A frame is
either text -- a line, or a list of lines for an ASCII face -- or an image
beside the theme. Text costs nothing, ships with no assets, and survives being
copied to another machine, so the theme in `themes/default.json` is written
entirely in it and a person with sprites can replace frames one at a time
rather than all at once.

**Sprite sheets, because that is how pixel art actually arrives.** An
animation may declare `sheet` and a `cell` size, after which a frame is just
its cell number -- `"frames": [0, 1, 2, 3]` -- counted left to right and then
top to bottom, which is the order every editor exports a strip in. The cell is
resolved to a pixel box here, at load, so `window.py` is handed coordinates and
never has to measure anything; the size comes out of the file's header via
`image_size`, twenty lines rather than a dependency. `zoom` and `subsample` sit
on the animation for the same reason: pixel art is drawn small and shown large,
and making an author repeat `"zoom": 5` on all twelve frames of a walk cycle is
twelve chances to typo one of them. `themes/pixel/` is the worked example.

**Loading is strict and says where.** A theme is edited by hand, at speed,
usually while the thing is running, so the failure that matters is a typo. An
unknown key, a missing animation, a state name that is not a state, an image
path that does not exist: each is refused at load with the JSON path that
caused it, because the alternative -- accepting it and drawing nothing -- makes
a typo look like an animation bug. `window.py` catches `ThemeError` on reload,
keeps the theme it already had, and shows the message; a bad save never costs
the running face.

**Timing is passed in, never read.** `Player.frame` takes `now` in
milliseconds rather than calling a clock, which is what lets
`scripts/check_overlay.py` step a whole animation through in a loop with no
display, no sleeping and no flakiness. The one place a real clock is read is
the Tk tick in `window.py`.

The format, all keys optional except `animations`:

    {
      "name": "default",
      "window": {"size": [320, 220], "transparent": "#010203",
                 "alpha": 1.0, "topmost": true},
      "face":   {"font": ["Consolas", 22], "color": "#e6e6e6",
                 "x": 0.5, "y": 0.72, "shadow": "#000000"},
      "bubble": {"font": ["Segoe UI", 10], "color": "#f0f0f0",
                 "background": "#1c1c22", "border": "#3a3a44",
                 "width": 300, "lines": 6, "pad": 8},
      "note":   {"font": ["Consolas", 8], "color": "#8a8a96", "show": true},
      "animations": {
        "idle": {"ms": 600, "frames": ["o_o", "-_-"]},
        "talk": {"sheet": "strip.png", "cell": [16, 20], "zoom": 5,
                 "ms": 150, "frames": [0, 2]}
      },
      "states": {"speaking": "talk", "thinking": "think"}
    }

An animation is `{"ms": int}` or `{"fps": number}` plus `frames`, and may add
`color`, `zoom`, `subsample`, and `sheet` with `cell`. A frame is a string, a
list of strings (one per line), a sheet cell number, or an object with any of
`text`, `image`, `cell`, `index`, `ms`, `dx`, `dy`, `color`, `zoom`,
`subsample`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, replace
from pathlib import Path

from .states import STATES


class ThemeError(ValueError):
    """A theme that cannot be drawn. The message always names the JSON path."""


# Defaults deep enough that a one-animation theme is a valid theme. A person
# trying the format for the first time should not have to write a window
# geometry to find out whether their frames look right.
DEFAULT_WINDOW = {"size": [320, 220], "transparent": "#010203", "alpha": 1.0,
                  "topmost": True}
DEFAULT_FACE = {"font": ["Consolas", 22], "color": "#e6e6e6", "x": 0.5,
                "y": 0.74, "spacing": 2, "shadow": "#000000"}
DEFAULT_BUBBLE = {"font": ["Segoe UI", 10], "color": "#f0f0f0",
                  "background": "#1c1c22", "border": "#3a3a44",
                  "width": 300, "lines": 7, "pad": 8, "radius": 10}
DEFAULT_NOTE = {"font": ["Consolas", 8], "color": "#8a8a96", "show": True}

_SECTIONS = {"window": DEFAULT_WINDOW, "face": DEFAULT_FACE,
             "bubble": DEFAULT_BUBBLE, "note": DEFAULT_NOTE}

_FRAME_KEYS = {"text", "image", "ms", "dx", "dy", "color", "zoom", "subsample",
               "index", "cell"}
_ANIM_KEYS = {"frames", "ms", "fps", "color", "zoom", "subsample", "sheet",
              "cell"}

# A theme may name an animation `tool:web_search` and it will be preferred over
# `tool` while that call is in flight. Documented here rather than hidden in a
# lookup because it is the one naming convention the format has.
TOOL_PREFIX = "tool:"

# Where the shipped themes live, and where a new one is found without being
# named on a command line.
THEMES_DIR = Path(__file__).resolve().parent / "themes"


def available(extra=None) -> list:
    """The themes on offer, as `(label, path)`, for a menu to list.

    **Two shapes, because art wants a directory and text does not.** A theme
    is either `themes/<name>.json` or `themes/<name>/theme.json`; the second
    is what a theme with sprites beside it looks like, and the label is the
    directory in that case. Anything else in there is ignored rather than
    guessed at.

    `extra` is a path loaded from somewhere else -- a `--theme` pointing
    outside this directory -- so the menu always contains the theme actually
    running. Without it, switching away from your own theme would be a
    one-way door.
    """
    found = {}
    if THEMES_DIR.is_dir():
        for path in sorted(THEMES_DIR.glob("*.json")):
            found[path.stem] = path
        for path in sorted(THEMES_DIR.glob("*/theme.json")):
            found[path.parent.name] = path
    if extra is not None:
        extra = Path(extra).resolve()
        if extra not in {p.resolve() for p in found.values()}:
            label = (extra.parent.name if extra.name == "theme.json"
                     else extra.stem)
            found[label] = extra
    return sorted(found.items())


@dataclass(frozen=True)
class Frame:
    """One drawn instant. `image` is absolute by the time it gets here, and
    `crop` is already resolved to a pixel box -- `window.py` gets coordinates,
    never a cell number it would have to work out against a sheet it would
    have to measure."""

    text: str = ""
    image: str = ""
    ms: int = 0          # 0 means "the animation's frame time"
    dx: int = 0
    dy: int = 0
    color: str = ""      # empty means "the animation's, then the face's"
    zoom: int = 1
    subsample: int = 1
    index: int = 0       # which frame of a multi-frame GIF
    crop: tuple = ()     # (x1, y1, x2, y2) into `image`, for a sprite sheet


@dataclass(frozen=True)
class Animation:
    name: str
    frames: tuple[Frame, ...]
    ms: int = 120
    color: str = ""
    # Kept only so `--check` can describe the sheet a theme is built on. The
    # frames already carry their own resolved crops and never consult it.
    sheet: "Sheet | None" = None

    def frame_ms(self, frame: Frame) -> int:
        return frame.ms if frame.ms > 0 else self.ms

    def duration(self) -> int:
        """One pass, in milliseconds. Never zero -- a zero-length animation
        would divide by zero in `at` and there is no sensible frame to hold."""
        return sum(max(1, self.frame_ms(f)) for f in self.frames)

    def at(self, elapsed: float, loop: bool = True) -> Frame | None:
        """The frame `elapsed` ms into a pass, or `None` past the end of a
        non-looping one -- which is how `Player` learns a flash is spent."""
        total = self.duration()
        if elapsed < 0:
            elapsed = 0
        if elapsed >= total:
            if not loop:
                return None
            elapsed %= total
        acc = 0.0
        for f in self.frames:
            acc += max(1, self.frame_ms(f))
            if elapsed < acc:
                return f if f.color or not self.color else replace(f, color=self.color)
        return self.frames[-1]


def image_size(path: Path) -> tuple[int, int]:
    """(width, height) from the file's header, decoding nothing.

    **Twenty lines instead of Pillow.** The only reason a theme needs this is
    to work out how many cells are in a sprite sheet, and a dependency bought
    for arithmetic that fits in a header is exactly what `harness/protocol.py`
    says not to buy -- every one of them is a thing a person hosting their own
    Corn-Jr has to install before he says a word. PNG and GIF are the two
    formats Tk reads, so they are the two formats this reads.
    """
    head = path.read_bytes()[:26]
    if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
        return (int.from_bytes(head[16:20], "big"),
                int.from_bytes(head[20:24], "big"))
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return (int.from_bytes(head[6:8], "little"),
                int.from_bytes(head[8:10], "little"))
    raise ThemeError(f"{path}: not a PNG or a GIF -- those are the two "
                     f"formats Tk reads without a dependency")


def _resolve(image: str, where: str, base: Path) -> str:
    """A theme-relative image path, checked now rather than at draw time.

    Relative to the theme file, so a theme plus its art is one movable
    directory. Checked here because a mistyped filename that only shows up as
    a blank face three states later is the worst place to find it.
    """
    path = (base / image) if not Path(image).is_absolute() else Path(image)
    if not path.exists():
        raise ThemeError(f"{where}: no such image {path}")
    return str(path)


def _frame(raw, where: str, base: Path, sheet: "Sheet | None" = None,
           zoom: int = 1, subsample: int = 1) -> Frame:
    """One frame. `sheet`, `zoom` and `subsample` are the animation's, and a
    frame that sets its own wins -- which is what keeps a sprite sheet's
    frame list down to the cell numbers."""
    if isinstance(raw, str):
        return Frame(text=raw)
    if isinstance(raw, int) and not isinstance(raw, bool):
        # A bare number is a cell of the animation's sheet. The whole reason
        # the shorthand exists: `"frames": [0, 1, 2, 3]` is what a strip
        # exported out of a pixel editor actually wants to say.
        if sheet is None:
            raise ThemeError(f"{where}: a number is a cell of a sprite sheet, "
                             f"and this animation has no `sheet`")
        return Frame(image=sheet.path, crop=sheet.cell(raw, where),
                     zoom=zoom, subsample=subsample)
    if isinstance(raw, list):
        if not all(isinstance(line, str) for line in raw):
            raise ThemeError(f"{where}: a list frame must be all strings")
        return Frame(text="\n".join(raw))
    if not isinstance(raw, dict):
        raise ThemeError(f"{where}: a frame is a string, a list of strings, a "
                         f"sheet cell number, or an object -- got "
                         f"{type(raw).__name__}")
    unknown = set(raw) - _FRAME_KEYS
    if unknown:
        raise ThemeError(f"{where}: unknown key(s) {sorted(unknown)}; "
                         f"a frame takes {sorted(_FRAME_KEYS)}")
    text = raw.get("text", "")
    if isinstance(text, list):
        text = "\n".join(str(line) for line in text)
    for key in ("ms", "dx", "dy", "zoom", "subsample", "index", "cell"):
        if key in raw and (not isinstance(raw[key], int)
                           or isinstance(raw[key], bool)):
            raise ThemeError(f"{where}.{key}: expected a whole number")
    zoom = int(raw.get("zoom", zoom))
    subsample = int(raw.get("subsample", subsample))
    if zoom < 1 or subsample < 1:
        raise ThemeError(f"{where}: `zoom` and `subsample` are 1 or more")

    crop: tuple = ()
    image = str(raw.get("image", ""))
    if "cell" in raw:
        if image:
            raise ThemeError(f"{where}: set `cell` or `image`, not both -- a "
                             f"cell comes from the animation's `sheet`")
        if sheet is None:
            raise ThemeError(f"{where}.cell: this animation has no `sheet`")
        image, crop = sheet.path, sheet.cell(int(raw["cell"]), where)
    elif image:
        image = _resolve(image, where, base)
    if not text and not image:
        raise ThemeError(f"{where}: a frame needs `text`, `image` or `cell`")
    if raw.get("index", 0) and not image.lower().endswith(".gif"):
        raise ThemeError(f"{where}.index: only a GIF has numbered frames")
    return Frame(text=str(text), image=image, ms=int(raw.get("ms", 0)),
                 dx=int(raw.get("dx", 0)), dy=int(raw.get("dy", 0)),
                 color=str(raw.get("color", "")), zoom=zoom,
                 subsample=subsample, index=int(raw.get("index", 0)),
                 crop=crop)


@dataclass(frozen=True)
class Sheet:
    """A sprite sheet, measured once, so a cell number becomes a pixel box.

    Cells run left to right and then top to bottom, which is the order every
    pixel editor exports a strip or a grid in. A sheet that is not a whole
    number of cells across is refused rather than rounded: the frames past the
    ragged edge would come out half-sprite, and a theme that silently drew
    half a sprite is worse than one that would not load.
    """

    path: str
    cw: int
    ch: int
    cols: int
    rows: int

    @property
    def count(self) -> int:
        return self.cols * self.rows

    def cell(self, n: int, where: str) -> tuple:
        if n < 0 or n >= self.count:
            raise ThemeError(f"{where}: cell {n} is not in the sheet -- "
                             f"{Path(self.path).name} holds {self.count} "
                             f"({self.cols} x {self.rows})")
        x, y = (n % self.cols) * self.cw, (n // self.cols) * self.ch
        return (x, y, x + self.cw, y + self.ch)

    @classmethod
    def load(cls, image: str, cell, where: str, base: Path) -> "Sheet":
        path = _resolve(image, f"{where}.sheet", base)
        if (not isinstance(cell, list) or len(cell) != 2
                or not all(isinstance(v, int) and v > 0 for v in cell)):
            raise ThemeError(f"{where}.cell: expected [width, height] in "
                             f"pixels, both greater than zero")
        cw, ch = cell
        sw, sh = image_size(Path(path))
        if sw % cw or sh % ch:
            raise ThemeError(f"{where}: {Path(path).name} is {sw}x{sh}, which "
                             f"is not a whole number of {cw}x{ch} cells")
        return cls(path=path, cw=cw, ch=ch, cols=sw // cw, rows=sh // ch)


def _animation(name: str, raw, base: Path) -> Animation:
    where = f"animations.{name}"
    if isinstance(raw, list):        # bare list of frames, the shortest form
        raw = {"frames": raw}
    if not isinstance(raw, dict):
        raise ThemeError(f"{where}: expected an object or a list of frames")
    unknown = set(raw) - _ANIM_KEYS
    if unknown:
        raise ThemeError(f"{where}: unknown key(s) {sorted(unknown)}; "
                         f"an animation takes {sorted(_ANIM_KEYS)}")
    if "ms" in raw and "fps" in raw:
        raise ThemeError(f"{where}: set `ms` or `fps`, not both")
    frames = raw.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ThemeError(f"{where}.frames: expected a non-empty list")

    if ("sheet" in raw) != ("cell" in raw):
        raise ThemeError(f"{where}: `sheet` and `cell` go together -- a sheet "
                         f"without a cell size cannot be cut up")
    sheet = (Sheet.load(str(raw["sheet"]), raw["cell"], where, base)
             if "sheet" in raw else None)
    # **Set the scale once, on the animation.** Pixel art is drawn small and
    # shown large, so every frame of it carries the same `zoom`; making an
    # author repeat it per frame is how a twelve-frame walk cycle turns into
    # twelve chances to typo one of them.
    for key in ("zoom", "subsample"):
        if key in raw and (not isinstance(raw[key], int)
                           or isinstance(raw[key], bool) or raw[key] < 1):
            raise ThemeError(f"{where}.{key}: expected a whole number, "
                             f"1 or more")
    zoom, subsample = int(raw.get("zoom", 1)), int(raw.get("subsample", 1))
    ms = 120
    if "fps" in raw:
        try:
            fps = float(raw["fps"])
        except (TypeError, ValueError):
            raise ThemeError(f"{where}.fps: expected a number") from None
        if fps <= 0:
            raise ThemeError(f"{where}.fps: must be greater than zero")
        ms = max(1, round(1000.0 / fps))
    elif "ms" in raw:
        if not isinstance(raw["ms"], int) or raw["ms"] < 1:
            raise ThemeError(f"{where}.ms: expected a whole number of "
                             f"milliseconds, 1 or more")
        ms = raw["ms"]
    return Animation(
        name=name,
        frames=tuple(_frame(f, f"{where}.frames[{i}]", base, sheet,
                            zoom, subsample)
                     for i, f in enumerate(frames)),
        ms=ms,
        color=str(raw.get("color", "")),
        sheet=sheet,
    )


@dataclass
class Theme:
    path: Path
    name: str
    window: dict
    face: dict
    bubble: dict
    note: dict
    animations: dict
    states: dict
    mtime: float = 0.0
    # Every image the theme references, to the mtime it had at load. Watched
    # alongside the theme file itself -- see `changed`.
    images: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path) -> "Theme":
        path = Path(path)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise ThemeError(f"no such theme: {path}") from None
        except json.JSONDecodeError as exc:
            # Line and column included: this is the error a person gets from a
            # trailing comma, and "invalid JSON" alone would not help them.
            raise ThemeError(f"{path}: not valid JSON -- {exc}") from None
        if not isinstance(raw, dict):
            raise ThemeError(f"{path}: a theme is a JSON object")

        base = path.parent
        sections = {}
        for key, default in _SECTIONS.items():
            got = raw.get(key, {})
            if not isinstance(got, dict):
                raise ThemeError(f"{path}: `{key}` is an object")
            unknown = set(got) - set(default)
            if unknown:
                raise ThemeError(f"{path}: {key}: unknown key(s) "
                                 f"{sorted(unknown)}; takes {sorted(default)}")
            sections[key] = {**default, **got}

        anims_raw = raw.get("animations")
        if not isinstance(anims_raw, dict) or not anims_raw:
            raise ThemeError(f"{path}: `animations` is required and is a "
                             f"non-empty object")
        animations = {name: _animation(name, spec, base)
                      for name, spec in anims_raw.items()}
        # **`idle` is the floor every lookup falls to**, so a theme without one
        # has a hole that only appears in whichever state was not mapped.
        if "idle" not in animations:
            raise ThemeError(f"{path}: every theme needs an `idle` animation; "
                             f"it is what unmapped states fall back to")

        states = raw.get("states", {})
        if not isinstance(states, dict):
            raise ThemeError(f"{path}: `states` is an object")
        for state, anim in states.items():
            if state not in STATES:
                raise ThemeError(f"{path}: states.{state}: not a state; "
                                 f"the states are {sorted(STATES)}")
            if anim not in animations:
                raise ThemeError(f"{path}: states.{state}: no animation "
                                 f"named {anim!r}")

        images = {}
        for anim in animations.values():
            for f in anim.frames:
                if f.image and f.image not in images:
                    try:
                        images[f.image] = Path(f.image).stat().st_mtime
                    except OSError:
                        pass

        return cls(path=path, name=str(raw.get("name", path.stem)),
                   window=sections["window"], face=sections["face"],
                   bubble=sections["bubble"], note=sections["note"],
                   animations=animations, states=states,
                   mtime=path.stat().st_mtime, images=images)

    def changed(self) -> bool:
        """Has anything the theme is made of been saved since it was read?

        **The art counts, not only the JSON.** Someone drawing a sprite saves
        the sheet a hundred times and the theme file once, and a reload that
        watched only the JSON would make the useful half of that loop the half
        that does nothing. A stat per image per second is nothing next to
        being able to redraw an eye and see it blink.
        """
        try:
            if self.path.stat().st_mtime != self.mtime:
                return True
        except OSError:
            return False
        for image, was in self.images.items():
            try:
                if Path(image).stat().st_mtime != was:
                    return True
            except OSError:
                # Gone, or being rewritten as we look. Neither is a reload
                # worth forcing -- the next tick asks again, and a load that
                # genuinely fails is caught and reported there.
                continue
        return False

    def animation(self, state: str, tool: str = "") -> Animation:
        """The animation for a state, most specific first.

        A per-tool animation wins over the `tool` state, so a theme that wants
        a different face for `web_search` names one and leaves every other tool
        alone. Then the theme's own `states` map, then an animation with the
        state's name, then `idle`.
        """
        if tool:
            named = self.animations.get(TOOL_PREFIX + tool)
            if named is not None:
                return named
        name = self.states.get(state, state)
        return (self.animations.get(name)
                or self.animations.get(state)
                or self.animations["idle"])


@dataclass
class Player:
    """Which animation is playing, and how far into it.

    Resting animations loop. A flash plays exactly one pass and then the
    resting one resumes from where it would have been -- which is why `rest`
    does not restart an animation that is already the one playing. Without
    that, every `obs` in a multi-call turn would snap a running tool animation
    back to its first frame and the loop would never be seen.
    """

    theme: Theme
    state: str = "offline"
    tool: str = ""
    _anim: Animation | None = None
    _since: float = 0.0
    _flash: Animation | None = None
    _flash_since: float = 0.0
    # Kept so a theme reload can re-resolve the same state against the new file
    # without waiting for the next event to arrive.
    _resting_key: tuple = field(default=("", ""))

    def rest(self, state: str, now: float, tool: str = "") -> None:
        self.state, self.tool = state, tool
        anim = self.theme.animation(state, tool)
        if self._anim is None or anim.name != self._anim.name:
            self._anim, self._since = anim, now
        self._resting_key = (state, tool)

    def flash(self, state: str, now: float, tool: str = "") -> None:
        self._flash = self.theme.animation(state, tool)
        self._flash_since = now

    def retheme(self, theme: Theme, now: float) -> None:
        """Swap the theme under a running player. The flash is dropped rather
        than carried across: it belongs to an event that is already over, and
        restarting one on a reload would look like the event happened twice."""
        self.theme = theme
        self._anim, self._flash = None, None
        self.rest(self._resting_key[0] or self.state, now,
                  self._resting_key[1] or self.tool)

    def frame(self, now: float) -> Frame:
        if self._flash is not None:
            got = self._flash.at(now - self._flash_since, loop=False)
            if got is not None:
                return got
            self._flash = None
        if self._anim is None:
            self.rest(self.state, now, self.tool)
        return self._anim.at(now - self._since) or Frame()

    @property
    def playing(self) -> str:
        """The animation's name, for `--demo` and for the guard."""
        if self._flash is not None:
            return self._flash.name
        return self._anim.name if self._anim is not None else ""
