"""Technical guide (DRAFT, not registered): Arc-enable servers on any platform and patch them with
Azure Update Manager in a controlled weekend wave model (Friday / Saturday / Sunday / Monday) driven by
criticality, sensitivity and redundancy tags, with health gates between the halves of redundant pairs.
Builds on — and links to — the pillar guides azure-arc-onboarding-enterprise-scale and
azure-update-manager-enterprise-patching; it does not repeat their RBAC, network, classification or
troubleshooting detail.
Documentation checked against linked Microsoft Learn sources on 2026-11-11; practical, not lab-tested.
Draft written 2026-11-11 for editor review. NOT in GUIDES / build_site.py.
Text in `backticks` renders as <code>. Steps carry an extra optional "code" list of (label, text) blocks;
build_site.py does not render "code" yet — a small <pre> renderer is needed before publication. 'rec' = recipe ids, 'tools' = tools ids, 'guides' = guide slugs.
"""

SLUG = "arc-update-manager-weekend-waves"
TIER = "technical"
PUBLISHED = "2026-11-11"
VERIFIED = "2026-11-11"
UPDATED = "2026-11-11"
TITLE = "Weekend patch waves with Azure Arc and Update Manager"
SHORT = "Arc + Update Manager weekend waves"
DESC = (
    "A practical design for Arc-enabling servers on any platform (on-premises Windows and Linux, VMware, AWS, GCP and "
    "other clouds) and patching them with Azure Update Manager in a Friday-to-Monday wave model based on criticality, "
    "sensitivity and production dependencies: a tag model enforced with Azure Policy, governed onboarding, one Resource "
    "Graph overview of every server, maintenance configurations per wave with dynamic scopes, pre-event health gates so "
    "Monday never starts if Sunday's side A failed, a check that flags redundant pairs sharing a wave, emergency "
    "patching, reporting, rollback and cost. Verified against Microsoft Learn; practical, not lab-tested."
)
BADGE = "documentation verified against Microsoft Learn; practical, not lab-tested"
SRC_LABEL = "Microsoft sources"
TIME_NOTE = (
    "Time estimates are Tenant Recipes planning figures for an estate of roughly 50–500 servers that is already partly "
    "Arc-enabled, not Microsoft numbers. Most of the calendar time goes to agreeing criticality and redundancy pairs with "
    "application owners, not to Azure configuration."
)
CTA_FIRST = "Start with the wave model →"

INTRO = [
    "It is Sunday evening and the patch window for the important servers has just closed. Somebody asks the obvious "
    "question in the change channel: did both domain controllers in the branch office reboot at the same time? Nobody "
    "can answer quickly. The schedule lives in one tool, the list of which servers belong together lives in a "
    "spreadsheet, the cloud servers in AWS are patched by a different script, and the result of tonight's run is in a "
    "third place. Monday morning the other half of the clusters is due — and nobody is sure the first half is healthy.",
    "If that feels familiar, this guide is for you. It describes a common pattern for patching a mixed server estate "
    "over a weekend, ordered by how much it hurts when a server goes down:",
    "Friday: servers that matter little if they are down for a while. Saturday: production-related servers that are "
    "not business-critical. Sunday: business-critical servers plus the first half (side A) of every redundant pair — "
    "one node of each cluster, one domain controller of each pair, one member of each load-balanced pair. Monday: the "
    "other half (side B), and only after Sunday's side A is verified healthy.",
    "The pattern is not new. What makes it work at scale is that the decisions are written down as data — tags on each "
    "server — and that Azure enforces them: Azure Arc brings every machine into the same control plane regardless of "
    "where it runs, Azure Policy keeps the tags honest, Azure Update Manager runs one maintenance configuration per "
    "wave, pre-events refuse to start Monday when Sunday failed, and one Azure Resource Graph view shows every server, "
    "its wave, its last assessment, its pending updates and its last run result. That single view is the point: an "
    "overview you can show to an application owner or an auditor without opening four tools.",
    "This is a technical companion to two pillar guides. The Azure Arc onboarding guide covers the landing zone, RBAC, "
    "network and agent security in depth; the Azure Update Manager guide covers classifications, reboot policy, "
    "window timelines and troubleshooting. Here we only add what the wave model needs and link to the rest.",
]

NAMING = (
    "Scope: Windows Server and Linux machines outside Azure connected through Azure Arc, plus Azure VMs that should "
    "follow the same waves. Windows 10/11 clients, scale sets and AKS nodes are out of scope for Update Manager. "
    "Tag names, wave names and offsets in this guide are our suggestions, not Microsoft terms. Tenant Recipes is not "
    "affiliated with Microsoft. The opening scenario is a generic illustration, not a case study."
)

NOTICE = {
    "title": "Evidence boundary",
    "text": (
        "Service behaviour, limits, timelines and pricing rules are taken from the Microsoft Learn articles linked under "
        "each step. The wave model, tag names, Azure Policy rule and Resource Graph queries are Tenant Recipes' "
        "practical design built on those documented capabilities; we have not run them in a lab. Steps are marked "
        "'official' when they restate Microsoft documentation and 'practical' when they are our design. Run every "
        "query and policy in a test subscription first. Anything we could not confirm is listed under "
        "'This is not verified'."
    ),
}

HISTORY = [
    ("2026-11-11", "Draft technical guide: weekend wave model for Arc-enabled servers with Azure Update Manager; documentation verified against Microsoft Learn, practical, not lab-tested."),
]


def S(*keys):
    return [L[k] for k in keys]


