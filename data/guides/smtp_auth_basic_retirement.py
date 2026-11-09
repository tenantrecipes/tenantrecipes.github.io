"""Technical guide DRAFT: SMTP AUTH Basic authentication retirement in Exchange Online.
Documentation checked against linked primary sources on 2026-11-09; not lab-tested.
"""

SLUG = "smtp-auth-basic-retirement"
TIER = "technical"
PUBLISHED = "2026-11-09"  # draft date; set real publish date on approval
VERIFIED = "2026-11-09"
UPDATED = "2026-11-09"
TITLE = "SMTP AUTH Basic authentication retirement in Exchange Online"
SHORT = "SMTP AUTH Basic retirement"
DESC = (
    "What Microsoft is retiring for Client Submission (SMTP AUTH) Basic authentication, "
    "how to find every sender still using it, and which alternatives to use before the "
    "default disable at end of December 2026 — OAuth SMTP AUTH, Graph sendMail, connector "
    "relay, Direct Send caveats, High Volume Email, and third-party relay. Documentation "
    "verified; not lab-tested."
)
BADGE = "documentation verified against linked primary sources; not lab-tested"
SRC_LABEL = "Primary sources"
TIME_NOTE = (
    "Time estimates are Tenant Recipes planning figures for a mid-size tenant "
    "(tens of devices/apps), not Microsoft SLAs. Re-check the Exchange Team blog before you cut over."
)
CTA_FIRST = "Start with the current timeline and inventory →"

INTRO = [
    "Printers, scanners, line-of-business apps and old scripts still often send mail by "
    "signing in to smtp.office365.com with a username and password. That pattern is Client "
    "Submission (SMTP AUTH) with Basic authentication — the last Exchange Online protocol "
    "that kept Basic auth after the wider 2022 disablement.",
    "Microsoft is not turning off SMTP. It is retiring Basic authentication for SMTP AUTH "
    "client submission. A client that authenticates with OAuth (XOAUTH2) to the same "
    "endpoints, mail sent through an inbound connector, Direct Send to your MX, High Volume "
    "Email, or Microsoft Graph sendMail are different paths and are not the same retirement.",
    "As of the Exchange Team update of 27 January 2026 (revised 29 January 2026), Basic auth "
    "for SMTP AUTH stays unchanged through December 2026, is disabled by default for existing "
    "tenants at the end of December 2026 (admins can re-enable), is unavailable by default for "
    "new tenants after that, and a final removal date will be announced in the second half of "
    "2027. Treat re-enable as borrowed time, not a destination. This guide inventories senders, "
    "picks a path, and hardens before the default flips.",
]

NAMING = (
    "Scope: Exchange Online / Microsoft 365 Worldwide tenants using Client Submission "
    "(smtp.office365.com / smtp-legacy.office365.com) with Basic auth. Defensive operations "
    "on tenants you administer. Product UI labels change; prefer the linked Learn articles. "
    "Tenant Recipes is not affiliated with Microsoft. "
)

NOTICE = {
    "title": "Evidence boundary",
    "text": (
        "Timeline quotes come from the Exchange Team Tech Community posts linked below. "
        "The older March/April 2026 permanent-removal dates in the 2024 announcement were "
        "superseded by the January 2026 update — do not plan against the superseded dates. "
        "Message Center item numbers cited in secondary write-ups were not re-fetched for this "
        "draft. Azure Communication Services Email is separately retiring on 30 September 2028; "
        "see that section before choosing ACS for a long-lived design."
    ),
}

HISTORY = [
    ("2026-11-09", "Published technical guide: SMTP AUTH Basic retirement timeline, inventory, alternatives and checklist; documentation verified, not lab-tested."),
]


def S(*keys):
    return [L[k] for k in keys]


