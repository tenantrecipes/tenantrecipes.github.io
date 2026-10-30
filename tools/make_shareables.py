"""Generate the shareable files that are committed to the repo (headless Chrome needed):
  downloads/<guide>-checklist.pdf   printable checklist per pillar guide (original wording from data/guides/*.py)
  downloads/copilot-license-checks.pdf   the 1-page quick guide
  assets/og/*.png                   1200x630 Open Graph / Twitter card images per section, category and guide
Run:  python3 tools/make_shareables.py [--force]
build.py calls this automatically when its inputs changed and Chrome is available; otherwise the committed files are used."""
import sys, json, re, hashlib, shutil, subprocess, tempfile, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "data" / "guides"))
import site_config as C
import secure_copilot_rollout as G1, windows_11_cis_hardening as G2, quick_copilot_license_checks as Q
DL, OG = ROOT / "downloads", ROOT / "assets" / "og"
MANIFEST = DL / "manifest.json"
SITE = C.SITE_URL.rstrip("/")
E = lambda s: html.escape(str(s), quote=True)


def chrome():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if shutil.which(c):
            return shutil.which(c)
    return None


def inputs_hash():
    h = hashlib.sha256()
    files = [ROOT / "tools/make_shareables.py", ROOT / "site_config.py", ROOT / "assets/mark.svg"] + sorted((ROOT / "data/guides").glob("*.py"))
    for f in files:
        h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()


def code(s):
    parts = s.split("`")
    return "".join(E(p) if i % 2 == 0 else f"<code>{E(p)}</code>" for i, p in enumerate(parts))


MARK = (ROOT / "assets" / "mark.svg").read_text()
BASE_CSS = """*{box-sizing:border-box}body{font-family:Inter,"Noto Sans","Segoe UI",system-ui,sans-serif;color:#0e1424;margin:0}
code{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.92em;background:#f1f3f8;padding:0 3px;border-radius:3px}
.hd{display:flex;align-items:center;gap:10px;border-bottom:2px solid #0f2f6b;padding-bottom:8px;margin-bottom:10px}
.hd svg{width:28px;height:28px}.hd b{font-size:15px;color:#0f2f6b}.hd span{margin-left:auto;font-size:9pt;color:#5d667c;text-align:right}
h1{font-size:17pt;line-height:1.2;margin:6px 0 4px}.lead{font-size:9.5pt;color:#3b4357;margin:0 0 10px}
.ft{margin-top:12px;border-top:1px solid #e2e6ef;padding-top:6px;font-size:7.5pt;color:#5d667c}"""


def checklist_html(g):
    rows = ""
    for i, ph in enumerate(g.PHASES, 1):
        rows += f'<h2><span>Phase {i}</span> {E(ph["title"])} <em>about {E(ph["time"])}</em></h2><ul>'
        rows += "".join(f'<li><i></i><div><b>{i}.{j} {code(st["t"])}</b><br>{code(st["check"])}</div></li>' for j, st in enumerate(ph["steps"], 1))
        rows += "</ul>"
    n = sum(len(p["steps"]) for p in g.PHASES)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
