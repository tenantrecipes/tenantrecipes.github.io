"""Draft /ignite/ hub and a date-driven homepage banner for Microsoft Ignite 2026.

PUBLISHED is False until Krister approves going live. A normal `python3 build.py`
does not write /ignite/ into dist/ or add the homepage banner, so an evening
publish cannot ship this by accident. Preview:

  TR_PREVIEW=1 TR_IGNITE_DRAFT=1 TR_DIST=/workspace/m365ai-ignite/preview python3 build_site.py

News items appear here only when data/news/<id>.json has "ignite": true.
Optional "ignite_area" (copilot|security|endpoint|collaboration|azure) overrides
the category-based grouping. See drafts/ignite-hub-README.md and RECIPES.md.

Visuals are original CSS/SVG only — no Microsoft logos, Ignite brand artwork,
photos or official imagery. Official event pages are linked, not copied.
"""
from __future__ import annotations

import datetime, os, pathlib
from html import escape as E
from zoneinfo import ZoneInfo

import build_news as NW
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
PUBLISHED = True  # approved by Krister 2026-11-16 19:08 ("Ja, publicera i kväll")
PATH = "ignite/index.html"
TITLE = "Microsoft Ignite 2026: short news for Microsoft 365 admins"
LEAD = (
    "Independent, source-linked coverage of Microsoft Ignite 2026 for tenant admins — "
    "short news items, grouped by area, with what to watch. Not affiliated with Microsoft."
)

STOCKHOLM = ZoneInfo("Europe/Stockholm")
# Conference days are 17–20 Nov 2026 (Moscone Center, San Francisco, and online).
# The homepage banner also covers Security Pre-Day on 16 Nov and hides after the 20th,
# using calendar dates in Europe/Stockholm.
BANNER_START = datetime.date(2026, 11, 16)
BANNER_END = datetime.date(2026, 11, 20)
EVENT_START = datetime.date(2026, 11, 17)
EVENT_END = datetime.date(2026, 11, 20)

# Opening keynote: 17 Nov 2026, 10:00–12:00 PT at Chase Center and online
# = 19:00–21:00 Europe/Stockholm (PST UTC-8, CET UTC+1).
KEYNOTE_PT = "10:00–12:00 PT"
KEYNOTE_SE = "19:00–21:00 Europe/Stockholm"
OFFICIAL_HOME = "https://ignite.microsoft.com/en-US/home"
OFFICIAL_SESSIONS = "https://ignite.microsoft.com/en-US/sessions"
# Book of News 2026 URL is not confirmed; do not present a 2026 Book of News as fact.

AREAS = [
    ("copilot", "Copilot & agents", "Copilot, agents, plugins and Copilot Studio."),
    ("security", "Security, Entra, Defender and Purview", "Identity, threat protection, data security and governance."),
    ("endpoint", "Intune & Windows", "Device management, Windows and endpoint changes."),
    ("collaboration", "Teams, SharePoint and Exchange", "Collaboration apps and the Microsoft 365 substrate."),
    ("azure", "Azure & infrastructure", "Azure, cloud infrastructure and related platform news."),
]
AREA_IDS = {a[0] for a in AREAS}
CAT_AREA = {
    "Copilot/AI": "copilot",
    "Entra": "security",
    "Defender": "security",
    "Purview": "security",
    "Security incidents": "security",
    "Regulation": "security",
    "Intune": "endpoint",
    "Windows": "endpoint",
    "M365": "collaboration",
}
AREA_HINTS = (
    ("azure", r"\bazure\b|arc\b|foundry|fabric|aks\b|defender for cloud"),
    ("copilot", r"copilot|\bagents?\b|plugin|cowork|copilot studio"),
    ("security", r"entra|defender|purview|sentinel|\bmfa\b|passkey|conditional access|zero trust|dlp\b"),
    ("endpoint", r"intune|windows|autopilot|\bwdac\b|endpoint"),
    ("collaboration", r"teams|sharepoint|exchange|outlook|onedrive|loop\b|viva"),
)


