/* Tenant Recipes: Conditional Access policy generator. 100 % client-side: nothing is sent anywhere.
   Field names and enum values follow the Microsoft Graph v1.0 conditionalAccessPolicy resource
   (learn.microsoft.com/graph/api/resources/conditionalaccesspolicy). SCHEMA below is the allowlist the
   output is validated against before it is shown (tests/test_apps.js runs the same check in Node). */
(function (root) {
  "use strict";
  var STRENGTH = { mfa: "00000000-0000-0000-0000-000000000002", passwordless: "00000000-0000-0000-0000-000000000003", phish: "00000000-0000-0000-0000-000000000004" };
  var STRENGTH_NAME = { mfa: "Multifactor authentication", passwordless: "Passwordless MFA", phish: "Phishing-resistant MFA" };
  /* Built-in role template IDs (Microsoft Entra built-in roles reference). The 14 roles Microsoft lists for the admin MFA policy. */
  var ADMIN_ROLES = [
    ["Global Administrator", "62e90394-69f5-4237-9190-012177145e10"],
    ["Application Administrator", "9b895d92-2cd3-44c7-9d02-a6ac2d5ea5c3"],
    ["Authentication Administrator", "c4e39bd9-1100-46d3-8c65-fb160da0071f"],
    ["Billing Administrator", "b0f54661-2d74-4c50-afa3-1ec803f12efe"],
    ["Cloud Application Administrator", "158c047a-c907-4556-b7ef-446551a6b5f7"],
    ["Conditional Access Administrator", "b1be1c3e-b65d-4f19-8427-f6fa0d97feb9"],
    ["Exchange Administrator", "29232cdf-9323-42fd-ade2-1d097af3e4de"],
    ["Helpdesk Administrator", "729827e3-9c14-49f7-bb1b-9608f156bbb8"],
    ["Password Administrator", "966707d0-3269-4727-9be2-8c3a10f19b9d"],
    ["Privileged Authentication Administrator", "7be44c8a-adaf-4e2a-84d6-ab2649e08a13"],
    ["Privileged Role Administrator", "e8611ab8-c189-46e8-94e1-60213ab1f814"],
    ["Security Administrator", "194ae4cb-b126-40b2-bd5b-6091b380977d"],
    ["SharePoint Administrator", "f28a1f50-f6e7-4571-818b-6a12f2af6b6c"],
    ["User Administrator", "fe930be7-5e62-47db-91af-98c3a49a38b1"]
  ];
  var DIRSYNC_ROLE = "d29b2b05-8046-44ba-8758-1e26182fcf32"; // Directory Synchronization Accounts
  var L = "https://learn.microsoft.com/en-us/entra/identity/conditional-access/";
  var EVERY_TIME = { isEnabled: true, frequencyInterval: "everyTime", authenticationType: "primaryAndSecondaryAuthentication" };

  function strength(o, def) {
    if (o.grant === "mfa") return { operator: "OR", builtInControls: ["mfa"] };
    return { operator: "OR", authenticationStrength: { id: STRENGTH[o.strength] || STRENGTH[def] } };
  }

  /* opts: scope (all|group), dirsync, grant (strength|mfa), strength, hybrid */
  var SCENARIOS = {
    "mfa-all": {
      label: "Require MFA for all users", short: "MFA-AllUsers", license: "Microsoft Entra ID P1", learn: L + "policy-all-users-mfa-strength",
      what: "Baseline policy: every user, every resource, multifactor authentication. Microsoft recommends this as the policy every tenant has, with no app exclusions.",
      opts: { scope: 1, dirsync: 1, grant: 1, strength: ["mfa", "passwordless", "phish"] }, defStrength: "mfa",
      build: function (o) { return { conditions: { clientAppTypes: ["all"], applications: { includeApplications: ["All"] } }, grantControls: strength(o, "mfa") }; },
      notes: ["External authentication methods can't be combined with authentication strengths. Pick 'Require multifactor authentication' as the grant if you use them.",
              "Authentication strength and the 'Require multifactor authentication' control can't be used together in one policy."]
    },
    "block-legacy": {
      label: "Block legacy authentication", short: "Block-LegacyAuth", license: "Microsoft Entra ID P1", learn: L + "policy-block-legacy-authentication",
      what: "Blocks Exchange ActiveSync and other legacy clients (POP, IMAP, SMTP AUTH and older Office clients) that can't do MFA.",
      opts: { scope: 1, dirsync: 0, grant: 0 },
      build: function () { return { conditions: { clientAppTypes: ["exchangeActiveSync", "other"], applications: { includeApplications: ["All"] } }, grantControls: { operator: "OR", builtInControls: ["block"] } }; },
      notes: ["Check the sign-in logs (interactive and non-interactive) for legacy client apps before you switch to On. Exclude only accounts that truly still need legacy protocols."]
    },
    "compliant-device": {
      label: "Require a compliant device", short: "Require-CompliantDevice", license: "Microsoft Entra ID P1 + Microsoft Intune", learn: L + "policy-all-users-device-compliance",
      what: "Access only from devices that Intune marks as compliant (optionally also Microsoft Entra hybrid joined devices).",
      opts: { scope: 1, dirsync: 1, grant: 0, hybrid: 1 },
      build: function (o) { return { conditions: { clientAppTypes: ["all"], applications: { includeApplications: ["All"] } }, grantControls: { operator: "OR", builtInControls: o.hybrid ? ["compliantDevice", "domainJoinedDevice"] : ["compliantDevice"] } }; },
      notes: ["Create and assign an Intune compliance policy first, and make sure at least one device is compliant, or this policy blocks everyone it targets.",
              "Unmanaged and personal devices, and guests without a compliant device, lose access. Start with a pilot group."]
    },
    "admin-phish": {
      label: "Phishing-resistant MFA for admins", short: "Admins-PhishingResistantMFA", license: "Microsoft Entra ID P1", learn: L + "policy-admin-phish-resistant-mfa",
      what: "The 14 privileged built-in roles Microsoft lists must sign in with a phishing-resistant method (passkey/FIDO2, Windows Hello for Business or certificate-based MFA).",
      opts: { scope: 0, dirsync: 0, grant: 0, strength: ["phish", "passwordless", "mfa"] }, defStrength: "phish", roles: true,
      build: function (o) { return { conditions: { clientAppTypes: ["all"], applications: { includeApplications: ["All"] } }, grantControls: { operator: "OR", authenticationStrength: { id: STRENGTH[o.strength] || STRENGTH.phish } } }; },
      notes: ["Make sure every admin has registered a phishing-resistant method first (a Temporary Access Pass helps with bootstrap), or you lock admins out.",
              "Conditional Access only applies to built-in roles assigned at directory scope, not to custom or administrative-unit-scoped roles."]
    },
    "signin-risk-mfa": {
      label: "Require MFA for medium and high sign-in risk", short: "SignInRisk-MFA", license: "Microsoft Entra ID P2", learn: L + "policy-risk-based-sign-in",
      what: "Sign-ins that ID Protection rates medium or high risk must complete MFA again, every time.",
      opts: { scope: 1, dirsync: 0, grant: 1, strength: ["mfa", "passwordless", "phish"] }, defStrength: "mfa",
      build: function (o) { return { conditions: { clientAppTypes: ["all"], applications: { includeApplications: ["All"] }, signInRiskLevels: ["high", "medium"] }, grantControls: strength(o, "mfa"), sessionControls: { signInFrequency: EVERY_TIME } }; },
      notes: ["Users who haven't registered for MFA are blocked on a risky sign-in (AADSTS53004). Run a registration campaign first."]
    },
    "signin-risk-block": {
      label: "Block high sign-in risk", short: "Block-HighSignInRisk", license: "Microsoft Entra ID P2", learn: L + "policy-risk-based-sign-in",
      what: "Blocks sign-ins that ID Protection rates high risk. Stricter than the MFA variant: users can't self-remediate.",
      opts: { scope: 1, dirsync: 0, grant: 0 },
      build: function () { return { conditions: { clientAppTypes: ["all"], applications: { includeApplications: ["All"] }, signInRiskLevels: ["high"] }, grantControls: { operator: "OR", builtInControls: ["block"] } }; },
      notes: ["A block can't be cleared by the user. Have a help-desk process to review risky sign-ins and dismiss or confirm risk."]
    },
    "user-risk": {
      label: "Secure password change for high user risk", short: "UserRisk-PasswordChange", license: "Microsoft Entra ID P2", learn: L + "policy-risk-based-user",
      what: "Users that ID Protection rates high risk must complete MFA and change their password (grant: MFA AND password change, re-authenticate every time).",
      opts: { scope: 1, dirsync: 0, grant: 0 },
      build: function () { return { conditions: { clientAppTypes: ["all"], applications: { includeApplications: ["All"] }, userRiskLevels: ["high"] }, grantControls: { operator: "AND", builtInControls: ["mfa", "passwordChange"] }, sessionControls: { signInFrequency: EVERY_TIME } }; },
      notes: ["Microsoft's article now leads with the newer 'Require risk remediation' grant, which also covers passwordless users. It's available in the admin center; this generator outputs the documented v1.0 passwordChange + mfa combination.",
              "Graph rules for passwordChange: combine it with mfa using AND, include userRiskLevels and target all resources."]
    },
    "block-device-code": {
      label: "Block device code flow", short: "Block-DeviceCodeFlow", license: "Microsoft Entra ID P1", learn: L + "policy-block-authentication-flows",
      what: "Blocks the device code authentication flow, which is widely abused for phishing. Allow it only for documented exceptions.",
      opts: { scope: 1, dirsync: 0, grant: 0 },
      build: function () { return { conditions: { clientAppTypes: ["all"], applications: { includeApplications: ["All"] }, authenticationFlows: { transferMethods: "deviceCodeFlow" } }, grantControls: { operator: "OR", builtInControls: ["block"] } }; },
      notes: ["Audit device code flow use in the sign-in logs first (Teams Rooms, shared devices and some CLI tools use it). Exclude a dedicated group for real exceptions."]
    },
    "secure-registration": {
      label: "Protect security info registration", short: "Secure-SecurityInfoRegistration", license: "Microsoft Entra ID P1", learn: L + "policy-all-users-security-info-registration",
      what: "Registering MFA or SSPR methods from outside trusted locations requires an authentication strength (new users bootstrap with a Temporary Access Pass).",
      opts: { scope: 1, dirsync: 0, grant: 1, strength: ["mfa", "passwordless", "phish"] }, defStrength: "mfa", guests: true,
      build: function (o) { return { conditions: { clientAppTypes: ["all"], applications: { includeUserActions: ["urn:user:registersecurityinfo"] }, locations: { includeLocations: ["All"], excludeLocations: ["AllTrusted"] } }, grantControls: strength(o, "mfa") }; },
      notes: ["Define your trusted named locations first; otherwise 'AllTrusted' excludes nothing.",
              "Guests and external users are excluded, as in Microsoft's example: a Temporary Access Pass doesn't work for guests."]
    }
  };

  /* Allowlist from the Graph v1.0 resource pages (conditionalAccessPolicy, ConditionSet, Users, Applications,
     Locations, AuthenticationFlows, GrantControls, SessionControls, signInFrequencySessionControl). */
  var RISK = ["low", "medium", "high", "hidden", "none"];
  var SCHEMA = {
    policy: { displayName: "string", state: ["enabled", "disabled", "enabledForReportingButNotEnforced"], conditions: "conditions", grantControls: "grant", sessionControls: "session" },
    conditions: { applications: "applications", users: "users", clientAppTypes: ["all", "browser", "mobileAppsAndDesktopClients", "exchangeActiveSync", "easSupported", "other"],
      signInRiskLevels: RISK, userRiskLevels: RISK, locations: "locations", authenticationFlows: "authFlows" },
    users: { includeUsers: "ids", excludeUsers: "ids", includeGroups: "guids", excludeGroups: "guids", includeRoles: "guids", excludeRoles: "guids" },
    applications: { includeApplications: "ids", excludeApplications: "ids", includeUserActions: ["urn:user:registersecurityinfo", "urn:user:registerdevice"] },
    locations: { includeLocations: "ids", excludeLocations: "ids" },
    authFlows: { transferMethods: ["none", "deviceCodeFlow", "authenticationTransfer"] },
    grant: { operator: ["AND", "OR"], builtInControls: ["block", "mfa", "compliantDevice", "domainJoinedDevice", "approvedApplication", "compliantApplication", "passwordChange"], authenticationStrength: "strengthRef" },
    strengthRef: { id: "guid" },
    session: { signInFrequency: "sif" },
    sif: { isEnabled: "boolean", frequencyInterval: ["timeBased", "everyTime"], authenticationType: ["primaryAndSecondaryAuthentication", "secondaryAuthentication"], type: ["days", "hours"], value: "number" }
  };
  var GUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  var PLACEHOLDER = /^<[a-z0-9-]+>$/;

  function validate(obj, type, path, errs) {
    type = type || "policy"; path = path || "body"; errs = errs || [];
    var spec = SCHEMA[type];
    if (!obj || typeof obj !== "object" || Array.isArray(obj)) { errs.push(path + ": expected object"); return errs; }
    Object.keys(obj).forEach(function (k) {
      var t = spec[k], v = obj[k], p = path + "." + k;
      if (t === undefined) { errs.push(p + ": unknown property"); return; }
      if (Array.isArray(t)) {
        var vals = Array.isArray(v) ? v : [v];
        if (Array.isArray(v) && !v.length) errs.push(p + ": empty list");
        vals.forEach(function (x) { if (t.indexOf(x) < 0) errs.push(p + ": invalid value " + JSON.stringify(x)); });
      } else if (t === "string") { if (typeof v !== "string" || !v.trim()) errs.push(p + ": expected non-empty string"); }
      else if (t === "boolean") { if (typeof v !== "boolean") errs.push(p + ": expected boolean"); }
      else if (t === "number") { if (typeof v !== "number") errs.push(p + ": expected number"); }
      else if (t === "guid") { if (!GUID.test(v)) errs.push(p + ": expected GUID"); }
      else if (t === "ids" || t === "guids") {
        if (!Array.isArray(v) || !v.length) { errs.push(p + ": expected non-empty list"); return; }
        v.forEach(function (x) { if (typeof x !== "string" || (t === "guids" && !GUID.test(x) && !PLACEHOLDER.test(x))) errs.push(p + ": invalid id " + JSON.stringify(x)); });
      } else validate(v, t, p, errs);
    });
    if (type === "policy") {
      ["displayName", "state", "conditions"].forEach(function (k) { if (!(k in obj)) errs.push(path + "." + k + ": required"); });
      if (!obj.grantControls && !obj.sessionControls) errs.push(path + ": needs grantControls or sessionControls");
      var c = obj.conditions || {};
      if (!c.applications) errs.push(path + ".conditions.applications: required");
      if (!c.users) errs.push(path + ".conditions.users: required");
      if (!c.clientAppTypes) errs.push(path + ".conditions.clientAppTypes: required");
      var g = obj.grantControls;
      if (g) {
        var b = g.builtInControls || [];
        if (b.indexOf("mfa") > -1 && g.authenticationStrength) errs.push(path + ".grantControls: 'mfa' and authenticationStrength can't be combined");
        if (b.indexOf("passwordChange") > -1 && (g.operator !== "AND" || b.indexOf("mfa") < 0 || !(c.userRiskLevels || []).length)) errs.push(path + ".grantControls: passwordChange needs mfa, operator AND and userRiskLevels");
        if (!b.length && !g.authenticationStrength) errs.push(path + ".grantControls: no control set");
      }
    }
    return errs;
  }

  function generate(key, o) {
    var s = SCENARIOS[key];
    if (!s) throw new Error("unknown scenario " + key);
    o = o || {};
    var body = s.build(o);
    var users = {};
    if (s.roles) users.includeRoles = ADMIN_ROLES.map(function (r) { return r[1]; });
    else if (o.scope === "group") users.includeGroups = [o.pilotGroup && GUID.test(o.pilotGroup) ? o.pilotGroup.toLowerCase() : "<pilot-group-object-id>"];
    else users.includeUsers = ["All"];
    if (o.breakGlass !== false) users.excludeGroups = [o.breakGlassGroup && GUID.test(o.breakGlassGroup) ? o.breakGlassGroup.toLowerCase() : "<break-glass-group-object-id>"];
    if (o.dirsync && s.opts.dirsync) users.excludeRoles = [DIRSYNC_ROLE];
    if (s.guests) users.excludeUsers = ["GuestsOrExternalUsers"];
    var name = (o.displayName || "").trim() || defaultName(key, o);
    var policy = { displayName: name, state: o.state || "enabledForReportingButNotEnforced", conditions: Object.assign({ users: users }, body.conditions) };
    policy.grantControls = body.grantControls;
    if (body.sessionControls) policy.sessionControls = body.sessionControls;
    return policy;
  }

  function defaultName(key, o) {
    var s = SCENARIOS[key];
    var scope = s.roles ? "Admins" : (o.scope === "group" ? "Pilot" : "AllUsers");
    return "CA - " + s.short + " - " + scope;
  }

  function psValue(v, ind) {
    var pad = new Array(ind + 1).join("  ");
    if (Array.isArray(v)) return "@(" + v.map(function (x) { return psValue(x, ind); }).join(", ") + ")";
    if (v && typeof v === "object") {
      var ks = Object.keys(v);
      return "@{\n" + ks.map(function (k) { return pad + "  " + k + " = " + psValue(v[k], ind + 1); }).join("\n") + "\n" + pad + "}";
    }
    if (typeof v === "boolean") return v ? "$true" : "$false";
    if (typeof v === "number") return String(v);
    return "'" + String(v).replace(/'/g, "''") + "'";
  }

  function powershell(policy) {
    return "# Microsoft Graph PowerShell SDK (Install-Module Microsoft.Graph.Identity.SignIns)\n" +
      "Connect-MgGraph -Scopes 'Policy.Read.All','Policy.ReadWrite.ConditionalAccess'\n\n" +
      "$params = " + psValue(policy, 0) + "\n\n" +
      "New-MgIdentityConditionalAccessPolicy -BodyParameter $params";
  }

  function http(policy) {
    return "POST https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies\nContent-Type: application/json\n\n" + JSON.stringify(policy, null, 2);
  }

  var API = { SCENARIOS: SCENARIOS, ADMIN_ROLES: ADMIN_ROLES, STRENGTH: STRENGTH, STRENGTH_NAME: STRENGTH_NAME, DIRSYNC_ROLE: DIRSYNC_ROLE,
    SCHEMA: SCHEMA, generate: generate, validate: validate, powershell: powershell, http: http, defaultName: defaultName, GUID: GUID };
  if (typeof module !== "undefined" && module.exports) { module.exports = API; return; }

  /* ---------- UI ---------- */
  function $(id) { return document.getElementById(id); }
  function init() {
    var form = $("cag-form"); if (!form) return;
    var sel = $("cag-scn");
    Object.keys(SCENARIOS).forEach(function (k) { var op = document.createElement("option"); op.value = k; op.textContent = SCENARIOS[k].label; sel.appendChild(op); });
    var q = new URLSearchParams(location.search).get("s");
    if (q && SCENARIOS[q]) sel.value = q;
    var nameTouched = false;
    $("cag-name").addEventListener("input", function () { nameTouched = !!this.value.trim(); });
    function radio(name) { var r = form.querySelector('input[name="' + name + '"]:checked'); return r ? r.value : ""; }
    function render() {
      var key = sel.value, s = SCENARIOS[key];
      $("cag-row-scope").hidden = !s.opts.scope;
      $("cag-row-dirsync").hidden = !s.opts.dirsync;
      $("cag-row-grant").hidden = !s.opts.grant;
      $("cag-row-hybrid").hidden = !s.opts.hybrid;
      $("cag-row-strength").hidden = !s.opts.strength || (s.opts.grant && radio("cag-grant") === "mfa");
      $("cag-pilot").disabled = radio("cag-scope") !== "group";
      var ss = $("cag-strength"), cur = ss.value;
      if (s.opts.strength && ss.dataset.for !== key) {
        ss.innerHTML = ""; s.opts.strength.forEach(function (x) { var op = document.createElement("option"); op.value = x; op.textContent = STRENGTH_NAME[x]; ss.appendChild(op); });
        ss.value = s.defStrength; ss.dataset.for = key; cur = s.defStrength;
      }
      var bg = $("cag-bg").value.trim(), pg = $("cag-pilot").value.trim();
      $("cag-bg-err").hidden = !bg || GUID.test(bg);
      $("cag-pilot-err").hidden = !pg || GUID.test(pg) || radio("cag-scope") !== "group";
      var o = { scope: s.opts.scope ? radio("cag-scope") : "all", pilotGroup: pg, breakGlass: $("cag-bgon").checked, breakGlassGroup: bg,
        dirsync: $("cag-dirsync").checked, grant: radio("cag-grant") || "strength", strength: ss.value || cur, hybrid: $("cag-hybrid").checked,
        state: radio("cag-state") || "enabledForReportingButNotEnforced" };
      if (!nameTouched) $("cag-name").value = defaultName(key, o);
      o.displayName = $("cag-name").value;
      var p = generate(key, o), errs = validate(p);
      $("cag-json").textContent = JSON.stringify(p, null, 2);
      $("cag-ps").textContent = powershell(p);
      $("cag-http").textContent = http(p);
      $("cag-what").textContent = s.what;
      $("cag-lic").textContent = s.license;
      var a = $("cag-learn"); a.href = s.learn; a.textContent = "Microsoft Learn: " + s.label;
      var ul = $("cag-notes"); ul.innerHTML = "";
      var notes = s.notes.slice();
      if (!o.breakGlass) notes.unshift("No break-glass exclusion: a mistake in this policy can lock every administrator out. Microsoft recommends excluding emergency access accounts.");
      else if (!GUID.test(bg)) notes.unshift("Replace <break-glass-group-object-id> with the object ID of your emergency access group before you run it.");
      if (o.scope === "group" && !GUID.test(pg) && s.opts.scope) notes.unshift("Replace <pilot-group-object-id> with the object ID of your pilot group.");
      if (o.state === "enabled") notes.unshift("State is On. Microsoft's guidance is to start in report-only and review the impact first.");
      notes.forEach(function (n) { var li = document.createElement("li"); li.textContent = n; ul.appendChild(li); });
      var v = $("cag-valid");
      v.className = "cag-valid " + (errs.length ? "bad" : "good");
      v.textContent = errs.length ? "Schema check failed: " + errs.join("; ") : "Schema check passed: every property and value is in the Graph v1.0 conditionalAccessPolicy schema.";
      var st = $("cag-state-lbl"); st.textContent = { enabledForReportingButNotEnforced: "Report-only", disabled: "Off", enabled: "On" }[o.state];
      if (history.replaceState) history.replaceState(null, "", "?s=" + key);
    }
    form.addEventListener("input", render);
    form.addEventListener("change", render);
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    $("cag-reset").addEventListener("click", function () { setTimeout(function () { nameTouched = false; $("cag-strength").dataset.for = ""; render(); }, 0); });
    render();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})(this);
