"""Pillar guide (project guide 2 of the evening-routine queue): an internal purple-team programme that follows one
authorized attack path from quiet on-premises name-resolution poisoning to a fully enumerated hybrid identity plane.
Chains Responder -> NetExec -> Hashcat -> BloodHound CE -> ROADtools -> AADInternals, then closes with detection
validation and remediation. It is the on-prem-to-cloud sibling of the cloud-only cloud-hardening-adversary-emulation
guide and shares the Tier 0 mindset of adcs-hardening-tier0.
Fact-checked on 2026-11-02 against the tool projects (Responder, NetExec, Hashcat, BloodHound CE, ROADtools, AADInternals)
and Microsoft Learn / Microsoft Support (LLMNR, NTLM auditing, SMB signing, Windows LAPS, Defender for Identity,
Entra Connect sign-in, Seamless SSO, Conditional Access, PIM, emergency access).
Text in `backticks` renders as <code>. 'rec' = recipe ids, 'tools' = /tools/ ids, 'guides' = other guide slugs.
Time estimates are Tenant Recipes' own planning figures, not vendor numbers.
Defensive use only: your own systems or systems you hold written authorization to test."""

SLUG = "purple-team-hybrid-identity"
TIER = "pillar"  # pillar | technical (see GUIDES.md)
PUBLISHED = "2026-11-02"
TITLE = "Internal purple team: from quiet network listening to compromised hybrid identity"
SHORT = "Purple team: network to hybrid identity"
DESC = ("An expert, authorization-first purple-team playbook that walks a single attack path end to end: quiet LLMNR/NBT-NS/mDNS "
        "listening with Responder, credential validation and lateral reconnaissance with NetExec, offline cracking with Hashcat, "
        "attack-path mapping with BloodHound CE, cloud directory enumeration with ROADtools and deep hybrid checks with AADInternals. "
        "It ends where it must: proving detection in Defender for Identity and Entra logs, then remediating the on-prem-to-cloud "
        "seams the path exploited. Defensive use only, on your own systems or with written permission.")
VERIFIED = "2026-11-02"
BADGE = "fact-checked against the tool projects and Microsoft Learn / Microsoft Support"
SRC_LABEL = "Official sources"
TIME_NOTE = ("Time estimates are our planning figures for one hybrid environment: an on-premises Active Directory forest synced to a single "
             "Entra tenant with a few thousand users. Large multi-domain forests, multi-tenant estates and heavy B2B add calendar time, "
             "most of it in scoping and remediation rather than the capture itself.")
CTA_FIRST = "Start with phase 1 ->"

INTRO = [
    "Most hybrid compromises do not start in the cloud. They start on a quiet corporate VLAN where a laptop still broadcasts LLMNR and "
    "NBT-NS queries, an attacker answers one, and a NetNTLMv2 response lands in a capture. From there the path is depressingly short: "
    "validate or crack the credential, map who it can reach on-premises, then ride Entra Connect, Seamless SSO and synchronized identities "
    "straight into the tenant. This guide runs that exact path on purpose, as a purple team, so your own detections and controls get tested "
    "before a real adversary tests them for you.",
    "The chain is deliberate and each link feeds the next. Responder listens and captures. NetExec validates and enumerates laterally. "
    "Hashcat cracks offline, in the lab or on authorized material only. BloodHound CE turns the forest and the tenant into an attack graph with "
    "hybrid edges. ROADtools enumerates the Entra directory the way a compromised identity would see it, and AADInternals answers the deep "
    "federation, sync and Seamless SSO questions the portal hides. The point is never the loot; it is the before/after evidence that the path "
    "was seen and then closed.",
    "This is not a beginner tour of each tool. Every tool already has its own page under Tools with install and usage notes, and we assume you "
    "can authenticate them. Here we focus on how an experienced operator sequences them along the on-prem-to-cloud seam, what to keep, what to "
    "ignore, and how to hand findings to change control without wrecking production. It is the on-premises-rooted counterpart to the cloud-only "
    "cloud-hardening-adversary-emulation programme, and it treats the identity bridge with the same Tier 0 discipline as adcs-hardening-tier0.",
]
NAMING = ("Legal boundary: run every technique on this page only against systems you own or hold written authorization to test. The tools below "
          "poison name resolution, validate credentials, crack hashes and enumerate a live directory; used without a signed scope and rules of "
          "engagement they are an intrusion, not an assessment. Responder must only answer queries inside the authorized VLAN, password spraying "
          "and cracking of production material need an explicit clause, and no write operation runs against on-prem or Entra without a change "
          "ticket. Tenant Recipes is not affiliated with Microsoft or with the authors of Responder, NetExec, Hashcat, BloodHound, ROADtools or "
          "AADInternals, and nothing here has been lab-tested by us; it is verified against the linked documentation.")


def S(*keys):
    return [L[k] for k in keys]


