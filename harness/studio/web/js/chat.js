// The chat: the conversation, his tool calls as cards, the gate's question as
// buttons, and the composer.
//
// Every event the reference client prints gets a visual here and nothing is
// invented: text streams into the reply, a `say` renders when the studio says
// it differs from what streamed (`shown`, decided in sitting.py by the
// reference client's own rule), a call and its observation are one card, and
// fold / rejected / waiting / error are small lines. "Show the machinery"
// adds what a researcher wants and a friend does not: who wrote each reply,
// why the runtime covered for him, the fold, the grammar's masks, the reading.

import { useEffect, useRef, useState } from "preact/hooks";
import { html, Icon, api, toast, attempt, stored, fmtMs, jsonHtml, Switch, Collapse,
  MenuButton, AsyncButton } from "./lib.js";
import { thread, busy, link, doc, info, status, send, sendTurn, outbox, unqueue, replaying, windowView,
  boot } from "./store.js";

export const machinery = stored("cj.machinery", false);
export const draft = { value: "" };
const sentHistory = [];

// --------------------------------------------------------------- the tools --
const TOOLS = {
  place_call: { icon: "phone", say: () => html`Calling <b>you</b>` },
  send_text: { icon: "msg", say: (a) => a.message ? html`Texting you <b>“${a.message}”</b>` : html`Texting <b>you</b>` },
  save_note: { icon: "note", say: (a) => a.text ? html`Noting <b>“${a.text}”</b>` : html`Saving <b>a note</b>` },
  web_search: { icon: "search", say: (a) => a.query ? html`Searched <b>${a.query}</b>` : html`Searched <b>the web</b>` },
  resolve_date: { icon: "cal", say: (a) => a.expression || a.text ? html`Worked out <b>${a.expression || a.text}</b>` : html`Worked out <b>a date</b>` },
  recall_day: { icon: "cal", say: (a) => a.date ? html`Looked up <b>${day(a.date)}</b>` : html`Looked up <b>a day</b>` },
  decline: { icon: "slash", say: () => html`No tool <b>covers this</b>` },
  ask_agent: { icon: "spark", say: () => html`Asked <b>a larger agent</b>` },
};

function day(iso) {
  const d = new Date(`${iso}T12:00:00`);
  if (isNaN(d)) return iso;
  return d.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" });
}

function ToolCard({ part }) {
  const [open, setOpen] = useState(false);
  const call = part.call;
  const obs = part.obs.value;
  const name = (call && call.name) || (obs && obs.name) || "tool";
  const args = (call && call.arguments) || {};
  const spec = TOOLS[name] || { icon: "wrench", say: () => html`Used <b>${name}</b>` };
  const payload = obs && obs.payload;
  const held = payload && payload.reason === "confirm";
  // Red is for a call the schema refused or a tool that broke. A tool that
  // ran and found nothing (`no_results`) says so in its own words, calmly.
  const refused = call && call.ok === false;
  const broke = payload && payload.reason === "tool_error";
  const failed = refused || broke;
  const empty = payload && payload.ok === false && !held && !broke;
  const pending = !obs && !refused;
  const tag = held ? "waiting for you" : refused ? "did not run" : broke ? "failed"
    : empty ? String(payload.reason || "nothing found").replace(/_/g, " ") : pending ? "running" : name;
  const raw = call ? (typeof call.raw === "string" ? call.raw : JSON.stringify(call.raw)) : "";
  const showMach = machinery.value;
  return html`<div class=${`tool part ${failed ? "failed" : ""}`}>
    <button class=${`tool-head ${open ? "open" : ""}`} onClick=${() => setOpen(!open)} aria-expanded=${open}>
      <span class="ico">${pending ? html`<${Icon} n="loader" cls="spin" />` : html`<${Icon} n=${failed ? "alert" : spec.icon} />`}</span>
      <span class="what">${spec.say(args)}</span>
      <span class="tag">${tag}</span>
      <${Icon} n="chev" cls=${`sm chev ${open ? "open" : ""}`} />
    </button>
    <${Collapse} open=${open}>
      <div class="tool-body">${raw ? html`<span class="k">${"-> "}</span>${raw}` : null}${call && call.ok === false
        ? html`\n<span class="lbl2">!! ${call.why}</span>` : null}${showMach && call && call.masked
        ? html`\n<span class="lbl2">~~ grammar masked ${call.masked}${call.held && call.held.length ? ` (held ${call.held.join(", ")})` : ""}</span>` : null}${showMach && call && call.author
        ? html`\n<span class="lbl2">~~ written by the ${call.author}</span>` : null}${payload !== undefined && payload !== null
        ? html`\n<span class="k">${"<- "}</span><span dangerouslySetInnerHTML=${{ __html: jsonHtml(payload) }}></span>` : null}${obs && obs.read
        ? html`\n<span class="lbl2">read: ${obs.read}</span>` : null}</div>
    <//>
  </div>`;
}

