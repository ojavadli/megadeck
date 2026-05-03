"""Pluggable theme registry — load themes from JSON files without writing Python.

Why
---
Motion / v0 / 21st.dev all expose a constantly-growing pool of designs. Megadeck
should do the same. Themes live as plain JSON files so any source — a local
folder, a remote registry, an MCP tool, a community pull-request — can feed
megadeck new designs without touching the renderer.

A theme JSON looks like this (every field is optional except `name`)::

    {
      "name": "stripe-classic",
      "description": "Stripe.com landing-page palette — blurple on warm white.",
      "bg":       "#FAFAFB",
      "surface":  "#FFFFFF",
      "title":    "#0A2540",
      "body":     "#425466",
      "accent":   "#635BFF",
      "accent_dk":"#3D2DCC",
      "accent_lt":"#A39EFF",
      "hairline": "#E3E8EE",
      "bg_style": "linear-mesh",
      "bg_aurora_a": "#FAFAFB",
      "bg_aurora_b": "#F1ECFF",
      "bg_aurora_c": "#F0F8FF",
      "card_style": "shadow",
      "accent_glow": false,
      "font_display": "Inter",
      "font_body": "Inter"
    }

The loader fills the rest of the Theme fields with sensible derivations
(e.g. if you don't pass `inverse`, white-on-dark / dark-on-light is computed
from the title color).

Public API
----------
* `load_theme_json(path)`             — parse a single JSON file → `Theme`
* `load_pool_dir(path)`               — load every `*.json` in a directory
* `register_pool_theme(theme)`        — drop a Theme into the global registry
* `register_pool_theme_from_dict(d)`  — same, from a dict
* `list_pool_themes()`                — names of every pool-loaded theme
* `default_pool_dir()`                — bundled `megadeck/design_system/pool/`
* `sync_default_pool()`               — load every JSON in the default dir
                                        (called once at import; idempotent)
"""
from __future__ import annotations

import json
from dataclasses import fields
from pathlib import Path
from typing import Any, Dict, List, Optional

from pptx.dml.color import RGBColor

from megadeck.design_system.tokens import (
    Spacing,
    Theme,
    TypeScale,
    _THEMES,
    _rgb,
    register_theme,
)


# ---------------------------------------------------------------------------
# JSON → Theme
# ---------------------------------------------------------------------------

def _hex_to_rgb(value: Optional[str]) -> Optional[RGBColor]:
    if value is None:
        return None
    return _rgb(value)


def _luma_invert(c: RGBColor) -> RGBColor:
    """If a colour is light, return black-ish; if dark, return white-ish.
    Used to auto-derive `inverse` when the JSON doesn't specify it."""
    s = str(c)
    r, g, b = (int(s[i:i + 2], 16) for i in (0, 2, 4))
    luma = 0.299 * r + 0.587 * g + 0.114 * b
    return _rgb("FFFFFF") if luma < 128 else _rgb("0F172A")


def _smart_default(field_name: str, data: Dict[str, Any], fallback: Any) -> Any:
    """Pull a colour or scalar from JSON, gracefully derive when missing."""
    if field_name in data:
        v = data[field_name]
        if isinstance(v, str) and v.startswith("#"):
            return _rgb(v)
        if isinstance(v, str) and len(v) == 6 and all(c in "0123456789abcdefABCDEF" for c in v):
            return _rgb(v)
        return v
    return fallback


