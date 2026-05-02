"""Round-trip: read an existing pptx and infer a best-effort `Deck` schema.

This is intentionally heuristic — pptx files have unbounded layout freedom, so
we cannot reliably classify every slide. We assign a slide kind based on
shape composition and emit a `numbered_list` fallback when in doubt.

This is useful for re-skinning an existing pptx with a Megadeck theme without
rebuilding from scratch.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

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


def _slide_text_blocks(slide: PptxSlide) -> List[str]:
    blocks: List[str] = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            txt = shape.text_frame.text.strip()
            if txt:
                blocks.append(txt)
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


def _classify_slide(blocks: List[str], idx: int, total: int) -> SlideUnion:
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

    # First slide → cover
    if idx == 0 and len(blocks) <= 4:
        title = blocks[0][:108]
        subtitle = blocks[1][:138] if len(blocks) > 1 else None
        presenter = blocks[2][:78] if len(blocks) > 2 else None
        date = blocks[3][:38] if len(blocks) > 3 else None
        return TitleSlide(
            kind="title", eyebrow="", title=title, subtitle=subtitle,
            presenter=presenter, date=date, notes=notes,
            transition=TransitionKind.FADE,
        )

    title = blocks[0][:108]
    rest = blocks[1:]

    # Hero-statement heuristic: very short title, very few other blocks
    if len(title) <= 40 and len(rest) <= 4:
        return HeroStatementSlide(
            kind="hero_statement",
            eyebrow=f"Slide {idx + 1:02d}",
            statement=title,
            supports=[r[:160] for r in rest][:4],
            notes=notes,
            transition=TransitionKind.FADE,
        )

    # Long bullety text → numbered_list
    bullets = []
    for line in rest[:6]:
        head, tail = _split_head_tail(line)
        bullets.append(BulletItem(head=head[:78], tail=tail[:200]))
    if len(bullets) < 2:
        bullets.extend([BulletItem(head="(detail)", tail="") for _ in range(2 - len(bullets))])
    return NumberedListSlide(
        kind="numbered_list",
        eyebrow=f"Imported slide {idx + 1:02d}",
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
