"""SWOT matrix — 2x2 grid of Strengths, Weaknesses, Opportunities, Threats."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import SwotMatrixSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_oval,
    add_page_chrome,
    add_round_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_swot_matrix(
    slide: Slide,
    data: SwotMatrixSlide,
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

    add_text(
        slide,
        left=LEFT, top=1.20, width=CONTENT_W, height=0.85,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h2,
        color=theme.title,
        bold=True,
    )

    grid_top = 2.60
    grid_h = 4.30
    cell_gap = 0.25
    cell_w = (CONTENT_W - cell_gap) / 2
    cell_h = (grid_h - cell_gap) / 2

    quadrants = [
        ("Strengths",      data.strengths,     theme.success, 0, 0),
        ("Weaknesses",     data.weaknesses,    theme.warning, 1, 0),
        ("Opportunities",  data.opportunities, theme.accent,  0, 1),
        ("Threats",        data.threats,       theme.danger,  1, 1),
    ]
    for label, items, accent, col, row in quadrants:
        x = LEFT + col * (cell_w + cell_gap)
        y = grid_top + row * (cell_h + cell_gap)
        add_round_rect(
            slide,
            left=x, top=y, width=cell_w, height=cell_h,
            fill=theme.surface, line=theme.hairline, line_w=0.5,
            adjust=0.04,
        )
        # Header strip
        from megadeck.design_system.primitives import add_rect
        add_rect(slide, left=x, top=y, width=cell_w, height=0.08, fill=accent)
        # Title
        add_text(
            slide,
            left=x + 0.30, top=y + 0.20, width=cell_w - 0.60, height=0.45,
            text=label.upper(),
            font=theme.font_body,
            size_pt=theme.type_scale.eyebrow + 1,
            color=accent,
            bold=True,
        )
        # Items list
        for j, item in enumerate(items[:5]):
            iy = y + 0.75 + j * 0.32
            add_oval(
                slide, left=x + 0.30, top=iy + 0.10, size=0.10,
                fill=accent,
            )
            add_text(
                slide,
                left=x + 0.50, top=iy, width=cell_w - 0.80, height=0.30,
                text=item,
                font=theme.font_body,
                size_pt=theme.type_scale.micro,
                color=theme.body,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
