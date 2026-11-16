#!/usr/bin/env python3
"""No-LLM hourly feed collector for Tenant Recipes' Microsoft Ignite coverage.

Reads RSS/Atom feeds, deduplicates into /workspace/m365ai-ignite/inbox.jsonl,
and writes /workspace/m365ai-ignite/new-since-last-read.md for items not yet
marked read. No model calls. Safe to run from cron or the companion loop.

Usage:
  python3 scripts/ignite_collect.py              # fetch and update inbox
  python3 scripts/ignite_collect.py --mark-read  # mark current unread items read
  python3 scripts/ignite_collect.py --status     # print feed health and counts
"""
from __future__ import annotations

import argparse, hashlib, html, json, os, re, sys, time, urllib.error, urllib.request, ssl
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from zoneinfo import ZoneInfo

try:
    import defusedxml.ElementTree as ET
except ImportError:  # pragma: no cover — defusedxml is installed on the box
    import xml.etree.ElementTree as ET  # nosec B405

STOCKHOLM = ZoneInfo("Europe/Stockholm")
UTC = timezone.utc

# Inbox lives outside the site repo so a site publish cannot ship it.
DATA_DIR = Path(os.environ.get("TR_IGNITE_DIR", "/workspace/m365ai-ignite")).resolve()
INBOX = DATA_DIR / "inbox.jsonl"
STATE = DATA_DIR / "state.json"
READ = DATA_DIR / "read.json"
NEW_MD = DATA_DIR / "new-since-last-read.md"
LOG = DATA_DIR / "collect.log"

# A browser-like UA is required: blogs.microsoft.com and news.microsoft.com/source
# return 403 to a custom collector UA (verified 2026-11-16). This is fetch-only.
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)
TIMEOUT = 25
RETRIES = 1
LOOKBACK_DAYS = 21
SUMMARY_CHARS = 300
# Roadmap RSS is huge; keep a shorter window so the first inbox is usable.
ROADMAP_LOOKBACK_DAYS = 10

