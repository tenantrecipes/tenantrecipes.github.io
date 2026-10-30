"""Security Tools & Testing section (/tools/).

Data: one JSON file per tool or method in data/tools/<id>.json. Facts (license, cost, commands) must be
checked on the tool's official site or repository on the date in `sources[].checked`; unknown values stay
null. Text is written in our own words. Exits non-zero on invalid data so the pipeline stops before deploy."""
import json, re, sys, pathlib
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "data" / "tools"
CATEGORIES = ["Domain & email", "External exposure", "M365 & Entra", "Active Directory", "Vulnerability scanning",
              "Web apps", "Client hardening", "Leaks & threat intel", "Methods"]
COSTS = {"free", "open source", "freemium"}
KINDS = {"tool", "method"}
REQ = ["id", "status", "kind", "name", "category", "what", "when", "cost", "url", "example", "pitfalls", "sources", "last_verified"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NOTICE = "Only test systems you own or have written permission to test."


def cat_slug(c):
    return re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")


def _validate(e, fname):
    err = [f"missing {k}" for k in REQ if e.get(k) in (None, "", [])]
    if e.get("id") and fname != e["id"] + ".json":
        err.append("file name must equal id")
    if e.get("category") not in CATEGORIES:
        err.append(f"category must be one of {CATEGORIES}")
    if e.get("cost") not in COSTS:
        err.append(f"cost must be one of {sorted(COSTS)}")
    if e.get("kind") not in KINDS:
        err.append("kind must be tool or method")
    if not str(e.get("url", "")).startswith("https://"):
        err.append("url must be https")
    for s in e.get("sources", []):
        if not s.get("url", "").startswith("https://") or not DATE.match(s.get("checked") or ""):
            err.append(f"source needs https url and checked date: {s}")
    if e.get("last_verified") and not DATE.match(e["last_verified"]):
        err.append("last_verified must be YYYY-MM-DD")
    return err


def load():
    out, bad = [], []
    for f in sorted(SRC.glob("*.json")):
        e = json.loads(f.read_text())
        errs = _validate(e, f.name)
        if errs:
            bad.append(f"{f.name}: " + "; ".join(errs))
        elif e["status"] == "published":
            out.append(e)
    if bad:
        print("Invalid tool data:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(1)
    return sorted(out, key=lambda e: (CATEGORIES.index(e["category"]), e.get("order", 0)))


def notice():
    return (f'<aside class="tl-perm" role="note">{T.icon("alert")}<span><strong>{NOTICE}</strong> '
            'Scanning or attacking systems without permission can be illegal and can disrupt services. '
            'Get approval in writing, agree the scope, and tell the people who monitor those systems.</span></aside>')


def _host(u):
    return re.sub(r"^https://(www\\.)?", "", u).rstrip("/")


def cost_badge(e):
    return f'<span class="tl-cost tl-c-{cat_slug(e["cost"])}">{T.esc(e["cost"].capitalize())}</span>'


def build(page, esc, step_html, signup, fmt_date, E, SITE_NAME):
    ents = load()
    tools = [e for e in ents if e["kind"] == "tool"]
    methods = [e for e in ents if e["kind"] == "method"]
    last = max(e["last_verified"] for e in ents)
    pages = []

    def card(rel, e):
        return (f'<a class="card tl-card" data-cat="{cat_slug(e["category"])}" href="{rel}tools/{e["id"]}.html">'
                f'<div class="tag">{esc(e["category"])}</div><h3>{esc(e["name"])}</h3><p class="clamp">{esc(e["what"])}</p>'
                f'<p class="tl-meta">{cost_badge(e)}' + (f'<span>{esc(e["license"])}</span>' if e.get("license") else "")
                + '</p></a>')

    def landing(rel):
        cnt = {c: sum(1 for e in ents if e["category"] == c) for c in CATEGORIES}
        fchips = (f'<button type="button" class="chip on" data-f="" aria-pressed="true">All <span>{len(ents)}</span></button>'
                  + "".join(f'<button type="button" class="chip" data-f="{cat_slug(c)}" aria-pressed="false">{esc(c)} <span>{n}</span></button>'
                            for c, n in cnt.items() if n))
        filt = (f'<div class="chips cy-filter" id="tl-filter" role="group" aria-label="Filter by category" hidden>{fchips}</div>'
                '<p class="fine" id="tl-fn" aria-live="polite"></p>'
                '<script>(function(){var w=document.getElementById("tl-filter");if(!w)return;w.hidden=false;var n=document.getElementById("tl-fn");'
                'w.addEventListener("click",function(ev){var b=ev.target.closest("button[data-f]");if(!b)return;var f=b.getAttribute("data-f");'
                'w.querySelectorAll("button").forEach(function(x){var on=x===b;x.classList.toggle("on",on);x.setAttribute("aria-pressed",on?"true":"false")});'
                'var k=0;document.querySelectorAll("#tools [data-cat]").forEach(function(r){var s=!f||r.getAttribute("data-cat")===f;r.hidden=!s;if(s)k++});'
                'n.textContent=f?k+" item"+(k===1?"":"s")+" in "+b.firstChild.textContent.trim():"";})})();</script>')
        st = "".join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in
                     [("Tools", len(tools)), ("Methods", len(methods)), ("Free or open source", sum(1 for e in tools if e["cost"] != "freemium")),
                      ("Official sources", len({s["url"] for e in ents for s in e["sources"]}))])
        return (f'<section class="gd-hero cy-hero"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i><i class="o3"></i></div><div class="wrap">'
                f'<p class="gd-crumb"><a href="{rel}index.html">Home</a> / Tools</p>'
                f'<p class="hx-badge"><span class="dot" aria-hidden="true"></span>Checked on each tool\'s official site · last verified {fmt_date(last)}</p>'
                '<h1>Security tools &amp; testing.<br><span class="grad">See your exposure before attackers do.</span></h1>'
                '<p class="hx-lead">Free and open-source tools to check your domains, internet exposure, Microsoft 365 tenant, Active Directory, '
                'web apps and Windows clients, each with a short example and the pitfalls. Plus a method for scoping an internal pentest.</p>'
                f'<dl class="hx-stats">{st}</dl></div></section>'
                f'<main class="wrap">{notice()}'
                f'<section class="sec" id="tools" aria-labelledby="tl-h"><p class="sec-k">Toolbox</p><h2 id="tl-h">Pick a tool by what you want to check</h2>{filt}'
                f'<div class="grid">{"".join(card(rel, e) for e in ents)}</div></section>'
                + T.ad_slot("tools-between-sections") +
                '<p class="fine">Independent and not affiliated with any of the vendors listed. Licenses and prices change; '
                'confirm on the official page before you rely on them.</p>'
                f'{signup(rel, "tools-index")}</main>')
    pages.append(page("tools/index.html", f"Security tools & testing: free scanners and checks | {SITE_NAME}",
                      "Free and open-source security tools for domains, external exposure, Microsoft 365, Active Directory, web apps and Windows, with examples and pitfalls.",
                      landing))

    for e in ents:
        def body(rel, e=e):
            path = f'tools/{e["id"]}.html'
            ism = e["kind"] == "method"
            facts = (f'<dl class="cy-facts"><div><dt>Category</dt><dd>{esc(e["category"])}</dd></div>'
                     + (f'<div><dt>Maker</dt><dd>{esc(e["vendor"])}</dd></div>' if e.get("vendor") else "")
                     + f'<div><dt>Cost</dt><dd>{cost_badge(e)}</dd></div>'
                     + (f'<div><dt>License</dt><dd>{esc(e["license"])}</dd></div>' if e.get("license") else "")
                     + f'<div><dt>Official site</dt><dd><a href="{E(e["url"])}" rel="noopener">{esc(_host(e["url"]))}</a></dd></div>'
                     + (f'<div><dt>Source code</dt><dd><a href="{E(e["repo"])}" rel="noopener">GitHub</a></dd></div>' if e.get("repo") else "")
                     + '</dl>' + (f'<p class="fine">{esc(e["cost_note"])}</p>' if e.get("cost_note") else ""))
            kind = "Method" if ism else "Tool"
            chips = T.chip("layers", esc(e["category"])) + T.chip("list", f'{len(e["example"])} steps') \
                + T.chip("link", f'{len(e["sources"])} official source{"s" if len(e["sources"]) != 1 else ""}')
            toc = [("what", "What it does" if not ism else "What it is"), ("when", "When to use it"), ("example", "Step by step"),
                   ("pitfalls", "Pitfalls"), ("verified", "Sources & corrections")]
            rel_items = [(x["name"], f'{rel}tools/{x["id"]}.html') for x in ents if x["category"] == e["category"] and x["id"] != e["id"]][:5] \
                or [(x["name"], f'{rel}tools/{x["id"]}.html') for x in ents if x["id"] != e["id"]][:5]
            return (T.page_hero(rel, T.crumbs_dark(rel, path, [("Home", rel + "index.html"), ("Tools", rel + "tools/index.html"), (e["category"], None)]),
                                f'{T.icon("shield")}{kind} · {esc(e["category"])}', esc(e["name"]), "", chips, kind="cyber")
                    + '<main class="wrap pg"><div class="pg-grid"><article class="doc">'
                    + T.verify_card(rel, e, "official sources") + notice()
                    + f'<h2 id="what">{"What it is" if ism else "What it does"}</h2><p>{esc(e["what"])}</p>{facts}'
                    f'<h2 id="when">When to use it</h2><p>{esc(e["when"])}</p>'
                    f'<h2 id="example" class="h-ic">{T.icon("list")}Step by step</h2><ol class="steps">'
                    + "".join(f'<li><div>{step_html(s)}</div></li>' for s in e["example"]) + '</ol>'
                    + f'<section id="pitfalls" class="co co-warn"><p class="co-h">{T.icon("alert")}Pitfalls</p><ul>'
                    + "".join(f'<li>{step_html(p)}</li>' for p in e["pitfalls"]) + '</ul></section>'
                    + T.trust_bottom(rel, path, e["name"], e, "Verified against (official sources)") + '</article>'
                    + T.side_nav(rel, toc, rel_items, f'More in {e["category"]}')
                    + '</div>' + signup(rel, "tools-" + e["id"]) + '</main>')
        title = e["name"] if e["kind"] == "method" else f'{e["name"]}: what it does and how to use it'
        desc = e["what"] if len(e["what"]) <= 160 else e["what"][:157].rsplit(" ", 1)[0] + "…"
        pages.append(page(f'tools/{e["id"]}.html', f'{title} | {SITE_NAME}', desc, body, "article"))
    print(f"Tools section: {len(tools)} tools, {len(methods)} methods, {len(pages)} pages")
    return pages


def search_docs():
    out = [{"t": "Security tools & testing", "k": "Page", "c": "Site", "u": "tools/index.html",
            "s": "Free and open-source security tools and testing methods, with examples, pitfalls and a permission notice."}]
    for e in load():
        out.append({"t": e["name"], "k": "Tool", "c": e["category"], "g": [e["cost"]] + ([e["license"]] if e.get("license") else []),
                    "p": e.get("vendor"), "s": e["what"][:220], "x": (e["when"] + " " + " ".join(e["example"]))[:360],
                    "u": f'tools/{e["id"]}.html', "d": e.get("updated")})
    return out
