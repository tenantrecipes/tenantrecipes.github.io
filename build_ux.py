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
    """Curated 'related' ids first (data/recipes/<id>.json), then scored by shared tags, category, guide phase and topic cluster."""
    import build_links as BL
    byid = {x["id"]: x for x in R}
    explicit = [byid[i] for i in r.get("related", []) if i in byid][:n]
    mine = set(tags_for(r))
    phases = {(g.SLUG, i) for g, i, j, ph, st in refs.get(r["id"], [])}
    scored = []
    for x in R:
        if x["id"] == r["id"] or x in explicit:
            continue
        s = 2 * len(mine & set(tags_for(x))) + (3 if x["category"] == r["category"] else 0) + BL.score(r, x)
        s += 4 * len(phases & {(g.SLUG, i) for g, i, j, ph, st in refs.get(x["id"], [])})
        if s:
            scored.append((s, x.get("order", 0), x))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return explicit + [x for _, _, x in scored[:n - len(explicit)]]


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
    if r.get("troubleshooting"):
        import build_markers as MK
        out += ["", "## Troubleshooting"] + [f"- {MK.ts_text(t, lambda x: x)}" for t in r["troubleshooting"]]
    if r.get("rollback"):
        out += ["", "## Rollback"] + [f"- [ ] {i}. {s}" for i, s in enumerate(r["rollback"], 1)]
    if r.get("tested"):
        out += ["", f'Tested configuration: {r["tested"]["environment"]}, {r["tested"]["date"]}']
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
    def wh(src):
        try:
            from PIL import Image
            import pathlib
            with Image.open(pathlib.Path(__file__).resolve().parent / src) as im:
                return f' width="{im.width}" height="{im.height}"'
        except Exception:
            return ""
    figs = "".join(f'<figure class="shot"><img src="{rel}{esc(s["src"])}" alt="{esc(s["alt"])}"{wh(s["src"])} loading="lazy" decoding="async">'
                   f'<figcaption>{esc(s["caption"])} <span class="fine">Screenshot taken {T.fmt(s["date"])}. Portal labels may have changed since.</span></figcaption></figure>'
                   for s in shots)
    return f'<section class="shots" aria-label="Screenshots">{figs}</section>'


# ---------------------------------------------------------------- newsletter CTA
def news_mid(rel, source):
    u = esc(C.BUTTONDOWN_USERNAME)
    return (f'<aside class="nm" aria-label="Newsletter"><div class="nm-t"><p class="nm-h">Get changes like this in your inbox</p>'
            f'<p>The Tenant Recipes Weekly Brief: 3 Microsoft changes, 2 security updates, 1 configuration tip and 1 thing to review in your tenant. 5 minutes, no fluff. '
            f'<a href="{rel}newsletter-sample.html">See a sample issue</a>.</p></div>'
            f'<form class="bd-form" action="https://buttondown.com/api/emails/embed-subscribe/{u}" method="post" target="_blank">'
            f'<label class="sr" for="nm-{source}">Email address</label>'
            f'<input id="nm-{source}" type="email" name="email" required autocomplete="email" placeholder="you@company.com">'
            f'<input type="hidden" name="embed" value="1"><input type="hidden" name="metadata__source" value="mid-{esc(source)}">'
            f'<button class="btn p" type="submit">Subscribe</button></form></aside>')


# ---------------------------------------------------------------- homepage finder + Start here
PROBLEM_IDS = ["ca-production-lockout-mistakes", "intune-devices-stay-noncompliant", "pim-least-privilege-daily-ops"]  # problem-oriented articles