# official=True: keep every in-window item. official=False: keyword filter.
# Dead or blocked feeds are omitted (documented in drafts/ignite-hub-README.md).
FEEDS = [
    # Microsoft official blogs / newsroom
    ("ms-official-blog", "The Official Microsoft Blog", "https://blogs.microsoft.com/feed/", True),
    ("ms-source", "Microsoft Source", "https://news.microsoft.com/source/feed/", True),
    ("ms-copilot-blog", "Microsoft Copilot Blog", "https://www.microsoft.com/en-us/copilot/blog/feed/", True),
    ("ms-security-blog", "Microsoft Security Blog", "https://www.microsoft.com/en-us/security/blog/feed/", True),
    ("ms-azure-blog", "Microsoft Azure Blog", "https://azure.microsoft.com/en-us/blog/feed/", True),
    ("m365-roadmap", "Microsoft 365 Roadmap", "https://www.microsoft.com/releasecommunications/api/v2/m365/rss", True),
    # Tech Community (Aurora-era board RSS)
    ("tc-entra", "Microsoft Entra Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=microsoft-entra-blog", True),
    ("tc-intune", "Microsoft Intune Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=microsoftintuneblog", True),
    ("tc-intune-cs", "Intune Customer Success", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=IntuneCustomerSuccess", True),
    ("tc-m365", "Microsoft 365 Blog (Tech Community)", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=microsoft_365blog", True),
    ("tc-copilot", "Microsoft Copilot Blog (Tech Community)", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=microsoft-copilot-blog", True),
    ("tc-winitpro", "Windows IT Pro Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=Windows-ITPro-blog", True),
    ("tc-teams", "Microsoft Teams Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=MicrosoftTeamsBlog", True),
    ("tc-exchange", "Exchange Team Blog", "https://techcommunity.microsoft.com/t5/s/gxcuf89792/rss/board?board.id=exchange", True),
    # YouTube (channel IDs verified from each channel's canonical URL, 2026-11-16)
    ("yt-microsoft", "YouTube: Microsoft", "https://www.youtube.com/feeds/videos.xml?channel_id=UCFtEEv80fQVKkD4h1PF-Xqw", True),
    ("yt-mechanics", "YouTube: Microsoft Mechanics", "https://www.youtube.com/feeds/videos.xml?channel_id=UCJ9905MRHxwLZ2jeNQGIWxA", True),
    ("yt-developer", "YouTube: Microsoft Developer", "https://www.youtube.com/feeds/videos.xml?channel_id=UCsMica-v34Irf9KVTh6xx-g", True),
    ("yt-security", "YouTube: Microsoft Security", "https://www.youtube.com/feeds/videos.xml?channel_id=UC4s3tv0Qq_OSUBfR735Jc6A", True),
    ("yt-azure", "YouTube: Microsoft Azure", "https://www.youtube.com/feeds/videos.xml?channel_id=UC0m-80FnNY2Qb7obvTL_2fA", True),
    # Independent / other vendors
    ("theregister", "The Register", "https://www.theregister.com/headlines.atom", False),
    ("bleepingcomputer", "BleepingComputer", "https://www.bleepingcomputer.com/feed/", False),
    ("cisa-news", "CISA News", "https://www.cisa.gov/news.xml", False),
    ("google-workspace", "Google Workspace Blog", "https://blog.google/products-and-platforms/products/workspace/rss/", False),
    ("openai-news", "OpenAI News", "https://openai.com/news/rss.xml", False),
]

RELEVANT = re.compile(
    r"\b(ignite|msignite|copilot|entra|intune|defender|purview|teams|"
    r"sharepoint|onedrive|exchange|outlook|windows|azure|agent|agents?|"
    r"agentic|security|cybersecurity|cisa|cve|vulnerability|microsoft|"
    r"m365|microsoft 365|copilot studio|conditional access|passkey|"
    r"entra id|graph api|sentinel|kev|cowork|foundry|fabric|"
    r"\bai\b|gemini|workspace|chatgpt|claude|openai|llm|gpt)\b",
    re.I,
)

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ocid", "wt.mc_id", "WT.mc_id", "clid", "fbclid", "gclid", "mc_cid", "mc_eid",
}

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}


def now_sthlm() -> datetime:
    return datetime.now(STOCKHOLM)


def iso_now() -> str:
    return now_sthlm().isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"{iso_now()} {msg}"
    print(line, flush=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower() if tag else ""


def text_of(el, *names) -> str:
    if el is None:
        return ""
    want = {n.lower() for n in names}
    if localname(el.tag) in want and (el.text or "").strip():
        return "".join(el.itertext()).strip()
    for child in list(el):
        if localname(child.tag) in want:
            return "".join(child.itertext()).strip()
    return ""


def child(el, *names):
    want = {n.lower() for n in names}
    for c in list(el):
        if localname(c.tag) in want:
            return c
    return None


def strip_html(raw: str) -> str:
    if not raw:
        return ""
    t = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", raw)
    t = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", t)
    t = re.sub(r"(?is)<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def trim_summary(raw: str, n: int = SUMMARY_CHARS) -> str:
    t = strip_html(raw)
    if len(t) <= n:
        return t
    cut = t[: n - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(",;:—-") + "…"


def normalize_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    try:
        parts = urlsplit(url)
    except ValueError:
        return url
    scheme = (parts.scheme or "https").lower()
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parts.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    q = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True) if k not in TRACKING_PARAMS]
    query = urlencode(q, doseq=True)
    return urlunsplit((scheme, netloc, path, query, ""))  # drop fragment


def parse_when(value: str) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (TypeError, ValueError, OverflowError):
        return None


def item_key(url: str, guid: str) -> str:
    base = normalize_url(url) or guid or ""
    return base.casefold() or hashlib.sha256((url + "|" + guid).encode()).hexdigest()


def fetch(url: str) -> tuple[int, str, bytes]:
    last_err = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": UA,
                    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            )
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
                return resp.status, resp.geturl(), resp.read(8_000_000)
        except Exception as e:  # noqa: BLE001 — we record the error per feed
            last_err = e
            if attempt < RETRIES:
                time.sleep(1.5)
    raise last_err


def iter_entries(root) -> list:
    out = []
    # RSS channel/item or Atom feed/entry, regardless of namespace
    for el in root.iter():
        if localname(el.tag) in {"item", "entry"}:
            out.append(el)
    return out


def entry_url(el) -> str:
    # Atom: link[@rel=alternate] or first link href; RSS: link text or guid[@isPermaLink=true]
    links = [c for c in list(el) if localname(c.tag) == "link"]
    alt = None
    for ln in links:
        href = (ln.get("href") or "").strip()
        rel = (ln.get("rel") or "alternate").lower()
        typ = (ln.get("type") or "").lower()
        if href and rel in {"alternate", ""} and "xml" not in typ:
            alt = href
            break
        if href and not alt:
            alt = href
    if alt:
        return alt
    for ln in links:
        t = "".join(ln.itertext()).strip()
        if t.startswith("http"):
            return t
    guid = child(el, "guid", "id")
    if guid is not None:
        permalink = (guid.get("isPermaLink") or "true").lower()
        t = "".join(guid.itertext()).strip()
        if t.startswith("http") and permalink != "false":
            return t
    return ""


def entry_guid(el) -> str:
    g = child(el, "guid", "id")
    if g is not None:
        return "".join(g.itertext()).strip()
    return ""


def entry_title(el) -> str:
    return strip_html(text_of(el, "title")) or "(untitled)"


def entry_summary(el) -> str:
    for name in ("summary", "description", "content", "encoded"):
        raw = text_of(el, name)
        if raw:
            return trim_summary(raw)
    # YouTube media:description
    for c in el.iter():
        if localname(c.tag) == "description" and (c.text or "").strip():
            return trim_summary(c.text)
    return ""


def entry_published(el) -> str:
    for name in ("published", "pubdate", "updated", "date", "created"):
        raw = text_of(el, name)
        dt = parse_when(raw)
        if dt:
            return dt.astimezone(STOCKHOLM).isoformat(timespec="seconds")
    # dc:date etc. already covered by localname 'date'
    return ""


def parse_feed(data: bytes, source_id: str, source_name: str, official: bool, cutoff: datetime) -> list[dict]:
    # Some feeds include a UTF-8 BOM or leading whitespace
    payload = data.lstrip(b"\xef\xbb\xbf \t\r\n")
    if payload.lower().lstrip().startswith(b"<html"):
        raise ValueError("HTML body instead of a feed")
    root = ET.fromstring(payload)
    items = []
    seen_here = set()
    for el in iter_entries(root):
        url = entry_url(el)
        guid = entry_guid(el)
        title = entry_title(el)
        published = entry_published(el)
        summary = entry_summary(el)
        key = item_key(url, guid)
        if not key or key in seen_here:
            continue
        if published:
            dt = parse_when(published)
            if dt and dt < cutoff:
                continue
        elif source_id == "m365-roadmap":
            # Roadmap items without a date would flood the inbox
            continue
        blob = f"{title} {summary} {url}"
        if not official and not RELEVANT.search(blob):
            continue
        seen_here.add(key)
        items.append({
            "source": source_id,
            "source_name": source_name,
            "title": title,
            "url": url or guid,
            "guid": guid,
            "published": published,
            "summary": summary,
            "key": key,
        })
    return items


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def load_inbox() -> list[dict]:
    if not INBOX.exists():
        return []
    out = []
    for line in INBOX.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def append_inbox(rows: list[dict]) -> None:
    if not rows:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with INBOX.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_new_md(unread: list[dict], marked: bool = False) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# New since last read",
        "",
        f"Generated: {iso_now()} (Europe/Stockholm).",
        "",
    ]
    if marked:
        lines += ["All previously listed items were marked read.", ""]
        NEW_MD.write_text("\n".join(lines), encoding="utf-8")
        return
    if not unread:
        lines += ["No unread items.", ""]
        NEW_MD.write_text("\n".join(lines), encoding="utf-8")
        return
    lines.append(f"{len(unread)} unread item(s). Run `python3 scripts/ignite_collect.py --mark-read` after reviewing.")
    lines.append("")
    # newest first
    def sort_key(r):
        return r.get("published") or r.get("seen_at") or ""

    groups = {}
    for r in sorted(unread, key=sort_key, reverse=True):
        groups.setdefault(r.get("source_name") or r.get("source") or "Other", []).append(r)
    for src, rows in groups.items():
        lines.append(f"## {src}")
        lines.append("")
        for r in rows:
            when = r.get("published") or "date unknown"
            # show Stockholm date if parseable
            dt = parse_when(when) if when != "date unknown" else None
            when_s = dt.strftime("%Y-%m-%d %H:%M") if dt else when
            lines.append(f"- **{r.get('title', '(untitled)')}**")
            lines.append(f"  - {when_s} · {r.get('url', '')}")
            if r.get("summary"):
                lines.append(f"  - {r['summary']}")
            lines.append("")
    NEW_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def collect() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    state = load_json(STATE, {"seen": {}, "feeds": {}, "last_run": None})
    seen = state.get("seen") or {}
    existing = {r.get("key") for r in load_inbox() if r.get("key")}
    # keys already in inbox count as seen
    for k in existing:
        seen.setdefault(k, True)

    cutoff_default = now_sthlm() - timedelta(days=LOOKBACK_DAYS)
    cutoff_roadmap = now_sthlm() - timedelta(days=ROADMAP_LOOKBACK_DAYS)
    new_rows = []
    feed_report = {}
    fetched = 0
    kept = 0
    errors = 0

    for fid, name, url, official in FEEDS:
        cutoff = cutoff_roadmap if fid == "m365-roadmap" else cutoff_default
        t0 = time.time()
        try:
            status, final, data = fetch(url)
            items = parse_feed(data, fid, name, official, cutoff)
            fresh = []
            for it in items:
                kept += 1
                if it["key"] in seen or it["key"] in existing:
                    continue
                row = {
                    "source": it["source"],
                    "title": it["title"],
                    "url": it["url"],
                    "published": it["published"],
                    "summary": it["summary"],
                    "seen_at": iso_now(),
                    "source_name": it["source_name"],
                    "guid": it["guid"],
                    "key": it["key"],
                }
                fresh.append(row)
                seen[it["key"]] = row["seen_at"]
            append_inbox(fresh)
            new_rows.extend(fresh)
            fetched += 1
            feed_report[fid] = {
                "ok": True,
                "name": name,
                "status": status,
                "url": url,
                "final_url": final,
                "entries_in_window": len(items),
                "new": len(fresh),
                "seconds": round(time.time() - t0, 2),
                "error": None,
                "fetched_at": iso_now(),
            }
            log(f"OK {fid}: {len(items)} in window, {len(fresh)} new")
        except Exception as e:  # noqa: BLE001
            errors += 1
            feed_report[fid] = {
                "ok": False,
                "name": name,
                "status": None,
                "url": url,
                "final_url": None,
                "entries_in_window": 0,
                "new": 0,
                "seconds": round(time.time() - t0, 2),
                "error": f"{type(e).__name__}: {e}",
                "fetched_at": iso_now(),
            }
            log(f"FAIL {fid}: {type(e).__name__}: {e}")

    state["seen"] = seen
    state["feeds"] = feed_report
    state["last_run"] = iso_now()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    unread = unread_items()
    write_new_md(unread)
    summary = {
        "feeds_ok": fetched,
        "feeds_failed": errors,
        "feeds_total": len(FEEDS),
        "entries_kept_in_window": kept,
        "new_this_run": len(new_rows),
        "inbox_total": len(load_inbox()),
        "unread": len(unread),
        "new_md": str(NEW_MD),
        "inbox": str(INBOX),
    }
    log(
        f"DONE ok={fetched}/{len(FEEDS)} failed={errors} "
        f"new={len(new_rows)} inbox={summary['inbox_total']} unread={summary['unread']}"
    )
    return summary


