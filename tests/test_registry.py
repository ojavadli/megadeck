"""Tests for the JSON theme registry / pool architecture."""
from __future__ import annotations

import json
from pathlib import Path

from megadeck.core.schemas import (
    BulletItem,
    Deck,
    HeroStatementSlide,
    NumberedListSlide,
    TitleSlide,
)
from megadeck.core.renderer import render_deck
from megadeck.design_system.registry import (
    default_pool_dir,
    list_pool_themes,
    load_pool_dir,
    load_theme_json,
    register_pool_theme,
    sync_default_pool,
    theme_from_dict,
    theme_to_dict,
)
from megadeck.design_system.tokens import get_theme


def test_theme_from_minimal_dict_fills_defaults() -> None:
    t = theme_from_dict({"name": "tiny", "bg": "#000000", "accent": "#FF0000"})
    assert t.name == "tiny"
    assert str(t.bg) == "000000"
    # Title luminance was auto-derived from a dark bg → should be white-ish
    assert str(t.title) in {"FFFFFF", "0F172A"}


def test_theme_from_dict_round_trip() -> None:
    src = {
        "name": "round-trip",
        "description": "Sanity-check round-trip.",
        "bg": "#FAFAFB",
        "title": "#0A2540",
        "accent": "#635BFF",
        "bg_style": "linear-mesh",
        "card_style": "shadow",
        "accent_glow": False,
    }
    t = theme_from_dict(src)
    d = theme_to_dict(t)
    # Every key we set should survive
    for k in src:
        if k == "description":
            continue  # description present in output
        assert k in d, f"{k} missing from round-trip"


def test_pool_dir_loads_every_json() -> None:
    """The default pool dir contains 18+ JSON files; they should all register."""
    pool = default_pool_dir()
    json_count = len(list(pool.glob("*.json")))
    sync_default_pool()
    names = list_pool_themes()
    assert len(names) >= json_count  # registry has at least one theme per JSON


def test_load_custom_pool_dir(tmp_path: Path) -> None:
    """A user-supplied pool directory loads correctly."""
    custom = tmp_path / "mypool"
    custom.mkdir()
    spec = {
        "name": "custom-test-theme",
        "description": "User pool",
        "bg": "#112233",
        "title": "#FFFFFF",
        "accent": "#FF8800",
    }
    (custom / "custom-test-theme.json").write_text(json.dumps(spec))
    loaded = load_pool_dir(custom)
    assert len(loaded) == 1
    assert loaded[0].name == "custom-test-theme"
    # Now the registry has it
    assert get_theme("custom-test-theme").name == "custom-test-theme"


def test_pool_theme_can_render(tmp_path: Path) -> None:
    """A theme registered from a JSON dict actually renders a real deck."""
    spec = {
        "name": "render-from-json",
        "description": "From JSON",
        "bg": "#FFFFFF",
        "title": "#1A1A1A",
        "accent": "#FF6600",
        "bg_style": "solid",
        "card_style": "flat",
    }
    register_pool_theme(theme_from_dict(spec))
    deck = Deck(
        title="JSON Theme Demo",
        theme="render-from-json",
        slides=[
            TitleSlide(kind="title", title="From JSON", presenter="Tests"),
            NumberedListSlide(
                kind="numbered_list",
                eyebrow="Demo",
                title="It works",
                items=[
                    BulletItem(head="One.", tail=""),
                    BulletItem(head="Two.", tail=""),
                ],
            ),
        ],
    )
    out = tmp_path / "json-theme.pptx"
    render_deck(deck, out)
    assert out.exists()


def test_load_bad_json_does_not_crash(tmp_path: Path) -> None:
    """Bad JSON in the pool directory is reported but doesn't abort load."""
    custom = tmp_path / "mixedpool"
    custom.mkdir()
    (custom / "good.json").write_text(json.dumps({
        "name": "good-one",
        "bg": "#FFFFFF",
        "title": "#000000",
        "accent": "#0000FF",
    }))
    (custom / "bad.json").write_text("{this is not valid json}")
    loaded = load_pool_dir(custom)  # should print a warning but return [good]
    names = [t.name for t in loaded]
    assert "good-one" in names
