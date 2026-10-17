"""The only file that imports tkinter. Draws what the other three decided.

**Tk because the dependency budget is not a preference.** `harness/
protocol.py` says the package ships beside the weights and that every
dependency is one a person hosting their own Corn-Jr has to install correctly
before he says a word; the reference client is eighty lines of `socket` with no
framework for the same reason. An overlay built on Qt or a browser shell would
have made the face the heaviest thing in the repository. Tk is in the standard
library, does borderless always-on-top windows, and -- on Windows -- does the
one thing this needs that a normal toolkit will not: `-transparentcolor` makes
every pixel of one colour both invisible *and* click-through, so he sits on the
desktop rather than in a box on top of it, and the desktop underneath stays
usable everywhere he is not drawn.

**The socket is not in here.** `link.py` owns it and hands events over a
queue, which the Tk loop drains in `after` -- so nothing that touches the
network can block the animation clock, and the reconnect logic is testable by
a guard that cannot open a window. What is left in this file is drawing and
the three `after` loops that drive it: redraw, drain, and stat the theme file
for a hot reload.

**A dropped server is a state, not a crash.** A `__down__` from the link puts
him in `offline` and starts retrying; nothing about the window closes. The
server is restarted often during development and an overlay that had to be
restarted with it would be an overlay nobody left running.
"""

from __future__ import annotations

import json
import queue
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path

from ..protocol import DEFAULT_HOST, DEFAULT_PORT
from .anim import Frame, Player, Theme, ThemeError, available
from .link import DOWN, UP, Link
from .states import Machine

# How often the face is redrawn, and how often the event queue is drained. 33ms
# is 30fps: fast enough that a 100ms frame lands within a frame time of where
# the theme asked for it, slow enough to be invisible on a machine that is also
# holding a 260M model resident.
TICK_MS = 33
# How often a theme file is stat'ed for a hot reload. Cheap, and a second of
# lag between saving a theme and seeing it is not noticeable while editing.
RELOAD_MS = 700
RECONNECT_MS = 2000


