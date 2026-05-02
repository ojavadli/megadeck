"""Per-template layout variants.

The renderer maps `(slide.kind, slide.variant)` → render function. When
`slide.variant` is `None`, the kind's default layout is used (the same
function previously dispatched on kind alone).

This is the difference between:

  * "I changed the colours" → all slides look like the same template
                              recoloured.
  * "I changed the design"  → a `numbered_list` can be a vertical timeline,
                              a 2-column split, individual cards, or the
                              classic outlined-numerals layout. *Same content*,
                              completely different reading experience.

Adding a variant
----------------

  1. Write `render_<kind>_<variant>(slide, data, theme, *, page_n, …)`.
  2. Register it in `VARIANTS[(kind, variant)] = render_fn` below.
  3. Done. The renderer picks it up automatically.

A theme can default-lock a variant via `theme.variant_overrides` (see
tokens.py) — handy for "every numbered_list in this theme renders as
cards by default".
"""
from __future__ import annotations

from typing import Callable, Dict, Optional, Tuple

from megadeck.design_system.tokens import Theme


# (kind, variant_name) → render function
VARIANTS: Dict[Tuple[str, str], Callable] = {}


def register_variant(kind: str, name: str):
    """Decorator: register a render function as a (kind, variant) variant."""
    def deco(fn: Callable) -> Callable:
        VARIANTS[(kind, name)] = fn
        return fn
    return deco


def get_variant_renderer(
    kind: str,
    variant: Optional[str],
    theme: Theme,
    default: Callable,
) -> Callable:
    """Resolve the render function for `(kind, variant)`.

    Resolution order:
      1. Explicit slide-level variant if registered.
      2. Theme's `variant_overrides[kind]` if set.
      3. The kind's default renderer.
    """
    if variant:
        fn = VARIANTS.get((kind, variant))
        if fn is not None:
            return fn
    overrides_raw = getattr(theme, "variant_overrides", None) or ()
    # `variant_overrides` is a tuple of (kind, variant) pairs (frozen-dataclass
    # friendly). Convert to a dict at lookup time.
    overrides = dict(overrides_raw) if not isinstance(overrides_raw, dict) else overrides_raw
    if kind in overrides:
        fn = VARIANTS.get((kind, overrides[kind]))
        if fn is not None:
            return fn
    return default


__all__ = ["VARIANTS", "register_variant", "get_variant_renderer"]
