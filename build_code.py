"""Code Library (/code/): copy-ready PowerShell, Azure CLI, azcmagent, Bicep, KQL, Graph/JSON and YAML snippets.
One snippet = data/code/<id>.json. Every snippet is taken (and condensed) from an existing guide step or recipe on this site
and links back to it plus the official references it was checked against. Static, no backend.
Schema: id, status, title, lang (see LANGS), tags[], summary, code, notes[], source {kind: guide|recipe, slug|id, anchor?, label},
refs [{title, url}] (https), created, last_verified. The build fails on invalid data or an unknown source."""
import json, re, sys, pathlib
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
LANGS = {"powershell": "PowerShell", "azcli": "Azure CLI", "shell": "azcmagent / shell", "bicep": "Bicep", "kql": "KQL",
         "json": "Graph / JSON", "http": "Graph HTTP", "yaml": "YAML"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(recipe_ids=(), guide_slugs=()):
    out, errs = [], []
    for f in sorted((ROOT / "data" / "code").glob("*.json")):
        s = json.loads(f.read_text())
        p = f.name
        for k in ("id", "status", "title", "lang", "tags", "summary", "code", "source", "refs", "created", "last_verified"):
            if k not in s:
                errs.append(f"{p}: missing {k}")
        if errs:
            continue
        if s["id"] + ".json" != p:
            errs.append(f"{p}: id must match file name")
        if s["lang"] not in LANGS:
            errs.append(f"{p}: lang must be one of {sorted(LANGS)}")
        src = s["source"]
        if src.get("kind") == "guide" and src.get("slug") not in guide_slugs:
            errs.append(f"{p}: unknown guide slug {src.get('slug')}")
        if src.get("kind") == "recipe" and src.get("id") not in recipe_ids:
            errs.append(f"{p}: unknown recipe id {src.get('id')}")
        if src.get("kind") not in ("guide", "recipe"):
            errs.append(f"{p}: source.kind must be guide or recipe")
        if not s["refs"] or not all(str(r.get("url", "")).startswith("https://") and r.get("title") for r in s["refs"]):
            errs.append(f"{p}: refs need title and https url")
        for k in ("created", "last_verified"):
            if not DATE.match(str(s[k])):
                errs.append(f"{p}: {k} must be YYYY-MM-DD")
        if s["status"] == "published":
            out.append(s)
    if errs:
        sys.exit("Code library validation failed:\n  " + "\n  ".join(errs))
    return out


def _src_href(rel, s):
    src = s["source"]
    if src["kind"] == "guide":
        return f'{rel}guides/{src["slug"]}.html' + (f'#{src["anchor"]}' if src.get("anchor") else "")
    return f'{rel}recipes/{src["id"]}.html'


def _block(esc, s, cid):
    return (f'<pre class="cb cl-code" data-lang="{s["lang"]}"><code id="{cid}">{esc(s["code"])}</code></pre>')


def build(page, esc, fmt_date, signup, SITE_NAME, recipe_ids, guide_slugs):
    S = load(recipe_ids, guide_slugs)
    pages = []
    langs = {k: v for k, v in LANGS.items() if any(s["lang"] == k for s in S)}
    tags = sorted({t for s in S for t in s["tags"]})
    last = max(s["last_verified"] for s in S)

    def lang_badge(s):
        return f'<span class="cl-lang cl-{s["lang"]}">{esc(LANGS[s["lang"]])}</span>'

    def card(rel, s):
        return (f'<article class="cl-card" id="{s["id"]}" data-lang="{s["lang"]}" data-tags="{esc("|".join(s["tags"]))}">'
                f'<header><p class="cl-meta">{lang_badge(s)}' + "".join(f'<span class="cl-tag">{esc(t)}</span>' for t in s["tags"]) + '</p>'
                f'<h3><a href="{rel}code/{s["id"]}.html">{esc(s["title"])}</a></h3><p>{esc(s["summary"])}</p></header>'
                + _block(esc, s, f'c-{s["id"]}') +
                f'<p class="cl-from">From: <a href="{_src_href(rel, s)}">{esc(s["source"]["label"])}</a> · '
                f'<a href="{rel}code/{s["id"]}.html">Notes &amp; sources →</a></p></article>')

    def index(rel):
        chips = ('<div class="chips cl-f" id="cl-lang" role="group" aria-label="Filter by language" hidden>'
                 f'<button type="button" class="chip on" data-v="" aria-pressed="true">All <span>{len(S)}</span></button>'
                 + "".join(f'<button type="button" class="chip" data-v="{k}" aria-pressed="false">{esc(v)} <span>{sum(1 for s in S if s["lang"] == k)}</span></button>' for k, v in langs.items())
                 + '</div><div class="chips cl-f" id="cl-tag" role="group" aria-label="Filter by topic" hidden>'
                 f'<button type="button" class="chip on" data-v="" aria-pressed="true">All topics</button>'
                 + "".join(f'<button type="button" class="chip" data-v="{esc(t)}" aria-pressed="false">{esc(t)}</button>' for t in tags) + '</div>'
                 '<p class="fine" id="cl-n" aria-live="polite"></p>')
        js = ('<script>(function(){var L="",G="",n=document.getElementById("cl-n"),c=document.querySelectorAll(".cl-card");'
              'function ap(){var k=0;c.forEach(function(x){var s=(!L||x.dataset.lang===L)&&(!G||x.dataset.tags.split("|").indexOf(G)>-1);x.hidden=!s;if(s)k++});'
              'n.textContent=(L||G)?k+" snippet"+(k===1?"":"s"):""}'
              '["cl-lang","cl-tag"].forEach(function(id){var w=document.getElementById(id);w.hidden=false;w.addEventListener("click",function(e){var b=e.target.closest("button[data-v]");if(!b)return;'
              'w.querySelectorAll("button").forEach(function(y){var on=y===b;y.classList.toggle("on",on);y.setAttribute("aria-pressed",on?"true":"false")});'
              'if(id==="cl-lang")L=b.dataset.v;else G=b.dataset.v;ap()})});'
              'var q=new URLSearchParams(location.search).get("lang");if(q){var b=document.querySelector(\'#cl-lang [data-v="\'+q+\'"]\');if(b)b.click()}})();</script>')
        return (T.page_hero(rel, T.crumbs_dark(rel, "code/index.html", [("Home", rel + "index.html"), ("Code Library", None)]), "Code Library",
                            "Copy-ready snippets for Microsoft Cloud admins",
                            f'{len(S)} PowerShell, Azure CLI, Bicep, KQL and Graph snippets lifted from our guides and recipes. Each one links back to the step it '
                            f'belongs to and to the official reference it was checked against. Last verified {fmt_date(last)}.', kind="page")
                + f'<main class="wrap pg"><aside class="co co-warn"><p class="co-h">{T.icon("alert")}Read before you paste</p><p>Replace every '
                '<code>&lt;placeholder&gt;</code>, run against a test subscription or tenant first, and read the linked step for prerequisites, '
                'permissions and rollback. Never paste secrets into a script file.</p></aside>'
                + chips + f'<div class="cl-g">{"".join(card(rel, s) for s in S)}</div>' + js
                + f'<p class="fine">Suggest a snippet or report a problem via the <a href="{rel}contact/index.html">contact page</a>.</p>'
                + signup(rel, "code-index") + '</main>')
    pages.append(page("code/index.html", f"Code Library: PowerShell, Azure CLI, Bicep, KQL and Graph snippets | {SITE_NAME}",
                      "Copy-ready PowerShell, Azure CLI, Bicep, KQL and Microsoft Graph snippets for Intune, Azure Arc, Update Manager and Conditional Access, each linked to its guide.",
                      index))

    for s in S:
        def body(rel, s=s):
            refs = "".join(f'<li><a href="{esc(r["url"])}">{esc(r["title"])}</a></li>' for r in s["refs"])
            notes = "".join(f'<li>{esc(x)}</li>' for x in s.get("notes", []))
            return (T.page_hero(rel, T.crumbs_dark(rel, f'code/{s["id"]}.html', [("Home", rel + "index.html"), ("Code Library", rel + "code/index.html"), (LANGS[s["lang"]], None)]),
                                f'{esc(LANGS[s["lang"]])} snippet', esc(s["title"]), esc(s["summary"]), kind="page")
                    + '<main class="wrap pg"><article class="doc">'
                    + f'<p class="pd"><span><b>Published</b> <time datetime="{s["created"]}">{fmt_date(s["created"])}</time></span>'
                    f'<span><b>Last verified</b> <time datetime="{s["last_verified"]}">{fmt_date(s["last_verified"])}</time></span>'
                    f'<a href="{_src_href(rel, s)}">Source on this site</a><a href="#sources">Sources</a></p>'
                    + f'<p class="cl-meta">{lang_badge(s)}' + "".join(f'<span class="cl-tag">{esc(t)}</span>' for t in s["tags"]) + '</p>'
                    + _block(esc, s, f'c-{s["id"]}')
                    + (f'<section class="co co-warn"><p class="co-h">{T.icon("alert")}Before you run it</p><ul>{notes}</ul></section>' if notes else "")
                    + f'<section class="co co-info"><p class="co-h">{T.icon("book")}Context</p><p>This snippet is condensed from '
                    f'<a href="{_src_href(rel, s)}">{esc(s["source"]["label"])}</a>, which explains prerequisites, permissions, verification and rollback.</p></section>'
                    + f'<section class="st" id="sources"><h2>Official references</h2><ul class="st-l">{refs}</ul></section>'
                    + f'<p><a class="btn" href="{rel}code/index.html?lang={s["lang"]}">More {esc(LANGS[s["lang"]])} snippets →</a></p>'
                    + '</article></main>')
        pages.append(page(f'code/{s["id"]}.html', f'{s["title"]} ({LANGS[s["lang"]]}) | {SITE_NAME}', s["summary"], body, "article"))
    print(f"Code library: {len(S)} snippets, {len(langs)} languages, {len(pages)} pages")
    return pages


def search_docs():
    return [{"t": s["title"], "k": "Code", "c": LANGS[s["lang"]], "s": s["summary"], "u": f'code/{s["id"]}.html', "x": " ".join(s["tags"]) + " " + s["code"][:300]}
            for s in load(recipe_ids=_all_recipe_ids(), guide_slugs=_all_guide_slugs())]


def _all_recipe_ids():
    return {p.stem for p in (ROOT / "data" / "recipes").glob("*.json")}


def _all_guide_slugs():
    out = set()
    for f in (ROOT / "data" / "guides").glob("*.py"):
        m = re.search(r'^SLUG = "([^"]+)"', f.read_text(), re.M)
        if m:
            out.add(m.group(1))
    return out
