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
import cloud_hardening_adversary_emulation as G3
import azure_update_manager_enterprise_patching as G4
import azure_arc_onboarding_enterprise_scale as G5
import admin_by_request_endpoint_privilege as GABR
import admin_by_request_intune_win32_packaging as GABRP
import entra_private_access_vpn_replacement as GPA
import adcs_hardening_tier0 as GADCS
import purple_team_hybrid_identity as GPTH
import external_attack_surface_osint as GEAS
import pivot_lateral_movement_segmented as GPLM
import azure_devops_hardening_key_eater as GADO
import enterprise_ai_governance as GAIG
import quick_copilot_license_checks as Q
GUIDES = [G1, G2, G3, G4, G5, GABR, GABRP, GPA, GADCS, GPTH, GEAS, GPLM, GADO, GAIG]
import build_cyber as CY
import build_trust as T
import build_ux as UX
import build_search as BS
import build_tools as TL
import build_links as BL
import build_policies as PL
import build_news as NW
import build_status as BST
import build_markers as MK
import build_tiers as TR
import build_history as HI
import build_code as CODE
import build_linkhub as LH
import build_aihub as AIH
import build_apps as AP

DIST = ROOT / "dist"
R = json.load(open(ROOT / "data" / "recipes.json"))
TODAY = datetime.date.today().isoformat()
BD_PLACEHOLDER = C.BUTTONDOWN_USERNAME in ("", "BUTTONDOWN_USERNAME")
SITE = C.SITE_URL.rstrip("/")
RID = {r["id"]: r for r in R}
CYD = {e["id"]: e for e in CY.load()}
SITE_LAST = max([d for r in R for d in (r.get("updated"), r.get("last_verified")) if d]
                + [d for e in CYD.values() for d in (e.get("updated"), e.get("last_verified")) if d]
                + [g.VERIFIED for g in GUIDES] + [Q.VERIFIED]
                + [x["date"] for x in json.load(open(ROOT / "data" / "changelog.json"))])


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


def canon(path):
    """Clean absolute URL for canonical/og:url/sitemap/JSON-LD: directory indexes end in '/', not 'index.html'.
    Built from SITE_URL, so switching to a custom domain only needs site_config.SITE_URL changed."""
    if not SITE:
        return ""
    p = path[:-len("index.html")] if path == "index.html" or path.endswith("/index.html") else path
    return f"{SITE}/{p}"


def _load_dates():
    """Published/updated dates for data-driven pages (tools, policies, news) -> {path: (published, updated)}."""
    out = {}
    for folder, pub in (("tools", "created"), ("policies", "created"), ("news", "date")):
        for f in sorted((ROOT / "data" / folder).glob("*.json")):
            try:
                e = json.load(open(f))
            except Exception:
                continue
            if isinstance(e, dict) and e.get("id") and e.get("status", "published") == "published":
                out[f'{folder}/{e["id"]}.html'] = (e.get(pub) or e.get("created"), e.get("updated") or e.get("last_verified"))
    return out


DATES = _load_dates()
LASTMOD = {}


def page_dates(path):
    """(published, modified) ISO dates for a page, or (None, None)."""
    if path.startswith("recipes/") and path[8:-5] in RID:
        r = RID[path[8:-5]]
        return r.get("created"), r.get("updated") or r.get("last_verified")
    if path.startswith("security/") and path[9:-5] in CYD:
        e = CYD[path[9:-5]]
        return e.get("created") or e.get("published") or e.get("kev_added"), e.get("updated") or e.get("last_verified")
    for g in GUIDES + [Q]:
        if path == f"guides/{g.SLUG}.html":
            return getattr(g, "PUBLISHED", None), getattr(g, "UPDATED", None) or g.VERIFIED
    return DATES.get(path, (None, None))


def json_ld(path, title, desc, og_type):
    """Light schema.org markup: WebSite + SearchAction on the home page, TechArticle on article pages."""
    if not SITE:
        return ""
    org = {"@type": "Organization", "name": C.SITE_NAME, "url": SITE + "/"}
    if path == "index.html":
        ld = {"@context": "https://schema.org", "@type": "WebSite", "name": C.SITE_NAME, "url": SITE + "/",
              "description": desc, "publisher": org,
              "potentialAction": {"@type": "SearchAction", "target": f"{SITE}/search/?q={{search_term_string}}",
                                  "query-input": "required name=search_term_string"}}
    elif og_type == "article":
        pub, mod = page_dates(path)
        ld = {"@context": "https://schema.org", "@type": "TechArticle", "headline": title.split(" | ")[0][:110],
              "description": desc, "url": canon(path), "mainEntityOfPage": canon(path), "inLanguage": "en",
              "author": {"@type": "Organization", "name": f"{C.SITE_NAME} editor", "url": canon("author/index.html")},
              "publisher": org, "image": f"{SITE}/assets/{UX.og_for(path, RID, title)[0]}"}
        if pub:
            ld["datePublished"] = pub
        if mod:
            ld["dateModified"] = mod
            ld.setdefault("datePublished", mod)
    else:
        return ""
    return '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + '</script>'


GC = (getattr(C, "GOATCOUNTER_CODE", "") or "").strip().lower()
if GC and not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,49}", GC):
    sys.exit(f"site_config.GOATCOUNTER_CODE must be just the site code (e.g. 'abc' from abc.goatcounter.com), got {GC!r}")