def finder(rel, R, guides, quick, n_sec):
    G1, G2 = guides[0], guides[1]
    chips = "".join(f'<a class="chip" href="?t={E(t.replace(" ", "+"))}#library" data-tag="{esc(t)}">{esc(t)} <span>{n}</span></a>'
                    for t, n in tag_counts(R))
    newest = sorted((r for r in R if r["id"] not in PROBLEM_IDS), key=lambda r: (r.get("created", ""), r.get("updated", "")), reverse=True)[:3]
    new_li = "".join(f'<li><a href="{rel}recipes/{r["id"]}.html">{esc(r["title"])}</a></li>' for r in newest)
    nsteps = lambda g: sum(len(p["steps"]) for p in g.PHASES)
    byid = {r["id"]: r for r in R}
    prob_li = "".join(f'<li><a href="{rel}recipes/{i}.html">{esc(byid[i]["title"])}</a></li>' for i in PROBLEM_IDS if i in byid)
    cards = (
        f'<a class="sh-c sh-1" href="{rel}guides/{G1.SLUG}.html"><span class="sh-k">{T.icon("shield")}Start here · pillar guide</span>'
        f'<strong>Secure Copilot rollout</strong><p>{len(G1.PHASES)} phases, {nsteps(G1)} steps, from licensing to oversharing clean-up and pilot.</p>'
        f'<span class="sh-go">Open the guide {T.icon("arrow")}</span></a>'
        f'<a class="sh-c sh-2" href="{rel}guides/{G2.SLUG}.html"><span class="sh-k">{T.icon("layers")}Pillar guide</span>'
        f'<strong>Windows 11 hardening</strong><p>{len(G2.PHASES)} phases built around the CIS Benchmark and Microsoft security baselines.</p>'
        f'<span class="sh-go">Open the guide {T.icon("arrow")}</span></a>'
        + (f'<div class="sh-c sh-3"><span class="sh-k">{T.icon("alert")}When it breaks</span><ul>{prob_li}</ul>'
           f'<a class="sh-go" href="{rel}?t=Security#library">All security recipes {T.icon("arrow")}</a></div>' if prob_li else "")
        + f'<div class="sh-c sh-4"><span class="sh-k">{T.icon("clock")}Newest recipes</span><ul>{new_li}</ul>'
        f'<a class="sh-go" href="{rel}guides/{quick.SLUG}.html">Quick guide: {esc(quick.SHORT.split(": ", 1)[-1])} {T.icon("arrow")}</a></div>')
    return (f'<section class="fd wrap" id="find" aria-labelledby="fd-k"><p class="sec-k fd-k" id="fd-k">Start here</p><div class="sh">{cards}</div></section>')


def search_bar(rel, R, n_sec):
    """Prominent search + topic filter at the top of the homepage hero, with News/retirements and What's new entry points."""
    news = [t for t, _ in tag_counts(R) if t.lower().startswith("news")]
    chips = "".join(f'<a class="chip" href="?t={E(t.replace(" ", "+"))}#library" data-tag="{esc(t)}">{esc(t)} <span>{n}</span></a>'
                    for t, n in tag_counts(R) if t not in news)
    lead = ""
    if news:
        nt = news[0]
        lead += f'<a class="chip chip-hi" href="{rel}news/index.html">{T.icon("alert")}News &amp; retirements</a>'
    lead += f'<a class="chip chip-hi" href="{rel}changelog/">{T.icon("clock")}What\'s new</a>'
    lead += f'<a class="chip chip-hi" href="{rel}security/index.html#watch">{T.icon("shield")}Vulnerability watch</a>'
    lead += f'<a class="chip chip-hi" href="{rel}tools/index.html">{T.icon("target")}Security tools</a>'
    lead += f'<a class="chip chip-hi" href="{rel}policies/index.html">{T.icon("list")}Policy templates</a>'
    return (f'<div class="hx-find"><form class="fd-s" action="{rel}search/index.html" method="get" role="search">{T.icon("search")}'
            f'<label class="sr" for="fd-q">Search all recipes, guides and security entries</label>'
            f'<input id="fd-q" name="q" type="search" placeholder="Search recipes, CVEs…" data-ph-wide="Search recipes, guides, CVEs and news: e.g. MFA, Citrix, oversharing" autocomplete="off" data-sx>'
            f'<button class="btn p" type="submit">Search</button></form>'
            f'<div class="fd-tags fd-quick" role="navigation" aria-label="Quick links">{lead}</div>'
            f'<div class="fd-tags fd-topics" role="navigation" aria-label="Browse recipes by topic"><span class="fd-l">Topics:</span>{chips}</div></div>')


# ---------------------------------------------------------------- quick guide page
def quick_body(rel, Q, RID, page_signup):
    import build_history as HI
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
                        f'<a class="tier tier-technical" href="{rel}guides/index.html#tier-technical">Technical guide</a> {T.icon("check")}Quick guide · 1 page', esc(Q.TITLE),
                        "A pre-flight check you can run in an afternoon. Each item links to the Microsoft Learn page it was checked against "
                        "and to our hands-on recipe.",
                        T.chip("check", f"Verified {T.fmt(Q.VERIFIED)}") + T.chip("link", f"{len(allsrc)} Microsoft sources") + T.chip("list", "Printable PDF"), kind="page")
            + f'<main class="wrap pg"><article class="doc qg">'
            + HI.dates_bar(Q.PUBLISHED, getattr(Q, "UPDATED", None) or Q.VERIFIED, Q.VERIFIED)
            + HI.sources_top([(Q.S[k][0], Q.S[k][1], "") for k in allsrc], "Sources", note="Every check below was compared with these Microsoft Learn pages.") +
            f'<div class="rx"><a class="btn p rx-b" href="{pdf}" download>{T.icon("book")}<span>Download the 1-page PDF</span></a>'
            f'<button class="btn rx-b" type="button" data-print="1">{T.icon("list")}<span>Print</span></button></div>'
            f'<ol class="qg-l">{items}</ol>'
            f'<section class="co co-info"><p class="co-h">{T.icon("arrow")}{esc(th["t"])}</p><p>{esc(th["text"])}</p><div class="gd-recs">{recs(th["rec"])}</div></section>'
            + news_mid(rel, "quick-" + Q.SLUG) + T.author_box(rel)
            + HI.history_html(f"guides/{Q.SLUG}.html", Q.PUBLISHED, getattr(Q, "UPDATED", None) or Q.VERIFIED, Q.VERIFIED, getattr(Q, "HISTORY", ())) +
            f'<section class="vs" id="verified"><h2>Verification &amp; corrections</h2><p class="fine">Every item was checked against these Microsoft Learn pages on '
            f'<strong>{T.fmt(Q.VERIFIED)}</strong>. The wording is ours: always confirm against the source before you act.</p>'
            f'<ul class="vs-l">{srcs(allsrc)}</ul><div class="vs-f"><p>Spotted something wrong or outdated?</p>'
            f'{T.report_link(f"guides/{Q.SLUG}.html", Q.TITLE, "rp btn")}</div></section>'
            f'<p>Want the full picture? Read <a href="{rel}guides/secure-copilot-rollout.html">the secure Copilot rollout guide</a>.</p>'
            f'</article></main>' + page_signup)


# ---------------------------------------------------------------- sample newsletter issue
def sample_issue_body(rel, R, CY, guides, NEWS=()):
    """A clearly labelled example issue in the fixed Weekly Brief format (NEWSLETTER.md), assembled only from pages
    already published (and fact-checked) on the site: 3 Microsoft changes, 2 security updates, 1 tip, 1 thing to review."""
    rid = {r["id"]: r for r in R}
    changes = [("news/" + n["id"] + ".html", n["title"], n["summary"], (n.get("todo") or [""])[0])
               for n in sorted(NEWS, key=lambda n: (n.get("date", ""), n["id"]), reverse=True)]
    if len(changes) < 3:
        news = sorted([r for r in R if "News / Retirement" in tags_for(r)], key=lambda r: (r.get("created", ""), r["id"]), reverse=True)
        changes += [("recipes/" + r["id"] + ".html", r["title"], r["problem"], "") for r in news]
    changes = changes[:3]
    vulns = sorted([e for e in CY if e["type"] == "vulnerability" and e.get("exploited")],
                   key=lambda e: (e.get("vendor") == "Microsoft", e.get("kev_added") or e.get("advisory_date") or ""), reverse=True)[:2]
    tip = rid.get("ca-break-glass") or R[0]
    review = rid.get("pim-least-privilege-daily-ops") or rid.get("purview-audit-copilot") or R[-1]
    first = lambda t: (t.split(". ")[0].rstrip(".") + ".") if t else ""
    def li(href, title, text, label="", action=""):
        act = f' <strong>{label}</strong> {esc(action)}' if action else ""
        return f'<li><a href="{href}"><strong>{esc(title)}</strong></a> {esc(first(text))}{act}</li>'
    return (T.page_hero(rel, T.crumbs_dark(rel, "newsletter-sample.html", [("Home", rel + "index.html"), ("Newsletter", rel + "newsletter.html"), ("Sample issue", None)]),
                        "Newsletter · example", "What the Weekly Brief looks like",
                        "A sample issue in the fixed weekly format, assembled from pages already published on this site, so you can see it before you subscribe.", kind="page")
            + '<main class="wrap pg"><article class="doc nl">'
            '<p class="nl-flag" role="note"><strong>Example issue.</strong> This page shows the format only. It was not sent to anyone, '
            'and every item links to a fact-checked page on Tenant Recipes, where you will find the Microsoft or vendor sources.</p>'
            f'<div class="nl-mail"><p class="nl-meta">From: Tenant Recipes · Subject: <strong>The Tenant Recipes Weekly Brief</strong> · 5-minute read</p>'
            '<h2>3 Microsoft changes you should know</h2><ol>'
            + "".join(li(rel + u, t, s, "Do:", d) for u, t, s, d in changes) + '</ol>'
            + ('<h2>2 security updates worth investigating</h2><ol>'
               + "".join(li(f'{rel}security/{e["id"]}.html', e["title"], e["summary"], "Check first:", first(e.get("action") or "")) for e in vulns) + '</ol>' if vulns else "")
            + f'<h2>1 practical configuration tip</h2><p><a href="{rel}recipes/{tip["id"]}.html"><strong>{esc(tip["title"])}</strong></a>. {esc(tip["problem"])} '
            'The recipe has the steps, a check that it worked and the rollback.</p>'
            f'<h2>1 thing to review in your tenant</h2><p><a href="{rel}recipes/{review["id"]}.html"><strong>{esc(review["title"])}</strong></a>. {esc(first(review["problem"]))}</p>'
            '<p class="fine">You get this because you subscribed on tenantrecipes.com. One click to unsubscribe in every real issue.</p></div>'
            '</article></main>')