function ConfirmCard({ part, active }) {
  const answer = (word) => sendTurn(word);
  return html`<div class=${`confirm part ${active ? "" : "stale"}`}>
    <div class="q">${part.question || "Shall I?"}</div>
    <div class="row acts">
      <button class="btn primary" onClick=${() => answer("yes")}><${Icon} n="check" cls="sm" />Yes</button>
      <button class="btn" onClick=${() => answer("no")}>No</button>
    </div>
  </div>`;
}

function Text({ part, caret }) {
  // The signal itself is the child: Preact binds it to one text node, so a
  // token never re-renders this component, let alone the turn.
  return html`<div class="reply part">${part.s}${caret ? html`<span class="caret" aria-hidden="true"></span>` : null}</div>`;
}

// ------------------------------------------------------- message actions --
function replyText(turn) {
  return turn.parts.peek().filter(p => p.kind === "text" || (p.kind === "say" && !p.echo))
    .map(p => (p.s ? p.s.peek() : p.text)).join("\n").trim();
}

async function copy(text) {
  try { await navigator.clipboard.writeText(text); }
  catch (e) {
    const ta = Object.assign(document.createElement("textarea"), { value: text });
    document.body.append(ta); ta.select(); document.execCommand("copy"); ta.remove();
  }
  toast("Copied");
}

// Put words in the composer as if typed: the composer's own input handler
// takes them, so its draft, height and send button all follow.
export function fillComposer(text) {
  const el = document.querySelector(".box textarea");
  if (!el) return;
  el.value = text;
  el.dispatchEvent(new Event("input", { bubbles: true }));
  el.focus();
  el.setSelectionRange(text.length, text.length);
}

function Act({ icon, label, onClick }) {
  return html`<button class="btn ghost sm icon" title=${label} aria-label=${label}
    onClick=${onClick}><${Icon} n=${icon} cls="sm" /></button>`;
}

function Meta({ turn, last }) {
  const d = turn.done.value;
  const m = turn.meta.value;
  const mach = machinery.value;
  if (!d && !mach) return null;
  const bits = [];
  if (d) {
    if (d.first_ms != null) bits.push(html`<span>${fmtMs(d.first_ms)} to first word</span>`);
    bits.push(html`<span>${fmtMs(d.ms)}</span>`);
  }
  return html`<div class="meta part">
    ${bits.map((b, i) => html`${i ? html`<span class="sep">·</span>` : null}${b}`)}
    ${mach && m.author ? html`<span class=${`badge ${m.author === "model" ? "" : "accent"}`}
        title="who composed the reply: the model, a runtime pool, or a tool payload">${m.author}</span>` : null}
    ${mach && m.fell_back ? html`<span class="badge bad" title="why his own attempt was refused">fell back: ${m.fell_back}</span>` : null}
    ${mach && m.state ? html`<span class="badge mono" title="the state record under the say">${m.state}</span>` : null}
    ${mach && m.fold ? html`<span class="badge mono" title="the utterance was normalised before he saw it">~~ ${m.fold.raw} -> ${m.fold.folded}</span>` : null}
    ${d ? html`<span class="msg-actions">
      <${Act} icon="copy" label="Copy his reply" onClick=${() => copy(replyText(turn))} />
      ${last && turn.user ? html`<${Act} icon="refresh" label="Ask again" onClick=${() => sendTurn(turn.user)} />` : null}
    </span>` : null}
  </div>`;
}

