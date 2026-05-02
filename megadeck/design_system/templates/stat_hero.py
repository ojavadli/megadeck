"""Stat hero — one massive number with title and subtitle."""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import StatHeroSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_stat_hero(
    slide: Slide,
    data: StatHeroSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg)
    add_corner_dotgrid(slide, theme)
    add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in

    # Massive stat value
    add_text(
        slide,
        left=LEFT, top=1.50, width=CONTENT_W, height=2.85,
        text=data.stat.value,
        font=theme.font_display,
        size_pt=180,
        color=theme.accent,
        bold=True,
        line_spacing=1.0,
    )
    # Stat label
    add_text(
        slide,
        left=LEFT, top=4.40, width=CONTENT_W, height=0.50,
        text=data.stat.label.upper(),
        font=theme.font_body,
        size_pt=theme.type_scale.body,
        color=theme.muted,
        bold=True,
    )
    # Accent dash
    add_rect(
        slide,
        left=LEFT, top=5.05, width=0.55, height=0.05,
        fill=theme.accent,
    )
    # Title
    add_text(
        slide,
        left=LEFT, top=5.20, width=CONTENT_W, height=0.85,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h3,
        color=theme.title,
        bold=True,
        line_spacing=1.05,
    )
    # Subtitle
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=6.10, width=CONTENT_W, height=0.55,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.body,
            color=theme.body,
            line_spacing=1.20,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
