"""Unified site search: builds dist/search/index.json at build time (docs, autocomplete phrases, synonyms, question map)
and the standalone /search/ results page. All matching runs client-side in assets/search.js; nothing is sent anywhere."""
import json, re, sys, pathlib
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
SYN = ROOT / "data" / "search_synonyms.json"
VERBS = {"run", "assign", "plan", "decide", "make", "require", "roll", "block", "set", "keep", "deploy", "create", "protect", "manage",
         "control", "find", "hide", "use", "audit", "move", "check", "stop", "catch", "restrict", "track", "pull", "list", "inventory",
         "kill", "harden", "close", "patch", "lock", "turn", "enable", "disable", "configure"}


def _clip(s, n):
    s = " ".join(str(s).replace("`", "").split())
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0]


def _parts(product):
    out = []
    for p in re.split(r"[,;()]| and ", product or ""):
        p = p.strip(" .")
        if 3 <= len(p) <= 40:
            out.append(p)
    return out


def build_index(R, CY, guides, Q, AREA, tags_for, site_notes, extra=()):
    """extra: ready-made doc dicts from other sections (tools, policies)."""
    docs, sug = [], []

    def doc(**d):
        d = {k: v for k, v in d.items() if v not in (None, "", [])}
        docs.append(d)

    for r in R:
        tg = tags_for(r)
        doc(t=r["title"], k="News" if any(t.startswith("News") for t in tg) else "Recipe", c=r["category"], g=tg,
            s=_clip(r["problem"], 220), x=_clip(" ".join(r["steps"]), 420), u=f'recipes/{r["id"]}.html', d=r.get("updated") or r.get("created"))
        w = r["title"].split(" ", 1)
        if w[0].lower() in VERBS and len(w) > 1:
            sug.append("how do I " + w[0].lower() + " " + w[1])
    for e in CY:
        isv = e["type"] == "vulnerability"
        cves = [c["id"] for c in e.get("cves", [])]
        doc(t=e["title"], k="Vulnerability" if isv else "Hardening", c=e.get("category") or AREA[e["area"]][0],
            g=[AREA[e["area"]][0]] + ([e["severity"], "exploited"] if isv and e.get("exploited") else ([e["severity"]] if isv else [])),
            cve=cves, p=(f'{e.get("vendor", "")} {e.get("product", "")}'.strip() if isv else None),
            s=_clip(e["summary"], 220), x=_clip(e.get("action") or " ".join(e["steps"]), 300), u=f'security/{e["id"]}.html',
            d=e.get("kev_added") or e.get("advisory_date") or e.get("updated"))
        sug += cves
        if isv:
            sug.append(e["vendor"])
            sug += _parts(e["product"])
    for g in guides:
        doc(t=g.TITLE, k="Guide", c="Pillar guide", s=_clip(g.DESC, 220),
            x=_clip(" ".join(st["t"] for ph in g.PHASES for st in ph["steps"]), 500), u=f"guides/{g.SLUG}.html", d=g.VERIFIED)
        for i, ph in enumerate(g.PHASES, 1):
            doc(t=f'{g.SHORT}: {ph["title"]}', k="Guide", c=f"Phase {i}", s=_clip(ph["goal"], 200),
                x=_clip(" ".join(st["t"] for st in ph["steps"]), 300), u=f'guides/{g.SLUG}.html#phase-{i}-{ph["id"]}')
            sug.append(ph["title"])
            sug += [st["t"] for st in ph["steps"]]
    doc(t=Q.TITLE, k="Guide", c="Quick guide", s=_clip(Q.DESC, 220), x=_clip(" ".join(c["t"] for c in Q.CHECKS), 300),
        u=f"guides/{Q.SLUG}.html", d=Q.VERIFIED)
    sug += [c["t"] for c in Q.CHECKS]
    for n in site_notes[:20]:
        t = n["text"].split(":", 1)[0] if ":" in n["text"][:60] else _clip(n["text"], 60)
        doc(t=f"What's new: {t}", k="News", c="What's new", s=_clip(n["text"], 220), u=f'changelog/index.html#d-{n["date"]}', d=n["date"])
    for t, u, s in (("Vulnerability watch: what to patch first", "security/index.html", "Exploited CVEs, newest first, with a one-line action for each, plus hardening recipes."),
                    ("What's new (changelog)", "changelog/index.html", "Every new and updated page, newest first."),
                    ("About Tenant Recipes", "about.html", "Independence, editorial standards, corrections and contact."),
                    ("Methodology: how we fact-check", "methodology.html", "Source hierarchy and verification process."),
                    ("Newsletter", "newsletter.html", "The free weekly Tenant Recipes brief."),
                    ("Sample newsletter issue", "newsletter-sample.html", "What the weekly brief looks like.")):
        doc(t=t, k="Page", c="Site", s=s, u=u)
    for d in extra:
        doc(**d)
    syn = json.loads(SYN.read_text())
    urls = {d["u"].split("#")[0] for d in docs}
    bad = [u for _, u in syn["questions"] if u not in urls]
    if bad:
        print(f"search_synonyms.json: question targets not in the index: {bad}", file=sys.stderr)
        sys.exit(1)
    sug += [d["t"] for d in docs if d["k"] != "News" or d["c"] != "What's new"]
    sug += sorted({c for d in docs for c in d.get("g", []) + [d.get("c", "")] if c and not c.startswith("Phase")})
    sug += [q for q, _ in syn["questions"]]
    seen, phrases = set(), []
    for s in sug:
        s = " ".join(str(s).split()).rstrip(".")
        if 2 <= len(s) <= 110 and s.lower() not in seen:
            seen.add(s.lower())
            phrases.append(s)
    return {"v": 1, "docs": docs, "sug": phrases, "syn": [[w.lower() for w in g] for g in syn["groups"]],
            "q": [[q.lower(), u] for q, u in syn["questions"]]}


def search_body(rel):
    return (T.page_hero(rel, T.crumbs_dark(rel, "search/index.html", [("Home", rel + "index.html"), ("Search", None)]), "Search",
                        "Search everything", "Recipes, guides, vulnerabilities, hardening, security tools, policy templates and news in one place. Search runs in your browser; nothing is sent anywhere.",
                        kind="page")
            + '<main class="wrap pg"><article class="prose doc sxp">'
            f'<form class="fd-s sxp-f" action="{rel}search/index.html" method="get" role="search">{T.icon("search")}'
            '<label class="sr" for="sxp-q">Search Tenant Recipes</label>'
            '<input id="sxp-q" name="q" type="search" placeholder="e.g. MFA, Citrix, oversharing, CVE-2026" autocomplete="off" data-sx-page>'
            '<button class="btn p" type="submit">Search</button></form>'
            '<div id="sxp-chips" class="chips sxp-chips" role="group" aria-label="Filter by type"></div>'
            '<p id="sxp-n" class="fine" aria-live="polite"></p><div id="sxp-r"></div>'
            f'<noscript><p>Search needs JavaScript. Browse the <a href="{rel}index.html#library">recipe library</a>, the '
            f'<a href="{rel}guides/index.html">guides</a> or the <a href="{rel}security/index.html">security section</a>.</p></noscript>'
            '</article></main>')
