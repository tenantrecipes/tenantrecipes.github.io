"""Technical guide: patch Azure DevOps Server 25H2 to the latest documented security patch.
Checked against Microsoft Learn, the Azure DevOps Blog and the Microsoft Security Update Guide
(November 2026 CVRF) on 12 November 2026; practical, not lab-tested.
"""

SLUG = "patch-azure-devops-server-25h2"
TIER = "technical"
PUBLISHED = "2026-11-14"
VERIFIED = "2026-11-12"
UPDATED = "2026-11-14"
TITLE = "Patch Azure DevOps Server 25H2 to the latest security patch"
SHORT = "Patch Azure DevOps Server 25H2"
DESC = (
    "How to check the current Azure DevOps Server 25H2 build, take a consistent backup, "
    "install the latest documented cumulative security patch (Patch 9 as of 12 November 2026), "
    "verify the result and roll back from backup if the update fails. Documentation verified; "
    "not lab-tested. Items that could not be confirmed officially are marked not verified."
)
BADGE = "Microsoft Learn, Azure DevOps Blog and Security Update Guide checked; not lab-tested"
SRC_LABEL = "Checked primary sources"
TIME_NOTE = (
    "Time estimates are Tenant Recipes planning figures for a single application-tier server, "
    "not Microsoft numbers. Re-check the release notes, the patches blog and the Security Update "
    "Guide immediately before the window in case a later documented patch has appeared."
)
CTA_FIRST = "Start with what latest means today →"
TAGS = ("azure-devops", "patching", "on-premises")
RELATED = ("azure-devops-hardening-key-eater",)

INTRO = [
    "It is a Monday morning after Patch Tuesday. Someone in the change channel asks whether the "
    "on-premises Azure DevOps Server is current. The Administration Console still shows a mid-year "
    "build. That server holds the organisation's source code, pipelines, variable groups, service "
    "connections and the credentials those connections use to reach production. That combination "
    "makes it an attractive target: a weakness in the application tier can reach pipelines that "
    "already have a path into other systems. Once a vulnerability is public, the window to patch is "
    "measured in days, not quarters. Keeping this product current is a recurring duty, the same as "
    "for the operating system and SQL Server underneath it. The opening is a generic illustration, "
    "not a case study.",
    "This guide assumes a server already running Azure DevOps Server 25H2 — product version "
    "20.256.37327.3, installed under `C:\\Program Files\\Azure DevOps Server\\`. Items that could "
    "not be confirmed officially are marked not verified. Do not install a package that has no "
    "published release notes and SHA-256 hash.",
]

NAMING = (
    "Scope: on-premises Azure DevOps Server 25H2 application and data tiers you administer. "
    "Do not assume feature parity with Azure DevOps Services. Product UI labels change; prefer "
    "the linked Learn articles and the current release notes. Tenant Recipes is not affiliated "
    "with Microsoft. Sources checked on 12 November 2026; this procedure has not been lab-tested."
)

NOTICE = {
    "title": "What is not verified",
    "text": (
        "The community mapping of 20.256.37327.3 to Patch 5, and of Patch 9 to 20.256.37721.1, "
        "is not in Microsoft's 25H2 release notes. Whether MSRC's product names \"Azure DevOps "
        "Server\" and \"Azure DevOps Server 2025\" are always the same 25H2 family is not formally "
        "explained, though the Patch 8 and Patch 9 remediations point at the current release notes. "
        "It is not verified which public 25H2 patch, if any, contains the 20260304.1 fixed build "
        "named for CVE-2026-120783. MSRC lists Patch 10 as the fix for CVE-2026-85923 but publishes "
        "no download URL, release notes or SHA-256; as of 12 November 2026, Learn and the Azure "
        "DevOps Blog still end at Patch 9. A file is reachable at aka.ms/devopsserverpatch10 "
        "(devopsserverpatch10.exe), under a generic AzureDevOpsServer folder rather than the "
        "month-named 2026 folders used for Patch 8 and Patch 9 — not verified that this file is a "
        "published November 2026 security patch for 25H2. Do not install it until Microsoft "
        "publishes release notes and a SHA-256 hash for that exact package. Exact "
        "service-interruption behaviour of Patch 9 on a given topology is also not verified; this "
        "procedure has not been lab-tested by Tenant Recipes."
    ),
}

