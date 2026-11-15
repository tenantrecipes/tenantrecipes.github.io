"""Pillar guide (DRAFT, not registered): from hybrid to cloud-native — convert group, user and contact
Source of Authority (SOA) to Microsoft Entra ID, turn off directory synchronization, move DNS and
decommission on-premises Active Directory and the Windows Servers behind it.
Documentation checked against the linked Microsoft Learn / Microsoft Support sources on 2026-11-15;
not lab-tested. Status: draft for editor review; NOT registered in build_site.py; NOT published.
Text in `backticks` renders as <code>. Steps carry an optional "code" list of (label, text) blocks.
"""

SLUG = "cloud-native-ad-decommission"
TIER = "pillar"
PUBLISHED = "2026-11-15"
VERIFIED = "2026-11-15"
UPDATED = "2026-11-15"
TITLE = "Go cloud-native: retire on-prem AD after Entra SOA"
SHORT = "Retire on-prem AD (cloud-native)"
DESC = (
    "End-to-end plan for leaving hybrid identity: inventory AD dependencies, convert group, user and contact "
    "Source of Authority to Microsoft Entra ID with Microsoft Graph, run a coexistence period, take restorable "
    "backups, turn off directory synchronization, move DNS to Azure DNS and demote the last domain controllers "
    "safely — with read-only checks, rollback per phase and the points of no return. Documentation verified; "
    "not lab-tested."
)
BADGE = "Microsoft Learn and Microsoft Support checked; not lab-tested"
SRC_LABEL = "Microsoft sources"
TIME_NOTE = (
    "Time estimates are Tenant Recipes planning figures for a single-forest, single-domain organisation of a few "
    "hundred to a few thousand users that has already moved mail to Exchange Online, not Microsoft numbers. "
    "Device re-provisioning and application remediation usually dominate the calendar."
)
CTA_FIRST = "Start with the decision and read-only checks →"
TAGS = ("entra-id", "active-directory", "hybrid-identity", "intune", "dns")
RELATED = ("entra-private-access-vpn-replacement", "purple-team-hybrid-identity", "adcs-hardening-tier0")

INTRO = [
    "Many organisations reach the same point: mail is in Exchange Online, laptops are managed by Intune, every "
    "new application signs in with Microsoft Entra ID — and yet two or three domain controllers still run in a "
    "server room, Microsoft Entra Connect still synchronises every user, and nobody can edit a job title in the "
    "cloud because the object is mastered on-premises. The domain has become a dependency you maintain, patch and "
    "defend mainly because it is there.",
    "Microsoft now gives you a controlled way out. Object-level Source of Authority (SOA) lets you move the "
    "authority for individual groups, users and contacts from Active Directory Domain Services (AD DS) to "
    "Microsoft Entra ID while synchronisation keeps running for everything else. Group SOA became generally "
    "available in October 2025 and user SOA in January 2026 (Microsoft Entra What's new). Once nothing depends on "
    "AD any more, you can turn off directory synchronization, move DNS and demote the domain controllers.",
    "This guide covers the whole journey in the order that keeps it reversible for as long as possible: decide, "
    "inventory, close the gaps (devices, Exchange, authentication, file and network services), convert groups "
    "first, then users and contacts, run a coexistence period, take restorable backups, and only then cross the "
    "two points of no return — turning off synchronization and demoting the last domain controller. Every "
    "technical claim links to Microsoft documentation; anything we could not confirm is listed under 'What is "
    "not verified'.",
    "Going fully cloud-native is not right for everyone. If you still run applications that need LDAP binds, "
    "Kerberos with passwords, Group Policy or domain join, the box 'When to choose something else' explains when "
    "to keep a minimised AD, use Microsoft Entra Domain Services, or stop at the AD-minimised state.",
]

NAMING = (
    "Scope: Microsoft 365 commercial tenants with one AD DS forest synchronised by Microsoft Entra Connect Sync or "
    "Microsoft Entra Cloud Sync, mail already in Exchange Online. Role names differ across Learn articles "
    "('Hybrid Administrator' and 'Hybrid Identity Administrator' refer to the same Entra role). Product labels "
    "change; prefer the linked Learn articles when a label differs. Basis: the end state and sequencing follow Microsoft's "
    "road-to-the-cloud transformation states and its cloud-first identity guidance for IT architects; the 11-phase model, "
    "gates and rollback table are Tenant Recipes' own. Tenant Recipes is not affiliated with Microsoft."
)

NOTICE = {
    "title": "Evidence boundary and points of no return",
    "text": (
        "Every step links to the Microsoft documentation it is based on, checked on 15 November 2026. Nothing in "
        "this guide has been lab-tested by Tenant Recipes. Two steps are effectively irreversible: turning off "
        "directory synchronization for the tenant (Phase 8) and demoting the last domain controller, which removes "
        "the domain (Phase 10). Do not start either without the go/no-go in Phase 7 signed off and restorable "
        "backups verified."
    ),
}

HISTORY = [
    ("2026-11-15", "Draft pillar guide: hybrid to cloud-native — group, user and contact SOA, sync shutdown, DNS move and AD decommissioning. Documentation verified, not lab-tested."),
]


def S(*keys):
    return [L[k] for k in keys]