AUM = "https://learn.microsoft.com/en-us/azure/update-manager/"
ARC = "https://learn.microsoft.com/en-us/azure/azure-arc/servers/"
L = {
    # Azure Update Manager
    "aum_overview": ("Microsoft Learn: Azure Update Manager overview", AUM + "overview"),
    "aum_faq": ("Microsoft Learn: Azure Update Manager FAQ (pricing, when an Arc server counts as managed)", AUM + "update-manager-faq"),
    "aum_price": ("Azure Update Manager pricing", "https://azure.microsoft.com/pricing/details/azure-update-management-center/"),
    "aum_sched": ("Microsoft Learn: Schedule recurring updates (limits, maintenance window timeline)", AUM + "scheduled-patching"),
    "aum_dyn": ("Microsoft Learn: Overview of dynamic scoping", AUM + "dynamic-scope-overview"),
    "aum_dyn_manage": ("Microsoft Learn: Manage a dynamic scope", AUM + "manage-dynamic-scoping"),
    "aum_pa": ("Microsoft Learn: Automate periodic assessment at scale by using Azure Policy", AUM + "periodic-assessment-at-scale"),
    "aum_policy": ("Microsoft Learn: Enable periodic assessment and scheduled patching using a policy", AUM + "tutorial-assessment-deployment-using-policy"),
    "aum_arc_api": ("Microsoft Learn: Manage Azure Arc-enabled servers programmatically", AUM + "manage-arc-enabled-servers-programmatically"),
    "aum_prepost": ("Microsoft Learn: About pre and post events", AUM + "pre-post-scripts-overview"),
    "aum_prepost_manage": ("Microsoft Learn: Manage pre and post events and cancel a schedule run", AUM + "manage-pre-post-events"),
    "aum_webhook": ("Microsoft Learn: Tutorial — pre and post events with webhooks and Automation runbooks", AUM + "tutorial-webhooks-using-runbooks"),
    "aum_logs": ("Microsoft Learn: Query Update Manager logs in Azure Resource Graph", AUM + "query-logs"),
    "aum_queries": ("Microsoft Learn: Sample Azure Resource Graph queries for Update Manager", AUM + "sample-query-logs"),
    "aum_wb": ("Microsoft Learn: Azure Update Manager workbooks", AUM + "workbooks"),
    "aum_alerts": ("Microsoft Learn: Create alerts in Azure Update Manager (preview)", AUM + "manage-alerts"),
    "aum_deploy": ("Microsoft Learn: Deploy updates now (one-time updates)", AUM + "deploy-updates"),
    "aum_ts": ("Microsoft Learn: Troubleshoot known issues with Azure Update Manager", AUM + "troubleshoot"),
    "rest_cancel": ("Microsoft Learn: Apply Updates — Create Or Update Or Cancel (REST)", "https://learn.microsoft.com/en-us/rest/api/maintenance/apply-updates/create-or-update-or-cancel"),
    "mc": ("Microsoft Learn: Maintenance Configurations for Azure virtual machines", "https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-configurations"),
    "arm_mc": ("Microsoft Learn: Microsoft.Maintenance/maintenanceConfigurations (Bicep/ARM)", "https://learn.microsoft.com/en-us/azure/templates/microsoft.maintenance/maintenanceconfigurations"),
    "cli_assign": ("Microsoft Learn: az maintenance assignment (Azure CLI)", "https://learn.microsoft.com/en-us/cli/azure/maintenance/assignment"),
    # Azure Arc
    "arc_plan": ("Microsoft Learn: Plan and deploy Azure Arc-enabled servers at scale", ARC + "plan-at-scale-deployment"),
    "arc_sp": ("Microsoft Learn: Connect hybrid machines to Azure at scale with a service principal", ARC + "onboard-service-principal"),
    "arc_options": ("Microsoft Learn: Azure Connected Machine agent deployment options", ARC + "deployment-options"),
    "arc_identity": ("Microsoft Learn: Identity and authorization for Azure Arc-enabled servers", ARC + "security-identity-authorization"),
    "arc_ext": ("Microsoft Learn: Extensions security — allowlists, blocklists and monitor mode", ARC + "security-extensions"),
    "arc_arg": ("Microsoft Learn: Azure Resource Graph sample queries for Arc-enabled servers", ARC + "resource-graph-samples"),
    "arc_vmware": ("Microsoft Learn: Install Arc agent at scale for your VMware VMs", "https://learn.microsoft.com/en-us/azure/azure-arc/vmware-vsphere/enable-guest-management-at-scale"),
    "arc_mcc": ("Microsoft Learn: What is Multicloud connector enabled by Azure Arc? (AWS, GCP preview)", "https://learn.microsoft.com/en-us/azure/azure-arc/multicloud-connector/overview"),
    "arc_wsm": ("Microsoft Learn: Windows Server Management enabled by Azure Arc", ARC + "windows-server-management-overview"),
    "caf_org": ("Microsoft Learn (CAF): Resource organization for Arc-enabled servers", "https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/hybrid/arc-enabled-servers/eslz-resource-organization"),
    # Azure Policy / tags / ARG
    "tag_pol": ("Microsoft Learn: Policy definitions for tagging resources", "https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-policies"),
    "pol_struct": ("Microsoft Learn: Azure Policy definition structure (policy rule, conditions)", "https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure-policy-rule"),
    "pol_effects": ("Microsoft Learn: Azure Policy effects (deny, audit, modify)", "https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-basics"),
    "arg_overview": ("Microsoft Learn: Azure Resource Graph overview", "https://learn.microsoft.com/en-us/azure/governance/resource-graph/overview"),
    "wb": ("Microsoft Learn: Azure Workbooks overview", "https://learn.microsoft.com/en-us/azure/azure-monitor/visualize/workbooks-overview"),
}

