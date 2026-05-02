"""Tests for the PPTX shape-level audit + self-heal loop."""
from __future__ import annotations

from pathlib import Path

from megadeck import render_deck
from megadeck.core.pptx_audit import audit_pptx, summarize_audit
from megadeck.core.schemas import (
    BulletItem,
    Deck,
    HeroStatementSlide,
    NumberedListSlide,
    TitleSlide,
)
from megadeck.core.selfheal import render_with_selfheal


def _clean_deck() -> Deck:
    return Deck(
        title="Audit Demo",
        slides=[
            TitleSlide(kind="title", title="Audit Test", presenter="QA"),
            NumberedListSlide(
                kind="numbered_list",
                eyebrow="Demo",
                title="Three short items",
                items=[
                    BulletItem(head="One.", tail=""),
                    BulletItem(head="Two.", tail=""),
                    BulletItem(head="Three.", tail=""),
                ],
            ),
            HeroStatementSlide(
                kind="hero_statement",
                eyebrow="Punchline",
                statement="Hello world.",
                supports=["This deck has only short text."],
            ),
        ],
    )


def test_audit_clean_deck_has_no_errors(tmp_path: Path) -> None:
    deck = _clean_deck()
    out = tmp_path / "clean.pptx"
    render_deck(deck, out)
    audit = audit_pptx(out)
    summary = summarize_audit(audit)
    assert summary.get("_errors", 0) == 0


def test_audit_runs_on_real_deck(tmp_path: Path) -> None:
    deck = _clean_deck()
    out = tmp_path / "real.pptx"
    render_deck(deck, out)
    audit = audit_pptx(out)
    # Every slide should appear in the audit
    assert len(audit) == len(deck.slides)


def test_selfheal_loop_returns_clean(tmp_path: Path) -> None:
    deck = _clean_deck()
    out = tmp_path / "healed.pptx"
    final_path, summary = render_with_selfheal(deck, out, max_iters=2)
    assert final_path.exists()
    assert summary.get("_errors", 0) == 0
