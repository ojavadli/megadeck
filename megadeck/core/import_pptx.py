"""Round-trip: read an existing pptx and infer a best-effort `Deck` schema.

This is intentionally heuristic — pptx files have unbounded layout freedom, so
we cannot reliably classify every slide. We assign a slide kind based on
shape composition and emit a `numbered_list` fallback when in doubt.

This is useful for re-skinning an existing pptx with a Megadeck theme without
rebuilding from scratch.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from pptx import Presentation
from pptx.slide import Slide as PptxSlide
from pptx.util import Emu

from megadeck.core.schemas import (
    AgendaItem,
    AgendaSlide,
    BulletItem,
    Deck,
    HeroStatementSlide,
    NumberedListSlide,
    SectionDividerSlide,
    Slide as SlideUnion,
    TitleSlide,
    TransitionKind,
)


def _slide_text_blocks(slide: PptxSlide) -> List[Tuple[str, float, float]]:
    """Return [(text, top_in, font_size_pt), ...] sorted by vertical position.

    Position-aware extraction lets us detect titles (large, near-top) vs body
    (smaller, lower) much more reliably than treating every text frame the same.
    """
    blocks: List[Tuple[str, float, float]] = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        txt = shape.text_frame.text.strip()
        if not txt:
            continue
        top_in = (shape.top or 0) / 914400.0
        # Approximate dominant font size by inspecting first run that has size set
        font_pt = 0.0
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.font.size:
                    font_pt = run.font.size.pt
                    break
            if font_pt:
                break
        blocks.append((txt, top_in, font_pt))
    blocks.sort(key=lambda b: (b[1], -b[2]))
    return blocks


def _split_head_tail(line: str) -> Tuple[str, str]:
    """Split a bullet-style line into (head, tail) on the first '.', '—', or ':' separator."""
    for sep in (".  ", "— ", "- ", ": "):
        if sep in line:
            head, _, tail = line.partition(sep)
            return head.strip(), tail.strip()
    # Otherwise return the whole thing as the head, no tail
    return line.strip()[:78], ""


def _extract_speaker_notes(slide: PptxSlide) -> str:
    if not slide.has_notes_slide:
        return ""
    tf = slide.notes_slide.notes_text_frame
    if tf is None:
        return ""
    return tf.text.strip()


def _classify_slide(
    blocks: List[Tuple[str, float, float]], idx: int, total: int
) -> SlideUnion:
    """Pick a Megadeck slide kind from the raw text on a pptx slide."""
    notes = ""  # caller adds this back

    if not blocks:
        return SectionDividerSlide(
            kind="section_divider",
            part_label=f"Section {idx + 1:02d}",
            title="(empty slide)",
            notes=notes,
            transition=TransitionKind.FADE,
        )

    # Pick the title: prefer the largest font near the top.
    by_size = sorted(blocks, key=lambda b: -b[2])
    title_block = by_size[0] if by_size[0][2] > 0 else blocks[0]
    title = title_block[0][:108]

    # Build the body from everything else, in original (top-down) order.
    body = [b[0] for b in blocks if b[0] != title_block[0]]
    eyebrow_text: Optional[str] = None
    # If there's a tiny eyebrow above the title (small font, near-top), capture it
    above_title = [
        b for b in blocks
        if b[1] < title_block[1] and b[2] and b[2] < title_block[2]
    ]
    if above_title:
        eyebrow_text = above_title[0][0][:38]
        body = [b for b in body if b != above_title[0][0]]

    # First slide → cover
    if idx == 0 and len(body) <= 3:
        subtitle = body[0][:138] if body else None
        presenter = body[1][:78] if len(body) > 1 else None
        date = body[2][:38] if len(body) > 2 else None
        return TitleSlide(
            kind="title", eyebrow=eyebrow_text or "",
            title=title, subtitle=subtitle,
            presenter=presenter, date=date, notes=notes,
            transition=TransitionKind.FADE,
        )

    # Hero-statement heuristic: very short title and few other blocks
    if len(title) <= 50 and len(body) <= 4 and not any(len(b) > 200 for b in body):
        return HeroStatementSlide(
            kind="hero_statement",
            eyebrow=eyebrow_text or f"Slide {idx + 1:02d}",
            statement=title[:78],
            supports=[r[:160] for r in body][:4],
            notes=notes,
            transition=TransitionKind.FADE,
        )

    # Default → numbered_list. Split each body line into head+tail.
    bullets = []
    for line in body[:6]:
        head, tail = _split_head_tail(line)
        bullets.append(BulletItem(head=head[:78], tail=tail[:200]))
    if len(bullets) < 2:
        bullets.extend([BulletItem(head="(detail)", tail="") for _ in range(2 - len(bullets))])
    return NumberedListSlide(
        kind="numbered_list",
        eyebrow=eyebrow_text or f"Slide {idx + 1:02d}",
        title=title,
        items=bullets,
        notes=notes,
        transition=TransitionKind.FADE,
    )


def import_pptx(path: str | Path, theme: str = "default") -> Deck:
    """Read a pptx and return a heuristically-classified Deck.

    Round-trip is best-effort: complex slides (charts, images, tables) are
    coerced into the closest matching template. Re-render the result through
    `render_deck` to get a Megadeck-themed pptx.
    """
    src = Presentation(str(Path(path)))
    slides_out: List[SlideUnion] = []
    for i, src_slide in enumerate(src.slides):
        blocks = _slide_text_blocks(src_slide)
        slide_obj = _classify_slide(blocks, i, len(src.slides))
        notes = _extract_speaker_notes(src_slide)
        if notes:
            slide_obj = slide_obj.model_copy(update={"notes": notes[:6000]})
        slides_out.append(slide_obj)

    return Deck(
        title=Path(path).stem.replace("_", " ").title(),
        theme=theme,
        slides=slides_out,
    )
