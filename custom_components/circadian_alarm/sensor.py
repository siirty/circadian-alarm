"""Sensor platform for circadian_alarm."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)

from .circadian import PHASE_DAY, PHASE_NIGHT, PHASE_WAKING, PHASE_WINDING_DOWN
from .entity import CircadianAlarmEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import CircadianAlarmCoordinator
    from .data import CircadianAlarmConfigEntry

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="phase",
        translation_key="phase",
        icon="mdi:sun-clock",
        device_class=SensorDeviceClass.ENUM,
        options=[PHASE_NIGHT, PHASE_WAKING, PHASE_DAY, PHASE_WINDING_DOWN],
    ),
    SensorEntityDescription(
        key="target_brightness",
        translation_key="target_brightness",
        icon="mdi:brightness-percent",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="target_color_temp",
        translation_key="target_color_temp",
        icon="mdi:thermometer",
        native_unit_of_measurement="K",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="next_change",
        translation_key="next_change",
        icon="mdi:clock-end",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: CircadianAlarmConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        CircadianAlarmSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class CircadianAlarmSensor(CircadianAlarmEntity, SensorEntity):
    """circadian_alarm Sensor class."""

    def __init__(
        self,
        coordinator: CircadianAlarmCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    @property
    def native_value(self) -> str | int | None:
        """Return the native value of the sensor."""
        state = self.coordinator.data
        if state is None:
            return None
        key = self.entity_description.key
        if key == "phase":
            return state.phase
        if key == "target_brightness":
            return round(state.brightness_pct)
        if key == "target_color_temp":
            return round(state.color_temp_kelvin)
        if key == "next_change":
            return state.next_change
        return None
