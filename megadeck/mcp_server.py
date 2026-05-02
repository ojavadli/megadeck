"""MCP server — exposes Megadeck's tools to Claude Code, Cursor, and any
MCP-aware client.

Run with: `megadeck-mcp` (stdio transport).

Add to Claude Code:
    claude mcp add megadeck --command "uvx megadeck-mcp"

Add to Cursor (~/.cursor/mcp.json):
    {
      "mcpServers": {
        "megadeck": { "command": "uvx", "args": ["megadeck-mcp"] }
      }
    }
"""
from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

from megadeck.core.critic import audit_deck as audit_deck_core
from megadeck.core.llm import generate_deck as llm_generate
from megadeck.core.preview import render_pptx_to_pngs
from megadeck.core.renderer import render_deck
from megadeck.design_system.tokens import list_themes


mcp = FastMCP(
    name="megadeck",
    instructions=(
        "Generate, audit, and preview PowerPoint decks. "
        "Use generate_deck(prompt, ...) for end-to-end generation; "
        "audit_deck(path) to flag visual issues on an existing pptx; "
        "list_themes() and list_templates() for discovery."
    ),
)


@mcp.tool()
def generate_deck_tool(
    prompt: str,
    output_path: str = "deck.pptx",
    n_slides: int = 20,
    theme: str = "default",
    provider: str = "auto",
    audit: bool = True,
) -> dict:
    """Generate a presentation deck from a prompt.

    Args:
        prompt: Free-form description of the deck (topic, audience, structure).
        output_path: Where the .pptx is saved.
        n_slides: Target number of slides (1–80).
        theme: One of the registered theme names ('default', 'dark', 'editorial').
        provider: 'auto' (default), 'anthropic', 'openai', or 'google'.
        audit: Run the visual critic loop after rendering.

    Returns:
        A dict with the absolute output path, slide count, and (if audit=True)
        a per-slide audit report.
    """
    deck = llm_generate(
        prompt,
        n_slides=n_slides,
        theme=theme,
        provider=provider,  # type: ignore[arg-type]
    )
    out = render_deck(deck, output_path)
    response = {
        "output_path": str(out.resolve()),
        "slide_count": len(deck.slides),
        "theme": deck.theme,
    }
    if audit:
        report = audit_deck_core(out, deck=deck)
        response["audit"] = report.model_dump()
    return response


@mcp.tool()
def audit_deck_tool(pptx_path: str, use_llm: bool = True) -> dict:
    """Audit an existing pptx for overflow, alignment, and sizing issues.

    Args:
        pptx_path: Path to a .pptx file.
        use_llm: If True, run the vision LLM critic in addition to heuristics.
    """
    report = audit_deck_core(pptx_path, use_llm=use_llm)
    return report.model_dump()


@mcp.tool()
def preview_deck_tool(pptx_path: str, dpi: int = 100) -> dict:
    """Render every slide of a pptx to PNG. Returns the list of PNG paths."""
    pngs = render_pptx_to_pngs(pptx_path, dpi=dpi)
    return {"pngs": [str(Path(p).resolve()) for p in pngs]}


@mcp.tool()
def list_themes_tool() -> list[dict]:
    """Return the registered themes (name + description)."""
    return [{"name": n, "description": d} for n, d in list_themes()]


@mcp.tool()
def list_templates_tool() -> list[dict]:
    """Return the available slide templates and when to use each."""
    return [
        {"kind": "hero_statement", "use": "One bold statement (≤ 80 chars) + up to 4 supporting lines."},
        {"kind": "numbered_list", "use": "2–6 items with bold heads + tail descriptions."},
        {"kind": "three_card", "use": "Exactly three side-by-side cards (badge / label / description)."},
        {"kind": "two_column", "use": "Side-by-side comparison."},
        {"kind": "section_divider", "use": "Part break with eyebrow + giant title."},
    ]


def main() -> None:
    """Stdio entry point used by Claude Code / Cursor."""
    mcp.run()


if __name__ == "__main__":
    main()
