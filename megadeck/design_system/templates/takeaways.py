"""Takeaways — numbered key takeaways with chevron treatment."""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR
from pptx.slide import Slide
from pptx.util import Inches, Pt

from megadeck.core.schemas import TakeawaysSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_oval,
    add_page_chrome,
    add_round_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_takeaways(
    slide: Slide,
    data: TakeawaysSlide,
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

    body_top = 2.70
    bottom = 6.95
    available = bottom - body_top
    n = len(data.items)
    gap = 0.20
    item_h = max(0.65, (available - (n - 1) * gap) / n)

    for i, item in enumerate(data.items):
        y = body_top + i * (item_h + gap)
        # Numbered circle
        circle_size = 0.65
        add_oval(
            slide, left=LEFT, top=y + (item_h - circle_size) / 2,
            size=circle_size, fill=theme.accent,
        )
        from pptx.enum.text import PP_ALIGN
        add_text(
            slide,
            left=LEFT, top=y + (item_h - circle_size) / 2,
            width=circle_size, height=circle_size,
            text=str(i + 1),
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.inverse,
            bold=True,
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        # Text
        tb = slide.shapes.add_textbox(
            Inches(LEFT + 0.85), Inches(y),
            Inches(CONTENT_W - 0.85), Inches(item_h),
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.04)
        tf.margin_top = Inches(0.02)
        try:
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        except Exception:
            pass
        p = tf.paragraphs[0]
        try:
            p.line_spacing = 1.20
        except Exception:
            pass
        r1 = p.add_run()
        r1.text = item.head
        r1.font.name = theme.font_display
        r1.font.size = Pt(theme.type_scale.h4 - 4)
        r1.font.bold = True
        r1.font.color.rgb = theme.title
        if item.tail:
            r2 = p.add_run()
            r2.text = "  " + item.tail
            r2.font.name = theme.font_body
            r2.font.size = Pt(theme.type_scale.micro + 1)
            r2.font.color.rgb = theme.body

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
