"""Quote-decorative — pull-quote with a giant decorative open-quote glyph.

Differs from the existing `pull_quote` by being editorial in feel: a
hero-sized typographic " glyph in accent colour anchors the slide,
the quote itself is set in the display serif at h2 size with italic, and
the attribution sits in a tight block under the rule.
"""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import QuoteDecorativeSlide
from megadeck.design_system.primitives import (
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_text,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_quote_decorative(
    slide: Slide,
    data: QuoteDecorativeSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in

    if data.eyebrow:
        add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme, top=0.85)

    # Giant open-quote glyph in accent colour — placed BELOW the eyebrow line.
    # auto_size=False (the character is sized to the box, not the other way).
    add_text(
        slide,
        left=LEFT, top=1.40, width=2.4, height=1.80,
        text="\u201C",
        font=theme.font_display,
        size_pt=160,
        color=theme.accent,
        bold=True,
        line_spacing=0.85,
        auto_size=False,
    )

    quote_top = 3.30
    quote_pt = fit_title(
        data.quote, max_pt=theme.type_scale.h2, min_pt=22, width_in=CONTENT_W * 0.82,
    )
    quote_h = measure_title_height(
        data.quote, size_pt=quote_pt, width_in=CONTENT_W * 0.82, line_spacing=1.30,
    ) + 0.40
    add_text(
        slide,
        left=LEFT, top=quote_top, width=CONTENT_W * 0.82, height=quote_h,
        text=data.quote,
        font=theme.font_display,
        size_pt=quote_pt,
        color=theme.title,
        italic=True,
        line_spacing=1.30,
        auto_size=False,
    )

    # Hairline rule between quote and attribution
    rule_top = quote_top + quote_h + 0.30
    add_rect(
        slide,
        left=LEFT, top=rule_top, width=0.80, height=0.04,
        fill=theme.accent,
    )

    add_text(
        slide,
        left=LEFT, top=rule_top + 0.20, width=CONTENT_W, height=0.40,
        text=data.author,
        font=theme.font_display,
        size_pt=theme.type_scale.h4 - 4,
        color=theme.title,
        bold=True,
    )
    if data.role:
        add_text(
            slide,
            left=LEFT, top=rule_top + 0.65, width=CONTENT_W, height=0.40,
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
