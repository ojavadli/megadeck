"""Tests for the open-source ecosystem adapters."""
from __future__ import annotations

from pathlib import Path

import pytest

from megadeck.design_system.adapters.catppuccin import (
    CATPPUCCIN,
    palette_from_catppuccin,
    generate_catppuccin_themes,
)
from megadeck.design_system.adapters.open_color import (
    OPEN_COLOR,
    palette_from_open_color,
    generate_open_color_themes,
)
from megadeck.design_system.adapters.radix import (
    RADIX_DARK,
    RADIX_LIGHT,
    palette_from_radix,
    generate_radix_themes,
)
from megadeck.design_system.adapters.shadcn import shadcn_to_megadeck
from megadeck.design_system.adapters.tailwind import (
    TAILWIND_PALETTES,
    palette_from_tailwind,
    generate_tailwind_themes,
)
from megadeck.design_system.adapters.vscode import vscode_theme_to_megadeck
from megadeck.design_system.registry import theme_from_dict
from megadeck.design_system.themegen import (
    Palette,
    VISUAL_STYLES,
    darken,
    generate_theme,
    hex_to_rgb,
    is_dark,
    lighten,
    luminance,
    rgb_to_hex,
    shift_hue,
)


# ---------------------------------------------------------------------------
# themegen colour helpers
# ---------------------------------------------------------------------------

def test_hex_round_trip() -> None:
    assert rgb_to_hex(*hex_to_rgb("#FF8800")) == "#FF8800"


def test_lighten_increases_luminance() -> None:
    assert luminance(lighten("#3B82F6", 0.20)) > luminance("#3B82F6")


def test_darken_decreases_luminance() -> None:
    assert luminance(darken("#3B82F6", 0.20)) < luminance("#3B82F6")


def test_is_dark_threshold() -> None:
    assert is_dark("#000000")
    assert not is_dark("#FFFFFF")


def test_shift_hue_changes_color() -> None:
    assert shift_hue("#FF0000", 120) != "#FF0000"


def test_visual_styles_complete() -> None:
    expected = {"flat", "shadow", "glass", "mesh", "orbs",
                "corner-glow", "geometric", "scribble", "aurora-band"}
    assert expected.issubset(set(VISUAL_STYLES))


def test_generate_theme_yields_loadable_dict() -> None:
    pal = Palette(name="test", accent="#3B82F6")
    out = generate_theme(pal, visual_style="flat", mode="light")
    # Round-trip through theme_from_dict to confirm the schema validates.
    theme = theme_from_dict(out)
    assert theme.name == "test-flat"


# ---------------------------------------------------------------------------
# Tailwind
# ---------------------------------------------------------------------------

def test_tailwind_has_22_palettes() -> None:
    assert len(TAILWIND_PALETTES) == 22


def test_palette_from_tailwind_blue() -> None:
    p = palette_from_tailwind("blue")
    assert p.accent == "#3b82f6"
    assert p.bg_dark == "#172554"


def test_generate_tailwind_themes_count() -> None:
    """22 palettes × 9 styles = 198 themes."""
    themes = list(generate_tailwind_themes())
    assert len(themes) == 22 * 9


def test_every_tailwind_theme_loadable() -> None:
    for t in generate_tailwind_themes(visual_styles=["flat", "shadow"]):
        theme = theme_from_dict(t)
        assert theme.name.startswith("tw-")


# ---------------------------------------------------------------------------
# Catppuccin
# ---------------------------------------------------------------------------

def test_catppuccin_4_flavors() -> None:
    assert set(CATPPUCCIN) == {"latte", "frappe", "macchiato", "mocha"}


def test_palette_from_catppuccin_mocha_blue() -> None:
    p = palette_from_catppuccin("mocha", "blue")
    assert p.accent == "#89b4fa"


def test_generate_catppuccin_themes_count() -> None:
    """4 flavors × 14 accents × 4 styles = 224 themes (default styles)."""
    themes = list(generate_catppuccin_themes())
    assert len(themes) == 4 * 14 * 4


