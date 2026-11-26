# Third-Party and Vendor Security Policy

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | Ensures that suppliers who access {{COMPANY}} systems or data, or deliver critical services, meet appropriate security requirements. |
| Audience | Procurement, contract owners, legal, IT, security and anyone who buys or manages a service from a supplier. |
| Review | Every 12 months. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Purpose

Suppliers often have access to our data, systems or users, so a weakness at a supplier can become our incident. This policy makes supplier risk visible and managed.

## 2. Scope

It covers cloud and software providers, IT service providers, consultants, outsourcers and any supplier that handles {{COMPANY}} data or connects to its systems.

## 3. Before signing

- Every new supplier has an internal owner and a risk tier (low, medium or high) based on the data and access involved.
- Medium- and high-risk suppliers complete a security assessment, for example a questionnaire, certifications such as ISO/IEC 27001 or SOC 2 reports, and a review of their incident history.
- Contracts include security requirements, incident notification within an agreed time, audit or evidence rights, data location, subcontractor rules and return or deletion of data at the end.

## 4. During the contract

- Supplier access to systems uses named accounts, MFA, the least privilege needed and time limits.
- High-risk suppliers are reassessed every year, others at renewal.
- Supplier incidents that affect {{COMPANY}} are handled through the incident response policy.
- When a certificate authority used by a supplier is distrusted by browser or operating-system vendors, the supplier replaces affected certificates within the vendor's deadline, and {{COMPANY}} does not re-trust removed roots locally to keep a supplier service working.
- Suppliers that host services {{COMPANY}} signs in to keep those services compatible with current platform security defaults (for example signed authentication protocols and modern TLS) and announce incompatibilities before the vendor's enforcement date, not after.
- Suppliers that manage {{COMPANY}} devices through remote-support or RMM tools keep technician clients and console extensions on vendor-supported versions, notify {{COMPANY}} of any compromise of those tools without delay, and support out-of-band investigation of managed devices.
- Application identities that suppliers use to access {{COMPANY}} tenants (for example backup or migration apps) are inventoried with an owner, have only the permissions they need, and are reviewed at least yearly and after any supplier incident.
- {{OWNER}} makes sure security notices from cloud providers' official channels (for example Azure Service Health security advisories) are monitored for every tenant or subscription {{COMPANY}} owns, and that managed service providers forward such notices for {{COMPANY}} tenants without delay.
- When a supplier reports that its systems, source code or build pipeline were compromised, {{OWNER}} rotates every credential {{COMPANY}} stored in or shared with that service (API tokens, keys, configuration files and secrets), reviews logs of the systems those credentials reach from the start date the supplier gives, and warns users about phishing that uses the incident as a pretext.

## 5. Ending the relationship

- All supplier access is removed on the end date.
- Data is returned or deleted, and the supplier confirms this in writing.
- For each high-risk cloud service {{COMPANY}} keeps a documented, tested exit plan (data export and an alternative platform) so the service can be left within weeks if the supplier withdraws it, for example after a security incident.

## 6. Register

{{OWNER}} keeps a register of suppliers, their risk tier, owner, last assessment and contract end date.

## 7. Exceptions

Exceptions must be requested in writing, explain the business reason and the risk, include compensating measures, and have an end date. {{OWNER}} approves or rejects them and keeps a record.

## 8. Compliance

Breaches of this policy may lead to access being removed and to action under employment or contract terms. Report suspected breaches to {{SECURITY_CONTACT}}.

## 9. Ownership and review

Policy owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Framework references

Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.

- **ISO/IEC 27001:2022 Annex A theme:** Organizational controls (clause 5)
- **NIST CSF 2.0:** Govern · GV.SC Cybersecurity Supply Chain Risk Management
- **CIS Controls v8:** Control 15: Service Provider Management

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
