"""Shared pytest fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Make examples/ importable so tests can reuse the sample-deck fixture
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

from build_sample_deck import build_sample_deck  # noqa: E402


@pytest.fixture
def sample_deck():
    return build_sample_deck()
