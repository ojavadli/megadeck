"""Low-level shape helpers used by every template.

These wrap the verbose `python-pptx` API into a small, expressive vocabulary
(`add_text`, `add_card`, `add_v_line`, `add_dot_grid`, …) so that template
files stay short and readable.
"""
from __future__ import annotations

import math
from typing import Iterable, Optional, Sequence, Tuple

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide
from pptx.util import Inches, Pt

from megadeck.design_system.tokens import Theme


# ----- Auto-fit / overflow protection -----------------------------------------

def fit_title(text: str, *, max_pt: int, min_pt: int = 18, width_in: float = 11.0) -> int:
    """Pick a font size that lets `text` fit in 1-3 lines at width `width_in`.

    Bias-toward-readable: starts at `max_pt`, shrinks by 2pt steps until the
    estimated rendered height stays within 3 lines.
    """
    for size_pt in range(max_pt, min_pt - 1, -2):
        chars_per_line = max(8, int(width_in * 72.0 / (size_pt * 0.50)))
        n_lines = max(1, math.ceil(len(text) / chars_per_line))
        if n_lines <= 3:
            return size_pt
    return min_pt


def measure_title_height(text: str, *, size_pt: int, width_in: float, line_spacing: float = 1.05) -> float:
    """Estimate rendered height in inches for a title at given pt + width.

    Used to compute where the body should start so it never collides with a
    multi-line title. We err on the side of slightly over-allocating space.
    """
    chars_per_line = max(8, int(width_in * 72.0 / (size_pt * 0.50)))
    explicit_lines = sum(1 for c in text if c == "\n") + 1
    wrapped_lines = max(1, math.ceil(len(text) / chars_per_line))
    n_lines = max(explicit_lines, wrapped_lines)
    line_height_in = (size_pt * line_spacing) / 72.0
    return n_lines * line_height_in + 0.10  # small breathing room


# ----- Background --------------------------------------------------------------

def set_slide_bg(slide: Slide, color: RGBColor) -> None:
    bg = slide.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = color


# ----- Text --------------------------------------------------------------------

def _set_run(
    run,
    *,
    name: Optional[str] = None,
    size_pt: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    color: Optional[RGBColor] = None,
) -> None:
    if name is not None:
        run.font.name = name
    if size_pt is not None:
        run.font.size = Pt(size_pt)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_text(
    slide: Slide,
    *,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    font: str,
    size_pt: int,
    color: RGBColor,
    bold: bool = False,
    italic: bool = False,
    align: Optional[PP_ALIGN] = None,
    anchor: Optional[MSO_ANCHOR] = None,
    line_spacing: Optional[float] = None,
):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    if anchor is not None:
        try:
            tf.vertical_anchor = anchor
        except Exception:
            pass
    p = tf.paragraphs[0]
    if align is not None:
        p.alignment = align
    if line_spacing is not None:
        try:
            p.line_spacing = line_spacing
        except Exception:
            pass
    r = p.add_run()
    r.text = text
    _set_run(r, name=font, size_pt=size_pt, bold=bold, italic=italic, color=color)
    return tb


def add_rich_text(
    slide: Slide,
    *,
    left: float,
    top: float,
    width: float,
    height: float,
    runs: Sequence[Tuple[str, dict]],
    font: str,
    line_spacing: Optional[float] = None,
    align: Optional[PP_ALIGN] = None,
    anchor: Optional[MSO_ANCHOR] = None,
):
    """Compose multiple styled runs in one paragraph."""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    if anchor is not None:
        try:
            tf.vertical_anchor = anchor
        except Exception:
            pass
    p = tf.paragraphs[0]
    if align is not None:
        p.alignment = align
    if line_spacing is not None:
        try:
            p.line_spacing = line_spacing
        except Exception:
            pass
    for text, opts in runs:
        r = p.add_run()
        r.text = text
        _set_run(
            r,
            name=opts.get("font", font),
            size_pt=opts.get("size_pt"),
            bold=opts.get("bold"),
            italic=opts.get("italic"),
            color=opts.get("color"),
        )
    return tb


# ----- Shapes ------------------------------------------------------------------

def add_rect(
    slide: Slide,
    *,
    left: float,
    top: float,
    width: float,
    height: float,
    fill: Optional[RGBColor] = None,
    line: Optional[RGBColor] = None,
    line_w: Optional[float] = None,
):
    rect = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    if fill is None:
        rect.fill.background()
    else:
        rect.fill.solid()
        rect.fill.fore_color.rgb = fill
    if line is None:
        rect.line.fill.background()
    else:
        rect.line.color.rgb = line
        if line_w is not None:
            rect.line.width = Pt(line_w)
    return rect


