"""Tests for the pure sunrise/sunset ramp calculations."""

from __future__ import annotations

from datetime import UTC, datetime, time

import pytest
from circadian import (
    PHASE_DAY,
    PHASE_NIGHT,
    PHASE_WAKING,
    PHASE_WINDING_DOWN,
    CircadianConfig,
    get_state,
)

CONFIG = CircadianConfig(
    wake_time=time(6, 30),
    sleep_time=time(22, 30),
    prewake_minutes=30,
    peak_offset_minutes=20,
    winddown_minutes=60,
    min_brightness_pct=1,
    max_brightness_pct=100,
    min_color_temp_kelvin=2000,
    max_color_temp_kelvin=4000,
)


def _at(hour: int, minute: int) -> datetime:
    return datetime(2026, 7, 13, hour, minute, tzinfo=UTC)


def test_night_before_ramp_is_idle_and_dim() -> None:
    state = get_state(CONFIG, _at(3, 0))
    assert state.phase == PHASE_NIGHT
    assert state.brightness_pct == CONFIG.min_brightness_pct
    assert state.color_temp_kelvin == CONFIG.min_color_temp_kelvin
    assert not state.is_active


def test_ramp_starts_dim_and_warm() -> None:
    state = get_state(CONFIG, _at(6, 0))
    assert state.phase == PHASE_WAKING
    assert state.brightness_pct == pytest.approx(CONFIG.min_brightness_pct, abs=0.5)
    assert state.color_temp_kelvin == pytest.approx(CONFIG.min_color_temp_kelvin, abs=5)
    assert state.is_active


def test_peak_brightness_reached_20_minutes_after_wake() -> None:
    just_before_peak = get_state(CONFIG, _at(6, 49))
    at_peak = get_state(CONFIG, _at(6, 50))  # wake_time (06:30) + peak_offset (20 min)

    assert just_before_peak.phase == PHASE_WAKING
    assert just_before_peak.brightness_pct < CONFIG.max_brightness_pct

    assert at_peak.phase == PHASE_DAY
    assert at_peak.brightness_pct == CONFIG.max_brightness_pct
    assert at_peak.color_temp_kelvin == CONFIG.max_color_temp_kelvin


def test_day_holds_peak_values_without_being_active() -> None:
    state = get_state(CONFIG, _at(12, 0))
    assert state.phase == PHASE_DAY
    assert state.brightness_pct == CONFIG.max_brightness_pct
    assert state.color_temp_kelvin == CONFIG.max_color_temp_kelvin
    assert not state.is_active


def test_winddown_dims_towards_sleep_time() -> None:
    state = get_state(CONFIG, _at(22, 0))
    assert state.phase == PHASE_WINDING_DOWN
    assert state.is_active
    assert CONFIG.min_brightness_pct < state.brightness_pct < CONFIG.max_brightness_pct


def test_sleep_time_reaches_minimum_values() -> None:
    state = get_state(CONFIG, _at(22, 30))
    assert state.phase == PHASE_NIGHT
    assert state.brightness_pct == CONFIG.min_brightness_pct
    assert state.color_temp_kelvin == CONFIG.min_color_temp_kelvin


def test_waking_ramp_is_monotonically_increasing() -> None:
    samples = [
        get_state(CONFIG, _at(6, minute)).brightness_pct for minute in range(0, 50, 5)
    ]
    assert samples == sorted(samples)
    assert samples[0] < samples[-1]


def test_schedule_crossing_midnight() -> None:
    """A night-shift schedule (wake late night, sleep in the afternoon) still works."""
    config = CircadianConfig(
        wake_time=time(23, 0),
        sleep_time=time(15, 0),
        prewake_minutes=30,
        peak_offset_minutes=20,
        winddown_minutes=30,
        min_brightness_pct=1,
        max_brightness_pct=100,
        min_color_temp_kelvin=2000,
        max_color_temp_kelvin=4000,
    )
    state = get_state(config, datetime(2026, 7, 13, 23, 10, tzinfo=UTC))
    assert state.phase == PHASE_WAKING
