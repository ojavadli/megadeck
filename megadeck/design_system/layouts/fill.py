"""Layout-fill renderer: take a Layout + content payload, draw the slide.

Given a Layout (geometry harvested from a real designed slide) and a
piece of megadeck content (a `Slide` from the DSL), we fill the layout's
slots with that content while preserving the original positions.

Strategy
--------
Each layout has shapes with roles. We bucket the layout's shapes by role:

    title        → bind to slide.title or slide.head
    subtitle     → slide.subtitle
    eyebrow      → slide.eyebrow
    body         → joined body / first item.tail
    number       → consecutive integers starting at 1
    accent_bar   → drawn as a coloured rect using theme.accent
    image        → if no image provided, drawn as a tinted card placeholder
    icon         → drawn as a circular badge with first letter of head
    decoration   → drawn as a tinted rect, no text
    unknown      → skipped

If the layout has K number+body slots and the slide has more items than K,
we trim. If fewer items than slots, we render only the populated ones.

This is intentionally not pixel-perfect — it is a layout reuse strategy,
not a full rendering engine. The benefit is that the *composition* of an
ingested human-designed slide carries over to your content.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.slide import Slide as PptxSlide
from pptx.util import Inches, Pt

from megadeck.design_system.layouts.registry import Layout, LayoutShape, get_layout
from megadeck.design_system.primitives import (
    add_round_rect,
    add_text,
    set_slide_bg,
)
from megadeck.design_system.tokens import Theme


# Per-layout dispatch table for custom fills (rarely used; the default fill
# function below handles 95% of cases.)
_LAYOUT_FILLS: Dict[str, Callable] = {}


def register_layout(name: str):
    """Decorator: bind a custom fill function to a specific layout name."""
    def deco(fn: Callable) -> Callable:
        _LAYOUT_FILLS[name] = fn
        return fn
    return deco


def list_layouts() -> List[str]:
    from megadeck.design_system.layouts.registry import all_layouts
    return [l.name for l in all_layouts()]


# ---------------------------------------------------------------------------
# Content extraction from Megadeck DSL
# ---------------------------------------------------------------------------

def _extract_content(slide_data: Any) -> Dict[str, Any]:
    """Pull content from a Megadeck DSL slide into role-keyed fields."""
    out: Dict[str, Any] = {
        "title": getattr(slide_data, "title", None),
        "subtitle": getattr(slide_data, "subtitle", None),
        "eyebrow": getattr(slide_data, "eyebrow", None),
        "body": getattr(slide_data, "body", None),
        "items": [],
    }
    items = getattr(slide_data, "items", None)
    if items:
        for it in items:
            head = getattr(it, "head", None) or getattr(it, "title", None) or str(it)
            tail = getattr(it, "tail", None) or getattr(it, "body", "")
            out["items"].append({"head": head, "tail": tail})
    # Fallbacks
    if not out["title"]:
        out["title"] = getattr(slide_data, "head", None)
    if not out["body"] and out["items"]:
        out["body"] = "  ".join(it["head"] for it in out["items"])
    return out


# ---------------------------------------------------------------------------
# Default fill — works for any layout
# ---------------------------------------------------------------------------

def _safe_color(hex_val: Optional[str], fallback: RGBColor) -> RGBColor:
    if not hex_val:
        return fallback
    try:
        return RGBColor.from_string(hex_val.lstrip("#").upper().ljust(6, "0")[:6])
    except Exception:
        return fallback


def _alignment_to_pp(a: str) -> PP_ALIGN:
    return {
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
    }.get(a, PP_ALIGN.LEFT)


def _draw_layout_shape(
    pptx_slide: PptxSlide,
    layout_shape: LayoutShape,
    *,
    text_override: Optional[str],
    theme: Theme,
) -> None:
    """Render one shape from the layout, with text overridden if provided."""
    role = layout_shape.role
    L, T, W, H = (
        layout_shape.left_in, layout_shape.top_in,
        layout_shape.width_in, layout_shape.height_in,
    )

    if role == "accent_bar":
        add_round_rect(
            pptx_slide,
            left=L, top=T, width=W, height=H,
            fill=theme.accent, adjust=0.05,
        )
        return

    if role == "decoration":
        # Subtle tinted box at low alpha — preserves spatial weight without
        # screaming.
        add_round_rect(
            pptx_slide,
            left=L, top=T, width=W, height=H,
            fill=theme.surface, adjust=0.04,
        )
        return

    if role == "image":
        # Placeholder image card with a soft tint, no actual photo (yet).
        add_round_rect(
            pptx_slide,
            left=L, top=T, width=W, height=H,
            fill=theme.accent_lt, adjust=0.06,
        )
        add_text(
            pptx_slide,
            left=L, top=T, width=W, height=H,
            text="◑",
            font=theme.font_display,
            size_pt=min(120, int(min(W, H) * 36)),
            color=theme.bg,
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
            auto_size=False,
        )
        return

    if role == "icon":
        from megadeck.design_system.primitives import add_oval
        add_oval(
            pptx_slide,
            left=L, top=T,
            size=min(W, H),
            fill=theme.accent,
        )
        # First glyph of overriding text (if any) goes inside.
        glyph = (text_override or "•")[:1].upper()
        add_text(
            pptx_slide,
            left=L, top=T, width=W, height=H,
            text=glyph,
            font=theme.font_display,
            size_pt=int(min(W, H) * 28),
            color=theme.inverse,
            bold=True,
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
            auto_size=False,
        )
        return

    # Text-bearing roles
    text = text_override
    if text is None:
        return  # nothing to render
    size_pt = layout_shape.font_size_pt or {
        "title": 36,
        "subtitle": 22,
        "body": 14,
        "eyebrow": 11,
        "number": 28,
    }.get(role, 14)
    color = {
        "title": theme.title,
        "subtitle": theme.title,
        "body": theme.body,
        "eyebrow": theme.muted,
        "number": theme.accent,
    }.get(role, theme.title)
    bold = layout_shape.font_bold or role in ("title", "number")

    add_text(
        pptx_slide,
        left=L, top=T, width=W, height=H,
        text=str(text)[:600],
        font=theme.font_display if role in ("title", "number") else theme.font_body,
        size_pt=float(size_pt),
        color=color,
        bold=bold,
        italic=layout_shape.font_italic,
        align=_alignment_to_pp(layout_shape.alignment),
        line_spacing=1.15 if role == "title" else 1.30,
        auto_size=False,
    )


def apply_layout(
    pptx_slide: PptxSlide,
    layout_name: str,
    slide_data: Any,
    theme: Theme,
) -> bool:
    """Render `slide_data` onto `pptx_slide` using the named ingested layout.

    Returns True on success, False if the layout is unknown.
    """
    lay = get_layout(layout_name)
    if lay is None:
        return False

    content = _extract_content(slide_data)
    items = content.get("items") or []

    # If a layout-specific fill is registered, use it.
    custom = _LAYOUT_FILLS.get(layout_name)
    if custom is not None:
        custom(pptx_slide, lay, content, theme)
        return True

    set_slide_bg(pptx_slide, color=theme.bg, theme=theme)

    # Counters per role to cycle through items / numbers.
    body_idx = 0
    number_idx = 0

    for sh in sorted(lay.shapes, key=lambda s: s.z):
        text_override: Optional[str] = None
        if sh.role == "title":
            text_override = content.get("title")
        elif sh.role == "subtitle":
            text_override = content.get("subtitle") or (
                items[0]["head"] if items else None
            )
        elif sh.role == "eyebrow":
            text_override = content.get("eyebrow") or ""
        elif sh.role == "body":
            if items and body_idx < len(items):
                head = items[body_idx]["head"] or ""
                tail = items[body_idx]["tail"] or ""
                text_override = (head + " — " + tail) if (head and tail) else (head or tail)
                body_idx += 1
            else:
                text_override = content.get("body")
        elif sh.role == "number":
            number_idx += 1
            text_override = f"{number_idx:02d}"
        elif sh.role == "icon":
            if items and (number_idx < len(items)):
                text_override = items[number_idx]["head"]
                number_idx += 1
        elif sh.role in ("accent_bar", "decoration", "image"):
            pass  # render as design element only, no text
        else:
            continue

        _draw_layout_shape(
            pptx_slide, sh,
            text_override=text_override,
            theme=theme,
        )

    return True


__all__ = ["apply_layout", "list_layouts", "register_layout"]
