/* Tenant Recipes: mail DNS checker. Runs entirely in the browser. Queries go straight from the visitor's browser to
   Cloudflare's public DNS-over-HTTPS JSON API (fallback: Google Public DNS). Nothing is sent to or stored by this site. */
(function (root) {
  "use strict";
  var TYPES = { A: 1, CNAME: 5, MX: 15, TXT: 16, CAA: 257 };
  var DOH = [
    function (n, t) { return "https://cloudflare-dns.com/dns-query?name=" + encodeURIComponent(n) + "&type=" + t; },
    function (n, t) { return "https://dns.google/resolve?name=" + encodeURIComponent(n) + "&type=" + t; }
  ];
  var LEARN = {
    spf: { t: "Microsoft Learn: Set up SPF to identify valid email sources", u: "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-spf-configure" },
    dkim: { t: "Microsoft Learn: Set up DKIM to sign mail from your Microsoft 365 domain", u: "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dkim-configure" },
    dmarc: { t: "Microsoft Learn: Set up DMARC to validate the From address domain", u: "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-dmarc-configure" },
    auth: { t: "Microsoft Learn: Email authentication in Microsoft 365", u: "https://learn.microsoft.com/en-us/defender-office-365/email-authentication-about" },
    mx: { t: "Microsoft Learn: Add DNS records to connect your domain", u: "https://learn.microsoft.com/en-us/microsoft-365/admin/get-help-with-domains/create-dns-records-at-any-dns-hosting-provider" },
    mtasts: { t: "Microsoft Learn: Enhancing mail flow with MTA-STS", u: "https://learn.microsoft.com/en-us/exchange/security-and-compliance/enhance-mail-flow-using-strict-transport-security" },
    rfc8461: { t: "RFC 8461: SMTP MTA Strict Transport Security (MTA-STS)", u: "https://www.rfc-editor.org/rfc/rfc8461.html" },
    rfc8460: { t: "RFC 8460: SMTP TLS Reporting", u: "https://www.rfc-editor.org/rfc/rfc8460.html" },
    rfc8659: { t: "RFC 8659: DNS Certification Authority Authorization (CAA)", u: "https://www.rfc-editor.org/rfc/rfc8659.html" },
    rfc7208: { t: "RFC 7208: SPF (section 4.6.4, DNS lookup limits)", u: "https://www.rfc-editor.org/rfc/rfc7208.html#section-4.6.4" }
  };
  var WEIGHTS = { spf: 25, dmarc: 30, dkim: 20, mx: 6, mtasts: 7, tlsrpt: 4, caa: 4, dnssec: 4 };

  function normDomain(input) {
    var d = String(input || "").trim().toLowerCase();
    d = d.replace(/^[a-z]+:\/\//, "").replace(/^[^@\s]*@/, "").split(/[\/?#:\s]/)[0].replace(/\.$/, "");
    if (typeof URL !== "undefined" && /[^\x00-\x7f]/.test(d)) { try { d = new URL("http://" + d).hostname; } catch (e) { return null; } }
    if (d.length > 253 || !/^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$/.test(d)) return null;
    return d;
  }

  /* TXT data from DoH JSON is one or more quoted character-strings: "a" "b" -> ab */
  function txtJoin(data) {
    var s = String(data), out = "", m, re = /"((?:[^"\\]|\\.)*)"/g, any = false;
    while ((m = re.exec(s))) { any = true; out += m[1]; }
    if (!any) out = s;
    return out.replace(/\\(\d{3})/g, function (_, n) { return String.fromCharCode(parseInt(n, 10)); }).replace(/\\(.)/g, "$1");
  }

  function makeResolver(fetchFn) {
    var cache = {};
    function one(i, name, type) {
      return fetchFn(DOH[i](name, type), { headers: { accept: "application/dns-json" }, credentials: "omit", referrerPolicy: "no-referrer", cache: "no-store" })
        .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); });
    }
    return function resolve(name, type) {
      var key = name + "|" + type;
      if (!cache[key]) {
        cache[key] = one(0, name, type).catch(function () { return one(1, name, type); }).then(function (j) {
          if (j.Status !== 0 && j.Status !== 3) throw new Error("DNS error (RCODE " + j.Status + ") for " + name + " " + type);
          return { status: j.Status, ad: !!j.AD, answers: (j.Answer || []).filter(function (a) { return a.type === TYPES[type]; }).map(function (a) { return a.data; }) };
        });
      }
      return cache[key];
    };
  }

  function txt(resolve, name) { return resolve(name, "TXT").then(function (r) { return r.answers.map(txtJoin); }); }

  /* ---------- parsers ---------- */
  function parseTags(rec) {
    var o = {};
    rec.split(";").forEach(function (p) { var i = p.indexOf("="); if (i > 0) o[p.slice(0, i).trim().toLowerCase()] = p.slice(i + 1).trim(); });
    return o;
  }
  function parseMx(data) { var m = String(data).trim().split(/\s+/); return { pref: parseInt(m[0], 10), host: (m[1] || "").replace(/\.$/, "").toLowerCase() }; }
  function isM365Mx(h) { return /\.mail\.protection\.outlook\.com$/.test(h) || /\.mx\.microsoft$/.test(h); }
  function parseCaa(data) { var m = String(data).match(/^(\d+)\s+(\S+)\s+"?(.*?)"?$/); return m ? { flags: +m[1], tag: m[2].toLowerCase(), value: m[3] } : { flags: 0, tag: "?", value: String(data) }; }

  /* Count SPF DNS lookups per RFC 7208 4.6.4: include, a, mx, ptr, exists and redirect each cost one, nested records count too. */
  function spfLookups(resolve, domain, seen, depth) {
    seen = seen || {}; depth = depth || 0;
    var res = { lookups: 0, errors: [], tree: [], includes: [] };
    if (seen[domain]) { res.errors.push("SPF loop via " + domain); return Promise.resolve(res); }
    seen[domain] = true;
    if (depth > 10) { res.errors.push("SPF nesting too deep at " + domain); return Promise.resolve(res); }
    return txt(resolve, domain).then(function (recs) {
      var spf = recs.filter(function (r) { return /^v=spf1(\s|$)/i.test(r); });
      if (!spf.length) { res.errors.push(domain + " has no SPF record (permerror)"); return res; }
      if (spf.length > 1) { res.errors.push(domain + " has " + spf.length + " SPF records (permerror)"); }
      var terms = spf[0].split(/\s+/).slice(1).filter(Boolean), chain = Promise.resolve(), hasAll = terms.some(function (t) { return /^[+\-~?]?all$/i.test(t); });
      terms.forEach(function (t) {
        var m = t.replace(/^[+\-~?]/, ""), low = m.toLowerCase(), target = null;
        if (/^include:/.test(low)) { res.lookups++; target = m.slice(8); res.includes.push(target.toLowerCase()); }
        else if (/^redirect=/.test(low)) { res.lookups++; if (!hasAll) target = m.slice(9); }
        else if (/^(a|mx|ptr)(:|\/|$)/.test(low) || /^exists:/.test(low)) res.lookups++;
        if (target && target.indexOf("%") < 0) {
          chain = chain.then(function () {
            return spfLookups(resolve, target.toLowerCase().replace(/\.$/, ""), seen, depth + 1).then(function (sub) {
              res.lookups += sub.lookups; res.errors = res.errors.concat(sub.errors); res.includes = res.includes.concat(sub.includes); res.tree.push({ domain: target, lookups: 1 + sub.lookups });
            });
          });
        }
      });
      return chain.then(function () { return res; });
    });
  }

  /* ---------- checks: each returns {id,title,status,score,summary,details[],records[],links[]} ---------- */
  function C(id, title) { return { id: id, title: title, status: "info", score: 1, summary: "", details: [], records: [], links: [] }; }

  function checkMx(resolve, d) {
    var c = C("mx", "MX (inbound mail)");
    c.links = [LEARN.mx];
    return resolve(d, "MX").then(function (r) {
      var mx = r.answers.map(parseMx).sort(function (a, b) { return a.pref - b.pref; });
      c.records = mx.map(function (m) { return m.pref + " " + (m.host || "."); });
      c.ad = r.ad; c.nx = r.status === 3;
      c.isNull = mx.length === 1 && (mx[0].host === "" || mx[0].host === ".");
      c.m365 = mx.some(function (m) { return isM365Mx(m.host); });
      c.parked = !mx.length || c.isNull;
      if (c.nx) { c.status = "fail"; c.score = 0; c.summary = "The domain doesn't exist in DNS (NXDOMAIN)."; }
      else if (c.isNull) { c.status = "ok"; c.summary = "Null MX: the domain declares that it accepts no mail (RFC 7505)."; }
      else if (!mx.length) { c.status = "warn"; c.score = 0.5; c.summary = "No MX record. Mail to this domain falls back to its A record or fails. If the domain never receives mail, publish a null MX (0 .)."; }
      else { c.status = "ok"; c.summary = c.m365 ? "Points to Exchange Online." : mx.length + " MX record" + (mx.length > 1 ? "s" : "") + " found (not Exchange Online)."; }
      return c;
    });
  }

  function checkSpf(resolve, d, mx) {
    var c = C("spf", "SPF");
    c.links = [LEARN.spf, LEARN.rfc7208];
    return txt(resolve, d).then(function (recs) {
      var spf = recs.filter(function (r) { return /^v=spf1(\s|$)/i.test(r); });
      c.records = spf;
      if (!spf.length) { c.status = "fail"; c.score = 0; c.summary = "No SPF record. Anyone can claim to send as this domain." + (mx.parked ? " For a domain that sends no mail, publish v=spf1 -all." : ""); return c; }
      if (spf.length > 1) { c.status = "fail"; c.score = 0; c.summary = spf.length + " SPF records found. Receivers treat more than one as a permanent error: merge them into one."; return c; }
      var rec = spf[0], all = (rec.match(/\s([+\-~?]?)all(\s|$)/i) || [])[1];
      var redirect = /\sredirect=/i.test(rec);
      return spfLookups(resolve, d).then(function (L) {
        c.lookups = L.lookups;
        var s = 1, st = "ok", msgs = [];
        if (all === undefined) { if (redirect) msgs.push("Uses redirect= (the target record's all applies)."); else { s = 0.4; st = "warn"; msgs.push("No all mechanism: unlisted senders get a neutral result."); } }
        else if (all === "-") msgs.push(mx.parked ? "Ends in -all (hard fail): no server may send as this domain." : "Ends in -all (hard fail), which Microsoft recommends for Microsoft 365 domains that also use DKIM and DMARC.");
        else if (all === "~") { s = 0.75; st = "warn"; msgs.push("Ends in ~all (soft fail). Microsoft recommends -all, because DMARC can only act on SPF failures of unsigned mail with -all."); }
        else if (all === "?") { s = 0.3; st = "warn"; msgs.push("Ends in ?all (neutral): no protection."); }
        else { s = 0; st = "fail"; msgs.push("Ends in +all: every server on the internet is authorized. Fix immediately."); }
        if (L.lookups > 10) { s = 0; st = "fail"; msgs.unshift(L.lookups + " DNS lookups: more than 10 means SPF fails with a permanent error for every message."); }
        else if (L.lookups >= 8) { s = Math.min(s, 0.8); if (st === "ok") st = "warn"; msgs.push(L.lookups + " of 10 DNS lookups used: close to the limit."); }
        else msgs.push(L.lookups + " of 10 DNS lookups used.");
        if (L.errors.length) { s = Math.min(s, 0.3); st = "fail"; msgs = msgs.concat(L.errors); }
        if (/\s[+\-~?]?ptr(:|\s|$)/i.test(rec)) { s = Math.min(s, 0.8); if (st === "ok") st = "warn"; msgs.push("Uses ptr, which RFC 7208 says not to use (slow, unreliable)."); }
        c.m365Include = L.includes.indexOf("spf.protection.outlook.com") > -1;
        if (mx.m365 && !c.m365Include) { s = Math.min(s, 0.7); if (st === "ok") st = "warn"; msgs.push("MX is Exchange Online but include:spf.protection.outlook.com is missing, so mail sent through Microsoft 365 fails SPF."); }
        c.status = st; c.score = s; c.summary = msgs.shift(); c.details = msgs;
        if (L.tree.length) c.details.push("Lookups per include/redirect: " + L.tree.map(function (t) { return t.domain + " (" + t.lookups + ")"; }).join(", ") + ".");
        return c;
      });
    });
  }

  function checkDmarc(resolve, d) {
    var c = C("dmarc", "DMARC");
    c.links = [LEARN.dmarc];
    return txt(resolve, "_dmarc." + d).then(function (recs) {
      var dm = recs.filter(function (r) { return /^v=DMARC1(\s*;|$)/i.test(r); });
      c.records = dm;
      if (!dm.length) { c.status = "fail"; c.score = 0; c.summary = "No DMARC record at _dmarc." + d + ". Receivers get no instruction for spoofed mail and you get no reports. (A subdomain may inherit the parent domain's sp= policy.)"; return c; }
      if (dm.length > 1) { c.status = "fail"; c.score = 0; c.summary = "More than one DMARC record: receivers ignore DMARC for the domain."; return c; }
      var t = parseTags(dm[0]), p = (t.p || "").toLowerCase(), pct = t.pct === undefined ? 100 : parseInt(t.pct, 10), s, st, msgs = [];
      c.policy = p;
      if (p === "reject") { s = 1; st = "ok"; msgs.push("p=reject: mail that fails DMARC should be rejected. This is the goal Microsoft describes."); }
      else if (p === "quarantine") { s = 0.8; st = "ok"; msgs.push("p=quarantine: failing mail should be treated as suspicious. Next step: p=reject once reports look clean."); }
      else if (p === "none") { s = 0.3; st = "warn"; msgs.push("p=none: monitoring only, spoofed mail is not stopped. Move to quarantine, then reject."); }
      else { s = 0; st = "fail"; msgs.push("Missing or invalid p= tag: the record is invalid."); }
      if (pct < 100) { s *= 0.85; if (st === "ok") st = "warn"; msgs.push("pct=" + pct + ": the policy applies to only " + pct + " % of failing mail."); }
      if (!t.rua) { s = Math.max(0, s - 0.1); if (st === "ok") st = "warn"; msgs.push("No rua= address: you receive no aggregate reports, so you can't see who sends as your domain."); }
      else msgs.push("Aggregate reports go to " + t.rua + ".");
      if (t.sp && t.sp.toLowerCase() === "none" && p !== "none") { s = Math.min(s, 0.7); if (st === "ok") st = "warn"; msgs.push("sp=none: subdomains are not protected even though the main policy is " + p + "."); }
      msgs.push("Alignment: DKIM " + ((t.adkim || "r").toLowerCase() === "s" ? "strict" : "relaxed") + ", SPF " + ((t.aspf || "r").toLowerCase() === "s" ? "strict" : "relaxed") + (t.adkim || t.aspf ? "." : " (defaults)."));
      c.status = st; c.score = s; c.summary = msgs.shift(); c.details = msgs;
      return c;
    });
  }

  function checkDkim(resolve, d, mx, spf) {
    var c = C("dkim", "DKIM (Microsoft 365 selectors)");
    c.links = [LEARN.dkim];
    var expectM365 = mx.m365 || !!spf.m365Include;
    return Promise.all(["selector1", "selector2"].map(function (sel) {
      return resolve(sel + "._domainkey." + d, "CNAME").then(function (r) { return { sel: sel, target: (r.answers[0] || "").replace(/\.$/, "") }; });
    })).then(function (res) {
      var ok = res.filter(function (x) { return /\._domainkey\..+\.(onmicrosoft\.com|dkim\.mail\.microsoft)$/i.test(x.target); });
      c.records = res.filter(function (x) { return x.target; }).map(function (x) { return x.sel + "._domainkey → " + x.target; });
      if (ok.length === 2) { c.status = "ok"; c.summary = "Both Microsoft 365 DKIM CNAMEs (selector1, selector2) are published."; c.details.push("A CNAME doesn't prove signing is on. Check that DKIM signing is enabled for the domain in the Defender portal, or look for DKIM-Signature: d=" + d + " in a sent message's headers."); }
      else if (ok.length === 1) { c.status = "warn"; c.score = 0.5; c.summary = "Only " + ok[0].sel + " is published. Microsoft 365 needs both selectors so it can rotate keys."; }
      else if (mx.parked && !expectM365) { c.status = "info"; c.score = 1; c.summary = "No Microsoft 365 DKIM CNAMEs. Fine for a domain that sends no mail (SPF -all and DMARC p=reject cover it)."; }
      else if (expectM365) { c.status = "fail"; c.score = 0; c.summary = "The domain uses Microsoft 365 but selector1/selector2._domainkey CNAMEs are missing, so mail isn't DKIM signed with this domain."; }
      else { c.status = "info"; c.score = 0.5; c.summary = "No Microsoft 365 DKIM CNAMEs. This checker only looks for the Microsoft 365 selectors; other mail providers use their own selector names."; }
      return c;
    });
  }

  function checkMtaSts(resolve, d, mx) {
    var c = C("mtasts", "MTA-STS");
    c.links = [LEARN.mtasts, LEARN.rfc8461];
    return txt(resolve, "_mta-sts." + d).then(function (recs) {
      var r = recs.filter(function (x) { return /^v=STSv1/i.test(x); });
      c.records = r;
      if (mx.parked) { c.status = "info"; c.summary = "Not needed: the domain receives no mail."; return c; }
      if (!r.length) { c.status = "warn"; c.score = 0; c.summary = "No MTA-STS record. Sending servers may deliver to you without TLS, or to a spoofed MX, without noticing."; c.details.push("Microsoft documents how to publish MTA-STS for Exchange Online (policy file with mx: *.mail.protection.outlook.com)."); return c; }
      var t = parseTags(r[0]);
      if (r.length > 1 || !t.id) { c.status = "warn"; c.score = 0.5; c.summary = r.length > 1 ? "More than one MTA-STS TXT record: senders ignore MTA-STS." : "The record has no id= value."; return c; }
      c.status = "ok"; c.summary = "MTA-STS is announced (id=" + t.id + ").";
      c.details.push("This checker doesn't download the policy file. Open https://mta-sts." + d + "/.well-known/mta-sts.txt and confirm mode: enforce and an mx: line that matches your MX.");
      return c;
    });
  }

  function checkTlsRpt(resolve, d, mx) {
    var c = C("tlsrpt", "TLS-RPT");
    c.links = [LEARN.rfc8460];
    return txt(resolve, "_smtp._tls." + d).then(function (recs) {
      var r = recs.filter(function (x) { return /^v=TLSRPTv1/i.test(x); });
      c.records = r;
      if (mx.parked) { c.status = "info"; c.summary = "Not needed: the domain receives no mail."; return c; }
      if (!r.length) { c.status = "warn"; c.score = 0; c.summary = "No TLS-RPT record. You won't get reports when senders fail to set up TLS to your MX (useful together with MTA-STS)."; return c; }
      var t = parseTags(r[0]);
      if (!t.rua) { c.status = "warn"; c.score = 0.5; c.summary = "TLS-RPT record has no rua= destination."; return c; }
      c.status = "ok"; c.summary = "TLS reports go to " + t.rua + ".";
      return c;
    });
  }

  function checkCaa(resolve, d) {
    var c = C("caa", "CAA (certificate issuance)");
    c.links = [LEARN.rfc8659];
    return resolve(d, "CAA").then(function (r) {
      var caa = r.answers.map(parseCaa);
      c.records = r.answers.slice();
      if (!caa.length) { c.status = "info"; c.score = 0.5; c.summary = "No CAA record on " + d + ": any public CA may issue certificates (a CAA record on a parent domain would still apply)."; return c; }
      var issue = caa.filter(function (x) { return x.tag === "issue"; }).map(function (x) { return x.value || ";"; });
      var wild = caa.filter(function (x) { return x.tag === "issuewild"; }).map(function (x) { return x.value || ";"; });
      if (!issue.length && !wild.length) { c.status = "info"; c.score = 0.5; c.summary = "CAA records exist but none has an issue or issuewild tag, so they don't restrict which CA may issue."; return c; }
      c.status = "ok"; c.summary = issue.length ? (issue.join(", ") === ";" ? "No CA may issue certificates (issue \";\")." : "Only " + issue.join(", ") + " may issue certificates.") : "Only wildcard issuance is restricted (no issue tag).";
      if (wild.length) c.details.push("Wildcard certificates: " + (wild.join(", ") === ";" ? "blocked" : wild.join(", ")) + ".");
      if (!caa.some(function (x) { return x.tag === "iodef"; })) c.details.push("Optional: add an iodef tag so CAs can report refused requests.");
      return c;
    });
  }

  function grade(score) { return score >= 90 ? "A" : score >= 75 ? "B" : score >= 60 ? "C" : score >= 40 ? "D" : "F"; }

  function run(domain, resolve) {
    var d = normDomain(domain);
    if (!d) return Promise.reject(new Error("That doesn't look like a domain name. Type something like contoso.com."));
    return checkMx(resolve, d).then(function (mx) {
      if (mx.nx) return { domain: d, nx: true, checks: [mx], score: 0, grade: "F" };
      return Promise.all([checkSpf(resolve, d, mx), checkDmarc(resolve, d)]).then(function (a) {
        var spf = a[0], dmarc = a[1];
        return Promise.all([checkDkim(resolve, d, mx, spf), checkMtaSts(resolve, d, mx), checkTlsRpt(resolve, d, mx), checkCaa(resolve, d)]).then(function (b) {
          var dnssec = C("dnssec", "DNSSEC");
          dnssec.links = [LEARN.auth];
          if (mx.ad) { dnssec.status = "ok"; dnssec.summary = "Answers are DNSSEC-validated (AD flag set by the resolver)."; }
          else { dnssec.status = "info"; dnssec.score = 0.3; dnssec.summary = "Answers are not DNSSEC-validated: the zone is unsigned or the chain is incomplete. Signing protects your MX, SPF and DMARC records from tampering."; }
          var checks = [mx, spf, dmarc, b[0], b[1], b[2], b[3], dnssec];
          var total = 0; checks.forEach(function (c) { total += (WEIGHTS[c.id] || 0) * c.score; });
          var score = Math.round(total);
          return { domain: d, parked: mx.parked, m365: mx.m365, checks: checks, score: score, grade: grade(score) };
        });
      });
    });
  }

  var API = { normDomain: normDomain, txtJoin: txtJoin, parseTags: parseTags, parseCaa: parseCaa, spfLookups: spfLookups, makeResolver: makeResolver,
    run: run, grade: grade, WEIGHTS: WEIGHTS, LEARN: LEARN };
  if (typeof module !== "undefined" && module.exports) { module.exports = API; return; }

  /* ---------- UI ---------- */
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; }
  var LABEL = { ok: "Pass", warn: "Improve", fail: "Fail", info: "Info" };
  function init() {
    var form = document.getElementById("mdc-form"); if (!form) return;
    var input = document.getElementById("mdc-domain"), out = document.getElementById("mdc-out"), btn = document.getElementById("mdc-go"), stat = document.getElementById("mdc-status");
    var resolve = null;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var d = normDomain(input.value);
      out.innerHTML = "";
      if (!d) { stat.textContent = "That doesn't look like a domain name. Type something like contoso.com."; return; }
      input.value = d;
      resolve = makeResolver(window.fetch.bind(window));
      btn.disabled = true; stat.textContent = "Checking " + d + " …";
      run(d, resolve).then(function (res) { render(res); stat.textContent = "Checked " + d + " at " + new Date().toLocaleTimeString() + "."; })
        .catch(function (err) { stat.textContent = "The check failed: " + err.message + ". Your network may block DNS-over-HTTPS; try again or use another network."; })
        .then(function () { btn.disabled = false; });
    });
    function render(res) {
      var head = el("div", "mdc-sum");
      var g = el("p", "mdc-grade g-" + res.grade.toLowerCase(), res.grade);
      g.setAttribute("aria-label", "Grade " + res.grade);
      var txtb = el("div");
      txtb.appendChild(el("h2", "", res.domain));
      txtb.appendChild(el("p", "", res.nx ? "Domain not found in DNS." : "Score " + res.score + " / 100" + (res.m365 ? " · Exchange Online" : "") + (res.parked ? " · receives no mail" : "")));
      var counts = { ok: 0, warn: 0, fail: 0, info: 0 }; res.checks.forEach(function (c) { counts[c.status]++; });
      txtb.appendChild(el("p", "fine", counts.ok + " pass · " + counts.warn + " to improve · " + counts.fail + " fail · " + counts.info + " info"));
      head.appendChild(g); head.appendChild(txtb); out.appendChild(head);
      res.checks.forEach(function (c) {
        var card = el("section", "mdc-c mdc-" + c.status);
        var h = el("h3"); h.appendChild(el("span", "mdc-pill", LABEL[c.status])); h.appendChild(document.createTextNode(" " + c.title)); card.appendChild(h);
        card.appendChild(el("p", "", c.summary));
        if (c.details.length) { var ul = el("ul"); c.details.forEach(function (x) { ul.appendChild(el("li", "", x)); }); card.appendChild(ul); }
        if (c.records.length) { var pre = el("pre", "mdc-rec"); pre.appendChild(el("code", "", c.records.join("\n"))); card.appendChild(pre); }
        if (c.links.length) { var p = el("p", "mdc-links"); c.links.forEach(function (l, i) { if (i) p.appendChild(document.createTextNode(" · ")); var a = el("a", "", l.t); a.href = l.u; a.rel = "noopener"; p.appendChild(a); }); card.appendChild(p); }
        out.appendChild(card);
      });
      out.focus && out.focus();
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})(this);
