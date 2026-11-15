"""Hashtags for the share sections (X intent, Bluesky, email, native share and the visible row under the end-of-page bar).

Every page that gets a share bar (see build_ux._SHARE_RULES) gets 3-4 established, searchable community hashtags.
They are derived centrally from the item's existing metadata, so new content gets hashtags without any extra field:
  recipes   title + category            news     category + title
  guides    TAGS + TITLE                 tools    category + kind + title
  security  vendor + product + title     code     lang + tags + title
  policies  title (+ framework badges)   ai/      fixed AI set
Optional override, used as-is (1-4 tags, letters/digits only, no '#'):
  JSON items (recipes, news, tools, cyber, code, policies):  "hashtags": ["EntraID", "ConditionalAccess", "ZeroTrust"]
  guide modules (data/guides/*.py):                         HASHTAGS = ("AzureArc", "PatchManagement", "WindowsServer")
The build fails on an invalid override. Edit RULES below to change the curated mapping for everyone."""
import json, re, pathlib, importlib

ROOT = pathlib.Path(__file__).resolve().parent
TAG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]{1,24}$")
MAX, MIN = 4, 3

# (regex on the metadata text, hashtag without '#'). Matched case-insensitively; the tag that matches EARLIEST in the
# signal text (category/tags first, title last) ranks first, so the item's own category wins over incidental words.
RULES = [
    (r"copilot studio|\bagents?\b|agent 365", "CopilotStudio"),
    (r"copilot", "Copilot"),
    (r"conditional access", "ConditionalAccess"),
    (r"\bentra\b|azure ad\b|\bmfa\b|passkey|\bpim\b|\bidentity\b|sign-ins?\b|app consent|privileged role", "EntraID"),
    (r"intune|autopilot|\bwin32\b|endpoint privilege|\bepm\b|company portal|remote lock", "MicrosoftIntune"),
    (r"purview|\bdlp\b|sensitivity label|oversharing|data security|information classification", "MicrosoftPurview"),
    (r"defender|\bmdi\b|\bmdo\b|\bxdr\b|advanced hunting|custom detection|\bmdca\b|cloud apps", "DefenderXDR"),
    (r"azure arc|\barc\b|azcmagent", "AzureArc"),
    (r"azure devops", "AzureDevOps"),
    (r"exchange(?! server)|\bexo\b|\bsmtp\b|\bews\b|outlook|mailbox", "ExchangeOnline"),
    (r"\bteams\b", "MicrosoftTeams"),
    (r"active directory|\bad cs\b|\badcs\b|\bntlm\b|kerberos|domain controller|\bldap\b|hybrid identity|locksmith|\bon-prem ad\b|\bad\b", "ActiveDirectory"),
    (r"windows server", "WindowsServer"),
    (r"windows(?! server)|\blaps\b|client hardening", "Windows"),
    (r"admin by request|endpoint privilege|local admin|just-in-time elevation", "EndpointSecurity"),
    (r"zero trust|private access|vpn replacement|replace vpn", "ZeroTrust"),
    (r"powershell|\bps1\b", "PowerShell"),
    (r"\bkql\b|kusto|sign-in logs", "KQL"),
    (r"microsoft graph|\bgraph\b", "MicrosoftGraph"),
    (r"update manager|maintenance config|\bbicep\b|landing zone|\bazure\b", "Azure"),
    (r"\bai\b|\bllms?\b|genai|generative|chatgpt|openai|copilot/ai", "AI"),
    (r"\bm365\b|microsoft 365|sharepoint|onedrive|licens|retire", "Microsoft365"),
    (r"\bcve-\d", "CVE"),
    (r"pen ?test|red team|offensive|lateral movement|credential access|pivot|web apps|external exposure|vulnerability scanning|osint|attack surface", "PenTesting"),
    (r"harden|vulnerab|exploit|attack|threat|secur|phish|ransomware|malware|purple team|credential|leak|incident", "CyberSecurity"),
    (r"patch tuesday", "PatchTuesday"),
    (r"patch(?! tuesday)", "PatchManagement"),
    (r"website|web server|\bhosting\b", "WebSecurity"),
    (r"regulation|compliance|nis2|\bdora\b|gdpr|\bbod\b", "Compliance"),
    (r"dmarc|dkim|\bspf\b|domain & email", "EmailSecurity"),
    (r"esxi|vmware|vcenter", "VMware"),
]
RULES = [(re.compile(p, re.I), t) for p, t in RULES]

