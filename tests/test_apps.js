#!/usr/bin/env node
/* Offline logic tests for the two interactive tools.
 *   node tests/test_apps.js
 * No network: the DNS checker runs against an in-memory mock resolver. */
"use strict";
const assert = require("assert");
const path = require("path");
const CA = require(path.join(__dirname, "..", "assets", "ca-gen.js"));
const MD = require(path.join(__dirname, "..", "assets", "mail-dns.js"));

let n = 0;
function t(name, fn) { return Promise.resolve().then(fn).then(() => { n++; }, (e) => { console.error("FAIL " + name + "\n  " + (e && e.stack || e)); process.exitCode = 1; }); }

/* ---------------- Conditional Access generator ---------------- */
const GUID1 = "11111111-2222-3333-4444-555555555555";
const GUID2 = "AAAAAAAA-BBBB-CCCC-DDDD-EEEEEEEEEEEE";
const optionSets = [];
for (const scope of ["all", "group"]) for (const grant of ["mfa", "strength"]) for (const dirsync of [false, true])
  for (const hybrid of [false, true]) for (const state of [undefined, "enabled", "disabled", "enabledForReportingButNotEnforced"])
    for (const bg of [undefined, GUID1, "not-a-guid"]) for (const strength of [undefined, "bogus"].concat(Object.keys(CA.STRENGTH)))
      optionSets.push({ scope, grant, dirsync, hybrid, state, breakGlassGroup: bg, pilotGroup: GUID2, strength });

const tests = [];
tests.push(t("every scenario x option combination passes the v1.0 schema allowlist", () => {
  for (const k of Object.keys(CA.SCENARIOS)) for (const o of optionSets) {
    const p = CA.generate(k, o);
    assert.deepStrictEqual(CA.validate(p), [], k + " " + JSON.stringify(o));
  }
}));
tests.push(t("defaults: report-only and break-glass excluded", () => {
  for (const k of Object.keys(CA.SCENARIOS)) {
    const p = CA.generate(k, {});
    assert.strictEqual(p.state, "enabledForReportingButNotEnforced", k);
    assert.deepStrictEqual(p.conditions.users.excludeGroups, ["<break-glass-group-object-id>"], k);
  }
}));
tests.push(t("break-glass GUID is used (lower-cased) and can be switched off", () => {
  assert.deepStrictEqual(CA.generate("mfa-all", { breakGlassGroup: GUID2 }).conditions.users.excludeGroups, [GUID2.toLowerCase()]);
  assert.ok(!("excludeGroups" in CA.generate("mfa-all", { breakGlass: false }).conditions.users));
}));
tests.push(t("pilot scope targets a group instead of All", () => {
  const u = CA.generate("mfa-all", { scope: "group", pilotGroup: GUID1 }).conditions.users;
  assert.deepStrictEqual(u.includeGroups, [GUID1]); assert.ok(!u.includeUsers);
}));
tests.push(t("admin scenario includes role template IDs and phishing-resistant strength", () => {
  const p = CA.generate("admin-phish", {});
  assert.ok(p.conditions.users.includeRoles.length >= 14);
  p.conditions.users.includeRoles.forEach((r) => assert.ok(CA.GUID.test(r)));
  assert.strictEqual(p.grantControls.authenticationStrength.id, "00000000-0000-0000-0000-000000000004");
}));
tests.push(t("block-legacy targets exchangeActiveSync + other and blocks", () => {
  const p = CA.generate("block-legacy", {});
  assert.deepStrictEqual(p.conditions.clientAppTypes.slice().sort(), ["exchangeActiveSync", "other"]);
  assert.deepStrictEqual(p.grantControls.builtInControls, ["block"]);
}));
tests.push(t("user-risk: passwordChange AND mfa, high user risk, sign-in every time", () => {
  const p = CA.generate("user-risk", {});
  assert.strictEqual(p.grantControls.operator, "AND");
  assert.deepStrictEqual(p.grantControls.builtInControls.slice().sort(), ["mfa", "passwordChange"]);
  assert.ok(p.conditions.userRiskLevels.includes("high"));
  assert.strictEqual(p.sessionControls.signInFrequency.frequencyInterval, "everyTime");
}));
tests.push(t("device code flow uses authenticationFlows.transferMethods", () => {
  assert.strictEqual(CA.generate("block-device-code", {}).conditions.authenticationFlows.transferMethods, "deviceCodeFlow");
}));
tests.push(t("validator rejects unknown properties, bad enums and missing grant", () => {
  const p = CA.generate("mfa-all", {});
  assert.ok(CA.validate(Object.assign({}, p, { foo: 1 })).some((e) => /unknown property/.test(e)));
  assert.ok(CA.validate(Object.assign({}, p, { state: "on" })).some((e) => /invalid value/.test(e)));
  const q = Object.assign({}, p); delete q.grantControls;
  assert.ok(CA.validate(q).some((e) => /grantControls/.test(e)));
}));
tests.push(t("PowerShell output escapes quotes and keeps arrays", () => {
  const ps = CA.powershell(CA.generate("mfa-all", { displayName: "O'Brien" }));
  assert.ok(ps.includes("'O''Brien'"));
  assert.ok(/includeUsers = @\('All'\)/.test(ps));
  assert.ok(ps.includes("New-MgIdentityConditionalAccessPolicy -BodyParameter $params"));
}));

