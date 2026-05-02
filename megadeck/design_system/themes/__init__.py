"""Built-in themes are registered in megadeck.design_system.tokens.

This subpackage is reserved for *user-extension* themes. To add a custom theme
at runtime:

    from megadeck.design_system.tokens import Theme, register_theme
    register_theme(Theme(name="mybrand", ...))
"""
