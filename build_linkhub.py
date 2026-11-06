"""IT link hub (/links/) and AI link department (/links/ai/).

Data: data/links/hub.json and data/links/ai.json.
Client filter/search: assets/links.js (CSP 'self', no inline handlers).
"""
import json
import pathlib
from html import escape as E
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "links"
KIND_LABEL = {
    "docs": "Docs",
    "product": "Product",
    "tool": "Tool",
    "community": "Community",
    "standard": "Standard",
    "portal": "Portal",
}


def load_hub():
    return json.loads((DATA_DIR / "hub.json").read_text())


def load_ai():
    return json.loads((DATA_DIR / "ai.json").read_text())


def _href(rel, link):
    u = link["url"]
    if link.get("internal"):
        path = u[1:] if u.startswith("/") else u
        return rel + path
    return E(u, quote=True)


def _kind(link):
    k = (link.get("kind") or "docs").lower()
    return k if k in KIND_LABEL else "docs"


def _search_blob(link, section_title):
    parts = [link.get("label", ""), link.get("note", ""), link.get("aka", ""),
             section_title, KIND_LABEL.get(_kind(link), ""), " ".join(link.get("tags") or [])]
    return E(" ".join(parts).lower(), quote=True)


def _link_card(rel, link, section_title):
    href = _href(rel, link)
    external = not link.get("internal")
    kind = _kind(link)
    aka = link.get("aka")
    note = link.get("note") or ""
    status = link.get("status")  # optional: blocked|timeout|auth — truthful, not "verified"
    rel_attr = ' rel="noopener"' if external else ""
    target = ' target="_blank"' if external else ""
    ext = ' <span class="lh-ext" aria-hidden="true">↗</span>' if external else ""
    aka_html = f'<code class="lh-aka">{E(aka)}</code>' if aka else ""
    st_html = f'<span class="lh-status lh-st-{E(status)}">{E(status)}</span>' if status else ""
    return (
        f'<li class="lh-item" data-sec="{E(link.get("_sec") or "")}" data-kind="{E(kind)}" '
        f'data-q="{_search_blob(link, section_title)}">'
        f'<a class="lh-a" href="{href}"{target}{rel_attr}>'
        f'<span class="lh-top"><span class="lh-kind lh-k-{E(kind)}">{E(KIND_LABEL[kind])}</span>'
        f'{aka_html}{st_html}</span>'
        f'<span class="lh-lab">{E(link["label"])}{ext}</span>'
        f'<span class="lh-note">{E(note)}</span>'
        f'</a></li>'
    )


def _toolbar(section_ids_titles, page_key):
    chips = "".join(
        f'<button type="button" class="chip lh-chip" data-lh-sec="{E(sid)}" aria-pressed="false">{E(title)}</button>'
        for sid, title in section_ids_titles
    )
    kinds = "".join(
        f'<button type="button" class="chip lh-chip" data-lh-kind="{E(k)}" aria-pressed="false">{E(lab)}</button>'
        for k, lab in KIND_LABEL.items()
    )
    return (
        f'<div class="lh-tools" data-lh-root="{E(page_key)}" role="search">'
        f'<label class="lh-search-lab" for="lh-q-{E(page_key)}">Filter links</label>'
        f'<div class="lh-search-row">'
        f'<input id="lh-q-{E(page_key)}" class="lh-q" type="search" autocomplete="off" '
        f'placeholder="Filter by name, note, aka.ms…" aria-controls="lh-results-{E(page_key)}">'
        f'<button type="button" class="btn lh-clear" data-lh-clear hidden>Clear</button>'
        f'</div>'
        f'<div class="lh-filters" role="group" aria-label="Filter by section">'
        f'<button type="button" class="chip lh-chip on" data-lh-sec="all" aria-pressed="true">All sections</button>'
        f'{chips}</div>'
        f'<div class="lh-filters" role="group" aria-label="Filter by type">'
        f'<button type="button" class="chip lh-chip on" data-lh-kind="all" aria-pressed="true">All types</button>'
        f'{kinds}</div>'
        f'<p class="fine lh-count" data-lh-count aria-live="polite"></p>'
        f'</div>'
    )


def _toc(sections):
    return "".join(f'<li><a href="#{E(s["id"])}">{E(s["title"])}</a></li>' for s in sections)


def _sections_html(rel, sections):
    out = ""
    for s in sections:
        for L in s["links"]:
            L["_sec"] = s["id"]
        feat = " lh-feat" if s.get("featured") else ""
        rows = "".join(_link_card(rel, L, s["title"]) for L in s["links"])
        out += (
            f'<section class="lh-sec{feat}" id="{E(s["id"])}" data-sec="{E(s["id"])}" '
            f'aria-labelledby="h-{E(s["id"])}">'
            f'<h2 id="h-{E(s["id"])}">{E(s["title"])} '
            f'<span class="lh-n fine">({len(s["links"])})</span></h2>'
            f'<p class="fine">{E(s.get("blurb") or "")}</p>'
            f'<ul class="lh-list">{rows}</ul></section>'
        )
    return out


def _notice(data, extra=""):
    return (
        f'<aside class="tl-perm pl-notice" role="note">{T.icon("info")}<span>'
        f'<strong>Independent bookmarks.</strong> Not affiliated with the vendors listed. '
        f'Last bulk review <time datetime="{E(data["checked"])}">{E(T.fmt(data["checked"]))}</time>. '
        f'Sign-in portals may challenge for auth from this network — expected. '
        f'{E(data.get("guardrails") or "")}{extra}</span></aside>'
    )


