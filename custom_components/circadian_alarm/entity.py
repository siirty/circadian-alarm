"""CircadianAlarmEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import CircadianAlarmCoordinator


class CircadianAlarmEntity(CoordinatorEntity[CircadianAlarmCoordinator]):
    """Base entity for the Circadian Alarm integration."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: CircadianAlarmCoordinator, key: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(entry.domain, entry.entry_id)},
            name=entry.title,
        )
