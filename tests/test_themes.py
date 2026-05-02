"""Theme-system tests."""
from __future__ import annotations

import pytest

from megadeck.design_system.tokens import (
    DARK_THEME,
    DEFAULT_THEME,
    EDITORIAL_THEME,
    Theme,
    get_theme,
    list_themes,
)


def test_default_theme_lookup() -> None:
    assert get_theme("default").name == "default"
    assert get_theme(None).name == "default"


def test_named_themes() -> None:
    assert get_theme("dark") is DARK_THEME
    assert get_theme("editorial") is EDITORIAL_THEME


def test_unknown_theme_raises() -> None:
    with pytest.raises(ValueError):
        get_theme("does-not-exist")


def test_list_themes_contains_built_ins() -> None:
    names = {n for n, _ in list_themes()}
    assert {"default", "dark", "editorial"} <= names


def test_theme_geometry_invariants() -> None:
    for t in (DEFAULT_THEME, DARK_THEME, EDITORIAL_THEME):
        assert isinstance(t, Theme)
        assert t.slide_width_in == 13.33
        assert t.slide_height_in == 7.50
        assert 0 < t.left_margin_in < t.slide_width_in / 2
