"""Layout variants for `kpi_grid`.

Variants
--------
* `default`     — equal tiles in a row (existing).
* `stack`       — vertical stack of full-width KPI rows with sparklines space.
* `asymmetric`  — one giant featured tile + smaller satellites.
* `data_card`   — info-graphic style: number left, label right, divider rule.
"""
from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import KpiGridSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_round_rect,
    add_text,
    add_themed_card,
    add_v_line,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme
from megadeck.design_system.variants import register_variant


def _delta_color(theme: Theme, positive: bool) -> RGBColor:
    if positive:
        return RGBColor.from_string("16A34A")  # green-600
    return RGBColor.from_string("DC2626")  # red-600


@register_variant("kpi_grid", "stack")
def render_kpi_grid_stack(
    slide: Slide,
    data: KpiGridSlide,
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
        font=theme.font_display, size_pt=title_pt,
        color=theme.title, bold=True,
    )

    body_top = 1.20 + title_h + 0.40
    bottom = 6.95
    avail = max(2.0, bottom - body_top)
    n = len(data.tiles)
    gap = 0.20
    row_h = max(0.85, (avail - (n - 1) * gap) / max(n, 1))

    for i, tile in enumerate(data.tiles):
        y = body_top + i * (row_h + gap)
        # Big value left
        add_text(
            slide,
            left=LEFT, top=y, width=4.0, height=row_h,
            text=tile.value,
            font=theme.font_display, size_pt=min(56, int(row_h * 60)),
            color=theme.title, bold=True,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        # Label + delta right
        add_text(
            slide,
            left=LEFT + 4.20, top=y + 0.10, width=CONTENT_W - 4.20, height=0.45,
            text=tile.label,
            font=theme.font_body, size_pt=14,
            color=theme.muted,
        )
        if tile.delta:
            add_text(
                slide,
                left=LEFT + 4.20, top=y + 0.55,
                width=CONTENT_W - 4.20, height=0.45,
                text=tile.delta,
                font=theme.font_body, size_pt=16,
                color=_delta_color(theme, tile.delta_positive), bold=True,
            )
        # Bottom hairline rule
        if i < n - 1:
            add_round_rect(
                slide,
                left=LEFT, top=y + row_h + (gap / 2) - 0.005,
                width=CONTENT_W, height=0.012,
                fill=theme.hairline, adjust=0.0,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("kpi_grid", "asymmetric")
def render_kpi_grid_asymmetric(
    slide: Slide,
    data: KpiGridSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """Big featured tile (first KPI) + 1-3 smaller satellites."""
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
        font=theme.font_display, size_pt=title_pt,
        color=theme.title, bold=True,
    )

    grid_top = 1.20 + title_h + 0.40
    bottom = 6.95
    avail = max(3.0, bottom - grid_top)
    big_w = CONTENT_W * 0.55
    small_w = CONTENT_W - big_w - 0.30
    sats = data.tiles[1:4]
    n_sats = max(1, len(sats))
    small_h = (avail - (n_sats - 1) * 0.20) / n_sats

    # Featured big tile
    big = data.tiles[0]
    add_themed_card(slide, theme,
                    left=LEFT, top=grid_top, width=big_w, height=avail)
    add_text(
        slide,
        left=LEFT + 0.40, top=grid_top + 0.40, width=big_w - 0.80, height=0.45,
        text=big.label.upper(),
        font=theme.font_body, size_pt=12,
        color=theme.muted,
    )
    add_text(
        slide,
        left=LEFT + 0.40, top=grid_top + 1.0,
        width=big_w - 0.80, height=avail * 0.50,
        text=big.value,
        font=theme.font_display, size_pt=120,
        color=theme.title, bold=True, line_spacing=0.95,
        auto_size=False,
    )
    if big.delta:
        add_text(
            slide,
            left=LEFT + 0.40, top=grid_top + avail - 0.80,
            width=big_w - 0.80, height=0.50,
            text=big.delta,
            font=theme.font_body, size_pt=18,
            color=_delta_color(theme, big.delta_positive), bold=True,
        )

    # Satellite tiles
    sat_x = LEFT + big_w + 0.30
    for i, tile in enumerate(sats):
        y = grid_top + i * (small_h + 0.20)
        add_themed_card(slide, theme,
                        left=sat_x, top=y, width=small_w, height=small_h)
        add_text(
            slide,
            left=sat_x + 0.30, top=y + 0.20, width=small_w - 0.60, height=0.40,
            text=tile.label.upper(),
            font=theme.font_body, size_pt=10,
            color=theme.muted,
        )
        add_text(
            slide,
            left=sat_x + 0.30, top=y + 0.60, width=small_w - 0.60, height=small_h - 1.0,
            text=tile.value,
            font=theme.font_display, size_pt=44,
            color=theme.title, bold=True,
            auto_size=False,
        )
        if tile.delta:
            add_text(
                slide,
                left=sat_x + 0.30, top=y + small_h - 0.50,
                width=small_w - 0.60, height=0.40,
                text=tile.delta,
                font=theme.font_body, size_pt=11,
                color=_delta_color(theme, tile.delta_positive), bold=True,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("kpi_grid", "data_card")
def render_kpi_grid_data_card(
    slide: Slide,
    data: KpiGridSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """Info-graphic style: number left, label right, divider hairlines."""
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
        font=theme.font_display, size_pt=title_pt,
        color=theme.title, bold=True,
    )

    body_top = 1.20 + title_h + 0.40
    bottom = 6.95
    avail = max(2.0, bottom - body_top)
    n = len(data.tiles)
    cols = 2 if n >= 4 else n
    rows = (n + cols - 1) // cols
    col_gap = 0.50
    row_gap = 0.40
    col_w = (CONTENT_W - (cols - 1) * col_gap) / cols
    row_h = (avail - (rows - 1) * row_gap) / max(rows, 1)

    for i, tile in enumerate(data.tiles):
        col = i % cols
        row = i // cols
        x = LEFT + col * (col_w + col_gap)
        y = body_top + row * (row_h + row_gap)
        # Big number left
        add_text(
            slide,
            left=x, top=y, width=col_w * 0.50, height=row_h,
            text=tile.value,
            font=theme.font_display,
            size_pt=min(72, int(row_h * 70)),
            color=theme.accent, bold=True,
            anchor=MSO_ANCHOR.MIDDLE,
            auto_size=False,
        )
        # Vertical hairline divider
        add_v_line(slide,
                   left=x + col_w * 0.50 - 0.015, top=y + 0.10,
                   height=row_h - 0.20, color=theme.hairline, width=0.012)
        # Label + delta right
        add_text(
            slide,
            left=x + col_w * 0.55, top=y + 0.20,
            width=col_w * 0.45, height=0.45,
            text=tile.label.upper(),
            font=theme.font_body, size_pt=11,
            color=theme.muted,
        )
        if tile.delta:
            add_text(
                slide,
                left=x + col_w * 0.55, top=y + 0.70,
                width=col_w * 0.45, height=0.50,
                text=tile.delta,
                font=theme.font_display, size_pt=18,
                color=_delta_color(theme, tile.delta_positive), bold=True,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
