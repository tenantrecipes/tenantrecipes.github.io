# Backup and Recovery Policy

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | Makes sure {{COMPANY}} can restore data and systems after deletion, failure or a ransomware attack within agreed times. |
| Audience | IT operations, system and data owners, cloud administrators and service providers who run backups for {{COMPANY}}. |
| Review | Every 12 months, and after any failed restore test or significant change to critical systems. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Purpose

Backups only matter if they can be restored when needed, including after an attacker has tried to destroy them.

## 2. Scope

It covers servers, databases, business applications, endpoints holding unique data, and cloud services such as Microsoft 365, where built-in retention is not the same as a backup.

## 3. Requirements

- Each critical system has a documented recovery point objective (default {{RPO_HOURS}} hours of data loss at most) and recovery time objective (default {{RTO_HOURS}} hours to restore).
- Backups follow the 3-2-1 idea: at least three copies, on two different types of storage, with one copy offsite or in a separate cloud account.
- At least one copy is immutable or offline, so ransomware and stolen admin accounts cannot change or delete it.
- Backups are encrypted in transit and at rest, and the keys are stored separately from the backups.
- Backups are kept for at least {{RETENTION_DAYS}} days, longer where law or contracts require.

## 4. Access and protection

- Backup systems use separate admin accounts with phishing-resistant MFA, not everyday domain accounts.
- Deleting backups or shortening retention needs approval by a second person.
- Backup failures raise alerts that are followed up the same working day.

## 5. Testing

- Restore tests are run at least quarterly for a sample of systems and at least yearly for each critical system.
- At least once a year, a full recovery scenario (for example a ransomware case) is exercised, including rebuilding identity services.
- Test results, the time it took and any gaps are recorded and fixed.

## 6. Roles

- System owners define what must be backed up and the RPO and RTO.
- IT operations runs, monitors and tests backups.
- {{OWNER}} reviews test results and reports risks to management.

## 7. Exceptions

Exceptions must be requested in writing, explain the business reason and the risk, include compensating measures, and have an end date. {{OWNER}} approves or rejects them and keeps a record.

## 8. Compliance

Breaches of this policy may lead to access being removed and to action under employment or contract terms. Report suspected breaches to {{SECURITY_CONTACT}}.

## 9. Ownership and review

Policy owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Framework references

Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.

- **ISO/IEC 27001:2022 Annex A theme:** Technological controls (clause 8)
- **NIST CSF 2.0:** Protect · PR.DS Data Security
- **NIST CSF 2.0:** Protect · PR.IR Technology Infrastructure Resilience
- **NIST CSF 2.0:** Recover · RC.RP Incident Recovery Plan Execution
- **CIS Controls v8:** Control 11: Data Recovery

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example
- `{{RPO_HOURS}}`: Default recovery point objective in hours
- `{{RTO_HOURS}}`: Default recovery time objective in hours
- `{{RETENTION_DAYS}}`: Minimum backup retention in days

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
