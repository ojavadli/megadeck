"""donut_chart template — title + native PowerPoint donut chart."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import DonutChartSlide
from megadeck.design_system.charts import add_donut_chart
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_text,
    fit_title,
    measure_title_height,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_donut_chart(
    slide: Slide,
    data: DonutChartSlide,
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

    title_pt = fit_title(data.title, max_pt=theme.type_scale.h2, width_in=CONTENT_W)
    title_h = measure_title_height(data.title, size_pt=title_pt, width_in=CONTENT_W)
    add_text(
        slide,
        left=LEFT, top=1.20, width=CONTENT_W, height=title_h,
        text=data.title,
        font=theme.font_display, size_pt=title_pt,
        color=theme.title, bold=True,
    )

    chart_top = 1.20 + title_h + 0.40
    chart_size = min(4.50, theme.slide_height_in - chart_top - 0.80)
    # Centre the donut horizontally within content area
    chart_left = LEFT + (CONTENT_W - chart_size) / 2

    add_donut_chart(
        slide,
        left_in=chart_left, top_in=chart_top,
        size_in=chart_size,
        categories=data.categories, values=data.values,
        theme=theme,
    )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
