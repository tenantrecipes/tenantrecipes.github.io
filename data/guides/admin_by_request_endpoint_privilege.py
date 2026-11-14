"""Pillar guide: removing standing local admin rights with Admin By Request (Endpoint Privilege Management), end to end.
Covers the problem (standing local admin vs fully locked-down users), plan and licensing, portal security, the Entra ID Connector,
policy design (Run As Admin, Admin Session, approval, MFA, lockdown), application control and malware scanning, deployment with
Intune (Windows Win32, macOS), pilot and rollout, removal of existing local admins, audit/reporting, troubleshooting and rollback.
Fact-checked against docs.adminbyrequest.com and Microsoft Learn on 2026-10-31. Setting names are as shown in the vendor docs on that date.
Text in `backticks` renders as <code>. 'rec' = recipe ids, 'tools' = tools ids under /tools/, 'sec' = cyber ids.
Not sponsored: Tenant Recipes has no commercial relationship with Admin By Request (see NOTICE)."""

SLUG = "admin-by-request-endpoint-privilege"
TIER = "pillar"  # pillar | technical (see GUIDES.md)
PUBLISHED = "2026-10-31"
TITLE = "Admin By Request: just-in-time elevation, no standing admin"
SHORT = "Admin By Request: just-in-time admin"
DESC = ("An expert, end-to-end playbook for replacing standing local administrator rights with Admin By Request: why permanent admin and total lockdown both fail, "
        "licensing and the free plan, portal SSO, the Entra ID Connector, Run As Admin vs Admin Session policy with approval and MFA, application control and malware scanning, "
        "Intune deployment for Windows and macOS, removing existing local admins, pilot to rollout, audit, troubleshooting and rollback.")
VERIFIED = "2026-10-31"
BADGE = "fact-checked against Admin By Request docs and Microsoft Learn"
SRC_LABEL = "Official sources"
TIME_NOTE = ("Time estimates are our planning figures for an estate of roughly 200–2,000 Windows and macOS endpoints managed with Intune, not vendor numbers. "
             "A 25-device free-plan tenant can do phases 1–7 in a few days; the long pole in a large estate is the pilot, because that is where you learn which applications people really elevate.")
CTA_FIRST = "Start with phase 1 →"

NOTICE = {
    "title": "Editorial note: this is not a sponsored article",
    "text": ("Tenant Recipes has no commercial relationship with Admin By Request. We were not paid, we receive no affiliate commission or free licences, "
             "and the vendor has not reviewed or approved this text. We recommend the product because, in our editorial judgement, it solves the standing-admin problem described below "
             "well and with little friction. Microsoft Intune Endpoint Privilege Management and other EPM products solve the same problem; phase 1 explains when they may fit better. "
             "Everything below is checked against the vendor's public documentation and Microsoft Learn, and every step links its sources."),
}

INTRO = [
    "Local administrator rights are the most common privilege that nobody owns. They are granted once to get a laptop working, inherited through an Entra join or an old image, "
    "and never taken back. This guide removes them for good without turning the service desk into an approval queue: users stay standard users, and elevation becomes a "
    "short, audited, policy-controlled event.",
    "We use Admin By Request (a Danish endpoint privilege management product) as the worked example, deployed with Microsoft Intune and governed through Microsoft Entra ID. "
    "The guide is written for administrators who already run Intune and Entra; it focuses on design decisions, setting names, limits and failure modes rather than on clicking through screens.",
]
NAMING = ("Scope: Windows 10/11 and macOS workstations managed by Intune, with notes for Windows Server and multi-session hosts. Product names: Admin By Request calls its privilege product "
          "Endpoint Privilege Management (EPM); Microsoft also sells an Intune feature called Endpoint Privilege Management — we always say which one we mean. "
          "Tenant Recipes is not affiliated with Admin By Request or Microsoft. Nothing on this page has been lab-tested by us; it is verified against vendor and Microsoft documentation.")

PROBLEM = {
    "title": "The problem: standing admin rights versus locked-down users",
    "blocks": [
        ("Why permanent local admin is a security debt",
         ["A user who is a permanent member of the local Administrators group hands that power to anything that runs in their session. A malicious attachment, a poisoned installer "
          "or a browser exploit no longer needs a privilege-escalation bug: it can disable or tamper with security tooling, install drivers and persistence, and read credential "
          "material cached on the machine.",
          "From there the problem stops being local. Credentials harvested on one workstation are reused for lateral movement, and shared or identical local admin passwords turn one "
          "compromised laptop into many. Offensive tools such as BloodHound and NetExec exist precisely to map and abuse these admin paths.",
          "Auditors look at the same thing from the other side. CIS Controls v8 asks that administrator privileges are restricted to dedicated administrator accounts, and NIS2 (Article 21) "
          "expects access control policies and multi-factor authentication as part of an entity's risk-management measures. Standing local admin for everyday accounts is hard to defend in either review."]),
        ("Why removing admin rights outright also fails",
         ["The obvious fix — make everyone a standard user and let IT install everything — moves the cost rather than removing it. Developers, engineers and field staff hit a wall "
          "several times a week: a driver for a new device, a CLI tool, a vendor installer, a printer. Each one becomes a ticket, productivity drops, and the organisation "
          "quietly starts handing out exceptions, shared admin passwords or a 'temporary' admin group that never empties.",
          "In other words, both extremes end in the same place: lots of people with uncontrolled admin rights, now with less visibility than before."]),
        ("How to solve it in general",
         ["The durable answer is least privilege with a controlled escape hatch. Everyday accounts are standard users. When elevation is genuinely needed it is granted just in time "
          "(for one application or for a short session), tied to a stated reason, optionally approved by IT and protected by MFA, and every elevated action is logged.",
          "Around that core sit a few companion controls: Windows LAPS (or an equivalent) so the built-in admin account is unique per device and rotated; application control "
          "(App Control for Business or AppLocker) where you need deny-by-default execution; Intune policy that keeps the local Administrators group clean; and privileged "
          "identities for IT staff managed separately, for example with PIM."]),
        ("Where Admin By Request fits",
         ["Admin By Request is the just-in-time elevation layer in that design. It strips standing admin rights at logon, then offers two ways back: Run As Admin elevates a single "
          "process while the user stays standard, and Admin Session makes the user a temporary administrator for a fixed number of minutes. Requests can require a reason, "
          "approval (in the portal or a mobile app), and MFA through Entra ID; elevated files can be checked against a multi-engine malware service first; and everything "
          "lands in one audit log. Policy can differ per Entra ID or Active Directory group, so developers and the finance team do not have to share one compromise.",
          "It is also deliberately not an application allow-listing product: software that runs without elevation is outside its view. Pair it with App Control for Business "
          "if you need that, which is exactly how this guide treats it."]),
    ],
    "src": [
        ("CIS Critical Security Controls v8", "https://www.cisecurity.org/controls/v8"),
        ("Directive (EU) 2022/2555 (NIS2), Article 21", "https://eur-lex.europa.eu/eli/dir/2022/2555/oj"),
        ("Implementing least-privilege administrative models (Microsoft Learn)", "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/implementing-least-privilege-administrative-models"),
        ("Windows LAPS overview (Microsoft Learn)", "https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview"),
        ("Admin By Request: Editions & Features (what the product does not do)", "https://docs.adminbyrequest.com/editions-features.htm"),
    ],
}