def today_stockholm(today=None) -> datetime.date:
    if today is not None:
        return today
    return datetime.datetime.now(STOCKHOLM).date()


def banner_open(today=None) -> bool:
    d = today_stockholm(today)
    return BANNER_START <= d <= BANNER_END


def event_open(today=None) -> bool:
    d = today_stockholm(today)
    return EVENT_START <= d <= EVENT_END


def should_emit(dist: pathlib.Path | None = None) -> bool:
    """Write hub/banner only when published, or in an explicit preview dir."""
    if PUBLISHED:
        return True
    if not (os.environ.get("TR_IGNITE_DRAFT") and os.environ.get("TR_PREVIEW")):
        return False
    if dist is None:
        raw = os.environ.get("TR_DIST")
        dist = pathlib.Path(raw).resolve() if raw else (ROOT / "dist")
    try:
        if dist.resolve() == (ROOT / "dist").resolve():
            return False
    except Exception:
        return False
    return True


def _area_for(e: dict) -> str:
    explicit = (e.get("ignite_area") or "").strip().lower()
    if explicit in AREA_IDS:
        return explicit
    import re
    blob = f'{e.get("category", "")} {e.get("title", "")} {e.get("summary", "")}'
    for aid, pat in AREA_HINTS:
        if re.search(pat, blob, re.I):
            return aid
    return CAT_AREA.get(e.get("category"), "collaboration")


def ignite_items() -> list[dict]:
    out = []
    for e in NW.load_curated():
        if e.get("ignite") is True or e.get("ignite") == "true":
            e = dict(e)
            e["ignite_area"] = _area_for(e)
            out.append(e)
    return sorted(out, key=lambda e: (e["date"], e["title"]), reverse=True)


def _decor() -> str:
    """Original geometric SVG atmosphere. Not a Microsoft/Ignite logo or brand mark."""
    return (
        '<svg class="ig-decor" viewBox="0 0 800 800" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">'
        '<defs>'
        '<linearGradient id="ig-g1" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#ff2d8f"/><stop offset=".45" stop-color="#ff5a00"/><stop offset="1" stop-color="#ffd000"/>'
        '</linearGradient>'
        '<linearGradient id="ig-g2" x1="1" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#7a3dff"/><stop offset="1" stop-color="#00d0ff"/>'
        '</linearGradient>'
        '</defs>'
        '<polygon points="640,40 780,180 620,220" fill="url(#ig-g1)" opacity=".85"/>'
        '<polygon points="700,260 790,430 620,400" fill="url(#ig-g2)" opacity=".75"/>'
        '<circle cx="520" cy="80" r="54" fill="#ffd000" opacity=".9"/>'
        '<circle cx="760" cy="520" r="86" fill="#ff2d8f" opacity=".55"/>'
        '<rect x="500" y="560" width="180" height="180" rx="28" transform="rotate(-18 590 650)" fill="#00d0ff" opacity=".7"/>'
        '<g fill="#1b1024" opacity=".85">'
        '<path d="M90 70 l12 32 32 12-32 12-12 32-12-32-32-12 32-12 z"/>'
        '<path d="M430 700 l9 24 24 9-24 9-9 24-9-24-24-9 24-9 z"/>'
        '<path d="M740 80 l8 20 20 8-20 8-8 20-8-20-20-8 20-8 z"/>'
        '</g></svg>'
    )


def _blobs() -> str:
    return (
        '<span class="ig-blob ig-blob-a"></span><span class="ig-blob ig-blob-b"></span>'
        '<span class="ig-blob ig-blob-c"></span><span class="ig-blob ig-blob-d"></span>'
        '<span class="ig-blob ig-blob-e"></span>'
    )


KEYNOTE_ISO_START = "2026-11-17T19:00:00+01:00"
KEYNOTE_ISO_END = "2026-11-17T21:00:00+01:00"


