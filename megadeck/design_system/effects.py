"""Low-level DrawingML XML helpers for fills + effects.

`python-pptx` exposes a clean API for solid fills, shapes, and basic styling,
but the moments where Megadeck needs to feel premium (gradients, soft drop
shadows, glows, glass cards) require dropping down to raw OOXML. This module
contains all of that XML so templates stay readable.
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Tuple

from lxml import etree
from pptx.dml.color import RGBColor
from pptx.oxml.ns import nsmap, qn
from pptx.shapes.base import BaseShape


# `python-pptx` registers its namespaces under shorter aliases. Using the same
# `qn()` helper means we generate XML that's bit-for-bit equivalent to what the
# library produces internally.
_A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hex(color: RGBColor | str) -> str:
    """Return an upper-case hex string for either an RGBColor or a hex string."""
    if isinstance(color, RGBColor):
        return str(color)  # RGBColor stringifies to 6-char hex
    s = str(color).lstrip("#")
    if len(s) != 6:
        raise ValueError(f"Expected 6-char hex, got {color!r}")
    return s.upper()


def _ensure_sppr(shape: BaseShape):
    sppr = shape._element.find(qn("p:spPr"))
    if sppr is None:
        sppr = shape._element.find(qn("a:spPr"))
    if sppr is None:
        raise ValueError(f"shape '{shape.name}' has no spPr element")
    return sppr


def _remove_children(parent, tags: Iterable[str]) -> None:
    for tag in tags:
        for el in parent.findall(qn(tag)):
            parent.remove(el)


def _strip_theme_style(shape: BaseShape) -> None:
    """Remove `<p:style>` from the shape so theme `fillRef` / `lnRef` /
    `effectRef` references can't override the explicit `spPr` fill we set.

    `python-pptx` adds a default `<p:style>` block to every newly-created shape
    that points at the theme's accent fills. When the shape is on a layout
    that doesn't have a matching theme (which is *every* megadeck slide since
    we drive everything from spPr directly), LibreOffice / PowerPoint render
    the theme accent instead of our gradient. Stripping the style block makes
    the spPr direct fill authoritative.
    """
    el = shape._element
    style = el.find(qn("p:style"))
    if style is not None:
        el.remove(style)


# ---------------------------------------------------------------------------
# Gradient fills
# ---------------------------------------------------------------------------

def _gs(pos_pct: int, hex6: str, alpha_pct: int = 100) -> etree._Element:
    """Build a single gradient stop element."""
    gs = etree.SubElement(etree.Element(qn("a:gsLst")), qn("a:gs"), pos=str(pos_pct * 1000))
    srgb = etree.SubElement(gs, qn("a:srgbClr"), val=hex6)
    if alpha_pct != 100:
        etree.SubElement(srgb, qn("a:alpha"), val=str(int(alpha_pct * 1000)))
    return gs


def apply_linear_gradient(
    shape: BaseShape,
    *,
    stops: List[Tuple[int, RGBColor | str, int]],
    angle_deg: float = 90.0,
) -> None:
    """Replace `shape`'s fill with a linear gradient.

    `stops` is a list of `(position_percent, color, alpha_percent)` triples.
    `angle_deg` follows DrawingML convention (0 = left→right, 90 = top→bottom).
    """
    _strip_theme_style(shape)
    sppr = _ensure_sppr(shape)
    _remove_children(sppr, ["a:noFill", "a:solidFill", "a:gradFill", "a:pattFill", "a:blipFill"])
    grad = etree.SubElement(sppr, qn("a:gradFill"), {"flip": "none", "rotWithShape": "1"})
    gs_lst = etree.SubElement(grad, qn("a:gsLst"))
    for pos, color, alpha in stops:
        gs = etree.SubElement(gs_lst, qn("a:gs"), pos=str(int(pos * 1000)))
        srgb = etree.SubElement(gs, qn("a:srgbClr"), val=_hex(color))
        if alpha != 100:
            etree.SubElement(srgb, qn("a:alpha"), val=str(int(alpha * 1000)))
    ang_60k = int(angle_deg * 60000) % (360 * 60000)
    etree.SubElement(grad, qn("a:lin"), ang=str(ang_60k), scaled="1")


def apply_radial_gradient(
    shape: BaseShape,
    *,
    inner_color: RGBColor | str,
    outer_color: RGBColor | str,
    inner_alpha: int = 100,
    outer_alpha: int = 100,
    focus_x: int = 50,
    focus_y: int = 50,
) -> None:
    """Replace `shape`'s fill with a radial gradient (used for hero glows)."""
    _strip_theme_style(shape)
    sppr = _ensure_sppr(shape)
    _remove_children(sppr, ["a:noFill", "a:solidFill", "a:gradFill", "a:pattFill", "a:blipFill"])
    grad = etree.SubElement(sppr, qn("a:gradFill"), {"flip": "none", "rotWithShape": "1"})
    gs_lst = etree.SubElement(grad, qn("a:gsLst"))
    gs1 = etree.SubElement(gs_lst, qn("a:gs"), pos="0")
    s1 = etree.SubElement(gs1, qn("a:srgbClr"), val=_hex(inner_color))
    if inner_alpha != 100:
        etree.SubElement(s1, qn("a:alpha"), val=str(int(inner_alpha * 1000)))
    gs2 = etree.SubElement(gs_lst, qn("a:gs"), pos="100000")
    s2 = etree.SubElement(gs2, qn("a:srgbClr"), val=_hex(outer_color))
    if outer_alpha != 100:
        etree.SubElement(s2, qn("a:alpha"), val=str(int(outer_alpha * 1000)))
    path = etree.SubElement(grad, qn("a:path"), path="circle")
    rect = etree.SubElement(path, qn("a:fillToRect"))
    rect.set("l", str(focus_x * 1000))
    rect.set("t", str(focus_y * 1000))
    rect.set("r", str(focus_x * 1000))
    rect.set("b", str(focus_y * 1000))