// One turn. Its parts, liveness and timing are its own signals, so a new card
// re-renders this turn and no other, and a token re-renders nothing (the text
// node is bound to the signal). A class with shouldComponentUpdate would
// block the signals' own re-render, so this stays a function.
function TurnView({ turn, last }) {
  const parts = turn.parts.value;
  const live = turn.live.value;
  // Whether words have started, read from the parts and never from a text
  // signal -- reading one here would re-render the turn on every token.
  const hasWords = parts.some(p => p.kind === "text" || p.kind === "say");
  const tail = parts[parts.length - 1];
  const showHim = live || parts.length || turn.done.value;
  return html`<div class="turn">
    ${turn.user !== null ? html`<div class="user-row">
      <span class="msg-actions">
        <${Act} icon="copy" label="Copy" onClick=${() => copy(turn.user)} />
        ${last ? html`<${Act} icon="edit" label="Edit and send again" onClick=${() => fillComposer(turn.user)} />` : null}
      </span>
      <div class="msg-user">${turn.user}</div></div>` : null}
    ${showHim ? html`<div class="msg-him">
      <div class=${`mark sm ${live ? "live" : ""}`}>CJ</div>
      <div class="body">
        ${parts.map(p => {
          if (p.kind === "text") return html`<${Text} key=${p.id} part=${p} caret=${live && p === tail} />`;
          if (p.kind === "say") return html`<div key=${p.id} class=${`reply part ${p.deferred ? "deferred" : ""} ${p.echo ? "echo" : ""}`}>${p.text}</div>`;
          if (p.kind === "tool") return html`<${ToolCard} key=${p.id} part=${p} />`;
          if (p.kind === "confirm") return html`<${ConfirmCard} key=${p.id} part=${p} active=${last && !live} />`;
          return html`<div key=${p.id} class=${`sys part ${p.tone}`}>${p.tone === "bad" ? "!!" : "··"} ${p.text}</div>`;
        })}
        ${live && !hasWords ? html`<div class="typing" aria-label="he is thinking"><i></i><i></i><i></i></div>` : null}
        <${Meta} turn=${turn} last=${last} />
      </div>
    </div>` : null}
  </div>`;
}

function Thread() {
  const items = thread.value;
  return html`<div class=${`thread ${replaying.value ? "" : "anim"} ${machinery.value ? "mach" : ""}`}>
    ${items.map((it, i) => it.note
      ? it.tone === "restart"
        ? html`<div key=${it.id} class="divider" role="separator"><span><${Icon} n="power" cls="sm" />${it.text}</span></div>`
        : html`<div key=${it.id} class=${`note-line ${it.tone === "bad" ? "sys bad" : ""}`}><${Icon} n=${it.tone === "bad" ? "alert" : "file"} cls="sm" />${it.text}</div>`
      : html`<${TurnView} key=${it.id} turn=${it} last=${i === items.length - 1} />`)}
  </div>`;
}

// ------------------------------------------------------------- empty state --
const SUGGEST = ["what's on tomorrow?", "remind me to call the dentist",
  "who wrote Frankenstein?", "save a note: buy oat milk", "text me to leave at half two"];

