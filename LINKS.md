# Admin link hub (`/links/`)

Curated portals, Microsoft Learn docs and **stable** `aka.ms` shortcuts for day-to-day Microsoft 365 / Entra / Intune / Defender / Azure / Copilot admin work.

## Files

| Path | Role |
|---|---|
| `data/links.json` | All sections and links (edit this) |
| `build_linkhub.py` | Builds `dist/links/index.html` and search entry |
| `assets/style.css` (`.lh-*`) | Layout for the hub |

## Rules

1. **Fact-check every new aka.ms** with a redirect follow before adding it. Reject Bing `?ref=aka&shorturl=…` dead ends, 404s, eng.ms / internal SharePoint, and wrong-product landings (e.g. `aka.ms/copilot` → GitHub Copilot).
2. Prefer **current portal hostnames** (`entra.microsoft.com`, `intune.microsoft.com`, `security.microsoft.com`, …) over fragile portal shorts.
3. Keep the **aka.ms** section featured and first — that was an explicit product ask.
4. Language: English UI copy (matches the rest of the site).
5. Update the JSON `"checked"` date when you re-verify the list.
6. Do **not** push/publish without Krister’s OK. Nav already includes **Links**; confirm he wants it in the main header (it is crowded).

## Rebuild

```bash
python3 build.py
```

Then review `dist/links/index.html` locally. Commit only after approval.
