// Packs: the owner's data folder, linted live and edited in place.
//
// Every listing is read through the loader the server uses, so what this page
// says a restart would load is what a restart would load. A table opens as a
// grid whose lint is the loader's own rules (the first column is the key, a
// repeated key keeps its first row, a blank key drops its row), checked as
// you type; a text file opens as text. "Try a question" runs the pack search
// in-process, so you can see which file would answer before restarting him.

import { useEffect, useRef, useState } from "preact/hooks";
import { html, Icon, api, attempt, toast, useResource, Switch, Collapse, Page, Skeleton, AsyncButton,
  openModal, confirmDialog, jsonHtml, fmtBytes, useDebounced, undoable, useHidden } from "../lib.js";

const enc = encodeURIComponent;
const KIND_ICON = { table: "table", prose: "text", empty: "file", dropped: "alert", ignored: "file" };

// ------------------------------------------------------------ table editor --
function TableEditor({ name, close, onSaved }) {
  const [header, setHeader] = useState(null);
  const [rows, setRows] = useState([]);
  const [lint, setLint] = useState({ blocking: [], warnings: [] });
  const [err, setErr] = useState("");
  const wrap = useRef();
  useEffect(() => {
    api(`/api/packs/file/${enc(name)}`).then(d => {
      setHeader(d.header); setRows(d.rows.length ? d.rows : [d.header.map(() => "")]);
      setLint({ blocking: d.blocking, warnings: d.warnings });
    }).catch(e => setErr(e.message));
  }, []);
  const relint = useDebounced((h, rs) => {
    api("/api/packs/lint", { method: "POST", body: { header: h, rows: rs.filter(r => r.some(c => c.trim())) } })
      .then(setLint).catch(() => {});
  }, 220);
  const update = (h, rs) => { setHeader(h); setRows(rs); setErr(""); relint(h, rs); };
  const cell = (i, j, v) => update(header, rows.map((r, k) => k === i ? r.map((c, m) => m === j ? v : c) : r));
  const head = (j, v) => update(header.map((c, m) => m === j ? v : c), rows);
  const addRow = () => {
    update(header, [...rows, header.map(() => "")]);
    setTimeout(() => { const el = wrap.current; el.scrollTop = el.scrollHeight;
      const ins = el.querySelectorAll("tbody tr:last-child input"); if (ins[0]) ins[0].focus(); }, 30);
  };
  const delRow = (i) => update(header, rows.filter((_, k) => k !== i));
  const addCol = () => update([...header, `Column ${header.length + 1}`], rows.map(r => [...r, ""]));
  const delCol = (j) => update(header.filter((_, m) => m !== j), rows.map(r => r.filter((_, m) => m !== j)));
  const onKey = (i, j) => (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (i === rows.length - 1) addRow();
      else setTimeout(() => { const r = wrap.current.querySelectorAll("tbody tr")[i + 1]; r && r.querySelectorAll("input")[j].focus(); }, 0);
    }
  };
  const save = async () => {
    try {
      const out = await api(`/api/packs/file/${enc(name)}`, { method: "PUT", body: { header, rows } });
      toast(`${out.note} -- restart him to use it`, out.warn ? "warn" : "ok");
      close(true); onSaved();
    } catch (e) { setErr(e.message); }
  };
  const seen = new Set();
  const dup = rows.map(r => { const k = (r[0] || "").trim().toLowerCase(); if (!k) return false;
    if (seen.has(k)) return true; seen.add(k); return false; });
  return html`
    <div class="modal-head"><${Icon} n="table" /><h2 class="grow">${name}</h2>
      <span class="small muted">${rows.length} row${rows.length === 1 ? "" : "s"} · ${header ? header.length : 0} columns</span></div>
    <div class="modal-body stack">
      <div class="small muted">The first column is the key -- what you name in a question ("charizard's speed" finds the row charizard, the column Speed). Enter moves down a row.</div>
      ${!header ? html`<div class="skeleton" style="height:180px"></div>` : html`
      <div class="grid-wrap scroll" ref=${wrap}><table class="grid">
        <thead><tr><th class="rownum">#</th>${header.map((c, j) => html`<th key=${j}><div class="row" style="gap:0">
          <input value=${c} onInput=${e => head(j, e.currentTarget.value)} aria-label=${`column ${j + 1} name`} />
          ${j > 0 && header.length > 2 ? html`<button class="btn ghost icon sm" title="Remove this column" onClick=${() => delCol(j)}><${Icon} n="x" cls="sm" /></button>` : null}
        </div></th>`)}
          <th class="rowx"><button class="btn ghost icon sm" title="Add a column" onClick=${addCol}><${Icon} n="plus" cls="sm" /></button></th></tr></thead>
        <tbody>${rows.map((r, i) => html`<tr key=${i} class=${dup[i] ? "dup" : ""} title=${dup[i] ? "a repeated key -- the loader keeps the first row" : ""}>
          <td class="rownum">${i + 1}</td>
          ${r.map((c, j) => html`<td key=${j}><input value=${c} onInput=${e => cell(i, j, e.currentTarget.value)} onKeyDown=${onKey(i, j)} /></td>`)}
          <td class="rowx"><button class="btn ghost icon sm" title="Delete this row" onClick=${() => delRow(i)}><${Icon} n="trash" cls="sm" /></button></td>
        </tr>`)}</tbody>
      </table></div>`}
      <div>
        ${lint.blocking.map(b => html`<div class="lint bad">!! ${b}</div>`)}
        ${lint.warnings.map(w => html`<div class="lint warn">!  ${w}</div>`)}
        ${err ? html`<div class="lint bad">!! ${err}</div>` : null}
        ${!lint.blocking.length && !lint.warnings.length && !err && header ? html`<div class="lint" style="color:var(--ok)">✓ the loader would take this as it is</div>` : null}
      </div>
    </div>
    <div class="modal-foot">
      <button class="btn" onClick=${addRow}><${Icon} n="plus" cls="sm" />Add row</button>
      <div class="grow"></div>
      <button class="btn" onClick=${() => close(false)}>Cancel</button>
      <${AsyncButton} cls="primary" disabled=${!header || lint.blocking.length > 0} onClick=${save}>Save<//>
    </div>`;
}

function TextEditor({ name, close, onSaved }) {
  const [text, setText] = useState(null);
  useEffect(() => { api(`/api/packs/file/${enc(name)}`).then(d => setText(d.text)).catch(e => toast(e.message, "bad")); }, []);
  const save = async () => {
    const out = await attempt(() => api(`/api/packs/file/${enc(name)}`, { method: "PUT", body: { text } }),
      o => `${o.note}${o.warn ? "" : " -- restart him to use it"}`);
    if (out) { close(true); onSaved(); }
  };
  return html`
    <div class="modal-head"><${Icon} n="text" /><h2>${name}</h2></div>
    <div class="modal-body stack">
      <div class="small muted">Prose is answered by paragraph, so keep one fact per paragraph. A <code>---</code> block at the top is configuration (a name, occasions, synonyms) and is never read out.</div>
      ${text === null ? html`<div class="skeleton" style="height:300px"></div>`
        : html`<textarea class="textarea mono" rows="20" value=${text} onInput=${e => setText(e.currentTarget.value)}></textarea>`}
    </div>
    <div class="modal-foot"><button class="btn" onClick=${() => close(false)}>Cancel</button>
      <${AsyncButton} cls="primary" disabled=${text === null} onClick=${save}>Save<//></div>`;
}

