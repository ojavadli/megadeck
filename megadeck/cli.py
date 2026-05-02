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
from megadeck.core.import_pptx import import_pptx
from megadeck.core.llm import generate_deck as llm_generate
from megadeck.core.preview import render_pptx_to_pngs
from megadeck.core.pptx_audit import audit_pptx, summarize_audit
from megadeck.core.renderer import render_deck
from megadeck.core.selfheal import render_with_selfheal
from megadeck.design_system.registry import (
    default_pool_dir,
    install_theme_url,
    list_pool_themes,
    load_theme_json,
    register_pool_theme,
    sync_default_pool,
    theme_to_dict,
)
from megadeck.design_system.tokens import get_theme, list_themes


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
    strict: bool = typer.Option(
        False, "--strict",
        help=(
            "After render, run shape-level audit + self-heal up to 4 iterations; "
            "exit non-zero if any errors remain."
        ),
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
    if strict:
        with console.status("[cyan]Rendering + self-heal loop…[/cyan]"):
            out_path, summary = render_with_selfheal(deck, output, max_iters=4)
        errors = summary.get("_errors", 0)
        if errors:
            console.print(f"[red]✗ {errors} audit errors remain after self-heal[/red]")
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] Wrote [bold]{out_path}[/bold] — strict audit clean")
    else:
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
        ("title",            "Cover slide — title, presenter, date, venue"),
        ("hero_statement",   "One bold statement + supporting lines"),
        ("numbered_list",    "Up to 6 items with big outlined numbers"),
        ("three_card",       "Three side-by-side cards"),
        ("two_column",       "Side-by-side comparison columns"),
        ("section_divider",  "Section break with eyebrow + giant title"),
        ("agenda",           "Numbered agenda with descriptions"),
        ("timeline",         "Horizontal timeline of milestones"),
        ("comparison_table", "Header + data rows comparison table"),
        ("pull_quote",       "Large quote with author and role"),
        ("bento_grid",       "Four cards in a 2x2 bento layout"),
        ("kpi_grid",         "2-4 metric tiles with delta"),
        ("before_after",     "Before / After split with verdict"),
        ("step_diagram",     "3-5 sequential steps with arrows"),
        ("code_snippet",     "Code block with language tag"),
        ("feature_grid",     "3-6 features with icon + title"),
        ("testimonial_grid", "2-3 customer quotes side by side"),
        ("team_grid",        "3-6 team members with initials"),
        ("pricing_table",    "2-3 pricing tiers"),
        ("takeaways",        "Numbered key takeaways"),
        ("call_to_action",   "Hero CTA with button-styled URL"),
        ("swot_matrix",      "Classic 2x2 SWOT"),
        ("faq_list",         "3-5 question / answer pairs"),
        ("stat_hero",        "Massive single stat with context"),
        ("logo_grid",        "Customer / partner logos grid"),
        ("question",         "Q&A pause slide"),
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


@app.command(name="import")
def import_command(
    pptx_path: Path = typer.Argument(..., help="Existing pptx to re-skin."),
    output: Path = typer.Option(
        Path("reskinned.pptx"), "--output", "-o", help="Output .pptx path.",
    ),
    theme: str = typer.Option(
        "default", "--theme", "-t",
        help="Theme to apply to the imported deck.",
    ),
    strict: bool = typer.Option(
        False, "--strict",
        help="Run audit + self-heal until clean; exit non-zero on remaining errors.",
    ),
) -> None:
    """Heuristically import an existing pptx into the Megadeck DSL and re-render it
    with a chosen theme. Best for re-skinning legacy decks. Complex slides may
    fall back to numbered_list template."""
    console.rule("[bold]Megadeck — Import + Re-render[/bold]")
    deck = import_pptx(pptx_path, theme=theme)
    console.print(f"[green]✓[/green] Imported {len(deck.slides)} slides")
    if strict:
        out, summary = render_with_selfheal(deck, output, max_iters=4, verbose=True)
        errors = summary.get("_errors", 0)
        if errors:
            console.print(f"[red]✗ {errors} audit errors remain after self-heal[/red]")
            raise typer.Exit(1)
        console.print(f"[green]✓[/green] [bold]{out}[/bold] — strict audit clean (errors=0)")
    else:
        out = render_deck(deck, output)
        console.print(f"[green]✓[/green] Re-rendered with theme [bold]{theme}[/bold] → {out}")


