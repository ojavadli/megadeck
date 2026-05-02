"""Design tokens — colors, typography, spacing, motion.

A theme is a self-contained bundle of tokens. Switching the theme on a Deck
re-themes every slide without touching content. Tokens are inspired by the
Tailwind / shadcn / Linear design-system conventions and adapted to fit the
visual capabilities of `python-pptx`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

from pptx.dml.color import RGBColor


# ----- Color helpers -----------------------------------------------------------

def _rgb(hex_str: str) -> RGBColor:
    """Build an RGBColor from a hex string like '#0EA5E9' or 'FAFAFC'."""
    s = hex_str.lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


@dataclass(frozen=True)
class TypeScale:
    """Type scale in points. Mirrors a tailored editorial scale."""
    eyebrow: int = 11        # uppercase small label
    micro: int = 13          # tiny supporting text
    body: int = 18           # default body
    body_large: int = 20
    h4: int = 22
    h3: int = 26
    h2: int = 34
    h1: int = 44
    hero: int = 64           # giant statement
    display_number: int = 56  # giant outlined numbers


@dataclass(frozen=True)
class Spacing:
    """Spacing scale in inches. Maps onto python-pptx Inches()."""
    xs: float = 0.10
    sm: float = 0.20
    md: float = 0.40
    lg: float = 0.70
    xl: float = 1.10
    xxl: float = 1.80


@dataclass(frozen=True)
class Theme:
    """A complete design theme.

    Colors are stored as RGBColor objects so they can be applied directly to
    python-pptx shapes.
    """
    name: str
    description: str
    # Surfaces
    bg: RGBColor
    surface: RGBColor          # cards / panels
    overlay: RGBColor          # raised surfaces (drop shadow)
    # Text
    title: RGBColor            # primary headings
    body: RGBColor             # default body
    muted: RGBColor            # secondary
    light: RGBColor            # hairlines, deemphasised
    inverse: RGBColor          # text on dark
    # Accents
    accent: RGBColor           # primary brand
    accent_dk: RGBColor
    accent_lt: RGBColor        # tinted variant
    accent_bg: RGBColor        # accent surface
    # Semantic
    success: RGBColor
    warning: RGBColor
    danger: RGBColor
    # Lines
    hairline: RGBColor
    # Type
    font_display: str = "SF Pro Display"
    font_body: str = "SF Pro Display"
    font_mono: str = "SF Mono"
    type_scale: TypeScale = field(default_factory=TypeScale)
    spacing: Spacing = field(default_factory=Spacing)
    # Layout
    slide_width_in: float = 13.33
    slide_height_in: float = 7.50
    left_margin_in: float = 1.10
    right_margin_in: float = 1.10
    top_margin_in: float = 0.85
    bottom_margin_in: float = 0.70

    @property
    def content_width_in(self) -> float:
        return self.slide_width_in - self.left_margin_in - self.right_margin_in


# ----- Built-in themes ---------------------------------------------------------

DEFAULT_THEME = Theme(
    name="default",
    description="Sky-blue minimalistic. Whitespace-first. The flagship Megadeck look.",
    bg=_rgb("FFFFFF"),
    surface=_rgb("F0F9FF"),       # sky-50
    overlay=_rgb("E2E8F0"),       # slate-200 soft shadow
    title=_rgb("090B11"),
    body=_rgb("475569"),
    muted=_rgb("64748B"),
    light=_rgb("94A3B8"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("0EA5E9"),        # sky-500
    accent_dk=_rgb("0284C7"),     # sky-700
    accent_lt=_rgb("BAE6FD"),     # sky-200
    accent_bg=_rgb("F0F9FF"),     # sky-50
    success=_rgb("16A34A"),
    warning=_rgb("D97706"),
    danger=_rgb("DC2626"),
    hairline=_rgb("E2E8F0"),
)


DARK_THEME = Theme(
    name="dark",
    description="Slate-900 background, white type, electric accent. For dramatic decks.",
    bg=_rgb("0F172A"),
    surface=_rgb("1E293B"),       # slate-800
    overlay=_rgb("334155"),       # slate-700
    title=_rgb("FFFFFF"),
    body=_rgb("CBD5E1"),          # slate-300
    muted=_rgb("94A3B8"),         # slate-400
    light=_rgb("64748B"),         # slate-500
    inverse=_rgb("0F172A"),
    accent=_rgb("38BDF8"),        # sky-400 (more vivid against dark)
    accent_dk=_rgb("0EA5E9"),
    accent_lt=_rgb("7DD3FC"),     # sky-300
    accent_bg=_rgb("0C4A6E"),     # sky-900
    success=_rgb("4ADE80"),
    warning=_rgb("FBBF24"),
    danger=_rgb("F87171"),
    hairline=_rgb("334155"),
)


EDITORIAL_THEME = Theme(
    name="editorial",
    description="Magazine editorial. Serif headlines, neutral palette, generous whitespace.",
    bg=_rgb("FBFBF8"),            # warm off-white
    surface=_rgb("F4F2EC"),
    overlay=_rgb("E5E1D5"),
    title=_rgb("141414"),
    body=_rgb("3F3F3F"),
    muted=_rgb("707070"),
    light=_rgb("A6A6A6"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("B45309"),        # amber-800 — paper-warm accent
    accent_dk=_rgb("78350F"),
    accent_lt=_rgb("FDE68A"),
    accent_bg=_rgb("FEF3C7"),
    success=_rgb("166534"),
    warning=_rgb("9A3412"),
    danger=_rgb("991B1B"),
    hairline=_rgb("D4D2C9"),
    font_display="New York",       # macOS serif fallback
    font_body="SF Pro Text",
)


_THEMES: Dict[str, Theme] = {
    "default": DEFAULT_THEME,
    "dark": DARK_THEME,
    "editorial": EDITORIAL_THEME,
}


def get_theme(name: str | None = None) -> Theme:
    """Look up a theme by name. Falls back to the default theme."""
    if not name:
        return DEFAULT_THEME
    if name not in _THEMES:
        raise ValueError(
            f"Unknown theme '{name}'. Available: {', '.join(_THEMES)}"
        )
    return _THEMES[name]


def list_themes() -> list[Tuple[str, str]]:
    """Return [(name, description), ...] for every registered theme."""
    return [(t.name, t.description) for t in _THEMES.values()]


def register_theme(theme: Theme) -> None:
    """Register a custom theme at runtime (used by plugins)."""
    _THEMES[theme.name] = theme
