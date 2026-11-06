"""Editorial AI hub (/ai/): reading paths over EXISTING Tenant Recipes AI content. Every card target is validated at build."""
import json, pathlib
from html import escape as E
import build_trust as T
ROOT = pathlib.Path(__file__).resolve().parent
PATH = "ai/index.html"
TITLE = "Enterprise AI: govern, secure and deploy assistants"
LEAD = "Reading paths for IT, security and governance teams adopting enterprise AI — Microsoft Copilot and other enterprise LLMs."
GUARD = ("Before any pilot: only approved tools, only data classes your policy allows, sign-in through your identity provider, "
         "and retention/training terms checked in the contract. A link on this site is not approval to send company data to any AI service.")
# (id, title, intro, [(label, path, kind, why)], honest note or "")
TRACKS = [
 ("start", "1. Start here: inventory, ownership and approval",
  "Know which AI tools are in use, who owns each one, and which are approved, conditional or denied — before you scale anything.",
  [("Enterprise AI governance (pillar)", "guides/enterprise-ai-governance.html", "Guide", "The end-to-end programme: inventory, shadow AI, SSO, retention, DLP and regulation hooks."),
   ("AI approved-tools inventory method", "tools/enterprise-ai-approved-inventory.html", "Method", "Build the Approved / Conditional / Denied register an auditor can check."),
   ("AI and Copilot use policy template", "policies/ai-copilot-use-policy.html", "Policy", "A starting policy covering Copilot and third-party enterprise LLMs."),
   ("Copilot readiness check", "recipes/copilot-readiness-checklist.html", "Recipe", "Pre-flight checks before Microsoft Copilot licences are assigned.")], ""),
 ("governance", "2. Security and governance: data, privacy, permissions, risk",
  "AI assistants surface what users can already reach. Fix oversharing and labelling first, then add AI-specific controls and audit.",
  [("Find oversharing before Copilot does", "recipes/purview-oversharing-assessment.html", "Recipe", "Data security posture for AI in Microsoft Purview."),
   ("Make Copilot respect sensitivity labels", "recipes/purview-sensitivity-labels-copilot.html", "Recipe", "Labels and encryption as the AI data boundary."),
   ("Stop Copilot processing labelled content with DLP", "recipes/purview-dlp-copilot-location.html", "Recipe", "DLP policy location for Copilot."),
   ("Hide sites with Restricted Content Discovery", "recipes/sharepoint-restricted-content-discovery.html", "Recipe", "Exclude specific SharePoint sites from AI grounding."),
   ("Phishing-resistant MFA for Copilot", "recipes/ca-require-mfa-copilot.html", "Recipe", "Conditional Access for AI sign-ins."),
   ("Audit Copilot interactions", "recipes/purview-audit-copilot.html", "Recipe", "Evidence for investigations and compliance.")],
  "Most hands-on recipes here are Microsoft-specific. The governance guide and policy above are written for any enterprise LLM."),
 ("deploy", "3. Practical deployment across vendors",
  "Roll out in rings with a named pilot group, licensing you can track, and the same identity and data rules for every vendor.",
  [("Secure Copilot rollout (pillar)", "guides/secure-copilot-rollout.html", "Guide", "Phased Microsoft Copilot programme from licensing to adoption."),
   ("5 checks before Copilot licences", "guides/copilot-license-checks.html", "Quick guide", "Short pre-flight list."),
   ("Pilot group licensing", "recipes/copilot-pilot-group-licensing.html", "Recipe", "Group-based licensing for a controlled pilot."),
   ("Copilot Chat vs licensed Copilot", "recipes/copilot-chat-pay-as-you-go.html", "Recipe", "Understand what users get before you buy.")],
  "No dedicated deployment guides for ChatGPT Enterprise, Claude or Gemini exist on this site yet. Apply the vendor-neutral governance guide and use the vendor admin docs in the AI link directory."),
 ("ops", "4. Technology and operations: integrations, agents, logging, cost",
  "Agents and connectors widen what AI can touch. Decide who may build them, keep them inside governed environments, and measure use.",
  [("Decide who can create agents", "recipes/agents-restrict-blueprint-creation.html", "Recipe", "Control agent creation in Entra."),
   ("Inventory agents in the admin center", "recipes/agents-inventory-admin-center.html", "Recipe", "See and manage deployed agents."),
   ("Copilot Studio environment strategy", "recipes/copilot-studio-environment-strategy.html", "Recipe", "Separate dev/test/production for agents."),
   ("Govern Copilot Studio connectors with data policies", "recipes/copilot-studio-dlp.html", "Recipe", "Limit which connectors agents may use."),
   ("Retention for Copilot interactions", "recipes/purview-retention-copilot.html", "Recipe", "Logging and retention of prompts and responses."),
   ("Track Copilot usage via Graph", "recipes/copilot-usage-graph.html", "Recipe", "Usage data for cost and adoption decisions.")],
  "Model evaluation, RAG architecture and multi-vendor cost management are not covered by articles here yet; the AI link directory lists vendor-neutral docs and frameworks."),
 ("templates", "5. Templates and tools",
  "Reusable starters. Adapt them to your organisation and have legal and security review them before use.",
  [("AI and Copilot use policy", "policies/ai-copilot-use-policy.html", "Policy", "Editable policy template."),
   ("Prompt: draft an AI acceptable use policy", "recipes/prompt-4.html", "Prompt", "Admin prompt to produce a first draft."),
   ("Prompt: write a rollout announcement", "recipes/prompt-2.html", "Prompt", "Communicate a pilot to users."),
   ("AI link directory", "links/ai/index.html", "Directory", "Vendor docs, open models, RAG, agents, evaluation and AI governance standards.")], ""),
]