export function editPackFile(name, onSaved) {
  return /\.(csv|tsv)$/i.test(name)
    ? openModal(close => html`<${TableEditor} name=${name} close=${close} onSaved=${onSaved} />`, { size: "wide", dismiss: false })
    : openModal(close => html`<${TextEditor} name=${name} close=${close} onSaved=${onSaved} />`, { size: "mid", dismiss: false });
}

// ------------------------------------------------------------------ forms --
function PersonaForm({ p, reload }) {
  const [f, setF] = useState(p);
  useEffect(() => setF(p), [p]);
  const occ = (i, k, v) => setF({ ...f, on: f.on.map((o, j) => j === i ? { ...o, [k]: v } : o) });
  const save = async () => { await attempt(() => api("/api/packs/persona", { method: "PUT", body: f }), "Wrote persona.md -- restart him to use it"); reload(); };
  return html`<div class="acc-body stack" style="padding-left:18px">
    ${p.seeded ? html`<div class="small muted">Not written yet -- the form starts from examples/persona.md.</div>` : null}
    <div class="row wrap">
      <div class="grow"><label class="lbl">His name</label><input class="input" value=${f.name} onInput=${e => setF({ ...f, name: e.currentTarget.value })} /></div>
      <div style="width:180px"><label class="lbl">Birthday (YYYY-MM-DD)</label><input class="input mono" value=${f.birthday} onInput=${e => setF({ ...f, birthday: e.currentTarget.value })} /></div>
    </div>
    <div><label class="lbl">Occasions -- what he says on a day</label>
      <div class="stack" style="gap:6px">${f.on.map((o, i) => html`<div class="row" key=${i}>
        <input class="input mono" style="width:90px" placeholder="MM-DD" value=${o.when} onInput=${e => occ(i, "when", e.currentTarget.value)} />
        <input class="input grow" placeholder="what he says that day" value=${o.line} onInput=${e => occ(i, "line", e.currentTarget.value)} />
        <${Switch} on=${o.peppy} onChange=${v => occ(i, "peppy", v)} label="peppy" />
        <button class="btn ghost icon sm" onClick=${() => setF({ ...f, on: f.on.filter((_, j) => j !== i) })}><${Icon} n="x" cls="sm" /></button>
      </div>`)}
      <div><button class="btn sm" onClick=${() => setF({ ...f, on: [...f.on, { when: "", line: "", peppy: false }] })}><${Icon} n="plus" cls="sm" />Add an occasion</button></div></div></div>
    <div><label class="lbl">Who he says he is</label><textarea class="textarea" rows="6" value=${f.body} onInput=${e => setF({ ...f, body: e.currentTarget.value })}></textarea></div>
    <div><${AsyncButton} cls="primary" onClick=${save}>Save persona<//></div>
  </div>`;
}

