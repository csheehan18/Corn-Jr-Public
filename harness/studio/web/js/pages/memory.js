// Memory: what he has written down on this machine, and the delete key.
//
// Notes, the schedule, the occasion marker, the structured turn log and the
// prose transcripts -- gitignored, personal, and readable here without
// knowing the file names. The edits offered are exactly the ones that are
// safe while he runs: he reads these files fresh each time. The schedule is
// read-only because the scheduler holds its entries in memory and would
// overwrite an outside edit.

import { useEffect } from "preact/hooks";
import { html, Icon, api, attempt, useResource, Page, Skeleton, confirmDialog, fmtBytes, undoable,
  useHidden } from "../lib.js";

const noteKey = (n) => JSON.stringify([n.date, n.title, n.text]);

export default function Memory({ shown }) {
  const r = useResource("/api/memory");
  const gone = useHidden();
  useEffect(() => { if (shown) r.reload(); }, [shown]);
  const d = r.data;
  if (!d) return html`<${Page} title="Memory"><${Skeleton} lines=${6} /><//>`;

  const delNote = (n) => {
    const k = noteKey(n);
    undoable("Note deleted", { hide: () => gone.hide(k), restore: () => gone.unhide(k),
      commit: async () => {
        // A note's line moves when another goes first, so it is found again
        // by what it says at the moment of deleting.
        const fresh = await api("/api/memory", { keepalive: true });
        const hit = fresh.notes.find(x => noteKey(x) === k);
        if (hit) await api(`/api/memory/note/${hit.line}`, { method: "DELETE", keepalive: true });
        await r.reload(); gone.unhide(k);
      } });
  };
  const forget = async () => { await attempt(() => api("/api/memory/marker", { method: "DELETE" }), "Forgotten -- he will mention today's occasion again"); r.reload(); };
  const clear = async () => {
    if (!await confirmDialog({ title: "Delete the turn log?", ok: "Delete", danger: true,
      body: `${d.turn_count} recorded turns are removed from disk. The prose transcripts are not touched.` })) return;
    await attempt(() => api("/api/memory/turns", { method: "DELETE" }), "Turn log cleared");
    r.reload();
  };

  return html`<${Page} title="Memory" hint="everything here stays on this machine"
      actions=${html`<button class="btn icon" title="Reload" onClick=${r.reload}><${Icon} n="refresh" cls="sm" /></button>`}>
    <div class="section-title"><span class="grow">Notes</span><span class="small muted" style="text-transform:none;letter-spacing:0">what save_note wrote and recall_day reads · ${d.notes_file}</span></div>
    <div class="card divide">
      ${d.notes.some(n => !gone.has(noteKey(n))) ? d.notes.filter(n => !gone.has(noteKey(n))).map(n => html`<div class="list-row" key=${noteKey(n)}>
        <div class="file-ico"><${Icon} n="note" /></div>
        <div class="grow" style="min-width:0"><div style="font-size:14px">${n.text}</div>
          <div class="s">${n.date}${n.title ? html` · <span class="badge">${n.title}</span>` : null}</div></div>
        <div class="acts"><button class="btn sm icon danger" title="Delete this note" onClick=${() => delNote(n)}><${Icon} n="trash" cls="sm" /></button></div>
      </div>`) : html`<div class="empty">Nothing written down yet.</div>`}
    </div>

    <div class="section-title">Occasions</div>
    <div class="card list-row">
      <div class="file-ico"><${Icon} n="spark" /></div>
      <div class="grow"><div style="font-size:14px">${d.marker ? `Last occasion mentioned: ${d.marker}` : "No occasion mentioned yet"}</div>
        <div class="s">so a birthday is said once a day</div></div>
      ${d.marker ? html`<button class="btn sm" onClick=${forget}>Forget</button>` : null}
    </div>

    <div class="section-title">Schedule</div>
    <div class="card">
      ${d.schedule.length ? html`<div class="divide">${d.schedule.map(s => html`<div class="list-row">
        <div class="file-ico"><${Icon} n="cal" /></div>
        <div class="grow"><div class="mono small">${s.at}</div><div style="font-size:14px">${s.action}${s.contact ? ` to ${s.contact}` : ""}: ${s.message}</div></div>
      </div>`)}</div>` : html`<div class="empty">Nothing scheduled.</div>`}
      <div class="small muted" style="padding:0 16px 12px">Read-only here: the server owns this file while it runs.</div>
    </div>

    <div class="section-title"><span class="grow">Turn log</span>
      ${d.turn_count ? html`<button class="btn sm danger" onClick=${clear}><${Icon} n="trash" cls="sm" />Clear</button>` : null}</div>
    <div class="card card-pad stack">
      <div class="small muted">${d.logging ? "" : "Not recording (--no-log). "}${d.turn_count} turn${d.turn_count === 1 ? "" : "s"} recorded in <span class="mono">${d.log_file}</span>.
        Your words exactly as typed, his calls, and what he said with who wrote it -- the most personal file the repo produces.</div>
      ${d.turns.length ? html`<div class="stack" style="gap:6px">${d.turns.map(t => html`<div class="win-entry">${t}</div>`)}</div>` : null}
    </div>

    <div class="section-title"><span class="grow">Saved transcripts</span><span class="small muted mono" style="text-transform:none;letter-spacing:0">${d.sessions_dir}/</span></div>
    <div class="card divide">
      ${d.sessions.length ? d.sessions.map(s => html`<div class="list-row"><div class="file-ico"><${Icon} n="file" /></div>
        <div class="grow mono small">${s.name}</div><span class="small muted">${fmtBytes(s.size)}</span></div>`)
        : html`<div class="empty">No saved transcripts. Chat's save button writes one.</div>`}
    </div>
  <//>`;
}
