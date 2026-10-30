"""Create a newsletter DRAFT whose recipe section is short teasers linking to the full recipe pages (with UTM tags).
Usage: python3 tools/newsletter_draft.py --issue 2 --recipes ca-break-glass,purview-audit-copilot [--date 2026-11-03]
Writes newsletters/drafts/issue-002.md. It never sends anything: KP reviews and sends from Buttondown."""
import argparse, datetime, json, pathlib, sys
from urllib.parse import urlencode
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import site_config as C

ap = argparse.ArgumentParser()
ap.add_argument("--issue", type=int, required=True)
ap.add_argument("--recipes", required=True, help="comma-separated recipe ids")
ap.add_argument("--date", default=datetime.date.today().isoformat())
a = ap.parse_args()

R = {r["id"]: r for r in json.load(open(ROOT / "data" / "recipes.json"))}
site = C.SITE_URL.rstrip("/") or "{SITE_URL}"
campaign = f"issue-{a.issue:03d}"
teasers = []
for rid in [x.strip() for x in a.recipes.split(",") if x.strip()]:
    if rid not in R:
        sys.exit(f"Unknown or unpublished recipe id: {rid}")
    r = R[rid]
    q = urlencode({"utm_source": C.UTM_SOURCE, "utm_medium": C.UTM_MEDIUM, "utm_campaign": campaign, "utm_content": rid})
    teaser = r["problem"] if len(r["problem"]) <= 220 else r["problem"][:217].rsplit(" ", 1)[0] + "…"
    teasers.append(f"### {r['title']}\n{teaser}\n[Read the full recipe →]({site}/recipes/{rid}.html?{q})\n")

tpl = (ROOT / "templates" / "newsletter.md").read_text()
fields = dict(issue=f"{a.issue:03d}", date=a.date, recipe_teasers="\n".join(teasers),
              site_url=f"{site}/?" + urlencode({"utm_source": C.UTM_SOURCE, "utm_medium": C.UTM_MEDIUM, "utm_campaign": campaign}))
for k in ("top_story_title", "top_story_teaser", "admin_take", "top_story_source", "copilot_item", "intune_item", "entra_purview_item"):
    fields[k] = f"TODO({k})"
out = ROOT / "newsletters" / "drafts" / f"issue-{a.issue:03d}.md"
out.write_text(tpl.replace("{{ unsubscribe_url }}", "\0").format(**fields).replace("\0", "{{ unsubscribe_url }}"))
print("Draft written:", out.relative_to(ROOT), "" if C.SITE_URL else "(SITE_URL empty: links contain {SITE_URL} placeholder)")
