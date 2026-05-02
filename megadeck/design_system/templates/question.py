"""Question slide — large 'Questions?' moment with optional contact line."""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import QuestionSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_oval,
    add_page_chrome,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_question(
    slide: Slide,
    data: QuestionSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)
    add_corner_dotgrid(slide, theme)

    LEFT = theme.left_margin_in
    CONTENT_W = theme.content_width_in

    # Decorative big "?" on the right side
    qm_size = 4.0
    add_oval(
        slide,
        left=theme.slide_width_in - qm_size - 0.5,
        top=(theme.slide_height_in - qm_size) / 2,
        size=qm_size,
        fill=theme.accent_bg,
    )
    add_text(
        slide,
        left=theme.slide_width_in - qm_size - 0.5,
        top=(theme.slide_height_in - qm_size) / 2,
        width=qm_size, height=qm_size,
        text="?",
        font=theme.font_display,
        size_pt=240,
        color=theme.accent,
        bold=True,
        align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE,
    )

    # Big title
    add_text(
        slide,
        left=LEFT, top=2.50, width=CONTENT_W * 0.55, height=1.40,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h1 + 8,
        color=theme.title,
        bold=True,
        line_spacing=1.05,
    )
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=4.10, width=CONTENT_W * 0.55, height=1.20,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.body_large,
            color=theme.muted,
            line_spacing=1.30,
        )
    if data.contact:
        add_text(
            slide,
            left=LEFT, top=6.85, width=CONTENT_W, height=0.30,
            text=data.contact,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.accent_dk,
            bold=True,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