# ---------------------------------------------------------------- Open Graph image per page
OG_CATS = {
    "Copilot rollout & governance": "copilot", "Conditional Access for AI": "conditional-access", "Intune & devices for AI": "intune",
    "Purview, DLP & data security for Copilot": "purview", "Identity & threat protection": "identity",
    "Agents & Copilot Studio governance": "agents", "Licensing & reporting": "licensing", "Admin prompt templates": "prompts",
}


# Per-page override: exact page path -> (image under assets/, alt text). Images are made by tools/make_shareables.py (og_specs).
OG_PAGES = {
    "code/ca-policy-generator.html": ("og/tool-ca-policy-generator.png", "Tenant Recipes: Conditional Access Policy Generator, Graph JSON and PowerShell, report-only by default"),
    "tools/mail-dns-checker.html": ("og/tool-mail-dns-checker.png", "Tenant Recipes: Mail DNS Checker for SPF, DKIM, DMARC, MTA-STS and CAA, graded A to F"),
}


def og_image(path, RID):
    """Return (file under assets/, alt text)."""
    if path in OG_PAGES:
        return OG_PAGES[path]
    if path.startswith("recipes/"):
        r = RID.get(path[8:-5])
        if r:
            return f'og/cat-{OG_CATS.get(r["category"], "copilot")}.png', f'Tenant Recipes: {r["category"]}'
    if path.startswith("guides/secure-copilot-rollout"):
        return "og/guide-secure-copilot-rollout.png", "Tenant Recipes guide: secure Copilot rollout"
    if path.startswith("guides/windows-11-cis-hardening"):
        return "og/guide-windows-11-cis-hardening.png", "Tenant Recipes guide: Windows 11 hardening with the CIS Benchmark"
    if path.startswith("guides/cloud-hardening-adversary-emulation"):
        return "og/guide-cloud-hardening-adversary-emulation.png", "Tenant Recipes guide: cloud hardening under attack simulation"
    if path.startswith("guides/azure-update-manager-enterprise-patching"):
        return "og/guide-azure-update-manager-enterprise-patching.png", "Tenant Recipes guide: Azure Update Manager at enterprise scale"
    if path.startswith("guides/azure-arc-onboarding-enterprise-scale"):
        return "og/guide-azure-arc-onboarding-enterprise-scale.png", "Tenant Recipes guide: Azure Arc onboarding at enterprise scale"
    if path.startswith("guides/admin-by-request-endpoint-privilege"):
        return "og/guide-admin-by-request-endpoint-privilege.png", "Tenant Recipes guide: remove local admin rights with Admin By Request"
    if path.startswith("guides/entra-private-access-vpn-replacement"):
        return "og/guide-entra-private-access-vpn-replacement.png", "Tenant Recipes guide: replace VPN with Entra Private Access"
    if path.startswith("guides/adcs-hardening-tier0"):
        return "og/guide-adcs-hardening-tier0.png", "Tenant Recipes guide: harden AD CS as Tier 0"
    if path.startswith("guides/purple-team-hybrid-identity"):
        return "og/guide-purple-team-hybrid-identity.png", "Tenant Recipes guide: internal purple team to hybrid identity"
    if path.startswith("guides/external-attack-surface-osint"):
        return "og/guide-external-attack-surface-osint.png", "Tenant Recipes guide: map your external attack surface"
    if path.startswith("guides/admin-by-request-intune-win32-packaging"):
        return "og/guide-admin-by-request-intune-win32-packaging.png", "Tenant Recipes guide: package Admin By Request for Intune"
    if path.startswith("guides/copilot-license-checks"):
        return "og/quick-copilot-license-checks.png", "Tenant Recipes quick guide: 5 checks before Copilot licenses"
    if path.startswith("guides/"):
        return "og/guides.png", "Tenant Recipes guides"
    if path.startswith("security/"):
        return "og/security.png", "Tenant Recipes security: vulnerability watch and hardening"
    if path.startswith("newsletter"):
        return "og/newsletter.png", "The Tenant Recipes Weekly Brief"
    return "og-image.png", f"{C.SITE_NAME}: {C.SITE_TAGLINE}"


