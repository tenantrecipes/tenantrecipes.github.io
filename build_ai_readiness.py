"""Interactive Enterprise AI readiness check (/ai/readiness-check/).

Runs entirely in the visitor's browser (assets/ai-readiness.js). Answers are never sent
to Tenant Recipes; localStorage is used only if the visitor opts in. Preview builds can
point DIST at another directory via TR_DIST and set TR_PREVIEW=1 (noindex, no GoatCounter).
"""
from html import escape as E
import build_trust as T

PATH = "ai/readiness-check/index.html"
PUBLISHED = "2026-11-14"
VERIFIED = "2026-11-14"
TITLE = "Enterprise AI readiness check"
LEAD = ("Answer a few questions about the AI tools in use, the data they can see, and the "
        "controls around them. You get a checklist tailored to your answers. Everything runs "
        "in your browser: nothing you type is sent to us.")
DESC = ("A vendor-neutral, in-browser checklist for enterprise AI: tools in use, data "
        "classification, oversharing, identity, DLP, audit, training and approval. "
        "Optional local save, export as Markdown. Nothing is sent to Tenant Recipes.")

WHY = [
    "Start with an inventory and a data boundary before you scale any assistant. The questions follow that order on purpose.",
    "The check is vendor-neutral: the same control questions apply to Microsoft Copilot, ChatGPT, Claude, Grok, Gemini or a self-hosted model. Vendor features differ by plan and change; confirm them in the current admin documentation and contract.",
    "Fix oversharing and identity first. Adding an assistant on top of open links or personal logins widens a problem you already have.",
]
ALT = [
    "If you only need a pre-flight list before assigning Microsoft Copilot licences, use the Copilot readiness checklist instead — it is shorter and Microsoft-specific.",
    "If a team has asked for one named service, run the approval and deployment runbook. This check is a programme-level gap analysis, not a substitute for a go / no-go record on that service.",
    "If you already have a mature AI governance programme and a complete inventory, you may not need this check. Use it when you want a fresh view of the gaps.",
]
UNVERIFIED = [
    "This is a planning aid produced from your answers. It is not a certification, an audit, or evidence that a service is GDPR- or AI Act-compliant. Legal and regulatory determinations stay with your organisation.",
    "Nothing here was lab-tested or run in a production tenant by Tenant Recipes. Feature availability, retention terms and DLP coverage differ by vendor and by plan, and they change.",
    "Items marked as plan-specific must be confirmed in the vendor's current contract, DPA or admin documentation for the exact SKU you buy.",
]


def _box(title, items, kind):
    cls = "co-warn" if kind == "warn" else "co-info"
    lis = "".join(f"<li>{E(t)}</li>" for t in items)
    return (f'<aside class="co {cls}" role="note"><p class="co-h">{E(title)}</p><ul>{lis}</ul></aside>')


def body(rel, fmt_date, signup, preview=False):
    banner = ""
    if preview:
        banner = ('<aside class="co co-warn air-preview" role="status"><p class="co-h">Preview — not published</p>'
                  "<p>This page is a local preview for review. It is not on the live site and must not be treated as published.</p></aside>")
    privacy = (
        '<aside class="co co-info" id="privacy"><p class="co-h">' + T.icon("shield") + "Private by design</p>"
        "<p>The check is plain JavaScript on this page. Your answers are never sent to Tenant Recipes, stored on our servers, "
        "or put in the page address. There is no account. If you tick “Save answers on this device”, a copy stays in this "
        "browser's local storage until you clear it; that is optional. Printing or downloading happens on your device.</p></aside>"
    )
    dates = (f'<p class="fine air-dates">Drafted {fmt_date(PUBLISHED)}. '
             "A planning aid, not a lab test or a compliance certificate.</p>")
    intro_boxes = (
        '<div class="air-intro">'
        + _box("Why we recommend this", WHY, "info")
        + _box("When to choose something else", ALT, "info")
        + _box("Not verified", UNVERIFIED, "warn")
        + "</div>"
    )
    app = (
        '<div id="air-app" class="air-app">'
        '<div class="air-toolbar">'
        f'<p class="air-stepmeta" id="air-stepmeta">Step 1 of 8</p>'
        '<label class="air-save"><input type="checkbox" id="air-save"> Save answers on this device (never sent to us)</label>'
        '<button type="button" class="btn air-reset" id="air-reset">Start over</button>'
        '</div>'
        '<nav class="air-progress" id="air-progress" aria-label="Check sections"></nav>'
        '<p class="air-err" id="air-err" role="alert" hidden></p>'
        '<div id="air-pane" class="air-pane"></div>'
        '</div>'
    )
    related = (
        f'<p class="air-static-related">Related: <a href="{rel}ai/index.html">Enterprise AI hub</a> · '
        f'<a href="{rel}guides/enterprise-ai-service-approval.html">Approve and deploy an AI service</a> · '
        f'<a href="{rel}guides/enterprise-ai-governance.html">Enterprise AI governance</a> · '
        f'<a href="{rel}tools/enterprise-ai-approved-inventory.html">Approved-tools inventory</a> · '
        f'<a href="{rel}recipes/copilot-readiness-checklist.html">Copilot readiness checklist</a></p>'
    )
    return (
        T.page_hero(rel, T.crumbs_dark(rel, PATH, [
            ("Home", rel + "index.html"),
            ("Enterprise AI", rel + "ai/index.html"),
            ("AI readiness check", None),
        ]),
            f'{T.icon("target")}Interactive tool · Enterprise AI', TITLE, E(LEAD),
            T.chip("layers", "Vendor-neutral") + T.chip("shield", "Runs in your browser") + T.chip("list", "Exportable checklist"),
            kind="page")
        + '<main class="wrap pg"><article class="doc ap air-page">'
        + banner + dates + privacy + intro_boxes + app + related
        + f'<script src="{rel}assets/ai-readiness.js" defer></script>'
        + '</article>'
        + f'<div id="air-subscribe" hidden>{signup(rel, "ai-readiness-check")}</div>'
        + '</main>'
    )


def build(page, fmt_date, signup, SITE_NAME, preview=False):
    pages = [
        page(PATH, f"{TITLE}: a vendor-neutral in-browser checklist | {SITE_NAME}", DESC,
             lambda rel: body(rel, fmt_date, signup, preview=preview)),
    ]
    print(f"AI readiness check: {len(pages)} page")
    return pages


def search_docs():
    return [{
        "t": TITLE,
        "k": "Tool",
        "c": "Enterprise AI",
        "u": PATH,
        "s": DESC,
        "x": ("ai readiness check införandekoll inventory data classification oversharing "
              "conditional access dlp audit training approval copilot chatgpt claude grok gemini checklist"),
    }]
