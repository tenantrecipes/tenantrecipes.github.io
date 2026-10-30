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
  "sources": [
    {"title": "Manage emergency access accounts",
     "url": "https://learn.microsoft.com/...",
     "checked": "2026-11-02"}             // date this link was checked against the recipe text, or null
  ],
  "last_verified": "2026-11-02",           // date every claim was fact-checked against the sources, or null
  "verified_by": "KP",                     // person or pipeline that verified, or null
  "created": "2026-10-12",
  "updated": "2026-11-02"
}
```
(Comments above are for explanation only; real files must be plain JSON.)

Recipe pages show "Last verified against Microsoft docs: <date>" when `last_verified` is set,
otherwise a notice that the recipe has not yet been re-verified.

The 40 original recipes were migrated on 2026-10-30 by `tools/migrate_v1_to_files.py` with
`last_verified: null` and `checked: null` (they have not been fact-checked yet; `created` is approximate).

## Cybersecurity entries (`data/cyber/<id>.json`)

Built by `build_cyber.py` into `/security/` (landing, one page per area, one page per entry).
Common fields: `id`, `status`, `order`, `type` (`vulnerability` | `hardening`), `area`
(`network` | `endpoint` | `server` | `services` | `virtualization` | `cloud`), `title`, `summary`,
`steps`, `pitfalls`, `sources` (https, with `checked`), `last_verified`, `verified_by`, `created`, `updated`.

Extra fields for `type: vulnerability`: `vendor`, `product`, `severity` (the vendor's own rating),
`exploited` (bool), `kev_added` (CISA KEV date or null), `advisory_date`, `advisory_id`, `impact`,
`affected` (list), `fixed` (list), and `cves`: `[{"id": "CVE-YYYY-NNNN", "cvss": 9.8 | null,
"cvss_version": "3.1", "cvss_source": "Broadcom", "severity": "Critical", "note": "..."}]`.

Rules: copy CVE ids, versions, CVSS and dates only from the vendor advisory, CISA (KEV JSON feed:
https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) or NIST NVD.
If a value can't be verified, leave it null or out. Never estimate a CVSS score.