def _countdown_html() -> str:
    """Server-rendered initial state (countdown / live / day-of-4), kept in sync by _countdown_js()."""
    now = datetime.datetime.now(STOCKHOLM)
    start = datetime.datetime.fromisoformat(KEYNOTE_ISO_START)
    end = datetime.datetime.fromisoformat(KEYNOTE_ISO_END)
    ev0 = datetime.datetime(2026, 11, 17, tzinfo=STOCKHOLM)
    ev1 = datetime.datetime(2026, 11, 20, 23, 59, 59, tzinfo=STOCKHOLM)

    def units(delta: datetime.timedelta) -> str:
        total = max(int(delta.total_seconds()), 0)
        d, rem = divmod(total, 86400)
        h, rem = divmod(rem, 3600)
        m, s = divmod(rem, 60)
        parts = (("d", d, "days"), ("h", h, "hours"), ("m", m, "min"), ("s", s, "sec"))
        lis = "".join(
            f'<li><strong data-{k}>{v:02d}</strong><span>{lab}</span></li>' for k, v, lab in parts
        )
        return f'<ul class="ig-count-units">{lis}</ul>'

    if now < start:
        phase, label = "countdown", "Opening keynote in"
        inner = units(start - now)
        inner += '<p class="ig-count-live" hidden>Live now</p><p class="ig-count-day" hidden></p>'
    elif now <= end:
        phase, label = "live", "Opening keynote"
        inner = (
            '<ul class="ig-count-units" hidden>'
            '<li><strong data-d>00</strong><span>days</span></li>'
            '<li><strong data-h>00</strong><span>hours</span></li>'
            '<li><strong data-m>00</strong><span>min</span></li>'
            '<li><strong data-s>00</strong><span>sec</span></li></ul>'
            '<p class="ig-count-live">Live now</p><p class="ig-count-day" hidden></p>'
        )
    elif now <= ev1:
        day = min(max((now.date() - ev0.date()).days + 1, 1), 4)
        phase, label = "days", "Microsoft Ignite 2026"
        inner = (
            '<ul class="ig-count-units" hidden>'
            '<li><strong data-d>00</strong><span>days</span></li>'
            '<li><strong data-h>00</strong><span>hours</span></li>'
            '<li><strong data-m>00</strong><span>min</span></li>'
            '<li><strong data-s>00</strong><span>sec</span></li></ul>'
            f'<p class="ig-count-live" hidden>Live now</p><p class="ig-count-day">Day {day} of 4</p>'
        )
    else:
        phase, label = "over", "Microsoft Ignite 2026"
        inner = (
            '<ul class="ig-count-units" hidden>'
            '<li><strong data-d>00</strong><span>days</span></li>'
            '<li><strong data-h>00</strong><span>hours</span></li>'
            '<li><strong data-m>00</strong><span>min</span></li>'
            '<li><strong data-s>00</strong><span>sec</span></li></ul>'
            '<p class="ig-count-live" hidden>Live now</p><p class="ig-count-day">Event archive</p>'
        )
    return (
        f'<div class="ig-count" data-ig-count data-phase="{phase}" role="timer" aria-live="polite" aria-atomic="true" '
        f'data-start="{KEYNOTE_ISO_START}" data-end="{KEYNOTE_ISO_END}">'
        f'<p class="ig-count-label">{E(label)}</p>{inner}</div>'
    )