L = {
    "whatsnew": ("Microsoft Learn: Microsoft Entra releases and announcements (What's new)", "https://learn.microsoft.com/en-us/entra/fundamentals/whats-new"),
    "whatsnew_arch": ("Microsoft Learn: Microsoft Entra What's new archive (Group SOA GA, October 2025)", "https://learn.microsoft.com/en-us/entra/fundamentals/whats-new-archive"),
    "road": ("Microsoft Learn: Road to the cloud — transformation states (State 5: 100% cloud)", "https://learn.microsoft.com/en-us/entra/architecture/road-to-the-cloud-posture"),
    "itarch": ("Microsoft Learn: Microsoft Entra cloud-first identity guidance for IT architects", "https://learn.microsoft.com/en-us/entra/identity/hybrid/guidance-it-architects-source-of-authority"),
    "gsoa": ("Microsoft Learn: Convert Group Source of Authority to the cloud (overview)", "https://learn.microsoft.com/en-us/entra/identity/hybrid/concept-source-of-authority-overview"),
    "gsoa_cfg": ("Microsoft Learn: Configure Group Source of Authority", "https://learn.microsoft.com/en-us/entra/identity/hybrid/how-to-group-source-of-authority-configure"),
    "gsoa_guid": ("Microsoft Learn: Guidance for using Group SOA in Microsoft Entra ID", "https://learn.microsoft.com/en-us/entra/identity/hybrid/concept-group-source-of-authority-guidance"),
    "usoa": ("Microsoft Learn: Transfer user SOA to Microsoft Entra ID (overview)", "https://learn.microsoft.com/en-us/entra/identity/hybrid/user-source-of-authority-overview"),
    "usoa_cfg": ("Microsoft Learn: Configure user (and contact) Source of Authority", "https://learn.microsoft.com/en-us/entra/identity/hybrid/how-to-user-source-of-authority-configure"),
    "graph_osb": ("Microsoft Learn: Update onPremisesSyncBehavior (Microsoft Graph v1.0)", "https://learn.microsoft.com/en-us/graph/api/onpremisessyncbehavior-update"),
    "pim": ("Microsoft Learn: What is Microsoft Entra Privileged Identity Management?", "https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-configure"),
    "pim_settings": ("Microsoft Learn: Configure Microsoft Entra role settings in PIM (activation maximum duration)", "https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-how-to-change-default-settings"),
    "dirsync_off": ("Microsoft Learn: Turn off directory synchronization for Microsoft 365", "https://learn.microsoft.com/en-us/microsoft-365/enterprise/turn-off-directory-synchronization"),
    "connect_uninstall": ("Microsoft Learn: Uninstall Microsoft Entra Connect", "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-uninstall"),
    "connect_sched": ("Microsoft Learn: Microsoft Entra Connect Sync scheduler", "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-sync-feature-scheduler"),
    "cs_agent": ("Microsoft Learn: Cloud provisioning agent — automatic upgrade and uninstall", "https://learn.microsoft.com/en-us/entra/identity/hybrid/cloud-sync/how-to-automatic-upgrade"),
    "cs_config": ("Microsoft Learn: Cloud Sync configuration — remove a configuration, agent removal timeline", "https://learn.microsoft.com/en-us/entra/identity/hybrid/cloud-sync/how-to-configure"),
    "cs_faq": ("Microsoft Learn: Microsoft Entra Cloud Sync FAQ", "https://learn.microsoft.com/en-us/entra/identity/hybrid/cloud-sync/reference-cloud-sync-faq"),
    "fed_to_cloud": ("Microsoft Learn: Migrate from federation to cloud authentication", "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/migrate-from-federation-to-cloud-authentication"),
    "sso_faq": ("Microsoft Learn: Seamless single sign-on FAQ (AZUREADSSO account)", "https://learn.microsoft.com/en-us/entra/identity/hybrid/connect/how-to-connect-sso-faq"),
    "sspr_wb": ("Microsoft Learn: How SSPR password writeback works", "https://learn.microsoft.com/en-us/entra/identity/authentication/concept-sspr-writeback"),
    "ckt": ("Microsoft Learn: Windows Hello for Business cloud Kerberos trust deployment", "https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/deploy/hybrid-cloud-kerberos-trust"),
    "exch_les": ("Microsoft Learn: Manage recipients in Exchange hybrid environments (last Exchange server)", "https://learn.microsoft.com/en-us/exchange/manage-hybrid-exchange-recipients-with-management-tools"),
    "exch_soa": ("Microsoft Learn: Cloud-based management of Exchange attributes for remote mailboxes", "https://learn.microsoft.com/en-us/exchange/hybrid-deployment/enable-exchange-attributes-cloud-management"),
    "devplan": ("Microsoft Learn: Plan your Microsoft Entra device deployment", "https://learn.microsoft.com/en-us/entra/identity/devices/plan-device-deployment"),
    "ap_existing": ("Microsoft Learn: Windows Autopilot for existing devices", "https://learn.microsoft.com/en-us/autopilot/existing-devices"),
    "ap_reset": ("Microsoft Learn: Windows Autopilot Reset overview (hybrid join not supported)", "https://learn.microsoft.com/en-us/autopilot/tutorial/reset/autopilot-reset-overview"),
    "ap_scen": ("Microsoft Learn: Windows Autopilot scenarios", "https://learn.microsoft.com/en-us/autopilot/tutorial/autopilot-scenarios"),
    "gpa": ("Microsoft Learn: Group Policy analytics in Intune", "https://learn.microsoft.com/en-us/intune/intune-service/configuration/group-policy-analytics"),
    "laps": ("Microsoft Learn: Windows LAPS with Microsoft Intune", "https://learn.microsoft.com/en-us/intune/intune-service/protect/windows-laps-overview"),
    "cloudpki": ("Microsoft Learn: Microsoft Cloud PKI for Intune", "https://learn.microsoft.com/en-us/intune/cloud-pki/"),
    "gsa_pa": ("Microsoft Learn: Microsoft Entra Private Access", "https://learn.microsoft.com/en-us/entra/global-secure-access/concept-private-access"),
    "aadds": ("Microsoft Learn: Microsoft Entra Domain Services overview", "https://learn.microsoft.com/en-us/entra/identity/domain-services/overview"),
    "ldap_sign": ("Microsoft Learn: How to enable LDAP signing (events 2887/2889)", "https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server"),
    "ad_diag": ("Microsoft Learn: AD and LDS diagnostic event logging", "https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/configure-ad-and-lds-event-logging"),
    "ntlm_audit": ("Microsoft Learn: Configure Windows event auditing — NTLM event 8004 (Defender for Identity)", "https://learn.microsoft.com/en-us/defender-for-identity/deploy/configure-windows-event-collection"),
    "ntlm_enh": ("Microsoft Support: NTLM auditing enhancements in Windows 11 24H2 and Windows Server", "https://support.microsoft.com/en-us/servicing/os/windows/2025/07/overview-of-ntlm-auditing-enhancements-in-windows-11-version-24h2-and-windows-server-2025"),
    "bkp": ("Microsoft Learn: AD forest recovery — back up a full server (wbadmin)", "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-backing-up-a-full-server"),
    "tsl": ("Microsoft Learn: Shelf life of a system-state backup of AD", "https://learn.microsoft.com/en-us/previous-versions/troubleshoot/windows-server/shelf-life-system-state-backup-ad"),
    "recover": ("Microsoft Learn: AD forest recovery — determine how to recover the forest", "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/forest-recovery-guide/ad-forest-recovery-determine-how-to-recover"),
    "demote": ("Microsoft Learn: Demote domain controllers and domains", "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/demoting-domain-controllers-and-domains--level-200-"),
    "uninst_dc": ("Microsoft Learn: Uninstall-ADDSDomainController", "https://learn.microsoft.com/en-us/powershell/module/addsdeployment/uninstall-addsdomaincontroller"),
    "fsmo": ("Microsoft Learn: Transfer or seize Operation Master roles in AD DS", "https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/transfer-or-seize-operation-master-roles-in-ad-ds"),
    "fsmo_ps": ("Microsoft Learn: Move-ADDirectoryServerOperationMasterRole", "https://learn.microsoft.com/en-us/powershell/module/activedirectory/move-addirectoryserveroperationmasterrole"),
    "meta": ("Microsoft Learn: Clean up AD DS server metadata", "https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/ad-ds-metadata-cleanup"),
    "dns_deleg": ("Microsoft Learn: Delegate a domain to Azure DNS", "https://learn.microsoft.com/en-us/azure/dns/dns-delegate-domain-azure-dns"),
    "dns_import": ("Microsoft Learn: Import and export a DNS zone file (Azure DNS)", "https://learn.microsoft.com/en-us/azure/dns/dns-import-export-portal"),
    "dns_private": ("Microsoft Learn: What is Azure Private DNS?", "https://learn.microsoft.com/en-us/azure/dns/private-dns-overview"),
    "dns_export": ("Microsoft Learn: Export-DnsServerZone", "https://learn.microsoft.com/en-us/powershell/module/dnsserver/export-dnsserverzone"),
}

# ---------------------------------------------------------------------------
# Snippets. Read-only first in every phase. Admin procedures only.
# ---------------------------------------------------------------------------
PS_TENANT_STATE = r"""# READ-ONLY. Microsoft Graph PowerShell. Tenant sync state and synced object counts.
Connect-MgGraph -Scopes "Organization.Read.All","User.Read.All","Group.Read.All"
Get-MgOrganization | Select-Object DisplayName, OnPremisesSyncEnabled, OnPremisesLastSyncDateTime

# Users / groups still mastered on-premises (advanced query needs ConsistencyLevel eventual)
Get-MgUser  -All -Filter "onPremisesSyncEnabled eq true" -ConsistencyLevel eventual -CountVariable u -Property Id,UserPrincipalName | Out-Null; "Synced users:  $u"
Get-MgGroup -All -Filter "onPremisesSyncEnabled eq true" -ConsistencyLevel eventual -CountVariable g -Property Id,DisplayName | Out-Null; "Synced groups: $g"
"""

PS_AD_INVENTORY = r"""# READ-ONLY. Management host with RSAT (ActiveDirectory, GroupPolicy, DnsServer, DhcpServer modules).
Get-ADDomainController -Filter * | Select-Object Name, Site, IPv4Address, OperatingSystem, IsGlobalCatalog, OperationMasterRoles
Get-ADComputer -Filter * -Properties OperatingSystem, LastLogonDate |
  Group-Object OperatingSystem | Sort-Object Count -Descending | Select-Object Count, Name
Get-ADUser -Filter "ServicePrincipalName -like '*'" -Properties ServicePrincipalName, LastLogonDate |
  Select-Object SamAccountName, LastLogonDate, @{n='SPNs';e={$_.ServicePrincipalName -join '; '}}
Get-ADServiceAccount -Filter * | Select-Object Name, Enabled
Get-GPO -All | Select-Object DisplayName, GpoStatus, ModificationTime | Sort-Object DisplayName
Get-DnsServerZone -ComputerName <dc> | Select-Object ZoneName, ZoneType, IsDsIntegrated, IsReverseLookupZone
Get-DhcpServerInDC
"""

LDAP_NTLM = r"""# CHANGE (diagnostic, reversible): log insecure LDAP binds as Directory Service event 2889.
# Set the value back to 0 when you have the data; Learn notes the performance cost.
reg add HKLM\SYSTEM\CurrentControlSet\Services\NTDS\Diagnostics /v "16 LDAP Interface Events" /t REG_DWORD /d 2 /f

# READ-ONLY: who still binds via LDAP, and who still uses NTLM (8004 needs the NTLM audit policies on DCs)
Get-WinEvent -FilterHashtable @{LogName='Directory Service'; Id=2889} -MaxEvents 500 |
  Select-Object TimeCreated, @{n='Detail';e={$_.Message -replace '\s+',' '}}
Get-WinEvent -FilterHashtable @{LogName='Security'; Id=8004} -MaxEvents 500 | Select-Object TimeCreated, Message
Get-WinEvent -LogName 'Microsoft-Windows-NTLM/Operational' -MaxEvents 500 | Select-Object TimeCreated, Id, Message
"""

