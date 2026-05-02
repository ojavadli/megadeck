"""Stat callout — full-bleed massive number as the entire slide.

Different from `stat_hero` (which has chrome and a side dash): this one
treats the number as artwork. The number occupies 60-70% of the slide
height, label in caps below, optional context paragraph beneath. No
numbered chrome, no decorations to fight with the type.
"""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import StatCalloutSlide
from megadeck.design_system.primitives import (
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_stat_callout(
    slide: Slide,
    data: StatCalloutSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in
    SLIDE_H = theme.slide_height_in

    add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme, top=0.95)

    # The hero number — sized to fill the slide vertically. We pick a font
    # pt that comfortably fits in the box; auto_size OFF so the box never
    # grows past the slide canvas.
    value_pt = 180 if len(data.value) <= 3 else 140 if len(data.value) <= 6 else 100
    add_text(
        slide,
        left=LEFT, top=1.50, width=CONTENT_W, height=SLIDE_H * 0.50,
        text=data.value,
        font=theme.font_display,
        size_pt=value_pt,
        color=theme.accent,
        bold=True,
        line_spacing=0.92,
        auto_size=False,
    )

    # Accent dash beneath the number
    add_rect(
        slide,
        left=LEFT, top=SLIDE_H * 0.50 + 1.65,
        width=0.80, height=0.07,
        fill=theme.accent,
    )

    # Label — uppercase, mid-grey
    add_text(
        slide,
        left=LEFT, top=SLIDE_H * 0.50 + 1.85, width=CONTENT_W, height=0.55,
        text=data.label.upper(),
        font=theme.font_body,
        size_pt=theme.type_scale.body_large,
        color=theme.muted,
        bold=True,
    )

    # Context paragraph
    if data.context:
        add_text(
            slide,
            left=LEFT, top=SLIDE_H * 0.50 + 2.45, width=CONTENT_W, height=0.80,
            text=data.context,
            font=theme.font_body,
            size_pt=theme.type_scale.body,
            color=theme.body,
            line_spacing=1.30,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
