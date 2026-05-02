"""Hero statement slide — one massive line, supporting copy below."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import HeroStatementSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_hero_statement(
    slide: Slide,
    data: HeroStatementSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg)
    add_corner_dotgrid(slide, theme)
    add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme, top=0.95)

    # Hero statement
    add_text(
        slide,
        left=theme.left_margin_in, top=2.10,
        width=theme.content_width_in, height=2.00,
        text=data.statement,
        font=theme.font_display,
        size_pt=theme.type_scale.hero,
        color=theme.title,
        bold=True,
        line_spacing=1.0,
    )

    # Thick accent dash under the statement
    add_rect(
        slide,
        left=theme.left_margin_in, top=4.30,
        width=0.55, height=0.06,
        fill=theme.accent,
    )

    # Supporting lines
    if data.supports:
        for i, line in enumerate(data.supports):
            add_text(
                slide,
                left=theme.left_margin_in,
                top=4.65 + i * 0.55,
                width=theme.content_width_in, height=0.45,
                text=line,
                font=theme.font_body,
                size_pt=theme.type_scale.body_large,
                color=theme.body,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