HISTORY = [
    (
        "2026-11-14",
        "Published technical guide: patch Azure DevOps Server 25H2 to the latest documented "
        "security patch; documentation verified, not lab-tested.",
    ),
]


def S(*keys):
    return [L[k] for k in keys]


L = {
    "notes": (
        "Azure DevOps Server release notes (Patch 9, 13 October 2026, including SHA-256)",
        "https://learn.microsoft.com/en-us/azure/devops/server/release-notes/azuredevopsserver?view=azure-devops",
    ),
    "octblog": (
        "October Patches for Azure DevOps Server",
        "https://devblogs.microsoft.com/devops/october-patches-for-azure-devops-server-4/",
    ),
    "patches_cat": (
        "Azure DevOps Blog: patches category",
        "https://devblogs.microsoft.com/devops/category/azure-devops-server/patches/",
    ),
    "sug": (
        "Microsoft Security Update Guide",
        "https://msrc.microsoft.com/update-guide",
    ),
    "nov_rn": (
        "November 2026 Security Update Guide release notes",
        "https://msrc.microsoft.com/update-guide/releaseNote/2026-Nov",
    ),
    "cve109467": (
        "CVE-2026-109467 — Azure DevOps Server remote code execution",
        "https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-109467",
    ),
    "cve112745": (
        "CVE-2026-112745 — Azure DevOps Server information disclosure",
        "https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-112745",
    ),
    "cve120783": (
        "CVE-2026-120783 — Azure DevOps Server elevation of privilege",
        "https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-120783",
    ),
    "cve85923": (
        "CVE-2026-85923 — Azure DevOps Server elevation of privilege",
        "https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-85923",
    ),
    "patch9": (
        "Official Patch 9 installer (aka.ms/devopsserverpatch9)",
        "https://aka.ms/devopsserverpatch9",
    ),
    "download": (
        "Azure DevOps Server download page",
        "https://learn.microsoft.com/en-us/azure/devops/server/download/azuredevopsserver?view=azure-devops",
    ),
    "lookup": (
        "Look up your Azure DevOps platform and version",
        "https://learn.microsoft.com/en-us/azure/devops/user-guide/lookup-platform-version?view=azure-devops",
    ),
    "console": (
        "Open the Administration Console",
        "https://learn.microsoft.com/en-us/azure/devops/server/admin/open-admin-console?view=azure-devops-server",
    ),
    "requirements": (
        "Setup and upgrade requirements",
        "https://learn.microsoft.com/en-us/azure/devops/server/requirements?view=azure-devops-server",
    ),
    "backup": (
        "Configure a backup schedule and plan",
        "https://learn.microsoft.com/en-us/azure/devops/server/admin/backup/config-backup-sched-plan?view=azure-devops-server",
    ),
    "upgrade": (
        "Upgrade to Azure DevOps Server",
        "https://learn.microsoft.com/en-us/azure/devops/server/upgrade/get-started?view=azure-devops-server",
    ),
    "restore": (
        "Restore data to the same location",
        "https://learn.microsoft.com/en-us/azure/devops/server/admin/backup/restore-data-same-location?view=azure-devops-server",
    ),
    "rc26": (
        "Azure DevOps Server RC (26H2) announcement",
        "https://devblogs.microsoft.com/devops/azure-devops-server-rc-26h2-is-now-available/",
    ),
    "community": (
        "Community version table (not official): FokkoVeegens/AzureDevOpsServerVersions",
        "https://github.com/FokkoVeegens/AzureDevOpsServerVersions",
    ),
}


def st(t, check, do, pit, src, rec=(), tools=(), guides=(), policies=(), marker="practical"):
    return {
        "t": t,
        "check": check,
        "do": do,
        "pit": pit,
        "src": S(*src),
        "rec": list(rec),
        "tools": list(tools),
        "guides": list(guides),
        "policies": list(policies),
        "marker": marker,
    }


