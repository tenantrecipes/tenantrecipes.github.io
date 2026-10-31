"""News section (/news/).

Two kinds of items:
1. Curated news in data/news/<id>.json (schema in RECIPES.md, "News items"): an announcement, retirement or
   change, summarized in our own words, with why it matters, what to do, an effective date if any, the primary
   source and related links (usually the recipe with the full how-to). Recipe URLs never move.
2. Exploited vulnerabilities from the security section (category "Security incidents"), generated from
   data/cyber, so there is one source of truth. They link to the existing /security/<id>.html pages.
Writes /news/index.html, /news/<id>.html for curated items and the Atom feed /news/feed.xml."""
import json, re, sys, pathlib
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "data" / "news"
CATEGORIES = ["M365", "Entra", "Intune", "Copilot/AI", "Purview", "Defender", "Windows", "Security incidents", "Regulation", "Retirements"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQ = ["id", "status", "title", "date", "category", "summary", "why", "todo", "primary", "sources", "last_verified"]


def cat_slug(c):
    return re.sub(r"[^a-z0-9]+", "-", c.lower()).strip("-")


def _validate(e, fname):
    err = [f"missing {k}" for k in REQ if e.get(k) in (None, "", [])]
    if e.get("id") and fname != e["id"] + ".json":
        err.append("file name must equal id")
    if e.get("category") not in CATEGORIES:
        err.append(f"category must be one of {CATEGORIES}")
    for k in ("date", "last_verified", "effective"):
        if e.get(k) and not DATE.match(e[k]):
            err.append(f"{k} must be YYYY-MM-DD")
    n = len(re.findall(r"[.!?](\s|$)", e.get("summary", "")))
    if not 2 <= n <= 4:
        err.append(f"summary must be 2-4 sentences (found {n})")
    if not str((e.get("primary") or {}).get("url", "")).startswith("https://"):
        err.append("primary.url must be https")
    return err


def load_curated():
    out, bad = [], []
    for f in sorted(SRC.glob("*.json")):
        e = json.loads(f.read_text())
        errs = _validate(e, f.name)
        if errs:
            bad.append(f"{f.name}: " + "; ".join(errs))
        elif e["status"] == "published":
            e["kind"] = "news"; e["u"] = f'news/{e["id"]}.html'
            out.append(e)
    if bad:
        print("Invalid news data:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(1)
    return out


def items(CY):
    out = load_curated()
    for v in CY:
        if v["type"] != "vulnerability" or not v.get("exploited"):
            continue
        d = v.get("kev_added") or v.get("advisory_date")
        if not d:
            continue
        out.append({"id": v["id"], "kind": "vuln", "title": v["title"], "date": d, "category": "Security incidents",
                    "summary": v["summary"], "why": None, "todo": [v["action"]] if v.get("action") else [],
                    "primary": v["sources"][0], "u": f'security/{v["id"]}.html', "effective": None,
                    "kev": bool(v.get("kev_added"))})
    return sorted(out, key=lambda e: (e["date"], e["kind"] == "news", e["title"]), reverse=True)


def card(rel, esc, fmt_date, e, short=False):
    eff = (f'<span class="nw-eff">Effective {fmt_date(e["effective"])}</span>' if e.get("effective")
           else (f'<span class="nw-eff">{esc(e["effective_note"])}</span>' if e.get("effective_note") else ""))
    lab = ("Added to CISA KEV " if e.get("kev") else "Published ") if e["kind"] == "vuln" else ""
    s = e["summary"] if not short else (e["summary"].split(". ")[0].rstrip(".") + ".")
    return (f'<li data-cat="{cat_slug(e["category"])}"><article class="nw-card"><p class="nw-m"><span class="nw-c nw-c-{cat_slug(e["category"])}">{esc(e["category"])}</span>'
            f'<time datetime="{e["date"]}">{lab}{fmt_date(e["date"])}</time>{eff}</p>'
            f'<h3><a href="{rel}{e["u"]}">{esc(e["title"])}</a></h3><p class="nw-s">{esc(s)}</p></article></li>')


def latest_strip(rel, esc, fmt_date, CY, n=4):
    """Homepage strip = Microsoft track only: curated news plus exploited Microsoft vulnerabilities."""
    ms = {v["id"] for v in CY if "Microsoft" in (v.get("vendor") or "")}
    its = [e for e in items(CY) if e["kind"] == "news" or e["id"] in ms][:n]
    return (f'<section class="wrap nw-strip" aria-labelledby="nw-sh"><div class="nw-sh-row"><h2 id="nw-sh">Latest Microsoft 365 news</h2>'
            f'<a href="{rel}news/index.html">All news &amp; retirements →</a></div>'
            f'<ol class="nw-list nw-mini">{"".join(card(rel, esc, fmt_date, e, True) for e in its)}</ol></section>')


def build(page, esc, step_html, signup, fmt_date, E, SITE_NAME, CY):
    import build_links as BL, build_data as BD
    RECIPES = BD.load()
    its = items(CY)
    pages = []

    def landing(rel):
        cnt = {c: sum(1 for e in its if e["category"] == c) for c in CATEGORIES}
        fchips = (f'<button type="button" class="chip on" data-f="" aria-pressed="true">All <span>{len(its)}</span></button>'
                  + "".join(f'<button type="button" class="chip" data-f="{cat_slug(c)}" aria-pressed="false">{esc(c)} <span>{n}</span></button>' for c, n in cnt.items() if n))
        filt = (f'<div class="chips cy-filter" id="nw-filter" role="group" aria-label="Filter by category" hidden>{fchips}</div><p class="fine" id="nw-fn" aria-live="polite"></p>'
                '<script>(function(){var w=document.getElementById("nw-filter");if(!w)return;w.hidden=false;var n=document.getElementById("nw-fn");'
                'w.addEventListener("click",function(ev){var b=ev.target.closest("button[data-f]");if(!b)return;var f=b.getAttribute("data-f");'
                'w.querySelectorAll("button").forEach(function(x){var on=x===b;x.classList.toggle("on",on);x.setAttribute("aria-pressed",on?"true":"false")});'
                'var k=0;document.querySelectorAll("#news [data-cat]").forEach(function(r){var s=!f||r.getAttribute("data-cat")===f;r.hidden=!s;if(s)k++});'
                'n.textContent=f?k+" item"+(k===1?"":"s")+" in "+b.firstChild.textContent.trim():""})})();</script>')
        return (f'<section class="gd-hero cy-hero"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i><i class="o3"></i></div><div class="wrap">'
                f'<p class="gd-crumb"><a href="{rel}index.html">Home</a> / News</p>'
                f'<p class="hx-badge"><span class="dot" aria-hidden="true"></span>Every item links to its primary source · newest first</p>'
                '<h1>News &amp; retirements.<br><span class="grad">What changes, when, and what to do.</span></h1>'
                '<p class="hx-lead">Microsoft 365, Entra, Defender and Copilot changes that need an admin\'s attention, plus vulnerabilities that are being exploited right now. '
                f'Subscribe with the <a href="{rel}news/feed.xml">news feed (Atom)</a>.</p></div></section>'
                f'<main class="wrap"><section class="sec" id="news" aria-labelledby="nw-h"><h2 id="nw-h" class="sr">All news</h2>{filt}'
                f'<ol class="nw-list">{"".join(card(rel, esc, fmt_date, e) for e in its)}</ol></section>'
                '<p class="fine">Summaries are written by us and fact-checked on the date shown. Rollout dates can move; always check the linked source. '
                'Independent and not affiliated with Microsoft.</p>' + signup(rel, "news-index") + '</main>')
    pages.append(page("news/index.html", f"Microsoft 365 news, retirements & exploited vulnerabilities | {SITE_NAME}",
                      "Microsoft 365, Entra, Defender and Copilot changes and retirements with dates, why they matter and what to do, plus exploited vulnerabilities.", landing))

    for e in [x for x in its if x["kind"] == "news"]:
        def body(rel, e=e):
            path = e["u"]
            eff = (f'<div><dt>Effective</dt><dd>{fmt_date(e["effective"])}' + (f' <span class="fine">({esc(e["effective_note"])})</span>' if e.get("effective_note") else "") + '</dd></div>') if e.get("effective") \
                else (f'<div><dt>Timing</dt><dd>{esc(e["effective_note"])}</dd></div>' if e.get("effective_note") else "")
            facts = (f'<dl class="cy-facts"><div><dt>Category</dt><dd>{esc(e["category"])}</dd></div><div><dt>Published</dt><dd>{fmt_date(e["date"])}</dd></div>{eff}'
                     f'<div><dt>Primary source</dt><dd><a href="{E(e["primary"]["url"])}" rel="noopener">{esc(e["primary"]["title"])}</a></dd></div></dl>')
            rel_links = "".join(f'<li><a href="{(rel + r["url"]) if not r["url"].startswith("http") else E(r["url"])}">{esc(r["title"])}</a></li>' for r in e.get("related", []))
            listed = {r["url"].rsplit("/", 1)[-1][:-5] for r in e.get("related", []) if r["url"].startswith("recipes/")} | ({e["recipe"]} if e.get("recipe") else set())
            rel_links += BL.related_list_html(rel, BL.recipe_matches(e, RECIPES, 3 if len(listed) < 2 else 2, skip=listed), esc)
            others = [(x["title"], rel + x["u"]) for x in its if x["id"] != e["id"]][:5]
            toc = [("what", "What's changing"), ("why", "Why it matters"), ("todo", "What to do"), ("related", "Related"), ("verified", "Sources")]
            return (T.page_hero(rel, T.crumbs_dark(rel, path, [("Home", rel + "index.html"), ("News", rel + "news/index.html"), (e["category"], None)]),
                                f'{T.icon("clock")}News · {esc(e["category"])}', esc(e["title"]), "",
                                T.chip("clock", f'Published {fmt_date(e["date"])}') + (T.chip("alert", f'Effective {fmt_date(e["effective"])}') if e.get("effective") else ""), kind="cyber")
                    + '<main class="wrap pg"><div class="pg-grid"><article class="doc">' + T.verify_card(rel, e, "official sources")
                    + f'<h2 id="what">What\'s changing</h2><p>{esc(e["summary"])}</p>{facts}'
                    + f'<h2 id="why">Why it matters</h2><p>{esc(e["why"])}</p>'
                    + f'<h2 id="todo" class="h-ic">{T.icon("list")}What to do</h2><ol class="steps">' + "".join(f'<li><div>{step_html(s)}</div></li>' for s in e["todo"]) + '</ol>'
                    + f'<h2 id="related">Related</h2><ul>{rel_links}</ul>'
                    + T.trust_bottom(rel, path, e["title"], e, "Verified against (official sources)") + '</article>'
                    + T.side_nav(rel, toc, others, "More news") + '</div>' + signup(rel, "news-" + e["id"]) + '</main>')
        desc = e["summary"]  # page() trims to <=158 chars, preferring a sentence end
        pages.append(page(e["u"], f'{e["title"]} | {SITE_NAME}', desc, body, "article"))
    print(f"News: {len(its)} items ({sum(1 for e in its if e['kind'] == 'news')} curated, {sum(1 for e in its if e['kind'] == 'vuln')} exploited vulnerabilities), {len(pages)} pages")
    return pages


def feed(SITE, SITE_NAME, CY):
    its = items(CY)[:50]
    esc = T.esc
    newest = its[0]["date"] if its else "2026-01-01"
    ent = "".join(f'<entry><title>{esc(e["title"])}</title><link href="{SITE}/{e["u"]}"/><id>{SITE}/{e["u"]}</id><updated>{e["date"]}T00:00:00Z</updated>'
                  f'<category term="{esc(e["category"])}"/><summary>{esc(e["summary"])}</summary></entry>' for e in its)
    return ('<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">'
            f'<title>{esc(SITE_NAME)} – News &amp; retirements</title><link href="{SITE}/news/feed.xml" rel="self"/><link href="{SITE}/news/"/>'
            f'<id>{SITE}/news/</id><updated>{newest}T00:00:00Z</updated><author><name>Tenant Recipes editorial</name></author>{ent}</feed>\n')


def search_docs(CY):
    out = [{"t": "News & retirements", "k": "Page", "c": "Site", "u": "news/index.html", "s": "Microsoft 365 changes, retirements and exploited vulnerabilities, newest first."}]
    for e in load_curated():
        out.append({"t": e["title"], "k": "News", "c": e["category"], "s": e["summary"][:220], "x": (e["why"] + " " + " ".join(e["todo"]))[:360], "u": e["u"], "d": e["date"]})
    return out
