"""Algorithmic theme generator — produce a full Theme spec from a seed color
plus a `visual_style` recipe.

Why
---
A "theme" in megadeck is a JSON file with ~25 colour fields plus optional
decorations. Hand-authoring 30 of them is fine; hand-authoring thousands
is not. This module generates *coherent* theme specs from a single accent
colour using HCL colour-space transformations and a small set of design
recipes ("flat", "glass-orbs", "mesh", "geometric", "scribble", "minimal").

The generator targets the ecosystems the user asked us to feed from:
Tailwind, Catppuccin, Radix Colors, Open Color, plus arbitrary VSCode and
shadcn/21st.dev JSON. Each of those ships ≥10 colour scales; multiplying
by visual-style recipes yields thousands of distinct designs.

Outputs are plain dicts ready to feed to `theme_from_dict()`.
"""
from __future__ import annotations

import colorsys
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple


# ---------------------------------------------------------------------------
# Colour-space helpers — operate on hex strings and tuples
# ---------------------------------------------------------------------------

def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    s = h.lstrip("#")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02X}{g:02X}{b:02X}"


def luminance(h: str) -> float:
    r, g, b = hex_to_rgb(h)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0


def is_dark(h: str) -> bool:
    return luminance(h) < 0.5


def lighten(h: str, amount: float) -> str:
    """Move the colour toward white in HLS space by `amount` (0..1)."""
    r, g, b = hex_to_rgb(h)
    hls_h, hls_l, hls_s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hls_l = min(1.0, hls_l + amount)
    rr, gg, bb = colorsys.hls_to_rgb(hls_h, hls_l, hls_s)
    return rgb_to_hex(int(rr * 255), int(gg * 255), int(bb * 255))


def darken(h: str, amount: float) -> str:
    r, g, b = hex_to_rgb(h)
    hls_h, hls_l, hls_s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hls_l = max(0.0, hls_l - amount)
    rr, gg, bb = colorsys.hls_to_rgb(hls_h, hls_l, hls_s)
    return rgb_to_hex(int(rr * 255), int(gg * 255), int(bb * 255))


def saturate(h: str, amount: float) -> str:
    r, g, b = hex_to_rgb(h)
    hls_h, hls_l, hls_s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hls_s = max(0.0, min(1.0, hls_s + amount))
    rr, gg, bb = colorsys.hls_to_rgb(hls_h, hls_l, hls_s)
    return rgb_to_hex(int(rr * 255), int(gg * 255), int(bb * 255))


def with_alpha(h: str, alpha_pct: int) -> str:
    """Used for output only — kept here for symmetry."""
    return h


def shift_hue(h: str, deg: float) -> str:
    """Rotate hue by `deg` degrees (0-360)."""
    r, g, b = hex_to_rgb(h)
    hls_h, hls_l, hls_s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    hls_h = (hls_h + deg / 360.0) % 1.0
    rr, gg, bb = colorsys.hls_to_rgb(hls_h, hls_l, hls_s)
    return rgb_to_hex(int(rr * 255), int(gg * 255), int(bb * 255))


# ---------------------------------------------------------------------------
# Visual style recipes — what makes a "Bauhaus" different from "Aurora-orbs"
#
# Each recipe is a function (palette) -> dict[str, Any] with the megadeck
# theme keys: bg_style, card_style, accent_glow, decorations, etc. Pure
# colour fields are filled in by `generate_theme()` afterwards.
# ---------------------------------------------------------------------------

@dataclass
class Palette:
    """Minimum colour information to drive theme generation."""
    name: str
    accent: str        # primary brand / accent
    accent_dk: Optional[str] = None
    accent_lt: Optional[str] = None
    bg_dark: Optional[str] = None    # for "dark" mode generation
    bg_light: Optional[str] = None   # for "light" mode generation


def _style_flat(p: Palette) -> Dict[str, Any]:
    """Clean, minimal — solid bg, hairline cards, no glow. Default."""
    return {
        "bg_style": "solid",
        "card_style": "flat",
        "accent_glow": False,
    }


