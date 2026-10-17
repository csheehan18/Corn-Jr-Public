"""Start the overlay, or check a theme without one.

`--demo` is the reason this file has more than two flags. Tuning an animation
against a live server means waiting for a real refusal or a real fall-back to
see the frames you just wrote, and some of those states are rare on purpose --
`covered` fires when the runtime had to write his reply for him, which is a
thing you cannot ask for. So the demo drives the same `Machine` with synthetic
events and no socket at all: every state in turn, named as it plays. A theme
can be written end to end with the model unloaded and the GPU free.

`--check` is the same idea with no window: it loads a theme, reports what is
in it, and exits non-zero if it will not load. That is the one thing worth
having in a shell loop while editing.

Themes are swapped from the right-click menu while he is running, and the
one you pick is remembered -- so `--theme` is for trying something once or for
pointing at a file outside `themes/`, not for daily use. A bare name is looked
up in `themes/`, so `--theme pixel` finds the directory with the art in it.

Usage:
    python -m harness.overlay                       # connect and sit there
    python -m harness.overlay --demo                # every state, no server
    python -m harness.overlay --theme pixel         # by name
    python -m harness.overlay --theme ~/mine.json   # or by path
    python -m harness.overlay --themes              # what is on offer
    python -m harness.overlay --check --theme pixel
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..protocol import DEFAULT_HOST, DEFAULT_PORT
from .anim import Theme, ThemeError, available, image_size
from .states import FLASHES, RESTING

THEMES = Path(__file__).resolve().parent / "themes"
DEFAULT_THEME = THEMES / "default.json"
# Beside the repo with the other per-instance files -- `notes.jsonl`,
# `contacts.json` -- and gitignored with them. Where the window was dragged to
# is this machine's fact and nobody else's.
DEFAULT_STATE = Path(__file__).resolve().parents[2] / "overlay.json"

# What the demo says while a state is on screen. Real notes come from real
# events; these exist so the state being drawn is never in doubt.
_DEMO_NOTE = {
    "tool": "web_search",
    "queued": "behind another turn",
    "refused": "arguments did not match the schema",
    "covered": "covered: names Graham",
    "error": "the request, not the model",
}
_DEMO_SAY = ("This is the demo. Every state in the theme gets a turn on "
             "screen so you can see the frames you just wrote, with no "
             "server running and nothing loaded on the card.")


def demo(app, hold_ms: int = 2200) -> None:
    """Walk the states, resting ones as rests and flashes as flashes."""
    order = list(RESTING) + list(FLASHES)

    def step(i: int = 0) -> None:
        state = order[i % len(order)]
        app.machine.note = _DEMO_NOTE.get(state, state)
        app.machine.text = _DEMO_SAY if state in ("speaking", "covered") else ""
        app.machine.tool = "web_search" if state == "tool" else ""
        if state in FLASHES:
            app.player.rest("idle", app._now())
            app.player.flash(state, app._now(), app.machine.tool)
        else:
            app.player.rest(state, app._now(), app.machine.tool)
        app.root.after(hold_ms, step, i + 1)

    app.root.after(200, step)


def pick_theme(args) -> Path:
    """Which theme to open with, most explicit first.

    A `--theme` typed on the command line beats one remembered from the menu,
    which beats the shipped default. That order is the only one that does not
    surprise: a flag you just typed doing nothing because of a choice you made
    a week ago is the kind of thing that gets debugged for ten minutes.

    A bare name is looked up in `themes/` before being treated as a path, so
    `--theme pixel` works and does not need to know whether that theme is a
    file or a directory with art in it.
    """
    if args.theme is not None:
        named = dict(available()).get(str(args.theme))
        return named if named is not None else args.theme
    if not args.no_state and args.state.exists():
        try:
            saved = json.loads(args.state.read_text(encoding="utf-8"))
            remembered = Path(saved["theme"])
            if remembered.exists():
                return remembered
        except (OSError, ValueError, KeyError, TypeError):
            pass
    return DEFAULT_THEME


def describe(theme: Theme) -> None:
    """What loaded, in the terms an author is about to change.

    The drawn size is spelled out for image frames because it is the number
    nobody can work out in their head: a 16x20 sprite at `zoom: 5` is 80x100
    on screen, and whether that fits the window is the first thing to get
    wrong.
    """
    print(f"{theme.path}")
    print(f"  {theme.name}: {len(theme.animations)} animations, "
          f"{int(theme.window['size'][0])}x{int(theme.window['size'][1])}")
    for name in sorted(theme.animations):
        a = theme.animations[name]
        kinds = "".join("i" if f.image else "t" for f in a.frames)
        print(f"    {name:<20} {len(a.frames):>2} frames  "
              f"{a.duration():>5}ms  [{kinds}]")
        if a.sheet is not None:
            s = a.sheet
            print(f"      sheet {Path(s.path).name}  {s.cols}x{s.rows} cells "
                  f"of {s.cw}x{s.ch}  ({s.count} available)")
        drawn = sorted({_drawn(f) for f in a.frames if f.image})
        if drawn:
            print(f"      drawn at {', '.join(drawn)}")
    unmapped = [s for s in RESTING + FLASHES
                if s not in theme.states and s not in theme.animations]
    if unmapped:
        print(f"  falling back to idle: {', '.join(unmapped)}")


def _drawn(frame) -> str:
    if frame.crop:
        w, h = frame.crop[2] - frame.crop[0], frame.crop[3] - frame.crop[1]
    else:
        try:
            w, h = image_size(Path(frame.image))
        except ThemeError:
            return "?"
    w, h = w * frame.zoom // frame.subsample, h * frame.zoom // frame.subsample
    return f"{w}x{h}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--theme", type=Path, default=None,
                    help=f"a theme file, or the name of one in {THEMES.name}/ "
                         f"(default: the last one picked from the menu, else "
                         f"{DEFAULT_THEME.name}). See {THEMES / 'README.md'}")
    ap.add_argument("--themes", action="store_true",
                    help="list the themes on offer, then exit")
    ap.add_argument("--state", type=Path, default=DEFAULT_STATE,
                    help="where the window position and the chosen "
                         "theme are remembered")
    ap.add_argument("--no-state", action="store_true",
                    help="do not remember the position or the theme, "
                         "and do not read a remembered one")
    ap.add_argument("--demo", action="store_true",
                    help="cycle every state with no server attached")
    ap.add_argument("--check", action="store_true",
                    help="load the theme, describe it, exit. No window")
    args = ap.parse_args()

    if args.themes:
        for label, path in available():
            print(f"  {label:<16} {path}")
        return 0

    try:
        theme = Theme.load(pick_theme(args))
    except ThemeError as exc:
        print(f"!! {exc}", file=sys.stderr)
        return 1

    if args.check:
        describe(theme)
        return 0

    # Imported here rather than at the top so `--check` works on a machine with
    # no display and no Tk -- the format is checkable anywhere the repo is.
    from .window import Overlay

    app = Overlay(theme, host=args.host, port=args.port,
                  state_path=None if args.no_state else args.state,
                  demo=args.demo)
    if args.demo:
        demo(app)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
