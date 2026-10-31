# Deploying Tenant Recipes

Production: **https://tenantrecipes.com** (GitHub Pages via Actions, custom domain set in the Pages settings; `www` and `tenantrecipes.github.io` redirect to it). See the security checklist at the end.

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

## Custom domain
Live as `tenantrecipes.com` since 2026-10-31. GitHub Pages: Settings > Pages > Custom domain (with an Actions deployment no
`CNAME` file is needed). `SITE_URL` in `site_config.py` drives canonical, sitemap, robots, RSS, Open Graph, security.txt
and newsletter links. Links to the GitHub repo/issues stay on `github.com/tenantrecipes/tenantrecipes.github.io`.

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

## What's new bar and changelog

Every page carries a thin **"What's new"** ticker at the bottom edge of the sticky header
(logo left, search + menu right). It sticks with the header (it lives *inside* `header.sh`, so the sticky
unit is ~76 px: 44 px nav + ~30 px ticker). Collapsed it shows the newest 1–2 entries; the toggle opens an
absolute dropdown of the latest 8 so the sticky height never jumps. "All updates →" goes to `/changelog/`.

**Source of truth:** `data/changelog.json` — same file that feeds `/changelog/` and the search index.
Do not invent a parallel feed. Schema per entry:

```json
{
  "date": "2026-10-31",          // required, YYYY-MM-DD (Europe/Stockholm calendar day)
  "time": "08:38",               // optional HH:MM Europe/Stockholm; omit rather than invent a clock
  "kind": "site",                // legacy bucket; keep "site" for curated notes
  "type": "Guide",               // Guide | Recipe | News | Security | Tool | Policy | Site — used as the badge
  "title": "Short title",        // linked title in the bar
  "blurb": "One-line description shown next to the title.",
  "url": "guides/slug.html",     // relative to the site root; used as the link target
  "text": "Full sentence for the changelog page and Atom feed."
}
```

When you publish something new, **append an entry at the top** of `data/changelog.json` with the Stockholm
date and the real publish time (or leave `time` out if you only know the day). Prefer the committer time of
the publishing commit for `time` — never invent a clock. The build sorts by `(date, time)` descending and
renders the bar + `/changelog/` automatically.

## Analytics (cookie-free, GoatCounter)


The site is ready for [GoatCounter](https://www.goatcounter.com): no cookies, no local storage, no personal data
stored, only aggregate counts. It is free for sites of this size ("reasonable public usage"), so no consent
banner is needed for it. Until a site code is set, **nothing** is added to the pages and the privacy policy says "no analytics".

Steps for the site owner:
1. Sign up at **https://www.goatcounter.com/signup**. Use the brand mailbox, not a personal or work address.
   - *Code*: pick e.g. `tenantrecipes`. This becomes `https://tenantrecipes.goatcounter.com` (the dashboard).
   - *Site domain*: `tenantrecipes.com`.
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


## Security checklist (tenantrecipes.com)

Status legend: [x] done, [ ] owner action.

### DNS (Loopia)
- [x] Apex `@`: four A records 185.199.108.153, .109, .110, .111 (GitHub Pages). AAAA optional.
- [x] `www`: CNAME to `tenantrecipes.github.io`. Nothing else on `www`.
- [x] No wildcard (`*`) records. GitHub warns that wildcards pointing at Pages allow domain takeover. Never add one.
- [ ] Verify the domain for GitHub Pages (account Settings > Pages > Add a domain): GitHub shows a TXT record
      `_github-pages-challenge-tenantrecipes` with a one-time value. Add it in Loopia and keep it. This blocks other
      GitHub accounts from claiming the domain or its subdomains. Not available via the REST API.
- [ ] CAA (after the HTTPS certificate is issued): `@ CAA 0 issue "letsencrypt.org"` and `@ CAA 0 issuewild ";"`.
      GitHub Pages certificates come from Let's Encrypt; any other CA is then refused. Re-check if you add a service
      that needs another CA (for example a third-party mail or marketing host on a subdomain).
- [ ] Optional: enable DNSSEC in Loopia if offered for .com.

### HTTPS
- [x] Custom domain set via API; certificate requested from Let's Encrypt (state is visible with
      `gh api repos/tenantrecipes/tenantrecipes.github.io/pages --jq .https_certificate`).
