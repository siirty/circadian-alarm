"""Binary sensor platform for circadian_alarm."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import CircadianAlarmEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import CircadianAlarmCoordinator
    from .data import CircadianAlarmConfigEntry

ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="active",
        translation_key="active",
        icon="mdi:weather-sunset",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: CircadianAlarmConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        CircadianAlarmBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class CircadianAlarmBinarySensor(CircadianAlarmEntity, BinarySensorEntity):
    """circadian_alarm binary_sensor class, on while a ramp is being applied."""

    def __init__(
        self,
        coordinator: CircadianAlarmCoordinator,
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    @property
    def is_on(self) -> bool | None:
        """Return true while the wake-up or wind-down ramp is active."""
        state = self.coordinator.data
        return state.is_active if state else None
