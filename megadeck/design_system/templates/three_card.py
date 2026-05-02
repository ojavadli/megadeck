"""Three-card slide — three side-by-side cards with badge, label, body."""
from __future__ import annotations

from pptx.slide import Slide

from megadeck.core.schemas import ThreeCardSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_page_chrome,
    add_rect,
    add_round_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_three_card(
    slide: Slide,
    data: ThreeCardSlide,
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
    )
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=2.15,
            width=CONTENT_W, height=0.40,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )

    card_top = 3.00
    card_h = 3.80
    col_gap = 0.40
    col_w = (CONTENT_W - 2 * col_gap) / 3

    for i, card in enumerate(data.items):
        x = LEFT + i * (col_w + col_gap)
        # Main card — themed (real drop shadow on shadow/glass themes,
        # painted-shadow rectangle behind on flat themes).
        if theme.card_style == "flat":
            add_round_rect(
                slide,
                left=x + 0.04, top=card_top + 0.05,
                width=col_w, height=card_h,
                fill=theme.overlay,
                adjust=0.04,
            )
            card_shape = add_round_rect(
                slide,
                left=x, top=card_top,
                width=col_w, height=card_h,
                fill=theme.bg,
                line=theme.hairline,
                line_w=0.5,
                adjust=0.04,
            )
        elif theme.card_style == "glass":
            card_shape = add_round_rect(
                slide,
                left=x, top=card_top,
                width=col_w, height=card_h,
                fill=None, line=None,
                adjust=0.04,
            )
            try:
                from megadeck.design_system.effects import glass_card
                glass_card(card_shape, tint=theme.title, border=theme.title, fill_alpha=14)
            except Exception:
                pass
        else:  # shadow
            card_shape = add_round_rect(
                slide,
                left=x, top=card_top,
                width=col_w, height=card_h,
                fill=theme.surface,
                line=theme.hairline,
                line_w=0.5,
                adjust=0.04,
            )
            try:
                from megadeck.design_system.effects import apply_drop_shadow
                apply_drop_shadow(
                    card_shape, color="000000", alpha_pct=35,
                    blur_pt=24, distance_pt=4,
                )
            except Exception:
                pass
        # Top accent strip — two-tone for gradient feel
        add_rect(
            slide,
            left=x, top=card_top,
            width=col_w / 2, height=0.07,
            fill=theme.accent,
        )
        add_rect(
            slide,
            left=x + col_w / 2, top=card_top,
            width=col_w / 2, height=0.07,
            fill=theme.accent_dk,
        )
        # Badge
        add_text(
            slide,
            left=x + 0.40, top=card_top + 0.40,
            width=col_w - 0.80, height=0.85,
            text=card.badge,
            font=theme.font_display,
            size_pt=theme.type_scale.h1,
            color=theme.accent,
            bold=True,
        )
        # Label
        add_text(
            slide,
            left=x + 0.40, top=card_top + 1.40,
            width=col_w - 0.80, height=0.85,
            text=card.label,
            font=theme.font_display,
            size_pt=theme.type_scale.h4,
            color=theme.title,
            bold=True,
            line_spacing=1.10,
        )
        # Description
        add_text(
            slide,
            left=x + 0.40, top=card_top + 2.30,
            width=col_w - 0.80, height=card_h - 2.50,
            text=card.description,
            font=theme.font_body,
            size_pt=theme.type_scale.micro + 2,
            color=theme.body,
        )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
