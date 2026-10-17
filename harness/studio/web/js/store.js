// The conversation as the page holds it, and the socket that feeds it.
//
// The studio process owns the one connection to the server (sitting.py);
// this socket is the page's subscription to it. On connect the page is
// handed the sitting so far (`hello`) and rebuilds the thread from it with
// the same reducer that handles live events, so a reload and a live turn can
// never draw the same events two different ways.
//
// Streaming is cheap by construction: each run of reply text is its own
// signal bound straight to a text node, so a token updates one node and
// re-renders nothing. Tokens that land within one frame are applied
// together on the next animation frame.

import { signal, batch, effect } from "@preact/signals";

export const conn = signal("connecting");   // the page's socket to the studio
export const outbox = signal([]);           // turns typed while he was away
export const unseen = signal(0);            // replies that landed while you looked elsewhere
export const link = signal(false);          // the studio's socket to the server
export const busy = signal(false);
export const status = signal({ state: "stopped", why: "", pending: false });
export const info = signal(null);
export const doc = signal(null);
export const thread = signal([]);           // Turn | Note, oldest first
export const replaying = signal(false);     // true while a hello is drawn: no entry animations
export const windowView = signal(null);
export const boot = signal(null);           // /api/boot: setup card, config problem

let seq = 0;

export class Turn {
  constructor(user = null, at = null) {
    this.id = ++seq;
    this.user = user;
    this.at = at;
    this.parts = signal([]);
    this.live = signal(user !== null);
    this.done = signal(null);
    this.meta = signal({});
  }
  push(part) { part.id = ++seq; this.parts.value = [...this.parts.peek(), part]; return part; }
  last() { const p = this.parts.peek(); return p[p.length - 1]; }
}

function note(text, tone = "") { return { id: ++seq, note: true, text, tone }; }

function current() {
  const items = thread.peek();
  const last = items[items.length - 1];
  if (last && !last.note && (last.live.peek() || !last.done.peek())) return last;
  const t = new Turn();
  t.live.value = true;
  thread.value = [...items, t];
  return t;
}

// ---------------------------------------------------- text, frame-batched --
let pending = new Set();
let frame = 0;
function flushText() {
  frame = 0;
  batch(() => { for (const part of pending) { part.s.value += part.buf; part.buf = ""; } });
  pending = new Set();
}
function appendText(turn, text) {
  let part = turn.last();
  if (!part || part.kind !== "text") {
    // A reply's leading whitespace is the tokenizer's, not his; a run that
    // is only whitespace so far opens nothing, so the typing dots stay.
    text = text.replace(/^\s+/, "");
    if (!text) return;
    part = turn.push({ kind: "text", s: signal(""), buf: "" });
  }
  if (replaying.peek()) { part.s.value += text; return; }
  part.buf += text;
  pending.add(part);
  if (!frame) frame = requestAnimationFrame(flushText);
}

