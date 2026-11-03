"""Pillar guide (project guide 3 of the evening-routine queue): map the entire external attack surface
from OSINT through verified exposure.
Chains crt.sh → Amass → Shodan → Nmap → Nuclei → HIBP Domain Search, then deepens selected web targets with
ffuf and Burp Suite. Closes with detection validation and remediation. External sibling of
cloud-hardening-adversary-emulation (cloud config) and purple-team-hybrid-identity (on-prem to hybrid).
Fact-checked on 2026-11-03 against the tool projects (crt.sh, OWASP Amass, Shodan, Nmap, ProjectDiscovery Nuclei,
Have I Been Pwned, ffuf, PortSwigger Burp) and Microsoft Learn / CISA / NIST guidance for external exposure,
logging and remediation.
Text in `backticks` renders as <code>. 'rec' = recipe ids, 'tools' = /tools/ ids, 'guides' = other guide slugs,
'sec' = cyber ids. Time estimates are Tenant Recipes' own planning figures, not vendor numbers.
Defensive use only: your own systems or systems you hold written authorization to test."""

SLUG = "external-attack-surface-osint"
TIER = "pillar"  # pillar | technical (see GUIDES.md)
PUBLISHED = "2026-11-03"
TITLE = "Map your entire external attack surface: OSINT to verified exposure"
SHORT = "External attack surface: OSINT to verified exposure"
DESC = ("An expert, authorization-first project that walks the external attack surface end to end: certificate "
        "transparency with crt.sh, subdomain and asset discovery with OWASP Amass, internet exposure with Shodan, "
        "active verification with Nmap, vulnerability templating with Nuclei, credential exposure with Have I Been "
        "Pwned domain search, then targeted web deepening with ffuf and Burp Suite. It ends where it must: proving "
        "detection of the scanning activity and remediating what the chain found. Defensive use only, on your own "
        "systems or with written permission.")
VERIFIED = "2026-11-03"
BADGE = "fact-checked against the tool projects and Microsoft Learn / CISA / NIST"
SRC_LABEL = "Official sources"
TIME_NOTE = ("Time estimates are our planning figures for one mid-size public footprint: a handful of registered "
             "domains, a few hundred confirmed hosts and a small set of internet-facing apps. Multi-brand estates, "
             "legacy acquisitions and heavy SaaS sprawl add calendar time, mostly in ownership verification and "
             "remediation rather than the scans themselves.")
CTA_FIRST = "Start with phase 1 →"

INTRO = [
    "Most external compromises do not start with a clever zero-day. They start with a hostname you forgot was yours, "
    "a management interface that still answers on the internet, a certificate that names a subdomain nobody owns any "
    "more, or a forgotten staging site that still talks to production identity. This guide runs that discovery path "
    "on purpose, as a purple-team style exposure programme, so you find and close the surface before an uninvited "
    "operator does.",
    "The chain is deliberate and each link feeds the next. crt.sh gives you certificate-transparency names. Amass "
    "expands that into a passive (then approved active) asset inventory. Shodan shows what the internet already "
    "indexes about your ranges and hostnames. Nmap verifies what is still open right now. Nuclei templates the "
    "confirmed hosts for known weak configurations and CVEs. HIBP domain search shows which corporate identities "
    "already appear in breach corpora. ffuf and Burp then deepen the handful of web apps that matter — content "
    "discovery and authenticated application testing — without turning the engagement into an unscoped crawl of the "
    "whole internet.",
    "This is not a beginner tour of each tool. Every tool already has its own page under Tools with install and usage "
    "notes. Here we focus on how an experienced operator sequences them, how ownership is proven before a packet is "
    "sent, what to keep versus ignore, and how to hand findings to change control without wrecking production DNS or "
    "edge. It is the internet-facing counterpart to cloud-hardening-adversary-emulation and the on-prem-rooted "
    "purple-team-hybrid-identity programme.",
]
NAMING = ("Legal boundary: run every technique on this page only against systems you own or hold written authorization "
          "to test. Passive OSINT still queries third-party APIs under their terms; active probing, fuzzing and "
          "authenticated Burp work without a signed scope and rules of engagement are an intrusion, not an assessment. "
          "Never scan ranges, hostnames or SaaS tenants you have not proven are yours. Tenant Recipes is not affiliated "
          "with Microsoft, CISA, crt.sh, OWASP, Shodan, Nmap, ProjectDiscovery, Have I Been Pwned, ffuf or PortSwigger, "
          "and nothing here has been lab-tested by us; it is verified against the linked documentation.")


def S(*keys):
    return [L[k] for k in keys]