function AboutForm({ body, reload }) {
  const [text, setText] = useState(body);
  useEffect(() => setText(body), [body]);
  const save = async () => { await attempt(() => api("/api/packs/about", { method: "PUT", body: { body: text } }), "Wrote about-me.md -- restart him to use it"); reload(); };
  return html`<div class="acc-body stack" style="padding-left:18px">
    <div class="small muted">Your facts, in prose -- he answers questions about you from this.</div>
    <textarea class="textarea" rows="7" value=${text} onInput=${e => setText(e.currentTarget.value)}></textarea>
    <div><${AsyncButton} cls="primary" onClick=${save}>Save about-me<//></div></div>`;
}

function VocabForm({ pairs, reload }) {
  const [list, setList] = useState(pairs);
  const [ask, setAsk] = useState("");
  const [col, setCol] = useState("");
  useEffect(() => setList(pairs), [pairs]);
  const write = async (next) => { await attempt(() => api("/api/packs/vocab", { method: "PUT", body: { pairs: next } }), "Saved vocab.md"); reload(); };
  return html`<div class="acc-body stack" style="padding-left:18px">
    <div class="small muted">An “ask” phrase counts toward whichever column header carries the column words -- the built-in tier already covers generic English.</div>
    ${list.length ? html`<div class="row wrap">${list.map(([a, c], i) => html`<span class="chip" key=${i}><span>“${a}”</span><${Icon} n="chev" cls="sm" /><b class="mono">${c}</b>
      <button class="btn ghost icon sm" style="width:20px;height:20px" onClick=${() => write(list.filter((_, j) => j !== i))}><${Icon} n="x" cls="sm" /></button></span>`)}</div>`
      : html`<div class="small muted">None yet.</div>`}
    <div class="row">
      <input class="input grow" placeholder="ask (as you say it)" value=${ask} onInput=${e => setAsk(e.currentTarget.value)} />
      <input class="input grow mono" placeholder="column header" value=${col} onInput=${e => setCol(e.currentTarget.value)} />
      <button class="btn" disabled=${!ask.trim() || !col.trim()} onClick=${() => { write([...list, [ask.trim(), col.trim()]]); setAsk(""); setCol(""); }}>Add</button>
    </div></div>`;
}

