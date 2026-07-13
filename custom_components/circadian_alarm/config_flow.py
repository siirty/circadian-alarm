"""Adds config flow for Circadian Alarm."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

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
    CONF_UPDATE_INTERVAL_SECONDS,
    CONF_WAKE_TIME,
    CONF_WINDDOWN_MINUTES,
    DEFAULT_MAX_BRIGHTNESS_PCT,
    DEFAULT_MAX_COLOR_TEMP_KELVIN,
    DEFAULT_MIN_BRIGHTNESS_PCT,
    DEFAULT_MIN_COLOR_TEMP_KELVIN,
    DEFAULT_PEAK_OFFSET_MINUTES,
    DEFAULT_PREWAKE_MINUTES,
    DEFAULT_TRANSITION_SECONDS,
    DEFAULT_TURN_OFF_AT_SLEEP,
    DEFAULT_UPDATE_INTERVAL_SECONDS,
    DEFAULT_WINDDOWN_MINUTES,
    DOMAIN,
    MAX_RAMP_MINUTES,
)

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult

_MINUTES = selector.NumberSelectorConfig(
    min=0,
    max=MAX_RAMP_MINUTES,
    step=1,
    unit_of_measurement="min",
    mode=selector.NumberSelectorMode.BOX,
)
_BRIGHTNESS_PCT = selector.NumberSelectorConfig(
    min=1,
    max=100,
    step=1,
    unit_of_measurement="%",
    mode=selector.NumberSelectorMode.BOX,
)
_COLOR_TEMP_KELVIN = selector.NumberSelectorConfig(
    min=1000,
    max=10000,
    step=50,
    unit_of_measurement="K",
    mode=selector.NumberSelectorMode.BOX,
)
_SECONDS = selector.NumberSelectorConfig(
    min=0,
    max=600,
    step=1,
    unit_of_measurement="s",
    mode=selector.NumberSelectorMode.BOX,
)


def _options_schema(defaults: dict[str, Any]) -> vol.Schema:
    """Build the schema shared by the config and options flows."""
    return vol.Schema(
        {
            vol.Required(
                CONF_LIGHTS,
                default=defaults.get(CONF_LIGHTS, []),
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="light", multiple=True),
            ),
            vol.Required(
                CONF_WAKE_TIME,
                default=defaults.get(CONF_WAKE_TIME, "06:30:00"),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_SLEEP_TIME,
                default=defaults.get(CONF_SLEEP_TIME, "22:30:00"),
            ): selector.TimeSelector(),
            vol.Required(
                CONF_PREWAKE_MINUTES,
                default=defaults.get(CONF_PREWAKE_MINUTES, DEFAULT_PREWAKE_MINUTES),
            ): selector.NumberSelector(_MINUTES),
            vol.Required(
                CONF_PEAK_OFFSET_MINUTES,
                default=defaults.get(
                    CONF_PEAK_OFFSET_MINUTES, DEFAULT_PEAK_OFFSET_MINUTES
                ),
            ): selector.NumberSelector(_MINUTES),
            vol.Required(
                CONF_WINDDOWN_MINUTES,
                default=defaults.get(CONF_WINDDOWN_MINUTES, DEFAULT_WINDDOWN_MINUTES),
            ): selector.NumberSelector(_MINUTES),
            vol.Required(
                CONF_MIN_BRIGHTNESS_PCT,
                default=defaults.get(
                    CONF_MIN_BRIGHTNESS_PCT, DEFAULT_MIN_BRIGHTNESS_PCT
                ),
            ): selector.NumberSelector(_BRIGHTNESS_PCT),
            vol.Required(
                CONF_MAX_BRIGHTNESS_PCT,
                default=defaults.get(
                    CONF_MAX_BRIGHTNESS_PCT, DEFAULT_MAX_BRIGHTNESS_PCT
                ),
            ): selector.NumberSelector(_BRIGHTNESS_PCT),
            vol.Required(
                CONF_MIN_COLOR_TEMP_KELVIN,
                default=defaults.get(
                    CONF_MIN_COLOR_TEMP_KELVIN, DEFAULT_MIN_COLOR_TEMP_KELVIN
                ),
            ): selector.NumberSelector(_COLOR_TEMP_KELVIN),
            vol.Required(
                CONF_MAX_COLOR_TEMP_KELVIN,
                default=defaults.get(
                    CONF_MAX_COLOR_TEMP_KELVIN, DEFAULT_MAX_COLOR_TEMP_KELVIN
                ),
            ): selector.NumberSelector(_COLOR_TEMP_KELVIN),
            vol.Required(
                CONF_TRANSITION_SECONDS,
                default=defaults.get(
                    CONF_TRANSITION_SECONDS, DEFAULT_TRANSITION_SECONDS
                ),
            ): selector.NumberSelector(_SECONDS),
            vol.Required(
                CONF_UPDATE_INTERVAL_SECONDS,
                default=defaults.get(
                    CONF_UPDATE_INTERVAL_SECONDS,
                    DEFAULT_UPDATE_INTERVAL_SECONDS,
                ),
            ): selector.NumberSelector(_SECONDS),
            vol.Required(
                CONF_TURN_OFF_AT_SLEEP,
                default=defaults.get(CONF_TURN_OFF_AT_SLEEP, DEFAULT_TURN_OFF_AT_SLEEP),
            ): selector.BooleanSelector(),
        },
    )


def _validate(data: dict[str, Any]) -> dict[str, str]:
    """Validate the submitted options, returning a dict of form errors."""
    errors: dict[str, str] = {}
    if not data[CONF_LIGHTS]:
        errors["base"] = "no_lights"
    elif data[CONF_MIN_BRIGHTNESS_PCT] > data[CONF_MAX_BRIGHTNESS_PCT]:
        errors["base"] = "brightness_range"
    elif data[CONF_MIN_COLOR_TEMP_KELVIN] > data[CONF_MAX_COLOR_TEMP_KELVIN]:
        errors["base"] = "color_temp_range"
    elif data[CONF_WAKE_TIME] == data[CONF_SLEEP_TIME]:
        errors["base"] = "same_time"
    return errors


class CircadianAlarmFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Circadian Alarm."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate(user_input)
            if not errors:
                name = user_input.pop(CONF_NAME)
                return self.async_create_entry(title=name, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=(user_input or {}).get(CONF_NAME, "Bedroom Alarm"),
                ): selector.TextSelector(),
            },
        ).extend(_options_schema(user_input or {}).schema)

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> CircadianAlarmOptionsFlowHandler:
        """Get the options flow for this handler."""
        return CircadianAlarmOptionsFlowHandler(config_entry)


class CircadianAlarmOptionsFlowHandler(config_entries.OptionsFlow):
    """Options flow for Circadian Alarm."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize."""
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        current = {**self.config_entry.data, **self.config_entry.options}
        if user_input is not None:
            errors = _validate(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(user_input or current),
            errors=errors,
        )