BOX_WHY = [
    "It encodes how people already think about risk. Owners understand 'this can be down Friday night' and 'this one "
    "is half of a pair' far better than ring names. Putting that judgement into tags makes it reviewable and keeps it "
    "out of someone's head.",
    "It never takes both halves of a redundant service down at once — by design and by check. Side A and side B live "
    "in different waves, a Resource Graph query flags any pair that drifts into the same wave, and Monday's pre-event "
    "cancels the run if Sunday's side A did not come back healthy.",
    "It gives one overview for every platform. Azure Arc projects on-premises, VMware, AWS and GCP machines as Azure "
    "resources, so a single Resource Graph query can show wave, last assessment, pending updates and last result for "
    "the whole estate.",
    "It is cheap to change. Moving a server to another wave is a tag change that dynamic scopes pick up at the next "
    "run — no schedule edits, no re-deployments.",
]
BOX_ALT = [
    "Choose the simpler ring model in the Update Manager pillar guide (Pilot / Test / Prod-A / Prod-B) when you have "
    "few redundant pairs or when weekend change windows are not available; the redundancy tags still apply.",
    "Keep Configuration Manager or WSUS-driven scheduling when most servers are on-premises, already patched well by "
    "that tooling, and you have no plan to use other Arc services. Arc + Update Manager carries a per-server charge for "
    "many Arc machines (see the cost step), and running two orchestrators is worse than either one.",
    "Use workload-native orchestration for clusters that patch themselves node by node (for example Cluster-Aware "
    "Updating for Windows failover clusters, or a Kubernetes distribution's own upgrade tooling). Then the wave model "
    "schedules the cluster as a unit and the cluster tooling handles node order — but do not let both do it.",
    "For Azure VMs where you do not need a fixed weekend window, Microsoft's automatic VM guest patching or "
    "hotpatching may cause less disruption than any wave calendar.",
    "If a wave needs strict ordering inside it (database before application before web front end), a single "
    "maintenance configuration is the wrong tool: Microsoft documents that a configuration starts updates on all "
    "associated machines at the same time. Split it into consecutive configurations or orchestrate from a runbook.",
]
BOX_UNVERIFIED = [
    "The wave model itself. It is a common customer pattern described here as a design, not a Microsoft "
    "recommendation and not something Tenant Recipes has run in a lab.",
    "Exact Resource Graph field names and status values in our queries. They follow Microsoft's published sample "
    "queries (`patchassessmentresources`, `patchinstallationresources`, `maintenanceresources`), but status strings "
    "such as `Succeeded` or `CompletedWithWarnings` and the `maintenanceRunId` property should be checked against "
    "the output in your own tenant before a health gate depends on them.",
    "Deny policies at onboarding. Arc machines are ordinary Azure Resource Manager resources, so a 'Require a tag' "
    "deny policy should block onboarding scripts that omit the tags. We have not confirmed how each onboarding path "
    "(portal script, VMware guest management, multicloud connector) reports such a denial; pilot with an Audit effect "
    "first.",
    "Tag propagation for the multicloud connector. Learn says you can apply Azure tags and policies to represented "
    "AWS/GCP resources; whether tags set on the inventory resource flow to the resulting Arc machine resource is not "
    "documented in the articles we checked. Tag the Arc machine resources directly.",
    "GCP onboarding through the multicloud connector is marked preview on Microsoft Learn; the standard agent "
    "onboarding script works on GCP VMs without it.",
    "Pricing amounts. We cite only Microsoft's rules for when an Arc server is charged; the current per-server price "
    "must be read on Microsoft's pricing page for your region and currency.",
]

EDITORIAL_BOXES = [
    {"kind": "why", "title": "Why we recommend this", "items": BOX_WHY},
    {"kind": "alt", "title": "When you should choose something else", "items": BOX_ALT},
    {"kind": "unverified", "title": "This is not verified", "items": BOX_UNVERIFIED},
]

PROBLEM = {
    "title": "The problem: patch schedules that nobody can see in one place",
    "blocks": [
        ("Why weekend waves go wrong",
         ["The calendar is rarely the problem. The problems are around it: a server nobody classified ends up in the "
          "wrong wave, both nodes of a cluster are in the same window because someone copied a tag, a cloud VM is "
          "patched by a different tool, and the Monday wave starts by itself even though Sunday's run left side A "
          "broken.",
          "Every one of those failures is invisible until it hurts, because the information lives in different places. "
          "The fix is to make the classification data, enforce it, and look at it in one view."]),
        ("The wave model at a glance",
         ["Friday — wave `fri`: low impact if down (test, internal tools, single non-critical services).",
          "Saturday — wave `sat`: production-related but not business-critical.",
          "Sunday — wave `sun`: business-critical servers that are not redundant, plus side A of every redundant pair.",
          "Monday — wave `mon`: side B of every redundant pair, gated on Sunday side A being healthy.",
          "Out of band — wave `oob`: emergency or excluded machines, patched only on explicit decision (see phase 7)."]),
        ("Why we recommend this", BOX_WHY),
        ("When you should choose something else", BOX_ALT),
        ("This is not verified", BOX_UNVERIFIED),
    ],
    "src": S("aum_overview", "aum_dyn", "aum_prepost", "arc_plan"),
}