# Per section: (always-include tags placed right after any lead tag, fallback tags used only to reach MIN)
SECTION = {
    "recipes": ((), ("Microsoft365", "SysAdmin", "CyberSecurity")),
    "guides": ((), ("SysAdmin", "Microsoft365", "InfoSec")),
    "news": ((), ("Microsoft365", "SysAdmin", "CyberSecurity")),
    "tools": (("CyberSecurity",), ("InfoSec", "PenTesting")),
    "security-vuln": (("CVE", "CyberSecurity"), ("PatchManagement", "InfoSec")),
    "security-hardening": (("CyberSecurity",), ("InfoSec", "SysAdmin")),
    "code": ((), ("SysAdmin", "Microsoft365")),
    "policies": (("CyberSecurity",), ("ISO27001", "InfoSec", "Compliance")),
    "other": ((), ("Microsoft365", "CyberSecurity", "SysAdmin")),
}
FIXED = {  # pages that are not data items
    "ai/index.html": ("AI", "AIGovernance", "Copilot", "GenAI"),
    "ai/readiness-check/index.html": ("AI", "AIGovernance", "Copilot", "CyberSecurity"),
    "newsletter-sample.html": ("Microsoft365", "CyberSecurity", "SysAdmin"),
    "tools/mail-dns-checker.html": ("EmailSecurity", "DMARC", "DNS", "CyberSecurity"),
}
LANG = {"powershell": "PowerShell", "kql": "KQL", "bicep": "Bicep", "azurecli": "AzureCLI", "bash": "Bash", "json": "MicrosoftGraph"}
VENDOR = {"Broadcom (VMware)": "VMware", "Linux": "Linux", "Palo Alto Networks": "PaloAlto", "Barracuda Networks": "Barracuda",
          "OpenBSD (OpenSSH portable)": "OpenSSH", "PHP Group": "PHP", "BerriAI (open source)": "LiteLLM",
          "Kludex (Starlette, open source)": "Python", "Microsoft": None}


def _vendor_tag(e):
    v = (e.get("vendor") or "").strip()
    if v in VENDOR:
        return VENDOR[v]
    if v.startswith("Google"):
        return "Chrome" if "chrom" in (e.get("product") or "").lower() else "Google"
    t = re.sub(r"[^A-Za-z0-9]", "", re.split(r"[(;,]", v)[0])
    return t if TAG_RE.match(t) and len(t) <= 16 else None


def validate_override(tags, where):
    if not isinstance(tags, (list, tuple)) or not 1 <= len(tags) <= MAX:
        raise SystemExit(f"hashtags: {where}: override must be a list of 1-{MAX} tags")
    bad = [t for t in tags if not isinstance(t, str) or not TAG_RE.match(t)]
    if bad:
        raise SystemExit(f"hashtags: {where}: invalid tag(s) {bad} (letters/digits only, no '#', max 25 chars)")
    return tuple(tags)


MSFT = {"CopilotStudio", "Copilot", "ConditionalAccess", "EntraID", "MicrosoftIntune", "MicrosoftPurview", "DefenderXDR", "AzureArc",
        "AzureDevOps", "ExchangeOnline", "MicrosoftTeams", "Microsoft365", "MicrosoftGraph", "Azure"}


GENERIC = {"AI", "Microsoft365", "CyberSecurity", "SysAdmin"}


def derive(signal, section, lead=(), microsoft=True):
    must, fallback = SECTION[section]
    hits = []
    for rx, tag in RULES:
        if not microsoft and tag in MSFT:
            continue
        m = rx.search(signal)
        if m:
            hits.append((m.start() + (10000 if tag in GENERIC else 0), tag))  # broad tags rank after specific ones
    ranked = [t for _, t in sorted(hits, key=lambda x: x[0])]
    out = []
    for t in [x for x in lead if x] + list(must) + ranked:
        if t not in out:
            out.append(t)
    if "Azure" in out and ({"AzureArc", "AzureDevOps"} & set(out)):
        out.remove("Azure")  # the specific Azure tag is enough
    if "Windows" in out and "WindowsServer" in out:  # keep whichever ranks first
        out.remove("WindowsServer" if out.index("Windows") < out.index("WindowsServer") else "Windows")
    out = out[:MAX]
    for t in fallback:
        if len(out) >= MIN:
            break
        if t not in out:
            out.append(t)
    return tuple(out)


