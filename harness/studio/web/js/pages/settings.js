// Settings: server.json as a form, generated from the dataclass.
//
// The server describes every field (configform.py): its kind, its help line
// (serverconfig.HELP verbatim), its released default and whether Restore
// defaults leaves it alone. Edits are held here until saved; a save is all
// or nothing on the server's side, so a typo never half-applies.

import { useEffect, useState } from "preact/hooks";
import { html, Icon, api, attempt, useResource, Switch, Collapse, Page, Skeleton, AsyncButton } from "../lib.js";

export function FieldControl({ f, value, onChange }) {
  if (f.kind === "bool") return html`<${Switch} on=${!!value} onChange=${onChange} />`;
  if (f.kind === "choice" && f.free) {
    const id = `dl-${f.name}`;
    return html`<span style="width:100%"><input class="input mono" list=${id} value=${value}
        onInput=${e => onChange(e.currentTarget.value)} />
      <datalist id=${id}>${f.choices.map(c => html`<option value=${c} />`)}</datalist></span>`;
  }
  if (f.kind === "choice") return html`<select class="select" value=${value} onChange=${e => onChange(e.currentTarget.value)}>
      ${f.choices.map(c => html`<option value=${c}>${c}</option>`)}</select>`;
  if (f.kind === "int" || f.kind === "float") return html`<input class="input mono" type="number"
      step=${f.kind === "int" ? 1 : "any"} value=${value}
      onInput=${e => onChange(e.currentTarget.value === "" ? "" : Number(e.currentTarget.value))} />`;
  if (f.kind === "list") return html`<input class="input mono" readonly value=${(value || []).join(", ")} />`;
  const mono = /[/\\.]/.test(String(f.default)) || /path|ckpt|log|notes|state|adapter|host/.test(f.name);
  return html`<input class=${`input ${mono ? "mono" : ""}`} value=${value} placeholder=${f.default === "" ? "(empty)" : ""}
      onInput=${e => onChange(e.currentTarget.value)} />`;
}

function Help({ text }) {
  const [open, setOpen] = useState(false);
  if (!text) return null;
  const long = text.length > 150;
  return html`<div class=${`help ${long && !open ? "clamp" : ""}`} title=${long && !open ? "click for the whole note" : ""}
    onClick=${() => long && setOpen(!open)}>${text}</div>`;
}

function FieldRow({ f, value, dirty, onChange }) {
  return html`<div class=${`field ${dirty ? "dirty" : ""}`}>
    <div><div class="name">${f.label}<code title="the key in server.json">${f.name}</code>${f.value !== f.default && !dirty ? html`<span class="badge" title=${`released default: ${JSON.stringify(f.default)}`}>changed</span>` : null}</div>
      <${Help} text=${f.help} /></div>
    <div class="ctl"><${FieldControl} f=${f} value=${value} onChange=${onChange} /></div>
  </div>`;
}

export function SaveBar({ count, onDiscard, onSave, onApply, what = "unsaved" }) {
  return html`<div class=${`savebar ${count ? "show" : ""}`} role="region" aria-label="Unsaved changes">
    <span class="what">${count} ${what} change${count === 1 ? "" : "s"}</span>
    <button class="btn" onClick=${onDiscard}>Discard</button>
    <${AsyncButton} onClick=${onSave}>Save<//>
    ${onApply ? html`<${AsyncButton} cls="primary" icon="refresh" onClick=${onApply}>Save & restart him<//>` : null}
  </div>`;
}

export default function Settings({ shown }) {
  const r = useResource("/api/config");
  const [edits, setEdits] = useState({});
  const [adv, setAdv] = useState(false);
  useEffect(() => { if (shown) r.reload(); }, [shown]);
  const d = r.data;

  const all = d ? [...d.sections.flatMap(s => s.fields), ...d.advanced.fields] : [];
  const base = Object.fromEntries(all.map(f => [f.name, f.value]));
  const dirtyNames = Object.keys(edits).filter(n => JSON.stringify(edits[n]) !== JSON.stringify(base[n]));
  const val = (f) => (f.name in edits ? edits[f.name] : f.value);
  const set = (name) => (v) => setEdits(e => ({ ...e, [name]: v }));

  const save = async (restart) => {
    const values = Object.fromEntries(dirtyNames.map(n => [n, edits[n]]));
    const out = await attempt(() => api("/api/config", { method: "PUT", body: { values, restart } }), o => o.note);
    if (out) { setEdits({}); await r.reload(); }
  };
  const restore = () => {
    const next = { ...edits };
    for (const [n, v] of Object.entries(d.restored)) if (JSON.stringify(v) !== JSON.stringify(base[n])) next[n] = v;
    setEdits(next);
  };

  return html`<${Page} title="Settings" hint=${d ? `${d.config} -- read when he starts` : ""}>
    ${!d ? html`<${Skeleton} lines=${6} />` : html`
      ${d.problem ? html`<div class="notice bad" style="margin-bottom:12px"><${Icon} n="alert" /><div>${d.config} could not be read and this form opened on defaults: ${d.problem}. Saving writes a good file over it.</div></div>` : null}
      ${d.sections.map(s => html`
        <div class="section-title">${s.title}</div>
        <div class="card divide">${s.fields.map(f => html`<${FieldRow} key=${f.name} f=${f} value=${val(f)}
          dirty=${dirtyNames.includes(f.name)} onChange=${set(f.name)} />`)}</div>`)}
      <div class="section-title"><span class="grow">Advanced</span>
        <button class="btn sm" onClick=${restore} title="The released settings, keeping your checkpoint, folders and address">
          <${Icon} n="reset" cls="sm" />Restore defaults</button></div>
      <div class="card">
        <button class=${`acc-head ${adv ? "open" : ""}`} onClick=${() => setAdv(!adv)}>
          <${Icon} n="chev" cls=${`sm chev ${adv ? "open" : ""}`} /><span class="grow">${d.advanced.title.replace(/^Advanced -- /, "")}</span>
          <span class="badge accent">${d.advanced.fields.length} knobs</span></button>
        <${Collapse} open=${adv}>
          <div class="notice warn" style="margin:0 14px 10px"><${Icon} n="alert" /><div>${d.advanced.note}</div></div>
          <div class="divide" style="border-top:1px solid var(--border)">${d.advanced.fields.map(f => html`<${FieldRow} key=${f.name} f=${f}
            value=${val(f)} dirty=${dirtyNames.includes(f.name)} onChange=${set(f.name)} />`)}</div>
        <//>
      </div>`}
    <${SaveBar} count=${dirtyNames.length} onDiscard=${() => setEdits({})} onSave=${() => save(false)} onApply=${() => save(true)} />
  <//>`;
}
