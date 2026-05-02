"""Slide template renderers — one function per slide kind."""
from megadeck.design_system.templates.agenda import render_agenda
from megadeck.design_system.templates.before_after import render_before_after
from megadeck.design_system.templates.bento_grid import render_bento_grid
from megadeck.design_system.templates.code_snippet import render_code_snippet
from megadeck.design_system.templates.comparison_table import render_comparison_table
from megadeck.design_system.templates.hero_statement import render_hero_statement
from megadeck.design_system.templates.kpi_grid import render_kpi_grid
from megadeck.design_system.templates.numbered_list import render_numbered_list
from megadeck.design_system.templates.pull_quote import render_pull_quote
from megadeck.design_system.templates.section_divider import render_section_divider
from megadeck.design_system.templates.step_diagram import render_step_diagram
from megadeck.design_system.templates.three_card import render_three_card
from megadeck.design_system.templates.timeline import render_timeline
from megadeck.design_system.templates.title import render_title
from megadeck.design_system.templates.two_column import render_two_column

__all__ = [
    "render_agenda",
    "render_before_after",
    "render_bento_grid",
    "render_code_snippet",
    "render_comparison_table",
    "render_hero_statement",
    "render_kpi_grid",
    "render_numbered_list",
    "render_pull_quote",
    "render_section_divider",
    "render_step_diagram",
    "render_three_card",
    "render_timeline",
    "render_title",
    "render_two_column",
]
