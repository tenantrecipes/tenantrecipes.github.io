# IT link hub (`/links/`) and AI department (`/links/ai/`)

Vendor-neutral curated directories for day-to-day IT work. English UI. Microsoft aka.ms is kept but must not dominate.

## Files

| Path | Role |
|---|---|
| `data/links/hub.json` | Main hub sections/links |
| `data/links/ai.json` | AI department page |
| `build_linkhub.py` | Builds both pages + search entries |
| `assets/links.js` | Client filter/search (CSP `self`) |
| `assets/style.css` (`.lh-*`) | Layout |

## Rules

1. Fact-check new external URLs before publish. Prefer official docs. Mark auth walls as portals; do not invent aka.ms shorts.
2. Every link needs a short `note` (what it is useful for) and a `kind`: `docs` | `product` | `tool` | `community` | `standard` | `portal`.
3. AI listings are **not** approval to upload company data — keep guardrails text and cross-links to the enterprise AI governance guide.
4. Do not conflate `/links/ai/` with the planned editorial `/ai/` hub.
5. Update `"checked"` when re-verifying. Do not push without Krister’s OK.

## Rebuild

```bash
python3 build.py
```

Preview: `dist/links/index.html` and `dist/links/ai/index.html`.
