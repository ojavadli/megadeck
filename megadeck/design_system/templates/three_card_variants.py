"""Layout variants for `three_card`.

Variants
--------
* `default`     — three equal-width cards in a row (existing).
* `staggered`   — three cards, each offset vertically (cascading).
* `asymmetric`  — one big featured card + two smaller cards beneath.
"""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import ThreeCardSlide
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
from megadeck.design_system.variants import register_variant


def _draw_card(
    slide, theme, *,
    x: float, y: float, w: float, h: float,
    head: str, body: str,
    head_pt: float = 18, body_pt: float = 13,
) -> None:
    add_themed_card(slide, theme, left=x, top=y, width=w, height=h, adjust=0.05)
    add_text(
        slide,
        left=x + 0.30, top=y + 0.30, width=w - 0.60, height=0.50,
        text=head,
        font=theme.font_display, size_pt=head_pt,
        color=theme.title, bold=True,
    )
    if body:
        add_text(
            slide,
            left=x + 0.30, top=y + 0.95, width=w - 0.60, height=h - 1.30,
            text=body,
            font=theme.font_body, size_pt=body_pt,
            color=theme.body, line_spacing=1.40,
        )


@register_variant("three_card", "staggered")
def render_three_card_staggered(
    slide: Slide,
    data: ThreeCardSlide,
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

    grid_top = 1.20 + title_h + 0.40
    bottom = 6.95
    available = max(2.5, bottom - grid_top)
    col_gap = 0.30
    col_w = (CONTENT_W - 2 * col_gap) / 3
    base_h = min(available - 0.80, 2.80)
    # Stagger vertical offsets: -0.40, 0, +0.40 inches.
    offsets = [-0.40, 0.00, 0.40]

    for i, item in enumerate(data.items):
        x = LEFT + i * (col_w + col_gap)
        y = grid_top + offsets[i]
        _draw_card(
            slide, theme,
            x=x, y=y, w=col_w, h=base_h,
            head=item.label, body=item.description,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("three_card", "asymmetric")
def render_three_card_asymmetric(
    slide: Slide,
    data: ThreeCardSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """One feature card on the left + two stacked cards on the right."""
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
    available = max(3.0, bottom - grid_top)

    big_w = CONTENT_W * 0.55
    small_w = CONTENT_W - big_w - 0.30
    small_h = (available - 0.30) / 2

    # Big feature card on the left
    _draw_card(
        slide, theme,
        x=LEFT, y=grid_top, w=big_w, h=available,
        head=data.items[0].label, body=data.items[0].description,
        head_pt=24, body_pt=14,
    )
    # Two small cards stacked on the right
    for i, item in enumerate(data.items[1:3]):
        x = LEFT + big_w + 0.30
        y = grid_top + i * (small_h + 0.30)
        _draw_card(
            slide, theme,
            x=x, y=y, w=small_w, h=small_h,
            head=item.label, body=item.description,
            head_pt=16, body_pt=12,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
