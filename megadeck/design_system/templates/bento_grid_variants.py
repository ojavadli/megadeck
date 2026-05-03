"""Layout variants for `bento_grid`.

Variants
--------
* `default`     — 4 equal cards 2×2 (existing).
* `featured`    — 1 big featured card + 3 stacked smaller cards.
* `strip`       — 1 wide top card + 3 narrow bottom cards.
* `tiles`       — 2×2 with one tall tile spanning two rows on the left.
"""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import BentoGridSlide
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


def _draw_bento_card(
    slide, theme,
    *,
    x, y, w, h, item,
    head_pt: float = 18, body_pt: float = 13,
):
    add_themed_card(slide, theme, left=x, top=y, width=w, height=h, adjust=0.05)
    add_text(
        slide,
        left=x + 0.30, top=y + 0.30, width=1.4, height=0.40,
        text=item.badge,
        font=theme.font_display, size_pt=14,
        color=theme.accent, bold=True,
    )
    add_text(
        slide,
        left=x + 0.30, top=y + 0.75, width=w - 0.60, height=0.50,
        text=item.label,
        font=theme.font_display, size_pt=head_pt,
        color=theme.title, bold=True,
    )
    add_text(
        slide,
        left=x + 0.30, top=y + 1.30, width=w - 0.60, height=h - 1.55,
        text=item.description,
        font=theme.font_body, size_pt=body_pt,
        color=theme.body, line_spacing=1.40,
    )


@register_variant("bento_grid", "featured")
def render_bento_grid_featured(
    slide: Slide,
    data: BentoGridSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """1 big featured card + 3 small stacked cards on the right."""
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
    small_h = (avail - 0.40) / 3

    _draw_bento_card(
        slide, theme,
        x=LEFT, y=grid_top, w=big_w, h=avail,
        item=data.items[0], head_pt=24, body_pt=14,
    )
    sat_x = LEFT + big_w + 0.30
    for i, item in enumerate(data.items[1:4]):
        y = grid_top + i * (small_h + 0.20)
        _draw_bento_card(
            slide, theme,
            x=sat_x, y=y, w=small_w, h=small_h,
            item=item, head_pt=15, body_pt=11,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("bento_grid", "strip")
def render_bento_grid_strip(
    slide: Slide,
    data: BentoGridSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """1 wide top card + 3 narrow cards in a strip below."""
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
    top_h = avail * 0.45
    bot_h = avail - top_h - 0.30
    col_gap = 0.20
    bot_col_w = (CONTENT_W - 2 * col_gap) / 3

    _draw_bento_card(
        slide, theme,
        x=LEFT, y=grid_top, w=CONTENT_W, h=top_h,
        item=data.items[0], head_pt=22, body_pt=14,
    )
    bot_y = grid_top + top_h + 0.30
    for i, item in enumerate(data.items[1:4]):
        x = LEFT + i * (bot_col_w + col_gap)
        _draw_bento_card(
            slide, theme,
            x=x, y=bot_y, w=bot_col_w, h=bot_h,
            item=item, head_pt=15, body_pt=11,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("bento_grid", "tiles")
def render_bento_grid_tiles(
    slide: Slide,
    data: BentoGridSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """Tall left tile spanning 2 rows + 3 small tiles right."""
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
    tall_w = CONTENT_W * 0.40
    right_w = CONTENT_W - tall_w - 0.30
    half_w = (right_w - 0.20) / 2
    half_h = (avail - 0.20) / 2

    # Tall left tile (item 0)
    _draw_bento_card(
        slide, theme,
        x=LEFT, y=grid_top, w=tall_w, h=avail,
        item=data.items[0], head_pt=22, body_pt=14,
    )
    # Top-right (item 1)
    _draw_bento_card(
        slide, theme,
        x=LEFT + tall_w + 0.30, y=grid_top, w=right_w, h=half_h,
        item=data.items[1], head_pt=18, body_pt=12,
    )
    # Bottom-right two side-by-side
    for i, item in enumerate(data.items[2:4]):
        x = LEFT + tall_w + 0.30 + i * (half_w + 0.20)
        _draw_bento_card(
            slide, theme,
            x=x, y=grid_top + half_h + 0.20, w=half_w, h=half_h,
            item=item, head_pt=15, body_pt=11,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
