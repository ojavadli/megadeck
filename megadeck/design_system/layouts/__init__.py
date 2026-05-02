"""Real-world layouts ingested from .pptx / .key files.

Unlike templates (Python functions in `templates/`), layouts are *data* —
JSON files describing the geometry, hierarchy, and text styling of slides
that human designers actually authored.

The ingestion pipeline (`ingest.py`) walks a folder of pptx files and for
each slide emits one layout JSON containing:

* shape bboxes (left/top/width/height in inches)
* shape role (title / subtitle / body / number / accent_bar / image / icon)
* text styling (font / size / weight / colour / alignment)
* z-order

The fill renderer (`fill.py`) takes a layout + content tuple and draws
the slide using those exact positions, so the output looks like the
ingested deck *did*, just with your content.

The library auto-loads every JSON in `megadeck/design_system/layouts/lib/`
at import time. Add new pptx files via `megadeck layouts ingest <path>`.
"""
from __future__ import annotations

from megadeck.design_system.layouts.fill import (
    apply_layout,
    list_layouts,
    register_layout,
)
from megadeck.design_system.layouts.ingest import ingest_pptx, ingest_folder
from megadeck.design_system.layouts.registry import (
    Layout,
    LayoutShape,
    layout_from_dict,
    layout_to_dict,
    sync_default_layout_lib,
)

__all__ = [
    "Layout", "LayoutShape",
    "apply_layout", "list_layouts", "register_layout",
    "ingest_pptx", "ingest_folder",
    "layout_from_dict", "layout_to_dict", "sync_default_layout_lib",
]