def _rounded(canvas: tk.Canvas, box, r: int, **kw) -> int:
    """A rounded rectangle, which Tk's canvas does not have. `smooth` on a
    polygon whose corners are doubled points is the cheap standard trick and
    needs no images."""
    x1, y1, x2, y2 = box
    r = max(0, min(r, (x2 - x1) // 2, (y2 - y1) // 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class Overlay:
    def __init__(self, theme: Theme, host: str = DEFAULT_HOST,
                 port: int = DEFAULT_PORT, state_path: Path | None = None,
                 demo: bool = False):
        self.theme = theme
        self.machine = Machine()
        self.player = Player(theme)
        self.link = Link(host, port)
        self.state_path = state_path
        self.demo = demo
        self._images: dict[tuple, tk.PhotoImage] = {}
        self._sources: dict[tuple, tk.PhotoImage] = {}
        self._fonts: dict[tuple, tkfont.Font] = {}
        self._bubble_hidden = False
        self._drag = (0, 0)

        self.root = tk.Tk()
        self.root.title("Corn-Jr")
        self.root.overrideredirect(True)
        self._apply_window()

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.entry = tk.Entry(self.root, relief="flat", insertwidth=1)
        self._entry_window: int | None = None
        # Which theme the menu shows a dot beside. A `StringVar` needs a root,
        # so it is built here and not in `__init__`'s first half.
        self._theme_choice = tk.StringVar(self.root, str(theme.path))

        self._bind()
        self._place()
        self.player.rest("offline", self._now())
        if not demo:
            self.link.connect()

    # -- window chrome ------------------------------------------------------

    def _apply_window(self) -> None:
        w, h = self.theme.window["size"]
        self.root.geometry(f"{int(w)}x{int(h)}")
        clear = self.theme.window["transparent"]
        self.root.configure(bg=clear)
        try:
            self.root.attributes("-transparentcolor", clear)
        except tk.TclError:
            # Not Windows. The window keeps its background and stops being
            # click-through; everything else works, which is a better answer
            # than refusing to start on a platform the owner is not on.
            pass
        self.root.attributes("-topmost", bool(self.theme.window["topmost"]))
        try:
            self.root.attributes("-alpha", float(self.theme.window["alpha"]))
        except (tk.TclError, ValueError):
            pass

    def _place(self) -> None:
        """Bottom-right by default, or wherever it was last dragged to."""
        w, h = (int(v) for v in self.theme.window["size"])
        x = y = None
        if self.state_path is not None and self.state_path.exists():
            try:
                saved = json.loads(self.state_path.read_text(encoding="utf-8"))
                x, y = int(saved["x"]), int(saved["y"])
            except (OSError, ValueError, KeyError, TypeError):
                x = y = None
        if x is None:
            x = self.root.winfo_screenwidth() - w - 24
            y = self.root.winfo_screenheight() - h - 64
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _save_place(self) -> None:
        """Where he sits and which theme he is wearing, in one small file.

        Both are this machine's business rather than the repository's -- the
        same reasoning `notes.jsonl` and `contacts.json` are gitignored under.
        """
        if self.state_path is None:
            return
        try:
            self.state_path.write_text(
                json.dumps({"x": self.root.winfo_x(),
                            "y": self.root.winfo_y(),
                            "theme": str(self.theme.path)}),
                encoding="utf-8")
        except OSError:
            pass

    # -- input --------------------------------------------------------------

    def _bind(self) -> None:
        self.canvas.bind("<Button-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._drag_to)
        self.canvas.bind("<ButtonRelease-1>", lambda e: self._save_place())
        self.canvas.bind("<Double-Button-1>", lambda e: self._open_entry())
        self.canvas.bind("<Button-3>", self._menu)
        self.entry.bind("<Return>", self._submit)
        self.entry.bind("<Escape>", lambda e: self._close_entry())
        self.entry.bind("<KeyRelease>", lambda e: self._typing())
        self.root.bind("<Escape>", lambda e: self._close_entry())

    def _press(self, ev) -> None:
        self._drag = (ev.x_root - self.root.winfo_x(),
                      ev.y_root - self.root.winfo_y())

    def _drag_to(self, ev) -> None:
        self.root.geometry(f"+{ev.x_root - self._drag[0]}"
                           f"+{ev.y_root - self._drag[1]}")

    def _open_entry(self) -> None:
        b = self.theme.bubble
        w = int(self.theme.window["size"][0])
        self.entry.configure(font=tuple(b["font"]), bg=b["background"],
                             fg=b["color"], insertbackground=b["color"])
        if self._entry_window is None:
            self._entry_window = self.canvas.create_window(
                w // 2, int(self.theme.window["size"][1]) - 12,
                window=self.entry, width=w - 24, height=24)
        self.canvas.itemconfigure(self._entry_window, state="normal")
        self.entry.focus_force()

    def _close_entry(self) -> None:
        if self._entry_window is not None:
            self.canvas.itemconfigure(self._entry_window, state="hidden")
        self.entry.delete(0, "end")
        self.canvas.focus_set()

    def _typing(self) -> None:
        if self.entry.get().strip():
            self._cue(self.machine.listening())

    def _submit(self, _ev=None) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        if self.demo:
            self._cue(self.machine.submit(text))
            return
        if not self.link.up and not self.link.connect():
            return
        if self.link.send(op="turn", user=text):
            self._cue(self.machine.submit(text))

    def _menu(self, ev) -> None:
        m = tk.Menu(self.root, tearoff=0)
        m.add_command(label="Say something...", command=self._open_entry)

        themes = tk.Menu(m, tearoff=0)
        here = self.theme.path.resolve()
        for label, path in available(self.theme.path):
            themes.add_radiobutton(
                label=label, value=str(path),
                variable=self._theme_choice,
                command=lambda p=path: self._switch(p))
            if path.resolve() == here:
                self._theme_choice.set(str(path))
        m.add_cascade(label="Theme", menu=themes)
        m.add_command(label="Reload theme", command=lambda: self._reload(True))
        m.add_command(
            label="Show bubble" if self._bubble_hidden else "Hide bubble",
            command=self._toggle_bubble)
        m.add_separator()
        m.add_command(label="Forget history",
                      command=lambda: self.link.send(op="reset"))
        m.add_command(label="Reconnect", command=self._reconnect)
        m.add_separator()
        m.add_command(label="Quit", command=self.quit)
        try:
            m.tk_popup(ev.x_root, ev.y_root)
        finally:
            m.grab_release()

    def _toggle_bubble(self) -> None:
        self._bubble_hidden = not self._bubble_hidden

    def _reconnect(self) -> None:
        self.link.drop()
        self.link.connect()

    # -- the loops ----------------------------------------------------------

    def _now(self) -> float:
        """Milliseconds, from Tk's own clock so the animation and the redraw
        cannot drift apart."""
        return float(self.root.tk.call("clock", "milliseconds"))

    def _cue(self, cue) -> None:
        """Apply a `states.Cue`. The resting state and the flash are separate
        calls into the player because they are separate timescales -- see
        `states.py` on why a flash is not a state."""
        self.player.rest(cue.state, self._now(), self.machine.tool)
        if cue.flash:
            self.player.flash(cue.flash, self._now(), self.machine.tool)

    def _pump(self) -> None:
        drained = 0
        while drained < 200:
            try:
                ev = self.link.q.get_nowait()
            except queue.Empty:
                break
            drained += 1
            kind = ev.get("t")
            if kind == DOWN:
                self.link.drop()
                self._cue(self.machine.offline(ev.get("why", "")))
                self.root.after(RECONNECT_MS, self._retry)
                continue
            if kind == UP:
                continue
            if kind == "info":
                self._cue(self.machine.online())
                self.machine.note = (f"{ev.get('ckpt', '')} -- "
                                     f"{len(ev.get('tools', []))} tools")
                continue
            if kind in ("pong", "reset", "doc"):
                continue
            self._cue(self.machine.feed(ev))
        self.root.after(TICK_MS, self._pump)

    def _retry(self) -> None:
        if not self.link.up:
            self.link.connect()

    def _adopt(self, path) -> bool:
        """Load a theme and take it, or keep the one running and say why.

        **The running face is worth more than the save that broke it.** A
        theme is edited while it is on screen, so a typo mid-edit is the
        ordinary case, not the exceptional one; going blank on it would make
        every keystroke a risk. The error goes where the note goes and the
        last good theme keeps drawing.
        """
        try:
            fresh = Theme.load(path)
        except ThemeError as exc:
            self.machine.note = str(exc).splitlines()[0][:120]
            return False
        self.theme = fresh
        # Both caches, so re-saving a sprite sheet shows up on the next
        # reload rather than being served from the old decode.
        self._images.clear()
        self._sources.clear()
        self._fonts.clear()
        # Dropped rather than moved: it was placed against the old window's
        # height, and a theme with a different one would leave it floating.
        if self._entry_window is not None:
            self.canvas.delete(self._entry_window)
            self._entry_window = None
        self._apply_window()
        self.player.retheme(fresh, self._now())
        return True

    def _switch(self, path) -> None:
        """Change theme from the menu, and remember it. Remembering is the
        half that makes it a swap rather than a preview -- an overlay that
        went back to the shipped theme every restart would make choosing one
        something you do daily."""
        if self._adopt(path):
            self.machine.note = f"theme: {self.theme.name}"
            self._save_place()

    def _reload(self, force: bool = False) -> None:
        if force or self.theme.changed():
            self._adopt(self.theme.path)
        self.root.after(RELOAD_MS, self._reload)

    def _tick(self) -> None:
        self._draw(self.player.frame(self._now()))
        self.root.after(TICK_MS, self._tick)

    # -- drawing ------------------------------------------------------------

    def _font(self, spec) -> tkfont.Font:
        """Cached, because a `Font` object measures by asking Tk and this is
        called on every frame of a 30fps redraw."""
        key = tuple(spec)
        got = self._fonts.get(key)
        if got is None:
            got = self._fonts[key] = tkfont.Font(font=key)
        return got

    def _source(self, path: str, index: int) -> tk.PhotoImage:
        """The whole file, decoded once. A sprite sheet is one decode for
        however many frames are cut out of it, which is the other half of why
        a sheet is worth supporting at all."""
        key = (path, index)
        got = self._sources.get(key)
        if got is None:
            got = self._sources[key] = (
                tk.PhotoImage(file=path, format=f"gif -index {index}")
                if index else tk.PhotoImage(file=path))
        return got

    def _photo(self, frame: Frame) -> tk.PhotoImage | None:
        key = (frame.image, frame.index, frame.crop, frame.zoom,
               frame.subsample)
        got = self._images.get(key)
        if got is not None:
            return got
        try:
            got = self._source(frame.image, frame.index)
            if frame.crop:
                # **Tk's own `copy -from`, which keeps the alpha channel.**
                # Cropping is the one image operation this needs and the photo
                # image already has it; anything more would be a dependency.
                x1, y1, x2, y2 = frame.crop
                cut = tk.PhotoImage(width=x2 - x1, height=y2 - y1)
                cut.tk.call(cut, "copy", got, "-from", x1, y1, x2, y2,
                            "-to", 0, 0)
                got = cut
            # Whole-number scaling, because that is what Tk does without a
            # dependency -- and for pixel art it is also what you want:
            # `zoom` replicates pixels, so a 16x16 sprite at 5x stays a
            # 16x16 sprite rather than becoming a blurred one.
            if frame.zoom > 1:
                got = got.zoom(frame.zoom)
            if frame.subsample > 1:
                got = got.subsample(frame.subsample)
        except tk.TclError as exc:
            # Said rather than drawn as nothing. The load-time checks catch a
            # missing file and a cell out of range; what reaches here is a
            # file Tk could not decode -- a PNG variant it does not read, a
            # GIF index past the end -- and a blank face is the one symptom
            # that looks like a bug in the animation system.
            self.machine.note = f"{Path(frame.image).name}: {exc}"[:120]
            return None
        # Held on the instance because Tk keeps no reference of its own and a
        # garbage-collected PhotoImage draws as nothing at all.
        self._images[key] = got
        return got

    def _draw(self, frame: Frame) -> None:
        c = self.canvas
        c.delete("art")
        clear = self.theme.window["transparent"]
        c.configure(bg=clear)
        w = int(self.theme.window["size"][0])
        h = int(self.theme.window["size"][1])
        face, bub, note = self.theme.face, self.theme.bubble, self.theme.note

        fx = int(w * float(face["x"])) + frame.dx
        fy = int(h * float(face["y"])) + frame.dy

        top = 0
        if frame.image:
            photo = self._photo(frame)
            if photo is not None:
                c.create_image(fx, fy, image=photo, tags="art")
                top = fy - photo.height() // 2
        if frame.text:
            # **One canvas item per line, not one multi-line item.** A canvas
            # text item has no line-spacing option -- `spacing1` belongs to the
            # Text widget and Tk refuses it here -- and an ASCII face is mostly
            # line spacing. Drawing the lines separately is what makes `face.
            # spacing` a real knob instead of a documented lie.
            lines = frame.text.split("\n")
            font = self._font(face["font"])
            step = font.metrics("linespace") + int(face["spacing"])
            y0 = fy - (step * len(lines)) // 2 + step // 2
            for i, line in enumerate(lines):
                y = y0 + i * step
                # **The shadow is not decoration; it is what makes him legible
                # on a desktop whose colour nobody chose.** He is drawn over
                # whatever is behind the window, and a wallpaper the same
                # brightness as the face would erase him. It also hides the
                # fringe `-transparentcolor` leaves: the key colour is keyed
                # out exactly, but the antialiased pixels around a glyph are a
                # blend of the text and the key and survive, so unshadowed
                # text picks up a rim of whatever the key colour is.
                if face["shadow"]:
                    c.create_text(fx + 1, y + 1, text=line, tags="art",
                                  fill=face["shadow"],
                                  font=tuple(face["font"]), justify="center")
                c.create_text(fx, y, text=line, tags="art",
                              fill=frame.color or face["color"],
                              font=tuple(face["font"]), justify="center")
            box = c.bbox("art")
            top = box[1] if box else fy

        if note["show"] and self.machine.note:
            # Between the bubble and the face, anchored to its bottom so it
            # grows upward like the bubble does. Anchored the other way it
            # would print over the face on any note long enough to wrap --
            # and the notes that wrap are the refusal reasons, which are the
            # ones worth reading.
            item = c.create_text(w // 2, max(2, top - 3), text=self.machine.note,
                                 anchor="s", tags="art", fill=note["color"],
                                 font=tuple(note["font"]), width=w - 16)
            # On a panel for the same reason the bubble is on one. The note is
            # the smallest text on screen, so it is almost entirely edge, and
            # edge is exactly what `-transparentcolor` cannot key out cleanly.
            nb = c.bbox(item)
            if nb is not None:
                panel = _rounded(c, (nb[0] - 5, nb[1] - 2, nb[2] + 5, nb[3] + 2),
                                 5, fill=bub["background"], outline="",
                                 tags="art")
                c.tag_lower(panel, item)
            box = c.bbox("art")
            top = box[1] if box else top

        if self.machine.text and not self._bubble_hidden:
            self._bubble(c, w, top, bub)

    def _bubble(self, c: tk.Canvas, w: int, below: int, bub: dict) -> None:
        """Above the face, growing upward, trimmed from the front when it will
        not fit. The tail is what he is saying now; the head is what he already
        said, and losing the head is the right way round."""
        pad, width = int(bub["pad"]), int(bub["width"])
        # **Two caps, and the window is the one that is not negotiable.** The
        # theme's `lines` is what the author wants; the space between the top
        # of the window and whatever is under the bubble is what there is. A
        # theme that asks for more lines than fit used to draw them at
        # negative coordinates, which is not a clipped bubble so much as a
        # missing one -- the first lines of a reply, gone off the top edge.
        max_h = min(int(bub["lines"]) * self._font(bub["font"]).metrics("linespace"),
                    max(self._font(bub["font"]).metrics("linespace"),
                        below - 2 * pad - 4))
        text = self.machine.text
        item = c.create_text(w // 2, below - pad, text=text, anchor="s",
                             tags=("art", "bubbletext"), fill=bub["color"],
                             font=tuple(bub["font"]), width=width,
                             justify="left")
        box = c.bbox(item)
        # A handful of passes rather than a binary search: the text grows a
        # token at a time, so one pass is the common case and the loop only
        # ever runs on a reply that is already longer than the bubble.
        for _ in range(24):
            if box is None or (box[3] - box[1]) <= max_h or len(text) <= 40:
                break
            text = text[max(1, len(text) // 8):]
            c.itemconfigure(item, text="..." + text.lstrip())
            box = c.bbox(item)
        if box is None:
            return
        panel = _rounded(c, (box[0] - pad, box[1] - pad,
                             box[2] + pad, box[3] + pad),
                         int(bub["radius"]), fill=bub["background"],
                         outline=bub["border"], width=1, tags="art")
        c.tag_lower(panel, item)

    # -- lifecycle ----------------------------------------------------------

    def quit(self) -> None:
        self._save_place()
        self.link.close()
        self.root.destroy()

    def run(self) -> None:
        self.root.after(TICK_MS, self._tick)
        self.root.after(TICK_MS, self._pump)
        self.root.after(RELOAD_MS, self._reload)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.mainloop()
