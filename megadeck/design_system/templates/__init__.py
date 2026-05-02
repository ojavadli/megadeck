"""Slide template renderers — one function per slide kind."""
from megadeck.design_system.templates.hero_statement import render_hero_statement
from megadeck.design_system.templates.numbered_list import render_numbered_list
from megadeck.design_system.templates.three_card import render_three_card
from megadeck.design_system.templates.two_column import render_two_column
from megadeck.design_system.templates.section_divider import render_section_divider

__all__ = [
    "render_hero_statement",
    "render_numbered_list",
    "render_three_card",
    "render_two_column",
    "render_section_divider",
]
