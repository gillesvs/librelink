"""Binary sensor platform for librelink."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_PATIENT_ID, DOMAIN
from .coordinator import LibreLinkDataUpdateCoordinator
from .sensor import LibreLinkSensorBase


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the binary_sensor platform."""

    coordinator: LibreLinkDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.data[CONF_USERNAME]
    ]

    pid = config_entry.data[CONF_PATIENT_ID]

    sensors = [
        HighSensor(coordinator, pid),
        LowSensor(coordinator, pid),
    ]
    async_add_entities(sensors)


class LibreLinkBinarySensor(LibreLinkSensorBase, BinarySensorEntity):
    """LibreLink Binary Sensor class."""

    @property
    def device_class(self) -> str:
        """Return the class of this device."""
        return BinarySensorDeviceClass.SAFETY


class HighSensor(LibreLinkBinarySensor):
    """High Sensor class."""

    @property
    def name(self) -> str:
        """Return the name of the binary_sensor."""
        return "Is High"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self._data.measurement.value >= self._data.target.high


class LowSensor(LibreLinkBinarySensor):
    """Low Sensor class."""

    @property
    def name(self) -> str:
        """Return the name of the binary_sensor."""
        return "Is Low"

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self._data.measurement.value <= self._data.target.low
