"""Critic tests — heuristic checks only (LLM call skipped without API key)."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from megadeck import render_deck
from megadeck.core.critic import audit_deck


_HAS_LIBREOFFICE = shutil.which("soffice") is not None or shutil.which("libreoffice") is not None
_HAS_POPPLER = shutil.which("pdftoppm") is not None


@pytest.mark.skipif(
    not (_HAS_LIBREOFFICE and _HAS_POPPLER),
    reason="LibreOffice + poppler are required for the visual audit pipeline.",
)
def test_audit_runs_without_llm(tmp_path: Path, sample_deck) -> None:
    out = tmp_path / "audit.pptx"
    render_deck(sample_deck, out)
    # Force LLM off to keep the test deterministic and key-free
    report = audit_deck(out, deck=sample_deck, use_llm=False)
    assert report.slide_count == len(sample_deck.slides)
    assert len(report.slide_audits) == len(sample_deck.slides)
    # Heuristics should NOT flag any of the rendered sample slides
    flagged = [a for a in report.slide_audits if a.issues]
    assert flagged == [], f"Unexpected heuristic issues: {flagged}"
