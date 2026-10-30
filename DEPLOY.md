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
- Newsletter drafts: `python3 tools/newsletter_draft.py --issue 2 --recipes id1,id2` writes
  `newsletters/drafts/issue-002.md` with teaser links + UTM tags. Drafts are never sent automatically;
  KP approves and sends from Buttondown.