def _countdown_js() -> str:
    # Compact, no dependencies. Updates every second unless the user prefers reduced motion (then every 30s).
    return (
        '<script>(function(){var S=Date.parse("2026-11-17T19:00:00+01:00"),E=Date.parse("2026-11-17T21:00:00+01:00"),'
        'A=Date.parse("2026-11-17T00:00:00+01:00"),B=Date.parse("2026-11-20T23:59:59+01:00");'
        'function p(n){return String(n).padStart(2,"0")}'
        'function tick(r){var n=Date.now(),L=r.querySelector(".ig-count-label"),U=r.querySelector(".ig-count-units"),'
        'V=r.querySelector(".ig-count-live"),D=r.querySelector(".ig-count-day");'
        'function hide(el,h){if(el)el.hidden=h}'
        'if(n<S){var ms=S-n,d=Math.floor(ms/864e5),h=Math.floor(ms%864e5/36e5),m=Math.floor(ms%36e5/6e4),s=Math.floor(ms%6e4/1e3);'
        'r.setAttribute("data-phase","countdown");if(L)L.textContent="Opening keynote in";'
        'if(U){hide(U,false);U.querySelector("[data-d]").textContent=p(d);U.querySelector("[data-h]").textContent=p(h);'
        'U.querySelector("[data-m]").textContent=p(m);U.querySelector("[data-s]").textContent=p(s)}hide(V,true);hide(D,true)}'
        'else if(n<=E){r.setAttribute("data-phase","live");if(L)L.textContent="Opening keynote";hide(U,true);hide(V,false);'
        'if(V)V.textContent="Live now";hide(D,true)}'
        'else if(n<=B){var day=Math.floor((n-A)/864e5)+1;if(day<1)day=1;if(day>4)day=4;'
        'r.setAttribute("data-phase","days");if(L)L.textContent="Microsoft Ignite 2026";hide(U,true);hide(V,true);'
        'hide(D,false);if(D)D.textContent="Day "+day+" of 4"}'
        'else{r.setAttribute("data-phase","over");if(L)L.textContent="Microsoft Ignite 2026";hide(U,true);hide(V,true);'
        'hide(D,false);if(D)D.textContent="Event archive"}}'
        'var roots=document.querySelectorAll("[data-ig-count]");if(!roots.length)return;'
        'function all(){roots.forEach(tick)}all();'
        'var rm=window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches;'
        'setInterval(all,rm?3e4:1e3)})();</script>'
    )


def _phase_label(today=None) -> str:
    d = today_stockholm(today)
    if d < EVENT_START:
        return "Starts tomorrow" if d == EVENT_START - datetime.timedelta(days=1) else "Coming up"
    if d <= EVENT_END:
        return "Live this week"
    return "Event archive"


def _wordmark(tag: str, hid: str, sub: str) -> str:
    return (
        f'<{tag} id="{E(hid)}" class="ig-wordmark">'
        f'<span class="ig-wm-k">Microsoft</span>'
        f'<span class="ig-wm-ignite">IGNITE</span> '
        f'<span class="ig-wm-year">2026</span>'
        f'<span class="ig-sub">{E(sub)}</span></{tag}>'
    )


def _news_cards(rel, fmt_date, items, empty_msg):
    if not items:
        return f'<p class="ig-empty">{E(empty_msg)}</p>'
    titles = {a[0]: a[1] for a in AREAS}
    lis = []
    for e in items:
        lis.append(
            f'<li><article class="ig-card"><p class="ig-card-m"><span class="ig-area ig-area-{E(e["ignite_area"])}">'
            f'{E(titles.get(e["ignite_area"], e["ignite_area"]))}</span>'
            f'<time datetime="{E(e["date"])}">{fmt_date(e["date"])}</time></p>'
            f'<h3><a href="{rel}{E(e["u"])}">{E(e["title"])}</a></h3>'
            f'<p>{E((e["summary"].split(". ")[0].rstrip(".") + "."))}</p></article></li>'
        )
    return f'<ol class="ig-cards">{"".join(lis)}</ol>'


