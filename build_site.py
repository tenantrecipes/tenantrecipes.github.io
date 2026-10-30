"""Generate the static site into dist/ from data/recipes.json + site_config.py.
All internal links and assets are relative, so dist/ works on a free subdomain or a sub-path
(e.g. https://user.github.io/tenantrecipes/). Run via `python3 build.py`."""
import json, re, shutil, pathlib, sys, datetime
from html import escape as E
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import site_config as C
sys.path.insert(0, str(ROOT / "data" / "guides"))
import secure_copilot_rollout as G1
import windows_11_cis_hardening as G2
GUIDES = [G1, G2]
import build_cyber as CY
import build_trust as T

DIST = ROOT / "dist"
R = json.load(open(ROOT / "data" / "recipes.json"))
TODAY = datetime.date.today().isoformat()
BD_PLACEHOLDER = C.BUTTONDOWN_USERNAME in ("", "BUTTONDOWN_USERNAME")
SITE = C.SITE_URL.rstrip("/")


def esc(s):  # match the original site's escaping style
    return E(s, quote=True)


def step_html(s):
    """Text between `backticks` in a recipe step is rendered as <code> (e.g. PowerShell)."""
    parts = s.split("`")
    out = []
    for i, p in enumerate(parts):
        if i % 2 == 0:
            out.append(esc(p))
        elif len(p) >= 40 and " " in p:  # commands / queries: block with copy button (added by assets/ui.js)
            out.append(f'<pre class="cb"><code>{esc(p)}</code></pre>')
        else:
            out.append(f"<code>{esc(p)}</code>")
    return "".join(out)


def head(title, desc, rel, path, og_type="website"):
    url = f"{SITE}/{path}" if SITE else ""
    img = f"{SITE}/assets/og-image.png" if SITE else f"{rel}assets/og-image.png"
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml">',
        f'<link rel="icon" href="{rel}favicon.ico" sizes="any">',
        f'<link rel="apple-touch-icon" href="{rel}assets/apple-touch-icon.png">',
        '<meta name="theme-color" content="#0f2f6b">',
        f'<meta property="og:site_name" content="{esc(C.SITE_NAME)}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(C.SITE_NAME)}: {esc(C.SITE_TAGLINE)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{img}">',
    ]
    if url:
        tags += [f'<meta property="og:url" content="{url}">', f'<link rel="canonical" href="{url}">']
    tags.append(f'<link rel="alternate" type="application/atom+xml" title="{esc(C.SITE_NAME)}" href="{rel}feed.xml">')
    tags.append(f'<link rel="stylesheet" href="{rel}assets/style.css">')
    tags.append(f'<script src="{rel}assets/ui.js" defer></script>')
    return "".join(tags)


def nav(rel):
    return T.nav(rel)


def footer(rel):
    return T.footer(rel, G1.SLUG)


def ad_slot(name):
    """Empty sponsor slot. Hidden unless SHOW_AD_SLOTS = True in site_config.py. No ad code."""
    hidden = "" if C.SHOW_AD_SLOTS else " hidden"
    inner = '<span class="slot-label">Sponsor</span>' if C.SHOW_AD_SLOTS else ""
    return f'<aside class="sponsor-slot" data-slot="{name}" aria-label="Sponsor"{hidden}><!-- sponsor slot: {name} (empty) -->{inner}</aside>'


