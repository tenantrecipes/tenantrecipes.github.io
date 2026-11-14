"""Technical guide: OneDrive/SharePoint on unmanaged devices with
Defender for Cloud Apps session control — the 'Access ... is monitored' notice and the
download-blocked message, how to reproduce them deliberately, and what they do not cover.
Documentation checked against linked Microsoft Learn sources on 2026-11-10; not lab-tested.
Approved for publication by the editor on 2026-11-10; registered in build_site.py.
Revised 2026-11-11: user-facing messages described in text from Microsoft Learn only; no screenshots.
"""

SLUG = "mdca-session-control-unmanaged-devices"
TIER = "technical"
PUBLISHED = "2026-11-10"
VERIFIED = "2026-11-10"
UPDATED = "2026-11-12"
TITLE = "MDCA session control: OneDrive on unmanaged devices"
SHORT = "OneDrive on unmanaged devices"
DESC = (
    "How to deliberately produce the Defender for Cloud Apps monitored-access notice ('Access to … is "
    "monitored') and the download-blocked message for users on unmanaged devices: licensing, defining a managed "
    "device, a Conditional Access policy with Conditional Access App Control, Defender for Cloud Apps "
    "session policies filtered by device, file extension and sensitivity label, user messages, the "
    "SharePoint app-enforced alternative, the gaps it leaves, testing and rollback. Documentation "
    "verified against Microsoft Learn; not lab-tested."
)
BADGE = "documentation verified against Microsoft Learn; not lab-tested"
SRC_LABEL = "Microsoft sources"
TIME_NOTE = (
    "Time estimates are Tenant Recipes planning figures for a mid-size tenant that already has Intune "
    "compliance or hybrid join in place, not Microsoft numbers."
)
CTA_FIRST = "Start with the two messages users see →"

INTRO = [
    "A consultant finishes a workshop, gets home, and opens OneDrive on the web from a personal laptop "
    "to check one last thing. A project folder is right there. One click on Download, and a .zip with "
    "customer documents is now in the Downloads folder of a machine your organisation has never seen: "
    "no compliance policy, no disk encryption you can verify, shared with the rest of the household, "
    "and synced to who knows which personal cloud backup.",
    "Nobody broke a rule on purpose, and nothing alerts. You find out weeks later — if you find out at "
    "all — when someone asks where a file came from. If that sounds like something that could happen in "
    "your tenant tomorrow, this guide is for you.",
    "Microsoft 365 can handle this moment differently. With Microsoft Entra Conditional Access and "
    "Microsoft Defender for Cloud Apps, a browser session from an unmanaged device can be routed "
    "through session control. The user first sees a notice that access is monitored and only "
    "available from a web browser. If they then try to download a file your policy covers — say any "
    ".zip, or anything labelled Confidential — the download is blocked with a message you write "
    "yourself, while viewing and working in the browser can continue.",
    "That last part matters. A good policy keeps data in, but it also guides people: it tells them "
    "what is happening, why, and what to do instead (open it in the browser, use a managed laptop, "
    "ask the service desk). A silent block teaches users to look for workarounds; a clear message "
    "teaches them where the line is.",
    "This guide shows how to deliberately produce both the monitored-access notice and the "
    "download-blocked message, how to choose between Defender for "
    "Cloud Apps session control and the simpler SharePoint/OneDrive app-enforced restrictions, and "
    "— just as important — what these controls do not protect against. Everything is checked against "
    "the linked Microsoft Learn articles; nothing here claims lab testing by Tenant Recipes.",
]

NAMING = (
    "Scope: Microsoft 365 commercial tenants using Microsoft Entra ID, SharePoint Online and "
    "OneDrive for Business, with browser access from devices that are not Intune compliant or "
    "Microsoft Entra hybrid joined. Product and portal labels change (Azure AD → Microsoft Entra, "
    "Microsoft 365 Defender → Microsoft Defender XDR, 'cloud apps' → 'resources'); prefer the linked "
    "Learn articles when a label differs. Tenant Recipes is not affiliated with Microsoft. "
)

NOTICE = {
    "title": "Evidence boundary",
    "text": (
        "Every configuration step is taken from the Microsoft Learn articles linked under each step. "
        "The exact wording of the end-user messages depends on whether the session runs "
        "through Microsoft Edge for Business in-browser protection or the reverse proxy, and on any "
        "custom text you configure; where Learn does not document the exact default wording we say "
        "so in 'What is not verified'. The opening scenario is a generic illustration, not a case "
        "study, and no figures or statistics are implied."
    ),
}

HISTORY = [
    ("2026-11-11", "Rewrote user-facing message descriptions; no screenshots. The monitored-access notice and the download-blocked message are now described in text from Microsoft Learn only, with the documented wording quoted and sourced; undocumented wording stays under 'What is not verified'."),
    ("2026-11-10", "Draft technical guide: reproduce the monitored-session notice and blocked-download message for OneDrive on unmanaged devices with Defender for Cloud Apps; documentation verified, not lab-tested."),
]


def S(*keys):
    return [L[k] for k in keys]


