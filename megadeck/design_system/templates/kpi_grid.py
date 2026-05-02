"""KPI grid — 2 to 4 metric tiles with delta indicators."""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import KpiGridSlide
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


def render_kpi_grid(
    slide: Slide,
    data: KpiGridSlide,
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
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=2.15, width=CONTENT_W, height=0.40,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )

    n = len(data.tiles)
    grid_top = 3.10
    grid_h = 3.50
    gap = 0.30
    tile_w = (CONTENT_W - (n - 1) * gap) / n

    # The display-number font has to shrink when there are more tiles or the
    # value strings are long (e.g. "1,832").
    max_value_len = max(len(t.value) for t in data.tiles)
    if n >= 4:
        value_pt = 36 if max_value_len <= 4 else 30
    elif n == 3:
        value_pt = 44 if max_value_len <= 4 else 36
    else:
        value_pt = theme.type_scale.display_number

    for i, tile in enumerate(data.tiles):
        x = LEFT + i * (tile_w + gap)
        add_themed_card(
            slide, theme,
            left=x, top=grid_top, width=tile_w, height=grid_h,
            adjust=0.06,
        )
        # Top accent
        add_rect(
            slide,
            left=x, top=grid_top, width=tile_w, height=0.10,
            fill=theme.accent,
        )
        # Label
        add_text(
            slide,
            left=x + 0.30, top=grid_top + 0.45, width=tile_w - 0.60, height=0.40,
            text=tile.label.upper(),
            font=theme.font_body,
            size_pt=theme.type_scale.eyebrow + 1,
            color=theme.muted,
            bold=True,
        )
        # Big value (font scaled to fit tile width)
        add_text(
            slide,
            left=x + 0.20, top=grid_top + 0.95, width=tile_w - 0.40, height=1.40,
            text=tile.value,
            font=theme.font_display,
            size_pt=value_pt,
            color=theme.title,
            bold=True,
            line_spacing=1.0,
        )
        # Delta
        if tile.delta:
            delta_color = theme.success if tile.delta_positive else theme.danger
            add_text(
                slide,
                left=x + 0.30, top=grid_top + 2.50,
                width=tile_w - 0.60, height=0.50,
                text=tile.delta,
                font=theme.font_body,
                size_pt=theme.type_scale.body,
                color=delta_color,
                bold=True,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
