"""Findability & sharing layer (2026-10-30): tags, Start-here cards, recipe toolbars (copy / checklist download),
Done-when, related recipes, back-to-guide links, mid-page newsletter CTA, quick guide and sample newsletter pages,
Open Graph image selection. Everything is computed from the site data at build time."""
import re, json, datetime
from html import escape as E
import site_config as C
import build_trust as T

SITE = C.SITE_URL.rstrip("/")


def esc(s):
    return E(str(s), quote=True)


# ---------------------------------------------------------------- tags
TAG_ORDER = ["Copilot", "Conditional Access", "Identity", "Intune", "Purview & DLP", "Agents", "Licensing",
             "Security", "News / Retirement", "PowerShell & Graph", "Prompts"]
SEC_CATS = {"Conditional Access for AI", "Identity & threat protection", "Purview, DLP & data security for Copilot"}
_CMD = re.compile(r"`[^`]*(?:\b[A-Z][a-z]+-[A-Z][A-Za-z]+\b|graph\.microsoft\.com)[^`]*`")
_DATE = re.compile(r"\b(?:\d{1,2} )?(?:January|February|March|April|May|June|July|August|September|October|November|December)[a-z]* (?:\d{1,2}, )?20\d\d\b|\bweek of \d")


def tags_for(r):
    head = (r["title"] + " " + r["problem"]).lower()
    cat = r["category"]
    t = set()
    if "copilot" in head or cat.startswith("Copilot"):
        t.add("Copilot")
    if cat == "Conditional Access for AI" or "conditional access" in head or r["id"].startswith("ca-"):
        t.add("Conditional Access")
    if cat in ("Identity & threat protection",) or any(k in head for k in ("mfa", "consent", "passkey", "sign-in", "entra", "guest")):
        t.add("Identity")
    if cat == "Intune & devices for AI" or "intune" in head:
        t.add("Intune")
    if cat.startswith("Purview") or any(k in head for k in ("purview", "dlp", "sensitivity label", "oversharing")):
        t.add("Purview & DLP")
    if cat.startswith("Agents") or "agent" in r["title"].lower():
        t.add("Agents")
    if cat == "Licensing & reporting" or "license" in r["title"].lower():
        t.add("Licensing")
    if cat in SEC_CATS or any(k in head for k in ("phishing", "risk", "break-glass", "legacy auth")):
        t.add("Security")
    if "retire" in head or _DATE.search(r["problem"] + " " + r["title"]):
        t.add("News / Retirement")
    if any(_CMD.search(s) for s in r["steps"]):
        t.add("PowerShell & Graph")
    if cat == "Admin prompt templates":
        t.add("Prompts")
    return [x for x in TAG_ORDER if x in t]


def tag_counts(R):
    c = {}
    for r in R:
        for t in tags_for(r):
            c[t] = c.get(t, 0) + 1
    return [(t, c[t]) for t in TAG_ORDER if t in c]


def slim_js(R):
    slim = [{"id": r["id"], "category": r["category"], "title": r["title"], "problem": r["problem"], "steps": r["steps"],
             "v": r.get("last_verified") or "", "n": len(r.get("sources", [])), "tg": tags_for(r), "c": r.get("created") or ""} for r in R]
    return "window.RECIPES=" + json.dumps(slim, ensure_ascii=False) + ";"


# ---------------------------------------------------------------- guides <-> recipes
def guide_refs(guides):
    """recipe id -> list of (guide, phase_no, step_no, phase, step) in guide order."""
    out = {}
    for g in guides:
        for i, ph in enumerate(g.PHASES, 1):
            for j, st in enumerate(ph["steps"], 1):
                for rid in st["rec"]:
                    out.setdefault(rid, []).append((g, i, j, ph, st))
    return out


def anchor(g, i, ph, j=None):
    return f'phase-{i}-{ph["id"]}' + (f"-s{j}" if j else "")


