"""Megadeck — AI-driven PowerPoint generation, audited slide-by-slide.

Public API:
    from megadeck import generate_deck, audit_deck, render_deck

The same package powers both the `megadeck` CLI and the `megadeck-mcp` MCP server.
"""
from megadeck.core.schemas import Deck, Slide  # noqa: F401
from megadeck.core.renderer import render_deck  # noqa: F401

# Auto-load every theme JSON shipped under `megadeck/design_system/pool/`
# so the registry is populated at import time. Failing themes are skipped
# (they print a warning) so a single bad JSON can't break `import megadeck`.
try:
    from megadeck.design_system.registry import sync_default_pool
    sync_default_pool()
except Exception as _exc:  # noqa: BLE001
    import warnings
    warnings.warn(f"megadeck pool sync failed: {_exc}")

# Auto-load every ingested layout JSON shipped under
# `megadeck/design_system/layouts/lib/`. These are real human-designed
# slide layouts harvested from .pptx files via `megadeck layouts ingest`.
try:
    from megadeck.design_system.layouts.registry import sync_default_layout_lib
    sync_default_layout_lib()
except Exception as _exc:  # noqa: BLE001
    import warnings
    warnings.warn(f"megadeck layout-lib sync failed: {_exc}")

__version__ = "0.2.0"
