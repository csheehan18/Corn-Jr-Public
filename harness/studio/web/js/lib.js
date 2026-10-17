// The studio's small toolkit: markup, icons, the API call, toasts, modals,
// and a cached loader. Everything a page needs that is not the page.

import { h, render } from "preact";
import { useEffect, useRef, useState } from "preact/hooks";
import { signal, effect } from "@preact/signals";
import htm from "htm";

export const html = htm.bind(h);
export { h, render };

// ------------------------------------------------------------------ icons --
// Paths transcribed from Lucide (ISC licence, see NOTICE), 24x24, stroked.
const P = {
  chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  pack: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7 12 12l8.7-5M12 22V12"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  book: '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/>',
  wrench: '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
  sliders: '<path d="M21 4h-7M10 4H3M21 12h-9M8 12H3M21 20h-5M12 20H3M14 2v4M8 10v4M16 18v4"/>',
  server: '<rect width="20" height="8" x="2" y="2" rx="2"/><rect width="20" height="8" x="2" y="14" rx="2"/><path d="M6 6h.01M6 18h.01"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
  moon: '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
  clip: '<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/>',
  up: '<path d="m5 12 7-7 7 7M12 19V5"/>',
  down: '<path d="M12 5v14M19 12l-7 7-7-7"/>',
  reset: '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/>',
  refresh: '<path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>',
  save: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5M12 15V3"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5M12 3v12"/>',
  chev: '<path d="m9 18 6-6-6-6"/>',
  cal: '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
  msg: '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
  phone: '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
  note: '<path d="M15.5 3H5a2 2 0 0 0-2 2v14c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2V8.5L15.5 3Z"/><path d="M15 3v6h6"/>',
  file: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M16 13H8M16 17H8"/>',
  table: '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/>',
  text: '<path d="M21 6H3M15 12H3M17 18H3"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  slash: '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
  spark: '<path d="M12 3l1.9 5.8L20 10.7l-5.8 1.9L12 18.5l-1.9-5.9L4 10.7l6.1-1.9z"/>',
  eye: '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
  plus: '<path d="M5 12h14M12 5v14"/>',
  trash: '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  alert: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/>',
  play: '<path d="M6 3l14 9-14 9z"/>',
  stop: '<rect width="14" height="14" x="5" y="5" rx="2"/>',
  layers: '<path d="m12 2 10 5-10 5L2 7Z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
  terminal: '<path d="m4 17 6-6-6-6M12 19h8"/>',
  cmd: '<path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  loader: '<path d="M21 12a9 9 0 1 1-6.22-8.56"/>',
  power: '<path d="M12 2v10M18.4 6.6a9 9 0 1 1-12.77.04"/>',
  copy: '<rect width="14" height="14" x="8" y="8" rx="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
  quit: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
};

export function Icon({ n, cls = "", ...rest }) {
  return h("svg", { class: `i ${cls}`, viewBox: "0 0 24 24", "aria-hidden": "true",
    dangerouslySetInnerHTML: { __html: P[n] || "" }, ...rest });
}

// -------------------------------------------------------------------- api --
export class ApiError extends Error {}

export async function api(path, { method = "GET", body, raw, query, keepalive } = {}) {
  let url = path;
  if (query) url += "?" + new URLSearchParams(query).toString();
  // keepalive lets a deferred delete finish when the window is closing.
  const init = { method, headers: {}, keepalive: !!keepalive };
  if (raw !== undefined) init.body = raw;
  else if (body !== undefined) {
    init.body = JSON.stringify(body);
    init.headers["Content-Type"] = "application/json";
  }
  let res;
  try { res = await fetch(url, init); }
  catch (e) { throw new ApiError("the studio is not answering"); }
  let data = null;
  try { data = await res.json(); } catch (e) { /* empty body */ }
  if (!res.ok) throw new ApiError((data && data.error) || `${res.status} ${res.statusText}`);
  return data || {};
}

// A page's data, cached across visits: the last answer renders at once and a
// fresh one replaces it when it lands, so returning to a page never shows a
// spinner for data it already had.
const cache = new Map();
export function useResource(path) {
  if (!cache.has(path)) cache.set(path, { data: signal(null), error: signal(null) });
  const entry = cache.get(path);
  const [, tick] = useState(0);
  const reload = async () => {
    try { entry.data.value = await api(path); entry.error.value = null; }
    catch (e) { entry.error.value = e.message; }
    tick(t => t + 1);
  };
  useEffect(() => { reload(); }, [path]);
  return { data: entry.data.value, error: entry.error.value, reload,
    set: (d) => { entry.data.value = d; tick(t => t + 1); } };
}

