"""Feature grid — 3-6 features with icon + title + description in a clean grid."""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import FeatureGridSlide
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


def render_feature_grid(
    slide: Slide,
    data: FeatureGridSlide,
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

    n = len(data.features)
    grid_top = 2.95
    grid_h = 3.85
    cols = 3 if n >= 3 else n
    rows = (n + cols - 1) // cols
    col_gap = 0.30
    row_gap = 0.30
    col_w = (CONTENT_W - (cols - 1) * col_gap) / cols
    row_h = (grid_h - (rows - 1) * row_gap) / rows

    for i, feat in enumerate(data.features):
        col = i % cols
        row = i // cols
        x = LEFT + col * (col_w + col_gap)
        y = grid_top + row * (row_h + row_gap)
        # Icon circle
        icon_size = 0.55
        add_oval(
            slide,
            left=x, top=y, size=icon_size,
            fill=theme.accent_lt,
        )
        if feat.icon_text:
            add_text(
                slide,
                left=x, top=y, width=icon_size, height=icon_size,
                text=feat.icon_text,
                font=theme.font_display,
                size_pt=theme.type_scale.h4 - 4,
                color=theme.accent_dk,
                bold=True,
                align=PP_ALIGN.CENTER,
            )
        # Title
        add_text(
            slide,
            left=x, top=y + 0.75, width=col_w, height=0.50,
            text=feat.title,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 2,
            color=theme.title,
            bold=True,
        )
        # Description
        add_text(
            slide,
            left=x, top=y + 1.30, width=col_w, height=row_h - 1.40,
            text=feat.description,
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
