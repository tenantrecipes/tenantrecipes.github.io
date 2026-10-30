# ======================================================================
#  Tenant Recipes: site settings. THIS IS THE ONLY FILE YOU NEED TO EDIT.
#  After a change, rebuild:  python3 build.py
# ======================================================================

# >>> CHANGE ME: your Buttondown username (the last part of https://buttondown.com/<username>).
#     While it is still "BUTTONDOWN_USERNAME", the signup form is shown but marked as not live.
BUTTONDOWN_USERNAME = "krister"

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

# Sponsor/ad slots: empty containers in index and recipe layouts. False = not rendered visibly (hidden).
SHOW_AD_SLOTS = False

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