def home_banner(rel, fmt_date, today=None) -> str:
    """Colorful homepage feature. Empty string when outside the date window or not emitting."""
    if not (should_emit() and banner_open(today)):
        return ""
    items = ignite_items()[:6]
    lis = ""
    if items:
        for e in items:
            lis += (
                f'<li><time datetime="{E(e["date"])}">{fmt_date(e["date"])}</time>'
                f'<a href="{rel}{E(e["u"])}">{E(e["title"])}</a></li>'
            )
        news = f'<ol class="ig-banner-list">{lis}</ol>'
    else:
        news = (
            '<p class="ig-banner-empty">No Ignite news items published here yet. '
            "We'll add short, fact-checked headlines as announcements are confirmed against official sources.</p>"
        )
    return (
        f'<section class="ig-banner" aria-labelledby="ig-banner-h">'
        f'<div class="ig-banner-bg" aria-hidden="true">{_blobs()}{_decor()}</div>'
        f'<div class="wrap ig-banner-in">'
        f'<div class="ig-banner-copy">'
        f'<p class="ig-kicker"><span class="ig-live" aria-hidden="true"></span>{E(_phase_label(today))} · 17–20 Nov 2026</p>'
        + _wordmark("h2", "ig-banner-h", "As it matters to admins")
        + f'<p class="ig-banner-lead">Opening keynote Tuesday 17 November, {E(KEYNOTE_SE)} '
        f'({E(KEYNOTE_PT)}), from Chase Center in San Francisco and online. Independent coverage — not affiliated with Microsoft.</p>'
        + _countdown_html()
        + f'<p class="ig-cta">'
        f'<a class="btn ig-btn" href="{rel}ignite/index.html">Open the Ignite hub</a>'
        f'<a class="btn ig-btn-2" href="{E(OFFICIAL_HOME)}" rel="noopener">Official event site</a>'
        f'</p></div>{news}</div>{_countdown_js()}</section>'
    )


