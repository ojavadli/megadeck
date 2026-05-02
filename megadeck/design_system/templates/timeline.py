"""Timeline slide — horizontal milestone flow with connecting line."""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import TimelineSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_h_line,
    add_oval,
    add_page_chrome,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_timeline(
    slide: Slide,
    data: TimelineSlide,
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

    add_text(
        slide,
        left=LEFT, top=1.20, width=CONTENT_W, height=0.85,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h2,
        color=theme.title,
        bold=True,
    )

    line_y = 4.00
    n = len(data.events)
    if n < 2:
        return
    step = CONTENT_W / (n - 1) if n > 1 else CONTENT_W
    # Connecting horizontal line
    add_h_line(
        slide,
        left=LEFT, top=line_y, width=CONTENT_W,
        color=theme.accent_lt, height=0.05,
    )
    dot_size = 0.25
    for i, ev in enumerate(data.events):
        cx = LEFT + i * step
        # Dot on the line
        add_oval(
            slide,
            left=cx - dot_size / 2,
            top=line_y - dot_size / 2 + 0.025,
            size=dot_size,
            fill=theme.accent,
            line=theme.bg,
        )
        # Label above
        add_text(
            slide,
            left=cx - 1.20, top=line_y - 1.20, width=2.40, height=0.30,
            text=ev.label,
            font=theme.font_body,
            size_pt=theme.type_scale.eyebrow + 1,
            color=theme.muted,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        add_text(
            slide,
            left=cx - 1.30, top=line_y - 0.85, width=2.60, height=0.45,
            text=ev.title,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.title,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        # Description below
        if ev.description:
            add_text(
                slide,
                left=cx - 1.40, top=line_y + 0.30,
                width=2.80, height=1.30,
                text=ev.description,
                font=theme.font_body,
                size_pt=theme.type_scale.micro,
                color=theme.body,
                align=PP_ALIGN.CENTER,
                line_spacing=1.20,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
