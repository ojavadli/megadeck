"""Section-hero — full-bleed gradient with massive part number + giant title.

Cinematic chapter break, much louder than `section_divider`. The slide
gets its own gradient overlay regardless of theme.bg_style — the part
number is rendered massive and outlined behind/beside the title.
"""
from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.slide import Slide
from pptx.util import Inches

WHITE = RGBColor(0xFF, 0xFF, 0xFF)

from megadeck.core.schemas import SectionHeroSlide
from megadeck.design_system.effects import apply_linear_gradient
from megadeck.design_system.primitives import (
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_text,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_section_hero(
    slide: Slide,
    data: SectionHeroSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)

    # Always overlay a strong diagonal gradient — section breaks should
    # *feel* different from any list/content slide.
    full = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0,
        Inches(theme.slide_width_in), Inches(theme.slide_height_in),
    )
    full.line.fill.background()
    accent_hex = str(theme.accent)
    accent_dk_hex = str(theme.accent_dk)
    bg_hex = str(theme.bg)
    apply_linear_gradient(
        full,
        stops=[(0, bg_hex, 100), (50, accent_dk_hex, 80), (100, accent_hex, 60)],
        angle_deg=135.0,
    )

    LEFT = theme.left_margin_in
    SLIDE_W = theme.slide_width_in
    SLIDE_H = theme.slide_height_in
    CONTENT_W = theme.content_width_in

    # Massive outline-styled part number on the right edge — pure typography.
    # auto_size=False: the box is sized to fit a 2-3 char number at 200pt;
    # we never want this glyph growing the textbox off-canvas.
    add_text(
        slide,
        left=SLIDE_W - 4.5, top=0.50,
        width=4.0, height=3.5,
        text=data.part_number,
        font=theme.font_display,
        size_pt=200,
        color=theme.accent_lt,
        bold=True,
        line_spacing=0.92,
        auto_size=False,
    )

    # Eyebrow part-label tag on the left
    add_eyebrow(slide, text=data.part_label.upper(), theme=theme, top=0.95)

    # Giant title — the main statement
    title_pt = fit_title(
        data.title,
        max_pt=theme.type_scale.hero,
        min_pt=44,
        width_in=CONTENT_W * 0.80,
    )
    title_h = measure_title_height(
        data.title, size_pt=title_pt, width_in=CONTENT_W * 0.80, line_spacing=0.98,
    ) + 0.30
    add_text(
        slide,
        left=LEFT, top=SLIDE_H * 0.40,
        width=CONTENT_W * 0.80, height=title_h,
        text=data.title,
        font=theme.font_display,
        size_pt=title_pt,
        color=WHITE,
        bold=True,
        line_spacing=0.98,
        auto_size=False,
    )

    if data.subtitle:
        sub_top = SLIDE_H * 0.40 + title_h + 0.40
        add_text(
            slide,
            left=LEFT, top=sub_top, width=CONTENT_W * 0.80, height=1.0,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.body_large,
            color=theme.accent_lt,
            line_spacing=1.30,
        )

    # Page chrome stays on top
    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=None,  # section divider IS the section label
        on_dark=True,
    )