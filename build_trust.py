"""Trust & navigation layer: header/footer, breadcrumbs, verification panels, "Report an error" links,
About / Methodology / Changelog / Search pages, the site-wide search index and the Atom feed.
Everything shown is computed from data (recipes, cyber entries, guides, data/changelog.json) at build time."""
import json, datetime, pathlib
from html import escape as E
from urllib.parse import quote
import site_config as C

ROOT = pathlib.Path(__file__).resolve().parent
SITE = C.SITE_URL.rstrip("/")
REPO = f"https://github.com/{C.GITHUB_REPO}"
TODAY = datetime.date.today()


def esc(s):
    return E(str(s), quote=True)


def fmt(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


# ---------------------------------------------------------------- header / footer
def nav(rel):
    return (f'<header class="sh"><nav><a class="logo" href="{rel}index.html"><img src="{rel}assets/logo.svg" alt="Tenant Recipes" width="158" height="36"></a>'
            f'<div class="nv">'
            f'<a href="{rel}index.html#library">Recipes</a><a href="{rel}guides/index.html">Guides</a>'
            f'<a href="{rel}security/index.html">Security</a><a href="{rel}about.html">About</a>'
            f'<form class="nv-s" action="{rel}search.html" method="get" role="search"><label class="sr" for="nv-q">Search the site</label>'
            f'<input id="nv-q" name="q" type="search" placeholder="Search…" autocomplete="off"></form>'
            f'<a class="nv-cta" href="{rel}newsletter.html">Newsletter</a></div></nav></header>')


def footer(rel, guide_slug):
    col = lambda h, links: (f'<div><h4>{h}</h4><ul>' + "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in links) + '</ul></div>')
    return ('<footer class="sf"><div class="sf-in">'
            f'<div class="sf-brand"><img src="{rel}assets/logo.svg" alt="Tenant Recipes" width="140" height="32">'
            '<p>Fact-checked AI &amp; security recipes for Microsoft 365 admins. An independent project — not affiliated with Microsoft or any vendor.</p></div>'
            + col("Content", [("Recipes", f"{rel}index.html#library"), ("Guides", f"{rel}guides/index.html"),
                              ("Secure Copilot rollout", f"{rel}guides/{guide_slug}.html"), ("Security &amp; vulnerability watch", f"{rel}security/index.html"),
                              ("Search", f"{rel}search.html")])
            + col("Trust", [("About", f"{rel}about.html"), ("Methodology", f"{rel}methodology.html"), ("Changelog", f"{rel}changelog.html"),
                            ("Report an issue", f"{REPO}/issues/new/choose")])
            + col("Stay updated", [("Newsletter", f"{rel}newsletter.html"), ("Atom / RSS feed", f"{rel}feed.xml"),
                                   ("Suggest a recipe", f"{REPO}/issues/new?template=suggest-recipe.yml")])
            + col("Legal", [("Privacy policy", f"{rel}privacy.html"), ("Disclaimer", f"{rel}about.html#disclaimer")])
            + f'</div><p class="sf-b">© {TODAY.year} Tenant Recipes · Microsoft, Microsoft 365, Copilot, Entra, Intune and Purview are trademarks of the Microsoft group of companies. '
            'Other product names belong to their owners.</p></footer>')


# ---------------------------------------------------------------- per-page trust pieces
def crumbs(rel, path, items):
    """items: list of (label, href-or-None). Renders visible breadcrumbs + schema.org BreadcrumbList."""
    vis = " / ".join(f'<a href="{h}">{esc(t)}</a>' if h else f'<span aria-current="page">{esc(t)}</span>' for t, h in items)
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": []}
    for i, (t, h) in enumerate(items, 1):
        el = {"@type": "ListItem", "position": i, "name": t}
        if h and SITE:
            el["item"] = SITE + "/" + _abs(path, h)
        ld["itemListElement"].append(el)
    return (f'<div class="crumb" role="navigation" aria-label="Breadcrumb">{vis}</div>'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def _abs(path, href):
    base = pathlib.PurePosixPath(path).parent
    parts = []
    for p in (base / href.split("#")[0]).parts:
        if p == "..":
            parts.pop()
        elif p != ".":
            parts.append(p)
    return "/".join(parts) + (("#" + href.split("#")[1]) if "#" in href else "")


def report_url(path, title):
    url = f"{SITE}/{path}"
    return (f"{REPO}/issues/new?template=report-error.yml&amp;title={quote('[Error] ' + title)}"
            f"&amp;page_url={quote(url, safe='')}")


def report_link(path, title, cls="rp"):
    return (f'<a class="{cls}" href="{report_url(path, title)}" rel="nofollow">'
            '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M4 17V3m0 1h9l-1.5 3L13 10H4"/></svg>Report an error on this page</a>')


def stale(last):
    if not last:
        return True
    return (TODAY - datetime.date.fromisoformat(last)).days > C.REVERIFY_DAYS


def trust_top(rel, item, nsrc_label):
    last, upd, created = item.get("last_verified"), item.get("updated"), item.get("created")
    bits = []
    if last:
        bits.append(f'<span class="tb-ok"><svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5 10.5l3.2 3.2L15 6.8"/></svg>Verified {fmt(last)}</span>')
    bits.append(f'<a href="#verified">{len(item["sources"])} {nsrc_label}</a>')
    if upd:
        bits.append(f'<span>Last updated {fmt(upd)}</span>')
    if created:
        bits.append(f'<span>First published {fmt(created)}</span>')
    bits.append(f'<a href="{rel}methodology.html">How we verify</a>')
    warn = ""
    if stale(last):
        warn = (f'<p class="tb-warn">Due for re-verification: this page was last checked more than {C.REVERIFY_DAYS} days ago. '
                'Check the linked sources before you make production changes.</p>')
    return f'<div class="tb" role="note">{"".join(bits)}</div>{warn}'


def trust_bottom(rel, path, title, item, heading):
    rows = "".join(f'<li><a href="{E(s["url"])}">{esc(s["title"])}</a><span class="vs-d">'
                   + (f'checked {fmt(s["checked"])}' if s.get("checked") else "date not recorded") + '</span></li>'
                   for s in item["sources"])
    last = item.get("last_verified")
    return (f'<section class="vs" id="verified" aria-labelledby="vs-h"><h2 id="vs-h">{heading}</h2>'
            f'<p class="fine">Each source below was opened and compared with the steps on this page on the date shown. '
            + (f'Page last verified <strong>{fmt(last)}</strong>' if last else 'Not yet verified')
            + (f' · last updated {fmt(item["updated"])}' if item.get("updated") else "") + '.</p>'
            f'<ul class="vs-l">{rows}</ul>'
            f'<div class="vs-f"><p>Spotted something wrong or outdated? Corrections are public and logged in the <a href="{rel}changelog.html">changelog</a>.</p>'
            f'{report_link(path, title, "rp btn")}</div></section>')


# ---------------------------------------------------------------- content pages
def about_body(rel, stats):
    n_rec, n_cy, n_g, n_src = stats
    return (
        f'<main class="wrap"><article class="prose">{crumbs(rel, "about.html", [("Home", rel + "index.html"), ("About", None)])}'
        '<p class="tag">Tenant Recipes editorial</p><h1>About Tenant Recipes</h1>'
        '<p class="lead">Practical, fact-checked recipes for the people who actually click through the Microsoft 365 admin portals: '
        'the exact steps, the pitfalls and a link to the primary source for every claim.</p>'
        f'<dl class="ab-stats"><div><dt>Tenant recipes</dt><dd>{n_rec}</dd></div><div><dt>Security entries</dt><dd>{n_cy}</dd></div>'
        f'<div><dt>Guides</dt><dd>{n_g}</dd></div><div><dt>Primary sources linked</dt><dd>{n_src}</dd></div></dl>'
        '<h2>Who it is for</h2><p>Microsoft 365, Entra and Intune administrators, security engineers and IT leads who have been asked to '
        '"roll out Copilot and AI agents — safely". If you need to know which setting to change, in which portal, and what can go wrong, '
        'this site is for you.</p>'
        '<h2>Why it exists</h2><p>Microsoft changes features, names and defaults every week. The official documentation is excellent but spread '
        'over hundreds of pages, Message center posts and blogs. Tenant Recipes turns that into short, task-focused playbooks — '
        'and keeps pointing back to the source, so you never have to take our word for it.</p>'
        '<h2>Who runs it</h2><p>Tenant Recipes is an independent side project, edited by a working Microsoft 365 administrator based in Sweden. '
        'We publish under the Tenant Recipes name rather than a personal byline on purpose: the content should stand on its sources, not on a name. '
        'That is why every page shows exactly what it was checked against and when, and why corrections happen in public.</p>'
        '<p>Tenant Recipes is <strong>not affiliated with, sponsored by or endorsed by Microsoft</strong> or any other vendor we write about. '
        'There are currently no sponsors and no affiliate links. If that ever changes, sponsored content will be clearly labelled and will never '
        'influence a recipe.</p>'
        '<h2>How a recipe is made</h2><ol class="ab-steps">'
        '<li><strong>Spot the change.</strong> We watch Microsoft Learn, the Microsoft 365 Message center, Microsoft blogs and, for the security section, '
        'vendor advisories and the CISA Known Exploited Vulnerabilities catalog.</li>'
        '<li><strong>Draft with AI assistance.</strong> Research and first drafts are AI-assisted. The AI does not get the last word.</li>'
        '<li><strong>Verify every claim.</strong> Each step, setting name, date and limitation is checked against the primary source, which is linked on the page. '
        'Anything we cannot confirm is removed, not softened.</li>'
        '<li><strong>Human in the loop.</strong> The editor owns the editorial rules, reviews flagged or contradictory claims and handles every correction.</li>'
        '<li><strong>Publish with receipts.</strong> Every page shows its sources, the date each was checked, and when the page was last updated.</li></ol>'
        f'<p>The full process, including our source hierarchy, is on the <a href="{rel}methodology.html">methodology page</a>.</p>'
        '<h2>What "last verified" means</h2><p>The date a page\'s steps were last compared with its linked sources. It is not a guarantee that '
        'Microsoft hasn\'t changed something since. Pages are re-checked when a change that affects them is announced, and at least every '
        f'{C.REVERIFY_DAYS} days; pages past that age show a "due for re-verification" notice.</p>'
        '<h2>Corrections</h2><p>Found an error? Every recipe, guide and security page has a <em>Report an error on this page</em> link that opens a '
        f'pre-filled <a href="{REPO}/issues">GitHub issue</a>. Confirmed errors are fixed, the page\'s "last updated" date changes, and the fix is '
        f'listed in the <a href="{rel}changelog.html">changelog</a>. You can also <a href="{REPO}/issues/new?template=suggest-recipe.yml">suggest a recipe</a>.</p>'
        '<h2>Contact</h2><p>' + contact_html() + '</p>'
        '<h2 id="disclaimer">Disclaimer</h2><p class="fine">Recipes are provided as-is for information. Settings, licensing and portal labels change; '
        'always confirm against the linked official documentation and test in a non-production tenant or pilot group first. '
        'You are responsible for changes you make in your environment. Product names are trademarks of their owners.</p>'
        '</article></main>')


def contact_html():
    if C.CONTACT_EMAIL:
        return (f'Email <a href="mailto:{E(C.CONTACT_EMAIL)}">{E(C.CONTACT_EMAIL)}</a>, or open a '
                f'<a href="{REPO}/issues/new/choose">GitHub issue</a> for corrections and suggestions.')
    return (f'The fastest way to reach the editor is a <a href="{REPO}/issues/new/choose">GitHub issue</a> (public — please leave out confidential details). '
            'Newsletter subscribers can also simply reply to any newsletter email; replies reach the editor privately. '
            'Sponsorship enquiries: open an issue and we will get back to you.')


def methodology_body(rel):
    tier = lambda n, t, d: f'<tr><td><span class="mt-n">{n}</span></td><td><strong>{t}</strong></td><td>{d}</td></tr>'
    return (
        f'<main class="wrap"><article class="prose">{crumbs(rel, "methodology.html", [("Home", rel + "index.html"), ("About", rel + "about.html"), ("Methodology", None)])}'
        '<p class="tag">Editorial standards</p><h1>How we fact-check</h1>'
        '<p class="lead">Every recipe is only as good as its sources. This page explains which sources we trust, in what order, '
        'how a claim gets onto the site, and what happens when it turns out to be wrong.</p>'
        '<h2>Source hierarchy — Microsoft 365 recipes and guides</h2>'
        '<p>When sources disagree, the higher tier wins, and we say so on the page if the difference matters.</p>'
        '<div class="cy-tw"><table class="mt-t"><thead><tr><th></th><th>Source</th><th>Used for</th></tr></thead><tbody>'
        + tier(1, '<a href="https://learn.microsoft.com/">Microsoft Learn</a>', 'Settings, portal paths, PowerShell, licensing requirements, limits. The default source for every step.')
        + tier(2, 'Microsoft 365 Message center', 'Dates and roll-out timing of announced changes (retirements, new defaults). When we cite a public mirror of a Message center post, we say so.')
        + tier(3, 'Official Microsoft blogs and the Microsoft 365 roadmap', 'Context and announcements not yet in Learn. Features only described here are marked as such.')
        + '</tbody></table></div>'
        '<h2>Source hierarchy — Security section</h2><div class="cy-tw"><table class="mt-t"><thead><tr><th></th><th>Source</th><th>Used for</th></tr></thead><tbody>'
        + tier(1, 'The vendor\'s own security advisory', 'Affected and fixed versions, the vendor\'s severity rating, workarounds, the vendor\'s exploitation statement.')
        + tier(2, '<a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog">CISA Known Exploited Vulnerabilities catalog</a>', 'Whether a CVE is known to be exploited in the wild, and the date it was added.')
        + tier(3, '<a href="https://nvd.nist.gov/">NIST National Vulnerability Database (NVD)</a>', 'CVE descriptions and CVSS scores when the vendor publishes none. Scores always name their source.')
        + tier(4, 'Vendor hardening guides', 'Hardening recipes (for example Microsoft, VMware/Broadcom or CIS-style vendor guidance).')
        + '</tbody></table></div>'
        '<p>If the vendor and CISA disagree — for example, the vendor says "not exploited" while CISA lists the CVE as known exploited — '
        'we show both statements openly rather than picking one.</p>'
        '<h2>What we do not use as sources</h2><ul><li>Forums, social media posts and other blogs (they can tip us off; they are never the citation).</li>'
        '<li>AI-generated answers, including our own drafts.</li><li>Undated or unofficial copies of documentation, except labelled mirrors of Message center posts.</li></ul>'
        '<h2>The process, step by step</h2><ol class="ab-steps">'
        '<li><strong>Collect.</strong> New and changed Microsoft documentation, Message center posts, vendor advisories and CISA KEV additions are scanned daily.</li>'
        '<li><strong>Draft.</strong> A first draft is written with AI assistance in a fixed structure: problem → steps → pitfalls → sources.</li>'
        '<li><strong>Verify.</strong> Every step and claim is compared with the linked source page, opened on the day of checking. Setting names are copied '
        'as the source writes them. Dates, versions and CVSS scores are never estimated.</li>'
        '<li><strong>Cut what cannot be confirmed.</strong> A claim without a matching source is removed. Preview features are labelled as preview. '
        'Our own estimates (for example, time per phase in a guide) are labelled as ours.</li>'
        '<li><strong>Automated checks.</strong> The build refuses to publish a page without sources, with malformed dates or CVE IDs, or with a broken internal link.</li>'
        '<li><strong>Human review.</strong> The editor sets these rules, reviews anything flagged as uncertain or contradictory, and handles every correction.</li>'
        '<li><strong>Publish and log.</strong> The page goes live with its sources and check dates, and the addition is listed in the changelog.</li></ol>'
        '<h2>What the dates mean</h2><dl class="mt-dl">'
        '<div><dt>Verified</dt><dd>The day the page\'s steps were last compared with all of its sources.</dd></div>'
        '<div><dt>Checked (per source)</dt><dd>The day that particular source page was opened and compared.</dd></div>'
        '<div><dt>Last updated</dt><dd>The day the page content last changed.</dd></div>'
        '<div><dt>First published</dt><dd>The day the page was added to the site.</dd></div></dl>'
        f'<p>Pages are re-verified when a change that affects them is announced, and at least every {C.REVERIFY_DAYS} days. '
        'Pages past that age automatically show a "due for re-verification" notice until they are checked again.</p>'
        '<h2>Corrections policy</h2><p>Anyone can report an error with the <em>Report an error on this page</em> link at the bottom of every page, '
        f'which opens a pre-filled <a href="{REPO}/issues">public GitHub issue</a>. Please include the source that shows the correct information. '
        'Confirmed errors are corrected on the page, the "last updated" date changes, and significant corrections are listed in the '
        f'<a href="{rel}changelog.html">changelog</a>. We do not silently rewrite history: if a recipe turns out to be wrong in a way that could have caused harm, '
        'we say so on the page.</p>'
        '<h2>Independence</h2><p>Tenant Recipes is not affiliated with Microsoft or any vendor, has no sponsors today and uses no affiliate links. '
        'The site sets no cookies and runs no analytics or ad trackers (see the <a href="' + rel + 'privacy.html">privacy policy</a>).</p>'
        '</article></main>')


def changelog_entries(R, CY, guides):
    """Group additions/updates by date, plus curated site entries from data/changelog.json."""
    days = {}
    def add(d, html):
        days.setdefault(d, []).append(html)
    site = json.loads((ROOT / "data" / "changelog.json").read_text())
    for s in site:
        add(s["date"], f'<li><span class="cl-k cl-site">Site</span>{esc(s["text"])}</li>')
    upd = {}
    for kind, items, pre in (("Recipe", R, "recipes/"), ("Security", CY, "security/")):
        for it in items:
            u = f'{pre}{it["id"]}.html'
            if it.get("created"):
                add(it["created"], f'<li><span class="cl-k cl-new">New {kind.lower()}</span><a href="{u}">{esc(it["title"])}</a></li>')
            if it.get("updated") and it.get("updated") != it.get("created"):
                upd.setdefault(it["updated"], []).append(f'<li><a href="{u}">{esc(it["title"])}</a></li>')
    for d, lis in upd.items():
        add(d, f'<li><span class="cl-k cl-upd">Updated</span>{len(lis)} page{"s" if len(lis) != 1 else ""} updated and re-verified'
               f'<details><summary>Show pages</summary><ul>{"".join(lis)}</ul></details></li>')
    for g in guides:
        add(g.VERIFIED, f'<li><span class="cl-k cl-new">Guide</span><a href="guides/{g.SLUG}.html">{esc(g.TITLE)}</a> (verified)</li>')
    return sorted(days.items(), reverse=True)


def changelog_body(rel, entries):
    out = ""
    for d, items in entries:
        out += f'<section class="cl-day"><h2 id="d-{d}">{fmt(d)}</h2><ul class="cl">{"".join(items)}</ul></section>'
    return (f'<main class="wrap"><article class="prose">{crumbs(rel, "changelog.html", [("Home", rel + "index.html"), ("Changelog", None)])}'
            '<p class="tag">What changed</p><h1>Changelog</h1>'
            f'<p class="lead">Every new page, update and correction, newest first. Generated automatically from the site data at each build. '
            f'Also available as an <a href="{rel}feed.xml">Atom feed</a>.</p>{out}</article></main>')


def search_body(rel):
    return (f'<main class="wrap"><article class="prose">{crumbs(rel, "search.html", [("Home", rel + "index.html"), ("Search", None)])}'
            '<h1>Search Tenant Recipes</h1><form class="ss-f" action="search.html" method="get" role="search">'
            '<label class="sr" for="ss-q">Search</label><input id="ss-q" name="q" type="search" placeholder="e.g. MFA, EEEU, LAPS, agents, VMware" autofocus>'
            '<button class="btn p" type="submit">Search</button></form><div id="ss-chips" class="chips"></div><p id="ss-n" class="fine"></p><ol id="ss-r" class="ss-r"></ol>'
            '<noscript><p>Search needs JavaScript. Browse the <a href="index.html#library">recipe library</a> or the <a href="security/index.html">security section</a>.</p></noscript>'
            '</article></main><script src="data/search.js"></script><script src="assets/search.js"></script>')


def search_index(R, CY, guides, AREA):
    idx = []
    for r in R:
        idx.append({"k": "Recipe", "c": r["category"], "t": r["title"], "u": f'recipes/{r["id"]}.html', "s": r["problem"],
                    "x": " ".join(r["steps"] + r.get("pitfalls", []))})
    for e in CY:
        idx.append({"k": "Security", "c": AREA[e["area"]][0], "t": e["title"], "u": f'security/{e["id"]}.html', "s": e["summary"],
                    "x": " ".join(e["steps"] + [c["id"] for c in e.get("cves", [])] + [e.get("vendor", ""), e.get("product", "")])})
    for g in guides:
        idx.append({"k": "Guide", "c": "Pillar guide", "t": g.TITLE, "u": f"guides/{g.SLUG}.html", "s": g.DESC,
                    "x": " ".join(st["t"] for ph in g.PHASES for st in ph["steps"])})
        for i, ph in enumerate(g.PHASES, 1):
            idx.append({"k": "Guide", "c": f"Phase {i}", "t": f'{g.SHORT}: {ph["title"]}', "u": f'guides/{g.SLUG}.html#phase-{i}-{ph["id"]}',
                        "s": ph["goal"], "x": " ".join(st["t"] + " " + " ".join(st["do"]) for st in ph["steps"])})
    for t, u, s in (("About Tenant Recipes", "about.html", "Who runs the site, independence, corrections and contact."),
                    ("Methodology: how we fact-check", "methodology.html", "Source hierarchy and verification process."),
                    ("Changelog", "changelog.html", "Every new page, update and correction."),
                    ("Newsletter", "newsletter.html", "The free weekly Tenant Recipes brief.")):
        idx.append({"k": "Page", "c": "Site", "t": t, "u": u, "s": s, "x": ""})
    return "window.SEARCH=" + json.dumps(idx, ensure_ascii=False) + ";"


def atom(R, CY, guides):
    items = []
    for r in R:
        items.append((r.get("updated") or r.get("last_verified") or "", r["title"], f'recipes/{r["id"]}.html', r["problem"], r["category"]))
    for e in CY:
        items.append((e.get("updated") or e.get("last_verified") or "", e["title"], f'security/{e["id"]}.html', e["summary"], "Security"))
    for g in guides:
        items.append((g.VERIFIED, g.TITLE, f"guides/{g.SLUG}.html", g.DESC, "Guide"))
    items = sorted([i for i in items if i[0]], key=lambda i: (i[0], i[1]), reverse=True)[:60]
    newest = items[0][0] if items else TODAY.isoformat()
    ent = "".join(
        f'<entry><title>{esc(t)}</title><link href="{SITE}/{u}"/><id>{SITE}/{u}</id><updated>{d}T00:00:00Z</updated>'
        f'<category term="{esc(c)}"/><summary>{esc(s)}</summary></entry>' for d, t, u, s, c in items)
    return ('<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">'
            f'<title>{esc(C.SITE_NAME)}</title><subtitle>{esc(C.SITE_TAGLINE)}</subtitle>'
            f'<link href="{SITE}/feed.xml" rel="self"/><link href="{SITE}/"/><id>{SITE}/</id>'
            f'<updated>{newest}T00:00:00Z</updated><author><name>Tenant Recipes editorial</name></author>{ent}</feed>\n')