_INDEX = None


def _load(d):
    for f in sorted((ROOT / "data" / d).glob("*.json")):
        try:
            j = json.loads(f.read_text())
        except Exception:
            continue
        if isinstance(j, dict) and j.get("id"):
            yield j


def _index():
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    ix = {}

    def put(path, e, signal, section, lead=()):
        o = e.get("hashtags") if isinstance(e, dict) else None
        ix[path] = validate_override(o, path) if o is not None else derive(signal, section, lead)

    for e in _load("recipes"):
        cat = re.sub(r"\s+for (AI|Copilot)$", "", e.get("category", ""))  # "Intune & devices for AI" is about Intune, not AI
        put(f'recipes/{e["id"]}.html', e, f'{e.get("title", "")} | {cat}', "recipes")
    for e in _load("news"):
        put(f'news/{e["id"]}.html', e, f'{e.get("category", "")} | {e.get("title", "")}', "news")
    for e in _load("tools"):
        put(f'tools/{e["id"]}.html', e, f'{e.get("category", "")} | {e.get("name", "")}', "tools")
    for e in _load("cyber"):
        sec = "security-vuln" if e.get("type") == "vulnerability" else "security-hardening"
        put(f'security/{e["id"]}.html', e, f'{e.get("product", "")} | {e.get("title", "")} | {e.get("category", "")}', sec,
            lead=("PatchTuesday",) if e.get("patch_tuesday") else (_vendor_tag(e),) if sec == "security-vuln" else ())
        if sec == "security-vuln" and "hashtags" not in e and not re.search(r"microsoft", f'{e.get("vendor", "")} {e.get("product", "")}', re.I):
            ix[f'security/{e["id"]}.html'] = derive(f'{e.get("product", "")} | {e.get("title", "")}', sec, (_vendor_tag(e),), microsoft=False)
    for e in _load("code"):
        put(f'code/{e["id"]}.html', e, " | ".join(e.get("tags", [])) + f' | {e.get("title", "")}', "code",
            lead=(LANG.get(str(e.get("lang", "")).lower()),))
    for e in _load("policies"):
        put(f'policies/{e["id"]}.html', e, f'{e.get("title", "")} | {e.get("short", "")}', "policies")
    gdir = ROOT / "data" / "guides"
    import sys
    if str(gdir) not in sys.path:
        sys.path.insert(0, str(gdir))
    for f in sorted(gdir.glob("*.py")):
        if f.name.startswith("_"):
            continue
        try:
            m = importlib.import_module(f.stem)
        except Exception:
            continue
        if not getattr(m, "SLUG", None):
            continue
        p = f"guides/{m.SLUG}.html"
        o = getattr(m, "HASHTAGS", None)
        if o is not None:
            ix[p] = validate_override(o, p)
        else:
            tags = " | ".join(str(t).replace("-", " ") for t in getattr(m, "TAGS", ()) or ())
            ix[p] = derive(f'{tags} | {m.TITLE} | {getattr(m, "SHORT", "")}', "guides")
    for p, t in FIXED.items():
        ix[p] = validate_override(t, p)
    _INDEX = ix
    return ix


def for_path(path):
    """3-4 hashtags (without '#') for a site path such as 'news/foo.html'."""
    ix = _index()
    if path in ix:
        return ix[path]
    sec = path.split("/")[0] if "/" in path else "other"
    return derive(path.replace("-", " ").replace("/", " | "), sec if sec in SECTION else "other")


if __name__ == "__main__":  # python3 build_hashtags.py  -> print the derived tags for every item
    for p, t in sorted(_index().items()):
        print(f"{p:70} {' '.join('#' + x for x in t)}")
