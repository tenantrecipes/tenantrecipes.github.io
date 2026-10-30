"""Microsoft cloud status page (/status/): an unofficial mirror of Microsoft's public, unauthenticated status sources.
Data comes from data/status.json, written by tools/fetch_status.py in the Pages workflow (on push and every 15 minutes).
assets/status.js re-reads /status/status.json every 2 minutes and shows times in the visitor's time zone."""
import json, pathlib, shutil
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data" / "status.json"
LABEL = {"ok": "Operational", "issue": "Issues reported", "notice": "Advisory", "unknown": "Not reachable"}
OVERALL = {"ok": "All monitored Microsoft cloud sources report no issues", "issue": "Microsoft reports active issues",
           "unknown": "Status sources could not be reached"}


def load():
    return json.loads(DATA.read_text()) if DATA.exists() else None


def pill(rel):
    d = load()
    lv = (d or {}).get("overall", "unknown")
    txt = {"ok": "Microsoft cloud: no reported issues", "issue": "Microsoft cloud: active issues", "unknown": "Microsoft cloud status"}[lv]
    return (f'<a class="st-pill st-{lv}" href="{rel}status/index.html" data-st-pill data-st-json="{rel}status/status.json">'
            f'<span class="st-dot" aria-hidden="true"></span><span class="st-pt">{txt}</span></a>')


def _t(iso):
    return f'<time datetime="{iso}" data-local>{iso.replace("T", " ").replace("Z", " UTC")}</time>' if iso else "—"


def body(rel, esc, E, d):
    notice = (f'<aside class="tl-perm pl-notice" role="note">{T.icon("info")}<span><strong>Unofficial mirror of Microsoft\'s public status sources.</strong> '
              'Your own tenant\'s health is in the Microsoft 365 admin center (Health &gt; Service health), which needs a sign-in. '
              'This page only uses public pages that anyone can open, refreshed about every 15 minutes, and is not affiliated with Microsoft.</span></aside>')
    if not d:
        return notice + '<p>Status has not been fetched yet.</p>'
    cards = ""
    for s in d["sources"]:
        lv = s["level"] if s["reachable"] else "unknown"
        st = esc(s["status"] or "") if s["reachable"] else f'Could not be reached from our checker{": " + esc(s["error"]) if s.get("error") else ""}'
        svc = ""
        if s.get("services"):
            svc = '<ul class="st-svc">' + "".join(f'<li class="st-{x["level"]}"><span class="st-dot"></span>{esc(x["name"])}: {esc(x["status"])}</li>' for x in s["services"]) + '</ul>'
        msg = f'<p class="st-msg">{esc(s["message"])}</p>' if s.get("message") and lv != "ok" else ""
        cards += (f'<article class="st-card st-{lv}" data-k="{s["key"]}"><div class="st-h"><span class="st-dot" aria-hidden="true"></span><h3>{esc(s["name"])}</h3>'
                  f'<span class="st-lab">{LABEL[lv]}</span></div><p class="st-s">{st}</p>{msg}{svc}'
                  f'<p class="st-f">Updated {_t(s.get("updated"))} · <a href="{E(s["official"])}" rel="noopener">Official source</a> · <code>{esc(s["endpoint"])}</code></p></article>')
    act = "".join(f'<li><strong><a href="{E(i["link"])}" rel="noopener">{esc(i["title"])}</a></strong><span>{esc(i["source_name"])} · started {_t(i.get("start"))}'
                  + (f' · {esc(", ".join(i["services"]))}' if i.get("services") else "") + f'</span><p>{esc(i.get("summary") or "")}</p></li>' for i in d["active"])
    hist = "".join(f'<li><a href="{E(h["link"])}" rel="noopener">{esc(h["title"])}</a> <span class="fine">{esc(h["source"])} · first seen {_t(h.get("first_seen"))} · last seen {_t(h.get("last_seen"))}</span></li>' for h in d["history"])
    return (notice
            + f'<section class="st-over st-{d["overall"]}" id="st-over"><span class="st-dot" aria-hidden="true"></span><div><strong id="st-ot">{OVERALL[d["overall"]]}</strong>'
            f'<p class="fine">Last checked {_t(d["generated"])} · <span id="st-ref">refreshes automatically</span></p></div></section>'
            f'<h2 id="active">Active incidents</h2><div id="st-act">' + (f'<ol class="st-inc">{act}</ol>' if act else '<p>No active incidents in the public sources right now.</p>') + '</div>'
            f'<h2 id="sources">Sources</h2><div class="st-grid" id="st-cards">{cards}</div>'
            '<h2 id="history">Last 30 days</h2>' + (f'<ul class="st-hist">{hist}</ul>' if hist else '<p>No incidents recorded by this mirror in the last 30 days.</p>')
            + '<h2 id="not-covered">What this page cannot show</h2><ul>'
            '<li>Microsoft 365 enterprise service health (Exchange Online, Teams, SharePoint for your tenant) is only available signed in, in the admin center or through the Service Communications API. We do not use it.</li>'
            '<li>Azure resource-specific health for your subscriptions is in Azure Service Health in the Azure portal.</li>'
            '<li>The Microsoft 365 and Power Platform admin center entries above are fallback notices Microsoft uses when the admin center itself has problems.</li></ul>')


def build(page, esc, E, SITE_NAME, DIST):
    d = load()

    def b(rel):
        return (T.page_hero(rel, T.crumbs_dark(rel, "status/index.html", [("Home", rel + "index.html"), ("Microsoft cloud status", None)]),
                            f'{T.icon("clock")}Status', "Microsoft cloud status",
                            "Azure, Microsoft 365 admin center, Power Platform admin center, Microsoft 365 consumer services and Azure DevOps, from Microsoft's public status sources.", kind="page")
                + f'<main class="wrap pg"><article class="prose doc" id="st-root" data-st-json="{rel}status/status.json">{body(rel, esc, E, d)}</article></main>'
                + f'<script src="{rel}assets/status.js" defer></script>')
    p = page("status/index.html", f"Microsoft cloud status (unofficial mirror) | {SITE_NAME}",
             "Unofficial mirror of Microsoft's public status sources for Azure, Microsoft 365 and Power Platform, with active incidents and a 30-day history.", b)
    if d:
        (DIST / "status").mkdir(exist_ok=True)
        shutil.copy(DATA, DIST / "status" / "status.json")
    print(f"Status page: {'overall ' + d['overall'] + ', generated ' + d['generated'] if d else 'no data yet'}")
    return [p]
