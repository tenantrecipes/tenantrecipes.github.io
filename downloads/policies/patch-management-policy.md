# Patch and Vulnerability Management Policy

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | Sets how quickly {{COMPANY}} installs security updates and fixes vulnerabilities, based on risk. |
| Audience | IT operations, system and application owners, and service providers that manage {{COMPANY}} systems. |
| Review | Every 12 months. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Purpose

Many attacks use known vulnerabilities for which a fix already exists. Patching on time, starting with what is actively exploited, removes that easy route.

## 2. Scope

It covers operating systems, applications, firmware, network and security devices, virtualisation platforms and cloud services that {{COMPANY}} manages.

## 3. Inventory

IT keeps an up-to-date inventory of hardware and software with an owner for each system. Systems that are not in the inventory cannot be patched reliably and must be added or removed.

The inventory includes self-hosted AI and developer platforms (for example AI gateways, model-serving clusters and MCP servers) and appliances built on Linux distributions, not only Windows servers and clients.

## 4. Timelines

- Vulnerabilities known to be exploited (for example listed in the CISA Known Exploited Vulnerabilities catalog) on internet-facing systems: fix or mitigate as fast as possible, and within {{PATCH_DAYS_CRITICAL}} days at the most.
- Other critical vulnerabilities: within {{PATCH_DAYS_CRITICAL}} days.
- High: within {{PATCH_DAYS_HIGH}} days.
- Medium and low: within {{PATCH_DAYS_OTHER}} days, or in the normal update cycle.
- Monthly vendor updates, such as Microsoft's Patch Tuesday, are deployed through test, pilot and broad rings.

## 5. When you cannot patch

- Apply the vendor's workaround or another mitigation, such as blocking access or turning off the vulnerable feature.
- Record a time-limited exception with the risk owner's approval.
- Plan to replace software and devices that no longer receive security updates.
- Products that embed another vendor's code (for example Chromium-based browsers, or appliances built on open-source components) are patched only when their own vendor ships a fixed build. An upstream fix does not close the risk; track the downstream vendor's release notes and record an exception with a mitigation until it ships.

## 6. Verification

- Vulnerability scans run at least monthly on internal systems and at least weekly on internet-facing systems.
- Patch compliance is reported monthly to {{OWNER}}, including overdue items and exceptions.
- A fix counts as deployed only when the patched code is actually running: services and daemons are restarted (or the host rebooted) after a package update, and the running version is checked, not just the installed package.
- For vulnerabilities known to be exploited, the system owner also checks for signs of compromise (unexpected accounts, keys, tokens or configuration changes) before closing the ticket, and rotates credentials that may have been exposed.

## 7. Exceptions

Exceptions must be requested in writing, explain the business reason and the risk, include compensating measures, and have an end date. {{OWNER}} approves or rejects them and keeps a record.

## 8. Compliance

Breaches of this policy may lead to access being removed and to action under employment or contract terms. Report suspected breaches to {{SECURITY_CONTACT}}.

## 9. Ownership and review

Policy owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Framework references

Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.

- **ISO/IEC 27001:2022 Annex A theme:** Technological controls (clause 8)
- **NIST CSF 2.0:** Identify · ID.AM Asset Management
- **NIST CSF 2.0:** Identify · ID.RA Risk Assessment
- **NIST CSF 2.0:** Protect · PR.PS Platform Security
- **CIS Controls v8:** Control 1: Inventory and Control of Enterprise Assets
- **CIS Controls v8:** Control 2: Inventory and Control of Software Assets
- **CIS Controls v8:** Control 7: Continuous Vulnerability Management

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example
- `{{PATCH_DAYS_CRITICAL}}`: Days to fix critical or exploited vulnerabilities
- `{{PATCH_DAYS_HIGH}}`: Days to fix high vulnerabilities
- `{{PATCH_DAYS_OTHER}}`: Days to fix medium and low vulnerabilities

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
