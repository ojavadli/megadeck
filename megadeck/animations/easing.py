"""Easing curves — direct port of Motion's `motion-utils/easing/` package.

Source studied (MIT-licensed):
  https://github.com/motiondivision/motion/tree/main/packages/motion-utils/src/easing

Why port these
--------------
PowerPoint's animation timing is XML-driven, but the *math* of an animation
curve is the same wherever it runs: a function `f(t) -> y` mapping progress
in [0, 1] to a value in [0, 1]. Motion exposes the canonical set:

* cubic-bezier (the engine behind every named curve)
* ease / easeIn / easeOut / easeInOut
* circ / circIn / circOut / circInOut       — derived from sin·acos
* back / backIn / backOut / backInOut       — overshoot curves (cubic-bezier)
* anticipate                                — pull-back-then-release
* steps(n, "start" | "end")                 — discrete stepping
* mirror(easing) / reverse(easing)          — modifiers

We use these to derive PPTX-renderable timing diagrams (linear keyframe
sequences a la Motion's `generateLinearEasing`) so a "spring bounce" is
serialisable into the limited animation primitives PowerPoint supports.

Everything below is a 1:1 translation from the TypeScript original. We
keep the same names and the same numerical constants so a Motion user can
read this file and recognise it line-for-line.
"""
from __future__ import annotations

import math
from typing import Callable, Literal

EasingFn = Callable[[float], float]


# ---------------------------------------------------------------------------
# Cubic bezier — the foundation
# ---------------------------------------------------------------------------

# Constants from Motion's cubic-bezier.ts
_SUBDIVISION_PRECISION = 0.0000001
_SUBDIVISION_MAX_ITERATIONS = 12


def _calc_bezier(t: float, a1: float, a2: float) -> float:
    """Return x(t) given t and the two control-point coordinates a1, a2.

    This is Motion's `calcBezier()`:
        ((1 - 3*a2 + 3*a1) * t + (3*a2 - 6*a1)) * t + 3*a1) * t
    """
    return (
        ((1.0 - 3.0 * a2 + 3.0 * a1) * t + (3.0 * a2 - 6.0 * a1)) * t + 3.0 * a1
    ) * t


def _binary_subdivide(x: float, mX1: float, mX2: float) -> float:
    lo, hi = 0.0, 1.0
    current_t = 0.0
    for _ in range(_SUBDIVISION_MAX_ITERATIONS):
        current_t = lo + (hi - lo) / 2.0
        current_x = _calc_bezier(current_t, mX1, mX2) - x
        if current_x > 0:
            hi = current_t
        else:
            lo = current_t
        if abs(current_x) <= _SUBDIVISION_PRECISION:
            return current_t
    return current_t


def cubic_bezier(mX1: float, mY1: float, mX2: float, mY2: float) -> EasingFn:
    """Return a cubic-bezier easing function. Direct port of Motion's
    `cubicBezier(.42, 0, .58, 1)` style API."""
    if mX1 == mY1 and mX2 == mY2:
        return lambda t: t  # linear shortcut

    def f(t: float) -> float:
        if t == 0 or t == 1:
            return t
        return _calc_bezier(_binary_subdivide(t, mX1, mX2), mY1, mY2)

    return f


# ---------------------------------------------------------------------------
# Modifiers
# ---------------------------------------------------------------------------

def reverse_easing(easing: EasingFn) -> EasingFn:
    """`easeIn` → `easeOut`. From Motion's `reverseEasing`."""
    return lambda p: 1 - easing(1 - p)


def mirror_easing(easing: EasingFn) -> EasingFn:
    """`easeIn` → `easeInOut`. From Motion's `mirrorEasing`."""
    return lambda p: easing(2 * p) / 2 if p <= 0.5 else (2 - easing(2 * (1 - p))) / 2


# ---------------------------------------------------------------------------
# Named easings — same constants as Motion
# ---------------------------------------------------------------------------

ease_in = cubic_bezier(0.42, 0, 1, 1)
ease_out = cubic_bezier(0, 0, 0.58, 1)
ease_in_out = cubic_bezier(0.42, 0, 0.58, 1)


# circular (Motion's circ.ts)
def circ_in(p: float) -> float:
    return 1 - math.sin(math.acos(p))


circ_out = reverse_easing(circ_in)
circ_in_out = mirror_easing(circ_in)


# back (overshoot) — Motion uses cubicBezier(0.33, 1.53, 0.69, 0.99) for backOut
back_out = cubic_bezier(0.33, 1.53, 0.69, 0.99)
back_in = reverse_easing(back_out)
back_in_out = mirror_easing(back_in)


def anticipate(p: float) -> float:
    """`anticipate` from Motion: pull-back-then-release. Often used for
    drawer/menu pop-ins."""
    if p >= 1:
        return 1
    p2 = p * 2
    if p2 < 1:
        return 0.5 * back_in(p2)
    return 0.5 * (2 - math.pow(2, -10 * (p - 1)))


def steps(n_steps: int, direction: Literal["start", "end"] = "end") -> EasingFn:
    """Discrete stepping easing — Motion's `steps(n, "end")`."""
    if n_steps < 1:
        raise ValueError("steps requires at least 1 step")

    def f(progress: float) -> float:
        if direction == "end":
            progress = min(progress, 0.999)
        else:
            progress = max(progress, 0.001)
        expanded = progress * n_steps
        rounded = math.floor(expanded) if direction == "end" else math.ceil(expanded)
        return max(0.0, min(1.0, rounded / n_steps))

    return f


# Convenient lookup dict — used by themes / decorations to specify
# easings declaratively in JSON.
EASINGS: dict[str, EasingFn] = {
    "linear":      lambda t: t,
    "ease":        ease_in_out,
    "ease-in":     ease_in,
    "ease-out":    ease_out,
    "ease-in-out": ease_in_out,
    "circ-in":     circ_in,
    "circ-out":    circ_out,
    "circ-in-out": circ_in_out,
    "back-in":     back_in,
    "back-out":    back_out,
    "back-in-out": back_in_out,
    "anticipate":  anticipate,
}


def get_easing(name: str) -> EasingFn:
    """Look up an easing by name. Raises if unknown — used by JSON theme parsers."""
    if name not in EASINGS:
        raise ValueError(f"Unknown easing: {name!r}. Known: {sorted(EASINGS)}")
    return EASINGS[name]


# ---------------------------------------------------------------------------
# Linear approximation — port of Motion's `generateLinearEasing()`.
#
# This is critical for PPTX: the underlying file format only stores a small
# set of named animation timings. To represent a *spring*, Motion samples
# the curve at N points and emits a `linear()` easing function with those
# samples. We do the equivalent — emit an N-point keyframe sequence that
# the slide animation engine plays back exactly.
# ---------------------------------------------------------------------------

def sample_curve(easing: EasingFn, n_samples: int = 30) -> list[tuple[float, float]]:
    """Sample an easing function at `n_samples + 1` evenly-spaced points
    in [0, 1] and return [(t0, y0), (t1, y1), …, (1, 1)] pairs."""
    if n_samples < 2:
        raise ValueError("n_samples must be ≥ 2")
    return [
        (i / n_samples, easing(i / n_samples))
        for i in range(n_samples + 1)
    ]
