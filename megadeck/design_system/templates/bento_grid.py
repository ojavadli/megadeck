"""Bento grid — 4 cards in a 2x2 layout, all equal size."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import BentoGridSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_round_rect,
    add_text,
    add_themed_card,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_bento_grid(
    slide: Slide,
    data: BentoGridSlide,
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

    grid_top = 2.40
    grid_h = 4.50
    col_gap = 0.30
    row_gap = 0.30
    col_w = (CONTENT_W - col_gap) / 2
    row_h = (grid_h - row_gap) / 2

    for i, card in enumerate(data.items):
        col = i % 2
        row = i // 2
        x = LEFT + col * (col_w + col_gap)
        y = grid_top + row * (row_h + row_gap)
        add_themed_card(
            slide, theme,
            left=x, top=y, width=col_w, height=row_h,
            adjust=0.04,
        )
        # Top accent
        add_rect(
            slide,
            left=x, top=y, width=col_w / 3, height=0.06,
            fill=theme.accent,
        )
        # Badge
        add_text(
            slide,
            left=x + 0.40, top=y + 0.30, width=col_w - 0.80, height=0.50,
            text=card.badge,
            font=theme.font_display,
            size_pt=theme.type_scale.h3,
            color=theme.accent,
            bold=True,
        )
        # Label
        add_text(
            slide,
            left=x + 0.40, top=y + 0.95, width=col_w - 0.80, height=0.50,
            text=card.label,
            font=theme.font_display,
            size_pt=theme.type_scale.h4,
            color=theme.title,
            bold=True,
        )
        # Description
        add_text(
            slide,
            left=x + 0.40, top=y + 1.50, width=col_w - 0.80, height=row_h - 1.65,
            text=card.description,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.body,
            line_spacing=1.20,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
