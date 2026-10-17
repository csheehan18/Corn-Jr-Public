// Tools: what he is offered, and the folder that extends it.
//
// The built-in switches write `tools` (all on is the empty list, which is
// what every caller before the subset meant) and take effect on a restart --
// he is told his tool set once, at load. `decline` stands apart because it is
// a measurement control, not a member of the set. The custom section is a
// live view of the declarations folder through the server's own loader, and
// Test run executes a declaration's command for real.

import { useEffect, useState } from "preact/hooks";
import { html, Icon, api, attempt, toast, useResource, Switch, Collapse, Page, Skeleton, AsyncButton,
  openModal, jsonHtml, undoable, useHidden } from "../lib.js";
import { SaveBar } from "./settings.js";

function DeclEditor({ decl, latencies, close, onSaved }) {
  const raw = (decl && decl.raw) || {};
  const [f, setF] = useState({
    name: raw.name || "", summary: raw.summary || "", latency: raw.latency || "slow",
    params: (raw.params || []).map(p => p.name + (p.required === false ? "?" : "")).join("\n"),
    command: (raw.command || []).join("\n"), gated: raw.gated !== false, timeout_s: raw.timeout_s ?? 30,
  });
  const [problem, setProblem] = useState("");
  const set = (k) => (e) => setF({ ...f, [k]: e && e.currentTarget ? e.currentTarget.value : e });
  const save = async () => {
    const obj = {
      name: f.name.trim(), summary: f.summary.trim(), latency: f.latency,
      params: f.params.split("\n").map(l => l.trim()).filter(Boolean).map(l => l.endsWith("?")
        ? { name: l.slice(0, -1), required: false } : { name: l }),
      command: f.command.split("\n").filter(Boolean), gated: !!f.gated, timeout_s: Number(f.timeout_s) || 30,
    };
    try {
      const out = await api("/api/tools/decl", { method: "PUT", body: { decl: obj, file: decl ? decl.file : null } });
      if (out.problem) { setProblem(out.problem); return; }
      toast(`Wrote ${out.file} -- restart him to offer it`);
      close(true); onSaved();
    } catch (e) { setProblem(e.message); }
  };
  return html`
    <div class="modal-head"><${Icon} n="wrench" /><h2>${decl ? `Edit ${decl.name}` : "Add a tool"}</h2></div>
    <div class="modal-body stack">
      <div class="small muted">A declaration file, not a code change: the summary is the whole of what he knows about it.</div>
      <div class="row wrap">
        <div class="grow"><label class="lbl">Name</label><input class="input mono" value=${f.name} onInput=${set("name")} placeholder="lowercase_snake_case" /></div>
        <div style="width:150px"><label class="lbl">Latency</label>
          <select class="select" value=${f.latency} onChange=${set("latency")}>${latencies.map(l => html`<option>${l}</option>`)}</select></div>
        <div style="width:110px"><label class="lbl">Timeout (s)</label><input class="input mono" type="number" value=${f.timeout_s} onInput=${set("timeout_s")} /></div>
      </div>
      <div><label class="lbl">Summary</label><input class="input" value=${f.summary} onInput=${set("summary")} /></div>
      <div class="row wrap" style="align-items:flex-start">
        <div class="grow"><label class="lbl">Params, one per line (name? for optional)</label>
          <textarea class="textarea mono" rows="4" value=${f.params} onInput=${set("params")}></textarea></div>
        <div class="grow"><label class="lbl">Command, one argument per line; {param} substitutes</label>
          <textarea class="textarea mono" rows="4" value=${f.command} onInput=${set("command")}></textarea></div>
      </div>
      <${Switch} on=${f.gated} onChange=${v => setF({ ...f, gated: v })} label="Ask before running (recommended)" />
      ${problem ? html`<div class="notice bad"><${Icon} n="alert" /><div class="mono small">${problem}</div></div>` : null}
    </div>
    <div class="modal-foot">
      <button class="btn" onClick=${() => close(false)}>Cancel</button>
      <${AsyncButton} cls="primary" onClick=${save}>Save<//>
    </div>`;
}

function DeclCard({ d, latencies, reload, remove }) {
  const [open, setOpen] = useState(false);
  const [args, setArgs] = useState({});
  const [result, setResult] = useState(null);
  const sig = `${d.name}(${d.params.map(p => p.name + (p.required ? "" : "?")).join(", ")})`;
  const run = async () => {
    const out = await attempt(() => api(`/api/tools/decl/${encodeURIComponent(d.file)}/test`, { method: "POST", body: { args } }));
    if (out) setResult(out);
  };
  const del = remove;
  const edit = () => openModal(close => html`<${DeclEditor} decl=${d} latencies=${latencies} close=${close} onSaved=${reload} />`, { size: "mid" });
  return html`<div class="card">
    <button class=${`acc-head ${open ? "open" : ""}`} onClick=${() => setOpen(!open)}>
      <${Icon} n="chev" cls=${`sm chev ${open ? "open" : ""}`} />
      <span class="grow"><span class="mono">${sig}</span><div class="small muted" style="font-weight:400">${d.summary}</div></span>
      <span class="badge">${d.latency}</span>
      <span class=${`badge ${d.gated ? "ok" : "accent"}`}>${d.gated ? "asks first" : "runs unasked"}</span>
    </button>
    <${Collapse} open=${open}>
      <div class="acc-body stack">
        <div class="small muted">Command</div>
        <div class="win-entry">${JSON.stringify(d.command)}</div>
        ${d.params.length ? html`<div class="row wrap">${d.params.map(p => html`<div class="grow" style="min-width:160px">
          <label class="lbl">${p.name}${p.required ? "" : " (optional)"}</label>
          <input class="input" value=${args[p.name] || ""} onInput=${e => setArgs({ ...args, [p.name]: e.currentTarget.value })} /></div>`)}</div>` : null}
        <div class="row">
          <${AsyncButton} icon="play" onClick=${run} title="runs the command for real, right now, with the arguments above">Test run<//>
          <button class="btn" onClick=${edit}><${Icon} n="edit" cls="sm" />Edit</button>
          <div class="grow"></div>
          <button class="btn danger" onClick=${del}><${Icon} n="trash" cls="sm" />Delete</button>
        </div>
        ${result ? html`<div class=${`notice ${result.ok ? "" : "bad"}`}><${Icon} n=${result.ok ? "check" : "alert"} />
          <div class="grow"><div>${result.verdict}</div>
          <pre class="mono small" style="margin:6px 0 0;white-space:pre-wrap" dangerouslySetInnerHTML=${{ __html: jsonHtml(result.payload) }}></pre></div></div>` : null}
      </div>
    <//>
  </div>`;
}