def _style_shadow(p: Palette) -> Dict[str, Any]:
    """Apple/Linear feel — solid bg + drop-shadow cards."""
    return {
        "bg_style": "solid",
        "card_style": "shadow",
        "accent_glow": False,
    }


def _style_glass(p: Palette) -> Dict[str, Any]:
    """Frosted glass — translucent cards on aurora gradient bg."""
    return {
        "bg_style": "aurora",
        "bg_aurora_a": darken(p.accent, 0.40) if is_dark(p.bg_dark or "#000000") else lighten(p.accent, 0.40),
        "bg_aurora_b": shift_hue(p.accent, 30),
        "bg_aurora_c": shift_hue(p.accent, -30),
        "card_style": "glass",
        "accent_glow": True,
        "accent_glow_radius_pt": 22,
        "accent_glow_alpha_pct": 60,
    }


def _style_mesh(p: Palette) -> Dict[str, Any]:
    """Stripe-style mesh gradient bg + shadow cards."""
    return {
        "bg_style": "linear-mesh",
        "bg_aurora_a": lighten(p.accent, 0.40),
        "bg_aurora_b": p.accent,
        "bg_aurora_c": shift_hue(p.accent, 60),
        "card_style": "shadow",
        "accent_glow": False,
    }


def _style_orbs(p: Palette) -> Dict[str, Any]:
    """Linear / v0 — solid dark bg with two gradient orbs floating off-canvas.

    The orbs are deliberately positioned past the slide edges so they only
    bloom INWARDS — the content area itself stays uncovered. This is what
    Linear and v0 do for their hero sections: orbs as ambient lighting,
    not as foreground elements.
    """
    return {
        "bg_style": "solid",
        "card_style": "shadow",
        "accent_glow": True,
        "accent_glow_radius_pt": 22,
        "accent_glow_alpha_pct": 65,
        "decorations": [
            # Top-left: bleed off to the upper-left so only ~30% of the orb
            # is on-canvas (a soft purple wash behind the eyebrow).
            {"kind": "orb", "x": -0.05, "y": -0.10, "size_in": 6.0,
             "color": p.accent, "alpha_pct": 35, "soft_edge_pt": 32},
            # Bottom-right: bleed off to the lower-right.
            {"kind": "orb", "x": 1.05, "y": 1.10, "size_in": 5.5,
             "color": shift_hue(p.accent, 60),
             "alpha_pct": 30, "soft_edge_pt": 30},
        ],
    }


def _style_corner_glow(p: Palette) -> Dict[str, Any]:
    """v0 / vercel — subtle radial corner glow."""
    return {
        "bg_style": "solid",
        "card_style": "shadow",
        "accent_glow": True,
        "decorations": [
            {"kind": "corner_glow", "corner": "tr",
             "color": p.accent, "alpha_pct": 35, "radius_frac": 0.65},
        ],
    }


def _style_geometric(p: Palette) -> Dict[str, Any]:
    """Bauhaus — primary geometric blocks at off-corners."""
    return {
        "bg_style": "solid",
        "card_style": "flat",
        "accent_glow": False,
        "decorations": [
            {"kind": "geometric", "shape": "circle", "x": 0.88, "y": 0.18,
             "size_in": 1.2, "color": p.accent, "alpha_pct": 100},
            {"kind": "geometric", "shape": "triangle", "x": 0.06, "y": 0.85,
             "size_in": 1.4, "color": shift_hue(p.accent, 120),
             "alpha_pct": 100},
            {"kind": "geometric", "shape": "square", "x": 0.92, "y": 0.78,
             "size_in": 0.9, "color": shift_hue(p.accent, -120),
             "alpha_pct": 100, "rotation_deg": 12},
        ],
    }


def _style_scribble(p: Palette) -> Dict[str, Any]:
    """Editorial / paper — scribbled dots scatter."""
    return {
        "bg_style": "solid",
        "card_style": "flat",
        "accent_glow": False,
        "decorations": [
            {"kind": "scribble_dots", "color": p.accent, "count": 30,
             "seed": 7, "alpha_pct": 28, "radius_pt": 1.8},
            {"kind": "edge_ribbon", "edge": "left",
             "color": p.accent, "width_in": 0.10, "inset_in": 0.45},
        ],
    }


