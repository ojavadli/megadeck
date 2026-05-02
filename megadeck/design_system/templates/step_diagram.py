"""Step diagram — sequential 3-5 nodes with arrow connectors."""
from __future__ import annotations

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide
from pptx.util import Inches, Pt

from megadeck.core.schemas import StepDiagramSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_round_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def _add_arrow(slide: Slide, left: float, top: float, w: float, h: float, color):
    arrow = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW,
        Inches(left), Inches(top), Inches(w), Inches(h),
    )
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = color
    arrow.line.fill.background()
    return arrow


def render_step_diagram(
    slide: Slide,
    data: StepDiagramSlide,
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

    n = len(data.steps)
    arrow_w = 0.40
    box_top = 3.10
    box_h = 2.30
    total_arrow_w = arrow_w * (n - 1)
    box_w = (CONTENT_W - total_arrow_w) / n

    for i, step in enumerate(data.steps):
        x = LEFT + i * (box_w + arrow_w)
        # Step card
        add_round_rect(
            slide,
            left=x, top=box_top, width=box_w, height=box_h,
            fill=theme.surface, line=theme.hairline, line_w=0.5,
            adjust=0.08,
        )
        # Step number badge
        add_text(
            slide,
            left=x + 0.20, top=box_top + 0.20, width=box_w - 0.40, height=0.50,
            text=f"STEP {i+1:02d}",
            font=theme.font_body,
            size_pt=theme.type_scale.eyebrow,
            color=theme.accent,
            bold=True,
        )
        # Step title
        add_text(
            slide,
            left=x + 0.20, top=box_top + 0.70, width=box_w - 0.40, height=0.55,
            text=step.title,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.title,
            bold=True,
            line_spacing=1.10,
        )
        # Step description
        if step.description:
            add_text(
                slide,
                left=x + 0.20, top=box_top + 1.30,
                width=box_w - 0.40, height=box_h - 1.45,
                text=step.description,
                font=theme.font_body,
                size_pt=theme.type_scale.micro,
                color=theme.body,
                line_spacing=1.20,
            )
        # Arrow to next step
        if i < n - 1:
            ax = x + box_w
            ay = box_top + box_h / 2 - 0.15
            _add_arrow(slide, ax, ay, arrow_w, 0.30, color=theme.accent_lt)

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
