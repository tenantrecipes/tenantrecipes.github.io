"""Cybersecurity section (/security/): vulnerability watch + hardening recipes beyond Microsoft 365.

Data: one JSON file per entry in data/cyber/<id>.json (schema in RECIPES.md, "Cybersecurity entries").
Called from build_site.build(); returns the list of page paths it wrote. Exits non-zero on invalid data,
so an automated pipeline stops before deploying. Never invent CVE ids, versions, CVSS or dates: leave
cvss null when no vendor/NVD score was verified."""
import json, re, sys, pathlib, datetime
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "data" / "cyber"

AREAS = [  # (key, title, blurb)
    ("network", "Network & edge", "Firewalls, VPN gateways, routers and the management interfaces attackers scan for first."),
    ("endpoint", "Endpoints & clients", "Windows clients, browsers and local admin rights: the first foothold."),
    ("server", "Windows & Linux servers", "Domain controllers, file servers, SharePoint and Linux hosts."),
    ("services", "Services & apps", "Web stacks, mail gateways and apps you expose to users or the internet."),
    ("virtualization", "VMware & virtualization", "vCenter, ESX and hypervisor hardening: one host, many servers."),
    ("cloud", "Cloud & identity", "Entra ID, Conditional Access and Microsoft 365: our tenant recipes."),
]
AREA = {k: (t, b) for k, t, b in AREAS}
CLOUD_CATS = ["Identity & threat protection", "Conditional Access for AI"]  # existing recipe categories shown under Cloud & identity
TYPES = {"vulnerability", "hardening"}
SEVERITIES = {"Critical", "High", "Important", "Medium", "Moderate", "Low"}
STATUSES = {"published", "draft", "needs-review", "retired"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CVE = re.compile(r"^CVE-\d{4}-\d{4,}$")
REQ = ["id", "status", "type", "area", "title", "summary", "steps", "pitfalls", "sources", "last_verified"]
REQ_VULN = ["vendor", "product", "cves", "severity", "exploited", "advisory_date", "affected", "fixed"]


def _validate(e, fname):
    errs = [f"missing field '{k}'" for k in REQ if k not in e]
    if e.get("type") == "vulnerability":
        errs += [f"missing field '{k}'" for k in REQ_VULN if k not in e]
    if errs:
        return errs
    if e["id"] + ".json" != fname:
        errs.append("id must match file name")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", e["id"]):
        errs.append("id must be lowercase-kebab-case")
    if e["status"] not in STATUSES:
        errs.append("bad status")
    if e["type"] not in TYPES:
        errs.append(f"type must be one of {sorted(TYPES)}")
    if e["area"] not in AREA:
        errs.append(f"area must be one of {list(AREA)}")
    if not e["steps"] or not all(isinstance(s, str) and s.strip() for s in e["steps"]):
        errs.append("steps must be non-empty strings")
    if not e["sources"]:
        errs.append("at least one source is required")
    for s in e["sources"]:
        if not s.get("title") or not str(s.get("url", "")).startswith("https://"):
            errs.append(f"source needs title and https url: {s}")
    for k in ("last_verified", "advisory_date", "kev_added"):
        if e.get(k) is not None and not DATE.match(str(e[k])):
            errs.append(f"'{k}' must be YYYY-MM-DD or null")
    if e["type"] == "vulnerability":
        if e["severity"] not in SEVERITIES:
            errs.append(f"severity must be one of {sorted(SEVERITIES)}")
        if not e["cves"]:
            errs.append("vulnerability needs at least one CVE")
        for c in e["cves"]:
            if not CVE.match(str(c.get("id", ""))):
                errs.append(f"bad CVE id: {c.get('id')}")
            if c.get("cvss") is not None and not (0 <= float(c["cvss"]) <= 10 and c.get("cvss_source")):
                errs.append(f"{c['id']}: cvss must be 0-10 and have cvss_source")
    return errs


def load():
    out, problems = [], []
    for f in sorted(SRC.glob("*.json")):
        try:
            e = json.loads(f.read_text())
        except json.JSONDecodeError as ex:
            problems.append(f"{f.name}: invalid JSON ({ex})"); continue
        problems += [f"{f.name}: {p}" for p in _validate(e, f.name)]
        out.append(e)
    if problems:
        print("Cyber entry validation failed:\n  " + "\n  ".join(problems), file=sys.stderr)
        sys.exit(1)
    return [e for e in out if e["status"] == "published"]


def _date_key(e):
    return e.get("kev_added") or e.get("advisory_date") or e.get("updated") or ""


def build(page, R, esc, step_html, signup, fmt_date, E, SITE_NAME):
    """page(path, title, desc, body_fn, og_type) writes a page; returns list of written paths."""
    ents = load()
    vulns = sorted([e for e in ents if e["type"] == "vulnerability"], key=_date_key, reverse=True)
    hards = sorted([e for e in ents if e["type"] == "hardening"], key=lambda e: e.get("order", 0))
    cloud_recipes = [r for r in R if r["category"] in CLOUD_CATS]
    last = max(e["last_verified"] for e in ents if e.get("last_verified"))
    nsrc = len({s["url"] for e in ents for s in e["sources"]})
    pages = []

    def sev(s):
        return f'<span class="cy-sev cy-{(s or "info").lower()}">{esc(s or "Info")}</span>'

    def kev(e):
        return (f'<span class="cy-kev" title="Listed in the CISA Known Exploited Vulnerabilities catalog">Exploited · CISA KEV {fmt_date(e["kev_added"])}</span>'
                if e.get("kev_added") else ('<span class="cy-kev">Exploited</span>' if e.get("exploited") else ""))

    def cve_list(e):
        return ", ".join(c["id"] for c in e["cves"])

    def disclaimer():
        return (f'<aside class="cy-disc" role="note">{T.icon("info")}<span><strong>Informational only.</strong> Summaries of public vendor and CISA advisories, '
                f'fact-checked on the date shown. Affected and fixed versions change — always confirm against the linked vendor advisory '
                'before you act, and test changes before production. Not affiliated with any vendor.</span></aside>')

    def vuln_rows(rel, items):
        rows = ""
        for e in items:
            rows += (f'<tr><td><a href="{rel}security/{e["id"]}.html"><strong>{esc(e["title"])}</strong></a>'
                     f'<span class="cy-meta">{esc(e["vendor"])} · {esc(cve_list(e))}</span></td>'
                     f'<td>{sev(e["severity"])}</td><td>{kev(e)}</td>'
                     f'<td><a class="cy-area" href="{rel}security/{e["area"]}.html">{esc(AREA[e["area"]][0])}</a></td>'
                     f'<td class="cy-d">{fmt_date(_date_key(e))}</td></tr>')
        return ('<div class="cy-tw"><table class="cy-t"><thead><tr><th>Vulnerability</th><th>Vendor severity</th><th>Exploitation</th>'
                f'<th>Area</th><th>Date</th></tr></thead><tbody>{rows}</tbody></table></div>')

    def hard_cards(rel, items):
        return "".join(f'<a class="card" href="{rel}security/{e["id"]}.html"><div class="tag">Hardening · {esc(AREA[e["area"]][0])}</div>'
                       f'<h3>{esc(e["title"])}</h3><p class="clamp">{esc(e["summary"])}</p>{T.card_meta(e)}</a>' for e in items)

    def recipe_cards(rel, items):
        return "".join(f'<a class="card" href="{rel}recipes/{r["id"]}.html"><div class="tag">{esc(r["category"])}</div>'
                       f'<h3>{esc(r["title"])}</h3><p class="clamp">{esc(r["problem"])}</p>{T.card_meta(r)}</a>' for r in items)

    def hero(rel, crumb, badge, title, lead, stats, cta=""):
        st = "".join(f'<div><dt>{esc(k)}</dt><dd>{v}</dd></div>' for k, v in stats)
        return (f'<section class="gd-hero cy-hero"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i><i class="o3"></i></div><div class="wrap">'
                f'<p class="gd-crumb">{crumb}</p><p class="hx-badge"><span class="dot" aria-hidden="true"></span>{badge}</p>'
                f'<h1>{title}</h1><p class="hx-lead">{lead}</p>{cta}<dl class="hx-stats">{st}</dl></div></section>')

    # ---------- landing ----------
    def landing(rel):
        tiles = ""
        for k, t, b in AREAS:
            n = len(cloud_recipes) if k == "cloud" else sum(1 for e in ents if e["area"] == k)
            nv = sum(1 for e in vulns if e["area"] == k)
            lab = "recipes" if k == "cloud" else ("entries" if n != 1 else "entry")
            tiles += (f'<a class="sec-tile" href="{rel}security/{k}.html"><span class="sec-n">{n}</span><span class="sec-l">{lab}</span>'
                      f'<strong>{esc(t)}</strong><p>{esc(b)}</p><span class="sec-go">'
                      + (f'{nv} in vulnerability watch · ' if nv else "") + 'Open →</span></a>')
        exploited = sum(1 for e in vulns if e.get("exploited"))
        return (hero(rel, f'<a href="{rel}index.html">Home</a> / Security', f'Fact-checked against vendor advisories and CISA · last verified {fmt_date(last)}',
                     'Cybersecurity beyond the tenant.<br><span class="grad">Patch what is exploited. Harden what is exposed.</span>',
                     'A vulnerability watch for the CVEs that are actually being exploited, plus hardening recipes for network, endpoints, servers, '
                     'services and VMware. Every entry links to the vendor advisory, CISA or NIST NVD.',
                     [("Vulnerabilities tracked", len(vulns)), ("Known exploited", exploited), ("Hardening recipes", len(hards)), ("Official sources", nsrc)],
                     f'<div class="hx-cta"><a class="btn hx-p" href="#watch">Vulnerability watch →</a><a class="btn hx-g" href="#hardening">Hardening recipes</a></div>')
                + f'<main class="wrap">{disclaimer()}'
                f'<section class="sec" aria-labelledby="areas-h"><p class="sec-k">Areas</p><h2 id="areas-h">Pick your layer</h2><div class="sec-grid cy-areas">{tiles}</div></section>'
                f'<section class="sec" id="watch" aria-labelledby="watch-h"><p class="sec-k">Vulnerability watch</p><h2 id="watch-h">What to patch first — newest first</h2>'
                '<p class="fine">Severity is the vendor\'s own rating. "Exploited" means the vendor or CISA reports exploitation in the wild. '
                'Dates are the CISA KEV addition date, or the advisory date when not in KEV.</p>'
                f'{vuln_rows(rel, vulns)}</section>'
                f'<section class="sec" id="hardening" aria-labelledby="hard-h"><p class="sec-k">Hardening</p><h2 id="hard-h">Close the doors attackers use most</h2>'
                f'<div class="grid">{hard_cards(rel, hards)}</div></section>'
                f'{signup(rel, "security-index")}</main>')
    pages.append(page("security/index.html", f"Cybersecurity: vulnerability watch & hardening | {SITE_NAME}",
                      "Exploited CVEs and hardening recipes for network, endpoints, servers, services and VMware — fact-checked against vendor advisories and CISA.",
                      landing))

    # ---------- area pages ----------
    for k, t, b in AREAS:
        def area_body(rel, k=k, t=t, b=b):
            av = [e for e in vulns if e["area"] == k]
            ah = [e for e in hards if e["area"] == k]
            body = ""
            if av:
                body += f'<section class="sec"><p class="sec-k">Vulnerability watch</p><h2>Exploited and critical in {esc(t)}</h2>{vuln_rows(rel, av)}</section>'
            if ah:
                body += f'<section class="sec"><p class="sec-k">Hardening</p><h2>Hardening recipes</h2><div class="grid">{hard_cards(rel, ah)}</div></section>'
            if k == "cloud":
                body += (f'<section class="sec"><p class="sec-k">Tenant recipes</p><h2>Identity and Conditional Access recipes for Microsoft 365</h2>'
                         f'<div class="grid">{recipe_cards(rel, cloud_recipes)}</div></section>')
            if not body:
                body = '<p>No entries yet — new ones are added as vendors publish advisories.</p>'
            n = len(cloud_recipes) if k == "cloud" else len(av) + len(ah)
            return (hero(rel, f'<a href="{rel}index.html">Home</a> / <a href="{rel}security/index.html">Security</a> / {esc(t)}',
                         f'Security area · last verified {fmt_date(last)}', esc(t), esc(b),
                         [("Entries" if k != "cloud" else "Recipes", n), ("Exploited", sum(1 for e in av if e.get("exploited")))])
                    + f'<main class="wrap">{disclaimer()}{body}{signup(rel, "security-" + k)}</main>')
        pages.append(page(f"security/{k}.html", f"{t} security | {SITE_NAME}", b, area_body))

    # ---------- entry pages ----------
    for e in ents:
        def body(rel, e=e):
            at, _ = AREA[e["area"]]
            src = "".join(f'<li><a href="{E(s["url"])}">{esc(s["title"])}</a>'
                          + (f' <span class="fine">(checked {s["checked"]})</span>' if s.get("checked") else "") + '</li>' for s in e["sources"])
            facts = ""
            if e["type"] == "vulnerability":
                crow = ""
                for c in e["cves"]:
                    score = (f'{c["cvss"]} <span class="fine">(CVSS {esc(str(c.get("cvss_version") or ""))}, {esc(c["cvss_source"])})</span>'
                             if c.get("cvss") is not None else '<span class="fine">not scored in sources checked</span>')
                    crow += (f'<tr><td><a href="https://nvd.nist.gov/vuln/detail/{c["id"]}">{c["id"]}</a></td><td>{sev(c.get("severity")) if c.get("severity") else ""}</td>'
                             f'<td>{score}</td><td>{esc(c.get("note", ""))}</td></tr>')
                facts = (f'<dl class="cy-facts"><div><dt>Vendor</dt><dd>{esc(e["vendor"])}</dd></div><div><dt>Product</dt><dd>{esc(e["product"])}</dd></div>'
                         f'<div><dt>Vendor severity</dt><dd>{sev(e["severity"])}</dd></div><div><dt>Exploitation</dt><dd>{kev(e) or "No exploitation reported in sources checked"}</dd></div>'
                         f'<div><dt>Advisory</dt><dd>{esc(e.get("advisory_id", ""))} · {fmt_date(e["advisory_date"])}</dd></div>'
                         + (f'<div><dt>Impact</dt><dd>{esc(e["impact"])}</dd></div>' if e.get("impact") else "") + '</dl>'
                         f'<h2>CVEs</h2><div class="cy-tw"><table class="cy-t"><thead><tr><th>CVE</th><th>Severity</th><th>CVSS base</th><th>Notes</th></tr></thead><tbody>{crow}</tbody></table></div>'
                         '<h2>Affected</h2><ul>' + "".join(f'<li>{step_html(x)}</li>' for x in e["affected"]) + '</ul>'
                         '<h2>Fixed versions</h2><ul class="cy-fix">' + "".join(f'<li>{step_html(x)}</li>' for x in e["fixed"]) + '</ul>')
            kind = "Vulnerability watch" if e["type"] == "vulnerability" else "Hardening recipe"
            path = f'security/{e["id"]}.html'
            isv = e["type"] == "vulnerability"
            chips = ((T.chip("alert", f'Vendor severity: {esc(e["severity"])}') + (T.chip("target", "Exploited in the wild") if e.get("exploited") else "")
                      + T.chip("list", esc(cve_list(e)))) if isv else T.chip("list", f'{len(e["steps"])} steps')) \
                + T.chip("link", f'{len(e["sources"])} official source{"s" if len(e["sources"]) != 1 else ""}')
            toc = [("what", "What it is" if isv else "Why it matters")] + ([("cves", "CVEs"), ("affected", "Affected & fixed")] if isv else []) \
                + [("todo", "What to do" if isv else "Steps")] + ([("pitfalls", "Pitfalls")] if e["pitfalls"] else []) + [("verified", "Sources & corrections")]
            rel_items = [(x["title"], f'{rel}security/{x["id"]}.html') for x in ents if x["area"] == e["area"] and x["id"] != e["id"]][:5]
            facts = facts.replace('<h2>CVEs</h2>', '<h2 id="cves">CVEs</h2>').replace('<h2>Affected</h2>', '<h2 id="affected">Affected</h2>')
            facts = facts.replace('<h2>Fixed versions</h2><ul class="cy-fix">', f'<section class="co co-ok"><p class="co-h">{T.icon("check")}Fixed versions</p><ul class="cy-fix">').replace('</ul>', '</ul></section>', 0)
            if isv:
                facts = facts[::-1].replace('>lu/<', '>noitces/<>lu/<', 1)[::-1]
            return (T.page_hero(rel, T.crumbs_dark(rel, path, [("Home", rel + "index.html"), ("Security", rel + "security/index.html"), (at, rel + f'security/{e["area"]}.html'), (kind, None)]),
                                f'{T.icon("shield")}{kind} · {esc(at)}', esc(e["title"]), "", chips, kind="cyber")
                    + '<main class="wrap pg"><div class="pg-grid"><article class="doc">'
                    + T.verify_card(rel, e, "official sources") + disclaimer()
                    + f'<h2 id="what">{"What it is" if isv else "Why it matters"}</h2><p>{esc(e["summary"])}</p>{facts}'
                    f'<h2 id="todo" class="h-ic">{T.icon("list")}{"What to do" if isv else "Steps"}</h2><ol class="steps">' + "".join(f'<li><div>{step_html(s)}</div></li>' for s in e["steps"]) + '</ol>'
                    + (f'<section id="pitfalls" class="co co-warn"><p class="co-h">{T.icon("alert")}Pitfalls</p><ul>' + "".join(f'<li>{step_html(p)}</li>' for p in e["pitfalls"]) + '</ul></section>' if e["pitfalls"] else "")
                    + T.trust_bottom(rel, path, e["title"], e, "Verified against (vendor &amp; official sources)") + '</article>'
                    + T.side_nav(rel, toc, rel_items, f'More in {at}')
                    + '</div>' + signup(rel, "security-" + e["id"]) + '</main>')
        pages.append(page(f'security/{e["id"]}.html', f'{e["title"]} | {SITE_NAME}', e["summary"], body, "article"))
    print(f"Security section: {len(vulns)} vulnerabilities, {len(hards)} hardening recipes, {len(pages)} pages")
    return pages
