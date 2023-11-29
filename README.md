# Integration Librelink


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

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `librelink`.
1. Download _all_ the files from the `custom_components/librelink/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Librelink"

## Configuration is done in the UI

- Using username (mail) and password.
- A token will be retreived for the duration of the HA session.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***
