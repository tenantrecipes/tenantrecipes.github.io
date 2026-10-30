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