def S(*keys):
    return [L[k] for k in keys]


L = {
    # Admin By Request documentation
    "abr_lic": ("Admin By Request: Licensing (free plan, paid plans)", "https://docs.adminbyrequest.com/licensing.htm"),
    "abr_price": ("Admin By Request: Pricing", "https://www.adminbyrequest.com/en/pricing"),
    "abr_ed": ("Admin By Request: Editions & Features", "https://docs.adminbyrequest.com/editions-features.htm"),
    "abr_win_set": ("Admin By Request: Windows Settings (portal reference)", "https://docs.adminbyrequest.com/portal/settings/windows.htm"),
    "abr_tenant": ("Admin By Request: Tenant Settings (identity, privacy, retention, API, webhooks, auto-update)", "https://docs.adminbyrequest.com/portal/settings/tenant.htm"),
    "abr_approval": ("Admin By Request: Approval flow, sub-settings and pre-approval", "https://docs.adminbyrequest.com/approval.htm"),
    "abr_entra": ("Admin By Request: Entra ID Connector", "https://docs.adminbyrequest.com/integrations/sso/entra-id.htm"),
    "abr_sso": ("Admin By Request: Single sign-on setup", "https://docs.adminbyrequest.com/integrations/sso/single-sign-on.htm"),
    "abr_logins": ("Admin By Request: Portal logins", "https://docs.adminbyrequest.com/portal/logins.htm"),
    "abr_win_inst": ("Admin By Request: Windows client install / uninstall", "https://docs.adminbyrequest.com/endpoints/Windows/install.htm"),
    "abr_intune": ("Admin By Request: Working with Intune", "https://docs.adminbyrequest.com/integrations/intune.htm"),
    "abr_mac_inst": ("Admin By Request: Mac client install / uninstall", "https://docs.adminbyrequest.com/endpoints/macOS/install.htm"),
    "abr_net": ("Admin By Request: IP addresses and API URLs for proxies and firewalls", "https://docs.adminbyrequest.com/MicroContent/resources/MicroContent/micro-faq-connectivity/what-ip-addresses-do-we-allow-in-our-proxy-and-firewall.htm"),
    "abr_ui": ("Admin By Request: Windows client user interface (connectivity, diagnostics, proxy)", "https://docs.adminbyrequest.com/endpoints/Windows/ui.htm"),
    "abr_pol": ("Admin By Request: Policies for Windows (ADMX and registry overrides)", "https://docs.adminbyrequest.com/endpoints/Windows/policies.htm"),
    "abr_audit": ("Admin By Request: Auditlog (remote kill, export)", "https://docs.adminbyrequest.com/portal/auditlog.htm"),
    "abr_bg": ("Admin By Request: Break Glass / LAPS", "https://docs.adminbyrequest.com/features/break-glass-account.htm"),
    "abr_app": ("Admin By Request: Mobile app", "https://docs.adminbyrequest.com/features/mobile-app.htm"),
    "abr_faq": ("Admin By Request: FAQ", "https://docs.adminbyrequest.com/support/all-faq.htm"),
    # Microsoft Learn
    "ms_localadmin": ("Manage the local administrators group on Microsoft Entra joined devices", "https://learn.microsoft.com/en-us/entra/identity/devices/assign-local-admin"),
    "ms_acctprot": ("Account protection policy (Local user group membership) in Intune", "https://learn.microsoft.com/en-us/intune/intune-service/protect/endpoint-security-account-protection-policy"),
    "ms_laps": ("Windows LAPS overview", "https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview"),
    "ms_laps_entra": ("Windows LAPS with Microsoft Entra ID", "https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-scenarios-azure-active-directory"),
    "ms_epm": ("Intune Endpoint Privilege Management overview", "https://learn.microsoft.com/en-us/intune/intune-service/protect/epm-overview"),
    "ms_win32": ("Win32 app management in Microsoft Intune", "https://learn.microsoft.com/en-us/intune/intune-service/apps/apps-win32-app-management"),
    "ms_win32_prep": ("Prepare a Win32 app for upload (Content Prep Tool)", "https://learn.microsoft.com/en-us/intune/intune-service/apps/apps-win32-prepare"),
    "ms_mac_lob": ("Add a macOS line-of-business app to Intune", "https://learn.microsoft.com/en-us/intune/intune-service/apps/lob-apps-macos"),
    "ms_catalog": ("Intune settings catalog", "https://learn.microsoft.com/en-us/intune/intune-service/configuration/settings-catalog"),
    "ms_monitor": ("Monitor app information and assignments in Intune", "https://learn.microsoft.com/en-us/intune/intune-service/apps/apps-monitor"),
    "ms_appreg": ("Register an application in Microsoft Entra ID", "https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app"),
    "ms_consent": ("Configure how users consent to applications", "https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-user-consent"),
    "ms_wl": ("Workload identities overview", "https://learn.microsoft.com/en-us/entra/workload-id/workload-identities-overview"),
    "ms_wdac": ("App Control for Business", "https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/appcontrol"),
    "ms_uac": ("User Account Control", "https://learn.microsoft.com/en-us/windows/security/application-security/application-control/user-account-control/"),
    "ms_lpam": ("Implementing least-privilege administrative models", "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/implementing-least-privilege-administrative-models"),
}