// ---------------------------------------------------------------- reducer --
export function apply(ev) {
  switch (ev.t) {
    case "user": {
      if (frame) { cancelAnimationFrame(frame); flushText(); }
      thread.value = [...thread.peek(), new Turn(ev.text, ev.at)];
      busy.value = true;
      return;
    }
    case "text": appendText(current(), ev.text); return;
    case "say": {
      const t = current();
      t.meta.value = { ...t.meta.peek(), author: ev.author, fell_back: ev.fell_back,
        state: ev.state, deferred: ev.deferred };
      if (ev.shown) {
        // The gate's question read back as the reply is already on the
        // confirm card; the words are kept (machinery shows them) but not
        // drawn twice.
        const words = (s) => String(s || "").toLowerCase().replace(/[^a-z0-9]/g, "");
        const echo = t.parts.peek().some(p => p.kind === "confirm" && words(p.question) === words(ev.text));
        t.push({ kind: "say", text: ev.text, deferred: !!ev.deferred, author: ev.author, echo });
      }
      return;
    }
    case "call": {
      const t = current();
      t.push({ kind: "tool", call: ev, obs: signal(null) });
      return;
    }
    case "obs": {
      const t = current();
      const parts = t.parts.peek();
      let tool = null;
      for (let i = parts.length - 1; i >= 0; i--) {
        if (parts[i].kind === "tool" && parts[i].obs.peek() === null) { tool = parts[i]; break; }
      }
      if (!tool) tool = t.push({ kind: "tool", call: null, obs: signal(null) });
      tool.obs.value = ev;
      const p = ev.payload;
      if (p && typeof p === "object" && p.reason === "confirm") {
        t.push({ kind: "confirm", question: p.clarify || "" });
        attention(`He's asking: ${p.clarify || "shall I?"}`, true);
      }
      return;
    }
    case "fold": {
      const t = current();
      t.meta.value = { ...t.meta.peek(), fold: ev };
      return;
    }
    case "rejected": current().push({ kind: "sys", tone: "bad", text: `not executed -- ${ev.why}` }); return;
    case "waiting": current().push({ kind: "sys", tone: "", text: "queued behind another turn" }); return;
    case "error": {
      const items = thread.peek();
      const last = items[items.length - 1];
      if (last && !last.note && last.live.peek()) {
        last.push({ kind: "sys", tone: "bad", text: ev.why });
        last.live.value = false;
      } else {
        thread.value = [...items, note(ev.why, "bad")];
      }
      busy.value = false;
      return;
    }
    case "done": {
      if (frame) { cancelAnimationFrame(frame); flushText(); }
      const t = current();
      for (const p of t.parts.peek()) if (p.kind === "text") p.s.value = p.s.peek().replace(/\s+$/, "");
      t.done.value = { ms: ev.ms, first_ms: ev.first_ms };
      t.live.value = false;
      busy.value = false;
      const words = t.parts.peek().filter(p => p.kind === "text" || (p.kind === "say" && !p.echo))
        .map(p => p.s ? p.s.peek() : p.text).join(" ").trim();
      attention(words || "He replied.", ev.ms > 4000);
      return;
    }
    case "note": {
      thread.value = [...thread.peek(), note(ev.text, ev.kind || "")];
      return;
    }
    case "doc": {
      doc.value = ev.doc || null;
      const text = ev.ok ? (ev.name ? `Answering lookups from ${ev.name} · ${ev.windows} windows`
        : "Document put away") : (ev.why || "the document did not load");
      thread.value = [...thread.peek(), note(text, ev.ok ? "" : "bad")];
      return;
    }
    case "reset": thread.value = []; busy.value = false; return;
    case "info": info.value = ev.info; doc.value = ev.doc || null; return;
    case "link": link.value = ev.up; if (!ev.up) busy.value = false; return;
    case "status": status.value = { state: ev.state, why: ev.why, pending: !!ev.pending }; return;
    case "window": windowView.value = ev; return;
    case "hello": {
      replaying.value = true;
      batch(() => {
        thread.value = [];
        link.value = ev.up;
        info.value = ev.info;
        doc.value = ev.doc || null;
        status.value = ev.status;
        for (const e of ev.log) apply(e);
        busy.value = ev.busy;
        const items = thread.peek();
        const last = items[items.length - 1];
        if (last && !last.note && !ev.busy) last.live.value = false;
      });
      requestAnimationFrame(() => requestAnimationFrame(() => { replaying.value = false; }));
      return;
    }
    default: return;
  }
}

// ----------------------------------------------------------------- socket --
let ws = null;
let backoff = 250;

export function connect() {
  const url = `${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`;
  ws = new WebSocket(url);
  conn.value = "connecting";
  ws.onopen = () => { conn.value = "open"; backoff = 250; };
  ws.onmessage = (m) => {
    const data = JSON.parse(m.data);
    if (Array.isArray(data)) batch(() => data.forEach(apply));
    else apply(data);
  };
  ws.onclose = () => {
    conn.value = "closed";
    link.value = false;
    setTimeout(connect, backoff);
    backoff = Math.min(backoff * 2, 3000);
  };
}

export function send(op, fields = {}) {
  if (!ws || ws.readyState !== 1) return false;
  ws.send(JSON.stringify({ op, ...fields }));
  return true;
}

// A turn typed while he is away waits here and goes the moment he is up --
// what the empty chat promises ("you can type now").
export function sendTurn(text) {
  askToNotify();
  if (link.peek() && send("turn", { user: text })) return "sent";
  outbox.value = [...outbox.peek(), { id: ++seq, text }];
  return "queued";
}
export function unqueue(id) { outbox.value = outbox.peek().filter(q => q.id !== id); }
effect(() => {
  if (!link.value || conn.value !== "open" || !outbox.peek().length) return;
  const waiting = outbox.peek();
  outbox.value = [];
  for (const q of waiting) send("turn", { user: q.text });
});

// --------------------------------------------- when you are looking away --
// The tab title counts replies you have not seen; a desktop notification
// says when he needs your yes, or when a slow turn finishes. Neither fires
// while the window has focus, and neither fires for a replayed sitting.
const away = () => document.hidden || !document.hasFocus();
function attention(text, notify) {
  if (replaying.peek() || !away()) return;
  unseen.value = unseen.peek() + 1;
  if (notify && "Notification" in window && Notification.permission === "granted") {
    const n = new Notification("Corn-Jr", { body: text.slice(0, 180), tag: "corn-jr", silent: false });
    n.onclick = () => { window.focus(); n.close(); };
  }
}
function askToNotify() {
  if ("Notification" in window && Notification.permission === "default") Notification.requestPermission();
}
const seen = () => { if (!away()) unseen.value = 0; };
addEventListener("focus", seen);
document.addEventListener("visibilitychange", seen);
effect(() => { document.title = unseen.value ? `(${unseen.value}) Corn-Jr Studio` : "Corn-Jr Studio"; });