function Empty({ onPick }) {
  const name = info.value && info.value.ckpt ? String(info.value.ckpt).split(/[\\/]/).slice(-2, -1)[0] : "";
  return html`<div class="empty-chat">
    <div class="mark">CJ</div>
    <h2>What can he do for you?</h2>
    <p>${link.value ? `He's here${name ? ` -- ${name}` : ""}. Ask for something, or start from one of these.`
      : "He isn't connected yet. You can type now; it sends once he is up."}</p>
    <div class="suggest">${SUGGEST.map((s, i) => html`<button style=${`animation-delay:${80 + i * 45}ms`}
        onClick=${() => onPick(s)}>${s}</button>`)}</div>
  </div>`;
}

// ------------------------------------------------------------- setup card --
function SetupCard() {
  const b = boot.value;
  const [pick, setPick] = useState(null);
  if (!b || !b.setup) return null;
  const chosen = pick ?? (b.setup.checkpoints[0] || "");
  const go = () => attempt(async () => {
    const out = await api("/api/setup", { method: "POST", body: { ckpt: chosen } });
    boot.value = { ...b, setup: null };
    return out;
  }, (o) => o.note);
  return html`<div class="thread" style="padding-bottom:0"><div class="card card-pad stack part"
      style="border-color:var(--accent-line)">
    <div class="row"><${Icon} n="spark" /><b>Set this instance up</b></div>
    ${b.setup.reasons.map(r => html`<div class="small" style="color:var(--text-2)">· ${r}</div>`)}
    ${b.setup.checkpoints.length ? html`<div class="row wrap">
        <select class="select mono grow" value=${chosen} onChange=${e => setPick(e.currentTarget.value)}>
          ${b.setup.checkpoints.map(c => html`<option value=${c}>${c}</option>`)}</select>
        <${AsyncButton} cls="primary" onClick=${go}>Save ${b.config} and start<//>
      </div>
      <div class="small muted">Packs are switched on with the packs/ folder; the Packs page is where your data goes.</div>`
      : html`<div class="small">${b.setup.hint}</div>
        <div><button class="btn" onClick=${() => location.reload()}><${Icon} n="refresh" cls="sm" />Rescan</button></div>`}
  </div></div>`;
}

// ---------------------------------------------------------------- composer --
function Composer({ inputRef }) {
  const [text, setText] = useState(draft.value);
  const [hist, setHist] = useState(-1);
  const fileRef = useRef();
  const up = link.value;
  useEffect(() => { draft.value = text; size(); }, [text]);
  const size = () => {
    const el = inputRef.current;
    if (!el) return;
    el.style.height = "auto";
    const max = Math.round(innerHeight * 0.4);
    el.style.height = `${Math.min(el.scrollHeight + 1, max)}px`;
    el.style.overflowY = el.scrollHeight > max ? "auto" : "hidden";
  };
  const submit = () => {
    const t = text.trim();
    if (!t) return;
    // Sent now, or held until he is up -- either way it has left the box.
    sendTurn(t);
    sentHistory.push(t);
    setText(""); setHist(-1);
  };
  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); submit(); return; }
    if (e.key === "ArrowUp" && (!text || hist >= 0) && sentHistory.length) {
      e.preventDefault();
      const i = hist < 0 ? sentHistory.length - 1 : Math.max(0, hist - 1);
      setHist(i); setText(sentHistory[i]);
    } else if (e.key === "ArrowDown" && hist >= 0) {
      e.preventDefault();
      const i = hist + 1;
      if (i >= sentHistory.length) { setHist(-1); setText(""); } else { setHist(i); setText(sentHistory[i]); }
    } else if (e.key === "Escape") e.currentTarget.blur();
  };
  const d = doc.value;
  return html`<div class="composer-wrap"><div class="composer">
    ${d ? html`<span class="docchip" title="while loaded, lookups answer from the document and never leave the machine">
      <${Icon} n="file" cls="sm" />Answering lookups from <b>${d.name}</b> · ${d.windows} windows
      <button title="Put the document away" onClick=${() => send("doc", { path: "" })}><${Icon} n="x" cls="sm" /></button>
    </span>` : null}
    ${outbox.value.map(q => html`<span class="docchip queued" key=${q.id} title="it sends the moment he is up">
      <${Icon} n="loader" cls="sm spin" />Sends when he's up: <b>${q.text.length > 60 ? q.text.slice(0, 60) + "..." : q.text}</b>
      <button title="Don't send it" onClick=${() => unqueue(q.id)}><${Icon} n="x" cls="sm" /></button></span>`)}
    <div class=${`box ${up ? "" : "offline"}`}>
      <button class="btn ghost icon" title="Give him a document to answer from (.txt or .md)"
        onClick=${() => fileRef.current.click()}><${Icon} n="clip" /></button>
      <input ref=${fileRef} type="file" accept=".txt,.md" hidden
        onChange=${e => { const f = e.currentTarget.files[0]; e.currentTarget.value = ""; if (f) uploadDoc(f); }} />
      <textarea ref=${inputRef} rows="1" value=${text} aria-label="Message"
        placeholder=${up ? "Message Corn-Jr..." : "He isn't up yet -- type anyway, it sends when he is"}
        onInput=${e => { setText(e.currentTarget.value); setHist(-1); }} onKeyDown=${onKey}></textarea>
      <button class="send" title=${up ? "Send (Enter)" : "Send when he's up (Enter)"} disabled=${!text.trim()} onClick=${submit}>
        <${Icon} n="up" /></button>
    </div>
    <div class="hint-line hide-narrow"><span><kbd>Enter</kbd> send</span><span><kbd>Shift</kbd>+<kbd>Enter</kbd> new line</span>
      <span><kbd>↑</kbd> last message</span><span><kbd>Ctrl</kbd>+<kbd>K</kbd> jump anywhere</span>
      ${busy.value ? html`<span style="color:var(--accent)">he is replying...</span>` : null}</div>
  </div></div>`;
}

export async function uploadDoc(file) {
  if (!/\.(txt|md)$/i.test(file.name)) { toast("Only .txt and .md documents load", "warn"); return; }
  await attempt(async () => api("/api/doc", { method: "POST", raw: await file.arrayBuffer(),
    query: { name: file.name } }));
}

// ------------------------------------------------------- what he sees -----
function WindowDrawer({ open, onClose }) {
  useEffect(() => { if (open) send("window"); }, [open, thread.value.length]);
  const w = windowView.value;
  const used = w ? w.tokens.reduce((a, b) => a + b, 0) : 0;
  const frac = w && w.room ? Math.min(1, used / w.room) : 0;
  return html`<aside class=${`drawer ${open ? "open" : ""}`} aria-hidden=${!open}>
    <div class="card-head"><${Icon} n="layers" /><h3 class="grow">What he sees</h3>
      <button class="btn ghost icon sm" onClick=${() => send("window")} title="Refresh"><${Icon} n="refresh" cls="sm" /></button>
      <button class="btn ghost icon sm" onClick=${onClose} title="Close"><${Icon} n="x" cls="sm" /></button></div>
    <div class="scroll grow" style="padding:14px 16px">
      ${!w ? html`<div class="empty">Asking the server...</div>` : html`
        <div class="small muted" style="margin-bottom:6px">The history the last turn was shown, in his own tokens.</div>
        <div class="row small" style="margin-bottom:6px"><b>${used}</b><span class="muted">of ${w.room} tokens of room · block ${w.block_size}</span></div>
        <div class="meter"><i style=${`transform:scaleX(${frac})`}></i></div>
        <div class="stack" style="margin-top:14px">
          ${w.entries.length ? w.entries.map((e, i) => html`<div>
            <div class="small muted" style="margin:0 0 4px 2px">entry ${i + 1} · ${w.tokens[i]} tokens</div>
            <div class="win-entry">${e}</div></div>`) : html`<div class="empty">Nothing yet -- a fresh conversation.</div>`}
        </div>`}
    </div>
  </aside>`;
}

// --------------------------------------------------------------- the page --
export function ChatPage() {
  const scrollRef = useRef();
  const innerRef = useRef();
  const inputRef = useRef();
  const pinned = useRef(true);
  const [away, setAway] = useState(false);
  const [drag, setDrag] = useState(false);
  const [drawer, setDrawer] = useState(false);
  const dragDepth = useRef(0);

  // Stay at the bottom while the reply grows, unless the reader scrolled up.
  useEffect(() => {
    const el = scrollRef.current;
    const ro = new ResizeObserver(() => { if (pinned.current) el.scrollTop = el.scrollHeight; });
    ro.observe(innerRef.current);
    return () => ro.disconnect();
  }, []);
  // A turn this page (or another tab) just sent pulls the view down.
  const count = thread.value.length;
  useEffect(() => { pinned.current = true; const el = scrollRef.current; if (el) el.scrollTop = el.scrollHeight; }, [count]);

  const onScroll = () => {
    const el = scrollRef.current;
    const gap = el.scrollHeight - el.scrollTop - el.clientHeight;
    pinned.current = gap < 80;
    setAway(gap > 240);
  };
  const toBottom = () => {
    const el = scrollRef.current;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    pinned.current = true;
  };
  const pick = (s) => fillComposer(s);

  const hasFiles = (e) => e.dataTransfer && [...e.dataTransfer.types].includes("Files");
  const onDragEnter = (e) => { if (!hasFiles(e)) return; e.preventDefault(); dragDepth.current++; setDrag(true); };
  const onDragLeave = () => { dragDepth.current = Math.max(0, dragDepth.current - 1); if (!dragDepth.current) setDrag(false); };
  const onDrop = (e) => {
    if (!hasFiles(e)) return;
    e.preventDefault(); dragDepth.current = 0; setDrag(false);
    const f = e.dataTransfer.files[0];
    if (f) uploadDoc(f);
  };

  const b = boot.value;
  return html`<div class="page chat" onDragEnter=${onDragEnter} onDragOver=${e => hasFiles(e) && e.preventDefault()}
      onDragLeave=${onDragLeave} onDrop=${onDrop}>
    <header class="top">
      <${MenuButton} /><h1>Chat</h1>
      <div class="grow"></div>
      <span class="hide-narrow"><${Switch} on=${machinery.value} onChange=${v => { machinery.value = v; }}
        label="Show the machinery" title="who wrote each reply, folds, masks and readings" /></span>
      <button class="btn ghost icon" title="What he sees -- the history the last turn was shown"
        onClick=${() => setDrawer(!drawer)}><${Icon} n="layers" /></button>
      <button class="btn icon" title="Save the transcript to Saved Sessions/"
        onClick=${() => attempt(() => api("/api/transcript", { method: "POST" }), o => `Saved to ${o.name}`)}><${Icon} n="save" /></button>
      <button class="btn" title="He forgets the conversation; the transcript keeps the whole sitting"
        disabled=${!link.value} onClick=${() => send("reset")}><${Icon} n="reset" cls="sm" /><span class="hide-narrow">New conversation</span></button>
    </header>
    ${b && b.config_problem ? html`<div class="thread" style="padding-bottom:0"><div class="notice bad"><${Icon} n="alert" />
      <div>${b.config} could not be read and the forms opened on defaults: ${b.config_problem}</div></div></div>` : null}
    <div class="thread-scroll">
      <div class="scroll" ref=${scrollRef} onScroll=${onScroll} style="height:100%">
        <div ref=${innerRef} style="min-height:100%;display:flex;flex-direction:column">
          <${SetupCard} />
          ${thread.value.length ? html`<${Thread} />` : html`<${Empty} onPick=${pick} />`}
        </div>
      </div>
      <button class=${`btn jump ${away ? "show" : ""}`} onClick=${toBottom}><${Icon} n="down" cls="sm" />Latest</button>
    </div>
    <${Composer} inputRef=${inputRef} />
    <div class=${`dropzone ${drag ? "show" : ""}`}><div class="inner"><${Icon} n="file" cls="lg" />
      Drop to let him answer from this document<span>.txt or .md -- it stays on this machine</span></div></div>
    <${WindowDrawer} open=${drawer} onClose=${() => setDrawer(false)} />
  </div>`;
}

export function focusComposer() {
  const el = document.querySelector(".box textarea");
  if (el) el.focus();
}