# ---------------------------------------------------------------- automatic per-page OG images
# Pages whose og_image() is only a generic section/category/default image get their own card
# (title + content type, site brand), made by tools/make_page_og.py and committed under assets/og/p/.
# Hand-made images (OG_PAGES, guide-*, quick guide, newsletter, home page) always win.
import hashlib as _hl, json as _json, pathlib as _pl, re as _re
_OG_GENERIC = _re.compile(r"^(og-image\.png|og/(cat-[a-z-]+|security|guides)\.png)$")
_OG_DIR = _pl.Path(__file__).resolve().parent / "assets" / "og" / "p"
OG_AUTO_VERSION = "1"   # bump to regenerate every auto card after a template change
OG_AUTO = {}            # path -> spec, filled during the build, written to .cache/og-pages.json
_OG_SECTIONS = {  # first path segment -> (label for a page, label for the section index, accent colour)
    "guides": ("Guide", "Guides", "#1f7bff"), "tools": ("Tool", "Tools", "#0f7a4f"), "code": ("Code", "Code Library", "#7a4dff"),
    "recipes": ("Recipe", "Recipes", "#1f7bff"), "security": ("Security", "Security", "#b3261e"), "policies": ("Policy", "Policies", "#0b6e99"),
    "news": ("News", "News", "#e39a1f"), "status": ("Status", "Status", "#0b6e99"), "author": ("About", "About", "#5b2c6f"),
    "contact": ("Contact", "Contact", "#5b2c6f"), "changelog": ("What's new", "What's new", "#e39a1f"), "search": ("Search", "Search", "#1f7bff"),
}


def og_auto_slug(path):
    return path[:-5].replace("/", "--")


def og_auto_hash(spec):
    return _hl.sha256(_json.dumps([OG_AUTO_VERSION, spec["kicker"], spec["title"], spec["accent"]]).encode()).hexdigest()[:16]


def _og_manifest():
    f = _OG_DIR / "manifest.json"
    return _json.loads(f.read_text()) if f.exists() else {}


def og_for(path, RID, title):
    """og_image() plus the automatic per-page card when only a generic image exists. Returns (file under assets/, alt)."""
    f, alt = og_image(path, RID)
    if path == "index.html" or not _OG_GENERIC.match(f):
        return f, alt
    t = title.split(" | ")[0].strip()
    seg = path.split("/")[0] if "/" in path else ""
    lab, idx_lab, accent = _OG_SECTIONS.get(seg, (C.SITE_NAME, C.SITE_NAME, "#7a4dff"))
    kicker = idx_lab if path.endswith("index.html") else lab
    if seg == "recipes" and path[8:-5] in RID:
        cat = RID[path[8:-5]]["category"]
        kicker = f"Recipe · {cat}"
    spec = {"path": path, "slug": og_auto_slug(path), "kicker": kicker, "title": t, "accent": accent}
    spec["hash"] = og_auto_hash(spec)
    OG_AUTO[path] = spec
    if _og_manifest().get(spec["slug"]) == spec["hash"] and (_OG_DIR / f'{spec["slug"]}.jpg').exists():
        return f'og/p/{spec["slug"]}.jpg', f"{C.SITE_NAME} {kicker.split(' · ')[0].lower()}: {t}"
    return f, alt   # card missing or stale (e.g. CI without Chrome): fall back to the generic image


def write_og_pages(root):
    d = _pl.Path(root) / ".cache"
    d.mkdir(exist_ok=True)
    (d / "og-pages.json").write_text(_json.dumps(sorted(OG_AUTO.values(), key=lambda s: s["path"]), indent=1))


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
    (r"^(code/(?!index)[^/]+|tools/mail-dns-checker)\.html$", r'<article class="doc[^"]*"><p class="pd">.*?</p>', r'</article>'),
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
    ms = [e for e in vulns if "Microsoft" in (e.get("vendor") or "")]  # homepage = Microsoft track; other vendors live in the second track
    v = max([e for e in ms if e.get("exploited")] or ms, key=vkey) if ms else None
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


def _webp(img):
    """WebP copies (1200w + 640w) of a carousel image, committed next to the PNG in assets/og/.
    Regenerated when the PNG is newer and Pillow is installed; without them the <picture> keeps only the PNG."""
    import pathlib
    png = pathlib.Path(__file__).resolve().parent / "assets" / img
    big, small = png.with_suffix(".webp"), png.with_name(png.stem + "-640.webp")
    try:
        from PIL import Image
        if png.exists() and (not big.exists() or big.stat().st_mtime < png.stat().st_mtime):
            with Image.open(png) as im:
                im = im.convert("RGB")
                im.save(big, "WEBP", quality=82, method=6)
                im.resize((640, round(640 * im.height / im.width)), Image.LANCZOS).save(small, "WEBP", quality=80, method=6)
    except ImportError:
        pass
    return big.exists() and small.exists()


