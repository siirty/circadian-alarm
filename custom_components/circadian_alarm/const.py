"""Constants for circadian_alarm."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "circadian_alarm"

CONF_LIGHTS = "lights"
CONF_WAKE_TIME = "wake_time"
CONF_SLEEP_TIME = "sleep_time"
CONF_PREWAKE_MINUTES = "prewake_minutes"
CONF_PEAK_OFFSET_MINUTES = "peak_offset_minutes"
CONF_WINDDOWN_MINUTES = "winddown_minutes"
CONF_MIN_BRIGHTNESS_PCT = "min_brightness_pct"
CONF_MAX_BRIGHTNESS_PCT = "max_brightness_pct"
CONF_MIN_COLOR_TEMP_KELVIN = "min_color_temp_kelvin"
CONF_MAX_COLOR_TEMP_KELVIN = "max_color_temp_kelvin"
CONF_TRANSITION_SECONDS = "transition_seconds"
CONF_UPDATE_INTERVAL_SECONDS = "update_interval_seconds"
CONF_TURN_OFF_AT_SLEEP = "turn_off_at_sleep"

DEFAULT_PREWAKE_MINUTES = 30
DEFAULT_PEAK_OFFSET_MINUTES = 20
DEFAULT_WINDDOWN_MINUTES = 60
DEFAULT_MIN_BRIGHTNESS_PCT = 1
DEFAULT_MAX_BRIGHTNESS_PCT = 100
DEFAULT_MIN_COLOR_TEMP_KELVIN = 2000
DEFAULT_MAX_COLOR_TEMP_KELVIN = 4000
DEFAULT_TRANSITION_SECONDS = 60
DEFAULT_UPDATE_INTERVAL_SECONDS = 30
DEFAULT_TURN_OFF_AT_SLEEP = True

# A cycle's ramps must fit within a single day.
MAX_RAMP_MINUTES = 360