L = {
    # crt.sh / CT
    "crtsh": ("crt.sh certificate search", "https://crt.sh/"),
    "crtsh_about": ("crt.sh about / CT log aggregation", "https://crt.sh/?"),
    "rfc6962": ("RFC 6962: Certificate Transparency", "https://datatracker.ietf.org/doc/html/rfc6962"),
    # Amass
    "amass_owasp": ("OWASP Amass project page", "https://owasp.org/www-project-amass/"),
    "amass_gh": ("owasp-amass/amass on GitHub", "https://github.com/owasp-amass/amass"),
    "amass_docs": ("OWASP Amass documentation", "https://owasp-amass.github.io/docs/"),
    # Shodan
    "shodan": ("Shodan", "https://www.shodan.io/"),
    "shodan_search": ("Shodan search documentation", "https://www.shodan.io/"),
    "shodan_api": ("Shodan API and account plans", "https://developer.shodan.io/"),
    # Nmap
    "nmap": ("Nmap", "https://nmap.org/"),
    "nmap_book": ("Nmap Reference Guide", "https://nmap.org/book/man.html"),
    "nmap_os": ("Nmap OS Detection", "https://nmap.org/book/osdetect.html"),
    # Nuclei
    "nuclei_docs": ("Nuclei documentation (ProjectDiscovery)", "https://docs.projectdiscovery.io/tools/nuclei/overview"),
    "nuclei_gh": ("projectdiscovery/nuclei on GitHub", "https://github.com/projectdiscovery/nuclei"),
    "nuclei_tpl": ("Nuclei Templates", "https://github.com/projectdiscovery/nuclei-templates"),
    # HIBP
    "hibp": ("Have I Been Pwned", "https://haveibeenpwned.com/"),
    "hibp_domain": ("HIBP domain search", "https://haveibeenpwned.com/DomainSearch"),
    "hibp_api": ("HIBP API documentation", "https://haveibeenpwned.com/API/v3"),
    # ffuf / Burp
    "ffuf_gh": ("ffuf on GitHub", "https://github.com/ffuf/ffuf"),
    "burp_comm": ("Burp Suite Community", "https://portswigger.net/burp/communitydownload"),
    "burp_pro": ("Burp Suite Professional", "https://portswigger.net/burp/pro"),
    "burp_docs": ("Burp Suite documentation", "https://portswigger.net/burp/documentation"),
    # Scoping / methodology
    "nist115": ("NIST SP 800-115: Technical Guide to Information Security Testing and Assessment", "https://csrc.nist.gov/pubs/sp/800/115/final"),
    "cisa_asm": ("CISA: Binding Operational Directive 23-01 Improving Asset Visibility and Vulnerability Detection on Federal Networks", "https://www.cisa.gov/news-events/directives/bod-23-01-improving-asset-visibility-and-vulnerability-detection-federal-networks"),
    "mitre_recon": ("MITRE ATT&CK TA0043: Reconnaissance", "https://attack.mitre.org/tactics/TA0043/"),
    "mitre_ascan": ("MITRE ATT&CK T1595: Active Scanning", "https://attack.mitre.org/techniques/T1595/"),
    "mitre_osint": ("MITRE ATT&CK T1596: Search Open Technical Databases", "https://attack.mitre.org/techniques/T1596/"),
    # Detection / remediation - Microsoft / edge
    "ca_named": ("Conditional Access: named locations", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-assignment-network"),
    "waf_afd": ("Azure Front Door WAF", "https://learn.microsoft.com/en-us/azure/web-application-firewall/afd/afd-overview"),
    "appgw_waf": ("Application Gateway WAF", "https://learn.microsoft.com/en-us/azure/web-application-firewall/ag/ag-overview"),
    "defender_ext": ("Microsoft Defender External Attack Surface Management", "https://learn.microsoft.com/en-us/azure/external-attack-surface-management/"),
    "secure_score": ("Microsoft Secure Score", "https://learn.microsoft.com/en-us/defender-xdr/microsoft-secure-score"),
    "graph_act": ("Microsoft Graph activity logs", "https://learn.microsoft.com/en-us/graph/microsoft-graph-activity-logs-overview"),
    "signin_logs": ("Microsoft Entra sign-in logs", "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/concept-sign-ins"),
    "audit_acts": ("Microsoft Entra audit log activity reference", "https://learn.microsoft.com/en-us/entra/identity/monitoring-health/reference-audit-activities"),
    "emerg": ("Manage emergency access accounts in Microsoft Entra ID", "https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access"),
    "pim": ("What is Privileged Identity Management?", "https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure"),
    "legacy": ("Block legacy authentication with Conditional Access", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/howto-conditional-access-policy-block-legacy"),
    "tls_best": ("Transport Layer Security best practices with .NET Framework (TLS guidance also used for edge)", "https://learn.microsoft.com/en-us/dotnet/framework/network-programming/tls"),
}


PHASES = [
 {
  "id": "authorize", "title": "Authorize the engagement, prove ownership and notify defenders", "time": "1–3 days", "deep": False,
  "goal": "A signed scope that names domains, public IP ranges and SaaS tenants you own, a notified SOC, and a containment plan before the first active probe.",
  "lead": "Passive OSINT is still an engagement. Active scanning without ownership proof and written authorization is an intrusion — and scanning someone else's forgotten SaaS hostname is how purple teams create real incidents.",
  "steps": [
   {"t": "Get written authorization that names domains, public ranges and out-of-scope systems",
    "check": "A signed or ticketed approval names registered domains, public IP/CIDR ranges, cloud accounts that publish public endpoints, the date window, allowed techniques and a stop-contact",
    "do": ["Document every in-scope second-level domain, every public ASN/CIDR you control, and every cloud subscription or tenant that publishes public apps or DNS.",
           "State explicitly which techniques are in scope: certificate-transparency and passive OSINT, approved Amass active techniques, Shodan queries against your own assets, Nmap/Nuclei against confirmed-owned hosts, HIBP domain search for your verified domains, and scoped ffuf/Burp on named applications.",
           "State what is out of scope unless a separate clause says otherwise: third-party SaaS you do not operate, partner or customer domains, denial-of-service intensity, exploitation that changes data, and any probe of ranges you cannot prove you own.",
           "Name a stop-contact who can halt the work in minutes and record how findings reach change control. Keep the approval with the engagement log alongside the per-tool permission reminders under /tools/."],
    "pit": ["Verbal 'go ahead' is not authorization. Security, legal, DNS/network owners and the application owners should all be able to point at the same document.",
            "A domain-only scope that forgets public IP ranges leaves the Shodan and Nmap phases legally undefined for hosts that have no matching DNS name."],
    "rec": [], "tools": ["internal-pentest-scoping"], "src": S("nist115", "cisa_asm", "mitre_recon"),
    "marker": "practical"},
   {"t": "Prove ownership before any active packet leaves your assessment host",
    "check": "Every domain and CIDR in scope has ownership evidence (registrar, DNS control, cloud public-IP inventory or ISP assignment) attached to the engagement log",
    "do": ["For domains: confirm registrar control and authoritative DNS (zone file or equivalent). For wildcards and brand lookalikes, decide in writing whether they are in or out.",
           "For public IPs: reconcile against your cloud public-IP inventory (for example Azure Public IP addresses / AWS Elastic IPs) and your ISP or RIR assignments; do not trust a reverse-DNS name alone.",
           "Tag every hostname that resolves into a third-party SaaS (mail filter, CDN, CRM, partner portal) as out-of-scope for active scanning unless that tenant is explicitly authorized.",
           "Build a living 'confirmed-owned' list that later phases may touch; everything else stays OSINT-only."],
    "pit": ["crt.sh and Amass will surface partner, reseller and acquired-brand names that look like yours. Ownership proof is the filter; curiosity is not.",
            "Shared hosting and CDN edges can place unrelated customers on the same IP — scanning the IP without confirming the hostname binding is how you hit someone else."],
    "rec": [], "tools": ["internal-pentest-scoping", "crt-sh", "amass"], "src": S("nist115", "cisa_asm"),
    "marker": "practical"},
   {"t": "Notify the SOC and agree how engagement scanning is marked",
    "check": "SOC has the window, the assessment source IPs, the jump-host identities and the expected volume of recon and active scanning",
    "do": ["Send the window, the public egress IPs of the assessment hosts, any VPN egress used, and the accounts that will authenticate to Burp or HIBP.",
           "Agree which signals are expected — bursts of Nmap SYN scans, Nuclei template hits, directory fuzzing against named apps — and which still page on-call.",
           "Agree a ticket tag so engagement-related IDS/WAF alerts are reviewed in phase 8 rather than auto-closed.",
           "Confirm emergency access and change-control paths exist before you start remediating anything found later."],
    "pit": ["Skip this and the first Nmap sweep plus Nuclei run looks like a live internet attack. That is useful once, as a planned detection test — not as a 2 a.m. surprise for on-call."],
    "rec": ["ca-break-glass"], "tools": [], "src": S("nist115", "audit_acts", "signin_logs"),
    "marker": "practical"},
  ]},

 {
  "id": "ct", "title": "Certificate transparency with crt.sh", "time": "0.5–1 day", "deep": False,
  "goal": "A first-pass inventory of hostnames that have ever appeared on publicly logged certificates for your domains — including forgotten and wildcard names.",
  "steps": [
   {"t": "Query crt.sh for every in-scope registered domain",
    "check": "For each in-scope domain you have an export of unique Common Names and SANs from crt.sh, with issue dates noted",
    "do": ["Query `https://crt.sh/?q=%.example.com&output=json` (or the interactive UI) for each registered domain; also query the bare domain without the wildcard prefix.",
           "Deduplicate on name, keep the earliest and latest seen dates, and separate wildcards (`*.example.com`) from concrete hostnames.",
           "Record certificate authorities and serials that look unexpected — a sudden CA change or a certificate for a retired brand is often the first hint of shadow IT.",
           "Treat the output as OSINT (MITRE T1596.003 style certificate searching), not as proof the host still exists."],
    "pit": ["CT logs retain historical names. A hostname in crt.sh may have been decommissioned years ago — never feed raw CT output straight into an active scanner.",
            "Some organizations log private or internal names onto public certificates. Those names are now public whether you like it or not; handle them as exposure."],
    "rec": [], "tools": ["crt-sh"], "src": S("crtsh", "rfc6962", "mitre_osint"),
    "marker": "official"},
   {"t": "Classify CT names: owned, retired, third-party, investigate",
    "check": "Every unique name is tagged owned-live, owned-retired, third-party/SaaS, or investigate — and only owned-live (plus approved investigate) proceeds",
    "do": ["Resolve each concrete name (DNS A/AAAA/CNAME) from an assessment resolver and note where it lands.",
           "Mark CNAMEs into vendor SaaS as third-party unless that specific tenant is in scope.",
           "Promote names that still resolve into your confirmed-owned list; keep retired names as remediation candidates (certificate cleanup, DNS tombstones).",
           "Feed the owned-live set into Amass as seed domains rather than as a finished inventory."],
    "pit": ["Wildcard certificates hide the real hostnames — CT alone will not enumerate every label under `*.example.com`. That is why Amass comes next."],
    "rec": [], "tools": ["crt-sh", "amass"], "src": S("crtsh", "amass_docs"),
    "marker": "practical"},
  ]},

 {
  "id": "amass", "title": "Asset and subdomain discovery with OWASP Amass", "time": "1–2 days", "deep": True,
  "goal": "A reconciled inventory of subdomains and related assets built first with passive sources, then with approved active techniques only inside the signed scope.",
  "steps": [
   {"t": "Run Amass in passive mode against every in-scope domain",
    "check": "`amass enum -passive -d <domain> -o amass-passive.txt` (or equivalent) has completed for each domain and results are stored with the engagement log",
    "do": ["Install from the OWASP Amass releases or your package manager on the assessment host; record the version.",
           "Start strictly passive: `amass enum -passive -d example.com -o amass-passive.txt`. Passive mode queries OSINT sources and configured APIs without probing the target.",
           "Configure API keys you are allowed to use (per each provider's terms) so coverage improves; never share those keys in chat or tickets.",
           "Merge with the crt.sh set and produce a single candidate hostname list."],
    "pit": ["Passive still talks to third-party APIs. Rate limits and terms of service apply; abused keys get you banned mid-engagement.",
            "Results include noise: parking pages, CDN shared names, lookalike brands. Ownership proof from phase 1 remains the gate."],
    "rec": [], "tools": ["amass", "crt-sh"], "src": S("amass_owasp", "amass_docs", "amass_gh"),
    "marker": "official"},
   {"t": "Expand with approved active Amass techniques only inside scope",
    "check": "Any active Amass run is limited to confirmed-owned domains, documented in the RoE, and its output is diffed against the passive baseline",
    "do": ["Only after the RoE allows it, run a fuller enum that may include DNS brute-forcing or zone-transfer attempts against your own resolvers/authoritative servers.",
           "Keep wordlists and concurrency conservative; the goal is coverage, not a denial-of-service against your own DNS.",
           "Diff active discoveries against the passive set — new names are high-value (and sometimes high-risk) findings.",
           "Re-apply the ownership classifier before anything reaches Shodan or Nmap."],
    "pit": ["Active Amass against a domain you do not control is unauthorized scanning. Pin the domain list to the signed scope.",
            "Aggressive brute force against shared authoritative DNS can affect unrelated zones on the same infrastructure."],
    "rec": [], "tools": ["amass"], "src": S("amass_docs", "nist115", "mitre_ascan"),
    "marker": "practical"},
   {"t": "Publish the confirmed-owned asset inventory that later phases consume",
    "check": "A single inventory file lists hostname, resolved IPs, ownership tag, source (CT/Amass/DNS) and whether active scanning is approved",
    "do": ["Normalize to FQDNs, drop out-of-scope SaaS, and attach the public IPs that belong to you.",
           "Include apex and www, mail-related names that still point at infrastructure you run, VPN/gateway names, and staging/dev that still resolve publicly.",
           "Version the inventory; every later tool reads from this file rather than rediscovering ad hoc.",
           "Hand a copy to the DNS and edge owners — many findings die here when someone says 'that was decommissioned last year' and you can prove the DNS still answers."],
    "pit": ["If later phases invent their own target lists, you will scan things the inventory never approved. One list, many consumers."],
    "rec": [], "tools": ["amass"], "guides": ["cloud-hardening-adversary-emulation"], "src": S("amass_docs", "cisa_asm"),
    "marker": "practical"},
  ]},

 {
  "id": "shodan", "title": "Internet exposure with Shodan", "time": "0.5–1 day", "deep": False,
  "goal": "See your confirmed-owned ranges and hostnames the way an outsider already can — ports, banners, certificates and products — before you send your own probes.",
  "steps": [
   {"t": "Query Shodan for your confirmed-owned IPs, CIDRs and hostnames",
    "check": "Shodan results for in-scope IPs/hostnames are exported, with product banners, open ports and certificate subjects recorded",
    "do": ["Search by your public IP ranges and by hostname where useful; prefer IP/CIDR searches for infrastructure you own.",
           "Note unexpected products: SSL VPN portals, firewall admin UIs, remote-access gateways, databases, Docker APIs, old IIS/Apache versions.",
           "Compare certificate subjects in Shodan with your crt.sh set — mismatches often mark hosts serving the wrong certificate or a forgotten vhost.",
           "On a plan that includes it, enable monitoring for your own ranges so newly exposed services alert you after the engagement."],
    "pit": ["Shodan data can be days or weeks old. Treat it as a lead list, not as ground truth — Nmap in the next phase confirms what is live now.",
            "Only monitor and deeply query ranges you own. Searching the wider internet for lookalike brands is OSINT; scanning them is not."],
    "rec": [], "tools": ["shodan"], "sec": ["harden-edge-management-interfaces"], "src": S("shodan", "shodan_api", "mitre_osint"),
    "marker": "official"},
   {"t": "Turn Shodan hits into prioritized exposure candidates",
    "check": "Every unexpected internet-facing service has an owner, a business justification or a 'remove from internet' ticket draft",
    "do": ["Rank by blast radius: management planes and VPN/remote-access first, then data stores, then app front ends, then noise.",
           "Cross-check each hit against your confirmed-owned inventory; drop anything that resolved to third-party space.",
           "Capture screenshots/banners in the engagement evidence store (redact tenant identifiers in anything that will leave the team).",
           "Feed the live candidate IPs/hostnames into the Nmap target list."],
    "pit": ["A 'temporary' RDP or SMB listener that Shodan indexed last month may already be closed — or it may have reopened. Verify before you escalate."],
    "rec": [], "tools": ["shodan", "nmap"], "sec": ["harden-edge-management-interfaces"], "src": S("shodan", "cisa_asm"),
    "marker": "practical"},
  ]},

 {
  "id": "nmap", "title": "Active verification with Nmap", "time": "1–2 days", "deep": True,
  "goal": "Ground-truth open ports and service fingerprints on confirmed-owned hosts only, at a rate the SOC expects and the RoE allows.",
  "steps": [
   {"t": "Scan confirmed-owned targets with an explicit profile and rate limit",
    "check": "Nmap has run against the approved host/IP list with a documented profile (ports, timing, scripts) and raw output archived",
    "do": ["Build targets exclusively from the confirmed-owned inventory plus Shodan leads that passed ownership checks.",
           "Start with a TCP connect or SYN scan of agreed ports (`nmap -sS -p <ports> -T3 --max-rate <n> -oA nmap-pass1 <targets>` or the RoE equivalent); avoid `-T5` against production edges.",
           "Add version detection (`-sV`) and, where approved, default safe scripts; leave intrusive NSE scripts for an explicit clause.",
           "Record scan start/stop, source IP and profile in the engagement log so phase 8 can correlate detections."],
    "pit": ["Scanning the wrong CDN anycast IP can touch unrelated customers. Prefer hostname-scoped scans through the front door you own, or IP scans only for addresses assigned to you.",
            "Unannounced UDP sweeps and broadcast-heavy discovery are classic ways to create a production incident during a 'recon' phase."],
    "rec": [], "tools": ["nmap"], "src": S("nmap", "nmap_book", "mitre_ascan", "nist115"),
    "marker": "official"},
   {"t": "Reconcile Nmap with Shodan and produce the verified exposure set",
    "check": "A verified exposure table lists host, port, service, product/version (if fingerprinted), Shodan-vs-now delta and owner",
    "do": ["Mark ports Shodan reported that Nmap no longer sees (closed or firewalled) and ports Nmap sees that Shodan never indexed (new or missed).",
           "Flag management interfaces, plaintext protocols, expired/wrong certificates and services with no business owner.",
           "This verified set — not the raw Amass dump — is what Nuclei is allowed to touch.",
           "Raise immediate containment tickets for anything that should never have been on the internet (for example database listeners, admin panels without SSO)."],
    "pit": ["Version fingerprints lie. Treat `-sV` output as a hint for Nuclei template selection, not as a CVE assertion."],
    "rec": [], "tools": ["nmap", "shodan", "nuclei"], "sec": ["harden-edge-management-interfaces"],
    "src": S("nmap_book", "shodan"),
    "marker": "practical"},
  ]},

 {
  "id": "nuclei", "title": "Templated vulnerability checks with Nuclei", "time": "1–2 days", "deep": True,
  "goal": "Known-issue and misconfiguration coverage across the verified exposure set, with templates and concurrency constrained by the RoE.",
  "steps": [
   {"t": "Pin Nuclei and templates, then run a scoped pass against verified hosts",
    "check": "Nuclei version and nuclei-templates commit/tag are recorded; a first pass has completed against the verified exposure set with output archived",
    "do": ["Install from ProjectDiscovery releases; update templates deliberately and record the tag/commit you used so results are reproducible.",
           "Feed only verified URLs/hosts: `nuclei -l verified-urls.txt -o nuclei-pass1.jsonl` (plus severity/tag filters the RoE allows).",
           "Prefer tags that match what you saw (ssl, misconfig, cves, exposed panels, technology-specific) over 'run everything'.",
           "Keep concurrency and rate limits production-safe; Nuclei can look like an attack because it is one — an authorized one."],
    "pit": ["Unfiltered template packs include intrusive and DoS-adjacent checks. Explicitly exclude them unless the RoE says otherwise.",
            "A Nuclei 'critical' finding is a lead. Validate before you page executives."],
    "rec": [], "tools": ["nuclei", "nmap"], "src": S("nuclei_docs", "nuclei_gh", "nuclei_tpl"),
    "marker": "official"},
   {"t": "Triage findings into verified, false-positive and accept-risk",
    "check": "Every Nuclei hit is classified with evidence, owner and next action; unverified hits do not enter the remediation backlog as facts",
    "do": ["Manually reproduce the highest-severity hits with the least invasive method (often a single authenticated or read-only request).",
           "Map confirmed issues to owners and to existing hardening work (edge management interfaces, TLS, VPN portals).",
           "File false positives back into your local template allow/deny notes so the next run is quieter.",
           "Keep raw jsonl evidence; redact secrets before anything leaves the assessment team."],
    "pit": ["Closing a ticket on 'Nuclei said so' without a reproduction wastes remediation cycles and burns trust with app owners."],
    "rec": [], "tools": ["nuclei"], "sec": ["harden-edge-management-interfaces"], "src": S("nuclei_docs", "nist115"),
    "marker": "practical"},
  ]},

 {
  "id": "hibp", "title": "Credential exposure with Have I Been Pwned domain search", "time": "0.5–1 day", "deep": False,
  "goal": "Know which corporate identities already appear in breach corpora for your verified domains, and turn that into forced-reset and detection work — not a public shaming list.",
  "steps": [
   {"t": "Verify domains in HIBP and pull domain search results",
    "check": "Each in-scope email domain is verified in HIBP Domain Search (or queried via the authorized API) and results are stored as restricted evidence",
    "do": ["Use Have I Been Pwned domain search for domains you can verify you control; follow HIBP's verification process exactly.",
           "Where you have an API key with domain entitlement, automate pulls per HIBP API v3 rules and rate limits.",
           "Treat the result as sensitive PII/credential-exposure data: restricted storage, named accessors, wipe at close.",
           "Correlate breached addresses against current Entra / AD accounts, privileged roles and shared mailboxes."],
    "pit": ["HIBP tells you an address appeared in a breach corpus; it does not tell you the current password is the breached one. Still force resets for privileged and high-risk users when the RoE/policy says so.",
            "Never paste breach lists into tickets or chat. Link to the secured evidence store."],
    "rec": [], "tools": ["hibp-domain-search"], "src": S("hibp", "hibp_domain", "hibp_api"),
    "marker": "official"},
   {"t": "Convert breach hits into identity actions",
    "check": "Privileged and high-risk accounts from the HIBP set have a documented action (reset, block legacy auth, phishing-resistant MFA, monitoring) or an explicit accept-risk",
    "do": ["Prioritize Global Administrators, other privileged roles, VPN/remote-access users and accounts that still allow legacy authentication.",
           "Pair resets with Conditional Access that blocks legacy auth and requires phishing-resistant MFA for admins.",
           "Watch Entra sign-in logs for those UPNs after the action window for impossible-travel and legacy-protocol attempts.",
           "Feed repeated-breach addresses into security awareness and into password-spray detection tuning."],
    "pit": ["A mass reset without legacy-auth controls just moves the problem to the next spray. Close the protocol gap in the same change window."],
    "rec": ["ca-block-legacy-auth", "ca-break-glass", "pim-least-privilege-daily-ops"], "tools": ["hibp-domain-search"],
    "src": S("hibp_domain", "legacy", "pim", "signin_logs"),
    "marker": "practical"},
  ]},

 {
  "id": "web", "title": "Deepen selected web apps with ffuf and Burp Suite", "time": "2–5 days", "deep": True,
  "goal": "Content discovery and expert application testing on a short, named list of internet-facing apps — not an unscoped crawl of everything Amass found.",
  "steps": [
   {"t": "Pick the web targets that deserve human depth",
    "check": "A written shortlist (typically a handful of apps) names URLs, environments, accounts, data sensitivity and whether destructive tests are allowed",
    "do": ["Select from the verified exposure set: customer portals, VPN/web admin cousins that are actually apps, APIs tied to identity, and anything Nuclei marked interesting but unconfirmed.",
           "Require a named application owner and a test account (or token) before Burp work begins; prefer dedicated test identities over personal admin accounts.",
           "State explicitly whether authenticated testing, state-changing requests and fuzzing of write endpoints are in scope.",
           "Everything not on the shortlist stays at Nuclei/Nmap depth for this engagement."],
    "pit": ["'Just fuzz the whole Amass list' is how you knock over a partner's fragile staging host that CNAMEs through your DNS."],
    "rec": [], "tools": ["ffuf", "burp-suite", "internal-pentest-scoping"], "src": S("nist115", "burp_docs"),
    "marker": "practical"},
   {"t": "Content discovery with ffuf under strict rate and scope controls",
    "check": "ffuf runs are limited to shortlisted hosts, with wordlists, rate, match/filter rules and output paths recorded",
    "do": ["Run focused content discovery: `ffuf -u https://app.example.com/FUZZ -w <wordlist> -mc 200,204,301,302,307,401,403 -rate <n> -o ffuf-app.json` (tune match codes to the app).",
           "Keep recursion shallow unless the RoE allows deeper discovery; watch for calendars, backups, `.git`, admin consoles and forgotten API docs.",
           "Feed interesting paths to Burp rather than auto-exploiting them.",
           "Stop on application instability — availability incidents during fuzzing are your problem to prevent."],
    "pit": ["Aggressive ffuf against a shared front door (WAF/CDN) can trigger blocks that affect real users. Coordinate with the edge owner and keep rates modest."],
    "rec": [], "tools": ["ffuf"], "src": S("ffuf_gh", "mitre_ascan"),
    "marker": "official"},
   {"t": "Authenticated application testing with Burp Suite",
    "check": "Burp project files exist for each shortlisted app, with scope locked to the named hosts and findings written up with request evidence",
    "do": ["Use Burp Community or Professional with target scope set to the shortlisted hosts only; out-of-scope hosts belong in the deny list.",
           "Map the application, exercise authentication and session handling, and test for the classes your RoE allows (authZ flaws, IDOR, injection, JWT misuse, secondary auth bypass).",
           "Prefer manual, evidence-backed findings over unreviewed scanner noise; Professional's scanner is fine when you triage it like Nuclei.",
           "Export evidence with secrets redacted; never leave Burp project files with session tokens on a shared laptop."],
    "pit": ["Passive proxying of your own admin session into a report archive is a credential leak. Strip Authorization headers and cookies from anything that leaves the tester's workstation.",
            "State-changing tests in production need an explicit clause and a rollback owner — otherwise stay in a lower environment."],
    "rec": [], "tools": ["burp-suite", "ffuf"], "src": S("burp_docs", "burp_comm", "burp_pro", "nist115"),
    "marker": "practical"},
  ]},

 {
  "id": "detect", "title": "Prove detection of the external recon and scanning path", "time": "1–2 days", "deep": False,
  "goal": "Evidence that each noisy step was visible (or a documented detection gap): edge/WAF/IDS, DNS, identity and application logs.",
  "steps": [
   {"t": "Correlate edge, DNS and IDS/WAF alerts with the engagement timeline",
    "check": "For each active phase (Amass active, Nmap, Nuclei, ffuf) the SOC can show matching telemetry or a ticketed gap",
    "do": ["Match Nmap and Nuclei windows to firewall/IDS and WAF events by source IP and destination.",
           "Confirm DNS query logs show Amass active / enumeration patterns where those were used.",
           "Review Azure Front Door / Application Gateway WAF (or your equivalent) hits for the ffuf/Burp paths.",
           "File a detection-engineering ticket for every technique the RoE said should alert but did not."],
    "pit": ["Default WAF retention is short. Export evidence during the window, not a week later."],
    "rec": [], "tools": [], "src": S("waf_afd", "appgw_waf", "mitre_ascan"),
    "marker": "official"},
   {"t": "Confirm identity-plane visibility for HIBP-driven and app-test accounts",
    "check": "Entra sign-in and audit logs show the test accounts and any forced-reset activity; gaps are ticketed",
    "do": ["In Entra sign-in logs, filter to the Burp/test UPNs and confirm Conditional Access results on those events.",
           "Confirm that password-reset and privileged actions from the HIBP follow-up appear in audit logs.",
           "If you use Defender External Attack Surface Management or Secure Score exposure data, compare its inventory to yours — deltas are findings either way.",
           "Record any blind spot as a detection gap with the exact technique missed."],
    "pit": ["Report-only CA results are easy to misread — confirm the specific result codes in the sign-in details."],
    "rec": ["ca-report-only-first"], "tools": ["hibp-domain-search"], "src": S("signin_logs", "audit_acts", "defender_ext", "secure_score"),
    "marker": "official"},
  ]},

 {
  "id": "remediate", "title": "Remediate exposure, retest and close the engagement", "time": "1–4 weeks", "deep": False,
  "goal": "Internet-facing management and orphaned assets removed or locked down, identities hardened, a retest that shows the headline paths broken, and a clean wipe of engagement material.",
  "steps": [
   {"t": "Remove or lock down what should never have been on the internet",
    "check": "Every critical verified exposure has a closed change (removed public listener, IP allow list, SSO/WAF in front, or accepted risk with expiry)",
    "do": ["Prioritize management interfaces, VPN/remote-access portals with weak auth, open administrative APIs and plaintext protocols — see also the edge-hardening entry on this site.",
           "Prefer removal from the public internet over 'we'll put MFA on it later'. When it must stay public, put SSO + phishing-resistant MFA + WAF/named locations in front and narrow source IPs.",
           "Clean DNS and certificates for retired names still answering or still logging in CT as active brands.",
           "Track each fix with before/after Nmap or Shodan evidence."],
    "pit": ["An allow list that still includes '0.0.0.0/0 for troubleshooting' is not a fix. Expiry dates on exceptions are mandatory."],
    "rec": [], "tools": ["nmap", "shodan"], "sec": ["harden-edge-management-interfaces"],
    "guides": ["entra-private-access-vpn-replacement"],
    "src": S("cisa_asm", "waf_afd", "ca_named"),
    "marker": "practical"},
   {"t": "Close the identity and application findings from HIBP, Nuclei and Burp",
    "check": "HIBP-driven resets and CA changes are done for priority accounts; confirmed Nuclei/Burp findings have owners and due dates",
    "do": ["Complete the identity actions from phase 7: legacy auth blocked, privileged MFA hardened, repeated-breach accounts monitored.",
           "Remediate confirmed application findings through the app owner's SDLC; retest with Burp/ffuf after the fix lands.",
           "Where cloud configuration gaps appeared (public storage, open management), feed them into the cloud-hardening programme rather than fixing them as one-offs with no baseline.",
           "Keep break-glass exclusions intact on every new Conditional Access change."],
    "pit": ["Turning CA policies to On without Report-only is a classic lockout during an exposure programme that was supposed to reduce risk."],
    "rec": ["ca-report-only-first", "ca-block-legacy-auth", "ca-break-glass", "pim-least-privilege-daily-ops"],
    "tools": ["burp-suite", "nuclei"],
    "guides": ["cloud-hardening-adversary-emulation", "purple-team-hybrid-identity"],
    "src": S("legacy", "pim", "emerg"),
    "marker": "official"},
   {"t": "Retest the headline paths, wipe the loot and schedule continuous discovery",
    "check": "A dated retest shows the critical exposures closed, all engagement data is wiped or vaulted, and continuous external discovery is scheduled",
    "do": ["Re-run a minimal slice: crt.sh delta since the engagement, a short Amass passive pass, Shodan on the previously bad IPs, Nmap on the previously open management ports, and Nuclei against the fixed hosts.",
           "Securely delete or vault raw outputs: Amass DBs, Nmap/Nuclei/ffuf artifacts, Burp projects, HIBP exports and any captured tokens.",
           "Disable assessment accounts and rotate any credentials or API keys used.",
           "Write the report as scope, inventory deltas, headline exposures, remediations, detection gaps, residual risk and retest date — then book continuous discovery (Shodan monitors, Defender EASM or equivalent, recurring Amass passive), because attack surface drifts quietly."],
    "pit": ["A forgotten Burp project with session cookies, or an un-wiped HIBP export in a shared drive, is a breach of your own making.",
            "Do not claim 'tested configuration' on Tenant Recipes unless a named lab and date exist; a retest that closes an exposure is engagement evidence, not a lab certification."],
    "rec": [], "tools": ["crt-sh", "amass", "shodan", "nmap", "nuclei"], "src": S("nist115", "cisa_asm", "defender_ext"),
    "marker": "practical"},
  ]},
]
