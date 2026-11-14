"""Pillar guide: Secure your website.
Vendor-neutral hardening for public websites (static hosts + optional CDN).
Documentation checked against linked primary sources on 2026-11-09; not lab-tested.
"""

SLUG = "secure-your-website"
TIER = "pillar"
PUBLISHED = "2026-11-09"  # draft date; set real publish date on approval
VERIFIED = "2026-11-09"
UPDATED = "2026-11-09"
TITLE = "Secure your website: accounts, DNS, hosting, third parties"
SHORT = "Secure your website"
DESC = (
    "A vendor-neutral programme to harden a public website: phishing-resistant accounts, "
    "domain verification and DNS hygiene, TLS and security headers, CI/CD pinning and least "
    "privilege, first-party code and third-party scripts, integrations and privacy, monitoring, "
    "then backup and a prioritised checklist. Documentation verified; not lab-tested."
)
BADGE = "documentation verified against linked primary sources; not lab-tested"
SRC_LABEL = "Primary sources"
TIME_NOTE = (
    "Time estimates are Tenant Recipes planning figures for a small public site "
    "(one domain, static or lightly dynamic hosting), not vendor SLAs."
)
CTA_FIRST = "Start with the accounts that can rewrite the site →"

INTRO = [
    "Most website compromises do not start with a clever exploit against your carefully written HTML. "
    "They start somewhere quieter: a registrar account without phishing-resistant sign-in, a DNS CNAME "
    "that still points at a decommissioned host, a CI job that pulls a third-party Action by a movable "
    "tag, or a JavaScript CDN you added years ago and never looked at again.",
    "Public reporting keeps making the same point. GitHub documents that custom domains for Pages can "
    "be taken over when DNS remains after the site is unlinked, and that account-level domain "
    "verification exists to stop other accounts publishing to your name. Codecov disclosed in 2021 "
    "that its Bash Uploader had been altered so CI environments could leak credentials. In 2024 the "
    "widely embedded cdn.polyfill.io service began serving malicious redirects after a change of "
    "ownership. In March 2025 CISA warned that tj-actions/changed-files was compromised and could "
    "disclose secrets from workflow logs.",
    "This guide is a programme, not a vendor tour. It walks identity, DNS, hosting and headers, the "
    "publishing pipeline, code and third-party scripts, integrations and privacy, monitoring, then "
    "backup — and ends with a prioritised checklist. Use it on sites you own or are authorised to "
    "harden. Nothing here claims lab testing by Tenant Recipes; it is checked against the linked "
    "documentation.",
]

NAMING = (
    "Scope: public websites on common static hosts (GitHub Pages, Netlify, Cloudflare Pages and "
    "similar), with or without a CDN. Mail DNS is covered where it shares the zone. Defensive "
    "hardening only on systems you own or have written authorisation to change. Tenant Recipes is "
    "not affiliated with the vendors named in the sources. "
)

NOTICE = {
    "title": "Evidence boundary",
    "text": (
        "Incident examples are attributed to the linked vendor or agency publications "
        "(GitHub, Codecov, Sansec, Cloudflare, CISA, NIST, OWASP, MDN). Editorial framing that "
        "many compromises begin with account or supply-chain weakness is illustrative, not a "
        "statistical study. Product-specific registrar UI labels vary by vendor."
    ),
}

HISTORY = [
    ("2026-11-09", "Published eight-phase vendor-neutral website hardening programme; documentation verified, not lab-tested."),
]


def S(*keys):
    return [L[k] for k in keys]


