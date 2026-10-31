"""Every page needs a unique <title>, a unique meta description (<=160 chars), og/twitter tags and an og:image file that exists."""
import re, sys, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import site_config as C
DIST, SITE = ROOT / "dist", C.SITE_URL.rstrip("/")
titles, descs, errs, warns = {}, {}, [], []
for f in sorted(DIST.rglob("*.html")):
    if f.name == "404.html":
        continue
    h, p = f.read_text(), str(f.relative_to(DIST))
    t = re.search(r"<title>(.*?)</title>", h)
    d = re.search(r'<meta name="description" content="([^"]*)"', h)
    if not t or not d:
        errs.append(f"{p}: missing title or description"); continue
    titles.setdefault(t.group(1), []).append(p)
    dd = html.unescape(d.group(1))
    descs.setdefault(dd, []).append(p)
    if not 50 <= len(dd) <= 160:
        errs.append(f"{p}: description length {len(dd)} (want 50-160)")
    for tag in ('property="og:title"', 'property="og:description"', 'property="og:image"', 'name="twitter:card"', 'property="og:url"'):
        if tag not in h:
            errs.append(f"{p}: missing {tag}")
    can = re.search(r'rel="canonical" href="([^"]+)"', h)
    if SITE and (not can or not can.group(1).startswith(SITE) or can.group(1).endswith("index.html")):
        errs.append(f"{p}: canonical missing, not absolute on SITE_URL, or ends in index.html")
    rob = re.search(r'<meta name="robots" content="([^"]*)">', h)
    if rob and "noindex" in rob.group(1) and p not in ("search.html", "changelog.html", "404.html"):
        errs.append(f"{p}: unexpected noindex")
    if not rob or "noai" not in rob.group(1) or "noimageai" not in rob.group(1):
        errs.append(f"{p}: robots meta missing noai/noimageai")
    img = re.search(r'property="og:image" content="([^"]+)"', h)
    if img and SITE and img.group(1).startswith(SITE) and not (DIST / img.group(1)[len(SITE) + 1:]).exists():
        errs.append(f"{p}: og:image not found: {img.group(1)}")
    # every content page should have its own OG image (DESIGN.md); generic images only mean a card was not rendered yet
    if img and p not in ("index.html", "search.html", "changelog.html") and re.search(r"/assets/(og-image\.png|og/(cat-[a-z-]+|security|guides)\.png)$", img.group(1)):
        warns.append(f"{p}: generic og:image (run python3 build.py on a machine with Chrome + Pillow and commit assets/og/p/)")
errs += [f"duplicate title on {v}" for k, v in titles.items() if len(v) > 1]
errs += [f"duplicate description on {v}" for k, v in descs.items() if len(v) > 1]
print(f"Checked meta on {sum(len(v) for v in titles.values())} pages: {len(errs)} problems")
for e in errs:
    print("  META", e)
if warns:
    print(f"WARNING: {len(warns)} pages use a generic OG image")
    for w in warns:
        print("  OG", w)
sys.exit(1 if errs else 0)
