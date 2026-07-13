"""
Custom integration to run a light-based wake-up/wind-down alarm.

For more details about this integration, please refer to
https://github.com/siirty/circadian-alarm
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from .const import CONF_UPDATE_INTERVAL_SECONDS, DEFAULT_UPDATE_INTERVAL_SECONDS
from .coordinator import CircadianAlarmCoordinator
from .data import CircadianAlarmData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import CircadianAlarmConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CircadianAlarmConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    update_interval_seconds = entry.options.get(
        CONF_UPDATE_INTERVAL_SECONDS,
        entry.data.get(CONF_UPDATE_INTERVAL_SECONDS, DEFAULT_UPDATE_INTERVAL_SECONDS),
    )
    coordinator = CircadianAlarmCoordinator(
        hass=hass,
        update_interval=timedelta(seconds=update_interval_seconds),
    )
    entry.runtime_data = CircadianAlarmData(
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: CircadianAlarmConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: CircadianAlarmConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