PHASES = [
    {
        "id": "current",
        "title": "Where you are, and what “latest” means today",
        "time": "20–40 minutes",
        "deep": True,
        "goal": "You can name the generally available release, the latest documented patch and the November 2026 advisories, and you know what is still not verified.",
        "lead": "“Latest” is the last patch with published release notes and a SHA-256 hash, not a file that happens to be reachable.",
        "steps": [
            st(
                "Confirm the current GA release and the latest documented patch",
                "Notes record 25H2 as current GA and Patch 9 (13 October 2026) as the latest documented patch, or a later documented patch if one has appeared",
                [
                    "The generally available on-premises product is marketed as Azure DevOps Server. The Administration Console labels the current release 25H2. The Security Update Guide also lists Azure DevOps Server 2025; Patch 9 for that product is the same Patch 9 on the current release notes.",
                    "As of 12 November 2026 the latest documented patch is Patch 9, dated 13 October 2026. Official notes say it includes security-vulnerability fixes. A Microsoft employee confirmed on the October patch blog that patches are cumulative, so you can install Patch 9 without applying earlier patches first.",
                    "RC (26H2) is for a test deployment, not the recommended production target while 25H2 remains current GA.",
                    "Official notes do not publish the product version for each 25H2 patch. A community table maps 20.256.37327.3 to Patch 5 (11 June 2026) and Patch 9 to 20.256.37721.1. That mapping is not verified on Microsoft Learn. If the console shows 20.256.37327.3, you are on 25H2 and not on the latest documented patch.",
                ],
                [
                    "Do not treat the 26H2 release candidate as the production target while 25H2 remains current GA.",
                    "Do not treat the community build table as official. Use it only as a hint, and mark it not verified.",
                ],
                ("notes", "octblog", "lookup", "rc26", "community"),
                marker="official",
            ),
            st(
                "Read the November 2026 Azure DevOps Server advisories and what to do",
                "Change record lists the four CVEs, the documented fix for each, and the items still marked not verified",
                [
                    "On 10 November 2026 Microsoft published four Azure DevOps Server advisories. None were listed as publicly disclosed or under active exploitation at publication. What is vulnerable, and what to do:",
                    "CVE-2026-109467 — Remote code execution, Important, CVSS 9.9. A user who already has Project Reader access may be able to trigger unauthorized pipeline execution, which could run code on pipeline agents. Apply Patch 9 (aka.ms/devopsserverpatch9).",
                    "CVE-2026-112745 — Information disclosure, Important, CVSS 6.5. Server-side request forgery that can disclose credentials. Fixed in Patch 8. Apply Patch 9 (cumulative).",
                    "CVE-2026-120783 — Elevation of privilege, Important, CVSS 6.4. Microsoft states a successful attack could grant read access to the Elasticsearch search corpus and could tamper with or delete the search index, not the source data. MSRC names fixed build 20260304.1 but no patch number. Not verified which public 25H2 patch contains this build.",
                    "CVE-2026-85923 — Elevation of privilege, Important, CVSS 8.8. Authorization bypass over a network by an authorized attacker. MSRC names Patch 10 as the fix but publishes no download URL, release notes or SHA-256. Do not treat an undocumented binary as the November fix.",
                ],
                [
                    "A reachable aka.ms/devopsserverpatch10 file is not a published patch until Microsoft provides release notes and a SHA-256 hash for that exact package.",
                    "This page describes what is vulnerable and which documented patch to apply. It does not describe how to exploit any of these issues.",
                ],
                ("cve109467", "cve112745", "cve120783", "cve85923", "nov_rn", "patch9", "sug"),
                marker="official",
            ),
        ],
    },
    {
        "id": "check-version",
        "title": "Check the current version",
        "time": "15–30 minutes",
        "goal": "You have recorded the application-tier and data-tier versions and what is already installed.",
        "steps": [
            st(
                "Read the version from the Administration Console, the web About page, or the fallback DLL",
                "Application-tier and data-tier versions, and Installed Updates, are recorded before the window",
                [
                    "On the application-tier server, open Azure DevOps Server Administration Console (or run `TFSMgmt.exe` from the Tools directory).",
                    "Select Application Tier and read the application-tier and data-tier versions. Choose Installed Updates to see what was installed and when.",
                    "In the web UI: open the profile menu, then Help > About, or browse `https://<server>/<collection>/_home/About`.",
                    r"If the console is unavailable, Microsoft documents a fallback: open properties for `Microsoft.TeamFoundation.Admin.dll` in `C:\Program Files\Azure DevOps Server\Tools` and read File version on the Details tab.",
                ],
                [
                    "A mid-year build such as 20.256.37327.3 means you are on 25H2 but not on the latest documented patch. The exact patch-number mapping of that build is not verified on Microsoft Learn.",
                ],
                ("console", "lookup"),
                marker="official",
            ),
        ],
    },
    {
        "id": "prepare",
        "title": "Before you patch",
        "time": "1–2 hours plus the maintenance window",
        "goal": "Release notes and prerequisites are re-checked, a complete consistent backup exists, pipelines are drained, and a window is agreed.",
        "steps": [
            st(
                "Re-read the notes and confirm prerequisites immediately before the window",
                "Patch 9 notes (or a later documented patch) and the official requirements are reviewed the same day as the window",
                [
                    "Review the Patch 9 release notes and the October patch blog. Re-check both, plus the patches blog category and the Security Update Guide, immediately before the window in case a later documented patch has appeared.",
                    "Prerequisites: confirm the notes. For this release Microsoft documents Windows Server 2022 or 2025 (64-bit) and, for production, SQL Server 2022 or 2025, Azure SQL Database or Azure SQL Managed Instance. SQL Server on Linux is not supported. The official requirements page does not call out a separate .NET version as a server prerequisite. A same-release security patch typically does not change those requirements.",
                ],
                [
                    "Do not skip the same-day re-check: a later documented patch may have appeared after this page was verified on 12 November 2026.",
                ],
                ("notes", "octblog", "patches_cat", "sug", "requirements"),
                marker="official",
            ),
            st(
                "Take a complete backup and plan the window",
                "A complete, consistent backup of the configuration database and every project collection exists, and running pipelines are paused or drained",
                [
                    "In the Administration Console open Scheduled Backups and take an immediate backup of a complete, consistent set: the configuration database and every project collection database (and reporting databases and the reporting encryption key if you use reporting). This is the official recovery path if the update fails.",
                    "Plan a maintenance window: even when MSRC says a restart is not required, services can still be interrupted. Pause or drain running pipelines.",
                    "A consistent VM snapshot after the database backup is a practical second rollback option; Microsoft's documented recovery method is the database backup. If you have a test server, apply the same patch there first.",
                ],
                [
                    "A snapshot without a consistent database backup is not the documented recovery path.",
                    "Exact service-interruption behaviour of Patch 9 on a given topology is not verified; this procedure has not been lab-tested.",
                ],
                ("backup", "notes"),
                marker="practical",
            ),
        ],
    },
    {
        "id": "apply",
        "title": "Apply Patch 9",
        "time": "30–90 minutes",
        "goal": "The official Patch 9 installer is hash-verified and installed on every application-tier server (and the proxy, if used).",
        "lead": "These are the steps Microsoft documents for this patch family. The October blog does not publish a silent-install switch.",
        "steps": [
            st(
                "Download the official installer and verify the SHA-256 hash",
                "Get-FileHash SHA-256 of the downloaded file matches the official hash in the release notes",
                [
                    "Download the official installer from aka.ms/devopsserverpatch9. The file name in the official hash table is `devopsserverpatch9`.",
                    "Verify the SHA-256 hash against the release notes before you run anything: `8860146214BEC8D3BA685F79058EC88B735E4858569FE35477AC364CCFFFF875`.",
                    r"On Windows: `Get-FileHash -Algorithm SHA256 .\devopsserverpatch9.exe`. Do not install a file whose hash does not match.",
                ],
                [
                    "Do not install a package that has no published release notes and SHA-256 hash, including a file reached via aka.ms/devopsserverpatch10 until those exist for that exact package.",
                ],
                ("patch9", "notes"),
                marker="official",
            ),
            st(
                "Run the installer on each application-tier server and confirm it with CheckInstall",
                "CheckInstall reports the patch as installed on every application-tier server, and on the proxy if you use one",
                [
                    "Run the official installer on each application-tier server, typically with administrative rights. Complete any prompts.",
                    "If the Configuration Center opens, finish its readiness checks rather than cancelling.",
                    "If you use Azure DevOps Server Proxy, Microsoft says the proxy must be updated as well.",
                    "Verify with `devopsserverpatch9.exe CheckInstall`.",
                    "Full version upgrade (for example 2022.2 to 25H2, or later 25H2 to a future RTW): download the official EXE or ISO from the download page, run the installer, then use the Configuration Center upgrade wizard, after a complete database backup. Do not use the 26H2 RC on production unless you have accepted release-candidate risk.",
                ],
                [
                    "The October blog does not publish a silent-install switch — do not invent one.",
                    "If CheckInstall fails, collect the log, confirm the hash, and check Event Logs — do not rerun the installer in a loop.",
                ],
                ("notes", "octblog", "download", "upgrade", "rc26"),
                marker="official",
            ),
        ],
    },
    {
        "id": "verify",
        "title": "Verify afterwards",
        "time": "30–60 minutes",
        "goal": "The console, Installed Updates and the web About page show the new update, and core services work again.",
        "steps": [
            st(
                "Confirm the patch is installed and the collections are healthy",
                "CheckInstall, Administration Console and the web About page show the new update; collections, portal sign-in, agents and a test pipeline work",
                [
                    "CheckInstall should report the patch as installed.",
                    "Administration Console > Application Tier and Installed Updates should show the new update, and the web About page should no longer show only the pre-patch build.",
                    "Confirm that every project collection comes online, the portal signs in, self-hosted agents reconnect, a simple test pipeline succeeds, and Code Search, extensions, service connections and (if used) reporting still work.",
                ],
                [
                    "The exact post-patch build number for Patch 9 is not published in the official 25H2 notes. Record what you see; do not fail the check only because it does not match a community table.",
                ],
                ("console", "lookup", "notes"),
                marker="practical",
            ),
        ],
    },
    {
        "id": "rollback",
        "title": "Rollback and troubleshooting",
        "time": "As needed",
        "goal": "If the update fails, you restore from the pre-window backup using the documented path rather than uninstalling.",
        "steps": [
            st(
                "Restore the pre-window databases — there is no documented uninstall switch",
                "If rollback is needed, databases are restored with the official same-location procedure after TFSServiceControl quiesce",
                [
                    "Microsoft does not document an uninstall switch for these patches. The supported recovery is to restore the databases you backed up before the window.",
                    r"Follow Restore data to the same location: `TFSServiceControl quiesce` from `C:\Program Files\Azure DevOps Server\Tools`, take the live databases offline and rename them, then run the Restore Databases wizard from Scheduled Backups.",
                    "After the restore, Microsoft documents updating service accounts if needed, optionally rebuilding the warehouse, clearing the application-tier file cache, and returning the server to service with `TFSServiceControl unquiesce`.",
                    "Reverting consistent application-tier and SQL snapshots is a practical last resort only.",
                    "If CheckInstall fails, collect the log, confirm the hash, and check Event Logs — do not rerun the installer in a loop.",
                ],
                [
                    "Do not treat a snapshot revert as the documented recovery path if a consistent database backup exists.",
                ],
                ("restore", "backup"),
                marker="official",
            ),
        ],
    },
    {
        "id": "keep-current",
        "title": "Keep the server current",
        "time": "Ongoing, around each Patch Tuesday",
        "goal": "A monthly reminder is in place to re-check notes, the patches blog and the Security Update Guide, and to install only hash-verified cumulative patches.",
        "steps": [
            st(
                "Set a monthly reminder and install only documented, hashed cumulative patches",
                "A recurring reminder exists, and the two November CVEs that still lack a clear hashed package are on the re-check list",
                [
                    "Set a monthly reminder around Microsoft's Patch Tuesday. Read the release notes and the patches blog category.",
                    "Check the Security Update Guide for new Azure DevOps Server CVEs and the fixed build they name.",
                    "Download only from Microsoft's short links or the official blog, verify the published SHA-256, and install the latest cumulative documented patch in a planned window with a fresh backup.",
                    "Re-check CVE-2026-85923 and CVE-2026-120783 until Microsoft publishes a clear, hashed package that names those fixes.",
                ],
                [
                    "Do not install an undocumented binary just because an aka.ms short link resolves.",
                ],
                ("notes", "patches_cat", "sug", "cve85923", "cve120783"),
                marker="practical",
            ),
        ],
    },
]
