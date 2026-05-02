"""Adapter: Coolors.co palette URLs → megadeck themes.

Coolors palette URLs look like:
  https://coolors.co/palette/264653-2a9d8f-e9c46a-f4a261-e76f51

The path segment after `/palette/` is a hyphen-separated list of 5-6 6-char
hex codes (no leading `#`). We parse those and map them onto the megadeck
theme contract by sorting on luminance:

  darkest  → bg_dark / surface_dark hint
  lightest → bg_light
  most-saturated mid-tone → accent
  rest → fall back to themegen.generate_theme()

The user passes either a URL or a comma/dash-separated hex string.
"""
from __future__ import annotations

import re
from typing import Dict, List

from megadeck.design_system.themegen import (
    Palette,
    VisualStyle,
    generate_theme,
    hex_to_rgb,
    luminance,
)


_COOLORS_URL_RE = re.compile(r"/palette/([0-9a-fA-F-]+)")
_HEX_RE = re.compile(r"[0-9a-fA-F]{6}")


def _saturation(hex_str: str) -> float:
    """Crude saturation proxy: max(R,G,B) − min(R,G,B). Used to pick the
    accent — most colourful mid-tone, not the most luminous."""
    r, g, b = hex_to_rgb(hex_str)
    return (max(r, g, b) - min(r, g, b)) / 255.0


def parse_coolors(source: str) -> List[str]:
    """Parse a coolors URL or any string containing 5-6 hex codes.

    Accepts:
      * https://coolors.co/palette/0a0e27-3b82f6-f97316-...
      * 0a0e27-3b82f6-f97316
      * #0A0E27, #3B82F6, ...
    """
    m = _COOLORS_URL_RE.search(source)
    if m:
        source = m.group(1)
    hexes = [h.lower() for h in _HEX_RE.findall(source)]
    if len(hexes) < 2:
        raise ValueError(f"Couldn't find at least 2 hex codes in {source!r}")
    return [f"#{h}" for h in hexes]


def palette_from_coolors(source: str, name: str = "coolors") -> Palette:
    hexes = parse_coolors(source)
    by_lum = sorted(hexes, key=luminance)
    bg_dark, *mids, bg_light = by_lum
    # Accent = highest-saturation among the mid-tones.
    accent = max(mids, key=_saturation) if mids else hexes[0]
    accent_dk = min((c for c in by_lum if c != bg_light), key=luminance)
    accent_lt = next((c for c in mids if c != accent), accent)
    return Palette(
        name=name,
        accent=accent,
        accent_dk=accent_dk,
        accent_lt=accent_lt,
        bg_dark=bg_dark,
        bg_light=bg_light,
    )


def generate_coolors_themes(
    source: str,
    *,
    base_name: str | None = None,
    visual_styles: List[VisualStyle] | None = None,
) -> List[Dict]:
    if visual_styles is None:
        visual_styles = ["flat", "shadow", "glass", "orbs"]
    palette = palette_from_coolors(source, name=base_name or "coolors")
    out: List[Dict] = []
    for mode in ("light", "dark"):
        for style in visual_styles:
            out.append(generate_theme(
                palette,
                visual_style=style,
                mode=mode,
                name=f"{palette.name}-{style}-{mode}",
                description=f"Coolors palette: {source} ({style}, {mode}).",
            ))
    return out


__all__ = ["parse_coolors", "palette_from_coolors", "generate_coolors_themes"]
