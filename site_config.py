# ======================================================================
#  Tenant Recipes: site settings. THIS IS THE ONLY FILE YOU NEED TO EDIT.
#  After a change, rebuild:  python3 build.py
# ======================================================================

# >>> CHANGE ME: your Buttondown username (the last part of https://buttondown.com/<username>).
#     While it is still "BUTTONDOWN_USERNAME", the signup form is shown but marked as not live.
BUTTONDOWN_USERNAME = "tenantrecipes"

# Public URL of the site, no trailing slash. Leave "" until the first deploy, then set e.g.
# "https://tenantrecipes.netlify.app" or "https://<github-user>.github.io/tenantrecipes".
# Needed for absolute share-image URLs (LinkedIn/X previews), canonical links, sitemap and newsletter links.
SITE_URL = "https://tenantrecipes.github.io"

# Contact address shown on About/Privacy. Leave "" to tell readers to reply to any newsletter email.
CONTACT_EMAIL = ""

# Name of the person responsible for the site (shown in the privacy policy as data controller).
OWNER_NAME = "Tenant Recipes"
OWNER_COUNTRY = "Sweden"

# Where the site is hosted (named in the privacy policy). "Netlify" or "GitHub Pages".
HOSTING_PROVIDER = "GitHub Pages"

# Ad slots. False = NOTHING is rendered (no markup, no ad code). True = empty, labelled placeholders appear at the
# natural break points (homepage, after a recipe's intro and before related recipes, between guide phases, between
# the vulnerability watch and hardening on /security/). Ad network code is never added automatically; see README.md.
ADS_ENABLED = False

# Cookie-free, privacy-friendly page-view counting with GoatCounter (https://www.goatcounter.com).
# >>> CHANGE ME after signup: only the site code, i.e. "abc" from https://abc.goatcounter.com (lowercase, no URL).
#     While it is "", NOTHING is added to the pages and the privacy policy keeps saying "no analytics".
#     When set, every page loads https://gc.zgo.at/count.js and the privacy policy describes GoatCounter. See DEPLOY.md.
GOATCOUNTER_CODE = ""

# UTM parameters added to links in newsletter drafts.
UTM_SOURCE = "newsletter"
UTM_MEDIUM = "email"

SITE_NAME = "Tenant Recipes"
SITE_TAGLINE = "AI recipes for Microsoft 365 admins"
SITE_DESCRIPTION = ("Step-by-step playbooks for rolling out Microsoft 365 Copilot and AI agents safely: "
                    "Conditional Access, Intune, Purview and licensing, linked to Microsoft Learn.")

# Category display order (new categories are appended alphabetically).
CATEGORY_ORDER = [
    "Copilot rollout & governance",
    "Conditional Access for AI",
    "Intune & devices for AI",
    "Purview, DLP & data security for Copilot",
    "Identity & threat protection",
    "Agents & Copilot Studio governance",
    "Licensing & reporting",
    "Admin prompt templates",
]

# Public GitHub repo used for "Report an error" / "Suggest a recipe" (GitHub Issues). Brand account only.
GITHUB_REPO = "tenantrecipes/tenantrecipes.github.io"

# Pages whose last verification is older than this many days show a "due for re-check" notice.
REVERIFY_DAYS = 90

# Social profiles (brand accounts only). Shown in the footer; X handle is also used for the twitter:site meta tag.
X_HANDLE = "TenantRecipes"
