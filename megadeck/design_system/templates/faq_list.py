"""FAQ list — 3-5 questions and answers."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import FaqListSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_h_line,
    add_page_chrome,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_faq_list(
    slide: Slide,
    data: FaqListSlide,
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

    body_top = 2.55
    bottom = 6.95
    available = bottom - body_top
    n = len(data.items)
    gap = 0.20
    item_h = (available - (n - 1) * gap) / n
    q_h = 0.40
    a_h = item_h - q_h - 0.05

    for i, faq in enumerate(data.items):
        y = body_top + i * (item_h + gap)
        # Q label
        add_text(
            slide,
            left=LEFT, top=y, width=0.50, height=q_h,
            text="Q.",
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.accent,
            bold=True,
        )
        add_text(
            slide,
            left=LEFT + 0.50, top=y, width=CONTENT_W - 0.50, height=q_h,
            text=faq.question,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.title,
            bold=True,
        )
        # Answer
        add_text(
            slide,
            left=LEFT + 0.50, top=y + q_h, width=CONTENT_W - 0.50, height=a_h,
            text=faq.answer,
            font=theme.font_body,
            size_pt=theme.type_scale.micro + 1,
            color=theme.body,
            line_spacing=1.30,
        )
        # Divider line below
        if i < n - 1:
            add_h_line(
                slide,
                left=LEFT, top=y + item_h + gap / 2,
                width=CONTENT_W,
                color=theme.hairline,
                height=0.008,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
