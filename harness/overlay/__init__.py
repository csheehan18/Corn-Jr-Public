"""A face for the event stream `harness/protocol.py` already emits.

The overlay is a client and nothing more. It opens the same socket
`harness/client.py` opens, reads the same events, and its whole contribution
is that it draws them instead of printing them -- so anything it can show is
something the protocol already said, and a state it wants that the protocol
does not carry is a protocol change rather than an overlay one.

Four pieces, split on whether they need a display:

    states.py   events in, a state name out. No Tk, no socket.
    anim.py     a theme file in, frames out at a given moment. No Tk.
    link.py     the socket and its reader thread. No Tk.
    window.py   the only file that imports tkinter.

Three of the four are importable on a headless machine, which is the point of
the split: `scripts/check_overlay.py` covers everything that decides *what* he
does -- including the reconnect, against a real socket -- and leaves `window.py`
the one question a guard genuinely cannot answer, which is whether it looks
right. That is the two-guards discipline `scripts/check_server.py` is built on,
applied to the same boundary.
"""

from .anim import Animation, Frame, Player, Theme, ThemeError
from .link import Link
from .states import STATES, Cue, Machine

__all__ = ["Animation", "Cue", "Frame", "Link", "Machine", "Player", "STATES",
           "Theme", "ThemeError"]