def carousel(rel, slides, n_recipes, last_verified, top="", lead=""):
    n = len(slides)
    items, dots = "", ""
    for i, s in enumerate(slides):
        load = 'fetchpriority="high"' if i == 0 else 'loading="lazy"'
        items += (f'<div class="car-s car-{s["c"]}" role="group" aria-roledescription="slide" aria-label="{i + 1} of {n}: {esc(s["t"])}" id="car-s{i}">'
                  f'<div class="car-tx"><p class="car-k">{esc(s["k"])}</p><h2 class="car-t"><a href="{rel}{s["u"]}">{esc(s["t"])}</a></h2>'
                  f'<p class="car-sum">{esc(s["s"])}</p><p class="car-m">{T.icon("clock")}{esc(s["dl"])} <time datetime="{s["d"]}">{T.fmt(s["d"])}</time></p>'
                  f'<a class="btn hx-p car-cta" href="{rel}{s["u"]}" tabindex="-1" aria-hidden="true">{esc(s["cta"])} →</a></div>'
                  f'<a class="car-img" href="{rel}{s["u"]}" tabindex="-1" aria-hidden="true"><picture>'
                  # the image is hidden below 860px (CSS), so phones get a 1x1 placeholder instead of a 1200px PNG
                  f'<source media="(max-width: 860px)" srcset="data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==">'
                  + (f'<source type="image/webp" srcset="{rel}assets/{s["img"][:-4]}-640.webp 640w, {rel}assets/{s["img"][:-4]}.webp 1200w" sizes="(max-width: 1200px) 45vw, 540px">' if _webp(s["img"]) else "") +
                  f'<img src="{rel}assets/{s["img"]}" alt="" width="1200" height="630" decoding="async" {load}></picture></a></div>')
        dots += f'<button type="button" class="car-dot" aria-controls="car-s{i}" aria-label="Show slide {i + 1}: {esc(s["t"])}"{" aria-current=true" if i == 0 else ""}></button>'
    arrow = lambda d: f'<svg viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><path d="{"M15 5l-7 7 7 7" if d < 0 else "M9 5l7 7-7 7"}"/></svg>'
    return (f'<section class="hx car" aria-labelledby="hx-title"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i><i class="o3"></i></div>'
            f'<div class="wrap"><h1 id="hx-title" class="car-h1">Independent Microsoft Cloud &amp; Modern Workplace playbooks</h1><p class="car-sub">Identity, devices, Copilot and automation for people who run tenants: exact settings, scripts, rollback and a source for every claim. <a href="#tasks">Explore by task ↓</a> · <a href="#infra">Cybersecurity &amp; Infrastructure track</a></p>{lead}'
            f'<p class="hx-badge car-badge"><span class="dot" aria-hidden="true"></span>{n_recipes} recipes, every one checked against its sources · last verified {T.fmt(last_verified)}</p>{top}'
            f'<div class="car-box" aria-roledescription="carousel" aria-label="Featured articles" role="region">'
            f'<div class="car-vp" id="car-vp" aria-live="off" tabindex="-1">{items}</div>'
            f'<div class="car-ctl"><button type="button" class="car-nav car-prev" aria-label="Previous slide" aria-controls="car-vp">{arrow(-1)}</button>'
            f'<div class="car-dots" role="group" aria-label="Choose slide">{dots}</div>'
            f'<button type="button" class="car-nav car-next" aria-label="Next slide" aria-controls="car-vp">{arrow(1)}</button>'
            f'<button type="button" class="car-play" aria-label="Pause automatic slide show" hidden>'
            f'<svg class="car-pi" viewBox="0 0 24 24" width="1em" height="1em" aria-hidden="true"><path class="pp-pause" d="M8 5v14M16 5v14"/><path class="pp-play" d="M8 5l11 7-11 7z"/></svg></button></div></div></div></section>')