@app.command(name="pptx-audit")
def pptx_audit_command(
    pptx_path: Path = typer.Argument(..., help="Existing .pptx to audit."),
    json_out: bool = typer.Option(False, "--json", help="Print as JSON."),
) -> None:
    """Shape-level audit (overlap / overflow / off-canvas). Fast, deterministic."""
    audit = audit_pptx(pptx_path)
    summary = summarize_audit(audit)
    if json_out:
        out = {label: [
            {
                "issue": i.issue,
                "severity": i.severity,
                "detail": i.detail,
                "shape_idxs": list(i.shape_idxs),
            }
            for i in issues
        ] for label, issues in audit.items()}
        out["_summary"] = summary
        print(json.dumps(out, indent=2))
        return
    table = Table(title=f"PPTX audit — total={summary.get('_total', 0)} errors={summary.get('_errors', 0)}")
    table.add_column("Slide")
    table.add_column("Issue")
    table.add_column("Severity")
    table.add_column("Detail")
    for label, issues in audit.items():
        for iss in issues:
            colour = "red" if iss.severity == "error" else "yellow"
            table.add_row(
                label,
                iss.issue,
                f"[{colour}]{iss.severity}[/{colour}]",
                iss.detail,
            )
    console.print(table)


pool_app = typer.Typer(help="Manage the design pool — pluggable theme JSON files.")
app.add_typer(pool_app, name="pool")


# ---------------------------------------------------------------------------
# layouts subcommand — manage ingested human-designed layouts
# ---------------------------------------------------------------------------

layouts_app = typer.Typer(
    help="Ingest, list, and apply real human-designed slide layouts harvested from .pptx files."
)
app.add_typer(layouts_app, name="layouts")


@layouts_app.command("ingest")
def layouts_ingest_command(
    source: str = typer.Argument(
        ...,
        help="Path to a .pptx file or a folder containing .pptx files to harvest.",
    ),
    name_prefix: Optional[str] = typer.Option(
        None, "--prefix", "-p",
        help="Optional name prefix for ingested layouts.",
    ),
) -> None:
    """Ingest .pptx file(s) into the layout library.

    Each slide becomes one Layout JSON with role-classified shape geometry,
    saved under `megadeck/design_system/layouts/lib/`. Use `slide.layout=<name>`
    in the DSL or pass `--layout <name>` to render with that layout.
    """
    from megadeck.design_system.layouts.ingest import ingest_folder, ingest_pptx
    from megadeck.design_system.layouts.registry import default_layout_lib_dir

    src_path = Path(source)
    if not src_path.exists():
        console.print(f"[red]No such path:[/red] {src_path}")
        raise typer.Exit(1)
    target = default_layout_lib_dir()
    target.mkdir(parents=True, exist_ok=True)
    if src_path.is_file():
        layouts = ingest_pptx(src_path, save_to=target, name_prefix=name_prefix)
    else:
        layouts = ingest_folder(src_path, save_to=target)
    console.print(
        f"[green]✓[/green] Ingested [bold]{len(layouts)}[/bold] layouts from {src_path} "
        f"→ {target}"
    )