def head(title, desc, rel, path, og_type="website", og_auto=True):
    url = canon(path)
    og, og_alt = UX.og_for(path, RID, title) if og_auto else UX.og_image(path, RID)
    img = f"{SITE}/assets/{og}" if SITE else f"{rel}assets/{og}"
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        f"<title>{esc(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="icon" href="{rel}assets/favicon-32.png" type="image/png" sizes="32x32">',
        f'<link rel="icon" href="{rel}favicon.ico" sizes="any">',
        f'<link rel="apple-touch-icon" href="{rel}assets/apple-touch-icon.png">',
        '<meta name="theme-color" content="#0f2f6b">',
        f'<meta property="og:site_name" content="{esc(C.SITE_NAME)}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:image" content="{img}">',
        '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(og_alt)}">',
        f'<meta name="twitter:image:alt" content="{esc(og_alt)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:site" content="@{C.X_HANDLE}">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        f'<meta name="twitter:image" content="{img}">',
    ]
    if url:
        tags += [f'<meta property="og:url" content="{url}">', f'<link rel="canonical" href="{url}">']
    tags.append(json_ld(path, title, desc, og_type))
    tags.append(f'<link rel="alternate" type="application/atom+xml" title="{esc(C.SITE_NAME)}" href="{rel}feed.xml">')
    tags.append(f'<link rel="stylesheet" href="{rel}assets/style.css">')
    tags.append(f'<script src="{rel}assets/ui.js" defer></script>')
    tags.append(f'<script src="{rel}assets/search.js" defer></script>')
    if GC:
        tags.append(f'<script data-goatcounter="https://{GC}.goatcounter.com/count" async src="{rel}assets/goatcounter.js"></script>')
    return "".join(tags)


def nav(rel):
    return T.nav(rel)


# AI / LLM crawlers that are refused (search engines such as Googlebot and Bingbot stay allowed).
AI_BOTS = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "CCBot", "ClaudeBot", "anthropic-ai", "Claude-Web", "Google-Extended",
           "Applebot-Extended", "PerplexityBot", "Bytespider", "Amazonbot", "meta-externalagent", "FacebookBot", "cohere-ai",
           "Diffbot", "Omgilibot", "ImagesiftBot", "YouBot", "Timpibot"]


def robots_txt():
    out = ["# Search engines are welcome. AI training and bulk scraping are not: see /ai.txt and /about.html#terms.", "",
           "User-agent: Googlebot", "Allow: /", "", "User-agent: Bingbot", "Allow: /", ""]
    for b in AI_BOTS:
        out += [f"User-agent: {b}", "Disallow: /", ""]
    out += ["User-agent: *", "Allow: /", ""]
    if SITE:
        out.append(f"Sitemap: {SITE}/sitemap.xml")
    return "\n".join(out) + "\n"


def ai_txt():
    return ("# ai.txt: Tenant Recipes does not permit use of this site's content for AI/ML training,\n"
            "# dataset building or bulk scraping without prior written permission. Terms: "
            + (f"{SITE}/about.html#terms" if SITE else "/about.html#terms") + "\n\n"
            "User-Agent: *\nDisallow: /\n"
            "Disallow: *.html\nDisallow: *.txt\nDisallow: *.json\nDisallow: *.png\nDisallow: *.jpg\nDisallow: *.webp\nDisallow: *.svg\n")


def footer(rel, path="", title="", updated=None):
    return T.footer(rel, G1.SLUG, path, title, updated or SITE_LAST)


def meta_desc(s, n=158):
    """Search/preview description: one clean sentence-ish string of at most n characters."""
    s = " ".join(s.replace("`", "").split())
    if len(s) <= n:
        return s
    cut = s[:n - 1]
    end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if end >= 90:  # end on a full sentence when one fits
        return cut[:end + 1]
    cut = cut[:cut.rfind(" ")] if " " in cut else cut
    return cut.rstrip(",;:—-") + "…"


def recipe_desc(r):
    """Problem + what the reader gets (the problem line alone is often < 90 chars)."""
    p = r["problem"].strip()
    p = p if p.endswith((".", "?", "!")) else p + "."
    for get in (" Exact steps, pitfalls and a done-when check, linked to official sources.", " Exact steps, pitfalls and official sources."):
        if len(p + get) <= 158:
            return p + get
    return p


def page_updated(path):
    return page_dates(path)[1]


def ad_slot(name):
    return T.ad_slot(name)


def signup(rel, source, heading=True):
    """Buttondown embed form. The username comes ONLY from site_config.BUTTONDOWN_USERNAME."""
    u = E(C.BUTTONDOWN_USERNAME)
    h = ('<h2>The Tenant Recipes Weekly Brief</h2><p>Every Tuesday: 3 Microsoft changes you should know, 2 security updates worth '
         'investigating, 1 configuration tip and 1 thing to review in your tenant. 5 minutes, no fluff.</p>') if heading else ""
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
    desc = meta_desc(desc)
    html = (f'<!doctype html><html lang="en"><head>{head(title, desc, rel, path, og_type)}</head><body>\n'
            f'{nav(rel)}{body(rel)}\n{footer(rel, path, title.split(" | ")[0], page_updated(path))}</body></html>\n')
    html = UX.add_share(html, path, title.split(" | ")[0])
    out = DIST / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    LASTMOD[path] = page_dates(path)[1]
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
        f'<a class="btn hx-g" href="#find">Find a recipe ({n})</a></div>'
        f'<p class="hx-note"><a href="guides/{G1.SLUG}.html"><strong>{len(G1.PHASES)} phases · {sum(len(p["steps"]) for p in G1.PHASES)} steps · printable checklist.</strong> '
        f'Starts where the real risk is: oversharing, EEEU, sharing links and guests.</a> · <a href="#newsletter">Free weekly brief</a></p>'
        f'<dl class="hx-stats"><div><dt>Recipes</dt><dd>{n}</dd></div><div><dt>Categories</dt><dd>{len(cats)}</dd></div>'
        f'<div><dt>Microsoft sources linked</dt><dd>{len(sources)}</dd></div><div><dt>Last verified</dt><dd>{fmt_date(last)}</dd></div></dl>'
        f'</div><div class="hx-art"><div class="hx-shield"><img src="{rel}assets/mark.svg" alt="" width="200" height="200"></div>'
        f'<div class="hx-card"><p class="hx-card-h"><span aria-hidden="true">●●●</span> tenant-check</p><ul>{checks}</ul>'
        f'<p class="hx-card-f">{n}/{n} recipes verified · {fmt_date(last)}</p></div></div></div>'
        f'<div class="ticker" aria-label="All recipes"><ul class="tk">{ticker_items}</ul><ul class="tk" aria-hidden="true">{ticker_dupe}</ul></div>'
        f'</section>'
        f'<section class="sec wrap" aria-labelledby="sec-title"><p class="sec-k">Microsoft security track</p>'
        f'<h2 id="sec-title">AI is only as safe as your tenant. {sec_total} recipes to harden it first.</h2>'
        f'<div class="sec-grid">{tiles}</div>'
        f'<a class="cy-promo" href="guides/{G2.SLUG}.html"><span class="cy-promo-k">New guide</span><strong>{esc(G2.TITLE)}:</strong> '
        f'{len(G2.PHASES)} phases from CIS Level 1 vs Level 2 to Credential Guard, ASR, BitLocker and compliance scans →</a></section>'
    )


