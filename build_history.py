"""Per-page dates, version history and a visible sources block (2026-10-31).
History is assembled automatically, so older pages need no hand-written history:
  1. "Initial publication" on the published date (recipe `created`, guide PUBLISHED)
  2. every data/changelog.json entry whose `url` is this page
  3. optional per-page notes: recipe "history": [{"date": "YYYY-MM-DD", "note": "..."}], guide HISTORY = [("YYYY-MM-DD", "...")]
  4. "Updated" on the last-updated date and "Re-verified against sources" on the last-verified date, unless already covered."""
import json, pathlib, datetime
from html import escape as E
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent
_CL = None


def _changelog():
    global _CL
    if _CL is None:
        _CL = json.loads((ROOT / "data" / "changelog.json").read_text())
    return _CL


def fmt(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%b %Y')}"


def entries(path, published, updated, verified, extra=()):
    """[(date, time, label, text)] newest first."""
    out = []
    if published:
        out.append((published, "", "Published", "Initial publication."))
    for s in _changelog():
        if s.get("url") == path:
            out.append((s["date"], s.get("time") or "", s.get("type") or "Update", s.get("blurb") or s.get("text") or s.get("title") or ""))
    for d, note in extra:
        out.append((d, "", "Update", note))
    dates = {e[0] for e in out}
    if updated and updated not in dates:
        out.append((updated, "", "Updated", "Content updated."))
        dates.add(updated)
    if verified and verified not in dates:
        out.append((verified, "", "Verified", "Re-verified against the linked sources."))
    # same date as publication: fold a curated 'new page' note into the published line
    out.sort(key=lambda e: (e[0], e[1], e[2] != "Published"), reverse=True)
    return out


def dates_bar(published, updated, verified):
    bits = []
    if published:
        bits.append(f'<span><b>Published</b> <time datetime="{published}">{fmt(published)}</time></span>')
    if updated:
        bits.append(f'<span><b>Last updated</b> <time datetime="{updated}">{fmt(updated)}</time></span>')
    if verified:
        bits.append(f'<span><b>Last verified</b> <time datetime="{verified}">{fmt(verified)}</time></span>')
    bits.append('<a href="#history">Version history</a><a href="#sources">Sources</a>')
    return f'<p class="pd" aria-label="Page dates">{"".join(bits)}</p>'


def history_html(path, published, updated, verified, extra=()):
    ev = entries(path, published, updated, verified, extra)
    lis = "".join(f'<li><time datetime="{d}">{fmt(d)}{(" " + E(t)) if t else ""}</time><span class="vh-k">{E(k)}</span>{E(x)}</li>' for d, t, k, x in ev)
    return (f'<section class="vh" id="history" aria-labelledby="vh-h"><h2 id="vh-h">Version history</h2>'
            f'<ol class="vh-l">{lis}</ol><p class="fine">Times are Europe/Stockholm. Site-wide history: <a href="{"../" * path.count("/")}changelog/index.html">changelog</a>.</p></section>')


def _host(u):
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def sources_top(items, label="Sources", total=None, note=""):
    """items: [(title, url, extra_text)] shown near the top of the page."""
    lis = "".join(f'<li><a href="{E(u)}">{E(t)}</a><span class="st-h">{E(_host(u))}{(" · " + E(x)) if x else ""}</span></li>' for t, u, x in items)
    more = f' <span class="fine">({len(items)} of {total} shown)</span>' if total and total > len(items) else ""
    return (f'<section class="st" id="sources" aria-labelledby="st-h"><h2 id="st-h">{E(label)}{more}</h2>'
            + (f'<p class="fine">{note}</p>' if note else "") + f'<ul class="st-l">{lis}</ul></section>')


def recipe_sources(r):
    return sources_top([(s["title"], s["url"], f'checked {fmt(s["checked"])}' if s.get("checked") else "") for s in r["sources"]],
                       "Sources", note='Every step was compared with these sources. Full verification details are at the <a href="#verified">end of the page</a>.')


def guide_sources(g, n=8):
    from collections import Counter
    cnt = Counter((t, u) for p in g.PHASES for s in p["steps"] for t, u in s["src"])
    for t, u in getattr(g, "PROBLEM", {}).get("src", []):
        cnt[(t, u)] += 0
    top = [(t, u, f'cited in {c} step{"s" if c != 1 else ""}' if c else "background") for (t, u), c in cnt.most_common(n)]
    return sources_top(top, "Key sources", len(cnt),
                       note='The most-cited references for this guide. Each step lists its own sources under “' + E(getattr(g, "SRC_LABEL", "Microsoft sources")) + '”.')
