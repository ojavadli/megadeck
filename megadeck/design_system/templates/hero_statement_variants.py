"""Layout variants for `hero_statement`.

Variants
--------
* `default`   — title + supports left-aligned (existing).
* `centered`  — everything centered, with accent rule under title.
* `full_bleed`— giant title that fills the whole canvas, supports below.
* `mark`      — title with a left accent mark (Müller-Brockmann style).
"""
from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import HeroStatementSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_round_rect,
    add_text,
    add_v_line,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme
from megadeck.design_system.variants import register_variant


@register_variant("hero_statement", "centered")
def render_hero_statement_centered(
    slide: Slide,
    data: HeroStatementSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)
    add_corner_dotgrid(slide, theme)

    sw = theme.slide_width_in
    sh = theme.slide_height_in

    add_text(
        slide,
        left=0.6, top=1.40, width=sw - 1.20, height=0.40,
        text=data.eyebrow.upper(),
        font=theme.font_body, size_pt=12, color=theme.muted,
        align=PP_ALIGN.CENTER,
        auto_size=False,
    )

    title_pt = fit_title(data.statement, max_pt=88, width_in=sw - 1.20)
    title_h = measure_title_height(data.statement, size_pt=title_pt, width_in=sw - 1.20)
    add_text(
        slide,
        left=0.6, top=1.90, width=sw - 1.20, height=title_h + 0.30,
        text=data.statement,
        font=theme.font_display, size_pt=title_pt,
        color=theme.title, bold=True,
        align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
        line_spacing=1.05, auto_size=False,
    )

    rule_y = 1.90 + title_h + 0.50
    add_round_rect(
        slide,
        left=sw / 2 - 0.45, top=rule_y,
        width=0.90, height=0.040,
        fill=theme.accent, adjust=0.0,
    )

    if data.supports:
        text = "  ·  ".join(data.supports)
        add_text(
            slide,
            left=0.6, top=rule_y + 0.30, width=sw - 1.20, height=1.20,
            text=text,
            font=theme.font_body, size_pt=15,
            color=theme.body, align=PP_ALIGN.CENTER,
            line_spacing=1.40,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("hero_statement", "mark")
def render_hero_statement_mark(
    slide: Slide,
    data: HeroStatementSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """Title with a tall left accent mark — Müller-Brockmann signature."""
    set_slide_bg(slide, color=theme.bg, theme=theme)
    add_corner_dotgrid(slide, theme)
    add_eyebrow(slide, text=data.eyebrow.upper(), theme=theme)

    sw = theme.slide_width_in
    LEFT = theme.left_margin_in

    # Tall left accent mark
    add_round_rect(
        slide,
        left=LEFT, top=1.60,
        width=0.080, height=4.60,
        fill=theme.accent, adjust=0.0,
    )

    title_pt = fit_title(data.statement, max_pt=72, width_in=sw - LEFT - 0.60)
    title_h = measure_title_height(data.statement, size_pt=title_pt, width_in=sw - LEFT - 0.60)
    add_text(
        slide,
        left=LEFT + 0.36, top=1.60,
        width=sw - LEFT - 0.40 - 0.36, height=title_h + 0.30,
        text=data.statement,
        font=theme.font_display, size_pt=title_pt,
        color=theme.title, bold=True, line_spacing=1.05,
        auto_size=False,
    )

    if data.supports:
        for i, line in enumerate(data.supports[:4]):
            add_text(
                slide,
                left=LEFT + 0.36, top=1.60 + title_h + 0.50 + i * 0.42,
                width=sw - LEFT - 0.40 - 0.36, height=0.40,
                text=line,
                font=theme.font_body, size_pt=15, color=theme.body,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )


@register_variant("hero_statement", "full_bleed")
def render_hero_statement_full_bleed(
    slide: Slide,
    data: HeroStatementSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    """Massive title fills the canvas; supports as a single line below."""
    set_slide_bg(slide, color=theme.bg, theme=theme)
    add_corner_dotgrid(slide, theme)

    sw = theme.slide_width_in
    sh = theme.slide_height_in

    title_pt = fit_title(data.statement, max_pt=140, width_in=sw - 1.20)
    title_h = measure_title_height(data.statement, size_pt=title_pt, width_in=sw - 1.20)
    add_text(
        slide,
        left=0.6, top=1.0, width=sw - 1.20, height=title_h + 0.30,
        text=data.statement,
        font=theme.font_display, size_pt=title_pt,
        color=theme.title, bold=True, line_spacing=0.98,
        auto_size=False,
    )

    if data.supports:
        text = "  /  ".join(data.supports[:3])
        add_text(
            slide,
            left=0.6, top=sh - 1.40, width=sw - 1.20, height=0.50,
            text=text.upper(),
            font=theme.font_body, size_pt=11, color=theme.muted,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