L = {
    "gh_verify": (
        "GitHub: Verifying your custom domain for GitHub Pages",
        "https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages",
    ),
    "gh_actions": (
        "GitHub: Security hardening for GitHub Actions",
        "https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions",
    ),
    "cisa_tj": (
        "CISA: Supply chain compromise of tj-actions/changed-files (CVE-2025-30066)",
        "https://www.cisa.gov/news-events/alerts/2025/03/18/supply-chain-compromise-third-party-tj-actionschanged-files-cve-2025-30066-and-reviewdogaction",
    ),
    "codecov": (
        "Codecov: Bash Uploader Security Update (15 April 2021)",
        "https://about.codecov.io/security-update/",
    ),
    "sansec_poly": (
        "Sansec: Polyfill supply chain attack",
        "https://sansec.io/research/polyfill-supply-chain-attack",
    ),
    "cf_poly": (
        "Cloudflare: Replacing polyfill.io links with a mirror",
        "https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/",
    ),
    "nist_63b": (
        "NIST SP 800-63B: Authentication and lifecycle management",
        "https://pages.nist.gov/800-63-4/sp800-63b.html",
    ),
    "nist_sync": (
        "NIST: Supplement for syncable authenticators (passkeys)",
        "https://www.nist.gov/blogs/cybersecurity-insights/giving-nist-digital-identity-guidelines-boost-supplement-incorporating",
    ),
    "owasp_sub": (
        "OWASP WSTG: Subdomain takeover",
        "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management/10-Subdomain_Takeover",
    ),
    "rfc9116": ("RFC 9116: security.txt", "https://www.rfc-editor.org/rfc/rfc9116.html"),
    "mdn_csp": ("MDN: Content Security Policy", "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"),
    "mdn_hsts": (
        "MDN: Strict-Transport-Security",
        "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security",
    ),
    "ssllabs": ("SSL Labs Server Test", "https://www.ssllabs.com/ssltest/"),
    "secheaders": ("SecurityHeaders.com", "https://securityheaders.com/"),
    "observatory": (
        "MDN HTTP Observatory",
        "https://developer.mozilla.org/en-US/observatory",
    ),
    "zap": ("OWASP ZAP", "https://www.zaproxy.org/"),
}

