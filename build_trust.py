"""Trust & navigation layer: header/footer, breadcrumbs, verification panels, "Report an error" links,
About / Methodology / Changelog / Search pages, the site-wide search index and the Atom feed.
Everything shown is computed from data (recipes, cyber entries, guides, data/changelog.json) at build time."""
import json, re, datetime, pathlib, subprocess
from html import escape as E
from urllib.parse import quote
import site_config as C
import build_markers as MK

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
NAV_LINKS = [("Recipes", "index.html#library"), ("Guides", "guides/index.html"), ("News", "news/index.html"), ("Security", "security/index.html"), ("Tools", "tools/index.html"), ("Code", "code/index.html"), ("Policies", "policies/index.html"),
             ("Links", "links/index.html"), ("What's new", "changelog/index.html"), ("Status", "status/index.html"), ("About", "about.html")]


def nav(rel):
    """Header: logo mark + wordmark left; inline links on wide screens; search + menu button right.
    The menu panel sits in normal flow under the nav (no fixed positioning, no backdrop-filter ancestor: iOS Safari hit-testing); assets/ui.js toggles it."""
    links = "".join(f'<a href="{rel}{u}">{esc(t)}</a>' for t, u in NAV_LINKS)
    menu = "".join(f'<a href="{rel}{u}">{esc(t)}</a>' for t, u in NAV_LINKS if t != "About") \
        + f'<a href="{rel}newsletter.html">Newsletter</a><a href="{rel}about.html">About</a>'
    return (f'<header class="sh" id="top" tabindex="-1"><nav aria-label="Main">'
            f'<a class="logo" href="{rel}index.html" aria-label="Tenant Recipes, home"><img class="logo-m" src="{rel}assets/mark-64.png" srcset="{rel}assets/mark-128.png 2x" alt="" width="32" height="32">'
            f'<span class="logo-w">Tenant <b>Recipes</b></span></a>'
            f'<div class="nv"><div class="nv-l">{links}</div>'
            f'<a class="nv-sb" href="{rel}search/index.html" data-sx-open aria-label="Search" title="Search (press /)">{icon("search")}<span class="nv-sbl">Search</span><kbd>/</kbd></a>'
            f'<a class="nv-cta" href="{rel}newsletter.html">Newsletter</a>'
            f'<button type="button" class="nv-mb" aria-expanded="false" aria-controls="nv-menu" aria-label="Menu">'
            f'<svg class="ic ic-o" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
            f'<svg class="ic ic-x" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div></nav>'
            f'<div class="nv-md" id="nv-menu" role="navigation" aria-label="All sections" hidden>{menu}</div>{whats_new_bar(rel)}</header>')


# ---------------------------------------------------------------- What's new bar (under the header, every page)
WN_N = 8        # entries in the expanded list
WN_TYPES = {"guide", "recipe", "news", "security", "tool", "policy", "site"}


def _changelog_sorted():
    """data/changelog.json newest first (date, then optional HH:MM Europe/Stockholm time)."""
    site = json.loads((ROOT / "data" / "changelog.json").read_text())
    return sorted(site, key=lambda x: (x["date"], x.get("time", "")), reverse=True)


def _wn_iso(d, t):
    """ISO datetime with the correct Stockholm offset (CET/CEST), or the bare date when no time is logged."""
    if not t:
        return d
    try:
        from zoneinfo import ZoneInfo
        return datetime.datetime.fromisoformat(f"{d}T{t}").replace(tzinfo=ZoneInfo("Europe/Stockholm")).isoformat(timespec="minutes")
    except Exception:
        return f"{d}T{t}"


def _wn_title(x):
    if x.get("title"):
        return x["title"]
    t = x["text"].split(". ")[0]
    return t if len(t) <= 70 else t[:69].rsplit(" ", 1)[0] + "…"


def _wn_blurb(x):
    if x.get("blurb"):
        return x["blurb"]
    rest = x["text"][len(x["text"].split(". ")[0]):].lstrip(". ")
    return rest if len(rest) <= 110 else rest[:109].rsplit(" ", 1)[0] + "…"


