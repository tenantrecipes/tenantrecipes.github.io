"""Content markers (Official guidance / Practical insight / Tested configuration), troubleshooting and rollback for recipes.

Schema (all optional, see RECIPES.md):
  "markers":  {"steps": "official", "pitfalls": "practical", ...}   section -> marker
  "notes":    [{"marker": "practical", "text": "..."}]              marker callouts, shown after the steps
  "tested":   {"environment": "...", "date": "YYYY-MM-DD", "result": "..."}   REQUIRED when any marker is "tested"
  "troubleshooting": ["...", {"symptom": "...", "cause": "...", "fix": "..."}]
  "rollback": ["step", ...]
Nothing renders when a field is missing or empty.
"""
import datetime, re
from html import escape as E

MARKERS = {
    "official": ("Official guidance", "Follows Microsoft's (or the primary vendor's) own documentation, linked under Sources."),
    "practical": ("Practical insight", "Editor experience and observations. Not lab-tested; confirm in your own pilot."),
    "tested": ("Tested configuration", "Configured and tested by the editor in a real test environment on the date shown."),
}
SECTIONS = ("steps", "done_when", "pitfalls", "troubleshooting", "rollback")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _today():
    return datetime.date.today().isoformat()


def validate_tested(t, where):
    errs = []
    if not isinstance(t, dict) or not str(t.get("environment", "")).strip() or not DATE.match(str(t.get("date", ""))):
        errs.append(f"{where}: marker 'tested' requires \"tested\": {{\"environment\": \"...\", \"date\": \"YYYY-MM-DD\"}} (never mark doc-only checks as tested)")
    elif t["date"] > _today():
        errs.append(f"{where}: tested date {t['date']} is in the future")
    return errs


def validate(r):
    errs, used = [], []
    m = r.get("markers")
    if m is not None:
        if not isinstance(m, dict):
            errs.append("'markers' must be an object {section: marker}")
        else:
            for k, v in m.items():
                if k not in SECTIONS:
                    errs.append(f"markers: unknown section '{k}' (allowed: {', '.join(SECTIONS)})")
                elif v not in MARKERS:
                    errs.append(f"markers.{k}: '{v}' must be one of {sorted(MARKERS)}")
                elif k != "steps" and not r.get(k):
                    errs.append(f"markers.{k}: section is empty")
                used.append(v)
    for n in r.get("notes") or []:
        if not isinstance(n, dict) or n.get("marker") not in MARKERS or not str(n.get("text", "")).strip():
            errs.append(f"note needs marker ({'/'.join(MARKERS)}) and text: {n}")
        else:
            used.append(n["marker"])
    if "official" in used and not r.get("last_verified"):
        errs.append("marker 'official' needs last_verified (the steps must have been checked against the sources)")
    if "tested" in used or "tested" in r:
        errs += validate_tested(r.get("tested"), "tested")
    for t in r.get("troubleshooting") or []:
        ok = (isinstance(t, str) and t.strip()) or (isinstance(t, dict) and str(t.get("symptom", "")).strip() and str(t.get("fix", "")).strip())
        if not ok:
            errs.append(f"troubleshooting item must be a string or {{symptom, fix, cause?}}: {t}")
    rb = r.get("rollback")
    if rb is not None and (not isinstance(rb, list) or not all(isinstance(x, str) and x.strip() for x in rb)):
        errs.append("'rollback' must be a list of non-empty strings")
    return errs


def badge(rel, key, tested=None, fmt=None):
    if not key:
        return ""
    label, tip = MARKERS[key]
    extra = ""
    if key == "tested" and tested:
        d = fmt(tested["date"]) if fmt else tested["date"]
        extra = f'<span class="mk-x"> · {E(tested["environment"])}, {E(d)}</span>'
        tip = f'{tip} Environment: {tested["environment"]}. Date: {tested["date"]}.'
    return f'<a class="mk mk-{key}" href="{rel}methodology.html#markers" title="{E(tip, quote=True)}"><i aria-hidden="true"></i>{label}{extra}</a>'


def section_badge(rel, r, section, fmt=None):
    return badge(rel, (r.get("markers") or {}).get(section), r.get("tested"), fmt)


def notes_html(rel, r, step_html, fmt=None):
    out = ""
    for n in r.get("notes") or []:
        out += (f'<aside class="co mk-note mk-n-{n["marker"]}" role="note"><p class="co-h">{badge(rel, n["marker"], r.get("tested"), fmt)}</p>'
                f'<p>{step_html(n["text"])}</p></aside>')
    return out


def ts_item(t, step_html):
    if isinstance(t, str):
        return f'<li>{step_html(t)}</li>'
    return (f'<li><p class="ts-s"><strong>Symptom:</strong> {step_html(t["symptom"])}</p>'
            + (f'<p class="ts-c"><strong>Likely cause:</strong> {step_html(t["cause"])}</p>' if t.get("cause") else "")
            + f'<p class="ts-f"><strong>Fix:</strong> {step_html(t["fix"])}</p></li>')


def troubleshooting_html(rel, r, step_html, icon, fmt=None):
    ts = r.get("troubleshooting") or []
    if not ts:
        return ""
    return (f'<section id="troubleshooting" class="co co-ts"><p class="co-h">{icon("alert")}Troubleshooting &amp; common mistakes {section_badge(rel, r, "troubleshooting", fmt)}</p>'
            f'<ul class="ts-l">' + "".join(ts_item(t, step_html) for t in ts) + '</ul></section>')


def rollback_html(rel, r, step_html, icon, fmt=None):
    rb = r.get("rollback") or []
    if not rb:
        return ""
    return (f'<section id="rollback" class="co co-rb"><p class="co-h">{icon("clock")}Rollback {section_badge(rel, r, "rollback", fmt)}</p>'
            '<ol>' + "".join(f'<li>{step_html(x)}</li>' for x in rb) + '</ol>'
            '<p class="fine">How to undo this change safely if it causes problems. Test the rollback in your pilot too.</p></section>')


def ts_text(t, plain=lambda s: s.replace("`", "")):
    if isinstance(t, str):
        return plain(t)
    return f'{plain(t["symptom"])} Cause: {plain(t["cause"])} Fix: {plain(t["fix"])}' if t.get("cause") else f'{plain(t["symptom"])} Fix: {plain(t["fix"])}'


def legend_html(rel):
    rows = "".join(f'<li>{badge(rel, k)}<span>{E(MARKERS[k][1])}</span></li>' for k in MARKERS)
    return (f'<h2 id="markers">Content markers</h2><p>Sections and callouts on recipes and guides can carry one of three markers, so you can see where a statement comes from:</p>'
            f'<ul class="mk-leg">{rows}</ul>'
            '<p>We only use <em>Tested configuration</em> when the configuration was actually run in a test environment, and the marker always shows that '
            'environment and the test date. Checking a step against documentation is verification, not testing, and is never labelled as tested. '
            'The build refuses a "tested" marker without an environment and date. Unmarked sections follow the normal verification process described above.</p>')
