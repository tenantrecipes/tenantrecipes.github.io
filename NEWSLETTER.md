# The Tenant Recipes Weekly Brief: format and Monday-draft rules

The evening routine follows this file when it writes the Monday draft. Change the format here, not in the routine.

## Schedule and approval
- **Monday:** the routine writes a draft to `newsletters/drafts/issue-NNN.md` (git-ignored, never published).
- **KP approves** the draft. Nothing is sent or scheduled without his explicit approval.
- **After approval:** the issue is scheduled in Buttondown (`tenantrecipes`) for **Thursday 22:00 Europe/Stockholm** (changed from Tuesday 15:00 on 2026-11-05).

## Fixed format (always these four sections, in this order)
Title: `The Tenant Recipes Weekly Brief — Issue #NNN (YYYY-MM-DD)`

1. **3 Microsoft changes you should know.** Microsoft 365, Entra, Intune, Purview, Defender, Copilot or agents.
   Each item: bold headline, one or two sentences on what changes and when, a **Do:** line, and a link.
2. **2 security updates worth investigating.** Exploited or high-impact vulnerabilities, Microsoft first, then
   infrastructure that M365 admins usually own (VPN, firewalls, hypervisors). Each item: headline, impact,
   a **Check first:** line, and a link.
3. **1 practical configuration tip.** One concrete setting, with the recipe that shows the steps, the check and the rollback.
4. **1 thing to review in your tenant.** One thing to look at this week, such as a report, a role assignment,
   an exclusion or an expiring setting, with where to find it (portal path, PowerShell or Graph) and a link.

## Rules
- **Length:** about a 5-minute read (roughly 500–700 words). Exactly 3 + 2 + 1 + 1 items. No extra sections.
- **Audience and tone:** experts who run tenants. Plain English, no hype and no beginner explanations. Write what to do, not what the feature is.
- **Sources:** every item links to a fact-checked page on Tenant Recipes (news, security or recipe), which carries the official sources.
  An item without a published page on the site is left out, or the page is published first.
- **Own words:** paraphrase; never copy Microsoft, CIS or vendor text.
- **UTM on every site link:** `utm_source=newsletter&utm_medium=email&utm_campaign=issue-NNN&utm_content=<page-id>`.
  The draft tool adds these automatically.
- **Dates:** state effective dates explicitly ("from 4 November 2026"). Do not reuse items from the previous issue
  unless the date or the action has changed.
- **Sponsor slot:** keep the HTML comment; it stays empty until a sponsor is signed.
- **Identity:** no personal names or employer anywhere; sign as "Tenant Recipes".

## How to create the draft
```
python3 tools/newsletter_draft.py --issue N --date YYYY-MM-DD \
  --changes <news-or-recipe-id>,<id>,<id> --security <cyber-id>,<cyber-id> \
  --tip <recipe-id> --review <recipe-id>
```
The tool pre-fills each item from the published page and writes UTM-tagged links. Any slot without an id becomes
a `TODO(...)` placeholder. Then edit the text by hand: tighten the wording, make the **Do:** / **Check first:** lines
specific, and remove every TODO before asking KP for approval.

Template: `templates/newsletter.md`. Public description of the format: `/newsletter.html` and the sample issue at
`/newsletter-sample.html` (built from published pages in `build_ux.sample_issue_body`).