PHASES = [
    {
        "id": "accounts",
        "title": "Lock the accounts that can rewrite the site",
        "time": "Half a day",
        "deep": True,
        "goal": "Every account that can change DNS, source, hosting or analytics has phishing-resistant sign-in, offline recovery and a reviewed token inventory.",
        "lead": "If an attacker can sign in as you at the registrar or the git forge, the rest of the checklist is theatre.",
        "steps": [
            {
                "t": "Turn on phishing-resistant MFA on registrar, host, git and SaaS",
                "check": "Registrar, DNS host, git forge, hosting/CDN, newsletter and analytics each show a passkey or hardware key enrolled, with recovery codes stored offline",
                "do": [
                    "Prefer phishing-resistant authenticators. NIST SP 800-63B describes phishing resistance as binding authenticator output to the legitimate verifier so a fake login page cannot replay it; OTP codes typed by hand are not phishing-resistant.",
                    "Enrol a platform or device-bound passkey where the service supports WebAuthn; keep a second factor and printed recovery codes offline.",
                    "Apply the same bar to personal accounts that own the organisation, not only the org settings page.",
                ],
                "pit": [
                    "SMS or push-only MFA still fails open to phishing and MFA fatigue.",
                    "A passkey on one laptop without recovery is a lockout risk.",
                ],
                "src": S("nist_63b", "nist_sync"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Inventory sessions, OAuth apps and long-lived tokens",
                "check": "A dated inventory lists active sessions, OAuth apps, PATs/deploy keys and CI secrets with owners and expiry",
                "do": [
                    "Review git forge security settings: sessions, SSH keys, PATs, deploy keys and authorised OAuth apps; revoke unknowns and rotate anything pasted into chat or tickets.",
                    "Prefer short-lived OIDC / workload identity over static deploy secrets where the host supports it.",
                ],
                "pit": [
                    "SSO alone does not retire old PATs. A forgotten deploy key is still write access.",
                ],
                "src": S("gh_actions", "codecov"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Protect the registrar and DNS console like production Tier 0",
                "check": "Registrar login has MFA, transfer/registrar lock is on, and who can create DNS records is named",
                "do": [
                    "Enable registrar lock (clientTransferProhibited or vendor equivalent) and restrict DNS API tokens.",
                    "Treat the domain contact mailbox with the same MFA bar as the registrar — inbox takeover often resets domains.",
                ],
                "pit": [
                    "Registrar lock UI labels vary by TLD and vendor — confirm in your registrar's own docs (not verified as one universal control name).",
                ],
                "src": S("gh_verify"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "dns-tls",
        "title": "Domain, DNS, DNSSEC, CAA and TLS",
        "time": "Half a day to 1 day",
        "deep": True,
        "goal": "Name ownership is proven to the host, certificates are constrained, and dangling records cannot be claimed by strangers.",
        "steps": [
            {
                "t": "Verify the custom domain with the publishing host",
                "check": "The host shows the apex (and www if used) as verified, and the verification TXT remains in DNS",
                "do": [
                    "On GitHub Pages, add the account/org domain verification TXT (_github-pages-challenge-<owner>) and keep it. GitHub states this stops other users publishing to the verified domain and its immediate subdomains.",
                    "Do not point wildcard DNS at a multi-tenant host. GitHub warns wildcards create takeover risk even after verification.",
                    "When retiring a subdomain, delete the DNS record and unlink it in the host — dangling CNAMEs are the classic takeover pattern.",
                ],
                "pit": [
                    "Repository-level custom domain alone is not account-level verification.",
                    "A host 404 fingerprint is a reason to investigate, not proof the name is safe.",
                ],
                "src": S("gh_verify", "owasp_sub"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Publish CAA and finish DNSSEC properly — or turn it off cleanly",
                "check": "CAA allows only the CAs you intend; DNSSEC either has a matching DS at the parent or is fully disabled",
                "do": [
                    "Start with a tight CAA (issue for your certificate issuer; issuewild denied unless required). Re-open CAA before adding a CDN or mail product that needs another CA.",
                    "Half-enabled DNSSEC (DNSKEY without DS) helps nobody — publish DS after enabling, or remove incomplete state.",
                ],
                "pit": [
                    "Moving nameservers to a CDN without copying CAA/MX/TXT breaks mail and certificates together.",
                ],
                "src": S("gh_verify"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Enforce HTTPS end-to-end",
                "check": "HTTP redirects to HTTPS, the certificate covers the names users type, and weak TLS is disabled at the edge",
                "do": [
                    "Prefer full (strict) style origin checks when a CDN sits in front of the origin.",
                    "Plan HSTS only once every hostname users might type is stably on HTTPS (Phase 3).",
                ],
                "pit": [],
                "src": S("mdn_hsts", "ssllabs"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "headers",
        "title": "Hosting and browser security headers",
        "time": "About 1 day",
        "deep": False,
        "goal": "The edge sends HSTS and framing/MIME/Permissions policy; CSP is enforced without unsafe-inline sprawl.",
        "steps": [
            {
                "t": "Know what your host can and cannot set",
                "check": "A short matrix lists which headers the origin can set versus which need a CDN or platform config",
                "do": [
                    "Some static hosts do not expose arbitrary response headers. CSP via meta can cover script policy but cannot set frame-ancestors or HSTS.",
                    "Target set: HSTS max-age=63072000; includeSubDomains (preload only when every subdomain is clean); CSP with hashed/nonced script, object-src none, tight form-action and frame-ancestors none; nosniff; Referrer-Policy strict-origin-when-cross-origin; Permissions-Policy disabling unused powerful features.",
                ],
                "pit": [
                    "Meta CSP is better than nothing; it is not a substitute for HTTP CSP where framing matters.",
                ],
                "src": S("mdn_csp", "mdn_hsts"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Self-host first-party assets; SRI for any third-party URL",
                "check": "Third-party script and stylesheet tags are removed, self-hosted, or carry integrity plus crossorigin",
                "do": [
                    "After polyfill.io, treat add this one CDN line as a standing risk: ownership of a popular hostname can change.",
                    "Pin versions; SRI does not help if the URL returns different bytes over time.",
                ],
                "pit": [],
                "src": S("sansec_poly", "cf_poly"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "pipeline",
        "title": "Harden the publishing pipeline",
        "time": "Half a day to 1 day",
        "deep": True,
        "goal": "Only trusted commits can publish; Actions run least privilege and cannot silently swap under a tag.",
        "lead": "CI is part of production identity. Mutable tags and broad tokens turn a third-party Action into a deploy key.",
        "steps": [
            {
                "t": "Pin Actions to full commit SHAs (or adopt a lockfile)",
                "check": "Every uses: line references a full-length commit SHA or a workflow lockfile, not a floating major tag",
                "do": [
                    "GitHub recommends pinning to a full-length commit SHA because tags can move.",
                    "The March 2025 tj-actions/changed-files compromise showed tags retargeted to a malicious commit; hash-pinned workflows outside those SHAs were not pulled along.",
                    "Restrict allowed Actions where possible and enable Dependabot for github-actions.",
                ],
                "pit": [
                    "Pinning @v4 is not pinning. Verify SHAs come from the upstream action repository, not a fork.",
                ],
                "src": S("gh_actions", "cisa_tj"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Least-privilege tokens, rulesets and secret scanning",
                "check": "Default GITHUB_TOKEN is read-only; write permissions are job-scoped; secret scanning and push protection are on; the default branch blocks force-push and deletion",
                "do": [
                    "Scope contents/pages write to the job that needs them. Enable secret scanning, push protection and Dependabot alerts.",
                    "Remember CI environment variables are high-value — the 2021 Codecov Bash Uploader incident showed how a compromised uploader can export them.",
                ],
                "pit": [
                    "pull_request_target checking out untrusted code is a classic privilege path — avoid unless you fully understand the model.",
                ],
                "src": S("gh_actions", "codecov"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "code-scripts",
        "title": "Code patterns and third-party JavaScript",
        "time": "Half a day",
        "deep": False,
        "goal": "First-party code avoids dangerous sinks; every external script has an owner and a removal date.",
        "steps": [
            {
                "t": "Ban the usual DOM and XSS footguns in first-party JS",
                "check": "Review finds no eval/new Function/document.write; innerHTML only with escaped data; target=_blank uses rel=noopener noreferrer",
                "do": [
                    "Keep a build-time check that fails on inline event handlers if you rely on a strict CSP.",
                ],
                "pit": [
                    "Template literals into innerHTML are still XSS if any field is user-controlled.",
                ],
                "src": S("mdn_csp"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
            {
                "t": "Maintain a bill of what the browser loads",
                "check": "A short inventory lists every script, connect and image endpoint the browser hits in production",
                "do": [
                    "Re-read CSP and DevTools Network on a cold load; drop unused tags.",
                ],
                "pit": [],
                "src": S("sansec_poly"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "integrations",
        "title": "Integrations, forms, analytics and privacy",
        "time": "Half a day",
        "deep": False,
        "goal": "Every byte that leaves the browser has a documented purpose, notice and kill switch.",
        "steps": [
            {
                "t": "Align privacy text with newsletter, forms and analytics reality",
                "check": "Privacy text matches cookies, localStorage, processors and regions; forms POST only to endpoints allowed by CSP form-action",
                "do": [
                    "If opt-out uses localStorage, say so. Document where newsletter processors store addresses.",
                    "Publish /.well-known/security.txt with a monitored contact and expiry; enable private vulnerability reporting on public repos.",
                ],
                "pit": [
                    "A privacy page that denies local storage while an opt-out flag uses it is a credibility bug.",
                ],
                "src": S("rfc9116", "mdn_csp"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "monitor",
        "title": "Monitoring and recurring checks",
        "time": "1–2 hours setup; quarterly thereafter",
        "deep": False,
        "goal": "HTTPS, headers and passive findings are checked on a calendar, not only at launch.",
        "steps": [
            {
                "t": "Run external scoreboards and keep the artefacts",
                "check": "Dated results exist from SSL Labs (or equivalent), SecurityHeaders or Observatory, and a passive ZAP scan against your own site",
                "do": [
                    "Store PDFs or screenshots with dates. Use SSL Labs, SecurityHeaders and the MDN HTTP Observatory (successor to observatory.mozilla.org).",
                    "Passive ZAP only against hosts you own or are authorised to test.",
                ],
                "pit": [
                    "A green scoreboard does not prove registrar MFA is on.",
                ],
                "src": S("ssllabs", "secheaders", "observatory", "zap"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
    {
        "id": "recovery",
        "title": "Backup, recovery and prioritised checklist",
        "time": "Half a day",
        "deep": False,
        "goal": "You can rebuild the site and regain the domain after account loss; work is ordered by blast radius.",
        "steps": [
            {
                "t": "Recovery drill and prioritised order of work",
                "check": "Offline notes cover registrar, DNS, git and host recovery; the prioritised checklist below is assigned to named owners",
                "do": [
                    "Critical/High — accounts: passkeys/MFA and token review on registrar, DNS, git, host, newsletter, analytics.",
                    "High — domain claim: host verification TXT; no wildcards; clean dangling CNAMEs.",
                    "High — pipeline: SHA-pin Actions; least-privilege tokens; secret scanning; protect default branch.",
                    "Medium — edge headers via CDN/host; third-party script inventory; mail SPF/DKIM/DMARC if same zone.",
                    "Low — finish or disable DNSSEC; Dependabot for Actions; security.txt expiry; disable unused wiki/projects.",
                    "Recurring quarterly — SSL/headers/passive ZAP; token inventory; CT and Search Console review.",
                ],
                "pit": [
                    "Do not store break-glass secrets in the public repository.",
                ],
                "src": S("gh_verify", "gh_actions", "cisa_tj", "codecov", "sansec_poly"),
                "rec": [],
                "tools": [],
                "marker": "practical",
            },
        ],
    },
]
