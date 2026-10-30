"""Policy Templates section (/policies/).

Data: one JSON file per template in data/policies/<id>.json. Bodies are written in our own words; nothing is
copied from SANS, ISO, NIST or other template libraries. Framework references only use identifiers checked on
the official sources below (ISO/IEC 27001:2022 Annex A themes, NIST CSF 2.0 categories, CIS Controls v8).
Downloads (.md and .docx) live in downloads/policies/ and are regenerated when the data changes
(python-docx needed for .docx); the build fails if they are stale and cannot be regenerated."""
import json, re, sys, hashlib, pathlib
import build_trust as T

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "data" / "policies"
OUT = ROOT / "downloads" / "policies"
GEN_VERSION = "4"
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PH = re.compile(r"\{\{([A-Z_]+)\}\}")
COMMON_PH = {
    "COMPANY": "Your organization's legal or trading name",
    "OWNER": "Role that owns this policy, e.g. Head of IT or CISO",
    "APPROVER": "Who approved it, e.g. Management team",
    "EFFECTIVE_DATE": "Date the policy takes effect",
    "REVIEW_DATE": "Next planned review date",
    "SECURITY_CONTACT": "Where to report security issues, e.g. security@yourcompany.example",
}
EXTRA_PH = {
    "IT_SERVICE_DESK": "How to reach the IT service desk",
    "MIN_PASSWORD_LENGTH": "Minimum password length, e.g. 14",
    "MDM_TOOL": "Your device management tool, e.g. Microsoft Intune",
    "APPROVED_AI_TOOLS": "Where the list of approved AI tools is published",
    "IR_LEAD": "Role that leads incident response",
    "RPO_HOURS": "Default recovery point objective in hours",
    "RTO_HOURS": "Default recovery time objective in hours",
    "RETENTION_DAYS": "Minimum backup retention in days",
    "LEAVER_HOURS": "Hours after the last day by which leaver accounts are disabled",
    "ACCESS_REVIEW_MONTHS": "Months between access reviews",
    "PATCH_DAYS_CRITICAL": "Days to fix critical or exploited vulnerabilities",
    "PATCH_DAYS_HIGH": "Days to fix high vulnerabilities",
    "PATCH_DAYS_OTHER": "Days to fix medium and low vulnerabilities",
}
ISO = {  # ISO/IEC 27001:2022 Annex A / ISO/IEC 27002:2022 control themes (clause numbers)
    "Organizational": "Organizational controls (clause 5)", "People": "People controls (clause 6)",
    "Physical": "Physical controls (clause 7)", "Technological": "Technological controls (clause 8)"}
CSF = {  # NIST CSF 2.0 (CSWP 29) categories used here
    "GV.PO": "Policy", "GV.RR": "Roles, Responsibilities, and Authorities", "GV.SC": "Cybersecurity Supply Chain Risk Management",
    "ID.AM": "Asset Management", "ID.RA": "Risk Assessment", "PR.AA": "Identity Management, Authentication, and Access Control",
    "PR.AT": "Awareness and Training", "PR.DS": "Data Security", "PR.PS": "Platform Security", "PR.IR": "Technology Infrastructure Resilience",
    "DE.AE": "Adverse Event Analysis", "RS.MA": "Incident Management", "RS.AN": "Incident Analysis",
    "RS.CO": "Incident Response Reporting and Communication", "RS.MI": "Incident Mitigation",
    "RC.RP": "Incident Recovery Plan Execution", "RC.CO": "Incident Recovery Communication"}
CSF_FN = {"GV": "Govern", "ID": "Identify", "PR": "Protect", "DE": "Detect", "RS": "Respond", "RC": "Recover"}
CIS = {1: "Inventory and Control of Enterprise Assets", 2: "Inventory and Control of Software Assets", 3: "Data Protection",
       4: "Secure Configuration of Enterprise Assets and Software", 5: "Account Management", 6: "Access Control Management",
       7: "Continuous Vulnerability Management", 8: "Audit Log Management", 9: "Email and Web Browser Protections",
       10: "Malware Defenses", 11: "Data Recovery", 12: "Network Infrastructure Management", 13: "Network Monitoring and Defense",
       14: "Security Awareness and Skills Training", 15: "Service Provider Management", 16: "Application Software Security",
       17: "Incident Response Management", 18: "Penetration Testing"}