def apply_solid_fill(shape: BaseShape, color: RGBColor | str, alpha: int = 100) -> None:
    """Solid fill with optional alpha. Equivalent to shape.fill.solid() but
    handles the alpha case which python-pptx doesn't expose directly."""
    _strip_theme_style(shape)
    sppr = _ensure_sppr(shape)
    _remove_children(sppr, ["a:noFill", "a:solidFill", "a:gradFill", "a:pattFill", "a:blipFill"])
    sf = etree.SubElement(sppr, qn("a:solidFill"))
    srgb = etree.SubElement(sf, qn("a:srgbClr"), val=_hex(color))
    if alpha != 100:
        etree.SubElement(srgb, qn("a:alpha"), val=str(int(alpha * 1000)))


# ---------------------------------------------------------------------------
# Effect list — shadows + glow
# ---------------------------------------------------------------------------

def _ensure_effectlst(shape: BaseShape) -> etree._Element:
    sppr = _ensure_sppr(shape)
    eff = sppr.find(qn("a:effectLst"))
    if eff is None:
        eff = etree.SubElement(sppr, qn("a:effectLst"))
    else:
        # Clear existing effects so we don't stack accidentally.
        for child in list(eff):
            eff.remove(child)
    return eff


def apply_drop_shadow(
    shape: BaseShape,
    *,
    color: RGBColor | str = "000000",
    alpha_pct: int = 35,
    blur_pt: float = 12.0,
    distance_pt: float = 4.0,
    direction_deg: float = 90.0,
) -> None:
    """Soft drop shadow under `shape`. Default values match a Linear/Stripe
    'card' aesthetic — gentle, low-contrast, blurred."""
    eff = _ensure_effectlst(shape)
    shdw = etree.SubElement(
        eff, qn("a:outerShdw"),
        blurRad=str(int(blur_pt * 12700)),
        dist=str(int(distance_pt * 12700)),
        dir=str(int(direction_deg * 60000) % (360 * 60000)),
        algn="ctr",
        rotWithShape="0",
    )
    srgb = etree.SubElement(shdw, qn("a:srgbClr"), val=_hex(color))
    etree.SubElement(srgb, qn("a:alpha"), val=str(int(alpha_pct * 1000)))


def apply_glow(
    shape: BaseShape,
    *,
    color: RGBColor | str,
    radius_pt: float = 14.0,
    alpha_pct: int = 60,
) -> None:
    """Soft outer glow — used for accent numerals on dark themes."""
    eff = _ensure_effectlst(shape)
    glow = etree.SubElement(eff, qn("a:glow"), rad=str(int(radius_pt * 12700)))
    srgb = etree.SubElement(glow, qn("a:srgbClr"), val=_hex(color))
    etree.SubElement(srgb, qn("a:alpha"), val=str(int(alpha_pct * 1000)))


def apply_soft_edge(shape: BaseShape, *, radius_pt: float = 4.0) -> None:
    """Feather the shape's edge — used to make orbs/blurs blend."""
    eff = _ensure_effectlst(shape)
    etree.SubElement(eff, qn("a:softEdge"), rad=str(int(radius_pt * 12700)))


# ---------------------------------------------------------------------------
# Higher-level "card" treatments
# ---------------------------------------------------------------------------

def style_card(
    shape: BaseShape,
    *,
    fill: RGBColor | str,
    fill_alpha: int = 100,
    border: Optional[RGBColor | str] = None,
    border_w_pt: float = 0.5,
    shadow: bool = True,
    shadow_alpha: int = 30,
    shadow_blur_pt: float = 18.0,
) -> None:
    """Apply a Linear/Stripe-style 'card' look in one call: solid (or alpha)
    fill + optional hairline border + soft drop shadow."""
    apply_solid_fill(shape, fill, alpha=fill_alpha)
    if border is not None:
        from pptx.util import Pt as _Pt
        shape.line.color.rgb = (
            border if isinstance(border, RGBColor) else RGBColor.from_string(_hex(border))
        )
        shape.line.width = _Pt(border_w_pt)
    if shadow:
        apply_drop_shadow(
            shape,
            color="000000",
            alpha_pct=shadow_alpha,
            blur_pt=shadow_blur_pt,
            distance_pt=3.0,
        )


def glass_card(
    shape: BaseShape,
    *,
    tint: RGBColor | str,
    border: Optional[RGBColor | str] = None,
    fill_alpha: int = 22,
) -> None:
    """Frosted-glass look: low-alpha tinted fill + faint hairline + tiny shadow.

    Real frosted glass needs a backdrop blur which OOXML can't render, but the
    alpha-stacked aesthetic is convincing on solid or gradient backgrounds.
    """
    apply_solid_fill(shape, tint, alpha=fill_alpha)
    if border is not None:
        from pptx.util import Pt as _Pt
        shape.line.color.rgb = (
            border if isinstance(border, RGBColor) else RGBColor.from_string(_hex(border))
        )
        shape.line.width = _Pt(0.25)
    apply_drop_shadow(
        shape, color="000000", alpha_pct=22, blur_pt=24, distance_pt=2,
    )


def aurora_background(
    shape: BaseShape,
    *,
    a: RGBColor | str,
    b: RGBColor | str,
    c: RGBColor | str,
) -> None:
    """3-stop diagonal gradient that reads as 'aurora' — used for hero / cover
    slide backgrounds. `a → b → c` from top-left to bottom-right."""
    apply_linear_gradient(
        shape,
        stops=[(0, a, 100), (50, b, 100), (100, c, 100)],
        angle_deg=135.0,
    )
