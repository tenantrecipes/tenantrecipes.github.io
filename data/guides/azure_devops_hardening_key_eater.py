"""Expert hardening guide. Documentation verified; not lab-tested."""
SLUG = 'azure-devops-hardening-key-eater'

TIER = 'pillar'

PUBLISHED = '2026-11-05'

VERIFIED = '2026-11-05'

UPDATED = '2026-11-05'

TITLE = 'Azure DevOps hardening after Key Eater: pipelines, identity'

SHORT = 'Azure DevOps hardening / Key Eater'

DESC = ('An expert Azure DevOps Services hardening playbook: Key Eater evidence limits, PAT controls, WIF, '
 'service-connection checks, job-token scope, agent isolation, KQL hunts and safe rollback.')

BADGE = 'Microsoft documentation verified; campaign observations attributed to Todyl'

SRC_LABEL = 'Checked primary sources'

TIME_NOTE = ('Time estimates are our planning figures per pilot project, not vendor promises; incident response and fleet '
 'rollout vary.')

CTA_FIRST = 'Start with scope and evidence →'

INTRO = ['Workload identity federation removes a stored deployment secret. It does not make the pipeline that can request '
 'the token trustworthy. This guide treats Azure DevOps as part of the production identity perimeter: editors, '
 'sessions, templates, resource administrators and agents all matter.',
 "Todyl's Key Eater investigation makes that distinction urgent, but the hardening below does not depend on "
 'accepting every campaign hypothesis. We separate attributed incident observations from Microsoft-documented '
 'control behavior and our proposed verification sequence.',
 'For experienced Azure DevOps, Entra and Azure administrators: eight phases, explicit permissions, read-only '
 'hunting examples, acceptance criteria and rollback. Use the printable checklist only after collecting evidence '
 'in your own environment.']

NAMING = ('Scope: Azure DevOps Services backed by Microsoft Entra ID; do not assume feature parity with Azure DevOps '
 'Server. Only assess environments you own or have written authorization for. Verified against the linked primary '
 'documentation on 5 November 2026; no tenant execution, lab testing or production implementation is claimed.')

NOTICE = {'title': 'Evidence boundary: report, documentation and proposed tests',
 'text': "Campaign claims are attributed to Todyl's evolving investigation, last updated 4 November 2026 when "
         'checked. Microsoft sources verify the controls, not this incident or our examples. Initial credential '
         'theft, AI involvement and the precise federation abuse mechanism remain unconfirmed. No exploit, '
         'automatic worm propagation or PAT compromise is asserted.'}

HISTORY = [('2026-11-05',
  'Published eight-phase Azure DevOps trust-boundary hardening and schema-reviewed KQL; no runtime tests '
  'claimed.')]

L = {'todyl': ('Todyl: Key Eater investigation (updated 4 November 2026)',
           'https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads'),
 'overview': ('Microsoft Learn: secure Azure Pipelines',
              'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops'),
 'connections': ('Microsoft Learn: service connections',
                 'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops'),
 'wif': ('Microsoft Learn: Azure Resource Manager service connections and conversion',
         'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops'),
 'checks': ('Microsoft Learn: approvals and checks',
            'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops'),
 'jobs': ('Microsoft Learn: job access tokens and repository protection',
          'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/access-tokens?view=azure-devops'),
 'pats': ('Microsoft Learn: manage PATs using policies',
          'https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/manage-pats-with-policies-for-administrators?view=azure-devops'),
 'audit': ('Microsoft Learn: Azure DevOps auditing (public preview)',
           'https://learn.microsoft.com/en-us/azure/devops/organizations/audit/azure-devops-auditing?view=azure-devops'),
 'ca': ('Microsoft Learn: Conditional Access policies on Azure DevOps',
        'https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/conditional-access-policies?view=azure-devops'),
 'workload': ('Microsoft Learn: Conditional Access for workload identities',
              'https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity'),
 'spschema': ('Microsoft Learn: AADServicePrincipalSignInLogs schema',
              'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs'),
 'adoschema': ('Microsoft Learn: AzureDevOpsAuditing schema',
               'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azuredevopsauditing')}