def theme_from_dict(d: Dict[str, Any]) -> Theme:
    """Build a `Theme` from a JSON-shaped dict.

    The dict must contain `name`. All colour fields (bg, surface, title, body,
    accent…) are accepted as `#RRGGBB` strings. Unspecified fields fall back to
    sensible defaults derived from the ones present.
    """
    if "name" not in d:
        raise ValueError("Theme JSON requires a `name` field.")

    bg = _hex_to_rgb(d.get("bg")) or _rgb("FFFFFF")
    title_default = _luma_invert(bg)  # readable on bg
    title = _hex_to_rgb(d.get("title")) or title_default
    inverse = _hex_to_rgb(d.get("inverse")) or _luma_invert(title)
    accent = _hex_to_rgb(d.get("accent")) or _rgb("0EA5E9")
    accent_dk = _hex_to_rgb(d.get("accent_dk")) or accent

    # Smart defaults
    surface = _hex_to_rgb(d.get("surface")) or bg
    overlay = _hex_to_rgb(d.get("overlay")) or surface
    body = _hex_to_rgb(d.get("body")) or title
    muted = _hex_to_rgb(d.get("muted")) or body
    light = _hex_to_rgb(d.get("light")) or muted
    accent_lt = _hex_to_rgb(d.get("accent_lt")) or accent
    accent_bg = _hex_to_rgb(d.get("accent_bg")) or surface
    success = _hex_to_rgb(d.get("success")) or _rgb("16A34A")
    warning = _hex_to_rgb(d.get("warning")) or _rgb("D97706")
    danger = _hex_to_rgb(d.get("danger")) or _rgb("DC2626")
    hairline = _hex_to_rgb(d.get("hairline")) or surface

    type_scale = TypeScale(**d.get("type_scale", {})) if "type_scale" in d else TypeScale()
    spacing = Spacing(**d.get("spacing", {})) if "spacing" in d else Spacing()

    # Decorations: list of dicts. Validate each one through the decoration
    # parser so a typo'd spec is caught at load-time.
    decoration_specs = d.get("decorations") or []
    decorations: List[Dict[str, Any]] = []
    if decoration_specs:
        try:
            from megadeck.design_system.decorations import parse_decoration
        except Exception:
            parse_decoration = None  # type: ignore[assignment]
        for spec in decoration_specs:
            if parse_decoration is not None:
                try:
                    parse_decoration(spec)  # validate; ignore returned model
                except Exception as exc:
                    raise ValueError(f"Invalid decoration on theme {d['name']!r}: {exc}")
            decorations.append(dict(spec))

    return Theme(
        name=d["name"],
        description=d.get("description", ""),
        bg=bg,
        surface=surface,
        overlay=overlay,
        title=title,
        body=body,
        muted=muted,
        light=light,
        inverse=inverse,
        accent=accent,
        accent_dk=accent_dk,
        accent_lt=accent_lt,
        accent_bg=accent_bg,
        success=success,
        warning=warning,
        danger=danger,
        hairline=hairline,
        font_display=d.get("font_display", "SF Pro Display"),
        font_body=d.get("font_body", "SF Pro Display"),
        font_mono=d.get("font_mono", "SF Mono"),
        type_scale=type_scale,
        spacing=spacing,
        slide_width_in=d.get("slide_width_in", 13.33),
        slide_height_in=d.get("slide_height_in", 7.50),
        left_margin_in=d.get("left_margin_in", 1.10),
        right_margin_in=d.get("right_margin_in", 1.10),
        top_margin_in=d.get("top_margin_in", 0.85),
        bottom_margin_in=d.get("bottom_margin_in", 0.70),
        bg_style=d.get("bg_style", "solid"),
        bg_aurora_a=_hex_to_rgb(d.get("bg_aurora_a")),
        bg_aurora_b=_hex_to_rgb(d.get("bg_aurora_b")),
        bg_aurora_c=_hex_to_rgb(d.get("bg_aurora_c")),
        card_style=d.get("card_style", "flat"),
        accent_glow=d.get("accent_glow", False),
        accent_glow_radius_pt=d.get("accent_glow_radius_pt", 22.0),
        accent_glow_alpha_pct=d.get("accent_glow_alpha_pct", 60),
        decorations=tuple(decorations),
        composition=d.get("composition"),
        rotate_compositions=d.get("rotate_compositions", True),
    )


def load_theme_json(path: str | Path) -> Theme:
    p = Path(path)
    return theme_from_dict(json.loads(p.read_text(encoding="utf-8")))


def load_theme_url(url: str, *, timeout: float = 10.0) -> Theme:
    """Download and parse a theme JSON from a URL.

    Supports GitHub raw URLs, gists, and any plain HTTPS endpoint that
    responds with a JSON body matching the Theme schema. Use for letting
    the community / MCP feed designs into the pool at runtime.
    """
    import urllib.request
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        if resp.status != 200:
            raise RuntimeError(f"GET {url} returned {resp.status}")
        body = resp.read().decode("utf-8")
    return theme_from_dict(json.loads(body))


