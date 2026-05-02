"""Schema validation tests."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from megadeck.core.schemas import (
    BulletItem,
    CardItem,
    Deck,
    HeroStatementSlide,
    NumberedListSlide,
    SectionDividerSlide,
    ThreeCardSlide,
    TwoColumnSlide,
    TransitionKind,
)


def test_hero_statement_validates() -> None:
    s = HeroStatementSlide(
        kind="hero_statement",
        eyebrow="Remember",
        statement="Hard is good.",
        supports=["A", "B"],
    )
    assert s.kind == "hero_statement"
    assert s.transition == TransitionKind.FADE


def test_hero_statement_rejects_too_long_statement() -> None:
    with pytest.raises(ValidationError):
        HeroStatementSlide(
            kind="hero_statement",
            eyebrow="x",
            statement="x" * 200,  # exceeds 80
        )


def test_numbered_list_min_max_items() -> None:
    items = [BulletItem(head="One"), BulletItem(head="Two")]
    NumberedListSlide(kind="numbered_list", eyebrow="x", title="t", items=items)
    with pytest.raises(ValidationError):
        NumberedListSlide(
            kind="numbered_list",
            eyebrow="x", title="t",
            items=[BulletItem(head="only one")],  # below min_length=2
        )


def test_three_card_requires_exactly_three() -> None:
    cards = [
        CardItem(badge="01", label="A", description="d"),
        CardItem(badge="02", label="B", description="d"),
        CardItem(badge="03", label="C", description="d"),
    ]
    ThreeCardSlide(kind="three_card", eyebrow="e", title="t", items=cards)
    with pytest.raises(ValidationError):
        ThreeCardSlide(kind="three_card", eyebrow="e", title="t", items=cards[:2])


def test_two_column_validates() -> None:
    items_l = [BulletItem(head="A"), BulletItem(head="B")]
    items_r = [BulletItem(head="X"), BulletItem(head="Y")]
    TwoColumnSlide(
        kind="two_column", eyebrow="e", title="t",
        left_title="L", left_items=items_l,
        right_title="R", right_items=items_r,
    )


def test_section_divider_dark_flag() -> None:
    s = SectionDividerSlide(
        kind="section_divider", part_label="Part 1", title="Intro",
        dark_background=True,
    )
    assert s.dark_background is True


def test_deck_rejects_duplicate_section_labels() -> None:
    with pytest.raises(ValidationError):
        Deck(
            title="t",
            slides=[
                SectionDividerSlide(kind="section_divider", part_label="Part 1", title="A"),
                SectionDividerSlide(kind="section_divider", part_label="part 1", title="B"),
            ],
        )


def test_deck_serialises_round_trip(sample_deck: Deck) -> None:
    payload = sample_deck.model_dump_json()
    restored = Deck.model_validate_json(payload)
    assert len(restored.slides) == len(sample_deck.slides)
