"""Slide-rhythm orchestrator (variants AND compositions).

A deck reads as composed (not random) when slide selection follows a
*rhythm*. This module post-processes a `Deck` to enforce four layered
rhythms across the deck without altering any content:

  1. variant rhythm for `numbered_list`     (default → cards → timeline → split)
  2. variant rhythm for `three_card`         (default → staggered → asymmetric)
  3. variant rhythm for `two_column`         (default → split_rule → vs_arrow → stacked)
  4. variant rhythm for `kpi_grid`           (default → stack → asymmetric → data_card)
  5. variant rhythm for `bento_grid`         (default → featured → strip → tiles)
  6. composition rhythm — every slide gets a different visual composition
     so adjacent slides never share visual language.
  7. section_divider → section_hero promotion.
"""
from __future__ import annotations

from typing import List, Optional

from megadeck.core.schemas import (
    BentoGridSlide,
    Deck,
    KpiGridSlide,
    NumberedListSlide,
    SectionDividerSlide,
    SectionHeroSlide,
    Slide as SlideUnion,
    ThreeCardSlide,
    TwoColumnSlide,
)


_NUMBERED_LIST_VARIANT_CYCLE: List[Optional[str]] = [
    None, "cards", "timeline", "split",
]

_THREE_CARD_VARIANT_CYCLE: List[Optional[str]] = [
    None, "staggered", "asymmetric",
]

_TWO_COLUMN_VARIANT_CYCLE: List[Optional[str]] = [
    None, "split_rule", "vs_arrow", "stacked",
]

_KPI_GRID_VARIANT_CYCLE: List[Optional[str]] = [
    None, "stack", "asymmetric", "data_card",
]

_BENTO_GRID_VARIANT_CYCLE: List[Optional[str]] = [
    None, "featured", "strip", "tiles",
]


_COMPOSITION_ROTATION: List[str] = [
    "typographic", "swiss", "editorial", "blueprint",
    "grid", "brutalist", "photographic", "mono-grid",
    "bauhaus", "risograph",
]


def apply_rhythm(deck: Deck, *, period: int = 6) -> Deck:
    """Return a copy of `deck` with all rhythms applied. Content is never
    altered — only `slide.variant` and `slide.composition` are set."""
    # Respect the theme's `rotate_compositions=False` setting: when the theme
    # opts out, every slide inherits the theme's `composition` rather than
    # being assigned a different composition per slide. This is essential for
    # cohesive themes like 'apple-glass' that want the same futurist HUD on
    # every slide.
    from megadeck.design_system.tokens import get_theme
    theme_for_rhythm = get_theme(deck.theme) if deck.theme else None
    rotate = True
    forced_comp: Optional[str] = None
    if theme_for_rhythm is not None:
        rotate = bool(getattr(theme_for_rhythm, "rotate_compositions", True))
        if not rotate:
            forced_comp = getattr(theme_for_rhythm, "composition", None)

    new_slides: List[SlideUnion] = []
    nl_i = 0
    tc_i = 0
    twc_i = 0
    kg_i = 0
    bg_i = 0
    comp_i = 0
    last_comp: Optional[str] = None

    for i, sd in enumerate(deck.slides):
        replacement: SlideUnion = sd

        if isinstance(sd, NumberedListSlide):
            v = _NUMBERED_LIST_VARIANT_CYCLE[nl_i % len(_NUMBERED_LIST_VARIANT_CYCLE)]
            nl_i += 1
            replacement = sd.model_copy(update={"variant": v})
        elif isinstance(sd, ThreeCardSlide):
            v = _THREE_CARD_VARIANT_CYCLE[tc_i % len(_THREE_CARD_VARIANT_CYCLE)]
            tc_i += 1
            replacement = sd.model_copy(update={"variant": v})
        elif isinstance(sd, TwoColumnSlide):
            v = _TWO_COLUMN_VARIANT_CYCLE[twc_i % len(_TWO_COLUMN_VARIANT_CYCLE)]
            twc_i += 1
            replacement = sd.model_copy(update={"variant": v})
        elif isinstance(sd, KpiGridSlide):
            v = _KPI_GRID_VARIANT_CYCLE[kg_i % len(_KPI_GRID_VARIANT_CYCLE)]
            kg_i += 1
            replacement = sd.model_copy(update={"variant": v})
        elif isinstance(sd, BentoGridSlide):
            v = _BENTO_GRID_VARIANT_CYCLE[bg_i % len(_BENTO_GRID_VARIANT_CYCLE)]
            bg_i += 1
            replacement = sd.model_copy(update={"variant": v})

        if isinstance(sd, SectionDividerSlide):
            replacement = SectionHeroSlide(
                kind="section_hero",
                part_number=sd.part_label.split()[-1] if sd.part_label else f"{i+1:02d}",
                part_label=sd.part_label,
                title=sd.title,
                subtitle=getattr(sd, "subtitle", None),
                notes=sd.notes,
                transition=sd.transition,
            )

        # Composition rhythm — never repeat back-to-back.
        if getattr(replacement, "composition", None) is None:
            if not rotate and forced_comp:
                # Theme has rotate_compositions=False — every slide gets the
                # theme's composition for a cohesive look.
                try:
                    replacement = replacement.model_copy(update={"composition": forced_comp})
                except Exception:
                    pass
                last_comp = forced_comp
            else:
                comp = _COMPOSITION_ROTATION[comp_i % len(_COMPOSITION_ROTATION)]
                comp_i += 1
                if comp == last_comp:
                    comp = _COMPOSITION_ROTATION[comp_i % len(_COMPOSITION_ROTATION)]
                    comp_i += 1
                try:
                    replacement = replacement.model_copy(update={"composition": comp})
                except Exception:
                    pass
                last_comp = comp
        else:
            last_comp = getattr(replacement, "composition", None)

        new_slides.append(replacement)

    return deck.model_copy(update={"slides": new_slides})


__all__ = ["apply_rhythm"]