SOURCES = [
    {"title": "ISO/IEC 27001:2022 – Information security management systems", "url": "https://www.iso.org/standard/27001", "checked": "2026-10-30"},
    {"title": "ISO/IEC JTC 1/SC 27 Journal: special issue on ISO/IEC 27002 (four control themes)",
     "url": "https://committee.iso.org/files/live/sites/jtc1sc27/files/resources/ISO-IECJTC1-SC27_N22394_SC%2027%20Journal%20Volume%202%2C%20Issue%202%20-%20Special%20issue%20on%20ISO-IEC%2027002.pdf", "checked": "2026-10-30"},
    {"title": "NIST Cybersecurity Framework (CSF) 2.0 – CSWP 29", "url": "https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf", "checked": "2026-10-30"},
    {"title": "CIS Critical Security Controls list", "url": "https://www.cisecurity.org/controls/cis-controls-list", "checked": "2026-10-30"},
]
NOTICE = "Template, not legal advice. Adapt it with your legal and HR teams before you adopt it."
REQ = ["id", "status", "title", "short", "purpose", "audience", "review", "frameworks", "body", "last_verified"]


def _placeholders(e):
    txt = json.dumps({k: e[k] for k in ("purpose", "audience", "body")})
    return set(PH.findall(txt))


def _validate(e, fname):
    err = [f"missing {k}" for k in REQ if e.get(k) in (None, "", [], {})]
    if e.get("id") and fname != e["id"] + ".json":
        err.append("file name must equal id")
    allowed = set(COMMON_PH) | set(e.get("extra_placeholders", []))
    used = _placeholders(e) if not err else set()
    if used - allowed:
        err.append(f"undeclared placeholders {sorted(used - allowed)}")
    for x in e.get("extra_placeholders", []):
        if x not in EXTRA_PH:
            err.append(f"unknown placeholder {x} (add a description in EXTRA_PH)")
    fw = e.get("frameworks") or {}
    err += [f"unknown ISO theme {x}" for x in fw.get("iso", []) if x not in ISO]
    err += [f"unknown CSF category {x}" for x in fw.get("csf", []) if x not in CSF]
    err += [f"unknown CIS control {x}" for x in fw.get("cis", []) if x not in CIS]
    for s in e.get("body", []):
        if not s.get("h") or not (s.get("p") or s.get("items")):
            err.append(f"section needs h and p or items: {s.get('h')}")
    if e.get("last_verified") and not DATE.match(e["last_verified"]):
        err.append("last_verified must be YYYY-MM-DD")
    return err


def load():
    out, bad = [], []
    for f in sorted(SRC.glob("*.json")):
        e = json.loads(f.read_text())
        errs = _validate(e, f.name)
        if errs:
            bad.append(f"{f.name}: " + "; ".join(errs))
        elif e["status"] == "published":
            e["sources"] = SOURCES
            out.append(e)
    if bad:
        print("Invalid policy data:\n  " + "\n  ".join(bad), file=sys.stderr)
        sys.exit(1)
    return sorted(out, key=lambda e: e.get("order", 0))


def ph_list(e):
    return [(k, COMMON_PH[k]) for k in COMMON_PH] + [(k, EXTRA_PH[k]) for k in e.get("extra_placeholders", [])]


def fw_rows(e):
    fw = e["frameworks"]
    return ([("ISO/IEC 27001:2022 Annex A theme", ISO[x]) for x in fw.get("iso", [])]
            + [("NIST CSF 2.0", f"{CSF_FN[x[:2]]} · {x} {CSF[x]}") for x in fw.get("csf", [])]
            + [("CIS Controls v8", f"Control {x}: {CIS[x]}") for x in fw.get("cis", [])])


# ------------------------------------------------------------------ downloads
def to_markdown(e):
    L = [f"# {e['title']}", "", f"> **{NOTICE}**", "", "| | |", "|---|---|",
         f"| Purpose | {e['purpose']} |", f"| Audience | {e['audience']} |", f"| Review | {e['review']} |",
         "| Owner | {{OWNER}} |", "| Approved by | {{APPROVER}} |", "| Effective | {{EFFECTIVE_DATE}} |", "| Next review | {{REVIEW_DATE}} |", ""]
    for i, s in enumerate(e["body"], 1):
        L += [f"## {i}. {s['h']}", ""]
        for p in s.get("p", []):
            L += [p, ""]
        for it in s.get("items", []):
            L.append(f"- {it}")
        if s.get("items"):
            L.append("")
    L += ["## Framework references", "", "Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.", ""]
    L += [f"- **{a}:** {b}" for a, b in fw_rows(e)] + [""]
    L += ["## Placeholders to replace", ""] + [f"- `{{{{{k}}}}}`: {d}" for k, d in ph_list(e)] + [""]
    L += ["---", "", "Template from Tenant Recipes (https://tenantrecipes.github.io/policies/). Free to adapt for use in your organization.",
          "Independent and not affiliated with Microsoft, ISO, NIST or CIS.", ""]
    return "\n".join(L)


