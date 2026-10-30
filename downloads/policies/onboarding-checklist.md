# Employee Onboarding Checklist (IT)

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | A step-by-step IT checklist so new starters at {{COMPANY}} get the right account, licences, device and access on day one, securely and without guesswork. |
| Audience | IT service desk, identity and device administrators, HR and hiring managers. |
| Review | Every 12 months, or when HR, identity or device processes change. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Before day 1: request and approval

- [ ] HR has confirmed the start date, job title, department, manager and contract end date (if any) in the HR system.
- [ ] The manager has requested role-based access using the standard role template; any extra access has a documented approval.
- [ ] Privileged or sensitive access (admin roles, finance, HR data) has a second approval and an end date.

## 2. Before day 1: account and licences

- [ ] Create the user in Microsoft Entra ID (or let HR-driven provisioning create it) with correct name, department, manager and usage location.
- [ ] Add the user to the role-based groups; licences are assigned through group-based licensing rather than by hand.
- [ ] Set an account expiry or review date for contractors and temporary staff.
- [ ] Mailbox, OneDrive and Teams are created by the licence; add shared mailboxes, Teams and SharePoint sites the role needs.

Microsoft Learn: [Create, invite and delete users in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/fundamentals/how-to-create-delete-users); [Assign licenses to a group](https://learn.microsoft.com/en-us/entra/identity/users/licensing-groups-assign); [What are lifecycle workflows?](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)

## 3. Before day 1: sign-in and device

- [ ] Prepare a Temporary Access Pass (TAP) so the new starter can register MFA or passkeys on day one without a known password; share it through a verified channel.
- [ ] Register the laptop for Windows Autopilot (or prepare the device in your MDM) and assign it to the user.
- [ ] Prepare the phone or confirm the BYOD route and app protection policies.

Microsoft Learn: [Configure a Temporary Access Pass](https://learn.microsoft.com/en-us/entra/identity/authentication/howto-authentication-temporary-access-pass); [Overview of Windows Autopilot](https://learn.microsoft.com/en-us/autopilot/overview)

## 4. Day 1

- [ ] Verify identity in person or by video before handing over the TAP or device.
- [ ] User signs in, registers phishing-resistant MFA or an authenticator app, and the TAP expires or is removed.
- [ ] Device completes Autopilot enrolment and shows as compliant.
- [ ] User confirms access to mail, Teams, OneDrive and the role's core applications.
- [ ] Give the acceptable use, password and MFA, and AI use policies; record acceptance.
- [ ] Explain how to report phishing and incidents to {{IT_SERVICE_DESK}} and {{SECURITY_CONTACT}}.

Microsoft Learn: [Manage authentication methods for Microsoft Entra MFA](https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-userdevicesettings)

## 5. First week

- [ ] Security awareness training is assigned and has a due date.
- [ ] Manager checks that access matches the role, no more and no less; remove anything granted 'just in case'.
- [ ] Any temporary or project access has an end date.
- [ ] Open issues are closed or tracked in a ticket.

## 6. Sign-off

- [ ] The hiring manager confirms every item above is done or marked not applicable with a reason.
- [ ] IT confirms the account, device and access changes, with date and initials.
- [ ] The completed checklist is stored with the ticket or HR record for at least {{RETENTION_DAYS}} days.

## 7. Ownership and review

Checklist owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Related

- Access management policy template: https://tenantrecipes.github.io/policies/access-management-policy.html

## Framework references

Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.

- **ISO/IEC 27001:2022 Annex A theme:** Organizational controls (clause 5)
- **ISO/IEC 27001:2022 Annex A theme:** People controls (clause 6)
- **ISO/IEC 27001:2022 Annex A theme:** Technological controls (clause 8)
- **NIST CSF 2.0:** Protect · PR.AA Identity Management, Authentication, and Access Control
- **NIST CSF 2.0:** Protect · PR.AT Awareness and Training
- **CIS Controls v8:** Control 5: Account Management
- **CIS Controls v8:** Control 6: Access Control Management
- **CIS Controls v8:** Control 14: Security Awareness and Skills Training

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example
- `{{IT_SERVICE_DESK}}`: How to reach the IT service desk
- `{{RETENTION_DAYS}}`: Minimum backup retention in days

---

Template from Tenant Recipes (https://tenantrecipes.github.io/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
