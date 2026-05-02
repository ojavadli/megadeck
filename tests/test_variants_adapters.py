"""Tests for the variant system + new adapters (Material You, Coolors, Figma, rhythm)."""
from __future__ import annotations

from pathlib import Path

import pytest

from megadeck import render_deck
from megadeck.core.rhythm import apply_rhythm
from megadeck.core.schemas import (
    BulletItem,
    Deck,
    NumberedListSlide,
    TitleSlide,
)
from megadeck.design_system.adapters.coolors import (
    generate_coolors_themes,
    palette_from_coolors,
    parse_coolors,
)
from megadeck.design_system.adapters.figma import figma_styles_to_megadeck
from megadeck.design_system.adapters.material_you import (
    _tonal_palette,
    generate_material_themes,
    palette_from_seed,
)
from megadeck.design_system.registry import theme_from_dict
from megadeck.design_system.variants import VARIANTS, get_variant_renderer
from megadeck.design_system.tokens import get_theme


# ---------------------------------------------------------------------------
# Variant registry
# ---------------------------------------------------------------------------

def test_numbered_list_variants_registered() -> None:
    """The 3 alt layouts (split, cards, timeline) must be registered."""
    expected = {
        ("numbered_list", "split"),
        ("numbered_list", "cards"),
        ("numbered_list", "timeline"),
    }
    assert expected.issubset(set(VARIANTS))


def test_get_variant_renderer_explicit_variant() -> None:
    from megadeck.design_system.templates.numbered_list import render_numbered_list
    fn = get_variant_renderer(
        "numbered_list", "cards",
        theme=get_theme("default"),
        default=render_numbered_list,
    )
    assert fn is VARIANTS[("numbered_list", "cards")]
    assert fn is not render_numbered_list


def test_get_variant_renderer_falls_back_to_default() -> None:
    from megadeck.design_system.templates.numbered_list import render_numbered_list
    fn = get_variant_renderer(
        "numbered_list", "no-such-variant",
        theme=get_theme("default"),
        default=render_numbered_list,
    )
    assert fn is render_numbered_list


def test_variant_renders_end_to_end(tmp_path: Path) -> None:
    """Each numbered_list variant renders a real deck without errors."""
    base = NumberedListSlide(
        kind="numbered_list",
        eyebrow="Test",
        title="Variant test",
        items=[
            BulletItem(head=f"Item {i}", tail="A short tail.")
            for i in range(1, 6)
        ],
    )
    for variant in (None, "cards", "timeline", "split"):
        deck = Deck(
            title="Variant test",
            slides=[
                TitleSlide(kind="title", title="Variant cover", presenter=""),
                base.model_copy(update={"variant": variant}),
            ],
        )
        out = tmp_path / f"variant-{variant or 'default'}.pptx"
        render_deck(deck, out)
        assert out.exists()


# ---------------------------------------------------------------------------
# Material You
# ---------------------------------------------------------------------------

def test_tonal_palette_returns_13_tones() -> None:
    pal = _tonal_palette("#3B82F6")
    assert set(pal.keys()) == {0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100}


def test_palette_from_seed() -> None:
    p = palette_from_seed("#3B82F6", name="my-mat")
    assert p.name == "my-mat"
    assert p.accent.startswith("#")


def test_generate_material_themes_count() -> None:
    """5 visual styles × 2 modes = 10 themes per seed."""
    themes = generate_material_themes("#3B82F6")
    assert len(themes) == 10
    for t in themes:
        theme_from_dict(t)


def test_generate_material_themes_unique_names() -> None:
    themes = generate_material_themes("#3B82F6")
    names = [t["name"] for t in themes]
    assert len(set(names)) == len(names)


# ---------------------------------------------------------------------------
# Coolors
# ---------------------------------------------------------------------------

def test_parse_coolors_url() -> None:
    hexes = parse_coolors("https://coolors.co/palette/264653-2a9d8f-e9c46a-f4a261-e76f51")
    assert len(hexes) == 5
    assert hexes[0] == "#264653"


def test_parse_coolors_dash_separated() -> None:
    hexes = parse_coolors("0a0e27-3b82f6-f97316")
    assert hexes == ["#0a0e27", "#3b82f6", "#f97316"]


def test_parse_coolors_too_few_raises() -> None:
    with pytest.raises(ValueError):
        parse_coolors("only-one-3b82f6")  # only 1 hex


def test_palette_from_coolors() -> None:
    p = palette_from_coolors(
        "https://coolors.co/palette/0a0e27-3b82f6-f97316-22d3ee-ffffff"
    )
    assert p.name == "coolors"
    assert p.bg_dark == "#0a0e27"
    assert p.bg_light == "#ffffff"


def test_generate_coolors_themes_count() -> None:
    """4 styles × 2 modes = 8 themes."""
    themes = generate_coolors_themes(
        "https://coolors.co/palette/264653-2a9d8f-e9c46a-f4a261-e76f51"
    )
    assert len(themes) == 8
    for t in themes:
        theme_from_dict(t)


# ---------------------------------------------------------------------------
# Figma
# ---------------------------------------------------------------------------

def test_figma_file_styles_shape() -> None:
    spec = {
        "styles": [
            {"name": "Brand/Primary", "fills": [
                {"color": {"r": 0.231, "g": 0.510, "b": 0.965, "a": 1}}
            ]},
            {"name": "Background/Default", "fills": [
                {"color": {"r": 1, "g": 1, "b": 1, "a": 1}}
            ]},
            {"name": "Text/Title", "fills": [
                {"color": {"r": 0, "g": 0, "b": 0, "a": 1}}
            ]},
        ],
    }
    out = figma_styles_to_megadeck(spec, name="brand")
    theme = theme_from_dict(out)
    assert theme.name == "figma-brand"
    assert str(theme.bg) == "FFFFFF"
    assert str(theme.title) == "000000"


def test_figma_variables_shape() -> None:
    spec = {
        "variables": [
            {"name": "color/primary", "valuesByMode": {
                "light": {"r": 0.4, "g": 0.2, "b": 0.9, "a": 1}
            }},
            {"name": "color/background", "valuesByMode": {
                "light": {"r": 1, "g": 1, "b": 1, "a": 1}
            }},
        ],
    }
    out = figma_styles_to_megadeck(spec, name="vars", mode="light")
    theme = theme_from_dict(out)
    assert theme.name == "figma-vars"
    assert str(theme.bg) == "FFFFFF"


# ---------------------------------------------------------------------------
# Rhythm
# ---------------------------------------------------------------------------

def test_apply_rhythm_assigns_variants() -> None:
    """Consecutive numbered_list slides should each get a different variant."""
    deck = Deck(
        title="Rhythm",
        slides=[
            TitleSlide(kind="title", title="Cover", presenter=""),
            *[
                NumberedListSlide(
                    kind="numbered_list",
                    eyebrow=f"Slide {i}",
                    title=f"List {i}",
                    items=[BulletItem(head="A", tail=""),
                           BulletItem(head="B", tail="")],
                )
                for i in range(1, 6)
            ],
        ],
    )
    out = apply_rhythm(deck)
    nl_slides = [s for s in out.slides if s.kind == "numbered_list"]
    variants = [s.variant for s in nl_slides]
    # First 4 numbered_lists must hit each of the 4 cycle slots
    assert variants[:4] == [None, "cards", "timeline", "split"]
    # 5th wraps back to default
    assert variants[4] == None
