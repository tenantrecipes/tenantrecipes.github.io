"""Pillar guide: Entra/M365 cloud hardening under authorized attack simulation.
Chains ScubaGear → Monkey365 → Maester → Prowler → ROADtools → AADInternals.
Fact-checked against vendor docs and Microsoft Learn on 2026-10-31.
Text in `backticks` renders as <code>. 'rec' = recipe ids, 'tools' = tools ids under /tools/, 'sec' = cyber ids.
Time estimates are Tenant Recipes' own planning figures, not vendor numbers.
Defensive use only: own tenants or written authorization."""

SLUG = "cloud-hardening-adversary-emulation"
TITLE = "Cloud hardening under attack simulation: Entra and Microsoft 365 from baseline to adversary emulation"
SHORT = "Cloud hardening + adversary emulation"
DESC = ("An expert project playbook that chains ScubaGear, Monkey365, Maester, Prowler, ROADtools and AADInternals: "
        "establish a measurable Entra/M365 baseline, run authorized directory enumeration as adversary emulation, "
        "then close the loop with detection validation and remediation. Defensive use only.")
VERIFIED = "2026-10-31"
BADGE = "fact-checked against vendor docs and Microsoft Learn"
SRC_LABEL = "Official sources"
TIME_NOTE = ("Time estimates are our planning figures for a mid-size hybrid tenant (a few thousand users), not vendor numbers. "
             "Large directories and multi-subscription Azure estates take longer.")
CTA_FIRST = "Start with phase 1 →"

INTRO = [
    "Configuration scanners tell you where the tenant fails a baseline. Adversary-emulation tools show what an attacker with a foothold can actually enumerate. "
    "Running either alone leaves a gap: you harden against a checklist you never validate, or you enumerate without a measurable before/after. "
    "This guide is the project that closes that gap.",
    "The flow is deliberate. First you measure with ScubaGear, Monkey365, Maester and Prowler and turn the output into a risk backlog. "
    "Then, still under written authorization, you use ROADtools and AADInternals for directory enumeration that mirrors what a compromised identity would see. "
    "Finally you prove detection in Entra and Defender logs, remediate, and re-run the scanners so the engagement ends with evidence — not a slide deck of unchecked findings.",
    "This is not a beginner how-to for each tool. Each tool already has its own page under Tools. Here we assume you can install and authenticate them, "
    "and we focus on how an experienced admin or pentester sequences them, what to keep, what to ignore, and how to hand findings to change control without wrecking production.",
]
NAMING = ("Legal boundary: only tenants you own or have written permission to assess. Get scope, rules of engagement and a SOC notification in writing before the first scan. "
          "Tenant Recipes is not affiliated with CISA, Microsoft, Prowler, or the authors of Monkey365, Maester, ROADtools or AADInternals.")


def S(*keys):
    return [L[k] for k in keys]