def back_to_guide(rel, r, refs, fallback):
    hits = refs.get(r["id"], [])
    if hits:
        g, i, j, ph, st = hits[0]
        href = f'{rel}guides/{g.SLUG}.html#{anchor(g, i, ph, j)}'
        more = f' <span class="bg-more">(+{len(hits) - 1} more step{"s" if len(hits) > 2 else ""})</span>' if len(hits) > 1 else ""
        return (f'<a class="bg" href="{href}"><span class="bg-k">{T.icon("book")}Part of {esc(g.SHORT)}</span>'
                f'<strong>← Back to the guide: phase {i}, step {i}.{j}: {esc(st["t"])}</strong>{more}</a>')
    g = fallback
    return (f'<a class="bg" href="{rel}guides/{g.SLUG}.html"><span class="bg-k">{T.icon("book")}Pillar guide</span>'
            f'<strong>← See where this fits: {esc(g.SHORT)}</strong></a>')


def related(r, R, refs, n=3):
    mine = set(tags_for(r))
    phases = {(g.SLUG, i) for g, i, j, ph, st in refs.get(r["id"], [])}
    scored = []
    for x in R:
        if x["id"] == r["id"]:
            continue
        s = 2 * len(mine & set(tags_for(x))) + (3 if x["category"] == r["category"] else 0)
        s += 4 * len(phases & {(g.SLUG, i) for g, i, j, ph, st in refs.get(x["id"], [])})
        if s:
            scored.append((s, x.get("order", 0), x))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [x for _, _, x in scored[:n]]


def related_cards(rel, items):
    return "".join(f'<a class="card" href="{rel}recipes/{x["id"]}.html"><div class="tag">{esc(x["category"])}</div>'
                   f'<h3>{esc(x["title"])}</h3><p class="clamp">{esc(x["problem"])}</p>{T.card_meta(x)}</a>' for x in items)


# ---------------------------------------------------------------- plain-text / markdown checklists
def plain(s):
    return s.replace("`", "")


def recipe_markdown(r):
    url = f'{SITE}/recipes/{r["id"]}.html'
    out = [f'# {r["title"]}', "", f'Source: {url}', f'Verified against Microsoft sources: {r.get("last_verified") or "not yet"}', "",
           "## Problem", r["problem"], "", "## Steps"]
    out += [f"- [ ] {i}. {s}" for i, s in enumerate(r["steps"], 1)]
    if r.get("done_when"):
        out += ["", "## Done when"] + [f"- [ ] {s}" for s in r["done_when"]]
    if r.get("pitfalls"):
        out += ["", "## Pitfalls"] + [f"- {s}" for s in r["pitfalls"]]
    out += ["", "## Sources"] + [f'- {s["title"]}: {s["url"]}' for s in r["sources"]]
    out += ["", f"From {C.SITE_NAME} ({SITE}). Always confirm against the linked sources and test in a pilot first.", ""]
    return "\n".join(out)


def steps_text(r):
    url = f'{SITE}/recipes/{r["id"]}.html'
    t = [r["title"], ""] + [f"{i}. {plain(s)}" for i, s in enumerate(r["steps"], 1)]
    if r.get("done_when"):
        t += ["", "Done when:"] + [f"- {plain(s)}" for s in r["done_when"]]
    return "\n".join(t + ["", url])


def guide_markdown(g):
    out = [f"# {g.TITLE}: checklist", "", f"Source: {SITE}/guides/{g.SLUG}.html", f"Verified: {g.VERIFIED}", ""]
    for i, ph in enumerate(g.PHASES, 1):
        out.append(f'## Phase {i}: {ph["title"]} (about {ph["time"]})')
        out += [f'- [ ] {i}.{j} {st["t"]}: {st["check"]}' for j, st in enumerate(ph["steps"], 1)]
        out.append("")
    out += [f"From {C.SITE_NAME} ({SITE}). Time estimates are our own planning figures.", ""]
    return "\n".join(out)


def _script_text(s):
    return s.replace("</", "<\\/").replace("<!--", "<\\!--")


def toolbar(rel, r):
    """Copy steps / Download checklist / Print. Text is pre-rendered at build time; ui.js only copies it."""
    return (f'<div class="rx" role="group" aria-label="Use this recipe">'
            f'<button class="btn rx-b" type="button" data-copy="rx-steps">{T.icon("list")}<span>Copy steps</span></button>'
            f'<a class="btn rx-b" href="{rel}recipes/checklists/{r["id"]}.md" download="{r["id"]}-checklist.md">{T.icon("check")}<span>Download checklist (.md)</span></a>'
            f'<button class="btn rx-b" type="button" data-print="1">{T.icon("book")}<span>Print / save as PDF</span></button>'
            f'<script type="text/plain" id="rx-steps">{_script_text(steps_text(r))}</script></div>')


