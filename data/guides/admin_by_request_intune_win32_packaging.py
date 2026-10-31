"""Technical guide: packaging the Admin By Request Windows client with the Microsoft Win32 Content Prep Tool (IntuneWinAppUtil.exe)
and deploying it as an Intune Win32 app, end to end: prerequisites, tool and folder layout, packaging, Program/Requirements/Detection,
assignments, verification, version ownership (Intune supersedence vs vendor Auto-Update), troubleshooting and rollback.
Companion to the pillar guide admin-by-request-endpoint-privilege, which covers the why, the portal and the policy design.
Fact-checked against docs.adminbyrequest.com, Microsoft Learn and the microsoft/Microsoft-Win32-Content-Prep-Tool repository on 2026-10-31.
Text in `backticks` renders as <code>. 'rec' = recipe ids, 'tools' = tools ids, 'sec' = cyber ids, 'guides' = other guide slugs.
Not sponsored: Tenant Recipes has no commercial relationship with Admin By Request (see NOTICE)."""

SLUG = "admin-by-request-intune-win32-packaging"
TIER = "technical"  # pillar | technical (see GUIDES.md)
PUBLISHED = "2026-10-31"
TITLE = "Package Admin By Request for Intune: IntuneWinAppUtil.exe to a production Win32 app"
SHORT = "Admin By Request: Intune Win32 packaging"
DESC = ("Technical deep dive: wrap the Admin By Request Windows client with the Win32 Content Prep Tool (IntuneWinAppUtil.exe) and ship it as an Intune Win32 app. "
        "Folder layout, exact packaging command, install and version-independent uninstall commands, file-version detection, requirements, return codes, "
        "pilot-to-wave assignments, verification, Intune supersedence vs vendor Auto-Update, IME logs, error codes and rollback.")
VERIFIED = "2026-10-31"
BADGE = "fact-checked against Admin By Request docs, Microsoft Learn and the Content Prep Tool repo"
SRC_LABEL = "Official sources"
TIME_NOTE = ("Time estimates are our planning figures for one packager working on an Intune tenant with a few hundred to a few thousand Windows devices, not vendor numbers. "
             "The packaging itself takes minutes; the time goes into the pilot and in deciding who owns client versions.")
CTA_FIRST = "Start with phase 1 →"

NOTICE = {
    "title": "Editorial note: not sponsored",
    "text": ("Tenant Recipes has no commercial relationship with Admin By Request; we receive no payment, commission or free licences, and the vendor has not reviewed this page. "
             "This is the hands-on companion to our pillar guide on removing local admin rights with Admin By Request, which carries the full editorial note and the policy design. "
             "Every step below links the vendor or Microsoft page it is based on."),
}

INTRO = [
    "The pillar guide explains why and how to remove standing local admin rights with Admin By Request. This guide does one thing in depth: it takes the tenant-specific Windows MSI "
    "from the portal, wraps it with Microsoft's Win32 Content Prep Tool (`IntuneWinAppUtil.exe`) and turns it into an Intune Win32 app that installs silently, detects correctly "
    "after every update, uninstalls cleanly whatever version is on the device, and can be rolled out in rings.",
    "Most failed Admin By Request rollouts in Intune fail on three details, not on the product: the default MSI product-code detection, the pre-filled product-code uninstall "
    "command, and running Intune and the vendor's Auto-Update side by side. Each of those has its own step below.",
]
NAMING = ("Scope: Windows 10/11 workstations enrolled in Intune, using the Admin By Request Workstation MSI. The Server edition is a separate MSI and a separate Intune app with the same pattern. "
          "macOS is covered in the pillar guide. Nothing on this page has been lab-tested by us; it is verified against vendor and Microsoft documentation. "
          "Tenant Recipes is not affiliated with Admin By Request or Microsoft.")


def S(*keys):
    return [L[k] for k in keys]


