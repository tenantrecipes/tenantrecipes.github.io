# Access Management Policy (Joiner, Mover, Leaver)

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | Controls how access to {{COMPANY}} systems is granted, changed and removed when people join, move roles or leave. |
| Audience | HR, managers, IT and identity administrators, application owners and anyone who approves access. |
| Review | Every 12 months, and when HR or identity systems change. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Purpose

People should have the access they need for their job, no more, and lose it when they no longer need it. Leftover access is a common way in for attackers.

## 2. Scope

It covers all user, guest, administrator, service and agent identities in company systems and cloud services.

## 3. Principles

- Least privilege: grant the minimum access needed, preferably through role-based groups rather than individual permissions.
- Separation of duties: one person should not be able to both request and approve their own access, or complete high-risk financial actions alone.
- Every account belongs to one named person or, for service accounts, a named owner.
- Every agent identity belongs to a named owner and has enough sponsors to remain accountable; unused agent identities are reviewed and disabled.

## 4. Joiners

- Accounts are created only after HR or the hiring manager confirms the start in the HR system.
- Standard access comes from the role; extra access needs an approved request.
- New users enrol MFA on day one and complete security awareness training within their first month.

## 5. Movers

- When someone changes role, the new manager confirms the access they need, and access from the old role is removed within 30 days at the latest.
- Temporary access for projects has an end date.

## 6. Leavers

- Accounts are disabled no later than {{LEAVER_HOURS}} hours after the last working day, and immediately for unfriendly departures.
- Sessions and tokens are revoked, devices returned or wiped, and mailbox and files handed over to the manager according to retention rules.
- Shared passwords the leaver knew are changed.

## 7. Guests, agent identities and privileged access

- Guest accounts have a named sponsor and expire or are reviewed at least every {{ACCESS_REVIEW_MONTHS}} months. Sponsors periodically confirm that the guest still needs access; unused guests and unredeemed invitations are disabled or deleted on a documented schedule.
- Agent identities, including AI agents registered in the company directory, have a named owner and sponsors. Identities that issue no sign-in tokens for a defined period, lack sponsors or are not reconfirmed are disabled or deleted under this process.
- Privileged roles are granted just-in-time where possible, and are reviewed at least quarterly.

## 8. Access reviews

Managers and application owners review who has access to their systems at least every {{ACCESS_REVIEW_MONTHS}} months and remove what is not needed. Results are recorded.

## 9. Exceptions

Exceptions must be requested in writing, explain the business reason and the risk, include compensating measures, and have an end date. {{OWNER}} approves or rejects them and keeps a record.

## 10. Compliance

Breaches of this policy may lead to access being removed and to action under employment or contract terms. Report suspected breaches to {{SECURITY_CONTACT}}.

## 11. Ownership and review

Policy owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Framework references

Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.

- **ISO/IEC 27001:2022 Annex A theme:** Organizational controls (clause 5)
- **ISO/IEC 27001:2022 Annex A theme:** People controls (clause 6)
- **ISO/IEC 27001:2022 Annex A theme:** Technological controls (clause 8)
- **NIST CSF 2.0:** Protect · PR.AA Identity Management, Authentication, and Access Control
- **NIST CSF 2.0:** Govern · GV.RR Roles, Responsibilities, and Authorities
- **CIS Controls v8:** Control 5: Account Management
- **CIS Controls v8:** Control 6: Access Control Management

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example
- `{{LEAVER_HOURS}}`: Hours after the last day by which leaver accounts are disabled
- `{{ACCESS_REVIEW_MONTHS}}`: Months between access reviews

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