def done_when(r, step_html):
    if not r.get("done_when"):
        return ""
    lis = "".join(f'<li>{step_html(x)}</li>' for x in r["done_when"])
    return (f'<section id="done" class="co co-ok dw"><p class="co-h">{T.icon("check")}Done when</p>'
            f'<ul class="dw-l">{lis}</ul><p class="fine">Our own completion criteria, derived from the steps above. Check them before you close the change.</p></section>')


def screenshots(r, rel):
    """Optional, real screenshots only (schema: src, alt, caption, date). Nothing is rendered when the list is empty."""
    shots = r.get("screenshots") or []
    if not shots:
        return ""
    figs = "".join(f'<figure class="shot"><img src="{rel}{esc(s["src"])}" alt="{esc(s["alt"])}" loading="lazy">'
                   f'<figcaption>{esc(s["caption"])} <span class="fine">Screenshot taken {T.fmt(s["date"])}. Portal labels may have changed since.</span></figcaption></figure>'
                   for s in shots)
    return f'<section class="shots" aria-label="Screenshots">{figs}</section>'


# ---------------------------------------------------------------- newsletter CTA
def news_mid(rel, source):
    u = esc(C.BUTTONDOWN_USERNAME)
    return (f'<aside class="nm" aria-label="Newsletter"><div class="nm-t"><p class="nm-h">Get changes like this in your inbox</p>'
            f'<p>The weekly Tenant Recipes brief: what changed in Copilot, Intune, Entra and Purview, and what to do about it. 5 minutes, no fluff. '
            f'<a href="{rel}newsletter-sample.html">See a sample issue</a>.</p></div>'
            f'<form class="bd-form" action="https://buttondown.com/api/emails/embed-subscribe/{u}" method="post" target="_blank">'
            f'<label class="sr" for="nm-{source}">Email address</label>'
            f'<input id="nm-{source}" type="email" name="email" required autocomplete="email" placeholder="you@company.com">'
            f'<input type="hidden" name="embed" value="1"><input type="hidden" name="metadata__source" value="mid-{esc(source)}">'
            f'<button class="btn p" type="submit">Subscribe</button></form></aside>')


# ---------------------------------------------------------------- homepage finder + Start here
def finder(rel, R, guides, quick, n_sec):
    G1, G2 = guides[0], guides[1]
    chips = "".join(f'<a class="chip" href="?t={E(t.replace(" ", "+"))}#library" data-tag="{esc(t)}">{esc(t)} <span>{n}</span></a>'
                    for t, n in tag_counts(R))
    newest = sorted(R, key=lambda r: (r.get("created", ""), r.get("updated", "")), reverse=True)[:3]
    new_li = "".join(f'<li><a href="{rel}recipes/{r["id"]}.html">{esc(r["title"])}</a></li>' for r in newest)
    nsteps = lambda g: sum(len(p["steps"]) for p in g.PHASES)
    cards = (
        f'<a class="sh-c sh-1" href="{rel}guides/{G1.SLUG}.html"><span class="sh-k">{T.icon("shield")}Start here · pillar guide</span>'
        f'<strong>Secure Copilot rollout</strong><p>{len(G1.PHASES)} phases, {nsteps(G1)} steps, from licensing to oversharing clean-up and pilot.</p>'
        f'<span class="sh-go">Open the guide {T.icon("arrow")}</span></a>'
        f'<a class="sh-c sh-2" href="{rel}guides/{G2.SLUG}.html"><span class="sh-k">{T.icon("layers")}Pillar guide</span>'
        f'<strong>Windows 11 hardening</strong><p>{len(G2.PHASES)} phases built around the CIS Benchmark and Microsoft security baselines.</p>'
        f'<span class="sh-go">Open the guide {T.icon("arrow")}</span></a>'
        f'<a class="sh-c sh-3" href="{rel}security/index.html"><span class="sh-k">{T.icon("alert")}Security</span>'
        f'<strong>Vulnerability watch &amp; hardening</strong><p>{n_sec} entries: exploited CVEs to patch first, plus network, server and VMware hardening.</p>'
        f'<span class="sh-go">Open security {T.icon("arrow")}</span></a>'
        f'<div class="sh-c sh-4"><span class="sh-k">{T.icon("clock")}Newest recipes</span><ul>{new_li}</ul>'
        f'<a class="sh-go" href="{rel}guides/{quick.SLUG}.html">Quick guide: {esc(quick.SHORT.split(": ", 1)[-1])} {T.icon("arrow")}</a></div>')
    return (f'<section class="fd wrap" id="find" aria-labelledby="fd-h"><h2 id="fd-h" class="sr">Find a recipe</h2>'
            f'<form class="fd-s" action="{rel}search.html" method="get" role="search">{T.icon("search")}'
            f'<label class="sr" for="fd-q">Search all recipes, guides and security entries</label>'
            f'<input id="fd-q" name="q" type="search" placeholder="Search {len(R)} recipes, guides and CVEs: e.g. MFA, DLP, LAPS, agents" autocomplete="off">'
            f'<button class="btn p" type="submit">Search</button></form>'
            f'<nav class="fd-tags" aria-label="Browse by topic"><span class="fd-l">Browse by topic:</span>{chips}</nav>'
            f'<p class="sec-k fd-k">Start here</p><div class="sh">{cards}</div></section>')


