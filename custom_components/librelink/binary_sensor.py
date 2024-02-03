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
from .entity import LibreLinkEntity

import logging

_LOGGER = logging.getLogger(__name__)


BinarySensorDescription = (
    BinarySensorEntityDescription(
        key="isHigh",
        name="Is High",
    ),
    BinarySensorEntityDescription(
        key="isLow",
        name="Is Low",
    ),
)


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

    for index, patients in enumerate(coordinator.data["data"]):
        patient = patients["firstName"] + " " + patients["lastName"]
        patientId = patients["patientId"]
#        print(f"patient : {patient}")

        async_add_entities(
            LibreLinkBinarySensor(
                coordinator,
                patients,
                patientId,
                patient,
                index,
                config_entry.entry_id,
                entity_description,
            )
            for entity_description in BinarySensorDescription
    )


class LibreLinkBinarySensor(LibreLinkEntity, BinarySensorEntity):
    """librelink binary_sensor class."""

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        patients,
        patientId: str,
        patient: str,
        index: int,
        entry_id,
        description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, patientId, patient, entry_id, description.key)
        self.entity_description = description
        self.patients = patients
        self.index = index

    # define state based on the entity_description key
    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self.coordinator.data["data"][self.index]["glucoseMeasurement"][
            self.entity_description.key
        ]

