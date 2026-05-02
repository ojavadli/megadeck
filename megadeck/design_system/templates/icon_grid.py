"""icon_grid template — 3-6 Lucide icon tiles with title + body."""
from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import IconGridSlide
from megadeck.design_system.icons import add_icon
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_text,
    add_themed_card,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_icon_grid(
    slide: Slide,
    data: IconGridSlide,
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

    title_pt = fit_title(data.title, max_pt=theme.type_scale.h2, width_in=CONTENT_W)
    title_h = measure_title_height(data.title, size_pt=title_pt, width_in=CONTENT_W)
    add_text(
        slide,
        left=LEFT, top=1.20, width=CONTENT_W, height=title_h,
        text=data.title,
        font=theme.font_display,
        size_pt=title_pt,
        color=theme.title,
        bold=True,
    )

    grid_top = 1.20 + title_h + 0.40
    bottom = 6.95
    available = max(2.0, bottom - grid_top)
    n = len(data.items)
    cols = 3 if n >= 3 else n
    rows = (n + cols - 1) // cols
    col_gap = 0.30
    row_gap = 0.30
    col_w = (CONTENT_W - (cols - 1) * col_gap) / cols
    row_h = max(1.50, (available - (rows - 1) * row_gap) / rows)

    for i, item in enumerate(data.items):
        col = i % cols
        row = i // cols
        x = LEFT + col * (col_w + col_gap)
        y = grid_top + row * (row_h + row_gap)
        add_themed_card(slide, theme, left=x, top=y, width=col_w, height=row_h, adjust=0.05)
        # Icon top-left of the card
        icon_size = 0.75
        add_icon(
            slide, item.icon,
            left_in=x + 0.30, top_in=y + 0.30,
            size_in=icon_size, color=theme.accent,
        )
        # Heading + body below the icon
        add_text(
            slide,
            left=x + 0.30, top=y + 0.30 + icon_size + 0.18,
            width=col_w - 0.60, height=0.45,
            text=item.head,
            font=theme.font_display,
            size_pt=16, color=theme.title, bold=True,
        )
        if item.tail:
            add_text(
                slide,
                left=x + 0.30, top=y + 0.30 + icon_size + 0.65,
                width=col_w - 0.60, height=row_h - 0.30 - icon_size - 0.65,
                text=item.tail,
                font=theme.font_body,
                size_pt=12, color=theme.body, line_spacing=1.30,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