def to_docx(e, path):
    import docx
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_COLOR_INDEX
    import datetime as dt
    d = docx.Document()
    st = d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(11)

    def para(text, style=None, bold=False):
        p = d.add_paragraph(style=style)
        for i, part in enumerate(PH.split(text)):
            if i % 2:
                r = p.add_run("{{" + part + "}}"); r.font.highlight_color = WD_COLOR_INDEX.YELLOW; r.bold = bold
            elif part:
                r = p.add_run(part); r.bold = bold
        return p
    d.add_heading(e["title"], 0)
    n = para(NOTICE, bold=True); n.runs[0].font.color.rgb = RGBColor(0x9A, 0x34, 0x12)
    from docx.shared import Cm
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    t = d.add_table(rows=0, cols=2); t.style = "Light Grid Accent 1"; t.autofit = False
    W = (Cm(4.2), Cm(11.8))  # fixed label/value columns (A4 text width ~16 cm)
    for k, v in [("Purpose", e["purpose"]), ("Audience", e["audience"]), ("Review cadence", e["review"]), ("Policy owner", "{{OWNER}}"),
                 ("Approved by", "{{APPROVER}}"), ("Effective date", "{{EFFECTIVE_DATE}}"), ("Next review", "{{REVIEW_DATE}}")]:
        c = t.add_row().cells; c[0].text = k
        for cell, w in zip(c, W):
            cell.width = w
        c[1].paragraphs[0].text = ""
        for i, part in enumerate(PH.split(v)):
            r = c[1].paragraphs[0].add_run("{{" + part + "}}" if i % 2 else part)
            if i % 2:
                r.font.highlight_color = WD_COLOR_INDEX.YELLOW
    grid = t._tbl.tblGrid
    for gc, w in zip(grid.findall(qn("w:gridCol")), W):
        gc.set(qn("w:w"), str(int(w.twips)))
    tp = t._tbl.tblPr
    lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tp.append(lay)
    look = tp.find(qn("w:tblLook"))
    if look is None:
        look = OxmlElement("w:tblLook"); tp.append(look)
    look.set(qn("w:firstRow"), "0"); look.set(qn("w:val"), "0420")  # no header-row styling: every row is label | value
    for row in t.rows:
        row.cells[0].paragraphs[0].runs[0].bold = True
        for r in row.cells[1].paragraphs[0].runs:
            r.bold = False
    for i, s in enumerate(e["body"], 1):
        d.add_heading(f"{i}. {s['h']}", 1)
        for p in s.get("p", []):
            para(p)
        for it in s.get("items", []):
            para(it, "List Bullet")
    d.add_heading("Framework references", 1)
    para("Indicative mapping prepared by Tenant Recipes; confirm against your own statement of applicability.")
    for a, b in fw_rows(e):
        para(f"{a}: {b}", "List Bullet")
    d.add_heading("Placeholders to replace", 1)
    for k, v in ph_list(e):
        para("{{" + k + "}}" + f": {v}", "List Bullet")
    para("Template from Tenant Recipes (tenantrecipes.github.io/policies/). Independent and not affiliated with Microsoft, ISO, NIST or CIS.")
    cp = d.core_properties
    cp.title = e["title"]; cp.author = "Tenant Recipes"; cp.last_modified_by = "Tenant Recipes"; cp.comments = NOTICE
    cp.created = cp.modified = dt.datetime.fromisoformat(e["updated"] + "T00:00:00")
    d.save(path)


def _hash(e):
    src = {k: v for k, v in e.items() if k != "sources"}
    blob = json.dumps([GEN_VERSION, src, ISO, CSF, CIS, COMMON_PH, EXTRA_PH, NOTICE], sort_keys=True)
    return hashlib.sha256((blob + pathlib.Path(__file__).read_text()).encode()).hexdigest()[:16]


def ensure_downloads(ents):
    OUT.mkdir(parents=True, exist_ok=True)
    man_p = OUT / "manifest.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    stale = [e for e in ents if man.get(e["id"]) != _hash(e) or not (OUT / f'{e["id"]}.docx').exists() or not (OUT / f'{e["id"]}.md').exists()]
    if stale:
        try:
            import docx  # noqa: F401
        except ImportError:
            print("Policy downloads are stale and python-docx is missing: run `pip install python-docx` and build again locally: "
                  + ", ".join(e["id"] for e in stale), file=sys.stderr)
            sys.exit(1)
        for e in stale:
            (OUT / f'{e["id"]}.md').write_text(to_markdown(e))
            to_docx(e, OUT / f'{e["id"]}.docx')
            man[e["id"]] = _hash(e)
        man_p.write_text(json.dumps(dict(sorted(man.items())), indent=1) + "\n")
        print(f"Policy downloads regenerated: {len(stale)}")


