/* Enterprise AI readiness check. Runs entirely in the browser.
 * Answers are never sent to Tenant Recipes. localStorage is used only if the visitor opts in.
 * Also loadable in Node for tests (module.exports). */
(function (root) {
  "use strict";

  var STORAGE_KEY = "tr-ai-readiness-v1";

  var SECTIONS = [
    {
      id: "tools",
      title: "Which AI tools are in use?",
      lead: "List every assistant staff already use or that you plan to approve. Consumer logins count.",
      questions: [
        {
          id: "vendors",
          type: "multi",
          label: "Select every tool that is in use or in scope for this check.",
          required: true,
          options: [
            { id: "copilot", label: "Microsoft Copilot (Microsoft 365 Copilot or Copilot Chat)" },
            { id: "chatgpt", label: "ChatGPT (OpenAI, any plan)" },
            { id: "claude", label: "Claude (Anthropic)" },
            { id: "grok", label: "Grok (xAI)" },
            { id: "gemini", label: "Gemini or Google Workspace AI" },
            { id: "other", label: "Other enterprise or self-hosted AI", extra: true },
            { id: "none", label: "None yet — we are still planning", exclusive: true }
          ]
        },
        {
          id: "consumer",
          type: "single",
          label: "Are staff using consumer or unmanaged accounts for work (for example a personal ChatGPT, Claude or Grok login)?",
          required: true,
          options: [
            { id: "yes", label: "Yes, we know they are" },
            { id: "suspect", label: "We suspect so, but have no inventory" },
            { id: "unchecked", label: "We have not checked" },
            { id: "no", label: "No — only approved, organisation-managed accounts" }
          ]
        }
      ]
    },
    {
      id: "data",
      title: "Data sensitivity and classification",
      lead: "The risk is driven by what the service can see, not by the vendor name.",
      questions: [
        {
          id: "sensitivity",
          type: "single",
          label: "What is the most sensitive class of data users may paste into a prompt or connect through a plugin or index?",
          required: true,
          options: [
            { id: "public", label: "Public or non-confidential internal data only" },
            { id: "internal", label: "Internal business data (not personal, not customer-confidential)" },
            { id: "personal", label: "Personal data (GDPR or equivalent)" },
            { id: "confidential", label: "Confidential or customer data" },
            { id: "special", label: "Special-category or otherwise regulated data" },
            { id: "unknown", label: "We do not know / we have no classification scheme in use" }
          ]
        },
        {
          id: "prohibited",
          type: "single",
          label: "Is there a written list of data classes that must not be entered or connected (for example secrets, regulated records)?",
          required: true,
          options: [
            { id: "yes", label: "Yes, and users can find it" },
            { id: "partial", label: "A list exists, but it is informal or hard to find" },
            { id: "no", label: "No written list" }
          ]
        }
      ]
    },
    {
      id: "permissions",
      title: "Permissions and oversharing",
      lead: "Grounded assistants surface what the connecting identity can already read. Fix that scope first.",
      questions: [
        {
          id: "pattern",
          type: "single",
          label: "What is the highest use pattern you will enable (including features planned later)?",
          required: true,
          options: [
            { id: "chat", label: "Chat only — users type or paste; no connectors to internal systems" },
            { id: "rag", label: "Grounded / RAG — the service reads internal mail, files, tickets or similar" },
            { id: "agent", label: "Agents or actions — the service can send messages, change records or run tools" }
          ]
        },
        {
          id: "oversharing",
          type: "single",
          label: "Have you assessed oversharing on the stores an assistant can ground on (open links, broad groups, inherited permissions)?",
          required: true,
          options: [
            { id: "yes", label: "Yes, and we are closing the findings" },
            { id: "progress", label: "In progress" },
            { id: "no", label: "Not yet" },
            { id: "na", label: "Not applicable — chat only, no connectors" }
          ]
        },
        {
          id: "labels",
          type: "single",
          label: "Do sensitivity labels or an equivalent classification apply, and does the assistant honour them (including encryption and exclusion)?",
          required: true,
          options: [
            { id: "yes", label: "Yes, and we have checked the behaviour" },
            { id: "partial", label: "Labels exist, but AI behaviour is untested or incomplete" },
            { id: "no", label: "No labels, or they are not applied where AI can reach" },
            { id: "unknown", label: "We do not know" }
          ]
        }
      ]
    },
    {
      id: "identity",
      title: "Identity and Conditional Access",
      lead: "Every approved tool should sign in through your identity provider, with a policy you can change.",
      questions: [
        {
          id: "sso",
          type: "single",
          label: "Do approved AI tools sign in through your identity provider (SSO), not personal emails?",
          required: true,
          options: [
            { id: "all", label: "Yes — every approved tool" },
            { id: "some", label: "Some tools only" },
            { id: "planning", label: "Planned, not in place" },
            { id: "none", label: "No" }
          ]
        },
        {
          id: "mfa",
          type: "single",
          label: "What authentication is required to use those tools?",
          required: true,
          options: [
            { id: "phish", label: "Phishing-resistant MFA (passkeys, FIDO2, Windows Hello for Business, or equivalent)" },
            { id: "mfa", label: "MFA, but not phishing-resistant" },
            { id: "password", label: "Password only, or we do not know" },
            { id: "unknown", label: "We have not checked the grant controls" }
          ]
        },
        {
          id: "ca",
          type: "single",
          label: "Is Conditional Access (or the vendor's equivalent access policy) scoped to the AI apps, including a compliant or managed device where you require one?",
          required: true,
          options: [
            { id: "yes", label: "Yes" },
            { id: "partial", label: "Partial — some apps or some controls only" },
            { id: "no", label: "No dedicated policy" },
            { id: "unknown", label: "We do not know" }
          ]
        }
      ]
    },
    {
      id: "dlp",
      title: "Data loss prevention",
      lead: "Prevent the paste and the upload, not only the policy document.",
      questions: [
        {
          id: "dlp",
          type: "single",
          label: "Does DLP (or an equivalent control) cover prompts, file uploads and AI connectors for the tools in scope?",
          required: true,
          options: [
            { id: "yes", label: "Yes, for the tools in scope" },
            { id: "partial", label: "Partial — some tools, channels or data types only" },
            { id: "no", label: "No" },
            { id: "unknown", label: "We do not know" }
          ]
        },
        {
          id: "browser",
          type: "single",
          label: "Do you inspect or block unsanctioned AI sites in the browser or on the endpoint (secure web gateway, Edge DLP, CASB, or similar)?",
          required: true,
          options: [
            { id: "yes", label: "Yes" },
            { id: "partial", label: "Partial or in pilot" },
            { id: "no", label: "No" },
            { id: "unknown", label: "We do not know" }
          ]
        }
      ]
    },
    {
      id: "audit",
      title: "Logging and audit",
      lead: "You will need evidence when something is pasted, leaked or hallucinated into a decision.",
      questions: [
        {
          id: "logs",
          type: "single",
          label: "Can you retain and search prompts, responses or admin audit logs for each approved tool?",
          required: true,
          options: [
            { id: "yes", label: "Yes, and we know how to search them" },
            { id: "some", label: "For some tools only" },
            { id: "no", label: "No, or the plan we bought does not offer export" },
            { id: "unknown", label: "We have not checked" }
          ]
        },
        {
          id: "retention",
          type: "single",
          label: "Is a retention period for those records decided and documented (including vendor-side retention)?",
          required: true,
          options: [
            { id: "yes", label: "Yes" },
            { id: "partial", label: "Vendor default only, not reviewed" },
            { id: "no", label: "No" }
          ]
        }
      ]
    },
    {
      id: "training",
      title: "User guidance and literacy",
      lead: "A control that users have never been told about will not be followed.",
      questions: [
        {
          id: "guidance",
          type: "single",
          label: "Have users been told, in writing, what they may and may not paste or connect?",
          required: true,
          options: [
            { id: "yes", label: "Yes — written guidance they can find" },
            { id: "informal", label: "Only informal advice (a meeting, a chat post)" },
            { id: "no", label: "Not yet" }
          ]
        },
        {
          id: "literacy",
          type: "single",
          label: "Is there a named briefing or training on acceptable use and the limits of AI output (human review before it leaves the organisation)?",
          required: true,
          options: [
            { id: "yes", label: "Yes" },
            { id: "planned", label: "Planned, not delivered" },
            { id: "no", label: "No" }
          ]
        }
      ]
    },
    {
      id: "approval",
      title: "Approval process",
      lead: "One accountable decision per service, with an owner and an expiry date.",
      questions: [
        {
          id: "inventory",
          type: "single",
          label: "Do you keep an approved / conditional / denied inventory of AI tools that an auditor could check?",
          required: true,
          options: [
            { id: "yes", label: "Yes" },
            { id: "informal", label: "An informal list only" },
            { id: "no", label: "No inventory" }
          ]
        },
        {
          id: "owners",
          type: "single",
          label: "Does each approved or conditional service have a named business owner and a technical owner?",
          required: true,
          options: [
            { id: "yes", label: "Yes, for every service" },
            { id: "some", label: "For some services only" },
            { id: "no", label: "No named owners" }
          ]
        },
        {
          id: "decision",
          type: "single",
          label: "Is there a written go / conditional go / no-go decision, with conditions, blockers and an expiry or reapproval date?",
          required: true,
          options: [
            { id: "yes", label: "Yes" },
            { id: "informal", label: "An informal nod, no written record" },
            { id: "no", label: "No decision record" }
          ]
        },
        {
          id: "contract",
          type: "single",
          label: "Have you reviewed the contract and data-processing terms for the exact plan you buy (training use, retention, region, subprocessors)?",
          required: true,
          options: [
            { id: "yes", label: "Yes, for the tools in scope" },
            { id: "some", label: "For some tools only" },
            { id: "no", label: "Not started" },
            { id: "na", label: "Not applicable — still planning, no service selected" }
          ]
        }
      ]
    }
  ];

  var LINKS = {
    hub: { href: "../../ai/index.html", label: "Enterprise AI hub" },
    approval: { href: "../../guides/enterprise-ai-service-approval.html", label: "Approve and deploy an AI service (any vendor)" },
    governance: { href: "../../guides/enterprise-ai-governance.html", label: "Enterprise AI governance pillar" },
    inventory: { href: "../../tools/enterprise-ai-approved-inventory.html", label: "AI approved-tools inventory method" },
    policy: { href: "../../policies/ai-copilot-use-policy.html", label: "AI and Copilot use policy template" },
    copilotReady: { href: "../../recipes/copilot-readiness-checklist.html", label: "Copilot readiness checklist" },
    oversharing: { href: "../../recipes/purview-oversharing-assessment.html", label: "Find oversharing before Copilot does" },
    labels: { href: "../../recipes/purview-sensitivity-labels-copilot.html", label: "Make Copilot respect sensitivity labels" },
    dlp: { href: "../../recipes/purview-dlp-copilot-location.html", label: "DLP policy location for Copilot" },
    rcd: { href: "../../recipes/sharepoint-restricted-content-discovery.html", label: "Restricted Content Discovery" },
    mfa: { href: "../../recipes/ca-require-mfa-copilot.html", label: "Phishing-resistant MFA for Copilot" },
    audit: { href: "../../recipes/purview-audit-copilot.html", label: "Audit Copilot interactions" },
    retention: { href: "../../recipes/purview-retention-copilot.html", label: "Retention for Copilot interactions" },
    agents: { href: "../../recipes/agents-restrict-blueprint-creation.html", label: "Decide who can create agents" }
  };

  var BOX = {
    why: [
      "Start with an inventory and a data boundary before you scale any assistant. The questions here follow that order on purpose.",
      "The check is vendor-neutral: the same control questions apply to Microsoft Copilot, ChatGPT, Claude, Grok, Gemini or a self-hosted model. Vendor features differ by plan and change; confirm them in the current admin documentation and contract.",
      "Fix oversharing and identity first. Adding an assistant on top of open links or personal logins widens a problem you already have."
    ],
    alt: [
      "If you only need a pre-flight list before assigning Microsoft Copilot licences, use the Copilot readiness checklist instead — it is shorter and Microsoft-specific.",
      "If a team has asked for one named service, run the approval and deployment runbook. This check is a programme-level gap analysis, not a substitute for a go / no-go record on that service.",
      "If you already have a mature AI governance programme and a complete inventory, you may not need this check. Use it when you want a fresh view of the gaps."
    ],
    unverified: [
      "This is a planning aid produced from your answers. It is not a certification, an audit, or evidence that a service is GDPR- or AI Act-compliant. Legal and regulatory determinations stay with your organisation.",
      "Nothing here was lab-tested or run in a production tenant by Tenant Recipes. Feature availability, retention terms and DLP coverage differ by vendor and by plan, and they change.",
      "Items marked as assumptions or plan-specific must be confirmed in the vendor's current contract, DPA or admin documentation for the exact SKU you buy."
    ]
  };

  function optionById(q, id) {
    for (var i = 0; i < q.options.length; i++) if (q.options[i].id === id) return q.options[i];
    return null;
  }

  function questionById(id) {
    for (var s = 0; s < SECTIONS.length; s++) {
      for (var q = 0; q < SECTIONS[s].questions.length; q++) {
        if (SECTIONS[s].questions[q].id === id) return SECTIONS[s].questions[q];
      }
    }
    return null;
  }

  function vendorsOf(answers) {
    var v = (answers && answers.vendors) || {};
    var ids = Object.keys(v).filter(function (k) { return v[k] && k !== "otherText"; });
    return ids;
  }

  function hasVendor(answers, id) {
    var v = (answers && answers.vendors) || {};
    return !!v[id];
  }

  function planningOnly(answers) {
    return hasVendor(answers, "none") && vendorsOf(answers).length === 1;
  }

  function usesCopilot(answers) { return hasVendor(answers, "copilot"); }
  function usesThirdParty(answers) {
    return ["chatgpt", "claude", "grok", "gemini", "other"].some(function (id) { return hasVendor(answers, id); });
  }

  function item(pri, text, opts) {
    opts = opts || {};
    var out = { pri: pri, text: text };
    if (opts.why) out.why = opts.why;
    if (opts.link) {
      out.href = opts.link.href;
      out.hrefLabel = opts.link.label;
    }
    return out;
  }

  function snapshotFor(answers, first, then, verify) {
    var sens = answers.sensitivity;
    var highData = sens === "special" || sens === "confidential" || sens === "personal";
    var unknownData = sens === "unknown";
    var consumerRisk = answers.consumer === "yes" || answers.consumer === "suspect" || answers.consumer === "unchecked";
    var noSso = answers.sso === "none" || answers.sso === "planning";
    var noInventory = answers.inventory === "no";
    var agents = answers.pattern === "agent";
    var rag = answers.pattern === "rag" || answers.pattern === "agent";
    var overshareOpen = rag && (answers.oversharing === "no" || answers.oversharing === "progress");
    var weakAuth = answers.mfa === "password" || answers.mfa === "unknown";
    var noDlp = answers.dlp === "no" || answers.dlp === "unknown";
    var noLogs = answers.logs === "no" || answers.logs === "unknown";
    var p1 = first.length;

    if (unknownData || noInventory || consumerRisk || noSso || weakAuth || (rag && answers.oversharing === "no") || (highData && noDlp)) {
      return {
        level: "gaps",
        label: "Foundation gaps",
        blurb: "There are control gaps that should be closed before you scale use, and in several cases before a pilot with real data. The 'Do first' list is the starting order."
      };
    }
    if (p1 > 0 || highData || agents || overshareOpen || noLogs || answers.decision !== "yes") {
      var level = (answers.decision === "yes" && answers.sso === "all" && !consumerRisk && answers.guidance === "yes") ? "pilot" : "partial";
      if (level === "pilot" && !(highData && answers.contract !== "yes") && !(agents && answers.owners !== "yes")) {
        return {
          level: "pilot",
          label: "Ready to pilot, with conditions",
          blurb: "The foundations are in place enough for a tightly scoped pilot on approved tools, with the remaining items treated as conditions. Do not treat this as approval to process special-category or regulated data."
        };
      }
      return {
        level: "partial",
        label: "Partly in place",
        blurb: "Some controls exist, but the remaining gaps would follow users into production. Work the 'Do first' items, then the rest, before you widen access."
      };
    }
    if (answers.sso === "all" && (answers.mfa === "phish" || answers.mfa === "mfa") && answers.inventory === "yes" && answers.decision === "yes" && answers.guidance === "yes" && !consumerRisk && !unknownData) {
      return {
        level: "scale",
        label: "Foundations look solid — verify before you scale",
        blurb: "Your answers describe a governed programme. Confirm each 'Already in place' item in the admin centre or contract before you add users or a higher use pattern (for example moving from chat to connectors or agents)."
      };
    }
    return {
      level: "partial",
      label: "Partly in place",
      blurb: "Some controls exist, but the remaining gaps would follow users into production. Work the 'Do first' items, then the rest, before you widen access."
    };
  }

  function generate(answers) {
    answers = answers || {};
    var first = [];
    var then = [];
    var verify = [];
    var vendors = vendorsOf(answers);
    var copilot = usesCopilot(answers);
    var third = usesThirdParty(answers);
    var planning = planningOnly(answers);
    var rag = answers.pattern === "rag" || answers.pattern === "agent";
    var agent = answers.pattern === "agent";
    var highData = answers.sensitivity === "special" || answers.sensitivity === "confidential";
    var personal = answers.sensitivity === "personal" || highData;

    // Tools / shadow AI
    if (answers.consumer === "unchecked" || answers.consumer === "suspect") {
      first.push(item("P1", "Discover which AI services staff already use, including consumer and unmanaged accounts, and record them on the inventory as approved, conditional or denied.", {
        why: "You cannot set a data boundary for tools you have not found.",
        link: LINKS.inventory
      }));
    } else if (answers.consumer === "yes") {
      first.push(item("P1", "Stop work use of consumer or unmanaged accounts: they rarely give you processor terms, SSO, retention control or audit export. Route people to an approved plan, or record a written denial.", {
        why: "Consumer terms are not an approval path for company data.",
        link: LINKS.inventory
      }));
    } else if (answers.consumer === "no") {
      verify.push(item("Verify", "Re-check periodically that staff are not using personal AI accounts for work (browser, CASB or secure web gateway logs, and a simple staff question in the briefing).", { link: LINKS.inventory }));
    }

    if (answers.inventory === "no" || answers.inventory === "informal") {
      first.push(item("P1", "Build an approved / conditional / denied register an auditor can check: service, plan, owner, data classes, decision and expiry.", {
        link: LINKS.inventory
      }));
    } else if (answers.inventory === "yes") {
      verify.push(item("Verify", "Open the inventory and confirm every tool you ticked on this check has a current decision and an owner.", { link: LINKS.inventory }));
    }

    if (planning) {
      then.push(item("P2", "When you pick a first service, run the vendor-neutral approval runbook before anyone uses real data in a trial.", { link: LINKS.approval }));
    }

    // Data
    if (answers.sensitivity === "unknown") {
      first.push(item("P1", "Adopt (or apply) a data classification scheme and map it to AI use: what may be pasted, what may be connected, and what is prohibited.", {
        why: "Without a classification, every later DLP, label and contract check is guesswork."
      }));
    } else if (answers.sensitivity === "special") {
      first.push(item("P1", "Treat this as a high-tier use: involve your DPO or counsel before real special-category or regulated data is entered or connected. Record the legal checks performed; do not label the service 'compliant' in the file.", {
        why: "GDPR, a DPIA (Art. 35) or AI Act duties may apply — that determination is yours, not this checklist's."
      }));
    } else if (personal) {
      then.push(item("P2", "Ask your DPO function to confirm whether this use is likely high-risk processing and whether a DPIA is required, and keep that decision with the service record.", { link: LINKS.governance }));
    }

    if (answers.prohibited === "no" || answers.prohibited === "partial") {
      first.push(item("P1", "Publish a short, findable list of prohibited data classes (for example credentials and secrets, special-category data, regulated customer records) and link it from the acceptable-use policy.", { link: LINKS.policy }));
    } else {
      verify.push(item("Verify", "Confirm the prohibited-data list is still accurate for the tools and connectors you have enabled."));
    }

    // Permissions
    if (rag && (answers.oversharing === "no" || answers.oversharing === "na")) {
      first.push(item("P1", "Assess oversharing on every store a connector or index can read (open sharing links, broad groups, inherited permissions) and close high-impact findings before you turn grounding on.", {
        why: "The assistant will surface what the connecting identity can already reach.",
        link: copilot ? LINKS.oversharing : LINKS.governance
      }));
    } else if (rag && answers.oversharing === "progress") {
      then.push(item("P2", "Finish the oversharing assessment and make closure of high-impact findings a condition of the pilot, not a follow-up.", { link: copilot ? LINKS.oversharing : LINKS.governance }));
    } else if (answers.oversharing === "yes") {
      verify.push(item("Verify", "Re-run the oversharing assessment when you add a site, a connector or a new group.", { link: copilot ? LINKS.oversharing : LINKS.governance }));
    }

    if (answers.pattern === "chat" && answers.oversharing === "na") {
      then.push(item("P2", "If you later enable connectors or retrieval over internal content, re-run this check and complete an oversharing review first. Treat that as a change of use pattern, not a feature toggle.", { link: LINKS.approval }));
    }

    if (agent) {
      first.push(item("P1", "List every action an agent may take (send mail, create records, run code, call a connector) and restrict who can create or publish agents. Every tool scope is a potential unintended action.", {
        link: copilot ? LINKS.agents : LINKS.governance
      }));
    }

    if (answers.labels === "no" || answers.labels === "unknown") {
      then.push(item("P2", "Apply sensitivity labels or an equivalent classification where the assistant can reach content, and test whether the tool honours encryption, exclusion and 'do not process' rules before you scale.", {
        link: copilot ? LINKS.labels : LINKS.governance
      }));
    } else if (answers.labels === "partial") {
      then.push(item("P2", "Test label behaviour in the assistant (including encrypted content and site exclusions) and record the result. Do not assume a label is a data boundary until you have seen it work.", {
        link: copilot ? LINKS.labels : LINKS.rcd
      }));
    } else if (answers.labels === "yes") {
      verify.push(item("Verify", "Spot-check that labelled or encrypted content is not surfaced or processed in ways your policy forbids.", { link: copilot ? LINKS.labels : LINKS.governance }));
    }

    // Identity
    if (answers.sso === "none" || answers.sso === "planning") {
      first.push(item("P1", "Put every approved tool behind your identity provider (SSO) on an enterprise plan that actually offers it, before staff use real data. If the affordable plan has no SSO, that is a valid no-go or a 'non-personal data only' condition.", { link: LINKS.approval }));
    } else if (answers.sso === "some") {
      first.push(item("P1", "Close SSO gaps: any approved tool still on personal emails or a plan without SSO should be upgraded, scoped down, or moved to denied.", { link: LINKS.approval }));
    } else if (answers.sso === "all") {
      verify.push(item("Verify", "Confirm SSO is enforced (not optional) and that guest or personal sign-in is blocked on each approved tool."));
    }

    if (answers.mfa === "password" || answers.mfa === "unknown") {
      first.push(item("P1", "Require MFA for every AI sign-in, preferably phishing-resistant, and confirm it in Conditional Access or the vendor's equivalent policy.", { link: copilot ? LINKS.mfa : LINKS.governance }));
    } else if (answers.mfa === "mfa") {
      then.push(item("P2", "Move AI sign-in to a phishing-resistant authentication strength (passkeys, FIDO2 or Windows Hello for Business, or the vendor equivalent). SMS and voice are being retired as a Microsoft-provided method in February 2027.", { link: copilot ? LINKS.mfa : LINKS.governance }));
    } else if (answers.mfa === "phish") {
      verify.push(item("Verify", "Confirm the phishing-resistant strength still applies to each new AI app or agent identity you add.", { link: copilot ? LINKS.mfa : LINKS.governance }));
    }

    if (answers.ca === "no" || answers.ca === "unknown") {
      then.push(item("P2", "Add Conditional Access (or the vendor equivalent) for the AI apps: grant controls, device compliance if you require it, and a break-glass exclusion you have tested.", { link: copilot ? LINKS.mfa : LINKS.governance }));
    } else if (answers.ca === "partial") {
      then.push(item("P2", "Extend access policy to every approved AI app, including any new agent identities, and review exclusions.", { link: copilot ? LINKS.mfa : LINKS.governance }));
    } else if (answers.ca === "yes") {
      verify.push(item("Verify", "Review the AI-related access policies after each new app registration or agent is approved."));
    }

    // DLP
    if (answers.dlp === "no" || answers.dlp === "unknown") {
      first.push(item("P1", "Turn on DLP (or an equivalent control) for the AI locations in scope — prompts, uploads and connectors — and test a prohibited-data paste before you widen access.", {
        link: copilot ? LINKS.dlp : LINKS.governance
      }));
    } else if (answers.dlp === "partial") {
      then.push(item("P2", "Fill DLP gaps for the tools and channels not yet covered, including browser or endpoint controls for unsanctioned sites if those are in use.", { link: copilot ? LINKS.dlp : LINKS.governance }));
    } else if (answers.dlp === "yes") {
      verify.push(item("Verify", "Test that a prohibited data class is blocked or alerted in each approved tool, not only in a policy list.", { link: copilot ? LINKS.dlp : LINKS.governance }));
    }

    if (answers.browser === "no" || answers.browser === "unknown") {
      then.push(item("P2", "Decide how you will handle unsanctioned AI sites in the browser or on the endpoint (block, warn, or inspect). An acceptable-use policy alone will not stop a paste into a consumer chatbot.", { link: LINKS.governance }));
    } else if (answers.browser === "partial" || answers.browser === "yes") {
      verify.push(item("Verify", "Confirm newly popular AI domains are in your allow/block or inspection list, and that any TLS inspection does not break required sign-in safeguards."));
    }

    if (third) {
      then.push(item("P2", "For non-Microsoft tools, confirm in the current admin documentation and contract that DLP, retention and audit exist on the exact plan you buy — and record 'not available on this plan' if they do not.", { link: LINKS.approval }));
    }

    // Audit
    if (answers.logs === "no" || answers.logs === "unknown") {
      first.push(item("P1", "Establish how you will retain and search prompts, responses or admin audit events for each approved tool. If a plan cannot export logs, record that as a limitation or a no-go for sensitive uses.", { link: copilot ? LINKS.audit : LINKS.approval }));
    } else if (answers.logs === "some") {
      then.push(item("P2", "Close logging gaps on the tools that have no search or export today, or narrow those tools' permitted data classes.", { link: copilot ? LINKS.audit : LINKS.approval }));
    } else if (answers.logs === "yes") {
      verify.push(item("Verify", "Run a test search for a known prompt or admin action and confirm the retention you think you have is the retention you actually have.", { link: copilot ? LINKS.audit : LINKS.retention }));
    }

    if (answers.retention === "no" || answers.retention === "partial") {
      then.push(item("P2", "Decide and document retention for prompts, outputs and files, including vendor-side defaults, deletion behaviour and any legal hold. Re-check at reapproval: terms change.", { link: copilot ? LINKS.retention : LINKS.approval }));
    } else if (answers.retention === "yes") {
      verify.push(item("Verify", "Confirm the documented retention still matches the vendor's current terms for your plan.", { link: copilot ? LINKS.retention : LINKS.approval }));
    }

    // Training
    if (answers.guidance === "no" || answers.guidance === "informal") {
      first.push(item("P1", "Publish short written guidance users can find: approved tools, prohibited data classes, and the rule that AI output needs human review before it is sent outside the organisation.", { link: LINKS.policy }));
    } else {
      verify.push(item("Verify", "Check that the guidance still names the tools you have actually approved, and that new starters receive it.", { link: LINKS.policy }));
    }

    if (answers.literacy === "no" || answers.literacy === "planned") {
      then.push(item("P2", "Deliver a named briefing on acceptable use and the limits of AI output. Staff AI literacy is also an expectation under the EU AI Act (Art. 4) where that law applies — counsel confirms applicability.", { link: LINKS.governance }));
    } else {
      verify.push(item("Verify", "Record who has completed the briefing and refresh it when you add a higher use pattern (connectors or agents)."));
    }

    // Approval
    if (answers.owners === "no" || answers.owners === "some") {
      then.push(item("P2", "Name a business owner and a technical owner for every approved or conditional service. A request without a business owner has nobody to accept residual risk.", { link: LINKS.approval }));
    } else if (answers.owners === "yes") {
      verify.push(item("Verify", "Confirm owners are still in post and that each one knows they own residual risk and reapproval."));
    }

    if (answers.decision === "no" || answers.decision === "informal") {
      first.push(item("P1", "Write a go / conditional go / no-go decision for each in-scope service: evidence, conditions, blockers, permitted data classes and an expiry date.", { link: LINKS.approval }));
    } else {
      verify.push(item("Verify", "Check that no approved service is past its expiry or reapproval date.", { link: LINKS.approval }));
    }

    if (answers.contract === "no" || answers.contract === "some") {
      then.push(item("P2", "File plan-specific contract and DPA evidence: training use of customer content, retention, regions and transfer mechanism, subprocessors, audit export and SSO. An answer from a chatbot or a sales email is not contract evidence.", { link: LINKS.approval }));
    } else if (answers.contract === "yes") {
      verify.push(item("Verify", "Re-read the terms at reapproval, or sooner if the vendor announces a change."));
    }

    // Vendor-specific reminders
    if (copilot) {
      then.push(item("P2", "On Microsoft 365, confirm Copilot-specific controls that match your use: DLP for the Copilot location, sensitivity label behaviour, Restricted Content Discovery where a site must stay out of grounding, and audit of Copilot interactions.", {
        link: LINKS.copilotReady
      }));
    }

    var snap = snapshotFor(answers, first, then, verify);
    var related = [LINKS.hub, LINKS.approval, LINKS.governance, LINKS.inventory, LINKS.policy];
    if (copilot) related = related.concat([LINKS.copilotReady, LINKS.oversharing, LINKS.dlp, LINKS.audit]);

    var result = {
      snapshot: snap,
      groups: [
        { id: "first", title: "Do first", items: first },
        { id: "then", title: "Then", items: then },
        { id: "verify", title: "Already in place — verify", items: verify }
      ].filter(function (g) { return g.items.length; }),
      boxes: BOX,
      vendors: vendors,
      related: uniqueLinks(related),
      answers: answers
    };
    result.markdown = toMarkdown(result, answers);
    return result;
  }

  function uniqueLinks(arr) {
    var seen = {};
    var out = [];
    for (var i = 0; i < arr.length; i++) {
      if (!seen[arr[i].href]) {
        seen[arr[i].href] = 1;
        out.push(arr[i]);
      }
    }
    return out;
  }

  function vendorLabels(answers) {
    var q = questionById("vendors");
    var ids = vendorsOf(answers);
    var labels = ids.map(function (id) {
      var o = optionById(q, id);
      var t = o ? o.label : id;
      if (id === "other" && answers.vendors && answers.vendors.otherText) t += " (" + answers.vendors.otherText + ")";
      return t;
    });
    return labels;
  }

  function todayISO(d) {
    d = d || new Date();
    var y = d.getFullYear();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + day;
  }

  function toMarkdown(result, answers) {
    var lines = [];
    lines.push("# Enterprise AI readiness checklist");
    lines.push("");
    lines.push("Generated on " + todayISO() + " from the Tenant Recipes AI readiness check.");
    lines.push("This is a planning aid, not a certification or an audit.");
    lines.push("");
    lines.push("## Snapshot");
    lines.push("");
    lines.push("**" + result.snapshot.label + "** — " + result.snapshot.blurb);
    lines.push("");
    lines.push("## Tools you recorded");
    lines.push("");
    vendorLabels(answers).forEach(function (t) { lines.push("- " + t); });
    lines.push("");
    result.groups.forEach(function (g) {
      lines.push("## " + g.title);
      lines.push("");
      g.items.forEach(function (it) {
        lines.push("- [ ] " + it.text);
        if (it.why) lines.push("  - Why: " + it.why);
        if (it.hrefLabel) lines.push("  - See: " + it.hrefLabel);
      });
      lines.push("");
    });
    lines.push("## Why we recommend this");
    lines.push("");
    result.boxes.why.forEach(function (t) { lines.push("- " + t); });
    lines.push("");
    lines.push("## When to choose something else");
    lines.push("");
    result.boxes.alt.forEach(function (t) { lines.push("- " + t); });
    lines.push("");
    lines.push("## Not verified");
    lines.push("");
    result.boxes.unverified.forEach(function (t) { lines.push("- " + t); });
    lines.push("");
    lines.push("## Related pages");
    lines.push("");
    result.related.forEach(function (l) { lines.push("- " + l.label); });
    lines.push("");
    lines.push("tenantrecipes.com/ai/readiness-check/");
    lines.push("");
    return lines.join("\n");
  }

  function sectionComplete(section, answers) {
    for (var i = 0; i < section.questions.length; i++) {
      var q = section.questions[i];
      var err = questionError(q, answers);
      if (err) return false;
    }
    return true;
  }

  function questionError(q, answers) {
    if (q.type === "multi") {
      var v = answers[q.id] || {};
      var picked = q.options.filter(function (o) { return !!v[o.id]; });
      if (!picked.length) return "Select at least one option.";
      if (v.other && !(v.otherText && String(v.otherText).trim())) return "Name the other tool, or uncheck Other.";
      return "";
    }
    if (!answers[q.id]) return "Choose one option to continue.";
    return "";
  }

  function applyExclusive(q, answers, changedId, checked) {
    if (q.type !== "multi") return;
    var v = answers[q.id] || (answers[q.id] = {});
    var opt = optionById(q, changedId);
    if (!opt) return;
    if (checked && opt.exclusive) {
      q.options.forEach(function (o) { if (o.id !== changedId) v[o.id] = false; });
      v.otherText = "";
    } else if (checked && !opt.exclusive) {
      q.options.forEach(function (o) { if (o.exclusive) v[o.id] = false; });
    }
  }

  function defaultAnswers() {
    return { vendors: {} };
  }

  function loadSaved() {
    try {
      var raw = root.localStorage && root.localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var data = JSON.parse(raw);
      if (!data || !data.optIn || !data.answers) return null;
      return data;
    } catch (e) {
      return null;
    }
  }

  function save(answers, step, optIn) {
    try {
      if (!root.localStorage) return;
      if (!optIn) {
        root.localStorage.removeItem(STORAGE_KEY);
        return;
      }
      root.localStorage.setItem(STORAGE_KEY, JSON.stringify({
        optIn: true, answers: answers, step: step, saved: todayISO()
      }));
    } catch (e) { /* private mode or quota — ignore */ }
  }

  function clearSaved() {
    try { if (root.localStorage) root.localStorage.removeItem(STORAGE_KEY); } catch (e) {}
  }

  /* ---------------- DOM UI ---------------- */

  function $(id) { return document.getElementById(id); }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null && text !== "") n.textContent = text;
    return n;
  }

  function init() {
    var rootEl = $("air-app");
    if (!rootEl) return;

    var state = { step: 0, answers: defaultAnswers(), optIn: false, result: null, view: "form" };
    var saved = loadSaved();
    if (saved) {
      state.answers = saved.answers;
      state.step = Math.min(saved.step || 0, SECTIONS.length - 1);
      state.optIn = true;
    }

    function persist() { save(state.answers, state.step, state.optIn); }

    function showError(msg) {
      var box = $("air-err");
      if (!box) return;
      box.textContent = msg || "";
      box.hidden = !msg;
    }

    function renderProgress() {
      var nav = $("air-progress");
      if (!nav) return;
      nav.innerHTML = "";
      var ol = el("ol", "air-steps");
      SECTIONS.forEach(function (s, i) {
        var li = el("li", "air-step" + (i === state.step && state.view === "form" ? " is-current" : "") + (sectionComplete(s, state.answers) ? " is-done" : ""));
        var b = el("button", "air-step-btn", (i + 1) + ". " + s.title);
        b.type = "button";
        b.disabled = state.view === "results" && false;
        if (i > 0) {
          var prevOk = true;
          for (var j = 0; j < i; j++) if (!sectionComplete(SECTIONS[j], state.answers)) { prevOk = false; break; }
          if (!prevOk && i !== state.step) b.disabled = true;
        }
        b.addEventListener("click", function () {
          if (state.view === "results") {
            state.view = "form";
            state.result = null;
          }
          state.step = i;
          persist();
          render();
        });
        li.appendChild(b);
        ol.appendChild(li);
      });
      nav.appendChild(ol);
      var meta = $("air-stepmeta");
      if (meta) {
        meta.textContent = state.view === "results"
          ? "Your checklist"
          : ("Step " + (state.step + 1) + " of " + SECTIONS.length);
      }
    }

    function renderQuestion(q) {
      var fs = el("fieldset", "air-q");
      var lg = el("legend", "", q.label);
      fs.appendChild(lg);
      var name = "air-" + q.id;
      if (q.type === "multi") {
        var v = state.answers[q.id] || (state.answers[q.id] = {});
        q.options.forEach(function (o) {
          var row = el("label", "air-opt");
          var inp = document.createElement("input");
          inp.type = "checkbox";
          inp.name = name;
          inp.value = o.id;
          inp.checked = !!v[o.id];
          inp.addEventListener("change", function () {
            v[o.id] = inp.checked;
            applyExclusive(q, state.answers, o.id, inp.checked);
            if (!inp.checked && o.extra) v.otherText = "";
            persist();
            render();
          });
          row.appendChild(inp);
          row.appendChild(document.createTextNode(" " + o.label));
          fs.appendChild(row);
          if (o.extra && v[o.id]) {
            var extra = el("div", "air-extra");
            var lab = el("label", "", "Name of the other tool");
            lab.setAttribute("for", "air-other-text");
            var tx = document.createElement("input");
            tx.type = "text";
            tx.id = "air-other-text";
            tx.value = v.otherText || "";
            tx.autocomplete = "off";
            tx.addEventListener("input", function () {
              v.otherText = tx.value;
              persist();
            });
            extra.appendChild(lab);
            extra.appendChild(tx);
            fs.appendChild(extra);
          }
        });
      } else {
        q.options.forEach(function (o) {
          var row = el("label", "air-opt");
          var inp = document.createElement("input");
          inp.type = "radio";
          inp.name = name;
          inp.value = o.id;
          inp.checked = state.answers[q.id] === o.id;
          inp.addEventListener("change", function () {
            if (inp.checked) state.answers[q.id] = o.id;
            persist();
            showError("");
          });
          row.appendChild(inp);
          row.appendChild(document.createTextNode(" " + o.label));
          fs.appendChild(row);
        });
      }
      return fs;
    }

    function renderForm() {
      var pane = $("air-pane");
      pane.innerHTML = "";
      var s = SECTIONS[state.step];
      var h = el("h2", "air-h", s.title);
      h.id = "air-heading";
      pane.appendChild(h);
      pane.appendChild(el("p", "air-lead", s.lead));
      s.questions.forEach(function (q) { pane.appendChild(renderQuestion(q)); });

      var actions = el("div", "air-actions");
      if (state.step > 0) {
        var back = el("button", "btn", "Back");
        back.type = "button";
        back.addEventListener("click", function () {
          state.step -= 1;
          persist();
          render({ focus: true });
        });
        actions.appendChild(back);
      }
      var next = el("button", "btn p", state.step === SECTIONS.length - 1 ? "See my checklist" : "Continue");
      next.type = "button";
      next.addEventListener("click", function () {
        var bad = "";
        for (var i = 0; i < s.questions.length; i++) {
          bad = questionError(s.questions[i], state.answers);
          if (bad) break;
        }
        if (bad) {
          showError(bad);
          return;
        }
        showError("");
        if (state.step === SECTIONS.length - 1) {
          state.result = generate(state.answers);
          state.view = "results";
          persist();
          render({ focus: true });
          return;
        }
        state.step += 1;
        persist();
        render({ focus: true });
      });
      actions.appendChild(next);
      pane.appendChild(actions);
    }

    function renderList(items) {
      var ul = el("ul", "air-items");
      items.forEach(function (it) {
        var li = el("li", "air-item air-pri-" + (it.pri || "P2").toLowerCase());
        var top = el("div", "air-item-h");
        if (it.pri) top.appendChild(el("span", "air-pri", it.pri));
        top.appendChild(el("p", "air-item-t", it.text));
        li.appendChild(top);
        if (it.why) li.appendChild(el("p", "air-why", it.why));
        if (it.href) {
          var a = el("a", "air-more", it.hrefLabel || "Related page");
          a.href = it.href;
          li.appendChild(a);
        }
        ul.appendChild(li);
      });
      return ul;
    }

    function renderBox(title, texts, cls) {
      var aside = el("aside", "co " + cls);
      aside.appendChild(el("p", "co-h", title));
      var ul = el("ul");
      texts.forEach(function (t) { ul.appendChild(el("li", "", t)); });
      aside.appendChild(ul);
      return aside;
    }

    function renderResults() {
      var pane = $("air-pane");
      pane.innerHTML = "";
      var r = state.result;
      var h = el("h2", "air-h", "Your checklist");
      h.id = "air-heading";
      pane.appendChild(h);

      var snap = el("div", "air-snap air-snap-" + r.snapshot.level);
      snap.appendChild(el("p", "air-snap-k", "Readiness snapshot"));
      snap.appendChild(el("p", "air-snap-l", r.snapshot.label));
      snap.appendChild(el("p", "", r.snapshot.blurb));
      var tools = vendorLabels(state.answers);
      if (tools.length) snap.appendChild(el("p", "fine", "Tools you recorded: " + tools.join("; ") + "."));
      pane.appendChild(snap);

      r.groups.forEach(function (g) {
        var sec = el("section", "air-group");
        sec.appendChild(el("h3", "", g.title + " (" + g.items.length + ")"));
        sec.appendChild(renderList(g.items));
        pane.appendChild(sec);
      });

      pane.appendChild(renderBox("Why we recommend this", r.boxes.why, "co-info"));
      pane.appendChild(renderBox("When to choose something else", r.boxes.alt, "co-info"));
      pane.appendChild(renderBox("Not verified", r.boxes.unverified, "co-warn"));

      if (r.related.length) {
        var rel = el("section", "air-related");
        rel.appendChild(el("h3", "", "Related pages"));
        var ul = el("ul");
        r.related.forEach(function (l) {
          var li = el("li");
          var a = el("a", "", l.label);
          a.href = l.href;
          li.appendChild(a);
          ul.appendChild(li);
        });
        rel.appendChild(ul);
        pane.appendChild(rel);
      }

      var actions = el("div", "air-actions air-export");
      var copy = el("button", "btn p", "Copy as Markdown");
      copy.type = "button";
      copy.addEventListener("click", function () {
        var md = r.markdown;
        var done = function (ok) {
          copy.textContent = ok ? "Copied" : "Copy failed — select and copy from the download instead";
          setTimeout(function () { copy.textContent = "Copy as Markdown"; }, 2000);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(md).then(function () { done(true); }).catch(function () { done(false); });
        } else {
          done(false);
        }
      });
      var dl = el("button", "btn", "Download Markdown");
      dl.type = "button";
      dl.addEventListener("click", function () {
        var blob = new Blob([r.markdown], { type: "text/markdown;charset=utf-8" });
        var a = el("a");
        a.href = URL.createObjectURL(blob);
        a.download = "ai-readiness-checklist.md";
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
      });
      var printBtn = el("button", "btn", "Print");
      printBtn.type = "button";
      printBtn.addEventListener("click", function () { root.print(); });
      var again = el("button", "btn", "Change answers");
      again.type = "button";
      again.addEventListener("click", function () {
        state.view = "form";
        state.result = null;
        render({ focus: true });
      });
      actions.appendChild(copy);
      actions.appendChild(dl);
      actions.appendChild(printBtn);
      actions.appendChild(again);
      pane.appendChild(actions);

      var sub = $("air-subscribe");
      if (sub) sub.hidden = false;
    }

    function render(opts) {
      opts = opts || {};
      var sub = $("air-subscribe");
      if (sub) sub.hidden = state.view !== "results";
      document.querySelectorAll(".air-intro").forEach(function (n) { n.hidden = state.view === "results"; });
      renderProgress();
      if (state.view === "results") renderResults();
      else renderForm();
      if (opts.focus) {
        var progress = $("air-progress");
        if (progress && progress.scrollIntoView) {
          progress.scrollIntoView({ block: "start", behavior: "auto" });
        }
        var heading = $("air-heading");
        if (heading) {
          heading.setAttribute("tabindex", "-1");
          heading.focus({ preventScroll: true });
        }
      }
    }

    var saveBox = $("air-save");
    if (saveBox) {
      saveBox.checked = state.optIn;
      saveBox.addEventListener("change", function () {
        state.optIn = !!saveBox.checked;
        persist();
      });
    }
    var reset = $("air-reset");
    if (reset) {
      reset.addEventListener("click", function () {
        state.answers = defaultAnswers();
        state.step = 0;
        state.result = null;
        state.view = "form";
        clearSaved();
        if (saveBox) saveBox.checked = state.optIn;
        showError("");
        render({ focus: true });
      });
    }

    render();
  }

  var API = {
    SECTIONS: SECTIONS,
    LINKS: LINKS,
    BOX: BOX,
    STORAGE_KEY: STORAGE_KEY,
    generate: generate,
    questionError: questionError,
    sectionComplete: sectionComplete,
    applyExclusive: applyExclusive,
    vendorsOf: vendorsOf,
    toMarkdown: function (answers) { return generate(answers).markdown; },
    todayISO: todayISO,
    init: init
  };

  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  }

  if (typeof module === "object" && module.exports) module.exports = API;
  else root.AIReadiness = API;
})(typeof globalThis !== "undefined" ? globalThis : this);
