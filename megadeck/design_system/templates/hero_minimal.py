"""Hero-minimal — Apple-keynote-style giant single line, full bleed, no chrome.

The whole slide is one massive sentence. No bullets, no decoration except a
tiny eyebrow + footer. Used for opening statements / declarations. The
content area uses 70-80% of the slide and the type is sized to nearly fill
the line width.
"""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import HeroMinimalSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_text,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_hero_minimal(
    slide: Slide,
    data: HeroMinimalSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in
    CENTER_Y = theme.slide_height_in / 2

    if data.eyebrow:
        add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme, top=0.85)

    # Massive title — sized to fill 2-3 lines max via fit_title with a much
    # higher upper bound than other templates (this is THE statement).
    title_pt = fit_title(
        data.title,
        max_pt=theme.type_scale.hero + 36,  # up to ~100pt
        min_pt=44,
        width_in=CONTENT_W,
    )
    title_h = measure_title_height(
        data.title, size_pt=title_pt, width_in=CONTENT_W, line_spacing=0.98,
    ) + 0.30  # safety pad
    title_top = max(1.6, CENTER_Y - title_h / 2)
    add_text(
        slide,
        left=LEFT, top=title_top,
        width=CONTENT_W, height=title_h,
        text=data.title,
        font=theme.font_display,
        size_pt=title_pt,
        color=theme.title,
        bold=True,
        line_spacing=0.98,
        auto_size=False,
    )

    if data.footer:
        add_text(
            slide,
            left=LEFT, top=theme.slide_height_in - 1.0,
            width=CONTENT_W, height=0.40,
            text=data.footer,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
