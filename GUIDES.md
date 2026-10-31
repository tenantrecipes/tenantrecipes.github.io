# Content tiers: Pillar guides, Technical guides, Recipes

Every piece of content on Tenant Recipes is exactly **one** of three levels. The tier is shown as a coloured badge on the page,
groups the cards on `/guides/` (with a filter) and appears as a "Three levels" strip under the task hubs on the homepage.
`build_tiers.py` holds the labels; the build **fails** when a guide or recipe has no valid tier.

| Tier | Where it lives | What it is | Typical size | Must have |
|---|---|---|---|---|
| **Pillar guide** (`pillar`) | `data/guides/<module>.py`, `TIER = "pillar"` | An end-to-end programme for a whole area (e.g. Copilot rollout, Windows 11 CIS, Azure Arc, Update Manager, Entra Private Access). Ties many recipes, tools and technical guides together. | 7–12 phases, 20–45 steps | Phases with goals and time estimates, per-step sources, printable checklist + PDF, troubleshooting and rollback phase. |
| **Technical guide** (`technical`) | `data/guides/<module>.py`, `TIER = "technical"` | A deep dive into one specific task or component (e.g. packaging Admin By Request with IntuneWinAppUtil.exe, a pre-flight check list). Links up to its pillar guide. | 1–9 phases, exact commands and verification | Prerequisites and permissions, exact commands, expected result, verification, troubleshooting, sources. |
| **Recipe** (`recipe`) | `data/recipes/<id>.json`, `"tier": "recipe"` | One short, concrete fix for one real problem. | 3–10 steps | Problem, steps, pitfalls, done-when, sources (schema in RECIPES.md). |

Rule of thumb: *If it needs phases, it is a guide. If it spans a whole area, it is a pillar. If it answers one question, it is a recipe.*

## Required module fields for a guide

```python
SLUG = "my-guide"            # URL: guides/my-guide.html
TIER = "pillar"              # "pillar" | "technical"  (required; build fails otherwise)
PUBLISHED = "2026-11-03"     # first publication date (required)
VERIFIED = "2026-11-03"      # last full fact-check against the sources (shown as "Last verified")
UPDATED = "2026-11-10"       # optional: last content change; defaults to VERIFIED
HISTORY = [("2026-11-10", "Added a rollback step for ring 3.")]   # optional per-page version notes
TITLE, SHORT, DESC, INTRO, NAMING, PHASES ...   # as in the existing modules
```

Register the module in `build_site.py` (`GUIDES = [...]`). Version history on the page is assembled automatically from
`PUBLISHED`, `UPDATED`/`VERIFIED`, `HISTORY` and every `data/changelog.json` entry whose `url` points to the page,
so older guides need no manual history.

Current assignments (2026-10-31): Pillar = secure-copilot-rollout, windows-11-cis-hardening, cloud-hardening-adversary-emulation,
azure-update-manager-enterprise-patching, azure-arc-onboarding-enterprise-scale, admin-by-request-endpoint-privilege (zero-to-production programme),
entra-private-access-vpn-replacement, adcs-hardening-tier0. Technical = admin-by-request-intune-win32-packaging, copilot-license-checks (quick guide). All 51 recipes = Recipe.

## Code Library (`data/code/<id>.json` → `/code/`)

Copy-ready snippets built by `build_code.py`. Each snippet must come from an existing guide step, recipe or interactive tool page on this site
(condensed, never copied from external sites) and link back to it. Fields: `id` (= file name), `status`, `title`,
`lang` (`powershell` | `azcli` | `shell` | `bicep` | `kql` | `json` | `http` | `yaml`), `tags`, `summary`, `code`,
`notes` (before-you-run warnings), `source` (`{"kind": "guide", "slug", "anchor", "label"}`, `{"kind": "recipe", "id", "label"}` or `{"kind": "tool", "path", "label"}` for an interactive tool page from `build_apps.py`),
`refs` (official references, https), `created`, `last_verified`. The build fails on an unknown language, guide slug or recipe id.
Use `<placeholders>` for tenant-specific values and never include secrets.

## Project-guide queue (evening routine state)

The evening routine writes one project guide per run in the order **1 → 2 → 3 → 5** (4 is already covered by the Entra Private Access guide).
Before writing, check this table and `data/guides/` so nothing is written twice; after publishing, mark the row done and move "Next".

| # | Project guide | Status | Module / slug |
|---|---|---|---|
| 1 | AD CS hardening as Tier 0 | **Done 2026-10-31** (written ahead of the evening run) | `adcs_hardening_tier0.py` / `adcs-hardening-tier0` |
| 2 | (per routine prompt) | **Next** | — |
| 3 | (per routine prompt) | Queued | — |
| 5 | (per routine prompt) | Queued | — |

Next run: start with guide **2**. Do not write another AD CS guide; extend `adcs-hardening-tier0` via `HISTORY` instead if sources change.