L = {
    # Admin By Request
    "abr_intune": ("Admin By Request: Working with Intune (Windows Win32 package)", "https://docs.adminbyrequest.com/integrations/intune.htm"),
    "abr_win_inst": ("Admin By Request: Windows client install / uninstall / upgrade", "https://docs.adminbyrequest.com/endpoints/Windows/install.htm"),
    "abr_large": ("Admin By Request: Updating client software for large enterprises", "https://docs.adminbyrequest.com/support/tech-notes/updating-large-orgs.htm"),
    "abr_tenant": ("Admin By Request: Tenant Settings (Auto-Update)", "https://docs.adminbyrequest.com/portal/settings/tenant.htm"),
    "abr_lic": ("Admin By Request: Licensing", "https://docs.adminbyrequest.com/licensing.htm"),
    "abr_ui": ("Admin By Request: Windows client user interface (Connectivity, Diagnostics)", "https://docs.adminbyrequest.com/endpoints/Windows/ui.htm"),
    "abr_net": ("Admin By Request: IP addresses and API URLs for proxies and firewalls", "https://docs.adminbyrequest.com/MicroContent/resources/MicroContent/micro-faq-connectivity/what-ip-addresses-do-we-allow-in-our-proxy-and-firewall.htm"),
    "abr_pol": ("Admin By Request: Policies for Windows (registry overrides)", "https://docs.adminbyrequest.com/endpoints/Windows/policies.htm"),
    "abr_audit": ("Admin By Request: Auditlog", "https://docs.adminbyrequest.com/portal/auditlog.htm"),
    # Content Prep Tool
    "cpt_repo": ("Microsoft Win32 Content Prep Tool (GitHub repository and README)", "https://github.com/microsoft/Microsoft-Win32-Content-Prep-Tool"),
    "cpt_rel": ("Microsoft Win32 Content Prep Tool releases", "https://github.com/microsoft/Microsoft-Win32-Content-Prep-Tool/releases"),
    # Microsoft Learn
    "ms_prep": ("Prepare a Win32 app to be uploaded to Intune", "https://learn.microsoft.com/en-us/intune/intune-service/apps/apps-win32-prepare"),
    "ms_add": ("Add and assign Win32 apps to Intune", "https://learn.microsoft.com/en-us/intune/intune-service/apps/apps-win32-add"),
    "ms_win32": ("Win32 app management in Intune (availability, restart grace period, Delivery Optimization)", "https://learn.microsoft.com/en-us/intune/app-management/deployment/win32"),
    "ms_super": ("Add Win32 app supersedence", "https://learn.microsoft.com/en-us/intune/app-management/deployment/configure-win32-supersedence"),
    "ms_assign": ("Assign apps to groups with Intune", "https://learn.microsoft.com/en-us/intune/app-management/deployment/assign-groups"),
    "ms_ime": ("Intune Management Extension for Windows", "https://learn.microsoft.com/en-us/intune/device-management/tools/management-extension-windows"),
    "ms_ts_win32": ("Troubleshoot Win32 app installations", "https://learn.microsoft.com/en-us/intune/app-management/deployment/troubleshoot-win32"),
    "ms_ts_app": ("Troubleshooting app installation issues with Intune", "https://learn.microsoft.com/en-us/troubleshoot/mem/intune/app-management/troubleshoot-app-install"),
    "ms_err": ("Intune app installation error reference", "https://learn.microsoft.com/en-us/troubleshoot/mem/intune/app-management/app-install-error-codes"),
    "ms_flow": ("Develop and deliver a working Win32 app via Intune (IME flow and .intunewin contents)", "https://learn.microsoft.com/en-us/troubleshoot/mem/intune/app-management/develop-deliver-working-win32-app-via-intune"),
    "ms_rbac": ("Role-based access control with Intune (built-in roles)", "https://learn.microsoft.com/en-us/intune/fundamentals/role-based-access-control/overview"),
    "ms_monitor": ("Monitor app information and assignments", "https://learn.microsoft.com/en-us/intune/app-management/monitor-assignments"),
    "ms_laps": ("Windows LAPS overview", "https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview"),
}

PILLAR = "admin-by-request-endpoint-privilege"

