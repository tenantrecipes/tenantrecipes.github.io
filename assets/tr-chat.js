/* Tenant Recipes site chat widget. Usage:
   <script src="/assets/tr-chat.js" data-endpoint="https://chat.tenantrecipes.com" data-sitekey="TURNSTILE_SITEKEY" defer></script>
   Nothing third-party loads until the visitor opens the chat. Answers are rendered as TEXT (no HTML injection). */
(() => {
  const me = document.currentScript;
  const API = (me.dataset.endpoint || "").replace(/\/$/, "");
  const SITEKEY = me.dataset.sitekey || "";
  const MAX = 500;
  let session = null, sessionExp = 0, tsReady = null, busy = false;
  const el = (t, a = {}, ...kids) => { const e = document.createElement(t); for (const [k, v] of Object.entries(a)) k === "text" ? (e.textContent = v) : e.setAttribute(k, v); kids.forEach(k => e.append(k)); return e; };
  const icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>';

  const fab = el("button", { class: "trc-fab", type: "button", "aria-expanded": "false", "aria-controls": "trc-panel" });
  fab.innerHTML = icon + "<span>Ask the site</span>";
  const panel = el("div", { class: "trc-panel", id: "trc-panel", role: "dialog", "aria-labelledby": "trc-title", hidden: "" });
  const close = el("button", { class: "trc-x", type: "button", "aria-label": "Close chat", text: "×" });
  const hd = el("div", { class: "trc-hd" }, el("div", {}, el("h2", { id: "trc-title", text: "Ask Tenant Recipes" }), el("p", { text: "Answers only from this site's pages, with links." })), close);
  const log = el("div", { class: "trc-log", role: "log", "aria-live": "polite", "aria-relevant": "additions" });
  const ta = el("textarea", { id: "trc-q", rows: "2", maxlength: String(MAX), placeholder: "e.g. How do I restrict who can create agents?", "aria-label": "Your question about Tenant Recipes" });
  const send = el("button", { class: "trc-send", type: "submit", text: "Ask" });
  const count = el("span", { "aria-live": "off", text: `0/${MAX}` });
  const ts = el("div", { class: "trc-ts" });
  const fine = el("p", { class: "trc-fine" }, el("span", { text: "AI answers can be wrong; check the linked page. Questions aren't stored. " }), count);
  const form = el("form", { class: "trc-f" }, ts, el("div", { class: "trc-row" }, ta, send), fine);
  panel.append(hd, log, form);
  document.body.append(panel, fab);

  const say = (cls, text) => { const m = el("div", { class: `trc-m ${cls}`, text }); log.append(m); log.scrollTop = log.scrollHeight; return m; };
  const lock = (msg) => { ta.disabled = true; send.disabled = true; if (msg) say("trc-sys", msg); };

  function toggle(open) {
    panel.hidden = !open; fab.setAttribute("aria-expanded", String(open));
    if (open) { if (!log.childElementCount) init(); ta.focus(); } else fab.focus();
  }
  fab.addEventListener("click", () => toggle(panel.hidden));
  close.addEventListener("click", () => toggle(false));
  panel.addEventListener("keydown", e => { if (e.key === "Escape") toggle(false); });
  ta.addEventListener("input", () => { count.textContent = `${ta.value.length}/${MAX}`; });
  ta.addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });

  async function init() {
    say("trc-a", "Hi! Ask me about the recipes, guides, news, tools and policies on Tenant Recipes. I only answer from this site.");
    try { const r = await fetch(`${API}/api/status`); const j = await r.json(); if (!j.open) lock("Chat is paused right now. Please try again tomorrow, or use the site search."); }
    catch { lock("Chat is unavailable right now. Please use the site search."); }
  }
  function turnstileToken() {      // loaded lazily, only after the visitor opens the chat and asks
    if (tsReady) return tsReady;
    tsReady = new Promise((res, rej) => {
      const render = () => window.turnstile.render(ts, { sitekey: SITEKEY, size: "flexible", appearance: "interaction-only", callback: res, "error-callback": () => rej(new Error("ts")) });
      if (window.turnstile) return render();
      window.trcTsLoad = render;
      const s = el("script", { src: "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=trcTsLoad", async: "" });
      s.onerror = () => rej(new Error("ts-load"));
      document.head.append(s);
    });
    return tsReady;
  }
  async function getSession() {
    if (session && Date.now() < sessionExp - 30000) return session;
    const token = await turnstileToken(); tsReady = null; try { window.turnstile.remove(ts); } catch {}
    const r = await fetch(`${API}/api/session`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ turnstile: token }) });
    const j = await r.json();
    if (!r.ok) throw Object.assign(new Error(j.error || "session"), { j, status: r.status });
    session = j.session; sessionExp = Date.now() + j.ttl * 1000; return session;
  }
  form.addEventListener("submit", async e => {
    e.preventDefault();
    const q = ta.value.trim();
    if (busy || q.length < 3) return;
    busy = true; send.disabled = true; ta.value = ""; count.textContent = `0/${MAX}`;
    say("trc-u", q);
    const wait = say("trc-sys", "Looking through Tenant Recipes…");
    try {
      const s = await getSession();
      const r = await fetch(`${API}/api/chat`, { method: "POST", headers: { "content-type": "application/json", authorization: `Bearer ${s}` }, body: JSON.stringify({ q }) });
      const j = await r.json(); wait.remove();
      if (r.status === 503) return lock(j.message || "Chat is paused for today. Please try again tomorrow.");
      if (r.status === 429) return say("trc-sys", j.message || "Too many questions. Please wait a moment.");
      if (r.status === 401) { session = null; return say("trc-sys", "Your chat session expired. Please ask again."); }
      if (!r.ok) return say("trc-sys", j.message || "Something went wrong. Please try again.");
      const m = say("trc-a", j.answer);
      if (j.sources?.length) {
        const ol = el("ol", { "aria-label": "Sources" });
        for (const s of j.sources) if (/^https:\/\/(www\.)?tenantrecipes\.com\//.test(s.url)) ol.append(el("li", {}, el("a", { href: s.url, text: s.title })));
        m.append(ol);
      }
    } catch (err) { wait.remove(); if (err.status === 503) lock(err.j?.message); else say("trc-sys", "Couldn't verify you're human, or the chat is unavailable. Please try again."); }
    finally { busy = false; if (!ta.disabled) send.disabled = false; }
  });
})();
