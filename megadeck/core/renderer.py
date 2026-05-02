"""Renderer — turns a validated `Deck` schema into a `.pptx` file."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Inches

from megadeck.animations.transitions import apply_transition
from megadeck.core.schemas import (
    Deck,
    HeroStatementSlide,
    NumberedListSlide,
    SectionDividerSlide,
    ThreeCardSlide,
    TwoColumnSlide,
)
from megadeck.design_system.templates import (
    render_hero_statement,
    render_numbered_list,
    render_section_divider,
    render_three_card,
    render_two_column,
)
from megadeck.design_system.tokens import Theme, get_theme


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NSMAP = {"a": A_NS, "p": P_NS}


def _set_speaker_notes(slide, text: str) -> None:
    """Inject speaker notes into a slide; create the placeholder if needed."""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    if tf is not None:
        tf.text = text
        return
    # Fallback path — fabricate the body placeholder
    notes_root = notes_slide.element
    body_sp = None
    for sp in notes_root.findall(".//p:sp", NSMAP):
        ph = sp.find(".//p:ph", NSMAP)
        if ph is not None and (ph.get("type") == "body" or ph.get("idx") == "3"):
            body_sp = sp
            break
    if body_sp is None:
        sp_xml = (
            f'<p:sp xmlns:a="{A_NS}" xmlns:p="{P_NS}">'
            '<p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/>'
            '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="body" sz="quarter" idx="3"/></p:nvPr>'
            "</p:nvSpPr><p:spPr/></p:sp>"
        )
        body_sp = etree.fromstring(sp_xml)
        notes_root.find(".//p:spTree", NSMAP).append(body_sp)
    existing = body_sp.find("p:txBody", NSMAP)
    if existing is not None:
        body_sp.remove(existing)
    tx_body = etree.SubElement(body_sp, "{%s}txBody" % P_NS)
    etree.SubElement(tx_body, "{%s}bodyPr" % A_NS)
    etree.SubElement(tx_body, "{%s}lstStyle" % A_NS)
    for line in text.split("\n"):
        p = etree.SubElement(tx_body, "{%s}p" % A_NS)
        if line:
            r = etree.SubElement(p, "{%s}r" % A_NS)
            r_pr = etree.SubElement(r, "{%s}rPr" % A_NS)
            r_pr.set("lang", "en-US")
            r_pr.set("sz", "1100")
            t = etree.SubElement(r, "{%s}t" % A_NS)
            t.text = line


def _section_label_for(deck: Deck, idx: int) -> Optional[str]:
    """Return the most recent section divider's label (used in the page chrome)."""
    label: Optional[str] = None
    for j, slide in enumerate(deck.slides):
        if j > idx:
            break
        if isinstance(slide, SectionDividerSlide):
            label = f"{slide.part_label.upper()}  ·  {slide.title.upper()}"
    return label


def render_deck(deck: Deck, output_path: str | Path) -> Path:
    """Render a validated `Deck` to a `.pptx` file. Returns the output path."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    theme: Theme = get_theme(deck.theme)

    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Emu(int(theme.slide_width_in * 914400))
    prs.slide_height = Emu(int(theme.slide_height_in * 914400))

    # Use the blank layout for everything — we draw all chrome ourselves.
    blank_layout = prs.slide_layouts[6]

    total = len(deck.slides)
    for idx, sdata in enumerate(deck.slides):
        slide = prs.slides.add_slide(blank_layout)
        page_n = idx + 1
        section_label = _section_label_for(deck, idx)

        if isinstance(sdata, HeroStatementSlide):
            render_hero_statement(
                slide, sdata, theme,
                page_n=page_n, page_total=total,
                section_label=section_label,
            )
        elif isinstance(sdata, NumberedListSlide):
            render_numbered_list(
                slide, sdata, theme,
                page_n=page_n, page_total=total,
                section_label=section_label,
            )
        elif isinstance(sdata, ThreeCardSlide):
            render_three_card(
                slide, sdata, theme,
                page_n=page_n, page_total=total,
                section_label=section_label,
            )
        elif isinstance(sdata, TwoColumnSlide):
            render_two_column(
                slide, sdata, theme,
                page_n=page_n, page_total=total,
                section_label=section_label,
            )
        elif isinstance(sdata, SectionDividerSlide):
            render_section_divider(
                slide, sdata, theme,
                page_n=page_n, page_total=total,
                section_label=section_label,
            )
        else:
            raise NotImplementedError(f"Unknown slide kind: {type(sdata).__name__}")

        # Speaker notes
        if sdata.notes:
            _set_speaker_notes(slide, sdata.notes)

        # Slide transition
        apply_transition(slide.element, sdata.transition)

    prs.save(str(out))
    return out