/* ---------------- Mail DNS checker ---------------- */
function mock(zone) {
  return (name, type) => {
    const k = name.toLowerCase() + "|" + type;
    if (zone.nx && zone.nx.includes(name)) return Promise.resolve({ status: 3, ad: false, answers: [] });
    return Promise.resolve({ status: 0, ad: !!zone.ad, answers: zone[k] || [] });
  };
}
const good = {
  ad: true,
  "contoso.com|MX": ["0 contoso-com.mail.protection.outlook.com."],
  "contoso.com|TXT": ['"v=spf1 include:spf.protection.outlook.com -all"'],
  "spf.protection.outlook.com|TXT": ['"v=spf1 ip4:40.92.0.0/15 -all"'],
  "_dmarc.contoso.com|TXT": ['"v=DMARC1; p=reject; rua=mailto:d@contoso.com; adkim=s; aspf=s"'],
  "selector1._domainkey.contoso.com|CNAME": ["selector1-contoso-com._domainkey.contoso.n-v1.dkim.mail.microsoft."],
  "selector2._domainkey.contoso.com|CNAME": ["selector2-contoso-com._domainkey.contoso.n-v1.dkim.mail.microsoft."],
  "_mta-sts.contoso.com|TXT": ['"v=STSv1; id=20261031"'],
  "_smtp._tls.contoso.com|TXT": ['"v=TLSRPTv1; rua=mailto:t@contoso.com"'],
  "contoso.com|CAA": ['0 issue "digicert.com"'],
};
tests.push(t("parsers", () => {
  assert.strictEqual(MD.normDomain(" https://User@Contoso.COM/path "), "contoso.com");
  assert.ok(!MD.normDomain("not a domain"));
  assert.strictEqual(MD.txtJoin('"v=spf1 include:a" " -all"'), "v=spf1 include:a -all");
  assert.deepStrictEqual(MD.parseTags("v=DMARC1; p=reject; pct=50"), { v: "DMARC1", p: "reject", pct: "50" });
  assert.deepStrictEqual(MD.parseCaa('0 issue "letsencrypt.org"'), { flags: 0, tag: "issue", value: "letsencrypt.org" });
  assert.strictEqual(MD.grade(95), "A"); assert.strictEqual(MD.grade(75), "B"); assert.strictEqual(MD.grade(10), "F");
}));
tests.push(t("well-configured M365 domain grades A", async () => {
  const r = await MD.run("contoso.com", mock(good));
  assert.strictEqual(r.grade, "A", JSON.stringify(r.checks.map((c) => [c.id, c.status, c.score])));
  assert.ok(r.m365);
  assert.deepStrictEqual(r.checks.map((c) => c.id), ["mx", "spf", "dmarc", "dkim", "mtasts", "tlsrpt", "caa", "dnssec"]);
}));
tests.push(t("weak domain: ~all, p=none, no DKIM -> low grade with warnings", async () => {
  const z = Object.assign({}, good, { ad: false,
    "contoso.com|TXT": ['"v=spf1 include:spf.protection.outlook.com ~all"'],
    "_dmarc.contoso.com|TXT": ['"v=DMARC1; p=none"'] });
  delete z["selector1._domainkey.contoso.com|CNAME"]; delete z["selector2._domainkey.contoso.com|CNAME"];
  delete z["_mta-sts.contoso.com|TXT"]; delete z["_smtp._tls.contoso.com|TXT"];
  const r = await MD.run("contoso.com", mock(z));
  assert.ok(r.score < 75, "score " + r.score);
  const by = Object.fromEntries(r.checks.map((c) => [c.id, c]));
  assert.notStrictEqual(by.dmarc.status, "ok"); assert.notStrictEqual(by.dkim.status, "ok");
}));
tests.push(t("SPF with more than 10 lookups is flagged", async () => {
  const z = { "big.com|MX": ["10 mx.big.com."], "big.com|TXT": ['"v=spf1 ' + Array.from({ length: 11 }, (_, i) => "include:s" + i + ".big.com").join(" ") + ' -all"'] };
  for (let i = 0; i < 11; i++) z["s" + i + ".big.com|TXT"] = ['"v=spf1 ip4:192.0.2.' + i + ' -all"'];
  const look = await MD.spfLookups(mock(z), "big.com");
  assert.strictEqual(look.lookups, 11);
  const r = await MD.run("big.com", mock(z));
  const spf = r.checks.find((c) => c.id === "spf");
  assert.strictEqual(spf.status, "fail", spf.summary);
}));
tests.push(t("SPF include loop does not hang", async () => {
  const z = { "a.com|TXT": ['"v=spf1 include:b.com -all"'], "b.com|TXT": ['"v=spf1 include:a.com -all"'] };
  const look = await MD.spfLookups(mock(z), "a.com");
  assert.ok(look.errors.some((e) => /loop/i.test(e)));
}));
tests.push(t("NXDOMAIN grades F", async () => {
  const r = await MD.run("nope.example", mock({ nx: ["nope.example"] }));
  assert.ok(r.nx); assert.strictEqual(r.grade, "F");
}));

Promise.all(tests).then(() => { console.log((process.exitCode ? "FAILED" : "OK") + ": " + n + "/" + tests.length + " tests passed"); });