GRAPH_GROUP_SOA = r"""# Graph PowerShell as Hybrid (Identity) Administrator, activated just-in-time in PIM.
# Consent for Group-OnPremisesSyncBehavior.ReadWrite.All must be granted to THIS app (Graph PowerShell != Graph Explorer).
Connect-MgGraph -TenantId "<tenant-id>" -Scopes "Group-OnPremisesSyncBehavior.ReadWrite.All"
$gid = "<group-object-id>"

# READ-ONLY: expect isCloudManaged = false
Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/groups/$gid/onPremisesSyncBehavior?`$select=isCloudManaged"

# CHANGE: move this group's SOA to Microsoft Entra ID
Invoke-MgGraphRequest -Method PATCH -Uri "https://graph.microsoft.com/v1.0/groups/$gid/onPremisesSyncBehavior" -Body @{ isCloudManaged = $true }

# VERIFY: expect true; audit log activity 'Change Source of Authority from AD to cloud'
Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/groups/$gid/onPremisesSyncBehavior?`$select=isCloudManaged"
"""

GRAPH_USER_SOA = r"""# Scope User-OnPremisesSyncBehavior.ReadWrite.All (contacts: Contacts-OnPremisesSyncBehavior.ReadWrite.All).
Connect-MgGraph -TenantId "<tenant-id>" -Scopes "User-OnPremisesSyncBehavior.ReadWrite.All"
$uid = "<user-object-id>"

# READ-ONLY
Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/users/$uid/onPremisesSyncBehavior?`$select=isCloudManaged"

# CHANGE (Learn also shows: Update-MgUserOnPremiseSyncBehavior -UserId $uid -BodyParameter @{ isCloudManaged = $true })
Invoke-MgGraphRequest -Method PATCH -Uri "https://graph.microsoft.com/v1.0/users/$uid/onPremisesSyncBehavior" -Body @{ isCloudManaged = $true }

# VERIFY
Invoke-MgGraphRequest -Method GET -Uri "https://graph.microsoft.com/v1.0/users/$uid/onPremisesSyncBehavior?`$select=isCloudManaged"

# Contacts (v1.0 per Learn)
# GET   https://graph.microsoft.com/v1.0/contacts/{id}/onPremisesSyncBehavior?$select=isCloudManaged
# PATCH https://graph.microsoft.com/v1.0/contacts/{id}/onPremisesSyncBehavior   { "isCloudManaged": true }
"""

BATCH_SOA = r"""# Wave pattern: reviewed CSV (ObjectId,Type), dry-run unless -Apply, every result logged.
param([string]$Csv = ".\soa-wave-01.csv", [switch]$Apply)
$log = foreach ($r in Import-Csv $Csv) {
  $seg = switch ($r.Type) { 'group' {'groups'} 'contact' {'contacts'} default {'users'} }
  $uri = "https://graph.microsoft.com/v1.0/$seg/$($r.ObjectId)/onPremisesSyncBehavior"
  $before = (Invoke-MgGraphRequest -Method GET -Uri "$uri`?`$select=isCloudManaged").isCloudManaged
  if ($Apply -and -not $before) { Invoke-MgGraphRequest -Method PATCH -Uri $uri -Body @{ isCloudManaged = $true } }
  $after = (Invoke-MgGraphRequest -Method GET -Uri "$uri`?`$select=isCloudManaged").isCloudManaged
  [pscustomobject]@{ When = Get-Date -Format s; Type = $r.Type; Id = $r.ObjectId; Before = $before; After = $after; Applied = [bool]$Apply }
}
$log | Export-Csv ".\soa-wave-log-$(Get-Date -Format yyyyMMdd-HHmm).csv" -NoTypeInformation
"""

SOA_ROLLBACK = r"""# Per-object SOA rollback (Learn). First remove cloud references (cloud members, access packages).
$syncId = "<onPremisesSynchronization id>"
Invoke-MgGraphRequest -Method PATCH -Uri "https://graph.microsoft.com/beta/directory/onPremisesSynchronization/$syncId" `
  -Body @{ features = @{ blockCloudObjectTakeoverThroughHardMatchEnabled = $false } }
Invoke-MgGraphRequest -Method PATCH -Uri "https://graph.microsoft.com/v1.0/users/<id>/onPremisesSyncBehavior" -Body @{ isCloudManaged = $false }
Start-ADSyncSyncCycle -PolicyType Delta   # on the Connect Sync server; rollback completes after this run
Invoke-MgGraphRequest -Method PATCH -Uri "https://graph.microsoft.com/beta/directory/onPremisesSynchronization/$syncId" `
  -Body @{ features = @{ blockCloudObjectTakeoverThroughHardMatchEnabled = $true } }
"""

BACKUP = r"""# READ-ONLY: tombstone lifetime (= backup shelf life; empty value means 60 days per Learn) and Recycle Bin
$cfg = (Get-ADRootDSE).configurationNamingContext
Get-ADObject "CN=Directory Service,CN=Windows NT,CN=Services,$cfg" -Properties tombstoneLifetime | Select-Object tombstoneLifetime
Get-ADOptionalFeature -Filter "Name -eq 'Recycle Bin Feature'" | Select-Object Name, EnabledScopes

# ADDITIVE: critical-volume backup per DC (Learn example) and configuration exports
wbadmin start backup -allCritical -backuptarget:E: -quiet
Backup-GPO -All -Path "\\records\ad-final\gpo"
Get-ADUser     -Filter * -Properties * | Export-Clixml "\\records\ad-final\users.xml"
Get-ADGroup    -Filter * -Properties * | Export-Clixml "\\records\ad-final\groups.xml"
Get-ADComputer -Filter * -Properties * | Export-Clixml "\\records\ad-final\computers.xml"
Get-ADOrganizationalUnit -Filter * -Properties * | Export-Clixml "\\records\ad-final\ous.xml"
Get-DnsServerZone | Where-Object { -not $_.IsAutoCreated } | ForEach-Object {
  Export-DnsServerZone -Name $_.ZoneName -FileName "$($_.ZoneName).dns" }   # written to %windir%\System32\dns
Export-DhcpServer -File "\\records\ad-final\dhcp.xml" -Leases
"""

SYNC_OFF = r"""# 1) Connect Sync server: READ-ONLY state, then pause the scheduler
Get-ADSyncScheduler
Set-ADSyncScheduler -SyncCycleEnabled $false

# 2) Uninstall: Control Panel > Uninstall a program > Microsoft Entra Connect > Remove.
#    Cloud Sync: uninstall 'Microsoft Entra Connect Agent Updater', 'Microsoft Entra Provisioning Agent'
#    and 'Microsoft Entra Provisioning Agent Package' on every agent server.

# 3) Tenant switch (Learn). POINT OF NO RETURN 1.
Connect-MgGraph -Scopes "Organization.ReadWrite.All","Directory.ReadWrite.All"
Get-MgOrganization | Select-Object OnPremisesSyncEnabled            # READ-ONLY, expect True
$organizationId = (Get-MgOrganization).Id
Update-MgOrganization -OrganizationId $organizationId -BodyParameter @{ onPremisesSyncEnabled = $false }
Get-MgOrganization | Select-Object OnPremisesSyncEnabled            # expect False
"""

DNS_MOVE = r"""# READ-ONLY: current delegation and records (save before/after)
Resolve-DnsName -Name contoso.com -Type NS  -Server 1.1.1.1
Resolve-DnsName -Name contoso.com -Type SOA -Server 1.1.1.1
Get-DnsServerResourceRecord -ZoneName contoso.com -ComputerName <dc> | Sort-Object RecordType, HostName

# CHANGE: Azure CLI — create the public zone, import the exported file, list the assigned name servers
az network dns zone create -g rg-dns -n contoso.com
az network dns zone import -g rg-dns -n contoso.com -f contoso.com.dns
az network dns zone show   -g rg-dns -n contoso.com --query nameServers
# At the registrar: replace NS with ALL FOUR Azure DNS name servers, then verify:
Resolve-DnsName -Name contoso.com -Type NS -Server 8.8.8.8
"""

