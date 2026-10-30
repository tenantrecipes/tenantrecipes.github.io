# Role Change (Mover) Checklist (IT)

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | An IT checklist for people at {{COMPANY}} who change role, team or location, so they get the new access they need and lose the old access they no longer need. |
| Audience | Managers (old and new), HR, IT service desk and application owners. |
| Review | Every 12 months. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Before the move

- [ ] HR records the new title, department, manager and start date of the new role.
- [ ] The new manager requests access using the new role template; the old manager lists access that must end.
- [ ] Agree a short overlap period for handover, with an end date (for example two weeks).

## 2. On the move date

- [ ] Update job title, department, manager and location in the HR system and Microsoft Entra ID.
- [ ] Add the new role-based groups; licences change automatically if they are group-based.
- [ ] Grant any extra approved access for the new role, with an end date if temporary.
- [ ] Check device and app requirements for the new role (for example a different device policy or a privileged access workstation).

Microsoft Learn: [Assign licenses to a group](https://learn.microsoft.com/en-us/entra/identity/users/licensing-groups-assign); [What are lifecycle workflows?](https://learn.microsoft.com/en-us/entra/id-governance/what-are-lifecycle-workflows)

## 3. End of the overlap period

- [ ] Remove the old role's groups, Teams, SharePoint sites, shared mailboxes and application roles.
- [ ] Remove admin roles and PIM eligibilities that the new role does not need.
- [ ] Transfer ownership of files, Teams, apps and automations that belong to the old team.

Microsoft Learn: [What is Privileged Identity Management?](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure)

## 4. Verify

- [ ] The new manager confirms the access list matches the new role.
- [ ] Include the person in the next access review for both the old and the new areas.
- [ ] Close the ticket with what was added and removed.

Microsoft Learn: [What are access reviews?](https://learn.microsoft.com/en-us/entra/id-governance/access-reviews-overview)

## 5. Sign-off

- [ ] The new manager confirms every item above is done or marked not applicable with a reason.
- [ ] IT confirms the account, device and access changes, with date and initials.
- [ ] The completed checklist is stored with the ticket or HR record for at least {{RETENTION_DAYS}} days.

## 6. Ownership and review

Checklist owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Related

- Access management policy template: https://tenantrecipes.github.io/policies/access-management-policy.html

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
- `{{RETENTION_DAYS}}`: Minimum backup retention in days
- `{{IT_SERVICE_DESK}}`: How to reach the IT service desk

---

Template from Tenant Recipes (https://tenantrecipes.github.io/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