# ---------------------------------------------------------------- quick guide page
def quick_body(rel, Q, RID, page_signup):
    def srcs(keys):
        return "".join(f'<li><a href="{E(Q.S[k][1])}">{esc(Q.S[k][0])}</a></li>' for k in keys)

    def recs(ids):
        return "".join(f'<a class="gd-chip" href="{rel}recipes/{i}.html">{esc(RID[i]["title"])}</a>' for i in ids)
    items = ""
    for n, c in enumerate(Q.CHECKS, 1):
        items += (f'<li class="qg-i" id="check-{n}"><span class="qg-n">{n}</span><div><h2>{esc(c["t"])}</h2><p>{esc(c["why"])}</p>'
                  f'<p class="qg-c"><strong>Check:</strong> {esc(c["check"])}</p><div class="gd-recs">{recs(c["rec"])}</div>'
                  f'<details class="gd-src"><summary>Microsoft sources ({len(c["src"])})</summary><ul>{srcs(c["src"])}</ul></details></div></li>')
    th = Q.THEN
    allsrc = []
    for c in Q.CHECKS + [th]:
        for k in c["src"]:
            if k not in allsrc:
                allsrc.append(k)
    pdf = f"{rel}downloads/{Q.SLUG}.pdf"
    return (T.page_hero(rel, T.crumbs_dark(rel, f"guides/{Q.SLUG}.html", [("Home", rel + "index.html"), ("Guides", rel + "guides/index.html"), ("Quick guide", None)]),
                        f'{T.icon("check")}Quick guide · 1 page', esc(Q.TITLE),
                        "A pre-flight check you can run in an afternoon. Each item links to the Microsoft Learn page it was checked against "
                        "and to our hands-on recipe.",
                        T.chip("check", f"Verified {T.fmt(Q.VERIFIED)}") + T.chip("link", f"{len(allsrc)} Microsoft sources") + T.chip("list", "Printable PDF"), kind="page")
            + f'<main class="wrap pg"><article class="doc qg">'
            f'<div class="rx"><a class="btn p rx-b" href="{pdf}" download>{T.icon("book")}<span>Download the 1-page PDF</span></a>'
            f'<button class="btn rx-b" type="button" data-print="1">{T.icon("list")}<span>Print</span></button></div>'
            f'<ol class="qg-l">{items}</ol>'
            f'<section class="co co-info"><p class="co-h">{T.icon("arrow")}{esc(th["t"])}</p><p>{esc(th["text"])}</p><div class="gd-recs">{recs(th["rec"])}</div></section>'
            + news_mid(rel, "quick-" + Q.SLUG) +
            f'<section class="vs" id="verified"><h2>Verification &amp; corrections</h2><p class="fine">Every item was checked against these Microsoft Learn pages on '
            f'<strong>{T.fmt(Q.VERIFIED)}</strong>. The wording is ours: always confirm against the source before you act.</p>'
            f'<ul class="vs-l">{srcs(allsrc)}</ul><div class="vs-f"><p>Spotted something wrong or outdated?</p>'
            f'{T.report_link(f"guides/{Q.SLUG}.html", Q.TITLE, "rp btn")}</div></section>'
            f'<p>Want the full picture? Read <a href="{rel}guides/secure-copilot-rollout.html">the secure Copilot rollout guide</a>.</p>'
            f'</article></main>' + page_signup)


