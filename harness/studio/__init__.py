"""A face for the protocol, and a hand on the server process.

The studio is the fourth client -- terminal, overlay, voice, and a web page --
and the first one that also *operates* the server: it spawns `python -m
harness.server --config server.json`, restarts it when the owner applies a
config change, and shows its console tail when it dies. Everything it says to
the model still goes over the one socket `harness/protocol.py` describes;
everything it changes about the instance goes through
`harness/serverconfig.py`'s file. It holds no behaviour of its own, on
`server.py`'s own rule about where behaviour lives.

**Three layers, split so a guard can reach each.** The page is static files
under `web/` -- Preact and htm vendored, no build step -- that draw
everything in the browser. `app.py` is the thin Starlette layer: one
WebSocket for the conversation, one JSON route per edit. Everything a route
decides lives in a framework-free module: `sitting` (the one conversation,
shared by every tab), `views` (each page's data and edits), `configform`
(`server.json` as a form), `mdlite` (the model card), and the older
`supervisor`, `transcript`, `packfiles`, `memoryfiles` and
`firstrun`. `scripts/check_studio.py` drives that half on a machine with no
web framework installed; `scripts/check_studio_pages.py` drives the web layer
in-process.

**The split is `harness/voice/`'s, for the same reason**, and the framework
is an **optional dependency on the voice client's terms**: nothing outside
`app.py` and `__main__.py` imports Starlette or uvicorn, `requirements.txt`
carries them commented out, and a person who never runs `python -m
harness.studio` never installs them.
"""
