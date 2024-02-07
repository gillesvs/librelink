"""Binary sensor platform for librelink."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant


from .const import DOMAIN
from .coordinator import LibreLinkDataUpdateCoordinator
from .device import LibreLinkDevice

import logging

_LOGGER = logging.getLogger(__name__)


# BinarySensorDescription = (
#     BinarySensorEntityDescription(
#         key="isHigh",
#         name="Is High",
#     ),
#     BinarySensorEntityDescription(
#         key="isLow",
#         name="Is Low",
#     ),
# )


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    # usermail = (config_entry.data[CONF_USERNAME]).split("@")
    # username = usermail[0]

    # to manage multiple patients, the API return an array of patients in "data". So we loop in the array
    # and create as many devices and sensors as we do have patients.
    sensors = []
    for index, patients in enumerate(coordinator.data["data"]):
        patient = patients["firstName"] + " " + patients["lastName"]
        patientId = patients["patientId"]
        #        print(f"patient : {patient}")
        sensors.extend( [
            LibreLinkBinarySensor(
                coordinator,
                patients,
                patientId,
                patient,
                index,
                config_entry.entry_id,
                key="isHigh",
                name= "Is High",
            ),
            LibreLinkBinarySensor(
                coordinator,
                patients,
                patientId,
                patient,
                index,
                config_entry.entry_id,
                key="isLow",
                name="Is Low",
            ),
        ])
    async_add_entities(sensors)



class LibreLinkBinarySensor(LibreLinkDevice, BinarySensorEntity):
    """librelink binary_sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        patients,
        patientId: str,
        patient: str,
        index: int,
        entry_id,
        key: str,
        name: str,
    ) -> None:
        """Initialize the device class."""
        super().__init__(
            coordinator, patientId, patient)

        self.key = key
        self.patients = patients
        self.patientId = patientId
        self.index = index
        self._attr_name = name

    @property
    def unique_id(self):
        # field = self._field
        # if self._index != None:
        #     field = f"{field}_{self._index}"
        return f"{self.patientId}_{self.key}_{self.index}"

    # @property
    # def name(self):
    #     # field = self._field
    #     # if self._index != None:
    #     #     field = f"{field}_{self._index}"
    #     return self.name

    # define state based on the entity_description key
    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        # return self.coordinator.data["data"][self.index]["glucoseMeasurement"][
        return self.patients["glucoseMeasurement"][
            self.key
        ]
