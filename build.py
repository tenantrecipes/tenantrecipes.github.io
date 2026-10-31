"""One command to build the site: validate recipes -> data files -> shareables (PDF/OG, only if inputs changed) -> dist/ -> link + meta check.
Usage: python3 build.py   (exit code != 0 means: do not deploy)"""
import subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parent
for step in (["build_data.py"], ["tools/make_shareables.py"], ["build_site.py"], ["tools/security_meta.py"], ["tools/check_links.py"], ["tools/check_meta.py"]):
    print(f"== {' '.join(step)}")
    if subprocess.call([sys.executable, *step], cwd=root) != 0:
        sys.exit(f"Build stopped at {step[0]}")
print("OK: dist/ is ready to deploy")
