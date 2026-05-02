"""Slide-level transitions and entrance animations (pptx XML).

PowerPoint's animation system is keyframe-based and lives in the slide's
`<p:transition>` and `<p:timing>` elements. We expose a small set of
declarative helpers here so the renderer never has to write raw XML.
"""
from megadeck.animations.transitions import apply_transition

__all__ = ["apply_transition"]