def unread_items() -> list[dict]:
    read = set(load_json(READ, {"keys": []}).get("keys") or [])
    return [r for r in load_inbox() if r.get("key") and r["key"] not in read]


def mark_read() -> int:
    unread = unread_items()
    data = load_json(READ, {"keys": [], "history": []})
    keys = set(data.get("keys") or [])
    for r in unread:
        keys.add(r["key"])
    data["keys"] = sorted(keys)
    data["history"] = (data.get("history") or [])[-20:] + [{"at": iso_now(), "marked": len(unread)}]
    READ.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_new_md([], marked=True)
    log(f"MARK-READ {len(unread)} items")
    return len(unread)


def status() -> None:
    state = load_json(STATE, {})
    inbox = load_inbox()
    unread = unread_items()
    print(f"inbox: {len(inbox)}  unread: {len(unread)}  last_run: {state.get('last_run')}")
    for fid, info in (state.get("feeds") or {}).items():
        flag = "OK " if info.get("ok") else "ERR"
        extra = f"n={info.get('entries_in_window', 0)} new={info.get('new', 0)}" if info.get("ok") else info.get("error")
        print(f"  {flag} {fid:16} {extra}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Collect Ignite-relevant RSS/Atom items (no LLM).")
    p.add_argument("--mark-read", action="store_true", help="Mark all currently unread inbox items as read and clear new-since-last-read.md")
    p.add_argument("--status", action="store_true", help="Print last-run feed health and counts")
    p.add_argument("--lookback-days", type=int, default=None, help="Override lookback window (default 14)")
    args = p.parse_args(argv)
    if args.lookback_days:
        global LOOKBACK_DAYS
        LOOKBACK_DAYS = args.lookback_days
    if args.mark_read:
        n = mark_read()
        print(f"Marked {n} item(s) read. {NEW_MD} cleared.")
        return 0
    if args.status:
        status()
        return 0
    summary = collect()
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["feeds_failed"] < summary["feeds_total"] else 1


if __name__ == "__main__":
    sys.exit(main())
