"""Every page needs a unique <title>, a unique meta description (<=160 chars), og/twitter tags and an og:image file that exists."""
import re, sys, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import site_config as C
DIST, SITE = ROOT / "dist", C.SITE_URL.rstrip("/")
titles, descs, errs = {}, {}, []
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
    if 'name="robots" content="noindex"' in h and p not in ("search.html", "changelog.html"):
        errs.append(f"{p}: unexpected noindex")
    img = re.search(r'property="og:image" content="([^"]+)"', h)
    if img and SITE and img.group(1).startswith(SITE) and not (DIST / img.group(1)[len(SITE) + 1:]).exists():
        errs.append(f"{p}: og:image not found: {img.group(1)}")
errs += [f"duplicate title on {v}" for k, v in titles.items() if len(v) > 1]
errs += [f"duplicate description on {v}" for k, v in descs.items() if len(v) > 1]
print(f"Checked meta on {sum(len(v) for v in titles.values())} pages: {len(errs)} problems")
for e in errs:
    print("  META", e)
sys.exit(1 if errs else 0)
