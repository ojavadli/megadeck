# Roadmap

## Phase 1 — Foundation (shipped)

- ✅ Pydantic DSL covering 5 core slide templates
- ✅ Theme system with 3 starter themes (default, dark, editorial)
- ✅ Renderer: DSL → python-pptx
- ✅ Preview pipeline: pptx → PDF → PNG via libreoffice
- ✅ Critic loop: visual audit with LLM
- ✅ Multi-provider LLM client (Anthropic / OpenAI / Google) via `instructor`
- ✅ CLI (`megadeck`)
- ✅ MCP server (`megadeck-mcp`) exposing 4 tools
- ✅ Tests + GitHub Actions CI

## Phase 2 — Breadth

### More templates (target 20+ total)

- [ ] `data_chart` — bar / line / pie with stylable axes
- [ ] `timeline` — horizontal / vertical event timeline
- [ ] `comparison_table` — feature matrix
- [ ] `pull_quote` — large quote + attribution
- [ ] `bento_grid` — 2x2 / 3x2 mixed-size cards
- [ ] `image_left_text_right`
- [ ] `kpi_grid` — 2x4 metric tiles with deltas
- [ ] `before_after`
- [ ] `step_diagram` — sequential arrow flow
- [ ] `team_grid` — photo grid with names/roles
- [ ] `roadmap_timeline`
- [ ] `pricing_table`
- [ ] `org_chart`
- [ ] `swot_matrix`
- [ ] `code_snippet` — syntax-highlighted code
- [ ] `agenda` — numbered topics with descriptions

### More themes

- [ ] `corporate` — navy + white, conservative
- [ ] `linear` — Linear-app aesthetic
- [ ] `pastel` — warm muted tones
- [ ] `neon` — high-contrast dark + electric accents
- [ ] `print` — magazine editorial style

### Animations module

- [ ] `entrance` presets (fade, slide-in, scale-up, zoom)
- [ ] `transitions` between slides (fade / morph / push)
- [ ] `motion_paths` for emphasis animations
- [ ] Stagger / sequence helpers

### Critic improvements

- [ ] Per-template overflow heuristics (rule-based) before LLM
- [ ] Auto-fix common issues (font scaling, line breaks)
- [ ] Diff view: before-fix / after-fix PNG side-by-side

## Phase 3 — Distribution & UX

- [ ] FastAPI web preview UI (live PNG of generated slides)
- [ ] PyPI release pipeline (GitHub Actions on tag)
- [ ] Smithery registry submission for one-command MCP install
- [ ] `megadeck import` — round-trip an existing pptx into the DSL for re-styling
- [ ] Keynote export (via AppleScript on macOS)
- [ ] Watch mode that re-renders on prompt-file edit
- [ ] Documentation site (mkdocs)

## Phase 4 — Quality & ecosystem

- [ ] Plugin system for community templates and themes
- [ ] Headless test renders via cloud LibreOffice
- [ ] Telemetry-free usage analytics (opt-in)
- [ ] Marketplace of community-contributed themes
