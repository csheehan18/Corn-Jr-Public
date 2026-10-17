# Themes — how he looks, and how to change it

Everything about the overlay's appearance is one JSON file. Nothing in
`harness/overlay/` needs editing to change a frame, a colour, a timing, or
which state plays what.

## Swapping

**A theme you are editing** — just save it. The file is re-read about once a
second, along with every image it references, and the face changes under you.
Nothing to restart, nothing to click. Right-click → **Reload theme** forces it
if you are impatient.

**Between themes** — right-click → **Theme**, and pick one. It changes
immediately and the choice is remembered, so that is the whole swap: one click,
once.

**Making a new one** — drop it in this directory and it appears in that menu.
Two shapes, both found automatically:

```
themes/mine.json            a theme on its own
themes/mine/theme.json      a theme with its art beside it
```

The second is the one you want for pixel art: the whole directory copies and
moves as one thing. Start by copying `default.json` or the `pixel/` directory.

```bash
python -m harness.overlay --themes   # what is on offer, and where
```

`--theme` still exists for trying one without committing to it, or for a file
kept somewhere else. A bare name is looked up here first, and an explicit
`--theme` beats the remembered one:

```bash
python -m harness.overlay --theme pixel
python -m harness.overlay --theme ~/somewhere/else.json
```

## Editing

Two things make it fast enough to be worth doing:

```bash
python -m harness.overlay --demo     # every state in turn, no server, no GPU
python -m harness.overlay --check    # load it, describe it, exit non-zero if broken
```

`--demo` matters more than it sounds. Some states are rare on purpose:
`covered` fires only when the runtime had to write his reply because
`corn.agent.social_rejection` refused his, and you cannot ask for that. The
demo drives the same state machine with synthetic events, so you can write
those frames and watch them without a model loaded.

A bad save never costs you the running face — the reload catches the error,
keeps the theme it already had, and prints the message where the note goes.

---

## The states

The overlay's whole vocabulary. Each one is something
[`harness/protocol.py`](../../protocol.py) already says; none of them is
guessed from timing or from what the words looked like.

| state | when |
|---|---|
| `offline` | no server, or the connection went away |
| `idle` | connected, nothing in flight |
| `listening` | you are typing into him |
| `thinking` | a turn was sent, nothing has come back |
| `queued` | a `waiting` event — he is behind another turn |
| `tool` | a call the schema accepted, and its `obs` |
| `speaking` | `text` events, or a `say` that differs from them |

Those seven **rest**: they last until something changes them. The next five
**flash**: they play once over whatever is resting and hand back.

| flash | when |
|---|---|
| `refused` | a call the schema would not run, or a `rejected` |
| `covered` | a reply he did not write — `fell_back`, or an `author` that is not `model` |
| `error` | an `error` event: the request, not the model |
| `confirmed` | the confirmation gate resolved yes |
| `cancelled` | the confirmation gate resolved no |

The split is why a refusal is visible at all. It lands one event before `done`,
so a state built out of it would be on screen for about a millisecond.

---

## The file

Every key is optional except `animations`. This is a complete, working theme:

```json
{"animations": {"idle": {"ms": 600, "frames": ["o_o", "-_-"]}}}
```

### `animations`

A name to a list of frames, or to an object with `frames` plus any of:

| key | means |
|---|---|
| `ms` | milliseconds per frame (default 120) |
| `fps` | frames per second, instead of `ms` — not both |
| `color` | the colour for frames that do not set their own |
| `sheet` | a sprite sheet beside the theme; frames become cell numbers |
| `cell` | `[width, height]` of one cell, in pixels — required with `sheet` |
| `zoom` | scale every frame up by a whole number |
| `subsample` | scale every frame down by a whole number |

A **frame** is one of four things:

```json
"( o.o )"                                    a line
[" \\|// ", "( o.o )", " ||||| "]            lines, top to bottom
3                                            a cell of the animation's sheet
{"text": "( o.o )", "ms": 40, "dy": -2}      or spell it out
```

The object form takes `text`, `image`, `cell`, `index`, `ms`, `dx`, `dy`,
`color`, `zoom`, `subsample`. `dx`/`dy` shift that frame in pixels, which is
how the shipped `refused` shakes and `yes` bounces. `ms` overrides the
animation's rate for that frame alone — the shipped flashes end on a long
resting frame that way, so the flash holds for a moment before handing back.