L = {
    # ScubaGear / CISA
    "scuba_gh": ("ScubaGear on GitHub (CISA)", "https://github.com/cisagov/ScubaGear"),
    "scuba_exec": ("ScubaGear execution", "https://cisagov.github.io/ScubaGear/docs/execution/execution.html"),
    "scuba_params": ("ScubaGear parameters (ProductNames)", "https://cisagov.github.io/ScubaGear/docs/configuration/parameters.html"),
    "scuba_dep": ("ScubaGear dependencies", "https://cisagov.github.io/ScubaGear/docs/prerequisites/dependencies.html"),
    "scuba_pages": ("ScubaGear documentation (GitHub Pages)", "https://cisagov.github.io/ScubaGear/"),
    # Monkey365
    "m365_gh": ("Monkey365 on GitHub", "https://github.com/silverhack/monkey365"),
    "m365_docs": ("Monkey365 documentation", "https://silverhack.github.io/monkey365/"),
    "m365_basic": ("Monkey365: run your first scan", "https://silverhack.github.io/monkey365/getting_started/basic-usage/"),
    "m365_opts": ("Monkey365 global options (IncludeEntraID)", "https://silverhack.github.io/monkey365/configuration/general-options/"),
    "m365_m365": ("Monkey365 Microsoft 365 options", "https://silverhack.github.io/monkey365/configuration/microsoft365-options/"),
    # Maester
    "maester": ("Maester documentation", "https://maester.dev/"),
    "maester_inst": ("Maester installation", "https://maester.dev/docs/installation"),
    "maester_gh": ("Maester on GitHub", "https://github.com/maester365/maester"),
    # Prowler
    "prowler_intro": ("Prowler documentation (introduction)", "https://docs.prowler.com/introduction"),
    "prowler_az": ("Prowler: getting started with Azure", "https://docs.prowler.com/projects/prowler-open-source/en/latest/tutorials/azure/getting-started-azure/"),
    "prowler_m365": ("Prowler: getting started with Microsoft 365", "https://docs.prowler.com/projects/prowler-open-source/en/latest/tutorials/microsoft365/getting-started-m365/"),
    "prowler_gh": ("prowler-cloud/prowler on GitHub", "https://github.com/prowler-cloud/prowler"),
    # ROADtools
    "road_gh": ("ROADtools on GitHub", "https://github.com/dirkjanm/ROADtools"),
    "road_wiki": ("Getting started with ROADrecon", "https://github.com/dirkjanm/ROADtools/wiki/Getting-started-with-ROADrecon"),
    "road_py": ("roadrecon on PyPI", "https://pypi.org/project/roadrecon/"),
    # AADInternals
    "aad_docs": ("AADInternals documentation", "https://aadinternals.com/aadinternals/"),
    "aad_gh": ("AADInternals on GitHub", "https://github.com/Gerenios/AADInternals"),
    # Microsoft Learn (detection / remediation)
    "emerg": ("Manage emergency access accounts in Microsoft Entra ID", "https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access"),
    "pim": ("What is Privileged Identity Management?", "https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure"),
    "consent": ("Configure how users consent to applications", "https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-user-consent"),
    "ro": ("Conditional Access report-only mode", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-report-only"),
    "risk_pol": ("Risk policies in Conditional Access (ID Protection)", "https://learn.microsoft.com/en-us/entra/id-protection/howto-identity-protection-configure-risk-policies"),
    "risk_concept": ("Microsoft Entra ID Protection risk-based access policies", "https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-policies"),
    "signin_ca": ("Conditional Access and Microsoft Entra activity logs", "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/how-to-view-applied-conditional-access-policies"),
    "audit_ca": ("Troubleshoot Conditional Access policy changes (audit log)", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/troubleshoot-policy-changes-audit-log"),
    "audit_acts": ("Microsoft Entra audit log activity reference", "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-audit-activities"),
    "authstr": ("Conditional Access authentication strengths", "https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths"),
    "legacy": ("Block legacy authentication with Conditional Access", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-policy-block-legacy"),
    "secure_score": ("Microsoft Secure Score", "https://learn.microsoft.com/en-us/defender-xdr/microsoft-secure-score"),
    "graph_act": ("Microsoft Graph activity logs", "https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview"),
    "workload": ("Secure workload identities with Conditional Access", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity"),
}


PHASES = [
 {
  "id": "authorize", "title": "Authorize the engagement and lock the scope", "time": "1–3 days", "deep": False,
  "goal": "Written permission, a named scope, notified defenders and a read-first account plan before any tool runs.",
  "lead": "Skip this phase and you are not doing a security project — you are creating an incident. Everything below assumes the paperwork is done.",
  "steps": [
   {"t": "Get written authorization and a rules-of-engagement sheet",
    "check": "A signed (or ticketed) approval names the tenants, subscriptions, date window, allowed techniques and a stop-contact",
    "do": ["Document tenant IDs, primary domains, in-scope Azure subscriptions and any explicitly out-of-scope workloads (for example production finance apps or a partner B2B tenant).",
           "State that configuration scanners and directory enumeration are in scope; destructive writes, password sprays against production identities and phishing of real users are out of scope unless a separate ticket says otherwise.",
           "Name a stop-contact who can halt the work within minutes, and record how findings will be handed to change control.",
           "Keep the approval with the engagement log. Tools under `/tools/` carry the same permission reminder for a reason."],
    "pit": ["Verbal 'go ahead' from a colleague is not authorization. Security, legal and the workload owners should all be able to point at the same document.",
            "A Global Administrator who 'just wants a quick look' still needs a ticket — the audit log will show the activity either way."],
    "rec": [], "tools": ["internal-pentest-scoping"], "src": S("scuba_pages", "prowler_intro"),
    "marker": "practical"},
   {"t": "Notify the SOC and freeze false-positive handling",
    "check": "SOC / security operations has the engagement window, source IPs or jump hosts, and the test account UPNs",
    "do": ["Send the window, the jump-host IPs or device names, and the UPNs or app registrations that will authenticate to Graph, Exchange, SharePoint and Azure.",
           "Agree which alerts will be expected (unusual Graph volume, new OAuth grants, PowerShell module traffic) and which still page on-call.",
           "Agree how to mark engagement-related incidents so they are not auto-closed without review."],
    "pit": ["If you do not tell the SOC, the first ROADrecon gather will look like a successful compromise. That is useful once — as a detection test you planned — not as a surprise."],
    "rec": [], "tools": [], "src": S("audit_acts", "graph_act"),
    "marker": "practical"},
   {"t": "Prepare accounts, break-glass exclusions and a clean workstation",
    "check": "A least-privilege read account (or app) for scanners, a separate privileged read account for MFA/role dumps, break-glass excluded from blocking CA, and a hardened admin workstation",
    "do": ["Create or reuse a cloud-only assessment account with Global Reader / Security Reader (or a custom role that can read CA, apps, roles and audit). Prefer PIM-eligible elevation over standing Global Administrator.",
           "Confirm emergency access accounts exist, are cloud-only, use phishing-resistant MFA, and are excluded from every Conditional Access policy that can block sign-in.",
           "Run tools from a hardened jump host or Privileged Access Workstation. Do not leave `roadrecon.db`, ScubaGear HTML reports or Monkey365 exports on a daily-driver laptop.",
           "Prefer device-code or certificate auth over pasting passwords into CLI flags; treat every token file as a production secret."],
    "pit": ["Standing Global Administrator for 'convenience' turns the engagement account into the highest-value target in the tenant.",
            "Storing `.roadtools_auth`, Prowler service-principal secrets or ScubaGear service-principal certificates in a shared Teams channel is an incident of its own."],
    "rec": ["ca-break-glass", "pim-least-privilege-daily-ops"], "tools": [], "src": S("emerg", "pim"),
    "marker": "official"},
  ]},

 {
  "id": "scuba", "title": "Baseline with CISA ScubaGear", "time": "0.5–1 day", "deep": False,
  "goal": "A first, independent SCuBA baseline report for Entra, Exchange, SharePoint, Teams and the security suite that you can re-run after remediation.",
  "steps": [
   {"t": "Install ScubaGear on Windows PowerShell 5.1 and verify the version",
    "check": "`Invoke-SCuBA -Version` returns a version; dependencies installed via `Install-ScubaDependencies`",
    "do": ["On a Windows machine, open Windows PowerShell 5.1 (ScubaGear depends on libraries still tied to Windows PowerShell 5).",
           "Install from the PowerShell Gallery: `Install-Module -Name ScubaGear`, then `Install-ScubaDependencies`.",
           "Confirm with `Invoke-SCuBA -Version`. Keep the install method (Gallery vs GitHub zip) recorded in the engagement log."],
    "pit": ["PowerShell 7 is not a substitute here until Microsoft updates the dependent libraries; the ScubaGear docs are explicit that the tool runs on Windows PowerShell 5.",
            "`Install-ScubaDependencies` was previously named `Initialize-SCuBA`; scripts that still call the old name keep working as an alias."],
    "rec": [], "tools": ["scubagear"], "src": S("scuba_gh", "scuba_dep", "scuba_exec"),
    "marker": "official"},
   {"t": "Run the assessment and capture the HTML/JSON/CSV output",
    "check": "A dated report folder exists for Entra (`aad`), security suite, Exchange, SharePoint and Teams (and Power Platform / Power BI only if licensed and in scope)",
    "do": ["Interactive commercial tenants: `Invoke-SCuBA -ProductNames *` and complete the sign-in prompts.",
           "For a focused first pass on identity only: `Invoke-SCuBA -ProductNames aad`. Expand to `aad, exo, sharepoint, teams, securitysuite` once identity findings are triaged.",
           "Non-interactive / pipeline: use the service-principal parameters documented by CISA (`-AppID`, `-CertificateThumbprint`, `-Organization`) — never embed secrets in the repo that builds this site.",
           "Archive the HTML report, JSON and CSV under a dated engagement folder. Hash or ticket the archive so you can prove the baseline date later."],
    "pit": ["Omitting `-ProductNames` assesses the default product set and skips Power Platform and Power BI; that is often what you want on day one.",
            "The baselines reflect CISA's view (including BOD 25-01 contexts). Map each failed 'shall' to your own risk acceptance — do not treat every failure as an automatic production change.",
            "GCC / GCCH tenants may need `-M365Environment` on current releases; check the ScubaGear release notes for your version."],
    "rec": [], "tools": ["scubagear"], "src": S("scuba_exec", "scuba_params", "scuba_gh"),
    "marker": "official"},
  ]},

 {
  "id": "monkey-maester", "title": "Widen the lens with Monkey365 and Maester", "time": "1–2 days", "deep": False,
  "goal": "A second and third configuration view that overlaps ScubaGear where it should, and catches Exchange/Teams/SharePoint/Entra drift ScubaGear alone may not emphasize.",
  "steps": [
   {"t": "Run Monkey365 against Microsoft 365 with Entra included",
    "check": "An HTML (or CSV) Monkey365 report covers Exchange Online, Teams, SharePoint Online and Entra ID for the engagement tenant",
    "do": ["Install: `Install-Module -Name monkey365 -Scope CurrentUser` then `Import-Module monkey365`.",
           "Use a parameter splat such as: `Instance = 'Microsoft365'`, `Collect = @('ExchangeOnline','MicrosoftTeams','SharePointOnline')`, `IncludeEntraID = $true`, `PromptBehavior = 'SelectAccount'`, `ExportTo = 'HTML'`, then `Invoke-Monkey365 @options`.",
           "Add `Purview` to `Collect` when information-protection settings are in scope; set `SpoSites` if Monkey365 cannot auto-detect the SharePoint root URL.",
           "Store the report with the ScubaGear archive. Tag findings that duplicate ScubaGear so you do not open two tickets for one control."],
    "pit": ["Monkey365 is read-oriented (GET/POST to gather configuration) but the signed-in identity still defines what you see. A weak role produces a quiet, falsely green report.",
            "Treat the HTML as sensitive: it enumerates weaknesses in enough detail to help an attacker."],
    "rec": [], "tools": ["monkey365"], "src": S("m365_gh", "m365_basic", "m365_opts", "m365_m365"),
    "marker": "official"},
   {"t": "Install Maester and run the Pester-based Entra/M365 tests",
    "check": "`Invoke-Maester` produces an HTML report; failed Conditional Access and privileged-role tests are listed in the backlog",
    "do": ["Pin Pester as Maester documents: `Install-Module Pester -MinimumVersion 5.7.1 -MaximumVersion 5.7.1 -SkipPublisherCheck -Force -Scope CurrentUser`, then `Install-Module Maester -Scope CurrentUser`.",
           "Create a working folder, `Install-MaesterTests`, `Connect-Maester`, then `Invoke-Maester`.",
           "For CISA-aligned optional tests, install the extra modules Maester lists (Az.Accounts, ExchangeOnlineManagement, MicrosoftTeams, PnP.PowerShell) and connect with the broader `Connect-Maester` service set.",
           "Export or archive the HTML report. Prefer Maester in a scheduled pipeline later; for this project, one dated run is the baseline."],
    "pit": ["A passed Maester test means the setting matched that test — not that the tenant is 'secure'. Keep ScubaGear and Monkey365 in the same backlog.",
            "Exchange Online tests need View-Only Configuration (or equivalent) in EXO; Graph-only roles are not enough for every suite."],
    "rec": ["ca-report-only-first", "ca-block-legacy-auth"], "tools": ["maester"], "src": S("maester_inst", "maester", "maester_gh"),
    "marker": "official"},
  ]},

 {
  "id": "prowler", "title": "Add Prowler for Azure and Microsoft 365 provider checks", "time": "0.5–1 day", "deep": False,
  "goal": "Provider-native checks (Azure subscriptions and/or M365) that map to common frameworks and catch cloud-control gaps the PowerShell frameworks do not own.",
  "steps": [
   {"t": "Authenticate Prowler with a least-privilege app or browser session",
    "check": "Prowler can list the in-scope Azure subscriptions and/or the M365 tenant without using a standing Global Administrator password",
    "do": ["Install the open-source CLI per current Prowler docs (pip or container) on the jump host.",
           "Azure: prefer a service principal with Reader (plus the graph permissions Prowler documents) via `AZURE_CLIENT_ID` / `AZURE_TENANT_ID` / `AZURE_CLIENT_SECRET` and `prowler azure --sp-env-auth`, or `prowler azure --browser-auth --tenant-id <tenant-id>` for an interactive pass.",
           "Microsoft 365: register an app with the Graph and PowerShell permissions in the M365 authentication guide, then run for example `prowler m365 --sp-env-auth` (add `--init-modules` when you need full PowerShell-backed coverage). Certificate auth is preferred over client secrets.",
           "Limit Azure scans with `--subscription-ids` so out-of-scope subscriptions stay out of the report."],
    "pit": ["Scanner credentials with broad read (and sometimes PowerShell) access are high value — rotate or disable the secret/certificate when the engagement ends.",
            "Government cloud support differs by provider path; confirm the current Prowler docs before promising GCC High coverage."],
    "rec": [], "tools": ["prowler"], "src": S("prowler_intro", "prowler_az", "prowler_m365", "prowler_gh"),
    "marker": "official"},
   {"t": "Run identity, storage and logging checks first; archive JSON/HTML",
    "check": "A dated Prowler output set exists; high findings for identity, storage and logging are in the backlog with check IDs",
    "do": ["Run the Azure and/or M365 provider scans agreed in the scope sheet and write JSON plus HTML.",
           "Triage identity, privileged access, storage exposure and logging/diagnostic-settings failures before lower-severity noise.",
           "Copy the check ID into each ticket so re-runs can prove closure.",
           "Do not assume AWS-oriented advice applies to Azure or M365 — keep provider findings in separate backlog columns."],
    "pit": ["False positives around intentional exceptions are common; verify against the architecture decision record before opening a Sev-1.",
            "One noisy multi-subscription run can bury the Entra findings you care about for this project — filter early."],
    "rec": [], "tools": ["prowler"], "src": S("prowler_az", "prowler_m365", "prowler_intro"),
    "marker": "practical"},
  ]},

 {
  "id": "triage", "title": "Build one risk backlog from four scanners", "time": "1–2 days", "deep": True,
  "goal": "A single, deduplicated backlog with owners and due dates — the input to both remediation and the adversary-emulation phase.",
  "lead": "This is the deepest project-management phase. Tool output without a backlog is how engagements die as unread HTML.",
  "steps": [
   {"t": "Deduplicate and classify findings across ScubaGear, Monkey365, Maester and Prowler",
    "check": "One backlog (work item tracker or spreadsheet) with columns for source tool, control/check ID, asset, severity, owner, due date and status",
    "do": ["Merge by control theme, not by tool: Conditional Access gaps, privileged standing roles, legacy authentication, user consent, guest sprawl, logging/retention, SharePoint/Teams sharing, Azure identity and storage.",
           "When two tools fail the same underlying setting, keep one remediation item and list both evidence links.",
           "Separate 'fix now' (broken MFA exclusion, public storage, unrestricted user consent) from 'fix in a change window' (CA tightening, Exchange transport changes).",
           "Record accepted risks with an expiry and an approver — ScubaGear YAML exclusions exist for this reason on the CISA side; mirror the discipline for the other tools."],
    "pit": ["Opening one ticket per tool finding creates ticket fatigue and conflicting owners.",
            "Leaving severity at the tool's default without a business impact note guarantees the wrong work gets done first."],
    "rec": ["ca-production-lockout-mistakes", "entra-user-consent-restrict"], "tools": ["scubagear", "monkey365", "maester", "prowler"],
    "src": S("scuba_pages", "maester", "secure_score"),
    "marker": "practical"},
   {"t": "Pick the remediations that shrink attacker value before enumeration",
    "check": "Break-glass, blocking legacy auth (or a dated plan), MFA/authentication strength and consent restrictions are either fixed or explicitly deferred with a ticket",
    "do": ["Fix emergency access exclusions and monitoring first — you need them before any CA enforcement from later phases.",
           "Put legacy authentication on a kill path (report-only → On) and phishing-resistant MFA for privileged and high-value users on the same path.",
           "Restrict user consent to applications so the enumeration phase does not also discover a consent-phishing hole you already knew about.",
           "Defer cosmetic Secure Score points that do not change attacker value; keep the backlog honest."],
    "pit": ["Enforcing a new CA policy mid-engagement without report-only review can lock out the assessment account itself.",
            "Do not 'fix' findings by excluding them from the scanner config without an accepted-risk record."],
    "rec": ["ca-break-glass", "ca-block-legacy-auth", "ca-require-mfa-copilot", "ca-report-only-first", "entra-user-consent-restrict"],
    "tools": [], "src": S("emerg", "legacy", "authstr", "consent", "ro"),
    "marker": "practical"},
  ]},

 {
  "id": "roadtools", "title": "Adversary-style directory enumeration with ROADtools", "time": "0.5–1 day", "deep": False,
  "goal": "An offline, queryable Entra snapshot (ROADrecon) that shows users, apps, roles and relationships the way a foothold account would see them.",
  "steps": [
   {"t": "Install ROADrecon and authenticate with device code",
    "check": "`.roadtools_auth` exists from a successful `roadrecon auth`; Python 3.10+ on the jump host",
    "do": ["In a virtualenv: `pip install roadrecon` (Python 3.10+; upstream develops on 3.11).",
           "Prefer device code so MFA and Conditional Access apply: `roadrecon auth --device-code`, then complete `https://microsoft.com/devicelogin`.",
           "Avoid embedding passwords on the command line. Username/password auth uses a legacy grant that fails when MFA is required — which is exactly what you want in a hardened tenant.",
           "Confirm the SOC still has this account and jump host on the allow-expected list."],
    "pit": ["Token files and the later database are full-fidelity identity exports. Encrypt at rest, restrict ACLs, and wipe them at close-out.",
            "Authenticating as Global Administrator 'to see more' defeats the point of emulation — use the agreed assessment identity unless a specific privileged dump (for example MFA details) is ticketed."],
    "rec": [], "tools": ["roadtools"], "src": S("road_gh", "road_wiki", "road_py"),
    "marker": "official"},
   {"t": "Gather the tenant snapshot and review high-value objects in the GUI",
    "check": "`roadrecon.db` gathered; GUI review notes cover privileged roles, stale guests, over-permissioned apps and interesting OAuth grants",
    "do": ["Run `roadrecon gather`. In large tenants this takes time and may print unresolved-reference warnings — that does not mean the gather failed.",
           "For MFA property dumps, use an account with a privileged directory role and `roadrecon gather --mfa` only when the rules of engagement allow it.",
           "Start the local UI with `roadrecon gui` (serve only on the jump host loopback) and walk privileged roles, application credentials, guests and ownership edges.",
           "Export concrete findings into the same backlog: standing Global Administrators, apps with dangerous application permissions, guests without owners, unused high-privilege role assignments."],
    "pit": ["Do not expose the Flask GUI beyond localhost on a shared network.",
            "ROADtools is complementary to Maester/ScubaGear, not a replacement — configuration baselines and directory relationships answer different questions."],
    "rec": ["pim-least-privilege-daily-ops", "entra-user-consent-restrict"], "tools": ["roadtools", "maester", "scubagear"],
    "src": S("road_wiki", "road_gh", "pim"),
    "marker": "practical"},
  ]},

 {
  "id": "aadinternals", "title": "Deep Entra checks with AADInternals", "time": "0.5–1 day", "deep": False,
  "goal": "Targeted, read-first verification of federation, sync and portal-hidden details that scanners and ROADrecon did not fully settle.",
  "steps": [
   {"t": "Install AADInternals and obtain a cached token",
    "check": "Modules imported; `Get-AADIntAccessTokenForAADGraph -SaveToCache` (or MS Graph equivalent) succeeded for the assessment identity",
    "do": ["Install from the PowerShell Gallery: `Install-Module -Name AADInternals` and, when endpoint-specific functions are needed, `Install-Module -Name AADInternals-Endpoints`.",
           "Import the modules, then `Get-AADIntAccessTokenForAADGraph -SaveToCache` (interactive) or the MS Graph variant when the cmdlet you need requires it.",
           "Use `Get-Help` on every cmdlet before running it. The module mixes research and administration — many functions can change federation, credentials or sync behaviour.",
           "Log every cmdlet and tenant ID in the engagement log."],
    "pit": ["Write-capable cmdlets are production changes. Stay on read-oriented functions until a change ticket exists.",
            "Random mirrors and outdated copies are a supply-chain risk — install from the PowerShell Gallery / official GitHub only."],
    "rec": [], "tools": ["aadinternals"], "src": S("aad_docs", "aad_gh"),
    "marker": "official"},
   {"t": "Run the read-only checklist agreed in the engagement plan",
    "check": "Notes exist for federation/PTA/seamless SSO posture, service locations, and any sync or application-credential oddities in scope — without unplanned writes",
    "do": ["Execute only the read-oriented cmdlets listed in the engagement plan (for example tenant/service location inventory and readbacks of federation-related configuration).",
           "Compare results with ROADrecon and the scanner backlog: a federation setting that 'looks fine' in the portal but differs in AADInternals is a finding, not a curiosity.",
           "If a write cmdlet is required (for example to demonstrate a misconfiguration safely), open a change ticket, take a rollback note first, and keep the SOC on the call.",
           "Revoke or clear cached tokens when the phase ends."],
    "pit": ["EDR and cloud logs will show unusual Graph and AD-related traffic — that is expected when the SOC was notified, and a detection opportunity when you reach phase 8.",
            "Do not chase every research function in the module; stick to the questions the backlog still has open."],
    "rec": [], "tools": ["aadinternals", "roadtools"], "src": S("aad_docs", "audit_acts"),
    "marker": "practical"},
  ]},

 {
  "id": "detect", "title": "Prove detection: logs, risk and Conditional Access", "time": "1–2 days", "deep": False,
  "goal": "Evidence that the enumeration activity was visible (or a documented detection gap), plus risk-based CA ready in report-only.",
  "steps": [
   {"t": "Review sign-in and audit logs for the engagement activity",
    "check": "Sign-in logs show the assessment authentications and CA results; audit logs show any directory reads/changes in scope; gaps are ticketed",
    "do": ["In Entra ID > Monitoring & health > Sign-in logs, filter to the assessment UPNs / app IDs and inspect the Conditional Access tab on representative events.",
           "In Audit logs, filter Service to Conditional Access (and other directory services you touched) and confirm you can see policy and role activity; use Modified properties when comparing before/after.",
           "If Microsoft Graph activity logs are enabled in the tenant, correlate high-volume ROADrecon gather traffic — absence of that telemetry is itself a finding.",
           "File a detection-gap ticket for anything the SOC did not see that the rules of engagement said should have alerted."],
    "pit": ["Default audit retention is short; if the engagement spans more than a few weeks, confirm diagnostic settings export to Log Analytics or storage before you need the evidence.",
            "Report-only CA results are easy to misread — confirm the specific report-only outcome codes in the sign-in details."],
    "rec": ["ca-report-only-first"], "tools": [], "src": S("signin_ca", "audit_ca", "audit_acts", "graph_act", "ro"),
    "marker": "official"},
   {"t": "Align ID Protection risk signals with Conditional Access (report-only first)",
    "check": "User-risk and sign-in-risk policies exist as separate Conditional Access policies in Report-only (or a dated migration plan from legacy ID Protection policies)",
    "do": ["Create separate Conditional Access policies for user risk and sign-in risk — do not combine both risk conditions in one policy.",
           "Exclude emergency access accounts. Start with Report-only, review impact in sign-in logs, then move to On.",
           "If legacy risk policies still live under ID Protection, plan migration to Conditional Access before the documented retirement date (1 October 2026 per Microsoft Learn).",
           "Use the engagement's simulated risky behaviours only if the rules of engagement and licensing allow; otherwise validate with historical true-positive risk events."],
    "pit": ["Turning risk policies to On without report-only review is a common lockout pattern — treat it like any other CA enforcement.",
            "Require risk remediation / authentication strength choices must match methods your users actually have registered."],
    "rec": ["ca-risk-based-ai", "ca-managed-risk-remediation-policy", "ca-break-glass", "ca-production-lockout-mistakes"],
    "tools": [], "src": S("risk_pol", "risk_concept", "ro", "emerg"),
    "marker": "official"},
  ]},

 {
  "id": "remediate", "title": "Remediate, re-baseline and close the engagement", "time": "3–10 days", "deep": False,
  "goal": "Owned fixes in production rings, a second scanner pass that shows movement, and a clean wipe of engagement secrets and exports.",
  "steps": [
   {"t": "Drive the backlog through change control with rollback notes",
    "check": "Every 'fix now' item is closed or accepted; every CA/Entra change has a rollback path (Report-only/Off, previous role assignment, previous consent setting)",
    "do": ["Implement through rings where possible: pilot group → wider cohort → tenant default.",
           "For Conditional Access, prefer Report-only → On over delete/recreate. Keep break-glass exclusions on every blocking policy.",
           "Attach evidence (scanner check IDs, ROADrecon notes, sign-in log screenshots with tenant identifiers redacted) to each work item.",
           "Re-run only the relevant scanners after each ring — full four-tool suites on every micro-change wastes calendar time."],
    "pit": ["Closing tickets based on 'we clicked around the portal' without a re-scan loses the before/after story the project was built for.",
            "Never delete a CA policy that caused pain — set it to Report-only or Off, then invent the replacement."],
    "rec": ["ca-report-only-first", "ca-production-lockout-mistakes", "pim-least-privilege-daily-ops"],
    "tools": ["scubagear", "maester"], "src": S("ro", "pim", "consent"),
    "marker": "practical"},
   {"t": "Re-run the baseline tools and publish the delta",
    "check": "A second dated archive of ScubaGear (+ at least Maester or Monkey365) exists; the backlog shows which check IDs moved from fail to pass",
    "do": ["Re-run ScubaGear with the same ProductNames and config you used at kickoff so the delta is meaningful.",
           "Re-run Maester (and Monkey365/Prowler as needed) and attach the HTML diffs or a short delta table to the engagement report.",
           "Optionally re-gather ROADrecon after privileged-role and app-permission clean-up to show the relationship graph changed.",
           "Write the final report as: scope, tools, baseline date, top findings, remediations, detection gaps, residual risk, and re-baseline date."],
    "pit": ["Changing scanner versions mid-engagement without noting it makes deltas look like regressions.",
            "Do not claim 'tested configuration' on Tenant Recipes (or in your own report) unless you actually named the lab and date — verification against docs is not a lab test."],
    "rec": [], "tools": ["scubagear", "monkey365", "maester", "prowler", "roadtools"],
    "src": S("scuba_exec", "maester_inst", "prowler_intro", "road_wiki"),
    "marker": "practical"},
   {"t": "Revoke access, wipe exports and schedule the recurring loop",
    "check": "Assessment secrets rotated/disabled; `roadrecon.db` / token files wiped or vaulted; Maester or ScubaGear scheduled for recurring drift detection",
    "do": ["Disable or rotate the assessment service principal secrets/certificates; remove standing role assignments that existed only for the engagement.",
           "Securely delete or vault scanner reports and ROADrecon databases per your data-handling rules.",
           "Leave Maester (and/or ScubaGear non-interactive) on a schedule so the next drift shows up without another full purple-team project.",
           "Book the next adversary-emulation window — baselines without occasional enumeration rot quietly."],
    "pit": ["Forgotten assessment apps with high Graph permissions are a favourite real-world persistence path.",
            "A scheduled scanner that nobody reads is theatre — wire failures into the same backlog owners you used here."],
    "rec": ["pim-least-privilege-daily-ops"], "tools": ["maester", "scubagear"],
    "src": S("pim", "maester", "scuba_exec", "graph_act"),
    "marker": "practical"},
  ]},
]
