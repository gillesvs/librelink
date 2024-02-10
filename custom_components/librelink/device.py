"""Sensor platform for LibreLink."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import LibreLinkDataUpdateCoordinator

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LibreLinkDataUpdateCoordinator

import logging

# enable logging
_LOGGER = logging.getLogger(__name__)


# This class is called when a device is created.
# A device is created for each patient to regroup patient entities

class LibreLinkDevice(CoordinatorEntity):
    """LibreLinkEntity class."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: LibreLinkDataUpdateCoordinator,
        index: int,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, context=index)

        # Creating unique IDs using for the device based on the Librelink patient Id.
        # self.patient = self.coordinator.data[index]["firstName"] + " " + self.coordinator.data[index]["lastName"]
        # self.patientId = self.coordinator.data[index]["patientId"]
        self._attr_unique_id = self.coordinator.data[index]["patientId"]

        _LOGGER.debug(
            "entity unique id is %s",
            self._attr_unique_id,
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.data[index]["patientId"])},
            name=self.coordinator.data[index]["firstName"] + " " + self.coordinator.data[index]["lastName"],
            model=VERSION,
            manufacturer=NAME,
        )

