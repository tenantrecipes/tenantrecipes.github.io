"""Interactive, fully client-side tools (no backend, nothing stored):
  - code/ca-policy-generator.html  Conditional Access policy generator (assets/ca-gen.js)
  - tools/mail-dns-checker.html    Mail DNS checker via DNS-over-HTTPS (assets/mail-dns.js)
Logic lives in the JS files so tests/test_apps.js can run it in Node. The DNS checker is the only page that may
connect to other hosts: tools/security_meta.py adds exactly the two DoH resolvers to its connect-src (EXTRA_CONNECT)."""
import build_trust as T
import build_markers as MK

VERIFIED = "2026-10-31"
CA_PATH, DNS_PATH = "code/ca-policy-generator.html", "tools/mail-dns-checker.html"
DOH_HOSTS = "https://cloudflare-dns.com https://dns.google"

CA_SOURCES = [
    ("conditionalAccessPolicy resource type (Microsoft Graph v1.0)", "https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccesspolicy?view=graph-rest-1.0"),
    ("conditionalAccessConditionSet resource type", "https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessconditionset?view=graph-rest-1.0"),
    ("conditionalAccessGrantControls resource type (incl. passwordChange rules)", "https://learn.microsoft.com/en-us/graph/api/resources/conditionalaccessgrantcontrols?view=graph-rest-1.0"),
    ("Create conditionalAccessPolicy (permissions and examples)", "https://learn.microsoft.com/en-us/graph/api/conditionalaccessroot-post-policies?view=graph-rest-1.0"),
    ("New-MgIdentityConditionalAccessPolicy (Microsoft Graph PowerShell)", "https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.identity.signins/new-mgidentityconditionalaccesspolicy"),
    ("List authenticationStrengthPolicies (built-in strength IDs)", "https://learn.microsoft.com/en-us/graph/api/authenticationstrengthroot-list-policies?view=graph-rest-1.0"),
    ("Conditional Access authentication strengths", "https://learn.microsoft.com/en-us/entra/identity/authentication/concept-authentication-strengths"),
    ("Microsoft Entra built-in roles (role template IDs)", "https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/permissions-reference"),
    ("Manage emergency access accounts in Microsoft Entra ID", "https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access"),
    ("Report-only mode", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-report-only"),
    ("Common Conditional Access policies", "https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policy-common"),
]
CA_SCENARIO_SOURCES = [
    ("Require MFA for all users (authentication strength)", "policy-all-users-mfa-strength"),
    ("Block legacy authentication", "policy-block-legacy-authentication"),
    ("Require a compliant device", "policy-all-users-device-compliance"),
    ("Require phishing-resistant MFA for administrators", "policy-admin-phish-resistant-mfa"),
    ("Require MFA for elevated sign-in risk", "policy-risk-based-sign-in"),
    ("Require remediation for risky users", "policy-risk-based-user"),
    ("Block authentication flows (device code flow)", "policy-block-authentication-flows"),
    ("Protect security info registration", "policy-all-users-security-info-registration"),
]
DNS_SOURCES = [
    ("Set up SPF to identify valid email sources for your Microsoft 365 domain", "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-spf-configure"),
    ("Set up DKIM to sign mail from your Microsoft 365 domain", "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dkim-configure"),
    ("Set up DMARC to validate the From address domain", "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dmarc-configure"),
    ("Email authentication in Microsoft 365", "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-about"),
    ("Enhancing mail flow with MTA-STS (Exchange Online)", "https://learn.microsoft.com/en-us/exchange/security-and-compliance/enhance-mail-flow-using-strict-transport-security"),
    ("Add DNS records to connect your domain (Microsoft 365)", "https://learn.microsoft.com/en-us/microsoft-365/admin/get-help-with-domains/create-dns-records-at-any-dns-hosting-provider"),
    ("RFC 7208: Sender Policy Framework (SPF)", "https://www.rfc-editor.org/rfc/rfc7208.html"),
    ("RFC 7489: DMARC", "https://www.rfc-editor.org/rfc/rfc7489.html"),
    ("RFC 8461: SMTP MTA Strict Transport Security (MTA-STS)", "https://www.rfc-editor.org/rfc/rfc8461.html"),
    ("RFC 8460: SMTP TLS Reporting", "https://www.rfc-editor.org/rfc/rfc8460.html"),
    ("RFC 8659: DNS Certification Authority Authorization (CAA)", "https://www.rfc-editor.org/rfc/rfc8659.html"),
    ("RFC 7505: A \"Null MX\" No Service Resource Record", "https://www.rfc-editor.org/rfc/rfc7505.html"),
    ("Cloudflare DNS-over-HTTPS JSON API", "https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/make-api-requests/dns-json/"),
    ("Google Public DNS JSON API", "https://developers.google.com/speed/public-dns/docs/doh/json"),
]


def promo(rel, here=""):
    """Small strip linking both interactive tools; shown on /code/ and /tools/."""
    items = [(CA_PATH, "Conditional Access policy generator", "Pick a scenario, get Graph JSON and PowerShell. Report-only by default."),
             (DNS_PATH, "Mail DNS checker", "MX, SPF lookups, DMARC, DKIM, MTA-STS, TLS-RPT and CAA, graded in your browser.")]
    return ('<section class="ap-promo" aria-labelledby="ap-promo-h"><p class="sec-k" id="ap-promo-h">Interactive tools · run in your browser</p><div class="ap-pg">'
            + "".join(f'<a class="ap-pc" href="{rel}{p}"><strong>{t}</strong><span>{d}</span></a>' for p, t, d in items if p != here)
            + '</div></section>')


def _sources(items):
    return '<ul class="st-l">' + "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in items) + '</ul>'


def _dates(fmt_date):
    return (f'<p class="pd"><span><b>Published</b> <time datetime="{VERIFIED}">{fmt_date(VERIFIED)}</time></span>'
            f'<span><b>Last verified</b> <time datetime="{VERIFIED}">{fmt_date(VERIFIED)}</time></span><a href="#sources">Sources</a></p>')


def ca_body(rel, fmt_date, signup):
    radio = lambda name, val, label, on=False: (f'<label class="ap-r"><input type="radio" name="{name}" value="{val}"{" checked" if on else ""}> {label}</label>')
    form = ('<form class="ap-form" id="cag-form" autocomplete="off" novalidate>'
            '<div class="ap-f"><label for="cag-scn">Scenario</label><select id="cag-scn"></select></div>'
            '<div class="ap-f"><label for="cag-name">Policy name</label><input id="cag-name" type="text" maxlength="256" spellcheck="false"></div>'
            '<fieldset class="ap-f"><legend>State</legend>'
            + radio("cag-state", "enabledForReportingButNotEnforced", "Report-only <span class=\"fine\">(default)</span>", True)
            + radio("cag-state", "disabled", "Off") + radio("cag-state", "enabled", "On") + '</fieldset>'
            '<fieldset class="ap-f" id="cag-row-scope"><legend>Users</legend>'
            + radio("cag-scope", "all", "All users", True) + radio("cag-scope", "group", "Pilot group")
            + '<label class="sr" for="cag-pilot">Pilot group object ID</label><input id="cag-pilot" type="text" placeholder="Pilot group object ID (GUID)" spellcheck="false" disabled>'
            '<p class="ap-err" id="cag-pilot-err" hidden>Not a valid GUID.</p></fieldset>'
            '<fieldset class="ap-f"><legend>Emergency access</legend>'
            '<label class="ap-r"><input type="checkbox" id="cag-bgon" checked> Exclude break-glass group</label>'
            '<label class="sr" for="cag-bg">Break-glass group object ID</label><input id="cag-bg" type="text" placeholder="Break-glass group object ID (GUID)" spellcheck="false">'
            '<p class="ap-err" id="cag-bg-err" hidden>Not a valid GUID.</p>'
            '<label class="ap-r" id="cag-row-dirsync"><input type="checkbox" id="cag-dirsync" checked> Exclude the Directory Synchronization Accounts role (Entra Connect / Cloud Sync)</label></fieldset>'
            '<fieldset class="ap-f" id="cag-row-grant"><legend>Grant</legend>'
            + radio("cag-grant", "strength", "Require authentication strength <span class=\"fine\">(recommended)</span>", True)
            + radio("cag-grant", "mfa", "Require multifactor authentication <span class=\"fine\">(if you use external authentication methods)</span>") + '</fieldset>'
            '<div class="ap-f" id="cag-row-strength"><label for="cag-strength">Authentication strength</label><select id="cag-strength"></select></div>'
            '<label class="ap-r" id="cag-row-hybrid"><input type="checkbox" id="cag-hybrid"> Also accept Microsoft Entra hybrid joined devices</label>'
            '<p><button type="reset" class="btn rx-b" id="cag-reset">Reset</button></p></form>')
    about = ('<section class="ap-about" aria-live="polite"><p class="ap-k">What this policy does</p><p id="cag-what"></p>'
             '<p class="fine"><b>License:</b> <span id="cag-lic"></span> · <b>State:</b> <span id="cag-state-lbl"></span></p>'
             '<p><a id="cag-learn" href="https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-policy-common">Microsoft Learn</a></p>'
             f'<p class="ap-k">Before you run it {MK.badge(rel, "practical")}</p><ul id="cag-notes"></ul>'
             '<p class="cag-valid" id="cag-valid"></p></section>')
    out = ('<section class="ap-out" aria-label="Generated policy">'
           '<h2 id="ps">PowerShell (Microsoft Graph SDK)</h2><pre class="cb"><code id="cag-ps"></code></pre>'
           '<h2 id="json">Graph JSON body</h2><pre class="cb"><code id="cag-json"></code></pre>'
           '<h2 id="http">Graph HTTP request</h2><pre class="cb"><code id="cag-http"></code></pre></section>')
    how = ('<section class="ap-how"><h2 id="how">How to use it safely</h2><ol class="steps">'
           '<li><div>Create (or reuse) a group with your two cloud-only emergency access accounts and paste its object ID above. Every generated policy excludes it unless you untick the box.</div></li>'
           '<li><div>Run the PowerShell as at least a Conditional Access Administrator. <code>Connect-MgGraph</code> asks for <code>Policy.Read.All</code> and <code>Policy.ReadWrite.ConditionalAccess</code>, the least-privileged pair the create API documents.</div></li>'
           '<li><div>Leave the policy in report-only for one to two weeks and review the policy impact view or the Conditional Access insights and reporting workbook. Use What If for guests and service accounts.</div></li>'
           '<li><div>Switch to On in a change window. To roll back, set the policy to Off or report-only; don\'t delete it, so you keep its history.</div></li></ol>'
           f'<p class="fine">{MK.badge(rel, "official")} Scenario settings follow Microsoft\'s own policy articles, and the JSON uses only property names and values from the Graph v1.0 resource pages linked below. '
           'Generated policies haven\'t been applied in a test tenant by us: test them in report-only first.</p></section>')
    return (T.page_hero(rel, T.crumbs_dark(rel, CA_PATH, [("Home", rel + "index.html"), ("Code Library", rel + "code/index.html"), ("CA policy generator", None)]),
                        f'{T.icon("shield")}Interactive tool · Conditional Access', "Conditional Access policy generator",
                        "Pick a scenario and your exclusions, then copy a Microsoft Graph JSON body or a ready-to-run PowerShell command. "
                        "Every policy starts in report-only. Runs entirely in your browser: nothing you type leaves this page.", kind="page")
            + '<main class="wrap pg"><article class="doc ap">' + _dates(fmt_date)
            + '<aside class="co co-info"><p class="co-h">' + T.icon("shield") + 'Private by design</p><p>The generator is plain JavaScript on this page. '
            'Group IDs and names you enter are never sent anywhere, stored or logged. There are no cookies and no network requests.</p></aside>'
            + '<div class="ap-grid">' + form + about + '</div>' + out + how
            + '<section class="st" id="sources"><h2>Sources</h2><p class="fine">Schema and IDs:</p>' + _sources(CA_SOURCES)
            + '<p class="fine">Scenario articles (Microsoft Learn):</p>'
            + _sources([(t, "https://learn.microsoft.com/en-us/entra/identity/conditional-access/" + s) for t, s in CA_SCENARIO_SOURCES]) + '</section>'
            + f'<p>Related: <a href="{rel}recipes/ca-break-glass.html">Keep break-glass accounts out of every policy</a> · '
            f'<a href="{rel}recipes/ca-report-only-first.html">Roll out in report-only first</a> · <a href="{rel}code/ca-check-emergency-exclusions.html">Check exclusions with PowerShell</a></p>'
            + promo(rel, CA_PATH) + '</article>'
            + f'<script src="{rel}assets/ca-gen.js" defer></script>' + signup(rel, "ca-generator") + '</main>')


def dns_body(rel, fmt_date, signup):
    return (T.page_hero(rel, T.crumbs_dark(rel, DNS_PATH, [("Home", rel + "index.html"), ("Tools", rel + "tools/index.html"), ("Mail DNS checker", None)]),
                        f'{T.icon("shield")}Interactive tool · Email security', "Mail DNS checker",
                        "Type a domain and get a graded check of MX, SPF (with DNS lookup count), DMARC, Microsoft 365 DKIM, MTA-STS, TLS-RPT, CAA and DNSSEC, "
                        "with what to fix and the Microsoft Learn article for each.", kind="page")
            + '<main class="wrap pg"><article class="doc ap">' + _dates(fmt_date)
            + '<aside class="co co-info" id="privacy"><p class="co-h">' + T.icon("shield") + 'No data stored</p><p>The check runs in your browser. '
            'Your browser asks <a href="https://developers.cloudflare.com/1.1.1.1/privacy/public-dns-resolver/">Cloudflare\'s public DNS resolver</a> directly over HTTPS '
            '(and <a href="https://developers.google.com/speed/public-dns/privacy">Google Public DNS</a> if Cloudflare doesn\'t answer). '
            'The domain you type is never sent to Tenant Recipes, and nothing is stored, logged or put in the page address. '
            'Only public DNS records are read; no mail is sent and no server is probed.</p></aside>'
            '<form class="ap-form mdc-form" id="mdc-form" autocomplete="off"><label for="mdc-domain">Domain</label>'
            '<div class="mdc-row"><input id="mdc-domain" type="text" inputmode="url" placeholder="contoso.com" spellcheck="false" autocapitalize="off" required>'
            '<button class="btn p" id="mdc-go" type="submit">Check</button></div>'
            '<p class="fine" id="mdc-status" aria-live="polite"></p></form>'
            '<div id="mdc-out" class="mdc-out" tabindex="-1"></div>'
            '<section class="ap-how"><h2 id="grading">How the grade works</h2><p>Each check gets a weight and a score: DMARC 30, SPF 25, DKIM 20, MTA-STS 7, MX 6, '
            'TLS-RPT 4, CAA 4 and DNSSEC 4 points. A is 90 or more, B 75, C 60, D 40. Checks that don\'t apply (for example MTA-STS on a domain with a null MX) score full points.</p>'
            '<ul><li><b>SPF:</b> exactly one <code>v=spf1</code> record, at most 10 DNS-querying terms counted recursively (include, a, mx, ptr, exists, redirect), and the <code>all</code> qualifier. '
            'Microsoft recommends <code>-all</code> for Microsoft 365 domains that also use DKIM and DMARC.</li>'
            '<li><b>DMARC:</b> policy (<code>reject</code> &gt; <code>quarantine</code> &gt; <code>none</code>), <code>pct</code>, an aggregate report address (<code>rua</code>), subdomain policy and alignment. '
            'Microsoft describes a gradual move from <code>none</code> through <code>quarantine</code> to <code>reject</code>.</li>'
            '<li><b>DKIM:</b> the two Microsoft 365 CNAMEs <code>selector1._domainkey</code> and <code>selector2._domainkey</code>. Other providers use other selectors, which this tool can\'t guess.</li>'
            '<li><b>MTA-STS and TLS-RPT:</b> the <code>_mta-sts</code> and <code>_smtp._tls</code> TXT records. The MTA-STS policy file itself isn\'t downloaded; the result links to it.</li>'
            '<li><b>CAA and DNSSEC:</b> which CAs may issue certificates, and whether the resolver validated the answer (AD flag).</li></ul>'
            f'<p class="fine">{MK.badge(rel, "official")} Explanations paraphrase the linked Microsoft Learn articles and RFCs. The weights are our own judgement, not a Microsoft score.</p></section>'
            + '<section class="st" id="sources"><h2>Sources</h2>' + _sources(DNS_SOURCES) + '</section>'
            + f'<p>Related: <a href="{rel}tools/mxtoolbox.html">MxToolbox</a> for deeper mail-flow tests · <a href="{rel}tools/index.html">all security tools</a></p>'
            + promo(rel, DNS_PATH) + '</article>'
            + f'<script src="{rel}assets/mail-dns.js" defer></script>' + signup(rel, "mail-dns-checker") + '</main>')


def build(page, esc, fmt_date, signup, SITE_NAME):
    pages = [
        page(CA_PATH, f"Conditional Access policy generator: Graph JSON and PowerShell | {SITE_NAME}",
             "Generate Microsoft Entra Conditional Access policies as Graph JSON or PowerShell: MFA, legacy auth, compliant device, admin phishing-resistant MFA, risk.",
             lambda rel: ca_body(rel, fmt_date, signup)),
        page(DNS_PATH, f"Mail DNS checker: SPF, DKIM, DMARC, MTA-STS and CAA | {SITE_NAME}",
             "Free mail DNS check in your browser: MX, SPF lookup count, DMARC policy, Microsoft 365 DKIM, MTA-STS, TLS-RPT, CAA and DNSSEC, graded. No data stored.",
             lambda rel: dns_body(rel, fmt_date, signup)),
    ]
    print(f"Interactive tools: {len(pages)} pages")
    return pages


def search_docs():
    return [
        {"t": "Conditional Access policy generator", "k": "Tool", "c": "Conditional Access", "u": CA_PATH,
         "s": "Generate Conditional Access policies as Microsoft Graph JSON or PowerShell (New-MgIdentityConditionalAccessPolicy), report-only by default, with break-glass exclusion.",
         "x": "conditional access generator template mfa legacy authentication compliant device phishing-resistant admins sign-in risk user risk device code flow security info registration graph json powershell"},
        {"t": "Mail DNS checker", "k": "Tool", "c": "Email security", "u": DNS_PATH,
         "s": "Check a domain's MX, SPF (DNS lookup count), DMARC, Microsoft 365 DKIM, MTA-STS, TLS-RPT, CAA and DNSSEC in your browser, with a grade and fixes.",
         "x": "spf dkim dmarc mta-sts tls-rpt caa dnssec mx email authentication checker exchange online"},
    ]
