# Tenant Recipes

Fact-checked, source-linked recipes for Microsoft 365 admins, plus guides and a security section.
Live at https://tenantrecipes.github.io/. An independent project, not affiliated with Microsoft or any vendor.

## Build

```
python3 build.py      # validates data, builds dist/, then runs tools/check_links.py and tools/check_meta.py
```

Every push to `main` builds and deploys to GitHub Pages (`.github/workflows/deploy-pages.yml`). The workflow
checks out the full git history because the What's new page (`/changelog/`) lists published changes from `git log`.

- Settings: `site_config.py` (the only file most changes need).
- Content: `data/recipes/`, `data/guides/`, `data/cyber/` (schemas in `RECIPES.md`), curated changelog notes in `data/changelog.json`.
- Deployment and domain notes: `DEPLOY.md`.

## Ad slots

The layout has ad placeholders at natural break points, so ads can be added later without hurting readability:

| Slot name | Where |
| --- | --- |
| `index-top`, `index-bottom` | Homepage, above and below the recipe library |
| `recipe-after-intro` | Recipe page, after "The problem" and the toolbar, before the steps |
| `recipe-before-related` | Recipe page, before "Related recipes & next steps" |
| `guide-after-intro`, `guide-between-phases-N` | Pillar guides, after phase 1 and between later phases |
| `security-between-sections` | `/security/`, between the vulnerability watch and the hardening recipes |

They are controlled by one flag in `site_config.py`:

```
ADS_ENABLED = False   # default: nothing is rendered, no markup and no ad code
ADS_ENABLED = True    # empty, labelled "Advertisement" placeholders appear (class .sponsor-slot, data-slot="<name>")
```

No ad network code is ever added automatically. To go live later, set `ADS_ENABLED = True`, put the network's
snippet into `ad_slot()` in `build_trust.py` (keyed on the slot name), update the privacy policy and cookie
consent, then rebuild. Keep ads out of the steps themselves and away from code blocks.