def install_theme_url(url: str, *, pool_dir: Optional[Path] = None) -> Theme:
    """Download a theme.json from `url`, save it under the pool directory,
    and register it. Returns the registered Theme."""
    target_dir = Path(pool_dir) if pool_dir else default_pool_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    theme = load_theme_url(url)
    register_pool_theme(theme)
    target = target_dir / f"{theme.name}.json"
    target.write_text(json.dumps(theme_to_dict(theme), indent=2), encoding="utf-8")
    return theme


def register_pool_theme(theme: Theme) -> None:
    register_theme(theme)


def register_pool_theme_from_dict(d: Dict[str, Any]) -> Theme:
    t = theme_from_dict(d)
    register_pool_theme(t)
    return t


def load_pool_dir(directory: str | Path, *, recursive: bool = True) -> List[Theme]:
    """Load every `*.json` under `directory` as a theme.

    With `recursive=True` (default) we walk subdirectories — this lets us
    organise the pool into `pool/`, `pool/auto/tailwind/`,
    `pool/auto/catppuccin/`, etc. without losing any themes.

    Files with parse errors are reported but don't abort the entire load.
    """
    d = Path(directory)
    if not d.is_dir():
        return []
    loaded: List[Theme] = []
    pattern = "**/*.json" if recursive else "*.json"
    for path in sorted(d.glob(pattern)):
        try:
            theme = load_theme_json(path)
            register_pool_theme(theme)
            loaded.append(theme)
        except Exception as exc:  # noqa: BLE001
            # Don't crash on a single bad file — report and skip.
            print(f"[megadeck.pool] failed to load {path.relative_to(d)}: {exc}")
    return loaded


def list_pool_themes() -> List[str]:
    return sorted(_THEMES.keys())


def default_pool_dir() -> Path:
    return Path(__file__).resolve().parent / "pool"


def sync_default_pool() -> List[Theme]:
    return load_pool_dir(default_pool_dir())


# ---------------------------------------------------------------------------
# Theme → JSON  (round-trippable export)
# ---------------------------------------------------------------------------

def theme_to_dict(theme: Theme) -> Dict[str, Any]:
    """Export a Theme back to a plain JSON-shaped dict. Round-trips via
    `theme_from_dict(theme_to_dict(t))`. Useful for the MCP `pool_export`
    tool and for users wanting to fork a built-in theme."""
    def _hex(c: Optional[RGBColor]) -> Optional[str]:
        return None if c is None else f"#{str(c)}"

    out: Dict[str, Any] = {
        "name": theme.name,
        "description": theme.description,
        "bg": _hex(theme.bg),
        "surface": _hex(theme.surface),
        "overlay": _hex(theme.overlay),
        "title": _hex(theme.title),
        "body": _hex(theme.body),
        "muted": _hex(theme.muted),
        "light": _hex(theme.light),
        "inverse": _hex(theme.inverse),
        "accent": _hex(theme.accent),
        "accent_dk": _hex(theme.accent_dk),
        "accent_lt": _hex(theme.accent_lt),
        "accent_bg": _hex(theme.accent_bg),
        "success": _hex(theme.success),
        "warning": _hex(theme.warning),
        "danger": _hex(theme.danger),
        "hairline": _hex(theme.hairline),
        "font_display": theme.font_display,
        "font_body": theme.font_body,
        "font_mono": theme.font_mono,
        "bg_style": theme.bg_style,
        "bg_aurora_a": _hex(theme.bg_aurora_a),
        "bg_aurora_b": _hex(theme.bg_aurora_b),
        "bg_aurora_c": _hex(theme.bg_aurora_c),
        "card_style": theme.card_style,
        "accent_glow": theme.accent_glow,
        "accent_glow_radius_pt": theme.accent_glow_radius_pt,
        "accent_glow_alpha_pct": theme.accent_glow_alpha_pct,
    }
    if getattr(theme, "decorations", None):
        out["decorations"] = [dict(d) for d in theme.decorations]
    return {k: v for k, v in out.items() if v is not None}
