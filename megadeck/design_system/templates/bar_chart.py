"""bar_chart template — title + native PowerPoint bar/column chart."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import BarChartSlide
from megadeck.design_system.charts import add_bar_chart
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


def render_bar_chart(
    slide: Slide,
    data: BarChartSlide,
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
        font=theme.font_display,
        size_pt=title_pt,
        color=theme.title,
        bold=True,
    )
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=1.20 + title_h + 0.05,
            width=CONTENT_W, height=0.45,
            text=data.subtitle,
            font=theme.font_body, size_pt=14, color=theme.body,
        )
        chart_top = 1.20 + title_h + 0.55
    else:
        chart_top = 1.20 + title_h + 0.30

    bottom = 6.40
    chart_h = max(2.0, bottom - chart_top)
    add_bar_chart(
        slide,
        left_in=LEFT, top_in=chart_top,
        width_in=CONTENT_W, height_in=chart_h,
        categories=data.categories, values=data.values,
        series_name=data.series_name, theme=theme,
        horizontal=data.horizontal,
    )

    if data.note:
        add_text(
            slide,
            left=LEFT, top=bottom + 0.10,
            width=CONTENT_W, height=0.40,
            text=data.note, font=theme.font_body,
            size_pt=11, color=theme.muted, italic=True,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
