"""Slide-rhythm orchestrator (variants AND compositions).

A deck reads as composed (not random) when slide selection follows a
*rhythm* — section breaks every N slides, hero moments at predictable
beats, dense lists balanced by manifestos. This module post-processes a
`Deck` to enforce that rhythm.

Three rhythms are layered
-------------------------

1. **Variant rhythm** — each numbered_list slide cycles through the four
   registered variants (default → cards → timeline → split → repeat).
2. **Composition rhythm** — each slide gets a different composition from
   a 10-element rotation. Adjacent slides never share visual language.
3. **Section-divider promotion** — source-side dividers become the
   cinematic `section_hero` kind.

Content is never altered.
"""
from __future__ import annotations

from typing import List, Optional

from megadeck.core.schemas import (
    Deck,
    HeroMinimalSlide,
    NumberedListSlide,
    SectionDividerSlide,
    SectionHeroSlide,
    Slide as SlideUnion,
    ThreeCardSlide,
)


_NUMBERED_LIST_VARIANT_CYCLE: List[Optional[str]] = [
    None,        # default outlined-numerals
    "cards",     # bento-style cards
    "timeline",  # vertical timeline
    "split",     # right-anchored numbers
]


_THREE_CARD_VARIANT_CYCLE: List[Optional[str]] = [
    None,           # default flat 3 cards
    "staggered",    # vertical-stagger asymmetric
    "asymmetric",   # one big card + two small
]


# 10 distinct visual languages, ordered so adjacent slides differ.
_COMPOSITION_ROTATION: List[str] = [
    "typographic", "swiss", "editorial", "blueprint",
    "grid", "brutalist", "photographic", "mono-grid",
    "bauhaus", "risograph",
]


def apply_rhythm(deck: Deck, *, period: int = 6) -> Deck:
    """Return a copy of `deck` with variants AND compositions assigned to
    maximise visual rhythm across the deck.

    `period` is reserved for future use (cycles auto-wrap).
    """
    new_slides: List[SlideUnion] = []
    nl_index = 0
    tc_index = 0
    comp_index = 0
    last_comp: Optional[str] = None

    for i, sd in enumerate(deck.slides):
        replacement: SlideUnion = sd

        if isinstance(sd, NumberedListSlide):
            v = _NUMBERED_LIST_VARIANT_CYCLE[nl_index % len(_NUMBERED_LIST_VARIANT_CYCLE)]
            nl_index += 1
            replacement = sd.model_copy(update={"variant": v})
        elif isinstance(sd, ThreeCardSlide):
            v = _THREE_CARD_VARIANT_CYCLE[tc_index % len(_THREE_CARD_VARIANT_CYCLE)]
            tc_index += 1
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

        # Composition rhythm — pick the next, skip if it equals previous.
        if getattr(replacement, "composition", None) is None:
            comp = _COMPOSITION_ROTATION[comp_index % len(_COMPOSITION_ROTATION)]
            comp_index += 1
            if comp == last_comp:
                comp = _COMPOSITION_ROTATION[comp_index % len(_COMPOSITION_ROTATION)]
                comp_index += 1
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