@layouts_app.command("list")
def layouts_list_command(
    kind: Optional[str] = typer.Option(
        None, "--kind", "-k",
        help="Filter by detected kind hint, e.g. 'numbered_list', 'hero_statement'.",
    ),
) -> None:
    """List all registered layouts."""
    from megadeck.design_system.layouts.registry import all_layouts

    rows = all_layouts()
    if kind:
        rows = [l for l in rows if l.kind_hint == kind]
    table = Table(title=f"Megadeck Layouts ({len(rows)})")
    table.add_column("Name", style="cyan")
    table.add_column("Kind hint")
    table.add_column("Shapes", justify="right")
    table.add_column("Source")
    for lay in sorted(rows, key=lambda x: x.name):
        table.add_row(lay.name, lay.kind_hint, str(len(lay.shapes)), lay.source)
    console.print(table)
    if not rows:
        console.print(
            "[yellow]No layouts ingested yet. Try:[/yellow]\n"
            "    megadeck layouts ingest <path-to-folder-of-pptx>"
        )


@pool_app.command("list")
def pool_list_command() -> None:
    """List every theme in the registry (built-ins + JSON pool)."""
    pool_dir = default_pool_dir()
    table = Table(title=f"Theme pool — {pool_dir}", show_lines=False)
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Source")
    pool_names = {p.stem for p in pool_dir.glob("*.json")}
    for name, description in list_themes():
        source = "pool/json" if name in pool_names else "built-in"
        table.add_row(name, description, source)
    console.print(table)


@pool_app.command("install")
def pool_install_command(
    source: str = typer.Argument(
        ...,
        help="Path to a theme .json (local) or HTTPS URL (e.g. github raw / gist).",
    ),
) -> None:
    """Install a theme from a local JSON file or a remote URL into the pool."""
    if source.startswith(("http://", "https://")):
        theme = install_theme_url(source)
        console.print(f"[green]✓[/green] Fetched + installed [bold]{theme.name}[/bold] from {source}")
        return
    json_path = Path(source)
    if not json_path.exists():
        console.print(f"[red]No such file:[/red] {json_path}")
        raise typer.Exit(1)
    theme = load_theme_json(json_path)
    register_pool_theme(theme)
    target = default_pool_dir() / f"{theme.name}.json"
    target.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
    console.print(f"[green]✓[/green] Installed [bold]{theme.name}[/bold] → {target}")


@pool_app.command("export")
def pool_export_command(
    name: str = typer.Argument(..., help="Theme name to export."),
    output: Path = typer.Option(Path("./theme.json"), "--output", "-o"),
) -> None:
    """Export an existing theme as JSON (good for forking a built-in)."""
    theme = get_theme(name)
    output.write_text(json.dumps(theme_to_dict(theme), indent=2), encoding="utf-8")
    console.print(f"[green]✓[/green] Exported [bold]{name}[/bold] → {output}")


@pool_app.command("sync")
def pool_sync_command() -> None:
    """Re-load every JSON in the pool directory."""
    loaded = sync_default_pool()
    console.print(
        f"[green]✓[/green] Synced [bold]{len(loaded)}[/bold] themes from "
        f"{default_pool_dir()}"
    )


@pool_app.command("generate")
def pool_generate_command(
    source: str = typer.Argument(
        "all",
        help="Adapter to run: tailwind / catppuccin / radix / open-color / all.",
    ),
) -> None:
    """Bulk-generate hundreds of themes from open-source ecosystems.

    `source=all` produces ~700 themes. Each adapter is sourced from the
    public colour spec of a major design system (Tailwind, Catppuccin,
    Radix, Open Color) — see megadeck/design_system/adapters/ for the
    licensed source citations.
    """
    from megadeck.design_system.adapters.bulk_generate import (
        SOURCES,
        generate_all,
    )
    target = default_pool_dir() / "auto"
    sources = None if source == "all" else [source]
    if sources is not None and sources[0] not in SOURCES:
        console.print(
            f"[red]Unknown source:[/red] {source}. Known: {sorted(SOURCES)}"
        )
        raise typer.Exit(1)
    written = generate_all(target, sources)
    console.print(
        f"[green]✓[/green] Wrote [bold]{len(written)}[/bold] themes to "
        f"{target} (run [italic]megadeck pool sync[/italic] to register)."
    )
    sync_default_pool()
    console.print(
        f"[green]✓[/green] Synced; live registry has [bold]"
        f"{len(set(list_pool_themes()))}[/bold] themes total."
    )