def _style_aurora_band(p: Palette) -> Dict[str, Any]:
    """Cinematic — diagonal gradient band sweeping across slide."""
    return {
        "bg_style": "solid",
        "card_style": "glass",
        "accent_glow": True,
        "decorations": [
            {"kind": "aurora_band",
             "colors": [p.accent, shift_hue(p.accent, 60), shift_hue(p.accent, -60)],
             "angle_deg": 18, "band_height_in": 4.5, "y_frac": 0.42},
        ],
    }


VISUAL_STYLES = {
    "flat":         _style_flat,
    "shadow":       _style_shadow,
    "glass":        _style_glass,
    "mesh":         _style_mesh,
    "orbs":         _style_orbs,
    "corner-glow":  _style_corner_glow,
    "geometric":    _style_geometric,
    "scribble":     _style_scribble,
    "aurora-band":  _style_aurora_band,
}


VisualStyle = Literal[
    "flat", "shadow", "glass", "mesh", "orbs",
    "corner-glow", "geometric", "scribble", "aurora-band",
]


# ---------------------------------------------------------------------------
# Theme generation — given a palette + style, emit the full theme dict
# ---------------------------------------------------------------------------

def generate_theme(
    palette: Palette,
    *,
    visual_style: VisualStyle = "flat",
    mode: Literal["light", "dark"] = "light",
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Produce a complete megadeck theme dict from a palette + visual style.

    The generated theme has all 25 colour fields filled in via HCL-derived
    relationships (lighten, darken, shift_hue) so the result reads as a
    cohesive palette, not a random colour pile.
    """
    accent = palette.accent
    accent_dk = palette.accent_dk or darken(accent, 0.15)
    accent_lt = palette.accent_lt or lighten(accent, 0.20)

    if mode == "dark":
        bg = palette.bg_dark or "#0F1014"
        surface = lighten(bg, 0.05)
        overlay = lighten(bg, 0.10)
        title = "#FFFFFF"
        body = "#D4D4D8"
        muted = "#9CA3AF"
        light = "#52525B"
        inverse = bg
        accent_bg = darken(accent, 0.35)
        hairline = lighten(bg, 0.08)
    else:
        bg = palette.bg_light or "#FFFFFF"
        surface = darken(bg, 0.02) if not is_dark(bg) else lighten(bg, 0.05)
        overlay = darken(bg, 0.05) if not is_dark(bg) else lighten(bg, 0.10)
        title = "#0A0A0A" if not is_dark(bg) else "#FFFFFF"
        body = "#374151"
        muted = "#6B7280"
        light = "#9CA3AF"
        inverse = "#FFFFFF"
        accent_bg = lighten(accent, 0.35)
        hairline = darken(bg, 0.08) if not is_dark(bg) else lighten(bg, 0.10)

    style_extras = VISUAL_STYLES[visual_style](palette)

    theme: Dict[str, Any] = {
        "name": name or f"{palette.name}-{visual_style}",
        "description": description or (
            f"Generated: {palette.name} palette with {visual_style} composition."
        ),
        "bg": bg,
        "surface": surface,
        "overlay": overlay,
        "title": title,
        "body": body,
        "muted": muted,
        "light": light,
        "inverse": inverse,
        "accent": accent,
        "accent_dk": accent_dk,
        "accent_lt": accent_lt,
        "accent_bg": accent_bg,
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "hairline": hairline,
        "font_display": "Inter",
        "font_body": "Inter",
    }
    theme.update(style_extras)
    return theme


__all__ = [
    "Palette",
    "VISUAL_STYLES",
    "VisualStyle",
    "generate_theme",
    # colour helpers
    "hex_to_rgb", "rgb_to_hex", "luminance", "is_dark",
    "lighten", "darken", "saturate", "shift_hue",
]
