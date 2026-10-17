// The shell: sidebar, status, router, command palette, theme.
//
// Chat is mounted once and never unmounted -- its scroll position, draft and
// open cards survive every trip to another page. The other pages load on
// first visit (their modules are fetched in the background right after the
// first paint, so the first visit does not wait on the network either) and
// then stay mounted, hidden, so a half-edited form is still half-edited when
// you come back.

import { useEffect, useLayoutEffect, useRef, useState } from "preact/hooks";
import { signal } from "@preact/signals";
import { html, render, Icon, Toasts, Modals, api, toast, navOpen, confirmDialog } from "./lib.js";
import { connect, conn, link, status, info, busy, boot, send } from "./store.js";
import { ChatPage, focusComposer, machinery } from "./chat.js";

const PAGES = [
  { id: "chat", title: "Chat", icon: "chat" },
  { id: "packs", title: "Packs", icon: "pack", load: () => import("./pages/packs.js") },
  { id: "memory", title: "Memory", icon: "book", load: () => import("./pages/memory.js") },
  { id: "tools", title: "Tools", icon: "wrench", load: () => import("./pages/tools.js") },
  { id: "settings", title: "Settings", icon: "sliders", load: () => import("./pages/settings.js") },
  { id: "server", title: "Server", icon: "server", load: () => import("./pages/server.js") },
  { id: "about", title: "About him", icon: "info", load: () => import("./pages/about.js") },
];
const MAIN_NAV = PAGES.slice(0, 7);

