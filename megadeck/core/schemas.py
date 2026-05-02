"""Pydantic DSL — the constrained schema the LLM must produce.

The whole point of this module is that the LLM cannot return malformed output.
`instructor` validates the LLM's response against the `Deck` model below,
retries with the validation error as a hint, and only returns once the
response is type-safe.

The renderer never runs on freeform JSON — it always runs on a validated
`Deck` instance.
"""
from __future__ import annotations

from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator


# ----- Enums -------------------------------------------------------------------

class TransitionKind(str, Enum):
    NONE = "none"
    FADE = "fade"
    PUSH = "push"
    MORPH = "morph"


class EntranceKind(str, Enum):
    NONE = "none"
    FADE_IN = "fade_in"
    SLIDE_FROM_LEFT = "slide_from_left"
    SLIDE_FROM_RIGHT = "slide_from_right"
    SLIDE_FROM_BOTTOM = "slide_from_bottom"
    SCALE_UP = "scale_up"


class Alignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


# ----- Re-usable atoms ---------------------------------------------------------

class BulletItem(BaseModel):
    head: str = Field(..., max_length=80, description="Short bold lead phrase, ≤ 80 chars.")
    tail: str = Field("", max_length=240, description="Optional supporting text, ≤ 240 chars.")


class CardItem(BaseModel):
    badge: str = Field(..., max_length=4, description="Tiny badge, e.g. '01'.")
    label: str = Field(..., max_length=40, description="Card title.")
    description: str = Field(..., max_length=180, description="Card body, ≤ 180 chars.")


# ----- Slide variants ----------------------------------------------------------

class _SlideBase(BaseModel):
    """Common fields for every slide type."""
    notes: str = Field(
        "",
        description="Speaker notes — short, organic sentences for delivery.",
    )
    transition: TransitionKind = TransitionKind.FADE


class HeroStatementSlide(_SlideBase):
    """Massive bold statement — for inflection points like 'Hard is good.'"""
    kind: Literal["hero_statement"] = "hero_statement"
    eyebrow: str = Field(..., max_length=40)
    statement: str = Field(..., max_length=80, description="Hero line, ≤ 80 chars.")
    supports: List[str] = Field(
        default_factory=list,
        description="Up to 4 supporting lines underneath.",
        max_length=4,
    )


class NumberedListSlide(_SlideBase):
    """Up to 6 numbered points with big outlined numbers (01-06)."""
    kind: Literal["numbered_list"] = "numbered_list"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    subtitle: Optional[str] = Field(None, max_length=140)
    items: List[BulletItem] = Field(..., min_length=2, max_length=6)


class ThreeCardSlide(_SlideBase):
    """Three side-by-side cards — for pillars / criteria / phases."""
    kind: Literal["three_card"] = "three_card"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    subtitle: Optional[str] = Field(None, max_length=140)
    items: List[CardItem] = Field(..., min_length=3, max_length=3)


class TwoColumnSlide(_SlideBase):
    """Two-column comparison — left vs right, before vs after."""
    kind: Literal["two_column"] = "two_column"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    subtitle: Optional[str] = Field(None, max_length=140)
    left_title: str = Field(..., max_length=60)
    left_items: List[BulletItem] = Field(..., min_length=2, max_length=5)
    right_title: str = Field(..., max_length=60)
    right_items: List[BulletItem] = Field(..., min_length=2, max_length=5)


class SectionDividerSlide(_SlideBase):
    """Big section break — Part 1, Part 2, Conclusion, etc."""
    kind: Literal["section_divider"] = "section_divider"
    part_label: str = Field(..., max_length=20)
    title: str = Field(..., max_length=80)
    subtitle: Optional[str] = Field(None, max_length=140)
    dark_background: bool = Field(
        default=False,
        description="True for a dramatic dark slide; False for the theme background.",
    )


# Discriminated union — the renderer dispatches on `kind`.
Slide = Annotated[
    Union[
        HeroStatementSlide,
        NumberedListSlide,
        ThreeCardSlide,
        TwoColumnSlide,
        SectionDividerSlide,
    ],
    Field(discriminator="kind"),
]


# ----- Deck (top-level) --------------------------------------------------------

class Deck(BaseModel):
    """A complete presentation — what the LLM is constrained to produce."""
    title: str = Field(..., max_length=120)
    author: Optional[str] = Field(None, max_length=80)
    theme: str = Field("default", description="Theme name, e.g. 'default'/'dark'/'editorial'.")
    slides: List[Slide] = Field(..., min_length=1, max_length=80)

    @model_validator(mode="after")
    def _check_unique_section_labels(self) -> "Deck":
        """Section divider part_labels should be unique within a deck."""
        seen: set[str] = set()
        for s in self.slides:
            if isinstance(s, SectionDividerSlide):
                key = s.part_label.strip().lower()
                if key in seen:
                    raise ValueError(
                        f"Duplicate section divider label: {s.part_label!r}"
                    )
                seen.add(key)
        return self