// ----------------------------------------------------------------- toasts --
export const toasts = signal([]);
let toastId = 0;
export function toast(text, tone = "ok", ms = 3600, action = null) {
  const id = ++toastId;
  toasts.value = [...toasts.value, { id, text, tone, action }];
  setTimeout(() => dismissToast(id), ms);
  return id;
}

// Delete now, on screen; on disk in a few seconds unless Undo is pressed.
// The page hides the row at once (`hide`), and puts it back on Undo
// (`restore`). A window closed inside the grace period still commits: the
// pending deletes run on pagehide, with keepalive fetches.
const pendingCommits = new Set();
const UNDO_MS = 6000;
export function undoable(text, { hide, restore, commit }) {
  let settled = false;
  const run = async () => {
    if (settled) return;
    settled = true;
    pendingCommits.delete(run);
    try { await commit(); } catch (e) { restore(); toast(e.message, "bad", 6000); }
  };
  hide();
  pendingCommits.add(run);
  const id = toast(text, "ok", UNDO_MS, { label: "Undo", run: () => {
    if (settled) return;
    settled = true;
    pendingCommits.delete(run);
    restore();
    dismissToast(id);
  } });
  setTimeout(run, UNDO_MS);
}
addEventListener("pagehide", () => { for (const run of [...pendingCommits]) run(); });
export function dismissToast(id) {
  const t = toasts.value.find(x => x.id === id);
  if (!t || t.out) return;
  toasts.value = toasts.value.map(x => x.id === id ? { ...x, out: true } : x);
  setTimeout(() => { toasts.value = toasts.value.filter(x => x.id !== id); }, 220);
}
export async function attempt(fn, ok) {
  try {
    const out = await fn();
    if (ok) toast(typeof ok === "function" ? ok(out) : ok, out && out.warn ? "warn" : "ok");
    return out;
  } catch (e) { toast(e.message, "bad", 6000); return undefined; }
}

export function Toasts() {
  const icon = { ok: "check", warn: "alert", bad: "alert" };
  return html`<div class="toasts" role="status" aria-live="polite">
    ${toasts.value.map(t => html`<div key=${t.id} class=${`toast ${t.tone} ${t.out ? "out" : ""}`}
        onClick=${() => !t.action && dismissToast(t.id)}>
      <${Icon} n=${t.action ? "trash" : icon[t.tone] || "info"} /><div class="grow">${t.text}</div>
      ${t.action ? html`<button class="btn sm" onClick=${(e) => { e.stopPropagation(); t.action.run(); }}>
        <${Icon} n="reset" cls="sm" />${t.action.label}</button>` : null}</div>`)}
  </div>`;
}

// ----------------------------------------------------------------- modals --
export const modals = signal([]);
let modalId = 0;
export function openModal(renderFn, { size = "", dismiss = true } = {}) {
  return new Promise(resolve => {
    const id = ++modalId;
    const close = (value) => {
      const m = modals.value.find(x => x.id === id);
      if (!m || m.closing) return;
      modals.value = modals.value.map(x => x.id === id ? { ...x, closing: true } : x);
      setTimeout(() => { modals.value = modals.value.filter(x => x.id !== id); resolve(value); }, 190);
    };
    modals.value = [...modals.value, { id, renderFn, close, size, dismiss }];
  });
}

function ModalHost({ m }) {
  const ref = useRef();
  useEffect(() => {
    const el = ref.current && ref.current.querySelector("[autofocus], input, textarea, select, button.primary");
    if (el) setTimeout(() => el.focus(), 30);
  }, []);
  return html`<div class=${`scrim ${m.closing ? "closing" : ""}`}
      onMouseDown=${e => { if (m.dismiss && e.target === e.currentTarget) m.close(undefined); }}>
    <div ref=${ref} class=${`modal ${m.size}`} role="dialog" aria-modal="true">${m.renderFn(m.close)}</div>
  </div>`;
}

export function Modals() {
  return html`${modals.value.map(m => html`<${ModalHost} key=${m.id} m=${m} />`)}`;
}

export function confirmDialog({ title, body = "", ok = "Confirm", danger = false }) {
  return openModal(close => html`
    <div class="modal-head"><h2>${title}</h2></div>
    <div class="modal-body"><p style="margin:4px 0 6px;color:var(--text-2)">${body}</p></div>
    <div class="modal-foot">
      <button class="btn" onClick=${() => close(false)}>Cancel</button>
      <button class=${`btn ${danger ? "danger solid" : "primary"}`} onClick=${() => close(true)}>${ok}</button>
    </div>`);
}

// ------------------------------------------------------------- components --
export function Switch({ on, onChange, label, disabled, title }) {
  return html`<button type="button" class=${`switch ${on ? "on" : ""}`} role="switch" aria-checked=${on}
      disabled=${disabled} title=${title} onClick=${() => onChange(!on)}>
    <span class="track"></span>${label ? html`<span>${label}</span>` : null}</button>`;
}

