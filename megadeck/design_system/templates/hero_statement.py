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
    fit_title,
    measure_title_height,
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

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in

    statement_pt = fit_title(
        data.statement, max_pt=theme.type_scale.hero, min_pt=36, width_in=CONTENT_W,
    )
    statement_h = measure_title_height(
        data.statement, size_pt=statement_pt, width_in=CONTENT_W, line_spacing=1.0,
    )
    statement_top = 2.10
    add_text(
        slide,
        left=LEFT, top=statement_top,
        width=CONTENT_W, height=statement_h,
        text=data.statement,
        font=theme.font_display,
        size_pt=statement_pt,
        color=theme.title,
        bold=True,
        line_spacing=1.0,
    )

    dash_top = statement_top + statement_h + 0.20
    add_rect(
        slide,
        left=LEFT, top=dash_top,
        width=0.55, height=0.06,
        fill=theme.accent,
    )

    if data.supports:
        bottom = 7.00
        sup_top = dash_top + 0.30
        available = max(0.5, bottom - sup_top)
        n = len(data.supports)
        line_h = min(0.55, available / max(n, 1))
        for i, line in enumerate(data.supports):
            add_text(
                slide,
                left=LEFT,
                top=sup_top + i * line_h,
                width=CONTENT_W, height=line_h,
                text=line,
                font=theme.font_body,
                size_pt=theme.type_scale.body_large,
                color=theme.body,
                line_spacing=1.20,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