def body(rel, fmt_date):
    items = ignite_items()
    by = {aid: [] for aid, *_ in AREAS}
    for e in items:
        by.setdefault(e["ignite_area"], []).append(e)
    toc = "".join(f'<li><a href="#{aid}">{E(title)}</a> <span>{len(by.get(aid, []))}</span></li>' for aid, title, _ in AREAS)
    sections = []
    empty = "No items in this area yet. They appear here once a news entry is tagged ignite and published."
    for aid, title, intro in AREAS:
        sections.append(
            f'<section class="ig-track ig-track-{aid}" id="{aid}" aria-labelledby="{aid}-h">'
            f'<header class="ig-track-h"><h2 id="{aid}-h">{E(title)}</h2><p>{E(intro)}</p></header>'
            f'{_news_cards(rel, fmt_date, by.get(aid, []), empty)}</section>'
        )
    draft = ""
    if not PUBLISHED:
        draft = (
            '<aside class="co co-warn" role="status"><p class="co-h">Draft — not published</p>'
            "<p>This hub is a local preview for review. It is not on the live site and must not be treated as published.</p></aside>"
        )
    guard = (
        "Announcements at Ignite are often previews or roadmaps. We mark anything announced but not generally "
        "available as unverified or preview, and we do not invent rollout dates. Always check the linked official source."
    )
    facts = (
        f'<dl class="ig-facts">'
        f'<div><dt>When</dt><dd>17–20 November 2026</dd></div>'
        f'<div><dt>Where</dt><dd>Moscone Center, San Francisco, and online</dd></div>'
        f'<div><dt>Opening keynote</dt><dd>Tuesday 17 November 2026, {E(KEYNOTE_SE)} ({E(KEYNOTE_PT)}), Chase Center and online. '
        f'Scheduled speakers: Satya Nadella and Judson Althoff.</dd></div>'
        f'<div><dt>Security Pre-Day</dt><dd>Monday 16 November 2026, 22:00–02:00 Europe/Stockholm (13:00–17:00 PT). Optional add-on during registration.</dd></div>'
        f'<div><dt>Official site</dt><dd><a href="{E(OFFICIAL_HOME)}" rel="noopener">ignite.microsoft.com</a> · '
        f'<a href="{E(OFFICIAL_SESSIONS)}" rel="noopener">Session catalog</a></dd></div>'
        f'</dl>'
        '<p class="fine">Times converted from Pacific Time with zoneinfo (PST UTC−8, CET UTC+1). '
        'Sources: the <a href="https://www.microsoft.com/en/events" rel="noopener">Microsoft Events</a> page, '
        'the official <a href="https://ignite.microsoft.com/en-US/home" rel="noopener">Ignite homepage</a>, and '
        '<a href="https://www.microsoft.com/en-us/security/blog/2026/09/30/secure-whats-next-your-guide-to-microsoft-security-at-microsoft-ignite-2026/" rel="noopener">Microsoft Security Blog, 30 September 2026</a>. '
        "Microsoft's <a href=\"https://news.microsoft.com/events/ignite/2026/live-news/\" rel=\"noopener\">Ignite live news page</a> (16 November 2026) refers to a Book of News, but no 2026 Book of News URL was public at the time of writing; we link it once it is live.</p>"
    )
    hero = (
        f'<section class="ig-page-hero" aria-labelledby="ig-hub-h">'
        f'<div class="ig-banner-bg" aria-hidden="true">{_blobs()}{_decor()}</div>'
        f'<div class="wrap ig-page-hero-in">'
        + T.crumbs(rel, PATH, [("Home", rel + "index.html"), ("Ignite 2026", None)])
        + f'<p class="ig-kicker"><span class="ig-live" aria-hidden="true"></span>{E(_phase_label())} · San Francisco and online</p>'
        + _wordmark("h1", "ig-hub-h", "Short, source-linked news for tenant admins")
        + f'<p class="ig-page-lead">{E(LEAD)} Opening keynote Tuesday 17 November, {E(KEYNOTE_SE)} ({E(KEYNOTE_PT)}).</p>'
        + _countdown_html()
        + f'<p class="ig-cta"><a class="btn ig-btn" href="{E(OFFICIAL_HOME)}" rel="noopener">Official event site</a>'
        f'<a class="btn ig-btn-2" href="{E(OFFICIAL_SESSIONS)}" rel="noopener">Session catalog</a></p>'
        + '<nav class="ig-area-nav" aria-label="Jump to an area">'
        + "".join(
            f'<a class="ig-area-chip ig-area-{aid}" href="#{aid}">{E(short)}</a>'
            for aid, title, _ in AREAS
            for short in ({
                "copilot": "Copilot & agents",
                "security": "Security",
                "endpoint": "Intune & Windows",
                "collaboration": "Teams & SharePoint",
                "azure": "Azure",
            }[aid],)
        )
        + "</nav>"
        + "</div>" + _countdown_js() + "</section>"
    )
    return (
        hero
        + '<main class="wrap pg"><article class="prose doc ignite-hub">'
        + draft
        + '<div class="ig-hero-panel"><h2>Event at a glance</h2>'
        + facts
        + "</div>"
        + f'<aside class="tl-perm pl-notice" role="note">{T.icon("info")}<span><strong>How we cover Ignite.</strong> {E(guard)}</span></aside>'
        + '<p>This page only lists news items we have written and fact-checked, tagged <code>ignite: true</code> in the news data. '
        "It is not a transcript of the keynote and it is not Microsoft's Book of News.</p>"
        + f'<div class="ai-toc ig-toc" role="navigation" aria-label="Areas"><p class="ps-h">{T.icon("list")}By area</p><ol>{toc}</ol></div>'
        + "".join(sections)
        + f'<p class="ig-cta"><a class="btn ig-btn" href="{E(OFFICIAL_HOME)}" rel="noopener">Official Microsoft Ignite site</a> '
        + f'<a class="btn ig-btn-2" href="{rel}news/index.html">All Tenant Recipes news</a></p>'
        + "</article></main>"
    )


def build(page, SITE_NAME, fmt_date):
    pages = [page(PATH, f"{TITLE} | {SITE_NAME}", LEAD, lambda rel: body(rel, fmt_date))]
    print(f"Ignite hub: {len(ignite_items())} tagged news items, published={PUBLISHED}")
    return pages


def search_docs():
    if not PUBLISHED:
        return []
    return [{"t": "Microsoft Ignite 2026 hub", "k": "Page", "c": "Site", "u": PATH, "s": LEAD,
             "x": "Microsoft Ignite Copilot agents Entra Defender Purview Intune Windows Teams SharePoint Azure"}]
