"""Admin link hub (/links/): curated portals, docs and stable aka.ms shortcuts.

Data: data/links.json. Only include aka.ms entries that resolve to a useful public
destination; re-check periodically (see the "checked" field in the JSON).
"""
import json
import pathlib
from html import escape as E
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data" / "links.json"


def load():
    return json.loads(DATA.read_text())


def _href(rel, link):
    u = link["url"]
    if link.get("internal"):
        # Allow "/guides/…" style paths in data; resolve against site root.
        path = u[1:] if u.startswith("/") else u
        return rel + path
    return E(u, quote=True)


def _link_row(rel, link):
    href = _href(rel, link)
    external = not link.get("internal")
    aka = link.get("aka")
    note = link.get("note")
    rel_attr = ' rel="noopener"' if external else ""
    target = ' target="_blank"' if external else ""
    aka_html = f'<code class="lh-aka">{E(aka)}</code>' if aka else ""
    note_html = f'<span class="lh-note">{E(note)}</span>' if note else ""
    ext = ' <span class="lh-ext" aria-hidden="true">↗</span>' if external else ""
    return (f'<li><a class="lh-a" href="{href}"{target}{rel_attr}>'
            f'<span class="lh-lab">{E(link["label"])}{ext}</span>'
            f'{aka_html}{note_html}</a></li>')


def body(rel, esc, data):
    toc = "".join(f'<li><a href="#{E(s["id"])}">{E(s["title"])}</a></li>' for s in data["sections"])
    sections = ""
    for s in data["sections"]:
        feat = ' lh-feat' if s.get("featured") else ""
        rows = "".join(_link_row(rel, L) for L in s["links"])
        sections += (
            f'<section class="lh-sec{feat}" id="{E(s["id"])}" aria-labelledby="h-{E(s["id"])}">'
            f'<h2 id="h-{E(s["id"])}">{E(s["title"])}</h2>'
            f'<p class="fine">{E(s.get("blurb") or "")}</p>'
            f'<ul class="lh-list">{rows}</ul></section>'
        )
    omit = data.get("omitted_note") or ""
    omit_html = f'<p class="fine lh-omit">{E(omit)}</p>' if omit else ""
    return (
        f'<aside class="tl-perm pl-notice" role="note">{T.icon("info")}<span>'
        f'<strong>Independent bookmarks.</strong> Not affiliated with Microsoft. '
        f'aka.ms and portal destinations change; last bulk check '
        f'<time datetime="{E(data["checked"])}">{E(T.fmt(data["checked"]))}</time>. '
        f'Sign-in portals may return an auth challenge from this network — that is expected.</span></aside>'
        f'<nav class="lh-toc" aria-label="Sections on this page"><p class="ps-h">{T.icon("list")}Jump to</p>'
        f'<ol>{toc}</ol></nav>'
        f'<p>{E(data["intro"])}</p>'
        f'{sections}{omit_html}'
    )


def build(page, esc, signup, SITE_NAME):
    data = load()

    def b(rel):
        chips = (T.chip("link", f'{sum(len(s["links"]) for s in data["sections"])} links')
                 + T.chip("layers", f'{len(data["sections"])} sections')
                 + T.chip("clock", f'Checked {T.fmt(data["checked"])}'))
        return (
            T.page_hero(
                rel,
                T.crumbs_dark(rel, "links/index.html", [("Home", rel + "index.html"), ("Admin links", None)]),
                f'{T.icon("link")}Resources',
                esc(data["title"]),
                esc(data["short"]),
                chips,
                kind="page",
            )
            + f'<main class="wrap pg"><article class="prose doc lh">{body(rel, esc, data)}</article>'
            + signup(rel, "links-index")
            + "</main>"
        )

    p = page(
        "links/index.html",
        f'{data["title"]}: portals, docs and aka.ms | {SITE_NAME}',
        data["description"],
        b,
    )
    print(f'Link hub: {len(data["sections"])} sections, '
          f'{sum(len(s["links"]) for s in data["sections"])} links '
          f'(checked {data["checked"]})')
    return [p]


def search_docs():
    data = load()
    aka = " ".join(
        L.get("aka", "") for s in data["sections"] for L in s["links"] if L.get("aka")
    )
    return [{
        "t": data["title"],
        "k": "Page",
        "c": "Site",
        "u": "links/index.html",
        "s": data["description"][:220],
        "x": (data["intro"] + " " + aka)[:360],
        "d": data.get("checked"),
    }]
