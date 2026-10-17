// About him: the model card, read from disk and rendered, so the card and the
// page can never disagree. When the numbers are re-run the card changes and
// this page follows.

import { useState } from "preact/hooks";
import { html, Icon, useResource, Collapse, Page, Skeleton } from "../lib.js";

function Section({ s }) {
  const [open, setOpen] = useState(s.open);
  return html`<div class="card">
    <button class=${`acc-head ${open ? "open" : ""}`} onClick=${() => setOpen(!open)}>
      <${Icon} n="chev" cls=${`sm chev ${open ? "open" : ""}`} /><span class="grow">${s.title}</span></button>
    <${Collapse} open=${open}><div class="acc-body prose" dangerouslySetInnerHTML=${{ __html: s.html }}></div><//>
  </div>`;
}

export default function About() {
  const r = useResource("/api/about");
  const d = r.data;
  return html`<${Page} title="About him">
    ${!d ? html`<${Skeleton} lines=${8} />` : html`
      <div class="lead">From <span class="mono">${d.card}</span> -- the same card that ships with the weights. Every number is a measurement on the released checkpoint.</div>
      ${d.sections.length ? d.sections.map(s => html`<${Section} key=${s.title} s=${s} />`)
        : html`<div class="empty">The model card is not in this checkout.</div>`}
      <div class="small muted" style="margin-top:16px">The findings behind each claim are in docs/findings/ -- one numbered file per capability and per defect.</div>`}
  <//>`;
}
