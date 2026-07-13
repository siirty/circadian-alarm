"""DataUpdateCoordinator for circadian_alarm."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .circadian import (
    PHASE_DAY,
    PHASE_NIGHT,
    PHASE_WAKING,
    PHASE_WINDING_DOWN,
    CircadianConfig,
    CircadianState,
    get_state,
)
from .const import (
    CONF_LIGHTS,
    CONF_MAX_BRIGHTNESS_PCT,
    CONF_MAX_COLOR_TEMP_KELVIN,
    CONF_MIN_BRIGHTNESS_PCT,
    CONF_MIN_COLOR_TEMP_KELVIN,
    CONF_PEAK_OFFSET_MINUTES,
    CONF_PREWAKE_MINUTES,
    CONF_SLEEP_TIME,
    CONF_TRANSITION_SECONDS,
    CONF_TURN_OFF_AT_SLEEP,
    CONF_WAKE_TIME,
    CONF_WINDDOWN_MINUTES,
    DOMAIN,
    LOGGER,
)

if TYPE_CHECKING:
    from datetime import timedelta

    from homeassistant.core import HomeAssistant

    from .data import CircadianAlarmConfigEntry


class CircadianAlarmCoordinator(DataUpdateCoordinator[CircadianState]):
    """Computes the current sunrise/sunset ramp and drives the lights."""

    config_entry: CircadianAlarmConfigEntry

    def __init__(self, hass: HomeAssistant, update_interval: timedelta) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.enabled = True
        self._last_phase: str | None = None

    def _options(self) -> dict[str, Any]:
        entry = self.config_entry
        return {**entry.data, **entry.options}

    @property
    def circadian_config(self) -> CircadianConfig:
        """Build the pure-math config from the config entry's current options."""
        opts = self._options()
        return CircadianConfig(
            wake_time=dt_util.parse_time(opts[CONF_WAKE_TIME]),
            sleep_time=dt_util.parse_time(opts[CONF_SLEEP_TIME]),
            prewake_minutes=opts[CONF_PREWAKE_MINUTES],
            peak_offset_minutes=opts[CONF_PEAK_OFFSET_MINUTES],
            winddown_minutes=opts[CONF_WINDDOWN_MINUTES],
            min_brightness_pct=opts[CONF_MIN_BRIGHTNESS_PCT],
            max_brightness_pct=opts[CONF_MAX_BRIGHTNESS_PCT],
            min_color_temp_kelvin=opts[CONF_MIN_COLOR_TEMP_KELVIN],
            max_color_temp_kelvin=opts[CONF_MAX_COLOR_TEMP_KELVIN],
        )

    async def _async_update_data(self) -> CircadianState:
        """Recompute the current ramp state and, if active, push it to the lights."""
        state = get_state(self.circadian_config, dt_util.now())
        await self._apply(state)
        self._last_phase = state.phase
        return state

    async def _apply(self, state: CircadianState) -> None:
        """Call light services for state transitions that need to be applied."""
        opts = self._options()
        lights: list[str] = opts[CONF_LIGHTS]
        if not self.enabled or not lights:
            return

        transition = opts[CONF_TRANSITION_SECONDS]
        just_finished_waking = (
            self._last_phase == PHASE_WAKING and state.phase == PHASE_DAY
        )
        just_finished_winding_down = (
            self._last_phase == PHASE_WINDING_DOWN and state.phase == PHASE_NIGHT
        )

        if state.is_active or just_finished_waking:
            await self._async_turn_on(lights, state, transition)
        elif just_finished_winding_down:
            if opts[CONF_TURN_OFF_AT_SLEEP]:
                await self.hass.services.async_call(
                    "light",
                    "turn_off",
                    {"entity_id": lights, "transition": transition},
                    blocking=True,
                )
            else:
                await self._async_turn_on(lights, state, transition)

    async def _async_turn_on(
        self,
        lights: list[str],
        state: CircadianState,
        transition: float,
    ) -> None:
        await self.hass.services.async_call(
            "light",
            "turn_on",
            {
                "entity_id": lights,
                "brightness_pct": round(state.brightness_pct),
                "color_temp_kelvin": round(state.color_temp_kelvin),
                "transition": transition,
            },
            blocking=True,
        )