# ---------------------------------------------------------------- sample newsletter issue
def sample_issue_body(rel, R, CY, guides):
    """A clearly labelled example issue assembled only from pages already published (and fact-checked) on the site."""
    news = [r for r in R if "News / Retirement" in tags_for(r)]
    news.sort(key=lambda r: (r.get("created", ""), r["id"]), reverse=True)
    top = news[0] if news else R[0]
    rest = [r for r in news if r["id"] != top["id"]][:4]
    vulns = sorted([e for e in CY if e["type"] == "vulnerability" and e.get("exploited")],
                   key=lambda e: e.get("kev_added") or e.get("advisory_date") or "", reverse=True)[:2]
    rotw = next((r for r in R if r["id"] == "ca-break-glass"), R[0])
    li = lambda href, title, text: f'<li><a href="{href}"><strong>{esc(title)}</strong></a> {esc(text)}</li>'
    g = guides[0]
    first = re.sub(r"`", "", top["steps"][0])
    return (T.page_hero(rel, T.crumbs_dark(rel, "newsletter-sample.html", [("Home", rel + "index.html"), ("Newsletter", rel + "newsletter.html"), ("Sample issue", None)]),
                        "Newsletter · example", "What the weekly brief looks like",
                        "A sample issue, assembled from pages already published on this site, so you can see the format before you subscribe.", kind="page")
            + '<main class="wrap pg"><article class="doc nl">'
            '<p class="nl-flag" role="note"><strong>Example issue.</strong> This page shows the format only. It was not sent to anyone, '
            'and every item links to a fact-checked page on Tenant Recipes, where you will find the Microsoft or vendor sources.</p>'
            f'<div class="nl-mail"><p class="nl-meta">From: Tenant Recipes · Subject: <strong>{esc(top["title"])}</strong> (+ {len(rest) + len(vulns)} more)</p>'
            f'<h2>Top story</h2><h3><a href="{rel}recipes/{top["id"]}.html">{esc(top["title"])}</a></h3><p>{esc(top["problem"])}</p>'
            f'<p><strong>Admin take:</strong> start here: {esc(first)}</p>'
            '<h2>Also this week</h2><ul>' + "".join(li(f'{rel}recipes/{r["id"]}.html', r["title"], r["problem"].split(". ")[0] + ".") for r in rest) + '</ul>'
            + ('<h2>Patch first</h2><ul>' + "".join(li(f'{rel}security/{e["id"]}.html', e["title"], e["summary"].split(". ")[0] + ".") for e in vulns) + '</ul>' if vulns else "")
            + f'<h2>Recipe of the week</h2><p><a href="{rel}recipes/{rotw["id"]}.html"><strong>{esc(rotw["title"])}</strong></a>. {esc(rotw["problem"])}</p>'
            f'<h2>From the guides</h2><p><a href="{rel}guides/{g.SLUG}.html">{esc(g.TITLE)}</a>: {len(g.PHASES)} phases with a printable checklist.</p>'
            '<p class="fine">You get this because you subscribed on tenantrecipes.github.io. One click to unsubscribe in every real issue.</p></div>'
            '</article></main>')


# ---------------------------------------------------------------- Open Graph image per page
OG_CATS = {
    "Copilot rollout & governance": "copilot", "Conditional Access for AI": "conditional-access", "Intune & devices for AI": "intune",
    "Purview, DLP & data security for Copilot": "purview", "Identity & threat protection": "identity",
    "Agents & Copilot Studio governance": "agents", "Licensing & reporting": "licensing", "Admin prompt templates": "prompts",
}