PHASES = [
 {
  "id": "plan", "title": "Plan: measure admin sprawl, choose the elevation model and the plan", "time": "2–4 days", "deep": False,
  "goal": "You know who holds local admin today and why, you have a persona model that maps to Run As Admin and Admin Session, and the licence plan and data location are signed off.",
  "lead": "Every later phase consumes these decisions. A persona model invented during the pilot means rebuilding sub-settings and groups while users are already waiting for approvals.",
  "steps": [
   {"t": "Measure who holds local admin today, and how they got it",
    "check": "A list per device class shows every account and group in the local Administrators group, with the mechanism that put it there (Entra join, Entra role, GPO, Intune, manual)",
    "do": ["On Entra joined devices, the account that performs the join is added to the local Administrators group by default, together with the Global Administrator and Microsoft Entra Joined Device Local Administrator roles. That is the most common source of standing admin in cloud-first estates.",
           "Check the Entra device registration setting that controls whether the registering user becomes local admin (`azureADJoin.localAdmins.registeringUsers` in Graph) and the Autopilot profile's user account type. Both decide whether new devices keep producing local admins.",
           "Collect the current group membership with your management tooling, and for domain-joined estates map admin paths with BloodHound CE or enumerate them with NetExec from an authorised test account. Record the before-state: you will repeat the same measurement in phase 8."],
    "pit": ["Microsoft notes that changes to the Entra Joined Device Local Administrator role do not necessarily take effect on the device immediately. Do not treat a portal change as proof that the device is clean.",
            "Only scan systems you are authorised to test, and tell the SOC first: admin-path enumeration looks exactly like an attacker's reconnaissance."],
    "rec": ["autopilot-device-preparation-entra-join"], "tools": ["bloodhound-ce", "netexec"], "sec": ["harden-windows-laps"],
    "src": S("ms_localadmin", "ms_lpam"),
    "marker": "official"},
   {"t": "Map personas to Run As Admin, Admin Session or nothing",
    "check": "Each persona (for example office staff, developers, engineers, IT support, external staff) has a decision: Run As Admin with or without approval, Admin Session with MFA, or no elevation at all",
    "do": ["Run As Admin (application elevation) gives administrator rights to one process; the user remains a standard user. It is the safer default for most people because the elevated identity disappears when the process ends.",
           "Admin Session (user elevation) puts the user in the local Administrators group for a fixed number of minutes. Reserve it for work that spans many tools — engineers, developers configuring local services, IT staff — and protect it with approval and MFA.",
           "Plan a deny-by-default persona as well: kiosks, shared devices and external staff can have both elevation types switched off, with IT using Support Assist or a Break Glass account when a task truly needs admin.",
           "Decide now how you will meet deny-by-default execution requirements. Admin By Request controls elevation, not ordinary execution; pair it with App Control for Business or AppLocker where you need an allow-list."],
    "pit": ["Giving everyone Admin Session without approval simply recreates standing admin in 15-minute slices. Start from Run As Admin and add sessions only where a persona proves the need."],
    "rec": [], "tools": [], "src": S("abr_win_set", "abr_ed", "ms_wdac", "ms_uac"),
    "marker": "practical"},
   {"t": "Choose the plan, check licensing and the data location",
    "check": "The licence plan matches the device count, the support expectation is explicit, and the tenant's data location and retention are recorded for your privacy assessment",
    "do": ["At the time of writing the vendor offers a lifetime Free Plan with all features: up to 25 workstation seats (Windows, macOS or Linux) and up to 10 Windows Server seats. It is meant for small estates and proofs of concept and comes with no support commitment.",
           "Paid plans are quoted per organisation and bought in blocks of 25 or more seats. A paid plan covers all its devices — you do not get the first 25 free on top — but you can run a separate Free Plan tenant alongside it, which is handy as a test tenant.",
           "Licences are per device. Devices above your licence count do not show up in the inventory or audit log, so count every endpoint that will get the agent, including multi-session hosts that need Server seats.",
           "On the Free Plan you cannot delete a computer from the inventory; a seat is released when the client is uninstalled or after 60 days without contact. Plan reimaging cycles accordingly.",
           "Note the data centre region shown under `Settings > Tenant Settings > Data > RETENTION` before you write the privacy assessment; the agent's firewall rules in phase 6 depend on it too."],
    "pit": ["Prices and seat counts change; re-read the licensing and pricing pages before you budget. Licences cannot be returned once allocated.",
            "If you compare products: Microsoft's own Intune Endpoint Privilege Management is a licensed Intune add-on capability. Evaluate both against your personas instead of on feature lists alone."],
    "rec": [], "tools": [], "src": S("abr_lic", "abr_price", "abr_ed", "abr_tenant", "ms_epm"),
    "marker": "official"},
  ]},

 {
  "id": "portal", "title": "Secure the portal: admins, SSO, privacy and retention", "time": "1 day", "deep": False,
  "goal": "Only named administrators can reach the portal, they sign in through Entra ID, and the tenant collects exactly the personal data your privacy assessment allows.",
  "lead": "The portal can approve elevation on every endpoint you own. Treat it as a tier-0-adjacent system from day one.",
  "steps": [
   {"t": "Move portal sign-in to Entra ID and scope portal rights",
    "check": "Every portal user is a named person signing in with Microsoft 365 / Entra ID single sign-on, rights are scoped per role, and one emergency portal login is documented",
    "do": ["Add portal users under `Logins > User Logins` and choose the Microsoft 365 / Entra ID sign-on method. ADFS, Okta and generic SAML 2.0 are also supported via `Logins > Single Sign-on Setup`.",
           "The Microsoft 365 sign-on relies on user consent for the first login. If your tenant blocks user consent (it should), follow the vendor's admin-consent path or the SAML enterprise-application route instead of loosening consent for everyone.",
           "For the SAML route, the vendor documents the identifier `https://www.adminbyrequest.com/samlmeta`, the reply URL `https://www.adminbyrequest.com/saml` and `user.mail` as the unique user identifier.",
           "Give approvers only the rights they need (for example no `Manage portal users`), and keep the first administrator account — the one used to sign up — as a protected emergency login."],
    "pit": ["Once sign-in goes through Entra ID your Conditional Access policies decide who reaches the portal. Exclude nothing ad hoc; use the same emergency-access pattern you use for the tenant."],
    "rec": ["entra-user-consent-restrict", "ca-break-glass"], "tools": [], "src": S("abr_logins", "abr_sso", "ms_consent"),
    "marker": "official"},
   {"t": "Set privacy collection and audit retention before the first endpoint reports",
    "check": "Privacy toggles and the retention period match the privacy assessment, and the decision is recorded",
    "do": ["Under `Settings > Tenant Settings > Data > PRIVACY` decide on `Obfuscate user accounts`, `Collect user names`, `Collect user email addresses`, `Collect user phone numbers`, `Collect inventory` and `Allow geo-tracking`. Changes only apply to data collected afterwards, so decide before rollout.",
           "Keep `Collect inventory` on if you want device owners: `Lock device to owner` has no effect without inventory data.",
           "Under `Data > RETENTION` choose an audit retention between 3 months and 5 years (default 1 year) that matches your logging policy and NIS2/ISO evidence needs."],
    "pit": ["Lowering the retention period permanently deletes audit data older than the new period as soon as you save."],
    "rec": [], "tools": [], "src": S("abr_tenant"),
    "marker": "official"},
   {"t": "Brand the client and publish a code of conduct",
    "check": "Users see your company name, a short code of conduct and the service desk contact in the elevation dialogs",
    "do": ["Upload the logo under `Endpoint Privilege Management > Settings > Windows Settings > Endpoint > BRANDING` before turning on `Use logo file` and before you download the installer.",
           "Under `Endpoint > INSTRUCTIONS` enable `Show instructions before start` for Run As Admin and Admin Session, with a short code of conduct (what is logged, what is not allowed, who to call) and a display frequency.",
           "Under `Endpoint > LOOK & FEEL` set the request form's email and phone fields to Mandatory, Optional or Hide to match the privacy decision above."],
    "pit": ["A code of conduct shown every time trains users to click through it. Once a week is usually enough for regular users."],
    "rec": [], "tools": [], "src": S("abr_win_set"),
    "marker": "official"},
  ]},

 {
  "id": "entra", "title": "Connect Entra ID and design the group model", "time": "1 day", "deep": False,
  "goal": "Endpoints resolve Entra ID (or AD) group membership, global settings are the safe catch-all, and each persona has a group that a sub-setting can target.",
  "steps": [
   {"t": "Create the Entra ID Connector app registration",
    "check": "The connector shows a green check mark in the portal, the app has only the Graph application permission `Directory.Read.All` with admin consent, and the secret has an owner and a renewal date",
    "do": ["Register a dedicated app in Entra ID (for example `Admin By Request Entra ID Connector`), remove the default delegated `User.Read`, and add the Microsoft Graph application permission `Directory.Read.All`. Grant admin consent.",
           "Create a client secret (the vendor suggests 24 months), then enter the tenant name, application (client) ID and secret under `Settings > Tenant Settings > Identity > ENTRA ID` and switch `Enable Connector` on. Saving validates the connection.",
           "The connector is used by endpoints to read user and device groups for sub-settings and global scope. It is not the portal sign-in; that was phase 2.",
           "Put the app under your workload-identity governance: named owner, secret expiry alert, and sign-in monitoring for the service principal."],
    "pit": ["`Directory.Read.All` is a broad read permission. Store the secret in a vault, never in tickets or chat, and rotate it on schedule. When it expires, endpoints keep using cached group data, but new memberships stop flowing in and the portal Summary warns you.",
            "National clouds (GCC High, DoD, 21Vianet) need the `National Cloud` toggle and the matching service."],
    "rec": [], "tools": [], "src": S("abr_entra", "abr_tenant", "ms_appreg", "ms_wl"),
    "marker": "official"},
   {"t": "Settle hybrid identity behaviour",
    "check": "For hybrid devices you have chosen `Prefer Active Directory` or `Prefer Entra ID / Azure AD` and tested one device of each join type",
    "do": ["On-premises Active Directory groups and OUs need no connector; endpoints read them directly and cache them encrypted, so sub-settings keep working off the LAN.",
           "For devices that are AD-joined while the user also has an Entra work-join, set `Hybrid Preference` so you know which directory's groups are evaluated.",
           "If you also use Okta, Google or JumpCloud as the Windows identity provider, the corresponding connectors exist (Windows client 8.5 or later); Jamf Pro device groups can drive macOS sub-settings."],
    "pit": ["Pick one directory per persona. Scopes that mix AD OUs with Entra groups make it hard to predict which rules apply to a hybrid user."],
    "rec": [], "tools": [], "src": S("abr_tenant", "abr_approval"),
    "marker": "official"},
   {"t": "Design global settings as the safe catch-all and sub-settings per persona",
    "check": "Global settings are the most restrictive profile, every persona from phase 1 has an Entra group, and a test user who belongs to no group gets the restrictive behaviour",
    "do": ["Treat global settings as what a user or device gets when they fall outside every group by mistake — so make them the strictest profile you can live with.",
           "Create one sub-setting per persona, scoped to user groups, computer groups or OUs. Sub-settings can override any setting, not only authorisation.",
           "Use the global `SCOPE` tab only to exclude populations from the product entirely; users or computers outside the scope cannot elevate at all, and local (non-directory) users cannot elevate when a scope is set.",
           "Name groups so the persona is obvious in the audit log (for example `EPM-Developers`, `EPM-Engineering`, `EPM-ITSupport`), because each audit entry shows which sub-setting applied."],
    "pit": ["Overlapping persona groups make it hard to predict which sub-setting a user gets. Keep persona groups mutually exclusive and check the sub-setting name in the audit log during the pilot."],
    "rec": [], "tools": [], "src": S("abr_approval", "abr_win_set", "abr_audit"),
    "marker": "practical"},
  ]},

 {
  "id": "policy", "title": "Build the elevation policy: authorisation, MFA and lockdown", "time": "2–3 days", "deep": True,
  "goal": "Global settings and every persona sub-setting define who may elevate, how (reason, approval, MFA), for how long, and what stays forbidden even when elevated.",
  "lead": "This is where the security value is decided. Most failed deployments either left the free-plan defaults in place or made the policy so strict that users went back to tickets.",
  "steps": [
   {"t": "Set authorisation: Run As Admin, Admin Session, approval, reason and time",
    "check": "For global and each sub-setting, `Allow Run As Admin`, `Require approval`, `Require reason`, `Allow Admin Sessions` and `Access time (minutes)` are set deliberately and documented",
    "do": ["Under `Windows Settings > Authorization > AUTHORIZATION`, `Allow Run As Admin` and `Allow Admin Sessions` are on by default, and `Require approval` is off by default for both. On the free plan that means any request is granted automatically — the vendor itself recommends turning approval on.",
           "Turning `Require approval` on makes `Require reason` mandatory. A reason for Run As Admin must be at least two words and is stored in the audit log with the user's contact details.",
           "`Access time (minutes)` defaults to 15. Size it for the longest legitimate install the persona runs; combine with `Force applications close at end` (lockdown, next step) so elevated processes do not outlive the session.",
           "With `Allow Run As Admin` off you can additionally switch on `Block Run As Admin`, which removes the UAC credential prompt even for people who know an admin password.",
           "Turn on email notifications under `Authorization > NOTIFICATION` for the approver mailbox, and install the vendor's mobile app for approvers; push notifications are sent automatically."],
    "pit": ["Approval for everything does not scale. Combine approval with pre-approvals, machine learning and AI approval (phase 5) so approvers only see the unusual requests."],
    "rec": [], "tools": [], "src": S("abr_win_set", "abr_approval", "abr_app"),
    "marker": "official"},
   {"t": "Require MFA for elevation through Entra ID",
    "check": "Personas that may start Admin Sessions authenticate with Entra ID MFA at elevation, and the email-matching mode is chosen deliberately",
    "do": ["Under `Endpoint > UAC` set `User Account Control Mode` to `Multi-factor Authentication` (alternatives: `Confirm`, a yes/no prompt, and `Authenticate`, Windows credentials or Hello). Choose `Microsoft 365 / Entra ID` as the sign-on method, or add any SAML provider.",
           "`Email match` (default) requires the MFA identity to match the user's email or UPN. `Account separation` requires a separate secondary account, which the vendor positions for Cyber Essentials Plus. `No matching` requires the Entra ID Connector so only identities from your own tenant can authenticate.",
           "Decide `MFA on pre-approvals`; leaving it off keeps pre-approved software friction-free.",
           "Windows Server edition runs in authenticate mode only: standard users supply credentials at every elevation, and there is no MFA mode on servers."],
    "pit": ["The elevation sign-in is an ordinary Entra sign-in, so your Conditional Access policies apply to it. Check the sign-in logs during the pilot: a device-compliance or location policy can block elevation in ways that look like a product fault."],
    "rec": ["ca-report-only-first"], "tools": [], "src": S("abr_win_set", "abr_sso", "abr_ed"),
    "marker": "official"},
   {"t": "Lock down what elevation may touch",
    "check": "Lockdown settings for admin rights, Run As Admin, Admin Session, device owner and Intune compliance are set per persona, and the excluded-accounts list contains only named break-glass or service accounts",
    "do": ["`Lockdown > ADMIN RIGHTS`: `Revoke admin rights` (on by default) demotes every account to standard user at logon except those listed in `Excluded accounts` (domain accounts as `DOMAIN\\name`).",
           "`Lockdown > RUN AS ADMIN` and `ADMIN SESSION`: `Deny elevating system files` blocks elevated `cmd.exe`, `regedit.exe` and other System32 binaries (define exceptions as pre-approvals); `Deny system file subprocesses` (client 8.3+) closes the child-process route; `Deny PIN code unlock` removes the offline PIN path.",
           "In `ADMIN SESSION` turn on `Force applications close at end`. If you allow `Allow session extension` (client 9.0+), cap `Extensions` (1–5) and `Minutes`; an extension resets the remaining time rather than adding to it and is logged.",
           "`Lockdown > OWNER`: `Lock device to owner` restricts elevation to the device owner, set automatically after a 24-hour stand-down from install. `Lockdown > INTUNE`: `Device must be compliant` blocks elevation on non-compliant devices (requires the Entra ID Connector).",
           "During an Admin Session the user cannot create or change accounts or uninstall the client, and the client restores its own files if they are tampered with — but Support Assist remains a legitimate admin path, so set its force-close timer too."],
    "pit": ["`Device must be compliant` makes the compliance policy a hard dependency of elevation. A device stuck in non-compliant state now also loses its escape hatch — fix compliance evaluation first.",
            "Excluded accounts are standing admins by definition. Review the list quarterly."],
    "rec": ["intune-compliance-baseline", "intune-devices-stay-noncompliant"], "tools": [], "src": S("abr_win_set", "abr_win_inst"),
    "marker": "official"},
   {"t": "Give each persona its sub-setting",
    "check": "Each persona group has a sub-setting whose differences from global settings are written down in one line each",
    "do": ["Office staff: Run As Admin with reason, approval on, no Admin Session — most of their needs will be covered by pre-approvals and machine-learning approvals.",
           "Developers and engineers: Run As Admin with reason but without approval for signed toolchains, Admin Session with approval and MFA, short access time.",
           "IT support: Admin Session with MFA (account separation if your audit framework requires it), longer access time, system-file elevation allowed.",
           "External staff and shared devices: both elevation types off; IT uses Support Assist or Break Glass when needed."],
    "pit": ["Copying the developer sub-setting to 'power users' is how standing admin creeps back. Every new sub-setting needs an owner and a reason."],
    "rec": ["pim-least-privilege-daily-ops"], "tools": [], "src": S("abr_approval", "abr_win_set"),
    "marker": "practical"},
  ]},

 {
  "id": "appcontrol", "title": "Application control and malware scanning", "time": "1–2 days, then ongoing", "deep": False,
  "goal": "Known-good software elevates without friction, known-bad software never elevates, and unknown files are checked before they run elevated.",
  "steps": [
   {"t": "Configure malware detection before the first elevation",
    "check": "`Real-time detection` and `Cloud scan unknown files` are set according to your data policy, the `Action` is chosen, and malware notifications reach the SOC",
    "do": ["Under `Windows Settings > Malware > DETECT`, Run As Admin requests are checked against OPSWAT MetaDefender: `Real-time detection` compares the file checksum with known results, and `Cloud scan unknown files` uploads files with no known result for multi-engine scanning. Both default to on.",
           "Choose the `Action` for detections: `Quarantine` (IT can review and decide) or `Permanently block`.",
           "Optionally set `Blackout period (minutes)` (client 9.0+) so a user cannot start new elevations for a while after a detection on their device.",
           "Send malware notifications to the SOC mailbox under `Malware > NOTIFICATION`, or better, push audit events into the SIEM (phase 8)."],
    "pit": ["Cloud scanning uploads unknown files to a third-party service. Internal tools and installers with confidential content may be among them — decide in your privacy assessment whether that is acceptable, or turn cloud scanning off and rely on checksum lookups plus local antivirus."],
    "rec": [], "tools": [], "src": S("abr_win_set"),
    "marker": "official"},
   {"t": "Pre-approve known-good software with rename-proof protection",
    "check": "The common installers and admin tools of each persona are pre-approved with a protection other than `No protection`, and trivial entries do not flood the audit log",
    "do": ["Under `App Control > PRE-APPROVE` add entries by type: single application, vendor (digital certificate), location (folder tree, including read-only UNC shares), or `Force running application elevated` for legacy apps that always need admin.",
           "Pick a `Protection` that defeats renaming: a read-only directory (recommended for installed apps, version-independent), certificate plus application or file name (good for downloaded installers), or checksum (exact but version-bound). Avoid `No protection` outside tests.",
           "Use the advanced options deliberately: `User confirmation`, `Log to auditlog` (only available when confirmation is on) and `Block subprocesses`.",
           "The fastest way to build the list is from the audit log during the pilot: each Run As Admin entry links straight to a pre-filled pre-approval or block entry.",
           "Server pre-approvals live under Windows Server settings; workstation entries do not apply to servers."],
    "pit": ["A vendor-certificate pre-approval trusts everything that vendor signs, including tools that are dangerous in the wrong hands. Prefer application-level entries for vendors that ship admin utilities."],
    "rec": [], "tools": [], "src": S("abr_win_set", "abr_approval", "abr_ed"),
    "marker": "official"},
   {"t": "Block the dangerous, then tune machine learning and AI approval",
    "check": "Block rules cover tools you never want elevated, and the machine-learning and AI approval thresholds are set consciously rather than left at defaults",
    "do": ["`App Control > BLOCK` stops named files, vendors or locations from running as administrator, with an optional message to the user. Attempts are audited.",
           "`App Control > MACHINE LEARNING` is on by default with `Approvals` set to 1: once an application has been approved manually that many times, later requests for it are auto-approved. Raise the threshold if a single approver's mistake should not become a tenant-wide rule.",
           "`App Control > AI APPROVAL` (off by default) auto-approves Run As Admin requests whose app or vendor reputation score meets your threshold (0–100). Use the audit log, which shows the scores for each elevation, to pick a threshold before you enable it.",
           "Sub-settings can override both auto-approval mechanisms, so you can keep them off for sensitive personas."],
    "pit": ["On macOS, block rules can be created in the portal but are currently not enforced by the client after an operating-system change; restrict macOS through pre-approval scoping instead.",
            "Remember the boundary: blocking elevation does not stop a portable tool from running as the user. Use App Control for Business for execution control."],
    "rec": [], "tools": [], "src": S("abr_win_set", "abr_audit", "abr_ed", "ms_wdac"),
    "marker": "official"},
  ]},

 {
  "id": "deploy", "title": "Deploy the agent with Intune (Windows and macOS)", "time": "1–2 days", "deep": True,
  "goal": "The tenant-specific agent installs silently on every in-scope Windows and macOS device, reports to the portal inventory, and only one mechanism owns agent versions.",
  "lead": "Configure phases 2–5 before the first install: the agent applies tenant settings — including `Revoke admin rights` — as soon as it connects.",
  "steps": [
   {"t": "Package the Windows client as a Win32 app",
    "check": "A Win32 app with a file-version detection rule installs the MSI in system context, and the uninstall command works on any installed version",
    "do": ["Download the Windows Workstation MSI from the portal's Download menu. The installer is licensed to your tenant only; devices installed from it appear in your inventory and nowhere else.",
           "Wrap it with the Content Prep Tool, pointing `-c` at the folder and `-s` at the MSI: `IntuneWinAppUtil.exe -c C:\\ABRInstall -s \"<downloaded file>.msi\" -o C:\\ABRInstall`.",
           "Install command: `msiexec /i \"<downloaded file>.msi\" /qn` with the exact packaged file name (portal names contain spaces and version numbers). Install behaviour: System.",
           "Replace Intune's pre-filled product-code uninstall with the version-independent command from the vendor: `powershell.exe -command \"Get-Package -Name 'Admin By Request Workstation' | Uninstall-Package -AllVersions -Force\"`.",
           "Detection rule: file `AdminByRequest.exe` in `C:\\Program Files (x86)\\FastTrack Software\\Admin By Request`, String (version), greater than or equal to the full four-part version of the MSI you packaged."],
    "pit": ["Do not use the MSI product-code detection rule: the code changes with every release, so after an auto-update Intune thinks the app is missing and keeps reinstalling the old package.",
            "The Workstation MSI will not install on Windows Server and vice versa. Azure Virtual Desktop and Windows Enterprise multi-session hosts need the Server edition.",
            "Step-by-step packaging, requirements, assignments, supersedence, IME logs and error codes are in the companion guide: Package Admin By Request for Intune."],
    "rec": [], "tools": [], "guides": ["admin-by-request-intune-win32-packaging"], "src": S("abr_win_inst", "abr_intune", "abr_ed", "ms_win32", "ms_win32_prep"),
    "marker": "official"},
   {"t": "Decide who owns agent versions: Intune or Auto-Update",
    "check": "Exactly one mechanism updates the agent on each platform, and the Intune app is aligned with that decision",
    "do": ["Auto-update over the internet is on by default per platform under `Settings > Tenant Settings > Auto-Update`; the vendor typically pushes new versions in bulk four to eight weeks after general availability.",
           "If Intune should own versions, disable auto-update for Windows Workstation and supersede the Win32 app at each release. If Auto-Update owns them, use the Intune app for new installs only and re-package at major releases.",
           "A LAN update option pulls the client from a UNC path readable by `Domain Computers`; it suits estates that cannot reach the internet update service.",
           "Server auto-updates are opt-in and paced by the vendor after confirmation with you."],
    "pit": ["Running both mechanisms produces version flapping and detection failures that look like broken installs."],
    "rec": [], "tools": [], "src": S("abr_tenant", "abr_intune", "abr_ed"),
    "marker": "official"},
   {"t": "Open the network path and handle proxies",
    "check": "Pilot devices show `Operational Status` and `Cloud Connectivity` as OK in the client's Connectivity panel from office, VPN and home networks",
    "do": ["The agent talks outbound on TCP 443 to the API hosts of your data region: `api1` (Netherlands), `api2` (US East), `api3` (UK), `api4` (Germany), `api5` (US West) or `api6` (Singapore) under `adminbyrequest.com`, with matching `macapiN` and `linuxapiN` hosts for macOS and Linux. `api.adminbyrequest.com` works everywhere but is less direct.",
           "If the user has a proxy configured, the client passes it to its service, which uses it without authentication as the computer account. Authenticated-only proxies therefore need an exception for these hosts.",
           "Break Glass, Unattended Access and Remote Support additionally need outbound WebSocket (MQTT) connectivity on 443 to the vendor's regional `azure-devices.net` hubs, and Secure Remote Access browsers need the regional cloud gateways; add them only if you use those features."],
    "pit": ["TLS-inspecting proxies frequently break agent traffic. Exclude the API hosts from inspection rather than debugging certificate errors device by device."],
    "rec": [], "tools": [], "src": S("abr_net", "abr_ui"),
    "marker": "official"},
   {"t": "Deploy the macOS client: profile first, package second",
    "check": "On target Macs the EPM configuration profile reports success before the package installs, and the menu-bar icon shows a standard user after install",
    "do": ["Deploy the vendor's `Admin By Request - EPM.mobileconfig` first. It pre-approves the background items and system extension and grants Full Disk Access, so users see no prompts.",
           "If you previously used the older separate FDA and system-extension profiles, remove them before deploying the combined profile instead of layering the new one on top.",
           "When the profile has succeeded, deploy the tenant-specific package as a required macOS app in Intune. Officially supported macOS versions at the time of writing: 15, 26 and 27.",
           "Client activity and errors are written to `/var/log/adminbyrequest.log`."],
    "pit": ["Installing the package before the profile lands can leave Full Disk Access unrecognised until a reboot.",
            "The vendor flags its older Intune-specific Mac profile walkthrough as being rewritten; follow the Mac install page for the current profile."],
    "rec": [], "tools": [], "src": S("abr_mac_inst", "abr_intune", "ms_mac_lob", "ms_catalog"),
    "marker": "official"},
  ]},

 {
  "id": "rollout", "title": "Pilot, remove existing local admins, roll out in waves", "time": "3–6 weeks", "deep": True,
  "goal": "A pilot has produced the pre-approval list and persona tuning, every device in scope has no standing admins except named exceptions, and the rollout ran in waves without a ticket spike.",
  "steps": [
   {"t": "Run an observe-then-enforce pilot",
    "check": "A pilot of 20–50 users across all personas has run for at least two weeks, first observing then enforcing, and its audit data has been turned into pre-approvals and sub-setting changes",
    "do": ["Scope a pilot sub-setting to a pilot group. For the first week you can leave `Revoke admin rights` off for that group: the audit log marks administrators in red, so you see whose rights will change and start collecting elevation data before anything is taken away.",
           "Then switch revocation on for the pilot, with approval enabled, and let approvers work from the mobile app. Every approval is a candidate pre-approval.",
           "Watch three numbers: requests per user per week, median approval time, and denied requests that turned into tickets. They decide whether a persona needs more pre-approvals or a different elevation type."],
    "pit": ["A pilot made only of IT staff proves nothing about finance or engineering. Recruit from every persona."],
    "rec": [], "tools": [], "src": S("abr_audit", "abr_approval", "abr_app"),
    "marker": "practical"},
   {"t": "Remove existing local admins and stop new ones appearing",
    "check": "On enforced devices the local Administrators group contains only the built-in account (managed by LAPS or disabled), named exclusions and intended Entra roles; new Entra joins no longer add the user",
    "do": ["Admin By Request's `Revoke admin rights` demotes users at logon. It deliberately leaves domain administrators on domain-joined devices and users holding the Microsoft Entra Joined Device Local Administrator role, so clean up those role and group assignments as well.",
           "Stop the source: set the Entra device registration policy so the registering user is not added as local admin, and set Autopilot profiles to create standard users.",
           "If you also enforce the group with Intune's Local user group membership policy (`Add (Replace)` behaves like Restricted Groups), keep its member list consistent with the Admin By Request excluded accounts so the two tools do not fight.",
           "Manage the built-in Administrator with Windows LAPS (backup to Entra ID or AD) or disable it and rely on Admin By Request Break Glass accounts — but pick one recovery path and document it."],
    "pit": ["Admin By Request's own documentation compares Break Glass with legacy Microsoft LAPS. Windows LAPS now supports Entra ID and Intune natively, so evaluate the current product, not the old one.",
            "Keep IT staff's privileged work on separate admin identities managed with PIM; just-in-time local elevation does not replace tiered admin accounts."],
    "rec": ["pim-least-privilege-daily-ops", "autopilot-device-preparation-entra-join"], "tools": [], "sec": ["harden-windows-laps"],
    "src": S("abr_win_inst", "ms_localadmin", "ms_acctprot", "ms_laps", "ms_laps_entra", "abr_bg"),
    "marker": "official"},
   {"t": "Roll out in waves with communication and support ready",
    "check": "Each wave has a date, a communication sent beforehand, approvers on call for the first days, and a go/no-go based on the pilot metrics",
    "do": ["Wave by persona or department, smallest risk first, and assign the Win32 app to one Entra group per wave.",
           "Tell users what changes: they are no longer admins, how to use Run As Admin and the tray icon, how long approvals take, and where the code of conduct lives.",
           "Route request notifications into the ticketing system with the vendor's ticketing email template so service desk metrics include elevation requests.",
           "Expect a spike in requests in the first week of each wave; machine-learning approvals and new pre-approvals should flatten it by week two."],
    "pit": ["Rolling out during a release week for a major line-of-business app guarantees a burst of approval requests. Check the change calendar."],
    "rec": [], "tools": [], "src": S("abr_win_set", "abr_approval", "ms_win32"),
    "marker": "practical"},
  ]},

 {
  "id": "operate", "title": "Operate: audit, reporting, SIEM and proof that admin rights are gone", "time": "Ongoing", "deep": False,
  "goal": "Elevation activity is reviewed, streamed to the SIEM, and the absence of standing admin rights is proven with the same tools an attacker would use.",
  "steps": [
   {"t": "Work the audit log and stop risky sessions remotely",
    "check": "Approvers review the audit log weekly, and the team can terminate a running elevation from the portal",
    "do": ["The audit log separates Run As Admin, Admin Sessions and Server events; each entry shows installs, uninstalls and elevated processes, the reason, the settings that applied and the AI reputation scores.",
           "With Windows client 9.0+ or Mac client 6.0+, a running session or elevation can be killed remotely from the expanded audit entry, with an optional blackout (default 15 minutes) before the user may elevate again. The kill ends all elevations on that device and is itself audited.",
           "Export to PDF, XLSX or CSV for audits, and use the aggregated view to see which applications are elevated most — prime pre-approval candidates."],
    "pit": ["During a blackout the user only sees a generic 'denied by company policy' message. Tell them directly when you use it."],
    "rec": [], "tools": [], "src": S("abr_audit"),
    "marker": "official"},
   {"t": "Stream events to the SIEM and ticketing",
    "check": "Elevation requests, approvals and alerts arrive in the SIEM within minutes, and API keys and webhook endpoints have owners",
    "do": ["Create a webhook under `Settings > Tenant Settings > Data > WEBHOOKS` for audit-log entries, requests and events (all, warnings and alerts, alerts only, or specific events). Your endpoint must answer HTTP 200; allow the vendor's documented source IP for your region.",
           "For pull-based collection create an API key under `Data > API KEYS` and use your region's API host.",
           "Alert on at least: malware detections, Admin Sessions outside working hours, extensions of sessions, and elevations by members of the excluded-accounts list."],
    "pit": ["API keys are tenant-wide credentials. Keep them in a vault and disable unused ones; the portal lets you disable a key without deleting it."],
    "rec": [], "tools": [], "src": S("abr_tenant"),
    "marker": "official"},
   {"t": "Prove the result with offensive tooling and hardening checks",
    "check": "A repeat of the phase 1 measurement shows no standing local admin for everyday users, and the residual admin paths are documented exceptions",
    "do": ["Re-run the admin-path analysis from phase 1 (BloodHound CE, NetExec) from an authorised standard account and compare with the before-state.",
           "Run HardeningKitty against a sample of enforced devices to confirm UAC and related settings were not weakened during the project.",
           "Report the result as numbers: devices in scope, users with standing admin before and after, median approval time, and top elevated applications."],
    "pit": ["A clean scan right after rollout says little about month six. Repeat the measurement quarterly."],
    "rec": [], "tools": ["bloodhound-ce", "netexec", "hardeningkitty"], "src": S("ms_lpam", "ms_uac"),
    "marker": "practical"},
  ]},

 {
  "id": "troubleshoot", "title": "Troubleshooting and rollback", "time": "Ongoing", "deep": False,
  "goal": "First-line staff can classify an elevation problem within minutes, and every change in this guide has a rehearsed, reversible way back.",
  "steps": [
   {"t": "Triage install, connectivity and policy problems",
    "check": "The runbook lists, in order: Intune device-level install status, client Connectivity panel, Diagnostics, licence count, applied sub-setting and local policy overrides",
    "do": ["Install: use the per-device status under the app in Intune rather than the overview, then confirm the program folder, a running `AdminByRequest.exe`, and MSI Installer entries in the Application event log.",
           "Connectivity: open the tray app, `About Admin By Request > Connectivity`, and check `Operational Status` and `Cloud Connectivity`. Submit Diagnostics from the same window before opening a vendor ticket.",
           "Device missing from inventory: check the licence count first; devices beyond it never appear.",
           "Unexpected behaviour: the audit entry names the sub-setting that applied. Then look for local overrides under `HKLM\\Software\\FastTrack Software\\Admin By Request\\Policies` — ADMX or registry policy always beats portal settings, and the vendor advises against it.",
           "macOS: read `/var/log/adminbyrequest.log` and confirm the configuration profile installed before the package."],
    "pit": ["A forgotten GPO from an earlier evaluation is the classic cause of 'the portal setting does nothing'."],
    "rec": [], "tools": [], "src": S("abr_intune", "abr_ui", "abr_pol", "abr_lic", "abr_mac_inst", "ms_monitor"),
    "marker": "official"},
   {"t": "Roll back safely, smallest step first",
    "check": "For a problem the team can, in order: relax the affected sub-setting, unlock a single device, and uninstall from a group — and knows how each device regains an admin path",
    "do": ["Portal changes reach endpoints in near real time, including off-network ones, so the first lever is the sub-setting: turn off approval or switch `Revoke admin rights` off for the affected group instead of uninstalling anything.",
           "For one stuck device, use the PIN code from that device's inventory record (unless `Deny PIN code unlock` is on) or a Break Glass account.",
           "To remove the agent from a group, assign the Intune app with the Uninstall intent; the PowerShell uninstall command removes whichever version is installed. `msiexec /x` with an older MSI fails with 1605 once the device has auto-updated.",
           "Before uninstalling at scale, make sure each device has a recovery admin path (Windows LAPS or a documented account). On macOS the vendor notes that a post-uninstall script may be needed to promote an account if every account was demoted.",
           "Never use tenant deletion as a rollback: it is irreversible and requires all endpoints to be uninstalled first."],
    "pit": ["Reverting by uninstalling hands standing admin rights back only to whoever is still in the Administrators group — which, after phase 7, should be nobody. Decide in advance who needs it."],
    "rec": [], "tools": [], "src": S("abr_approval", "abr_win_inst", "abr_mac_inst", "abr_tenant", "abr_bg"),
    "marker": "practical"},
  ]},
]
