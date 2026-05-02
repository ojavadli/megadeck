"""Self-heal loop — render → audit → autofix → re-render until clean.

Strategy
--------
1. Render the deck normally.
2. Run `pptx_audit.audit_pptx()` and group issues per slide.
3. For each slide with issues, mutate the corresponding `Slide` in the deck
   schema using the `_repair_*` helpers below — these shrink the offending
   text, split a too-long bullet, drop a placeholder, etc.
4. Re-render. Iterate up to `max_iters` times or until the audit is empty.

The repair helpers stay in DSL space (i.e. they edit Pydantic models, not
shape XML) so the next render is fully deterministic and benefits from the
auto-fit logic in the templates.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Tuple

from megadeck.core.pptx_audit import AuditIssue, audit_pptx, summarize_audit
from megadeck.core.renderer import render_deck
from megadeck.core.schemas import (
    BulletItem,
    Deck,
    HeroStatementSlide,
    NumberedListSlide,
    Slide as SlideUnion,
)


def _repair_numbered_list(slide: NumberedListSlide, issues: List[AuditIssue]) -> NumberedListSlide:
    """Try to neutralise overflow / overlap on a numbered_list slide.

    Heuristics, in order:
      * if there are too many items, drop the last ones (we keep at least 2).
      * if any bullet has a very long tail, clip it harder.
      * if the title is very long, clip it.
    """
    new = slide.model_copy(deep=True)
    overflow = any(i.issue == "text_likely_overflow" for i in issues)
    overlap = any(i.issue == "shape_overlap" for i in issues)
    if overflow or overlap:
        # Drop trailing items if we have spares.
        while len(new.items) > 4 and (overflow or overlap):
            new.items = new.items[:-1]
            overflow = False  # one pass suffices
        # Trim long tails.
        for it in new.items:
            if len(it.tail or "") > 120:
                it.tail = (it.tail or "")[:118].rsplit(" ", 1)[0] + "…"
        if len(new.title) > 80:
            new.title = new.title[:78].rsplit(" ", 1)[0] + "…"
    return new


def _repair_hero_statement(slide: HeroStatementSlide, issues: List[AuditIssue]) -> HeroStatementSlide:
    """Shorten supports if they overlap."""
    new = slide.model_copy(deep=True)
    if any(i.issue in ("shape_overlap", "text_likely_overflow") for i in issues):
        new.supports = [
            (s if len(s) <= 110 else s[:108].rsplit(" ", 1)[0] + "…")
            for s in (new.supports or [])
        ][:3]
        if len(new.statement) > 70:
            new.statement = new.statement[:68].rsplit(" ", 1)[0] + "…"
    return new


def _repair_slide(slide: SlideUnion, issues: List[AuditIssue]) -> SlideUnion:
    if isinstance(slide, NumberedListSlide):
        return _repair_numbered_list(slide, issues)
    if isinstance(slide, HeroStatementSlide):
        return _repair_hero_statement(slide, issues)
    # Fallback — leave the slide untouched but allow the audit to keep iterating.
    return slide


def render_with_selfheal(
    deck: Deck,
    output_path: str | Path,
    *,
    max_iters: int = 4,
    verbose: bool = False,
) -> Tuple[Path, Dict[str, int]]:
    """Render `deck`, audit, repair, repeat. Return (final_path, summary_after).

    The deck argument is not mutated — we deep-copy so the caller's object
    stays clean. The summary is the audit summary at the final iteration.
    """
    work = deepcopy(deck)
    out = Path(output_path)
    summary: Dict[str, int] = {}
    for it in range(max_iters):
        render_deck(work, out)
        audit = audit_pptx(out)
        summary = summarize_audit(audit)
        errors = summary.get("_errors", 0)
        total = summary.get("_total", 0)
        if verbose:
            print(f"[selfheal] iter={it+1} total={total} errors={errors}")
        if errors == 0 and total <= 1:
            return out, summary
        # Repair only slides with actual issues
        new_slides: List[SlideUnion] = []
        for i, sd in enumerate(work.slides):
            label = f"slide_{i+1:02d}"
            issues = audit.get(label, [])
            if not issues:
                new_slides.append(sd)
            else:
                new_slides.append(_repair_slide(sd, issues))
        work = work.model_copy(update={"slides": new_slides})
    return out, summary