PHASES = [
 {
  "id": "prereq", "title": "Prerequisites: devices, roles and the version-ownership decision", "time": "Half a day", "deep": False,
  "goal": "Target devices can receive Win32 apps, the packager has exactly the Intune rights needed, the Admin By Request tenant is configured, and you have decided whether Intune or Auto-Update owns client versions.",
  "lead": "The agent applies tenant settings, including `Revoke admin rights`, the moment it connects. Packaging comes after the portal and policy work, not before it.",
  "steps": [
   {"t": "Confirm the devices can take a Win32 app",
    "check": "Every target device is Entra joined, hybrid joined or Entra registered, enrolled in Intune, runs a supported Pro, Enterprise or Education edition, and its user holds an Intune licence",
    "do": ["Win32 apps are delivered by the Intune Management Extension (IME). Intune installs the IME automatically the first time a Win32 app, PowerShell script or similar workload is assigned, so you do not deploy it yourself.",
           "Admin By Request's own Intune walkthrough assumes Entra joined, MDM-enrolled devices in a device group and users with an Intune-capable licence (it uses EMS E3 as its example).",
           "The client is a Windows Installer package and installs silently, which is what Intune requires: interactive installs are not supported for Win32 apps.",
           "Workstation and Server are different MSIs. The Workstation MSI will not install on Windows Server, so multi-session hosts and servers need their own app built from the Server MSI."],
    "pit": ["Devices beyond your Admin By Request licence count never show up in the portal inventory, even when Intune reports a successful install. Check the seat count before a large wave."],
    "rec": ["intune-compliance-baseline"], "tools": [], "src": S("ms_add", "ms_ime", "abr_intune", "abr_win_inst", "abr_lic"),
    "marker": "official"},
   {"t": "Give the packager least-privilege Intune rights",
    "check": "The account that creates the app holds the Intune built-in role Application Manager (or a custom role with Win32 app and supersedence rights), not Global Administrator, and uses PIM where available",
    "do": ["The Entra role Intune Administrator has full read/write in Intune. For app packaging, the Intune built-in role Application Manager is enough: it manages apps, reads device information and views configuration profiles.",
           "Microsoft adds the Win32 app supersedence permission to Application Manager, so the same role covers the update path in phase 7.",
           "If you use scope tags, tag the app so only the endpoint team can change it. The uninstall and install command fields run as SYSTEM on every targeted device; whoever can edit them effectively has admin rights on the fleet.",
           "On the Admin By Request side you need a portal login that can open the Download menu; the downloaded installer is licensed to your tenant only."],
    "pit": ["Microsoft warns that harmful commands can be passed through the install and uninstall fields. Treat edit rights on this app like tier-1 admin rights and review its audit trail."],
    "rec": ["pim-least-privilege-daily-ops"], "tools": [], "src": S("ms_rbac", "ms_super", "ms_add", "abr_win_inst"),
    "marker": "official"},
   {"t": "Decide who owns client versions before you package",
    "check": "One written decision per platform: either Intune owns versions (Auto-Update for Windows Workstation off) or Auto-Update owns them (Intune app used for new installs only)",
    "do": ["The vendor recommends that large estates update the client with their own deployment tool (Intune, Configuration Manager, Jamf) rather than Auto-Update, because that gives control over version targeting, schedules, rollback and compliance reporting.",
           "Auto-Update is set per platform under `Settings > Tenant Settings > Auto-Update > WINDOWS WORKSTATION`. The vendor suggests using it temporarily, for example two to four weeks to catch off-network devices or for an emergency fix, then switching it off again.",
           "Never run both on the same devices. The vendor's own Intune page says so explicitly; running both causes version flapping and detection failures.",
           "Finish the portal work first: SSO, Entra ID Connector, global settings and persona sub-settings (pillar guide phases 2–5)."],
    "pit": ["Auto-Update is on by default. If Intune is going to own versions, switch it off before the first wave, not after the first surprise upgrade."],
    "rec": [], "tools": [], "guides": [PILLAR], "src": S("abr_large", "abr_intune", "abr_tenant"),
    "marker": "official"},
  ]},

 {
  "id": "tool", "title": "Get the Content Prep Tool and lay out the packaging folders", "time": "30 minutes", "deep": False,
  "goal": "A current IntuneWinAppUtil.exe lives in its own tools folder, and every client version has its own clean source and output folder.",
  "steps": [
   {"t": "Download and verify IntuneWinAppUtil.exe",
    "check": "`IntuneWinAppUtil.exe -v` on the packaging machine prints the current release from the GitHub repository (1.8.7 at the time of writing)",
    "do": ["Download the tool from Microsoft's `microsoft/Microsoft-Win32-Content-Prep-Tool` repository on GitHub (the release ZIP or `IntuneWinAppUtil.exe` from the repository root). The ZIP contains the tool, the licence terms, a readme and release notes.",
           "The latest release when we checked was v1.8.7 (published 13 August 2025, adding FIPS compliance). The tool needs .NET Framework 4.7.2.",
           "`IntuneWinAppUtil.exe -v` prints the version (available from 1.8.2); `-h` prints usage. Run without parameters, it prompts for each value interactively.",
           "Always package with the latest release: the Intune admin center warns when a package was made with an older version of the tool."],
    "pit": ["Read and keep the licence terms; using the tool means accepting them. Download only from the Microsoft repository, never from a mirror or a blog attachment, because you will run it on a machine that holds licensed installers."],
    "rec": [], "tools": [], "src": S("cpt_repo", "cpt_rel", "ms_prep", "ms_add"),
    "marker": "official"},
   {"t": "Separate tool, source and output folders",
    "check": "The tool sits outside every source folder, each source folder contains only the Admin By Request MSI, and the output folder is not inside the source folder",
    "do": ["The tool compresses every file and subfolder of the `-c` setup folder into the package. Microsoft explicitly tells you to keep the tool itself out of that folder, and the README adds that only the setup files for this app should be there.",
           "A layout that scales across releases: `C:\\Packaging\\Tools\\IntuneWinAppUtil.exe`, `C:\\Packaging\\AdminByRequest\\<full version>\\source\\` for the MSI, and `C:\\Packaging\\AdminByRequest\\<full version>\\output\\` for the result.",
           "The vendor's walkthrough puts the MSI, the tool and the output in one folder (`C:\\ABRInstall`). That works once, but the package then contains the tool, and a second run also packs the first `.intunewin`. Use separate folders instead."],
    "pit": ["Files you need at install time (for example a wrapper script) belong in a subfolder of the source folder and are referenced by relative path. Admin By Request needs nothing extra: the MSI carries the tenant licence."],
    "rec": [], "tools": [], "src": S("ms_prep", "cpt_repo", "abr_intune"),
    "marker": "practical"},
  ]},

 {
  "id": "package", "title": "Package the MSI into an .intunewin file", "time": "30 minutes", "deep": True,
  "goal": "You hold a .intunewin built from the tenant's current Workstation MSI, you know its full four-part version, and you have checked what is inside.",
  "steps": [
   {"t": "Download the MSI and record its full four-part version",
    "check": "The MSI from the portal's Download menu is in the version's source folder, and its four-part version (for example `8.5.1.0`) is recorded in the change ticket",
    "do": ["Download the Windows Workstation MSI from the portal's Download menu. It is signed with your tenant's licence; devices installed from it appear in your inventory only.",
           "The portal shows only major.minor (for example 8.5). Read the full version from the file: right-click, `Properties > Details`, and look in the `Comments` field. Detection and the Intune app version both need all four parts.",
           "Keep the downloaded file name exactly as it is. Portal names contain spaces and the version, and the install command must name the MSI exactly as it was packaged. There is no file called `AdminByRequest.msi` in any portal download.",
           "Optional, for your records only: the vendor documents a short PowerShell snippet that reads `ProductCode`, `ProductVersion` and `UpgradeCode` from the MSI through the `WindowsInstaller.Installer` COM object. Neither the install nor the uninstall command needs the product code."],
    "pit": ["Do not rename the MSI to something without spaces 'to make it easier'. It works only if you also change the install command, and it breaks the link between the file name and the version you documented."],
    "rec": [], "tools": [], "src": S("abr_intune", "abr_large", "abr_win_inst"),
    "marker": "official"},
   {"t": "Run IntuneWinAppUtil.exe with exact, quoted paths",
    "check": "The output folder contains a `.intunewin` named after the MSI, and the tool reported no errors",
    "do": ["From an elevated PowerShell prompt, on one line: `& \"C:\\Packaging\\Tools\\IntuneWinAppUtil.exe\" -c \"C:\\Packaging\\AdminByRequest\\8.5.1.0\\source\" -s \"Admin By Request 8.5 Workstation.msi\" -o \"C:\\Packaging\\AdminByRequest\\8.5.1.0\\output\" -q` (replace the version and file name with yours).",
           "`-c` is the setup folder, `-s` the setup file inside it, `-o` the output folder. `-q` runs without prompts, overwrites an existing output file and creates the output folder if needed; `-qq` does the same with no console output, which suits a build pipeline.",
           "For an MSI the tool reads the information Intune needs from the package, so the Intune portal can pre-fill several fields after upload.",
           "The vendor's own example runs from the folder as `.\\IntuneWinAppUtil.exe -c \"C:\\ABRInstall\" -s \"Admin By Request 8.5 Workstation.msi\" -o \"C:\\ABRInstall\"`; the only difference above is the separate folders."],
    "pit": ["'The folder you specified cannot be accessed' means `-c` points at the MSI instead of its folder.",
            "The vendor lists two more classic causes: a prompt that is not elevated, and a command that was broken across lines when pasted. Paths with spaces must be quoted."],
    "rec": [], "tools": [], "src": S("cpt_repo", "ms_prep", "abr_intune"),
    "marker": "official"},
   {"t": "Inspect the package and store it like the installer",
    "check": "A copy of the .intunewin opened as a ZIP shows a `Contents` and a `Metadata` folder, and the file is stored with restricted access next to the MSI",
    "do": ["Microsoft notes that a `.intunewin` is a ZIP: copy it, rename the copy to `.zip` and open it. You will find `Contents` (the encrypted installer) and `Metadata` (including the detection XML the tool generated).",
           "Check the size: it should be roughly that of the MSI. A package that is much larger usually contains the tool or an older package by mistake.",
           "The README warns that the `.intunewin` contains the encrypted setup files together with the information to decrypt them. Store it with the same access controls as the tenant-licensed MSI, not on a public share."],
    "pit": ["Inspect a copy, never the file you upload."],
    "rec": [], "tools": [], "src": S("ms_flow", "cpt_repo"),
    "marker": "official"},
  ]},

 {
  "id": "app", "title": "Create the Win32 app: information, program and requirements", "time": "1 hour", "deep": True,
  "goal": "The Intune app installs the MSI silently in system context, uninstalls any installed version, and only targets devices that can run the Workstation client.",
  "lead": "Intune pre-fills several fields from the MSI metadata. Two of those defaults are wrong for Admin By Request; this phase replaces them.",
  "steps": [
   {"t": "Upload the package and fill in app information",
    "check": "The app exists under `Apps > Windows` as a Windows app (Win32) with a unique name, publisher, and the full four-part version as app version",
    "do": ["In the Intune admin center go to `Apps > All Apps > Create` (or `Apps > Windows > Add`), choose `Windows app (Win32)` and select the `.intunewin` as app package file.",
           "The vendor's values: Name `Admin By Request Workstation`, Publisher `Admin By Request`, App Version the full version you recorded (for example `8.5.1.0`).",
           "App names should be unique; if two apps share a name, only one shows in the Company Portal. If you keep several versions side by side during an update, put the version in the name.",
           "Add an Information URL, an owner (the endpoint team) and a note with the change ticket. The Company Portal shows the description and URL to users."],
    "pit": ["Turn on `Show this as a featured app` only if you also publish it as Available; for a Required security agent it adds nothing."],
    "rec": [], "tools": [], "src": S("abr_intune", "ms_add"),
    "marker": "official"},
   {"t": "Set install and uninstall commands, context and restart behaviour",
    "check": "Install command is `msiexec /i \"<exact file name>.msi\" /qn`, the uninstall command is the vendor's `Get-Package` PowerShell line, install behaviour is System, and `Allow available uninstall` is No",
    "do": ["Install command: `msiexec /i \"Admin By Request 8.5 Workstation.msi\" /qn`, using the exact packaged file name in quotes. The vendor's generic scripted form is `msiexec.exe /I \"<file>.msi\" /QN`; Windows Installer switches are not case-sensitive.",
           "Uninstall command: replace Intune's pre-filled `msiexec /x \"{ProductCode}\" /qn` with `powershell.exe -command \"Get-Package -Name 'Admin By Request Workstation' | Uninstall-Package -AllVersions -Force\"`. The product code belongs to one exact release, so the pre-filled command stops working as soon as a device has been upgraded; the PowerShell line removes whichever version is installed. For the Server app, replace `Workstation` with `Server`.",
           "Install behaviour: System. The vendor's example sets device restart behaviour to `App install may force a device restart`; Microsoft documents that with this option a hard-reboot return code gives the user a 120-minute restart notice and a soft-reboot code only a notification. If you prefer an explicit grace period, choose `Determine behavior based on return codes` and set the restart grace period on the assignment.",
           "Set `Allow available uninstall` to No: users must not be able to remove their own privilege-management agent from the Company Portal.",
           "Keep the default installation time (60 minutes) and the default return codes Intune adds; the client needs nothing special."],
    "pit": ["Microsoft notes that `powershell.exe` in these fields starts a 32-bit PowerShell, and that environment variables are not expanded in the uninstall command. Use the vendor's command as documented and test it on a pilot device rather than 'improving' it.",
            "`wmic product ... call uninstall` scripts no longer work on Windows 11 25H2, where WMIC is not present. The vendor has replaced them with the PowerShell form above."],
    "rec": [], "tools": [], "src": S("abr_intune", "abr_win_inst", "ms_add", "ms_win32"),
    "marker": "official"},
   {"t": "Set requirements: architecture and minimum OS",
    "check": "Requirements match the vendor's guidance (x64, minimum Windows 10 1607) or a stricter floor that reflects your supported Windows versions, and Arm devices are handled deliberately",
    "do": ["The vendor's Intune walkthrough sets `Operating system architecture` to x64 and `Minimum operating system` to Windows 10 1607.",
           "You can raise the minimum OS to the oldest Windows release you still support. That keeps unsupported devices from receiving the agent, but it also means they keep standing admin rights; report them rather than silently skipping them.",
           "The vendor states that the client runs on x86, x64 and ARM. Intune Win32 apps support 32-bit, 64-bit and ARM64 requirements. If you have Arm devices, check which installer the portal provides for them and pilot before you add ARM64 to the requirement."],
    "pit": ["A requirement that does not match shows the device as 'Not applicable', not 'Failed'. Include the Not applicable count in your rollout report so excluded devices are visible."],
    "rec": [], "tools": [], "src": S("abr_intune", "abr_win_inst", "ms_add", "ms_win32"),
    "marker": "official"},
  ]},

 {
  "id": "detect", "title": "Detection rule, dependencies and supersedence", "time": "30 minutes", "deep": True,
  "goal": "Intune detects the client by file version so that a vendor or Intune upgrade never makes the app look missing, and the first app has no dependency or supersedence baggage.",
  "steps": [
   {"t": "Detect AdminByRequest.exe by file version, never by MSI product code",
    "check": "One manual detection rule of type File: path `C:\\Program Files (x86)\\FastTrack Software\\Admin By Request`, file `AdminByRequest.exe`, detection method String (version), operator Greater than or equal to, value the full four-part version",
    "do": ["Choose `Manually configure detection rules`, rule type `File`, and enter the path and file name above.",
           "Detection method `String (version)`, operator `Greater than or equal to`, value the full version from phase 3, for example `8.5.1.0`. The vendor stresses the four parts: `8.5.1` does not match where `8.5.1.0` does.",
           "Greater than or equal to is deliberate: after an upgrade by Auto-Update or a newer package, the rule still matches and Intune leaves the device alone.",
           "Do not use the MSI rule type. Its product code changes with every release, so after an upgrade Intune reports the app as not installed and retries the older package on every evaluation cycle."],
    "pit": ["The path is literal and contains no environment variables, so the `Associated with a 32-bit app on 64-bit clients` toggle does not change the result here.",
            "Detection runs in the IME on its own schedule. For Required apps, Intune offers the app again within about 24 hours when detection fails, so a wrong rule shows up as a daily reinstall loop."],
    "rec": [], "tools": [], "src": S("abr_intune", "ms_add"),
    "marker": "official"},
   {"t": "Leave dependencies and supersedence empty for the first version",
    "check": "The first Admin By Request app has no dependencies and supersedes nothing, and a reviewer has checked every tab on Review + create",
    "do": ["The vendor leaves both tabs empty: the client depends on no other Win32 app.",
           "Supersedence is added later, on the next version's app, if Intune owns client versions (phase 7).",
           "On `Review + create`, check the install command against the uploaded file name, the uninstall command, the detection value and the architecture before you select Create."],
    "pit": ["If you later make another app depend on this one, remember that Win32 apps in a dependency relationship cannot be deleted until the relationship is removed."],
    "rec": [], "tools": [], "src": S("abr_intune", "ms_add"),
    "marker": "official"},
  ]},

 {
  "id": "assign", "title": "Assign: pilot device group, then waves", "time": "1–3 weeks", "deep": False,
  "goal": "The app reaches a pilot device group first, then one wave group at a time, as Required, with predictable restart behaviour and no user-controlled uninstall.",
  "steps": [
   {"t": "Assign Required to a pilot device group",
    "check": "The app is assigned with the Required intent to a pilot device group of 20–50 devices spanning all personas, and nothing else is assigned yet",
    "do": ["The vendor's walkthrough assigns the app as Required to a device group (its example is called `ABR Installation Dep`). Device targeting with System context installs whether or not a user is signed in.",
           "Microsoft warns that a user-targeted Win32 app that needs admin rights fails for standard users. Device groups avoid that class of problem entirely for a system agent.",
           "Use Required for the agent. Microsoft documents that apps installed through `Available for enrolled devices` are not reinstalled automatically if they are removed; that is the opposite of what you want for privilege management.",
           "You can add the group as Available in addition, so IT can trigger an install from the Company Portal on a specific device, but Required stays the primary assignment."],
    "pit": ["Pick pilot devices whose users actually elevate things (developers, engineers, field staff). A pilot of IT laptops proves only that the MSI installs."],
    "rec": [], "tools": [], "guides": [PILLAR], "src": S("abr_intune", "ms_add", "ms_win32", "ms_assign"),
    "marker": "official"},
   {"t": "Tune notifications, restart grace and delivery",
    "check": "End-user notifications, availability, deadline and (if used) the restart grace period are set on each assignment, and Delivery Optimization priority is chosen",
    "do": ["Per assignment you can set end-user notifications, an availability time and an installation deadline (as soon as possible or a specific date and time).",
           "The restart grace period appears only when the program's restart behaviour is `Determine behavior based on return codes` or `Intune will force a mandatory device restart`. Its default is 1,440 minutes, with a countdown dialog 15 minutes before the restart by default.",
           "Set Delivery Optimization priority to background for waves; the package is small and there is no need to compete with user traffic."],
    "pit": ["`Show all toast notifications` for a security agent invites tickets. Choose `Show toast notifications for computer restarts`, and tell users beforehand through your normal change communication."],
    "rec": [], "tools": [], "src": S("ms_win32", "ms_add"),
    "marker": "official"},
   {"t": "Roll out in waves by device group",
    "check": "Each wave is a separate device group added to the same app, with a go/no-go based on install success, Not applicable count and elevation tickets from the previous wave",
    "do": ["Add one wave group at a time to the existing assignment instead of creating copies of the app, so reporting stays in one place.",
           "Before each wave, check in the Admin By Request portal that the licence count covers the wave and that the pilot's pre-approvals are in place (pillar guide phases 5 and 7).",
           "Exclude kiosk, lab or break-glass devices with an Excluded group on the assignment if they must not get the agent."],
    "pit": ["If Autopilot provisioning includes the agent, decide deliberately whether it is a blocking app in the Enrollment Status Page; we leave it non-blocking so a portal or network issue cannot stall provisioning."],
    "rec": ["autopilot-device-preparation-entra-join"], "tools": [], "guides": [PILLAR], "src": S("ms_add", "ms_assign", "abr_lic"),
    "marker": "practical"},
  ]},

 {
  "id": "verify", "title": "Verify the install end to end", "time": "1 hour per wave", "deep": False,
  "goal": "For a sample of devices you can prove four things: Intune says Installed, the agent runs, it talks to the portal, and an elevation is audited.",
  "steps": [
   {"t": "Check Intune status per device, not on the overview",
    "check": "For the sample devices, `Devices > <device> > Managed Apps` shows Admin By Request Workstation as Installed",
    "do": ["The vendor points out that the app overview in Intune may lag; use the device-level Managed Apps view for reliable results.",
           "For a user's device, `Troubleshoot + support` shows the managed apps with their install status and failure details.",
           "To speed up a test device: in the Company Portal choose `Settings > Sync`, which triggers both an MDM and an IME check-in, or restart the `IntuneManagementExtension` service. Without that, the IME checks for new or changed apps every 8 hours."],
    "pit": ["A device shown as Pending for hours usually has not checked in with the IME yet; sync it before you troubleshoot the package."],
    "rec": [], "tools": [], "src": S("abr_intune", "ms_ts_app", "ms_ime", "ms_monitor"),
    "marker": "official"},
   {"t": "Check the agent on the endpoint and in the portal",
    "check": "The program folder exists, `AdminByRequest.exe` runs, the MSI Installer events are in the Application log, Connectivity shows OK, and the device is in the portal inventory",
    "do": ["On the device: `C:\\Program Files (x86)\\FastTrack Software\\Admin By Request` exists, `AdminByRequest.exe` is running in Task Manager, and `Event Viewer > Application` has MsiInstaller entries for a successful install.",
           "Open the tray icon, `About Admin By Request > Connectivity`: `Operational Status` and `Cloud Connectivity` should both be OK. The icon is green for a standard user and red for an administrator.",
           "In the portal, open `Inventory` and the device's details to confirm it reports to your tenant.",
           "If connectivity fails, check outbound TCP 443 to your region's API host and proxy behaviour as described in the pillar guide's network step."],
    "pit": ["A red tray icon after sign-in on a pilot device means the user is still an administrator: either revocation is off for that group, the account is excluded, or it holds an Entra or domain admin role that the client deliberately leaves alone."],
    "rec": [], "tools": [], "guides": [PILLAR], "src": S("abr_intune", "abr_win_inst", "abr_ui", "abr_net"),
    "marker": "official"},
   {"t": "Prove elevation works and is audited",
    "check": "A pilot user has completed one Run As Admin (and, if allowed, one Admin Session) and both appear in the portal audit log with the expected sub-setting",
    "do": ["Ask a pilot user to run a known installer with Run As Admin, then find the entry in the audit log; it shows the reason, the settings that applied and what was installed.",
           "Check that the sub-setting named in the entry is the persona you expected. A wrong sub-setting is a group-design problem, not a packaging problem.",
           "Record the result in the wave's go/no-go."],
    "pit": ["Test as the real persona, on a real persona device. Testing as an excluded IT account hides exactly the behaviour you need to see."],
    "rec": [], "tools": [], "src": S("abr_audit", "abr_win_inst"),
    "marker": "practical"},
  ]},

 {
  "id": "update", "title": "Update the client: supersedence or Auto-Update", "time": "Per release", "deep": True,
  "goal": "New client releases reach devices through the one mechanism you chose, detection stays correct after every upgrade, and downgrades never loop.",
  "steps": [
   {"t": "If Intune owns versions: package the new release and supersede",
    "check": "For each release there is a new app with its own .intunewin, detection value raised to the new four-part version, a supersedence entry on the old app with `Uninstall previous version` set to No, and its own explicit assignment",
    "do": ["Repeat phases 3–5 for the new MSI in a new version folder. Set the detection value to the new full version, so devices on the old version are detected as needing the update.",
           "On the new app's Supersedence tab add the previous Admin By Request app. Keep `Uninstall previous version` at No: the vendor documents that the MSI detects the older version and upgrades in place, and Microsoft says no uninstall command is needed when the installer updates the old app itself.",
           "Assign the new app explicitly, pilot group first. Microsoft states that superseding apps do not get automatic targeting.",
           "A supersedence graph is limited to 10 nodes. Once every device runs the new version, remove the oldest apps from the chain rather than letting it grow.",
           "Keep Auto-Update for Windows Workstation switched off in the portal."],
    "pit": ["Never assign an older package to devices that already run a newer client. The MSI refuses to downgrade: msiexec returns 1603 ('Newer version already installed') and Intune shows 0x80070643.",
            "The vendor's large-enterprise note recommends version-aware deployment, installing only where the installed version is older than the package. The `Greater than or equal to` detection rule gives you exactly that in Intune."],
    "rec": [], "tools": [], "src": S("abr_win_inst", "abr_large", "ms_super", "abr_tenant"),
    "marker": "official"},
   {"t": "If Auto-Update owns versions: keep the Intune app for new installs",
    "check": "Auto-Update for Windows Workstation is on, the Intune app's detection rule is still `Greater than or equal to` an older version, and the app is repackaged at major releases only",
    "do": ["With Auto-Update, the vendor pushes new versions in bulk, typically four to eight weeks after general availability, and updates are small (under 3 MB per the vendor).",
           "The Intune app then only installs the client on new devices. Because detection is `Greater than or equal to`, devices that auto-updated stay compliant in Intune.",
           "Repackage at major releases so newly enrolled devices do not start on a very old client and immediately upgrade.",
           "To exempt specific devices from Auto-Update, the vendor documents a `REG_DWORD` named `InternetUpdate` (0 = off, 1 = on) under `HKLM\\Software\\FastTrack Software\\Admin By Request\\Policies`, which overrides the portal setting."],
    "pit": ["Local registry policy always beats the portal and is easy to forget. If you use `InternetUpdate`, deploy it from Intune with a documented owner, and remove it when it is no longer needed."],
    "rec": [], "tools": [], "src": S("abr_large", "abr_win_inst", "abr_tenant", "abr_pol"),
    "marker": "official"},
  ]},

 {
  "id": "troubleshoot", "title": "Troubleshooting and rollback", "time": "Ongoing", "deep": False,
  "goal": "First-line staff can map an Intune status or exit code to its cause in minutes, and the team can remove the agent from a group without leaving devices without an admin path.",
  "steps": [
   {"t": "Read the IME logs and collect them from Intune",
    "check": "The runbook names the log folder, the three logs to open first, and how to collect them remotely",
    "do": ["IME logs are in `C:\\ProgramData\\Microsoft\\IntuneManagementExtension\\Logs`; open them with CMTrace. Start with `AppWorkload.log` (check-ins, downloads, installs, applicability and detection), then `AppActionProcessor.log` (detection and applicability checks) and `IntuneManagementExtension.log` (check-ins and policy processing).",
           "For a failed install, use `Collect logs` in the app's installation details in Intune to pull the logs without touching the device.",
           "Search the logs for the app name or for `AdminByRequest.exe` to see the detection result before and after the install."],
    "pit": ["Read the detection lines first. Most 'failed' Admin By Request installs actually succeeded and were then not detected."],
    "rec": [], "tools": [], "src": S("ms_ts_win32", "ms_ime", "ms_flow"),
    "marker": "official"},
   {"t": "Map the common symptoms to their cause",
    "check": "Each symptom below has a known fix in the runbook, and the team has seen at least one of them in the pilot",
    "do": ["`0x87D1041C`, 'The application was not detected after installation completed successfully': the detection rule does not match. Check the path, that detection uses `String (version)`, and that the value has four parts.",
           "Daily reinstall attempts, or `0x80070643` with msiexec 1603 'Newer version already installed' on a schedule: the device was upgraded but the rule no longer matches (typically an MSI product-code rule or an `Equals` operator), so Intune keeps retrying the older package.",
           "Uninstall returns 1605 ('only valid for products that are currently installed') or 1619 ('could not be opened'): a product-code or file-name based uninstall was used. Switch to the vendor's `Get-Package` command.",
           "Installed in Intune but missing from the portal inventory: licence count exceeded, or the device cannot reach the API host (Connectivity panel, proxy, TLS inspection). Submit Diagnostics from the client before opening a vendor ticket.",
           "Reading `MSIProductId` from `HKLM:\\SOFTWARE\\FastTrack Software\\Admin By Request` fails with 'Requested registry access is not allowed': the client denies standard users access to its key. Run the query elevated or from Intune as SYSTEM."],
    "pit": ["Look up any other code in Microsoft's Intune app installation error reference before guessing; codes are easy to misread across HRESULT and decimal forms."],
    "rec": [], "tools": [], "src": S("ms_err", "abr_win_inst", "abr_intune", "abr_ui", "abr_net", "abr_lic"),
    "marker": "official"},
   {"t": "Roll back: smallest lever first, uninstall intent last",
    "check": "The team can, in order: relax the portal sub-setting, stop a wave, and uninstall from a group with the Uninstall intent, and each device has a documented admin recovery path",
    "do": ["First lever is the portal, not Intune: relaxing a sub-setting or switching `Revoke admin rights` off for a group reaches endpoints in near real time (pillar guide, rollback step).",
           "To stop a wave, remove that wave's group from the Required assignment so no new devices install it. Do not rely on a removed assignment to take the agent off devices that already have it; that is what the Uninstall intent is for.",
           "To remove the agent, assign the app to the group with the `Uninstall` intent; Intune runs the PowerShell uninstall, which removes whichever version is installed. Microsoft notes that the Uninstall intent takes precedence over Available.",
           "The vendor documents that uninstalling restores revoked admin rights for local accounts, but not for on-premises Active Directory accounts. A signed-in user keeps their standard-user token until they sign out and back in; check the machine with `net localgroup Administrators` from another admin account.",
           "For a single device, the portal can generate an uninstall PIN from the device's inventory record, entered under `About Admin By Request > System`."],
    "pit": ["Before any group uninstall, make sure each device has a recovery admin path, such as Windows LAPS. Otherwise you trade standing admin for no admin at all."],
    "rec": [], "tools": [], "sec": ["harden-windows-laps"], "guides": [PILLAR], "src": S("abr_win_inst", "ms_add", "ms_super", "ms_laps"),
    "marker": "practical"},
  ]},
]
