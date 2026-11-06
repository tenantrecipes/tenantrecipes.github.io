"""Technical guide: approve and deploy one enterprise AI service, any vendor.
Normative sources checked 2026-11-06 (HTTP 200 + relevant section text); not lab-tested or production-implemented."""

SLUG = "enterprise-ai-service-approval"
TIER = "technical"
PUBLISHED = "2026-11-06"
VERIFIED = "2026-11-06"
UPDATED = "2026-11-06"
TITLE = "Approve and deploy an enterprise AI service, any vendor: intake to reapproval"
SHORT = "Approve an enterprise AI service"
DESC = ("A vendor-neutral runbook for taking one AI service from request to production: intake, use-case and data "
        "classification, contract and data-processing checks, a go / conditional go / no-go decision record, "
        "identity and connector scoping, a safe pilot, launch, incident revocation and reapproval.")
BADGE = "Primary NIST, OWASP and EU sources checked; no lab or production testing claimed"
SRC_LABEL = "Checked primary sources"
TIME_NOTE = ("Time estimates are Tenant Recipes planning figures for one service in a mid-size organisation. "
             "Exit criteria and templates are editorial suggestions, not legal or regulatory requirements. Not legal advice.")
CTA_FIRST = "Start with intake →"
INTRO = [
    "The enterprise AI governance pillar sets the programme: principles, inventory, shadow AI and the control plane. "
    "This guide is the repeatable procedure you run each time a team asks for one specific AI service — a chat assistant, "
    "a retrieval (RAG) app over internal content, or an agent that can take actions.",
    "It is vendor-neutral on purpose. Plans, retention terms, training defaults and regions differ by vendor and by plan, "
    "and change. Every vendor answer in this runbook must come from that vendor's current contract, DPA or admin "
    "documentation for the exact plan you buy — not from this page, a sales deck or a model's own answer.",
]
NAMING = ("Scope: business use of third-party or self-hosted generative AI services by employees. Consumer accounts are not "
          "an approval path. Sources checked on 6 November 2026; nothing here was executed in a tenant, lab or production. "
          "GDPR, AI Act and sector-law applicability is a legal determination for your organisation.")
NOTICE = {
    "title": "A runbook, not a compliance certificate",
    "text": ("Following these steps produces evidence for a decision. It does not make a service GDPR- or AI Act-compliant, "
             "and it does not replace your DPO, counsel or security review. Where a check depends on a vendor feature, "
             "confirm it for your plan in writing."),
}
HISTORY = [("2026-11-06", "Published vendor-neutral approval and deployment runbook; documentation verified only.")]

L = {
    "rmf": ("NIST: AI Risk Management Framework (AI RMF 1.0)", "https://www.nist.gov/itl/ai-risk-management-framework"),
    "genai": ("NIST AI 600-1: Generative AI Profile", "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf"),
    "owasp": ("OWASP: Top 10 for LLM Applications 2025", "https://genai.owasp.org/llm-top-10/"),
    "llm01": ("OWASP LLM01: Prompt injection", "https://genai.owasp.org/llmrisk/llm01-prompt-injection/"),
    "llm06": ("OWASP LLM06: Excessive agency", "https://genai.owasp.org/llmrisk/llm062025-excessive-agency/"),
    "ssdf": ("NIST SP 800-218A: SSDF community profile for generative AI", "https://csrc.nist.gov/pubs/sp/800/218/a/final"),
    "gdpr": ("Regulation (EU) 2016/679 (GDPR) — see Art. 5, 28, 32, 35 and Chapter V", "https://eur-lex.europa.eu/eli/reg/2016/679/oj"),
    "dpia": ("EDPB: Guidelines on Data Protection Impact Assessment", "https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/data-protection-impact-assessments-high-risk-processing_en"),
    "aiact": ("Regulation (EU) 2024/1689 (AI Act)", "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689"),
    "art4": ("AI Act Service Desk: Article 4 — AI literacy", "https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-4"),
    "art26": ("AI Act Service Desk: Article 26 — deployers of high-risk AI systems", "https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-26"),
    "art50": ("AI Act Service Desk: Article 50 — transparency obligations", "https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50"),
}
S = lambda *k: [L[x] for x in k]

