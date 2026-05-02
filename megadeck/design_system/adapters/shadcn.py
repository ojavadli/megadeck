"""Adapter: shadcn/ui registry & 21st.dev component spec → megadeck Theme.

Both projects use a JSON registry format (https://ui.shadcn.com/registry,
https://21st.dev/api/registry) to publish design tokens. The relevant
shape — present in every component's `cssVars` field — looks like:

    {
      "cssVars": {
        "light": {
          "background": "0 0% 100%",          // HSL "h s% l%"
          "foreground": "240 10% 3.9%",
          "primary": "240 5.9% 10%",
          "muted": "240 4.8% 95.9%",
          "accent": "240 4.8% 95.9%",
          "border": "240 5.9% 90%",
        },
        "dark": { … }
      }
    }

We parse those HSL triplets, build a Palette from `primary`, and call
`generate_theme()` with the `bg` / `title` / `muted` / `border` overrides
applied so an imported shadcn theme reads visually identically to the
component it was extracted from.
"""
from __future__ import annotations

import colorsys
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from megadeck.design_system.themegen import Palette, generate_theme, is_dark


_HSL_RE = re.compile(r"^\s*([\d.]+)\s+([\d.]+)%\s+([\d.]+)%\s*$")


def _hsl_to_hex(value: str) -> Optional[str]:
    """Parse an HSL string like '240 5.9% 10%' into '#RRGGBB'."""
    m = _HSL_RE.match(value)
    if not m:
        return None
    h, s, l = float(m.group(1)), float(m.group(2)), float(m.group(3))
    rr, gg, bb = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
    return f"#{int(rr*255):02X}{int(gg*255):02X}{int(bb*255):02X}"


def shadcn_to_megadeck(
    spec: Dict[str, Any],
    *,
    name: Optional[str] = None,
    mode: str = "light",
) -> Dict[str, Any]:
    """Convert a shadcn-style cssVars dict to a megadeck theme.

    `spec` should be either the full registry component (with `cssVars`)
    or directly the `cssVars[mode]` mapping.
    """
    if "cssVars" in spec:
        css_vars = spec["cssVars"].get(mode, {}) or spec["cssVars"].get("light", {})
        if not name and spec.get("name"):
            name = spec["name"]
    else:
        css_vars = spec

    bg = _hsl_to_hex(css_vars.get("background", "")) or "#FFFFFF"
    fg = _hsl_to_hex(css_vars.get("foreground", "")) or "#000000"
    primary = _hsl_to_hex(css_vars.get("primary", "")) or fg
    muted_bg = _hsl_to_hex(css_vars.get("muted", "")) or bg
    accent_lt = _hsl_to_hex(css_vars.get("accent", "")) or primary
    border = _hsl_to_hex(css_vars.get("border", "")) or "#E5E7EB"

    pal = Palette(name=f"shadcn-{name}" if name else "shadcn-import", accent=primary)
    theme = generate_theme(
        pal,
        visual_style="shadow",
        mode="dark" if is_dark(bg) else "light",
        name=_normalise_name(name or "shadcn-import"),
        description=f"shadcn / 21st.dev import: {name!r} ({mode} mode).",
    )
    theme.update({
        "bg": bg,
        "title": fg,
        "surface": muted_bg,
        "accent": primary,
        "accent_lt": accent_lt,
        "hairline": border,
    })
    return theme


def import_shadcn_registry(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    return shadcn_to_megadeck(json.loads(p.read_text(encoding="utf-8")))


def _normalise_name(name: str) -> str:
    safe = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return f"shadcn-{safe}"


__all__ = ["shadcn_to_megadeck", "import_shadcn_registry"]
