# AI, Microsoft Copilot and enterprise LLM use policy

> **Template, not legal advice. Adapt it with your legal and HR teams before you adopt it.**

| | |
|---|---|
| Purpose | Sets the rules for using generative AI tools — Microsoft Copilot and approved third-party enterprise LLMs — so people can benefit without leaking information or relying on wrong answers. |
| Audience | All employees and contractors who use generative AI for work, plus IT, security, legal and data owners who approve AI tools. |
| Review | Every 6 months, because AI tools, features and regulations change quickly. |
| Owner | {{OWNER}} |
| Approved by | {{APPROVER}} |
| Effective | {{EFFECTIVE_DATE}} |
| Next review | {{REVIEW_DATE}} |

## 1. Purpose

Generative AI can save time, but it can also expose confidential data, produce convincing errors and create legal risk. This policy describes safe and responsible use.

## 2. Scope

It covers chat assistants, AI features in business apps, coding assistants and any service that generates text, images, code or audio, whether provided by {{COMPANY}} or found online.

## 3. Approved tools

- Only the AI tools listed in {{APPROVED_AI_TOOLS}} may be used with company information. Consumer ChatGPT, consumer Microsoft Copilot (personal Microsoft account) and personal Grok accounts are not approved for company data.
- Microsoft 365 Copilot works with the files, mail and chats you already have access to. Before it is enabled, data owners review and fix oversharing (broad sharing links, 'Everyone' permissions and public Teams or sites).
- Third-party enterprise LLMs (for example ChatGPT Enterprise, Claude Enterprise or an approved Grok enterprise offering) require SSO through the company identity provider, a recorded retention and training stance, and security approval before seats are assigned.
- New AI tools, plug-ins, agents, API keys and IDE assistants are approved by IT and security before use. Personal API keys against company data are treated as shadow AI.
- Local AI agents (coding command-line agents, desktop agents, agentic IDEs and editor extensions) and the MCP servers or connectors they use are AI tools under this policy. They act with your account's access to files, credentials and systems, so only agents and MCP servers listed in {{APPROVED_AI_TOOLS}} may be installed or configured on company devices, and IT may inventory them through endpoint security tools.
- Microsoft-managed AI subprocessors (for example Anthropic models in Microsoft Copilot) are approved only for the users and groups that IT has assigned in the admin center. IT reviews these settings before any announced default change takes effect and records the decision in the AI inventory.

## 4. What you may not put into AI tools

- Information classified as Confidential or Restricted, unless the specific approved tool is listed for that level in {{APPROVED_AI_TOOLS}}.
- Personal data about customers or colleagues, passwords, keys, source code secrets or security details, in any tool that is not approved for that class.
- Anything you are not allowed to share with the provider of the tool under the company DPA and data-residency rules.
- Company information pasted into a consumer or personal AI account, even if you believe the text is anonymised.

## 5. Using AI output

- You are responsible for anything you produce with AI. Check facts, figures, quotes and references before you use them.
- Interactive outputs that an AI tool builds for you, such as calculators, dashboards, forms or simulations, are AI output too. Check their inputs and logic before you rely on them or share them.
- Do not use AI output alone for decisions about people, such as hiring, performance or credit.
- Be open about AI use when a customer, colleague or reader would reasonably expect to know.
- Respect copyright and licences; do not ask tools to reproduce protected material.

## 6. Security and monitoring

- Sensitivity labels and data loss prevention apply to AI features in the same way as to other apps, including Endpoint DLP controls for unsanctioned generative AI sites where deployed.
- Self-hosted AI infrastructure, such as AI gateways, model-serving clusters and MCP servers, must be in the approved AI inventory with a named owner, must not be reachable from the internet without authentication, and is patched under the patch management policy.
- AI interactions in company tools may be logged and retained for security, compliance and legal holds.
- Report suspicious AI behaviour, prompt injection, unsanctioned tools or a possible data leak to {{SECURITY_CONTACT}}.

## 7. Training

Everyone who gets access to AI tools completes short training on safe prompting, data handling and checking output.

## 8. Exceptions

Exceptions must be requested in writing, explain the business reason and the risk, include compensating measures, and have an end date. {{OWNER}} approves or rejects them and keeps a record.

## 9. Compliance

Breaches of this policy may lead to access being removed and to action under employment or contract terms. Report suspected breaches to {{SECURITY_CONTACT}}.

## 10. Ownership and review

Policy owner: {{OWNER}}. Approved by: {{APPROVER}}. Effective from: {{EFFECTIVE_DATE}}. Next review: {{REVIEW_DATE}}.

## Framework references

Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.

- **ISO/IEC 27001:2022 Annex A theme:** Organizational controls (clause 5)
- **ISO/IEC 27001:2022 Annex A theme:** People controls (clause 6)
- **ISO/IEC 27001:2022 Annex A theme:** Technological controls (clause 8)
- **NIST CSF 2.0:** Govern · GV.PO Policy
- **NIST CSF 2.0:** Protect · PR.DS Data Security
- **NIST CSF 2.0:** Protect · PR.AT Awareness and Training
- **CIS Controls v8:** Control 3: Data Protection
- **CIS Controls v8:** Control 14: Security Awareness and Skills Training

## Placeholders to replace

- `{{COMPANY}}`: Your organization's legal or trading name
- `{{OWNER}}`: Role that owns this policy, e.g. Head of IT or CISO
- `{{APPROVER}}`: Who approved it, e.g. Management team
- `{{EFFECTIVE_DATE}}`: Date the policy takes effect
- `{{REVIEW_DATE}}`: Next planned review date
- `{{SECURITY_CONTACT}}`: Where to report security issues, e.g. security@yourcompany.example
- `{{APPROVED_AI_TOOLS}}`: Where the list of approved AI tools is published

---

Template from Tenant Recipes (https://tenantrecipes.com/policies/). Free to adapt for use in your organization.
Independent and not affiliated with Microsoft, ISO, NIST or CIS.