L = {
    "mdca_session": (
        "Microsoft Learn: Create session policies (Defender for Cloud Apps)",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/session-policy-aad",
    ),
    "mdca_caac": (
        "Microsoft Learn: Conditional Access app control in Defender for Cloud Apps",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/proxy-deployment-aad",
    ),
    "mdca_edge": (
        "Microsoft Learn: In-browser protection with Microsoft Edge for Business",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/in-browser-protection",
    ),
    "mdca_tut": (
        "Microsoft Learn: Block download of sensitive information with Conditional Access app control",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/use-case-proxy-block-session-aad",
    ),
    "mdca_ts": (
        "Microsoft Learn: Troubleshoot access and session controls for admins",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/troubleshooting-proxy",
    ),
    "mdca_devid": (
        "Microsoft Learn: Identity-managed devices with Conditional Access app control",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/conditional-access-app-control-identity",
    ),
    "mdca_access": (
        "Microsoft Learn: Create access policies (Defender for Cloud Apps)",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/access-policy-aad",
    ),
    "mdca_stepup": (
        "Microsoft Learn: Require step-up authentication (authentication context) upon risky action",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/tutorial-step-up-authentication",
    ),
    "mdca_start": (
        "Microsoft Learn: Get started with Microsoft Defender for Cloud Apps",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/get-started",
    ),
    "sd_defender": (
        "Microsoft Learn: Microsoft Defender service description (Defender for Cloud Apps plans)",
        "https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-365-service-descriptions/microsoft-365-tenantlevel-services-licensing-guidance/microsoft-defender-service-description",
    ),
    "mdca_editions": (
        "Microsoft Learn: Discovery capability differences for Defender for Cloud Apps and Cloud App Discovery",
        "https://learn.microsoft.com/en-us/defender-cloud-apps/editions-cloud-app-security-aad",
    ),
    "lic_suites": (
        "Microsoft Licensing: Enterprise Security Suites (Defender Suite, formerly Microsoft 365 E5 Security)",
        "https://www.microsoft.com/licensing/guidance/Security-Suites",
    ),
    "ts_monitored": (
        "Microsoft Learn (troubleshoot): Users are redirected when browsing to a SharePoint or OneDrive site",
        "https://learn.microsoft.com/en-us/troubleshoot/sharepoint/administration/access-to-sharepoint-online-is-monitored",
    ),
    "spo_unmanaged": (
        "Microsoft Learn: Control access from unmanaged devices (SharePoint and OneDrive)",
        "https://learn.microsoft.com/en-us/sharepoint/control-access-from-unmanaged-devices",
    ),
    "ca_session": (
        "Microsoft Learn: Conditional Access session controls",
        "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-session",
    ),
    "ca_filters": (
        "Microsoft Learn: Conditional Access filter for devices",
        "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-condition-filters-for-devices",
    ),
    "ca_conditions": (
        "Microsoft Learn: Conditional Access conditions (client apps, supported browsers)",
        "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-conditions",
    ),
    "ca_reportonly": (
        "Microsoft Learn: Conditional Access report-only mode",
        "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-report-only",
    ),
    "ca_compliance": (
        "Microsoft Learn: Require a compliant device, hybrid joined device or MFA for all users",
        "https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-all-users-device-compliance",
    ),
    "ca_legacy": (
        "Microsoft Learn: Block legacy authentication with Conditional Access",
        "https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-block-legacy-authentication",
    ),
    "ca_signinlog": (
        "Microsoft Learn: View applied Conditional Access policies in sign-in logs",
        "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/how-to-view-applied-conditional-access-policies",
    ),
    "intune_app": (
        "Microsoft Learn: App protection policies overview (Intune)",
        "https://learn.microsoft.com/en-us/intune/intune-service/apps/app-protection-policy",
    ),
}

# ---------------------------------------------------------------------------
# Recurring editorial boxes. There is no dedicated renderer for these yet
# (GUIDES.md: "Then: ... recurring editorial boxes"), so they are exposed as
# EDITORIAL_BOXES for a future renderer AND rendered today through PROBLEM.
# ---------------------------------------------------------------------------
BOX_WHY = [
    "It meets users where the risk actually happens. Many people opening OneDrive from a home laptop are "
    "not trying to steal anything; they want to read a file. Session control lets them do that in the "
    "browser while stopping the one action — the download to an unmanaged disk — that moves the file "
    "outside your control.",
    "It is granular. A Defender for Cloud Apps session policy can block only what matters (for example "
    ".zip archives, or files with a given sensitivity label) instead of every download, and it can "
    "label-and-protect files on download instead of blocking them (Protect action, Microsoft Purview "
    "required).",
    "It explains itself. The monitored-access notice and a customised block message tell users what is "
    "happening and what to do next. Microsoft Learn explicitly recommends educating users with a "
    "custom message when they hit a policy, for example how to enroll a device.",
    "It leaves an audit trail. Sessions routed through Conditional Access App Control appear in the "
    "Defender for Cloud Apps activity log and policy reports, so you can see who was blocked, from which "
    "kind of device, and on which file.",
]
BOX_ALT = [
    "Choose SharePoint/OneDrive app-enforced restrictions ('Allow limited, web-only access') when you "
    "only need 'no download, print or sync on unmanaged devices' for SharePoint and OneDrive, you have no "
    "Defender for Cloud Apps licences, or you want the simplest possible setup. It needs only Entra ID P1 "
    "Conditional Access and the SharePoint admin center, but it cannot filter by file extension or label, "
    "has no custom block message, and changes can take up to 24 hours.",
    "Choose plain Conditional Access blocking (require a compliant or hybrid joined device, no browser "
    "exception) when unmanaged access should not exist at all — for example for administrators, finance "
    "or regulated data. Monitoring is pointless if the answer is always 'no'.",
    "Choose Intune app protection policies (MAM) for personal phones and tablets: they protect data inside "
    "the Office mobile apps, which browser session control does not cover.",
    "Choose Purview DLP and sensitivity labels with encryption when the requirement is 'the file must stay "
    "protected wherever it ends up', including on managed devices and after a legitimate download.",
    "Choose Microsoft Entra Private Access, VDI/Windows 365 or a managed browser strategy when people "
    "regularly need full desktop-app productivity from devices you do not manage; session control is "
    "browser-only by design.",
]
BOX_UNVERIFIED = [
    "Exact default wording of the download-blocked message. Microsoft Learn documents only that a "
    "'Download restricted' message appears and that the downloaded file is replaced by a text file whose "
    "message you can configure (reverse proxy). Learn does not publish the full default text of that "
    "message or of the replacement file, and does not quote the Edge for Business in-browser block text. "
    "We therefore do not quote any default block wording; expect it to differ by delivery path and over time.",
    "Options on the monitored-access notice beyond 'Continue'. Learn documents the notification on/off "
    "switch, default versus custom message and a Preview link (Settings > Cloud apps > Conditional Access "
    "App Control > User monitoring), and quotes only a 'Continue to …' link on the notice. Whether the "
    "notice offers other options (for example suppressing it for a period) is not documented on Learn; "
    "use Preview in your own tenant.",
    "Exact notice text for OneDrive. Learn quotes only the SharePoint variant, and says the message "
    "'resembles' that text. We assume the OneDrive variant substitutes the app name; the exact OneDrive "
    "wording is not documented on Learn.",
    "Label names in the portals. Learn uses both 'Hybrid Azure AD joined' and 'Microsoft Entra hybrid "
    "joined' for the same Defender for Cloud Apps device tag, and 'Monitor only' / 'Block downloads' are "
    "shown as Preview in some tenants. App names in the session policy App filter (for example "
    "'Microsoft OneDrive for Business', 'Microsoft SharePoint Online') may differ slightly.",
    "Built-in 'Block downloads' scope. Learn says the built-in Conditional Access options Monitor only and "
    "Block downloads 'apply and enforce the Defender for Cloud Apps proxy' and that complex policies need "
    "Use custom policy. Learn does not list exactly which download paths the built-in option covers, or "
    "whether it can be filtered by file type; we therefore use a custom session policy for the .zip case.",
    "Licensing edge cases. Learn's service description lists the plans that include Defender for Cloud "
    "Apps and says Conditional Access App Control also needs Entra ID P1. Whether Office 365 Cloud App "
    "Security / Microsoft 365 Cloud App Security alone supports this scenario was not verified for this "
    "draft — confirm with your licensing partner.",
    "'Anyone' links. Learn states that 'Anyone' links are not affected by the SharePoint app-enforced "
    "unmanaged-device policy. Learn does not state the Defender for Cloud Apps behaviour explicitly; "
    "since Conditional Access evaluates sign-ins and an 'Anyone' link needs no sign-in, assume session "
    "control does not apply and restrict 'Anyone' links separately.",
    "Report-only behaviour for this policy type. Learn says report-only does not enforce session controls; "
    "we did not find Learn guidance on how much Defender for Cloud Apps telemetry a report-only policy with "
    "Use Conditional Access App Control produces. Plan to pilot with a small group in On mode.",
]

