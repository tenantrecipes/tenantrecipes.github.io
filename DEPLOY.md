# Deploying Tenant Recipes (free, no custom domain)

Everything the site needs is built into `dist/`. All links are relative, so it works on a free
subdomain (`*.netlify.app`) or a GitHub Pages sub-path (`https://<user>.github.io/<repo>/`).

## 0. Before the first deploy
1. Create a free Buttondown account and note your username (`https://buttondown.com/<username>`).
2. Open `site_config.py` (the only file to edit) and set `BUTTONDOWN_USERNAME`.
   Optional: `CONTACT_EMAIL`, `OWNER_NAME`, `HOSTING_PROVIDER`.
3. Build: `python3 build.py`. It validates all recipes, regenerates the PDF checklists and link-preview images when their inputs changed (needs Chrome/Chromium; otherwise the committed files in `downloads/` and `assets/og/` are used), builds `dist/`, and checks links and page titles/descriptions.
   A non-zero exit code means: do not deploy.

## Option A: Netlify Drop (fastest, no Git)
1. Run `python3 build.py`.
2. Go to https://app.netlify.com/drop and sign up/log in (free).
3. Drag the **`dist` folder** (not the whole project) onto the page. You get a URL like
   `https://random-name-123.netlify.app`.
4. Site configuration > Change site name, e.g. `tenantrecipes` -> `https://tenantrecipes.netlify.app`.
5. Put that URL in `site_config.py` as `SITE_URL`, rebuild, and drag `dist` again
   (Deploys > drag & drop). This makes LinkedIn/X share previews, canonical links and the sitemap work.

Note: Netlify Drop does not run `netlify.toml` builds; you always drop the built `dist/` folder.

## Option B: Netlify connected to a Git repo (needed for automation)
1. Push the project to a GitHub repo (see the privacy note below).
2. Netlify > Add new site > Import an existing project > pick the repo.
   `netlify.toml` already sets build command `python3 build.py` and publish directory `dist`.
3. Every push to `main` now rebuilds and redeploys. A failed recipe validation or link check stops the deploy.

## Option C: GitHub Pages
1. Create a repo, e.g. `tenantrecipes`, and push the project.
2. Repo > Settings > Pages > Build and deployment > Source: **GitHub Actions**.
3. The included workflow `.github/workflows/deploy-pages.yml` builds and deploys on every push to `main`
   (or run it manually under Actions). URL: `https://<user>.github.io/tenantrecipes/`.
4. Set `SITE_URL = "https://<user>.github.io/tenantrecipes"` in `site_config.py` and push again.

**Privacy note:** free GitHub Pages needs a *public* repo. `.gitignore` keeps `PLAN.md` (sponsor
prospects), `screenshots/` and newsletter drafts out of Git. Double-check with `git status` before the first push.
Netlify Drop never uploads anything except `dist/`.

## Adding a custom domain later
Netlify: Domain management > Add a domain. GitHub Pages: Settings > Pages > Custom domain.
Then update `SITE_URL` and rebuild. Nothing else changes.

## Ad slots
See `README.md` ("Ad slots"). `ADS_ENABLED = False` in `site_config.py` (default) renders nothing.

## Automation hooks (for the future weekly pipeline)
- New recipe = new file `data/recipes/<id>.json` (schema in `RECIPES.md`), then `python3 build.py`.
- `build.py` exits non-zero on invalid recipes or broken links, so CI never deploys a broken site.
- Use `"status": "needs-review"` for recipes that failed fact-checking; only `published` ones are built.
- Newsletter drafts ("The Tenant Recipes Weekly Brief": 3 changes, 2 security updates, 1 tip, 1 thing to review):
  `python3 tools/newsletter_draft.py --issue 2 --changes id,id,id --security id,id --tip id --review id` writes
  `newsletters/drafts/issue-002.md` with UTM-tagged links. Format and Monday-draft rules: `NEWSLETTER.md`.
  Drafts are never sent automatically; KP approves, then the issue is scheduled in Buttondown for Tuesday 15:00 (Stockholm).

## SEO (technical)

- `robots.txt` (generated) allows everything and points to `https://<SITE_URL>/sitemap.xml`.
- `sitemap.xml` (generated) lists every indexable page with clean canonical URLs (directory pages end in `/`,
  not `index.html`) and `<lastmod>` from the page's `updated`/`last_verified` date where one exists.
  Redirect stubs (`search.html`, `changelog.html`) and `404.html` carry `noindex` and are left out.
- Every page gets `<link rel="canonical">` + `og:url` from `canon()` in `build_site.py`, built from
  `site_config.SITE_URL`. When the custom domain is live: change `SITE_URL`, rebuild, push. Nothing else.
- JSON-LD: `WebSite` + `SearchAction` (`/search/?q=`) on the home page, `TechArticle` on recipes, guides,
  news, security entries, tools and templates, `BreadcrumbList` wherever breadcrumbs are shown.
- `tools/check_meta.py` fails the build on missing/duplicate titles or descriptions, missing OG tags or canonical.
- Search Console (needs the site owner): add the property for the live domain, verify it, then submit
  `sitemap.xml`. Redo this after the move to the custom domain (plus a change-of-address if available).

## Analytics (cookie-free, GoatCounter)

The site is ready for [GoatCounter](https://www.goatcounter.com): no cookies, no local storage, no personal data
stored, only aggregate counts. It is free for sites of this size ("reasonable public usage"), so no consent
banner is needed for it. Until a site code is set, **nothing** is added to the pages and the privacy policy says "no analytics".

Steps for the site owner:
1. Sign up at **https://www.goatcounter.com/signup**. Use the brand mailbox, not a personal or work address.
   - *Code*: pick e.g. `tenantrecipes`. This becomes `https://tenantrecipes.goatcounter.com` (the dashboard).
   - *Site domain*: `tenantrecipes.github.io` (change it in GoatCounter settings when the custom domain is live).
   - Choose a strong password (save it in the password manager) and confirm the email.
2. In `site_config.py` set only the code, nothing else:
   ```python
   GOATCOUNTER_CODE = "tenantrecipes"   # the "abc" in https://abc.goatcounter.com
   ```
   Not the script, not the URL, not a password or API key. The build refuses anything other than a plain code.
3. Rebuild and push (`python3 build.py`, commit, push). Every page then loads
   `<script data-goatcounter="https://<code>.goatcounter.com/count" async src="https://gc.zgo.at/count.js">`,
   and the privacy policy and "How we verify" page switch automatically to the GoatCounter text.
4. Check: open the live site with the ad blocker off. A page view should show in the dashboard within about 10 seconds.
5. Optional, in GoatCounter settings: turn off screen size collection if not needed, and use "Ignore IPs", or open the site once with
   `#toggle-goatcounter` at the end of the URL, so your own visits are not counted.

To turn analytics off again: set `GOATCOUNTER_CODE = ""` and rebuild.

