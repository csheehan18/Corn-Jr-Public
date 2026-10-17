// Server: the process, its console, and the three buttons.
//
// Nothing here changes what the server is -- Settings does that -- only
// whether it is running. A crash lands its traceback in the console, which
// polls once a second while this page is open and not at all otherwise.

import { useEffect, useRef, useState } from "preact/hooks";
import { html, Icon, api, attempt, Page, AsyncButton } from "../lib.js";
import { status, link, info } from "../store.js";
import { quitStudio } from "../main.js";

const STATES = {
  up: ["ok", "Running"], starting: ["warn pulse", "Starting"],
  stopped: ["", "Stopped"], crashed: ["bad", "Crashed"],
};

function Console({ lines }) {
  const ref = useRef();
  const pinned = useRef(true);
  useEffect(() => { const el = ref.current; if (el && pinned.current) el.scrollTop = el.scrollHeight; }, [lines]);
  return html`<div class="console scroll" ref=${ref}
      onScroll=${e => { const el = e.currentTarget; pinned.current = el.scrollHeight - el.scrollTop - el.clientHeight < 40; }}>
    ${lines.length ? lines.map((l, i) => html`<div key=${i} class=${/Traceback|Error|error:|exited/.test(l) ? "err"
      : /^\s*!!/.test(l) ? "warn" : /^\s*(~~|--|loading)/.test(l) ? "dim" : ""}>${l || " "}</div>`) : html`<span class="dim">(nothing printed yet)</span>`}
  </div>`;
}

export default function Server({ shown }) {
  const [d, setD] = useState(null);
  useEffect(() => {
    if (!shown) return undefined;
    let live = true;
    const tick = async () => {
      try { const x = await api("/api/server"); if (live) setD(x); } catch (e) { /* the shell shows offline */ }
    };
    tick();
    const t = setInterval(tick, 1000);
    return () => { live = false; clearInterval(t); };
  }, [shown]);

  const st = d ? d.state : status.value.state;
  const [dot, label] = STATES[st] || STATES.stopped;
  const act = (a) => attempt(() => api(`/api/server/${a}`, { method: "POST" }), o => o.note);
  const owned = d && !d.external && !d.no_server;
  const running = st === "up" || st === "starting";
  const i = info.value;

  return html`<${Page} title="Server" hint="the process this studio talks to"
      actions=${html`<button class="btn" onClick=${quitStudio} title="Close the studio and stop him"><${Icon} n="quit" cls="sm" />Quit studio</button>`}>
    <div class="card">
      <div class="state-hero">
        <span class=${`dot ${dot}`}></span>
        <div class="grow">
          <div class="big">${label}${st === "up" && !link.value ? " -- opening the sitting" : ""}</div>
          <div class="small muted mono ellipsis">${d ? `${d.addr}${d.pid ? `  ·  pid ${d.pid}` : ""}  ·  ${d.config}` : "..."}</div>
        </div>
        <div class="row">
          <${AsyncButton} icon="play" disabled=${!owned || running} onClick=${() => act("start")}>Start<//>
          <${AsyncButton} icon="stop" disabled=${!owned || !running} onClick=${() => act("stop")}>Stop<//>
          <${AsyncButton} icon="refresh" cls="primary" disabled=${!owned} onClick=${() => act("restart")}>Restart<//>
        </div>
      </div>
      ${d && (d.external || d.no_server) ? html`<div class="notice" style="margin:0 16px 14px">
        <${Icon} n="info" /><div>${d.no_server ? "The studio was started with --no-server: it talks to a server somebody else runs, and does not drive one."
          : "That server was not started by the studio; restart or stop it where it is running."}</div></div>` : null}
      ${d && d.pending ? html`<div class="notice warn" style="margin:0 16px 14px"><${Icon} n="refresh" />
        <div>A saved change -- settings, packs, tools or the book -- is waiting for a restart.</div></div>` : null}
      ${d && d.why && st !== "up" ? html`<div class="notice ${st === "crashed" ? "bad" : ""}" style="margin:0 16px 14px">
        <${Icon} n=${st === "crashed" ? "alert" : "info"} /><div class="mono small" style="white-space:pre-wrap">${d.why}</div></div>` : null}
    </div>
    ${i ? html`<div class="section-title">Loaded</div>
      <div class="card card-pad row wrap" style="gap:18px">
        <div><div class="small muted">Checkpoint</div><div class="mono small">${i.ckpt}</div></div>
        <div><div class="small muted">Parameters</div><div class="mono small">${Number(i.params || 0).toLocaleString()}</div></div>
        ${i.block_size ? html`<div><div class="small muted">Block</div><div class="mono small">${i.block_size}</div></div>` : null}
        <div><div class="small muted">Tools</div><div class="mono small">${(i.tools || []).length}</div></div>
        <div><div class="small muted">Recording</div><div class="mono small">${i.log || "off (--no-log)"}</div></div>
      </div>` : null}
    <div class="section-title"><span class="grow">Console</span><span class="small muted" style="text-transform:none;letter-spacing:0">newest at the bottom</span></div>
    <${Console} lines=${d ? d.tail : []} />
  <//>`;
}