EDITORIAL_BOXES = [
    {"kind": "why", "title": "Why we recommend this", "items": BOX_WHY},
    {"kind": "alt", "title": "When to choose something else", "items": BOX_ALT},
    {"kind": "unverified", "title": "What is not verified", "items": BOX_UNVERIFIED},
]

PROBLEM = {
    "title": "The problem: files that quietly leave on someone else's laptop",
    "blocks": [
        ("Why unmanaged devices are different",
         ["A device you do not manage gives you no assurance about disk encryption, patch level, malware "
          "protection, who else uses it, or where its Downloads folder is backed up. Once a file is "
          "downloaded there, your retention, DLP and revocation options largely stop at the device boundary.",
          "Blocking all unmanaged access is safe but often unrealistic for consultants, partners and staff "
          "working from home. Allowing everything is easy and invisible. The middle ground is to allow "
          "browser access, make it visible, and stop the specific actions that move data out."]),
        ("What users see: the monitored-access notice and the download block",
         ["The monitored-access notice is a page the user meets before the app opens. It tells them that "
          "access to the app is monitored, that their organisation allows access in monitor mode for "
          "improved security, and that access is only available from a web browser. It ends with a link to "
          "continue to the app. Microsoft Learn quotes the SharePoint variant as a message that resembles: "
          "'Access to Microsoft SharePoint Online is monitored. For improved security, your organization "
          "allows access to Microsoft SharePoint Online in monitor mode. Access is only available from a web "
          "browser.' followed by the link 'Continue to Microsoft SharePoint Online' (source: Microsoft Learn, "
          "'Users are redirected when browsing to a SharePoint or OneDrive site', "
          "https://learn.microsoft.com/en-us/troubleshoot/sharepoint/administration/access-to-sharepoint-online-is-monitored). "
          "It comes from Defender for Cloud Apps user monitoring and appears when a Conditional Access policy "
          "routes the session to Conditional Access App Control and 'Notify users that their activity is "
          "being monitored' is on; you can use the default message or write your own.",
          "The download-blocked message appears when the user tries to download a file that a Defender for "
          "Cloud Apps session policy (or the built-in Block downloads option in Conditional Access) covers — "
          "in our example a .zip on an unmanaged device. Microsoft Learn documents that 'a Download restricted "
          "message appears for the user, and the downloaded file is replaced with a text file', and that you "
          "configure the text file's message for your organisation (source: Microsoft Learn, 'Create session "
          "policies', https://learn.microsoft.com/en-us/defender-cloud-apps/session-policy-aad). In other words "
          "the user gets a notice in the browser and, in reverse-proxy sessions, a small text file in place of "
          "the file they asked for. Learn does not publish the full default wording of either, so we do not "
          "quote one; see 'What is not verified'.",
          "You recognise both messages from this description and confirm them in the logs — the Microsoft "
          "Entra sign-in log and the Defender for Cloud Apps activity log — not from pictures. This guide "
          "contains no screenshots."]),
        ("Why we recommend this", BOX_WHY),
        ("When to choose something else", BOX_ALT),
        ("What is not verified", BOX_UNVERIFIED),
    ],
    "src": S("ts_monitored", "mdca_session", "mdca_caac", "spo_unmanaged"),
}

