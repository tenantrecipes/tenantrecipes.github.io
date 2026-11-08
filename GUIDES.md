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

**Every new page must have its own OG image.** The build does this automatically (`tools/make_page_og.py`, cached per page,
layout in `DESIGN.md`): run `python3 build.py` and commit the new `assets/og/p/*.jpg` and `assets/og/p/manifest.json` together with the page.
A pillar or technical guide may get a hand-made card instead (add it to `og_specs()` in `tools/make_shareables.py` and `og_image()`/`OG_PAGES`
in `build_ux.py`). `tools/check_meta.py` warns about any page that still falls back to a generic image.

Current assignments (2026-11-06): Pillar = secure-copilot-rollout, enterprise-ai-governance, windows-11-cis-hardening, cloud-hardening-adversary-emulation, azure-update-manager-enterprise-patching, azure-arc-onboarding-enterprise-scale, admin-by-request-endpoint-privilege (zero-to-production programme), entra-private-access-vpn-replacement, adcs-hardening-tier0, purple-team-hybrid-identity, external-attack-surface-osint, azure-devops-hardening-key-eater, pivot-lateral-movement-segmented. Technical = admin-by-request-intune-win32-packaging, copilot-license-checks (quick guide). All recipes = Recipe.
azure-update-manager-enterprise-patching, azure-arc-onboarding-enterprise-scale, admin-by-request-endpoint-privilege (zero-to-production programme),
entra-private-access-vpn-replacement, adcs-hardening-tier0, purple-team-hybrid-identity, external-attack-surface-osint. Technical = admin-by-request-intune-win32-packaging, copilot-license-checks (quick guide). All 51 recipes = Recipe.

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
| 2 | Internal purple team: network listening to compromised hybrid identity | **Done 2026-11-02** | `purple_team_hybrid_identity.py` / `purple-team-hybrid-identity` |
| 3 | Map your entire external attack surface: OSINT to verified exposure | **Done 2026-11-03** | `external_attack_surface_osint.py` / `external-attack-surface-osint` |
| 5 | Pivot and lateral movement in a segmented network – post-exploitation end-to-end | **Done 2026-11-04** | `pivot_lateral_movement_segmented.py` / `pivot-lateral-movement-segmented` |

All five project guides (1, 2, 3, 4-via-Entra-Private-Access, 5) are now **COMPLETE** as of 2026-11-04. The evening routine no longer writes a new project guide each run; instead deepen existing guides via `HISTORY` when sources change, and keep growing breadth (new /tools/ or /code/ pages) and height (troubleshooting, detections, internal links).

## Priority editorial queue (state updated 2026-11-08)

- **Done 2026-11-05:** Azure DevOps hardening / Key Eater expert pillar (`azure_devops_hardening_key_eater.py`, `azure-devops-hardening-key-eater`), related source-qualified news, new service-connection trust-review method, and workload-CA troubleshooting depth in the cloud-hardening guide. Documentation verified; no lab testing claimed.
- **Done 2026-11-06:** Enterprise AI governance pillar for Copilot and third-party enterprise LLMs (`enterprise_ai_governance.py`, `enterprise-ai-governance`): approved inventory, shadow AI, SSO/CA, data boundaries/retention, Purview/DLP, AI Act/NIS2 hooks, link to secure Copilot rollout. Documentation verified; no lab testing claimed. Deploy AI homepage hub updated; dedicated `/ai/` hub page deferred.
- **Done 2026-11-06:** Dedicated `/ai/` hub page (editorial Enterprise AI hub + homepage feature, vendor-neutral AI service approval guide/checklist, AI link directory) — commits `eba47ca` / `fb91ea8`. The earlier "Next = /ai/ hub" item is closed.
- **Evening 2026-11-07:** breadth (`garak` LLM vulnerability scanner tool, `graph-copilot-usage-csv` code snippet), height (enterprise-ai-governance: Defender local AI agent/MCP discovery + garak pre-scale gate; copilot-usage-graph D28/v2 fix), 4 news, 2 KEV entries. Interactive AI-införandekoll NOT started (by design).
- **Evening 2026-11-08:** 4 news (Entra Agent ID lifecycle preview, Entra guest lifecycle preview, Intune EPM network settings, SharePoint `.agent` → Copilot Agent Builder), 2 KEV backlog items (Cisco SEG CVE-2026-76461 with the 3 November advisory update, WSO2 CVE-2026-5430), breadth (`locksmith` AD CS scanner, `invoke-locksmith-mode2` snippet), height (enterprise-ai-governance Agent ID lifecycle; AD CS guide now links the Locksmith tool page), policy updates (access-management + offboarding for agent identities). CISA KEV catalog version 2026.11.06 — no new additions since 6 November. Interactive AI-införandekoll NOT started (by design; preview first).
- **Next:** Interactive **AI-införandekoll** tool (approved by Krister 2026-11-07): runs locally in the visitor's browser, asks about usage/data/permissions and produces a customised checklist. **Must be shown to Krister as a readable draft or working preview before it goes live** — do not build-and-publish it inside an evening run.
- **Then:** Develop guides into interactive workflows (mark steps, save progress locally on the visitor's device, export an implementation plan) with recurring editorial boxes: "Why we recommend this", "When to choose something else", "Not verified". No invented experiences; author identity not revealed yet.
- **Ongoing:** breadth (new /tools/ or /code/ pages) + height (troubleshooting, detections, internal links) each evening, and the ordinary fact-check / KEV backlog. This queue update does not modify the scheduled routine itself.
