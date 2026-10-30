# Screenshot candidates

Recipes support optional, real screenshots (`"screenshots"` in the recipe JSON, files in `assets/screenshots/`, see RECIPES.md).
Nothing is fabricated: the slots stay empty until a real, redacted screenshot from a test tenant is added.

Top 5 recipes where a screenshot helps most (admin UI with easy-to-miss settings):

1. `ca-require-mfa-copilot`: the Conditional Access Grant pane with *Require authentication strength > Phishing-resistant MFA*, and the report-only toggle.
2. `sharepoint-restricted-content-discovery`: SharePoint admin center > Active sites > site > Settings with *Restrict content from Microsoft Copilot*.
3. `purview-dlp-copilot-location`: the DLP Locations step with *Microsoft 365 Copilot and Copilot Chat* turned on, and the *Prevent Copilot from processing content* action.
4. `copilot-pilot-group-licensing`: Microsoft 365 admin center > Billing > Licenses > Assign licenses to a group, plus the Errors & issues tab.
5. `agents-restrict-blueprint-creation`: Entra ID > Users > User settings with *Users can create agent blueprints* set to No.

Runner-up: `copilot-teams-meeting-transcription` (Teams meeting policy Copilot dropdown).

Rules: take them in a test tenant, redact tenant/user names and IDs, crop to the relevant pane, add the date you took them, and re-take when the portal changes.
