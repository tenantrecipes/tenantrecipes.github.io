"""One command to build the site: validate recipes -> data files -> dist/ -> link check.
Usage: python3 build.py   (exit code != 0 means: do not deploy)"""
import subprocess, sys, pathlib
root = pathlib.Path(__file__).resolve().parent
for step in (["build_data.py"], ["build_site.py"], ["tools/check_links.py"]):
    print(f"== {' '.join(step)}")
    if subprocess.call([sys.executable, *step], cwd=root) != 0:
        sys.exit(f"Build stopped at {step[0]}")
print("OK: dist/ is ready to deploy")
