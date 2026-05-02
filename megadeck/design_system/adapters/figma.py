"""Adapter: Figma published-style-token JSON → megadeck themes.

Figma exposes published styles via the REST API (and via export). The
relevant payload shape — for both file-styles and the variables-API —
is a list of styles each with a `paint` (a fill) and a `name`.

Two flavors supported here:

1. **Figma File Styles** (the older REST shape):
       {
         "styles": [
           {"name": "Brand/Primary", "fills": [{"color":{"r":0.23,"g":0.51,"b":0.96,"a":1}}]},
           ...
         ]
       }

2. **Figma Variables Modes** (newer, supports light/dark):
       {
         "variables": [
           {"name": "color/primary", "valuesByMode": {"<mode>": {"r":..,"g":..,"b":..}}},
           ...
         ]
       }

The adapter walks either shape, normalises the name → category mapping by
looking for keywords (primary / accent / bg / surface / text / muted /
border), and emits a megadeck theme dict.

You don't need a Figma token — pass the JSON you already have on disk or
via a public URL.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from megadeck.design_system.themegen import Palette, generate_theme, is_dark


# ---------------------------------------------------------------------------
# Color extraction
# ---------------------------------------------------------------------------

def _figma_paint_to_hex(rgba: Dict[str, float]) -> Optional[str]:
    """Figma paints store r/g/b in [0, 1]. Convert to '#RRGGBB'."""
    try:
        r = int(round(rgba["r"] * 255))
        g = int(round(rgba["g"] * 255))
        b = int(round(rgba["b"] * 255))
    except Exception:
        return None
    return f"#{r:02X}{g:02X}{b:02X}"


def _name_category(name: str) -> Optional[str]:
    """Map a style name like 'Brand/Primary 500' to a megadeck token."""
    s = name.lower()
    if any(k in s for k in ("primary", "brand", "accent")):
        if "dark" in s or "700" in s or "800" in s or "900" in s:
            return "accent_dk"
        if "light" in s or "200" in s or "100" in s:
            return "accent_lt"
        return "accent"
    if any(k in s for k in ("background", "bg")):
        return "bg"
    if any(k in s for k in ("surface", "card")):
        return "surface"
    if any(k in s for k in ("text", "foreground", "fg", "title")):
        return "title"
    if any(k in s for k in ("muted", "secondary")):
        return "muted"
    if any(k in s for k in ("border", "divider", "outline")):
        return "hairline"
    return None


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------

def figma_styles_to_megadeck(
    spec: Dict[str, Any],
    *,
    name: Optional[str] = None,
    mode: str = "default",
) -> Dict[str, Any]:
    """Walk a Figma styles or variables JSON and emit one megadeck theme dict."""
    tokens: Dict[str, str] = {}

    # 1) File-styles shape
    for style in spec.get("styles") or []:
        cat = _name_category(style.get("name", ""))
        if not cat or cat in tokens:
            continue
        for fill in style.get("fills") or []:
            color = fill.get("color")
            if color:
                hex_v = _figma_paint_to_hex(color)
                if hex_v:
                    tokens[cat] = hex_v
                    break

    # 2) Variables-API shape
    for var in spec.get("variables") or []:
        cat = _name_category(var.get("name", ""))
        if not cat or cat in tokens:
            continue
        values = var.get("valuesByMode") or {}
        if not values:
            continue
        # If a specific mode was requested, look it up; else take first.
        v = values.get(mode) or next(iter(values.values()))
        if isinstance(v, dict) and "r" in v:
            hex_v = _figma_paint_to_hex(v)
            if hex_v:
                tokens[cat] = hex_v

    accent = tokens.get("accent") or "#3B82F6"
    bg = tokens.get("bg") or "#FFFFFF"
    palette = Palette(
        name=name or "figma-import",
        accent=accent,
        accent_dk=tokens.get("accent_dk"),
        accent_lt=tokens.get("accent_lt"),
        bg_light=bg if not is_dark(bg) else None,
        bg_dark=bg if is_dark(bg) else None,
    )
    out = generate_theme(
        palette,
        visual_style="shadow",
        mode="dark" if is_dark(bg) else "light",
        name=_normalise_name(name or "figma-import"),
        description=f"Imported from Figma styles ({mode} mode).",
    )
    # Apply explicit overrides.
    for cat in ("bg", "surface", "title", "muted", "accent",
                "accent_dk", "accent_lt", "hairline"):
        if cat in tokens:
            out[cat] = tokens[cat]
    return out


def import_figma_json(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    return figma_styles_to_megadeck(json.loads(p.read_text(encoding="utf-8")))


def _normalise_name(name: str) -> str:
    safe = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return f"figma-{safe}"


__all__ = ["figma_styles_to_megadeck", "import_figma_json"]
