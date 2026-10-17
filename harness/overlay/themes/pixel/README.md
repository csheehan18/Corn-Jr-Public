# pixel — a worked sprite-sheet theme

All twelve states off one strip, so the format has a running example rather
than only a description.

```bash
python -m harness.overlay --demo --theme harness/overlay/themes/pixel/theme.json
```

`strip.png` is a **placeholder** — 6 cells of 16×20, drawn to be overwritten.
Keep the cell layout and your own art drops straight in:

| cell | used for |
|---|---|
| 0 | at rest, eyes open |
| 1 | blink — also `queued`, `cancelled`, `offline` |
| 2 | mouth open, for `speaking` |
| 3 | looking up, for `thinking` and `tool` |
| 4 | eyes crossed, for `refused` and `error` |
| 5 | pleased, for `confirmed` and `listening` |

Change the layout freely — `cell` in `theme.json` is the only place the size is
written down, and cell numbers run left to right then top to bottom, so a 6×2
grid is cells 0–11 with no other edit. `--check` prints the grid it found and
the size each frame is drawn at:

```bash
python -m harness.overlay --check --theme harness/overlay/themes/pixel/theme.json
```

Transparent pixels key straight through to the desktop, and saving the PNG
reloads it in a running overlay without touching the JSON. The format is in
[../README.md](../README.md).
