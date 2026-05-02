"""Pricing table — 2-3 tiers with featured highlight."""
from __future__ import annotations

from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide

from megadeck.core.schemas import PricingTableSlide
from megadeck.design_system.primitives import (
    add_corner_dotgrid,
    add_eyebrow,
    add_oval,
    add_page_chrome,
    add_round_rect,
    add_text,
    add_v_line,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


def render_pricing_table(
    slide: Slide,
    data: PricingTableSlide,
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
    if data.subtitle:
        add_text(
            slide,
            left=LEFT, top=2.15, width=CONTENT_W, height=0.40,
            text=data.subtitle,
            font=theme.font_body,
            size_pt=theme.type_scale.micro,
            color=theme.muted,
        )

    n = len(data.tiers)
    card_top = 2.85
    card_h = 4.05
    gap = 0.30
    col_w = (CONTENT_W - (n - 1) * gap) / n

    for i, tier in enumerate(data.tiers):
        x = LEFT + i * (col_w + gap)
        # Card
        fill = theme.accent_bg if tier.is_featured else theme.surface
        line = theme.accent if tier.is_featured else theme.hairline
        line_w = 1.5 if tier.is_featured else 0.5
        add_round_rect(
            slide,
            left=x, top=card_top, width=col_w, height=card_h,
            fill=fill, line=line, line_w=line_w,
            adjust=0.05,
        )
        # Featured ribbon
        if tier.is_featured:
            add_text(
                slide,
                left=x, top=card_top - 0.40, width=col_w, height=0.35,
                text="MOST POPULAR",
                font=theme.font_body,
                size_pt=theme.type_scale.eyebrow - 1,
                color=theme.accent,
                bold=True,
                align=PP_ALIGN.CENTER,
            )
        # Tier name
        add_text(
            slide,
            left=x + 0.30, top=card_top + 0.30, width=col_w - 0.60, height=0.45,
            text=tier.name,
            font=theme.font_display,
            size_pt=theme.type_scale.h4 - 2,
            color=theme.accent_dk if tier.is_featured else theme.title,
            bold=True,
        )
        # Price
        add_text(
            slide,
            left=x + 0.30, top=card_top + 0.85, width=col_w - 0.60, height=0.85,
            text=tier.price,
            font=theme.font_display,
            size_pt=theme.type_scale.h1,
            color=theme.title,
            bold=True,
        )
        # Tagline
        if tier.tagline:
            add_text(
                slide,
                left=x + 0.30, top=card_top + 1.70, width=col_w - 0.60, height=0.40,
                text=tier.tagline,
                font=theme.font_body,
                size_pt=theme.type_scale.micro,
                color=theme.muted,
            )
        # Features list
        feat_top = card_top + 2.20
        for j, feature in enumerate(tier.features[:6]):
            y = feat_top + j * 0.30
            add_oval(slide, left=x + 0.30, top=y + 0.08, size=0.10,
                     fill=theme.accent if tier.is_featured else theme.muted)
            add_text(
                slide,
                left=x + 0.50, top=y, width=col_w - 0.80, height=0.30,
                text=feature,
                font=theme.font_body,
                size_pt=theme.type_scale.micro - 1,
                color=theme.body,
            )

    add_page_chrome(
        slide, theme=theme,
        page_n=page_n, page_total=page_total,
        section_label=section_label,
    )
