"""Adapter: Open Color → megadeck themes.

Source data
-----------
Open Color is a small public colour scheme: 13 hues × 10 shades. CC0/MIT-licensed.
https://yeun.github.io/open-color/

13 hues × 4 visual styles = 52 themes.
"""
from __future__ import annotations

from typing import Dict, Iterator, List

from megadeck.design_system.themegen import Palette, VisualStyle, generate_theme


OPEN_COLOR: Dict[str, Dict[int, str]] = {
    "gray":   {0: "#f8f9fa", 2: "#e9ecef", 5: "#adb5bd", 7: "#495057", 9: "#212529"},
    "red":    {0: "#fff5f5", 2: "#ffc9c9", 5: "#ff6b6b", 7: "#f03e3e", 9: "#c92a2a"},
    "pink":   {0: "#fff0f6", 2: "#ffdeeb", 5: "#f06595", 7: "#d6336c", 9: "#a61e4d"},
    "grape":  {0: "#f8f0fc", 2: "#eebefa", 5: "#cc5de8", 7: "#ae3ec9", 9: "#862e9c"},
    "violet": {0: "#f3f0ff", 2: "#d0bfff", 5: "#845ef7", 7: "#6741d9", 9: "#5f3dc4"},
    "indigo": {0: "#edf2ff", 2: "#bac8ff", 5: "#5c7cfa", 7: "#4263eb", 9: "#364fc7"},
    "blue":   {0: "#e7f5ff", 2: "#a5d8ff", 5: "#339af0", 7: "#1c7ed6", 9: "#1864ab"},
    "cyan":   {0: "#e3fafc", 2: "#99e9f2", 5: "#22b8cf", 7: "#1098ad", 9: "#0b7285"},
    "teal":   {0: "#e6fcf5", 2: "#96f2d7", 5: "#20c997", 7: "#0ca678", 9: "#087f5b"},
    "green":  {0: "#ebfbee", 2: "#b2f2bb", 5: "#51cf66", 7: "#37b24d", 9: "#2b8a3e"},
    "lime":   {0: "#f4fce3", 2: "#d8f5a2", 5: "#94d82d", 7: "#74b816", 9: "#5c940d"},
    "yellow": {0: "#fff9db", 2: "#ffec99", 5: "#fcc419", 7: "#f59f00", 9: "#e67700"},
    "orange": {0: "#fff4e6", 2: "#ffd8a8", 5: "#ff922b", 7: "#f76707", 9: "#d9480f"},
}


def palette_from_open_color(name: str) -> Palette:
    if name not in OPEN_COLOR:
        raise ValueError(f"Unknown Open Color hue: {name!r}")
    p = OPEN_COLOR[name]
    return Palette(
        name=f"oc-{name}",
        accent=p[5],
        accent_dk=p[7],
        accent_lt=p[2],
        bg_light=p[0],
        bg_dark=p[9],
    )


def generate_open_color_themes(
    visual_styles: List[VisualStyle] = None,
) -> Iterator[Dict]:
    if visual_styles is None:
        visual_styles = ["flat", "shadow", "glass", "orbs"]
    for hue in OPEN_COLOR:
        palette = palette_from_open_color(hue)
        for style in visual_styles:
            yield generate_theme(
                palette,
                visual_style=style,
                mode="light",
                name=f"oc-{hue}-{style}",
                description=f"Open Color {hue} ({style}).",
            )


__all__ = ["OPEN_COLOR", "palette_from_open_color", "generate_open_color_themes"]
