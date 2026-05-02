"""Pull-quote slide — large quote with attribution."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import PullQuoteSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_pull_quote(
    slide: Slide,
    data: PullQuoteSlide,
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

    # Decorative oversized opening quotation mark (kept as text shape so it
    # styles cleanly with the theme accent).
    add_text(
        slide,
        left=LEFT, top=1.40, width=1.20, height=1.50,
        text="“",
        font=theme.font_display,
        size_pt=160,
        color=theme.accent_lt,
        bold=True,
    )
    # Quote body — italic for editorial feel
    add_text(
        slide,
        left=LEFT, top=2.40, width=CONTENT_W, height=2.80,
        text=data.quote,
        font=theme.font_display,
        size_pt=theme.type_scale.h2,
        color=theme.title,
        bold=False,
        italic=True,
        line_spacing=1.20,
    )
    # Attribution line
    add_rect(
        slide,
        left=LEFT, top=5.50, width=0.40, height=0.04,
        fill=theme.accent,
    )
    add_text(
        slide,
        left=LEFT + 0.55, top=5.40, width=CONTENT_W - 0.55, height=0.40,
        text=data.author,
        font=theme.font_display,
        size_pt=theme.type_scale.body_large,
        color=theme.title,
        bold=True,
    )
    if data.role:
        add_text(
            slide,
            left=LEFT + 0.55, top=5.85, width=CONTENT_W - 0.55, height=0.40,
            text=data.role,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
