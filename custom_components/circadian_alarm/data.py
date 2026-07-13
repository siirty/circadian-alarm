"""Custom types for circadian_alarm."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import CircadianAlarmCoordinator


type CircadianAlarmConfigEntry = ConfigEntry[CircadianAlarmData]


@dataclass
class CircadianAlarmData:
    """Runtime data for the Circadian Alarm integration."""

    coordinator: CircadianAlarmCoordinator
    integration: Integration