L = {
    "exo_timeline": (
        "Exchange Team: Updated SMTP AUTH Basic Authentication Deprecation Timeline (27 Jan 2026)",
        "https://techcommunity.microsoft.com/blog/exchange/updated-exchange-online-smtp-auth-basic-authentication-deprecation-timeline/4489835",
    ),
    "exo_retire": (
        "Exchange Team: Retire Basic auth for Client Submission (SMTP AUTH) — superseded timeline",
        "https://techcommunity.microsoft.com/blog/exchange/exchange-online-to-retire-basic-auth-for-client-submission-smtp-auth/4114750",
    ),
    "learn_deprec": (
        "Microsoft Learn: Deprecation of Basic authentication in Exchange Online",
        "https://learn.microsoft.com/en-us/exchange/clients-and-mobile-in-exchange-online/deprecation-of-basic-authentication-exchange-online",
    ),
    "learn_smtp_auth": (
        "Microsoft Learn: Enable or disable SMTP AUTH in Exchange Online",
        "https://learn.microsoft.com/en-us/Exchange/clients-and-mobile-in-exchange-online/authenticated-client-smtp-submission",
    ),
    "learn_oauth": (
        "Microsoft Learn: Authenticate an IMAP, POP or SMTP connection using OAuth",
        "https://learn.microsoft.com/en-us/exchange/client-developer/legacy-protocols/how-to-authenticate-an-imap-pop-smtp-application-by-using-oauth",
    ),
    "learn_device": (
        "Microsoft Learn: Multifunction device or application send email (Microsoft 365)",
        "https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/how-to-set-up-a-multifunction-device-or-application-to-send-email-using-microsoft-365-or-office-365",
    ),
    "learn_smtp_report": (
        "Microsoft Learn: SMTP AUTH clients report in the new EAC",
        "https://learn.microsoft.com/en-us/exchange/monitoring/mail-flow-reports/mfr-smtp-auth-clients-report",
    ),
    "learn_hve": (
        "Microsoft Learn: Manage High Volume Email for Microsoft 365",
        "https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/high-volume-mails-m365",
    ),
    "learn_hve_oauth": (
        "Microsoft Learn: OAuth authentication for High Volume Email",
        "https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/oauth-high-volume-mails-m365",
    ),
    "learn_hve_ts": (
        "Microsoft Learn: Troubleshoot High Volume Email",
        "https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/troubleshoot-high-volume-email-m365",
    ),
    "learn_graph_send": (
        "Microsoft Learn: user: sendMail (Microsoft Graph)",
        "https://learn.microsoft.com/en-us/graph/api/user-sendmail",
    ),
    "learn_app_rbac": (
        "Microsoft Learn: Role Based Access Control for Applications in Exchange Online",
        "https://learn.microsoft.com/en-us/exchange/permissions-exo/application-rbac",
    ),
    "learn_aap": (
        "Microsoft Learn: Application Access Policies (legacy)",
        "https://learn.microsoft.com/en-us/exchange/permissions-exo/application-access-policies",
    ),
    "learn_acs_retire": (
        "Microsoft Learn: Azure Communication Services retirement and breaking changes",
        "https://learn.microsoft.com/en-us/azure/communication-services/acs-retirement-and-breaking-changes-guide",
    ),
    "tc_directsend": (
        "Exchange Team: Introducing more control over Direct Send in Exchange Online",
        "https://techcommunity.microsoft.com/blog/exchange/introducing-more-control-over-direct-send-in-exchange-online/4408790",
    ),
    "learn_orgconfig": (
        "Microsoft Learn: Set-OrganizationConfig (RejectDirectSend)",
        "https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/set-organizationconfig",
    ),
}

