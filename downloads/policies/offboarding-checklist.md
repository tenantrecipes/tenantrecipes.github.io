# Employee Offboarding Checklist (IT)

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | A step-by-step IT checklist to remove a leaver's access at {{COMPANY}} completely and on time, while keeping the business data they leave behind. |
| Audience | IT service desk, identity and device administrators, HR, managers and the security team. |
| Review | Every 12 months, and after any offboarding that went wrong. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Choose the path

HR or the manager opens the leaver ticket as early as possible, with the last working day and who receives the person's mail and files.

- [ ] Planned departure: complete the steps below on the last working day, and no later than {{LEAVER_HOURS}} hours after it.
- [ ] Immediate or hostile termination: HR tells IT before the conversation with the employee; IT blocks sign-in and revokes sessions while the conversation happens. Do the 'Block access now' section first, then the rest.

## 2. Block access now

- [ ] Block sign-in for the user in Microsoft Entra ID (and disable the account in on-premises Active Directory if synced).
- [ ] Reset the password so cached credentials stop working.
- [ ] Revoke all sign-in sessions and refresh tokens (in the admin center or with Revoke-MgUserSignInSession).
- [ ] Remove or disable the user's registered MFA methods, passkeys and Temporary Access Passes.
- [ ] Disable or remove VPN, remote access and any accounts outside Entra single sign-on.

Microsoft Learn: [Revoke user access in an emergency in Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/users/users-revoke-access); [Revoke-MgUserSignInSession](https://learn.microsoft.com/en-us/powershell/module/microsoft.graph.users.actions/revoke-mgusersigninsession); [Manage authentication methods for Microsoft Entra MFA](https://learn.microsoft.com/en-us/entra/identity/authentication/howto-mfa-userdevicesettings)

## 3. Mail and files

- [ ] With the manager's or HR's written approval, convert the mailbox to a shared mailbox and give access to the agreed person; or set up forwarding or an auto-reply for a limited period.
- [ ] Before removing the licence, check the shared mailbox is under the size limit for unlicensed shared mailboxes or keep a licence.
- [ ] Transfer or give access to OneDrive content; the manager gets access by default when the user is deleted, but files are removed after the retention period.
- [ ] Make sure legal holds or retention policies are in place before deleting anything.

Microsoft Learn: [Convert a user mailbox to a shared mailbox](https://learn.microsoft.com/en-us/microsoft-365/admin/email/convert-user-mailbox-to-shared-mailbox); [OneDrive retention and deletion](https://learn.microsoft.com/en-us/sharepoint/retention-and-deletion); [Remove a former employee (Microsoft 365 admin)](https://learn.microsoft.com/en-us/microsoft-365/admin/add-users/remove-former-employee)

## 4. Groups, apps and roles

- [ ] Remove the user from all security groups, Microsoft 365 groups, Teams and distribution lists.
- [ ] Remove admin roles and PIM eligibilities.
- [ ] Remove access to business applications that do not use single sign-on (finance, CRM, line-of-business apps).
- [ ] Revoke third-party SaaS accounts, API keys and personal access tokens the user created; transfer ownership of app registrations, automations and shared resources.
- [ ] Change shared passwords, service account secrets and door or alarm codes the user knew.
- [ ] Transfer ownership of agent identities the leaver owns or sponsors, or disable agents that existed only for that person's work; do not leave agent identities without an accountable owner or sponsor.
- [ ] Reassign guest sponsorships the leaver holds so external guests are not left unsponsored.

Microsoft Learn: [What is Privileged Identity Management?](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)

## 5. Devices and hardware

- [ ] Collect laptop, phone, security keys, badges and other hardware; check against the asset register.
- [ ] Company devices: wipe and re-provision, or retire from Intune; personal devices: remove company data with a selective wipe/retire.
- [ ] Remove the device objects from Entra ID and Intune when they are no longer used.

Microsoft Learn: [Wipe devices with Microsoft Intune](https://learn.microsoft.com/en-us/intune/intune-service/remote-actions/devices-wipe)

## 6. Check and close

- [ ] Review the sign-in and audit logs for the last days of employment for unusual downloads, forwarding rules or sharing.
- [ ] Confirm no mail forwarding rules or external sharing links created by the user remain active unless approved.
- [ ] Delete or keep the account according to the retention rules; record the decision.
- [ ] Confirm no orphaned agent identities or unsponsored guests remain against the leaver's account.

Microsoft Learn: [Search the audit log](https://learn.microsoft.com/en-us/purview/audit-search)

## 7. Sign-off

- [ ] The manager and HR confirms every item above is done or marked not applicable with a reason.
- [ ] IT confirms the account, device and access changes, with date and initials.
- [ ] The completed checklist is stored with the ticket or HR record for at least {{RETENTION_DAYS}} days.

## 8. Ownership and review

Checklist owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Related

- Access management policy template: https://tenantrecipes.com/policies/access-management-policy.html

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
- `{{RETENTION_DAYS}}`: Minimum backup retention in days
- `{{IT_SERVICE_DESK}}`: How to reach the IT service desk

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
