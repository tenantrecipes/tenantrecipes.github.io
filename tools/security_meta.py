"""Post-build hardening for dist/*.html (GitHub Pages cannot set custom HTTP headers).

Injects into every page, right after <meta charset>:
  - a per-page Content-Security-Policy <meta> with sha256 hashes for each inline <script>/<style>
    (no 'unsafe-inline', no 'unsafe-eval'); GoatCounter hosts are only allowed when GOATCOUNTER_CODE is set,
  - <meta name="referrer" content="strict-origin-when-cross-origin">,
  - <meta name="robots" content="noai, noimageai"> (merged into an existing robots meta such as noindex).
Not possible via <meta> (browsers ignore it there): HSTS, X-Frame-Options, frame-ancestors, X-Content-Type-Options,
Permissions-Policy. See DEPLOY.md "Security checklist". Fails the build if a page has inline event handlers or
style="" attributes, since the policy would silently break them.
"""
import base64, hashlib, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import site_config as C

DIST = pathlib.Path(__file__).resolve().parent.parent / "dist"
GC = (getattr(C, "GOATCOUNTER_CODE", "") or "").strip().lower()
NONEXEC = re.compile(r'type\s*=\s*"(application/ld\+json|application/json|text/plain)"', re.I)
SCRIPT = re.compile(r"<script(\s[^>]*)?>(.*?)</script>", re.S | re.I)
STYLE = re.compile(r"<style(\s[^>]*)?>(.*?)</style>", re.S | re.I)
MARK = 'http-equiv="Content-Security-Policy"'


def h(s):
    return "'sha256-" + base64.b64encode(hashlib.sha256(s.encode("utf-8")).digest()).decode() + "'"


def policy(scripts, styles):
    gc_script = " https://gc.zgo.at" if GC else ""
    gc_conn = f" https://{GC}.goatcounter.com" if GC else ""
    return "; ".join([
        "default-src 'self'",
        "script-src 'self'" + "".join(" " + x for x in scripts) + gc_script,
        "style-src 'self'" + "".join(" " + x for x in styles),
        "img-src 'self' data:" + gc_conn,
        "connect-src 'self'" + gc_conn,
        "font-src 'self'",
        "manifest-src 'self'",
        "object-src 'none'",
        "frame-src 'none'",
        "worker-src 'none'",
        "base-uri 'self'",
        "form-action 'self' https://buttondown.com",
        "upgrade-insecure-requests",
    ])


ROBOTS = re.compile(r'<meta name="robots" content="([^"]*)">', re.I)
NOAI = ["noai", "noimageai"]


def add_noai(t):
    """Signal 'no AI training' on every page; merges into an existing robots meta (keeps noindex etc.)."""
    m = ROBOTS.search(t)
    if m:
        vals = [v.strip() for v in m.group(1).split(",") if v.strip()]
        vals += [v for v in NOAI if v not in [x.lower() for x in vals]]
        return t[:m.start()] + f'<meta name="robots" content="{", ".join(vals)}">' + t[m.end():]
    tag = '<meta name="robots" content="noai, noimageai">'
    new, k = re.subn(r'(<meta charset="utf-8">)', lambda mm: mm.group(1) + tag, t, count=1, flags=re.I)
    if not k:
        new, k = re.subn(r"(<head[^>]*>)", lambda mm: mm.group(1) + tag, t, count=1, flags=re.I)
    return new


def main():
    bad, n = [], 0
    for p in sorted(DIST.rglob("*.html")):
        t = p.read_text(encoding="utf-8")
        t2 = add_noai(t)
        if t2 != t:
            p.write_text(t2, encoding="utf-8")
            t = t2
        if MARK in t:
            continue
        if re.search(r"<[a-z][^>]*\son[a-z]+\s*=", t, re.I) or re.search(r"<[a-z][^>]*\sstyle\s*=", t, re.I):
            bad.append(str(p.relative_to(DIST)))
            continue
        sc = sorted({h(m.group(2)) for m in SCRIPT.finditer(t)
                     if not re.search(r"\ssrc\s*=", m.group(1) or "") and not NONEXEC.search(m.group(1) or "")})
        st = sorted({h(m.group(2)) for m in STYLE.finditer(t)})
        meta = (f'<meta {MARK} content="{policy(sc, st)}">'
                '<meta name="referrer" content="strict-origin-when-cross-origin">')
        new, k = re.subn(r'(<meta charset="utf-8">)', r"\1" + meta.replace("\\", "\\\\"), t, count=1, flags=re.I)
        if not k:
            new, k = re.subn(r"(<head[^>]*>)", r"\1" + meta.replace("\\", "\\\\"), t, count=1, flags=re.I)
        if not k:
            bad.append(str(p.relative_to(DIST)) + " (no <head>)")
            continue
        p.write_text(new, encoding="utf-8")
        n += 1
    if bad:
        sys.exit("security_meta: inline handlers/style attributes or missing <head> in: " + ", ".join(bad[:20]))
    print(f"security_meta: CSP + referrer meta added to {n} pages")


if __name__ == "__main__":
    main()
