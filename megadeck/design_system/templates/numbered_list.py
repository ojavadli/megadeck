"""Numbered list slide — big outlined numbers + bold head + body tail."""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide
from pptx.util import Inches, Pt

from megadeck.core.schemas import NumberedListSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_text,
    add_v_line,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_numbered_list(
    slide: Slide,
    data: NumberedListSlide,
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
        left=LEFT, top=1.20,
        width=CONTENT_W, height=0.85,
        text=data.title,
        font=theme.font_display,
        size_pt=theme.type_scale.h2,
        color=theme.title,
        bold=True,
        line_spacing=1.05,
    )
    body_top = 1.20 + 0.95
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=body_top,
            width=CONTENT_W, height=0.40,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )
        body_top += 0.55
    else:
        body_top += 0.10

    bottom = 6.95
    available = bottom - body_top
    n = len(data.items)

    # Adaptive sizing — keeps text inside bounds for any item count
    if n <= 3:
        head_pt, tail_pt, gap, num_pt = 22, 19, 0.30, 64
    elif n == 4:
        head_pt, tail_pt, gap, num_pt = 21, 18, 0.22, 56
    elif n == 5:
        head_pt, tail_pt, gap, num_pt = 19, 17, 0.18, 50
    else:
        head_pt, tail_pt, gap, num_pt = 17, 15, 0.14, 44
    item_h = max(0.65, (available - (n - 1) * gap) / n)

    NUM_COL_W = 1.30

    for i, item in enumerate(data.items):
        y = body_top + i * (item_h + gap)
        # Big outlined number
        add_text(
            slide,
            left=LEFT, top=y - 0.05,
            width=NUM_COL_W, height=item_h + 0.10,
            text=f"{i+1:02d}",
            font=theme.font_display,
            size_pt=num_pt,
            color=theme.accent_lt,
            bold=True,
            align=PP_ALIGN.LEFT,
            anchor=MSO_ANCHOR.MIDDLE,
            line_spacing=0.95,
        )
        # Vertical accent
        bar_pad = 0.06
        add_v_line(
            slide,
            left=LEFT + NUM_COL_W,
            top=y + bar_pad,
            height=item_h - 2 * bar_pad,
            color=theme.accent,
            width=0.025,
        )
        # Text block (head + tail in one paragraph)
        text_left = LEFT + NUM_COL_W + 0.20
        text_w = CONTENT_W - NUM_COL_W - 0.20
        tb = slide.shapes.add_textbox(
            Inches(text_left), Inches(y), Inches(text_w), Inches(item_h),
        )
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.04)
        tf.margin_top = Inches(0.02)
        tf.margin_bottom = Inches(0.02)
        try:
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        except Exception:
            pass
        p = tf.paragraphs[0]
        try:
            p.line_spacing = 1.15
        except Exception:
            pass
        # Head
        r1 = p.add_run()
        r1.text = item.head
        r1.font.name = theme.font_display
        r1.font.size = Pt(head_pt)
        r1.font.bold = True
        r1.font.color.rgb = theme.title
        # Tail
        if item.tail:
            r2 = p.add_run()
            r2.text = "  " + item.tail
            r2.font.name = theme.font_body
            r2.font.size = Pt(tail_pt)
            r2.font.color.rgb = theme.body

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