# ------------------------------------------------------------------ pages
def _ph_html(esc, s):
    return PH.sub(lambda m: f'<mark class="ph">{{{{{m.group(1)}}}}}</mark>', esc(s))


def notice():
    return (f'<aside class="tl-perm pl-notice" role="note">{T.icon("alert")}<span><strong>Template, not legal advice.</strong> '
            'Adapt it with your legal and HR teams, check local law and works-council or union rules, and remove anything that does not fit '
            'before you adopt it.</span></aside>')


def build(page, esc, signup, fmt_date, E, SITE_NAME):
    ents = load()
    ensure_downloads(ents)
    pages = []
    last = max(e["last_verified"] for e in ents)

    def dl(rel, e, cls=""):
        return (f'<div class="pl-dl {cls}"><a class="btn p" href="{rel}downloads/policies/{e["id"]}.docx" download>{T.icon("download") if "download" in T._P else ""}Word (.docx)</a>'
                f'<a class="btn" href="{rel}downloads/policies/{e["id"]}.md" download>Markdown (.md)</a></div>')

    def landing(rel):
        cards = "".join(f'<a class="card pl-card" href="{rel}policies/{e["id"]}.html"><div class="tag">Policy template</div><h3>{esc(e["title"])}</h3>'
                        f'<p class="clamp">{_ph_html(esc, e["purpose"])}</p><p class="tl-meta"><span class="tl-cost">.docx + .md</span>'
                        f'<span>Review: {esc(e["review"].split(",")[0].rstrip("."))}</span></p></a>' for e in ents)
        return (f'<section class="gd-hero cy-hero"><div class="hx-bg" aria-hidden="true"><i class="o1"></i><i class="o2"></i><i class="o3"></i></div><div class="wrap">'
                f'<p class="gd-crumb"><a href="{rel}index.html">Home</a> / Policy templates</p>'
                f'<p class="hx-badge"><span class="dot" aria-hidden="true"></span>Framework references checked on official sources · {fmt_date(last)}</p>'
                '<h1>Security policy templates.<br><span class="grad">Plain language, ready to adapt.</span></h1>'
                '<p class="hx-lead">Ten short IT security policies written from scratch for small and mid-sized organizations on Microsoft 365. '
                'Replace the placeholders, adapt with your legal and HR teams, and download as Word or Markdown. References: ISO/IEC 27001, NIST CSF 2.0 and CIS Controls v8.</p>'
                f'<dl class="hx-stats"><div><dt>Templates</dt><dd>{len(ents)}</dd></div><div><dt>Formats</dt><dd>.docx · .md</dd></div>'
                '<div><dt>Frameworks referenced</dt><dd>3</dd></div></dl></div></section>'
                f'<main class="wrap">{notice()}'
                f'<section class="sec" aria-labelledby="pl-h"><p class="sec-k">Templates</p><h2 id="pl-h">Pick a policy</h2><div class="grid">{cards}</div></section>'
                '<section class="sec"><p class="sec-k">How to use them</p><h2>From template to adopted policy</h2><ol class="steps">'
                '<li><div>Download the Word file and replace every highlighted <code>{{PLACEHOLDER}}</code>.</div></li>'
                '<li><div>Delete rules that do not fit your organization and add the ones you need; a short policy people follow beats a long one they ignore.</div></li>'
                '<li><div>Review with legal, HR and, where required, employee representatives, then have it approved by management.</div></li>'
                '<li><div>Publish it where staff can find it, explain the changes, and set the review date in your calendar.</div></li></ol></section>'
                + T.ad_slot("policies-between-sections") +
                '<p class="fine">Independent and not affiliated with Microsoft, ISO, NIST or CIS. The texts are original and free to adapt for use in your organization. '
                'Framework references are an indicative mapping, not an official crosswalk.</p>'
                f'{signup(rel, "policies-index")}</main>')
    pages.append(page("policies/index.html", f"IT security policy templates (Word & Markdown) | {SITE_NAME}",
                      "Ten free, plain-language IT security policy templates for Microsoft 365 organizations, with placeholders and ISO 27001, NIST CSF 2.0 and CIS v8 references.",
                      landing))
    for e in ents:
        def body(rel, e=e):
            path = f'policies/{e["id"]}.html'
            secs = ""
            for i, s in enumerate(e["body"], 1):
                secs += f'<h3 id="s{i}">{i}. {esc(s["h"])}</h3>' + "".join(f'<p>{_ph_html(esc, p)}</p>' for p in s.get("p", []))
                if s.get("items"):
                    secs += '<ul>' + "".join(f'<li>{_ph_html(esc, x)}</li>' for x in s["items"]) + '</ul>'
            fw = "".join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>' for a, b in fw_rows(e))
            phs = "".join(f'<tr><td><code>{{{{{k}}}}}</code></td><td>{esc(v)}</td></tr>' for k, v in ph_list(e))
            meta = (f'<dl class="cy-facts"><div><dt>Purpose</dt><dd>{_ph_html(esc, e["purpose"])}</dd></div>'
                    f'<div><dt>Audience</dt><dd>{_ph_html(esc, e["audience"])}</dd></div><div><dt>Review cadence</dt><dd>{esc(e["review"])}</dd></div></dl>')
            chips = T.chip("list", f'{len(e["body"])} sections') + T.chip("layers", f'{len(fw_rows(e))} framework references') + T.chip("download" if "download" in T._P else "link", ".docx + .md")
            toc = [("about", "About this template"), ("download", "Download"), ("policy", "Policy text"), ("frameworks", "Framework references"),
                   ("placeholders", "Placeholders"), ("verified", "Sources & corrections")]
            rel_items = [(x["title"], f'{rel}policies/{x["id"]}.html') for x in ents if x["id"] != e["id"]][:6]
            return (T.page_hero(rel, T.crumbs_dark(rel, path, [("Home", rel + "index.html"), ("Policy templates", rel + "policies/index.html"), (e["short"], None)]),
                                f'{T.icon("shield")}Policy template', esc(e["title"]), "", chips, kind="cyber")
                    + '<main class="wrap pg"><div class="pg-grid"><article class="doc">' + notice()
                    + f'<h2 id="about">About this template</h2>{meta}'
                    + f'<h2 id="download">Download</h2><p>Editable files with the same text. Placeholders are highlighted in the Word file.</p>{dl(rel, e)}'
                    + f'<h2 id="policy">Policy text</h2><div class="pl-body">{secs}</div>'
                    + f'<h2 id="frameworks">Framework references</h2><p class="fine">Indicative mapping prepared by us to identifiers checked on the official ISO, NIST and CIS sources. '
                    'It is not an official crosswalk; confirm against your own statement of applicability. ISO control-level numbers are not listed because the control text is copyrighted.</p>'
                    f'<div class="cy-tw"><table class="cy-t"><thead><tr><th>Framework</th><th>Reference</th></tr></thead><tbody>{fw}</tbody></table></div>'
                    + f'<h2 id="placeholders">Placeholders to replace</h2><div class="cy-tw"><table class="cy-t"><thead><tr><th>Placeholder</th><th>Replace with</th></tr></thead><tbody>{phs}</tbody></table></div>'
                    + T.trust_bottom(rel, path, e["title"], e, "Framework references checked against") + '</article>'
                    + T.side_nav(rel, toc, rel_items, "More policy templates")
                    + '</div>' + signup(rel, "policies-" + e["id"]) + '</main>')
        desc = f'Free {e["short"].lower()} policy template in plain English: ' + PH.sub(lambda m: "your company" if m.group(1) == "COMPANY" else m.group(1).lower(), e["purpose"])
        desc = desc if len(desc) <= 160 else desc[:157].rsplit(" ", 1)[0] + "…"
        pages.append(page(f'policies/{e["id"]}.html', f'{e["title"]} template | {SITE_NAME}', desc, body, "article"))
    print(f"Policy templates: {len(ents)} templates, {len(pages)} pages")
    return pages


def search_docs():
    out = [{"t": "Security policy templates", "k": "Page", "c": "Site", "u": "policies/index.html",
            "s": "Ten free plain-language IT security policy templates with Word and Markdown downloads."}]
    for e in load():
        txt = " ".join(" ".join(s.get("p", []) + s.get("items", [])) for s in e["body"])
        out.append({"t": e["title"], "k": "Policy", "c": "Policy template", "g": [e["short"]], "s": PH.sub(lambda m: "your organization" if m.group(1) == "COMPANY" else m.group(1).lower().replace("_", " "), e["purpose"])[:220],
                    "x": PH.sub("", txt)[:420], "u": f'policies/{e["id"]}.html', "d": e.get("updated")})
    return out