def whats_new_bar(rel):
    """Thin bar at the bottom edge of the sticky header: the latest data/changelog.json entries (date, Stockholm time,
    type, linked title, one-line blurb). Collapsed it shows the newest entry (two on wide screens); the toggle opens a
    dropdown with the latest WN_N entries, positioned absolutely so the sticky header never changes height."""
    items = _changelog_sorted()[:WN_N]
    if not items:
        return ""
    week = (TODAY - datetime.timedelta(days=6)).isoformat()
    n_week = sum(1 for x in _changelog_sorted() if x["date"] >= week)
    lis = ""
    for x in items:
        ty = (x.get("type") or "Site").strip()
        k = ty.lower() if ty.lower() in WN_TYPES else "site"
        when = fmt(x["date"]).rsplit(" ", 1)[0] + (f' {x["time"]}' if x.get("time") else "")
        href = rel + (x.get("url") or f'changelog/index.html#d-{x["date"]}')
        lis += (f'<li><a href="{esc(href)}"><time datetime="{_wn_iso(x["date"], x.get("time"))}">{esc(when)}</time>'
                f'<span class="wn-k wn-{k}">{esc(ty)}</span><b>{esc(_wn_title(x))}</b><span class="wn-d">{esc(_wn_blurb(x))}</span></a></li>')
    cnt = f"{n_week} update{'s' if n_week != 1 else ''} this week" if n_week else f"Latest {len(items)}"
    return (f'<div class="wn" id="wn"><div class="wn-in">'
            f'<a class="wn-h" href="{rel}changelog/index.html">{icon("clock")}<span>What\'s new</span></a>'
            f'<ol class="wn-l" id="wn-l" aria-label="Latest updates (times in Stockholm time)">{lis}'
            f'<li class="wn-all"><a href="{rel}changelog/index.html">All updates and the full changelog →</a></li></ol>'
            f'<button type="button" class="wn-x" aria-expanded="false" aria-controls="wn-l" hidden><span class="wn-c">{esc(cnt)}</span><span class="wn-cs">{n_week or len(items)} new</span>'
            f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></button></div></div>')


def ad_slot(name):
    """Ad placeholder at a natural break point. Renders nothing unless site_config.ADS_ENABLED is True."""
    if not getattr(C, "ADS_ENABLED", False):
        return ""
    return (f'<aside class="sponsor-slot" data-slot="{name}" aria-label="Advertisement"><!-- ad slot: {name} -->'
            '<span class="slot-label">Advertisement</span></aside>')


def footer(rel, guide_slug, path="", title="", updated=None):
    col = lambda h, links: (f'<div><h4>{h}</h4><ul>' + "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in links) + '</ul></div>')
    rep = report_url(path, title or C.SITE_NAME) if path else f"{REPO}/issues/new/choose"
    bar = (f'<div class="sf-pg"><span>{icon("clock")}Last updated <time datetime="{updated}">{fmt(updated)}</time></span>'
           f'<a href="{rel}methodology.html">{icon("shield")}Methodology: how we verify</a>'
           f'<a href="{rep}" rel="nofollow">{icon("alert")}Report an error on this page</a>'
           f'<a href="{edit_url(path, title or C.SITE_NAME) if path else REPO + "/issues/new/choose"}" rel="nofollow">Suggest an edit</a>'
           f'<a href="{rel}contact/index.html">Contact</a></div>') if updated else ""
    return ('<footer class="sf">' + bar + '<div class="sf-in">'
            f'<div class="sf-brand"><img src="{rel}assets/logo-dark.svg" alt="Tenant Recipes" width="140" height="32" loading="lazy" decoding="async">'
            '<p>Fact-checked AI &amp; security recipes for Microsoft 365 admins. An independent project — not affiliated with Microsoft or any vendor.</p>'
            f'<p class="sf-ed">{EDITOR}</p></div>'
            + col("Content", [("Recipes", f"{rel}index.html#library"), ("Guides", f"{rel}guides/index.html"),
                              ("Secure Copilot rollout", f"{rel}guides/{guide_slug}.html"), ("Windows 11 CIS hardening", f"{rel}guides/windows-11-cis-hardening.html"), ("Cloud hardening + adversary emulation", f"{rel}guides/cloud-hardening-adversary-emulation.html"), ("Azure Arc onboarding at scale", f"{rel}guides/azure-arc-onboarding-enterprise-scale.html"), ("Azure Update Manager at scale", f"{rel}guides/azure-update-manager-enterprise-patching.html"), ("Admin By Request: just-in-time admin", f"{rel}guides/admin-by-request-endpoint-privilege.html"),
                              ("Entra Private Access: replace VPN", f"{rel}guides/entra-private-access-vpn-replacement.html"), ("AD CS hardening (Tier 0)", f"{rel}guides/adcs-hardening-tier0.html"), ("Admin By Request: Intune Win32 packaging", f"{rel}guides/admin-by-request-intune-win32-packaging.html"), ("News &amp; retirements", f"{rel}news/index.html"), ("Microsoft cloud status", f"{rel}status/index.html"), ("Security &amp; vulnerability watch", f"{rel}security/index.html"), ("Security tools &amp; testing", f"{rel}tools/index.html"), ("Policy templates", f"{rel}policies/index.html"), ("Quick guide: 5 Copilot license checks", f"{rel}guides/copilot-license-checks.html"),
                              ("Code Library", f"{rel}code/index.html"), ("IT link hub", f"{rel}links/index.html"), ("AI link department", f"{rel}links/ai/index.html"), ("Search", f"{rel}search/index.html")])
            + col("Trust", [("About", f"{rel}about.html"), ("Methodology", f"{rel}methodology.html"), ("Editor", f"{rel}author/index.html"), ("What's new (changelog)", f"{rel}changelog/index.html"),
                            ("Contact &amp; corrections", f"{rel}contact/index.html"), ("Report an issue", f"{REPO}/issues/new/choose")])
            + col("Stay updated", [("Newsletter", f"{rel}newsletter.html"), ("Sample issue", f"{rel}newsletter-sample.html"), (f"X (@{C.X_HANDLE})", f"https://x.com/{C.X_HANDLE}"), ("Atom / RSS feed", f"{rel}feed.xml"),
                                   ("Suggest a recipe", f"{REPO}/issues/new?template=suggest-recipe.yml")])
            + col("Legal", [("Privacy policy", f"{rel}privacy.html"), ("Disclaimer", f"{rel}about.html#disclaimer"), ("Terms of use", f"{rel}about.html#terms")])
            + f'</div><p class="sf-ind">{icon("shield")}<strong>Independent, not affiliated with Microsoft.</strong> No sponsors, no affiliate links; every claim links to its source.</p>'
            f'<p class="sf-b">© {TODAY.year} Tenant Recipes · Microsoft, Microsoft 365, Copilot, Entra, Intune and Purview are trademarks of the Microsoft group of companies. '
            'Other product names belong to their owners.</p></footer>')


# ---------------------------------------------------------------- per-page trust pieces
def crumbs(rel, path, items):
    """items: list of (label, href-or-None). Renders visible breadcrumbs + schema.org BreadcrumbList."""
    vis = " / ".join(f'<a href="{h}">{esc(t)}</a>' if h else f'<span aria-current="page">{esc(t)}</span>' for t, h in items)
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": []}
    for i, (t, h) in enumerate(items, 1):
        el = {"@type": "ListItem", "position": i, "name": t}
        if h and SITE:
            a = _abs(path, h).split("#")[0]
            a = a[:-len("index.html")] if a == "index.html" or a.endswith("/index.html") else a
            el["item"] = SITE + "/" + a
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


def edit_url(path, title):
    """Pre-filled 'outdated information / suggest an edit' issue for one page (title + URL in the form)."""
    url = f"{SITE}/{path}"
    return (f"{REPO}/issues/new?template=outdated-info.yml&amp;title={quote('[Edit] ' + title)}"
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
            f'<div class="vs-f"><p>Spotted something wrong or outdated? Corrections are public and logged in the <a href="{rel}changelog/index.html">changelog</a>.</p>'
            f'{report_link(path, title, "rp btn")}</div></section>')


# ---------------------------------------------------------------- content pages
def about_body(rel, stats):
    n_rec, n_cy, n_g, n_src = stats
    return (
        page_hero(rel, crumbs_dark(rel, "about.html", [("Home", rel + "index.html"), ("About", None)]), "Tenant Recipes editorial",
                  "About Tenant Recipes", 'Practical, fact-checked recipes for the people who actually click through the Microsoft 365 admin portals: '
                  'the exact steps, the pitfalls and a link to the primary source for every claim.', kind="page")
        + f'<main class="wrap pg"><article class="prose doc">'
        + '<aside class="co co-ok ind-note" role="note"><p class="co-h">' + icon("shield") + 'Independent, not affiliated with Microsoft</p>'
        '<p>Tenant Recipes is an independent project. It is not affiliated with, sponsored by or endorsed by Microsoft or any other vendor we cover, '
        'has no sponsors and uses no affiliate links. Product names are trademarks of their owners.</p></aside>'
        f'<dl class="ab-stats"><div><dt>Tenant recipes</dt><dd>{n_rec}</dd></div><div><dt>Security entries</dt><dd>{n_cy}</dd></div>'
        f'<div><dt>Guides</dt><dd>{n_g}</dd></div><div><dt>Primary sources linked</dt><dd>{n_src}</dd></div></dl>'
        '<h2>Who it is for</h2><p>Microsoft 365, Entra and Intune administrators, security engineers and IT leads who have been asked to '
        '"roll out Copilot and AI agents — safely". If you need to know which setting to change, in which portal, and what can go wrong, '
        'this site is for you.</p>'
        f'<aside class="ed" aria-label="About the editor"><span class="ed-i">{icon("user")}</span><div><p class="ed-h">About the editor</p><p>{EDITOR} <a href="{rel}author/index.html">Editor profile</a></p></div></aside>'
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
        f'listed in the <a href="{rel}changelog/index.html">changelog</a>. You can also <a href="{REPO}/issues/new?template=suggest-recipe.yml">suggest a recipe</a>.</p>'
        '<h2>Contact</h2><p>' + contact_html() + f' All contact routes, including how to report a security problem, are on the <a href="{rel}contact/index.html">contact page</a>.</p>'
        '<h2 id="disclaimer">Disclaimer</h2><p class="fine">Recipes are provided as-is for information. Settings, licensing and portal labels change; '
        'always confirm against the linked official documentation and test in a non-production tenant or pilot group first. '
        'You are responsible for changes you make in your environment. Product names are trademarks of their owners.</p>'
        '<h2 id="terms">Terms of use</h2><p class="fine">You are welcome to read, link to and quote short excerpts with attribution. '
        'The content of this site may not be used to train, fine-tune or evaluate AI/machine-learning models, or be collected by bulk scraping '
        f'or automated download, without prior written permission. Search-engine indexing is allowed. See <a href="{rel}robots.txt">robots.txt</a> '
        f'and <a href="{rel}ai.txt">ai.txt</a>.</p>'
        '</article></main>')


def author_box(rel):
    """Small byline box for guides: anonymous editor, links to /author/."""
    return (f'<aside class="ed ed-by" aria-label="Author"><span class="ed-i">{icon("user")}</span><div><p class="ed-h">Author</p>'
            f'<p>Written and technically reviewed by the <a href="{rel}author/index.html">Tenant Recipes editor</a>. '
            f'<a href="{rel}methodology.html">How we verify</a></p></div></aside>')


def author_body(rel):
    li = lambda t, d: f'<li><strong>{t}</strong> {d}</li>'
    return (
        page_hero(rel, crumbs_dark(rel, "author/index.html", [("Home", rel + "index.html"), ("About", rel + "about.html"), ("Editor", None)]),
                  "Tenant Recipes editorial", "About the editor",
                  'Every recipe, guide and security entry on Tenant Recipes is written and technically reviewed by one editor. '
                  'This page explains who that is in professional terms, what they focus on and how they work.', kind="page")
        + '<main class="wrap pg"><article class="prose doc">'
        + f'<aside class="ed" aria-label="Editor profile"><span class="ed-i">{icon("user")}</span><div><p class="ed-h">Editor profile</p>'
        '<p>IT professional since 1999, focused on Microsoft technology since 2013. Hands-on with tenant administration, identity and endpoint '
        'security in production environments.</p></div></aside>'
        '<h2>Focus areas</h2><ul>'
        + li("Microsoft 365:", "tenant configuration, Exchange Online, SharePoint and Teams governance, licensing.")
        + li("Microsoft Entra ID:", "Conditional Access, authentication methods, privileged roles and PIM, app consent and workload identities.")
        + li("Intune:", "compliance and configuration profiles, security baselines, Windows Autopilot and update rings.")
        + li("Microsoft Defender:", "Defender for Endpoint, Defender for Office 365, attack surface reduction and exposure management.")
        + li("Microsoft Purview:", "sensitivity labels, DLP, retention and audit.")
        + li("Copilot governance:", "oversharing controls, licensing, agent and plugin governance before and after roll-out.")
        + li("Security hardening:", "Windows 11 and server hardening, CIS-style baselines, vulnerability triage and offensive testing tools.")
        + '</ul>'
        '<h2>How content is fact-checked</h2>'
        '<p>Research and first drafts are AI-assisted; the AI never gets the last word. Every step, setting name, date and limitation is compared with '
        'the primary source on the day of checking, and the source is linked on the page with that date. In order of precedence:</p><ul>'
        '<li><a href="https://learn.microsoft.com/">Microsoft Learn</a> for settings, portal paths, PowerShell, licensing and limits.</li>'
        '<li>Microsoft 365 Message center and official Microsoft blogs and roadmap for dates and announced changes.</li>'
        '<li>Vendor security advisories, the <a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog">CISA Known Exploited Vulnerabilities catalog</a> '
        'and <a href="https://nvd.nist.gov/">NIST NVD</a> for the security section.</li></ul>'
        '<p>Anything that cannot be confirmed is removed, not softened. Third-party standards such as CIS Benchmarks are paraphrased in our own words and linked, never copied. '
        f'The full source hierarchy is on the <a href="{rel}methodology.html">methodology page</a>.</p>'
        '<h2>Principles</h2><ul>'
        + li("Least privilege.", "Recipes use the narrowest role, scope and permission that gets the job done, and say which role is required.")
        + li("Production-safe changes.", "Pilot groups, report-only modes and rollback steps come before tenant-wide enforcement.")
        + li("Sources over opinion.", "Every claim links to its source and shows when it was last verified.")
        + li("Independent.", "Not affiliated with, sponsored by or endorsed by Microsoft or any other vendor. No sponsors, no affiliate links.")
        + '</ul>'
        '<h2>Why there is no name</h2><p>Tenant Recipes is published under its own name on purpose. No employer is named and no personal byline is used: '
        'the content should stand on its sources, not on a person or a company. That is also why corrections happen in public, '
        f'in the <a href="{rel}changelog/index.html">changelog</a>.</p>'
        '<h2>Get in touch</h2><ul>'
        f'<li><a href="{REPO}/issues/new/choose">Report an error</a> (public GitHub issue, please leave out confidential details).</li>'
        f'<li><a href="{REPO}/issues/new?template=suggest-recipe.yml">Suggest a recipe</a>.</li>'
        f'<li>All contact routes and responsible disclosure: <a href="{rel}contact/index.html">contact page</a>.</li>'
        f'<li>Read more <a href="{rel}about.html">about Tenant Recipes</a>.</li></ul>'
        '</article></main>')


def contact_html():
    if C.CONTACT_EMAIL:
        return (f'Email <a href="mailto:{E(C.CONTACT_EMAIL)}">{E(C.CONTACT_EMAIL)}</a>, or open a '
                f'<a href="{REPO}/issues/new/choose">GitHub issue</a> for corrections and suggestions.')
    return (f'The fastest way to reach the editor is a <a href="{REPO}/issues/new/choose">GitHub issue</a> (public — please leave out confidential details). '
            'Newsletter subscribers can also simply reply to any newsletter email; replies reach the editor privately. '
            'Sponsorship enquiries: open an issue and we will get back to you.')


def contact_body(rel):
    """/contact/: every way to reach the editors. No personal identity; GitHub issues are the primary channel until CONTACT_EMAIL is set."""
    new = f"{REPO}/issues/new"
    card = lambda h, d, links: (f'<div class="ct-c"><h3>{h}</h3><p>{d}</p><p>' + " · ".join(f'<a href="{u}" rel="nofollow">{t}</a>' for t, u in links) + '</p></div>')
    mail = (f'<p>Email: <a href="mailto:{esc(C.CONTACT_EMAIL)}">{esc(C.CONTACT_EMAIL)}</a> (read by the editors; we aim to reply within a few working days).</p>'
            if C.CONTACT_EMAIL else
            '<p>There is no public email address yet. Until there is, GitHub issues are the primary channel, and newsletter subscribers can simply '
            'reply to any newsletter email; replies reach the editors privately.</p>')
    _sec = getattr(C, "SECURITY_EMAIL", "") or C.CONTACT_EMAIL
    sec_mail = (f' or email <a href="mailto:{esc(_sec)}">{esc(_sec)}</a> with "Security" in the subject' if _sec else "")
    return (
        page_hero(rel, crumbs_dark(rel, "contact/index.html", [("Home", rel + "index.html"), ("About", rel + "about.html"), ("Contact", None)]),
                  "Contact &amp; corrections", "Contact Tenant Recipes",
                  'Found a mistake, a setting that moved, a broken link, or a topic we should cover? This page lists every way to reach the editors '
                  'and what happens next.', kind="page")
        + '<main class="wrap pg"><article class="prose doc">'
        + '<aside class="co co-warn" role="note"><p class="co-h">' + icon("alert") + 'Issues are public</p>'
        '<p>GitHub issues can be read by anyone. Never include tenant names, domain names, user names, object IDs, screenshots with personal data, '
        'logs, passwords, keys or other confidential details. Describe the problem in general terms instead.</p></aside>'
        '<h2>Report a problem with a page</h2>'
        '<p>Every recipe, guide, security entry, tool page and policy template has links at the bottom: <em>Report an error on this page</em> and '
        '<em>Suggest an edit</em>. They open a GitHub issue with the page title and URL already filled in. You can also start here:</p>'
        '<div class="ct-g">'
        + card("Content error", "A step, setting name, licence requirement or statement is wrong.", [("Report an error", f"{new}?template=report-error.yml")])
        + card("Outdated information", "A portal path, feature name, default or date has changed since the page was verified.", [("Report outdated info", f"{new}?template=outdated-info.yml")])
        + card("Broken link", "A link on the site, or a source we cite, no longer works.", [("Report a broken link", f"{new}?template=broken-link.yml")])
        + card("Suggest a topic", "A task, problem or tool you would like a recipe or guide for.", [("Suggest a topic", f"{new}?template=suggest-recipe.yml")])
        + '</div>'
        '<h2>What happens next</h2><ol>'
        '<li>The editors read every issue and check the claim against the primary source (see the <a href="' + rel + 'methodology.html">methodology</a>).</li>'
        '<li>Confirmed errors are fixed, the page\'s "last updated" date changes and the correction is listed in the '
        f'<a href="{rel}changelog/index.html">changelog</a>.</li>'
        '<li>The issue is closed with a short note on what changed, or why nothing changed.</li></ol>'
        '<h2>Contact the editors</h2>' + mail +
        f'<p>Prefer GitHub? <a href="{new}/choose" rel="nofollow">Open an issue</a> and choose the closest template. Sponsorship and partnership enquiries are '
        'welcome the same way; the site currently has no sponsors and no affiliate links (see <a href="' + rel + 'about.html">About</a>).</p>'
        '<h2 id="security">Report a security problem (responsible disclosure)</h2>'
        '<p>If you find a security problem with this website or its repository, for example a script or link that could be abused, please report it '
        f'<strong>privately</strong>: use <a href="{REPO}/security/advisories/new" rel="nofollow">GitHub private vulnerability reporting</a>{sec_mail}. '
        'Do not open a public issue for security problems.</p><ul>'
        '<li>Include the affected URL, what you observed and how to reproduce it.</li>'
        '<li>Test only against this website, do not access other people\'s data, and do not run denial-of-service or automated high-volume scans.</li>'
        '<li>Give us reasonable time to fix the problem before you publish anything. We will confirm receipt and keep you updated.</li>'
        '<li>This is a volunteer project: there is no bug bounty, but we are happy to credit you in the changelog if you want.</li></ul>'
        '<p class="fine">Vulnerabilities in Microsoft or other vendors\' products are not ours to fix: report those to the vendor, for Microsoft via the '
        '<a href="https://msrc.microsoft.com/report/vulnerability">Microsoft Security Response Center</a>. Our machine-readable contact file is at '
        f'<a href="{rel}.well-known/security.txt">/.well-known/security.txt</a>.</p>'
        '<h2>Privacy</h2><p>' + ('Email you send us is used only to answer you and is not shared. ' if C.CONTACT_EMAIL else '') + 'Contacting us through GitHub is subject to GitHub\'s own terms and privacy statement. We do not use contact forms, '
        f'cookies or tracking for any of this. See the <a href="{rel}privacy.html">privacy policy</a>.</p>'
        '</article></main>')


def security_txt():
    """RFC 9116 security.txt (served at /.well-known/security.txt and /security.txt). Expires about one year after the build."""
    exp = (datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0) + datetime.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = []
    sec = getattr(C, "SECURITY_EMAIL", "") or C.CONTACT_EMAIL
    if sec:
        lines.append(f"Contact: mailto:{sec}")
    lines += [f"Contact: {REPO}/security/advisories/new", f"Contact: {SITE}/contact/#security", f"Expires: {exp}",
              "Preferred-Languages: en, sv", f"Canonical: {SITE}/.well-known/security.txt", f"Policy: {SITE}/contact/#security"]
    return "\n".join(lines) + "\n"


def methodology_body(rel):
    tier = lambda n, t, d: f'<tr><td><span class="mt-n">{n}</span></td><td><strong>{t}</strong></td><td>{d}</td></tr>'
    return (
        page_hero(rel, crumbs_dark(rel, "methodology.html", [("Home", rel + "index.html"), ("About", rel + "about.html"), ("Methodology", None)]),
                  "Editorial standards", "How we fact-check", 'Every recipe is only as good as its sources. This page explains which sources we trust, in what order, '
                  'how a claim gets onto the site, and what happens when it turns out to be wrong.', kind="page")
        + '<main class="wrap pg"><article class="prose doc">'
        + '<aside class="co co-ok ind-note" role="note"><p class="co-h">' + icon("shield") + 'Independent, not affiliated with Microsoft</p>'
        '<p>Tenant Recipes is an independent project. It is not affiliated with, sponsored by or endorsed by Microsoft or any other vendor we cover, '
        'has no sponsors and uses no affiliate links. Product names are trademarks of their owners.</p></aside>'
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
        + MK.legend_html(rel) +
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
        f'<a href="{rel}changelog/index.html">changelog</a>. We do not silently rewrite history: if a recipe turns out to be wrong in a way that could have caused harm, '
        'we say so on the page.</p>'
        '<h2>Independence</h2><p>Tenant Recipes is not affiliated with Microsoft or any vendor, has no sponsors today and uses no affiliate links. '
        + ('The site sets no cookies and runs no ad trackers; it only counts page views in aggregate with cookie-free GoatCounter'
           if (getattr(C, "GOATCOUNTER_CODE", "") or "").strip() else 'The site sets no cookies and runs no analytics or ad trackers')
        + ' (see the <a href="' + rel + 'privacy.html">privacy policy</a>).</p>'
        '</article></main>')


def git_history():
    """{date: [commit subjects]} from git log (Stockholm dates). Empty if git/history is unavailable (e.g. shallow CI checkout)."""
    try:
        out = subprocess.run(["git", "log", "--no-merges", "--date=format-local:%Y-%m-%d", "--format=%ad%x09%s"], cwd=ROOT,
                             capture_output=True, text=True, timeout=20, env={"TZ": "Europe/Stockholm", "PATH": "/usr/bin:/bin:/usr/local/bin"}).stdout
    except Exception:
        return {}
    days = {}
    for line in out.splitlines():
        d, _, subj = line.partition("\t")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and subj:
            days.setdefault(d, []).append(subj)
    return days


def _subj(s, n=150):
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "…"


def changelog_entries(R, CY, guides, rel=""):
    """Group additions/updates by date: curated notes (data/changelog.json), data dates of recipes, guides and
    security entries, and the git history of the site (one collapsible line per day)."""
    days = {}
    def add(d, html):
        days.setdefault(d, []).append(html)
    site = json.loads((ROOT / "data" / "changelog.json").read_text())
    for s in site:
        tm = f'<time class="cl-tm" datetime="{_wn_iso(s["date"], s.get("time"))}">{s["time"]}</time> ' if s.get("time") else ""
        lk = f' <a href="{rel}{esc(s["url"])}">Open →</a>' if s.get("url") else ""
        add(s["date"], f'<li>{tm}<span class="cl-k cl-site">{esc(s.get("type") or "Site")}</span>{esc(s["text"])}{lk}</li>')
    upd = {}
    for kind, items, pre in (("Recipe", R, "recipes/"), ("Security", CY, "security/")):
        for it in items:
            u = f'{rel}{pre}{it["id"]}.html'
            if it.get("created"):
                add(it["created"], f'<li><span class="cl-k cl-new">New {kind.lower()}</span><a href="{u}">{esc(it["title"])}</a></li>')
            if it.get("updated") and it.get("updated") != it.get("created"):
                upd.setdefault(it["updated"], []).append(f'<li><a href="{u}">{esc(it["title"])}</a></li>')
    for d, lis in upd.items():
        add(d, f'<li><span class="cl-k cl-upd">Updated</span>{len(lis)} page{"s" if len(lis) != 1 else ""} updated and re-verified'
               f'<details><summary>Show pages</summary><ul>{"".join(lis)}</ul></details></li>')
    for g in guides:
        add(g.VERIFIED, f'<li><span class="cl-k cl-new">Guide</span><a href="{rel}guides/{g.SLUG}.html">{esc(g.TITLE)}</a> (verified)</li>')
    for d, subs in git_history().items():
        add(d, f'<li><span class="cl-k cl-git">Changes</span>{len(subs)} published change{"s" if len(subs) != 1 else ""} to the site'
               f'<details><summary>Show change log</summary><ul>{"".join(f"<li>{esc(_subj(x))}</li>" for x in subs)}</ul></details></li>')
    return sorted(days.items(), reverse=True)


def changelog_body(rel, entries):
    out = ""
    for d, items in entries:
        out += f'<section class="cl-day"><h2 id="d-{d}"><time datetime="{d}">{fmt(d)}</time></h2><ul class="cl">{"".join(items)}</ul></section>'
    return (page_hero(rel, crumbs_dark(rel, "changelog/index.html", [("Home", rel + "index.html"), ("What's new", None)]), "Changelog", "What's new",
                      'Every new recipe, guide and security entry, every update and correction, newest first. Generated automatically at each build '
                      'from the content dates and the site\'s publishing history. '
                      f'Also available as an <a href="{rel}feed.xml">Atom feed</a>.', kind="page")
            + f'<main class="wrap pg"><article class="prose doc">{out}</article></main>')


def search_body(rel):
    return (page_hero(rel, crumbs_dark(rel, "search.html", [("Home", rel + "index.html"), ("Search", None)]), "Search",
                      "Search Tenant Recipes", "Every recipe, guide phase and security entry — searched in your browser, nothing is sent anywhere.", kind="page")
            + '<main class="wrap pg"><article class="prose doc"><form class="ss-f" action="search.html" method="get" role="search">'
            '<label class="sr" for="ss-q">Search</label><input id="ss-q" name="q" type="search" placeholder="e.g. MFA, EEEU, LAPS, agents, VMware" autofocus>'
            '<button class="btn p" type="submit">Search</button></form><div id="ss-chips" class="chips"></div><p id="ss-n" class="fine"></p><ol id="ss-r" class="ss-r"></ol>'
            '<noscript><p>Search needs JavaScript. Browse the <a href="index.html#library">recipe library</a> or the <a href="security/index.html">security section</a>.</p></noscript>'
            '</article></main><script src="data/search.js"></script><script src="assets/search.js"></script>')


def search_index(R, CY, guides, AREA, extra=()):
    idx = list(extra)
    for r in R:
        idx.append({"k": "Recipe", "c": r["category"], "t": r["title"], "u": f'recipes/{r["id"]}.html', "s": r["problem"],
                    "x": " ".join(r["steps"] + r.get("pitfalls", []))})
    for e in CY:
        idx.append({"k": "Security", "c": AREA[e["area"]][0], "t": e["title"], "u": f'security/{e["id"]}.html', "s": e["summary"],
                    "x": " ".join(e["steps"] + [c["id"] for c in e.get("cves", [])] + [e.get("vendor", ""), e.get("product", "")])})
    for g in guides:
        idx.append({"k": "Guide", "c": {"technical": "Technical guide"}.get(getattr(g, "TIER", ""), "Pillar guide"), "t": g.TITLE, "u": f"guides/{g.SLUG}.html", "s": g.DESC,
                    "x": " ".join(st["t"] for ph in g.PHASES for st in ph["steps"])})
        for i, ph in enumerate(g.PHASES, 1):
            idx.append({"k": "Guide", "c": f"Phase {i}", "t": f'{g.SHORT}: {ph["title"]}', "u": f'guides/{g.SLUG}.html#phase-{i}-{ph["id"]}',
                        "s": ph["goal"], "x": " ".join(st["t"] + " " + " ".join(st["do"]) for st in ph["steps"])})
    for t, u, s in (("About Tenant Recipes", "about.html", "Who runs the site, independence, corrections and contact."),
                    ("Contact and corrections", "contact/index.html", "Report an error, suggest a topic, report a security problem or contact the editor."),
                    ("Methodology: how we fact-check", "methodology.html", "Source hierarchy and verification process."),
                    ("About the editor", "author/index.html", "Who writes and reviews Tenant Recipes, focus areas and editorial principles."),
                    ("Changelog", "changelog.html", "Every new page, update and correction."),
                    ("Newsletter", "newsletter.html", "The free Tenant Recipes Weekly Brief.")):
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


# ---------------------------------------------------------------- v5 design system components (2026-10-30)
EDITOR = ("Edited by an IT professional working in IT since 1999, focused on Microsoft technology since 2013, based in Sweden.")

_P = {  # inline SVG icon paths (24x24, stroke icons)
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8.3-8 9-4.6-.7-8-4.5-8-9V6l8-3z"/><path d="M8.5 12.2l2.4 2.4 4.6-4.8"/>',
    "check": '<path d="M5 12.5l4.2 4.2L19 7"/>',
    "alert": '<path d="M12 3.5L2.8 19.5h18.4L12 3.5z"/><path d="M12 10v4.2M12 17.2v.1"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.6v.1"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/>',
    "book": '<path d="M4 5.5A2.5 2.5 0 016.5 3H20v15H6.5A2.5 2.5 0 004 20.5v-15z"/><path d="M4 20.5A2.5 2.5 0 016.5 23H20v-5"/>',
    "link": '<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><circle cx="4.5" cy="6" r="1"/><circle cx="4.5" cy="12" r="1"/><circle cx="4.5" cy="18" r="1"/>',
    "bug": '<path d="M12 3a9 9 0 100 18 9 9 0 000-18z"/><path d="M12 8v5M12 16v.1"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.2-4.2 4.4-6 8-6s6.8 1.8 8 6"/>',
}


def icon(name, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{_P[name]}</svg>'


def page_hero(rel, crumb_html, kicker, title_html, lead_html="", chips="", kind=""):
    """Dark page intro used on every non-home page (matches the homepage hero)."""
    return (f'<section class="ph{(" ph-" + kind) if kind else ""}"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i></div>'
            f'<div class="wrap ph-in">{crumb_html}'
            + (f'<p class="ph-k">{kicker}</p>' if kicker else "")
            + f'<h1>{title_html}</h1>'
            + (f'<p class="ph-lead">{lead_html}</p>' if lead_html else "")
            + (f'<ul class="ph-chips">{chips}</ul>' if chips else "")
            + '</div></section>')


def chip(ic, text):
    return f'<li>{icon(ic)}<span>{text}</span></li>'


def verify_card(rel, item, noun="Microsoft sources"):
    """Prominent verification summary under the title. Only shows values present in the data."""
    srcs = item.get("sources", [])
    last = item.get("last_verified")
    due = stale(last)
    badge = ('<span class="vc-b vc-due">' + icon("clock") + 'Re-check due</span>') if due else \
            ('<span class="vc-b vc-ok">' + icon("check") + 'Verified</span>')
    prim = ""
    if srcs:
        s = srcs[0]
        when = f' · checked on <time datetime="{s["checked"]}">{fmt(s["checked"])}</time>' if s.get("checked") else " · check date not recorded"
        prim = (f'<div class="vc-p"><span class="vc-l">Primary source</span><a href="{E(s["url"])}">{esc(s["title"])}</a>'
                f'<span class="vc-w">{when.lstrip(" ·")}</span></div>')
    stats = (f'<dl class="vc-s"><div><dt>Last verified</dt><dd>{fmt(last) if last else "Not yet"}</dd></div>'
             f'<div><dt>Sources checked</dt><dd><a href="#verified">{len(srcs)} {noun}</a></dd></div>'
             + (f'<div><dt>Last updated</dt><dd>{fmt(item["updated"])}</dd></div>' if item.get("updated") else "")
             + '</dl>')
    warn = (f'<p class="vc-warn">{icon("alert")}This page was last checked more than {C.REVERIFY_DAYS} days ago. '
            'Check the linked sources before you make production changes.</p>') if due else ""
    return (f'<section class="vc{" is-due" if due else ""}" aria-labelledby="vc-h"><div class="vc-h"><span class="vc-i">{icon("shield")}</span>'
            f'<h2 id="vc-h">Verification</h2>{badge}<a class="vc-m" href="{rel}methodology.html">How we verify {icon("arrow")}</a></div>'
            f'{prim}{stats}{warn}</section>')


def guide_verify_card(rel, g):
    """Guide version: every source was checked on g.VERIFIED (see the guide module). Primary = most-cited source."""
    from collections import Counter
    cnt = Counter((t, u) for p in g.PHASES for s in p["steps"] for t, u in s["src"])
    (t, u), n = cnt.most_common(1)[0]
    due = stale(g.VERIFIED)
    badge = ('<span class="vc-b vc-due">' + icon("clock") + 'Re-check due</span>') if due else ('<span class="vc-b vc-ok">' + icon("check") + 'Verified</span>')
    return (f'<section class="vc" aria-labelledby="vc-h"><div class="vc-h"><span class="vc-i">{icon("shield")}</span>'
            f'<h2 id="vc-h">Verification</h2>{badge}<a class="vc-m" href="{rel}methodology.html">How we verify {icon("arrow")}</a></div>'
            f'<div class="vc-p"><span class="vc-l">Most-cited source ({n} steps)</span><a href="{E(u)}">{esc(t)}</a>'
            f'<span class="vc-w">checked on <time datetime="{g.VERIFIED}">{fmt(g.VERIFIED)}</time></span></div>'
            f'<dl class="vc-s"><div><dt>Last verified</dt><dd>{fmt(g.VERIFIED)}</dd></div>'
            f'<div><dt>Sources checked</dt><dd><a href="#verified">{len(cnt)} {getattr(g, "SRC_LABEL", "Microsoft sources")}</a></dd></div>'
            f'<div><dt>Per step</dt><dd>Open “{getattr(g, "SRC_LABEL", "Microsoft sources")}” under each step</dd></div></dl></section>')


def card_meta(item, nsteps=True):
    bits = []
    if item.get("last_verified"):
        bits.append(f'<span class="cm-ok">{icon("check")}Verified {fmt(item["last_verified"])}</span>')
    if nsteps and item.get("steps"):
        bits.append(f'<span>{len(item["steps"])} steps</span>')
    if item.get("sources"):
        bits.append(f'<span>{len(item["sources"])} source{"s" if len(item["sources"]) != 1 else ""}</span>')
    return f'<span class="cm">{"".join(bits)}</span>'


def side_nav(rel, links, related, related_h, extra=""):
    toc = "".join(f'<li><a href="#{a}">{esc(t)}</a></li>' for a, t in links)
    rel_html = "".join(f'<li><a href="{u}">{esc(t)}</a></li>' for t, u in related)
    return (f'<aside class="pg-side" aria-label="On this page"><div class="ps-box"><p class="ps-h">{icon("list")}On this page</p><ol class="ps-toc">{toc}</ol></div>'
            + (f'<div class="ps-box"><p class="ps-h">{icon("layers")}{esc(related_h)}</p><ul class="ps-rel">{rel_html}</ul></div>' if rel_html else "")
            + extra + '</aside>')


def crumbs_dark(rel, path, items):
    return crumbs(rel, path, items).replace('class="crumb"', 'class="crumb ph-crumb"', 1)