ARG_OVERVIEW = r"""// Overview: every Arc server and Azure VM with wave, owner, last assessment, pending updates and last run
let machines = resources
| where type in~ ("microsoft.hybridcompute/machines", "microsoft.compute/virtualmachines")
| extend machineId = tolower(id),
         wave = tostring(tags["patch-wave"]), criticality = tostring(tags["criticality"]),
         sensitivity = tostring(tags["sensitivity"]), rgroup = tostring(tags["redundancy-group"]),
         side = tostring(tags["redundancy-side"]), owner = tostring(tags["owner"]),
         arcStatus = tostring(properties.status)
| project machineId, name, type, location, wave, criticality, sensitivity, rgroup, side, owner, arcStatus;
let assess = patchassessmentresources
| where type !has "softwarepatches"
| extend machineId = tolower(tostring(split(id, "/patchassessmentresults")[0]))
| extend lastAssessment = todatetime(properties.lastModifiedDateTime),
         critical = toint(properties.availablePatchCountByClassification.critical),
         security = toint(properties.availablePatchCountByClassification.security),
         other = toint(properties.availablePatchCountByClassification.other)
| project machineId, lastAssessment, critical, security, other;
let runs = patchinstallationresources
| where type !has "softwarepatches"
| extend machineId = tolower(tostring(split(id, "/patchinstallationresults")[0]))
| extend lastRun = todatetime(properties.lastModifiedDateTime), lastRunStatus = tostring(properties.status),
         failed = toint(properties.failedPatchCount), pending = toint(properties.pendingPatchCount)
| summarize arg_max(lastRun, lastRunStatus, failed, pending) by machineId;
machines
| join kind=leftouter assess on machineId
| join kind=leftouter runs on machineId
| project name, wave, criticality, sensitivity, rgroup, side, owner, arcStatus, location,
          lastAssessment, critical, security, other, lastRun, lastRunStatus, failed, pending
| order by wave asc, rgroup asc, side asc"""

ARG_PAIRS = r"""// Flag redundancy groups whose members share a wave, or whose A/B sides are missing or duplicated
resources
| where type in~ ("microsoft.hybridcompute/machines", "microsoft.compute/virtualmachines")
| extend rgroup = tostring(tags["redundancy-group"]), side = tostring(tags["redundancy-side"]),
         wave = tostring(tags["patch-wave"])
| where isnotempty(rgroup)
| summarize members = count(), waves = make_set(wave), sides = make_set(side),
            waveCount = dcount(wave), aInMon = countif(side == "A" and wave != "sun"),
            bInSun = countif(side == "B" and wave != "mon")
            by rgroup
| extend problem = case(
    waveCount < 2, "All members share one wave",
    array_length(sides) < 2, "Only one side tagged",
    aInMon > 0 or bInSun > 0, "Side/wave mismatch (A must be sun, B must be mon)",
    "")
| where isnotempty(problem)
| order by rgroup asc"""

ARG_GATE = r"""// Monday pre-event gate: did every Sunday side-A machine finish its latest run successfully, and is it connected?
let sideA = resources
| where type in~ ("microsoft.hybridcompute/machines", "microsoft.compute/virtualmachines")
| where tostring(tags["patch-wave"]) == "sun" and tostring(tags["redundancy-side"]) == "A"
| project machineId = tolower(id), name, arcStatus = tostring(properties.status);
let lastRun = patchinstallationresources
| where type !has "softwarepatches"
| extend machineId = tolower(tostring(split(id, "/patchinstallationresults")[0]))
| extend lastRun = todatetime(properties.lastModifiedDateTime), status = tostring(properties.status)
| where lastRun > ago(36h)
| summarize arg_max(lastRun, status) by machineId;
sideA
| join kind=leftouter lastRun on machineId
| where isempty(status) or status !in ("Succeeded") or (arcStatus != "" and arcStatus != "Connected")
| project name, arcStatus, lastRun, status"""

POLICY_WAVE = r"""{
  "mode": "Indexed",
  "policyRule": {
    "if": {
      "allOf": [
        { "field": "type", "in": [ "Microsoft.HybridCompute/machines", "Microsoft.Compute/virtualMachines" ] },
        { "anyOf": [
          { "field": "tags['patch-wave']", "exists": "false" },
          { "field": "tags['patch-wave']", "notIn": [ "fri", "sat", "sun", "mon", "oob" ] },
          { "allOf": [
            { "field": "tags['redundancy-side']", "equals": "A" },
            { "field": "tags['patch-wave']", "notEquals": "sun" } ] },
          { "allOf": [
            { "field": "tags['redundancy-side']", "equals": "B" },
            { "field": "tags['patch-wave']", "notEquals": "mon" } ] }
        ] }
      ]
    },
    "then": { "effect": "[parameters('effect')]" }
  },
  "parameters": {
    "effect": { "type": "String", "allowedValues": [ "Audit", "Deny" ], "defaultValue": "Audit" }
  }
}"""

