"""Comparison table — header row + N data rows, themed."""
from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import ComparisonTableSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_h_line,
    add_page_chrome,
    add_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_comparison_table(
    slide: Slide,
    data: ComparisonTableSlide,
    theme: Theme,
    *,
    page_n: int,
    page_total: int,
    section_label: str | None = None,
) -> None:
    set_slide_bg(slide, color=theme.bg, theme=theme)
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

    body_top = 2.40
    bottom = 6.95
    available = bottom - body_top

    cols = len(data.header)
    rows = len(data.rows)
    col_w = CONTENT_W / cols
    header_h = 0.55
    row_h = max(0.45, (available - header_h) / max(rows, 1))

    # Header background
    add_rect(
        slide,
        left=LEFT, top=body_top, width=CONTENT_W, height=header_h,
        fill=theme.accent_bg,
    )
    # Bottom hairline of header
    add_h_line(
        slide,
        left=LEFT, top=body_top + header_h, width=CONTENT_W,
        color=theme.accent, height=0.025,
    )
    # Header cells
    for ci, cell in enumerate(data.header):
        add_text(
            slide,
            left=LEFT + ci * col_w + 0.10, top=body_top,
            width=col_w - 0.20, height=header_h,
            text=cell,
            font=theme.font_display,
            size_pt=theme.type_scale.micro + 1,
            color=theme.accent_dk,
            bold=True,
            anchor=MSO_ANCHOR.MIDDLE,
            align=PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER,
        )
    # Data rows
    for ri, row in enumerate(data.rows):
        y = body_top + header_h + ri * row_h
        # Alternating row tint
        if ri % 2 == 1:
            add_rect(
                slide,
                left=LEFT, top=y, width=CONTENT_W, height=row_h,
                fill=theme.surface,
            )
        cells = list(row.cells) + [""] * (cols - len(row.cells))
        for ci, cell in enumerate(cells[:cols]):
            add_text(
                slide,
                left=LEFT + ci * col_w + 0.10, top=y,
                width=col_w - 0.20, height=row_h,
                text=cell,
                font=theme.font_body if ci > 0 else theme.font_display,
                size_pt=theme.type_scale.micro + (1 if ci == 0 else 0),
                color=theme.title if ci == 0 else theme.body,
                bold=(ci == 0),
                anchor=MSO_ANCHOR.MIDDLE,
                align=PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER,
            )
        # Row separator
        if ri < rows - 1:
            add_h_line(
                slide,
                left=LEFT, top=y + row_h, width=CONTENT_W,
                color=theme.hairline, height=0.008,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
