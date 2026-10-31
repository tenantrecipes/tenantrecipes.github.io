"""Build the recipe dataset from one JSON file per recipe.

Add a recipe: drop data/recipes/<id>.json (see RECIPES.md for the schema), then run `python3 build.py`.
Outputs: data/recipes.json (all published recipes) and data/recipes.js (used by the search page).
Exits non-zero if any recipe file is invalid, so an automated pipeline stops before deploying.
"""
import json, re, sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import site_config as C
import build_markers as MK

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "data" / "recipes"
REQUIRED = ["id", "status", "tier", "category", "title", "problem", "steps", "pitfalls", "sources", "last_verified"]
STATUSES = {"published", "draft", "needs-review", "retired"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate(r, fname):
    errs = []
    for k in REQUIRED:
        if k not in r:
            errs.append(f"missing field '{k}'")
    if errs:
        return errs
    if r["id"] + ".json" != fname:
        errs.append(f"id '{r['id']}' must match file name")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", r["id"]):
        errs.append("id must be lowercase-kebab-case")
    if r["tier"] != "recipe":
        errs.append("'tier' must be \"recipe\" for files in data/recipes/ (pillar/technical guides live in data/guides/, see GUIDES.md)")
    if r["status"] not in STATUSES:
        errs.append(f"status must be one of {sorted(STATUSES)}")
    for k in ("title", "problem", "category"):
        if not isinstance(r[k], str) or not r[k].strip():
            errs.append(f"'{k}' must be a non-empty string")
    if not r["steps"] or not all(isinstance(s, str) and s.strip() for s in r["steps"]):
        errs.append("'steps' must be a non-empty list of strings")
    if not isinstance(r["pitfalls"], list):
        errs.append("'pitfalls' must be a list")
    if not r["sources"]:
        errs.append("at least one source is required")
    for s in r["sources"]:
        if not s.get("title") or not str(s.get("url", "")).startswith("https://"):
            errs.append(f"source needs title and https url: {s}")
        if s.get("checked") is not None and not DATE.match(str(s["checked"])):
            errs.append(f"source 'checked' must be YYYY-MM-DD or null: {s}")
    if "done_when" in r and (not isinstance(r["done_when"], list) or not all(isinstance(x, str) and x.strip() for x in r["done_when"])):
        errs.append("'done_when' must be a list of non-empty strings")
    for sh in r.get("screenshots") or []:  # optional REAL screenshots only: {src, alt, caption, date}
        if not all(sh.get(k) for k in ("src", "alt", "caption", "date")) or not DATE.match(str(sh.get("date"))):
            errs.append(f"screenshot needs src, alt, caption and date (YYYY-MM-DD): {sh}")
        elif not (str(sh["src"]).startswith("assets/screenshots/") and (ROOT / sh["src"]).exists()):
            errs.append(f"screenshot file must live under assets/screenshots/ and exist: {sh['src']}")
    if r["last_verified"] is not None and not DATE.match(str(r["last_verified"])):
        errs.append("'last_verified' must be YYYY-MM-DD or null")
    for h in r.get("history") or []:  # optional per-page version notes
        if not (isinstance(h, dict) and DATE.match(str(h.get("date"))) and isinstance(h.get("note"), str) and h["note"].strip()):
            errs.append(f"history items need date (YYYY-MM-DD) and note: {h}")
    errs += MK.validate(r)  # markers, notes, tested, troubleshooting, rollback (all optional)
    return errs


def load(include_drafts=False):
    recipes, problems = [], []
    for f in sorted(SRC.glob("*.json")):
        try:
            r = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{f.name}: invalid JSON ({e})"); continue
        for e in validate(r, f.name):
            problems.append(f"{f.name}: {e}")
        recipes.append(r)
    if problems:
        print("Recipe validation failed:\n  " + "\n  ".join(problems), file=sys.stderr)
        sys.exit(1)
    ids = [r["id"] for r in recipes]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        sys.exit(f"Duplicate ids: {dupes}")
    keep = [r for r in recipes if r["status"] == "published" or (include_drafts and r["status"] != "retired")]
    order = {c: i for i, c in enumerate(C.CATEGORY_ORDER)}
    keep.sort(key=lambda r: (order.get(r["category"], 999), r["category"], r.get("order", 10**6), r["id"]))
    return keep


def main():
    R = load()
    (ROOT / "data" / "recipes.json").write_text(json.dumps(R, indent=1, ensure_ascii=False))
    # Slim copy for the client-side search
    import build_ux
    (ROOT / "data" / "recipes.js").write_text(build_ux.slim_js(R))  # includes derived topic tags for the homepage filter
    unverified = sum(1 for r in R if not r["last_verified"])
    no_dw = [r["id"] for r in R if not r.get("done_when")]
    print(f"{len(R)} published recipes ({unverified} not yet verified)"
          + (f"  WARNING: no done_when in {', '.join(no_dw)}" if no_dw else ""))


if __name__ == "__main__":
    main()
