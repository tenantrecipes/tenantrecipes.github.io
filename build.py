"""One command to build the site: validate recipes -> data files -> shareables (PDF/OG, only if inputs changed) -> dist/ -> per-page OG cards (cached) -> link + meta check.
Usage: python3 build.py   (exit code != 0 means: do not deploy)"""
import subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parent
for step in (["build_data.py"], ["tools/make_shareables.py"], ["build_site.py"], ["tools/make_page_og.py"], ["tools/security_meta.py"], ["tools/check_links.py"], ["tools/check_meta.py"]):
    print(f"== {' '.join(step)}")
    rc = subprocess.call([sys.executable, *step], cwd=root)
    if rc == 3 and step[0] == "tools/make_page_og.py":   # new per-page OG cards: rebuild so og:image points to them
        print("== build_site.py (again, to wire in the new OG cards)")
        rc = subprocess.call([sys.executable, "build_site.py"], cwd=root)
    if rc != 0:
        sys.exit(f"Build stopped at {step[0]}")
print("OK: dist/ is ready to deploy")