def body_hub(rel, data):
    pairs = [(s["id"], s["title"]) for s in data["sections"]]
    omit = f'<p class="fine lh-omit">{E(data["omitted_note"])}</p>' if data.get("omitted_note") else ""
    return (
        _notice(data)
        + f'<nav class="lh-toc" aria-label="Sections on this page"><p class="ps-h">{T.icon("list")}Jump to</p>'
        + f'<ol>{_toc(data["sections"])}</ol></nav>'
        + f'<p>{E(data["intro"])}</p>'
        + _toolbar(pairs, "hub")
        + f'<div id="lh-results-hub">{_sections_html(rel, data["sections"])}</div>'
        + omit
    )


def body_ai(rel, data):
    pairs = [(s["id"], s["title"]) for s in data["sections"]]
    parent = data.get("parent") or {}
    related = data.get("related_internal") or []
    rel_html = "".join(
        f'<li><a href="{rel}{E(x["url"])}">{E(x["label"])}</a>'
        f'<span class="fine"> — {E(x.get("note") or "")}</span></li>'
        for x in related
    )
    parent_html = (
        f'<p class="fine"><a href="{rel}{E(parent["url"])}">← {E(parent["label"])}</a> · '
        f'Explore AI documentation, tools and governance resources by category.</p>'
        if parent else ""
    )
    return (
        _notice(data, " Listings are not approval to upload company data to any model or SaaS.")
        + parent_html
        + (f'<section class="lh-related" aria-label="Related Tenant Recipes pages"><h2>On Tenant Recipes</h2>'
           f'<ul>{rel_html}</ul></section>' if rel_html else "")
        + f'<nav class="lh-toc" aria-label="Sections on this page"><p class="ps-h">{T.icon("list")}Jump to</p>'
        + f'<ol>{_toc(data["sections"])}</ol></nav>'
        + f'<p>{E(data["intro"])}</p>'
        + _toolbar(pairs, "ai")
        + f'<div id="lh-results-ai">{_sections_html(rel, data["sections"])}</div>'
    )



def build(page, esc, signup, SITE_NAME):
    hub, ai = load_hub(), load_ai()
    pages = []

    def hub_body(rel):
        n = sum(len(s["links"]) for s in hub["sections"])
        chips = (T.chip("link", f"{n} links")
                 + T.chip("layers", f'{len(hub["sections"])} sections')
                 + T.chip("clock", f'Checked {T.fmt(hub["checked"])}'))
        return (
            T.page_hero(
                rel,
                T.crumbs_dark(rel, "links/index.html",
                              [("Home", rel + "index.html"), ("IT link hub", None)]),
                f'{T.icon("link")}Resources',
                esc(hub["title"]),
                esc(hub["short"]),
                chips,
                kind="page",
            )
            + f'<main class="wrap pg"><article class="prose doc lh" data-lh-page>{body_hub(rel, hub)}</article>'
            + signup(rel, "links-index")
            + f'<script src="{rel}assets/links.js" defer></script></main>'
        )

    def ai_body(rel):
        n = sum(len(s["links"]) for s in ai["sections"])
        chips = (T.chip("link", f"{n} links")
                 + T.chip("layers", f'{len(ai["sections"])} sections')
                 + T.chip("clock", f'Checked {T.fmt(ai["checked"])}'))
        return (
            T.page_hero(
                rel,
                T.crumbs_dark(rel, "links/ai/index.html",
                              [("Home", rel + "index.html"),
                               ("IT link hub", rel + "links/index.html"),
                               ("AI", None)]),
                f'{T.icon("link")}AI resources',
                esc(ai["title"]),
                esc(ai["short"]),
                chips,
                kind="page",
            )
            + f'<main class="wrap pg"><article class="prose doc lh" data-lh-page>{body_ai(rel, ai)}</article>'
            + signup(rel, "links-ai")
            + f'<script src="{rel}assets/links.js" defer></script></main>'
        )

    pages.append(page(
        "links/index.html",
        f'{hub["title"]}: networking to AI | {SITE_NAME}',
        hub["description"],
        hub_body,
    ))
    pages.append(page(
        "links/ai/index.html",
        f'{ai["title"]}: assistants, APIs, RAG and governance | {SITE_NAME}',
        ai["description"],
        ai_body,
    ))
    print(f'Link hub: {len(hub["sections"])} sections / {sum(len(s["links"]) for s in hub["sections"])} links; '
          f'AI dept: {len(ai["sections"])} sections / {sum(len(s["links"]) for s in ai["sections"])} links '
          f'(checked {hub["checked"]})')
    return pages


def search_docs():
    out = []
    for loader, path in ((load_hub, "links/index.html"), (load_ai, "links/ai/index.html")):
        data = loader()
        blob = " ".join(
            f'{L.get("label","")} {L.get("note","")} {L.get("aka","")}'
            for s in data["sections"] for L in s["links"]
        )
        out.append({
            "t": data["title"],
            "k": "Page",
            "c": "Site",
            "u": path,
            "s": data["description"][:220],
            "x": (data["intro"] + " " + blob)[:360],
            "d": data.get("checked"),
        })
    return out
