"""Design tokens — colors, typography, spacing, motion.

A theme is a self-contained bundle of tokens. Switching the theme on a Deck
re-themes every slide without touching content. Tokens are inspired by the
Tailwind / shadcn / Linear design-system conventions and adapted to fit the
visual capabilities of `python-pptx`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

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

    # Optional polish — opt-in for "megaslick" themes (motion / aurora / vercel)
    bg_style: str = "solid"           # "solid" | "aurora" | "vercel-glow" | "linear-mesh"
    bg_aurora_a: RGBColor | None = None  # top-left stop for aurora bg
    bg_aurora_b: RGBColor | None = None  # mid stop
    bg_aurora_c: RGBColor | None = None  # bottom-right stop
    card_style: str = "flat"          # "flat" | "shadow" | "glass"
    accent_glow: bool = False         # add outer glow to numerals + accents
    accent_glow_radius_pt: float = 22.0
    accent_glow_alpha_pct: int = 60
    # Decorations — list of decoration dicts (parsed lazily via decorations.py).
    # Each entry has a `kind` ("orb"/"mesh"/"corner_glow"/"edge_ribbon"/etc.)
    # and shape-specific fields. Defined as `field(default_factory=list)` to
    # keep the dataclass frozen & hashable.
    decorations: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    # Variant overrides: theme-level default variant per slide kind.
    # e.g. `{"numbered_list": "split", "three_card": "staggered"}`. The
    # renderer applies these when the slide doesn't specify its own variant.
    variant_overrides: Tuple[Tuple[str, str], ...] = field(default_factory=tuple)
    # Default composition for slides on this theme. One of the names registered
    # in `megadeck.design_system.compositions.COMPOSITIONS`. None → 'typographic'
    # (no ambient shapes). Slides can override per-slide via `slide.composition`.
    composition: Optional[str] = None
    # When True, the slide rhythm orchestrator will rotate compositions across
    # the deck so consecutive slides never share visual language. When the
    # theme already specifies a composition, this is the *base* and rotation
    # cycles outwards from it.
    rotate_compositions: bool = True

    @property
    def content_width_in(self) -> float:
        return self.slide_width_in - self.left_margin_in - self.right_margin_in

    @property
    def is_dark(self) -> bool:
        """Quick heuristic — dark themes have low-luminance backgrounds."""
        try:
            r, g, b = (int(str(self.bg)[i:i+2], 16) for i in (0, 2, 4))
            return (0.299 * r + 0.587 * g + 0.114 * b) < 128
        except Exception:
            return False


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


CORPORATE_THEME = Theme(
    name="corporate",
    description="Navy + white. Conservative, board-room friendly.",
    bg=_rgb("FFFFFF"),
    surface=_rgb("F8FAFC"),
    overlay=_rgb("E2E8F0"),
    title=_rgb("0B1D3A"),
    body=_rgb("334155"),
    muted=_rgb("64748B"),
    light=_rgb("CBD5E1"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("1E3A8A"),         # blue-900
    accent_dk=_rgb("172554"),
    accent_lt=_rgb("DBEAFE"),
    accent_bg=_rgb("EFF6FF"),
    success=_rgb("166534"),
    warning=_rgb("9A3412"),
    danger=_rgb("991B1B"),
    hairline=_rgb("E2E8F0"),
)


LINEAR_THEME = Theme(
    name="linear",
    description="Inspired by Linear's product UI. Cool slate + electric purple accent.",
    bg=_rgb("FAFAFA"),
    surface=_rgb("F5F4F8"),
    overlay=_rgb("E4E1EC"),
    title=_rgb("0E0E10"),
    body=_rgb("3A3A40"),
    muted=_rgb("80808B"),
    light=_rgb("BABAC0"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("5E6AD2"),         # Linear-style indigo-violet
    accent_dk=_rgb("3F4ED6"),
    accent_lt=_rgb("DDDFFB"),
    accent_bg=_rgb("EFF0FE"),
    success=_rgb("3CB371"),
    warning=_rgb("E6A23C"),
    danger=_rgb("E55353"),
    hairline=_rgb("E5E5EA"),
)


PASTEL_THEME = Theme(
    name="pastel",
    description="Warm muted pastel — gentle, optimistic, designed for product decks.",
    bg=_rgb("FFFAF3"),             # cream
    surface=_rgb("FFF3E2"),
    overlay=_rgb("F1E2C8"),
    title=_rgb("2D1F12"),
    body=_rgb("5C4733"),
    muted=_rgb("8C7560"),
    light=_rgb("BFAA90"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("DB7B5A"),         # warm clay accent
    accent_dk=_rgb("A85031"),
    accent_lt=_rgb("F8D7C5"),
    accent_bg=_rgb("FCEEDF"),
    success=_rgb("65A876"),
    warning=_rgb("D9A45A"),
    danger=_rgb("BD5E5A"),
    hairline=_rgb("EBDDC8"),
)


NEON_THEME = Theme(
    name="neon",
    description="High-contrast dark + electric green / pink accents. Loud and modern.",
    bg=_rgb("050507"),
    surface=_rgb("0F0F14"),
    overlay=_rgb("191926"),
    title=_rgb("FFFFFF"),
    body=_rgb("CFCFD8"),
    muted=_rgb("8A8A95"),
    light=_rgb("4F4F5A"),
    inverse=_rgb("050507"),
    accent=_rgb("38F8C2"),         # electric mint-green
    accent_dk=_rgb("18BD92"),
    accent_lt=_rgb("4FFEDC"),
    accent_bg=_rgb("0A1F1A"),
    success=_rgb("38F8C2"),
    warning=_rgb("F2D060"),
    danger=_rgb("FF5D8B"),
    hairline=_rgb("23232E"),
)


PRINT_THEME = Theme(
    name="print",
    description="Magazine-print aesthetic. Serif headlines, deep ink, generous margins.",
    bg=_rgb("F8F4EC"),             # warm paper
    surface=_rgb("EFE9DB"),
    overlay=_rgb("DDD3BE"),
    title=_rgb("0E0E0E"),
    body=_rgb("3F3A33"),
    muted=_rgb("76715F"),
    light=_rgb("A89F8A"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("8B0000"),         # ink crimson
    accent_dk=_rgb("4F0000"),
    accent_lt=_rgb("F1C2C2"),
    accent_bg=_rgb("F6E4E4"),
    success=_rgb("3D5C2E"),
    warning=_rgb("8A5A23"),
    danger=_rgb("8B0000"),
    hairline=_rgb("D4CDB8"),
    font_display="New York",
    font_body="Iowan Old Style",
)


VIBRANT_THEME = Theme(
    name="vibrant",
    description="High-energy colour palette — magenta accent on white, designed for product launches.",
    bg=_rgb("FFFFFF"),
    surface=_rgb("FDF4FF"),
    overlay=_rgb("F5D0FE"),
    title=_rgb("0A0A0A"),
    body=_rgb("475569"),
    muted=_rgb("64748B"),
    light=_rgb("CBD5E1"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("D946EF"),         # fuchsia-500
    accent_dk=_rgb("A21CAF"),
    accent_lt=_rgb("F0ABFC"),
    accent_bg=_rgb("FDF4FF"),
    success=_rgb("10B981"),
    warning=_rgb("F59E0B"),
    danger=_rgb("EF4444"),
    hairline=_rgb("E2E8F0"),
)

MONOCHROME_THEME = Theme(
    name="monochrome",
    description="Pure black + white. Zero colour. Brutally minimal.",
    bg=_rgb("FFFFFF"),
    surface=_rgb("F4F4F4"),
    overlay=_rgb("E5E5E5"),
    title=_rgb("000000"),
    body=_rgb("262626"),
    muted=_rgb("737373"),
    light=_rgb("A3A3A3"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("000000"),
    accent_dk=_rgb("000000"),
    accent_lt=_rgb("D4D4D4"),
    accent_bg=_rgb("F4F4F4"),
    success=_rgb("171717"),
    warning=_rgb("404040"),
    danger=_rgb("000000"),
    hairline=_rgb("D4D4D4"),
)

SWISS_THEME = Theme(
    name="swiss",
    description="Swiss design school: strict grid, red accent, Helvetica feel.",
    bg=_rgb("FFFFFF"),
    surface=_rgb("F8F8F8"),
    overlay=_rgb("EDEDED"),
    title=_rgb("000000"),
    body=_rgb("1A1A1A"),
    muted=_rgb("707070"),
    light=_rgb("BABABA"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("E2231A"),         # Swiss-red
    accent_dk=_rgb("9E1814"),
    accent_lt=_rgb("FECACA"),
    accent_bg=_rgb("FEF2F2"),
    success=_rgb("000000"),
    warning=_rgb("E2231A"),
    danger=_rgb("E2231A"),
    hairline=_rgb("E0E0E0"),
    font_display="Helvetica Neue",
    font_body="Helvetica Neue",
)

JAPANDI_THEME = Theme(
    name="japandi",
    description="Japanese-Scandinavian. Soft beige, muted earth tones. Calm and warm.",
    bg=_rgb("F5EFE6"),
    surface=_rgb("EFE7D8"),
    overlay=_rgb("E5DAC4"),
    title=_rgb("2C2419"),
    body=_rgb("4F4434"),
    muted=_rgb("8B7E69"),
    light=_rgb("BAB099"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("8E5A2D"),         # warm tobacco
    accent_dk=_rgb("5C3A1E"),
    accent_lt=_rgb("D4B894"),
    accent_bg=_rgb("EBDFC8"),
    success=_rgb("4A6B3F"),
    warning=_rgb("B8762F"),
    danger=_rgb("8B3A2A"),
    hairline=_rgb("D6CDB8"),
)

GLASS_THEME = Theme(
    name="glass",
    description="Frosted-glass aesthetic — soft tinted backgrounds, gentle blue accent.",
    bg=_rgb("EAF2FB"),
    surface=_rgb("F7FAFD"),
    overlay=_rgb("D8E5F4"),
    title=_rgb("0F1A2C"),
    body=_rgb("394A66"),
    muted=_rgb("6F7E94"),
    light=_rgb("AFB8C8"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("3B82F6"),
    accent_dk=_rgb("1D4ED8"),
    accent_lt=_rgb("BFDBFE"),
    accent_bg=_rgb("DBEAFE"),
    success=_rgb("0EA47A"),
    warning=_rgb("F59E0B"),
    danger=_rgb("E11D48"),
    hairline=_rgb("CBDCEC"),
)


MOTION_THEME = Theme(
    name="motion",
    description="Motion.dev energy — indigo→cobalt→cyan aurora, mint accent, glowing numerals.",
    bg=_rgb("0B0B14"),
    surface=_rgb("13131F"),
    overlay=_rgb("1B1B2A"),
    title=_rgb("FFFFFF"),
    body=_rgb("CBD5E1"),
    muted=_rgb("9CA3B8"),
    light=_rgb("64748B"),
    inverse=_rgb("0B0B14"),
    accent=_rgb("00E5A0"),
    accent_dk=_rgb("00B57F"),
    accent_lt=_rgb("4FFFC9"),
    accent_bg=_rgb("12251F"),
    success=_rgb("22D3EE"),
    warning=_rgb("FBBF24"),
    danger=_rgb("F87171"),
    hairline=_rgb("262638"),
    bg_style="aurora",
    bg_aurora_a=_rgb("0E0E20"),    # very dark indigo (top-left)
    bg_aurora_b=_rgb("1F2D7A"),    # cobalt (mid)
    bg_aurora_c=_rgb("083344"),    # cyan-950 (bottom-right)
    card_style="glass",
    accent_glow=True,
    accent_glow_radius_pt=20.0,
    accent_glow_alpha_pct=60,
)


AURORA_THEME = Theme(
    name="aurora",
    description="Sweeping violet→fuchsia→teal aurora gradient. White type. Cinematic.",
    bg=_rgb("0E1023"),
    surface=_rgb("1B1F3A"),
    overlay=_rgb("2A2F55"),
    title=_rgb("FFFFFF"),
    body=_rgb("E2E8F0"),
    muted=_rgb("CBD5E1"),
    light=_rgb("94A3B8"),
    inverse=_rgb("0E1023"),
    accent=_rgb("F0ABFC"),
    accent_dk=_rgb("D946EF"),
    accent_lt=_rgb("F5D0FE"),
    accent_bg=_rgb("3B0764"),
    success=_rgb("4ADE80"),
    warning=_rgb("FACC15"),
    danger=_rgb("FB7185"),
    hairline=_rgb("3B3F66"),
    bg_style="aurora",
    bg_aurora_a=_rgb("3B0764"),    # violet-950 (deep)
    bg_aurora_b=_rgb("BE185D"),    # pink-700 (lit-up middle)
    bg_aurora_c=_rgb("0E7490"),    # cyan-700 (cool teal)
    card_style="glass",
    accent_glow=True,
    accent_glow_radius_pt=22.0,
    accent_glow_alpha_pct=70,
)


VERCEL_THEME = Theme(
    name="vercel",
    description="Pure black, white type, electric blue glow. Vercel/v0 marketing aesthetic.",
    bg=_rgb("000000"),
    surface=_rgb("0A0A0A"),
    overlay=_rgb("171717"),
    title=_rgb("FFFFFF"),
    body=_rgb("A1A1AA"),           # zinc-400
    muted=_rgb("71717A"),           # zinc-500
    light=_rgb("3F3F46"),           # zinc-700
    inverse=_rgb("000000"),
    accent=_rgb("3B82F6"),          # blue-500
    accent_dk=_rgb("2563EB"),
    accent_lt=_rgb("60A5FA"),
    accent_bg=_rgb("0F1729"),
    success=_rgb("22C55E"),
    warning=_rgb("EAB308"),
    danger=_rgb("EF4444"),
    hairline=_rgb("262626"),
    bg_style="vercel-glow",
    bg_aurora_a=_rgb("000000"),
    bg_aurora_b=_rgb("0B1733"),
    bg_aurora_c=_rgb("000000"),
    card_style="shadow",
    accent_glow=True,
    accent_glow_radius_pt=24.0,
    accent_glow_alpha_pct=50,
    font_mono="JetBrains Mono",
)


FRAMER_THEME = Theme(
    name="framer",
    description="Layered glass on warm gradient — Framer landing-page energy.",
    bg=_rgb("F4ECFF"),
    surface=_rgb("FFFFFF"),
    overlay=_rgb("EDE3FF"),
    title=_rgb("0E0B1F"),
    body=_rgb("3F3754"),
    muted=_rgb("706892"),
    light=_rgb("ADA4C9"),
    inverse=_rgb("FFFFFF"),
    accent=_rgb("6E29FF"),
    accent_dk=_rgb("5118D1"),
    accent_lt=_rgb("B795FF"),
    accent_bg=_rgb("EFE3FF"),
    success=_rgb("16A34A"),
    warning=_rgb("F97316"),
    danger=_rgb("E11D48"),
    hairline=_rgb("E0D6F4"),
    bg_style="aurora",
    bg_aurora_a=_rgb("F4ECFF"),
    bg_aurora_b=_rgb("FFE9F4"),
    bg_aurora_c=_rgb("E5F2FF"),
    card_style="glass",
    accent_glow=False,
)


LINEAR_PRO_THEME = Theme(
    name="linear-pro",
    description="Linear app exact: graphite background, lavender accent, exquisite hairlines.",
    bg=_rgb("0F1014"),
    surface=_rgb("1A1B22"),
    overlay=_rgb("23242C"),
    title=_rgb("F4F4F5"),
    body=_rgb("D4D4D8"),
    muted=_rgb("A1A1AA"),
    light=_rgb("52525B"),
    inverse=_rgb("0F1014"),
    accent=_rgb("8B5CF6"),
    accent_dk=_rgb("7C3AED"),
    accent_lt=_rgb("C4B5FD"),
    accent_bg=_rgb("231A45"),
    success=_rgb("4ADE80"),
    warning=_rgb("FBBF24"),
    danger=_rgb("F87171"),
    hairline=_rgb("2B2C36"),
    bg_style="solid",
    card_style="shadow",
    accent_glow=True,
    accent_glow_radius_pt=18.0,
    accent_glow_alpha_pct=45,
)


_THEMES: Dict[str, Theme] = {
    "default": DEFAULT_THEME,
    "dark": DARK_THEME,
    "editorial": EDITORIAL_THEME,
    "corporate": CORPORATE_THEME,
    "linear": LINEAR_THEME,
    "pastel": PASTEL_THEME,
    "neon": NEON_THEME,
    "print": PRINT_THEME,
    "vibrant": VIBRANT_THEME,
    "monochrome": MONOCHROME_THEME,
    "swiss": SWISS_THEME,
    "japandi": JAPANDI_THEME,
    "glass": GLASS_THEME,
    "motion": MOTION_THEME,
    "aurora": AURORA_THEME,
    "vercel": VERCEL_THEME,
    "framer": FRAMER_THEME,
    "linear-pro": LINEAR_PRO_THEME,
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
