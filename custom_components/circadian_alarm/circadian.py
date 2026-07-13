"""
Pure sunrise/sunset ramp calculations for the circadian alarm.

This module has no Home Assistant dependencies so the math can be unit
tested in isolation. Given a wake/sleep schedule, it figures out whether
"now" falls inside a wake-up ramp (a simulated sunrise ending in a
brightness peak shortly after the alarm) or a wind-down ramp (a simulated
sunset ending at bedtime), and what brightness/color temperature to show
for that moment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, time, timedelta

PHASE_NIGHT = "night"
PHASE_WAKING = "waking"
PHASE_DAY = "day"
PHASE_WINDING_DOWN = "winding_down"

# Phases during which the alarm should actively be pushing updates to the
# light. Outside of these the reported values are informational only.
ACTIVE_PHASES = (PHASE_WAKING, PHASE_WINDING_DOWN)

_KELVIN_TO_MIRED = 1_000_000


@dataclass(frozen=True, kw_only=True)
class CircadianConfig:
    """User-configurable schedule and brightness/color temperature range."""

    wake_time: time
    sleep_time: time
    prewake_minutes: float
    peak_offset_minutes: float
    winddown_minutes: float
    min_brightness_pct: float
    max_brightness_pct: float
    min_color_temp_kelvin: float
    max_color_temp_kelvin: float


@dataclass(frozen=True, kw_only=True)
class CircadianState:
    """The computed state of the alarm at a single point in time."""

    phase: str
    brightness_pct: float
    color_temp_kelvin: float
    next_change: datetime

    @property
    def is_active(self) -> bool:
        """Return True if the alarm should be actively driving the light."""
        return self.phase in ACTIVE_PHASES


def _ease(pct: float) -> float:
    """
    Ease a linear 0-1 progress value for a natural sunrise/sunset feel.

    Uses the same raised-cosine shape as a sun elevation curve: slow at
    the start and end of the ramp, fastest through the middle.
    """
    pct = min(1.0, max(0.0, pct))
    return (1 - math.cos(pct * math.pi)) / 2


def _brightness_at(cfg: CircadianConfig, pct: float) -> float:
    return (
        cfg.min_brightness_pct + (cfg.max_brightness_pct - cfg.min_brightness_pct) * pct
    )


def _color_temp_at(cfg: CircadianConfig, pct: float) -> float:
    """
    Interpolate color temperature in mireds for perceptual uniformity.

    `pct=0` returns the warm end of the range and `pct=1` the cool end,
    matching how a real sunrise shifts from warm to cool light.
    """
    warm_mired = _KELVIN_TO_MIRED / cfg.min_color_temp_kelvin
    cool_mired = _KELVIN_TO_MIRED / cfg.max_color_temp_kelvin
    mired = warm_mired - (warm_mired - cool_mired) * pct
    return _KELVIN_TO_MIRED / mired


@dataclass(frozen=True, kw_only=True)
class _Cycle:
    sunrise_start: datetime
    sunrise_peak: datetime
    sunset_start: datetime
    sunset_end: datetime


def _combine(now: datetime, day_offset: int, moment: time) -> datetime:
    day = now.date() + timedelta(days=day_offset)
    return datetime.combine(day, moment, tzinfo=now.tzinfo)


def _cycle_for_day(cfg: CircadianConfig, now: datetime, day_offset: int) -> _Cycle:
    wake_dt = _combine(now, day_offset, cfg.wake_time)
    sleep_dt = _combine(now, day_offset, cfg.sleep_time)
    if sleep_dt <= wake_dt:
        # The configured sleep clock-time is not later than the wake
        # clock-time, so bedtime falls on the following calendar day.
        sleep_dt += timedelta(days=1)
    return _Cycle(
        sunrise_start=wake_dt - timedelta(minutes=cfg.prewake_minutes),
        sunrise_peak=wake_dt + timedelta(minutes=cfg.peak_offset_minutes),
        sunset_start=sleep_dt - timedelta(minutes=cfg.winddown_minutes),
        sunset_end=sleep_dt,
    )


def get_state(cfg: CircadianConfig, now: datetime) -> CircadianState:
    """
    Compute the alarm phase and target brightness/color temp for `now`.

    Looks at yesterday's, today's and tomorrow's wake/sleep cycle so the
    ramps are found correctly even when they cross midnight.
    """
    cycles = [_cycle_for_day(cfg, now, offset) for offset in (-1, 0, 1)]

    for cycle in cycles:
        if cycle.sunrise_start <= now < cycle.sunset_end:
            if now < cycle.sunrise_peak:
                span = (cycle.sunrise_peak - cycle.sunrise_start).total_seconds()
                pct = (
                    _ease((now - cycle.sunrise_start).total_seconds() / span)
                    if span
                    else 1.0
                )
                return CircadianState(
                    phase=PHASE_WAKING,
                    brightness_pct=_brightness_at(cfg, pct),
                    color_temp_kelvin=_color_temp_at(cfg, pct),
                    next_change=cycle.sunrise_peak,
                )
            if now < cycle.sunset_start:
                return CircadianState(
                    phase=PHASE_DAY,
                    brightness_pct=cfg.max_brightness_pct,
                    color_temp_kelvin=cfg.max_color_temp_kelvin,
                    next_change=cycle.sunset_start,
                )
            span = (cycle.sunset_end - cycle.sunset_start).total_seconds()
            pct = (
                _ease((now - cycle.sunset_start).total_seconds() / span)
                if span
                else 1.0
            )
            return CircadianState(
                phase=PHASE_WINDING_DOWN,
                brightness_pct=_brightness_at(cfg, 1 - pct),
                color_temp_kelvin=_color_temp_at(cfg, 1 - pct),
                next_change=cycle.sunset_end,
            )

    next_sunrise = min(
        cycle.sunrise_start for cycle in cycles if cycle.sunrise_start > now
    )
    return CircadianState(
        phase=PHASE_NIGHT,
        brightness_pct=cfg.min_brightness_pct,
        color_temp_kelvin=cfg.min_color_temp_kelvin,
        next_change=next_sunrise,
    )
