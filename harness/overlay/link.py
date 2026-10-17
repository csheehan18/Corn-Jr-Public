"""The socket and its reader thread. No Tk, so the guard can drive it.

**One writer, one reader, and a queue between them.** Turns are sent from
whichever thread owns the UI; events arrive on a background thread and are put
on `q` for that thread to drain when it likes. Nothing here blocks the caller,
which is the whole requirement: the face has to keep moving while a turn is in
flight, and a client that read the socket from its animation loop would freeze
on the first slow decode -- exactly when it most needs to look alive.

**A dropped server is an event, not an exception.** Both failure paths -- the
reader hitting EOF and a send raising -- put one `__down__` on the same queue,
so the caller has a single place to go back to `offline` and a single place to
start retrying. The server gets restarted constantly during development, and
an overlay that had to be restarted with it is an overlay nobody leaves
running.

The two synthetic events are underscored the way `corn/agent.py` underscores
`__eot__`: they are this module's, not the protocol's, and must never be
mistaken for something the server said.
"""

from __future__ import annotations

import json
import queue
import socket
import threading

from ..client import Client
from ..protocol import DEFAULT_HOST, DEFAULT_PORT

UP = "__up__"
DOWN = "__down__"


class Link:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host, self.port = host, port
        self.q: queue.Queue = queue.Queue()
        self.client: Client | None = None
        self._reader: threading.Thread | None = None

    @property
    def up(self) -> bool:
        return self.client is not None

    def connect(self) -> bool:
        """Connect and ask for `info`. Idempotent: already-up is success, so a
        retry timer that fires once more than it needed to costs nothing."""
        if self.client is not None:
            return True
        try:
            self.client = Client(self.host, self.port)
        except OSError as exc:
            self.client = None
            self.q.put({"t": DOWN, "why": str(exc)})
            return False
        self._reader = threading.Thread(target=self._read, args=(self.client,),
                                        daemon=True)
        self._reader.start()
        self.q.put({"t": UP})
        # The reply is what actually moves him out of `offline`: a socket that
        # connected to something that is not answering is not a server yet.
        self.send(op="info")
        return True

    def _read(self, client: Client) -> None:
        try:
            for line in client.rx:
                if line.strip():
                    self.q.put(json.loads(line))
        except (OSError, ValueError) as exc:
            self.q.put({"t": DOWN, "why": str(exc)})
            return
        self.q.put({"t": DOWN, "why": "the server closed the connection"})

    def send(self, **req) -> bool:
        """From the owning thread only. A failure is reported as `__down__`
        rather than raised, so both ends of a broken connection arrive at the
        caller the same way."""
        if self.client is None:
            return False
        try:
            self.client.send(**req)
            return True
        except OSError as exc:
            self.q.put({"t": DOWN, "why": str(exc)})
            return False

    def drop(self) -> None:
        """Forget the connection, and unblock the reader before doing it.

        **`shutdown` first, then `close`, and the order is the whole point.**
        The reader thread is parked inside `readline` on a file object wrapping
        this socket. Closing the file out from under a blocked read does not
        wake it on Windows -- it hangs, and because `drop` is called from the
        UI thread (the Reconnect menu item, and every retry after a server
        restart) the hang is the face freezing. `shutdown` tears down the
        connection itself, which is what the blocked read is actually waiting
        on; it returns, posts its `__down__`, and the thread ends.

        Both calls are guarded because either can find the socket already gone
        -- which is the ordinary case when the server is what dropped first.
        """
        client, self.client = self.client, None
        if client is None:
            return
        try:
            client.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            client.close()
        except OSError:
            pass

    close = drop
