"""Create a DRAFT of "The Tenant Recipes Weekly Brief" (format: NEWSLETTER.md) with UTM-tagged links to site pages.

Usage:
  python3 tools/newsletter_draft.py --issue 2 [--date 2026-11-09] \
      [--changes news-id,news-id,recipe-id] [--security cyber-id,cyber-id] [--tip recipe-id] [--review recipe-id]

Each id is looked up in published news (data/news), security entries (data/cyber) or recipes (data/recipes.json),
and the item is pre-filled from that page. Anything not given is a TODO(...) placeholder to write by hand.
Writes newsletters/drafts/issue-NNN.md. It never sends anything: KP approves, then it is scheduled in Buttondown."""
import argparse, datetime, json, pathlib, sys
from urllib.parse import urlencode
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import site_config as C

ap = argparse.ArgumentParser()
ap.add_argument("--issue", type=int, required=True)
ap.add_argument("--date", default=datetime.date.today().isoformat())
ap.add_argument("--changes", default="", help="up to 3 ids (news or recipe)")
ap.add_argument("--security", default="", help="up to 2 ids (security entries)")
ap.add_argument("--tip", default="", help="1 recipe id")
ap.add_argument("--review", default="", help="1 recipe id")
ap.add_argument("--recipes", default="", help=argparse.SUPPRESS)  # old flag: treated as --tip/--review
a = ap.parse_args()

site = C.SITE_URL.rstrip("/") or "{SITE_URL}"
campaign = f"issue-{a.issue:03d}"
utm = lambda content: urlencode({"utm_source": C.UTM_SOURCE, "utm_medium": C.UTM_MEDIUM, "utm_campaign": campaign, "utm_content": content})


def published(folder):
    out = {}
    for f in sorted((ROOT / "data" / folder).glob("*.json")):
        e = json.loads(f.read_text())
        if e.get("status") == "published":
            out[e["id"]] = e
    return out


NEWS, CYBER = published("news"), published("cyber")
RECIPES = {r["id"]: r for r in json.load(open(ROOT / "data" / "recipes.json"))}
short = lambda s, n=240: s if len(s) <= n else s[:n - 3].rsplit(" ", 1)[0] + "…"
ids = lambda s: [x.strip() for x in s.split(",") if x.strip()]


def item(i, kind):
    if i in NEWS:
        e = NEWS[i]
        do = e["todo"][0] if e.get("todo") else "TODO(what to do)"
        return f"**{e['title']}**\n{short(e['summary'])}\n**Do:** {do}\n[Details and sources →]({site}/news/{i}.html?{utm(i)})\n"
    if i in CYBER:
        e = CYBER[i]
        act = e.get("action") or "TODO(what to check first)"
        return f"**{e['title']}**\n{short(e['summary'])}\n**Check first:** {short(act, 200)}\n[Details and sources →]({site}/security/{i}.html?{utm(i)})\n"
    if i in RECIPES:
        r = RECIPES[i]
        return f"**{r['title']}**\n{short(r['problem'])}\n[Steps, checks and rollback →]({site}/recipes/{i}.html?{utm(i)})\n"
    sys.exit(f"Unknown or unpublished id ({kind}): {i}")


def section(given, n, kind):
    got = [item(i, kind) for i in ids(given)[:n]]
    got += [f"**TODO({kind} {k + 1})**: headline · one-line why it matters · what to do · source link with UTM\n" for k in range(len(got), n)]
    return "\n".join(f"{k + 1}. {g}" if n > 1 else g for k, g in enumerate(got))


old = ids(a.recipes)
fields = dict(issue=f"{a.issue:03d}", date=a.date,
              changes=section(a.changes, 3, "change"), security=section(a.security, 2, "security"),
              tip=section(a.tip or (old[0] if old else ""), 1, "tip"),
              review=section(a.review or (old[1] if len(old) > 1 else ""), 1, "review"),
              site_url=f"{site}/?" + urlencode({"utm_source": C.UTM_SOURCE, "utm_medium": C.UTM_MEDIUM, "utm_campaign": campaign}))
tpl = (ROOT / "templates" / "newsletter.md").read_text()
out = ROOT / "newsletters" / "drafts" / f"issue-{a.issue:03d}.md"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(tpl.replace("{{ unsubscribe_url }}", "\0").format(**fields).replace("\0", "{{ unsubscribe_url }}"))
print("Draft written:", out.relative_to(ROOT), "" if C.SITE_URL else "(SITE_URL empty: links contain {SITE_URL} placeholder)")
