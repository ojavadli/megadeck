"""Manifesto — dense paragraph treated as the entire artwork.

Used for principle slides ("Hard is good. Hard is what makes it…").
The body type is oversize, the leading is generous, the eyebrow is tiny.
No bullets, no chrome on the body — the words ARE the design.
"""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import ManifestoSlide
from megadeck.design_system.primitives import (
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_text,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_manifesto(
    slide: Slide,
    data: ManifestoSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in
    # Manifesto reads better in 70% width — like a column of editorial text
    BODY_W = CONTENT_W * 0.78

    if data.eyebrow:
        add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme, top=0.95)

    # Drop-cap-ish accent: a thick coloured dash above the body
    add_rect(
        slide,
        left=LEFT, top=1.55, width=0.80, height=0.08,
        fill=theme.accent,
    )

    # Body — large, generously leaded.
    body_pt = (
        theme.type_scale.h3 if len(data.body) <= 200
        else theme.type_scale.h4 if len(data.body) <= 400
        else theme.type_scale.body_large
    )
    body_h = measure_title_height(
        data.body, size_pt=body_pt, width_in=BODY_W, line_spacing=1.40,
    ) + 0.40  # safety pad
    add_text(
        slide,
        left=LEFT, top=1.95, width=BODY_W, height=body_h,
        text=data.body,
        font=theme.font_display,
        size_pt=body_pt,
        color=theme.title,
        bold=False,
        line_spacing=1.40,
        auto_size=False,
    )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
