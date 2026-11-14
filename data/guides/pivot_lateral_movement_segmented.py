"""Pillar guide (project guide 5 of the evening-routine queue): pivot and lateral movement in a segmented
network, post-exploitation end to end.
Chains Ligolo-ng (pivot) -> Responder (network listening/relay) -> NetExec (credential validation and spread)
-> Impacket (remote execution, secrets, tickets) -> Evil-WinRM (interactive WinRM) -> Metasploit (controlled
post-exploitation). Closes with detection validation and remediation. On-prem/assumed-breach sibling of
purple-team-hybrid-identity (listening to hybrid identity), external-attack-surface-osint (external) and
cloud-hardening-adversary-emulation (cloud).
Fact-checked on 2026-11-04 against the tool projects (Ligolo-ng, Responder, NetExec, Impacket, Evil-WinRM,
Metasploit) and Microsoft Learn / CISA / NIST / MITRE ATT&CK guidance for lateral movement, logging and
remediation.
Text in `backticks` renders as <code>. 'rec' = recipe ids, 'tools' = /tools/ ids, 'guides' = other guide slugs,
'sec' = cyber ids. Time estimates are Tenant Recipes' own planning figures, not vendor numbers.
Defensive use only: your own systems or systems you hold written authorization to test."""

SLUG = "pivot-lateral-movement-segmented"
TIER = "pillar"  # pillar | technical (see GUIDES.md)
PUBLISHED = "2026-11-04"
TITLE = "Pivot and lateral movement in a segmented network"
SHORT = "Pivot and lateral movement, post-exploitation end to end"
DESC = ("An expert, authorization-first project that runs post-exploitation across a segmented network from a "
        "single foothold: route into the segment with Ligolo-ng, listen and relay with Responder, validate and "
        "spread credentials with NetExec, pull secrets and abuse tickets with Impacket, take interactive WinRM "
        "shells with Evil-WinRM, and drive controlled post-exploitation with Metasploit. It ends where it must: "
        "proving the blue team saw each step and remediating the paths that worked. Defensive use only, on your "
        "own systems or with written permission.")
VERIFIED = "2026-11-04"
BADGE = "fact-checked against the tool projects and Microsoft Learn / CISA / NIST / MITRE ATT&CK"
SRC_LABEL = "Official sources"
TIME_NOTE = ("Time estimates are our planning figures for one assumed-breach engagement against a mid-size "
             "segmented estate: a single foothold, a handful of reachable segments and a few hundred domain-joined "
             "hosts. Flat networks shorten the pivot work; heavily segmented, well-monitored estates add time in "
             "tunnelling, quiet credential validation and detection correlation rather than in the exploitation "
             "itself.")
CTA_FIRST = "Start with phase 1 ->"

INTRO = [
    "Most damaging intrusions are not one clever exploit; they are a quiet walk. An attacker lands on one host, "
    "finds a route into the next segment, listens for a credential, validates it against a hundred machines, pulls "
    "a secret, and repeats until something privileged falls. This guide runs that walk on purpose, as a "
    "purple-team post-exploitation programme, so you learn where your segmentation, signing and monitoring actually "
    "stop an operator and where they only slow one down.",
    "The chain is deliberate and each link feeds the next. Ligolo-ng turns the foothold into a routed pivot so your "
    "tooling can reach the target segment without a heavyweight C2 just for routing. Responder listens for "
    "name-resolution poisoning and, where in scope, relays what it catches. NetExec takes any credential or hash "
    "and tells you exactly which hosts accept it and what you can do there. Impacket converts that access into "
    "remote execution, secret extraction and Kerberos ticket abuse. Evil-WinRM gives you a clean interactive shell "
    "where WinRM is open. Metasploit ties it together for controlled post-exploitation, session management and "
    "further pivoting when the engagement needs it.",
    "This is not a beginner tour of each tool. Every tool already has its own page under Tools with install and "
    "usage notes. Here we focus on how an experienced operator sequences them inside a segmented network, how scope "
    "and ownership are proven before a packet crosses a segment boundary, what to keep versus leave alone, and how "
    "to hand findings to the people who own segmentation, signing and detection. It is the internal, "
    "assumed-breach counterpart to the purple-team-hybrid-identity programme and the external-attack-surface "
    "mapping guide.",
]
NAMING = ("Legal boundary: run every technique on this page only against systems you own or hold written "
          "authorization to test. Pivoting, name-resolution poisoning, credential spraying, secret extraction, "
          "ticket abuse and remote code execution without a signed scope and rules of engagement are an intrusion, "
          "not an assessment. Never cross a segment boundary, poison a subnet or authenticate to a host you have not "
          "proven is in scope. Tenant Recipes is not affiliated with Microsoft, CISA, NIST, MITRE, nicocha30, "
          "lgandx, Pennyw0rth, Fortra, Hackplayers or Rapid7, and nothing here has been lab-tested by us; it is "
          "verified against the linked documentation.")


def S(*keys):
    return [L[k] for k in keys]


L = {
    # Ligolo-ng
    "ligolo_gh": ("Ligolo-ng on GitHub", "https://github.com/nicocha30/ligolo-ng"),
    # Responder
    "responder_gh": ("Responder on GitHub", "https://github.com/lgandx/Responder"),
    # NetExec
    "nxc_wiki": ("NetExec documentation wiki", "https://www.netexec.wiki/"),
    "nxc_gh": ("NetExec on GitHub", "https://github.com/Pennyw0rth/NetExec"),
    # Impacket
    "impacket_gh": ("Impacket on GitHub (Fortra)", "https://github.com/fortra/impacket"),
    # Evil-WinRM
    "evilwinrm_gh": ("Evil-WinRM on GitHub", "https://github.com/Hackplayers/evil-winrm"),
    # Metasploit
    "msf_docs": ("Metasploit documentation", "https://docs.metasploit.com/"),
    "msf_gh": ("metasploit-framework on GitHub", "https://github.com/rapid7/metasploit-framework"),
    # Methodology / standards
    "nist115": ("NIST SP 800-115: Technical Guide to Information Security Testing and Assessment", "https://csrc.nist.gov/pubs/sp/800/115/final"),
    "nist207": ("NIST SP 800-207: Zero Trust Architecture", "https://csrc.nist.gov/pubs/sp/800/207/final"),
    # MITRE ATT&CK
    "mitre_lm": ("MITRE ATT&CK TA0008: Lateral Movement", "https://attack.mitre.org/tactics/TA0008/"),
    "mitre_pivot": ("MITRE ATT&CK T1090: Proxy (internal pivoting)", "https://attack.mitre.org/techniques/T1090/"),
    "mitre_poison": ("MITRE ATT&CK T1557.001: LLMNR/NBT-NS Poisoning and SMB Relay", "https://attack.mitre.org/techniques/T1557/001/"),
    "mitre_pth": ("MITRE ATT&CK T1550.002: Use Alternate Authentication Material - Pass the Hash", "https://attack.mitre.org/techniques/T1550/002/"),
    "mitre_tickets": ("MITRE ATT&CK T1558: Steal or Forge Kerberos Tickets", "https://attack.mitre.org/techniques/T1558/"),
    "mitre_winrm": ("MITRE ATT&CK T1021.006: Remote Services - Windows Remote Management", "https://attack.mitre.org/techniques/T1021/006/"),
    "mitre_dumpntds": ("MITRE ATT&CK T1003.003: OS Credential Dumping - NTDS", "https://attack.mitre.org/techniques/T1003/003/"),
    # Microsoft detection / hardening
    "mde_hunt": ("Microsoft Defender XDR advanced hunting overview", "https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-overview"),
    "mdi": ("Microsoft Defender for Identity overview", "https://learn.microsoft.com/en-us/defender-for-identity/what-is"),
    "mdi_lateral": ("Defender for Identity lateral movement paths", "https://learn.microsoft.com/en-us/defender-for-identity/understand-lateral-movement-paths"),
    "winrm_sec": ("WinRM security (Windows Remote Management)", "https://learn.microsoft.com/en-us/windows/win32/winrm/installation-and-configuration-for-windows-remote-management"),
    "smb_signing": ("Overview of SMB signing in Windows", "https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing-overview"),
    "laps": ("Windows LAPS overview", "https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview"),
    "tiermodel": ("Microsoft privileged access: securing privileged access", "https://learn.microsoft.com/en-us/security/privileged-access-workstations/overview"),
    "cred_guard": ("Credential Guard overview", "https://learn.microsoft.com/en-us/windows/security/identity-protection/credential-guard/"),
    "signin_logs": ("Microsoft Entra sign-in logs", "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins"),
}


