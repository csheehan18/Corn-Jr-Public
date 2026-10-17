"""The studio's web layer: one page, one WebSocket, and a JSON route per edit.

**Thin on purpose.** Everything a route decides is in a framework-free module
-- `views` for the pages, `configform` for `server.json`, `sitting` for the
conversation, `supervisor` for the process -- so this file is wiring: parse
the request, call the function, return its dict. A rule found here rather
than there is in the wrong file.

**Why Starlette.** It is the small ASGI toolkit FastAPI is built on -- routing,
a WebSocket, static files, a test client -- and nothing else: no component
model, no server-side widget tree, no second event loop. The NiceGUI studio
drew every widget from Python and round-tripped every click; here the page
is static files drawn in the browser (`web/`), and the only things that cross
the wire are the protocol's own events and the JSON a page asks for.

**The WebSocket carries the conversation and nothing else.** On connect the
tab is handed `Sitting.snapshot()` -- the sitting so far, the link, the
supervisor's state -- and then every event as it lands. Whatever has queued
while a frame was being written goes out as one array frame, so a burst costs
one write and a lone token is never held back waiting for company. Turns,
reset, document and window requests come back up the same socket.

**Every page and route is unauthenticated, and binds 127.0.0.1 by default**
-- `__main__.py`'s sentence, which applies here unchanged.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import tempfile
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, Response
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect

from ..client import SAVE_DIR
from ..serverconfig import ConfigError, ServerConfig
from . import configform, firstrun, views
from .sitting import Sitting
from .supervisor import REPO_ROOT, Supervisor

WEB = Path(__file__).resolve().parent / "web"

# A dropped document is written here before the server is pointed at it --
# the temp folder, so a personal file never lands inside the repo.
DOC_DIR = Path(tempfile.gettempdir()) / "corn-jr-studio-docs"
DOC_SUFFIXES = (".txt", ".md")

# Where the conversation waits across a studio restart (sitting.py): beside
# the saved transcripts, in a folder gitignored for this content -- for the
# instance's own server.json. Any other config keeps its conversation next to
# itself, so a temporary instance (a guard's, a test's) never leaves one in
# the owner's folder.
STATE_FILE = SAVE_DIR / "studio-sitting.json"


def state_file(cfg_path: Path) -> Path:
    from ..serverconfig import DEFAULT_CONFIG
    if Path(cfg_path).resolve() == Path(DEFAULT_CONFIG).resolve():
        return STATE_FILE
    return Path(cfg_path).with_name(Path(cfg_path).stem + ".sitting.json")
MAX_UPLOAD = 32 * 1024 * 1024


class Studio:
    """The process-wide state every route shares."""

    def __init__(self, cfg_path: Path, *, repo: Path = REPO_ROOT,
                 no_server: bool = False, supervisor: Supervisor | None = None,
                 state_path: Path | None | type(...) = ...):
        self.repo = Path(repo)
        # Set by __main__ to stop uvicorn; the Quit action calls it.
        self.on_quit = None
        self.cfg_path = Path(cfg_path)
        self.no_server = no_server
        self.config_problem = ""
        try:
            self.cfg = ServerConfig.load(self.cfg_path)
        except ConfigError as exc:
            # The form still opens -- on defaults -- because the form is how
            # the file gets fixed. Saving writes a good file over the bad.
            self.cfg = ServerConfig()
            self.config_problem = str(exc)
        self.supervisor = supervisor or Supervisor(self.cfg_path)
        if state_path is ...:
            state_path = state_file(self.cfg_path)
        self.sitting = Sitting(lambda: (self.cfg.host, self.cfg.port),
                               status=self.status, state_path=state_path)

    def status(self) -> tuple[str, str, bool]:
        """`(state, why, pending)`: the supervisor's answer and whether a
        saved change waits on a restart -- or, with `--no-server`, whether
        anything answers at all, since there is no process of ours to ask
        about and nothing of ours to restart."""
        if self.no_server:
            where = f"{self.cfg.host}:{self.cfg.port}"
            return (("up", f"attached to a server on {where}", False)
                    if self.supervisor.ping()
                    else ("stopped", f"waiting for a server on {where}", False))
        state, why = self.supervisor.status()
        return state, why, self.supervisor.pending()

    def set_cfg(self, cfg: ServerConfig) -> None:
        self.cfg = cfg
        self.config_problem = ""

    def save_fields(self, values: dict) -> ServerConfig:
        self.set_cfg(configform.save(self.cfg, values, self.cfg_path))
        return self.cfg

    def restart(self) -> str:
        if self.no_server:
            return "the studio was started with --no-server; restart the " \
                   "server where it is running"
        return (firstrun.blocking(self.cfg, self.repo)
                or self.supervisor.restart())


class Revalidate:
    """`Cache-Control: no-cache` on every static file, as raw ASGI so the
    WebSocket and the API pass through untouched. Each file is revalidated --
    a 304 on loopback costs about a millisecond -- so an edited script is
    never served stale from a heuristic cache and nothing needs a version in
    its URL."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith("/static/"):
            return await self.app(scope, receive, send)

        async def patched(message):
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                message["headers"] = [
                    (k, v) for k, v in message["headers"]
                    if k.lower() != b"cache-control"] + [
                    (b"cache-control", b"no-cache")]
            await send(message)

        return await self.app(scope, receive, patched)