def test_every_catppuccin_theme_loadable() -> None:
    for t in generate_catppuccin_themes(visual_styles=["flat"]):
        theme_from_dict(t)


# ---------------------------------------------------------------------------
# Radix
# ---------------------------------------------------------------------------

def test_radix_has_30_light_scales() -> None:
    assert len(RADIX_LIGHT) >= 30


def test_palette_from_radix_violet_dark() -> None:
    p = palette_from_radix("violet", mode="dark")
    assert p.accent == "#6E56CF"


def test_generate_radix_themes_count() -> None:
    """≥(30+24) scales × 4 styles per (light + dark) split."""
    themes = list(generate_radix_themes())
    expected = (len(RADIX_LIGHT) + len(RADIX_DARK)) * 4
    assert len(themes) == expected


def test_every_radix_theme_loadable() -> None:
    for t in generate_radix_themes(visual_styles=["flat"]):
        theme_from_dict(t)


# ---------------------------------------------------------------------------
# Open Color
# ---------------------------------------------------------------------------

def test_open_color_13_hues() -> None:
    assert len(OPEN_COLOR) == 13


def test_palette_from_open_color_grape() -> None:
    p = palette_from_open_color("grape")
    assert p.accent == "#cc5de8"


def test_generate_open_color_themes_count() -> None:
    """13 hues × 4 styles = 52 themes."""
    themes = list(generate_open_color_themes())
    assert len(themes) == 13 * 4


# ---------------------------------------------------------------------------
# VSCode
# ---------------------------------------------------------------------------

def test_vscode_minimal_theme_imports() -> None:
    spec = {
        "name": "Test Dark Theme",
        "colors": {
            "editor.background": "#0F1014",
            "editor.foreground": "#FFFFFF",
            "editorCursor.foreground": "#A855F7",
            "panel.border": "#26282E",
        },
    }
    out = vscode_theme_to_megadeck(spec)
    theme = theme_from_dict(out)
    assert theme.name == "vscode-test-dark-theme"
    assert str(theme.bg) == "0F1014"
    assert str(theme.accent) == "A855F7"


def test_vscode_alpha_hex_normalised() -> None:
    """VSCode often uses 8-char hex (with alpha). We strip the alpha."""
    spec = {
        "name": "Alpha Test",
        "colors": {
            "editor.background": "#0F101480",  # alpha 80
        },
    }
    out = vscode_theme_to_megadeck(spec)
    assert out["bg"] == "#0F1014"  # 6-char


def test_vscode_missing_keys_fall_back() -> None:
    spec = {"name": "Empty", "colors": {}}
    out = vscode_theme_to_megadeck(spec)
    theme = theme_from_dict(out)
    assert theme.name == "vscode-empty"


# ---------------------------------------------------------------------------
# shadcn / 21st.dev
# ---------------------------------------------------------------------------

def test_shadcn_hsl_parsing() -> None:
    spec = {
        "name": "Test Component",
        "cssVars": {
            "light": {
                "background": "0 0% 100%",
                "foreground": "240 10% 3.9%",
                "primary": "240 5.9% 10%",
                "muted": "240 4.8% 95.9%",
                "border": "240 5.9% 90%",
            },
        },
    }
    out = shadcn_to_megadeck(spec, mode="light")
    theme = theme_from_dict(out)
    # white bg
    assert str(theme.bg) == "FFFFFF"
    # primary at HSL(240, 5.9%, 10%) → roughly #181820
    r, g, b = hex_to_rgb(out["accent"])
    assert r < 32 and b > r  # blueish dark


def test_shadcn_dark_mode() -> None:
    spec = {
        "cssVars": {
            "dark": {
                "background": "240 10% 3.9%",
                "foreground": "0 0% 98%",
                "primary": "0 0% 98%",
            },
        },
    }
    out = shadcn_to_megadeck(spec, mode="dark", name="dark-comp")
    theme_from_dict(out)
