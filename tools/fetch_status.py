"""Fetch Microsoft's PUBLIC, unauthenticated status sources and write data/status.json (+ 30-day history).

No authenticated APIs (no Microsoft Graph / Service Health). If a source cannot be reached, it is reported as
unreachable on the page instead of guessing. Used by the Pages workflow before every build (push and the
15-minute schedule). Prints `changed=true|false` (state fingerprint vs. the deployed copy) for the workflow."""
import json, re, sys, html, hashlib, pathlib, datetime, urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "status.json"
HIST = ROOT / "data" / "status-history.json"
UA = {"User-Agent": "TenantRecipesStatusMirror/1.0 (+https://tenantrecipes.com/status/)"}
OK = {"available", "operational", "healthy", "ok", "none"}
NOW = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def get(url, timeout=20):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def text(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h or ""))).strip()


def iso(s):
    if not s:
        return None
    try:
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return None if d.year < 2000 else d.astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except ValueError:
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(s).astimezone(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        except Exception:
            return None


def level(st):
    return "ok" if (st or "").strip().lower() in OK else "issue"


def src(key, name, official, endpoint, fn):
    s = {"key": key, "name": name, "official": official, "endpoint": endpoint, "reachable": False, "level": "unknown",
         "status": None, "message": None, "updated": None, "incidents": [], "error": None}
    try:
        fn(s)
        s["reachable"] = True
    except Exception as e:  # report, never fake
        s["error"] = f"{type(e).__name__}: {str(e)[:160]}"
    return s


def azure_post(s):
    code, body = get("https://status.cloud.microsoft/api/posts/azure")
    d = json.loads(body)
    s.update(status=d.get("Status"), level=level(d.get("Status")), message=text(d.get("Message")), updated=iso(d.get("LastUpdatedTime")))


def azure_rss(s):
    code, body = get("https://azure.status.microsoft/en-us/status/feed/")
    ch = ET.fromstring(body).find("channel")
    for it in ch.findall("item"):
        s["incidents"].append({"id": "azure-" + hashlib.sha1((it.findtext("guid") or it.findtext("title") or "").encode()).hexdigest()[:12],
                               "title": text(it.findtext("title")), "summary": text(it.findtext("description"))[:600],
                               "start": iso(it.findtext("pubDate")), "link": it.findtext("link") or "https://azure.status.microsoft/en-us/status/"})
    s["status"] = "Active incidents" if s["incidents"] else "No incidents in feed"
    s["level"] = "issue" if s["incidents"] else "ok"
    s["updated"] = iso(ch.findtext("lastBuildDate"))


def portal_post(path):
    def fn(s):
        code, body = get(f"https://status.cloud.microsoft/api/posts/{path}")
        d = json.loads(body)
        st = d.get("Status")
        s.update(status=st, level=level(st), message=text(d.get("Message"))[:600], updated=iso(d.get("LastUpdatedTime")))
        if level(st) != "ok":
            s["incidents"].append({"id": f"{path}-" + (d.get("Id") or hashlib.sha1((d.get("Title") or st).encode()).hexdigest()[:12]),
                                   "title": text(d.get("Title")) or f'{s["name"]}: {st}', "summary": s["message"],
                                   "start": iso(d.get("AuthoredDateTime")), "link": s["official"]})
    return fn


def consumer(s):
    code, body = get("https://status.cloud.microsoft/api/posts/m365Consumer")
    rows = json.loads(body)
    s["services"] = [{"name": r.get("ServiceDisplayName"), "status": r.get("Status"), "level": level(r.get("Status"))} for r in rows]
    bad = [r for r in rows if level(r.get("Status")) != "ok"]
    for r in bad:
        s["incidents"].append({"id": "consumer-" + (r.get("Id") or r.get("ServiceWorkloadName") or "x"), "title": text(r.get("Title")) or f'{r.get("ServiceDisplayName")}: {r.get("Status")}',
                               "summary": text(r.get("Message"))[:600], "start": iso(r.get("AuthoredDateTime")), "link": s["official"],
                               "services": [r.get("ServiceDisplayName")]})
    s["status"] = f"{len(rows) - len(bad)} of {len(rows)} services operational"
    s["level"] = "issue" if bad else "ok"
    s["updated"] = max([iso(r.get("LastUpdatedTime")) or "" for r in rows] or [None]) or None


def devops(s):
    code, body = get("https://status.dev.azure.com/_apis/status/health?api-version=7.1-preview.1")
    d = json.loads(body)
    h = (d.get("status") or {}).get("health")
    s.update(status=(d.get("status") or {}).get("message") or h, level="ok" if h == "healthy" else ("issue" if h in ("unhealthy", "degraded") else "notice"),
             updated=iso(d.get("lastUpdated")))


def main():
    sources = [
        src("azure", "Azure", "https://azure.status.microsoft/en-us/status/", "status.cloud.microsoft/api/posts/azure", azure_post),
        src("azure-feed", "Azure status feed (incidents)", "https://azure.status.microsoft/en-us/status/", "azure.status.microsoft/en-us/status/feed/", azure_rss),
        src("m365-admin", "Microsoft 365 admin center", "https://status.cloud.microsoft/", "status.cloud.microsoft/api/posts/mac", portal_post("mac")),
        src("ppac", "Power Platform admin center", "https://status.cloud.microsoft/", "status.cloud.microsoft/api/posts/ppac", portal_post("ppac")),
        src("m365-consumer", "Microsoft 365 consumer services", "https://status.cloud.microsoft/", "status.cloud.microsoft/api/posts/m365Consumer", consumer),
        src("azure-devops", "Azure DevOps", "https://status.dev.azure.com/", "status.dev.azure.com/_apis/status/health", devops),
    ]
    active = [dict(i, source=s["key"], source_name=s["name"]) for s in sources for i in s["incidents"]]
    hist = json.loads(HIST.read_text()) if HIST.exists() else []
    known = {h["id"]: h for h in hist}
    for i in active:
        h = known.get(i["id"]) or {"id": i["id"], "first_seen": NOW.isoformat().replace("+00:00", "Z")}
        h.update(title=i["title"], source=i["source_name"], link=i["link"], start=i.get("start"), last_seen=NOW.isoformat().replace("+00:00", "Z"))
        known[i["id"]] = h
    cutoff = (NOW - datetime.timedelta(days=30)).isoformat()
    hist = sorted([h for h in known.values() if (h.get("last_seen") or "") >= cutoff[:19]], key=lambda h: h.get("last_seen", ""), reverse=True)
    reach = [s for s in sources if s["reachable"]]
    overall = "unknown" if not reach else ("issue" if any(s["level"] == "issue" for s in reach) else "ok")
    state = {"generated": NOW.isoformat().replace("+00:00", "Z"), "overall": overall, "sources": sources, "active": active,
             "history": hist[:100]}
    fp = hashlib.sha256(json.dumps([[s["key"], s["reachable"], s["level"], s["status"], [i["id"] for i in s["incidents"]]] for s in sources]).encode()).hexdigest()[:16]
    state["fingerprint"] = fp
    OUT.write_text(json.dumps(state, indent=1, ensure_ascii=False) + "\n")
    hist_changed = json.dumps(hist[:100], sort_keys=True) != (json.dumps(json.loads(HIST.read_text()), sort_keys=True) if HIST.exists() else "[]")
    if hist_changed or not HIST.exists():
        HIST.write_text(json.dumps(hist[:100], indent=1, ensure_ascii=False) + "\n")
    deployed = None
    try:
        deployed = json.loads(get("https://tenantrecipes.com/status/status.json", 15)[1]).get("fingerprint")
    except Exception:
        pass
    print(f"overall={overall} reachable={len(reach)}/{len(sources)} active={len(active)} fingerprint={fp} deployed={deployed}")
    print(f"changed={'true' if fp != deployed else 'false'}")
    print(f"history_changed={'true' if hist_changed else 'false'}")


if __name__ == "__main__":
    main()