@page{{size:A4;margin:14mm 14mm 14mm 14mm}}body{{font-size:9pt}}
h2{{font-size:10.5pt;margin:12px 0 4px;color:#0f2f6b;break-after:avoid}}h2 span{{background:#0f2f6b;color:#fff;border-radius:4px;padding:1px 6px;font-size:8.5pt;margin-right:4px}}
h2 em{{font-weight:400;font-style:normal;color:#5d667c;font-size:8.5pt}}
ul{{list-style:none;margin:0;padding:0}}li{{display:flex;gap:8px;padding:4px 0;border-bottom:1px solid #eef1f6;break-inside:avoid}}
li i{{flex:none;width:11px;height:11px;border:1.5px solid #0f2f6b;border-radius:2px;margin-top:2px}}li b{{font-weight:650}}
.meta{{display:flex;gap:10px;flex-wrap:wrap;font-size:8.5pt;margin:6px 0 4px}}.meta span{{border:1px solid #d5dbe7;border-radius:99px;padding:1px 8px}}
.sig{{margin-top:14px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;font-size:8.5pt;color:#3b4357}}.sig div{{border-top:1px solid #0e1424;padding-top:3px}}
</style></head><body><div class="hd">{MARK}<b>Tenant Recipes</b><span>Printable checklist<br>Verified {g.VERIFIED}</span></div>
<h1>{E(g.TITLE)}</h1><p class="lead">{E(g.DESC)}</p>
<div class="meta"><span>{len(g.PHASES)} phases</span><span>{n} steps</span><span>Tick each item when its "done when" criterion is true</span></div>
{rows}<div class="sig"><div>Owner</div><div>Change / ticket</div><div>Date completed</div></div>
<p class="ft">Original checklist by Tenant Recipes, an independent project not affiliated with Microsoft{", CIS" if g is G2 else ""} or any vendor. Every step, its actions, pitfalls and the official sources it was checked against are on
{SITE}/guides/{g.SLUG}.html. Time estimates are our own planning figures. Confirm against the linked sources and test in a pilot before production.</p></body></html>"""


def quick_html():
    items = ""
    for n, c in enumerate(Q.CHECKS, 1):
        src = " · ".join(E(Q.S[k][1].replace("https://learn.microsoft.com/en-us/", "learn.microsoft.com/…/")) for k in c["src"])
        items += (f'<li><span class="n">{n}</span><div><h2>{E(c["t"])}</h2><p>{E(c["why"])}</p>'
                  f'<p class="ck"><i></i><b>Check:</b> {E(c["check"])}</p><p class="s">Source: {src}</p></div></li>')
    th = Q.THEN
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}
@page{{size:A4;margin:12mm 14mm}}body{{font-size:9.2pt}}
ol{{list-style:none;margin:0;padding:0}}li{{display:flex;gap:10px;padding:7px 0;border-bottom:1px solid #eef1f6;break-inside:avoid}}
.n{{flex:none;width:24px;height:24px;border-radius:7px;background:linear-gradient(135deg,#1f7bff,#7a4dff);color:#fff;font-weight:800;display:grid;place-items:center}}
h2{{font-size:11pt;margin:0 0 2px}}p{{margin:2px 0}}.ck{{background:#e8f7ef;border-radius:5px;padding:4px 8px;display:flex;gap:6px;align-items:flex-start}}
.ck i{{flex:none;width:10px;height:10px;border:1.5px solid #0f7a4f;border-radius:2px;margin-top:2px}}.s{{font-size:7.5pt;color:#5d667c}}
.then{{margin-top:8px;padding:8px 10px;border:1px solid #d3e1fb;background:#eef4ff;border-radius:6px}}
</style></head><body><div class="hd">{MARK}<b>Tenant Recipes</b><span>Quick guide · 1 page<br>Verified against Microsoft Learn {Q.VERIFIED}</span></div>
<h1>{E(Q.TITLE)}</h1><p class="lead">A pre-flight check before the first Copilot license lands. Wording is ours; each item names the Microsoft Learn page it was checked against.</p>
<ol>{items}</ol><div class="then"><b>{E(th["t"])}.</b> {E(th["text"])}</div>
<p class="ft">Tenant Recipes is independent and not affiliated with Microsoft. Full version with links and hands-on recipes: {SITE}/guides/{Q.SLUG}.html.
Licensing and requirements change: confirm against the linked sources before you act.</p></body></html>"""


def og_html(kicker, title, sub, pills, accent="#7a4dff"):
    p = "".join(f"<div>{E(x)}</div>" for x in pills)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{font-family:Inter,"Noto Sans",system-ui,sans-serif;color:#fff;background:radial-gradient(circle at 88% 12%,{accent}cc,transparent 42%),linear-gradient(135deg,#071027,#0f2f6b 55%,#2a1360);
display:flex;flex-direction:column;justify-content:center;padding:0 84px;box-sizing:border-box}}
.logo{{font-size:34px;font-weight:800;display:flex;align-items:center;gap:16px}}.logo svg{{width:58px;height:58px}}.logo span{{color:#9fd0ff}}
.k{{margin-top:44px;font-size:24px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#b9c6ff}}
h1{{font-size:{66 if len(title) < 48 else 56}px;line-height:1.07;margin:14px 0 20px;font-weight:800;letter-spacing:-1.2px;max-width:1030px}}
p{{font-size:28px;margin:0;opacity:.9;max-width:1000px}}
.pills{{display:flex;gap:12px;margin-top:38px;flex-wrap:wrap}}.pills div{{border:2px solid #ffffff88;border-radius:999px;padding:6px 20px;font-size:22px;font-weight:600}}
.url{{position:absolute;right:84px;bottom:34px;font-size:22px;color:#c9d4f5}}
</style></head><body><div class="logo">{MARK}<div>Tenant<span>Recipes</span></div></div>
<div class="k">{E(kicker)}</div><h1>{E(title)}</h1><p>{E(sub)}</p><div class="pills">{p}</div><div class="url">{E(SITE.replace("https://", ""))}</div></body></html>"""


def og_specs():
    cats = {
        "copilot": ("Copilot rollout & governance", "Roll out Copilot the right way", ["Licensing", "Readiness", "Teams", "Web search"]),
        "conditional-access": ("Conditional Access for AI", "Conditional Access for the AI era", ["Phishing-resistant MFA", "Report-only", "Break-glass"]),
        "intune": ("Intune & devices for AI", "Intune and devices for AI", ["Compliance", "App protection", "Update channels"]),
        "purview": ("Purview, DLP & data security for Copilot", "Stop oversharing before Copilot finds it", ["Purview", "DLP", "Labels", "Audit"]),
        "identity": ("Identity & threat protection", "Identity and threat protection", ["Passkeys", "Risk policies", "Guests", "Teams phishing"]),
        "agents": ("Agents & Copilot Studio governance", "Govern agents and Copilot Studio", ["Agent registry", "Consent", "Data policies"]),
        "licensing": ("Licensing & reporting", "Copilot licensing and usage reporting", ["Usage reports", "Graph", "License inventory"]),
        "prompts": ("Admin prompt templates", "Prompt templates for M365 admins", ["Conditional Access", "Comms", "Help desk"]),
    }
    out = {}
    for slug, (cat, title, pills) in cats.items():
        out[f"cat-{slug}"] = og_html(f"Recipe · {cat}", title, "Fact-checked, step-by-step recipes, each linked to Microsoft Learn.", pills)
    ns = lambda g: sum(len(p["steps"]) for p in g.PHASES)
    out["guide-secure-copilot-rollout"] = og_html("Pillar guide", "Roll out Microsoft Copilot without opening a hole in your tenant",
        f"{len(G1.PHASES)} phases · {ns(G1)} steps · printable checklist PDF", ["Oversharing", "Conditional Access", "Labels & DLP", "Pilot"], "#1f7bff")
    out["guide-windows-11-cis-hardening"] = og_html("Pillar guide", "Harden Windows 11 with the CIS Benchmark",
        f"{len(G2.PHASES)} phases · {ns(G2)} steps · Level 1 vs 2, Intune vs GPO, compliance scans", ["CIS", "Security baselines", "BitLocker", "ASR"], "#0f7a4f")
    out["quick-copilot-license-checks"] = og_html("Quick guide · 1 page", "5 things to check before you assign Copilot licenses",
        "Base licenses, mailboxes, update channel, network and oversharing. Free PDF.", ["Checklist", "Microsoft Learn sources"], "#e39a1f")
    out["guides"] = og_html("Guides", "Fact-checked playbooks for Microsoft 365 and Windows admins", "Phased guides with printable checklists.", ["Copilot", "Windows 11", "Quick guides"])
    out["security"] = og_html("Security", "Patch what is exploited. Harden what is exposed.",
        "Vulnerability watch and hardening recipes, checked against vendor advisories and CISA.", ["Exploited CVEs", "Network", "Servers", "VMware"], "#b3261e")
    out["newsletter"] = og_html("Free weekly brief", "What changed in Copilot, Intune, Entra and Purview", "And what admins should do about it. 5 minutes, no fluff.", ["Weekly", "Free", "Sources linked"])
    return out


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)


def generate(force=False):
    ch = chrome()
    h = inputs_hash()
    old = json.loads(MANIFEST.read_text()).get("inputs") if MANIFEST.exists() else None
    if old == h and not force:
        print("Shareables up to date"); return 0
    if not ch:
        print("WARNING: shareables are out of date but no Chrome/Chromium found; using committed files"); return 0
    DL.mkdir(exist_ok=True); OG.mkdir(parents=True, exist_ok=True)
    flags = [ch, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--run-all-compositor-stages-before-draw"]
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        docs = {f"{G1.SLUG}-checklist": checklist_html(G1), f"{G2.SLUG}-checklist": checklist_html(G2), Q.SLUG: quick_html()}
        for name, doc in docs.items():
            src = td / f"{name}.html"; src.write_text(doc)
            run(flags + ["--no-pdf-header-footer", f"--print-to-pdf={DL / (name + '.pdf')}", src.as_uri()])
        for name, doc in og_specs().items():
            src = td / f"og-{name}.html"; src.write_text(doc)
            out = OG / f"{name}.png"
            run(flags + ["--window-size=1200,630", f"--screenshot={out}", src.as_uri()])
            try:  # shrink: flatten to a 256-colour palette (gradients stay smooth enough at 1200x630)
                from PIL import Image
                im = Image.open(out).convert("RGB")
                im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).save(out, optimize=True)
            except Exception:
                pass
    MANIFEST.write_text(json.dumps({"inputs": h, "note": "hash of the inputs of tools/make_shareables.py"}, indent=1) + "\n")
    print(f"Shareables regenerated: {len(docs)} PDFs in downloads/, {len(og_specs())} OG images in assets/og/")
    return 0


if __name__ == "__main__":
    sys.exit(generate("--force" in sys.argv))