def _check():
    miss = [p for t in TRACKS for _, p, _, _ in t[3] if not _src_exists(p)]
    if miss: raise SystemExit("AI hub: missing link targets: " + ", ".join(miss))

def _src_exists(p):
    if p.startswith("recipes/"): return any(r["id"] == p[8:-5] for r in json.loads((ROOT / "data/recipes.json").read_text()))
    if p.startswith("guides/"): return any(f'"{p[7:-5]}"' in f.read_text() for f in (ROOT / "data/guides").glob("*.py"))
    if p.startswith(("policies/", "tools/")): return (ROOT / "data" / p.split("/")[0] / (p.split("/")[1][:-5] + ".json")).exists()
    return p in ("links/ai/index.html",)

def _card(rel, label, path, kind, why):
    return (f'<li><a class="ai-card" href="{rel}{path}"><span class="ai-kind">{E(kind)}</span>'
            f'<strong>{E(label)}</strong><span class="ai-why">{E(why)}</span></a></li>')

def body(rel):
    toc = "".join(f'<li><a href="#{i}">{E(t)}</a></li>' for i, t, *_ in TRACKS)
    tr = "".join(
        f'<section class="ai-track" id="{i}" aria-labelledby="{i}-h"><h2 id="{i}-h">{E(t)}</h2><p>{E(intro)}</p>'
        f'<ul class="ai-cards">{"".join(_card(rel, *c) for c in cards)}</ul>'
        + (f'<p class="fine ai-gap">{E(note)}</p>' if note else "") + '</section>'
        for i, t, intro, cards, note in TRACKS)
    return (T.page_hero(rel, T.crumbs_dark(rel, PATH, [("Home", rel + "index.html"), ("Enterprise AI", None)]),
                        f'{T.icon("target")}Enterprise AI', E(TITLE), E(LEAD),
                        T.chip("layers", "5 reading paths") + T.chip("link", f'{sum(len(t[3]) for t in TRACKS)} existing pages'), kind="page")
            + '<main class="wrap pg"><article class="prose doc ai-hub">'
            f'<aside class="tl-perm pl-notice" role="note">{T.icon("info")}<span><strong>Guardrails</strong>{E(GUARD)}</span></aside>'
            '<p>Every card links to a page already on Tenant Recipes. Where we have no article yet, the path says so instead of linking to an empty placeholder.</p>'
            f'<div class="ai-toc" role="navigation" aria-label="Reading paths"><p class="ps-h">{T.icon("list")}Reading paths</p><ol>{toc}</ol></div>'
            f'{tr}<p><a class="btn" href="{rel}links/ai/index.html">Browse the AI link directory {T.icon("arrow")}</a></p></article></main>')

def home_promo(rel):
    return (f'<section class="ai-promo wrap" aria-labelledby="ai-promo-h"><div class="ai-promo-in">'
            f'<div><p class="sec-k">New hub · Enterprise AI</p><h2 id="ai-promo-h">Govern, secure and deploy enterprise AI</h2>'
            '<p>Five reading paths from inventory and approval to data protection, rollout, agents and templates — for Copilot and other enterprise LLMs.</p></div>'
            f'<div class="ai-promo-a"><a class="btn p" href="{rel}ai/index.html">Open the AI hub {T.icon("arrow")}</a>'
            f'<a class="btn" href="{rel}links/ai/index.html">AI link directory</a></div></div></section>')

def build(page, SITE_NAME):
    _check()
    return [page(PATH, f"{TITLE} | {SITE_NAME}", LEAD + " Five paths over fact-checked guides, recipes, policies and tools.", body)]

def search_docs():
    return [{"t": "Enterprise AI hub", "k": "Page", "c": "Site", "u": PATH, "s": LEAD,
             "x": " ".join(t[1] for t in TRACKS)[:360]}]
