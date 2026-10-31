# Incident Response Policy

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | Describes how {{COMPANY}} detects, reports, handles and learns from information security incidents. |
| Audience | All staff (who must report incidents), the incident response team, IT operations, management, legal, communications and HR. |
| Review | Every 12 months, and after every major incident or exercise. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Purpose

A fast, coordinated response limits damage and cost. This policy makes sure everyone knows what to report, who leads and what happens next.

## 2. Scope

It covers any event that threatens the confidentiality, integrity or availability of {{COMPANY}} information or systems, including those at suppliers that affect us.

## 3. What to report

- Suspected phishing that someone clicked or replied to, unusual sign-in prompts, malware warnings, lost or stolen devices, data sent to the wrong person and unexpected system behaviour.
- Report straight away to {{IT_SERVICE_DESK}} or {{SECURITY_CONTACT}}. Do not investigate on your own, delete evidence or contact the attacker.

## 4. Roles

- {{IR_LEAD}} leads the response, decides severity and calls in the incident response team.
- IT and security staff contain, investigate and recover systems.
- Management decides on business impact, external help and spending.
- Legal and the data protection officer assess notification duties to authorities, customers and individuals within the legal deadlines.
- Communications handles all external statements; nobody else speaks to media about an incident.

## 5. Response phases

- Prepare: keep contact lists, playbooks, logging and out-of-band communication ready, and test them.
- Detect and analyse: confirm the incident, set a severity level and record a timeline from the first report.
- Contain: limit spread, for example by isolating devices, revoking sessions and resetting credentials.
- Eradicate and recover: remove the cause, restore from clean backups, monitor closely and return to normal operation.
- Learn: within two weeks of closing a significant incident, hold a blameless review and track every improvement to completion.

## 6. Severity levels

- Low: limited impact, handled by IT in normal working hours.
- Medium: affects several users or internal data; incident team engaged the same day.
- High: business-critical systems, confidential data or many users affected; management informed immediately.
- Critical: major outage, ransomware or likely notifiable data breach; full team and executive leadership engaged around the clock.

## 7. Evidence and records

Preserve logs and affected systems before rebuilding where possible. Keep an incident record with timeline, decisions, impact and notifications for at least the period required by law and contracts.

## 8. Exceptions

Exceptions must be requested in writing, explain the business reason and the risk, include compensating measures, and have an end date. {{OWNER}} approves or rejects them and keeps a record.

## 9. Compliance

Breaches of this policy may lead to access being removed and to action under employment or contract terms. Report suspected breaches to {{SECURITY_CONTACT}}.

## 10. Ownership and review

Policy owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Framework references

Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.

- **ISO/IEC 27001:2022 Annex A theme:** Organizational controls (clause 5)
- **ISO/IEC 27001:2022 Annex A theme:** Technological controls (clause 8)
- **NIST CSF 2.0:** Detect · DE.AE Adverse Event Analysis
- **NIST CSF 2.0:** Respond · RS.MA Incident Management
- **NIST CSF 2.0:** Respond · RS.AN Incident Analysis
- **NIST CSF 2.0:** Respond · RS.CO Incident Response Reporting and Communication
- **NIST CSF 2.0:** Respond · RS.MI Incident Mitigation
- **NIST CSF 2.0:** Recover · RC.RP Incident Recovery Plan Execution
- **NIST CSF 2.0:** Recover · RC.CO Incident Recovery Communication
- **CIS Controls v8:** Control 17: Incident Response Management

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example
- `{{IR_LEAD}}`: Role that leads incident response
- `{{IT_SERVICE_DESK}}`: How to reach the IT service desk

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
