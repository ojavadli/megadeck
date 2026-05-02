"""Slide compositions — *shape language*, not colour palette.

This module is the answer to "every slide looks the same with different
colours". A composition decides *how* a slide is built up visually:

  * `typographic` — pure type, no shapes other than a hairline grid
  * `swiss`       — strict 12-col grid, hairlines, accent block top-left,
                    no decoration. International Typographic Style.
  * `blueprint`   — graph-paper grid, technical hairline, monospaced
                    eyebrow, mark-up overlays.
  * `brutalist`   — heavy black shapes, raw geometry, no shadows, large
                    typographic flexes. Blackletter accents.
  * `editorial`   — magazine-style asymmetric grid with rule lines and
                    drop caps. Generous negative space.
  * `photographic`— dominant photo zone (or photo-placeholder) covering
                    40-60% of the slide.
  * `grid`        — explicit modular grid of cards / cells.
  * `orbs`        — the previous default: glowing orbs in two corners
                    (still available, just no longer mandatory).

A composition is rendered AFTER the background fill but BEFORE template
content. Each composition contributes only ambient design elements
(grids, hairlines, photo zones, accent blocks). Templates draw on top.

The result: two consecutive slides on the same theme can have completely
different visual language even if they're the same kind.
"""
from __future__ import annotations

import random
from typing import Callable, Dict, Optional

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.slide import Slide
from pptx.util import Inches, Pt

from megadeck.design_system.effects import apply_solid_fill
from megadeck.design_system.tokens import Theme


# Type alias for a composition function.
CompositionFn = Callable[[Slide, Theme], None]
COMPOSITIONS: Dict[str, CompositionFn] = {}


def register_composition(name: str):
    def deco(fn: CompositionFn) -> CompositionFn:
        COMPOSITIONS[name] = fn
        return fn
    return deco


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hex_to_rgb(h: str) -> RGBColor:
    h = h.lstrip("#").upper().ljust(6, "0")[:6]
    return RGBColor.from_string(h)


def _add_line(
    slide: Slide,
    *,
    left: float, top: float, width: float, height: float,
    color: RGBColor, weight_pt: float = 0.5,
) -> None:
    sh = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    apply_solid_fill(sh, color)
    sh.line.fill.background()
    return sh


def _add_text(slide: Slide, text: str, *, left: float, top: float, w: float, h: float,
              color: RGBColor, font: str, size_pt: float, bold: bool = False) -> None:
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size_pt)
    r.font.bold = bold
    r.font.color.rgb = color


# ---------------------------------------------------------------------------
# typographic — no shapes, pure space
# ---------------------------------------------------------------------------

@register_composition("typographic")
def _typographic(slide: Slide, theme: Theme) -> None:
    pass  # intentionally empty — typography only


# ---------------------------------------------------------------------------
# swiss — strict grid, accent block, hairlines
# ---------------------------------------------------------------------------

@register_composition("swiss")
def _swiss(slide: Slide, theme: Theme) -> None:
    slide_w = theme.slide_width_in
    slide_h = theme.slide_height_in
    accent = theme.accent
    hairline = theme.hairline

    # Single accent block top-left
    _add_line(
        slide, left=theme.left_margin_in, top=0.55, width=0.45, height=0.10,
        color=accent,
    )
    # Vertical baseline rule on the right margin (1/3 down)
    _add_line(
        slide, left=slide_w - 0.45, top=0.55, width=0.012, height=slide_h - 1.20,
        color=hairline,
    )
    # Horizontal baseline rule near bottom
    _add_line(
        slide, left=theme.left_margin_in, top=slide_h - 0.55,
        width=slide_w - 2 * theme.left_margin_in, height=0.008,
        color=hairline,
    )


# ---------------------------------------------------------------------------
# blueprint — graph paper + corner crop marks
# ---------------------------------------------------------------------------

@register_composition("blueprint")
def _blueprint(slide: Slide, theme: Theme) -> None:
    slide_w = theme.slide_width_in
    slide_h = theme.slide_height_in
    grid_color = theme.hairline

    # Vertical hairlines on a 1.0in grid
    for i in range(1, int(slide_w)):
        _add_line(
            slide, left=float(i), top=0.0,
            width=0.005, height=slide_h,
            color=grid_color,
        )
    # Horizontal hairlines on a 1.0in grid
    for i in range(1, int(slide_h)):
        _add_line(
            slide, left=0.0, top=float(i),
            width=slide_w, height=0.005,
            color=grid_color,
        )
    # Crop marks in the corners
    crop = theme.muted
    L = 0.30
    for cx, cy in (
        (0.20, 0.20), (slide_w - 0.30, 0.20),
        (0.20, slide_h - 0.30), (slide_w - 0.30, slide_h - 0.30),
    ):
        _add_line(slide, left=cx, top=cy, width=L, height=0.012, color=crop)
        _add_line(slide, left=cx, top=cy, width=0.012, height=L, color=crop)