function Accordion({ title, sub, icon, children, open: start = false }) {
  const [open, setOpen] = useState(start);
  return html`<div class="card"><button class=${`acc-head ${open ? "open" : ""}`} onClick=${() => setOpen(!open)}>
    <${Icon} n="chev" cls=${`sm chev ${open ? "open" : ""}`} />${icon ? html`<${Icon} n=${icon} cls="sm" />` : null}
    <span class="grow">${title}</span>${sub ? html`<span class="small muted" style="font-weight:400">${sub}</span>` : null}</button>
    <${Collapse} open=${open}>${children}<//></div>`;
}

// ------------------------------------------------------------------- page --
function TryQuestion() {
  const [q, setQ] = useState("");
  const [out, setOut] = useState(null);
  const go = async () => { if (q.trim()) setOut(await attempt(() => api("/api/packs/try", { method: "POST", body: { q } }))); };
  return html`<div class="card card-pad stack">
    <div class="row"><input class="input grow" placeholder="a question your data should answer -- e.g. charmander's speed"
      value=${q} onInput=${e => setQ(e.currentTarget.value)} onKeyDown=${e => e.key === "Enter" && go()} />
      <${AsyncButton} icon="search" onClick=${go}>Try<//></div>
    ${out ? html`<div class=${`notice ${out.answered ? "" : "warn"} part`} key=${JSON.stringify(out)} style="animation:pop .3s var(--ease-spring) both">
      <${Icon} n=${out.answered ? "check" : "info"} /><div class="grow"><div>${out.verdict}</div>
      ${out.detail ? html`<pre class="mono small" style="margin:6px 0 0;white-space:pre-wrap" dangerouslySetInnerHTML=${{ __html: jsonHtml(out.detail) }}></pre>` : null}</div></div>` : null}
  </div>`;
}