const fromHash = () => {
  const id = location.hash.replace(/^#\/?/, "");
  return PAGES.some(p => p.id === id) ? id : "chat";
};
export const route = signal(fromHash());
const loaded = signal({});           // id -> page component, once fetched
const visited = signal(new Set([route.value]));

export function go(id) {
  if (!PAGES.some(p => p.id === id)) return;
  navOpen.value = false;
  if (route.value === id) return;
  history.replaceState(null, "", `#/${id}`);
  route.value = id;
  visited.value = new Set([...visited.value, id]);
  ensure(id);
  if (id === "chat") setTimeout(focusComposer, 30);
}
window.addEventListener("hashchange", () => go(fromHash()));

async function ensure(id) {
  const page = PAGES.find(p => p.id === id);
  if (!page || !page.load || loaded.value[id]) return;
  let comp;
  try { comp = (await page.load()).default; }
  catch (e) {
    // A browser remembers a failed module fetch for the life of the document
    // (the studio restarting mid-load, say), so the way back is a reload.
    comp = () => html`<div class="body"><div class="content"><div class="notice bad"><${Icon} n="alert" />
      <div class="grow">This page did not load (${e.message}).</div>
      <button class="btn" onClick=${() => location.reload()}>Reload</button></div></div></div>`;
  }
  loaded.value = { ...loaded.value, [id]: comp };
}

// ------------------------------------------------------------------ theme --
const media = matchMedia("(prefers-color-scheme: dark)");
const theme = signal(document.documentElement.dataset.theme || "");
const effective = () => theme.value || (media.matches ? "dark" : "light");
media.addEventListener("change", () => { theme.value = theme.peek(); });

function toggleTheme(e) {
  const next = effective() === "dark" ? "light" : "dark";
  const apply = () => {
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("cj.theme", next); } catch (err) { /* none */ }
    theme.value = next;
  };
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!document.startViewTransition || reduced) { apply(); return; }
  // A circle of the new theme grows from wherever the click was.
  const x = e && e.clientX ? e.clientX : innerWidth / 2;
  const y = e && e.clientY ? e.clientY : innerHeight / 2;
  const r = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
  const vt = document.startViewTransition(apply);
  vt.ready.then(() => document.documentElement.animate(
    { clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${r}px at ${x}px ${y}px)`] },
    { duration: 460, easing: "cubic-bezier(.2,.8,.2,1)", pseudoElement: "::view-transition-new(root)" }));
}

// ------------------------------------------------------- restart, quit ----
async function restartHim() {
  try { const o = await api("/api/server/restart", { method: "POST" }); toast(o.note, o.warn ? "warn" : "ok"); }
  catch (e) { toast(e.message, "bad", 6000); }
}

export const closed = signal(false);
export async function quitStudio() {
  const ok = await confirmDialog({ title: "Quit the studio?", ok: "Quit", danger: true,
    body: "The studio closes and stops him with it. Your conversation is kept for next time." });
  if (!ok) return;
  try { await api("/api/quit", { method: "POST" }); closed.value = true; }
  catch (e) { toast(e.message, "bad", 6000); }
}

// A saved change the running server has not read -- settings, packs, tools
// or the book. It stays until he restarts, because a toast is too easy to
// miss and a change that silently did not apply is the worst kind.
function PendingBar() {
  if (!status.value.pending || !link.value) return null;
  return html`<div class="pending-bar" role="status">
    <div class="row"><${Icon} n="refresh" cls="sm" /><b>Restart to apply</b></div>
    <div class="small">Saved changes wait until he restarts.</div>
    <button class="btn sm primary" onClick=${restartHim}>Restart him now</button>
  </div>`;
}

// ---------------------------------------------------------------- sidebar --
function Nav({ items }) {
  const ref = useRef();
  const [pill, setPill] = useState(null);
  const active = route.value;
  useLayoutEffect(() => {
    const el = ref.current && ref.current.querySelector("a.on");
    setPill(el ? el.offsetTop : null);
  }, [active]);
  return html`<nav class="nav" ref=${ref}>
    <div class="nav-pill" style=${pill === null ? "opacity:0" : `transform:translateY(${pill}px)`}></div>
    ${items.map((p) => html`<a key=${p.id} href=${`#/${p.id}`} class=${active === p.id ? "on" : ""}
        aria-current=${active === p.id ? "page" : null}
        onClick=${(e) => { e.preventDefault(); go(p.id); }}
        onMouseEnter=${() => ensure(p.id)}>
      <${Icon} n=${p.icon} />${p.title}<span class="kbd">Alt ${PAGES.indexOf(p) + 1}</span></a>`)}
  </nav>`;
}

function shortName(ckpt) {
  if (!ckpt) return "";
  const parts = String(ckpt).split(/[\\/]/);
  return (parts.length > 1 ? parts[parts.length - 2] : parts[0]).replace(/^corn_jr_/, "");
}

function StatusCard() {
  const st = status.value;
  const i = info.value;
  let dot = "", label = "Stopped", sub = st.why || "Start him from the Server page";
  if (conn.value !== "open") {
    dot = "bad pulse"; label = "Studio offline"; sub = "reconnecting to the studio...";
  } else if (st.state === "up" && link.value) {
    dot = busy.value ? "ok pulse" : "ok";
    label = busy.value ? "Replying" : "Online";
    sub = i ? `${shortName(i.ckpt)} · ${(i.params / 1e6).toFixed(0)}M` : "connected";
  } else if (st.state === "up") {
    dot = "warn pulse"; label = "Connecting"; sub = st.why || "the server answers; opening the sitting";
  } else if (st.state === "starting") {
    dot = "warn pulse"; label = "Starting"; sub = st.why || "loading the checkpoint";
  } else if (st.state === "crashed") {
    dot = "bad"; label = "Crashed"; sub = "open Server for the console";
  } else if (link.value) {
    dot = "ok"; label = "Online"; sub = i ? shortName(i.ckpt) : "attached";
  }
  return html`<button class="status" onClick=${() => go("server")} title=${st.why || label}>
    <div class="row"><span class=${`dot ${dot}`}></span><b>${label}</b>
      ${i && i.device ? html`<span class="grow"></span><span class="muted">${String(i.device).toUpperCase()}</span>` : null}</div>
    <div class="sub">${sub}</div>
  </button>`;
}

function Side() {
  return html`<aside class="side">
    <div class="brand"><div class=${`mark ${busy.value ? "live" : ""}`}>CJ</div><div><b>Corn-Jr</b><span>Studio</span></div></div>
    <${Nav} items=${MAIN_NAV} />
    <div class="side-fill"></div>
    <${Nav} items=${[PAGES[7]]} />
    <nav class="nav"><a onClick=${toggleTheme} role="button">
      <${Icon} n=${effective() === "dark" ? "sun" : "moon"} />${effective() === "dark" ? "Light mode" : "Dark mode"}</a></nav>
    <${PendingBar} />
    <${StatusCard} />
  </aside>`;
}

// ---------------------------------------------------------- the palette ----
const paletteOpen = signal(false);

function actions() {
  return [
    ...PAGES.map(p => ({ label: `Go to ${p.title}`, icon: p.icon, kind: "page", run: () => go(p.id) })),
    { label: "New conversation", icon: "reset", kind: "action", run: () => { send("reset"); go("chat"); } },
    { label: "Save the transcript", icon: "save", kind: "action",
      run: () => api("/api/transcript", { method: "POST" }).then(o => toast(`Saved to ${o.name}`)).catch(e => toast(e.message, "bad")) },
    { label: "Restart him", icon: "refresh", kind: "action", run: restartHim },
    { label: "Quit the studio", icon: "quit", kind: "action", run: quitStudio },
    { label: machinery.value ? "Hide the machinery" : "Show the machinery", icon: "eye", kind: "toggle",
      run: () => { machinery.value = !machinery.value; } },
    { label: effective() === "dark" ? "Light mode" : "Dark mode", icon: effective() === "dark" ? "sun" : "moon",
      kind: "toggle", run: () => toggleTheme() },
  ];
}

function score(label, q) {
  if (!q) return 1;
  const l = label.toLowerCase();
  if (l.includes(q)) return 2 + (l.startsWith(q) ? 1 : 0);
  let i = 0;
  for (const c of l) if (c === q[i]) i++;
  return i === q.length ? 1 : 0;
}

function Palette() {
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(0);
  const [closing, setClosing] = useState(false);
  const input = useRef();
  useEffect(() => { input.current && input.current.focus(); }, []);
  const list = actions().map(a => [a, score(a.label, q.trim().toLowerCase())])
    .filter(([, s]) => s > 0).sort((a, b) => b[1] - a[1]).map(([a]) => a);
  const close = () => { setClosing(true); setTimeout(() => { paletteOpen.value = false; }, 160); };
  const run = (a) => { close(); setTimeout(() => a.run(), 0); };
  const onKey = (e) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setSel(s => Math.min(s + 1, list.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setSel(s => Math.max(s - 1, 0)); }
    else if (e.key === "Enter" && list[sel]) { e.preventDefault(); run(list[sel]); }
    else if (e.key === "Escape") { e.preventDefault(); close(); }
  };
  return html`<div class=${`scrim ${closing ? "closing" : ""}`} onMouseDown=${e => e.target === e.currentTarget && close()}>
    <div class="palette" role="dialog" aria-label="Command palette">
      <input ref=${input} placeholder="Jump to a page or run an action..." value=${q}
        onInput=${e => { setQ(e.currentTarget.value); setSel(0); }} onKeyDown=${onKey} />
      <ul>${list.length ? list.map((a, i) => html`<li class=${i === sel ? "on" : ""} onMouseMove=${() => setSel(i)}
          onClick=${() => run(a)}><${Icon} n=${a.icon} cls="sm" />${a.label}<span class="kind">${a.kind}</span></li>`)
        : html`<li class="muted">Nothing matches</li>`}</ul>
    </div>
  </div>`;
}

// ------------------------------------------------------------------- app ---
function PageSlot({ id }) {
  const Comp = loaded.value[id];
  const shown = route.value === id;
  return html`<div class=${`page ${shown ? "enter" : ""}`} hidden=${!shown}>
    ${Comp ? html`<${Comp} shown=${shown} />` : html`<div class="body"><div class="content">
      <div class="skeleton" style="width:30%;height:22px;margin-top:20px"></div>
      <div class="skeleton" style="width:80%"></div><div class="skeleton" style="width:65%"></div></div></div>`}
  </div>`;
}

function App() {
  const active = route.value;
  return html`<div class=${`app ${navOpen.value ? "nav-open" : ""}`}>
    <${Side} />
    <main class="main" onClick=${(e) => { if (navOpen.value && !e.target.closest(".menu-btn")) navOpen.value = false; }}>
      <div class=${`page ${active === "chat" ? "enter" : ""}`} hidden=${active !== "chat"}><${ChatPage} /></div>
      ${PAGES.filter(p => p.id !== "chat" && visited.value.has(p.id)).map(p => html`<${PageSlot} key=${p.id} id=${p.id} />`)}
    </main>
    ${paletteOpen.value ? html`<${Palette} />` : null}
    ${closed.value ? html`<div class="scrim closed-screen"><div class="empty-chat">
      <div class="mark">CJ</div><h2>The studio is closed</h2>
      <p>Your conversation is kept. Start it again from the shortcut, then reload this window.</p>
      <button class="btn" onClick=${() => location.reload()}><${Icon} n="refresh" cls="sm" />Reload</button></div></div>` : null}
    <${Modals} /><${Toasts} />
  </div>`;
}

// ------------------------------------------------------------------- keys --
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault(); paletteOpen.value = !paletteOpen.value; return;
  }
  if (e.altKey && /^[1-8]$/.test(e.key)) { e.preventDefault(); go(PAGES[Number(e.key) - 1].id); return; }
  const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement && document.activeElement.tagName);
  if (e.key === "/" && !typing && route.value === "chat") { e.preventDefault(); focusComposer(); }
});

// ------------------------------------------------------------------- boot --
connect();
api("/api/boot").then(b => { boot.value = b; }).catch(() => {});
render(html`<${App} />`, document.getElementById("app"));
ensure(route.value);
// Fetch every other page's module once the first paint is done, so no page
// waits on the network the first time it is opened.
(window.requestIdleCallback || ((f) => setTimeout(f, 300)))(() => PAGES.forEach(p => p.load && p.load()));
if (route.value === "chat") setTimeout(focusComposer, 50);
