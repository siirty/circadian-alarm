"""Switch platform for circadian_alarm."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.helpers.restore_state import RestoreEntity

from .entity import CircadianAlarmEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import CircadianAlarmCoordinator
    from .data import CircadianAlarmConfigEntry

ENTITY_DESCRIPTION = SwitchEntityDescription(
    key="enabled",
    translation_key="enabled",
    icon="mdi:alarm-light-outline",
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: CircadianAlarmConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    async_add_entities(
        [
            CircadianAlarmSwitch(
                coordinator=entry.runtime_data.coordinator,
                entity_description=ENTITY_DESCRIPTION,
            ),
        ],
    )


class CircadianAlarmSwitch(CircadianAlarmEntity, RestoreEntity, SwitchEntity):
    """Switch to enable or disable the alarm without removing the config entry."""

    def __init__(
        self,
        coordinator: CircadianAlarmCoordinator,
        entity_description: SwitchEntityDescription,
    ) -> None:
        """Initialize the switch class."""
        super().__init__(coordinator, entity_description.key)
        self.entity_description = entity_description

    async def async_added_to_hass(self) -> None:
        """Restore the last enabled/disabled state after a restart."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None:
            self.coordinator.enabled = last_state.state == "on"

    @property
    def is_on(self) -> bool:
        """Return true if the alarm is enabled."""
        return self.coordinator.enabled

    async def async_turn_on(self, **_: Any) -> None:
        """Enable the alarm."""
        self.coordinator.enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **_: Any) -> None:
        """Disable the alarm."""
        self.coordinator.enabled = False
        self.async_write_ha_state()
