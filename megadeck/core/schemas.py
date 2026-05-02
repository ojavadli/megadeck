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


class AgendaItem(BaseModel):
    number: str = Field(..., max_length=4, description="Item number, e.g. '01'.")
    title: str = Field(..., max_length=60)
    description: str = Field("", max_length=140)


class TimelineEvent(BaseModel):
    label: str = Field(..., max_length=20, description="Date / phase, e.g. 'Q1 2026'.")
    title: str = Field(..., max_length=50)
    description: str = Field("", max_length=140)


class TableRow(BaseModel):
    cells: List[str] = Field(..., min_length=2, max_length=6)


class KpiTile(BaseModel):
    label: str = Field(..., max_length=30, description="KPI name, e.g. 'MRR'.")
    value: str = Field(..., max_length=14, description="Big number, e.g. '$24K'.")
    delta: str = Field("", max_length=20, description="Change indicator, e.g. '+12% MoM'.")
    delta_positive: bool = Field(True, description="Color delta green (True) or red (False).")


class StepNode(BaseModel):
    title: str = Field(..., max_length=40)
    description: str = Field("", max_length=120)


class ChartSeries(BaseModel):
    name: str = Field(..., max_length=30)
    values: List[float] = Field(..., min_length=1, max_length=24)


class TeamMember(BaseModel):
    name: str = Field(..., max_length=40)
    role: str = Field(..., max_length=60)
    bio: str = Field("", max_length=120)


class PricingTier(BaseModel):
    name: str = Field(..., max_length=30)
    price: str = Field(..., max_length=20, description="e.g. '$49 / mo'.")
    tagline: str = Field("", max_length=60)
    features: List[str] = Field(..., min_length=1, max_length=8)
    is_featured: bool = Field(False, description="Highlight as the recommended tier.")


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


class AgendaSlide(_SlideBase):
    """Numbered agenda — 'today we will cover…' style."""
    kind: Literal["agenda"] = "agenda"
    title: str = Field("Agenda", max_length=40)
    items: List[AgendaItem] = Field(..., min_length=2, max_length=8)


class TimelineSlide(_SlideBase):
    """Horizontal milestone timeline."""
    kind: Literal["timeline"] = "timeline"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    events: List[TimelineEvent] = Field(..., min_length=2, max_length=6)


class ComparisonTableSlide(_SlideBase):
    """Feature-comparison table with header row + data rows."""
    kind: Literal["comparison_table"] = "comparison_table"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    header: List[str] = Field(..., min_length=2, max_length=6)
    rows: List[TableRow] = Field(..., min_length=1, max_length=8)


class PullQuoteSlide(_SlideBase):
    """Large pull quote with attribution — for emphasis."""
    kind: Literal["pull_quote"] = "pull_quote"
    eyebrow: str = Field(..., max_length=40)
    quote: str = Field(..., max_length=260)
    author: str = Field(..., max_length=60)
    role: str = Field("", max_length=60)


class BentoGridSlide(_SlideBase):
    """4 mixed-size cards in a bento layout — perfect for KPIs / features."""
    kind: Literal["bento_grid"] = "bento_grid"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    items: List[CardItem] = Field(..., min_length=4, max_length=4)


class KpiGridSlide(_SlideBase):
    """Up to 4 metric tiles with delta indicators."""
    kind: Literal["kpi_grid"] = "kpi_grid"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    subtitle: Optional[str] = Field(None, max_length=140)
    tiles: List[KpiTile] = Field(..., min_length=2, max_length=4)


class BeforeAfterSlide(_SlideBase):
    """Two-side before/after split with verdict."""
    kind: Literal["before_after"] = "before_after"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    before_label: str = Field("Before", max_length=20)
    before_points: List[str] = Field(..., min_length=2, max_length=5)
    after_label: str = Field("After", max_length=20)
    after_points: List[str] = Field(..., min_length=2, max_length=5)
    verdict: Optional[str] = Field(None, max_length=140)


class StepDiagramSlide(_SlideBase):
    """Sequential 3-5 step flow with arrows."""
    kind: Literal["step_diagram"] = "step_diagram"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    steps: List[StepNode] = Field(..., min_length=3, max_length=5)


class CodeSnippetSlide(_SlideBase):
    """Code block with title and short caption."""
    kind: Literal["code_snippet"] = "code_snippet"
    eyebrow: str = Field(..., max_length=40)
    title: str = Field(..., max_length=110)
    language: str = Field("python", max_length=20)
    code: str = Field(..., max_length=1200, description="The code, verbatim.")
    caption: Optional[str] = Field(None, max_length=160)


class TitleSlide(_SlideBase):
    """Cover slide / opening — title, presenter, date, venue."""
    kind: Literal["title"] = "title"
    eyebrow: str = Field("", max_length=40)
    title: str = Field(..., max_length=110)
    subtitle: Optional[str] = Field(None, max_length=140)
    presenter: Optional[str] = Field(None, max_length=80)
    date: Optional[str] = Field(None, max_length=40)
    venue: Optional[str] = Field(None, max_length=80)


# Discriminated union — the renderer dispatches on `kind`.
Slide = Annotated[
    Union[
        HeroStatementSlide,
        NumberedListSlide,
        ThreeCardSlide,
        TwoColumnSlide,
        SectionDividerSlide,
        AgendaSlide,
        TimelineSlide,
        ComparisonTableSlide,
        PullQuoteSlide,
        BentoGridSlide,
        KpiGridSlide,
        BeforeAfterSlide,
        StepDiagramSlide,
        CodeSnippetSlide,
        TitleSlide,
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
