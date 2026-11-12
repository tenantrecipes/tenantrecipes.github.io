# Password and Multi-Factor Authentication Policy

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | Defines how {{COMPANY}} protects sign-ins with strong passwords or passphrases, multi-factor authentication (MFA) and phishing-resistant methods. |
| Audience | All users with a {{COMPANY}} account, IT administrators and anyone who manages identity systems such as Microsoft Entra ID. |
| Review | Every 12 months, or when identity guidance or the threat landscape changes. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Purpose

Stolen and guessed passwords are among the most common ways attackers get in. This policy makes sign-ins harder to abuse without making daily work harder than necessary.

## 2. Scope

It applies to every account that can access {{COMPANY}} systems, including user, administrator, service and break-glass accounts, and to every system that signs people in.

## 3. Passwords and passphrases

- Use at least {{MIN_PASSWORD_LENGTH}} characters. A passphrase of several unrelated words is easier to remember and harder to crack.
- Never reuse a {{COMPANY}} password anywhere else, and never write it where others can see it.
- Passwords do not expire on a timer. They must be changed at once if there is any sign they have been exposed.
- Use the company-approved password manager for passwords that cannot be replaced by single sign-on.
- The identity system blocks commonly used and known-breached passwords.

## 4. Multi-factor authentication

- MFA is required for every user account, for all cloud services and for all remote access.
- Preferred methods, in order: phishing-resistant methods (passkeys, FIDO2 security keys, Windows Hello for Business), then an authenticator app with number matching. SMS and voice calls are only allowed as a temporary fallback approved by IT.
- New users register a phishing-resistant or passwordless method as their first MFA method where the identity platform supports it, rather than starting with SMS, voice or an app code.
- Where SMS or voice is still needed after the identity provider stops delivering it itself, it is only used through a contracted telephony provider approved by IT, for named users with a documented reason.
- Never approve a sign-in request you did not start; report it to {{SECURITY_CONTACT}} instead.
- IT never asks for your password or MFA code by email, phone or chat.

## 5. Administrator and special accounts

- Administrators use a separate admin account for privileged work, protected by phishing-resistant MFA.
- Privileged roles are granted just-in-time and time-limited where the platform supports it.
- At least two emergency (break-glass) accounts exist, are excluded only from the policies needed to stay usable, use strong credentials stored securely, and are monitored for any sign-in.
- Service accounts and app credentials have a named owner, the least privilege needed and a documented rotation plan.

## 6. Legacy network authentication

- Kerberos or modern authentication is the default for internal services. NTLM is allowed only where a system cannot use them, and every remaining NTLM dependency is recorded with an owner.
- NTLM connections to {{COMPANY}} servers must use message signing. Servers are configured to reject unsigned NTLM once auditing shows that no legitimate client still depends on it, and no later than the date the platform vendor enforces it by default.
- Settings that allow clients to skip NTLM signing, or that relax SMB/LDAP signing or LDAPS channel binding, are exceptions under this policy: written, time-limited and owned.
- Systems that cannot meet these rules are isolated or scheduled for replacement; their limitation is not a reason to weaken the rule for everyone else.

## 7. Lost devices and resets

Report a lost phone or security key the same day. Identity checks for password and MFA resets are done through a verified channel, never only on the caller's word.

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
- **NIST CSF 2.0:** Protect · PR.AA Identity Management, Authentication, and Access Control
- **CIS Controls v8:** Control 5: Account Management
- **CIS Controls v8:** Control 6: Access Control Management

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example
- `{{MIN_PASSWORD_LENGTH}}`: Minimum password length, e.g. 14

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