export function Button({ icon, children, cls = "", busy, ...rest }) {
  return html`<button class=${`btn ${cls}`} ...${rest}>
    ${busy ? html`<${Icon} n="loader" cls="sm spin" />` : icon ? html`<${Icon} n=${icon} cls="sm" />` : null}
    ${children}</button>`;
}

// A button whose click is async: it shows a spinner until the work lands.
export function AsyncButton({ onClick, children, ...rest }) {
  const [busy, setBusy] = useState(false);
  return html`<${Button} ...${rest} busy=${busy} disabled=${busy || rest.disabled}
    onClick=${async (e) => { setBusy(true); try { await onClick(e); } finally { setBusy(false); } }}>${children}<//>`;
}

export function Skeleton({ lines = 4 }) {
  return html`<div class="card card-pad">${Array.from({ length: lines }, (_, i) =>
    html`<div class="skeleton" style=${`width:${92 - (i * 17) % 40}%`}></div>`)}</div>`;
}

export function Collapse({ open, children }) {
  return html`<div class=${`collapse ${open ? "open" : ""}`}><div>${children}</div></div>`;
}

// The page header that gains a border once its body scrolls.
export function useScrolled() {
  const [scrolled, setScrolled] = useState(false);
  const onScroll = (e) => setScrolled(e.currentTarget.scrollTop > 4);
  return [scrolled, onScroll];
}

export function Page({ title, actions, children, wide = false, hint }) {
  const [scrolled, onScroll] = useScrolled();
  return html`
    <header class=${`top ${scrolled ? "scrolled" : ""}`}>
      <${MenuButton} /><h1>${title}</h1>${hint ? html`<span class="hint hide-narrow">${hint}</span>` : null}
      <div class="grow"></div>${actions}
    </header>
    <div class="body scroll" onScroll=${onScroll}>
      <div class=${`content ${wide ? "wide" : ""}`}>${children}</div>
    </div>`;
}

export const navOpen = signal(false);
export function MenuButton() {
  return html`<button class="btn ghost icon menu-btn" aria-label="Menu"
    onClick=${() => { navOpen.value = !navOpen.value; }}><${Icon} n="menu" /></button>`;
}

// ---------------------------------------------------------------- helpers --
const esc = (s) => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
export { esc };

// Pretty JSON with the keys, strings and numbers tinted. Escaped first.
export function jsonHtml(value) {
  const text = typeof value === "string" ? value : JSON.stringify(value, null, 2);
  return esc(text).replace(
    /(&quot;(?:[^&]|&(?!quot;))*?&quot;)(\s*:)?|\b(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)\b|\b(true|false|null)\b/g,
    (m, str, colon, num, lit) => {
      if (str) return colon ? `<span class="j-key">${str}</span>${colon}` : `<span class="j-str">${str}</span>`;
      if (num) return `<span class="j-num">${num}</span>`;
      return `<span class="j-num">${lit}</span>`;
    });
}

export function fmtMs(ms) {
  if (ms == null) return "";
  return ms < 1000 ? `${Math.round(ms)} ms` : `${(ms / 1000).toFixed(ms < 10000 ? 1 : 0)} s`;
}

export function fmtBytes(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / 1024 / 1024).toFixed(1)} MB`;
}

// A persisted signal: a per-viewer preference that survives a reload.
export function stored(key, initial) {
  let v = initial;
  try { const raw = localStorage.getItem(key); if (raw !== null) v = JSON.parse(raw); } catch (e) { /* none */ }
  const s = signal(v);
  effect(() => { try { localStorage.setItem(key, JSON.stringify(s.value)); } catch (e) { /* none */ } });
  return s;
}

// Run a DOM change inside a view transition when the browser has them.
export function transition(update, opts) {
  if (!document.startViewTransition || matchMedia("(prefers-reduced-motion: reduce)").matches) {
    update(); return null;
  }
  return document.startViewTransition(async () => { update(); await new Promise(r => setTimeout(r, 0)); });
}

// Rows deleted on screen and not yet on disk (see `undoable`).
export function useHidden() {
  const [set, setSet] = useState(() => new Set());
  return {
    has: (k) => set.has(k),
    hide: (k) => setSet(s => new Set([...s, k])),
    unhide: (k) => setSet(s => { const n = new Set(s); n.delete(k); return n; }),
  };
}

export function useDebounced(fn, ms) {
  const t = useRef();
  return (...args) => { clearTimeout(t.current); t.current = setTimeout(() => fn(...args), ms); };
}

// Read a dropped/picked file as bytes for a raw upload.
export function readFile(file) { return file.arrayBuffer(); }
