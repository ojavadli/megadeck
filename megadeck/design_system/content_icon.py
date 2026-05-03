"""Content-aware Lucide icon selector.

Given a slide's text content (title / eyebrow / body), pick the most
relevant icon from `LUCIDE_INLINE` based on keyword matching.

The matcher is deliberately simple — a regex-based keyword → icon map.
For richer mappings, swap in an embedding-based picker; the API stays
the same.

Usage
-----
    from megadeck.design_system.content_icon import icon_for_slide
    icon_name = icon_for_slide(slide_data)
"""
from __future__ import annotations

import re
from typing import Any, List, Tuple

from megadeck.design_system.icons import LUCIDE_INLINE


# Keyword → icon. First matching wins. Order matters (most specific first).
_RULES: List[Tuple[str, str]] = [
    # Money / business
    (r"\b(money|fund|raise|invest|valuation|seed|venture|vc|capital|cash|revenue|mrr|profit|charge|price|pricing|monetiz)\w*", "trending-up"),
    (r"\b(growth|scale|scaling|expand|adoption)\w*", "trending-up"),
    (r"\b(decline|loss|fail|risk|drop)\w*", "trending-down"),
    # Customer / user
    (r"\b(customer|user|audience|persona|consumer|client|founder|team|cofounder|partner)\w*", "users"),
    # Idea / insight
    (r"\b(idea|insight|inspiration|imagine|innovate|innovation|invent)\w*", "lightbulb"),
    (r"\b(launch|ship|release|deploy|go.?live|rocket)\w*", "rocket"),
    (r"\b(speed|fast|quick|rapid|instant|momentum|accelerate)\w*", "zap"),
    # Risk / safety
    (r"\b(risk|danger|warn|caution|threat|attack)\w*", "alert-triangle"),
    (r"\b(secur|safe|protect|defend|shield|guard|trust)\w*", "shield"),
    # Goals
    (r"\b(target|goal|objective|aim|focus|priorit|kpi)\w*", "target"),
    # Code / tech
    (r"\b(code|engineer|develop|tech|stack|framework|api|library|build|software|prompt|llm|model|agent)\w*", "code"),
    (r"\b(layer|stack|architect|infrastructure|platform)\w*", "layers"),
    # Search / explore
    (r"\b(search|find|explore|discover|research|investigat)\w*", "search"),
    # Settings / process
    (r"\b(setting|config|optimi[sz]e|tune|adjust|control|process|loop|workflow|pipeline|cycle)\w*", "settings"),
    # Data / charts
    (r"\b(data|metric|measure|report|chart|graph|number|stat|baseline|track|monitor|observ|telemetry)\w*", "chart-bar"),
    (r"\b(trend|over time|timeline|history|evolution)\w*", "chart-line"),
    (r"\b(distribution|share|portion|percentage|breakdown|fraction)\w*", "chart-pie"),
    # Time / book
    (r"\b(read|book|chapter|article|lesson|study|course|teach|learn)\w*", "book"),
    # Stars
    (r"\b(quality|best|top|excellence|premium|outstanding|star)\w*", "star"),
    # Heart
    (r"\b(love|passion|care|empathy|delight)\w*", "heart"),
    # Network / globe
    (r"\b(global|world|geograph|international|country|valley|silicon)\w*", "globe"),
    # Briefcase / work
    (r"\b(work|business|enterprise|company|corporate|hire|job|career)\w*", "briefcase"),
    # Action / play
    (r"\b(start|begin|action|do|execute|run|trigger|play|step)\w*", "play"),
    # Confirmation
    (r"\b(yes|true|correct|approved|right|positive|win|success)\w*", "check"),
    (r"\b(no|wrong|incorrect|reject|denied|fail|miss)\w*", "x"),
    # Forward arrow
    (r"\b(next|forward|advance|onward|then|future|tomorrow|later)\w*", "arrow-right"),
    (r"\b(level.?up|breakthrough|leap)\w*", "arrow-up-right"),
    # Square / circle / triangle (geometric fallbacks)
    (r"\b(category|type|class|kind|group)\w*", "square"),
    # Info / help
    (r"\b(why|what|how|note|info|help|fyi|caveat|terminology|definition)\w*", "info"),
]


def icon_for_text(text: str, *, default: str = "circle") -> str:
    """Return the best-matching Lucide icon name for `text`.

    Falls back to `default` ('circle') if nothing matches. The default
    icon is intentionally subtle so unrecognised content gets a neutral
    geometric mark rather than something semantically wrong.
    """
    if not text:
        return default
    s = text.lower()
    for pattern, icon in _RULES:
        if re.search(pattern, s):
            if icon in LUCIDE_INLINE:
                return icon
    return default


def icon_for_slide(slide: Any, *, default: str = "circle") -> str:
    """Return an icon name for a slide based on its title + eyebrow + body."""
    parts: List[str] = []
    for attr in ("title", "head", "statement", "eyebrow", "subtitle", "body"):
        v = getattr(slide, attr, None)
        if isinstance(v, str):
            parts.append(v)
    items = getattr(slide, "items", None)
    if items:
        for it in items[:3]:
            for sub in ("head", "title", "label", "tail", "description"):
                v = getattr(it, sub, None)
                if isinstance(v, str):
                    parts.append(v)
    return icon_for_text(" ".join(parts), default=default)


__all__ = ["icon_for_text", "icon_for_slide"]
