"""Section divider — large title break, optionally on a dark background."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import SectionDividerSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_h_line,
    add_page_chrome,
    add_text,
    add_v_line,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_section_divider(
    slide: Slide,
    data: SectionDividerSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    on_dark = data.dark_background
    if on_dark:
        bg_color = theme.title  # use the deep slate as background
        title_color = theme.inverse
        sub_color = theme.muted
        eyebrow_color = theme.accent_lt
        chrome_line = theme.overlay
        chrome_text = theme.muted
    else:
        bg_color = theme.bg
        title_color = theme.title
        sub_color = theme.muted
        eyebrow_color = theme.accent
        chrome_line = theme.hairline
        chrome_text = theme.light
    set_slide_bg(slide, color=bg_color)

    if not on_dark:
        add_corner_dotgrid(slide, theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in

    # Eyebrow
    add_v_line(
        slide,
        left=LEFT - 0.10, top=2.55,
        height=0.30,
        color=theme.accent,
    )
    add_text(
        slide,
        left=LEFT, top=2.55,
        width=4.0, height=0.32,
        text=data.part_label.upper(),
        font=theme.font_body,
        size_pt=theme.type_scale.eyebrow + 1,
        color=eyebrow_color,
        bold=True,
    )
    # Big title (sized to fit on one line)
    add_text(
        slide,
        left=LEFT, top=2.95,
        width=CONTENT_W, height=2.10,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h1 + 6,
        color=title_color,
        bold=True,
        line_spacing=1.05,
    )
    # Subtitle pushed lower so a wrapped title can't overlap
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=5.20,
            width=CONTENT_W, height=0.55,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.body_large,
            color=sub_color,
        )

    # Chrome — both light and dark variants
    add_h_line(
        slide,
        left=LEFT, top=7.10,
        width=CONTENT_W,
        color=chrome_line,
        height=0.012,
    )
    if section_label:
        add_text(
            slide,
            left=LEFT, top=7.18,
            width=6.0, height=0.30,
            text=section_label,
            font=theme.font_body,
            size_pt=theme.type_scale.eyebrow - 1,
            color=chrome_text,
            bold=True,
        )
    add_text(
        slide,
        left=theme.slide_width_in - theme.right_margin_in - 1.20,
        top=7.18, width=1.20, height=0.30,
        text=f"{page_n:02d} / {page_total:02d}",
        font=theme.font_body,
        size_pt=theme.type_scale.eyebrow - 1,
        color=chrome_text,
    )
