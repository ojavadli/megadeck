"""Layout variants for `two_column`.

Variants
--------
* `default`     — left/right columns with shared subtitle (existing).
* `split_rule`  — title on top, big vertical centered rule, items each side.
* `vs_arrow`    — left side title + items, "vs" badge mid, right side title + items.
* `stacked`     — left card stacked above right card (vertical version).
"""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import TwoColumnSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_oval,
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


def _draw_items(slide, theme, items, *, x, y, w, head_pt=15, tail_pt=12, gap=0.30):
    cy = y
    for it in items:
        add_text(
            slide,
            left=x, top=cy, width=w, height=0.40,
            text=it.head,
            font=theme.font_display, size_pt=head_pt,
            color=theme.title, bold=True,
        )
        if it.tail:
            add_text(
                slide,
                left=x, top=cy + 0.42, width=w, height=0.55,
                text=it.tail,
                font=theme.font_body, size_pt=tail_pt,
                color=theme.body, line_spacing=1.30,
            )
            cy += 0.42 + 0.65 + gap
        else:
            cy += 0.42 + gap


@register_variant("two_column", "split_rule")
def render_two_column_split_rule(
    slide: Slide,
    data: TwoColumnSlide,
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

    grid_top = 1.20 + title_h + 0.50
    half_w = (CONTENT_W - 0.50) / 2

    add_v_line(
        slide,
        left=LEFT + half_w + 0.25, top=grid_top - 0.10,
        height=6.95 - grid_top, color=theme.title, width=0.025,
    )

    add_text(
        slide,
        left=LEFT, top=grid_top, width=half_w, height=0.40,
        text=data.left_title,
        font=theme.font_display, size_pt=18,
        color=theme.accent, bold=True,
    )
    _draw_items(slide, theme, data.left_items,
                x=LEFT, y=grid_top + 0.55, w=half_w)

    add_text(
        slide,
        left=LEFT + half_w + 0.50, top=grid_top, width=half_w, height=0.40,
        text=data.right_title,
        font=theme.font_display, size_pt=18,
        color=theme.accent, bold=True,
    )
    _draw_items(slide, theme, data.right_items,
                x=LEFT + half_w + 0.50, y=grid_top + 0.55, w=half_w)

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("two_column", "vs_arrow")
def render_two_column_vs_arrow(
    slide: Slide,
    data: TwoColumnSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """Two cards with a circular 'VS' badge between them."""
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

    grid_top = 1.20 + title_h + 0.50
    badge = 0.85
    gap = 0.50
    card_w = (CONTENT_W - badge - 2 * gap) / 2
    card_h = 6.95 - grid_top

    add_themed_card(slide, theme,
                    left=LEFT, top=grid_top, width=card_w, height=card_h)
    add_text(
        slide,
        left=LEFT + 0.30, top=grid_top + 0.30, width=card_w - 0.60, height=0.50,
        text=data.left_title,
        font=theme.font_display, size_pt=20,
        color=theme.title, bold=True,
    )
    _draw_items(slide, theme, data.left_items,
                x=LEFT + 0.30, y=grid_top + 0.95,
                w=card_w - 0.60, head_pt=14, tail_pt=11)

    badge_x = LEFT + card_w + gap
    badge_y = grid_top + (card_h - badge) / 2
    add_oval(slide, left=badge_x, top=badge_y, size=badge, fill=theme.accent)
    add_text(
        slide,
        left=badge_x, top=badge_y, width=badge, height=badge,
        text="VS",
        font=theme.font_display, size_pt=22,
        color=theme.inverse, bold=True,
        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
        auto_size=False,
    )

    right_x = badge_x + badge + gap
    add_themed_card(slide, theme,
                    left=right_x, top=grid_top, width=card_w, height=card_h)
    add_text(
        slide,
        left=right_x + 0.30, top=grid_top + 0.30, width=card_w - 0.60, height=0.50,
        text=data.right_title,
        font=theme.font_display, size_pt=20,
        color=theme.title, bold=True,
    )
    _draw_items(slide, theme, data.right_items,
                x=right_x + 0.30, y=grid_top + 0.95,
                w=card_w - 0.60, head_pt=14, tail_pt=11)

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("two_column", "stacked")
def render_two_column_stacked(
    slide: Slide,
    data: TwoColumnSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """Top card / bottom card vertical layout."""
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
    avail = 6.95 - grid_top
    gap = 0.30
    card_h = (avail - gap) / 2

    for i, (label, items) in enumerate((
        (data.left_title, data.left_items),
        (data.right_title, data.right_items),
    )):
        y = grid_top + i * (card_h + gap)
        add_themed_card(slide, theme,
                        left=LEFT, top=y, width=CONTENT_W, height=card_h)
        add_text(
            slide,
            left=LEFT + 0.30, top=y + 0.20, width=2.0, height=0.45,
            text=f"{i+1:02d}",
            font=theme.font_display, size_pt=28,
            color=theme.accent, bold=True,
        )
        add_text(
            slide,
            left=LEFT + 1.20, top=y + 0.30, width=CONTENT_W - 1.50, height=0.45,
            text=label,
            font=theme.font_display, size_pt=18,
            color=theme.title, bold=True,
        )
        # Render bullets in a single line (joined by " · ")
        joined = "  ·  ".join(it.head for it in items[:4])
        add_text(
            slide,
            left=LEFT + 1.20, top=y + 0.85, width=CONTENT_W - 1.50,
            height=card_h - 1.0,
            text=joined,
            font=theme.font_body, size_pt=13,
            color=theme.body, line_spacing=1.40,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
