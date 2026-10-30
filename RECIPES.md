# Recipe data format

One recipe = one file: `data/recipes/<id>.json`. `build_data.py` picks up every file, validates it,
and only publishes `"status": "published"`. Run `python3 build.py` after adding or editing.

```json
{
  "id": "ca-break-glass",                  // = file name, lowercase-kebab-case, becomes recipes/<id>.html
  "status": "published",                   // published | draft | needs-review | retired
  "order": 130,                            // sort order within the category (optional)
  "category": "Conditional Access for AI", // see CATEGORY_ORDER in site_config.py
  "title": "Keep break-glass accounts out of every AI-era CA policy",
  "problem": "One or two sentences. Also used as page description and newsletter teaser.",
  "steps": ["Plain text. Put commands in `backticks` to render them as code."],
  "pitfalls": ["..."],
  "done_when": ["Observable end state, e.g. 'The policy is On and break-glass accounts are excluded.'"],  // our own wording, derived from the steps
  "sources": [
    {"title": "Manage emergency access accounts",
     "url": "https://learn.microsoft.com/...",
     "checked": "2026-11-02"}             // date this link was checked against the recipe text, or null
  ],
  "last_verified": "2026-11-02",           // date every claim was fact-checked against the sources, or null
  "verified_by": "KP",                     // person or pipeline that verified, or null
  "created": "2026-10-12",
  "updated": "2026-11-02",
  "screenshots": []                        // optional, REAL screenshots only (never mock-ups): see below
}
```
(Comments above are for explanation only; real files must be plain JSON.)

`done_when` (recommended; the build warns when it is missing) is rendered as a "Done when" checklist and included in the
"Copy steps" text and the downloadable Markdown checklist. Write it originally; it must not claim anything the steps and sources don't support.

`screenshots` is a list of `{"src": "assets/screenshots/<file>.png", "alt": "...", "caption": "...", "date": "YYYY-MM-DD"}`.
Only add genuine screenshots from a real tenant (redact tenant names, users and IDs). The caption shows "Screenshot taken <date>".
The build fails if a listed file is missing. Candidate recipes are listed in SCREENSHOTS.md.

Topic tags on the homepage (Copilot, Conditional Access, News / Retirement, ...) are derived automatically in `build_ux.tags_for()`.

Recipe pages show "Last verified against Microsoft docs: <date>" when `last_verified` is set,
otherwise a notice that the recipe has not yet been re-verified.

The 40 original recipes were migrated on 2026-10-30 by `tools/migrate_v1_to_files.py` with
`last_verified: null` and `checked: null` (they have not been fact-checked yet; `created` is approximate).

## Cybersecurity entries (`data/cyber/<id>.json`)

Built by `build_cyber.py` into `/security/` (landing, one page per area, one page per entry).
Common fields: `id`, `status`, `order`, `type` (`vulnerability` | `hardening`), `area`
(`network` | `endpoint` | `server` | `services` | `virtualization` | `cloud`), `title`, `summary`,
`category` (required for vulnerabilities, optional for hardening; one of `Client` | `Server` | `Network` |
`Web/Runtime` | `Virtualization` | `Firmware` | `Cloud/M365`, validated by the build and used by the filter chips on /security/),
`steps`, `pitfalls`, `sources` (https, with `checked`), `last_verified`, `verified_by`, `created`, `updated`.

Extra fields for `type: vulnerability`: `vendor`, `product`, `severity` (the vendor's own rating),
`exploited` (bool), `kev_added` (CISA KEV date or null), `advisory_date`, `advisory_id`, `impact`,
`affected` (list), `fixed` (list), `action` (one short 'What to do' line, max 200 chars, shown on the watch list), and `cves`: `[{"id": "CVE-YYYY-NNNN", "cvss": 9.8 | null,
"cvss_version": "3.1", "cvss_source": "Broadcom", "severity": "Critical", "note": "..."}]`.

Rules: copy CVE ids, versions, CVSS and dates only from the vendor advisory, CISA (KEV JSON feed:
https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) or NIST NVD.
If a value can't be verified, leave it null or out. Never estimate a CVSS score.
A Patch Tuesday summary entry should use an id starting with `patch-tuesday-` (or set `"patch_tuesday": true`);
the countdown widget then links to the newest one during the 24 hours after release.

## News items (`data/news/<id>.json`)

Shown at `/news/` (newest first, category filter), on the homepage "Latest news" strip, in search (group "News") and in the Atom feed `/news/feed.xml`. Built by `build_news.py`; the build stops on invalid data.

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Equals the file name. Page URL is `/news/<id>.html`. |
| `status` | yes | `published` or `draft`. |
| `title` | yes | Plain statement of the change. |
| `date` | yes | `YYYY-MM-DD`, the date we published the item. |
| `category` | yes | One of: M365, Entra, Intune, Copilot/AI, Purview, Defender, Windows, Security incidents, Regulation, Retirements. |
| `summary` | yes | 2–4 sentences in our own words (checked by the build). |
| `why` | yes | Why it matters to an admin. |
| `todo` | yes | List of short actions ("What to do"). Backticks render as code. |
| `effective` | no | `YYYY-MM-DD` when the change takes effect; `null` if no single date. |
| `effective_note` | no | Free text for rollout windows or a second date. |
| `primary` | yes | `{title, url}`: the primary source (Microsoft Learn, message center, vendor advisory). |
| `related` | no | `[{title, url}]`; relative URLs are site pages, usually the recipe with the full how-to. |
| `recipe` | no | Id of the related recipe. Recipes keep their own URLs; news items link to them. |
| `sources` | yes | `[{title, url, checked}]` as for recipes; `last_verified` is required. |

Exploited vulnerabilities (`data/cyber`, `type: vulnerability`, `exploited: true`) appear automatically as category "Security incidents" and link to their `/security/<id>.html` page; do not duplicate them in `data/news`.