export default function Tools({ shown }) {
  const r = useResource("/api/tools");
  const [edits, setEdits] = useState({});
  const [folder, setFolder] = useState(null);
  const gone = useHidden();
  useEffect(() => { if (shown) r.reload(); }, [shown]);
  const d = r.data;
  if (!d) return html`<${Page} title="Tools"><${Skeleton} lines=${6} /><//>`;

  const on = (t) => (t.name in edits ? edits[t.name] : t.on);
  const decline = "decline" in edits ? edits.decline : d.decline;
  const dirty = d.builtin.filter(t => on(t) !== t.on).length + (decline !== d.decline ? 1 : 0);
  const save = async (restart) => {
    const enabled = d.builtin.filter(on).map(t => t.name);
    const out = await attempt(() => api("/api/tools", { method: "PUT", body: { enabled, decline, restart } }),
      o => restart ? (o.warn ? o.note : "Saved; he is restarting") : "Saved -- restart him to apply");
    if (out) { setEdits({}); r.reload(); }
  };
  const setDir = async (value) => {
    await attempt(() => api("/api/tools", { method: "PUT", body: { tools_dir: value } }), value ? `Using ${value}` : "No declarations folder");
    setFolder(null); r.reload();
  };
  const add = () => openModal(close => html`<${DeclEditor} decl=${null} latencies=${d.latency_classes} close=${close} onSaved=${r.reload} />`, { size: "mid" });
  const dir = folder ?? d.tools_dir;

  return html`<${Page} title="Tools" hint="changes take effect when he restarts">
    <div class="section-title">Built in</div>
    <div class="card divide">
      ${d.builtin.map(t => html`<div class="list-row" key=${t.name}>
        <div class="grow"><div class="t mono">${t.name}</div><div class="s">${t.summary}</div></div>
        <${Switch} on=${on(t)} onChange=${v => setEdits({ ...edits, [t.name]: v })} />
      </div>`)}
      <div class="list-row">
        <div class="grow"><div class="t">Offer “none of these”</div>
          <div class="s" style="white-space:normal">A measurement control, not a setting: without it he cannot say that no tool covers a request.</div></div>
        <${Switch} on=${decline} onChange=${v => setEdits({ ...edits, decline: v })} />
      </div>
    </div>

    <div class="section-title"><span class="grow">Your own tools</span>
      <button class="btn sm" onClick=${add}><${Icon} n="plus" cls="sm" />Add a tool</button></div>
    <div class="card card-pad stack">
      <div class="row">
        <input class="input mono grow" value=${dir} placeholder="tools.d -- empty means no declaration files load"
          onInput=${e => setFolder(e.currentTarget.value)} onKeyDown=${e => e.key === "Enter" && setDir(dir)} />
        ${folder !== null && folder !== d.tools_dir ? html`<button class="btn primary" onClick=${() => setDir(dir)}>Use folder</button>`
          : !d.tools_dir ? html`<button class="btn" onClick=${() => setDir("tools.d")}>Use tools.d/</button>` : null}
        <button class="btn icon" title="Reload" onClick=${r.reload}><${Icon} n="refresh" cls="sm" /></button>
      </div>
      ${d.warnings.map(w => html`<div class="lint bad">!! ${w}</div>`)}
      ${!d.tools_dir ? html`<div class="small muted">No folder configured.</div>`
        : !d.declarations.length ? html`<div class="small muted">No declarations yet -- add one, or drop .json files into the folder.</div>` : null}
    </div>
    ${d.declarations.filter(x => !gone.has(x.file)).map(x => html`<${DeclCard} key=${x.file} d=${x} latencies=${d.latency_classes}
      reload=${r.reload} remove=${() => undoable(`Deleted ${x.file}`, { hide: () => gone.hide(x.file), restore: () => gone.unhide(x.file),
        commit: async () => {
          await api(`/api/tools/decl/${encodeURIComponent(x.file)}`, { method: "DELETE", keepalive: true });
          await r.reload(); gone.unhide(x.file);
        } })} />`)}
    <${SaveBar} count=${dirty} onDiscard=${() => setEdits({})} onSave=${() => save(false)} onApply=${() => save(true)} />
  <//>`;
}