PHASES = [
    {
        "id": "decode",
        "title": "Understand the two messages users see",
        "time": "30–60 minutes",
        "deep": True,
        "goal": "From the description of the messages and two log views (Entra sign-in log and Defender for Cloud Apps activity log), you can tell exactly which policy produced the monitored-access notice and the blocked download.",
        "lead": "Before you build anything, learn to recognise the two messages from their description and from the logs (activity log and audit) — not from attached images — and understand what produced them, in your own tenant or in someone else's.",
        "steps": [
            {
                "t": "The monitored-access notice",
                "check": "Team can explain that the notice comes from Defender for Cloud Apps user monitoring after a Conditional Access policy applied Conditional Access App Control",
                "do": [
                    "Learn documents the notice as: 'Access to Microsoft SharePoint Online is monitored. For improved security, your organization allows access to Microsoft SharePoint Online in monitor mode. Access is only available from a web browser.' followed by a 'Continue to Microsoft SharePoint Online' link. Learn says the message 'resembles' this text; for OneDrive the app name differs.",
                    "Cause per Learn: a Defender for Cloud Apps policy applies to the user's session, so the session is routed to session control instead of directly to the app.",
                    "Two delivery paths: users in Microsoft Edge for Business (work profile) get in-browser protection with a lock icon (briefcase symbol in the lock pane) and no URL change; other browsers are reverse-proxied and the URL gains a suffix such as `*.mcas.ms`.",
                    "The notice is controlled in the Microsoft Defender portal: Settings > Cloud apps > Conditional Access App Control > User monitoring ('Notify users that their activity is being monitored', default or custom message, Preview).",
                ],
                "pit": [
                    "A user can see this notice from a tenant that is not yours — for example as a B2B guest in a partner's OneDrive. Check whose tenant the URL belongs to before you start troubleshooting your own policies.",
                    "Turning the notification off hides the notice but keeps the monitoring. Decide deliberately; we recommend keeping it on (see the user-messaging step).",
                ],
                "src": S("ts_monitored", "mdca_session", "mdca_caac", "mdca_edge"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "The download-blocked message",
                "check": "Team can explain that the block comes from a session policy with Block action (or the built-in Block downloads) and where its message text is configured",
                "do": [
                    "Session policy type 'Control file download (with inspection)' with action Block prevents downloads that match the file filters. In reverse-proxy sessions Learn says a 'Download restricted' message appears and the downloaded file is replaced by a text file whose message you can configure.",
                    "Block policies let you notify users by email and customise the block message — this is where a guiding message ('open it in the browser, or use your managed laptop') belongs.",
                    "In Microsoft Edge for Business, block/monitor of file download is one of the policy types served by in-browser protection, so the block is enforced inside the browser instead of through the reverse proxy. Learn does not quote the Edge message text (see What is not verified).",
                    "The Conditional Access session control 'Use Conditional Access App Control' also offers the built-in options Monitor only and Block downloads; for filtered policies (file type, label) choose Use custom policy and build the session policy in Defender for Cloud Apps.",
                ],
                "pit": [
                    "When two session policies match, the more restrictive wins — an audit policy will not 'cancel' a block policy.",
                ],
                "src": S("mdca_session", "mdca_edge", "mdca_ts"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Trace a real event in the logs",
                "check": "For one test sign-in you have the Entra sign-in log entry showing the Conditional Access policy with App Control, and the matching Defender for Cloud Apps activity",
                "do": [
                    "Microsoft Entra sign-in logs: open the sign-in and review the Conditional Access tab for the policy that applied 'Use Conditional Access App Control'. The Device info tab shows whether the device was seen as compliant or hybrid joined.",
                    "Microsoft Defender portal > Cloud apps > Activity log (https://security.microsoft.com/cloudapps/activity-log): filter by user, app and time and open the blocked activity to see which session or access policy matched.",
                    "Policy management > select the session policy to open its policy report: it shows which sign-ins were redirected and which files were downloaded or blocked.",
                ],
                "pit": [
                    "If neither the `.mcas.ms` suffix nor the Edge lock indicator is present and a whole site is blocked, Learn points to a different cause: an app marked Unsanctioned and enforced through Defender for Endpoint.",
                ],
                "src": S("mdca_ts", "ca_signinlog", "mdca_session"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
        ],
    },
    {
        "id": "prereqs",
        "title": "Licensing and choosing the right control",
        "time": "1–2 hours",
        "deep": True,
        "goal": "Licences are confirmed for every in-scope user and you have consciously chosen Defender for Cloud Apps session control, SharePoint app-enforced restrictions, or both.",
        "lead": "Session control is the more capable tool; app-enforced restrictions are the simpler one. Pick on purpose.",
        "steps": [
            {
                "t": "Confirm licensing from the service description",
                "check": "Every user in scope has a Defender for Cloud Apps entitlement and Entra ID P1 (or a plan that includes them); Purview entitlement confirmed if you plan to use Protect/labels",
                "do": [
                    "Learn's Microsoft Defender service description: Defender for Cloud Apps is available standalone and as part of Enterprise Mobility + Security E5; Microsoft 365 E5/A5/G5 and Microsoft Defender Suite; Microsoft Purview Suite; and Microsoft 365 E5/F5/G5 Information Protection and Governance (plus EDU/GOV/FLW variants as listed).",
                    "Microsoft's licensing guidance names Microsoft Defender Suite as 'previously Microsoft 365 E5 Security'.",
                    "To use Conditional Access App Control, users must also be licensed for Microsoft Entra ID P1 (included in EMS E3/E5, Microsoft 365 E3/E5 and others per the service description).",
                    "Get started (Learn): obtain a Defender for Cloud Apps licence for each user you want protected.",
                    "The Protect action (label on download) requires a Microsoft Purview licence and the Information Protection integration enabled; the troubleshooting article lists this as the cause when Protect is greyed out.",
                ],
                "pit": [
                    "Microsoft 365 E3 includes Cloud App Discovery, not full Defender for Cloud Apps — do not assume E3 can do session control.",
                    "If the 'Use Conditional Access App Control' option is missing in the Conditional Access policy, Learn's first check is licensing: Entra ID P1 plus a valid Defender for Cloud Apps licence.",
                ],
                "src": S("sd_defender", "lic_suites", "mdca_start", "mdca_editions", "mdca_ts"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Choose session control, app-enforced restrictions, or both",
                "check": "Decision record states which control protects which data, for which users, and why",
                "do": [
                    "Defender for Cloud Apps session control: filter by device tag, file extension, file name, size and sensitivity label; block, audit or protect (label) downloads; block copy/cut/paste and print; custom messages; works across Entra-integrated apps, not only SharePoint/OneDrive.",
                    "SharePoint/OneDrive app-enforced restrictions ('Allow limited, web-only access'): users on unmanaged devices get browser-only access with no download, print or sync, and cannot open content in Office desktop apps; optional read-only or Office-only preview. No file-type targeting and no custom message.",
                    "Both rely on Conditional Access. App-enforced restrictions use the Conditional Access session control 'Use app enforced restrictions'; session control uses 'Use Conditional Access App Control'.",
                    "A common pattern is app-enforced restrictions as the tenant-wide floor, plus Defender for Cloud Apps session policies where you need finer control, labels or other apps. Test the combination with a pilot group before relying on it.",
                ],
                "pit": [
                    "App-enforced restrictions only cover SharePoint and OneDrive. Learn notes that blocking only SharePoint creates odd results (Teams chat works, the Files tab does not) and recommends a policy on the Office 365 app for broader control.",
                ],
                "src": S("spo_unmanaged", "ca_session", "mdca_session", "mdca_caac"),
                "rec": [],
                "tools": [],
                "guides": ["enterprise-ai-governance"],
                "marker": "official",
            },
            {
                "t": "If you choose the SharePoint route: allow limited, web-only access",
                "check": "Access control > Unmanaged devices set to 'Allow limited, web-only access' (or per-site via PowerShell) and 'Apps that don't use modern authentication' blocked",
                "do": [
                    "SharePoint admin center > Policies > Access control > Unmanaged devices > Allow limited, web-only access > Save. This creates Conditional Access policies for you and disables earlier policies created from that page.",
                    "PowerShell equivalent: `Set-SPOTenant -ConditionalAccessPolicy AllowLimitedAccess`. Options: `-AllowEditing $false`, `-ReadOnlyForUnmanagedDevices $true`, `-LimitedAccessFileType OfficeOnlineFilesOnly | WebPreviewableFiles | OtherFiles`.",
                    "Per site or per OneDrive: `Set-SPOSite -Identity <url> -ConditionalAccessPolicy AllowLimitedAccess` (site setting must be at least as restrictive as the tenant setting), or via a sensitivity label for sites.",
                    "Also block 'Apps that don't use modern authentication' on the same page, as Learn recommends.",
                    "External people who open items shared with specific people (verification-code recipients) are also affected; Learn shows `Set-SPOTenant -ApplyAppEnforcedRestrictionsToAdHocRecipients $false` to exempt them if that is your decision.",
                ],
                "pit": [
                    "Changes can take up to 24 hours and do not affect users already signed in from unmanaged devices.",
                    "`-LimitedAccessFileType OtherFiles` explicitly allows downloading non-previewable files such as .zip and .exe — the opposite of what you want for our scenario.",
                    "'Anyone' links are not affected by these policies; disable them on sites where you enforce this.",
                ],
                "src": S("spo_unmanaged"),
                "rec": ["sharepoint-otp-retirement-b2b"],
                "tools": [],
                "marker": "official",
            },
        ],
    },
    {
        "id": "devices",
        "title": "Define what a managed device is",
        "time": "Half a day (if Intune or hybrid join already exists)",
        "deep": True,
        "goal": "Managed devices reliably present compliance or hybrid-join state in the browser, so only genuinely unmanaged devices get the monitored, download-restricted experience.",
        "lead": "Every false 'unmanaged' turns a colleague on a company laptop into a support ticket.",
        "steps": [
            {
                "t": "Use Intune compliance or Microsoft Entra hybrid join as the signal",
                "check": "Defender portal > Settings > Cloud apps > Device identification shows Intune compliant and hybrid joined identification configured; a managed test device appears with the right Device tag in the activity log",
                "do": [
                    "Conditional Access passes Intune-compliant and Microsoft Entra hybrid joined state directly to Defender for Cloud Apps, where it becomes the Device tag filter (Intune compliant, Hybrid Azure AD joined / Microsoft Entra hybrid joined).",
                    "Check Settings > Cloud apps > Conditional Access App Control > Device identification > View configuration for both options; Learn says these services are synced from Entra ID and Intune automatically.",
                    "Make sure Windows devices you consider managed actually have a compliance policy assigned and evaluate as compliant.",
                ],
                "pit": [
                    "Devices without an assigned compliance policy, or stuck in 'Not evaluated', will be treated as unmanaged once the policy is live.",
                ],
                "src": S("mdca_devid", "mdca_ts"),
                "rec": ["intune-compliance-baseline", "intune-devices-stay-noncompliant"],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Make browsers on managed devices send device identity",
                "check": "Test sign-in from a managed device in each supported browser shows the device as compliant/hybrid joined in the Entra sign-in log",
                "do": [
                    "Edge 85+ must be signed in with the work profile to pass device identity.",
                    "Chrome on Windows needs the Microsoft Single Sign On extension or the `CloudAPAuthEnabled` policy (Learn gives registry examples under `HKLM\\Software\\Policies\\Google\\Chrome`).",
                    "Firefox 91+ on Windows needs 'Allow Windows single sign-on for Microsoft, work, and school accounts'.",
                    "Learn: the device check fails if the browser runs in private mode or cookies are disabled.",
                    "On iOS, Android and macOS, devices are identified with a client certificate provisioned at registration; users may see a certificate selection prompt.",
                ],
                "pit": [
                    "InPrivate/Incognito windows on a managed laptop look unmanaged — expect testers to 'reproduce' the block accidentally.",
                ],
                "src": S("ca_conditions", "ca_compliance", "mdca_ts"),
                "rec": ["intune-edge-policies-ai"],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Optional: identify managed devices with client certificates",
                "check": "Root or intermediate CA (.pem) uploaded under Device identification; test device with user-store certificate shows Device tag Valid client certificate",
                "do": [
                    "Use when devices are managed by something other than Intune/hybrid join (for example a third-party MDM).",
                    "Upload the X.509 root or intermediate CA certificate (PEM) under Settings > Cloud apps > Conditional Access App Control > Device identification.",
                    "Deploy client certificates (PKCS #12, .p12/.pfx) to the user store, not the computer store. Firefox needs the certificate in its own store.",
                    "Optional: require CRL checks — certificates without a CRL endpoint will then fail.",
                ],
                "pit": [
                    "Mobile and desktop apps often use embedded browsers that cannot do the client certificate check.",
                ],
                "src": S("mdca_devid", "mdca_ts"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
        ],
    },
    {
        "id": "ca-policy",
        "title": "Route unmanaged browser sessions with Conditional Access",
        "time": "1–2 hours",
        "deep": True,
        "goal": "A Conditional Access policy sends browser sessions from unmanaged devices to Conditional Access App Control for a pilot group, with break-glass accounts excluded.",
        "lead": "Conditional Access decides who is routed; Defender for Cloud Apps decides what happens in the session.",
        "steps": [
            {
                "t": "Create the Conditional Access policy",
                "check": "Policy exists with pilot group, break-glass excluded, Office 365 targeted, Browser client app, device filter for unmanaged devices and Session > Use Conditional Access App Control",
                "do": [
                    "Microsoft Entra admin center > Entra ID > Conditional Access > Policies > New policy (at least Conditional Access Administrator).",
                    "Users: include a pilot group first; exclude emergency access / break-glass accounts.",
                    "Target resources: select Office 365 (Learn recommends the Office 365 app to avoid service-dependency surprises), or SharePoint Online if you deliberately want a narrower scope.",
                    "Conditions > Client apps: Configure = Yes, select Browser only. Session control applies only to browser sessions; desktop and mobile clients are handled in a separate policy (phase 6).",
                    "Conditions > Filter for devices: Configure = Yes, 'Include filtered devices in policy' with rule `device.isCompliant -ne \"True\" -and device.trustType -ne \"ServerAD\"`. Learn: unregistered devices have null properties, so negative operators are the way to catch them.",
                    "Access controls > Session > Use Conditional Access App Control > Use custom policy (for the .zip / label filters in phase 5). Select.",
                    "Enable policy: Report-only first to check scope in the sign-in logs, then On for the pilot group (see pitfalls).",
                ],
                "pit": [
                    "Report-only does not enforce session controls, so you will not see the monitored-access notice or blocked downloads until the policy is On.",
                    "Learn: report-only policies that require compliant devices can prompt macOS, iOS and Android users for a device certificate; exclude those platforms from report-only policies that check compliance if this is disruptive.",
                    "Device state and filter for devices cannot be combined in one policy; the device state condition is deprecated.",
                ],
                "src": S("mdca_session", "ca_filters", "ca_conditions", "ca_reportonly", "spo_unmanaged"),
                "rec": ["ca-report-only-first", "ca-break-glass", "ca-production-lockout-mistakes"],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Pick Monitor only, Block downloads or Use custom policy",
                "check": "Choice documented: built-in option for a quick start, or Use custom policy with named Defender for Cloud Apps session policies",
                "do": [
                    "Monitor only (built-in): routes the session through Conditional Access App Control; useful to see the notice and collect activity before blocking anything.",
                    "Block downloads (built-in): blocks downloads in routed sessions without any file filter configuration on your side.",
                    "Use custom policy: Defender for Cloud Apps access and session policies decide what is blocked, audited or protected — needed for filters on device tag, extension, sensitivity label, or for custom messages per policy.",
                    "Learn: Microsoft Defender for Cloud Apps uses the 'Microsoft Defender for Cloud Apps - Session Controls' enterprise application. Do not let another Conditional Access block policy target it, and include it in location-based policies. If it is missing, Learn shows `New-MgServicePrincipal -AppId 8a0c2593-9cbc-4f86-a247-beb7aab00d83`.",
                ],
                "pit": [
                    "Entra ID apps only appear on the Conditional Access App Control apps page after they are in at least one policy (or a user has signed in under a policy without app scope).",
                ],
                "src": S("mdca_ts", "mdca_session", "mdca_caac"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
        ],
    },
    {
        "id": "session-policy",
        "title": "Block the .zip download and write the messages",
        "time": "1–3 hours",
        "deep": True,
        "goal": "On unmanaged devices, .zip downloads (and optionally labelled files) from OneDrive and SharePoint are blocked with a clear, helpful message, and the monitored-access notice says what you want it to say.",
        "lead": "This is where you deliberately trigger the download-blocked message — and decide what it tells people.",
        "steps": [
            {
                "t": "Create a session policy that blocks .zip downloads on unmanaged devices",
                "check": "Session policy 'Block .zip download – unmanaged – OneDrive/SharePoint' is enabled with Device tag does not equal managed tags, App = OneDrive for Business + SharePoint Online, Extension = zip, Action = Block",
                "do": [
                    "Microsoft Defender portal > Cloud apps > Policies > Policy management > Conditional Access tab > Create policy > Session policy.",
                    "Session control type: Control file download (with inspection).",
                    "Activities matching all of the following: Device tag does not equal Intune compliant and Hybrid Azure AD joined (and/or Valid client certificate, depending on how you identify managed devices). App: Automated Azure AD onboarding > Microsoft OneDrive for Business and Microsoft SharePoint Online.",
                    "Files matching all of the following: Extension equals zip (add 7z, rar or others if your risk view requires).",
                    "Actions: Block. Tick 'Notify users by email' if you want a follow-up mail, and Customize block message (see next step).",
                    "Alerts: create an alert per matching event if useful, with a daily alert limit so you are not flooded.",
                ],
                "pit": [
                    "Policies created for a host app are not connected to related resource apps (Teams/Exchange policies do not cover SharePoint/OneDrive). Select OneDrive and SharePoint explicitly.",
                    "With no App filter, the policy applies to every app enabled on the Conditional Access App Control apps page.",
                    "If the Conditional Access policy already targets only unmanaged devices, the device-tag filter is a second safety net — keep it, so a later Conditional Access change does not suddenly block managed users.",
                ],
                "src": S("mdca_session", "mdca_tut", "mdca_caac"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Write a block message that guides instead of just stopping",
                "check": "Custom block message names the reason, offers an alternative and a contact; reviewed by someone outside IT",
                "do": [
                    "Learn recommends educating users with policy-specific messages, for example how to enroll an unmanaged device or how to label a file.",
                    "Suggested editorial template (adapt): 'Downloading .zip files is blocked on devices our organisation doesn't manage. You can still open and work with files in your browser. Need the file on a computer? Use your work laptop, or contact the service desk at <link> and quote MDCA-ZIP.'",
                    "Keep it specific (what and why) and actionable (what to do now). Avoid internal jargon such as 'MDCA' as the only explanation.",
                ],
                "pit": [
                    "A generic 'blocked by policy' text sends every user to the service desk. Give the self-service path first.",
                ],
                "src": S("mdca_session", "mdca_tut"),
                "rec": [],
                "tools": [],
            },
            {
                "t": "Optional: label-based block, Protect on download, or step-up",
                "check": "If used, policies for sensitivity-label block or Protect are scoped and tested; step-up uses an Entra authentication context",
                "do": [
                    "Block by label: in Files matching, filter by a Microsoft Purview sensitivity label (for example Confidential) instead of, or in addition to, the extension.",
                    "Protect instead of block: action Protect applies an encrypting sensitivity label to Word, Excel, PowerPoint and PDF files on download; the cloud original is unchanged. Protect does not overwrite an existing label.",
                    "Step-up: action Require step-up authentication sends the session back to Conditional Access with an authentication context (for example MFA or compliant device) when the activity occurs.",
                    "Block activities: you can also block print and copy/cut/paste in the browser session, optionally with content inspection.",
                ],
                "pit": [
                    "Protect cannot apply to .zip files — it supports only the Office and PDF types Learn lists.",
                    "Protect is greyed out without a Purview licence or with the Information Protection integration off.",
                ],
                "src": S("mdca_session", "mdca_stepup", "mdca_ts"),
                "rec": ["purview-sensitivity-labels-copilot"],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Configure the monitored-access notice and Edge for Business settings",
                "check": "User monitoring notification on with reviewed custom text; Edge for Business protection setting chosen and documented",
                "do": [
                    "Defender portal > Settings > Cloud apps > Conditional Access App Control > User monitoring: keep 'Notify users that their activity is being monitored' on; choose default or custom message; use Preview to check it.",
                    "Suggested editorial custom text (adapt): 'You're opening company files from a device we don't manage. You can view and edit in the browser; some downloads are blocked to keep customer data safe. Questions? <link>'",
                    "Settings > Cloud apps > Conditional Access App Control > Edge for Business protection: in-browser protection is on by default with 'Do not enforce'. Options: Allow access only from Edge, or Enforce access from Edge when possible, scoped to All devices or Unmanaged devices only; optionally notify non-Edge users.",
                    "Learn: in-browser protection needs the Edge work profile, Windows 10/11 or macOS, one of the last two stable Edge versions, and only supported policy types; otherwise the reverse proxy is used.",
                ],
                "pit": [
                    "Policies defined only in the Entra portal (built-in Monitor only / Block downloads), Edge InPrivate, B2B guests and protect-on-download policies are always served by the reverse proxy.",
                    "Learn notes developer tools are turned off with in-browser protection — expect questions from developers.",
                ],
                "src": S("mdca_session", "mdca_edge"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
        ],
    },
    {
        "id": "gaps",
        "title": "Close the gaps session control does not cover",
        "time": "Half a day to 2 days",
        "deep": True,
        "goal": "Desktop apps, the OneDrive sync client, mobile apps, legacy protocols and anonymous links cannot be used to bypass the browser-only control on unmanaged devices.",
        "lead": "Session control protects browser sessions. Everything else needs its own control.",
        "steps": [
            {
                "t": "Block desktop, sync and mobile clients on unmanaged devices",
                "check": "Second Conditional Access policy for Mobile apps and desktop clients requires a compliant or hybrid joined device for the same users; optional Defender for Cloud Apps access policy blocks Mobile and desktop",
                "do": [
                    "Learn: session controls apply only to web browser sessions; to prevent bypass, configure access policies that block native clients and allow only browser sessions.",
                    "Entra Conditional Access: same users, Office 365, Client apps = Mobile apps and desktop clients, Grant = Require device to be marked as compliant (or hybrid joined). On an unmanaged device this cannot be satisfied, so the OneDrive sync client and Office desktop apps are blocked there.",
                    "Defender for Cloud Apps alternative: access policy with Client app = Mobile and desktop, Action = Block, with a custom message such as 'You must use a web browser to access this app'.",
                    "For personal phones and tablets, use Intune app protection policies so data stays inside managed Office apps instead of relying on browser control.",
                ],
                "pit": [
                    "Unless the Client app filter is explicitly Mobile and desktop, a Defender for Cloud Apps access policy only applies to browser sessions.",
                    "Learn: the Teams desktop app is not supported for session controls; if desktop access is allowed, users may download content there even with browser controls in place.",
                ],
                "src": S("mdca_caac", "mdca_session", "mdca_access", "mdca_ts", "ca_compliance", "intune_app"),
                "rec": ["ca-compliant-device-ai", "intune-app-protection-copilot"],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Block legacy authentication and restrict 'Anyone' links",
                "check": "Legacy authentication blocked by Conditional Access; 'Anyone' links disabled or restricted on sites in scope",
                "do": [
                    "Legacy authentication clients do not pass device state, so device-based policies cannot evaluate them; block them with a dedicated Conditional Access policy.",
                    "SharePoint Learn: 'Anyone' links are not affected by the unmanaged-device policies; disable them on sites where you enforce those controls.",
                ],
                "pit": [
                    "'People in your organization' and guest links still require sign-in and are subject to Conditional Access; 'Anyone' links are not.",
                ],
                "src": S("ca_legacy", "ca_conditions", "spo_unmanaged"),
                "rec": ["ca-block-legacy-auth"],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Be honest about what remains possible",
                "check": "Risk register lists residual paths: screenshots/photos, manual retyping, copy/paste and print unless separately blocked, previews in the browser, guests from other tenants",
                "do": [
                    "Viewing is allowed by design: screenshots, phone photos of the screen and retyping cannot be prevented by session control.",
                    "Copy/cut/paste and print are only blocked if you add Block activities session policies for them.",
                    "Learn: in rare cases Defender for Cloud Apps blocks activities only on the client side to keep an app usable, which is potentially susceptible to exploitation by malicious insiders.",
                    "Session control is a guardrail for well-meaning users and a speed bump for careless ones — not a guarantee against a determined insider. Combine with sensitivity labels with encryption, Purview DLP and audit.",
                ],
                "pit": [
                    "Do not market the control internally as 'data cannot leave'. It reduces the most common accidental path.",
                ],
                "src": S("mdca_caac", "mdca_session"),
                "rec": ["purview-sensitivity-labels-copilot", "purview-oversharing-assessment"],
                "tools": [],
                "guides": ["secure-copilot-rollout", "entra-private-access-vpn-replacement"],
            },
        ],
    },
    {
        "id": "test",
        "title": "Pilot, test and communicate",
        "time": "1–2 weeks pilot",
        "deep": False,
        "goal": "The monitored-access notice and the download-blocked message appear exactly where intended, managed users are unaffected, and users know what to expect before the scope widens.",
        "steps": [
            {
                "t": "Run the test matrix with a pilot account",
                "check": "Matrix completed: unmanaged Edge (work profile), unmanaged Chrome, managed device, InPrivate, sync client, Office desktop app, mobile; results match expectations",
                "do": [
                    "Sign out of all sessions first, then sign in with a user in scope.",
                    "Unmanaged device, Edge work profile: monitored-access notice, lock icon with briefcase, .zip download blocked with your message, .docx download allowed (unless another policy blocks it).",
                    "Unmanaged device, Chrome/Firefox: same, but URL shows the `.mcas.ms` suffix (reverse proxy) and the downloaded file is replaced with your text file.",
                    "Managed device, signed-in browser: no notice, normal downloads.",
                    "Unmanaged device: OneDrive sync client and Office desktop apps blocked by the second policy.",
                    "Check the policy report and Activity log for each test; visit all pages users normally use to confirm the app renders correctly.",
                ],
                "pit": [
                    "Add test admins to App onboarding/maintenance so they get the Admin View toolbar (bypass, session recording, discovered domains) for troubleshooting.",
                ],
                "src": S("mdca_session", "mdca_tut", "mdca_ts", "mdca_edge"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Tell users before you widen the scope",
                "check": "Short notice sent to affected users and service desk briefed with a written description of both messages, the reason and the self-service path",
                "do": [
                    "Describe both messages to users in advance — the monitored-access notice and the download-blocked message, including the text you configured — and explain the reason in one sentence: files stay on managed devices; the browser still works.",
                    "Brief the service desk: how to recognise the two messages from a user's description and confirm them in the activity log, how to check a device's compliance, and when an exception is justified.",
                    "Widen scope gradually (pilot group → department → all users), watching the activity log and ticket volume.",
                ],
                "pit": [
                    "If users first meet the notice without context, 'monitored' sounds like surveillance. Explain what is and is not logged.",
                ],
                "src": S("mdca_session"),
                "rec": [],
                "tools": [],
            },
        ],
    },
    {
        "id": "troubleshoot",
        "title": "Troubleshooting and rollback",
        "time": "As needed",
        "deep": False,
        "goal": "Common failures have a known check, and you can switch the control off quickly without leaving a gap you did not intend.",
        "steps": [
            {
                "t": "Work through the common failure modes",
                "check": "Runbook covers misidentified devices, missing App Control option, app not listed, network/TLS errors, slow sign-ins and default behaviour",
                "do": [
                    "Managed device treated as unmanaged: check the Entra sign-in log Device info; check browser sign-in/extension; check compliance state; check Device identification configuration.",
                    "'Use Conditional Access App Control' missing: check Entra ID P1 and Defender for Cloud Apps licences.",
                    "App missing from the App filter: Entra ID apps appear only after being included in a policy and used.",
                    "'This site isn't secure' / no internet connection errors: allow outbound 443 to the Defender for Cloud Apps IPs and DNS names for your data centre; ensure TLS 1.2+.",
                    "Slow sign-ins: remove forward-proxy chaining where possible; review nonce-handling per app.",
                    "Settings > Conditional Access App Control > Default behavior decides whether users are allowed or blocked if the service cannot enforce policy — set it deliberately.",
                ],
                "pit": [
                    "A Conditional Access policy that blocks 'All resources' without excluding the Session Controls enterprise app will break every session-controlled app.",
                ],
                "src": S("mdca_ts", "mdca_session", "ca_conditions"),
                "rec": ["ca-production-lockout-mistakes"],
                "tools": [],
                "marker": "official",
            },
            {
                "t": "Roll back narrowly",
                "check": "Rollback steps documented and rehearsed: Conditional Access policy to Off/Report-only, session policy disabled, scope group reduced",
                "do": [
                    "Fastest: set the Conditional Access policy that applies App Control to Off (or Report-only). Sessions stop being routed to Defender for Cloud Apps on next sign-in.",
                    "Narrower: disable the specific session policy, or remove affected users from the pilot group. Learn's troubleshoot article describes finding the policy via the activity log and disabling it or removing users.",
                    "To stop the notice only, clear 'Notify users' in User monitoring — sessions remain monitored.",
                    "SharePoint app-enforced restrictions: reverting to Allow full access can take up to 24 hours.",
                    "Keep the second policy (desktop/mobile clients) under the same change record — rolling back only one half can open or close the native-app path unexpectedly.",
                ],
                "pit": [
                    "Users with an existing session may keep the old experience until they sign in again.",
                ],
                "src": S("ts_monitored", "mdca_session", "spo_unmanaged"),
                "rec": [],
                "tools": [],
                "marker": "official",
            },
        ],
    },
]
