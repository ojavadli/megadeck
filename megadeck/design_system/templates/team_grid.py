"""Team grid — 3-6 team members shown as initials avatar + name + role."""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import TeamGridSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_oval,
    add_page_chrome,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_team_grid(
    slide: Slide,
    data: TeamGridSlide,
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

    n = len(data.members)
    grid_top = 2.80
    grid_h = 3.95
    cols = 3 if n >= 3 else n
    rows = (n + cols - 1) // cols
    col_gap = 0.50
    row_gap = 0.30
    col_w = (CONTENT_W - (cols - 1) * col_gap) / cols
    row_h = (grid_h - (rows - 1) * row_gap) / rows

    for i, m in enumerate(data.members):
        col = i % cols
        row = i // cols
        x = LEFT + col * (col_w + col_gap)
        y = grid_top + row * (row_h + row_gap)
        # Avatar
        avatar_size = 1.40
        avatar_x = x + (col_w - avatar_size) / 2
        add_oval(
            slide,
            left=avatar_x, top=y,
            size=avatar_size,
            fill=theme.accent_bg,
            line=theme.accent,
        )
        add_text(
            slide,
            left=avatar_x, top=y, width=avatar_size, height=avatar_size,
            text=m.initials.upper(),
            font=theme.font_display,
            size_pt=theme.type_scale.h2,
            color=theme.accent_dk,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        # Name
        add_text(
            slide,
            left=x, top=y + avatar_size + 0.20,
            width=col_w, height=0.45,
            text=m.name,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 4,
            color=theme.title,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        # Role
        add_text(
            slide,
            left=x, top=y + avatar_size + 0.70,
            width=col_w, height=0.45,
            text=m.role,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
            align=PP_ALIGN.CENTER,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
