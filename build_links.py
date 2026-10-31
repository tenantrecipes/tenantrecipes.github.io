"""Strategic internal linking (2026-10-31): topic clusters computed from the data.

A recipe, news item or security entry belongs to every cluster whose keywords appear in its id, title and summary.
Pages in the same cluster link to each other ("More in <cluster>"), and news / security entries get "Related recipes"
when they share at least one cluster keyword with a recipe. Curated cross-links go in a recipe's optional
"related": ["<recipe-id>", ...] field (shown first, validated at build time)."""
import re, sys
from html import escape as E

CLUSTERS = [
    ("identity", "Identity & access",
     ["conditional access", "mfa", "multifactor", "pim", "privileged", "break-glass", "emergency access", "identity protection",
      "sign-in risk", "user risk", "risk-based", "risk remediation", "passkey", "phishing-resistant", "sms", "consent", "legacy auth",
      "sign-in frequency", "authentication", "entra"],
     ("ca-", "entra-", "pim-")),
    ("devices", "Devices & Windows",
     ["intune", "autopilot", "compliance", "compliant", "laps", "autopatch", "windows 11", "windows", "enrollment", "device", "edge", "bitlocker"],
     ("intune-", "autopilot-")),
    ("ai", "Copilot, agents & data protection",
     ["copilot", "agent", "purview", "dlp", "sensitivity label", "oversharing", "retention", "license", "licensing",
      "restricted content discovery", "restricted search", "audit"],
     ("copilot-", "agents-", "purview-", "license-", "sharepoint-restricted")),
]
LABEL = {c: l for c, l, _, _ in CLUSTERS}
# Extra pages that belong to a cluster (shown in the recipe cluster box after the recipes)
EXTRA = {
    "identity": [("Cloud hardening + adversary emulation", "guides/cloud-hardening-adversary-emulation.html"), ("Replace VPN with Entra Private Access", "guides/entra-private-access-vpn-replacement.html")],
    "devices": [("Windows 11 CIS hardening guide", "guides/windows-11-cis-hardening.html"), ("Azure Arc onboarding at enterprise scale", "guides/azure-arc-onboarding-enterprise-scale.html"), ("Azure Update Manager at enterprise scale", "guides/azure-update-manager-enterprise-patching.html"), ("Remove local admin rights with Admin By Request", "guides/admin-by-request-endpoint-privilege.html"), ("Package Admin By Request for Intune (Win32)", "guides/admin-by-request-intune-win32-packaging.html"), ("Windows LAPS hardening", "security/harden-windows-laps.html")],
    "ai": [("Secure Copilot rollout guide", "guides/secure-copilot-rollout.html"), ("Copilot license pre-flight checks", "guides/copilot-license-checks.html")],
}


def _text(x):
    return " ".join(str(x.get(k) or "") for k in ("id", "title", "problem", "summary", "category")).lower().replace("-", " ") + " " + x.get("id", "")


def keywords(x):
    t = _text(x)
    return {k for _, _, kws, _ in CLUSTERS for k in kws if re.search(r"(?<![a-z])" + re.escape(k), t)}


def clusters(x):
    t, kw, i = _text(x), keywords(x), x.get("id", "")
    return [c for c, _, kws, pre in CLUSTERS if i.startswith(pre) or (kw & set(kws))]


def check(R):
    ids = {r["id"] for r in R}
    bad = [f'{r["id"]}: unknown related id {x}' for r in R for x in r.get("related", []) if x not in ids or x == r["id"]]
    if bad:
        sys.exit("Invalid 'related' links:\n  " + "\n  ".join(bad))


def score(a, b):
    ca, cb = set(clusters(a)), set(clusters(b))
    return 3 * len(ca & cb) + 2 * len(keywords(a) & keywords(b))


GENERIC = {"entra", "authentication", "device", "windows", "windows 11", "enrollment", "audit", "agent", "compliance", "compliant", "edge", "license", "licensing"}
STOP = set("about after their there these those which while with without from into your this that have will when what where before every other users user admin admins microsoft tenant policy policies".split())


def _words(x):
    return {w for w in re.findall(r"[a-z][a-z0-9]{3,}", _text(x)) if w not in STOP}


def recipe_matches(x, R, n=3, skip=(), min_kw=1):
    """Recipes that share at least `min_kw` specific (non-generic) cluster keywords with x (news item or security entry),
    ranked by shared keywords, clusters and title/summary word overlap."""
    kx = keywords(x) - GENERIC
    wx = _words(x)
    out = []
    for r in R:
        if r["id"] in skip:
            continue
        shared = kx & keywords(r)
        if len(shared) >= min_kw:
            out.append((4 * len(shared) + 3 * len(set(clusters(x)) & set(clusters(r))) + len(wx & _words(r))
                        + (6 if r["id"] == x.get("recipe") else 0), r.get("order", 0), r))
    out.sort(key=lambda t: (-t[0], t[1]))
    return [r for _, _, r in out[:n]]


def cluster_box(rel, r, R, shown, news, esc):
    """'More in <cluster>' link list on a recipe page: other recipes in the same clusters, matching news, guides."""
    mine = clusters(r)
    if not mine:
        return ""
    cand = sorted((x for x in R if x["id"] != r["id"] and x["id"] not in shown and set(clusters(x)) & set(mine)),
                  key=lambda x: (-score(r, x), x.get("order", 0)))[:6]
    li = "".join(f'<li><a href="{rel}recipes/{x["id"]}.html">{esc(x["title"])}</a></li>' for x in cand)
    nw = [e for e in news if e.get("recipe") == r["id"] or (set(clusters(e)) & set(mine) and keywords(e) & keywords(r))][:2]
    li += "".join(f'<li><a href="{rel}news/{e["id"]}.html"><span class="cl-t">News</span> {esc(e["title"])}</a></li>' for e in nw)
    li += "".join(f'<li><a href="{rel}{u}"><span class="cl-t">Guide</span> {esc(t)}</a></li>' if u.startswith("guides/")
                  else f'<li><a href="{rel}{u}"><span class="cl-t">Hardening</span> {esc(t)}</a></li>' for t, u in EXTRA.get(mine[0], []))
    labels = " · ".join(esc(LABEL[c]) for c in mine)
    return f'<div class="cl-box"><p class="cl-h">More in this topic cluster: {labels}</p><ul class="cl-l">{li}</ul></div>'


def related_list_html(rel, items, esc):
    return "".join(f'<li><a href="{rel}recipes/{x["id"]}.html">{esc(x["title"])}</a> <span class="fine">· recipe</span></li>' for x in items)
