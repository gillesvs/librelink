[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate with Hassfest](https://github.com/gillesvs/librelink/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/gillesvs/librelink/actions/workflows/hassfest.yaml)
[![Validate with HACS](https://github.com/gillesvs/librelink/actions/workflows/validate.yaml/badge.svg)](https://github.com/gillesvs/librelink/actions/workflows/validate.yaml)

# Librelink Integration for Home Assistant 


[integration_librelink]: https://github.com/gillesvs/librelink.git
[buymecoffee]: https://www.buymeacoffee.com/gillesvs

**This integration will set up the following platforms.**

Platform | Description
-- | --

`sensor` | Show info from Librelink API.
- Active Sensor (in days) : All information about your sensor. State is number of days since activation.
- Glucose Measurement (in mg/dL) : Measured value every minute.
- Glucose Trend : in plain text + icon.
- Minutes since update (in min) : self explanatory.

`binary_sensor` | to measure high and low.
- Is High | True of False.
- Is Low  | True of False.

## Installation

1. Add this repository as a custom repository in HACS
2. Restart Home Assistant
3. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Librelink"

## Configuration is done in the UI

- Using username (mail) and password.
- A token will be retreived for the duration of the HA session.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***