def add_round_rect(
    slide: Slide,
    *,
    left: float,
    top: float,
    width: float,
    height: float,
    fill: Optional[RGBColor] = None,
    line: Optional[RGBColor] = None,
    line_w: Optional[float] = None,
    adjust: float = 0.05,
):
    rect = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(left), Inches(top), Inches(width), Inches(height),
    )
    rect.adjustments[0] = adjust
    if fill is None:
        rect.fill.background()
    else:
        rect.fill.solid()
        rect.fill.fore_color.rgb = fill
    if line is None:
        rect.line.fill.background()
    else:
        rect.line.color.rgb = line
        if line_w is not None:
            rect.line.width = Pt(line_w)
    return rect


def add_oval(
    slide: Slide,
    *,
    left: float,
    top: float,
    size: float,
    fill: RGBColor,
    line: Optional[RGBColor] = None,
):
    c = slide.shapes.add_shape(
        MSO_SHAPE.OVAL, Inches(left), Inches(top), Inches(size), Inches(size),
    )
    c.fill.solid()
    c.fill.fore_color.rgb = fill
    if line is None:
        c.line.fill.background()
    else:
        c.line.color.rgb = line
    return c


def add_v_line(
    slide: Slide,
    *,
    left: float,
    top: float,
    height: float,
    color: RGBColor,
    width: float = 0.04,
):
    return add_rect(
        slide,
        left=left, top=top, width=width, height=height,
        fill=color,
    )


def add_h_line(
    slide: Slide,
    *,
    left: float,
    top: float,
    width: float,
    color: RGBColor,
    height: float = 0.012,
):
    return add_rect(
        slide,
        left=left, top=top, width=width, height=height,
        fill=color,
    )


def add_dot_grid(
    slide: Slide,
    *,
    left: float,
    top: float,
    cols: int = 8,
    rows: int = 3,
    gap: float = 0.13,
    size: float = 0.03,
    color: RGBColor,
) -> None:
    """Draw a tiny dot grid — decorative anchor in a slide corner."""
    for r in range(rows):
        for c in range(cols):
            add_oval(
                slide,
                left=left + c * gap,
                top=top + r * gap,
                size=size,
                fill=color,
            )


# ----- Composite chrome (used by every template) ------------------------------

def add_eyebrow(
    slide: Slide,
    *,
    text: str,
    theme: Theme,
    left: Optional[float] = None,
    top: float = 0.85,
):
    """Standard eyebrow row: thin vertical accent + small uppercase label."""
    x = theme.left_margin_in if left is None else left
    add_v_line(
        slide,
        left=x - 0.10, top=top,
        height=0.30,
        color=theme.accent,
    )
    add_text(
        slide,
        left=x, top=top, width=11.0, height=0.30,
        text=text,
        font=theme.font_body,
        size_pt=theme.type_scale.eyebrow,
        color=theme.muted,
        bold=True,
    )


def add_corner_dotgrid(slide: Slide, theme: Theme) -> None:
    """Tiny decorative dot grid in the top-right corner."""
    add_dot_grid(
        slide,
        left=theme.slide_width_in - 1.95, top=0.35,
        cols=8, rows=3, gap=0.13, size=0.03,
        color=theme.accent_lt,
    )


def add_page_chrome(
    slide: Slide,
    *,
    theme: Theme,
    page_n: int,
    page_total: int,
    section_label: Optional[str] = None,
    on_dark: bool = False,
) -> None:
    """Bottom-of-slide chrome: hairline + section label + page counter."""
    line_color = theme.hairline if not on_dark else theme.overlay
    text_color = theme.light if not on_dark else theme.muted
    add_h_line(
        slide,
        left=theme.left_margin_in, top=7.10,
        width=theme.content_width_in,
        color=line_color,
        height=0.012,
    )
    if section_label:
        add_text(
            slide,
            left=theme.left_margin_in, top=7.18, width=6.0, height=0.30,
            text=section_label,
            font=theme.font_body,
            size_pt=theme.type_scale.eyebrow - 1,
            color=text_color,
            bold=True,
            align=PP_ALIGN.LEFT,
        )
    add_text(
        slide,
        left=theme.slide_width_in - theme.right_margin_in - 1.20,
        top=7.18, width=1.20, height=0.30,
        text=f"{page_n:02d} / {page_total:02d}",
        font=theme.font_body,
        size_pt=theme.type_scale.eyebrow - 1,
        color=text_color,
        align=PP_ALIGN.RIGHT,
    )