PHASES = [
 {
  "id": "model", "title": "Design the wave and tag model", "time": "2–5 days (mostly owner workshops)", "deep": True,
  "goal": "Every in-scope server has an agreed wave, criticality, sensitivity, owner and — if it is part of a redundant service — a redundancy group and side, documented before anything is onboarded.",
  "lead": "The tags are the whole system. Dynamic scopes select machines by tag, Azure Policy validates tags, and the overview and gates read tags. Get the vocabulary right once.",
  "steps": [
   {"t": "Fix a small tag vocabulary",
    "check": "A one-page tag standard lists names and allowed values: `patch-wave` (fri | sat | sun | mon | oob), `criticality` (low | medium | high | critical), `sensitivity` (e.g. public | internal | confidential | restricted), `redundancy-group` (free text, one value per service pair), `redundancy-side` (A | B), `owner` (team mailbox or group)",
    "do": ["Keep the names lowercase and hyphenated and the values short; dynamic scope tag filters and Resource Graph queries are easier to read and harder to mistype.",
           "Let `patch-wave` be the only tag the schedules read. `criticality` and `sensitivity` explain why a server is in that wave and drive reporting and change approval; they do not select machines on their own.",
           "Use `owner` for a team, not a person, so alerts survive staff changes.",
           "Record the rules that connect the tags: side A → `sun`, side B → `mon`; `criticality` = critical and no redundancy → `sun`; low → `fri`. These rules become the Azure Policy in phase 2."],
    "pit": ["Free-text wave values ('Sunday', 'sun', 'Sön') silently fall outside every dynamic scope. Allowed values must be enforced, not just documented."],
    "rec": [], "tools": [], "src": S("aum_dyn", "tag_pol", "caf_org"),
    "guides": ["azure-update-manager-enterprise-patching"],
    "marker": "practical"},
   {"t": "Classify servers with owners, not for them",
    "check": "Each application owner has confirmed wave, criticality, sensitivity and any redundancy pair for their servers, and the result is in a version-controlled file or CMDB",
    "do": ["Ask three questions per server: what happens if it is down for two hours on a Friday night; does production depend on it; is it one half of something redundant?",
           "Name redundancy groups after the service (`dc-site1`, `sql-ag-erp`, `web-lb-portal`) and assign exactly one A and one B for pairs. For groups larger than two, put roughly half on each side.",
           "Mark servers whose sensitivity requires extra approval (for example restricted data) so their change records can be prepared in advance for their wave.",
           "Store the classification as data (CSV or CMDB export) so tagging can be scripted and diffed."],
    "pit": ["Owners tend to call everything critical. If more than about a third of servers land in `sun`, the Sunday window will not fit; push back with the 'down for two hours' question.",
            "A 'redundant' pair that shares a storage array, a hypervisor host or a network path is not fully redundant. Note those shared dependencies; patching does not fix them."],
    "rec": [], "tools": [], "src": S("arc_plan", "caf_org"),
    "marker": "practical"},
   {"t": "Anchor the four waves to Patch Tuesday",
    "check": "Each wave has a recurrence, start time, duration and time zone written down, and a pilot or test step precedes Friday",
    "do": ["Update Manager supports monthly recurrences on the nth weekday plus an offset of −6 to +6 days. One example (our planning figures): Friday `Month Second Tuesday Offset3`, Saturday `Offset4`, Sunday `Offset5`, Monday `Offset6` — the weekend straight after Patch Tuesday.",
           "If you want a pilot week first, use the third Tuesday with the same offsets (Friday to Monday ten days after release) and point a pilot configuration at the Thursday after Patch Tuesday.",
           "Set the configuration `timeZone` to the zone the business thinks in (for example `W. Europe Standard Time`) so windows follow daylight saving.",
           "Guest-scope windows are between 1 hour 30 minutes and 3 hours 55 minutes. A wave that needs more time becomes two consecutive configurations (for example `sun-1` 18:00 and `sun-2` 22:00)."],
    "pit": ["A window that is too short leaves updates skipped with a maintenance-window-exceeded state. Size Sunday on the baseline backlog, not on an average month."],
    "rec": [], "tools": [], "src": S("aum_sched", "arm_mc", "mc"),
    "guides": ["azure-update-manager-enterprise-patching"],
    "marker": "practical"},
  ]},

 {
  "id": "enforce", "title": "Enforce the tags with Azure Policy", "time": "1–2 days", "deep": False,
  "goal": "A server cannot sit in the estate with a missing or invalid wave, and side A/side B cannot drift into the wrong wave without being flagged (Audit) or blocked (Deny).",
  "steps": [
   {"t": "Require the tags with built-in policies",
    "check": "Built-in 'Require a tag on resources' assignments exist for `patch-wave`, `criticality` and `owner` on the Arc landing-zone scope; compliance is reviewed weekly",
    "do": ["Assign the built-in definition Require a tag on resources (deny) once per mandatory tag, scoped to the management group or subscription that holds Arc machines.",
           "Use Inherit a tag from the resource group if missing (modify, with remediation) for tags that are genuinely per resource group, such as `owner` when each team has its own group.",
           "Start in a pilot scope; a deny assignment on the production scope makes onboarding scripts without tags fail by design."],
    "pit": ["Built-in 'Require a tag' checks existence, not the allowed values. Pair it with the custom rule below."],
    "rec": [], "tools": [], "src": S("tag_pol", "pol_effects"),
    "marker": "official"},
   {"t": "Add a custom rule for allowed waves and the A/B rule",
    "code": [("Custom Azure Policy: allowed waves and the A/B rule", POLICY_WAVE)],
    "check": "A custom policy (Audit first, Deny later) flags any Arc server or Azure VM whose `patch-wave` is outside the allowed list, or whose `redundancy-side` contradicts its wave",
    "do": ["Create the policy definition below (mode `Indexed`), assign it with `effect` = `Audit`, and switch to `Deny` once compliance is clean.",
           "The rule allows `oob` for excluded machines; review that list every cycle.",
           "Custom definition (practical, adapt; not lab-tested) is in the code block below."],
    "pit": ["A Deny effect blocks tag changes too. An operator moving a side-A node to `mon` during an incident must also change `redundancy-side`; document that in the runbook.",
            "Policy cannot compare two resources, so it cannot see that both members of a pair are side A. That is what the Resource Graph pair check in phase 4 is for."],
    "rec": [], "tools": [], "src": S("pol_struct", "pol_effects", "tag_pol"),
    "marker": "practical"},
   {"t": "Enforce periodic assessment on the same scope",
    "check": "The built-in periodic-assessment policies for Azure Arc-enabled servers (and Azure VMs) are assigned with remediation, separately for Windows and Linux",
    "do": ["Assign Configure periodic checking for missing system updates on Azure Arc-enabled servers (and the Azure VM equivalent) per OS type and run a remediation task.",
           "Periodic assessment runs every 24 hours and feeds the overview in phase 4 — without it the 'pending updates' column is empty."],
    "pit": ["Microsoft's troubleshooting guide names a missing `Microsoft.Compute` registration as a cause of Arc machines producing no periodic assessment data — register it even in Arc-only subscriptions."],
    "rec": [], "tools": [], "src": S("aum_pa", "aum_policy", "aum_ts"),
    "marker": "official"},
  ]},

 {
  "id": "onboard", "title": "Arc-enable servers on every platform into a governed landing zone", "time": "1–10 days depending on estate", "deep": False,
  "goal": "Every non-Azure server shows as Connected in Azure Arc, in the intended resource group and region, already carrying its tags, onboarded with a least-privilege identity.",
  "lead": "The full design — landing zone, RBAC, network patterns, agent lockdown, offboarding — is in the Arc onboarding guide. This phase lists only what the wave model needs.",
  "steps": [
   {"t": "Prepare one governed landing zone for Arc machines",
    "check": "A dedicated subscription or resource groups per site/platform exist with resource providers registered, the policies from phase 2 assigned, and an extension allowlist decided",
    "do": ["Group Arc machines by management boundary (for example `rg-arc-onprem-sto`, `rg-arc-aws-eu`), not by wave — waves are tags so a server can change wave without moving.",
           "Register `Microsoft.HybridCompute`, `Microsoft.GuestConfiguration`, `Microsoft.HybridConnectivity` and `Microsoft.Compute` before onboarding.",
           "Decide the agent's local extension allowlist so only the extensions you need (Update Manager's patch extensions plus your monitoring and security agents) can be installed."],
    "pit": ["Moving an Arc machine to another resource group or subscription drops its schedule assignment; Microsoft documents re-creating it after a move. Get the resource-group design right before onboarding."],
    "rec": [], "tools": [], "src": S("caf_org", "arc_plan", "arc_ext", "aum_ts"),
    "guides": ["azure-arc-onboarding-enterprise-scale"],
    "marker": "official"},
   {"t": "Use a least-privilege onboarding identity",
    "check": "A service principal with only the Azure Connected Machine Onboarding role, scoped to the target resource groups, is used for onboarding; its secret lives in a vault and has an expiry",
    "do": ["Create the service principal from Azure Arc > Service principals or with PowerShell/CLI and assign Azure Connected Machine Onboarding at resource-group scope.",
           "Pass the tags at connect time so machines arrive classified: `azcmagent connect` accepts `--tags` alongside `--service-principal-id`, `--tenant-id`, `--subscription-id`, `--resource-group` and `--location`.",
           "Separate this identity from the identities that later run patching or pre/post events."],
    "pit": ["Microsoft's onboarding examples create secrets valid for one year; rotate and never leave the secret in a script share."],
    "rec": [], "tools": [], "src": S("arc_sp", "arc_identity"),
    "guides": ["azure-arc-onboarding-enterprise-scale"],
    "marker": "official"},
   {"t": "Pick the onboarding path per platform",
    "check": "Each platform has a named method and owner: on-premises physical/Hyper-V, VMware vSphere, AWS, GCP and other clouds",
    "do": ["On-premises Windows/Linux and other clouds: the generated onboarding script pushed with Configuration Manager, Group Policy or Ansible (all documented by Microsoft).",
           "VMware vSphere: with Arc-enabled VMware vSphere, install the agent from the vCenter inventory ('Arc agent with virtual hardware management') or with Microsoft's batch script; Learn lists VMware Tools as a prerequisite for that path and documents out-of-band onboarding plus linking to vCenter when VMware Tools are missing.",
           "AWS and GCP: the multicloud connector enabled by Azure Arc can auto-discover EC2 instances and GCP VMs and install the agent; GCP support is preview, and the GCP path requires Google Cloud VM Manager, which GCP charges for. The standard script remains an option.",
           "Do not install the Connected Machine agent on Azure VMs; tag them with the same model and let Update Manager manage them natively."],
    "pit": ["Different onboarding paths make it easy to forget tags on one platform. The deny/audit policies in phase 2 catch that; the overview in phase 4 shows it."],
    "rec": [], "tools": [], "src": S("arc_options", "arc_vmware", "arc_mcc", "arc_plan"),
    "marker": "official"},
  ]},

 {
  "id": "overview", "title": "Build the one overview: Resource Graph and a workbook", "time": "1–2 days", "deep": True,
  "goal": "One query, pinned in a workbook, shows every server with wave, criticality, owner, redundancy pair, Arc status, last assessment, pending updates and last run result — plus an exception list of broken pairs.",
  "lead": "This is the 'overviewable' part. If it is not in this view, it is not in the model.",
  "steps": [
   {"t": "Create the estate overview query",
    "code": [("Resource Graph: estate overview", ARG_OVERVIEW)],
    "check": "The query returns one row per machine across all subscriptions in scope; machines with no assessment or no run are visible, not filtered out",
    "do": ["Update Manager stores its data in Azure Resource Graph: assessment results in `patchassessmentresources` (kept 7 days) and installation results in `patchinstallationresources` (kept 30 days).",
           "Join them to `resources` on the machine ID and project the tags. The query in the code block below is practical, based on Microsoft's sample queries; field names to be checked in your tenant.",
           "Sort by wave and redundancy group so an owner reads their pairs side by side."],
    "pit": ["Left outer joins are deliberate: a machine with an empty `lastAssessment` is an onboarding or connectivity failure, not a compliant machine.",
            "Because Resource Graph keeps installation results for 30 days, export the view monthly if you need history for audits."],
    "rec": [], "tools": [], "src": S("aum_logs", "aum_queries", "arg_overview"),
    "marker": "practical"},
   {"t": "Add the redundant-pair check",
    "code": [("Resource Graph: redundant-pair check", ARG_PAIRS)],
    "check": "A second query lists every redundancy group whose members share a wave, have only one side tagged, or have a side in the wrong wave; the list is empty before each weekend",
    "do": ["The query (practical, not lab-tested) is in the code block below.",
           "Run it on Thursday before each wave weekend and treat any row as a blocker for that pair."],
    "pit": ["The query only knows the pairs you tagged. A cluster without a `redundancy-group` tag is invisible to it — the classification in phase 1 is what makes it work."],
    "rec": [], "tools": [], "src": S("arg_overview", "arc_arg"),
    "marker": "practical"},
   {"t": "Publish both in a workbook",
    "check": "A shared workbook shows the overview, the pair check and per-wave totals; application owners have Reader access to it",
    "do": ["Start from the built-in Update Manager workbooks and add the two queries as grid visualisations with a wave parameter.",
           "Add per-wave tiles: machines in wave, assessed in last 24 h, with pending critical/security updates, last run failed.",
           "Grant readers only what they need; Reader on the scopes is enough to view Resource Graph results."],
    "pit": ["A dashboard average hides exceptions. Show counts of machines with no assessment and no successful run next to the percentages."],
    "rec": [], "tools": [], "src": S("aum_wb", "wb", "aum_logs"),
    "marker": "practical"},
  ]},

 {
  "id": "waves", "title": "Maintenance configurations per wave with dynamic scopes", "time": "1–2 days", "deep": False,
  "goal": "Four (or more) maintenance configurations, deployed as code, each selecting its machines only by `patch-wave` through subscription-level dynamic scopes.",
  "steps": [
   {"t": "Create one configuration per wave",
    "check": "`mc-wave-fri`, `mc-wave-sat`, `mc-wave-sun` (or `sun-1`/`sun-2`) and `mc-wave-mon` exist with scope `InGuestPatch`, the agreed recurrence, reboot setting and classifications, deployed from source control",
    "do": ["Use the Bicep or CLI patterns from the Update Manager pillar guide; only the recurrence, window and name change per wave.",
           "Reboot setting: `IfRequired` for all waves unless an owner explicitly reboots in their own window.",
           "Tag the configurations themselves with `patch-wave` and `owner` so they show up in the overview."],
    "pit": ["Microsoft's documented limits apply per wave: 3,000 resource associations per schedule and 1,000 per dynamic scope; split very large waves."],
    "rec": [], "tools": [], "src": S("arm_mc", "aum_sched", "mc"),
    "guides": ["azure-update-manager-enterprise-patching"],
    "marker": "official"},
   {"t": "Attach machines with tag-driven dynamic scopes",
    "check": "Each configuration has a dynamic scope over all Arc and workload subscriptions filtering only on its `patch-wave` value; the scope preview matches the overview query for that wave",
    "do": ["Example: `az maintenance assignment create-or-update-subscription --maintenance-configuration-id <mc-wave-sun id> --name wave-sun --filter-tags \"{patch-wave:[sun]}\" --filter-tags-operator All --filter-os-types windows linux` (the CLI reference marks this command experimental).",
           "Scopes are evaluated at run time: changing a tag moves the server to another wave at the next run without touching the schedule.",
           "Do not mix static assignments into wave configurations; if a server needs special handling, give it the `oob` wave."],
    "pit": ["Edits to scopes or configurations must be done at least 15 minutes before the window (40 minutes when a pre-event is attached), or that run can be affected."],
    "rec": [], "tools": [], "src": S("aum_dyn", "aum_dyn_manage", "cli_assign"),
    "marker": "official"},
  ]},

 {
  "id": "gates", "title": "Health gates: Monday only starts when Sunday side A is healthy", "time": "2–3 days", "deep": True,
  "goal": "A pre-event on the Monday configuration checks Sunday's side-A results and the service health of each pair, and cancels Monday's run if anything failed.",
  "lead": "Update Manager never cancels a run by itself. The gate is your code, triggered by a documented event, calling a documented cancellation API.",
  "steps": [
   {"t": "Wire pre and post events",
    "check": "`mc-wave-sun` and `mc-wave-mon` have Event Grid subscriptions for `Microsoft.Maintenance.PreMaintenanceEvent` and `Microsoft.Maintenance.PostMaintenanceEvent`, delivered to a runbook webhook or Azure Function with a managed identity",
    "do": ["Follow Microsoft's tutorial for pre/post events with webhooks and Automation runbooks; give the identity Reader on the machine scopes (for Resource Graph) and the rights needed to cancel runs on the configuration.",
           "Sunday post-event: run service checks for every side-A machine (for example the application's own health endpoint, cluster node state, domain controller replication status) and write the result somewhere the Monday gate can read it.",
           "Make handlers idempotent: Event Grid delivers at least once."],
    "pit": ["The schedule's success covers update installation only, not the pre/post events. Monitor the handler jobs separately."],
    "rec": [], "tools": [], "src": S("aum_prepost", "aum_webhook", "aum_prepost_manage"),
    "marker": "official"},
   {"t": "Implement the Monday gate",
    "code": [("Resource Graph: Monday gate", ARG_GATE)],
    "check": "Monday's pre-event runs the gate query plus Sunday's recorded service checks, and calls the cancellation API when any side-A machine failed, is disconnected or has no result",
    "do": ["Run the gate query in the code block below (practical; confirm status values in your tenant).",
           "If the query returns any rows, or Sunday's post-event recorded a failed service check, cancel the Monday run with REST Apply Updates Create Or Update Or Cancel, `New-AzApplyUpdate` or `az maintenance applyupdate`, and notify the owners.",
           "Respect the timeline: pre-events are triggered at least 30 minutes before the window, all pre-events must finish within 20 minutes, and cancellation must be called at least 10 minutes before start."],
    "pit": ["Cancelling stops that run only, not the schedule. Next month the gate runs again — make sure Sunday is fixed and the pair is re-checked.",
            "A gate that fails open (handler error, missing permissions) lets Monday start. Treat a handler error as 'cancel'."],
    "rec": [], "tools": [], "src": S("aum_prepost", "aum_prepost_manage", "rest_cancel", "aum_queries"),
    "marker": "practical"},
   {"t": "Add lighter gates for Saturday and Sunday",
    "check": "Saturday and Sunday pre-events check that the previous wave has no failed runs above an agreed threshold before starting",
    "do": ["Reuse the gate logic with a threshold rather than zero tolerance, for example: cancel Sunday if more than a set number of Saturday machines failed.",
           "Always run the pair check from phase 4 in the Sunday pre-event; cancel if any pair has both sides in `sun`."],
    "pit": ["Too strict gates cancel every weekend and people start bypassing them. Agree thresholds with the owners and review after each cycle."],
    "rec": [], "tools": [], "src": S("aum_prepost", "aum_prepost_manage"),
    "marker": "practical"},
  ]},

 {
  "id": "operate", "title": "Emergency patching, reporting, rollback and cost", "time": "1–2 days, then monthly", "deep": False,
  "goal": "A documented out-of-band path, a monthly report per wave, a rehearsed rollback and a cost line for Arc servers based on Microsoft's pricing rules.",
  "steps": [
   {"t": "Patch out of band without breaking the pair rule",
    "check": "An emergency runbook exists: one-time updates on side A and non-redundant servers first, verification, then side B — never both sides in one action",
    "do": ["Use one-time updates (Install one-time updates / on-demand install for Arc servers) with a specific KB or package include list.",
           "Compress the waves in time, do not skip them: the order Friday → Saturday → Sunday/A → Monday/B stays, only the gaps shrink.",
           "Run the pair query and the gate query manually between the halves.",
           "Verify with an independent vulnerability scanner after the run."],
    "pit": ["One-time updates ignore the calendar by design. Gate them with the same change approval as scheduled runs."],
    "rec": [], "tools": [], "src": S("aum_deploy", "aum_arc_api"),
    "guides": ["azure-update-manager-enterprise-patching"],
    "marker": "practical"},
   {"t": "Report per wave and alert on exceptions",
    "check": "After each weekend a report shows per wave: machines in scope, succeeded, failed, not run, pending critical/security; alerts go to the `owner` team",
    "do": ["Export the overview query after Monday's run to storage or your CMDB; Resource Graph keeps installation results for 30 days.",
           "Create Update Manager alert rules (preview) from Resource Graph queries for failed runs and missing assessments, routed to action groups per owner.",
           "Track the pair-check result over time; a non-empty list on Thursday is a process problem, not a patch problem."],
    "pit": ["Alert rules (preview) are not available in Azure US Government or Azure operated by 21Vianet; use scheduled queries there."],
    "rec": [], "tools": [], "src": S("aum_alerts", "aum_logs", "aum_wb"),
    "marker": "official"},
   {"t": "Roll back: stop the next wave first",
    "check": "For a bad update the team can, in order: cancel the next wave, exclude the KB/package in later waves, uninstall or restore on affected machines, verify",
    "do": ["Cancel the next wave from its pre-event or the portal (History > by maintenance run ID > Cancel schedule update, in the last 10 minutes before start).",
           "Add the KB to `kbNumbersToExclude` (or the package to `packageNameMasksToExclude`) on later wave configurations.",
           "On affected machines, uninstall with the operating system's own tooling or restore from the hypervisor/backup snapshot taken in the pre-event.",
           "Move a broken server to `oob` while it is investigated, so it does not get patched again by accident."],
    "pit": ["Restoring a domain controller or a clustered database node from a snapshot has its own supported procedures; follow the workload's restore guidance, not a generic VM revert."],
    "rec": [], "tools": [], "src": S("aum_prepost_manage", "aum_arc_api", "aum_ts"),
    "guides": ["azure-update-manager-enterprise-patching"],
    "marker": "practical"},
   {"t": "Budget Arc servers in Update Manager from Microsoft's rules",
    "check": "A cost line lists Arc servers that are charged and those that are not, using Microsoft's FAQ and pricing page",
    "do": ["Microsoft Learn: Update Manager is available at no extra charge for Azure VMs and for Arc-enabled Azure Local VMs created through an Arc resource bridge on Azure Local; other Arc-enabled servers are charged per server per month, prorated daily.",
           "An Arc server counts as managed (charged) on a day when it is Connected at any time that day and an update operation is triggered on it — on-demand or periodic assessment, or patching — or it is associated with a schedule. In the wave model every machine is associated with a schedule, so expect every connected Arc server to be charged unless an exemption applies.",
           "Not charged per Microsoft Learn: Arc servers enabled for Extended Security Updates through Arc; subscriptions with Defender for Servers Plan 2 (not through a security connector); Windows Server with active Software Assurance, Windows Server subscription licences or pay-as-you-go through Arc (Windows Server Management enabled by Azure Arc).",
           "Read the current per-server price on Microsoft's Azure Update Manager pricing page; we do not quote a figure."],
    "pit": ["Defender for Servers plans other than Plan 2 do not remove the charge, per the FAQ.",
            "Decommissioned but still connected Arc machines keep counting while associated with a wave. Offboard them."],
    "rec": [], "tools": [], "src": S("aum_faq", "aum_price", "arc_wsm"),
    "marker": "official"},
  ]},
]
