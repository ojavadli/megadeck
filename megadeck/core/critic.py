"""Visual critic — render every slide to PNG and audit it for overflow,
alignment, and sizing issues. Combines fast rule-based heuristics with a
vision LLM as the second line of defense.
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from PIL import Image
from pydantic import BaseModel, Field

from megadeck.core.preview import render_pptx_to_pngs
from megadeck.core.prompts import CRITIC_SYSTEM_PROMPT
from megadeck.core.schemas import Deck


# ----- Issue model -------------------------------------------------------------

class CriticIssue(BaseModel):
    issue: str = Field(
        ...,
        description=(
            "One of: text_overflow, text_overlap, title_too_large, "
            "title_too_small, empty_block, alignment_break, color_contrast"
        ),
    )
    detail: str = Field(..., max_length=240)
    suggested_fix: str = Field(..., max_length=240)


class SlideAudit(BaseModel):
    slide_index: int
    slide_kind: str
    png_path: str
    issues: List[CriticIssue] = Field(default_factory=list)


class DeckAudit(BaseModel):
    pptx_path: str
    slide_count: int
    slide_audits: List[SlideAudit]

    @property
    def total_issues(self) -> int:
        return sum(len(a.issues) for a in self.slide_audits)


# ----- Heuristic checks --------------------------------------------------------

@dataclass
class _ImgStats:
    width: int
    height: int
    mean_brightness: float
    dark_pixel_ratio: float  # fraction of pixels below 100 / 255 (i.e. real ink)


def _png_stats(path: Path) -> _ImgStats:
    img = Image.open(path).convert("L")
    width, height = img.size
    pixels = list(img.getdata())
    n = max(len(pixels), 1)
    mean = sum(pixels) / n
    dark = sum(1 for p in pixels if p < 100) / n
    return _ImgStats(
        width=width, height=height,
        mean_brightness=mean, dark_pixel_ratio=dark,
    )


def _heuristic_issues(png_path: Path) -> list[CriticIssue]:
    """Cheap rule-based checks before we spend an LLM call.

    A slide is considered empty only if it has BOTH near-white mean brightness
    AND essentially no ink (dark pixels). This avoids flagging legitimate
    minimalist layouts (section dividers, hero statements) where the mean is
    high but the title clearly draws ink.
    """
    issues: list[CriticIssue] = []
    stats = _png_stats(png_path)
    if stats.mean_brightness > 252 and stats.dark_pixel_ratio < 0.001:
        issues.append(
            CriticIssue(
                issue="empty_block",
                detail="Slide appears almost completely blank.",
                suggested_fix="Verify the slide has content.",
            )
        )
    return issues


# ----- LLM critic --------------------------------------------------------------

def _audit_one_with_llm(png_path: Path, slide_kind: str, slide_json: dict) -> List[CriticIssue]:
    """Ask a vision LLM to flag visual issues. Skips silently if no key set."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return []
    try:
        import instructor
        from anthropic import Anthropic
    except ImportError:
        return []

    class _LLMResp(BaseModel):
        issues: List[CriticIssue] = Field(default_factory=list)

    client = instructor.from_anthropic(Anthropic())

    with open(png_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    user_content = [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": b64},
        },
        {
            "type": "text",
            "text": (
                f"Slide kind: {slide_kind}\n"
                f"Slide schema (JSON): {slide_json}\n\n"
                "List any mechanical visual issues. Empty list if the slide is clean."
            ),
        },
    ]

    try:
        resp = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            system=CRITIC_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
            response_model=_LLMResp,
        )
        return resp.issues
    except Exception:
        return []


# ----- Public API --------------------------------------------------------------

def audit_deck(
    pptx_path: str | Path,
    deck: Optional[Deck] = None,
    *,
    use_llm: bool = True,
) -> DeckAudit:
    """Render the deck and return per-slide visual audit results."""
    pptx_path = Path(pptx_path)
    pngs = render_pptx_to_pngs(pptx_path)
    audits: List[SlideAudit] = []
    for i, png in enumerate(pngs):
        issues = _heuristic_issues(png)
        slide_kind = "unknown"
        slide_json: dict = {}
        if deck is not None and i < len(deck.slides):
            slide_kind = deck.slides[i].kind  # type: ignore[union-attr]
            slide_json = deck.slides[i].model_dump()  # type: ignore[union-attr]
        if use_llm and not issues:
            # Only spend an LLM call if heuristics found nothing — this saves cost.
            issues.extend(_audit_one_with_llm(png, slide_kind, slide_json))
        audits.append(
            SlideAudit(
                slide_index=i,
                slide_kind=slide_kind,
                png_path=str(png),
                issues=issues,
            )
        )
    return DeckAudit(
        pptx_path=str(pptx_path),
        slide_count=len(pngs),
        slide_audits=audits,
    )


def audit_dict(audit: DeckAudit) -> dict:
    """Convenience JSON-friendly dict for MCP responses."""
    return audit.model_dump()