def signup(rel, source, heading=True):
    """Buttondown embed form. The username comes ONLY from site_config.BUTTONDOWN_USERNAME."""
    u = E(C.BUTTONDOWN_USERNAME)
    h = ('<h2>The weekly Tenant Recipes brief</h2><p>Every week: what changed in Copilot, Intune, Entra and Purview '
         '— and what you should do about it. 5 minutes, no fluff.</p>') if heading else ""
    guard = (' onsubmit="alert(\'Newsletter signup is not live yet: set BUTTONDOWN_USERNAME in site_config.py.\');return false"'
             if BD_PLACEHOLDER else "")
    note = ('<p class="todo">Not live yet: set BUTTONDOWN_USERNAME in site_config.py and rebuild.</p>'
            if BD_PLACEHOLDER else "")
    return (f'<section class="news" id="newsletter">{h}'
            f'<!-- Buttondown embed form. Username is set in site_config.py (BUTTONDOWN_USERNAME), nowhere else. -->'
            f'<form class="bd-form" action="https://buttondown.com/api/emails/embed-subscribe/{u}" method="post" target="_blank"{guard}>'
            f'<label class="sr" for="bd-email-{source}">Email address</label>'
            f'<input id="bd-email-{source}" type="email" name="email" required autocomplete="email" placeholder="you@company.com"> '
            f'<input type="hidden" name="embed" value="1">'
            f'<input type="hidden" name="metadata__source" value="{E(source)}">'
            f'<button class="btn p" type="submit">Subscribe</button></form>'
            f'<p class="fine">Free. Unsubscribe anytime. See the <a href="{rel}privacy.html">privacy policy</a>.</p>{note}</section>')


def page(path, title, desc, body, og_type="website"):
    rel = "../" * path.count("/")
    html = (f'<!doctype html><html lang="en"><head>{head(title, desc, rel, path, og_type)}</head><body>\n'
            f'{nav(rel)}{body(rel)}\n{footer(rel)}</body></html>\n')
    out = DIST / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return path


def contact_html():
    return T.contact_html()


SECURITY_TRACK = [  # (category, headline, blurb, preferred first recipe id) — counts and links are computed from data
    ("Conditional Access for AI", "Lock down sign-ins", "Phishing-resistant MFA, risk-based blocks and break-glass hygiene before AI scales.", "ca-require-mfa-copilot"),
    ("Purview, DLP & data security for Copilot", "Stop oversharing", "Find what Copilot can see, then fence it with labels, DLP and audit.", "purview-oversharing-assessment"),
    ("Intune & devices for AI", "Harden devices", "Compliant devices and app protection so AI only runs where it should.", "intune-compliance-baseline"),
    ("Identity & threat protection", "Stop identity attacks", "Passkeys before SMS retires, Microsoft-managed risk policies, guest access and Teams phishing.", "entra-sms-voice-retirement-passkeys"),
]


