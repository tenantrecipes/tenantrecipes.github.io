"""One-off migration (2026-10-30): split the old monolithic build_data.py list into one JSON file per recipe.
Reads the v1 data from data/recipes.json (produced by the old build_data.py) and writes data/recipes/<id>.json."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
R = json.load(open(root / "data/recipes.json"))
out = root / "data/recipes"; out.mkdir(exist_ok=True)
for i, r in enumerate(R):
    rec = {
        "id": r["id"],
        "status": "published",
        "order": (i + 1) * 10,
        "category": r["category"],
        "title": r["title"].strip(),
        "problem": r["problem"],
        "steps": r["steps"],
        "pitfalls": r["pitfalls"],
        "sources": [{"title": l["title"], "url": l["url"], "checked": None} for l in r["links"]],
        "last_verified": None,
        "verified_by": None,
        "created": "2026-10-12",
        "updated": "2026-10-12",
    }
    (out / f"{r['id']}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n")
print(len(R), "recipes written to", out)
