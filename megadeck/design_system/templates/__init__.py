"""Slide template renderers — one function per slide kind."""
from megadeck.design_system.templates.agenda import render_agenda
from megadeck.design_system.templates.bar_chart import render_bar_chart
from megadeck.design_system.templates.before_after import render_before_after
from megadeck.design_system.templates.bento_grid import render_bento_grid
from megadeck.design_system.templates.call_to_action import render_call_to_action
from megadeck.design_system.templates.code_snippet import render_code_snippet
from megadeck.design_system.templates.comparison_table import render_comparison_table
from megadeck.design_system.templates.donut_chart import render_donut_chart
from megadeck.design_system.templates.editorial_split import render_editorial_split
from megadeck.design_system.templates.faq_list import render_faq_list
from megadeck.design_system.templates.feature_grid import render_feature_grid
from megadeck.design_system.templates.hero_minimal import render_hero_minimal
from megadeck.design_system.templates.hero_statement import render_hero_statement
from megadeck.design_system.templates.icon_grid import render_icon_grid
from megadeck.design_system.templates.kpi_grid import render_kpi_grid
from megadeck.design_system.templates.logo_grid import render_logo_grid
from megadeck.design_system.templates.manifesto import render_manifesto
from megadeck.design_system.templates.numbered_list import render_numbered_list
from megadeck.design_system.templates.photo_card import render_photo_card
from megadeck.design_system.templates.pricing_table import render_pricing_table
from megadeck.design_system.templates.pull_quote import render_pull_quote
from megadeck.design_system.templates.question import render_question
from megadeck.design_system.templates.quote_decorative import render_quote_decorative
from megadeck.design_system.templates.section_divider import render_section_divider
from megadeck.design_system.templates.section_hero import render_section_hero
from megadeck.design_system.templates.stat_callout import render_stat_callout
from megadeck.design_system.templates.stat_hero import render_stat_hero
from megadeck.design_system.templates.step_diagram import render_step_diagram
from megadeck.design_system.templates.swot_matrix import render_swot_matrix
from megadeck.design_system.templates.takeaways import render_takeaways
from megadeck.design_system.templates.team_grid import render_team_grid
from megadeck.design_system.templates.testimonial_grid import render_testimonial_grid
from megadeck.design_system.templates.three_card import render_three_card
from megadeck.design_system.templates.timeline import render_timeline
from megadeck.design_system.templates.title import render_title
from megadeck.design_system.templates.two_column import render_two_column

# Side-effect imports: register (kind, variant) → render_fn into VARIANTS.
# Without these, the variant dispatch silently falls back to defaults.
from megadeck.design_system.templates import numbered_list_variants  # noqa: F401
from megadeck.design_system.templates import hero_statement_variants  # noqa: F401
from megadeck.design_system.templates import three_card_variants  # noqa: F401

__all__ = [
    "render_agenda",
    "render_bar_chart",
    "render_before_after",
    "render_bento_grid",
    "render_call_to_action",
    "render_code_snippet",
    "render_comparison_table",
    "render_donut_chart",
    "render_editorial_split",
    "render_faq_list",
    "render_feature_grid",
    "render_hero_minimal",
    "render_hero_statement",
    "render_icon_grid",
    "render_kpi_grid",
    "render_logo_grid",
    "render_manifesto",
    "render_numbered_list",
    "render_photo_card",
    "render_pricing_table",
    "render_pull_quote",
    "render_question",
    "render_quote_decorative",
    "render_section_divider",
    "render_section_hero",
    "render_stat_callout",
    "render_stat_hero",
    "render_step_diagram",
    "render_swot_matrix",
    "render_takeaways",
    "render_team_grid",
    "render_testimonial_grid",
    "render_three_card",
    "render_timeline",
    "render_title",
    "render_two_column",
]
