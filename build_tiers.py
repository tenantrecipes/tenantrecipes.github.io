"""Content tiers (2026-10-31): every piece of content is exactly one of three levels.
  pillar    – Pillar guide: an end-to-end programme across a whole area (phases, many steps, checklist PDF).
  technical – Technical guide: a deep dive into one specific task or component (fewer phases, exact commands).
  recipe    – Recipe: one short, concrete fix for one real problem (data/recipes/*.json).
Guides declare TIER = "pillar" | "technical" in data/guides/<module>.py; recipes declare "tier": "recipe".
The build fails when a guide or recipe has no valid tier (see GUIDES.md and RECIPES.md)."""
import sys

TIERS = {
    "pillar": ("Pillar guide", "Pillar guides", "End-to-end programmes for a whole area: phased, with a printable checklist."),
    "technical": ("Technical guide", "Technical guides", "Deep dives into one specific task or component, with exact commands."),
    "recipe": ("Recipe", "Recipes", "Short, concrete fixes for one real problem: steps, pitfalls, sources."),
}
GUIDE_TIERS = ("pillar", "technical")


def guide_tier(g):
    t = getattr(g, "TIER", None)
    if t not in GUIDE_TIERS:
        sys.exit(f"Guide {getattr(g, 'SLUG', g.__name__)}: TIER must be one of {GUIDE_TIERS} (got {t!r}). See GUIDES.md.")
    return t


def validate_guides(guides):
    for g in guides:
        guide_tier(g)
        p = getattr(g, "PUBLISHED", None)
        if not (isinstance(p, str) and len(p) == 10):
            sys.exit(f"Guide {g.SLUG}: PUBLISHED = 'YYYY-MM-DD' is required. See GUIDES.md.")


def label(t):
    return TIERS[t][0]


def badge(rel, t, extra=""):
    """Small tier pill linking to the tier legend on the guides index."""
    return (f'<a class="tier tier-{t}" href="{rel}guides/index.html#tier-{t}" title="{TIERS[t][2]}">{TIERS[t][0]}</a>'
            + (f'<span class="tier-x">{extra}</span>' if extra else ""))


def by_tier(guides):
    out = {t: [] for t in GUIDE_TIERS}
    for g in guides:
        out[guide_tier(g)].append(g)
    return out