def og_image(path, RID):
    """Return (file under assets/og/, alt text)."""
    if path.startswith("recipes/"):
        r = RID.get(path[8:-5])
        if r:
            return f'og/cat-{OG_CATS.get(r["category"], "copilot")}.png', f'Tenant Recipes: {r["category"]}'
    if path.startswith("guides/secure-copilot-rollout"):
        return "og/guide-secure-copilot-rollout.png", "Tenant Recipes guide: secure Copilot rollout"
    if path.startswith("guides/windows-11-cis-hardening"):
        return "og/guide-windows-11-cis-hardening.png", "Tenant Recipes guide: Windows 11 hardening with the CIS Benchmark"
    if path.startswith("guides/copilot-license-checks"):
        return "og/quick-copilot-license-checks.png", "Tenant Recipes quick guide: 5 checks before Copilot licenses"
    if path.startswith("guides/"):
        return "og/guides.png", "Tenant Recipes guides"
    if path.startswith("security/"):
        return "og/security.png", "Tenant Recipes security: vulnerability watch and hardening"
    if path.startswith("newsletter"):
        return "og/newsletter.png", "The weekly Tenant Recipes brief"
    return "og-image.png", f"{C.SITE_NAME}: {C.SITE_TAGLINE}"


# ---------------------------------------------------------------- share buttons (plain links, no third-party scripts)
_SI = {
    "linkedin": ('fill', '<path d="M4 9h3.2v11H4zM5.6 3.6a1.85 1.85 0 110 3.7 1.85 1.85 0 010-3.7zM9.8 9h3v1.5c.5-.9 1.6-1.8 3.3-1.8 3.4 0 4 2.2 4 5.1V20h-3.2v-5.5c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9V20H9.8z"/>'),
    "x": ('fill', '<path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.4l4.4 5.8zm-1.1 16.2h1.7L7.4 4.7H5.6z"/>'),
    "reddit": ('fill', '<path fill-rule="evenodd" d="M12 8.2c-4.6 0-8.3 2.6-8.3 5.9S7.4 20 12 20s8.3-2.6 8.3-5.9S16.6 8.2 12 8.2zM8.8 15.4a1.4 1.4 0 110-2.8 1.4 1.4 0 010 2.8zm6.4 0a1.4 1.4 0 110-2.8 1.4 1.4 0 010 2.8z"/><circle cx="17.6" cy="4.6" r="1.6"/><path d="M12.6 8.3l1.3-4.4 3.7.8-.2.9-2.8-.6-1 3.4z"/>'),
    "bluesky": ('fill', '<path d="M6.3 4.4C8.6 6.1 11 9.6 12 11.4c1-1.8 3.4-5.3 5.7-7 1.6-1.2 4.3-2.2 4.3.9 0 .6-.4 5.2-.6 5.9-.7 2.6-3.3 3.2-5.6 2.8 4 .7 5 2.9 2.8 5.2-4.2 4.3-6-1.1-6.5-2.5L12 16l-.1.7c-.5 1.4-2.3 6.8-6.5 2.5-2.2-2.3-1.2-4.5 2.8-5.2-2.3.4-4.9-.2-5.6-2.8C2.4 10.5 2 5.9 2 5.3c0-3.1 2.7-2.1 4.3-.9z"/>'),
    "mail": ('stroke', '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5l8.5 6.5 8.5-6.5"/>'),
    "link": ('stroke', T._P["link"]),
    "share": ('stroke', '<circle cx="18" cy="5.5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="18.5" r="2.5"/><path d="M8.2 10.8l7.6-4.1M8.2 13.2l7.6 4.1"/>'),
}


def _sic(name):
    kind, body = _SI[name]
    attrs = 'fill="currentColor" stroke="none"' if kind == "fill" else 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg class="shr-i" width="1em" height="1em" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {attrs}>{body}</svg>'