---

## Pixel art

Everything below works today; [`pixel/`](pixel/) is a complete worked theme
that drives all twelve states off a single six-cell strip. Copy the directory,
draw over `strip.png`, keep the cell size or change it in one place.

```bash
python -m harness.overlay --demo --theme harness/overlay/themes/pixel/theme.json
```

**Sprite sheets.** Declare the sheet and the cell size once on the animation,
then frames are cell numbers — counted left to right, then top to bottom, which
is the order every editor exports a strip or a grid in:

```json
"talk": {
  "sheet": "strip.png", "cell": [16, 20], "zoom": 5,
  "ms": 150,
  "frames": [0, 2, {"cell": 2, "dy": 1}]
}
```

The sheet is decoded once no matter how many frames come out of it. A cell
number past the end is refused at load, and it tells you how many the sheet
actually holds; a sheet that is not a whole number of cells across is refused
too, rather than quietly serving you half a sprite.

**Individual files** still work — `{"image": "walk-01.png"}` — and mixing image
and text frames in one animation is fine.

**Animated GIFs.** `{"image": "walk.gif", "index": 3}` picks one frame out of a
multi-frame GIF, which is the other thing pixel editors export.

**Scale.** `zoom` and `subsample` are whole numbers, because that is what Tk
does without a dependency — and for pixel art it is also what you want: `zoom`
replicates pixels, so a 16×20 sprite at `"zoom": 5` is a crisp 80×100 rather
than a blurred one. Set it on the animation and every frame inherits it; set it
on a frame to override. `--check` prints the drawn size, which is the number
nobody can do in their head.

**Transparency.** PNG alpha works: fully transparent pixels come out as the key
colour and are keyed straight through to the desktop, so a sprite on a
transparent background needs nothing done to it. `face.shadow` is for text and
does not apply to images.

**Saving art reloads it.** The watch covers every image the theme references,
not just the JSON — so you can redraw an eye, hit save in your editor, and see
him blink about a second later without touching anything else.

---

**Per-tool animations.** An animation named `tool:web_search` is used instead
of the `tool` state while that call is in flight. Name one per tool you care
about; every other tool keeps the generic one.

### `states`

Which animation each state plays. Anything unmapped falls back to an animation
of the same name, then to `idle` — so `idle` is the one animation every theme
must have.

```json
"states": {"thinking": "think", "speaking": "talk", "refused": "boom"}
```

### `window`, `face`, `bubble`, `note`

| section | keys |
|---|---|
| `window` | `size` `[w, h]`, `transparent`, `alpha`, `topmost` |
| `face` | `font` `[family, size]`, `color`, `x`, `y` (fractions of the window), `spacing`, `shadow` |
| `bubble` | `font`, `color`, `background`, `border`, `width`, `lines`, `pad`, `radius` |
| `note` | `font`, `color`, `show` |

`window.transparent` is the key colour: on Windows every pixel of it is
invisible **and** click-through, which is what makes him sit on the desktop
instead of in a box on top of it. Two consequences worth knowing before you
change it:

- Do not use a colour your art contains — those pixels vanish too.
- Antialiased edges are a blend of the glyph and the key colour, and they
  survive the keying. A bright key colour puts a rim of itself around every
  letter. The default is near-black for that reason, and `face.shadow` covers
  the rest; set `shadow` to `""` to turn it off.

`bubble.lines` is a preference, not a guarantee: the bubble is also capped by
the space above whatever is under it, so it can never run off the top of the
window. When a reply outgrows the bubble it is trimmed from the **front** —
the tail is what he is saying now.

---

## What it will refuse

Loudly, at load, with the JSON path that caused it — because the failure worth
catching is a typo, and a typo that loads and draws nothing looks like a bug in
the animation system.

- an unknown key, in any section, in an animation, or in a frame
- a theme with no `animations`, or with no `idle`
- an animation with no frames, or with both `ms` and `fps`
- a `states` key that is not one of the twelve states
- a `states` value naming an animation that does not exist
- an `image` or `sheet` path that is not there
- a frame with none of `text`, `image` or `cell`
- a `sheet` without a `cell` size, or a `cell` size without a `sheet`
- a sheet that is not a whole number of cells across or down
- a cell number past the end of its sheet — it says how many there are
- a bare number frame in an animation that has no sheet
- an `index` on anything but a GIF
- a `zoom` or `subsample` below 1
