"""Binary sensor platform for librelink."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LibreLinkDataUpdateCoordinator
from .device import LibreLinkDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the binary_sensor platform."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # to manage multiple patients, the API return an array of patients in "data". So we loop in the array
    # and create as many devices and sensors as we do have patients.
    sensors = []
    # Loop through list of patients which are under "Data"
    for index, _ in enumerate(coordinator.data):
        sensors.extend(
            [
                LibreLinkBinarySensor(
                    coordinator,
                    index,
                    key="isHigh",
                    name="Is High",
                ),
                LibreLinkBinarySensor(
                    coordinator,
                    index,
                    key="isLow",
                    name="Is Low",
                ),
            ]
        )
    async_add_entities(sensors)


class LibreLinkBinarySensor(LibreLinkDevice, BinarySensorEntity):
    """librelink binary_sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        index: int,
        key: str,
        name: str,
    ) -> None:
        """Initialize the device class."""
        super().__init__(coordinator, index)

        self.key = key
        self.patients = (
            coordinator.data[index]["firstName"]
            + " "
            + coordinator.data[index]["lastName"]
        )
        self.patientId = self.coordinator.data[index]["patientId"]
        self.index = index
        self._attr_name = name
        self.coordinator = coordinator

    # define unique_id based on patient id and sensor key
    @property
    def unique_id(self) -> str:
        """Return a unique id for the sensor."""
        return f"{self.coordinator.data[self.index]['patientId']}_{self.key}"

    # define state based on the entity_description key
    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.data[self.index]["glucoseMeasurement"][self.key]
