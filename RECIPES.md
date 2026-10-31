# Recipe data format

Content has three levels (Pillar guide / Technical guide / Recipe). This file covers **recipes**; see GUIDES.md for the tiers and guide modules.

One recipe = one file: `data/recipes/<id>.json`. `build_data.py` picks up every file, validates it,
and only publishes `"status": "published"`. Run `python3 build.py` after adding or editing.

```json
{
  "id": "ca-break-glass",                  // = file name, lowercase-kebab-case, becomes recipes/<id>.html
  "status": "published",                   // published | draft | needs-review | retired
  "tier": "recipe",                        // REQUIRED, always "recipe" here (pillar/technical guides: see GUIDES.md)
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
  "screenshots": [],                       // optional, REAL screenshots only (never mock-ups): see below
  "history": [{"date": "2026-11-05", "note": "Added rollback for the report-only step."}]   // optional version notes
}
```
(Comments above are for explanation only; real files must be plain JSON.)

`done_when` (recommended; the build warns when it is missing) is rendered as a "Done when" checklist and included in the
"Copy steps" text and the downloadable Markdown checklist. Write it originally; it must not claim anything the steps and sources don't support.

`screenshots` is a list of `{"src": "assets/screenshots/<file>.png", "alt": "...", "caption": "...", "date": "YYYY-MM-DD"}`.
Only add genuine screenshots from a real tenant (redact tenant names, users and IDs). The caption shows "Screenshot taken <date>".
The build fails if a listed file is missing. Candidate recipes are listed in SCREENSHOTS.md.

## Optional sections: troubleshooting and rollback

Both are optional but **encouraged for every new recipe that changes tenant configuration**. When a field is missing or empty,
nothing is rendered (no empty heading, no TOC entry, nothing in the Markdown checklist).

```json
"troubleshooting": [
  "A plain string works for a short tip.",
  {"symptom": "What the admin sees", "cause": "Likely cause (optional)", "fix": "What to do. `backticks` render as code."}
],
"rollback": ["Ordered steps that undo the change safely, e.g. set the CA policy back to Report-only or Off instead of deleting it."]
```

Rules: write only what the linked sources or the steps above support. No invented error codes, no guessed portal paths.
A rollback should name the safest reversible state (Report-only, Off, unassign, previous ring) and how to confirm the undo worked.

## Content markers: Official guidance / Practical insight / Tested configuration

Markers tell the reader where a section comes from. They are rendered as small badges that link to
`/methodology.html#markers` (legend). All fields are optional.

```json
"markers": {"steps": "official", "pitfalls": "practical", "troubleshooting": "practical", "rollback": "practical"},
"notes": [{"marker": "practical", "text": "Short editor callout shown after the steps."}],
"tested": {"environment": "E5 dev tenant, 25 users, Windows 11 24H2", "date": "2026-11-05", "result": "Policy blocked IMAP; Outlook unaffected."}
```

Sections that can carry a marker: `steps`, `done_when`, `pitfalls`, `troubleshooting`, `rollback`.

| Marker | Use when | Never use when |
|---|---|---|
| `official` – **Official guidance** | The section restates what Microsoft (or the primary vendor) documents, and the linked sources were checked. The build requires `last_verified`. | The section adds our own judgement or ordering that the source does not state. |
| `practical` – **Practical insight** | Editor experience, observations and field patterns (typical breakages, sensible rollout order). Not claimed as lab-tested. | It is only a paraphrase of the docs (use `official`). |
| `tested` – **Tested configuration** | The configuration was actually applied and tested in a real test environment. **`tested.environment` and `tested.date` are required**; the build fails without them or with a future date. The badge shows both. | The steps were only compared with documentation. That is verification, not testing. |

When in doubt, leave the section unmarked; unmarked sections still follow the verification process on the methodology page.

Guides (`guides/*.py`): a step dict may carry `"marker": "official" | "practical" | "tested"` (and `"tested": {...}` for tested).
The badge shows next to the step title.

Status 2026-10-31: the 40 published recipes whose sources are all Microsoft (Learn, Support, Tech Community, Adoption, labelled Message center mirror)
and whose steps were checked on 2026-10-30 have `"markers": {"steps": "official"}`. The `prompt-*` recipes are not marked.
Nothing is marked `tested`. `ca-block-legacy-auth`, `ca-require-mfa-copilot` and 11 more config-changing recipes (CA, Entra consent, Intune, Purview DLP, SharePoint RCD) have troubleshooting and rollback (marked `practical`).

## Checklist for new recipes (nightly pipeline)

1. Required fields (including `"tier": "recipe"`) plus `done_when`. If the content needs phases, it is a guide, not a recipe (GUIDES.md).
2. Add `troubleshooting` (2–4 items, symptom/fix) and `rollback` whenever the recipe changes configuration. Skip them rather than invent content.
3. Set `markers.steps` to `official` only when every step is backed by a checked Microsoft/vendor source. Use `practical` for editor-experience sections.
4. Never set `tested` unless a real test was run; record environment and date.
5. Write for experienced admins and pentesters: no beginner explanations, exact setting names, cmdlets and Graph endpoints.

Topic tags on the homepage (Copilot, Conditional Access, News / Retirement, ...) are derived automatically in `build_ux.tags_for()`.

## Internal linking: `related` and topic clusters

Optional `"related": ["<recipe-id>", ...]` lists curated cross-links (max 3 shown first under "Related recipes"; the build fails on an unknown id).
The rest is automatic (`build_links.py`): every recipe, news item and security entry belongs to the topic clusters whose keywords appear in its id, title and summary
(Identity & access, Devices & Windows, Copilot, agents & data protection). Recipe pages get a "More in this topic cluster" list; news items and Microsoft/Windows
security entries get related recipes when they share a specific cluster keyword. New recipes should set `related` to 2–3 recipes in a *neighbouring* cluster
(for example a CA recipe → device compliance or PIM), because same-cluster links are already added automatically.

Every recipe page shows Published (`created`), Last updated (`updated`) and Last verified at the top, a Sources block after the problem, and a Version history built from `created`, `updated`, `last_verified`, optional `history` notes and `data/changelog.json` entries whose `url` is the page (see `build_history.py`).

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

## OG image for every page

Every new recipe, guide, tool, code snippet, security or news page must have its own Open Graph image. It is automatic:
`python3 build.py` renders a branded card (title + content type, see `DESIGN.md`) for each page without a hand-made one,
caches it by title, and wires it into `og:image` and `twitter:image`. Commit the new `assets/og/p/*.jpg` and
`assets/og/p/manifest.json` with the page. `tools/check_meta.py` warns when a page still uses a generic image.

## Changelog entry for every publish

When you publish a new (or meaningfully updated) recipe, guide, tool, policy, news item or site feature,
add a curated note at the **top** of `data/changelog.json`. That file feeds both the site-wide What's new
bar under the sticky header and the `/changelog/` page. Schema and time rules: see the "What's new bar and
changelog" section of `DEPLOY.md`. Prefer a real Europe/Stockholm publish time; omit `time` rather than invent one.
