"""Choreography — port of Motion's `motion-dom/utils/stagger.ts` plus
`motion-dom/animation/utils/calc-child-stagger.ts`.

Source studied (MIT-licensed):
  https://github.com/motiondivision/motion/blob/main/packages/motion-dom/src/utils/stagger.ts

What it does
------------
Given a list of N children (e.g. the items in a numbered_list slide), return
the start-time delay for each child so they animate in a *choreographed*
sequence rather than all at once. Motion supports four stagger origins:

* "first"  — sequential from the top                  (default)
* "last"   — sequential from the bottom
* "center" — out-from-the-middle ripple
* `<int>`  — custom origin index

When an `easing` is provided, the delays are remapped through the easing
function so the choreography itself can be eased — slow start, fast middle,
slow end.

Why we need this in megadeck
----------------------------
PowerPoint supports per-shape `<p:par>` timing nodes with `delay=` (in ms).
We compute the delay via Motion's exact formula and emit one timing node
per shape; the result is a deck where (e.g.) bullet items cascade in just
like Motion's WAAPI examples.
"""
from __future__ import annotations

from typing import Callable, List, Literal, Optional, Union

from megadeck.animations.easing import EasingFn, get_easing


StaggerOrigin = Union[Literal["first", "last", "center"], int]


def get_origin_index(origin: StaggerOrigin, total: int) -> float:
    """Direct port of Motion's `getOriginIndex()`."""
    if origin == "first":
        return 0.0
    last = total - 1
    if origin == "last":
        return float(last)
    if origin == "center":
        return last / 2.0
    return float(origin)


def stagger_delay(
    duration_s: float = 0.1,
    *,
    start_delay_s: float = 0.0,
    origin: StaggerOrigin = 0,
    easing: Optional[Union[str, EasingFn]] = None,
) -> Callable[[int, int], float]:
    """Return a function `(index, total) -> delay_seconds` matching
    Motion's `stagger(duration, { startDelay, from, ease })`."""
    easing_fn: Optional[EasingFn] = None
    if easing is not None:
        easing_fn = get_easing(easing) if isinstance(easing, str) else easing

    def f(index: int, total: int) -> float:
        from_idx = (
            float(origin)
            if isinstance(origin, (int, float))
            else get_origin_index(origin, total)
        )
        distance = abs(from_idx - index)
        delay = duration_s * distance
        if easing_fn is not None and total > 0:
            max_delay = total * duration_s
            if max_delay > 0:
                delay = easing_fn(delay / max_delay) * max_delay
        return start_delay_s + delay

    return f


def materialise_stagger(
    n_children: int,
    *,
    duration_s: float = 0.08,
    start_delay_s: float = 0.0,
    origin: StaggerOrigin = "first",
    easing: Optional[Union[str, EasingFn]] = None,
) -> List[float]:
    """Compute the actual list of `delay_seconds` for `n_children` items.

    Convenience wrapper used by the renderer to emit timing XML.
    """
    if n_children < 1:
        return []
    fn = stagger_delay(
        duration_s,
        start_delay_s=start_delay_s,
        origin=origin,
        easing=easing,
    )
    return [fn(i, n_children) for i in range(n_children)]


__all__ = ["stagger_delay", "materialise_stagger", "get_origin_index", "StaggerOrigin"]