# ---------------------------------------------------------------- homepage task hubs (2026-10-31)
def task_hubs(rel, R, guides, quick, CYL, tools, pols):
    """'What are you trying to solve?': four task hubs that deep-link into existing content. Counts computed from data."""
    from urllib.parse import quote_plus as qp
    G1, G2 = guides[0], guides[1]
    G3 = guides[2] if len(guides) > 2 else None
    G4 = guides[3] if len(guides) > 3 else None
    G5 = guides[4] if len(guides) > 4 else None
    GABR = next((g for g in guides if g.SLUG == "admin-by-request-endpoint-privilege"), None)
    GABRP = next((g for g in guides if g.SLUG == "admin-by-request-intune-win32-packaging"), None)
    GPA = next((g for g in guides if g.SLUG == "entra-private-access-vpn-replacement"), None)
    GADCS = next((g for g in guides if g.SLUG == "adcs-hardening-tier0"), None)
    GPTH = next((g for g in guides if g.SLUG == "purple-team-hybrid-identity"), None)
    GEAS = next((g for g in guides if g.SLUG == "external-attack-surface-osint"), None)
    tc = dict(tag_counts(R))
    tag = lambda t: f'{rel}?t={qp(t)}#library'
    exploited = sum(1 for e in CYL if e["type"] == "vulnerability" and e.get("exploited"))
    m365_tools = sum(1 for e in tools if e["category"] in ("M365 & Entra", "Cloud assessment"))
    ai_n = sum(1 for r in R if {"Copilot", "Agents", "Licensing", "Prompts"} & set(tags_for(r)))
    sec_n = sum(1 for r in R if {"Conditional Access", "Identity", "Purview & DLP", "Security"} & set(tags_for(r)))
    pid = {p["id"] for p in pols}
    ap_n = sum(1 for r in R if "autopilot" in r["title"].lower())
    L = lambda u, t, n=None: f'<li><a href="{u}">{t}' + (f' <span>{n}</span>' if n else "") + '</a></li>'
    hubs = [
        ("shield", "Secure", "Identity, Conditional Access, Defender, Purview",
         "Close sign-in gaps, stop oversharing and patch what is being exploited.",
         ([L(f'{rel}guides/{G3.SLUG}.html', "Cloud hardening + adversary emulation")] if G3 else [])
         + ([L(f'{rel}guides/{GPA.SLUG}.html', "Replace VPN with Entra Private Access")] if GPA else [])
         + ([L(f'{rel}guides/{GADCS.SLUG}.html', "Harden AD CS as Tier 0")] if GADCS else [])
         + ([L(f'{rel}guides/{GPTH.SLUG}.html', "Purple team: network to hybrid identity")] if GPTH else [])
         + ([L(f'{rel}guides/{GEAS.SLUG}.html', "Map external attack surface (OSINT)")] if GEAS else [])
         + [L(tag("Conditional Access"), "Conditional Access", tc.get("Conditional Access")),
          L(tag("Identity"), "Identity &amp; threat protection", tc.get("Identity")),
          L(tag("Purview & DLP"), "Purview &amp; DLP", tc.get("Purview & DLP")),
          L(f'{rel}recipes/ca-production-lockout-mistakes.html', "CA mistakes that cause lockouts") if any(r["id"] == "ca-production-lockout-mistakes" for r in R) else "",
          L(f'{rel}policies/index.html', "Security policy templates", len(pols))],
         (f'{rel}guides/{G3.SLUG}.html' if G3 else f'{rel}?t=Security#library'),
         ("Open the cloud hardening guide" if G3 else f"All {tc.get('Security', sec_n)} security recipes")),
        ("layers", "Manage", "Intune, Windows, Autopilot, devices",
         "Autopilot provisioning, compliance baselines, hardened Windows 11 and clean joiner/leaver handling.",
         [L(tag("Intune"), "Intune &amp; device recipes", tc.get("Intune"))]
         + ([L(f'{rel}search/index.html?q=Autopilot', "Windows Autopilot", ap_n)] if ap_n else [])
         + ([L(f'{rel}guides/{G5.SLUG}.html', "Onboard servers to Azure Arc")] if G5 else [])
         + ([L(f'{rel}guides/{G4.SLUG}.html', "Server patching with Azure Update Manager")] if G4 else [])
         + ([L(f'{rel}guides/{GABR.SLUG}.html', "Remove local admin rights (Admin By Request)")] if GABR else [])
         + ([L(f'{rel}guides/{GABRP.SLUG}.html', "Package Admin By Request for Intune (Win32)")] if GABRP else [])
         + [L(f'{rel}guides/{G2.SLUG}.html', "Windows 11 CIS hardening guide"),
          L(f'{rel}security/endpoint.html', "Endpoint &amp; client security"),
          L(f'{rel}security/harden-windows-laps.html', "Windows LAPS hardening")]
         + ([L(f'{rel}policies/onboarding-checklist.html', "Joiner / leaver checklists")] if "onboarding-checklist" in pid else []),
         f'{rel}guides/{G2.SLUG}.html', "Open the Windows 11 guide"),
        ("target", "Deploy AI", "Copilot, agents, governance",
         "License, scope and govern Copilot and Copilot Studio agents before users find the gaps.",
         [L(f'{rel}guides/{G1.SLUG}.html', "Secure Copilot rollout guide"),
          L(f'{rel}guides/{quick.SLUG}.html', "Copilot pre-flight checks"),
          L(tag("Copilot"), "Copilot recipes", tc.get("Copilot")),
          L(tag("Agents"), "Agents &amp; Copilot Studio", tc.get("Agents")),
          L(tag("Licensing"), "Licensing &amp; reporting", tc.get("Licensing"))]
         + ([L(f'{rel}policies/ai-copilot-use-policy.html', "AI use policy template")] if "ai-copilot-use-policy" in pid else []),
         f'{rel}guides/{G1.SLUG}.html', "Start with the rollout guide"),
        ("list", "Automate", "PowerShell, Graph, scripts, tools",
         "Copy-paste PowerShell and Graph, plus assessment and pentest tooling for the tenant and beyond.",
         [L(f'{rel}code/index.html', "Code Library: copy-ready snippets", len(list((__import__("pathlib").Path(__file__).resolve().parent / "data" / "code").glob("*.json"))) or None),
          L(tag("PowerShell & Graph"), "PowerShell &amp; Graph recipes", tc.get("PowerShell & Graph")),
          L(tag("Prompts"), "Admin prompt templates", tc.get("Prompts")),
          L(f'{rel}tools/index.html?f=m365-entra#tools', "M365 &amp; Entra assessment tools", m365_tools or None),
          L(f'{rel}tools/index.html', "All security &amp; pentest tools", len(tools))]
         + ([L(f'{rel}guides/{G3.SLUG}.html', "Project: chain the M365/Entra tools")] if G3 else []),
         f'{rel}tools/index.html', "Open the tools"),
    ]
    cards = "".join(
        f'<div class="tk-c tk-{i}"><p class="sh-k">{T.icon(ic)}{esc(k)}</p><h3>{esc(scope)}</h3><p class="tk-d">{esc(d)}</p>'
        f'<ul class="tk-l">{"".join(li)}</ul><a class="sh-go" href="{go}">{esc(gol)} {T.icon("arrow")}</a></div>'
        for i, (ic, k, scope, d, li, go, gol) in enumerate(hubs, 1))
    return (f'<section class="tk-hub wrap" id="tasks" aria-labelledby="tk-h"><p class="sec-k">Microsoft Cloud &amp; Modern Workplace · explore by task</p>'
            f'<h2 id="tk-h">What are you trying to solve?</h2><div class="tk-g">{cards}</div>'
            + _tier_strip(rel, R, guides, quick) + '</section>')


