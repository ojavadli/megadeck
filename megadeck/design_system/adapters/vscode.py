"""Adapter: VSCode theme.json → megadeck Theme.

VSCode's theme.json format is published on the VS Code marketplace (thousands
of themes) and follows a documented JSON schema:
  https://code.visualstudio.com/api/extension-guides/color-theme

A theme.json declares `colors.editor.background`, `colors.editor.foreground`,
`tokenColors[…].settings.foreground`, etc. We map the most common keys:

  editor.background                → bg
  editor.foreground                → title
  editorWidget.background          → surface
  editorLineNumber.foreground      → muted
  editorCursor.foreground          → accent
  textLink.activeForeground        → accent_dk
  panel.border / focusBorder       → hairline

Anyone can do `megadeck pool install-vscode <url-to-theme.json>` and get
a working megadeck theme with colours derived from the VSCode theme.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from megadeck.design_system.themegen import (
    Palette,
    generate_theme,
    is_dark,
)


def _coerce_hex(value: Any) -> Optional[str]:
    """Force a value into #RRGGBB. VSCode often uses 8-char hex (with alpha)."""
    if not isinstance(value, str):
        return None
    s = value.lstrip("#")
    if len(s) >= 6 and all(c in "0123456789abcdefABCDEF" for c in s[:6]):
        return f"#{s[:6].upper()}"
    return None


def vscode_theme_to_megadeck(
    vscode_json: Dict[str, Any],
    *,
    fallback_name: str = "vscode-import",
) -> Dict[str, Any]:
    """Convert a parsed VSCode theme JSON into a megadeck theme dict.

    `vscode_json` is the loaded JSON object. Missing keys are tolerated —
    everything has sensible defaults. The result is a megadeck-compatible
    theme dict ready for `theme_from_dict()`.
    """
    colors = vscode_json.get("colors", {}) or {}
    name = vscode_json.get("name") or fallback_name

    bg = _coerce_hex(colors.get("editor.background")) or "#FFFFFF"
    title = _coerce_hex(colors.get("editor.foreground")) or "#0A0A0A"
    surface = _coerce_hex(colors.get("editorWidget.background")) or bg
    muted = _coerce_hex(colors.get("editorLineNumber.foreground")) or "#6B7280"
    accent = (
        _coerce_hex(colors.get("editorCursor.foreground"))
        or _coerce_hex(colors.get("textLink.activeForeground"))
        or _coerce_hex(colors.get("activityBarBadge.background"))
        or _coerce_hex(colors.get("button.background"))
        or "#3B82F6"
    )
    accent_dk = (
        _coerce_hex(colors.get("button.hoverBackground"))
        or _coerce_hex(colors.get("textLink.foreground"))
        or accent
    )
    hairline = _coerce_hex(colors.get("panel.border")) or _coerce_hex(colors.get("focusBorder")) or "#E5E7EB"

    pal = Palette(name=name, accent=accent, accent_dk=accent_dk)
    out = generate_theme(
        pal,
        visual_style="shadow",
        mode="dark" if is_dark(bg) else "light",
        name=_normalise_name(name),
        description=f"Imported from VSCode theme {name!r}.",
    )
    # Override generated colours with the imported ones where present.
    out.update({
        "bg": bg,
        "title": title,
        "surface": surface,
        "muted": muted,
        "accent": accent,
        "accent_dk": accent_dk,
        "hairline": hairline,
    })
    return out


def import_vscode_theme(path: str | Path) -> Dict[str, Any]:
    """Load a VSCode theme.json from disk and convert it."""
    p = Path(path)
    return vscode_theme_to_megadeck(json.loads(p.read_text(encoding="utf-8")))


def _normalise_name(name: str) -> str:
    """Make a VSCode theme name URL/file-safe and prefix it."""
    safe = "".join(
        c.lower() if c.isalnum() else "-"
        for c in name
    ).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return f"vscode-{safe}"


__all__ = ["vscode_theme_to_megadeck", "import_vscode_theme"]