@pool_app.command("from-seed")
def pool_from_seed_command(
    seed: str = typer.Argument(
        ...,
        help="Hex color (e.g. '#3B82F6' or '3B82F6'). Generates 10 themes (5 styles × light/dark).",
    ),
    name: str = typer.Option(
        "material", "--name", "-n", help="Theme name prefix.",
    ),
) -> None:
    """Generate themes from a single seed color via Material You's TonalPalette algorithm.

    Pass any hex code, get back 10 distinct themes spanning 5 visual styles
    × light/dark modes — the entire family is derived mathematically.
    """
    import json as _json
    from megadeck.design_system.adapters.material_you import generate_material_themes
    seed_clean = "#" + seed.lstrip("#")
    themes = generate_material_themes(seed_clean, base_name=name)
    target = default_pool_dir() / "auto" / "material"
    target.mkdir(parents=True, exist_ok=True)
    for t in themes:
        (target / f"{t['name']}.json").write_text(_json.dumps(t, indent=2), encoding="utf-8")
    sync_default_pool()
    console.print(
        f"[green]✓[/green] Generated [bold]{len(themes)}[/bold] Material themes "
        f"from seed [bold]{seed_clean}[/bold] → {target}"
    )


@pool_app.command("from-coolors")
def pool_from_coolors_command(
    source: str = typer.Argument(
        ...,
        help="Coolors palette URL or dash-separated hex string.",
    ),
    name: str = typer.Option(
        "coolors", "--name", "-n", help="Theme name prefix.",
    ),
) -> None:
    """Generate themes from a Coolors.co palette URL.

    Pass a URL like https://coolors.co/palette/0a0e27-3b82f6-f97316 —
    you get 8 themes (4 styles × light/dark) using those exact colours.
    """
    import json as _json
    from megadeck.design_system.adapters.coolors import generate_coolors_themes
    themes = generate_coolors_themes(source, base_name=name)
    target = default_pool_dir() / "auto" / "coolors"
    target.mkdir(parents=True, exist_ok=True)
    for t in themes:
        (target / f"{t['name']}.json").write_text(_json.dumps(t, indent=2), encoding="utf-8")
    sync_default_pool()
    console.print(
        f"[green]✓[/green] Generated [bold]{len(themes)}[/bold] Coolors themes → {target}"
    )


@pool_app.command("install-vscode")
def pool_install_vscode_command(
    source: str = typer.Argument(
        ...,
        help="Path or HTTPS URL of a VSCode theme.json.",
    ),
) -> None:
    """Convert a VSCode theme.json into a megadeck theme and install it.

    VSCode marketplace exposes thousands of themes as plain JSON; pass any
    theme.json (file or URL) and megadeck will adapt the colour mappings.
    """
    import json as _json
    import urllib.request
    from megadeck.design_system.adapters.vscode import vscode_theme_to_megadeck
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=10) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
    else:
        data = _json.loads(Path(source).read_text(encoding="utf-8"))
    spec = vscode_theme_to_megadeck(data)
    register_pool_theme(load_theme_json_dict(spec))
    out = default_pool_dir() / "auto" / f"{spec['name']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps(spec, indent=2), encoding="utf-8")
    console.print(
        f"[green]✓[/green] Installed VSCode theme [bold]{spec['name']}[/bold] "
        f"→ {out}"
    )


def load_theme_json_dict(d: dict):
    """Helper: build a Theme from an in-memory dict (used by install-vscode)."""
    from megadeck.design_system.registry import theme_from_dict
    return theme_from_dict(d)


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
