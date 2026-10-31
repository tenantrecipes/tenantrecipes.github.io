# Tenant Recipes design spec

Derived from what the site already uses: `assets/style.css` (`:root` tokens), `assets/mark.svg`, and the
Open Graph templates in `tools/make_shareables.py` and `tools/make_page_og.py`. Keep new pages, images and
cards inside these rules. The site is anonymous, so no personal names, employers or photos go in any asset.

## Palette

| Token | Hex | Use |
|---|---|---|
| `--brand-ink` | `#0f2f6b` | Headings on light backgrounds, `theme-color`, the middle stop of the dark card gradient |
| `--brand` | `#1f6feb` | Links, primary buttons, the accent for Guide and Recipe cards |
| `--brand-2` | `#7a4dff` | Secondary accent (purple), the accent for Code cards and the default card |
| `--ink` / `--ink-2` / `--ink-3` | `#0e1424` / `#3b4357` / `#5d667c` | Body text, secondary text, captions |
| `--bg` / `--surface` / `--line` | `#f5f7fb` / `#fff` / `#e2e6ef` | Page background, cards, borders |
| `--ok` | `#0f7a4f` | Success, "Tested" marker, the accent for Tool cards |
| `--danger` | `#b3261e` | Exploited or critical, the accent for Security cards |
| `--info` | `#1b4fb8` | Info notes |
| Amber | `#e39a1f` | News and What's new cards (warm highlight, never for errors) |
| Teal blue | `#0b6e99` | Policy and Status cards |

Dark brand gradient (logo, OG cards): `#071027 → #0f2f6b (55%) → #2a1360`, with a soft radial glow in the
card's accent colour in the top-right corner. The logo tile uses `#0b2a6b → #1366d6 → #6b3fd4`.

## Type

- UI and headings: `Inter`, then the system stack in `--font`. Headings weight 800, tight letter spacing (about -1px at display sizes).
- Code: `--mono` (`ui-monospace`, Cascadia Code, SF Mono, Menlo, Consolas).
- No webfont downloads: the site relies on locally installed fonts, which keeps the strict CSP and zero third-party requests.

## Logo

- The mark is `assets/mark.svg`: a white shield with a blue check on a rounded gradient tile (radius 14/64).
- Wordmark: "Tenant" in white (on dark) or `--brand-ink` (on light), followed by "Recipes" in `#9fd0ff` on dark.
- Keep clear space of at least half the mark's width around it. Do not recolour, stretch, outline or add effects to the mark.

## Open Graph and Twitter cards

- Size 1200 × 630 (declared in `og:image:width`/`height`). `twitter:card` is `summary_large_image`.
- **Every page gets its own image.** Precedence, from `build_ux.og_for()`:
  1. Hand-made per page: `OG_PAGES` in `build_ux.py` (for example the CA policy generator and the mail DNS checker), the pillar,
     technical and quick guides, the newsletter and the home page. These are made by `tools/make_shareables.py` (PNG, `assets/og/`).
  2. Automatic card for every other page: `tools/make_page_og.py` renders `assets/og/p/<path-with-->.jpg`.
     It is cached by a hash of title, label, accent and template version, so only new or renamed pages are rendered.
     The build runs it automatically and rebuilds the HTML when new cards were made. Commit the new JPEGs with the page.
  3. Generic section image: used only when a card is missing or stale and the machine has no Chrome or Pillow (for example in CI).
- Automatic card layout: brand gradient background; logo and wordmark top-left; a pill with the content type; the page title
  (72 → 46 px depending on length, at most 4 lines); a footer row with "Fact-checked · sources linked" on the left and the domain on the right.
- Content type label and accent per section:

| Section | Label | Accent |
|---|---|---|
| `guides/` | Guide | `#1f7bff` |
| `recipes/` | Recipe · *category* | `#1f7bff` |
| `tools/` | Tool | `#0f7a4f` |
| `code/` | Code | `#7a4dff` |
| `security/` | Security | `#b3261e` |
| `policies/` | Policy | `#0b6e99` |
| `news/`, `changelog/` | News, What's new | `#e39a1f` |
| `status/` | Status | `#0b6e99` |
| Section index pages | The section name (Guides, Tools, Code Library …) | Same as the section |
| Root pages | Tenant Recipes | `#7a4dff` |

- To change the card design: edit `tools/make_page_og.py` and bump `OG_AUTO_VERSION` in `build_ux.py`, then build; every card is re-rendered.
- Social previews are cached by LinkedIn and X. After changing an image, refresh it in the LinkedIn Post Inspector
  (https://www.linkedin.com/post-inspector/).