def share_bar(path, title, where="top"):
    from urllib.parse import quote
    url = f"{SITE}/{path}"
    u, t = quote(url, safe=""), quote(title, safe="")
    links = [
        ("linkedin", "LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={u}"),
        ("x", "X", f"https://x.com/intent/post?text={t}&url={u}"),
        ("reddit", "Reddit", f"https://www.reddit.com/submit?url={u}&title={t}"),
        ("bluesky", "Bluesky", f"https://bsky.app/intent/compose?text={quote(title + ' ' + url, safe='')}"),
        ("mail", "Email", f"mailto:?subject={t}&body={quote(title + chr(10) + chr(10) + url, safe='')}"),
    ]
    a = "".join(f'<a class="shr-b shr-{k}" href="{E(h, quote=True)}"'
                + (f' data-x-app data-title="{esc(title)}" data-url="{E(url, quote=True)}"' if k == "x" else "")
                + ('' if k == "mail" else ' target="_blank" rel="noopener noreferrer"')
                + f' aria-label="Share on {n}' + (' (opens in a new tab)' if k != "mail" else '') + f'" title="Share on {n}">{_sic(k)}<span>{n}</span></a>'
                for k, n, h in links)
    a = a.replace('aria-label="Share on Email"', 'aria-label="Share by email"').replace('title="Share on Email"', 'title="Share by email"')
    a += (f'<button class="shr-b" type="button" data-share-copy="{E(url, quote=True)}" aria-label="Copy link to this page">{_sic("link")}<span>Copy link</span></button>'
          f'<button class="shr-b shr-native" type="button" data-share-native data-title="{esc(title)}" data-url="{E(url, quote=True)}" aria-label="Share with an app on this device" hidden>{_sic("share")}<span>Share…</span></button>')
    lab = "Share this page" if where == "top" else "Found this useful? Share it with a colleague"
    return f'<div class="shr shr-{where}" role="group" aria-label="{"Share this page" if where == "top" else "Share this page (end of page)"}"><span class="shr-l">{lab}</span>{a}</div>'


_SHARE_RULES = [  # (path regex, top-insert regex (insert AFTER match), bottom-insert regex (insert BEFORE match))
    (r"^recipes/[^/]+\.html$", r'id="rx-steps">.*?</script></div>', r'<section class="vs" id="verified"'),
    (r"^guides/copilot-license-checks\.html$", r'data-print="1">.*?</button></div>', r'<section class="vs" id="verified"'),
    (r"^guides/(?!index)[^/]+\.html$", r'<div class="gd-body">', r'<section class="vs" id="verified"'),
    (r"^security/[a-z0-9-]+-[a-z0-9-]+\.html$", r'<article class="doc">', r'<section class="vs" id="verified"'),
    (r"^newsletter-sample\.html$", r'<article class="doc nl">', r'</article></main>'),
]


def add_share(html, path, title):
    for pr, top, bot in _SHARE_RULES:
        if re.match(pr, path):
            m = re.search(top, html, re.S)
            b = re.search(bot, html)
            if not m or not b:
                raise SystemExit(f"share bar: marker not found on {path}")
            return html[:m.end()] + share_bar(path, title, "top") + html[m.end():b.start()] + share_bar(path, title, "end") + html[b.start():]
    return html


# ---------------------------------------------------------------- homepage featured carousel (data-driven, rotates with new content)
def featured(R, CY, guides, Q):
    """5 slides: pinned Copilot guide, latest exploited vulnerability, newest recipe, quick guide, Windows 11 guide.
    'Latest' is computed from data, so the nightly routine's new entries rotate in automatically."""
    G1, G2 = guides[0], guides[1]
    ns = lambda g: sum(len(p["steps"]) for p in g.PHASES)
    vkey = lambda e: e.get("kev_added") or e.get("advisory_date") or e.get("updated") or ""
    vulns = [e for e in CY if e["type"] == "vulnerability"]
    v = max([e for e in vulns if e.get("exploited")] or vulns, key=vkey) if vulns else None
    r = max(R, key=lambda x: (x.get("created", ""), x.get("updated", ""), x["id"]))
    first = lambda s: (s.split(". ")[0].rstrip(".") + ".") if s else ""
    slides = [dict(k="Pillar guide", t=G1.TITLE, s=f"{len(G1.PHASES)} phases and {ns(G1)} steps, from licensing and admin roles to the oversharing clean-up, labels, DLP and pilot.",
                   d=G1.VERIFIED, dl="Verified", u=f"guides/{G1.SLUG}.html", cta="Read the guide", img="og/guide-secure-copilot-rollout.png", c="c1")]
    if v:
        lab = "Vulnerability watch · " + ("Exploited · " if v.get("exploited") else "") + v.get("severity", "")
        slides.append(dict(k=lab, t=v["title"], s=first(v["summary"]), d=vkey(v), dl="Advisory" if not v.get("kev_added") else "Added to CISA KEV",
                           u=f'security/{v["id"]}.html', cta="What to patch", img="og/security.png", c="c3"))
    slides.append(dict(k=f'New recipe · {r["category"]}', t=r["title"], s=first(r["problem"]), d=r.get("created") or r.get("updated"), dl="Published",
                       u=f'recipes/{r["id"]}.html', cta="Open the recipe", img=f'og/cat-{OG_CATS.get(r["category"], "copilot")}.png', c="c2"))
    slides.append(dict(k="Quick guide · 1 page + PDF", t=Q.TITLE, s="Base licenses, mailboxes, update channel, network and oversharing: a pre-flight check you can run in an afternoon.",
                       d=Q.VERIFIED, dl="Verified", u=f"guides/{Q.SLUG}.html", cta="Run the checks", img="og/quick-copilot-license-checks.png", c="c4"))
    slides.append(dict(k="Pillar guide", t=G2.TITLE, s=f"{len(G2.PHASES)} phases: CIS Level 1 vs Level 2, Intune vs GPO, Credential Guard, ASR, BitLocker and compliance scans.",
                       d=G2.VERIFIED, dl="Verified", u=f"guides/{G2.SLUG}.html", cta="Read the guide", img="og/guide-windows-11-cis-hardening.png", c="c5"))
    return slides


