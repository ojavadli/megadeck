"""Before / After slide — split comparison with verdict."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import BeforeAfterSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_h_line,
    add_oval,
    add_page_chrome,
    add_rect,
    add_round_rect,
    add_text,
    add_v_line,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_before_after(
    slide: Slide,
    data: BeforeAfterSlide,
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

    body_top = 2.40
    has_verdict = bool(data.verdict)
    # Reserve room for the verdict bar (header + line + body ≈ 0.85 in) above
    # the page chrome at y=7.10.
    body_h = (3.40 if has_verdict else 4.40)
    col_gap = 0.40
    col_w = (CONTENT_W - col_gap) / 2

    def build_side(x: float, label: str, points: list[str], muted: bool) -> None:
        # Side label
        head_color = theme.muted if muted else theme.accent_dk
        add_text(
            slide,
            left=x, top=body_top, width=col_w, height=0.45,
            text=label.upper(),
            font=theme.font_body,
            size_pt=theme.type_scale.eyebrow + 1,
            color=head_color,
            bold=True,
        )
        # Card
        card_top = body_top + 0.55
        card_h = body_h - 0.55
        card_fill = theme.overlay if muted else theme.accent_bg
        add_round_rect(
            slide,
            left=x, top=card_top, width=col_w, height=card_h,
            fill=card_fill, line=theme.hairline, line_w=0.5,
            adjust=0.06,
        )
        n = len(points)
        gap = 0.18
        item_h = (card_h - 0.40 - (n - 1) * gap) / n
        for i, p in enumerate(points):
            y = card_top + 0.20 + i * (item_h + gap)
            # Bullet dot
            add_oval(
                slide,
                left=x + 0.20, top=y + 0.18, size=0.12,
                fill=theme.muted if muted else theme.accent,
            )
            add_text(
                slide,
                left=x + 0.45, top=y, width=col_w - 0.55, height=item_h,
                text=p,
                font=theme.font_body,
                size_pt=theme.type_scale.micro + 1,
                color=theme.body,
                line_spacing=1.20,
            )

    build_side(LEFT, data.before_label, data.before_points, muted=True)
    build_side(LEFT + col_w + col_gap, data.after_label, data.after_points, muted=False)

    if has_verdict:
        # Verdict bar across the bottom
        v_top = body_top + body_h + 0.20
        add_h_line(
            slide,
            left=LEFT, top=v_top, width=CONTENT_W,
            color=theme.accent, height=0.04,
        )
        add_text(
            slide,
            left=LEFT, top=v_top + 0.10, width=CONTENT_W, height=0.50,
            text=data.verdict,
            font=theme.font_display,
            size_pt=theme.type_scale.body_large,
            color=theme.title,
            bold=True,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