PHASES = [
    {
        "id": "timeline",
        "title": "Confirm what is retiring — and what is not",
        "time": "30–60 minutes",
        "deep": True,
        "goal": "Everyone planning the change quotes the January 2026 timeline, not the superseded March/April 2026 dates, and knows OAuth SMTP AUTH is a different path.",
        "lead": "Wrong dates cause either panic or complacency. Start from the Exchange Team update.",
        "steps": [
            {
                "t": "Lock the current timeline from the Exchange Team post",
                "check": "Change record cites the 27 Jan 2026 update (revised 29 Jan 2026) with the four milestones below",
                "do": [
                    "Now to December 2026: SMTP AUTH Basic Authentication behaviour remains unchanged (Exchange Team).",
                    "End of December 2026: SMTP AUTH Basic Authentication disabled by default for existing tenants; administrators can still enable it if needed.",
                    "New tenants created after December 2026: SMTP AUTH Basic Authentication unavailable by default; OAuth is the supported authentication method.",
                    "Second half of 2027: Microsoft will announce the final removal date for SMTP AUTH Basic Authentication.",
                    "Superseded: the earlier gradual rejection from 1 March 2026 to 100% on 30 April 2026 in the 2024 post — that post now points to the January 2026 update.",
                    "After permanent disable, Basic clients receive: 550 5.7.30 Basic authentication is not supported for Client Submission.",
                ],
                "pit": [
                    "Re-enabling after the December 2026 default flip only buys time until the still-unannounced final removal.",
                    "Do not plan cutovers from secondary blogs alone — re-read the Exchange Team post before you freeze a project date.",
                ],
                "src": S("exo_timeline", "exo_retire", "learn_deprec"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Separate SMTP AUTH Basic from everything that still works",
                "check": "Decision notes list at least: OAuth SMTP AUTH, Graph sendMail, SMTP relay connector, Direct Send, HVE, third-party relay",
                "do": [
                    "Retiring: Basic authentication (username/password, including app passwords used as Basic) against Client Submission endpoints smtp.office365.com and smtp-legacy.office365.com.",
                    "Not the same retirement: SMTP AUTH with OAuth / XOAUTH2 (Modern Auth) — still the supported Client Submission auth method per Microsoft Learn and the Exchange Team.",
                    "Not Client Submission: inbound connector SMTP relay (certificate or static IP on port 25 to your MX), Direct Send (unauthenticated to MX, internal recipients only), High Volume Email (smtp.hve.mx.microsoft), Microsoft Graph sendMail, on-premises relay.",
                    "Org toggle Set-TransportConfig -SmtpClientAuthenticationDisabled disables the SMTP AUTH protocol for the organisation; per-mailbox Set-CASMailbox -SmtpClientAuthenticationDisabled overrides. That toggle is broader than “Basic only” — use it deliberately when you mean to shut SMTP AUTH off.",
                ],
                "pit": [
                    "Outlook desktop / OWA do not use SMTP AUTH for ordinary send — do not inventory them as SMTP AUTH clients.",
                    "Security defaults already block Basic auth patterns; do not “fix” scanners by weakening Security defaults without a replacement path.",
                ],
                "src": S("learn_smtp_auth", "learn_oauth", "learn_device"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "inventory",
        "title": "Find every sender still using Basic SMTP AUTH",
        "time": "Half a day to several days",
        "deep": True,
        "goal": "A named inventory of mailboxes, IPs, apps and devices that still authenticate with Basic against smtp.office365.com.",
        "lead": "You cannot migrate what you have not listed. The EAC report is the fastest start.",
        "steps": [
            {
                "t": "Export the SMTP AUTH clients report",
                "check": "CSV from Reports → Mail flow → SMTP AUTH clients covers up to 90 days; Authentication Protocol column reviewed for Basic Auth vs Modern Auth",
                "do": [
                    "In the new Exchange admin center: Reports → Mail flow → SMTP AUTH clients.",
                    "Authentication Protocol: Basic Auth maps to TlsAuthLogin; Modern Auth maps to XOAUTH2.",
                    "Widen the date range (up to 90 days). Export CSV. Note Microsoft’s note that Authentication Protocol data needed time to build up after the column was added.",
                    "Group by sender address and correlate to printers, scanners, monitoring, ERP, scripts.",
                ],
                "pit": [
                    "An empty 7-day window is not proof of zero usage — expand the range and cross-check Entra sign-ins.",
                    "OAuth senders still appear in the report as Modern Auth; they are not the retirement problem.",
                ],
                "src": S("learn_smtp_report", "exo_retire"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Cross-check Entra sign-in logs and message trace",
                "check": "Entra sign-in filter documents SMTP AUTH Basic activity; message trace samples confirm From/IP for top senders",
                "do": [
                    "In Microsoft Entra admin center, review sign-in logs for the mailboxes that send via SMTP. Filter on client app / authentication protocol fields that show SMTP / legacy auth where available in your portal version.",
                    "Use Exchange message trace for the top SMTP AUTH senders to capture source IP and volume.",
                    "List PowerShell / scripts using Send-MailMessage against smtp.office365.com — that cmdlet historically used Basic and is a common sleeper.",
                    "Ask application owners: multi-function printers, badge systems, backup alerts, Azure runbooks, on-premises IIS SMTP forwarders.",
                ],
                "pit": [
                    "Shared “scanner@” mailboxes may show interactive sign-ins disabled while SMTP AUTH remains enabled — check CAS mailbox settings, not only Entra interactive risk.",
                    "Third-party SaaS that “sends as” your domain may use Graph or a connector instead of SMTP AUTH — confirm before changing passwords.",
                ],
                "src": S("learn_smtp_auth", "learn_device"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Record SMTP AUTH enablement state",
                "check": "Document org SmtpClientAuthenticationDisabled and every mailbox with an explicit override",
                "do": [
                    "Get-TransportConfig | Format-List SmtpClientAuthenticationDisabled",
                    "Get-CASMailbox -ResultSize unlimited | where {$_.SmtpClientAuthenticationDisabled -eq $false}  # explicitly enabled",
                    "Also list $true (explicitly disabled) and $null (follow org). Prefer org disabled + allow-list of mailboxes that still need SMTP AUTH (OAuth or temporary Basic).",
                ],
                "pit": [
                    "Leaving SMTP AUTH enabled for every mailbox widens the blast radius of stolen passwords until Basic is gone everywhere.",
                ],
                "src": S("learn_smtp_auth"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "decide",
        "title": "Pick a path with the decision table",
        "time": "1–2 hours workshop",
        "deep": True,
        "goal": "Each inventoried sender has one primary path and one rollback path before anyone changes production credentials.",
        "lead": "Mismatch — for example HVE for external recipients — fails at send time.",
        "steps": [
            {
                "t": "Map each sender to one supported path",
                "check": "Inventory rows each have: path, owner, target cutover week, rollback",
                "do": [
                    "Device/app supports OAuth + needs mailbox Sent Items / external mail → SMTP AUTH with OAuth (client credentials or delegated) to smtp.office365.com:587.",
                    "Custom app you control, Graph-capable → Microsoft Graph sendMail with application permission scoped by Exchange Application RBAC (prefer) or legacy ApplicationAccessPolicy.",
                    "Internal-only high volume / many devices, Worldwide cloud → High Volume Email (HVE) account to smtp.hve.mx.microsoft:587 (OAuth preferred; Basic still offered on HVE today — prefer OAuth).",
                    "Static public IP or TLS cert, need internal + external, cannot do OAuth → SMTP relay inbound connector to tenant MX:25.",
                    "Internal only, no auth, accept spoofing risk until RejectDirectSend → Direct Send to MX:25 (last resort; plan to leave it).",
                    "External bulk / transactional at scale → third-party relay or transactional email provider; treat ACS Email as short-horizon only (retires 30 Sep 2028).",
                    "Hybrid with on-premises Exchange → relay via on-premises receive connector where that fits your security model.",
                ],
                "pit": [
                    "HVE cannot send to the internet — internal recipients only.",
                    "SMTP relay from Azure-hosted apps through Exchange Online connectors is not supported the same way as on-premises static IP devices — see Microsoft’s device guide limitations.",
                ],
                "src": S("learn_device", "learn_hve", "learn_acs_retire"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "oauth-smtp",
        "title": "Implement SMTP AUTH with OAuth 2.0",
        "time": "Half a day to 2 days per app family",
        "deep": True,
        "goal": "Apps that can speak SASL XOAUTH2 send via smtp.office365.com without a mailbox password.",
        "lead": "This keeps Client Submission and drops Basic — the path Microsoft points to first when the client can be updated.",
        "steps": [
            {
                "t": "Register the app and grant Exchange Online SMTP.SendAsApp",
                "check": "Entra app has Office 365 Exchange Online application permission SMTP.SendAsApp with admin consent; token audience outlook.office365.com",
                "do": [
                    "Register an application in Microsoft Entra ID (single-tenant unless you are an ISV).",
                    "API permissions → APIs my organization uses → Office 365 Exchange Online → Application permissions → SMTP.SendAsApp. Grant admin consent.",
                    "For client credentials, request token with scope https://outlook.office365.com/.default.",
                    "Delegated interactive/device flows use scope https://outlook.office.com/SMTP.Send (see Learn table for IMAP/POP/SMTP).",
                    "Create a client secret or certificate; prefer certificate. Store in a vault, not in the printer UI screenshot archive.",
                ],
                "pit": [
                    "Consenting Graph Mail.Send is not a substitute for Exchange Online SMTP.SendAsApp when the wire protocol is SMTP.",
                    "Some printers cannot store long secrets — if the device cannot hold the secret or do OAuth, choose relay or HVE instead of forcing OAuth.",
                ],
                "src": S("learn_oauth"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Register the Exchange service principal and mailbox access",
                "check": "New-ServicePrincipal succeeded; Add-MailboxPermission grants the service principal access to the sending mailbox; SMTP AUTH enabled on that mailbox",
                "do": [
                    "Connect-ExchangeOnline. Run New-ServicePrincipal -AppId <appId> -ObjectId <enterprise-application-object-id> (Enterprise application Object ID, not the app registration object id).",
                    "Add-MailboxPermission -Identity <mailbox> -User <servicePrincipalIdentity> -AccessRights FullAccess.",
                    "If sending as another address, also grant Send As: Add-RecipientPermission as documented for SendAs scenarios.",
                    "Ensure the mailbox has SMTP AUTH allowed: Set-CASMailbox -Identity <mailbox> -SmtpClientAuthenticationDisabled $false when the org default is disabled.",
                    "Client connects to smtp.office365.com:587 with STARTTLS and AUTH XOAUTH2 using the SASL format base64(user=...^Aauth=Bearer <token>^A^A).",
                ],
                "pit": [
                    "Wrong Object ID (app registration vs enterprise application) is a common cause of 535 5.7.3 Authentication unsuccessful.",
                    "Replication can take time after permission changes — wait and re-test before opening a support case.",
                ],
                "src": S("learn_oauth", "learn_smtp_auth"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "graph",
        "title": "Send with Microsoft Graph sendMail (scoped)",
        "time": "Half a day to 2 days",
        "deep": True,
        "goal": "Custom apps send via Graph without SMTP, with mailbox scope limited to the accounts that should send.",
        "lead": "Prefer Graph when you own the code and do not need a literal SMTP conversation.",
        "steps": [
            {
                "t": "Use Application Mail.Send with Exchange Application RBAC",
                "check": "App can POST /users/{id}/sendMail only for mailboxes in the assigned scope; tenant-wide send is not granted",
                "do": [
                    "Register Entra app; add Microsoft Graph application permission Mail.Send; admin consent.",
                    "Prefer Exchange Online Role Based Access Control for Applications: assign role Application Mail.Send with a custom resource scope that contains only the sending mailboxes (see Learn: Application RBAC).",
                    "Legacy alternative: Application Access Policies (New-ApplicationAccessPolicy) to restrict an app to a security group of mailboxes — Microsoft documents this as legacy; prefer Application RBAC for new designs.",
                    "Call POST https://graph.microsoft.com/v1.0/users/{user}/sendMail with the JSON message body. Authenticate with client credentials.",
                    "Do not also grant unbounded Exchange impersonation or full_access_as_app unless a separate design requires it.",
                ],
                "pit": [
                    "Tenant-wide Mail.Send without an Exchange scope is over-privileged — a stolen client secret can send as any user.",
                    "Graph is not a drop-in for devices that only expose SMTP settings fields.",
                ],
                "src": S("learn_graph_send", "learn_app_rbac", "learn_aap"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "relay-direct-hve",
        "title": "Relay, Direct Send, HVE, ACS and third-party options",
        "time": "Half a day to several days depending on path",
        "deep": True,
        "goal": "Legacy devices that cannot do OAuth have a documented relay or HVE design, and Direct Send risk is explicit.",
        "lead": "Most MFPs land here when firmware has no OAuth client credentials support.",
        "steps": [
            {
                "t": "SMTP relay with an inbound connector (certificate or static IP)",
                "check": "Connector On; device sends to tenant MX:25; SPF includes the sending IP or cert domain; external test recipient receives mail",
                "do": [
                    "Device smart host = your MX (for example contoso-com.mail.protection.outlook.com), port 25, TLS preferred, From address in an accepted domain (mailbox optional).",
                    "EAC → Mail flow → Connectors → Add: from Your organization's email server to Office 365.",
                    "Prefer certificate auth (Subject/SAN contains accepted domain). Otherwise authenticate by exclusive static public IP (not shared, not dynamic).",
                    "Add the IP to SPF. Test internal and external. Keep connector inventory with owner and IP change process.",
                ],
                "pit": [
                    "Dynamic or CGNAT IPs will break IP-based connectors when the WAN address moves.",
                    "Microsoft documents that SMTP relay is not the path for arbitrary third-party hosted apps in Azure without the right networking story — read the device guide limitations.",
                ],
                "src": S("learn_device"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Treat Direct Send as transitional and control RejectDirectSend",
                "check": "If Direct Send is used: SPF/DKIM/DMARC documented; RejectDirectSend decision recorded; migration off Direct Send scheduled",
                "do": [
                    "Direct Send: same MX:25, no credentials, delivers only to recipients in your Microsoft 365 organisation. External recipients are rejected.",
                    "Microsoft states most customers do not need Direct Send and is working on disabling it by default. Spoofing of accepted domains is a known abuse pattern.",
                    "Admins can reject unauthenticated Direct Send with Set-OrganizationConfig -RejectDirectSend $true (see Exchange Team Direct Send control post and Set-OrganizationConfig). Error takes the form 550 5.7.68 … Direct Send not allowed … when rejected.",
                    "If you enable RejectDirectSend, move devices to connector relay, HVE, OAuth, or Graph first.",
                ],
                "pit": [
                    "Direct Send looks “simple” on a printer and silently cannot reach Gmail/customers.",
                    "Enabling RejectDirectSend without migrating scanners causes an immediate incident — inventory first.",
                ],
                "src": S("learn_device", "tc_directsend", "learn_orgconfig"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "High Volume Email for internal application mail (Worldwide)",
                "check": "HVE account Active with billing policy; device points at smtp.hve.mx.microsoft:587; test to internal recipient succeeds; external test correctly fails",
                "do": [
                    "HVE is for internal recipients only. Endpoint smtp.hve.mx.microsoft (recommended); smtp-hve.office365.com will be deprecated later per Learn.",
                    "Create HVE accounts in EAC → Mail flow → High Volume Email (or New-MailUser -HVEAccount). Assign a Microsoft 365 pay-as-you-go billing policy (billing for HVE began 1 June 2026 per troubleshooting docs).",
                    "Authenticate with HVE credentials or OAuth (prefer OAuth; see OAuth for HVE Learn article). HVE can authenticate even when TransportConfig SMTP AUTH is disabled, because it uses a dedicated endpoint.",
                    "Limits include up to 100 HVE accounts/tenant, 50 recipients/message, 10 MB, Worldwide cloud; other clouds under evaluation.",
                ],
                "pit": [
                    "HVE Basic auth is still Basic — prefer OAuth for HVE so you are not recreating the same credential problem on a new endpoint.",
                    "GCC / sovereign: confirm support before promising HVE; Learn currently states Worldwide.",
                ],
                "src": S("learn_hve", "learn_hve_oauth", "learn_hve_ts"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "ACS Email and third-party relay — choose with eyes open",
                "check": "Any ACS Email choice records the 30 Sep 2028 retirement; external bulk has an owner-approved provider",
                "do": [
                    "Azure Communication Services Email still appears in older SMTP AUTH alternative lists for internal+external send, but ACS Email is on the retired list effective 30 September 2028 (announced September 2026). Maintenance mode — do not start green-field long-term designs on ACS Email.",
                    "Microsoft’s ACS retirement guide points internal scenarios to HVE / Exchange Online and lists Marketplace partners (for example Infobip, Telesign, Blip) for A2P email.",
                    "Third-party SMTP relays remain valid for MFPs: verify SPF/DKIM/DMARC, data residency, and that the relay itself supports modern auth to upstream if required.",
                ],
                "pit": [
                    "Copying “use ACS Email” from 2024–2025 guidance without the 2026 retirement note creates a second migration in 2028.",
                ],
                "src": S("learn_acs_retire", "learn_device", "exo_retire"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "harden",
        "title": "Best practices before the December 2026 default flip",
        "time": "Ongoing through December 2026",
        "deep": False,
        "goal": "SMTP AUTH surface is least-privilege, monitored, and ready for Basic to be off by default.",
        "steps": [
            {
                "t": "Shrink and monitor before you rely on re-enable",
                "check": "Org SMTP AUTH disabled with explicit mailbox allow-list; Conditional Access / authentication policies reviewed; alert on new Basic SMTP AUTH",
                "do": [
                    "Disable SMTP AUTH organisation-wide; enable only on mailboxes that still need Client Submission (OAuth or temporary Basic).",
                    "Replace shared passwords with OAuth or relay; rotate any password that was stored on devices.",
                    "Where Basic must remain briefly: dedicated mailbox, no privileged roles, strong unique password, block interactive sign-in if possible, Conditional Access limiting legacy clients / locations as your licence allows, short retention on that mailbox.",
                    "Continue exporting the SMTP AUTH clients report weekly until Basic volume is zero.",
                    "Plan cutovers before end of December 2026; treat any post-disable re-enable as an exception with an expiry date — final removal date still TBA in H2 2027.",
                ],
                "pit": [
                    "Turning Security defaults off solely to keep Basic SMTP AUTH working increases overall tenant risk.",
                    "App passwords are Basic auth artifacts — expect them to die with Basic SMTP AUTH.",
                ],
                "src": S("learn_smtp_auth", "exo_timeline", "learn_smtp_report"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "troubleshoot",
        "title": "Troubleshooting and rollback",
        "time": "As needed",
        "deep": False,
        "goal": "Failed sends have a known error map and a rehearsed rollback that does not permanently re-expand Basic auth.",
        "steps": [
            {
                "t": "Match the error to the path, then roll back narrowly",
                "check": "Runbook lists 550 5.7.30, 535 5.7.3, 550 5.7.68, connector/SPF failures and the matching fix or rollback",
                "do": [
                    "550 5.7.30 Basic authentication is not supported for Client Submission — Basic retired or blocked; move to OAuth or another path.",
                    "535 5.7.3 Authentication unsuccessful on OAuth SMTP — check token scope, enterprise Object ID, service principal, mailbox permission, SMTP AUTH mailbox flag, clock skew.",
                    "550 5.7.68 Direct Send not allowed — RejectDirectSend is on; use connector relay or authenticated path.",
                    "HVE Account status Not active — assign valid billing policy; confirm PAYG Azure subscription.",
                    "Rollback: keep previous connector / HVE / Graph config disabled but documented; temporary re-enable of Basic SMTP AUTH on one mailbox only with owner + expiry; never re-open org-wide Basic as the steady state.",
                    "After rollback, file the exception and continue the migration — December 2026 default and H2 2027 final removal still apply.",
                ],
                "pit": [
                    "Silent “success” to internal recipients only may mean you accidentally landed on Direct Send.",
                ],
                "src": S("exo_retire", "learn_oauth", "learn_hve_ts", "learn_device", "tc_directsend"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
]