def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def hero(rel):
    """Homepage hero. Every number is computed from data/recipes.json at build time — nothing invented."""
    n = len(R)
    cats = sorted({r["category"] for r in R})
    sources = {s["url"] for r in R for s in r.get("sources", [])}
    last = max(r["last_verified"] for r in R if r.get("last_verified"))
    newest = sorted(R, key=lambda r: (r.get("updated", ""), r.get("created", ""), -r.get("order", 0)), reverse=True)[:4]
    ticker_items = "".join(f'<li><a href="recipes/{r["id"]}.html"><span>{esc(r["category"])}</span>{esc(r["title"])}</a></li>' for r in R)
    ticker_dupe = "".join(f'<li><a href="recipes/{r["id"]}.html" tabindex="-1"><span>{esc(r["category"])}</span>{esc(r["title"])}</a></li>' for r in R)
    checks = "".join(f'<li><a href="recipes/{r["id"]}.html"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.5l3.2 3.2L15 6.8"/></svg>'
                     f'<span>{esc(r["title"])}</span></a></li>' for r in newest)
    tiles = ""
    for cat, h, blurb, pick in SECURITY_TRACK:
        rs = [r for r in R if r["category"] == cat]
        if not rs:
            continue
        rs.sort(key=lambda r: r["id"] != pick)  # preferred recipe first, if it still exists
        tiles += (f'<a class="sec-tile" href="recipes/{rs[0]["id"]}.html"><span class="sec-n">{len(rs)}</span><span class="sec-l">recipes</span>'
                  f'<strong>{esc(h)}</strong><p>{esc(blurb)}</p><span class="sec-go">Start with: {esc(rs[0]["title"])} →</span></a>')
    sec_total = sum(1 for r in R if r["category"] in {t[0] for t in SECURITY_TRACK})
    return (
        f'<section class="hx" aria-labelledby="hx-title"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i><i class="o3"></i></div>'
        f'<div class="wrap hx-in"><div class="hx-copy">'
        f'<p class="hx-badge"><span class="dot" aria-hidden="true"></span>Every recipe fact-checked against Microsoft sources · last verified {fmt_date(last)}</p>'
        f'<h1 id="hx-title">Roll out Copilot.<br><span class="grad">Without opening a hole in your tenant.</span></h1>'
        f'<p class="hx-lead">Step-by-step AI &amp; security recipes for Microsoft 365 admins — Conditional Access, Intune, Purview, '
        f'Copilot Studio agents and licensing. The exact clicks, the pitfalls, and a link to Microsoft Learn for every claim.</p>'
        f'<div class="hx-cta"><a class="btn hx-p" href="guides/{G1.SLUG}.html">Read the rollout guide →</a>'
        f'<a class="btn hx-g" href="#library">Browse {n} recipes</a></div>'
        f'<p class="hx-note"><a href="guides/{G1.SLUG}.html"><strong>{len(G1.PHASES)} phases · {sum(len(p["steps"]) for p in G1.PHASES)} steps · printable checklist.</strong> '
        f'Starts where the real risk is: oversharing, EEEU, sharing links and guests.</a> · <a href="#newsletter">Free weekly brief</a></p>'
        f'<dl class="hx-stats"><div><dt>Recipes</dt><dd>{n}</dd></div><div><dt>Categories</dt><dd>{len(cats)}</dd></div>'
        f'<div><dt>Microsoft sources linked</dt><dd>{len(sources)}</dd></div><div><dt>Last verified</dt><dd>{fmt_date(last)}</dd></div></dl>'
        f'</div><div class="hx-art"><div class="hx-shield"><img src="{rel}assets/mark.svg" alt="" width="200" height="200"></div>'
        f'<div class="hx-card"><p class="hx-card-h"><span aria-hidden="true">●●●</span> tenant-check</p><ul>{checks}</ul>'
        f'<p class="hx-card-f">{n}/{n} recipes verified · {fmt_date(last)}</p></div></div></div>'
        f'<div class="ticker" aria-label="All recipes"><ul class="tk">{ticker_items}</ul><ul class="tk" aria-hidden="true">{ticker_dupe}</ul></div>'
        f'</section>'
        f'<section class="sec wrap" aria-labelledby="sec-title"><p class="sec-k">Security track</p>'
        f'<h2 id="sec-title">AI is only as safe as your tenant. {sec_total} recipes to harden it first.</h2>'
        f'<div class="sec-grid">{tiles}</div>'
        f'<a class="cy-promo" href="security/index.html"><span class="cy-promo-k">New</span><strong>Cybersecurity beyond the tenant:</strong> '
        f'vulnerability watch for exploited CVEs, plus hardening for network, servers and VMware →</a>'
        f'<a class="cy-promo" href="guides/{G2.SLUG}.html"><span class="cy-promo-k">New guide</span><strong>{esc(G2.TITLE)}:</strong> '
        f'{len(G2.PHASES)} phases from CIS Level 1 vs Level 2 to Credential Guard, ASR, BitLocker and compliance scans →</a></section>'
    )


def _txt(s):
    return step_html(s)