MLH = "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/"
L = {
    # Responder
    "resp_gh": ("Responder on GitHub (lgandx/Responder)", "https://github.com/lgandx/Responder"),
    "resp_wiki": ("Responder usage and configuration (wiki)", "https://github.com/lgandx/Responder/wiki"),
    # NetExec
    "nxc_gh": ("NetExec on GitHub (Pennyw0rth/NetExec)", "https://github.com/Pennyw0rth/NetExec"),
    "nxc_docs": ("NetExec documentation", "https://www.netexec.wiki/"),
    "nxc_cred": ("NetExec: using credentials (passwords, hashes, --local-auth)", "https://www.netexec.wiki/getting-started/using-credentials"),
    "nxc_shares": ("NetExec: enumerate shares and access", "https://www.netexec.wiki/smb-protocol/enumeration/enumerate-shares-and-access"),
    # Hashcat
    "hc_site": ("Hashcat (hashcat.net)", "https://hashcat.net/hashcat/"),
    "hc_hashes": ("Hashcat example hashes (mode 5600 = NetNTLMv2)", "https://hashcat.net/wiki/doku.php?id=example_hashes"),
    # BloodHound CE
    "bh_quick": ("BloodHound Community Edition quickstart (SpecterOps)", "https://bloodhound.specterops.io/get-started/quickstart/community-edition-quickstart"),
    "bh_sharp": ("SharpHound Community Edition collection", "https://bloodhound.specterops.io/collect-data/ce-collection/sharphound"),
    "bh_azure": ("AzureHound Community Edition collection", "https://bloodhound.specterops.io/collect-data/ce-collection/azurehound"),
    # ROADtools
    "road_gh": ("ROADtools on GitHub (dirkjanm/ROADtools)", "https://github.com/dirkjanm/ROADtools"),
    "road_wiki": ("Getting started with ROADrecon (wiki)", "https://github.com/dirkjanm/ROADtools/wiki/Getting-started-with-ROADrecon"),
    "road_py": ("roadrecon on PyPI", "https://pypi.org/project/roadrecon/"),
    # AADInternals
    "aad_docs": ("AADInternals documentation", "https://aadinternals.com/aadinternals/"),
    "aad_gh": ("AADInternals on GitHub (Gerenios/AADInternals)", "https://github.com/Gerenios/AADInternals"),
    # Scoping / methodology
    "nist": ("NIST SP 800-115: Technical Guide to Information Security Testing and Assessment", "https://csrc.nist.gov/pubs/sp/800/115/final"),
    "mitre_poison": ("MITRE ATT&CK T1557.001: LLMNR/NBT-NS Poisoning and SMB Relay", "https://attack.mitre.org/techniques/T1557/001/"),
    "mitre_pth": ("MITRE ATT&CK T1550.002: Use Alternate Authentication Material - Pass the Hash", "https://attack.mitre.org/techniques/T1550/002/"),
    # Detection / remediation - Windows / on-prem
    "llmnr": ("Turn off multicast name resolution (ADMX_DnsClient Policy CSP)", "https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-dnsclient"),
    "ntlm_audit": ("Network security: Restrict NTLM: Audit NTLM authentication in this domain", "https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-audit-ntlm-authentication-in-this-domain"),
    "smb_sign": ("Control SMB signing behavior", "https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing"),
    "smb_overview": ("Overview of Server Message Block signing in Windows", "https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing-overview"),
    "laps": ("Windows LAPS overview", "https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview"),
    "laps_entra": ("Use Windows LAPS with Microsoft Entra ID", "https://learn.microsoft.com/en-us/entra/identity/devices/howto-manage-local-admin-passwords"),
    "tier": ("Enterprise access model (privileged access tiering)", "https://learn.microsoft.com/en-us/security/privileged-access-workstations/privileged-access-access-model"),
    "ev4625": ("4625(F) An account failed to log on", "https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4625"),
    "ev4776": ("4776(S, F) The computer attempted to validate the credentials for an account", "https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4776"),
    "audit_cred": ("Audit Credential Validation (4776) and Audit Logon (4624/4625)", "https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/audit-credential-validation"),
    # Defender for Identity
    "mdi_events": ("Configure Windows event collection for Defender for Identity", "https://learn.microsoft.com/en-us/defender-for-identity/deploy/configure-windows-event-collection"),
    "mdi_xdr": ("Microsoft Defender for Identity security alerts (lateral movement, Pass-the-Hash, NTLM relay)", "https://learn.microsoft.com/en-us/defender-for-identity/alerts-xdr"),
    "mdi_investigate": ("Investigate Defender for Identity security alerts", "https://learn.microsoft.com/en-us/defender-for-identity/investigate-security-alerts"),
    # Entra hybrid / detection
    "choose_authn": ("Choose the right authentication method for Microsoft Entra hybrid identity", MLH + "choose-ad-authn"),
    "pta_signin": ("Microsoft Entra Connect: user sign-in options (PHS, PTA, federation)", MLH + "plan-connect-user-signin"),
    "seamless": ("Microsoft Entra Connect: Seamless single sign-on", MLH + "how-to-connect-sso"),
    "connect_prereq": ("Microsoft Entra Connect: prerequisites and hardening (Tier 0 identity bridge)", MLH + "how-to-connect-install-prerequisites"),
    "signin_ca": ("Conditional Access and Microsoft Entra activity logs (applied policies on sign-ins)", "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/how-to-view-applied-conditional-access-policies"),
    "audit_acts": ("Microsoft Entra audit log activity reference", "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-audit-activities"),
    # Conditional Access / PIM / consent / break-glass
    "pim": ("What is Privileged Identity Management?", "https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure"),
    "emerg": ("Manage emergency access accounts in Microsoft Entra ID", "https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access"),
    "ca_report": ("Conditional Access report-only mode", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-report-only"),
    "consent": ("Configure how users consent to applications", "https://learn.microsoft.com/en-us/entra/identity/enterprise-apps/configure-user-consent"),
}


PHASES = [
 {
  "id": "authorize", "title": "Authorize the engagement, notify defenders and build the lab", "time": "2–4 days", "deep": False,
  "goal": "A signed scope that covers on-premises AD and the Entra tenant, a notified SOC, and a contained capture position before Responder ever answers a query.",
  "lead": "This path crosses from a broadcast domain into a production identity plane. Without the paperwork and a notified SOC, the first poisoned response is an incident you caused, not a test you ran.",
  "steps": [
   {"t": "Get written authorization that names both on-prem AD and the Entra tenant",
    "check": "A signed or ticketed approval names the forest(s)/domains, the authorized VLAN(s) and subnets, the Entra tenant ID and primary domains, the date window, allowed techniques and a stop-contact",
    "do": ["Document the in-scope domains, DC names, the capture VLAN/subnet, the Entra tenant ID and verified domains, and any explicitly out-of-scope systems (OT, partner B2B tenants, production finance apps).",
           "State explicitly which techniques are in scope: LLMNR/NBT-NS/mDNS answering inside the authorized VLAN, credential validation, authenticated enumeration, offline cracking of captured or lab material, and read-first directory enumeration in Entra.",
           "State what is out of scope unless a separate clause says otherwise: password spraying against production accounts, cracking production password hashes, relaying to live hosts, and any write/change in AD or Entra.",
           "Name a stop-contact who can halt the work in minutes and record how findings reach change control. Keep the approval with the engagement log alongside the per-tool permission reminders under /tools/."],
    "pit": ["Verbal 'go ahead' is not authorization. Security, legal and the identity owners should all be able to point at the same document.",
            "An on-prem-only scope that forgets to name the Entra tenant leaves the most important half of this path — the hybrid seam — legally undefined."],
    "rec": [], "tools": ["internal-pentest-scoping"], "src": S("nist", "mitre_poison"),
    "marker": "practical"},
   {"t": "Notify the SOC and agree how engagement activity is marked",
    "check": "SOC has the window, the capture host IP/MAC and jump-host IPs, the test account UPNs/SamAccountNames, and the Entra app or account that will authenticate to Graph",
    "do": ["Send the window, the Responder host's IP and MAC, jump-host IPs, the on-prem test accounts and the Entra identity (UPN or app registration) that ROADrecon and AADInternals will use.",
           "Agree which signals are expected — LLMNR/NBT-NS answers from your host, bursts of NTLM validation from NetExec, a high-volume ROADrecon gather — and which still page on-call.",
           "Agree a tag or ticket reference so engagement-related alerts are not auto-closed before they are reviewed in phase 8."],
    "pit": ["Skip this and the first Responder capture plus NetExec spray looks like a live breach. That is useful once, as a planned detection test — not as a 2 a.m. surprise for on-call."],
    "rec": [], "tools": [], "src": S("mdi_xdr", "audit_acts"),
    "marker": "practical"},
   {"t": "Stand up a contained capture position and a cracking lab",
    "check": "A hardened Linux host on the authorized VLAN runs Responder; an isolated, offline lab holds any hashes that will be cracked; least-privilege accounts exist for enumeration",
    "do": ["Place the capture host on the authorized VLAN only. Confirm it cannot reach out-of-scope segments and that its answering scope is limited to that broadcast domain.",
           "Prepare an offline cracking box (ideally GPU-equipped) that never touches production and holds only authorized captured or lab-generated material.",
           "Create a cloud-only Entra assessment identity with Global Reader / Security Reader (or a custom read role for CA, apps, roles, sync) and prefer PIM-eligible elevation over standing Global Administrator.",
           "Confirm emergency access accounts exist, are cloud-only with phishing-resistant MFA, and are excluded from blocking Conditional Access before you touch anything in the tenant."],
    "pit": ["A capture host dual-homed into other VLANs turns a scoped test into uncontrolled poisoning across the estate.",
            "Standing Global Administrator 'for convenience' makes the engagement identity the highest-value target in the tenant; the audit log shows its activity either way."],
    "rec": ["ca-break-glass", "pim-least-privilege-daily-ops"], "tools": ["internal-pentest-scoping"], "src": S("nist", "emerg", "pim"),
    "marker": "official"},
  ]},

 {
  "id": "listen", "title": "Quiet listening with Responder", "time": "0.5–2 days", "deep": True,
  "goal": "NetNTLMv2 material captured from authorized name-resolution poisoning, with analyze-first discipline so you measure exposure before you ever influence it.",
  "steps": [
   {"t": "Baseline the broadcast domain in analyze mode first",
    "check": "Responder has run in analyze mode (`responder -I <iface> -A`) and you have a list of hosts emitting LLMNR/NBT-NS/mDNS without having answered a single query",
    "do": ["Start with `responder -I <iface> -A`: analyze mode observes and logs LLMNR, NBT-NS and mDNS queries and browser traffic without responding, so you can prove the exposure before changing it.",
           "Record which hosts and users are leaking name-resolution queries — this is the raw material both for the attack and for the phase 9 remediation evidence.",
           "Confirm the interface is the authorized VLAN and that Responder's configured scope will not answer beyond it."],
    "pit": ["Analyze mode is the honest baseline. Jumping straight to poisoning loses the 'here is how exposed we were' number that makes remediation defensible.",
            "LLMNR/NBT-NS poisoning maps to MITRE ATT&CK T1557.001; keep that mapping in your detection catalogue from the start."],
    "rec": [], "tools": ["responder"], "src": S("resp_gh", "resp_wiki", "mitre_poison"),
    "marker": "practical"},
   {"t": "Enable answering inside the authorized VLAN and capture NetNTLMv2",
    "check": "Responder is poisoning only in the authorized scope and NetNTLMv2 hashes are landing in its logs/`Responder-Session.log` and hash files",
    "do": ["Run Responder with the poisoners you need for the test (LLMNR, NBT-NS, mDNS) on the authorized interface; keep rogue services you do not need turned off in `Responder.conf`.",
           "Collect NetNTLMv2 responses as they arrive; note the account and source host for each so you can tie captures back to real exposure.",
           "Leave SMB/HTTP relay disabled unless the rules of engagement explicitly allow relaying — capturing for offline analysis is a smaller blast radius than relaying to live hosts.",
           "Stop answering as soon as you have representative material; long unattended poisoning widens impact with no extra evidence."],
    "pit": ["Answering outside the authorized VLAN, even accidentally through a dual-homed host, is unauthorized interception. Pin the interface and scope.",
            "Capturing is not cracking. The NetNTLMv2 hashes you collect here do not get cracked until phase 4, and only lab or authorized material does."],
    "rec": [], "tools": ["responder"], "src": S("resp_gh", "resp_wiki"),
    "marker": "practical"},
   {"t": "Log the capture and set the cracking boundary",
    "check": "Every captured hash is recorded with account, source host and timestamp, and each is tagged lab/authorized-for-cracking or capture-only",
    "do": ["Export the NetNTLMv2 hashes to the offline lab box; keep the engagement log authoritative on provenance.",
           "Tag production-account hashes as capture-only unless a specific clause authorizes cracking them; tag lab-generated hashes as crackable.",
           "Treat the capture files as production secrets: restricted storage, no shared chat channels, wiped at close in phase 9."],
    "pit": ["A loose hash file in a Teams channel is its own incident.",
            "Mixing lab and production hashes in one file is how an out-of-scope credential ends up in a wordlist run."],
    "rec": [], "tools": ["responder", "hashcat"], "src": S("resp_gh", "hc_hashes"),
    "marker": "practical"},
  ]},

 {
  "id": "validate", "title": "Credential validation and lateral reconnaissance with NetExec", "time": "1–2 days", "deep": True,
  "goal": "Know which captured or provided credentials actually work, where they work, and what they can reach — without spraying production unless a clause allows it.",
  "steps": [
   {"t": "Validate credentials across SMB/WinRM/LDAP in scope",
    "check": "You know, per in-scope host, whether a given credential authenticates over SMB (and where relevant WinRM/LDAP), and whether it holds local admin",
    "do": ["Validate a known-good credential first: `nxc smb <targets> -u <user> -p <pass>` (or `-H <nthash>` for pass-the-hash, `--local-auth` for local accounts) and read the `(Pwn3d!)` marker for local admin.",
           "Repeat over `winrm` and `ldap` protocols where those are in scope to understand remote-management and directory read access for the same identity.",
           "Feed targets from a scoped host list, never a broad corporate range; keep the authorized subnets authoritative.",
           "Record the credential/host/protocol matrix — it drives both the BloodHound 'owned' marking in phase 5 and the remediation in phase 9."],
    "pit": ["Pass-the-hash validation (`-H`) is MITRE T1550.002 and will light up Defender for Identity if auditing is on — expected here, and a detection check for phase 8.",
            "A `(Pwn3d!)` on one host does not authorize moving to the next subnet; stay inside the signed scope."],
    "rec": [], "tools": ["netexec"], "src": S("nxc_cred", "nxc_docs", "mitre_pth"),
    "marker": "official"},
   {"t": "Enumerate shares, sessions and directory objects",
    "check": "You have share/ACL, logged-on-session and relevant LDAP enumeration for the in-scope hosts, captured as files for the graph",
    "do": ["Enumerate shares and effective access with `nxc smb <targets> -u <user> -p <pass> --shares`; flag writable or sensitive shares and readable secrets.",
           "Map where privileged users are logged on with session enumeration (`--sessions`, `--loggedon-users`) to find lateral-movement and credential-theft opportunities.",
           "Use LDAP enumeration (users, groups, delegation, `--users`, `--groups`, password-policy and ASREP/Kerberoast-oriented modules) only as the scope allows, and export output for ingest.",
           "Keep everything as files so BloodHound and the engagement report draw from the same evidence."],
    "pit": ["NetExec is authenticated enumeration: the signed-in identity defines what you see, so a weak account produces a falsely quiet picture.",
            "Enumeration output lists real weaknesses in attacker-useful detail — handle it as sensitive as the captured hashes."],
    "rec": [], "tools": ["netexec"], "src": S("nxc_shares", "nxc_docs"),
    "marker": "official"},
   {"t": "Spray only if explicitly authorized, with lockout math first",
    "check": "Either no spraying occurred, or spraying followed the written clause with a documented attempts-per-window well under the domain lockout threshold",
    "do": ["Before any spray, read the domain and fine-grained password policies for lockout threshold and observation window; compute a safe attempts-per-window and stay well under it.",
           "Spray only the account set the clause names, from the declared source host, in the declared window — never the whole directory.",
           "Log every attempt so the SOC can match your activity to the 4625/4776 events they will review in phase 8.",
           "Prefer validating already-captured credentials over spraying; spraying is the noisiest, highest-risk step in this phase."],
    "pit": ["A careless spray locks out production users and turns a quiet assessment into a helpdesk incident and a self-inflicted denial of service.",
            "Lockout counters are per-DC in some topologies; validate your math against the real policy, not an assumption."],
    "rec": ["ca-production-lockout-mistakes"], "tools": ["netexec"], "src": S("nxc_cred", "nxc_docs"),
    "marker": "practical"},
  ]},

 {
  "id": "crack", "title": "Offline cracking with Hashcat", "time": "0.5–2 days", "deep": True,
  "goal": "Turn authorized NetNTLMv2 captures into plaintext only where the rules allow, measure password weakness, and stop the moment the point is proven.",
  "steps": [
   {"t": "Crack NetNTLMv2 in mode 5600 against curated wordlists",
    "check": "Hashcat runs `-m 5600` against the authorized/lab hash file on the offline box and reports cracked/uncracked counts",
    "do": ["On the isolated lab box, run `hashcat -m 5600 captured.txt wordlist.txt` — mode 5600 is NetNTLMv2, the format Responder captures.",
           "Start with a curated wordlist (for example a well-known leaked-password list plus organization-specific terms), then add targeted rule files for mutations rather than brute force.",
           "Track the crack rate per wordlist/rule pass; the percentage and the time-to-crack are the metrics the report needs, not the individual passwords.",
           "Keep cracking entirely offline and only against hashes tagged crackable in phase 2."],
    "pit": ["Cracking production-account hashes without the explicit clause is out of scope even though the capture succeeded.",
            "A password that cracks in seconds is a finding; publishing the actual plaintext in a report is a second incident — report strength metrics, not credentials."],
    "rec": [], "tools": ["hashcat"], "src": S("hc_site", "hc_hashes"),
    "marker": "official"},
   {"t": "Decide when to stop and what the result means",
    "check": "A written stop rule is honoured (coverage reached, time budget spent, or point proven) and results are expressed as weakness metrics, not a dump",
    "do": ["Set the stop rule before you start: a fixed GPU-time budget and/or 'stop once we have demonstrated weak-password prevalence', whichever comes first.",
           "Feed the outcome back into scope — a high early crack rate justifies prioritising password and MFA remediation over deeper enumeration.",
           "Securely store or destroy cracked output per the data-handling clause; nothing leaves the lab box in cleartext.",
           "Never claim 'tested' on Tenant Recipes unless a named lab and date exist — this guide is verified against docs, not lab-run by us."],
    "pit": ["Infinite brute force burns the engagement budget and proves nothing a wordlist pass did not already show.",
            "Treating cracked plaintext as a trophy rather than evidence is how passwords leak out of an assessment."],
    "rec": [], "tools": ["hashcat"], "src": S("hc_site", "hc_hashes"),
    "marker": "practical"},
  ]},

 {
  "id": "paths", "title": "Attack-path mapping with BloodHound CE", "time": "1–3 days", "deep": True,
  "goal": "The forest and the tenant as one attack graph, owned principals marked, and the shortest paths to Tier 0 and across the hybrid seam made explicit.",
  "steps": [
   {"t": "Collect on-premises data with SharpHound and ingest it",
    "check": "A SharpHound collection is ingested into BloodHound CE and you can query from an owned principal to Tier 0 (Domain Admins / DC)",
    "do": ["Stand up BloodHound Community Edition (the SpecterOps-maintained open-source graph) per the quickstart, then collect with the matching SharpHound version.",
           "Run SharpHound from an in-scope domain context (for example default collection methods, or `-c All`/session loops as the scope allows) and upload the resulting ZIP via the CE file-ingest UI.",
           "Mark the principals you validated or cracked in phases 3–4 as Owned so shortest-path queries start from reality.",
           "Run the built-in Tier 0 / high-value queries and shortest-path-to-Domain-Admins from each owned node; export the paths as evidence."],
    "pit": ["Collector and BloodHound CE versions must match; a mismatched SharpHound produces a graph that silently misses edges.",
            "An un-owned graph is just inventory — the value is the path from what you actually control to what you must not lose."],
    "rec": [], "tools": ["bloodhound-ce"], "src": S("bh_quick", "bh_sharp"),
    "marker": "official"},
   {"t": "Collect the Entra tenant with AzureHound",
    "check": "An AzureHound collection for the in-scope tenant is ingested alongside the AD data in the same BloodHound CE instance",
    "do": ["Run AzureHound (CE) against the authorized tenant with the read-scoped assessment identity and ingest its output into the same instance.",
           "Review Entra high-value targets: Global Administrator and other privileged-role holders, app registrations and service principals with dangerous Graph permissions, and role-eligible principals.",
           "Keep the collection read-only; AzureHound enumerates, it does not change the directory.",
           "Treat the combined graph as sensitive — it maps both estates' crown jewels in one place."],
    "pit": ["A thin AzureHound result usually means the assessment identity is under-permissioned, not that the tenant is clean — confirm the role before concluding.",
            "Ingesting into a separate instance from the AD data breaks the hybrid-edge analysis the next step depends on."],
    "rec": [], "tools": ["bloodhound-ce", "roadtools"], "src": S("bh_azure", "bh_quick"),
    "marker": "official"},
   {"t": "Analyse the hybrid edges from on-prem to tenant",
    "check": "You have at least one documented path that crosses the on-prem/Entra seam (synced account to Entra role, Entra Connect/sync service identity, or an on-prem admin with cloud privilege)",
    "do": ["Look specifically for hybrid relationships: synced on-prem accounts that hold Entra roles, the Entra Connect sync service account and the MSOL/sync identities, and on-prem Tier 0 principals that also carry cloud privilege.",
           "Trace the realistic chain end to end — captured credential, on-prem lateral path, then the seam into the tenant — and write it as the engagement's headline attack path.",
           "Cross-check candidates against the NetExec matrix (phase 3) and prepare the ROADrecon/AADInternals questions (phases 6–7) that confirm the cloud side.",
           "Record the seam edges as the primary remediation targets for phase 9."],
    "pit": ["BloodHound shows a possible path, not a certainty; validate the cloud end with ROADrecon/AADInternals before calling it exploitable.",
            "The Entra Connect sync identity is a routine BloodHound finding and a genuine Tier 0 asset — do not bury it in the noise."],
    "rec": ["pim-least-privilege-daily-ops"], "tools": ["bloodhound-ce", "roadtools"], "src": S("bh_quick", "bh_azure", "pim"),
    "marker": "practical"},
  ]},

 {
  "id": "cloud", "title": "Cloud directory enumeration with ROADtools", "time": "0.5–1 day", "deep": False,
  "goal": "The Entra directory enumerated the way a compromised identity would see it: privileged roles, applications, consent grants and sync configuration, all read-only and offline.",
  "steps": [
   {"t": "Authenticate and gather with ROADrecon",
    "check": "`roadrecon auth` succeeded for the assessment identity and `roadrecon gather` has populated `roadrecon.db`",
    "do": ["Authenticate with `roadrecon auth` (prefer `--device-code` so MFA and Conditional Access apply) using the read-scoped assessment identity, which writes tokens to `.roadtools_auth`.",
           "Run `roadrecon gather` to pull the directory into the local `roadrecon.db`; this is a high-volume read and a planned detection event for phase 8.",
           "Keep `.roadtools_auth` and `roadrecon.db` on the hardened jump host and treat both as production secrets.",
           "Log the tenant ID, identity and gather time in the engagement log."],
    "pit": ["ROADrecon reads only, but the gather volume looks like enumeration to the SOC — which is exactly why you notified them in phase 1.",
            "Install roadrecon from PyPI / the official GitHub only; a tampered copy of an auth tool is a supply-chain compromise."],
    "rec": [], "tools": ["roadtools"], "src": S("road_wiki", "road_gh", "road_py"),
    "marker": "official"},
   {"t": "Explore roles, apps and sync in the offline GUI",
    "check": "Notes exist on privileged role holders, risky app/service-principal permissions and consent grants, and the sync/Connect configuration, cross-checked against the BloodHound graph",
    "do": ["Run `roadrecon gui` from the database directory and review privileged directory roles, applications and service principals with high Graph permissions, and user/admin consent grants.",
           "Confirm the hybrid seam from the cloud side: which accounts are synced (onPremisesSyncEnabled), the Directory Synchronization Accounts, and any app credentials that would survive a user password reset.",
           "Reconcile findings with BloodHound's hybrid edges and the NetExec matrix so one story emerges, not three partial ones.",
           "Flag standing high-privilege apps and broad user-consent as priority remediation and recipe candidates for phase 9."],
    "pit": ["ROADrecon answers directory-relationship questions; it is complementary to configuration baselines, not a replacement for them.",
            "Over-consented third-party apps are a favourite real-world persistence path — do not skip the consent review because the roles looked clean."],
    "rec": ["entra-user-consent-restrict", "pim-least-privilege-daily-ops"], "tools": ["roadtools"], "src": S("road_wiki", "consent", "pim"),
    "marker": "practical"},
  ]},

 {
  "id": "hybrid", "title": "Deep hybrid checks with AADInternals (read-first)", "time": "0.5–1 day", "deep": False,
  "goal": "Targeted, read-first verification of the federation/PTA/PHS posture, Seamless SSO and sync details that the portal hides and ROADrecon did not fully settle — with no unplanned writes.",
  "steps": [
   {"t": "Install AADInternals and obtain a cached token",
    "check": "Modules imported and a read token cached for the assessment identity (for example `Get-AADIntAccessTokenForAADGraph -SaveToCache`)",
    "do": ["Install from the PowerShell Gallery: `Install-Module AADInternals` (and `AADInternals-Endpoints` only if an endpoint-specific read is needed).",
           "Import the module and cache a token for the assessment identity; run `Get-Help` on every cmdlet before using it, because the module mixes read research with write/administration functions.",
           "Install from the Gallery / official Gerenios GitHub only — outdated mirrors are a supply-chain risk.",
           "Log every cmdlet and tenant ID in the engagement log."],
    "pit": ["Many AADInternals cmdlets can change federation, credentials or sync behaviour. Stay on read-oriented functions until a change ticket exists.",
            "A cached token is a live credential; clear it when the phase ends."],
    "rec": [], "tools": ["aadinternals"], "src": S("aad_docs", "aad_gh"),
    "marker": "official"},
   {"t": "Read the hybrid posture: federation, PTA/PHS, Seamless SSO and sync",
    "check": "Notes exist on the sign-in method (PHS/PTA/federation), Seamless SSO state, sync/service details and tenant/service-location info — gathered with read-only cmdlets and compared to docs",
    "do": ["Confirm the authentication method actually in effect (password hash sync, pass-through authentication or federation) and compare it to what the org believes is configured.",
           "Check Seamless SSO state: its `AZUREADSSOACC` Kerberos key is a high-value secret, and Seamless SSO is best disabled where modern devices rely on Primary Refresh Tokens instead.",
           "Note the Entra Connect / sync identity exposure confirmed in phases 5–6; if a write is ever needed to safely demonstrate a misconfiguration, open a change ticket and take a rollback note first.",
           "Clear cached tokens at the end of the phase."],
    "pit": ["EDR and cloud logs will show unusual Graph/AD traffic from this step — expected because the SOC was notified, and a detection opportunity for phase 8.",
            "Do not chase every research function in the module; answer only the hybrid questions the BloodHound/ROADrecon findings left open."],
    "rec": [], "tools": ["aadinternals", "roadtools"], "src": S("choose_authn", "pta_signin", "seamless", "connect_prereq"),
    "marker": "practical"},
  ]},

 {
  "id": "detect", "title": "Prove detection: on-premises capture and cloud enumeration", "time": "1–2 days", "deep": False,
  "goal": "Evidence that each step of the path was visible (or a documented, ticketed detection gap): poisoning and NTLM on-prem, lateral movement in Defender for Identity, and the enumeration in Entra logs.",
  "steps": [
   {"t": "Confirm on-prem visibility of poisoning, NTLM and logon anomalies",
    "check": "Logs show the Responder-era name-resolution anomalies and the NetExec authentications: 4624/4625 on targets, 4776 on DCs, and NTLM auditing events where enabled",
    "do": ["Correlate the Responder window with any LLMNR/NBT-NS anomaly detection and with the NTLM authentication the capture provoked; where 'Audit NTLM authentication in this domain' is enabled, review the NTLM Operational log on DCs.",
           "Match NetExec's validation/spray to Audit Logon events — 4624 (success) and 4625 (failure) on the target hosts, and 4776 credential-validation events on the domain controllers.",
           "Confirm the pass-the-hash validation surfaced where expected and that your capture host's answering was noticed.",
           "File a ticket for any step the SOC did not see that the rules of engagement said should alert."],
    "pit": ["Default event retention is short; if the engagement spans weeks, confirm forwarding to the SIEM before you need the evidence.",
            "4776 lives on the DC for domain accounts while 4624/4625 live on the target — correlate both or you will miss half the story."],
    "rec": [], "tools": [], "src": S("audit_cred", "ev4625", "ev4776", "ntlm_audit"),
    "marker": "official"},
   {"t": "Validate Defender for Identity lateral-movement and relay detections",
    "check": "The SOC has a runbook entry for the MDI alerts this path should raise (Pass-the-Hash, NTLM relay, identity-theft and enumeration alerts), tied to the sensors and event collection",
    "do": ["Check that Defender for Identity raised the lateral-movement family you exercised — suspected identity theft via Pass-the-Hash and suspected NTLM-relay alerts in particular — and that the alert evidence names your accounts and hosts.",
           "Confirm MDI sensors and the Windows event collection it requires are in place; a missing sensor or unforwarded event is itself a finding.",
           "Investigate one representative alert end to end (story, entity graph, evidence) and classify it so the engagement doubles as a SOC exercise.",
           "Record any detection gap as a ticket with the exact technique it missed."],
    "pit": ["Alert availability depends on licensing and sensors; absence of an alert can mean 'not licensed/instrumented', not 'attacker invisible' — verify which.",
            "Exclusions added during a noisy pilot are easy to forget; review MDI exclusions as part of this phase."],
    "rec": [], "tools": [], "src": S("mdi_xdr", "mdi_investigate", "mdi_events"),
    "marker": "official"},
   {"t": "Confirm Entra sign-in and audit visibility for the cloud enumeration",
    "check": "Sign-in logs show the ROADrecon/AADInternals authentications with their Conditional Access results, and audit logs show any directory reads in scope; gaps are ticketed",
    "do": ["In Entra sign-in logs, filter to the assessment UPN/app and inspect the Conditional Access tab on representative events — confirm MFA and CA applied to the device-code auth.",
           "In audit logs, confirm the directory activity you performed is visible, and that high-volume ROADrecon gather traffic correlates with Graph telemetry; absent telemetry is a finding.",
           "Check that the planned hybrid-seam reads (ROADrecon gather, AADInternals posture checks) matched the SOC's expectations from phase 1.",
           "Ticket any gap between what the rules of engagement said should alert and what the SOC actually saw."],
    "pit": ["Report-only CA outcomes are easy to misread — confirm the specific result codes in the sign-in details.",
            "Short audit retention again applies; export to Log Analytics if the evidence must outlive the window."],
    "rec": ["ca-report-only-first"], "tools": [], "src": S("signin_ca", "audit_acts"),
    "marker": "official"},
  ]},

 {
  "id": "remediate", "title": "Remediate the seam, retest and close the engagement", "time": "1–3 weeks", "deep": False,
  "goal": "The name-resolution and NTLM exposure closed on-prem, the hybrid identity path hardened, a retest that shows the path broken, and a clean wipe of all engagement material.",
  "steps": [
   {"t": "Kill the capture surface: LLMNR/NBT-NS/mDNS, SMB signing and NTLM",
    "check": "LLMNR is disabled by GPO/Intune, NBT-NS and mDNS are addressed, SMB signing is required, and NTLM auditing (and, where feasible, restriction) is in place",
    "do": ["Disable LLMNR via GPO or Intune: 'Turn off multicast name resolution' (ADMX_DnsClient), which sets `EnableMulticast = 0`; disable NBT-NS via DHCP option 001/registry or scripted NIC settings, and disable mDNS where your OS versions allow.",
           "Require SMB signing on servers and clients (`Set-SmbServerConfiguration`/`Set-SmbClientConfiguration -RequireSecuritySignature $true`) so captured hashes cannot be relayed; modern Windows increasingly requires it by default.",
           "Enable 'Audit NTLM authentication in this domain' on DCs, review the traffic, and plan NTLM restriction where applications allow.",
           "Roll these out in rings (pilot group, then wider) and keep the Responder analyze-mode baseline from phase 2 as the before/after proof."],
    "pit": ["Disabling NBT-NS can break legacy name resolution for old apps — pilot it and have the rollback (re-enable per interface) documented before the wide ring.",
            "SMB signing 'required' can surface old or misconfigured clients; stage it so you fix clients rather than reverting the control."],
    "rec": [], "tools": ["responder"], "src": S("llmnr", "smb_sign", "smb_overview", "ntlm_audit"),
    "marker": "official"},
   {"t": "Harden the identity plane: local admin, tiering and the hybrid seam",
    "check": "Windows LAPS randomises local admin passwords, local-admin and lateral reuse are constrained by tiering, and the Entra Connect/sync identities are treated as Tier 0",
    "do": ["Deploy Windows LAPS to randomise and vault local administrator passwords (BackupDirectory to Entra ID or AD), killing the pass-the-local-hash lateral path the NetExec matrix exposed.",
           "Constrain lateral movement with the enterprise access (tiering) model: no Tier 0 credential logs on to Tier 1/2 hosts, and privileged access runs from clean workstations.",
           "Treat Entra Connect, the sync service account and Seamless SSO's `AZUREADSSOACC` as Tier 0: hardened dedicated hosts, tight privileged access, and rotate the Seamless SSO Kerberos key (or retire Seamless SSO where PRT-based SSO covers it).",
           "Fix the exact BloodHound/ROADrecon findings: remove dangerous synced-account role assignments, over-consented apps and standing high-privilege service principals."],
    "pit": ["LAPS without a tiering model still lets a Tier 0 credential be harvested from a Tier 2 box — deploy both, not just the password rotation.",
            "Rotating the Seamless SSO key or changing sign-in method touches live authentication; schedule it as the Tier 0 change it is."],
    "rec": ["pim-least-privilege-daily-ops", "entra-user-consent-restrict"], "tools": ["bloodhound-ce", "roadtools"], "src": S("laps", "laps_entra", "tier", "connect_prereq"),
    "marker": "official"},
   {"t": "Fix the Conditional Access and privileged-access gaps the path exploited",
    "check": "CA closes the gaps the cloud enumeration found (phishing-resistant MFA for admins, risk and legacy-auth policies), PIM replaces standing roles, and every change keeps a break-glass exclusion",
    "do": ["Translate the ROADrecon/AADInternals findings into Conditional Access: phishing-resistant MFA for privileged roles, block legacy authentication, and risk-based policies — staged Report-only before On.",
           "Move standing privileged roles to PIM-eligible with approval and time limits, and restrict user consent so over-consented apps cannot return.",
           "Keep emergency-access accounts excluded from every blocking policy and never delete a painful CA policy — set it to Report-only/Off and replace it.",
           "Attach evidence (BloodHound paths, ROADrecon notes, sign-in screenshots with tenant identifiers redacted) to each work item."],
    "pit": ["Turning risk or MFA policies to On without a Report-only review is a classic lockout; treat every enforcement like a production change.",
            "Closing tickets on 'we clicked around the portal' without a re-check loses the before/after story the engagement was built to produce."],
    "rec": ["ca-report-only-first", "ca-block-legacy-auth", "ca-risk-based-ai", "ca-break-glass"], "tools": [], "src": S("ca_report", "pim", "consent", "emerg"),
    "marker": "official"},
   {"t": "Retest the path, wipe the loot and schedule the next window",
    "check": "The headline attack path no longer completes in a dated retest, every capture/hash/token/db is wiped or vaulted, and the next purple-team window is booked",
    "do": ["Re-run the minimal slice that proves the fix: a short Responder analyze-mode pass (no captures), a NetExec recheck of the previously-owned hosts, and a fresh BloodHound/ROADrecon look to confirm the seam edges are gone.",
           "Securely delete or vault all engagement material: Responder logs and hash files, Hashcat potfiles, BloodHound/AzureHound collections, `roadrecon.db` and `.roadtools_auth`, and any cached AADInternals tokens.",
           "Disable or rotate the assessment identity's credentials and remove any standing role assignments created for the engagement.",
           "Write the final report as scope, tools, baseline, headline path, remediations, detection gaps, residual risk and retest date — then book the next window, because name-resolution and consent drift come back quietly."],
    "pit": ["A forgotten assessment app with high Graph permissions, or an un-wiped `roadrecon.db`, is a real-world persistence and data-leak path of your own making.",
            "Do not claim 'tested configuration' on Tenant Recipes unless a named lab and date exist; a retest that breaks the path is engagement evidence, not a lab certification."],
    "rec": ["pim-least-privilege-daily-ops"], "tools": ["responder", "netexec", "bloodhound-ce", "roadtools"], "src": S("nist", "mitre_poison", "mitre_pth"),
    "marker": "practical"},
  ]},
]
