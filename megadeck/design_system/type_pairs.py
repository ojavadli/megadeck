"""Composition-driven typography pairings.

Each composition has a typographic personality. Sans-serif everywhere is
boring. Editorial wants serif headlines. Blueprint wants monospace.
Brutalist wants display weight. This module returns the (display, body)
font pair for a given composition, so templates can pick the right
typography for the slide's visual language.

Resolution order
----------------
1. If the composition has an explicit pairing, use it.
2. Otherwise, fall back to the theme's font_display/font_body.
"""
from __future__ import annotations

from typing import Tuple

from megadeck.design_system.tokens import Theme


# (display_font, body_font) per composition.
# Fonts chosen are widely available; LibreOffice falls back gracefully.
_PAIRINGS = {
    "typographic": (None, None),                     # use theme defaults
    "swiss":       ("Inter", "Inter"),                # geometric sans (Helvetica-ish)
    "editorial":   ("Playfair Display", "Source Serif Pro"),
    "blueprint":   ("IBM Plex Mono", "IBM Plex Sans"),
    "brutalist":   ("Inter Black", "Inter"),         # falls back to Inter Bold
    "grid":        ("Inter Tight", "Inter"),
    "mono-grid":   ("IBM Plex Mono", "IBM Plex Mono"),
    "photographic": ("Playfair Display", "Inter"),    # editorial photo caption
    "bauhaus":     ("Futura", "Futura"),              # iconic Bauhaus typeface
    "risograph":   ("Space Grotesk", "Space Grotesk"),
    "orbs":        (None, None),
}


def fonts_for_composition(composition: str, theme: Theme) -> Tuple[str, str]:
    """Return (display_font, body_font) for a composition. Falls back to
    the theme's defaults when no pairing is registered or the pairing is
    explicitly None."""
    pair = _PAIRINGS.get(composition or "typographic", (None, None))
    display = pair[0] or theme.font_display
    body = pair[1] or theme.font_body
    return display, body


__all__ = ["fonts_for_composition"]
