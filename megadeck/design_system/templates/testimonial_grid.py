"""Testimonial grid — 2-3 customer quotes side by side."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import TestimonialGridSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_round_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_testimonial_grid(
    slide: Slide,
    data: TestimonialGridSlide,
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

    n = len(data.items)
    card_top = 2.40
    card_h = 4.10
    gap = 0.40
    col_w = (CONTENT_W - (n - 1) * gap) / n

    for i, t in enumerate(data.items):
        x = LEFT + i * (col_w + gap)
        # Card
        add_round_rect(
            slide,
            left=x, top=card_top, width=col_w, height=card_h,
            fill=theme.surface, line=theme.hairline, line_w=0.5,
            adjust=0.05,
        )
        # Decorative quote mark
        add_text(
            slide,
            left=x + 0.20, top=card_top + 0.05, width=1.0, height=1.0,
            text="“",
            font=theme.font_display,
            size_pt=80,
            color=theme.accent_lt,
            bold=True,
        )
        # Quote
        add_text(
            slide,
            left=x + 0.30, top=card_top + 0.95, width=col_w - 0.60, height=card_h - 2.20,
            text=t.quote,
            font=theme.font_display,
            size_pt=theme.type_scale.body,
            color=theme.title,
            italic=True,
            line_spacing=1.30,
        )
        # Author
        add_text(
            slide,
            left=x + 0.30, top=card_top + card_h - 1.05,
            width=col_w - 0.60, height=0.45,
            text=t.author,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.title,
            bold=True,
        )
        if t.role:
            add_text(
                slide,
                left=x + 0.30, top=card_top + card_h - 0.55,
                width=col_w - 0.60, height=0.40,
                text=t.role,
                font=theme.font_body,
                size_pt=theme.type_scale.micro,
                color=theme.muted,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
