/* The library's motion: what moves, and why it stays out of the way.

   Every page is a real page (no client router), so movement between them is
   the browser's cross-document view transition, declared in library.css. This
   file only tells it *what carries over*: the finding number you clicked flies
   to the big number on the finding's page, a thread's title in a contents list
   becomes the thread page's heading, and turning a page (the foot's previous /
   next, or the arrow keys) slides the way a page turns. Going back reverses
   the same flight. Without view-transition support all of it is a no-op and
   the pages just load.

   Pages are prerendered on hover by the speculation rules in base.html, so a
   click shows a page that is already built; anything that animates on arrival
   waits for the page to be shown, not for it to be prerendered.

   Nothing here is needed to read the record: it is all progressive. */
(function () {
  "use strict";
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var last = null;                    // the link the reader last chose

  function shown(fn) {
    if (document.prerendering) document.addEventListener("prerenderingchange", fn, { once: true });
    else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn, { once: true });
    else fn();
  }

  function visible(el) {
    if (!el || !el.getClientRects().length) return false;
    var r = el.getBoundingClientRect();
    return r.bottom > 0 && r.top < innerHeight;
  }

  // The element on this page that stands for a link to `path`, and the name
  // it shares with the page it leads to.
  function carrier(a, path) {
    if (/\/finding\/\d+(\.html)?$/.test(path)) {
      var fn = a.closest(".fn") || a.querySelector(".fn");
      return fn ? [fn, "num"] : null;
    }
    if (/\/thread\//.test(path) && (a.classList.contains("t") || a.closest(".index-thread h3")))
      return [a, "title"];
    return null;
  }

  // Elements that hold a name on every page of their kind (the finding's big
  // number, the thread's heading). Two holders of one name abort the whole
  // transition, so a named link first quiets the page's own holder.
  var HOLDER = { num: ".chapter-open .cn", title: ".vt-title" };

  // A transition the browser abandons (a page restored from the back-forward
  // cache, a hidden tab) rejects; that is not an error, the page just shows.
  function after(vt, fn) { vt.finished.then(fn, fn); }

  function quiet(n, vt) {
    var el = document.querySelector(HOLDER[n]);
    if (!el) return false;
    el.style.viewTransitionName = "none";
    after(vt, function () { el.style.viewTransitionName = ""; });
    return true;
  }

  function name(el, n, vt) {
    if (el.matches(HOLDER[n])) return;
    quiet(n, vt);
    el.style.viewTransitionName = n;
    after(vt, function () { el.style.viewTransitionName = ""; });
  }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a[href]");
    if (a) last = a;
  }, true);

  addEventListener("pageswap", function (e) {
    if (!e.viewTransition || !e.activation || !e.activation.entry) return;
    var to = new URL(e.activation.entry.url);
    if (to.origin !== location.origin) return;
    var a = last && new URL(last.href, location.href).pathname === to.pathname ? last : null;
    if (!a) {                         // a typed URL or the arrow keys' fallback
      a = Array.prototype.find.call(document.querySelectorAll('a[href="' + to.pathname + '"]'), visible) || null;
    }
    var turn = a && a.closest(".turn") ? (a.closest(".r") ? "next" : "prev") : "";
    if (turn) { quiet("num", e.viewTransition); quiet("title", e.viewTransition); }  // a turned page slides whole
    else if (a) {
      var c = carrier(a, to.pathname);
      if (c && visible(c[0])) name(c[0], c[1], e.viewTransition);
    }
    try { sessionStorage.setItem("turn", turn); } catch (_) {}
  });

  addEventListener("pagereveal", function (e) {
    if (!e.viewTransition) return;
    var turn = "";
    try { turn = sessionStorage.getItem("turn") || ""; sessionStorage.removeItem("turn"); } catch (_) {}
    var act = window.navigation && navigation.activation;
    if (act && act.navigationType === "traverse") turn = "back";
    if (turn) e.viewTransition.types.add(turn);
    if (turn === "next" || turn === "prev") { quiet("num", e.viewTransition); quiet("title", e.viewTransition); return; }
    // Coming back from a finding or thread: the number or title flies home,
    // unless this page holds that name itself (finding to finding).
    var from = act && act.from && act.from.url ? new URL(act.from.url) : null;
    if (from && from.origin === location.origin) {
      var a = Array.prototype.find.call(document.querySelectorAll('a[href="' + from.pathname + '"]'), visible);
      var c = a && carrier(a, from.pathname);
      if (c && !document.querySelector(HOLDER[c[1]])) name(c[0], c[1], e.viewTransition);
    }
  });

  // Arrow keys turn the page; "/" goes to the finder.
  document.addEventListener("keydown", function (e) {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    var t = e.target;
    if (t.closest && t.closest("input, textarea, select, [contenteditable]")) {
      if (e.key === "Escape" && t.blur) t.blur();
      return;
    }
    var a = null;
    if (e.key === "ArrowRight") a = document.querySelector(".turn .r a");
    else if (e.key === "ArrowLeft") a = document.querySelector(".turn > div:first-child a");
    else if (e.key === "/") {
      var box = document.querySelector(".filter input");
      if (box) { e.preventDefault(); box.focus(); box.select(); }
      else {                          // the nav's own link, so a prefixed export goes home too
        var f = document.querySelector('.running nav [data-key="findings"]');
        if (f) { e.preventDefault(); location.href = f.href; }
      }
      return;
    }
    if (a) { e.preventDefault(); a.click(); }
  });

  // The shelf: a book read aloud under the shelf while you point at it, and
  // the books set out once a sitting.
  shown(function () {
    var shelf = document.querySelector("svg.shelf");
    if (!shelf) return;
    var read = document.querySelector(".shelf-fig .read");
    var cap = document.querySelector(".shelf-fig figcaption");
    var books = shelf.querySelectorAll("a");
    function point(a) {
      if (!read) return;
      read.querySelector(".rn").textContent = a.dataset.name;
      read.querySelector(".rc").textContent = a.dataset.count + " findings" + (a.classList.contains("pale") ? ", at rest" : "");
      read.querySelector(".rl").textContent = a.dataset.line;
      read.style.setProperty("--c", a.dataset.cloth);
      cap.classList.add("reading");
    }
    function leave() { cap.classList.remove("reading"); }
    Array.prototype.forEach.call(books, function (a) {
      a.addEventListener("mouseenter", function () { point(a); });
      a.addEventListener("focus", function () { point(a); });
      a.addEventListener("mouseleave", leave);
      a.addEventListener("blur", leave);
    });
    var seen = false;
    try { seen = sessionStorage.getItem("shelf") === "1"; sessionStorage.setItem("shelf", "1"); } catch (_) {}
    if (!seen && !reduce) shelf.classList.add("enter");
  });
})();
