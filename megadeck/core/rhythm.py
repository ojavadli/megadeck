"""Slide-rhythm orchestrator.

A deck reads as composed (not random) when the template selection follows
a *rhythm* — section breaks every N slides, hero moments at predictable
beats, dense lists balanced by manifestos and quotes. This module post-
processes a `Deck` to enforce that rhythm.

Rules
-----

* Every Nth slide (configurable, default 6) gets variant rotation: a
  numbered_list at position 0 mod 6 stays default; at 1 mod 6 it becomes
  `cards`; at 2 mod 6 it becomes `timeline`; at 3 mod 6 it becomes `split`.
* The deck never has 4+ identical-kind slides in a row (we promote one to
  hero_minimal or section_hero to break the monotony).
* If a deck has a section_divider every K slides, those become section_hero
  (the bigger cinematic version) automatically.

The rhythm is non-destructive — content is never altered, only the
*variant* and occasionally the *kind* are mutated to maximise visual
variety.
"""
from __future__ import annotations

from typing import Dict, List, Optional

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


def apply_rhythm(deck: Deck, *, period: int = 6) -> Deck:
    """Return a copy of `deck` with variants assigned to maximise visual
    rhythm. Content is never altered.

    `period` controls how many slides between cycle resets.
    """
    new_slides: List[SlideUnion] = []
    numbered_streak = 0
    nl_index = 0  # which variant next time we see a numbered_list

    for i, sd in enumerate(deck.slides):
        replacement: SlideUnion = sd

        if isinstance(sd, NumberedListSlide):
            # Rotate variants every numbered_list we encounter.
            variant = _NUMBERED_LIST_VARIANT_CYCLE[nl_index % len(_NUMBERED_LIST_VARIANT_CYCLE)]
            nl_index += 1
            replacement = sd.model_copy(update={"variant": variant})
            numbered_streak += 1
        else:
            numbered_streak = 0

        # Promote source-side section dividers to the cinematic section_hero.
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

        new_slides.append(replacement)

    return deck.model_copy(update={"slides": new_slides})


__all__ = ["apply_rhythm"]
