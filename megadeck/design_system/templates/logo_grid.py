"""Logo grid — 4-12 customer/partner logos shown as named tiles."""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import LogoGridSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_round_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_logo_grid(
    slide: Slide,
    data: LogoGridSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)
    add_corner_dotgrid(slide, theme)
    add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in

    add_text(
        slide,
        left=LEFT, top=1.20, width=CONTENT_W, height=0.85,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h2,
        color=theme.title,
        bold=True,
    )
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=2.15, width=CONTENT_W, height=0.40,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )

    n = len(data.logos)
    grid_top = 2.85
    grid_h = 4.05
    cols = 4 if n >= 8 else min(n, 4)
    rows = (n + cols - 1) // cols
    col_gap = 0.30
    row_gap = 0.30
    col_w = (CONTENT_W - (cols - 1) * col_gap) / cols
    row_h = (grid_h - (rows - 1) * row_gap) / rows

    for i, logo in enumerate(data.logos):
        col = i % cols
        row = i // cols
        x = LEFT + col * (col_w + col_gap)
        y = grid_top + row * (row_h + row_gap)
        add_round_rect(
            slide,
            left=x, top=y, width=col_w, height=row_h,
            fill=theme.surface, line=theme.hairline, line_w=0.5,
            adjust=0.10,
        )
        add_text(
            slide,
            left=x, top=y, width=col_w, height=row_h,
            text=logo,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.muted,
            bold=True,
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