def carousel(rel, slides, n_recipes, last_verified, top=""):
    n = len(slides)
    items, dots = "", ""
    for i, s in enumerate(slides):
        load = 'fetchpriority="high"' if i == 0 else 'loading="lazy"'
        items += (f'<div class="car-s car-{s["c"]}" role="group" aria-roledescription="slide" aria-label="{i + 1} of {n}: {esc(s["t"])}" id="car-s{i}">'
                  f'<div class="car-tx"><p class="car-k">{esc(s["k"])}</p><h2 class="car-t"><a href="{rel}{s["u"]}">{esc(s["t"])}</a></h2>'
                  f'<p class="car-sum">{esc(s["s"])}</p><p class="car-m">{T.icon("clock")}{esc(s["dl"])} <time datetime="{s["d"]}">{T.fmt(s["d"])}</time></p>'
                  f'<a class="btn hx-p car-cta" href="{rel}{s["u"]}" tabindex="-1" aria-hidden="true">{esc(s["cta"])} →</a></div>'
                  f'<a class="car-img" href="{rel}{s["u"]}" tabindex="-1" aria-hidden="true"><img src="{rel}assets/{s["img"]}" alt="" width="1200" height="630" {load}></a></div>')
        dots += f'<button type="button" class="car-dot" aria-controls="car-s{i}" aria-label="Show slide {i + 1}: {esc(s["t"])}"{" aria-current=true" if i == 0 else ""}></button>'
    arrow = lambda d: f'<svg viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><path d="{"M15 5l-7 7 7 7" if d < 0 else "M9 5l7 7-7 7"}"/></svg>'
    return (f'<section class="hx car" aria-labelledby="hx-title"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i><i class="o3"></i></div>'
            f'<div class="wrap"><h1 id="hx-title" class="car-h1">Fact-checked Copilot, Intune &amp; security recipes for Microsoft 365 admins</h1>'
            f'<p class="hx-badge car-badge"><span class="dot" aria-hidden="true"></span>{n_recipes} recipes, every one checked against its sources · last verified {T.fmt(last_verified)}</p>{top}'
            f'<div class="car-box" aria-roledescription="carousel" aria-label="Featured articles" role="region">'
            f'<div class="car-vp" id="car-vp" aria-live="off" tabindex="-1">{items}</div>'
            f'<div class="car-ctl"><button type="button" class="car-nav car-prev" aria-label="Previous slide" aria-controls="car-vp">{arrow(-1)}</button>'
            f'<div class="car-dots" role="group" aria-label="Choose slide">{dots}</div>'
            f'<button type="button" class="car-nav car-next" aria-label="Next slide" aria-controls="car-vp">{arrow(1)}</button>'
            f'<button type="button" class="car-play" aria-label="Pause automatic slide show" hidden>'
            f'<svg class="car-pi" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><path class="pp-pause" d="M8 5v14M16 5v14"/><path class="pp-play" d="M8 5l11 7-11 7z"/></svg></button></div></div></div></section>')