- [x] Certificate approved (Let's Encrypt, apex + www, auto-renewed by GitHub) and **Enforce HTTPS** on (2026-10-31):
      `http://` -> `https://`, `www` and `tenantrecipes.github.io` -> `https://tenantrecipes.com/` (301).
- HSTS: checked 2026-10-31, GitHub Pages sends **no** `Strict-Transport-Security` header on custom domains, and the repo
  cannot add one (a meta tag does not work for HSTS). HSTS and preload need a proxy/CDN in front (see below).

### Headers and browser policy
GitHub Pages cannot set custom HTTP headers (`_headers` and `netlify.toml` only work on Netlify). What the site does instead:
- [x] `tools/security_meta.py` (runs in `build.py`) adds a per-page `Content-Security-Policy` meta tag to every page:
      `default-src 'self'`, sha256 hashes for each inline script/style (no `unsafe-inline`, no `unsafe-eval`),
      `object-src 'none'`, `frame-src 'none'`, `base-uri 'self'`, `form-action 'self' https://buttondown.com`,
      `upgrade-insecure-requests`. GoatCounter hosts are allowed only when `GOATCOUNTER_CODE` is set.
      The build fails if a page gains inline event handlers (`onclick=`) or `style=""` attributes.
- [x] `<meta name="referrer" content="strict-origin-when-cross-origin">` on every page.
- [x] Clickjacking: `assets/ui.js` hides the page and breaks out when it is loaded inside a frame (X-Frame-Options and
      CSP `frame-ancestors` are ignored in meta tags).
- Not possible on GitHub Pages (checked 2026-10-31, none of these headers are sent): HSTS, X-Frame-Options,
  `frame-ancestors`, X-Content-Type-Options, Permissions-Policy. GitHub serves correct `Content-Type` values, which
  limits the sniffing risk. For full header control later: a proxy/CDN in front (for example Cloudflare with
  Transform/Response Header rules; certificate issuance must then be handled at the proxy) or Netlify hosting, where
  `netlify.toml` already carries headers. Target set: `Strict-Transport-Security: max-age=63072000; includeSubDomains`,
  `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` + `frame-ancestors 'none'`,
  `Referrer-Policy: strict-origin-when-cross-origin`,
  `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()`.

### Privacy
- [x] No cookies, no local storage, no tracking while `GOATCOUNTER_CODE` is empty. GoatCounter is cookie-free when enabled.
- [x] `/.well-known/security.txt` and `/security.txt` (RFC 9116) on the new domain; private vulnerability reporting
      on the GitHub repo is enabled.

### Mail (Microsoft 365) - owner action when the domain is added to the tenant
Copy every value from the Microsoft 365 admin center (Settings > Domains > tenantrecipes.com > DNS records) or
the Defender portal. Do not type them from memory: Microsoft assigns parts of them per tenant.
- [ ] TXT `@`: `MS=ms########` (domain verification, value from the admin center).
- [ ] MX `@`: the exact host the admin center shows (`tenantrecipes-com.mail.protection.outlook.com` or the newer
      `...mx.microsoft` form for new domains), priority 0. Remove any Loopia MX records.
- [ ] TXT `@` (SPF, only one SPF record): `v=spf1 include:spf.protection.outlook.com -all`
- [ ] CNAME `autodiscover` -> `autodiscover.outlook.com`
- [ ] DKIM: CNAME `selector1._domainkey` and `selector2._domainkey` with the targets from
      `Get-DkimSigningConfig -Identity tenantrecipes.com | Format-List Selector1CNAME,Selector2CNAME`
      (new domains use `selector1-tenantrecipes-com._domainkey.<tenant>.<x>-v1.dkim.mail.microsoft`). Then enable
      DKIM signing for the domain in Defender > Email authentication settings.
- [ ] DMARC TXT `_dmarc`: start with `v=DMARC1; p=quarantine; pct=100; adkim=s; aspf=s; rua=mailto:dmarc@tenantrecipes.com`
      and move to `p=reject` after a week or two of clean reports. The domain only sends through Microsoft 365.
- [ ] Optional hardening: MTA-STS (`_mta-sts` TXT + policy file on `https://mta-sts.tenantrecipes.com`) and TLS-RPT
      (`_smtp._tls` TXT `v=TLSRPTv1; rua=mailto:tlsrpt@tenantrecipes.com`).
- [ ] Create the aliases `contact@tenantrecipes.com` and `security@tenantrecipes.com` (plus `dmarc@` / `tlsrpt@` for reports if used)
      and send a test mail to each. Only then set `CONTACT_EMAIL = "contact@tenantrecipes.com"` and
      `SECURITY_EMAIL = "security@tenantrecipes.com"` in `site_config.py`, add the security address to `SECURITY.md`, and rebuild.

### GitHub account `tenantrecipes`
- [ ] 2FA on the account (passkey or authenticator app, recovery codes in the password manager). Cannot be checked or
      enabled via the API with the current token.
- [x] Repo ruleset `protect-main`: blocks deletion and force-push of `main` (normal pushes and the status workflow still work).
- [x] Secret scanning + push protection on; Dependabot vulnerability alerts on; private vulnerability reporting on.
- [x] Default workflow token permission is read-only; only the Pages workflow asks for `contents`/`pages`/`id-token` write.

### Anti-scraping (AI crawlers)
- [x] `robots.txt` (generated in `build_site.py`, list in `AI_BOTS`): Googlebot, Bingbot and `*` allowed; known AI
      crawlers (GPTBot, ChatGPT-User, OAI-SearchBot, CCBot, ClaudeBot, anthropic-ai, Claude-Web, Google-Extended,
      Applebot-Extended, PerplexityBot, Bytespider, Amazonbot, meta-externalagent, FacebookBot, cohere-ai, Diffbot,
      Omgilibot, ImagesiftBot, YouBot, Timpibot) get `Disallow: /`. `Google-Extended` only opts out of Gemini training,
      not Google Search. Well-behaved bots honour this; scrapers that ignore it need the proxy below.
- [x] `<meta name="robots" content="noai, noimageai">` on every page (`tools/security_meta.py`, merged with any existing
      `noindex`); `tools/check_meta.py` fails the build if a page lacks it.
- [x] `/ai.txt` disallowing AI training; Terms of use at `/about.html#terms` (footer: Legal > Terms of use).

### TODO: Cloudflare (free plan) in front — after the M365 mail DNS is done
Do this only after MX/SPF/DKIM/DMARC for M365 are in place and verified, so the mail records are copied over intact.
- [ ] Add `tenantrecipes.com` to Cloudflare (free), let it import the zone, compare every record with Loopia
      (A x4, `www` CNAME, `_github-pages-challenge-tenantrecipes` TXT, MX, SPF, DKIM CNAMEs, DMARC, autodiscover, CAA).
      Keep the GitHub Pages records **DNS only** (grey) until the certificate question is settled, then proxy.
- [ ] Move the nameservers at Loopia to the two Cloudflare nameservers. If DNSSEC is on at Loopia: turn it off
      first, then re-enable it in Cloudflare and add the new DS record at Loopia.
- [ ] SSL/TLS mode **Full (strict)**; Always Use HTTPS; minimum TLS 1.2; keep GitHub "Enforce HTTPS" on.
- [ ] Security > Bots: **Block AI bots** (all pages) and **Bot Fight Mode** on. Check that Googlebot/Bingbot still
      reach the site (Search Console URL inspection) after enabling.
- [ ] Rate limiting rule (free plan allows one): for example more than ~60 requests per 10 s per IP -> block/challenge.
- [ ] WAF custom rules: challenge empty or known-bad user agents, block requests for `/.git`, `/wp-*`, `*.php`.
- [ ] Response headers (Transform Rules): HSTS `max-age=63072000; includeSubDomains` (preload only once stable),
      `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy: frame-ancestors 'none'`,
      `Referrer-Policy`, `Permissions-Policy` (target set above).
- [ ] Re-check CAA: Cloudflare edge certificates need its CAs (letsencrypt.org, pki.goog, ssl.com) allowed.
- [ ] Verify afterwards: `curl -sI https://tenantrecipes.com/` shows the headers; GitHub Pages settings still green.
