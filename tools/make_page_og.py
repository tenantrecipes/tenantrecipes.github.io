"""Automatic per-page Open Graph cards (1200x630 JPEG) for pages that only have a generic section image.
Input:  .cache/og-pages.json, written by build_site.py (path, title, content-type kicker, accent, hash).
Output: assets/og/p/<slug>.jpg + assets/og/p/manifest.json (slug -> hash). Committed, so CI does not need Chrome.
Cached: a card is only rendered when its hash (title, kicker, accent, template version) changed.
Cards of pages that no longer exist are removed.
Exit code 3 = new cards were made, so build.py runs build_site.py again to wire them in. 0 = nothing to do."""
import sys, json, html, shutil, subprocess, tempfile, pathlib, concurrent.futures as cf
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import site_config as C
LIST, OUT = ROOT / ".cache" / "og-pages.json", ROOT / "assets" / "og" / "p"
MAN = OUT / "manifest.json"
MARK = (ROOT / "assets" / "mark.svg").read_text()
SITE = C.SITE_URL.rstrip("/").replace("https://", "")
E = lambda s: html.escape(str(s), quote=True)


def card(s):
    t = s["title"]
    size = 72 if len(t) < 32 else 64 if len(t) < 52 else 54 if len(t) < 80 else 46
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{font-family:Inter,"Noto Sans",system-ui,sans-serif;color:#fff;background:radial-gradient(circle at 88% 12%,{s["accent"]}cc,transparent 42%),linear-gradient(135deg,#071027,#0f2f6b 55%,#2a1360);
display:flex;flex-direction:column;justify-content:center;padding:0 84px 30px;box-sizing:border-box;position:relative}}
.logo{{position:absolute;top:56px;left:84px;font-size:34px;font-weight:800;display:flex;align-items:center;gap:16px}}.logo svg{{width:58px;height:58px}}.logo span{{color:#9fd0ff}}
.k{{display:inline-block;align-self:flex-start;margin-top:70px;font-size:24px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#fff;
background:{s["accent"]}55;border:2px solid #ffffff66;border-radius:999px;padding:6px 20px}}
h1{{font-size:{size}px;line-height:1.08;margin:22px 0 0;font-weight:800;letter-spacing:-1.2px;max-width:1030px;
display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}}
.bar{{position:absolute;left:84px;right:84px;bottom:40px;display:flex;justify-content:space-between;font-size:22px;color:#c9d4f5}}
</style></head><body><div class="logo">{MARK}<div>Tenant<span>Recipes</span></div></div>
<div class="k">{E(s["kicker"])}</div><h1>{E(t)}</h1>
<div class="bar"><div>Fact-checked · sources linked</div><div>{E(SITE)}</div></div></body></html>"""


def chrome():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        if shutil.which(c):
            return shutil.which(c)


def render(ch, s, td):
    from PIL import Image
    src, png = td / f'{s["slug"]}.html', td / f'{s["slug"]}.png'
    src.write_text(card(s))
    subprocess.run([ch, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--run-all-compositor-stages-before-draw", "--window-size=1200,630",
                    f"--screenshot={png}", src.as_uri()], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    Image.open(png).convert("RGB").save(OUT / f'{s["slug"]}.jpg', "JPEG", quality=84, optimize=True, progressive=True)
    return s


def main():
    if not LIST.exists():
        print("make_page_og: no .cache/og-pages.json (run build_site.py first)"); return 0
    pages = json.loads(LIST.read_text())
    man = json.loads(MAN.read_text()) if MAN.exists() else {}
    want = {s["slug"]: s for s in pages}
    todo = [s for s in pages if man.get(s["slug"]) != s["hash"] or not (OUT / f'{s["slug"]}.jpg').exists()]
    gone = [k for k in man if k not in want]
    ch = chrome()
    try:
        import PIL  # noqa: F401
    except ImportError:
        ch = None
    if todo and not ch:
        print(f"WARNING: {len(todo)} OG cards missing or stale but no Chrome/Pillow; those pages keep the generic image"); todo = []
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    if todo:
        with tempfile.TemporaryDirectory() as td, cf.ThreadPoolExecutor(6) as ex:
            for s in ex.map(lambda s: render(ch, s, pathlib.Path(td)), todo):
                man[s["slug"]] = s["hash"]; made += 1
    for k in gone:
        (OUT / f"{k}.jpg").unlink(missing_ok=True); man.pop(k, None)
    if made or gone:
        MAN.write_text(json.dumps(dict(sorted(man.items())), indent=1) + "\n")
    print(f"OG cards: {len(pages)} pages, {made} rendered, {len(gone)} removed, {len(pages) - made} cached")
    return 3 if made else 0


if __name__ == "__main__":
    sys.exit(main())
