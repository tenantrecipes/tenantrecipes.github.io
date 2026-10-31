"""One-page quick guide: 5 things to check before assigning Microsoft Copilot licenses.
Original wording. Fact-checked against the linked Microsoft Learn pages on VERIFIED.
Rendered as guides/<SLUG>.html and as a printable PDF in downloads/ (tools/make_shareables.py)."""

SLUG = "copilot-license-checks"
TIER = "technical"  # pillar | technical (see GUIDES.md)
PUBLISHED = "2026-10-30"
TITLE = "5 things to check before you assign Microsoft Copilot licenses"
SHORT = "Quick guide: 5 checks before Copilot licenses"
DESC = ("A one-page pre-flight check for Microsoft 365 admins: base licenses, identity and mailboxes, update channel, "
        "network and oversharing. Fact-checked against Microsoft Learn, with a printable PDF.")
VERIFIED = "2026-10-30"

S = {
 "req": ("Microsoft Copilot requirements", "https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-requirements"),
 "unify": ("Channel unification: Semi-Annual Enterprise Channel to Monthly Enterprise Channel", "https://learn.microsoft.com/en-us/microsoft-365-apps/updates/unified-update-channels"),
 "chan": ("Change the Microsoft 365 Apps update channel for devices in your organization", "https://learn.microsoft.com/en-us/deployoffice/updates/change-channel-for-copilot"),
 "priv": ("Data, privacy, and security for Microsoft Copilot", "https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy"),
 "dag": ("Data access governance reports for SharePoint sites", "https://learn.microsoft.com/en-us/sharepoint/data-access-governance-reports"),
 "rcd": ("Restrict discovery of SharePoint sites and content", "https://learn.microsoft.com/en-us/sharepoint/restricted-content-discovery"),
 "grouplic": ("Assign or unassign licenses to a group in the Microsoft 365 admin center", "https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-group-licenses"),
}

CHECKS = [
 {"t": "Each user has a qualifying base license, assigned to the user",
  "why": "A Copilot license only works on top of an eligible Microsoft 365 or Office 365 base license. Device-based licensing for Microsoft 365 Apps for enterprise does not qualify.",
  "check": "Compare your base plans with Microsoft's current list of eligible plans, then run the Copilot License Details diagnostic for a handful of pilot users.",
  "rec": ["copilot-readiness-checklist", "copilot-chat-pay-as-you-go"], "src": ["req"]},
 {"t": "Identity, mailbox and OneDrive are in place",
  "why": "Users need a work or school account in Entra ID. Anything that uses mail, calendar or meetings needs a primary mailbox in Exchange Online (group mailboxes are not supported), and some features need OneDrive.",
  "check": "For the pilot group, confirm each user has an Exchange Online mailbox and a provisioned OneDrive before the license lands.",
  "rec": ["copilot-readiness-checklist"], "src": ["req"]},
 {"t": "Microsoft 365 Apps are on a monthly channel",
  "why": "Copilot in the desktop apps needs Current Channel or Monthly Enterprise Channel. Since Version 2606 (July 2026), Semi-Annual Enterprise Channel devices get the Monthly Enterprise Channel experience, which Microsoft says makes them eligible once the other requirements are met.",
  "check": "Look up pilot devices in the Microsoft 365 Apps admin center inventory (or Intune) and move stragglers with Cloud Update, Intune or Group Policy.",
  "rec": ["intune-deploy-m365-apps-channel", "intune-windows-autopatch"], "src": ["unify", "chan"]},
 {"t": "The network doesn't break Copilot",
  "why": "Microsoft asks you to allow the whole *.cloud.microsoft domain (allowing only some subdomains is not supported) and full WebSocket Secure connectivity to *.office.com, *.cloud.microsoft and copilot.cloud.microsoft. TLS inspection or aggressive proxy timeouts on that traffic can make Copilot fail in the apps.",
  "check": "Ask your network team to confirm the allow list and WSS path, run Microsoft's connectivity test, and make sure browsers allow the third-party cookies Copilot in the Office web apps needs.",
  "rec": ["copilot-readiness-checklist"], "src": ["req"]},
 {"t": "Oversharing is reviewed before Copilot can find it",
  "why": "Copilot only surfaces content the user already has at least view access to. That also means anything overshared to everyone becomes much easier to find.",
  "check": "Run an oversharing assessment (Purview DSPM or SharePoint Advanced Management's data access governance reports, which come with Copilot), fix the top sites first, and use Restricted Content Discovery for sites you can't clean up in time.",
  "rec": ["purview-oversharing-assessment", "sharepoint-restricted-content-discovery"], "src": ["priv", "req", "dag", "rcd"]},
]

THEN = {"t": "Then: license a pilot group, not everyone",
        "text": "Assign Copilot to a security group with group-based licensing in the Microsoft 365 admin center (nested groups are not supported), "
                "watch usage and feedback, and widen the group in waves.",
        "rec": ["copilot-pilot-group-licensing"], "src": ["grouplic"]}