DC_DEMOTE = r"""# READ-ONLY health and role placement
repadmin /replsummary
dcdiag /q
netdom query fsmo
Get-ADDomainController -Filter * | Select-Object Name, OperationMasterRoles, IsGlobalCatalog

# Transfer all five roles to the DC that will be removed LAST
Move-ADDirectoryServerOperationMasterRole -Identity "DC-LAST" `
  -OperationMasterRole SchemaMaster, DomainNamingMaster, PDCEmulator, RIDMaster, InfrastructureMaster

# Each additional DC: preview, then demote normally (no -ForceRemoval); prompts for the new local admin password
Uninstall-ADDSDomainController -WhatIf
Uninstall-ADDSDomainController

# LAST DC ONLY — removes the domain (and the forest if it is the last domain). POINT OF NO RETURN 2. Preview first.
Uninstall-ADDSDomainController -LastDomainControllerInDomain -RemoveApplicationPartitions -IgnoreLastDnsServerForZone -WhatIf
"""

POSTCHECK = r"""# READ-ONLY post-checks (Graph PowerShell)
Get-MgOrganization | Select-Object OnPremisesSyncEnabled, OnPremisesLastSyncDateTime      # expect False
Get-MgUser  -All -Filter "onPremisesSyncEnabled eq true" -ConsistencyLevel eventual -CountVariable u | Out-Null; "Still-synced users: $u"    # expect 0
Get-MgGroup -All -Filter "onPremisesSyncEnabled eq true" -ConsistencyLevel eventual -CountVariable g | Out-Null; "Still-synced groups: $g"   # expect 0
Get-MgDevice -All -Property DisplayName,TrustType,ApproximateLastSignInDateTime |
  Group-Object TrustType | Select-Object Count, Name      # 'ServerAd' = hybrid joined; expect none active
Resolve-DnsName -Name contoso.com -Type NS -Server 8.8.8.8                                 # expect Azure DNS
"""

# ---------------------------------------------------------------------------
# Editorial boxes. Rendered through PROBLEM today; EDITORIAL_BOXES for a future renderer.
# ---------------------------------------------------------------------------
BOX_WHY = [
    "It removes a high-value target. Microsoft's architect guidance calls AD the 'keys to the kingdom'; every "
    "domain controller you retire is one less tier-0 system to patch, back up, monitor and defend.",
    "It moves identity to where your controls already are. Cloud-managed users and groups are governed with "
    "Conditional Access, phishing-resistant authentication, PIM, access reviews and lifecycle workflows instead "
    "of a directory those controls cannot see.",
    "Object-level SOA makes the journey gradual and reversible. You convert one group, user or contact at a time, "
    "test, and can revert per object (documented by Microsoft) until you deliberately turn sync off.",
    "It forces a dependency inventory you need anyway. Even if you stop at an AD-minimised state, knowing every "
    "LDAP bind, NTLM caller, GPO and service account is valuable security work.",
]
BOX_ALT = [
    "Keep a minimised AD when line-of-business applications still need LDAP binds with passwords, Kerberos with "
    "passwords, LDAP writes or AD-specific schema features. Microsoft states that users whose SOA is transferred "
    "cannot be tied to password-based LDAP/Kerberos applications, and that password writeback is not available "
    "for users provisioned from Entra ID to AD.",
    "Use Microsoft Entra Domain Services for Azure-hosted legacy workloads that need domain join, Group Policy, "
    "LDAP or Kerberos/NTLM, with Entra ID as the source of authority. Microsoft positions it as a transitional "
    "capability, not a general replacement for on-premises AD, and users may need to reset passwords to generate "
    "the required hashes.",
    "Stop at the AD-minimised state — users and groups cloud-managed, Cloud Sync provisioning back to AD only what "
    "Kerberos apps need, Windows Hello for Business cloud Kerberos trust — when file servers or apps cannot move "
    "yet. That is a supported end state, not a failure.",
    "Use Azure Virtual Desktop or Windows 365 as a last resort for client-server apps tied to domain-joined "
    "machines; Microsoft's guidance names this fallback because of the added cost and complexity.",
    "Wait if you still federate with AD FS (user SOA is not supported for AD FS-federated users), still host "
    "mailboxes on-premises, or have hybrid-joined devices without a re-provisioning plan.",
]
BOX_UNVERIFIED = [
    "How long the tenant-wide conversion takes after `onPremisesSyncEnabled = false`. The current Learn article "
    "says only that you must wait 72 hours before you can turn sync back on, and lists the cleared properties. "
    "Planning for up to 72 hours of conversion is our assumption, not a documented duration.",
    "Cleanup of the Entra-side directory synchronization service account after uninstall. Learn's uninstall article "
    "covers Entra Connect itself only; confirm in your tenant whether the account remains and remove it if so.",
    "Contact SOA with Cloud Sync. Learn documents contact SOA and a Connect Sync minimum of 2.5.79.0; we found no "
    "explicit Cloud Sync minimum for contacts.",
    "The user experience right after sync is turned off (password expiry, sign-in prompts) for users on password "
    "hash synchronization. Learn does not describe it; pilot sign-ins in the change window.",
    "The observation-window exit criteria (Phase 6) and the powered-off observation window before demotion (Phase 10) "
    "are Tenant Recipes' own gates, not Microsoft requirements.",
    "A full rollback after sync-off. Learn allows re-enabling after 72 hours, but rematching depends on hard/soft "
    "match, and since 1 June 2026 hard match is blocked for cloud users holding Entra roles (What's new). We have "
    "not tested it, so we treat sync-off as a point of no return.",
    "'Entra DNS' is not a Microsoft product name we could find. Public zones move to Azure DNS; internal names to "
    "Azure Private DNS or your network platform. DHCP has no Entra equivalent; it moves to whatever DHCP service your "
    "network platform provides.",
    "Older samples call onPremisesSyncBehavior on the Graph beta endpoint. Learn's current procedure uses v1.0 for "
    "users, groups and contacts; only the takeover-protection flag in the rollback uses beta.",
    "Hybrid-joined to Entra-joined conversion. Learn documents Autopilot for existing devices as the conversion "
    "method and that Autopilot Reset does not support hybrid-joined devices; the explicit statement 'no in-place "
    "conversion' comes from Microsoft Q&A answers, not from a Learn article.",
]

EDITORIAL_BOXES = [
    {"kind": "why", "title": "Why we recommend this", "items": BOX_WHY},
    {"kind": "alt", "title": "When to choose something else", "items": BOX_ALT},
    {"kind": "unverified", "title": "What is not verified", "items": BOX_UNVERIFIED},
]

PROBLEM = {
    "title": "The problem: a hybrid identity you keep only because it is there",
    "blocks": [
        ("Where the authority lives",
         ["In a synchronised tenant, AD DS is the Source of Authority: attributes, group memberships and passwords "
          "are mastered on-premises and edits in the cloud are rejected. As long as that is true, the directory, "
          "the sync server and every domain controller sit on the critical path for sign-ins and changes.",
          "Microsoft's road-to-the-cloud model ends in 'State 5: 100% cloud': no on-premises IAM footprint, all "
          "devices managed in Entra ID and cloud tools such as Intune, all users and groups cloud-native, and "
          "network services that relied on AD relocated. This guide is a practical path to that state."]),
        ("The order that keeps it safe",
         ["Microsoft recommends transferring group SOA ahead of users, to keep memberships intact and allow "
          "testing. Contacts can follow. Only when no object, device, application or network service needs AD do "
          "you turn off synchronization, move DNS and demote the domain controllers — each with a backup, a "
          "rollback plan and the two points of no return made explicit."]),
        ("Why we recommend this", BOX_WHY),
        ("When to choose something else", BOX_ALT),
        ("What is not verified", BOX_UNVERIFIED),
    ],
    "src": S("road", "itarch", "gsoa", "usoa", "whatsnew"),
}