export default function Packs({ shown }) {
  const r = useResource("/api/packs");
  const [folder, setFolder] = useState(null);
  const [newName, setNewName] = useState("");
  const [over, setOver] = useState(false);
  const pick = useRef();
  const gone = useHidden();
  useEffect(() => { if (shown) r.reload(); }, [shown]);
  const d = r.data;

  const setDir = async (value) => {
    await attempt(() => api("/api/packs/folder", { method: "PUT", body: { folder: value } }), value ? `Using ${value}` : "Packs switched off");
    setFolder(null); r.reload();
  };
  const upload = async (files) => {
    for (const file of files) {
      const raw = await file.arrayBuffer();
      try {
        let out = await api("/api/packs/upload", { method: "POST", raw, query: { name: file.name } });
        if (out.exists) {
          if (!await confirmDialog({ title: `Replace ${file.name}?`, body: "A file with that name is already in the folder.", ok: "Replace", danger: true })) continue;
          out = await api("/api/packs/upload", { method: "POST", raw, query: { name: file.name, replace: "1" } });
        }
        toast(`Added ${file.name}`);
      } catch (e) { toast(`${file.name}: ${e.message}`, "bad", 6000); }
    }
    r.reload();
  };
  const create = async () => {
    const out = await attempt(() => api("/api/packs/new", { method: "POST", body: { name: newName.trim() } }));
    if (out) { setNewName(""); r.reload(); editPackFile(out.name, r.reload); }
  };
  const del = (name) => undoable(`Deleted ${name}`, { hide: () => gone.hide(name), restore: () => gone.unhide(name),
    commit: async () => {
      await api(`/api/packs/file/${enc(name)}`, { method: "DELETE", keepalive: true });
      await r.reload(); gone.unhide(name);
    } });

  if (!d) return html`<${Page} title="Packs"><${Skeleton} lines=${7} /><//>`;
  const dir = folder ?? d.folder;
  return html`<${Page} title="Packs" hint="he reads them when he starts">
    <div class="lead">Your data: tables (.csv, .tsv) he looks things up in, and prose (.txt, .md) he answers from.</div>
    <div class="card card-pad row">
      <${Icon} n="pack" />
      <input class="input mono grow" value=${dir} placeholder="packs folder -- empty means none"
        onInput=${e => setFolder(e.currentTarget.value)} onKeyDown=${e => e.key === "Enter" && setDir(dir)} />
      ${folder !== null && folder !== d.folder ? html`<button class="btn primary" onClick=${() => setDir(dir)}>Use folder</button>`
        : !d.folder ? html`<button class="btn" onClick=${() => setDir("packs")}>Use packs/</button>` : null}
      <button class="btn icon" title="Reload" onClick=${r.reload}><${Icon} n="refresh" cls="sm" /></button>
    </div>

    ${d.folder ? html`
    <div class="section-title"><span class="grow">Files</span><span class="small muted" style="text-transform:none;letter-spacing:0">${d.files.length} in the folder</span></div>
    ${d.warnings.length ? html`<div class="notice warn" style="margin-bottom:10px"><${Icon} n="alert" /><div>${d.warnings.map(w => html`<div class="mono small">${w}</div>`)}</div></div>` : null}
    <div class="card divide">
      ${d.files.filter(f => !gone.has(f.name)).map(f => html`<div class="list-row" key=${f.name}>
        <div class=${`file-ico ${f.kind === "table" ? "table" : f.kind === "dropped" ? "bad" : ""}`}><${Icon} n=${KIND_ICON[f.kind] || "file"} /></div>
        <div class="grow" style="min-width:0"><div class="t">${f.name}</div><div class="s">${f.summary} · ${fmtBytes(f.size)}</div></div>
        <div class="acts">
          ${f.editable ? html`<button class="btn sm" onClick=${() => editPackFile(f.name, r.reload)}><${Icon} n="edit" cls="sm" />Edit</button>` : null}
          <button class="btn sm icon danger" title="Delete" onClick=${() => del(f.name)}><${Icon} n="trash" cls="sm" /></button>
        </div>
      </div>`)}
      <div style="padding:12px 14px" class="stack">
        <div class=${`upload-zone ${over ? "over" : ""}`} onClick=${() => pick.current.click()}
          onDragOver=${e => { e.preventDefault(); setOver(true); }} onDragLeave=${() => setOver(false)}
          onDrop=${e => { e.preventDefault(); setOver(false); upload([...e.dataTransfer.files]); }}>
          <${Icon} n="upload" /> <span>Drop .csv, .tsv, .txt or .md files here, or click to choose</span></div>
        <input type="file" multiple accept=".csv,.tsv,.txt,.md" hidden ref=${pick}
          onChange=${e => { const fs = [...e.currentTarget.files]; e.currentTarget.value = ""; upload(fs); }} />
        <div class="row"><input class="input grow mono" placeholder="new file, e.g. teams.csv or guide.md" value=${newName}
          onInput=${e => setNewName(e.currentTarget.value)} onKeyDown=${e => e.key === "Enter" && create()} />
          <button class="btn" disabled=${!newName.trim()} onClick=${create}><${Icon} n="plus" cls="sm" />New file</button></div>
      </div>
    </div>

    <div class="section-title">Try a question</div>
    <${TryQuestion} />

    <div class="section-title">Him, you, and your words</div>
    <${Accordion} title="Who he is" sub="persona.md" icon="spark"><${PersonaForm} p=${d.persona} reload=${r.reload} /><//>
    <${Accordion} title="Who you are" sub="about-me.md" icon="users"><${AboutForm} body=${d.about.body} reload=${r.reload} /><//>
    <${Accordion} title="Your words for your columns" sub="vocab.md" icon="text"><${VocabForm} pairs=${d.vocab} reload=${r.reload} /><//>
    ` : html`<div class="empty">No packs folder -- he has none of your data to answer from. Choose a folder above, or use packs/.</div>`}
  <//>`;
}