def _err(msg: str, status: int = 400) -> JSONResponse:
    return JSONResponse({"error": msg}, status_code=status)


async def _body(request: Request) -> dict:
    try:
        data = await request.json()
    except (ValueError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def build(studio: Studio) -> Starlette:
    s = studio

    def guarded(fn):
        """`Refused` and `ConfigError` become a 400 carrying their sentence;
        anything else is a bug and propagates."""
        async def route(request: Request) -> Response:
            try:
                out = await fn(request)
            except (views.Refused, ConfigError) as exc:
                return _err(str(exc))
            if isinstance(out, Response):
                return out
            return JSONResponse({} if out is None else out)
        return route

    def sync(fn, *args):
        return asyncio.to_thread(fn, *args)

    # -- the page ------------------------------------------------------------

    async def index(request: Request) -> Response:
        return FileResponse(WEB / "index.html",
                            headers={"Cache-Control": "no-cache"})

    # -- boot, setup, server -------------------------------------------------

    @guarded
    async def boot(request: Request):
        found = firstrun.checkpoints(s.repo)
        why = firstrun.reasons(s.cfg, s.cfg_path, s.repo)
        return {"config": s.cfg_path.name, "config_problem": s.config_problem,
                "no_server": s.no_server,
                "setup": ({"reasons": why, "checkpoints": found,
                           "hint": firstrun.WEIGHTS_HINT} if why else None)}

    @guarded
    async def setup(request: Request):
        body = await _body(request)
        ckpt = str(body.get("ckpt") or "")
        if not ckpt:
            raise views.Refused("pick a checkpoint")
        cfg = ServerConfig.load(s.cfg_path) if s.cfg_path.exists() \
            else ServerConfig()
        firstrun.bootstrap(cfg, s.cfg_path, s.repo, ckpt)
        s.set_cfg(cfg)
        problem = "" if s.no_server else await sync(s.restart)
        return {"problem": problem,
                "note": problem or f"wrote {s.cfg_path.name}; he is starting"}

    @guarded
    async def server(request: Request):
        sup = s.supervisor
        state, why, pending = await sync(s.status)
        host, port = s.cfg.host, s.cfg.port
        pid = getattr(sup.proc, "pid", None) if sup.proc is not None else None
        return {"state": state, "why": why, "pending": pending,
                "external": sup.external,
                "no_server": s.no_server, "addr": f"{host}:{port}",
                "pid": pid, "config": s.cfg_path.name,
                "tail": list(sup.tail)}

    @guarded
    async def server_action(request: Request):
        action = request.path_params["action"]
        sup = s.supervisor
        if s.no_server:
            raise views.Refused("the studio was started with --no-server; "
                                "it does not own a process to drive")
        if action == "start":
            why = await sync(lambda: firstrun.blocking(s.cfg, s.repo)
                             or sup.start())
        elif action == "restart":
            why = await sync(s.restart)
        elif action == "stop":
            if sup.external:
                raise views.Refused("that server was not started by the "
                                    "studio; stop it where it is running")
            await sync(sup.stop)
            why = ""
        else:
            return _err(f"unknown action {action!r}", 404)
        return {"note": why or f"{action} sent", "warn": bool(why)}

    @guarded
    async def quit_studio(request: Request):
        """Stop the studio -- and the server it owns -- from the page, which
        is the only way to when it was launched with no console."""
        if s.on_quit is None:
            raise views.Refused("this studio was not started by its own "
                                "launcher; stop it where it is running")
        asyncio.get_running_loop().call_later(0.2, s.on_quit)
        return {"note": "Closing the studio" + (
            "" if s.no_server else " and stopping him")}

    # -- settings ------------------------------------------------------------

    @guarded
    async def config_get(request: Request):
        return {"config": s.cfg_path.name, "problem": s.config_problem,
                **configform.schema(s.cfg, s.repo),
                "restored": configform.restored(s.cfg)}

    @guarded
    async def config_put(request: Request):
        body = await _body(request)
        s.save_fields(body.get("values") or {})
        why = await sync(s.restart) if body.get("restart") else ""
        return {"note": why or (f"saved {s.cfg_path.name}"
                                + ("; he is restarting" if body.get("restart")
                                   else "")),
                "warn": bool(why)}

    # -- tools ---------------------------------------------------------------

    @guarded
    async def tools_get(request: Request):
        return await sync(views.tools, s.cfg, s.repo)

    @guarded
    async def tools_put(request: Request):
        body = await _body(request)
        values = {}
        if "enabled" in body:
            values["tools"] = views.tool_selection(list(body["enabled"]))
        if "decline" in body:
            values["decline"] = bool(body["decline"])
        if "tools_dir" in body:
            values["tools_dir"] = str(body["tools_dir"] or "")
            if values["tools_dir"]:
                views.at(s.repo, values["tools_dir"]).mkdir(
                    parents=True, exist_ok=True)
        s.save_fields(values)
        why = await sync(s.restart) if body.get("restart") else ""
        return {"note": why or "saved", "warn": bool(why)}

    @guarded
    async def decl_put(request: Request):
        body = await _body(request)
        return views.write_declaration(s.cfg, s.repo, body.get("decl") or {},
                                       body.get("file") or None)

    @guarded
    async def decl_delete(request: Request):
        views.delete_declaration(s.cfg, s.repo, request.path_params["file"])

    @guarded
    async def decl_test(request: Request):
        body = await _body(request)
        return await sync(views.test_run, s.cfg, s.repo,
                          request.path_params["file"], body.get("args") or {})

    # -- packs ---------------------------------------------------------------

    @guarded
    async def packs_get(request: Request):
        return await sync(views.packs, s.cfg, s.repo)

    @guarded
    async def packs_folder(request: Request):
        body = await _body(request)
        folder = str(body.get("folder") or "")
        s.save_fields({"packs": folder})
        if folder:
            views.at(s.repo, folder).mkdir(parents=True, exist_ok=True)

    @guarded
    async def pack_file_get(request: Request):
        return views.read_pack_file(s.cfg, s.repo, request.path_params["name"])

    @guarded
    async def pack_file_put(request: Request):
        return views.write_pack_file(s.cfg, s.repo,
                                     request.path_params["name"],
                                     await _body(request))

    @guarded
    async def pack_file_delete(request: Request):
        views.delete_pack_file(s.cfg, s.repo, request.path_params["name"])

    @guarded
    async def pack_new(request: Request):
        body = await _body(request)
        return views.new_pack_file(s.cfg, s.repo, str(body.get("name") or ""))

    @guarded
    async def pack_upload(request: Request):
        name = request.query_params.get("name", "")
        data = await request.body()
        if len(data) > MAX_UPLOAD:
            raise views.Refused("that file is larger than the studio takes")
        return views.upload_pack_file(
            s.cfg, s.repo, name, data,
            request.query_params.get("replace") == "1")

    @guarded
    async def pack_lint(request: Request):
        body = await _body(request)
        return views.lint_table([str(h) for h in body.get("header") or []],
                                [[str(c) for c in r]
                                 for r in body.get("rows") or []])

    @guarded
    async def pack_persona(request: Request):
        views.save_persona(s.cfg, s.repo, await _body(request))

    @guarded
    async def pack_about(request: Request):
        views.save_about(s.cfg, s.repo,
                         str((await _body(request)).get("body") or ""))

    @guarded
    async def pack_vocab(request: Request):
        views.save_vocab(s.cfg, s.repo,
                         (await _body(request)).get("pairs") or [])

    @guarded
    async def pack_try(request: Request):
        body = await _body(request)
        return await sync(views.try_question, s.cfg, s.repo,
                          str(body.get("q") or ""))

    # -- memory --------------------------------------------------------------

    @guarded
    async def memory_get(request: Request):
        return await sync(views.memory, s.cfg, s.repo)

    @guarded
    async def memory_note_delete(request: Request):
        ok = views.delete_note(s.cfg, s.repo,
                               int(request.path_params["line"]))
        return {"ok": ok, "note": "deleted" if ok else
                "the file changed under the page; reloaded"}

    @guarded
    async def memory_marker_delete(request: Request):
        views.forget_marker(s.cfg, s.repo)

    @guarded
    async def memory_turns_delete(request: Request):
        views.clear_turns(s.cfg, s.repo)

    # -- about ---------------------------------------------------------------

    @guarded
    async def about(request: Request):
        return await sync(views.about, s.repo)

    # -- the conversation ----------------------------------------------------

    @guarded
    async def transcript_save(request: Request):
        path = await sync(s.sitting.save_transcript)
        return {"path": str(path), "name": Path(path).name}

    @guarded
    async def doc_upload(request: Request):
        """A dropped file is written to the temp folder and the server is
        pointed at it with the protocol's own `doc` op; the reply arrives on
        every tab's socket like any other event."""
        name = views.basename(request.query_params.get("name", ""),
                              DOC_SUFFIXES)
        data = await request.body()
        if len(data) > MAX_UPLOAD:
            raise views.Refused("that document is larger than the studio "
                                "takes")
        DOC_DIR.mkdir(parents=True, exist_ok=True)
        path = DOC_DIR / name
        path.write_bytes(data)
        if not await s.sitting.send(op="doc", path=str(path)):
            raise views.Refused("he is not connected -- the document will "
                                "load once he is")
        return {"ok": True}

    async def ws(socket: WebSocket) -> None:
        await socket.accept()
        q = s.sitting.subscribe()

        async def pump() -> None:
            await socket.send_text(json.dumps(s.sitting.snapshot(),
                                              ensure_ascii=False))
            while True:
                batch = [await q.get()]
                while not q.empty():
                    batch.append(q.get_nowait())
                await socket.send_text(json.dumps(
                    batch if len(batch) > 1 else batch[0],
                    ensure_ascii=False))

        sender = asyncio.create_task(pump())
        try:
            while True:
                msg = json.loads(await socket.receive_text())
                op = msg.get("op")
                if op == "turn":
                    await s.sitting.send(op="turn",
                                         user=str(msg.get("user") or ""))
                elif op in ("reset", "window", "info"):
                    await s.sitting.send(op=op)
                elif op == "doc":
                    await s.sitting.send(op="doc",
                                         path=str(msg.get("path") or ""))
        except (WebSocketDisconnect, ValueError, RuntimeError):
            pass
        finally:
            s.sitting.unsubscribe(q)
            sender.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await sender

    @contextlib.asynccontextmanager
    async def lifespan(app):
        if not s.no_server:
            why = await sync(lambda: firstrun.blocking(s.cfg, s.repo)
                             or s.supervisor.start())
            if why:
                print(f"studio: {why}")
        s.sitting.start()
        try:
            yield
        finally:
            await s.sitting.stop()
            if not s.no_server:
                await sync(s.supervisor.stop)

    api = [
        Route("/api/boot", boot),
        Route("/api/setup", setup, methods=["POST"]),
        Route("/api/server", server),
        Route("/api/server/{action}", server_action, methods=["POST"]),
        Route("/api/quit", quit_studio, methods=["POST"]),
        Route("/api/config", config_get),
        Route("/api/config", config_put, methods=["PUT"]),
        Route("/api/tools", tools_get),
        Route("/api/tools", tools_put, methods=["PUT"]),
        Route("/api/tools/decl", decl_put, methods=["PUT"]),
        Route("/api/tools/decl/{file}", decl_delete, methods=["DELETE"]),
        Route("/api/tools/decl/{file}/test", decl_test, methods=["POST"]),
        Route("/api/packs", packs_get),
        Route("/api/packs/folder", packs_folder, methods=["PUT"]),
        Route("/api/packs/file/{name}", pack_file_get),
        Route("/api/packs/file/{name}", pack_file_put, methods=["PUT"]),
        Route("/api/packs/file/{name}", pack_file_delete, methods=["DELETE"]),
        Route("/api/packs/new", pack_new, methods=["POST"]),
        Route("/api/packs/upload", pack_upload, methods=["POST"]),
        Route("/api/packs/lint", pack_lint, methods=["POST"]),
        Route("/api/packs/persona", pack_persona, methods=["PUT"]),
        Route("/api/packs/about", pack_about, methods=["PUT"]),
        Route("/api/packs/vocab", pack_vocab, methods=["PUT"]),
        Route("/api/packs/try", pack_try, methods=["POST"]),
        Route("/api/memory", memory_get),
        Route("/api/memory/note/{line:int}", memory_note_delete,
              methods=["DELETE"]),
        Route("/api/memory/marker", memory_marker_delete, methods=["DELETE"]),
        Route("/api/memory/turns", memory_turns_delete, methods=["DELETE"]),
        Route("/api/about", about),
        Route("/api/transcript", transcript_save, methods=["POST"]),
        Route("/api/doc", doc_upload, methods=["POST"]),
    ]

    app = Starlette(middleware=[Middleware(Revalidate)], routes=[
        Route("/", index),
        *api,
        WebSocketRoute("/ws", ws),
        Mount("/static", app=StaticFiles(directory=WEB), name="static"),
    ], lifespan=lifespan)

    app.state.studio = s
    return app
