# Megadeck

> AI-driven PowerPoint generation, audited slide-by-slide, ready for Claude Code and any MCP-compatible client.

Megadeck turns a natural-language prompt into a styled `.pptx` file. It exposes the same core both as a **command-line tool** and as a **Model Context Protocol (MCP) server**, so Claude Code, Claude Desktop, and any MCP-aware client can call it directly.

It is opinionated about three things:

1. **Constrained output** — the LLM never produces freeform text; it produces a typed Pydantic schema that the renderer turns into pptx.
2. **Visual auditing** — every slide is rendered to PNG and checked for overflow, alignment, and sizing issues *before* the deck is saved.
3. **Theming first** — slide content lives in JSON; visual style lives in themes. Switch themes without rewriting content.

---

## Install

The fastest path is `uvx` (zero install, runs the latest from PyPI):

```bash
# CLI
uvx megadeck generate "30-slide masterclass on entrepreneurship and AI agents" \
    --output deck.pptx

# MCP server (stdio)
uvx megadeck-mcp
```

Or install with `pip`:

```bash
pip install megadeck
megadeck --help
```

---

## Use it inside Claude Code

```bash
claude mcp add megadeck \
    --command "uvx megadeck-mcp" \
    --env "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
```

Then in any Claude Code session:

> "Read `notes.md` and generate a 20-slide pitch deck. Use the editorial theme."

Claude calls Megadeck's MCP tools, runs the critic loop, and saves the `.pptx`.

## Use it inside any MCP-compatible client

Megadeck speaks the standard Model Context Protocol over stdio, so any MCP-aware client (Claude Desktop, Continue, Zed, etc.) can launch it. Drop the following into the client's MCP config:

```json
{
  "mcpServers": {
    "megadeck": {
      "command": "uvx",
      "args": ["megadeck-mcp"],
      "env": { "ANTHROPIC_API_KEY": "..." }
    }
  }
}
```

Restart the client; its agent now has access to Megadeck.

---

## What's in the box

### Slide templates (Phase 1)

| Template | When to use |
|---|---|
| `hero_statement` | One-line bold idea, e.g. "Hard is good." |
| `numbered_list` | Up to six points with big outlined numbers |
| `three_card` | Three side-by-side concepts |
| `two_column` | Comparison / before-after |
| `section_divider` | Part-break with eyebrow + giant title |

More templates land in Phase 2 — see `ROADMAP.md`.

### Themes (Phase 1)

| Theme | Mood |
|---|---|
| `default` | Sky-blue, minimalistic, lots of whitespace |
| `dark` | Slate-900 background, white type |
| `editorial` | Serif headings, neutral palette |

### CLI

```bash
megadeck generate "<prompt>"           # full pipeline
megadeck audit deck.pptx               # render + critique an existing deck
megadeck themes                        # list available themes
megadeck templates                     # list available slide templates
megadeck preview deck.pptx --out png/  # render every slide to PNG
```

### MCP tools

When loaded via `megadeck-mcp`, the server exposes these tools:

- `generate_deck(prompt, theme, n_slides, output_path)`
- `audit_deck(path)` — returns per-slide overflow/alignment report
- `list_templates()`
- `list_themes()`

### LLM provider

Picks up whichever environment variable is set, in this order:

1. `ANTHROPIC_API_KEY` → Claude Sonnet 4 (default)
2. `OPENAI_API_KEY` → GPT-4o
3. `GOOGLE_API_KEY` → Gemini 2.5 Pro (with `pip install megadeck[google]`)

You can force a provider with `--model anthropic|openai|google`.

---

## Architecture

```
prompt
   │
   ▼
┌──────────────────────────────────────────────────┐
│  LLM + instructor  →  validated Pydantic Deck    │
│  (constrained output — no malformed JSON ever)   │
└──────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────┐
│  Renderer (theme-aware) → python-pptx → .pptx    │
└──────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────┐
│  Preview (libreoffice → PDF → PNG per slide)     │
└──────────────────────────────────────────────────┘
   │
   ▼
┌──────────────────────────────────────────────────┐
│  Critic (LLM audits PNG for overflow/alignment)  │
│  → flagged slides regenerate until they pass     │
└──────────────────────────────────────────────────┘
   │
   ▼
.pptx (clean, audited, ready to present)
```

---

## Roadmap

See [`ROADMAP.md`](./ROADMAP.md). Phase 1 ships the foundation, the MCP/CLI surface, and 5 production templates. Phase 2 adds 15+ more templates, animation primitives, and additional themes. Phase 3 adds a web preview UI and Smithery registry submission.

---

## Built with

- [`python-pptx`](https://github.com/scanny/python-pptx) — pptx file authoring
- [`pydantic`](https://github.com/pydantic/pydantic) — schema validation
- [`instructor`](https://github.com/jxnl/instructor) — typed LLM output
- [`fastmcp`](https://github.com/jlowin/fastmcp) — MCP server framework
- [`typer`](https://github.com/tiangolo/typer) + [`rich`](https://github.com/Textualize/rich) — CLI surface
- LibreOffice (headless) + [`pdf2image`](https://github.com/Belval/pdf2image) — slide preview
- Architecture inspired by AI-assisted code-generation tools and constrained-output prompting techniques.

## Contributors

- [Orkhan Javadli](https://github.com/ojavadli)
- [Anni Zimina](https://github.com/anni-stanford)

See [`CONTRIBUTORS.md`](./CONTRIBUTORS.md).

## License

MIT — see [`LICENSE`](./LICENSE).
