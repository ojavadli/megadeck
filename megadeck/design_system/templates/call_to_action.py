"""Call-to-action slide — title + button-styled URL + footer."""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import CallToActionSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_round_rect,
    add_text,
    add_v_line,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_call_to_action(
    slide: Slide,
    data: CallToActionSlide,
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

    # Big hero title
    add_text(
        slide,
        left=LEFT, top=2.00, width=CONTENT_W, height=1.40,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h1 + 4,
        color=theme.title,
        bold=True,
        line_spacing=1.05,
    )
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=3.55, width=CONTENT_W, height=0.85,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.body_large,
            color=theme.muted,
            line_spacing=1.30,
        )

    # CTA button (filled rounded rect with bold text)
    btn_top = 5.00
    btn_w = 4.20
    btn_h = 0.80
    add_round_rect(
        slide,
        left=LEFT, top=btn_top, width=btn_w, height=btn_h,
        fill=theme.accent, line=None,
        adjust=0.45,
    )
    add_text(
        slide,
        left=LEFT, top=btn_top, width=btn_w, height=btn_h,
        text=data.button_text,
        font=theme.font_display,
        size_pt=theme.type_scale.body_large,
        color=theme.inverse,
        bold=True,
        align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE,
    )

    # URL beneath the button
    if data.url:
        add_text(
            slide,
            left=LEFT, top=btn_top + btn_h + 0.20,
            width=CONTENT_W, height=0.40,
            text=data.url,
            font=theme.font_mono,
            size_pt=theme.type_scale.body,
            color=theme.accent_dk,
            bold=True,
        )

    # Footer
    if data.footer:
        add_text(
            slide,
            left=LEFT, top=6.85, width=CONTENT_W, height=0.30,
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
