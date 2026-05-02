"""Bulk-generate hundreds of pool themes from the ecosystem adapters.

Run once at build time / on demand from `megadeck pool generate <source>`
to ship a large body of themes derived from open-source palettes:

    Tailwind   22 palettes × 9 styles = 198
    Radix      54 scales (light + dark) × 4 styles = 216
    Catppuccin 4 flavors × 14 accents × 4 styles = 224
    Open Color 13 hues × 4 styles = 52
    --------------------------------------------------
    Total                                          690+

These are emitted as standalone JSON files in
`megadeck/design_system/pool/auto/`. The default pool sync at import time
loads the entire `pool/` tree recursively (handled by `registry.load_pool_dir`
once we adjust it to walk subdirs).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from megadeck.design_system.adapters.catppuccin import generate_catppuccin_themes
from megadeck.design_system.adapters.open_color import generate_open_color_themes
from megadeck.design_system.adapters.radix import generate_radix_themes
from megadeck.design_system.adapters.tailwind import generate_tailwind_themes


SOURCES = {
    "tailwind":   generate_tailwind_themes,
    "catppuccin": generate_catppuccin_themes,
    "radix":      generate_radix_themes,
    "open-color": generate_open_color_themes,
}


def write_themes_to(out_dir: Path, themes: Iterable[dict]) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    for theme in themes:
        name = theme["name"]
        path = out_dir / f"{name}.json"
        path.write_text(json.dumps(theme, indent=2), encoding="utf-8")
        written.append(name)
    return written


def generate_all(target_dir: Path, sources: List[str] | None = None) -> List[str]:
    """Run every selected adapter and write the result under `target_dir`.

    `sources` filters which adapters to run. When None, all are run.
    """
    if sources is None:
        sources = list(SOURCES)
    written: List[str] = []
    for src in sources:
        if src not in SOURCES:
            raise ValueError(f"Unknown source {src!r}. Known: {sorted(SOURCES)}")
        out = target_dir / src
        themes = SOURCES[src]()
        written.extend(write_themes_to(out, themes))
    return written


__all__ = ["SOURCES", "write_themes_to", "generate_all"]
