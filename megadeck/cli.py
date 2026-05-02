"""Megadeck CLI — `megadeck generate`, `audit`, `themes`, `templates`, `preview`."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from megadeck import __version__
from megadeck.core.critic import audit_deck as audit_deck_core
from megadeck.core.llm import generate_deck as llm_generate
from megadeck.core.preview import render_pptx_to_pngs
from megadeck.core.renderer import render_deck
from megadeck.design_system.tokens import list_themes


app = typer.Typer(
    name="megadeck",
    help="AI-driven PowerPoint generation. Turn prompts into audited .pptx decks.",
    add_completion=False,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"megadeck v{__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v",
        callback=_version_callback,
        is_eager=True,
        help="Print the installed version and exit.",
    ),
) -> None:
    """Megadeck — AI-driven PowerPoint generation."""


@app.command()
def generate(
    prompt: str = typer.Argument(..., help="What the deck should be about."),
    output: Path = typer.Option(
        Path("deck.pptx"), "--output", "-o", help="Output .pptx path.",
    ),
    n_slides: int = typer.Option(
        20, "--slides", "-n", help="Target number of slides.",
    ),
    theme: str = typer.Option(
        "default", "--theme", "-t", help="Theme name (default / dark / editorial).",
    ),
    provider: str = typer.Option(
        "auto", "--provider", "-p",
        help="LLM provider: auto / anthropic / openai / google.",
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m", help="Override the default model for the provider.",
    ),
    audit: bool = typer.Option(
        True, "--audit/--no-audit",
        help="Run the visual critic loop after rendering.",
    ),
) -> None:
    """Generate a deck from a natural-language prompt."""
    console.rule("[bold]Megadeck — Generate[/bold]")
    console.print(f"[muted]Prompt:[/muted] {prompt[:120]}{'…' if len(prompt) > 120 else ''}")
    console.print(f"[muted]Theme:[/muted] {theme}   [muted]Slides:[/muted] {n_slides}   [muted]Provider:[/muted] {provider}")
    with console.status("[cyan]Calling LLM (constrained schema)…[/cyan]"):
        deck = llm_generate(
            prompt,
            n_slides=n_slides,
            theme=theme,
            provider=provider,  # type: ignore[arg-type]
            model=model,
        )
    console.print(f"[green]✓[/green] LLM produced {len(deck.slides)} slides.")
    with console.status("[cyan]Rendering pptx…[/cyan]"):
        out_path = render_deck(deck, output)
    console.print(f"[green]✓[/green] Wrote [bold]{out_path}[/bold]")
    if audit:
        with console.status("[cyan]Running visual critic…[/cyan]"):
            report = audit_deck_core(out_path, deck=deck)
        console.print(_format_audit(report))


@app.command()
def audit(
    pptx_path: Path = typer.Argument(..., help="Existing .pptx to audit."),
    use_llm: bool = typer.Option(
        True, "--llm/--no-llm",
        help="Whether to use the vision LLM in addition to heuristics.",
    ),
    json_out: bool = typer.Option(
        False, "--json", help="Print the audit as JSON instead of a table.",
    ),
) -> None:
    """Visually audit an existing pptx for overflow / alignment issues."""
    report = audit_deck_core(pptx_path, use_llm=use_llm)
    if json_out:
        print(json.dumps(report.model_dump(), indent=2))
        return
    console.print(_format_audit(report))


@app.command()
def themes() -> None:
    """List the built-in themes."""
    table = Table(title="Themes", show_lines=False)
    table.add_column("Name", style="bold")
    table.add_column("Description")
    for name, description in list_themes():
        table.add_row(name, description)
    console.print(table)


@app.command()
def templates() -> None:
    """List the available slide templates."""
    rows = [
        ("hero_statement", "One bold statement + supporting lines"),
        ("numbered_list",  "Up to 6 items with big outlined numbers"),
        ("three_card",     "Three side-by-side cards"),
        ("two_column",     "Side-by-side comparison columns"),
        ("section_divider","Section break with eyebrow + giant title"),
    ]
    table = Table(title="Slide templates", show_lines=False)
    table.add_column("Kind", style="bold")
    table.add_column("Description")
    for k, d in rows:
        table.add_row(k, d)
    console.print(table)


@app.command()
def preview(
    pptx_path: Path = typer.Argument(..., help="The .pptx to render."),
    out_dir: Optional[Path] = typer.Option(
        None, "--out", "-o", help="Output directory for PNG previews.",
    ),
    dpi: int = typer.Option(100, "--dpi", help="DPI of rendered PNGs."),
) -> None:
    """Render every slide of a pptx to PNG (one image per slide)."""
    pngs = render_pptx_to_pngs(pptx_path, output_dir=out_dir, dpi=dpi)
    for p in pngs:
        console.print(f"  [green]•[/green] {p}")
    console.print(f"\n[bold]{len(pngs)}[/bold] preview images written.")


# ----- Helpers -----------------------------------------------------------------

def _format_audit(report) -> Panel:
    if report.total_issues == 0:
        body = "[green]No mechanical issues detected on any slide.[/green]"
    else:
        lines = [f"[bold]{report.total_issues}[/bold] issues found across {report.slide_count} slides:\n"]
        for sa in report.slide_audits:
            if not sa.issues:
                continue
            lines.append(f"[bold]Slide {sa.slide_index + 1}[/bold] ({sa.slide_kind})")
            for issue in sa.issues:
                lines.append(f"  • [yellow]{issue.issue}[/yellow] — {issue.detail}")
                lines.append(f"    [dim]fix:[/dim] {issue.suggested_fix}")
            lines.append("")
        body = "\n".join(lines)
    return Panel(body, title="Visual audit", border_style="cyan")


if __name__ == "__main__":
    app()