def guide_page(g):
    RID = {r["id"]: r for r in R}
    SEC = {e["id"]: e for e in CY.load()}
    SL = getattr(g, "SRC_LABEL", "Microsoft sources")
    for ph in g.PHASES:
        for st in ph["steps"]:
            for rid in st["rec"]:
                if rid not in RID:
                    sys.exit(f"Guide {g.SLUG}: unknown recipe id {rid}")
            for sid in st.get("sec", []):
                if sid not in SEC:
                    sys.exit(f"Guide {g.SLUG}: unknown security entry id {sid}")
    nsteps = sum(len(p["steps"]) for p in g.PHASES)
    nsrc = len({u for p in g.PHASES for s in p["steps"] for _, u in s["src"]})
    nrec = len({r for p in g.PHASES for s in p["steps"] for r in s["rec"] + s.get("sec", [])})

    def body(rel):
        toc, phases, strip = "", "", ""
        for i, ph in enumerate(g.PHASES, 1):
            pid = f'phase-{i}-{ph["id"]}'
            deep = " deep" if ph.get("deep") else ""
            strip += (f'<li class="{deep.strip()}"><a href="#{pid}"><span class="gd-sn">{i}</span><strong>{esc(ph["title"])}</strong>'
                      f'<em>{esc(ph["time"])}</em></a></li>')
            sub = "".join(f'<li><a href="#{pid}-s{j}">{i}.{j} {esc(st["t"])}</a></li>' for j, st in enumerate(ph["steps"], 1)) if ph.get("deep") else ""
            toc += f'<li class="{deep.strip()}"><a href="#{pid}">{i}. {esc(ph["title"])}</a>' + (f'<ul>{sub}</ul>' if sub else "") + '</li>'
            steps = ""
            for j, st in enumerate(ph["steps"], 1):
                recs = ("".join(f'<a class="gd-chip" href="{rel}recipes/{rid}.html">{esc(RID[rid]["title"])}</a>' for rid in st["rec"])
                        + "".join(f'<a class="gd-chip" href="{rel}security/{sid}.html">{esc(SEC[sid]["title"])}</a>' for sid in st.get("sec", [])))
                srcs = "".join(f'<li><a href="{E(u)}">{esc(t)}</a></li>' for t, u in st["src"])
                steps += (f'<div class="gd-step" id="{pid}-s{j}"><h3><span>{i}.{j}</span> {esc(st["t"])}</h3>'
                          f'<p class="gd-done"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.5l3.2 3.2L15 6.8"/></svg>Done when: {_txt(st["check"])}</p>'
                          '<h4>Do this</h4><ul class="gd-do">' + "".join(f'<li>{_txt(x)}</li>' for x in st["do"]) + '</ul>'
                          + ('<div class="gd-pit"><h4>Pitfalls</h4><ul>' + "".join(f'<li>{_txt(x)}</li>' for x in st["pit"]) + '</ul></div>' if st["pit"] else "")
                          + (f'<div class="gd-recs"><h4>Hands-on recipes</h4>{recs}</div>' if recs else "")
                          + (f'<details class="gd-src"><summary>{SL} ({len(st["src"])})</summary><ul>{srcs}</ul></details>' if srcs else "")
                          + '</div>')
            phases += (f'<section class="gd-phase{deep}" id="{pid}" aria-labelledby="{pid}-h"><div class="gd-ph-h"><span class="gd-num">Phase {i}</span>'
                       f'<h2 id="{pid}-h">{esc(ph["title"])}</h2><span class="gd-time" title="Our planning estimate">≈ {esc(ph["time"])}</span></div>'
                       + ('<p class="gd-flag">Deepest phase: most of the risk lives here</p>' if deep else "")
                       + f'<p class="gd-goal">{esc(ph["goal"])}</p>' + (f'<p>{esc(ph["lead"])}</p>' if ph.get("lead") else "") + steps + '</section>')
        # rebuild checklist cleanly, grouped by phase
        check = ""
        for i, ph in enumerate(g.PHASES, 1):
            pid = f'phase-{i}-{ph["id"]}'
            check += f'<li class="gd-ck-h">Phase {i}: {esc(ph["title"])} <em>(≈ {esc(ph["time"])})</em></li>'
            check += "".join(f'<li><label><input type="checkbox" data-k="{g.SLUG}:{pid}-s{j}"> <span><b>{i}.{j}</b> {_txt(st["check"])}</span></label></li>'
                             for j, st in enumerate(ph["steps"], 1))
        intro = "".join(f'<p>{esc(x)}</p>' for x in g.INTRO)
        return (
            f'<section class="gd-hero"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i></div><div class="wrap">'
            + T.crumbs_dark(rel, f"guides/{g.SLUG}.html", [("Home", rel + "index.html"), ("Guides", rel + "guides/index.html"), (g.SHORT, None)]) +
            f'<p class="hx-badge"><span class="dot" aria-hidden="true"></span>Pillar guide · {getattr(g, "BADGE", "fact-checked against Microsoft Learn")} on {fmt_date(g.VERIFIED)}</p>'
            f'<h1>{esc(g.TITLE)}</h1><p class="hx-lead">{esc(g.DESC)}</p>'
            f'<div class="hx-cta"><a class="btn hx-p" href="#phase-1-{g.PHASES[0]["id"]}">Start with phase 1 →</a>'
            f'<a class="btn hx-g" href="#checklist">Printable checklist</a></div>'
            f'<dl class="hx-stats"><div><dt>Phases</dt><dd>{len(g.PHASES)}</dd></div><div><dt>Steps</dt><dd>{nsteps}</dd></div>'
            f'<div><dt>Linked recipes</dt><dd>{nrec}</dd></div><div><dt>{SL}</dt><dd>{nsrc}</dd></div></dl>'
            f'<ol class="gd-strip">{strip}</ol></div></section>'
            f'<div class="wrap gd-grid"><aside class="gd-toc" aria-label="Table of contents"><p>On this page</p><ol>{toc}'
            f'<li><a href="#checklist">Printable checklist</a></li></ol></aside>'
            f'<div class="gd-body">{T.guide_verify_card(rel, g)}<div class="gd-intro">{intro}<p class="meta">{esc(g.NAMING)} {esc(getattr(g, "TIME_NOTE", "Time estimates are our planning figures for a mid-size tenant, not Microsoft numbers."))}</p></div>'
            f'{phases}'
            f'<section class="gd-check" id="checklist" aria-labelledby="ck-h"><div class="gd-ph-h"><span class="gd-num">Checklist</span><h2 id="ck-h">The printable checklist</h2></div>'
            f'<p>Tick items as you go (saved in this browser only), then print or save as PDF for your change board.</p>'
            f'<p class="gd-ck-btns"><button class="btn p" type="button" id="ck-print">Print checklist</button> <button class="btn" type="button" id="ck-reset">Clear ticks</button> <span id="ck-n" class="fine"></span></p>'
            f'<ol class="gd-ck">{check}</ol><p class="fine">{esc(g.TITLE)} · {C.SITE_NAME} · verified {g.VERIFIED} · {SITE}/guides/{g.SLUG}.html</p></section>'
            f'<section class="vs" id="verified"><h2>Verification &amp; corrections</h2><p class="fine">Every step above lists the {SL.lower()} it was checked against '
            f'(open “{SL}” under each step). Guide last verified <strong>{fmt_date(g.VERIFIED)}</strong>. '
            f'<a href="{rel}methodology.html">How we verify</a> · <a href="{rel}changelog.html">Changelog</a></p>'
            f'<div class="vs-f"><p>Spotted something wrong or outdated?</p>{T.report_link(f"guides/{g.SLUG}.html", g.TITLE, "rp btn")}</div></section>'
            f'{signup(rel, "guide-" + g.SLUG)}</div></div>'
            '<script>(function(){var b=document.querySelectorAll(".gd-ck input"),n=document.getElementById("ck-n");'
            'function u(){var c=0;b.forEach(function(x){if(x.checked)c++});n.textContent=c+" of "+b.length+" done"}'
            'b.forEach(function(x){try{x.checked=localStorage.getItem(x.dataset.k)==="1"}catch(e){}x.addEventListener("change",function(){try{localStorage.setItem(x.dataset.k,x.checked?"1":"0")}catch(e){}u()})});u();'
            'document.getElementById("ck-print").onclick=function(){document.body.classList.add("print-ck");window.print();setTimeout(function(){document.body.classList.remove("print-ck")},500)};'
            'document.getElementById("ck-reset").onclick=function(){b.forEach(function(x){x.checked=false;try{localStorage.removeItem(x.dataset.k)}catch(e){}});u()};})();</script>'
        )
    return page(f"guides/{g.SLUG}.html", f"{g.TITLE} | {C.SITE_NAME}", g.DESC, body, "article")


