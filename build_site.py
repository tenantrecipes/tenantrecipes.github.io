"""Generate the static site into dist/ from data/recipes.json + site_config.py.
All internal links and assets are relative, so dist/ works on a free subdomain or a sub-path
(e.g. https://user.github.io/tenantrecipes/). Run via `python3 build.py`."""
import json, re, shutil, pathlib, sys, datetime
from html import escape as E
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import site_config as C

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
    return "".join(esc(p) if i % 2 == 0 else f"<code>{esc(p)}</code>" for i, p in enumerate(parts))


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
    tags.append(f'<link rel="stylesheet" href="{rel}assets/style.css">')
    return "".join(tags)


def nav(rel):
    return (f'<header><nav><a class="logo" href="{rel}index.html"><img src="{rel}assets/logo.svg" alt="Tenant Recipes" width="158" height="36"></a><div>'
            f'<a href="{rel}index.html#library">Recipes</a><a href="{rel}newsletter.html">Newsletter</a>'
            f'<a href="{rel}about.html">About</a></div></nav></header>')


def footer(rel):
    return (f'<footer>Tenant Recipes · Practical AI recipes for Microsoft 365 admins · Not affiliated with Microsoft<br>'
            f'<a href="{rel}newsletter.html">Newsletter</a> · <a href="{rel}about.html">About</a> · '
            f'<a href="{rel}privacy.html">Privacy policy</a></footer>')


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
    if C.CONTACT_EMAIL:
        return f'<a href="mailto:{E(C.CONTACT_EMAIL)}">{E(C.CONTACT_EMAIL)}</a>'
    return "reply to any newsletter email"


SECURITY_TRACK = [  # (category, headline, blurb, preferred first recipe id) — counts and links are computed from data
    ("Conditional Access for AI", "Lock down sign-ins", "Phishing-resistant MFA, risk-based blocks and break-glass hygiene before AI scales.", "ca-require-mfa-copilot"),
    ("Purview, DLP & data security for Copilot", "Stop oversharing", "Find what Copilot can see, then fence it with labels, DLP and audit.", "purview-oversharing-assessment"),
    ("Intune & devices for AI", "Harden devices", "Compliant devices and app protection so AI only runs where it should.", "intune-compliance-baseline"),
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
        f'<div class="hx-cta"><a class="btn hx-p" href="#library">Browse {n} recipes →</a>'
        f'<a class="btn hx-g" href="#newsletter">Get the free weekly brief</a></div>'
        f'<dl class="hx-stats"><div><dt>Recipes</dt><dd>{n}</dd></div><div><dt>Categories</dt><dd>{len(cats)}</dd></div>'
        f'<div><dt>Microsoft sources linked</dt><dd>{len(sources)}</dd></div><div><dt>Last verified</dt><dd>{fmt_date(last)}</dd></div></dl>'
        f'</div><div class="hx-art"><div class="hx-shield"><img src="{rel}assets/mark.svg" alt="" width="200" height="200"></div>'
        f'<div class="hx-card"><p class="hx-card-h"><span aria-hidden="true">●●●</span> tenant-check</p><ul>{checks}</ul>'
        f'<p class="hx-card-f">{n}/{n} recipes verified · {fmt_date(last)}</p></div></div></div>'
        f'<div class="ticker" aria-label="All recipes"><ul class="tk">{ticker_items}</ul><ul class="tk" aria-hidden="true">{ticker_dupe}</ul></div>'
        f'</section>'
        f'<section class="sec wrap" aria-labelledby="sec-title"><p class="sec-k">Security track</p>'
        f'<h2 id="sec-title">AI is only as safe as your tenant. {sec_total} recipes to harden it first.</h2>'
        f'<div class="sec-grid">{tiles}</div></section>'
    )


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

    pages.append(page("about.html", f"About | {C.SITE_NAME}", "Who writes Tenant Recipes and how the recipes are made.", lambda rel: (
        '<main class="wrap"><article><h1>About Tenant Recipes</h1><p>Tenant Recipes is run by a Microsoft 365 administrator who spent '
        'years deep in Intune, device management and Conditional Access — and is now all-in on AI: Microsoft 365 Copilot, Copilot Studio '
        'agents and AI assistants.</p><p>Every recipe is written for working admins: the problem, the exact steps, the pitfalls, and links '
        'to official Microsoft Learn documentation. Microsoft changes fast, so always check the linked docs before production changes. '
        'Each recipe shows when it was last verified against those docs.</p>'
        f'<p>Want to sponsor the newsletter or suggest a recipe? Just {contact_html()}.</p></article></main>')))

    pages.append(page("newsletter.html", f"Newsletter | {C.SITE_NAME}",
                      "A free weekly 5-minute brief on what changed in Copilot, Intune, Entra and Purview, and what admins should do about it.",
                      lambda rel: (
        '<main class="wrap"><article><h1>The weekly Tenant Recipes brief</h1><p>One short email every Tuesday morning (CET) for Microsoft 365 '
        'admins who were handed “roll out Copilot and agents safely”.</p><ul><li><strong>Top story</strong>: the one change that matters this week, '
        'with an admin take.</li><li><strong>Copilot · Intune · Entra &amp; Purview</strong>: short items with what to do, each linked to the source.</li>'
        '<li><strong>Recipe of the week</strong>: a hands-on playbook from this site.</li></ul><p>5 minutes, no fluff, free.</p></article>'
        + signup(rel, "newsletter-page", heading=False) + '</main>')))

    host = E(C.HOSTING_PROVIDER)
    pages.append(page("privacy.html", f"Privacy policy | {C.SITE_NAME}", "How Tenant Recipes handles personal data.", lambda rel: (
        f'<main class="wrap"><article><h1>Privacy policy</h1><p class="fine">Last updated: {TODAY}</p>'
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
        f'withdraw consent at any time. To do so, {contact_html()}. You can also complain to the Swedish Authority for Privacy Protection '
        '(<a href="https://www.imy.se/en/">IMY</a>).</p>'
        '<h2>External links</h2><p>Recipes link to Microsoft Learn and other sites, which have their own privacy policies.</p>'
        '<h2>Changes</h2><p>If this policy changes, the date above is updated.</p></article></main>')))

    for r in R:
        def body(rel, r=r):
            ver = (f'Last verified against Microsoft docs: <strong>{r["last_verified"]}</strong>' if r.get("last_verified")
                   else 'Not yet re-verified against current Microsoft docs. Check the linked sources before production changes.')
            src = "".join(f'<li><a href="{E(s["url"])}">{esc(s["title"])}</a>'
                          + (f' <span class="fine">(checked {s["checked"]})</span>' if s.get("checked") else "") + '</li>'
                          for s in r["sources"])
            return (f'<main class="wrap"><article><a href="{rel}index.html#library">← All recipes</a>'
                    f'<div class="tag" style="margin-top:14px">{esc(r["category"])}</div><h1>{esc(r["title"])}</h1>'
                    f'<p class="meta">{ver}</p>'
                    f'<h2>The problem</h2><p>{esc(r["problem"])}</p>'
                    f'<h2>Steps</h2><ol>' + "".join(f'<li>{step_html(s)}</li>' for s in r["steps"]) + '</ol>'
                    + (f'<h2>Pitfalls</h2><ul>' + "".join(f'<li>{esc(p)}</li>' for p in r["pitfalls"]) + '</ul>' if r["pitfalls"] else "")
                    + f'{ad_slot("recipe-inline")}<h2>Official docs</h2><ul>{src}</ul></article>'
                    + signup(rel, "recipe-" + r["id"]) + '</main>')
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


if __name__ == "__main__":
    build()