def _txt(s):
    return step_html(s)


def guide_page(g):
    RID = {r["id"]: r for r in R}
    SEC = {e["id"]: e for e in CY.load()}
    TOOLS = {e["id"]: e for e in TL.load()}
    SL = getattr(g, "SRC_LABEL", "Microsoft sources")
    GS = {x.SLUG: x for x in GUIDES}
    for ph in g.PHASES:
        for st in ph["steps"]:
            for rid in st["rec"]:
                if rid not in RID:
                    sys.exit(f"Guide {g.SLUG}: unknown recipe id {rid}")
            for sid in st.get("sec", []):
                if sid not in SEC:
                    sys.exit(f"Guide {g.SLUG}: unknown security entry id {sid}")
            for tid in st.get("tools", []):
                if tid not in TOOLS:
                    sys.exit(f"Guide {g.SLUG}: unknown tool id {tid}")
            for gs in st.get("guides", []):
                if gs not in GS or gs == g.SLUG:
                    sys.exit(f"Guide {g.SLUG}: unknown guide slug {gs}")
            if st.get("marker") and st["marker"] not in MK.MARKERS:
                sys.exit(f"Guide {g.SLUG}: unknown marker {st['marker']} on step {st['t']}")
            if st.get("marker") == "tested" and MK.validate_tested(st.get("tested"), st["t"]):
                sys.exit(f"Guide {g.SLUG}: " + "; ".join(MK.validate_tested(st.get("tested"), st["t"])))
    nsteps = sum(len(p["steps"]) for p in g.PHASES)
    nsrc = len({u for p in g.PHASES for s in p["steps"] for _, u in s["src"]} | {u for _, u in getattr(g, "PROBLEM", {}).get("src", [])})
    nrec = len({r for p in g.PHASES for s in p["steps"] for r in s["rec"] + s.get("sec", []) + s.get("tools", [])})

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
                        + "".join(f'<a class="gd-chip" href="{rel}security/{sid}.html">{esc(SEC[sid]["title"])}</a>' for sid in st.get("sec", []))
                        + "".join(f'<a class="gd-chip" href="{rel}tools/{tid}.html">{esc(TOOLS[tid]["name"])}</a>' for tid in st.get("tools", []))
                        + "".join(f'<a class="gd-chip" href="{rel}guides/{gs}.html">Guide: {esc(GS[gs].SHORT)}</a>' for gs in st.get("guides", [])))
                srcs = "".join(f'<li><a href="{E(u)}">{esc(t)}</a></li>' for t, u in st["src"])
                steps += (f'<div class="gd-step" id="{pid}-s{j}"><h3><span>{i}.{j}</span> {esc(st["t"])}{MK.badge(rel, st.get("marker"), st.get("tested"), fmt_date)}</h3>'
                          f'<p class="gd-done"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.5l3.2 3.2L15 6.8"/></svg><span>Done when: {_txt(st["check"])}</span></p>'
                          '<h4>Do this</h4><ul class="gd-do">' + "".join(f'<li>{_txt(x)}</li>' for x in st["do"]) + '</ul>'
                          + ('<div class="gd-pit"><h4>Pitfalls</h4><ul>' + "".join(f'<li>{_txt(x)}</li>' for x in st["pit"]) + '</ul></div>' if st["pit"] else "")
                          + (f'<div class="gd-recs"><h4>Related on this site</h4>{recs}</div>' if recs else "")
                          + (f'<details class="gd-src"><summary>{SL} ({len(st["src"])})</summary><ul>{srcs}</ul></details>' if srcs else "")
                          + '</div>')
            if i == 2:
                phases += ad_slot("guide-after-intro")
            if i == len(g.PHASES) // 2 + 1:
                phases += UX.news_mid(rel, "guide-" + g.SLUG)
            elif i > 2 and i % 3 == 0:
                phases += ad_slot(f"guide-between-phases-{i}")
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
        nt = getattr(g, "NOTICE", None)
        notice = (f'<aside class="co co-info gd-notice" aria-label="Editorial note"><p class="co-h">{esc(nt["title"])}</p><p>{esc(nt["text"])}</p></aside>') if nt else ""
        pb = getattr(g, "PROBLEM", None)
        problem = (f'<section class="gd-phase gd-problem" id="the-problem" aria-labelledby="pb-h"><div class="gd-ph-h"><span class="gd-num">Background</span><h2 id="pb-h">{esc(pb["title"])}</h2></div>'
                   + "".join(f'<h3>{esc(h)}</h3>' + "".join(f'<p>{esc(x)}</p>' for x in ps) for h, ps in pb["blocks"])
                   + (f'<details class="gd-src"><summary>{SL} ({len(pb["src"])})</summary><ul>' + "".join(f'<li><a href="{E(u)}">{esc(t)}</a></li>' for t, u in pb["src"]) + '</ul></details>' if pb.get("src") else "")
                   + '</section>') if pb else ""
        if pb:
            toc = f'<li><a href="#the-problem">The problem</a></li>' + toc
        return (
            f'<section class="gd-hero"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i></div><div class="wrap">'
            + T.crumbs_dark(rel, f"guides/{g.SLUG}.html", [("Home", rel + "index.html"), ("Guides", rel + "guides/index.html"), (g.SHORT, None)]) +
            f'<p class="hx-badge"><span class="dot" aria-hidden="true"></span>{TR.label(TR.guide_tier(g))} · {getattr(g, "BADGE", "fact-checked against Microsoft Learn")} on {fmt_date(g.VERIFIED)}</p>'
            f'<p class="tier-row">{TR.badge(rel, TR.guide_tier(g))}</p>'
            f'<h1>{esc(g.TITLE)}</h1><p class="hx-lead">{esc(g.DESC)}</p>'
            f'<div class="hx-cta"><a class="btn hx-p" href="#phase-1-{g.PHASES[0]["id"]}">Start with phase 1 →</a>'
            f'<a class="btn hx-g" href="#checklist">Printable checklist</a>'
            f'<a class="btn hx-g" href="{rel}downloads/{g.SLUG}-checklist.pdf" download>Checklist PDF</a></div>'
            f'<dl class="hx-stats"><div><dt>Phases</dt><dd>{len(g.PHASES)}</dd></div><div><dt>Steps</dt><dd>{nsteps}</dd></div>'
            f'<div><dt>Linked recipes</dt><dd>{nrec}</dd></div><div><dt>{SL}</dt><dd>{nsrc}</dd></div></dl>'
            f'<ol class="gd-strip">{strip}</ol></div></section>'
            f'<div class="wrap gd-grid"><aside class="gd-toc" aria-label="Table of contents"><p>On this page</p><ol>{toc}'
            f'<li><a href="#checklist">Printable checklist</a></li></ol></aside>'
            f'<div class="gd-body">{HI.dates_bar(g.PUBLISHED, getattr(g, "UPDATED", None) or g.VERIFIED, g.VERIFIED)}{T.guide_verify_card(rel, g)}{T.author_box(rel)}{notice}<div class="gd-intro">{intro}<p class="meta">{esc(g.NAMING)} {esc(getattr(g, "TIME_NOTE", "Time estimates are our planning figures for a mid-size tenant, not Microsoft numbers."))}</p></div>'
            f'{HI.guide_sources(g)}{problem}{phases}'
            f'<section class="gd-check" id="checklist" aria-labelledby="ck-h"><div class="gd-ph-h"><span class="gd-num">Checklist</span><h2 id="ck-h">The printable checklist</h2></div>'
            f'<p>Tick items as you go (saved in this browser only), then print or save as PDF for your change board.</p>'
            f'<p class="gd-ck-btns"><button class="btn p" type="button" id="ck-print">Print checklist</button> '
            f'<a class="btn" href="{rel}downloads/{g.SLUG}-checklist.pdf" download>Download PDF</a> '
            f'<a class="btn" href="{rel}guides/checklists/{g.SLUG}.md" download="{g.SLUG}-checklist.md">Markdown (.md)</a> '
            f'<button class="btn" type="button" id="ck-reset">Clear ticks</button> <span id="ck-n" class="fine"></span></p>'
            f'<ol class="gd-ck">{check}</ol><p class="fine">{esc(g.TITLE)} · {C.SITE_NAME} · verified {g.VERIFIED} · {SITE}/guides/{g.SLUG}.html</p></section>'
            + HI.history_html(f"guides/{g.SLUG}.html", g.PUBLISHED, getattr(g, "UPDATED", None) or g.VERIFIED, g.VERIFIED, getattr(g, "HISTORY", ())) +
            f'<section class="vs" id="verified"><h2>Verification &amp; corrections</h2><p class="fine">Every step above lists the {SL.lower()} it was checked against '
            f'(open “{SL}” under each step). Guide last verified <strong>{fmt_date(g.VERIFIED)}</strong>. '
            f'<a href="{rel}methodology.html">How we verify</a> · <a href="{rel}changelog/index.html">Changelog</a></p>'
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
    def gcard(rel, g):
        t = TR.guide_tier(g)
        return (f'<a class="card card-lg" href="{g.SLUG}.html"><span class="card-i">{T.icon("book" if t == "pillar" else "layers")}</span><div class="tag">{TR.label(t)} · {len(g.PHASES)} phases · '
                f'{sum(len(p["steps"]) for p in g.PHASES)} steps</div><h3>{esc(g.TITLE)}</h3><p>{esc(g.DESC)}</p>'
                f'<span class="cm"><span class="cm-ok">{T.icon("check")}Verified {fmt_date(g.VERIFIED)}</span><span>Printable checklist</span></span></a>')

    def body(rel):
        tiers = TR.by_tier(GUIDES)
        qcard = (f'<a class="card card-lg" href="{Q.SLUG}.html"><span class="card-i">{T.icon("check")}</span><div class="tag">{TR.label(TR.guide_tier(Q))} · quick checks · 1 page · PDF</div>'
                 f'<h3>{esc(Q.TITLE)}</h3><p>{esc(Q.DESC)}</p><span class="cm"><span class="cm-ok">{T.icon("check")}Verified {fmt_date(Q.VERIFIED)}</span>'
                 f'<span>{len(Q.CHECKS)} checks</span></span></a>')
        n_tech = len(tiers["technical"]) + (1 if TR.guide_tier(Q) == "technical" else 0)
        counts = {"pillar": len(tiers["pillar"]), "technical": n_tech, "recipe": len(R)}
        legend = "".join(f'<a class="tl-c tl-{t}" href="#tier-{t}"><span class="tier tier-{t}">{TR.TIERS[t][0]}</span><strong>{counts[t]}</strong><span>{esc(TR.TIERS[t][2])}</span></a>'
                         for t in ("pillar", "technical", "recipe"))
        filt = ('<div class="chips tl-f" role="group" aria-label="Filter by level"><button class="chip on" type="button" data-tier="all" aria-pressed="true">All</button>'
                + "".join(f'<button class="chip" type="button" data-tier="{t}" aria-pressed="false">{TR.TIERS[t][1]}</button>' for t in ("pillar", "technical", "recipe")) + '</div>')
        cats = {}
        for r in R:
            cats[r["category"]] = cats.get(r["category"], 0) + 1
        rcards = "".join(f'<a class="card" href="{rel}index.html#library"><div class="tag">{TR.label("recipe")} · {n}</div><h3>{esc(c)}</h3></a>' for c, n in cats.items())
        sec = lambda t, h, inner: (f'<section class="tl-s" id="tier-{t}" data-tier="{t}" aria-labelledby="tier-{t}-h"><h2 id="tier-{t}-h">{TR.badge(rel, t)} {h}</h2>'
                                    f'<p class="fine">{esc(TR.TIERS[t][2])}</p><div class="grid">{inner}</div></section>')
        return (T.page_hero(rel, T.crumbs_dark(rel, "guides/index.html", [("Home", rel + "index.html"), ("Guides", None)]), "Guides",
                            "Pillar guides, technical guides and recipes", "Three levels of content: pillar guides for a whole area, technical guides for one component, recipes for one problem. Every claim links to its official source.", kind="page")
                + f'<main class="wrap pg"><div class="tl-g">{legend}</div>{filt}'
                + sec("pillar", f'{counts["pillar"]} pillar guides', "".join(gcard(rel, g) for g in tiers["pillar"]))
                + sec("technical", f'{n_tech} technical guides', "".join(gcard(rel, g) for g in tiers["technical"]) + (qcard if TR.guide_tier(Q) == "technical" else ""))
                + sec("recipe", f'{len(R)} recipes', rcards + f'<a class="card" href="{rel}index.html#library"><div class="tag">All recipes</div><h3>Browse and filter all {len(R)} recipes →</h3></a>')
                + '<script>(function(){var b=document.querySelectorAll(".tl-f .chip"),s=document.querySelectorAll(".tl-s");b.forEach(function(x){x.addEventListener("click",function(){'
                  'b.forEach(function(y){y.classList.toggle("on",y===x);y.setAttribute("aria-pressed",y===x)});s.forEach(function(z){z.hidden=x.dataset.tier!=="all"&&z.dataset.tier!==x.dataset.tier})})})})();</script>'
                + f'{signup(rel, "guides-index")}</main>')
    return page("guides/index.html", f"Guides: pillar guides, technical guides and recipes for Microsoft Cloud admins | {C.SITE_NAME}",
                "Pillar guides for whole areas (Copilot, Windows 11 CIS, Azure Arc, Update Manager, Entra Private Access, AD CS hardening), technical deep dives and short recipes, all fact-checked with printable checklists.", body)


def build():
    TR.validate_guides(GUIDES + [Q])
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    pages = []
    n = len(R)

    pages.append(page("index.html", f"{C.SITE_NAME}: Microsoft Cloud & Modern Workplace playbooks for admins",
                      "Fact-checked playbooks for Microsoft 365 admins: Conditional Access, PIM, Intune, Autopilot, Copilot and Purview, plus a Cybersecurity & Infrastructure track.", lambda rel: (
        UX.carousel(rel, UX.featured(R, CY.load(), GUIDES, Q), len(R), max(r["last_verified"] for r in R if r.get("last_verified")),
                    CY.patch_tuesday_widget(rel, CY.load()).replace('class="pt-cd"', 'class="pt-cd pt-hero"', 1),
                    UX.search_bar(rel, R, len(CY.load())) + BST.pill(rel) + f'<script src="{rel}assets/status.js" defer></script>')
        + AIH.home_promo(rel)
        + UX.task_hubs(rel, R, GUIDES, Q, CY.load(), TL.load(), PL.load())
        + NW.latest_strip(rel, esc, fmt_date, CY.load())
        + UX.finder(rel, R, GUIDES, Q, len(CY.load()))
        + hero(rel)[hero(rel).index('<section class="sec wrap" aria-labelledby="sec-title">'):]
        + UX.infra_track(rel, CY.load(), TL.load(), PL.load()) +
        f'<main class="wrap" id="library">{ad_slot("index-top")}<h2 class="lib-h">The recipe library</h2><p class="lib-hint fine">Filter by topic, or use the search at the top to search everything.</p><div id="chips" class="chips" role="group" aria-label="Filter recipes by topic"></div>'
        f'<p id="count" class="fine" aria-live="polite"></p><div class="grid" id="grid"></div>'
        f'<noscript><ul>' + "".join(f'<li><a href="recipes/{r["id"]}.html">{esc(r["title"])}</a></li>' for r in R) + '</ul></noscript>'
        f'{ad_slot("index-bottom")}{signup(rel, "index")}</main>'
        f'<script src="data/recipes.js" defer></script><script src="assets/app.js" defer></script><script src="assets/carousel.js" defer></script>')))

    stats = (len(R), len(CY.load()), len(GUIDES), len({s["url"] for r in R for s in r["sources"]} | {s["url"] for e in CY.load() for s in e["sources"]}))
    pages.append(page("about.html", f"About Tenant Recipes: independent, fact-checked and source-linked | {C.SITE_NAME}", "Who edits Tenant Recipes, why there is no personal byline, how every recipe is fact-checked against primary sources, and how to report an error.",
                      lambda rel: T.about_body(rel, stats)))
    pages.append(page("author/index.html", f"About the editor: who writes and reviews Tenant Recipes | {C.SITE_NAME}",
                      "Tenant Recipes is written and technically reviewed by an anonymous editor: IT professional since 1999, Microsoft-focused since 2013. Focus areas, fact-checking and principles.",
                      T.author_body))
    pages.append(page("contact/index.html", f"Contact, corrections and security reports | {C.SITE_NAME}",
                      "How to reach the Tenant Recipes editors: report an error or outdated step, flag a broken link, suggest a topic, or report a security problem privately.",
                      T.contact_body))
    pages.append(page("methodology.html", f"Methodology: how every page is fact-checked | {C.SITE_NAME}",
                      "The source hierarchy, verification steps and re-check schedule behind every Tenant Recipes recipe, guide, CVE entry and template.", T.methodology_body))
    pages.append(page("changelog/index.html", f"What's new: changelog of recipes, guides and security entries | {C.SITE_NAME}", "Every new recipe, guide and security entry, every re-verification and every correction on Tenant Recipes, newest first.",
                      lambda rel: T.changelog_body(rel, T.changelog_entries(R, CY.load(), GUIDES, rel))))
    # old URL: redirect stub (not in sitemap)
    (DIST / "changelog.html").write_text(
        f'<!doctype html><html lang="en"><head>{head("Changelog moved | " + C.SITE_NAME, "The Tenant Recipes changelog has moved to the What is new page, which lists every new and updated page.", "", "changelog/index.html", og_auto=False)}'
        '<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=changelog/index.html"></head>'
        '<body><p>The changelog has moved to <a href="changelog/index.html">What\'s new</a>.</p></body></html>\n')
    pages.append(page("search/index.html", f"Search recipes, guides, CVEs and news | {C.SITE_NAME}", "Search every Tenant Recipes recipe, guide, vulnerability, hardening recipe and news item in your browser, with suggestions and typo tolerance.", BS.search_body))
    (DIST / "search.html").write_text(
        f'<!doctype html><html lang="en"><head>{head("Search moved | " + C.SITE_NAME, "Tenant Recipes search has moved to a new page that searches recipes, guides, vulnerabilities and news.", "", "search/index.html", og_auto=False)}'
        '<meta name="robots" content="noindex"><script>location.replace("search/index.html"+location.search)</script>'
        '<meta http-equiv="refresh" content="0; url=search/index.html"></head><body><p>Search has moved to <a href="search/index.html">the new search page</a>.</p></body></html>\n')

    pages.append(page("newsletter.html", f"The Tenant Recipes Weekly Brief (free newsletter) | {C.SITE_NAME}",
                      "A free 5-minute weekly brief for Microsoft 365 admins: 3 Microsoft changes, 2 security updates, 1 configuration tip and 1 thing to review in your tenant.",
                      lambda rel: (
        T.page_hero(rel, T.crumbs_dark(rel, "newsletter.html", [("Home", rel + "index.html"), ("Newsletter", None)]), "Newsletter",
                    "The Tenant Recipes Weekly Brief", "One short email every Tuesday (CET) for people who run Microsoft 365 tenants. "
                    "Same four sections every week, so you can scan it in five minutes.", kind="page")
        + '<main class="wrap pg"><article class="prose doc"><ul>'
        '<li><strong>3 Microsoft changes you should know</strong>: what changes, from when, and what to do.</li>'
        '<li><strong>2 security updates worth investigating</strong>: exploited or high-impact issues and what to check first.</li>'
        '<li><strong>1 practical configuration tip</strong>: one setting, with the recipe that has the steps, the check and the rollback.</li>'
        '<li><strong>1 thing to review in your tenant</strong>: one report, assignment or exception worth a look this week.</li></ul>'
        '<p>Every item links to a fact-checked page with the official sources. Free, no fluff. <a href="newsletter-sample.html">See a sample issue</a>.</p></article>'
        + signup(rel, "newsletter-page", heading=False) + '</main>')))

    host = E(C.HOSTING_PROVIDER)
    pages.append(page("privacy.html", f"Privacy policy | {C.SITE_NAME}", ("How Tenant Recipes handles personal data: no cookies, cookie-free aggregate visitor counts, and a newsletter you can leave with one click." if GC else "How Tenant Recipes handles personal data: no cookies, no analytics, and a newsletter you can leave with one click."), lambda rel: (
        T.page_hero(rel, T.crumbs_dark(rel, "privacy.html", [("Home", rel + "index.html"), ("Privacy policy", None)]), "Legal", "Privacy policy",
                    f"Last updated: {TODAY}. No cookies, no ad trackers" + (", only cookie-free aggregate visitor counts." if GC else ", no analytics."), kind="page")
        + f'<main class="wrap pg"><article class="prose doc">'
        f'<p>Tenant Recipes is a personal project based in {E(C.OWNER_COUNTRY)}. {E(C.OWNER_NAME)} is the data controller for the '
        f'personal data described here. We collect as little as possible.</p>'
        + ('<h2>Visiting the site</h2><p>The site uses no cookies and no advertising trackers. '
        f'Like any website, our hosting provider ({host}) processes technical data such as your IP address and browser type in server logs '
        'to deliver and protect the site. We do not use these logs to identify you.</p>'
        + ('<h2>Visitor statistics</h2><p>To see which pages are useful, we count page views with '
           '<a href="https://www.goatcounter.com">GoatCounter</a>. It sets no cookies, uses no local storage and builds no profile of you. '
           'It keeps only aggregate counts per page and per day or hour, such as the page, the referring site, browser and operating system, '
           'screen width, language and country (derived from the IP address, which is not stored). These counts cannot be linked to each other or to a person. '
           'The legal basis is our legitimate interest in knowing how the site is used (GDPR Art. 6(1)(f)). See GoatCounter’s '
           '<a href="https://www.goatcounter.com/help/privacy">privacy policy</a>. Browsers with an ad or tracker blocker usually block the counter, '
           'and that is fine.</p>' if GC else '<p>We do not run analytics.</p>'))
        + ''
        '<h2>Newsletter</h2><p>If you subscribe, your email address (and the page you signed up from) is stored by our newsletter provider, '
        '<a href="https://buttondown.com/legal/privacy">Buttondown</a>, which processes it on our behalf and may store data outside the EU/EEA '
        'under appropriate safeguards. We use your address only to send the newsletter. The legal basis is your consent (GDPR Art. 6(1)(a)); '
        'you confirm it by clicking the link in the confirmation email. Buttondown may record opens and link clicks, which we only look at in '
        'aggregate to improve the newsletter. Links in the newsletter may carry “utm” tags that show a visit came from the newsletter; they '
        'do not identify you.</p><p>Every email has an unsubscribe link. When you unsubscribe, we stop sending to you and delete your address '
        'on request.</p>'
        '<h2>Sponsors</h2><p>Sponsors never receive subscriber lists or personal data.</p>'
        '<h2>Your rights</h2><p>Under the GDPR you can ask for access to, correction of, or deletion of your personal data, and you can '
        f'withdraw consent at any time. To do so, ' + (f'email <a href="mailto:{E(C.CONTACT_EMAIL)}">{E(C.CONTACT_EMAIL)}</a>, ' if C.CONTACT_EMAIL else '') + f'reply to any newsletter email (replies reach the editor privately), or open a <a href="{T.REPO}/issues/new/choose">GitHub issue</a> asking us to get in touch — please do not post personal data in the issue itself. You can also complain to the Swedish Authority for Privacy Protection '
        '(<a href="https://www.imy.se/en/">IMY</a>).</p>'
        '<h2>External links</h2><p>Recipes link to Microsoft Learn and other sites, which have their own privacy policies.</p>'
        '<h2>Changes</h2><p>If this policy changes, the date above is updated.</p></article></main>')))

    for g in GUIDES:
        pages.append(guide_page(g))
    pages.append(guides_index())
    pages += CY.build(page, R, esc, step_html, signup, fmt_date, E, C.SITE_NAME)
    pages += TL.build(page, esc, step_html, signup, fmt_date, E, C.SITE_NAME)
    pages += PL.build(page, esc, signup, fmt_date, E, C.SITE_NAME)
    pages += BST.build(page, esc, E, C.SITE_NAME, DIST)
    pages += NW.build(page, esc, step_html, signup, fmt_date, E, C.SITE_NAME, CY.load())
    pages += CODE.build(page, esc, fmt_date, signup, C.SITE_NAME, set(RID), {g.SLUG for g in GUIDES + [Q]})
    pages += LH.build(page, esc, signup, C.SITE_NAME)
    pages += AIH.build(page, C.SITE_NAME)
    pages += AP.build(page, esc, fmt_date, signup, C.SITE_NAME)

    refs = UX.guide_refs(GUIDES)
    BL.check(R)
    NEWS = NW.load_curated()
    for r in R:
        def body(rel, r=r):
            path = f'recipes/{r["id"]}.html'
            same = [x for x in R if x["category"] == r["category"] and x["id"] != r["id"]][:5]
            chips = (T.chip("list", f'{len(r["steps"])} steps') + (T.chip("alert", f'{len(r["pitfalls"])} pitfall{"s" if len(r["pitfalls"]) != 1 else ""}') if r["pitfalls"] else "")
                     + T.chip("link", f'{len(r["sources"])} Microsoft source{"s" if len(r["sources"]) != 1 else ""}')
                     + (T.chip("clock", f'First published {fmt_date(r["created"])}') if r.get("created") else ""))
            toc = ([("problem", "The problem"), ("steps", "Steps")] + ([("done", "Done when")] if r.get("done_when") else [])
                   + ([("pitfalls", "Pitfalls")] if r["pitfalls"] else []) + ([("troubleshooting", "Troubleshooting")] if r.get("troubleshooting") else [])
                   + ([("rollback", "Rollback")] if r.get("rollback") else []) + [("next", "Related & next steps"), ("history", "Version history"), ("verified", "Sources & corrections")])
            pg = G2 if r["id"] in {x for p in G2.PHASES for st in p["steps"] for x in st["rec"]} else G1
            promo = (f'<a class="ps-promo" href="{rel}guides/{pg.SLUG}.html"><span class="ps-k">Pillar guide</span><strong>{esc(pg.SHORT)}</strong>'
                     f'<span>{len(pg.PHASES)} phases · printable checklist {T.icon("arrow")}</span></a>')
            tags = "".join(f'<a class="tg" href="{rel}index.html?t={E(t.replace(" ", "+"))}#library">{esc(t)}</a>' for t in UX.tags_for(r))
            rel_items = UX.related(r, R, refs)
            return (T.page_hero(rel, T.crumbs_dark(rel, path, [("Home", rel + "index.html"), ("Recipes", rel + "index.html#library"), (r["category"], None)]),
                                f'{TR.badge(rel, "recipe")} {T.icon("layers")}{esc(r["category"])}', esc(r["title"]), "", chips, kind="recipe")
                    + '<main class="wrap pg"><div class="pg-grid"><article class="doc">'
                    + HI.dates_bar(r.get("created"), r.get("updated"), r.get("last_verified"))
                    + T.verify_card(rel, r, "Microsoft sources")
                    + UX.back_to_guide(rel, r, refs, pg)
                    + f'<section id="problem" class="co co-info"><p class="co-h">{T.icon("target")}The problem</p><p>{esc(r["problem"])}</p></section>'
                    + HI.recipe_sources(r)
                    + UX.toolbar(rel, r) + ad_slot("recipe-after-intro")
                    + f'<h2 id="steps" class="h-ic">{T.icon("list")}Steps{MK.section_badge(rel, r, "steps", fmt_date)}</h2><ol class="steps">' + "".join(f'<li><div>{step_html(s)}</div></li>' for s in r["steps"]) + '</ol>'
                    + MK.notes_html(rel, r, step_html, fmt_date)
                    + UX.screenshots(r, rel)
                    + UX.done_when(r, step_html)
                    + (f'<section id="pitfalls" class="co co-warn"><p class="co-h">{T.icon("alert")}Pitfalls{MK.section_badge(rel, r, "pitfalls", fmt_date)}</p><ul>' + "".join(f'<li>{step_html(p)}</li>' for p in r["pitfalls"]) + '</ul></section>' if r["pitfalls"] else "")
                    + MK.troubleshooting_html(rel, r, step_html, T.icon, fmt_date) + MK.rollback_html(rel, r, step_html, T.icon, fmt_date)
                    + UX.news_mid(rel, "recipe-" + r["id"]) + ad_slot("recipe-before-related")
                    + f'<section id="next" class="nx" aria-labelledby="nx-h"><h2 id="nx-h">Related recipes &amp; next steps</h2>'
                    + (f'<p class="tgs"><span class="fine">Topics:</span> {tags}</p>' if tags else "")
                    + f'<div class="grid nx-g">{UX.related_cards(rel, rel_items)}</div>'
                    + BL.cluster_box(rel, r, R, {x["id"] for x in rel_items}, NEWS, esc) + f'{UX.back_to_guide(rel, r, refs, pg)}</section>'
                    + HI.history_html(path, r.get("created"), r.get("updated"), r.get("last_verified"), [(h["date"], h["note"]) for h in r.get("history") or []])
                    + T.trust_bottom(rel, path, r["title"], r, "Verified against") + '</article>'
                    + T.side_nav(rel, toc, [(x["title"], f'{rel}recipes/{x["id"]}.html') for x in same], f'More in {r["category"]}', promo)
                    + '</div>' + signup(rel, "recipe-" + r["id"]) + '</main>')
        pages.append(page(f'recipes/{r["id"]}.html', f'{r["title"]} | {C.SITE_NAME}', recipe_desc(r), body, "article"))

    # Quick guide + sample newsletter issue
    pages.append(page(f"guides/{Q.SLUG}.html", f"{Q.TITLE} | {C.SITE_NAME}", Q.DESC,
                      lambda rel: UX.quick_body(rel, Q, RID, '<div class="wrap">' + signup(rel, "quick-" + Q.SLUG) + '</div>'), "article"))
    pages.append(page("newsletter-sample.html", f"Sample issue of the weekly brief | {C.SITE_NAME}",
                      "See what the free Tenant Recipes Weekly Brief looks like: 3 Microsoft changes, 2 security updates, 1 configuration tip and 1 thing to review in your tenant.",
                      lambda rel: UX.sample_issue_body(rel, R, CY.load(), GUIDES, NEWS) + f'<div class="wrap">{signup(rel, "newsletter-sample")}</div>'))

    # Markdown checklists (download buttons)
    (DIST / "recipes" / "checklists").mkdir(parents=True, exist_ok=True)
    for r in R:
        (DIST / "recipes" / "checklists" / f'{r["id"]}.md').write_text(UX.recipe_markdown(r))
    (DIST / "guides" / "checklists").mkdir(parents=True, exist_ok=True)
    for g in GUIDES:
        (DIST / "guides" / "checklists" / f"{g.SLUG}.md").write_text(UX.guide_markdown(g))

    # 404: self-contained (works at any depth)
    home = (SITE + "/") if SITE else "/"
    (DIST / "404.html").write_text(
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Not found | Tenant Recipes</title><meta name="robots" content="noindex"><style>body{font-family:system-ui,Segoe UI,sans-serif;text-align:center;padding:80px 20px;'
        'color:#1b1b1f}a{color:#0f6cbd}</style>'
        + (f'<script data-goatcounter="https://{GC}.goatcounter.com/count" async src="{home}assets/goatcounter.js"></script>' if GC else '')
        + '</head><body><h1>Page not found</h1>'
        f'<p>That recipe may have moved. <a href="{home}">Browse all recipes</a>.</p></body></html>\n')

    # static assets
    UX.write_og_pages(ROOT)   # list of pages that want an automatic OG card (tools/make_page_og.py)
    shutil.copytree(ROOT / "assets", DIST / "assets", ignore=shutil.ignore_patterns("manifest.json"))
    shutil.copytree(ROOT / "downloads", DIST / "downloads", ignore=shutil.ignore_patterns("manifest.json"))
    (DIST / "data").mkdir()
    shutil.copy(ROOT / "data" / "recipes.js", DIST / "data" / "recipes.js")
    idx = BS.build_index(R, CY.load(), GUIDES, Q, CY.AREA, UX.tags_for, json.load(open(ROOT / "data" / "changelog.json")),
                         TL.search_docs() + PL.search_docs() + NW.search_docs(CY.load()) + CODE.search_docs() + AP.search_docs() + LH.search_docs() + AIH.search_docs())
    (DIST / "search").mkdir(exist_ok=True)
    (DIST / "search" / "index.json").write_text(json.dumps(idx, ensure_ascii=False, separators=(",", ":")))
    print(f"Search index: {len(idx['docs'])} docs, {len(idx['sug'])} suggestions, {len(idx['syn'])} synonym groups, {len(idx['q'])} questions")
    fingerprint_assets()
    if SITE:
        (DIST / "feed.xml").write_text(T.atom(R, CY.load(), GUIDES))
        (DIST / "news" / "feed.xml").write_text(NW.feed(SITE, C.SITE_NAME, CY.load()))
    shutil.copy(ROOT / "favicon.ico", DIST / "favicon.ico")
    (DIST / ".nojekyll").write_text("")  # GitHub Pages: serve files as-is
    if SITE:  # RFC 9116 security.txt (needs include-hidden-files in the Pages workflow for /.well-known/)
        (DIST / ".well-known").mkdir(exist_ok=True)
        (DIST / ".well-known" / "security.txt").write_text(T.security_txt())
        (DIST / "security.txt").write_text(T.security_txt())
    (DIST / "robots.txt").write_text(robots_txt())
    (DIST / "ai.txt").write_text(ai_txt())
    if SITE:
        urls = "".join(f"<url><loc>{canon(p)}</loc>" + (f"<lastmod>{LASTMOD[p]}</lastmod>" if LASTMOD.get(p) else "") + "</url>"
                       for p in dict.fromkeys(pages))
        (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>'
            f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    print(f"Built {len(pages)} pages into {DIST.relative_to(ROOT)}/"
          + ("" if SITE else "  (SITE_URL empty: share image uses a relative URL, no sitemap)")
          + ("  (Buttondown username not set: form not live)" if BD_PLACEHOLDER else ""))


def _min_css(css):
    """Conservative CSS minifier: drops comments and collapses whitespace around braces/semicolons only
    (never inside selectors, so descendant combinators and ':' pseudo-classes are untouched)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s*\n\s*", "\n", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    return css.replace("\n", " ").strip() + "\n"


def optimise_assets():
    """Performance pass on dist/ only (sources stay readable): minified style.css."""
    f = DIST / "assets" / "style.css"
    before = f.stat().st_size
    f.write_text(_min_css(f.read_text()))
    print(f"Assets: style.css {before // 1024} KB -> {f.stat().st_size // 1024} KB (minified)")


def fingerprint_assets():
    """Cache-busting + no-CSS safety net for every page in dist/.
    1) CSS/JS references get ?v=<content hash>, so a browser never combines new HTML with an old cached
       style.css (GitHub Pages serves assets with max-age=600; stale CSS made inline icons render huge).
    2) Inline SVG icons without explicit size get width/height="1em", so they stay icon-sized even if
       the stylesheet is missing or outdated (CSS still overrides these presentation attributes)."""
    import hashlib, re
    optimise_assets()
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