def guides_index():
    def body(rel):
        cards = "".join(
            f'<a class="card card-lg" href="{g.SLUG}.html"><span class="card-i">{T.icon("book")}</span><div class="tag">Pillar guide · {len(g.PHASES)} phases · '
            f'{sum(len(p["steps"]) for p in g.PHASES)} steps</div><h3>{esc(g.TITLE)}</h3><p>{esc(g.DESC)}</p>'
            f'<span class="cm"><span class="cm-ok">{T.icon("check")}Verified {fmt_date(g.VERIFIED)}</span><span>Printable checklist</span></span></a>'
            for g in GUIDES)
        return (T.page_hero(rel, T.crumbs_dark(rel, "guides/index.html", [("Home", rel + "index.html"), ("Guides", None)]), "Guides",
                            "Long-form playbooks", "Phased, fact-checked guides that tie the recipes together. Every claim links to its official source.", kind="page")
                + f'<main class="wrap pg"><div class="grid">{cards}</div>{signup(rel, "guides-index")}</main>')
    return page("guides/index.html", f"Guides | {C.SITE_NAME}", "Long-form, fact-checked playbooks for Microsoft 365 and Windows admins.", body)


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    pages = []
    n = len(R)

    pages.append(page("index.html", f"{C.SITE_TAGLINE} | {C.SITE_NAME}", C.SITE_DESCRIPTION, lambda rel: (
        hero(rel) +
        f'<main class="wrap" id="library">{ad_slot("index-top")}<h2 class="lib-h">The recipe library</h2><div class="controls"><input id="q" aria-label="Search recipes" '
        f'placeholder="Search recipes: e.g. DLP, MFA, license, agent…"></div><div id="chips" class="chips"></div>'
        f'<p id="count" style="color:#666"></p><div class="grid" id="grid"></div>'
        f'<noscript><ul>' + "".join(f'<li><a href="recipes/{r["id"]}.html">{esc(r["title"])}</a></li>' for r in R) + '</ul></noscript>'
        f'{ad_slot("index-bottom")}{signup(rel, "index")}</main>'
        f'<script src="data/recipes.js"></script><script src="assets/app.js"></script>')))

    stats = (len(R), len(CY.load()), len(GUIDES), len({s["url"] for r in R for s in r["sources"]} | {s["url"] for e in CY.load() for s in e["sources"]}))
    pages.append(page("about.html", f"About | {C.SITE_NAME}", "Who runs Tenant Recipes, how every recipe is fact-checked, and how to report an error.",
                      lambda rel: T.about_body(rel, stats)))
    pages.append(page("methodology.html", f"Methodology: how we fact-check | {C.SITE_NAME}",
                      "Source hierarchy and verification process behind every Tenant Recipes page.", T.methodology_body))
    pages.append(page("changelog.html", f"Changelog | {C.SITE_NAME}", "Every new page, update and correction on Tenant Recipes.",
                      lambda rel: T.changelog_body(rel, T.changelog_entries(R, CY.load(), GUIDES))))
    pages.append(page("search.html", f"Search | {C.SITE_NAME}", "Search all Tenant Recipes recipes, guides and security entries.", T.search_body))

    pages.append(page("newsletter.html", f"Newsletter | {C.SITE_NAME}",
                      "A free weekly 5-minute brief on what changed in Copilot, Intune, Entra and Purview, and what admins should do about it.",
                      lambda rel: (
        T.page_hero(rel, T.crumbs_dark(rel, "newsletter.html", [("Home", rel + "index.html"), ("Newsletter", None)]), "Newsletter",
                    "The weekly Tenant Recipes brief", "One short email every Tuesday morning (CET) for Microsoft 365 "
                    "admins who were handed “roll out Copilot and agents safely”.", kind="page")
        + '<main class="wrap pg"><article class="prose doc"><ul><li><strong>Top story</strong>: the one change that matters this week, '
        'with an admin take.</li><li><strong>Copilot · Intune · Entra &amp; Purview</strong>: short items with what to do, each linked to the source.</li>'
        '<li><strong>Recipe of the week</strong>: a hands-on playbook from this site.</li></ul><p>5 minutes, no fluff, free.</p></article>'
        + signup(rel, "newsletter-page", heading=False) + '</main>')))

    host = E(C.HOSTING_PROVIDER)
    pages.append(page("privacy.html", f"Privacy policy | {C.SITE_NAME}", "How Tenant Recipes handles personal data.", lambda rel: (
        T.page_hero(rel, T.crumbs_dark(rel, "privacy.html", [("Home", rel + "index.html"), ("Privacy policy", None)]), "Legal", "Privacy policy",
                    f"Last updated: {TODAY}. No cookies, no analytics, no ad trackers.", kind="page")
        + f'<main class="wrap pg"><article class="prose doc">'
        f'<p>Tenant Recipes is a personal project based in {E(C.OWNER_COUNTRY)}. {E(C.OWNER_NAME)} is the data controller for the '
        f'personal data described here. We collect as little as possible.</p>'
        '<h2>Visiting the site</h2><p>The site uses no cookies, no analytics and no advertising trackers. '
        f'Like any website, our hosting provider ({host}) processes technical data such as your IP address and browser type in server logs '
        'to deliver and protect the site. We do not use these logs to identify you.</p>'
        '<h2>Newsletter</h2><p>If you subscribe, your email address (and the page you signed up from) is stored by our newsletter provider, '
        '<a href="https://buttondown.com/legal/privacy">Buttondown</a>, which processes it on our behalf and may store data outside the EU/EEA '
        'under appropriate safeguards. We use your address only to send the newsletter. The legal basis is your consent (GDPR Art. 6(1)(a)); '
        'you confirm it by clicking the link in the confirmation email. Buttondown may record opens and link clicks, which we only look at in '
        'aggregate to improve the newsletter. Links in the newsletter may carry “utm” tags that show a visit came from the newsletter; they '
        'do not identify you.</p><p>Every email has an unsubscribe link. When you unsubscribe, we stop sending to you and delete your address '
        'on request.</p>'
        '<h2>Sponsors</h2><p>Sponsors never receive subscriber lists or personal data.</p>'
        '<h2>Your rights</h2><p>Under the GDPR you can ask for access to, correction of, or deletion of your personal data, and you can '
        f'withdraw consent at any time. To do so, reply to any newsletter email (replies reach the editor privately), or open a <a href="{T.REPO}/issues/new/choose">GitHub issue</a> asking us to get in touch — please do not post personal data in the issue itself. You can also complain to the Swedish Authority for Privacy Protection '
        '(<a href="https://www.imy.se/en/">IMY</a>).</p>'
        '<h2>External links</h2><p>Recipes link to Microsoft Learn and other sites, which have their own privacy policies.</p>'
        '<h2>Changes</h2><p>If this policy changes, the date above is updated.</p></article></main>')))

    for g in GUIDES:
        pages.append(guide_page(g))
    pages.append(guides_index())
    pages += CY.build(page, R, esc, step_html, signup, fmt_date, E, C.SITE_NAME)

    for r in R:
        def body(rel, r=r):
            path = f'recipes/{r["id"]}.html'
            same = [x for x in R if x["category"] == r["category"] and x["id"] != r["id"]][:5]
            chips = (T.chip("list", f'{len(r["steps"])} steps') + (T.chip("alert", f'{len(r["pitfalls"])} pitfall{"s" if len(r["pitfalls"]) != 1 else ""}') if r["pitfalls"] else "")
                     + T.chip("link", f'{len(r["sources"])} Microsoft source{"s" if len(r["sources"]) != 1 else ""}')
                     + (T.chip("clock", f'First published {fmt_date(r["created"])}') if r.get("created") else ""))
            toc = [("problem", "The problem"), ("steps", "Steps")] + ([("pitfalls", "Pitfalls")] if r["pitfalls"] else []) + [("verified", "Sources & corrections")]
            pg = G2 if r["id"] in {x for p in G2.PHASES for st in p["steps"] for x in st["rec"]} else G1
            promo = (f'<a class="ps-promo" href="{rel}guides/{pg.SLUG}.html"><span class="ps-k">Pillar guide</span><strong>{esc(pg.SHORT)}</strong>'
                     f'<span>{len(pg.PHASES)} phases · printable checklist {T.icon("arrow")}</span></a>')
            return (T.page_hero(rel, T.crumbs_dark(rel, path, [("Home", rel + "index.html"), ("Recipes", rel + "index.html#library"), (r["category"], None)]),
                                f'{T.icon("layers")}{esc(r["category"])}', esc(r["title"]), "", chips, kind="recipe")
                    + '<main class="wrap pg"><div class="pg-grid"><article class="doc">'
                    + T.verify_card(rel, r, "Microsoft sources")
                    + f'<section id="problem" class="co co-info"><p class="co-h">{T.icon("target")}The problem</p><p>{esc(r["problem"])}</p></section>'
                    f'<h2 id="steps" class="h-ic">{T.icon("list")}Steps</h2><ol class="steps">' + "".join(f'<li><div>{step_html(s)}</div></li>' for s in r["steps"]) + '</ol>'
                    + (f'<section id="pitfalls" class="co co-warn"><p class="co-h">{T.icon("alert")}Pitfalls</p><ul>' + "".join(f'<li>{step_html(p)}</li>' for p in r["pitfalls"]) + '</ul></section>' if r["pitfalls"] else "")
                    + ad_slot("recipe-inline") + T.trust_bottom(rel, path, r["title"], r, "Verified against") + '</article>'
                    + T.side_nav(rel, toc, [(x["title"], f'{rel}recipes/{x["id"]}.html') for x in same], f'More in {r["category"]}', promo)
                    + '</div>' + signup(rel, "recipe-" + r["id"]) + '</main>')
        pages.append(page(f'recipes/{r["id"]}.html', f'{r["title"]} | {C.SITE_NAME}', r["problem"], body, "article"))

    # 404: self-contained (works at any depth)
    home = (SITE + "/") if SITE else "/"
    (DIST / "404.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Not found | Tenant Recipes</title><style>body{font-family:system-ui,Segoe UI,sans-serif;text-align:center;padding:80px 20px;'
        'color:#1b1b1f}a{color:#0f6cbd}</style></head><body><h1>Page not found</h1>'
        f'<p>That recipe may have moved. <a href="{home}">Browse all recipes</a>.</p></body></html>\n')

    # static assets
    shutil.copytree(ROOT / "assets", DIST / "assets")
    (DIST / "data").mkdir()
    shutil.copy(ROOT / "data" / "recipes.js", DIST / "data" / "recipes.js")
    (DIST / "data" / "search.js").write_text(T.search_index(R, CY.load(), GUIDES, CY.AREA))
    fingerprint_assets()
    if SITE:
        (DIST / "feed.xml").write_text(T.atom(R, CY.load(), GUIDES))
    shutil.copy(ROOT / "favicon.ico", DIST / "favicon.ico")
    (DIST / ".nojekyll").write_text("")  # GitHub Pages: serve files as-is
    robots = "User-agent: *\nAllow: /\n" + (f"Sitemap: {SITE}/sitemap.xml\n" if SITE else "")
    (DIST / "robots.txt").write_text(robots)
    if SITE:
        urls = "".join(f"<url><loc>{SITE}/{p}</loc></url>" for p in pages)
        (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    print(f"Built {len(pages)} pages into {DIST.relative_to(ROOT)}/"
          + ("" if SITE else "  (SITE_URL empty: share image uses a relative URL, no sitemap)")
          + ("  (Buttondown username not set: form not live)" if BD_PLACEHOLDER else ""))


def fingerprint_assets():
    """Cache-busting + no-CSS safety net for every page in dist/.
    1) CSS/JS references get ?v=<content hash>, so a browser never combines new HTML with an old cached
       style.css (GitHub Pages serves assets with max-age=600; stale CSS made inline icons render huge).
    2) Inline SVG icons without explicit size get width/height="1em", so they stay icon-sized even if
       the stylesheet is missing or outdated (CSS still overrides these presentation attributes)."""
    import hashlib, re
    def ver(rel_path):
        f = DIST / rel_path
        return hashlib.sha256(f.read_bytes()).hexdigest()[:10] if f.exists() else None
    ref = re.compile(r'((?:href|src)="(?:\.\./)*((?:assets|data)/[\w.-]+\.(?:css|js)))(")')
    svg = re.compile(r'<svg (?![^>]*\bwidth=)(?=[^>]*(?:class="ic"|viewBox="0 0 20 20"))')
    for f in DIST.rglob("*.html"):
        html = f.read_text()
        out = ref.sub(lambda m: f'{m.group(1)}?v={ver(m.group(2))}{m.group(3)}' if ver(m.group(2)) else m.group(0), html)
        out = svg.sub('<svg width="1em" height="1em" ', out)
        if out != html:
            f.write_text(out)


if __name__ == "__main__":
    build()