PHASES = [{'id': 'scope',
  'title': 'Scope the trust chain and preserve evidence',
  'goal': 'One owner can trace every production pipeline to its Azure identity, permissions and evidence sources.',
  'steps': [{'t': 'Separate the campaign evidence from the hardening decision',
             'check': 'The incident ticket distinguishes Todyl observations, unknowns and our defensive '
                      'recommendations',
             'do': ['Todyl reports activity beginning 1 November 2026 using pre-existing stolen app credentials, an '
                    'Azure DevOps federated workload identity and replayed Azure DevOps user sessions. This is vendor '
                    'incident reporting, not our telemetry or a Microsoft confirmation of this campaign.',
                    'Todyl says no Microsoft vulnerability is involved. Its latest investigation update describes a '
                    'human-directed operator with scripted tooling, not a self-propagating worm. It rates AI '
                    'assistance as low confidence and does not identify an AI model directing the activity.',
                    'The initial credential source is unknown. The latest update assesses the activity as unrelated to '
                    'Storm-0940 / ConnectWise Cloud Backup; older hypotheses remain lower on the same page. Do not '
                    'turn those earlier leads into attribution.',
                    'Open an incident process for suspicious evidence, not a breach declaration based only on a shared '
                    'hosting provider or user-agent string. The 199.19.77.84 indicator is a point-in-time lead from '
                    'Todyl, not a complete detection strategy.'],
             'pit': ['A report of a federated identity being used does not establish an OIDC protocol vulnerability, a '
                     'Microsoft platform compromise, or how the attacker acquired the token. Reported PAT use was '
                     'still under investigation.'],
             'src': [('Todyl: Key Eater investigation (updated 4 November 2026)',
                      'https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads')],
             'rec': [],
             'tools': []},
            {'t': 'Inventory identities, connections and authorities without collecting secrets',
             'check': 'The inventory records organization/project, connection ID, identity IDs, Azure scope, allowed '
                      'pipelines, checks, owner and exception expiry',
             'do': ['In each project open `Project settings > Service connections`. Record authentication type and '
                    'Usage history, pipeline authorization, administrators and the Azure app or managed identity '
                    'behind the connection. Keep identifiers, not secret values.',
                    'Trace production connections back to YAML repositories, template repositories, variable groups, '
                    'secure files, environments and agent pools. Record who can edit each resource or bypass checks; a '
                    'protected environment alone is not proof the deployment credential cannot be used elsewhere.',
                    'Ask the Azure identity/resource owner to record the complete role assignment scope and any Key '
                    'Vault data access. A narrow-looking connection name does not prove the identity has no other '
                    'grants. Separate dev/test and production identities in the remediation plan.'],
             'pit': ['Treat this inventory as sensitive architecture information; store it in the approved '
                     'change/incident system, not in a public issue.'],
             'src': [('Microsoft Learn: service connections',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops'),
                     ('Microsoft Learn: approvals and checks',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops'),
                     ('Microsoft Learn: secure Azure Pipelines',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops')],
             'rec': [],
             'tools': ['azure-devops-service-connection-trust-review']},
            {'t': 'Export what exists before retention or cleanup removes the trail',
             'check': 'Available audit exports and pipeline evidence are preserved with a time window and collection '
                      'gaps',
             'do': ['Azure DevOps Services auditing requires an Entra-backed organization and is currently public '
                    'preview. Microsoft documents auditing as off by default: check rather than assume it exists.',
                    'At `Organization settings > Policies` enable `Log Audit Events` if absent, then refresh and use '
                    '`Organization settings > Auditing`. Export the relevant available range as JSON or CSV before '
                    'remediation. Native audit retention is 90 days; use an audit stream or approved exports for '
                    'longer retention.',
                    'Preserve Entra service-principal and user sign-ins, pipeline run IDs/logs, connection usage, '
                    'repository revisions and relevant Azure/Key Vault/Storage diagnostics. Record missing logging and '
                    'earliest retained timestamps. Enabling logging now does not reconstruct past events.'],
             'pit': ['Azure DevOps audit logs do not record sign-in events or Entra group membership changes. '
                     'Correlate Entra evidence separately; an empty DevOps audit export is not an all-clear.'],
             'src': [('Microsoft Learn: Azure DevOps auditing (public preview)',
                      'https://learn.microsoft.com/en-us/azure/devops/organizations/audit/azure-devops-auditing?view=azure-devops'),
                     ('Todyl: Key Eater investigation (updated 4 November 2026)',
                      'https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads')],
             'rec': [],
             'tools': []}],
  'time': 'Half a day',
  'deep': True},
 {'id': 'users-pats',
  'title': 'Constrain human sessions and PAT exceptions',
  'goal': 'User access and automation tokens have separate, explicit controls.',
  'steps': [{'t': 'Target Azure DevOps itself in user Conditional Access',
             'check': 'Report-only evidence covers the intended users and Azure DevOps resource, with emergency access '
                      'validated',
             'do': ['Use a Conditional Access Administrator and the existing emergency-access change process. Target '
                    '`Azure DevOps` / `Microsoft Visual Studio Team Services`, resource ID '
                    '`499b84ac-1321-427f-aa17-267ca6975798`, not just Azure Resource Manager.',
                    'Microsoft documents that Azure DevOps sign-in no longer depends on the ARM audience since '
                    'September 2025. An ARM-only CA policy therefore does not cover DevOps sign-in.',
                    'Pilot appropriate MFA/authentication-strength and device/location policy requirements in '
                    'Report-only, check intended users and emergency exclusions, then enforce only after review. '
                    'Microsoft notes external authentication methods are not compatible with authentication strength; '
                    'use the supported MFA grant when applicable.'],
             'pit': ['This user policy does not make service principals perform MFA. Do not copy user-scoped controls '
                     'into a workload identity design and claim equivalent coverage.'],
             'src': [('Microsoft Learn: Conditional Access policies on Azure DevOps',
                      'https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/conditional-access-policies?view=azure-devops'),
                     ('Microsoft Learn: Conditional Access for workload identities',
                      'https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity')],
             'rec': [],
             'tools': []},
            {'t': 'Validate non-interactive IP fencing separately',
             'check': 'A sanctioned allowed-path and denied-path check has an owner and captured outcome',
             'do': ['A Project Collection Administrator can enable the organization policy `IP Conditional Access '
                    'policy validation on non-interactive flows`. This applies IP fencing to non-interactive flows '
                    'such as PAT REST API calls.',
                    'Before enforcement map developer VPNs, agent egress, IPv4 and IPv6 paths with the network owner. '
                    'Pilot from an approved allowed path and an approved disallowed path, recording results without '
                    'publishing tokens.',
                    'Do not promise that this switch adds device compliance or an MFA challenge to a PAT. It is an '
                    'IP-fencing control, not a substitute for retiring PATs.'],
             'pit': ['Different IP addresses at Entra sign-in and resource access can cause legitimate blocking with '
                     'split-tunnel VPNs. Restore only the affected pilot setting if the agreed recovery condition is '
                     'met.'],
             'src': [('Microsoft Learn: Conditional Access policies on Azure DevOps',
                      'https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/conditional-access-policies?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Restrict PAT creation, scope and lifespan; revoke compromised tokens explicitly',
             'check': 'Each remaining token has an owner, narrow scope and expiry, and incident tokens are revoked',
             'do': ['For tenant policies use Azure DevOps Administrator; organization PAT creation restrictions '
                    'require Project Collection Administrator. At `Organization settings > Microsoft Entra` restrict '
                    'global PAT creation, restrict full-scoped PAT creation and enforce a maximum lifespan for new '
                    'PATs.',
                    'At `Organization settings > Policies` consider `Restrict personal access token (PAT) creation`. '
                    'Document each allowlist and any packaging-only exception, its owner and its expiry. Choose the '
                    'maximum lifetime to fit your recovery capability; no universal day count makes tokens safe.',
                    'Keep automatic leaked-PAT revocation enabled. It covers PATs detected in public GitHub '
                    'repositories, not every possible leak location. Inventory and explicitly revoke/replace known '
                    'exposed existing tokens: creation/lifetime policies do not retroactively shorten all existing '
                    'PATs.'],
             'pit': ['An allowlist is a bypass of that policy, not an approval workflow. Do not leave a broad '
                     'service-account group permanently exempt.'],
             'src': [('Microsoft Learn: manage PATs using policies',
                      'https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/manage-pats-with-policies-for-administrators?view=azure-devops')],
             'rec': [],
             'tools': []}],
  'time': 'Half a day',
  'deep': True},
 {'id': 'service-connections',
  'title': 'Replace secrets without leaving the trust issuer unguarded',
  'goal': 'One pilot uses WIF with least privilege and explicit pipeline authorization.',
  'steps': [{'t': 'Build a narrow WIF pilot rather than a fleet-wide conversion',
             'check': 'A nonproduction pipeline uses a dedicated WIF connection and an explicitly recorded Azure '
                      'permission scope',
             'do': ['For Azure DevOps Services, create or convert an Azure Resource Manager connection using workload '
                    'identity federation with an app registration or user-assigned managed identity. Confirm every '
                    'task/extension supports WIF first.',
                    'The automatic app-registration path documented by Microsoft requires Azure subscription Owner. '
                    'Where standing Owner is inappropriate, have the identity and RBAC owners use the documented '
                    'manual setup rather than elevating every pipeline maintainer.',
                    'Choose a resource group where practical and assign only required roles. Use distinct '
                    'identities/connections for production and nonproduction. Leave `Grant access permission to all '
                    'pipelines` unselected; authorize the named pilot pipeline only.',
                    'Copy issuer, subject and audience from the actual connection/federated credential setup; do not '
                    'invent or reuse a blog literal. Current Microsoft documentation distinguishes issuers and '
                    'migration scope, so inspect your connection rather than assuming every tenant uses the same '
                    'issuer.'],
             'pit': ['WIF removes a stored secret, not the need to protect the issuing pipeline, its editors, its '
                     'session holders and its resource authorization. A broadly authorized federated connection can '
                     'still be abused.'],
             'src': [('Microsoft Learn: Azure Resource Manager service connections and conversion',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops'),
                     ('Microsoft Learn: service connections',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops'),
                     ('Microsoft Learn: secure Azure Pipelines',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Retire the old credential only after pilot evidence',
             'check': 'The production task path has a successful sanctioned verification and the unused old credential '
                      'has an approved removal decision',
             'do': ['Run a read-only verification or a change-approved nonproduction deployment with the intended '
                    'branch, identity and agent. Capture run ID, connection identity and expected target resource; a '
                    'connection Verify action alone is not proof that every pipeline task works.',
                    "Microsoft's in-place conversion tool applies to connections originally created by Azure DevOps "
                    'and used by one project; manually created and cross-project connections need a different plan. '
                    'The documented automatic conversion has a seven-day revert window.',
                    'After the migration owner validates all consumers, remove unused old credentials through change '
                    'control. Do not remove a shared app secret before discovering all its consumers, and do not '
                    'retain a known-compromised secret as a rollback option.'],
             'pit': ['If conversion fails, keep the rollout paused; investigate task WIF support and actual trust '
                     'values. Do not solve a failed authentication by granting subscription-wide Owner to the runtime '
                     'identity.'],
             'src': [('Microsoft Learn: Azure Resource Manager service connections and conversion',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops'),
                     ('Microsoft Learn: service connections',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Reduce who can create, administer and consume deployment connections',
             'check': 'Resource owners have reviewed connection Security and pipeline permissions with named backups',
             'do': ['Use the connection Security settings to review administrators and users, then review explicit '
                    'pipeline authorizations. Remove obsolete access only through the approved change process.',
                    'Keep resource administration separate from ordinary YAML contribution where possible. Review '
                    'project/organization administrators as effective override authorities, not just the listed '
                    'pipeline users.',
                    'Use Usage history to identify obsolete connections and investigate unexpected consumers. '
                    'Disabling an unused or suspicious connection is a controlled containment/change action; capture '
                    'dependencies and evidence first.'],
             'pit': ['A service connection has standing access to its target. WIF is not a replacement for Azure RBAC '
                     'review or connection lifecycle management.'],
             'src': [('Microsoft Learn: service connections',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops'),
                     ('Microsoft Learn: approvals and checks',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops')],
             'rec': [],
             'tools': []}],
  'time': 'Half a day',
  'deep': True},
 {'id': 'resource-checks',
  'title': 'Put production gates on the resource, not only in YAML',
  'goal': 'The production credential itself has branch control and independent approval.',
  'steps': [{'t': 'Protect the service connection with branch control',
             'check': 'A new run from an unapproved branch cannot consume the production connection',
             'do': ['On the production connection open `Approvals and checks`. Add Branch control and specify fully '
                    'qualified allowed branch names such as `refs/heads/main`; require branch protection and decide to '
                    'fail closed when protection status is unknown.',
                    'Check all linked pipeline resources, including templates and upstream pipeline artifacts. Branch '
                    'control evaluates linked resources, not merely the name of the repository containing the '
                    'top-level YAML.',
                    'Keep code review branch policies on pipeline and template repositories. Microsoft considers a '
                    'branch protected with at least one policy; configure your actual review requirements rather than '
                    'equating that minimum flag with rigorous review.'],
             'pit': ['A YAML condition that checks Build.SourceBranch is editable by a YAML contributor. It is not '
                     'equivalent to a resource-owner-managed check.'],
             'src': [('Microsoft Learn: approvals and checks',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops'),
                     ('Microsoft Learn: secure Azure Pipelines',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Require independent approval and constrain override rights',
             'check': 'Production consumption waits for a designated independent approver and bypass rights are '
                      'reviewed',
             'do': ['Add an Approvals check to the production service connection and, where useful, to its '
                    "environment. Disable approval of one's own runs and name a small operational approver group with "
                    'a backup.',
                    'Checks are not stored in YAML; resource administrators manage them. Resource administrator '
                    'permission can also bypass certain checks, so inventory those administrators and require a '
                    'recorded emergency process.',
                    'For centralized policy, add a Required template check on the connection and protect the template '
                    'repository. It requires the pipeline to extend the specified template; merely including a '
                    'convenient template is not the same control.'],
             'pit': ['When a group is an approver, one member is enough. A group does not automatically require every '
                     'member or two-person approval. Record what your control actually enforces.'],
             'src': [('Microsoft Learn: approvals and checks',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Prove both a permitted and a denied consumption path',
             'check': 'Run IDs show an approved run waiting/passing and a disallowed branch or unauthorized pipeline '
                      'blocked',
             'do': ['With written test authorization, use a harmless nonproduction target to validate the exact policy '
                    'arrangement before production. Queue a fresh run after checks are configured; existing run '
                    'behavior is not sufficient evidence.',
                    'Try an approved pipeline from the allowed branch, an unauthorized test pipeline and a disallowed '
                    'branch. Capture the check results and confirm blocked runs performed no target write. No '
                    'credential extraction or real adversary token replay is needed.',
                    'If a check does not start, verify stage conditions were met, the run started after the check was '
                    'added, and the stage actually consumes the protected resource.'],
             'pit': ['These are proposed acceptance tests, not tests Tenant Recipes has performed. Do not tick the '
                     'checklist until your own evidence exists.'],
             'src': [('Microsoft Learn: approvals and checks',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops'),
                     ('Microsoft Learn: service connections',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops')],
             'rec': [],
             'tools': []}],
  'time': 'Half a day',
  'deep': True},
 {'id': 'jobs-repositories',
  'title': 'Reduce job-token and repository blast radius',
  'goal': 'Project-scoped job identities and explicit repository access replace collection-wide assumptions.',
  'steps': [{'t': 'Enable project-scoped job authorization in a pilot',
             'check': 'The pilot succeeds with the project build identity and documented cross-project exceptions only',
             'do': ['At `Organization settings > Pipelines > Settings` review `Limit job authorization scope to '
                    'current project for non-release pipelines` and the separate setting for release pipelines. Pilot '
                    'at project level first if existing dependencies are unknown, then enforce at organization level '
                    'after review.',
                    'The non-release switch covers YAML and classic build pipelines; classic release pipelines have a '
                    'separate switch. Organization-enforced project scope cannot be relaxed by a project.',
                    'Job token permissions depend on both job authorization scope and build-service account '
                    'permissions. Review `{Project Name} Build Service ({Org Name})` rather than assuming the scope '
                    'toggle removes every explicit grant.'],
             'pit': ['Project scope is not a hard guarantee of zero cross-project access: explicit grants can permit '
                     'it. Review and document those grants.'],
             'src': [('Microsoft Learn: job access tokens and repository protection',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/access-tokens?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Protect repository access and repair narrow dependencies',
             'check': 'Only explicitly referenced and authorized Azure Repos repositories are used by the YAML job',
             'do': ['Enable `Protect access to repositories in YAML pipelines`. It reduces Azure Repos access to '
                    'repositories explicitly referenced by a checkout or uses statement in the consuming job.',
                    'For an approved cross-project repository, grant the project build identity only required project '
                    'visibility and repository Read. Reference the repository explicitly in YAML and authorize the '
                    'pipeline; do not turn off protection to repair a hidden script clone.',
                    'The project build identity is created after the first pipeline run. If it cannot be found in '
                    'permission search, verify that initialization and expand the identity search as Microsoft '
                    'documents.'],
             'pit': ['This switch governs Azure Repos access through the pipeline identity; it does not revoke a '
                     'separate PAT or SSH key placed in a script. Inventory those paths too.'],
             'src': [('Microsoft Learn: job access tokens and repository protection',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/access-tokens?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Keep fork validation away from deployment trust',
             'check': 'External PR validation has no production connection, secrets or privileged self-hosted pool',
             'do': ['For GitHub forks, do not enable `Make secrets available to builds of forks`. Consider manual fork '
                    'triggering after review; check the PR comment requirements for both internal and fork sources.',
                    'Use Microsoft-hosted agents for untrusted fork validation rather than letting external code run '
                    'inside a corporate self-hosted network. Separate validation and production deployment '
                    'pipelines/resources.',
                    'Apply branch policies and resource checks to pipeline changes, not just application code. A PR '
                    'that edits YAML or a template can change what executes under the deployment identity.'],
             'pit': ['A masked log is not a sandbox. Untrusted code must not receive a secret merely because the log '
                     'renderer tries to hide it.'],
             'src': [('Microsoft Learn: secure Azure Pipelines',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops')],
             'rec': [],
             'tools': []}],
  'time': 'Half a day',
  'deep': True},
 {'id': 'agents-secrets',
  'title': 'Contain agents and secondary credential exposure',
  'goal': 'Agent placement and secret access do not undo the identity hardening.',
  'steps': [{'t': 'Separate trusted deployment agents from untrusted builds',
             'check': 'Production pool permissions, runtime account and network paths are documented',
             'do': ['Prefer Microsoft-hosted agents when the task and network model permit. For required self-hosted '
                    'agents use low-privileged runtime accounts, dedicated project/sensitivity pools, restrictive '
                    'network rules and current agent software.',
                    'Do not run untrusted builds on a VM whose identity or network reach grants production data '
                    'access. Treat execution on that agent as a separate trust path even when the production '
                    'connection is protected.',
                    'Review Marketplace tasks and extensions: they execute code in the job. Retain an approved task '
                    'inventory and validate WIF support before credential migration.'],
             'pit': ['Do not promise Microsoft-hosted agents can reach your private endpoint. Private resource access '
                     'may require a deliberately isolated self-hosted or managed pool with approved network '
                     'connectivity.'],
             'src': [('Microsoft Learn: secure Azure Pipelines',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops'),
                     ('Microsoft Learn: Azure Resource Manager service connections and conversion',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Keep remaining secrets out of YAML and incident artifacts',
             'check': 'The pilot uses no embedded credential; unavoidable secrets have restricted access and rotation '
                      'ownership',
             'do': ['Use secretless authentication where possible. For remaining secrets use restricted secret '
                    'variables, variable groups or Key Vault-backed groups; minimize which pipelines and branches can '
                    'consume them.',
                    'Never echo secrets, place them in YAML or pass them in command-line arguments. Redaction does not '
                    'cover every transformation; structured JSON secrets are especially difficult to mask reliably.',
                    'Review logs and artifacts for accidental exposure under the approved incident process. If the '
                    'affected identity could read downstream credentials, scope and rotate those credentials too; '
                    'replacing only the entry secret is insufficient.'],
             'pit': ['A Key Vault token request is not evidence that a secret was read. Obtain vault diagnostic '
                     'evidence before asserting exfiltration, and record uncertainty if those logs were not enabled.'],
             'src': [('Microsoft Learn: secure Azure Pipelines',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops'),
                     ('Todyl: Key Eater investigation (updated 4 November 2026)',
                      'https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads')],
             'rec': [],
             'tools': []}],
  'time': 'Half a day',
  'deep': True},
 {'id': 'hunt',
  'title': 'Hunt across Entra and Azure DevOps without inventing telemetry',
  'goal': 'Queries provide triage leads, with source availability and interpretation recorded.',
  'steps': [{'t': 'Search service-principal sign-ins including failures',
             'check': 'Results are reviewed for app identity, credential type, resource and outcome; missing ingestion '
                      'is recorded',
             'do': ['Prerequisite: Entra service-principal sign-in diagnostic data must reach the queried Log '
                    'Analytics workspace, and the analyst needs query rights. Run the query below as a read-only '
                    'triage example; widen the lookback to retained history.',
                    '`AADServicePrincipalSignInLogs\n'
                    '| where TimeGenerated >= ago(7d)\n'
                    '| where IPAddress == "199.19.77.84"\n'
                    '| project TimeGenerated, AppId, ServicePrincipalId, ServicePrincipalName,\n'
                    '          IPAddress, ClientCredentialType, FederatedCredentialId,\n'
                    '          ResourceDisplayName, ResultType, ResultDescription, CorrelationId\n'
                    '| order by TimeGenerated asc`',
                    'The query intentionally retains failures and successes. Check ResultType and ResultDescription '
                    'against actual records; do not require a success before investigating leaked or expired '
                    'credential attempts. FederatedCredentialId can help identify the trust used, but does not by '
                    'itself explain how it was obtained.',
                    'An empty result means only that no matching records were returned from the data available to this '
                    'query. Also review user/non-interactive sign-ins for session-replay evidence; this '
                    'service-principal table is not their replacement.'],
             'pit': ['The KQL is documentation/schema-reviewed, not executed against a tenant or lab. Log query times '
                     'use UTC internally; preserve that timezone when correlating exports.'],
             'src': [('Todyl: Key Eater investigation (updated 4 November 2026)',
                      'https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads'),
                     ('Microsoft Learn: AADServicePrincipalSignInLogs schema',
                      'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs')],
             'rec': [],
             'tools': []},
            {'t': 'Correlate DevOps changes and executions separately',
             'check': 'Audit hits retain actor, organization, operation, IP and correlation ID for incident review',
             'do': ['Prerequisite: configure Azure DevOps audit collection/streaming into the workspace so '
                    'AzureDevOpsAuditing exists. Native portal auditing does not automatically create this table in '
                    'every workspace.',
                    '`AzureDevOpsAuditing\n'
                    '| where TimeGenerated >= ago(7d)\n'
                    '| where IpAddress == "199.19.77.84"\n'
                    '| project TimeGenerated, ScopeDisplayName, ProjectName, ActorUPN,\n'
                    '          ActorClientId, OperationName, AuthenticationMechanism,\n'
                    '          IpAddress, UserAgent, Details, CorrelationId\n'
                    '| order by TimeGenerated asc`',
                    'Follow actor IDs, connection IDs, pipeline run IDs and repository revisions in the original '
                    'records. Review token lifecycle changes, permissions, service-connection changes and suspicious '
                    'pipeline activity where those events are available.',
                    'Do not inner-join Entra and Azure DevOps solely on CorrelationId: the schemas expose their own '
                    'correlation fields but do not promise shared cross-product IDs. Start with identity, IP and '
                    'time-window correlation, then validate in source records.'],
             'pit': ['Use `IpAddress` in AzureDevOpsAuditing and `IPAddress` in AADServicePrincipalSignInLogs. Do not '
                     'invent event names or assume every token use is logged as a sign-in.'],
             'src': [('Microsoft Learn: Azure DevOps auditing (public preview)',
                      'https://learn.microsoft.com/en-us/azure/devops/organizations/audit/azure-devops-auditing?view=azure-devops'),
                     ('Microsoft Learn: AzureDevOpsAuditing schema',
                      'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/azuredevopsauditing'),
                     ('Microsoft Learn: AADServicePrincipalSignInLogs schema',
                      'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs')],
             'rec': [],
             'tools': []},
            {'t': 'Widen to behavior and validate before alerting',
             'check': 'A baselined candidate detection has exclusions, an owner and a documented false-positive review',
             'do': ['`AADServicePrincipalSignInLogs\n'
                    '| where TimeGenerated >= ago(7d)\n'
                    '| summarize Apps=dcount(AppId), AppIds=make_set(AppId, 100),\n'
                    '            Results=make_set(ResultType, 20),\n'
                    '            Resources=make_set(ResourceDisplayName, 50), Events=count()\n'
                    '    by IPAddress, bin(TimeGenerated, 30m)\n'
                    '| where Apps >= 3\n'
                    '| order by Events desc`',
                    'This is our candidate triage heuristic: three apps per source IP in a 30-minute bin. It is not a '
                    'Microsoft rule, not a validated Key Eater detection, and not proof of compromise. Shared NAT, '
                    'legitimate MSP automation and scanners can match.',
                    'Compare unfamiliar app/resource sequences and credential types with the baseline and authorized '
                    'deployment window. A request for ARM and then Key Vault is a lead, not proof of a Key Vault read.',
                    'Todyl identifies 199.19.77.84 as the confirmed operator address, advises against attributing the '
                    'whole ASN, and explicitly lists some Microsoft service addresses as non-attacker infrastructure. '
                    'Re-check its evolving report before operational blocking.'],
             'pit': ['Do not copy a hosting ASN block into production from a campaign article. Indicators change '
                     'and shared infrastructure creates collateral impact.'],
             'src': [('Todyl: Key Eater investigation (updated 4 November 2026)',
                      'https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads'),
                     ('Microsoft Learn: AADServicePrincipalSignInLogs schema',
                      'https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs')],
             'rec': [],
             'tools': []}],
  'time': 'Half a day',
  'deep': True},
 {'id': 'response-rollback',
  'title': 'Contain an incident, recover safely and hand over',
  'goal': 'Production adoption requires evidence, reversible changes and explicit residual risk.',
  'steps': [{'t': 'If evidence is suspicious, contain the whole credential chain',
             'check': 'An incident lead owns app, session, DevOps and downstream credential containment with preserved '
                      'evidence',
             'do': ["Use the organization's incident response process. Preserve available evidence, then have "
                    'authorized owners disable/restrict the affected identity and connection, remove compromised '
                    "trust/credentials and revoke affected users' sessions, PATs and SSH keys as applicable.",
                    'Scope every Azure/API/data permission of the affected identity and any MSP/customer access. '
                    'Rotate downstream credentials exposed through accessible vaults or downloaded documents based on '
                    'the investigation, and investigate developer/admin endpoints that held the original material.',
                    'Do not promise deleting a credential instantly invalidates every already-issued token. Monitor '
                    "resource access during containment and validate the target service's behavior. Customer/legal "
                    'notifications are incident-owner decisions, not automated steps in this guide.'],
             'pit': ['A WIF migration is preventive engineering, not proof that an active intruder has been removed. '
                     'Do not resume deployment solely because a new connection authenticates.'],
             'src': [('Todyl: Key Eater investigation (updated 4 November 2026)',
                      'https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads'),
                     ('Microsoft Learn: service connections',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/service-endpoints?view=azure-devops')],
             'rec': [],
             'tools': []},
            {'t': 'Apply workload Conditional Access only within its supported scope',
             'check': 'Policy coverage and unsupported identities are written down before anyone calls the tenant '
                      'protected',
             'do': ['For eligible single-tenant service principals registered in your tenant, a Conditional Access '
                    'Administrator can pilot a location-based workload policy in Report-only and inspect '
                    'service-principal sign-in CA results before enforcement.',
                    'Microsoft requires Workload Identities Premium licensing to create/modify such policies. Assign '
                    'the service principals directly as workload identities, not via a group containing them.',
                    'These policies do not cover managed identities, multitenant applications or third-party SaaS. A '
                    'user block policy and a named location alone do not solve these gaps; keep least privilege, '
                    'resource networking and pipeline governance in the design.'],
             'pit': ["Never interpret an unsupported identity's absence from a workload CA report as successful "
                     'enforcement. Report-only also does not block access.'],
             'src': [('Microsoft Learn: Conditional Access for workload identities',
                      'https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity')],
             'rec': [],
             'tools': []},
            {'t': 'Troubleshoot narrowly and define safe rollback',
             'check': 'Every failing dependency has a targeted repair or time-bound exception, not a blanket '
                      'permission reset',
             'do': ['WIF authentication failure: verify task support and the actual issuer/subject/audience and '
                    'identity selection. Authorization failure after successful authentication: review the precise '
                    'target operation and missing Azure role, not merely the connection name.',
                    'Cross-project checkout/feed failure after scoping: review the project build identity and explicit '
                    'resource authorization. A missing check: verify the resource is actually consumed and the run '
                    'started after configuration. A CA failure: inspect policy results and legitimate egress paths.',
                    'Record previous settings before each pilot. Roll back one project scope/check/policy change at a '
                    'time to the approved prior state if the service recovery criterion is met, with an owner and '
                    'expiry. For workload CA use Report-only or Off; for WIF automatic conversion use the supported '
                    'seven-day revert only if the old credential is safe.',
                    'Never re-enable a compromised identity or restore a stolen secret as routine rollback. Pause '
                    'deployment and issue a narrowly scoped clean identity through the incident process instead.'],
             'pit': ['Time-bound exceptions still create exposure. Document the compensating control and require '
                     're-validation before moving to the next project.'],
             'src': [('Microsoft Learn: Azure Resource Manager service connections and conversion',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/library/connect-to-azure?view=azure-devops'),
                     ('Microsoft Learn: job access tokens and repository protection',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/access-tokens?view=azure-devops'),
                     ('Microsoft Learn: approvals and checks',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops'),
                     ('Microsoft Learn: Conditional Access for workload identities',
                      'https://learn.microsoft.com/en-us/entra/identity/conditional-access/workload-identity')],
             'rec': [],
             'tools': []},
            {'t': 'Accept the hardening only with evidence and operational ownership',
             'check': 'Approved and denied paths, identity permissions, log coverage and rollback are signed off',
             'do': ['The handover includes a before/after permission inventory, connection and pipeline IDs, allowed '
                    'branches, independent approvers and bypass authorities, PAT exceptions, and agent pool/network '
                    'decisions.',
                    'Attach fresh authorized-run and denied-run evidence plus downstream resource verification. Attach '
                    'actual audit/sign-in results and a log-gap register; schema-reviewed example queries alone do not '
                    'satisfy acceptance.',
                    'Assign recurring reviews for stale connections/identities, new federated credentials, broad role '
                    'changes, PAT exceptions, template edits and agent maintenance. Link this guide into the broader '
                    'cloud hardening programme.'],
             'pit': ['Nothing on this page has been lab-tested or production-implemented by Tenant Recipes. '
                     'Documentation verification is not runtime validation.'],
             'src': [('Microsoft Learn: secure Azure Pipelines',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/security/overview?view=azure-devops'),
                     ('Microsoft Learn: Azure DevOps auditing (public preview)',
                      'https://learn.microsoft.com/en-us/azure/devops/organizations/audit/azure-devops-auditing?view=azure-devops'),
                     ('Microsoft Learn: approvals and checks',
                      'https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops')],
             'rec': [],
             'tools': [],
             'guides': ['cloud-hardening-adversary-emulation']}],
  'time': 'Half a day',
  'deep': True}]