# ---------------------------------------------------------------------------
# brutalist — heavy slabs, raw geometry
# ---------------------------------------------------------------------------

@register_composition("brutalist")
def _brutalist(slide: Slide, theme: Theme) -> None:
    slide_w = theme.slide_width_in
    slide_h = theme.slide_height_in
    title_color = theme.title

    # Heavy black slab across the bottom 0.18in
    _add_line(
        slide, left=0.0, top=slide_h - 0.18,
        width=slide_w, height=0.18,
        color=title_color,
    )
    # Heavy left rail 0.20in
    _add_line(
        slide, left=0.0, top=0.0,
        width=0.20, height=slide_h,
        color=title_color,
    )
    # An asymmetric slab top-right
    _add_line(
        slide, left=slide_w - 1.30, top=0.55,
        width=1.30, height=0.50,
        color=theme.accent,
    )


# ---------------------------------------------------------------------------
# editorial — asymmetric grid, drop-cap rule
# ---------------------------------------------------------------------------

@register_composition("editorial")
def _editorial(slide: Slide, theme: Theme) -> None:
    slide_w = theme.slide_width_in
    slide_h = theme.slide_height_in
    rule = theme.hairline

    # Strong vertical rule at the 7/12 column position
    rule_x = slide_w * (7 / 12)
    _add_line(
        slide, left=rule_x, top=0.65,
        width=0.012, height=slide_h - 1.30,
        color=rule,
    )
    # Top eyebrow rule above title area
    _add_line(
        slide, left=theme.left_margin_in, top=1.10,
        width=2.0, height=0.012,
        color=theme.accent,
    )
    # A single accent square top-right (folio mark)
    _add_line(
        slide, left=slide_w - 0.80, top=0.55,
        width=0.32, height=0.32,
        color=theme.accent_lt,
    )


# ---------------------------------------------------------------------------
# photographic — large photo zone (placeholder card)
# ---------------------------------------------------------------------------

@register_composition("photographic")
def _photographic(slide: Slide, theme: Theme) -> None:
    slide_w = theme.slide_width_in
    slide_h = theme.slide_height_in

    # Photo-placeholder zone — right 45% of the slide
    photo_w = slide_w * 0.45
    photo_l = slide_w - photo_w
    photo_t = 0.0
    photo_h = slide_h
    sh = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(photo_l), Inches(photo_t),
        Inches(photo_w), Inches(photo_h),
    )
    apply_solid_fill(sh, theme.accent_lt)
    sh.line.fill.background()
    # Subtle rule between text and photo
    _add_line(
        slide, left=photo_l - 0.012, top=0.0,
        width=0.012, height=slide_h,
        color=theme.hairline,
    )


# ---------------------------------------------------------------------------
# grid — modular 12-col cell ghosting
# ---------------------------------------------------------------------------

@register_composition("grid")
def _grid(slide: Slide, theme: Theme) -> None:
    slide_w = theme.slide_width_in
    slide_h = theme.slide_height_in
    margin = theme.left_margin_in
    cells = 12
    inner_w = slide_w - 2 * margin
    col_w = inner_w / cells

    # Ghost vertical column markers — TOP and BOTTOM 0.18in tick marks only
    for i in range(cells + 1):
        x = margin + i * col_w
        _add_line(
            slide, left=x, top=0.40, width=0.006, height=0.18,
            color=theme.hairline,
        )
        _add_line(
            slide, left=x, top=slide_h - 0.55, width=0.006, height=0.18,
            color=theme.hairline,
        )


# ---------------------------------------------------------------------------
# orbs — the legacy default, kept for back-compat (still available)
# ---------------------------------------------------------------------------

@register_composition("orbs")
def _orbs(slide: Slide, theme: Theme) -> None:
    """The original default: two glowing orbs. Kept opt-in only."""
    from megadeck.design_system.decorations import apply_decorations

    apply_decorations(slide, theme)


# ---------------------------------------------------------------------------
# Public dispatch
# ---------------------------------------------------------------------------

def apply_composition(slide: Slide, theme: Theme, *, override: Optional[str] = None) -> str:
    """Apply a composition to the slide. Returns the composition name used.

    If `override` names a composition that isn't registered, we silently
    fall back to 'typographic' (and report it as such).
    """
    requested = override or getattr(theme, "composition", None) or "typographic"
    fn = COMPOSITIONS.get(requested)
    if fn is None:
        fn = COMPOSITIONS["typographic"]
        requested = "typographic"
    fn(slide, theme)
    return requested


# Default rotation order — used by the rhythm orchestrator.
DEFAULT_ROTATION = [
    "typographic", "swiss", "editorial", "blueprint",
    "grid", "brutalist", "photographic",
]


def composition_at_index(idx: int, *, rotation=DEFAULT_ROTATION) -> str:
    return rotation[idx % len(rotation)]


__all__ = [
    "COMPOSITIONS", "register_composition",
    "apply_composition", "composition_at_index", "DEFAULT_ROTATION",
]
