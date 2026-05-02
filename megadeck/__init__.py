"""Megadeck — AI-driven PowerPoint generation, audited slide-by-slide.

Public API:
    from megadeck import generate_deck, audit_deck, render_deck

The same package powers both the `megadeck` CLI and the `megadeck-mcp` MCP server.
"""
from megadeck.core.schemas import Deck, Slide  # noqa: F401
from megadeck.core.renderer import render_deck  # noqa: F401

__version__ = "0.1.0"
