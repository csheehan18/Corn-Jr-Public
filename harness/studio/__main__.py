"""One command that starts everything: the server, the page, the sitting.

    python -m harness.studio
    python -m harness.studio --no-server        # attach to a running server
    python -m harness.studio --ui-port 8770
    python -m harness.studio --tab              # a browser tab, not a window

**The page binds 127.0.0.1 and so does the server it spawns, and moving
either is a decision.** The studio is an unauthenticated web page wired to a
server that has no authentication and executes real tools -- `server.py`'s
own `--host` warning, and it applies twice here. `--ui-host` exists for the
LAN case and shares that sentence.

**A window, not a tab, by default.** Edge's `--app` mode -- present on every
Windows machine -- opens the page as a borderless window with its own
taskbar entry, which is what a thing used every day should feel like, and
costs no dependency. Chrome is the second choice, a browser tab the third;
`--tab` asks for the tab, `--no-browser` for nothing (a headless machine that
somebody browses to from elsewhere).

**One studio per machine, and a double-click is a launcher.** If a studio
already answers on the port, a second launch opens a window onto it and
exits instead of failing to bind -- so the shortcut `scripts/
studio_shortcut.py` makes (`pythonw -m harness.studio`, no console) is the
same gesture whether the studio is running or not. With no console there is
nothing to Ctrl+C: the page's Quit action stops the studio and the server it
owns, and the output that would have gone to a terminal goes to
`~/.corn-jr/logs/studio.log`; a missing dependency is a message box rather
than a silent nothing.

**A first run is handled before a server is spawned.** `firstrun.py` checks
that the configured checkpoint is on disk; when it is not, the page opens on
a setup card instead of a crash tail, and the server starts only once a
checkpoint that exists has been picked and saved.

Starlette and uvicorn are imported inside `main` behind a hint, on the voice
client's faster-whisper posture: they are optional, and the failure a fresh
clone hits should be one line saying what to install rather than a
traceback. The page itself is static files under `web/` with its libraries
vendored (`web/vendor/README.md`): no npm, no build step, nothing fetched
from the internet at runtime.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

from ..serverconfig import DEFAULT_CONFIG

# Where Edge and Chrome live when they are not on PATH, which on Windows is
# usual. First hit wins.
_APP_BROWSERS = (
    "msedge", "chrome",
    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
    r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
)


def app_browser() -> str | None:
    for cand in _APP_BROWSERS:
        if "%" in cand:
            path = Path(os.path.expandvars(cand))
            if path.is_file():
                return str(path)
        elif shutil.which(cand):
            return shutil.which(cand)
    return None


def open_when_listening(url: str, host: str, port: int, tab: bool) -> None:
    """Wait for the port, then open the window (or the tab). On a thread, so
    uvicorn's startup is never held up by it."""
    def go() -> None:
        end = time.monotonic() + 15
        while time.monotonic() < end:
            try:
                with socket.create_connection((host, port), timeout=0.25):
                    break
            except OSError:
                time.sleep(0.1)
        exe = None if tab else app_browser()
        if exe is not None:
            try:
                subprocess.Popen([exe, f"--app={url}",
                                  "--window-size=1320,880"],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return
            except OSError:
                pass
        webbrowser.open(url)

    threading.Thread(target=go, daemon=True).start()


LOG_FILE = Path.home() / ".corn-jr" / "logs" / "studio.log"


def windowless() -> bool:
    """Launched by pythonw (the shortcut): no console to print to."""
    return sys.stdout is None or sys.stderr is None


def tell(message: str) -> None:
    """A sentence the person must see: the console when there is one, a
    message box when there is not."""
    if not windowless():
        print(message)
        return
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, "Corn-Jr Studio", 0x40)
    except (ImportError, AttributeError, OSError):
        pass


def already_running(host: str, port: int) -> bool:
    """A studio answers here -- its own /api/boot, not merely an open port,
    so another program on 8770 is not mistaken for one."""
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/api/boot",
                                    timeout=0.6) as r:
            return "config" in json.loads(r.read().decode("utf-8"))
    except (OSError, ValueError):
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG,
                    help="the server.json this studio reads, writes and "
                         "starts the server on")
    ap.add_argument("--ui-host", default="127.0.0.1",
                    help="where the page itself listens. 127.0.0.1 by "
                         "default; a LAN bind is a decision -- this page "
                         "has no authentication and drives a server that "
                         "executes tools")
    ap.add_argument("--ui-port", type=int, default=8770)
    ap.add_argument("--no-server", action="store_true",
                    help="never spawn a server; attach to one already "
                         "running, like every other client")
    ap.add_argument("--no-browser", action="store_true",
                    help="serve the page without opening anything")
    ap.add_argument("--tab", action="store_true",
                    help="open a browser tab instead of an app window")
    args = ap.parse_args()

    if windowless():
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        log = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = log
        print(f"\n-- studio starting {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # A wildcard bind is still browsed at loopback on this machine.
    here = "127.0.0.1" if args.ui_host in ("0.0.0.0", "::") else args.ui_host
    url = f"http://{here}:{args.ui_port}/"
    if already_running(here, args.ui_port):
        print(f"studio: already running at {url}; opening it")
        if not args.no_browser:
            open_when_listening(url, here, args.ui_port, args.tab)
            time.sleep(1.0)  # the opener is a daemon thread
        return

    try:
        import uvicorn

        from .app import Studio, build
    except ImportError:
        tell("The studio needs Starlette and uvicorn, which are optional and "
             "not installed:\n\npip install \"starlette>=0.37\" "
             "\"uvicorn>=0.29\" websockets\n\n"
             "(the server, the terminal client, the overlay and the voice "
             "client all run without them)")
        raise SystemExit(1)

    studio = Studio(args.config, no_server=args.no_server)
    app = build(studio)
    print(f"studio: {url}")
    if not args.no_browser:
        open_when_listening(url, here, args.ui_port, args.tab)
    server = uvicorn.Server(uvicorn.Config(
        app, host=args.ui_host, port=args.ui_port, log_level="warning",
        access_log=False))
    studio.on_quit = lambda: setattr(server, "should_exit", True)
    server.run()


if __name__ == "__main__":
    main()
