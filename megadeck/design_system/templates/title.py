"""Title / cover slide — opening of the deck."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import TitleSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_h_line,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_title(
    slide: Slide,
    data: TitleSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg)
    add_corner_dotgrid(slide, theme)
    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in
    if data.eyebrow:
        add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme, top=1.20)
    # Massive title centered vertically
    add_text(
        slide,
        left=LEFT, top=2.20, width=CONTENT_W, height=2.40,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h1 + 12,
        color=theme.title,
        bold=True,
        line_spacing=1.04,
    )
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=4.70, width=CONTENT_W, height=0.55,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.body_large,
            color=theme.muted,
        )
    # Bottom block: presenter / date / venue
    add_h_line(
        slide,
        left=LEFT, top=6.10, width=2.5, color=theme.accent, height=0.04,
    )
    line_y = 6.30
    if data.presenter:
        add_text(
            slide,
            left=LEFT, top=line_y, width=CONTENT_W, height=0.40,
            text=data.presenter,
            font=theme.font_body,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.accent_dk,
            bold=True,
        )
    bits = []
    if data.date:
        bits.append(data.date)
    if data.venue:
        bits.append(data.venue)
    if bits:
        add_text(
            slide,
            left=LEFT, top=line_y + 0.45, width=CONTENT_W, height=0.40,
            text="  ·  ".join(bits),
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )
