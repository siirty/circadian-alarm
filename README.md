# Circadian Alarm

[![License][license-shield]](LICENSE)

A Home Assistant custom integration that turns any light into a sunrise/sunset alarm clock. Set a wake time and a sleep time; the integration ramps your lights up like a sunrise before your alarm and dims them down like a sunset before bed — no cloud, no dependency on a real sunrise, fully local and computed from the clock.

## How it works

Unlike a full-day adaptive lighting solution, Circadian Alarm only acts around your **wake** and **sleep** times:

- **Wake-up ramp** – starts `prewake_minutes` before your wake time, and reaches **peak brightness `peak_offset_minutes` after** your wake time (20 minutes by default). Brightness rises from your configured minimum to maximum, and color temperature shifts from warm to cool, easing in and out like a real sunrise.
- **Day** – once the peak is reached, the integration leaves your lights alone until the wind-down window begins.
- **Wind-down ramp** – starts `winddown_minutes` before your sleep time and dims/warms the lights back down, reaching the minimum exactly at sleep time. Optionally turns the lights off at that point.
- **Night** – outside of these windows, the integration stays idle.

All of the timing, brightness and color temperature values are configurable per alarm, and you can run multiple instances (e.g. one per bedroom).

**This integration sets up the following platforms:**

Platform | Description
-- | --
`sensor` | Current phase (`night`/`waking`/`day`/`winding_down`), target brightness %, target color temperature, and the time of the next transition.
`binary_sensor` | On while a wake-up or wind-down ramp is actively being applied.
`switch` | Enable/disable the alarm without removing the configuration.

## Installation

### HACS

1. Add this repository as a custom repository in [HACS](https://hacs.xyz).
2. Search for "Circadian Alarm" and install it.
3. Restart Home Assistant.

### Manual

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `circadian_alarm`.
4. Download _all_ the files from the `custom_components/circadian_alarm/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant.
7. In the HA UI go to "Settings" -> "Devices & Services" -> "Add Integration" and search for "Circadian Alarm".

## Configuration

Configuration is done entirely in the UI. When adding the integration you'll be asked for:

- **Lights to control**
- **Wake time** and **sleep time**
- **Prewake minutes** – how long before wake time the sunrise ramp starts
- **Peak offset minutes** – how long after wake time peak brightness is reached (default 20)
- **Winddown minutes** – how long before sleep time the sunset ramp starts
- **Minimum/peak brightness** and **warmest/coolest color temperature**
- **Transition duration** and **update interval** used for the light service calls
- Whether to **turn the lights off** once sleep time is reached

All of these can be changed later from the integration's "Configure" options without recreating it.

## Reference

The wake-up/wind-down ramp shape and warm-to-cool color temperature interpolation take inspiration from [`basnijholt/adaptive-lighting`](https://github.com/basnijholt/adaptive-lighting), scoped down to just the alarm window instead of tracking the sun all day.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[license-shield]: https://img.shields.io/github/license/siirty/circadian-alarm.svg?style=for-the-badge