PHASES = [
 {
  "id": "authorize", "title": "Authorize the engagement, fix the segment scope and notify defenders", "time": "1-3 days", "deep": False,
  "goal": "A signed scope that names the starting foothold, the in-scope segments and hosts, the allowed techniques (poisoning, relay, spraying, secret extraction, ticket abuse, RCE), a notified SOC and a stop-contact before a single packet crosses a segment boundary.",
  "lead": "Post-exploitation is the part of an assessment that looks exactly like a real incident. Name-resolution poisoning, credential spraying and secret extraction without written authorization and a defined blast radius are how a purple team turns into an outage or a legal problem.",
  "steps": [
   {"t": "Get written authorization that names the foothold, the segments and the destructive-test boundary",
    "check": "A signed or ticketed approval names the assumed-breach foothold, each in-scope subnet/VLAN and host group, the account tiers you may target, the allowed techniques, the date window and a stop-contact",
    "do": ["Document the starting position (an assumed-breach foothold host or planted agent) and every segment you are allowed to reach from it.",
           "State explicitly which techniques are in scope: LLMNR/NBT-NS/mDNS poisoning, SMB/HTTP relay, credential spraying, hash/key reuse, NTDS/LSASS secret extraction, Kerberos ticket abuse, and interactive RCE.",
           "State what is out of scope unless a separate clause says so: production domain controllers for destructive tests, OT/ICS segments, denial-of-service intensity, and any host or segment you cannot prove is in scope.",
           "Name a stop-contact who can halt the work in minutes and record how findings reach change control. Keep the approval with the engagement log alongside the per-tool permission reminders under Tools."],
    "pit": ["Verbal 'go ahead' is not authorization. Network, identity, server and application owners should all be able to point at the same document.",
            "A host-only scope that forgets segment boundaries leaves pivoting legally undefined the moment Ligolo-ng routes into the next VLAN."],
    "rec": [], "tools": ["internal-pentest-scoping"], "src": S("nist115", "mitre_lm", "nist207"),
    "marker": "practical"},
   {"t": "Notify the SOC and agree what engagement activity looks like",
    "check": "SOC has the window, the foothold and assessment source identities, and the expected signals (poisoning, spraying, WinRM sessions, DCSync-style reads) so engagement alerts are triaged, not auto-closed",
    "do": ["Send the window, the foothold host, the assessment accounts and any jump identities that will authenticate.",
           "Agree which signals are expected and which still page on-call: bursts of SMB logons across a subnet, Kerberos roasting patterns, WinRM sessions from an unusual host, NTDS reads.",
           "Agree a ticket tag so engagement-related Defender for Identity and advanced-hunting alerts are reviewed in the detection phase rather than lost.",
           "Confirm emergency access, break-glass and change-control paths exist before you touch anything you may later need to remediate."],
    "pit": ["Skip this and the first Responder plus NetExec sweep looks like a live domain compromise. That is useful once, as a planned detection test, not as a 2 a.m. surprise."],
    "rec": ["ca-break-glass"], "tools": [], "guides": ["purple-team-hybrid-identity"], "src": S("mdi", "mde_hunt", "nist115"),
    "marker": "practical"},
  ]},

 {
  "id": "pivot", "title": "Establish the pivot into the segment with Ligolo-ng", "time": "0.5-1 day", "deep": True,
  "goal": "A stable, scoped route from your assessment host into the target segment through the approved foothold, with only in-scope subnets routed and a clean teardown plan.",
  "steps": [
   {"t": "Bring up the Ligolo-ng tunnel and route only in-scope subnets",
    "check": "The proxy has a TUN interface up, the agent is running on the approved foothold, and routes exist only for subnets named in the scope",
    "do": ["Download matching proxy and agent binaries from the Ligolo-ng releases for your platforms and record the version.",
           "Start the proxy on the assessment host, create the TUN interface as the project documents, and run the agent on the approved foothold only.",
           "Add routes for in-scope subnets exactly (for example the single target /24), never a broad supernet that pulls unrelated segments into the tunnel.",
           "Verify reachability with a light, approved check before any noisy tooling runs through the tunnel."],
    "pit": ["Ligolo-ng is explicitly for authorized network penetration tests; routing into a segment you cannot prove is in scope is unauthorized pivoting.",
            "A too-broad route (a /16 instead of a /24) silently makes the rest of the chain touch hosts the scope never approved.",
            "TUN setup needs privileges on the proxy host; practise in a lab before the engagement so you are not debugging routing live."],
    "rec": [], "tools": ["ligolo-ng"], "src": S("ligolo_gh", "mitre_pivot", "nist115"),
    "marker": "official"},
   {"t": "Treat the tunnel as monitored infrastructure and plan teardown",
    "check": "Tunnel source, routes and active window are in the engagement log, and a teardown step removes routes and stops the agent at the end of the phase",
    "do": ["Record when the tunnel is up, which routes are active and which tools ran through it, so the detection phase can correlate.",
           "Keep concurrent tunnels to what you need; more routes mean more blast radius and more to clean up.",
           "Remove routes and stop the agent when the pivot phase ends or when you move to a different segment.",
           "Hand the network team the exact subnets you traversed; segmentation gaps are a finding in their own right."],
    "pit": ["A forgotten agent and open route left after the engagement is a backdoor you created. Teardown is part of the work, not an afterthought."],
    "rec": [], "tools": ["ligolo-ng"], "guides": ["external-attack-surface-osint"], "src": S("ligolo_gh", "nist207"),
    "marker": "practical"},
  ]},

 {
  "id": "listen", "title": "Listen and (where in scope) relay with Responder", "time": "0.5-1 day", "deep": True,
  "goal": "Capture name-resolution poisoning opportunities and, only where the rules of engagement allow, relay them, while proving whether SMB/LDAP signing already breaks the attack.",
  "steps": [
   {"t": "Run Responder in analyze mode first to measure the exposure",
    "check": "Responder has run in a passive/analyze posture on the in-scope segment and the volume of LLMNR/NBT-NS/mDNS requests and responder-visible hosts is recorded",
    "do": ["Start with analyze mode so you observe LLMNR, NBT-NS and mDNS traffic without actively poisoning, to measure how much name resolution is still broadcast.",
           "Record which clients broadcast lookups for non-existent names (the classic typo/stale-mapping source of poisoning).",
           "Decide, from the scope, whether active poisoning and relay are permitted on this segment or whether analysis is the agreed limit.",
           "Map what you expect to catch to the hardening you want to prove: SMB signing, LDAP signing and channel binding should neutralise relay."],
    "pit": ["Active poisoning affects real users on the segment: it can break legitimate name resolution and capture real credentials. Only poison where the scope explicitly allows it.",
            "On a segment where SMB signing is enforced, SMB relay should fail; that is a successful control test, not a tool failure."],
    "rec": [], "tools": ["responder"], "sec": ["harden-smb-ldap-signing-relay"], "src": S("responder_gh", "mitre_poison"),
    "marker": "official"},
   {"t": "Capture or relay within scope and feed results to the next phase",
    "check": "Captured NetNTLM material is stored as restricted evidence (for offline cracking) or relayed only to in-scope targets that lack signing, with every action logged",
    "do": ["Where only capture is allowed, store NetNTLMv1/v2 hashes as restricted evidence and crack them offline with Hashcat rather than relaying.",
           "Where relay is in scope, relay only to in-scope hosts that do not enforce signing, and keep the target list pinned to the scope.",
           "Treat every captured credential as sensitive: restricted storage, named accessors, wipe at close.",
           "Pass validated credentials and crackable hashes into the NetExec phase to measure spread."],
    "pit": ["Relaying to a domain controller or an out-of-scope host is a fast way to cause a real incident. Pin targets to the scope and prefer capture-then-crack when in doubt.",
            "NetNTLMv1 is far weaker than v2; if you capture v1, that downgrade is itself a finding to remediate."],
    "rec": [], "tools": ["responder", "hashcat"], "sec": ["harden-smb-ldap-signing-relay"], "guides": ["purple-team-hybrid-identity"],
    "src": S("responder_gh", "mitre_poison", "smb_signing"),
    "marker": "practical"},
  ]},

 {
  "id": "spread", "title": "Validate and measure credential spread with NetExec", "time": "1-2 days", "deep": True,
  "goal": "Know exactly which in-scope hosts accept a given credential or hash, where it has local admin, and where signing or account controls stop it, before you execute anything.",
  "steps": [
   {"t": "Confirm reachability and validate credentials across the in-scope range",
    "check": "NetExec has confirmed SMB/LDAP/WinRM reachability for the in-scope subnet and validated each test credential, with results exported for the report",
    "do": ["Install NetExec on the approved assessment host (for example `pipx install git+https://github.com/Pennyw0rth/NetExec`) and run through the Ligolo-ng tunnel.",
           "Confirm reachability for the in-scope subnet only: `nxc smb 10.10.20.0/24` (replace with your scoped range).",
           "Validate a captured or provided credential against that range: `nxc smb 10.10.20.0/24 -u <user> -p '<REDACTED>'` (or `-H <hash>` for pass-the-hash), and note where it authenticates and where it is local admin (Pwn3d!).",
           "Use CrackMapExec's successor NetExec, not the archived packages, and record the version."],
    "pit": ["Credential spraying can lock accounts and trip EDR. Agree lockout thresholds and SOC notification before you spray.",
            "'Authenticated' is not 'local admin'. Read the NetExec output carefully before assuming you can execute."],
    "rec": [], "tools": ["netexec"], "sec": ["harden-smb-ldap-signing-relay"], "src": S("nxc_wiki", "nxc_gh", "mitre_pth"),
    "marker": "official"},
   {"t": "Map the reachable attack surface with read-only modules before executing",
    "check": "Shares, sessions, logged-on users and signing status across the in-scope hosts are enumerated and feed a prioritised target list; no destructive module has run yet",
    "do": ["Enumerate shares, sessions and logged-on users with read-only modules to find where privileged credentials are exposed and where data lives.",
           "Record SMB signing status per host; unsigned hosts are relay targets and a hardening finding.",
           "Prioritise hosts where a reused local-admin credential grants access to many machines (the classic lateral-movement multiplier) and feed them to BloodHound for path analysis.",
           "Keep destructive or secret-dumping modules behind an explicit change ticket; this phase is measurement."],
    "pit": ["Running secret-dump modules domain-wide 'to see what happens' is how an assessment becomes an incident. Pick targets deliberately.",
            "A single reused local admin password across the fleet is usually the real finding; the exploitation after it is just proof."],
    "rec": [], "tools": ["netexec", "bloodhound-ce"], "sec": ["harden-windows-laps"], "guides": ["adcs-hardening-tier0"],
    "src": S("nxc_wiki", "mitre_lm", "laps"),
    "marker": "practical"},
  ]},

 {
  "id": "execute", "title": "Remote execution, secrets and tickets with Impacket", "time": "1-3 days", "deep": True,
  "goal": "Convert validated access into controlled remote execution, scoped secret extraction and Kerberos ticket abuse on named in-scope hosts, with evidence for each action.",
  "steps": [
   {"t": "Execute on named hosts with the quietest sufficient Impacket method",
    "check": "Any remote execution uses a documented Impacket example tool against a named in-scope host, with the method, host and output recorded",
    "do": ["Use the Impacket example scripts on the approved assessment host (for example `psexec.py`, `smbexec.py`, `wmiexec.py`, `atexec.py`) and record which you chose.",
           "Prefer the least-invasive method that works: `wmiexec.py` or `atexec.py` are quieter than service-creating `psexec.py` on a monitored host.",
           "Authenticate with the credential or hash NetExec validated, and run only commands the scope allows; capture output as evidence.",
           "For captured keys, use pass-the-hash/overpass-the-hash rather than planting credentials on the target."],
    "pit": ["`psexec.py` creates and deletes a service and a share; it is reliable but loud and well-detected. Choose the method that matches your detection-test goal.",
            "Running execution tools against a host NetExec never validated wastes time and generates noise."],
    "rec": [], "tools": ["impacket", "netexec"], "src": S("impacket_gh", "mitre_pth", "mitre_lm"),
    "marker": "official"},
   {"t": "Extract secrets and abuse tickets only within an explicit clause",
    "check": "NTDS/LSA/SAM extraction and Kerberos ticket operations are limited to hosts named in a destructive-test clause, stored as restricted evidence, and logged for the detection phase",
    "do": ["Where the scope allows, pull local secrets with `secretsdump.py` against a named host, and DCSync-style domain secrets only against a DC explicitly in scope for that test.",
           "For Kerberoasting and AS-REP roasting use `GetUserSPNs.py` / `GetNPUsers.py`, then crack offline with Hashcat; for ticket reuse use `getTGT.py` / `ticketer.py` strictly within the clause.",
           "Treat every extracted hash, key and ticket as crown-jewel evidence: restricted storage, named accessors, wiped at close.",
           "Hand the exact accounts and hosts touched to the blue team so NTDS-read and ticket-abuse detections can be validated."],
    "pit": ["DCSync and NTDS extraction against a production DC without a specific clause is the single riskiest step in the chain; never freelance it.",
            "Silver/golden ticket forging assumes you already hold the service or krbtgt key; it is a persistence/impact demonstration, not initial access, and must be explicitly authorized."],
    "rec": ["pim-least-privilege-daily-ops"], "tools": ["impacket", "hashcat", "certipy"], "sec": ["harden-windows-laps"],
    "guides": ["adcs-hardening-tier0", "purple-team-hybrid-identity"],
    "src": S("impacket_gh", "mitre_tickets", "mitre_dumpntds"),
    "marker": "practical"},
  ]},

 {
  "id": "interactive", "title": "Interactive WinRM footholds with Evil-WinRM", "time": "0.5-1 day", "deep": False,
  "goal": "A clean, logged interactive shell on hosts where WinRM is open and you hold valid credentials, used for scoped post-exploitation rather than blind execution.",
  "steps": [
   {"t": "Open an Evil-WinRM session only where WinRM is in scope and reachable",
    "check": "An Evil-WinRM session exists against a named in-scope host over WinRM, authenticated with validated credentials or a hash, with the session window logged",
    "do": ["Confirm WinRM (5985/5986) is open on the target from NetExec before connecting.",
           "Connect with `evil-winrm -i <host> -u <user> -p '<REDACTED>'` (or with `-H <hash>` for pass-the-hash) through the Ligolo-ng tunnel.",
           "Use the session for scoped enumeration and evidence collection; prefer built-in commands over uploading tooling on a monitored host.",
           "Record the session start/stop and the host so the detection phase can match WinRM logon events."],
    "pit": ["WinRM activity is well-logged (WinRM operational logs, logon type 3, Defender for Identity). Treat a successful connect as a detection test, not stealth.",
            "Uploading binaries via Evil-WinRM is convenient and noisy; only do it when the scope needs it and the SOC expects it."],
    "rec": [], "tools": ["evil-winrm", "netexec"], "src": S("evilwinrm_gh", "mitre_winrm", "winrm_sec"),
    "marker": "official"},
  ]},

 {
  "id": "c2", "title": "Controlled post-exploitation and further pivoting with Metasploit", "time": "1-3 days", "deep": True,
  "goal": "Where the engagement needs session management, modules and deeper pivoting, drive it through Metasploit with scope locked and payloads controlled.",
  "steps": [
   {"t": "Use Metasploit for session management and scoped modules, not spray-and-pray",
    "check": "Any Metasploit module is chosen for a named in-scope host with the module, options and output recorded; payloads and listeners are controlled and removed at close",
    "do": ["Install from the Rapid7 project and record the version; set `RHOSTS` to named in-scope targets only.",
           "Prefer specific post/auxiliary modules and credentialed execution over opportunistic exploit modules against production.",
           "Use Metasploit routing/pivoting only across in-scope segments, as a complement to Ligolo-ng, not to reach new ones without authorization.",
           "Track every listener, payload and session so nothing is left running after the engagement."],
    "pit": ["Exploit modules can crash production services; on a live estate, prefer credentialed post-exploitation to memory-corruption exploits unless the scope says otherwise.",
            "Payloads and persistence left behind are your mess to clean. Inventory and remove them as part of teardown."],
    "rec": [], "tools": ["metasploit", "ligolo-ng"], "src": S("msf_docs", "msf_gh", "mitre_lm"),
    "marker": "official"},
   {"t": "Tie the chain into a single lateral-movement narrative",
    "check": "The report shows the end-to-end path (foothold -> pivot -> capture -> spread -> execute -> privilege) with the control that should have broken each link",
    "do": ["Assemble the timeline: how the foothold reached the segment, what Responder caught, where NetExec showed spread, what Impacket extracted, and how far it escalated.",
           "For each link, name the control that should have stopped it (segmentation, SMB/LDAP signing, LAPS, tiering, Credential Guard, WinRM restriction).",
           "Rank findings by how many hosts or identities each one unlocks, not by tool output severity.",
           "Carry the privileged findings into the remediation phase with owners and due dates."],
    "pit": ["A pile of tool logs is not a finding. The deliverable is the path and the missing control, told so an owner can fix it."],
    "rec": [], "tools": ["metasploit"], "guides": ["cloud-hardening-adversary-emulation"], "src": S("nist115", "mitre_lm", "tiermodel"),
    "marker": "practical"},
  ]},

 {
  "id": "detect", "title": "Prove detection across the lateral-movement chain", "time": "1-2 days", "deep": False,
  "goal": "Evidence that each noisy step was visible (or a documented detection gap): name-resolution poisoning, credential spread, remote execution, secret reads, ticket abuse and WinRM sessions.",
  "steps": [
   {"t": "Correlate identity and endpoint telemetry with the engagement timeline",
    "check": "For each active phase the SOC can show matching Defender for Identity / advanced-hunting telemetry or a ticketed detection gap",
    "do": ["Match Responder poisoning and relay to Defender for Identity and network telemetry for the window.",
           "In Defender XDR advanced hunting, look for the NetExec/Impacket/WinRM footprints: bursts of logon type 3 across hosts, service creation (psexec), WMI execution, and WinRM sessions. For example, hunt remote process creation with a `DeviceProcessEvents` query filtered to the engagement window and hosts.",
           "Confirm NTDS/LSASS secret reads and DCSync-style replication show up (Defender for Identity surfaces replication and lateral-movement paths).",
           "File a detection-engineering ticket for every technique the scope said should alert but did not."],
    "pit": ["Default log retention can be short on endpoints. Export evidence during the window, not a week later.",
            "A missing alert is a finding, not a failure to report; the gap is the value."],
    "rec": [], "tools": [], "src": S("mde_hunt", "mdi", "mdi_lateral"),
    "marker": "official"},
   {"t": "Confirm Kerberos and account-control detections fired",
    "check": "Kerberoasting/AS-REP patterns, pass-the-hash and ticket-reuse activity are visible in identity telemetry for the test accounts, and gaps are ticketed",
    "do": ["Review Kerberos service-ticket request patterns (roasting), encryption-type downgrades and anomalous TGS activity for the accounts you touched.",
           "Confirm pass-the-hash and overpass-the-hash attempts are visible, and that privileged logons from the foothold raised the expected alerts.",
           "Where identities are hybrid, check Entra sign-in logs for the test accounts to close the loop with the cloud side.",
           "Record each blind spot as a detection gap with the exact technique missed."],
    "pit": ["Roasting against a few deliberately chosen SPNs may stay under volume thresholds; tune detections for low-and-slow, not just bursts."],
    "rec": [], "tools": [], "guides": ["purple-team-hybrid-identity"], "src": S("mdi", "mde_hunt", "signin_logs"),
    "marker": "official"},
  ]},

 {
  "id": "remediate", "title": "Remediate the paths, retest, wipe and close", "time": "1-4 weeks", "deep": False,
  "goal": "Segmentation and signing gaps closed, privileged-credential reuse removed, detections added for the blind spots, a retest that shows the headline path broken, and a clean wipe of engagement material.",
  "steps": [
   {"t": "Close the controls that should have broken the chain",
    "check": "Each headline link has a closed change: segmentation, SMB/LDAP signing, LAPS, tiering, Credential Guard or WinRM restriction, with before/after evidence",
    "do": ["Enforce SMB signing and LDAP signing plus channel binding to neutralise relay (see the on-prem relay hardening entry), and audit first to avoid breaking legacy clients.",
           "Remove reused local-admin passwords with Windows LAPS so one credential no longer unlocks the fleet.",
           "Apply privileged-access tiering and Credential Guard so harvested credentials lose reach, and restrict WinRM to management hosts.",
           "Tighten segmentation so a single foothold cannot route freely; track each fix with before/after NetExec evidence."],
    "pit": ["Turning on signing or tiering without an audit window can break NAS devices, legacy apps and admin workflows. Audit, then enforce.",
            "LAPS without monitored retrieval just moves the secret; watch who reads local-admin passwords."],
    "rec": ["pim-least-privilege-daily-ops", "ca-block-legacy-auth"], "tools": ["netexec"],
    "sec": ["harden-smb-ldap-signing-relay", "harden-windows-laps"],
    "guides": ["adcs-hardening-tier0"],
    "src": S("smb_signing", "laps", "cred_guard", "tiermodel"),
    "marker": "practical"},
   {"t": "Add the missing detections and retest the headline path",
    "check": "Detection-engineering tickets from phase 8 are implemented, and a dated retest shows the critical lateral-movement path broken",
    "do": ["Implement the detections for every gap: poisoning/relay, pass-the-hash, DCSync/NTDS reads, roasting and anomalous WinRM.",
           "Re-run a minimal slice of the chain against the previously successful path and confirm the control now stops it and the alert now fires.",
           "Feed hybrid-identity findings into the purple-team-hybrid-identity programme and cloud gaps into the cloud-hardening programme rather than fixing one-offs.",
           "Keep break-glass exclusions intact on every new Conditional Access or access change."],
    "pit": ["A control that blocks the attack but produces no alert is only half the fix; you want both prevention and detection."],
    "rec": ["ca-break-glass", "ca-report-only-first"], "tools": [],
    "guides": ["purple-team-hybrid-identity", "cloud-hardening-adversary-emulation"],
    "src": S("mde_hunt", "mdi", "nist115"),
    "marker": "official"},
   {"t": "Wipe the loot, remove tooling and schedule the next assessment",
    "check": "All engagement data is wiped or vaulted, tunnels/agents/payloads are removed, assessment accounts are disabled, and a retest cadence is booked",
    "do": ["Securely delete or vault raw outputs: Responder captures, NetExec results, Impacket dumps, cracked credentials, tickets and Metasploit artifacts.",
           "Remove every Ligolo-ng agent and route, every Metasploit listener/payload, and any files uploaded via Evil-WinRM.",
           "Disable assessment accounts and rotate any credentials or keys used during the engagement.",
           "Write the report as scope, path, headline findings, remediations, detection gaps, residual risk and retest date, then book the next internal assessment because the estate drifts."],
    "pit": ["A forgotten foothold agent, an un-rotated harvested credential or an un-wiped NTDS dump is a breach of your own making.",
            "Do not claim 'tested configuration' on Tenant Recipes unless a named lab and date exist; a retest that closes a path is engagement evidence, not a lab certification."],
    "rec": [], "tools": ["ligolo-ng", "metasploit"], "src": S("nist115", "nist207", "mitre_lm"),
    "marker": "practical"},
  ]},
]
