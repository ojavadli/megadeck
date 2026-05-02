"""Spring physics — direct port of Motion's `motion-dom/animation/generators/spring.ts`.

Source studied (MIT-licensed):
  https://github.com/motiondivision/motion/blob/main/packages/motion-dom/src/animation/generators/spring.ts

Math
----
Spring state at time t (ms) for a mass on a spring with stiffness k, damping c,
initial displacement Δx₀, initial velocity v₀:

    ω₀  = √(k / m)                          undamped angular frequency
    ζ   = c / (2·√(k·m))                    damping ratio

For the underdamped case (ζ < 1), which covers the typical "bouncy" UI feel:

    ωd  = ω₀ · √(1 - ζ²)                    damped angular frequency
    A   = (v₀ + ζ·ω₀·Δx₀) / ωd
    x(t) = target − e^(−ζ·ω₀·t) · ( A·sin(ωd·t) + Δx₀·cos(ωd·t) )

For ζ = 1 (critically damped) and ζ > 1 (overdamped) Motion uses the closed-form
solutions; we port both.

Why we need this in megadeck
----------------------------
PowerPoint can't run Python at slide-show time, but we can pre-compute the
spring's position at N evenly-spaced times and emit those as a keyframe
sequence. The CLI option `megadeck animate --spring stiffness=200 damping=18`
turns into an entrance animation whose underlying timing matches a Motion-
spring exactly.

The `Spring` class returned here is a fully-resolvable generator: call
`spring.next(t_ms)` to get position + velocity at time t, or call
`spring.sample(n)` to materialise N evenly-spaced keyframes for emission
into pptx animation XML.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


# Motion's `springDefaults` translated 1:1.
DEFAULT_STIFFNESS = 100.0
DEFAULT_DAMPING = 10.0
DEFAULT_MASS = 1.0
DEFAULT_VELOCITY = 0.0
DEFAULT_DURATION_MS = 800.0
DEFAULT_BOUNCE = 0.3
DEFAULT_VISUAL_DURATION_S = 0.3
MIN_DAMPING = 0.05
MAX_DAMPING = 1.0
MIN_DURATION_S = 0.01
MAX_DURATION_S = 10.0


@dataclass
class SpringSample:
    t_ms: float
    value: float
    velocity_per_s: float


@dataclass
class Spring:
    """Resolvable spring. Set `stiffness/damping/mass` directly OR pass
    `duration` + `bounce` and we solve for k/c via Newton-Raphson, exactly
    as Motion does in `findSpring`.

    The animation goes from `origin` (default 0) to `target` (default 1).
    Use `sample(n)` to discretise into PPTX keyframes.
    """
    stiffness: float = DEFAULT_STIFFNESS
    damping: float = DEFAULT_DAMPING
    mass: float = DEFAULT_MASS
    velocity: float = DEFAULT_VELOCITY  # per-second
    origin: float = 0.0
    target: float = 1.0

    @classmethod
    def from_visual_duration(
        cls,
        visual_duration_s: float = DEFAULT_VISUAL_DURATION_S,
        bounce: float = DEFAULT_BOUNCE,
        mass: float = DEFAULT_MASS,
    ) -> "Spring":
        """Match Motion's `visualDuration` / `bounce` shorthand.

        Replicates the exact derivation:
            root = 2π / (visualDuration · 1.2)
            stiffness = root²
            damping = 2 · clamp(0.05, 1, 1 - bounce) · √(stiffness)
        """
        root = (2 * math.pi) / (visual_duration_s * 1.2)
        stiffness = root * root
        damping_ratio = max(MIN_DAMPING, min(MAX_DAMPING, 1.0 - bounce))
        damping = 2.0 * damping_ratio * math.sqrt(stiffness)
        return cls(stiffness=stiffness, damping=damping, mass=mass)

    @classmethod
    def from_duration(
        cls,
        duration_ms: float = DEFAULT_DURATION_MS,
        bounce: float = DEFAULT_BOUNCE,
        velocity: float = 0.0,
        mass: float = DEFAULT_MASS,
    ) -> "Spring":
        """Match Motion's `findSpring` — solve for stiffness + damping that
        produce a given duration + bounce. Newton-Raphson with the same
        envelope/derivative pair as the JS source."""
        damping_ratio = 1.0 - bounce
        damping_ratio = max(MIN_DAMPING, min(MAX_DAMPING, damping_ratio))
        duration_s = max(MIN_DURATION_S, min(MAX_DURATION_S, duration_ms / 1000.0))
        safe_min = 0.001
        v = velocity

        if damping_ratio < 1:
            def envelope(undamped_freq: float) -> float:
                exponential_decay = undamped_freq * damping_ratio
                delta = exponential_decay * duration_s
                a = exponential_decay - v
                b = undamped_freq * math.sqrt(1 - damping_ratio * damping_ratio)
                c = math.exp(-delta)
                return safe_min - (a / b) * c

            def derivative(undamped_freq: float) -> float:
                exponential_decay = undamped_freq * damping_ratio
                delta = exponential_decay * duration_s
                d = delta * v + v
                e = (damping_ratio ** 2) * (undamped_freq ** 2) * duration_s
                f = math.exp(-delta)
                g = (undamped_freq ** 2) * math.sqrt(1 - damping_ratio * damping_ratio)
                factor = -1 if (-envelope(undamped_freq) + safe_min) > 0 else 1
                return (factor * ((d - e) * f)) / g
        else:
            def envelope(undamped_freq: float) -> float:
                a = math.exp(-undamped_freq * duration_s)
                b = (undamped_freq - v) * duration_s + 1
                return -safe_min + a * b

            def derivative(undamped_freq: float) -> float:
                a = math.exp(-undamped_freq * duration_s)
                b = (v - undamped_freq) * (duration_s ** 2)
                return a * b

        # Newton-Raphson — same iterations as Motion's `rootIterations = 12`.
        result = 5.0 / duration_s
        for _ in range(12):
            try:
                result = result - envelope(result) / derivative(result)
            except ZeroDivisionError:
                break

        if math.isnan(result):
            return cls(stiffness=DEFAULT_STIFFNESS, damping=DEFAULT_DAMPING, mass=mass)
        stiffness = result * result * mass
        damping = damping_ratio * 2.0 * math.sqrt(mass * stiffness)
        return cls(stiffness=stiffness, damping=damping, mass=mass, velocity=velocity)

    # ----- Math -----------------------------------------------------------

    @property
    def damping_ratio(self) -> float:
        return self.damping / (2.0 * math.sqrt(self.stiffness * self.mass))

    @property
    def undamped_angular_freq_per_s(self) -> float:
        # Motion uses millisecondsToSeconds(sqrt(k/m)) at line 264 of spring.ts
        # which produces a per-millisecond frequency. We expose the per-second
        # version because it's the natural unit; t_ms is the time argument.
        return math.sqrt(self.stiffness / self.mass)

    def position(self, t_ms: float) -> float:
        """Position at time t (ms). Mirrors `resolveSpring(t)` for all three
        damping regimes (under, critical, over) in Motion's spring.ts."""
        z = self.damping_ratio
        # Motion stores frequency in per-ms internally to match its tick clock.
        omega0 = self.undamped_angular_freq_per_s / 1000.0
        delta = self.target - self.origin
        v0 = self.velocity / 1000.0  # per-ms

        if z < 1:
            wd = omega0 * math.sqrt(1 - z * z)
            A = (v0 + z * omega0 * delta) / wd
            envelope = math.exp(-z * omega0 * t_ms)
            return self.target - envelope * (A * math.sin(wd * t_ms) + delta * math.cos(wd * t_ms))
        if z == 1:
            envelope = math.exp(-omega0 * t_ms)
            return self.target - envelope * (delta + (v0 + omega0 * delta) * t_ms)
        # overdamped
        wd = omega0 * math.sqrt(z * z - 1)
        envelope = math.exp(-z * omega0 * t_ms)
        freq_for_t = min(wd * t_ms, 300)
        return self.target - (
            envelope
            * (
                (v0 + z * omega0 * delta) * math.sinh(freq_for_t)
                + wd * delta * math.cosh(freq_for_t)
            )
            / wd
        )

    def velocity_per_s(self, t_ms: float) -> float:
        """Analytical derivative of `position()`. Returns px/s (Motion's
        units — `secondsToMilliseconds(resolveVelocity(t))`)."""
        z = self.damping_ratio
        omega0 = self.undamped_angular_freq_per_s / 1000.0
        delta = self.target - self.origin
        v0 = self.velocity / 1000.0

        envelope = math.exp(-z * omega0 * t_ms)
        if z < 1:
            wd = omega0 * math.sqrt(1 - z * z)
            A = (v0 + z * omega0 * delta) / wd
            sin_coeff = z * omega0 * A + delta * wd
            cos_coeff = z * omega0 * delta - A * wd
            return 1000.0 * envelope * (sin_coeff * math.sin(wd * t_ms) + cos_coeff * math.cos(wd * t_ms))
        if z == 1:
            C = v0 + omega0 * delta
            return 1000.0 * envelope * (omega0 * C * t_ms - v0)
        wd = omega0 * math.sqrt(z * z - 1)
        P = (v0 + z * omega0 * delta) / wd
        sinh_coeff = z * omega0 * P - delta * wd
        cosh_coeff = z * omega0 * delta - P * wd
        freq_for_t = min(wd * t_ms, 300)
        return 1000.0 * envelope * (
            sinh_coeff * math.sinh(freq_for_t) + cosh_coeff * math.cosh(freq_for_t)
        )

    def sample(self, n_samples: int = 30, duration_ms: float = 1500.0) -> List[SpringSample]:
        """Emit `n_samples + 1` evenly-spaced positions over `duration_ms`.

        Use this to materialise the spring as a PPTX keyframe sequence.
        """
        if n_samples < 2:
            raise ValueError("n_samples must be ≥ 2")
        out: List[SpringSample] = []
        for i in range(n_samples + 1):
            t = duration_ms * i / n_samples
            out.append(SpringSample(
                t_ms=t,
                value=self.position(t),
                velocity_per_s=self.velocity_per_s(t),
            ))
        return out


__all__ = [
    "Spring", "SpringSample",
    "DEFAULT_STIFFNESS", "DEFAULT_DAMPING", "DEFAULT_MASS",
    "DEFAULT_DURATION_MS", "DEFAULT_BOUNCE", "DEFAULT_VISUAL_DURATION_S",
]