def st(t, check, do, pit, src, rec=(), tools=(), guides=(), policies=()):
    return {"t": t, "check": check, "do": do, "pit": pit, "src": S(*src), "rec": list(rec), "tools": list(tools),
            "guides": list(guides), "policies": list(policies)}

PHASES = [
 {"id": "intake", "title": "Intake: business need, owner and request", "time": "1–3 days",
  "goal": "One written request per service with a named business owner and a concrete problem — before any trial account exists.",
  "steps": [
   st("Capture the request with the intake checklist",
      "Every intake field below is answered or explicitly marked unknown",
      ["Intake checklist (copy into your request form): service and vendor; exact plan/SKU; business owner (named person); technical owner; problem it solves and current workaround; users in scope and count; use pattern (chat / RAG over internal content / agent with actions); data classes users would enter or connect; systems to connect (mail, files, CRM, code, ticketing); output use (internal draft / customer-facing / automated decision); regions where users and data sit; expected start and budget; alternatives already approved in your inventory.",
       "Check the approved-tools inventory first. If an already approved service covers the need, route the request there instead of starting a new approval.",
       "Reject 'just let us try it with real data' at intake. Trials before approval use synthetic or public data only."],
      ["A request without a named business owner has nobody to accept residual risk later."],
      ("rmf",), tools=("enterprise-ai-approved-inventory",), guides=("enterprise-ai-governance",)),
  ]},
 {"id": "classify", "title": "Classify the use case and the data", "time": "1–2 days", "deep": True,
  "goal": "A risk tier driven by what the service can see and do, not by which vendor it is.",
  "steps": [
   st("Place the use case on the chat → RAG → agent ladder",
      "Use pattern, connected systems and permitted actions are documented and agreed by the technical owner",
      ["Chat: users type or paste content; risk is mostly what they paste and what the vendor retains.",
       "RAG / grounded: the service reads internal content through a connector or index. Risk adds permission scope (it can surface what the connector identity can read) and indirect prompt injection through retrieved documents.",
       "Agent / actions: the service can call tools, send messages, change records or run code. Risk adds excessive agency: every tool scope is a potential unintended action.",
       "Record the highest rung the service will reach, including features you plan to enable later. Re-run this guide when the rung goes up."],
      ["Treating a RAG app as 'just chat' skips the permission review that matters most."],
      ("owasp", "llm01", "llm06", "genai")),
   st("Classify data and decide the risk tier",
      "Allowed and prohibited data classes are listed, and the tier (low / medium / high) is recorded with a reason",
      ["Map each data class in the intake to your classification scheme. Mark prohibited classes explicitly (for example credentials and secrets, special-category personal data, regulated customer data) unless a specific control and approval allows them.",
       "Suggested editorial tiering: Low = public or internal non-personal data, chat only. Medium = personal data or confidential data, or any RAG connector. High = special-category or regulated data, customer-facing output, automated decisions about people, or agents with write actions. Adjust to your own risk framework.",
       "Flag possible legal triggers for Legal/DPO, without deciding them yourself: processing of personal data (GDPR), likely high-risk processing (DPIA, GDPR Art. 35), and AI Act categories such as uses listed as high-risk or transparency duties (Art. 50)."],
      ["Do not label a service 'AI Act compliant' or 'GDPR compliant' in the record — record the checks done and who decided."],
      ("gdpr", "dpia", "aiact", "art50", "rmf")),
  ]},
 {"id": "vendor", "title": "Vendor, contract and data-processing evaluation", "time": "1–3 weeks", "deep": True,
  "goal": "Written, plan-specific answers on how the vendor handles your data — with document names and dates.",
  "steps": [
   st("Collect plan-specific evidence, not marketing claims",
      "Each question has an answer with a source document, version or date, and the plan it applies to",
      ["Ask and file evidence for: Is customer content used to train or improve models on this plan, and how is that controlled? Default retention of prompts, outputs and files; admin-configurable retention; deletion behaviour and timelines, including backups and legal holds. Subprocessors and how changes are notified. Processing and storage regions, and the transfer mechanism for any transfer outside the EU/EEA (GDPR Chapter V). Security attestations offered and their scope. Audit-log availability and export. SSO, SCIM and admin role options. Abuse-monitoring access by vendor staff.",
       "Note plan-specific limitations explicitly: features such as SSO, retention controls, audit export or regional processing are often limited to specific enterprise tiers. Record 'not available on this plan' rather than assuming parity.",
       "Store the evidence with the decision record. Re-check it at reapproval: terms change."],
      ["An answer from the vendor's chatbot or a sales email is not contract evidence.",
       "Consumer and business plans of the same product frequently have different data terms."],
      ("gdpr", "genai")),
   st("Put the processing relationship in writing",
      "Signed contract and DPA (or equivalent) exist, or the decision is blocked",
      ["Where the vendor processes personal data on your behalf, GDPR Art. 28 requires a processor contract with defined content; Legal confirms whether the vendor's standard DPA is sufficient.",
       "Confirm security obligations (Art. 32 context), breach-notification commitments, deletion or return at end of contract, and audit or information rights.",
       "If the vendor will not offer a DPA for the plan you can afford, that is a valid no-go or a 'non-personal data only' conditional go."],
      ["Click-through consumer terms rarely give you processor commitments."],
      ("gdpr",)),
  ]},
 {"id": "assess", "title": "Proportionate privacy, security and legal checks", "time": "1–4 weeks",
  "goal": "Checks scaled to the tier: light for low, full assessments for high.",
  "steps": [
   st("Run the checks the tier requires",
      "Each required check is complete or recorded as a blocker",
      ["Low: security questionnaire review, SSO check, user guidance. Medium: add a privacy review by the DPO function, a connector permission review and a threat review against the OWASP LLM Top 10. High: add a DPIA where GDPR Art. 35 applies (your DPO decides, using EDPB guidance), a legal review of AI Act role and obligations, and a design review of every agent action.",
       "Threat review prompts: prompt injection (direct and via retrieved content), sensitive information disclosure, excessive agency, insecure output handling into other systems, and supply-chain risk in plug-ins or models.",
       "If the organisation acts as a deployer of a high-risk AI system, Art. 26 deployer obligations apply — counsel confirms classification. Separately, Art. 4 expects measures for staff AI literacy; plan training regardless of tier."],
      ["Running a full DPIA for every low-risk chat tool burns goodwill; skipping it for a high-risk use is worse."],
      ("dpia", "gdpr", "owasp", "art26", "art4", "ssdf")),
  ]},
 {"id": "decide", "title": "Decision: go, conditional go or no-go", "time": "1–2 days",
  "goal": "One accountable decision with evidence, conditions, blockers and an expiry date.",
  "steps": [
   st("Complete the approval decision record",
      "Record is signed by the named approver roles and stored with the evidence",
      ["Decision record template: Service, vendor, plan, version of terms reviewed (date). Use case and highest rung (chat / RAG / agent). Risk tier and reason. Allowed data classes; prohibited data classes. Connectors and tool scopes approved. Evidence list (contract, DPA, security docs, DPIA if any). Open risks and owner of each. Decision: GO / CONDITIONAL GO / NO-GO. Conditions (each with owner and due date). Blockers (for no-go). Pilot scope and exit criteria. Review / expiry date. Roles and sign-off: business owner (accepts business risk), technical owner (operates it), security approver, DPO or privacy function (consulted or approver for personal data), Legal where triggered, AI risk owner (final approval for medium and high).",
       "Conditional go is the normal outcome for medium risk: for example 'approved for internal non-personal data only until the DPA is signed'. Conditions must be checkable.",
       "Update the approved-tools inventory status (Approved / Conditional / Denied) the same day."],
      ["A decision with no expiry date never gets reviewed."],
      ("rmf",), tools=("enterprise-ai-approved-inventory",), policies=("ai-copilot-use-policy",)),
  ]},
 {"id": "access", "title": "Identity, access and connector scoping", "time": "2–5 days", "deep": True,
  "goal": "Least privilege everywhere the service touches: users, admins, connectors and tools.",
  "steps": [
   st("Lock down identity and lifecycle",
      "SSO and MFA are enforced, access is group-based, and leavers lose access through the normal deprovisioning path",
      ["Integrate with your identity provider via SSO where the plan supports it, enforce MFA or phishing-resistant methods through the IdP, and block local password sign-in if the service allows.",
       "Assign access through a dedicated group; use SCIM or equivalent provisioning if available so deprovisioning is automatic. Test that removing a user from the group removes access.",
       "Separate admin roles from user access, keep at least two named admins, and review admin assignments at reapproval."],
      ["Personal-email sign-ups for a 'quick pilot' bypass deprovisioning entirely."],
      ("genai", "rmf"), rec=("ca-require-mfa-copilot",)),
   st("Scope connectors, keys and agent tools",
      "Every connector and tool has a documented scope, a service identity and an owner",
      ["Connectors (RAG): use a dedicated service identity with read access to the minimum set of sites, mailboxes or repositories. Prefer per-user delegated access where the design allows, so users only retrieve what they can already open. Fix oversharing in the source before connecting it.",
       "Agent tools: allow-list specific actions; require human confirmation for writes, sends and payments; avoid broad scopes such as full mailbox send or tenant-wide write. This directly addresses excessive agency.",
       "API keys: store in a secrets manager, rotate on a schedule, one key per integration, never in prompts or shared documents."],
      ["A RAG connector running as a highly privileged account surfaces everything that account can read."],
      ("llm06", "llm01", "owasp"), rec=("purview-oversharing-assessment",), guides=("secure-copilot-rollout",)),
  ]},
 {"id": "pilot", "title": "Safe pilot with exit criteria", "time": "2–6 weeks", "deep": True,
  "goal": "Evidence that the service is useful and controlled, gathered without exposing data you have not approved.",
  "steps": [
   st("Run the pilot on approved data and test the controls",
      "Pilot group, data scope and test plan are documented, and tests are executed and recorded",
      ["Start with synthetic, public or non-sensitive data; widen to approved data classes only when the controls tests pass.",
       "Quality: define 5–20 representative tasks with expected outputs and have domain users score accuracy and usefulness. Record failure modes, not just averages.",
       "Security tests (in a controlled environment, with authorization): direct prompt-injection attempts; indirect injection through a planted document in the RAG scope; attempts to retrieve content the test user should not see; attempts to make an agent act outside its allow-list. Verify human review gates actually block.",
       "Leakage checks: confirm prohibited data classes are blocked or detected where your DLP covers the service, and that logs capture what you need for investigations."],
      ["A pilot on the CEO's mailbox is not a pilot."],
      ("llm01", "llm06", "owasp", "genai")),
   st("Apply pilot exit criteria",
      "Each criterion is met, waived by the approver with a reason, or the pilot ends",
      ["Suggested editorial exit criteria — adapt them: all decision-record conditions closed; no unresolved high-severity finding from security tests; deprovisioning verified; audit logs available and retained as decided; quality scores meet the threshold the business owner set before the pilot; users completed guidance and know the prohibited data classes; support and incident contacts documented; cost per user or per call known.",
       "Record the outcome in the decision record and move inventory status from Conditional to Approved only when criteria are met."],
      ["Moving goalposts after the pilot ('it was mostly fine') makes the criteria meaningless."],
      ("rmf",)),
  ]},
 {"id": "launch", "title": "Controlled launch: policy, training, monitoring, cost", "time": "1–2 weeks",
  "goal": "Wider access with guidance, monitoring and a budget owner.",
  "steps": [
   st("Launch in rings with guidance and monitoring",
      "Policy published, training delivered, monitoring and cost alerts in place before each ring",
      ["Publish the use rules with the approved and prohibited data classes for this service; link your AI use policy.",
       "Deliver short role-based training (what to enter, what never to enter, how to verify outputs, how to report problems). This also supports the AI literacy expectation in AI Act Art. 4.",
       "Monitoring: sign-in and admin-change alerts, connector-scope changes, DLP events, unusual volume. Cost: per-seat or usage budget alerts with a named budget owner.",
       "Where outputs reach customers or the public, check transparency duties with Legal (AI Act Art. 50) and label AI-generated content as your policy requires."],
      ["Launching to everyone at once removes your ability to pause a ring."],
      ("art4", "art50", "rmf"), policies=("ai-copilot-use-policy",), rec=("copilot-usage-report",)),
  ]},
 {"id": "incident", "title": "Incident response, rollback and troubleshooting", "time": "Prepare: 1 day",
  "goal": "Anyone on call can pause the service, revoke access and preserve evidence within the hour.",
  "steps": [
   st("Pause and revoke",
      "Runbook names who can execute each step, and it has been walked through once",
      ["Order: disable or narrow connectors and agent tools → revoke API keys → remove the access group or block the app at the IdP → preserve logs and exports → notify per your incident process.",
       "Deletion semantics: deleting chats in the UI may not delete backups, logs or legally held copies. Ask the vendor, per your contract, what deletion covers and how long it takes; record the answer.",
       "Personal-data incidents follow your GDPR breach process; the DPO decides on notification."],
      ["Revoking users but leaving a service-identity connector live keeps the data flowing."],
      ("gdpr", "genai")),
   st("Troubleshoot common failures narrowly",
      "Each fix keeps the control intact",
      ["Users cannot sign in: check IdP app assignment, group membership and certificate — do not re-enable local passwords.",
       "RAG returns too little: check connector scope and indexing; returns too much: oversharing in the source — fix permissions, not the prompt.",
       "Agent action blocked: check the allow-list and confirmation gate; widen one scope with approval, not to 'all'.",
       "Rollback a ring: remove that ring's group, keep logs, tell users the same day, and record the reason in the decision record."],
      ["The fastest unblock is usually the next incident."],
      ("owasp",), guides=("enterprise-ai-governance",)),
  ]},
 {"id": "reapprove", "title": "Periodic reapproval and change triggers", "time": "Recurring",
  "goal": "Approval stays true as the vendor, the use and the law change.",
  "steps": [
   st("Review on a schedule and on triggers",
      "Expiry date set, triggers documented, and a reviewer named",
      ["Suggested cadence: 12 months for low, 6 months for medium and high — editorial suggestion.",
       "Re-run classification and decision when: the plan or terms change; new subprocessors or regions; a new connector, data class or user population; the service moves up the ladder (chat → RAG → agent); a significant security incident; a new legal determination by Legal/DPO.",
       "At review: confirm evidence still current, admin and access lists, usage and cost, open risks, and whether the service is still needed. Retire unused services and revoke their access."],
      ["Silent feature launches by vendors can move a chat tool into agent territory without a new request."],
      ("rmf", "genai"), tools=("enterprise-ai-approved-inventory",)),
   st("Worked example (fictional): a contract-summary RAG assistant",
      "Reader can map each phase to the example",
      ["Fictional example — not a real organisation or vendor. 'Nordwind Logistics' Legal team requests an assistant that summarises supplier contracts stored in one document library.",
       "Intake: owner Head of Legal; rung = RAG; data = confidential contracts containing names and contact details of supplier staff (personal data). Tier = Medium (personal data plus a connector).",
       "Vendor: plan offers SSO, configurable retention and an EU processing option; training on customer content is contractually excluded on this plan; DPA signed. Audit export is only on a higher tier — recorded as a limitation.",
       "Decision: CONDITIONAL GO — connector limited to the contracts library via a read-only service identity; no special-category data; audit-export limitation accepted by the AI risk owner until reapproval in 6 months.",
       "Pilot: 8 users, 15 reference contracts, a planted injection document; one finding (summary followed injected text) fixed by instructing users to verify against source and restricting the library to approved uploaders. Exit criteria met; inventory updated to Approved with expiry."],
      [], ("owasp", "rmf")),
  ]},
]