PHASES = [
    {
        "id": "decide",
        "title": "Decide the target state and check readiness",
        "time": "1–2 weeks",
        "goal": "A signed decision — full cloud-native (State 5) or AD-minimised — with owners, a read-only baseline and sync clients on SOA-aware versions.",
        "lead": "Nothing in this phase changes production. You decide where you are going and measure where you are.",
        "steps": [
            {
                "t": "Choose the end state explicitly",
                "check": "Decision record states 'cloud-native' or 'AD-minimised', with sponsor, scope (forests/domains) and exit criteria",
                "do": [
                    "Use Microsoft's transformation states: AD-minimised keeps AD only for what still needs it; State 5 (100% cloud) has no on-premises IAM footprint.",
                    "Turn Learn's State 5 description into your Phase 7 gate now, one line per criterion: no on-premises IAM footprint required; all devices managed in Entra ID and cloud tools such as Intune; user lifecycle managed through Entra ID; all users and groups cloud-native; network services that rely on AD relocated.",
                    "Read 'When to choose something else' before you commit; stopping at AD-minimised is a valid result.",
                ],
                "pit": ["Treating SOA conversion as the goal. It is a means; the goal is removing dependencies safely."],
                "src": S("road", "itarch"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Baseline the tenant read-only and confirm feature status",
                "check": "Counts of synced users and groups, OnPremisesSyncEnabled and last sync time saved with a date",
                "do": [
                    "Run the read-only Graph snippet and keep the output. Repeat it at the end of every phase.",
                    "Feature status (Microsoft Entra What's new): group SOA generally available since October 2025, user SOA since January 2026; contact SOA is documented in the user SOA article.",
                    "Licence: Learn lists Microsoft Entra Free as sufficient for user and group SOA.",
                ],
                "pit": ["Older posts still call SOA 'preview'. Use the Learn What's new pages as the authority."],
                "code": [("Read-only tenant baseline (Graph PowerShell)", PS_TENANT_STATE)],
                "src": S("whatsnew", "whatsnew_arch", "usoa_cfg", "gsoa_cfg"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Upgrade sync clients and set up least-privilege access",
                "check": "Connect Sync ≥ 2.5.76.0 (≥ 2.5.79.0 for contacts) or Cloud Sync agent ≥ 1.1.1370.0; Hybrid Administrator eligible in PIM; consent granted to the tool you will use; test tenant rehearsal done",
                "do": [
                    "Learn sets these minimum versions so the sync client honours the SOA flag. Upgrade before converting anything.",
                    "Use the Hybrid Administrator (Hybrid Identity Administrator) role for SOA operations rather than Global Administrator. Learn names Hybrid Administrator as the role required to read and update SOA. Make it eligible in Privileged Identity Management and set the role's activation maximum duration (configurable from 1 to 24 hours) and approval requirements to match your change-window policy.",
                    "An Application Administrator or Cloud Application Administrator grants consent for `Group-OnPremisesSyncBehavior.ReadWrite.All`, `User-OnPremisesSyncBehavior.ReadWrite.All` and, if needed, `Contacts-OnPremisesSyncBehavior.ReadWrite.All` to the exact app you use. Consent to Graph Explorer does not carry over to Microsoft Graph PowerShell.",
                    "The SOA permissions do not allow editing other properties; rename tests also need `Group.ReadWrite.All` / `User.ReadWrite.All`.",
                    "Optional: scope user SOA operations to an administrative unit so an operator can only convert the current wave (documented by Learn).",
                    "Rehearse the full sequence in a test tenant with a test forest before touching production.",
                ],
                "pit": ["Running the first conversion in production because 'it is only one PATCH'."],
                "src": S("gsoa_cfg", "usoa_cfg", "pim", "pim_settings"),
                "rec": ["ca-break-glass"], "tools": [], "marker": "official",
            },
        ],
    },
    {
        "id": "inventory",
        "title": "Inventory everything that still depends on AD",
        "time": "2–6 weeks",
        "deep": True,
        "goal": "A dependency register listing every application, device, server role, service account and identity feature that uses AD, each with an owner and a target.",
        "lead": "Microsoft's guidance: always begin with an application inventory before transferring SOA. This phase is read-only apart from temporary diagnostic logging.",
        "steps": [
            {
                "t": "Applications: LDAP, Kerberos and NTLM callers",
                "check": "Every client seen in events 2889/8004 and the NTLM operational log is mapped to an application and an owner",
                "do": [
                    "Enable LDAP interface diagnostics (value 2) for a representative period; event 2889 logs the client IP and bind identity, and summary event 2887 the daily count.",
                    "Collect NTLM usage: event 8004 on DCs (with the 'Restrict NTLM' audit policies) and, on Windows Server 2019 or later and Windows 11 24H2 or later, the Microsoft-Windows-NTLM/Operational log.",
                    "For each application record how it authenticates (LDAP bind, Kerberos, NTLM, SAML/OIDC), whether it writes to AD, and which AD groups gate access.",
                    "Microsoft's rule: users tied to password-based LDAP bind or Kerberos-with-password apps cannot have their SOA transferred unless another supported authentication path exists.",
                ],
                "pit": ["Leaving diagnostic logging on; set it back to 0 afterwards.",
                        "Network appliances (VPN, Wi-Fi/RADIUS, printers, scanners) often bind via LDAP and are easy to miss."],
                "code": [("Diagnostic logging and read-only event review", LDAP_NTLM)],
                "src": S("itarch", "ldap_sign", "ad_diag", "ntlm_audit", "ntlm_enh"),
                "rec": ["ntlm-signing-phase2-readiness"], "tools": ["pingcastle"], "marker": "official",
            },
            {
                "t": "Servers, service accounts, GPOs, DNS and DHCP",
                "check": "Register lists every domain-joined server and role (file, print, AD CS, NPS, DNS, DHCP, app/SQL), every SPN or gMSA account and every GPO, each with a target",
                "do": [
                    "Run the read-only AD inventory: DCs and FSMO placement, computers by OS, accounts with SPNs, gMSAs, GPOs, DNS zones and authorised DHCP servers.",
                    "Give each server a target that matches Learn's State 5 criterion ('network services that rely on Active Directory are relocated'): relocate the workload to a cloud service, keep it without a domain dependency, or retire it.",
                    "AD CS usually issues Wi-Fi, VPN and Intune certificates. Plan a replacement such as Microsoft Cloud PKI for Intune before the domain goes away.",
                    "LAPS: legacy LAPS stores passwords in AD; Windows LAPS with Intune can back them up to Microsoft Entra ID for Entra-joined devices.",
                ],
                "pit": ["Forgetting VPN and RADIUS (NPS) — they often validate against AD directly."],
                "code": [("Read-only AD estate inventory", PS_AD_INVENTORY)],
                "src": S("itarch", "cloudpki", "laps", "road"),
                "rec": [], "tools": [], "guides": ["adcs-hardening-tier0"], "marker": "official",
            },
            {
                "t": "Devices: hybrid-joined, domain-only and GPO-managed",
                "check": "Count of hybrid-joined and domain-only devices per site with a re-provisioning date per batch; GPO-to-Intune mapping reviewed",
                "do": [
                    "List devices by join type (trust type) in Entra ID and in AD. Every Windows device must end up Microsoft Entra joined and Intune-managed; macOS and mobile devices enrolled in Intune.",
                    "Import GPOs into Intune Group Policy analytics to see which settings have Intune equivalents.",
                    "Microsoft recommends deploying new devices as Entra joined and does not recommend deploying new devices as hybrid joined.",
                ],
                "pit": ["Assuming hybrid-joined devices can be switched in place — see Phase 3."],
                "src": S("devplan", "gpa", "ap_scen"),
                "rec": ["autopilot-device-preparation-entra-join"], "tools": [], "marker": "official",
            },
            {
                "t": "Identity features: federation, Exchange, writeback, SSO, Kerberos trust",
                "check": "For each feature the register says: in use? replacement? owner?",
                "do": [
                    "Federation: user SOA is not supported for AD FS-federated users. With third-party federation the AD account must be managed manually.",
                    "Exchange: the user SOA prerequisites require no on-premises Exchange workloads. Note whether a 'last Exchange server' remains only for recipient management.",
                    "Password writeback (SSPR): after cloud-native, passwords live only in Entra ID; writeback is not available for users provisioned from Entra ID to AD.",
                    "Seamless SSO creates an `AZUREADSSO` computer account in AD and Windows Hello for Business cloud Kerberos trust an `AzureADKerberos` object; both only matter while AD exists.",
                    "HR-driven provisioning should already target Entra ID directly (a Learn prerequisite for user SOA).",
                ],
                "pit": ["Cloud Kerberos trust is a bridge to on-premises resources; it needs domain controllers and has no role once AD is gone."],
                "src": S("usoa", "fed_to_cloud", "exch_les", "sspr_wb", "sso_faq", "ckt"),
                "rec": [], "tools": [], "marker": "official",
            },
        ],
    },
    {
        "id": "close-gaps",
        "title": "Close the gaps: devices, Exchange, authentication, services",
        "time": "1–6 months",
        "deep": True,
        "goal": "Every item in the register has moved, been replaced or been retired — or is consciously kept on a minimised AD.",
        "lead": "Most of the calendar is spent here. Each workstream has its own rollback because nothing tenant-wide has changed yet.",
        "steps": [
            {
                "t": "Re-provision hybrid-joined devices as Entra joined",
                "check": "Zero hybrid-joined or domain-only Windows devices in active use; all devices Entra joined and compliant in Intune",
                "do": [
                    "Learn documents Windows Autopilot for existing devices (a Configuration Manager task sequence) as a method to convert hybrid-joined devices to Entra joined by reimaging; the alternative is wipe and redeploy with Autopilot.",
                    "Windows Autopilot Reset does not support hybrid-joined devices; Learn says a device wipe is required for them.",
                    "Protect user data first (OneDrive Known Folder Move, Windows Backup) and align batches with hardware refresh where possible.",
                ],
                "pit": ["Manually unjoining and joining devices outside a supported provisioning path tends to leave inconsistent state and lost profiles."],
                "src": S("ap_existing", "ap_reset", "ap_scen"),
                "rec": ["autopilot-device-preparation-entra-join", "autopilot-troubleshoot-enrollment"], "tools": [], "marker": "official",
            },
            {
                "t": "Remove the Exchange dependency on AD",
                "check": "No mailboxes on-premises; Exchange attributes managed from Exchange Online (IsExchangeCloudManaged) or the last Exchange server shut down as Learn describes",
                "do": [
                    "Cloud management of Exchange attributes is GA: set `IsExchangeCloudManaged` per mailbox to manage Exchange attributes in Exchange Online instead of on-premises.",
                    "If a last Exchange server exists only for recipient management, Learn says do NOT uninstall it: shut it down and use the documented cleanup, because uninstalling removes AD information the management tools need.",
                    "Mail-enabled security groups and distribution lists can have their SOA converted; afterwards they are managed in Exchange Online or Exchange PowerShell, not in Entra ID or Graph.",
                ],
                "pit": ["Built-in admin mailboxes are not synced by default; Learn says to disable them before proceeding."],
                "src": S("exch_soa", "exch_les", "gsoa"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Move authentication fully to Entra ID",
                "check": "All domains managed (no federation), MFA/passwordless enforced by Conditional Access, SSPR works without writeback",
                "do": [
                    "Migrate from federation to cloud authentication (password hash synchronization during the sync era) before any user SOA transfer.",
                    "Enforce MFA and phishing-resistant methods with Conditional Access; keep two emergency-access accounts excluded and monitored.",
                    "Plan SSPR as cloud-only: once sync is off there is nothing to write back to.",
                ],
                "pit": ["Switching off writeback before users know the new reset path."],
                "src": S("fed_to_cloud", "sspr_wb", "itarch"),
                "rec": ["ca-break-glass", "ca-report-only-first", "ca-block-legacy-auth"], "tools": [], "marker": "official",
            },
            {
                "t": "Relocate file, print, remote access and other AD-bound services",
                "check": "File shares, printers, VPN/remote access, Wi-Fi certificates and line-of-business apps no longer authenticate against AD",
                "do": [
                    "File shares: move content to SharePoint/OneDrive or Azure Files and re-permission with cloud groups.",
                    "Remote access: replace AD-backed VPN with Microsoft Entra Private Access (Global Secure Access) where it fits.",
                    "Applications: move to SAML/OIDC with Entra ID; for Azure-hosted legacy workloads consider Microsoft Entra Domain Services; AVD/Windows 365 only as a last resort.",
                    "Certificates: issue device and user certificates from a non-AD PKI such as Microsoft Cloud PKI before AD CS goes away.",
                ],
                "pit": ["Re-permissioning shares with on-premises groups that are about to disappear."],
                "src": S("gsa_pa", "aadds", "cloudpki", "itarch"),
                "rec": [], "tools": [], "guides": ["entra-private-access-vpn-replacement"], "marker": "official",
            },
        ],
    },
    {
        "id": "group-soa",
        "title": "Convert group Source of Authority (groups first)",
        "time": "1–4 weeks",
        "deep": True,
        "goal": "Every group that must survive is cloud-managed (isCloudManaged = true) and editable in Entra ID or Exchange Online, with memberships unchanged.",
        "lead": "Microsoft recommends transferring group SOA ahead of users to keep membership integrity and allow testing. The object stays the same object; only the authority moves and sync stops for that object.",
        "steps": [
            {
                "t": "Clean up and order the groups",
                "check": "Unused groups removed (scream test), nested groups mapped and ordered bottom-up, mail-enabled groups flagged, extension-attribute users identified",
                "do": [
                    "Learn suggests a scream-test approach to find unused groups; remove them instead of converting them.",
                    "Nested groups are NOT converted with their parent. Convert one by one, starting with the lowest group in the hierarchy and moving up.",
                    "Extension attributes 1–15 are not supported on converted groups; check whether any app depends on them.",
                    "Mail-enabled security groups and distribution lists: manage them in Exchange Online after conversion.",
                    "If a converted security group must still exist in AD for a Kerberos app (AD-minimised path), provision it back with Cloud Sync and prepare it as Learn describes (Universal scope, extension property for the original OU).",
                ],
                "pit": ["Editing a converted group in AD: there is no reconciliation; local changes are ignored and overwritten on the next provisioning run."],
                "src": S("gsoa_cfg", "gsoa_guid", "gsoa"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Convert a test group, then waves",
                "check": "Test group shows isCloudManaged = true, is editable, audit event 'Change Source of Authority from AD to cloud' present; each wave logged",
                "do": [
                    "Read `onPremisesSyncBehavior` (expect false), confirm the group is read-only in the cloud, PATCH `isCloudManaged = true`, read again, check the audit log, then confirm the group is editable — the verification sequence in Learn's configuration article.",
                    "Run a sync cycle and confirm Connect Sync skips the object: Application log event 6956 on the sync server.",
                    "Then convert in waves defined by your dependency register. Learn's app-centric approach suggests sequencing per application — pilot an application together with its groups, then test its users end-to-end. Use a reviewed CSV and a dry-run first.",
                ],
                "pit": ["403 errors usually mean consent was granted to a different app than the one you use (Learn: consent to one app does not grant it to another) or the PIM role is not active."],
                "code": [("Group SOA: read, convert, verify (Graph PowerShell)", GRAPH_GROUP_SOA), ("Wave script with dry-run and log", BATCH_SOA)],
                "src": S("gsoa_cfg", "graph_osb", "itarch"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Rollback for a group",
                "check": "Rollback rehearsed on the test group: cloud references removed, isCloudManaged = false, sync took the object back",
                "do": [
                    "Before reverting, remove cloud-only members and access-package assignments (Learn provides a script to find cloud members; for mail-enabled groups remove them in Exchange).",
                    "PATCH `isCloudManaged = false`. The sync client takes the object back on its next cycle; rollback is complete only after that run.",
                ],
                "pit": [],
                "src": S("gsoa_cfg"),
                "rec": [], "tools": [], "marker": "official",
            },
        ],
    },
    {
        "id": "user-soa",
        "title": "Transfer user and contact Source of Authority",
        "time": "2–6 weeks",
        "deep": True,
        "goal": "All remaining users (and synced contacts) are cloud-managed and editable in Entra ID, with sign-in, licences and access unchanged.",
        "lead": "Learn's user SOA article defines the entry criteria; this phase applies them per wave. The change is per object and reversible until Phase 8.",
        "steps": [
            {
                "t": "Confirm user prerequisites",
                "check": "Every user in the wave meets each prerequisite in Learn's user SOA overview, and the groups that gate their access are already cloud-managed (Phase 4)",
                "do": [
                    "Work through Learn's prerequisite list in its own order: cloud HR integrated with Entra ID; no on-premises Exchange workloads; any authentication method for cloud users, with Windows Hello for Business cloud Kerberos trust for Kerberos apps; no password-based LDAP bind or Kerberos-with-password apps; no AD FS federation; third-party federation only with manual AD account management.",
                    "If users still need on-premises Kerberos resources during coexistence, Learn requires the cloud Kerberos trust model for passwordless and an AD account that remains (or is provisioned back).",
                    "Keep on-premises attributes such as `onPremisesSamAccountName` and `onPremisesSecurityIdentifier` on transferred users while they still access on-premises resources; Learn says do not delete them.",
                ],
                "pit": ["Converting privileged admin accounts early. Do them last, deliberately, after checking emergency access."],
                "src": S("usoa", "usoa_cfg", "itarch"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Transfer a test user, then waves; include contacts",
                "check": "Test user isCloudManaged = true, fields editable, audit event logged, sign-in and licences unchanged; synced contacts converted",
                "do": [
                    "Same pattern as groups with `User-OnPremisesSyncBehavior.ReadWrite.All`: GET (false), confirm read-only, PATCH true, GET (true), audit log, edit test.",
                    "After transfer `isCloudManaged` is true and `onPremisesSyncEnabled` becomes null (Learn attribute table).",
                    "Contacts: `/contacts/{id}/onPremisesSyncBehavior` with `Contacts-OnPremisesSyncBehavior.ReadWrite.All` and Connect Sync 2.5.79.0 or later.",
                    "Use the wave script; for large estates go by department and keep every log.",
                    "Learn's AD-minimisation scenario: once the user is cloud-managed you can remove the AD DS account completely — do that only when the dependency register shows nothing on-premises still uses it.",
                ],
                "pit": ["Copying an old sample that uses the beta URL; Learn's procedure uses v1.0."],
                "code": [("User and contact SOA (Graph PowerShell)", GRAPH_USER_SOA)],
                "src": S("usoa_cfg", "graph_osb", "usoa"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Rollback for a user",
                "check": "Rollback rehearsed on the test user and written into the runbook",
                "do": [
                    "Remove cloud references first (cloud groups, access packages).",
                    "Temporarily disable `blockCloudObjectTakeoverThroughHardMatchEnabled`, PATCH `isCloudManaged = false`, run sync, then re-enable the protection flag (Learn).",
                ],
                "pit": ["Forgetting to re-enable takeover protection after a rollback."],
                "code": [("Per-object SOA rollback", SOA_ROLLBACK)],
                "src": S("usoa_cfg"),
                "rec": [], "tools": [], "marker": "official",
            },
        ],
    },
    {
        "id": "coexist",
        "title": "Run a coexistence and monitoring period",
        "time": "Until the exit criteria are met",
        "goal": "Evidence — not a calendar date — that nothing still uses AD: every monitored signal is quiet for at least one full business cycle.",
        "steps": [
            {
                "t": "Monitor and shrink",
                "check": "Exit criteria met: zero 2889/8004/NTLM-operational callers across at least one full business cycle including month-end; register items all closed; no AD-related incidents",
                "do": [
                    "Keep LDAP and NTLM monitoring on the DCs and review weekly; investigate every new caller.",
                    "Watch Entra sign-in and audit logs for SOA changes and unexpected edits.",
                    "Stop creating objects in AD; create new users and groups in Entra ID only.",
                    "Define the observation window by your own business cycle (payroll, month-end, quarter-end batch jobs), not by a fixed number of days; extend it whenever a new caller appears.",
                ],
                "pit": ["Quarterly or yearly jobs (payroll, audits) that bind to AD rarely — ask owners explicitly."],
                "src": S("itarch", "ldap_sign", "ntlm_audit"),
                "rec": [], "tools": [], "marker": "practical",
            },
        ],
    },
    {
        "id": "backup",
        "title": "Backups, records and go/no-go",
        "time": "1–2 days",
        "goal": "Restorable DC backups inside the tombstone lifetime, exported configuration records, and a signed go/no-go naming both points of no return.",
        "steps": [
            {
                "t": "Take restorable backups and check their shelf life",
                "check": "Critical-volume backups of at least two DCs verified; tombstone lifetime and Recycle Bin recorded; DSRM and local admin passwords stored securely",
                "do": [
                    "Back up each DC with `wbadmin start backup -allCritical` (Learn's forest-recovery example).",
                    "A system-state backup is usable only within the tombstone lifetime: 180 days by default for forests created on Windows Server 2003 SP1 or later; an empty attribute means 60. With the Recycle Bin enabled, the shorter of deletedObjectLifetime and tombstoneLifetime applies.",
                    "Keep the Administrator/DSRM password history with the backups for as long as they are valid (Learn).",
                ],
                "pit": ["Never change system clocks to stretch backup life; Learn warns against it."],
                "code": [("Shelf-life check, backups and configuration exports", BACKUP)],
                "src": S("bkp", "tsl", "recover"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Export configuration records",
                "check": "GPO backups, object exports, DNS zone files and the DHCP export stored with access control and a retention period set by your records policy",
                "do": [
                    "These exports feed Phase 9 (DNS zone files for the Azure DNS import, DHCP scopes for the new DHCP service) and answer later questions about who had access to what. Use `Export-DnsServerZone` and `Export-DhcpServer` (Learn) and Backup-GPO.",
                    "Treat the exports as tier-0 data: they describe your former identity system in detail.",
                ],
                "pit": ["Exports are records, not a restore method; the DC backups are the rollback point."],
                "src": S("dns_export", "dns_import", "recover"),
                "rec": [], "tools": [], "marker": "practical",
            },
            {
                "t": "Go/no-go with the points of no return",
                "check": "Go/no-go signed: register closed, rollback per phase rehearsed, backups verified, change window and communication agreed",
                "do": [
                    "Point of no return 1: turning off directory synchronization for the tenant (Phase 8). Re-enabling is only possible after 72 hours and rematching is not guaranteed.",
                    "Point of no return 2: demoting the last domain controller removes the domain, and the forest if it is the last domain (Phase 10). After that, only a forest recovery from a backup within its shelf life remains.",
                    "Everything before Phase 8 is reversible per object or per workstream. Re-check the State 5 criteria written in Phase 1 before signing.",
                ],
                "pit": [],
                "src": S("dirsync_off", "demote", "tsl"),
                "rec": [], "tools": [], "marker": "official",
            },
        ],
    },
    {
        "id": "sync-off",
        "title": "Uninstall sync and turn off directory synchronization",
        "time": "1 day + up to 72 h",
        "deep": True,
        "goal": "No sync client running, OnPremisesSyncEnabled = False, every object cloud-only.",
        "lead": "POINT OF NO RETURN 1. Learn's order when disabling sync permanently: uninstall the sync client first, then turn off synchronization in the tenant.",
        "steps": [
            {
                "t": "Pause and uninstall the sync clients",
                "check": "Connect Sync uninstalled (Control Panel shows no remaining components) or all Cloud Sync agents uninstalled and the configuration removed",
                "do": [
                    "Connect Sync: pause the scheduler, then Control Panel > Uninstall a program > Microsoft Entra Connect > Remove; refresh to confirm all components are gone (Learn).",
                    "Cloud Sync: uninstall the Agent Updater, Provisioning Agent and Provisioning Agent Package on every agent server. The agent shows Inactive after about an hour and disappears after about 10 days.",
                    "Do NOT shrink the sync scope to 'clean up' beforehand; in Cloud Sync, scoping objects out is the documented way to remove them from Entra ID.",
                    "Cloud Sync: after uninstalling, delete the configuration in the Microsoft Entra admin center if you do not want to wait for automatic agent cleanup (Learn).",
                ],
                "pit": ["Deleting the Cloud Sync configuration does not convert objects; only the tenant switch does."],
                "code": [("Uninstall sync and turn off directory synchronization", SYNC_OFF)],
                "src": S("dirsync_off", "connect_uninstall", "connect_sched", "cs_agent", "cs_config", "cs_faq"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Turn off directory synchronization in the tenant",
                "check": "Get-MgOrganization shows OnPremisesSyncEnabled = False; spot-checked users and groups are editable in Entra ID",
                "do": [
                    "Connect with Microsoft Graph PowerShell (Learn uses `Organization.ReadWrite.All` and `Directory.ReadWrite.All` with a Hybrid Identity Administrator) and run `Update-MgOrganization` with `onPremisesSyncEnabled = $false`.",
                    "Learn: you must then wait 72 hours before you can turn sync back on, and the change clears DnsDomainName, NetBiosName, OnPremisesDistinguishedName, OnPremisesSamAccountName and OnPremisesUserPrincipalName.",
                    "Microsoft does not recommend turning off directory sync as a troubleshooting step; do it only as this planned change.",
                    "Allow time for the conversion to complete before bulk edits; pilot sign-ins and spot-check objects.",
                ],
                "pit": ["Anything that still relied on those on-premises attributes (for example Kerberos SSO to a remaining server) stops working when they are cleared."],
                "src": S("dirsync_off"),
                "rec": [], "tools": [], "marker": "official",
            },
        ],
    },
    {
        "id": "dns",
        "title": "Move DNS and DHCP off the domain controllers",
        "time": "1–2 weeks incl. TTL",
        "goal": "Public zones authoritative in Azure DNS, internal resolution and DHCP served without DCs, verified from outside.",
        "steps": [
            {
                "t": "Export, import and compare zones",
                "check": "Azure DNS record sets match the export; CNAMEs pointing into private zones resolved or rewritten",
                "do": [
                    "Export AD-integrated zones to files with Export-DnsServerZone, then import with the Azure CLI or portal. Importing into an existing zone merges record sets.",
                    "Learn warns that imported CNAMEs pointing into a private zone fail unless that zone is also imported or the records are changed.",
                    "Lower TTLs on the old zone a few days before the cut-over.",
                ],
                "pit": ["AD-only records (_msdcs, _ldap, _kerberos SRV) have no purpose once the domain is gone; do not import them blindly."],
                "code": [("DNS: read-only checks, Azure DNS import, delegation check", DNS_MOVE)],
                "src": S("dns_import", "dns_export"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Delegate at the registrar and verify",
                "check": "Public resolvers return the four Azure DNS name servers; MX, SPF, autodiscover and web records resolve correctly",
                "do": [
                    "Retrieve the zone's name servers in Azure and replace the NS records at the registrar with all four (Learn).",
                    "Verify the delegation from external resolvers; keep the old servers answering until TTLs expire.",
                ],
                "pit": ["Updating only some NS records, or forgetting DNSSEC DS records at the registrar if you use DNSSEC."],
                "src": S("dns_deleg"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Internal names and DHCP",
                "check": "Clients get addresses and DNS from non-DC infrastructure; internal names resolve via Azure Private DNS or the network platform",
                "do": [
                    "Internal or Azure-hosted names: Azure Private DNS zones linked to your virtual networks.",
                    "DHCP: import the Phase 7 export into the DHCP service your network team runs going forward, update the DNS server option, and only then deauthorise the old DHCP servers.",
                ],
                "pit": ["Devices with static DNS settings pointing at DC IP addresses."],
                "src": S("dns_private", "road"),
                "rec": [], "tools": [], "marker": "practical",
            },
        ],
    },
    {
        "id": "decommission",
        "title": "Decommission domain controllers and Windows Servers",
        "time": "1 day per DC + observation window",
        "deep": True,
        "goal": "All DCs demoted cleanly in a controlled order, no orphaned metadata, domain removed, remaining servers retired or without a domain dependency.",
        "lead": "POINT OF NO RETURN 2 is the last DC. Learn says never remove the AD DS role from a DC with DISM, and to avoid forced removal.",
        "steps": [
            {
                "t": "Observation window, health check and role placement",
                "check": "DCs powered off (not demoted) for the observation window set in the change record with no impact; then restarted, replication healthy, all five FSMO roles on the DC that goes last",
                "do": [
                    "Optional: power the DCs off (not demoted) for an observation window that covers your business cycle and ends well inside the tombstone lifetime from Phase 7, so the backups remain valid if you must restart them.",
                    "Power on, check `repadmin /replsummary` and `dcdiag`, then transfer (not seize) all FSMO roles with Move-ADDirectoryServerOperationMasterRole while the holder is healthy.",
                    "Learn: after a transfer the new holder waits for a successful inbound replication before acting.",
                    "Retire or unjoin remaining member servers first; a server left joined to a domain that disappears loses domain logons.",
                ],
                "pit": ["Seizing the RID master without need causes RID burn (Learn)."],
                "src": S("fsmo", "fsmo_ps"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Demote additional DCs, then the last DC",
                "check": "Each additional DC demoted without -ForceRemoval; last DC demoted with LastDomainControllerInDomain; dcpromo logs archived",
                "do": [
                    "Run `Uninstall-ADDSDomainController -WhatIf` first to see the effective settings. Once demotion starts it cannot be halted.",
                    "Demoting the last DC needs Enterprise Admins and removes the domain (and the forest if it is the last domain). Use `-LastDomainControllerInDomain`, `-RemoveApplicationPartitions` and `-IgnoreLastDnsServerForZone` only after DNS has moved.",
                    "Keep `%systemroot%\\debug\\dcpromo.log` and `dcpromoui.log`. Let the server reboot; Learn advises against overriding the reboot.",
                    "If the server will not be promoted again, remove the remaining AD DS, DNS and GPMC roles and features, then retire it.",
                ],
                "pit": ["Forced demotion leaves orphaned metadata and loses unreplicated changes; Learn names orphaned metadata as a root cause in a significant share of AD support cases."],
                "code": [("Health, FSMO transfer and demotion (preview with -WhatIf)", DC_DEMOTE)],
                "src": S("demote", "uninst_dc"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Clean up metadata if a DC was lost or forced",
                "check": "No NTDS Settings objects remain for removed DCs in Active Directory Sites and Services",
                "do": [
                    "Deleting the DC computer object in Active Directory Users and Computers (Windows Server 2008 or later RSAT) cleans up metadata automatically; in Sites and Services delete the NTDS Settings object first.",
                    "ntdsutil metadata cleanup is the command-line alternative.",
                ],
                "pit": [],
                "src": S("meta"),
                "rec": [], "tools": [], "marker": "official",
            },
        ],
    },
    {
        "id": "validate",
        "title": "Validate, document, troubleshoot and roll back",
        "time": "1–2 weeks",
        "goal": "Evidence that the tenant runs without AD, a complete runbook and records, and known answers for common failures.",
        "steps": [
            {
                "t": "Post-checks",
                "check": "Sync disabled, zero synced objects, zero active hybrid-joined devices, DNS on Azure, sign-ins and MFA healthy, licences intact",
                "do": [
                    "Run the read-only Graph post-check and compare with the Phase 1 baseline.",
                    "From a clean Entra-joined device, test sign-in, SSPR, Conditional Access, compliance, mail flow, file access and remote access.",
                    "Remove role assignments and PIM eligibility created only for the migration.",
                ],
                "pit": [],
                "code": [("Read-only post-checks", POSTCHECK)],
                "src": S("dirsync_off", "road"),
                "rec": [], "tools": ["maester"], "marker": "official",
            },
            {
                "t": "Document and hand over",
                "check": "Runbook, decision record, dependency register, wave logs, backup and export locations and the date the backups expire are filed",
                "do": [
                    "Record the date the DC backups pass their shelf life; after it, restoring the old domain is no longer possible.",
                    "Update operating procedures: user lifecycle via Entra ID / HR provisioning, group creation in the cloud, device provisioning with Autopilot.",
                ],
                "pit": [],
                "src": S("recover", "tsl"),
                "rec": [], "tools": [], "marker": "practical",
            },
            {
                "t": "Troubleshooting",
                "check": "Team can resolve each listed symptom from the runbook",
                "do": [
                    "PATCH returns 403: consent was granted to another app, or the role is not active. Grant the `*-OnPremisesSyncBehavior.ReadWrite.All` permission to the app you use and activate Hybrid Administrator in PIM.",
                    "Object still read-only after conversion: confirm `isCloudManaged = true` with GET and the audit event 'Change Source of Authority from AD to cloud'; check the sync client meets the minimum version.",
                    "AD edits of a converted object never reach the cloud: expected — sync skips the object (event 6956).",
                    "Converted a parent group but nested groups are still read-only: nested groups convert separately, bottom-up.",
                    "Mail-enabled group cannot be edited in the Entra admin center: manage it in Exchange Online.",
                    "Portal shows sync disabled but password hash sync 'enabled': Learn says this happens when sync is disabled before the client is uninstalled; it is cosmetic.",
                    "Cloud Sync agent still listed after uninstall: expected for about 10 days; delete the configuration to remove it sooner.",
                    "After sync-off, users cannot reach an old file server or app: it still depended on AD. Restore the service path (Entra Domain Services or a retained server) rather than re-enabling sync.",
                ],
                "pit": [],
                "src": S("gsoa_cfg", "usoa_cfg", "dirsync_off", "cs_config"),
                "rec": [], "tools": [], "marker": "official",
            },
            {
                "t": "Rollback per phase",
                "check": "Rollback table in the runbook is current and has an owner",
                "do": [
                    "Phases 1–3: no tenant-wide change; revert per workstream (device redeploy, `IsExchangeCloudManaged = false`, Conditional Access policy to report-only).",
                    "Phases 4–5: per-object SOA rollback as documented (remove cloud references, isCloudManaged = false, next sync run).",
                    "Phases 6–7: nothing to undo; monitoring, backups and exports are additive.",
                    "Phase 8: re-enabling sync is possible only after 72 hours and is not a tested rollback — the first point of no return.",
                    "Phase 9: point NS records back to the previous provider while it still answers; restore DHCP scopes from the export.",
                    "Phase 10: before the last DC is demoted, powered-off DCs can be restarted. After it, only a forest recovery from a backup within its shelf life is possible.",
                ],
                "pit": [],
                "src": S("usoa_cfg", "gsoa_cfg", "exch_soa", "dirsync_off", "recover"),
                "rec": [], "tools": [], "marker": "official",
            },
        ],
    },
]