def _tier_strip(rel, R, guides, quick):
    """Three content levels with live counts, linking to the sections on /guides/."""
    import build_tiers as TR
    n = {"pillar": 0, "technical": 0, "recipe": len(R)}
    for g in list(guides) + [quick]:
        n[TR.guide_tier(g)] += 1
    return ('<p class="tk-tiers"><span class="fine">Three levels:</span>'
            + "".join(f'<a href="{rel}guides/index.html#tier-{t}"><span class="tier tier-{t}">{TR.TIERS[t][1]}</span> {n[t]}</a>'
                      for t in ("pillar", "technical", "recipe")) + '</p>')


# ---------------------------------------------------------------- homepage second track (2026-10-31)
def infra_track(rel, CYL, tools, pols):
    """Compact, clearly secondary band: Cybersecurity & Infrastructure (non-Microsoft CVEs, hardening, tools, templates)."""
    vk = lambda e: e.get("kev_added") or e.get("advisory_date") or ""
    other = sorted((e for e in CYL if e["type"] == "vulnerability" and e.get("exploited") and "Microsoft" not in (e.get("vendor") or "")), key=vk, reverse=True)
    expl = sum(1 for e in CYL if e["type"] == "vulnerability" and e.get("exploited"))
    hard = sum(1 for e in CYL if e["type"] == "hardening")
    L = lambda u, t, n: f'<li><a href="{rel}{u}">{t} <span>{n}</span></a></li>'
    latest = " · ".join(f'<a href="{rel}security/{e["id"]}.html">{esc((e.get("vendor") or "").split(" (")[0])} {esc(e["cves"][0]["id"] if e.get("cves") else "")}</a>' for e in other[:3])
    return (f'<section class="t2 wrap" id="infra" aria-labelledby="t2-h"><div class="t2-in"><div class="t2-tx"><p class="sec-k t2-k">Second track</p>'
            f'<h2 id="t2-h">Cybersecurity &amp; Infrastructure</h2><p>Beyond the tenant: exploited CVEs in network, server and virtualisation products, '
            f'hardening baselines, pentest tooling and policy templates.</p>'
            + (f'<p class="t2-new fine">Latest exploited: {latest}</p>' if latest else "") +
            f'</div><ul class="t2-l">{L("security/index.html#watch", "Vulnerability watch", expl)}{L("security/index.html#hardening", "Hardening recipes", hard)}'
            f'{L("tools/index.html", "Security &amp; pentest tools", len(tools))}{L("policies/index.html", "Policy templates", len(pols))}</ul></div></section>')
